"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Observability - Distributed Tracing & Span Engine (FG158).
    Tracks execution pathways and latency across kernel subsystems using cryptographic 
    span IDs and parent-child hierarchy.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready execution tracing system. Zero child's place.
    Job 28:24 - "For he looks to the ends of the earth and sees everything under the heavens."

Collaboration & Maintenance:
    - [Architecture]: Cryptographic execution span tracking and duration telemetry.
    - [Compliance]: Guarantees end-to-end auditability of request and kernel pathways.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Span:
    """
    Immutable representation of an isolated execution span within a distributed trace.
    """
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    subsystem: str
    operation_name: str
    start_time_unix: float
    duration_ms: float = 0.0
    status: str = "SUCCESS"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the span into a dictionary."""
        return asdict(self)


class Tracer:
    """
    Manages active execution spans, timing computations, and trace hierarchy generation.
    """

    def __init__(self, trace_id: Optional[str] = None) -> None:
        self.trace_id = trace_id or f"trace-{uuid.uuid4().hex[:16]}"
        self._spans: List[Span] = []

    # [FUNCTION EXPLANATION]: Creates a new child span within the active trace context.
    def start_span(
        self,
        subsystem: str,
        operation_name: str,
        parent_span_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ActiveSpanContext:
        """
        Starts a timed execution span.

        Args:
            subsystem (str): Subsystem executing the operation.
            operation_name (str): Name of the operation or function.
            parent_span_id (Optional[str]): Optional parent span identifier for nested traces.
            metadata (Optional[Dict[str, Any]]): Contextual key-value pairs.

        Returns:
            ActiveSpanContext: Context manager object for timing and completing the span.
        """
        span_id = f"span-{uuid.uuid4().hex[:12]}"
        return ActiveSpanContext(
            tracer=self,
            trace_id=self.trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            subsystem=subsystem,
            operation_name=operation_name,
            metadata=metadata or {},
        )

    # [FUNCTION EXPLANATION]: Internal method to record a completed span into the trace registry.
    def _record_span(self, span: Span) -> None:
        """Appends a completed span to the trace collection."""
        self._spans.append(span)

    def get_trace_summary(self) -> Dict[str, Any]:
        """Returns a serialized audit report of all spans recorded in this trace."""
        return {
            "trace_id": self.trace_id,
            "total_spans": len(self._spans),
            "spans": [s.to_dict() for s in self._spans],
        }


class ActiveSpanContext:
    """
    Context manager for measuring execution duration of active spans.
    """

    def __init__(
        self,
        tracer: Tracer,
        trace_id: str,
        span_id: str,
        parent_span_id: Optional[str],
        subsystem: str,
        operation_name: str,
        metadata: Dict[str, Any],
    ) -> None:
        self._tracer = tracer
        self._trace_id = trace_id
        self._span_id = span_id
        self._parent_span_id = parent_span_id
        self._subsystem = subsystem
        self._operation_name = operation_name
        self._metadata = metadata
        self._start_time = 0.0
        self._status = "SUCCESS"

    def __enter__(self) -> ActiveSpanContext:
        self._start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        elapsed_ms = round((time.perf_counter() - self._start_time) * 1000, 3)
        if exc_type is not None:
            self._status = "ERROR"
            self._metadata["exception"] = str(exc_val)

        span = Span(
            trace_id=self._trace_id,
            span_id=self._span_id,
            parent_span_id=self._parent_span_id,
            subsystem=self._subsystem,
            operation_name=self._operation_name,
            start_time_unix=self._start_time,
            duration_ms=elapsed_ms,
            status=self._status,
            metadata=self._metadata,
        )
        self._tracer._record_span(span)

    @property
    def span_id(self) -> str:
        return self._span_id
