# EOS runtime database-consumer inventory

**Version:** v1.0.0-EOS-RUNTIME-DB-CONSUMER-INVENTORY  
**Scope:** repository-defined active development and production entrypoints on PR #342  
**Boundary:** inventory evidence only; this document does not authorize deployment or production database changes.

## Canonical business database owner

The Python EOS kernel owns the business MongoDB client/database lifecycle through `tools/eos/kernel/db.py`. Business registries and API routes either resolve that kernel-owned database/client or receive a caller-owned `client + database + session` graph and enforce the same-client transaction boundary.

## Active entrypoints

| Entrypoint | Runtime role | Database posture |
|---|---|---|
| `npm run dev` → `scripts/start-dev-stack.sh` | Python EOS + Vite development stack | Starts `uvicorn tools.eos.api.server:app`; no Node business database process |
| `npm run dev:kernel` | Python EOS API | Kernel-owned Mongo lifecycle |
| `npm run prod:kernel` | Python EOS API | Kernel-owned Mongo lifecycle |
| `server/ecosystem.config.js` → `server/server.js` | Production Node BFF | HTTP proxy only; no Mongo client, no Mongoose connection, no business registry |
| `server/deploy.sh` | PM2 deployment wrapper | Reloads the BFF entrypoint above |

The active Node BFF health response now states `database: NOT_CONNECTED_BY_BFF` and `databaseAuthority: PYTHON_EOS`. It no longer opens a duplicate connection merely to report Mongoose connection state.

## Business registry and API consumers reviewed

- Tenant, plan, subscription, employee and principal repositories resolve `get_database()` through the kernel database module.
- Owner commercial workspace, billing and PayShap HTTP routes obtain the kernel client/database and pass the caller-owned transaction session to their registries.
- PayShap evidence persistence resolves the kernel database when no explicit collection is supplied.
- Password reset and recovery-contact completion use the kernel-owned client/session transaction boundary.
- Order-number service accepts a client only when it is exactly `get_database().client`.
- Financial approval aggregation defaults to the kernel database and rejects a mixed client/database graph.
- Platform billing release authorization obtains `get_client()` and `get_database()` from the kernel.
- Financial execution-request issuance and PRDCA application composition are dependency-injected: the caller supplies the client/database/session; the code does not create a second Mongo client and validates graph identity where applicable.

## Explicit non-business exception

`tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_runtime.py` creates a separate Mongo client only for its dedicated reconciliation audit sink. It requires `WILSY_LEGAL_EVIDENCE_RECONCILIATION_AUDIT_MONGODB_URI`, compares that target with the canonical `MONGODB_URI`, requires TLS, and rejects an audit database whose client is the business database client. This is an isolated audit sink, not a business-registry connection or a fallback business database.

## Dormant legacy/operator surfaces

- `server/app.js`, `server/config/database.js` and `server/jobs/scheduler.js` retain legacy Mongoose-era code. They are not referenced by the repository's active PM2 BFF process definition or the current development stack. In particular, the scheduler's direct-start block is not part of the active PM2 app list.
- `tools/eos/scripts/update_platform_tenant.py`, `tools/eos/scripts/update_platform_tenant_direct.py`, and `tools/eos/tenancy/retire_legacy_root_aliases.py` are explicit operator/migration commands, not imported API runtime modules. Their direct connection behavior is excluded from the runtime-client scan and should remain manually invoked under separately approved operational controls.

**Operational caveat:** this is a repository-defined entrypoint inventory. It cannot prove that an external PM2, cron, shell, or container configuration outside the repository is not manually launching a dormant legacy process. Deployment operations must reconcile the actual host process list before any production cutover.

## Automated guard

`tests/unit/test_eos_runtime_database_consumer_inventory.py` checks that:
1. direct Mongo client construction in runtime `tools/eos` code is confined to the canonical kernel connector and the explicit isolated audit sink;
2. active BFF and development entrypoints do not load the dormant Mongoose app/scheduler;
3. the BFF source contains no Mongoose connection lifecycle; and
4. representative business registry consumers retain the kernel-owned or caller-owned same-client boundary.
