# Product scope

Nodex Studio proposes an authoring and publishing layer on top of bipp. The
[founder proposal](00-executive-summary.md) describes the customer workflow,
expected benefits and pilot. This appendix records the scope for integration
planning; design statements describe intended behavior, not verified shipping
capabilities.

## Scope

The proposal covers prompt and visual dashboard authoring, versioned component
publishing, site-specific data bindings and query execution in the customer's
environment. It relies on reviewed semantic models and enforced access controls.
Compatibility with bippDash and the embedded SDK needs an integration review.

Existing bipp capabilities should be reused where their interfaces permit it.
Alerts, scheduled delivery, maps and annotations in this specification describe
how those experiences could work with published components; they do not imply
that bipp lacks them today. See the [platform baseline](00b-platform.md).

## Boundaries

The pilot uses structured data already available through bipp models. Document
search, ingestion pipelines and modifications to business records are outside
its scope. User commentary may be stored separately from business records.
Temporary query caching stays in the customer's environment and is disposable.

The initial widget set is bounded. Uncovered customer needs require a supported
extension to the dashboard schema and renderer. Whether that covers the chosen
workflow should be demonstrated during the pilot.

## Delivery decisions

Customer-side runtime operation, managed support access and integration ownership
must be agreed before deployment. The product's placement within or alongside
bipp is also open. Library selection, package mechanics and detailed protocol
design can follow agreement on the workflow and integration boundaries.
