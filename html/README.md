# Studio product document

The product overview uses ../00-executive-summary.md. The new detailed reference
uses technical.md, technical-contracts.ts, technical-template.html, technical.css,
technical.js, technical_build.py, and technical_diagrams.py. Earlier specifications
and ADRs remain excluded.

## Build and preview

Run python3 html/build.py with Python Markdown installed. The build writes a
self-contained html/dist/index.html with inline styles and interaction code.
It does not deploy or contact an external service.

To also generate a built-in visualization fragment, pass an absolute destination
with --preview /absolute/task-owned/path/dashboard-studio.html.

template.html is a fragment shared by both presentations. The interactive
architecture describes layer responsibilities, and document navigation
highlights the current section. The build verifies identifiers and local links.

The generated technical.html is a fresh native-bundle architecture reference,
not the historical appendix. It includes diagrams, lifecycle and HTTP contracts,
and an interactive revision-switching walkthrough. technical-contracts.ts is
also copied to dist as a download. API examples are documentation, not live endpoints.
The six diagram locations use inline SVG with wide and narrow layouts, accessible
titles/descriptions, theme-aware colors, and no external diagram library. The
revision SVG switches with the existing scenario controls. Component details
remain available in the topology disclosure.

Serve only the generated directory locally:

    python3 -m http.server 8765 --bind 127.0.0.1 --directory html/dist

Open http://127.0.0.1:8765/technical.html. This is local-only hosting.

Verify contracts and interaction script:

    tsc --noEmit --strict --lib ES2022,DOM html/technical-contracts.ts
    node --check html/technical.js

## Deployment status

The user authorized publication of the consolidated revision on 29 September
2026. The existing Pages workflow publishes changes pushed to main; the local
build and preview commands do not invoke that workflow.
