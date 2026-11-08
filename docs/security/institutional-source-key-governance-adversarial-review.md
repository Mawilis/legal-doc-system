# PR #393 — Institutional Source-Key Governance Adversarial Review

**Review posture:** remediation in progress; do not approve or merge.  
**Reviewed baseline:** `368b428ad6529973d76132888885c693024c08cb`  
**Implementation branch:** `eos/institutional-source-key-governance-commands-20261108`

## Implemented in the remediation commits

1. **Proposal evidence binding:** the provider-issued SHA-256 evidence fingerprint is persisted in the immutable `PROPOSED` event and included in the proposal command fingerprint used for idempotency.
2. **Approval evidence binding:** the provider-issued SHA-256 evidence fingerprint is persisted in the immutable `APPROVED` event and included in the approval command fingerprint used for idempotency.
3. **Revocation result binding:** the typed result now binds tenant, source, key, public-key fingerprint, proposer, revoker, reason, governance decision, approval evidence reference, independent approver and evidence fingerprint. The route compares each field against the authenticated command context before mutation.
4. **Denial evidence:** route-level command denials are written to a separate denial collection after the failed lifecycle transaction aborts. The record contains actor, tenant, action, source/key identifiers, bounded reason code, HTTP status, timestamp and correlation ID. Evidence references, request bodies, public-key bytes and provider payloads are excluded.
5. **Tamper detection:** successful per-key lifecycle events carry a canonical SHA-256 hash linked to the prior event. A separate transactional audit-head document anchors the latest sequence/hash. Proposal reads and current/historical trust resolution verify the event chain and head. Replica-set tests cover event edits and tail deletion.
6. **Authenticated IAM route:** a new real-replica-set test keeps the production `RequireTenantAuthorization` dependencies in place and overrides only the authentication identity seam. It exercises proposal, maker-checker rejection, independent approval, revocation and ordinary tenant-owner denial using durable principal, membership, business-role and authorization-role records.
7. **Transaction retry contract:** the evidence-verifier protocol now explicitly requires read-only, retry-safe, idempotent behavior with no one-time evidence consumption or external side effects. A replica-set HTTP test injects a transient transaction error and expects the provider verification callback to be repeated while only one proposal and one audit-head event persist.
8. **Lifecycle projection:** the immutable key document remains a proposal snapshot; the registry derives its returned lifecycle projection from append-only events. Approval and revocation responses explicitly report `APPROVED` and `REVOKED`.

## Controls still required before approval

- **Protected audit storage:** the hash chain and separate head detect event alteration or tail deletion while the head remains protected. The repository changes do not prove MongoDB database-role permissions prevent update/delete of lifecycle events and audit heads, nor do they establish an independently protected audit sink. Provision and test those controls before production trust activation.
- **IAM-boundary denial persistence:** route-level command denials are durably recorded. Authentication/authorization denials rejected before the route handler continue to rely on the central tenant-authorization observation path; durable outbox-backed denial records for that boundary remain to be certified.
- **Storage outage certification:** add a real route test for MongoDB unavailable during command execution and during denial-audit persistence. The original denial must remain the HTTP outcome if the audit sink is unavailable, and the operational signal must be bounded.
- **Audit retention and restore:** define retention, backup, independent export, restore verification and alerting for broken/missing event chains and audit heads.
- **Production composition:** continue to use the unavailable verifier by default. No positive institutional adapter, trust anchor, DHA/CIPC credential, production key custody or activation is authorized by this PR.
- **Exact-head CI:** the latest code changes must complete the source-key workflow and all inherited required workflows successfully. A previous green run is not certification of a later head.

## Review rules

- A test fixture or synthetic verifier is not institutional evidence.
- A hash chain is not a substitute for protected storage permissions or an independently held checkpoint.
- A real Mongo replica set proves database transaction behavior only for the exercised path; it does not prove production IAM configuration, infrastructure permissions or institutional authority.
- Provider verification may execute inside a retryable MongoDB callback only while the provider adapter obeys the documented read-only/idempotent retry contract.
- Keep PR #393 draft and unmerged until all required controls are closed and the resulting exact head has fresh certification.
