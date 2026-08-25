"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Observability - Performance Dashboard Generator (FG158).
    Aggregates metrics, traces, timings, and resource usage telemetry into a unified
    executive dashboard report for Wilsy OS.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready performance dashboard and telemetry synthesizer. Zero child's place.
    Habakkuk 2:2 - "Write the vision; make it plain on tablets, so he may run who reads it."

Collaboration & Maintenance:
    - [Architecture]: Executive observability dashboard aggregator.
    - [Compliance]: Guarantees real-time visibility into kernel performance and resource health.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from tools.eos.observability.metrics_exporter import MetricsExporter
from tools.eos.observability.telemetry import TelemetryCollector
from tools.eos.observability.trace import Tracer


class PerformanceDashboard:
    """
    Generates consolidated executive performance dashboards combining metrics,
    timings, traces, and system resource telemetry.
    """

    def __init__(self, collector: TelemetryCollector) -> None:
        """
        Initializes the performance dashboard linked to a telemetry collector.

        Args:
            collector (TelemetryCollector): Active telemetry collector instance.
        """
        self.collector = collector

    # [FUNCTION EXPLANATION]: Generates a unified performance dashboard report incorporating all active telemetry and traces.
    def generate_dashboard_report(
        self,
        tracers: Optional[List[Tracer]] = None,
    ) -> Dict[str, Any]:
        """
        Compiles all recorded metrics and optional traces into a structured executive report.

        Args:
            tracers (Optional[List[Tracer]]): Optional list of active execution tracers.

        Returns:
            Dict[str, Any]: Comprehensive dashboard summary report.
        """
        events = self.collector.get_events()
        
        # Calculate summary statistics by subsystem
        subsystems_summary: Dict[str, Any] = {}
        for e in events:
            sub = e["subsystem"]
            if sub not in subsystems_summary:
                subsystems_summary[sub] = {
                    "event_count": 0,
                    "metrics": {},
                }
            subsystems_summary[sub]["event_count"] += 1
            metric_name = e["metric_name"]
            if metric_name not in subsystems_summary[sub]["metrics"]:
                subsystems_summary[sub]["metrics"][metric_name] = []
            subsystems_summary[sub]["metrics"][metric_name].append(e["value"])

        # Compute averages or latest values for metrics
        formatted_subsystems: Dict[str, Any] = {}
        for sub, data in subsystems_summary.items():
            metrics_avg = {}
            for m_name, values in data["metrics"].items():
                metrics_avg[m_name] = {
                    "latest": values[-1] if values else 0.0,
                    "average": round(sum(values) / len(values), 3) if values else 0.0,
                    "samples": len(values),
                }
            formatted_subsystems[sub] = {
                "total_events": data["event_count"],
                "metrics": metrics_avg,
            }

        # Aggregate trace summaries if provided
        trace_summaries = []
        if tracers:
            for t in tracers:
                trace_summaries.append(t.get_trace_summary())

        return {
            "dashboard_title": "WilsyOS Executive Performance & Observability Dashboard",
            "status": "OPERATIONAL",
            "total_telemetry_events": len(events),
            "subsystem_telemetry": formatted_subsystems,
            "distributed_traces": trace_summaries,
        }

    def generate_dashboard_json(self, tracers: Optional[List[Tracer]] = None) -> str:
        """Exports the dashboard report as a pretty-printed JSON string."""
        report = self.generate_dashboard_report(tracers=tracers)
        return json.dumps(report, indent=2, sort_keys=True)
