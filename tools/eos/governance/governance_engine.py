from __future__ import annotations

"""
===============================================================================
WILSY OS KERNEL — GOVERNANCE ENGINE: EVALUATION CORE (FG177)
===============================================================================
Epitome:
    High-performance, deterministic policy evaluation engine for validating
    execution contexts against institutional governance policies in Wilsy OS.

Biblical Worth Billions:
    Righteous judgment rendered with absolute speed, unwavering precision, and 
    zero compromise (Psalm 89:14, Proverbs 16:11). Guarantees that every execution
    intent is weighed on divine balances before kernel allocation. No child's place.

Collaboration & Ownership:
    - Lead Architect & Founder: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Enterprise Legal Document Infrastructure
    - Phase / Milestone: FG177 - Kernel Governance Gate
    - Target Directory: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/
    - File Path: tools/eos/governance/governance_engine.py

Architectural Role & How It Fits:
    `governance_engine.py` is the execution point of the governance gate.
    When a request enters the kernel, `GovernanceEngine.evaluate()` processes the
    request's context dictionary against all active policies in the `GovernanceRegistry`.
    It outputs a `GovernanceDecision` artifact (`APPROVED`, `BLOCKED`, or `REQUIRES_REVIEW`)
    which determines whether the scheduler allows execution to proceed.
===============================================================================
"""

from datetime import datetime, timezone
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple

from tools.eos.governance.governance_decision import GovernanceDecision, GovernanceStatus
from tools.eos.governance.governance_policy import (
    EnforcementMode,
    GovernancePolicy,
    GovernanceRule,
    PolicySeverity,
)
from tools.eos.governance.governance_registry import GovernanceRegistry

logger = logging.getLogger(__name__)


class GovernanceEngine:
    """
    Epitome: Evaluation engine processing runtime contexts against institutional policies.
    Biblical Worth Billions: The supreme lawgiver engine enforcing system integrity.
    Collaboration Note: Invoked by Kernel Gatekeepers prior to worker thread dispatch.
    """

    def __init__(self, registry: Optional[GovernanceRegistry] = None) -> None:
        """
        Initializes the GovernanceEngine with a policy registry instance.

        Args:
            registry (Optional[GovernanceRegistry]): Target registry. Creates new if None.
        """
        self.registry = registry if registry is not None else GovernanceRegistry()

    def evaluate(self, execution_id: str, context: Dict[str, Any]) -> GovernanceDecision:
        """
        Evaluates an execution context against all active policies in the registry.
        Production Ready: Complete policy traversal with strict/audit posture resolution.

        Args:
            execution_id (str): Unique tracking identifier for the execution context.
            context (Dict[str, Any]): Dynamic key-value map representing execution parameters.

        Returns:
            GovernanceDecision: Sealed authorization disposition artifact.
        """
        decision_id = f"DEC-{uuid.uuid4().hex[:12].upper()}"
        active_policies = self.registry.get_active_policies()

        if not active_policies:
            logger.info(f"No active policies found in registry. Defaulting execution '{execution_id}' to APPROVED.")
            return GovernanceDecision(
                decision_id=decision_id,
                execution_id=execution_id,
                status=GovernanceStatus.APPROVED,
                approval_reason="No active policies in registry; default pass-through.",
            )

        violated_policies: List[Dict[str, Any]] = []
        warnings: List[str] = []
        has_strict_block = False
        has_audit_trigger = False

        for policy in active_policies:
            if policy.enforcement_mode == EnforcementMode.DISABLED:
                continue

            policy_violations: List[Dict[str, Any]] = []

            for rule in policy.rules:
                passed, error_msg = self._evaluate_rule(rule, context)
                if not passed:
                    policy_violations.append({
                        "rule_id": rule.rule_id,
                        "description": rule.description,
                        "error": error_msg,
                    })

            if policy_violations:
                violation_record = {
                    "policy_id": policy.policy_id,
                    "name": policy.name,
                    "severity": policy.severity.value,
                    "enforcement_mode": policy.enforcement_mode.value,
                    "failed_rules": policy_violations,
                }

                if policy.enforcement_mode == EnforcementMode.STRICT:
                    has_strict_block = True
                    violated_policies.append(violation_record)
                    logger.warning(
                        f"STRICT Policy violation on '{policy.policy_id}' for execution '{execution_id}'."
                    )
                elif policy.enforcement_mode == EnforcementMode.AUDIT:
                    has_audit_trigger = True
                    violated_policies.append(violation_record)
                    logger.info(
                        f"AUDIT Policy trigger on '{policy.policy_id}' for execution '{execution_id}'."
                    )
                elif policy.enforcement_mode == EnforcementMode.WARN:
                    for v in policy_violations:
                        warnings.append(f"[{policy.policy_id}:{v['rule_id']}] {v['error']}")
                    logger.info(
                        f"WARN Policy recorded non-blocking violation on '{policy.policy_id}'."
                    )

        # Resolve final status based on aggregated enforcement postures
        if has_strict_block:
            final_status = GovernanceStatus.BLOCKED
            reason = "Execution blocked due to STRICT policy violations."
        elif has_audit_trigger:
            final_status = GovernanceStatus.REQUIRES_REVIEW
            reason = "Execution requires compliance review due to AUDIT policy triggers."
        else:
            final_status = GovernanceStatus.APPROVED
            reason = "Execution complies with all active governance policies."

        return GovernanceDecision(
            decision_id=decision_id,
            execution_id=execution_id,
            status=final_status,
            violated_policies=violated_policies,
            warnings=warnings,
            approval_reason=reason,
            metadata={"evaluated_policies_count": len(active_policies)},
        )

    def _evaluate_rule(self, rule: GovernanceRule, context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Evaluates a single atomic rule against the context.
        Production Ready: Dispatches rule types (REQUIRED_PARAM, RESOURCE_LIMIT, ALLOWED_ROLES).

        Args:
            rule (GovernanceRule): The constraint rule to evaluate.
            context (Dict[str, Any]): Execution context map.

        Returns:
            Tuple[bool, str]: Tuple of (pass_status, error_description).
        """
        rule_type = rule.rule_type.upper()

        if rule_type == "REQUIRED_PARAM":
            param_name = rule.params.get("param")
            if not param_name or param_name not in context or context[param_name] is None:
                return False, f"Missing required context parameter: '{param_name}'"
            return True, ""

        elif rule_type == "RESOURCE_LIMIT":
            param_name = rule.params.get("param")
            max_limit = rule.params.get("max")
            if param_name in context and max_limit is not None:
                val = context[param_name]
                if isinstance(val, (int, float)) and val > max_limit:
                    return False, f"Parameter '{param_name}' value ({val}) exceeds maximum threshold ({max_limit})"
            return True, ""

        elif rule_type == "ALLOWED_ROLES":
            required_roles = rule.params.get("roles", [])
            user_roles = context.get("roles", [])
            if not any(role in user_roles for role in required_roles):
                return False, f"User roles {user_roles} do not satisfy required roles {required_roles}"
            return True, ""

        else:
            # Custom or unrecognized rule types pass by default with a warning log
            logger.debug(f"Unrecognized rule type '{rule_type}' passed by default.")
            return True, ""
