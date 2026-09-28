#!/usr/bin/env python3
"""Build the single-file architecture document from the markdown sources.

Reads ../*.md and ../adr/*.md, inlines ../diagrams/*.svg at their image
references, rewrites cross-document links to in-page anchors, and emits
dist/index.html with CSS and JS inlined. No network at build time.
"""
import re, json, pathlib, html as htmllib
import markdown
from markdown.extensions.toc import TocExtension

ROOT = pathlib.Path(__file__).resolve().parent
SRC  = ROOT.parent
DIST = ROOT / "dist"
DOMAIN = "nodex.studio"

# (source file, section id, nav label, kind)
DOCS = [
    ("00a-product-update.md", "product-update", "Product update",  "intro"),
    ("00b-platform.md",       "platform",       "Platform baseline", "intro"),
    ("01-overview.md",     "overview",     "Overview",            "doc"),
    ("02-ast.md",          "ast",          "The AST",             "doc"),
    ("03-studio.md",       "studio",       "Studio",              "doc"),
    ("04-codegen.md",      "codegen",      "Code generation",     "doc"),
    ("05-distribution.md", "distribution", "Distribution",        "doc"),
    ("06-data-plane.md",   "data-plane",   "Data plane",          "doc"),
    ("07-versioning.md",   "versioning",   "Versioning",          "doc"),
    ("08-security.md",     "security",     "Security",            "doc"),
    ("adr/0001-ast-as-source-of-truth.md",      "adr-0001", "0001 · Source of truth",      "adr"),
    ("adr/0002-schema-bounded-generation.md",   "adr-0002", "0002 · Bounded generation",   "adr"),
    ("adr/0003-web-components-target.md",       "adr-0003", "0003 · Web Components",       "adr"),
    ("adr/0004-manifest-not-service.md",        "adr-0004", "0004 · Manifest, not service","adr"),
    ("adr/0005-runtime-configured-endpoint.md", "adr-0005", "0005 · Runtime config",       "adr"),
    ("adr/0006-stable-node-identity.md",        "adr-0006", "0006 · Stable identity",      "adr"),
    ("adr/0007-reactive-runtime.md",            "adr-0007", "0007 · Reactive runtime",     "adr"),
    ("adr/0008-no-escape-hatch.md",             "adr-0008", "0008 · No escape hatch",      "adr"),
    ("adr/0009-runtime-repetition.md",          "adr-0009", "0009 · Runtime repetition",   "adr"),
    ("adr/0010-definition-and-binding.md",      "adr-0010", "0010 · Definition and binding","adr"),
    ("adr/0011-geo-widget-kinds.md",            "adr-0011", "0011 · Geo widget kinds",     "adr"),
]

FILE_TO_ID, FILE_TO_LABEL = {}, {}
for path, sid, label, _ in DOCS:
    name = pathlib.Path(path).name
    FILE_TO_ID[path] = FILE_TO_ID[name] = sid
    FILE_TO_LABEL[name] = label


def gh_slug(text, sep="-"):
    """GitHub-compatible heading slug, so links written as #some-heading resolve."""
    s = htmllib.unescape(str(text)).lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.U)
    return re.sub(r"[\s]+", sep, s.strip())


def prefixed_slugify(prefix):
    return lambda text, sep: f"{prefix}--{gh_slug(text, sep)}"


# ---------------------------------------------------------------- diagrams
_instance = [0]


def load_diagram(name):
    """Inline an SVG, uniquifying its internal ids.

    Keyed per *instance*, not per name: a diagram embedded in two sections would
    otherwise duplicate every id and gradient ref, and its scoped <style> block
    would apply to both copies.
    """
    _instance[0] += 1
    svg = (SRC / "diagrams" / f"{name}.svg").read_text()
    svg = svg.replace("diagram-1", f"dg{_instance[0]}-{name}")
    svg = re.sub(r'\swidth="100%"', "", svg, count=1)
    svg = re.sub(r'\sstyle="max-width:[^"]*"', "", svg, count=1)
    # Give the SVG its intrinsic size so it is a replaced element with a real
    # aspect ratio; CSS then clamps it by width AND height without distortion.
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if m:
        w, h = float(m.group(1)), float(m.group(2))
        svg = svg.replace("<svg ", f'<svg width="{w:.0f}" height="{h:.0f}" ', 1)
    return svg


DIAGRAM_CAPTIONS = {
    "system-context":   "The three planes, and the boundary artifacts cross in one direction.",
    "ast-pipeline":     "One AST becomes a deterministic shell, a generated interior, and an inert manifest.",
    "studio-edit-loop": "Prompts and direct manipulation converge on the same validated patch.",
    "query-path":       "The token is minted by the host application; row-level security is applied in the runtime.",
    "version-cadences": "Three clocks, two of them outside our control, and the contracts that hold between them.",
}


def diagram_figure(name):
    cap = DIAGRAM_CAPTIONS.get(name, "")
    svg = load_diagram(name)                 # increments the instance counter
    key = f"{name}-{_instance[0]}"
    return (
        f'<figure class="diagram" id="fig-{key}">'
        f'<div class="diagram-frame" data-diagram="{key}">'
        f'<div class="diagram-scroll">{svg}</div>'
        f'<button class="diagram-zoom" type="button" data-zoom="{key}" '
        f'aria-label="Open {name.replace("-", " ")} diagram full screen">Expand</button>'
        f"</div>"
        f'<figcaption>{cap}</figcaption></figure>'
    )


# ---------------------------------------------------------------- transforms
def rewrite_links(html_text, cur):
    """Turn cross-file markdown links into in-page anchors.

    A bare "#anchor" is a same-document link, correct in the repo's markdown
    view. Headings here are prefixed per section, so it is resolved against
    this document first; main() catches anything that lands nowhere.
    """
    def sub(m):
        href = m.group(1)
        if href.startswith(("http://", "https://", "mailto:")):
            return m.group(0)
        if href.startswith("#"):
            return f'href="#{cur}--{href[1:]}"'
        path, _, anchor = href.partition("#")
        path = path.replace("../", "").lstrip("./")
        sid = FILE_TO_ID.get(path) or FILE_TO_ID.get(pathlib.Path(path).name)
        if not sid:
            return m.group(0)
        return f'href="#{sid}--{anchor}"' if anchor else f'href="#{sid}"'
    html_text = re.sub(r'href="([^"]+)"', sub, html_text)

    # A bare filename is the right link text in the repo, but reads as debris
    # here. Swap it for the section's name.
    def label(m):
        return m.group(1) + FILE_TO_LABEL.get(m.group(2), m.group(2)) + "</a>"
    return re.sub(r'(<a href="#[^"]*">)([0-9]{2}[a-z]?-[a-z-]+\.md)</a>', label, html_text)


IDENT = re.compile(r"(?<![\w#/-])(I[1-9][0-9]?|O[1-9][0-9]?)(?![\w-])")


def link_identifiers(html_text):
    """Make every I1-I9 / O1-O5 reference a live chip, outside code and headings."""
    parts = re.split(r"(<code.*?</code>|<pre.*?</pre>|<h[1-6][^>]*>.*?</h[1-6]>|<a\b.*?</a>)", html_text, flags=re.S)
    for i in range(0, len(parts), 2):
        parts[i] = IDENT.sub(
            lambda m: f'<button class="ident ident-{"inv" if m.group(1)[0]=="I" else "open"}" '
                      f'type="button" data-ident="{m.group(1)}">{m.group(1)}</button>',
            parts[i],
        )
    return "".join(parts)


def swap_diagrams(html_text):
    return re.sub(
        r'<p><img alt="[^"]*" src="[^"]*diagrams/([a-z-]+)\.png"\s*/?></p>',
        lambda m: diagram_figure(m.group(1)),
        html_text,
    )


def convert(path, sid):
    raw = (SRC / path).read_text()
    raw = re.sub(r'<a id="([^"]+)"', rf'<a id="{sid}--\1"', raw)      # keep manual anchors unique
    raw = re.sub(r"^#\s+.*\n", "", raw, count=1)                      # title comes from nav metadata
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "attr_list", "sane_lists",
                    TocExtension(slugify=prefixed_slugify(sid), toc_depth="2-3")]
    )
    out = md.convert(raw)
    out = swap_diagrams(out)
    out = rewrite_links(out, sid)
    out = link_identifiers(out)
    out = out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    headings = [{"id": t["id"], "text": t["name"]} for t in md.toc_tokens]
    return out, headings


# ---------------------------------------------------------------- extraction
def extract_invariants():
    text = (SRC / "01-overview.md").read_text()
    body = text.split("## Core invariants")[1].split("## Glossary")[0]
    out = []
    for m in re.finditer(r"\*\*(I[1-9][0-9]?) — ([^*]+?)\*\*\s*(.*?)(?=\n\*\*I[1-9]|\Z)", body, re.S):
        rest = re.sub(r"\s+", " ", m.group(3)).strip()
        rest = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", rest)
        rest = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", rest)
        rest = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", rest)
        rest = re.sub(r"`([^`]+)`", r"<code>\1</code>", rest).rstrip()
        out.append({"id": m.group(1), "rule": m.group(2).strip().rstrip("."), "detail": rest})
    return out


def extract_open():
    text = (SRC / "01-overview.md").read_text()
    body = text.split("## Open decisions")[1]
    out = []
    for m in re.finditer(r"\|\s*(O[1-9][0-9]?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|", body):
        where = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", m.group(3))
        out.append({"id": m.group(1), "rule": m.group(2), "detail": f"Decided in: {where}"})
    return out


# ---------------------------------------------------------------- assembly
def main():
    DIST.mkdir(exist_ok=True)
    invariants, opens = extract_invariants(), extract_open()
    idents = {d["id"]: d for d in invariants + opens}

    sections, nav = [], []
    for path, sid, label, kind in DOCS:
        body, headings = convert(path, sid)
        sections.append(f'<section class="doc doc-{kind}" id="{sid}"><h2 class="doc-title">{label}</h2>{body}</section>')
        nav.append({"id": sid, "label": label, "kind": kind, "headings": headings})

    hero = "".join(
        f'<li id="inv-{i["id"]}"><span class="inv-id">{i["id"]}</span>'
        f'<span class="inv-rule">{i["rule"]}.</span></li>'
        for i in invariants
    )
    open_cards = "".join(
        f'<li><span class="inv-id">{o["id"]}</span><span class="inv-rule">{o["rule"]}</span></li>'
        for o in opens
    )
    nav_html = ""
    for group, title in (("intro", "Product"), ("doc", "Architecture"), ("adr", "Decisions")):
        items = [n for n in nav if n["kind"] == group]
        links = "".join(
            f'<li><a href="#{n["id"]}" data-nav="{n["id"]}">{n["label"]}</a>'
            + ("<ul class='sub'>" + "".join(
                f'<li><a href="#{h["id"]}" data-nav="{h["id"]}">{h["text"]}</a></li>' for h in n["headings"]
              ) + "</ul>" if n["headings"] else "")
            + "</li>"
            for n in items
        )
        nav_html += f'<div class="nav-group"><p class="nav-group-title">{title}</p><ul>{links}</ul></div>'

    words = ["zero", "one", "two", "three", "four", "five", "six", "seven",
             "eight", "nine", "ten", "eleven", "twelve"]
    def spell(n, cap=False):
        w = words[n] if n < len(words) else str(n)
        return w.capitalize() if cap else w

    # Every in-page anchor must land. A bare same-document link that belonged to
    # another section is repaired here; anything left over fails the build rather
    # than shipping as a dead link.
    n_sections = len(sections)
    body = "".join(sections)
    ids = set(re.findall(r'id="([^"]+)"', body))
    dead = {h for h in re.findall(r'href="#([^"]+)"', body) if h not in ids}
    unresolved = []
    for h in sorted(dead):
        tail = h.split("--", 1)[-1]
        cand = [i for i in ids if i.endswith("--" + tail)]
        if len(cand) == 1:
            body = body.replace(f'href="#{h}"', f'href="#{cand[0]}"')
        else:
            unresolved.append(h if not cand else f"{h} (ambiguous: {cand})")
    if unresolved:
        raise SystemExit("dead in-page anchors: " + ", ".join(unresolved))
    sections = [body]

    tpl = (ROOT / "template.html").read_text()
    out = (tpl
           .replace("/*STYLES*/", (ROOT / "styles.css").read_text())
           .replace("/*SCRIPT*/", (ROOT / "app.js").read_text())
           .replace("<!--NAV-->", nav_html)
           .replace("<!--HERO-->", hero)
           .replace("<!--OPEN-->", open_cards)
           .replace("<!--SECTIONS-->", "".join(sections))
           .replace("<!--INVCOUNT-->", spell(len(invariants)))
           .replace("<!--OPENCOUNT-->", spell(len(opens), cap=True))
           .replace("/*IDENTS*/", json.dumps(idents)))
    (DIST / "index.html").write_text(out)
    # GitHub Pages drops a custom domain unless CNAME is in the published
    # artifact, so it is emitted by the build rather than committed once.
    (DIST / "CNAME").write_text(DOMAIN + "\n")
    (DIST / ".nojekyll").write_text("")
    kb = len(out.encode()) / 1024
    print(f"dist/index.html  {kb:.0f} KB  ·  {n_sections} sections  ·  "
          f"{len(invariants)} invariants  ·  {len(opens)} open decisions")


if __name__ == "__main__":
    main()
