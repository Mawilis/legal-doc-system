# WILSY OS — System Services Department and IAM Command Center

Version: v1.0.0-SYSTEM-SERVICES-IAM-FOUNDATION
Date: 2026-11-03
Status: Architecture contract and implementation backlog; no production service-desk API or new IAM grant is claimed by this document.
Repository: Mawilis/legal-doc-system
Branch: eos/tenant-discovery-iam-dashboard-roadmap
Related integration: PR #342

## 1. Product decision

Create one platform-owned **WILSY OS System Services Department**. It is the accountable service owner for platform identity support, account recovery operations, access-request routing, IAM administration, incident handling and service health.

It is not a new authentication authority and it is not a universal administrator account. **Python EOS remains the policy enforcement point and source of truth**. The dashboard is an operational interface; every read and command must be independently authorized by EOS against current principal, current SYSTEM or tenant scope, exact permission possession, target sensitivity, workforce currentness, and current evidence.

The System Services Department is operated by WILSY OS. It is not delegated to each customer tenant by default. Tenant administrators receive only separately defined own-tenant support powers. A platform support operator cannot gain tenant Legal, finance, or business-role authority by handling an account ticket.

## 2. User-facing surfaces

1. **My Account / Self-Service** — password recovery request, verified recovery-contact maintenance, MFA recovery guidance, active-session review/revocation where supported, sign-in history, and support ticket creation. It never exposes recovery tokens or lets a browser assert verified state.
2. **System Services Console** — platform support queue, ticket triage, identity lookup by opaque principal/case reference, account-security posture, recovery workflow status, device/session evidence, incident escalation and immutable audit timeline.
3. **IAM Administration** — role and permission catalogue, current assignments, scope, grantor, expiry, approval evidence, access requests, periodic access review, revocation and policy-denial explanation.
4. **Service Health** — authentication/recovery delivery health, Mongo persistence health, queue latency, throttling/lockout metrics, device provenance and audit-ingestion status. Operational metrics must be sourced; no hardcoded/demo counters.

The current WilsyAccountCommandCenter remains the user's account and self-service entry point. The new System Services Console is a separate staff workspace. Do not duplicate the user's security panel or imply that an account settings panel is an internal help desk.

## 3. Role and permission model (IAM-owned)

The dashboard must not authorize from a React role string, route, local storage, JWT display claim, or hidden navigation item. EOS must issue a bounded workspace projection only after it verifies current authority. The client uses that projection to decide which panels to render; EOS independently checks every API request.

Proposed permission vocabulary (design identifiers; **not active grants**):

| Permission | Scope | Intended capability |
|---|---|---|
| system_services:queue:read | SYSTEM | Read sanitized platform support queue and case metadata |
| system_services:case:triage | SYSTEM | Assign/route a case within permitted queue partitions |
| system_services:identity:read | SYSTEM | Read minimum identity/security posture for a case-bound principal |
| system_services:recovery:request | SYSTEM | Initiate a governed recovery workflow; never set a password directly |
| system_services:session:revoke | SYSTEM | Revoke a case-bound session/device only under exact current evidence and policy |
| system_services:incident:escalate | SYSTEM | Escalate a suspected compromise to the security incident workflow |
| iam:access_request:read | SYSTEM | Read access requests and their evidence |
| iam:access_request:decide | SYSTEM | Approve/reject a bounded request where policy allows; approval does not itself create possession |
| iam:role_assignment:read | SYSTEM or TENANT | Read assignments only within the granted scope |
| iam:role_assignment:write | SYSTEM or TENANT | Request/execute only the exact assignment operation permitted by the governed issuer |
| iam:role_assignment:revoke | SYSTEM or TENANT | Revoke only the exact assignment within the actor's scope |

The identifiers above must be reconciled with tools/eos/auth/permission_namespace.py before adoption. Do not add an alias, wildcard, admin:all, or role-derived bypass. The existing SYSTEM permission command plane is intentionally narrow: system_permission_command_policy.py currently permits only a small explicit allowlist. Extend it only through a separately reviewed policy change and tests; never assume a new namespace entry makes a permission assignable.

### Proposed role profiles

- **System Services Viewer** — read health and sanitized queue summaries only.
- **System Services Analyst** — queue read, case triage, case-bound identity/security read, support notes and escalation. No password reset, MFA reset, role grant or privilege activation.
- **Account Recovery Specialist** — analyst permissions plus narrowly scoped recovery initiation for non-privileged principals. The recovery service sends a one-time link/code to a previously verified contact; the operator cannot view the secret or choose the new password.
- **IAM Reviewer** — read access requests, compare requested scope with current authority and decide only requests allowed by a dedicated approval policy. Cannot self-approve or directly mint role possession.
- **IAM Assignment Operator** — can execute only separately authorized, source-policy-delegable assignments; no wildcard grants, self-elevation, privileged target reset, or unbounded SYSTEM delegation.
- **IAM Security Approver** — independent approval for sensitive role, MFA, session, and platform privilege actions; distinct actor from requester/operator.
- **System Services Auditor** — read-only audit/evidence access, with secrets and recovery material always redacted.
- **Platform Root / Break-glass** — existing governed privileged activation and dual-control mechanisms only. No permanent dashboard role or informal founder bypass.

Tenant-side roles must be separate: a tenant account administrator may handle only members of their own currently active tenant and may not reset platform-root, privileged, or cross-tenant principals. Professional Legal roles remain separate from tenant commercial ownership and from WILSY platform operations.

## 4. Password failure, lockout and compromise workflow

- Apply failure-only throttles on both normalized principal/email and transport peer dimensions; return generic errors to prevent account enumeration.
- Use bounded exponential/capped cooldown and Retry-After; never lock an account permanently from unauthenticated attempts alone (prevents denial-of-service lockout attacks).
- Distinguish temporary rate throttle from a durable security suspension. A throttle expires automatically at its governed deadline; a security suspension requires verified recovery or an authorized, evidence-backed incident resolution.
- On suspected compromise: preserve evidence, notify the verified recovery channel where policy permits, revoke affected sessions/device bindings, require fresh MFA or factor re-enrolment only through the governed workflow, and audit every decision.
- Never unlock an account solely because a support caller knows profile details. Require possession of a verified recovery factor or an approved higher-assurance process.
- Do not reveal whether an email/principal exists. Avoid displaying full recovery addresses or raw device identifiers to staff without a separate permission.

Existing PrincipalAuthenticationRateLimit, password-recovery, recovery-contact verification and device-provenance components must be reused and reconciled. Do not create a second competing lockout counter or password store.

## 5. Case workflow

OPEN → TRIAGED → IDENTITY_VERIFIED → ACTION_PENDING_APPROVAL (when required) → ACTION_EXECUTED → USER_CONFIRMATION_PENDING → RESOLVED

Alternative terminal states: REJECTED, CANCELLED, ESCALATED_SECURITY_INCIDENT, EXPIRED.

Each case records opaque case/principal references, tenant scope if applicable, issue category, requester channel, timestamps, assigned queue/analyst, evidence references, action and decision references, approval actors, status transitions, notification delivery state and resolution reason. Never store passwords, OTPs, reset tokens, MFA seeds or raw authentication secrets in tickets or logs.

## 6. Dashboard contract

The System Services Console may render these sections only when the EOS workspace projection contains their exact capabilities:

- Overview: source-backed queue counts, overdue cases, active security escalations and service-health states.
- Account support: case-bound identity posture, temporary throttle/suspension distinction, recovery-contact verification status, MFA posture, active sessions and device provenance.
- Recovery queue: recovery request state, delivery state, expiry and safe resend/expire actions where supported.
- Access requests: requester, target, requested role/permission, scope, justification, evidence, separation-of-duties and approval state.
- Role & permission catalogue: canonical namespace metadata, scope, current possession, assignment source, expiry, revocation state and effective authorization explanation.
- Audit timeline: immutable event references, actor, target, action, decision, timestamp and evidence link.
- Service health: live dependencies and last-success timestamps, with UNKNOWN / UNAVAILABLE distinct from zero.

No synthetic metrics, sample identities, or buttons that appear functional without a certified backend command. If a source is not connected, show NOT CONNECTED and keep the command unavailable.

## 7. API and persistence work to build next

Before the UI is wired to live operations, implement and certify EOS contracts:

1. GET /api/system-services/workspace-bootstrap — bounded console capabilities derived from current SYSTEM permission possession and workforce currentness.
2. GET /api/system-services/cases and GET /api/system-services/cases/{case_id} — paginated, sanitized, case-bound reads.
3. POST /api/system-services/cases — create support case; enumeration-safe identity handling.
4. POST /api/system-services/cases/{case_id}/triage and /escalate — governed transitions with immutable evidence.
5. GET /api/system-services/recovery-operations — status projection only; no raw tokens.
6. POST /api/system-services/recovery-operations — request a governed recovery workflow for a case-bound principal.
7. GET /api/iam/access-requests, POST /api/iam/access-requests/{id}/decision — separated review and execution.
8. GET /api/iam/role-assignments and governed assignment/revocation command endpoints — exact scope, source-policy allowlist, evidence and current possession.
9. Append-only audit records and outbox-backed notifications; no email send or external action before durable transaction commit.

Use Mongo transactions and unique/TTL indexes where required. Index DDL belongs to canonical application startup, never request handlers. Every write must be idempotent or replay-protected, correlated to a case, and tested against concurrent/replayed commands.

## 8. Implementation sequence

- **S0 — Certification recovery:** get Global Principal and Membership Selection passing; run its real-Mongo suite; complete Deputy Device Provenance and all dependent workspace checks on one exact PR head SHA.
- **S1 — IAM contract:** reconcile the proposed permission IDs with the canonical namespace, permission metadata, role policy, system assignment allowlist, current-possession resolver, workforce-currentness and dual-control tests. No automatic grants.
- **S2 — Service case domain:** immutable case state, repository, transition service, audit/outbox and real-Mongo concurrency/replay tests.
- **S3 — Recovery integration:** case-bound adapters to existing R10 recovery/contact verification and session/device revocation. Preserve enumeration safety and one-time capability semantics.
- **S4 — EOS APIs and bootstrap:** implement permission-checked reads and commands; deny by default; add real-Mongo API tests.
- **S5 — Console UI:** build the staff dashboard and navigation only from EOS workspace capability projection; add accessibility, empty/unavailable, denial and cross-tenant tests.
- **S6 — Adversarial certification:** unauthorized role, stale grant, revoked assignment, tenant mismatch, privileged target, self-approval, replay, concurrency, notification failure, persistence outage and audit/outbox atomicity.
- **S7 — Release:** merge only after all required workflows pass on the same PR head SHA and a deployment/runtime smoke test confirms EOS-only operation.

## 9. Acceptance criteria

- No permanent global support administrator or frontend-only permission.
- No support operator can see or mutate an unrelated tenant or privileged account.
- Password/MFA reset operations are workflow-based, verified, audited and never disclose secrets.
- Every role/permission decision is an EOS IAM decision with exact scope and currentness.
- Self-service and staff support are distinct surfaces.
- UI metrics and case lists are source-backed; unavailable sources are visibly unavailable.
- Real-Mongo tests prove atomicity, uniqueness, replay protection, concurrency and fail-closed behavior.
- All required CI runs refer to one exact PR head SHA before merge.

## 10. Competitive design references

- Okta Help Desk Admin demonstrates least-privilege support actions (password/MFA reset, unlock and session clearing) separated from Super Admin.
- Microsoft Entra documents target-role restrictions on password resets and separates self-service account portals for password, security information and sign-in activity.
- WILSY differentiator: unify case handling, identity recovery, device provenance, access governance and tenant-safe IAM under one EOS policy plane, with explicit evidence and dual control rather than a generic unrestricted helpdesk.

References:
- https://help.okta.com/en-us/content/topics/security/administrators-help-desk-admin.htm
- https://help.okta.com/oie/en-us/content/topics/security/administrators-admin-comparison.htm
- https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/privileged-roles-permissions
- https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-user-self-service-portals
