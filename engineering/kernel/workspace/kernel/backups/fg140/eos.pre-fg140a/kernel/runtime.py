"""
Wilsy Engineering Kernel

Engineering Kernel Runtime Context

Immutable runtime state shared by the Engineering Kernel.
"""

from __future__ import annotations

from dataclasses import dataclass

from .registry import KernelRegistry


@dataclass(frozen=True)
class KernelRuntimeContext:
    """
    Immutable Engineering Kernel runtime context.
    """

    registry: KernelRegistry
    version: str
    startup_mode: str
