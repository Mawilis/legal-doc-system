# WILSY OS Python EOS Backend Retirement and Dependency Audit

**TITLE:** Python EOS Backend Retirement and Dependency Audit
**VERSION:** v1.0.2-PYTHON-EOS-RETIREMENT-DEPENDENCY-AUDIT
**AUTHORITY:** Wilsy OS Core Governance
**EPITOME:** Records the dependency, source-owner, evidence-preservation, runtime, governance-marker, and certification findings for the Python EOS consolidation.
**ABSOLUTE CANONICAL PATH:** `/Users/wilsonkhanyezi/legal-doc-system/docs/architecture/python-eos-backend-retirement-dependency-audit-2026-11-10.md`
**COLLABORATION / OWNERSHIP:** Python EOS, authentication, billing, workspace, client, repository-integrity, and release owners.
**CERTIFICATION / UPDATE DATE:** 2026-11-10
**CHANGELOG:** v1.0.2-PYTHON-EOS-RETIREMENT-DEPENDENCY-AUDIT adds the root/nested governance and index-state findings to the independently verified Git-blob inventory, corrects local test evidence, and distinguishes local evidence from exact-head hosted certification.
**COMPLIANCE:** AGENTS.md v1.2.0; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
**SECURITY / PRIVACY POSTURE:** Repository metadata and synthetic test data only; no production records, signing secrets, or private keys were read.
**TENANT BOUNDARY:** This report grants no cross-tenant, membership, Legal, billing, or audit write authority.
**AUTHORITY BOUNDARY:** Repository/runtime evidence only. Python EOS is the sole supported application and authorization runtime.
**FINANCIAL AUTHORITY BOUNDARY:** Kennel EOS exclusively owns financial execution and settlement.

## 1. Scope and conclusion

The candidate comparison against baseline `2c9a807849f9596040c4c6aee9435d66f68d40f2` contains **1,499 deleted paths**. Every deleted path is classified `RETIRED_NODE_BACKEND` by the repository-surface policy. No deleted path belongs to `tools/eos/`, `docs/evidence/`, or `docs/trust/`; no migration path or scanned key, certificate, or signature artifact was deleted. `server/manifest.txt`, `server/scripts/rollback-migration-production.patch`, and the historical runtime inventory are preserved.

This is a bounded source and dependency audit, not a claim that every archived Node route has Python parity. Route families with no mounted Python owner remain unavailable or explicitly identified below. No production deployment, database migration, live key read, or key rotation was performed.

## 2. Sovereign-file audit and classified inventory

The canonical Mac repository's 6,580 tracked paths were independently enumerated from Git trees and their contents read from Git blobs. The scan found 3,364 tracked Python blobs: 1,946 production-source files, 1,391 tests, and 27 active-governance files. Applying the full mandatory-header, current-changelog, canonical-path, matching-version, and sovereign-end-seal contract identified **2,787 confirmed legacy violations**: 1,656 production-source, 1,109 test, and 22 active-governance files. A narrower header-field-only scan found 2,350 files missing at least one field. The preliminary 2,094 estimate is not reproduced under either independently applied criterion and remains preliminary, not a confirmed count.

The canonical tree contains only the root AGENTS.md contract and no nested AGENTS.md; no tracked paths were missing and no special Git index flags were present at inspection. No tracked Python findings were classified as generated output, retained historical evidence, or legitimate exclusion. The repository guard separately excludes generated lock/build/cache outputs and named immutable historical material. Historical evidence and migrations were inspected as preservation targets, not rewritten to improve the marker count.

The current consolidation artifacts were checked from Git blobs by the changed-artifact guard. New or modified applicable files must carry a complete sovereign header, current changelog entry, canonical path, ownership, security/privacy, tenant and authority posture, financial boundary, and terminal end seal with matching version. The guard also validates the full repository path policy and Git snapshot. It is not a marker-only check.

Remediation priority is bounded: **P0** keep the changed/new-file guard mandatory and repair any changed applicable artifact before integration; **P1** remediate production and active governance legacy files by touched domain during future governed work; **P2** remediate tests as their owning suites are maintained. Do not mass-rewrite the 2,787 legacy files. Retained evidence and migration history are excluded from churn.

## 3. Deletion and preservation evidence

| Audit subject | Evidence | Result |
|---|---|---|
| Deleted paths | Git comparison to baseline: 1,499 paths | All classify `RETIRED_NODE_BACKEND`; zero are Python EOS source. |
| Runtime trees | `server/`, root `services/`, `client/server/`, `middleware/`, `models/`, and `algorithms/` | Retired executable backend code, manifests, launchers, and backend-only dependencies are removed. |
| Python dependencies | Deleted-path scan under `tools/eos/` | Zero. Kernel DB, registries, routers, schedulers, workers, and domain owners remain. |
| Migrations | Deleted-path scan and named-retention policy | Zero deleted migrations. Thirteen historical Node migration/rollback/verification scripts and all six inventoried Python migration modules remain. No migration was run. |
| Audit and trust evidence | Deleted-path scans under `docs/evidence/`, `docs/trust/`, and scanned key/certificate/signature suffixes | Zero deleted artifacts. The manifest, rollback patch, and historical runtime inventory remain unchanged. |
| Package and launch surface | Root package and Vite/dev launcher inspection | Node remains client build/test tooling. Development serves Python EOS at 9095 and Vite at 5173. |
| Git history | Existing PR branches and local merge ancestry | No reset, rebase, force-push, or squash is used. The PR #409 history is integrated as a normal merge parent into the existing PR #410 branch. |

Retained Node migration history: `server/scripts/finalize-migration.js`, `migrate-audit-legacy.js`, `migrate-case-legacy.js`, `migrate-documents-tenancy.js`, `migrate-fixed.js`, `migrate.js`; `server/scripts/migration/DocumentMigrationEngine.js`, `MigrationLogger.js`, and `MigrationRunner.js`; and the named rollback and verification scripts. Active Python migration owners include four authentication modules and two inbound-billing configuration/security modules.

## 4. Runtime relationship map

```text
React / Vite client (:5173)
  └─ /api proxy → Python FastAPI composition (:9095)
       ├─ Global Principal and tenant authentication
       │    └─ canonical identity, membership, MFA, session, and tenant authorization
       ├─ Tenant and tenant-module workspace routes
       │    └─ authenticated tenant scope and tenant-owned projections/actions
       ├─ My Work and Daily Attention routes
       │    └─ source-owned projections; display grants no assignment or completion authority
       ├─ Legal Operations routes
       │    └─ Python registries, commands, evidence, and tenant authorization
       ├─ Billing, subscription, invoice, audit-read, and QR routes
       │    └─ Python registries; Kennel EOS remains execution/settlement authority
       └─ Kernel DB, schedulers, and opt-in Python workers
            └─ canonical persistence and worker ownership
```

No frontend module imports the retired Node backend trees. `tools/eos/api/server.py` composes the Python API. The Vite proxy uses the loopback EOS target on port 9095; the browser client avoids duplicating an `/api` prefix already present in its base URL.

### Connection matrix

| Dimension | Current owner and relationship |
|---|---|
| Direct imports / exports | `server.py` composes Python routers. `billing_router.py` consumes authenticated tenant context, billing registries, and `invoice_qr_legacy_contract.py`. `ForensicProofBlock.jsx` uses the authenticated API client. Daily Attention consumes My Work and attention projections. |
| Routes / HTTP surface | Auth: `/api/auth/*`, `/api/auth/global/*`; My Work and attention: `/api/my-work`, `/api/attention/{feed,counts,calendar,sources/health}`; invoice QR issue: `/api/billing/invoices/{invoice_id}/qr`; QR verify: `/api/qr/verify/{encoded_payload}`. Each is mounted once under `/api`. |
| Models / collections | QR reads tenant-owned `client_invoices` only and validates tenant aliases. Audit views read `billing_audit_events` and `billing_integrity_controls`. Platform invoices are not collapsed into client invoices. QR performs no invoice or audit-state mutation. |
| Metrics / telemetry | QR adds no counter, label, or telemetry event. Existing telemetry is Python-owned. No Node metrics registry is retained as an application runtime. |
| Shared crypto | QR preserves legacy JSON field order and SHA3-512 of `payload_json + "|" + configured_secret`; signature comparisons are timing-safe. This compatibility signature is not PKI, payment, legal validity, execution, or settlement proof. |
| Config / environment | QR uses only existing `QR_SIGNING_SECRET` or `QR_SECRET` and `QR_VERIFICATION_BASE_URL`; missing/invalid configuration fails closed. EOS port is 9095; Vite is 5173. No key rotation or new fallback is introduced. |
| UI / hooks | Daily Attention is mounted in the authenticated application and connected to EOS. TMS shows lifecycle availability without global controls. Audit integrity values are read-only. Billing proof UI obtains QR issue/verify responses through authenticated transport. |
| Latency-sensitive chains | QR issue: authenticate → derive tenant from server authorization context → tenant-scoped invoice read → compare persisted identity/amount/currency/trace → sign legacy envelope → respond. Verify: authenticate → validate signature/expiry → enforce signed tenant before DB access → exact tenant-scoped invoice query → compare persisted fields → respond. No open transaction or write is introduced. |

## 5. Source-owned actions and authority decisions

| Action | Python owner / proof | Boundary |
|---|---|---|
| Global principal login, membership, MFA, session currentness | Global Principal/auth routers, registries, and startup tests | Python owns identity and authorization truth; browser roles and JWT claims do not replace server authorization. |
| Tenant-scoped workspace | Tenant and tenant-module routers plus authenticated tenant context | Own-tenant work remains available. Global list/create/suspend remain disabled until a governed Python EOS C2 capability exists. |
| Billing and audit | Billing/subscription registries, invoice and audit routes | `auto_renew`, `encrypted_backup`, and `neural_sync` are read-only. `audit:read`, SUPER_ADMIN, and `X-Tenant-ID` do not grant write authority. |
| Legacy invoice QR | Python compatibility contract and authenticated billing routes | Exact tenant-scoped client-invoice payload/signature contract is retained with fixed-vector, tamper, missing-config, and isolation tests. No platform-invoice or statement QR parity is claimed. |
| Daily Attention / My Work | Unified My Work and attention routers and projections | Read projections do not create assignment, completion, permission, or matter authority. |
| Legal work and evidence | Python Legal Operations routers, registries, commands, and evidence owners | Retired Node paths are not authority or fallback implementations. |
| CRM | Owner-commercial Python workspace | This is not full parity for historical CRM command/live/intelligence calls. Those client calls are not certified operational; a Python-owned route or unavailable projection remains required. |
| FICA/onboarding | No mounted Python FICA owner was found | Deleted legacy code contained placeholder/provider and fabricated-score behavior; no screening fact or compliance result is claimed as migrated. |
| Execution and settlement | Kennel EOS and Python settlement/evidence owners | UI, authorization, approval, or provider attempts do not become execution or settlement truth. |

The QR implementation preserves the historical envelope and fails closed without configured secrets/base URL. Its tests certify a synthetic compatibility vector and tenant/tamper boundaries, not production key custody or historical production records. Legacy QR verification-state mutation and offline reconciliation remain disabled until a governed write capability and append-only idempotent evidence contract exist.

## 6. Policy and certification-check changes

`production_surface_policy.json` remains schema version 1 with `default: UNCLASSIFIED`. It removes retired root/backend names from the active allowlist, classifies removed Node backend paths as retired, preserves exact retained rules for the manifest, rollback patch, migration history, and governance evidence, and keeps `tools/eos/**` sovereign.

The Python runtime certification tests now assert physical removal of retired backend trees/manifests, retained Python API/database/worker ownership, preserved migration and audit artifacts, and retired-path classifications. QR owner/contract coverage and tenant boundaries are checked. The repository-integrity workflow remains active and fails on changed Git-blob contract violations; it validates canonical path and metadata content in addition to surface classification.

## 7. Verification evidence

| Gate | Exact local evidence |
|---|---|
| Changed-blob repository guard | Passed against candidate Git index snapshot after validating the modified artifact set. Exact committed-head workflow is reported separately. |
| Python governance and focused retirement/auth tests | 82 passed after integrating the PR #409 test changes; tenant-module route/transport suite: 13 passed. |
| Python syntax and Pyright | All 17 changed Python files compiled; Pyright reported 0 errors, 0 warnings, 0 informations. |
| Full Python unit suite | 16,831 passed, 52 failed, 1 skipped. All 52 failing node IDs also fail on clean canonical HEAD, where 16,773 passed, 56 failed, 1 skipped; candidate-only failures: zero, and four canonical failures pass on candidate. This is not a green full-suite certificate. |
| Full client suite | 93 files passed, 791 tests passed. |
| Client build and source secret scan | Build passed (3,070 modules; warnings only). Secret guard passed after inspecting 474 source files. |
| Real Mongo | 15 passed, 0 skipped on disposable local replica set `wilsyVendorCertRS`; no production database was used. |
| Authenticated application browser | Daily Attention desktop/mobile 2/2; critical system authentication/scope checks 4/4; broad authenticated L8-8M suite 32/32. Local browser evidence is separate from hosted CI. |
| PR #409 exact head | Existing PR #409 head `e360f3c824c28cd12327dd0f9a4d49eadfc744db`: all 19 triggered workflows completed successfully. |
| PR #410 exact head | Pending publication of the integrated candidate. No exact-head hosted result is claimed in this report until GitHub completes the candidate workflows. |

The Python full-suite failures are a pre-existing baseline condition, not new candidate failures. They remain a merge-readiness consideration if a required protected check runs the entire suite. No unrelated historical source was changed to mask that baseline.

## 8. Remaining priorities

| Priority | Required action | Surface |
|---|---|---|
| P0 | Publish the integrated candidate to the existing PR #410 branch and inspect every required exact-head workflow. | PR #410 |
| P0 | Keep global tenant list/create/suspend unavailable until an explicit governed Python EOS C2 capability exists. | TMS and tenant lifecycle routes |
| P0 | Keep audit-integrity controls read-only until a governed write capability and command exist. | Audit UI and billing-integrity API |
| P1 | Reconcile historical CRM calls with Python-owned routes or truthful unavailable states. | CRM client and EOS API |
| P1 | Certify production QR secret custody and historical records before activation. | Billing QR |
| P1 | Govern any QR verification-state persistence or offline reconciliation before implementation. | Billing evidence and scheduler boundary |
| P2 | Remediate legacy sovereign-header violations by touched domain; do not mass-rewrite. | Production source, governance, then tests |

## POST-UPDATE TODO — after `python-eos-backend-retirement-dependency-audit-2026-11-10.md` `v1.0.2-PYTHON-EOS-RETIREMENT-DEPENDENCY-AUDIT`

|  | Action | File / surface | Why (blast radius) | Priority | Done? |
|---|---|---|---|---|---|
| 1 | Publish the integrated candidate to existing PR #410 and verify all exact-head required workflows. | PR #410 | The candidate is not merge-certified until hosted checks cover its exact commit. | P0 | [ ] |
| 2 | Keep cross-tenant tenant lifecycle commands unavailable pending governed C2 capability. | `/api/tenants/*`; TMS | Prevents UI roles or legacy permissions from becoming cross-tenant authority. | P0 | [x] |
| 3 | Keep integrity controls read-only pending governed write capability. | `/api/billing/audit/integrity`; Audit UI | `audit:read` cannot authorize persisted integrity-control mutation. | P0 | [x] |
| 4 | Govern QR verification-state persistence, statement QR, and offline reconciliation before activation. | Billing QR and audit evidence | Prevents ungoverned writes, key fallbacks, or scheduler-owned reconciliation. | P1 | [x] |
| 5 | Reconcile historical CRM calls with Python-owned routes or truthful unavailable projections. | CRM client; `/api/crm/*` | The owner-commercial workspace is not broad CRM route parity. | P1 | [ ] |
| 6 | Certify production QR key/configuration and historical records before activation. | QR environment and authenticated billing routes | Synthetic vectors do not prove production key custody or record compatibility. | P1 | [ ] |
| 7 | Remediate legacy source/test markers by domain without mass churn. | Changed-file governance and later touched domains | Preserves history and avoids marker-only rewrites while preventing new violations. | P1/P2 | [ ] |

## Certification score

**9/10.** Local runtime and bounded integration evidence is recorded. The full Python suite remains baseline-red, and exact-head PR #410 hosted checks and governed merge review are not yet complete. No production deployment or production QR activation is authorized by this report.

---

**ARTIFACT:** Python EOS Backend Retirement and Dependency Audit
**VERSION:** v1.0.2-PYTHON-EOS-RETIREMENT-DEPENDENCY-AUDIT
**AUTHORITY BOUNDARY:** Repository dependency, governance, and local runtime evidence only.
**TENANT POSTURE:** No cross-tenant authority or live tenant access.
**FAIL-CLOSED POSTURE:** Unknown parity, missing configuration, and ungoverned authority remain unavailable.
**FINANCIAL EXECUTION AUTHORITY:** Kennel EOS exclusively.
**END OF WILSY OS SOVEREIGN ARTIFACT**
