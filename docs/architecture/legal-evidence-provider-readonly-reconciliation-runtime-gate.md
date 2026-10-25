# Legal Evidence Provider Read-Only Reconciliation — Runtime Gate

**Status:** BLOCKED — authorization contract required before runtime wiring  
**Version:** v1.0.0-L10A2R-C4D7B-RUNTIME-GATE  
**Date:** 2026-10-25  
**Branch baseline inspected:** `feat/legal-evidence-provider-readonly-reconciliation` at `6aa40d7347f943b29a39e90fe8f805a5b3a6cf04`

## Decision

The first runtime invocation is intended for privileged internal operators only. It must be bound to one exact tenant and provider scope, remain read-only at the provider boundary, and preserve the caller-owned active Mongo transaction required by the coordinator.

No route, CLI command, scheduler, or service entry point may be added until the repository has a canonical, enforceable source for internal-operator identity and current authorization. A role string, caller-selected tenant, tenant Legal Partner grant, evidence-write permission, or cleanup-authorization permission is not a substitute.

## Verified existing components

- `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_factory.py` assembles existing read-only dependencies from an explicitly supplied provider and Mongo database. It does not establish identity, authorization, tenant scope, provider configuration, or transaction lifecycle.
- `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_coordinator.py` requires an already-active caller-owned transaction and rejects missing/incomplete coverage, source drift, and invalid evidence. It does not start, commit, abort, or retry transactions.
- `tools/eos/legal_operations/service/legal_evidence_provider_coverage_verification_service.py` verifies exhaustive provider coverage; it does not establish orphan status or deletion authority.
- `tools/eos/legal_operations/orchestration/legal_evidence_provider_object_orphan_proof_orchestrator.py` is a separate downstream authority boundary. Reconciliation output is not an orphan proof, cleanup authorization, retention clearance, legal-hold clearance, or deletion authorization.

## Current evidence and limits

The previously observed local focused test runs reported:
- Factory tests: 11 passed.
- Coordinator tests: 22 passed.

These are focused unit tests only. They do not certify a production invocation path, live provider configuration, real-Mongo end-to-end reconciliation, CI, or deployment.

Repository inspection found canonical tenant IAM patterns and canonical SYSTEM permission vocabulary, but did not establish a dedicated reconciliation-read permission together with an approved internal-operator grant, exact operation binding, and tenant-scope derivation. The existing tenant authorization composition requires tenant membership/business-role/role-grant semantics and is not by itself an internal-operator policy.

## Required contract before wiring

1. **Operator principal:** derive from a canonical authenticated server-side authority; reject caller-supplied identity or role claims.
2. **Dedicated permission:** add a narrowly scoped canonical reconciliation-read permission and exact operation binding through the repository's approved IAM lifecycle. Do not reuse evidence-write or cleanup-authorization permissions.
3. **Grant policy:** identify the approved internal-operator authorization role or SYSTEM assignment authority and prove current possession, revocation state, and any required privileged activation. Do not infer authority from static role definitions alone.
4. **Tenant/provider scope:** derive tenant identity and the canonical scope fingerprint from trusted server-side authority and provider configuration. Reject default/global tenants and caller-selected unbound provider coordinates.
5. **Runtime configuration:** resolve the certified provider adapter and database through canonical application configuration; fail closed if either is unavailable. Do not create a second provider/configuration authority.
6. **Transaction ownership:** the invoking layer owns the active Mongo session/transaction. The coordinator and downstream orphan-proof orchestrator must not create, commit, abort, or retry it.
7. **Audit and denial:** use existing canonical audit/denial evidence facilities without logging credentials, raw legal evidence, or provider secrets.
8. **Adversarial certification:** test unauthorized/missing/revoked operator grants, tenant/provider scope substitution, absent configuration, inactive transactions, incomplete coverage, incomplete write-session membership, provider read-only behavior, and proof that reconciliation cannot directly issue orphan proof or deletion authority.
9. **Integration certification:** exercise the actual approved entry point with real Mongo transaction semantics and the supported provider adapter. Report unavailable infrastructure as blocked, never passed.

## Non-goals

This gate does not authorize provider deletion, retention modification, legal-hold release, automatic retries, orphan-proof issuance, or financial execution. Provider mutation remains outside the reconciliation capability.

## Exit criteria

Runtime wiring may proceed only after the canonical operator grant, permission-operation binding, trusted tenant/provider scope, provider configuration, transaction owner, and audit path are each located in repository evidence and covered by adversarial tests. If any authority is absent, the correct outcome is a stable fail-closed denial—not a fallback path.

---
