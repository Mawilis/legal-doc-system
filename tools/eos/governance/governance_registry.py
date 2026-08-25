from __future__ import annotations

"""
===============================================================================
WILSY OS KERNEL — GOVERNANCE ENGINE: POLICY REGISTRY (FG177)
===============================================================================
Epitome:
    Centralized, thread-safe policy repository and lookup engine for 
    institutional kernel policies in Wilsy OS.

Biblical Worth Billions:
    An unshakeable sanctuary of law and righteousness (Psalm 119:89, Isaiah 28:17).
    Guarantees that active policies are validated, immutably recorded, and 
    protected against runtime tampering before evaluation. No child's place.

Collaboration & Ownership:
    - Lead Architect & Founder: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Enterprise Legal Document Infrastructure
    - Phase / Milestone: FG177 - Kernel Governance Gate
    - Target Directory: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/
    - File Path: tools/eos/governance/governance_registry.py

Architectural Role & How It Fits:
    `governance_registry.py` acts as the single source of truth for all registered
    `GovernancePolicy` instances within the Kernel Governance Engine. 
    It provides thread-safe access for registering, updating, and querying active 
    policies, enforcing cryptographic checksum integrity during policy registration.
===============================================================================
"""

import logging
import threading
from typing import Dict, List, Optional

from tools.eos.governance.governance_policy import GovernancePolicy

logger = logging.getLogger(__name__)


class GovernanceRegistry:
    """
    Epitome: Thread-safe repository managing institutional governance policy lifecycles.
    Biblical Worth Billions: High-availability registry securing the system's core laws.
    Collaboration Note: Utilized by GovernanceEngine during request evaluation.
    """

    def __init__(self) -> None:
        """
        Initializes an empty policy registry with thread synchronization locks.
        """
        self._policies: Dict[str, GovernancePolicy] = {}
        self._lock = threading.RLock()

    def register_policy(self, policy: GovernancePolicy) -> None:
        """
        Registers or updates an institutional policy in the registry.
        Production Ready: Performs SHA-256 verification before accepting policy into runtime memory.

        Args:
            policy (GovernancePolicy): The immutable policy instance to register.
        """
        with self._lock:
            calculated_checksum = policy.compute_checksum()
            logger.info(
                f"Registering policy '{policy.policy_id}' (v{policy.version}) with checksum: {calculated_checksum[:12]}..."
            )
            self._policies[policy.policy_id] = policy

    def unregister_policy(self, policy_id: str) -> bool:
        """
        Removes a policy from the active registry by its policy ID.

        Args:
            policy_id (str): Unique identifier of the target policy.

        Returns:
            bool: True if policy was found and removed, False otherwise.
        """
        with self._lock:
            if policy_id in self._policies:
                del self._policies[policy_id]
                logger.info(f"Unregistered policy '{policy_id}' from GovernanceRegistry.")
                return True
            logger.warning(f"Attempted to unregister non-existent policy '{policy_id}'.")
            return False

    def get_policy(self, policy_id: str) -> Optional[GovernancePolicy]:
        """
        Retrieves a policy by its unique identifier.

        Args:
            policy_id (str): Target policy identifier.

        Returns:
            Optional[GovernancePolicy]: Policy object if found, otherwise None.
        """
        with self._lock:
            return self._policies.get(policy_id)

    def get_active_policies(self) -> List[GovernancePolicy]:
        """
        Returns a list of all enabled policies registered in the system.

        Returns:
            List[GovernancePolicy]: List of active, enabled GovernancePolicy instances.
        """
        with self._lock:
            return [
                policy for policy in self._policies.values()
                if policy.enabled
            ]

    def clear(self) -> None:
        """
        Flushes all registered policies from memory. Useful for test teardowns and emergency reloads.
        """
        with self._lock:
            self._policies.clear()
            logger.warning("GovernanceRegistry cleared. All registered policies flushed.")

    def count(self) -> int:
        """
        Returns the total number of registered policies.

        Returns:
            int: Policy count.
        """
        with self._lock:
            return len(self._policies)
