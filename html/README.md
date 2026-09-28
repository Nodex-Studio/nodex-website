# Studio product document

The only content input is ../00-executive-summary.md. Earlier specifications
and ADRs are not read or linked by the build.

## Build and preview

Run python3 html/build.py with Python Markdown installed. The build writes a
self-contained html/dist/index.html with inline styles and interaction code.
It does not deploy or contact an external service.

To also generate a built-in visualization fragment, pass an absolute destination
with --preview /absolute/task-owned/path/dashboard-studio.html.

template.html is a fragment shared by both presentations. The interactive
architecture describes layer responsibilities, and document navigation
highlights the current section. The build verifies identifiers and local links.

The generated technical.html contains only a redirect to the new document,
so the old architecture does not remain available through the previous route
in a future publication. Historical source files are preserved outside the build.

## Deployment status

The user authorized publication of the consolidated revision on 29 September
2026. The existing Pages workflow publishes changes pushed to main; the local
build and preview commands do not invoke that workflow.
