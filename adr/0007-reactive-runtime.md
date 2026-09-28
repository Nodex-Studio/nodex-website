# ADR-0007 — Reactive runtime: Lit vs. bespoke

**Status:** **OPEN** (O1) · raised 2026-09-28

## Context

Widget interiors need reactive properties, templating, and lifecycle. Two
options: adopt Lit, or build a bespoke reactive library designed for generation.

The original argument for bespoke was sound — constrain the generator to a small,
predictable API rather than letting it improvise DOM wiring.

Note the decision is narrower than it first appears. Under
[ADR-0002](0002-schema-bounded-generation.md) the model emits AST, not code, and
under [ADR-0001](0001-ast-as-source-of-truth.md) generated code is disposable. So
this choice affects only the **interior** ([04-codegen.md](../04-codegen.md)) —
the shell is templates and the AST is framework-agnostic. That makes it
reversible at moderate cost, and it should not block anything else.

## Options

### A — Lit

**For.** ~5KB. Battle-tested. Reactive properties, Shadow DOM, and SSR are
solved. Strongly represented in model training data, so the interior generator
writes it reliably without being taught the API in-context on every call. Someone
else maintains it and fixes its bugs. `@lit/react` covers the React wrapper.

**Against.** A general-purpose API surface larger than dashboard widgets need,
so generation is less constrained than a purpose-built DSL would be. An external
dependency loaded into every customer's application.

### B — Bespoke

**For.** Exactly the primitives dashboard widgets need and nothing else. Narrow
enough to validate and auto-repair generated output mechanically. No external
runtime dependency in customer applications.

**Against.** Zero presence in training data, so the API must be taught in-context
on every generation — more tokens, more hallucinated methods, more repair loops,
permanently. We own every bug, every browser quirk, and the SSR story. It is a
library with exactly one consumer, competing for attention with the product.

## Recommendation (not yet a decision)

Start with **Lit**, and add a thin dashboard-specific layer on top if generation
proves insufficiently constrained. This gets reliable generation on day one and
defers the bespoke investment until there is evidence it is needed.

If bespoke is chosen, the library must be narrow enough to be a genuine DSL that
is *validated and auto-repaired* the way the AST is — not merely described in a
prompt and hoped for. "We'll prompt the model with our API docs" is the failure
mode to avoid.

## Deciding factors

- Measured generation reliability for widget interiors, both ways, on a real
  widget corpus.
- Whether the chart library choice (**O2**) constrains or is constrained by this.
- Whether SSR is a requirement for the standalone mode — this is substantial work
  in the bespoke case and free in Lit's.

## Owner

Unassigned. Blocks nothing; should be settled before the interior generator is
built in earnest.
