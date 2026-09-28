# 07 — Versioning and release

## Three cadences

The platform releases on three independent clocks. Conflating them is the most
expensive mistake available here, because two of the three are outside our
control.

| | Cadence | Controlled by | Version skew |
|---|---|---|---|
| **Control plane** (Studio, build) | Continuous | Nodex | None — one version live |
| **Query runtime** (customer premises) | Customer-paced | Customer | Months to years |
| **Exported artifacts** (npm, CDN) | Pinned at install | Consuming developer | Indefinite |

A realistic steady state: Studio is on this week's build, a customer's runtime is
eleven months old, and a team inside that customer has a dashboard package pinned
from before the runtime was last upgraded. All three must interoperate, and none
of them can be forced.

Two consequences follow, and they are the spine of this document:

- **The AST schema and the query protocol are long-lived public contracts**, not
  internal formats. They are versioned explicitly and negotiated at runtime.
- **The exported package's public API is a contract with a human** — the
  consuming developer, whose code we cannot see and cannot regenerate.

![Three release cadences](diagrams/version-cadences.png)

## Mechanical semver

Because the public API is a deterministic function of the AST (**I4**) and node
ids are stable (**I5**), the version bump is computed, not judged:

```
AST(n-1) ──┐
           ├──▶ shell diff ──▶ API diff ──▶ semver bump ──▶ release gate
AST(n)   ──┘
```

| AST change | API effect | Bump |
|---|---|---|
| Widget added | New handle, new event source | minor |
| Param added (optional) | New optional prop | minor |
| Widget title changed | None — ids are stable | patch |
| Layout reordered | None | patch |
| Interior regenerated | None | patch |
| Param renamed or re-typed | Prop renamed / re-typed | **major** |
| Widget deleted | Handle removed | **major** |
| Exposed `::part()` removed | Consumer CSS breaks | **major** |

Enforced in CI by diffing the generated `.d.ts` between builds (api-extractor or
equivalent). A major bump requires explicit acknowledgement from the authoring
developer, in Studio, at the moment they make the change — with a plain statement
of what breaks:

> Renaming this parameter is a breaking change for 3 applications importing
> `@nodex/dashboard-sales`. They will need a code change to upgrade.

That message is the entire point of the machinery. Without it, an authoring
developer has no way to know that a rename in a visual tool is an API break in
someone else's build.

## Compatibility contracts

### AST schema

Additive changes are minor. Removal or re-typing is major and ships with a
forward-only migration, applied eagerly in the control plane
([02-ast.md](02-ast.md#schema-versioning)). Runtimes never migrate ASTs at read
time.

Each built artifact declares `minRuntime`. A runtime too old to execute a
manifest refuses it with an explicit version error — never a partial render, and
never a silently wrong number, which is the worst possible failure in an
analytics product.

### Query protocol

Negotiated at handshake; the runtime advertises capabilities and the client
degrades predictably. Additive within a major version
([06-data-plane.md](06-data-plane.md#query-protocol)).

### Public surfaces, enumerated

Everything here is under the compatibility policy. Everything not here is
internal and may change on any build:

- Custom element tag names
- Properties, attributes, and their types
- Custom events and payload shapes
- Named slots
- CSS custom properties (theme tokens)
- Exposed `::part()` names
- The `mount()` options object
- The iframe `postMessage` protocol
- The query protocol
- The AST schema

The list should stay short. Every entry is something we cannot change for the
length of the support window.

## Support windows

Published, not implied:

- **Query runtime** — security fixes backported for N months; feature
  compatibility with control plane for M months. Both stated publicly; customers
  plan upgrades around them.
- **Query protocol major versions** — supported for at least one full runtime
  support window past deprecation, because a pinned artifact outlives the runtime
  it was built against.
- **Exported packages** — the customer owns the upgrade decision entirely. We
  guarantee that a package built against protocol vN keeps working against any
  runtime advertising vN.
- **CDN URLs** — immutable and permanent. Published bytes are never changed or
  removed. Withdrawing a version breaks production pages we cannot see.

Deprecations are announced with a date, surfaced in Studio for the authoring
developer and in the runtime's health output for the operator. Nothing is removed
without both having been told.

## Release flow

```
AST change in Studio
  └─ build (reproducible, cached by AST hash)
  └─ API diff vs. previous release
  └─ semver computed
        ├─ patch/minor ──▶ publish
        └─ major ──────▶ explicit acknowledgement required
  └─ publish
        ├─ npm (private registry, scoped)
        ├─ CDN (immutable, versioned, SRI)
        ├─ standalone bundle
        └─ query manifest ──▶ customer's runtime
  └─ audit record: who changed what, what it broke, who acknowledged it
```

Manifest and frontend are published together and version-matched. A frontend must
never run against a manifest from a different dashboard version — the failure
mode is a chart that renders successfully with the wrong numbers, which nobody
catches.
