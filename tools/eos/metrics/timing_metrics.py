"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Metrics Framework - Timing Metrics.
    Records granular timestamp breakdown for pipeline phases, engine initialization,
    execution, and teardown across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise timing telemetry. Zero child's place.
    Provides precise high-resolution chronometry for operational profiling.

Collaboration & Maintenance:
    - [Architecture]: Dataclass recording start, end, and phase durations.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class TimingMetrics:
    """
    Institutional timing telemetry container tracking pipeline phase durations and timestamps.
    """

    start_timestamp: float = 0.0
    end_timestamp: float = 0.0
    total_duration_ms: float = 0.0
    phase_durations_ms: Dict[str, float] = field(default_factory=dict)

    def record_phase(self, phase_name: str, duration_ms: float) -> None:
        """
        Record the duration of a specific pipeline or engine phase.

        Args:
            phase_name (str): Identifier of the phase.
            duration_ms (float): Duration in milliseconds.
        """
        self.phase_durations_ms[phase_name] = duration_ms

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes timing metrics into an institutional dictionary payload.

        Returns:
            Dict[str, Any]: Serialized timing metrics.
        """
        return {
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "total_duration_ms": self.total_duration_ms,
            "phase_durations_ms": dict(self.phase_durations_ms),
        }
