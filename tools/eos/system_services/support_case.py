"""Immutable WILSY OS System Services support-case domain.

This domain owns case identity, scope, category and legal state transitions only.
It accepts opaque references and never accepts credentials or recovery secrets.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Final

VERSION: Final[str] = "v1.0.0-SYSTEM-SERVICES-CASE-DOMAIN"
SCHEMA: Final[str] = "WILSY-SYSTEM-SERVICES-CASE/V1"
_IDENTIFIER = re.compile(r"^[^\s\x00-\x1f\x7f]{1,256}$")


class SupportCaseError(ValueError):
    """Stable fail-closed domain validation or transition error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class SupportCaseScope(StrEnum):
    SYSTEM = "SYSTEM"
    TENANT = "TENANT"


class SupportCaseCategory(StrEnum):
    ACCOUNT_ACCESS = "ACCOUNT_ACCESS"
    PASSWORD_RECOVERY = "PASSWORD_RECOVERY"
    MFA_RECOVERY = "MFA_RECOVERY"
    RECOVERY_CONTACT = "RECOVERY_CONTACT"
    SESSION_OR_DEVICE = "SESSION_OR_DEVICE"
    SUSPECTED_COMPROMISE = "SUSPECTED_COMPROMISE"
    ACCESS_REQUEST = "ACCESS_REQUEST"
    OTHER = "OTHER"


class SupportCaseStatus(StrEnum):
    OPEN = "OPEN"
    TRIAGED = "TRIAGED"
    IDENTITY_VERIFIED = "IDENTITY_VERIFIED"
    ACTION_PENDING_APPROVAL = "ACTION_PENDING_APPROVAL"
    ACTION_EXECUTED = "ACTION_EXECUTED"
    USER_CONFIRMATION_PENDING = "USER_CONFIRMATION_PENDING"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    ESCALATED_SECURITY_INCIDENT = "ESCALATED_SECURITY_INCIDENT"
    EXPIRED = "EXPIRED"


TERMINAL_STATUSES: Final = frozenset({
    SupportCaseStatus.RESOLVED,
    SupportCaseStatus.REJECTED,
    SupportCaseStatus.CANCELLED,
    SupportCaseStatus.ESCALATED_SECURITY_INCIDENT,
    SupportCaseStatus.EXPIRED,
})

_ALLOWED_TRANSITIONS: Final = {
    SupportCaseStatus.OPEN: frozenset({
        SupportCaseStatus.TRIAGED,
        SupportCaseStatus.CANCELLED,
        SupportCaseStatus.EXPIRED,
    }),
    SupportCaseStatus.TRIAGED: frozenset({
        SupportCaseStatus.IDENTITY_VERIFIED,
        SupportCaseStatus.ESCALATED_SECURITY_INCIDENT,
        SupportCaseStatus.REJECTED,
        SupportCaseStatus.CANCELLED,
        SupportCaseStatus.EXPIRED,
    }),
    SupportCaseStatus.IDENTITY_VERIFIED: frozenset({
        SupportCaseStatus.ACTION_PENDING_APPROVAL,
        SupportCaseStatus.ACTION_EXECUTED,
        SupportCaseStatus.ESCALATED_SECURITY_INCIDENT,
        SupportCaseStatus.REJECTED,
        SupportCaseStatus.EXPIRED,
    }),
    SupportCaseStatus.ACTION_PENDING_APPROVAL: frozenset({
        SupportCaseStatus.ACTION_EXECUTED,
        SupportCaseStatus.ESCALATED_SECURITY_INCIDENT,
        SupportCaseStatus.REJECTED,
        SupportCaseStatus.EXPIRED,
    }),
    SupportCaseStatus.ACTION_EXECUTED: frozenset({
        SupportCaseStatus.USER_CONFIRMATION_PENDING,
        SupportCaseStatus.RESOLVED,
        SupportCaseStatus.ESCALATED_SECURITY_INCIDENT,
    }),
    SupportCaseStatus.USER_CONFIRMATION_PENDING: frozenset({
        SupportCaseStatus.RESOLVED,
        SupportCaseStatus.ESCALATED_SECURITY_INCIDENT,
        SupportCaseStatus.EXPIRED,
    }),
}


def _identifier(value: object, code: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        raise SupportCaseError(code)
    return value


def _utc(value: object, code: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise SupportCaseError(code)
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class SupportCase:
    case_id: str
    scope: SupportCaseScope
    principal_id: str
    category: SupportCaseCategory
    created_at: datetime
    updated_at: datetime
    status: SupportCaseStatus = SupportCaseStatus.OPEN
    tenant_id: str | None = None
    revision: int = 0

    def __post_init__(self) -> None:
        _identifier(self.case_id, "CASE_ID_INVALID")
        _identifier(self.principal_id, "PRINCIPAL_ID_INVALID")
        if not isinstance(self.scope, SupportCaseScope):
            raise SupportCaseError("CASE_SCOPE_INVALID")
        if not isinstance(self.category, SupportCaseCategory):
            raise SupportCaseError("CASE_CATEGORY_INVALID")
        if not isinstance(self.status, SupportCaseStatus):
            raise SupportCaseError("CASE_STATUS_INVALID")
        if self.scope is SupportCaseScope.SYSTEM and self.tenant_id is not None:
            raise SupportCaseError("SYSTEM_CASE_MUST_NOT_BIND_TENANT")
        if self.scope is SupportCaseScope.TENANT:
            _identifier(self.tenant_id, "TENANT_ID_REQUIRED")
        created = _utc(self.created_at, "CASE_CREATED_AT_INVALID")
        updated = _utc(self.updated_at, "CASE_UPDATED_AT_INVALID")
        if updated < created:
            raise SupportCaseError("CASE_TIME_ORDER_INVALID")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 0:
            raise SupportCaseError("CASE_REVISION_INVALID")
        object.__setattr__(self, "created_at", created)
        object.__setattr__(self, "updated_at", updated)

    def transition(self, status: SupportCaseStatus, *, observed_at: datetime) -> "SupportCase":
        """Return the next immutable case state; callers must persist via CAS."""
        if not isinstance(status, SupportCaseStatus):
            raise SupportCaseError("CASE_STATUS_INVALID")
        allowed = _ALLOWED_TRANSITIONS.get(self.status, frozenset())
        if status not in allowed:
            raise SupportCaseError("CASE_TRANSITION_NOT_ALLOWED")
        observed = _utc(observed_at, "CASE_TRANSITION_TIME_INVALID")
        if observed < self.updated_at:
            raise SupportCaseError("CASE_TRANSITION_TIME_REGRESSION")
        return replace(self, status=status, updated_at=observed, revision=self.revision + 1)

    def to_document(self) -> dict[str, object]:
        return {
            "schema": SCHEMA,
            "case_id": self.case_id,
            "scope": self.scope.value,
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "category": self.category.value,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "revision": self.revision,
        }

    @classmethod
    def from_document(cls, value: dict[str, object]) -> "SupportCase":
        if value.get("schema") != SCHEMA:
            raise SupportCaseError("CASE_SCHEMA_INVALID")
        expected_fields = {
            "schema", "case_id", "scope", "tenant_id", "principal_id",
            "category", "status", "created_at", "updated_at", "revision",
        }
        if set(value) != expected_fields:
            raise SupportCaseError("CASE_PERSISTED_FIELDS_INVALID")
        try:
            return cls(
                case_id=value["case_id"],  # type: ignore[arg-type]
                scope=SupportCaseScope(value["scope"]),  # type: ignore[arg-type]
                tenant_id=value.get("tenant_id"),  # type: ignore[arg-type]
                principal_id=value["principal_id"],  # type: ignore[arg-type]
                category=SupportCaseCategory(value["category"]),  # type: ignore[arg-type]
                status=SupportCaseStatus(value["status"]),  # type: ignore[arg-type]
                created_at=value["created_at"],  # type: ignore[arg-type]
                updated_at=value["updated_at"],  # type: ignore[arg-type]
                revision=value["revision"],  # type: ignore[arg-type]
            )
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, SupportCaseError):
                raise
            raise SupportCaseError("CASE_PERSISTED_STATE_INVALID") from error


@dataclass(frozen=True, slots=True)
class SupportCaseEvent:
    event_id: str
    case_id: str
    actor_principal_id: str
    idempotency_key: str
    from_status: SupportCaseStatus | None
    to_status: SupportCaseStatus
    action: str
    occurred_at: datetime
    evidence_reference: str | None = None

    def __post_init__(self) -> None:
        for value, code in (
            (self.event_id, "CASE_EVENT_ID_INVALID"),
            (self.case_id, "CASE_EVENT_CASE_ID_INVALID"),
            (self.actor_principal_id, "CASE_EVENT_ACTOR_INVALID"),
            (self.idempotency_key, "CASE_EVENT_IDEMPOTENCY_INVALID"),
            (self.action, "CASE_EVENT_ACTION_INVALID"),
        ):
            _identifier(value, code)
        if self.evidence_reference is not None:
            _identifier(self.evidence_reference, "CASE_EVENT_EVIDENCE_REFERENCE_INVALID")
        if not isinstance(self.to_status, SupportCaseStatus):
            raise SupportCaseError("CASE_EVENT_STATUS_INVALID")
        if self.from_status is not None and not isinstance(self.from_status, SupportCaseStatus):
            raise SupportCaseError("CASE_EVENT_FROM_STATUS_INVALID")
        object.__setattr__(self, "occurred_at", _utc(self.occurred_at, "CASE_EVENT_TIME_INVALID"))

    def to_document(self) -> dict[str, object]:
        return {
            "schema": SCHEMA,
            "event_id": self.event_id,
            "case_id": self.case_id,
            "actor_principal_id": self.actor_principal_id,
            "idempotency_key": self.idempotency_key,
            "from_status": self.from_status.value if self.from_status else None,
            "to_status": self.to_status.value,
            "action": self.action,
            "occurred_at": self.occurred_at,
            "evidence_reference": self.evidence_reference,
        }

    @classmethod
    def from_document(cls, value: dict[str, object]) -> "SupportCaseEvent":
        expected_fields = {
            "schema", "event_id", "case_id", "actor_principal_id",
            "idempotency_key", "from_status", "to_status", "action",
            "occurred_at", "evidence_reference",
        }
        if value.get("schema") != SCHEMA:
            raise SupportCaseError("CASE_EVENT_SCHEMA_INVALID")
        if set(value) != expected_fields:
            raise SupportCaseError("CASE_EVENT_PERSISTED_FIELDS_INVALID")
        try:
            before = value.get("from_status")
            return cls(
                event_id=value["event_id"],  # type: ignore[arg-type]
                case_id=value["case_id"],  # type: ignore[arg-type]
                actor_principal_id=value["actor_principal_id"],  # type: ignore[arg-type]
                idempotency_key=value["idempotency_key"],  # type: ignore[arg-type]
                from_status=SupportCaseStatus(before) if before is not None else None,
                to_status=SupportCaseStatus(value["to_status"]),  # type: ignore[arg-type]
                action=value["action"],  # type: ignore[arg-type]
                occurred_at=value["occurred_at"],  # type: ignore[arg-type]
                evidence_reference=value.get("evidence_reference"),  # type: ignore[arg-type]
            )
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, SupportCaseError):
                raise
            raise SupportCaseError("CASE_EVENT_PERSISTED_STATE_INVALID") from error


__all__ = [
    "VERSION", "SCHEMA", "SupportCaseError", "SupportCaseScope",
    "SupportCaseCategory", "SupportCaseStatus", "TERMINAL_STATUSES",
    "SupportCase", "SupportCaseEvent",
]
