"""Canonical immutable workforce relationship for WILSY OS.

VERSION:
    v1.0.0-WILSY-W3A-WORKFORCE-RELATIONSHIP

AUTHORITY:
    Immutable organisation-scoped workforce relationship evidence only.

This domain deliberately does not own:
- person identity proofing;
- authentication;
- principal lifecycle;
- tenant membership;
- business/system roles;
- permissions;
- authorization;
- subscription/commercial eligibility;
- professional or regulatory standing;
- financial execution;
- session/token revocation.

Semantic locks:
    PERSON != PRINCIPAL
    WORKFORCE_RELATIONSHIP != IAM_AUTHORITY
    EMPLOYMENT != AUTHORIZATION
    STATUS != PERMISSION
    JOB_TITLE != AUTHORITY
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha3_512
import json
from typing import Any, Final, Mapping, Self


VERSION: Final[str] = (
    "v1.0.0-WILSY-W3A-WORKFORCE-RELATIONSHIP"
)
SCHEMA: Final[str] = (
    "WILSY-WORKFORCE-RELATIONSHIP/V1"
)

WORKFORCE_RELATIONSHIP_FIELDS: Final[
    frozenset[str]
] = frozenset(
    {
        "relationship_id",
        "revision",
        "scope_kind",
        "scope_id",
        "principal_id",
        "relationship_type",
        "status",
        "effective_from",
        "effective_until",
        "status_effective_at",
        "reason_reference",
        "supersedes_fingerprint",
        "schema",
        "version",
        "fingerprint",
    }
)


class WorkforceRelationshipError(ValueError):
    """Base fail-closed workforce-domain error."""


class WorkforceScopeKind(str, Enum):
    """Organisation authority boundary."""

    PLATFORM = "PLATFORM"
    TENANT = "TENANT"


class WorkforceRelationshipType(str, Enum):
    """Closed initial workforce relationship vocabulary."""

    EMPLOYEE = "EMPLOYEE"
    CONTRACTOR = "CONTRACTOR"
    CONSULTANT = "CONSULTANT"
    TEMPORARY_WORKER = "TEMPORARY_WORKER"
    INTERN = "INTERN"
    AGENCY_WORKER = "AGENCY_WORKER"


class WorkforceRelationshipStatus(str, Enum):
    """Operational relationship currentness input."""

    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    ENDED = "ENDED"


def _nonblank(
    value: object,
    field: str,
) -> str:
    if type(value) is not str:
        raise WorkforceRelationshipError(
            f"{field.upper()}_INVALID"
        )

    result = value.strip()

    if not result:
        raise WorkforceRelationshipError(
            f"{field.upper()}_INVALID"
        )

    return result


def _aware(
    value: object,
    field: str,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise WorkforceRelationshipError(
            f"{field.upper()}_INVALID"
        )

    return value


def _optional_aware(
    value: object,
    field: str,
) -> datetime | None:
    if value is None:
        return None

    return _aware(
        value,
        field,
    )


def _optional_nonblank(
    value: object,
    field: str,
) -> str | None:
    if value is None:
        return None

    return _nonblank(
        value,
        field,
    )


def _parse_datetime(
    value: object,
    field: str,
) -> datetime:
    if type(value) is not str:
        raise WorkforceRelationshipError(
            f"{field.upper()}_INVALID"
        )

    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise WorkforceRelationshipError(
            f"{field.upper()}_INVALID"
        ) from error

    return _aware(
        parsed,
        field,
    )


def _optional_parse_datetime(
    value: object,
    field: str,
) -> datetime | None:
    if value is None:
        return None

    return _parse_datetime(
        value,
        field,
    )


def _fingerprint_payload(
    payload: Mapping[str, Any],
) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")

    return sha3_512(
        encoded
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class WorkforceRelationship:
    """One immutable workforce relationship revision.

    This artifact is an input to later authorization/currentness
    composition.  It does not itself grant access.
    """

    relationship_id: str
    revision: int

    scope_kind: WorkforceScopeKind
    scope_id: str

    principal_id: str
    relationship_type: WorkforceRelationshipType
    status: WorkforceRelationshipStatus

    effective_from: datetime
    effective_until: datetime | None
    status_effective_at: datetime

    reason_reference: str
    supersedes_fingerprint: str | None

    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        relationship_id = _nonblank(
            self.relationship_id,
            "relationship_id",
        )

        if (
            type(self.revision) is not int
            or self.revision < 1
        ):
            raise WorkforceRelationshipError(
                "REVISION_INVALID"
            )

        if not isinstance(
            self.scope_kind,
            WorkforceScopeKind,
        ):
            raise WorkforceRelationshipError(
                "SCOPE_KIND_INVALID"
            )

        scope_id = _nonblank(
            self.scope_id,
            "scope_id",
        )

        principal_id = _nonblank(
            self.principal_id,
            "principal_id",
        )

        if not isinstance(
            self.relationship_type,
            WorkforceRelationshipType,
        ):
            raise WorkforceRelationshipError(
                "RELATIONSHIP_TYPE_INVALID"
            )

        if not isinstance(
            self.status,
            WorkforceRelationshipStatus,
        ):
            raise WorkforceRelationshipError(
                "STATUS_INVALID"
            )

        effective_from = _aware(
            self.effective_from,
            "effective_from",
        )

        effective_until = _optional_aware(
            self.effective_until,
            "effective_until",
        )

        status_effective_at = _aware(
            self.status_effective_at,
            "status_effective_at",
        )

        reason_reference = _nonblank(
            self.reason_reference,
            "reason_reference",
        )

        supersedes_fingerprint = (
            _optional_nonblank(
                self.supersedes_fingerprint,
                "supersedes_fingerprint",
            )
        )

        if (
            effective_until is not None
            and effective_until <= effective_from
        ):
            raise WorkforceRelationshipError(
                "EFFECTIVE_PERIOD_INVALID"
            )

        if status_effective_at < effective_from:
            raise WorkforceRelationshipError(
                "STATUS_EFFECTIVE_AT_INVALID"
            )

        if (
            effective_until is not None
            and status_effective_at
            > effective_until
        ):
            raise WorkforceRelationshipError(
                "STATUS_EFFECTIVE_AT_INVALID"
            )

        if self.revision == 1:
            if supersedes_fingerprint is not None:
                raise WorkforceRelationshipError(
                    "FIRST_REVISION_SUPERSEDES_FORBIDDEN"
                )
        else:
            if supersedes_fingerprint is None:
                raise WorkforceRelationshipError(
                    "LATER_REVISION_SUPERSEDES_REQUIRED"
                )

            if (
                len(supersedes_fingerprint) != 128
                or any(
                    char not in "0123456789abcdef"
                    for char in supersedes_fingerprint
                )
            ):
                raise WorkforceRelationshipError(
                    "SUPERSEDES_FINGERPRINT_INVALID"
                )

        if (
            self.status
            is WorkforceRelationshipStatus.ACTIVE
            and effective_until is not None
            and status_effective_at
            >= effective_until
        ):
            raise WorkforceRelationshipError(
                "ACTIVE_AT_OR_AFTER_EXPIRY"
            )

        object.__setattr__(
            self,
            "relationship_id",
            relationship_id,
        )
        object.__setattr__(
            self,
            "scope_id",
            scope_id,
        )
        object.__setattr__(
            self,
            "principal_id",
            principal_id,
        )
        object.__setattr__(
            self,
            "effective_from",
            effective_from,
        )
        object.__setattr__(
            self,
            "effective_until",
            effective_until,
        )
        object.__setattr__(
            self,
            "status_effective_at",
            status_effective_at,
        )
        object.__setattr__(
            self,
            "reason_reference",
            reason_reference,
        )
        object.__setattr__(
            self,
            "supersedes_fingerprint",
            supersedes_fingerprint,
        )

        canonical = self._payload_without_fingerprint()
        expected = _fingerprint_payload(
            canonical
        )

        supplied = self.fingerprint

        if supplied:
            if supplied != expected:
                raise WorkforceRelationshipError(
                    "FINGERPRINT_INVALID"
                )
        else:
            object.__setattr__(
                self,
                "fingerprint",
                expected,
            )

    def _payload_without_fingerprint(
        self,
    ) -> dict[str, Any]:
        return {
            "relationship_id":
                self.relationship_id,
            "revision":
                self.revision,
            "scope_kind":
                self.scope_kind.value,
            "scope_id":
                self.scope_id,
            "principal_id":
                self.principal_id,
            "relationship_type":
                self.relationship_type.value,
            "status":
                self.status.value,
            "effective_from":
                self.effective_from.isoformat(),
            "effective_until":
                (
                    None
                    if self.effective_until is None
                    else
                    self.effective_until.isoformat()
                ),
            "status_effective_at":
                self.status_effective_at.isoformat(),
            "reason_reference":
                self.reason_reference,
            "supersedes_fingerprint":
                self.supersedes_fingerprint,
            "schema":
                self.schema,
            "version":
                self.version,
        }

    def to_dict(
        self,
    ) -> dict[str, Any]:
        payload = (
            self._payload_without_fingerprint()
        )

        payload["fingerprint"] = (
            self.fingerprint
        )

        return payload

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> Self:
        if not isinstance(
            payload,
            Mapping,
        ):
            raise WorkforceRelationshipError(
                "PAYLOAD_INVALID"
            )

        keys = frozenset(
            payload.keys()
        )

        if keys != WORKFORCE_RELATIONSHIP_FIELDS:
            raise WorkforceRelationshipError(
                "PAYLOAD_FIELDS_INVALID"
            )

        try:
            scope_kind = WorkforceScopeKind(
                payload["scope_kind"]
            )
            relationship_type = (
                WorkforceRelationshipType(
                    payload[
                        "relationship_type"
                    ]
                )
            )
            status = (
                WorkforceRelationshipStatus(
                    payload["status"]
                )
            )
        except (
            ValueError,
            TypeError,
        ) as error:
            raise WorkforceRelationshipError(
                "ENUM_VALUE_INVALID"
            ) from error

        revision = payload["revision"]

        if type(revision) is not int:
            raise WorkforceRelationshipError(
                "REVISION_INVALID"
            )

        schema = payload["schema"]
        version = payload["version"]

        if schema != SCHEMA:
            raise WorkforceRelationshipError(
                "SCHEMA_INVALID"
            )

        if version != VERSION:
            raise WorkforceRelationshipError(
                "VERSION_INVALID"
            )

        fingerprint = payload[
            "fingerprint"
        ]

        if type(fingerprint) is not str:
            raise WorkforceRelationshipError(
                "FINGERPRINT_INVALID"
            )

        return cls(
            relationship_id=_nonblank(
                payload["relationship_id"],
                "relationship_id",
            ),
            revision=revision,
            scope_kind=scope_kind,
            scope_id=_nonblank(
                payload["scope_id"],
                "scope_id",
            ),
            principal_id=_nonblank(
                payload["principal_id"],
                "principal_id",
            ),
            relationship_type=(
                relationship_type
            ),
            status=status,
            effective_from=(
                _parse_datetime(
                    payload[
                        "effective_from"
                    ],
                    "effective_from",
                )
            ),
            effective_until=(
                _optional_parse_datetime(
                    payload[
                        "effective_until"
                    ],
                    "effective_until",
                )
            ),
            status_effective_at=(
                _parse_datetime(
                    payload[
                        "status_effective_at"
                    ],
                    "status_effective_at",
                )
            ),
            reason_reference=_nonblank(
                payload[
                    "reason_reference"
                ],
                "reason_reference",
            ),
            supersedes_fingerprint=(
                _optional_nonblank(
                    payload[
                        "supersedes_fingerprint"
                    ],
                    "supersedes_fingerprint",
                )
            ),
            schema=SCHEMA,
            version=VERSION,
            fingerprint=fingerprint,
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "WORKFORCE_RELATIONSHIP_FIELDS",
    "WorkforceRelationship",
    "WorkforceRelationshipError",
    "WorkforceRelationshipStatus",
    "WorkforceRelationshipType",
    "WorkforceScopeKind",
]


# AUTHORITY BOUNDARY:
# immutable workforce relationship evidence only
#
# FAIL-CLOSED POSTURE:
# malformed, ambiguous, invalid-period, invalid-lineage and
# fingerprint-corrupt artifacts reject
#
# FINANCIAL EXECUTION AUTHORITY:
# NONE
