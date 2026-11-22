# WILSY OS — Role-projected My Work and Governed Automation Programme

VERSION: v1.0.0-SOURCE-OWNED-OPERATING-GRAPH-ROADMAP
AUTHORITY: WILSY OS Core Governance / AGENTS.md
ARTIFACT: docs/architecture/my-work-role-graph-operating-programme.md
UPDATE DATE: 2026-11-22
STATUS: DISCOVERED AND MAPPED; IMPLEMENTATION / CERTIFICATION GATES OPEN
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
CHANGELOG: v1.0.0 establishes a source-grounded current-state inventory, permission-first target graph, migration sequence, role/ranking/automation contracts and executable production-readiness gates. No runtime or IAM authority is changed by this document.

## Decision and non-negotiables

**My Work is the principal's next authorized action, not a CRM table.** Source business registries remain canonical; the unified work graph is a **projection and routing/index layer**, not a second store of business task, approval, payroll, invoice, project or financial truth. A graph edge never grants access. A designation such as Founder never implies customer-tenant permissions. No content-title classifier may secretly retag old CRM tasks. No seeded, synthetic, stale or cached row may be presented as EOS-certified operating work. Preserve the current seven authenticated work records and existing task IDs during migration.

The signed-in capacity, tenant membership, module entitlements, seat, source-level permissions and active workforce/participation evidence govern access. WILSY's perpetual zero-rated Founder subscription is a commercial rule, not an IAM override. Paying tenant users receive the same product architecture with different exact-tenant admission.

## Source-level connection matrix (2026-11-22 branch head)

| Surface | Current observed implementation | Authority / data | Consumers / dependency | Gap and next owner |
|---|---|---|---|---|
| Unified source admission | `tools/eos/api/unified_my_work_router.py` `GET /my-work`, independently authorizes Legal, Operations, Intelligence, CRM, HR and Projects; four admitted source reads in current local trace | Current global principal, X-Tenant-ID, OptionalTenantAuthorization, module transactions | My Work, Headquarters, Daily Attention | Add accountable graph/role projection **after** independent source IAM; do not create a parallel unrestricted reader |
| Aggregation contract | `tools/eos/workspaces/service/unified_my_work_projection.py` V1; source_key, source identity, status/priority/due, is_overdue, visibility_provenance, source counts; fail-closed exact-tenant checks | Read-only, in-memory; no graph persistence | `client/src/services/unifiedMyWorkProjection.js` | No role reason, audience, source deep link authority, work-edge provenance, operating classification or role-score policy |
| Founder queue | `client/src/components/workspaces/MyWorkWorkspace.jsx` status/source/search/sort, source details, source commands | Existing authenticated projection; commands remain source-owned | HQ My Work and selected record details | UI has no Operating / Platform / Waiting on me / Waiting on others audience; no role-aware reason or outcome-first presentation |
| Daily Attention | `tools/eos/workspaces/service/attention_feed_projection.py` and `client/src/services/attentionFeedClient.js`; v1 read and six-module admission fixed in PR #418 | Same My Work admitted projection | Bell popup, filters, completion capability | Ranking and row semantics must derive from same later graph; do not regress authenticated seven-item flow |
| Project tasks | `tools/eos/api/project_attention_source.py`, `tools/eos/saas/projects/project_task_registry.py`; exact-project ACTIVE CONTRIBUTOR and current assignee checks | Projects registry and transactional participation | My Work, Projects task UI | Preserve task IDs, lifecycle CAS, no owner/Founder bypass; add reason/edge as verified **derived** participation evidence |
| Project reviews | `tools/eos/saas/projects/project_approval_registry.py`, `GET /projects/my-approvals`, `client/src/components/workspaces/ProjectApprovalInbox.jsx` | Reviewer-only pending approval; requester != reviewer; separate CAS decision | Projects reviewer inbox | Add approved read-only approval adapter to My Work; **do not** make list approval grant a financial/spending authority |
| CRM work | Owner commercial workspace source read/commands | CRM source truth, exact CRM IAM and commercial entitlement | My Work and Daily Attention | Introduce source-owned audience/category revisions; existing engineering titles are **candidates for explicit review**, not auto-classified by string heuristics |
| HR | Independent headcount/offer sources admitted only by matching HR/platform-employer permission | HR hiring evidence and authority; employee admission separately disabled | My Work HR | No inferred employee, principal, signer or HR permission; add approved HR review edges only after source contract |
| Legal | Productive work admitted by Legal source IAM | Practice/matter confidentiality and source work service | My Work Legal | No Founder backdoor to confidential matters |
| Security/System Services | Incident and responder services exist outside unified source set; system services startup has workforce scope configuration warning | System service owner, separate incident IAM | Future operating items | Add only after authorized read adapter + workforce scope configuration certified |
| Finance/Billing | Billing and financial decision registries exist, not yet admitted as My Work work producers | Billing/payables/approvals; Kennel executes money | Future payment-approval work | Separate review evidence from payment authorization/execution/settlement; source item must not imply release |
| Intelligence Dock | `client/src/components/intelligence/WilsyOSIntelligenceDock*.jsx`, separate suggestion systems | AI suggestions are advisory, not execution | AI companion | Must consume the same authorized graph identity/scores; no client-side independent entitlement claims |
| QA | `tests/unit/test_unified_my_work_projection.py`, `tests/unit/test_unified_my_work_router.py`, `tests/integration/test_unified_my_work_real_mongo.py`, attention suites, authenticated browser work suites | Test environments / exact-head evidence | CI and Founder browser acceptance | Add audience and edge regressions, real Mongo dedup and source consistency, desktop/mobile role matrix |
| Governance | `AGENTS.md` dictates one primary file per delivery, full-file version/changelog/end seal and source-first certification | Repository policy | Every workstream | Separate narrowly scoped code deliveries; avoid dirty worktree / competing prototypes |

### Current system truth vs target

- **Verified now:** 7 live source items (5 CRM, 2 Projects), authenticated API and browser list. PR #418 fixes six-source frontend/backend compatibility. A production-attachment activation task is source-persisted in Projects and visible in My Work.
- **Not verified / not yet built as canonical My Work:** cross-domain WorkItem/WorkEdge registry, source-defined audience classification, explicit founder pins, approved independent review edges inside unified feed, rule engine, cross-module governed scoring, role packs, Dock parity and complete desktop/mobile certification.
- **Never claim:** seven items are all company obligations, that a GitHub issue appears as a task without EOS creation, or that an inaccessible module contains zero work.

## Target graph and authority contract

A `WorkNode` is a **validated index** of source-owned state, not a new task ledger:

```text
WorkNode: {
  key: "MODULE:source_record_id", tenant_id, source: {module, record_id, route_id},
  title, kind: TASK|DECISION|APPROVAL|MILESTONE|RISK|COMMITMENT,
  status, priority, due_at, source_revision, source_evidence_ref,
  audience: OPERATING|PLATFORM_BUILD|UNCLASSIFIED,
  audience_classification_provenance, updated_at
}
WorkEdge: {
  key: source_key + principal/capacity/reason + source revision,
  tenant_id, source_key, principal_id, capacity_id,
  reason: ASSIGNEE|APPROVER|OWNER|ESCALATION|EXPLICIT_PIN|ROLE_QUEUE|WATCHER,
  issuer, source_permission_dependency, source_revision, created_at, revoked_at
}
```

No `WorkNode` or `WorkEdge` exists as a trusted record until its source owner and exact-tenant authority have been independently verified. In phase one prefer pure request-scoped derived edges from source-owned assignment/approval and no new persisted graph store. If persistent read-model indexing is later necessary, require versioned outbox/CDC consumers, CAS, provenance, reconciliation, shard/tenant indexes and automatic revocation on source/permission changes. Graph records never authorize commands.

**Audience semantics:** `OPERATING` means real company/tenant operation or business outcome; `PLATFORM_BUILD` means engineering/product delivery; `UNCLASSIFIED` means no source-verified classification yet. Category is controlled via source-owned audited commands or explicit governed classification evidence, not regexes or AI. Platform builds include a separate `critical_gate` only when an authorized source records a release/customer impact gate. Founder default presents Operating plus **certified critical gates**; unclassified work remains visible under All / Needs classification, not silently dropped. Do not silently downgrade an overdue item.

**Identity:** `tenant_id + source module + record id` are canonical. A display title, GitHub issue, role label, notification or AI suggestion is never identity proof. The same source item linked to multiple work areas appears once per authorized principal with explainable aggregated reasons. A pinned item must still be source-readable in current scope.

## Strict execution order: policy first, ranking second

```text
Authenticated principal and selected capacity / exact tenant
  → source entitlement, membership, seat and currentness
  → source-owned record visibility (per item + confidentiality + participation)
  → derive zero or more validated role/assignment/review edges
  → audience classification from reviewed source metadata
  → filter Operating | Platform | Waiting on me | Waiting on others | All
  → policy-admitted scoring and diversity (never a permission grant)
  → stable page/cursor and source coverage evidence
  → UI: outcome, why me, priority/deadline, one authorized action
  → source-owned command -> CAS/readback -> outbox -> reproject / notify
```

Filtering/scoring on unauthorized candidate sets is prohibited: rejected work has **no score**, not score zero. Cross-tenant absence must not expose whether an item exists. Multiple capacities require explicit session selection; do not collapse them into Founder implicit permissions.

### Role packs (admission comes from IAM, NOT the pack)

| Current verified capacity | Initial landing | Preferred reasons / types | Boundaries |
|---|---|---|---|
| WILSY Founder / Platform Owner | Operating plus certified critical platform gates | Owner, approver, explicit pin, strategic decisions/risk/commitments | No automatic cross-tenant, HR, Legal, payroll or finance grants |
| HQ Engineer | Platform build + assigned operational incidents | Assignee, escalation, milestone | Active workforce and department capacity needed |
| HQ Customer Success | Tenant-support operating queues explicitly delegated | Escalation, onboarding, response | Support scopes with audit, no customer-wide browse |
| Tenant Owner/Admin | Own tenant Operating | Owner/approver/risk | Separate subscription/seat/module entitlement and exact tenant membership |
| Tenant Employee | Own tenant assigned Operating | Assignee, approver, due | No owner/company-global visibility |
| Security reviewer | Both only when incident capacity selected | Escalation, risk, decision | Audit and segregation of duties; no universal security browse |

### V1 explainable scoring contract

After IAM and audience filters: linear score `40*due_urgency + 25*priority + 20*edge_reason + 10*role_type_fit + 5*age_boost`. Normalize each term to [0,1], except documented capped overdue contribution; clamp final score to bounded range. Priority: critical 1.0, high 0.7, normal 0.35, low 0.1. Reason values must come from installed role-pack evidence, not arbitrary browser identity. Due absent gives only bounded neutral urgency, never invented lateness. Sort by score desc, due_at asc with null last, source_key asc; tie-break deterministic. Return `ranking_explanation` computed from non-sensitive source-provided facts.

Apply a **soft** per-module cap only within the first display window (e.g. 4 of 12), then backfill from suppressed candidates to preserve access to all due items. A hard cap on all results would hide real work and is prohibited. Show actual total counts from admitted sources, not diversified subset count. Same scorer for My Work, Daily Attention and Dock; Dock may suggest actions but cannot invent an approval or completion.

### Decision/approval lifecycle

- A request for independent review is a business decision workflow, not task completion or spending authorization. Preserve requester != sole reviewer and exact current contributor approval IAM.
- Distinguish `PENDING_REVIEW` / `APPROVED` / `REJECTED` and underlying task `OPEN` / `IN_PROGRESS` / `BLOCKED` / `DONE` / `CANCELLED`. Approval decision must not magically mark task DONE.
- My Work reviewer edges must come from the current `/projects/my-approvals` source read or an equivalent source-owned exact-scope service, including version and pending-status readback.
- The Projects Approvals picker must paginate active eligible independent contributors, explain verified zero and distinguish unavailable read; reviewer admission remains source-owned, self-review denied.
- Evidence-bound review requires the exact original version, scanned, independently cleared attachment and source audit; AWS production quarantine remains funding-gated separately.

## Production implementation roadmap and acceptance gates

| Stage | Primary delivery, one file at a time | Definition of done | Required tests / blocker |
|---|---|---|---|
| **P0-A: Operating taxonomy** | Source-owner reviewed audience fields / immutable revision contract; migrate legacy CRM product backlog only by explicit reviewed classification; mark unknown `UNCLASSIFIED` | Founder default shows real Operating work and certified critical gates; current seven items remain accessible from All; no title-based automatic reclassification | Source schema, CAS + idempotent classification, exact-tenant owner privileges, 7-item replay and rollback |
| **P0-B: Projection parity** | One EOS graph projection with reason + audience provenance and source coverage; then separately adapt client validator, My Work, Daily Attention and HQ | Operating/Platform/All + honest unclassified and missing-source messages; exact task counts unchanged; same source_key | Python unit + real Mongo + exact-scope HTTP + client 100% focused tests + desktop/mobile |
| **P0-C: Review intake** | Adapt `/projects/my-approvals` to read-only My Work review edges without duplicating approval DB | Reviewer pending item appears once and links to source approval; cannot self-approve; approval decision refreshes queues | Tenant/participant read, foreign denial, revision conflict, self-review, browser reviewer flows |
| **P1-A: Derived work graph** | Versioned `WorkNode/WorkEdge` representation derived only from source-approved snapshots; no new business ledger | Assignee, owner, approver, escalation, pin reasons display, source revoke removes edge, no phantom tasks | Deterministic multi-source graph tests, 500+ paging, race/revocation, dedup, failure isolation |
| **P1-B: Roles and scoring** | Verified role-pack config + Python scorer + cursor; then same source to Dock | Distinct Founder/HQ/Tenant/Security queues, explainable scores, fair source diversity, stable pagination | Cross-tenant/seat/capacity denial matrix, ordering snapshots, no unauthorized scoring |
| **P1-C: Source work actions** | Per-source open/complete/edit/reassign/review command adaptors, no generic omnipotent work POST | One primary action per work row and optimistic UI forbidden until durable source readback; direct source route never bypassed | CAS, idempotency, audit, revocation/replay tests, stale session and denied commands |
| **P2: Automation v1** | Governed rule registry and event-derived routing engine with unique event identity | Trigger→condition→authorized WorkEdge creation/notification; five defined rules; no duplicate execution | replay, majority commit, concurrency, dead-letter, loop prevention, invalid permission |
| **P2: Intelligence Dock parity** | Dock advisory suggestions consume same admitted graph and scorer; explicit action handoff to source | Same identity/priority/reason and module authority across surfaces; no generated approvals | Cross-surface E2E consistency, deny and currentness verification |
| **P3: Enterprise scope** | Finance, Security, Legal, HR, tenant packs, mobile/edge ingestion separately admitted | Paying tenant organization work remains isolated; platform support strictly audited; no universal HQ cross-tenant list | role/device/accessibility/load/HA/perf and tenancy boundary certificates |
| **P4: Operations** | Telemetry, alerting, recovery, migration support, adoption analytics | No 503 retry storm; usable queue under load; clear stale/unavailable evidence without asserting zero | SLOs, chaos, privacy audits, rollback drills, security reviews |

### The first executable P0 decisions

1. Approve an explicit **Operating / Platform build / Unclassified** source-authoritative taxonomy and the semantic distinction between business outcomes, engineering build tasks and critical release gates.
2. Preserve existing CRM tasks. Review classification of `Expand the CRM Entry Form`, `Task Creation Flow` and `My Work — What needs your attention` as candidate Platform work; **never** mutate based on title without source-authorized explicit update.
3. Confirm `Meet Investors` and `Mission and Strategy` as potential Operating commitments only after source-owner confirmation. Source-prove time/calendar linkage rather than treating a title as an appointment.
4. Keep `Activate WILSY OS production attachments` as one Projects-controlled funded deployment task; distinguish funding blocked from blocked execution. No CloudFormation deployment before budget approval.
5. Use the existing Projects approval registry to prove the first **independent approver** queue edge. The empty contributor picker is a separate intake UX/participation issue, not license for self-approval.
6. Do not seed artificial company outcomes or duplicate CEO tasks. New founder commitments must be created by real authorized EOS commands, with exact readback and audit.

### Automated production-readiness gate (required, NOT completed by this document)

- [ ] **Source control:** clean branch, one-primary-file delivery, AGENTS.md sovereign header/version/changelog/end seal, review/CI required, no unrelated migration or skipped tests.
- [ ] **Python:** `python -m py_compile`, Pyright, direct projection/IAM/scoring tests, API contract and 500+ page cursor tests, deterministic dependency/revision races.
- [ ] **Persistence:** isolated Mongo replica-set integration for dedup, CAS, outbox and cross-source consistency; persistent production collections are never test targets.
- [ ] **Client:** full relevant Vitest suite, production Vite build, accessibility/keyboard/contrast, verified zero vs unavailable vs unclassified, responsive 390px / 1440px.
- [ ] **Authenticated journey:** Founder, HQ employee, tenant owner/employee, approver and denied cross-tenant subject; confirm operating default and source-specific single-step action with persisted readback.
- [ ] **Security:** least IAM; module subscription and seat; same-tenant/role filtering before scoring; confidential Legal/HR and financial action denial; no blanket Founder `work.*`, no cross-tenant existence disclosure.
- [ ] **Automation:** same event same fingerprint → replay, conflicting key → reject; rule action under evaluated service and target principal, source revoke updates graph; no external sends/money/deletions without independently approved source commands.
- [ ] **Observability:** source and policy admission/denial counters, bounded spans without PII, explicit fail-closed 503 presentation and backoff, no cache presented as current, accepted head SHA logged in certificate.
- [ ] **Performance:** 500/5,000/50,000-item safe bounded-load profiles with recorded latency, no serial per-item IAM/N+1 loops, capped page, verified stale cursor and denial tests; establish SLOs from measurements, not guessed targets.
- [ ] **Operations:** reversible schema expansion, dual-read parity, guarded backfill with audited owner approval, cutover/rollback, backup/restore, feature flag off by default, no loss of the current seven tasks.
- [ ] **Financial/AWS:** no spending authority or AWS attachment activation inferred from approval, funding gate separately controlled by Projects deployment task and PR #416.
- [ ] **Release:** cannot mark complete until source runtime + sovereign file-contract pass, real Mongo and authenticated browser certificates green, explicit owner acceptance, PR merged and new exact head certified.

## Competitive research translated into measurable product work

These are externally documented features, **not claims that WILSY already exceeds them**:

- Microsoft Planner aggregates assigned work from multiple Microsoft surfaces and offers My Day. WILSY must prove multi-module operating intake with tenant/role permissions, not merely create a different task-list skin. https://support.microsoft.com/en-us/planner/training/manage-your-tasks-with-my-tasks-and-my-day
- Linear My Issues orders urgent, SLA, blockers, cycle and triage work by focus; its initiatives provide leadership views. WILSY should demonstrate measurable outcome/reason explanations and source-owned business decisions. https://linear.app/docs/my-issues and https://linear.app/docs/initiatives
- Asana My Tasks rules automate triage and multi-homing keeps one task shared across projects. WILSY differentiator can be source-owned cross-domain Work identity and stricter runtime action permission checks, but needs real certification. https://help.asana.com/s/article/rules-in-my-tasks?language=en_US and https://help.asana.com/s/article/how-to-multi-home-tasks?language=en_US

## Delivery and change-control policy

Operate in order **DISCOVER → MAP → WIRE → CLEAN → CERTIFY → OBSERVE → INTELLIGENCE → EVOLVE**. Keep this architecture document as the stable programme anchor. Every behavioral change is its own bounded, reviewed file delivery with exact source owner and a test certificate; do not open dozens of overlapping feature branches, override existing source task registries or claim browser completion from source-only tests.

**Current certificate:** only the previous Daily Attention bugfix's focused Python tests and authenticated browser visuals have been observed. All roadmap implementation phases above remain unimplemented or not fully verified until separately evidenced.

---
ARTIFACT: docs/architecture/my-work-role-graph-operating-programme.md
VERSION: v1.0.0-SOURCE-OWNED-OPERATING-GRAPH-ROADMAP
TENANT POSTURE: exact-current-tenant policy, authorization before ranking, no Founder bypass.
AUTHORITY BOUNDARY: architecture and delivery acceptance only; grants, approval and source commands remain EOS owned.
FAIL-CLOSED POSTURE: unknown sources/classifications are not silently treated as authorized or verified empty.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
END OF WILSY OS SOVEREIGN ARTIFACT
