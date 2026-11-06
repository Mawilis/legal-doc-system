# WILSY OS — Day 1 Runtime, Route and Dependency Inventory

Inventory date: 3 November 2026
Repository: `Mawilis/legal-doc-system`
Source checkpoint: `eos/atomic-owner-genesis-integration` at `e482195fd70eda3fcceafe0ef6c0bdca2c0ad931`
Inventory branch: `eos/tenant-discovery-iam-dashboard-roadmap`
Purpose: establish the EOS-only application runtime, map active API routing and classify the legacy server-side runtime before retirement.

## 1. Executive finding

WILSY OS already has a substantial Python EOS API composition root and an established authenticated workspace-bootstrap projection. The frontend is React/Vite. The current local development launcher additionally starts a separate Express process, and Vite had routed selected API prefixes to EOS while forwarding its remaining API paths to that separate process.

The Express gateway is not the identity or authorization authority, but it is still an active local runtime dependency in the existing `npm run dev` orchestration. The older `server/app.js` is a separate, larger Express application with local route implementations and many imports. It must be assessed separately from the active `server/server.js` entrypoint.

**Day 1 result:** source composition, API routing, workspace/auth call chain, runtime scripts and repository-scale inventory are mapped sufficiently to begin the first reversible changes. This is not yet a file-by-file certification of all 2,029 files under `server/`; the dependency closure for that directory remains a retirement gate, not a presumed deletion.

## 2. Repository census

A recursive Git tree snapshot returned 7,062 entries and was not truncated. Counts below include tracked files and directories within the named path; they are repository census figures, not counts of executable source files.

| Area | Entries |
|---|---:|
| Entire repository tree | 7,062 |
| `server/` legacy application tree | 2,029 |
| `scripts/` | 187 |
| `tools/eos/auth/` | 109 |
| `tools/eos/api/` | 41 |
| `client/src/contexts/` | 7 |
| `client/src/services/` | 65 |
| `client/src/components/sovereign/` | 86 |
| `tests/unit/` | 829 |
| `tests/eos/` | 19 |
| `tests/e2e/` | 9 |
| `.github/workflows/` | 60 |

The `server/` tree contains two application entrypoints, route/controller/service/model/middleware trees, workers, jobs, deployment scripts, tests, security/forensic evidence, reports, certificates and historical artifacts. File extension is not a safe deletion criterion.

## 3. Active local development process graph

### Before this implementation

`npm run dev`
→ `scripts/start-dev-stack.mjs`
→ Python EOS on `127.0.0.1:9095`
→ Express gateway started through `npm run server:start` on `127.0.0.1:4000`
→ React/Vite client on `127.0.0.1:5173`

The launcher health-checks EOS and the Express gateway before exposing/reusing Vite. Root `package.json` also defines `server:dev`, `server:start`, `pm2:deploy`, `pm2:stop` and `pm2:status`.

### Current target

`React/Vite client` → `Python EOS API`

Vite remains a frontend development/build tool. Python EOS is the sole application API and business-authority runtime. This does not mean deleting React, JSX, Vite or the Node runtime needed to build/test the frontend.

## 4. Server-side entrypoint classification

### 4.1 `server/server.js` — active development gateway

Observed source characteristics:
- 534 lines.
- Imports Express, CORS, Helmet, express-fileupload, Mongoose, `httpxy`, Node HTTP/URL/path helpers and the PDF controller.
- Selectively forwards API paths to EOS, including auth, tenants, employees, kernel, plans, subscriptions, billing, owner workspace, Legal advisory and Legal acceptance.
- Preserves raw request streams for selected routes before body parsing.
- Implements health/ping routes.
- Implements `POST /api/generate/pdf` locally using `businessArtifactPdfController.js`.
- Returns a local 404 for API prefixes not on its selective forwarding allowlist.
- Starts an HTTP listener and is the entrypoint used by the root development launcher.

Retirement dependencies:
1. Replace/verify every selected API route directly against EOS.
2. Migrate and certify PDF generation, including binary response headers, tenant branding, artifact seal, content integrity and failure semantics.
3. Remove the process from development orchestration.
4. Verify no workflow, deployment, operator runbook or external client expects this listener.

### 4.2 `server/app.js` — separate legacy application

Observed source characteristics:
- 614 lines.
- Imports Express, Helmet, Morgan, Chalk, express-rate-limit, Mongoose, OS, CRM route modules, billing, QR, forensic, sovereign, AI and telemetry services, middleware and a verification scheduler.
- Local routes include a non-production CRM lead persistence recovery route, PDF generation, status/ping/telemetry and sovereign health.
- Mounts CRM live/command/intelligence, AI, billing, QR, generic API, forensics and monitoring routes.
- Owns a separate scheduler lifecycle function.

This file is not the entrypoint used by the inspected root launcher. It is nevertheless not safe to delete merely because the launcher does not invoke it: imports, direct scripts, tests, deployment manifests, worker processes and persisted-data semantics must be checked before retirement.

## 5. API routing inventory

### 5.1 EOS composition

`tools/eos/api/server.py` is the canonical FastAPI composition root. The inspected composition mounts:
- Auth router under `/api`.
- Kernel and core API routers.
- Tenant, employee, plan and subscription routers.
- Billing router at its canonical billing prefix and API-prefixed compatibility mount.
- Owner commercial workspace and Legal Operations routers under `/api`.
- Legal acceptance, Legal Evidence, Legal deadline, Legal practitioner binding, Legal operating model, tenant branding, telemetry and WILSY AI routers.
- HR document and authority bridge routes.

The API surface is therefore not a blank replacement target. Many routes are already EOS-owned and mounted.

### 5.2 Existing gateway route families

The active gateway's selective mounts included:
- `/api/auth` → EOS `/api/auth`
- `/api/tenants` → EOS `/api/tenants`
- `/api/business/tenants` → EOS `/api/tenants`
- `/api/employees` → EOS `/api/employees`
- `/api/kernel` → EOS `/api/kernel`
- `/api/plans` → EOS `/api/plans`
- `/api/subscriptions` → EOS `/api/subscriptions`
- `/api/billing` and `/billing` → EOS billing routes
- `/auth` → EOS `/api/auth`
- `/api/crm/owner-workspace` → selected EOS owner workspace reads/commands
- `/api/wilsy-ai/legal-services` → selected EOS route
- `/api/wilsy-ai/legal-next-actions` → selected EOS route
- `/api/legal-acceptance` → selected EOS route
- `/api/generate/pdf` → local Express PDF implementation
- Other unproxied API requests → local gateway 404

### 5.3 Older application route families

The separate `server/app.js` imports/mounts:
- CRM live, command and intelligence.
- CRM lead persistence recovery.
- WILSY AI.
- Billing and QR.
- Generic API, forensic and sovereign/monitoring surfaces.
- PDF and health/telemetry endpoints.

These routes overlap with or predate EOS-owned domains. Their presence is not proof that each is still called. The route/caller matrix must be established before deletion or migration.

## 6. Authentication-to-dashboard call chain

Current source chain:
1. `TenantDiscovery.jsx` calls `POST /api/auth/discover`.
2. `auth_router.py` resolves one canonical active tenant and returns a bounded tenant projection.
3. `authContext.jsx` calls `POST /api/auth/login` and handles MFA state.
4. After a candidate session is issued, AuthContext calls `GET /api/auth/workspace-bootstrap`.
5. `workspace_bootstrap_projection.py` independently revalidates ACTIVE principal, exact ACTIVE membership, exact ACTIVE tenant business role and canonical tenant.
6. Auth router adds durable profile, Legal presentation permissions and branding projection.
7. AuthContext accepts the READY response and stores a browser presentation projection.
8. `SovereignDashboardController.jsx` previously mapped business-role labels to dashboard components; `OWNER` was explicitly mapped to CRM.

Key limitation before this implementation: the EOS bootstrap response had no canonical workspace identifier. The browser therefore had to infer a presentation shard from a business-role string. This is now being replaced by the versioned EOS workspace contract.

## 7. Tenant context defect and correction

The frontend API client previously derived `X-Tenant-ID` from the discovery result in browser storage. That meant a pre-authentication selector could be carried as if it were the active session tenant. Earlier integration source variants also contained a hardcoded WILSY tenant constant.

New transport contract:
- No hardcoded tenant identifier.
- No localStorage/discovery-based tenant header resolver.
- The API client has a process-memory active tenant transport context.
- AuthContext sets that context only after it accepts a READY EOS workspace-bootstrap response.
- Discovery clears the active transport context; it does not establish authenticated tenant scope.
- Logout, failed restore and absent session clear the context.
- EOS still validates the authenticated principal, canonical tenant membership and each operation. The header is only a transport selector, never authority.

The existing persisted discovery tenant remains a candidate for comparing the user's intended tenant with the server-authenticated workspace; it is not promoted to request authority.

## 8. Canonical workspace contract introduced

EOS workspace-bootstrap now returns:
- `workspace.workspaceId`
- `workspace.workspaceContractVersion`
- existing canonical `tenantId`, `businessRole`, membership revision, role revision, Legal presentation permissions, branding and tenant projection.

Current mapping is deliberately server-side and closed:
- `tenant_owner` → `EXECUTIVE_COMMAND_CENTRE`
- `tenant_legal_partner`, attorney, paralegal, secretary → `LEGAL_PRACTICE`
- sheriff/deputy → `PROCESS_SERVICE`
- legal finance → `LEGAL_FINANCE`
- legal client → `CLIENT_PORTAL`
- admin/manager → `TENANT_ADMINISTRATION`
- auditor → `AUDIT_REPORTING`
- HR catalogue roles → `PEOPLE_OPERATIONS`
- approved provider/operations capacities → `TENANT_OPERATIONS`

Unmapped roles fail closed. The browser validates the exact contract version and closed workspace identifier set, then maps the server-issued workspace ID to an existing presentation component. It no longer uses `ROLE_DASHBOARD_MAP`; the `OWNER → CRM` defect is removed. Manual dashboard preferences cannot override the EOS-selected workspace.

Important boundaries:
- The contract selects presentation only; it does not grant API access.
- Tenant Owner is mapped to the Executive Command Centre, not Sales/CRM or Legal Practice.
- Professional Legal Partner remains a separate Legal Practice role.
- Tenant Partner is not yet an admitted IAM business role in the inspected catalogue; its executive-equivalent role policy and permission parity remain Day 3 work.
- A user holding multiple capacities still requires a separate explicit active-capacity/session selection design; the current bootstrap remains a single-active-business-role projection.

## 8A. Discovery-bound login/MFA selector

The discovered canonical tenant is now carried from `SovereignLogin` through AuthContext into EOS credential login. The same selector is sent with MFA setup and OTP verification. EOS rejects a missing selector or one that differs from the durable user's canonical tenant before issuing a challenge/session. The resulting candidate session is still not promoted until workspace-bootstrap independently proves current ACTIVE membership and IAM.

This closes a tenant-confusion gap in the current two-user, single-tenant-shaped development profile. It is **not** the global-principal/multiple-membership feature: AuthRegistry's credential user still contains one `tenantId`. Multi-firm identity, listing eligible memberships after authentication, selecting one membership, binding MFA/session issuance to that membership, and revocation-safe tenant switching remain open implementation gates.

## 9. Files changed in this implementation phase

| File | Change |
|---|---|
| `tools/eos/auth/workspace_bootstrap_projection.py` | Closed EOS role-to-workspace resolver; workspace identifier included in projection |
| `tools/eos/api/auth_router.py` | Emits versioned canonical workspace identifier in workspace-bootstrap; binds login and MFA requests to the exact discovered tenant selector |
| `tests/unit/test_workspace_bootstrap_projection.py` | Verifies Owner/Legal separation, full published-role mapping and unknown-role denial |
| `client/src/services/api.js` | Removes discovery/local-storage tenant header inference; adds in-memory verified-session transport context |
| `client/src/contexts/authContext.jsx` | Strictly validates workspace contract, carries discovered tenant through login/MFA, and establishes/clears tenant transport context at session boundaries |
| `client/src/components/sovereign/SovereignDashboardController.jsx` | Removes client role-to-dashboard mapping; renders from EOS workspace identifier |
| `client/src/components/auth/SovereignLogin.jsx` and `SovereignMfaPortal.jsx` | Pass only the discovered canonical tenant selector through login/MFA; no tenant default |
| `client/src/__tests__/services/api.test.js` | Verifies discovery storage does not establish authenticated tenant transport |
| `client/src/__tests__/components/sovereignDashboardWorkspaceResolution.test.jsx` | Certifies Owner executive landing, Legal practice landing and fail-closed missing workspace behavior |
| `client/vite.config.js` | Application API fallback and legacy `/auth` compatibility path route directly to EOS |

## 10. Remaining dependency closure before legacy file deletion

The following have not yet been certified for deletion:
- `server/server.js` and `server/app.js`.
- `server/package.json`, `server/package-lock.json`, server-only dependencies and all server subdirectories.
- `scripts/start-dev-stack.mjs`.
- Root `package.json` server/PM2 lifecycle scripts and server-only dependencies.
- Local PDF controller and its imported services/assets.
- Express route modules, models, jobs, workers, sockets, middleware and deployment manifests.
- Legacy test suites and test fixtures.
- Historical evidence/report files stored under `server/`.

The next inventory pass must build a recursive import/caller graph and reconcile each route to a direct EOS route, an explicitly retired endpoint or a migrated artifact implementation. It must also inspect GitHub workflows, Dockerfiles, Kubernetes manifests, PM2 configs, CI scripts, shell launchers and external callback/webhook paths. No file deletion is approved by this report.

## 11. Verification status

| Check | Status |
|---|---|
| Recursive repository tree census | <b>PASS</b> — 7,062 entries; tree response not truncated |
| EOS auth/workspace route chain inspected | <b>PASS</b> |
| Hardcoded WILSY tenant constant removed from current API client | <b>PASS — source inspection</b> |
| Discovery/localStorage no longer establishes request tenant header | <b>PASS — source inspection and updated test</b> |
| Login and MFA require the exact discovered tenant selector | <b>IMPLEMENTED — tests added; execution pending</b> |
| EOS workspace identifier emitted by workspace-bootstrap | <b>PASS — source inspection</b> |
| Browser dashboard resolver no longer maps role names | <b>PASS — source inspection and added test</b> |
| Python unit tests executed | <b>NOT YET RUN</b> — connector edits have not been executed in a local checkout |
| Frontend unit tests executed | <b>NOT YET RUN</b> |
| Local browser login against new contract | <b>NOT YET VERIFIED</b> |
| All APIs proven to work without legacy runtime | <b>NOT YET VERIFIED</b> |
| PDF migration certified | <b>NOT STARTED</b> |
| Legacy runtime and files deleted | <b>NOT STARTED</b> |
| One-million-tenant load test | <b>NOT STARTED</b> |

## 12. Immediate next actions

1. Pull the implementation branch into the integration checkout without overwriting local work.
2. Run the focused Python workspace-bootstrap test and frontend API/dashboard tests.
3. Run the local EOS server from the implementation checkout and verify the browser workspace-bootstrap response contains the exact version and workspace ID.
4. Confirm the Tenant Owner lands on the Executive Command Centre and the Legal user lands on Legal Practice.
5. Capture every frontend API request that still fails or depends on an unmounted EOS route; reconcile route-by-route.
6. Continue the full dependency closure for the legacy server tree, then migrate PDF and replace the local development launcher before removing the runtime.

**Day 1 disposition:** architecture and route census completed to the scope above; first tenant-context and EOS workspace-contract implementation committed on the roadmap branch. No production authority or data was changed.
