# Native application architecture

## Architecture decisions

This is a detailed **proposed implementation**, not documentation of an existing Nodex API. Contract version **v1-draft**. bipp interface availability must be verified before implementation. Nodex owns its UI, charts, dashboard host, and authoring experience; bipp contributes backend analytics only.

| Decision | Proposed default | Consequence |
| --- | --- | --- |
| Rendering | Disposable IIFE bundles registered with a persistent native host | No dashboard iframe; generated code shares page privileges |
| Authoring | One orchestrator and one coding agent | Tool-controlled edit / test / repair loop; no agent swarm required |
| Source of truth | Versioned application source plus configuration | Chat supplies context, not executable application state |
| Build | Isolated backend worker with pinned toolchain | Reproducible artifacts; no compiler shipped to dashboard viewers |
| Delivery | Approved immutable releases; authenticated script route | The shell registers a factory without rebuilding itself |
| Data | Nodex SDK → backend gateway → bipp adapter | Authorization and service credentials remain server-side |
| First runtime | Self-contained React / TypeScript application | Separate root per dashboard; no cross-root React objects |
| Initial scope | Read-only analytics and drilldown | Writes, arbitrary server functions, and scheduled rendering are later contracts |

<aside class="callout warning"><strong>Non-negotiable trust trade-off.</strong> Native modules are trusted frontend code, not sandboxed plugins. They can affect the studio DOM, browser storage, and requests available to page scripts. Neither an SDK nor code scanning makes hostile same-page JavaScript safe. If the product requires executing untrusted code with containment, this architecture must change.</aside>

## System topology

<!--TOPOLOGY-->

The browser holds the studio shell, native dashboard host, and generated application. The control backend manages identity, projects, runs, approval, events, and publication. Build workers and browser-test workers run outside that backend with resource and network limits. Artifact storage is private; an authenticated delivery route serves approved bytes. The data gateway authorizes requests and delegates to server-only adapters.

Start with a modular control service plus independently scalable workers. A queue separates long-running generation and builds from HTTP requests. A relational database stores metadata; source storage retains immutable trees; object storage retains releases and diagnostics. These are deployment roles, not a requirement for a microservice per box.

| Component | Owns | Must not own |
| --- | --- | --- |
| Studio shell | Chat, navigation, project controls, user session | bipp credentials, compiler execution |
| Dashboard host | Script loading, bounded factory registry, lifecycle, styles, revision selection | Business query authorization |
| Orchestrator | Run state, budgets, cancellation, tool policy | Unrestricted execution in the control server |
| Coding agent | Proposed edits and repairs | Self-approval, role changes, direct production deployment |
| Build/test worker | Disposable checkout, compilation, diagnostics | Production secrets or broad network access |
| Release service | Provenance, checks, approval, immutable manifest | Approval based solely on an agent’s assertion |
| Gateway + adapter | Tenant/user authorization, permitted operations, query limits | Browser-provided tenant identity as authority |

## From studio prompt to visible dashboard

Your prompt starts a background authoring job. That job produces an approved dashboard bundle, which Nodex loads and mounts directly inside the studio. **The studio itself is not rebuilt.** This is the end-to-end workflow for the proposed implementation, including the approval gate and failure paths.

Example request: “Build a sales dashboard with monthly revenue and a supplier graph. Double-clicking a supplier should show its facilities.”

<!--PROMPT_WORKFLOW-->

### 1. Submit the prompt and create a run

The studio sends the project ID, prompt, current source revision, and optionally the selected component to the authoring API. It includes the project ETag and an idempotency key. The backend authenticates the session, checks authoring permissions, and verifies that the request targets the current draft. A retry with the same key does not create a duplicate job.

The backend persists a run, queues it, and returns its run ID immediately with HTTP 202. The chat displays the run’s progress. The existing dashboard remains visible; a new project shows an empty canvas until its first candidate is ready.

### 2. Assemble the agent’s working context

A background worker claims the job. The orchestrator gathers relevant source files and configuration, permitted bipp model metadata, approved metric definitions, Nodex SDK documentation, approved libraries, and relevant conversation history or diagnostics. The agent receives scoped tools rather than unrestricted platform access.

If “revenue” has several possible meanings, the workflow pauses for clarification before editing. In the first version, a clarification ends the planning attempt without a candidate; the studio records the question and submits the answered request as a new run against the current draft. This avoids silently inventing a metric and does not require an undocumented resume API.

### 3. Plan the application change

The agent identifies the revenue view, supplier graph, required data operations, double-click behavior, and loading, empty, and error states. It plans targeted changes so an existing dashboard’s unrelated work is preserved.

The agent checks whether the necessary data operations are available. Frontend code cannot create a missing bipp API or backend permission. If facilities cannot be queried through an approved operation, Nodex reports the gap or offers a supported alternative instead of producing a graph that only pretends to work.

### 4. Create an isolated workspace and edit source

The backend checks out the specified revision into a temporary workspace. A new project starts from a Nodex scaffold; an existing project starts from its versioned application source. The agent patches components, layout, styles, SDK data bindings, interaction handlers, and tests through scoped tools.

These edits affect only the candidate workspace. They do not modify the studio shell or the currently visible dashboard. The original base revision is retained for the later concurrency check.

### 5. Compile the candidate on the backend

The orchestrator sends the candidate to an isolated build worker. It resolves approved pinned dependencies, checks types and build policy, and compiles a classic JavaScript bundle in IIFE format. The output includes CSS, assets, and a manifest tying the artifact to its source revision and runtime contract.

The bundle registers a dashboard factory when loaded; it is not a complete copy of Nodex. Revision-specific dependencies remain inside its disposable scope. The persistent studio host and SDK do not need recompilation for every edit.

### 6. Test, diagnose, and repair

A separate test environment executes the candidate before it reaches the user’s studio. Checks cover rendering, required-view readiness, approved data operations, agreed calculations, double-click expansion, error states, and cleanup.

Failed checks return diagnostics to the agent for a bounded edit → build → test loop. Exhausting the retry, time, or cost budget ends the run with a useful failure report while retaining the existing dashboard. Cancellation prevents promotion of late results. If the draft has changed since the run began, the candidate must be reconciled or retried against the newer revision rather than silently overwriting it.

### 7. Persist and approve the release

The backend persists successful candidate source, immutable build artifacts, runtime compatibility, and test evidence. The release service records a pending release with a precise source/build identity.

**The current proposal requires reviewer approval before generated code runs in the studio page.** The agent cannot approve its own output. The studio shows “Awaiting approval” until that decision is recorded. Future automatic approval would require an explicit policy decision; a passing build is not automatic approval. This gate reflects the fact that native code shares the studio’s browser privileges. Approval still does not prove that code is safe.

### 8. Notify the studio and reconcile release state

After approval, the backend emits a `release.approved` event containing the project, run, release, and event sequence. The event does not contain the bundle itself.

The studio checks that the result belongs to its currently desired edit, re-fetches authoritative release status and the manifest, and verifies access and runtime compatibility. An event is a notification, not authorization. A late result from an older prompt must not replace a newer dashboard. Reconnection replays events or triggers a state resync if the cursor has expired.

### 9. Load the bundle and register its factory

The native host loads the approved JavaScript from its authenticated script URL and loads the associated styles. When executed, the bundle calls `NodexRuntime.register` with the expected project/release identity, runtime major, and factory.

Registration should not render, query data, or start timers. The host accepts only the expected registration, then creates an instance. Failed or stale loads are cleaned up. There is no iframe and no fresh native ES-module import for every revision.

### 10. Mount an instance in a staging container

The host prepares a DOM container inside the studio with measurable dimensions but hidden visibility and disabled interaction. It calls the instance’s `mount` method with the container, theme, locale, timezone, validated configuration, compatible saved state, Nodex SDK, and an abort signal.

The application creates its React root and begins rendering. Its handle exposes readiness, context updates, state capture/restoration, and disposal. The previous dashboard stays visible while the candidate prepares. Staging performs only read-only operations; it must not trigger business writes.

### 11. Fetch authorized data and finish initial rendering

The candidate calls the Nodex SDK for the initial revenue and supplier data. The SDK invokes the backend gateway, which verifies the session, project/release relationship, operation, parameters, and current permissions. The verified bipp adapter executes the supported analytics request; service credentials remain server-side.

Normalized results return to the application, which updates its state and renders the charts and graph. The coding agent is no longer involved. Empty results are a valid ready state; a failed required view rejects readiness rather than masquerading as an empty chart.

### 12. Activate the new UI and retire the old instance

Once required views settle, the candidate resolves its readiness promise. The host checks its desired release and load token again. If necessary, it briefly pauses old-dashboard input, captures the latest compatible selections, and asks the candidate to restore them. Incompatible state is reported rather than silently claimed as restored.

The host activates the new instance and switches the visible container. It then aborts the old request scope, unmounts the previous application, removes its listeners and timers, destroys chart/graphics resources, and releases styles. It unregisters the retired factory after its last instance or loading reference is released. **The newly built dashboard is now visible inside Nodex.**

On an ordinary loading or mounting failure, dispose the candidate and resume the previous view. On a first-build failure, keep the empty canvas with diagnostics. This recovery logic is not security isolation: harmful same-page code or an infinite loop can disrupt the host itself.

### After display: interaction is different from authoring

A supplier double-click executes the generated handler: SDK request → authorized facilities data → graph state update → rerender. No agent call, source edit, or build is needed. A new chat request that changes application code starts another authoring run against the latest source revision.

**An approved preview is not a publication.** Publishing is a separate authorized operation that pins the accepted release and configuration version for viewers; further draft edits do not change that published pair. See [HTTP contracts](#http), [native runtime interfaces](#runtime), and [revision switching](#delivery) for the detailed boundaries.

For the service transactions, browser loading, factory registry, and activation handover behind steps 7–12, read [Release to live UI: execution details](#release-execution).

## Agentic authoring loop

<!--AUTHORING-->

**Input envelope:** project ID, base revision, prompt, optional selected component, permitted model metadata, runtime SDK contract, approved dependency catalogue, and relevant diagnostics. Resolve identity from the authenticated session. Retrieve only authorized metadata and redact sampled data before sending it to a model provider.

| Tool | Input / output | Enforcement |
| --- | --- | --- |
| project.read / search | Relative paths or query → source snippets | Project allowlist; path traversal and symlink checks |
| models.describe | Model selector → permitted fields and definitions | Server-side model permissions; returned descriptions are untrusted data |
| project.patch | Base tree hash + patch → candidate tree hash | Workspace-only edits; protected build policy files cannot be changed |
| validate.build | Candidate tree → build ID and diagnostics | Fixed toolchain, vetted dependencies, isolated worker |
| validate.browser | Build ID + scenario → rendering / interaction evidence | Separate disposable browser; fixture or scoped read-only data |
| candidate.submit | Tree hash + evidence IDs → pending release | Trusted service verifies evidence matches the exact build |

The orchestrator, not the model, decides when tool execution is allowed. Treat instructions embedded in data, comments, or dependency documentation as untrusted input. Allow read tools during planning; enable edits only inside the run workspace. The agent can propose a dependency but cannot bypass its approval policy.

**State machine:** queued → planning → editing → building → testing → awaiting_approval → ready. A test failure may return to editing with an incremented attempt count. Failed, cancelled, and superseded are terminal. Ready means an approved preview candidate exists; it does not mean published. An illustrative pilot budget is three repair attempts and ten minutes per run; tune from evidence rather than promising this as a service level.

Persist run transitions and tool results. Queue delivery is at least once: workers claim leases, heartbeat, and use idempotent stage outputs keyed by run, attempt, and source hash. After a crash, inspect completed outputs before restarting work. Cancellation revokes leases and kills sandbox processes where supported; late completions cannot promote cancelled work.

Before accepting candidate source, compare its base revision with the project’s current draft using a transaction. A conflict supersedes the run; the user can retry against the new draft. Do not silently rebase generated code. Code-generation approval and permission changes are separate operations.

## Source, revisions and release records

<!--RECORDS-->

| Record | Identity and important fields | Lifetime |
| --- | --- | --- |
| Project | projectId, tenantId, draftRevisionId, publishedReleaseId, version | Durable; tenant-scoped |
| SourceRevision | revisionId, parentRevisionId, treeHash, lockfileHash, runId | Immutable |
| AuthoringRun | runId, baseRevisionId, status, attempt, candidateRevisionId | Durable audit record |
| Build | buildId, revisionId, toolchain digest, log reference, status | Immutable successful output; bounded diagnostics retention |
| Release | releaseId, buildId, manifest, approval/revocation status | Artifact bytes immutable; approval status mutable |
| Configuration | projectId, releaseId, configVersion, validated values | Versioned; changes require optimistic concurrency |
| Viewer state | userId, projectId, stateSchemaVersion, selections | User-scoped; never source or credentials |

Publishing atomically advances the project’s published release and configuration-version pointers after approval and version checks. Draft code and configuration edits do not move them. Rollback is another audited pointer change to an approved compatible release/configuration pair; it does not rewrite history or undo changes in external data. Source, dependencies, model version, and query parameters must be recorded separately: pinning code does not freeze live business data.

Delete artifacts only after reference checks covering published releases, active previews, audit retention, and rollback policy. Revocation prevents future delivery and queries for that release; it cannot erase JavaScript already downloaded into a browser. An online host can react to a revocation event by unmounting and rechecking state.

## Build and artifact contract

Checkout a candidate tree → install from approved lockfile → type-check → build → browser-test → persist candidate artifacts → review → approve. Execute package scripts only under the build sandbox policy. Pin the toolchain image, dependency lockfile, SDK major, and compiler settings. Reuse dependency caches without reusing another tenant’s private source or credentials.

<h3 id="pinned-toolchain">What “pinned toolchain” means</h3>

A **toolchain** is the collection of software that turns the agent’s source code into the dashboard bundle: the JavaScript runtime, package manager, compiler, bundler, plugins, and build configuration. **Pinned** means each build uses an explicitly recorded, approved set of versions and settings—not whatever happens to be newest on the worker that day.

For Nodex, the goal is to distinguish “the agent changed the dashboard” from “the build tools changed underneath it.” If two workers build the same revision, they should use the same build recipe. Pinning supports reproducibility, debugging, and controlled upgrades; it does not alone guarantee byte-for-byte identical output or safe code.

| What we fix | What Nodex records | Why it matters |
| --- | --- | --- |
| Worker environment | Container image digest and target OS / CPU architecture | Workers start from the same environment, not a mutable image tag |
| Runtime and installer | Exact Node.js and package-manager versions | Installation and build behavior do not drift between workers |
| Compilation tools | Exact TypeScript, bundler, plugin, and minifier versions | The same source is transformed with the same compiler behavior |
| Application dependencies | Committed lockfile, resolved package versions, and integrity data | React, chart libraries, and their transitive dependencies do not silently change |
| Nodex integration | Exact SDK package version plus supported runtime API major | The bundle is built against the intended host contract; the major alone does not pin package bytes |
| Build recipe | Configuration hash, browser target, IIFE output settings, and allowed environment inputs | An unchanged compiler cannot silently produce a different delivery format |
| Validation environment | Test-runner and browser-build versions, fixture versions | Test results can be investigated against a known test environment |

**How the build worker uses it.** The platform selects an approved toolchain profile, starts its recorded image, checks out the source revision, and installs from the committed lockfile. It fails if the dependency manifest and lockfile disagree instead of updating the lockfile during the build. For an npm-based implementation, `npm ci` provides that frozen-install behavior; installation flags must also match the recorded recipe. [npm clean-install documentation](https://docs.npmjs.com/cli/v11/commands/npm-ci/).

The build record retains the profile ID, image digest, source and lockfile hashes, configuration hash, and resulting artifact hashes. Build-cache keys include the relevant environment and dependency inputs, with tenant isolation. Toolchain profiles and build policy are platform-controlled; the coding agent can propose a dependency change but cannot silently upgrade the compiler or bypass approval.

**Example:** a dashboard revision is built with profile A. A newer compiler becomes available tomorrow. Rebuilding that revision still selects profile A unless a deliberate upgrade is requested. Testing profile B creates a new build and candidate release; it does not replace the bytes of the already published release. Viewers receive the compiled bundle, not the toolchain.

**Pinned does not mean permanently frozen.** The platform team updates profiles for security fixes and compatibility, tests representative dashboards and the register / mount / dispose lifecycle, then approves migration. Each update records a new profile and image digest. Image tags can move; digest references identify fixed image content, but updates must still be managed explicitly. [Docker image-pinning guidance](https://docs.docker.com/build/building/best-practices/#pin-base-image-versions).

Pinning controls build inputs, not live business data or every nondeterministic input. Timestamps, randomness, external downloads, and environment-dependent paths must also be controlled to claim bit-for-bit reproduction. It does not make a vulnerable dependency secure or isolate generated JavaScript inside the studio page.

### Resulting release manifest

```json
{
  "schemaVersion": 1,
  "releaseId": "rel_42",
  "projectId": "prj_retail",
  "sourceRevisionId": "rev_42",
  "runtimeApiMajor": 1,
  "format": "iife-register",
  "entry": "assets/dashboard.42ab.js",
  "styles": ["assets/dashboard.18cd.css"],
  "assets": [
    {"path": "assets/dashboard.42ab.js", "sha256": "<64-hex-digest>", "bytes": 180240},
    {"path": "assets/dashboard.18cd.css", "sha256": "<64-hex-digest>", "bytes": 6230}
  ],
  "stateSchemaVersion": 1,
  "requiredOperations": ["retail.sales.summary", "retail.supplier.facilities"]
}
```

The example digest is a placeholder. Manifest entries must be relative, normalized paths within the release directory; reject traversal, absolute URLs, and unexpected MIME types. Build one classic IIFE script per release with revision-specific dependencies inside its function scope. Reject residual revision-specific native imports, including those left in dependencies. Shared runtime dependencies, if introduced, stay pinned and loaded once. The asset list covers the bundle and static assets. Toolchain-generated metadata is transformed into this Nodex release manifest, not passed through as a browser runtime contract. Vite documents a general asset-manifest integration pattern, but its default output does not by itself implement this registration format. [Vite manifest reference](https://vite.dev/guide/backend-integration).

Serve assets through `/api/v1/projects/{projectId}/releases/{releaseId}/assets/{path}` on the studio origin. Validate session, project access, and release status for every request. The host loads the entry through a classic script element, never `type="module"`, and waits for expected registration as well as load success. Use correct JavaScript MIME types and the same-origin session rather than bearer tokens in script URLs. Reserve the release identity before packaging so the registration matches its manifest.

Keep artifact bytes immutable in storage, but use private browser caching with revalidation at the delivery route; do not put tenant-private responses in an unauthenticated public CDN cache. Authenticated conditional requests may return 304. Digest checks protect server-side artifact provenance; the host can derive script integrity metadata from the approved digest. A digest merely listed in JSON does not enforce browser integrity by itself. A signed release is also not proof that its code is safe.

## Native runtime interface

<!--RUNTIME_CONTRACT-->

The bundle calls the persistent host’s `NodexRuntime.register` with project/release identity, runtime major, and a factory. The host accepts only expected, compatible registrations; duplicates and late registrations without an active load are rejected. This is lifecycle bookkeeping, not protection from hostile same-page code. The factory creates an instance implementing `mount`. No React component objects cross the host boundary. `mount` returns a handle synchronously so the host can dispose it while readiness is pending. If mounting throws before returning, the instance must unwind partially allocated resources. These are proposed Nodex contracts, not existing bipp APIs.

| Lifecycle | Required behavior |
| --- | --- |
| Register / create | Registration is the sole top-level effect; factory creation starts no timers, requests, or rendering |
| Mount | Use only the assigned container; return a handle; obey the instance AbortSignal |
| Ready | Resolve after required initial views settle; empty data is valid; reject on a required-view failure |
| Update context | Apply theme, locale, timezone, validated configuration, or activation phase; asynchronous and idempotent for identical values |
| Serialize state | Return bounded JSON with schema version, not DOM nodes, functions, query rows, or credentials |
| Restore state | Validate the state schema, reconcile the staged view, and report whether restoration succeeded |
| Dispose | Idempotently abort requests, unmount React, remove listeners/timers/portals and release-owned styles |
| Unregister | Remove the factory after its last instance/loading reference is released; release script nodes, callbacks and registry references |

Use a per-instance scope class for CSS, namespaced animation names, and an instance-local overlay container for menus and tooltips. Generated CSS must not target document-wide roots. Use a unique React ID prefix. These are collision-prevention conventions, not security enforcement. React can mount separate roots into existing DOM containers and unmount them later. [React root lifecycle](https://react.dev/reference/react-dom/client/createRoot).

The contract checker rejects unsupported runtime majors before mounting; loading a script itself executes code, so provenance and approval are checked first. Reference-count factories and styles when multiple dashboard instances use a release. Keep only active releases and in-flight replacements, not the full revision history, in the registry. A major interface change requires a rebuild or a supported adapter. State schema versions are separate from runtime API versions. If an instance cannot restore an old state, start clean and inform the user; do not silently claim successful restoration.

## Fresh-code delivery and revision switching

<!--SWITCHER-->

<p class="caption">Interactive sequence model only. It illustrates host decisions using local data; it does not execute generated code or contact bipp.</p>

| Step | Owner → receiver | Contract |
| --- | --- | --- |
| 1 | Release service → event stream | Approved release ID with run ID and monotonic event sequence |
| 2 | Studio → release API | Re-fetch authoritative status and manifest; event payload is not authority |
| 3 | Host → asset route | Check paths/runtime version; load styles and the classic bundle; verify expected registration |
| 4 | Host → candidate instance | Mount in a staging container with measurable dimensions, `inert`, and hidden visibility |
| 5 | Candidate → host | Ready or failed within a host deadline; display state errors separately |
| 6 | Host → old / new instance | Briefly pause input, obtain latest compatible state if needed, reconcile, switch visibility |
| 7 | Host → previous instance | Abort its request scope and dispose; unregister retired factory when unused and release styles |

Keep a monotonically increasing local load token and the latest desired run/release ID. Check both after every asynchronous operation, including script registration, readiness, and activation. Superseded candidates must be disposed and must never become visible. Removing a script node is not a guarantee that pending execution is cancelled. Reject late registrations after the corresponding load is retired; release any stale factory and owned resources.

State can change while the candidate loads. For the first implementation, briefly pause old-dashboard interactions during the final state capture and candidate restoration, then activate or resume the old dashboard on failure. A staged module runs read-only operations; ordinary user interaction begins only in the active phase. Lifecycle compliance is a trusted-code obligation, not containment.

An illustrative readiness timeout is 15 seconds; configure it and report timeout distinctly from empty data. Keep the previous dashboard on ordinary loading failures. Same-thread infinite loops can prevent even timeout handlers from firing. Error boundaries cannot guarantee studio recovery from arbitrary same-page code.

**Normal release updates do not refresh the Studio.** Keep the shell, chat, editor, and session running while the dashboard host stages and swaps native instances. Serialize replacements per dashboard slot: normally retain one active instance and briefly one candidate (or one retiring instance after activation). Finish retirement before admitting another candidate; coalesce queued updates to the latest desired release. A cleanup failure pauses that slot's replacement loop instead of accumulating more instances.

Each release has a distinct script URL. This avoids a native ES-module-cache entry per revision, but removing the script node alone does not unload executed code. Dispose instances, destroy chart/graphics resources, unregister unused factories, and release references so objects become eligible for collection. Keep history on the backend and reload approved, still-authorized bundles for rollback. Test repeated replacement and rollback for retained objects and listeners. Native module caching is why per-revision `import()` is not this design’s delivery mechanism. [Dynamic import and cache behavior](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/import).

Refresh-free swapping is the normal workflow, not an unconditional guarantee for arbitrary same-page code. Use [host-managed cleanup and dashboard-only recovery](#resource-scopes) first; a full-page refresh is an exceptional fallback when shared-page health cannot be restored.

## Release to live UI: execution details

Approval, delivery, registration, mounting, querying, activation, and retirement are distinct operations. This section specifies their proposed implementation behind workflow steps 7–12. The APIs and runtime remain a design, not an implemented platform. Code snippets illustrate boundaries; omitted helpers belong to the future host or generated bundle.

<h3 id="exact-release-approval">1. Approve exact release bytes, not a moving branch</h3>

“Exact release” binds the approval to a specific compiled artifact and its provenance. It is not approval of a prompt or whichever build happens to be latest.

```text
Project                 prj_retail
Source revision         rev_42
Build                   build_108
Release                 rel_42
Toolchain profile       toolchain_A
Manifest digest         sha256:<manifest digest>
JavaScript / CSS digests sha256:<artifact digests>
Test evidence           checks_for_build_108
```

The reviewer sees the requested change, source diff, exact release identity, dependency and operation changes, test results, and warnings. Preapproval execution occurs in the isolated test environment, not inside the production studio. Source, build output, and manifest bytes are immutable; the release’s approval status is mutable.

The review request uses the existing contract:

```http
POST /api/v1/projects/prj_retail/releases/rel_42/review
If-Match: "release-5"
Idempotency-Key: approval-unique-id
X-CSRF-Token: <session-csrf-token>
Content-Type: application/json

{"decision":"approve","reason":"Verified chart behavior and authorized queries"}
```

The backend authenticates the reviewer, checks the reviewer role, and conditionally updates the release using its ETag. It verifies that the release is awaiting approval, that successful evidence matches the exact build, and that stored artifacts match their digests. It records reviewer identity, timestamp, reason, and manifest digest before changing the status to approved. **Any changed artifact requires a new release and approval.** Do not rebuild after review and assume the new bytes are equivalent.

Use a transactional outbox: commit the approval and a pending event record in the same database transaction. A dispatcher emits the event with retries and a stable event ID. Delivery is at least once, so clients still deduplicate. This closes the gap where approval succeeds but its notification is lost.

“No self-approval” means the coding agent has no authority or credentials to approve its output. Requiring the human reviewer to differ from the requesting author is a separate governance policy. Approval is not proof that same-page code is safe.

<h3 id="release-delivery">2. Deliver approved assets to the browser</h3>

The studio receives `release.approved` with project, run, release, and event sequence. The event contains neither application code nor an authorization grant. The host checks whether this is still its desired edit, deduplicates the event, and fetches the release’s current status and manifest from `GET /api/v1/projects/prj_retail/releases/rel_42`.

The server checks access; the host validates the project/release identity, runtime major, IIFE registration format, normalized asset paths, and configuration compatibility. It constructs an authenticated same-origin URL and installs load/error handlers before inserting a classic script element:

```js
// Illustrative loader setup; the host implements validation and handlers.
const script = document.createElement("script");
script.src = approvedAssetUrl;
script.integrity = approvedSriDigest;
script.crossOrigin = "anonymous";
// Deliberately not type="module". Attach handlers before inserting it.
```

The integrity value is the hash algorithm plus a base64 digest derived from the approved artifact hash, not the manifest’s raw hexadecimal string. The browser can reject bytes that do not match. This verifies delivery integrity, not behavioral safety. See [Subresource Integrity](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Subresource_Integrity).

Load and track the release’s CSS separately, including failures and ownership references. Scoped selectors prevent accidental restyling of the active view while a candidate stages. Script load success alone is insufficient: the expected factory must also register, within a bounded deadline.

<h3 id="factory-registration">3. Register a factory without rendering</h3>

The compiled bundle contains its components and revision-specific dependencies in an IIFE scope. It registers a factory with the persistent host:

```js
(function () {
  // Compiled implementation, including createDashboardModule, lives here.
  window.NodexRuntime.register({
    projectId: "prj_retail",
    releaseId: "rel_42",
    runtimeApiMajor: 1,
    create() {
      return createDashboardModule();
    }
  });
})();
```

Registration means “this factory can create release 42 instances.” It must not render, query data, or start timers. The host checks the expected pending load, supported runtime major, required method shapes, and duplicate/retired-registration rules. It then retains the factory and calls `create()` when an instance is needed.

The host registry tracks the factory, active-instance references, pending-load references, and script/style ownership by project and release. Multiple dashboard instances may share one loaded factory; their application state remains separate.

Correlate registration with the actual loading script element and load generation, not only the release ID. A cancelled load and a later reload of the same release must not be confused. Synchronous classic-script registration can inspect `document.currentScript`; the host maps that element to its pending load. Reject registration outside that expected synchronous window. This is lifecycle bookkeeping, not protection against malicious same-page code. See [currentScript](https://developer.mozilla.org/en-US/docs/Web/API/Document/currentScript).

<h3 id="candidate-mounting">4. Mount a candidate instance in the native DOM</h3>

The host creates an instance ID, request AbortController, instance-scoped SDK, and a staging container. The container is invisible and noninteractive but has real dimensions. Prefer a positioned container with hidden visibility and `inert` over `display: none`, since charts need layout measurements.

```js
// Values are prepared and validated by the host.
const instance = registration.create();
const handle = instance.mount(container, {
  instanceId,
  projectId,
  releaseId,
  mode: "preview",
  phase: "staging",
  theme,
  locale,
  timezone,
  scopeClass,
  initialState,
  configuration,
  sdk,
  signal: controller.signal
});
```

The instance creates its React root and renders into the assigned container. `mount` returns its handle synchronously so cleanup is possible while data loads. The handle exposes readiness, context updates, state serialization/restoration, and disposal. If mounting throws before returning a handle, the implementation must unwind partially allocated resources.

Calling `root.render()` is not the readiness signal. The application resolves `handle.ready` only after required initial data and views settle; React rendering does not itself establish application readiness. See [React root lifecycle](https://react.dev/reference/react-dom/client/createRoot). The previous dashboard stays visible throughout preparation.

<h3 id="initial-querying">5. Query authorized data and finish rendering</h3>

The mounted application uses the supplied SDK, not the coding agent, to request initial data:

```js
const result = await context.sdk.query({
  operationId: "retail.supplier.facilities",
  parameters: { supplierId: "supplier_17" },
  pageSize: 100
}, { signal: requestController.signal });
```

The SDK scopes the request to the instance’s project and release and calls `POST /api/v1/projects/prj_retail/releases/rel_42/queries`. It combines instance disposal with per-request cancellation. The gateway independently checks session identity, current project/release access, release status, named operation, parameter schema, query limits, and data permissions before invoking the bipp adapter. The release’s declared operations never grant permission.

The server-only adapter translates the request to verified bipp interfaces and returns normalized rows and metadata. Exact bipp endpoint names remain unverified; frontend code cannot invent them. Service credentials stay on the backend.

The application rejects stale responses using a request/selection generation and checks disposal before updating state. Required views render the results and complete readiness. Empty data may resolve with `status: "empty"`; a failed required query rejects readiness. Browser abort stops applicable fetch work, while upstream cancellation remains best effort and adapter-dependent. See [AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController/abort).

<h3 id="activation-commit">6. Activate at an explicit host commit point</h3>

Keep a monotonically increasing generation for the desired load: release 42 might use generation 7; a later request for release 43 advances it to 8. Each asynchronous continuation checks that its generation is still current. An obsolete candidate is cleaned up, never activated—even when the release ID happens to match a later reload.

For the final handover, the host:

1. Waits for candidate readiness, with a configured deadline.
2. Briefly pauses interaction with the old dashboard.
3. Captures its latest serializable state and restores compatible state into the candidate.
4. Waits for restoration and checks the desired generation again.
5. Updates the candidate context to the active phase, then rechecks after that asynchronous call.
6. Commits the active-instance pointer, container visibility, interaction ownership, and appropriate focus in a short synchronous operation.
7. Starts retirement of the old instance.

Preparation happens before the visibility change. The first implementation must not perform irreversible business writes during staging or activation. On a precommit failure, dispose the candidate and resume the old view; on a first-build failure, keep the empty canvas with diagnostics. Activation changes this editor’s visible preview, not the published release pointer.

Same-thread infinite loops can prevent deadlines from firing. Neither lifecycle promises nor error boundaries provide isolation from hostile native code.

<h3 id="instance-retirement">7. Retire instances, then release unused factories</h3>

After a successful switch, the host aborts the old instance’s request scope and calls `await oldHandle.dispose()`. Disposal is idempotent and must unmount React, cancel requests, clear timers and animation loops, unsubscribe listeners and observers, remove overlays/portals, destroy chart instances, release graphics resources, and drop callback/store references.

Only then release the host’s ownership references. If another active instance or pending load uses that factory or stylesheet, retain it. Otherwise unregister the factory, remove owned script/style elements as appropriate, clear loader callbacks, and delete registry references. Removing a script element alone does not undo its executed code. Objects become eligible for collection only after their references and side effects are released; collection timing is not guaranteed.

A cleanup error after activation is recorded as degraded host health; it does not automatically roll back the newly visible dashboard. Pause further replacements for the affected slot and attempt bounded cleanup and dashboard-only recovery as described below. Retain release history on the backend, not as every past factory in browser memory.

<h3 id="resource-scopes">Host-managed resource scopes: keep swapping without a page refresh</h3>

Create a resource scope before mounting each instance. The host's SDK wrappers and vetted component adapters register cleanup actions with this scope. Generated code must use these wrappers for supported resources and register explicit disposers for custom integrations. React unmounting removes the React tree, but external subscriptions and other non-React resources still need cleanup. [React root lifecycle](https://react.dev/reference/react-dom/client/createRoot).

| Resource owned by an instance | Scope retirement action |
| --- | --- |
| Queries and subscriptions | Abort applicable requests, unsubscribe, and reject late responses by instance/generation |
| Timers and animation loops | Cancel scheduled work and prevent new scheduling after scope closure |
| DOM listeners and observers | Remove registered listeners and disconnect observers |
| Chart and graphics instances | Call adapter-specific destruction and graphics-resource disposal methods |
| Workers | Terminate instance-owned workers; release message handlers and host references |
| Portals and overlays | Remove instance-owned elements outside the main dashboard container |
| Factories and styles | Release host ownership references; retain shared assets only while another instance/load needs them |

Mark the scope closed before cleanup so it rejects new acquisitions and ignores callbacks from retired generations. Abort outstanding work, invoke idempotent application disposal, and run remaining tracked disposers even if one fails. Coordinate dependency order so framework teardown can still access the resources it needs. Record each failure; a timeout bounds the host's wait but cannot interrupt a synchronous main-thread hang or prove disposal completed. Shared assets belong to separately reference-counted host ownership, not an individual instance's unconditional destructor.

This is a proposed extension to the host and SDK implementation; resource-wrapper APIs are not yet defined in the downloadable TypeScript contracts. It is lifecycle management, **not a sandbox**. Do not globally monkey-patch browser APIs and claim complete tracking. Direct global listeners, third-party caches, and allocations outside the scope can escape it; generated code and dependency adapters must cooperate.

<h3 id="dashboard-recovery">Dashboard-only recovery before a full-page refresh</h3>

1. Pause the affected slot's replacement queue and invalidate pending load generations. Cancel and dispose any candidate.
2. Capture bounded, compatible dashboard state if the instance can still serialize safely. If not, recover with clean state and tell the user.
3. Close the affected scopes, dispose their instances, and release unused factory/style references. Run all available cleanup even when some actions fail.
4. Recreate only the dashboard container and React root. Re-fetch a known-good release after checking current approval, revocation, and access; never bypass authorization to recover.
5. Restore compatible state, wait for readiness, and activate the recovered dashboard. Keep the Studio shell, chat, navigation, and session in place.
6. Resume swapping only when tracked cleanup and readiness checks pass. Bound automatic recovery attempts; if they fail, keep replacements paused and show diagnostics and a controlled full-page refresh option. Recovery does not change the published release pointer.

For computation delegated to a worker, terminating and recreating that worker resets its execution context without reloading the Studio. Workers cannot directly manipulate the ordinary DOM; restarting one does not remove main-thread chart objects or DOM leaks. Worker termination also does not undo server-side work. [Worker lifecycle and limitations](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers).

**Swapping is not itself leak recovery.** A surviving global listener can keep an old instance reachable after its container is removed; another swap can add more retained objects. Unreachable objects are eligible for garbage collection, but collection timing is not guaranteed. A dashboard-only restart cannot reliably undo untracked global references, shared-state corruption, or an infinite loop on the host thread. Health checks are evidence of recovery, not proof of a leak-free heap. [JavaScript memory management](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Memory_management).

Capture project/release/instance IDs, load generation, lifecycle timestamps, cleanup duration/outcomes, scope resource counts, factory/style reference counts, and recovery attempts. Send bounded diagnostic metadata to the backend; do not retain retired instance objects or closures in browser logs/history, or log raw query data. Compare tracked resources against baseline and use repeated-swap browser profiling to find untracked retention.

**Product promise:** dashboard releases swap natively without reloading the Studio during normal operation. Dashboard-scoped recovery comes first. A full-page refresh remains an exceptional fallback for shared-page failures, not a routine release step.

### Ownership and completion boundaries

| Operation | Owner | Completion means |
| --- | --- | --- |
| Approve | Release service + authorized reviewer | Exact artifact identity and evidence accepted; audit/outbox committed |
| Deliver | Host loader + authenticated artifact service | Approved assets retrieved and integrity checks satisfied |
| Register | Bundle + host registry | Expected factory is available; no application mounted yet |
| Mount | Factory instance + native host | Candidate exists with a disposable lifecycle handle |
| Query / ready | SDK, gateway, adapter, application | Required authorized data/views have settled |
| Activate | Native host | Candidate becomes the current visible instance |
| Retire | Old instance + host registry | Owned resources released; unused factory references removed |
| Publish | Authorized publisher + project service | Release/configuration pair pinned for viewers |

Approval audit records and the outbox are server implementation records. Load-generation tracking, script correlation, reference counting, and commit/cleanup behavior are host implementation responsibilities. The existing TypeScript contracts describe the public lifecycle; these implementation details still require code and tests. In particular, test cancellation followed by reloading the same release, not only two different releases finishing out of order.

## HTTP API contracts

All routes below are proposed **Nodex** APIs under `/api/v1`. The local documentation server serves files only; it does not implement these endpoints. Use JSON requests/responses except SSE and asset bytes. Identity and tenant come from the authenticated session, never from a client-supplied tenant ID.

**Common rules:** HTTPS in production; HttpOnly session cookies with an appropriate SameSite policy; origin and CSRF checks on mutations. Roles: viewer reads published apps and permitted data; editor authors and previews; reviewer approves; publisher changes published pointers. Artifact access requires both project access and release eligibility. Unauthorized resources return 404 where existence must remain private.

Mutations carry `Idempotency-Key` and `X-CSRF-Token`; concurrency-sensitive mutations also carry `If-Match` with the resource ETag. A key is scoped to user, project, and operation and retained for an initial 24-hour retry window. Same key/body replays the response; same key/different body returns 409. After expiry, reconcile operation state before retrying. Missing preconditions return 428; a stale ETag returns 412. This is a proposed server policy.

<!--API_TABLE-->

### Author a change

```http
POST /api/v1/projects/prj_retail/runs
Content-Type: application/json
If-Match: "project-17"
Idempotency-Key: edit-retail-001
X-CSRF-Token: <session-csrf-token>

{"prompt":"Expand supplier facilities on double-click","baseRevisionId":"rev_41"}
```

```json
{"id":"run_42","projectId":"prj_retail","baseRevisionId":"rev_41","status":"queued","attempt":0,"candidateRevisionId":null,"releaseId":null,"failure":null}
```

Return 202 and `Location: /api/v1/projects/prj_retail/runs/run_42`. Validate base revision against the draft inside the same transaction that records the run. A retry returns the same run. This accepts work; it does not imply a new release is available.

### Approve and publish

Approval request: `{"decision":"approve","reason":"Reviewed interaction and query evidence"}`. Require reviewer role, the release ETag, and matching immutable build evidence. A reject decision records the reason and prevents activation. Return the updated Release record and ETag. Only approved releases can produce preview candidates.

Publication request: `{"releaseId":"rel_42","configVersion":3}`. Require publisher role, the project ETag, approved release status, a validated configuration version for that release, project ownership match, and supported runtime. Return the Project with its incremented version and new ETag. Publishing never reruns the agent or rebuilds mutable source. Rollback uses the same operation with an earlier approved release/configuration pair.

### Configuration changes

`PUT /projects/{projectId}/configuration` accepts `{"releaseId":"rel_42","values":{"title":"Chicago performance"}}` and a configuration ETag. The server validates against a configuration schema registered with that release and returns `{releaseId, configVersion, values}`. Each write creates an immutable draft configuration version; it does not alter the published pointer. It does not accept source patches or arbitrary property paths. Config is tied to a release; promotion requires explicit compatibility validation. Initial GET returns version 0 with validated defaults and an ETag, so creation also has a precondition. Editors read the latest draft or a requested version; viewers can read only the published pair. The runtime passes that version through context updates without rebuilding.

### Error envelope

```json
{"error":{"code":"REVISION_CONFLICT","message":"The draft changed. Reload before retrying.","retryable":false,"requestId":"req_9","details":{"currentRevisionId":"rev_43"}}}
```

| HTTP | Example code | Client action |
| --- | --- | --- |
| 400 / 422 | INVALID_REQUEST / INVALID_PARAMETERS | Show field diagnostics; do not blindly retry |
| 401 / 403 / 404 | UNAUTHENTICATED / FORBIDDEN / NOT_FOUND | Reauthenticate or stop; do not reveal hidden resources |
| 409 / 412 / 428 | INVALID_TRANSITION / PRECONDITION_FAILED / PRECONDITION_REQUIRED | Reconcile state and preconditions |
| 429 | RATE_LIMITED | Respect Retry-After; bounded backoff |
| 502 / 504 | ANALYTICS_UNAVAILABLE / QUERY_TIMEOUT | Preserve current view; offer bounded retry |

Redact secrets, raw database errors, and source contents from public errors. A 500 response includes a request ID for support, not a stack trace. Idempotent transport retries and business-level conflict resolution are different operations.

## Events and reconnection

```text
id: evt_1042
event: release.approved
data: {"eventId":"evt_1042","type":"release.approved","projectId":"prj_retail","runId":"run_42","releaseId":"rel_42","sequence":1042,"occurredAt":"2026-09-29T10:00:00Z"}

```

The stream endpoint uses `text/event-stream`, disables intermediary buffering, and sends heartbeat comments. EventSource uses the same-origin session. Editors receive their authorized run/release updates; viewers receive only eligible publication/revocation events, never draft diagnostics. The server replays authorized events after `Last-Event-ID`; the initial retention target is 24 hours. Events may be duplicated: deduplicate IDs and ignore older sequence numbers. A reconnect never grants new access; recheck authorization during stream lifetime and terminate expired sessions.

If the cursor is no longer retained, emit `resync.required`; the client reloads authoritative project/run/release state before continuing. A release event only prompts reconciliation. It must not activate a stale run, a revoked release, or another editor’s unwanted preview. Publication notifications are separate from the current editor’s desired preview. SSE IDs and reconnect behavior are documented by [MDN](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events).

## Data gateway and bipp adapter

<!--DATA_FLOW-->

```json
{"operationId":"retail.supplier.facilities","parameters":{"supplierId":"supplier_17"},"pageSize":100}
```

The runtime query URL includes project and release IDs, but the server independently checks their relationship and the viewer’s current permissions. The release’s operation list describes what the code expects; it never grants access. Resolve the operation against a server-owned registry with a parameter schema, model binding, required permission, and limits. Do not accept arbitrary SQL or arbitrary outbound URLs from dashboard code.

```json
{"requestId":"req_10","columns":[{"name":"facilityId","type":"string"},{"name":"name","type":"string"}],"rows":[{"facilityId":"fac_8","name":"Chicago distribution"}],"nextCursor":null,"truncated":false,"modelVersion":"retail-model-7","asOf":"2026-09-29T10:00:02Z"}
```

Decimal values that need exact precision are encoded as strings; timestamps use RFC 3339 and dates use YYYY-MM-DD. Null is JSON null. Unknown operation IDs or extra/invalid parameters fail validation. Cursors are opaque, signed, and bound to identity, operation, and parameters. Proposed pilot limits: default 100 rows, maximum 1,000 rows per page, and a 30-second query deadline. Graph expansion uses pagination and maximum depth rather than fetching an unbounded network.

Partition query caches by tenant, permission version, model version, operation, and normalized parameters. Check authorization before serving cached data. Browser cancellation aborts the gateway request and attempts upstream cancellation; upstream support must be verified. Discard stale graph responses when the user changes selection. HTTP cancellation alone is not proof that the database stopped executing.

<!--ADAPTER_CONTRACT-->

The bipp adapter translates Nodex operations to supported bipp APIs while preserving identity and row-level rules. Do not invent bipp endpoint names or assume a service account automatically reproduces user permissions. Required discovery: metadata access, query execution, identity delegation, model-version semantics, cancellation, and limits. Until verified, tests use a clearly labelled adapter fixture; a fixture is not a production substitute.

## Security, failures and observability

| Failure / threat | Response | Residual limitation |
| --- | --- | --- |
| Prompt injection in metadata or code | Treat retrieved text as data; scoped tools; protected policy files | Model compliance alone is not a security boundary |
| Malicious dependency or generated source | Restricted build workers, pinned packages, review and browser tests | Approved code may still contain harmful behavior |
| Native module reaches outside its container | Contract checks, review, scoped styles | Same-page JS is not confined to the container |
| Build completes after cancellation | Check run state and lease before commit | Work may have consumed resources already |
| Stale or duplicate release event | Re-fetch state; verify desired token after each await | Requires correctness in host implementation |
| Mount failure | Dispose candidate; keep old view; surface diagnostics | A hung shared thread can defeat recovery |
| Retirement or cleanup failure | Pause the affected replacement queue; run scoped cleanup and bounded dashboard-only recovery | Untracked leaks or shared-page corruption may still require a full-page refresh |
| Access revoked during session | Recheck gateway calls and assets; notify host | Downloaded code/data cannot be clawed back |
| Model schema changed | Version-aware adapter validation; explicit error | A pinned application does not freeze external models |

A native module may issue requests using the user’s broader studio session rather than the SDK. Server authorization protects tenant and user boundaries, but it does not create a per-module privilege boundary within that page. Do not place privileged admin controls or credentials in the same execution environment and claim generated modules cannot reach them. Review whether this trust model is acceptable before enabling user-generated code in production.

Trace project ID, run ID, revision ID, build ID, release ID, runtime instance ID, and request ID across stages. Log state transitions and approval/publication decisions. Avoid logging raw query results or complete prompts by default. Measure authoring success, repair attempts, build latency, ready latency, mount failures, stale-result rejection, query duration, and cleanup leaks. Set retention and AI-provider data policies explicitly.

## Implementation sequence and acceptance tests

| Stage | Deliverable | Exit evidence |
| --- | --- | --- |
| 1 · Prove the boundary | bipp adapter discovery and same-page trust review | Authorized model/query access demonstrated; trust model accepted |
| 2 · Native host | Hand-authored module, SDK fixture, lifecycle and release loader | Mount, empty data, theme update, state restore and disposal pass |
| 3 · Durable pipeline | Project store, worker queue, builds, private artifacts and approval | Retry, cancellation, stale-base conflict and provenance verified |
| 4 · Agentic editing | Scoped tools and bounded repair | Retail dashboard created and revised without losing unrelated source |
| 5 · Connected behavior | Real read-only adapter and custom graph | Double-click fetch, pagination, permission denial and cancellation tested |
| 6 · Publication | Pinned release, recovery, monitoring and embedding integration | Draft does not alter published app; rollback and session expiry tested |

Mandatory host tests: revision 43 wins when revision 42 resolves late; a failed candidate leaves 41 visible; disposal twice is harmless; style and listener counts return to baseline; two mounted instances do not collide; state migration failure is visible; permission changes invalidate queries; a revoked release cannot be newly loaded. A headless test must exercise a real built module, not only mock lifecycle functions.

Refresh-free lifecycle acceptance: exercise repeated swaps and rollbacks without a page reload; verify the per-slot active/candidate/retiring bound, closed-scope acquisition rejection, ignored late callbacks, and remaining-disposer execution after one fails. Inject a retirement failure and prove replacements pause rather than accumulate. Demonstrate dashboard-only recovery while chat and shell state remain intact, clean-state recovery when serialization fails, authorization rechecks on rollback, and bounded failed recovery with an explicit refresh option. Profile retained objects over repeated cycles; passing tracked-resource counts alone is not proof that third-party code is leak-free.

Deferred deliberately: automatic backend code generation, write actions, full drag-and-drop reconstruction of arbitrary code, HMR infrastructure, and scheduled PDF delivery. Snapshot rendering will need a separate readiness/export contract and verification of bipp delivery compatibility. No timeline or production-readiness claim is implied by this document.

## Contract downloads and references

[Download the TypeScript contracts](technical-contracts.ts). They define the proposed browser lifecycle, SDK, records, and server adapter and are type-checked by the local verification command. HTTP endpoints are specified above; no API server is implemented by this documentation site.

Primary references: [React DOM roots](https://react.dev/reference/react-dom/client/createRoot), [Vite asset manifests](https://vite.dev/guide/backend-integration), [JavaScript dynamic import](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/import), [SSE transport](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events), and [Shadow DOM limitations](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_shadow_DOM). Proposed endpoint names, policies, lifecycle methods, and limits are Nodex design choices, not claims about these libraries or bipp.
