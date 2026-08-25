"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Execution Contracts Framework - Execution Contract.
    Defines the immutable core contract for executing pipeline phases and orchestrating
    subsystems across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise execution contract. Zero child's place.
    Enforces strict typing, thread-safe execution, and immutable state passage.

Collaboration & Maintenance:
    - [Architecture]: Pure protocol definition for kernel execution pipelines.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ...runtime.context import ExecutionContext


class ExecutionContract(ABC):
    """
    Base institutional contract implemented by execution orchestrators and pipeline runners.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The canonical identifier of the execution component."""
        raise NotImplementedError

    @property
    @abstractmethod
    def version(self) -> str:
        """The semantic version of the execution contract implementation."""
        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
        context: ExecutionContext,
    ) -> Any:
        """
        Execute the pipeline step or orchestration workflow using the shared execution context.

        Args:
            context (ExecutionContext): The unified, immutable runtime context.

        Returns:
            Any: The resulting execution artifact or telemetry report.
        """
        raise NotImplementedError
