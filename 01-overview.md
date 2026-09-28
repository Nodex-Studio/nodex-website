# 01 — Overview

## Purpose

This working design supports the [founder proposal](00-executive-summary.md).
It proposes prompt and visual authoring, versioned component publishing and
site bindings on top of bipp's analytics stack. The following contracts describe
intended behavior. Reuse of bippDash, the SDK and existing services must be
validated before implementation ownership or missing capabilities are assumed.

## Actors

| Actor | Role |
|---|---|
| **Nodex** | Operates Studio and the build service and publishes the query runtime. Never hosts the data plane in Nodex cloud, but may operate it inside the customer's account on a managed plan. |
| **Authoring developer** | Employed by the customer. Connects data sources, defines models, and publishes dashboards. Never edits generated code. Publishing is theirs alone, because a published dashboard is an API contract. |
| **Business user** | Explores. Poses a question in Studio, builds a chart, filters it, shares it by link. Their work is ephemeral and produces no package (I10), so they need no developer skills and can break nothing. |
| **Consuming developer** | Also employed by the customer, but a different person and often a different team. Imports the exported package into an internal application and writes code against its public API by hand. Their code is not generated and not visible to us. |
| **End user** | Views the dashboard, applies filters, drills in. Subject to row-level security. |
| **Site owner** | Employed by the customer, one per site in an estate. Owns a **binding**: points their site's data at the shared definition's declared format and opts into the optional widgets that apply locally. Authors nothing and cannot change the definition ([ADR-0010](adr/0010-definition-and-binding.md)). |
| **Operator** | Runs the query runtime, upgrades it, holds the warehouse credentials. Either the customer or Nodex on a managed plan — in both cases the runtime sits inside the customer's own environment (I8). |

The consuming developer is the actor most easily forgotten and the one who
constrains the design most, because they are the only party who writes
hand-maintained code against an interface that the platform regenerates.

## The three planes

**Control plane — Nodex cloud, multi-tenant.** Studio, the AST store, the prompt
pipeline, the build service, the package registry. Nodex operates this and ships
to it continuously.

**Build plane — Nodex cloud, per dashboard version.** Takes an AST and emits the
frontend artifact and the query manifest. Deterministic: same AST in, byte-identical
public API out. It never reads customer data, which is why repetition and bindings
resolve later rather than here (I11, I12).

**Data plane — the customer's environment.** The query runtime in its web and
scheduler roles, the bipp data models, the binding registry, the runtime's own
state — monitor firing state and the annotation store — and the warehouse. It always runs in the customer's
own network or cloud account; it may be operated by the customer, or by Nodex on a
managed plan inside that same account. Warehouse credentials live here and only
here (I8). Where it runs and who operates it are separate questions — see
[Data plane](06-data-plane.md#where-it-runs-and-who-operates-it).

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
Data-dependent structure does not enter it: a repeater appears as a collection and
never as its members (I11), and a binding-optional widget is typed as possibly
absent (I12).

**I5 — Node identity is stable for the life of a dashboard.** Ids are assigned at
creation and never derived from titles, positions, or ordering. A consuming
developer's hand-written code depends on them. Repeater instances are the one
exception and are governed by I11: their identity is derived, not assigned.

**I6 — Edits are patches, never replacements.** Every prompt and every manual
action produces a diff against the existing AST. Nothing regenerates the whole
tree.

**I7 — Artifacts carry no endpoint and no credentials.** The query endpoint and
the auth token provider are injected at runtime. One artifact serves every
deployment topology.

**I8 — Warehouse credentials never leave the customer's environment.** The
runtime holds them and runs in the customer's own network or cloud account,
whoever operates it. The control plane never holds them and never proxies a
query.

**I9 — One query runtime, many manifests.** Dashboards generate declarative
manifests, not deployable services. There is exactly one executable to patch.
See [ADR-0004](adr/0004-manifest-not-service.md).

**I10 — Exploration produces no artifact.** Only a published dashboard carries a
public API, a manifest, or a version. Ad hoc exploration is ephemeral by
construction, so a business user cannot break a consuming developer's build.
See [Explore and publish](03-studio.md#explore-and-publish).

**I11 — Repetition expands at query time. Only authored nodes have authored
identity.** A repeater is authored and carries an assigned id; its instances are
enumerated when the query runs and their identity is derived from the repeater's id
and a stable business key. Adding a site is a data change, never an API change.
See [ADR-0009](adr/0009-runtime-repetition.md).

**I12 — A definition plus a binding set produces one artifact, never one per
binding.** Bindings are data in the data plane, resolved at mount, and versioned
independently of the definition. An estate of any size is one package and one
semver stream. See [ADR-0010](adr/0010-definition-and-binding.md).

**I13 — Anything that must run without a browser runs in the data plane.** The
control plane cannot query the warehouse (I8), so scheduled evaluation, threshold
monitoring, and rendered delivery are the runtime's work, not Studio's. This is a
general rule rather than three exceptions.

**I14 — Writes are annotations only.** The warehouse and the customer's systems of
record are read-only to everything described here. The platform may store
commentary the customer creates about a number; it never writes back, mutates, or
retains a durable duplicate of the number itself. A disposable query cache may
exist inside the customer environment. This is what keeps the product from becoming the
second system of record it exists to avoid
([Product update](00a-product-update.md)).

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

**Repeater** — an authored node that renders one copy of its contents per value of
a dimension. Its instances are enumerated at query time, not authored (I11).

**Definition** — the AST of a dashboard, independent of any site it is bound to.

**Binding** — a per-site record naming which concrete models a site's data lives
in, its parameter defaults, and which optional widgets it has locally. Data in the
data plane, not AST (I12).

**Model interface** — a declared model shape that many concrete models implement.
The contract a site conforms its data to. Belongs to the modeling layer; ownership
is O10.

**Query manifest** — the declarative, non-executable description of every query a
dashboard needs: model references, dimensions, metrics, filters, parameters.

**Query runtime** — the single versioned service that executes manifests against
the modeling layer. Always hosted in the customer's environment; operated by the
customer or by Nodex on a managed plan.

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
| O4 | Query runtime packaging: container, Helm chart, or binary | [06-data-plane.md](06-data-plane.md) |
| O5 | Where the AST is stored for on-premise customers — Nodex cloud or the customer's own git. bipp already has git-based version control, which argues for theirs | [02-ast.md](02-ast.md) |
| O6 | How existing content governance, usage reporting and lineage apply to generated dashboards, and who owns any integration work | [00b-platform.md](00b-platform.md) |
| O7 | Whether the runtime pushes updates (SSE or WebSocket) or the client polls. Polling ships sooner; push is the only honest answer for a dashboard on a wall | [06-data-plane.md](06-data-plane.md) |
| O8 | Whether a Nodex operator may read query results or result-bearing logs while debugging a managed runtime. Convenient, and the one hole in "we never see your data" | [08-security.md](08-security.md) |
| O9 | Default fan-out cap for a repeater, and whether a grouped query is always mandatory or merely preferred | [06-data-plane.md](06-data-plane.md) |
| O10 | How existing models expose the declared shapes needed for site bindings, whether extensions are required, and who owns that integration | [00b-platform.md](00b-platform.md) |
| O11 | Which identity a scheduled monitor runs as: the recipient's row-level security, the author's, or a declared service principal. There is no obvious default and it is a contract question, not a code one | [08-security.md](08-security.md) |
| O12 | Whether the annotation store is embedded in the runtime or a customer-provided database. Embedded is one less thing to operate; external is the only answer for a customer who wants annotations in their own backup and retention regime | [06-data-plane.md](06-data-plane.md) |
| O13 | How cross-dashboard link targets resolve across semver — by id plus a version range, or pinned | [07-versioning.md](07-versioning.md) |

Resolved decisions become ADRs and leave this table. Their numbers are retired and
never reused, for the same reason node ids are not (I5): a reference to O3 in a
meeting note from last quarter should not silently come to mean something else.
**O3** — the custom-widget escape hatch — is resolved in
[ADR-0008](adr/0008-no-escape-hatch.md): there is no escape hatch.
