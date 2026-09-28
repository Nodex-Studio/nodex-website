# Proposal and technical appendix

The Markdown files in architecture/ are the source of truth.

## Build

Run `python3 html/build.py` with the Python `markdown` package installed.
The build emits two self-contained pages in `html/dist/`:

- `index.html`: the founder proposal from `00-executive-summary.md`.
- `technical.html`: supporting context, architecture specifications and ADRs.

The output also contains CNAME and .nojekyll for GitHub Pages. CSS, JavaScript and
referenced SVG diagrams are inlined. No network access is needed to build.

## Preview

Run `python3 -m http.server 8811 --directory html/dist`.

## Build behavior

The DOCS list controls document ordering and navigation. The proposal is kept on
its own page; engineering details stay in the appendix. Links between Markdown
sources become links to the correct HTML page and heading. The build validates
local pages and anchors across both outputs, failing on unresolved links.

Invariant and open-decision chips derive their content from the overview.
The appendix's accepted-decision count is parsed from ADR status fields;
an open ADR is not counted as accepted.

The proposal's diagram summarizes authoring, publishing, execution and site
reuse. Detailed engineering diagrams appear only in the appendix.

## Deployment

.github/workflows/deploy.yml builds and verifies both pages on pushes to main,
then publishes html/dist/ to GitHub Pages at nodex.studio.
