# WILSY OS — Day 1 Runtime, Dependency and Route Inventory

Date: 2026-11-03
Repository: Mawilis/legal-doc-system
Inventory baseline: eos/atomic-owner-genesis-integration at e482195fd70eda3fcceafe0ef6c0bdca2c0ad931
Working branch: eos/tenant-discovery-iam-dashboard-roadmap
Status: Initial dependency/route inventory and first tenant-header correction committed; exhaustive recursive legacy retirement certification remains in progress.

## 1. Runtime boundary

| Layer | Current artifact | Target disposition |
|---|---|---|
| Business/API authority | Python EOS / FastAPI, tools/eos/api/server.py | Retain; sole application API and business-authority runtime |
| Browser application | React, JSX, client/src | Retain; presentation and transport only |
| Frontend development/build | Vite, client/vite.config.js, client/package.json | Retain; not a business runtime |
| Legacy API runtime | Express, server/server.js and server/app.js | Retire after every active route, job, import, data dependency and test has a certified EOS replacement or documented removal |
| Development orchestration | scripts/start-dev-stack.mjs | Replace with EOS + Vite launcher; no additional API process |
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
| Dashboard selection | SovereignDashboardController.jsx | No canonical EOS workspace decision contract yet at baseline | Currently browser role map | Must be replaced by EOS workspace_id contract; client may map only a server-issued workspace_id to a view |
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
- Request tenant scope is read from the JSON server-discovery projection in discoveredTenant.
- Malformed, absent or non-canonical discovery data yields no tenant header; there is no WILSY, GLOBAL_ROOT or other fallback.
- A stale default header is removed when discovery cannot supply a valid tenant.
- client/src/__tests__/services/api.test.js now covers a non-WILSY discovered tenant, missing/malformed discovery, and preservation of the MFA candidate bearer without substituting a tenant.
- client/src/components/ErrorBoundary.jsx no longer manufactures GLOBAL_ROOT for telemetry; it sends a tenant header only when it can parse a valid server-discovery projection.

This changes transport selection only. EOS continues to prove membership and authorization. It does not create or assign membership, issue a tenant-scoped session, or enable cross-tenant switching.

## 4. Client route and session dependencies

| Artifact | Responsibility | Day 1 finding / disposition |
|---|---|---|
| client/src/components/sovereign/TenantDiscovery.jsx | Tenant discovery presentation | Retain; calls AuthContext discovery |
| client/src/contexts/authContext.jsx | Candidate token, discovery projection, MFA and server bootstrap promotion | Retain and evolve; must support selected membership/session context from EOS |
| client/src/contexts/tenantContext.jsx | Browser projection of authenticated tenant | Retain as projection only; prevent local storage and directory calls from authorizing tenant switches |
| client/src/services/api.js | Shared Axios transport | Retain; hardcoded tenant removed; no fallback before discovery |
| client/src/components/sovereign/SovereignDashboardController.jsx | Dashboard component composition | Refactor only after EOS workspace contract exists; role-to-dashboard map is not authority |
| client/src/components/ErrorBoundary.jsx | Error boundary and optional telemetry | Retain; synthetic GLOBAL_ROOT tenant fallback removed |
| client/vite.config.js | Development routing | Must be audited so every API path goes directly to EOS; remove any route targeting port 4000 after EOS equivalents are verified |
| client/src/__tests__/services/api.test.js | Shared transport contract tests | Updated for dynamic discovered tenant and fail-closed no-discovery behavior |

## 5. EOS authority dependencies

| Concern | Canonical files / components | Required proof |
|---|---|---|
| Principal identity and session | tools/eos/auth/identity.py, authentication.py, tools/eos/saas/auth/auth_registry.py | Global principal identity separated from tenant membership; access token bound to selected membership/session revision |
| Tenant discovery | tools/eos/api/auth_router.py, tools/eos/saas/domain/auth.py DiscoverRequest, tools/eos/saas/tenancy/tenant_registry.py | Alias/domain exact resolution, ACTIVE tenant, bounded response and anti-enumeration behavior |
| Membership | tools/eos/auth/tenant_access.py, tenant_membership.py, tenant_membership_repository.py | Exact ACTIVE membership for principal and discovered tenant |
| Business capacity | tools/eos/auth/tenant_business_role_authority.py, tenant_authority_policy.py | Explicit active capacity selection; no silent most-permissive role or union |
| Authorization | tools/eos/auth/tenant_authorization.py, tenant_authorization_http.py, role and permission registries | Exact operation/permission and active granting-role decisions on every protected route |
| Workspace bootstrap | tools/eos/auth/workspace_bootstrap_projection.py and GET /api/auth/workspace-bootstrap | Extend to a versioned canonical workspace decision with workspace_id, active membership/capacity references, revisions and bounded manifest |
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

- Root package.json currently includes Express-era scripts: server:dev, server:start, pm2:deploy, pm2:stop and pm2:status. Remove only after no active workflow, developer command or deployment references them.
- Root package.json includes frontend/test dependencies and scripts as well as legacy server dependencies. Do not remove all root Node dependencies wholesale.
- client/package.json owns Vite, React, browser build and Vitest dependencies; preserve.
- scripts/start-dev-stack.mjs starts EOS, a legacy Express process and the Vite client. Replace with a launcher that starts only EOS and Vite and performs explicit health/readiness checks.
- client/vite.config.js contains direct EOS route entries and legacy port-4000 proxy entries. Build a full path-to-EOS-router table before deleting catch-all/legacy entries.
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
| Identify principal/membership limitation in login | CONFIRMED; implementation outstanding |
| Identify role/capacity ambiguity | CONFIRMED; implementation outstanding |
| Freeze EOS workspace contract schema and implement it | OUTSTANDING |
| Exhaustive recursive server route/import/test/workflow/data inventory | IN PROGRESS |
| Retire legacy server runtime | NOT STARTED; blocked on migration proof |

## 9. Safety and release boundaries

- No membership, role, permission, subscription, entitlement or user record was created or modified by the tenant-header correction.
- No production data migration has been run.
- No legacy server files have been deleted.
- A missing discovery projection must never be replaced with a tenant default.
- Tenant discovery is not proof of membership; a user must be admitted by EOS against the selected tenant.
- A workspace contract controls presentation only; each operation remains independently authorized.
- Keep Tenant Owner / proposed Tenant Partner executive authority separate from professional Legal Partner practice authority.
- Do not claim multi-tenant principal support until the identity, login, MFA, session, membership and revocation paths all support it and tests prove isolation.

**END OF DAY 1 INVENTORY**
