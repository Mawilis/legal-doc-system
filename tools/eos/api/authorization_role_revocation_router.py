"""
WILSY OS governed ordinary authorization-role revocation HTTP router.

VERSION:
v1.0.0-P1-R3D-B1-AUTHORIZATION-ROLE-REVOCATION-ROUTER

AUTHORITY:
HTTP admission, collection binding, caller-owned transaction lifecycle,
bounded result projection, and transport error translation only.

The certified AuthorizationRoleRevocationCommand remains the sole owner of
current IAM re-authorization, replay semantics, target currentness, ordinary
revocation policy, authorization evidence, role-assignment CAS, and durable
revocation evidence.

TENANT BOUNDARY:
Actor and tenant are supplied exclusively by RequireTenantAuthorization.
Neither actor nor tenant can be asserted in the request body.

TRANSACTION BOUNDARY:
The API host opens exactly one Mongo session and transaction. The unchanged
certified command receives that exact session. Success commits; failure aborts.
The command owns neither transaction lifecycle nor transaction retry.

RETRY BOUNDARY:
No hidden automatic mutation retry exists here. A transient transaction failure
returns a bounded retry-required conflict. An uncertain commit result returns a
bounded reconciliation-required conflict. Reconciliation occurs through a fresh
authenticated request using the same idempotency key.

ROOT BOUNDARY:
ENTERPRISE_ADMIN and SOVEREIGN_ARCHITECT targets remain outside ordinary
revocation authority through the certified command policy.

FINANCIAL EXECUTION AUTHORITY:
None. Kennel EOS remains exclusive.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Callable, Final, TypeVar
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.auth.authorization_role_revocation_command import (
    AuthorizationRoleRevocationCommand,
    AuthorizationRoleRevocationCommandAuthorizationDeniedError,
    AuthorizationRoleRevocationCommandError,
    AuthorizationRoleRevocationCommandPolicyDeniedError,
    AuthorizationRoleRevocationCommandReplayConflictError,
    AuthorizationRoleRevocationCommandTargetInvalidError,
    AuthorizationRoleRevocationCommandTransactionRequiredError,
    AuthorizationRoleRevocationResult,
    OPERATION,
    PERMISSION,
)
from tools.eos.auth.authorization_role_revocation_evidence_registry import (
    COLLECTION as REVOCATION_COLLECTION,
    AuthorizationRoleRevocationEvidenceRegistry,
)
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityRepository,
)
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
)
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    COLLECTION as AUTHORIZATION_COLLECTION,
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleRepository,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository,
)
from tools.eos.kernel.db import get_client, get_database


VERSION: Final[str] = (
    "v1.0.0-P1-R3D-B1-"
    "AUTHORIZATION-ROLE-REVOCATION-ROUTER"
)

router = APIRouter(
    prefix="/tenants/role-assignments",
    tags=["Sovereign IAM"],
)

_WRITE = RequireTenantAuthorization(
    PERMISSION,
    OPERATION,
)

_T = TypeVar("_T")


class AuthorizationRoleRevocationHttpCommand(BaseModel):
    """Caller material permitted for one ordinary role revocation."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    target_principal_id: str = Field(
        min_length=1,
        max_length=256,
    )
    target_role_id: str = Field(
        min_length=1,
        max_length=128,
    )
    expected_target_assignment_revision: int = Field(
        ge=0,
    )
    reason_reference: str = Field(
        min_length=1,
        max_length=512,
    )
    idempotency_key: str = Field(
        min_length=1,
        max_length=256,
    )

    @field_validator(
        "target_principal_id",
        "target_role_id",
        "reason_reference",
        "idempotency_key",
    )
    @classmethod
    def _trimmed_nonempty(
        cls,
        value: str,
    ) -> str:
        if value != value.strip():
            raise ValueError(
                "value must be trimmed"
            )

        if not value:
            raise ValueError(
                "value must not be empty"
            )

        return value


def _collection(
    database: Any,
    name: str,
) -> Any:
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "AUTHORIZATION_ROLE_REVOCATION_"
                "PERSISTENCE_UNAVAILABLE"
            ),
        )

    try:
        return database.get_collection(name)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "AUTHORIZATION_ROLE_REVOCATION_"
                "PERSISTENCE_UNAVAILABLE"
            ),
        ) from error


def _business_role_repository(
    collection: Any,
) -> type:
    """Bind production business-role reads to one canonical collection."""

    class BusinessRoleRepository:
        @staticmethod
        def resolve(
            principal_id: str,
            tenant_id: str,
            role_id: str,
            *,
            session: Any = None,
        ) -> Any:
            value = TenantBusinessRoleRepository.resolve(
                principal_id,
                tenant_id,
                collection,
                session=session,
            )

            if value.business_role != role_id:
                raise RoleAssignmentNotFoundError(
                    "ROLE_ASSIGNMENT_NOT_FOUND"
                )

            return value

    return BusinessRoleRepository


def _principal_repository(
    collection: Any,
) -> type:
    class PrincipalRepository:
        @staticmethod
        def resolve(
            principal_id: str,
            *,
            session: Any = None,
        ) -> Any:
            return PrincipalAuthorityRepository.resolve(
                principal_id,
                collection,
                session=session,
            )

    return PrincipalRepository


def _membership_repository(
    collection: Any,
) -> type:
    class MembershipRepository:
        @staticmethod
        def resolve(
            principal_id: str,
            tenant_id: str,
            *,
            session: Any = None,
        ) -> Any:
            return TenantMembershipRepository.resolve(
                principal_id,
                tenant_id,
                collection,
                session=session,
            )

    return MembershipRepository


def _role_repository(
    collection: Any,
) -> type:
    class RoleRepository:
        @staticmethod
        def resolve(
            principal_id: str,
            tenant_id: str,
            role_id: str,
            ignored_collection: Any = None,
            *,
            session: Any = None,
        ) -> Any:
            del ignored_collection

            return RoleAssignmentRepository.resolve(
                principal_id,
                tenant_id,
                role_id,
                collection,
                session=session,
            )

        @staticmethod
        def compare_and_swap(
            value: Any,
            expected_revision: int,
            ignored_collection: Any = None,
            *,
            session: Any = None,
        ) -> Any:
            del ignored_collection

            return RoleAssignmentRepository.compare_and_swap(
                value,
                expected_revision,
                collection,
                session=session,
            )

    return RoleRepository


def _build_command(
    database: Any,
) -> AuthorizationRoleRevocationCommand:
    """Compose the unchanged certified command from production authorities."""

    principal_collection = _collection(
        database,
        "principal_authorities",
    )
    membership_collection = _collection(
        database,
        "tenant_memberships",
    )
    business_role_collection = _collection(
        database,
        "tenant_business_roles",
    )
    role_collection = _collection(
        database,
        "role_assignments",
    )

    principal_repository = _principal_repository(
        principal_collection
    )
    membership_repository = _membership_repository(
        membership_collection
    )
    business_role_repository = _business_role_repository(
        business_role_collection
    )
    role_repository = _role_repository(
        role_collection
    )

    authorization_registry = (
        TenantAuthorizationDecisionEvidenceRegistry(
            _collection(
                database,
                AUTHORIZATION_COLLECTION,
            ),
            principal_repository=principal_repository,
            membership_repository=membership_repository,
            role_assignment_repository=role_repository,
            business_role_repository=business_role_repository,
        )
    )

    revocation_registry = (
        AuthorizationRoleRevocationEvidenceRegistry(
            _collection(
                database,
                REVOCATION_COLLECTION,
            )
        )
    )

    return AuthorizationRoleRevocationCommand(
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        role_assignment_repository=role_repository,
        business_role_repository=business_role_repository,
        role_assignment_collection=role_collection,
        authorization_evidence_registry=authorization_registry,
        revocation_evidence_registry=revocation_registry,
        clock=lambda: datetime.now(
            timezone.utc
        ),
        revocation_id_factory=lambda: (
            "role-revocation-"
            + uuid.uuid4().hex
        ),
    )


def _has_error_label(
    error: BaseException,
    label: str,
) -> bool:
    method = getattr(
        error,
        "has_error_label",
        None,
    )

    if not callable(method):
        return False

    try:
        return method(label) is True
    except Exception:
        return False


def _transaction(
    callback: Callable[[Any, Any], _T],
) -> _T:
    """Run one request in one API-owned caller transaction."""

    client = get_client()
    database = get_database()

    if client is None or database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "AUTHORIZATION_ROLE_REVOCATION_"
                "PERSISTENCE_UNAVAILABLE"
            ),
        )

    try:
        with client.start_session() as session:
            session.start_transaction()

            try:
                result = callback(
                    session,
                    database,
                )

                session.commit_transaction()

                return result
            except Exception as error:
                if bool(
                    getattr(
                        session,
                        "in_transaction",
                        False,
                    )
                ):
                    session.abort_transaction()

                if _has_error_label(
                    error,
                    "TransientTransactionError",
                ):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            "AUTHORIZATION_ROLE_REVOCATION_"
                            "RETRY_REQUIRED"
                        ),
                    ) from error

                if _has_error_label(
                    error,
                    "UnknownTransactionCommitResult",
                ):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            "AUTHORIZATION_ROLE_REVOCATION_"
                            "RECONCILIATION_REQUIRED"
                        ),
                    ) from error

                raise

    except HTTPException:
        raise

    except Exception as error:
        if _has_error_label(
            error,
            "TransientTransactionError",
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "AUTHORIZATION_ROLE_REVOCATION_"
                    "RETRY_REQUIRED"
                ),
            ) from error

        if _has_error_label(
            error,
            "UnknownTransactionCommitResult",
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "AUTHORIZATION_ROLE_REVOCATION_"
                    "RECONCILIATION_REQUIRED"
                ),
            ) from error

        raise


def _http_error(
    error: BaseException,
) -> HTTPException:
    """Translate bounded command/persistence outcomes without granting authority."""

    code = getattr(
        error,
        "code",
        None,
    )

    if not isinstance(code, str):
        code = type(error).__name__

    if isinstance(
        error,
        AuthorizationRoleRevocationCommandReplayConflictError,
    ) or code == "IDEMPOTENCY_DIVERGENT_REPLAY":
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "AUTHORIZATION_ROLE_REVOCATION_"
                "REPLAY_CONFLICT"
            ),
        )

    if isinstance(
        error,
        AuthorizationRoleRevocationCommandAuthorizationDeniedError,
    ) or code in {
        "CURRENT_AUTHORIZATION_DENIED",
        "AUTHORIZATION_EVIDENCE_INVALID",
    }:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "AUTHORIZATION_ROLE_REVOCATION_"
                "AUTHORIZATION_REQUIRED"
            ),
        )

    if isinstance(
        error,
        AuthorizationRoleRevocationCommandPolicyDeniedError,
    ) or code == "REVOCATION_POLICY_DENIED":
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "AUTHORIZATION_ROLE_REVOCATION_"
                "POLICY_DENIED"
            ),
        )

    if code == "TARGET_ASSIGNMENT_UNAVAILABLE":
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "AUTHORIZATION_ROLE_REVOCATION_"
                "TARGET_NOT_AVAILABLE"
            ),
        )

    if isinstance(
        error,
        AuthorizationRoleRevocationCommandTargetInvalidError,
    ) or code in {
        "TARGET_ASSIGNMENT_NOT_CURRENT",
        "ROLE_ASSIGNMENT_CAS_RESULT_INVALID",
        "ROLE_ASSIGNMENT_REVISION_CONFLICT",
    }:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "AUTHORIZATION_ROLE_REVOCATION_"
                "TARGET_CONFLICT"
            ),
        )

    if (
        "WHOLE_TRANSACTION_RETRY_REQUIRED"
        in code
    ):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "AUTHORIZATION_ROLE_REVOCATION_"
                "RETRY_REQUIRED"
            ),
        )

    if isinstance(
        error,
        AuthorizationRoleRevocationCommandTransactionRequiredError,
    ) or (
        "TRANSACTION_REQUIRED" in code
        or "PERSISTENCE_UNAVAILABLE" in code
        or "PERSISTED_RECORD_INVALID" in code
        or code.startswith(
            "ROLE_ASSIGNMENT_"
        )
    ):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "AUTHORIZATION_ROLE_REVOCATION_"
                "UNAVAILABLE"
            ),
        )

    if isinstance(
        error,
        AuthorizationRoleRevocationCommandError,
    ):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "AUTHORIZATION_ROLE_REVOCATION_"
                "INVALID"
            ),
        )

    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=(
            "AUTHORIZATION_ROLE_REVOCATION_"
            "UNAVAILABLE"
        ),
    )


@router.post(
    "/revocations",
    status_code=status.HTTP_200_OK,
)
async def revoke_authorization_role(
    command: AuthorizationRoleRevocationHttpCommand,
    context: TenantAuthorizationContext = Depends(
        _WRITE
    ),
) -> dict[str, Any]:
    """Revoke one ordinary authorization role through the certified command."""

    def run(
        session: Any,
        database: Any,
    ) -> AuthorizationRoleRevocationResult:
        production_command = _build_command(
            database
        )

        return production_command.execute(
            actor_principal_id=(
                context.identity.identity_id
            ),
            tenant_id=context.tenant_id,
            target_principal_id=(
                command.target_principal_id
            ),
            target_role_id=command.target_role_id,
            expected_target_assignment_revision=(
                command.expected_target_assignment_revision
            ),
            reason_reference=(
                command.reason_reference
            ),
            idempotency_key=(
                command.idempotency_key
            ),
            session=session,
        )

    try:
        value = _transaction(run)
    except HTTPException:
        raise
    except Exception as error:
        raise _http_error(error) from error

    return {
        "data": asdict(value),
    }


__all__ = [
    "VERSION",
    "AuthorizationRoleRevocationHttpCommand",
    "revoke_authorization_role",
    "router",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: authorization_role_revocation_router.py
# VERSION: v1.0.0-P1-R3D-B1-AUTHORIZATION-ROLE-REVOCATION-ROUTER
# AUTHORITY BOUNDARY: HTTP admission, collection binding, API-owned transaction lifecycle, bounded result/error projection only; certified command retains IAM/revocation authority
# TENANT POSTURE: actor and tenant derive only from RequireTenantAuthorization; body cannot assert either; exact certified command re-authorizes current IAM inside the caller transaction
# FAIL-CLOSED POSTURE: missing persistence, authorization denial, root-policy denial, stale target, replay divergence, transaction conflict, and unexpected failure never produce partial success
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
