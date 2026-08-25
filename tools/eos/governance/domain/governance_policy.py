from __future__ import annotations

"""
===============================================================================
WILSY OS KERNEL — GOVERNANCE POLICY DOMAIN MODEL (FG177)
===============================================================================
Epitome:
    Domain entities defining institutional governance rules, severity levels,
    and enforcement behavior.

Biblical Worth Billions:
    "To do justice and judgment is more acceptable to the Lord than sacrifice."
    (Proverbs 21:3). Strict rule boundary definitions with cryptographic integrity.

Collaboration & Ownership:
    - Lead Architect & Founder: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Enterprise Legal Document Infrastructure
    - Phase / Milestone: FG177 - Kernel Governance Gate
    - Target Directory: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/domain/
    - File Path: tools/eos/governance/domain/governance_policy.py
===============================================================================
"""

import hashlib
import json
from enum import Enum
from typing import Any, Dict, List, Optional


class PolicySeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class EnforcementMode(str, Enum):
    STRICT = "STRICT"      # Blocks execution immediately on failure
    AUDIT = "AUDIT"        # Flags for review without blocking
    DISABLED = "DISABLED"  # Policy ignored during evaluation


class GovernanceRule:
    """Atomic rule definition evaluated against execution contexts."""

    def __init__(
        self,
        rule_id: str,
        rule_type: str,
        params: Dict[str, Any],
        description: str = "",
    ) -> None:
        self.rule_id = rule_id
        self.rule_type = rule_type
        self.params = params
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_type": self.rule_type,
            "params": self.params,
            "description": self.description,
        }


class GovernancePolicy:
    """Institutional policy containing one or more compliance rules."""

    def __init__(
        self,
        policy_id: str,
        name: str,
        description: str,
        version: str = "1.0.0",
        severity: PolicySeverity = PolicySeverity.HIGH,
        enforcement_mode: EnforcementMode = EnforcementMode.STRICT,
        rules: Optional[List[GovernanceRule]] = None,
    ) -> None:
        self.policy_id = policy_id
        self.name = name
        self.description = description
        self.version = version
        self.severity = severity
        self.enforcement_mode = enforcement_mode
        self.rules: List[GovernanceRule] = rules or []

    def compute_integrity_hash(self) -> str:
        payload = {
            "policy_id": self.policy_id,
            "version": self.version,
            "severity": self.severity.value,
            "enforcement_mode": self.enforcement_mode.value,
            "rules": [r.to_dict() for r in self.rules],
        }
        raw_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw_bytes).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "severity": self.severity.value,
            "enforcement_mode": self.enforcement_mode.value,
            "integrity_hash": self.compute_integrity_hash(),
            "rules": [r.to_dict() for r in self.rules],
        }
