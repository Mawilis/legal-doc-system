"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Observability - Core Telemetry Aggregator (FG158).
    Collects and unifies system metrics, execution traces, timings, and resource usage.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready telemetry collector. Zero child's place.
    Psalm 19:1 - "The heavens declare the glory of God, and the sky above proclaims his handiwork."

Collaboration & Maintenance:
    - [Architecture]: Unified telemetry collector and metric aggregator.
    - [Compliance]: Thread-safe event recording and performance telemetry hooks.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class TelemetryEvent:
    """
    Immutable representation of an isolated system telemetry or resource event.
    """
    event_id: str
    subsystem: str
    metric_name: str
    value: float
    unit: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the telemetry event into a dictionary."""
        return asdict(self)


class TelemetryCollector:
    """
    Thread-safe central collector for all kernel metrics, timings, and resource usage logs.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: List[TelemetryEvent] = []

    # [FUNCTION EXPLANATION]: Records a new telemetry metric event into the thread-safe collector.
    def record_metric(
        self,
        subsystem: str,
        metric_name: str,
        value: float,
        unit: str = "ms",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TelemetryEvent:
        """
        Records a performance metric or resource usage telemetry point.

        Args:
            subsystem (str): The origin subsystem (e.g., 'RiskEngine', 'WorkerPool', 'Cluster').
            metric_name (str): Name of the metric (e.g., 'execution_duration', 'cpu_usage').
            value (float): Metric numerical value.
            unit (str): Unit of measurement (e.g., 'ms', 'pct', 'count').
            metadata (Optional[Dict[str, Any]]): Additional context dictionary.

        Returns:
            TelemetryEvent: The recorded immutable event object.
        """
        import uuid
        event_id = f"tel-{uuid.uuid4().hex[:12]}"
        event = TelemetryEvent(
            event_id=event_id,
            subsystem=subsystem,
            metric_name=metric_name,
            value=value,
            unit=unit,
            metadata=metadata or {},
        )

        with self._lock:
            self._events.append(event)

        return event

    # [FUNCTION EXPLANATION]: Retrieves all recorded telemetry events matching optional filters.
    def get_events(self, subsystem: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns a serialized list of recorded telemetry events, optionally filtered by subsystem.
        """
        with self._lock:
            filtered = [
                e.to_dict() for e in self._events 
                if subsystem is None or e.subsystem == subsystem
            ]
            return filtered

    # [FUNCTION EXPLANATION]: Clears the telemetry event buffer.
    def clear(self) -> None:
        """Resets the internal telemetry event store."""
        with self._lock:
            self._events.clear()
