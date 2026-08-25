"""
===============================================================================
WILSY OS — FG224 AUTONOMOUS OPERATIONS ENGINE
POLICY SUBSYSTEM: APPROVAL LEVELS
===============================================================================

File Path:
    tools/eos/autonomous/policy/approval_levels.py

Version:
    v224.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Defines institutional approval tiers, governance ordering, human intervention
    triggers, and escalation semantics for governed autonomous action execution.

Biblical Worth Billions:
    "Let every soul be subject unto the higher powers. For there is no power 
    but of God: the powers that be are ordained of God."
    — Romans 13:1

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

import enum
import os
import sys
from typing import Any, Dict, List, Tuple

# --- ABSOLUTE PATH BOOTSTRAP GUARANTEE ---
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", "..", "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


class ApprovalLevel(str, enum.Enum):
    """
    Hierarchical institutional approval levels required for executing actions.
    """
    AUTO_APPROVED = "AUTO_APPROVED"
    AUTOMATIC = "AUTOMATIC"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CHIEF_ARCHITECT = "CHIEF_ARCHITECT"
    BOARD = "BOARD"


# Explicit numeric rank hierarchy mapping for deterministic comparisons
APPROVAL_LEVEL_WEIGHTS: Dict[ApprovalLevel, int] = {
    ApprovalLevel.AUTO_APPROVED: 0,
    ApprovalLevel.AUTOMATIC: 0,
    ApprovalLevel.LOW: 1,
    ApprovalLevel.MEDIUM: 2,
    ApprovalLevel.HIGH: 3,
    ApprovalLevel.CHIEF_ARCHITECT: 4,
    ApprovalLevel.BOARD: 5,
}


def get_approval_level_weight(level: ApprovalLevel) -> int:
    """
    Returns the numeric weight of a given ApprovalLevel for priority comparisons.
    """
    return APPROVAL_LEVEL_WEIGHTS.get(level, 99)


def requires_human_approval(level: ApprovalLevel) -> bool:
    """
    Determines if an approval level requires explicit manual human sign-off.
    """
    return level in (
        ApprovalLevel.MEDIUM,
        ApprovalLevel.HIGH,
        ApprovalLevel.CHIEF_ARCHITECT,
        ApprovalLevel.BOARD,
    )


def is_approval_sufficient(granted: ApprovalLevel, required: ApprovalLevel) -> bool:
    """
    Validates whether granted approval level meets or exceeds the required level.
    """
    return get_approval_level_weight(granted) >= get_approval_level_weight(required)


def determine_approval_level_from_risk(risk_score: float) -> ApprovalLevel:
    """
    Maps a calculated risk score (0.0 to 100.0) to an institutional ApprovalLevel.
    """
    if risk_score < 10.0:
        return ApprovalLevel.AUTO_APPROVED
    elif risk_score < 30.0:
        return ApprovalLevel.LOW
    elif risk_score < 60.0:
        return ApprovalLevel.MEDIUM
    elif risk_score < 85.0:
        return ApprovalLevel.HIGH
    elif risk_score < 95.0:
        return ApprovalLevel.CHIEF_ARCHITECT
    else:
        return ApprovalLevel.BOARD


if __name__ == "__main__":
    # Self-verification test block
    print("✅ Testing ApprovalLevel hierarchy & risk mapping...")

    # Test weight ordering
    assert get_approval_level_weight(ApprovalLevel.AUTO_APPROVED) == 0
    assert get_approval_level_weight(ApprovalLevel.BOARD) == 5

    # Test human approval triggers
    assert not requires_human_approval(ApprovalLevel.AUTO_APPROVED)
    assert not requires_human_approval(ApprovalLevel.LOW)
    assert requires_human_approval(ApprovalLevel.CHIEF_ARCHITECT)
    assert requires_human_approval(ApprovalLevel.BOARD)

    # Test approval sufficiency
    assert is_approval_sufficient(
        granted=ApprovalLevel.CHIEF_ARCHITECT,
        required=ApprovalLevel.HIGH
    )
    assert not is_approval_sufficient(
        granted=ApprovalLevel.LOW,
        required=ApprovalLevel.HIGH
    )

    # Test risk score mapping
    assert determine_approval_level_from_risk(5.0) == ApprovalLevel.AUTO_APPROVED
    assert determine_approval_level_from_risk(45.0) == ApprovalLevel.MEDIUM
    assert determine_approval_level_from_risk(90.0) == ApprovalLevel.CHIEF_ARCHITECT
    assert determine_approval_level_from_risk(98.0) == ApprovalLevel.BOARD

    print("  - Approval Level Weights: Verified")
    print("  - Human Intervention Flags: Verified")
    print("  - Risk Score Tier Mapping: Verified")
    print("  - Status: GOLD_PRODUCTION_READY")
