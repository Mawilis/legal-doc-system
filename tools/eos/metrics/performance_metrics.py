"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Metrics Framework - Performance Metrics.
    Captures CPU utilization, execution throughput, and latency distribution
    across Wilsy OS engines.

Biblical Scale & Architecture:
    Production-ready enterprise performance telemetry. Zero child's place.
    Provides robust statistical analysis of engine performance.

Collaboration & Maintenance:
    - [Architecture]: Dataclass recording CPU load, throughput, and latency percentiles.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class PerformanceMetrics:
    """
    Institutional performance telemetry container for tracking CPU, throughput, and latency.
    """

    cpu_percent_start: float = 0.0
    cpu_percent_end: float = 0.0
    throughput_engines_per_sec: float = 0.0
    latency_p50_ms: float = 0.0
    latency_p95_ms: float = 0.0
    latency_p99_ms: float = 0.0
    custom_indicators: Dict[str, Any] = field(default_factory=dict)

    def calculate_percentiles(self, latencies_ms: List[float]) -> None:
        """
        Calculates p50, p95, and p99 latency percentiles from a list of durations.

        Args:
            latencies_ms (List[float]): List of execution durations in milliseconds.
        """
        if not latencies_ms:
            return

        sorted_latencies = sorted(latencies_ms)
        n = len(sorted_latencies)

        def percentile(p: float) -> float:
            idx = int(p * n)
            return sorted_latencies[min(idx, n - 1)]

        self.latency_p50_ms = percentile(0.50)
        self.latency_p95_ms = percentile(0.95)
        self.latency_p99_ms = percentile(0.99)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes performance metrics into an institutional dictionary payload.

        Returns:
            Dict[str, Any]: Serialized performance metrics.
        """
        return {
            "cpu_percent_start": self.cpu_percent_start,
            "cpu_percent_end": self.cpu_percent_end,
            "throughput_engines_per_sec": self.throughput_engines_per_sec,
            "latency_p50_ms": self.latency_p50_ms,
            "latency_p95_ms": self.latency_p95_ms,
            "latency_p99_ms": self.latency_p99_ms,
            "custom_indicators": dict(self.custom_indicators),
        }
