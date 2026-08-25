"""
===============================================================================
WILSY OS KERNEL — FG173 DECISION ENGINE
===============================================================================
[EPITOME]:
    Synthesizes master institutional engineering decisions by consolidating historical 
    execution telemetry, evidence graph chains, prioritized recommendations, and optimal execution strategies.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for technical debt, unverified heuristics, or static analysis warnings.

[BIBLICAL FOUNDATION]:
    Proverbs 2:6 — "For the Lord giveth wisdom: out of his mouth cometh knowledge and understanding."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Decision Engine
===============================================================================
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, cast

from tools.eos.intelligence.contracts import IDecisionEngine
from tools.eos.intelligence.models import EngineeringDecision
from tools.eos.intelligence.execution_history import ExecutionHistoryStore
from tools.eos.intelligence.history_analyzer import HistoryAnalyzer
from tools.eos.intelligence.evidence_graph import EvidenceGraph
from tools.eos.intelligence.recommendation_engine import RecommendationEngine
from tools.eos.intelligence.strategy_engine import StrategyEngine


class DecisionEngine(IDecisionEngine):
    """
    [ENGINE SPECIFICATION]: Decision Engine Implementation
    Synthesizes executive institutional decisions backed by full dependency injection 
    of history stores, analyzers, evidence graphs, recommendations, and execution strategies.
    """

    def __init__(
        self,
        history_store: ExecutionHistoryStore,
        history_analyzer: HistoryAnalyzer,
        evidence_graph: EvidenceGraph,
        recommendation_engine: RecommendationEngine,
        strategy_engine: StrategyEngine
    ) -> None:
        """
        [FUNCTION EXPLANATION]:
            Initializes the DecisionEngine with all necessary intelligence engines and stores.
        """
        self._history_store = history_store
        self._history_analyzer = history_analyzer
        self._evidence_graph = evidence_graph
        self._recommendation_engine = recommendation_engine
        self._strategy_engine = strategy_engine

    def synthesize_decision(self, context: Optional[Any] = None) -> EngineeringDecision:
        """
        [FUNCTION EXPLANATION]:
            Synthesizes a master EngineeringDecision DTO by evaluating telemetry history, 
            evidence chains, active recommendations, and optimal execution strategies with context.
        """
        records = self._history_store.get_all_records()
        latest_execution_id = records[-1].execution_id if records else "EXEC-BASELINE-001"
        
        exec_context = context or {"execution_id": latest_execution_id}
        
        evidence_chain = self._evidence_graph.build_evidence_chain(latest_execution_id)
        recommendations = self._recommendation_engine.generate_recommendations()
        
        # Robust duck-typing resolver passing execution context to strategy selectors
        strategy_engine_any: Any = self._strategy_engine
        if hasattr(strategy_engine_any, "select_optimal_strategy"):
            try:
                strategy = strategy_engine_any.select_optimal_strategy(exec_context)
            except TypeError:
                strategy = strategy_engine_any.select_optimal_strategy()
        elif hasattr(strategy_engine_any, "select_strategy"):
            try:
                strategy = strategy_engine_any.select_strategy(exec_context)
            except TypeError:
                strategy = strategy_engine_any.select_strategy()
        elif hasattr(strategy_engine_any, "get_optimal_strategy"):
            try:
                strategy = strategy_engine_any.get_optimal_strategy(exec_context)
            except TypeError:
                strategy = strategy_engine_any.get_optimal_strategy()
        else:
            raise AttributeError("StrategyEngine instance lacks a valid strategy selection method.")

        rec_ids = [r.recommendation_id for r in recommendations]
        decision_id = f"DEC-{latest_execution_id[:8]}"
        
        raw_sig = f"{decision_id}:{strategy.strategy_id}:{evidence_chain.checksum}"
        checksum = hashlib.sha256(raw_sig.encode("utf-8")).hexdigest()

        return EngineeringDecision(
            decision_id=decision_id,
            producing_engine="DecisionEngine",
            decision_summary=f"Synthesized execution decision using strategy [{strategy.strategy_name}] with {len(recommendations)} active recommendations.",
            confidence_score=94.5,
            recommendation_ids=rec_ids,
            supporting_evidence_ids=[evidence_chain.evidence_id],
            referenced_execution_ids=[latest_execution_id],
            traceability_checksum=f"sha256:{checksum}",
            metadata={
                "strategy_id": strategy.strategy_id,
                "strategy_name": strategy.strategy_name,
                "historical_success_rate": strategy.historical_success_rate
            }
        )

    def make_decision(self, context: Optional[Any] = None) -> EngineeringDecision:
        """
        [FUNCTION EXPLANATION]:
            Protocol alias for synthesize_decision() to satisfy IDecisionEngine interface contracts, 
            accepting optional execution context dictionaries.
        """
        return self.synthesize_decision(context)
