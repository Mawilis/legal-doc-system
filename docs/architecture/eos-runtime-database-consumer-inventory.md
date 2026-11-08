# WILSY OS — Kennel EOS runtime and legacy Node forensic inventory

**TITLE:** Kennel EOS Runtime and Legacy Node Forensic Inventory  
**VERSION:** v2.2.0-KENNEL-EOS-LEGACY-NODE-FORENSIC-INVENTORY  
**AUTHORITY:** Wilsy OS Core Governance  
**EPITOME:** Evidence-based inventory of the supported Python runtime and the remaining Express, route, middleware, worker, scheduler, persistence, and integration surfaces that must be mapped before legacy retirement.  
**ABSOLUTE CANONICAL PATH:** /Users/wilsonkhanyezi/legal-doc-system/docs/architecture/eos-runtime-database-consumer-inventory.md  
**COLLABORATION / OWNERSHIP:** Wilson Khanyezi (Founder); Codex (AI Engineering)  
**CERTIFICATION / UPDATE DATE:** 2026-11-08  
**CHANGELOG:**
- v2.2.0-KENNEL-EOS-LEGACY-NODE-FORENSIC-INVENTORY: Corrects the prior retirement overstatement; records route mounts, middleware, callable scheduler activation, queue workers, persistence and explicit parity gaps.
- v2.1.0-KENNEL-EOS-LEGACY-NODE-FORENSIC-INVENTORY: Establishes the first corrected legacy runtime forensic inventory.
- v2.0.0-KENNEL-EOS-CANONICAL-RUNTIME: Established the Python EOS deployment and database-owner inventory.
**COMPLIANCE:** WILSY OS Sovereign Codex Governance Contract v1.2.0; forensic inventory only.
**SECURITY / PRIVACY POSTURE:** Repository source inspection only; no production credentials, live customer records, or production database access used.
**TENANT BOUNDARY:** Inventory does not grant or exercise tenant authority. Legacy tenant filters and isolation semantics remain unverified until each mounted capability is inspected and tested.
**AUTHORITY BOUNDARY:** Kennel EOS is the canonical application/API and business authority. Legacy Node source is classified as LEGACY / MIGRATION SOURCE or UNKNOWN / REQUIRES FORENSICS until parity is proven.
**FINANCIAL AUTHORITY BOUNDARY:** Kennel EOS is the exclusive financial execution authority. No Node source may establish payment, provider execution, paid, settlement, or ledger truth.
**TRANSACTION BOUNDARY:** This document performs no database operations and authorizes no migration, worker activation, cutover, or deployment.

WILSY OWNS BUSINESS TRUTH. KENNEL EOS IS THE EXCLUSIVE FINANCIAL EXECUTION AUTHORITY.

---

## 1. Executive finding

The repository supports the Python Kennel EOS runtime, but the legacy Node application has **not** been fully retired from source control.

The following facts are directly observable on branch `eos/kennel-eos-production-runtime-20261108`:

- `server/server.js`, `server/ecosystem.config.js`, and `server/deploy.sh` are absent.
- `server/app.js` still contains an Express application, direct route handlers, global middleware, route imports, and error handling. Its source imports Express, Mongoose, Redis health, CRM, billing, QR, AI and sovereign route modules.
- `server/routes/api.js` still creates an Express router, exposes health/metrics handlers, mounts authentication and tenant middleware, and mounts business route modules.
- The `server/routes`, `server/controllers`, `server/middleware`, `server/models`, `server/services`, `server/jobs`, `server/config`, and `server/utils` trees remain in the repository.
- `server/package.json` still declares Express, Mongoose, Redis, BullMQ, Agenda, cron, and other server-oriented dependencies. Its description says retired backend, but the dependency manifest is not a minimal isolated test-tooling manifest.
- The legacy verification sync job still contains a Mongoose aggregation and a 60-second `setInterval` scheduler. The currently named `server/jobs/scheduler.js` is a separate inert retirement stub; that does not retire every other scheduler.
- `server/jobs/workerEntry.js` still imports BullMQ, IORedis and Mongoose and contains a Mongo query against the Client model.
- `server/config/database.js`, `server/config/db.js`, and `server/config/redis.js` retain Mongoose/Redis connection implementations. The Redis module contains connection and reconnect behavior.

Therefore, “Node backend launch paths disabled” is not equivalent to “all Node application implementation removed.” No legacy source tree may be deleted until its live and historical dependencies, canonical replacement, data contract, and tests are mapped.

## 2. Supported target runtime — current repository evidence

| Surface | Observed implementation | Classification | Status |
|---|---|---|---|
| Kennel EOS API | `tools.eos.api.server:app`, Python FastAPI/Uvicorn | CANONICAL | Supported |
| Kennel EOS durable worker | `tools/eos/runtime/worker_process.py` | CANONICAL | Supported only through explicit Python worker profile |
| Root Docker image | Python EOS Dockerfile | CANONICAL | Repository default |
| Production Compose | Python EOS API and optional Python worker | CANONICAL | Candidate manifest; no deployment implied |
| Vite development proxy | Direct to Python EOS port 9095 | CLIENT SURFACE / TRANSPORT | Local development path |
| Node frontend tooling | Vite, npm scripts, browser certification | CLIENT SURFACE / BUILD TOOLING | Permitted; must not host business/API authority |

This inventory does not prove the currently running external host, load balancer, DNS, ingress, or process supervisor targets Kennel EOS. That requires a separately authorized operational inspection.

## 3. Express application and route inventory

### 3.1 Application entry module

`server/app.js` still imports and composes:

- Runtime packages: `express`, `helmet`, `morgan`, `chalk`, `express-rate-limit`, `mongoose`, and `os`.
- CRM command routes and CRM live/intelligence routes.
- Tenant-context and production-integrity middleware.
- Metrics, audit, telemetry and circuit-breaker helpers.
- The shared `server/routes/api.js` router.
- AI and sovereign routes.
- Billing and QR routes.
- Redis health.
- `startSyncScheduler` and `stopSyncScheduler` from `server/jobs/verificationSyncJob.js`.

Direct application handlers and mounts observed in `server/app.js`:

| Direct path / mount | Capability | Classification | Python parity |
|---|---|---|---|
| `PATCH /api/crm/command/leads/:id` | Local non-production Lead persistence recovery handler; directly opens Mongoose collection access | LEGACY / MIGRATION SOURCE | UNKNOWN; requires forensic mapping and tenant-isolation review |
| `GET /api/status` | Health status | LEGACY / MIGRATION SOURCE | Must map to Kennel EOS readiness/health |
| `POST /api/telemetry/pulse` | Telemetry pulse acknowledgement | LEGACY / MIGRATION SOURCE | UNKNOWN |
| `GET /api/ping`, `GET /ping` | Legacy BFF ping responses | LEGACY / MIGRATION SOURCE | Must map to canonical EOS health without BFF identity |
| `GET /api/v1/sovereign-health` | Composite metrics, Redis and telemetry health | LEGACY / MIGRATION SOURCE | UNKNOWN; dependency and observability parity required |
| `/api/crm/live` | CRM live routes | LEGACY / MIGRATION SOURCE | UNKNOWN; route-by-route mapping required |
| `/api/crm/command` | CRM command routes | LEGACY / MIGRATION SOURCE | UNKNOWN; command authority and audit parity required |
| `/api/crm/intelligence` | CRM intelligence routes | LEGACY / MIGRATION SOURCE | UNKNOWN |
| `/api/wilsy/ai` | AI routes | LEGACY / MIGRATION SOURCE | UNKNOWN; entitlement and inference boundaries required |
| `/api/billing` | Billing routes | LEGACY / MIGRATION SOURCE | UNKNOWN; Kennel financial authority lock applies |
| `/api/qr` | QR and verification routes | LEGACY / MIGRATION SOURCE | UNKNOWN; evidence and reconciliation parity required |
| `/api` | Shared API router | LEGACY / MIGRATION SOURCE | See §3.2 |
| `/monitoring` | Sovereign monitoring routes | LEGACY / MIGRATION SOURCE | UNKNOWN |

The direct Lead recovery handler is particularly sensitive: it selects among candidate collection names, constructs a Mongo ObjectId, and updates a record by `_id` without a tenant predicate in the visible query. It must remain non-authoritative and unavailable to production traffic; any replacement must use canonical tenant-scoped EOS persistence and authorization. This is a source-level observation, not a claim that the handler is currently reachable.

### 3.2 Shared API router

`server/routes/api.js` still:

- Creates an Express router.
- Exposes `/ping`, `/test`, `/metrics/counter`, `/metrics/histogram`, `/metrics/ledger`, and `/status`.
- Imports Mongoose, Redis health, telemetry, circuit-breaker, logging, and authentication/tenant middleware.
- Mounts `/auth` before the shared `requireSovereignAuth`, tenant guard, and tenant-isolation middleware.
- Mounts these route modules:

| Prefix | Module | Domain classification | Python EOS parity |
|---|---|---|---|
| `/auth` | `authRoutes.js` | Identity / authentication | UNKNOWN; compare with global principal, membership, capacity, MFA and session authorities |
| `/telemetry` | `telemetryRoutes.js` | Observability | UNKNOWN |
| `/tenant` | `tenantRoutes.js` | Tenant / organization | UNKNOWN |
| `/compliance` | `complianceRoutes.js` | Compliance | UNKNOWN |
| `/lpc` | `lpcRoutes.js` | Professional regulation | UNKNOWN |
| `/assets` | `assetRoutes.js` | Asset / evidence | UNKNOWN |
| `/contracts` | `contractRoutes.js` | Contracts | UNKNOWN |
| `/revenue` | `revenueRoutes.js` | Revenue | UNKNOWN; no financial truth outside Kennel |
| `/billing` | `billingRoutes.js` | Billing | UNKNOWN; no financial truth outside Kennel |
| `/finance` | `financeRoutes.js` | Finance | UNKNOWN; Kennel exclusive authority |
| `/analytics` | `analyticsRoutes.js` | Analytics | UNKNOWN |
| `/crm` | `crmRoutes.js` | CRM | UNKNOWN |
| `/employees` | `employees.js` | Workforce | UNKNOWN |
| `/legal` | `legal/index.js` | Legal operations | UNKNOWN; full legal-service parity matrix required |
| `/jurisdiction` | `jurisdictionRoutes.js` | Jurisdiction | UNKNOWN |
| `/ledger` | `ledgerRoutes.js` | Ledger | UNKNOWN; Kennel exclusive financial authority |
| `/branding` | `brandingRoutes.js` | Tenant branding | UNKNOWN |
| `/invoices` | `invoiceRoutes.js` | Invoicing | UNKNOWN; Kennel financial authority boundary |
| `/courts` | `courtRoutes.js` | Courts | UNKNOWN |
| `/nodes` | `nodeRoutes.js` | Legacy node/edge operations | UNKNOWN |
| `/seizure` | `sovereignSeizureRoutes.js` | Legal enforcement | UNKNOWN |
| `/statements` | `statements.routes.js` | Statements | UNKNOWN |
| `/subscriptions` | `subscriptionRoutes.js` | Subscriptions / entitlements | UNKNOWN |
| `/treasury` | `treasuryRoutes.js` | Treasury | UNKNOWN; Kennel exclusive authority |
| `/dunning` | `dunningRoutes.js` | Collections / dunning | UNKNOWN; lifecycle authority must remain in EOS |
| `/qr` | `qrRoutes.js` | Verification evidence | UNKNOWN |

The router also imports `wilsyAiRoutes.js` without a corresponding `router.use` mount in the inspected source, and imports an AI ledger-query controller. The AI router is mounted directly by `server/app.js` at `/api/wilsy/ai`. Exact handler semantics, authorization, persistence, audit and client callers for each mounted module remain to be mapped. No parity is inferred from matching route names.

### 3.3 Route, controller and middleware source trees

Repository directory enumeration at this revision found these top-level source counts; nested directories exist in each of several trees and must also be traversed:

| Tree | Top-level files observed | Classification |
|---|---:|---|
| `server/routes` | 138 | LEGACY / MIGRATION SOURCE; includes mounted and apparently unmounted route modules |
| `server/controllers` | 85 | LEGACY / MIGRATION SOURCE; caller and route reachability not yet fully mapped |
| `server/middleware` | 72 | LEGACY / MIGRATION SOURCE; authentication, tenant, authorization, audit and security semantics require mapping |
| `server/models` | 138 | LEGACY / MIGRATION SOURCE; persistence schema and writers/readers require mapping |
| `server/services` | 138 | LEGACY / MIGRATION SOURCE; domain and integration semantics require mapping |
| `server/jobs` | 7 | LEGACY / MIGRATION SOURCE; includes active-looking worker/job modules and one inert scheduler stub |
| `server/config` | 30 | LEGACY / MIGRATION SOURCE; database, Redis, queues, cron and integration configuration remain |
| `server/utils` | 89 | LEGACY / MIGRATION SOURCE; callers and business authority require mapping |

These are root-directory counts, not totals for nested descendants. The directory contents include duplicates, alternate versions and potentially orphaned modules. A filename alone is not proof of a live route or capability. The next forensic pass must traverse nested directories, follow imports from mounted modules, and search frontend, worker, scripts and deployment references before classifying a file as orphaned.

## 4. Middleware and security boundary inventory

The application-level middleware observed in `server/app.js` includes:

1. CORS response policy and OPTIONS handling.
2. Latency and forensic response headers.
3. Tenant-keyed Express rate limiting.
4. Helmet security headers.
5. JSON and URL-encoded body parsing.
6. Development request logging.
7. `tenantContext`.
8. `integrityShield` with explicit bypass path conditions.
9. Express error handling.

The shared API router additionally imports and applies:

- `auth.middleware.js`
- `tenantBypass.js`
- `tenantGuard.js`
- tenant-isolation middleware
- audit logging middleware
- telemetry, circuit-breaker, Redis and logger helpers.

The middleware tree includes separate authentication, MFA, role, permission, tenant-resolution, tenant-scope, tenant-bypass, forensic, security, audit, billing and compliance modules. Their actual ordering and semantics are not certified by directory presence. In particular, bypass rules, fallback tenant identifiers, principal/capacity authority, session freshness, CSRF, rate-limit keys, error handling and audit-failure behavior must be compared with Kennel EOS before any retirement.

## 5. Worker, scheduler and queue inventory

| Surface | Observed source behavior | Classification | Python replacement / parity |
|---|---|---|---|
| `server/app.js` | Exports the Express app and `initializeSovereignJobs(options)`; that function calls `startSyncScheduler` and can start the verification interval when invoked | LEGACY / MIGRATION SOURCE | No Python parity proven for this callable activation surface; no listener is started in this module |
| `server/jobs/scheduler.js` | Inert stub; `start()` raises a retirement error | LEGACY / RETIRED STUB | Not a replacement for all old jobs |
| `server/jobs/verificationSyncJob.js` | Mongoose aggregation over `Invoice.verificationLog`; loads invoices; calls reconciliation service; runs once immediately and schedules via `setInterval` (default 60 seconds) | LEGACY / MIGRATION SOURCE | UNKNOWN; identify canonical EOS evidence model, durable task and reconciliation route |
| `server/jobs/workerEntry.js` | Opens IORedis and Mongoose; creates BullMQ compliance, notification and invoice workers; queries expired Client records | LEGACY / MIGRATION SOURCE | UNKNOWN; map each queue consumer to Python durable worker and exact lifecycle authority |
| `server/jobs/billingCycle.js` | Uses `node-cron` weekly (Monday 00:00); reads trial/active subscriptions; calls TrialEngine and BillingEngine and audit logger | LEGACY / MIGRATION SOURCE | UNKNOWN; subscription lifecycle and billing authority must be verified in EOS; no Node financial truth |
| `server/jobs/bundleWorker.js` | Creates BullMQ Worker; reads Document records; generates document bundles and writes job/audit state | LEGACY / MIGRATION SOURCE | UNKNOWN; map document generation, job state and audit evidence |
| `server/jobs/queue.js` | Creates BullMQ queues `NOTIF_SVC`, `FIN_SYNC`, `DOC_ARCHITECT`, and `LOG_TRACKER` | LEGACY / MIGRATION SOURCE | UNKNOWN; map producers, consumers, payload contracts, retry and idempotency |
| `server/jobs/riskArchivalJob.js` | Uses node-cron, Mongoose RiskAssessment reads and sessions, Redis client, archival writes and delayed timer behavior | LEGACY / MIGRATION SOURCE | UNKNOWN; map archive authority, retention/legal-hold policy, transaction and notification semantics |
| `server/config/cron-jobs.yml` | Legacy cron configuration remains | UNKNOWN / REQUIRES FORENSICS | Determine whether any external scheduler consumes this file |
| `server/config/queues.js` | Legacy queue configuration remains | LEGACY / MIGRATION SOURCE | Map every queue and producer/consumer to Python EOS contracts |
| `server/worker.js` | Inert export-only retirement stub; no imports or work on load | LEGACY / RETIRED STUB | Not a replacement for the legacy job inventory |

The presence of a Python durable worker does not prove semantic parity with any specific legacy job. The Express module also exports a callable scheduler initializer, so disabling a Node process launcher alone does not prove that no test, script, or external consumer can activate the legacy timer. Each job requires trigger, cadence, retry, idempotency, tenant scope, persistence, audit, failure recovery, and lifecycle-authority mapping.

## 6. Database, cache and external integration consumers

### 6.1 Directly observed legacy persistence consumers

| Consumer | Observed dependency | Risk / required mapping |
|---|---|---|
| `server/app.js` local Lead handler | Dynamic Mongoose import; direct `connection.db.collection(...).findOneAndUpdate`; candidate collection probing | Tenant scope absent from visible query; must remain unavailable and be replaced only through authorized EOS command |
| `server/routes/api.js` | Mongoose connection readiness and Redis health | Health projection must derive from canonical EOS readiness and supported dependencies |
| `server/jobs/verificationSyncJob.js` | `Invoice.aggregate`, `Invoice.findById`, reconciliation service, invoice model | Tenant-scoped aggregate, session/transaction, append-only evidence, concurrency and replay semantics unverified |
| `server/jobs/workerEntry.js` | BullMQ, IORedis, Mongoose, Client model, `Client.find` | Tenant scope, lifecycle authority, retry and audit semantics unverified |
| `server/config/database.js` | Mongoose connection, reconnect timer and connection listeners | Legacy independent database lifecycle |
| `server/config/db.js` | Mongoose connection facade and disconnect | Legacy independent database lifecycle |
| `server/config/redis.js` | Redis client creation, connect/reconnect, health and disconnect | Legacy cache/queue/health dependency |
| `server/package.json` | Express, Mongoose, Redis, BullMQ, Agenda, cron and other backend packages | Dependency tree is not yet isolated to frontend/test tooling |

The full model/service/controller route-to-collection graph is not yet established. The tables above are confirmed examples, not a complete database-consumer inventory.

### 6.2 External integrations still requiring route-to-provider mapping

The legacy dependency and source trees contain email/SMS, payment, banking/treasury, Redis/queue, AI/model, document/PDF, storage, blockchain/cryptographic, regulatory, court, identity and notification integration code. Each integration must be classified as CANONICAL, ADAPTER, EXTERNAL CAPABILITY, EVIDENCE SOURCE, PROJECTION, LEGACY / MIGRATION SOURCE, DUPLICATE / OVERLAPPING, ORPHANED, or UNKNOWN / REQUIRES FORENSICS.

No integration is certified as safely removable based solely on package names or source-directory presence. For payment and settlement, external providers may supply evidence or execution capability only under Kennel EOS authorization and reconciliation; they do not own WILSY financial truth.

## 7. Python EOS parity rule

A legacy capability is eligible for retirement only after all of the following are evidenced:

1. Canonical Python domain/service and persistence authority identified.
2. Authenticated FastAPI route and exact IAM permission binding identified.
3. Tenant isolation, membership/capacity and authorization failure behavior tested.
4. Client/API contract and frontend callers mapped; no remaining Node BFF transport dependency.
5. Audit/evidence, observability, notifications and integration behavior mapped.
6. Idempotency, concurrency, transaction ownership and recovery behavior tested where applicable.
7. Real Mongo replica-set tests pass for transaction-sensitive behavior.
8. Route-level tests prove the canonical Python endpoint, including cross-tenant denial.
9. No legacy worker, scheduler, process manager or deployment manifest still activates the old implementation.
10. Exact-head CI and local verification are green; no infrastructure absence is represented as a passing certification.

Matching endpoint names or passing static tests alone do not establish parity.

## 8. Production traffic and deployment boundary

Repository source can establish intended manifests and local proxy configuration. It cannot prove the live external ingress target, DNS, load balancer, process list, PM2 state, or host supervisor.

Before any production cutover, an authorized operator must separately verify:

- The actual ingress/load-balancer target points directly to Kennel EOS.
- No Node BFF, Express listener, PM2 application, or Node worker is running on the host.
- Kennel EOS health/readiness and authenticated route probes pass directly.
- Worker activation is explicit and owned by the Python EOS process contract.
- Rollback and recovery are documented without reintroducing Node business authority.

No external host action, production deployment, migration, worker activation, or cutover is claimed by this document.

## 9. Remaining forensic work and certification state

**Status: PARTIAL — NOT OPERATIONALLY CERTIFIED**

The route mount inventory is established for `server/app.js` and `server/routes/api.js`. The full route/controller/middleware import graph, all nested source directories, model/service database consumers, frontend callers, external integrations and per-capability Python parity remain unverified.

| | Action | File / surface | Why (blast radius) | Priority | Done? |
|---|---|---|---|---|---|
| | Inventory every mounted route and direct handler | `server/app.js`, `server/routes/api.js` | Establishes reachable Node API surface | P0 | Partial |
| | Trace every mounted route to controllers, middleware, models and services | `server/routes/**`, `server/controllers/**`, `server/middleware/**` | Prevents capability loss and authorization bypass | P0 | No |
| | Inventory all worker, scheduler, queue and timer activators | `server/jobs/**`, `server/config/**`, `server/app.js` | Prevents duplicate or unauthorized background execution | P0 | Partial |
| | Complete model/database/cache consumer graph | `server/models/**`, `server/services/**`, `server/config/**` | Protects tenant, transaction and data integrity | P0 | No |
| | Map each capability to authenticated Python EOS authority | `tools/eos/**`, frontend clients and API contracts | Proves parity before retirement | P0 | No |
| | Retire Express route/controller/middleware and server dependency tree after parity | `server/**`, package manifests and lockfiles | Removes all Node backend implementation | P1 | No |
| | Prove production ingress directly targets Kennel EOS | Production deployment and external host | Prevents hidden Node BFF traffic path | P0 | No |

### Verification and checks

- Source inspection: completed for the application imports/mounts, shared API router imports/mounts, named worker/scheduler modules, database and Redis connection modules, and top-level directory enumeration.
- Exact route/controller/middleware-to-domain parity: not completed.
- Full recursive route/controller/middleware/model/service inventory: not completed.
- Pyright, Python compilation, route integration tests and real replica-set certification: not run as part of this documentation-only update.
- Production host/ingress inspection: not run; requires authorized operational access.
- No claim of operational certification or production readiness is made.

**Artifact score:** 6/10 for this partial forensic inventory; known gaps prevent a higher score.  
**Runtime contract:** supported Python runtime tests passed in the earlier local checkpoint; that evidence does not certify legacy parity.  
**Sovereign artifact contract:** this document carries the required versioned header, changelog and end seal; the broader inventory and runtime contract remain incomplete.

---

**END OF INVENTORY — PARITY AND RETIREMENT NOT YET CERTIFIED**

ARTIFACT: eos-runtime-database-consumer-inventory.md
VERSION: v2.2.0-KENNEL-EOS-LEGACY-NODE-FORENSIC-INVENTORY
AUTHORITY BOUNDARY: forensic inventory only; Kennel EOS owns business authority.
TENANT POSTURE: no tenant data access or authority granted; legacy isolation remains under review.
FAIL-CLOSED POSTURE: UNKNOWN parity is not treated as certified or safe to retire.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
END OF WILSY OS SOVEREIGN ARTIFACT
