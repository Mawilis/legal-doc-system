"""Wilsy OS immutable legal-matter deadline evidence.

TITLE: Wilsy OS Legal Matter Deadline Pure Domain
VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D1-DEADLINE-DOMAIN
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Model one exact tenant-and-matter-bound deadline from explicit source
         evidence without calculating jurisdictional periods, mutating matter
         lifecycle, or inventing filing, service, court, AI, or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_matter_deadline.py
COLLABORATION / OWNERSHIP: Legal Operations owns deadline evidence; CaseMatter
                            owns matter identity; a later D2 registry will own
                            persistence; later projections may observe but may
                            not manufacture this truth.
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0-LEGAL-OPS-COMPLETION-D1-DEADLINE-DOMAIN
           establishes immutable deadline identity, explicit source evidence,
           UTC chronology, append-only supersession reference, strict hydration,
           deterministic SHA3-512 integrity, and pure temporal observation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque bounded identifiers and evidence references
                             only; no party narrative, credentials, tokens, or
                             unnecessary personal information.
TENANT BOUNDARY: Every deadline is bound to one exact tenant_id and
                 case_matter_id; deadline_id never grants global lookup scope.
AUTHORITY BOUNDARY: Operational legal-calendar evidence only. It does not prove
                    filing or service, create court or representation authority,
                    calculate legal periods, or permit AI to invent deadline truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains the exclusive financial
                               execution and settlement authority.
TRANSACTION BOUNDARY: Pure immutable in-memory construction, serialization,
                      hydration, and observation only; no IO or persistence.
FAIL-CLOSED DECLARATION: Malformed identity, classification, evidence, time,
                         schema, supersession, or fingerprint material rejects.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Final, NoReturn, cast
import unicodedata


VERSION: Final[str] = "v1.0.0-LEGAL-OPS-COMPLETION-D1-DEADLINE-DOMAIN"
SCHEMA: Final[str] = "WILSY-LEGAL-MATTER-DEADLINE/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_SHA3_512: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalMatterDeadlineError(ValueError):
    """Stable fail-closed deadline-domain error without authority-value leakage."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalMatterDeadlineKind(StrEnum):
    """Bounded descriptive classes that never calculate a legal period."""

    FILING = "FILING"
    HEARING = "HEARING"
    RESPONSE = "RESPONSE"
    SERVICE = "SERVICE"
    CONTRACTUAL = "CONTRACTUAL"
    INTERNAL_WORKFLOW = "INTERNAL_WORKFLOW"
    OTHER_EVIDENCED_DEADLINE = "OTHER_EVIDENCED_DEADLINE"


class LegalMatterDeadlineSourceType(StrEnum):
    """Closed provenance classes; classification does not establish correctness."""

    COURT_ORDER = "COURT_ORDER"
    RULE_OR_STATUTE = "RULE_OR_STATUTE"
    CONTRACTUAL = "CONTRACTUAL"
    CLIENT_INSTRUCTION = "CLIENT_INSTRUCTION"
    INTERNAL_WORKFLOW = "INTERNAL_WORKFLOW"
    OTHER_EVIDENCED_SOURCE = "OTHER_EVIDENCED_SOURCE"


class LegalMatterDeadlineStatus(StrEnum):
    """Explicit persisted lifecycle facts; none is inferred from clock time."""

    ACTIVE = "ACTIVE"
    SATISFIED = "SATISFIED"
    SUPERSEDED = "SUPERSEDED"
    CANCELLED = "CANCELLED"


class LegalMatterDeadlineTemporalPosture(StrEnum):
    """Pure observation at a caller-supplied time; never persisted authority."""

    UPCOMING = "UPCOMING"
    DUE = "DUE"
    OVERDUE = "OVERDUE"
    INACTIVE = "INACTIVE"


_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "deadline_version",
    "tenant_id",
    "case_matter_id",
    "deadline_id",
    "deadline_kind",
    "title",
    "due_at",
    "source_type",
    "source_reference",
    "source_evidence_fingerprint",
    "jurisdiction_reference",
    "created_at",
    "supersedes_deadline_id",
    "status",
    "fingerprint",
)
DEADLINE_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalMatterDeadlineError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail(f"D1_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("D1_TENANT_REQUIRED")
    return tenant


def _text(name: str, value: object, *, limit: int) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(
            ord(character) < 32
            or 0x7F <= ord(character) <= 0x9F
            or 0xD800 <= ord(character) <= 0xDFFF
            for character in value
        )
    ):
        _fail(f"D1_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if normalized != value:
        _fail(f"D1_{name.upper()}_INVALID")
    return value


def _fingerprint(name: str, value: object) -> str:
    if not isinstance(value, str) or _SHA3_512.fullmatch(value) is None:
        _fail(f"D1_{name.upper()}_INVALID")
    return value


def _timestamp(name: str, value: object) -> datetime:
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"D1_{name.upper()}_INVALID", error)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail(f"D1_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return (
            value.astimezone(timezone.utc)
            .isoformat(timespec="microseconds")
            .replace("+00:00", "Z")
        )
    if isinstance(value, StrEnum):
        return value.value
    return value


@dataclass(frozen=True, slots=True)
class LegalMatterDeadline:
    """Immutable evidenced deadline for one exact tenant and matter.

    Construction performs no legal-date calculation. ``jurisdiction_reference``
    and source provenance are context evidence, not court-rule authority.
    Supersession is only an append-only reference to earlier truth; it neither
    mutates nor proves the lifecycle status of the referenced deadline.
    """

    tenant_id: str
    case_matter_id: str
    deadline_id: str
    deadline_kind: LegalMatterDeadlineKind | str
    title: str
    due_at: datetime
    source_type: LegalMatterDeadlineSourceType | str
    source_reference: str
    source_evidence_fingerprint: str
    jurisdiction_reference: str
    created_at: datetime
    supersedes_deadline_id: str | None = None
    status: LegalMatterDeadlineStatus | str = LegalMatterDeadlineStatus.ACTIVE
    schema: str = SCHEMA
    deadline_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.deadline_version != VERSION:
            _fail("D1_IDENTITY_INVALID")
        try:
            kind = LegalMatterDeadlineKind(self.deadline_kind)
            source_type = LegalMatterDeadlineSourceType(self.source_type)
            status = LegalMatterDeadlineStatus(self.status)
        except (TypeError, ValueError) as error:
            _fail("D1_CLASSIFICATION_INVALID", error)
        deadline_id = _identity("deadline_id", self.deadline_id)
        supersedes = self.supersedes_deadline_id
        if supersedes is not None:
            supersedes = _identity("supersedes_deadline_id", supersedes)
            if supersedes == deadline_id:
                _fail("D1_SELF_SUPERSESSION_FORBIDDEN")
        normalized: dict[str, object] = {
            "tenant_id": _tenant(self.tenant_id),
            "case_matter_id": _identity("case_matter_id", self.case_matter_id),
            "deadline_id": deadline_id,
            "deadline_kind": kind,
            "title": _text("title", self.title, limit=240),
            "due_at": _timestamp("due_at", self.due_at),
            "source_type": source_type,
            "source_reference": _text(
                "source_reference", self.source_reference, limit=512
            ),
            "source_evidence_fingerprint": _fingerprint(
                "source_evidence_fingerprint", self.source_evidence_fingerprint
            ),
            "jurisdiction_reference": _text(
                "jurisdiction_reference", self.jurisdiction_reference, limit=240
            ),
            "created_at": _timestamp("created_at", self.created_at),
            "supersedes_deadline_id": supersedes,
            "status": status,
        }
        for field, value in normalized.items():
            object.__setattr__(self, field, value)
        payload = {
            field: _json_value(getattr(self, field)) for field in _FIELDS[:-1]
        }
        digest = hashlib.sha3_512(
            json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=False,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("D1_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize the complete exact domain payload without adding authority."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalMatterDeadline":
        """Hydrate only the exact schema and verify its SHA3-512 fingerprint."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("D1_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(
            stored, result.fingerprint
        ):
            _fail("D1_FINGERPRINT_MISMATCH")
        return result

    def temporal_posture(
        self, at: datetime
    ) -> LegalMatterDeadlineTemporalPosture:
        """Observe temporal posture at explicit aware time without mutation.

        Inactive lifecycle states remain inactive regardless of clock position.
        This method uses no reminder threshold, holiday, business-day, filing,
        service, court-calendar, external-system, or AI inference.
        """
        observed_at = _timestamp("observation_at", at)
        if self.status is not LegalMatterDeadlineStatus.ACTIVE:
            return LegalMatterDeadlineTemporalPosture.INACTIVE
        if observed_at < self.due_at:
            return LegalMatterDeadlineTemporalPosture.UPCOMING
        if observed_at == self.due_at:
            return LegalMatterDeadlineTemporalPosture.DUE
        return LegalMatterDeadlineTemporalPosture.OVERDUE


__all__ = [
    "DEADLINE_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalMatterDeadline",
    "LegalMatterDeadlineError",
    "LegalMatterDeadlineKind",
    "LegalMatterDeadlineSourceType",
    "LegalMatterDeadlineStatus",
    "LegalMatterDeadlineTemporalPosture",
]


# ARTIFACT: legal_matter_deadline.py
# VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D1-DEADLINE-DOMAIN
# AUTHORITY BOUNDARY: immutable evidenced deadline domain only; no filing, service, court, representation, AI, persistence, or calendar-rule authority
# TENANT POSTURE: exact tenant_id plus case_matter_id binding; no global deadline lookup authority
# FAIL-CLOSED POSTURE: malformed identity, evidence, time, classification, schema, supersession, and fingerprint material reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
