# EOS mounted-router and execution-entrypoint discovery — tranche 6

**Repository:** `Mawilis/legal-doc-system`  
**Branch:** `eos/tenant-discovery-iam-dashboard-roadmap`  
**Audit basis:** source tree at commit `8a5180c982484a43c02dc941041b153593ab94fc`, plus this tranche's source reads  
**Status:** mounted-router inventory and selected dependency closure; not a complete permission contract  
**Production mutation:** none

## 1. Canonical API composition root

The canonical FastAPI composition root is `tools/eos/api/server.py`. The router imports and mount declarations were read directly.

| Router | Mount | Source closure status |
|---|---|---|
| `kernel_routes` | root and `/api` (two mounts) | route source uses application/kernel boundary; transitive command execution dependencies still open |
| `router.py` direct/router | root | telemetry/dashboard/engine/runtime/repository/artifact/event/history/report/documentation and execution/scheduler/governance/compatibility surfaces; complete source closure open |
| `tenant_router` | root | module has no directly declared route decorators in inspected source; determine imported/re-exported router behavior |
| `legal_operations_router` | `/api` | many read surfaces, including lifecycle, deputy, sheriff, location and conflict views; transitive registry mapping incomplete |
| `owner_commercial_workspace_router` | `/api` | work-item create/complete; registry plus entitlement current/history collections; router invokes registry index ensure method |
| `legal_operations_command_router` | `/api` | intake, directory, allocation, attempt, transition, device, location, conflict, notification, return and completion commands; dynamic collection resolver; full action matrix open |
| `authorization_role_revocation_router` | `/api` | role-revocation command; dynamic collection resolver; full registry action matrix open |
| `legal_operations_billing_read_router` | `/api` | read-only tariff assessment, eligibility, client invoice and issuance reads |
| `legal_matter_deadline_router` | `/api` | deadline create/list/read and deadline-intelligence; dynamic registry resolution |
| `legal_client_acceptance_router` | `/api` | acceptance instruments, issuance/content and acceptance commands; dynamic collection resolver |
| `legal_evidence_upload_router` | `/api` | six upload registries plus lifecycle, subscription and entitlement dependencies; prior tranche |
| `legal_evidence_provider_readonly_reconciliation_router` | `/api` | signed internal workload ingress, business transaction, separate audit client, idempotency evidence; prior audit |
| `tenant_legal_operating_model_router` | `/api` | tenant operating-model read/create through one registry |
| `legal_practitioner_matter_binding_router` | `/api` | access/binding/conflict evidence, IAM and provisioning; prior tranche |
| `legal_storefront_public_intent_router` | `/api` | anonymous pre-tenant intent plus atomic rate-limit admission |
| `wilsy_ai_legal_gateway_router` | `/api` | entitlement, usage, legal lifecycle, tariff, eligibility, invoices, issuance and legal-tool invocation collections |
| `wilsy_ai_reasoning_router` | `/api` | tenant entitlement/admission/model invocation/usage evidence; prior tranche |
| `wilsy_ai_legal_services_router` | `/api` | entitlement and usage plus server-owned orchestrator |
| `wilsy_ai_advisory_router` | `/api` | create/read next-action advisory; service is composed in app state; transitive persistence still open |
| `legal_acceptance_router` | `/api` | legal document and acceptance collections |
| `tenant_branding_router` | `/api` | profile, selection, current projection, assets and entitlement dependencies |
| `telemetry_ingestion_router` | `/api` | append to `wilsy_sovereign_telemetry` |
| `subscription_router` | root | module contains no directly declared route decorators in inspected source; determine imported/re-exported router behavior |
| `plan_router` | root | module contains no directly declared route decorators in inspected source; determine imported/re-exported router behavior |
| `auth_router` | `/api` | legacy auth, recovery, MFA/3FA, discovery, workspace and branding dependencies; multiple registry index ensure calls |
| `global_principal_auth_router` | `/api` | global credentials, membership, MFA and sessions; prior audit |
| `system_services_router` | `/api` | case/event queue and transitions; prior audit |
| `billing_router` | root and `/api` (two mounts) | invoices, payments, billing intelligence, dunning and audit; legacy billing registry and kernel DB binding |
| `employee_router` | root | employee search and exact employee read; delegates to employee registry |
| `authority_bridge_router` | root | internal-service trust, replay, workload credential, privileged proof/currentness and identity/membership/role evidence; caller-owned transaction |
| `payshap_webhook_router` | root | signed provider evidence, execution attempts/commands, provider observations, AP/platform financial truth and Kennel reconciliation in one caller transaction |
| `hr_document_router` | root | tenant-authorized streaming HR binary upload, document metadata, uncertainty and reconciliation evidence; S3 separate from Mongo |

The billing router is mounted twice. Kernel routes are mounted twice. These are deliberate composition facts to preserve while checking route collisions and middleware/dependency behavior; they are not separate workloads or separate database identities.

## 2. New cross-cutting findings

### 2.1 API startup still owns substantial index DDL

The startup block in `server.py` calls index creation/ensure methods for:
- global principal credentials and membership-selection challenges;
- global sessions/refresh tokens and MFA factors/enrollment;
- principal authentication rate limits;
- tenant authorization decision evidence and role-revocation evidence;
- privileged factor currentness, internal-service replay/workload credentials, privileged workload trust, noninteractive proofs and assurance evidence;
- deputy bindings and process-service location permission/observation/revocation/access-audit collections;
- Legal Storefront intents and rate limits;
- practitioner/matter access, binding and conflict-disposition evidence;
- C1C AI orchestration (when provider composition is available).

It also directly creates the unique sparse telemetry `trace_id` index. Other startup-owned index families exist in earlier audits. The candidate API role therefore cannot yet be reduced to only request CRUD rights. The complete DDL inventory and a non-mutating parity verifier are prerequisites to removing startup DDL safely.

### 2.2 Legacy auth router also creates indexes at route composition

The legacy auth router invokes `ensure_indexes()` for recovery contacts, capabilities, rate limiting and verification registries at multiple composition points. This must be included in the DDL extraction; moving only `server.py` calls would not eliminate runtime index creation.

### 2.3 Billing dunning is not transactionally atomic

The daily scheduler remains embedded in `server.py` and calls `evaluate_all_tenant_dunning_lifecycles()` from the API billing router. It runs daily at 00:15 Africa/Johannesburg when `WILSY_DUNNING_SCHEDULER_ENABLED` is true; the default is disabled in production and enabled outside production unless overridden.

The evaluator:
1. derives tenant IDs from `platform_invoices` using `distinct` on `tenant_id` and `tenantId`;
2. reads tenant platform invoices and dunning policy;
3. reads current `billing_dunning_states`;
4. writes state with `update_one(upsert=True)`;
5. updates matching `subscriptions` with `update_many`;
6. inserts `billing_audit_events`;
7. emits telemetry.

The transition's writes do not pass a Mongo session through this evaluator. A crash after one write can leave dunning state, subscription posture and audit evidence inconsistent. The evaluator also runs sequentially across tenants and returns aggregate results.

**Do not simply move this function into a new process.** The worker extraction must first introduce a caller-owned transaction spanning the state compare-and-set, subscription projection and audit event, with idempotent replay and an explicit unknown-commit strategy. Add a durable per-tenant evaluation claim/lease or another concurrency fence so two worker instances cannot race the same transition. Only then give a separately deployed dunning worker the narrowly scoped write authority. API routes should retain only the permissions needed by their own policy/state reads and any explicitly approved command route.

### 2.4 Billing routes are not one uniform write capability

The billing router contains commercial invoice/payment and audit operations, but its source explicitly rejects HTTP attempts to establish paid state, refunds, partial settlement and payment execution. Kennel EOS owns financial execution/settlement truth. The eventual Mongo role must reflect the actual reachable billing operations and avoid broad settlement mutation assumptions.

### 2.5 PayShap and internal authority bridge are transaction-sensitive

PayShap route authenticates the provider message, resolves exactly one tenant/command-correlated attempt, persists provider evidence and composes canonical financial execution reconciliation inside one caller-owned Mongo transaction. It does not itself establish settlement.

The internal authority bridge authenticates service trust first, then composes replay/workload proof/currentness evidence and only after that current human identity, tenant membership and authorization. Its request path has no index DDL. Its persistence requirements are not interchangeable with the PayShap webhook or ordinary API role.

## 3. HR document persistence and object storage

The HR document route is a streaming upload path with bounded queue and worker execution. It uses:
- `hr_documents`: append-only tenant/employee/document/version metadata;
- `hr_document_commit_uncertainties`: append-only provider-complete/Mongo-unproven evidence;
- `hr_document_commit_reconciliation_outcomes`: append-only terminal reconciliation outcome.

Exact source indexes for all three collections were added to the index manifest in commit `268f2181e99dcd74211f4d063d73b406084b8088`.

The HR S3 adapter derives object keys under `hr-documents/v1/t/<tenant digest>/e/<employee digest>/d/<document digest>/v/<version digest>/i/<ingestion digest>/content`. It performs multipart upload, part upload, completion, object inspection and abort. This is a distinct HR storage policy, separate from Legal Evidence's bucket/adapter. Exact bucket and KMS configuration and AWS identity remain unverified. Do not assume both products use the same S3 bucket, prefix or role.

The HR commit-reconciliation service explicitly requires a caller-owned active transaction and does not own provider I/O, deletion, retention or disposal. The complete invocation/cleanup owner is still unresolved. No deletion authority should be inferred from the word "cleanup".

## 4. Operator, migration and background entrypoint discovery

The repository tree identifies the following EOS operator/migration entrypoints:
- `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_audit_provisioner.py`: dedicated separate audit Mongo client; creates/validates only the platform decision evidence audit indexes.
- `tools/eos/saas/auth/migrations/reconcile_legacy_principal_authority.py`: explicit CLI migration; shared kernel DB binding; session transaction; exact principal authority reconciliation.
- `tools/eos/saas/auth/migrations/reconcile_legacy_super_admin_tenant.py`: explicit CLI; exact tenant/principal preflight, transaction, targeted user tenant update and principal-scoped session/refresh-token deletion.
- `tools/eos/saas/auth/migrations/refresh_token_indexes.py`: dedicated index migration/provisioning entrypoint; exact caller-controlled create-index boundary.
- `tools/eos/saas/auth/migrations/refresh_token_tenant_backfill.py`: migration module; direct invocation and mutation details still need source review.
- `tools/eos/saas/billing/migrations/tenant_inbound_merchant_configuration_lifecycle_idempotency_projection.py`: scans and updates projection rows, then creates unique partial index.
- `tools/eos/saas/billing/migrations/tenant_inbound_provider_credential_security_authority_index_migration.py`: scans source facts and creates indexes for fact/pointer collections.
- `tools/eos/saas/billing/reconcile_wilsy_founder_legal_entitlement.py`: CLI connecting through kernel DB; reads subscription/plan/current entitlement and performs governed reconciliation.
- `tools/eos/auth/global_principal_mfa_legacy_migration_service.py`: service-level migration; invocation and deployment principal need separate identification.
- `tools/eos/auth/principal_credential_migration_assessment.py`: assessment module; no mutation authority should be presumed.
- `tools/eos/auth/developer_persona_provisioner.py`, `principal_authority_provisioning.py`, `tenant_owner_genesis_provisioning.py`, `tools/eos/cloud/tenancy/tenant_provisioner.py`: provisioning services/entrypoints to classify by exact invocation and persistence.
- `tools/eos/automation/scheduler.py`, `tools/eos/runtime/scheduler.py`, `tools/eos/runtime/worker.py`, `tools/eos/cluster/application/scheduler.py`, `tools/eos/distributed/cluster_scheduler.py`, `tools/eos/run_scheduler_playbook.py`: scheduler/worker framework modules. Their presence in the tree is not evidence they are deployed or that they run dunning.
- Legal Evidence cleanup authorization/command registries and cleanup classification/discovery services exist. Their presence does not establish an active cleanup worker or deletion permission.

Legacy Node `server/scripts/*` migrations and retention workers also exist in the repository. They are a separate runtime family from the dedicated Python EOS API and must not be silently assigned the EOS runtime MongoDB identity.

This is a source-tree inventory, not proof that any of these entrypoints are deployed, scheduled, or used in production. For each one, finish the caller/CI/manual invocation, target database, collection/action, transaction, and credential-source matrix.

## 5. Manifest update

`infra/mongodb/eos-index-manifest-v1.json` now includes source-declared HR indexes for:
- `hr_documents`;
- `hr_document_commit_uncertainties`;
- `hr_document_commit_reconciliation_outcomes`.

Commit: `268f2181e99dcd74211f4d063d73b406084b8088`.

The manifest remains `INVENTORY_INCOMPLETE`, non-executable, and explicitly disallows production mutation. It does not yet include all API, authentication, billing, Kennel, tenant, operator, migration, worker and provisioning index families.

## 6. Next engineering sequence

1. Finish per-router transitive repository/action closure, including dynamic registry factories and router modules with no local decorators.
2. Inventory every `ensure_indexes` / `create_index` call across API composition, imported routers, constructors and CLIs; compare exact options to manifest.
3. Complete HR and Legal Evidence object-store IAM contracts separately, including retention/disposal and multipart lifecycle owners.
4. Extract dunning into a separate process only after transactional CAS, subscription projection, audit, idempotency and multi-worker fencing are certified.
5. Build a dedicated non-production provisioner with read-only plan/diff mode, duplicate-data preflight, exact target fingerprint check, explicit apply approval, post-apply index verification and safe failure reporting.
6. Move runtime index DDL to the provisioner; make API startup perform read-only verification and fail readiness if required indexes are absent/divergent.
7. Create separate candidate identities for API, dunning worker, legal evidence/HR storage workloads where independently deployed, migration operator, index provisioner and CI test.
8. Validate each candidate with representative positive and denied Mongo commands, transaction behavior, TTL/index options, network restrictions and cloud-object operations against an explicitly verified non-production target.

**NO-GO:** no production credential, MongoDB role/user, network entry, cloud identity, S3 policy, KMS key, deployment or production data has been changed. The target non-production Atlas cluster and its runtime secret reference have not yet been proven to be the EOS test target.
