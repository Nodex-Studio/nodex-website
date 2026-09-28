# ADR-0011 — Geo widget kinds in the schema, renderer in the interior

**Status:** Accepted · 2026-09-28

## Context

Two of the highest-profile dashboards built on the platform to date were maps: a
shipment tracker showing origin, destination, route, ETA and live temperature, and
a vaccine distribution map. Both were hand-built in JavaScript, because the schema
had no map node type.

They were also the strongest argument for an escape hatch. They are in fact the
strongest argument against one ([ADR-0008](0008-no-escape-hatch.md)): the demand
was for one missing widget kind, not for arbitrary code.

## Decision

**`map` is a widget kind with a bounded spec.** Its renderer is generated interior
([04-codegen.md](../04-codegen.md)), free to change between builds, and is ours —
not customer code.

Indicative shape:

```ts
type MapSpec = {
  basemap: BasemapRef;          // resolved from runtime config, never baked in (I7)
  view: { fit: 'data' | 'bounds' | 'fixed'; center?: GeoPoint; zoom?: number };
  layers: MapLayer[];
};

type MapLayer =
  | { kind: 'marker';     id: NodeId; at: GeoFieldRef; label?: DimensionRef;
                          size?: MetricRef; color?: ColorRule; tooltip: FieldRef[] }
  | { kind: 'route';      id: NodeId; path: GeoPathRef; color?: ColorRule; direction?: boolean }
  | { kind: 'choropleth'; id: NodeId; region: DimensionRef; metric: MetricRef; scale: ScaleSpec }
  | { kind: 'heat';       id: NodeId; at: GeoFieldRef; weight?: MetricRef };
```

The shipment tracker is then a marker layer plus a route layer, `tooltip:
[shipment_id, eta, temperature]`, and a `ColorRule` band that turns a marker red
when temperature leaves its declared range. Promptable, panel-editable, and every
query stays in the manifest.

## Consequences

**Good.** The flagship visual becomes a first-class node: authored by prompt,
refined in the property panel, versioned like anything else, and identical across
all six delivery modes.

**It needs geo types in the modeling layer.** `GeoFieldRef` and `GeoPathRef` must
resolve against declared model entities, which means the modeling layer has to
express point, path and region fields. Same ownership question as O10.

**Basemap tiles are third-party egress from the end user's browser.** A map that
hard-requires tiles from a commercial provider breaks the airgapped deployment
path that on-premise customers chose specifically because they have no egress. The
basemap must therefore be operator-configured and self-hostable, and a dashboard
must degrade to a plain coordinate plot when no tile source is reachable rather
than rendering an empty grey box.

**It constrains O2.** Map libraries inject global CSS and measure layout in ways
that behave badly inside a shadow root — the same constraint that already narrows
the chart library choice, applied to a second library. Deciding both together is
cheaper than deciding them apart.

## Alternatives considered

**A custom JavaScript map widget.** How it was done before, and rejected in
[ADR-0008](0008-no-escape-hatch.md).

**Server-rendered map images.** A static image per view avoids the shadow-root and
tile problems in the browser, but loses pan, zoom, hover and drill — most of why a
map is used — and needs a headless renderer in the data plane. Rejected for
interactive use. Note that scheduled PDF delivery needs that renderer anyway, so
the two should share it rather than each growing one.
