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


### 10.1 Additional exact legal-operation indexes added to the manifest

Source declarations were checked against each registry's `ensure_indexes` body and literal index-name constants. The manifest now includes 12 more collection entries:
- `legal_client_acceptance_contexts` (8 indexes);
- `legal_client_acceptances` (3);
- `legal_client_acting_capacities` (5);
- `legal_client_matter_acceptance_instrument_approvals` (5);
- `legal_client_matter_acceptance_instrument_lifecycle` (5, including its exact partial unique terminal-state filter);
- `legal_client_matter_acceptance_instruments` (5);
- `legal_client_matter_acceptance_instrument_contents` (3);
- `legal_operations_client_matter_visibility_bindings` (4);
- `legal_matter_parties` (4);
- `legal_operations_lifecycle_evidence` (3);
- `legal_matter_deadlines` (4);
- `legal_tenant_operating_models` (5).

The index names were cross-checked against the registry constants after initial construction; the manifest uses the exact source literals, ordered key tuples, uniqueness flags and lifecycle partial filter. Commit `2c4ec26` contains the corrected exact names. These are index specifications only; no indexes were created in Atlas.

### 10.2 Harness CI coverage

The GitHub provisioning gate now runs `tests.unit.test_eos_index_provisioning_harness` and exercises the CLI's `--apply` refusal, requiring exit code 3. The gate now runs on pull requests and pushes to the roadmap branch when the manifest/workflow changes. The job remains intentionally non-mutating and does not contact MongoDB.


## 12. Legal Operations command factory closure

The mounted `/api/legal-operations` command router does not own a generic collection name supplied by the request. Its `_collection(database, name)` factory receives only imported registry constants. The direct collection dependency set was closed from the router's import graph and all call sites:

- Core lifecycle journal: `legal_operations_lifecycle_evidence`.
- Allocation: allocation current pointer and immutable allocation receipt.
- Attempt authority, transition and outcome registries.
- Deputy principal binding and device provenance.
- Field evidence and return evidence.
- Location permission, observation and revocation evidence.
- Conflict screening and review evidence.
- Workflow definition, topology, stage, instance, gate satisfaction and transition registries.
- Notification recipient binding and lifecycle registries.
- Legal work assignment, work item and completion event registries.
- Tenant authorization decision evidence.
- Principal authority, tenant membership, tenant business role and role assignment repositories.

The exact imported registry symbols in the router are `LIFECYCLE_COLLECTION`, `ALLOCATION_CURRENT_COLLECTION`, `ALLOCATION_RECEIPT_COLLECTION`, `ATTEMPT_AUTHORITY_COLLECTION`, `TRANSITION_COLLECTION`, `OUTCOME_COLLECTION`, `RETURN_COLLECTION`, `FIELD_EVIDENCE_COLLECTION`, `DEPUTY_PRINCIPAL_BINDING_COLLECTION`, `DEPUTY_DEVICE_PROVENANCE_COLLECTION`, `LOCATION_PERMISSION_COLLECTION`, `LOCATION_OBSERVATION_COLLECTION`, `LOCATION_REVOCATION_COLLECTION`, `LEGAL_CONFLICT_SCREENING_COLLECTION`, `LEGAL_CONFLICT_REVIEW_COLLECTION`, `WORKFLOW_DEFINITION_COLLECTION`, `WORKFLOW_TOPOLOGY_COLLECTION`, `WORKFLOW_STAGE_COLLECTION`, `WORKFLOW_INSTANCE_COLLECTION`, `WORKFLOW_GATE_SATISFACTION_COLLECTION`, `WORKFLOW_TRANSITION_COLLECTION`, `RECIPIENT_BINDING_COLLECTION`, `RECIPIENT_BINDING_LIFECYCLE_COLLECTION`, `LEGAL_WORK_ASSIGNMENT_COLLECTION`, `LEGAL_WORK_ITEM_COLLECTION`, and `LEGAL_WORK_COMPLETION_EVENT_COLLECTION`, plus the canonical IAM collection constants.

This is a bounded server-side factory, not an unrestricted dynamic collection resolver. The API caller's Mongo role still needs the union of CRUD actions actually reached by the invoked command; collection presence alone does not justify blanket read/write rights. The existing API-owned transaction is propagated into the orchestration/registry calls. Index DDL remains a distinct provisioner responsibility.

## 13. AI Legal Gateway transitive read closure

The mounted `/api/wilsy-ai/legal-tools` routes resolve the following direct collections:
- `wilsy_ai_entitlements` — current entitlement read;
- `wilsy_ai_usage_observations` — usage/capacity read;
- `legal_operations_lifecycle_evidence` — instruction, attempt, execution and return source read;
- process-service tariff assessment and billing eligibility registries — read projections;
- `client_invoices` and `issuance` — invoice projection/correlation read;
- `wilsy_ai_legal_tool_invocations` — append-only post-read invocation evidence write.

The `LegalAIReadAdapter` delegates seven tool identities to canonical L7A/L7C read callables: instruction, attempt, execution, return, tariff assessment, billing eligibility and invoice. It does not implement a second legal repository or grant mutation authority. Gateway authorization separately recomposes current IAM and commercial admission before materializing legal data. The invocation evidence write occurs after the read; listing tools persists no invocation evidence.

This gateway's effective permissions therefore include the read dependencies of both canonical router families plus the invocation append. It does not imply permission to mutate invoices, payments, tariffs, legal lifecycle, entitlement or usage observations.

## 14. Branding persistence closure and index declarations

The mounted `/api/tenant-branding` router composes these registries:
- `tenant_branding_assets`: tenant/reference immutable asset evidence and content lookup;
- `tenant_branding_entitlement_history` and `tenant_branding_entitlement_current`: revisioned commercial branding entitlement and current pointer;
- `tenant_branding_profiles`, `tenant_branding_profile_selections`, and `tenant_branding_profile_current`: immutable profile/selection facts and explicit current pointer.

The router's reads/writes are transaction-scoped and tenant-scoped. Asset bytes are stored in the asset record as bounded payload/content evidence; no S3/object-storage dependency is inferred from these registries. No separate cleanup worker or object deletion caller was established by this source pass.

The manifest now records the exact `ensure_indexes` declarations for these six collections (17 index declarations), including all unique flags and key order. AI entitlement, usage-observation and invocation registry indexes are also recorded (9 declarations). These definitions have not been provisioned.

## 15. Read-only live index verifier

Added `tools/eos/mongodb/read_only_index_verifier.py`. It:
- requires explicit `--target nonproduction`, exact database name, an independently approved opaque fingerprint and a protected environment URI variable;
- uses only MongoDB `hello` and `list_indexes()` read operations;
- fingerprints replica-set identity/host membership plus the explicitly selected database without printing hostnames or URI material;
- compares key order and the declared unique/sparse/TTL/partial-filter/collation/hidden options;
- reports missing, divergent and undeclared extra indexes;
- contains no create/drop/update/insert/delete operation and always reports zero mutations.

The verifier refuses to run while the manifest is `INVENTORY_INCOMPLETE`, refuses the separate audit database in the same invocation, and fails if the independently injected approval does not match the command-line approval. Unit tests use fake collections and cover exact match, missing index, TTL mismatch, undeclared extra index, and database-scoped fingerprint stability. The CI provisioning gate runs these tests.

**Execution is intentionally pending.** No EOS non-production Atlas target has been verified; `legal-doc-test` remains rejected. The verifier must not be run against that cluster or any guessed target.

## 16. Remaining explicit blockers after this tranche

- Dunning's `collections_day` policy field has no implemented state/event semantics. A product/legal policy decision is required before a safe evaluator can map it into lifecycle transitions.
- Dunning audit and state idempotency indexes, duplicate-data preflight and exact subscription identity are not yet source-certified; no transaction implementation is enabled.
- Branding and AI indexes are now inventoried, but C1C orchestration/accounting and AI advisory/service router transitive persistence require separate route-to-registry closure.
- Dynamic legal command collection references are closed to imported registry constants, but their exact index options and CRUD action set must still be merged from every registry source before the API permission manifest is marked complete.
- No candidate workload identity or live runtime target is proven; operator credentials and production remain unchanged.


## 17. Legal Operations workflow/command index tranche

Added 11 more source-verified collection entries to `infra/mongodb/eos-index-manifest-v1.json`:
- process-service allocation receipts and current pointer (4 exact indexes);
- deputy device provenance challenges (2);
- legal conflict screenings and reviews (8);
- legal matter workflow instances and transitions (8);
- legal workflow definitions, gate satisfactions, stages and topologies (11).

All index names, key order and unique flags were checked against the registry source. No TTL indexes are declared by these registries. These additions are manifest-only and do not provision MongoDB.

The source pass also identified collections in the command dependency graph for which no `ensure_indexes` or direct `create_index` declaration was found in the inspected registry module:
- `legal_operations_lifecycle_evidence`;
- `legal_operations_deputy_principal_bindings`;
- `process_service_attempt_outcome_evidence`;
- `process_service_attempt_transition_evidence`;
- `process_service_field_evidence`;
- `process_service_return_evidence`;
- the four process-service location permission/observation/revocation/access-audit collections;
- legal notification recipient binding and lifecycle collections;
- legal work assignment, work item and completion-event collections.

This does **not** prove these collections have no indexes: indexes may be declared in another bootstrap or a shared owner. Their canonical index owner and exact deployed definitions remain unresolved, so they are excluded from any complete-manifest claim. The API's reachable CRUD actions are likewise not collapsed into blanket CRUD; each registry method remains the source of the action matrix.

## 18. Dunning implementation gate

The transaction redesign remains a reviewed contract, not an activated code path. Two source facts make immediate implementation unsafe:
- `collections_day` is accepted and persisted by policy normalization but is ignored by the state derivation function; product/legal policy must decide its meaning.
- The exact unique/idempotency indexes and canonical subscription identity needed for a transaction-safe state + subscription + audit transition are not yet source-certified.

No worker was extracted and no dunning writes were changed. The next implementation must introduce the idempotency/fencing evidence and CAS semantics together with its exact index manifest entries and disposable replica-set integration tests, then replace the API evaluator in one reviewed change. The current evaluator remains the known non-atomic implementation; it must not be represented as certified.


## 19. C1C orchestration, AI reasoning, legal services and advisory closure

Additional mounted AI route families were followed:

| Route family | Persistence dependencies | Operations / notes |
|---|---|---|
| `/api/wilsy-ai/legal-services` | `wilsy_ai_entitlements`, `wilsy_ai_usage_observations`, C1C orchestration composition and invocation evidence | Tool orchestrator invokes only server-registered tools; API composition persists bounded C1C orchestration and invocation facts. Provider execution is separate from legal source reads and has no legal lifecycle/payment authority. |
| `/api/wilsy-ai/reasoning` | `wilsy_ai_entitlements`, `wilsy_ai_usage_admissions`, `wilsy_ai_model_invocations`, `wilsy_ai_usage_observations` | One request transaction; current entitlement/capacity admission, admission evidence, model invocation evidence and usage observation. Model/provider configuration is external runtime dependency, not a MongoDB collection. |
| `/api/wilsy-ai/legal-next-actions` | `wilsy_ai_tool_orchestrations`, `wilsy_ai_legal_tool_invocations`, `wilsy_ai_next_best_action_advisories`, plus legal L7A/L7C read sources, IAM, entitlement and usage capacity | Service reads completed C1C TOOL_ASSISTED root and invocation, reauthorizes the underlying legal permission, re-reads the legal source snapshot, then appends an immutable advisory. Advisory GET derives current/stale status from successor evidence. |
| C1C orchestration registry | `wilsy_ai_tool_orchestrations` | `find_one`, `insert_one`, `replace_one`; unique tenant/orchestration identity and revision CAS. Its index provisioning is explicitly called from API startup through `ensure_c1c_indexes`, so API runtime currently performs this DDL. |
| C1D advisory registry | `wilsy_ai_next_best_action_advisories` | `find_one`, `insert_one`, bounded `find`; immutable append-only records and derived successor status. Four exact indexes include partial unique successor constraint. The inspected server startup does not call its `ensure_indexes`; actual index installation entrypoint remains unproven. |

### Advisory collection drift found and corrected

The C1E advisory service had five hardcoded collection names. Three did not match the canonical L7A/L7C providers:
- lifecycle: old `legal_operations_lifecycle_facts` vs canonical `legal_operations_lifecycle_evidence`;
- billing eligibility: plural `process_service_billing_eligibilities` vs canonical singular `process_service_billing_eligibility`;
- invoice issuance: `process_service_client_invoice_issuances` vs canonical L7C `issuance`.

This could have made the advisory path read a different or empty data family than the authenticated gateway, despite using the same adapter contract. Commit `3e48152` changes the service to import and use the canonical lifecycle, tariff, eligibility, invoice and issuance constants. Commit `717a112` adds a unit assertion for the exact collection map. This is a source correction; runtime deployment and Mongo data parity remain unproven.

### Additional C1C/C1D/C1B index manifest entries

The manifest now contains the source-declared C1C orchestration identity index. Existing C1D advisory, C1A model invocation and C1B usage-admission index entries were confirmed against their respective registry declarations. The C1B admission set includes the unique tenant/admission identity, unique tenant/idempotency identity and non-unique tenant/entitlement/window/state lookup. No indexes were created.

### Remaining AI gaps

- C1C startup index DDL must move to the separate provisioner and be replaced by read-only readiness verification.
- C1D advisory index installation caller must be identified; do not infer that a registry method is deployed.
- AI Legal Services and Reasoning provider credential/configuration sources, usage observation/outbox behavior and any background retry/cleanup invocation require their own runtime/worker inventory.
- The advisory legal-source collection mismatch is corrected in code but requires the existing unit and real-Mongo advisory suites to certify before the fix is considered complete.


### C1E collection-map correction certification

Commit `3e48152` changes advisory source reads to canonical L7A/L7C registry constants; `717a112` adds the exact collection-map unit assertion. A dedicated workflow, `.github/workflows/eos-ai-advisory-certification.yml`, now runs the C1E/C1D/C1C focused unit suites and existing real-replica-set advisory/gateway integration suites against a disposable local MongoDB replica set. It is currently running on PR head `5c3eaf2`; no certification claim is made until its job completes.


## 20. Billing and PayShap webhook execution / credential closure

### Billing HTTP surface

The mounted `tools/eos/api/billing_router.py` exposes platform/client invoice create/read/update/void operations, payment read/create/status/refund compatibility routes, invoice email and partial-payment compatibility routes, audit/integrity, investor proof, statement, plans, intelligence and dunning routes. Its direct collection references include:

- Commercial invoice/payment: `platform_invoices`, `client_invoices`, `payments`.
- Subscription and dunning: `subscriptions`, `billing_dunning_policies`, `billing_dunning_states`.
- Audit/financial evidence: `billing_audit_events`, `billing_statements`, `billing_integrity_controls`, `billing_investor_proofs`.
- Intelligence/receivables: `billing_intelligence_evidence`, `commercial_receivables`, `commercial_receivable_aging`, `commercial_receivable_dunning`.

The route code uses `find`, `find_one`, `distinct`, `insert_one`, `update_one` and `update_many`. The registry-owned invoice indexes are now in the manifest, but direct billing-router collections and commercial receivable projection families still require their canonical index owner and exact options. The existing billing registry's `_ensure_indexes()` creates indexes for platform invoices, client invoices and payments, but source search found no caller; two legacy idempotency index calls are wrapped in broad exception suppression. No deployment-time provisioning proof follows from the function's presence.

The billing registry is a commercial invoice and historical payment projection owner only. HTTP settlement mutations are guarded by the Kennel financial-truth boundary; a caller cannot establish payment success, refund, paid state or settlement by posting a billing DTO.

### Dunning runtime remains unsafe for extraction

The current API-hosted daily task in `tools/eos/api/server.py` invokes `evaluate_all_tenant_dunning_lifecycles()` from the API lifecycle. It uses the API's shared kernel database/client; no dedicated dunning worker process or independent Mongo identity was found. The scheduler's exact trigger/enable configuration remains in the API composition root.

The evaluator reads platform invoices, tenant policy and current dunning state, then performs separate writes to `billing_dunning_states`, `subscriptions`, and `billing_audit_events`, followed by telemetry. It does not pass one caller-owned Mongo session through the sequence. Its subscription projection uses `update_many`, and the state write is an upsert, so the current path is not transactionally atomic or protected by a canonical state-revision CAS.

Policy normalization accepts `collections_day`, but `_dunning_state_for_days` does not use it. The current state ladder is ACTIVE, WARNING, CRITICAL, SUSPENDED_READONLY and TERMINATED; the collections threshold has no defined state/action. This remains a policy/legal product decision and must not be guessed in code. No dunning worker extraction, transactional write or policy reinterpretation was made.

### PayShap webhook host ingress

The mounted `POST /providers/payshap/webhook` route:
- Resolves the already-connected shared kernel Mongo client/database at request execution time.
- Resolves `WILSY_PAYSHAP_WEBHOOK_SECRET` from process environment; no secret value was read or recorded. Its deployment secret reference and rotation owner are unverified.
- Starts one Mongo session and transaction around authenticated PayShap evidence, provider observation, attempt/command correlation, neutral execution fact and applicable AP/platform execution-truth reconciliation.
- Uses the API process database credential; no separate webhook workload identity, queue consumer or dedicated worker was found.

The persistence dependency set is source-verified: `kennel_payshap_provider_evidence`, `kennel_financial_execution_attempts`, `kennel_financial_execution_provider_observations`, `kennel_financial_execution_commands`, `kennel_financial_execution_facts`, `kennel_financial_execution_truth`, and `kennel_platform_billing_financial_execution_truth`. Their registry index declarations have been added to the manifest. The webhook route itself does not call those registries' `ensure_indexes`; no canonical deployment-time provisioner invocation was established by this pass.

PayShap EXECUTED is authenticated provider evidence, not by itself settlement. The router delegates to Kennel reconciliation and never directly writes the commercial invoice paid state.

### Index inventory tranche

Commit `e2f01f9` adds 10 source-verified collection entries and 38 index declarations:
- platform/client invoices and payments (13);
- PayShap provider evidence (2);
- Kennel command and attempt (8);
- provider observations (5);
- AP execution truth and neutral execution facts (8);
- platform billing execution truth (2).

These entries describe source declarations only. No Atlas index was created or inspected. The manifest remains `INVENTORY_INCOMPLETE`; direct billing projections, webhook provisioning invocation, billing index exception suppression, and deployed API/webhook credential source remain open evidence items.


### Runtime invocation details confirmed

- Dunning schedule: daily at 00:15 Africa/Johannesburg. `WILSY_DUNNING_SCHEDULER_ENABLED` defaults to false in production mode and true outside production, with explicit environment override. It is an in-process asyncio task, not a separately deployed worker.
- PayShap secret: repository search found `WILSY_PAYSHAP_WEBHOOK_SECRET` only in the webhook router's environment lookup. No K8s Secret key mapping, external secret reference, rotation automation or independent workload credential source was found in the reviewed repository.
- Registry index methods for PayShap/financial execution are invoked in integration-test fixtures. Repository search did not find an API startup or webhook request call to those methods. Their existence in test setup is not deployment provisioning evidence.
- Subscription registry's `create` path invokes `_ensure_indexes` itself, so its four indexes are runtime DDL on the create path. Its tenant+subscription identity unique index is a useful source-level identity contract, but the dunning evaluator does not use that registry or a subscription revision CAS.


### Billing / webhook repeatable certification

Added `.github/workflows/eos-billing-webhook-certification.yml`. It provisions a disposable local MongoDB 7.0.37 replica set and runs existing billing registry, financial-truth firewall, subscription transaction-injection, execution reconciliation and PayShap host integration suites, plus focused billing/dunning unit suites. It uses the repository's fixed test URI contract on loopback port 27027 and a synthetic PayShap test secret from the test fixture. This does not connect to Atlas or require production credentials. The workflow is new and its first run must complete before certification is claimed.


## 21. Legal registry index-owner closure — corrected source findings

A deeper registry-owner pass found that several families previously listed as lacking an index declaration do in fact declare their own indexes. The earlier statement that these had no declaration in the inspected registry module is superseded by this section. Source owners and exact definitions are now recorded for 21 additional collections / 45 indexes:

- deputy principal bindings;
- notification contact verification, verified contacts, recipient bindings and recipient-binding lifecycle;
- return-ready notification intents;
- legal work assignments, work items and completion events;
- process-service attempt authority receipts, attempt outcomes, attempt transitions and field evidence;
- process-service location permission grants, observations, revocations and access audit;
- process-service return evidence;
- process-service tariff schedules, versions and assessments.

The new manifest commit `8500989` adds the exact source-declared key order, uniqueness, explicit names and partial filters. Notable non-default options include:
- verified notification active-address unique index filtered by `revoked_at: null`;
- legal work assignment initial-current index filtered by `supersedes_assignment_id: null`;
- legal work assignment predecessor unique index filtered by `supersedes_assignment_id: {$type: "string"}`.

These are source-owner declarations, not live Atlas observations. The source registry methods must still be separated from runtime DDL and invoked by a controlled external provisioner/readiness path. No production index creation or live target verification occurred.

The manifest now contains 87 collection entries and 281 index declarations. It remains `INVENTORY_INCOMPLETE`: other collection families, deployed index state, API-startup DDL migration, and source-to-runtime provisioning invocation still require closure.


### Billing / PayShap workflow result

The first run of `.github/workflows/eos-billing-webhook-certification.yml` completed successfully on commit `8500989`: compilation passed, 28 focused unit tests passed, and 87 disposable replica-set integration tests passed (115 total). The test environment used only a local MongoDB replica set and the synthetic fixture secret. This certifies the existing billing registry, subscription transaction-injection, Kennel execution reconciliation and PayShap host composition suites; it does not certify the current dunning evaluator as atomic or authorize production use.


## 22. Extended Legal Evidence, mandate, operating-role and work registry closure

A complete pass over the 93 Python Legal Operations registry modules found and source-verified another 44 collection/index definitions across these families:
- Legal Evidence content, legal holds, cleanup authorization/commands, delete execution claims/evidence/uncertainties, object disownership/orphan proofs and retention constraints.
- Legal operating-role definitions, capability bindings, scope bindings and principal operating-role bindings.
- Client matter engagements and firm decisions; mandate grants, acknowledgments, lifecycle and mandates; representation authorities, authorization evidence, final representations and firm decisions.
- Legal corpus approval and provisioning authority, courier observations, court-operation preparation and versioned legal documents.
- Legal work transition materialization receipts, dependency edges, ethical-wall policy revisions/currentness, materialization policies, operational matter access, confidentiality clearances, supervision bindings and tenant workflow activations.
- Professional-standing evidence, legal acceptance and process-service billing eligibility.

The source declarations include the non-default unique/partial filters for revision roots, successors, current work access roots, and predecessor lineage. The manifest now has 131 collection entries and 466 index declarations. The provisioning gate passed on commit `376c287`: manifest validation, the manifest/harness/verifier unit suites, and the explicit apply-refusal check all passed.

### Remaining source boundary

The 93-file comparison leaves only three registry-tree modules without a manifest source path:
- `legal_practitioner_matter_access_history_reader.py`: read-only query helper, not an index owner.
- `legal_practitioner_matter_access_review_codec.py`: serialization/validation codec, not a persistence owner.
- `legal_practitioner_ethical_wall_restriction_registry.py`: declares three index methods but receives its collection by injection and has no canonical collection-name constant or repository caller that proves the collection identity. It is deliberately not added under a guessed collection name.

The final item requires a verified caller/collection binding before its indexes can be included. The source registry modules that do declare canonical collection names now have matching manifest source entries. This source-level closure still does not prove that deployment provisioning invokes every owner or that live Atlas indexes match.
