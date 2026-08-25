"""
===============================================================================
WILSY OS KERNEL — FG173 DECISION ENGINE CONTRACTS & PROTOCOLS
===============================================================================
[EPITOME]:
    Defines strict protocol interfaces and abstract base classes for all FG173 
    intelligence engines, guaranteeing type safety, immutability, and end-to-end 
    traceability across Wilsy OS.

[BIBLICAL FOUNDATION]:
    Proverbs 2:3-6 — "Yea, if thou criest after knowledge, and liftest up thy voice for understanding..."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Immutable Interface
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from tools.eos.intelligence.models import (
    EngineeringDecision,
    EngineeringRecommendation,
    ExecutionPrediction,
    EvidenceChain,
    ExecutionStrategy,
    HistoricalPattern,
)


class IHistoryAnalyzer(ABC):
    """
    [INTERFACE CONTRACT]: History Analyzer
    Responsibility: Consumes historical execution records, telemetry, and artifacts 
    to extract institutional insights and performance metrics.
    """

    @abstractmethod
    def analyze_history(self) -> Dict[str, Any]:
        """
        [CONTRACT METHOD]: Analyzes historical records and returns aggregated intelligence.
        """
        pass


class IEvidenceGraph(ABC):
    """
    [INTERFACE CONTRACT]: Evidence Graph Engine
    Responsibility: Constructs immutable evidence chains linking executions, events, 
    artifacts, reports, and recommendations for complete auditability.
    """

    @abstractmethod
    def build_evidence_chain(self, execution_id: str) -> EvidenceChain:
        """
        [CONTRACT METHOD]: Constructs and verifies the evidence chain for a given execution.
        """
        pass


class IRecommendationEngine(ABC):
    """
    [INTERFACE CONTRACT]: Recommendation Engine
    Responsibility: Generates prioritized, evidence-backed engineering recommendations 
    from historical telemetry and anomaly detection.
    """

    @abstractmethod
    def generate_recommendations(self) -> List[EngineeringRecommendation]:
        """
        [CONTRACT METHOD]: Produces actionable, high-priority engineering recommendations.
        """
        pass


class IStrategyEngine(ABC):
    """
    [INTERFACE CONTRACT]: Strategy Engine
    Responsibility: Selects the optimal execution strategy based on historical success rates 
    and pipeline context.
    """

    @abstractmethod
    def select_strategy(self, context: Dict[str, Any]) -> ExecutionStrategy:
        """
        [CONTRACT METHOD]: Determines and selects the optimal execution strategy.
        """
        pass


class IDecisionEngine(ABC):
    """
    [INTERFACE CONTRACT]: Master Decision Engine
    Responsibility: Synthesizes historical intelligence, evidence chains, and recommendations 
    into audited institutional engineering decisions.
    """

    @abstractmethod
    def make_decision(self, context: Dict[str, Any]) -> EngineeringDecision:
        """
        [CONTRACT METHOD]: Produces audited institutional engineering decisions with confidence scoring.
        """
        pass


class IExecutionPredictor(ABC):
    """
    [INTERFACE CONTRACT]: Execution Predictor
    Responsibility: Forecasts execution duration, failure risk, bottlenecks, missing dependencies, 
    and success probability prior to execution start.
    """

    @abstractmethod
    def predict_outcome(self, execution_context: Dict[str, Any]) -> ExecutionPrediction:
        """
        [CONTRACT METHOD]: Computes pre-execution telemetry forecasts and confidence scores.
        """
        pass
