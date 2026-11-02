# Issue 300 — provider conformance, cryptographic verification and recovery replay

## Scope

This tranche turns the provider-neutral contracts into executable, fail-closed validation primitives. It deliberately does not create a legal ownership verifier or make any positive ownership assertion. `VerifiedTenantOwnershipEvidence` remains unavailable until independent issuer and recovery governance is verified.

## Source freshness and filing lineage

`assess_registry_lineage` requires timezone-aware retrieval/effective timestamps, a bounded freshness policy, stable source/entity identity, SHA-256 fingerprints and an unambiguous filing chain. It rejects stale/future snapshots, unknown or cyclic supersession links, forks, duplicate filing references with conflicting fingerprints, unknown statuses and non-active terminal filings. A current filing is selected only when exactly one terminal record is active.

The source adapter must retrieve the complete relevant filing lineage and an authoritative current status. A provider that cannot expose sufficient lineage, source timestamps or revocation/currentness data is unavailable for this use case; the caller must not infer currentness from the newest item it happens to receive.

## Cryptographic integrity and key lifecycle

`verify_provider_signature` verifies exact payload bytes using versioned PEM public keys and one of Ed25519, ECDSA/SHA-256 or RSA-PSS/SHA-256. It enforces key validity windows, explicit revocation and supersession times, algorithm/key-type agreement, strict base64 decoding and signature verification. A key revision is immutable; rotation creates a new revision and the previous revision must be retired/revoked under governed policy.

Key records must themselves come from an independently governed trust-root/key-custody source. The verifier accepts public keys only; private keys remain in the external HSM/KMS. This code does not enroll a trust root, prove legal appointment of a signer, or substitute for HSM attestation.

## Recovery decision validation

A recovery decision is bound to the exact tenant, legal entity, case reference and fingerprint, and successor principal. It must have an unexpired validity interval, no effective revocation timestamp, and a final appeal state (`FINAL`, `NO_APPEAL` or `APPEAL_EXHAUSTED`). The canonical `recovery_decision_signing_payload` binds every decision claim to the lookup scope. `RecoveryDecisionReplayRegistry.consume` requires a valid signature under a key explicitly bound to the receipt's trust-root reference before writing.

The replay registry has unique tenant/decision and tenant/case indexes. Consumption requires the caller's active Mongo transaction; duplicate decisions or a second decision for the same case are rejected. The registry never starts, commits, aborts or retries a transaction.

The independent adjudicator must separately establish quorum, conflict/recusal checks, notice and objections, appeal finality, authority scope and revocation. Fingerprints in a receipt are references to those proofs, not proof that the referenced processes were legally sufficient. A production adapter must verify those proof objects and the signing authority against approved governance records before it calls these primitives.

## Provider failure policy

`invoke_provider_fail_closed` maps timeout, transport, malformed-response and other provider exceptions to a bounded unavailable error without returning provider payloads or silently falling back to caller assertions. A returned provider object remains untrusted until its schema, scope, provenance, freshness, signature and revocation have been checked.

No provider credentials, private keys, live CIPC access, identity documents or production KMS integration are included. No vendor is appointed. No authority is inferred from successful unit or replica-set tests.

## Certification

The dedicated `.github/workflows/issue-300-provider-conformance-certification.yml` workflow compiles and type-checks the provider contracts, runs adversarial source/signature/recovery/provider-failure tests, then starts a disposable Mongo 7 replica set to certify rollback, commit and replay protection.

Production readiness still requires separately governed provider adapters and real external-provider certification using approved test credentials and documented authority. The current canonical ownership verifier remains deny-only with `OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE`.
