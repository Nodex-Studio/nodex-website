# The architecture document

`dist/index.html` is a single self-contained page built from the markdown in
`architecture/`. The markdown is the source of truth — edit that, not the HTML.

## Build

```bash
pip install markdown
python3 html/build.py
```

Output lands in `html/dist/` (`index.html`, `CNAME`, `.nojekyll`). No network
access is needed: the diagrams are inlined from `diagrams/*.svg` at build time,
and CSS and JS are inlined from this directory.

## Preview locally

```bash
python3 -m http.server 8811 --directory html/dist
```

## What the build does

- Converts each markdown file to a section, in the order set by `DOCS` in
  `build.py`.
- Inlines `diagrams/*.svg` wherever the markdown references the matching `.png`,
  uniquifying every internal id per instance so a diagram used in two sections
  does not collide with itself.
- Rewrites cross-file links (`06-data-plane.md#query-protocol`) into in-page
  anchors, and swaps bare-filename link text for the section's name.
- Turns every invariant and open-decision identifier (`I…` and `O…`) into a chip
  that surfaces the rule on hover, reading the text straight out of
  `01-overview.md`.

## Adding a document

Add the file, then add a row to `DOCS` in `build.py`. Nothing else needs
touching — navigation, search, and the outline are all derived.

## Deployment

`.github/workflows/deploy.yml` builds on push to `main` and publishes to GitHub
Pages. The workflow fails the build if sections, diagrams, or invariant chips go
missing, so a broken document does not reach the domain.
