"""
===============================================================================
WILSY OS KERNEL — INSTITUTIONAL MEMORY STATISTICS
===============================================================================
[EPITOME]:
    Computes analytics, telemetry metrics, record volume distributions, and memory growth 
    statistics across institutional memory records.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for inaccurate calculations.

[BIBLICAL FOUNDATION]:
    Luke 14:28 — "For which of you, intending to build a tower, sitteth not down first, and counteth the cost..."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Memory Statistics
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List
from tools.eos.memory.memory_store import MemoryStore


class MemoryStatisticsCalculator:
    """
    [ENGINE SPECIFICATION]: Memory Statistics Calculator
    Analyzes institutional memory store contents to produce executive telemetry analytics.
    """

    def __init__(self, store: MemoryStore) -> None:
        """
        [FUNCTION EXPLANATION]:
            Initializes the MemoryStatisticsCalculator with a MemoryStore instance.
        """
        self._store = store

    def compute_statistics(self) -> Dict[str, Any]:
        """
        [FUNCTION EXPLANATION]:
            Computes comprehensive statistical metrics regarding institutional memory volume, 
            type breakdowns, producer activity, and tag distribution.
        """
        records = self._store.get_all_records()
        total_records = len(records)

        type_distribution: Dict[str, int] = {}
        producer_activity: Dict[str, int] = {}
        tag_distribution: Dict[str, int] = {}
        execution_counts: Dict[str, int] = {}

        for r in records:
            type_distribution[r.record_type] = type_distribution.get(r.record_type, 0) + 1
            producer_activity[r.producer] = producer_activity.get(r.producer, 0) + 1
            execution_counts[r.execution_id] = execution_counts.get(r.execution_id, 0) + 1
            for t in r.tags:
                tag_distribution[t] = tag_distribution.get(t, 0) + 1

        unique_executions = len(execution_counts)
        avg_records_per_execution = (total_records / unique_executions) if unique_executions > 0 else 0.0

        return {
            "total_institutional_records": total_records,
            "unique_executions_recorded": unique_executions,
            "average_records_per_execution": round(avg_records_per_execution, 2),
            "record_type_distribution": type_distribution,
            "producer_activity_distribution": producer_activity,
            "tag_distribution": tag_distribution
        }
