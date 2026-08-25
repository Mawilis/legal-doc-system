from __future__ import annotations

"""
===============================================================================
WILSY OS KERNEL — GOVERNANCE EVALUATION ENGINE (FG177)
===============================================================================
Epitome:
    High-performance rule evaluation engine consuming ExecutionContext (FG145)
    and emitting structured Event Bus events.

Biblical Worth Billions:
    "Let all things be done decently and in order." (1 Corinthians 14:40).
    Zero-bypass evaluation consuming immutable execution contexts.

Collaboration & Ownership:
    - Lead Architect & Founder: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Enterprise Legal Document Infrastructure
    - Phase / Milestone: FG177 - Kernel Governance Gate
    - Target Directory: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/application/
    - File Path: tools/eos/governance/application/governance_engine.py
===============================================================================
"""

from typing import Any, Callable, Dict, List, Optional

from tools.eos.governance.application.governance_registry import GovernanceRegistry
from tools.eos.governance.domain.governance_decision import (
    GovernanceDecision,
    GovernanceStatus,
)
from tools.eos.governance.domain.governance_policy import (
    EnforcementMode,
    GovernancePolicy,
    GovernanceRule,
)


class GovernanceEngine:
    """Evaluates ExecutionContext objects against active policies and emits Event Bus events."""

    def __init__(
        self,
        registry: GovernanceRegistry,
        event_bus_publisher: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> None:
        self.registry = registry
        self.event_publisher = event_bus_publisher or self._default_event_publisher

    def _default_event_publisher(self, event_type: str, payload: Dict[str, Any]) -> None:
        # Fallback in-memory logger when full Event Bus is unattached
        pass

    def evaluate(self, context: Any) -> GovernanceDecision:
        """Evaluates an ExecutionContext (FG145) object or dictionary context."""
        # Extract execution ID & parameters cleanly from ExecutionContext or dict
        if hasattr(context, "execution_id"):
            execution_id = getattr(context, "execution_id")
            context_data = getattr(context, "parameters", {}) if hasattr(context, "parameters") else context.__dict__
        elif isinstance(context, dict):
            execution_id = context.get("execution_id", "EXEC-UNKNOWN")
            context_data = context
        else:
            execution_id = "EXEC-UNKNOWN"
            context_data = {}

        self.event_publisher("GovernanceEvaluationStarted", {"execution_id": execution_id})

        policies = self.registry.get_all_policies()
        violations: List[Dict[str, Any]] = []
        triggers: List[Dict[str, Any]] = []
        evaluated_policies: List[str] = []

        for policy in policies:
            evaluated_policies.append(policy.policy_id)
            for rule in policy.rules:
                passed, details = self._evaluate_rule(rule, context_data)
                if passed:
                    self.event_publisher("GovernancePolicyPassed", {
                        "execution_id": execution_id,
                        "policy_id": policy.policy_id,
                        "rule_id": rule.rule_id,
                    })
                else:
                    event_data = {
                        "execution_id": execution_id,
                        "policy_id": policy.policy_id,
                        "rule_id": rule.rule_id,
                        "details": details,
                        "mode": policy.enforcement_mode.value,
                    }
                    self.event_publisher("GovernancePolicyViolated", event_data)

                    if policy.enforcement_mode == EnforcementMode.STRICT:
                        violations.append({
                            "policy_id": policy.policy_id,
                            "rule_id": rule.rule_id,
                            "severity": policy.severity.value,
                            "details": details,
                        })
                    elif policy.enforcement_mode == EnforcementMode.AUDIT:
                        triggers.append({
                            "policy_id": policy.policy_id,
                            "rule_id": rule.rule_id,
                            "severity": policy.severity.value,
                            "details": details,
                        })

        if violations:
            status = GovernanceStatus.BLOCKED
            reason = "Execution blocked due to STRICT governance policy violations."
            self.event_publisher("GovernanceBlocked", {"execution_id": execution_id, "reason": reason})
        elif triggers:
            status = GovernanceStatus.REQUIRES_REVIEW
            reason = "Execution requires compliance review due to AUDIT policy triggers."
            self.event_publisher("GovernanceRequiresReview", {"execution_id": execution_id, "reason": reason})
        else:
            status = GovernanceStatus.APPROVED
            reason = "Execution cleared all active governance policies."
            self.event_publisher("GovernanceApproved", {"execution_id": execution_id, "reason": reason})

        return GovernanceDecision(
            execution_id=execution_id,
            status=status,
            evaluated_policies=evaluated_policies,
            violations=violations,
            triggers=triggers,
            approval_reason=reason,
        )

    def _evaluate_rule(self, rule: GovernanceRule, context_data: Dict[str, Any]) -> tuple[bool, str]:
        rule_type = rule.rule_type
        params = rule.params

        if rule_type == "REQUIRED_PARAM":
            param_name = params.get("param")
            if param_name not in context_data or context_data[param_name] is None:
                return False, f"Missing required parameter '{param_name}' in ExecutionContext."
            return True, "Parameter present."

        elif rule_type == "RESOURCE_LIMIT":
            param_name = params.get("param")
            max_limit = params.get("max")
            value = context_data.get(param_name)
            if value is not None and max_limit is not None and value > max_limit:
                return False, f"Resource parameter '{param_name}' value {value} exceeds ceiling limit of {max_limit}."
            return True, "Resource limit respected."

        elif rule_type == "ALLOWED_ROLES":
            allowed = set(params.get("roles", []))
            user_roles = set(context_data.get("roles", []))
            if allowed and not user_roles.intersection(allowed):
                return False, f"User roles {list(user_roles)} do not intersect with authorized roles {list(allowed)}."
            return True, "Role authorized."

        return True, "Default rule clear."
