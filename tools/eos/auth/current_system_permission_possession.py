"""
TITLE:
    WILSY OS Current System Permission Possession Resolver

VERSION:
    v1.0.0-P4-R4-D9-CURRENT-SYSTEM-PERMISSION-POSSESSION

AUTHORITY:
    Wilsy OS Sovereign IAM

EPITOME:
    Resolve current possession of one exact canonical SYSTEM permission by
    conjunctively requiring one current ACTIVE principal and one current ACTIVE
    exact SYSTEM permission assignment inside the same caller-owned session.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/current_system_permission_possession.py

CERTIFICATION / UPDATE DATE:
    2026-10-14

CHANGELOG:
    v1.0.0-P4-R4-D9-CURRENT-SYSTEM-PERMISSION-POSSESSION
        Introduces read-only current SYSTEM permission possession composition.
        Principal currentness comes only from PrincipalAuthorityRepository and
        assignment currentness only from SystemPermissionAssignmentRegistry.
        The same caller-owned ClientSession, when supplied, is propagated
        unchanged to both reads.

AUTHORITY BOUNDARY:
    Proves only current possession of one exact SYSTEM permission. Creates no
    permission grant, tenant authority, role authority, privileged eligibility,
    security assurance, privileged activation, P4 issuance authorization,
    break-glass authority, or financial authority.

FINANCIAL AUTHORITY BOUNDARY:
    NONE.
"""

from __future__ import annotations

from typing import Any, Final

from pymongo.client_session import ClientSession

from tools.eos.auth.permission_namespace import (
    PermissionDisposition,
    permission_metadata,
)
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_status import (
    PrincipalStatus,
)
from tools.eos.auth.system_permission_assignment import (
    SystemPermissionAssignment,
)
from tools.eos.auth.system_permission_assignment_registry import (
    SystemPermissionAssignmentRegistry,
    SystemPermissionAssignmentRegistryError,
)


VERSION: Final = (
    "v1.0.0-P4-R4-D9-"
    "CURRENT-SYSTEM-PERMISSION-POSSESSION"
)


class CurrentSystemPermissionPossessionError(
    RuntimeError
):
    """Structured failure for malformed or unavailable currentness composition."""

    def __init__(
        self,
        code: str,
    ) -> None:
        super().__init__(code)
        self.code = code


def _identifier(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "*" in value
    ):
        raise CurrentSystemPermissionPossessionError(
            name + "_INVALID"
        )

    return value


def _system_permission(
    value: object,
) -> str:
    permission_id = _identifier(
        "PERMISSION_ID",
        value,
    )

    try:
        metadata = permission_metadata(
            permission_id
        )

    except (
        TypeError,
        ValueError,
    ) as error:
        raise CurrentSystemPermissionPossessionError(
            "SYSTEM_PERMISSION_INVALID"
        ) from error

    if (
        metadata.permission_id != permission_id
        or metadata.scope_kind != "SYSTEM"
        or metadata.system_assignment_required
        is not True
        or metadata.tenant_membership_required
        is not False
        or metadata.authorizes_by_itself
        is not False
        or metadata.disposition
        is not PermissionDisposition.CANONICAL
    ):
        raise CurrentSystemPermissionPossessionError(
            "SYSTEM_PERMISSION_REQUIRED"
        )

    return permission_id


class CurrentSystemPermissionPossessionResolver:
    """Read-only conjunction of current principal and current SYSTEM assignment."""

    def __init__(
        self,
        *,
        principal_collection: Any,
        assignment_registry:
            SystemPermissionAssignmentRegistry,
    ) -> None:
        if principal_collection is None:
            raise CurrentSystemPermissionPossessionError(
                "PRINCIPAL_COLLECTION_REQUIRED"
            )

        if (
            type(assignment_registry)
            is not SystemPermissionAssignmentRegistry
        ):
            raise CurrentSystemPermissionPossessionError(
                "ASSIGNMENT_REGISTRY_REQUIRED"
            )

        self._principal_collection = (
            principal_collection
        )

        self._assignment_registry = (
            assignment_registry
        )

    def resolve(
        self,
        *,
        principal_id: str,
        permission_id: str,
        session: ClientSession | None = None,
    ) -> SystemPermissionAssignment | None:
        """Return assignment evidence only when both current truths hold."""

        principal = _identifier(
            "PRINCIPAL_ID",
            principal_id,
        )

        permission = _system_permission(
            permission_id
        )

        try:
            authority = (
                PrincipalAuthorityRepository
                .get(
                    principal,
                    collection=
                        self._principal_collection,
                    session=session,
                )
            )

        except PrincipalAuthorityNotFoundError:
            return None

        except PrincipalAuthorityRepositoryError as error:
            raise CurrentSystemPermissionPossessionError(
                "PRINCIPAL_CURRENTNESS_UNAVAILABLE"
            ) from error

        if authority.principal_id != principal:
            raise CurrentSystemPermissionPossessionError(
                "PRINCIPAL_BINDING_INVALID"
            )

        if (
            authority.status
            is not PrincipalStatus.ACTIVE
        ):
            return None

        try:
            assignment = (
                self._assignment_registry
                .resolve_current(
                    principal_id=principal,
                    permission_id=permission,
                    session=session,
                )
            )

        except SystemPermissionAssignmentRegistryError as error:
            raise CurrentSystemPermissionPossessionError(
                "SYSTEM_ASSIGNMENT_CURRENTNESS_UNAVAILABLE"
            ) from error

        if assignment is None:
            return None

        if (
            assignment.principal_id
            != principal
            or assignment.permission_id
            != permission
        ):
            raise CurrentSystemPermissionPossessionError(
                "SYSTEM_ASSIGNMENT_BINDING_INVALID"
            )

        return assignment

    def possesses(
        self,
        *,
        principal_id: str,
        permission_id: str,
        session: ClientSession | None = None,
    ) -> bool:
        """Return True only for the exact current principal+assignment conjunction."""

        return (
            self.resolve(
                principal_id=principal_id,
                permission_id=permission_id,
                session=session,
            )
            is not None
        )


__all__ = [
    "VERSION",
    "CurrentSystemPermissionPossessionError",
    "CurrentSystemPermissionPossessionResolver",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: tools/eos/auth/current_system_permission_possession.py
# VERSION: v1.0.0-P4-R4-D9-CURRENT-SYSTEM-PERMISSION-POSSESSION
# FORMULA: CURRENT PRINCIPAL + CURRENT ACTIVE EXACT SYSTEM PERMISSION ASSIGNMENT
# SESSION TYPE: ClientSession | None
# SAME CALLER SESSION: PRESERVED ACROSS BOTH READS
# TRANSACTION OWNERSHIP: CALLER
# WRITES: NONE
# TENANT AUTHORITY: NONE
# ROLE AUTHORITY: NONE
# PRIVILEGED ELIGIBILITY AUTHORITY: NONE
# SECURITY ASSURANCE AUTHORITY: NONE
# PRIVILEGED ACTIVATION AUTHORITY: NONE
# FINAL P4 ISSUANCE AUTHORIZATION: NONE
# BREAK-GLASS AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
