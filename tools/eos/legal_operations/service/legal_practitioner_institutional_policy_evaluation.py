"""G63 pure institutional confidentiality policy boundary.

This module is a non-authorizing readiness projection. Its inputs are labels,
not authenticated evidence; it performs no source reads, persistence, IAM
checks, network calls, or operational admission. Even an all-APPROVED projection
returns DENY while institutional ratification and the later G64/G65 authority
work remain outside this code boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final


VERSION: Final[str] = "v1.0.0-G63-FAIL-CLOSED-INSTITUTIONAL-POLICY"
OPERATIONAL_ADMISSION_ENABLED: Final[bool] = False


class InstitutionalEvidenceState(StrEnum):
    """Non-authoritative status labels for required institutional dependencies."""

    UNASSIGNED = "UNASSIGNED"
    UNVERIFIED = "UNVERIFIED"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    REVOKED = "REVOKED"
    STALE = "STALE"
    CONTRADICTORY = "CONTRADICTORY"
    UNAVAILABLE = "UNAVAILABLE"
    INEFFECTIVE = "INEFFECTIVE"


class InstitutionalPolicyDecision(StrEnum):
    """The G63 boundary deliberately has no ALLOW member."""

    DENY = "DENY"


@dataclass(frozen=True, slots=True, kw_only=True)
class InstitutionalPolicyInputs:
    """Readiness labels only; these values are not evidence of real authority."""

    reviewer_authority: InstitutionalEvidenceState = InstitutionalEvidenceState.UNASSIGNED
    wall_policy_authority: InstitutionalEvidenceState = InstitutionalEvidenceState.UNASSIGNED
    wall_enforcement: InstitutionalEvidenceState = InstitutionalEvidenceState.UNASSIGNED
    emergency_denial_authority: InstitutionalEvidenceState = InstitutionalEvidenceState.UNASSIGNED
    confidentiality_source: InstitutionalEvidenceState = InstitutionalEvidenceState.UNASSIGNED
    conflict_source: InstitutionalEvidenceState = InstitutionalEvidenceState.UNASSIGNED
    matter_scope: InstitutionalEvidenceState = InstitutionalEvidenceState.UNASSIGNED
    currentness: InstitutionalEvidenceState = InstitutionalEvidenceState.UNASSIGNED
    institutional_ratification: InstitutionalEvidenceState = InstitutionalEvidenceState.UNASSIGNED

    def __post_init__(self) -> None:
        for name in _INPUT_FIELDS:
            if type(getattr(self, name)) is not InstitutionalEvidenceState:
                raise ValueError("G63_INSTITUTIONAL_EVIDENCE_STATE_INVALID")


@dataclass(frozen=True, slots=True)
class InstitutionalPolicyEvaluation:
    """A deterministic denial projection, never an access decision."""

    decision: InstitutionalPolicyDecision
    reason_codes: tuple[str, ...]
    operational_admission: bool


_INPUT_FIELDS: Final[tuple[str, ...]] = (
    "reviewer_authority",
    "wall_policy_authority",
    "wall_enforcement",
    "emergency_denial_authority",
    "confidentiality_source",
    "conflict_source",
    "matter_scope",
    "currentness",
    "institutional_ratification",
)
_NEGATIVE_STATES: Final[frozenset[InstitutionalEvidenceState]] = frozenset(
    {
        InstitutionalEvidenceState.DENIED,
        InstitutionalEvidenceState.REVOKED,
        InstitutionalEvidenceState.CONTRADICTORY,
        InstitutionalEvidenceState.INEFFECTIVE,
    }
)


def evaluate_institutional_policy_boundary(
    inputs: InstitutionalPolicyInputs,
) -> InstitutionalPolicyEvaluation:
    """Return stable denial reasons; never grant, authorize, read, or persist.

    Explicit negative states receive precedence. Any unassigned, unverified,
    stale, unavailable, or otherwise non-approved dependency also denies.
    If every supplied label says APPROVED, the result still denies because
    this G63 boundary cannot ratify policy or enable operational admission.
    """
    if type(inputs) is not InstitutionalPolicyInputs:
        raise ValueError("G63_INSTITUTIONAL_POLICY_INPUTS_INVALID")

    states = tuple((name, getattr(inputs, name)) for name in _INPUT_FIELDS)
    has_negative = any(state in _NEGATIVE_STATES for _, state in states)
    reasons: list[str] = []
    if has_negative:
        reasons.append("G63_EXPLICIT_NEGATIVE_PRECEDENCE")

    for name, state in states:
        if state is not InstitutionalEvidenceState.APPROVED:
            reasons.append(f"G63_{name.upper()}_{state.value}")

    if not reasons:
        reasons.append("G63_OPERATIONAL_ADMISSION_DISABLED")

    return InstitutionalPolicyEvaluation(
        decision=InstitutionalPolicyDecision.DENY,
        reason_codes=tuple(reasons),
        operational_admission=OPERATIONAL_ADMISSION_ENABLED,
    )


__all__ = [
    "VERSION",
    "OPERATIONAL_ADMISSION_ENABLED",
    "InstitutionalEvidenceState",
    "InstitutionalPolicyDecision",
    "InstitutionalPolicyInputs",
    "InstitutionalPolicyEvaluation",
    "evaluate_institutional_policy_boundary",
]
