# WILSY OS — deployment authority and runtime boundary

**TITLE:** Kennel EOS Deployment Authority and Production Cutover Boundary
**VERSION:** v1.3.0-PYTHON-EOS-RETIRED-BACKEND-AND-MIGRATION-LINEAGE
**AUTHORITY:** Wilsy OS Core Governance
**EPITOME:** Records Python Kennel EOS as the supported API and business runtime, the retained migration-history boundary, and the production facts that remain unverified.
**ABSOLUTE CANONICAL PATH:** /Users/wilsonkhanyezi/legal-doc-system/DEPLOYMENT.md
**COLLABORATION / OWNERSHIP:** Wilson Khanyezi (Founder); Kennel EOS runtime owners; Codex (AI Engineering).
**CERTIFICATION / UPDATE DATE:** 2026-11-10
**CHANGELOG:** v1.3.0-PYTHON-EOS-RETIRED-BACKEND-AND-MIGRATION-LINEAGE updates the retired Node source inventory, records the exact retained migration-history artifacts, and distinguishes Python runtime evidence from production and data-migration evidence.
**COMPLIANCE:** AGENTS.md v1.2.0; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
**SECURITY / PRIVACY POSTURE:** No production credentials, private keys, host process or tenant records are included. Repository files do not prove live infrastructure state.
**TENANT BOUNDARY:** No tenant data or tenant authority is established by deployment configuration.
**AUTHORITY BOUNDARY:** Kennel EOS is the supported application/API and business authority. This document authorizes no deployment, data migration or ingress change.
**FINANCIAL AUTHORITY BOUNDARY:** Kennel EOS exclusively owns financial execution and settlement truth.
**TRANSACTION BOUNDARY:** No database migration, worker activation, transaction or production cutover is performed.

WILSY OWNS BUSINESS TRUTH. KENNEL EOS IS THE EXCLUSIVE FINANCIAL EXECUTION AUTHORITY.

---

## Supported runtime

The supported API and business runtime is Python Kennel EOS:

```bash
python -m uvicorn tools.eos.api.server:app --host 0.0.0.0 --port 9095
```

The repository-root `Dockerfile`, `Dockerfile.eos` and `docker-compose.prod.yml` describe the Python EOS runtime candidate. The durable worker is a separate Python process and is opt-in through the `python-workers` Compose profile.

The Vite development proxy connects to Kennel EOS on port 9095. Node is used for the client, build, test and browser-certification tooling; it is not the application API, business runtime, database owner, worker, scheduler or production deployment authority.

## Supported development commands

```bash
npm run dev
npm run dev:kernel
```

The development stack starts Python EOS and frontend tooling. Use the Python EOS command for the API; do not substitute a server-directory npm script or a legacy Node launcher.

## Retired Node backend

The current source tree no longer contains the legacy Node API entrypoint, route/controller/model implementation, Node package manifests, server workers, cron configuration, or backend deployment manifests. Root `services/`, `client/server/`, and the former root Node backend aliases have been removed from the active source tree. The root npm manifest retains only frontend, test, documentation and certification tooling.

The following legacy migration-history files are retained exactly as source records and are classified `RETAIN` by `tools/eos/governance/production_surface_policy.json`:

- `server/scripts/finalize-migration.js`
- `server/scripts/migrate-audit-legacy.js`
- `server/scripts/migrate-case-legacy.js`
- `server/scripts/migrate-documents-tenancy.js`
- `server/scripts/migrate-fixed.js`
- `server/scripts/migrate.js`
- `server/scripts/migration/DocumentMigrationEngine.js`
- `server/scripts/migration/MigrationLogger.js`
- `server/scripts/migration/MigrationRunner.js`
- `server/scripts/rollback-migration.js`
- `server/scripts/rollback-simple.js`
- `server/scripts/verify-migration-state-diagnostic.js`
- `server/scripts/verify-migration-state.js`

These files are historical migration/rollback source, not an approved runtime or a verified current-data migration plan. Their contents have not been executed or validated against live records. Their Node dependencies, models and application entrypoints are not retained as a supported execution environment. Do not run these scripts as part of deployment or assume their work was applied.

`server/manifest.txt` and `server/scripts/rollback-migration-production.patch` are preserved historical artifacts. The deletion commit preserves its Git ancestry; removed source remains available from the parent history. Neither that history nor the manifest proves production deployment, migration completion or current database state.

## Python-owned business surfaces

| Surface | Current owner | Boundary |
|---|---|---|
| API composition and authentication | `tools/eos/api/server.py`, Python auth routers and `tools/eos/saas/auth/` | Python EOS owns authenticated identity and request authorization. |
| Billing and subscription | `tools/eos/api/billing_router.py`, subscription routers/registries and Kennel EOS | Tenant-scoped business truth remains Python-owned; Kennel EOS alone owns execution and settlement. |
| Forensic verification and PDF | `forensic_merkle_router.py`, `billing_router.py`, `artifact_pdf_router.py` | Authenticated seal-reference checks and PDF generation are Python routes. A seal-reference match is not a signed-QR or document-content verification. |
| Legal Operations | Python Legal Operations routers, registries and command services | Source registries own legal lifecycle; the client remains a projection and command transport. |
| Daily Attention / My Work | Python attention and unified My Work projections plus their client adapters | Read projections do not grant assignment, completion, Legal-access, payment or release authority. |
| Scheduling and durable workers | EOS Python schedulers and the opt-in Python worker process | No Node worker or cron process is supported. |
| Data migrations | Python migration modules under `tools/eos/**/migrations/` | Each migration retains its own authorization, transaction and evidence requirements. No migration ran during this cleanup. |

## Connection and migration boundary

The billing forensic client calls `POST /billing/merkle/verify` through its `/api` base URL. Python EOS mounts the router under `/api`; it derives tenant scope from the authenticated authorization context, audits the scoped persisted-reference lookup, and does not accept caller tenant authority. `POST /billing/audit/verifyChain` is also mounted by Python EOS.

The client PDF surfaces call `POST /api/generate/pdf`; Python EOS mounts `artifact_pdf_router` at that path. The old Node PDF implementation is not the current route owner.

The repository retains Python auth and billing migration modules, including refresh-token tenant/index migrations and legacy-principal reconciliation. The removed Node migration sources are preserved above as historical records. No live data was read, no schema migration was run, and no claim is made about whether any historical Node migration was previously applied.

## Remaining verification and production no-go

Production remains NO-GO until all of the following are verified by their proper evidence owners:

1. External load balancer, DNS, ingress, process supervisor and host process state route to Python EOS; repository manifests alone cannot establish this.
2. Authenticated route, tenant-isolation, persistence, audit and client parity gates pass at the exact delivered revision.
3. Transaction-sensitive flows pass against an approved disposable real Mongo replica set; unavailable infrastructure is not a pass.
4. Any legacy dataset migration need is assessed from authoritative migration state before an operator separately approves and executes a Python-owned migration.
5. Signed audit-QR issuance and signature verification receive an explicit Python parity decision. The current Python invoice proof reference check is not signed-QR parity. The legacy React audit/QR components have no current import or route caller in the client source tree.
6. Independent operational approval is obtained before production activation.

No build, unit test, CI result, browser certificate or source inspection is production authorization. Do not activate the optional worker, execute historical migration files, change ingress, or deploy from this document.

---

**STATUS: PYTHON EOS IS THE SUPPORTED APPLICATION RUNTIME; PRODUCTION INGRESS, LIVE MIGRATION STATE AND SIGNED-QR PARITY ARE NOT CERTIFIED HERE.**

ARTIFACT: DEPLOYMENT.md
VERSION: v1.3.0-PYTHON-EOS-RETIRED-BACKEND-AND-MIGRATION-LINEAGE
AUTHORITY BOUNDARY: Kennel EOS is the supported application/API authority; no deployment or migration is authorized.
TENANT POSTURE: No tenant authority or data access is granted.
FAIL-CLOSED POSTURE: Unverified migration state, ingress and parity block production cutover.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
END OF WILSY OS SOVEREIGN ARTIFACT
