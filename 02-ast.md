# 02 — The AST

The AST is the dashboard (**I1**). Studio edits it, the build plane compiles it,
and its shape determines the public API that a consuming developer writes code
against. Everything else is derived and disposable.

## Design principle: the schema is closed

The AST conforms to a fixed schema. Every node type has a known set of
properties, and every property has a known set of legal values. Nothing in a
valid AST is free-form except user-supplied strings such as titles.

This is not a limitation to be apologised for — it is the property that makes
the product work:

- **It makes visual editing possible.** A form can only render what it has a
  field for. A bounded schema is exactly what a property panel is.
- **It makes prompt editing round-trip.** Because a prompt produces the same
  representation that a dropdown produces, a dashboard can be built by prompt and
  refined by hand indefinitely, in any order.
- **It makes generation verifiable.** A model's output is either valid against
  the schema or it is not. There is no "looks plausible" middle ground, which is
  the failure mode of free-form code generation.
- **It makes regeneration safe.** The build is a pure function of a validated
  structure.

The cost is real and should be stated plainly: a request outside the schema must
fail honestly rather than improvise. There is no escape hatch and there will not
be one — the schema growing is the only valve
([ADR-0008](adr/0008-no-escape-hatch.md),
[When the schema falls short](03-studio.md#when-the-schema-falls-short)).

## Node types

Indicative, not final. The point is the shape, not the field list.

```ts
type Dashboard = {
  id: NodeId;
  schemaVersion: string;        // see "Schema versioning"
  title: string;
  theme: ThemeRef;
  params: Param[];              // dashboard-level inputs, exposed as public props
  filters: Filter[];
  layout: Layout;
  widgets: Widget[];
};

type Layout = {
  kind: 'grid';
  columns: number;
  items: { widgetId: NodeId; x: number; y: number; w: number; h: number }[];
};

type Filter = {
  id: NodeId;
  label: string;
  field: ModelFieldRef;          // resolved against the modeling layer
  operator: 'equals' | 'in' | 'between' | 'contains' | ...;
  control: 'select' | 'multiselect' | 'daterange' | 'text';
  defaultValue?: Value;
  appliesTo: NodeId[] | 'all';
};

// fields every Widget variant also carries
type WidgetCommon = {
  optional?: boolean;            // a binding opts in; typed possibly-absent (I12)
  link?: LinkSpec;               // drill to another dashboard
};

type Widget =
  | { kind: 'kpi';   id: NodeId; title: string; metric: MetricRef; format: FormatSpec; comparison?: ComparisonSpec }
  | { kind: 'chart'; id: NodeId; title: string; chart: ChartSpec }
  | { kind: 'table'; id: NodeId; title: string; columns: ColumnSpec[]; pageSize: number }
  | { kind: 'text';  id: NodeId; content: string }
  | { kind: 'map';   id: NodeId; title: string; map: MapSpec }
  | { kind: 'section';  id: NodeId; title: string; display: 'group' | 'tabs'; layout: Layout }
  | { kind: 'repeater'; id: NodeId; over: RepeatSpec; layout: Layout };

type ChartSpec = {
  type: 'bar' | 'line' | 'area' | 'donut' | 'scatter' | 'combo';
  x: DimensionRef;
  series: { metric: MetricRef; type?: 'bar' | 'line'; axis?: 'left' | 'right' }[];
  sort?: SortSpec;
  limit?: number;
  referenceLines?: ReferenceLine[];
};

type RepeatSpec = {
  key: DimensionRef;             // must be a stable business key — see below
  orderBy?: SortSpec;
  limit: number;                 // hard fan-out bound; default is O9
  empty: 'hide' | 'placeholder';
};

type LinkSpec = {
  to: DashboardRef;              // checked at build; resolution is O13
  params: { from: FieldRef | ParamRef; to: ParamName }[];
  open: 'host' | 'self' | 'new'; // 'host' emits navigate-request, never routes itself
};
```

`section` and `repeater` are **containers**: they hold their own `Layout`, so
grouping and repetition nest without needing a second layout concept. A
scorecard's four KPI groups are four sections; a tile per plant is one repeater
over the plant dimension. `MapSpec` is specified in
[ADR-0011](adr/0011-geo-widget-kinds.md).

There is deliberately no `custom` kind ([ADR-0008](adr/0008-no-escape-hatch.md)).

`ModelFieldRef`, `MetricRef`, and `DimensionRef` resolve against the customer's
bipp data models. The AST references model entities by name; it does not contain
SQL, table names, or join logic. That is the modeling layer's job and it is
already solved — see [06-data-plane.md](06-data-plane.md).

## Node identity

**Ids are assigned once, at creation, and never change (I5).**

They are opaque and meaningless — `w_7f3a91`, not `total-sales` and not
`widget-3`. Specifically, an id is never derived from:

- the widget's title (a user renaming "Revenue" to "Net Revenue" must not rename
  anything),
- its position in the layout (reordering is not an API change),
- its index in an array (inserting is not an API change),
- its content (changing a metric is not an API change).

This matters because the exported package's public API is derived from these ids
(**I4**), and a consuming developer's hand-written code references them:

```tsx
<SalesDashboard region="APAC" onWidgetClick={(e) => ...} />
```

If ids drifted on regeneration, an authoring developer renaming a chart on a
Tuesday would break a different team's production build, with no signal to either
of them. Stable identity is what converts that from an accident into a
deliberate, reviewable API change — see
[07-versioning.md](07-versioning.md#mechanical-semver).

Deleting a node retires its id permanently. Ids are never reused.

## Instance identity

A repeater's contents exist once in the AST and many times on screen. How many
times is decided by data — the distinct values of the repeat key — which the AST
does not know and must not have to be edited to learn. So the rule above cannot
apply to them, and **I11** governs instead
([ADR-0009](adr/0009-runtime-repetition.md)).

**Authored identity** is everything described in the previous section: assigned
once, opaque, retired on delete. The repeater node itself has it. **Instance
identity** is derived:

```
w_7f3a91              the repeater      — authored
w_7f3a91#plant=P-4471 one instance      — derived, enumerated at query time
```

Four rules make this safe:

- **The key is a stable business key**, declared in the modeling layer. Never an
  ordinal, an array index, a row number, or a position in the result. If it were
  positional, onboarding the 131st plant would silently renumber the other 130,
  which is the [ADR-0006](adr/0006-stable-node-identity.md) failure arriving
  through a side door and triggered by data rather than by an edit.
- **Instances are never retired.** A key value missing from today's result may
  return tomorrow. That is not a deletion, and the id is not burned.
- **The public API exposes the repeater, never its members** (I4). A repeater is
  a collection in the generated surface; instance ids appear only in event
  payloads and drill targets, as `{ repeater, key }`.
- **A repeater is not a fan-out of queries.** Its children compile to one grouped
  query with the key as a dimension, partitioned after execution
  ([06-data-plane.md](06-data-plane.md)).

The cost is honest and worth naming: a consuming developer can handle a click on
any instance, but cannot write code against one particular instance and be told
mechanically when it disappears. The alternative is worse — it would make every
data change an API change.

## What is not AST

**I1** says a dashboard *is* its AST. Three things that a dashboard displays are
nonetheless not part of it, and putting them there would be a mistake:

| | Lives in | Why not AST |
|---|---|---|
| **Bindings** | Data plane registry ([ADR-0010](adr/0010-definition-and-binding.md)) | Adding a site would otherwise be an AST edit, a rebuild, and a version bump for every consumer (I12) |
| **Repeater instances** | Enumerated at query time | The AST cannot contain what only the data knows (I11) |
| **Annotations** | Data plane store | They are the customer's commentary, anchored to semantic coordinates rather than to node ids, so they survive a widget being moved or deleted (I14) |

The test is simple: if it changes without anyone authoring anything, it is not
AST.

## Patches, not replacements

Every edit — a prompt, a drag, a dropdown selection — produces a **patch**
against the current AST (**I6**). Nothing produces a new tree.

```ts
type Patch = {
  id: PatchId;
  baseVersion: AstVersion;       // optimistic concurrency
  ops: Op[];
  origin: 'prompt' | 'manual';
  promptText?: string;           // retained for history and audit
};

type Op =
  | { op: 'add';     path: NodePath; value: unknown }
  | { op: 'remove';  path: NodePath }
  | { op: 'replace'; path: NodePath; value: unknown }
  | { op: 'move';    path: NodePath; to: NodePath };
```

This is the single most consequential mechanical decision in Studio. If a prompt
regenerated the whole AST, every manual adjustment the user had made would be
silently discarded on the next prompt — which is the specific failure that makes
people abandon AI builders. Patches make "prompt, tweak, prompt again" the normal
workflow rather than a losing battle.

Patches also give you an undo stack, a change history, an audit trail, and
collaborative editing for free, because they are the same primitive.

## Provenance

Each property carries a flag recording whether its current value was set by a
prompt or by hand.

```ts
type Provenance = Record<NodePath, { origin: 'prompt' | 'manual'; at: Timestamp }>;
```

The rule: **a prompt-originated patch does not overwrite a manually-set
property.** It either leaves it alone or surfaces the conflict for the user to
resolve.

Without this, the interaction degrades in a predictable way. A user hand-picks a
chart colour, then asks for an unrelated change, and the model — regenerating
that widget's properties from its own defaults — resets the colour. The user
re-applies it. It happens again. They stop trusting prompts for anything they
care about.

Provenance is cleared for a property when the user explicitly asks a prompt to
change it ("make this one green").

## Schema versioning

The AST schema is a long-lived contract between the control plane and
customer-operated runtimes that upgrade on their own schedule
([07-versioning.md](07-versioning.md)). Studio may be twelve releases ahead of a
customer's runtime.

- Every AST carries `schemaVersion`.
- Additive changes (new optional property, new widget kind) are minor. New widget
  kinds are the primary way the platform grows capability, now that there is no
  escape hatch ([ADR-0008](adr/0008-no-escape-hatch.md)).
- Removing or re-typing a property is major and requires a migration.
- Migrations are forward-only, versioned, and applied in the control plane when a
  dashboard is opened. Stored ASTs are upgraded eagerly, never lazily at read
  time in the runtime.
- The build plane records the minimum runtime version an AST requires;
  the artifact declares it and the runtime refuses to execute a manifest it is
  too old to understand, with a clear error rather than a partial render.

## Validation

An AST is validated before it is stored and again before it is built:

1. **Structural** — conforms to the schema.
2. **Referential** — every `ModelFieldRef` / `MetricRef` resolves against the
   customer's current data models.
3. **Semantic** — the combination makes sense (a metric on the x-axis of a bar
   chart, a filter targeting a widget that doesn't exist, a layout item with no
   widget, a repeater whose key is not a declared stable business key, a link
   whose target dashboard does not accept the params mapped to it).

Referential validation runs against the models a **binding** resolves to, not
against models in the abstract. A definition is valid only if every binding in
its set satisfies it — which is what makes "conform your data to this format" a
checkable contract rather than a convention (O10).

Validation failure from a prompt is a repair loop
([03-studio.md](03-studio.md#validation-and-repair)). Validation failure at build
time is a bug in Studio, and should be impossible by the time an AST is stored.

## Storage

The AST is stored versioned, with full patch history. Each dashboard version is
immutable and addressable, because exported packages pin to one.

**O5 (OPEN)** — where the AST lives for on-premise customers. bipp already
provides git-based version control for data models, which argues for storing
dashboard ASTs in the customer's own git alongside them: it keeps authored
artifacts under customer control, gives review and rollback for free, and fits
their existing compliance story. The alternative — ASTs in Nodex cloud — is
simpler to operate but puts authored IP in the control plane for customers whose
entire reason for choosing on-premise was to avoid that.
