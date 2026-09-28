# Editorial direction

The current product is a SaaS dashboard-building studio. Customers can embed the
studio itself in their applications or use an independently deployed application.
AI chat guides dashboard creation and iterative editing inside the studio.

- Start from the business question and the experience of building a dashboard.
- Explain product, architecture, and benefits in business terms.
- Treat arbitrary dashboards as an extensibility ambition, not a promise of
  unlimited capability or guaranteed AI correctness.
- Recommend a managed application project with versioned source/configuration,
  isolated backend builds, disposable versioned bundles, and native mounting in the studio DOM.
  Describe these as proposals to validate, not implemented capabilities.
- The user rejected iframe-based dashboard rendering. Use a native dashboard host
  with mount, readiness, context/state transfer, and disposal responsibilities.
  Calls go directly through the Nodex SDK to the authorized backend gateway.
- Use a persistent host runtime and classic IIFE bundles that register factories,
  not a fresh native ES-module import per revision. Dispose instances, unregister
  retired factories, and release side effects and references. Store history on
  the backend and reload bundles for rollback. Check for revision-specific imports
  in dependencies. Normal updates swap without refreshing the Studio. Use per-instance
  host-managed resource scopes, bounded replacements, and dashboard-only recovery
  first; full-page refresh is an exceptional shared-page failure fallback. Test repeated
  updates for retained resources; neither HMR nor cleanup guarantees immediate
  collection, leak-free execution, or no future refresh.
- Native modules share the studio page's browser privileges. Do not claim that
  SDK restrictions, testing, error boundaries, or Shadow DOM sandbox arbitrary
  JavaScript. Approved releases are trusted frontend code. Build isolation remains.
- Distinguish embedding the interface from hosting its backend services.
- Reuse bipp backend capabilities where validated; do not invent platform gaps
  or claim that integrations have already been implemented. Nodex has its own
  studio interface, dashboard canvas, and visual components. Do not suggest reuse
  of bipp’s UI, dashboard editor, charts, embedding UI, or bippDash definitions.
- Keep the founder's reading path concise and specific. The user now explicitly
  wants the source/build/runtime lifecycle, incremental delivery, and custom
  interactions explained. Include those decisions without exhaustive schemas.
- Generate full browser applications for expressive freedom. Component libraries
  accelerate creation but must not define the ceiling of supported layouts and
  behavior. Do not restore the superseded schema-only compilation architecture.
- Do not include the superseded technical appendix in the current HTML.
- The user authorized consolidation and deployment on 29 September 2026.
- Position bipp as the existing analytics foundation, not a hypothetical vendor.
  Distinguish demonstrated workflows, published capabilities, and unverified APIs.
- Reuse its modeling, SQL generation, access controls, and compatible backend
  delivery services where interfaces permit. Descriptions of existing bipp
  screens are evidence only, not proposed Nodex frontend dependencies.
- Keep conversational authoring separate from greater rendering freedom.
- Distinguish model development and release from dashboard editing. Preserve
  a path to snapshot rendering, but verify whether bipp delivery can consume it.
- Distinguish state changes, configuration edits, and code rebuilds. Ordinary
  dashboard interactions execute program logic, not repeated AI calls.
- Do not promise automatic full visual editing of arbitrary code, preservation
  of all state after code changes, or backend capabilities from frontend code.
- The user explicitly authorized deployment of the current overview and detailed
  technical reference. This does not imply publishing every subsequent revision.

The overview source is 00-executive-summary.md. The new detailed reference is
html/technical.md with its companion contracts and presentation files. Earlier
numbered specifications, ADRs, and diagrams remain historical and excluded.
