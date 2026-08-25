"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Metrics Framework - Memory Metrics.
    Tracks RAM consumption, peak memory usage, and allocation deltas
    across Wilsy OS execution.

Biblical Scale & Architecture:
    Production-ready enterprise memory telemetry. Zero child's place.
    Provides accurate memory footprint auditing during execution.

Collaboration & Maintenance:
    - [Architecture]: Dataclass recording baseline, peak, and delta RAM usage.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class MemoryMetrics:
    """
    Institutional memory telemetry container tracking resident set size (RSS) and peak allocations.
    """

    rss_start_bytes: int = 0
    rss_end_bytes: int = 0
    rss_peak_bytes: int = 0
    delta_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def compute_delta(self) -> None:
        """
        Computes memory delta between start and end RSS allocations.
        """
        self.delta_bytes = self.rss_end_bytes - self.rss_start_bytes

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes memory metrics into an institutional dictionary payload.

        Returns:
            Dict[str, Any]: Serialized memory metrics.
        """
        return {
            "rss_start_bytes": self.rss_start_bytes,
            "rss_end_bytes": self.rss_end_bytes,
            "rss_peak_bytes": self.rss_peak_bytes,
            "delta_bytes": self.delta_bytes,
            "metadata": dict(self.metadata),
        }
