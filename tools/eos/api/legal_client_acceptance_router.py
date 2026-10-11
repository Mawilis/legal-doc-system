"""Authenticated HTTP boundary for canonical Legal Client Acceptance.

TITLE: WILSY OS Legal Client Acceptance HTTP Router
VERSION: v1.0.0-LEGAL-CLIENT-ACCEPTANCE-HTTP-PARITY
AUTHORITY: Existing Wilsy OS Legal Operations client-acceptance authorities only.
EPITOME: Projects certified server-composed acceptance-context creation and
         immutable client-acceptance issuance without creating new authority.
COLLABORATION / OWNERSHIP: HTTP owns request validation, API transaction
                            lifecycle, dependency wiring and error translation.
                            Canonical Legal Operations orchestrators own business
                            truth and persistence decisions.
TENANT BOUNDARY: Tenant and principal derive only from authenticated
                 TenantAuthorizationContext; request bodies cannot assert them.
AUTHORITY BOUNDARY: This router does not create engagement, representation,
                    Court, billing, payment, execution or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

from typing import Any, Callable, Final, Mapping, TypeVar

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from pymongo.client_session import ClientSession

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
    get_role_assignment_repository,
)
from tools.eos.auth.authentication import get_principal_authority_repository
from tools.eos.auth.tenant_access import get_tenant_membership_repository
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    COLLECTION as TENANT_AUTHORIZATION_EVIDENCE_COLLECTION,
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.legal_operations.orchestration.legal_client_acceptance_context_orchestrator import (
    LegalClientAcceptanceContextOrchestrationError,
    LegalClientAcceptanceContextOrchestrationRetryRequiredError,
    compose_legal_client_acceptance_context,
)
from tools.eos.legal_operations.orchestration.legal_client_acceptance_orchestrator import (
    LegalClientAcceptanceOrchestrationError,
    LegalClientAcceptanceOrchestrationRetryRequiredError,
    issue_legal_client_acceptance,
)
from tools.eos.legal_operations.registry.legal_client_acceptance_context_registry import (
    COLLECTION as ACCEPTANCE_CONTEXT_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_client_acceptance_registry import (
    COLLECTION as ACCEPTANCE_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_client_acting_capacity_registry import (
    COLLECTION as CAPACITY_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_client_matter_acceptance_instrument_approval_registry import (
    COLLECTION as APPROVAL_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_client_matter_acceptance_instrument_lifecycle_registry import (
    COLLECTION as INSTRUMENT_LIFECYCLE_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_client_matter_acceptance_instrument_registry import (
    COLLECTION as INSTRUMENT_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_client_matter_visibility_registry import (
    COLLECTION as VISIBILITY_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_matter_party_registry import (
    COLLECTION as PARTY_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as MATTER_LIFECYCLE_COLLECTION,
)


VERSION: Final[str] = "v1.0.0-LEGAL-CLIENT-ACCEPTANCE-HTTP-PARITY"

router = APIRouter(
    prefix="/legal-operations/client",
    tags=["Legal Client Acceptance"],
)

_WRITE = RequireTenantAuthorization(
    "legal_operations:client_acceptance:write",
    "legal_client_acceptance_write",
)

_T = TypeVar("_T")


class AcceptanceContextCommand(BaseModel):
    """Only opaque identifiers explicitly accepted by the canonical composer."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    acceptance_context_id: str = Field(min_length=1, max_length=256)
    replay_key: str = Field(min_length=1, max_length=256)
    instrument_id: str = Field(min_length=1, max_length=256)


class AcceptanceCommand(BaseModel):
    """Explicit human confirmation only; all legal truth remains server-derived."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    confirmed: bool


def _db_handles() -> tuple[Any, Any]:
    from tools.eos.kernel.db import get_client, get_database

    return get_client(), get_database()


def _collection(database: Any, name: str) -> Any:
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_CLIENT_ACCEPTANCE_PERSISTENCE_UNAVAILABLE",
        )
    try:
        return database.get_collection(name)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_CLIENT_ACCEPTANCE_PERSISTENCE_UNAVAILABLE",
        ) from error


def _transaction(callback: Callable[[Any, Any], _T]) -> _T:
    client, database = _db_handles()
    if client is None or database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_CLIENT_ACCEPTANCE_PERSISTENCE_UNAVAILABLE",
        )

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
    except HTTPException:
        raise
    except Exception:
        raise


def _error_code(error: BaseException) -> str:
    code = getattr(error, "code", None)
    if isinstance(code, str) and code.strip():
        return code
    message = str(error).strip()
    return message if message else type(error).__name__


def _http_error(error: BaseException) -> HTTPException:
    code = _error_code(error)

    if isinstance(
        error,
        (
            LegalClientAcceptanceContextOrchestrationRetryRequiredError,
            LegalClientAcceptanceOrchestrationRetryRequiredError,
        ),
    ) or "RETRY_REQUIRED" in code or "REPLAY_CONFLICT" in code:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=code,
        )

    if (
        "AUTHORIZATION_REQUIRED" in code
        or "AUTHORIZATION_DENIED" in code
        or "ACTOR_MISMATCH" in code
        or "PRINCIPAL_INACTIVE" in code
    ):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=code,
        )

    if (
        "NOT_FOUND" in code
        or "EXPIRED" in code
        or "VISIBILITY_REQUIRED" in code
    ):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=code,
        )

    if (
        "UNAVAILABLE" in code
        or "PERSISTENCE" in code
        or "ACTIVE_TRANSACTION_REQUIRED" in code
        or "CORRELATION_INVALID" in code
    ):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=code,
        )

    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=code,
    )


class _AuthorizationEvidenceIssuerAdapter:
    """Narrow structural adapter over canonical authorization-evidence issuance.

    The P2C3 orchestration protocol intentionally accepts a generic keyword seam.
    HTTP does not widen that seam: this adapter validates the exact canonical
    keyword set and types proven at the orchestrator call site, then delegates
    unchanged values to TenantAuthorizationDecisionEvidenceRegistry.
    """

    _KEYS: Final[frozenset[str]] = frozenset(
        {
            "tenant_id",
            "principal_id",
            "operation",
            "permission",
            "subject_reference",
            "subject_evidence_fingerprint",
            "idempotency_key",
            "session",
        }
    )

    def __init__(
        self,
        registry: TenantAuthorizationDecisionEvidenceRegistry,
    ) -> None:
        self._registry = registry

    @staticmethod
    def _required_text(values: Mapping[str, object], key: str) -> str:
        value = values.get(key)
        if not isinstance(value, str) or not value or value != value.strip():
            raise TypeError("LEGAL_CLIENT_ACCEPTANCE_AUTHORIZATION_ISSUER_INVALID")
        return value

    def issue(self, **kwargs: object) -> object:
        """Validate the structural seam and delegate to canonical issuance."""

        if set(kwargs) != self._KEYS:
            raise TypeError("LEGAL_CLIENT_ACCEPTANCE_AUTHORIZATION_ISSUER_INVALID")

        session = kwargs.get("session")
        if not isinstance(session, ClientSession):
            raise TypeError("LEGAL_CLIENT_ACCEPTANCE_AUTHORIZATION_ISSUER_INVALID")

        return self._registry.issue(
            tenant_id=self._required_text(kwargs, "tenant_id"),
            principal_id=self._required_text(kwargs, "principal_id"),
            operation=self._required_text(kwargs, "operation"),
            permission=self._required_text(kwargs, "permission"),
            subject_reference=self._required_text(kwargs, "subject_reference"),
            subject_evidence_fingerprint=self._required_text(
                kwargs,
                "subject_evidence_fingerprint",
            ),
            idempotency_key=self._required_text(kwargs, "idempotency_key"),
            session=session,
        )


def _authorization_registry(
    database: Any,
    *,
    principal_repository: Any,
    membership_repository: Any,
    role_assignment_repository: Any,
) -> TenantAuthorizationDecisionEvidenceRegistry:
    return TenantAuthorizationDecisionEvidenceRegistry(
        _collection(database, TENANT_AUTHORIZATION_EVIDENCE_COLLECTION),
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        role_assignment_repository=role_assignment_repository,
        business_role_repository=role_assignment_repository,
    )


@router.post(
    "/matters/{case_matter_id}/acceptance-contexts",
    status_code=status.HTTP_201_CREATED,
)
async def create_client_acceptance_context(
    case_matter_id: str,
    command: AcceptanceContextCommand,
    context: TenantAuthorizationContext = Depends(_WRITE),
    principal_repository: Any = Depends(get_principal_authority_repository),
    membership_repository: Any = Depends(get_tenant_membership_repository),
    role_assignment_repository: Any = Depends(get_role_assignment_repository),
) -> dict[str, Any]:
    """Compose one durable server-authoritative client acceptance context."""

    def run(session: Any, database: Any) -> Any:
        authorization_registry = _authorization_registry(
            database,
            principal_repository=principal_repository,
            membership_repository=membership_repository,
            role_assignment_repository=role_assignment_repository,
        )
        return compose_legal_client_acceptance_context(
            identity=context.identity,
            case_matter_id=case_matter_id,
            acceptance_context_id=command.acceptance_context_id,
            replay_key=command.replay_key,
            instrument_id=command.instrument_id,
            matter_lifecycle_collection=_collection(
                database, MATTER_LIFECYCLE_COLLECTION
            ),
            visibility_collection=_collection(database, VISIBILITY_COLLECTION),
            party_collection=_collection(database, PARTY_COLLECTION),
            capacity_collection=_collection(database, CAPACITY_COLLECTION),
            instrument_collection=_collection(database, INSTRUMENT_COLLECTION),
            instrument_lifecycle_collection=_collection(
                database, INSTRUMENT_LIFECYCLE_COLLECTION
            ),
            approval_collection=_collection(database, APPROVAL_COLLECTION),
            context_collection=_collection(
                database, ACCEPTANCE_CONTEXT_COLLECTION
            ),
            authorization_evidence_registry=_AuthorizationEvidenceIssuerAdapter(
                authorization_registry
            ),
            principal_repository=principal_repository,
            membership_repository=membership_repository,
            business_role_repository=role_assignment_repository,
            role_assignment_repository=role_assignment_repository,
            session=session,
        )

    try:
        value = _transaction(run)
    except (
        LegalClientAcceptanceContextOrchestrationError,
        LegalClientAcceptanceContextOrchestrationRetryRequiredError,
    ) as error:
        raise _http_error(error) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_CLIENT_ACCEPTANCE_CONTEXT_UNAVAILABLE",
        ) from error

    return {"data": value.to_dict()}


@router.post(
    "/acceptance-contexts/{acceptance_context_id}/acceptances",
    status_code=status.HTTP_201_CREATED,
)
async def create_client_acceptance(
    acceptance_context_id: str,
    command: AcceptanceCommand,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_WRITE),
    principal_repository: Any = Depends(get_principal_authority_repository),
    membership_repository: Any = Depends(get_tenant_membership_repository),
    role_assignment_repository: Any = Depends(get_role_assignment_repository),
) -> dict[str, Any]:
    """Issue one immutable acceptance from one current persisted context."""

    if (
        not isinstance(idempotency_key, str)
        or not idempotency_key.strip()
        or len(idempotency_key) > 256
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="LEGAL_CLIENT_ACCEPTANCE_IDEMPOTENCY_REQUIRED",
        )

    def run(session: Any, database: Any) -> Any:
        authorization_registry = _authorization_registry(
            database,
            principal_repository=principal_repository,
            membership_repository=membership_repository,
            role_assignment_repository=role_assignment_repository,
        )
        return issue_legal_client_acceptance(
            identity=context.identity,
            acceptance_context_id=acceptance_context_id,
            confirmed=command.confirmed,
            idempotency_key=idempotency_key,
            context_collection=_collection(
                database, ACCEPTANCE_CONTEXT_COLLECTION
            ),
            matter_lifecycle_collection=_collection(
                database, MATTER_LIFECYCLE_COLLECTION
            ),
            visibility_collection=_collection(database, VISIBILITY_COLLECTION),
            party_collection=_collection(database, PARTY_COLLECTION),
            capacity_collection=_collection(database, CAPACITY_COLLECTION),
            instrument_collection=_collection(database, INSTRUMENT_COLLECTION),
            instrument_lifecycle_collection=_collection(
                database, INSTRUMENT_LIFECYCLE_COLLECTION
            ),
            approval_collection=_collection(database, APPROVAL_COLLECTION),
            acceptance_collection=_collection(database, ACCEPTANCE_COLLECTION),
            authorization_evidence_registry=authorization_registry,
            principal_repository=principal_repository,
            membership_repository=membership_repository,
            business_role_repository=role_assignment_repository,
            role_assignment_repository=role_assignment_repository,
            session=session,
        )

    try:
        value = _transaction(run)
    except (
        LegalClientAcceptanceOrchestrationError,
        LegalClientAcceptanceOrchestrationRetryRequiredError,
    ) as error:
        raise _http_error(error) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_CLIENT_ACCEPTANCE_UNAVAILABLE",
        ) from error

    return {"data": value.to_dict()}


__all__ = [
    "AcceptanceCommand",
    "AcceptanceContextCommand",
    "VERSION",
    "router",
]

# ARTIFACT: legal_client_acceptance_router.py
# VERSION: v1.0.0-LEGAL-CLIENT-ACCEPTANCE-HTTP-PARITY
# AUTHORITY BOUNDARY: authenticated transport only over certified client-acceptance truth
# TENANT POSTURE: authenticated TenantAuthorizationContext only; no caller tenant authority
# FAIL-CLOSED POSTURE: malformed, unauthorized, stale, divergent and unavailable truth rejects
# FINANCIAL EXECUTION AUTHORITY: none
