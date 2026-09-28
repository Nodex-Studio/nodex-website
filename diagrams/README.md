# Diagrams

Each diagram is a `.mmd` mermaid source — the thing to edit — plus its `.svg` and
`.png` renders. The `.svg` is what [../html/build.py](../html/build.py) inlines
into the published document; the `.png` is what renders in markdown.

| Diagram | Shows | Referenced from |
|---|---|---|
| [system-context](system-context.png) | The three planes, the trust boundary artifacts cross, and the state the runtime holds | [01](../01-overview.md), [08](../08-security.md) |
| [ast-pipeline](ast-pipeline.png) | Prompt/manual → patch → AST → shell + interior + manifest → six modes | [04](../04-codegen.md) |
| [studio-edit-loop](studio-edit-loop.png) | Generation, validation, repair, provenance, apply | [03](../03-studio.md) |
| [query-path](query-path.png) | Embed token minting through to warehouse, with binding resolution, repeater expansion and RLS | [06](../06-data-plane.md) |
| [version-cadences](version-cadences.png) | Four release clocks and the contracts between them | [07](../07-versioning.md) |

The mermaid source is authoritative. To change a diagram, edit the `.mmd` and
re-render — never hand-edit the SVG, because the next re-render discards the edit
with no warning.

## Re-rendering

```bash
npx -y @mermaid-js/mermaid-cli -i <name>.mmd -o <name>.svg \
  --svgId diagram-1 -b transparent -c mermaid.json
npx -y @mermaid-js/mermaid-cli -i <name>.mmd -o <name>.png \
  -b transparent -c mermaid.json -s 2
```

`mermaid.json` pins the font stack (`Helvetica, "Liberation Sans", Arial, …` at
16px) so every diagram matches. The flags are not cosmetic: `../html/build.py`
keys off `diagram-1`, `width="100%"`, a `max-width` style, and a `viewBox` with a
`0 0` origin. Newer mermaid emits `viewBox="4 4 …"` and a
`background-color: transparent` in the style attribute — normalize both after
rendering, or the diagrams collapse on the published page with no build error.
