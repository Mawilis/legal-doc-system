"""Tenant-principal workforce currentness projection.

VERSION: v1.0.0-W3D-R6-WORKFORCE-AUTHORIZATION-CURRENTNESS

AUTHORITY BOUNDARY:
This module derives workforce currentness facts only.  It does not authorize,
grant permissions, infer employment from a business role, create IAM authority,
open transactions, or create financial authority.

SEMANTIC LOCK:
WORKFORCE CURRENTNESS != AUTHORIZATION.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Mapping, Sequence

from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceScopeKind,
)
from tools.eos.workforce.domain.workforce_relationship_currentness import (
    WorkforceRelationshipCurrentness,
    WorkforceRelationshipCurrentnessError,
    derive_workforce_relationship_currentness,
)


VERSION = "v1.0.0-W3D-R6-WORKFORCE-AUTHORIZATION-CURRENTNESS"


class WorkforceAuthorizationCurrentnessError(ValueError):
    """Raised when tenant-principal workforce history cannot be trusted."""


@dataclass(frozen=True, slots=True)
class TenantPrincipalWorkforceCurrentness:
    """Derived currentness facts for one principal in one tenant."""

    tenant_id: str
    principal_id: str
    observed_at: datetime
    relationship_currentness: Mapping[
        str,
        WorkforceRelationshipCurrentness,
    ]
    active_relationship_ids: tuple[str, ...]

    @property
    def has_active_relationship(self) -> bool:
        """Return fact only; this property does not authorize."""
        return bool(self.active_relationship_ids)


def _nonblank(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        raise WorkforceAuthorizationCurrentnessError(
            f"{label.upper()}_INVALID"
        )
    return value


def _observed(value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise WorkforceAuthorizationCurrentnessError(
            "OBSERVED_AT_INVALID"
        )
    return value


def derive_tenant_principal_workforce_currentness(
    relationships: Sequence[WorkforceRelationship],
    *,
    tenant_id: object,
    principal_id: object,
    observed_at: object,
) -> TenantPrincipalWorkforceCurrentness:
    """Derive exact tenant-principal workforce currentness without authorization.

    ``relationships`` must contain the complete persisted histories returned for
    exactly one TENANT scope and principal.  Empty history is lawful and means
    no current workforce relationship is observed.

    Every relationship history is delegated to the canonical W3B temporal
    currentness derivation; this component does not duplicate W3B lifecycle
    semantics.
    """

    tenant = _nonblank(tenant_id, "tenant_id")
    principal = _nonblank(principal_id, "principal_id")
    moment = _observed(observed_at)

    if not isinstance(relationships, Sequence):
        raise WorkforceAuthorizationCurrentnessError(
            "RELATIONSHIPS_INVALID"
        )

    values = tuple(relationships)

    if any(
        not isinstance(value, WorkforceRelationship)
        for value in values
    ):
        raise WorkforceAuthorizationCurrentnessError(
            "RELATIONSHIP_TYPE_INVALID"
        )

    histories: dict[str, list[WorkforceRelationship]] = {}

    for value in values:
        if value.scope_kind is not WorkforceScopeKind.TENANT:
            raise WorkforceAuthorizationCurrentnessError(
                "NON_TENANT_RELATIONSHIP_FORBIDDEN"
            )

        if value.scope_id != tenant:
            raise WorkforceAuthorizationCurrentnessError(
                "CROSS_TENANT_RELATIONSHIP_FORBIDDEN"
            )

        if value.principal_id != principal:
            raise WorkforceAuthorizationCurrentnessError(
                "PRINCIPAL_RELATIONSHIP_MISMATCH"
            )

        histories.setdefault(
            value.relationship_id,
            [],
        ).append(value)

    derived: dict[str, WorkforceRelationshipCurrentness] = {}
    active: list[str] = []

    for relationship_id in sorted(histories):
        history = tuple(
            sorted(
                histories[relationship_id],
                key=lambda item: item.revision,
            )
        )

        try:
            currentness = (
                derive_workforce_relationship_currentness(
                    history,
                    moment,
                )
            )
        except WorkforceRelationshipCurrentnessError as error:
            raise WorkforceAuthorizationCurrentnessError(
                "RELATIONSHIP_CURRENTNESS_INVALID"
            ) from error

        derived[relationship_id] = currentness

        if currentness.is_active:
            active.append(relationship_id)

    return TenantPrincipalWorkforceCurrentness(
        tenant_id=tenant,
        principal_id=principal,
        observed_at=moment,
        relationship_currentness=MappingProxyType(
            dict(derived)
        ),
        active_relationship_ids=tuple(active),
    )


__all__ = [
    "VERSION",
    "TenantPrincipalWorkforceCurrentness",
    "WorkforceAuthorizationCurrentnessError",
    "derive_tenant_principal_workforce_currentness",
]


# ARTIFACT: workforce_authorization_currentness.py
# AUTHORITY BOUNDARY: derived workforce facts only; never authorization.
# FINANCIAL EXECUTION AUTHORITY: NO.
