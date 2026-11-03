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


## 7. Additional route-to-registry closure from the next source pass

The following modules were followed from mounted router through their directly constructed service/orchestrator and registry dependencies. They are now classified more precisely than the initial router-name inventory.

| Router / route family | Durable collections and transitive repositories | Operations / authority notes |
|---|---|---|
| `legal_acceptance_router` | `legal_documents`, `legal_client_acceptances` | Service composes document read and append-only acceptance write; document registry also exposes approved/current document selection. Authenticated identity; no corporate execution/payment authority. |
| `legal_client_acceptance_router` | `legal_operations_lifecycle_evidence`, `legal_operations_client_matter_visibility_bindings`, `legal_matter_parties`, `legal_client_acting_capacities`, `legal_client_matter_acceptance_instruments`, `legal_client_matter_acceptance_instrument_contents`, `legal_client_matter_acceptance_instrument_lifecycle`, `legal_client_matter_acceptance_instrument_approvals`, `legal_client_acceptance_contexts`, `legal_client_acceptances`, plus tenant authorization evidence and IAM principal/membership/role repositories | Four route concerns: actionable instrument projection, instrument provisioning, content delivery, context composition and acceptance issuance. Router owns one caller Mongo transaction and passes exact session to orchestration/registries. Append-only evidence and immutable instrument/content facts; lifecycle/context operations must be scoped by tenant and matter. |
| `legal_matter_deadline_router` | `legal_operations_lifecycle_evidence`, `legal_matter_deadlines` | Create/list/detail and deterministic intelligence read. Exact tenant authorization. One caller transaction per route; telemetry is bounded logging, not a durable collection in this router. |
| `legal_operations_billing_read_router` | tariff assessment collection, process-service billing eligibility collection, `client_invoices`, `issuance` | GET-only read projection; no invoice issuance, payment or settlement writes. Client business-role projection is explicitly denied pending a separate client policy. |
| `tenant_legal_operating_model_router` | `legal_tenant_operating_models`, plus IAM principal, membership, business-role and role-assignment repositories | Read current revision and append/configure revision under caller transaction. Operating-model configuration is not entitlement or IAM authority. |
| `legal_storefront_public_intent_router` | `legal_storefront_public_intents`, `legal_storefront_public_intent_rate_limits` | Anonymous pre-tenant POST only. Atomic rate admission is a distinct operation; intent persistence is in caller-owned transaction. No tenant/principal/billing authority is created. |
| `authorization_role_revocation_router` | `authorization_role_revocation_evidence`, `tenant_authorization_decision_evidence`, principal authority, role assignments, tenant business roles and tenant memberships | One caller transaction. Reauthorization, replay protection, target currentness, role-assignment CAS and revocation evidence are command-owned. Root roles are outside ordinary revocation. |
| `owner_commercial_workspace_router` | `owner_commercial_work_items`, `tenant_product_entitlement_current`, `tenant_product_entitlement_history`, subscription registry collection | Queue read, create and complete. Router currently calls `ensure_indexes` inside request transaction setup; this is another runtime DDL site to move to the provisioner. Subscription and product entitlement are read-side admission dependencies, not authority to mutate billing. |
| `tenant_branding_router` | branding profile, selection, asset and entitlement current/history registries; principal authority, tenant membership, business role and role assignment repositories | Authenticated tenant-scoped profile/asset writes and projections. Asset bytes are bounded in the route; this is not a global asset-storage or tenant-independent role. Exact per-registry indexes and any external object store need a separate source closure. |

**Collection-name rule:** the table names constants as exposed by the imported registry modules where the source pass confirmed them. For the deadline, billing tariff/eligibility and branding registry families, the manifest must use the registry module's canonical constant and exact index declaration—not a guessed collection name. The exact names/options for those remaining families are not marked complete by this table.

## 8. Operator/worker invocation matrix — invocation proof separated from code presence

| Entrypoint / process family | Invocation evidence found | Target/identity status | Decision |
|---|---|---|---|
| API-hosted dunning scheduler | Explicit task creation in `server.py`, env flag and daily clock schedule | Same API kernel Mongo client; no separate workload identity | Must extract only after transaction and concurrency redesign |
| Legal Evidence audit index provisioner | Explicit CLI `main`; dedicated audit URI environment variable; separate audit client | Separate audit DB identity is architecturally required; actual deployed secret/identity not proven | Keep separate; only its two audit indexes are in scope |
| Legacy principal-authority reconciliation | CLI module and `__main__` path; kernel DB connection | Shared configured kernel URI unless separately injected; deployed operator credential unproven | Human migration identity, not API |
| Legacy super-admin tenant reconciliation | CLI module and `__main__` path; explicit preflight/confirmation/transaction | Shared configured kernel URI unless separately injected; deployed operator credential unproven | Human migration identity, tightly targeted update/delete |
| Refresh-token index migration | CLI module; index creation path | Exact invocation and deployed credential not proven | Separate index-provisioner identity |
| Refresh-token tenant backfill | Migration module exists; direct executable entrypoint not confirmed in inspected source | Unknown | Do not assign mutation role until caller and operations verified |
| Merchant-configuration lifecycle idempotency projection migration | Migration module has scan/update/create-index logic | Direct runner and target credential not confirmed | Separate migration/provisioning phases; do not run from API |
| Provider-credential security authority index migration | Migration module exists in source tree | Direct runner/target credential not confirmed | Source closure remains open |
| Founder legal entitlement reconciliation | CLI and kernel DB binding | Deployed identity not proven | Human-governed migration/reconciliation role |
| HR commit reconciliation service | Caller-owned transaction service, no autonomous scheduler found | Invoker/worker owner not proven | No independent worker identity or cleanup rights inferred |
| Legal Evidence cleanup authorization/command services | Authorization and command domains/registries found; no active worker schedule established | No deployment or object-delete caller proven | No delete permission inferred |
| Generic EOS scheduler/worker frameworks | Framework modules present in source tree | No evidence they run dunning, HR reconciliation or Legal Evidence cleanup | Not deployment evidence |
| Legacy Node scheduler/retention/migration scripts | Separate Node runtime tree | Separate legacy DB/config boundary not proven equivalent to Python EOS | Do not share EOS runtime identity |

The matrix intentionally distinguishes **code exists**, **direct CLI is executable**, **scheduler is wired**, and **deployed invocation is proven**. Only the dunning scheduler is directly wired into the API host in the reviewed Python composition root. The other service/framework presence must not be mistaken for a running production worker.

## 9. Dunning transaction redesign — prepared contract, not yet implemented

Current evaluator has the following unsafe sequence without one shared Mongo session: read policy/invoices/state; upsert dunning state; update matching subscription documents; insert audit event; emit telemetry. Two concurrent evaluators can read the same old state and independently write duplicate or divergent transitions. A crash can persist only a prefix of the transition.

Proposed transition contract:

1. **Stable evaluation identity:** derive a deterministic idempotency key from tenant, subscription, invoice, target state and policy revision/fingerprint. Do not use the evaluation timestamp as the identity.
2. **Claim/fence:** atomically claim a tenant+subscription evaluation lease with owner token, lease expiry and monotonic fencing revision. Expired leases may be reclaimed only with a strictly higher fencing revision.
3. **Snapshot and compare:** read invoice, policy revision, dunning state revision and subscription correlation inside the transaction. Revalidate invoice is still overdue/unpaid and policy still current.
4. **CAS state transition:** update only when expected state/revision still matches; set new state, transition key, proof hash and incremented revision. Never use blind upsert for a transition after the canonical state row is established.
5. **Subscription projection:** update only the exact tenant+subscription identity, requiring a matched canonical subscription and an expected prior projection/revision. No broad tenant update.
6. **Audit:** append exactly one immutable `billing_audit_events` transition with the same idempotency key and proof hash, under the same Mongo session/transaction.
7. **Commit uncertainty:** on unknown commit result, do not blindly repeat writes. Resolve by exact idempotency key/transition ID from a fresh primary read; return a reconciliation-required state if evidence is incomplete.
8. **Telemetry:** emit only after a confirmed commit; telemetry failure cannot roll back or fabricate a business transition.
9. **Dry-run:** same read/derivation path, no lease, state, subscription or audit writes.
10. **Worker boundary:** standalone worker gets only invoice/policy/state reads, claim/CAS state writes, exact subscription projection writes and append-only audit writes. API command route receives its own explicitly approved narrower scope. Index DDL and KMS/S3 rights are not part of the worker role.

Before worker deployment, add replica-set tests for simultaneous evaluators, expired lease/fencing, stale state revision, paid invoice racing evaluation, policy revision racing evaluation, subscription missing/divergent, duplicate audit prevention, transaction abort after each write boundary, unknown commit recovery, dry-run read-only behavior, and two-worker concurrency.

No dunning source code was changed in this tranche. The contract is a design input for a separately reviewed implementation.

## 10. Provisioning harness execution and remaining blockers

Existing `tools/eos/mongodb/index_provisioning_harness.py` is deliberately non-mutating:
- validates manifest schema and unique collection/index declarations;
- requires explicit `nonproduction` target and matching approved/observed opaque fingerprints for `--plan`;
- prints a plan only; it has no MongoDB client;
- rejects `--apply` with exit code 3;
- returns NO-GO while manifest status is `INVENTORY_INCOMPLETE`.

Unit coverage exists in `tests/unit/test_eos_index_provisioning_harness.py` for manifest structure, duplicate collection, production target rejection, fingerprint mismatch and matching non-production fingerprint.

A real target cannot yet be safely tested. The discovered Atlas `legal-doc-test` cluster is rejected as an EOS target because its databases/collections do not match the EOS manifest. The deployment-owned non-production EOS secret reference and its target fingerprint are still unknown. The harness must not be given a URI until that identity/target chain is established; it must never print the URI.

The next harness phase should add a separate read-only live verifier (not apply) that connects using an explicitly injected non-production credential, verifies server/cluster/database fingerprint against independent approval, lists current indexes, compares every option (key order, unique, sparse, partial filter, collation, TTL, hidden/expire options), and reports missing/extra/divergent indexes. Only after complete inventory, duplicate-data preflight, backup/restore proof, approved target and role tests should a separately reviewed apply command exist.

## 11. Updated no-go conditions

- Manifest stays `INVENTORY_INCOMPLETE`.
- No Atlas cluster is approved as EOS non-production target yet.
- No apply path exists.
- API startup DDL has not been removed.
- No candidate runtime/provisioner/worker roles have been created.
- Dunning remains API-hosted and non-atomic.
- No production credentials, Atlas roles, network entries, cloud identities, object-storage policies, KMS keys, deployments or production data have been changed.
