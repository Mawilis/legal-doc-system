"""WILSY OS sovereign HR operations pure domain.

TITLE: Sovereign HR Operations Pure Domain
VERSION: v1.0.0-P0-C12E1-HR-OPERATIONS-DOMAIN
AUTHORITY: Wilsy OS Core Governance / Python EOS
PURPOSE: Immutable HR evidence values only.

CURRENT CERTIFIED SCOPE:
- EmployeeRelation only.

AUTHORITY BOUNDARY:
This module records bounded HR relation evidence. It does not
authenticate a principal, grant IAM authority, determine legal
sufficiency, execute payroll, calculate payroll, authorize payment,
release funds, settle money, generate artifacts, expose HTTP routes,
provide BFF transport, or wire a browser client.

FINANCIAL AUTHORITY BOUNDARY:
No financial execution or settlement authority exists here.
Kennel EOS remains the exclusive financial-execution authority.

TRANSACTION BOUNDARY:
Pure immutable in-memory construction and deterministic
serialization only. No MongoDB, HTTP, filesystem, network,
transaction, retry, notification, or side effects.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Final, NoReturn, cast
import unicodedata


VERSION: Final[str] = (
    "v1.0.0-P0-C12E1-HR-OPERATIONS-DOMAIN"
)

EMPLOYEE_RELATION_SCHEMA: Final[str] = (
    "WILSY-HR-EMPLOYEE-RELATION/V1"
)

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)

_HEX_512: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)

_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "default",
        "global",
        "global_root",
        "root",
        "master",
        "*",
    }
)


class EmployeeRelationError(ValueError):
    """Stable non-sensitive employee-relation validation failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class EmployeeRelationActionType(StrEnum):
    """Bounded employee-relations actions evidenced by the HR UI."""

    VERBAL_WARNING = "Verbal warning"
    WRITTEN_WARNING = "Written warning"
    FINAL_WRITTEN_WARNING = "Final written warning"
    SUSPENSION = "Suspension"
    DISCIPLINARY_HEARING = "Disciplinary hearing"
    DISMISSAL = "Dismissal"
    PERFORMANCE_IMPROVEMENT_PLAN = "Performance improvement plan"


class EmployeeRelationStatus(StrEnum):
    """Bounded case states evidenced by the HR UI."""

    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    EMPLOYEE_RESPONSE_PENDING = "EMPLOYEE_RESPONSE_PENDING"
    HEARING_SCHEDULED = "HEARING_SCHEDULED"
    CLOSED = "CLOSED"


_EMPLOYEE_RELATION_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "relation_version",
    "tenant_id",
    "relation_id",
    "employee_id",
    "action_type",
    "incident_date",
    "policy_breach",
    "incident_summary",
    "corrective_action",
    "employee_response",
    "hearing_date",
    "outcome",
    "status",
    "source_artifact_id",
    "source_artifact_fingerprint",
    "fingerprint",
)

EMPLOYEE_RELATION_FIELDS: Final[frozenset[str]] = frozenset(
    _EMPLOYEE_RELATION_FIELDS
)


def _fail(
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = EmployeeRelationError(code)

    if cause is None:
        raise error

    raise error from cause


def _identity(
    name: str,
    value: object,
) -> str:

    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail(
            f"P0_C12E1_{name.upper()}_INVALID"
        )

    return cast(str, value)


def _tenant(
    value: object,
) -> str:

    tenant = _identity(
        "tenant_id",
        value,
    )

    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail(
            "P0_C12E1_TENANT_REQUIRED"
        )

    return tenant


def _required_text(
    name: str,
    value: object,
    *,
    limit: int = 4096,
) -> str:

    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or "\x00" in value
    ):
        _fail(
            f"P0_C12E1_{name.upper()}_INVALID"
        )

    normalized = unicodedata.normalize(
        "NFC",
        value,
    )

    if (
        not normalized
        or len(normalized) > limit
    ):
        _fail(
            f"P0_C12E1_{name.upper()}_INVALID"
        )

    return normalized


def _optional_text(
    name: str,
    value: object,
    *,
    limit: int = 4096,
) -> str | None:

    if value is None:
        return None

    return _required_text(
        name,
        value,
        limit=limit,
    )


def _date_value(
    name: str,
    value: object,
) -> date | None:

    if value is None:
        return None

    if isinstance(
        value,
        date,
    ):
        return value

    if isinstance(
        value,
        str,
    ):
        try:
            return date.fromisoformat(
                value
            )
        except ValueError as error:
            _fail(
                f"P0_C12E1_{name.upper()}_INVALID",
                error,
            )

    _fail(
        f"P0_C12E1_{name.upper()}_INVALID"
    )


def _fingerprint(
    name: str,
    value: object,
) -> str:

    if (
        not isinstance(
            value,
            str,
        )
        or _HEX_512.fullmatch(
            value
        ) is None
    ):
        _fail(
            f"P0_C12E1_{name.upper()}_INVALID"
        )

    return value


def _json_value(
    value: object,
) -> object:

    if isinstance(
        value,
        date,
    ):
        return value.isoformat()

    if isinstance(
        value,
        StrEnum,
    ):
        return value.value

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class EmployeeRelation:
    """Immutable bounded employee-relations evidence."""

    tenant_id: str
    relation_id: str
    employee_id: str
    action_type: EmployeeRelationActionType | str
    status: EmployeeRelationStatus | str

    incident_date: date | str | None = None
    policy_breach: str | None = None
    incident_summary: str | None = None
    corrective_action: str | None = None
    employee_response: str | None = None
    hearing_date: date | str | None = None
    outcome: str | None = None

    source_artifact_id: str | None = None
    source_artifact_fingerprint: str | None = None

    schema: str = EMPLOYEE_RELATION_SCHEMA
    relation_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(
        self,
    ) -> None:

        tenant = _tenant(
            self.tenant_id
        )

        relation_id = _identity(
            "relation_id",
            self.relation_id,
        )

        employee_id = _identity(
            "employee_id",
            self.employee_id,
        )

        try:
            action = EmployeeRelationActionType(
                self.action_type
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            _fail(
                "P0_C12E1_EMPLOYEE_RELATION_ACTION_TYPE_INVALID",
                error,
            )

        try:
            status = EmployeeRelationStatus(
                self.status
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            _fail(
                "P0_C12E1_EMPLOYEE_RELATION_STATUS_INVALID",
                error,
            )

        incident_date = _date_value(
            "incident_date",
            self.incident_date,
        )

        policy_breach = _optional_text(
            "policy_breach",
            self.policy_breach,
        )

        incident_summary = _optional_text(
            "incident_summary",
            self.incident_summary,
        )

        corrective_action = _optional_text(
            "corrective_action",
            self.corrective_action,
        )

        employee_response = _optional_text(
            "employee_response",
            self.employee_response,
        )

        hearing_date = _date_value(
            "hearing_date",
            self.hearing_date,
        )

        outcome = _optional_text(
            "outcome",
            self.outcome,
        )

        if (
            status
            is not EmployeeRelationStatus.DRAFT
            and (
                incident_date is None
                or policy_breach is None
                or incident_summary is None
                or corrective_action is None
            )
        ):
            _fail(
                "P0_C12E1_EMPLOYEE_RELATION_EVIDENCE_REQUIRED"
            )

        source_artifact_id = (
            None
            if self.source_artifact_id is None
            else _identity(
                "source_artifact_id",
                self.source_artifact_id,
            )
        )

        source_artifact_fingerprint = (
            None
            if self.source_artifact_fingerprint is None
            else _fingerprint(
                "source_artifact_fingerprint",
                self.source_artifact_fingerprint,
            )
        )

        if (
            (
                source_artifact_id
                is None
            )
            != (
                source_artifact_fingerprint
                is None
            )
        ):
            _fail(
                "P0_C12E1_EMPLOYEE_RELATION_ARTIFACT_EVIDENCE_INCOMPLETE"
            )

        if (
            self.schema
            != EMPLOYEE_RELATION_SCHEMA
            or self.relation_version
            != VERSION
        ):
            _fail(
                "P0_C12E1_EMPLOYEE_RELATION_IDENTITY_INVALID"
            )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "relation_id",
            relation_id,
        )
        object.__setattr__(
            self,
            "employee_id",
            employee_id,
        )
        object.__setattr__(
            self,
            "action_type",
            action,
        )
        object.__setattr__(
            self,
            "status",
            status,
        )
        object.__setattr__(
            self,
            "incident_date",
            incident_date,
        )
        object.__setattr__(
            self,
            "policy_breach",
            policy_breach,
        )
        object.__setattr__(
            self,
            "incident_summary",
            incident_summary,
        )
        object.__setattr__(
            self,
            "corrective_action",
            corrective_action,
        )
        object.__setattr__(
            self,
            "employee_response",
            employee_response,
        )
        object.__setattr__(
            self,
            "hearing_date",
            hearing_date,
        )
        object.__setattr__(
            self,
            "outcome",
            outcome,
        )
        object.__setattr__(
            self,
            "source_artifact_id",
            source_artifact_id,
        )
        object.__setattr__(
            self,
            "source_artifact_fingerprint",
            source_artifact_fingerprint,
        )

        payload = {
            field: _json_value(
                getattr(
                    self,
                    field,
                )
            )
            for field
            in _EMPLOYEE_RELATION_FIELDS[:-1]
        }

        digest = hashlib.sha3_512(
            json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode(
                "utf-8"
            )
        ).hexdigest()

        if self.fingerprint:
            if (
                not isinstance(
                    self.fingerprint,
                    str,
                )
                or not hmac.compare_digest(
                    self.fingerprint,
                    digest,
                )
            ):
                _fail(
                    "P0_C12E1_EMPLOYEE_RELATION_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def to_dict(
        self,
    ) -> dict[str, object]:

        return {
            field: _json_value(
                getattr(
                    self,
                    field,
                )
            )
            for field
            in _EMPLOYEE_RELATION_FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[
            str,
            object,
        ],
    ) -> "EmployeeRelation":

        if (
            not isinstance(
                payload,
                Mapping,
            )
            or set(payload)
            != set(
                _EMPLOYEE_RELATION_FIELDS
            )
        ):
            _fail(
                "P0_C12E1_EMPLOYEE_RELATION_SCHEMA_INVALID"
            )

        values = dict(
            payload
        )

        stored = values.pop(
            "fingerprint"
        )

        result = cls(
            **cast(
                Any,
                values,
            )
        )

        if (
            not isinstance(
                stored,
                str,
            )
            or not hmac.compare_digest(
                stored,
                result.fingerprint,
            )
        ):
            _fail(
                "P0_C12E1_EMPLOYEE_RELATION_FINGERPRINT_MISMATCH"
            )

        return result


__all__ = [
    "EMPLOYEE_RELATION_FIELDS",
    "EMPLOYEE_RELATION_SCHEMA",
    "VERSION",
    "EmployeeRelation",
    "EmployeeRelationActionType",
    "EmployeeRelationError",
    "EmployeeRelationStatus",
]
