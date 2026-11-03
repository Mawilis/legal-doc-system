# WILSY OS Day 1 — Runtime, Route and Dependency Inventory

Date: 2026-11-03
Repository: Mawilis/legal-doc-system
Inventory baseline: eos/atomic-owner-genesis-integration @ e482195fd70eda3fcceafe0ef6c0bdca2c0ad931
Implementation branch: eos/tenant-iam-workspace-implementation
Status: Source inventory completed for the primary local API runtime and its direct route mounts. Full transitive caller/data/workflow classification remains in progress.

## 1. Repository scale snapshot

Git tree enumeration at the baseline commit returned:

| Area | Tracked files / items |
|---|---:|
| Entire repository | 6,221 files |
| `server/` subtree | 1,806 files |
| JavaScript/CommonJS/ESM under `server/` | 1,263 |
| Python under `server/` | 13 |
| `server/` test and test-support paths | 178 |
| `server/routes/` | 155 |
| `server/controllers/` | 99 |
| `server/services/` | 234 |
| `server/models/` | 156 |
| Root `scripts/` JavaScript/ESM files | 140 |
| `client/` JavaScript/JSX/ESM files | 468 |
| GitHub Actions workflows | 60 |

The `server/` subtree is not a homogeneous set of disposable runtime files. It contains production entrypoints, route/controller/service/model code, tests, deployment manifests, workers, evidence, documentation, historical snapshots, binary assets and scripts. These categories require separate disposition.

## 2. Current primary runtime topology

### Browser and EOS

- React client: `client/`.
- Vite development server: port 5173.
- Python EOS FastAPI application: port 9095.
- Current integration source: `eos/atomic-owner-genesis-integration`.
- The local EOS source was verified to declare the newer Founder perpetual commercial-context contract, while the old main checkout declares the older HTTP contract.
- EOS owns authentication, durable tenant membership, dedicated business-role authority, workspace bootstrap, Legal, billing and all business operations.

### Legacy application runtime

- Primary Express entrypoint: `server/server.js`.
- Secondary Express composition: `server/app.js`.
- Root launcher: `scripts/start-dev-stack.mjs`.
- Root `package.json` starts the root launcher via `npm run dev`.
- The launcher starts EOS, then starts `npm run server:start`, then reuses or starts Vite.
- Root scripts include `server:dev`, `server:start`, `pm2:deploy`, `pm2:stop`, and `pm2:status`.
- `server/package.json` defines its own runtime, test, deployment and worker dependency set.
- The secondary `server/app.js` is a separate older application composition. Its tests and import references must be accounted for; it is not safe to delete based solely on the primary entrypoint not importing it.

## 3. Direct route inventory — primary Express entrypoint

The primary Express application has the following explicit route mounts:

| Browser-facing route | Current behavior in `server/server.js` | EOS source / status | Migration disposition |
|---|---|---|---|
| `/api/auth/*` | Raw request forwarding | `tools/eos/api/auth_router.py`, mounted under `/api` | Direct EOS route exists; Vite already points here. |
| `/api/tenants/*` | Raw request forwarding | `tools/eos/api/tenant_router.py`, prefix `/api/tenants` | Direct EOS route exists; Vite already points here. |
| `/api/business/tenants/*` | Path rewrite to `/api/tenants/*` | Tenant router | Inventory callers and preserve only if still used. |
| `/api/employees/*` | Raw request forwarding | `tools/eos/api/employee_router.py`, prefix `/api/employees` | Direct EOS route exists; Vite already points here. |
| `/api/kernel/*` | Raw request forwarding | EOS kernel router is dual-mounted, including `/api` | Direct EOS route exists; Vite already points here. |
| `/api/plans/*` | Raw request forwarding | `tools/eos/api/plan_router.py`, prefix `/api/plans` | Direct EOS route exists; Vite has a billing-path rewrite for some routes that must be reconciled with the canonical plan path. |
| `/api/subscriptions/*` | Raw request forwarding | `tools/eos/api/subscription_router.py`, prefix `/api/subscriptions` | Direct EOS route exists. |
| `/api/billing/*` | Prefix forwarding/rewrite to `/billing/*` | `tools/eos/api/billing_router.py` is dual-mounted at `/billing` and `/api/billing` | Vite rewrites selected paths; confirm callers and canonical path before simplifying. |
| `/billing/*` | Raw prefix forwarding | EOS billing router prefix `/billing` | Direct EOS route exists. |
| `/auth/*` | Rewrites to `/api/auth/*` | EOS auth router prefix `/api` | Legacy alias; frontend should use `/api/auth` exclusively. |
| `/api/crm/owner-workspace/*` | Selective GET/POST forwarding | `owner_commercial_workspace_router`, mounted under `/api` | Direct EOS route exists; must retain commercial-only semantics and not make CRM a Tenant Owner landing page. |
| `/api/wilsy-ai/legal-services` | Selective POST forwarding | `wilsy_ai_legal_services_router`, mounted under `/api` | Direct EOS route exists. |
| `/api/wilsy-ai/legal-next-actions/*` | Selective GET/POST forwarding | `wilsy_ai_advisory_router`, mounted under `/api` | Direct EOS route exists. |
| `/api/legal-acceptance/*` | Selective GET/POST forwarding | `legal_acceptance_router`, mounted under `/api` | Direct EOS route exists. |
| `/api/generate/pdf` | Local Express handler: `generateSovereignArtifactPdf` | No equivalent EOS handler was established by this inventory | Migration blocker. Inspect `client/src/services/pdfService.js`, `server/controllers/businessArtifactPdfController.js`, `server/services/pdfService.js`, and artifact route contracts before retiring. |
| Unmatched `/api/*` | Local 404 response | EOS route inventory must be compared to actual client callers | Every client call must be classified; no blind catch-all forwarding. |

Local health/presentation routes also exist: `/ping`, `/api/ping`, `/api/billing/ping`, `/health`, and `/`. EOS already exposes root/kernel health, but exact health consumers and response contracts must be checked before removal.

## 4. Vite proxy inventory

`client/vite.config.js` currently defines:

- `/api/auth` → EOS port 9095.
- `/auth` → port 4000 (legacy alias; retire after confirming no frontend caller).
- `/api/billing/platform` and `/api/billing/client` → EOS with `/api` removed.
- Selected `/api/billing/{plans,summary,analytics,credit-scores,forensic-status}` → EOS with `/api` removed.
- `/api/kernel` → EOS.
- `/api/tenant-branding` → EOS.
- `/api/crm/owner-workspace` → EOS.
- `/api/legal-operations` → EOS.
- `/api/legal-acceptance` → EOS.
- `/api/tenants` and `/api/employees` → EOS.
- General `/api` catch-all → port 4000.

The intended final client API topology is one direct EOS target for every supported application API route, with explicit path rewrites only where the canonical EOS route contract requires them. Unknown paths should fail visibly rather than being sent to a retired runtime.

## 5. PDF migration blocker

The primary Express entrypoint owns `POST /api/generate/pdf` through `server/controllers/businessArtifactPdfController.js`. Related source/callers include:

- `client/src/services/pdfService.js`
- `client/src/components/artifacts/BusinessArtifactStudio.jsx`
- `server/services/pdfService.js`
- `server/controllers/businessArtifactPdfController.js`
- `server/routes/businessArtifactRoutes.js`
- `server/routes/artifactRoutes.js`
- `server/routes/api.js`

The route is not eligible for deletion until its exact input schema, tenant-branding behavior, authorization, binary response headers, PDF integrity checks, storage and audit evidence are migrated and tested in EOS. Search results show additional document and billing PDF surfaces; each must be classified independently.

## 6. Dashboard and tenant context findings

- `client/src/services/api.js` previously pinned `WILSYTENANT-4CD2FZ4O` in `CANONICAL_WILSY_TENANT_ID`. This is a test-tenant constant and cannot be global request authority.
- `client/src/contexts/authContext.jsx` already requires EOS `workspace-bootstrap` to revalidate the principal, membership, business role, tenant and branding before session promotion.
- The existing workspace bootstrap response included tenant ID, business role, membership and business-role revisions, Legal presentation permissions, branding and tenant metadata, but no canonical workspace identifier.
- `client/src/components/sovereign/SovereignDashboardController.jsx` previously derived dashboard selection from browser role strings and route intent. It mapped legacy `OWNER` to CRM.
- The durable business-role catalogue currently includes `tenant_owner`, Legal practice roles and other tenant capacities, but does not yet include a distinct `tenant_partner`. Do not conflate Tenant Partner with `tenant_legal_partner`.

## 7. Day 1 implementation delivered on this branch

The following changes have been committed to `eos/tenant-iam-workspace-implementation`:

1. Added `tools/eos/auth/workspace_contract.py`: deterministic, fail-closed mapping from exact durable business-role identifiers to a versioned canonical workspace identifier.
2. Extended `WorkspaceBootstrapProjection` with `workspace_id` and `workspace_contract_version`; mapping occurs only after principal, membership, role and canonical tenant validation.
3. Extended `GET /api/auth/workspace-bootstrap` to publish `workspaceId` and `workspaceContractVersion`.
4. Updated browser session promotion to require a supported EOS workspace contract before marking the session authenticated.
5. Updated dashboard resolution to prefer the EOS workspace contract; stale role labels, manual dashboard intent and browser preferences cannot override it. Legacy `OWNER` now resolves to the executive presentation fallback rather than CRM.
6. Removed the hardcoded WILSY tenant constant from the HTTP client. The client now forwards only a syntactically valid tenant ID from the active server workspace projection or discovered tenant projection; malformed/missing storage produces no tenant header. EOS remains responsible for verifying current authenticated tenant scope.
7. Added/updated focused Python and browser tests for canonical role-to-workspace resolution and dynamic tenant transport.

These changes are implementation evidence, not a claim of local test execution or production certification. Local test execution and real-Mongo/browser verification remain required.

## 8. Retirement gates — no deletion yet

The following files/directories remain protected from blind deletion:

- `server/server.js` until every route, including PDF, health and websocket/worker consumers, is migrated.
- `server/app.js` until imports, scripts, tests and deployment references are classified.
- `server/routes/`, `server/controllers/`, `server/services/`, `server/models/` until each item has caller and persistence disposition.
- `server/tests/` and `server/__tests__/` until tests are migrated, superseded with equivalent certification, or proven dead.
- `server/docs/`, `server/assets/`, evidence and signed/historical artifacts are not runtime cleanup targets.
- Root JavaScript scripts are mixed-use: frontend build/test/guards, repository maintenance, deployment and legacy runtime. Each script needs its own classification.
- Root package dependencies are shared; only remove packages after import and script reference analysis.
- React/Vite source and build/test tooling remain part of the browser product and are not legacy application-server files.

## 9. Remaining Day 1 tasks

- Complete recursive import/caller search for `server/app.js`, `server/server.js`, `businessArtifactPdfController`, websocket servers, workers and scheduled jobs.
- Compare all frontend API callsites with EOS OpenAPI routes and identify missing, duplicate and legacy paths.
- Inspect all GitHub workflows and deployment manifests for dependencies on `server/`, root server scripts, port 4000 and server-specific secrets.
- Classify all 1,806 `server/` files into: active runtime, migratable domain capability, frontend/build support, test/evidence, historical artifact, or deletion candidate.
- Do not delete until a file's consumers, persisted collections, workflow use and replacement tests are recorded.

**END — DAY 1 RUNTIME, ROUTE AND DEPENDENCY INVENTORY**
