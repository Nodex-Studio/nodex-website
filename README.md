# Nodex Studio Spec

Nodex Studio is the intelligence layer over a customer's existing system of
record, built on the bipp analytics modeling layer.
A customer's developer builds a dashboard in **Studio**, and the platform emits a
self-contained dashboard artifact that the customer deploys and operates
themselves — as a standalone app, an iframe embed, a web component, a CDN
bundle, or an npm library imported into their own internal applications.

## The system in one paragraph

Studio is a multi-tenant SaaS control plane. A dashboard authored in Studio is
represented as an **AST** conforming to a closed schema. Prompts and direct
manipulation both edit that AST and nothing else. From the AST, a deterministic
build emits a frontend artifact (custom elements, packaged six ways) and a
declarative **query manifest**. The manifest is executed by a single versioned
**query runtime** that the customer runs inside their own network, bound to
their bipp data models and their warehouse. No generated code is ever
hand-edited, and no artifact ever carries an endpoint or a credential.

## Documents

| Doc | Subject |
|---|---|
| [00-product-update.md](00-product-update.md) | Where Nodex Studio sits: systems of record, content and intelligence, and the AI maturity ladder |
| [01-overview.md](01-overview.md) | Actors, planes, core invariants, glossary |
| [02-ast.md](02-ast.md) | The AST: schema, node identity, patches, provenance, versioning |
| [03-studio.md](03-studio.md) | Authoring: prompt pipeline, manual editing, selection, escape hatch |
| [04-codegen.md](04-codegen.md) | Deterministic shell vs. generated interior; compilation target |
| [05-distribution.md](05-distribution.md) | The six delivery modes and the consumer-facing package contract |
| [06-data-plane.md](06-data-plane.md) | Query manifest, query runtime, modeling layer, auth, on-prem |
| [07-versioning.md](07-versioning.md) | Three release cadences, mechanical semver, compatibility windows |
| [08-security.md](08-security.md) | Trust boundaries, credentials, embed tokens, tenant isolation |

Decisions are recorded in [adr/](adr/). Diagrams (editable `.excalidraw` plus
rendered `.svg`) are in [diagrams/](diagrams/).

## Conventions

Load-bearing rules are stated once in [01-overview.md](01-overview.md) as
numbered invariants (**I1**–**I9**) and referenced by number elsewhere. If a
design in any document appears to violate an invariant, the invariant wins and
the document is wrong.

Open decisions are marked **OPEN** and listed in
[01-overview.md](01-overview.md#open-decisions). They are deliberately not
resolved here.

Status: draft, 2026-09-28.
