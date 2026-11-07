# Royal Logistics & Supplies — customer workspace implementation contract

**Status:** Proposed customer-specific implementation contract; not a live customer tenant or production configuration.  
**Target:** CMHL Royal Logistics and Supplies Co. Ltd, Tanzania  
**Public reference:** https://royal.co.tz/  
**Engineering baseline:** WILSY EOS My Work exact-head certification `5f07d4fc152f184eea9ba09bf2296466d22666a1`  
**Date:** 2026-11-07

## 1. Customer facts and evidence boundary

Royal's public website describes the company as formed in 2019 and incorporated in Tanzania in 2021. Its stated business lines are used motor vehicle imports, auto-parts importation, agri-business and general supplies. The site describes used spare parts sourced from Japan on a wholesale basis. Its public team listing identifies responsibilities for management, vehicle and clearance, spare parts (including a Dodoma branch), sales and operations, and agri-business.

These are public business descriptions, not verified customer operational data. This contract does not assert Royal's current inventory, shipment counts, revenue, supplier balances, customer records, customs status, branch addresses, staff permissions or active contracts. No real customer data, credentials, or live integrations are included.

## 2. Product objective

Deliver a daily-use operating workspace in which each Royal employee sees the work their authenticated business capacity is allowed to see, performs source-owned commands, and can trace every consequential change to its actor, evidence and timestamp.

The workspace is an operational system, not a KPI mock-up. It must never fill missing source data with sample values, derive business authority from a browser role, or turn an aggregate dashboard into a command authority.

## 3. Proposed workspace navigation

The tenant's final module list must come from its authenticated EOS-issued module manifest and active product entitlements. The following is the proposed Royal information architecture, not an entitlement grant:

- **My Work:** cross-source projection of independently authorized assignments and follow-ups.
- **Vehicle Imports:** vehicle procurement/import cases, supplier documents, shipment milestones, clearance evidence, local delivery and customer handover.
- **Auto Parts:** wholesale catalogue, supplier purchasing, inbound consignments, branch/warehouse stock, reservations and sales fulfilment.
- **Agri-Business:** supplier and product records, purchase commitments, inbound stock, customer orders and delivery.
- **General Supplies:** quotation requests, procurement, goods receipt, stock allocation and delivery.
- **Customers & Suppliers:** party records and relationship activity, subject to independently authorized CRM capabilities.
- **Finance & Collections:** invoices, receipts, reconciliations and aging from the authoritative finance services; no dashboard-side balance mutation.
- **Management & Reports:** read-only cross-domain reporting with source, as-of time, currency and completeness labels.

A module must be hidden or unavailable unless EOS issues the corresponding tenant-bound entitlement and the current principal has the independent permission to enter it. A public website description does not activate a product.

## 4. First implementation slice: vehicle import case lifecycle

Vehicle Imports is the first proposed vertical slice because it is a clearly stated core service and the public website has a dedicated vehicle-importation service page.

### Case stages

1. **Enquiry and customer instruction** — capture the customer's request, target vehicle requirements, agreed commercial terms and responsible operator.
2. **Sourcing and supplier commitment** — record supplier, source-market details, quotation, purchase approval and evidence of the commitment.
3. **Vehicle identity and acquisition** — capture vehicle identifiers and source documents; validate uniqueness and record discrepancies for review.
4. **Shipment preparation and transit** — record shipment reference, origin, carrier/forwarder, planned dates and source-backed milestone updates.
5. **Arrival and customs clearance** — track required documents, assigned clearance responsibility, submitted evidence, assessments and outstanding blockers. A status must not imply customs approval without authoritative evidence.
6. **Local movement and receipt** — record custody transfer, inspection, condition discrepancies, location and receipt evidence.
7. **Customer delivery and handover** — record delivery appointment, customer acceptance, handover documents and unresolved exceptions.
8. **Closure and aftercare** — close only when required evidence and financial/customer obligations have been reconciled by their owning services.

These are proposed WILSY workflow stages. They are not a claim that Royal currently uses these exact stages or that WILSY has customs-authority integration.

### Core records

- Import case: stable ID, tenant ID, customer reference, responsible capacity, lifecycle state, created/updated timestamps and revision.
- Vehicle identity: VIN/chassis number, make, model, year, source-market attributes and identity verification state.
- Supplier commitment: supplier reference, quotation/contract reference, currency, amount, approval evidence and revision.
- Shipment: external shipment reference, origin/destination, carrier/forwarder references, planned/actual milestone timestamps and source provenance.
- Clearance dossier: document references, fingerprints, submission/assessment evidence, responsible operator and explicit unresolved requirements.
- Receipt/inspection: receiving location, custody event, inspection result, discrepancy evidence and operator.
- Handover: customer acceptance evidence, delivery event, outstanding exception state and closure decision.

Do not store raw document contents in the work queue. Use the authoritative document/evidence service, stable references and cryptographic fingerprints. Sensitive customer and identity fields must be minimized and protected by the owning service.

## 5. Authority and data boundaries

- **Identity and access:** EOS global principal, active tenant membership, explicit business capacity, MFA and authenticated workspace session remain the only admission chain.
- **Tenant boundary:** tenant identity comes from authenticated server context. A browser-supplied tenant ID or header cannot switch scope.
- **Work projection:** My Work may aggregate only independently authorized source projections. It does not own cases, inventory, financial balances or completion authority.
- **Vehicle import domain:** owns import-case lifecycle, revisions, allowed transitions, assignments and case audit records.
- **Documents and evidence:** the evidence service owns document persistence, integrity verification, access and retention. A text reference supplied by a user is not proof that evidence is valid.
- **Commercial authority:** quotes, purchase commitments and approvals require explicit permissions and approval thresholds from server-side policy. A job title or dashboard tile is not authority.
- **Inventory:** stock-on-hand changes only through recorded receipts, transfers, reservations, sales, returns and approved adjustments in the inventory-owning service.
- **Finance:** invoices, payments, receipts, settlement and reconciliation remain with their authoritative financial services. A vehicle case cannot mark an invoice paid by changing its own status.
- **External customs/carrier data:** integration is read/verified evidence with provenance. No simulated carrier event or inferred customs clearance may be presented as a confirmed external fact.

Every command must re-authorize at execution time, validate the expected revision, enforce the state transition, persist its audit evidence atomically with the domain mutation, and support safe retry semantics. Failed or unavailable authorization/evidence providers fail closed.

## 6. Role and separation-of-duties model

Proposed capacity-specific responsibilities, to be configured only after Royal confirms its operating model:

- Managing Director: oversight and explicitly delegated high-value approvals; no implicit ability to perform every specialist action.
- Vehicle and Clearance: assigned vehicle import cases, shipment and clearance evidence, exception handling.
- Sales and Operations: customer instructions, quotations within delegated limits, delivery coordination and customer communications.
- Spare Parts: wholesale enquiries, purchasing/receiving, branch stock and fulfilment within assigned locations.
- Agri-Business: supplier commitments, agricultural goods receipt, orders and delivery.
- Finance: invoice, receipt and reconciliation actions only through the finance service.
- Auditor/Read-only: source-scoped read access and evidence export where explicitly authorized; no mutation commands.

Maker-checker controls must be enforced server-side for configured thresholds and sensitive transitions. No user may approve their own transaction where policy requires independent approval. The above roles are a proposed mapping, not grants to named individuals.

## 7. Delivery sequence

1. Confirm Royal's actual operating model, branches, staff capacities, approval thresholds, currencies, documents and exception paths.
2. Provision a non-production tenant and configure verified legal identity, branding, locale/time zone and module entitlements through existing tenant administration and EOS controls.
3. Implement the Vehicle Imports domain registry, schemas, lifecycle transition service, assignment policy, audit events and idempotent commands.
4. Add real replica-set integration tests for tenant isolation, role/capacity admission, transition/revision races, audit atomicity, evidence integrity, retry/replay and provider outages.
5. Add authenticated browser journeys for each proposed capacity, including denied cross-capacity and cross-tenant access.
6. Integrate My Work as a projection only after the import domain has its independently authorized read model and command routes.
7. Add Auto Parts inventory and procurement only after inventory movement, branch/location and financial boundaries are separately designed and certified.
8. Add external carrier/customs connectors only with verified provider contracts, credentials, provenance, failure handling and operational monitoring.
9. Conduct customer acceptance testing with Royal before any production tenant activation or data migration.

## 8. Acceptance gates

- No sample or fabricated operational figures appear in any live tenant view.
- Every visible record is tenant-bound and principal/capacity-authorized at read time.
- Unauthorized source denial does not disclose record existence; provider outages are not rendered as empty queues.
- Every command checks current authorization and expected revision at execution time.
- State changes and audit/outbox evidence are atomic under the documented transaction contract.
- Retries are idempotent; replay, concurrency and stale-revision cases are tested.
- Clearance, receipt, delivery and financial states require their own authoritative evidence.
- Cross-tenant, cross-branch and cross-capacity negative tests pass on a real Mongo replica set.
- Authenticated browser tests prove daily-use flows at desktop and narrow viewport sizes.
- No production activation until customer acceptance, security review, provider binding and deployment gates are independently green.

## 9. Explicit non-goals for this slice

- No scraping or importing Royal customer, employee, supplier or shipment data from the public website.
- No claims about live Royal performance, stock, revenue, shipment counts or customer balances.
- No automated customs declarations, tax calculations or regulatory decisions without validated jurisdictional rules and authorized integrations.
- No replacement of accounting, payment, customs, carrier or document authorities by a dashboard.
- No production tenant creation, entitlement grant, external integration or deployment under this contract.
