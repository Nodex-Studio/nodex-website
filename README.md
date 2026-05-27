# Nodex Studio — marketing website

Static marketing site for **Nodex Studio** and its products. No build step — plain
HTML, CSS and vanilla JS. Open `index.html` or serve the folder with any static
file server.

```sh
# any of these work
python3 -m http.server 8080
npx serve .
```

Then visit <http://localhost:8080>.

## Structure

```
index.html                     Nodex Studio home — hero, product catalogue, ethos
products/typing-mastery.html   Typing Mastery product page
assets/
  css/  base.css               design tokens, theme system, header/footer, shared UI
        home.css               studio landing styles
        product.css            Typing Mastery page styles (editorial / pink)
  js/   site.js                theme toggle (persisted), sticky header, scroll reveal
        product.js             OS-detect downloads + GitHub Releases API, lightbox, demo
  img/  brand/                 favicon / logo mark
        shots/                 product screenshots (light + dark per feature, 13 themes)
  video/screencast.webm        hero demo (muted autoplay loop)
```

## Design

- **Identity** — Nodex Studio uses its own editorial-developer look (Fraunces display,
  Newsreader body, JetBrains Mono labels, rose-crimson accent, warm ink canvas).
  The Typing Mastery page leans into the app's own pink editorial styling.
- **Light / dark** — toggle in the header, persisted to `localStorage`
  (`nodex-theme`), defaulting to the OS preference. Feature screenshots swap
  between their light and dark captures to match the active theme.
- **Responsive** — fluid type and spacing; layouts collapse to single column on
  small screens; nav condenses on mobile.

## Downloads

`assets/js/product.js` detects the visitor's OS and points the primary button at
the matching build. On load it queries the GitHub Releases API
(`Nodex-Studio/typing-mastery`); when a published release exists it wires the
buttons to the real asset URLs and shows the version + file sizes. Until a
release is tagged it gracefully links to the Releases page.

> Note: the product repo's `build.yml` currently uploads CI **artifacts** only.
> Publish a tagged **Release** (with the Tauri bundles attached) for the
> per-platform direct-download buttons to light up.
