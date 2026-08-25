"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Core Framework - Engine Lifecycle Protocol.
    Defines institutional lifecycle hooks for initialization, execution, teardown,
    and recovery across Wilsy OS engines.

Biblical Scale & Architecture:
    Production-ready enterprise lifecycle protocol. Zero child's place.
    Enforces standardized state transition hooks for all executing components.

Collaboration & Maintenance:
    - [Architecture]: Abstract protocol defining mandatory engine lifecycle hooks.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class EngineLifecycle(ABC):
    """
    Abstract protocol establishing standard lifecycle hooks for institutional engines.
    """

    @abstractmethod
    def initialize(self, context: Dict[str, Any]) -> None:
        """
        Initialize engine resources, connections, and state prior to execution.

        Args:
            context (Dict[str, Any]): Execution context and shared state.
        """
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute core engine logic.

        Args:
            context (Dict[str, Any]): Execution context and shared state.

        Returns:
            Any: Engine execution result data.
        """
        pass

    @abstractmethod
    def teardown(self, context: Dict[str, Any]) -> None:
        """
        Release engine resources, close connections, and clean up state after execution.

        Args:
            context (Dict[str, Any]): Execution context and shared state.
        """
        pass

    def rollback(self, context: Dict[str, Any], error: Exception) -> None:
        """
        Rollback engine state in the event of an execution failure.

        Args:
            context (Dict[str, Any]): Execution context and shared state.
            error (Exception): The exception that triggered the rollback.
        """
        pass
