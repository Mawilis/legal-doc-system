"""
TITLE:
    WILSY OS System Permission Assignment Pure Domain

VERSION:
    v1.0.0-P4-R4-D5-SYSTEM-PERMISSION-ASSIGNMENT-DOMAIN

AUTHORITY:
    Wilsy OS Sovereign IAM

EPITOME:
    Represent one explicit immutable assignment of one canonical SYSTEM-scoped
    permission to one principal without creating tenant authority, role authority,
    privileged activation, break-glass authority, or financial authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/system_permission_assignment.py

COLLABORATION / OWNERSHIP:
    Sovereign IAM owns the pure assignment semantics. Permission Namespace owns
    permission vocabulary. Future persistence owns durable history. Future
    authorization composition must separately prove current principal and current
    ACTIVE assignment.

CERTIFICATION / UPDATE DATE:
    2026-10-14

CHANGELOG:
    v1.0.0-P4-R4-D5-SYSTEM-PERMISSION-ASSIGNMENT-DOMAIN
        Introduces explicit SYSTEM permission-possession evidence scoped only by
        principal_id + permission_id, with immutable ACTIVE -> REVOKED revision
        chaining. No registry, assignment issuance authority, privileged
        activation, P5 use, break-glass, tenant, role, or financial authority.

SECURITY / PRIVACY POSTURE:
    Contains no password, OTP, token, session secret, private key, or raw proof.

TENANT BOUNDARY:
    No tenant identifier exists in this domain.

AUTHORITY BOUNDARY:
    Assignment evidence is not authorization. Historic ACTIVE assignment is not
    current permission possession. Current permission possession must later
    compose current principal truth plus a current ACTIVE durable assignment.

FINANCIAL AUTHORITY BOUNDARY:
    NONE.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
from json import dumps
from typing import Final

from tools.eos.auth.permission_namespace import (
    PermissionDisposition,
    permission_metadata,
)


VERSION: Final = (
    "v1.0.0-P4-R4-D5-"
    "SYSTEM-PERMISSION-ASSIGNMENT-DOMAIN"
)

SCHEMA: Final = (
    "WILSY-SYSTEM-PERMISSION-ASSIGNMENT/V1"
)

FINGERPRINT_LENGTH: Final = 128


class SystemPermissionAssignmentError(ValueError):
    """Raised when assignment authority material is malformed or inconsistent."""


class SystemPermissionAssignmentStatus(StrEnum):
    """Closed lifecycle for one SYSTEM permission assignment."""

    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


def _identifier(
    field_name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        raise SystemPermissionAssignmentError(
            field_name + "_INVALID"
        )
    return value


def _timestamp(
    field_name: str,
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise SystemPermissionAssignmentError(
            field_name + "_INVALID"
        )
    return value.astimezone(timezone.utc)


def _fingerprint(
    payload: dict[str, object],
) -> str:
    encoded = dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")

    return sha3_512(encoded).hexdigest()


def _require_system_permission(
    permission_id: object,
) -> str:
    permission = _identifier(
        "PERMISSION_ID",
        permission_id,
    )

    try:
        metadata = permission_metadata(
            permission
        )
    except (TypeError, ValueError) as error:
        raise SystemPermissionAssignmentError(
            "PERMISSION_NOT_CANONICAL"
        ) from error

    if (
        metadata.permission_id != permission
        or metadata.scope_kind != "SYSTEM"
        or metadata.system_assignment_required
        is not True
        or metadata.tenant_membership_required
        is not False
        or metadata.cross_tenant_capable
        is not False
        or metadata.financial_execution_capable
        is not False
        or metadata.deprecated_or_legacy
        is not False
        or metadata.authorizes_by_itself
        is not False
        or metadata.disposition
        is not PermissionDisposition.CANONICAL
    ):
        raise SystemPermissionAssignmentError(
            "SYSTEM_PERMISSION_REQUIRED"
        )

    return permission


@dataclass(
    frozen=True,
    slots=True,
)
class SystemPermissionAssignment:
    """Immutable evidence that one principal was explicitly assigned one SYSTEM permission."""

    assignment_id: str
    principal_id: str
    permission_id: str
    status: SystemPermissionAssignmentStatus
    assigned_by_principal_id: str
    assigned_at: datetime
    assignment_evidence_reference: str
    revision: int
    previous_assignment_fingerprint: str | None
    revoked_by_principal_id: str | None
    revoked_at: datetime | None
    revocation_evidence_reference: str | None
    assignment_fingerprint: str = field(
        init=False,
    )

    def __post_init__(self) -> None:
        assignment_id = _identifier(
            "ASSIGNMENT_ID",
            self.assignment_id,
        )
        principal_id = _identifier(
            "PRINCIPAL_ID",
            self.principal_id,
        )
        permission_id = _require_system_permission(
            self.permission_id,
        )
        assigned_by = _identifier(
            "ASSIGNED_BY_PRINCIPAL_ID",
            self.assigned_by_principal_id,
        )
        assigned_at = _timestamp(
            "ASSIGNED_AT",
            self.assigned_at,
        )
        evidence = _identifier(
            "ASSIGNMENT_EVIDENCE_REFERENCE",
            self.assignment_evidence_reference,
        )

        if (
            not isinstance(
                self.status,
                SystemPermissionAssignmentStatus,
            )
        ):
            raise SystemPermissionAssignmentError(
                "STATUS_INVALID"
            )

        if (
            not isinstance(self.revision, int)
            or isinstance(self.revision, bool)
            or self.revision < 1
        ):
            raise SystemPermissionAssignmentError(
                "REVISION_INVALID"
            )

        previous = (
            self.previous_assignment_fingerprint
        )

        if previous is not None:
            if (
                not isinstance(previous, str)
                or len(previous)
                != FINGERPRINT_LENGTH
                or any(
                    char not in "0123456789abcdef"
                    for char in previous
                )
            ):
                raise SystemPermissionAssignmentError(
                    "PREVIOUS_ASSIGNMENT_FINGERPRINT_INVALID"
                )

        revoked_by = (
            self.revoked_by_principal_id
        )
        revoked_at = self.revoked_at
        revocation_reference = (
            self.revocation_evidence_reference
        )

        if (
            self.status
            is SystemPermissionAssignmentStatus.ACTIVE
        ):
            if self.revision != 1:
                raise SystemPermissionAssignmentError(
                    "ACTIVE_REVISION_INVALID"
                )
            if previous is not None:
                raise SystemPermissionAssignmentError(
                    "ACTIVE_PREVIOUS_FINGERPRINT_FORBIDDEN"
                )
            if (
                revoked_by is not None
                or revoked_at is not None
                or revocation_reference is not None
            ):
                raise SystemPermissionAssignmentError(
                    "ACTIVE_REVOCATION_METADATA_FORBIDDEN"
                )

        else:
            if self.revision < 2:
                raise SystemPermissionAssignmentError(
                    "REVOKED_REVISION_INVALID"
                )
            if previous is None:
                raise SystemPermissionAssignmentError(
                    "REVOKED_PREVIOUS_FINGERPRINT_REQUIRED"
                )
            revoked_by = _identifier(
                "REVOKED_BY_PRINCIPAL_ID",
                revoked_by,
            )
            revoked_at = _timestamp(
                "REVOKED_AT",
                revoked_at,
            )
            revocation_reference = _identifier(
                "REVOCATION_EVIDENCE_REFERENCE",
                revocation_reference,
            )
            if revoked_at < assigned_at:
                raise SystemPermissionAssignmentError(
                    "REVOCATION_CHRONOLOGY_INVALID"
                )

        object.__setattr__(
            self,
            "assignment_id",
            assignment_id,
        )
        object.__setattr__(
            self,
            "principal_id",
            principal_id,
        )
        object.__setattr__(
            self,
            "permission_id",
            permission_id,
        )
        object.__setattr__(
            self,
            "assigned_by_principal_id",
            assigned_by,
        )
        object.__setattr__(
            self,
            "assigned_at",
            assigned_at,
        )
        object.__setattr__(
            self,
            "assignment_evidence_reference",
            evidence,
        )
        object.__setattr__(
            self,
            "revoked_by_principal_id",
            revoked_by,
        )
        object.__setattr__(
            self,
            "revoked_at",
            revoked_at,
        )
        object.__setattr__(
            self,
            "revocation_evidence_reference",
            revocation_reference,
        )

        fingerprint = _fingerprint(
            self.authority_payload()
        )

        object.__setattr__(
            self,
            "assignment_fingerprint",
            fingerprint,
        )

    @classmethod
    def assign(
        cls,
        *,
        assignment_id: str,
        principal_id: str,
        permission_id: str,
        assigned_by_principal_id: str,
        assigned_at: datetime,
        assignment_evidence_reference: str,
    ) -> SystemPermissionAssignment:
        """Construct one initial ACTIVE immutable assignment."""

        return cls(
            assignment_id=assignment_id,
            principal_id=principal_id,
            permission_id=permission_id,
            status=(
                SystemPermissionAssignmentStatus
                .ACTIVE
            ),
            assigned_by_principal_id=
                assigned_by_principal_id,
            assigned_at=assigned_at,
            assignment_evidence_reference=
                assignment_evidence_reference,
            revision=1,
            previous_assignment_fingerprint=None,
            revoked_by_principal_id=None,
            revoked_at=None,
            revocation_evidence_reference=None,
        )

    def revoke(
        self,
        *,
        revoked_by_principal_id: str,
        revoked_at: datetime,
        revocation_evidence_reference: str,
    ) -> SystemPermissionAssignment:
        """Return the next terminal REVOKED revision without mutating self."""

        if (
            self.status
            is not SystemPermissionAssignmentStatus.ACTIVE
        ):
            raise SystemPermissionAssignmentError(
                "ASSIGNMENT_ALREADY_REVOKED"
            )

        return SystemPermissionAssignment(
            assignment_id=self.assignment_id,
            principal_id=self.principal_id,
            permission_id=self.permission_id,
            status=(
                SystemPermissionAssignmentStatus
                .REVOKED
            ),
            assigned_by_principal_id=
                self.assigned_by_principal_id,
            assigned_at=self.assigned_at,
            assignment_evidence_reference=
                self.assignment_evidence_reference,
            revision=self.revision + 1,
            previous_assignment_fingerprint=
                self.assignment_fingerprint,
            revoked_by_principal_id=
                revoked_by_principal_id,
            revoked_at=revoked_at,
            revocation_evidence_reference=
                revocation_evidence_reference,
        )

    @property
    def is_active(self) -> bool:
        """Return lifecycle state only; this is not current permission authorization."""

        return (
            self.status
            is SystemPermissionAssignmentStatus.ACTIVE
        )

    def authority_payload(
        self,
    ) -> dict[str, object]:
        """Return canonical authority material used only for integrity fingerprinting."""

        return {
            "schema": SCHEMA,
            "version": VERSION,
            "assignment_id":
                self.assignment_id,
            "principal_id":
                self.principal_id,
            "permission_id":
                self.permission_id,
            "status":
                self.status.value,
            "assigned_by_principal_id":
                self.assigned_by_principal_id,
            "assigned_at":
                self.assigned_at.isoformat(),
            "assignment_evidence_reference":
                self.assignment_evidence_reference,
            "revision":
                self.revision,
            "previous_assignment_fingerprint":
                self.previous_assignment_fingerprint,
            "revoked_by_principal_id":
                self.revoked_by_principal_id,
            "revoked_at": (
                None
                if self.revoked_at is None
                else self.revoked_at.isoformat()
            ),
            "revocation_evidence_reference":
                self.revocation_evidence_reference,
        }

    def to_dict(
        self,
    ) -> dict[str, object]:
        """Serialize immutable evidence without turning it into authorization."""

        return {
            **self.authority_payload(),
            "assignment_fingerprint":
                self.assignment_fingerprint,
        }


__all__ = [
    "VERSION",
    "SCHEMA",
    "SystemPermissionAssignmentError",
    "SystemPermissionAssignmentStatus",
    "SystemPermissionAssignment",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: tools/eos/auth/system_permission_assignment.py
# VERSION: v1.0.0-P4-R4-D5-SYSTEM-PERMISSION-ASSIGNMENT-DOMAIN
# SCOPE: principal_id + canonical SYSTEM permission_id only
# TENANT AUTHORITY: NONE
# ROLE AUTHORITY: NONE
# PRIVILEGED ACTIVATION AUTHORITY: NONE
# P5 PRIVILEGED USE AUTHORITY: NONE
# BREAK-GLASS AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# PERSISTENCE AUTHORITY: NONE
# CURRENT PERMISSION POSSESSION: NOT PROVEN BY THIS VALUE ALONE
# END OF WILSY OS SOVEREIGN ARTIFACT
