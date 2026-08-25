"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Execution Contracts Framework - Report Contract.
    Defines the immutable institutional contract for generating and sealing
    unified engineering reports across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise report contract. Zero child's place.
    Enforces structured reporting telemetry using the immutable ExecutionContext matrix.

Collaboration & Maintenance:
    - [Architecture]: Pure protocol definition for reporting subsystems.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ...runtime.context import ExecutionContext


class ReportContract(ABC):
    """
    Base institutional contract implemented by report generation and serialization engines.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The canonical identifier of the report contract component."""
        raise NotImplementedError

    @property
    @abstractmethod
    def version(self) -> str:
        """The semantic version of the report contract implementation."""
        raise NotImplementedError

    @abstractmethod
    def generate(
        self,
        context: ExecutionContext,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Generate and serialize the institutional engineering report using the shared execution context.

        Args:
            context (ExecutionContext): The unified, immutable runtime context.
            *args: Additional positional evaluation artifacts.
            **kwargs: Additional keyword evaluation parameters.

        Returns:
            Any: The serialized report artifact or path location.
        """
        raise NotImplementedError
