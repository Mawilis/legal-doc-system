"""
===============================================================================
WILSY OS — FG221 CLUSTER METRICS COLLECTOR SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/application/metrics_collector.py

Epitome:
    Aggregates operational cluster metrics, task latencies, execution counters,
    and system telemetry for observability dashboards and audit compliance.

Biblical Worth Billions:
    "A false balance is an abomination to the Lord, but a just weight is His delight."
    — Proverbs 11:1

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import threading
import time
from typing import Dict, Any, List


class MetricsCollector:
    """
    Production-grade metrics aggregator tracking cluster performance counters,
    latencies, and operational telemetry with thread-safe synchronization.
    """

    def __init__(self) -> None:
        self._metrics: Dict[str, List[float]] = {}
        self._counters: Dict[str, int] = {}
        self._lock = threading.RLock()

    def record_metric(self, name: str, value: float) -> None:
        """Records a numerical metric sample (e.g., latency, execution time)."""
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = []
            self._metrics[name].append(value)

    increment_counter = record_metric  # Alias for backward compatibility if needed

    def increment(self, name: str, amount: int = 1) -> None:
        """Increments an operational counter."""
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + amount

    def get_summary(self) -> Dict[str, Any]:
        """Returns aggregated statistical summary of all tracked metrics and counters."""
        with self._lock:
            summary: Dict[str, Any] = {}
            for name, values in self._metrics.items():
                if values:
                    summary[f"{name}_count"] = len(values)
                    summary[f"{name}_sum"] = sum(values)
                    summary[f"{name}_avg"] = sum(values) / len(values)
                    summary[f"{name}_max"] = max(values)
                    summary[f"{name}_min"] = min(values)
                else:
                    summary[f"{name}_count"] = 0

            for name, count in self._counters.items():
                summary[name] = count

            return summary
