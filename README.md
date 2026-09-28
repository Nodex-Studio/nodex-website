# nodex.studio

The bipps dashboard platform architecture document, published at
<https://nodex.studio>.

The markdown in this repository is the source of truth. `html/build.py` compiles
it into a single self-contained page, and GitHub Actions publishes that page on
every push to `main`.

| Path | What it is |
|---|---|
| `01-overview.md` … `08-security.md` | The architecture, in reading order |
| `adr/` | Decision records — six accepted, one open |
| `diagrams/` | Mermaid sources, editable `.excalidraw` scenes, and renders |
| `html/` | The build script, template, stylesheet and page script |

Edit the markdown, push to `main`, and the published document updates. See
[html/README.md](html/README.md) to build or preview it locally.
