"""
Wilsy Engineering Kernel

Engineering Kernel Lifecycle

Canonical institutional lifecycle for Engineering Kernel execution.
"""

from __future__ import annotations

from enum import Enum


class EngineeringKernelLifecycle(str, Enum):
    """
    Canonical Engineering Kernel execution lifecycle.

    Defines the institutional execution states used throughout
    the Engineering Kernel.
    """

    BOOTSTRAPPING = "BOOTSTRAPPING"

    VALIDATING = "VALIDATING"

    HEALTH_CHECK = "HEALTH_CHECK"

    READINESS = "READINESS"

    ASSURANCE = "ASSURANCE"

    REPORTING = "REPORTING"

    COMPLETE = "COMPLETE"

    FAILED = "FAILED"
