"""
===============================================================================
WILSY OS — INSTITUTIONAL VERSIONING ENGINE (FG209)
MODULE: AUTOMATED VERSION POLICY ENFORCER
===============================================================================
Epitome:
    Automated governance and CI/CD guardrail. Enforces breaking-change approval
    policies, prevents usage of deprecated/removed entities, and enforces system
    sunsetting constraints prior to runtime execution.

Biblical Worth Billions:
    "Let all things be done decently and in order." — 1 Corinthians 14:40

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/versioning/version_policy_enforcer.py
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List

from tools.eos.versioning.version_identifier import VersionIdentifier
from tools.eos.versioning.version_registry import VersionRegistry, VersionNotFoundError
from tools.eos.versioning.version_comparator import VersionComparator


class PolicyViolationError(PermissionError):
    """Raised when a deployment or runtime invocation violates versioning policy."""
    pass


@dataclass(frozen=True)
class PolicyEvaluationResult:
    """Outcome of a version policy evaluation pass."""
    passed: bool
    violations: List[str]


class VersionPolicyEnforcer:
    """
    Evaluates operational requests against institutional software governance policies.
    """

    def __init__(self, registry: VersionRegistry, allow_deprecated: bool = False) -> None:
        self.registry = registry
        self.allow_deprecated = allow_deprecated

    def enforce_execution_allowed(self, urn: str) -> None:
        """
        Validates whether an entity URN is legally permitted to execute in production.
        
        Raises:
            PolicyViolationError: If entity is removed or deprecated (and allow_deprecated=False).
            VersionNotFoundError: If URN is not registered.
        """
        record = self.registry.get_record(urn)

        if record.is_removed:
            raise PolicyViolationError(
                f"Execution Blocked: Entity version '{urn}' has been officially REMOVED from Wilsy OS."
            )

        if record.is_deprecated and not self.allow_deprecated:
            reason = record.deprecation_reason or "No reason provided."
            raise PolicyViolationError(
                f"Execution Blocked: Entity version '{urn}' is DEPRECATED. Reason: {reason}"
            )

    def validate_upgrade_path(
        self, 
        current_urn: str, 
        target_urn: str, 
        breaking_change_approved: bool = False
    ) -> PolicyEvaluationResult:
        """
        Evaluates whether upgrading an entity from current_urn to target_urn is compliant.
        
        Args:
            current_urn: Active URN in production.
            target_urn: Target URN proposed for deployment.
            breaking_change_approved: Explicit flag indicating executive sign-off for major bumps.
        """
        current_id = VersionIdentifier.parse_urn(current_urn)
        target_id = VersionIdentifier.parse_urn(target_urn)

        violations: List[str] = []

        if current_id.name != target_id.name or current_id.kind != target_id.kind:
            violations.append(f"Mismatched entities: Cannot upgrade '{current_id.short_id}' to '{target_id.short_id}'.")
            return PolicyEvaluationResult(passed=False, violations=violations)

        is_breaking = VersionComparator.is_breaking_change(current_id.version, target_id.version)

        if is_breaking and not breaking_change_approved:
            violations.append(
                f"Breaking change detected from '{current_id.version}' to '{target_id.version}'. "
                f"Major version upgrade requires explicit executive approval."
            )

        if VersionComparator.is_older(current_id.version, target_id.version):
            violations.append(
                f"Rollback policy restriction: Target version '{target_id.version}' is older than "
                f"current active version '{current_id.version}'."
            )

        return PolicyEvaluationResult(passed=len(violations) == 0, violations=violations)
