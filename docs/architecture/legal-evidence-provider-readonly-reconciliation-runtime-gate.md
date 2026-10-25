# Legal Evidence Provider Read-Only Reconciliation — Runtime Gate

**Status:** RUNTIME WIRING BLOCKED — durable platform allow/deny evidence and provider-boundary certification pass; the existing generic runtime API is not a safe reconciliation invocation surface  
**Version:** v1.4.3-L10A2R-C4D7C-SOVEREIGN-COMPOSITION-155-PASS-UNIFIED-GATE-FAILED  
**Date:** 2026-10-25  
**Implementation state reviewed:** `323c6189ec21799bf4227bdefbe757db8bccaea0`

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

## Signed-workload transport and canonical invocation

The Python/EOS transport adapter extracts the existing signed internal-service
header contract from the actual ASGI scope, preserves exact body bytes, binds
method and raw path/query, and rejects missing/duplicate required headers or
malformed encoding. It accepts no caller-selected identity, tenant, provider,
or scope. Signature verification, current workload proof, P5 activation,
SYSTEM permission possession, server-owned scope, and durable authorization
evidence remain in the canonical authority chain.

The canonical EOS server mounts the dedicated route at
`POST /api/legal-operations/evidence-provider/reconciliation`. The route's
strict body contract is a UTF-8 JSON object containing exactly
`idempotency_key`. The key is not taken from an unsigned header, and signed
correlation remains correlation only. The composition requires a fresh signed
nonce per attempt, reauthorizes every attempt, and stores/replays the exact
bounded result under authenticated service ID plus operation key in the same
caller-owned business transaction. Changed body or server-resolved scope under
the same key conflicts rather than overwriting the cached result.

The existing generic signer in `server/services/pythonAuthorityTransport.js`
can sign an exact path/body, but repository search has not identified a
reconciliation-specific caller invocation. No Node/JavaScript change is made
under the Python/EOS-only boundary. The service owner must approve and wire the
actual caller to this exact route and body contract before production launch.

## Latest governed state — 2026-10-25

At code head `323c6189ec21799bf4227bdefbe757db8bccaea0`:

- Focused Python and isolated real-Mongo certification [40186415809](https://github.com/Mawilis/legal-doc-system/actions/runs/40186415809): **155 passed, 20 warnings in 7.70 seconds; zero skipped**. Python compilation, replica-set initialization/cleanup, and zero-skip enforcement passed.
- Repository integrity [40186415826](https://github.com/Mawilis/legal-doc-system/actions/runs/40186415826): passed.
- EOS image publication [40186415805](https://github.com/Mawilis/legal-doc-system/actions/runs/40186415805): passed.
- Unified production pipeline [40186416007](https://github.com/Mawilis/legal-doc-system/actions/runs/40186416007): failed at `npm audit --omit=dev --audit-level=high`. The observed production dependency report remains **24 vulnerabilities (2 moderate, 22 high)**. The broader install audit reported 26 total (1 low, 4 moderate, 21 high). Reported production packages include `body-parser` (high), `ip-address` (moderate), `multer` (high), `nodemailer` (moderate), `undici` (high), and `zod` (high, including a web3 dependency chain). The report identifies normal fixes for some packages and breaking-range fixes for others. No Node/JavaScript or dependency edits were made in this Python/EOS task. Retained production gates failed; downstream R2A/R2B real-Mongo jobs were skipped.
- The production composition source now carries the mandatory sovereign header and matching end seal at version `v1.0.1-L10A2R-C4D7C-SOVEREIGN-COMPOSITION-SEAL`. This structural governance correction does not change runtime behavior and passed the current focused workflow.
- The current focused run certifies the authorization/evidence/provider composition and adversarial transport adapter tests. It does **not** certify a mounted production route, an approved caller, or a production audit deployment.

### Production closure remains blocked

1. **Actual caller approval:** the signed path and operation-key protocol are implemented, but no reconciliation-specific call site was found in the repository. The owning service must approve and connect its actual caller to the exact route; do not infer that generic signer availability proves a caller is wired.
2. **Deployment audit target:** deployment must set `WILSY_LEGAL_EVIDENCE_RECONCILIATION_AUDIT_MONGODB_URI` to the approved separate audit target and run the deployment-only provisioner using that same environment variable. Runtime verifies the unique audit indexes read-only and rejects a business target that resolves to the same host/database. No production target/secret is available to this code-edit session, so target provisioning and parity remain unobserved.
3. **Current-head certification:** the focused workflow now includes the route, canonical server bootstrap, audit provisioner, idempotency registry and adversarial unit tests. The older 155-test result does not certify these new changes. The latest exact-head focused + isolated real-Mongo run must pass with zero skips.
4. **Unified security release gate:** the previously observed production dependency audit reported 24 vulnerabilities (2 moderate, 22 high). This Python/EOS task does not change Node/JavaScript dependencies; the owning dependency/security workflow must remediate and rerun that gate. No bypass is acceptable.
5. **Operational launch sign-off:** after the above, certify the actual caller over HTTP against isolated real Mongo, verify commit/abort/replay and audit durability, rerun the unified production gate, and obtain operational approval.

The canonical EOS startup now constructs and injects the real composition only
when all required authority and deployment configuration is present. Missing
configuration leaves the route at a fail-closed 503. This is a deliberate
safety posture, not evidence that production configuration has been supplied.

## Dedicated HTTP invocation and deployment bootstrap — implemented, not launch-certified

The Python route is mounted only by the canonical `WilsyAPIServer` in
`tools/eos/api/server.py` at `POST /api/legal-operations/evidence-provider/reconciliation`. The canonical
server startup now builds the composition from existing P2/P4/P5/SYSTEM
authorities, the canonical business Mongo database, the existing internal
workload trust configuration, and a separately configured audit Mongo client.
It retains and closes the audit client with the application lifecycle. If
configuration or composition fails, the application logs only a stable error
code and the route remains fail-closed with 503.

The runtime requires `WILSY_LEGAL_EVIDENCE_RECONCILIATION_AUDIT_MONGODB_URI`.
That URI must resolve to a different Mongo target (host/database) from
`MONGODB_URI`. Runtime startup never provisions platform decision-audit
indexes; it verifies them read-only. An authorized deployment operator must run
`python -m tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_audit_provisioner`
with both URIs set to provision and verify the required unique indexes. The
provisioner and runtime share the exact audit-URI environment contract and both
reject a target identical to the business host/database. No URI or credential
is logged.

The operation body is strict UTF-8 JSON with exactly one property:
`{"idempotency_key":"<1-160 permitted characters>"}`. Duplicate properties,
additional fields, wildcard characters, invalid encoding, and invalid keys are
rejected. The exact body bytes are bound by the existing signed
`X-Wilsy-Body-SHA3-512` protocol. Each attempt must have a fresh signed nonce;
correlation remains audit correlation, never operation idempotency. The
idempotency ledger uses authenticated service ID plus operation key, stores a
bounded summary in the same caller-owned business transaction, replays the
exact prior response for matching signed body and server-resolved scope, and
rejects key reuse with different request/scope material. Authorization is
re-evaluated on every retry before the stored result can be replayed.

The actual route/path is therefore fixed and code-mounted. Repository discovery
found the existing generic internal transport signer in
`server/services/pythonAuthorityTransport.js`, but did not establish a
reconciliation-specific caller invocation against this path. No Node/JavaScript
caller change is included, consistent with the Python/EOS-only implementation
boundary. Until the service owner approves and wires the actual caller to this
exact path and body contract, caller approval remains an explicit release gate.

The focused workflow now compiles the canonical `server.py`, the secondary
`api_server.py`, the runtime bootstrap, the audit provisioner, and the
idempotency registry, and includes the corresponding unit tests. No current-head
workflow result has yet been observed. The previously observed unified
production dependency audit failure remains an independent release blocker.

## Non-goals

This gate does not authorize provider deletion, retention modification, legal-hold release, automatic retries, orphan-proof issuance, or financial execution. Provider mutation remains outside the reconciliation capability.

## Exit criteria

Production launch remains blocked pending (a) an approved actual caller invocation of the exact mounted route/body contract, (b) deployment execution of the audit provisioner against the approved target and verification of runtime target parity, (c) current-head focused and real-Mongo certification, and (d) clearance of the unified production dependency audit. The generic runtime endpoint remains prohibited.

---
