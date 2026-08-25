"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Execution Contracts Framework - Repository Contract.
    Defines the immutable institutional contract for repository discovery,
    codebase scanning, and file exploration across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise repository contract. Zero child's place.
    Enforces unified codebase analysis utilizing the immutable ExecutionContext matrix.

Collaboration & Maintenance:
    - [Architecture]: Pure protocol definition for repository subsystems.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List

from ...runtime.context import ExecutionContext


class RepositoryContract(ABC):
    """
    Base institutional contract implemented by repository discovery and scanning engines.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The canonical identifier of the repository contract component."""
        raise NotImplementedError

    @property
    @abstractmethod
    def version(self) -> str:
        """The semantic version of the repository contract implementation."""
        raise NotImplementedError

    @abstractmethod
    def discover(
        self,
        context: ExecutionContext,
    ) -> List[Any]:
        """
        Discover and index workspace modules and codebase assets using the shared execution context.

        Args:
            context (ExecutionContext): The unified, immutable runtime context.

        Returns:
            List[Any]: The institutional list of discovered repository components or nodes.
        """
        raise NotImplementedError
