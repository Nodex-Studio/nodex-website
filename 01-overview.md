# 01 — Overview

## Purpose

The platform lets a developer at a customer company build internal dashboards by
describing them, then take the result away and run it themselves. It sits on top
of bipp's existing analytics stack — the data modeling layer, its SQL generation,
its warehouse connectors, and its row-level security — and adds two things those
don't have: a prompt-driven authoring surface, and a build system that emits the
dashboard as a real, deployable, importable artifact in six different shapes.

## Actors

| Actor | Role |
|---|---|
| **Nodex** | Operates Studio and the build service. Publishes the query runtime. Does not operate the customer's data plane. |
| **Authoring developer** | Employed by the customer. Connects data sources, defines models, and publishes dashboards. Never edits generated code. Publishing is theirs alone, because a published dashboard is an API contract. |
| **Business user** | Explores. Poses a question in Studio, builds a chart, filters it, shares it by link. Their work is ephemeral and produces no package (I10), so they need no developer skills and can break nothing. |
| **Consuming developer** | Also employed by the customer, but a different person and often a different team. Imports the exported package into an internal application and writes code against its public API by hand. Their code is not generated and not visible to us. |
| **End user** | Views the dashboard, applies filters, drills in. Subject to row-level security. |
| **Operator** | Runs the query runtime in the customer's environment, upgrades it, holds the warehouse credentials. |

The consuming developer is the actor most easily forgotten and the one who
constrains the design most, because they are the only party who writes
hand-maintained code against an interface that the platform regenerates.

## The three planes

**Control plane — Nodex cloud, multi-tenant.** Studio, the AST store, the prompt
pipeline, the build service, the package registry. Nodex operates this and ships
to it continuously.

**Build plane — Nodex cloud, per dashboard version.** Takes an AST and emits the
frontend artifact and the query manifest. Deterministic: same AST in, byte-identical
public API out.

**Data plane — the customer's environment.** The query runtime, the bipp data
models, and the warehouse. Customer-operated, customer-paced. Warehouse
credentials live here and only here.

The separation is what makes on-premise deployment a configuration rather than a
product variant. It also means that a customer-managed dashboard never queries
Nodex cloud — see [08-security.md](08-security.md).

![System context and trust boundaries](diagrams/system-context.png)

## Core invariants

These hold everywhere. Everything else in these documents is a consequence of
them.

**I1 — The AST is the single source of truth.** A dashboard *is* its AST.
Generated code, packages, and manifests are derived artifacts and may be
discarded and rebuilt at any time.

**I2 — Generated code is never hand-edited.** Not by us, not by the customer.
Anything a user needs to change is changed in the AST, through Studio.

**I3 — The LLM emits AST, never code.** The model's entire output surface is
schema-conforming AST patches. It does not author component code, SQL, or public
API. See [ADR-0002](adr/0002-schema-bounded-generation.md).

**I4 — The public API is a deterministic function of the AST.** Element names,
props, events, slots, theme tokens, and TypeScript declarations are emitted by
templates, not by a model. The same AST always produces the same public surface.

**I5 — Node identity is stable for the life of a dashboard.** Ids are assigned at
creation and never derived from titles, positions, or ordering. A consuming
developer's hand-written code depends on them.

**I6 — Edits are patches, never replacements.** Every prompt and every manual
action produces a diff against the existing AST. Nothing regenerates the whole
tree.

**I7 — Artifacts carry no endpoint and no credentials.** The query endpoint and
the auth token provider are injected at runtime. One artifact serves every
deployment topology.

**I8 — Warehouse credentials never leave the customer's network.** The control
plane never holds them and never proxies a query.

**I9 — One query runtime, many manifests.** Dashboards generate declarative
manifests, not deployable services. There is exactly one executable to patch.
See [ADR-0004](adr/0004-manifest-not-service.md).

**I10 — Exploration produces no artifact.** Only a published dashboard carries a
public API, a manifest, or a version. Ad hoc exploration is ephemeral by
construction, so a business user cannot break a consuming developer's build.
See [Explore and publish](03-studio.md#explore-and-publish).

## Glossary

**AST** — the structured, schema-conforming representation of a dashboard. The
source of truth (I1).

**Schema** — the closed set of node types and legal values the AST may contain.
Bounded by construction; this is what makes visual editing and prompt editing
round-trip.

**Shell** — the deterministically generated part of the artifact: public API,
types, wrappers, registration. Templates only.

**Interior** — the generated rendering logic inside each widget. Free to change
between builds because nothing outside can observe it.

**Query manifest** — the declarative, non-executable description of every query a
dashboard needs: model references, dimensions, metrics, filters, parameters.

**Query runtime** — the single versioned service that executes manifests against
the modeling layer. Customer-operated.

**Modeling layer** — bipp's existing semantic layer. Defines models, joins,
metrics, and row-level security, and generates SQL. Pre-existing; not designed
here.

**Embed token** — a short-lived signed token minted by the customer's host
application, carrying user identity and row-level filters.

## Open decisions

Deliberately unresolved. Each needs an owner before implementation starts.

| # | Decision | Where it bites |
|---|---|---|
| O1 | Reactive runtime: Lit vs. a bespoke library | [ADR-0007](adr/0007-reactive-runtime.md) |
| O2 | Chart library — must render correctly inside a shadow root, which eliminates several candidates | [04-codegen.md](04-codegen.md) |
| O3 | Is the custom-widget escape hatch in v1, or deferred? | [03-studio.md](03-studio.md) |
| O4 | Query runtime packaging: container, Helm chart, or binary | [06-data-plane.md](06-data-plane.md) |
| O5 | Where the AST is stored for on-premise customers — Nodex cloud or the customer's own git. bipp already has git-based version control, which argues for theirs | [02-ast.md](02-ast.md) |
| O6 | Who closes the content-governance gap — folders, certification, usage analytics, lineage. It degrades fastest under our usage pattern, not bipp's | [00b-platform.md](00b-platform.md) |
| O7 | Whether the runtime pushes updates (SSE or WebSocket) or the client polls. Polling ships sooner; push is the only honest answer for a dashboard on a wall | [06-data-plane.md](06-data-plane.md) |
