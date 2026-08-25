"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Policy Engine - Evaluates repository artifacts against institutional governance rules (FG165).
    Orchestrates policy loading, validation, and enforcement across Wilsy OS.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready policy evaluation pipeline. Zero child's place.
    Psalm 119:105 - "Your word is a lamp to my feet and a light to my path."

Collaboration & Maintenance:
    - [Architecture]: Master coordinator for policy evaluation and compliance verification.
    - [Compliance]: Zero-tolerance adherence to institutional code standards and security requirements.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from tools.eos.policy.policy_models import PolicyRule, PolicyViolation, PolicyEvaluationResult
from tools.eos.policy.policy_registry import PolicyRegistry
from tools.eos.policy.policy_loader import PolicyLoader
from tools.eos.policy.policy_validator import PolicyValidator

logger = logging.getLogger("WilsyOS.PolicyEngine")


class PolicyEngine:
    """
    Orchestrates policy loading, validation, and enforcement across the Wilsy OS repository.
    """

    def __init__(
        self,
        registry: Optional[PolicyRegistry] = None,
        workspace_root: Union[Path, str] = "."
    ) -> None:
        """
        Initializes the PolicyEngine with an optional policy registry and workspace root.

        Args:
            registry (Optional[PolicyRegistry]): Rule registry instance.
            workspace_root (Path | str): Root directory of the repository.
        """
        self.registry = registry or PolicyRegistry()
        self.workspace_root = Path(workspace_root).resolve()

    # [FUNCTION EXPLANATION]: Evaluates a file and its metadata against registered registry rules.
    def evaluate_file(
        self,
        file_path: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PolicyEvaluationResult:
        """
        Evaluates a code or document file against all registered policies in the registry.

        Args:
            file_path (str): Path of the file.
            content (str): Full text content of the file.
            metadata (Optional[Dict[str, Any]]): Additional target metadata (e.g. complexity).

        Returns:
            PolicyEvaluationResult: Evaluation outcome containing violations and warnings.
        """
        meta = metadata or {}
        rules = self.registry.list_all()
        violations: List[PolicyViolation] = []
        warnings: List[PolicyViolation] = []

        file_size_bytes = len(content.encode("utf-8"))
        file_lines = len(content.splitlines())
        file_name = os.path.basename(file_path)

        for rule in rules:
            # 1. Maximum File Size / Line Count Rule
            if rule.category == "size":
                max_bytes = rule.parameters.get("max_bytes")
                max_lines = rule.parameters.get("max_lines")
                if max_bytes and file_size_bytes > max_bytes:
                    v = PolicyViolation(rule.rule_id, file_path, f"File size {file_size_bytes} bytes exceeds max {max_bytes} bytes", rule.severity)
                    if rule.severity == "ERROR":
                        violations.append(v)
                    else:
                        warnings.append(v)
                if max_lines and file_lines > max_lines:
                    v = PolicyViolation(rule.rule_id, file_path, f"File lines {file_lines} exceeds max {max_lines}", rule.severity)
                    if rule.severity == "ERROR":
                        violations.append(v)
                    else:
                        warnings.append(v)

            # 2. Maximum Complexity Rule
            elif rule.category == "complexity":
                max_comp = rule.parameters.get("max_complexity")
                actual_comp = meta.get("complexity", 1)
                if max_comp and actual_comp > max_comp:
                    v = PolicyViolation(rule.rule_id, file_path, f"Complexity {actual_comp} exceeds max {max_comp}", rule.severity)
                    if rule.severity == "ERROR":
                        violations.append(v)
                    else:
                        warnings.append(v)

            # 3. Naming Standards Rule
            elif rule.category == "naming":
                pattern = rule.parameters.get("pattern")
                if pattern and not re.match(pattern, file_name):
                    v = PolicyViolation(rule.rule_id, file_path, f"Filename '{file_name}' does not match standard pattern '{pattern}'", rule.severity)
                    if rule.severity == "ERROR":
                        violations.append(v)
                    else:
                        warnings.append(v)

            # 4. Release Requirements Rule
            elif rule.category == "release":
                required_markers = rule.parameters.get("required_markers", [])
                for marker in required_markers:
                    if marker not in content:
                        v = PolicyViolation(rule.rule_id, file_path, f"Missing required release marker: '{marker}'", rule.severity)
                        if rule.severity == "ERROR":
                            violations.append(v)
                        else:
                            warnings.append(v)

        passed = len(violations) == 0
        return PolicyEvaluationResult(
            target_id=file_path,
            passed=passed,
            violations=tuple(violations),
            warnings=tuple(warnings),
        )

    # [FUNCTION EXPLANATION]: Evaluates repository workspace against institutional policy sets.
    def evaluate_policies(self, policy_source: Union[str, Path] = "default_governance") -> Dict[str, Any]:
        """
        Evaluates the workspace against a specified institutional policy set.

        Args:
            policy_source (str | Path): Identifier or file path of the policy set to evaluate.

        Returns:
            Dict[str, Any]: Comprehensive policy evaluation verdict report.
        """
        try:
            policy_data = PolicyLoader.load_policy(policy_source)
            validation_result = PolicyValidator.validate_compliance(policy_data, self.workspace_root)

            is_compliant = validation_result.get("compliant", False)
            status = "COMPLIANT" if is_compliant else "VIOLATION_DETECTED"

            return {
                "policy_source": str(policy_source),
                "status": status,
                "validation_details": validation_result,
                "comments": "Policy engine evaluated workspace with absolute institutional rigor.",
            }
        except Exception as e:
            logger.error(f"Policy evaluation failed for source {policy_source}: {e}")
            return {
                "policy_source": str(policy_source),
                "status": "EVALUATION_ERROR",
                "error": str(e),
                "validation_details": {"compliant": False, "violations": [str(e)]},
                "comments": "Policy evaluation aborted due to structural or IO error.",
            }
