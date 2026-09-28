# ADR-0008 — No escape hatch: schema growth is the only valve

**Status:** Accepted · 2026-09-28 · resolves **O3**

## Context

Studio's schema is closed ([ADR-0002](0002-schema-bounded-generation.md)), so some
requests will fall outside it. The proposed relief was an **escape hatch**: a
custom widget with "its own query and its own render", shown as an opaque block
that the property panel does not attempt to turn into a form, and explicitly
one-way — once custom, not editable by prompt or panel.

O3 framed this as a scoping question: ship it in v1, or defer it.

It is not a scoping question. The hatch as specified cannot be built at any point
without breaking three load-bearing properties:

- **I2** — a custom render is code not derived from the AST, so changing it means
  hand-editing generated output.
- **I3** — the model's output surface stops being only AST patches.
- **The query protocol guarantee.** "Its own query" contradicts
  [06-data-plane.md](../06-data-plane.md#query-protocol): *a client can only ask
  for queries the manifest already declares*. That single sentence is what makes
  compromising the frontend unable to widen data access, and what lets the
  business logic stay out of the client entirely. A widget that constructs its
  own query voids both, for every dashboard that contains one.

By the convention in [01-overview.md](../01-overview.md#core-invariants), the invariant wins and the
document is wrong.

## Decision

**There is no escape hatch.** Not in v1, not later. The `custom` widget kind is
removed from the AST schema.

A request outside the schema fails honestly and is logged. The log is the input to
the next schema version.

Three mechanisms absorb the tail, in the order they should be reached for:

1. **The schema grows.** The prompt-failure log names what is missing, and
   missing node types get added. This is the primary channel and it is already
   the stated purpose of the log.
2. **Bounded expressiveness inside the schema** — computed fields over declared
   metrics, conditional formatting, predicate-banded colour rules, reference
   lines. Declarative, not Turing-complete, and where most requests that feel
   like "we need something custom" actually land.
3. **New widget kinds ship as a schema version, by Nodex.** Additive is a minor
   change under [07-versioning.md](../07-versioning.md), and `minRuntime` already
   handles the resulting skew. This is the honest home for the long tail: a
   platform release, never a per-customer artifact.

## Coverage to validate

Existing bipp map and custom-visualization use cases should be checked against
the proposed schema. A bounded map widget is one candidate representation
([ADR-0011](0011-geo-widget-kinds.md)); it does not establish that a closed schema
covers every customer need. The pilot must identify unsupported requirements and
the work needed to add them as supported capabilities.

## Consequences

**Good.** I2, I3, and the query protocol hold without exception, so the safety
argument for the data plane has no "except over there" clause. Bidirectional
editing is true of every widget in every dashboard, permanently. No part of the
build plane compiles customer-supplied code, which removes a sandbox boundary and
a supply-chain surface from [08-security.md](../08-security.md) entirely. Users
report gaps instead of routing around them, which is the only way the schema
learns what it is missing.

**Costs, stated plainly.** Some evaluations will be lost over a single widget, and
that is a real loss with no mitigation other than schema velocity. This makes two
things obligatory rather than nice to have: the failure log must be reviewed on a
regular cadence with a named owner, and schema releases must be frequent enough
that "we will add it" is credible to a customer rather than a deflection.

## Alternatives considered

**Ship the contained, one-way hatch.** Rejected — the containment argument is
about blast radius within a document, and says nothing about the protocol
violation, which is global.

**A render-only hatch, whose queries still go through the manifest.** This fixes
the protocol violation and is the strongest version of the idea. Rejected anyway:
it still breaks I2 and I3, and the widget still loses bidirectional editing
forever, which is the specific failure [ADR-0002](0002-schema-bounded-generation.md)
exists to prevent.

**Per-customer schema extension.** Rejected — the schema is a versioned contract
between the control plane and customer-operated runtimes
([02-ast.md](../02-ast.md#schema-versioning)). Per-customer forks make the skew
problem unbounded and the runtime unable to state what it can execute.
