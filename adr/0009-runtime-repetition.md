# ADR-0009 — Repetition expands at query time, not build time

**Status:** Accepted · 2026-09-28

## Context

A shared scorecard across many sites is the same page repeated per site: one
definition, a tile per plant, a chart per KPI per plant. At 130 plants and
seventeen tiles that is well over two thousand charts, and building them by hand
is exactly the cost the product exists to remove.

The set of tiles is determined by **data** — the distinct values of a dimension —
not by the AST. The AST cannot enumerate it, because the AST does not know how
many plants exist and must not have to be edited when a plant is added.

This collides with two invariants. **I4** makes the public API a deterministic
function of the AST, and **I5** assigns node ids at creation. Neither can hold
unamended for nodes that come into existence when a query returns.

## Decision

**A `repeater` is an authored node. Its instances are expanded when the query
runs.**

- The **repeater** has an ordinary authored id, is authored by prompt or panel
  like any other node, and is what appears in the public API — as a collection,
  never as members.
- **Instance identity is derived**: `(repeaterId, keyValue)`. Deterministic given
  the key, enumerated at query time, and surfaced only in event payloads and
  drill targets.
- **The repeat key must be a stable business key** declared in the modeling
  layer — never an ordinal, an array index, or a row number.
- **Instances are never retired.** A dimension value absent from today's result
  may return tomorrow; that is not a deletion, and its id is not burned.
- **Repeated queries compile to one grouped query** with the repeat key as a
  dimension, partitioned after execution — not one query per instance.

## Consequences

**Good.** Adding a site is a data change, not an authoring change, and not a
version bump for anyone consuming the package. One definition remains the single
point of change for every instance, which is the property that a copied dashboard
per site destroys.

**The key rule is load-bearing.** If the key were positional, onboarding plant 131
would silently renumber the other 130 and break every consuming developer at
once — the [ADR-0006](0006-stable-node-identity.md) failure, arriving through a
side door and triggered by data rather than by an edit.

**Fan-out is now a cost surface.** A repeater over an unexpectedly high-cardinality
dimension is the new unbounded scan. The runtime needs a per-request fan-out cap
alongside its existing row caps and cost ceilings, and Studio needs to show
cardinality at authoring time rather than at first render. Default cap is
**O9 (OPEN)**.

**Preview needs a binding.** A repeater cannot be rendered without resolving its
key values, so Studio's preview must resolve against real data with the authoring
developer's own row-level security, and must cap fan-out more aggressively than
production.

**Costs.** Instance-level identity is weaker than authored identity: a consuming
developer can handle a click on any instance, but cannot write code against one
specific instance at compile time and be told mechanically when it disappears.
That is the correct trade — the alternative makes data changes into API changes.

## Alternatives considered

**Expand at build time.** The build plane would have to query the warehouse,
which it cannot do (**I8**) and which would end determinism — the same AST would
produce different artifacts on different days. Adding a plant would require a
rebuild and a version bump for every consumer. Rejected.

**Author one widget per site, by prompt.** Cheap to build and it produces N
independent widgets with no single point of change. It reproduces the per-site
dashboard sprawl the customer is migrating away from, and the prompt cost scales
with site count. Rejected.

**Expand in the client.** The client would have to construct queries the manifest
does not declare, which voids the query protocol guarantee
([06-data-plane.md](../06-data-plane.md#query-protocol)). Rejected.
