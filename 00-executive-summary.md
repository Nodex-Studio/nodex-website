# Nodex Studio, built on bipp

A conversational dashboard studio built on bipp’s analytics foundation, available inside a customer’s product or as an independent application.

## The product

Nodex is a proposed studio where users describe a business need, see a working dashboard take shape, and refine it through chat or direct editing. The studio itself can be embedded in a customer’s application or deployed independently.

Each dashboard is a managed web application with versioned source code. Nodex builds it in an isolated backend environment and loads a disposable dashboard bundle into a persistent studio runtime. Native here means rendering in the studio’s own page, without an iframe—not a desktop-native application.

Nodex’s studio interface, dashboard canvas, and visual components are developed independently of bipp’s UI. The proposed integration uses bipp’s data modeling, query generation, access controls, and compatible backend delivery services. Nodex presents those analytics through its own conversational experience and generated applications.

The intended business benefit is less manual configuration and fewer repeated requests to specialists. Customers could offer dashboard creation inside their own products. Faster delivery, broader adoption, and reduced support effort are outcomes to measure, not results already achieved.

## What bipp already provides

The supplied demonstrations establish a connected workflow from modeled data to reports and scheduled distribution.

<dl class="trust-list">
<div><dt>Reusable business definitions</dt><dd>Visual modeling adds tables, join types, and matching columns. Named calculations such as Profit become reusable fields in the explorer.</dd></div>
<div><dt>Visual exploration and generated SQL</dt><dd>Users select dimensions, measures, aggregations, filters, sorting, and limits. bipp generates the corresponding SQL; the demonstrations describe execution against the underlying database.</dd></div>
<div><dt>Controlled model development</dt><dd>The Git demonstration shows development and production branches, commits, conflict resolution, validation, deployment, and history. It establishes model versioning; it does not establish the same lifecycle for every dashboard.</dd></div>
<div><dt>Composed dashboards</dt><dd>The retail dashboard combines KPI cards, time trends, brand and department comparisons, geographic views, and filters. bipp’s published material also describes cross-filtering, drilldowns, a visual dashboard editor, and custom HTML or JavaScript visualizations.</dd></div>
<div><dt>Filtered, scheduled distribution</dt><dd>The delivery demonstration configures a Chicago-specific report, daily timing and timezone, recipients, PDF/JPG output, and dimensions. It shows schedule management and a received PDF snapshot.</dd></div>
</dl>

bipp also publicly describes granular access controls and cloud or customer-managed deployment. These inform the backend integration assessment. The existing bipp screens described above are evidence of its product capabilities, not UI components proposed for Nodex.

## The experience Nodex adds

<div class="conversation" aria-label="Proposed Nodex conversation using bipp’s retail model">
<div class="exchange"><span class="speaker">User</span><p>Build a Chicago sales dashboard with monthly sales and profit, top brands, and a department breakdown.</p></div>
<div class="exchange assistant"><span class="speaker">Nodex</span><p>I found Sales and Profit in the bipp retail model. I’ll use those definitions and apply Chicago across the views.</p></div>
<div class="exchange"><span class="speaker">User</span><p>Put the monthly trend first. Make selecting a brand filter the other charts.</p></div>
<div class="exchange result"><span class="speaker">Canvas</span><p>A proposed dashboard with connected views, ready to inspect, adjust, and save.</p></div>
</div>

Today’s demonstrated workflow asks users to translate a question into fields, measures, filters, and presentation choices. Nodex would handle that coordination while keeping the result visible and editable. A follow-up request should change the relevant part without discarding unrelated work.

Once authoring works, the conversation could extend to “send this every morning at 7 Chicago time,” using bipp’s delivery services. Recipients, filters, timing, and access must be resolved before creating a schedule. Conversational delivery is a follow-on opportunity; flexible dashboard creation is the first priority.

## What arbitrary dashboards means

There are two separate goals: making existing capabilities easier to use, and expanding what the dashboard can express. Adding chat alone does not expand the renderer.

<div class="capability-list">
<div><span class="item-number">01</span><div><h3>Turn approved data into useful views</h3><p>Build Nodex charts, filters, and interactions around the user’s question, backed by approved metrics and data from bipp.</p></div></div>
<div><span class="item-number">02</span><div><h3>Generate new components and behavior</h3><p>Write application code for unusual layouts, specialized graphs, custom widgets, and interactions. Reusable components accelerate creation; their catalogue does not define the limit.</p></div></div>
<div><span class="item-number">03</span><div><h3>Keep the result maintainable</h3><p>A customized dashboard must remain editable, respect permissions, and support the viewing and export workflows its users need.</p></div></div>
</div>

Nodex applications use their own source code and rendering runtime, not bipp’s dashboard editor, visual components, or bippDash definitions. Nodex-owned components and supported third-party libraries accelerate development without limiting the application to a fixed widget catalogue.

General browser code can express custom SVG, canvas, charts, layouts, and event handlers using supported dependencies. Backend operations remain subject to authorization, but native modules share the studio page’s browser privileges. New server-side algorithms, background jobs, or database writes require separately authorized backend capabilities; a frontend bundle cannot supply them alone.

“Arbitrary” is an ambition for extensibility. Unsupported requests should produce a clear explanation or a supported alternative, rather than a plausible but incorrect result.

## How Nodex uses bipp

The proposed architecture is a managed application project per dashboard, an agentic authoring loop, isolated backend builds, and disposable, versioned dashboard bundles mounted directly into Nodex’s page. The studio host and its runtime SDK stay loaded across edits; the SDK connects applications to an authorized backend gateway. All UI and dashboard rendering belong to Nodex.

<!--ARCHITECTURE-->

Start with one authoring orchestrator and one coding agent. The agent reads relevant project files, permitted model metadata, SDK documentation, and the user’s request. It clarifies business meaning, plans a targeted change, and patches an isolated workspace based on a specific source revision. Scoped tools allow inspection, edits, builds, and browser tests—not permission changes or direct publication.

An isolated build worker resolves approved pinned dependencies, compiles JavaScript and CSS, and checks rendering, interactions, and agreed data results. Diagnostics return to the agent for repair within retry, time, and cost limits. Trusted services apply release checks and approval policy; passing tests is not proof of correctness or safety. Concurrent changes require reconciliation rather than overwriting newer source. Build workers have restricted network access, resource limits, and no production credentials; generated code and dependency scripts do not execute inside Nodex’s main server.

A successful build produces an immutable classic JavaScript bundle wrapped in a function (IIFE format), CSS, assets, and a manifest tied to the source revision and runtime version. The studio receives a release-ready notification and loads the bundle through an authorized script URL, not a fresh native ES-module import for every revision. The bundle registers a dashboard factory with Nodex; the host creates an instance and mounts it into a DOM container without rebuilding the shell or evaluating raw chat output.

Use a React and TypeScript application as the initial target, with a self-contained React root per dashboard. The host and dashboard exchange data through an explicit SDK contract rather than sharing React context or component objects. Bundle revision-specific dependencies into the disposable function scope; any shared runtime dependencies stay pinned and loaded once. Build checks must reject revision-specific native imports, including imports left in dependencies, that would recreate the module-cache problem. Module Federation is not required initially.

The proposed bundle lifecycle is deliberately small:

<dl class="trust-list">
<div><dt>Register and create</dt><dd>The bundle registers a factory under its project and release identity. The host checks the expected release and runtime compatibility, then creates an instance. Registration should not start application side effects.</dd></div>
<div><dt>Mount and signal readiness</dt><dd>The host supplies a container, theme, supported state, and the Nodex SDK. The instance renders its application and reports readiness or an error.</dd></div>
<div><dt>Update context and serialize state</dt><dd>Apply supported context changes without rebuilding, and export compatible filters or selections before replacing a revision.</dd></div>
<div><dt>Dispose and unregister</dt><dd>Unmount React; cancel requests, timers, and animation loops; remove listeners, subscriptions, and owned styles; destroy chart instances and release graphics resources. Delete the retired factory and release references from registries, caches, and callbacks. Removing the script element alone is not enough.</dd></div>
</dl>

The application calls the Nodex SDK directly; there is no cross-frame bridge. The SDK invokes the backend gateway, which independently authorizes every operation. bipp’s models, query generation, and access controls remain the preferred analytics path where supported interfaces permit. Approved backend connectors expose other services. bipp and external-service credentials stay on the backend; the SDK is an integration contract, not a browser security boundary.

Changing a view of Profit is different from changing the definition of Profit. Dashboard edits can use an approved metric; changes to shared business definitions belong in the model development and release workflow.

Backend compilation is the recommended default for consistent builds, reusable artifacts, and snapshot rendering. Browser-side building is possible, but would place the toolchain and its compatibility requirements in each editing session. Nodex components and approved third-party libraries are dependencies of the backend-built app. In a customer-managed installation, build and runtime services run in that customer’s environment.

## Where the application lives

<table class="storage-table">
<thead><tr><th scope="col">Asset</th><th scope="col">Proposed home</th></tr></thead>
<tbody>
<tr><th scope="row">Source code, styles, and dependency lockfile</th><td>Durable Nodex project storage with revision history.</td></tr>
<tr><th scope="row">Working files and build tools</th><td>A temporary, isolated backend workspace.</td></tr>
<tr><th scope="row">Permissions and draft/published pointers</th><td>Nodex’s application database.</td></tr>
<tr><th scope="row">Compiled JavaScript, CSS, and assets</th><td>Versioned artifact storage with authenticated delivery.</td></tr>
<tr><th scope="row">Business definitions and data</th><td>bipp models and the customer’s existing data sources.</td></tr>
<tr><th scope="row">Selections and drilldown state</th><td>The browser; persist selected settings when needed.</td></tr>
<tr><th scope="row">Live dashboard factories and instances</th><td>A bounded browser registry for active dashboards and in-flight replacements—not the full revision history.</td></tr>
</tbody>
</table>

The project’s source and configuration are authoritative. Temporary workspaces can be discarded after their changes are persisted. Chat history supplies context, but cannot be the only record of the application. Git integration is useful for history and export; a separate external repository for every dashboard is optional.

Nodex application revisions are distinct from bipp’s demonstrated model branches. Publishing pins an accepted application revision while further prompts change its draft.

## How changes reach the dashboard

<dl class="trust-list">
<div><dt>Data and interaction changes: rerender</dt><dd>A filter selection or graph expansion changes browser state and may fetch data. The running application rerenders without AI participation or a build.</dd></div>
<div><dt>Supported property changes: update configuration</dt><dd>Changing an exposed title, color, or layout setting can update saved configuration directly. No compilation is needed if the component implements that property.</dd></div>
<div><dt>Code changes: build a new revision</dt><dd>A prompt that introduces a new widget or changes interaction logic edits source. Nodex builds that revision and notifies the studio when its artifacts are ready.</dd></div>
</dl>

The notification carries the project, revision, and artifact location, using a channel such as SSE or WebSocket. The browser fetches the dashboard bundle and required assets, not the entire source repository. Unchanged assets can remain HTTP-cached, but a code edit may require a new complete dashboard bundle. The persistent host runtime is not reloaded for each edit.

The native dashboard host checks that the release still matches the latest requested edit, loads and registers the new bundle, and mounts an instance in a staging container with appropriate layout dimensions. It transfers compatible state, waits for readiness, switches the visible container, then disposes and unregisters the previous release. Failed or superseded candidates must also be cleaned up. Preparation should avoid write-side effects. Readiness coordinates display; it does not certify safety.

Keep the last working revision on ordinary build or preparation failures, and prevent older builds from replacing newer edits. State transfer is explicit and cannot preserve every selection after every code change. Native modules share the page: harmful side effects or an infinite loop can disrupt the studio itself, so fallback is not a containment guarantee.

Unique release URLs still identify immutable bundles, but classic script registration avoids adding an ES-module-cache entry for every dashboard revision. Once the old instance, factory, side effects, and other references are released, their objects and functions become eligible for garbage collection. Collection timing and leak-free behavior are not guaranteed; browser-managed code caches may also persist. Keep revision history on the backend and reload an older bundle for rollback rather than retaining every factory in memory.

Validate long editing sessions with repeated replacement and rollback tests, checking retained objects, listeners, DOM nodes, and graphics resources. Hot module replacement may later improve edit latency, but does not itself guarantee native module-cache eviction and must preserve the disposable-bundle contract. This removes the specific per-revision ES-module accumulation issue, not every possible reason for a page refresh. Published viewers load the pinned build, not an unfinished development session.

Use scoped styles or CSS Modules to avoid accidental style conflicts. Shadow DOM is optional for style encapsulation, not JavaScript security. Changing the bundle format does not change the shared-page trust model.

## Deep interactions and reusable widgets

Consider a request to show a supplier network, expand facilities on double-click, and open deliveries when a facility is selected. The generated application holds the graph, navigation state, and event handlers.

<ol class="runtime-steps">
<li>A double-click identifies the supplier and starts a loading state.</li>
<li>The widget calls the Nodex SDK, which requests facilities through the backend gateway.</li>
<li>The gateway checks permissions and invokes bipp or an approved service.</li>
<li>The response updates application state and expands the graph.</li>
<li>Further selections load details; breadcrumbs, cancellation, and errors are handled by the application.</li>
</ol>

The AI creates or edits this behavior during authoring. Normal clicks execute the resulting program. A widget can become reusable once it has a stable interface, a version, and defined runtime and export behavior.

Standard Nodex components should expose properties that visual controls can edit. Custom components expose only their declared properties; deeper changes use prompts or code. Arbitrary generated code cannot automatically map to a complete drag-and-drop editor. Both editing paths must update the same project source or configuration.

Custom visuals need a snapshot mode or a readiness signal for asynchronous rendering. Integration must prove that bipp’s export and scheduling services can consume Nodex output, or identify an additional rendering service. Existing bipp delivery does not automatically support every generated app.

## The same studio, two ways to use it

<div class="delivery-grid">
<div><span class="delivery-label">Inside the customer’s product</span><h3>Embedded studio</h3><p>Users create and refine dashboards in their existing application. The host supplies trusted identity and workspace context; backend services enforce permissions.</p></div>
<div><span class="delivery-label">A dedicated application</span><h3>Independent studio</h3><p>The same chat, canvas, and saved dashboards are available in a standalone workspace. Independent deployment includes the required backend services and integrations.</p></div>
</div>

Embedding determines where the interface appears. Hosting determines where the services run. Assess bipp’s existing hosting options for both the SaaS offering and customer-managed installations, including AI-provider access and data policies.

Embedding exposes Nodex’s own authoring interface and application runtime. Host identity, session handling, and access to bipp’s backend services require an integration design; bipp’s embedded dashboard UI is not part of this approach.

## What makes the result trustworthy

<dl class="trust-list">
<div><dt>Correct business meaning</dt><dd>Use approved definitions and relationships, and clarify ambiguous requests. A structurally valid dashboard can still show the wrong calculation or comparison.</dd></div>
<div><dt>Backend permissions and build isolation</dt><dd>Apply permissions to queries, saved apps, AI context, and delivery. Isolate backend build and test workers, keep service credentials server-side, and authorize every operation. A filter selecting Chicago is not itself an authorization boundary.</dd></div>
<div><dt>Native execution requires trusted code</dt><dd>Generated modules can access the studio’s DOM, browser storage, and APIs available to page scripts. Dependency controls, static checks, browser tests, and release review reduce risk but do not sandbox arbitrary JavaScript. SDK restrictions, error boundaries, and Shadow DOM are not security isolation. Native execution treats approved modules as trusted frontend code, not untrusted plugins.</dd></div>
<div><dt>Inspectability and recovery</dt><dd>Show what changed, preserve unrelated edits, and retain a working version when an edit fails. Verify the results and interactions, not only the generated structure.</dd></div>
<div><dt>Reliable distribution</dt><dd>Check customized visuals in the live dashboard and exported snapshots. One filtered schedule does not establish automatic personalization for every recipient.</dd></div>
</dl>

## Prove the product with one workflow

Use the existing retail model to create monthly sales and profit views, add top brands, link filters, and revise the layout through conversation. Save and reopen the result, then exercise the same authoring flow inside a host application and independently.

Include one design the current editor cannot conveniently express. Compare it with the existing bipp workflow to separate faster authoring from additional expressive power. Verify a filtered PDF snapshot; conversational scheduling can follow after the creation experience is proven.

Exercise the complete application lifecycle: persist source, build and register a bundle, mount its instance directly in the studio, change one widget through chat, transfer compatible state, switch revisions, and dispose and unregister the old release. Repeat updates and rollbacks to detect retained resources; verify cleanup of failed candidates and recovery from an ordinary failed build or mount. Include a double-click that fetches authorized detail data and verify that it works without another AI call.

Measure time to an accepted dashboard, correctness against agreed results, successful follow-up edits, and specialist intervention. Include a restricted user, an ambiguous metric, and a failed edit.

Before committing to implementation, confirm access to model metadata, query interfaces, permission enforcement, and export services. Nodex manages its own application source and authoring permissions. The investment decision is whether Nodex lets users build and maintain useful dashboards with less effort and greater freedom.

## Evidence and remaining uncertainty

This understanding combines three supplied screen recordings and an animated modeling demonstration with bipp’s published product material. The recordings have no audio tracks; analysis used their visible workflows and captions. They show historical interfaces and establish demonstrated capabilities, not the exact state of every current installation.

The in-database recording demonstrates query generation and exploration. The modeling animation demonstrates tables and joins. The Git recording demonstrates metric development, conflict resolution, release, and reuse in a chart. The scheduled-delivery recording demonstrates a composed dashboard, a filtered schedule, and an emailed snapshot.

Public references: [data modeling](https://www.bipp.io/features/bipp-data-modeling-layer/), [version control](https://www.bipp.io/features/git-based-version-control/), [dashboards and visualization](https://www.bipp.io/features/data-visualization/), [embedding](https://www.bipp.io/platform/embedded-analytics/), [security](https://bipp.io/platform/security/), [scheduled delivery](https://www.bipp.io/features/scheduled-delivery-and-alerts/), and [hosting options](https://www.bipp.io/).

The [healthcare case study](https://www.bipp.io/casestudies/fortune50-healthcare-company-reduces-its-cost-with-boost-in-business-intelligence-performance) describes bippDash and JavaScript extensions. This is background on bipp’s existing product, not a dependency of Nodex’s UI or rendering architecture.

Technical references for the proposed delivery model: [IIFE bundle output](https://esbuild.github.io/api/#format), [hot-update cleanup hooks](https://vite.dev/guide/api-hmr), [native module-cache limitations motivating classic bundles](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/import), [React mounting and cleanup](https://react.dev/reference/react-dom/client/createRoot), and [Shadow DOM encapsulation limits](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_shadow_DOM). These establish available building blocks, not a completed Nodex implementation or guaranteed memory reclamation.

Available bipp model and query interfaces, permission enforcement, and compatibility of generated applications with backend export services require product and code review. Nodex’s independently developed UI, managed projects, build pipeline, gateway, and application runtime remain proposed work.
