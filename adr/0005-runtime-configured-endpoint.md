# ADR-0005 — Endpoint and auth as runtime configuration

**Status:** Accepted · 2026-09-28

## Context

The same dashboard artifact must run against different query runtimes: a
customer's on-premise deployment, their staging environment, their production
environment. Multiplying six delivery formats by each customer's environment
count would make the build matrix unbounded.

## Decision

**Artifacts carry no endpoint and no credentials.** Both are injected at
initialisation:

```js
mount(el, {
  endpoint: 'https://analytics.acme.internal/q',
  getToken: () => acmeAuth.embedToken(),
  theme: acmeTheme,
});
```

## Consequences

**Good.** One artifact per dashboard version, regardless of topology or
environment count. A build can be promoted from staging to production without
rebuilding, so the bytes that were tested are the bytes that ship. Published
artifacts are inert — no secret can leak from a CDN bundle or an npm package,
which matters because those are the components most likely to end up somewhere
unintended.

**Costs.** The consuming developer must wire configuration, so the integration
has a required setup step rather than being drop-in. Misconfiguration becomes a
support category, and the failure must be diagnosable — an artifact pointed at
the wrong runtime should say so clearly rather than failing as a blank panel.

## Alternatives considered

**Bake the endpoint at build time.** Drop-in for the consumer, at the cost of a
distinct artifact per environment per format, rebuilds to promote between
environments, and a class of artifact that is no longer safe to publish. Rejected.

**Runtime discovery from a well-known location.** Removes explicit
configuration but introduces a discovery dependency and an ambient-authority
pattern in someone else's application. Rejected.
