"""Wilsy OS Legal Matter Deadline intelligence projection.

TITLE: Wilsy OS Legal Matter Deadline Intelligence Projection
VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D6-DEADLINE-INTELLIGENCE
AUTHORITY: Wilsy OS Core Governance / read-only intelligence projection.
EPITOME: Project exact canonical deadline evidence into deterministic temporal
         posture counts at one explicit observation instant without calculating
         legal periods, recommending legal action, or creating lifecycle truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/domain/legal_matter_deadline_intelligence.py
COLLABORATION / OWNERSHIP: Legal Matter Deadline D1 owns immutable deadline truth
                            and temporal posture semantics. D6 owns only a bounded
                            deterministic intelligence projection over those facts.
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0-LEGAL-OPS-COMPLETION-D6-DEADLINE-INTELLIGENCE
           establishes exact tenant/matter correlation, deterministic ordering,
           explicit-time posture counts, bounded item projection and SHA3-512
           observation integrity without source-evidence disclosure.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Projection excludes source_reference and
                             source_evidence_fingerprint; only bounded deadline
                             identity, classification, chronology and provenance
                             class/jurisdiction references are exposed.
TENANT BOUNDARY: Every source deadline must match the exact requested tenant and
                 matter; mixed-tenant or mixed-matter input rejects.
AUTHORITY BOUNDARY: Observation/aggregation only; no legal-period calculation,
                    court-rule inference, filing/service truth, reminder policy,
                    recommendation, authorization, execution, or AI command authority.
TRANSACTION BOUNDARY: Pure in-memory projection only; no IO or persistence.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Malformed observation time, duplicate identities,
                         mixed scope, non-deadline input, or integrity drift rejects.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
from typing import Final

from tools.eos.legal_operations.domain.legal_matter_deadline import (
    LegalMatterDeadline,
    LegalMatterDeadlineTemporalPosture,
)

VERSION: Final[str] = "v1.0.0-LEGAL-OPS-COMPLETION-D6-DEADLINE-INTELLIGENCE"
SCHEMA: Final[str] = "WILSY-LEGAL-MATTER-DEADLINE-INTELLIGENCE/V1"


class LegalMatterDeadlineIntelligenceError(ValueError):
    """Stable fail-closed D6 projection error without source-evidence leakage."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _aware(value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalMatterDeadlineIntelligenceError("D6_OBSERVATION_TIME_INVALID")
    return value.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return (
        value.astimezone(timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )


@dataclass(frozen=True, slots=True)
class LegalMatterDeadlineIntelligenceItem:
    """Bounded observation of one canonical deadline."""

    deadline_id: str
    case_matter_id: str
    deadline_kind: str
    due_at: datetime
    source_type: str
    jurisdiction_reference: str
    status: str
    temporal_posture: LegalMatterDeadlineTemporalPosture
    deadline_fingerprint: str

    def to_dict(self) -> dict[str, object]:
        """Return the exact bounded intelligence item."""
        return {
            "deadline_id": self.deadline_id,
            "case_matter_id": self.case_matter_id,
            "deadline_kind": self.deadline_kind,
            "due_at": _iso(self.due_at),
            "source_type": self.source_type,
            "jurisdiction_reference": self.jurisdiction_reference,
            "status": self.status,
            "temporal_posture": str(self.temporal_posture),
            "deadline_fingerprint": self.deadline_fingerprint,
        }


@dataclass(frozen=True, slots=True)
class LegalMatterDeadlineIntelligenceProjection:
    """Deterministic tenant/matter deadline observation at one explicit instant."""

    tenant_id: str
    case_matter_id: str
    observed_at: datetime
    items: tuple[LegalMatterDeadlineIntelligenceItem, ...]
    active_count: int
    upcoming_count: int
    due_count: int
    overdue_count: int
    inactive_count: int
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.version != VERSION:
            raise LegalMatterDeadlineIntelligenceError("D6_IDENTITY_INVALID")
        observed = _aware(self.observed_at)
        object.__setattr__(self, "observed_at", observed)
        counts = (
            self.active_count,
            self.upcoming_count,
            self.due_count,
            self.overdue_count,
            self.inactive_count,
        )
        if any(
            not isinstance(value, int) or isinstance(value, bool) or value < 0
            for value in counts
        ):
            raise LegalMatterDeadlineIntelligenceError("D6_COUNT_INVALID")
        if self.active_count != (
            self.upcoming_count + self.due_count + self.overdue_count
        ):
            raise LegalMatterDeadlineIntelligenceError("D6_COUNT_INVALID")
        if len(self.items) != self.active_count + self.inactive_count:
            raise LegalMatterDeadlineIntelligenceError("D6_COUNT_INVALID")
        payload = {
            "schema": self.schema,
            "version": self.version,
            "tenant_id": self.tenant_id,
            "case_matter_id": self.case_matter_id,
            "observed_at": _iso(self.observed_at),
            "items": [item.to_dict() for item in self.items],
            "active_count": self.active_count,
            "upcoming_count": self.upcoming_count,
            "due_count": self.due_count,
            "overdue_count": self.overdue_count,
            "inactive_count": self.inactive_count,
        }
        digest = hashlib.sha3_512(
            json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=False,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if self.fingerprint and not hmac.compare_digest(self.fingerprint, digest):
            raise LegalMatterDeadlineIntelligenceError("D6_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Return the exact bounded deterministic projection."""
        return {
            "schema": self.schema,
            "version": self.version,
            "tenant_id": self.tenant_id,
            "case_matter_id": self.case_matter_id,
            "observed_at": _iso(self.observed_at),
            "items": [item.to_dict() for item in self.items],
            "active_count": self.active_count,
            "upcoming_count": self.upcoming_count,
            "due_count": self.due_count,
            "overdue_count": self.overdue_count,
            "inactive_count": self.inactive_count,
            "fingerprint": self.fingerprint,
        }


def project_legal_matter_deadline_intelligence(
    deadlines: tuple[LegalMatterDeadline, ...],
    *,
    tenant_id: str,
    case_matter_id: str,
    observed_at: datetime,
) -> LegalMatterDeadlineIntelligenceProjection:
    """Project exact deadline facts into non-authoritative temporal intelligence."""
    observed = _aware(observed_at)
    if (
        not isinstance(deadlines, tuple)
        or not isinstance(tenant_id, str)
        or not tenant_id
        or tenant_id != tenant_id.strip()
        or not isinstance(case_matter_id, str)
        or not case_matter_id
        or case_matter_id != case_matter_id.strip()
    ):
        raise LegalMatterDeadlineIntelligenceError("D6_INPUT_INVALID")

    seen: set[str] = set()
    items: list[LegalMatterDeadlineIntelligenceItem] = []
    for deadline in deadlines:
        if type(deadline) is not LegalMatterDeadline:
            raise LegalMatterDeadlineIntelligenceError("D6_DEADLINE_INVALID")
        if (
            deadline.tenant_id != tenant_id
            or deadline.case_matter_id != case_matter_id
        ):
            raise LegalMatterDeadlineIntelligenceError("D6_SCOPE_MISMATCH")
        if deadline.deadline_id in seen:
            raise LegalMatterDeadlineIntelligenceError("D6_DUPLICATE_DEADLINE")
        seen.add(deadline.deadline_id)
        posture = deadline.temporal_posture(observed)
        items.append(
            LegalMatterDeadlineIntelligenceItem(
                deadline_id=deadline.deadline_id,
                case_matter_id=deadline.case_matter_id,
                deadline_kind=str(deadline.deadline_kind),
                due_at=deadline.due_at,
                source_type=str(deadline.source_type),
                jurisdiction_reference=deadline.jurisdiction_reference,
                status=str(deadline.status),
                temporal_posture=posture,
                deadline_fingerprint=deadline.fingerprint,
            )
        )

    ordered = tuple(
        sorted(items, key=lambda item: (item.due_at, item.deadline_id))
    )
    upcoming = sum(
        item.temporal_posture is LegalMatterDeadlineTemporalPosture.UPCOMING
        for item in ordered
    )
    due = sum(
        item.temporal_posture is LegalMatterDeadlineTemporalPosture.DUE
        for item in ordered
    )
    overdue = sum(
        item.temporal_posture is LegalMatterDeadlineTemporalPosture.OVERDUE
        for item in ordered
    )
    inactive = sum(
        item.temporal_posture is LegalMatterDeadlineTemporalPosture.INACTIVE
        for item in ordered
    )

    return LegalMatterDeadlineIntelligenceProjection(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        observed_at=observed,
        items=ordered,
        active_count=upcoming + due + overdue,
        upcoming_count=upcoming,
        due_count=due,
        overdue_count=overdue,
        inactive_count=inactive,
    )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalMatterDeadlineIntelligenceError",
    "LegalMatterDeadlineIntelligenceItem",
    "LegalMatterDeadlineIntelligenceProjection",
    "project_legal_matter_deadline_intelligence",
]

# ARTIFACT: legal_matter_deadline_intelligence.py
# VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D6-DEADLINE-INTELLIGENCE
# AUTHORITY BOUNDARY: deterministic explicit-time observation only; no legal calculation, recommendation, authorization, AI command or lifecycle mutation
# TENANT POSTURE: every source deadline must match the exact requested tenant and matter
# FAIL-CLOSED POSTURE: invalid time, input, scope, duplicate identity or fingerprint drift rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
