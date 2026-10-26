# Node BFF Route and Consumer Matrix

Branch: `arch/python-eos-node-runtime-retirement`  
Evidence: static review of `server/server.js`, `client/vite.config.js`, `scripts/start-dev-stack.mjs`, `tools/eos/api/server.py`, `.github/workflows/ci.yml`. This is not live parity certification.

## Route matrix

| Incoming method/path | Current behavior / rewrite | Headers and body | Errors and parity decision |
|---|---|---|---|
| GET `/ping`, `/api/ping`, `/` | Node-local status JSON | No route-specific auth shown | Python equivalent not verified; replace only after consumer check. |
| GET `/health` | Node-local health; reports optional Mongoose state and mount map | No route-specific auth shown | Not equivalent to EOS readiness until health contract is specified. |
| GET `/api/billing/ping` | Node-local diagnostic JSON | Includes target URL/mapping | Candidate removal after caller search. |
| `/api/auth/**` | BFF -> EOS `/api/auth/**`; Vite also sends direct to 9095 | BFF forwards Authorization, tenant aliases, idempotency aliases, trace/request IDs; raw stream preserved | BFF upstream failure -> 503 JSON; Vite failure -> 502 JSON. Direct EOS parity must be tested. |
| `/api/tenants/**` | BFF -> EOS `/api/tenants/**`; Vite direct to 9095 | Same BFF header normalization; raw request stream | BFF 503 on transport error; test direct EOS methods and auth. |
| `/api/business/tenants/**` | BFF rewrites to EOS `/api/tenants/**` | Institutional headers; raw stream | Python alias/consumer parity unverified. |
| `/api/employees/**` | BFF -> EOS same prefix; Vite direct to 9095 | Institutional headers; raw stream | BFF 503; verify method and tenant-scope parity. |
| `/api/kernel/**` | BFF -> EOS same prefix; Vite direct to 9095 | Institutional headers; raw stream | Launcher waits on both EOS `/kernel` and BFF `/api/kernel`; readiness contract must change before removal. |
| `/api/plans/**`, `/api/subscriptions/**` | BFF -> EOS same prefix | Institutional headers; raw stream | Exact Python method/path parity unverified. |
| `/api/billing/**` | BFF rewrites to EOS `/billing/**`; Vite directly sends selected paths to EOS, others to Node | Institutional headers; raw stream; billing timeout 60s | Partial parity only. Identify Node-owned partial-payment/PDF/audit consumers first. |
| `/billing/**` | BFF -> EOS `/billing/**` unchanged | Institutional headers; raw stream; 60s timeout | External consumers not yet mapped. |
| `/auth/**` | BFF rewrites to EOS `/api/auth/**`; Vite sends this prefix to port 4000 | Institutional headers; raw stream | Vite error 502; confirm cookies/redirects and external callers. |
| POST `/api/wilsy-ai/legal-services` collection root only | Selective BFF -> EOS same path | Institutional headers; raw POST stream | Other methods/shapes fall through; verify exact Python contract. |
| POST `/api/wilsy-ai/legal-next-actions`; GET `/api/wilsy-ai/legal-next-actions/:id` | Selective BFF -> EOS same path | Institutional headers; raw stream | Other shapes fall through; verify exact Python contract. |
| GET `/api/legal-acceptance/status`; GET `/api/legal-acceptance/documents/:id`; POST `/api/legal-acceptance/accept` | Selective BFF -> EOS same path; Vite direct to 9095 | Institutional headers; raw stream | Invalid shapes fall through; focus-test direct EOS before retirement. |
| POST `/api/generate/pdf` | Node invokes `generateSovereignArtifactPdf` locally | JSON body limit 10 MB; upload/body middleware runs after proxies | No Python equivalent proven. Hard blocker for deleting the controller/runtime. |
| Other `/api/**` | Node returns 404 `BFF_ROUTE_NOT_PROXIED`; Vite generic `/api` routes here | No upstream request | Client-visible 404 contract exists; inventory callers before replacing. |

## Cross-cutting transport contract

- EOS target: `KENNEL_URL`, then `KENNEL_EOS_URL`, then `http://127.0.0.1:9095`.
- Default timeout 30 seconds; billing timeout 60 seconds.
- Query strings are preserved during rewrites. Express mount-prefix stripping is reconstructed with the configured EOS prefix.
- Forwarded headers: Authorization; tenant chosen from `x-tenant-id`, `x-wilsy-tenant`, `x-tenant`, `x-wilsy-tenant-id` or `req.tenantId` and copied to three tenant header spellings; idempotency chosen from three aliases and copied to three spellings; `x-trace-id`; `x-request-id`.
- Proxy runs before body parsers, preserving raw request bytes.
- BFF transport failures return 503 JSON with generic wording; Vite proxy failures return 502 JSON. Vite rules do not visibly apply the BFF's explicit header normalization.
- BFF applies Helmet and CORS (`origin: true`, credentials enabled). Equivalent security-header and CORS behavior must be tested after migration.
- Selective legal paths only proxy allowed method/path shapes; other shapes fall through to the BFF 404.
- Optional Mongoose connection is read by `/health`; do not remove until consumers and deployment configuration are checked.

## Consumers and required migration

| Consumer | Evidence | Required action |
|---|---|---|
| Root `npm run dev` | Runs `node scripts/start-dev-stack.mjs` | Replace with Python-owned process orchestration; preserve readiness, failure timeout, cleanup and port conflict handling. |
| Startup launcher | Starts EOS, Node BFF and Vite; waits on EOS and BFF health | Remove BFF process only after a single canonical EOS readiness contract is tested. |
| `client/vite.config.js` | `/auth` and generic `/api` route to port 4000; selected prefixes go direct to EOS | Map every browser caller; migrate missing routes; test auth, cookies, redirects and errors. |
| `.github/workflows/ci.yml` | Installs server dependencies; npm audit; lints BFF/PDF files; secret guard references Node files | Replace Node-runtime gates with Python EOS/PDF security and route tests; retain browser build tooling where needed. |
| Root/server Docker and Compose | Deployment scripts reference server Docker and compose files | Prove active production targets; switch to EOS image and smoke-test deployment configuration before deletion. |
| Package manifests / PM2 | Root scripts include server start and PM2; server manifest names `server.js` as main | Remove backend dependencies only after all runtime, test, deployment and operations references are classified. |
| Production-surface policy | Explicitly marks `server/server.js` RETAIN | Change policy only after replacement and certification. |

## Exit gates

- [ ] Method/path parity for every required BFF route.
- [ ] Adversarial tests for tenant header aliases, Authorization, idempotency, trace/request IDs, raw bodies, query strings and rejected method/path shapes.
- [ ] Test timeout, 503/502, upstream response passthrough, CORS, Helmet, cookies and redirects.
- [ ] Python PDF parity and authorization tests, or formally retained approved artifact service.
- [ ] Launcher tests for readiness, timeout, shutdown, process cleanup and port conflicts.
- [ ] Browser auth and Legal Operations certification with no port-4000 dependency.
- [ ] Python security/dependency checks, browser build/tests, Legal Operations regressions and EOS image smoke test.
- [ ] No required runtime references to Node BFF, port 4000, PM2 server deployment or server-only packages.
- [ ] Governance policy updated using the passing evidence.

**Decision:** This static inventory does not prove route parity and does not authorize deleting `server/server.js`.