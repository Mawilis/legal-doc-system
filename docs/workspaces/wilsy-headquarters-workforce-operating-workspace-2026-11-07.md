# WILSY OS Headquarters: internal company and workforce operating workspace

**Status:** Proposed implementation contract  
**Date:** 2026-11-07  
**Target tenant:** Existing canonical WILSY tenant only  
**Foundation:** Certified authenticated My Work vertical slice (PR #350, head `5f07d4fc152f184eea9ba09bf2296466d22666a1`)

## 1. Product decision

Build the internal WILSY OS Headquarters workspace: the authenticated daily operating environment used to run Wilsy (Pty) Ltd as the company that owns, builds, operates, sells and supports the WILSY OS product family.

This is not public customer signup, tenant genesis, a second tenant, or another customer-facing industry workspace. The canonical WILSY tenant already exists. All headquarters work must remain inside that tenant and its existing IAM, membership, entitlement, audit and source-of-truth boundaries.

The headquarters is an integrated workspace, not a dashboard presentation. Staff must be able to see assigned work, create and execute authorized tasks, manage hiring and employee lifecycle, run product delivery, resolve customer issues, review operational exceptions, submit approvals and trace decisions to authoritative records.

## 2. Two planes, one company

### WILSY company operating plane
Runs the company and workforce:
- Executive office and governance.
- People / HR and workforce lifecycle.
- Finance, billing operations, collections and procurement.
- Product management, engineering and release operations.
- Sales, partnerships and customer success.
- Customer support and service operations.
- Security, risk, privacy, compliance and institutional evidence.
- Internal IT, workplace and access lifecycle.

### WILSY OS product plane
Runs the products WILSY builds and operates:
- Canonical product catalogue and product ownership.
- Product roadmaps, releases, quality gates and incidents.
- Customer workspaces and industry capability packs.
- Product entitlements, service health and customer adoption.
- Product support, change management and release evidence.

The company plane owns employment and internal governance. The product plane owns product lifecycle and customer-facing service state. Shared identities and references do not collapse their separate authority.

## 3. Workspace information architecture

One authenticated shell with role- and capacity-filtered navigation:

1. **Headquarters / Today** — My Work, critical decisions, due/overdue assignments, escalations and source-health status.
2. **Executive Office** — company objectives, delegated decisions, governance calendar, risk and board/leadership packs.
3. **People & Workforce** — organisation structure, workforce directory, hiring, offers, onboarding, employment records, role changes, leave, performance, employee relations and offboarding.
4. **Product & Engineering** — product portfolio, roadmap, backlog, delivery milestones, code/release links, quality gates, incidents and change approvals.
5. **Customers & Success** — customer accounts, implementation, adoption, support escalations, renewals and customer commitments.
6. **Sales & Partnerships** — pipeline, proposals, partner relationships, commercial approvals and handover to delivery.
7. **Finance & Procurement** — budgets, invoices, receivables, payables, procurement requests, purchase approvals and reconciliation.
8. **Operations & Service Desk** — operational queues, service requests, incidents, runbooks and cross-functional handoffs.
9. **Security, Risk & Compliance** — access reviews, control exceptions, evidence, policy attestations, incidents and audit actions.
10. **Products & Capabilities** — catalogue, capability ownership, entitlements, industry packs, product readiness and service status.
11. **Knowledge & Documents** — controlled policies, procedures, templates, decisions and versioned company knowledge.
12. **Administration** — tenant-scoped configuration, workforce access requests, branch/location records, integrations and notification preferences.

The shell must hide inaccessible destinations or explain the exact admission requirement. It must not render fake cards or placeholder KPI values as operational truth.

## 4. Identity, employment and authorization model

Do not create a second identity system. Reuse global principals, canonical WILSY tenant membership, explicit business capacity, MFA and current-session checks.

Keep these records distinct:
- Global principal: authentication identity.
- WILSY tenant membership: admission to the existing company tenant.
- Workforce employment relationship: governed HR record linking a principal to an employee lifecycle in Wilsy (Pty) Ltd.
- Job position: approved role in the organisation structure.
- Department / reporting line: organisational assignment with effective dates.
- Business capacity: the selected operational capacity in the current session.
- Authorization role and permission: current IAM decision; never inferred from job title, department, HR status or a client-side menu.
- Product responsibility: assignment to own a product or delivery area, not blanket access to customer data.

An employee record does not itself create an authenticated principal, tenant membership, permission or session. Hiring acceptance, employee onboarding, access provisioning and role assignment are separate coordinated commands with their own approvals and audit evidence.

Workforce departure must revoke or suspend the applicable WILSY membership, role assignments, sessions, delegations, device bindings and product access according to the governed offboarding policy. HR record retention and identity access revocation are separate actions coordinated with explicit evidence.

## 5. Source-of-truth and command ownership

| Domain | Authoritative owner | Headquarters responsibility |
|---|---|---|
| Principal identity and MFA | Global identity / IAM | Request and track access; never mint identity or MFA authority |
| WILSY tenant and membership | Canonical tenant / membership registries | Display current company scope; no tenant creation |
| Employment and HR records | HR source services | Workforce lifecycle commands only through certified HR APIs |
| My Work | Source-owned Operations, Intelligence, CRM, Legal and other queues | Authorized projection and source command handoff |
| Product catalogue and entitlements | Canonical SaaS catalogue / subscription registries | Product portfolio and entitlement visibility |
| Finance | Finance / billing / payment authorities | Review, prepare and submit authorized actions; no shadow ledger |
| Procurement and inventory | Source-owned procurement / inventory capabilities | Requests, approvals and reconciliation through those sources |
| Product delivery | Product / engineering workflow services and Git provider | Link work to authoritative issue, commit, build and release evidence |
| Security and audit | IAM, audit, evidence and incident sources | Review and initiate governed remediation |
| Customer relationships | CRM and customer-success source | Customer commitments and handoffs |

Headquarters may aggregate read projections but must not become a universal write database. Every mutation is sent to the domain that owns the record, which reauthorizes the current principal, tenant, capacity, object and transition.

## 6. Daily operating loop

The landing page is task-first:
- Start with assigned work, decisions waiting on the user, due dates and escalations.
- Each card identifies source, accountable owner, priority, due date, status freshness and the next permitted action.
- Completion, approval, reassignment and escalation call the source-owned command and then refresh from that source.
- Cross-department work is represented by linked source records and explicit handoffs, not duplicated shadow tasks.
- Source outage is shown as unavailable / stale / partial with retry guidance; never as a successful empty queue.
- Metrics are shown only when returned by an authoritative source with a generated-at time and definition.
- No global transaction or globally atomic snapshot is implied across independent services.

## 7. Workforce lifecycle to make hiring real

Required end-to-end flow:
1. Approved headcount / position request with budget and accountable approver.
2. Requisition publication and candidate intake.
3. Candidate evaluation and interview feedback with restricted access.
4. Offer preparation, maker-checker approval and acceptance evidence.
5. Employment record creation by HR source.
6. Principal identity invitation or linking through canonical identity service.
7. WILSY tenant membership admission and capacity/role grants through IAM approvals.
8. Equipment, training, policy acknowledgement and first-week onboarding tasks.
9. Probation, leave, performance, employee relations and remuneration changes under HR policy.
10. Transfer, suspension, resignation or termination with explicit HR decision and coordinated access revocation.
11. Retention, evidence and audit closure.

Payroll, remuneration, employee relations, health information and identity documents require narrow purpose-based access and field-level controls. A manager must not automatically see every HR or payroll record.

## 8. Engineering rules for the integrated workspace

- Keep the existing canonical WILSY tenant. Never fall back to `MASTER`, a synthetic tenant, browser-provided tenant ID or a newly generated tenant.
- Resolve tenant scope from the authenticated session and durable membership.
- Use server-issued capability manifest for product navigation; entitlement is not permission.
- Reuse the certified My Work projection and its source isolation rules.
- Reuse the existing HR domain only after each route's actual authorization, persistence, audit and transaction contract is verified. Do not build a competing HR registry.
- No browser-side fake success, local-only mutations, hard-coded KPIs, sample staff, invented payroll or silent catch-to-empty behavior.
- No generic administrator persona, self-approval or privilege escalation through department/job-title metadata.
- Sensitive commands require maker-checker where policy demands it and append-only audit/outbox evidence in the owning transaction.
- Use optimistic revision / idempotency for retryable mutations; stale commands return explicit conflict and current readback.
- Keep internal WILSY employee access distinct from customer tenant access and from Legal Partner/practitioner authority.
- Cross-source orchestration is a saga / linked-command flow with visible partial state and reconciliation, not an invented distributed transaction.

## 9. Delivery plan

### Slice A — Headquarters shell and truthful landing page
- Authenticated route within the existing WILSY tenant.
- Reuse certified My Work as the central daily queue.
- Add headquarters navigation with server-authorized destination discovery.
- Display real source health, assigned work and decisions only.
- Add responsive desktop and mobile layouts, keyboard navigation and accessibility.
- Remove or block legacy hard-coded tenant fallbacks in the paths used by headquarters.

### Slice B — Workforce authority and HR lifecycle
- Audit the existing HR API route inventory and source services.
- Identify which read and command contracts are truly executable and certified.
- Implement missing HR source-owned commands: position/headcount approval, hiring transition, offer approval, employee admission coordination, manager assignment and offboarding.
- Enforce IAM separation and coordinated access revocation.
- Certify with real replica-set tests and authenticated browser journeys.

### Slice C — Product and engineering operations
- Connect roadmap work to authoritative GitHub issues/PRs/commits/workflow runs.
- Track product ownership, milestones, release approvals, deployment evidence and incidents.
- Do not represent GitHub state or CI state with manually typed status.

### Slice D — Customer operations
- Connect CRM, customer success, support, onboarding and renewal source queues.
- Preserve customer tenant isolation and data minimization.
- Provide explicit handoff and escalation ownership.

### Slice E — Finance, procurement and governance
- Connect existing finance/billing sources, procurement and security controls.
- Add approval packets and reconciliation views without duplicating ledgers or authorizing payment execution from a dashboard.

### Slice F — Full operating-company certification
- Founder/Executive, HR, Engineering, Customer Success, Finance, Operations and Security personas.
- Real persisted principals, memberships, capacities and roles.
- Cross-department denial tests, foreign tenant denial, stale session/revocation, maker-checker, replay, concurrency, audit atomicity and source outage behavior.
- Full authenticated browser journey across desktop and narrow viewport.
- Exact-head CI and replica-set tests green before calling the headquarters operational.

## 10. Immediate repository findings

- PR #350 provides a certified My Work foundation: exact-head authenticated browser suite 29/29, critical SYSTEM browser 4/4, My Work unit/projection and client tests, and real-replica-set HTTP tests. This is the right daily queue foundation, not a reason to rebuild it.
- The existing `HrDashboard.jsx` still declares `DEFAULT_TENANT_ID = 'MASTER'`. That fallback is not acceptable in the canonical headquarters path and must be removed or proven unreachable through an explicit safe remediation.
- The HR component header states that work-log, employee-relations, payroll-record, candidate full-update, artifact and payslip operations fail closed pending executable backend contracts. These must be treated as blocked, not marketed as live.
- The existing executive suite is broad and imports many legacy service domains. Each metric and command must be audited for authoritative source and current IAM before being used as a company-wide command centre.
- The owner commercial workspace is narrowly scoped to Legal commercial context and is not the WILSY company headquarters. Do not expand its authority by renaming it.

## 11. Acceptance criteria

- The existing WILSY tenant is used; no tenant genesis or signup route is introduced.
- The founder can enter one headquarters workspace and see a real task-first daily operating view.
- Workforce, product delivery, customer success, finance, operations and governance appear as one coherent navigation while remaining independently authorized.
- A real employee lifecycle can be initiated, approved, completed and offboarded through source-owned HR and IAM commands.
- Every action is reauthorized at its source and produces traceable audit evidence.
- No `MASTER` fallback, synthetic employee, mock KPI, browser-only success or silent empty-state fallback exists in the certified path.
- Source outages, stale data and partial access are visible and honest.
- No employee receives privileges solely because of a title, department, invitation, or HR record.
- The complete authenticated headquarters journey is green on the exact commit with real replica-set and browser evidence.

## 12. Explicit non-goals

- No new tenant, public signup, business genesis or customer ownership-verification work.
- No new identity provider or duplicate employee authentication store.
- No blanket administrator access for the founder or workforce by bypassing IAM.
- No shadow HR, finance, procurement, product, CRM or customer databases.
- No production deployment in this change.


## 13. Additional workforce API audit — quarantine before headquarters admission

A deeper inspection of the same baseline found legacy employee/HR routes that must not be connected to the headquarters:

- `tools/eos/api/employee_router.py` exposes `/api/employees/search` and `/api/employees/{employee_id}`. It resolves tenant scope from query parameter or `X-Tenant-ID`, defaults to `GLOBAL_ROOT`, and invokes the employee registry without the canonical `RequireTenantAuthorization` dependency. Its telemetry helper is logging, not authorization or durable audit evidence.
- `server/routes/hr.js` resolves tenant from query/body/header and defaults to `MASTER`. Its employee reads query legacy Mongoose model names directly. Candidate, job-opening, payroll, benefits, performance, time-off, activity, relations and artifact endpoints return successful empty responses from stub handlers.
- `client/src/services/hrService.js` explicitly converts HR read failures and open-circuit states into empty paginated datasets. This hides source outages and cannot be used for a truthful headquarters operating queue.
- The HR dashboard itself declares `DEFAULT_TENANT_ID = 'MASTER'`.

These are concrete legacy containment findings, not proof that all HR records or commands are unavailable. The canonical employee router and Express HR ledger must be removed from the headquarters request path until replaced or independently certified. Do not simply add a new header or patch the default constant: the complete route must derive tenant and principal from the authenticated current session, authorize every operation, and use the correct source-owned persistence contract.

### Required remediation gate

1. Inventory every consumer of `/api/employees/*` and `/api/hr/*`; distinguish current certified consumers from legacy UI paths.
2. Replace the legacy employee router with an authenticated EOS route using current principal, membership, capacity, HR permission and object-level checks. No query/header fallback may establish tenant scope.
3. Remove or unmount Express HR stubs from the certified headquarters path. A source outage or unimplemented domain must return an explicit unavailable/unsupported response, not HTTP 200 with an empty list.
4. Change HR read services to preserve and surface authorization, source-unavailable and malformed-response failures. Never turn them into a successful empty queue.
5. Keep the existing certified HR document route as a separate capability; it does not imply employee directory, payroll, hiring or lifecycle command certification.
6. Add real replica-set tests for cross-tenant denial, forged scope, role/capacity denial, stale session, source outage, malformed persisted records, and durable audit for each activated command.
7. Only then admit HR routes into the WILSY Headquarters navigation and workforce daily-use journey.
