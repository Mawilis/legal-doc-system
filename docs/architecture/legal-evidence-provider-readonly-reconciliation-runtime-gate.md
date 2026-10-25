# Legal Evidence Provider Read-Only Reconciliation — Runtime Gate

**Status:** RUNTIME WIRING BLOCKED — governed authorization gate and focused certification exist; platform audit and full-gate integration remain outstanding  
**Version:** v1.1.0-L10A2R-C4D7C-SERVER-OWNED-AUTHORIZATION-GATE  
**Date:** 2026-10-25  
**Implementation state reviewed:** `093e198f395bc8441d5fc721d042246d18918185`

## Decision

The first runtime invocation is intended for privileged internal operators only. It must be bound to one exact server-configured tenant and provider, remain read-only at the provider boundary, and preserve the caller-owned active Mongo transaction required by the reconciliation coordinator.

The authorization layer now exists as a separately testable gate. No route, CLI command, scheduler, or production service entry point is connected. Do not connect one until the full P5/P3/permission/scope composition has real-Mongo certification and the canonical platform-scoped authorization audit/denial path is established.

## Implemented authorization contract

- `tools/eos/auth/privileged_activation_use_authority.py` exposes `authorize_noninteractive_workload`. It composes the signed workload request once, requires the canonical `WorkloadTrustFact` to be current, validates P3 assurance identity before P4/P2 lookup, then checks current activation and exact P2 eligibility lineage in the caller-owned transaction.
- `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_authorization_gate.py` requires the exact `SOVEREIGN_ARCHITECT` / `PLATFORM_SYSTEM_ROOT` activation with activation `tenant_id=None`, current possession of `legal_operations:evidence_provider_reconciliation:read`, and a provider-bound server-owned scope resolver. Request header fields are exact-allowlisted; request-selected tenant/provider fields are rejected.
- `build_server_configured_reconciliation_target` binds the deployment tenant from `WILSY_LEGAL_EVIDENCE_RECONCILIATION_TENANT_ID` to the existing validated S3 configuration. It uses `WILSY_LEGAL_EVIDENCE_S3_BUCKET`, the existing region default/override, and optional `WILSY_LEGAL_EVIDENCE_S3_KMS_KEY_ID`. The resulting resolver rereads the fixed tenant through canonical `TenantRegistry.get` with the same session and derives the SHA3-512 tenant-scope fingerprint itself.
- This configuration supports **one server-configured tenant/provider target per resolver instance**. Multi-tenant batch selection is not implemented and must not be added as caller-supplied scope.
- `tools/eos/auth/system_permission_command_policy.py` now permits exactly three ongoing non-command SYSTEM permissions: `privileged_activation:issue`, `privileged_activation:break_glass`, and `legal_operations:evidence_provider_reconciliation:read`. Assignment and revocation remain subject to the existing command-possession, ACTIVE-target, evidence, lineage, and caller-transaction contracts. Assignment of the read permission alone does not authorize use; the reconciliation gate independently requires P5 platform-root use.

## Existing reconciliation boundaries retained

- `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_factory.py` assembles read-only dependencies from an explicitly supplied provider and Mongo database; it does not establish identity or authorization.
- `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_coordinator.py` requires an already-active caller-owned transaction and rejects missing/incomplete coverage, source drift, and invalid evidence. It does not start, commit, abort, or retry transactions.
- `tools/eos/legal_operations/service/legal_evidence_provider_coverage_verification_service.py` verifies exhaustive provider coverage; it does not establish orphan status or deletion authority.
- `tools/eos/legal_operations/orchestration/legal_evidence_provider_object_orphan_proof_orchestrator.py` remains a separate downstream authority boundary. Reconciliation output is not orphan proof, cleanup authorization, retention clearance, legal-hold clearance, or deletion authorization.

## Observed certification evidence

At commit `093e198f395bc8441d5fc721d042246d18918185`, the focused GitHub Actions workflow completed:

- Python compilation: passed.
- Focused unit and real-Mongo tests: **114 passed in 4.43 seconds; zero skipped**.
- The run includes adversarial tests for the P5 workload-principal derivation, closed-world SYSTEM delegation policy, assignment/revocation command services, gate scope substitution and transaction failures, current SYSTEM permission possession against real Mongo, and server-configured tenant currentness/transaction visibility against a real Mongo replica set.

This evidence is not a full production certification. The real-Mongo tests exercise permission possession and scope resolution as components; they do **not** yet exercise the entire P3 → P5 → current permission → scope gate with the actual signed workload verifier and all persisted authorities in one transaction. They do not execute the provider adapter through a production entry point.

## Remaining blockers before runtime wiring

1. **Full-gate real-Mongo integration:** construct the actual noninteractive workload trust verifier, proof/evidence registries, P4/P2 authorities, SYSTEM permission registry, canonical tenant registry, and gate in one caller-owned transaction. Prove identity mismatch, stale/revoked activation, missing/revoked permission, inactive tenant, transaction abort, and no gate-owned commit/retry.
2. **Platform authorization audit/denial evidence:** no canonical platform-scoped durable authorization-decision/denial registry has been established for this internal operation. The tenant authorization decision registry is tenant-scoped and is not interchangeable with platform-root authority. Structured application logging alone is not a durable authorization audit.
3. **Runtime composition root:** bind the server workload keys/audience, configured S3 target, canonical tenant collection, P5 authority, permission resolver, and scope resolver from trusted server configuration. Do not accept tenant/provider coordinates from a request.
4. **Provider-boundary certification:** exercise the actual supported adapter through the read-only coordinator and prove no provider mutation, cleanup, deletion, retention, or legal-hold authority is exposed.
5. **Invocation surface:** only after items 1–4 pass should the governed launch/system-command documentation select and authorize a specific internal invocation path. No route, CLI command, or scheduler is presently wired.

## Non-goals

This gate does not authorize provider deletion, retention modification, legal-hold release, automatic retries, orphan-proof issuance, or financial execution. Provider mutation remains outside the reconciliation capability.

## Exit criteria

Runtime wiring remains blocked until full-gate real-Mongo evidence, the platform audit/denial contract, server-owned provider/tenant configuration, and provider read-only certification are observed passing. Missing evidence is a blocker, not a pass.

---
