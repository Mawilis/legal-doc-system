# Legal Evidence Provider Read-Only Reconciliation — Runtime Gate

**Status:** RUNTIME WIRING BLOCKED — durable platform allow/deny evidence and provider-boundary certification pass; the existing generic runtime API is not a safe reconciliation invocation surface  
**Version:** v1.4.2-L10A2R-C4D7C-155-PASS-IDEMPOTENCY-OPEN-UNIFIED-GATE-FAILED  
**Date:** 2026-10-25  
**Implementation state reviewed:** `6dfb97b3e70205bc98a06463a1e8210c30313f7d`

## Decision

The first runtime invocation is intended for privileged internal operators only. It must be bound to one exact server-configured tenant and provider, remain read-only at the provider boundary, and preserve the caller-owned active Mongo transaction required by the reconciliation coordinator.

The reconciliation-specific authorization gate now persists a canonical platform-scoped ALLOW/DENY decision through an independently transactional Mongo audit registry before returning an authorization result or surfacing a denial. Audit persistence failure rejects authorization fail-closed. Focused real-Mongo tests and the actual S3 adapter through the authorized read-only composition have passed. A generic runtime API exists, but source inspection found it is not an approved or safe invocation surface for this privileged operation. Runtime wiring remains blocked until the invocation owner, deployment-owned audit-client/collection configuration, and final operational review are approved.

## Implemented authorization contract

- `tools/eos/auth/privileged_activation_use_authority.py` exposes `authorize_noninteractive_workload`. It composes the signed workload request once, requires the canonical `WorkloadTrustFact` to be current, validates P3 assurance identity before P4/P2 lookup, then checks current activation and exact P2 eligibility lineage in the caller-owned transaction.
- `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_authorization_gate.py` (v1.0.7) requires the exact `SOVEREIGN_ARCHITECT` / `PLATFORM_SYSTEM_ROOT` activation with activation `tenant_id=None`, current possession of `legal_operations:evidence_provider_reconciliation:read`, and a provider-bound server-owned scope resolver. Request header fields are exact-allowlisted; request-selected tenant/provider fields are rejected.
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

At commit `2a0652ead7e48fb6db63586ba3a0ee8cf05cde1f`, the focused GitHub Actions run completed successfully:

- Run: [40179540830](https://github.com/Mawilis/legal-doc-system/actions/runs/40179540830).
- Python compilation and the focused Python/real-Mongo suite passed: **142 passed, 20 warnings in 6.93 seconds**; the zero-skip enforcement step passed.
- Real-Mongo audit tests proved denial evidence survives caller transaction abort, allow/deny evidence uses an independently owned audit transaction, replay returns the original evidence, conflicting idempotency/decision identities reject, unique indexes are present, and audit-store failure fails closed.
- The audit registry commits its independent transaction with MongoDB `writeConcern=majority`; the gate records only verified actor/authority facts established before a downstream denial, while pre-verification failures remain explicitly unverified.
- The full authorization gate now writes ALLOW/DENY evidence before returning/raising. An allow record is not operation-completion evidence.
- Provider-boundary tests use the actual `LegalEvidenceS3StorageAdapter` behind the four-operation facade and authorized coordinator composition. Successful reconciliation invokes only provider enumeration reads; authorization failure causes zero provider calls; upload/complete/abort methods are not exposed through the facade.
- Twenty warnings remain; this run is not warning-free. The broader unified pipeline has a separate security-audit failure and is not fully green.

## Existing runtime surface assessment (read-only repository inspection)

The current Python runtime has `tools/eos/runtime/app.py` mounting `tools/eos/runtime/router.py` under `/runtime`. That is a real existing API surface, but it is **not suitable for reconciliation wiring as currently implemented**:

- `POST /runtime/execute` accepts generic caller-provided `input_data` and optional `context`; the handler does not declare an authorization dependency or invoke the reconciliation-specific signed-workload authorization gate.
- The handler dynamically selects a kernel method from `boot_and_execute`, `execute`, `run`, `process`, `start`, or `bootstrap` using `find_execution_method`. This generic execution contract is not a bounded reconciliation command contract.
- The inspected application factory installs request-ID/logging middleware and CORS, but no authentication/authorization middleware is wired there. It configures `allow_origins=["*"]` together with `allow_credentials=True`; this is not evidence of an internal-only privileged boundary.
- Neither inspected file constructs the canonical platform decision-evidence registry, the reconciliation authorization gate, the server-configured tenant/provider resolver, or the caller-owned active Mongo session required by reconciliation.

These observations do not establish that every other WILSY route is unsafe; they establish that this existing generic route cannot be treated as the approved reconciliation invocation. Do not attach privileged reconciliation to `/runtime/execute` or rely on request-provided `context`, tenant, provider, or identity fields. A dedicated governed composition must obtain the signed workload context from a trusted transport boundary, inject deployment-owned audit and provider dependencies, and preserve the active caller-owned transaction.

## Certification on the current documentation commit

At commit `b38adc8b085593bde9fbf63062e9f7c1b17499e3`, GitHub Actions completed:

- Focused Python / isolated real-Mongo workflow: [run 40179900787](https://github.com/Mawilis/legal-doc-system/actions/runs/40179900787) — **142 passed, 20 warnings in 6.83 seconds**; Python compilation, Mongo replica-set initialization/cleanup, and zero-skip enforcement passed.
- Repository integrity: [run 40179900856](https://github.com/Mawilis/legal-doc-system/actions/runs/40179900856) — passed.
- Unified pipeline: [run 40179900706](https://github.com/Mawilis/legal-doc-system/actions/runs/40179900706) — failed at the security audit. The observed audit reported **24 production dependency vulnerabilities (2 moderate, 22 high)**; the pipeline's retained production-gates step consequently failed and downstream R2A/R2B real-Mongo jobs were skipped. This is a separate existing dependency/security gate, not a failure in the focused Python reconciliation tests. No Node.js or dependency changes were made as part of this Python/EOS task.

This improves the evidence for the current branch head but does not clear the launch blocker: the focused suite certifies the authorization/evidence components and provider-boundary tests, not a production invocation route.

## Certification on commit `5ce69c633c4a875c94c9d6d88906e52429f038cc`

The latest branch-head CI results have now completed:

- Focused Python / isolated real-Mongo authorization gate: [run 40180120093](https://github.com/Mawilis/legal-doc-system/actions/runs/40180120093) — **142 passed, 20 warnings in 6.75 seconds**. Python compilation, replica-set initialization and cleanup, and zero-skip enforcement all passed.
- Repository integrity: [run 40180120082](https://github.com/Mawilis/legal-doc-system/actions/runs/40180120082) — passed.
- Unified pipeline: [run 40180120085](https://github.com/Mawilis/legal-doc-system/actions/runs/40180120085) — failed at the security audit; the retained production-gates step failed and downstream R2A/R2B real-Mongo certification was skipped. This is not a focused reconciliation-suite failure and remains a separate production release blocker.
- EOS image publication: [run 40180120137](https://github.com/Mawilis/legal-doc-system/actions/runs/40180120137) — completed successfully.

The focused tests exercise the real signed workload verifier and current P5/P2/SYSTEM permission authorities against isolated MongoDB, verify the caller-owned transaction rollback boundary, and test the actual S3 adapter through the read-only facade. The focused suite is now confirmed green on the current commit, not inferred from a prior code commit. It does not certify a production HTTP/service invocation or deployment-owned audit-client composition.

## Dedicated production composition (implementation added; not runtime-enabled)

The branch now contains `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_production_composition.py` (v1.0.0). It composes the already-verified P5 use authority, current SYSTEM permission resolver, server-configured canonical tenant/provider target, validated S3 adapter behind the strict four-operation facade, coordinator, and platform decision-evidence registry.

Fail-closed composition rules:
- The business database and platform-audit database must be attached to distinct MongoClient instances; the supplied audit client must be the audit database's actual client.
- The composition does not silently create indexes or become ready at construction. A standalone deployment-only index provisioner uses its distinct deployment-owned MongoClient to create the required unique indexes. Runtime composition then verifies those indexes read-only through the runtime audit client; it does not retain deployment credentials or index-management authority. The deployment provisioner must target the same approved audit deployment/database.
- Authorization and reconciliation share the caller-owned active business session; the independent audit registry owns its separate client/session. The caller remains responsible for aborting the business transaction on failure.
- The signed workload fields must be extracted by an approved transport adapter from the actual incoming request. The composition does not register a route, trust caller-selected tenant/provider fields, or infer transport trust from a generic mapping.
- No S3 provider operation is performed during construction. Provider enumeration is reachable only through the read-only facade.

Focused unit coverage and the Python certification workflow were extended for the composition's not-ready guard, index-provisioning failure, and gate-derived scope propagation. This is a composition seam, not yet a production invocation path: the approved transport adapter, deployment identity/configuration, index-provisioning procedure and operational ownership still must be selected and wired before invocation can be enabled.

## Composition-focused certification on code commit `4b7919a4d5c05ca08bd5b6a44e0808664d209a2f`

- Focused Python / isolated real-Mongo workflow: [run 40180958680](https://github.com/Mawilis/legal-doc-system/actions/runs/40180958680) — **147 passed, 20 warnings in 7.48 seconds**. Python compilation, isolated replica-set setup/cleanup and zero-skip enforcement passed. Coverage includes the composition readiness/fail-closed tests and real-Mongo proof that runtime index verification accepts both required unique indexes and rejects a missing index.
- Repository integrity: [run 40180958779](https://github.com/Mawilis/legal-doc-system/actions/runs/40180958779) — passed.
- EOS image publication: [run 40180958710](https://github.com/Mawilis/legal-doc-system/actions/runs/40180958710) — passed.
- Unified production pipeline: [run 40180958700](https://github.com/Mawilis/legal-doc-system/actions/runs/40180958700) — failed at the existing production dependency security audit, reporting **24 vulnerabilities (2 moderate, 22 high)**. Retained production gates failed and downstream R2A/R2B real-Mongo jobs were skipped. No Node.js or dependency changes were made in this Python/EOS task. Focused success is not broader release certification.

The runtime composition verifies the two required unique audit indexes read-only during construction. The deployment-only index provisioner is separate and is not retained by the runtime composition, so the runtime audit client does not need index-management authority. This verifies index shape/existence, not that a deployment provisioner has been configured against the correct production cluster; that remains a deployment-owned configuration and release-governance obligation.

## Signed-workload transport extraction (not mounted)

The Python/EOS transport adapter now exists at
`tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_transport_adapter.py`.
It maps the already-existing signed internal-service header contract
(`X-Wilsy-Auth-Version`, `X-Wilsy-Service-ID`, `X-Wilsy-Audience`,
`X-Wilsy-Key-ID`, `X-Wilsy-Timestamp`, `X-Wilsy-Nonce`,
`X-Wilsy-Body-SHA3-512`, `X-Wilsy-Correlation-ID`,
`X-Wilsy-Signature`) into the canonical P3 request mapping. It derives the
HTTP method and raw origin-form path/query from the ASGI scope, reads the exact
body bytes, rejects missing/duplicate required headers, rejects malformed path
and header encoding, and does not accept identity, tenant, provider, or scope
from the request body or context. The signed correlation ID is preserved for audit correlation only. It is not
an operation idempotency key. The existing signed protocol has no dedicated
operation-idempotency field, so the invocation owner must approve a
protocol-compatible idempotency contract before runtime wiring; an unsigned
auxiliary header must not substitute for that contract.

The adapter only normalizes transport input. It does not verify the signature,
authorize the operation, create a Mongo session, start/commit/abort a
transaction, or mount a route. The canonical P3/P5/gate chain remains the sole
authorization path. Its focused adversarial tests are now included in the
reconciliation workflow's explicit compile and pytest command; certification
for the new adapter is pending the current-head workflow result.

This reduces the transport-mapping implementation gap but does not resolve
operational approval: the actual internal caller must still approve the exact
route/path and signed header contract, and the deployment composition owner
must supply the production dependencies and caller-owned transaction lifecycle.
Do not mount this adapter on the generic runtime endpoint or expose a route
until that approval and production wiring are independently evidenced.

## Launch-governance decision

The launch command system requires an authenticated, observable API and treats the launch date as a target, not permission to bypass certification. Repository inspection found a generic runtime API but no already-approved, reconciliation-specific route, CLI command, scheduler, or production service entry point. The generic `/runtime/execute` route is explicitly unsuitable under its current authorization and execution contract. Therefore no production invocation path can honestly be called approved today, and none is being wired in this delivery.

Before runtime wiring, the owner must approve and document:
1. The exact internal invocation surface and route/path agreement with the existing signed workload transport contract. A Python extraction adapter now exists, but no route is mounted and the actual internal caller has not yet been approved against it. The operation-idempotency contract must also be established; correlation IDs are not silently promoted to idempotency keys.
2. Deployment-owned configuration for the audit Mongo client, collection, credentials/permissions, index provisioning, retention and operational monitoring.
3. The composition root that constructs the real audit registry and gate; the caller must not be able to substitute a no-op or alternate audit writer.
4. The invocation's active caller-owned transaction lifecycle, rollback behavior, idempotency handling, and observable audit-store outage response.
5. A final focused and broader certification against that exact invocation composition.

The current constructor requires a decision-evidence registry dependency and the gate persists a decision before returning. This does not by itself establish that a production composition root supplies the canonical registry; that binding must be proved when the governed invocation surface is selected.

## Non-goals

This gate does not authorize provider deletion, retention modification, legal-hold release, automatic retries, orphan-proof issuance, or financial execution. Provider mutation remains outside the reconciliation capability.

## Exit criteria

Runtime wiring remains blocked pending explicit approval of a dedicated invocation surface and its production composition root. The focused platform-audit and actual-provider-boundary tests pass, but they do not authorize attaching this operation to the generic runtime endpoint or otherwise create production invocation authority.

---
