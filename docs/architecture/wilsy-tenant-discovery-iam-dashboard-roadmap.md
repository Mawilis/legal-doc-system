# WILSY OS — Tenant Discovery, IAM and Dashboard Resolution Roadmap

Version: v1.0.0-TENANT-DISCOVERY-IAM-WORKSPACE-ROADMAP
Authority: Wilsy OS Core Governance
Date: 2026-11-03
Status: Seven-day engineering programme; Day 1 implementation started. Dynamic discovery-derived request scope is committed; global-principal membership selection and canonical workspace contract remain outstanding.
Scope: EOS-owned identity, tenant resolution, IAM, workspace selection, dashboard delivery and retirement of the legacy server-side JavaScript runtime.

## 1. Executive decision

WILSY OS will operate one canonical business and authorization runtime: Python EOS. The React client remains a presentation layer. Vite, React, JavaScript and JSX remain permissible frontend development/build technologies; they do not own identity, tenant, role, permission, workspace, subscription, legal, financial or operational truth.

The required sign-in sequence is:

`TENANT DISCOVERY → IDENTITY AUTHENTICATION → MEMBERSHIP RESOLUTION → ACTIVE CAPACITY SELECTION → EOS IAM DECISION → WORKSPACE CONTRACT → DASHBOARD PROJECTION`.

A browser role label, URL, local-storage value, tenant alias, frontend constant or manually selected dashboard must never grant access. EOS must independently authorize every protected API request.

The current development tenant is `WILSYTENANT-4CD2FZ4O` (alias `wilsy`). It is a development/testing tenant, not a global tenant constant. The currently known test population is two users: the tenant owner and a tenant Legal user. These are baseline fixtures, not evidence of production scale.

## 2. Repository findings at the integration checkpoint

Repository: `Mawilis/legal-doc-system`
Inspected ref: `eos/atomic-owner-genesis-integration`
Checkpoint: `e482195fd70eda3fcceafe0ef6c0bdca2c0ad931`
Related work: PR #341, atomic tenant-owner genesis integration.

### Confirmed defects and constraints

| Finding | Evidence | Consequence |
|---|---|---|
| Legacy dashboard alias maps `OWNER` to CRM | `client/src/components/sovereign/SovereignDashboardController.jsx`, `ROLE_DASHBOARD_MAP` | An account projected as `OWNER` can land in CRM; `TENANT_OWNER` maps to Executive. Dashboard choice is still client role mapping. |
| Frontend pins one tenant ID | `client/src/services/api.js`, `CANONICAL_WILSY_TENANT_ID` and `resolveRequestTenantId()` | Requests are not safely tenant-dynamic. The interceptor writes the WILSY test tenant header rather than deriving verified active-session scope. |
| Login user record is single-tenant shaped | `tools/eos/saas/auth/auth_registry.py`; user records and authentication carry `tenantId`, and email lookup is global | One person with memberships in several firms is not yet represented as a clean global principal plus many tenant memberships. |
| Login does not explicitly select a tenant membership | `client/src/contexts/authContext.jsx` and `tools/eos/api/auth_router.py` | Discovery and login are separate, but the credential endpoint authenticates by email/password and relies on the stored user's tenant. |
| Workspace bootstrap is a useful foundation | `GET /api/auth/workspace-bootstrap`, `tools/eos/auth/workspace_bootstrap_projection.py` | EOS already revalidates principal, active membership, business role and canonical tenant before promoting the browser session. |
| Multiple active capacities can be ambiguous | `tools/eos/auth/tenant_business_role_authority.py` | When more than one active role is eligible for the same operation, the resolver returns `MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES`; capacity selection must be explicit. |
| No distinct Tenant Partner business role is in the current catalogue | `tools/eos/auth/tenant_authority_policy.py`, `TENANT_ROLES` | `tenant_legal_partner` is a professional Legal role and must not be repurposed as an executive co-owner. |
| Owner grants currently include CRM work-item permissions | `tools/eos/auth/roles.py`, `TENANT_OWNER` | Owner authority and owner workspace semantics need an executive command model, not a sales/customer-service task model. |
| Current frontend route is not EOS-only | `client/vite.config.js` | Several paths go directly to EOS, while `/auth` and the catch-all `/api` route to port 4000. |
| Development launcher starts an additional Express service | `scripts/start-dev-stack.mjs` | The launcher waits for EOS, starts `server/server.js`, then starts/reuses Vite. |
| Express runtime is predominantly a forwarding layer, with one local PDF endpoint | `server/server.js` | It forwards auth, tenant, employee, kernel, plan, subscription, billing, legal acceptance, owner-workspace and advisory routes to EOS; `/api/generate/pdf` remains locally implemented and must be migrated or retired before removal. |
| A second, older Express application exists | `server/app.js` | It contains legacy local CRM, billing, telemetry, QR and other routes. Its live callers, imports, tests and persisted-data dependencies must be mapped before deletion. |
| Root package scripts retain server lifecycle commands | root `package.json` | Server start/dev and PM2 scripts must be retired after replacement. Frontend build/test scripts and required JS test tooling must not be deleted blindly. |
| Owner-genesis PR is not an end-to-end login completion | PR #341 description | The genesis command is not yet wired to an authenticated onboarding/login route; no production Owner login is claimed by that PR. |

### Canonical source inventory already identified

- Identity/authentication: `tools/eos/auth`, `tools/eos/saas/auth`, `tools/eos/api/auth_router.py`.
- Tenant identity and membership: `tools/eos/saas/tenancy/tenant_registry.py`, `tools/eos/auth/tenant_membership*`, `tools/eos/auth/workspace_bootstrap_projection.py`.
- IAM: `tools/eos/auth/roles.py`, `tenant_authority_policy.py`, `tenant_business_role_authority.py`, `tenant_authorization.py`, role assignment and permission registries.
- API composition: `tools/eos/api/server.py` and routers under `tools/eos/api`.
- Client session and tenant projections: `client/src/contexts/authContext.jsx`, `client/src/contexts/tenantContext.jsx`.
- Dashboard selection: `client/src/components/sovereign/SovereignDashboardController.jsx`.
- Discovery presentation: `client/src/components/sovereign/TenantDiscovery.jsx` and `client/src/pages/Discovery.jsx`.
- Runtime routing: `client/vite.config.js`, root `package.json`, `scripts/start-dev-stack.mjs`, `server/server.js`.

This is a focused architecture inventory, not a claim that every repository file has already been individually certified. Full retirement requires recursive import/caller/test/workflow inspection of every candidate path.

## 3. Target identity and tenant model

### 3.1 Separate the person from the firm

Use one global principal identity for a person and a separate, durable membership for each tenant.

Target relationship:

`Principal 1 ── N TenantMembership N ── 1 Tenant`

A membership carries its own lifecycle, tenant business capacities, authorization-role assignments, permission evidence, invitation/admission provenance and revision. A person's global credentials do not themselves confer access to any tenant.

A person may:
- belong to one firm;
- belong to multiple firms using one identity;
- hold multiple separately granted capacities within one firm;
- have one active tenant and one active capacity per authenticated workspace session.

### 3.2 Tenant discovery

1. Accept a tenant alias, canonical tenant identifier or verified custom domain.
2. Resolve exactly one ACTIVE canonical tenant through EOS.
3. Return only a minimal, browser-safe tenant identity projection.
4. Do not return a tenant directory, membership list or private account data before authentication.
5. Normalize aliases and enforce rate limits, bounded errors and enumeration-resistant responses.
6. Never treat discovery as membership, authentication, subscription or workspace authority.

For `wilsy`, discovery must resolve the canonical development tenant `WILSYTENANT-4CD2FZ4O`. No client constant may assume that identity for other tenants.

### 3.3 Authentication and membership selection

- Authenticate a global principal and complete required MFA.
- Resolve the discovered tenant against that principal's current ACTIVE membership.
- If the principal has several eligible tenant memberships, provide a server-authorized tenant selector after authentication; issue a new tenant-scoped session when the active tenant changes.
- If discovery was supplied before login, the server must verify the exact membership for that tenant; it must not trust the submitted tenant header.
- Session/token context must be bound to principal, tenant, membership, session, credential/authentication revision and expiry. Role/permission claims are not a substitute for current durable IAM reads.
- Revocation, suspension, tenant mismatch, stale revisions and unavailable authority fail closed.

### 3.4 Multi-capacity selection

A membership can hold more than one independently evidenced business capacity. EOS must return the capacities the principal is currently entitled to activate. The user selects a capacity/workspace when more than one is valid; the selection is bound to a fresh server-authorized session context and revalidated on every protected request.

Do not union all permissions merely because a person has multiple roles. Do not select the most permissive role silently. The selected capacity narrows the request context; the underlying permission and resource checks remain mandatory.

## 4. Target law-firm role and dashboard model

| Tenant capacity / role | Default workspace | Intended boundary |
|---|---|---|
| Tenant Owner | Executive Command Centre | Firm identity, commercial position, governance, subscriptions, executive reporting and authorised organisation oversight. No automatic confidential matter access. |
| Tenant Partner | Executive Command Centre | Same executive operating workspace and explicitly equivalent executive permission profile as Tenant Owner, where the firm's IAM policy grants this capacity. Ownership transfer/title evidence remains a separate lifecycle authority. |
| Legal Practice Partner (`tenant_legal_partner`) | WILSY Legal OS | Professional practice work, only within current legal role, matter assignment, confidentiality, conflict and G68 controls. |
| Legal Attorney | WILSY Legal OS | Assigned legal work and permissions only. |
| Candidate Attorney / Paralegal / Secretary | WILSY Legal OS | Supervised or assigned daily legal operations according to exact IAM grants. |
| Legal Finance | Legal finance workspace | Finance functions and matter financial visibility only where separately authorized. Kennel EOS remains the exclusive financial execution authority. |
| Sheriff / Deputy | Process-service workspace | Office-, assignment- and role-scoped process-service operations. |
| Sales / Business Development | CRM / Sales workspace | Leads, pipeline, customer acquisition and sales follow-ups. |
| Customer Services | Customer Service workspace | Client support and service operations. |
| Auditor | Audit / reporting workspace | Read-only evidence and reports within explicit scope. |

**Tenant Partner is not `tenant_legal_partner`.** The proposed business role identifier is `tenant_partner` with a separate authorization-role mapping. Owner and Tenant Partner receive the same executive workspace and approved executive operating permissions. A professional Legal Partner capacity is separate and may be held by the same person only through an independently granted capacity.

## 5. EOS workspace contract

Replace browser role-to-dashboard inference with one versioned EOS workspace contract. The contract should contain:

- canonical `tenant_id`, `principal_id`, `membership_id` and active capacity identifier;
- current authorization/membership revisions and session correlation;
- canonical `workspace_id` and contract version;
- a bounded navigation/module manifest;
- presentation-safe capability identifiers and feature entitlements;
- the minimal profile and tenant identity projection;
- server-generated decision/evidence correlation identifiers;
- explicit denial or unavailable states where no workspace can be resolved.

The frontend may map the canonical `workspace_id` to a presentation component. It may not infer the workspace from `OWNER`, `TENANT_OWNER`, `LEGAL_PARTNER`, a role array, local storage, a query parameter or a manually selected dashboard. Every API behind a visible module must independently enforce EOS IAM and tenant scope. A workspace manifest is not an authorization token.

Recommended workspace identifiers include `EXECUTIVE_COMMAND_CENTRE`, `LEGAL_PRACTICE`, `LEGAL_FINANCE`, `PROCESS_SERVICE`, `SALES_CRM`, `CUSTOMER_SERVICE`, and `AUDIT_REPORTING`. Final identifiers must be frozen in the EOS contract and tested against the published role/capacity catalogue.

## 6. Executive Command Centre product definition

The Tenant Owner and Tenant Partner landing environment is an executive legal-enterprise dashboard, not CRM.

It should present only server-verified and permissioned information:
- firm and tenant identity/status;
- subscription and product entitlements;
- commercial commitments and renewal status;
- governance, assurance and compliance posture;
- executive operational indicators and approved firm-level reports;
- organisation/workforce overview;
- authorised practice-level performance summaries that do not reveal confidential matter content;
- executive decisions and alerts with traceable source evidence.

Leads, deals, sales pipeline, customer-service queues and sales follow-ups belong to their respective business functions. Matter files, legal advice, client communications and reviewer actions remain behind separate professional practice permissions and matter-level confidentiality checks.

The executive dashboard must not invent empty counts when a source is unavailable. Each tile reports source state, freshness and authority; unavailable data is not reported as zero.

## 7. Seven-day execution plan

### Day 1 — Freeze architecture and map the runtime

- Establish the integration branch as the baseline; record clean/dirty worktrees and protect local uncommitted work.
- Build a complete route map: frontend caller → Vite path → EOS route → service → registry/collection → IAM permission → tests.
- Inventory every `server/` file, import, entrypoint, route, job, worker, package dependency, test, workflow, deployment file and persisted collection.
- Identify every endpoint currently reached through port 4000 and whether EOS has an equivalent.
- Freeze the workspace contract, role/capacity vocabulary and test matrix before behavior changes.

**Exit:** no unknown active API path, no unclassified server entrypoint, approved target role/workspace matrix.

### Day 2 — Tenant discovery and global identity

- Preserve the existing exact tenant discovery route, improve safe discovery errors and rate limiting where required.
- Separate global principal credentials from tenant membership; design a compatibility migration for the existing two development users.
- Bind login to the discovered/selected tenant membership and MFA flow.
- Support post-auth tenant selection for principals with multiple memberships.
- Remove the hardcoded WILSY tenant ID from frontend request authority; derive tenant context only from the verified EOS session/workspace projection.

**Exit:** the owner and Legal test users can authenticate against the WILSY development tenant; a synthetic second tenant proves isolation without changing production records.

### Day 3 — IAM capacities and workspace decision

- Add distinct `tenant_partner` business-role vocabulary and explicit policy eligibility.
- Define a shared executive permission profile for `tenant_owner` and `tenant_partner`; keep ownership lifecycle authority distinct.
- Preserve `tenant_legal_partner` as professional practice capacity.
- Implement explicit active-capacity selection for users with multiple eligible roles.
- Compose a versioned EOS workspace decision and decision-evidence trail.
- Remove client role-name mapping as the authority for workspace selection.

**Exit:** policy tests prove Owner and Tenant Partner resolve to the same executive workspace and approved executive permissions; Legal Partner resolves to Legal Practice; ambiguous or revoked capacities fail closed.

### Day 4 — Dashboard composition and user experience

- Build the Executive Command Centre as the Tenant Owner/Tenant Partner landing workspace.
- Route Legal practitioners, finance, process-service, sales, customer-service and auditor roles to their distinct workspaces using the EOS workspace contract.
- Replace CRM labels and navigation from the executive workspace.
- Make multi-capacity users select a valid workspace/capacity when needed.
- Add source freshness, unavailable states and permission-aware dashboard tiles.
- Ensure browser navigation cannot open a workspace whose server authorization is absent.

**Exit:** each test role lands on its intended workspace; cross-role deep links and direct API calls remain denied without permission.

### Day 5 — Retire the legacy server-side JavaScript runtime

- Replace `scripts/start-dev-stack.mjs` with an EOS-first development launcher that starts Python EOS and the Vite client only.
- Route every required client API path directly to EOS; remove port-4000 and legacy `/auth` forwarding.
- Migrate or retire the local PDF endpoint after binary-response and document-integrity certification.
- Confirm all server-side route behavior has an EOS owner or is intentionally removed.
- Remove Express runtime entrypoints, the legacy server package, server-only environment configuration, PM2 lifecycle scripts and obsolete deployment references only after dependency checks.
- Remove dead legacy files only when import, route, test, workflow, job, data and operational references are proven absent or migrated.
- Retain React/JSX client source, Vite configuration/build tools, browser tests and necessary Node-based frontend tooling. EOS-only means EOS owns application APIs and business authority; it does not mean deleting the JavaScript frontend or the build runtime it requires.

**Exit:** no Express application process, no port 4000 listener, no active frontend API route to port 4000, no production dependency on the legacy server directory, and all required APIs are EOS-owned.

### Day 6 — Adversarial and regression certification

Test at minimum:
- unknown, inactive, archived and duplicate tenant aliases;
- tenant discovery followed by wrong-tenant login;
- same principal with two tenant memberships;
- one membership with Owner and Tenant Partner capacities;
- Owner and Tenant Partner executive permission parity;
- Tenant Partner without ownership-transfer authority;
- Tenant Partner plus separate Legal Practice capacity;
- Legal Partner without executive capacity;
- revoked/suspended membership, role and permission;
- stale session, stale credential revision and tenant switching;
- direct API access bypassing the dashboard;
- cross-tenant object identifiers, cache collisions and replay;
- missing/outage/corrupt IAM or workspace source;
- unavailable dashboard data versus true zero;
- PDF, billing, Legal Operations, tenant branding and auth regression after route migration.

Use disposable real-Mongo replica-set tests for transaction/index behavior and browser tests against the actual local EOS runtime. Do not use the development tenant to simulate destructive migration.

**Exit:** zero cross-tenant disclosures, zero unauthorized workspace/API access, all existing critical EOS suites pass, and every retired route has a tested replacement or a documented removal.

### Day 7 — Scale, operational readiness and release decision

- Run indexed tenant-discovery and membership-resolution load tests at increasing tenant/principal counts, including a one-million-tenant dataset simulation.
- Verify no global tenant scans; validate compound indexes for canonical alias/domain, principal-to-membership, tenant-to-membership, role/capacity and current-session lookup.
- Ensure cache keys include tenant, principal, membership/capacity and relevant authorization revision; invalidate on revocation and role changes.
- Measure p50/p95/p99 latency, error rate, connection-pool pressure, cache hit ratio and tenant-isolation failures.
- Complete backup/restore, audit evidence, observability, security review and deployment-environment checks.
- Publish a release decision with verified facts, unresolved gates and rollback instructions.

**Exit:** scale evidence is published; no claim of one-million-tenant production readiness is made until the dataset, load profile, infrastructure and isolation tests demonstrate it.

## 8. Legacy JavaScript retirement rules

### Remove after proof

- The Express application/runtime under `server/`, including its package and runtime-only dependencies.
- The current Express forwarding gateway and the local PDF handler after PDF migration.
- `scripts/start-dev-stack.mjs` after an EOS-only launcher is tested.
- Root `package.json` scripts that start, deploy or manage the legacy Express service.
- Vite proxy entries targeting port 4000 or forwarding `/auth` to that port.
- Legacy environment files and deployment references that exist only for the retired server, after secrets/config ownership is migrated securely.
- Dead server-only route, controller, middleware, model, job and worker files after recursive dependency and test proof.

### Preserve unless separately proven obsolete

- `client/src/**/*.js`, `*.jsx`, CSS and React components: these are the browser application, not the server authority.
- Vite and frontend build/test configuration.
- Browser automation and frontend certification.
- JavaScript utilities still used by tests, documentation/security guards or build pipelines.
- Historical governance evidence, signed documents, test fixtures and audit artifacts.
- Python EOS source, domain contracts, registries, migrations, workflows and tests.

No bulk deletion by filename extension. No deleting an entire directory before an import/caller/test/workflow/data dependency report exists. No removing tests to make cleanup pass.

## 9. Scale and security design for one million tenants

- Tenant discovery must be indexed exact lookup by canonical alias/domain/ID; never scan all tenants or expose directory search.
- Every protected database operation must include tenant scope in the query predicate, not merely filter after retrieval.
- Use unique indexes for canonical tenant identity and membership identity; use compound indexes for common `(tenant_id, principal_id, status)` and `(principal_id, status)` access paths, adjusted to actual query plans.
- Keep authorization reads close to the authoritative IAM source; cache only with tenant/principal/capacity/revision keys and reliable revocation invalidation.
- Do not place large role/permission lists in a long-lived token as the source of truth.
- Use bounded pagination, per-tenant quotas, rate limits and abuse controls for discovery and login.
- Avoid cross-tenant aggregate reports unless a separately authorized platform-level purpose and data minimization contract exists.
- Treat one million tenants as a load-test target, not a current capability claim. Production capacity also depends on actual cluster topology, indexes, shard strategy, connection pools, regions, observability and operational staffing.

## 10. Competitive design references

Research date: 3 November 2026. Public vendor descriptions are product claims, not independent security or performance audits.

- Microsoft Learn, [Identity and access management for SaaS workloads](https://learn.microsoft.com/en-us/azure/well-architected/saas/identity-access): one user identity can have access to multiple tenants; membership and tenant isolation are explicit; authentication and authorization are separate.
- Microsoft Learn, [Identity approaches for multitenant solutions](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/identity): active tenant context and role claims must be selected and validated; user and tenant must not be conflated.
- AWS Prescriptive Guidance, [Multi-tenant SaaS authorization and API access control](https://docs.aws.amazon.com/prescriptive-guidance/latest/saas-multitenant-api-access-authorization/introduction.html): consistent policy decision/enforcement, tenant isolation, RBAC/ABAC and auditable API authorization.
- Clio, [Roles and Permissions](https://help.clio.com/hc/en-us/articles/9200279456667-Roles-and-Permissions-in-Clio-Manage): standard and custom roles, permission-level controls, firm dashboard and practice-specific Partner/Paralegal/Billing examples. Clio's documented most-permissive-role inheritance is not copied as an automatic WILSY privilege-union rule.
- Actionstep, [System Roles and Data Permissions](https://support.actionstep.com/hc/en-us/articles/50482548468499-Configuring-System-Roles-and-Data-Permissions-Admin): modular system permissions, object-level controls and division-scoped data permissions.
- MyCase, [Large law firm software](https://www.mycase.com/solutions/large-law-firm-software/): firm-wide insights, role-based controls and department/practice-area access.
- Existing WILSY process-service competitor research: `docs/competitive/2026-11-02-legal-operations-competitive-benchmark.md`. This remains a separate product-vertical benchmark.

Competitive lesson: use a clear persona/workspace experience, granular permissions and firm-level reporting, but preserve WILSY's stricter separation between executive authority, professional legal authority, matter confidentiality and financial execution.

## 11. Release gates and non-negotiable boundaries

1. EOS is the sole application API/business-authority runtime.
2. The browser is presentation only; IAM and resource authorization remain server-enforced.
3. Tenant discovery is not membership. Authentication is not authorization. Workspace selection is not permission.
4. Tenant Owner and Tenant Partner share the approved executive workspace and executive operating permission profile; legal ownership evidence and non-delegable lifecycle actions remain separately governed.
5. `tenant_legal_partner` remains a professional Legal capacity and never becomes an executive alias.
6. CRM/Sales and Customer Services are not the Tenant Owner landing environment.
7. Owner executive summaries do not grant access to confidential Legal matter files or professional review actions.
8. Kennel EOS remains the exclusive financial execution authority. Approval, release authorization, execution and settlement remain distinct.
9. Missing or unavailable evidence fails closed; unavailable data is never displayed as zero.
10. Legacy runtime deletion is complete only when callers, routes, imports, tests, workflows, deployment references and data dependencies are reconciled.
11. No production readiness or one-million-tenant capacity claim without live infrastructure, adversarial tests and measured evidence.
12. No secrets, credentials or private governance evidence are copied into Git or this roadmap.

## 12. Implementation progress — 3 November 2026

Day 1 implementation is active on `eos/tenant-discovery-iam-dashboard-roadmap`.

- Removed the compiled-in WILSY tenant constant from `client/src/services/api.js`. Authenticated tenant transport is now set only after EOS workspace-bootstrap revalidates the current session; discovery storage alone cannot establish authenticated request scope.
- Added tests for authenticated tenant context, discovery-only denial, missing tenant context and MFA bearer preservation. Execution is pending in the local checkout/CI.
- Removed the synthetic `GLOBAL_ROOT` tenant fallback from browser error telemetry.
- Added a versioned EOS workspace contract. EOS maps the exact durable business role to a closed `workspaceId` and returns `workspaceContractVersion`; AuthContext validates both before session promotion.
- Replaced browser role-to-dashboard inference with a presentation mapping from the EOS `workspaceId`. Added tests for Owner executive routing, Legal practice routing, absent-contract denial and refusal to honor a conflicting manual dashboard preference.
- Changed Vite's catch-all `/api` and legacy `/auth` compatibility route to target Python EOS directly. No port-4000 proxy target remains in the current PR branch.
- Added an EOS-only shell development launcher with process-working-directory checks, changed the root `dev` command to use it, removed root Express lifecycle scripts and deleted the old multi-runtime `.mjs` launcher.
- Expanded the Day 1 inventory with the client endpoint census, direct-origin findings, Express route mounts, legacy process-manager references, production retention-policy conflicts and root/server/client package dependency counts.

The first workspace contract is a presentation-routing contract, not a full membership-selection implementation. Current AuthRegistry login still authenticates against a user record carrying one `tenantId`; the ACCESS token carries one tenant context, and workspace bootstrap revalidates membership for that scope. A global principal with multiple tenant memberships, discovery-bound membership selection, tenant-scoped session issuance/switching, explicit active-capacity selection and revocation-safe tenant switching remain outstanding.

The currently published workspace map routes `tenant_owner` to `EXECUTIVE_COMMAND_CENTRE` and professional Legal roles to their separately governed workspaces. The proposed `tenant_partner` business capacity is not yet present in the IAM catalogue; it must be added as a distinct executive-equivalent capacity, never by reusing `tenant_legal_partner`.

The route/dependency inventory is substantially expanded but still requires a recursive caller/import/test/workflow/data reconciliation before deleting the remaining legacy server tree. No legacy server source files have been deleted. No membership, role, permission, subscription, entitlement or production data was changed. No test execution or certification is claimed until it has been run against the synced local checkout.

## 12A. Discovery-bound authentication implementation — 3 November 2026

The Day 2 entry gate has begun with a narrow, reversible tenant-binding change:

- The browser login call now sends the exact canonical `tenantId` returned by `POST /api/auth/discover`; no WILSY tenant fallback is introduced.
- EOS `AuthRequest` and `VerifyOTPRequest` accept a strict optional `tenant_id` selector for compatibility at the schema boundary, but login, MFA setup and OTP verification reject a missing selector and reject a selector that differs from the durable authenticated user's canonical `tenantId`.
- The selected tenant is carried through the MFA setup/verification requests. The final ACCESS session is still promoted only after `GET /api/auth/workspace-bootstrap` revalidates current principal, ACTIVE membership, business capacity and canonical tenant.
- Added backend tests for missing discovery and tenant mismatch, and updated browser/backend fixtures to assert selector propagation.
- Removed the unreferenced `client/src/bootstrap/EnterpriseBootstrap.jsx`, which fabricated `tenant_wilsy_001` and provided a direct login bypass; repository search found no imports/callers.
- Removed the `wilsy` fallback from the legacy superadmin auth adapter and the legacy ObjectId tenant fallback from the sovereign auth bridge. The adapter now requires the EOS-discovered tenant projection and sends `tenant_id`.
- Removed the unused bootstrap component that fabricated a tenant and bypassed MFA, removed the synthetic `GLOBAL_ROOT` telemetry tenant, and blocked browser-only cross-tenant switching until EOS issues a fresh membership-bound session.

**Important scope limit:** this closes a discovery-to-login tenant-confusion gap for the existing single-tenant-shaped AuthRegistry user record. It does not yet implement a global principal with multiple memberships. A person who belongs to multiple firms still needs the Day 2 global-principal credential model, membership enumeration after authentication, explicit selected-membership MFA/session binding, and tenant-switch session rotation. The current `tenantId` field must not be treated as a permanent one-tenant-per-person model.

The optional schema field preserves controlled compatibility for non-login consumers, but the login and MFA HTTP handlers fail closed if it is absent. No membership, role, permission, subscription, entitlement or production data was changed. Test execution remains pending; commits are not a substitute for running the suites.

## 13. Delivery control

Implementation should proceed in small, reversible, independently tested changes. Each change must identify its primary file, callers, consumers, persisted schemas, tests, tenant/authority blast radius and rollback. Preserve the current integration branch and all local uncommitted work. The roadmap does not authorize production data mutation, permission elevation, deletion of evidence or bypass of independent governance gates.

**Document owner:** WILSY OS Core Engineering
**Review boundary:** Founder/Director product approval; independent security/legal review where required
**END OF WILSY OS TENANT DISCOVERY, IAM AND DASHBOARD RESOLUTION ROADMAP**
