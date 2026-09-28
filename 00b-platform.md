# bipp foundation and integration questions

This baseline reflects bipp's public product pages reviewed on 28 September
2026. They establish published capabilities, including examples of customer
solutions. Current interfaces, packaging and roadmap need confirmation with
bipp; a capability not described publicly is not presumed absent.

## What bipp already provides

bipp describes semantic modeling, SQL generation, in-database queries,
self-service exploration, embedded analytics, scheduled reporting and alerts.
These are foundations for the proposed workflow.
[Platform overview](https://www.bipp.io/).

| Published capability | Relevance to Nodex |
|---|---|
| Embedded SDK, static and dynamic embedding, filtered embed tokens | Establish the existing integration surface before designing component publishing. |
| SSO, granular role-based controls, row and column security, SOC 2 Type II | Reuse applicable controls and confirm how they extend to published components and runtime operations. |
| Maps, drill-down, grid charts and dashboard editing | Map existing visualization capabilities into the supported authoring schema. |
| Audit logs and usage reports, with plan-dependent availability | Confirm coverage and availability for the pilot rather than list them as missing features. |

Sources: [embedded analytics](https://www.bipp.io/platform/embedded-analytics/),
[security](https://bipp.io/platform/security/),
[visualizations](https://www.bipp.io/features/data-visualization/), and
[platform and plan overview](https://www.bipp.io/).

The healthcare case study describes bippLang and bippDash reuse, scorecards at
130 locations at the time of publication, custom maps and version-controlled
executive comments. These are precedents for multi-site workflows and
annotations, not evidence that every capability is exposed through a general
integration API. [Customer case study](https://www.bipp.io/casestudies/fortune50-healthcare-company-reduces-its-cost-with-boost-in-business-intelligence-performance).

## What Nodex proposes to add

The proposal combines prompt and visual authoring with versioned component
publishing and independent site bindings. The hypothesis is that this can
reduce authoring, integration and rollout effort beyond existing workflows.
The pilot should compare that hypothesis with what bipp already supports.

| Proposed contract | Question to validate |
|---|---|
| One structured dashboard definition | Can it map to or extend bippDash, and preserve existing model references? |
| Versioned component interfaces | Which SDK capabilities are reusable, and what compatibility guarantees need to be added? |
| One definition with per-site bindings | How do existing models declare equivalent shapes across sites? |
| Customer-environment query runtime | Which query, security and scheduling services can be reused or packaged for this deployment? |

## Ownership

Ownership of model interfaces, site onboarding and content governance should be
agreed jointly (O10, O6). The document does not assume these capabilities are
missing or assign their implementation to bipp without review. Geo field mapping
should likewise start from existing map support.

Security validation should focus on the integration: identity propagation,
enforcement of access policies, runtime operating permissions and coverage of
existing controls. Details such as provisioning protocols, masking and compliance
scope remain questions where the public pages do not establish the needed
contract. Customer-environment hosting alone does not settle those questions.
