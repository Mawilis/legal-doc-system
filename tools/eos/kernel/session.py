"""
===============================================================================
WILSY OS KERNEL: ENGINEERING SESSION
===============================================================================
Epitome:
    The immutable operational state container for the Wilsy EOS. This session 
    object is produced by the EngineeringKernel upon successful ingestion 
    of a verified ExecutionContext.

Biblical Scale & Architecture:
    The "output" of the Kernel. Once initialized, the session represents 
    the active state of the OS. It is frozen/immutable to ensure that 
    during an execution lifecycle, the environment parameters cannot be 
    altered or sabotaged. 

Collaboration & Maintenance:
    - Acts as the operational manifest for all downstream engines.
    - Encapsulates the execution metadata and active subsystem registry.
    - Future-proof: Easily extensible to hold runtime telemetry or logs.
===============================================================================
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class EngineeringKernelSession:
    """
    The immutable snapshot of an active Wilsy OS Kernel session.
    """
    metadata: Any  # ExecutionMetadata
    active_engines: Dict[str, bool]

    def is_engine_active(self, engine_name: str) -> bool:
        """
        Check if a specific sub-engine is registered as active in this session.
        """
        return self.active_engines.get(engine_name, False)

    def __repr__(self) -> str:
        return f"<EngineeringKernelSession: {self.metadata.execution_id} | Engines: {len(self.active_engines)}>"
