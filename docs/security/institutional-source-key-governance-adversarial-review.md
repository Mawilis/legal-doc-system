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


## AI code-review addendum — repository contract and denial integrity

Reviewed against the mandatory `AGENTS.md` Sovereign Codex Governance Contract at the same branch.

### Findings

1. **Blocking — source artifact contract nonconformance.**
   - `tools/eos/api/institutional_source_key_router.py` lacks the required institutional versioned header, changelog, authority/tenant/security boundaries and sovereign end seal.
   - `tools/eos/security/institutional_source_key_governance_evidence.py` lacks the same required artifact metadata and end seal.
   - `tools/eos/security/institutional_source_signing_key_registry.py` records behavioral changes in its changelog but remains at `v1.0.0`; the header and end-seal version were not incremented.
   - Required contract: `AGENTS.md` sections 5–7 and 17–20. These are code-governance certification failures even though the runtime test workflow passed.

2. **High — denial evidence is outside the lifecycle integrity chain.**
   - The denial collection is indexed but denial documents have no event sequence/hash, chained checkpoint or independently protected export in this PR.
   - Include the denial collection in the protected storage policy and add integrity verification/reconciliation.

3. **Medium — denial-audit persistence failure is insufficiently observable.**
   - `_record_denial` catches all exceptions and emits only a fixed log string. Preserve the original HTTP denial, but add structured, durable operational evidence and a reconciliation path for audit-write failure.

4. **Medium — denial coverage begins too late in the request path.**
   - Authentication/authorization failures rejected before handler execution and validation/readiness failures before the guarded transaction are not captured in the new denial collection.
   - Integrate with the canonical IAM audit/outbox boundary; do not duplicate authorization or create a parallel authority path.

### Required remediation sequence

1. Bring each affected production source artifact into compliance with the repository contract, one primary file per certified delivery, using full-file review and exact version alignment.
2. Extend tamper evidence and protected-storage policy to denial records.
3. Add durable structured audit-failure telemetry and reconciliation.
4. Wire pre-handler authorization denials through the canonical IAM audit/outbox.
5. Add tests for event and denial mutation/deletion, audit-head rollback, storage outage and denial reconciliation.
6. Re-run all relevant checks after each file change and all applicable workflows on the final exact head.

These findings supersede any earlier implication that the prior 446-test/16-workflow result closed the complete security review. That result remains evidence for its exact commit only.

**Disposition: remediation continues; do not approve, merge, or activate production trust.**


## Resolution update — exact head `dcd12a64906316bfab91b0c41e0b6f09691f4a5e`

The following repository-contract findings are now corrected:

- `tools/eos/api/institutional_source_key_router.py`: versioned sovereign header, changelog, authority/tenant/security boundaries, public request/route documentation and end seal added at `092bc393a28f3a48aa19280bac2c8258449b9b28`.
- `tools/eos/security/institutional_source_key_governance_evidence.py`: versioned sovereign header, changelog, authority/tenant/security boundaries and end seal added at `68b5d7160e6af1274289e6edca39b5e5e685314b`.
- `tools/eos/security/institutional_source_signing_key_registry.py`: semantic version advanced to `v1.1.0`, with matching changelog and end-seal version, at `dcd12a64906316bfab91b0c41e0b6f09691f4a5e`.

Both corresponding artifact-contract review threads have been resolved after source inspection and successful certification.

The latest exact-head signed-offer workflow on `dcd12a6` completed successfully: **446 passed, 12 warnings, 0 failed**, using a real MongoDB replica set. All 16 applicable workflows completed successfully, with no failed or pending workflows; one superseded run was cancelled by concurrency control.

### Remaining code findings

5. **Medium — append path does not verify the complete existing chain before mutation.** `_seal_event` validates the last event and audit head, but does not call the full `_verify_event_chain` before adding another event. The router currently calls `get_proposal` first for approval/revocation, which verifies the chain, but the registry's public mutation methods should enforce this invariant themselves. A direct caller could otherwise append to a chain whose earlier link is already corrupt. Require full-chain verification before every non-genesis append and add a real-replica-set regression test.

6. **High — denial audit is not independently protected or tamper-evident.** The denial collection remains outside the lifecycle chain. Its protection must be covered by the same explicit storage-role policy or an independently protected sink, and its integrity must be verified/reconciled.

7. **Medium — denial-audit write failure lacks durable recovery.** The recorder still catches broad exceptions and emits only a fixed log string. The original denial response must remain intact, but the audit-write failure needs structured durable telemetry and a reconciliation path.

8. **High — canonical IAM denial observation is not durable audit persistence.** The current tenant authorization terminal observer emits a structured application log only; the authentication audit helper also logs and returns an in-memory payload. No generic durable IAM-denial outbox was found in the repository search. Pre-handler denials therefore need a governed persistence/outbox path, with a safe fallback when the database is unavailable.

9. **Operational — protected audit infrastructure is not yet proven.** Define and test database roles that prevent ordinary application identities from updating/deleting lifecycle events, audit heads and denial evidence, or use an independently protected audit sink. Add retention, independent export, backup/restore verification and integrity alerts.

### Current disposition

The artifact-contract findings are closed. The remaining audit-integrity, IAM-denial persistence and infrastructure findings remain open. Keep PR #393 draft and unmerged; do not activate production trust.


## Resolution update — registry append integrity

**Reviewed and certified head:** `0857d57b5155f25b5d7b2711472a12c9fbd3cf92`

The registry now invokes full `_verify_event_chain` inside `_seal_event` before every lifecycle append. This moves the invariant into the registry boundary and protects direct callers, not only router-mediated calls.

A new real-replica-set regression test corrupts the earlier PROPOSED event, invokes registry approval directly, and verifies:
- the append fails with `SOURCE_SIGNING_KEY_AUDIT_CHAIN_INVALID`;
- no APPROVED event is inserted;
- the audit head remains byte-for-byte unchanged.

Certification evidence:
- Institutional Signed-Offer Verification: **447 passed, 12 warnings, 0 failed**, on a real MongoDB replica set. The new regression test passed.
- All **16 applicable workflows succeeded** on this head. One superseded Repository Integrity run was cancelled by concurrency control; the current Repository Integrity run succeeded.
- PR remains draft and unmerged.

## Additional repository-wide security blocker discovered during AI review

The branch contains legacy MongoDB bootstrap scripts outside the PR's changed-file set that undermine the intended IAM and audit-storage security boundaries:

- `server/fix_tenant_auth.sh` contains a hard-coded service-account password and uses that account to grant itself tenant database access.
- `server/inject_master_user.sh` contains the same hard-coded credential and directly upserts an active privileged identity into the users collection, bypassing canonical global-principal, membership, capacity and MFA flows.
- `server/elevate_wilsy_app.sh` grants `userAdmin` to the application service account.
- `server/force_fix_wilsy.sh` runs an unauthenticated MongoDB role-injection path and grants broad database privileges.

The credential is treated as exposed; its value is intentionally not reproduced in this review record. If it has ever been valid in any environment, rotate/revoke it and inspect authentication logs. These scripts must be disabled or replaced by a governed, externally authenticated provisioning workflow. Do not assume they are active in a live environment without runtime evidence.

This is a **critical repository-wide IAM/security blocker** for production trust activation, even though the scripts are not part of PR #393's current diff. Their remediation should be isolated into separately certified source-file changes or a dedicated security PR so that the source-key governance change does not silently absorb unrelated bootstrap migration risk.

## Remaining source-key governance gates

1. Denial records remain outside the lifecycle hash chain and require protected storage or an independently protected sink.
2. Denial-audit write failures need durable structured telemetry and reconciliation while preserving the original denial.
3. Pre-handler IAM denials need canonical durable audit/outbox persistence.
4. MongoDB roles must demonstrably prevent the application identity from updating/deleting lifecycle events, audit heads and denial evidence.
5. Retention, independent export, backup/restore verification and integrity alerting remain unproven.

**Disposition:** the registry append-integrity finding is resolved and certified. The denial-audit and protected-storage gates remain open. The legacy bootstrap scripts are a separate critical repository-wide blocker. Keep PR #393 draft and unmerged; do not activate production trust.
