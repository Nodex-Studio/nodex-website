# ADR-0001 — AST as the single source of truth

**Status:** Accepted · 2026-09-28

## Context

A dashboard authored in Studio must be exportable to six delivery formats,
regenerable on demand, and versioned as a public API. Two representations could
plausibly be authoritative: the generated code, or a structured description of
the dashboard.

## Decision

The **AST is the dashboard**. Generated code, packages, bundles, and query
manifests are derived artifacts, reproducible from the AST and discardable at any
time.

Generated code is never hand-edited — not by bipp, not by the customer. Anything
a user needs to change is changed in the AST, through Studio.

## Consequences

**Good.** Regeneration is safe by construction. The six export formats are six
renderings of one structure rather than six codebases. Builds are cacheable and
reproducible by AST hash. Diffs, history, undo, and audit are all operations on
one well-understood object.

**Costs.** Anything a user wants must be expressible in the AST. The schema
becomes the product's true feature set, and extending it is the only way to add
capability — which makes schema design a permanent, load-bearing activity rather
than a one-time task.

**Ruled out.** Any "eject to code" feature in the usual sense. Customers can
receive the generated source, but editing it forks them off the platform
permanently; that must be presented as a one-way door, not a workflow.

## Alternatives considered

**Generated code as source of truth, AST as a lossy cache.** Allows hand-editing,
but makes regeneration destructive and removes any mechanical basis for API
versioning. Rejected.

**Dual source of truth with reconciliation.** Three-way merge between last
generation, hand edits, and new generation — a permanent tax on every feature.
Rejected.
