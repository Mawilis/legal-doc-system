"""
===============================================================================
WILSY OS KERNEL — FG173 STRATEGY ENGINE
===============================================================================
[FILE EXPLANATION]:
    Selects and optimizes the master execution strategy for Wilsy OS pipelines 
    based on historical success rates, runtime analytics, and operational telemetry.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for technical debt or fallback guesswork.

[BIBLICAL FOUNDATION]:
    Proverbs 24:3-4 — "Through wisdom is an house builded; and by understanding it is established: And by knowledge shall the chambers be filled with all precious and pleasant riches."
    Luke 14:28 — "For which of you, intending to build a tower, sitteth not down first, and counteth the cost..."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Strategy Engine
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from tools.eos.intelligence.contracts import IStrategyEngine
from tools.eos.intelligence.models import ExecutionStrategy
from tools.eos.intelligence.execution_history import ExecutionHistoryStore
from tools.eos.intelligence.history_analyzer import HistoryAnalyzer


class StrategyEngine(IStrategyEngine):
    """
    [ENGINE SPECIFICATION]: Strategy Engine Implementation
    Evaluates historical telemetry to select the optimal execution path, worker 
    sequencing, and resource allocation profile for upcoming pipeline runs.
    """

    def __init__(
        self,
        history_store: ExecutionHistoryStore,
        history_analyzer: HistoryAnalyzer
    ) -> None:
        """
        [FUNCTION EXPLANATION]: 
            Initializes the StrategyEngine with historical data stores and analytics engines.
        """
        self._history_store = history_store
        self._history_analyzer = history_analyzer

    def select_strategy(self, context: Dict[str, Any]) -> ExecutionStrategy:
        """
        [FUNCTION EXPLANATION]: 
            Analyzes current execution context and historical success metrics to 
            determine and return the optimal ExecutionStrategy DTO.
        """
        analysis = self._history_analyzer.analyze_history()
        total_runs = analysis.get("total_analyzed", 0)
        total_failures = analysis.get("total_failures", 0)
        avg_health = analysis.get("average_health_score", 100.0)

        # Calculate historical success rate
        if total_runs > 0:
            success_count = total_runs - min(total_runs, total_failures)
            success_rate = (success_count / total_runs) * 100.0
        else:
            success_rate = 100.0  # Default baseline for pristine bootstrap

        # Determine optimized engine execution order
        if total_failures > 2:
            strategy_id = "STRAT-HARDENED-RECOVERY-001"
            strategy_name = "Hardened Recovery & Strict Telemetry Verification"
            target_engine_order = [
                "RuntimeEventBus",
                "HistoryAnalyzer",
                "EvidenceGraph",
                "ArtifactAggregator",
                "DashboardLiveManager",
                "KernelBootstrap"
            ]
            justification = f"Historical execution records reveal {total_failures} failures. Enforcing strict validation and diagnostic sequencing."
        elif avg_health < 90.0:
            strategy_id = "STRAT-OPTIMIZED-ACCELERATED-002"
            strategy_name = "Optimized Snapshot & High-Velocity Concurrency"
            target_engine_order = [
                "RuntimeEventBus",
                "DashboardLiveManager",
                "ArtifactAggregator",
                "KernelBootstrap"
            ]
            justification = "Health scores suggest latency bottlenecks. Prioritizing O(1) snapshot caching and parallel worker dispatch."
        else:
            strategy_id = "STRAT-PRISTINE-SUPREMACY-003"
            strategy_name = "Pristine Event-Driven Supremacy Pipeline"
            target_engine_order = [
                "RuntimeEventBus",
                "ArtifactAggregator",
                "DashboardLiveManager",
                "KernelBootstrap"
            ]
            justification = "Historical success rate is optimal. Executing pure Event-Driven Architecture pipeline with zero polling overhead."

        return ExecutionStrategy(
            strategy_id=strategy_id,
            strategy_name=strategy_name,
            target_engine_order=target_engine_order,
            historical_success_rate=round(success_rate, 2),
            justification=justification
        )
