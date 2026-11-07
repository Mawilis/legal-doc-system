# ADR-002: Universal business signup and integrated WILSY OS onboarding

**Status:** Proposed; implementation blocked on independently governed tenant-owner evidence authority  
**Date:** 2026-11-07  
**Depends on:** ADR-001 reusable industry platform and declarative packs

## Decision

WILSY OS is one integrated operating system that any lawful business or professional organisation can join. Signup is not restricted to a closed industry enum, a fixed product bundle, or a customer-specific software contract.

The platform uses one universal business-genesis and onboarding journey. Industry packs and tenant configuration tailor the workspace after the business identity and its authorised owner have been established. A business may select a suggested profile (for example law firm, importer/exporter, medical practice, dentist, clinic, auto-parts wholesaler, mechanic, vehicle dealership, agriculture, general trading, or other) without that selection becoming an authorization fact or a hard product boundary.

"All or nothing" means one coherent operating experience and one platform relationship. It does not mean every capability is automatically entitled, every user is an administrator, or every regulated action is available without the required authority. Capabilities remain independently owned and independently authorized.

## Customer promise

A customer should be able to:
1. Discover WILSY OS and start signup without a sales call or manual document exchange.
2. Create a global principal account and verify control of the contact channel.
3. Start a business workspace with the minimum information needed to identify the proposed organisation and jurisdiction.
4. Choose a suggested business profile or describe an unlisted business in plain language.
5. Save and resume onboarding without losing progress.
6. Receive a clear workspace setup checklist and begin using permitted general capabilities as soon as the relevant genesis and entitlement gates are satisfied.
7. Add branches, staff, workflow preferences and integrations progressively, without repeating the original signup.
8. See one integrated navigation and one My Work experience, with unavailable or unentitled capabilities explained clearly rather than represented as broken or empty modules.

No onboarding screen may promise a business is legally verified, an owner is established, a regulated professional is licensed, a subscription is active, or a capability is enabled unless the corresponding authoritative service confirms that state.

## Universal identity model

Keep these concepts distinct:
- **Global principal:** the human identity that authenticates to WILSY OS.
- **Proposed business:** a draft onboarding object; it is not yet a tenant and grants no access.
- **Legal entity / organisation evidence:** verified external evidence binding the organisation to its jurisdiction-specific identifier and legal status where applicable.
- **Tenant:** the canonical isolated customer boundary created only by governed genesis.
- **Tenant owner:** a principal whose authority to bind the exact legal entity to the exact tenant is established by the configured independent ownership/signatory verifier.
- **Membership and capacity:** separately issued and current authorization facts. An onboarding selection, email address, invitation, uploaded document, or tenant header cannot create these facts.
- **Industry pack:** a versioned, declarative composition of reusable capabilities and workflow templates. It is not a tenant, entitlement, role, permission, or source of truth.
- **Entitlement:** commercial authority issued only through the canonical subscription and entitlement lifecycle.
- **Tenant configuration:** branch, locale, terminology, workflow choices, approval thresholds, staff bindings and verified integration settings. Configuration cannot grant authority.

## Progressive onboarding journey

### Stage 0 — Discover
- Public product explanation and transparent plan/capability catalogue.
- No account or industry category required to explore.
- Support a broad, searchable industry suggestion list plus "Other / describe my business".
- Do not infer or assign regulated status from a label.

### Stage 1 — Principal account
- Create or authenticate a global principal using the canonical identity service.
- Verify email/phone challenge through the configured provider; protect against enumeration, replay and abuse.
- MFA enrollment and recovery follow the principal-scoped identity policy.
- No tenant is created by this stage.

### Stage 2 — Business draft
- Capture only business display name, country/jurisdiction, organisation type (including individual professional / sole proprietor where lawful), and contact details needed for the next step.
- Industry is an open vocabulary with optional suggested categories and a free-text description. Store the selected taxonomy version and original description.
- Support multiple business profiles per principal and multiple authorised principals per business, subject to governed ownership evidence.
- Autosave draft with idempotency and expiry/recovery controls. Draft is not an active tenant.

### Stage 3 — Authority and identity verification
- Resolve the appropriate authoritative legal-entity registry or signatory source for the selected jurisdiction and entity type.
- Verify exact entity identifier, status, source provenance, freshness, issuer trust, revocation/currentness, and the principal's exact authority to bind that entity.
- For sole practitioners and entities without a corporate registry record, use a separately governed evidence route appropriate to that legal form; do not silently weaken verification.
- Uploaded files and self-attestation are evidence candidates only, never verification by themselves.
- Where automated verification is unavailable, create a clearly labelled pending case for governed review. Do not create an active tenant or grant owner authority while unresolved.
- Prevent duplicate tenant genesis for the same canonical entity and handle conflicting claims through an adjudication process.

### Stage 4 — Governed tenant genesis
- Use one canonical orchestration command, not legacy UI or Node-side provisioning.
- In a caller-owned Mongo replica-set transaction, atomically persist tenant identity, verified ownership evidence reference, initial owner membership, required authentication/business-role assignments, genesis event, audit/outbox evidence, and idempotency result.
- Revalidate evidence currentness and conflicts inside the command boundary.
- No partial tenant, orphaned owner, or owner role without the corresponding verified evidence.
- Tenant creation remains unavailable until the independent issuer/verifier and recovery authority are configured and certified.

### Stage 5 — First-use workspace
- Resolve the server-issued capability manifest from canonical product catalogue and active entitlements.
- Render one integrated WILSY OS workspace and navigation. Show capability status (available, setup required, not included, pending verification) accurately.
- Provide a guided checklist, not a mandatory multi-page questionnaire.
- Start with general, non-regulated capabilities that are actually authorized and available.
- Keep My Work as a projection of source-owned queues; every action returns to the owning service for fresh authorization.

### Stage 6 — Progressive business setup
- Add branches/locations, staff invitations, roles/capacities, approval policies, document templates, integrations and industry workflows when needed.
- Each action is an independently authorized command, with maker-checker and evidence where required.
- Allow later changes to industry profile and pack version without changing tenant identity or rewriting historical records.
- Preserve configuration history and effective dates; migration must be explicit and reversible where safe.

## Universal capability architecture

The integrated workspace is composed from:
1. **EOS foundation:** principal identity, tenant isolation, IAM, membership/capacity, MFA, entitlements, audit, evidence, notifications, workflow orchestration and My Work.
2. **Reusable capabilities:** CRM, Legal Operations, Billing, POS, Operations, Intelligence, HR, procurement, inventory, logistics, document/evidence, scheduling, finance integrations and reporting. Each capability owns its data, policy and commands.
3. **Industry packs:** declarative workflow compositions (legal practice, healthcare practice, dental practice, vehicle trade/imports, wholesale parts, mechanics/workshops, vehicle dealerships, export/import, agriculture and general trading).
4. **Tenant configuration:** jurisdiction, entity form, branches, terminology, enabled workflows, approval thresholds, staff assignments and verified integrations.

The existing canonical product catalogue remains the authority for sellable products and entitlements. An industry pack must not add a product, activate a subscription, or grant capability access. A capability may be shared by multiple packs and customers.

## Industry coverage without a closed-world enum

Initial reference profiles should include:
- Law firms and legal practices.
- Private doctors, dentists, medical practices and clinics.
- Importers, exporters, customs/logistics operators and freight businesses.
- Auto-parts retailers, wholesalers and distributors.
- Mechanics, repair workshops and service centres.
- Vehicle dealers and used-vehicle importers.
- Agriculture, general supplies, wholesale, retail and professional services.
- Other / describe your business.

This list is discovery assistance, not a list of supported legal categories. Unknown business descriptions must be accepted into a neutral profile and mapped to capabilities through a governed pack publication process. The system must never reject signup solely because a business model is not yet represented by a pack.

Regulated domains require jurisdiction-aware controls. For example, a clinic profile does not establish practitioner registration, clinical privileges, patient consent, prescribing authority or access to health records. A law-firm profile does not establish Legal Partner capacity or matter access. These are separately verified and authorized in their source systems.

## "All or nothing" product experience

- One account and one canonical tenant per governed business identity.
- One workspace shell, navigation, search, notifications and My Work.
- One coherent commercial relationship and transparent capability catalogue.
- Shared customer, supplier, document and location references where ownership contracts permit.
- Cross-capability workflows orchestrate source-owned commands; they do not bypass them.
- A single customer support and account-management journey.
- No fragmented customer-specific forks.

The following remain deliberately separate behind the unified experience: capability data stores, authorization decisions, financial ledgers, regulated records, source transactions and audit boundaries. A global dashboard must not imply a globally atomic snapshot across independent services.

## Security, privacy and governance invariants

- Tenant scope is derived from authenticated current membership/capacity; browser-provided tenant headers are never membership evidence.
- Signup and onboarding endpoints are rate-limited, idempotent, abuse-resistant and safe against account/entity enumeration.
- No principal may self-assign tenant ownership, professional status, role, capacity, permission, approval limit or entitlement.
- Ownership, transfer and recovery use independent issuer trust and conflict adjudication.
- Verification outages fail closed for authority creation; they are not treated as successful or as proof of nonexistence.
- No user sees another tenant's draft, identity evidence, staff, financial or operational records.
- Every genesis and privileged onboarding mutation has correlated audit/outbox evidence in the same transaction as the state mutation.
- Evidence references are provenance-bound and currentness checked; fingerprints alone do not prove authenticity.
- Medical, legal, financial and other regulated records remain in their governed source capability with purpose-limited access.
- No production tenant genesis before issuer/verifier, recovery, replica-set, replay, concurrency, cross-tenant and browser certification.

## Current repository gap and implementation gate

The canonical tenant router currently denies tenant creation. The Issue #300 ownership-evidence review records that no independent issuer/verifier or recovery authority is configured, and that the HTTP POST route is unavailable. This is the correct containment state.

Legacy onboarding artifacts are not canonical authority:
- The old sovereign wizard has a closed industry dropdown and posts to a legacy `/api/v1/onboarding/initialize` endpoint.
- The simple tenant onboarding form simulates success in the browser with a random identifier.
- The older SaaS facade calls a tenant creation method that is absent from the current canonical registry.
These must not be reactivated as a shortcut.

### Required implementation sequence

1. Governance selects jurisdiction-specific legal-entity/signatory evidence issuers, trust roots, verifier contracts, revocation/currentness sources and independent recovery/adjudication authority.
2. Implement universal principal signup/draft onboarding without tenant-creation authority.
3. Implement ownership evidence domain, verifier adapter, immutable evidence registry and conflict/currentness projection.
4. Implement one atomic tenant-genesis orchestration transaction with idempotency, audit/outbox and canonical IAM assignment.
5. Implement a universal onboarding API and progressive UI; remove hard-coded industry restrictions and simulated tenant creation.
6. Connect the server-issued manifest and integrated workspace shell; industry packs configure workflows but never grant entitlements.
7. Certify replica-set atomicity, duplicate/replay/concurrency, evidence forgery/revocation, wrong entity/principal/tenant, outage fail-closed, recovery, cross-tenant isolation, accessibility, mobile and authenticated browser journeys.
8. Prove onboarding with materially different businesses (Royal vehicle imports, law firm, clinic/dental practice, auto-parts business, mechanic/workshop, exporter and an unlisted "Other" business) without customer-specific code forks.

## Acceptance criteria

- Any lawful business model can start signup; unknown industry never blocks draft creation.
- The user can complete principal signup and save a business draft without tenant authority.
- A tenant is created only after independent ownership evidence is verified and atomically bound to the exact principal and entity.
- Duplicate/replayed genesis produces one canonical tenant and one durable result.
- Failed verification, issuer outage, stale/revoked evidence, conflicts and transaction failures create no partial tenant or owner assignment.
- A customer sees one integrated workspace with honest capability status.
- Different industry packs can compose shared capabilities without changing IAM or commercial authority.
- A second customer in the same industry and a customer in an unlisted industry can onboard through configuration / neutral profile, not code forks.
- Regulated source capabilities continue to enforce their own professional, record, consent and workflow authority.
- The full browser journey and real replica-set evidence are green on the exact commit before the onboarding programme is declared complete.

## Non-goals

- No blanket activation of every paid product or regulated capability.
- No automatic tenant creation from an email address, form submission, uploaded document or browser action.
- No generic workflow scripting that can execute arbitrary code or grant permissions.
- No new product catalogue item for every industry.
- No production tenant creation or deployment in this architecture-only change.
