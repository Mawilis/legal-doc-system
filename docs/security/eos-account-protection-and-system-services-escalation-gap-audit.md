# EOS Account Protection and System Services Escalation — Gap Audit

**Status:** ENGINEERING GAP AUDIT — NOT A SECURITY CERTIFICATION  
**Scope:** PR #342 branch `eos/tenant-discovery-iam-dashboard-roadmap`  
**Reviewed head:** `0c10b635f4e2053b0f06fae35046853cbd1fd768`  
**Decision:** Continue implementation in development only. No production activation, credential reset authority, account unlock authority, or staff permission grant is implied.

## 1. Existing controls verified in source

The current branch contains:

- A closed System Services agent workflow allowlist and explicit human-escalation reasons.
- A forbidden-material field-name list covering passwords, OTPs, recovery tokens/capabilities, MFA seeds/secrets, private keys, session tokens and refresh tokens.
- A support-case domain with tenant/system scope separation, a constrained status machine, immutable transition values and revision tracking.
- A support-case registry with append-only events, idempotency uniqueness, revision-guarded transitions, and caller-owned Mongo transactions.
- A tenant self-service application-service surface bound to the authenticated principal and exact tenant, including case creation, own-case listing and own-case history.
- A SYSTEM queue application-service surface guarded by current SYSTEM permission possession and active platform-workforce relationship evidence in the same transaction.
- A router that derives the actor from the verified EOS identity, ignores request-supplied actor/tenant authority, and fails closed when runtime dependencies or storage readiness are absent.
- Disposable replica-set tests for case creation, transition, transaction abort, stale revision, replay, tenant isolation and startup index readiness.

These are source-level findings. They do not establish deployed configuration, live incident response readiness, or production authorization.

## 2. Material integration gaps

### 2.1 Tenant self-service is not exposed by the inspected router

The application service implements `create_own_case`, `list_own_cases` and `read_own_case_history`, but the inspected `tools/eos/api/system_services_router.py` exposes only SYSTEM workspace/queue, SYSTEM case history and SYSTEM transition routes.

Consequences:
- A tenant user cannot reach the implemented self-service case workflow through these inspected HTTP routes.
- The agent allowlist names `SUPPORT_CASE_CREATE` and `OWN_CASE_STATUS`, but no corresponding tenant-facing route was found in this router.
- Account-protection escalation therefore has a domain/service foundation but is not yet a complete authenticated user journey.

Required closure:
- Add authenticated tenant-scoped create/list/status/history routes.
- Derive principal and tenant exclusively from canonical authenticated EOS context; never accept either from body, query or headers as authority.
- Revalidate current tenant membership and exact operation permission in the same caller-owned transaction as each read/write.
- Enforce principal ownership for case status/history; tenant scope alone must not expose another member's account case.
- Add route-level negative tests for forged tenant/principal, cross-tenant, cross-principal, unauthenticated, stale membership, unavailable IAM and replay.

### 2.2 Security incident intake and response are not yet a distinct governed workflow

The case domain includes `SUSPECTED_COMPROMISE` and `ESCALATED_SECURITY_INCIDENT`, and the agent policy requires human escalation for suspected compromise. The inspected router does not expose a tenant incident-intake route, and the generic case lifecycle does not itself define incident evidence, containment decisions, incident ownership, notification delivery or independent closure approval.

Required closure:
- Provide a narrowly scoped suspected-compromise intake path that creates durable, sanitized evidence and escalates without waiting for an ordinary support queue action.
- Keep incident facts append-only and separately attributable: source event/reference, observation time, reporter principal, affected principal/account reference, severity, correlation fingerprint, evidence provenance and disposition history. Do not store credentials, OTPs, recovery secrets or raw authentication tokens.
- Define explicit incident states and authorized transitions, including triage, containment recommendation, containment execution evidence, recovery review and closure.
- Treat containment actions (for example session revocation) as separate canonical EOS operations requiring their own current permission, target binding, approval policy and audit evidence. A support-case status must never execute them.
- Require independent review for privileged accounts, suspected compromise, repeated recovery failures and any identity-proofing exception.
- Preserve emergency deny/revoke capability only through its separately governed authority; support agents and the AI agent cannot self-authorize it.

### 2.3 Human escalation is policy metadata, not a staffed operational process

The agent policy identifies escalation reasons but the inspected implementation does not establish routing ownership, duty coverage, acknowledgement deadlines, escalation timers, secure evidence handoff, conflict-of-interest checks or a governed decision record.

Required closure:
- Define an attributable escalation assignment/acceptance record with current workforce scope, assigned responder, reason, evidence references, timestamps, SLA clocks and reassignment history.
- Require a responder to possess the exact current SYSTEM permission and active PLATFORM workforce relationship at every sensitive read/write.
- Prevent self-approval and requester/target conflicts; separate identity proofing, approval and execution where policy requires.
- Record unavailable/out-of-hours escalation as an explicit fail-closed state with safe user guidance, not an implied approval or silent queue success.
- Keep human escalation as a fallback after self-service is unavailable or policy requires it; do not make staff the default route for ordinary password recovery.

### 2.4 Agent policy does not implement account operations

The agent module is an allowlist and secret-field-name guard. It is not an identity verifier, recovery engine, incident detector, session authority, notification service or IAM adapter.

Required closure:
- Keep the agent limited to help content, initiating approved self-service workflows, reading the authenticated user's own non-secret status, and preparing a sanitized escalation.
- All password reset, recovery-contact verification, MFA enrollment/recovery, session revocation and device trust changes must execute through their canonical EOS services and proof requirements.
- Never expose secret values to the agent or persist them in support cases, event payloads, telemetry or prompts.
- Escalate when proof fails, verified factors are unavailable, the account is privileged, compromise is suspected, dependencies are unavailable or policy requires approval.
- Ensure agent outputs cannot mark identity verified, approve a recovery, execute an account action or grant a permission.

## 3. Required end-to-end certification

The next development tranche must add and certify:

1. Authenticated tenant routes for self-service case create/list/status/history.
2. Dedicated suspected-compromise intake and append-only incident evidence.
3. Explicit SYSTEM incident queue permissions, responder assignment/acceptance and conflict-of-interest checks.
4. Exact permission checks and current workforce checks at point of every sensitive read/write.
5. Independent approval and execution boundaries for session revocation, recovery and other account-protection actions.
6. Atomic case/incident state, immutable event and audit/outbox persistence in caller-owned replica-set transactions.
7. Replay, duplicate delivery, unknown commit, concurrent transition, stale revision, transaction abort and recovery/reconciliation tests.
8. Authenticated HTTP tests for tenant/principal spoofing, cross-tenant isolation, privilege escalation, denied SYSTEM actors, stale workforce/permission evidence, and unavailable dependencies.
9. A full browser journey from failed self-service through escalation, responder acknowledgement, governed action, user confirmation and closure.
10. Exact-commit CI evidence before any release or deployment consideration.

## 4. Explicitly prohibited shortcuts

- No password-only MFA reset for MFA-enabled accounts.
- No support-case status or agent decision may grant identity, IAM, tenant, Legal, financial or platform authority.
- No staff permission may be self-assigned or inferred from a job title, GitHub role, case assignment or UI capability.
- No request-supplied tenant/principal/permission/workforce scope is authoritative.
- No credential, OTP, recovery token, MFA secret, session token or private key may enter support-case or incident persistence.
- No production credential changes, account operations, workforce assignments, subscription lifecycle changes or deployment are authorized by this audit.

## 5. Exit decision

**Current result: PARTIALLY IMPLEMENTED; NOT READY FOR OPERATIONAL CERTIFICATION.**

The foundation is appropriately deny-first, but the missing tenant-facing routes and distinct incident/escalation operating controls are material. Close those gaps in the PR branch, then require authenticated route-level and real replica-set transaction certification on one exact commit. Keep PR #342 open and unmerged until its independent release gates are satisfied.


## 6. Development implementation update (2026-11-05)

The following foundations have since been committed to this branch:

- Authenticated tenant self-service case create/list/status/history routes. The actor comes from EOS authentication; the tenant header is only a selector. ACTIVE principal and exact ACTIVE membership are re-resolved inside the same caller-owned Mongo transaction as each case operation.
- Tenant + principal + idempotency-key scoping for self-service case creation.
- A distinct structured security-incident intake domain and append-only registry. It accepts bounded categories and an aware observation timestamp, not free-form narrative or secret-bearing fields.
- Tenant-owned incident intake/list routes, with durable incident and initial event inserted in one caller-owned transaction.
- A bounded SYSTEM incident queue read route guarded by current `system_services:queue:read`.
- A responder assignment and acceptance/decline foundation. Assignment requires current `system_services:case:triage` for the assigning staff principal and current `system_services:incident:escalate` for the proposed responder, each checked through the EOS System Services authorizer in the same transaction. The assignment rejects reporter/assigner/responder conflicts, supports one assignment per incident, records immutable events, and uses revision-guarded acceptance/decline. Only the assigned responder can accept or decline.
- Startup provisioning and readiness flags for incident and assignment registries, independent of whether SYSTEM workforce authority is configured. Missing staff authority keeps staff operations unavailable without disabling the tenant's case storage.
- Real-replica-set tests for tenant spoofing, cross-principal case privacy, forged request fields, incident replay, incident record/event rollback, assignment replay, permission separation and responder-only acceptance. Startup certification checks the new unique indexes.

These are implementation claims, not test-pass claims. The exact-head System Services certification workflow must complete successfully before this work is described as certified.

### Remaining before operational certification

1. Replace the assignment service test double with real Mongo-backed `SystemServicesEosAuthorizer` coverage proving both exact permission assignments and current PLATFORM workforce relationships for assigner and responder.
2. Add governed re-assignment, duty routing, acknowledgement deadlines, out-of-hours handling and conflict/recusal history.
3. Integrate the independent audit/outbox contract atomically with incident, assignment and event writes; the current event collections are not a substitute for the platform audit/outbox.
4. Define independent approval and canonical execution for containment/recovery. Assignment acceptance does not authorize session revocation, MFA reset, password reset, unlock, recovery-contact changes or device trust changes.
5. Add full authenticated browser journey, negative route tests for every staff operation, concurrency/unknown-commit/reconciliation coverage and exact-head CI.
6. Review privacy retention, POPIA purpose limitation, user notification and incident closure policy before operational activation.

No production deployment, credential/account mutation, self-assigned permission, subscription lifecycle action, merge or Electrum activation is authorized by this implementation update.


### Additional responder workflow increment

- Added a principal-bound responder inbox and exact assignment-detail read. Both require the responder's current `system_services:incident:escalate` permission; detail reads also verify the assignment's tenant and reporter bindings against the incident record.
- Added real-replica-set EOS authorizer tests for exact `system_services:case:triage` and `system_services:incident:escalate` assignments plus active PLATFORM workforce relationships.
- Added an authenticated HTTP integration journey using the real EOS System Services authorizer: independently authorized triage actor assigns, the separately authorized responder reads their inbox/detail, and that responder accepts under a revision guard.
- Fixed self-service support-case idempotency so the persisted event key is scoped to tenant + principal + caller idempotency key, matching the unique event index and preventing cross-tenant collisions.

The System Services exact-head CI run is queued/pending at the time of this update. These tests are authored but not yet reported as passing.


### Transactional platform audit/outbox implementation increment (2026-11-05)

- Added separate `system_platform_audit_events` and `system_platform_audit_outbox` collections for responder assignment and acknowledgement/decline events. These are distinct from the System Services assignment event history.
- Assignment and transition services now write the business projection, immutable assignment event, platform audit record and pending outbox intent through the same caller-owned MongoDB session. No nested transaction or background dispatch is introduced.
- Audit/outbox event identity is deterministic and idempotent. Duplicate delivery is accepted only when the stored evidence exactly matches; a conflicting event fails closed.
- Audit evidence is derived from the immutable persisted assignment event, including its original timestamp, so a command replay does not fabricate a new audit time.
- Startup index provisioning now includes unique audit/outbox event keys and a bounded pending-outbox scan index. Failure to provision these indexes prevents assignment registry readiness.
- Added real-replica-set assertions that assignment and acceptance each produce independent audit/outbox records, plus a transaction-abort test proving assignment, assignment event, audit record and outbox intent all roll back together.

**Certification status:** implementation committed; exact-head CI is pending. This does not certify delivery/dispatch, alert notification, browser workflow, duty-rota/SLA coverage, or any containment/recovery operation. The outbox remains pending and no worker is activated by this change.

### Remaining before operational certification (revised)

1. Complete exact-head Python compilation, Pyright, unit and real-replica-set certification for the audit/outbox integration; fix any failures before treating it as certified.
2. Add governed duty routing, acknowledgement deadlines, escalation timers, out-of-hours fallback, reassignment and conflict/recusal history. Do not invent a staffed rota; missing or stale rota data must fail closed into an explicit unstaffed state.
3. Build and certify the authenticated browser journey from incident intake through responder acknowledgement and user-visible status/closure.
4. Define independent approval and canonical execution for containment/recovery. Audit/outbox persistence and responder acceptance do not authorize session revocation, MFA reset, password reset, unlock, recovery-contact changes or device trust changes.
5. Add outbox consumer delivery/retry/dead-letter/reconciliation policy only after the delivery owner and operational notification contract are defined. The current implementation creates durable pending intents only.
6. Review privacy retention, POPIA purpose limitation, user notification and incident closure policy before operational activation.

No production deployment, credential/account mutation, workforce assignment, subscription lifecycle action, merge or Electrum activation is authorized by this implementation update.

### Duty coverage and acknowledgement policy foundation (2026-11-05)

- Added a pure, immutable duty-policy resolver that accepts only an explicitly supplied roster snapshot and an approved acknowledgement interval.
- Exactly one active duty entry resolves to `ROUTED`; an existing schedule with no active entry resolves to `OUT_OF_HOURS`; an absent rota resolves to `UNSTAFFED`. Neither uncovered state invents a responder.
- Overlapping active entries fail closed instead of selecting an arbitrary staff member. All timestamps must be timezone-aware, and acknowledgement intervals are explicitly bounded.
- The resolver returns a deterministic acknowledgement deadline and next scheduled coverage time when available. It does not assign staff, send notifications, execute escalation timers or grant permissions.
- Added unit coverage for routed, out-of-hours, unstaffed, overlap-conflict and invalid-time/SLA cases. The dedicated System Services workflow now includes this module and test in compilation, Pyright and pytest gates.

**Operational limitation:** no trusted duty roster, acknowledgement SLA approval, notification channel, after-hours fallback owner or dispatch worker has been configured. This is a tested policy foundation only; it is not a live on-call process.

### Exact-head certification result (2026-11-05)

- Latest System Services workflow #578 on commit `80a4132545e5b50638ada874bce78f96da2d1ca3`: **success** — https://github.com/Mawilis/legal-doc-system/actions/runs/42004272573
- Python compilation: passed.
- Pyright: passed.
- Unit and real MongoDB replica-set certification: **61 passed, 0 failed**.
- `git diff --check` and clean-checkout verification: passed.
- The 61 tests include the independent platform audit/outbox rollback proof and the five duty-policy cases.

This certifies the code-level audit/outbox and duty-policy foundations on the tested commit. It does not certify a live duty roster, dispatch/notification delivery, a browser journey, or containment/recovery authority.

### Incident-intake audit/outbox extension (2026-11-05)

- Extended the same independent platform audit/outbox contract to tenant security-incident intake. The incident record, immutable `INCIDENT_REPORTED` event, platform audit event and pending outbox intent now share the same caller-owned MongoDB transaction.
- Idempotent intake replay verifies the original immutable event timestamp and does not create duplicate audit/outbox rows.
- Added real-replica-set assertions for intake audit/outbox persistence and transaction rollback across all four records.
- Exact-head System Services workflow #582 on commit `8b5277b19010ad5e402a31ae80f3caf1b2534a3b`: **success** — https://github.com/Mawilis/legal-doc-system/actions/runs/42004725693
- Compilation, Pyright, unit and real MongoDB replica-set tests passed: **61 passed, 0 failed**. Patch whitespace and clean-checkout checks passed.

The audit/outbox foundation now covers incident intake, responder assignment and responder acknowledgement/decline. Outbox delivery remains intentionally unimplemented/unactivated pending a defined notification owner, privacy-safe payload contract, retry/dead-letter policy and operational approval.

### Browser and containment/recovery integration audit (2026-11-05)

- The documentation-only exact-head rerun, System Services workflow #583 on `4c274a1cf510161800d984ed7cf289df87c65748`, completed successfully: https://github.com/Mawilis/legal-doc-system/actions/runs/42004970281. Mongo replica-set startup, compilation, Pyright, the unit/real-Mongo certificate, whitespace and clean-checkout steps all passed. This rerun does not change the previously recorded 61-test code result.
- The current React `SystemServicesDashboard` is still a projection-only surface. It renders the verified workspace summary and support cases, but does not yet render the security-incident queue, the principal-bound responder inbox/detail, or accept/decline controls. Those authenticated EOS routes already exist; the UI journey is therefore an integration gap, not a reason to create a second authorization path.
- The controller opens this dashboard only after the authenticated global-command action requests `/system-services/workspace-bootstrap` and validates the EOS projection. The existing browser-cert runner is a separate authenticated Legal workspace harness; it does not currently seed a governed SYSTEM workforce principal and assignment. A real System Services browser certificate must add that fixture deliberately, with independently seeded exact SYSTEM permissions and active PLATFORM workforce evidence, rather than simulate staff authority in browser state.
- Canonical recovery remains in the existing EOS authentication router and its recovery services. The global-principal session authority exposes exact principal + tenant + session-reference revocation inside a caller-owned transaction, including associated refresh credentials. No System Services incident approval/execution route currently binds a reviewer decision to that canonical revocation operation.
- Consequently, do not add a parallel password/MFA/session mutation service under System Services. The next safe implementation step is to define a separate, attributable containment/recovery decision record with independent approver and target binding, then compose it with the canonical EOS session authority only after the required permission and approval policy are proven. Password reset, MFA recovery, recovery-contact verification, account unlock and device-trust operations remain with their existing canonical services and proof requirements.
- No real duty roster, approved acknowledgement SLA, notification owner, or after-hours fallback has been supplied. The resolver remains non-operational; no timer or dispatch worker is activated. The platform audit outbox remains pending-only.

**Current decision:** continue development with the authenticated incident/responder browser surface and a separately governed containment-decision contract. Do not treat #583 as browser, operational-duty, containment/recovery, notification-delivery or production certification. PR #342 remains open and unmerged; no deployment or production mutation is authorized.


### Authenticated System Services browser integration increment (2026-11-05)

- The React System Services workspace now consumes the existing EOS security-incident queue and principal-bound responder inbox/detail routes. Responder accept/decline calls use the server-projected assignment revision and an idempotency key; the UI never treats local state as authority.
- The authenticated workspace bootstrap now projects `system_services:incident:escalate` only after the EOS authorizer confirms the exact permission. The responder inbox and controls render only when that exact capability is present.
- The UI explicitly states that acknowledgement/decline is not containment or account mutation.
- Added component tests for exact capability gating, queue and inbox projection, assignment detail/decision callbacks, and missing metrics. Exact-head System Services workflow #42007610523 on `eaced413b18d6c75aff425c39e22b2a0019aa52f` passed: Python compilation, Pyright (0 errors), component tests (6 passed), real MongoDB replica-set tests (61 passed), and clean-checkout checks — https://github.com/Mawilis/legal-doc-system/actions/runs/42007610523.
- Added a disposable authenticated browser fixture with distinct synthetic triage and responder principals, explicit SYSTEM permission assignments, and active PLATFORM workforce relationship evidence. It seeds a synthetic tenant-reported incident and assigns it through the same EOS escalation service. Browser coverage exercises queue, inbox, detail, acceptance and the triage-only responder-inbox denial.
- The full Playwright + real-Mongo browser run #42007610319 is in progress at the time of this update — https://github.com/Mawilis/legal-doc-system/actions/runs/42007610319. Do not treat the browser journey as certified until this exact-head run completes successfully.

### Containment and recovery execution boundary (reaffirmed)

- The canonical `GlobalPrincipalSessionAuthority.revoke_session` operation is the only session-revocation execution authority identified. It revokes one exact principal + tenant + session reference and associated refresh credentials inside a caller-owned transaction.
- The inspected current authenticated System Services HTTP identity path does not yet establish a verified global-principal session reference for the target. Therefore the browser/UI increment deliberately does not add a session-revocation endpoint or infer a target session from browser, tenant or legacy session metadata.
- Next safe containment increment is an immutable decision record bound to incident, target principal, exact canonical session reference, requesting principal, independent approving principal, decision evidence, and revision. Requester and approver must be distinct and neither may be the target. Execution must revalidate current permission/workforce evidence and invoke the existing canonical session authority in the same transaction as the decision event and independent platform audit/outbox record.
- Password reset, MFA recovery, recovery-contact verification and account unlock remain with their existing canonical EOS proof and recovery services; this decision record must not reproduce those operations or accept their secrets.
- No production session revocation, password/MFA mutation, device-trust change, duty-rota operation, notification delivery or outbox dispatch is enabled by this increment.


## Independent containment and recovery decision record

The System Services response-governance foundation now defines a separate decision
record and caller-transaction-owned registry:

- `SecurityIncidentResponseDecision` binds the incident, tenant, exact target
  principal, proposed action, requesting responder, request evidence, and
  independent decision-maker evidence.
- The requester cannot approve or reject their own request.
- Decisions are revision guarded and terminal at revision 1 (`APPROVED` or
  `REJECTED`); stale or second decisions fail closed.
- The registry persists the decision projection, immutable request/decision
  events, independent platform audit evidence, and a PENDING outbox intent in
  the same caller-owned transaction. It does not dispatch notifications.
- Permission-revocation decisions must identify the exact existing assignment
  and permission. This preserves the lineage required by
  `SystemPermissionRevocationCommandService`; the decision registry does not
  revoke anything itself.
- Password-reset approval does not mint or replace a recovery capability.
  Execution must still traverse the canonical
  `PasswordResetService.reset_password` path, which validates and consumes a
  durable single-use recovery capability and atomically updates credentials,
  revokes sessions and refresh tokens, and persists its notification intent.

The decision domain and real-replica-set registry tests are included in the
System Services certification workflow. This is a governance evidence layer,
not yet an authenticated decision route or an execution adapter. Before route
activation, EOS still needs an independently issued decision permission,
current platform workforce evidence for the approver, a governed approver
assignment source, and a route-level test proving separation of requester,
approver, and canonical action executor. No new permission is self-issued here.

### Explicitly disabled

- No containment or recovery action is executed by incident intake, assignment,
  responder acceptance, or the decision registry.
- No password-reset bypass, custom session revocation, principal suspension,
  or parallel permission-revocation implementation is introduced.
- No notification delivery, duty routing, or outbox dispatcher is enabled.
- The outbox remains durable PENDING intent only.

## Authenticated browser workspace increment

The System Services dashboard now consumes the authenticated EOS incident queue
and responder inbox projections. It supports exact assignment detail and
revision-guarded accept/decline requests through the existing EOS routes. The
responder confirmation explicitly states that acceptance performs no
containment or account action.

The browser certification fixture independently seeds synthetic SYSTEM
principals with exact SYSTEM permission assignments and active PLATFORM
workforce relationships. Its preflight checks that the authorized responder
can read their inbox and that a queue-only principal receives 403 from the
responder inbox. The Playwright journey covers queue visibility, exact
assignment detail, responder acceptance, and absence of containment side
effects. This remains disposable development certification only.
