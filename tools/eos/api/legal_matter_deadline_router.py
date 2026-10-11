"""Wilsy OS Legal Matter Deadline HTTP router.

TITLE: Wilsy OS Legal Matter Deadline HTTP Router
VERSION: v1.1.0-LEGAL-OPS-COMPLETION-D5-DEADLINE-OBSERVABILITY
AUTHORITY: Wilsy OS Core Governance / FastAPI transport composition only.
EPITOME: Expose authenticated tenant-scoped deadline create/read transport over
         the certified D3A service and emit bounded post-authorization operational
         telemetry without duplicating legal, persistence, IAM, or evidence truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/legal_matter_deadline_router.py
COLLABORATION / OWNERSHIP: D1 owns deadline semantics; D2 owns persistence;
                            D3A owns matter/deadline orchestration; D3B owns HTTP;
                            D5 adds bounded transport observability only.
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.1.0-LEGAL-OPS-COMPLETION-D5-DEADLINE-OBSERVABILITY
           adds pseudonymized success/failure/count telemetry for authorized
           deadline create/list/detail handlers after canonical transaction
           outcomes, excluding evidence contents and authority-bearing input.
           2026-10-11 v1.0.0-LEGAL-OPS-COMPLETION-D3B1-DEADLINE-HTTP-ROUTER
           establishes exact read/write authorization dependencies, strict POST
           input, API-owned Mongo transaction composition, D3A-only delegation,
           bounded tenant/matter/deadline absence, and secret-safe responses.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Caller-supplied identity, role, permission, tenant
                             authority, AI, filing, service, payment, and
                             settlement fields are rejected as extras.
TENANT BOUNDARY: X-Tenant-ID is accepted only through durable
                 RequireTenantAuthorization and is forwarded unchanged to D3A.
AUTHORITY BOUNDARY: Transport only; no deadline calculation, lifecycle
                    invention, matter truth, persistence truth, AI, filing,
                    service, court, representation, billing, or payment authority.
TRANSACTION BOUNDARY: The API owns one session/transaction per request, passes
                      the exact active session to D3A, commits only on success,
                      aborts on failure, and performs no blind retry.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Invalid input, denied authority, absence, conflict,
                         corruption, persistence failure, and unexpected errors
                         return bounded non-success responses; telemetry failure
                         never changes legal/transaction outcomes.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import logging
from typing import Any, Callable, Final, TypeVar

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.legal_operations.domain.legal_matter_deadline import (
    LegalMatterDeadline,
    LegalMatterDeadlineKind,
    LegalMatterDeadlineSourceType,
    LegalMatterDeadlineStatus,
)
from tools.eos.legal_operations.registry.legal_matter_deadline_registry import (
    COLLECTION as DEADLINE_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
)
from tools.eos.legal_operations.service.legal_matter_deadline_service import (
    LegalMatterDeadlineServiceError,
    get_legal_matter_deadline,
    list_legal_matter_deadlines,
    record_legal_matter_deadline,
)


VERSION: Final[str] = "v1.1.0-LEGAL-OPS-COMPLETION-D5-DEADLINE-OBSERVABILITY"
logger = logging.getLogger("WilsyOS.API.LegalMatterDeadlineRouter")
router = APIRouter(prefix="/legal-operations", tags=["Legal Operations Deadlines"])
_T = TypeVar("_T")


def _telemetry_ref(value: str) -> str:
    """Return a deterministic SHA3-512 pseudonymous locator for telemetry only."""
    return hashlib.sha3_512(value.encode("utf-8")).hexdigest()


def _observe(
    *,
    operation: str,
    outcome: str,
    tenant_id: str,
    case_matter_id: str,
    deadline_id: str | None = None,
    count: int | None = None,
    http_status: int = 200,
    error_code: str | None = None,
) -> None:
    """Emit bounded operational telemetry without exposing legal evidence content.

    Telemetry is non-authoritative and intentionally excludes source references,
    evidence fingerprints, titles, timestamps, principal identity, role, and
    financial/AI fields. Logging failure cannot alter the request outcome.
    """
    payload: dict[str, Any] = {
        "event": "LEGAL_MATTER_DEADLINE_HTTP",
        "operation": operation,
        "outcome": outcome,
        "tenant_ref": _telemetry_ref(tenant_id),
        "matter_ref": _telemetry_ref(case_matter_id),
        "http_status": http_status,
    }
    if deadline_id is not None:
        payload["deadline_ref"] = _telemetry_ref(deadline_id)
    if count is not None:
        payload["count"] = count
    if error_code is not None:
        payload["error_code"] = error_code
    try:
        logger.log(
            logging.INFO if outcome == "SUCCESS" else logging.WARNING,
            "LEGAL_MATTER_DEADLINE_HTTP",
            extra={"wilsy_observation": payload},
        )
    except Exception:
        return


class LegalMatterDeadlineCommand(BaseModel):
    """Strict caller-supplied deadline evidence with all authority fields excluded."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    deadline_id: str = Field(min_length=1, max_length=160)
    deadline_kind: LegalMatterDeadlineKind
    title: str = Field(min_length=1, max_length=240)
    due_at: datetime
    source_type: LegalMatterDeadlineSourceType
    source_reference: str = Field(min_length=1, max_length=512)
    source_evidence_fingerprint: str = Field(min_length=128, max_length=128)
    jurisdiction_reference: str = Field(min_length=1, max_length=240)
    created_at: datetime
    supersedes_deadline_id: str | None = Field(default=None, max_length=160)
    status: LegalMatterDeadlineStatus = LegalMatterDeadlineStatus.ACTIVE


class DeadlineHttpError(RuntimeError):
    """Stable transport failure that exposes no persistence or authority internals."""

    def __init__(self, code: str, cause: BaseException | None = None) -> None:
        self.code = code
        super().__init__(code)
        if cause is not None:
            self.__cause__ = cause


def _db_handles() -> tuple[Any, Any]:
    """Resolve the configured Kernel Mongo client/database only on request."""
    from tools.eos.kernel.db import get_client, get_database

    return get_client(), get_database()


def _collection(database: Any, name: str) -> Any:
    if database is None:
        raise DeadlineHttpError("DEADLINE_HTTP_UNAVAILABLE")
    try:
        return database.get_collection(name)
    except Exception as error:
        raise DeadlineHttpError("DEADLINE_HTTP_UNAVAILABLE", error) from error


def _transaction(callback: Callable[[Any, Any], _T]) -> _T:
    """Run one deadline request in one API-owned caller transaction."""
    client, database = _db_handles()
    if client is None or database is None:
        raise DeadlineHttpError("DEADLINE_HTTP_UNAVAILABLE")
    try:
        with client.start_session() as session:
            session.start_transaction()
            try:
                result = callback(session, database)
                session.commit_transaction()
                return result
            except Exception:
                if bool(getattr(session, "in_transaction", False)):
                    session.abort_transaction()
                raise
    except (DeadlineHttpError, LegalMatterDeadlineServiceError):
        raise
    except Exception as error:
        raise DeadlineHttpError("DEADLINE_HTTP_UNAVAILABLE", error) from error


def _http_error(error: BaseException) -> HTTPException:
    code = getattr(error, "code", "DEADLINE_HTTP_UNAVAILABLE")
    if code == "DEADLINE_INVALID":
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="LEGAL_MATTER_DEADLINE_INVALID",
        )
    if code in {"DEADLINE_MATTER_NOT_AVAILABLE", "DEADLINE_NOT_AVAILABLE"}:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LEGAL_MATTER_DEADLINE_NOT_AVAILABLE",
        )
    if code == "DEADLINE_CONFLICT":
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="LEGAL_MATTER_DEADLINE_CONFLICT",
        )
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="LEGAL_MATTER_DEADLINE_UNAVAILABLE",
    )


def _project(value: LegalMatterDeadline) -> dict[str, Any]:
    """Return a bounded transport projection with no persistence internals."""
    return {
        "deadline_id": value.deadline_id,
        "case_matter_id": value.case_matter_id,
        "deadline_kind": str(value.deadline_kind),
        "title": value.title,
        "due_at": value.due_at.isoformat(),
        "source_type": str(value.source_type),
        "jurisdiction_reference": value.jurisdiction_reference,
        "created_at": value.created_at.isoformat(),
        "supersedes_deadline_id": value.supersedes_deadline_id,
        "status": str(value.status),
    }


_WRITE = RequireTenantAuthorization(
    "legal_operations:matter_deadline:write",
    "legal_matter_deadline_write",
)
_READ = RequireTenantAuthorization(
    "legal_operations:matter_deadline:read",
    "legal_matter_deadline_read",
)


@router.post("/matters/{case_matter_id}/deadlines")
async def create_legal_matter_deadline(
    case_matter_id: str,
    command: LegalMatterDeadlineCommand,
    context: TenantAuthorizationContext = Depends(_WRITE),
) -> dict[str, Any]:
    """Create or exactly replay one evidenced own-tenant matter deadline."""

    def run(session: Any, database: Any) -> LegalMatterDeadline:
        return record_legal_matter_deadline(
            tenant_id=context.tenant_id,
            case_matter_id=case_matter_id,
            deadline_id=command.deadline_id,
            deadline_kind=command.deadline_kind,
            title=command.title,
            due_at=command.due_at,
            source_type=command.source_type,
            source_reference=command.source_reference,
            source_evidence_fingerprint=command.source_evidence_fingerprint,
            jurisdiction_reference=command.jurisdiction_reference,
            created_at=command.created_at,
            supersedes_deadline_id=command.supersedes_deadline_id,
            status=command.status,
            matter_collection=_collection(database, LIFECYCLE_COLLECTION),
            deadline_collection=_collection(database, DEADLINE_COLLECTION),
            session=session,
        )

    try:
        value = _transaction(run)
        _observe(
            operation="CREATE",
            outcome="SUCCESS",
            tenant_id=context.tenant_id,
            case_matter_id=case_matter_id,
            deadline_id=value.deadline_id,
        )
        return {"data": _project(value)}
    except (DeadlineHttpError, LegalMatterDeadlineServiceError) as error:
        http_error = _http_error(error)
        _observe(
            operation="CREATE",
            outcome="ERROR",
            tenant_id=context.tenant_id,
            case_matter_id=case_matter_id,
            deadline_id=command.deadline_id,
            http_status=http_error.status_code,
            error_code=getattr(error, "code", "DEADLINE_HTTP_UNAVAILABLE"),
        )
        raise http_error from error


@router.get("/matters/{case_matter_id}/deadlines")
async def list_matter_deadlines(
    case_matter_id: str,
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, Any]:
    """List immutable deadlines for one exact authorized tenant/matter scope."""

    def run(session: Any, database: Any) -> tuple[LegalMatterDeadline, ...]:
        return list_legal_matter_deadlines(
            tenant_id=context.tenant_id,
            case_matter_id=case_matter_id,
            deadline_collection=_collection(database, DEADLINE_COLLECTION),
            session=session,
        )

    try:
        values = _transaction(run)
        _observe(
            operation="LIST",
            outcome="SUCCESS",
            tenant_id=context.tenant_id,
            case_matter_id=case_matter_id,
            count=len(values),
        )
        return {"data": [_project(value) for value in values]}
    except (DeadlineHttpError, LegalMatterDeadlineServiceError) as error:
        http_error = _http_error(error)
        _observe(
            operation="LIST",
            outcome="ERROR",
            tenant_id=context.tenant_id,
            case_matter_id=case_matter_id,
            http_status=http_error.status_code,
            error_code=getattr(error, "code", "DEADLINE_HTTP_UNAVAILABLE"),
        )
        raise http_error from error


@router.get("/matters/{case_matter_id}/deadlines/{deadline_id}")
async def get_matter_deadline(
    case_matter_id: str,
    deadline_id: str,
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, Any]:
    """Read one deadline and re-check its matter correlation after D3A hydration."""

    def run(session: Any, database: Any) -> LegalMatterDeadline:
        return get_legal_matter_deadline(
            tenant_id=context.tenant_id,
            deadline_id=deadline_id,
            deadline_collection=_collection(database, DEADLINE_COLLECTION),
            session=session,
        )

    try:
        value = _transaction(run)
        if value.case_matter_id != case_matter_id:
            _observe(
                operation="DETAIL",
                outcome="ERROR",
                tenant_id=context.tenant_id,
                case_matter_id=case_matter_id,
                deadline_id=deadline_id,
                http_status=status.HTTP_404_NOT_FOUND,
                error_code="DEADLINE_NOT_AVAILABLE",
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LEGAL_MATTER_DEADLINE_NOT_AVAILABLE",
            )
        _observe(
            operation="DETAIL",
            outcome="SUCCESS",
            tenant_id=context.tenant_id,
            case_matter_id=case_matter_id,
            deadline_id=deadline_id,
        )
        return {"data": _project(value)}
    except HTTPException:
        raise
    except (DeadlineHttpError, LegalMatterDeadlineServiceError) as error:
        http_error = _http_error(error)
        _observe(
            operation="DETAIL",
            outcome="ERROR",
            tenant_id=context.tenant_id,
            case_matter_id=case_matter_id,
            deadline_id=deadline_id,
            http_status=http_error.status_code,
            error_code=getattr(error, "code", "DEADLINE_HTTP_UNAVAILABLE"),
        )
        raise http_error from error


__all__ = [
    "VERSION",
    "DeadlineHttpError",
    "LegalMatterDeadlineCommand",
    "_telemetry_ref",
    "create_legal_matter_deadline",
    "get_matter_deadline",
    "list_matter_deadlines",
    "router",
]

# ARTIFACT: legal_matter_deadline_router.py
# VERSION: v1.1.0-LEGAL-OPS-COMPLETION-D5-DEADLINE-OBSERVABILITY
# AUTHORITY BOUNDARY: authenticated HTTP/transaction composition plus non-authoritative bounded telemetry only; D1/D2/D3A remain canonical
# TENANT POSTURE: exact durable tenant authorization and exact tenant/matter/deadline service scope
# FAIL-CLOSED POSTURE: invalid, denied, absent, conflicting, corrupt, unavailable, and unexpected requests never fabricate success
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
