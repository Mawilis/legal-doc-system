# Issue #300 — Competitive architecture review and provider-neutral adapter plan

**Status:** ENGINEERING DESIGN; provider selection and institutional appointments remain unresolved  
**Date:** 2026-11-02

## Executive decision

Do not buy or integrate one identity-verification vendor as if it were the ownership authority. WILSY needs a source-of-truth and authority architecture, not a selfie/document-KYC feature. Keep five replaceable roles: (1) authoritative legal-entity source connector; (2) natural-person identity connector; (3) issuer authority verifier; (4) cryptographic custody/signing service; (5) independent recovery adjudicator.

Production composition must fail closed if any required role, trust-list source, revocation source or currentness check is absent or unavailable. An identity vendor can supply evidence; it cannot appoint itself as a legal ownership authority.

## Competitive landscape and implications

| Market/system | Demonstrated strength | Limitation for WILSY ownership | Engineering implication |
|---|---|---|---|
| South African CIPC Beneficial Ownership Register | Jurisdiction-specific BO filings, natural-person ownership/control relationships and supporting documents; access restricted to authorised users/accountable institutions | Filing data can have multiple versions and can be incomplete, changed or subject to further verification; CIPC warns against sole reliance | Build permissioned, source-centric connector with filing ID/version, retrieval time, source fingerprint, change detection and corroboration. A filing confirmation is not a legal opinion or conclusive owner proof. |
| Microsoft Entra Verified ID | Decoupled issuer/holder/verifier model, cryptographic credential verification and Key Vault-backed key provisioning | Credential authenticity does not establish legal entitlement to assert a specific South African ownership claim | Reuse role separation and key-vault isolation; retain independent issuer allow-list and legal-scope policy. |
| SAP Decentralized Identity Verification | REST issuance/verification, DID-resolved issuer keys and configured trust lists | DID resolution proves key association/integrity, not legal appointment, beneficial ownership or mandate sufficiency | Treat resolvable key metadata as one cryptographic input; separately verify institutional appointment, purpose, jurisdiction, status and revocation. |
| EU digital trust patterns / eIDAS | Explicit issuer, holder, verifier, data-source and trust-framework roles; source-centric, user-centric and issuer-centric patterns | Frameworks and trusted lists are jurisdiction- and purpose-specific | Use source-centric checks for current registry facts, holder-presented credentials for provenance/privacy, issuer trust lists for signature authority; never collapse them. |
| UK Digital Verification Services trust framework | Certification, role separation and defined orchestration/holder/identity-service outcomes | Certification is not a blanket legal determination of South African ownership | Borrow assurance, audit, role and lifecycle controls; do not treat overseas certification as South African legal authorization. |
| Entrust / HID / Thales / Persona / Trulioo / Sumsub and peers | Mature identity proofing, PKI, credential, biometric, orchestration or document verification capabilities | These are capability providers, not automatically independent statutory or institutional ownership/recovery authorities | Evaluate as replaceable components for local source access, assurance, audit, data residency, revocation, portability, incident response and contractual controls. No vendor is selected here. |

## Competitive differentiation target

WILSY should compete on complete legal-authority decision quality, not faster document scanning:
- South African registry-source freshness and filing lineage.
- Explicit separation of registered directors, beneficial owners, controllers, mandates and persons authorized to bind an entity.
- Multi-source corroboration and deterministic conflict handling.
- Portable issuer provenance without making the vendor the trust anchor.
- Non-exportable key custody, rotation/revocation and independent dual control.
- Independently adjudicated, contestable, time-bounded and auditable recovery.
- Exact tenant/entity/principal/operation binding, immutable history, replay resistance and atomic lifecycle changes.

## Provider-neutral contracts to implement

### A. Registry source connector
Input: exact jurisdiction, entity reference, source filing identifier and evaluated-at instant. Output: source-authenticated record reference, filing/version identifier, retrieval timestamp, source fingerprint, jurisdiction, legal form, status, relevant ownership/control attributes, effective date and source limitations. Preserve provenance; detect newer filings; handle multiple filings explicitly; never silently choose the most favorable record; distinguish unavailable from negative; enforce access entitlement; minimize personal data; invalidate evidence on correction/revocation.

### B. Identity proofing connector
Input: subject reference and purpose-limited challenge. Output: verified subject reference, method/assurance level, evidence reference/fingerprint, timestamp, validity/revocation status and verifier provenance. Do not store raw identity documents; bind to exact principal only through canonical identity linking; email, display name, JWT role or browser assertion is not identity proof.

### C. Issuer authority verifier
Input: signed institutional appointment, delegation, scope, jurisdiction, decision fingerprint and issuer key reference. Output: verified issuer authority only after independent signer/capacity/delegation verification, quorum/conflict checks, validity, trust-list membership and revocation. Issuer cannot appoint itself or approve its own trust root; issuer and recovery scopes remain separate.

### D. Key custody / signing adapter
Input: canonical payload digest, approved key reference/revision and operation purpose. Output: signature, algorithm, key ID/revision, signing receipt, timestamp and verifiable custody/audit reference. Require non-exportable private keys, payload/domain separation, exact audience and operation, no arbitrary signing endpoint, rotation, dual-control, compromise response and revocation. KMS/HSM selection is a security procurement decision, not an engineering guess.

### E. Recovery authority adapter
Input: exact tenant/entity/case, evidence set, current owner state, proposed successor, notices, objections, decision scope and evaluated-at instant. Output: signed, time-bounded adjudication tied to exact case and successor, independent authority identity, quorum, conflict/recusal evidence, appeal/objection disposition and revocation status. Recovery authority and trust root must be distinct from issuer; no support/tenant-admin fallback.

## Production composition gates

1. Separate deployment identities, endpoints, credentials, trust roots and audit streams for issuer, custody and recovery.
2. Verify institutional approval and delegated capacity independently of the provider being approved.
3. Pin adapter protocol versions and accepted signature algorithms; reject downgrade and unknown algorithms.
4. Verify revocation/currentness at evaluation time; no stale-cache positive decision on source outage.
5. Require exact cross-binding across tenant, legal entity, principal, operation, evidence, mandate, issuer, key revision and (for recovery) case/successor.
6. Sign a canonical, domain-separated decision envelope; store references/fingerprints only.
7. Do not hold a Mongo transaction open during slow external calls. Obtain immutable verified evidence first, then re-check bounded validity and append with expected-revision CAS inside the caller-owned transaction.
8. Timeout, network partition, signature failure, clock uncertainty, malformed response, revocation-source outage, key rollover ambiguity and provider disagreement all deny.
9. Preserve OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE until all independent governance and production gates pass.
10. No provider KYC result grants WILSY permissions, admin roles, financial execution, legal-practitioner privileges, Sheriff scope or product entitlements.

## Build-versus-buy scorecard

Score candidates 0–5 with evidence, not marketing claims:
- South African CIPC/registry access rights and filing-history completeness (20%).
- Independent assurance, accreditation and legal-scope transparency (15%).
- Cryptographic key custody, HSM/KMS, dual control and audit exports (15%).
- Revocation/currentness, webhook plus authoritative re-check semantics (15%).
- Privacy, POPIA controls, data residency, retention and deletion/legal hold (10%).
- API reliability, idempotency, versioning, sandbox and incident SLA (10%).
- Portability, open standards and exit/export rights (10%).
- Recovery independence, dispute process and appealability (5%).

Hard disqualifiers: provider self-appoints as issuer; provider controls both issuer and recovery decision; private keys exportable without approved exception; no auditable revocation; no lawful source access; or provider claims KYC alone proves legal ownership.

## Implementation sequence

1. Build source/identity/issuer/custody/recovery ports and conformance tests without choosing a vendor or enabling positive production results.
2. Build CIPC connector only after lawful access credentials and API/portal integration terms are confirmed; access to the restricted BO register is not presumed.
3. Select KMS/HSM only after security review, key-custody ownership and dual-control appointment.
4. Select identity proofing and credential infrastructure using the scorecard; keep provider claims distinct from WILSY legal determinations.
5. Implement issuer and recovery adapters only after their separate signed institutional appointments and trust roots are verified.
6. Run adversarial contract suites, real-source sandbox tests, key ceremony/rotation/revocation tests, real replica-set Mongo atomicity tests, outage tests and production composition review on one exact commit.

## Current decision

No vendor or authority is appointed by this design. This review authorizes engineering of provider-neutral contracts and conformance tests only. Production issuer, key custody, ownership issuance and recovery remain disabled. Required denial: OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE.