"""
===============================================================================
WILSY OS KERNEL — INTELLIGENCE MODELS (PRODUCTION GRADE)
===============================================================================
Shared data models for the intelligence package.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionRecord:
    """Immutable execution record."""
    execution_id: str
    duration_ms: float = 0.0
    engine_names: List[str] = field(default_factory=list)
    failure_count: int = 0
    warning_count: int = 0
    artifact_count: int = 0
    health_score: float = 100.0
    fingerprint: str = ""
    checksum: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""


# Aliases for compatibility
ExecutionRecordDTO = ExecutionRecord


@dataclass
class ExecutionSnapshotDTO:
    """Execution snapshot DTO."""
    execution_id: str
    snapshot_timestamp: str = ""
    runtime_context: Dict[str, Any] = field(default_factory=dict)
    repository_session: Dict[str, Any] = field(default_factory=dict)
    knowledge_graph_snapshot: Dict[str, Any] = field(default_factory=dict)
    sentinel_snapshot: Dict[str, Any] = field(default_factory=dict)
    dashboard_snapshot: Dict[str, Any] = field(default_factory=dict)
    execution_plan: Dict[str, Any] = field(default_factory=dict)
    scheduler_results: Dict[str, Any] = field(default_factory=dict)
    event_summary: Dict[str, Any] = field(default_factory=dict)
    artifact_summary: Dict[str, Any] = field(default_factory=dict)
    unified_report_reference: str = ""


@dataclass
class HistoricalPattern:
    """Historical pattern detected from execution data."""
    pattern: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecommendationDTO:
    """Recommendation DTO."""
    priority: str
    message: str
    recommendation_id: str = ""


@dataclass
class EngineeringDecision:
    """Institutional engineering decision."""
    decision_id: str
    title: str
    rationale: str
    producing_engine: str
    decision_summary: str
    confidence_score: float = 0.98
    traceability_checksum: str = "CHECKSUM-WILSY-001"


@dataclass
class ExecutionPrediction:
    """Execution prediction."""
    prediction_id: str
    target_metric: str
    predicted_value: float
    confidence: float
    confidence_score: float = 0.96
