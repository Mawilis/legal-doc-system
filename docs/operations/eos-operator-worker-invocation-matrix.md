# EOS operator and worker invocation matrix — tranche 8

**Repository snapshot:** branch `eos/tenant-discovery-iam-dashboard-roadmap`  
**Status:** source invocation classification; deployment invocation remains unverified.  
**No production changes.**

## 1. Explicit operator / migration execution

| Entrypoint | Invocation model | Persistence/authority | Transaction / DDL boundary | Runtime identity decision |
|---|---|---|---|---|
| `tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_audit_provisioner.py` | explicit deployment provisioner CLI | separate platform decision-evidence audit database; index DDL and verification only | dedicated audit URI; creates/verifies its two indexes | separate audit-index provisioner, not API or business DB role |
| `tools/eos/saas/auth/migrations/reconcile_legacy_principal_authority.py` | explicit operator CLI | legacy principal authority reconciliation; exact principal scoped source | shared kernel DB source; transaction; disconnect in finally | human migration operator role, not API |
| `tools/eos/saas/auth/migrations/reconcile_legacy_super_admin_tenant.py` | explicit operator CLI | exact tenant/user preflight; update one user's tenant; revoke that principal's sessions and refresh tokens | transaction; dry-run reads; mutation requires explicit confirmation | human migration operator role with exact legacy collection update/delete scope |
| `tools/eos/saas/auth/migrations/refresh_token_indexes.py` | caller-invoked migration service; caller supplies collection | refresh-token index topology | dry-run reads only; APPLY creates two exact indexes; caller owns connection/quiescence | index provisioner only; never API |
| `tools/eos/saas/auth/migrations/refresh_token_tenant_backfill.py` | source module present; invocation and persistence not established by inspected lines | unresolved | unresolved | do not assign rights until invocation and CRUD are proven |
| `tools/eos/saas/billing/migrations/tenant_inbound_merchant_configuration_lifecycle_idempotency_projection.py` | caller-invoked one-shot deployment migration | `tenant_inbound_merchant_configurations`; scans lifecycle history, writes derived projection, creates new partial unique index, drops only named defective old index | caller supplies collections/session policy; module itself does not open client/transaction; DDL not transaction-atomic | dedicated migration/provisioner role; collection update plus narrowly scoped index DDL, not API |
| `tools/eos/saas/billing/migrations/tenant_inbound_provider_credential_security_authority_index_migration.py` | caller-invoked deployment migration | credential security fact/current-pointer collections plus merchant configuration read | requires explicit quiescence; full scans and provenance checks; drops two named legacy indexes and creates repaired unique indexes | dedicated migration/provisioner role; no credential issuance or security mutation |
| `tools/eos/saas/billing/reconcile_wilsy_founder_legal_entitlement.py` | explicit CLI with `--apply`; dry-run default | hardcoded canonical tenant/subscription/plan; reads subscriptions, plans, entitlement current/history and authorization evidence; governed entitlement reconciliation | shared kernel DB; requires database name `wilsy` and replica set; closes connection | restricted human operator/one-off migration identity; not runtime API |
| `tools/eos/auth/developer_persona_provisioner.py` | provisioning service; explicit CLI invocation not established in inspected excerpt | obtains Mongo client and transaction for developer persona provisioning | caller/client session transaction | separate provisioning identity; exact collection actions still need registry closure |
| `tools/eos/auth/principal_authority_provisioning.py` | provisioning service | resolves canonical kernel database; exact registry writes need service closure | no standalone invocation proven | separate provisioning identity; no normal API assumption |
| `tools/eos/auth/tenant_owner_genesis_provisioning.py` | provisioning module | exact persistence and caller not yet established | unresolved | no rights assigned until invocation proven |
| `tools/eos/cloud/tenancy/tenant_provisioner.py` | provisioning module | exact persistence and caller not yet established | unresolved | no rights assigned until invocation proven |

### Important DDL distinctions

The two explicit billing migrations are not interchangeable:
- Merchant lifecycle projection migration changes business documents, then creates a partial unique index, then drops a named old index. It is a controlled data migration plus DDL.
- Provider credential security migration is intended to be index-topology-only, scans facts/pointers/configuration, requires quiescence and makes no document writes. Its DDL sequence is not atomic; failure handling and rollback must be part of the deployment plan.

Neither should run with the API runtime identity.

## 2. Background execution and worker framework

| Source | What is verified | What is not verified |
|---|---|---|
| `tools/eos/api/server.py` dunning task | API composition starts optional daily task; 00:15 Africa/Johannesburg; calls billing evaluator | independent worker deployment does not exist in inspected composition |
| `tools/eos/automation/scheduler.py` | scheduler framework module exists | no proof it schedules dunning or runs in deployed production |
| `tools/eos/runtime/scheduler.py`, `runtime/scheduler/*`, `scheduler_bridge.py` | runtime scheduler abstractions exist | no proof of deployment or exact Mongo consumer |
| `tools/eos/runtime/worker.py`, `worker_registry.py`, `cluster/application/worker_registry.py` | worker abstractions/registry exist | no proof of a deployed worker process or collection rights |
| `tools/eos/cluster/application/scheduler.py`, `tools/eos/distributed/cluster_scheduler.py` | scheduler modules exist | no proof of a configured production schedule |
| `tools/eos/run_scheduler_playbook.py` | scheduler playbook entrypoint exists | target, invocation owner, credential source and persistence not yet closed |
| `tools/eos/legal_operations/service/legal_evidence_commit_reconciliation_service.py` | service-level commit reconciliation exists | no independent worker/CLI invocation proven |
| `tools/eos/saas/hr/hr_document_commit_reconciliation_service.py` | service requires caller-owned transaction; provider I/O is outside service | no independent scheduler/worker invocation proven |
| Legal Evidence cleanup domain/registries | cleanup authorization, command and retention constraints exist | no active cleanup worker, object deletion consumer or deletion rights proven |

A file named `worker` or `scheduler` is not proof that it runs. Do not create runtime roles for dormant frameworks. The deployment process, command, schedule, image and secret reference must all be identified first.

## 3. Runtime identity separation target

| Identity | Permitted purpose | Explicit exclusions |
|---|---|---|
| EOS API | mounted HTTP routes and their proven business/auth persistence actions | index DDL, migrations, broad operator mutation, dunning scheduler loop |
| Dunning worker | transactional platform dunning evaluation and exact subscription posture projection | IAM/MFA, legal content, provider payments, settlement, index DDL |
| HR document workload | tenant-scoped HR object upload/read and Mongo evidence operations proven by route | Legal Evidence bucket assumptions, broad object deletion, index DDL |
| Legal Evidence workload | approved legal evidence object operations and Mongo upload/reconciliation actions | HR bucket assumptions, arbitrary deletion, index DDL |
| AI workload (if separately deployed) | bounded tenant admission, allowlisted reads, invocation/orchestration evidence | model/provider secret administration, legal mutation, finance/settlement |
| Mongo index provisioner | exact approved create/verify index operations | business document CRUD, API traffic, production by default |
| Migration operator | individually approved, time-bound migration actions | standing API/workload credentials |
| Audit index provisioner | separate audit database index DDL only | business database writes, API runtime |
| CI test identity | non-production-only certification fixture actions | production network, production credentials, production data |

These are target roles, not currently provisioned identities.

## 4. Required closure before granting any role

For each row above, record:
1. exact caller (workflow, command, deployment, scheduler or route);
2. invocation schedule and owner;
3. image/commit digest and runtime environment;
4. database URI secret reference (name/key only, never value);
5. resolved cluster/database fingerprint;
6. exact collection and CRUD/command set;
7. session/transaction ownership and retry behavior;
8. exact index DDL or read-only verification calls;
9. positive and denied integration tests;
10. operational rollback, logs and audit evidence.

The source tree currently proves the existence of some modules and their local behavior. It does not prove which are deployed, who invokes them, or which live credentials they use.
