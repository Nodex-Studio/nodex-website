# Nodex Studio, built on bipp

A conversational dashboard studio built on bipp’s analytics foundation, available inside a customer’s product or as an independent application.

## The product

Nodex is a proposed studio where users describe a business need, see a working dashboard take shape, and refine it through chat or direct editing. The studio itself can be embedded in a customer’s application or deployed independently.

bipp supplies an established foundation for data modeling, query generation, reporting, dashboards, and delivery. Nodex would coordinate those capabilities through conversation and extend the dashboard experience where existing tools cannot express what users need.

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

bipp also publicly describes an embedding SDK, static and dynamic embedding, granular access controls, and cloud or customer-managed deployment. These are existing capabilities to assess for reuse. Embedding the full Nodex authoring studio still requires an integration design.

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
<div><span class="item-number">01</span><div><h3>Compose existing capabilities</h3><p>Use bipp’s charts, metrics, filters, and interactions in arrangements chosen around the user’s question.</p></div></div>
<div><span class="item-number">02</span><div><h3>Support more expressive designs</h3><p>Test specific requests that exceed the current editor: unusual layouts, specialized visualizations, or custom interactions. Establish the actual limit before choosing an extension.</p></div></div>
<div><span class="item-number">03</span><div><h3>Keep the result maintainable</h3><p>A customized dashboard must remain editable, respect permissions, and support the viewing and export workflows its users need.</p></div></div>
</div>

bipp already describes customization through HTML, JavaScript, and its dashboard structuring language, bippDash. Inspect those capabilities before introducing a replacement format or rendering engine. Their existence does not establish that arbitrary creation is accessible to business users through conversation.

“Arbitrary” is an ambition for extensibility. Unsupported requests should produce a clear explanation or a supported alternative, rather than a plausible but incorrect result.

## How Nodex uses bipp

The proposed architecture puts conversation and editing above bipp’s existing analytics and delivery capabilities. The integration must establish which supported interfaces can expose them.

<!--ARCHITECTURE-->

The assistant interprets the request, discovers permitted model fields, asks about missing business meaning, and proposes dashboard changes. Application services validate and apply those changes. bipp’s model and query facilities should remain the preferred path for data access, with authorization enforced independently of the assistant.

Chat and direct editing need a shared, saved dashboard representation. First establish whether bipp’s existing definitions can provide it. Extend only where required so AI edits, manual refinements, saving, and reopening remain consistent.

Changing a view of Profit is different from changing the definition of Profit. Dashboard edits can use an approved metric; changes to shared business definitions belong in the model development and release workflow.

Specialized components or generated code may be needed for additional freedom. They require isolated execution and limited data access. New visuals must also support snapshot rendering, or clearly declare an export limitation before users rely on scheduled delivery.

## The same studio, two ways to use it

<div class="delivery-grid">
<div><span class="delivery-label">Inside the customer’s product</span><h3>Embedded studio</h3><p>Users create and refine dashboards in their existing application. The host supplies trusted identity and workspace context; backend services enforce permissions.</p></div>
<div><span class="delivery-label">A dedicated application</span><h3>Independent studio</h3><p>The same chat, canvas, and saved dashboards are available in a standalone workspace. Independent deployment includes the required backend services and integrations.</p></div>
</div>

Embedding determines where the interface appears. Hosting determines where the services run. Assess bipp’s existing hosting options for both the SaaS offering and customer-managed installations, including AI-provider access and data policies.

bipp’s published dashboard embedding is a starting point. Whether its SDK exposes the full authoring experience, or needs additional interfaces, remains an integration question.

## What makes the result trustworthy

<dl class="trust-list">
<div><dt>Correct business meaning</dt><dd>Use approved definitions and relationships, and clarify ambiguous requests. A structurally valid dashboard can still show the wrong calculation or comparison.</dd></div>
<div><dt>Consistent access</dt><dd>Apply customer and user permissions to queries, saved dashboards, AI context, and delivery. A filter selecting Chicago is not itself an authorization boundary.</dd></div>
<div><dt>Inspectability and recovery</dt><dd>Show what changed, preserve unrelated edits, and retain a working version when an edit fails. Verify the results and interactions, not only the generated structure.</dd></div>
<div><dt>Reliable distribution</dt><dd>Check customized visuals in the live dashboard and exported snapshots. One filtered schedule does not establish automatic personalization for every recipient.</dd></div>
</dl>

## Prove the product with one workflow

Use the existing retail model to create monthly sales and profit views, add top brands, link filters, and revise the layout through conversation. Save and reopen the result, then exercise the same authoring flow inside a host application and independently.

Include one design the current editor cannot conveniently express. Compare it with the existing bipp workflow to separate faster authoring from additional expressive power. Verify a filtered PDF snapshot; conversational scheduling can follow after the creation experience is proven.

Measure time to an accepted dashboard, correctness against agreed results, successful follow-up edits, and specialist intervention. Include a restricted user, an ambiguous metric, and a failed edit.

Before committing to implementation, confirm access to report and dashboard definitions, query interfaces, extension boundaries, authoring permissions, and export services. The investment decision is whether Nodex lets users build and maintain useful dashboards with less effort and greater freedom.

## Evidence and remaining uncertainty

This understanding combines three supplied screen recordings and an animated modeling demonstration with bipp’s published product material. The recordings have no audio tracks; analysis used their visible workflows and captions. They show historical interfaces and establish demonstrated capabilities, not the exact state of every current installation.

The in-database recording demonstrates query generation and exploration. The modeling animation demonstrates tables and joins. The Git recording demonstrates metric development, conflict resolution, release, and reuse in a chart. The scheduled-delivery recording demonstrates a composed dashboard, a filtered schedule, and an emailed snapshot.

Public references: [data modeling](https://www.bipp.io/features/bipp-data-modeling-layer/), [version control](https://www.bipp.io/features/git-based-version-control/), [dashboards and visualization](https://www.bipp.io/features/data-visualization/), [embedding](https://www.bipp.io/platform/embedded-analytics/), [security](https://bipp.io/platform/security/), [scheduled delivery](https://www.bipp.io/features/scheduled-delivery-and-alerts/), and [hosting options](https://www.bipp.io/).

The [healthcare case study](https://www.bipp.io/casestudies/fortune50-healthcare-company-reduces-its-cost-with-boost-in-business-intelligence-performance) describes bippDash and JavaScript extensions. Customer-specific examples do not establish that every extension is available as a general-purpose interface.

The precise limits of the current dashboard editor, availability of programmatic authoring, and compatibility of custom visuals with exports require product and code review. Nodex’s conversation and extension capabilities remain proposed work.
