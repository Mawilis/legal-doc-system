# Python EOS / Node Runtime Retirement — Evidence Ledger

**Branch:** `arch/python-eos-node-runtime-retirement`  
**Baseline reviewed:** `main` at `a9d80e3619ec2aeb8862c337145133469b20548f`  
**Status:** Inventory in progress; Node runtime retirement is not yet certified.

## Governing rule

Python EOS (`tools/eos/api/server.py`) is the canonical application authority. Node may only be removed after every still-consumed transport or service responsibility has a certified Python EOS or browser/build replacement. Do not infer parity from a route name, duplicate handler, or the existence of a Python container. Do not change production deployment, secrets, databases, or merge state as part of this inventory.

## Runtime surfaces and disposition

| Surface | Observed repository evidence | Disposition |
|---|---|---|
| `tools/eos/api/server.py` | Canonical FastAPI composition; dedicated EOS Dockerfile targets this application | RETAIN |
| `infra/docker/Dockerfile.eos` | Dedicated Python 3.12 / Uvicorn image, port 9095 | RETAIN |
| `.github/workflows/eos-image-publication.yml` | Existing EOS image publication workflow | RETAIN; verify production traffic/deployment cutover separately |
| `server/server.js` | Express BFF; explicit proxies for auth, tenants, employees, kernel, plans, subscriptions, billing and selective Legal routes; owns `POST /api/generate/pdf`; governance policy explicitly says RETAIN | MIGRATE FIRST; DO NOT DELETE |
| `scripts/start-dev-stack.mjs` | Starts Python EOS, Node BFF and Vite; readiness check calls `http://127.0.0.1:4000/api/kernel` | REPLACE only after Python readiness contract and browser routes are certified |
| `client/vite.config.js` | Browser development server config; sends selected APIs directly to Python port 9095 and retains Node BFF catch-all for other API paths | RETAIN during migration; route-by-route update required |
| `server/package.json` | Node server runtime and test dependencies; `server.js` is main/start target | RETAIN until its consumers have been migrated; later prune dependencies by evidence |
| root `package.json` | `dev` uses Node launcher; server scripts, browser/build scripts and test utilities coexist | SPLIT responsibilities; do not remove the manifest wholesale |
| root `Dockerfile`, compose files, server Docker/PM2 configs | Potentially active Node deployment/operations surfaces; exact deployment consumers not yet certified | HOLD until all deployment workflows/targets are mapped |
| `server/app.js` | Separate large Express application with many route/middleware mounts and PDF route; may be used by tests or other entry points | CLASSIFY before removal; not assumed equivalent to `server/server.js` |
| `server/routes/quietSurfaceRoutes.js` | Exposes `registerQuietSurfaces(app)`, including quiet `/api/telemetry/event` acknowledgement; no registration found in `server/server.js` | Candidate unreachable route module; verify all consumers before deletion |
| `server/routes/telemetryRoutes.js` | Distinct telemetry implementation with event broadcasting; search results show it is imported by `server/routes/api.js` | Not interchangeable with quiet acknowledgement; map exact mounts/callers |
| `server/vite.config.js` | Duplicate Vite configuration; no references found by repository code search | REMOVED on this branch |
| `server/debug-model.js` | Ad hoc model-debug script; no references found by repository code search | REMOVED on this branch |
| `server/fix-tenant-import.js` | Hard-coded local path and source mutation; no references found by repository code search | REMOVED on this branch |
| `server/fix-mfa.mjs` | Standalone account MFA mutation; no references found by repository code search | REMOVED on this branch |

## Known API / transport obligations

1. `server/server.js` explicitly mounts proxy surfaces for `/api/auth`, `/api/tenants`, `/api/business/tenants`, `/api/employees`, `/api/kernel`, `/api/plans`, `/api/subscriptions`, `/api/billing`, `/billing`, and `/auth`, plus selective Legal paths. The exact path rewrite, method, header, body-stream, error, and authentication contracts must be extracted before cutover.
2. `POST /api/generate/pdf` calls `generateSovereignArtifactPdf` in the Node BFF. The same controller is also used by `server/app.js` and other route modules. No certified Python parity was established in this inventory.
3. `scripts/start-dev-stack.mjs` gates client startup on both EOS kernel and BFF kernel health. A Python-only replacement must preserve readiness failure behavior, child process cleanup, port conflict handling, and correct Python health path; no replacement was made yet.
4. `client/vite.config.js` intentionally sends selected routes to Python and leaves other `/api` requests to Node. Deleting the BFF without rewriting and testing this routing would cause API failures.
5. Repository search found `registerQuietSurfaces` only in `server/routes/quietSurfaceRoutes.js`; `server/server.js` does not import it. This is a candidate orphan, but a repository-wide static search is not proof against dynamic imports or deployment-side loading. Keep until that check is certified.
6. `.github/workflows/ci.yml` installs `server` Node dependencies, runs `npm audit --omit=dev`, lints the BFF/PDF renderer, and runs the secret guard against Node paths. This is a live CI dependency and must be replaced with Python/browser equivalent gates before removing those paths.
7. `tools/eos/governance/production_surface_policy.json` explicitly classifies `server/server.js` as RETAIN. Update policy only after a documented replacement and certification.

## Exit criteria before deleting the BFF

- Produce a machine-readable route matrix of all Node-mounted paths, rewrites, methods, auth/header/body semantics and owning service.
- Prove Python EOS parity for every required endpoint or formally retire the endpoint with consumer evidence.
- Replace local startup orchestration with Python-owned readiness and preserve client startup/shutdown guarantees.
- Update Vite proxy routes and test browser flows against Python EOS without Node BFF.
- Update CI, Docker/Compose, PM2, deployment scripts and governance policy so no production path invokes the retired Node runtime.
- Run focused Python route tests, browser certification, legal-operation regression, security/audit gates, and production-image smoke tests in isolated environments.
- Only then remove Node server entry points and dependencies, and verify no references remain.

## Changes made on this branch

Four deletion commits remove only the duplicate Vite config and three unreferenced ad hoc scripts listed above. No production runtime, route, manifest, lockfile, CI workflow, deployment file, or governance policy has been deleted or altered. No test suite has yet been run against this branch; these removals are not represented as certified.
