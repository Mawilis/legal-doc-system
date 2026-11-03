# WILSY OS — Day 1 Runtime, Dependency and Route Inventory

Date: 2026-11-03
Repository: Mawilis/legal-doc-system
Inventory baseline: eos/atomic-owner-genesis-integration at e482195fd70eda3fcceafe0ef6c0bdca2c0ad931
Working branch: eos/tenant-discovery-iam-dashboard-roadmap
Status: Runtime/route inventory recorded; EOS workspace contract and session-bound tenant transport implemented; exhaustive recursive legacy retirement certification remains in progress.

## 1. Runtime boundary

| Layer | Current artifact | Target disposition |
|---|---|---|
| Business/API authority | Python EOS / FastAPI, tools/eos/api/server.py | Retain; sole application API and business-authority runtime |
| Browser application | React, JSX, client/src | Retain; presentation and transport only |
| Frontend development/build | Vite, client/vite.config.js, client/package.json | Retain; not a business runtime |
| Legacy API runtime | Express, server/server.js and server/app.js | Retire after every active route, job, import, data dependency and test has a certified EOS replacement or documented removal |
| Development orchestration | scripts/start-dev-stack.sh | EOS + Vite launcher; no additional application API process |
| Root package tooling | package.json | Remove legacy server scripts/dependencies only after callers are migrated; preserve frontend build/test/security tooling |

## 2. Authentication and workspace route map

| User journey stage | Browser caller | EOS route / owner | Authority source | Required behavior |
|---|---|---|---|---|
| Tenant discovery | TenantDiscovery.jsx → AuthContext.discoverTenant | POST /api/auth/discover | TenantRegistry canonical ACTIVE tenant resolver | Exact bounded tenant projection; discovery grants no membership |
| Credential login | AuthContext.login | POST /api/auth/login | AuthRegistry credentials | Authenticate principal; do not trust tenant header or browser role |
| MFA setup | AuthContext.verifyOTP | POST /api/auth/validate-mfa-setup | AuthRegistry + factor-currentness evidence | Verify factor, durably record and issue session |
| MFA verification | AuthContext.verifyOTP | POST /api/auth/verify-otp (and alias /verify-3fa) | AuthRegistry + factor-currentness evidence | Verify factor and issue session |
| Authenticated workspace resolution | AuthContext.persistSession / restore / refreshWorkspace | GET /api/auth/workspace-bootstrap | Principal authority, TenantMembershipRepository, TenantBusinessRoleRepository, TenantRegistry and canonical permission compositor | Return READY only after current principal, active membership, business capacity, tenant and bounded permission projections are revalidated |
| Authenticated branding | AuthContext workspace projection | GET /api/auth/workspace-branding/{asset_kind} | D21B current branding projection and asset delivery | Exact tenant-bound asset; no browser-created branding authority |
| Dashboard selection | SovereignDashboardController.jsx | GET /api/auth/workspace-bootstrap now returns workspaceId and workspaceContractVersion from EOS | EOS business-role-to-workspace projection | Client maps only the validated server-issued workspaceId to a view; browser role mapping has been removed in this branch |
| Protected operations | Client API callers | Corresponding mounted /api EOS routers | Route-specific EOS IAM and resource scope | Independently authorize each request; dashboard manifest is not an access token |

### Current auth limitations

- AuthRequest currently accepts email/password only in the login handler. The handler looks up a user by email and the current durable user record supplies a single tenantId.
- Workspace bootstrap takes tenant scope from the authenticated SovereignIdentity and revalidates membership against that scope.
- Discovery currently does not select a membership during credential authentication.
- Therefore removing a frontend constant does **not** yet implement a global-principal / many-memberships model. A tenant-scoped session issuance and membership-selection design is still required.
- Existing TenantMembershipRepository and TenantBusinessRoleRepository are useful foundations. The current workspace projection resolves one business role and can fail when multiple active capacities are ambiguous; explicit capacity selection is still required.
- The existing TenantProvider switchTenant helper must not be mistaken for a server-authorized membership switch. Authenticated cross-tenant switching must obtain a newly authorized EOS session/workspace contract.

## 3. First tenant-context correction

Committed on this branch:

- client/src/services/api.js no longer contains CANONICAL_WILSY_TENANT_ID.
- Request tenant scope is held in memory only after AuthContext accepts a READY EOS workspace-bootstrap response; discovery storage is not promoted to authenticated request scope.
- Missing authenticated session context yields no tenant header; there is no WILSY, GLOBAL_ROOT, discovery-storage or other fallback.
- A stale default header is removed when discovery cannot supply a valid tenant.
- client/src/__tests__/services/api.test.js now covers the in-memory EOS-verified tenant context, proves discovery storage cannot establish it, and verifies preservation of an MFA candidate bearer without substituting a tenant.
- client/src/components/ErrorBoundary.jsx sends no tenant selector for optional error telemetry; EOS derives authenticated scope from the bearer where applicable.

This changes transport selection only. EOS continues to prove membership and authorization. It does not create or assign membership, issue a tenant-scoped session, or enable cross-tenant switching.

## 4. Client route and session dependencies

| Artifact | Responsibility | Day 1 finding / disposition |
|---|---|---|
| client/src/components/sovereign/TenantDiscovery.jsx | Tenant discovery presentation | Retain; calls AuthContext discovery |
| client/src/contexts/authContext.jsx | Candidate token, discovery projection, MFA and server bootstrap promotion | Retain and evolve; must support selected membership/session context from EOS |
| client/src/contexts/tenantContext.jsx | Browser projection of authenticated tenant | Retain as projection only; prevent local storage and directory calls from authorizing tenant switches |
| client/src/services/api.js | Shared Axios transport | Retain; no hardcoded tenant; session-bound in-memory scope only after EOS revalidation |
| client/src/components/sovereign/SovereignDashboardController.jsx | Dashboard component composition | Consumes the validated EOS workspace identifier; client role-to-dashboard map removed |
| client/src/components/ErrorBoundary.jsx | Error boundary and optional telemetry | Retain; synthetic GLOBAL_ROOT tenant fallback removed |
| client/vite.config.js | Development routing | All application API routes now target EOS directly; remaining endpoint gaps must be reconciled against EOS route mounts |
| client/src/__tests__/services/api.test.js | Shared transport contract tests | Updated for dynamic discovered tenant and fail-closed no-discovery behavior |

## 5. EOS authority dependencies

| Concern | Canonical files / components | Required proof |
|---|---|---|
| Principal identity and session | tools/eos/auth/identity.py, authentication.py, tools/eos/saas/auth/auth_registry.py | Global principal identity separated from tenant membership; access token bound to selected membership/session revision |
| Tenant discovery | tools/eos/api/auth_router.py, tools/eos/saas/domain/auth.py DiscoverRequest, tools/eos/saas/tenancy/tenant_registry.py | Alias/domain exact resolution, ACTIVE tenant, bounded response and anti-enumeration behavior |
| Membership | tools/eos/auth/tenant_access.py, tenant_membership.py, tenant_membership_repository.py | Exact ACTIVE membership for principal and discovered tenant |
| Business capacity | tools/eos/auth/tenant_business_role_authority.py, tenant_authority_policy.py | Explicit active capacity selection; no silent most-permissive role or union |
| Authorization | tools/eos/auth/tenant_authorization.py, tenant_authorization_http.py, role and permission registries | Exact operation/permission and active granting-role decisions on every protected route |
| Workspace bootstrap | tools/eos/auth/workspace_bootstrap_projection.py and GET /api/auth/workspace-bootstrap | Versioned workspaceId/contract version and membership/business-role revisions now exist; membership_id, active capacity selection, server-issued manifest and multi-membership session context remain outstanding |
| API composition | tools/eos/api/server.py and tools/eos/api/*_router.py | Each application route mounted exactly once in EOS and covered by route-level tests |

## 6. Legacy server route inventory — migration register

The roadmap checkpoint identifies these legacy runtime surfaces. This is the migration register; each path must be reconciled against the current server route table and caller graph before deletion.

| Legacy surface | Known behavior | EOS migration gate |
|---|---|---|
| server/server.js | Express runtime and route forwarding | Inventory every mounted route, middleware, startup hook and external listener |
| server/app.js | Older Express application with local CRM, billing, telemetry, QR and other routes | Determine whether active, imported, tested or data-bearing; do not delete by assumption |
| /api/auth and /auth | Legacy auth forwarding / aliases | All required auth routes directly mounted in EOS; no alias depends on Express |
| /api/tenants, /api/employees | Tenant and employee forwarding | Confirm exact EOS route contracts and client callers |
| /api/kernel | Kernel health/contract forwarding | Direct EOS route and health test |
| /api/plans, /api/subscriptions, /api/billing/* | Commercial and billing forwarding | Verify every read/write lifecycle endpoint and Kennel authority boundary |
| /api/legal-acceptance, /api/legal-operations/* | Legal acceptance and Legal Operations forwarding | Verify direct EOS route, IAM, payload and response parity |
| /api/owner-workspace and advisory paths | Owner commercial workspace and advisory forwarding | Confirm correct executive product destination; CRM is not the Owner workspace |
| /api/generate/pdf | Local PDF endpoint in server/server.js | Migrate to EOS or remove only after binary response, integrity, authorization and download tests |
| WebSocket / Socket.IO and scheduled jobs | Server runtime dependencies to be discovered | Identify each active client, message contract, worker, scheduler and persistence effect before retirement |

## 7. Package, process and deployment dependencies

- Root package.json no longer exposes server:dev, server:start, pm2:deploy, pm2:stop or pm2:status scripts. The default dev command now invokes scripts/start-dev-stack.sh.
- Root package.json includes frontend/test dependencies and scripts as well as legacy server dependencies. Do not remove all root Node dependencies wholesale.
- client/package.json owns Vite, React, browser build and Vitest dependencies; preserve.
- scripts/start-dev-stack.mjs has been deleted. scripts/start-dev-stack.sh now starts/reuses Python EOS and starts/reuses the Vite presentation client only; bash syntax check passed.
- client/vite.config.js routes the catch-all /api and legacy /auth compatibility path directly to EOS; there are no port-4000 proxy targets in the current PR branch. Endpoint parity is not yet proven for all frontend callers.
- Audit .github/workflows, Dockerfiles, deployment manifests, Procfiles, PM2 config, shell scripts and docs for server startup, port 4000, Express and server/.env references.
- Never print or commit secrets while comparing environment-variable names and configuration ownership.

## 8. Day 1 exit status

| Deliverable | Status |
|---|---|
| Confirm integration baseline and branch | COMPLETE |
| Identify hardcoded tenant transport source | COMPLETE |
| Remove hardcoded tenant from shared API client | COMMITTED |
| Add dynamic-discovery and no-fallback transport tests | COMMITTED; execution pending in the local checkout/CI |
| Remove synthetic GLOBAL_ROOT telemetry tenant fallback | COMMITTED |
| Identify principal/membership limitation in login | CONFIRMED; global-principal implementation outstanding |
| Bind login and MFA requests to exact EOS-discovered tenant | IMPLEMENTED; tests added, execution pending |
| Identify role/capacity ambiguity | CONFIRMED; explicit multi-capacity selection outstanding |
| Establish versioned EOS workspaceId and client contract validation | COMMITTED; tests added, execution pending |
| Exhaustive recursive server route/import/test/workflow/data inventory | IN PROGRESS |
| Retire legacy server runtime | NOT STARTED; blocked on migration proof |


## 10. Expanded endpoint and legacy dependency census

The committed `runtime_endpoints.txt` snapshot contains 384 source-reference lines and 196 distinct `/api/*` path strings (including dynamic path fragments and query variants). It is a client-callsite inventory, not proof that each route is mounted or implemented in EOS. `runtime_fetch_all.txt` contains 92 fetch callsite lines. Direct-origin callsites were also found that bypass Vite, including `http://127.0.0.1:8000/api/v1` and several `http://localhost:5050/api` routes. These must be removed or redirected through an EOS-owned API contract; do not silently point them at unrelated routes.

### Distinct client endpoint tokens

```text
/api/account/compliance-command
/api/account/compliance-command?tenantId=
/api/account/identity-posture?tenantId=
/api/agriculture/fields
/api/agriculture/metrics
/api/analytics/revenue?period=
/api/audit/verify-qr/:traceId
/api/auth/discover
/api/auth/login
/api/auth/logout
/api/auth/me
/api/auth/refresh
/api/auth/verify-3fa
/api/auth/webauthn-challenge
/api/axiosConfig.js
/api/axiosConfig.js:
/api/business/contracts?tenantId=
/api/business/deals?tenantId=
/api/business/employees?tenantId=
/api/consulting/metrics
/api/consulting/projects
/api/crm
/api/crm/
/api/crm/activities
/api/crm/command
/api/crm/command-center
/api/crm/command/address/suggest
/api/crm/command/contacts
/api/crm/command/contacts.
/api/crm/command/leads
/api/crm/command/leads/
/api/crm/command/leads/:id
/api/crm/command/leads/:id.
/api/crm/command/meetings
/api/crm/command/meetings/
/api/crm/command/meetings/:id
/api/crm/command/meetings/action
/api/crm/command/meetings/import-preview
/api/crm/command/protected
/api/crm/command/search/regulator-evidence/terminal-api-surface-registry/latest
/api/crm/command/search/regulator-evidence/terminal-cockpit-contract/latest
/api/crm/command/search/regulator-evidence/terminal-command-index/latest
/api/crm/command/search/regulator-evidence/terminal-launch-packet/latest
/api/crm/command/search/regulator-evidence/terminal-release-brief/latest
/api/crm/command/search/regulator-evidence/terminal-release-passport/latest
/api/crm/command/search/regulator-evidence/terminal-release-passport/verify/latest
/api/crm/command/search/regulator-evidence/terminal-release-readiness/latest
/api/crm/command/setup/control-surface/resolve
/api/crm/command/setup/reviews
/api/crm/command/setup/reviews/
/api/crm/command/setup/reviews/approve
/api/crm/command/setup/reviews/clear
/api/crm/command/setup/reviews/evidence
/api/crm/command/setup/reviews/list
/api/crm/command/setup/reviews/open
/api/crm/command/setup/reviews/release
/api/crm/control-state/leads/filters
/api/crm/customers
/api/crm/export
/api/crm/import
/api/crm/import/preview
/api/crm/intelligence/
/api/crm/intelligence/accounts
/api/crm/intelligence/deals
/api/crm/intelligence/leads
/api/crm/leads/views
/api/crm/leads/views/
/api/crm/leads/views/proof-ledger/access/resolve
/api/crm/live/
/api/crm/live/accounts
/api/crm/live/connectors
/api/crm/live/contacts
/api/crm/live/deals
/api/crm/live/evidence
/api/crm/live/leads
/api/crm/live/meetings
/api/crm/live/source-posture
/api/crm/live/tasks
/api/crm/source-registry/evidence
/api/deals
/api/deals/
/api/deals?limit=100
/api/deals?limit=20
/api/education/metrics
/api/education/students
/api/email/send
/api/energy/generation
/api/energy/metrics
/api/entertainment/metrics
/api/entertainment/productions
/api/finance/metrics?range=
/api/finance/portfolio
/api/forensics/merkle-auditor/anchors?
/api/forensics/merkle-auditor/receipts/
/api/forensics/merkle-auditor/receipts?
/api/forensics/merkle-auditor/run
/api/forensics/merkle-auditor/seal-safe-window
/api/forensics/merkle-auditor/status
/api/forensics/verify-chain
/api/forensics/verify-chain?
/api/generate/pdf
/api/generate/pdf.
/api/kernel
/api/kernel/status
/api/knowledge-base/vault
/api/legal/deputies
/api/legal/documents
/api/legal/metrics?district=
/api/logistics/agri
/api/logistics/alerts
/api/logistics/borders
/api/logistics/metrics
/api/logistics/parts
/api/logistics/ports
/api/logistics/routes
/api/logistics/shipments
/api/logistics/vehicles
/api/production/alerts
/api/production/downtime/events
/api/production/downtime/reasons
/api/production/lines
/api/production/live
/api/production/metrics
/api/production/oee/components
/api/production/quality/defects
/api/production/shift/schedule
/api/project/alerts
/api/project/list
/api/project/metrics
/api/project/milestones
/api/project/resources
/api/project/risks
/api/property/alerts
/api/property/financials
/api/property/list
/api/property/maintenance
/api/property/market-trends
/api/property/metrics
/api/property/tenants
/api/public/alerts
/api/public/analytics
/api/public/budget
/api/public/metrics
/api/public/projects
/api/public/requests
/api/public/services
/api/retail/alerts
/api/retail/inventory
/api/retail/products/top
/api/retail/sales
/api/source-registry
/api/source-registry/health
/api/source-registry/health?wilsyAiContext=RESOLVE
/api/sports/alerts
/api/sports/injuries
/api/sports/matches
/api/sports/metrics
/api/sports/players
/api/sports/standings
/api/statements/
/api/superadmin
/api/superadmin.js
/api/superadmin/metrics
/api/tech/alerts
/api/tech/metrics
/api/tech/services
/api/telemetry
/api/telemetry/boardroom
/api/telemetry/dashboard
/api/telemetry/error
/api/telemetry/event
/api/tenantApi.js
/api/tenantApi.js:
/api/tenants/
/api/tenants/activate/
/api/tenants/create
/api/tenants/suspend
/api/tenants/suspend/
/api/users/anchor-biometric
/api/users/forensic/
/api/users/revoke
/api/users?tenant=
/api/v1
/api/v1/crm/dashboard
/api/v1/crm/dashboard.
/api/v1/crm/execution
/api/v1/dashboard
/api/v1/engines
/api/v1/events
/api/v1/execution
/api/v1/execution.
/api/v1/intelligence/repository-census
/api/v1/onboarding/initialize
/api/v1/runtime
/api/v2/sovereign/demo/ignite
/api/wilsy/ai/operator/resolve
```

### Legacy Express application route mounts

`server/server.js` is a selective transport layer. It has health routes (`/ping`, `/api/ping`, `/api/billing/ping`, `/health`, `/`), forwarding mounts for auth, tenants, business/tenants, employees, kernel, plans, subscriptions, billing, legacy auth, owner-workspace, Legal acceptance, Legal AI/advisory, and a local `POST /api/generate/pdf` implementation. It ends with a 404 for every unproxied `/api` route. Its PDF handler and renderer are currently classified RETAIN by `tools/eos/governance/production_surface_policy.json`.

`server/app.js` is a separate 614-line Express application with 17 route declarations/mounts:

```text
PATCH /api/crm/command/leads/:id
POST /api/generate/pdf
GET /api/status
POST /api/telemetry/pulse
GET /api/ping
GET /ping
USE /api/
GET /api/v1/sovereign-health
USE /api/crm/live
USE /api/crm/command
USE /api/crm/intelligence
USE /api/wilsy/ai
USE /api/billing
USE /api/qr
USE /api
USE /api/forensics
USE /monitoring
```

It imports CRM command routes, a local PDF renderer, tenant context middleware, production hardening middleware, metrics, route bundles for CRM live/intelligence, billing, QR, AI, forensics and sovereign operations, audit/telemetry helpers, Redis health and a verification-sync scheduler. It also contains a local non-production PATCH `/api/crm/command/leads/:id` persistence route. This is not a safe blind-delete candidate. Every imported route/service/job and persistence path must be inventoried and either migrated into EOS or formally retired.

`orchestrator.js` is another legacy Node process manager: it forks `server/server.js` and `server/jobs/workerEntry.js`, and restarts failed children. Its references, worker schedule and data effects are a separate retirement gate. Search also found historical gate scripts and release manifests that explicitly read/assert `server/app.js` or `server/server.js`; those tests/evidence must be updated only when their tested behavior is migrated, not deleted to hide failures.

### Runtime and package changes already made on this branch

- Added `scripts/start-dev-stack.sh`, which starts/reuses only Python EOS and Vite. It verifies the working directory of listeners on ports 9095 and 5173 and refuses to reuse a process from another checkout.
- Changed root `package.json` default `dev` to the shell launcher.
- Removed root Express lifecycle scripts (`server:dev`, `server:start`, `pm2:deploy`, `pm2:stop`, `pm2:status`).
- Deleted `scripts/start-dev-stack.mjs`.
- Vite's `/api` catch-all and legacy `/auth` compatibility route now target Python EOS directly.
- This removes the legacy Express process from the default development startup path; it does not yet delete the server source tree or certify every former route. The launcher requires macOS/Linux `lsof` to verify process ownership; validate this on the target developer OS.

### Production retention policy conflict

`tools/eos/governance/production_surface_policy.json` explicitly classifies `server/server.js`, the PDF controller/renderer/QR generator and `server/package.json` / `server/package-lock.json` as RETAIN. `tests/unit/test_owner_commercial_workspace_server_mount.py` also reads `server/server.js` and asserts its proxy mount. Other historical CRM gate scripts read `server/app.js`. These governance/test dependencies must be reconciled through a deliberate policy and test migration before deleting those files.


## 11. Package dependency census

Package manifests at this checkpoint:

| Manifest | Runtime dependencies | Development dependencies | Disposition |
|---|---:|---:|---|
| Root `package.json` | 10 | 25 | Mixed tooling and legacy dependencies; classify imports before removal |
| `server/package.json` | 114 | 34 | Legacy Express application, worker and server test dependencies; retire after all active behavior migrates |
| `client/package.json` | 27 | 23 | React/Vite presentation and browser-test dependencies; preserve |

### Root runtime dependencies

```text
@aws-sdk/client-s3, @fidm/x509, bcrypt, dotenv, ioredis, node-cache, prom-client, qrcode, speakeasy, uuid
```

### Root development/test dependencies

```text
@babel/core, @babel/preset-env, @babel/preset-react, @babel/register, @playwright/test, @testing-library/jest-dom, @testing-library/react, @testing-library/react-hooks, @vitest/ui, chai, husky, jsdom, jsdom-global, lint-staged, mocha, mongodb-memory-server, mongoose, nock, nodemon, pm2, pyright, react, react-dom, sinon, vitest
```

### Legacy server runtime dependencies (114)

```text
@babel/core, @babel/preset-env, @babel/preset-react, @huggingface/transformers, @mongodb-js/zstd, @noble/curves, @noble/post-quantum, @pagerduty/pdjs, @react-pdf/renderer, @tensorflow/tfjs, @tensorflow/tfjs-backend-cpu, @tensorflow/tfjs-backend-webgl, agenda, asn1js, async-mutex, axios, axios-retry, bcrypt, bcryptjs, bn.js, bullmq, canonical-json, chalk, compression, compromise, compromise-dates, compromise-ngrams, compromise-numbers, cors, crypto, csv-parser, docxtemplater, dotenv, exceljs, express, express-async-handler, express-fileupload, express-mongo-sanitize, express-rate-limit, express-validator, express-ws, fast-json-patch, fast-xml-parser, gpu.js, handlebars, helmet, hpp, httpxy, ical-generator, ioredis, ip-address, joi, js-sha3, js-yaml, jsdom, json-stable-stringify, json2csv, jsonwebtoken, keccak256, lodash, lru-cache, luxon, mammoth, merkle-tree-stream, merkletreejs, moment, moment-timezone, mongoose-sequence, morgan, msgpack-lite, multer, node-cache, node-cron, node-rsa, nodemailer, opossum, otplib, pdf-lib, pdf-parse, pdfkit, pg, pg-hstore, pino, pino-http, pino-pretty, pizzip, pkijs, prom-client, qrcode, rate-limit-redis, rate-limiter-flexible, redis, sequelize, sha3, snappy, socket.io, speakeasy, sqlite3, stopword, tar, twilio, ua-parser-js, ulid, uuid, validator, winston, winston-daily-rotate-file, winston-mongodb, ws, xml2js, xss, xss-clean, zod, zxcvbn
```

### Legacy server development/test dependencies (34)

```text
@babel/core, @babel/preset-env, @babel/register, @tensorflow/tfjs-node, @types/chai, @types/ioredis-mock, @types/jest, @types/mocha, ajv, ajv-formats, brain.js, chai, chai-as-promised, eslint, eslint-config-airbnb-base, eslint-config-prettier, eslint-plugin-import, eslint-plugin-prettier, geoip-lite, glob, ioredis-mock, jest, mocha, mocha-junit-reporter, mongodb-memory-server, mongoose, natural, nodemon, nyc, prettier, redis-mock, rimraf, sinon, supertest
```

### Client runtime dependencies (27)

```text
axios, canvas, chart.js, cmdk, crypto-js, docx, history, html2canvas, js-sha3, jspdf, libphonenumber-js, lodash, lucide-react, pdfkit, qrcode, react, react-chartjs-2, react-dom, react-joyride, react-router-dom, recharts, socket.io-client, styled-components, topojson-client, uuid, world-atlas, zustand
```

### Client development/test dependencies (23)

```text
@babel/core, @babel/preset-env, @babel/preset-react, @babel/register, @tailwindcss/postcss, @testing-library/jest-dom, @testing-library/react, @testing-library/user-event, @types/react, @types/react-dom, @vitejs/plugin-react, @vitest/ui, autoprefixer, c8, chai, jsdom, mocha, postcss, prop-types, sinon, tailwindcss, vite, vitest
```

Manifest presence is not proof of runtime use. The next dependency pass must map every direct import/require/dynamic import, worker, test, script and workflow to its owning package. In particular, keep React, Vite, JSX, Vitest, Playwright and required build tooling even though they run on Node.js; they are not the legacy application server.

## 11A. Discovery-to-login tenant selector closure

The Day 1 transport correction is now carried into the authentication boundary:

- `SovereignLogin` passes the exact tenant ID from the EOS discovery projection to AuthContext.
- AuthContext sends that value as `tenant_id` for credential login and carries it through MFA setup/verification.
- EOS rejects missing selectors and tenant mismatch before MFA enrollment, challenge completion or session issuance.
- Removed the unused `client/src/bootstrap/EnterpriseBootstrap.jsx` component after repository search found no imports/callers; it fabricated `tenant_wilsy_001` and issued a direct login outside the canonical MFA/session flow.
- Removed the old `wilsy` hostname/storage fallback from `client/src/services/superadmin/auth.service.js`; its selector now comes only from the EOS discovery projection and is submitted as `tenant_id`. Removed the legacy ObjectId tenant fallback from `client/src/services/sovereignAuth.js`.
- Removed the synthetic `GLOBAL_ROOT` tenant selector from App route telemetry; unresolved telemetry now uses the non-tenant sentinel `unresolved`.
- Blocked client-only cross-tenant switching in `TenantProvider`. A different tenant now requires a fresh EOS membership-selection/session decision; same-tenant projection remains idempotent.
- Workspace bootstrap remains the final promotion gate for ACTIVE membership, business capacity, tenant and workspace authority.

This is not yet multi-membership authentication. AuthRegistry still stores one `tenantId` on the current user credential record; global-principal identity and many tenant memberships, selection of one exact ACTIVE membership, and membership-bound token/session issuance are Day 2 work. Do not claim cross-tenant identity support from this selector check alone.

### Additional tenant-default cleanup in the client

- Added shared `isCanonicalTenantTransportId` validation in `client/src/services/api.js`; it rejects reserved pseudo-tenant values before establishing the in-memory authenticated tenant context.
- Removed pseudo-tenant defaults from Executive AI/context hooks, Compliance/Revenue/Billing/Identity metrics hooks, and the Kennel billing client. Tenant-scoped requests now wait for an explicit canonical tenant or fail closed.
- Updated RevenueHUD, InvoiceSentinel, GlobalSearch, BoardroomHUD, SecurityManager and SovereignOrchestrator to use the authenticated tenant projection rather than a `GLOBAL_ROOT` fallback.
- The Boardroom and Invoice Sentinel surfaces compare the projected tenant against the authenticated user tenant before sending requests.

**Not a repo-wide zero-default certification:** the wider client/server scan still finds legacy tenant placeholders in older tax/dunning/intelligence surfaces and throughout the inactive server-side runtime. Those files remain in the Day 1 dependency closure and must be migrated or retired before declaring that no tenant default exists anywhere. The 2,029-file legacy server tree has not been deleted.


## 12. Safety and release boundaries

- No membership, role, permission, subscription, entitlement or user record was created or modified by the tenant-header correction.
- No production data migration has been run.
- No legacy server files have been deleted.
- A missing discovery projection must never be replaced with a tenant default.
- Tenant discovery is not proof of membership; a user must be admitted by EOS against the selected tenant.
- A workspace contract controls presentation only; each operation remains independently authorized.
- Keep Tenant Owner / proposed Tenant Partner executive authority separate from professional Legal Partner practice authority.
- Do not claim multi-tenant principal support until the identity, login, MFA, session, membership and revocation paths all support it and tests prove isolation.

**END OF DAY 1 INVENTORY**


## 11. Global-principal membership-selection implementation checkpoint

The follow-on implementation is recorded in `global-principal-membership-selection-contract.md`.

Committed code on this branch:

- `TenantMembershipRepository.list_for_principal` adds deterministic cursor pagination scoped by one exact principal, with a maximum page size of 100 and caller-owned Mongo session propagation.
- `membership_selection_projection.py` composes the ACTIVE global PrincipalAuthority, principal-scoped membership page, current canonical ACTIVE tenant, and every ACTIVE tenant business capacity. Each capacity maps to an EOS workspace identifier but conveys no permissions or authorization grant.
- Unit tests cover principal status, active/inactive membership filtering, multiple capacities, workspace projection, tenant mismatch, cursor preservation, page bounds and caller-session propagation.

**Integration boundary:** this is deliberately a read-only projection primitive, not yet a public login endpoint. The global credential authority does not yet exist. The existing AuthRegistry stores password hash, MFA state and tenantId together in `users`; login looks up one row by email; credential-revision validation, MFA, ACCESS issuance and refresh-token persistence remain tenant-bound. Wiring the new projection into login before migrating those credential/session dependencies would preserve the same single-tenant assumption behind a new endpoint and is therefore prohibited.

**Additional credential foundation now committed:**

- `PrincipalCredential` defines a tenant-neutral immutable record containing global principal ID, normalized email, bcrypt verifier and credential revision only.
- `PrincipalCredentialRepository` defines unique principal/email indexes, exact lookups, duplicate rejection and password-verifier compare-and-swap revision updates.
- Unit tests cover schema separation, uniqueness, normalized email lookup, CAS, malformed records and caller-session propagation.
- The repository is not wired into login/startup and has not created a production collection. This is intentional: existing MFA, recovery, refresh, session and access-token revision paths still depend on the old tenant-bound `users` document.

**Next engineering gate:** implement the controlled legacy credential migration and move MFA, recovery, credential revision, refresh, session and token verification together to the global principal credential. Then bind selected membership and capacity revisions to the session, expose the membership choices endpoint and complete the HTTP/browser journey. Ambiguous duplicate/conflicting legacy identities must be quarantined, never silently merged or used to create membership.
