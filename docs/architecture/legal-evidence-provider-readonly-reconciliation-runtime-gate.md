# Legal Evidence Provider Read-Only Reconciliation — Runtime Gate

**Status:** RUNTIME WIRING BLOCKED — full authorization gate and real-Mongo transaction certification pass; platform audit and provider-boundary gates remain outstanding  
**Version:** v1.2.0-L10A2R-C4D7C-FULL-GATE-MONGO-CERTIFIED  
**Date:** 2026-10-25  
**Implementation state reviewed:** `204e516364fec72f3cc08ce3660ba3ff134c9da0`

## Decision

The first runtime invocation is intended for privileged internal operators only. It must be bound to one exact server-configured tenant and provider, remain read-only at the provider boundary, and preserve the caller-owned active Mongo transaction required by the reconciliation coordinator.

The reconciliation-specific authorization gate and full real-Mongo composition now exist and pass focused certification. No route, CLI command, scheduler, or production service entry point is connected. Runtime wiring remains blocked until a canonical platform-scoped durable authorization allow/deny audit path and end-to-end provider read-only certification are established.

## Implemented authorization contract

- `tools/eos/auth/privileged_activation_use_authority.py` exposes `authorize_noninteractive_workload`. It composes the signed workload request once, requires the canonical `WorkloadTrustFact` to be current, validates P3 assurance identity before P4/P2 lookup, then checks current activation and exact P2 eligibility lineage in the caller-owned transaction.
- `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_authorization_gate.py` requires the exact `SOVEREIGN_ARCHITECT` / `PLATFORM_SYSTEM_ROOT` activation with activation `tenant_id=None`, current possession of `legal_operations:evidence_provider_reconciliation:read`, and a provider-bound server-owned scope resolver. Request header fields are exact-allowlisted; request-selected tenant/provider fields are rejected.
- `build_server_configured_reconciliation_target` binds the deployment tenant from `WILSY_LEGAL_EVIDENCE_RECONCILIATION_TENANT_ID` to the existing validated S3 configuration. It uses `WILSY_LEGAL_EVIDENCE_S3_BUCKET`, the existing region default/override, and optional `WILSY_LEGAL_EVIDENCE_S3_KMS_KEY_ID`. The resulting resolver rereads the fixed tenant through canonical `TenantRegistry.get` with the same session and derives the SHA3-512 tenant-scope fingerprint itself.
- This configuration supports **one server-configured tenant/provider target per resolver instance**. Multi-tenant batch selection is not implemented and must not be added as caller-supplied scope.
- `tools/eos/auth/system_permission_command_policy.py` permits exactly three ongoing non-command SYSTEM permissions: `privileged_activation:issue`, `privileged_activation:break_glass`, and `legal_operations:evidence_provider_reconciliation:read`. Assignment and revocation remain subject to the existing command-possession, ACTIVE-target, evidence, lineage, and caller-transaction contracts. Assignment of the read permission alone does not authorize use; the reconciliation gate independently requires P5 platform-root use.

## Existing reconciliation boundaries retained

- `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_factory.py` assembles read-only dependencies from an explicitly supplied provider and Mongo database; it does not establish identity or authorization.
- `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_coordinator.py` requires an already-active caller-owned transaction and rejects missing/incomplete coverage, source drift, and invalid evidence. It does not start, commit, abort, or retry transactions.
- `tools/eos/legal_operations/service/legal_evidence_provider_coverage_verification_service.py` verifies exhaustive provider coverage; it does not establish orphan status or deletion authority.
- `tools/eos/legal_operations/orchestration/legal_evidence_provider_object_orphan_proof_orchestrator.py` remains a separate downstream authority boundary. Reconciliation output is not orphan proof, cleanup authorization, retention clearance, legal-hold clearance, or deletion authorization.

## Observed certification evidence

At commit `204e516364fec72f3cc08ce3660ba3ff134c9da0`, the focused GitHub Actions workflow completed:

- Python compilation: passed.
- Focused unit and real-Mongo tests: **116 passed in 5.10 seconds; zero skipped** (12 warnings were reported).
- The suite includes adversarial P5 workload-principal derivation, closed-world SYSTEM delegation policy, assignment/revocation command services, scope substitution and transaction failures, real-Mongo current permission possession, real-Mongo server-configured tenant currentness, and the **full gate** using the actual signed workload verifier, current P4/P2 authorities, current SYSTEM permission assignment, canonical tenant registry, and one caller-owned Mongo transaction.
- The full-gate real-Mongo success test commits the caller transaction and verifies P3 proof/currentness/replay/assurance evidence. A companion abort test proves those P3 writes and replay claims roll back when the caller aborts; the gate does not commit or abort.

This is focused certification, not full production certification. It does not invoke a production route or the provider adapter through the gate.

## Remaining blockers before runtime wiring

1. **Platform authorization audit/denial evidence:** no canonical platform-scoped durable authorization-decision/denial registry has been established for this internal operation. The tenant authorization decision registry is tenant-scoped and is not interchangeable with platform-root authority. Structured application logging alone is not durable authorization audit. Define/approve this contract before exposing the operation.
2. **Provider-boundary certification:** exercise the actual supported S3 adapter through the read-only coordinator under the authorized tenant/provider scope. Prove exhaustive coverage handling and that no provider mutation, cleanup, deletion, retention, or legal-hold authority is exposed. No provider I/O has been performed by the gate tests.
3. **Runtime composition root and invocation surface:** bind workload keys/audience, configured S3 target, canonical tenant collection, P5 authority, current permission resolver, scope resolver, and approved audit writer from trusted server configuration. Only after blockers 1–2 pass should the governed launch/system-command documentation select and authorize a specific internal invocation path. No route, CLI command, or scheduler is presently wired.

## Non-goals

This gate does not authorize provider deletion, retention modification, legal-hold release, automatic retries, orphan-proof issuance, or financial execution. Provider mutation remains outside the reconciliation capability.

## Exit criteria

Runtime wiring remains blocked until the platform audit/denial contract and provider read-only certification pass. The full-gate real-Mongo authorization and transaction boundary is now certified; missing audit/provider evidence is still a blocker, not a pass.

---
