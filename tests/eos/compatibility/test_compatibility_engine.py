"""
===============================================================================
WILSY OS — COMPATIBILITY ENGINE TEST SUITE (FG208)
===============================================================================
Epitome:
    Automated test suite validating end-to-end functionality of Kernel FG208 
    Compatibility & Version Negotiation. Tests ABI resolution, adapter translation, 
    capability negotiation, error rejection, and report artifact integrity.

Biblical Worth Billions:
    "Thy word is true from the beginning: and every one of thy righteous 
    judgments endureth for ever."
    — Psalm 119:160

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tests/eos/compatibility/test_compatibility_engine.py
===============================================================================
"""

import unittest
from tools.eos.compatibility import (
    CompatibilityEngine,
    EngineCompatibilityBlock,
    CompatibilityStatus,
    CapabilityRegistry,
    AdapterManager,
    CompatibilityReportBuilder,
)


class TestCompatibilityEngine(unittest.TestCase):
    """
    Test suite for Wilsy OS FG208 Compatibility & Version Negotiation Engine.
    """

    def setUp(self) -> None:
        """Initializes compatibility engine fixture before each test case."""
        self.engine = CompatibilityEngine()

    def test_native_abi_v2_compatible(self) -> None:
        """Verifies that native ABI v2.0 engines evaluate to COMPATIBLE."""
        block = EngineCompatibilityBlock(
            engine_id="ENG-ANALYSIS-V2",
            engine_version="2.1.0",
            abi_version="2.0",
            minimum_kernel_version="2.0.0",
            maximum_kernel_version="3.0.0",
            required_capabilities=["ExecutionContext", "EventBus"],
            optional_capabilities=["DigitalTwin"]
        )
        result = self.engine.evaluate_engine("EXEC-101", block)
        self.assertEqual(result.decision.status, CompatibilityStatus.COMPATIBLE)
        self.assertTrue(result.decision.verify_checksum())
        self.assertEqual(result.decision.adapter_selected, "ADAPTER-ABI-V2-NATIVE")

    def test_abi_v1_adapter_required(self) -> None:
        """Verifies that legacy ABI v1.0 engines trigger ADAPTER_REQUIRED status."""
        block = EngineCompatibilityBlock(
            engine_id="ENG-LEGACY-ANALYSIS",
            engine_version="1.4.2",
            abi_version="1.0",
            minimum_kernel_version="1.0.0",
            maximum_kernel_version="3.0.0",
            required_capabilities=["ExecutionContext"],
            optional_capabilities=[]
        )
        result = self.engine.evaluate_engine("EXEC-102", block)
        self.assertEqual(result.decision.status, CompatibilityStatus.ADAPTER_REQUIRED)
        self.assertEqual(result.decision.adapter_selected, "ADAPTER-ABI-V1-TO-V2")
        self.assertTrue(result.decision.verify_checksum())

    def test_incompatible_missing_required_capability(self) -> None:
        """Verifies that engines requiring unfulfilled capabilities are marked INCOMPATIBLE."""
        block = EngineCompatibilityBlock(
            engine_id="ENG-QUANTUM-AUDIT",
            engine_version="3.0.0",
            abi_version="2.0",
            minimum_kernel_version="2.0.0",
            maximum_kernel_version="3.0.0",
            required_capabilities=["ExecutionContext", "QuantumDecryption"],
            optional_capabilities=[]
        )
        result = self.engine.evaluate_engine("EXEC-103", block)
        self.assertEqual(result.decision.status, CompatibilityStatus.INCOMPATIBLE)
        self.assertIn("QuantumDecryption", result.decision.missing_capabilities)

    def test_incompatible_kernel_bounds(self) -> None:
        """Verifies that engines with incompatible kernel version bounds return INCOMPATIBLE."""
        block = EngineCompatibilityBlock(
            engine_id="ENG-FUTURE-SPEC",
            engine_version="5.0.0",
            abi_version="2.0",
            minimum_kernel_version="3.0.0",
            maximum_kernel_version="4.0.0",
            required_capabilities=["ExecutionContext"],
            optional_capabilities=[]
        )
        result = self.engine.evaluate_engine("EXEC-104", block)
        self.assertEqual(result.decision.status, CompatibilityStatus.INCOMPATIBLE)

    def test_rejected_malformed_descriptor(self) -> None:
        """Verifies that malformed or incomplete engine descriptors yield REJECTED status."""
        block = EngineCompatibilityBlock(
            engine_id="",
            engine_version="1.0.0",
            abi_version="2.0",
            minimum_kernel_version="1.0.0",
            maximum_kernel_version="3.0.0"
        )
        result = self.engine.evaluate_engine("EXEC-105", block)
        self.assertEqual(result.decision.status, CompatibilityStatus.REJECTED)

    def test_report_artifact_generation(self) -> None:
        """Verifies end-to-end transformation of evaluation results into signed report artifacts."""
        block = EngineCompatibilityBlock(
            engine_id="ENG-REPORT-TEST",
            engine_version="2.0.0",
            abi_version="2.0",
            minimum_kernel_version="2.0.0",
            maximum_kernel_version="3.0.0",
            required_capabilities=["ExecutionContext"]
        )
        result = self.engine.evaluate_engine("EXEC-106", block)
        artifact = CompatibilityReportBuilder.build_report_artifact(result)
        
        self.assertEqual(artifact.execution_id, "EXEC-106")
        self.assertEqual(artifact.schema_version, "compatibility_report_v1")
        self.assertEqual(artifact.decision, CompatibilityStatus.COMPATIBLE.value)
        self.assertIsNotNone(artifact.sha256)


if __name__ == "__main__":
    unittest.main()
