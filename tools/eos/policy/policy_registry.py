"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Policy Registry - Central institutional policy registry and store (FG165).
    Manages active policy definitions, rulebook caching, and domain indexing
    across Wilsy OS engines.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready centralized policy cache and store. Zero child's place.
    1 Corinthians 14:40 - "But all things should be done decently and in order."

Collaboration & Maintenance:
    - [Architecture]: Centralized thread-safe in-memory registry and repository for institutional policies.
    - [Compliance]: Strict validation and safe retrieval of active rulebooks.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import threading
from typing import Dict, Optional, Tuple

from tools.eos.policy.policy_models import PolicyRule

logger = logging.getLogger("WilsyOS.PolicyRegistry")


class PolicyRegistry:
    """
    Central registry storing active policy definitions and rulebooks for instant retrieval
    and execution across the Wilsy OS kernel.
    """

    def __init__(self) -> None:
        """Initializes the thread-safe policy registry."""
        self._registry: Dict[str, PolicyRule] = {}
        self._lock = threading.Lock()

    # [FUNCTION EXPLANATION]: Registers or updates an institutional policy rule into the central store.
    def register(self, rule: PolicyRule) -> None:
        """
        Registers or updates a policy rule in the central registry.

        Args:
            rule (PolicyRule): The policy rule definition object.
        """
        if not rule.rule_id or not isinstance(rule.rule_id, str):
            raise ValueError("Policy rule ID must be a non-empty string.")
        
        with self._lock:
            self._registry[rule.rule_id] = rule
        logger.info(f"Policy successfully registered in kernel registry: [{rule.rule_id}]")

    # [FUNCTION EXPLANATION]: Retrieves a registered policy rule by its unique identifier.
    def get(self, rule_id: str) -> Optional[PolicyRule]:
        """
        Retrieves a registered policy rule by ID.

        Args:
            rule_id (str): The policy identifier to look up.

        Returns:
            Optional[PolicyRule]: Policy rule definition if found, else None.
        """
        with self._lock:
            return self._registry.get(rule_id)

    # [FUNCTION EXPLANATION]: Lists all currently registered policy rules in the system.
    def list_all(self) -> Tuple[PolicyRule, ...]:
        """
        Returns a tuple of all registered policy rules.

        Returns:
            Tuple[PolicyRule, ...]: Tuple of PolicyRule objects.
        """
        with self._lock:
            return tuple(self._registry.values())

    # [FUNCTION EXPLANATION]: Unregisters a policy rule from the registry.
    def unregister(self, rule_id: str) -> bool:
        """
        Removes a policy rule from the registry.

        Args:
            rule_id (str): Policy identifier to remove.

        Returns:
            bool: True if policy was present and removed, False otherwise.
        """
        with self._lock:
            if rule_id in self._registry:
                del self._registry[rule_id]
                logger.info(f"Policy unregistered from kernel registry: [{rule_id}]")
                return True
        return False

    def clear(self) -> None:
        """Clears all registered policies from memory."""
        with self._lock:
            self._registry.clear()
        logger.info("Policy registry cleared.")
