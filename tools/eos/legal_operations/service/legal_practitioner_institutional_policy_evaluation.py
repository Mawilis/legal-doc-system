"""TITLE: WILSY OS G63 Institutional Confidentiality Policy Boundary
VERSION: v1.0.0-G63-FAIL-CLOSED-INSTITUTIONAL-POLICY
AUTHORITY: Python EOS Legal Operations policy-readiness projection only.
EPITOME: Pure deterministic fail-closed status evaluation with no positive
    authorization path, source reads, persistence, IAM grants or live admission.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_practitioner_institutional_policy_evaluation.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering; institutional authority
    decisions remain owned by an authorized institutional governance process.
CERTIFICATION OR UPDATE DATE: 2026-10-26
CHANGELOG:
    2026-10-26 v1.0.0-G63-FAIL-CLOSED-INSTITUTIONAL-POLICY establishes the
    non-authorizing G63 boundary. Caller-supplied labels are not evidence;
    even all-APPROVED labels remain DENY until later ratification and authority
    work is independently certified.
COMPLIANCE: AGENTS.md v1.2.0; ENGINEERING_CONSTITUTION.md v1.1.0; G63 in the
    practitioner confidentiality institutional authority contract.
SECURITY / PRIVACY POSTURE: Pure in-memory evaluation; no network, persistence,
    secret, credential, or source-authority access.
TENANT BOUNDARY: No tenant, matter, practitioner, provider, or caller identity
    is accepted or resolved by this readiness-only boundary.
AUTHORITY BOUNDARY: No institutional ratification, IAM grant, ethical-wall
    clearance, matter-content authorization, or operational admission is created.
FINANCIAL AUTHORITY BOUNDARY: NONE; Kennel EOS remains the exclusive financial
    execution authority.
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
        operational_admission=False,
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


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_practitioner_institutional_policy_evaluation.py
# VERSION: v1.0.0-G63-FAIL-CLOSED-INSTITUTIONAL-POLICY
# AUTHORITY BOUNDARY: non-authorizing policy-readiness projection only
# TENANT POSTURE: no tenant or matter scope is created or inferred
# FAIL-CLOSED POSTURE: every input state returns DENY; operational admission fixed false
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
