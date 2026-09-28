# Nodex Studio

A proposed dashboard-building studio with AI chat, built on bipp's existing
analytics and delivery capabilities, embedded or independently deployed.
Nodex’s UI and dashboard rendering are independently developed; bipp integration
is through backend capabilities, not reuse of its editor or visual components.
Disposable dashboard bundles are built on the backend, register factories with a
persistent host, and mount natively in the studio's DOM. Retired instances and
factories are released instead of importing a new ES module for every revision.
This replaces the iframe proposal and still requires a trusted-code execution model.

The [current product and architecture document](00-executive-summary.md) starts
fresh from that product definition. It covers the user experience, dashboard
flexibility, proposed architecture, source storage, backend builds, incremental
delivery, custom interactions, trust, bipp integration, and a pilot.
It consolidates findings from three supplied recordings, a modeling animation,
and official product sources, distinguishing evidence from proposed work.

The [HTML build](html/README.md) produces the overview and a new
[detailed native architecture reference](html/technical.md). The previous numbered
specifications, ADRs, and diagrams are superseded working material, not current
requirements, and are not included in the HTML. The technical route now serves
the new native-bundle contracts and diagrams, not the historical appendix.

[Editorial guidance](EDITORIAL.md) records the current scope.

Status: proposed design, 29 September 2026. Publication of the overview and
detailed native architecture reference is authorized. Publication does not imply
product implementation.
