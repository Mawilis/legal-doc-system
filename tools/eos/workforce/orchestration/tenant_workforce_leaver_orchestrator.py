"""WILSY OS tenant-scoped workforce leaver orchestration.

TITLE: Tenant Workforce Leaver Orchestrator
VERSION: v1.0.0-W3C-TENANT-WORKFORCE-LEAVER

EPITOME:
    Atomically close one exact TENANT workforce relationship and the tenant-
    scoped IAM/session authority derived from that engagement.

AUTHORITY BOUNDARY:
    This orchestrator may end one canonical tenant-scoped WorkforceRelationship,
    revoke that exact principal/tenant membership, revoke ACTIVE role
    assignments in that tenant, and revoke tenant-bound sessions and refresh
    tokens. It never mutates PrincipalStatus and owns no global principal,
    commercial, subscription, billing, financial-execution, professional-status,
    or cross-tenant authority.

TRANSACTION BOUNDARY:
    The caller must provide one already-active Mongo transaction. Every W3B,
    membership, role, session and refresh mutation receives that exact caller
    session. This module never starts, commits, aborts, or retries a transaction.

SECURITY POSTURE:
    TENANT leaver != global principal revocation.
    ENDED is terminal.
    Rehire requires a new WorkforceRelationship identity.
    Cross-tenant mutation is forbidden.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Final

from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentRepository,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository,
)
from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceRelationshipStatus,
    WorkforceScopeKind,
)
from tools.eos.workforce.domain.workforce_relationship_currentness import (
    derive_workforce_relationship_currentness,
)
from tools.eos.workforce.registry import workforce_relationship_registry


VERSION: Final[str] = "v1.0.0-W3C-TENANT-WORKFORCE-LEAVER"


class TenantWorkforceLeaverError(RuntimeError):
    """Base failure for bounded tenant-workforce leaver orchestration."""


class TenantWorkforceLeaverInputError(TenantWorkforceLeaverError):
    """Input or scope contract failed closed."""


class TenantWorkforceLeaverTransactionRequiredError(
    TenantWorkforceLeaverError
):
    """Caller did not provide one active transaction."""


class TenantWorkforceLeaverConflictError(TenantWorkforceLeaverError):
    """Current durable lifecycle truth conflicts with this command."""


@dataclass(frozen=True, slots=True)
class TenantWorkforceLeaverResult:
    """Exact durable outcome from one tenant-scoped leaver command."""

    relationship: WorkforceRelationship
    membership: TenantMembershipAuthority
    revoked_role_ids: tuple[str, ...]
    revoked_session_count: int
    revoked_refresh_token_count: int
    exact_replay: bool


def _text(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        raise TenantWorkforceLeaverInputError(
            f"W3C_{name.upper()}_INVALID"
        )
    return value


def _moment(value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise TenantWorkforceLeaverInputError(
            "W3C_ENDED_AT_INVALID"
        )
    return value


def _transaction(session: Any) -> Any:
    if session is None:
        raise TenantWorkforceLeaverTransactionRequiredError(
            "W3C_ACTIVE_TRANSACTION_REQUIRED"
        )

    marker = getattr(
        session,
        "in_transaction",
        None,
    )

    try:
        active = (
            marker()
            if callable(marker)
            else marker
        )
    except Exception as error:
        raise TenantWorkforceLeaverTransactionRequiredError(
            "W3C_ACTIVE_TRANSACTION_REQUIRED"
        ) from error

    if active is not True:
        raise TenantWorkforceLeaverTransactionRequiredError(
            "W3C_ACTIVE_TRANSACTION_REQUIRED"
        )

    return session


def _ended_revision(
    current: WorkforceRelationship,
    *,
    ended_at: datetime,
    reason_reference: str,
) -> WorkforceRelationship:
    """Construct only the next immutable ENDED revision."""

    if current.status is WorkforceRelationshipStatus.ENDED:
        raise TenantWorkforceLeaverConflictError(
            "W3C_RELATIONSHIP_ALREADY_ENDED"
        )

    if current.status_effective_at > ended_at:
        raise TenantWorkforceLeaverConflictError(
            "W3C_END_BEFORE_LATEST_STATUS_EFFECTIVE_AT"
        )

    return WorkforceRelationship(
        relationship_id=current.relationship_id,
        revision=current.revision + 1,
        scope_kind=current.scope_kind,
        scope_id=current.scope_id,
        principal_id=current.principal_id,
        relationship_type=current.relationship_type,
        status=WorkforceRelationshipStatus.ENDED,
        effective_from=current.effective_from,
        effective_until=ended_at,
        status_effective_at=ended_at,
        reason_reference=reason_reference,
        supersedes_fingerprint=current.fingerprint,
    )


def close_tenant_workforce_access(
    *,
    tenant_id: object,
    principal_id: object,
    relationship_id: object,
    ended_at: object,
    reason_reference: object,
    workforce_collection: Any,
    membership_collection: Any,
    role_assignment_collection: Any,
    auth_registry: Any,
    session: Any,
) -> TenantWorkforceLeaverResult:
    """Atomically close one tenant engagement and its tenant access.

    Global PrincipalStatus is intentionally outside this command.
    """

    tenant = _text(
        "tenant_id",
        tenant_id,
    )
    principal = _text(
        "principal_id",
        principal_id,
    )
    relationship_identity = _text(
        "relationship_id",
        relationship_id,
    )
    reason = _text(
        "reason_reference",
        reason_reference,
    )
    occurred = _moment(
        ended_at
    )
    tx = _transaction(
        session
    )

    history = (
        workforce_relationship_registry.list_history(
            WorkforceScopeKind.TENANT.value,
            tenant,
            relationship_identity,
            collection=workforce_collection,
            session=tx,
        )
    )

    currentness = (
        derive_workforce_relationship_currentness(
            history,
            occurred,
        )
    )

    latest = history[-1]

    if (
        latest.scope_kind
        is not WorkforceScopeKind.TENANT
        or latest.scope_id != tenant
        or latest.principal_id != principal
    ):
        raise TenantWorkforceLeaverInputError(
            "W3C_RELATIONSHIP_SCOPE_OR_PRINCIPAL_MISMATCH"
        )

    exact_replay = False

    if (
        latest.status
        is WorkforceRelationshipStatus.ENDED
    ):
        if (
            latest.status_effective_at
            != occurred
            or latest.reason_reference
            != reason
        ):
            raise TenantWorkforceLeaverConflictError(
                "W3C_DIVERGENT_ENDED_REPLAY"
            )

        ended = latest
        exact_replay = True
    else:
        if (
            currentness.relationship.relationship_id
            != latest.relationship_id
        ):
            raise TenantWorkforceLeaverConflictError(
                "W3C_CURRENTNESS_IDENTITY_MISMATCH"
            )

        ended = _ended_revision(
            latest,
            ended_at=occurred,
            reason_reference=reason,
        )

        ended = (
            workforce_relationship_registry.persist_revision(
                ended,
                collection=workforce_collection,
                session=tx,
            )
        )

    membership = TenantMembershipRepository.resolve(
        principal,
        tenant,
        membership_collection,
        session=tx,
    )

    if (
        membership.status
        is not TenantMembershipStatus.REVOKED
    ):
        membership = (
            TenantMembershipRepository.compare_and_swap(
                TenantMembershipAuthority(
                    principal_id=principal,
                    tenant_id=tenant,
                    status=TenantMembershipStatus.REVOKED,
                    revision=membership.revision + 1,
                ),
                membership.revision,
                membership_collection,
                session=tx,
            )
        )

    assignments = (
        RoleAssignmentRepository.list_assignments(
            principal,
            tenant,
            role_assignment_collection,
            session=tx,
        )
    )

    revoked_roles: list[str] = []

    for assignment in assignments:
        if (
            assignment.status
            is not RoleAssignmentStatus.ACTIVE
        ):
            continue

        revoked = (
            RoleAssignmentRepository.compare_and_swap(
                RoleAssignmentAuthority(
                    principal_id=assignment.principal_id,
                    tenant_id=assignment.tenant_id,
                    role_id=assignment.role_id,
                    status=RoleAssignmentStatus.REVOKED,
                    revision=assignment.revision + 1,
                ),
                assignment.revision,
                role_assignment_collection,
                session=tx,
            )
        )

        revoked_roles.append(
            revoked.role_id
        )

    sessions = auth_registry.revoke_sessions(
        tenant,
        principal,
        session=tx,
    )

    refresh = auth_registry.revoke_refresh_tokens(
        tenant,
        principal,
        session=tx,
    )

    if (
        type(sessions) is not int
        or sessions < 0
        or type(refresh) is not int
        or refresh < 0
    ):
        raise TenantWorkforceLeaverConflictError(
            "W3C_AUTH_REVOCATION_RESULT_INVALID"
        )

    return TenantWorkforceLeaverResult(
        relationship=ended,
        membership=membership,
        revoked_role_ids=tuple(
            revoked_roles
        ),
        revoked_session_count=sessions,
        revoked_refresh_token_count=refresh,
        exact_replay=exact_replay,
    )


__all__ = [
    "VERSION",
    "TenantWorkforceLeaverConflictError",
    "TenantWorkforceLeaverError",
    "TenantWorkforceLeaverInputError",
    "TenantWorkforceLeaverResult",
    "TenantWorkforceLeaverTransactionRequiredError",
    "close_tenant_workforce_access",
]

# ARTIFACT: tenant_workforce_leaver_orchestrator.py
# VERSION: v1.0.0-W3C-TENANT-WORKFORCE-LEAVER
# AUTHORITY BOUNDARY: exact tenant-workforce/IAM/session closure only
# GLOBAL PRINCIPAL MUTATION: forbidden
# FINANCIAL EXECUTION AUTHORITY: none
