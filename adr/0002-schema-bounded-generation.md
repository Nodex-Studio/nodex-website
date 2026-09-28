# ADR-0002 — Schema-bounded generation over free-form code

**Status:** Accepted · 2026-09-28

## Context

Studio offers two editing modes: prompts, and direct manipulation through
property panels. Prompts are unbounded — a user can ask for anything. A property
panel is bounded — a form can only render what it has a field for.

This is a genuine conflict. If the model can produce arbitrary output, the visual
editor cannot edit the result, because arbitrary generated code cannot be
rendered back into a form. Manual refinement would stop working precisely when a
prompt did something novel, which is when users most want to refine it.

## Decision

**The LLM emits schema-conforming AST patches. It does not write code.**

Both prompts and direct manipulation produce patches against the same AST, so the
two modes are interchangeable and round-trip perfectly, in any order, for the
life of the dashboard.

Requests outside the schema fail honestly rather than improvising. There is no
escape hatch — the schema growing is the only valve
([ADR-0008](0008-no-escape-hatch.md),
[03-studio.md](../03-studio.md#when-the-schema-falls-short)).

## Consequences

**Good.** Bidirectional editing always works. Model output is mechanically
verifiable — valid or invalid, with no plausible-looking middle ground. Structured
decoding against the schema makes invalid output largely unrepresentable rather
than merely discouraged. Repair loops get precise, machine-generated errors. The
public API stays derivable ([ADR-0006](0006-stable-node-identity.md)).

**Costs.** Expressiveness is capped by the schema. Some user requests will be
refused. Schema extension becomes the *only* channel for adding capability
([ADR-0008](0008-no-escape-hatch.md)), and prompt-failure logs become the primary
roadmap input.

## Alternatives considered

**Free-form code generation.** Maximum expressiveness. Loses bidirectional
editing permanently, makes the public API a byproduct of model output, and makes
regeneration unsafe for anyone who has hand-written code against it. Rejected.

**Code generation with an AST extracted afterwards.** Parsing generated code back
into a schema is lossy and fails unpredictably. It inherits the costs of both
approaches. Rejected.

## Note

Bidirectional editing requires a bounded representation. This is not specific to
LLMs — every visual builder that has tried otherwise, across two decades, has
landed in the same place.
