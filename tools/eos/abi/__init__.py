"""
===============================================================================
WILSY OS KERNEL ARCHITECTURE - ENTERPRISE ENGINEERING PLATFORM
===============================================================================
PROJECT: Wilsy OS (Billion-Dollar Sovereign Infrastructure)
SUBSYSTEM: Kernel ABI & Core Governance Framework
MILESTONE: FG178.5 - Kernel ABI Freeze
MODULE: __init__.py

COLLABORATION & ARCHITECTURAL NOTICE:
This module defines frozen, non-negotiable Kernel Application Binary Interface (ABI)
contracts for Wilsy OS. All present and future engines, distributed workers,
governance hooks, and runtime extensions MUST conform to this immutable spec.
===============================================================================
"""

from tools.eos.abi.kernel_version import (
    KERNEL_VERSION,
    ABI_VERSION,
    RUNTIME_VERSION,
    ARTIFACT_VERSION,
    EVENT_VERSION,
    PROTOCOL_VERSION,
    SCHEMA_VERSION,
    KernelVersionSpec,
    Version,
    ABICompatibilityLevel,
)
from tools.eos.abi.kernel_contracts import (
    BaseKernelEngineProtocol,
    LifecyclePhase,
    EngineExecutionStatus,
    ExecutionContextProtocol,
    EngineResultProtocol,
    EngineCapability,
    BaseKernelEngine,
)
from tools.eos.abi.kernel_abi import KernelABI
from tools.eos.abi.compatibility import (
    ABICompatibilityManager,
    EngineCompatibilityAdapter,
)
from tools.eos.abi.migration import ABIMigrationEngine, MigrationPlan
from tools.eos.abi.abi_validator import (
    ABIValidator,
    ABIValidationReport,
    ABIValidationError,
)

__all__ = [
    "KERNEL_VERSION",
    "ABI_VERSION",
    "RUNTIME_VERSION",
    "ARTIFACT_VERSION",
    "EVENT_VERSION",
    "PROTOCOL_VERSION",
    "SCHEMA_VERSION",
    "KernelVersionSpec",
    "Version",
    "ABICompatibilityLevel",
    "BaseKernelEngineProtocol",
    "BaseKernelEngine",
    "LifecyclePhase",
    "EngineExecutionStatus",
    "ExecutionContextProtocol",
    "EngineResultProtocol",
    "EngineCapability",
    "KernelABI",
    "ABICompatibilityManager",
    "EngineCompatibilityAdapter",
    "ABIMigrationEngine",
    "MigrationPlan",
    "ABIValidator",
    "ABIValidationReport",
    "ABIValidationError",
]
