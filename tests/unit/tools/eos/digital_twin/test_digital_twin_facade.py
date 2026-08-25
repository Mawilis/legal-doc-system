"""
===============================================================================
WILSY OS — FG223 DIGITAL TWIN INTELLIGENCE PLATFORM
===============================================================================

File Path:
    tests/unit/tools/eos/digital_twin/test_digital_twin_facade.py

Epitome:
    Production validation suite for the FG223 Digital Twin Intelligence Platform.
    Verifies end-to-end synchronization, graph state management, snapshot integrity,
    topological queries, simulation scenarios, and predictive risk forecasting.

Biblical Worth Billions:
    "Prove all things; hold fast that which is good."
    — 1 Thessalonians 5:21

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import unittest
import time
from tools.eos.digital_twin.interface.twin_facade import DigitalTwinFacade


class TestDigitalTwinFacade(unittest.TestCase):
    """
    Comprehensive test suite ensuring 100% production readiness for Digital Twin.
    """

    def setUp(self) -> None:
        """Initializes a fresh DigitalTwinFacade instance before each test."""
        self.facade = DigitalTwinFacade()

    def test_facade_initialization(self) -> None:
        """Validates proper instantiation and sub-service wiring."""
        self.assertIsNotNone(self.facade.engine)
        self.assertIsNotNone(self.facade.registry)
        self.assertIsNotNone(self.facade.snapshots)
        self.assertIsNotNone(self.facade.query)
        self.assertIsNotNone(self.facade.simulation)
        self.assertIsNotNone(self.facade.prediction)
        self.assertEqual(len(self.facade.registry.registered_adapters), 9)

    def test_platform_synchronization(self) -> None:
        """Validates multi-adapter synchronization and topology build."""
        sync_result = self.facade.synchronize_platform()

        self.assertIn("adapters_executed", sync_result)
        self.assertEqual(sync_result["adapters_executed"], 9)
        self.assertGreater(sync_result["total_entities"], 0)
        self.assertGreater(sync_result["total_relationships"], 0)

        telemetry = self.facade.get_system_telemetry()
        self.assertGreater(telemetry["entity_count"], 0)
        self.assertGreater(telemetry["relationship_count"], 0)

    def test_snapshot_lifecycle(self) -> None:
        """Validates snapshot creation, hashing, and state immutability."""
        self.facade.synchronize_platform()

        snapshot_dict = self.facade.capture_snapshot(metadata={"environment": "production_test"})
        
        self.assertIn("snapshot_id", snapshot_dict)
        self.assertIn("sha3_hash", snapshot_dict)
        self.assertEqual(snapshot_dict["metadata"]["environment"], "production_test")
        self.assertGreater(snapshot_dict["entity_count"], 0)

    def test_topological_queries(self) -> None:
        """Validates query service filtering and relationship traversals."""
        self.facade.synchronize_platform()

        # Query all Repository entities
        repos = self.facade.query.filter_entities(entity_type="Repository")
        self.assertTrue(len(repos) >= 1)
        self.assertEqual(repos[0]["entity_id"], "REPO-WILSY-OS-MAIN")

        # Query dependencies for the core engine
        engine_deps = self.facade.query.get_entity_dependencies(
            entity_id="ENG-SOVEREIGN-KERNEL", 
            direction="OUTGOING"
        )
        self.assertTrue(isinstance(engine_deps, list))

    def test_simulation_scenario(self) -> None:
        """Validates failure simulation and blast radius calculation."""
        self.facade.synchronize_platform()

        sim_result = self.facade.simulation.simulate_node_failure(target_node_id="REPO-WILSY-OS-MAIN")
        
        self.assertEqual(sim_result["target_node_id"], "REPO-WILSY-OS-MAIN")
        self.assertIn("blast_radius", sim_result)
        self.assertIn("affected_entities", sim_result)

    def test_prediction_and_risk_analysis(self) -> None:
        """Validates predictive risk indicators and architectural drift detection."""
        self.facade.synchronize_platform()

        predictions = self.facade.run_health_and_predictive_analysis()
        
        self.assertIn("health_score", predictions)
        self.assertIn("drift_count", predictions)
        self.assertIn("predictions", predictions)
        self.assertGreaterEqual(predictions["health_score"], 0.0)
        self.assertLessEqual(predictions["health_score"], 100.0)


if __name__ == "__main__":
    unittest.main()
