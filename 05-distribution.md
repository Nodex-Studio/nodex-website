# 05 — Distribution

One build, six deliveries. The frontend compiles to custom elements
([04-codegen.md](04-codegen.md)); each mode is a packaging of the same core, not
a separate pipeline.

## The six modes

| Mode | Operated by | What ships |
|---|---|---|
| Standalone, Nodex-hosted | **Nodex** | App shell + core bundle, served from Nodex cloud |
| Standalone, self-hosted | Customer | Same artifact, customer's infrastructure |
| iframe embed | Customer | App shell + a `postMessage` API |
| Web component | Customer | The core bundle, unchanged |
| CDN | Customer | ESM at immutable versioned URLs, with SRI |
| npm library | Customer | Package with framework wrappers and types |

Only the first is operated by Nodex. The other five are customer-managed: the
customer deploys them, and they query a runtime the customer also operates. **A
customer-managed frontend never queries Nodex cloud** — see
[08-security.md](08-security.md).

Note that these are *delivery* modes. Where the query runtime lives is a separate
question ([06-data-plane.md](06-data-plane.md)), and the two must not be
conflated: a customer using the npm library and a customer using the iframe
embed have identical data-plane requirements.

## Runtime configuration

**Artifacts carry no endpoint and no credentials (I7).** Both are injected at
initialisation:

```js
import { mount } from '@nodex/dashboard-sales';

mount(document.querySelector('#dash'), {
  endpoint: 'https://analytics.acme.internal/q',   // customer's runtime
  getToken: () => acmeAuth.embedToken(),           // host app mints it
  theme: acmeTheme,
});
```

If the endpoint were baked in at build time, every deployment topology would need
its own build, and the six modes would multiply by the number of environments
each customer runs. Injection keeps it at six, forever, and means an artifact can
be promoted from staging to production without a rebuild.

## Package layout

```json
{
  "name": "@nodex/dashboard-sales",
  "version": "2.4.0",
  "type": "module",
  "sideEffects": false,
  "exports": {
    ".":            { "types": "./dist/index.d.ts",   "import": "./dist/index.js" },
    "./elements":   { "types": "./dist/elements.d.ts","import": "./dist/elements.js" },
    "./react":      { "types": "./dist/react.d.ts",   "import": "./dist/react.js" },
    "./vue":        { "types": "./dist/vue.d.ts",     "import": "./dist/vue.js" },
    "./angular":    { "types": "./dist/angular.d.ts", "import": "./dist/angular.js" },
    "./svelte":     { "types": "./dist/svelte.d.ts",  "import": "./dist/svelte.js" },
    "./server":     { "types": "./dist/server.d.ts",  "import": "./dist/server.js" },
    "./styles.css": "./dist/styles.css"
  },
  "peerDependencies": {
    "@nodex/runtime": "^2.0.0",
    "react": ">=17", "react-dom": ">=17",
    "vue": ">=3", "svelte": ">=4"
  },
  "peerDependenciesMeta": {
    "react": { "optional": true }, "react-dom": { "optional": true },
    "vue": { "optional": true }, "svelte": { "optional": true }
  }
}
```

## Framework wrappers

Vue, Svelte, and Angular consume custom elements natively — Vue and Svelte set
properties and listen for custom events correctly out of the box; Angular needs
`CUSTOM_ELEMENTS_SCHEMA` on the consuming module and binds with `[prop]` and
`(event)`.

**React is the exception and needs a real wrapper.** React below v19 sets
everything as string attributes and does not listen for custom events, so the
wrapper assigns properties via ref and binds events with `addEventListener`:

```tsx
export const SalesDashboard = forwardRef<SalesDashboardElement, Props>((props, ref) => {
  const el = useRef<SalesDashboardElement>(null);
  useImperativeHandle(ref, () => el.current!);

  useEffect(() => {                       // properties, not attributes
    if (!el.current) return;
    el.current.region = props.region ?? null;
    el.current.dateRange = props.dateRange ?? null;
  }, [props.region, props.dateRange]);

  useEffect(() => {                       // custom events
    const node = el.current;
    if (!node || !props.onWidgetClick) return;
    const h = (e: Event) => props.onWidgetClick!(e as WidgetClickEvent);
    node.addEventListener('widget-click', h);
    return () => node.removeEventListener('widget-click', h);
  }, [props.onWidgetClick]);

  return <nodex-dashboard-sales ref={el} />;
});
```

React 19 supports custom elements natively, but customers will be on 17 and 18
for years. Ship the wrapper regardless; it is generated from the shell and costs
nothing per dashboard.

## Consumer-facing hazards

These produce support tickets rather than design debates, and each needs an
explicit mitigation in the generated package.

**Tag name collisions.** A company with several internal dashboards will end up
with two versions of `@nodex/runtime` on one page, and the second
`customElements.define()` throws *"already defined"*, taking down the host
application. Mitigations: a define-guard that no-ops on redefinition rather than
throwing, version-scoped tag names for shared runtime elements, and a dev-mode
warning naming both versions.

**Duplicate runtimes.** Related but distinct: even without a collision, ten
dashboard packages each bundling the runtime ship ten copies. Externalise it as
`@nodex/runtime` and declare it a peer dependency, so the consumer's package
manager deduplicates. <a id="shared-runtime"></a>

**Peer dependencies.** React, Vue, and Svelte must be peers, never dependencies.
Bundling React yields two Reacts and invalid-hook-call errors in the consumer's
app, which is a miserable thing to debug from their side.

**SSR.** The consuming application is plausibly Next.js or Nuxt. A module that
touches `HTMLElement` at import time crashes the server build. Ship a
client-only entry (`./server` exporting inert stubs, dynamic registration on
mount), and document it prominently — this is the first thing a consuming
developer will hit.

**TypeScript.** Hand-written consumer code needs real declarations:
`HTMLElementTagNameMap` augmentation for the elements, JSX intrinsic
declarations for React, and typed event payloads. Without them the consuming
developer gets no autocomplete and a type error on every tag.

## iframe embed

The iframe mode exists for customers who want hard isolation rather than
integration — a different security posture, not a different feature set. It ships
the standalone shell plus a narrow `postMessage` protocol:

- **In:** set params, set filters, set theme, refresh, provide token.
- **Out:** ready, height changed (for auto-resize), widget clicked, filter
  changed, error.

Every message is origin-checked against an allowlist configured per deployment.
The protocol is versioned like any other public API
([07-versioning.md](07-versioning.md)).

## CDN

- Immutable, versioned URLs. A published URL's bytes never change.
- Subresource Integrity hashes published with each release.
- The shared runtime is a separate, separately versioned URL so multiple
  dashboards on one page fetch it once.
- No latest/floating tag. Consumers pin, deliberately.
