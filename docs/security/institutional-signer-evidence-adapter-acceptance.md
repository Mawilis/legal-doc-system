# Institutional Signer Evidence Adapter Acceptance Gate

## Status

**NOT CONFIGURED — positive enrollment and approval remain denied. Full source-snapshot persistence is implemented; no positive adapter is approved.**

The EOS route composition installs `UnavailableInstitutionalSignerEvidenceVerifier`. This is intentional. No adapter may be substituted until governance names and approves the authoritative systems and their accountable owners.

## Required authoritative authorities

Governance must identify three independently controlled evidence authorities. They may be distinct services within one institution only where their access controls, record custody and approval roles remain independently governed.

1. **Natural-person identity proofing**
   - Authoritative identity-proofing provider and legal basis for the assurance level.
   - Exact subject principal binding and certificate public-key fingerprint binding.
   - Source record identifier, immutable revision, evidence fingerprint, verification time, validity window, current status and revocation state.
   - Documented challenge/liveness and in-person or equivalent controls where required by the approved assurance profile. EOS must not ingest raw identity documents unless separately approved and strictly necessary.

2. **Corporate signatory mandate**
   - Authoritative company secretarial, board-resolution or legally approved mandate register.
   - Exact legal-entity reference, named principal, certificate fingerprint, permitted signing scope, effective period and revocation status.
   - Source record identifier/revision and cryptographically verifiable provenance.
   - The mandate must be independently confirmed against the institution's governing records; a user-provided URI, EOS tenant role or subscription is never sufficient.

3. **Independent approval attestation**
   - Authoritative maker-checker approval source or governed attestation service.
   - Exact enrollment request, certificate fingerprint, requester, distinct reviewer, approval scope, source revision and validity.
   - Reviewer must be distinct from the requester and must possess independently established approval authority.
   - Attestation must bind the exact enrollment evidence snapshot, not merely the certificate common name or a mutable URI.

## South African source-system selection notes

These are candidate source authorities, not approved adapters or proof that WILSY has access:

- **Natural-person identity:** the Department of Home Affairs states that its National Population Register verification service is available to private-sector clients as well as government users. WILSY must complete DHA's formal client onboarding and confirm the permitted verification purpose, assurance level, data minimisation and service terms; do not assume an unauthenticated public API. See [South African Government — DHA identity verification service, 6 July 2025](https://www.gov.za/news/media-statements/home-affairs-launch-world-class-new-identity-verification-service-and-cost).
- **Corporate mandate:** CIPC states that company records include the Memorandum of Incorporation, director records, meeting notices/minutes and resolutions. Use CIPC records to corroborate the legal entity and director status, then verify the actual signing power and scope against the current MOI and valid company/board resolutions. A director listing alone is not evidence of authority to sign this particular institutional instrument. See [CIPC — Company Records](https://www.cipc.co.za/?page_id=2683).
- **Independent approval:** no external government register is assumed to confer WILSY's internal approval authority. The proposed WILSY-appointed governance function and any external legal reviewer remain subject to explicit institutional appointment, separation-of-duties rules and documented approval. No committee or reviewer is configured by this implementation.

The DHA and CIPC references above identify candidate authorities only. Formal access, source ownership, service contracts, legal basis, source authentication and field-level response semantics must be verified before adapter implementation.

## Adapter acceptance contract

Every adapter must be read-only and must:

- Authenticate EOS using a dedicated workload identity with least-privilege read access.
- Authenticate and validate the source system, its signing key/certificate chain, response integrity and source identity.
- Resolve caller-supplied references as lookup coordinates only.
- Verify exact tenant, principal, certificate fingerprint, legal entity, purpose and evidence kind.
- Reject missing, malformed, ambiguous, stale, expired, suspended, withdrawn, revoked, superseded or cross-tenant records.
- Return source system ID, immutable record ID/revision, record status, validity interval, revocation state, verification timestamp and evidence fingerprint.
- Enforce bounded timeouts, response-size limits, retry policy and circuit-breaker behavior. Any timeout or source outage denies the command.
- Never create a signer, IAM membership, role, mandate, approval or certificate as a side effect.
- Expose a documented reconciliation path for later source corrections and revocations.

The adapter must produce a signed or otherwise independently verifiable evidence snapshot. MongoDB transaction atomicity covers EOS persistence only; it does not make a remote source transaction atomic. EOS now persists complete source-system, record ID/revision, original evidence reference, status, evidence fingerprint, validity interval, revocation state, verification/evaluation times, identity assurance level, legal-entity and mandate scope, approval scope, and exact tenant/principal/certificate/requester/reviewer bindings in the enrollment/approval records and append-only event snapshots. Canonical digests are recomputed and checked at the registry boundary. This closes the fingerprint-only persistence gap; it does not itself prove that a source is authoritative or that a remote source remained current after the read. The governance-approved maximum evidence age, source revision recheck/reconciliation policy and pre-use revocation check remain unconfigured and must be approved before positive adapters can be enabled. In addition, signer activation records are now marked `PENDING_VERIFICATION` after approval, and the certificate-use registry refuses to return an active signer until a separate post-approval source-currentness verification records `CURRENT`. No currentness verifier or positive adapter is configured yet, so signer use remains blocked by design.

## Persistence and route gates

Before enabling a positive verifier:

1. **Implemented in the provenance-snapshot branch:** persist complete identity, mandate and approval provenance in enrollment records and append-only event snapshots; reject incomplete, expired, revoked or malformed snapshots; recompute and compare canonical SHA-256 digests at the registry boundary.
2. **Implemented in route contract:** bind provenance to the canonical tenant, principal, certificate fingerprint and exact evidence/request scope; require distinct requester and reviewer.
3. **Implemented in transaction composition; certification pending:** provenance and lifecycle state are written through the same caller-owned Mongo transaction as the append-only event; real replica-set abort/retry proof remains required.
4. **Partially implemented:** authoritative verification is invoked at enrollment and again at approval. A governance-approved maximum age, source revision reconciliation and pre-use source-currentness/revocation check remain unconfigured.
5. Prove duplicate/replay behavior, source revision changes, revocation races, requester/reviewer separation, digest tampering, forced abort and outage fail-closed behavior on a real replica set.
6. Keep revocation independent and immediately effective in EOS; CRL publication remains a separate durable obligation.

## Independent institutional review package

The review package must contain only controlled references and cryptographic digests, not raw identity documents or secrets:

- Governance approval naming each authoritative source, its owner, evidence class and assurance standard.
- Adapter threat model, workload identity, source authentication and least-privilege review.
- Source-record samples or controlled fixtures demonstrating exact binding, expiry, revocation, supersession and tampering rejection.
- Mongo replica-set transaction and audit-outbox evidence, including forced abort and retry tests.
- Maker-checker evidence proving distinct, authorized requester and reviewer identities.
- Independent revocation test proving signer use/offer acceptance is denied before and after CRL publication.
- Reviewer sign-off from institutional governance/legal authority, security, PKI operations and an independent technical reviewer.

No single engineer, tenant owner, CI workflow or EOS service may self-approve the institutional mandate or activate the trust chain.

## Exit decision

Until the source authorities are selected, adapters independently assessed, full provenance persistence implemented, replica-set certification green and institutional reviewers have signed the evidence package, the verifier remains unavailable and the signer enrollment/approval routes remain fail-closed.


## Post-approval currentness reconciliation contract

The registry now accepts only a verifier-issued opaque currentness result. The verifier contract includes a separate `verify_currentness` operation that must re-read the identity, mandate and independent approval source records. Reconciliation is bound to the enrollment's expected revision, exact evidence references, source-system and immutable source-record identities, canonical tenant/certificate/principal/requester/reviewer scope, and a digest of all three current snapshots. A source revision may advance only for the same source system and immutable record identity; a changed source identity is denied for governance review.

The currentness result carries two distinct digests: the canonical digest of the verified provenance snapshot and the fingerprint of a persisted, bounded, non-PII source-observation snapshot. The observation snapshot records each evidence kind, source system, immutable record ID/revision, status, revocation flag, evidence fingerprint and observation time, including the negative source state when a record is withdrawn or revoked. The caller-owned Mongo transaction atomically writes the currentness projection, enrollment revision and append-only event. Stale revisions, divergent idempotency replay, scope changes and digest mismatches fail closed. `CURRENT` requires an adapter-issued finite `valid_until` lease; signer use is denied when that lease expires, even if no reconciliation worker has yet marked the record stale. `NOT_CURRENT` records a reason and observation fingerprint and immediately makes the signer unusable.

No lease duration, maximum evidence age, source polling cadence, positive adapter or external source credentials are configured by this change. The approved adapter must derive the finite lease from a separately approved governance policy and authoritative source semantics. The current default verifier rejects currentness verification, so no record can be promoted to `CURRENT` through production runtime today. The replica-set test uses a test-only opaque result fixture to exercise the registry contract; it is not a live source adapter or evidence of institutional authority.


## Reconciliation execution boundary

The new orchestration function performs a short transactional enrollment read, closes that transaction, calls the authoritative source verifier outside MongoDB, then opens a separate caller-owned transaction to persist the result using the revision captured before the source call. This prevents slow or unavailable external systems from holding MongoDB transactions open. If the enrollment changes while source checks are in flight, the compare-and-set fails and the worker must restart from a fresh read; it must not retry the old verification result against a newer revision. The default verifier is unavailable, so orchestration cannot create a positive currentness result today.


The enrollment registry also provisions a compound index over tenant, lifecycle status, currentness status and lease expiry so a future governed worker can efficiently discover pending and expired-currentness candidates. This index is not a scheduler: no polling interval or automatic retry cadence is assumed. `NOT_CURRENT` records are deliberately excluded from automatic promotion and require a new authoritative check under the approved governance process.


Currentness rechecks must preserve the previously approved identity-assurance level, legal-entity reference, mandate scope and independent-approval scope. Any change to those authority-bearing fields is not silently accepted as routine freshness: it is rejected for a new governance decision and re-enrollment/approval as applicable.


## Candidate discovery

`list_currentness_candidates` provides a bounded, caller-transaction read for ACTIVE enrollments that are awaiting first verification (including legacy ACTIVE records with no currentness status) or whose finite CURRENT lease has expired. Results are ordered deterministically by request time and certificate fingerprint. `NOT_CURRENT` and revoked enrollments are not automatically requeued. The compound index supports this query, but the code intentionally defines no background schedule, polling cadence, retry budget or actor identity; those remain governed operational settings.


A negative source observation may legitimately report a newer source revision and changed evidence fingerprint (for example, an authority record transitions from active to revoked). The reconciliation contract therefore requires stable source-system and immutable record identity for all observations, but requires exact revision/fingerprint equality with the provenance snapshot only for a `CURRENT` result. For `NOT_CURRENT`, the new observed revision, status, revocation flag and fingerprint are persisted as the negative observation while the last verified-good provenance snapshot remains available for audit.


The source-observation snapshot also carries `valid_from` and `valid_until`. A record can therefore be classified `NOT_CURRENT` because it is revoked/withdrawn/superseded or because its validity interval has expired or has not yet begun, even when the source's status string remains ACTIVE. A CURRENT result is accepted only when each observation's validity interval covers the exact observation time.


## Provider adapter framework (contract only)

The source-adapter framework defines three distinct read-only evidence channels: identity proofing, corporate signatory mandate and independent approval. Each lookup is tenant-, principal-, certificate-, evidence-kind- and evaluation-time-bound. Returned source envelopes carry immutable source-system/record/revision identity, exact evidence references and scope bindings, evidence fingerprint, status, validity interval, revocation state, observation time and a source-response signature reference. Provider response authenticity is a separate protocol from parsing or field validation; a provider response is untrusted until an independently configured authenticator validates source identity, signature/integrity and exact request binding.

The default adapter set denies all three channels. This change intentionally supplies no DHA, CIPC, company-secretarial or internal governance network client, credentials, trust anchors, provider URLs, or positive verifier. The framework is not connected to the enrollment route and cannot issue VerifiedInstitutionalSignerEvidence or VerifiedSignerEvidenceCurrentness. Provider-specific adapters may only be implemented after formal source onboarding, legal-purpose confirmation, workload-identity approval, source-response trust configuration, field mapping review and independent security assessment. Provider I/O must remain outside MongoDB transactions; a timeout, invalid signature, source mismatch or outage is a denial, not an empty record.


The framework now includes a shared authenticated-read boundary. It checks that the adapter supports the requested evidence kind, authenticates the provider response through a separately supplied response authenticator, and then enforces exact equality for tenant, principal, certificate fingerprint, evidence kind/reference, legal entity, requester, reviewer and required authority scope. It intentionally preserves negative status and revocation observations for the currentness reconciler rather than converting them to transport errors. This is contract/conformance code only: no production authenticator or provider implementation is present.


## Cryptographic response authentication

A concrete provider-neutral Ed25519 authenticator is available for independent source-response verification. Its trust map is keyed by the exact pair (source-system ID, response-signing key ID), and an empty map denies all responses. The canonical signed payload binds the tenant, evidence kind/reference, subject principal, certificate fingerprint, legal entity, requester/reviewer, authority scope, source record/revision, evidence fingerprint, status, validity interval, revocation flag, observation time, signing-key ID and signature reference. Tampering with the source revision or using a key pinned to a different source is rejected. Key issuance, custody, rotation, revocation and source trust onboarding remain external governance gates; this implementation does not pin any live institutional key.

The Ed25519 authenticator is a cryptographic primitive, not proof that a purported DHA/CIPC/governance endpoint is genuine. Source identity and exact lookup binding still require the separately governed adapter/authenticator configuration and independent review. No production trust configuration is present.
