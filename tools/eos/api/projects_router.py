"""
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive.
Authenticated tenant Projects lifecycle HTTP authority.

TITLE: WILSY OS Projects HTTP Router
VERSION: v1.2.1-FOUNDER-INVITATION-AUTHORITY
AUTHORITY: Python EOS canonical tenant IAM, entitlement and Projects registry.
EPITOME: Exposes one tenant-scoped Projects lifecycle through the existing
         validated domain and caller-transaction-owned registry. Role/entitlement activation is limited to the explicitly authorized Founder
         command; it does not select tenants or assign workforce ownership.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/projects_router.py
COLLABORATION / OWNERSHIP: Projects domain and registry own business lifecycle;
                           tenant authorization and entitlement registries own
                           independent admission; server.py mounts this router.
CERTIFICATION / UPDATE DATE: 2026-11-17.
CHANGELOG:
  v1.2.1-FOUNDER-INVITATION-AUTHORITY — Uses tenant_owner's already
  eligible membership_invite operation, retaining the separately governed
  ENTERPRISE_ADMIN -> PROJECTS_PLATFORM_OWNER invitation delegation policy.
  Generic role_grant business-capacity policy remains unchanged.
  v1.2.0-GOVERNED-FOUNDER-PROJECTS-ADMISSION — Gates the API on startup index readiness, bounds list/path/idempotency inputs, and maps invalid domain construction to 422. Existing tenant, entitlement, IAM, transaction and readback rules remain intact.
  v1.0.0-PROJECTS-GOVERNED-API — Adds authenticated list, summary, detail,
  create, update/status-transition and soft-archive HTTP operations with exact
  session tenant matching, ACTIVE Projects entitlement, current permission /
  operation checks, transaction-bound persistence and durable event readback.
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
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
from typing import Any, Callable, Final, Mapping

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.auth.authentication import get_current_identity
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID
from tools.eos.auth.invitation_creation import create_invitation, InvitationCreationError
from tools.eos.auth.invited_member_admission import admit_invited_member, InvitedMemberAdmissionError
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentRepository, RoleAssignmentNotFoundError, RoleAssignmentRepositoryError,
)
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
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
from tools.eos.saas.projects.project_registry import (
    COLLECTION as PROJECT_COLLECTION,
    EVENT_COLLECTION as PROJECT_EVENT_COLLECTION,
    ProjectNotFound,
    ProjectRegistry,
    ProjectRegistryConflict,
    ProjectRegistryError,
)


VERSION: Final[str] = "v1.2.1-FOUNDER-INVITATION-AUTHORITY"
_READ = RequireTenantAuthorization("project:read", "project_list")
_DETAIL = RequireTenantAuthorization("project:read", "project_detail")
_CREATE = RequireTenantAuthorization("project:create", "project_create")
_UPDATE = RequireTenantAuthorization("project:update", "project_update")
_ARCHIVE = RequireTenantAuthorization("project:archive", "project_archive")
_FOUNDER_INVITE = RequireTenantAuthorization("tenant:membership:write", "membership_invite")
_FOUNDER_PRODUCT_ISSUE = RequireTenantAuthorization("tenant_product_entitlement:issue", "tenant_product_entitlement_issue")



class ProjectCreateRequest(BaseModel):
    """Bounded project creation input; actor, tenant, status and IDs stay EOS-owned."""

    model_config = ConfigDict(extra="forbid", strict=True)

    name: str = Field(min_length=1, max_length=180)
    code: str | None = Field(default=None, max_length=80)
    summary: str | None = Field(default=None, max_length=4000)
    start_date: date | None = None
    target_date: date | None = None


class ProjectUpdateRequest(BaseModel):
    """Revision-guarded update; status transition cannot be mixed with edits."""

    model_config = ConfigDict(extra="forbid", strict=True)

    expected_revision: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=180)
    code: str | None = Field(default=None, max_length=80)
    summary: str | None = Field(default=None, max_length=4000)
    start_date: date | None = None
    target_date: date | None = None
    status: ProjectStatus | None = None


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


def _require_active_projects_entitlement(tenant_id: str, session: Any) -> None:
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
) -> Any:
    """Run one exact-tenant operation in a caller-owned majority transaction.

    PyMongo's transaction callback retries begin from fresh snapshot state; all
    project and entitlement reads in each attempt receive the exact callback
    session. Index DDL belongs to the application startup readiness gate.
    """
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
        with client.start_session() as mongo_session:
            return mongo_session.with_transaction(
                lambda current: _execute_with_entitlement(
                    context, registry, callback, current
                ),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except HTTPException:
        raise
    except ProjectNotFound as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except ProjectRegistryConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except ProjectError as error:
        raise HTTPException(status_code=422, detail=error.code) from error
    except ProjectRegistryError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except PyMongoError as error:
        raise HTTPException(status_code=503, detail="PROJECT_DATABASE_UNAVAILABLE") from error
    except Exception as error:
        raise HTTPException(status_code=503, detail="PROJECT_TRANSACTION_UNAVAILABLE") from error


def _execute_with_entitlement(
    context: TenantAuthorizationContext,
    registry: ProjectRegistry,
    callback: Callable[[ProjectRegistry, Any], Any],
    session: Any,
) -> Any:
    """Compose entitlement before invoking the source-owned project operation."""
    _require_active_projects_entitlement(context.tenant_id, session)
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


@router.get("")
def list_projects(
    response: Response,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    project_status: ProjectStatus | None = None,
    include_archived: bool = False,
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, object]:
    """Read the current tenant's bounded project page under current IAM."""
    response.headers["Cache-Control"] = "no-store"

    def load(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        items = registry.list_for_tenant(
            tenant_id=context.tenant_id,
            session=session,
            limit=limit,
            offset=offset,
            status=project_status,
            include_archived=include_archived,
        )
        return {
            "schema": "WILSY-PROJECT-LIST/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "items": [item.to_dict() for item in items],
            "limit": limit,
            "offset": offset,
        }

    return _transaction(context, load)


@router.get("/summary")
def project_summary(
    response: Response,
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, object]:
    """Return tenant-scoped status counts derived from validated project records."""
    response.headers["Cache-Control"] = "no-store"
    return _transaction(
        context,
        lambda registry, session: {
            "schema": "WILSY-PROJECT-SUMMARY/V1",
            "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id,
            "counts": registry.summary_for_tenant(
                tenant_id=context.tenant_id, session=session
            ),
        },
    )


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
            code=payload.code,
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
        return _result(
            context,
            value,
            events=registry.list_events(
                tenant_id=context.tenant_id,
                project_id=project_id,
                session=session,
            ),
        )

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
    values = payload.model_dump(exclude={"expected_revision"}, exclude_unset=True)
    status_value = values.pop("status", None)
    if not values and status_value is None:
        raise HTTPException(status_code=422, detail="PROJECT_UPDATE_FIELDS_REQUIRED")
    if status_value is not None and values:
        raise HTTPException(status_code=422, detail="PROJECT_STATUS_TRANSITION_MUST_BE_ISOLATED")
    now = datetime.now(timezone.utc)

    def update(registry: ProjectRegistry, session: Any) -> dict[str, object]:
        if status_value is not None:
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
# VERSION: v1.2.1-FOUNDER-INVITATION-AUTHORITY
# AUTHORITY BOUNDARY: existing canonical tenant IAM and active product entitlement plus source-owned project persistence
# TENANT POSTURE: request tenant must equal authenticated session tenant; persistence and entitlement queries are exact-tenant scoped
# FAIL-CLOSED POSTURE: missing assignment, entitlement, current database, indexes, transaction, replay integrity, or readback denies or fails unavailable
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
