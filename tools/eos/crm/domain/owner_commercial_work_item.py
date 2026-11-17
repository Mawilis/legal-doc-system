"""TITLE: WILSY OS Owner Commercial Work Item Domain.
VERSION: v1.2.0-DRAFT-AND-PROGRESS-LIFECYCLE
AUTHORITY: Python EOS CRM owner-commercial domain.
EPITOME: Defines immutable, tenant-owned CRM task evidence, deterministic
         queue projection, canonical serialization, and retry fingerprints.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/crm/domain/owner_commercial_work_item.py
COLLABORATION / OWNERSHIP: OwnerCommercialWorkspaceService and OwnerCommercialWorkRegistry.
CERTIFICATION / UPDATE DATE: 2026-11-17
CHANGELOG: v1.2.0-DRAFT-AND-PROGRESS-LIFECYCLE adds a canonical
           persisted DRAFT state excluded from active attention, while
           IN_PROGRESS remains a source-backed active work state.
CHANGELOG: v1.1.0-STRICT-TYPED-READBACK narrows every persisted field before
           domain construction and separates optional from required timestamps;
           serialized contract and authorization behavior are unchanged.
           v1.0.0-OWNER-COMMERCIAL-WORK-ITEM establishes tenant-bound owner tasks.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No logging, secret handling, external I/O, or inferred record content.
TENANT BOUNDARY: Work records and queue results are exact-tenant scoped; global-root tenants are rejected.
AUTHORITY BOUNDARY: Domain validation only; CRM IAM, entitlement, and source commands remain independent.
TRANSACTION BOUNDARY: Pure immutable values; registries and callers own Mongo sessions and transactions.
FINANCIAL AUTHORITY BOUNDARY: Work records do not authorize approval, execution, payment, or settlement.
FAIL-CLOSED POSTURE: Malformed schema, type, tenant, enum, timestamp, or completion evidence is rejected.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import json
import re
from typing import Final
from uuid import uuid4

VERSION: Final[str] = "v1.1.0-STRICT-TYPED-READBACK"
SCHEMA: Final[str] = "WILSY-OWNER-COMMERCIAL-WORK-ITEM/V1"
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset({
    "MASTER", "GLOBAL_ROOT", "WILSY_ROOT", "WILSY_MASTER",
    "WILSY_GLOBAL_ROOT", "SOVEREIGN_ROOT",
})
_HEX = re.compile(r"^[0-9a-f]{128}$")


class OwnerWorkItemError(ValueError):
    """Stable fail-closed validation error for source-owned owner work."""

    def __init__(self, code: str) -> None:
        """Create an error carrying a non-sensitive stable code."""
        self.code = code
        super().__init__(code)


class OwnerWorkKind(StrEnum):
    """Supported owner-commercial work categories; no Legal matter authority."""

    TASK = "TASK"
    REMINDER = "REMINDER"
    FOLLOW_UP = "FOLLOW_UP"


class OwnerWorkStatus(StrEnum):
    """Source-owned work lifecycle; terminal status requires source evidence."""

    DRAFT = "DRAFT"
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class OwnerWorkPriority(StrEnum):
    """Canonical source priority ordering for the owner queue."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


def _text(value: object, code: str, *, allow_empty: bool = False) -> str:
    """Validate one canonical bounded text field without coercion."""
    if not isinstance(value, str) or (not allow_empty and not value) or value != value.strip():
        raise OwnerWorkItemError(code)
    if any(ord(ch) < 32 for ch in value):
        raise OwnerWorkItemError(code)
    return value


def _time(value: object, code: str) -> datetime:
    """Require an aware timestamp and normalize it to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise OwnerWorkItemError(code)
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class OwnerCommercialWorkItem:
    """Immutable exact-tenant owner task evidence.

    Construction validates the domain record only. CRM authorization, active
    product entitlement, persistence, idempotency transactions, and mutation
    authority remain owned by their existing EOS services and registries.
    """

    work_item_id: str
    tenant_id: str
    title: str
    description: str
    kind: OwnerWorkKind
    status: OwnerWorkStatus
    priority: OwnerWorkPriority
    owner_principal_id: str
    due_at: datetime | None
    source_type: str | None
    source_id: str | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    completion_note: str | None = None

    def __post_init__(self) -> None:
        """Enforce immutable field, tenant, time, and completion invariants."""
        tenant = _text(self.tenant_id, "TENANT_ID_INVALID")
        if tenant.upper() in _FORBIDDEN_TENANTS:
            raise OwnerWorkItemError("TENANT_ID_INVALID")
        _text(self.work_item_id, "WORK_ITEM_ID_INVALID")
        _text(self.title, "TITLE_INVALID")
        _text(self.description, "DESCRIPTION_INVALID", allow_empty=True)
        _text(self.owner_principal_id, "OWNER_PRINCIPAL_ID_INVALID")
        if not isinstance(self.kind, OwnerWorkKind) or not isinstance(self.status, OwnerWorkStatus) or not isinstance(self.priority, OwnerWorkPriority):
            raise OwnerWorkItemError("CLASSIFICATION_INVALID")
        created = _time(self.created_at, "CREATED_AT_INVALID")
        updated = _time(self.updated_at, "UPDATED_AT_INVALID")
        if updated < created:
            raise OwnerWorkItemError("UPDATED_AT_INVALID")
        if self.due_at is not None:
            _time(self.due_at, "DUE_AT_INVALID")
        if self.completed_at is not None:
            completed = _time(self.completed_at, "COMPLETED_AT_INVALID")
            if self.status is not OwnerWorkStatus.COMPLETED or completed < created:
                raise OwnerWorkItemError("COMPLETION_EVIDENCE_INVALID")
        elif self.status is OwnerWorkStatus.COMPLETED:
            raise OwnerWorkItemError("COMPLETION_EVIDENCE_REQUIRED")
        if self.completion_note is not None:
            _text(self.completion_note, "COMPLETION_NOTE_INVALID")
        if (self.source_type is None) != (self.source_id is None):
            raise OwnerWorkItemError("SOURCE_COORDINATE_INVALID")
        if self.source_type is not None:
            _text(self.source_type, "SOURCE_TYPE_INVALID")
            _text(self.source_id, "SOURCE_ID_INVALID")

    @classmethod
    def create(
        cls, *, tenant_id: str, title: str, description: str = "",
        kind: OwnerWorkKind = OwnerWorkKind.TASK,
        priority: OwnerWorkPriority = OwnerWorkPriority.NORMAL,
        owner_principal_id: str, due_at: datetime | None = None,
        source_type: str | None = None, source_id: str | None = None,
        now: datetime,
    ) -> "OwnerCommercialWorkItem":
        """Create a new open item; caller owns authorization and persistence.

        Tenant scope is preserved exactly. The generated item identity and times
        are server-owned; the caller's transaction/session belongs to the registry.
        """
        instant = _time(now, "CREATED_AT_INVALID")
        return cls(
            work_item_id="owk_" + uuid4().hex,
            tenant_id=tenant_id, title=title, description=description,
            kind=kind, status=OwnerWorkStatus.OPEN, priority=priority,
            owner_principal_id=owner_principal_id, due_at=due_at,
            source_type=source_type, source_id=source_id,
            created_at=instant, updated_at=instant,
        )

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> "OwnerCommercialWorkItem":
        """Hydrate one exact persisted schema without coercing field types.

        This is a read-only parser. It grants no command authority and leaves
        exact-tenant query scope and caller-owned Mongo session handling to the
        persistence registry.
        """
        expected = {
            "schema", "work_item_id", "tenant_id", "title", "description",
            "kind", "status", "priority", "owner_principal_id", "due_at",
            "source_type", "source_id", "created_at", "updated_at",
            "completed_at", "completion_note",
        }
        if not isinstance(value, dict) or set(value) != expected or value.get("schema") != SCHEMA:
            raise OwnerWorkItemError("DOCUMENT_INVALID")

        def parse_optional_time(raw: object, code: str) -> datetime | None:
            if raw is None:
                return None
            if not isinstance(raw, str):
                raise OwnerWorkItemError(code)
            try:
                return _time(datetime.fromisoformat(raw), code)
            except ValueError as error:
                raise OwnerWorkItemError(code) from error

        def parse_required_time(raw: object, code: str) -> datetime:
            parsed = parse_optional_time(raw, code)
            if parsed is None:
                raise OwnerWorkItemError(code)
            return parsed

        try:
            kind_value = value["kind"]
            status_value = value["status"]
            priority_value = value["priority"]
            if not all(isinstance(item, str) for item in (kind_value, status_value, priority_value)):
                raise TypeError("classification field is not text")
            source_type_value = value["source_type"]
            source_id_value = value["source_id"]
            completion_note_value = value["completion_note"]
            if source_type_value is not None:
                source_type_value = _text(source_type_value, "SOURCE_TYPE_INVALID")
            if source_id_value is not None:
                source_id_value = _text(source_id_value, "SOURCE_ID_INVALID")
            if completion_note_value is not None:
                completion_note_value = _text(completion_note_value, "COMPLETION_NOTE_INVALID")
            return cls(
                work_item_id=_text(value["work_item_id"], "WORK_ITEM_ID_INVALID"),
                tenant_id=_text(value["tenant_id"], "TENANT_ID_INVALID"),
                title=_text(value["title"], "TITLE_INVALID"),
                description=_text(value["description"], "DESCRIPTION_INVALID", allow_empty=True),
                kind=OwnerWorkKind(kind_value),
                status=OwnerWorkStatus(status_value),
                priority=OwnerWorkPriority(priority_value),
                owner_principal_id=_text(value["owner_principal_id"], "OWNER_PRINCIPAL_ID_INVALID"),
                due_at=parse_optional_time(value["due_at"], "DUE_AT_INVALID"),
                source_type=source_type_value,
                source_id=source_id_value,
                created_at=parse_required_time(value["created_at"], "CREATED_AT_INVALID"),
                updated_at=parse_required_time(value["updated_at"], "UPDATED_AT_INVALID"),
                completed_at=parse_optional_time(value["completed_at"], "COMPLETED_AT_INVALID"),
                completion_note=completion_note_value,
            )
        except (TypeError, ValueError) as error:
            if isinstance(error, OwnerWorkItemError):
                raise
            raise OwnerWorkItemError("DOCUMENT_INVALID") from error

    def to_dict(self) -> dict[str, object]:
        """Serialize canonical fields without adding transport or authority data."""
        return {
            "schema": SCHEMA, "work_item_id": self.work_item_id,
            "tenant_id": self.tenant_id, "title": self.title,
            "description": self.description, "kind": self.kind.value,
            "status": self.status.value, "priority": self.priority.value,
            "owner_principal_id": self.owner_principal_id,
            "due_at": self.due_at.isoformat() if self.due_at else None,
            "source_type": self.source_type, "source_id": self.source_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "completion_note": self.completion_note,
        }


def command_fingerprint(item: OwnerCommercialWorkItem, idempotency_key: str) -> str:
    """Fingerprint caller-controlled command fields using canonical SHA3-512.

    Identity and timestamps are excluded because EOS creates them. Tenant and
    idempotency key are included; no transaction or execution authority is granted.
    """
    key = _text(idempotency_key, "IDEMPOTENCY_KEY_INVALID")
    command = item.to_dict()
    # Server-generated identity and timestamps must not make a client retry
    # divergent. All caller-controlled business fields remain fingerprinted.
    for generated in ("work_item_id", "created_at", "updated_at"):
        command.pop(generated, None)
    material = {"tenant_id": item.tenant_id, "idempotency_key": key, "item": command}
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return sha3_512(encoded).hexdigest()


def build_daily_queue(
    items: tuple[OwnerCommercialWorkItem, ...] | list[OwnerCommercialWorkItem],
    *, tenant_id: str, now: datetime,
) -> tuple[dict[str, object], ...]:
    """Return deterministic active own-tenant work, without inferred legal dates.

    The result is a source-backed projection. It performs no persistence,
    authorization, status mutation, or financial/legal workflow transition.
    """
    tenant = _text(tenant_id, "TENANT_ID_INVALID")
    instant = _time(now, "NOW_INVALID")
    active = []
    for item in items:
        if not isinstance(item, OwnerCommercialWorkItem):
            raise OwnerWorkItemError("WORK_ITEM_INVALID")
        if item.tenant_id != tenant:
            continue
        if item.status in (OwnerWorkStatus.DRAFT, OwnerWorkStatus.COMPLETED, OwnerWorkStatus.CANCELLED):
            continue
        due = item.due_at
        overdue = due is not None and due < instant
        due_today = due is not None and due.date() == instant.date()
        priority_rank = {
            OwnerWorkPriority.CRITICAL: 0, OwnerWorkPriority.HIGH: 1,
            OwnerWorkPriority.NORMAL: 2, OwnerWorkPriority.LOW: 3,
        }[item.priority]
        active.append((
            (
                0 if overdue else 1 if due_today else 2 if due is not None else 3,
                priority_rank, due or datetime.max.replace(tzinfo=timezone.utc),
                item.created_at, item.work_item_id,
            ), item, overdue, due_today,
        ))
    active.sort(key=lambda row: row[0])
    return tuple({
        **item.to_dict(), "is_overdue": overdue, "is_due_today": due_today,
        "queue_position": index,
    } for index, (_, item, overdue, due_today) in enumerate(active, start=1))


__all__ = [
    "SCHEMA", "VERSION", "OwnerCommercialWorkItem", "OwnerWorkItemError",
    "OwnerWorkKind", "OwnerWorkPriority", "OwnerWorkStatus",
    "build_daily_queue", "command_fingerprint",
]

# ARTIFACT: tools/eos/crm/domain/owner_commercial_work_item.py
# VERSION: v1.2.0-DRAFT-AND-PROGRESS-LIFECYCLE
# AUTHORITY BOUNDARY: Domain validation and projection only; CRM services authorize commands.
# TENANT POSTURE: Exact tenant retained; global-root tenant values are rejected.
# FAIL-CLOSED POSTURE: Malformed persistence documents and invalid transitions reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; this artifact cannot execute funds.
# END OF WILSY OS SOVEREIGN ARTIFACT
