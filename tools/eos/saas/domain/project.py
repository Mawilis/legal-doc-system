"""TITLE: WILSY OS Tenant Project Domain
VERSION: v1.0.1-TENANT-PROJECT-DOMAIN
AUTHORITY: Python EOS canonical project facts and lifecycle invariants.
EPITOME: Defines one immutable, validated tenant project aggregate with
         deterministic serialization and permitted status transitions; it
         performs no persistence, authorization, assignment, or transport.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/project.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering; consumed by the tenant-scoped
                           EOS project registry and router.
CERTIFICATION / UPDATE DATE: 2026-11-16.
CHANGELOG:
  v1.0.1-TENANT-PROJECT-DOMAIN — Corrects strict type narrowing and persisted
  schema hydration for Pyright; enforces monotonic update/archive timestamps.
  v1.0.0-TENANT-PROJECT-DOMAIN — Establishes canonical internal project facts,
  strict persisted schema, UTC timestamps, SHA3-512 state fingerprint, revision
  counter, soft archive marker, and closed project-status transitions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Rejects unknown persisted fields, malformed scope,
                            invalid state and naive timestamps. Fingerprints
                            are integrity checks, not signatures or anonymity.
TENANT BOUNDARY: Every aggregate has one explicit canonical tenant_id; this
                 model never resolves or defaults tenant authority.
AUTHORITY BOUNDARY: Domain validation only. EOS IAM and the owning registry
                    must independently authorize every read and command.
FINANCIAL AUTHORITY BOUNDARY: Project status and summary do not authorize
                              spending, approval, payment, execution or settlement.

Tenant ownership, caller identity, membership and business capacity must be
established by EOS before constructing or reading an aggregate. Owner and
department references are opaque identifiers here; a registry or route must
validate them against current tenant-scoped source authority before assignment.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Final, Mapping, cast


VERSION: Final[str] = "v1.0.1-TENANT-PROJECT-DOMAIN"
SCHEMA: Final[str] = "wilsy.project.v1"
_HEX_512: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_UPDATE_FIELDS: Final[frozenset[str]] = frozenset({
    "name", "code", "summary", "owner_principal_id", "department_id",
    "start_date", "target_date",
})


class ProjectError(ValueError):
    """Stable project-domain validation or transition failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class ProjectStatus(StrEnum):
    """Canonical project lifecycle states; these are not financial facts."""

    PLANNED = "planned"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    DONE = "done"
    CANCELLED = "cancelled"


class ProjectSourceType(StrEnum):
    """Closed project origin vocabulary for internal v0 projects."""

    INTERNAL = "internal"
    CERTIFIED_EXTERNAL = "certified_external"


_ALLOWED_TRANSITIONS: Final[dict[ProjectStatus, frozenset[ProjectStatus]]] = {
    ProjectStatus.PLANNED: frozenset({ProjectStatus.ACTIVE, ProjectStatus.ON_HOLD, ProjectStatus.CANCELLED}),
    ProjectStatus.ACTIVE: frozenset({ProjectStatus.ON_HOLD, ProjectStatus.DONE, ProjectStatus.CANCELLED}),
    ProjectStatus.ON_HOLD: frozenset({ProjectStatus.PLANNED, ProjectStatus.ACTIVE, ProjectStatus.CANCELLED}),
    ProjectStatus.DONE: frozenset(),
    ProjectStatus.CANCELLED: frozenset(),
}


def _required_text(name: str, value: object, *, maximum: int = 180) -> str:
    """Validate one exact, bounded, non-empty identifier or display field."""
    if (not isinstance(value, str) or not value or value != value.strip()
            or len(value) > maximum or any(ord(character) < 32 for character in value)):
        raise ProjectError(f"PROJECT_{name.upper()}_INVALID")
    return value


def _optional_text(name: str, value: object, *, maximum: int) -> str | None:
    """Validate nullable bounded project text without normalizing stored truth."""
    if value is None:
        return None
    if (not isinstance(value, str) or value != value.strip() or len(value) > maximum
            or any(ord(character) < 32 and character not in "\n\t" for character in value)):
        raise ProjectError(f"PROJECT_{name.upper()}_INVALID")
    return value or None


def _timestamp(name: str, value: object, *, optional: bool = False) -> datetime | None:
    """Require timezone-aware timestamps and canonicalize them to UTC."""
    if value is None and optional:
        return None
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ProjectError(f"PROJECT_{name.upper()}_TIMESTAMP_INVALID")
    return value.astimezone(timezone.utc)


def _parse_timestamp(name: str, value: object, *, optional: bool = False) -> datetime | None:
    """Parse persisted ISO timestamps without accepting naive local time."""
    if value is None and optional:
        return None
    if isinstance(value, datetime):
        return _timestamp(name, value, optional=optional)
    if isinstance(value, str):
        try:
            return _timestamp(name, datetime.fromisoformat(value), optional=optional)
        except (TypeError, ValueError) as error:
            raise ProjectError(f"PROJECT_{name.upper()}_TIMESTAMP_INVALID") from error
    raise ProjectError(f"PROJECT_{name.upper()}_TIMESTAMP_INVALID")


def _date_value(name: str, value: object) -> date | None:
    """Validate date-only project schedule fields and reject timestamp ambiguity."""
    if value is None:
        return None
    if isinstance(value, datetime) or not isinstance(value, date):
        raise ProjectError(f"PROJECT_{name.upper()}_DATE_INVALID")
    return value


@dataclass(frozen=True, slots=True)
class Project:
    """Immutable canonical project state owned by exactly one tenant.

    Mutators return a new revision and never persist it. The caller must use a
    tenant-scoped registry transaction with current authorization, idempotency,
    assignment validation, and audit evidence. Owner and department identifiers
    must be verified against authoritative tenant records before construction.
    """

    project_id: str
    tenant_id: str
    name: str
    code: str | None
    summary: str | None
    status: ProjectStatus | str
    owner_principal_id: str | None
    department_id: str | None
    start_date: date | None
    target_date: date | None
    source_type: ProjectSourceType | str
    external_source_reference: str | None
    created_by_principal_id: str
    created_at: datetime
    updated_by_principal_id: str
    updated_at: datetime
    archived_at: datetime | None = None
    revision: int = 1
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        for field_name in ("project_id", "tenant_id", "created_by_principal_id", "updated_by_principal_id"):
            object.__setattr__(self, field_name, _required_text(field_name, getattr(self, field_name)))
        object.__setattr__(self, "name", _required_text("name", self.name))
        object.__setattr__(self, "code", _optional_text("code", self.code, maximum=80))
        object.__setattr__(self, "summary", _optional_text("summary", self.summary, maximum=5000))
        object.__setattr__(self, "owner_principal_id", _optional_text("owner_principal_id", self.owner_principal_id, maximum=180))
        object.__setattr__(self, "department_id", _optional_text("department_id", self.department_id, maximum=180))
        object.__setattr__(self, "external_source_reference", _optional_text("external_source_reference", self.external_source_reference, maximum=512))
        try:
            status = ProjectStatus(self.status)
            source_type = ProjectSourceType(self.source_type)
        except (TypeError, ValueError) as error:
            raise ProjectError("PROJECT_ENUM_VALUE_INVALID") from error
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "source_type", source_type)
        if source_type is ProjectSourceType.CERTIFIED_EXTERNAL and self.external_source_reference is None:
            raise ProjectError("PROJECT_EXTERNAL_REFERENCE_REQUIRED")
        if source_type is ProjectSourceType.INTERNAL and self.external_source_reference is not None:
            raise ProjectError("PROJECT_EXTERNAL_REFERENCE_FORBIDDEN")
        start_date = _date_value("start", self.start_date)
        target_date = _date_value("target", self.target_date)
        if start_date is not None and target_date is not None and target_date < start_date:
            raise ProjectError("PROJECT_TARGET_BEFORE_START")
        object.__setattr__(self, "start_date", start_date)
        object.__setattr__(self, "target_date", target_date)
        created_at = _timestamp("created_at", self.created_at)
        updated_at = _timestamp("updated_at", self.updated_at)
        archived_at = _timestamp("archived_at", self.archived_at, optional=True)
        assert created_at is not None and updated_at is not None
        if updated_at < created_at or (archived_at is not None and archived_at < updated_at):
            raise ProjectError("PROJECT_TIMESTAMP_ORDER_INVALID")
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "updated_at", updated_at)
        object.__setattr__(self, "archived_at", archived_at)
        if type(self.revision) is not int or self.revision < 1:
            raise ProjectError("PROJECT_REVISION_INVALID")
        if self.schema != SCHEMA or self.version != VERSION:
            raise ProjectError("PROJECT_SCHEMA_VERSION_INVALID")
        digest = self._digest()
        if self.fingerprint and (not isinstance(self.fingerprint, str)
                or not _HEX_512.fullmatch(self.fingerprint)
                or not hmac.compare_digest(self.fingerprint, digest)):
            raise ProjectError("PROJECT_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def _payload(self) -> dict[str, object]:
        """Return the exact canonical project semantic payload."""
        return {
            "project_id": self.project_id, "tenant_id": self.tenant_id,
            "name": self.name, "code": self.code, "summary": self.summary,
            "status": cast(ProjectStatus, self.status).value, "owner_principal_id": self.owner_principal_id,
            "department_id": self.department_id,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "source_type": cast(ProjectSourceType, self.source_type).value,
            "external_source_reference": self.external_source_reference,
            "created_by_principal_id": self.created_by_principal_id,
            "created_at": self.created_at.isoformat(),
            "updated_by_principal_id": self.updated_by_principal_id,
            "updated_at": self.updated_at.isoformat(),
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "revision": self.revision, "schema": self.schema, "version": self.version,
        }

    def _digest(self) -> str:
        """Fingerprint canonical persisted semantics with SHA3-512."""
        raw = json.dumps(self._payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return hashlib.sha3_512(raw).hexdigest()

    def to_dict(self) -> dict[str, object]:
        """Serialize one complete canonical aggregate for its owning registry."""
        return {**self._payload(), "fingerprint": self.fingerprint}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> Project:
        """Hydrate only the exact supported persistence schema; reject unknown fields."""
        expected = {
            "project_id", "tenant_id", "name", "code", "summary", "status",
            "owner_principal_id", "department_id", "start_date", "target_date",
            "source_type", "external_source_reference", "created_by_principal_id",
            "created_at", "updated_by_principal_id", "updated_at", "archived_at",
            "revision", "schema", "version", "fingerprint",
        }
        if not isinstance(payload, dict) or set(payload) != expected:
            raise ProjectError("PROJECT_PERSISTED_SCHEMA_INVALID")
        values: dict[str, Any] = dict(payload)
        for name in ("start_date", "target_date"):
            value = values[name]
            if value is not None:
                try:
                    values[name] = date.fromisoformat(value) if isinstance(value, str) else value
                except (TypeError, ValueError) as error:
                    raise ProjectError(f"PROJECT_{name.upper()}_DATE_INVALID") from error
        for name in ("created_at", "updated_at", "archived_at"):
            values[name] = _parse_timestamp(name, values[name], optional=name == "archived_at")
        try:
            return cls(**values)
        except TypeError as error:
            raise ProjectError("PROJECT_PERSISTED_SCHEMA_INVALID") from error

    def update(self, *, actor_principal_id: str, updated_at: datetime,
               expected_revision: int, changes: Mapping[str, object]) -> Project:
        """Return a revision-advanced project from an explicitly bounded field map."""
        self._expect_mutable(expected_revision)
        if not isinstance(changes, Mapping) or not set(changes).issubset(_UPDATE_FIELDS):
            raise ProjectError("PROJECT_UPDATE_FIELDS_INVALID")
        actor = _required_text("actor_principal_id", actor_principal_id)
        timestamp = _timestamp("updated_at", updated_at)
        assert timestamp is not None
        if timestamp < self.updated_at:
            raise ProjectError("PROJECT_TIMESTAMP_ORDER_INVALID")
        return replace(self, **dict(changes), updated_by_principal_id=actor,
                       updated_at=timestamp, revision=self.revision + 1, fingerprint="")

    def transition(self, *, actor_principal_id: str, updated_at: datetime,
                   expected_revision: int, resulting_status: ProjectStatus | str) -> Project:
        """Return a new revision only for an allowed project status transition."""
        self._expect_mutable(expected_revision)
        actor = _required_text("actor_principal_id", actor_principal_id)
        timestamp = _timestamp("updated_at", updated_at)
        assert timestamp is not None
        if timestamp < self.updated_at:
            raise ProjectError("PROJECT_TIMESTAMP_ORDER_INVALID")
        try:
            target = ProjectStatus(resulting_status)
        except (TypeError, ValueError) as error:
            raise ProjectError("PROJECT_STATUS_INVALID") from error
        if target not in _ALLOWED_TRANSITIONS[cast(ProjectStatus, self.status)]:
            raise ProjectError("PROJECT_STATUS_TRANSITION_INVALID")
        return replace(self, status=target, updated_by_principal_id=actor,
                       updated_at=timestamp, revision=self.revision + 1, fingerprint="")

    def archive(self, *, actor_principal_id: str, archived_at: datetime,
                expected_revision: int) -> Project:
        """Return a soft-archived project while retaining its prior lifecycle state."""
        self._expect_mutable(expected_revision)
        actor = _required_text("actor_principal_id", actor_principal_id)
        timestamp = _timestamp("archived_at", archived_at)
        assert timestamp is not None
        if timestamp < self.updated_at:
            raise ProjectError("PROJECT_TIMESTAMP_ORDER_INVALID")
        return replace(self, archived_at=timestamp, updated_by_principal_id=actor,
                       updated_at=timestamp, revision=self.revision + 1, fingerprint="")

    def _expect_mutable(self, expected_revision: int) -> None:
        """Reject archived aggregates and stale revision commands."""
        if type(expected_revision) is not int or expected_revision != self.revision:
            raise ProjectError("PROJECT_REVISION_CONFLICT")
        if self.archived_at is not None:
            raise ProjectError("PROJECT_ARCHIVED_IMMUTABLE")


__all__ = ["VERSION", "SCHEMA", "Project", "ProjectError", "ProjectSourceType", "ProjectStatus"]

# ARTIFACT: project.py
# VERSION: v1.0.1-TENANT-PROJECT-DOMAIN
# AUTHORITY BOUNDARY: validated tenant project facts only; authorization and persistence belong to EOS
# TENANT POSTURE: explicit tenant identity is required and never inferred or defaulted
# FAIL-CLOSED POSTURE: malformed fields, transitions, timestamps, persisted schema, and fingerprints reject
# FINANCIAL EXECUTION AUTHORITY: project state grants no financial authority; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
