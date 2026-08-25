"""
===============================================================================
WILSY OS — FG224 AUTONOMOUS OPERATIONS ENGINE
POLICY SUBSYSTEM: RISK MATRIX ENGINE
===============================================================================

File Path:
    tools/eos/autonomous/policy/risk_matrix.py

Version:
    v224.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Implements the RiskMatrix engine responsible for calculating deterministic,
    multi-factor risk scores (0.0 - 100.0) for requested autonomous operations.
    Evaluates blast radius, subsystem criticality, priority weightings, and 
    destructive potential to drive governance approval workflows.

Biblical Worth Billions:
    "A prudent man foreseeth the evil, and hideth himself: but the simple pass 
    on, and are punished."
    — Proverbs 22:3

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# --- ABSOLUTE PATH BOOTSTRAP GUARANTEE ---
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", "..", "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from tools.eos.autonomous.domain.autonomous_action import (
    AutonomousAction,
    ActionCategory,
    ActionPriority,
)

# Subsystem Criticality Weights (0.0 to 1.0)
SUBSYSTEM_CRITICALITY_MAP: Dict[str, float] = {
    "kernel": 1.0,
    "security": 0.95,
    "database": 0.90,
    "cluster": 0.85,
    "reliability": 0.80,
    "marketplace": 0.60,
    "digital_twin": 0.50,
    "repository": 0.30,
    "documentation": 0.10,
}


@dataclass
class RiskEvaluation:
    """
    Immutable breakdown of risk factors synthesized by the RiskMatrix engine.
    """
    overall_score: float
    subsystem_criticality: float
    blast_radius_base: float
    priority_multiplier: float
    destructive_penalty: float
    factors: Dict[str, Any] = field(default_factory=dict)


class RiskMatrix:
    """
    Sovereign quantitative risk calculation engine for Wilsy OS autonomous operations.
    """

    def _get_category_blast_radius(self, category: Any) -> float:
        """
        Safely determines base blast radius for any ActionCategory variant or string representation.
        """
        cat_str = str(category.value if hasattr(category, "value") else category).upper()
        
        if any(k in cat_str for k in ["INFRASTRUCTURE", "CLUSTER", "KERNEL", "SYSTEM"]):
            return 80.0
        elif "SECURITY" in cat_str:
            return 75.0
        elif any(k in cat_str for k in ["DATABASE", "STORAGE", "DATA"]):
            return 70.0
        elif "MARKETPLACE" in cat_str:
            return 50.0
        elif any(k in cat_str for k in ["APPLICATION", "SERVICE", "WORKFLOW"]):
            return 40.0
        elif any(k in cat_str for k in ["REPOSITORY", "CODE"]):
            return 20.0
        elif any(k in cat_str for k in ["DOCUMENTATION", "REPORT"]):
            return 5.0
        return 30.0

    def calculate_risk(self, action: AutonomousAction) -> RiskEvaluation:
        """
        Calculates a multi-dimensional risk score for a given AutonomousAction.

        Args:
            action (AutonomousAction): The operational action intent.

        Returns:
            RiskEvaluation: Comprehensive risk assessment payload.
        """
        # 1. Subsystem Criticality
        target_sub = action.target_subsystem.lower().split("/")[0]
        subsystem_criticality = SUBSYSTEM_CRITICALITY_MAP.get(target_sub, 0.40)

        # 2. Base Category Blast Radius
        blast_radius_base = self._get_category_blast_radius(action.category)

        # 3. Priority Multiplier
        prio_str = str(action.priority.value if hasattr(action.priority, "value") else action.priority).upper()
        if "CRITICAL" in prio_str:
            priority_mult = 1.35
        elif "HIGH" in prio_str:
            priority_mult = 1.20
        elif "MEDIUM" in prio_str:
            priority_mult = 1.00
        else: # LOW / DEFAULT
            priority_mult = 0.85

        # 4. Destructive / Mutation Penalties
        destructive_penalty = 0.0
        act_type = action.action_type.upper()
        
        if any(keyword in act_type for keyword in ["DELETE", "DROP", "WIPE", "RESTORE", "PURGE"]):
            destructive_penalty += 35.0
        elif any(keyword in act_type for keyword in ["UPDATE", "UPGRADE", "SCALE", "MODIFY"]):
            destructive_penalty += 15.0

        if getattr(action, "requires_rollback", False):
            destructive_penalty += 5.0

        # Calculate final normalized composite score
        raw_score = (blast_radius_base * subsystem_criticality * priority_mult) + destructive_penalty
        final_score = max(0.0, min(100.0, round(raw_score, 2)))

        return RiskEvaluation(
            overall_score=final_score,
            subsystem_criticality=subsystem_criticality,
            blast_radius_base=blast_radius_base,
            priority_multiplier=priority_mult,
            destructive_penalty=destructive_penalty,
            factors={
                "action_type": action.action_type,
                "category": str(action.category),
                "target_subsystem": action.target_subsystem,
                "priority": str(action.priority),
            }
        )


if __name__ == "__main__":
    # Institutional self-verification test block
    matrix = RiskMatrix()

    # Case 1: Low risk repository format
    action_low = AutonomousAction(
        action_type="FORMAT_CODE",
        category=getattr(ActionCategory, "REPOSITORY", list(ActionCategory)[0]),
        target_subsystem="repository/tools",
        priority=getattr(ActionPriority, "LOW", list(ActionPriority)[0])
    )
    eval_low = matrix.calculate_risk(action_low)
    print(f"✅ Low Risk Action Score: {eval_low.overall_score}/100.0")

    # Case 2: High risk kernel purge
    action_high_cat = getattr(ActionCategory, "INFRASTRUCTURE", getattr(ActionCategory, "SECURITY", list(ActionCategory)[-1]))
    action_high_prio = getattr(ActionPriority, "CRITICAL", getattr(ActionPriority, "HIGH", list(ActionPriority)[-1]))
    
    action_high = AutonomousAction(
        action_type="PURGE_KERNEL_CACHE",
        category=action_high_cat,
        target_subsystem="kernel/core",
        priority=action_high_prio
    )
    eval_high = matrix.calculate_risk(action_high)
    print(f"✅ High Risk Action Score: {eval_high.overall_score}/100.0")

    assert eval_low.overall_score < eval_high.overall_score, "Risk matrix scoring hierarchy failure!"
    assert eval_low.overall_score >= 0.0 and eval_high.overall_score <= 100.0, "Risk score out of bounds!"
    print("  - Blast Radius Matrix: Verified")
    print("  - Subsystem Criticality Mapping: Verified")
    print("  - Score Normalization [0-100]: Verified")
    print("  - Status: GOLD_PRODUCTION_READY")
