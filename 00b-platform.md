# 00b — Platform baseline

Nodex Studio is not built from nothing. It sits on bipp Analytics, and anyone
deciding what to fund needs to see three things separately: what is inherited,
what is new, and what nobody has built yet.

## What bipp already provides

**In-database analytics.** Queries run directly against the customer's warehouse
— Redshift, BigQuery, Snowflake, Postgres, MySQL, SQL Server and others. No
cubes, no extracts, so a dashboard shows current data even across billions of
rows.

This is the capability the rest of the architecture depends on. Warehouse
credentials never leaving the customer's network (I8) is only possible because
nothing needs to be moved to be useful. A product that extracted would have to
hold the data, and would become a second system of record
([Product update](00a-product-update.md)).

**Data modeling layer.** Analysts define reusable models through a point-and-click
interface or in SQL, under Git version control, so the organization holds one
agreed definition per metric.

This is the semantic contract the AST binds to. It is why a generated query is
verifiable rather than trusted: the manifest can only reference metrics someone
already declared and reviewed, so it cannot express a wrong join or an unbounded
scan ([ADR-0004](adr/0004-manifest-not-service.md)). It is also why level 3 is a
prerequisite rather than a preference.

It is what secures the organization's business logic, and Nodex Studio makes that
guarantee stronger rather than weaker: because the manifest carries references
rather than SQL, business logic never reaches a client at all, including one
running inside someone else's web application ([Data plane](06-data-plane.md)).

**Visual SQL explorer.** Non-technical users build charts without code;
developers get a SQL editor. Data from several sources can be combined without
standing up a separate pipeline.

**Dashboards and alerts.** Dashboards are interactive and cross-filter every
chart at once. Reports can be scheduled by email as PDF or JPG, and email alerts
fire when a number crosses a threshold.

These live in the BI server, which means they work for dashboards viewed *in bipp*.
An artifact Nodex emits runs in the customer's own application against a query
runtime, so it cannot reach them — which is why monitors are specified in the
runtime rather than inherited
([Data plane](06-data-plane.md#monitors-alerts-and-scheduled-delivery)). The
capability is not new to the platform; its availability to a deployed artifact is.

**Deployment options.** Cloud by default, self-hosted on the customer's own
servers, or embedded in their web application. The self-hosted path is the
precedent for our data plane ([Data plane](06-data-plane.md)) — that model is
proven here, not invented by us. Nodex Studio narrows it deliberately: the
runtime always sits in the customer's own environment, and the hosting choice is
who operates it rather than where it runs.

## What Nodex Studio adds

| | bipp today | With Nodex Studio |
|---|---|---|
| Authoring | Point-and-click, or SQL | Prompts and direct manipulation, both editing one AST ([Studio](03-studio.md)) |
| Who can author | Analysts and developers | Anyone explores; developers publish ([Explore and publish](03-studio.md#explore-and-publish)) |
| Staying current | Queries return current data | Declared freshness, refresh intervals, and visible staleness ([Data plane](06-data-plane.md)) |
| Output | A dashboard inside the BI tool | A deployable, importable artifact the customer owns and versions (I1) |
| Distribution | One embed path | Six delivery modes, including npm libraries for four frameworks ([Distribution](05-distribution.md)) |
| Backend | A BI server | A declarative manifest executed by one versioned runtime (I9) |
| Public API | None | A per-dashboard API under mechanical semver ([Versioning](07-versioning.md)) |
| Rolling out across sites | One dashboard per site, built per site | One definition bound to many sites, one artifact, one version ([ADR-0010](adr/0010-definition-and-binding.md)) |
| Repeated structure | Charts built per site by hand | A repeater expands over the data (**I11**) |
| Alerts and scheduled reports | In the BI server, for dashboards viewed there | In the runtime, for dashboards deployed anywhere ([Data plane](06-data-plane.md#monitors-alerts-and-scheduled-delivery)) |
| Flagging a suspect number | Not supported | Annotations anchored to semantic coordinates, append-only (**I14**) |
| Maps | Not a chart type | A widget kind ([ADR-0011](adr/0011-geo-widget-kinds.md)) |
| Maturity reached | Level 3, Defined | Levels 4 and 5, Distributed and Generative |

The short version: bipp makes an organization's numbers trustworthy. Nodex
Studio takes those numbers to where decisions are made, and lowers the cost of
asking a new question.

## What neither provides yet

Stated plainly because it is better found here than in a procurement review.

### Blocks an enterprise sale

| Gap | Why it matters |
|---|---|
| SSO/SAML/OIDC and SCIM provisioning | Effectively mandatory above a few hundred seats. No SCIM means manual deprovisioning, which fails audit |
| RBAC over models and dashboards | "Who can see which model" is the first question a governance team asks |
| Audit logging | Currently an Enterprise-tier feature. Regulated buyers treat it as a baseline, not an upsell |
| Column-level security and PII masking | Required in healthcare and financial services before a pilot starts |
| SOC 2 Type II | A procurement gate rather than a feature, but it blocks the same conversations |

**Row-level security is currently sold as an add-on.** This one deserves separate
attention: the architecture in this document assumes RLS is present and
non-bypassable — it is load-bearing for the embed token design
([Security](08-security.md)) and for cache correctness
([Data plane](06-data-plane.md)). A security control that ships separately reads
to an enterprise buyer as an incomplete product, and reads to this architecture
as a dependency that might not be there. It should be standard.

### Fails deployments after the sale

- **Content organization** — folders, collections, tagging, search across
  content. Every BI deployment accumulates sprawl; ours accumulates it faster,
  because prompting makes dashboards cheap to create.
- **Certification** — a way to mark which dashboard is the trusted one. Without
  it, several dashboards answer the same question differently and the trust the
  modeling layer bought is spent again.
- **Usage analytics** — which dashboards are opened, by whom, how often. You
  cannot prune what you cannot see, and you cannot show value at renewal.
- **Lineage and impact analysis** — what breaks if this model changes. Analysts
  stop editing models they cannot reason about, and the semantic layer sets.

These matter more for us than for bipp alone. Generated dashboards are cheap, so
a customer reaches thirty of them faster than they would by hand, and sprawl
arrives sooner.

### Behind modern competitors

Natural-language query and generated narrative (ours to fill); a metrics API
serving certified definitions to other tools; caching and aggregate awareness,
which at billions of rows are cost controls as much as performance features;
period-over-period comparison, pivot and cross-tab; cohort and funnel analysis;
anomaly detection; drill-down *within* a dashboard.

Three have moved off this list and it is worth saying why, because each was a real
gap and none was closed by accident:

- **Write-back** is now annotations — bounded deliberately to commentary, never a
  mutation of the customer's numbers (**I14**).
- **Drill-through between dashboards** is a `link` node; drill-*down* within a
  widget is still absent, which is the narrower gap left above.
- **Delivery into Slack or Teams** is a monitor delivery transport rather than an
  email-only path.

Of the rest, the query-cost controls are already specified on our side — per-tenant
concurrency limits, row caps, timeouts, cost ceilings and repeater fan-out bounds
live in the query runtime ([Data plane](06-data-plane.md)).

### Deliberately absent

No ETL, no cubes, no extracts, and no SaaS application connectors. These are the
in-database architecture working as intended, not omissions. Adding connectors
for Salesforce or HubSpot would mean ingesting and storing, which contradicts the
stance and turns the platform into the second system of record it exists to avoid.
When a customer asks, the answer is that their pipeline tool lands the data and
we query it in place.

CSV and spreadsheet upload is the one honest exception: a common request, and a
real crack in the position. It is not currently supported and should be decided
deliberately rather than drifted into.

## Ownership

Most of the above is bipp's to close. The content-governance cluster — folders,
certification, usage analytics, lineage — is genuinely ambiguous, because it
degrades fastest under our usage pattern rather than bipp's. That is recorded as
an open decision (O6) and should be settled before the first customer passes a
few dozen generated dashboards.

**One new dependency runs the other way.** Binding a definition across an estate
needs **model interfaces** in the modeling layer — one declared shape that many
concrete models implement, so a site's data can be validated against it at
onboarding rather than guessed at
([ADR-0010](adr/0010-definition-and-binding.md)). Maps need geo field types in the
same layer ([ADR-0011](adr/0011-geo-widget-kinds.md)). Neither exists today, both
are bipp's to build, and the estate features do not work properly without the
first. Recorded as **O10**, and it is on the critical path in a way O6 is not.
