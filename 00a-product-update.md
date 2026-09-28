# 00 — Product update

Before you can say where AI adds value, you have to say which layer of the
enterprise you are talking about. Most conversations about AI in analytics fail
because the two sides are discussing different layers and neither says so.

## Three layers

**System of Record.** The authoritative source of truth for a data type. CRM for
customers, ERP for financials, HR systems for employees. Structured, governed,
and the place a disagreement is finally settled.

**System of Content.** Where unstructured content lives — documents, emails,
reports, contracts. Usually the larger half of what an organization knows, and
much harder to query or act on.

**System of Intelligence.** The analytics and AI layer sitting on top of both. It
does not store the data. It makes the data useful.

Most organizations do not have all three working well at once. Knowing where an
organization actually sits is what makes the AI conversation meaningful rather
than aspirational.

## AI maturity

A useful ladder, because it converts a vague question ("are you ready for AI?")
into a specific one:

| | State | What it looks like from the inside |
|---|---|---|
| **1** | Fragmented | Records sit in silos. Answers are assembled by hand. Two teams' numbers disagree and nobody can say which is right. |
| **2** | Consolidated | The data is in one warehouse. Queries are possible. Definitions are still argued per team. |
| **3** | Defined | Metrics are declared once and reviewed. A number means one thing across the organization. |
| **4** | Distributed | Answers reach the point of decision, inside the tools people already work in. |
| **5** | Generative | Anyone can pose a new question and get a trustworthy answer without the data team as a bottleneck. |

**Nodex Studio requires level 3 and delivers levels 4 and 5.**

That sentence is the qualification criterion, and it should be used as one. An
organization at level 1 or 2 is not ready, and selling to them produces a failed
deployment rather than a customer. The question that qualifies a prospect is not
whether they have data. It is whether they have agreed definitions.

## Where Nodex Studio sits

Nodex Studio is a System of Intelligence, and the architecture in the rest of
this document is what makes that a description rather than a claim.

**It is defined by what it refuses to store.** Most analytics products drift into
becoming a second system of record: they ingest, extract, cache, and within a
year the organization has a subtly different duplicate of its own numbers, and a
new argument about which one is right. Nodex Studio is forbidden from doing this.
Warehouse credentials never leave the customer's network (I8), queries run
in-database with no extracts, and no data path crosses into Nodex cloud at all
([Security](08-security.md)). The data stays where the organization already
governs it.

**It speaks the organization's own definitions.** Nodex Studio binds to the
System of Record through the modeling layer, so it references metrics that were
declared once and reviewed — never raw tables it interpreted for itself. A System
of Intelligence that invents its own definition of revenue does not clarify an
organization, it fragments it further. This is also why level 3 is a
prerequisite: the semantic layer is the contract between the two systems.

**It delivers into the systems people already work in.** This is the difference
between reporting on an organization and changing how it operates. A dashboard
behind its own login is a destination, and destinations get visited on Mondays.
The six delivery modes ([Distribution](05-distribution.md)) exist so an answer
can sit inside the application where the decision is actually made — the internal
ops tool, the account page, the planning app — as a component the customer's own
developers import. Insight that has to be travelled to is insight that mostly
does not get used.

**It lowers the cost of asking.** An organization reaches level 5 when posing a
new question stops requiring a specialist. Prompt authoring does that, and
exploration is open to anyone with access to the models — no developer in the
loop ([Explore and publish](03-studio.md#explore-and-publish)). Schema-bounded
generation ([ADR-0002](adr/0002-schema-bounded-generation.md)) is what keeps it
trustworthy: a non-specialist cannot author a wrong join or an unbounded scan,
because the schema does not contain one. The guardrail is structural, not
advisory, which is why self-serve here does not mean unreliable.

## What we do not do yet

Nodex Studio operates on the System of Record. The System of Content — contracts,
emails, reports, the unstructured majority of what an organization knows — is out
of scope today. Nothing in the current architecture reads a document.

This should be said plainly in customer conversations rather than left to be
discovered. The credible version of this positioning names its boundary; the
alternative invites the one question we would have to dodge. It is also the most
obvious direction of expansion, and the manifest and modeling-layer design
([Data plane](06-data-plane.md)) does not preclude a second source type later.

## How to use this

When the conversation is about the product, the claim is narrow and checkable:
Nodex Studio is the intelligence layer over a customer's existing system of
record, it deploys into their own environment, and it puts answers inside the
applications their people already use.

When the conversation is about the category, the argument is that the analytics
market has largely been building destinations, and that the value of a System of
Intelligence is realised at the point of decision rather than in a reporting
tool. That argument is credible for us specifically because the distribution
architecture already exists (I7, I9) — it is a property of the system, not a
roadmap item.

The thing worth not saying: that this is a better dashboard product. It is not
positioned against dashboard tools, and winning that comparison would be winning
the wrong argument.
