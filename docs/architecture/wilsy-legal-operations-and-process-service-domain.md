# WILSY OS — LEGAL OPERATIONS & PROCESS SERVICE DOMAIN

Version: v1.0.0-LEGAL-OPERATIONS-PROCESS-SERVICE-CONSTITUTION
Authority: Wilsy OS Core Governance
Source: `Software Notes.docx` (authoritative discovery input)
Status: domain constitution; implementation remains staged

## Sovereign plane

The Legal Operations & Process Service Plane owns operational legal-service
truth for law firms, attorneys, clients, matters, instructions, documents,
sheriffs, districts, deputies, custody, service, returns, tariffs, quotations,
courier instructions and notifications. It does not own financial execution,
settlement, or general-ledger truth. Kennel EOS remains the exclusive financial
execution authority.

## Canonical entities and lifecycle

Canonical entities are `LegalInstruction`, `CaseMatter`, `ProcessDocument`,
`SheriffOffice`, `District`, `Deputy`, `ServiceAddress`, `DocumentReceipt`,
`DocumentCustodyEvent`, `ServiceAttempt`, `ServiceExecution`, `ReturnOfService`,
`TariffAssessment`, `FeeLine`, `Quotation`, `CourierInstruction`, and
`Notification`. Law firms and attorneys are tenant customers; client and matter
identity must not be conflated with tenant identity.

The lifecycle is:

`INSTRUCTION != DOCUMENT REGISTERED != DOCUMENT RECEIVED != ALLOCATED TO DEPUTY != SERVICE ATTEMPTED != SERVICE COMPLETED != RETURN GENERATED != INVOICE GENERATED != PAYMENT EXECUTED != SETTLED`.

`DOCUMENT REGISTERED != DOCUMENT IN OFFICE != DOCUMENT WITH DEPUTY != DOCUMENT RETURNED TO CLIENT`.
`ATTEMPT != SERVICE`; `SERVICE COMPLETED != RETURN GENERATED`; `RETURN GENERATED != TAX INVOICE`;
`INVOICE GENERATED != PAYMENT EXECUTED`; `PAYMENT EXECUTED != SETTLED`.

Registration records document type, client/account type, client reference,
case number, court, plaintiff/applicant sequence, defendant/respondent,
service address, service type, assigned sheriff/deputy, notes, annexures and
uploaded material. Registration is not receipt or service proof.

## Custody, mobile and evidence

Custody is an append-only event journal: registered, awaiting receipt, received
into office, signed out, attempted, served/non-served, returned, sent,
couriered, collected, or posted. Each event records identity, tenant, document,
from/to locations, actor, timestamp, method and evidence. Current location is a
projection, never the sole mutable truth.

Deputy mobile workflows may navigate, begin/end service, capture lawful
geospatial and person-served evidence, outcome, notes and synchronization data.
Offline operation requires device/deputy identity, tenant/district scope,
ordered event journal and conflict-safe sync. Mobile cannot create payment or
settlement truth.

Multiple `ServiceAttempt` records precede one service execution or final
non-service result. A `ReturnOfService` is generated only from certified facts
and remains legal/process evidence, not an invoice or payment.

## Billing, tariffs and quotations

Only completed, return-eligible work enters billing. Registered or unserved work
remains operationally visible but must not appear as a zero-value billed item.
The source scenario (100 registered, 20 completed) therefore yields 20
invoice-bearing items and 80 operationally visible non-billed items.

Tariff calculation is future, versioned and jurisdiction-aware: magistrates'
court, High Court, district/family, auction, service, return, attempts,
travel/kilometres and expenses. `TariffSchedule`, `TariffVersion`, effective
date, court/jurisdiction, service type, fee code, quantity, unit amount,
travel rule, tax treatment and evidence basis are required; values are not
hard-coded here. `QUOTE != INSTRUCTION != INVOICE != PAYMENT`.

Invoice, tax invoice and file copy are distinct projections. Accounting truth
belongs to the billing/accounting plane.

## Attorney, sheriff and storefront journey

`Storefront -> signup -> tenant genesis -> firm -> attorney/member -> authority -> client -> instruction -> registration/upload -> sheriff/deputy -> service -> return -> invoice -> payment -> settlement evidence`.

District is an authority and scope dimension, not cosmetic UI. Queues cover
office receipt, deputy assignment, same-day/urgent work, attempts, returns,
distance and billing readiness. Search must support case number and client name.

## Integrations and authority boundaries

Courier, email, SMS, mapping and payment providers are adapters. Courier status
is external evidence, not legal completion. Payment UI/provider success is not
settlement; all provider execution routes through Kennel EOS. Notifications
announce return readiness and pickup without mutating canonical state.

`APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED`.
`SALE != PAYMENT`.
`OBSERVED FACT != DERIVED SIGNAL != AI INFERENCE != RECOMMENDATION != AUTHORIZATION != EXECUTION`.

## Migration and open questions

Discover existing routes and persistence before implementation; map canonical
owners, wire projections/evidence/observability, then clean duplicates only
after certification. Open questions from the notes requiring domain
confirmation include account creation boundaries, quotation/payment timing,
return-versus-tax-invoice presentation, jurisdiction tariff authority, COD
rules, and lawful geospatial retention.

## Sovereign EOF seal

Artifact: `wilsy-legal-operations-and-process-service-domain.md`
Version: `v1.0.0-LEGAL-OPERATIONS-PROCESS-SERVICE-CONSTITUTION`
Authority: Wilsy OS Core Governance
Financial authority: Kennel EOS exclusively
Compliance posture: technical-control-only; no independent legal-compliance claim
END OF WILSY OS SOVEREIGN ARTIFACT
