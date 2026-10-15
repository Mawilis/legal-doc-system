"""WILSY OS Tenant Legal Operating Model HTTP command plane.

TITLE: Tenant Legal Operating Model Router
VERSION: v1.0.0-CX26-R3-CURRENT-OPERATING-MODEL-HTTP
AUTHORITY: Wilsy OS Core Governance / Python EOS API
EPITOME: Expose authenticated current-configuration read and immutable revision commands at /legal/operating-model.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/tenant_legal_operating_model_router.py
COLLABORATION / OWNERSHIP: CX26-R3 service owns admission/composition; CX26-R2 registry owns persistence; this router owns HTTP validation and transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: v1.0.0-CX26-R3 adds GET and POST with exact tenant correlation, required header idempotency, bounded errors, and commit-before-response behavior.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: JWT projections never grant authority; no caller may select tenant, identity, revision ID, effective time, catalogue binding, or fingerprint.
TENANT BOUNDARY: X-Tenant-ID must exactly equal the authenticated identity tenant and all persistence predicates remain tenant-first.
AUTHORITY BOUNDARY: Transport and transaction composition only; configuration is not entitlement, assignment, permission, workflow, legal, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement.
FAIL-CLOSED DECLARATION: Missing authentication/scope/key, denied or unavailable IAM, stale state, invalid catalogue input, ambiguity, and persistence failure reject.
"""
from __future__ import annotations

from typing import Annotated, Any, Final

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, StrictInt

from tools.eos.api.tenant_authorization_http import get_role_assignment_repository
from tools.eos.auth.authentication import (
    get_current_identity,
    get_principal_authority_repository,
)
from tools.eos.auth.authorization import (
    get_role_assignment_repository as get_authorization_role_repository,
)
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.tenant_access import get_tenant_membership_repository
from tools.eos.kernel.db import get_client, get_database
from tools.eos.legal_operations.domain.tenant_legal_operating_model import (
    TenantLegalOperatingModelError,
)
from tools.eos.legal_operations.registry.tenant_legal_operating_model_registry import (
    COLLECTION_NAME,
    TenantLegalOperatingModelRegistry,
    TenantLegalOperatingModelRegistryConflictError,
    TenantLegalOperatingModelRegistryError,
    TenantLegalOperatingModelRegistryNotFoundError,
    TenantLegalOperatingModelRegistryRetryTransactionError,
)
from tools.eos.legal_operations.service.tenant_legal_operating_model_service import (
    TenantLegalOperatingModelAuthorizationDeniedError,
    TenantLegalOperatingModelAuthorityUnavailableError,
    TenantLegalOperatingModelRevisionConflictError,
    configure_tenant_legal_operating_model,
    get_current_tenant_legal_operating_model,
)

VERSION: Final[str] = "v1.0.0-CX26-R3-CURRENT-OPERATING-MODEL-HTTP"
router = APIRouter(prefix="/legal/operating-model", tags=["Tenant Legal Operating Model"])


class ConfigureTenantLegalOperatingModelRequest(BaseModel):
    """Closed client command containing only CAS expectation and catalogue IDs."""

    model_config = ConfigDict(extra="forbid", strict=True)
    expected_revision: StrictInt | None
    activated_item_ids: list[str]


def _error(status_code: int, code: str, message: str) -> HTTPException:
    """Create one bounded structured HTTP error without authority disclosure."""
    return HTTPException(status_code=status_code, detail={"error": code, "message": message})


def _tenant(identity: SovereignIdentity, selected_tenant: str | None) -> str:
    """Correlate explicit request scope with authenticated tenant projection."""
    if not isinstance(selected_tenant, str) or not selected_tenant or selected_tenant != selected_tenant.strip():
        raise _error(status.HTTP_400_BAD_REQUEST, "TENANT_SCOPE_REQUIRED", "A valid tenant scope is required.")
    if selected_tenant != identity.tenant_id:
        raise _error(status.HTTP_403_FORBIDDEN, "TENANT_SCOPE_DENIED", "Tenant authorization denied.")
    return selected_tenant


def _dependencies(database: Any) -> TenantLegalOperatingModelRegistry:
    """Bind the canonical collection without creating persistence truth."""
    if database is None:
        raise _error(status.HTTP_503_SERVICE_UNAVAILABLE, "OPERATING_MODEL_PERSISTENCE_UNAVAILABLE", "Operating-model persistence is unavailable.")
    return TenantLegalOperatingModelRegistry(database[COLLECTION_NAME])


def _translate(error: Exception) -> HTTPException:
    """Translate domain/service/registry failures into the governed HTTP set."""
    if isinstance(error, TenantLegalOperatingModelAuthorizationDeniedError):
        return _error(403, "OPERATING_MODEL_AUTHORIZATION_DENIED", "Tenant authorization denied.")
    if isinstance(error, TenantLegalOperatingModelRegistryNotFoundError):
        return _error(404, "OPERATING_MODEL_NOT_FOUND", "No current operating model exists.")
    if isinstance(error, (TenantLegalOperatingModelRevisionConflictError, TenantLegalOperatingModelRegistryConflictError, TenantLegalOperatingModelRegistryRetryTransactionError)):
        return _error(409, getattr(error, "code", "OPERATING_MODEL_CONFLICT"), "Operating-model command conflicts with current durable truth.")
    if isinstance(error, TenantLegalOperatingModelError):
        return _error(400, error.code, "Operating-model command is invalid.")
    if isinstance(error, (TenantLegalOperatingModelAuthorityUnavailableError, TenantLegalOperatingModelRegistryError)):
        return _error(503, getattr(error, "code", "OPERATING_MODEL_UNAVAILABLE"), "Operating-model authority is unavailable.")
    return _error(503, "OPERATING_MODEL_UNAVAILABLE", "Operating-model authority is unavailable.")


def _run_transaction(callback: Any) -> Any:
    """Run one callback in a caller-owned transaction and commit before return."""
    client = get_client()
    database = get_database()
    if client is None or database is None:
        raise _error(503, "OPERATING_MODEL_PERSISTENCE_UNAVAILABLE", "Operating-model persistence is unavailable.")
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
    except Exception as error:
        raise _translate(error) from error


@router.get("")
def get_current_operating_model(
    identity: Annotated[SovereignIdentity, Depends(get_current_identity)],
    tenant_id: Annotated[str | None, Header(alias="X-Tenant-ID")] = None,
    principal_repository: Any = Depends(get_principal_authority_repository),
    membership_repository: Any = Depends(get_tenant_membership_repository),
    business_role_repository: Any = Depends(get_role_assignment_repository),
    role_assignment_repository: Any = Depends(get_authorization_role_repository),
) -> dict[str, object]:
    """Return the authorized tenant's current immutable configuration revision."""
    tenant = _tenant(identity, tenant_id)
    try:
        value = _run_transaction(
            lambda session, database: get_current_tenant_legal_operating_model(
                tenant_id=tenant,
                principal_id=identity.identity_id,
                registry=_dependencies(database),
                principal_repository=principal_repository,
                membership_repository=membership_repository,
                business_role_repository=business_role_repository,
                role_assignment_repository=role_assignment_repository,
                session=session,
            )
        )
    except HTTPException:
        raise
    except Exception as error:
        raise _translate(error) from error
    return value.to_dict()


@router.post("", status_code=status.HTTP_201_CREATED)
def configure_operating_model(
    command: ConfigureTenantLegalOperatingModelRequest,
    identity: Annotated[SovereignIdentity, Depends(get_current_identity)],
    tenant_id: Annotated[str | None, Header(alias="X-Tenant-ID")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    principal_repository: Any = Depends(get_principal_authority_repository),
    membership_repository: Any = Depends(get_tenant_membership_repository),
    business_role_repository: Any = Depends(get_role_assignment_repository),
    role_assignment_repository: Any = Depends(get_authorization_role_repository),
) -> dict[str, object]:
    """Persist one server-owned immutable successor after exact transactional IAM."""
    tenant = _tenant(identity, tenant_id)
    if idempotency_key is None:
        raise _error(400, "IDEMPOTENCY_KEY_REQUIRED", "Idempotency-Key is required.")
    try:
        value = _run_transaction(
            lambda session, database: configure_tenant_legal_operating_model(
                tenant_id=tenant,
                principal_id=identity.identity_id,
                expected_revision=command.expected_revision,
                activated_item_ids=command.activated_item_ids,
                idempotency_key=idempotency_key,
                registry=_dependencies(database),
                principal_repository=principal_repository,
                membership_repository=membership_repository,
                business_role_repository=business_role_repository,
                role_assignment_repository=role_assignment_repository,
                session=session,
            )
        )
    except HTTPException:
        raise
    except Exception as error:
        raise _translate(error) from error
    return value.to_dict()


__all__ = ["VERSION", "router", "ConfigureTenantLegalOperatingModelRequest"]

# ARTIFACT: tenant_legal_operating_model_router.py
# VERSION: v1.0.0-CX26-R3-CURRENT-OPERATING-MODEL-HTTP
# AUTHORITY BOUNDARY: HTTP and transaction composition only; configuration grants no downstream authority
# TENANT POSTURE: authenticated and explicit tenant scopes must match exactly
# FAIL-CLOSED POSTURE: malformed, unauthenticated, unauthorized, stale, ambiguous, or unavailable requests reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
