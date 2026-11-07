# ADR-001: Reusable WILSY Industry Platform and Configurable Business Packs

- **Status:** Proposed architecture decision for implementation
- **Date:** 2026-11-07
- **Decision owner:** WILSY EOS platform architecture
- **First proving customer:** CMHL Royal Logistics and Supplies Co. Ltd (Tanzania)
- **Parent customer discovery:** [Royal workspace contract](./royal-logistics-tanzania-workspace-contract-2026-11-07.md)

## Context

WILSY must serve businesses with materially different operating models without creating a bespoke codebase, database model, API surface or customer-specific release for each new tenant. Royal is a useful first proving case because its public business description spans vehicle imports, wholesale auto parts, agri-business and general supplies.

A single generic task engine is not enough: vehicle identity, import clearance evidence, stock movements and customer fulfilment have different domain invariants. Conversely, hard-coding each customer's screens and workflows creates an unmaintainable forked product.

The existing platform already provides important reusable foundations: global principal and tenant membership, explicit business capacity and permissions, tenant product entitlements and module manifest, source-owned Operations/Intelligence queues, My Work projections, POS location assignment, CRM work and audit/evidence authorities. These must be composed rather than replaced.

## Decision

Adopt a layered, capability-oriented platform with declarative industry packs and tenant configuration. Do not create one software contract per customer.

### Layer 1 — Universal EOS foundation

Shared services and invariants used by every industry:

- global principal, tenant membership, explicit capacity, MFA and session currentness;
- tenant isolation and authorization decision evidence;
- product catalogue, entitlement lifecycle and server-issued module manifest;
- revision-guarded domain commands, idempotency, transactions and append-only audit/outbox;
- document/evidence references and cryptographic integrity;
- My Work as an authorized projection, never a central command authority;
- notifications, reporting provenance, integration credential custody and observability.

### Layer 2 — Reusable business capabilities

Domain capabilities that can be reused by multiple industry packs, each with a single owning service and source of truth:

- parties / customer and supplier relationship;
- product and service catalogue;
- procurement and supplier commitments;
- inventory ledger, warehouse, branch and location assignment;
- sales, quotations, orders and fulfilment;
- shipment and logistics milestones;
- finance read projections and evidence-backed receivables/payables;
- documents, approvals, workflow and exception management.

A capability is not merely a UI component. It includes its domain model, persistence registry, indexes, authorization contract, entitlement boundary where applicable, commands, read model, audit behavior, migrations and test certificates.

### Layer 3 — Industry packs

An industry pack composes capabilities and provides default workflow templates, field profiles, vocabulary, role-capacity suggestions, document checklists, reports and integration adapter declarations.

Initial pack candidates:

- Vehicle Trade & Imports
- Wholesale Distribution & Auto Parts
- Agricultural Trading & Produce Supply
- General Wholesale & Procurement
- Professional Services
- Retail & Point of Sale

Packs are versioned and declarative. A pack may reference known capability IDs and workflow definitions, but it cannot define executable code, bypass IAM, create permissions, activate entitlements, set a user's capacity, or change a capability's source of truth.

### Layer 4 — Tenant configuration

A tenant selects entitled capabilities and pack versions, then configures:

- legal identity, locale, timezone and currency policy;
- branches, warehouses and operating locations;
- terminology, workflow options and required evidence templates;
- staff-to-capacity bindings through the existing IAM authority;
- approval thresholds and maker-checker rules through server-owned policy;
- external integrations using tenant-scoped, vaulted credentials and explicit provider verification.

Tenant configuration is data validated against schemas and policy. It is not a customer-specific code fork.

## Why this is the best option

| Option | Decision | Reason |
|---|---|---|
| Bespoke contract and code for every customer | Reject | Forks product, duplicates security fixes and raises cost of change |
| One generic ERP schema and universal CRUD | Reject | Erases domain invariants; encourages unsafe generic mutation and status fields |
| Industry-specific standalone products | Reject | Duplicates identity, billing, evidence, audit, reporting and operations foundations |
| Universal platform + reusable capabilities + declarative industry packs + tenant config | **Adopt** | Reuses foundations while preserving domain-specific authority and evidence |

The key distinction: **configure composition, never configure away authority.**

## Royal as the proving implementation

Royal is not a one-off "Royal module". It is the first tenant configuration of reusable capabilities and pack templates:

- Vehicle Imports pack: import case, vehicle identity, sourcing commitment, shipment, clearance dossier, receipt, inspection and customer handover.
- Wholesale Parts pack: supplier purchasing, SKU catalogue, branch stock, reservations, sales and fulfilment.
- Agricultural Trading pack: supplier lots, quality/grade evidence, procurement, stock and order fulfilment.
- General Supplies pack: quotation, purchase order, receipt, allocation and delivery.

The first vertical slice should prove Vehicle Imports end-to-end. The domain capability is reusable for any importer; Royal's terminology, branch setup, workflow options and staff assignments are tenant configuration.

## Authority model

- Pack metadata is not an authorization policy.
- Tenant pack selection does not activate a product entitlement.
- Product entitlement does not grant principal permission.
- A module manifest controls discoverability only; each API command independently checks current principal, membership, capacity, permission, entitlement and relevant scope.
- Branch and warehouse IDs are selectors, not authority. Server-side assignment resolution is mandatory for each read and command.
- My Work projects authorized items from source services. Completing a projected item calls the owning domain command and re-authorizes there.
- External carrier/customs observations remain untrusted until verified against configured provider evidence and provenance.
- Financial balances, payment execution and settlement remain with their existing authoritative services.

## Versioning and extension rules

- Each pack has an immutable ID, semantic version, schema version, capability dependency list and compatibility declaration.
- A pack upgrade is an explicit tenant configuration revision with validation and rollback planning.
- Breaking capability changes require a migration plan and compatibility tests; never silently reinterpret historical records.
- Customer-specific exceptions should first be modeled as validated configuration or extension points. If an exception changes core domain invariants, it belongs in a separately reviewed capability extension—not arbitrary tenant scripting.
- No tenant-supplied executable code, expressions, dynamic imports or arbitrary webhook handlers are permitted in pack definitions.

## Delivery sequence

1. Establish a generic industry-pack schema and static validator; schema validation is not entitlement or IAM authority.
2. Define capability catalogue IDs and dependency compatibility rules.
3. Certify Vehicle Imports as a source-owned domain capability: registry, lifecycle, revision guards, idempotency, evidence, audit/outbox and transaction contract.
4. Add authenticated route-level read and command certification using live IAM and real Mongo replica set.
5. Add branch/location scope as a server-resolved authority, reusing the POS assignment pattern where semantically appropriate rather than copying POS financial logic.
6. Add a My Work adapter that exposes assigned import work without owning case lifecycle.
7. Instantiate Royal's non-production tenant configuration only after the customer confirms branches, capacities, workflows, thresholds, documents and integrations.
8. Add Parts/Inventory by implementing reusable inventory ledger and procurement capabilities; do not add stock quantity CRUD.
9. Certify a second, materially different tenant configuration using the same capabilities and pack schema. This is the proof that the architecture scales without bespoke code.

## Acceptance criteria

- A second tenant can adopt the Vehicle Imports pack without a customer-specific code change.
- A tenant may enable only products it is actually entitled to; pack metadata cannot activate products.
- Every route resolves tenant and principal context server-side and rejects forged tenant/branch selectors.
- Branch/warehouse access is independently checked for each command and query.
- Every lifecycle mutation validates expected revision and allowed transition.
- Domain mutation, audit evidence and outbox event share the documented atomic transaction boundary.
- Idempotency and concurrent update behavior are certified on a real replica set.
- Evidence-required transitions reject missing, malformed, foreign-tenant or unverifiable evidence.
- My Work source outage is distinguishable from an empty queue; source command re-authorizes independently.
- A pack cannot add permissions, change IAM role grants, execute arbitrary code, or bypass entitlements.
- A second tenant configuration passes the same reusable certification suite.

## Consequences

This adds a small platform layer for pack schema, compatibility and configuration governance. It avoids a customer-by-customer codebase while preserving independently owned business domains. The up-front discipline is intentional: a workflow is reusable only after its authority, evidence, persistence and lifecycle semantics are defined.
