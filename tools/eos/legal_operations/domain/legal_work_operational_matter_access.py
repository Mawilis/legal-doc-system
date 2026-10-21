"""TITLE: WILSY OS Operational Practitioner Matter Access History.
VERSION: v1.0.0-P47-R95-G11-OPERATIONAL-ACCESS-HISTORY
AUTHORITY: Immutable historical evidence and non-authorizing currentness.
EPITOME: Exact tenant/matter/practitioner lineage; deterministic
    revocation, future exclusion, and corruption-first denial.
ABSOLUTE CANONICAL PATH:
    tools/eos/legal_operations/domain/legal_work_operational_matter_access.py
COLLABORATION / OWNERSHIP: WILSY OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-21
CHANGELOG:
    2026-10-21 v1.0.0-P47-R95-G11-OPERATIONAL-ACCESS-HISTORY
    Introduces integrity-bound grant/revocation event history and
    purely historical, always-non-authorizing currentness.
SECURITY: No names, emails, tokens or financial authority.
TENANT BOUNDARY: Exact non-default tenant and matter scope.
AUTHORITY BOUNDARY: A GRANTED event is never sufficient for
    matter-content access, actor authority or work assignment.
ISSUER BOUNDARY: Issuer references are claims pending independent,
    transaction-bound authorization and source verification.
TRANSACTION BOUNDARY: Pure domain; no database or session access.
FAIL CLOSED: Missing, forked, malformed, tampered or ambiguous
    evidence cannot establish operational permission.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from hashlib import sha3_512
import json
import re
from typing import Final, Iterable

VERSION: Final[str] = "v1.0.0-P47-R95-G11-OPERATIONAL-ACCESS-HISTORY"
_SCHEMA: Final[str] = "WILSY-LEGAL-WORK-OPERATIONAL-MATTER-ACCESS/V1"
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}$")
_FORBIDDEN = frozenset({"default", "global", "root", "*"})


class LegalWorkMatterAccessError(ValueError):
    """Fail-closed event or history validation error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _identity(name: str, value: object, *, tenant: bool = False) -> str:
    if type(value) is not str or _ID.fullmatch(value) is None:
        raise LegalWorkMatterAccessError(f"P47_R95_{name.upper()}_INVALID")
    if tenant and value.casefold() in _FORBIDDEN:
        raise LegalWorkMatterAccessError("P47_R95_TENANT_INVALID")
    return value


def _moment(value: object) -> datetime:
    if (
        type(value) is not datetime
        or value.tzinfo is None
        or value.utcoffset() != timedelta(0)
    ):
        raise LegalWorkMatterAccessError("P47_R95_UTC_TIMESTAMP_REQUIRED")
    return value.astimezone(timezone.utc)


def _digest(payload: dict[str, object]) -> str:
    raw = json.dumps(
        payload, sort_keys=True, ensure_ascii=False,
        allow_nan=False, separators=(",", ":"),
    ).encode("utf-8")
    return sha3_512(raw).hexdigest()


class LegalWorkMatterAccessState(StrEnum):
    NO_GRANT = "NO_GRANT"
    GRANTED_UNVERIFIED = "GRANTED_UNVERIFIED"
    REVOKED = "REVOKED"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"


@dataclass(frozen=True, slots=True)
class LegalWorkMatterAccessEvent:
    tenant_id: str
    case_matter_id: str
    practitioner_principal_id: str
    event_id: str
    predecessor_event_id: str | None
    decision: str
    occurred_at: datetime
    issuer_principal_id: str
    issuer_authorization_evidence_reference: str
    reason_reference: str
    schema: str = _SCHEMA
    fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "tenant_id", "case_matter_id", "practitioner_principal_id",
            "event_id", "issuer_principal_id",
            "issuer_authorization_evidence_reference", "reason_reference",
        ):
            _identity(
                name, getattr(self, name),
                tenant=name == "tenant_id",
            )

        predecessor = self.predecessor_event_id
        if predecessor is not None:
            _identity("predecessor_event_id", predecessor)
            if predecessor == self.event_id:
                raise LegalWorkMatterAccessError("P47_R95_SELF_PREDECESSOR")

        if type(self.decision) is not str or self.decision not in (
            "GRANTED", "REVOKED",
        ):
            raise LegalWorkMatterAccessError("P47_R95_DECISION_INVALID")

        if self.schema != _SCHEMA:
            raise LegalWorkMatterAccessError("P47_R95_SCHEMA_INVALID")

        moment = _moment(self.occurred_at)
        object.__setattr__(self, "occurred_at", moment)
        object.__setattr__(self, "fingerprint", _digest(self.payload()))

    def payload(self) -> dict[str, object]:
        """Exact versioned canonical material; excludes fingerprint."""
        return {
            "schema": self.schema,
            "version": VERSION,
            "tenant_id": self.tenant_id,
            "case_matter_id": self.case_matter_id,
            "practitioner_principal_id": self.practitioner_principal_id,
            "event_id": self.event_id,
            "predecessor_event_id": self.predecessor_event_id,
            "decision": self.decision,
            "occurred_at": self.occurred_at.isoformat(),
            "issuer_principal_id": self.issuer_principal_id,
            "issuer_authorization_evidence_reference":
                self.issuer_authorization_evidence_reference,
            "reason_reference": self.reason_reference,
        }

    def verify_integrity(self) -> bool:
        """Reject field mutation or forged digest, without issuer validation."""
        try:
            return (
                type(self) is LegalWorkMatterAccessEvent
                and self.schema == _SCHEMA
                and _digest(self.payload()) == self.fingerprint
            )
        except (TypeError, ValueError, AttributeError):
            return False


@dataclass(frozen=True, slots=True)
class LegalWorkMatterAccessCurrentness:
    state: LegalWorkMatterAccessState
    decisive_event_id: str | None = None
    decisive_event_fingerprint: str | None = None

    @property
    def permits_operational_access(self) -> bool:
        """Historical currentness NEVER grants operational access."""
        return False


def project_legal_work_matter_access_currentness(
    *,
    tenant_id: str,
    case_matter_id: str,
    practitioner_principal_id: str,
    evaluation_time: datetime,
    events: Iterable[LegalWorkMatterAccessEvent],
) -> LegalWorkMatterAccessCurrentness:
    """Project complete evidence history; no affirmative access admission."""
    _identity("tenant_id", tenant_id, tenant=True)
    _identity("case_matter_id", case_matter_id)
    _identity("practitioner_principal_id", practitioner_principal_id)
    now = _moment(evaluation_time)

    no_grant = LegalWorkMatterAccessCurrentness(
        LegalWorkMatterAccessState.NO_GRANT
    )
    corrupt = LegalWorkMatterAccessCurrentness(
        LegalWorkMatterAccessState.CORRUPT_BLOCKED
    )

    try:
        history = tuple(events)
    except Exception:
        return corrupt

    if not history:
        return no_grant

    by_id: dict[str, LegalWorkMatterAccessEvent] = {}
    for value in history:
        if (
            type(value) is not LegalWorkMatterAccessEvent
            or not value.verify_integrity()
            or (
                value.tenant_id,
                value.case_matter_id,
                value.practitioner_principal_id,
            ) != (
                tenant_id, case_matter_id, practitioner_principal_id
            )
        ):
            return corrupt

        existing = by_id.get(value.event_id)
        if existing is not None:
            if existing.fingerprint != value.fingerprint:
                return corrupt
            continue
        by_id[value.event_id] = value

    roots = [
        event for event in by_id.values()
        if event.predecessor_event_id is None
    ]
    if len(roots) != 1:
        return corrupt

    root = roots[0]
    if root.decision != "GRANTED":
        return corrupt

    successors: dict[str, LegalWorkMatterAccessEvent] = {}
    for event in by_id.values():
        predecessor = event.predecessor_event_id
        if predecessor is None:
            continue
        prior = by_id.get(predecessor)
        if (
            prior is None
            or event.occurred_at <= prior.occurred_at
            or predecessor in successors
        ):
            return corrupt
        successors[predecessor] = event

    ordered = []
    seen: set[str] = set()
    current = root
    while True:
        if current.event_id in seen:
            return corrupt
        seen.add(current.event_id)
        ordered.append(current)
        successor = successors.get(current.event_id)
        if successor is None:
            break
        current = successor

    if len(seen) != len(by_id):
        return corrupt

    # A revoked lineage is terminal. Regrant requires a separate,
    # governed issuance contract; a successor cannot resurrect it.
    revoked_seen = False
    for entry in ordered:
        if revoked_seen:
            return corrupt
        if entry.decision == "REVOKED":
            revoked_seen = True

    # Revocation never resurrects an earlier grant.
    # A future event is not applicable yet, but malformed future
    # lineage has already been rejected.
    applicable = [event for event in ordered if event.occurred_at <= now]
    if not applicable:
        return no_grant

    decisive = applicable[-1]
    return LegalWorkMatterAccessCurrentness(
        LegalWorkMatterAccessState.REVOKED
        if decisive.decision == "REVOKED"
        else LegalWorkMatterAccessState.GRANTED_UNVERIFIED,
        decisive.event_id,
        decisive.fingerprint,
    )


__all__ = [
    "VERSION",
    "LegalWorkMatterAccessError",
    "LegalWorkMatterAccessEvent",
    "LegalWorkMatterAccessState",
    "LegalWorkMatterAccessCurrentness",
    "project_legal_work_matter_access_currentness",
]

# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_work_operational_matter_access.py
# VERSION: v1.0.0-P47-R95-G11-OPERATIONAL-ACCESS-HISTORY
# DOCUMENTARY GRANT IS OPERATIONAL AUTHORITY: NO
# ISSUER CURRENT AUTHORITY VERIFIED: NO
# MATTER ACCESS OR ASSIGNMENT ENABLED: NO
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
