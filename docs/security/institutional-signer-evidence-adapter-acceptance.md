# Institutional Signer Evidence Adapter Acceptance Gate

## Status

**NOT CONFIGURED — positive enrollment and approval remain denied.**

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

The adapter must produce a signed or otherwise independently verifiable evidence snapshot. MongoDB transaction atomicity covers EOS persistence only; it does not make a remote source transaction atomic. The implementation must therefore persist the complete source snapshot identity/revision and verification time, enforce a governance-approved maximum age, and reconcile revocations or superseding revisions. A fingerprint alone is not a complete audit record.

## Persistence and route gates

Before enabling a positive verifier:

1. Persist complete identity, mandate and approval provenance in the enrollment record and append-only event snapshots, including source system, record ID, revision, evidence fingerprint, status, validity and verification time.
2. Bind provenance to the canonical tenant, principal, certificate fingerprint and exact request/approval scope.
3. Ensure provenance and lifecycle state are written in the same caller-owned Mongo transaction; abort must leave neither state nor audit event.
4. Re-check source currentness at approval and before any use of the signer certificate, according to the approved freshness/revocation policy.
5. Prove duplicate/replay behavior, source revision changes, revocation races, requester/reviewer separation and outage fail-closed behavior on a real replica set.
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
