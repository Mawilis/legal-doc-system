"""
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive.
Authenticated tenant Projects lifecycle HTTP authority.

TITLE: WILSY OS Projects HTTP Router
VERSION: v1.48.1-MONGO-DRIVER-PHASE-CORRELATION
AUTHORITY: Python EOS canonical tenant IAM, entitlement and Projects registry.
EPITOME: Exposes one tenant-scoped Projects lifecycle through the existing
         validated domain and caller-transaction-owned registry. Role/entitlement activation is limited to the explicitly authorized Founder
         command; it does not select tenants or assign workforce ownership.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/projects_router.py
COLLABORATION / OWNERSHIP: Projects domain and registry own business lifecycle;
                           tenant authorization and entitlement registries own
                           independent admission; server.py mounts this router.
CERTIFICATION / UPDATE DATE: 2026-11-24.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No client-provided actor or tenant authority; IDs,
                            idempotency and revision are bounded; no-store
                            responses; errors disclose stable codes only.
TENANT BOUNDARY: X-Tenant-ID must equal the authenticated selected session
                 tenant; all registry and entitlement reads bind that tenant.
AUTHORITY BOUNDARY: Existing EOS principal, membership, capacity, permission,
                    assigned role and product entitlement remain conjunctive.
                    The internal Projects Platform Owner role is confined to
                    canonical WILSY; customer admission remains independently
                    governed and is not inferred here.
TRANSACTION BOUNDARY: Router owns each Mongo transaction and passes its exact
                      session to every registry/entitlement read and write;
                      response follows commit. The registry never opens one.
FINANCIAL AUTHORITY BOUNDARY: Projects cannot authorize spend, approval,
                              payment, execution or settlement; Kennel EOS only.
CHANGELOG:
   v1.48.1-MONGO-DRIVER-PHASE-CORRELATION wraps authorized
  GET transaction execution in the existing opt-in Mongo driver scope,
  exposing command/pool/pre-command waits to the same safe trace as IAM.
  No new Mongo call, changed transaction interface, timeout or retry.
  v1.48.0-TRACE-CORRELATED-PROJECT-READS joins the existing EOS
  authentication and tenant authorization opt-in timing stages to Projects
  slow GET and summary phases by an allowlisted opaque trace reference;
  no user/tenant/session IDs, token material, query data, new DB I/O,
  altered privilege or timeout semantics are recorded.
  v1.47.1-PRESERVED-READ-RETRY-INTERFACE retains the original
  zero-keyword Projects list transaction call and exact bounded retry
  contract, while a request-local ContextVar carries timing state into
  the unmodified transaction/entitlement path. No global mutable scope,
  IAM change or repeated source query is introduced.
  v1.47.0-BOUNDED-PROJECT-GET-LATENCY-PHASES profiles slow/failing
   read-only Projects list/task/task activity/evidence transactions;
   times Mongo session, entitlement and source phases with safe labels.
   No IAM, session, retry, query, mutation or timeout changes.
  v1.46.0-EXACT-SOURCE-WORK-PURPOSE-HISTORY exposes only a
  read-authorized exact-project/task bounded audit timeline with verified
  decisions and rationale; never returns actor principal IDs, replay keys,
  database records or cryptographic internals in the browser.
  v1.45.0-AUDITED-PURPOSE-UNCLASSIFIED-COMMAND admits
  reasoned purpose clearing as UNCLASSIFIED with current project:update,
  stable CAS and audit; no unverified source category is projected.
  v1.44.1-PURPOSE-CAS-HTTP-REVISION-READBACK includes the exact
  independent source-purpose revision in authorized GET and POST readback
  so clients use source CAS instead of guessing current metadata revision.
  v1.44.0-AUDITED-PROJECT-WORK-PURPOSE-COMMAND adds exact-source project work-purpose GET and audited
  project:update POST, strict revision/idempotency and same-transaction
  current source+event readback. No Founder or participant privilege inheritance.
  v1.46.0-EXACT-SOURCE-WORK-PURPOSE-HISTORY restores the historical
  v1.42.0 Founder contributor and participant profile changelog attribution
  without expanding the read-only Projects transaction recovery scope.
  v1.43.0-BOUNDED-PROJECT-LIST-SOURCE-RETRY reopens one fresh majority/snapshot
  transaction only if a read-only list's source cursor failed with the exact
  PROJECT_LIST_UNAVAILABLE code. It never retries IAM, entitlement, other
  source or transport errors and never retries write commands.
  v1.42.0-FOUNDER-EXPLICIT-CONTRIBUTOR-IAM-ADMISSION adds an explicit POST admission for an already-active Founder project contributor with a separately verified current ENTERPRISE_ADMIN grant authority. Delegates the narrow WILSY-only contributor IAM role through existing digest-only invitation/acceptance and durable readback, never by direct role write, automatic project participation or root fallback.
    v1.41.1-TYPED-PARTICIPANT-NAME-LOOKUP validates participant
  principal identifiers as nonempty strings before bounded display-name
  enrichment. Malformed identifiers fail closed; tenant IAM, project
  participation, persistence and financial authority remain unchanged.
  v1.42.0-FOUNDER-EXPLICIT-CONTRIBUTOR-IAM-ADMISSION resolves exact-tenant first/last
  names alongside source-verified active project participants for display
  only. Registry identity, permission, audit and assignment commands stay
  unchanged. Missing names yield null rather than an opaque identifier.
  v1.40.0-REVIEWED-TEMPLATE-WORK-OVERRIDES allows explicit, bounded
  edits to a verified starter template's titles, due offsets and acceptance
  criteria before atomic activation. Step IDs, DAG, kinds, role requirements,
  source revision and all EOS IAM are immutable; divergent replays reject.
  v1.39.0-IMMUTABLE-BASELINE-AUDITED-DEADLINES admits a bounded
  reason for target-date revision, leaves it out of project aggregate
  patches, and delegates its atomic immutable event persistence to the
  source-owned registry. Code/start baseline remains domain-immutable.
  v1.38.1-TYPED-TEMPLATE-STEP-BOUNDARY explicitly types the validated
  read-only platform blueprint at the router's activation boundary, fixing
  non-iterable object diagnostics for the target-date and task-step loops.
  It does not modify catalogue bytes, materialization, transaction, replay,
  IAM/tenant admission, idempotency, dates, or response payloads.
  v1.38.0-EXACT-TENANT-WORK-CAPABILITIES exposes a read-only
  per-project task action projection only after existing project:update
  authorization and exact-tenant registry read; no privileges are issued.
  v1.37.1-ATOMIC-TEMPLATE-REPLAY-READBACK reconciles retried activation against the immutable original
  project creation snapshot, avoiding divergent timestamp fingerprints;
  only identical tenant, actor, template, revision, dates and command replay.
  v1.37.1-ATOMIC-TEMPLATE-REPLAY-READBACK exposes seven audited read-only industry blueprints and an explicit
  jointly create/update-authorized atomic materialization of one PLANNED
  exact-tenant project, milestones, tasks and dependency topology. Each task
  is independently replay-bound; no staff, IAM or finance authority is issued.
  v1.36.0-AUTHORIZED-TASK-ACTIVITY-READ adds separately authorized,
  bounded owner and active-participant task event reads exposing immutable
  lifecycle evidence without replay tokens, command digests or snapshots.
  v1.36.0-AUTHORIZED-TASK-ACTIVITY-READ accepts bounded JSON arrays of string
  mentioned principal IDs as strict typed tuples at task comment admission;
  no domain permission, notification, idempotency or audit semantics change.
  v1.36.0-AUTHORIZED-TASK-ACTIVITY-READ bounds People name
  projection to one exact-tenant users query per verified option page;
  duplicate or cross-identity collisions fail closed. Names never grant IAM
  and missing names stay null, without per-option name query amplification.
  v1.36.0-AUTHORIZED-TASK-ACTIVITY-READ enriches already-eligible exact-tenant
  participant choices with source-verified display-only first/last names;
  unknown names remain null, never inferred from IDs or emails. No IAM,
  membership scope, grant/revoke, ordering or pagination change.
  v1.36.0-AUTHORIZED-TASK-ACTIVITY-READ also converts JSON dependency arrays to strict typed tuples
  only when every element remains a string; malformed values, lengths and
  dependency IDs retain strict/domain rejection. No IAM or task mutations change.
  v1.33.0-STRICT-TASK-DATE-WIRE-FIX normalizes only canonical YYYY-MM-DD task create and
  revision JSON dates through the existing strict project date parser.
  Malformed, non-date, or noncanonical inputs remain rejected; IAM,
  idempotency, transactions, and task-domain invariants are unchanged.
  v1.32.0-ENTITLEMENT-POINTER-HISTORY-TIMINGS records separately the existing current entitlement pointer and immutable history read times on slow Projects summaries without skipping either integrity check or altering non-profiled routes.
  v1.32.0-ENTITLEMENT-POINTER-HISTORY-TIMINGS separates per-attempt entitlement read, transaction wrapper, and source cursor/validation times for slow summary reads without extra Mongo queries or weaker tenant/IAM gates.
  v1.32.0-ENTITLEMENT-POINTER-HISTORY-TIMINGS logs safe bounded summary endpoint total and source-count latency only when slow or failing, separating Mongo/entitlement transaction overhead from validated registry scanning. No tenant/principal/record values, IAM changes, new queries or source-data fallbacks.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY narrows each immutable event actor to a bounded string before set insertion and exact-tenant identity lookup; rejects malformed event identity without coercion or privilege changes.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY adds current-principal owned_by_me owner-read filtering before paginating the exact tenant's projects. It never grants participant IAM, modifies project assignment or exposes foreign project records.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY canonicalizes only exact YYYY-MM-DD JSON dates and known project-status strings at the strict HTTP boundary. Rejects malformed values, extra fields, unsafe coercion; preserves domain status/date invariants and exact-tenant command authority.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY admits bounded palette colour on original owner/contributor note create and owner-only author revision, passes it to signed note state, without modifying note IAM, archive or legacy body-only requests.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY returns bounded creator/event-actor descriptive names in exact-tenant authorized project detail without modifying immutable audit actor IDs or the project result authority; absent names stay null.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY projects only first/last name from a bounded exact-tenant durable user identity to eligible project-owner selector records, preserving opaque ID as command authority; missing names remain missing and conflicting identity records deny the directory. No new IAM or role is created.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY requires fresh exact-version GuardDuty tag and pinned-policy provider readback outside Mongo transactions before evidence-backed approval requests and pending decisions; the write snapshot rechecks the exact immutable manifest and clearance fingerprints, with no new IAM/financial authority.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY allows bounded
  browser download only after current owner/participant IAM, a persisted
  matched scan clearance and fresh exact-version S3 tag and SHA3 byte checks.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY adds a verified
  scan-clearance field to exact-task attachment lists; missing scans remain
  quarantined and no signed document or download authority is asserted.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY binds optional
  task approval attachments exclusively after source-owned GuardDuty clearance;
  a named reviewer must revalidate every immutable evidence reference before
  deciding. Legacy rationale-only approvals remain distinct and unchanged.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY independently
  verifies exact-version GuardDuty clean tags and pinned S3 policy before
  storing immutable clearance. The principal cannot self-assert scan safety.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY accepts exact task
  encrypted provider-verified bytes in quarantine only; independently
  reauthorizes the contributor before immutable Mongo manifest commit.
  GET reads redact provider receipt; no scan, download or approval release.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY lists the named
  current Contributor's pending reviews, checking every project's active
  participation and exact source task before showing reviewer inbox rows.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY adds owner-requested,
  independently reviewed project-task business approvals with explicit
  currently active contributor reviewers, CAS and no financial authority.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY permits exact-project
  participants to see current co-participants for controlled mentions;
  tenant-wide membership directory access remains owner-only.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY atomically persists comment
  mention inbox evidence and exposes recipient-only project notification
  read and CAS read-receipt commands with current participant IAM gates.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY exposes a bounded my-projects
  discovery route, using exact current participant IAM, membership,
  entitlement, ACTIVE project records and nondisclosing tenant scope.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY adds source-owned task comments
  for owners and project contributors. Mentions require current ACTIVE exact-
  project participants; no notification delivery or approval is inferred.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY permits owner-only task edit and
  reassignment with current tenant/project contributor readback, guarded
  revision, idempotent Mongo transaction and immutable source task event.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY exposes bounded exact-tenant project
  participant candidate pages from current membership and EOS principal/role
  sources; client cannot invent a principal or bypass grantee eligibility.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY exposes owner and exact-project participant task
  listing, audited owner-authorized creation/assignment and revisioned
  lifecycle transitions; contributor completion requires personal assignment.
  Dependencies and unfinished child work are enforced in source transactions.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY admits exact project-bound participant detail and
  notes through separate current IAM read/contribute pairs, a matching active
  project participation record and canonical Projects entitlement. No tenant-wide
  project listing, generic update or owner privilege is granted.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY adds exact-tenant owner-authorized participant grant,
  revoke, and list operations; grantees require current principal/membership
  and ACTIVE tenant business capacity. Participation is never an IAM grant.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY moves note-domain validation inside existing
  authenticated transaction exception mapping; malformed text yields safe 422.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY introduces authenticated, project-existence-verified
  note CRUD through the existing exact-tenant Projects IAM, entitlements,
  majority transaction and audit boundaries. Notes never alter project state.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY projects verified next-page availability and exact offset
  into the authenticated list envelope; preserves page limits, IAM, tenant
  sessions, and all existing lifecycle command behavior.
  v1.29.0-TYPED-AUDIT-ACTOR-BOUNDARY refuses a PLANNED-to-ACTIVE
  transition unless the project has a current eligible owner and active
  tenant department. The check runs in the caller-owned project transaction;
  no activation or IAM grants occur during this change.
  v1.4.1-DEPARTMENT-REPLAY-ACTOR-BINDING binds department idempotency
  evidence to the exact authorized actor and returns identical successful
  command shape on replay; retained tenant, entitlement and CAS guards apply.
  v1.4.0-TENANT-GOVERNED-PROJECT-ASSIGNMENTS establishes independently
  authorized department provisioning, source-verified owner/department choices,
  and revision-guarded, immutable-event-backed owner assignment. No employee,
  principal, membership, entitlement or role is created. The generic project
  edit route cannot mutate either assignment field. Every query binds tenant.
  v1.3.1-SAFE-TRANSACTION-FAILURE-DIAGNOSTICS logs only bounded error
  classes and stable source codes for failed project transactions, separating
  corrupt audit/readback, entitlement and Mongo failures without exposing
  tenant, principal, records, Mongo details or relaxing fail-closed responses.
  v1.3.0-DETERMINISTIC-REUSABLE-PROJECT-CODE — Generates stable
  tenant-scoped project codes from EOS identity when a caller omits a code,
  preserves legacy replay snapshots, and retains unique-index collision denial.
  v1.2.1-FOUNDER-INVITATION-AUTHORITY — Uses tenant_owner's already
  eligible membership_invite operation, retaining the separately governed
  ENTERPRISE_ADMIN -> PROJECTS_PLATFORM_OWNER invitation delegation policy.
  Generic role_grant business-capacity policy remains unchanged.
  v1.2.0-GOVERNED-FOUNDER-PROJECTS-ADMISSION — Gates the API on startup index readiness, bounds list/path/idempotency inputs, and maps invalid domain construction to 422. Existing tenant, entitlement, IAM, transaction and readback rules remain intact.
  v1.0.0-PROJECTS-GOVERNED-API — Adds authenticated list, summary, detail,
  create, update/status-transition and soft-archive HTTP operations with exact
  session tenant matching, ACTIVE Projects entitlement, current permission /
  operation checks, transaction-bound persistence and durable event readback.

"""
from __future__ import annotations

from contextvars import ContextVar
from datetime import date, datetime, timezone
import hashlib
import logging
import re
from time import perf_counter
from typing import Literal, Any, Callable, Final, Mapping, TypedDict, cast

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, Request, Response, status
from starlette.datastructures import UploadFile
from pydantic import BaseModel, ConfigDict, Field, field_validator
from bson import ObjectId
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.auth.authentication import (
    get_current_identity, current_request_timing_correlation,
)
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_authority_policy import ELIGIBLE, tenant_role_operation_eligibility
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository, TenantMembershipNotFoundError,
    TenantMembershipRepositoryError,
)
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleRepository, TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID
from tools.eos.auth.invitation_creation import create_invitation, InvitationCreationError
from tools.eos.auth.invited_member_admission import admit_invited_member, InvitedMemberAdmissionError
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentRepository, RoleAssignmentNotFoundError, RoleAssignmentRepositoryError,
)
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityRepository, PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_authorization_decision_evidence_registry import TenantAuthorizationDecisionEvidenceRegistry
from tools.eos.saas.entitlement.tenant_product_entitlement_issuance_orchestrator import (
    issue_tenant_product_entitlement, TenantProductEntitlementIssuanceOrchestratorError,
)
from datetime import timedelta

from tools.eos.kernel import db as kernel_db
from tools.eos.saas.domain.project import (
    Project,
    ProjectError,
    ProjectSourceType,
    ProjectStatus,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
    derive_tenant_product_entitlement_id,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION as ENTITLEMENT_CURRENT_COLLECTION,
    HISTORY_COLLECTION as ENTITLEMENT_HISTORY_COLLECTION,
    TenantProductEntitlementRegistryError,
    TenantProductEntitlementRegistryNotFoundError,
    get_current as get_current_entitlement,
)
from tools.eos.saas.domain.project_note import ProjectNote, ProjectNoteError
from tools.eos.saas.projects.project_notification_registry import (
    COLLECTION as PROJECT_NOTIFICATION_COLLECTION,
    EVENT_COLLECTION as PROJECT_NOTIFICATION_EVENT_COLLECTION,
    ProjectNotificationRegistry, ProjectNotificationError,
    ProjectNotificationConflict, ProjectNotificationNotFound,
)
from tools.eos.saas.projects.project_attachment_clearance_registry import (
    COLLECTION as PROJECT_ATTACHMENT_CLEARANCE_COLLECTION,
    EVENT_COLLECTION as PROJECT_ATTACHMENT_CLEARANCE_EVENT_COLLECTION,
    ProjectAttachmentClearance, ProjectAttachmentClearanceRegistry,
    ProjectAttachmentClearanceError, ProjectAttachmentClearanceConflict,
    ProjectAttachmentClearanceNotFound,
)
from tools.eos.saas.projects.project_attachment_registry import (
    COLLECTION as PROJECT_ATTACHMENT_COLLECTION,
    EVENT_COLLECTION as PROJECT_ATTACHMENT_EVENT_COLLECTION,
    MAX_ATTACHMENT_BYTES,
    ProjectAttachment, ProjectAttachmentRegistry, ProjectAttachmentError,
    ProjectAttachmentConflict, ProjectAttachmentNotFound,
    attachment_id_for_command,
)
from tools.eos.saas.projects.project_attachment_storage import (
    ProjectAttachmentStorageError, store_quarantined_attachment,
    verify_guardduty_clean_attachment,
    read_verified_scanned_attachment,
)
from tools.eos.saas.projects.project_approval_registry import (
    COLLECTION as PROJECT_APPROVAL_COLLECTION,
    EVENT_COLLECTION as PROJECT_APPROVAL_EVENT_COLLECTION,
    ProjectApproval, ProjectApprovalRegistry, ProjectApprovalError,
    ProjectApprovalConflict, ProjectApprovalNotFound,
    approval_id_for_request,
)
from tools.eos.saas.projects.project_comment_registry import (
    COLLECTION as PROJECT_COMMENT_COLLECTION,
    EVENT_COLLECTION as PROJECT_COMMENT_EVENT_COLLECTION,
    ProjectComment, ProjectCommentRegistry, ProjectCommentError,
    ProjectCommentConflict, comment_id_for_command,
)
from tools.eos.saas.projects.project_template_catalogue import (
    get_blueprint, list_blueprints, SCHEMA as PROJECT_TEMPLATE_SCHEMA,
)
from tools.eos.saas.projects.project_work_purpose_registry import (
    COLLECTION as PROJECT_WORK_PURPOSE_COLLECTION,
    EVENT_COLLECTION as PROJECT_WORK_PURPOSE_EVENT_COLLECTION,
    ProjectWorkPurposeRegistry, WorkPurposeError, WorkPurposeConflict,
)
from tools.eos.saas.projects.project_task_registry import (
    COLLECTION as PROJECT_TASK_COLLECTION,
    EVENT_COLLECTION as PROJECT_TASK_EVENT_COLLECTION,
    ProjectTask, ProjectTaskRegistry, ProjectTaskError, ProjectTaskConflict,
    ProjectTaskNotFound, task_id_for_command,
)
from tools.eos.saas.projects.project_participant_registry import (
    COLLECTION as PROJECT_PARTICIPANT_COLLECTION,
    EVENT_COLLECTION as PROJECT_PARTICIPANT_EVENT_COLLECTION,
    ProjectParticipantRegistry, ProjectParticipantError,
    ProjectParticipantConflict, ProjectParticipantNotFound, PARTICIPANT_ROLES,
)
from tools.eos.saas.projects.project_note_registry import (
    COLLECTION as PROJECT_NOTE_COLLECTION,
    EVENT_COLLECTION as PROJECT_NOTE_EVENT_COLLECTION,
    ProjectNoteRegistry, ProjectNoteRegistryError,
    ProjectNoteConflict, ProjectNoteNotFound, note_id_for_command,
)
from tools.eos.saas.projects.project_registry import (
    COLLECTION as PROJECT_COLLECTION,
    EVENT_COLLECTION as PROJECT_EVENT_COLLECTION,
    ProjectNotFound,
    ProjectRegistry,
    ProjectRegistryConflict,
    ProjectRegistryError,
)


VERSION: Final[str] = "v1.48.1-MONGO-DRIVER-PHASE-CORRELATION"
logger = logging.getLogger("WilsyOS.API.Projects")

def _safe_projects_read_trace() -> str:
    """Expose only an EOS-issued or strictly validated request trace label."""
    value = current_request_timing_correlation()
    return value if isinstance(value, str) and re.fullmatch(
        r"TRC-(?:[A-Z0-9]{8}-[A-Z0-9]{6}|SERVER-[A-F0-9]{12})", value,
    ) else "TRACE_UNAVAILABLE"

# Projects list keeps its established _transaction(context, callback) call
# contract; profiling metadata lives only within the current request context.
_project_list_read_timings: ContextVar[dict[str, float] | None] = ContextVar(
    "wilsy_projects_list_read_timings", default=None,
)
_READ = RequireTenantAuthorization("project:read", "project_list")
_DETAIL = RequireTenantAuthorization("project:read", "project_detail")
_CREATE = RequireTenantAuthorization("project:create", "project_create")
_UPDATE = RequireTenantAuthorization("project:update", "project_update")
_ARCHIVE = RequireTenantAuthorization("project:archive", "project_archive")
_PARTICIPANT_DETAIL = RequireTenantAuthorization("project:participant:read", "project_participant_detail")
_PARTICIPANT_CONTRIBUTE = RequireTenantAuthorization("project:participant:contribute", "project_participant_contribute")
_DEPARTMENT_PROVISION = RequireTenantAuthorization("tenant:profile:write", "profile_update")
_DEPARTMENT_COLLECTION: Final[str] = "wilsy_tenant_departments"
_DEPARTMENT_EVENTS_COLLECTION: Final[str] = "wilsy_tenant_department_events"
_FOUNDER_INVITE = RequireTenantAuthorization("tenant:membership:write", "membership_invite")
_FOUNDER_PRODUCT_ISSUE = RequireTenantAuthorization("tenant_product_entitlement:issue", "tenant_product_entitlement_issue")



def _project_wire_iso_date(value: object) -> object:
    """Accept only canonical date-only JSON; preserve strict typed date support.

    The browser calendar emits YYYY-MM-DD strings. FastAPI validates its parsed
    JSON object in Python mode; strict Pydantic dates otherwise reject those
    legitimate strings before the project domain is reached. Other values are
    returned unchanged for strict model rejection.
    """
    if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return value
    return value


class ProjectCreateRequest(BaseModel):
    """Bounded project creation input; actor, tenant, status and IDs stay EOS-owned."""

    model_config = ConfigDict(extra="forbid", strict=True)

    name: str = Field(min_length=1, max_length=180)
    code: str | None = Field(default=None, max_length=80)
    summary: str | None = Field(default=None, max_length=4000)
    start_date: date | None = None
    target_date: date | None = None

    @field_validator("start_date", "target_date", mode="before")
    @classmethod
    def parse_wire_date(cls, value: object) -> object:
        """Normalize canonical date-only JSON without relaxing strict fields."""
        return _project_wire_iso_date(value)


class ProjectTemplateStepOverride(BaseModel):
    """Reviewed customization of one source-defined work step, not a new command."""

    model_config = ConfigDict(extra="forbid", strict=True)

    id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,63}$")
    title: str | None = Field(default=None, min_length=1, max_length=180)
    day: int | None = Field(default=None, ge=0, le=3650)
    acceptance: str | None = Field(default=None, min_length=1, max_length=1000)


class ProjectTemplateActivationRequest(BaseModel):
    """Explicit reviewed platform-blueprint activation, without grants."""

    model_config = ConfigDict(extra="forbid", strict=True)

    name: str = Field(min_length=1, max_length=180)
    template_revision: int = Field(ge=1)
    step_overrides: list[ProjectTemplateStepOverride] = Field(default_factory=list, max_length=25)
    start_date: date

    @field_validator("start_date", mode="before")
    @classmethod
    def parse_start_date(cls, value: object) -> object:
        return _project_wire_iso_date(value)


class ProjectUpdateRequest(BaseModel):
    """Revision-guarded update; status transition cannot be mixed with edits."""

    model_config = ConfigDict(extra="forbid", strict=True)

    expected_revision: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=180)
    code: str | None = Field(default=None, max_length=80)
    summary: str | None = Field(default=None, max_length=4000)
    start_date: date | None = None
    target_date: date | None = None
    target_change_reason: str | None = Field(default=None, min_length=12, max_length=1000)
    status: ProjectStatus | None = None

    @field_validator("start_date", "target_date", mode="before")
    @classmethod
    def parse_wire_date(cls, value: object) -> object:
        """Normalize only canonical date-only JSON for strict project updates."""
        return _project_wire_iso_date(value)

    @field_validator("status", mode="before")
    @classmethod
    def parse_wire_status(cls, value: object) -> object:
        """Map exact declared JSON enum values, never unknown status aliases."""
        if isinstance(value, str):
            try:
                return ProjectStatus(value)
            except ValueError:
                return value
        return value


class DepartmentCreateRequest(BaseModel):
    """Exact tenant department creation. ID and audit actor are EOS-generated."""

    model_config = ConfigDict(extra="forbid", strict=True)
    name: str = Field(min_length=2, max_length=100)


class ProjectAssignmentRequest(BaseModel):
    """Explicit, revision-guarded assignment; neither input establishes IAM."""

    model_config = ConfigDict(extra="forbid", strict=True)
    expected_revision: int = Field(ge=1)
    owner_principal_id: str = Field(min_length=1, max_length=180)
    department_id: str = Field(pattern=r"^dept-[0-9a-f]{32}$")


class ProjectTaskCreateRequest(BaseModel):
    """Bounded project task/subtask/milestone; identity, tenant and actor EOS-owned."""

    model_config = ConfigDict(extra="forbid", strict=True)
    kind: Literal["TASK", "MILESTONE"]
    parent_task_id: str | None = Field(default=None, pattern=r"^ptk-[0-9a-f]{48}$")
    title: str = Field(min_length=1, max_length=180)
    description: str = Field(default="", max_length=5000)
    due_date: date | None = None
    assignee_principal_id: str | None = Field(default=None, min_length=1, max_length=180)
    depends_on: tuple[str, ...] = Field(default=(), max_length=25)

    @field_validator("due_date", mode="before")
    @classmethod
    def parse_wire_date(cls, value: object) -> object:
        """Admit canonical calendar strings without weakening strict validation."""
        return _project_wire_iso_date(value)

    @field_validator("depends_on", mode="before")
    @classmethod
    def parse_wire_dependencies(cls, value: object) -> object:
        """Decode JSON string arrays; retain strict element and size validation."""
        return tuple(value) if isinstance(value, list) and all(
            isinstance(item, str) for item in value
        ) else value


class ProjectApprovalRequest(BaseModel):
    """Owner requests one separately reviewed task business decision."""

    model_config = ConfigDict(extra="forbid", strict=True)
    reviewer_principal_id: str = Field(min_length=1, max_length=180)
    rationale: str = Field(min_length=1, max_length=3000)
    evidence_attachment_ids: tuple[str, ...] = Field(default=(), max_length=10)


class ProjectApprovalDecisionRequest(BaseModel):
    """Named reviewer decides with explicit expected revision and rationale."""

    model_config = ConfigDict(extra="forbid", strict=True)
    expected_revision: int = Field(ge=1)
    decision: Literal["APPROVED", "REJECTED"]
    rationale: str = Field(min_length=1, max_length=3000)


class ProjectNotificationReadRequest(BaseModel):
    """Recipient-only notification receipt with explicit expected revision."""

    model_config = ConfigDict(extra="forbid", strict=True)
    expected_revision: int = Field(ge=1)


class ProjectTaskCommentRequest(BaseModel):
    """Plain-text task comment with at most ten explicit mentioned principals."""

    model_config = ConfigDict(extra="forbid", strict=True)
    body: str = Field(min_length=1, max_length=5000)
    mentions: tuple[str, ...] = Field(default=(), max_length=10)

    @field_validator("mentions", mode="before")
    @classmethod
    def parse_wire_mentions(cls, value: object) -> object:
        """Decode JSON string arrays without weakening strict model checks."""
        return tuple(value) if isinstance(value, list) and all(
            isinstance(item, str) for item in value
        ) else value


class ProjectTaskReviseRequest(BaseModel):
    """Owner-command task revision with complete editable fields and CAS."""

    model_config = ConfigDict(extra="forbid", strict=True)
    expected_revision: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=180)
    description: str = Field(default="", max_length=5000)
    due_date: date | None = None
    assignee_principal_id: str | None = Field(default=None, min_length=1, max_length=180)

    @field_validator("due_date", mode="before")
    @classmethod
    def parse_wire_date(cls, value: object) -> object:
        """Retain strict revision admission for canonical calendar strings."""
        return _project_wire_iso_date(value)


class ProjectTaskWorkPurposeRequest(BaseModel):
    """Source-owner categorization command; no inferred approval or gate."""

    model_config = ConfigDict(extra="forbid", strict=True)
    audience: Literal["OPERATING", "PLATFORM_BUILD", "UNCLASSIFIED"]
    reason: str = Field(min_length=10, max_length=1000)
    expected_task_revision: int = Field(ge=1)
    expected_purpose_revision: int = Field(ge=0)


class ProjectTaskTransitionRequest(BaseModel):
    """Revision-guarded task status transition without implicit completion."""

    model_config = ConfigDict(extra="forbid", strict=True)
    expected_revision: int = Field(ge=1)
    status: Literal["IN_PROGRESS", "BLOCKED", "DONE", "CANCELLED"]


class ProjectParticipantGrantRequest(BaseModel):
    """Grant a current tenant member one non-possessory project participation role."""

    model_config = ConfigDict(extra="forbid", strict=True)
    principal_id: str = Field(min_length=1, max_length=180)
    role: Literal["VIEWER", "CONTRIBUTOR"]


class ProjectParticipantRevokeRequest(BaseModel):
    """CAS-guarded participant revocation, preserving immutable audit history."""

    model_config = ConfigDict(extra="forbid", strict=True)
    expected_revision: int = Field(ge=1)


class ProjectNoteCreateRequest(BaseModel):
    """One bounded project note; tenant and author are server-derived."""

    model_config = ConfigDict(extra="forbid", strict=True)
    body: str = Field(min_length=1, max_length=10000)
    colour: Literal["yellow", "blue", "mint", "rose", "violet", "slate"] | None = None


class ProjectNoteReviseRequest(BaseModel):
    """Revision-guarded author-owned note content update."""

    model_config = ConfigDict(extra="forbid", strict=True)
    expected_revision: int = Field(ge=1)
    body: str = Field(min_length=1, max_length=10000)
    colour: Literal["yellow", "blue", "mint", "rose", "violet", "slate"] | None = None


class ProjectNoteArchiveRequest(BaseModel):
    """Revision-guarded soft archive without deleting note evidence."""

    model_config = ConfigDict(extra="forbid", strict=True)
    expected_revision: int = Field(ge=1)


class ProjectArchiveRequest(BaseModel):
    """Expected revision for an auditable soft-archive command."""

    model_config = ConfigDict(extra="forbid", strict=True)

    expected_revision: int = Field(ge=1)


def _require_selected_session_tenant(
    identity: SovereignIdentity = Depends(get_current_identity),
    tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> None:
    """Require the transport selector to match EOS-authenticated session scope.

    GLOBAL sessions carry current selected membership and capacity in the
    authenticated identity. Legacy tenant sessions remain supported only when
    the EOS identity's verified tenant exactly matches the request selector.
    """
    if (
        not isinstance(tenant_id, str)
        or not tenant_id
        or tenant_id != tenant_id.strip()
        or tenant_id != identity.tenant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "PROJECT_TENANT_SCOPE_MISMATCH",
                "message": "The requested tenant does not match the authenticated session.",
            },
            headers={"Cache-Control": "no-store"},
        )


def require_projects_indexes_ready(request: Request) -> None:
    """Keep every Projects route unavailable until canonical startup DDL succeeds."""
    if getattr(request.app.state, "projects_indexes_ready", False) is not True:
        raise HTTPException(status_code=503, detail="PROJECT_INDEXES_NOT_READY")


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
    dependencies=[
        Depends(_require_selected_session_tenant),
        Depends(require_projects_indexes_ready),
    ],
)


def _require_project_role_tenant(context: TenantAuthorizationContext) -> None:
    """Keep the internal-only Projects Platform Owner assignment company-scoped."""
    if (
        context.decision.authorization_role == "PROJECTS_PLATFORM_OWNER"
        and context.tenant_id != WILSY_COMPANY_TENANT_ID
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="PROJECT_PLATFORM_OWNER_TENANT_DENIED",
            headers={"Cache-Control": "no-store"},
        )


def _require_active_projects_entitlement(
    tenant_id: str, session: Any, phase_timings: dict[str, float] | None = None,
) -> None:
    """Require exact active canonical Projects entitlement in this transaction."""
    database = kernel_db.get_database()
    if database is None:
        raise HTTPException(status_code=503, detail="PROJECT_ENTITLEMENT_SOURCE_UNAVAILABLE")
    entitlement_id = derive_tenant_product_entitlement_id(
        tenant_id, TenantProductId.PROJECTS
    )
    try:
        entitlement = get_current_entitlement(
            tenant_id,
            entitlement_id,
            database[ENTITLEMENT_HISTORY_COLLECTION],
            database[ENTITLEMENT_CURRENT_COLLECTION],
            session=session,
            **({"phase_timings": phase_timings} if phase_timings is not None else {}),
        )
    except TenantProductEntitlementRegistryNotFoundError as error:
        raise HTTPException(
            status_code=403,
            detail="PROJECTS_ENTITLEMENT_REQUIRED",
            headers={"Cache-Control": "no-store"},
        ) from error
    except TenantProductEntitlementRegistryError as error:
        raise HTTPException(
            status_code=503,
            detail="PROJECT_ENTITLEMENT_SOURCE_UNAVAILABLE",
        ) from error
    if (
        entitlement.tenant_id != tenant_id
        or entitlement.product_id is not TenantProductId.PROJECTS
        or entitlement.lifecycle_state is not TenantProductEntitlementState.ACTIVE
    ):
        raise HTTPException(
            status_code=403,
            detail="PROJECTS_ENTITLEMENT_REQUIRED",
            headers={"Cache-Control": "no-store"},
        )


def _transaction(
    context: TenantAuthorizationContext,
    callback: Callable[[ProjectRegistry, Any], Any],
    *,
    write: bool = False,
    phase_timings: dict[str, float] | None = None,
) -> Any:
    """Run one exact-tenant operation in a caller-owned majority transaction.

    PyMongo's transaction callback retries begin from fresh snapshot state; all
    project and entitlement reads in each attempt receive the exact callback
    session. Index DDL belongs to the application startup readiness gate.
    """
    if phase_timings is None:
        phase_timings = _project_list_read_timings.get()
    _require_project_role_tenant(context)
    client, database = kernel_db.get_client(), kernel_db.get_database()
    if client is None or database is None:
        raise HTTPException(status_code=503, detail="PROJECT_DATABASE_UNAVAILABLE")
    projects = database.get_collection(
        PROJECT_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    events = database.get_collection(
        PROJECT_EVENT_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    registry = ProjectRegistry(projects, events)
    try:
        if phase_timings is None:
            with client.start_session() as mongo_session:
                return mongo_session.with_transaction(
                    lambda current: _execute_with_entitlement(
                        context, registry, callback, current
                    ),
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )
        session_started = perf_counter()
        with client.start_session() as mongo_session:
            phase_timings["session_open_ms"] = round(
                (perf_counter() - session_started) * 1000, 2
            )
            transaction_started = perf_counter()
            try:
                return mongo_session.with_transaction(
                    lambda current: _execute_with_entitlement(
                        context, registry, callback, current,
                        phase_timings=phase_timings,
                    ),
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority", j=True),
                    read_preference=ReadPreference.PRIMARY,
                )
            finally:
                phase_timings["transaction_ms"] = round(
                    (perf_counter() - transaction_started) * 1000, 2
                )
    except HTTPException as error:
        if error.status_code == 503:
            logger.error("PROJECTS_TRANSACTION_FAILURE failure_class=AUTHORITY status=503 code=%s", str(error.detail)[:100])
        raise
    except ProjectAttachmentClearanceNotFound as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except ProjectAttachmentClearanceConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except ProjectAttachmentClearanceError as error:
        logger.error("PROJECT_ATTACHMENT_CLEARANCE_FAILURE code=%s", error.code)
        raise HTTPException(status_code=503, detail=error.code) from error
    except ProjectAttachmentNotFound as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except ProjectAttachmentConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except ProjectAttachmentError as error:
        logger.error("PROJECT_ATTACHMENT_TRANSACTION_FAILURE code=%s", error.code)
        raise HTTPException(status_code=503, detail=error.code) from error
    except ProjectApprovalNotFound as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except ProjectApprovalConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except ProjectApprovalError as error:
        logger.error("PROJECT_APPROVAL_TRANSACTION_FAILURE code=%s", error.code)
        raise HTTPException(status_code=503, detail=error.code) from error
    except ProjectNotificationNotFound as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except ProjectNotificationConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except ProjectNotificationError as error:
        logger.error("PROJECT_NOTIFICATION_TRANSACTION_FAILURE code=%s", error.code)
        raise HTTPException(status_code=503, detail=error.code) from error
    except ProjectCommentConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except ProjectCommentError as error:
        logger.error("PROJECT_COMMENT_TRANSACTION_FAILURE code=%s", error.code)
        raise HTTPException(status_code=503, detail=error.code) from error
    except WorkPurposeConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except WorkPurposeError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except ProjectTaskNotFound as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except ProjectTaskConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except ProjectTaskError as error:
        logger.error("PROJECT_TASK_TRANSACTION_FAILURE code=%s", error.code)
        raise HTTPException(status_code=503, detail=error.code) from error
    except ProjectParticipantNotFound as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except ProjectParticipantConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except ProjectParticipantError as error:
        logger.error("PROJECT_PARTICIPANT_TRANSACTION_FAILURE code=%s", error.code)
        raise HTTPException(status_code=503, detail=error.code) from error
    except ProjectNoteNotFound as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except ProjectNoteConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except ProjectNoteError as error:
        raise HTTPException(status_code=422, detail=error.code) from error
    except ProjectNoteRegistryError as error:
        logger.error("PROJECTS_NOTE_TRANSACTION_FAILURE code=%s", error.code)
        raise HTTPException(status_code=503, detail=error.code) from error
    except ProjectNotFound as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except ProjectRegistryConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except ProjectError as error:
        raise HTTPException(status_code=422, detail=error.code) from error
    except ProjectRegistryError as error:
        logger.error("PROJECTS_TRANSACTION_FAILURE failure_class=REGISTRY code=%s", error.code)
        raise HTTPException(status_code=503, detail=error.code) from error
    except PyMongoError as error:
        logger.error("PROJECTS_TRANSACTION_FAILURE failure_class=MONGO error_type=%s", type(error).__name__)
        raise HTTPException(status_code=503, detail="PROJECT_DATABASE_UNAVAILABLE") from error
    except Exception as error:
        logger.error("PROJECTS_TRANSACTION_FAILURE failure_class=UNEXPECTED error_type=%s", type(error).__name__)
        raise HTTPException(status_code=503, detail="PROJECT_TRANSACTION_UNAVAILABLE") from error


def _execute_with_entitlement(
    context: TenantAuthorizationContext,
    registry: ProjectRegistry,
    callback: Callable[[ProjectRegistry, Any], Any],
    session: Any,
    phase_timings: dict[str, float] | None = None,
) -> Any:
    """Compose entitlement before invoking the source-owned project operation."""
    if phase_timings is None:
        _require_active_projects_entitlement(context.tenant_id, session)
        return callback(registry, session)
    phase_timings["attempts"] = phase_timings.get("attempts", 0.0) + 1
    entitlement_started = perf_counter()
    try:
        _require_active_projects_entitlement(
            context.tenant_id, session, phase_timings=phase_timings,
        )
    finally:
        phase_timings["entitlement_ms"] = phase_timings.get("entitlement_ms", 0.0) + round(
            (perf_counter() - entitlement_started) * 1000, 2
        )
    return callback(registry, session)


def _result(
    context: TenantAuthorizationContext,
    project: Project,
    *,
    events: tuple[dict[str, object], ...] = (),
) -> dict[str, object]:
    """Serialize canonical source state and audit evidence without UI inference."""
    return {
        "schema": "WILSY-PROJECT-RESULT/V1",
        "tenant_id": context.tenant_id,
        "principal_id": context.identity.identity_id,
        "project": project.to_dict(),
        "events": list(events),
        "authority": {"source": "PYTHON_EOS_PROJECT_REGISTRY", "financial_execution": False},
    }


@router.post("/founder-projects-admission")
def admit_founder_projects(
    grant_context: TenantAuthorizationContext = Depends(_FOUNDER_INVITE),
    issue_context: TenantAuthorizationContext = Depends(_FOUNDER_PRODUCT_ISSUE),
) -> dict[str, object]:
    """Execute the explicitly requested, canonical Founder Projects admission.

    A current tenant_owner with an ACTIVE ENTERPRISE_ADMIN assignment must
    independently pass membership-invite and entitlement-issue IAM. Delegation of
    PROJECTS_PLATFORM_OWNER remains governed by the invitation source policy. An additional
    PROJECTS_PLATFORM_OWNER role is accepted through the existing digest-only
    invitation service, not inserted directly. The source subscription-backed
    issuance orchestrator owns commercial evidence, and the caller-owned
    majority transaction owns its commit. Response follows durable readback.

    Two source transactions are necessarily separate: an accepted invitation
    may precede an entitlement failure. Retrying this explicit command safely
    reuses the already ACTIVE role and re-evaluates the missing entitlement.
    No production/customer tenant, generic role, plan mutation or financial
    execution is admitted.
    """
    tenant_id = WILSY_COMPANY_TENANT_ID
    principal_id = grant_context.identity.identity_id
    if (
        grant_context.tenant_id != tenant_id
        or issue_context.tenant_id != tenant_id
        or issue_context.identity.identity_id != principal_id
        or grant_context.decision.business_role != "tenant_owner"
        or issue_context.decision.business_role != "tenant_owner"
        or grant_context.decision.authorization_role != "ENTERPRISE_ADMIN"
        or issue_context.decision.authorization_role != "ENTERPRISE_ADMIN"
    ):
        raise HTTPException(status_code=403, detail="FOUNDER_PROJECTS_AUTHORITY_REQUIRED")
    client, database = kernel_db.get_client(), kernel_db.get_database()
    if client is None or database is None:
        raise HTTPException(status_code=503, detail="PROJECT_DATABASE_UNAVAILABLE")

    # Source role admission is explicitly governed by an inviter assignment,
    # recipient principal currentness, short-lived digest-only invitation,
    # capability acceptance and the ACTIVE existing membership gate.
    try:
        try:
            assigned = RoleAssignmentRepository.resolve(
                principal_id, tenant_id, "PROJECTS_PLATFORM_OWNER",
                collection=database["role_assignments"],
            )
        except RoleAssignmentNotFoundError:
            assigned = None
        if assigned is None:
            invitation = create_invitation(
                identity=grant_context.identity, tenant_id=tenant_id,
                recipient_principal_id=principal_id,
                authorization_role_id="PROJECTS_PLATFORM_OWNER",
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            )
            admit_invited_member(
                identity=grant_context.identity,
                invitation_id=invitation.invitation.invitation_id,
                capability=invitation.capability,
            )
        elif assigned.status.value != "ACTIVE":
            raise HTTPException(status_code=409, detail="PROJECTS_ROLE_NOT_ACTIVE")
    except (InvitationCreationError, InvitedMemberAdmissionError, RoleAssignmentRepositoryError) as error:
        raise HTTPException(status_code=409, detail="PROJECTS_ROLE_ADMISSION_UNVERIFIED") from error

    # Never bypass active subscription/commercial checks or create indexes in a
    # request. Index provisioning is an explicit administrative prerequisite.
    evidence = TenantAuthorizationDecisionEvidenceRegistry(
        database["tenant_authorization_decision_evidence"],
        principal_repository=PrincipalAuthorityRepository,
        membership_repository=TenantMembershipRepository,
        role_assignment_repository=RoleAssignmentRepository,
        business_role_repository=TenantBusinessRoleRepository,
    )
    entitlement_id = derive_tenant_product_entitlement_id(tenant_id, TenantProductId.PROJECTS)

    def issue(current: Any) -> None:
        try:
            existing = get_current_entitlement(
                tenant_id, entitlement_id,
                database[ENTITLEMENT_HISTORY_COLLECTION],
                database[ENTITLEMENT_CURRENT_COLLECTION],
                session=current,
            )
        except TenantProductEntitlementRegistryNotFoundError:
            existing = None
        if existing is not None:
            if existing.lifecycle_state is not TenantProductEntitlementState.ACTIVE:
                raise HTTPException(status_code=409, detail="PROJECTS_ENTITLEMENT_NOT_ACTIVE")
            return
        issue_tenant_product_entitlement(
            identity=issue_context.identity,
            product_id=TenantProductId.PROJECTS,
            idempotency_key="wilsy-founder-projects-internal-20261117",
            occurred_at=datetime.now(timezone.utc),
            subscription_collection=database["subscriptions"],
            entitlement_history_collection=database[ENTITLEMENT_HISTORY_COLLECTION],
            entitlement_current_collection=database[ENTITLEMENT_CURRENT_COLLECTION],
            authorization_evidence_registry=evidence,
            session=current,
        )

    try:
        with client.start_session() as session:
            session.with_transaction(
                issue, read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
            with session.start_transaction(read_concern=ReadConcern("snapshot")):
                entitlement = get_current_entitlement(
                    tenant_id, entitlement_id, database[ENTITLEMENT_HISTORY_COLLECTION],
                    database[ENTITLEMENT_CURRENT_COLLECTION], session=session,
                )
                assigned = RoleAssignmentRepository.resolve(
                    principal_id, tenant_id, "PROJECTS_PLATFORM_OWNER",
                    collection=database["role_assignments"], session=session,
                )
                if (entitlement.lifecycle_state is not TenantProductEntitlementState.ACTIVE
                    or assigned.status.value != "ACTIVE"):
                    raise HTTPException(status_code=503, detail="PROJECTS_ADMISSION_READBACK_UNVERIFIED")
    except HTTPException:
        raise
    except (TenantProductEntitlementIssuanceOrchestratorError, TenantProductEntitlementRegistryError, PyMongoError) as error:
        raise HTTPException(status_code=503, detail="PROJECTS_ENTITLEMENT_ISSUANCE_UNVERIFIED") from error
    return {
        "schema": "WILSY-FOUNDER-PROJECTS-ADMISSION/V1",
        "tenant_id": tenant_id,
        "principal_id": principal_id,
        "project_role": "ACTIVE",
        "projects_entitlement": "ACTIVE",
    }


@router.post("/{project_id}/founder-contributor-iam-admission")
def admit_founder_project_contributor_iam(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    grant_context: TenantAuthorizationContext = Depends(_FOUNDER_INVITE),
    project_context: TenantAuthorizationContext = Depends(_DETAIL),
) -> dict[str, object]:
    """Explicit self-admission of the narrowly scoped contributor IAM role.

    Only the canonical WILSY Founder tenant, an already current project
    CONTRIBUTOR and a separately authorized ENTERPRISE_ADMIN with current
    membership-invite authority may request this command. Grant executes
    through existing invitation+acceptance authority, never a direct database
    role write or a fabricated permission. User initiation is required.
    """
    response.headers["Cache-Control"] = "no-store"
    tenant_id = WILSY_COMPANY_TENANT_ID
    actor = grant_context.identity.identity_id
    if (
        grant_context.tenant_id != tenant_id
        or project_context.tenant_id != tenant_id
        or project_context.identity.identity_id != actor
        or grant_context.decision.business_role != "tenant_owner"
        or project_context.decision.business_role != "tenant_owner"
        or grant_context.decision.authorization_role != "ENTERPRISE_ADMIN"
        or project_context.decision.authorization_role != "PROJECTS_PLATFORM_OWNER"
    ):
        raise HTTPException(status_code=403, detail="PROJECT_CONTRIBUTOR_IAM_ADMISSION_DENIED")

    def require_existing_participant(registry: ProjectRegistry, session: Any) -> None:
        participants = _project_participants(registry, tenant_id, project_id, session)
        person = participants.get(
            tenant_id=tenant_id, project_id=project_id,
            principal_id=actor, session=session,
        )
        if person.role != "CONTRIBUTOR":
            raise HTTPException(status_code=403, detail="PROJECT_CONTRIBUTOR_SCOPE_REQUIRED")

    _transaction(project_context, require_existing_participant)

    database = kernel_db.get_database()
    if database is None:
        raise HTTPException(status_code=503, detail="PROJECT_DATABASE_UNAVAILABLE")
    role_id = "PROJECTS_PARTICIPANT_CONTRIBUTOR"

    try:
        try:
            assignment = RoleAssignmentRepository.resolve(
                actor, tenant_id, role_id, collection=database["role_assignments"],
            )
        except RoleAssignmentNotFoundError:
            assignment = None
        if assignment is None:
            invitation = create_invitation(
                identity=grant_context.identity,
                tenant_id=tenant_id,
                recipient_principal_id=actor,
                authorization_role_id=role_id,
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            )
            admit_invited_member(
                identity=grant_context.identity,
                invitation_id=invitation.invitation.invitation_id,
                capability=invitation.capability,
            )
        elif assignment.status.value != "ACTIVE":
            raise HTTPException(status_code=409, detail="PROJECT_CONTRIBUTOR_IAM_REVOKED")
    except HTTPException:
        raise
    except (InvitationCreationError, InvitedMemberAdmissionError, RoleAssignmentRepositoryError) as error:
        raise HTTPException(
            status_code=409, detail="PROJECT_CONTRIBUTOR_IAM_ADMISSION_UNVERIFIED",
        ) from error

    client = kernel_db.get_client()
    if client is None:
        raise HTTPException(status_code=503, detail="PROJECT_DATABASE_UNAVAILABLE")
    try:
        with client.start_session() as session:
            with session.start_transaction(read_concern=ReadConcern("snapshot")):
                assignment = RoleAssignmentRepository.resolve(
                    actor, tenant_id, role_id,
                    collection=database["role_assignments"], session=session,
                )
                if assignment.status.value != "ACTIVE":
                    raise HTTPException(
                        status_code=503,
                        detail="PROJECT_CONTRIBUTOR_IAM_READBACK_UNVERIFIED",
                    )
    except HTTPException:
        raise
    except (RoleAssignmentRepositoryError, RoleAssignmentNotFoundError, PyMongoError) as error:
        raise HTTPException(
            status_code=503, detail="PROJECT_CONTRIBUTOR_IAM_READBACK_UNVERIFIED",
        ) from error

    return {
        "schema": "WILSY-PROJECT-CONTRIBUTOR-IAM-ADMISSION/V1",
        "tenant_id": tenant_id,
        "principal_id": actor,
        "project_id": project_id,
        "authorization_role": role_id,
        "authorization_state": "ACTIVE",
        "authority": {"source": "PYTHON_EOS_ROLE_ASSIGNMENT", "financial_execution": False},
    }


def _profiled_projects_get(
    context: TenantAuthorizationContext,
    operation: str,
    callback: Callable[[ProjectRegistry, Any], dict[str, object]],
) -> dict[str, object]:
    """Profile an authorized GET without additional queries or identity logging.

    Timing begins after FastAPI authorization dependencies. Thus handler_ms
    does not measure authentication or prehandler permission evaluation.
    """
    if operation not in {
        "PROJECT_LIST", "TASK_LIST", "TASK_COMMENTS",
        "TASK_EVENTS", "TASK_APPROVALS", "TASK_ATTACHMENTS",
    }:
        raise RuntimeError("PROJECT_READ_PROFILE_OPERATION_INVALID")
    started = perf_counter()
    timings: dict[str, float] = {}
    outcome = "OK"

    def measured(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        source_started = perf_counter()
        try:
            return callback(registry, session)
        finally:
            timings["source_ms"] = round(
                timings.get("source_ms", 0.0)
                + (perf_counter() - source_started) * 1000, 2,
            )

    try:
        # Instrument the existing exact-snapshot transaction, not its query
        # data. When diagnostics are disabled, this scope is a no-op.
        with kernel_db.mongo_timing_scope(
            stage="PROJECTS_READ", correlation=_safe_projects_read_trace(),
        ):
            if operation == "PROJECT_LIST":
                token = _project_list_read_timings.set(timings)
                try:
                    # Preserve the no-keyword call and exact bounded retry.
                    return _transaction(context, measured)
                finally:
                    _project_list_read_timings.reset(token)
            return _transaction(context, measured, phase_timings=timings)
    except Exception:
        outcome = "FAILED"
        raise
    finally:
        handler_ms = round((perf_counter() - started) * 1000, 2)
        if outcome == "FAILED" or handler_ms >= 1000:
            logger.warning(
                "PROJECTS_GET_LATENCY trace_id=%s operation=%s outcome=%s handler_ms=%.2f "
                "session_open_ms=%s transaction_ms=%s entitlement_ms=%s "
                "source_ms=%s pointer_ms=%s history_ms=%s attempts=%s",
                _safe_projects_read_trace(), operation, "SLOW" if outcome == "OK" else outcome, handler_ms,
                timings.get("session_open_ms", "NOT_REACHED"),
                timings.get("transaction_ms", "NOT_REACHED"),
                timings.get("entitlement_ms", "NOT_REACHED"),
                timings.get("source_ms", "NOT_REACHED"),
                timings.get("entitlement_pointer_ms", "NOT_REACHED"),
                timings.get("entitlement_history_ms", "NOT_REACHED"),
                int(timings.get("attempts", 0)),
            )


@router.get("")
def list_projects(
    response: Response,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    project_status: ProjectStatus | None = None,
    include_archived: bool = False,
    owned_by_me: bool = False,
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, object]:
    """Read the current tenant's bounded project page under current IAM."""
    response.headers["Cache-Control"] = "no-store"

    def load(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        items, has_more = registry.list_page_for_tenant(
            tenant_id=context.tenant_id,
            session=session,
            limit=limit,
            offset=offset,
            status=project_status,
            include_archived=include_archived,
            owner_principal_id=context.identity.identity_id if owned_by_me else None,
        )
        return {
            "schema": "WILSY-PROJECT-LIST/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "items": [item.to_dict() for item in items],
            "limit": limit,
            "offset": offset,
            "has_more": has_more,
            "next_offset": offset + len(items) if has_more else None,
        }

    # A registry-wrapped Mongo cursor failure is no longer visible to
    # PyMongo's with_transaction transient retry classifier. Re-admit the
    # exact already-authorized GET in one wholly new snapshot transaction,
    # including fresh current entitlement verification; never retry writes,
    # denials, missing indexes, source corruption or unrelated 503s.
    for attempt in range(2):
        try:
            return _profiled_projects_get(context, "PROJECT_LIST", load)
        except HTTPException as error:
            if (attempt != 0 or error.status_code != 503
                    or error.detail != "PROJECT_LIST_UNAVAILABLE"):
                raise
    raise HTTPException(status_code=503, detail="PROJECT_LIST_UNAVAILABLE")


@router.get("/summary")
def project_summary(
    response: Response,
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, object]:
    """Return tenant-scoped status counts derived from validated project records."""
    response.headers["Cache-Control"] = "no-store"
    started = perf_counter()
    count_elapsed_ms: float | None = None
    phase_timings: dict[str, float] = {}

    def read(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        nonlocal count_elapsed_ms
        scan_started = perf_counter()
        try:
            counts = registry.summary_for_tenant(
                tenant_id=context.tenant_id, session=session,
                phase_timings=phase_timings,
            )
        finally:
            count_elapsed_ms = round((perf_counter() - scan_started) * 1000, 2)
        return {
            "schema": "WILSY-PROJECT-SUMMARY/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "counts": counts,
        }

    try:
        result = _transaction(context, read, phase_timings=phase_timings)
    except Exception:
        elapsed_ms = round((perf_counter() - started) * 1000, 2)
        logger.warning(
            "PROJECTS_SUMMARY_READ trace_id=%s outcome=FAILED total_ms=%.2f count_ms=%s "
            "entitlement_ms=%s transaction_ms=%s session_open_ms=%s "
            "pointer_ms=%s history_ms=%s cursor_first_ms=%s "
            "cursor_remaining_ms=%s hydrate_ms=%s attempts=%s",
            _safe_projects_read_trace(), elapsed_ms, count_elapsed_ms if count_elapsed_ms is not None else "NOT_REACHED",
            phase_timings.get("entitlement_ms", "NOT_REACHED"),
            phase_timings.get("transaction_ms", "NOT_REACHED"),
            phase_timings.get("session_open_ms", "NOT_REACHED"),
            phase_timings.get("entitlement_pointer_ms", "NOT_REACHED"),
            phase_timings.get("entitlement_history_ms", "NOT_REACHED"),
            phase_timings.get("cursor_first_ms", "NOT_REACHED"),
            phase_timings.get("cursor_remaining_ms", "NOT_REACHED"),
            phase_timings.get("hydrate_ms", "NOT_REACHED"),
            int(phase_timings.get("attempts", 0)),
        )
        raise
    elapsed_ms = round((perf_counter() - started) * 1000, 2)
    if elapsed_ms >= 1000:
        logger.warning(
            "PROJECTS_SUMMARY_READ trace_id=%s outcome=SLOW total_ms=%.2f count_ms=%s "
            "entitlement_ms=%s transaction_ms=%s session_open_ms=%s "
            "pointer_ms=%s history_ms=%s cursor_first_ms=%s "
            "cursor_remaining_ms=%s hydrate_ms=%s attempts=%s",
            _safe_projects_read_trace(), elapsed_ms, count_elapsed_ms if count_elapsed_ms is not None else "NOT_REACHED",
            phase_timings.get("entitlement_ms", "NOT_REACHED"),
            phase_timings.get("transaction_ms", "NOT_REACHED"),
            phase_timings.get("session_open_ms", "NOT_REACHED"),
            phase_timings.get("entitlement_pointer_ms", "NOT_REACHED"),
            phase_timings.get("entitlement_history_ms", "NOT_REACHED"),
            phase_timings.get("cursor_first_ms", "NOT_REACHED"),
            phase_timings.get("cursor_remaining_ms", "NOT_REACHED"),
            phase_timings.get("hydrate_ms", "NOT_REACHED"),
            int(phase_timings.get("attempts", 0)),
        )
    return result


class _ProjectTemplateStep(TypedDict):
    """Static shape certified by project_template_catalogue._validate_catalogue."""

    id: str
    kind: Literal["TASK", "MILESTONE"]
    title: str
    day: int
    role: str
    acceptance: str
    depends_on: list[str]


class _ProjectTemplateBlueprint(TypedDict):
    """Validated catalogue description; no caller-supplied step authority."""

    slug: str
    industry: str
    title: str
    revision: int
    description: str
    steps: list[_ProjectTemplateStep]


def _generated_project_code(project_id: str) -> str:
    """Derive an immutable human-readable code from EOS project identity.

    Tenant/actor/idempotency are already bound into the SHA3-512 project ID.
    The 64-bit code suffix is stable across retries; tenant-scoped unique
    persistence indexes reject the extremely unlikely collision rather than
    silently relabeling a different project.
    """
    if not isinstance(project_id, str) or not re.fullmatch(r"prj-[0-9a-f]{48}", project_id):
        raise ProjectRegistryError("PROJECT_CODE_SOURCE_INVALID")
    return "PRJ-" + project_id[-16:].upper()


@router.get("/templates")
def list_project_templates(
    response: Response,
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, object]:
    """List platform-provided starting definitions under actual tenant IAM."""
    response.headers["Cache-Control"] = "no-store"
    def read(_registry: ProjectRegistry, _session: Any) -> dict[str, object]:
        return {
            "schema": "WILSY-PROJECT-TEMPLATE-CATALOGUE/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "items": list(list_blueprints()),
            "ownership": "PLATFORM_STARTERS",
        }
    return _transaction(context, read)


@router.post("/templates/{slug}/activate", status_code=status.HTTP_201_CREATED)
def activate_project_template(
    payload: ProjectTemplateActivationRequest,
    response: Response,
    slug: str = Path(pattern=r"^[a-z][a-z0-9-]{2,63}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_CREATE),
    update_context: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Atomically materialise exact-tenant project work; grant nothing."""
    response.headers["Cache-Control"] = "no-store"
    if (context.tenant_id != update_context.tenant_id
        or context.identity.identity_id != update_context.identity.identity_id):
        raise HTTPException(status_code=403, detail="PROJECT_TEMPLATE_ACTOR_SCOPE_DENIED")
    key = _note_idempotency_key(idempotency_key)
    source_blueprint = get_blueprint(slug)
    if source_blueprint is None:
        raise HTTPException(status_code=404, detail="PROJECT_TEMPLATE_NOT_FOUND")
    # The static cast reflects the catalogue's mandatory startup validation.
    # Only trusted platform definitions reach this boundary; HTTP cannot
    # supply template steps or rewrite source dependencies.
    template = cast(_ProjectTemplateBlueprint, source_blueprint)
    if payload.template_revision != template["revision"]:
        raise HTTPException(status_code=409, detail="PROJECT_TEMPLATE_REVISION_CHANGED")
    permitted_ids = {step["id"] for step in template["steps"]}
    changes: dict[str, dict[str, object]] = {}
    for override in payload.step_overrides:
        if override.id not in permitted_ids or override.id in changes:
            raise HTTPException(status_code=422, detail="PROJECT_TEMPLATE_OVERRIDE_INVALID")
        patch = override.model_dump(exclude={"id"}, exclude_none=True)
        if not patch:
            raise HTTPException(status_code=422, detail="PROJECT_TEMPLATE_OVERRIDE_EMPTY")
        changes[override.id] = patch
    steps = [
        cast(_ProjectTemplateStep, {**step, **changes.get(step["id"], {})})
        for step in template["steps"]
    ]
    prior_days: dict[str, int] = {}
    for step in steps:
        if any(prior_days.get(dep, 3651) > step["day"] for dep in step["depends_on"]):
            raise HTTPException(status_code=422, detail="PROJECT_TEMPLATE_DEPENDENCY_DATE_INVALID")
        prior_days[step["id"]] = step["day"]
    actor = context.identity.identity_id
    tenant = context.tenant_id
    prefix = hashlib.sha3_512(
        f"{tenant}\x00{actor}\x00{key}\x00{slug}\x00{payload.template_revision}".encode()
    ).hexdigest()
    project_key = "template-project:" + prefix
    project_id = "prj-" + hashlib.sha3_512(
        f"{tenant}\x00{actor}\x00{project_key}".encode()
    ).hexdigest()[:48]
    instant = datetime.now(timezone.utc)
    project = Project(
        project_id=project_id, tenant_id=tenant, name=payload.name,
        code=_generated_project_code(project_id),
        summary=("Activated platform template: " + str(template["title"])
            + " (revision " + str(template["revision"]) + "). "
            + str(template["description"])),
        status=ProjectStatus.PLANNED, owner_principal_id=None,
        department_id=None, start_date=payload.start_date,
        target_date=payload.start_date + timedelta(
            days=max(step["day"] for step in steps)),
        source_type=ProjectSourceType.INTERNAL, external_source_reference=None,
        created_by_principal_id=actor, created_at=instant,
        updated_by_principal_id=actor, updated_at=instant,
    )

    def materialize(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        # Project creation fingerprints include source timestamps. Recover the
        # original immutable snapshot before replay instead of regenerating
        # creation timestamps and falsely treating a valid retry as divergent.
        previous = registry.list_events(
            tenant_id=tenant, project_id=project_id, session=session,
        )
        replay = next((event for event in previous
                       if event.get("idempotency_key") == project_key), None)
        if replay is None:
            committed = registry.create_or_replay(
                project=project, actor_principal_id=actor,
                idempotency_key=project_key, occurred_at=instant, session=session,
            )
        else:
            snapshot = replay.get("result_snapshot")
            if (replay.get("event_type") != "PROJECT_CREATED"
                or replay.get("actor_principal_id") != actor
                or not isinstance(snapshot, Mapping)):
                raise ProjectRegistryConflict("PROJECT_TEMPLATE_REPLAY_CONFLICT")
            committed = Project.from_dict(dict(snapshot))
            expected = project.to_dict()
            persisted = committed.to_dict()
            fields = (
                "project_id", "tenant_id", "name", "code", "summary", "status",
                "owner_principal_id", "department_id", "start_date", "target_date",
                "source_type", "created_by_principal_id",
            )
            if any(persisted.get(field) != expected.get(field) for field in fields):
                raise ProjectRegistryConflict("PROJECT_TEMPLATE_REPLAY_CONFLICT")
        if committed.project_id != project_id or committed.name != payload.name:
            raise ProjectRegistryConflict("PROJECT_TEMPLATE_REPLAY_CONFLICT")
        tasks = _project_task_store(registry, tenant, project_id, session)
        mapped: dict[str, str] = {}
        manifest: list[dict[str, object]] = []
        for step in steps:
            task_key = "template-step:" + hashlib.sha3_512(
                (prefix + ":" + step["id"]).encode()
            ).hexdigest()
            task_id = task_id_for_command(tenant, project_id, actor, task_key)
            dependencies = tuple(mapped[value] for value in step["depends_on"])
            expected = ProjectTask(
                tenant_id=tenant, project_id=project_id, task_id=task_id,
                kind=step["kind"], parent_task_id=None,
                title=step["title"],
                description=("Role required: " + step["role"]
                    + ". Acceptance evidence: " + step["acceptance"]),
                status="TODO", assignee_principal_id=None,
                due_date=(payload.start_date + timedelta(days=step["day"])).isoformat(),
                depends_on=dependencies, created_by_principal_id=actor,
                updated_by_principal_id=actor, created_at=instant, updated_at=instant,
            )
            saved = tasks.create_or_replay(
                task=expected, idempotency_key=task_key, session=session,
            )
            verified = tasks.get(
                tenant_id=tenant, project_id=project_id, task_id=task_id, session=session,
            )
            if verified.fingerprint != saved.fingerprint:
                raise ProjectTaskError("PROJECT_TEMPLATE_TASK_READBACK_MISMATCH")
            mapped[step["id"]] = task_id
            manifest.append({
                "template_step_id": step["id"],
                "task_id": task_id,
                "revision": verified.revision,
                "kind": verified.kind,
                "due_date": verified.due_date,
                "depends_on": list(verified.depends_on),
            })
        verified_project = registry.get(
            tenant_id=tenant, project_id=project_id, session=session,
        )
        if verified_project.fingerprint != committed.fingerprint:
            raise ProjectRegistryError("PROJECT_TEMPLATE_PROJECT_READBACK_MISMATCH")
        return {
            "schema": "WILSY-PROJECT-TEMPLATE-ACTIVATION/V1",
            "tenant_id": tenant, "principal_id": actor,
            "template_slug": slug, "template_revision": template["revision"],
            "template_schema": PROJECT_TEMPLATE_SCHEMA,
            "project": verified_project.to_dict(), "items": manifest,
            "authority": {"financial_execution": False,
                          "auto_assignments": False, "iam_grants": False},
        }

    return _transaction(context, materialize, write=True)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreateRequest,
    response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_CREATE),
) -> dict[str, object]:
    """Create an internal project and prove persisted readback before response.

    The stable identity is derived from tenant, actor and idempotency key. A
    retry returns the original creation snapshot only when the caller and all
    business-input fields match the immutable event; divergent reuse conflicts.
    When a code is omitted, EOS derives a stable PRJ-<hex> reference from the
    tenant/actor/idempotency-bound project identity. Legacy null-code replays
    remain immutable and never silently rewrite existing persisted history.
    """
    response.headers["Cache-Control"] = "no-store"
    if (
        not isinstance(idempotency_key, str)
        or not idempotency_key.strip()
        or idempotency_key != idempotency_key.strip()
        or len(idempotency_key) > 200
    ):
        raise HTTPException(status_code=422, detail="PROJECT_IDEMPOTENCY_KEY_INVALID")
    key = idempotency_key
    now = datetime.now(timezone.utc)
    project_id = "prj-" + hashlib.sha3_512(
        f"{context.tenant_id}\x00{context.identity.identity_id}\x00{key}".encode("utf-8")
    ).hexdigest()[:48]
    try:
        project = Project(
            project_id=project_id,
            tenant_id=context.tenant_id,
            name=payload.name,
            code=payload.code if payload.code is not None else _generated_project_code(project_id),
            summary=payload.summary,
            status=ProjectStatus.PLANNED,
            owner_principal_id=None,
            department_id=None,
            start_date=payload.start_date,
            target_date=payload.target_date,
            source_type=ProjectSourceType.INTERNAL,
            external_source_reference=None,
            created_by_principal_id=context.identity.identity_id,
            created_at=now,
            updated_by_principal_id=context.identity.identity_id,
            updated_at=now,
        )
    except ProjectError as error:
        raise HTTPException(status_code=422, detail=error.code) from error

    def create(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        events = registry.list_events(
            tenant_id=context.tenant_id, project_id=project_id, session=session
        )
        replay = next((event for event in events if event.get("idempotency_key") == key), None)
        if replay is not None:
            snapshot = replay.get("result_snapshot")
            if (
                replay.get("event_type") != "PROJECT_CREATED"
                or replay.get("actor_principal_id") != context.identity.identity_id
                or not isinstance(snapshot, Mapping)
            ):
                raise ProjectRegistryConflict("PROJECT_DIVERGENT_REPLAY")
            prior = Project.from_dict(dict(snapshot))
            command_fields = (
                "project_id", "tenant_id", "name", "code", "summary", "status",
                "owner_principal_id", "department_id", "start_date", "target_date",
                "source_type", "external_source_reference", "created_by_principal_id",
            )
            requested = project.to_dict()
            stored = prior.to_dict()
            # Legacy projects created before automatic codes may have a null
            # code. Preserve their immutable idempotent replay response.
            if payload.code is None and stored.get("code") is None:
                requested["code"] = None
            if any(stored.get(field) != requested.get(field) for field in command_fields):
                raise ProjectRegistryConflict("PROJECT_DIVERGENT_REPLAY")
            return _result(context, prior, events=events)
        created = registry.create_or_replay(
            project=project,
            actor_principal_id=context.identity.identity_id,
            idempotency_key=key,
            occurred_at=now,
            session=session,
        )
        readback = registry.get(
            tenant_id=context.tenant_id,
            project_id=project_id,
            session=session,
        )
        if readback.fingerprint != created.fingerprint:
            raise ProjectRegistryError("PROJECT_CREATE_READBACK_MISMATCH")
        event_readback = registry.list_events(
            tenant_id=context.tenant_id, project_id=project_id, session=session
        )
        return _result(context, readback, events=event_readback)

    return _transaction(context, create, write=True)


def _project_owner_eligible(database: Any, tenant_id: str, principal_id: str, session: Any) -> bool:
    """Verify current principal, membership and tenant-owner business capacity.

    This is project responsibility eligibility, not authorization to operate
    under the assignee's identity. Explicit command IAM remains with the caller.
    No employee record, personal details, or browser role is trusted.
    """
    if not principal_id or principal_id != principal_id.strip():
        return False
    try:
        principal = PrincipalAuthorityRepository.get(
            principal_id, database["principal_authorities"], session=session,
        )
        membership = TenantMembershipRepository.resolve(
            principal_id, tenant_id, database["tenant_memberships"], session=session,
        )
        roles = TenantBusinessRoleRepository.resolve_all(
            principal_id, tenant_id, database["tenant_business_roles"], session=session,
        )
    except (PrincipalAuthorityNotFoundError, TenantMembershipNotFoundError):
        return False
    except (
        PrincipalAuthorityRepositoryError, TenantMembershipRepositoryError,
        TenantBusinessRoleRepositoryError,
    ) as error:
        raise HTTPException(status_code=503, detail="PROJECT_OWNER_AUTHORITY_UNAVAILABLE") from error
    return (
        principal.status is PrincipalStatus.ACTIVE
        and membership.status is TenantMembershipStatus.ACTIVE
        and any(
            role.status is TenantBusinessRoleStatus.ACTIVE
            and role.business_role == "tenant_owner"
            and tenant_role_operation_eligibility(role.business_role, "project_update") == ELIGIBLE
            for role in roles
        )
    )


def _project_participant_eligible(
    database: Any, tenant_id: str, principal_id: str, session: Any,
) -> bool:
    """Require ACTIVE principal, membership and at least one ACTIVE tenant role.

    Employment, founder status, project ownership and an assignment selector are
    not substitutes for these independent currentness sources. This eligibility
    does NOT itself create an IAM role or permit a participant API command.
    """
    if not isinstance(principal_id, str) or not principal_id or principal_id != principal_id.strip():
        return False
    try:
        principal = PrincipalAuthorityRepository.get(
            principal_id, database["principal_authorities"], session=session,
        )
        membership = TenantMembershipRepository.resolve(
            principal_id, tenant_id, database["tenant_memberships"], session=session,
        )
        roles = TenantBusinessRoleRepository.resolve_all(
            principal_id, tenant_id, database["tenant_business_roles"], session=session,
        )
    except (PrincipalAuthorityNotFoundError, TenantMembershipNotFoundError):
        return False
    except (
        PrincipalAuthorityRepositoryError, TenantMembershipRepositoryError,
        TenantBusinessRoleRepositoryError,
    ) as error:
        raise HTTPException(status_code=503, detail="PROJECT_PARTICIPANT_AUTHORITY_UNAVAILABLE") from error
    return (
        principal.status is PrincipalStatus.ACTIVE
        and membership.status is TenantMembershipStatus.ACTIVE
        and any(role.status is TenantBusinessRoleStatus.ACTIVE for role in roles)
    )


def _current_department(database: Any, tenant_id: str, department_id: str, session: Any) -> dict[str, object]:
    """Resolve one active, validated canonical tenant department, never a label."""
    try:
        row = database[_DEPARTMENT_COLLECTION].find_one(
            {"tenant_id": tenant_id, "department_id": department_id}, session=session,
        )
    except PyMongoError as error:
        raise HTTPException(status_code=503, detail="PROJECT_DEPARTMENT_SOURCE_UNAVAILABLE") from error
    if row is None or row.get("status") != "ACTIVE":
        raise HTTPException(status_code=409, detail="PROJECT_DEPARTMENT_NOT_ELIGIBLE")
    name = row.get("name")
    if (
        not isinstance(name, str) or not 2 <= len(name) <= 100
        or name != name.strip() or not isinstance(row.get("revision"), int)
        or row["revision"] < 1
        or row.get("tenant_id") != tenant_id
        or row.get("department_id") != department_id
    ):
        raise HTTPException(status_code=503, detail="PROJECT_DEPARTMENT_RECORD_INVALID")
    return {
        "department_id": department_id,
        "name": name,
        "revision": row["revision"],
        "status": "ACTIVE",
    }


def _exact_tenant_project_person_name(
    database: Any, tenant_id: str, principal_id: str, session: Any,
) -> dict[str, str | None]:
    """Project display-only names from exact tenant-scoped durable authentication.

    Owner eligibility, when required, is established separately. Actor names
    are descriptive historical evidence, not current-role authority.
    This query neither admits a principal nor trusts a client-provided name.
    Legacy ObjectId identity is accepted only when it matches the same exact
    tenant and no colliding canonical user identity is found. Absent optional
    profile names remain null; never infer them from email, IDs or session.
    """
    selectors: list[dict[str, object]] = [{"user_id": principal_id}]
    if re.fullmatch(r"[0-9a-fA-F]{24}", principal_id):
        selectors.append({"_id": ObjectId(principal_id)})
    try:
        profiles = list(database["users"].find(
            {"tenantId": tenant_id, "$or": selectors},
            {"_id": 0, "user_id": 1, "firstName": 1, "lastName": 1,
             "tenantId": 1},
            session=session,
        ).limit(2))
    except PyMongoError as error:
        raise HTTPException(
            status_code=503, detail="PROJECT_OWNER_PROFILE_UNAVAILABLE",
        ) from error
    if len(profiles) > 1:
        raise HTTPException(
            status_code=503, detail="PROJECT_OWNER_PROFILE_COLLISION",
        )
    profile = profiles[0] if profiles else {}
    if profile and (
        profile.get("tenantId") != tenant_id
        or (profile.get("user_id") is not None
            and profile.get("user_id") != principal_id)
    ):
        raise HTTPException(
            status_code=503, detail="PROJECT_OWNER_PROFILE_INVALID",
        )
    def optional(value: object) -> str | None:
        return value if (
            isinstance(value, str) and 0 < len(value) <= 100
            and value == value.strip()
        ) else None

    return {
        "first_name": optional(profile.get("firstName")),
        "last_name": optional(profile.get("lastName")),
    }


@router.get("/assignment-options")
def project_assignment_options(
    response: Response,
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, object]:
    """Read verified tenant-owner candidates and active canonical departments.

    Results only suggest valid choices. Assignment independently rechecks each
    source inside its write transaction. No directory value creates a grant.
    """
    response.headers["Cache-Control"] = "no-store"
    def read(_registry: ProjectRegistry, session: Any) -> dict[str, object]:
        database = kernel_db.get_database()
        if database is None:
            raise HTTPException(status_code=503, detail="PROJECT_ASSIGNMENT_SOURCE_UNAVAILABLE")
        try:
            members = list(
                database["tenant_memberships"].find(
                    {"tenant_id": context.tenant_id, "status": "ACTIVE"},
                    {"_id": 0, "principal_id": 1}, session=session,
                ).sort("principal_id", 1).limit(101)
            )
            departments = list(
                database[_DEPARTMENT_COLLECTION].find(
                    {"tenant_id": context.tenant_id, "status": "ACTIVE"},
                    {"_id": 0, "tenant_id": 1, "department_id": 1,
                     "name": 1, "revision": 1, "status": 1},
                    session=session,
                ).sort("department_id", 1).limit(101)
            )
        except PyMongoError as error:
            raise HTTPException(status_code=503, detail="PROJECT_ASSIGNMENT_SOURCE_UNAVAILABLE") from error
        if len(members) > 100 or len(departments) > 100:
            raise HTTPException(status_code=503, detail="PROJECT_ASSIGNMENT_DIRECTORY_PAGE_REQUIRED")
        candidates: list[dict[str, object]] = []
        for member in members:
            principal_id = member.get("principal_id")
            if not isinstance(principal_id, str):
                raise HTTPException(status_code=503, detail="PROJECT_MEMBER_RECORD_INVALID")
            if _project_owner_eligible(database, context.tenant_id, principal_id, session):
                candidates.append({
                    "principal_id": principal_id,
                    "eligibility": "VERIFIED_CURRENT",
                    **_exact_tenant_project_person_name(
                        database, context.tenant_id, principal_id, session,
                    ),
                })
        values: list[dict[str, object]] = []
        for department in departments:
            department_id = department.get("department_id")
            if not isinstance(department_id, str):
                raise HTTPException(status_code=503, detail="PROJECT_DEPARTMENT_RECORD_INVALID")
            values.append(_current_department(database, context.tenant_id, department_id, session))
        return {
            "schema": "WILSY-PROJECT-ASSIGNMENT-OPTIONS/V1",
            "tenant_id": context.tenant_id,
            "principals": candidates,
            "departments": values,
            "source": "EOS_CURRENT_IAM_AND_TENANT_DEPARTMENTS",
        }
    return _transaction(context, read)


@router.post("/departments", status_code=status.HTTP_201_CREATED)
def provision_project_department(
    payload: DepartmentCreateRequest,
    response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_DEPARTMENT_PROVISION),
    project_context: TenantAuthorizationContext = Depends(_CREATE),
) -> dict[str, object]:
    """Provision a canonical tenant department with conjunctive, distinct IAM.

    Profile-write and Projects-create authority are both revalidated by EOS;
    records and immutable command evidence commit in one caller-owned majority
    transaction. Identical keyed retries read the exact persisted result.
    """
    response.headers["Cache-Control"] = "no-store"
    if context.tenant_id != project_context.tenant_id or context.identity.identity_id != project_context.identity.identity_id:
        raise HTTPException(status_code=403, detail="PROJECT_DEPARTMENT_AUTHORITY_MISMATCH")
    if not isinstance(idempotency_key, str) or not 1 <= len(idempotency_key) <= 200 or idempotency_key != idempotency_key.strip():
        raise HTTPException(status_code=422, detail="PROJECT_IDEMPOTENCY_KEY_INVALID")
    name = payload.name.strip()
    if len(name) < 2 or name != payload.name:
        raise HTTPException(status_code=422, detail="PROJECT_DEPARTMENT_NAME_INVALID")
    department_id = "dept-" + hashlib.sha3_512(
        (context.tenant_id + "\0" + name.casefold()).encode("utf-8"),
    ).hexdigest()[:32]
    digest = hashlib.sha3_512(
        (context.tenant_id + "\0" + context.identity.identity_id + "\0" + name + "\0" + idempotency_key).encode("utf-8"),
    ).hexdigest()
    def create(_registry: ProjectRegistry, session: Any) -> dict[str, object]:
        database = kernel_db.get_database()
        if database is None:
            raise HTTPException(status_code=503, detail="PROJECT_DEPARTMENT_SOURCE_UNAVAILABLE")
        collection = database[_DEPARTMENT_COLLECTION]
        events = database[_DEPARTMENT_EVENTS_COLLECTION]
        event_id = context.tenant_id + ":" + idempotency_key
        try:
            previous = events.find_one(
                {"_id": event_id, "tenant_id": context.tenant_id}, session=session,
            )
            if previous is not None:
                if previous.get("request_fingerprint") != digest or previous.get("department_id") != department_id:
                    raise HTTPException(status_code=409, detail="PROJECT_DEPARTMENT_DIVERGENT_REPLAY")
                value = _current_department(database, context.tenant_id, department_id, session)
                return {"tenant_id": context.tenant_id, "department": value, "replayed": False}
            record = {
                "_id": context.tenant_id + ":" + department_id,
                "tenant_id": context.tenant_id, "department_id": department_id,
                "name": name, "revision": 1, "status": "ACTIVE",
                "created_by_principal_id": context.identity.identity_id,
                "created_at": datetime.now(timezone.utc),
            }
            collection.insert_one(record, session=session)
            events.insert_one({
                "_id": event_id, "tenant_id": context.tenant_id,
                "department_id": department_id, "event_type": "DEPARTMENT_CREATED",
                "actor_principal_id": context.identity.identity_id,
                "request_fingerprint": digest,
                "result_fingerprint": hashlib.sha3_512(
                    (department_id + "\0" + name).encode("utf-8")
                ).hexdigest(),
                "revision": 1, "occurred_at": record["created_at"],
            }, session=session)
            value = _current_department(database, context.tenant_id, department_id, session)
            return {"tenant_id": context.tenant_id, "department": value, "replayed": False}
        except DuplicateKeyError as error:
            raise HTTPException(status_code=409, detail="PROJECT_DEPARTMENT_ALREADY_EXISTS") from error
        except PyMongoError as error:
            raise HTTPException(status_code=503, detail="PROJECT_DEPARTMENT_SOURCE_UNAVAILABLE") from error
    return _transaction(context, create, write=True)


@router.patch("/{project_id}/assignment")
def assign_project_accountability(
    payload: ProjectAssignmentRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Assign source-verified owner and department with audited CAS/readback.

    Caller IAM authorizes the command; assignee membership and role establish
    eligibility only. This command does not activate the project or create IAM.
    """
    response.headers["Cache-Control"] = "no-store"
    if not isinstance(idempotency_key, str) or not 1 <= len(idempotency_key) <= 200 or idempotency_key != idempotency_key.strip():
        raise HTTPException(status_code=422, detail="PROJECT_IDEMPOTENCY_KEY_INVALID")
    now = datetime.now(timezone.utc)
    def assign(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        database = kernel_db.get_database()
        if database is None:
            raise HTTPException(status_code=503, detail="PROJECT_ASSIGNMENT_SOURCE_UNAVAILABLE")
        if not _project_owner_eligible(database, context.tenant_id, payload.owner_principal_id, session):
            raise HTTPException(status_code=409, detail="PROJECT_OWNER_NOT_ELIGIBLE")
        _current_department(database, context.tenant_id, payload.department_id, session)
        updated = registry.update(
            tenant_id=context.tenant_id, project_id=project_id,
            actor_principal_id=context.identity.identity_id,
            expected_revision=payload.expected_revision,
            changes={"owner_principal_id": payload.owner_principal_id,
                     "department_id": payload.department_id},
            idempotency_key=idempotency_key, occurred_at=now, session=session,
        )
        readback = registry.get(
            tenant_id=context.tenant_id, project_id=project_id, session=session,
        )
        if readback.fingerprint != updated.fingerprint or (
            readback.owner_principal_id != payload.owner_principal_id
            or readback.department_id != payload.department_id
        ):
            raise ProjectRegistryError("PROJECT_ASSIGNMENT_READBACK_MISMATCH")
        return _result(
            context, readback,
            events=registry.list_events(
                tenant_id=context.tenant_id, project_id=project_id, session=session,
            ),
        )
    return _transaction(context, assign, write=True)


def _project_note_store(
    registry: ProjectRegistry, tenant_id: str,
    project_id: str, session: Any,
) -> ProjectNoteRegistry:
    """Require current readable project before resolving the notes collection."""
    registry.get(tenant_id=tenant_id, project_id=project_id, session=session)
    database = kernel_db.get_database()
    if database is None:
        raise ProjectNoteRegistryError("PROJECT_NOTE_SOURCE_UNAVAILABLE")
    return ProjectNoteRegistry(
        database.get_collection(PROJECT_NOTE_COLLECTION),
        database.get_collection(PROJECT_NOTE_EVENT_COLLECTION),
    )


def _project_note_result(
    context: TenantAuthorizationContext, project_id: str, note: ProjectNote,
    *, events: tuple[dict[str, object], ...] = (),
) -> dict[str, object]:
    """Expose source-backed note state without creating approval authority."""
    return {
        "schema": "WILSY-PROJECT-NOTE-RESULT/V1",
        "tenant_id": context.tenant_id,
        "principal_id": context.identity.identity_id,
        "project_id": project_id,
        "note": note.to_dict(),
        "events": list(events),
    }


def _note_idempotency_key(key: str | None) -> str:
    """Validate nonblank bounded replay keys; never generate them in the router."""
    if not isinstance(key, str) or not 1 <= len(key) <= 200 or key != key.strip():
        raise HTTPException(status_code=422, detail="PROJECT_NOTE_IDEMPOTENCY_KEY_INVALID")
    return key


def _project_participants(
    registry: ProjectRegistry, tenant_id: str, project_id: str, session: Any,
) -> ProjectParticipantRegistry:
    """Resolve an already-authorized project before exposing participant records."""
    registry.get(tenant_id=tenant_id, project_id=project_id, session=session)
    database = kernel_db.get_database()
    if database is None:
        raise ProjectParticipantError("PROJECT_PARTICIPANT_SOURCE_UNAVAILABLE")
    return ProjectParticipantRegistry(
        database[PROJECT_PARTICIPANT_COLLECTION],
        database[PROJECT_PARTICIPANT_EVENT_COLLECTION],
    )


def _require_current_project_participation(
    context: TenantAuthorizationContext, registry: ProjectRegistry,
    project_id: str, session: Any, *, contribute: bool = False,
) -> tuple[Project, ProjectParticipantRegistry]:
    """Join current IAM to one ACTIVE exact-project participant assignment.

    Never infer participant scope from project ownership, workforce employment,
    founder status or tenant-wide module entitlements. Each command revalidates
    current membership and active role through RequireTenantAuthorization,
    product entitlement through _transaction and explicit record here.
    """
    if context.decision.authorization_role not in {
        "PROJECTS_PARTICIPANT_VIEWER", "PROJECTS_PARTICIPANT_CONTRIBUTOR",
    }:
        raise HTTPException(status_code=403, detail="PROJECT_PARTICIPANT_IAM_REQUIRED")
    project = registry.get(
        tenant_id=context.tenant_id, project_id=project_id, session=session,
    )
    participants = _project_participants(
        registry, context.tenant_id, project_id, session,
    )
    participant = participants.get(
        tenant_id=context.tenant_id, project_id=project_id,
        principal_id=context.identity.identity_id, session=session,
    )
    if contribute and (
        participant.role != "CONTRIBUTOR"
        or context.decision.authorization_role != "PROJECTS_PARTICIPANT_CONTRIBUTOR"
    ):
        raise HTTPException(status_code=403, detail="PROJECT_CONTRIBUTOR_SCOPE_REQUIRED")
    return project, participants


def _project_task_store(
    registry: ProjectRegistry, tenant_id: str, project_id: str, session: Any,
) -> ProjectTaskRegistry:
    """Require an existing exact-tenant project before accessing project work."""
    registry.get(tenant_id=tenant_id, project_id=project_id, session=session)
    database = kernel_db.get_database()
    if database is None:
        raise ProjectTaskError("PROJECT_TASK_SOURCE_UNAVAILABLE")
    return ProjectTaskRegistry(
        database[PROJECT_TASK_COLLECTION], database[PROJECT_TASK_EVENT_COLLECTION],
    )


def _task_result(
    context: TenantAuthorizationContext, project_id: str, task: ProjectTask,
) -> dict[str, object]:
    """Expose only persisted task state with an exact authenticated envelope."""
    return {
        "schema": "WILSY-PROJECT-TASK-RESULT/V1",
        "tenant_id": context.tenant_id,
        "principal_id": context.identity.identity_id,
        "project_id": project_id, "task": task.to_dict(),
    }


def _list_project_tasks(
    context: TenantAuthorizationContext, project_id: str,
    registry: ProjectRegistry, session: Any, limit: int, offset: int,
) -> dict[str, object]:
    """Return one bounded page; caller must already satisfy project visibility."""
    tasks = _project_task_store(registry, context.tenant_id, project_id, session)
    items, more = tasks.list_page(
        tenant_id=context.tenant_id, project_id=project_id,
        session=session, limit=limit, offset=offset,
    )
    return {
        "schema": "WILSY-PROJECT-TASK-LIST/V1",
        "tenant_id": context.tenant_id,
        "principal_id": context.identity.identity_id,
        "project_id": project_id, "items": [item.to_dict() for item in items],
        "limit": limit, "offset": offset, "has_more": more,
        "next_offset": offset + len(items) if more else None,
    }


def _project_comment_store(
    registry: ProjectRegistry, tenant_id: str,
    project_id: str, task_id: str, session: Any,
) -> ProjectCommentRegistry:
    """Check one real project and task before resolving their comment timeline."""
    _project_task_store(registry, tenant_id, project_id, session).get(
        tenant_id=tenant_id, project_id=project_id,
        task_id=task_id, session=session,
    )
    database = kernel_db.get_database()
    if database is None:
        raise ProjectCommentError("PROJECT_COMMENT_SOURCE_UNAVAILABLE")
    return ProjectCommentRegistry(
        database[PROJECT_COMMENT_COLLECTION],
        database[PROJECT_COMMENT_EVENT_COLLECTION],
    )


def _list_project_comments(
    context: TenantAuthorizationContext, registry: ProjectRegistry,
    project_id: str, task_id: str, session: Any,
    limit: int, offset: int,
) -> dict[str, object]:
    """Return one source-authorized exact-project/task comment page."""
    store = _project_comment_store(
        registry, context.tenant_id, project_id, task_id, session,
    )
    items, has_more = store.list_page(
        tenant_id=context.tenant_id, project_id=project_id,
        task_id=task_id, limit=limit, offset=offset, session=session,
    )
    return {
        "schema": "WILSY-PROJECT-COMMENT-LIST/V1",
        "tenant_id": context.tenant_id,
        "principal_id": context.identity.identity_id,
        "project_id": project_id, "task_id": task_id,
        "items": [item.to_dict() for item in items],
        "limit": limit, "offset": offset, "has_more": has_more,
        "next_offset": offset + len(items) if has_more else None,
    }


def _create_project_comment(
    context: TenantAuthorizationContext, registry: ProjectRegistry,
    project_id: str, task_id: str, payload: ProjectTaskCommentRequest,
    idempotency_key: str, session: Any,
) -> dict[str, object]:
    """Persist a comment only after independent current mention membership checks."""
    store = _project_comment_store(
        registry, context.tenant_id, project_id, task_id, session,
    )
    participants = _project_participants(
        registry, context.tenant_id, project_id, session,
    )
    database = kernel_db.get_database()
    if database is None:
        raise ProjectCommentError("PROJECT_COMMENT_SOURCE_UNAVAILABLE")
    for principal in payload.mentions:
        if not _project_participant_eligible(
            database, context.tenant_id, principal, session,
        ):
            raise HTTPException(status_code=409, detail="PROJECT_COMMENT_MENTION_NOT_CURRENT")
        participants.get(
            tenant_id=context.tenant_id, project_id=project_id,
            principal_id=principal, session=session,
        )
    actor = context.identity.identity_id
    comment = ProjectComment(
        tenant_id=context.tenant_id, project_id=project_id,
        task_id=task_id,
        comment_id=comment_id_for_command(
            context.tenant_id, project_id, task_id, actor, idempotency_key,
        ),
        author_principal_id=actor, body=payload.body,
        mentions=tuple(payload.mentions), created_at=datetime.now(timezone.utc),
    )
    stored = store.create_or_replay(
        comment=comment, actor_principal_id=actor,
        idempotency_key=idempotency_key, session=session,
    )
    notification_store = ProjectNotificationRegistry(
        database[PROJECT_NOTIFICATION_COLLECTION],
        database[PROJECT_NOTIFICATION_EVENT_COLLECTION],
    )
    notification_store.append_for_comment(comment=stored, session=session)
    return {
        "schema": "WILSY-PROJECT-COMMENT-RESULT/V1",
        "tenant_id": context.tenant_id,
        "principal_id": actor, "project_id": project_id,
        "task_id": task_id, "comment": stored.to_dict(),
    }


def _project_notification_store(
    registry: ProjectRegistry, tenant_id: str, project_id: str, session: Any,
) -> ProjectNotificationRegistry:
    """Require exact-project existence before recipient-scoped inbox reads."""
    registry.get(tenant_id=tenant_id, project_id=project_id, session=session)
    database = kernel_db.get_database()
    if database is None:
        raise ProjectNotificationError("PROJECT_NOTIFICATION_SOURCE_UNAVAILABLE")
    return ProjectNotificationRegistry(
        database[PROJECT_NOTIFICATION_COLLECTION],
        database[PROJECT_NOTIFICATION_EVENT_COLLECTION],
    )


@router.get("/{project_id}/my-project/participants")
def list_my_project_participants(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_DETAIL),
) -> dict[str, object]:
    """Read co-participant identities after the caller's current record gate."""
    response.headers["Cache-Control"] = "no-store"

    def read(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        _require_current_project_participation(context, registry, project_id, session)
        participants = _project_participants(
            registry, context.tenant_id, project_id, session,
        )
        items, more = participants.page(
            tenant_id=context.tenant_id, project_id=project_id,
            session=session, limit=limit, offset=offset,
        )
        return {
            "schema": "WILSY-PROJECT-PARTICIPANT-LIST/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "project_id": project_id,
            "items": [item.to_dict() for item in items],
            "limit": limit, "offset": offset, "has_more": more,
            "next_offset": offset + len(items) if more else None,
        }

    return _transaction(context, read)


@router.get("/{project_id}/my-project/notifications")
def list_my_project_notifications(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_DETAIL),
) -> dict[str, object]:
    """Read only this exact principal's project mentions while currently admitted."""
    response.headers["Cache-Control"] = "no-store"

    def read(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        _require_current_project_participation(context, registry, project_id, session)
        notifications = _project_notification_store(
            registry, context.tenant_id, project_id, session,
        )
        items, more = notifications.list_for_recipient(
            tenant_id=context.tenant_id, project_id=project_id,
            recipient_principal_id=context.identity.identity_id,
            limit=limit, offset=offset, session=session,
        )
        return {
            "schema": "WILSY-PROJECT-NOTIFICATION-LIST/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "project_id": project_id,
            "items": [item.to_dict() for item in items],
            "limit": limit, "offset": offset,
            "has_more": more,
            "next_offset": offset + len(items) if more else None,
        }

    return _transaction(context, read)


@router.post("/{project_id}/my-project/notifications/{notification_id}/read")
def read_my_project_notification(
    payload: ProjectNotificationReadRequest, response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    notification_id: str = Path(pattern=r"^pnf-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_DETAIL),
) -> dict[str, object]:
    """Mark one recipient-only in-app signal read, without approving any work."""
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)

    def write(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        _require_current_project_participation(context, registry, project_id, session)
        notifications = _project_notification_store(
            registry, context.tenant_id, project_id, session,
        )
        result = notifications.mark_read(
            tenant_id=context.tenant_id, project_id=project_id,
            recipient_principal_id=context.identity.identity_id,
            notification_id=notification_id,
            expected_revision=payload.expected_revision,
            idempotency_key=key, occurred_at=datetime.now(timezone.utc),
            session=session,
        )
        return {
            "schema": "WILSY-PROJECT-NOTIFICATION-RESULT/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "project_id": project_id,
            "notification": result.to_dict(),
        }

    return _transaction(context, write, write=True)


def _project_approval_store(
    registry: ProjectRegistry, tenant_id: str, project_id: str,
    task_id: str, session: Any,
) -> ProjectApprovalRegistry:
    """Require an existing task before exposing independent review evidence."""
    _project_task_store(registry, tenant_id, project_id, session).get(
        tenant_id=tenant_id, project_id=project_id, task_id=task_id,
        session=session,
    )
    database = kernel_db.get_database()
    if database is None:
        raise ProjectApprovalError("PROJECT_APPROVAL_SOURCE_UNAVAILABLE")
    return ProjectApprovalRegistry(
        database[PROJECT_APPROVAL_COLLECTION],
        database[PROJECT_APPROVAL_EVENT_COLLECTION],
    )


def _approval_result(
    context: TenantAuthorizationContext, project_id: str, task_id: str,
    approval: ProjectApproval,
) -> dict[str, object]:
    """Return authoritative business decision state, never task completion."""
    return {
        "schema": "WILSY-PROJECT-APPROVAL-RESULT/V1",
        "tenant_id": context.tenant_id,
        "principal_id": context.identity.identity_id,
        "project_id": project_id, "task_id": task_id,
        "approval": approval.to_dict(),
    }


def _approval_page(
    context: TenantAuthorizationContext, project_id: str, task_id: str,
    registry: ProjectRegistry, session: Any, limit: int, offset: int,
) -> dict[str, object]:
    """Project/task-scoped approval timeline under previously checked IAM."""
    store = _project_approval_store(
        registry, context.tenant_id, project_id, task_id, session,
    )
    items, more = store.list_page(
        tenant_id=context.tenant_id, project_id=project_id,
        task_id=task_id, session=session, limit=limit, offset=offset,
    )
    return {
        "schema": "WILSY-PROJECT-APPROVAL-LIST/V1",
        "tenant_id": context.tenant_id,
        "principal_id": context.identity.identity_id,
        "project_id": project_id, "task_id": task_id,
        "items": [item.to_dict() for item in items],
        "offset": offset, "limit": limit, "has_more": more,
        "next_offset": offset + len(items) if more else None,
    }


def _project_attachment_store(
    registry: ProjectRegistry, tenant_id: str, project_id: str,
    task_id: str, session: Any,
) -> ProjectAttachmentRegistry:
    """Check exact source task existence before accessing quarantined manifests."""
    _project_task_store(registry, tenant_id, project_id, session).get(
        tenant_id=tenant_id, project_id=project_id,
        task_id=task_id, session=session,
    )
    database = kernel_db.get_database()
    if database is None:
        raise ProjectAttachmentError("PROJECT_ATTACHMENT_SOURCE_UNAVAILABLE")
    return ProjectAttachmentRegistry(
        database[PROJECT_ATTACHMENT_COLLECTION],
        database[PROJECT_ATTACHMENT_EVENT_COLLECTION],
    )


def _attachment_projection(attachment: ProjectAttachment) -> dict[str, object]:
    """Redact opaque storage receipt and any capability/provider coordinates."""
    record = attachment.to_dict()
    record.pop("storage_receipt")
    record.pop("fingerprint")
    record["scan_clearance_status"] = "QUARANTINED"
    record["scan_clearance_fingerprint"] = None
    return record


def _attachment_page(
    context: TenantAuthorizationContext, project_id: str, task_id: str,
    registry: ProjectRegistry, session: Any, limit: int, offset: int,
) -> dict[str, object]:
    """Present bounded quarantined task manifest metadata, not safe files."""
    items, more = _project_attachment_store(
        registry, context.tenant_id, project_id, task_id, session,
    ).list_page(
        tenant_id=context.tenant_id, project_id=project_id,
        task_id=task_id, session=session, limit=limit, offset=offset,
    )
    clearances = _project_attachment_clearances(
        registry, context.tenant_id, project_id, task_id, session,
    )
    rendered: list[dict[str, object]] = []
    for item in items:
        visible = _attachment_projection(item)
        try:
            verified = clearances.get(
                tenant_id=context.tenant_id,
                project_id=project_id, task_id=task_id,
                attachment_id=item.attachment_id, session=session,
            )
        except ProjectAttachmentClearanceNotFound:
            pass
        else:
            if verified.attachment_fingerprint != item.fingerprint:
                raise ProjectAttachmentClearanceError(
                    "PROJECT_ATTACHMENT_CLEARANCE_SOURCE_MISMATCH",
                )
            visible["scan_clearance_status"] = "SCAN_CLEAN_VERIFIED"
            visible["scan_clearance_fingerprint"] = verified.fingerprint
        rendered.append(visible)
    return {
        "schema": "WILSY-PROJECT-ATTACHMENT-LIST/V1",
        "tenant_id": context.tenant_id,
        "principal_id": context.identity.identity_id,
        "project_id": project_id, "task_id": task_id,
        "items": rendered,
        "limit": limit, "offset": offset, "has_more": more,
        "next_offset": offset + len(items) if more else None,
    }


@router.get("/{project_id}/tasks/{task_id}/attachments")
def list_owner_project_task_attachments(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_DETAIL),
) -> dict[str, object]:
    """Expose redacted exact-task metadata only to authorized project owner."""
    response.headers["Cache-Control"] = "no-store"
    return _profiled_projects_get(context, "TASK_ATTACHMENTS", lambda registry, session: _attachment_page(
        context, project_id, task_id, registry, session, limit, offset,
    ))


@router.get("/{project_id}/my-project/tasks/{task_id}/attachments")
def list_participant_project_task_attachments(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_DETAIL),
) -> dict[str, object]:
    """Require ACTIVE project participation before exposing quarantined files."""
    response.headers["Cache-Control"] = "no-store"

    def read(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        _require_current_project_participation(context, registry, project_id, session)
        return _attachment_page(
            context, project_id, task_id, registry, session, limit, offset,
        )

    return _transaction(context, read)


@router.post("/{project_id}/my-project/tasks/{task_id}/attachments", status_code=status.HTTP_201_CREATED)
async def upload_participant_project_attachment(
    request: Request, response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    content_length: int | None = Header(default=None, alias="Content-Length"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_CONTRIBUTE),
) -> dict[str, object]:
    """Accept bounded bytes in encrypted quarantine; never approve or download.

    The exact participant and task are rechecked in snapshot/majority Mongo
    before AND after the external S3 write. Provider receipt is server-only.
    A provider success followed by Mongo failure remains inaccessible
    quarantine; later exact-key replay reconciles the immutable S3 object.
    """
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)
    if (
        content_length is None or content_length <= 0
        or content_length > MAX_ATTACHMENT_BYTES + 1024 * 1024
    ):
        raise HTTPException(status_code=413, detail="PROJECT_ATTACHMENT_MULTIPART_SIZE_INVALID")

    def authorize(registry: ProjectRegistry, session: Any) -> None:
        _require_current_project_participation(
            context, registry, project_id, session, contribute=True,
        )
        _project_task_store(
            registry, context.tenant_id, project_id, session,
        ).get(
            tenant_id=context.tenant_id, project_id=project_id,
            task_id=task_id, session=session,
        )

    _transaction(context, authorize)
    try:
        form = await request.form(
            max_files=1, max_fields=0, max_part_size=MAX_ATTACHMENT_BYTES,
        )
    except Exception as error:
        raise HTTPException(status_code=422, detail="PROJECT_ATTACHMENT_MULTIPART_INVALID") from error
    if list(form.keys()) != ["file"]:
        raise HTTPException(status_code=422, detail="PROJECT_ATTACHMENT_MULTIPART_FIELDS_INVALID")
    file = form.get("file")
    if not isinstance(file, UploadFile):
        raise HTTPException(status_code=422, detail="PROJECT_ATTACHMENT_FILE_REQUIRED")
    name = file.filename or ""
    media_type = (file.content_type or "").split(";", 1)[0].strip().lower()
    if (
        not name or name != name.strip() or len(name) > 255
        or name.startswith(".") or "/" in name or "\\" in name
        or any(ord(char) < 32 for char in name)
        or media_type not in {"application/pdf", "image/png", "image/jpeg"}
    ):
        raise HTTPException(status_code=422, detail="PROJECT_ATTACHMENT_FILE_INVALID")
    try:
        file.file.seek(0, 2)
        measured = file.file.tell()
        file.file.seek(0)
        if measured <= 0 or measured > MAX_ATTACHMENT_BYTES:
            raise HTTPException(status_code=413, detail="PROJECT_ATTACHMENT_SIZE_INVALID")
        try:
            size, digest, receipt = store_quarantined_attachment(
                tenant_id=context.tenant_id, project_id=project_id,
                task_id=task_id, uploader_principal_id=context.identity.identity_id,
                idempotency_key=key, media_type=media_type,
                content_length=measured, stream=file.file,
            )
        except ProjectAttachmentStorageError as error:
            raise HTTPException(status_code=503, detail=error.code) from error
    finally:
        await file.close()

    def commit(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        authorize(registry, session)
        attachment = ProjectAttachment(
            tenant_id=context.tenant_id, project_id=project_id,
            task_id=task_id,
            attachment_id=attachment_id_for_command(
                context.tenant_id, project_id, task_id,
                context.identity.identity_id, key,
            ),
            uploader_principal_id=context.identity.identity_id,
            filename=name, media_type=media_type,
            size_bytes=size, content_sha3_512=digest,
            storage_receipt=receipt,
            created_at=datetime.now(timezone.utc),
        )
        stored = _project_attachment_store(
            registry, context.tenant_id, project_id, task_id, session,
        ).create_or_replay(
            attachment=attachment, idempotency_key=key, session=session,
        )
        return {
            "schema": "WILSY-PROJECT-ATTACHMENT-RESULT/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "project_id": project_id, "task_id": task_id,
            "attachment": _attachment_projection(stored),
        }

    return _transaction(context, commit, write=True)


def _project_attachment_clearances(
    registry: ProjectRegistry, tenant_id: str, project_id: str,
    task_id: str, session: Any,
) -> ProjectAttachmentClearanceRegistry:
    """Resolve a current task before accessing independently verified scans."""
    _project_attachment_store(
        registry, tenant_id, project_id, task_id, session,
    )
    database = kernel_db.get_database()
    if database is None:
        raise ProjectAttachmentClearanceError("PROJECT_ATTACHMENT_CLEARANCE_SOURCE_UNAVAILABLE")
    return ProjectAttachmentClearanceRegistry(
        database[PROJECT_ATTACHMENT_CLEARANCE_COLLECTION],
        database[PROJECT_ATTACHMENT_CLEARANCE_EVENT_COLLECTION],
    )


def _require_cleared_project_attachment(
    registry: ProjectRegistry, tenant_id: str, project_id: str,
    task_id: str, attachment_id: str, session: Any,
) -> tuple[ProjectAttachment, ProjectAttachmentClearance]:
    """Bind immutable source manifest to its independently verified clean scan."""
    manifest = _project_attachment_store(
        registry, tenant_id, project_id, task_id, session,
    ).get(
        tenant_id=tenant_id, project_id=project_id,
        task_id=task_id, attachment_id=attachment_id, session=session,
    )
    clearance = _project_attachment_clearances(
        registry, tenant_id, project_id, task_id, session,
    ).get(
        tenant_id=tenant_id, project_id=project_id,
        task_id=task_id, attachment_id=attachment_id, session=session,
    )
    if clearance.attachment_fingerprint != manifest.fingerprint:
        raise ProjectAttachmentClearanceError("PROJECT_ATTACHMENT_CLEARANCE_SOURCE_MISMATCH")
    return manifest, clearance


def _fresh_project_approval_evidence(
    context: TenantAuthorizationContext, project_id: str, task_id: str,
    attachment_ids: tuple[str, ...], *, participant: bool,
) -> dict[str, tuple[str, str]]:
    """Revalidate original clean evidence without external I/O in a Mongo transaction.

    The caller's already-admitted tenant context and exact task are read in a
    separate source snapshot; the trusted S3 policy, version, KMS metadata and
    GuardDuty clean tag are inspected outside its transaction. The returned
    immutable manifest/clearance fingerprints MUST be compared again inside the
    subsequent command transaction. This is a bounded observation, not a
    signature, legal validity finding, authorization to release funds, or a
    guarantee against a provider policy change after the command commits.
    """
    if not attachment_ids:
        return {}
    if len(attachment_ids) > 10 or len(set(attachment_ids)) != len(attachment_ids):
        raise HTTPException(status_code=422, detail="PROJECT_APPROVAL_EVIDENCE_INVALID")
    if any(re.fullmatch(r"pat-[0-9a-f]{48}", identifier) is None
           for identifier in attachment_ids):
        raise HTTPException(status_code=422, detail="PROJECT_APPROVAL_EVIDENCE_ID_INVALID")

    def source(registry: ProjectRegistry, session: Any) -> tuple[
        tuple[ProjectAttachment, ProjectAttachmentClearance], ...
    ]:
        if participant:
            _require_current_project_participation(
                context, registry, project_id, session, contribute=True,
            )
        return tuple(
            _require_cleared_project_attachment(
                registry, context.tenant_id, project_id, task_id,
                identifier, session,
            ) for identifier in attachment_ids
        )

    originals = _transaction(context, source)
    evidence: dict[str, tuple[str, str]] = {}
    for manifest, clearance in originals:
        try:
            policy_sha3, scan_sha3 = verify_guardduty_clean_attachment(manifest)
        except ProjectAttachmentStorageError as error:
            raise HTTPException(status_code=503, detail=error.code) from error
        if (
            policy_sha3 != clearance.policy_sha3_512
            or scan_sha3 != clearance.scan_evidence_sha3_512
        ):
            raise HTTPException(
                status_code=409, detail="PROJECT_APPROVAL_EVIDENCE_PROVIDER_CHANGED",
            )
        evidence[manifest.attachment_id] = (
            manifest.fingerprint, clearance.fingerprint,
        )
    return evidence


def _download_project_attachment(
    context: TenantAuthorizationContext, project_id: str, task_id: str,
    attachment_id: str, *, participant: bool,
) -> Response:
    """Return safe-by-policy bytes only after two fresh authorization snapshots.

    External S3 read does not hold open MongoDB transactions. A second
    source read gates the response after the provider byte digest is checked.
    No raw provider keys, object versions or presigned links are exposed.
    """
    def scoped(registry: ProjectRegistry, session: Any) -> ProjectAttachment:
        if participant:
            _require_current_project_participation(
                context, registry, project_id, session,
            )
        manifest, _clearance = _require_cleared_project_attachment(
            registry, context.tenant_id, project_id,
            task_id, attachment_id, session,
        )
        return manifest

    original = _transaction(context, scoped)
    try:
        content = read_verified_scanned_attachment(original)
    except ProjectAttachmentStorageError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    current = _transaction(context, scoped)
    if current.fingerprint != original.fingerprint:
        raise HTTPException(status_code=409, detail="PROJECT_ATTACHMENT_SOURCE_CHANGED")
    safe_filename = re.sub(r"[^A-Za-z0-9._-]", "_", original.filename)
    return Response(
        content=content,
        media_type=original.media_type,
        headers={
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "sandbox",
            "Content-Disposition": 'attachment; filename="' + safe_filename + '"',
        },
    )


@router.get("/{project_id}/tasks/{task_id}/attachments/{attachment_id}/download")
def download_owner_project_attachment(
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    attachment_id: str = Path(pattern=r"^pat-[0-9a-f]{48}$"),
    context: TenantAuthorizationContext = Depends(_DETAIL),
) -> Response:
    """Read exact clean task bytes under current independently admitted owner."""
    return _download_project_attachment(
        context, project_id, task_id, attachment_id, participant=False,
    )


@router.get("/{project_id}/my-project/tasks/{task_id}/attachments/{attachment_id}/download")
def download_participant_project_attachment(
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    attachment_id: str = Path(pattern=r"^pat-[0-9a-f]{48}$"),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_DETAIL),
) -> Response:
    """Read clean bytes only with current exact-project participant admission."""
    return _download_project_attachment(
        context, project_id, task_id, attachment_id, participant=True,
    )


@router.post("/{project_id}/my-project/tasks/{task_id}/attachments/{attachment_id}/verify-scan")
def reconcile_project_attachment_guardduty_scan(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    attachment_id: str = Path(pattern=r"^pat-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_CONTRIBUTE),
) -> dict[str, object]:
    """Observe clean scanner evidence only under exact live object/policy proof.

    Storage inspection runs OUTSIDE MongoDB transaction; authorization and
    attachment fingerprint are checked before and after. No request body
    supplies scanner status, provider version, trust policy or verdict.
    """
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)

    def current(registry: ProjectRegistry, session: Any) -> ProjectAttachment:
        _require_current_project_participation(
            context, registry, project_id, session, contribute=True,
        )
        return _project_attachment_store(
            registry, context.tenant_id, project_id, task_id, session,
        ).get(
            tenant_id=context.tenant_id, project_id=project_id,
            task_id=task_id, attachment_id=attachment_id, session=session,
        )

    manifest = _transaction(context, current)
    try:
        pinned_policy, scan_digest = verify_guardduty_clean_attachment(manifest)
    except ProjectAttachmentStorageError as error:
        raise HTTPException(status_code=503, detail=error.code) from error

    def record(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        observed = current(registry, session)
        if observed.fingerprint != manifest.fingerprint:
            raise ProjectAttachmentClearanceError("PROJECT_ATTACHMENT_CLEARANCE_SOURCE_CHANGED")
        result = _project_attachment_clearances(
            registry, context.tenant_id, project_id, task_id, session,
        ).record_or_replay(
            clearance=ProjectAttachmentClearance(
                tenant_id=context.tenant_id, project_id=project_id,
                task_id=task_id, attachment_id=attachment_id,
                attachment_fingerprint=manifest.fingerprint,
                policy_sha3_512=pinned_policy,
                scan_evidence_sha3_512=scan_digest,
                observed_by_principal_id=context.identity.identity_id,
                observed_at=datetime.now(timezone.utc),
            ),
            idempotency_key=key, session=session,
        )
        return {
            "schema": "WILSY-PROJECT-ATTACHMENT-SCAN-RESULT/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "project_id": project_id, "task_id": task_id,
            "attachment_id": attachment_id,
            "scan_status": result.scan_status,
            "clearance_fingerprint": result.fingerprint,
        }

    return _transaction(context, record, write=True)


@router.get("/my-approvals")
def list_my_pending_project_approvals(
    response: Response,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_CONTRIBUTE),
) -> dict[str, object]:
    """Read only pending approvals assigned to this active reviewer.

    A reviewer principal's IAM is necessary but not sufficient. Each project
    must independently have a current ACTIVE CONTRIBUTOR participation record
    and the referenced task must still exist in exact tenant scope. Filter
    before page boundaries; source capacity overflow fails closed.
    """
    response.headers["Cache-Control"] = "no-store"

    def read(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        database = kernel_db.get_database()
        if database is None:
            raise ProjectApprovalError("PROJECT_APPROVAL_SOURCE_UNAVAILABLE")
        approvals = ProjectApprovalRegistry(
            database[PROJECT_APPROVAL_COLLECTION],
            database[PROJECT_APPROVAL_EVENT_COLLECTION],
        )
        eligible = []
        known: dict[str, bool] = {}
        for approval in approvals.pending_for_reviewer(
            tenant_id=context.tenant_id,
            reviewer_principal_id=context.identity.identity_id,
            session=session,
        ):
            if approval.project_id not in known:
                try:
                    _project, participants = _require_current_project_participation(
                        context, registry, approval.project_id, session,
                    )
                    assignment = participants.get(
                        tenant_id=context.tenant_id,
                        project_id=approval.project_id,
                        principal_id=context.identity.identity_id,
                        session=session,
                    )
                    known[approval.project_id] = assignment.role == "CONTRIBUTOR"
                except (ProjectParticipantNotFound, ProjectNotFound):
                    known[approval.project_id] = False
            if not known[approval.project_id]:
                continue
            try:
                _project_task_store(
                    registry, context.tenant_id, approval.project_id, session,
                ).get(
                    tenant_id=context.tenant_id,
                    project_id=approval.project_id,
                    task_id=approval.task_id,
                    session=session,
                )
            except ProjectTaskNotFound:
                continue
            eligible.append(approval)
        items = eligible[offset:offset + limit]
        more = len(eligible) > offset + limit
        return {
            "schema": "WILSY-PROJECT-PENDING-APPROVALS/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "items": [item.to_dict() for item in items],
            "offset": offset, "limit": limit, "has_more": more,
            "next_offset": offset + len(items) if more else None,
        }

    return _transaction(context, read)


@router.get("/{project_id}/tasks/{task_id}/approvals")
def list_project_task_approvals(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_DETAIL),
) -> dict[str, object]:
    """List task decisions only through separately admitted owner read IAM."""
    response.headers["Cache-Control"] = "no-store"
    return _profiled_projects_get(context, "TASK_APPROVALS", lambda registry, session: _approval_page(
        context, project_id, task_id, registry, session, limit, offset,
    ))


@router.get("/{project_id}/my-project/tasks/{task_id}/approvals")
def list_participant_task_approvals(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_DETAIL),
) -> dict[str, object]:
    """List task decisions only after the caller's current project admission."""
    response.headers["Cache-Control"] = "no-store"

    def read(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        _require_current_project_participation(context, registry, project_id, session)
        return _approval_page(
            context, project_id, task_id, registry, session, limit, offset,
        )

    return _transaction(context, read)


@router.post("/{project_id}/tasks/{task_id}/approvals", status_code=status.HTTP_201_CREATED)
def request_project_task_approval(
    payload: ProjectApprovalRequest, response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Request an independently reviewed business decision on an existing task."""
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)
    evidence = _fresh_project_approval_evidence(
        context, project_id, task_id, payload.evidence_attachment_ids,
        participant=False,
    )

    def write(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        store = _project_approval_store(
            registry, context.tenant_id, project_id, task_id, session,
        )
        database = kernel_db.get_database()
        if database is None:
            raise ProjectApprovalError("PROJECT_APPROVAL_SOURCE_UNAVAILABLE")
        actor = context.identity.identity_id
        if payload.reviewer_principal_id == actor:
            raise HTTPException(status_code=403, detail="PROJECT_APPROVAL_SELF_REVIEW_DENIED")
        if not _project_participant_eligible(
            database, context.tenant_id, payload.reviewer_principal_id, session,
        ):
            raise HTTPException(status_code=409, detail="PROJECT_APPROVAL_REVIEWER_NOT_CURRENT")
        participants = _project_participants(
            registry, context.tenant_id, project_id, session,
        )
        reviewer = participants.get(
            tenant_id=context.tenant_id, project_id=project_id,
            principal_id=payload.reviewer_principal_id, session=session,
        )
        if reviewer.role != "CONTRIBUTOR":
            raise HTTPException(status_code=409, detail="PROJECT_APPROVAL_REVIEWER_NOT_CONTRIBUTOR")
        if len(set(payload.evidence_attachment_ids)) != len(payload.evidence_attachment_ids):
            raise HTTPException(status_code=422, detail="PROJECT_APPROVAL_EVIDENCE_DUPLICATED")
        for attachment_id in payload.evidence_attachment_ids:
            if re.fullmatch(r"pat-[0-9a-f]{48}", attachment_id) is None:
                raise HTTPException(status_code=422, detail="PROJECT_APPROVAL_EVIDENCE_ID_INVALID")
            manifest, clearance = _require_cleared_project_attachment(
                registry, context.tenant_id, project_id,
                task_id, attachment_id, session,
            )
            if evidence.get(attachment_id) != (
                manifest.fingerprint, clearance.fingerprint,
            ):
                raise HTTPException(
                    status_code=409, detail="PROJECT_APPROVAL_EVIDENCE_CHANGED",
                )
        approval = ProjectApproval(
            tenant_id=context.tenant_id, project_id=project_id,
            task_id=task_id,
            approval_id=approval_id_for_request(
                context.tenant_id, project_id, task_id, actor, key,
            ),
            requester_principal_id=actor,
            reviewer_principal_id=payload.reviewer_principal_id,
            rationale=payload.rationale, status="PENDING",
            evidence_attachment_ids=payload.evidence_attachment_ids,
            requested_at=datetime.now(timezone.utc),
        )
        committed = store.create_or_replay(
            approval=approval, idempotency_key=key, session=session,
        )
        return _approval_result(context, project_id, task_id, committed)

    return _transaction(context, write, write=True)


@router.post("/{project_id}/my-project/tasks/{task_id}/approvals/{approval_id}/decision")
def decide_project_task_approval(
    payload: ProjectApprovalDecisionRequest, response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    approval_id: str = Path(pattern=r"^par-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_CONTRIBUTE),
) -> dict[str, object]:
    """Allow only the designated current Contributor to decide exactly once.

    A PENDING evidence-backed review requires fresh GuardDuty provider readback
    before entering the write transaction. Terminal idempotent replay does not
    generate a new verdict or replace already durable decision evidence.
    """
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)

    def original(registry: ProjectRegistry, session: Any) -> ProjectApproval:
        _require_current_project_participation(
            context, registry, project_id, session, contribute=True,
        )
        saved = _project_approval_store(
            registry, context.tenant_id, project_id, task_id, session,
        ).get(
            tenant_id=context.tenant_id, project_id=project_id,
            task_id=task_id, approval_id=approval_id, session=session,
        )
        if saved.reviewer_principal_id != context.identity.identity_id:
            raise HTTPException(status_code=404, detail="PROJECT_APPROVAL_NOT_FOUND")
        return saved

    observed = _transaction(context, original)
    evidence = (
        _fresh_project_approval_evidence(
            context, project_id, task_id, observed.evidence_attachment_ids,
            participant=True,
        ) if observed.status == "PENDING" else None
    )

    def write(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        _require_current_project_participation(
            context, registry, project_id, session, contribute=True,
        )
        store = _project_approval_store(
            registry, context.tenant_id, project_id, task_id, session,
        )
        current_approval = store.get(
            tenant_id=context.tenant_id, project_id=project_id,
            task_id=task_id, approval_id=approval_id, session=session,
        )
        if current_approval.reviewer_principal_id != context.identity.identity_id:
            raise HTTPException(status_code=404, detail="PROJECT_APPROVAL_NOT_FOUND")
        if current_approval.fingerprint != observed.fingerprint:
            raise HTTPException(
                status_code=409, detail="PROJECT_APPROVAL_SOURCE_CHANGED",
            )
        for attachment_id in current_approval.evidence_attachment_ids:
            manifest, clearance = _require_cleared_project_attachment(
                registry, context.tenant_id, project_id,
                task_id, attachment_id, session,
            )
            if evidence is not None and evidence.get(attachment_id) != (
                manifest.fingerprint, clearance.fingerprint,
            ):
                raise HTTPException(
                    status_code=409, detail="PROJECT_APPROVAL_EVIDENCE_CHANGED",
                )
        committed = store.decide_or_replay(
            tenant_id=context.tenant_id, project_id=project_id,
            task_id=task_id, approval_id=approval_id,
            reviewer_principal_id=context.identity.identity_id,
            decision=payload.decision, rationale=payload.rationale,
            expected_revision=payload.expected_revision,
            occurred_at=datetime.now(timezone.utc),
            idempotency_key=key, session=session,
        )
        return _approval_result(context, project_id, task_id, committed)

    return _transaction(context, write, write=True)


def _task_activity_page(
    context: TenantAuthorizationContext, registry: ProjectRegistry,
    project_id: str, task_id: str, session: Any, limit: int, offset: int,
) -> dict[str, object]:
    source = _project_task_store(registry, context.tenant_id, project_id, session)
    events, more = source.list_event_page(
        tenant_id=context.tenant_id, project_id=project_id,
        task_id=task_id, session=session, limit=limit, offset=offset,
    )
    return {
        "schema": "WILSY-PROJECT-TASK-EVENT-LIST/V1",
        "tenant_id": context.tenant_id,
        "principal_id": context.identity.identity_id,
        "project_id": project_id, "task_id": task_id,
        "items": list(events), "limit": limit, "offset": offset,
        "has_more": more,
        "next_offset": offset + len(events) if more else None,
    }


@router.get("/{project_id}/tasks/{task_id}/events")
def list_owner_task_events(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_DETAIL),
) -> dict[str, object]:
    """Read immutable exact-task events through owner Projects detail IAM."""
    response.headers["Cache-Control"] = "no-store"
    return _profiled_projects_get(context, "TASK_EVENTS", lambda registry, session: _task_activity_page(
        context, registry, project_id, task_id, session, limit, offset,
    ))


@router.get("/{project_id}/my-project/tasks/{task_id}/events")
def list_participant_task_events(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_DETAIL),
) -> dict[str, object]:
    """Verify current participation before exposing scoped task events."""
    response.headers["Cache-Control"] = "no-store"
    def read(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        _require_current_project_participation(context, registry, project_id, session)
        return _task_activity_page(
            context, registry, project_id, task_id, session, limit, offset,
        )
    return _transaction(context, read)


@router.get("/{project_id}/tasks/{task_id}/comments")
def list_owner_task_comments(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_DETAIL),
) -> dict[str, object]:
    """Read task comments through current tenant owner IAM and entitlement."""
    response.headers["Cache-Control"] = "no-store"
    return _profiled_projects_get(context, "TASK_COMMENTS", lambda registry, session: _list_project_comments(
        context, registry, project_id, task_id, session, limit, offset,
    ))


@router.post("/{project_id}/tasks/{task_id}/comments", status_code=status.HTTP_201_CREATED)
def create_owner_task_comment(
    payload: ProjectTaskCommentRequest, response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Append one audited owner-authored task comment, not an approval."""
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)
    return _transaction(context, lambda registry, session: _create_project_comment(
        context, registry, project_id, task_id, payload, key, session,
    ), write=True)


@router.get("/{project_id}/my-project/tasks/{task_id}/comments")
def list_participant_task_comments(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_DETAIL),
) -> dict[str, object]:
    """Read task comments only through active current project participation."""
    response.headers["Cache-Control"] = "no-store"

    def read(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        _require_current_project_participation(context, registry, project_id, session)
        return _list_project_comments(
            context, registry, project_id, task_id, session, limit, offset,
        )

    return _transaction(context, read)


@router.post("/{project_id}/my-project/tasks/{task_id}/comments", status_code=status.HTTP_201_CREATED)
def create_participant_task_comment(
    payload: ProjectTaskCommentRequest, response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_CONTRIBUTE),
) -> dict[str, object]:
    """Write comments only with contributor IAM and active project record."""
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)

    def write(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        _require_current_project_participation(
            context, registry, project_id, session, contribute=True,
        )
        return _create_project_comment(
            context, registry, project_id, task_id, payload, key, session,
        )

    return _transaction(context, write, write=True)


@router.get("/{project_id}/task-action-capabilities")
def read_project_task_action_capabilities(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    context: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Project task action projection gated by existing update authority.

    Every command independently reauthorizes and rechecks its revision.
    This read does not issue a grant, entitlement, or session.
    """
    response.headers["Cache-Control"] = "no-store"

    def read(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        registry.get(
            tenant_id=context.tenant_id, project_id=project_id, session=session,
        )
        return {
            "schema": "WILSY-PROJECT-TASK-ACTION-CAPABILITIES/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "project_id": project_id,
            "can_start": True,
            "can_complete": True,
            "can_block": True,
            "can_cancel": True,
            "can_assign": True,
            "can_edit": True,
        }

    return _transaction(context, read)


def _work_purpose_store() -> ProjectWorkPurposeRegistry:
    """Compose the source-owned purpose registry without introducing new IAM."""
    database = kernel_db.get_database()
    if database is None:
        raise WorkPurposeError("PROJECT_WORK_PURPOSE_SOURCE_UNAVAILABLE")
    return ProjectWorkPurposeRegistry(
        database[PROJECT_WORK_PURPOSE_COLLECTION],
        database[PROJECT_WORK_PURPOSE_EVENT_COLLECTION],
    )


@router.get("/{project_id}/tasks/{task_id}/work-purpose")
def read_project_task_work_purpose(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    context: TenantAuthorizationContext = Depends(_DETAIL),
) -> dict[str, object]:
    """Read source-audited task purpose after exact project-detail authority."""
    response.headers["Cache-Control"] = "no-store"

    def read(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        task = _project_task_store(registry, context.tenant_id, project_id, session).get(
            tenant_id=context.tenant_id, project_id=project_id,
            task_id=task_id, session=session,
        )
        purpose = _work_purpose_store().current_for_task(task=task, session=session)
        return {
            "schema": "WILSY-PROJECT-WORK-PURPOSE/V1",
            "tenant_id": context.tenant_id, "principal_id": context.identity.identity_id,
            "project_id": project_id, "task_id": task_id,
            "task_revision": task.revision,
            "purpose_revision": purpose["purpose_revision"] if purpose else 0,
            "audience": purpose["audience"] if purpose else "UNCLASSIFIED",
            "evidence_ref": purpose["evidence_ref"] if purpose else None,
            "source_revision": purpose["source_revision"] if purpose else None,
            "critical_gate": False,
        }

    return _transaction(context, read)


@router.get("/{project_id}/tasks/{task_id}/work-purpose/events")
def read_project_work_purpose_history(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    limit: int = Query(default=25, ge=1, le=50),
    context: TenantAuthorizationContext = Depends(_DETAIL),
) -> dict[str, object]:
    """Expose source-verified history through current project read authority."""
    response.headers["Cache-Control"] = "no-store"

    def read(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        task = _project_task_store(registry, context.tenant_id, project_id, session).get(
            tenant_id=context.tenant_id, project_id=project_id,
            task_id=task_id, session=session,
        )
        events, more = _work_purpose_store().history_for_task(
            task=task, session=session, limit=limit,
        )
        return {
            "schema": "WILSY-PROJECT-WORK-PURPOSE-HISTORY/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "project_id": project_id, "task_id": task_id,
            "items": events, "limit": limit, "has_more": more,
        }

    return _transaction(context, read)


@router.post("/{project_id}/tasks/{task_id}/work-purpose")
def classify_project_task_work_purpose(
    payload: ProjectTaskWorkPurposeRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Audited exact-source purpose command, separately gated by project:update."""
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)
    timestamp = datetime.now(timezone.utc)

    def commit(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        task = _project_task_store(registry, context.tenant_id, project_id, session).get(
            tenant_id=context.tenant_id, project_id=project_id,
            task_id=task_id, session=session,
        )
        purpose_registry = _work_purpose_store()
        purpose_registry.classify(
            task=task, actor_principal_id=context.identity.identity_id,
            audience=payload.audience, reason=payload.reason,
            expected_task_revision=payload.expected_task_revision,
            expected_purpose_revision=payload.expected_purpose_revision,
            idempotency_key=key, session=session, now=timestamp,
        )
        verified = purpose_registry.current_for_task(task=task, session=session)
        if verified is None or verified["audience"] != payload.audience:
            raise WorkPurposeError("PROJECT_WORK_PURPOSE_READBACK_UNVERIFIED")
        return {
            "schema": "WILSY-PROJECT-WORK-PURPOSE/V1",
            "tenant_id": context.tenant_id, "principal_id": context.identity.identity_id,
            "project_id": project_id, "task_id": task_id,
            "task_revision": task.revision,
            "purpose_revision": verified["purpose_revision"],
            "audience": verified["audience"],
            "evidence_ref": verified["evidence_ref"],
            "source_revision": verified["source_revision"],
            "critical_gate": False,
        }

    return _transaction(context, commit, write=True)


@router.get("/{project_id}/tasks")
def list_project_tasks(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_DETAIL),
) -> dict[str, object]:
    """Return exact-project task page through tenant-owner Projects IAM."""
    response.headers["Cache-Control"] = "no-store"
    return _profiled_projects_get(context, "TASK_LIST", lambda registry, session: _list_project_tasks(
        context, project_id, registry, session, limit, offset,
    ))


@router.get("/{project_id}/my-project/tasks")
def list_assigned_project_tasks(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_DETAIL),
) -> dict[str, object]:
    """Read task page only after exact current project participation verification."""
    response.headers["Cache-Control"] = "no-store"

    def read(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        _require_current_project_participation(context, registry, project_id, session)
        return _list_project_tasks(context, project_id, registry, session, limit, offset)

    return _transaction(context, read)


@router.post("/{project_id}/tasks", status_code=status.HTTP_201_CREATED)
def create_project_task(
    payload: ProjectTaskCreateRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Create one audited task/milestone, validating exact assigned participant."""
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)
    instant = datetime.now(timezone.utc)

    def create(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        tasks = _project_task_store(registry, context.tenant_id, project_id, session)
        if payload.assignee_principal_id is not None:
            database = kernel_db.get_database()
            if database is None:
                raise ProjectTaskError("PROJECT_TASK_SOURCE_UNAVAILABLE")
            if not _project_participant_eligible(
                database, context.tenant_id, payload.assignee_principal_id, session,
            ):
                raise HTTPException(status_code=409, detail="PROJECT_TASK_ASSIGNEE_NOT_CURRENT")
            participants = _project_participants(registry, context.tenant_id, project_id, session)
            assignment = participants.get(
                tenant_id=context.tenant_id, project_id=project_id,
                principal_id=payload.assignee_principal_id, session=session,
            )
            if assignment.role != "CONTRIBUTOR":
                raise HTTPException(status_code=409, detail="PROJECT_TASK_ASSIGNEE_NOT_CONTRIBUTOR")
        task_id = task_id_for_command(
            context.tenant_id, project_id, context.identity.identity_id, key,
        )
        task = ProjectTask(
            tenant_id=context.tenant_id, project_id=project_id,
            task_id=task_id, kind=payload.kind,
            parent_task_id=payload.parent_task_id,
            title=payload.title, description=payload.description,
            status="TODO", assignee_principal_id=payload.assignee_principal_id,
            due_date=payload.due_date.isoformat() if payload.due_date else None,
            depends_on=payload.depends_on,
            created_by_principal_id=context.identity.identity_id,
            updated_by_principal_id=context.identity.identity_id,
            created_at=instant, updated_at=instant,
        )
        committed = tasks.create_or_replay(
            task=task, idempotency_key=key, session=session,
        )
        return _task_result(context, project_id, committed)

    return _transaction(context, create, write=True)


@router.patch("/{project_id}/tasks/{task_id}")
def revise_project_task(
    payload: ProjectTaskReviseRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Edit one exact task with current-project assignee verification and CAS."""
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)
    instant = datetime.now(timezone.utc)

    def revise(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        tasks = _project_task_store(registry, context.tenant_id, project_id, session)
        if payload.assignee_principal_id is not None:
            database = kernel_db.get_database()
            if database is None:
                raise ProjectTaskError("PROJECT_TASK_SOURCE_UNAVAILABLE")
            if not _project_participant_eligible(
                database, context.tenant_id, payload.assignee_principal_id, session,
            ):
                raise HTTPException(status_code=409, detail="PROJECT_TASK_ASSIGNEE_NOT_CURRENT")
            participants = _project_participants(
                registry, context.tenant_id, project_id, session,
            )
            assignment = participants.get(
                tenant_id=context.tenant_id, project_id=project_id,
                principal_id=payload.assignee_principal_id, session=session,
            )
            if assignment.role != "CONTRIBUTOR":
                raise HTTPException(status_code=409, detail="PROJECT_TASK_ASSIGNEE_NOT_CONTRIBUTOR")
        committed = tasks.revise_or_replay(
            tenant_id=context.tenant_id, project_id=project_id, task_id=task_id,
            actor_principal_id=context.identity.identity_id,
            title=payload.title, description=payload.description,
            due_date=payload.due_date.isoformat() if payload.due_date else None,
            assignee_principal_id=payload.assignee_principal_id,
            expected_revision=payload.expected_revision,
            idempotency_key=key, occurred_at=instant, session=session,
        )
        return _task_result(context, project_id, committed)

    return _transaction(context, revise, write=True)


@router.post("/{project_id}/tasks/{task_id}/transition")
def transition_project_task(
    payload: ProjectTaskTransitionRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Require owner update IAM and source CAS for a project task transition."""
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)
    instant = datetime.now(timezone.utc)

    def change(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        tasks = _project_task_store(registry, context.tenant_id, project_id, session)
        result = tasks.transition_or_replay(
            tenant_id=context.tenant_id, project_id=project_id,
            task_id=task_id, actor_principal_id=context.identity.identity_id,
            status=payload.status, expected_revision=payload.expected_revision,
            idempotency_key=key, occurred_at=instant, session=session,
        )
        return _task_result(context, project_id, result)

    return _transaction(context, change, write=True)


@router.post("/{project_id}/my-project/tasks/{task_id}/transition")
def transition_assigned_project_task(
    payload: ProjectTaskTransitionRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    task_id: str = Path(pattern=r"^ptk-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_CONTRIBUTE),
) -> dict[str, object]:
    """Permit contributor lifecycle only for personally assigned project work."""
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)
    instant = datetime.now(timezone.utc)

    def change(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        _require_current_project_participation(
            context, registry, project_id, session, contribute=True,
        )
        tasks = _project_task_store(registry, context.tenant_id, project_id, session)
        task = tasks.get(
            tenant_id=context.tenant_id, project_id=project_id,
            task_id=task_id, session=session,
        )
        if task.assignee_principal_id != context.identity.identity_id:
            raise HTTPException(status_code=403, detail="PROJECT_TASK_ASSIGNEE_SCOPE_REQUIRED")
        result = tasks.transition_or_replay(
            tenant_id=context.tenant_id, project_id=project_id,
            task_id=task_id, actor_principal_id=context.identity.identity_id,
            status=payload.status, expected_revision=payload.expected_revision,
            idempotency_key=key, occurred_at=instant, session=session,
        )
        return _task_result(context, project_id, result)

    return _transaction(context, change, write=True)


@router.get("/my-projects")
def list_my_assigned_projects(
    response: Response,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_DETAIL),
) -> dict[str, object]:
    """Discover only this principal's explicit active Projects assignments.

    No tenant-wide project list is accessible through participant IAM.
    Each participating record is rechecked against the current canonical
    Projects source in the same read snapshot before being revealed.
    """
    response.headers["Cache-Control"] = "no-store"

    def read(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        database = kernel_db.get_database()
        if database is None:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_SOURCE_UNAVAILABLE")
        participants = ProjectParticipantRegistry(
            database[PROJECT_PARTICIPANT_COLLECTION],
            database[PROJECT_PARTICIPANT_EVENT_COLLECTION],
        )
        assignments, more = participants.projects_for_principal(
            tenant_id=context.tenant_id,
            principal_id=context.identity.identity_id,
            limit=limit, offset=offset, session=session,
        )
        verified = []
        for assignment in assignments:
            project = registry.get(
                tenant_id=context.tenant_id,
                project_id=assignment.project_id, session=session,
            )
            verified.append({
                "project": project.to_dict(),
                "participation": assignment.to_dict(),
            })
        return {
            "schema": "WILSY-PROJECT-MY-PROJECTS/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "items": verified, "limit": limit, "offset": offset,
            "has_more": more,
            "next_offset": offset + len(verified) if more else None,
        }

    return _transaction(context, read)


@router.get("/{project_id}/my-project")
def read_assigned_project(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_DETAIL),
) -> dict[str, object]:
    """Read only the one exact project covered by a current participant record."""
    response.headers["Cache-Control"] = "no-store"

    def read(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        project, participants = _require_current_project_participation(
            context, registry, project_id, session,
        )
        own = participants.get(
            tenant_id=context.tenant_id, project_id=project_id,
            principal_id=context.identity.identity_id, session=session,
        )
        return {
            "schema": "WILSY-PROJECT-PARTICIPANT-DETAIL/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "project_id": project_id, "project": project.to_dict(),
            "participation": own.to_dict(),
        }

    return _transaction(context, read)


@router.get("/{project_id}/my-project/notes")
def read_assigned_project_notes(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_DETAIL),
) -> dict[str, object]:
    """Read project notes only after participant IAM and exact record checks."""
    response.headers["Cache-Control"] = "no-store"

    def read(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        _require_current_project_participation(context, registry, project_id, session)
        notes = _project_note_store(registry, context.tenant_id, project_id, session)
        items, more = notes.list_for_project(
            tenant_id=context.tenant_id, project_id=project_id,
            limit=limit, offset=offset, session=session,
        )
        return {
            "schema": "WILSY-PROJECT-NOTE-LIST/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "project_id": project_id,
            "items": [item.to_dict() for item in items],
            "limit": limit, "offset": offset,
            "has_more": more,
            "next_offset": offset + len(items) if more else None,
        }

    return _transaction(context, read)


@router.post("/{project_id}/my-project/notes", status_code=status.HTTP_201_CREATED)
def create_assigned_project_note(
    payload: ProjectNoteCreateRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_PARTICIPANT_CONTRIBUTE),
) -> dict[str, object]:
    """Author a descriptive note only with active contributor IAM and project role."""
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)
    instant = datetime.now(timezone.utc)

    def create(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        _require_current_project_participation(
            context, registry, project_id, session, contribute=True,
        )
        notes = _project_note_store(registry, context.tenant_id, project_id, session)
        note_id = note_id_for_command(
            context.tenant_id, project_id, context.identity.identity_id, key,
        )
        note = ProjectNote(
            tenant_id=context.tenant_id, project_id=project_id,
            note_id=note_id, author_principal_id=context.identity.identity_id,
            body=payload.body, colour=payload.colour, created_at=instant, updated_at=instant,
        )
        result = notes.create_or_replay(
            note=note, actor_principal_id=context.identity.identity_id,
            idempotency_key=key, occurred_at=instant, session=session,
        )
        return _project_note_result(context, project_id, result)

    return _transaction(context, create, write=True)


def _project_participant_page_names(
    database: Any, tenant_id: str, principal_ids: list[str], session: Any,
) -> dict[str, dict[str, str | None]]:
    """One bounded exact-tenant display-only lookup, never membership authority."""
    if not principal_ids:
        return {}
    if len(principal_ids) > 100 or len(set(principal_ids)) != len(principal_ids):
        raise HTTPException(status_code=503, detail="PROJECT_PARTICIPANT_NAMES_INVALID")
    by_identity = set(principal_ids)
    legacy = [
        ObjectId(value) for value in principal_ids
        if re.fullmatch(r"[0-9a-fA-F]{24}", value)
    ]
    clauses: list[dict[str, object]] = [{"user_id": {"$in": principal_ids}}]
    if legacy:
        clauses.append({"_id": {"$in": legacy}})
    try:
        cursor = database["users"].find(
            {"tenantId": tenant_id, "$or": clauses},
            {"_id": 1, "user_id": 1, "tenantId": 1,
             "firstName": 1, "lastName": 1},
            session=session,
        ).limit(2 * len(principal_ids) + 1)
        profiles = list(cursor)
    except PyMongoError as error:
        raise HTTPException(
            status_code=503, detail="PROJECT_PARTICIPANT_NAMES_UNAVAILABLE",
        ) from error
    if len(profiles) > 2 * len(principal_ids):
        raise HTTPException(status_code=503, detail="PROJECT_PARTICIPANT_NAMES_COLLISION")
    results: dict[str, dict[str, str | None]] = {}
    for profile in profiles:
        if not isinstance(profile, dict) or profile.get("tenantId") != tenant_id:
            raise HTTPException(status_code=503, detail="PROJECT_PARTICIPANT_NAMES_INVALID")
        canonical = profile.get("user_id")
        legacy_id = str(profile.get("_id")) if isinstance(profile.get("_id"), ObjectId) else None
        matches = [value for value in (canonical, legacy_id) if value in by_identity]
        if not matches:
            raise HTTPException(status_code=503, detail="PROJECT_PARTICIPANT_NAMES_INVALID")
        # A matching legacy ObjectId must not silently alias a different user ID.
        if legacy_id in matches and canonical is not None and canonical != legacy_id:
            raise HTTPException(status_code=503, detail="PROJECT_PARTICIPANT_NAMES_COLLISION")
        for identifier in matches:
            if identifier in results:
                raise HTTPException(status_code=503, detail="PROJECT_PARTICIPANT_NAMES_COLLISION")
            def optional(value: object) -> str | None:
                return value if (
                    isinstance(value, str) and 0 < len(value) <= 100
                    and value == value.strip()
                ) else None
            results[identifier] = {
                "first_name": optional(profile.get("firstName")),
                "last_name": optional(profile.get("lastName")),
            }
    return results


@router.get("/{project_id}/participant-options")
def project_participant_options(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_DETAIL),
) -> dict[str, object]:
    """List exact-tenant currently eligible member principals for owner assignment.

    This is a choice projection, not employment, current permission possession,
    project participation or an invitation. Grants independently revalidate
    source principal, membership and capacity within the write transaction.
    """
    response.headers["Cache-Control"] = "no-store"

    def load(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        _project_participants(registry, context.tenant_id, project_id, session)
        database = kernel_db.get_database()
        if database is None:
            raise HTTPException(status_code=503, detail="PROJECT_PARTICIPANT_SOURCE_UNAVAILABLE")
        try:
            members = database["tenant_memberships"].find({
                "tenant_id": context.tenant_id, "status": "ACTIVE",
            }, {"principal_id": 1, "_id": 0}, session=session).sort(
                "principal_id", 1,
            ).skip(offset).limit(limit + 1)
            records = list(members)
        except PyMongoError as error:
            raise HTTPException(status_code=503, detail="PROJECT_PARTICIPANT_DIRECTORY_UNAVAILABLE") from error
        candidates = []
        for entry in records[:limit]:
            principal_id = entry.get("principal_id")
            if not isinstance(principal_id, str) or not principal_id:
                raise HTTPException(status_code=503, detail="PROJECT_PARTICIPANT_DIRECTORY_INVALID")
            if _project_participant_eligible(
                database, context.tenant_id, principal_id, session,
            ):
                candidates.append({"principal_id": principal_id})
        names = _project_participant_page_names(
            database, context.tenant_id,
            [entry["principal_id"] for entry in candidates], session,
        )
        candidates = [
            {"principal_id": entry["principal_id"],
             **names.get(entry["principal_id"], {
                 "first_name": None, "last_name": None,
             })}
            for entry in candidates
        ]
        return {
            "schema": "WILSY-PROJECT-PARTICIPANT-OPTIONS/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "project_id": project_id, "items": candidates,
            "limit": limit, "offset": offset,
            "has_more": len(records) > limit,
            "next_offset": offset + limit if len(records) > limit else None,
        }

    return _transaction(context, load)


@router.get("/{project_id}/participants")
def list_project_participants(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_DETAIL),
) -> dict[str, object]:
    """List verified active participant records for an authorized project owner."""
    response.headers["Cache-Control"] = "no-store"

    def load(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        participants = _project_participants(registry, context.tenant_id, project_id, session)
        items, has_more = participants.page(
            tenant_id=context.tenant_id, project_id=project_id,
            session=session, limit=limit, offset=offset,
        )
        source_rows = [item.to_dict() for item in items]
        principal_ids: list[str] = []
        for row in source_rows:
            principal_id = row.get("principal_id")
            if not isinstance(principal_id, str) or not principal_id:
                raise HTTPException(
                    status_code=503,
                    detail="PROJECT_PARTICIPANT_NAMES_INVALID",
                )
            principal_ids.append(principal_id)

        database = kernel_db.get_database()
        if database is None:
            raise HTTPException(
                status_code=503, detail="PROJECT_PARTICIPANT_NAMES_UNAVAILABLE",
            )
        names = _project_participant_page_names(
            database, context.tenant_id, principal_ids, session,
        )
        displayed_rows = [
            {
                **row,
                **names.get(principal_id, {
                    "first_name": None, "last_name": None,
                }),
            }
            for row, principal_id in zip(
                source_rows, principal_ids, strict=True
            )
        ]
        return {
            "schema": "WILSY-PROJECT-PARTICIPANT-LIST/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "project_id": project_id,
            "items": displayed_rows,
            "limit": limit, "offset": offset, "has_more": has_more,
            "next_offset": offset + len(items) if has_more else None,
        }

    return _transaction(context, load)


@router.post("/{project_id}/participants", status_code=status.HTTP_201_CREATED)
def grant_project_participant(
    payload: ProjectParticipantGrantRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Grant one exact-project participation, without issuing IAM or employment."""
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)
    now = datetime.now(timezone.utc)

    def grant(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        participants = _project_participants(registry, context.tenant_id, project_id, session)
        database = kernel_db.get_database()
        if database is None:
            raise ProjectParticipantError("PROJECT_PARTICIPANT_SOURCE_UNAVAILABLE")
        if not _project_participant_eligible(database, context.tenant_id, payload.principal_id, session):
            raise HTTPException(status_code=409, detail="PROJECT_PARTICIPANT_NOT_ELIGIBLE")
        result = participants.grant(
            tenant_id=context.tenant_id, project_id=project_id,
            principal_id=payload.principal_id, role=payload.role,
            actor_principal_id=context.identity.identity_id,
            idempotency_key=key, occurred_at=now, session=session,
        )
        return {
            "schema": "WILSY-PROJECT-PARTICIPANT-RESULT/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "project_id": project_id, "participant": result.to_dict(),
        }

    return _transaction(context, grant, write=True)


@router.post("/{project_id}/participants/{participant_principal_id}/revoke")
def revoke_project_participant(
    payload: ProjectParticipantRevokeRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    participant_principal_id: str = Path(min_length=1, max_length=180),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Revoke one participant under owner IAM and exact optimistic revision."""
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)
    now = datetime.now(timezone.utc)

    def revoke(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        participants = _project_participants(registry, context.tenant_id, project_id, session)
        result = participants.revoke(
            tenant_id=context.tenant_id, project_id=project_id,
            principal_id=participant_principal_id,
            actor_principal_id=context.identity.identity_id,
            expected_revision=payload.expected_revision,
            idempotency_key=key, occurred_at=now, session=session,
        )
        return {
            "schema": "WILSY-PROJECT-PARTICIPANT-RESULT/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "project_id": project_id, "participant": result.to_dict(),
        }

    return _transaction(context, revoke, write=True)


@router.get("/{project_id}/notes")
def list_project_notes(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: TenantAuthorizationContext = Depends(_DETAIL),
) -> dict[str, object]:
    """Return one permission-checked tenant/project note page."""
    response.headers["Cache-Control"] = "no-store"

    def load(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        notes = _project_note_store(registry, context.tenant_id, project_id, session)
        values, more = notes.list_for_project(
            tenant_id=context.tenant_id, project_id=project_id,
            limit=limit, offset=offset, session=session,
        )
        return {
            "schema": "WILSY-PROJECT-NOTE-LIST/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "project_id": project_id,
            "items": [item.to_dict() for item in values],
            "limit": limit, "offset": offset,
            "has_more": more,
            "next_offset": offset + len(values) if more else None,
        }

    return _transaction(context, load)


@router.post("/{project_id}/notes", status_code=status.HTTP_201_CREATED)
def create_project_note(
    payload: ProjectNoteCreateRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Author one project note; replay and readback are transaction-bound."""
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)
    now = datetime.now(timezone.utc)
    note_id = note_id_for_command(
        context.tenant_id, project_id, context.identity.identity_id, key,
    )
    def create(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        notes = _project_note_store(registry, context.tenant_id, project_id, session)
        note = ProjectNote(
            tenant_id=context.tenant_id, project_id=project_id, note_id=note_id,
            author_principal_id=context.identity.identity_id,
            body=payload.body, colour=payload.colour, created_at=now, updated_at=now,
        )
        committed = notes.create_or_replay(
            note=note, actor_principal_id=context.identity.identity_id,
            idempotency_key=key, occurred_at=now, session=session,
        )
        return _project_note_result(
            context, project_id, committed,
            events=notes.list_events(
                tenant_id=context.tenant_id, project_id=project_id,
                note_id=note_id, session=session,
            ),
        )

    return _transaction(context, create, write=True)


@router.patch("/{project_id}/notes/{note_id}")
def revise_project_note(
    payload: ProjectNoteReviseRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    note_id: str = Path(pattern=r"^pnt-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Revise only an author's visible current note with audited CAS."""
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)
    now = datetime.now(timezone.utc)

    def revise(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        notes = _project_note_store(registry, context.tenant_id, project_id, session)
        committed = notes.revise_or_replay(
            tenant_id=context.tenant_id, project_id=project_id, note_id=note_id,
            actor_principal_id=context.identity.identity_id,
            expected_revision=payload.expected_revision, body=payload.body,
            colour=payload.colour, idempotency_key=key, occurred_at=now, session=session,
        )
        return _project_note_result(
            context, project_id, committed,
            events=notes.list_events(
                tenant_id=context.tenant_id, project_id=project_id,
                note_id=note_id, session=session,
            ),
        )

    return _transaction(context, revise, write=True)


@router.post("/{project_id}/notes/{note_id}/archive")
def archive_project_note(
    payload: ProjectNoteArchiveRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    note_id: str = Path(pattern=r"^pnt-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Soft-archive a note with author CAS, immutable audit and readback."""
    response.headers["Cache-Control"] = "no-store"
    key = _note_idempotency_key(idempotency_key)
    now = datetime.now(timezone.utc)

    def archive(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        notes = _project_note_store(registry, context.tenant_id, project_id, session)
        committed = notes.archive_or_replay(
            tenant_id=context.tenant_id, project_id=project_id, note_id=note_id,
            actor_principal_id=context.identity.identity_id,
            expected_revision=payload.expected_revision,
            idempotency_key=key, occurred_at=now, session=session,
        )
        return _project_note_result(
            context, project_id, committed,
            events=notes.list_events(
                tenant_id=context.tenant_id, project_id=project_id,
                note_id=note_id, session=session,
            ),
        )

    return _transaction(context, archive, write=True)


@router.get("/{project_id}")
def get_project(
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    include_archived: bool = False,
    context: TenantAuthorizationContext = Depends(_DETAIL),
) -> dict[str, object]:
    """Read one current tenant project and its immutable lifecycle evidence."""
    response.headers["Cache-Control"] = "no-store"

    def load(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        value = registry.get(
            tenant_id=context.tenant_id,
            project_id=project_id,
            session=session,
            include_archived=include_archived,
        )
        events = registry.list_events(
            tenant_id=context.tenant_id, project_id=project_id, session=session,
        )
        response_payload = _result(context, value, events=events)
        actor_ids = {value.created_by_principal_id}
        if value.owner_principal_id:
            actor_ids.add(value.owner_principal_id)
        for event in events:
            actor_id = event["actor_principal_id"]
            if not isinstance(actor_id, str) or not actor_id or len(actor_id) > 180:
                raise HTTPException(
                    status_code=503, detail="PROJECT_ACTOR_DIRECTORY_PAGE_REQUIRED",
                )
            actor_ids.add(actor_id)
        if len(actor_ids) > 100 or any(
            not isinstance(actor_id, str) or not actor_id or len(actor_id) > 180
            for actor_id in actor_ids
        ):
            raise HTTPException(
                status_code=503, detail="PROJECT_ACTOR_DIRECTORY_PAGE_REQUIRED",
            )
        database = kernel_db.get_database()
        if database is None:
            raise HTTPException(
                status_code=503, detail="PROJECT_ACTOR_PROFILE_SOURCE_UNAVAILABLE",
            )
        response_payload["actor_profiles"] = {
            actor_id: _exact_tenant_project_person_name(
                database, context.tenant_id, actor_id, session,
            ) for actor_id in sorted(actor_ids)
        }
        return response_payload

    return _transaction(context, load)


@router.patch("/{project_id}")
def update_project(
    payload: ProjectUpdateRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_UPDATE),
) -> dict[str, object]:
    """Apply exactly one revision-guarded field update or status transition."""
    response.headers["Cache-Control"] = "no-store"
    if (
        not isinstance(idempotency_key, str)
        or not idempotency_key.strip()
        or idempotency_key != idempotency_key.strip()
        or len(idempotency_key) > 200
    ):
        raise HTTPException(status_code=422, detail="PROJECT_IDEMPOTENCY_KEY_INVALID")
    values = payload.model_dump(exclude={"expected_revision", "target_change_reason"},
                                exclude_unset=True)
    reason = payload.target_change_reason
    status_value = values.pop("status", None)
    if not values and status_value is None:
        raise HTTPException(status_code=422, detail="PROJECT_UPDATE_FIELDS_REQUIRED")
    if status_value is not None and (values or reason is not None):
        raise HTTPException(status_code=422, detail="PROJECT_STATUS_TRANSITION_MUST_BE_ISOLATED")
    now = datetime.now(timezone.utc)

    def update(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        if status_value is not None:
            if status_value is ProjectStatus.ACTIVE:
                current = registry.get(
                    tenant_id=context.tenant_id, project_id=project_id, session=session,
                )
                if not current.owner_principal_id or not current.department_id:
                    raise HTTPException(status_code=409, detail="PROJECT_ACCOUNTABILITY_REQUIRED")
                database = kernel_db.get_database()
                if database is None:
                    raise HTTPException(status_code=503, detail="PROJECT_ASSIGNMENT_SOURCE_UNAVAILABLE")
                if not _project_owner_eligible(
                    database, context.tenant_id, current.owner_principal_id, session,
                ):
                    raise HTTPException(status_code=409, detail="PROJECT_OWNER_NOT_ELIGIBLE")
                _current_department(
                    database, context.tenant_id, current.department_id, session,
                )
            updated = registry.transition(
                tenant_id=context.tenant_id,
                project_id=project_id,
                actor_principal_id=context.identity.identity_id,
                expected_revision=payload.expected_revision,
                resulting_status=status_value,
                idempotency_key=idempotency_key.strip(),
                occurred_at=now,
                session=session,
            )
        else:
            updated = registry.update(
                tenant_id=context.tenant_id,
                project_id=project_id,
                actor_principal_id=context.identity.identity_id,
                expected_revision=payload.expected_revision,
                changes=values,
                idempotency_key=idempotency_key.strip(),
                occurred_at=now,
                session=session,
                target_change_reason=reason,
            )
        readback = registry.get(
            tenant_id=context.tenant_id, project_id=project_id, session=session
        )
        if readback.fingerprint != updated.fingerprint:
            raise ProjectRegistryError("PROJECT_UPDATE_READBACK_MISMATCH")
        return _result(
            context,
            readback,
            events=registry.list_events(
                tenant_id=context.tenant_id, project_id=project_id, session=session
            ),
        )

    return _transaction(context, update, write=True)


@router.post("/{project_id}/archive")
def archive_project(
    payload: ProjectArchiveRequest,
    response: Response,
    project_id: str = Path(pattern=r"^prj-[0-9a-f]{48}$"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_ARCHIVE),
) -> dict[str, object]:
    """Soft archive a project and return the committed aggregate/event readback."""
    response.headers["Cache-Control"] = "no-store"
    if (
        not isinstance(idempotency_key, str)
        or not idempotency_key.strip()
        or idempotency_key != idempotency_key.strip()
        or len(idempotency_key) > 200
    ):
        raise HTTPException(status_code=422, detail="PROJECT_IDEMPOTENCY_KEY_INVALID")
    now = datetime.now(timezone.utc)

    def archive(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        archived = registry.archive(
            tenant_id=context.tenant_id,
            project_id=project_id,
            actor_principal_id=context.identity.identity_id,
            expected_revision=payload.expected_revision,
            idempotency_key=idempotency_key.strip(),
            occurred_at=now,
            session=session,
        )
        readback = registry.get(
            tenant_id=context.tenant_id,
            project_id=project_id,
            session=session,
            include_archived=True,
        )
        if readback.fingerprint != archived.fingerprint or readback.archived_at is None:
            raise ProjectRegistryError("PROJECT_ARCHIVE_READBACK_MISMATCH")
        return _result(
            context,
            readback,
            events=registry.list_events(
                tenant_id=context.tenant_id, project_id=project_id, session=session
            ),
        )

    return _transaction(context, archive, write=True)


__all__ = [
    "VERSION",
    "router",
    "ProjectCreateRequest",
    "ProjectUpdateRequest",
    "ProjectArchiveRequest",
]

# ARTIFACT: projects_router.py
# VERSION: v1.48.1-MONGO-DRIVER-PHASE-CORRELATION
# AUTHORITY BOUNDARY: existing canonical tenant IAM and active product entitlement plus source-owned project persistence
# TENANT POSTURE: request tenant must equal authenticated session tenant; persistence and entitlement queries are exact-tenant scoped
# FAIL-CLOSED POSTURE: unverified owner/department, missing entitlement, malformed source, stale revision, replay conflict or transaction failure rejects without IAM expansion
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
