"""
Wilsy Engineering Kernel

Engineering Kernel Bootstrap

Initializes the Engineering Kernel Runtime.
"""

from __future__ import annotations

from .registry import KernelRegistry
from .runtime import KernelRuntimeContext


class KernelBootstrap:
    """
    Read-only Engineering Kernel bootstrap.

    Responsible only for preparing the Engineering Kernel runtime.
    """

    VERSION = "1.0.0"

    STARTUP_MODE = "STANDARD"

    def boot(
        self,
    ) -> KernelRuntimeContext:
        """
        Initialize the Engineering Kernel.

        Returns
        -------
        KernelRuntimeContext
            Immutable runtime context.
        """

        registry = KernelRegistry()

        return KernelRuntimeContext(
            registry=registry,
            version=self.VERSION,
            startup_mode=self.STARTUP_MODE,
        )
