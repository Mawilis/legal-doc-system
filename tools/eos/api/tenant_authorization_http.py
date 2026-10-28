"""Canonical tenant authorization HTTP composition and denial observation.

TITLE: WILSY OS Tenant Authorization HTTP Boundary
VERSION: v1.3.0-P6-DIRECT-BUSINESS-ROLE-RESOLUTION
AUTHORITY: FastAPI dependency translation of frozen durable tenant authorization.
EPITOME: Binds an authenticated identity and explicit tenant scope to current
         IAM truth, then emits one bounded terminal observation for admitted
         authorization denial or dependency unavailability without becoming
         an authorization authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/tenant_authorization_http.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering / Python EOS IAM.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-28 v1.3.0-P6-DIRECT-BUSINESS-ROLE-RESOLUTION exposes one exact-scope,
    single-read business-role lookup for the canonical resolver while preserving
    separate authorization-role reads and existing denial/outage classification.
    2026-10-19 v1.2.0-P6-IAM-DENIAL-OBSERVABILITY adds one failure-safe,
    bounded, post-decision structured observation for authenticated tenant IAM
    denials and dependency unavailability. Server-generated correlation and
    SHA3-512 pseudonyms exclude raw identity, credential, policy, request, and
    legal evidence; existing authentication, authorization, HTTP, tenant, and
    persistence authority remain unchanged.
    v1.1.0 routes governed tenant business-role identifiers to dedicated
    tenant_business_roles truth while preserving authorization-role resolution
    in role_assignments.
    v1.0.0 established the fail-closed tenant authorization HTTP dependency.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Transport projections never grant authority;
                            malformed scope denies. SHA3-512 references are
                            pseudonymous and linkable, not anonymous.
TENANT BOUNDARY: X-Tenant-ID is explicit request scope and never membership evidence.
AUTHORITY BOUNDARY: Composes frozen durable authorization only; observations
                    classify existing results and never decide access.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass
from typing import Any, Final

from fastapi import Depends, Header, Request, status

from tools.eos.api.exceptions import ForbiddenOperationException, WilsyAPIException
from tools.eos.auth.authentication import (
    get_current_identity,
    get_principal_authority_repository,
)
from tools.eos.auth.authorization import (
    get_role_assignment_repository as _get_role_assignment_repository,
)
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepositoryError,
)
from tools.eos.auth.tenant_access import get_tenant_membership_repository
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.kernel.db import get_client, get_database
from tools.eos.workforce.registry.workforce_relationship_registry import (
    COLLECTION_NAME as WORKFORCE_RELATIONSHIP_COLLECTION,
)


VERSION: Final[str] = "v1.3.0-P6-DIRECT-BUSINESS-ROLE-RESOLUTION"
logger = logging.getLogger("WilsyOS.API.TenantAuthorization")
_OBSERVATION_SCHEMA: Final[str] = "WILSY-TENANT-AUTHORIZATION-OBSERVATION/V1"
_OBSERVATION_VERSION: Final[str] = "v1.0.0-P6-IAM-DENIAL-OBSERVABILITY"

_UNAVAILABLE: Final[frozenset[TenantAuthorizationReason]] = frozenset(
    {
        TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE,
        TenantAuthorizationReason.MEMBERSHIP_AUTHORITY_UNAVAILABLE,
        TenantAuthorizationReason.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE,
        TenantAuthorizationReason.ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE,
        TenantAuthorizationReason.WORKFORCE_AUTHORITY_UNAVAILABLE,
    }
)
_DENIED: Final[frozenset[TenantAuthorizationReason]] = frozenset(
    {
        TenantAuthorizationReason.INVALID_INPUT,
        TenantAuthorizationReason.PRINCIPAL_NOT_FOUND,
        TenantAuthorizationReason.PRINCIPAL_INACTIVE,
        TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND,
        TenantAuthorizationReason.MEMBERSHIP_INACTIVE,
        TenantAuthorizationReason.NO_ACTIVE_TENANT_BUSINESS_ROLE,
        TenantAuthorizationReason.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES,
        TenantAuthorizationReason.PERMISSION_UNKNOWN,
        TenantAuthorizationReason.PERMISSION_NOT_CANONICAL,
        TenantAuthorizationReason.PERMISSION_NAMESPACE_MISMATCH,
        TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH,
        TenantAuthorizationReason.PERMISSION_NOT_GRANTED,
        TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE,
        TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE,
        TenantAuthorizationReason.SYSTEM_AUTHORITY_REQUIRED,
        TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED,
        TenantAuthorizationReason.WORKFORCE_NOT_CURRENT,
    }
)
_PRINCIPAL_REASONS: Final[frozenset[TenantAuthorizationReason]] = frozenset(
    {
        TenantAuthorizationReason.PRINCIPAL_NOT_FOUND,
        TenantAuthorizationReason.PRINCIPAL_INACTIVE,
        TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE,
    }
)
_MEMBERSHIP_REASONS: Final[frozenset[TenantAuthorizationReason]] = frozenset(
    {
        TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND,
        TenantAuthorizationReason.MEMBERSHIP_INACTIVE,
        TenantAuthorizationReason.MEMBERSHIP_AUTHORITY_UNAVAILABLE,
    }
)
_BUSINESS_ROLE_REASONS: Final[frozenset[TenantAuthorizationReason]] = frozenset(
    {
        TenantAuthorizationReason.NO_ACTIVE_TENANT_BUSINESS_ROLE,
        TenantAuthorizationReason.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES,
        TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE,
        TenantAuthorizationReason.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE,
    }
)
_ROLE_ASSIGNMENT_REASONS: Final[frozenset[TenantAuthorizationReason]] = frozenset(
    {
        TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE,
        TenantAuthorizationReason.ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE,
    }
)
_PERMISSION_REASONS: Final[frozenset[TenantAuthorizationReason]] = frozenset(
    {
        TenantAuthorizationReason.PERMISSION_UNKNOWN,
        TenantAuthorizationReason.PERMISSION_NOT_CANONICAL,
        TenantAuthorizationReason.PERMISSION_NAMESPACE_MISMATCH,
        TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH,
        TenantAuthorizationReason.PERMISSION_NOT_GRANTED,
    }
)
_WORKFORCE_REASONS: Final[frozenset[TenantAuthorizationReason]] = frozenset(
    {
        TenantAuthorizationReason.WORKFORCE_NOT_CURRENT,
        TenantAuthorizationReason.WORKFORCE_AUTHORITY_UNAVAILABLE,
    }
)


@dataclass(frozen=True, slots=True)
class TenantAuthorizationContext:
    """Authenticated exact-tenant context containing the canonical decision."""

    identity: SovereignIdentity
    tenant_id: str
    decision: TenantAuthorizationDecision


def _new_correlation_id() -> str:
    """Create one server-owned identifier for an admitted IAM evaluation."""

    return f"tenant-authorization-{uuid.uuid4().hex}"


def _observation_ref(value: str) -> str:
    """Return a linkable SHA3-512 pseudonym, never an anonymity claim."""

    return hashlib.sha3_512(value.encode("utf-8")).hexdigest()


def _decision_class(reason: TenantAuthorizationReason | None) -> str:
    """Collapse internal IAM reasons into a closed operational class."""

    if reason is None:
        return "CONSISTENCY"
    if reason in _PRINCIPAL_REASONS:
        return "PRINCIPAL"
    if reason in _MEMBERSHIP_REASONS:
        return "MEMBERSHIP"
    if reason in _BUSINESS_ROLE_REASONS:
        return "BUSINESS_ROLE"
    if reason in _ROLE_ASSIGNMENT_REASONS:
        return "ROLE_ASSIGNMENT"
    if reason in _PERMISSION_REASONS:
        return "PERMISSION"
    if reason in _WORKFORCE_REASONS:
        return "WORKFORCE"
    if reason is TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED:
        return "FINANCIAL_BOUNDARY"
    if reason is TenantAuthorizationReason.SYSTEM_AUTHORITY_REQUIRED:
        return "SYSTEM_BOUNDARY"
    if reason is TenantAuthorizationReason.INVALID_INPUT:
        return "INPUT"
    return "CONSISTENCY"


def _observe_terminal(
    *,
    outcome: str,
    reason: TenantAuthorizationReason | None,
    tenant_id: str,
    principal_id: str,
    correlation_id: str,
    http_status: int,
) -> None:
    """Emit one bounded terminal observation without affecting the verdict.

    Raw identifiers, tokens, request headers, permission names, operation names,
    internal policy details, exception text, and legal evidence are excluded.
    The event observes an already-produced IAM result and has no grant, deny,
    persistence, workflow, legal-decision, or financial authority.
    """

    try:
        payload: dict[str, object] = {
            "schema": _OBSERVATION_SCHEMA,
            "version": _OBSERVATION_VERSION,
            "event": "TENANT_AUTHORIZATION_HTTP_TERMINAL",
            "outcome": outcome,
            "decision_class": _decision_class(reason),
            "tenant_ref": _observation_ref(tenant_id),
            "principal_ref": _observation_ref(principal_id),
            "correlation_ref": _observation_ref(correlation_id),
            "http_status": http_status,
        }
        logger.log(
            logging.WARNING if outcome == "AUTHORIZATION_DENIED" else logging.ERROR,
            "TENANT_AUTHORIZATION_HTTP_TERMINAL",
            extra={"wilsy_authorization_observation": payload},
        )
    except Exception:
        return


class _TenantAuthorityRoleReader:
    """Resolve each role namespace from its canonical durable store."""

    def __init__(
        self,
        *,
        authorization_repository: Any,
        business_repository: Any,
    ) -> None:
        self._authorization_repository = authorization_repository
        self._business_repository = business_repository

    def resolve_current_business_role(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> object:
        """Resolve the single canonical business-role row without role fan-out."""

        try:
            return (
                self._business_repository.resolve(principal_id, tenant_id)
                if session is None
                else self._business_repository.resolve(
                    principal_id, tenant_id, session=session
                )
            )
        except TenantBusinessRoleNotFoundError as exc:
            raise RoleAssignmentNotFoundError(
                "TENANT_BUSINESS_ROLE_NOT_FOUND"
            ) from exc
        except TenantBusinessRoleRepositoryError as exc:
            raise RoleAssignmentRepositoryError(
                "TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE"
            ) from exc

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> object:
        """Read one current role from its existing namespace authority."""

        if role_id in TENANT_ROLES:
            try:
                value = (
                    self._business_repository.resolve(principal_id, tenant_id)
                    if session is None
                    else self._business_repository.resolve(
                        principal_id, tenant_id, session=session
                    )
                )
            except TenantBusinessRoleNotFoundError as exc:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                ) from exc
            except TenantBusinessRoleRepositoryError as exc:
                raise RoleAssignmentRepositoryError(
                    "TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE"
                ) from exc
            if getattr(value, "business_role", None) != role_id:
                raise RoleAssignmentNotFoundError("TENANT_BUSINESS_ROLE_NOT_FOUND")
            return value

        return (
            self._authorization_repository.resolve(principal_id, tenant_id, role_id)
            if session is None
            else self._authorization_repository.resolve(
                principal_id, tenant_id, role_id, session=session
            )
        )


def get_role_assignment_repository() -> _TenantAuthorityRoleReader:
    """Compose separate existing business-role and authorization-role stores."""

    return _TenantAuthorityRoleReader(
        authorization_repository=_get_role_assignment_repository(),
        business_repository=TenantBusinessRoleRepository(),
    )


class RequireTenantAuthorization:
    """Require one canonical permission-operation pair for one exact tenant.

    Authentication remains owned by ``get_current_identity``. This dependency
    passes the authenticated principal and explicit tenant scope to the existing
    ``authorize_tenant_operation`` composer. It observes terminal denials and
    outages only after that canonical boundary has classified the result.
    """

    def __init__(self, permission_id: str, operation: str) -> None:
        """Freeze the canonical permission and operation without granting them."""

        if not all(
            isinstance(value, str) and value and value == value.strip()
            for value in (permission_id, operation)
        ):
            raise ValueError(
                "permission_id and operation must be non-empty trimmed strings"
            )
        self.permission_id = permission_id
        self.operation = operation

    async def __call__(
        self,
        request: Request,
        identity: SovereignIdentity = Depends(get_current_identity),
        tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
        principal_repository: Any = Depends(get_principal_authority_repository),
        membership_repository: Any = Depends(get_tenant_membership_repository),
        role_assignment_repository: Any = Depends(get_role_assignment_repository),
    ) -> TenantAuthorizationContext:
        """Return existing authorized context or preserve bounded 403/503 truth."""

        del request
        correlation_id = _new_correlation_id()
        observed_tenant = (
            tenant_id
            if isinstance(tenant_id, str) and tenant_id
            else "UNRESOLVED_TENANT_SCOPE"
        )
        if (
            not isinstance(tenant_id, str)
            or not tenant_id
            or tenant_id != tenant_id.strip()
        ):
            _observe_terminal(
                outcome="AUTHORIZATION_DENIED",
                reason=TenantAuthorizationReason.INVALID_INPUT,
                tenant_id=observed_tenant,
                principal_id=identity.identity_id,
                correlation_id=correlation_id,
                http_status=status.HTTP_403_FORBIDDEN,
            )
            raise ForbiddenOperationException("Tenant scope is required.")

        workforce_required = False
        try:
            workforce_required = (
                permission_metadata(self.permission_id).workforce_currentness_required
                is True
            )
        except ValueError:
            workforce_required = False

        try:
            if workforce_required:
                client = get_client()
                database = get_database()
                if client is None or database is None:
                    _observe_terminal(
                        outcome="DEPENDENCY_UNAVAILABLE",
                        reason=TenantAuthorizationReason.WORKFORCE_AUTHORITY_UNAVAILABLE,
                        tenant_id=tenant_id,
                        principal_id=identity.identity_id,
                        correlation_id=correlation_id,
                        http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
                    )
                    raise WilsyAPIException(
                        "Authorization authority unavailable.",
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    )
                workforce_collection = database[WORKFORCE_RELATIONSHIP_COLLECTION]
                with client.start_session() as session:
                    with session.start_transaction():
                        decision = authorize_tenant_operation(
                            principal_id=identity.identity_id,
                            tenant_id=tenant_id,
                            permission_id=self.permission_id,
                            operation=self.operation,
                            principal_repository=principal_repository,
                            membership_repository=membership_repository,
                            business_role_repository=role_assignment_repository,
                            role_assignment_repository=role_assignment_repository,
                            session=session,
                            workforce_relationship_collection=workforce_collection,
                        )
            else:
                decision = authorize_tenant_operation(
                    principal_id=identity.identity_id,
                    tenant_id=tenant_id,
                    permission_id=self.permission_id,
                    operation=self.operation,
                    principal_repository=principal_repository,
                    membership_repository=membership_repository,
                    business_role_repository=role_assignment_repository,
                    role_assignment_repository=role_assignment_repository,
                )
        except (ForbiddenOperationException, WilsyAPIException):
            raise
        except Exception as error:
            _observe_terminal(
                outcome="DEPENDENCY_UNAVAILABLE",
                reason=(
                    TenantAuthorizationReason.WORKFORCE_AUTHORITY_UNAVAILABLE
                    if workforce_required
                    else None
                ),
                tenant_id=tenant_id,
                principal_id=identity.identity_id,
                correlation_id=correlation_id,
                http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
            raise WilsyAPIException(
                "Authorization authority unavailable.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            ) from error

        if (
            decision.authorized is True
            and decision.reason is TenantAuthorizationReason.AUTHORIZED
        ):
            return TenantAuthorizationContext(identity, tenant_id, decision)
        if decision.authorized is True or decision.reason is TenantAuthorizationReason.AUTHORIZED:
            _observe_terminal(
                outcome="DEPENDENCY_UNAVAILABLE",
                reason=None,
                tenant_id=tenant_id,
                principal_id=identity.identity_id,
                correlation_id=correlation_id,
                http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
            raise WilsyAPIException(
                "Authorization decision unavailable.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        if decision.reason in _UNAVAILABLE:
            _observe_terminal(
                outcome="DEPENDENCY_UNAVAILABLE",
                reason=decision.reason,
                tenant_id=tenant_id,
                principal_id=identity.identity_id,
                correlation_id=correlation_id,
                http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
            raise WilsyAPIException(
                "Authorization authority unavailable.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        if decision.reason in _DENIED:
            _observe_terminal(
                outcome="AUTHORIZATION_DENIED",
                reason=decision.reason,
                tenant_id=tenant_id,
                principal_id=identity.identity_id,
                correlation_id=correlation_id,
                http_status=status.HTTP_403_FORBIDDEN,
            )
            raise ForbiddenOperationException("Tenant authorization denied.")
        _observe_terminal(
            outcome="DEPENDENCY_UNAVAILABLE",
            reason=None,
            tenant_id=tenant_id,
            principal_id=identity.identity_id,
            correlation_id=correlation_id,
            http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        raise WilsyAPIException(
            "Authorization decision unavailable.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


__all__ = ["VERSION", "TenantAuthorizationContext", "RequireTenantAuthorization"]


# ARTIFACT: tenant_authorization_http.py
# VERSION: v1.2.0-P6-IAM-DENIAL-OBSERVABILITY
# AUTHORITY BOUNDARY: existing HTTP IAM composition plus bounded post-decision observation only; no authentication, grant, deny, persistence, workflow, legal-decision, AI, notification, payment, execution, or settlement truth ownership
# TENANT POSTURE: explicit X-Tenant-ID remains scope only; current durable membership and role evidence remain mandatory
# FAIL-CLOSED POSTURE: only canonical AUTHORIZED succeeds; denied, unavailable, inconsistent, and unknown results remain bounded and telemetry failure cannot alter them
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
