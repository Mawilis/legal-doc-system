# WILSY OS — deployment authority and runtime boundary

**TITLE:** Kennel EOS Deployment Authority and Production Cutover Boundary  
**VERSION:** v1.2.0-KENNEL-EOS-DEPLOYMENT-AUTHORITY-BOUNDARY  
**AUTHORITY:** Wilsy OS Core Governance  
**EPITOME:** Defines Python Kennel EOS as the supported application/API runtime while explicitly identifying repository deployment and ingress surfaces that remain stale or unverified.  
**ABSOLUTE CANONICAL PATH:** /Users/wilsonkhanyezi/legal-doc-system/DEPLOYMENT.md  
**COLLABORATION / OWNERSHIP:** Wilson Khanyezi (Founder); Kennel EOS runtime owners; Codex (AI Engineering).  
**CERTIFICATION / UPDATE DATE:** 2026-11-08  
**CHANGELOG:**
- v1.2.0-KENNEL-EOS-DEPLOYMENT-AUTHORITY-BOUNDARY: Adds root Node service listeners, launch scripts, 124 non-browser Node test files and unsafe ledger/crypto/AI/standards surfaces to the deployment no-go boundary.
- v1.1.0-KENNEL-EOS-DEPLOYMENT-AUTHORITY-BOUNDARY: Removes the inaccurate claim that all legacy deployment scripts are retired; identifies root Node ignition/deployment automation and stale Nginx/Kubernetes/Helm targets as unresolved no-go gates.
- v1.0.0: Established Python EOS as the supported deployment candidate and separated production activation from CI.
**COMPLIANCE:** AGENTS.md v1.2.0; ENGINEERING_CONSTITUTION.md v1.1.0.  
**SECURITY / PRIVACY POSTURE:** No production credentials, private keys, or host access are included. Repository manifests are not evidence of live infrastructure state.  
**TENANT BOUNDARY:** No tenant data or tenant authority is established by deployment configuration.  
**AUTHORITY BOUNDARY:** Kennel EOS is the only supported application/API and business authority. This document does not authorize a deployment or migration.  
**FINANCIAL AUTHORITY BOUNDARY:** Kennel EOS exclusively owns financial execution and settlement truth.  
**TRANSACTION BOUNDARY:** No database migration, worker activation, transaction, or cutover is performed.

WILSY OWNS BUSINESS TRUTH. KENNEL EOS IS THE EXCLUSIVE FINANCIAL EXECUTION AUTHORITY.

---

## Canonical runtime candidate

The supported application/API runtime is Python Kennel EOS:

```bash
python -m uvicorn tools.eos.api.server:app --host 0.0.0.0 --port 9095
```

The repository-root `Dockerfile`, `Dockerfile.eos`, and `docker-compose.prod.yml` describe the Python EOS candidate runtime. The durable worker is a separate Python process and is opt-in through the `python-workers` Compose profile.

The Vite development proxy is intended to connect directly to Kennel EOS on port 9095. Node is permitted for frontend build and browser-certification tooling only; it is not the application API, business runtime, database owner, worker, or production deployment authority.

## Development

The supported local development commands are:

```bash
npm run dev
npm run dev:kernel
```

The development stack starts the Python EOS API and frontend tooling. Confirm the current script implementation before using it; do not substitute any server-directory npm script.

## Legacy paths — not approved for execution

The following checked-in sources remain and must not be treated as retired merely because the old server listener and PM2 launcher were removed:

- `server/app.js` and the `server/routes/**`, `server/controllers/**`, `server/middleware/**`, `server/models/**`, `server/services/**`, and `server/jobs/**` source trees.
- `server/package.json`, which still contains Express, Mongoose, Redis, BullMQ, cron and other server-oriented dependencies.
- `Sovereign_Deployment_Automation.sh`, which runs server-side Node tests and invokes `server/scripts/generateManifest.js`.
- `Genesis_Ignition.sh`, which invokes the legacy deployment script and runs a Node import/signing sequence against `server/app.js`.
- `server/scripts/SovereignDeployment.script.js`, which is a legacy Node deployment orchestrator.
- `server/scripts/generateManifest.js`, which invokes the legacy ForensicService and writes under `server/dist`.
- Root `services/ai`, `services/auth`, `services/crypto`, `services/ledger`, and `services/standards` contain separate Node business/service implementations. The AI and crypto modules expose Express listeners; standards has an npm start listener; auth contains a legacy JWT router; ledger repair code can generate a Mongoose-backed global ledger service. `services/billing` is an empty package directory. These are not approved runtimes.
- `start_all.sh`, `start_wilsy_os.sh`, and `GlobalLaunchSequence.sh` attempt to start Node service processes. `Genesis_Ignition.sh` and `Sovereign_Deployment_Automation.sh` execute legacy Node deployment/manifest paths.
- `server/tests/**` contains 124 Node test files (136 directory entries); they are not browser tests and must be ported to Python EOS or retired only after capability parity.

Do not run `pm2`, `npm start` or other server-directory scripts, `server/app.js`, any legacy worker/cron module, root service modules, `start_all.sh`, `start_wilsy_os.sh`, `GlobalLaunchSequence.sh`, `Genesis_Ignition.sh`, `Sovereign_Deployment_Automation.sh`, `deploy-production.sh`, `deploy-prod.sh`, or server deployment scripts. The presence of these files is a migration finding, not permission to execute them.

## Unresolved ingress and deployment manifests

The repository currently contains conflicting deployment descriptions:

| File | Observed target | Status |
|---|---|---|
| `nginx.conf` | `wilsy-os:3000` for API; separate investor upstream `wilsy-os:9096` | Legacy / unverified |
| `infra/nginx/fortress-lb.conf` | Multiple regional private IPs on port 3000 | Legacy / unverified |
| `k8s/predictive-deployment.yaml` | `wilsy-os-core:latest`, port 3000 and Node-named environment field | Runtime provenance unknown |
| `charts/legal-os/Chart.yaml` and subcharts | Separate gateway, auth, ledger, billing, AI and crypto microservices | Legacy / duplicate architecture; release usage unverified |
| `charts/legal-os/values.yaml` | Includes `GLOBAL_ROOT` tenant default and independent microservice images | Not an approved canonical tenant/runtime contract |
| `charts/legal-os/values-production.yaml` | Public ingress host/TLS without demonstrated direct Kennel EOS service binding | Unverified |

The retired `server/k8s/` files are inert stubs. That does not retire the separate root `k8s/predictive-deployment.yaml` or the root Helm/Nginx configuration.

## Production no-go conditions

Production remains NO-GO until all of these are satisfied:

1. Every checked-in deployment, ingress, Nginx, Helm, Kubernetes, root service, launcher and ignition path is classified and either retired or proven to target Kennel EOS directly.
2. The actual external load balancer, DNS, ingress, process supervisor and host process list are inspected by an authorized operator. Repository source alone cannot prove live routing.
3. No Node BFF, Express listener, PM2 application, Node worker, Node cron, or legacy deployment script can be activated.
4. Kennel EOS readiness and authenticated route probes pass directly against port 9095.
5. Approved secrets, workload identity, Mongo replica-set connectivity, audit storage, and independent security review are verified.
6. Every business capability formerly served by Node has authenticated Python EOS route, permission, tenant-isolation, audit, persistence and client parity tests.
7. Transaction-sensitive flows pass real Mongo replica-set certification, and no unavailable infrastructure is represented as a passing test.
8. Explicit operational approval is obtained before production activation.

A successful build or CI run is not production authorization. Do not activate the optional worker, perform database migrations, or cut over ingress without separate approval.

## Legal-evidence reconciliation

The dedicated internal route is `POST /api/legal-operations/evidence-provider/reconciliation`; it is not the generic `/runtime/execute` endpoint.

That service has its own production security and real-Mongo certification gates. It is not evidence that the legacy QR/offline verification feature has Python EOS parity.

---

**Status: PYTHON EOS IS THE SUPPORTED RUNTIME CANDIDATE; PRODUCTION INGRESS AND LEGACY PARITY REMAIN UNVERIFIED.**

ARTIFACT: DEPLOYMENT.md  
VERSION: v1.2.0-KENNEL-EOS-DEPLOYMENT-AUTHORITY-BOUNDARY  
AUTHORITY BOUNDARY: Kennel EOS is the only supported application/API authority; no deployment is authorized.  
TENANT POSTURE: no tenant authority or data access is granted.  
FAIL-CLOSED POSTURE: unresolved deployment targets block production cutover.  
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.  
END OF WILSY OS SOVEREIGN ARTIFACT
