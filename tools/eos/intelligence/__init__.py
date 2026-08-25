"""
===============================================================================
WILSY OS — INTELLIGENCE PACKAGE
===============================================================================
Exports all intelligence modules for the kernel.
===============================================================================
"""

from .execution_history import ExecutionHistoryStore, ExecutionRecord, ExecutionRecordDTO
from .execution_snapshot import ExecutionSnapshotDTO
from .execution_memory import InstitutionalMemory
from .execution_statistics import ExecutionStatisticsEngine
from .execution_patterns import ExecutionPatternAnalyzer, HistoricalPattern
from .execution_recommendations import ExecutionRecommendationEngine, RecommendationDTO
from .execution_timeline import ExecutionTimelineBuilder, TimelineEventDTO
from .execution_trends import ExecutionTrendAnalyzer
from .execution_intelligence import ExecutionIntelligenceEngine, ExecutionIntelligenceReport

__all__ = [
    "ExecutionHistoryStore",
    "ExecutionRecord",
    "ExecutionRecordDTO",
    "ExecutionSnapshotDTO",
    "InstitutionalMemory",
    "ExecutionStatisticsEngine",
    "ExecutionPatternAnalyzer",
    "HistoricalPattern",
    "ExecutionRecommendationEngine",
    "RecommendationDTO",
    "ExecutionTimelineBuilder",
    "TimelineEventDTO",
    "ExecutionTrendAnalyzer",
    "ExecutionIntelligenceEngine",
    "ExecutionIntelligenceReport",
]
