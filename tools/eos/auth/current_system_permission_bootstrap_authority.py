"""
TITLE:
    WILSY OS Current System Permission Bootstrap Authority Resolver

VERSION:
    v1.0.0-P4-R4-D11-R4-CURRENT-BOOTSTRAP-AUTHORITY

AUTHORITY:
    Wilsy OS Sovereign IAM

PURPOSE:
    Resolve current possession of one exact bootstrap authority purpose by
    conjunctively requiring one current ACTIVE principal and one current ACTIVE
    bootstrap authority bound to that exact principal and exact purpose.

FORMULA:
    CURRENT BOOTSTRAP AUTHORITY =
        CURRENT ACTIVE PRINCIPAL
        AND CURRENT ACTIVE EXACT BOOTSTRAP PURPOSE

AUTHORITY BOUNDARY:
    Read-only currentness composition. Creates no bootstrap authority, SYSTEM
    permission grant, command authority, privileged activation, break-glass
    authority, or financial authority. Owns no transaction lifecycle and reads
    no clock.
"""

from __future__ import annotations

from typing import Any, Final

from pymongo.client_session import ClientSession

from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)

from tools.eos.auth.principal_status import (
    PrincipalStatus,
)

from tools.eos.auth.system_permission_bootstrap_authority import (
    SystemPermissionBootstrapAuthority,
)

from tools.eos.auth.system_permission_bootstrap_authority_registry import (
    SystemPermissionBootstrapAuthorityRegistry,
    SystemPermissionBootstrapAuthorityRegistryError,
)


VERSION: Final = (
    "v1.0.0-P4-R4-D11-R4-"
    "CURRENT-BOOTSTRAP-AUTHORITY"
)


class CurrentSystemPermissionBootstrapAuthorityError(
    RuntimeError
):
    """Fail-closed currentness composition failure."""

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
        raise CurrentSystemPermissionBootstrapAuthorityError(
            name + "_INVALID"
        )

    return value


class CurrentSystemPermissionBootstrapAuthorityResolver:
    """Read-only conjunction of current principal and bootstrap-purpose truth."""

    def __init__(
        self,
        *,
        principal_collection: Any,
        bootstrap_registry:
            SystemPermissionBootstrapAuthorityRegistry,
    ) -> None:
        if principal_collection is None:
            raise CurrentSystemPermissionBootstrapAuthorityError(
                "PRINCIPAL_COLLECTION_REQUIRED"
            )

        if (
            type(bootstrap_registry)
            is not SystemPermissionBootstrapAuthorityRegistry
        ):
            raise CurrentSystemPermissionBootstrapAuthorityError(
                "BOOTSTRAP_REGISTRY_REQUIRED"
            )

        self._principal_collection = (
            principal_collection
        )

        self._bootstrap_registry = (
            bootstrap_registry
        )

    def resolve(
        self,
        *,
        principal_id: str,
        purpose: str,
        session: ClientSession | None = None,
    ) -> SystemPermissionBootstrapAuthority | None:
        principal = _identifier(
            "PRINCIPAL_ID",
            principal_id,
        )

        exact_purpose = _identifier(
            "BOOTSTRAP_PURPOSE",
            purpose,
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
            raise CurrentSystemPermissionBootstrapAuthorityError(
                "PRINCIPAL_CURRENTNESS_UNAVAILABLE"
            ) from error

        if authority.principal_id != principal:
            raise CurrentSystemPermissionBootstrapAuthorityError(
                "PRINCIPAL_BINDING_INVALID"
            )

        if (
            authority.status
            is not PrincipalStatus.ACTIVE
        ):
            return None

        try:
            bootstrap = (
                self._bootstrap_registry
                .resolve_current(
                    actor_principal_id=principal,
                    purpose=exact_purpose,
                    session=session,
                )
            )

        except SystemPermissionBootstrapAuthorityRegistryError as error:
            raise CurrentSystemPermissionBootstrapAuthorityError(
                "BOOTSTRAP_CURRENTNESS_UNAVAILABLE"
            ) from error

        if bootstrap is None:
            return None

        if (
            bootstrap.actor_principal_id
            != principal
            or bootstrap.purpose
            != exact_purpose
        ):
            raise CurrentSystemPermissionBootstrapAuthorityError(
                "BOOTSTRAP_BINDING_INVALID"
            )

        return bootstrap

    def possesses(
        self,
        *,
        principal_id: str,
        purpose: str,
        session: ClientSession | None = None,
    ) -> bool:
        return (
            self.resolve(
                principal_id=principal_id,
                purpose=purpose,
                session=session,
            )
            is not None
        )


__all__ = [
    "VERSION",
    "CurrentSystemPermissionBootstrapAuthorityError",
    "CurrentSystemPermissionBootstrapAuthorityResolver",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: tools/eos/auth/current_system_permission_bootstrap_authority.py
# VERSION: v1.0.0-P4-R4-D11-R4-CURRENT-BOOTSTRAP-AUTHORITY
# FORMULA: CURRENT ACTIVE PRINCIPAL + CURRENT ACTIVE EXACT BOOTSTRAP PURPOSE
# PRINCIPAL SOURCE: PrincipalAuthorityRepository.get
# PRINCIPAL COLLECTION: CALLER-INJECTED
# SAME CALLER SESSION: PRESERVED ACROSS BOTH READS
# TRANSACTION OWNERSHIP: CALLER
# WRITES: NONE
# CLOCK: NONE
# TENANT AUTHORITY: NONE
# ROLE AUTHORITY: NONE
# FOUNDER AUTHORITY: NONE
# P2 AUTHORITY: NONE
# P3 AUTHORITY: NONE
# P4 ACTIVATION AUTHORITY: NONE
# BREAK-GLASS AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
