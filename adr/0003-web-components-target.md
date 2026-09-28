# ADR-0003 — Web Components as the universal compilation target

**Status:** Accepted · 2026-09-28

## Context

One dashboard must ship as a standalone app, an iframe embed, a web component, a
CDN bundle, and an npm library importable into React, Vue, Angular, and Svelte
applications. Building and maintaining separate implementations per target is not
viable.

## Decision

Compile every dashboard to **custom elements with Shadow DOM**. Every delivery
mode is a packaging of that one artifact.

| Target | Packaging |
|---|---|
| Standalone | App shell + core bundle |
| iframe | App shell + `postMessage` API |
| Web component | The core bundle, unchanged |
| CDN | The same ESM at immutable versioned URLs |
| npm (4 frameworks) | Generated wrappers over the same elements |

## Consequences

**Good.** Custom elements are the only component model browsers implement
natively and every framework can consume. Six modes collapse to one build plus
packaging. Shadow DOM gives real style isolation, which is mandatory when our
markup runs inside a customer application whose CSS we have never seen.

**Costs.**

- *React below v19* sets properties as string attributes and does not listen for
  custom events, so React needs a real generated wrapper. Customers will be on 17
  and 18 for years.
- *Theming* must go through CSS custom properties and a small enumerated set of
  `::part()` names, each of which becomes a compatibility commitment.
- *Shadow DOM friction* — overlays, measurement, focus traversal, cross-boundary
  ARIA, and `@font-face` all need deliberate handling
  ([04-codegen.md](../04-codegen.md#known-costs-of-shadow-dom)).
- *Chart library choice is constrained* to libraries that render correctly inside
  a shadow root (**O2**), which eliminates several otherwise reasonable
  candidates.
- *Tag name collisions* across versions on one page must be guarded
  ([05-distribution.md](../05-distribution.md#consumer-facing-hazards)).

## Alternatives considered

**Generate per-framework implementations.** Best-in-class integration per
ecosystem, at four times the generation surface and four times the bug surface,
with divergent behaviour guaranteed. Rejected.

**iframe only.** Trivially isolated and much simpler, but no npm library, no web
component, poor theming, awkward sizing, and a bad fit for embedding inside an
existing internal application — which is the stated requirement. Rejected as the
sole mode; retained as one mode among six.

## Prior art

Stencil productised exactly this pattern with per-framework output targets, and
`@lit/react` covers the React wrapper case. This is a paved road, not a
speculative one.
