#!/usr/bin/env python3
"""Build the founder proposal and technical appendix from Markdown sources.

Reads ../*.md and ../adr/*.md, inlines ../diagrams/*.svg at their image
references, rewrites cross-document links to in-page anchors, and emits
dist/index.html and dist/technical.html with CSS and JS inlined.
No network at build time.
"""
import re, json, pathlib, html as htmllib
from html.parser import HTMLParser
import markdown
from markdown.extensions.toc import TocExtension

ROOT = pathlib.Path(__file__).resolve().parent
SRC  = ROOT.parent
DIST = ROOT / "dist"
DOMAIN = "nodex.studio"

# (source file, section id, nav label, kind)
DOCS = [
    ("00-executive-summary.md", "executive-summary", "The proposal", "proposal"),
    ("00a-product-update.md", "product-update", "Product scope",  "intro"),
    ("00b-platform.md",       "platform",       "bipp foundation", "intro"),
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
    "proposal-architecture": "One dashboard definition becomes a reusable component; queries run through bipp inside the customer's environment.",
    "system-context":   "The three planes, and the boundary artifacts cross in one direction.",
    "ast-pipeline":     "One AST becomes a deterministic shell, a generated interior, and an inert manifest.",
    "studio-edit-loop": "Prompts and direct manipulation converge on the same validated patch.",
    "query-path":       "The token is minted by the host application; row-level security is applied in the runtime.",
    "version-cadences": "Studio, runtime and artifact releases; site bindings evolve independently as described below.",
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
        destination = "index.html" if sid == "executive-summary" else "technical.html"
        current = "index.html" if cur == "executive-summary" else "technical.html"
        prefix = "" if destination == current else destination
        return f'href="{prefix}#{sid}--{anchor}"' if anchor else f'href="{prefix}#{sid}"'
    html_text = re.sub(r'href="([^"]+)"', sub, html_text)

    # A bare filename is the right link text in the repo, but reads as debris
    # here. Swap it for the section's name.
    def label(m):
        return m.group(1) + FILE_TO_LABEL.get(m.group(2), m.group(2)) + "</a>"
    return re.sub(r'(<a href="[^"]*#[^"]*">)([0-9]{2}[a-z]?-[a-z-]+\.md)</a>', label, html_text)


IDENT = re.compile(r"(?<![\w#/-])(I[1-9][0-9]?|O[1-9][0-9]?)(?![\w-])")


def link_identifiers(html_text):
    """Make invariant and open-decision references live chips outside code/headings."""
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
        r'<p><img alt="[^"]*" src="[^"]*diagrams/([a-z-]+)\.(?:png|svg)"\s*/?></p>',
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
    accepted = sum(
        bool(re.search(r"^\*\*Status:\*\* Accepted\b", (SRC / path).read_text(), re.M))
        for path, _, _, kind in DOCS if kind == "adr"
    )
    rendered = []
    for path, sid, label, kind in DOCS:
        body, headings = convert(path, sid)
        section = f'<section class="doc doc-{kind}" id="{sid}"><h2 class="doc-title">{label}</h2>{body}</section>'
        rendered.append({"id": sid, "label": label, "kind": kind,
                         "headings": headings, "html": section})

    pages = {
        "index.html": {
            "title": "bipp’s Next Chapter",
            "description": "From prompt to production analytics. A proposal for a new authoring and publishing experience built on bipp.",
            "subtitle": "From prompt to production analytics",
            "label": "proposal",
            "meta": '<span><b>By</b> Nodex Studio</span><span><b>Read</b> 5 minutes</span>',
            "items": [n for n in rendered if n["kind"] == "proposal"],
            "other": '<a href="technical.html">Technical appendix →</a>',
        },
        "technical.html": {
            "title": "Technical architecture appendix",
            "description": "Supporting design and integration questions for the Nodex Studio proposal.",
            "subtitle": "Working design for integration review. Requirements describe intended behavior; implementation choices remain subject to validation.",
            "label": "appendix",
            "meta": f'<span><b>ADRs</b> {accepted} accepted</span><span><b>Open decisions</b> {len(opens)}</span>',
            "items": [n for n in rendered if n["kind"] != "proposal"],
            "other": '<a href="index.html">← Read the proposal</a>',
        },
    }
    tpl = (ROOT / "template.html").read_text()
    outputs = {}
    for filename, page in pages.items():
        nav = ""
        for group, title in (("proposal", "The proposal"), ("intro", "Context"),
                             ("doc", "Architecture"), ("adr", "Design decisions")):
            items = [n for n in page["items"] if n["kind"] == group]
            if not items:
                continue
            if group == "proposal":
                links = "".join(
                    f'<li><a href="#{h["id"]}" data-nav="{h["id"]}">{h["text"]}</a></li>'
                    for n in items for h in n["headings"]
                )
            else:
                links = "".join(
                    f'<li><a href="#{n["id"]}" data-nav="{n["id"]}">{n["label"]}</a>'
                    + ("<ul class='sub'>" + "".join(
                        f'<li><a href="#{h["id"]}" data-nav="{h["id"]}">{h["text"]}</a></li>'
                        for h in n["headings"]) + "</ul>" if n["headings"] else "")
                    + "</li>" for n in items
                )
            nav += f'<div class="nav-group"><p class="nav-group-title">{title}</p><ul>{links}</ul></div>'
        nav += f'<div class="nav-group page-link">{page["other"]}</div>'
        replacements = {
            "/*STYLES*/": (ROOT / "styles.css").read_text(),
            "/*SCRIPT*/": (ROOT / "app.js").read_text(),
            "/*IDENTS*/": json.dumps(idents),
            "/*APPENDIX_IDS*/": json.dumps([n["id"] for n in rendered if n["kind"] != "proposal"]),
            "<!--TITLE-->": htmllib.escape(page["title"]),
            "<!--DESCRIPTION-->": htmllib.escape(page["description"], quote=True),
            "<!--SUBTITLE-->": htmllib.escape(page["subtitle"]),
            "<!--LABEL-->": page["label"],
            "<!--META-->": page["meta"],
            "<!--NAV-->": nav,
            "<!--SECTIONS-->": "".join(n["html"] for n in page["items"]),
            "<!--OTHER-->": page["other"],
        }
        out = tpl
        for key, value in replacements.items():
            out = out.replace(key, value)
        outputs[filename] = out

    # Parse actual elements so JavaScript string templates are not treated as links.
    class PageLinks(HTMLParser):
        def __init__(self, source):
            super().__init__()
            self.ids, self.links = set(), set()
            self.feed(source)

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if "id" in attrs:
                self.ids.add(attrs["id"])
            if tag == "a" and "href" in attrs:
                self.links.add(attrs["href"])

    parsed = {name: PageLinks(out) for name, out in outputs.items()}
    page_ids = {name: page.ids for name, page in parsed.items()}
    for name, out in outputs.items():
        for href in parsed[name].links:
            if href.startswith(("https://", "http://", "mailto:", "data:")):
                continue
            target, _, anchor = href.partition("#")
            target = target or name
            if target not in outputs:
                raise SystemExit(f"{name}: unknown local page {href}")
            if anchor and anchor not in page_ids[target]:
                tail = anchor.split("--", 1)[-1]
                candidates = [i for i in page_ids[target] if i.endswith("--" + tail)]
                if len(candidates) != 1:
                    raise SystemExit(f"{name}: unresolved link {href}")
                prefix = "" if target == name else target
                out = out.replace(f'href="{href}"', f'href="{prefix}#{candidates[0]}"')
        (DIST / name).write_text(out)
        print(f"dist/{name}  {len(out.encode()) / 1024:.0f} KB · {len(pages[name]['items'])} sections")
    (DIST / "CNAME").write_text(DOMAIN + "\n")
    (DIST / ".nojekyll").write_text("")
    print(f"{len(invariants)} invariants · {accepted} accepted ADRs · {len(opens)} open decisions")


if __name__ == "__main__":
    main()
