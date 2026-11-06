"""Concrete EOS SYSTEM Services authorization adapter.

This adapter composes canonical SYSTEM permission possession with current
platform-workforce relationship evidence. It grants nothing, creates no role,
and never derives platform authority from tenant membership or browser claims.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Callable, Protocol, cast

from pymongo.client_session import ClientSession

from pymongo.client_session import ClientSession

from tools.eos.auth.current_system_permission_possession import (
    CurrentSystemPermissionPossessionError,
)
from tools.eos.auth.permission_namespace import (
    PermissionDisposition,
    permission_metadata,
)
from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceScopeKind,
)
from tools.eos.workforce.domain.workforce_relationship_currentness import (
    WorkforceRelationshipCurrentnessError,
    derive_workforce_relationship_currentness,
)
from tools.eos.workforce.registry.workforce_relationship_registry import (
    WorkforceRelationshipRegistryError,
    list_principal_relationships,
)

VERSION = "v1.0.0-SYSTEM-SERVICES-EOS-IAM-AUTHORIZER"
PLATFORM_SCOPE_KIND = WorkforceScopeKind.PLATFORM.value


class SystemServicesAuthorizationError(PermissionError):
    """A well-formed request lacks one required current authority fact."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class SystemServicesAuthorizationUnavailable(RuntimeError):
    """Canonical authority evidence could not be safely resolved."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class PermissionPossessionResolver(Protocol):
    def resolve(
        self, *, principal_id: str, permission_id: str, session: ClientSession | None = None
    ) -> object | None: ...


class SystemServicesEosAuthorizer:
    """Require ACTIVE principal, exact current SYSTEM assignment and active platform workforce."""

    def __init__(
        self,
        *,
        possession_resolver: PermissionPossessionResolver,
        workforce_collection: Any,
        platform_scope_id: str,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not callable(getattr(possession_resolver, "resolve", None)):
            raise SystemServicesAuthorizationUnavailable("POSSESSION_RESOLVER_REQUIRED")
        if workforce_collection is None:
            raise SystemServicesAuthorizationUnavailable("WORKFORCE_COLLECTION_REQUIRED")
        if (
            not isinstance(platform_scope_id, str)
            or not platform_scope_id
            or platform_scope_id != platform_scope_id.strip()
            or "*" in platform_scope_id
        ):
            raise SystemServicesAuthorizationUnavailable("PLATFORM_SCOPE_ID_REQUIRED")
        self._possession = possession_resolver
        self._workforce = workforce_collection
        # Supplied by trusted EOS composition, never by an HTTP request.
        self._platform_scope_id = platform_scope_id
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def require(
        self,
        *,
        principal_id: str,
        permission_id: str,
        session: object | None,
    ) -> None:
        if (
            not isinstance(principal_id, str)
            or not principal_id
            or principal_id != principal_id.strip()
            or "*" in principal_id
        ):
            raise SystemServicesAuthorizationError("SYSTEM_ACTOR_INVALID")
        if session is None or getattr(session, "in_transaction", False) is not True:
            raise SystemServicesAuthorizationUnavailable("ACTIVE_TRANSACTION_REQUIRED")

        try:
            metadata = permission_metadata(permission_id)
        except (TypeError, ValueError) as error:
            raise SystemServicesAuthorizationError("CANONICAL_PERMISSION_REQUIRED") from error

        if (
            metadata.permission_id != permission_id
            or metadata.scope_kind != "SYSTEM"
            or metadata.system_assignment_required is not True
            or metadata.tenant_membership_required is not False
            or metadata.workforce_currentness_required is not True
            or metadata.authorizes_by_itself is not False
            or metadata.cross_tenant_capable is not False
            or metadata.financial_execution_capable is not False
            or metadata.deprecated_or_legacy is not False
            or metadata.disposition is not PermissionDisposition.CANONICAL
        ):
            raise SystemServicesAuthorizationError("SYSTEM_WORKFORCE_PERMISSION_REQUIRED")

        try:
            assignment = self._possession.resolve(
                principal_id=principal_id,
                permission_id=permission_id,
                session=cast(ClientSession | None, session),
            )
        except CurrentSystemPermissionPossessionError as error:
            raise SystemServicesAuthorizationUnavailable(
                "SYSTEM_PERMISSION_CURRENTNESS_UNAVAILABLE"
            ) from error
        if assignment is None:
            raise SystemServicesAuthorizationError("CURRENT_SYSTEM_PERMISSION_REQUIRED")
        if (
            getattr(assignment, "principal_id", None) != principal_id
            or getattr(assignment, "permission_id", None) != permission_id
        ):
            raise SystemServicesAuthorizationUnavailable("SYSTEM_ASSIGNMENT_BINDING_INVALID")

        observed_at = self._clock()
        if (
            not isinstance(observed_at, datetime)
            or observed_at.tzinfo is None
            or observed_at.utcoffset() is None
        ):
            raise SystemServicesAuthorizationUnavailable("OBSERVED_AT_INVALID")

        try:
            relationships = list_principal_relationships(
                PLATFORM_SCOPE_KIND,
                self._platform_scope_id,
                principal_id,
                collection=self._workforce,
                session=session,
            )
        except WorkforceRelationshipRegistryError as error:
            raise SystemServicesAuthorizationUnavailable(
                "PLATFORM_WORKFORCE_CURRENTNESS_UNAVAILABLE"
            ) from error

        if not relationships:
            raise SystemServicesAuthorizationError("ACTIVE_PLATFORM_WORKFORCE_REQUIRED")

        histories: dict[str, list[WorkforceRelationship]] = defaultdict(list)
        for relationship in relationships:
            if (
                not isinstance(relationship, WorkforceRelationship)
                or relationship.scope_kind is not WorkforceScopeKind.PLATFORM
                or relationship.scope_id != self._platform_scope_id
                or relationship.principal_id != principal_id
            ):
                raise SystemServicesAuthorizationUnavailable(
                    "PLATFORM_WORKFORCE_SCOPE_MISMATCH"
                )
            histories[relationship.relationship_id].append(relationship)

        try:
            currentness = tuple(
                derive_workforce_relationship_currentness(
                    tuple(sorted(history, key=lambda item: item.revision)),
                    observed_at,
                )
                for history in histories.values()
            )
            active = any(item.is_active for item in currentness)
        except WorkforceRelationshipCurrentnessError as error:
            raise SystemServicesAuthorizationUnavailable(
                "PLATFORM_WORKFORCE_HISTORY_INVALID"
            ) from error

        if not active:
            raise SystemServicesAuthorizationError("ACTIVE_PLATFORM_WORKFORCE_REQUIRED")


__all__ = [
    "VERSION",
    "PLATFORM_SCOPE_KIND",
    "SystemServicesAuthorizationError",
    "SystemServicesAuthorizationUnavailable",
    "SystemServicesEosAuthorizer",
]
