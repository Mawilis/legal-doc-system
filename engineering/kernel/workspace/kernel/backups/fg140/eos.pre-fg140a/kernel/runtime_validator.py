"""
Wilsy Engineering Kernel

Engineering Kernel Runtime Validator

Read-only validation of the Engineering Kernel startup lifecycle.
"""

from __future__ import annotations

from .bootstrap import KernelBootstrap
from .runtime import KernelRuntimeContext


class RuntimeValidator:
    """
    Validate the Engineering Kernel runtime.

    This validator performs no repository mutation.
    """

    def validate(
        self,
    ) -> KernelRuntimeContext:
        """
        Validate Engineering Kernel startup.

        Returns
        -------
        KernelRuntimeContext
            Verified runtime context.
        """

        runtime = KernelBootstrap().boot()

        if not isinstance(runtime, KernelRuntimeContext):
            raise RuntimeError(
                "Kernel bootstrap returned an invalid runtime context."
            )

        if runtime.registry is None:
            raise RuntimeError(
                "Kernel runtime context has no registry."
            )

        return runtime
