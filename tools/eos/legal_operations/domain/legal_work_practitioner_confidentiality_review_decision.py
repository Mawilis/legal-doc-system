"""TITLE: WILSY OS Practitioner Confidentiality Review Decision Domain.
VERSION: v1.0.0-P47-R95-G58-NON-AUTHORIZING-DECISION-FOUNDATION
AUTHORITY: Immutable practitioner-specific confidentiality adjudication evidence.
EPITOME: Records one independently attributable review decision with exact
tenant, matter, practitioner, reviewer-IAM, conflict, screening and ethical-wall
provenance while refusing to convert recorded evidence into operational access.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_work_practitioner_confidentiality_review_decision.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering; future
transactional services must re-read every referenced authority source.
CERTIFICATION / UPDATE DATE: 2026-10-21.
CHANGELOG: 2026-10-21 v1.0.0 introduces the G58 immutable decision and
corruption-first terminal-state projection without reviewer grants or access.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque identifiers and SHA3-512 fingerprints only;
no privileged narrative, client secret, wall membership, or matter content.
TENANT BOUNDARY: Exact tenant, matter and practitioner scope; drift is corrupt.
AUTHORITY BOUNDARY: Recorded approval is unverified evidence, never permission.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import json
import re
from typing import Final, Iterable

VERSION: Final[str] = "v1.0.0-P47-R95-G58-NON-AUTHORIZING-DECISION-FOUNDATION"
SCHEMA: Final[str] = "WILSY-LEGAL-PRACTITIONER-CONFIDENTIALITY-REVIEW/V1"
_ID: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,199}\Z")
_HEX: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{128}\Z")


class ConfidentialityReviewDecisionError(ValueError):
    """Expose one stable content-free domain validation code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class ConfidentialityReviewDecisionState(StrEnum):
    """Closed historical adjudication vocabulary."""

    APPROVED = "APPROVED"
    DENIED = "DENIED"
    REVOKED = "REVOKED"


class EthicalWallRequirement(StrEnum):
    """Record the independently sourced wall-policy determination."""

    REQUIRED = "REQUIRED"
    NOT_REQUIRED = "NOT_REQUIRED"


class ConfidentialityReviewCurrentnessState(StrEnum):
    """Derived evidence states; none conveys operational permission."""

    NO_DECISION = "NO_DECISION"
    APPROVED_RECORDED_UNVERIFIED = "APPROVED_RECORDED_UNVERIFIED"
    DENIED_BLOCKED = "DENIED_BLOCKED"
    REVOKED_BLOCKED = "REVOKED_BLOCKED"
    EXPIRED_BLOCKED = "EXPIRED_BLOCKED"
    CORRUPT_BLOCKED = "CORRUPT_BLOCKED"


def _id(name: str, value: object) -> str:
    if type(value) is not str or _ID.fullmatch(value) is None:
        raise ConfidentialityReviewDecisionError(name.upper() + "_INVALID")
    if name == "tenant_id" and value.casefold() in {"default", "global", "root", "*"}:
        raise ConfidentialityReviewDecisionError("TENANT_ID_INVALID")
    return value


def _optional_id(name: str, value: object) -> str | None:
    if value is None:
        return None
    return _id(name, value)


def _fingerprint(name: str, value: object) -> str:
    if type(value) is not str or _HEX.fullmatch(value) is None:
        raise ConfidentialityReviewDecisionError(name.upper() + "_INVALID")
    return value


def _optional_fingerprint(name: str, value: object) -> str | None:
    if value is None:
        return None
    return _fingerprint(name, value)


def _time(name: str, value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise ConfidentialityReviewDecisionError(name.upper() + "_INVALID")
    result = value.astimezone(timezone.utc)
    if result.microsecond or result != value:
        raise ConfidentialityReviewDecisionError(name.upper() + "_NONCANONICAL")
    return result


@dataclass(frozen=True, slots=True)
class ConfidentialityReviewDecision:
    """Immutable review evidence whose sources require later transactional verification."""

    decision_id: str
    tenant_id: str
    case_matter_id: str
    practitioner_principal_id: str
    reviewer_principal_id: str
    predecessor_decision_id: str | None
    decision: ConfidentialityReviewDecisionState | str
    decided_at: datetime
    expires_at: datetime
    reviewer_authorization_evidence_reference: str
    reviewer_authorization_evidence_fingerprint: str
    conflict_disposition_reference: str
    conflict_disposition_fingerprint: str
    screening_evidence_reference: str
    screening_evidence_fingerprint: str
    ethical_wall_requirement: EthicalWallRequirement | str
    ethical_wall_policy_reference: str | None
    ethical_wall_policy_fingerprint: str | None
    ethical_wall_satisfaction_reference: str | None
    ethical_wall_satisfaction_fingerprint: str | None
    schema: str = SCHEMA
    decision_version: str = VERSION
    fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.decision_version != VERSION:
            raise ConfidentialityReviewDecisionError("IDENTITY_INVALID")
        for name in (
            "decision_id", "tenant_id", "case_matter_id",
            "practitioner_principal_id", "reviewer_principal_id",
            "reviewer_authorization_evidence_reference",
            "conflict_disposition_reference", "screening_evidence_reference",
        ):
            object.__setattr__(self, name, _id(name, getattr(self, name)))
        predecessor = _optional_id("predecessor_decision_id", self.predecessor_decision_id)
        if predecessor == self.decision_id:
            raise ConfidentialityReviewDecisionError("SELF_PREDECESSOR")
        object.__setattr__(self, "predecessor_decision_id", predecessor)
        if self.reviewer_principal_id == self.practitioner_principal_id:
            raise ConfidentialityReviewDecisionError("SELF_REVIEW")
        try:
            decision = ConfidentialityReviewDecisionState(self.decision)
            wall = EthicalWallRequirement(self.ethical_wall_requirement)
        except (TypeError, ValueError) as error:
            raise ConfidentialityReviewDecisionError("DECISION_ENUM_INVALID") from error
        if decision is ConfidentialityReviewDecisionState.REVOKED and predecessor is None:
            raise ConfidentialityReviewDecisionError("REVOCATION_PREDECESSOR_REQUIRED")
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "ethical_wall_requirement", wall)
        start, end = _time("decided_at", self.decided_at), _time("expires_at", self.expires_at)
        if end <= start:
            raise ConfidentialityReviewDecisionError("WINDOW_INVALID")
        object.__setattr__(self, "decided_at", start)
        object.__setattr__(self, "expires_at", end)
        for name in (
            "reviewer_authorization_evidence_fingerprint",
            "conflict_disposition_fingerprint", "screening_evidence_fingerprint",
        ):
            object.__setattr__(self, name, _fingerprint(name, getattr(self, name)))
        policy_ref = _optional_id("ethical_wall_policy_reference", self.ethical_wall_policy_reference)
        policy_fp = _optional_fingerprint("ethical_wall_policy_fingerprint", self.ethical_wall_policy_fingerprint)
        if policy_ref is None or policy_fp is None:
            raise ConfidentialityReviewDecisionError("WALL_POLICY_REQUIRED")
        satisfaction_ref = _optional_id(
            "ethical_wall_satisfaction_reference", self.ethical_wall_satisfaction_reference
        )
        satisfaction_fp = _optional_fingerprint(
            "ethical_wall_satisfaction_fingerprint", self.ethical_wall_satisfaction_fingerprint
        )
        if wall is EthicalWallRequirement.REQUIRED and (
            satisfaction_ref is None or satisfaction_fp is None
        ):
            raise ConfidentialityReviewDecisionError("WALL_SATISFACTION_REQUIRED")
        if wall is EthicalWallRequirement.NOT_REQUIRED and (
            satisfaction_ref is not None or satisfaction_fp is not None
        ):
            raise ConfidentialityReviewDecisionError("WALL_SATISFACTION_FORBIDDEN")
        object.__setattr__(self, "ethical_wall_policy_reference", policy_ref)
        object.__setattr__(self, "ethical_wall_policy_fingerprint", policy_fp)
        object.__setattr__(self, "ethical_wall_satisfaction_reference", satisfaction_ref)
        object.__setattr__(self, "ethical_wall_satisfaction_fingerprint", satisfaction_fp)
        material = {
            name: (getattr(self, name).value if isinstance(getattr(self, name), StrEnum)
                   else getattr(self, name).isoformat() if isinstance(getattr(self, name), datetime)
                   else getattr(self, name))
            for name in self.__dataclass_fields__ if name != "fingerprint"
        }
        raw = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
        object.__setattr__(self, "fingerprint", sha3_512(raw).hexdigest())

    @property
    def permits_operational_access(self) -> bool:
        """Refuse to elevate recorded review evidence into runtime authority."""
        return False


@dataclass(frozen=True, slots=True)
class ConfidentialityReviewCurrentness:
    """Pure historical projection with corruption-first blocking semantics."""

    tenant_id: str
    case_matter_id: str
    practitioner_principal_id: str
    evaluation_time: datetime
    state: ConfidentialityReviewCurrentnessState
    decisive_fingerprint: str | None = None

    @property
    def permits_operational_access(self) -> bool:
        """Never authorize from an in-memory historical projection."""
        return False


def project_confidentiality_review_currentness(
    *, tenant_id: str, case_matter_id: str, practitioner_principal_id: str,
    evaluation_time: datetime, decisions: Iterable[ConfidentialityReviewDecision],
) -> ConfidentialityReviewCurrentness:
    """Validate exact-scope linear history and derive non-authorizing currentness."""
    tenant, matter = _id("tenant_id", tenant_id), _id("case_matter_id", case_matter_id)
    practitioner = _id("practitioner_principal_id", practitioner_principal_id)
    at = _time("evaluation_time", evaluation_time)

    def result(state: ConfidentialityReviewCurrentnessState,
               fingerprint: str | None = None) -> ConfidentialityReviewCurrentness:
        return ConfidentialityReviewCurrentness(tenant, matter, practitioner, at, state, fingerprint)

    corrupt = ConfidentialityReviewCurrentnessState.CORRUPT_BLOCKED
    try:
        history = tuple(decisions)
        if not history:
            return result(ConfidentialityReviewCurrentnessState.NO_DECISION)
        by_id: dict[str, ConfidentialityReviewDecision] = {}
        roots: list[ConfidentialityReviewDecision] = []
        children: dict[str, list[ConfidentialityReviewDecision]] = {}
        for item in history:
            if type(item) is not ConfidentialityReviewDecision or replace(item).fingerprint != item.fingerprint:
                return result(corrupt)
            if (item.tenant_id != tenant or item.case_matter_id != matter
                    or item.practitioner_principal_id != practitioner
                    or item.decision_id in by_id):
                return result(corrupt)
            by_id[item.decision_id] = item
            if item.predecessor_decision_id is None:
                roots.append(item)
            else:
                children.setdefault(item.predecessor_decision_id, []).append(item)
        if len(roots) != 1 or any(len(values) != 1 for values in children.values()):
            return result(corrupt)
        if any(parent not in by_id for parent in children):
            return result(corrupt)
        ordered: list[ConfidentialityReviewDecision] = []
        current = roots[0]
        while True:
            ordered.append(current)
            successors = children.get(current.decision_id, ())
            if not successors:
                break
            successor = successors[0]
            if (successor.decided_at <= current.decided_at
                    or current.decision is not ConfidentialityReviewDecisionState.APPROVED
                    or successor.decision is ConfidentialityReviewDecisionState.APPROVED):
                return result(corrupt)
            current = successor
        if len(ordered) != len(history):
            return result(corrupt)
        effective = [item for item in ordered if item.decided_at <= at]
        if not effective:
            return result(ConfidentialityReviewCurrentnessState.NO_DECISION)
        current = effective[-1]
        if current.decision is ConfidentialityReviewDecisionState.REVOKED:
            return result(ConfidentialityReviewCurrentnessState.REVOKED_BLOCKED, current.fingerprint)
        if current.decision is ConfidentialityReviewDecisionState.DENIED:
            return result(ConfidentialityReviewCurrentnessState.DENIED_BLOCKED, current.fingerprint)
        if at >= current.expires_at:
            return result(ConfidentialityReviewCurrentnessState.EXPIRED_BLOCKED, current.fingerprint)
        return result(
            ConfidentialityReviewCurrentnessState.APPROVED_RECORDED_UNVERIFIED,
            current.fingerprint,
        )
    except Exception:
        return result(corrupt)


__all__ = [
    "VERSION", "SCHEMA", "ConfidentialityReviewDecisionError",
    "ConfidentialityReviewDecisionState", "EthicalWallRequirement",
    "ConfidentialityReviewCurrentnessState", "ConfidentialityReviewDecision",
    "ConfidentialityReviewCurrentness", "project_confidentiality_review_currentness",
]

# ARTIFACT: legal_work_practitioner_confidentiality_review_decision.py
# VERSION: v1.0.0-P47-R95-G58-NON-AUTHORIZING-DECISION-FOUNDATION
# AUTHORITY BOUNDARY: immutable review evidence and pure currentness only
# TENANT POSTURE: exact tenant, matter and practitioner; scope drift corrupt-blocked
# FAIL-CLOSED POSTURE: self-review, missing provenance, forks, tampering, denial, revocation and expiry block
# OPERATIONAL ACCESS / ETHICAL-WALL WAIVER / FINANCIAL AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
