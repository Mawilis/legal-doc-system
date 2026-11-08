# WILSY OS — legacy Node server source boundary

**TITLE:** Legacy Node Server Source and Retirement Boundary  
**VERSION:** v1.1.0-LEGACY-NODE-SOURCE-BOUNDARY  
**AUTHORITY:** Wilsy OS Core Governance  
**EPITOME:** Identifies the server directory as an unsupported legacy migration source while explicitly disclosing that Express routes, Mongoose models, Redis, BullMQ, cron jobs and callable scheduler modules remain present and are not yet safe to delete.  
**ABSOLUTE CANONICAL PATH:** /Users/wilsonkhanyezi/legal-doc-system/server/README.md  
**COLLABORATION / OWNERSHIP:** Wilson Khanyezi (Founder); Kennel EOS runtime owners; Codex (AI Engineering).  
**CERTIFICATION / UPDATE DATE:** 2026-11-08  
**CHANGELOG:**
- v1.1.0-LEGACY-NODE-SOURCE-BOUNDARY: Corrects the previous description that remaining server files were isolated test/lint tooling; records active-looking legacy source and prohibits runtime activation pending Python EOS parity.
- v1.0.0: Established the initial unsupported Node backend notice.
**COMPLIANCE:** AGENTS.md v1.2.0; ENGINEERING_CONSTITUTION.md v1.1.0.  
**SECURITY / PRIVACY POSTURE:** Do not start or expose legacy server modules. The source tree contains historical trust, authentication, tenant and persistence code that is not certified for production use.  
**TENANT BOUNDARY:** No legacy tenant fallback, bypass, or Mongoose access is authorized by this document.  
**AUTHORITY BOUNDARY:** Kennel EOS is the sole supported application/API and business authority. This directory is LEGACY / MIGRATION SOURCE, not a supported runtime.  
**FINANCIAL AUTHORITY BOUNDARY:** Kennel EOS exclusively owns financial execution and settlement truth.  
**TRANSACTION BOUNDARY:** No migration, scheduler activation, data mutation, or deployment is authorized here.

WILSY OWNS BUSINESS TRUTH. KENNEL EOS IS THE EXCLUSIVE FINANCIAL EXECUTION AUTHORITY.

---

## Supported application runtime

The supported application/API is the Python Kennel EOS FastAPI application:

```bash
python -m uvicorn tools.eos.api.server:app --host 0.0.0.0 --port 9095
```

Node may be used only for approved frontend build and browser-certification tooling. It must not provide an Express API, BFF, business command, database consumer, scheduler, worker, or deployment authority.

## Actual contents of this directory

This directory is not yet a clean historical test-only package. The current branch still contains:

- `server/app.js`: an Express application module with route imports, middleware, direct handlers, and an exported `initializeSovereignJobs(options)` activation function.
- `server/routes/**`, `server/controllers/**`, and `server/middleware/**`: legacy route, controller and security implementations, including authentication and tenant handling.
- `server/models/**` and `server/services/**`: Mongoose schemas, persistence consumers, reconciliation and integration code.
- `server/jobs/**`: legacy BullMQ workers, queues, cron jobs, and verification reconciliation.
- `server/config/**`: Mongoose, Redis, queue, and cron configuration.
- `server/package.json`: a large Node dependency manifest that still includes Express, Mongoose, Redis, BullMQ, Agenda, cron, and server-oriented packages. Its test/lint scripts do not make the dependency tree frontend-only.
- `server/tests/**`: historical Node tests. These are not browser tests and are not an approved application runtime.
- `server/scripts/**`: legacy Node deployment and manifest-generation scripts.

The absence of `server/server.js`, PM2 launchers, or the former Node Dockerfiles prevents those specific launch paths; it does not prove that the remaining modules, workers, or scripts are harmless or unreachable. The legacy app exports a callable scheduler initializer, and other repository scripts still reference old deployment tooling.

## Runtime prohibition

Do not execute:

- `npm start`, `npm run dev`, or server test/lint scripts from this directory.
- `server/app.js` as an Express application.
- Any module under `server/jobs/**` that starts a worker, queue consumer, cron schedule, or interval.
- `server/scripts/**` deployment or manifest generators.
- PM2 or a legacy server Kubernetes manifest.

The root `Sovereign_Deployment_Automation.sh` and `Genesis_Ignition.sh` still reference legacy Node deployment/test behavior and are not approved deployment paths. Root `nginx.conf`, `infra/nginx/fortress-lb.conf`, `k8s/predictive-deployment.yaml`, and the legacy Helm chart also remain unresolved. See the repository's forensic inventory for the exact route and ingress findings.

## Retirement condition

A legacy capability may be removed only after its callers, routes, controllers, middleware, models, database consumers, workers, schedulers, external integrations, data contracts, client callers, and Python EOS replacement have been mapped and certified. The required evidence includes authenticated route tests, tenant-isolation tests, caller-owned transaction/session tests, real Mongo replica-set tests where applicable, and exact-head CI.

This README does not certify route parity, production ingress, host process state, or safe deletion of the remaining server tree.

---

**Status: LEGACY / MIGRATION SOURCE — NOT A SUPPORTED RUNTIME; RETIREMENT NOT YET CERTIFIED.**

ARTIFACT: server/README.md  
VERSION: v1.1.0-LEGACY-NODE-SOURCE-BOUNDARY  
AUTHORITY BOUNDARY: no Node runtime, API, worker, scheduler, or deployment authority.  
TENANT POSTURE: no tenant access or fallback authority.  
FAIL-CLOSED POSTURE: legacy modules remain disabled pending mapped and certified Python EOS replacements.  
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.  
END OF WILSY OS SOVEREIGN ARTIFACT
