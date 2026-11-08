# EOS runtime database-consumer inventory

**Version:** v2.0.0-KENNEL-EOS-CANONICAL-RUNTIME  
**Scope:** repository-defined application and worker entrypoints.  
**Boundary:** inventory evidence only; this document does not authorize deployment or production database changes.

## Canonical application and business authority

Kennel EOS is the existing canonical application/API and business authority. The Python EOS API is launched through `tools.eos.api.server:app` on port 9095. Business registries and API routes resolve the kernel-owned database/client or receive a caller-owned `client + database + session` graph and enforce the same-client transaction boundary.

## Supported runtime entrypoints

| Entrypoint | Runtime role | Status |
|---|---|---|
| `npm run dev` → `scripts/start-dev-stack.sh` | Python EOS + Vite development stack | Supported; Node is frontend tooling only |
| `npm run dev:kernel` | Python EOS API | Supported |
| `npm run prod:kernel` | Python EOS API | Supported |
| Root `Dockerfile` / `Dockerfile.eos` | Python Kennel EOS API | Supported |
| `docker-compose.prod.yml` | Python Kennel EOS API; opt-in Python durable worker | Supported candidate; deployment still requires approval |
| `tools/eos/runtime/worker_process.py` | Durable EOS worker | Supported only through explicit `python-workers` profile |

## Retired Node backend entrypoints

The following are deliberately disabled and must not be restored as application runtime paths:

- `server/ecosystem.config.js` exports an empty PM2 application list.
- `server/package.json` has no `start`, `dev`, or `predev` backend scripts and no Node server main entry.
- `server/server.js` remains temporarily importable for legacy test isolation, but direct execution exits non-zero with a retirement message. It is not an approved proxy or application runtime.
- `server/deploy.sh` fails closed and cannot install dependencies, run migrations, or reload PM2.
- `server/Dockerfile` and `server/Dockerfile.worker` are non-buildable retirement stubs based on `scratch`; they cannot produce Node backend images.

Node remains permitted for frontend build, test and browser-certification tooling. This exception does not permit Express, PM2, a Node BFF, a Node worker, or Node-owned business/API execution.

## Canonical business database owner

The Python EOS kernel owns the business MongoDB client/database lifecycle through `tools/eos/kernel/db.py`. Tenant, plan, subscription, employee, principal, billing and owner-workspace registries use this canonical database or a caller-owned same-client transaction graph.

## Explicit non-business exception

`tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_runtime.py` creates a separate Mongo client only for its dedicated reconciliation audit sink. It requires `WILSY_LEGAL_EVIDENCE_RECONCILIATION_AUDIT_MONGODB_URI`, compares that target with the canonical `MONGODB_URI`, requires TLS, and rejects an audit database whose client is the business database client. This is an isolated audit sink, not a business-registry connection or fallback business database.

## External operational boundary

Repository changes cannot prove or stop a PM2 process already running on an external host, nor can they alter an out-of-repository load balancer, DNS record, ingress, or process supervisor. Before any production traffic cutover, the authorized operator must inspect the actual host process list and ingress target, verify the direct Kennel EOS endpoint and health/readiness, then remove any externally managed stale PM2 process and proxy route. No such host action is claimed by this repository change.

## Certification

`tests/unit/test_python_eos_runtime_deployment.py` asserts that the supported production containers are Python EOS and that the retired Node backend has no supported PM2, package-script, direct-execution, deployment-script, or Docker-image entrypoint.
