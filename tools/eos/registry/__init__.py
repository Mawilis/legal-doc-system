"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Registry Framework - Package Initializer.
    Registers and orchestrates all institutional engines across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise engine registry. Zero child's place.
    Exposes dependency resolution, execution ordering, and component descriptors.

Collaboration & Maintenance:
    - [Exports]: EngineRegistry, DependencyGraph, ExecutionOrderResolver, EngineDescriptor.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from .engine_registry import EngineRegistry
from .dependency_graph import DependencyGraph
from .execution_order import ExecutionOrderResolver
from .engine_descriptor import EngineDescriptor

__all__ = [
    "EngineRegistry",
    "DependencyGraph",
    "ExecutionOrderResolver",
    "EngineDescriptor",
]
