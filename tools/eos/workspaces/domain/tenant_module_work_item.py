"""WILSY OS tenant-module work item domain.

TITLE: Tenant Module Work Item
VERSION: v1.0.0-TENANT-MODULE-WORK-ITEM
AUTHORITY: Python EOS tenant-module operations.
PURPOSE:
    Model tenant-owned operational tasks, reminders and follow-ups without
    creating Legal practice, matter, client-confidentiality, IAM or financial
    execution authority. Business records remain owned by their respective
    module domains and are never inferred from a task description.
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

VERSION: Final[str] = "v1.0.0-TENANT-MODULE-WORK-ITEM"
SCHEMA: Final[str] = "WILSY-TENANT-MODULE-WORK-ITEM/V1"
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset({
    "MASTER", "GLOBAL_ROOT", "WILSY_ROOT", "WILSY_MASTER",
    "WILSY_GLOBAL_ROOT", "SOVEREIGN_ROOT",
})
_HEX = re.compile(r"^[0-9a-f]{128}$")


class ModuleWorkItemError(ValueError):
    """Stable fail-closed tenant-module work validation error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class ModuleWorkKind(StrEnum):
    TASK = "TASK"
    REMINDER = "REMINDER"
    FOLLOW_UP = "FOLLOW_UP"


class ModuleWorkStatus(StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ModuleWorkPriority(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


def _text(value: object, code: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value) or value != value.strip():
        raise ModuleWorkItemError(code)
    if any(ord(ch) < 32 for ch in value):
        raise ModuleWorkItemError(code)
    return value


def _time(value: object, code: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ModuleWorkItemError(code)
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class TenantModuleWorkItem:
    work_item_id: str
    tenant_id: str
    title: str
    description: str
    kind: ModuleWorkKind
    status: ModuleWorkStatus
    priority: ModuleWorkPriority
    created_by_principal_id: str
    due_at: datetime | None
    source_type: str | None
    source_id: str | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    completion_note: str | None = None

    def __post_init__(self) -> None:
        tenant = _text(self.tenant_id, "TENANT_ID_INVALID")
        if tenant.upper() in _FORBIDDEN_TENANTS:
            raise ModuleWorkItemError("TENANT_ID_INVALID")
        _text(self.work_item_id, "WORK_ITEM_ID_INVALID")
        _text(self.title, "TITLE_INVALID")
        _text(self.description, "DESCRIPTION_INVALID", allow_empty=True)
        _text(self.created_by_principal_id, "CREATED_BY_PRINCIPAL_ID_INVALID")
        if not isinstance(self.kind, ModuleWorkKind) or not isinstance(self.status, ModuleWorkStatus) or not isinstance(self.priority, ModuleWorkPriority):
            raise ModuleWorkItemError("CLASSIFICATION_INVALID")
        created = _time(self.created_at, "CREATED_AT_INVALID")
        updated = _time(self.updated_at, "UPDATED_AT_INVALID")
        if updated < created:
            raise ModuleWorkItemError("UPDATED_AT_INVALID")
        if self.due_at is not None:
            _time(self.due_at, "DUE_AT_INVALID")
        if self.completed_at is not None:
            completed = _time(self.completed_at, "COMPLETED_AT_INVALID")
            if self.status is not ModuleWorkStatus.COMPLETED or completed < created:
                raise ModuleWorkItemError("COMPLETION_EVIDENCE_INVALID")
        elif self.status is ModuleWorkStatus.COMPLETED:
            raise ModuleWorkItemError("COMPLETION_EVIDENCE_REQUIRED")
        if self.completion_note is not None:
            _text(self.completion_note, "COMPLETION_NOTE_INVALID")
        if (self.source_type is None) != (self.source_id is None):
            raise ModuleWorkItemError("SOURCE_COORDINATE_INVALID")
        if self.source_type is not None:
            _text(self.source_type, "SOURCE_TYPE_INVALID")
            _text(self.source_id, "SOURCE_ID_INVALID")

    @classmethod
    def create(
        cls, *, tenant_id: str, title: str, description: str = "",
        kind: ModuleWorkKind = ModuleWorkKind.TASK,
        priority: ModuleWorkPriority = ModuleWorkPriority.NORMAL,
        created_by_principal_id: str, due_at: datetime | None = None,
        source_type: str | None = None, source_id: str | None = None,
        now: datetime,
    ) -> "TenantModuleWorkItem":
        instant = _time(now, "CREATED_AT_INVALID")
        return cls(
            work_item_id="tmw_" + uuid4().hex,
            tenant_id=tenant_id, title=title, description=description,
            kind=kind, status=ModuleWorkStatus.OPEN, priority=priority,
            created_by_principal_id=created_by_principal_id, due_at=due_at,
            source_type=source_type, source_id=source_id,
            created_at=instant, updated_at=instant,
        )

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> "TenantModuleWorkItem":
        expected = {
            "schema", "work_item_id", "tenant_id", "title", "description",
            "kind", "status", "priority", "created_by_principal_id", "due_at",
            "source_type", "source_id", "created_at", "updated_at",
            "completed_at", "completion_note",
        }
        if not isinstance(value, dict) or set(value) != expected or value.get("schema") != SCHEMA:
            raise ModuleWorkItemError("DOCUMENT_INVALID")
        def parse(raw: object, code: str) -> datetime | None:
            if raw is None:
                return None
            if not isinstance(raw, str):
                raise ModuleWorkItemError(code)
            try:
                return _time(datetime.fromisoformat(raw), code)
            except ValueError as error:
                raise ModuleWorkItemError(code) from error
        try:
            return cls(
                work_item_id=value["work_item_id"], tenant_id=value["tenant_id"],
                title=value["title"], description=value["description"],
                kind=ModuleWorkKind(value["kind"]), status=ModuleWorkStatus(value["status"]),
                priority=ModuleWorkPriority(value["priority"]),
                created_by_principal_id=value["created_by_principal_id"],
                due_at=parse(value["due_at"], "DUE_AT_INVALID"),
                source_type=value["source_type"], source_id=value["source_id"],
                created_at=parse(value["created_at"], "CREATED_AT_INVALID"),
                updated_at=parse(value["updated_at"], "UPDATED_AT_INVALID"),
                completed_at=parse(value["completed_at"], "COMPLETED_AT_INVALID"),
                completion_note=value["completion_note"],
            )
        except (TypeError, ValueError) as error:
            if isinstance(error, ModuleWorkItemError):
                raise
            raise ModuleWorkItemError("DOCUMENT_INVALID") from error

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": SCHEMA, "work_item_id": self.work_item_id,
            "tenant_id": self.tenant_id, "title": self.title,
            "description": self.description, "kind": self.kind.value,
            "status": self.status.value, "priority": self.priority.value,
            "created_by_principal_id": self.created_by_principal_id,
            "due_at": self.due_at.isoformat() if self.due_at else None,
            "source_type": self.source_type, "source_id": self.source_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "completion_note": self.completion_note,
        }


def command_fingerprint(item: TenantModuleWorkItem, idempotency_key: str) -> str:
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
    items: tuple[TenantModuleWorkItem, ...] | list[TenantModuleWorkItem],
    *, tenant_id: str, now: datetime,
) -> tuple[dict[str, object], ...]:
    """Return deterministic own-tenant actionable queue; no inferred legal dates."""
    tenant = _text(tenant_id, "TENANT_ID_INVALID")
    instant = _time(now, "NOW_INVALID")
    active = []
    for item in items:
        if not isinstance(item, TenantModuleWorkItem):
            raise ModuleWorkItemError("WORK_ITEM_INVALID")
        if item.tenant_id != tenant:
            continue
        if item.status in (ModuleWorkStatus.COMPLETED, ModuleWorkStatus.CANCELLED):
            continue
        due = item.due_at
        overdue = due is not None and due < instant
        due_today = due is not None and due.date() == instant.date()
        priority_rank = {
            ModuleWorkPriority.CRITICAL: 0, ModuleWorkPriority.HIGH: 1,
            ModuleWorkPriority.NORMAL: 2, ModuleWorkPriority.LOW: 3,
        }[item.priority]
        active.append(((
            0 if overdue else 1 if due_today else 2 if due is not None else 3,
            priority_rank, due or datetime.max.replace(tzinfo=timezone.utc),
            item.created_at, item.work_item_id,
        ), item, overdue, due_today))
    active.sort(key=lambda row: row[0])
    return tuple({
        **item.to_dict(), "is_overdue": overdue, "is_due_today": due_today,
        "queue_position": index,
    } for index, (_, item, overdue, due_today) in enumerate(active, start=1))


__all__ = [
    "SCHEMA", "VERSION", "TenantModuleWorkItem", "ModuleWorkItemError",
    "ModuleWorkKind", "ModuleWorkPriority", "ModuleWorkStatus",
    "build_daily_queue", "command_fingerprint",
]
