"""
===============================================================================
WILSY OS — FG220 PLUGIN TELEMETRY & OBSERVABILITY ENGINE
===============================================================================

Epitome:
    Telemetry collection and performance monitoring engine for marketplace plugins.
    Tracks invocation counts, execution latency histograms, memory footprints,
    and runtime error rates for sovereign audit and system optimization.

Biblical Worth Billions:
    "So teach us to number our days, that we may apply our hearts unto wisdom."
    — Psalm 90:12

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
    - File Path: tools/eos/marketplace/plugin_telemetry.py
===============================================================================
"""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from tools.eos.marketplace import logger


@dataclass
class PluginMetricRecord:
    """Represents a single execution telemetry event for a plugin method."""
    plugin_id: str
    method_name: str
    latency_ms: float
    success: bool
    timestamp: float = field(default_factory=time.time)
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts metric record to dictionary representation."""
        return {
            "plugin_id": self.plugin_id,
            "method_name": self.method_name,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "timestamp": self.timestamp,
            "error_message": self.error_message
        }


class PluginTelemetryCollector:
    """
    Singleton-ready telemetry registry and metrics aggregator for Wilsy OS plugins.
    """

    def __init__(self, max_history_size: int = 1000) -> None:
        """
        Initializes telemetry collector.

        Args:
            max_history_size (int): Maximum number of records to retain in memory.
        """
        self.max_history_size = max_history_size
        self._records: List[PluginMetricRecord] = []
        self._plugin_stats: Dict[str, Dict[str, Any]] = {}

    def record_execution(
        self,
        plugin_id: str,
        method_name: str,
        latency_ms: float,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """
        Records a telemetry event for a plugin invocation.

        Args:
            plugin_id (str): Unique plugin identifier.
            method_name (str): Method invoked.
            latency_ms (float): Execution latency in milliseconds.
            success (bool): Whether execution succeeded.
            error_message (Optional[str]): Error description if failed.
        """
        record = PluginMetricRecord(
            plugin_id=plugin_id,
            method_name=method_name,
            latency_ms=latency_ms,
            success=success,
            error_message=error_message
        )

        self._records.append(record)
        if len(self._records) > self.max_history_size:
            self._records.pop(0)

        # Update aggregated stats
        if plugin_id not in self._plugin_stats:
            self._plugin_stats[plugin_id] = {
                "total_invocations": 0,
                "successful_invocations": 0,
                "failed_invocations": 0,
                "total_latency_ms": 0.0,
                "max_latency_ms": 0.0,
                "min_latency_ms": float('inf')
            }

        stats = self._plugin_stats[plugin_id]
        stats["total_invocations"] += 1
        if success:
            stats["successful_invocations"] += 1
        else:
            stats["failed_invocations"] += 1

        stats["total_latency_ms"] += latency_ms
        stats["max_latency_ms"] = max(stats["max_latency_ms"], latency_ms)
        stats["min_latency_ms"] = min(stats["min_latency_ms"], latency_ms)

        logger.info(
            f"[TELEMETRY] Plugin '{plugin_id}' method '{method_name}' executed in {latency_ms:.2f}ms "
            f"[Success: {success}]"
        )

    def get_plugin_stats(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves aggregated telemetry metrics for a specific plugin.

        Args:
            plugin_id (str): Unique plugin identifier.

        Returns:
            Optional[Dict[str, Any]]: Aggregated metrics dictionary.
        """
        stats = self._plugin_stats.get(plugin_id)
        if not stats:
            return None

        total = stats["total_invocations"]
        avg_latency = stats["total_latency_ms"] / total if total > 0 else 0.0

        return {
            "plugin_id": plugin_id,
            "total_invocations": total,
            "successful_invocations": stats["successful_invocations"],
            "failed_invocations": stats["failed_invocations"],
            "success_rate": (stats["successful_invocations"] / total) * 100 if total > 0 else 0.0,
            "average_latency_ms": round(avg_latency, 4),
            "max_latency_ms": stats["max_latency_ms"],
            "min_latency_ms": stats["min_latency_ms"] if stats["min_latency_ms"] != float('inf') else 0.0
        }

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Retrieves telemetry metrics for all plugins."""
        return {pid: self.get_plugin_stats(pid) for pid in self._plugin_stats}

    def clear(self) -> None:
        """Clears all recorded metrics."""
        self._records.clear()
        self._plugin_stats.clear()
        logger.info("[TELEMETRY] Telemetry records cleared.")
