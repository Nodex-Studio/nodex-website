# Diagrams

Each diagram is a triplet: `.mmd` (mermaid source, the thing to edit),
`.excalidraw` (editable scene — open at excalidraw.com via File → Open), and
`.svg` / `.png` renders.

| Diagram | Shows | Referenced from |
|---|---|---|
| [system-context](system-context.png) | The three planes and the trust boundary artifacts cross | [01](../01-overview.md), [08](../08-security.md) |
| [ast-pipeline](ast-pipeline.png) | Prompt/manual → patch → AST → shell + interior + manifest → six modes | [04](../04-codegen.md) |
| [studio-edit-loop](studio-edit-loop.png) | Generation, validation, repair, provenance, apply | [03](../03-studio.md) |
| [query-path](query-path.png) | Embed token minting through to warehouse, with RLS | [06](../06-data-plane.md) |
| [version-cadences](version-cadences.png) | Three release clocks and the contracts between them | [07](../07-versioning.md) |

The mermaid source is authoritative. To change a diagram, edit the `.mmd` and
re-render — don't hand-edit the SVG.
