# ADR-0010 — One artifact per definition, never one per binding

**Status:** Accepted · 2026-09-28

## Context

A scorecard rolled out across a large estate is one page bound many times. Each
site shapes its data to a fixed format and points at its own source; the
definition itself does not change. Sites also vary: a KPI that exists at one
plant has no meaning at another.

The target is that adding a site takes days rather than months. That target is
about the rollout path, not the authoring surface — authoring is already cheap.

## Decision

**A dashboard is a definition and a set of bindings. It compiles to one
artifact.**

A **binding** is a per-site record: the concrete models this site's data lives in,
parameter defaults, which optional widgets it has locally, and theme. Bindings are
data held in the data plane, not AST.

The binding is selected at mount:

```js
mount(el, { endpoint, getToken, binding: 'plant-47' });
```

- The manifest carries **binding-resolved model references** rather than resolved
  model names. It stays inert data; resolution moves into the runtime.
- The runtime holds a **binding registry** and resolves it per request, under the
  same row-level security as everything else.
- **Bindings version independently of the definition.** Onboarding a site is not a
  change to the dashboard's public API and does not bump its semver.
- Widgets may be declared `optional`. A binding opts in. The generated public API
  types every binding-optional member as possibly absent, and the element reports
  what is actually present.

## Consequences

**Good.** One definition, one artifact, one semver stream, regardless of estate
size. A fix to the definition reaches every site at once. Adding a site touches a
registry row and a data source, which is what makes days rather than months
achievable.

**Bindings must version separately or the scheme collapses.** If adding a site
bumped the dashboard version, an estate onboarding sites continuously would emit
permanent version noise to every consuming team, and the semver signal — which
exists so a consuming developer can trust a minor bump — would be worthless
within a month.

**Optional widgets weaken the typed surface.** A consuming developer writing
against a possibly-absent member has to handle absence. This is the cost of one
artifact, and it is smaller than the alternative: typing per binding would mean a
package per binding.

**It depends on something we do not own.** "Conform your data to this fixed
format" is a **model interface** — one declared shape, many concrete models
implementing it — and it belongs in the modeling layer, which is bipp's. Without
it, binding validation degrades into per-site guesswork. Ownership is
**O10 (OPEN)**, of the same kind as O6.

## Alternatives considered

**One package per binding.** Straightforward, and gives each site a fully typed
surface with no optional members. It also gives 130 semver streams, 130 rebuilds
per definition change, and a registry no one can operate. Rejected.

**Copy the AST per site.** Each site gets its own dashboard, diverging from day
one. This is precisely the per-site sprawl that made the estate unmanageable
before migration, reproduced faster because prompting makes dashboards cheap.
Rejected.

**Bind at build time, one manifest per site.** Keeps the manifest fully resolved,
but a new site requires a build, and a definition change requires N builds.
Rejected — it trades an operational problem for a worse one.
