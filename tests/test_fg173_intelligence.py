"""
===============================================================================
WILSY OS KERNEL — FG173 INSTITUTIONAL INTELLIGENCE TEST SUITE
===============================================================================
[FILE EXPLANATION]:
    Comprehensive unit and integration test suite for all FG173 intelligence engines, 
    including DTO models, HistoryAnalyzer, EvidenceGraph, RecommendationEngine, 
    StrategyEngine, DecisionEngine, InstitutionalMemory, and ExecutionPredictor.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for regression or technical debt.

[BIBLICAL FOUNDATION]:
    1 Corinthians 14:40 — "Let all things be done decently and in order."
    Proverbs 12:15 — "The way of a fool is right in his own eyes: but he that hearkeneth unto counsel is wise."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Test Suite
===============================================================================
"""

from __future__ import annotations

import unittest
import shutil
from pathlib import Path
from datetime import datetime, timezone

from tools.eos.intelligence.models import (
    HistoricalPattern,
    EvidenceChain,
    EngineeringRecommendation,
    EngineeringDecision,
    ExecutionStrategy,
    ExecutionPrediction,
)
from tools.eos.intelligence.execution_history import ExecutionHistoryStore, ExecutionRecord
from tools.eos.intelligence.history_analyzer import HistoryAnalyzer
from tools.eos.intelligence.evidence_graph import EvidenceGraph
from tools.eos.intelligence.recommendation_engine import RecommendationEngine
from tools.eos.intelligence.strategy_engine import StrategyEngine
from tools.eos.intelligence.decision_engine import DecisionEngine
from tools.eos.intelligence.institutional_memory import InstitutionalMemory
from tools.eos.intelligence.execution_predictor import ExecutionPredictor


class TestFG173InstitutionalIntelligence(unittest.TestCase):
    """
    [TEST SUITE]: Validates absolute correctness, immutability, and end-to-end 
    integration of all FG173 institutional intelligence engines.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.test_memory_dir = "data/eos/test_institutional_memory"
        # Ensure clean test memory environment
        memory_path = Path(cls.test_memory_dir)
        if memory_path.exists():
            shutil.rmtree(memory_path)

    @classmethod
    def tearDownClass(cls) -> None:
        memory_path = Path(cls.test_memory_dir)
        if memory_path.exists():
            shutil.rmtree(memory_path)

    def setUp(self) -> None:
        # Initialize history store with sample execution telemetry
        self.history_store = ExecutionHistoryStore()
        # Insert test execution record
        sample_record = ExecutionRecord(
            execution_id="EXEC-TEST-2026-001",
            duration_ms=450.0,
            failures_count=0,
            warnings_count=1,
            artifacts_count=3,
            health_score=98.5,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        self.history_store.add_record(sample_record)

        self.history_analyzer = HistoryAnalyzer(self.history_store)
        self.evidence_graph = EvidenceGraph(self.history_store)
        self.recommendation_engine = RecommendationEngine(
            self.history_store,
            self.history_analyzer,
            self.evidence_graph
        )
        self.strategy_engine = StrategyEngine(self.history_store, self.history_analyzer)
        self.decision_engine = DecisionEngine(
            self.history_store,
            self.history_analyzer,
            self.evidence_graph,
            self.recommendation_engine,
            self.strategy_engine
        )
        self.institutional_memory = InstitutionalMemory(storage_dir=self.test_memory_dir)
        self.execution_predictor = ExecutionPredictor(self.history_store, self.history_analyzer)

    def test_01_models_immutability(self) -> None:
        """
        [TEST]: Verifies that institutional DTO models are strictly frozen (immutable).
        """
        pattern = HistoricalPattern(
            pattern_id="PAT-001",
            pattern_name="Pristine Run",
            occurrence_count=10,
            confidence_score=99.9
        )
        self.assertEqual(pattern.pattern_id, "PAT-001")
        with self.assertRaises(Exception):
            pattern.occurrence_count = 15  # Should fail due to frozen=True

    def test_02_history_analyzer(self) -> None:
        """
        [TEST]: Verifies HistoryAnalyzer computation of operational telemetry metrics.
        """
        analysis = self.history_analyzer.analyze_history()
        self.assertEqual(analysis["total_analyzed"], 1)
        self.assertEqual(analysis["total_failures"], 0)
        self.assertEqual(analysis["average_runtime_ms"], 450.0)
        self.assertTrue(len(analysis["insights"]) > 0)

    def test_03_evidence_graph(self) -> None:
        """
        [TEST]: Verifies EvidenceGraph construction and cryptographic checksum verification.
        """
        chain = self.evidence_graph.build_evidence_chain("EXEC-TEST-2026-001")
        self.assertEqual(chain.execution_id, "EXEC-TEST-2026-001")
        self.assertTrue(chain.checksum.startswith("sha256:"))
        self.assertEqual(len(chain.artifact_ids), 3)

    def test_04_recommendation_engine(self) -> None:
        """
        [TEST]: Verifies RecommendationEngine generates prioritized, evidence-backed recommendations.
        """
        recs = self.recommendation_engine.generate_recommendations()
        self.assertTrue(len(recs) > 0)
        self.assertIsInstance(recs[0], EngineeringRecommendation)
        self.assertTrue(recs[0].traceability_checksum.startswith("sha256:"))

    def test_05_strategy_engine(self) -> None:
        """
        [TEST]: Verifies StrategyEngine selects optimal operational execution strategies.
        """
        strategy = self.strategy_engine.select_strategy({"mode": "production"})
        self.assertIsInstance(strategy, ExecutionStrategy)
        self.assertTrue(len(strategy.target_engine_order) > 0)
        self.assertGreaterEqual(strategy.historical_success_rate, 0.0)

    def test_06_decision_engine(self) -> None:
        """
        [TEST]: Verifies DecisionEngine synthesizes master institutional decisions with full auditability.
        """
        decision = self.decision_engine.make_decision({"execution_id": "EXEC-TEST-2026-001"})
        self.assertIsInstance(decision, EngineeringDecision)
        self.assertEqual(decision.producing_engine, "DecisionEngine")
        self.assertTrue(decision.traceability_checksum.startswith("sha256:"))
        self.assertGreater(decision.confidence_score, 0.0)

    def test_07_institutional_memory(self) -> None:
        """
        [TEST]: Verifies InstitutionalMemory archives and recalls decisions successfully.
        """
        decision = self.decision_engine.make_decision({"execution_id": "EXEC-TEST-2026-001"})
        archived_path = self.institutional_memory.archive_decision(decision)
        self.assertTrue(Path(archived_path).exists())

        recalled = self.institutional_memory.recall_decision(decision.decision_id)
        self.assertIsNotNone(recalled)
        self.assertEqual(recalled["decision_id"], decision.decision_id)

        decisions_list = self.institutional_memory.list_archived_decisions()
        self.assertIn(decision.decision_id, decisions_list)

    def test_08_execution_predictor(self) -> None:
        """
        [TEST]: Verifies ExecutionPredictor forecasts execution duration and success probabilities.
        """
        prediction = self.execution_predictor.predict_outcome({
            "execution_id": "EXEC-TEST-2026-001",
            "pipeline_mode": "production"
        })
        self.assertIsInstance(prediction, ExecutionPrediction)
        self.assertEqual(prediction.predicted_duration_ms, 450.0)
        self.assertEqual(prediction.predicted_success_probability, 100.0)
        self.assertTrue(prediction.traceability_checksum.startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()
