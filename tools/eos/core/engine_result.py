"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Core Framework - Engine Result.
    Encapsulates institutional engine execution output, status, telemetry,
    metrics, and error payloads across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise result container. Zero child's place.
    Provides immutable execution payload wrapping with precise performance timing.

Collaboration & Maintenance:
    - [Architecture]: Immutable result envelope for all engine executions.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .engine_status import EngineStatus


@dataclass(frozen=True)
class EngineResult:
    """
    Immutable container encapsulating the output, status, and telemetry of an engine execution.
    """

    engine_id: str
    status: EngineStatus
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the engine result into an institutional dictionary payload.

        Returns:
            Dict[str, Any]: Serialized result dictionary.
        """
        return {
            "engine_id": self.engine_id,
            "status": self.status.value,
            "data": self.data,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "metadata": dict(self.metadata),
        }
