# WILSY OS — Kennel EOS runtime and legacy Node forensic inventory

**TITLE:** Kennel EOS Runtime and Legacy Node Forensic Inventory  
**VERSION:** v2.6.0-KENNEL-EOS-LEGACY-NODE-FORENSIC-INVENTORY  
**AUTHORITY:** Wilsy OS Core Governance  
**EPITOME:** Evidence-based inventory of the supported Python runtime and the remaining Express, route, middleware, worker, scheduler, persistence, and integration surfaces that must be mapped before legacy retirement.  
**ABSOLUTE CANONICAL PATH:** /Users/wilsonkhanyezi/legal-doc-system/docs/architecture/eos-runtime-database-consumer-inventory.md  
**COLLABORATION / OWNERSHIP:** Wilson Khanyezi (Founder); Codex (AI Engineering)  
**CERTIFICATION / UPDATE DATE:** 2026-11-08  
**CHANGELOG:**
- v2.6.0-KENNEL-EOS-LEGACY-NODE-FORENSIC-INVENTORY: Corrects the route crosswalk and restores the complete version history after adding root services, launchers and legacy test inventory.
- v2.5.0-KENNEL-EOS-LEGACY-NODE-FORENSIC-INVENTORY: Adds root Node microservices, active-looking launchers, 124 Node test files, and unsafe legacy AI/crypto/ledger/standards implementations.
- v2.4.0-KENNEL-EOS-LEGACY-NODE-FORENSIC-INVENTORY: Adds Python candidate crosswalk and identifies QR/offline reconciliation as missing/unverified parity, including tenant, signature, audit and transaction hazards.
- v2.3.0-KENNEL-EOS-LEGACY-NODE-FORENSIC-INVENTORY: Adds checked-in Nginx, Helm, Kubernetes and Node deployment-automation findings that prevent direct-Kennel-ingress certification.
- v2.2.0-KENNEL-EOS-LEGACY-NODE-FORENSIC-INVENTORY: Records mounted routes, middleware, callable scheduler activation, queue workers, Mongoose/Redis consumers and explicit parity gaps.
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

The router mounts `wilsyAiRoutes.js` at `/wilsy-ai` under the `/api` prefix; `server/app.js` additionally mounts the AI router at `/api/wilsy/ai`. The router also imports an AI ledger-query controller. These are separate route prefixes and require separate caller mapping. Exact handler semantics, authorization, persistence, audit and client callers for each mounted module remain to be mapped. No parity is inferred from matching route names.

### 3.3 Python EOS candidate crosswalk — candidates are not parity

The canonical FastAPI composition in `tools/eos/api/server.py` includes the following relevant Python routers. These are candidate authorities based on domain and API composition only; route-level request/response, authorization, persistence, audit, client, and lifecycle parity have not been proven.

| Legacy Express surface | Python EOS candidate / authority | Classification | Parity status |
|---|---|---|---|
| `authRoutes.js` | `auth_router.py`, `global_principal_auth_router.py` | CANONICAL candidate | Not proven endpoint-by-endpoint; global principal, explicit membership/capacity, MFA and session-currentness contracts must be compared |
| `tenantRoutes.js` | `tenant_router.py` | CANONICAL candidate | Not proven; legacy tenant discovery and administration flows require exact mapping |
| `billingRoutes.js` | `billing_router.py` | CANONICAL financial application boundary | Python exposes platform/client invoice, payment, statement, audit and dunning routes; exact legacy parity is unverified and HTTP cannot invent execution/paid/settlement truth |
| `subscriptionRoutes.js` | `subscription_router.py`, `plan_router.py`, billing registries | CANONICAL candidate | Not proven; entitlement and lifecycle authority must be mapped |
| `employees.js` | `employee_router.py`, `hr_workforce_directory_router.py` | CANONICAL candidate | Not proven; workforce identity and authorization parity required |
| `legal/index.js` | `legal_operations_router.py` plus specialized legal operations routers | CANONICAL candidate | Not proven; complete legal lifecycle/client/mobile/evidence parity required |
| `brandingRoutes.js` | `tenant_branding_router.py` | CANONICAL candidate | Not proven; tenant ownership, asset delivery and cache invalidation must be compared |
| `telemetryRoutes.js` | `telemetry_ingestion_router.py` | CANONICAL candidate | Not proven; event identity, tenant scope and delivery semantics must be compared |
| `wilsyAiRoutes.js` | `wilsy_ai_legal_gateway_router.py`, `wilsy_ai_reasoning_router.py`, `wilsy_ai_legal_services_router.py`, `wilsy_ai_advisory_router.py` | CANONICAL candidate | Not proven; entitlement, evidence, model-provider and audit boundaries must be compared |
| `contractRoutes.js` | `commercial_agreement_router.py` | CANONICAL candidate | Not proven; signing, acceptance and immutable evidence contracts must be compared |
| `crmCommandRoutes.js`, `wilsyCrmLiveRoutes.js`, `wilsyCrmIntelligenceRoutes.js` | `owner_commercial_workspace_router.py` and `tools/eos/crm/**` | CANONICAL partial candidate | Owner workspace endpoints are certified separately; this does not establish parity for the full legacy CRM route surface |
| `assetRoutes.js` | `candidate_evidence_upload_router.py`, `legal_evidence_upload_router.py`, `artifact_pdf_router.py` | CANONICAL partial candidate | Upload, evidence and artifact capabilities differ; no blanket parity |
| `qrRoutes.js` | No dedicated Python QR router found. `billing_router.py` exposes invoice/statement operations and `forensic_merkle_router.py` verifies forensic chains, but neither establishes the legacy QR contract | UNKNOWN / MISSING PARITY | Missing/unverified signed-payload QR verification, trace lookup, verify-and-persist and offline/online reconciliation routes |
| `financeRoutes.js`, `revenueRoutes.js`, `ledgerRoutes.js`, `treasuryRoutes.js`, `invoiceRoutes.js`, `statements.routes.js`, `dunningRoutes.js` | `billing_router.py`, SaaS billing registries and Kennel EOS financial execution boundary | CANONICAL candidate | Not proven per endpoint; do not retain or reintroduce Node financial truth |
| `complianceRoutes.js`, `analyticsRoutes.js`, `lpcRoutes.js`, `courtRoutes.js`, `jurisdictionRoutes.js`, `nodeRoutes.js`, `sovereignSeizureRoutes.js` | No exact one-to-one Python router mapping established in this pass | UNKNOWN / REQUIRES FORENSICS | Missing or unverified until exact routes, controllers, data and callers are traced |

### 3.4 QR verification and offline reconciliation — identified parity gap

The legacy QR router is mounted both directly at `/api/qr` in `server/app.js` and as `/qr` inside `server/routes/api.js`, which is itself mounted under `/api`. Its three declared operations are:

- `GET /api/qr/audit/:traceId`: authenticated read-only invoice/statement verification.
- `POST /api/qr/audit/:traceId/verify`: authenticated verify-and-persist operation that sets verification state and appends audit/reconciliation evidence.
- `GET /api/qr/verify/:payload`: authenticated signed QR payload verification.

The legacy controller resolves tenant context from user, header, query, or middleware state and falls back to `MASTER`; it recognizes legacy sovereign roles and tenant aliases. It also contains optional audit/anomaly imports that fall back to no-op implementations, and a missing PKI public key disables PKI verification. These behaviors are not an acceptable migration contract and must not be copied into EOS.

The legacy `Invoice` and `Statement` Mongoose schemas persist `traceId`, `qrVerified`, and `qrVerifiedAt`; invoices additionally persist `verificationLog` entries with local/server timestamps and a resolution. The old reconciliation service appends to the Mongoose invoice document and calls `save()` without an explicit caller-owned session/transaction parameter. Its tenant fallback includes `GLOBAL_ROOT`.

The old scheduler aggregates invoices whose latest verification entry is `LocalOnly`, then loads and updates each invoice by ID. The aggregate is not visibly tenant-filtered, and the operation has no explicit caller-owned transaction/session boundary. It is invoked immediately and on a 60-second interval when `initializeSovereignJobs()` is called.

Python EOS currently has canonical client invoice issuance/read operations in `billing_router.py`, a commercial statement domain/registry, and forensic Merkle verification. These are related authorities, not proof that QR signing, trace lookup, QR verification persistence, or offline timestamp reconciliation has been implemented. No Python QR router or equivalent offline reconciliation worker was found in the inspected `tools/eos/**` path inventory.

**Migration decision:** treat the legacy QR and offline reconciliation feature as a missing/unverified capability. Before retiring its source or claiming parity, define a Python-owned, tenant-scoped evidence contract; use canonical EOS invoice/statement identities and approved signing/trust material; persist append-only verification evidence with deterministic idempotency and caller-owned transaction/session semantics; add authenticated routes and exact IAM permissions; and certify cross-tenant denial, signature failure, replay, concurrency and real replica-set recovery. No legacy fallback tenant, no-op audit fallback, or scheduler-owned lifecycle authority may be carried forward.

### 3.5 Separate root Node service tree

The repository also contains a second Node service architecture outside `server/`. These services are separate from the Express application and must be included in the retirement graph.

| Service | Observed implementation | Activation / port | Classification | Python EOS parity |
|---|---|---|---|---|
| `services/ai/aiService.js` | Express `POST /risk-score`; deterministic rule-based simulation using `area` and `defendantHistory`; `crimeStats` is accepted but not used | Direct Node execution; listens on 6500; package has no start script | LEGACY / MIGRATION SOURCE; simulated model | Candidate AI/legal advisory routers exist, but this risk-score contract has no proven parity; do not present this as a trained model |
| `services/auth/authService.js` | Express router with `/register`, `/login`, `/refresh`, `/me`; legacy User Mongoose model; default JWT secret fallback; no global-principal MFA/session authority | Package declares `node index.js`, but no `index.js` is present in the enumerated directory; import reachability remains unverified | LEGACY / MIGRATION SOURCE | Python global-principal authentication is the canonical candidate; exact route and migration parity not certified |
| `services/billing/` | Package manifest only; no service source or start script found | No current service entrypoint found | ORPHANED / UNKNOWN | Python `billing_router.py` is canonical candidate; no Node capability inferred from an empty package |
| `services/crypto/cryptoService.js` | Express `POST /sign-document`; generates a fresh RSA key pair per request, mixes request hash with a defaultable secret, returns signature without a durable public-key/certificate binding; labels provider as `Wilsy-Vault-v1` | Direct Node execution; listens on 6600; package has no start script | LEGACY / UNSAFE SIMULATION | Institutional PKI/KMS and signer-enrollment services are canonical candidates; the legacy behavior is not cryptographic parity and must never be treated as HSM/KMS evidence |
| `services/ledger/repair_ledger_service.js` | Writes a new `index.js` containing Express/Mongoose `POST /events`, `GET /events`, and `/health`; global sequence, SHA-256 chain, no tenant scope, no caller-owned transaction or concurrency-safe sequence reservation | Package has no start script; repair script can generate a runnable Node service on port 6000 | LEGACY / UNSAFE FINANCIAL AUTHORITY | Kennel EOS financial and audit registries are canonical; this global ledger is not valid financial/audit truth |
| `services/standards/standardsService.js` | Express `POST /validate`, `GET /rules`; Mongoose Rule collection; global default seeding; falls back to High Court rules when requested court type is missing; no visible tenant or authenticated permission guard | `npm start`; listens on 6100 | LEGACY / MIGRATION SOURCE | Python legal operations/jurisdiction rules are candidates; exact rule schema, jurisdiction authority, versioning and tenant parity not established |
| `services/httpSetup.js` | Redux-aware HTTP interceptor importing modules under `client/src` from a root `services/` path | Client-side import candidate; no server listener | CLIENT SURFACE / MISPLACED SOURCE | Frontend transport only; verify actual client import callers before moving or deleting |

The root `services/` directory also contains `AdvancedDocumentGenerationService.js`, `clientOnboardingService.js`, and `ficaScreeningService.js`. Their import callers, persistence consumers and frontend/backend boundaries remain unverified. They are not classified as Python parity merely because related EOS modules exist.

The `services/ledger/repair_ledger_service.js` source is especially dangerous: it can generate an executable ledger server that derives sequence and hash-chain state from a global collection without tenant scope or a transaction-safe sequence reservation. It must not be run or accepted as ledger authority.

### 3.4 Route, controller and middleware source trees

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
| `server/tests` | 136 entries, including 124 Node test files and 132 JS/CJS/MJS files | LEGACY TEST SOURCE; not browser tests; migrate test intent to Python EOS or retire only after capability parity |

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

### 8.1 Stale or contradictory repository deployment surfaces

The following repository files still describe non-Kennel or unverified application targets:

| File / surface | Observed configuration | Classification | Required disposition |
|---|---|---|---|
| `start_all.sh` | Starts ledger and standards with `npm start`, then starts `server/` with `npm start`; kills ports 3001, 6000 and 6100 | LEGACY / MIGRATION SOURCE | Must be replaced by an EOS-owned launcher; no Node service activation |
| `start_wilsy_os.sh` | Attempts to start ledger, standards, billing, AI, crypto and server services on ports 6000/6100/6400/6500/6600/3001 | LEGACY / MIGRATION SOURCE | Multiple service packages lack declared start scripts; do not use |
| `GlobalLaunchSequence.sh` | Runs Node validation suite, starts `server/` with `npm start`, then starts Vite | LEGACY / MIGRATION SOURCE | Replace with a governed Python EOS + frontend development command |
| `Genesis_Ignition.sh` | Invokes legacy deployment automation, imports `server/app.js` in Node, and calls legacy ForensicService signing | LEGACY / MIGRATION SOURCE | No production ignition authority |
| `Sovereign_Deployment_Automation.sh` | Runs Node server tests, frontend test, build, and Node manifest generator | LEGACY / MIGRATION SOURCE | Frontend build may remain; server Node tests and Node manifest generation must be migrated or retired |
| `deploy-production.sh` | Runs Node/npm checks and server Mocha tests; prints `npm start` as deployment command | LEGACY / MIGRATION SOURCE | Not an approved production deployment workflow |
| `deploy-prod.sh` | Runs `server/` npm tests, builds images, and invokes Compose deployment | LEGACY / MIGRATION SOURCE | Must not be used until server tests and every target image/manifest are reconciled with Python EOS |
| `setup.sh` | Installs dependencies under `server/` | LEGACY / MIGRATION SOURCE | Do not use; server dependency tree is not frontend tooling |
| `production-ready.sh` | Checks legacy server test files, Node modules and server production environment | LEGACY / MIGRATION SOURCE | Its green status cannot certify Kennel EOS readiness |
| `server/scripts/ci/deploy.sh` | Runs Node Mocha tests, `npm ci`, and generates a deployment manifest | LEGACY / MIGRATION SOURCE | Replace with Python EOS certification/deployment workflow |
| `server/scripts/SovereignDeployment.script.js` | Runs server Node test/audit commands and records legacy PM2/Docker deployment intent | LEGACY / MIGRATION SOURCE | Not approved for deployment |
| `server/scripts/generateManifest.js` | Signs a legacy manifest through `ForensicService` and writes under `server/dist` | LEGACY / MIGRATION SOURCE | Map manifest semantics to canonical EOS evidence before deletion |
| `nginx.conf` | API upstream `wilsy-os:3000`; investor upstream `wilsy-os:9096`; API and investor paths proxy to those upstreams | LEGACY / MIGRATION SOURCE | Replace only after service and investor capability mapping; target must be an explicitly named Kennel EOS service on 9095 |
| `infra/nginx/fortress-lb.conf` | Regional upstreams point to multiple private IPs on port 3000; health probe uses `/api/v1/sys/health` | LEGACY / MIGRATION SOURCE | Infrastructure owner must identify each node and prove it runs Kennel EOS before changing the target |
| `k8s/predictive-deployment.yaml` | Kubernetes Deployment uses `ghcr.io/wilsonkhanyezi/wilsy-os-core:latest`, container and probes on port 3000, and a `NODE_NAME` environment field | UNKNOWN / REQUIRES FORENSICS | Inspect image provenance and all consumers; do not assume this image is Python EOS |
| `charts/legal-os/Chart.yaml` and subcharts | Umbrella chart declares separate gateway, auth, ledger, billing, AI and crypto microservices; billing and AI templates deploy separate containers on ports 6400 and 6500 | LEGACY / DUPLICATE / OVERLAPPING | Determine whether the chart is referenced by any release; replace with a single Kennel EOS application service only after every capability is mapped |
| `charts/legal-os/values.yaml` | Includes a global `tenantId: GLOBAL_ROOT` and independent service image repositories | LEGACY / MIGRATION SOURCE | Must not be used as canonical tenant authority or production configuration |
| `charts/legal-os/values-production.yaml` | Enables a public ingress host and TLS but does not establish a direct Kennel EOS service target | UNKNOWN / REQUIRES FORENSICS | Resolve chart templates and release references; no direct EOS ingress claim |
| `Sovereign_Deployment_Automation.sh` | Runs server-side Node tests and invokes `node scripts/generateManifest.js` from `server/` | LEGACY / MIGRATION SOURCE | Retire or replace with a governed Python EOS deployment workflow; Node is not permitted as deployment/business runtime |
| `server/scripts/generateManifest.js` | Imports a legacy ForensicService and writes a generated manifest under `server/dist` | LEGACY / MIGRATION SOURCE | Map evidence/signing contract to canonical EOS artifact issuance before removal |
| `server/scripts/SovereignDeployment.script.js` | Executes Node deployment orchestration and contains a PM2/Docker switch placeholder | LEGACY / MIGRATION SOURCE | Must not be an authorized production deployment path |

The above are repository-defined configuration sources. Their presence does not prove that they are currently deployed, but it prevents certification that every checked-in ingress and deployment manifest already targets Kennel EOS directly. The root `k8s/predictive-deployment.yaml` is separate from the retired `server/k8s/` stubs.

Before any production cutover, an authorized operator must separately verify:

- The actual ingress/load-balancer target points directly to Kennel EOS.
- No Node BFF, Express listener, PM2 application, or Node worker is running on the host.
- Kennel EOS health/readiness and authenticated route probes pass directly.
- Worker activation is explicit and owned by the Python EOS process contract.
- Rollback and recovery are documented without reintroducing Node business authority.

No external host action, production deployment, migration, worker activation, or cutover is claimed by this document. The repository-defined Nginx, Helm and Kubernetes surfaces above are known unresolved gates; no merge or deployment can be treated as certified until each is reconciled.

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
VERSION: v2.6.0-KENNEL-EOS-LEGACY-NODE-FORENSIC-INVENTORY
AUTHORITY BOUNDARY: forensic inventory only; Kennel EOS owns business authority.
TENANT POSTURE: no tenant data access or authority granted; legacy isolation remains under review.
FAIL-CLOSED POSTURE: UNKNOWN parity is not treated as certified or safe to retire.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
END OF WILSY OS SOVEREIGN ARTIFACT
