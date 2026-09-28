# Executive summary

## Product

Nodex Studio is an AI-assisted intelligence layer built on top of bipp
Analytics. It lets customers create trustworthy dashboards through
natural-language prompts or direct visual editing, then deploy those dashboards
inside the applications where people already make decisions.

The product is designed for organizations that already have governed, agreed
metric definitions. In the maturity model used by this specification, bipp
provides level 3 — **Defined** — while Nodex Studio enables level 4 —
**Distributed** — and level 5 — **Generative**. It is deliberately not another
data warehouse, ETL tool, or system of record.

## Architecture

The system is divided into three planes:

1. **Control plane — Nodex cloud.** Studio, prompt processing, AST storage, the
   build service, and package publishing. Prompts and direct manipulation both
   produce validated patches to the same dashboard AST.
2. **Build plane — Nodex cloud.** Deterministically compiles the AST into a
   frontend artifact and a declarative query manifest. It never reads customer
   data.
3. **Data plane — the customer's environment.** A single versioned query runtime
   executes manifests against bipp's semantic models and the customer's
   warehouse. Credentials, query results, monitor state, and annotations stay in
   that environment, whether the customer operates the runtime or Nodex manages
   it in the customer's account.

A dashboard's schema-conforming AST is its single source of truth. The LLM
generates AST patches rather than code or SQL, and generated code is never
hand-edited. One definition can serve many sites through runtime bindings;
repeated structures expand from live data at query time. Artifacts contain no
endpoint or credentials and can be delivered as standalone applications, iframe
embeds, Web Components, CDN bundles, or framework packages.

## Benefits

- **Trustworthy AI authoring.** Generation is structurally limited to approved
  dashboard nodes and reviewed semantic metrics, reducing the risk of invented
  SQL, joins, or business definitions.
- **Data sovereignty.** Warehouse credentials and business data remain in the
  customer's own network or cloud account.
- **No duplicate source of truth.** Queries run against data in place. Nodex
  does not ingest or retain a durable competing copy of the customer's numbers;
  the runtime may cache query results temporarily inside the customer's
  environment.
- **Intelligence at the point of decision.** Dashboards, alerts, and scheduled
  delivery can appear inside the tools and channels people already use.
- **Faster delivery with a stable contract.** Prompting accelerates authoring,
  while deterministic APIs, stable node identities, and semantic versioning
  protect consuming applications.
- **Estate-scale reuse.** One definition, artifact, and version stream can serve
  many sites through independently managed bindings.
- **Simpler operations.** One query runtime executes many inert manifests, so
  there is no separately deployed backend for every dashboard.
- **Deployment flexibility.** The same artifact supports several packaging and
  embedding modes without carrying environment-specific secrets or endpoints.

## Current boundaries

This specification is a draft. Enterprise readiness still depends on closing
gaps including SSO and provisioning, comprehensive RBAC, audit logging,
column-level security and PII masking, SOC 2 Type II, and content-governance
features. Reliable multi-site binding also depends on model interfaces being
added to bipp's modeling layer.

The current product operates on structured systems-of-record data. Documents,
emails, contracts, and other unstructured systems of content are outside its
present scope.
