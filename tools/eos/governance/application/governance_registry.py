from __future__ import annotations

"""
===============================================================================
WILSY OS KERNEL — GOVERNANCE REGISTRY SERVICE (FG177)
===============================================================================
Epitome:
    Thread-safe repository for governance policies and kernel engine registration.

Biblical Worth Billions:
    "Set thee up waymarks, make thee high heaps: set thine heart toward the highway."
    (Jeremiah 31:21). Centralized, thread-safe institutional policy store.

Collaboration & Ownership:
    - Lead Architect & Founder: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Enterprise Legal Document Infrastructure
    - Phase / Milestone: FG177 - Kernel Governance Gate
    - Target Directory: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/application/
    - File Path: tools/eos/governance/application/governance_registry.py
===============================================================================
"""

from threading import RLock
from typing import Any, Dict, List, Optional

from tools.eos.governance.domain.governance_policy import (
    EnforcementMode,
    GovernancePolicy,
)


class GovernanceRegistry:
    """Thread-safe policy registry and kernel engine coordinator."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._policies: Dict[str, GovernancePolicy] = {}
        self._registered_engines: Dict[str, Dict[str, Any]] = {}

    def register_policy(self, policy: GovernancePolicy) -> None:
        with self._lock:
            self._policies[policy.policy_id] = policy

    def get_policy(self, policy_id: str) -> Optional[GovernancePolicy]:
        with self._lock:
            return self._policies.get(policy_id)

    def get_all_policies(self) -> List[GovernancePolicy]:
        with self._lock:
            return [
                p for p in self._policies.values()
                if p.enforcement_mode != EnforcementMode.DISABLED
            ]

    def register_engine(self, engine_id: str, engine_instance: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Registers Governance as an active engine in the central Wilsy OS Kernel registry."""
        with self._lock:
            self._registered_engines[engine_id] = {
                "instance": engine_instance,
                "metadata": metadata or {},
            }

    def count(self) -> int:
        with self._lock:
            return len(self._policies)
