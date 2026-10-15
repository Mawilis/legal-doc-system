"""TITLE: WILSY OS Legal Work Item Domain.

VERSION: v1.0.1-G7E-LEGAL-WORK-ITEM

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations.

EPITOME:
    Preserve one immutable tenant- and matter-scoped unit of operational Legal
    work without manufacturing matter, workflow, assignment, supervision,
    professional, IAM, legal-event, billing, payment, settlement or financial
    execution authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_work_item.py

COLLABORATION / OWNERSHIP:
    CaseMatter remains canonical matter truth.
    Domain-specific Legal artifacts remain canonical legal-event truth.
    Future workflow domains may correlate work items but do not delegate their
    authority into this value.
    Future assignment and supervision domains own principal/team bindings.
    Future work registry owns persistence.
    Kennel EOS remains exclusive financial-execution authority.

TENANT BOUNDARY:
    Every item binds one exact non-pseudo tenant_id and case_matter_id.

AUTHORITY BOUNDARY:
    Operational work posture only. OPEN, IN_PROGRESS, BLOCKED, COMPLETED and
    CANCELLED describe the work item, never the legal state of its source.

DUE-DATE BOUNDARY:
    due_at is caller-supplied operational evidence. This domain never calculates
    jurisdictional periods, filing dates, limitation dates, SLAs or legal rules.

COMPLETION BOUNDARY:
    COMPLETED requires explicit completion evidence reference and fingerprint.
    Completion never proves completion of the source legal event.

COMMERCIAL BOUNDARY:
    Work items contain no plan, price, subscription or entitlement truth.

FINANCIAL AUTHORITY BOUNDARY:
    No invoice, payment, trust, settlement or financial execution authority.

FAIL-CLOSED POSTURE:
    Malformed identity, pseudo tenants, unknown status, invalid chronology,
    invalid evidence fingerprints, impossible completion/cancellation evidence,
    schema drift and fingerprint drift reject without fallback.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import hmac
import json
from typing import Final, NoReturn


VERSION: Final[str] = "v1.0.1-G7E-LEGAL-WORK-ITEM"
SCHEMA: Final[str] = "WILSY-LEGAL-WORK-ITEM/V1"


class LegalWorkItemError(ValueError):
    """Stable fail-closed Legal work-item validation failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalWorkItemStatus(StrEnum):
    """Operational work posture only; never source-domain legal state."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


def _fail(code: str) -> NoReturn:
    raise LegalWorkItemError(code)


def _text(name: str, value: object, *, limit: int = 240) -> str:
    if not isinstance(value, str):
        _fail(f"G7E_{name.upper()}_INVALID")

    normalized = value.strip()

    if (
        not normalized
        or normalized != value
        or len(normalized) > limit
    ):
        _fail(f"G7E_{name.upper()}_INVALID")

    return normalized


def _tenant(value: object) -> str:
    tenant = _text("tenant_id", value, limit=160)

    if tenant.casefold() in {"default", "global", "root", "*"}:
        _fail("G7E_TENANT_REQUIRED")

    return tenant


def _timestamp(name: str, value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(f"G7E_{name.upper()}_INVALID")

    return value.astimezone(timezone.utc)


def _fingerprint(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 128
        or value.lower() != value
    ):
        _fail(f"G7E_{name.upper()}_INVALID")

    try:
        int(value, 16)
    except ValueError as error:
        raise LegalWorkItemError(
            f"G7E_{name.upper()}_INVALID"
        ) from error

    return value


def _optional_text(
    name: str,
    value: object,
    *,
    limit: int = 240,
) -> str | None:
    if value is None:
        return None
    return _text(name, value, limit=limit)


def _optional_fingerprint(
    name: str,
    value: object,
) -> str | None:
    if value is None:
        return None
    return _fingerprint(name, value)


def _optional_timestamp(
    name: str,
    value: object,
) -> datetime | None:
    if value is None:
        return None
    return _timestamp(name, value)


@dataclass(frozen=True, slots=True)
class LegalWorkItem:
    """One immutable operational unit of Legal work."""

    work_item_id: str
    tenant_id: str
    case_matter_id: str

    title: str
    source_kind: str
    source_reference: str
    source_evidence_fingerprint: str

    status: LegalWorkItemStatus | str
    created_at: datetime

    due_at: datetime | None = None

    completion_evidence_reference: str | None = None
    completion_evidence_fingerprint: str | None = None
    completed_at: datetime | None = None

    cancellation_reason_reference: str | None = None
    cancelled_at: datetime | None = None

    schema: str = SCHEMA
    work_item_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        work_item_id = _text(
            "work_item_id",
            self.work_item_id,
            limit=160,
        )
        tenant_id = _tenant(self.tenant_id)
        case_matter_id = _text(
            "case_matter_id",
            self.case_matter_id,
            limit=160,
        )
        title = _text(
            "title",
            self.title,
            limit=500,
        )
        source_kind = _text(
            "source_kind",
            self.source_kind,
            limit=160,
        )
        source_reference = _text(
            "source_reference",
            self.source_reference,
            limit=320,
        )
        source_fingerprint = _fingerprint(
            "source_evidence_fingerprint",
            self.source_evidence_fingerprint,
        )

        try:
            status = LegalWorkItemStatus(self.status)
        except (TypeError, ValueError) as error:
            raise LegalWorkItemError(
                "G7E_STATUS_INVALID"
            ) from error

        created_at = _timestamp(
            "created_at",
            self.created_at,
        )
        due_at = _optional_timestamp(
            "due_at",
            self.due_at,
        )

        completion_reference = _optional_text(
            "completion_evidence_reference",
            self.completion_evidence_reference,
            limit=320,
        )
        completion_fingerprint = _optional_fingerprint(
            "completion_evidence_fingerprint",
            self.completion_evidence_fingerprint,
        )
        completed_at = _optional_timestamp(
            "completed_at",
            self.completed_at,
        )

        cancellation_reference = _optional_text(
            "cancellation_reason_reference",
            self.cancellation_reason_reference,
            limit=320,
        )
        cancelled_at = _optional_timestamp(
            "cancelled_at",
            self.cancelled_at,
        )

        if self.schema != SCHEMA or self.work_item_version != VERSION:
            _fail("G7E_IDENTITY_INVALID")

        if due_at is not None and due_at < created_at:
            _fail("G7E_DUE_AT_BEFORE_CREATED")

        completion_fields = (
            completion_reference,
            completion_fingerprint,
            completed_at,
        )

        if status is LegalWorkItemStatus.COMPLETED:
            if any(value is None for value in completion_fields):
                _fail("G7E_COMPLETION_EVIDENCE_REQUIRED")

            assert completed_at is not None

            if completed_at < created_at:
                _fail("G7E_COMPLETED_AT_BEFORE_CREATED")

            if cancellation_reference is not None or cancelled_at is not None:
                _fail("G7E_COMPLETION_CANCELLATION_CONFLICT")
        else:
            if any(value is not None for value in completion_fields):
                _fail("G7E_COMPLETION_EVIDENCE_NOT_ALLOWED")

        if status is LegalWorkItemStatus.CANCELLED:
            if cancellation_reference is None or cancelled_at is None:
                _fail("G7E_CANCELLATION_EVIDENCE_REQUIRED")

            if cancelled_at < created_at:
                _fail("G7E_CANCELLED_AT_BEFORE_CREATED")

            if (
                completion_reference is not None
                or completion_fingerprint is not None
                or completed_at is not None
            ):
                _fail("G7E_COMPLETION_CANCELLATION_CONFLICT")
        else:
            if (
                cancellation_reference is not None
                or cancelled_at is not None
            ):
                _fail("G7E_CANCELLATION_EVIDENCE_NOT_ALLOWED")

        object.__setattr__(self, "work_item_id", work_item_id)
        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(
            self,
            "case_matter_id",
            case_matter_id,
        )
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "source_kind", source_kind)
        object.__setattr__(
            self,
            "source_reference",
            source_reference,
        )
        object.__setattr__(
            self,
            "source_evidence_fingerprint",
            source_fingerprint,
        )
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "due_at", due_at)
        object.__setattr__(
            self,
            "completion_evidence_reference",
            completion_reference,
        )
        object.__setattr__(
            self,
            "completion_evidence_fingerprint",
            completion_fingerprint,
        )
        object.__setattr__(
            self,
            "completed_at",
            completed_at,
        )
        object.__setattr__(
            self,
            "cancellation_reason_reference",
            cancellation_reference,
        )
        object.__setattr__(
            self,
            "cancelled_at",
            cancelled_at,
        )

        digest = self._compute_fingerprint()

        if self.fingerprint:
            supplied = _fingerprint(
                "fingerprint",
                self.fingerprint,
            )

            if not hmac.compare_digest(
                supplied,
                digest,
            ):
                _fail("G7E_FINGERPRINT_MISMATCH")

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def semantic_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "work_item_version": self.work_item_version,
            "work_item_id": self.work_item_id,
            "tenant_id": self.tenant_id,
            "case_matter_id": self.case_matter_id,
            "title": self.title,
            "source_kind": self.source_kind,
            "source_reference": self.source_reference,
            "source_evidence_fingerprint":
                self.source_evidence_fingerprint,
            "status": LegalWorkItemStatus(self.status).value,
            "created_at": self.created_at.isoformat(),
            "due_at": (
                self.due_at.isoformat()
                if self.due_at is not None
                else None
            ),
            "completion_evidence_reference":
                self.completion_evidence_reference,
            "completion_evidence_fingerprint":
                self.completion_evidence_fingerprint,
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at is not None
                else None
            ),
            "cancellation_reason_reference":
                self.cancellation_reason_reference,
            "cancelled_at": (
                self.cancelled_at.isoformat()
                if self.cancelled_at is not None
                else None
            ),
        }

    def _compute_fingerprint(self) -> str:
        canonical = json.dumps(
            self.semantic_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        return sha3_512(
            canonical.encode("utf-8")
        ).hexdigest()

    def to_dict(self) -> dict[str, object]:
        return {
            **self.semantic_dict(),
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        value: object,
    ) -> "LegalWorkItem":
        if not isinstance(value, dict):
            _fail("G7E_PAYLOAD_INVALID")

        required = {
            "schema",
            "work_item_version",
            "work_item_id",
            "tenant_id",
            "case_matter_id",
            "title",
            "source_kind",
            "source_reference",
            "source_evidence_fingerprint",
            "status",
            "created_at",
            "due_at",
            "completion_evidence_reference",
            "completion_evidence_fingerprint",
            "completed_at",
            "cancellation_reason_reference",
            "cancelled_at",
            "fingerprint",
        }

        if set(value) != required:
            _fail("G7E_PAYLOAD_SCHEMA_INVALID")

        def parse_required_time(
            name: str,
        ) -> datetime:
            raw = value[name]

            if not isinstance(raw, str):
                _fail(f"G7E_{name.upper()}_INVALID")

            try:
                return datetime.fromisoformat(raw)
            except ValueError as error:
                raise LegalWorkItemError(
                    f"G7E_{name.upper()}_INVALID"
                ) from error

        def parse_optional_time(
            name: str,
        ) -> datetime | None:
            raw = value[name]

            if raw is None:
                return None

            if not isinstance(raw, str):
                _fail(f"G7E_{name.upper()}_INVALID")

            try:
                return datetime.fromisoformat(raw)
            except ValueError as error:
                raise LegalWorkItemError(
                    f"G7E_{name.upper()}_INVALID"
                ) from error

        return cls(
            schema=value["schema"],
            work_item_version=value["work_item_version"],
            work_item_id=value["work_item_id"],
            tenant_id=value["tenant_id"],
            case_matter_id=value["case_matter_id"],
            title=value["title"],
            source_kind=value["source_kind"],
            source_reference=value["source_reference"],
            source_evidence_fingerprint=value[
                "source_evidence_fingerprint"
            ],
            status=value["status"],
            created_at=parse_required_time("created_at"),
            due_at=parse_optional_time("due_at"),
            completion_evidence_reference=value[
                "completion_evidence_reference"
            ],
            completion_evidence_fingerprint=value[
                "completion_evidence_fingerprint"
            ],
            completed_at=parse_optional_time("completed_at"),
            cancellation_reason_reference=value[
                "cancellation_reason_reference"
            ],
            cancelled_at=parse_optional_time("cancelled_at"),
            fingerprint=value["fingerprint"],
        )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalWorkItem",
    "LegalWorkItemError",
    "LegalWorkItemStatus",
]

# ARTIFACT: legal_work_item.py
# VERSION: v1.0.1-G7E-LEGAL-WORK-ITEM
# AUTHORITY BOUNDARY: immutable operational Legal work posture only
# WORK ITEM NOT LEGAL EVENT: YES
# ASSIGNMENT AUTHORITY: NONE
# SUPERVISION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# TENANT POSTURE: exact tenant correlation; cross-tenant inference prohibited
# FAIL-CLOSED POSTURE: malformed, incomplete, or divergent evidence rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
