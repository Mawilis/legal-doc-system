"""
TITLE:
    WILSY OS System Permission Bootstrap Authority Pure Domain

VERSION:
    v1.0.0-P4-R4-D11-R1-SYSTEM-PERMISSION-BOOTSTRAP-AUTHORITY

AUTHORITY:
    Wilsy OS Sovereign IAM

EPITOME:
    Immutable non-tenant bootstrap authority evidence for seeding only the
    SYSTEM permission assignment/revocation command control plane.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/system_permission_bootstrap_authority.py

CERTIFICATION / UPDATE DATE:
    2026-10-14

AUTHORITY BOUNDARY:
    This domain is not a normal SYSTEM permission assignment, tenant authority,
    authorization role, business role, privileged activation, break-glass
    authority, or financial authority. It cannot authorize normal application
    operations or seed arbitrary permissions.

CREATION BOUNDARY:
    This pure domain does not decide who may create bootstrap authority.
    Creation must later be bound to a separately certified offline or
    installation trust-root path.

FINANCIAL AUTHORITY BOUNDARY:
    NONE.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
import re
from typing import Final


VERSION: Final = (
    "v1.0.0-P4-R4-D11-R1-"
    "SYSTEM-PERMISSION-BOOTSTRAP-AUTHORITY"
)

_FINGERPRINT = re.compile(r"^[0-9a-f]{128}$")

_SEED_ASSIGNMENT = (
    "SEED_SYSTEM_PERMISSION_ASSIGNMENT_COMMAND_AUTHORITY"
)

_SEED_REVOCATION = (
    "SEED_SYSTEM_PERMISSION_REVOCATION_COMMAND_AUTHORITY"
)

_ALLOWED_PURPOSES: Final = frozenset(
    {
        _SEED_ASSIGNMENT,
        _SEED_REVOCATION,
    }
)


class SystemPermissionBootstrapAuthorityStatus(
    StrEnum
):
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"


class SystemPermissionBootstrapAuthorityError(
    ValueError
):
    """Bounded pure-domain failure."""

    def __init__(
        self,
        code: str,
    ) -> None:
        self.code = code
        super().__init__(code)


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
        raise SystemPermissionBootstrapAuthorityError(
            name + "_INVALID"
        )

    return value


def _timestamp(
    name: str,
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise SystemPermissionBootstrapAuthorityError(
            name + "_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _revision(
    value: object,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 1
    ):
        raise SystemPermissionBootstrapAuthorityError(
            "REVISION_INVALID"
        )

    return value


def _fingerprint(
    value: object,
    *,
    nullable: bool,
) -> str | None:
    if value is None and nullable:
        return None

    if (
        not isinstance(value, str)
        or _FINGERPRINT.fullmatch(value) is None
    ):
        raise SystemPermissionBootstrapAuthorityError(
            "PREVIOUS_FINGERPRINT_INVALID"
        )

    return value


def _purpose(
    value: object,
) -> str:
    purpose = _identifier(
        "PURPOSE",
        value,
    )

    if purpose not in _ALLOWED_PURPOSES:
        raise SystemPermissionBootstrapAuthorityError(
            "BOOTSTRAP_PURPOSE_NOT_ALLOWED"
        )

    return purpose


def _canonical_payload(
    *,
    bootstrap_id: str,
    actor_principal_id: str,
    purpose: str,
    evidence_reference: str,
    issued_at: datetime,
    status: SystemPermissionBootstrapAuthorityStatus,
    revision: int,
    previous_fingerprint: str | None,
    retired_at: datetime | None,
    retirement_evidence_reference: str | None,
) -> bytes:
    payload = {
        "actor_principal_id":
            actor_principal_id,
        "bootstrap_id":
            bootstrap_id,
        "evidence_reference":
            evidence_reference,
        "issued_at":
            issued_at.isoformat(),
        "previous_fingerprint":
            previous_fingerprint,
        "purpose":
            purpose,
        "retired_at":
            (
                retired_at.isoformat()
                if retired_at is not None
                else None
            ),
        "retirement_evidence_reference":
            retirement_evidence_reference,
        "revision":
            revision,
        "status":
            status.value,
    }

    return json.dumps(
        payload,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest(
    **kwargs: object,
) -> str:
    payload = _canonical_payload(
        bootstrap_id=kwargs["bootstrap_id"],  # type: ignore[arg-type]
        actor_principal_id=kwargs["actor_principal_id"],  # type: ignore[arg-type]
        purpose=kwargs["purpose"],  # type: ignore[arg-type]
        evidence_reference=kwargs["evidence_reference"],  # type: ignore[arg-type]
        issued_at=kwargs["issued_at"],  # type: ignore[arg-type]
        status=kwargs["status"],  # type: ignore[arg-type]
        revision=kwargs["revision"],  # type: ignore[arg-type]
        previous_fingerprint=kwargs["previous_fingerprint"],  # type: ignore[arg-type]
        retired_at=kwargs["retired_at"],  # type: ignore[arg-type]
        retirement_evidence_reference=kwargs["retirement_evidence_reference"],  # type: ignore[arg-type]
    )

    return hashlib.sha3_512(
        payload
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class SystemPermissionBootstrapAuthority:
    bootstrap_id: str
    actor_principal_id: str
    purpose: str
    evidence_reference: str
    issued_at: datetime
    status: SystemPermissionBootstrapAuthorityStatus
    revision: int
    previous_fingerprint: str | None
    retired_at: datetime | None
    retirement_evidence_reference: str | None
    authority_fingerprint: str

    def __post_init__(
        self,
    ) -> None:
        bootstrap_id = _identifier(
            "BOOTSTRAP_ID",
            self.bootstrap_id,
        )

        actor = _identifier(
            "ACTOR_PRINCIPAL_ID",
            self.actor_principal_id,
        )

        purpose = _purpose(
            self.purpose,
        )

        evidence = _identifier(
            "EVIDENCE_REFERENCE",
            self.evidence_reference,
        )

        issued = _timestamp(
            "ISSUED_AT",
            self.issued_at,
        )

        revision = _revision(
            self.revision,
        )

        previous = _fingerprint(
            self.previous_fingerprint,
            nullable=True,
        )

        if not isinstance(
            self.status,
            SystemPermissionBootstrapAuthorityStatus,
        ):
            raise SystemPermissionBootstrapAuthorityError(
                "STATUS_INVALID"
            )

        retired_at = self.retired_at
        retirement_evidence = (
            self.retirement_evidence_reference
        )

        if (
            self.status
            is SystemPermissionBootstrapAuthorityStatus.ACTIVE
        ):
            if revision != 1:
                raise SystemPermissionBootstrapAuthorityError(
                    "ACTIVE_REVISION_MUST_BE_ONE"
                )

            if previous is not None:
                raise SystemPermissionBootstrapAuthorityError(
                    "ACTIVE_PREVIOUS_FINGERPRINT_FORBIDDEN"
                )

            if (
                retired_at is not None
                or retirement_evidence is not None
            ):
                raise SystemPermissionBootstrapAuthorityError(
                    "ACTIVE_RETIREMENT_MATERIAL_FORBIDDEN"
                )

        else:
            if revision != 2:
                raise SystemPermissionBootstrapAuthorityError(
                    "RETIRED_REVISION_MUST_BE_TWO"
                )

            if previous is None:
                raise SystemPermissionBootstrapAuthorityError(
                    "RETIRED_PREVIOUS_FINGERPRINT_REQUIRED"
                )

            if retired_at is None:
                raise SystemPermissionBootstrapAuthorityError(
                    "RETIRED_AT_REQUIRED"
                )

            retired_at = _timestamp(
                "RETIRED_AT",
                retired_at,
            )

            if retired_at < issued:
                raise SystemPermissionBootstrapAuthorityError(
                    "RETIREMENT_BEFORE_ISSUANCE"
                )

            retirement_evidence = _identifier(
                "RETIREMENT_EVIDENCE_REFERENCE",
                retirement_evidence,
            )

        fingerprint = _identifier(
            "AUTHORITY_FINGERPRINT",
            self.authority_fingerprint,
        )

        if _FINGERPRINT.fullmatch(
            fingerprint
        ) is None:
            raise SystemPermissionBootstrapAuthorityError(
                "AUTHORITY_FINGERPRINT_INVALID"
            )

        expected = _digest(
            bootstrap_id=bootstrap_id,
            actor_principal_id=actor,
            purpose=purpose,
            evidence_reference=evidence,
            issued_at=issued,
            status=self.status,
            revision=revision,
            previous_fingerprint=previous,
            retired_at=retired_at,
            retirement_evidence_reference=retirement_evidence,
        )

        if expected != fingerprint:
            raise SystemPermissionBootstrapAuthorityError(
                "AUTHORITY_FINGERPRINT_MISMATCH"
            )

        object.__setattr__(
            self,
            "bootstrap_id",
            bootstrap_id,
        )

        object.__setattr__(
            self,
            "actor_principal_id",
            actor,
        )

        object.__setattr__(
            self,
            "purpose",
            purpose,
        )

        object.__setattr__(
            self,
            "evidence_reference",
            evidence,
        )

        object.__setattr__(
            self,
            "issued_at",
            issued,
        )

        object.__setattr__(
            self,
            "retired_at",
            retired_at,
        )

        object.__setattr__(
            self,
            "retirement_evidence_reference",
            retirement_evidence,
        )

    @classmethod
    def issue(
        cls,
        *,
        bootstrap_id: str,
        actor_principal_id: str,
        purpose: str,
        evidence_reference: str,
        issued_at: datetime,
    ) -> SystemPermissionBootstrapAuthority:
        identity = _identifier(
            "BOOTSTRAP_ID",
            bootstrap_id,
        )

        actor = _identifier(
            "ACTOR_PRINCIPAL_ID",
            actor_principal_id,
        )

        bounded_purpose = _purpose(
            purpose,
        )

        evidence = _identifier(
            "EVIDENCE_REFERENCE",
            evidence_reference,
        )

        issued = _timestamp(
            "ISSUED_AT",
            issued_at,
        )

        fingerprint = _digest(
            bootstrap_id=identity,
            actor_principal_id=actor,
            purpose=bounded_purpose,
            evidence_reference=evidence,
            issued_at=issued,
            status=SystemPermissionBootstrapAuthorityStatus.ACTIVE,
            revision=1,
            previous_fingerprint=None,
            retired_at=None,
            retirement_evidence_reference=None,
        )

        return cls(
            bootstrap_id=identity,
            actor_principal_id=actor,
            purpose=bounded_purpose,
            evidence_reference=evidence,
            issued_at=issued,
            status=SystemPermissionBootstrapAuthorityStatus.ACTIVE,
            revision=1,
            previous_fingerprint=None,
            retired_at=None,
            retirement_evidence_reference=None,
            authority_fingerprint=fingerprint,
        )

    def retire(
        self,
        *,
        retired_at: datetime,
        retirement_evidence_reference: str,
    ) -> SystemPermissionBootstrapAuthority:
        if (
            self.status
            is not SystemPermissionBootstrapAuthorityStatus.ACTIVE
        ):
            raise SystemPermissionBootstrapAuthorityError(
                "BOOTSTRAP_AUTHORITY_TERMINAL"
            )

        retired = _timestamp(
            "RETIRED_AT",
            retired_at,
        )

        if retired < self.issued_at:
            raise SystemPermissionBootstrapAuthorityError(
                "RETIREMENT_BEFORE_ISSUANCE"
            )

        retirement_evidence = _identifier(
            "RETIREMENT_EVIDENCE_REFERENCE",
            retirement_evidence_reference,
        )

        fingerprint = _digest(
            bootstrap_id=self.bootstrap_id,
            actor_principal_id=self.actor_principal_id,
            purpose=self.purpose,
            evidence_reference=self.evidence_reference,
            issued_at=self.issued_at,
            status=SystemPermissionBootstrapAuthorityStatus.RETIRED,
            revision=2,
            previous_fingerprint=self.authority_fingerprint,
            retired_at=retired,
            retirement_evidence_reference=retirement_evidence,
        )

        return SystemPermissionBootstrapAuthority(
            bootstrap_id=self.bootstrap_id,
            actor_principal_id=self.actor_principal_id,
            purpose=self.purpose,
            evidence_reference=self.evidence_reference,
            issued_at=self.issued_at,
            status=SystemPermissionBootstrapAuthorityStatus.RETIRED,
            revision=2,
            previous_fingerprint=self.authority_fingerprint,
            retired_at=retired,
            retirement_evidence_reference=retirement_evidence,
            authority_fingerprint=fingerprint,
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "bootstrap_id":
                self.bootstrap_id,
            "actor_principal_id":
                self.actor_principal_id,
            "purpose":
                self.purpose,
            "evidence_reference":
                self.evidence_reference,
            "issued_at":
                self.issued_at.isoformat(),
            "status":
                self.status.value,
            "revision":
                self.revision,
            "previous_fingerprint":
                self.previous_fingerprint,
            "retired_at":
                (
                    self.retired_at.isoformat()
                    if self.retired_at is not None
                    else None
                ),
            "retirement_evidence_reference":
                self.retirement_evidence_reference,
            "authority_fingerprint":
                self.authority_fingerprint,
        }


__all__ = [
    "VERSION",
    "SystemPermissionBootstrapAuthority",
    "SystemPermissionBootstrapAuthorityError",
    "SystemPermissionBootstrapAuthorityStatus",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: tools/eos/auth/system_permission_bootstrap_authority.py
# VERSION: v1.0.0-P4-R4-D11-R1-SYSTEM-PERMISSION-BOOTSTRAP-AUTHORITY
# SCOPE: NON-TENANT BOOTSTRAP CONTROL-PLANE SEED AUTHORITY ONLY
# NORMAL SYSTEM PERMISSION ASSIGNMENT: NO
# TENANT AUTHORITY: NONE
# AUTHORIZATION ROLE AUTHORITY: NONE
# BUSINESS ROLE AUTHORITY: NONE
# FOUNDER SHORTCUT: NONE
# ADMIN SHORTCUT: NONE
# PRIVILEGED ELIGIBILITY AUTHORITY: NONE
# SECURITY ASSURANCE AUTHORITY: NONE
# PRIVILEGED ACTIVATION AUTHORITY: NONE
# BREAK-GLASS AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# I/O: NONE
# CLOCK: NONE
# RANDOMNESS: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
