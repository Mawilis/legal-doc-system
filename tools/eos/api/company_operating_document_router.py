"""TITLE: WILSY OS Company Mission and Strategy HTTP Authority.
VERSION: v1.4.1-FOUNDER-REPOSITORY-CURRENTNESS-FAIL-CLOSED
AUTHORITY: Existing canonical tenant IAM; source lifecycle/registry own evidence.
EPITOME: Expose approved company documents and separately authorized author/
publication commands without reusing Legal agreements, HR files or Founder labels.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/company_operating_document_router.py
COLLABORATION / OWNERSHIP: Headquarters shared viewer, RequireTenantAuthorization,
company document lifecycle/registry; explicit operators own index provisioning.
CERTIFICATION / UPDATE DATE: 2026-11-22
CHANGELOG: v1.4.1-FOUNDER-REPOSITORY-CURRENTNESS-FAIL-CLOSED
maps source-currentness/repository transport failures to HTTP 503 without
exposing stack traces or bypassing publisher role and tenant isolation.
CHANGELOG: v1.4.0-FOUNDER-DURABLE-STRATEGY-SELF-RATIFICATION
admits separate Strategy-only Founder commands via existing READ session
authority and source-verified durable designation; reuses canonical registry
transactions and fingerprints. No staff/owner inherited publisher grant.
CHANGELOG: v1.3.0-GOVERNED-STRATEGY-PROJECT-LINK composes an explicit
read-only current exact-tenant Strategy project-link projection and an audited
link command requiring *both* canonical Strategy author and Projects read IAM,
current project entitlement, source publication/pillar/project revisions and
caller-owned majority transactions. Link command is fail-closed until the
separate registry's unique indexes are explicitly provisioned. No Strategy
publication, completion percentage or financial authority is created.
CHANGELOG: v1.2.0-AUTHENTICATED-FOUNDER-SESSION-EVIDENCE adds a
read-only authenticated session-principal evidence endpoint; v1.1.0 adds a
fixed-reader grant endpoint and existing-session currentness enforcement. All
publication endpoints, source ownership and independent approval remain unchanged.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Authenticated own-principal evidence and governed reader grant only; no generated policy, public draft,
raw persistence diagnostics, PII logs, automatic DDL or browser-owned approval.
TENANT BOUNDARY: Canonical WILSY company tenant only after current central IAM.
AUTHORITY BOUNDARY: Read/author/publish are distinct current permissions. The
publisher must differ from the author. Published content is source truth only.
TRANSACTION BOUNDARY: HTTP owns snapshot/majority transactions and whole retries;
response occurs after commit. No source command permits financial execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any, Callable, Final

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from pymongo import ReadPreference
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.api.tenant_authorization_http import (
    OptionalTenantAuthorization, RequireTenantAuthorization, TenantAuthorizationContext,
)
from tools.eos.auth.authentication import get_current_identity
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.auth.company_document_reader_grant import CompanyDocumentReaderGrant, CompanyReaderGrantError
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID
from tools.eos.auth.founder_institutional_designation import (
    read_founder_designation, FounderDesignationRejected,
)
from tools.eos.kernel import db as kernel_db
from tools.eos.saas.company_operating_document_registry import CompanyOperatingDocumentRegistry
from tools.eos.saas.strategy_project_relationship_registry import (
    StrategyProjectLinkError, StrategyProjectRelationshipRegistry,
)
from tools.eos.saas.projects.project_registry import (
    ProjectRegistry, ProjectNotFound, ProjectRegistryError, COLLECTION as PROJECT_COLLECTION,
    EVENT_COLLECTION as PROJECT_EVENT_COLLECTION,
)
from tools.eos.api.projects_router import _require_active_projects_entitlement
from tools.eos.saas.domain.company_operating_document import (
    CompanyDocumentClass, CompanyDocumentError, CompanyDocumentState,
    CompanyOperatingDocumentRevision, instant,
)

VERSION: Final = "v1.4.1-FOUNDER-REPOSITORY-CURRENTNESS-FAIL-CLOSED"
def _require_current_company_session(identity: SovereignIdentity = Depends(get_current_identity)) -> None:
    """Reuse canonical authentication and session authority; never mint a session.

    GLOBAL authentication already checks selected membership/capacity currentness.
    Legacy TENANT authentication checks credential revision; this boundary also
    checks its existing exact durable session reference. Absence/expiry is 401,
    while an unavailable currentness source is 503, never an unpublished result.
    """
    if identity.principal_scope == "GLOBAL":
        return
    if identity.principal_scope not in (None, "TENANT") or not identity.session_reference:
        raise _error("COMPANY_DOCUMENT_SESSION_REQUIRED", 401)
    try:
        current = AuthRegistry().is_session_current(identity.tenant_id, identity.identity_id, identity.session_reference)
    except Exception as error:
        logger.error("Company session currentness unavailable", extra={"error_code": "COMPANY_DOCUMENT_SESSION_SOURCE_UNAVAILABLE"})
        raise _error("COMPANY_DOCUMENT_SESSION_SOURCE_UNAVAILABLE") from error
    if current is not True:
        raise _error("COMPANY_DOCUMENT_SESSION_STALE", 401)


router = APIRouter(prefix="/company-operating-documents", tags=["Company Operating Documents"],
                   dependencies=[Depends(_require_current_company_session)])
logger = logging.getLogger("WilsyOS.CompanyOperatingDocuments")
_GRANT = RequireTenantAuthorization("tenant:role_assignment:write", "role_grant")
_READ = RequireTenantAuthorization("company_operating_document:read", "company_operating_document_read")
_PROJECT_READ = RequireTenantAuthorization("project:read", "project_detail")
_AUTHOR = RequireTenantAuthorization("company_operating_document:author", "company_operating_document_author")
_PUBLISH = RequireTenantAuthorization("company_operating_document:publish", "company_operating_document_publish")
_MAY_AUTHOR = OptionalTenantAuthorization("company_operating_document:author", "company_operating_document_author")
_MAY_PUBLISH = OptionalTenantAuthorization("company_operating_document:publish", "company_operating_document_publish")


class ReaderGrantInput(BaseModel):
    """Fixed-reader command material; actor/tenant/role derive only from EOS.

    Approval reference records the independent authorized grantor's decision;
    it is not a permission or an alternative to maker/checker authority.
    """

    model_config = ConfigDict(extra="forbid", strict=True)
    target_principal_id: str = Field(min_length=1, max_length=128)
    target_business_role: str = Field(min_length=1, max_length=128)
    expected_membership_revision: int = Field(ge=0)
    expected_capacity_revision: int = Field(ge=0)
    expected_assignment_revision: int | None
    approval_reference: str = Field(min_length=1, max_length=48)
    reason_reference: str = Field(min_length=1, max_length=256)
    idempotency_key: str = Field(min_length=1, max_length=200)


@router.post("/reader-grants")
def grant_company_reader(payload: ReaderGrantInput, response: Response,
                         context: TenantAuthorizationContext = Depends(_GRANT)) -> dict[str, Any]:
    """Commit one governed reader grant; never infer permission from a receipt.

    Existing current tenant_admin and EnterpriseAdmin authority, independent
    actor, policy edge and exact target revisions are checked in the transaction.
    Runtime reads inspect required uniqueness; they never provision indexes.
    Grant/replay output is historical evidence. Fresh document reads and durable
    evidence/assignment readback remain required after canonical execution.
    """
    response.headers["Cache-Control"] = "no-store"
    if context.tenant_id != WILSY_COMPANY_TENANT_ID:
        raise _error("COMPANY_READER_GRANT_DENIED", 403)
    database = kernel_db.get_database()
    if database is None:
        raise _error("COMPANY_READER_SOURCE_UNAVAILABLE")
    try:
        command = CompanyDocumentReaderGrant(database)
        command.require_indexes()
        selected = context.identity.roles[0] if context.identity.principal_scope == "GLOBAL" and len(context.identity.roles) == 1 else None
        return _transaction(context, lambda registry, session: command.execute(
            actor_principal_id=context.identity.identity_id, tenant_id=context.tenant_id,
            selected_business_role=selected, session=session, **payload.model_dump()))
    except CompanyReaderGrantError as error:
        if error.status >= 500:
            logger.error("Company reader grant unavailable", extra={"error_code": error.code})
        raise _error(error.code, error.status) from error
    except PyMongoError as error:
        raise _error("COMPANY_READER_SOURCE_UNAVAILABLE") from error


@router.get("/founder-session-evidence")
def founder_session_evidence(
    response: Response,
    identity: SovereignIdentity = Depends(get_current_identity),
) -> dict[str, Any]:
    """Read authenticated principal and selected tenant from EOS, not browser claims.

    Router-level session-currentness dependency must succeed first. This
    endpoint makes no IAM grants, exposes no bearer/session references, and
    does not assert that a matching durable role assignment exists. A GLOBAL
    session must be validated by the existing authentication dependency.
    """
    response.headers["Cache-Control"] = "no-store"
    if identity.tenant_id != WILSY_COMPANY_TENANT_ID:
        raise _error("FOUNDER_SESSION_TENANT_DENIED", 403)
    if identity.principal_scope not in ("GLOBAL", "TENANT", None):
        raise _error("FOUNDER_SESSION_SCOPE_DENIED", 403)
    principal_id = identity.identity_id
    if not isinstance(principal_id, str) or not principal_id.strip():
        raise _error("FOUNDER_SESSION_IDENTITY_UNAVAILABLE", 401)
    # Claims are reported as claims. They do not establish current IAM grants.
    claimed_capacity = identity.roles[0] if len(identity.roles) == 1 else None
    return {
        "schema": "WILSY-FOUNDER-SESSION-EVIDENCE/V1",
        "state": "AUTHENTICATED_SESSION_OBSERVED",
        "principal_id": principal_id,
        "tenant_id": identity.tenant_id,
        "principal_scope": identity.principal_scope,
        "selected_capacity_claim": claimed_capacity,
        "capacity_authority_verified_by_this_endpoint": False,
        "grant_issued": False,
        "administrative_grantor_appointed": False,
    }


class SectionInput(BaseModel):
    """Bounded proposed plain text; receiving it never approves company policy."""

    model_config = ConfigDict(extra="forbid", strict=True)
    section_id: str = Field(pattern=r"^[a-z][a-z0-9-]{0,63}$")
    title: str = Field(min_length=1, max_length=160)
    body: str = Field(min_length=1, max_length=20_000)


class DraftInput(BaseModel):
    """Author input only; tenant, actor, state, digest and approval stay server-owned."""

    model_config = ConfigDict(extra="forbid", strict=True)
    expected_revision: int = Field(ge=0)
    title: str = Field(min_length=1, max_length=200)
    document_version: str = Field(pattern=r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)$", max_length=40)
    sections: list[SectionInput] = Field(min_length=1, max_length=24)


class StrategyProjectLinkInput(BaseModel):
    """Explicit current source revisions for one EOS-persisted Strategy association.

    The tenant, current principal, real publication fingerprint, project source
    snapshot, command evidence and majority transaction are server governed.
    """
    model_config = ConfigDict(extra="forbid", strict=True)
    pillar_id: str = Field(pattern=r"^pillar-(?:one|two|three|four|five|six)$")
    project_id: str = Field(pattern=r"^prj-[a-f0-9]{48}$")
    expected_strategy_revision: int = Field(ge=1)
    expected_project_revision: int = Field(ge=1)


class RevisionInput(BaseModel):
    """Explicit expected revision; no client-supplied lifecycle status is admitted."""

    model_config = ConfigDict(extra="forbid", strict=True)
    expected_revision: int = Field(ge=1)


class PublishInput(RevisionInput):
    """A publisher's decision reference/date; IAM and independent actor are mandatory."""

    approval_reference: str = Field(min_length=1, max_length=500)
    effective_from: str = Field(min_length=1, max_length=50)


def _error(code: str, status_code: int = 503) -> HTTPException:
    return HTTPException(status_code=status_code,
                         detail={"error": code, "message": "The company-document source could not authorize or verify this operation."},
                         headers={"Cache-Control": "no-store"})


def _same_actor(candidate: TenantAuthorizationContext | None, base: TenantAuthorizationContext) -> bool:
    return bool(candidate is not None and candidate.tenant_id == base.tenant_id
                and candidate.identity.identity_id == base.identity.identity_id)


def _transaction(context: TenantAuthorizationContext, callback: Callable[..., Any], *, write: bool = False) -> Any:
    if context.tenant_id != WILSY_COMPANY_TENANT_ID:
        raise _error("COMPANY_DOCUMENT_ACCESS_DENIED", 403)
    client, database = kernel_db.get_client(), kernel_db.get_database()
    if client is None or database is None:
        raise _error("COMPANY_DOCUMENT_SOURCE_UNAVAILABLE")
    registry = CompanyOperatingDocumentRegistry(database)
    try:
        if write:
            registry.require_command_indexes()
        # Driver transient retries restart the entire callback. A concurrent
        # unique-key winner also requires a new transaction before replay lookup.
        for attempt in range(3):
            try:
                with client.start_session() as session:
                    return session.with_transaction(
                        lambda current: callback(registry, current),
                        read_concern=ReadConcern("snapshot"),
                        write_concern=WriteConcern(w="majority", j=True),
                        read_preference=ReadPreference.PRIMARY,
                    )
            except DuplicateKeyError:
                if attempt == 2:
                    raise _error("COMPANY_DOCUMENT_REVISION_CONFLICT", 409)
    except CompanyDocumentError as error:
        code = error.code
        conflict = any(marker in code for marker in ("CONFLICT", "ALREADY_PUBLISHED"))
        denied = any(marker in code for marker in (
            "TENANT_DENIED", "OWNER_REQUIRED", "SUBMISSION_DENIED",
            "INDEPENDENT_APPROVER_REQUIRED", "FOUNDER_AUTHORITY_DENIED",
            "FOUNDER_AUTHOR_REQUIRED", "FOUNDER_STRATEGY_ONLY",
        ))
        integrity = any(marker in code for marker in (
            "INTEGRITY", "PERSISTED", "LINEAGE", "READBACK", "INDEX",
            "HISTORY_LIMIT", "TRANSACTION_REQUIRED", "FOUNDER_SOURCE_UNAVAILABLE",
        ))
        if integrity:
            logger.error("Company document integrity/source operation failed", extra={"error_code": code})
        raise _error(code, 409 if conflict else 403 if denied else 503 if integrity else 422) from error
    except HTTPException:
        raise
    except PyMongoError as error:
        logger.error("Company document persistence unavailable", extra={"error_code": "COMPANY_DOCUMENT_SOURCE_UNAVAILABLE"})
        raise _error("COMPANY_DOCUMENT_SOURCE_UNAVAILABLE") from error
    raise _error("COMPANY_DOCUMENT_SOURCE_UNAVAILABLE")


def _actions(context: TenantAuthorizationContext, latest: CompanyOperatingDocumentRevision | None,
             author: TenantAuthorizationContext | None, publisher: TenantAuthorizationContext | None,
             *, review: bool, founder: bool = False) -> list[str]:
    actions = ["READ_HISTORY"]
    can_author, can_publish = _same_actor(author, context), _same_actor(publisher, context)
    if can_author or can_publish or founder:
        actions.append("REVIEW_DRAFTS")
    if founder and (latest is None or latest.state is CompanyDocumentState.PUBLISHED):
        actions.append("FOUNDER_CREATE_DRAFT")
    if can_author and (latest is None or latest.state is CompanyDocumentState.PUBLISHED):
        actions.append("CREATE_DRAFT")
    if review and latest is not None:
        if can_author and latest.state is CompanyDocumentState.DRAFT and latest.author_principal_id == context.identity.identity_id:
            actions.append("SUBMIT")
        if can_publish and latest.state is CompanyDocumentState.SUBMITTED and latest.author_principal_id != context.identity.identity_id:
            actions.append("PUBLISH")
        if founder and latest.author_principal_id == context.identity.identity_id:
            if latest.state is CompanyDocumentState.DRAFT:
                actions.append("FOUNDER_SUBMIT")
            elif latest.state is CompanyDocumentState.SUBMITTED:
                actions.append("FOUNDER_RATIFY")
    return actions


@router.get("/{classification}")
def read_company_document(
    classification: CompanyDocumentClass, response: Response,
    review: bool = False, revision: int | None = Query(default=None, ge=1),
    context: TenantAuthorizationContext = Depends(_READ),
    author: TenantAuthorizationContext | None = Depends(_MAY_AUTHOR),
    publisher: TenantAuthorizationContext | None = Depends(_MAY_PUBLISH),
) -> dict[str, Any]:
    """Read current effective publication or explicitly authorized review/history.

    No draft, submission, future publication or private revision count is exposed
    to ordinary readers. Actor/tenant scope is revalidated on every request.
    """
    response.headers["Cache-Control"] = "no-store"
    may_review = _same_actor(author, context) or _same_actor(publisher, context)
    now = datetime.now(timezone.utc)
    def load(registry: CompanyOperatingDocumentRegistry, session: Any) -> dict[str, Any]:
        founder = False
        if classification is CompanyDocumentClass.STRATEGY:
            try:
                founder = read_founder_designation(
                    principal_id=context.identity.identity_id,
                    tenant_id=context.tenant_id, database=kernel_db.get_database(),
                    session=session,
                ) is not None
            except (FounderDesignationRejected, RuntimeError, PyMongoError) as error:
                raise _error("COMPANY_DOCUMENT_FOUNDER_SOURCE_UNAVAILABLE") from error
        if review and not (may_review or founder):
            raise _error("COMPANY_DOCUMENT_REVIEW_DENIED", 403)
        history = registry.history(context.tenant_id, classification, session=session)
        latest = history[-1] if history else None
        permitted = history if review else tuple(item for item in history if item.state is CompanyDocumentState.PUBLISHED
                                                 and item.effective_from is not None and item.effective_from <= instant(now))
        selected = next((item for item in permitted if item.revision == revision), None) if revision is not None else (permitted[-1] if permitted else None)
        if revision is not None and selected is None:
            raise _error("COMPANY_DOCUMENT_NOT_FOUND", 404)
        return {
            "schema": "WILSY-COMPANY-OPERATING-DOCUMENT-VIEW/V1",
            "tenant_id": context.tenant_id, "principal_id": context.identity.identity_id,
            "classification": classification.value, "view": "review" if review else "published",
            "state": selected.state.value if selected else "NOT_YET_PUBLISHED",
            "document": selected.to_dict() if selected else None,
            "current_revision": latest.revision if (may_review or founder) and latest else selected.revision if selected else 0,
            "available_actions": _actions(context, latest, author, publisher, review=review, founder=founder) if revision is None else ["READ_HISTORY"],
            "relationships": {"state": "NOT_GOVERNED"}, "as_of": instant(now),
            "authority": {"publication_owned_by": "PYTHON_EOS", "financial_execution": False},
        }
    return _transaction(context, load)


def _strategy_publication(registry: CompanyOperatingDocumentRegistry, tenant_id: str,
                          session: Any, now: datetime) -> CompanyOperatingDocumentRevision:
    """Require a currently effective independently published Strategy revision."""
    history = registry.history(tenant_id, CompanyDocumentClass.STRATEGY, session=session)
    permitted = [item for item in history if item.state is CompanyDocumentState.PUBLISHED
                 and item.effective_from is not None and item.effective_from <= instant(now)]
    if not permitted:
        raise _error("STRATEGY_LINK_PUBLISHED_SOURCE_REQUIRED", 409)
    return permitted[-1]


def _project_source(database: Any, tenant_id: str, project_id: str, session: Any) -> Any:
    """Verify currently entitled exact-tenant project without membership inference."""
    _require_active_projects_entitlement(tenant_id, session)
    registry = ProjectRegistry(database[PROJECT_COLLECTION], database[PROJECT_EVENT_COLLECTION])
    try:
        return registry.get(tenant_id=tenant_id, project_id=project_id, session=session)
    except ProjectNotFound as error:
        raise _error("STRATEGY_LINK_PROJECT_NOT_VERIFIED", 404) from error
    except ProjectRegistryError as error:
        raise _error("STRATEGY_LINK_PROJECT_SOURCE_UNAVAILABLE") from error


def _same_scope(base: TenantAuthorizationContext, candidate: TenantAuthorizationContext) -> bool:
    """Require identical authenticated principal and exact tenant at both authorities."""
    return _same_actor(candidate, base)


@router.get("/STRATEGY/project-links")
def read_strategy_project_links(
    response: Response,
    context: TenantAuthorizationContext = Depends(_READ),
    project_context: TenantAuthorizationContext = Depends(_PROJECT_READ),
) -> dict[str, Any]:
    """Show only current document and project evidence authorized for same actor.

    A verified relationship does NOT imply a verified strategic outcome score.
    Obsolete snapshots are marked as changed, never counted as progress.
    """
    response.headers["Cache-Control"] = "no-store"
    if not _same_scope(context, project_context):
        raise _error("STRATEGY_LINK_AUTHORITY_MISMATCH", 403)
    now = datetime.now(timezone.utc)
    def load(registry: CompanyOperatingDocumentRegistry, session: Any) -> dict[str, Any]:
        database = kernel_db.get_database()
        if database is None:
            raise _error("STRATEGY_LINK_SOURCE_UNAVAILABLE")
        publication = _strategy_publication(registry, context.tenant_id, session, now)
        relationships = StrategyProjectRelationshipRegistry(database)
        rows = relationships.list_links(tenant_id=context.tenant_id, session=session)
        items: list[dict[str, object]] = []
        for row in rows:
            project = _project_source(database, context.tenant_id, str(row["project_id"]), session)
            pillar_id = str(row["pillar_id"])
            pillar_is_current = any(section.section_id == pillar_id for section in publication.sections)
            source_current = (pillar_is_current
                and row["strategy_fingerprint"] == publication.fingerprint
                and row["strategy_revision"] == publication.revision
                and row["project_revision"] == project.revision)
            items.append({"pillar_id": pillar_id, "project_id": project.project_id,
                          "project_name": project.name, "project_status": project.status.value,
                          "source_project_revision": project.revision,
                          "source_strategy_revision": publication.revision,
                          "state": "VERIFIED_CURRENT" if source_current else "SOURCE_CHANGED"})
        return {"schema": "WILSY-STRATEGY-PROJECT-LINK-LIST/V1",
                "tenant_id": context.tenant_id, "principal_id": context.identity.identity_id,
                "classification": "STRATEGY", "strategy_revision": publication.revision,
                "items": items, "source_verified": True, "strategy_progress": None,
                "financial_execution": False}
    try:
        return _transaction(context, load)
    except StrategyProjectLinkError as error:
        raise _error(error.code) from error


@router.post("/STRATEGY/project-links", status_code=201)
def create_strategy_project_link(
    payload: StrategyProjectLinkInput, response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_AUTHOR),
    read_context: TenantAuthorizationContext = Depends(_READ),
    project_context: TenantAuthorizationContext = Depends(_PROJECT_READ),
) -> dict[str, Any]:
    """Create a source-owned audited relationship, never a strategy completion.

    Independent company author, company read and project read rights are
    mandatory. Both source objects and exact revisions are checked within the
    same majority transaction as link and immutable event persistence.
    """
    response.headers["Cache-Control"] = "no-store"
    if not _same_scope(context, read_context) or not _same_scope(context, project_context):
        raise _error("STRATEGY_LINK_AUTHORITY_MISMATCH", 403)
    if not idempotency_key:
        raise _error("STRATEGY_LINK_IDEMPOTENCY_REQUIRED", 422)
    now = datetime.now(timezone.utc)
    database = kernel_db.get_database()
    if database is None:
        raise _error("STRATEGY_LINK_SOURCE_UNAVAILABLE")
    link_registry = StrategyProjectRelationshipRegistry(database)
    try:
        link_registry.require_indexes()
    except StrategyProjectLinkError as error:
        raise _error(error.code) from error

    def persist(registry: CompanyOperatingDocumentRegistry, session: Any) -> dict[str, Any]:
        publication = _strategy_publication(registry, context.tenant_id, session, now)
        if publication.revision != payload.expected_strategy_revision:
            raise _error("STRATEGY_LINK_PUBLICATION_REVISION_CONFLICT", 409)
        if not any(section.section_id == payload.pillar_id for section in publication.sections):
            raise _error("STRATEGY_LINK_PILLAR_NOT_VERIFIED", 409)
        project = _project_source(database, context.tenant_id, payload.project_id, session)
        if project.revision != payload.expected_project_revision or project.status.value != "active":
            raise _error("STRATEGY_LINK_PROJECT_REVISION_CONFLICT", 409)
        receipt = link_registry.link(
            tenant_id=context.tenant_id, actor_id=context.identity.identity_id,
            project_id=project.project_id, pillar_id=payload.pillar_id,
            strategy_revision=publication.revision, strategy_fingerprint=publication.fingerprint,
            project_revision=project.revision, idempotency_key=idempotency_key,
            recorded_at=instant(now), session=session,
        )
        return {"schema": "WILSY-STRATEGY-PROJECT-LINK-RESULT/V1",
                "tenant_id": context.tenant_id, "principal_id": context.identity.identity_id,
                "classification": "STRATEGY", "pillar_id": payload.pillar_id,
                "project_id": project.project_id, "strategy_revision": publication.revision,
                "project_revision": project.revision,
                "command_fingerprint": receipt["command_fingerprint"],
                "relationship_state": "RECORDED_NOT_OUTCOME_CERTIFIED",
                "strategy_progress": None, "financial_execution": False}
    try:
        return _transaction(context, persist)
    except StrategyProjectLinkError as error:
        conflict = "CONFLICT" in error.code or "ALREADY_EXISTS" in error.code
        raise _error(error.code, 409 if conflict else 503) from error


@router.get("/{classification}/revisions")
def company_document_history(
    classification: CompanyDocumentClass, response: Response, review: bool = False,
    context: TenantAuthorizationContext = Depends(_READ),
    author: TenantAuthorizationContext | None = Depends(_MAY_AUTHOR),
    publisher: TenantAuthorizationContext | None = Depends(_MAY_PUBLISH),
) -> dict[str, Any]:
    """Read permitted revision metadata; draft content/counts stay private."""
    response.headers["Cache-Control"] = "no-store"
    may_review = _same_actor(author, context) or _same_actor(publisher, context)
    now = datetime.now(timezone.utc)
    def load(registry: CompanyOperatingDocumentRegistry, session: Any) -> dict[str, Any]:
        founder = False
        if review and classification is CompanyDocumentClass.STRATEGY:
            try:
                founder = read_founder_designation(
                    principal_id=context.identity.identity_id,
                    tenant_id=context.tenant_id, database=kernel_db.get_database(),
                    session=session,
                ) is not None
            except (FounderDesignationRejected, RuntimeError, PyMongoError) as error:
                raise _error("COMPANY_DOCUMENT_FOUNDER_SOURCE_UNAVAILABLE") from error
        if review and not (may_review or founder):
            raise _error("COMPANY_DOCUMENT_REVIEW_DENIED", 403)
        history = registry.history(context.tenant_id, classification, session=session)
        visible = [item for item in history if review or (item.state is CompanyDocumentState.PUBLISHED
                   and item.effective_from is not None and item.effective_from <= instant(now))]
        return {"schema": "WILSY-COMPANY-OPERATING-DOCUMENT-HISTORY/V1", "tenant_id": context.tenant_id,
                "principal_id": context.identity.identity_id, "classification": classification.value,
                "view": "review" if review else "published", "as_of": instant(now),
                "items": [{key: value for key, value in item.to_dict().items() if key != "sections"} for item in reversed(visible)]}
    return _transaction(context, load)


def _command(classification: CompanyDocumentClass, context: TenantAuthorizationContext, action: str,
             payload: dict[str, Any], expected_revision: int, key: str | None, response: Response) -> dict[str, Any]:
    response.headers["Cache-Control"] = "no-store"
    if not key:
        raise _error("COMPANY_DOCUMENT_IDEMPOTENCY_REQUIRED", 422)
    now = datetime.now(timezone.utc)
    record = _transaction(context, lambda registry, session: registry.command(
        context.tenant_id, classification, actor_id=context.identity.identity_id, action=action,
        payload=payload, expected_revision=expected_revision, idempotency_key=key, now=now, session=session,
    ), write=True)
    return {"schema": "WILSY-COMPANY-OPERATING-DOCUMENT-COMMAND-RESULT/V1", "tenant_id": context.tenant_id,
            "principal_id": context.identity.identity_id, "classification": classification.value, "document": record.to_dict()}


@router.post("/STRATEGY/founder-drafts", status_code=201)
def founder_strategy_draft(
    payload: DraftInput, response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, Any]:
    """Founder-specific author command; registry rechecks the durable designation."""
    body = payload.model_dump()
    expected = body.pop("expected_revision")
    return _command(CompanyDocumentClass.STRATEGY, context, "FOUNDER_CREATE_DRAFT",
                    body, expected, idempotency_key, response)


@router.post("/STRATEGY/founder-submit")
def founder_strategy_submit(
    payload: RevisionInput, response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, Any]:
    """Submit only the same Founder's private Strategy revision."""
    return _command(CompanyDocumentClass.STRATEGY, context, "FOUNDER_SUBMIT",
                    {}, payload.expected_revision, idempotency_key, response)


class FounderRatifyInput(RevisionInput):
    """Explicit date chosen by the Founder; decision basis remains server-owned."""
    effective_from: str = Field(min_length=1, max_length=50)


@router.post("/STRATEGY/founder-ratify")
def founder_strategy_ratify(
    payload: FounderRatifyInput, response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, Any]:
    """Ratify a submitted Founder-authored Strategy; reference is server owned."""
    return _command(CompanyDocumentClass.STRATEGY, context, "FOUNDER_RATIFY",
                    {"effective_from": payload.effective_from},
                    payload.expected_revision, idempotency_key, response)


@router.post("/{classification}/drafts", status_code=201)
def create_company_document_draft(classification: CompanyDocumentClass, payload: DraftInput, response: Response,
                                  idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
                                  context: TenantAuthorizationContext = Depends(_AUTHOR)) -> dict[str, Any]:
    """Persist a proposed draft only; no official purpose, strategy or approval is inferred."""
    body = payload.model_dump()
    expected = body.pop("expected_revision")
    return _command(classification, context, "CREATE_DRAFT", body, expected, idempotency_key, response)


@router.post("/{classification}/submit")
def submit_company_document(classification: CompanyDocumentClass, payload: RevisionInput, response: Response,
                            idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
                            context: TenantAuthorizationContext = Depends(_AUTHOR)) -> dict[str, Any]:
    """Submit the current author's draft with exact replay and expected-revision protection."""
    return _command(classification, context, "SUBMIT", {}, payload.expected_revision, idempotency_key, response)


@router.post("/{classification}/publish")
def publish_company_document(classification: CompanyDocumentClass, payload: PublishInput, response: Response,
                             idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
                             context: TenantAuthorizationContext = Depends(_PUBLISH)) -> dict[str, Any]:
    """Record an independently authorized publisher's explicit approval and effective date.

    The source verifies submission and a different author/publisher principal.
    Commit precedes response; clients must independently re-read durable truth.
    """
    return _command(classification, context, "PUBLISH", {
        "approval_reference": payload.approval_reference, "effective_from": payload.effective_from,
    }, payload.expected_revision, idempotency_key, response)


# ARTIFACT: company_operating_document_router.py
# VERSION: v1.4.1-FOUNDER-REPOSITORY-CURRENTNESS-FAIL-CLOSED
# AUTHORITY BOUNDARY: Current canonical IAM plus source-owned lifecycle commands.
# TENANT POSTURE: Exact canonical WILSY company tenant; no root fallback.
# FAIL-CLOSED POSTURE: Draft privacy, independent approval, indexes and readback required.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
