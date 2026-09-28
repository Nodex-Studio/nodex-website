# 06 — Data plane

Everything in this document runs inside the customer's own environment. The
control plane holds no warehouse credentials (**I8**) and never proxies a query.
Nodex may *operate* the runtime on a managed plan, but it runs in the customer's
account either way — see below.

Two things in this document changed the runtime's character, and both follow from
I8 rather than from preference. Because the control plane cannot query the
warehouse, **anything that must run without a browser runs here** (**I13**):
threshold monitoring, scheduled delivery, and the evaluation behind them. And
because monitors need to remember what they have already fired, and annotations
need somewhere to live, **the runtime holds state**. It is no longer a pure
request-response service, which is the single largest operational change the
architecture has taken on — see
[State, deployment and upgrade](#state-deployment-and-upgrade).

## Where it runs and who operates it

Two independent questions. Conflating them is how a deployment conversation goes
wrong, because one of them is fixed and the other is a choice.

**Where it runs is not a choice.** The runtime sits in the customer's own network
or cloud account, always. This is I8, and it is what lets the product claim it
never holds the customer's data — a claim that would otherwise be
untrue the moment we offered hosting
([Product update](00a-product-update.md)).

**Who operates it is a choice.**

| | Self-operated | Nodex-managed |
|---|---|---|
| Runs in | Customer's network or cloud account | Customer's cloud account |
| Deployed and upgraded by | The customer | Nodex, through a scoped role |
| Credentials held by | The customer's secret store | The customer's secret store |
| Runtime state (monitors, annotations) held in | The customer's account | The customer's account |
| Upgrade pace | Customer's schedule | Nodex's, within an agreed window |
| Suits | Airgapped, regulated, or infrastructure-confident customers | Customers who want the capability without running it |

Because the runtime is a single versioned deployable executing inert manifests
(I9, [ADR-0004](adr/0004-manifest-not-service.md)), who operates it is a
deployment decision rather than an architectural one. Nothing about the manifest,
the query protocol, or the artifact changes between these columns.

### What Nodex-managed means concretely

- Nodex holds a **scoped role in the customer's cloud account** — enough to
  deploy, upgrade, monitor and restart the runtime. Not enough to read from the
  warehouse.
- **Warehouse credentials stay in the customer's own secret store.** Nodex
  configures the runtime with a reference to them, never the value, and cannot
  retrieve them through the role it holds.
- **Every action is logged in the customer's own account**, in their audit trail
  rather than one we show them.
- **The role is revocable by the customer at any time**, which stops managed
  operation and leaves the runtime in place, still running.

The operating principle is that Nodex operates the service without reading the
data passing through it. **O8 (OPEN)** is the honest exception: whether an
operator may read query results or result-bearing logs while debugging a
customer's incident. Convenient, occasionally the fastest path to a fix, and the
one hole in the claim above. Decide it deliberately and write it into the
contract rather than discovering it during an incident.

Runtime state widens O8 rather than adding a second question. The annotation
store holds customer-authored text — an executive writing *"this number is wrong,
finance is restating it"* — which is business-sensitive in a way a query result
row is not, and it sits at rest in a service Nodex operates. The role must
therefore be scoped to the service, not to its storage, and O8 must be resolved
to cover data at rest and not only results in flight.

### What it buys beyond convenience

Managed customers stay close to current, which shrinks the version-skew problem
that [Versioning](07-versioning.md) is largely about. The long tail of runtimes
eleven months behind is a property of self-operation, not of the architecture.

## The central decision: manifest, not service

When a dashboard is built, the build plane emits a **declarative query manifest**
— not a deployable backend service (**I9**,
[ADR-0004](adr/0004-manifest-not-service.md)).

The manifest is inert data describing every query the dashboard needs. It is
executed by **one versioned query runtime**, which the customer deploys once and
upgrades on their own schedule, and which serves every dashboard they have.

The alternative — generating a backend service per dashboard — sounds equivalent
in a design meeting and is operationally very different. N customers × M
dashboards produces thousands of distinct services, an unknown number of them
inside customer premises we cannot reach. The day an auth bug is found in the
query path, remediation is a fleet-wide redeploy across infrastructure we do not
own, to a version list we do not have. That is not a patchable system.

With a manifest: the security fix is one runtime release, the customer upgrades
one component, and every dashboard they own is fixed at once. The generated
artifact contains no executable code and no credentials, so it is not a patch
target at all.

**The manifest is a template, not a resolved plan.** Two things it deliberately
leaves unresolved — which models a site's data lives in (I12) and how many copies
of a repeated tile exist (I11) — are resolved by the runtime, per request. It
stays inert either way: a template is still data, and the client still cannot
author one.

## Manifest shape

Indicative:

```yaml
manifestVersion: "1.4"
dashboardId: d_9a21e4
astVersion: 47
minRuntime: "2.4.0"

binding:
  interface: plant_scorecard_v2   # the shape every binding must satisfy (O10)
  resolve: runtime                # never baked in (I12)

queries:
  - id: q_kpi_total_cost
    widget: w_7f3a91
    model: $binding.production    # a binding-resolved reference, not a model name
    metrics: [cost_per_device]
    filters: [$region, $period]
    maxAge: 60s

  - id: q_plant_keys              # the repeat key query
    repeater: w_3b81c7
    model: $binding.plants
    dimensions: [{ field: plant_code }]
    orderBy: [{ field: plant_code, dir: asc }]
    limit: 200                    # hard fan-out bound (O9)

  - id: q_cost_by_plant
    widget: w_88ffa1
    within: w_3b81c7              # lives inside the repeater
    model: $binding.production
    dimensions: [{ field: plant_code }, { field: month, grain: month }]
    partitionBy: plant_code       # ONE query, split after execution
    metrics: [cost_per_device]
    maxAge: 15m

monitors:
  - id: m_temp_excursion
    query: q_shipment_temp
    condition: { metric: temp_c, op: outside, range: [2, 8] }
    for: 5m                       # must hold this long before firing
    every: 5m                     # evaluation interval
    runAs: $service               # which identity — O11
    deliver: [qa_channel, site_oncall]

params:
  - { name: region, type: string[], required: false }
  - { name: period, type: daterange, required: false }
```

Note what is absent: no SQL, no table names, no join logic, no connection
details. The manifest references **model entities by name** — or, under a
binding, by the role a model plays in a declared interface. Resolving those into
SQL is the modeling layer's job, and it is pre-existing bipp functionality —
models, joins, metric definitions, and row-level security are already declared
there, under the customer's own git version control.

This is the reason this design is materially safer than prompt-to-SQL: the
generated layer never expresses arbitrary SQL, so it cannot express a wrong join,
a fan-out, or an unbounded scan. It can only reference metrics someone already
defined and reviewed.

It also means **business logic never ships to a client.** A dashboard running
inside a customer's own web application, served from a CDN, or imported into an
internal tool contains no join, no metric definition and no table name. The
organization's business logic stays in the modeling layer under its own version
control, and the artifact carries only references into it. That is a stronger
guarantee than keeping queries server-side: there is no query in the client to
begin with, so there is nothing to read out of a bundle.

## Binding resolution

A definition is bound to many sites and compiles to one artifact
(**I12**, [ADR-0010](adr/0010-definition-and-binding.md)). The runtime holds the
**binding registry** and resolves `$binding.*` references per request.

A binding record is small and entirely declarative:

```yaml
binding: plant-47
interface: plant_scorecard_v2
models:
  production: acme_plant47_production
  plants:     acme_plant_master
  quality:    acme_plant47_quality
params:
  region: [EMEA]
widgets:
  enabled: [w_88ffa1, w_7f3a91, w_c14b02]   # optional widgets this site has
theme: acme_emea
```

Four rules govern it:

**A binding is not a credential.** Naming a binding at mount does not grant
access to it. The embed token decides what its bearer may see, row-level security
applies exactly as it does everywhere else, and a request for a binding the
bearer is not entitled to is refused. Otherwise "one artifact for the whole
estate" would mean any site's dashboard could read any other site's numbers by
changing one string in the host application.

**Binding visibility is itself authorized.** The list of bindings is business
information — an estate roster. A site manager who may query plant 47 must not be
able to enumerate the other 129. The registry answers "may this identity use this
binding" and, separately and more narrowly, "which bindings may this identity
see".

**Validation happens at registration, not at first query.** When a binding is
registered, the runtime checks every model it names against the declared
interface — every field the definition references must exist, with a compatible
type. A site whose data does not conform fails during onboarding, with an error
naming the missing fields, rather than rendering a dashboard full of broken
widgets on its first Monday. This is what makes "conform your data to this
format" a checkable contract; without a model interface in the modeling layer it
degrades to per-site guesswork (**O10**).

**The binding is part of the cache key.** Non-negotiable, for the same reason the
RLS context is: two sites asking the same question with the same parameters are
asking about different data, and serving one the other's cached answer is a
cross-site leak that looks exactly like a correct result.

## Repeater expansion

A repeater's instances are enumerated when the query runs, never at build time
(**I11**, [ADR-0009](adr/0009-runtime-repetition.md)). Expansion is the
runtime's work, in two phases:

```
1. key query      q_plant_keys ──▶ distinct values of the repeat key
                                   (ordered, bounded by `limit`)
2. child queries  one grouped query per child widget, with the key as a
                  dimension and `partitionBy` naming it ──▶ partitioned into
                  per-instance results after execution
```

**Expansion must not become fan-out.** A scorecard with seventeen tiles across
130 plants is seventeen grouped queries, not 2,210 individual ones. The
`partitionBy` field is what makes this expressible declaratively: the runtime asks
one question per child widget and splits the answer, rather than asking the same
question 130 times with a different filter.

**The fan-out bound is enforced, and exceeding it is an error.** If the key query
returns more values than `limit`, the runtime refuses the request with an explicit
error naming the count and the bound. It does **not** silently render the first
200 — a dashboard that quietly shows 200 of 340 plants is a wrong number wearing
the costume of a right one, which is the failure mode this architecture treats as
the worst available ([Versioning](07-versioning.md#compatibility-contracts)).
The default bound is **O9 (OPEN)**.

**Key values become instance identity**, as `(repeaterId, keyValue)`
([02-ast.md](02-ast.md#instance-identity)). The runtime returns them with the
results, and they appear in event payloads. They are not enumerable in the public
API, because the public API cannot depend on data (**I4**).

**An empty key set is a rendering decision, not an error.** The AST's `empty`
field says whether the repeater hides itself or shows a placeholder. A site with
no plants yet is a normal state.

## Query runtime

One service. One version at a time per customer. Responsibilities, in the order
they execute:

1. **Serve manifests.** Load the manifests for deployed dashboards.
2. **Authenticate.** Validate the embed token; extract identity and row-level
   filter context ([08-security.md](08-security.md)).
3. **Resolve the binding.** Map `$binding.*` references to concrete models, and
   refuse a binding this identity may not use.
4. **Expand repeaters.** Run key queries, bound the fan-out, plan the partitioned
   child queries.
5. **Plan.** Resolve the manifest query plus the request's params and filters
   against the modeling layer.
6. **Delegate SQL generation** to the modeling layer, with row-level security
   applied as a non-bypassable predicate.
7. **Execute** against the warehouse, in-database, no extract.
8. **Enforce limits** — per-tenant and per-user query concurrency, row caps,
   timeouts, cost ceilings, and repeater fan-out.
9. **Cache** by (query, resolved params, binding, RLS context). Both the binding
   and the RLS context must be part of the key; omitting either is a data leak
   that renders as a plausible number.
10. **Audit.** Log who ran what, when, with which filters, under which binding.
11. **Evaluate monitors** on their schedule, and hold their firing state.
12. **Deliver** notifications and rendered reports through configured transports.
13. **Store annotations**, and return them alongside the results they annotate.

It also refuses manifests it is too old to execute (`minRuntime`), with an
explicit version error rather than a partial render
([07-versioning.md](07-versioning.md)).

![Runtime query path](diagrams/query-path.png)

### Two roles, one deployable

Responsibilities 11 and 12 are not request-driven, so they run on a timer rather
than on a request. They are the **same deployable in a different role**
(`--role=web`, `--role=scheduler`), not a second service.

This matters because I9 exists to keep exactly one executable to patch. Splitting
the scheduler into its own service would double the patch target and halve the
value of the invariant, for no architectural gain — it is the same code reading
the same manifests against the same models.

Two operational consequences follow, and neither is optional:

- **Scheduler work must be single-flight.** Three replicas of the scheduler role
  must produce one alert, not three. Leader election, or a lease on each monitor.
- **A monitor's schedule is not a guarantee of its evaluation.** Restarts,
  upgrades, and lease handovers mean a monitor can be late. It must record when it
  last *actually* evaluated, and that must be visible — see below.

## Query protocol

The wire protocol between artifact and runtime is a long-lived public contract.
A dashboard pinned into a customer's internal application two years ago is still
calling it ([07-versioning.md](07-versioning.md#four-cadences)).

- Explicitly versioned, negotiated at handshake.
- Additive changes only within a major version.
- The runtime advertises its capabilities — protocol version, and whether it
  supports bindings, repeaters, monitors and annotations — and the client degrades
  predictably against an older runtime rather than failing opaquely. A dashboard
  using repeaters against a runtime that does not expand them is a `minRuntime`
  refusal, not a degradation: there is no correct partial rendering of it.
- Requests carry: query id, params, filter values, binding, embed token, protocol
  version.
- Requests never carry: SQL, model definitions, credentials, or anything the
  client could forge to widen its own access.

The last point is the important one. A client can only ask for queries the
manifest already declares, with parameter values the runtime validates. It cannot
construct a new query. Compromising the frontend does not widen data access
beyond what that dashboard was already permitted.

**The protocol has exactly one write verb, and it writes annotations
(I14).** Annotations are the only thing a client may create, and creating one
grants no additional read access: an annotation is visible to precisely those who
can already see the number it is attached to. There is no verb that writes to the
warehouse, the models, or the manifest, and adding one would make the platform the
second system of record it exists not to be
([Product update](00a-product-update.md)).

## Freshness and refresh

In-database execution means a query returns current data. It does not, on its
own, mean a dashboard stays current — a page that loaded an hour ago shows
hour-old numbers unless something refreshes it. For a dashboard people use to
monitor anything, silent staleness is the failure that matters, because a stale
number looks exactly like a fresh one.

Three mechanisms, and they are separate on purpose:

**Declared freshness.** Each query in the manifest carries a `maxAge`. It is the
cache's authority: a request arriving after `maxAge` bypasses the cached result
rather than serving it. Freshness is a property of the query, not of the client
asking, so a fast-moving operational metric and a monthly financial rollup do not
have to share a policy.

**Refresh interval.** The host application sets it at mount, because only the
host knows whether this dashboard is on a wall or in a settings page:

```js
mount(el, { endpoint, getToken, binding, refresh: 30_000 });  // ms; omit for manual
```

**Observable currency.** Every response carries `asOf` — the time the underlying
result was produced, not the time it was served from cache. Components expose it,
so a dashboard can state its own age rather than implying it is live. A widget
whose data is older than its `maxAge` and has failed to refresh must say so
visibly; it must never keep displaying a stale number as if it were current.

**Monitors never read the cache.** A monitor evaluates against a fresh result,
always. Firing an alert — or, worse, *not* firing one — on a cached value is
indistinguishable from a bug and destroys trust in the whole alerting surface
faster than a missed alert does.

**O7 (OPEN)** — whether the runtime pushes updates (server-sent events or
WebSocket) instead of the client polling. Polling is simple, works through every
proxy a customer has, and ships sooner; it also scales badly with widget count
and wastes warehouse spend on queries nobody is watching. Push is the honest
answer for genuinely live dashboards and a significant amount of work in a
customer-operated runtime. Polling first, with the protocol versioned so push can
be added without breaking pinned clients ([Versioning](07-versioning.md)).

## Monitors: alerts and scheduled delivery

A threshold crossing has to be noticed when nobody is looking at the dashboard,
and a scheduled report has to be produced when nobody asked for it. Neither can
happen in a browser, so by **I13** both happen here.

This is not a convenience. The control plane cannot query the warehouse (I8), so
there is no design in which Nodex cloud evaluates a customer's thresholds. Alerting
is data-plane work or it does not exist.

**A monitor is a manifest entry, not a widget.** It names a query, a condition, an
evaluation interval, a hysteresis window, an identity, and one or more delivery
targets. It is authored in Studio and compiled like everything else, so it is
versioned with the dashboard and cannot reference a query the manifest does not
declare.

**Firing state lives in the runtime.** A monitor that evaluates true every five
minutes must notify once, not 288 times a day. That requires remembering what has
already fired, and a hysteresis window (`for`) so a metric oscillating across a
boundary does not emit a stream of alerts. Recovery is also an event: a monitor
that stops being true should say so, because an alert with no resolution leaves
someone wondering.

**Silence must be distinguishable from health.** A monitor that cannot evaluate —
warehouse unreachable, model changed underneath it, lease not held through an
upgrade — must escalate the *failure to evaluate*, separately from the condition
it watches. Silence reading as "all clear" is the specific way monitoring systems
betray the people relying on them. Each monitor therefore exposes when it last
successfully evaluated, in the runtime's health output alongside its version.

**Delivery transports are the operator's configuration, never the artifact's**
(**I7**). Email through the customer's own relay, a webhook, or a chat channel.
Airgapped deployments constrain this hard: a customer with no egress has an
internal SMTP relay and nothing else, so no transport may be assumed present and
a monitor whose transport is unconfigured must fail loudly at deployment rather
than silently at 3am.

**Rendered delivery needs a renderer in the data plane.** A scheduled PDF means
loading the artifact, waiting for its queries, and capturing it — a headless
browser inside the customer's network. It is the heaviest single dependency this
document adds, and it is the same component a server-rendered map would need
([ADR-0011](adr/0011-geo-widget-kinds.md)); the two must share it rather than each
growing one.

**Which identity a monitor runs as is genuinely undecided.** The embed-token model
([08-security.md](08-security.md#embed-tokens)) assumes a user, a host
application, and a short expiry. A scheduler has none of those. The candidates —
the recipient's row-level security, the author's, or a declared service principal
with its own RLS context — differ in who can cause what data to be sent to whom,
which makes it a contract question rather than an implementation detail.
**O11 (OPEN)**, and it blocks implementation rather than merely informing it.

**A monitor never writes to the warehouse (I14).** It reads, compares, and
notifies. It does not update a status column, tick a workflow, or acknowledge
itself in the customer's system of record.

## Annotations

A number that looks wrong needs somewhere for the person who noticed to say so.
Annotations are the only write in the system (**I14**), and they are the
customer's commentary — never a copy of, or an edit to, the number itself.

**Annotations anchor to semantic coordinates, not to node ids.**

```yaml
anchor:
  model:   plant_scorecard
  metric:  cost_per_device
  at:      { plant_code: P-4471, month: 2026-09 }
body:    "Restated — September included two weeks of the pilot line."
author:  u_3f81   # from the embed token, never client-supplied
at:      2026-09-28T11:04:00Z
```

This is the decision that makes the feature durable. An annotation keyed to
`w_7f3a91` is orphaned the first time someone restructures the page, and invisible
on every other dashboard that shows the same cell. An annotation keyed to the
coordinate survives the widget being moved, renamed, or deleted, appears wherever
that cell appears, and works from an ephemeral exploration as readily as from a
published dashboard — which is what keeps **I10** intact, because nothing about it
depends on a published node existing.

**The store is append-only.** Edits and deletions are new entries superseding old
ones. "Version-controlled comments" is the requirement, and an append-only log is
the whole of it.

**Visibility follows the number.** An annotation is readable by exactly those who
can read the cell it annotates, which means the annotation store is subject to the
same row-level security as the query that produced the cell. Getting this wrong
leaks the numbers themselves: *"Restated — September included two weeks of the
pilot line"* tells a reader who cannot see plant P-4471 a great deal about plant
P-4471.

**Authorship comes from the token, never from the request body.** A client that
could name its own author could forge attribution on a record executives make
decisions from.

**Moderation and retention are the customer's.** Annotations are their content in
their store, under their retention policy. The platform provides an append-only
log and RLS; deciding who may resolve, redact or export is theirs.

**O12 (OPEN)** — whether the store is embedded in the runtime or a
customer-provided database. Embedded is one less thing to operate and suits the
single-binary path; external is the only honest answer for a customer who needs
annotations inside their own backup, retention and legal-hold regime, which
regulated buyers will.

## Authentication and row-level security

The customer's host application mints a short-lived signed **embed token**
server-side, carrying user identity and any row-level filter context. The
frontend receives it through `getToken()`
([05-distribution.md](05-distribution.md#runtime-configuration)) and presents it
with each request.

Row-level security is enforced **in the runtime, by the modeling layer**, never
in the client. The client cannot see, influence, or remove it. A token is scoped
to one user, one dashboard, and a short expiry.

Three additions follow from this document:

- **The token also scopes bindings.** Which bindings its bearer may use, and
  which they may see listed, are decided here — not by what the host application
  passes to `mount()`.
- **Annotation reads and writes run under the same context** as the query whose
  cell they attach to. There is no separate annotation permission model to get
  out of step with the data one.
- **Scheduled work has no token**, because it has no user and no host
  application. It needs a principal of its own, and which one is **O11**.

## State, deployment and upgrade

The runtime is a normal service deployed into the customer's environment, with
access to their warehouse and their model repository, upgraded when they choose —
or, on a managed plan, when Nodex does within the agreed window.

It now holds state, and the kinds differ in how badly losing them hurts:

| State | Losing it means |
|---|---|
| Query cache | Nothing. Cold queries, higher warehouse spend for a while |
| Monitor firing state | Duplicate alerts, or a missed recovery notification |
| Annotations | Permanent loss of customer content |
| Binding registry | The estate stops resolving until it is restored |

Only the first is disposable. The rest need backup, restore, and a retention
policy, and because they live in the customer's account those are the customer's
to run — which has to be said during deployment rather than discovered during an
incident.

For self-operated customers we cannot force an upgrade, so the release process
must assume a long tail of versions in production:

- Published version support window and deprecation policy
  ([07-versioning.md](07-versioning.md)).
- Security releases backported across the support window.
- **State migrations are part of the upgrade**, forward-only and versioned, with
  the same discipline as AST migrations ([02-ast.md](02-ast.md#schema-versioning)).
  A runtime that cannot migrate its state refuses to start rather than running
  against a schema it half-understands.
- Offline/airgapped installation path — some customers choosing on-premise are
  choosing it precisely because they have no egress.
- Health and version reporting that the customer can see, so they know how far
  behind they are without us telling them — now including each monitor's last
  successful evaluation and the scheduler's lease holder.

**O4 (OPEN)** — packaging, and statefulness has changed this decision rather than
merely complicated it. A single binary is still far easier for the airgapped and
the Kubernetes-averse, but it now needs an embedded store, and "easy to install"
becomes "easy to install and nobody backs it up". Helm suits customers already on
Kubernetes, makes upgrades declarative, and gives persistence and leader election
to platforms built for both — at the cost of the buyers least able to run
Kubernetes. Shipping both is plausible; the state layer must then be pluggable
from the start, which is a decision that cannot be deferred as cheaply as the
packaging itself. It should still follow the first ten customers rather than
precede them, but the pluggable-state question should not.
