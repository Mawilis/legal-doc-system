"""
===============================================================================
WILSY OS KERNEL ARCHITECTURE - ENTERPRISE ENGINEERING PLATFORM
===============================================================================
PROJECT: Wilsy OS (Billion-Dollar Sovereign Infrastructure)
SUBSYSTEM: Kernel Runtime Context
MILESTONE: FG178.5 - Kernel ABI Freeze
MODULE: tools/eos/kernel/runtime.py

COLLABORATION & ARCHITECTURAL NOTICE:
Defines the immutable KernelRuntimeContext released by KernelBootstrap upon successful
ABI startup validation. Holds references to system registry, version specs,
and validation reports.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Dict

from tools.eos.abi.kernel_version import KernelVersionSpec
from tools.eos.abi.abi_validator import ABIValidationReport


@dataclass(frozen=True)
class KernelRuntimeContext:
    """
    Immutable Runtime Context for the Wilsy OS Engineering Kernel.
    
    Constructed and returned by KernelBootstrap after full ABI validation
    and system locking under Milestone FG178.5.
    """

    registry: Any
    version: str = "1.0.0"
    startup_mode: str = "STANDARD"
    abi_validation_report: Optional[ABIValidationReport] = None
    version_spec: Optional[KernelVersionSpec] = None

    def export_telemetry(self) -> Dict[str, Any]:
        """Export runtime telemetry data for system attestations."""
        return {
            "version": self.version,
            "startup_mode": self.startup_mode,
            "is_abi_compliant": (
                self.abi_validation_report.is_system_compliant
                if self.abi_validation_report
                else True
            ),
            "version_spec": (
                self.version_spec.export_manifest()
                if self.version_spec
                else None
            ),
        }
