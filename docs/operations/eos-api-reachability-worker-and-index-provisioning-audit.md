# EOS API reachability, worker and index provisioning audit — tranche 4

**Branch:** `eos/tenant-discovery-iam-dashboard-roadmap`  
**Status:** source-level partial inventory; not a complete role contract  
**Production changes:** none

## 1. System Services case and event persistence — resolved

Source chain:
`tools/eos/api/server.py` -> `tools/eos/api/system_services_router.py` -> `tools/eos/system_services/support_case_service.py` -> `tools/eos/system_services/support_case_registry.py`.

Collections: `system_service_cases`, `system_service_case_events`.

Case operations: `find_one` exact identity/scope and replay lookup; bounded `find`; `insert_one`; revision/status CAS `replace_one` with `upsert=False`.

Event operations: `find_one` replay lookup; bounded ordered `find`; `insert_one` for create and transition. No update/delete operation is exposed by this registry. Events are append-only.

Routes:
- `GET /api/system-services/workspace-bootstrap`: bounded SYSTEM queue read; optional identity-read permission check for capability projection.
- `GET /api/system-services/cases`: bounded queue read, requires `system_services:queue:read`.
- `GET /api/system-services/cases/{case_id}/events`: exact SYSTEM case history, requires `system_services:identity:read`.
- `POST /api/system-services/cases/{case_id}/transition`: current case read, revision-guarded case replace and event insert, requires `system_services:case:triage`.

Each request starts a Mongo session and transaction. The application service independently calls the injected current SYSTEM authorizer. The registry requires an active caller-owned transaction for writes.

The same service exposes tenant self-service methods (`create_own_case`, `list_own_cases`, `read_own_case_history`), but the inspected mounted SYSTEM router does not expose those tenant routes. Do not grant tenant case write permissions to the SYSTEM API merely because the service supports them.

Startup currently calls `SupportCaseRegistry.ensure_indexes()` directly from `server.py`; the API process therefore performs index DDL.

## 2. Dunning scheduler — embedded in API process, not an independent worker

The scheduler is defined inside the API composition root. `WILSY_DUNNING_SCHEDULER_ENABLED` controls activation; its default is disabled in production and enabled outside production unless overridden. It runs daily at 00:15 Africa/Johannesburg and invokes `evaluate_all_tenant_dunning_lifecycles()`. Shutdown cancels the asyncio task.

The scheduler calls the same billing-router implementation as `POST /dunning/evaluate`. It enumerates `platform_invoices` using `distinct("tenant_id")` and `distinct("tenantId")`, then accesses:

| Collection | Operations observed |
|---|---|
| `platform_invoices` | `distinct`, `find` |
| `billing_dunning_policies` | `find_one`, `update_one` with `upsert=True` |
| `billing_dunning_states` | `find_one`, `find`, `update_one` with `upsert=True` |
| `subscriptions` | `update_many` |
| `billing_audit_events` | `insert_one` |

The policy update route also writes an audit event. Dunning transitions call the telemetry helper. The scheduler has no independent database client or credential: it uses the billing router's shared kernel database binding. Its effective database permissions are therefore currently inseparable from the API process. A separate scheduler identity requires extracting the task into a separately deployable worker and defining its own exact collection/action contract.

## 3. Separate Legal Evidence reconciliation audit persistence — clarified

### 3.1 Platform decision evidence audit database

- Collection: `platform_authorization_decision_evidence`.
- Registry: `tools/eos/auth/platform_authorization_decision_evidence_registry.py`.
- Operations: `find_one` and `insert_one` inside a separate audit-client session/transaction; duplicate-key recovery performs exact `find_one` reads outside the failed transaction.
- Indexes: unique `idempotency_key` and unique `decision_id`.
- Runtime composition verifies these indexes read-only.
- Existing deployment-only command: `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_audit_provisioner.py`. It uses `WILSY_LEGAL_EVIDENCE_RECONCILIATION_AUDIT_MONGODB_URI`, requires a distinct business deployment and TLS, provisions the two audit indexes, verifies them, and prints only target fingerprint/database name (URI redacted).

### 3.2 Business database operation idempotency

- Collection: `legal_evidence_provider_reconciliation_operations`.
- Operations: `find_one`, `insert_one` inside the caller-owned business transaction.
- Index: unique `service_id, idempotency_key`.
- This is the canonical business database, not the separate platform audit database.

### 3.3 Runtime startup still performs business-side DDL

The reconciliation runtime builder currently calls `ensure_indexes()` on five business-database registries: platform privileged eligibility prerequisite, privileged eligibility evidence, System Permission assignment, privileged activation, and reconciliation operation idempotency. These calls are on the API startup path. They must be migrated to the general business index provisioning contract or separately justified. The independent audit provisioner does not provision these five business collections.

## 4. Versioned index inventory and provisioning gate

Added:
- `infra/mongodb/eos-index-manifest-v1.json`
- `.github/workflows/eos-mongodb-index-provisioning-gate.yml`

The manifest records verified specifications for System Services cases/events, telemetry trace, Legal Storefront public-intent rate limiting, reconciliation business-operation idempotency, and independent platform authorization audit indexes. The public-intent rate lookup index is **not unique**; the manifest reflects the source.

The GitHub Actions workflow is a non-mutating validation gate. It opens no MongoDB connection and creates/modifies no index. The manifest is marked `INVENTORY_INCOMPLETE`, so an apply stage is deliberately unavailable. The existing dedicated audit provisioner remains separate.

Before an apply stage exists, require: complete source/route/worker inventory; exact index option parity; duplicate-data and existing-index preflight; approved non-production target fingerprint; separate provisioner credentials and environment approval; post-provision verification; and rollback/recovery plan.

## 5. Remaining route, worker and CLI gaps

- The dunning scheduler is the only in-process scheduler positively identified in the inspected server composition; its shared API database identity is not isolated.
- CLI/operator/migration entrypoints importing `tools.eos.kernel.db` must be classified individually; import count does not prove deployed commands or required permissions.
- Legacy MFA source collection and migration-only identity remain unresolved.
- Legal Evidence upload/capacity/usage/cleanup registries need an end-to-end action matrix.
- All mounted routers need route-level dependency and repository closure, not only import/mount enumeration.
- AI orchestration indexes depend on configured reasoning-provider state.
- Moving index DDL out of startup must retain fail-closed readiness: routes cannot become ready until provisioned indexes are verified read-only.

## Decision

The System Services case/event contract is source-verified. The in-process dunning scheduler and its shared API database identity are now identified. The two reconciliation persistence targets are distinguished. The initial manifest and workflow are intentionally non-mutating and incomplete.

**NO-GO** remains for production role changes, index application, credential rotation or Atlas network changes. No production resources or secrets were modified.


## 6. CLI migration identity — explicit principal reconciliation utility

The repository contains `tools/eos/saas/auth/migrations/reconcile_legacy_super_admin_tenant.py`. It is an operator-invoked CLI, not a request handler or worker. It calls `kernel_db.connect_db()`, obtains the shared configured database/client, and disconnects in `finally`.

Exact collections and operations:
- `tenants`: `find` for exact canonical tenant and legacy pseudo-tenant validation.
- `users`: `find` exact ObjectId + legacy/canonical tenant; `update_one` exact ObjectId + old tenant predicate to change only `tenantId`.
- `sessions`: `find` principal-scoped preflight; `delete_many` exact `user_id` during confirmed execution.
- `refresh_tokens`: `find` principal-scoped preflight; `delete_many` exact `user_id` during confirmed execution.

Dry-run performs reads only. Mutation requires explicit old/new tenant confirmation and a Mongo transaction. The operation revokes only that principal's sessions and refresh tokens. This CLI therefore requires a separately governed migration/operator identity with tightly scoped write/delete rights, not the normal API role. The current source uses the same kernel URI authority unless the CLI environment is separately configured; the deployed operator credential boundary is not yet proven.

The source uses a legacy auth data model (`users`, `sessions`, `refresh_tokens`, `tenants`) distinct from the global-principal collections. Do not merge those grants into the EOS global-identity runtime role.

## 7. Scheduler transaction and isolation risk

The dunning evaluator performs sequential collection writes directly through the shared billing database helper. In the inspected function, no caller-owned Mongo session is opened or passed through those reads/writes. A failure between the state update, subscription update, audit insert and telemetry emission may therefore leave a partially applied lifecycle transition. This is both an identity-isolation issue and a consistency/certification issue; extract and transactionally redesign it before granting an independent scheduler role.

