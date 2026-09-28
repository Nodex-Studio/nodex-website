# 08 — Security

## Trust boundaries

```
┌─ bipp cloud (multi-tenant) ──────────────────┐
│  Studio · AST store · prompt pipeline        │
│  build plane · package registry              │
│  holds: ASTs, prompts, generated artifacts   │
│  never holds: warehouse credentials, query   │
│               results, end-user PII          │
└───────────────────┬──────────────────────────┘
                    │  artifacts + manifests only
                    │  (no runtime data path)
┌───────────────────▼──────────── customer network ─┐
│  host application ─── mints embed tokens          │
│         │                                         │
│  dashboard artifact ──▶ query runtime             │
│                             │                     │
│                        modeling layer             │
│                             │                     │
│                          warehouse                │
│  holds: credentials, data, results                │
└───────────────────────────────────────────────────┘
```

The boundary is crossed only by build artifacts moving in one direction. **No
query ever crosses it.**

![System context and trust boundaries](diagrams/system-context.png)

## No public query API

Customer-managed frontends query a customer-operated runtime, never bipp cloud.
This is a deliberate product decision and it removes an entire class of exposure
that would otherwise be the largest surface in the system.

Had exported dashboards been able to query bipp cloud, we would need a public,
internet-facing, multi-tenant query API: embed-token validation for every
customer, per-tenant CORS origin allowlists, per-tenant rate limiting and query
cost caps, and cross-tenant isolation on a path reachable from any browser on the
internet. Every one of those is a place to get multi-tenant isolation wrong.

None of it exists, because the data path never leaves the customer's network.

The trade-off is honest and should be stated to customers: **every export format
requires the customer to run the query runtime.** A customer who wants a single
widget in an internal app must still deploy infrastructure. That is a real
commercial constraint, and it is the price of the property above.

## Credentials

**Warehouse credentials never leave the customer's network (I8).** They are held
by the query runtime and the modeling layer, both customer-operated. The control
plane has no field for them, no code path that accepts them, and no ability to
proxy a query.

Studio's preview needs data, and gets it the same way everything else does:
through the customer's own runtime, over a customer-configured development
connection, with the authoring developer's own identity and row-level security
applied. The preview is not a privileged path.

**Artifacts contain no secrets (I7).** A published CDN bundle or npm package is
inert: no endpoint, no token, no connection string. This is worth restating here
because artifacts are the things most likely to end up somewhere unintended — a
public registry, a customer's public CDN, a decompiled bundle.

## Embed tokens

```
end user ──▶ customer's host app
                  │ authenticates the user (their IdP, their session)
                  │ mints a signed token, server-side:
                  │   { sub, dashboardId, rlsContext, exp, aud }
                  ▼
            dashboard artifact ──▶ query runtime
                                      validates signature, expiry, audience
                                      applies rlsContext via modeling layer
```

Rules:

- Minted **server-side only**. A token mintable in the browser is not a token.
- Short-lived, with refresh through `getToken()`.
- Scoped to one user and one dashboard.
- Signed with a key the customer controls; the runtime validates against it.
- `rlsContext` is applied by the modeling layer as a non-bypassable predicate.
  The client cannot read, alter, or drop it.

## What a compromised client can do

Worth stating explicitly, because it is the payoff of the manifest design
([06-data-plane.md](06-data-plane.md)):

A client can only request queries that its manifest already declares, with
parameter values the runtime validates against declared types and the token's
RLS context. It cannot compose a new query, reference a model it was not given,
remove a filter, or widen its own scope.

So compromising the frontend — an XSS in the host page, a tampered bundle, a
malicious browser extension — yields **no more data access than that dashboard
already had for that user**. This is not true of any design where the client
sends SQL or where query construction happens browser-side.

## Origin controls

For iframe and web component modes, where our code runs inside a page we do not
control:

- `postMessage` messages are origin-checked against an allowlist configured per
  deployment; unrecognised origins are dropped silently.
- The runtime applies a CORS allowlist per deployment. It is customer-configured,
  because only the customer knows their internal hostnames.
- Framing controls (`X-Frame-Options` / CSP `frame-ancestors`) are set by the
  customer for their standalone and iframe deployments; we document the required
  configuration rather than guessing it.

## Tenant isolation in the control plane

The control plane is multi-tenant and holds authored IP — ASTs, prompts,
generated artifacts — even though it holds no customer data.

- Tenant scoping enforced at the data access layer, not in request handlers.
- Prompt context is assembled from one tenant's models only. A prompt must never
  be able to surface another tenant's model names, metric definitions, or
  dashboard structure through the LLM context window.
- Package registry namespaces are per-tenant and private by default.
- Build isolation: one tenant's build cannot read another's AST or artifacts.
- Full audit log — who authored, who built, who published, who acknowledged a
  breaking change ([07-versioning.md](07-versioning.md)).

**O5 (OPEN)** — storing ASTs in the customer's own git rather than the control
plane reduces this surface considerably, and fits customers who chose on-premise
specifically to keep authored IP in-house. See [02-ast.md](02-ast.md#storage).

## Supply chain

Artifacts are executable code running inside customers' applications, which makes
the build plane a high-value target.

- Reproducible builds — the same AST and toolchain produce identical output, so a
  tampered artifact is detectable by rebuild.
- SRI hashes published for every CDN release.
- Signed packages; published provenance attestation.
- Immutable published versions. Bytes at a published URL never change.
- Dependency pinning and review for anything entering the generated bundle. The
  reactive runtime and the chart library (**O1**, **O2**) will be loaded into
  every customer's application, and should be chosen with that in mind.
