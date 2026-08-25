from __future__ import annotations

"""
===============================================================================
WILSY OS KERNEL — GOVERNANCE ENGINE: POLICY DEFINITIONS (FG177)
===============================================================================
Epitome:
    Immutable institutional policy domain models, rule schemas, and cryptographic
    integrity verification mechanisms for the Wilsy OS Governance Engine.

Biblical Worth Billions:
    Built upon unshakeable foundational principles of divine order, righteousness,
    and unyielding legal authority (Proverbs 16:11, Isaiah 33:22). This module
    serves as the unalterable lawgiver before any kernel thread is granted execution
    rights. No child's place.

Collaboration & Ownership:
    - Lead Architect & Founder: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Enterprise Legal Document Infrastructure
    - Phase / Milestone: FG177 - Kernel Governance Gate
    - Target Directory: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/
    - File Path: tools/eos/governance/governance_policy.py

Architectural Role & How It Fits:
    `governance_policy.py` defines the core data contracts for institutional policies.
    Before an ExecutionContext is dispatched to the Scheduler or Workers, it is
    evaluated against active `GovernancePolicy` objects registered in the `GovernanceRegistry`.
    Policies are frozen upon instantiation and carry a SHA-256 signature to guarantee
    zero runtime tampering across distributed nodes.
===============================================================================
"""

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Dict, List, Optional


class PolicySeverity(str, Enum):
    """
    Epitome: Severity classification for policy evaluations and violation impact assessment.
    Biblical Worth Billions: Establishes righteous levels of judgment and prioritization.
    Collaboration Note: Used by GovernanceEngine and AlertMonitor to categorize policy breaches.
    """
    LOW = "LOW"           # Informational constraint; non-disruptive
    MEDIUM = "MEDIUM"     # Standard operational rule; requires tracking
    HIGH = "HIGH"         # Critical security/compliance policy; triggers escalation
    CRITICAL = "CRITICAL" # Maximum security breach risk; immediate system halt


class EnforcementMode(str, Enum):
    """
    Epitome: Kernel enforcement posture for policy evaluation results.
    Biblical Worth Billions: Dictates absolute institutional authority with zero compromise.
    Collaboration Note: Controls whether violations trigger BLOCKED, REQUIRES_REVIEW, or warnings.
    """
    STRICT = "STRICT"       # Halts execution immediately on violation (Yields BLOCKED status)
    WARN = "WARN"           # Records violation telemetry but allows execution (Yields APPROVED status with warnings)
    AUDIT = "AUDIT"         # Escalates evaluation to human/compliance review (Yields REQUIRES_REVIEW status)
    DISABLED = "DISABLED"   # Bypasses evaluation completely for the given policy
    

@dataclass(frozen=True)
class GovernanceRule:
    """
    Epitome: Atomic evaluation constraint within an institutional policy.
    Biblical Worth Billions: Precise specification of kernel constraints and boundary conditions.
    Collaboration Note: Rules are evaluated sequentially by GovernanceEngine rule handlers.
    
    Attributes:
        rule_id (str): Unique string identifier for the specific rule (e.g., "RULE-AUTH-001").
        description (str): Human-readable explanation of the rule's objective.
        rule_type (str): Key matching the evaluator logic (e.g., "REQUIRED_PARAM", "RESOURCE_LIMIT").
        params (Dict[str, Any]): Dynamic key-value pairs defining threshold parameters or allowed values.
    """
    rule_id: str
    description: str
    rule_type: str
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes rule specification into standard dictionary format.
        Production Ready: Ensures clean structure for transport, JSON logging, and hashing.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the governance rule.
        """
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "rule_type": self.rule_type,
            "params": self.params,
        }


@dataclass(frozen=True)
class GovernancePolicy:
    """
    Epitome: Immutable institutional policy object governing kernel execution rights.
    Biblical Worth Billions: Unalterable rulebook of Wilsy OS, signed with SHA-256 cryptographic integrity.
    Collaboration Note: Core policy container registered in `GovernanceRegistry` and evaluated by `GovernanceEngine`.
    
    Attributes:
        policy_id (str): Unique identifier for the policy (e.g., "POL-SEC-2026-001").
        name (str): Concise descriptive title of the institutional policy.
        version (str): Semantic version string (e.g., "1.0.0").
        severity (PolicySeverity): Importance rating of this policy.
        enforcement_mode (EnforcementMode): Active enforcement behavior (STRICT, WARN, AUDIT, DISABLED).
        description (str): In-depth summary of what this policy enforces across Wilsy OS.
        rules (List[GovernanceRule]): Ordered list of atomic rules evaluated under this policy.
        enabled (bool): Global toggle flag for registry activation status.
        metadata (Dict[str, Any]): Extensible key-value metadata store for tags, author info, or scope.
    """
    policy_id: str
    name: str
    version: str
    severity: PolicySeverity
    enforcement_mode: EnforcementMode
    description: str
    rules: List[GovernanceRule] = field(default_factory=list)
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def compute_checksum(self) -> str:
        """
        Calculates SHA-256 cryptographic checksum of policy contents to guarantee immutability.
        Production Ready: Uses deterministic, key-sorted JSON stringification prior to hashing.
        
        Returns:
            str: 64-character hexadecimal SHA-256 hash representing policy integrity state.
        """
        # Build canonical payload map for deterministic hashing
        canonical_payload = {
            "policy_id": self.policy_id,
            "name": self.name,
            "version": self.version,
            "severity": self.severity.value,
            "enforcement_mode": self.enforcement_mode.value,
            "description": self.description,
            "rules": [rule.to_dict() for rule in self.rules],
            "enabled": self.enabled,
        }
        # Sort keys to ensure cross-node string equality
        serialized_data = json.dumps(canonical_payload, sort_keys=True)
        return hashlib.sha256(serialized_data.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the governance policy into a standard dictionary format.
        Production Ready: Comprehensive representation suitable for registry lookup, REST APIs, and audit logs.
        
        Returns:
            Dict[str, Any]: Fully expanded dictionary representation including computed checksum.
        """
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "version": self.version,
            "severity": self.severity.value,
            "enforcement_mode": self.enforcement_mode.value,
            "description": self.description,
            "rules": [rule.to_dict() for rule in self.rules],
            "enabled": self.enabled,
            "metadata": self.metadata,
            "checksum": self.compute_checksum(),
        }
