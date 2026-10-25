# Legal Evidence Provider Read-Only Reconciliation — Runtime Gate

**Status:** RUNTIME WIRING BLOCKED — durable platform allow/deny evidence is integrated; focused real-Mongo audit and actual-adapter read-only composition tests pass; no production invocation is approved or wired  
**Version:** v1.2.2-L10A2R-C4D7C-PLATFORM-AUDIT-CERTIFIED  
**Date:** 2026-10-25  
**Implementation state reviewed:** `f74a9341083a8f910173c0302fb46f635cfbdf34`

## Decision

The first runtime invocation is intended for privileged internal operators only. It must be bound to one exact server-configured tenant and provider, remain read-only at the provider boundary, and preserve the caller-owned active Mongo transaction required by the reconciliation coordinator.

The reconciliation-specific authorization gate now persists a canonical platform-scoped ALLOW/DENY decision through an independently transactional Mongo audit registry before returning an authorization result or surfacing a denial. Audit persistence failure rejects authorization fail-closed. Focused real-Mongo tests and the actual S3 adapter through the authorized read-only composition have passed. No route, CLI command, scheduler, or production service entry point is connected. Runtime wiring remains blocked until the launch-governed invocation owner, deployment-owned audit-client/collection configuration, and final operational review are approved.

## Implemented authorization contract

- `tools/eos/auth/privileged_activation_use_authority.py` exposes `authorize_noninteractive_workload`. It composes the signed workload request once, requires the canonical `WorkloadTrustFact` to be current, validates P3 assurance identity before P4/P2 lookup, then checks current activation and exact P2 eligibility lineage in the caller-owned transaction.
- `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_authorization_gate.py` requires the exact `SOVEREIGN_ARCHITECT` / `PLATFORM_SYSTEM_ROOT` activation with activation `tenant_id=None`, current possession of `legal_operations:evidence_provider_reconciliation:read`, and a provider-bound server-owned scope resolver. Request header fields are exact-allowlisted; request-selected tenant/provider fields are rejected.
- `build_server_configured_reconciliation_target` binds the deployment tenant from `WILSY_LEGAL_EVIDENCE_RECONCILIATION_TENANT_ID` to the existing validated S3 configuration. It uses `WILSY_LEGAL_EVIDENCE_S3_BUCKET`, the existing region default/override, and optional `WILSY_LEGAL_EVIDENCE_S3_KMS_KEY_ID`. The resulting resolver rereads the fixed tenant through canonical `TenantRegistry.get` with the same session and derives the SHA3-512 tenant-scope fingerprint itself.
- This configuration supports **one server-configured tenant/provider target per resolver instance**. Multi-tenant batch selection is not implemented and must not be added as caller-supplied scope.
- `tools/eos/auth/system_permission_command_policy.py` permits exactly three ongoing non-command SYSTEM permissions: `privileged_activation:issue`, `privileged_activation:break_glass`, and `legal_operations:evidence_provider_reconciliation:read`. Assignment and revocation remain subject to the existing command-possession, ACTIVE-target, evidence, lineage, and caller-transaction contracts. Assignment of the read permission alone does not authorize use; the reconciliation gate independently requires P5 platform-root use.

## Existing reconciliation boundaries retained

- `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_provider.py` is a strict four-operation facade around the configured adapter and does not dynamically forward adapter attributes. `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_factory.py` requires the exact facade type before assembling services; construction does not establish identity or authorization.
- `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_coordinator.py` requires an already-active caller-owned transaction and rejects missing/incomplete coverage, source drift, and invalid evidence. It does not start, commit, abort, or retry transactions.
- `tools/eos/legal_operations/service/legal_evidence_provider_coverage_verification_service.py` verifies exhaustive provider coverage; it does not establish orphan status or deletion authority.
- `tools/eos/legal_operations/orchestration/legal_evidence_provider_object_orphan_proof_orchestrator.py` remains a separate downstream authority boundary. Reconciliation output is not orphan proof, cleanup authorization, retention clearance, legal-hold clearance, or deletion authorization.

## Observed certification evidence

At commit `204e516364fec72f3cc08ce3660ba3ff134c9da0`, the focused GitHub Actions workflow completed:

- Python compilation: passed.
- Focused unit and real-Mongo tests: **116 passed in 5.46 seconds; zero skipped** (12 warnings were reported).
- The suite includes adversarial P5 workload-principal derivation, closed-world SYSTEM delegation policy, assignment/revocation command services, scope substitution and transaction failures, real-Mongo current permission possession, real-Mongo server-configured tenant currentness, and the **full gate** using the actual signed workload verifier, current P4/P2 authorities, current SYSTEM permission assignment, canonical tenant registry, and one caller-owned Mongo transaction.
- The full-gate real-Mongo success test commits the caller transaction and verifies P3 proof/currentness/replay/assurance evidence. A companion abort test proves those P3 writes and replay claims roll back when the caller aborts; the gate does not commit or abort. Factory tests now require the explicit mutation-hiding facade and assert no adapter upload/delete methods are exposed and construction performs no provider calls.

This is focused certification, not full production certification. It does not invoke a production route or the provider adapter through the gate.

## Current certification and launch-governance reassessment

At commit `f74a9341083a8f910173c0302fb46f635cfbdf34`, the focused GitHub Actions run completed successfully:

- Run: [40179284634](https://github.com/Mawilis/legal-doc-system/actions/runs/40179284634).
- Python compilation and the focused Python/real-Mongo suite passed: **142 passed, 20 warnings in 7.10 seconds**; the zero-skip enforcement step passed.
- Real-Mongo audit tests proved denial evidence survives caller transaction abort, allow/deny evidence uses an independently owned audit transaction, replay returns the original evidence, conflicting idempotency/decision identities reject, unique indexes are present, and audit-store failure fails closed.
- The full authorization gate now writes ALLOW/DENY evidence before returning/raising. An allow record is not operation-completion evidence.
- Provider-boundary tests use the actual `LegalEvidenceS3StorageAdapter` behind the four-operation facade and authorized coordinator composition. Successful reconciliation invokes only provider enumeration reads; authorization failure causes zero provider calls; upload/complete/abort methods are not exposed through the facade.
- Twenty warnings remain; this run is not warning-free. The broader unified pipeline has a separate security-audit failure and is not fully green.

## Launch-governance decision

The launch command system requires an authenticated, observable API and treats the launch date as a target, not permission to bypass certification. The current runtime gate documentation and repository surface do **not** identify an already-approved route, CLI command, scheduler, or production service entry point for this reconciliation operation. Therefore no production invocation path can be honestly called approved today, and none is being wired in this delivery.

Before runtime wiring, the owner must approve and document:
1. The exact internal invocation surface and transport-derived signed workload request boundary.
2. Deployment-owned configuration for the audit Mongo client, collection, credentials/permissions, index provisioning, retention and operational monitoring.
3. The composition root that constructs the real audit registry and gate; the caller must not be able to substitute a no-op or alternate audit writer.
4. The invocation's active caller-owned transaction lifecycle, rollback behavior, idempotency handling, and observable audit-store outage response.
5. A final focused and broader certification against that exact invocation composition.

The current constructor requires a decision-evidence registry dependency and the gate persists a decision before returning. This does not by itself establish that a production composition root supplies the canonical registry; that binding must be proved when the governed invocation surface is selected.

## Non-goals

This gate does not authorize provider deletion, retention modification, legal-hold release, automatic retries, orphan-proof issuance, or financial execution. Provider mutation remains outside the reconciliation capability.

## Exit criteria

Runtime wiring remains blocked pending explicit approval of the invocation surface and its production composition root. The focused platform-audit and actual-provider-boundary tests pass, but they do not authorize a route, CLI command, scheduler, or production service entry point.

---
