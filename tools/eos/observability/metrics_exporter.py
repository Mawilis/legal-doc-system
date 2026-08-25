"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Observability - Metrics Exporter (FG158).
    Formats and exports kernel telemetry metrics into structured formats (JSON, Prometheus)
    for external monitoring systems and dashboards.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready metrics export engine. Zero child's place.
    Numbers 1:2 - "Take a census of all the congregation of the people of Israel..."

Collaboration & Maintenance:
    - [Architecture]: Exporter supporting Prometheus and JSON metric serialization.
    - [Compliance]: Guarantees standardized observability data ingestion.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from tools.eos.observability.telemetry import TelemetryCollector, TelemetryEvent


class MetricsExporter:
    """
    Exports recorded telemetry metrics into standardized formats for ingestion
    by monitoring systems (Prometheus, Grafana, JSON APIs).
    """

    # [FUNCTION EXPLANATION]: Exports all collected telemetry events into a formatted JSON string.
    @staticmethod
    def export_json(collector: TelemetryCollector, subsystem: Optional[str] = None) -> str:
        """
        Exports telemetry events as a pretty-printed JSON payload.

        Args:
            collector (TelemetryCollector): The active telemetry collector instance.
            subsystem (Optional[str]): Optional filter by subsystem name.

        Returns:
            str: Formatted JSON string of metrics.
        """
        events = collector.get_events(subsystem=subsystem)
        return json.dumps({
            "export_format": "WilsyOS-Telemetry-JSON",
            "total_events": len(events),
            "events": events,
        }, indent=2, sort_keys=True)

    # [FUNCTION EXPLANATION]: Formats telemetry events into standard Prometheus text line protocol.
    @staticmethod
    def export_prometheus(collector: TelemetryCollector) -> str:
        """
        Converts recorded telemetry events into Prometheus exposition text format.

        Args:
            collector (TelemetryCollector): The active telemetry collector instance.

        Returns:
            str: Prometheus formatted text block.
        """
        events = collector.get_events()
        lines: List[str] = [
            "# HELP wilsy_os_telemetry_metric Recorded kernel telemetry metric",
            "# TYPE wilsy_os_telemetry_metric gauge"
        ]

        for e in events:
            # Format metric name safely for Prometheus: subsystem_metric_name
            metric_key = f"wilsy_{e['subsystem'].lower()}_{e['metric_name'].lower()}"
            
            # Construct label string
            labels = [f'event_id="{e["event_id"]}"', f'unit="{e["unit"]}"']
            for k, v in e.get("metadata", {}).items():
                labels.append(f'{k}="{v}"')
            
            label_str = f"{{{', '.join(labels)}}}" if labels else ""
            line = f"{metric_key}{label_str} {e['value']}"
            lines.append(line)

        return "\n".join(lines) + "\n"
