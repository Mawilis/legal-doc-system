"""
===============================================================================
WILSY OS KERNEL — FG173 HISTORY ANALYZER ENGINE
===============================================================================
[FILE EXPLANATION]:
    Consumes historical execution records from the ExecutionHistoryStore to compute 
    deep institutional analytics, error frequencies, latency trends, and performance 
    baselines across Wilsy OS execution runs.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for compromise or technical debt.

[BIBLICAL FOUNDATION]:
    Proverbs 13:20 — "He that walketh with wise men shall be wise: but a companion of fools shall be destroyed."
    Proverbs 18:15 — "The heart of the prudent getteth knowledge; and the ear of the wise seeketh knowledge."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / History Analyzer Engine
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from tools.eos.intelligence.contracts import IHistoryAnalyzer
from tools.eos.intelligence.execution_history import ExecutionHistoryStore


class HistoryAnalyzer(IHistoryAnalyzer):
    """
    [ENGINE SPECIFICATION]: History Analyzer Implementation
    Consumes the ExecutionHistoryStore to compute aggregated institutional analytics, 
    failure frequencies, latency percentiles, and performance bottlenecks across runs.
    """

    def __init__(self, history_store: ExecutionHistoryStore) -> None:
        """
        [FUNCTION EXPLANATION]: 
            Initializes the HistoryAnalyzer with a reference to the immutable 
            ExecutionHistoryStore instance.
        """
        self._history_store = history_store

    def analyze_history(self) -> Dict[str, Any]:
        """
        [FUNCTION EXPLANATION]: 
            Analyzes all stored historical execution records to produce comprehensive 
            institutional intelligence metrics, including total execution counts, failure 
            aggregates, warning counts, artifact yields, latency statistics, and 
            actionable operational insights.
        """
        records = self._history_store.get_all_records()
        if not records:
            return {
                "total_analyzed": 0,
                "status": "no_history_available",
                "insights": []
            }

        total_runs = len(records)
        total_failures = sum(r.failures_count for r in records)
        total_warnings = sum(r.warnings_count for r in records)
        total_artifacts = sum(r.artifacts_count for r in records)
        
        runtimes = [r.duration_ms for r in records]
        avg_runtime = sum(runtimes) / total_runs if total_runs > 0 else 0.0
        max_runtime = max(runtimes) if runtimes else 0.0
        min_runtime = min(runtimes) if runtimes else 0.0

        health_scores = [r.health_score for r in records]
        avg_health = sum(health_scores) / total_runs if total_runs > 0 else 0.0

        insights: List[Dict[str, Any]] = []

        if total_failures > 0:
            insights.append({
                "insight_type": "operational_risk",
                "description": f"Detected {total_failures} total failures across {total_runs} institutional executions."
            })
        else:
            insights.append({
                "insight_type": "pristine_compliance",
                "description": "Zero failures detected across historical institutional execution records."
            })

        if avg_runtime > 1000.0:
            insights.append({
                "insight_type": "performance_warning",
                "description": f"Average execution runtime of {avg_runtime:.2f}ms exceeds optimal latency threshold."
            })

        return {
            "total_analyzed": total_runs,
            "total_failures": total_failures,
            "total_warnings": total_warnings,
            "total_artifacts_produced": total_artifacts,
            "average_runtime_ms": round(avg_runtime, 2),
            "max_runtime_ms": round(max_runtime, 2),
            "min_runtime_ms": round(min_runtime, 2),
            "average_health_score": round(avg_health, 2),
            "insights": insights
        }
