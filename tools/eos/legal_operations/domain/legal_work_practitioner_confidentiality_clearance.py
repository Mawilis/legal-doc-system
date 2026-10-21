"""TITLE: WILSY OS Practitioner Confidentiality Clearance Evidence Domain.
VERSION: v1.0.0-P47-R95-G38-IMMUTABLE-CLEARANCE-EVIDENCE
AUTHORITY: Immutable documentary evidence, not operational access authority.
EPITOME: Captures exact tenant/matter/practitioner confidentiality decisions
    as deterministic integrity evidence. A recorded CLEARED event is unverified
    and cannot establish ethical-wall satisfaction, permission, assignment or
    matter-content access. Terminal revocation, expiry, corrupt history and
    scope mismatch are always fail-closed.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_work_practitioner_confidentiality_clearance.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-21
CHANGELOG:
    2026-10-21 v1.0.0-P47-R95-G38-IMMUTABLE-CLEARANCE-EVIDENCE
    Introduces immutable, content-free clearance evidence only.
COMPLIANCE: WILSY OS sovereign Python/EOS fail-closed domain.
SECURITY / PRIVACY POSTURE: No matter content or clearance override tokens.
TENANT BOUNDARY: Exact tenant, matter and practitioner identities.
AUTHORITY BOUNDARY: Event and projection never authorize operational access.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import json
import re
from typing import Iterable


VERSION = "v1.0.0-P47-R95-G38-IMMUTABLE-CLEARANCE-EVIDENCE"
_DIGEST = re.compile(r"[0-9a-f]{128}\Z")
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,199}\Z")


class PractitionerConfidentialityClearanceError(ValueError):
    """Invalid immutable evidence or noncanonical query."""


class PractitionerConfidentialityClearanceState(StrEnum):
    NO_CLEARANCE = "NO_CLEARANCE"
    CLEARED_UNVERIFIED = "CLEARED_UNVERIFIED"
    REVOKED_BLOCKED = "REVOKED_BLOCKED"
    EXPIRED_BLOCKED = "EXPIRED_BLOCKED"
    DENIED_BLOCKED = "DENIED_BLOCKED"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"


def _identity(name: str, value: object) -> str:
    if type(value) is not str or _ID.fullmatch(value) is None:
        raise PractitionerConfidentialityClearanceError(name + "_INVALID")
    return value


def _time(name: str, value: object) -> datetime:
    if (
        type(value) is not datetime
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise PractitionerConfidentialityClearanceError(name + "_INVALID")
    at = value.astimezone(timezone.utc)
    if at.microsecond:
        raise PractitionerConfidentialityClearanceError(name + "_PRECISION_INVALID")
    return at


@dataclass(frozen=True, slots=True)
class PractitionerConfidentialityClearanceEvent:
    """Content-free, scope-bound documentary event; never an access grant."""

    tenant_id: str
    case_matter_id: str
    practitioner_principal_id: str
    clearance_event_id: str
    predecessor_event_id: str | None
    decision: str
    effective_at: datetime
    expires_at: datetime
    issuer_principal_id: str
    issuer_authorization_evidence_reference: str
    conflict_provenance_fingerprint: str
    confidentiality_decision_reference: str
    fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        fields = (
            "tenant_id", "case_matter_id", "practitioner_principal_id",
            "clearance_event_id", "issuer_principal_id",
            "issuer_authorization_evidence_reference",
            "confidentiality_decision_reference",
        )
        for name in fields:
            _identity(name, getattr(self, name))
        if self.predecessor_event_id is not None:
            _identity("predecessor_event_id", self.predecessor_event_id)
            if self.predecessor_event_id == self.clearance_event_id:
                raise PractitionerConfidentialityClearanceError("SELF_PREDECESSOR")
        if self.decision not in ("CLEARED", "DENIED", "REVOKED"):
            raise PractitionerConfidentialityClearanceError("DECISION_INVALID")
        if (
            type(self.conflict_provenance_fingerprint) is not str
            or _DIGEST.fullmatch(self.conflict_provenance_fingerprint) is None
        ):
            raise PractitionerConfidentialityClearanceError("PROVENANCE_INVALID")
        start = _time("effective_at", self.effective_at)
        end = _time("expires_at", self.expires_at)
        if end <= start:
            raise PractitionerConfidentialityClearanceError("WINDOW_INVALID")
        if start != self.effective_at or end != self.expires_at:
            raise PractitionerConfidentialityClearanceError("TIME_NONCANONICAL")
        payload = {
            name: getattr(self, name)
            for name in (
                *fields,
                "predecessor_event_id", "decision",
                "conflict_provenance_fingerprint",
            )
        }
        payload["effective_at"] = start.isoformat()
        payload["expires_at"] = end.isoformat()
        raw = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        object.__setattr__(self, "fingerprint", sha3_512(raw).hexdigest())


@dataclass(frozen=True, slots=True)
class PractitionerConfidentialityClearanceCurrentness:
    """Documentary projection. Never conveys access authorization."""

    tenant_id: str
    case_matter_id: str
    practitioner_principal_id: str
    evaluation_time: datetime
    state: PractitionerConfidentialityClearanceState
    evidence_fingerprint: str | None = None

    @property
    def permits_operational_access(self) -> bool:
        return False


def project_practitioner_confidentiality_clearance(
    *,
    tenant_id: str,
    case_matter_id: str,
    practitioner_principal_id: str,
    evaluation_time: datetime,
    events: Iterable[PractitionerConfidentialityClearanceEvent],
) -> PractitionerConfidentialityClearanceCurrentness:
    """Validate documentary lineage only; never verify real-world clearance."""
    tenant = _identity("tenant_id", tenant_id)
    matter = _identity("case_matter_id", case_matter_id)
    practitioner = _identity("practitioner_principal_id", practitioner_principal_id)
    at = _time("evaluation_time", evaluation_time)

    def result(
        state: PractitionerConfidentialityClearanceState,
        digest: str | None = None,
    ) -> PractitionerConfidentialityClearanceCurrentness:
        return PractitionerConfidentialityClearanceCurrentness(
            tenant, matter, practitioner, at, state, digest
        )

    blocked = PractitionerConfidentialityClearanceState.CORRUPT_BLOCKED
    try:
        history = tuple(events)
        if not history:
            return result(PractitionerConfidentialityClearanceState.NO_CLEARANCE)
        seen: dict[str, PractitionerConfidentialityClearanceEvent] = {}
        roots = []
        successors: dict[str, list[PractitionerConfidentialityClearanceEvent]] = {}
        for event in history:
            if type(event) is not PractitionerConfidentialityClearanceEvent:
                return result(blocked)
            # Re-run canonical construction and SHA3-512 hashing against
            # every supplied field. A forged persisted fingerprint is never
            # accepted, even when the frozen object was bypass-mutated.
            if replace(event).fingerprint != event.fingerprint:
                return result(blocked)
            if (
                event.tenant_id != tenant
                or event.case_matter_id != matter
                or event.practitioner_principal_id != practitioner
                or event.clearance_event_id in seen
            ):
                return result(blocked)
            seen[event.clearance_event_id] = event
            if event.predecessor_event_id is None:
                roots.append(event)
            else:
                successors.setdefault(event.predecessor_event_id, []).append(event)
        if len(roots) != 1 or any(len(items) != 1 for items in successors.values()):
            return result(blocked)
        if any(key not in seen for key in successors):
            return result(blocked)
        current = roots[0]
        visited = set()
        while True:
            if current.clearance_event_id in visited:
                return result(blocked)
            visited.add(current.clearance_event_id)
            children = successors.get(current.clearance_event_id, ())
            if not children:
                break
            child = children[0]
            if (
                child.effective_at < current.effective_at
                or child.effective_at >= current.expires_at
                or child.decision == "CLEARED"
            ):
                return result(blocked)
            current = child
        if len(visited) != len(history):
            return result(blocked)

        # First validate the entire successor lineage, including future
        # events. Then independently choose the event effective at the
        # requested evaluation time. Future revocation does not rewrite
        # an earlier documentary projection.
        current = roots[0]
        while successors.get(current.clearance_event_id):
            successor = successors[current.clearance_event_id][0]
            if successor.effective_at > at:
                break
            current = successor

        if current.effective_at > at:
            return result(PractitionerConfidentialityClearanceState.NO_CLEARANCE)
        if current.decision == "REVOKED":
            return result(
                PractitionerConfidentialityClearanceState.REVOKED_BLOCKED,
                current.fingerprint,
            )
        if current.decision == "DENIED":
            return result(
                PractitionerConfidentialityClearanceState.DENIED_BLOCKED,
                current.fingerprint,
            )
        if at >= current.expires_at:
            return result(
                PractitionerConfidentialityClearanceState.EXPIRED_BLOCKED,
                current.fingerprint,
            )
        return result(
            PractitionerConfidentialityClearanceState.CLEARED_UNVERIFIED,
            current.fingerprint,
        )
    except Exception:
        return result(blocked)


__all__ = [
    "VERSION",
    "PractitionerConfidentialityClearanceError",
    "PractitionerConfidentialityClearanceState",
    "PractitionerConfidentialityClearanceEvent",
    "PractitionerConfidentialityClearanceCurrentness",
    "project_practitioner_confidentiality_clearance",
]

# ARTIFACT: tools/eos/legal_operations/domain/legal_work_practitioner_confidentiality_clearance.py
# VERSION: v1.0.0-P47-R95-G38-IMMUTABLE-CLEARANCE-EVIDENCE
# AUTHORITY BOUNDARY: documentary clearance state only; no issuer, ethical-wall verification or operational permission
# TENANT POSTURE: exact tenant, matter and practitioner; cross-scope history corrupt-blocked
# FAIL-CLOSED POSTURE: unknown, revoked, denied, expired or corrupt evidence never permits access
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
