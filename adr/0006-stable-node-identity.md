# ADR-0006 — Stable AST node identity as a public API contract

**Status:** Accepted · 2026-09-28

## Context

The exported package's public API — props, widget handles, event payloads — is
derived from the AST. A **consuming developer**, typically on a different team
from the person authoring the dashboard, imports that package and writes code
against it by hand. Their code is not generated, not visible to us, and not
regenerable.

Meanwhile the authoring developer edits the dashboard in a visual tool where
nothing looks like an API change.

## Decision

**AST node ids are assigned once at creation and never change.** They are opaque
(`w_7f3a91`), and never derived from titles, positions, array indices, or
content. Deleted ids are retired permanently and never reused.

## Consequences

**Good.**

- Renaming a widget, reordering the layout, or changing a metric is not a
  breaking change, because none of them touch identity.
- The public API becomes a pure function of the AST, which makes the semver gate
  in [07-versioning.md](../07-versioning.md#mechanical-semver) computable:
  diff the AST, derive the API diff, compute the bump.
- Genuine breaking changes — a renamed param, a deleted widget — are detected
  mechanically and surfaced to the authoring developer *at the moment they make
  the change*, naming the applications that will break.

Without this, an authoring developer renaming a chart on a Tuesday breaks another
team's production build, with no signal to either party. Stable identity converts
that from an accident into a deliberate, reviewable act.

**Costs.** Ids are meaningless to humans, so Studio must always display titles
and never raw ids. Generated API names derived from ids need a readable
mapping — a title-derived alias layer over stable ids, where the alias may change
and the id may not. Migration of any existing dashboards requires a one-time id
assignment pass.

## Alternatives considered

**Derive ids from titles, slugified.** Readable generated APIs, but every rename
is a silent breaking change and collisions need disambiguation that shifts when
widgets are added. Rejected — this is the exact failure the decision exists to
prevent.

**Positional ids.** Reordering the layout would break consumers. Rejected.

**Content-hash ids.** Changing a metric would change the id. Rejected.
