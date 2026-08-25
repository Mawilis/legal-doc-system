"""
Wilsy Engineering Kernel

Engineering Kernel Runtime Validator

Read-only validation of the Engineering Kernel startup lifecycle.
"""

from __future__ import annotations

from .runtime import KernelRuntimeContext


class RuntimeValidator:
    """
    Validate the Engineering Kernel runtime.

    This validator performs no repository mutation.
    """

    def validate(
        self,
        runtime: KernelRuntimeContext,
    ) -> KernelRuntimeContext:
        """
        Validate Engineering Kernel startup.

        Parameters
        ----------
        runtime
            Runtime context produced by KernelBootstrap.

        Returns
        -------
        KernelRuntimeContext
            Verified runtime context.
        """

        if not isinstance(runtime, KernelRuntimeContext):
            raise RuntimeError(
                "Kernel bootstrap returned an invalid runtime context."
            )

        if runtime.registry is None:
            raise RuntimeError(
                "Kernel runtime context has no registry."
            )

        return runtime
