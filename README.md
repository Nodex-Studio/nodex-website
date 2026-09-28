# bipp's Next Chapter

Start with [the founder proposal](00-executive-summary.md): the customer
experience, expected benefits, proposed architecture and a focused pilot.

Nodex Studio proposes prompt and visual authoring, reusable dashboard components
and site bindings on top of bipp. The architecture is a working design for
integration review; implementation and benefits require validation.

## Reading paths

- **Proposal:** [From prompt to production analytics](00-executive-summary.md).
- **Evidence:** [bipp foundation and integration questions](00b-platform.md).
- **Technical appendix:** [architecture overview](01-overview.md), followed by
  the specifications below.
- **Editing guidance:** [editorial direction](EDITORIAL.md), excluded from the site.

## Technical reference

| Document | Subject |
|---|---|
| [00a-product-update.md](00a-product-update.md) | Product scope and boundaries |
| [01-overview.md](01-overview.md) | Proposed planes, roles, invariants and open decisions |
| [02-ast.md](02-ast.md) | Dashboard definition and editing contracts |
| [03-studio.md](03-studio.md) | Authoring and publication |
| [04-codegen.md](04-codegen.md) | Component compilation |
| [05-distribution.md](05-distribution.md) | Delivery formats and integration contracts |
| [06-data-plane.md](06-data-plane.md) | Queries, bindings and runtime operations |
| [07-versioning.md](07-versioning.md) | Four release cadences and compatibility |
| [08-security.md](08-security.md) | Trust boundaries and access controls |

Design decisions are recorded in [adr/](adr/). Accepted records describe choices
within the proposed design, not proof that the features are implemented.
Invariants I1–I14 are defined in the overview; open decisions remain unresolved.

The [HTML build](html/README.md) publishes the proposal at the site root and the
engineering reference on a separate technical appendix page.

Status: proposal draft, 28 September 2026.
