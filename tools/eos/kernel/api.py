"""
Wilsy Engineering Kernel

Engineering Kernel API

Stable institutional API for the Engineering Kernel.
"""

from __future__ import annotations

from .runner import EngineeringKernelRunner
from .session import EngineeringKernelSession


class EngineeringKernel:
    """
    Stable institutional Engineering Kernel API.

    Responsible only for exposing the canonical
    Engineering Kernel execution interface.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initialize Engineering Kernel API dependencies.
        """

        self._runner = EngineeringKernelRunner()

    def execute(
        self,
    ) -> EngineeringKernelSession:
        """
        Execute the Engineering Kernel.

        Returns the canonical immutable Engineering
        Kernel Session.
        """

        return self._runner.run()
