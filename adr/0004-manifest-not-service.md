# ADR-0004 — Query manifest and shared runtime, not per-dashboard services

**Status:** Accepted · 2026-09-28

## Context

Each dashboard needs a backend: something that turns widget definitions into
queries against the customer's warehouse. "The backend is generated along with
the dashboard" admits two very different readings, which sound equivalent in a
design meeting.

The deployment context makes the difference severe: customers run the data plane
themselves, on premises we cannot reach, upgrading on their own schedule.

## Decision

A dashboard build emits a **declarative query manifest** — inert data, no
executable code — describing every query the dashboard needs, by reference to
bipp model entities.

Manifests are executed by **one versioned query runtime**, deployed once per
customer, serving all of their dashboards.

## Consequences

**Good.**

- **One executable to patch.** A vulnerability in the query path is fixed by one
  runtime release, and each customer upgrades one component to fix every
  dashboard they own.
- **Manifests contain no executable code or credentials.** Frontend bundles
  remain executable software with their own update requirements.
- **The manifest references reviewed models rather than arbitrary SQL.** Model
  correctness and runtime query-cost and fan-out limits are still required.
- **A compromised client cannot widen access** — it can only request queries the
  manifest already declares ([08-security.md](../08-security.md)).
- Operationally boring: one service to document, monitor, support, and version.

**Costs.** Dashboard capability is bounded by what the manifest format can
express and the runtime can execute. New query capability requires a runtime
release, which customers adopt on their own schedule — so capability rollout is
gated by the slowest upgrader, not by our release cadence.

## Alternatives considered

**Generate a deployable backend service per dashboard.** N customers × M
dashboards yields thousands of distinct services, an unknown number inside
customer premises, at unknown versions. A security fix becomes a fleet-wide
redeploy across infrastructure we neither own nor can enumerate. This is not a
patchable system, and the problem grows linearly with commercial success.
Rejected.

**Generate a service but centralise the sensitive parts in a shared library.**
Still requires rebuilding and redeploying every dashboard to ship a fix, and
relies on every customer's deployment pipeline being live. Rejected.
