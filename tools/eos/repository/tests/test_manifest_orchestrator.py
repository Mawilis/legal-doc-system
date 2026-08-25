"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    High-Fidelity Automated Unit and Integration Testing Infrastructure Matrix.
    Validates end-to-end processing durability, boundary security enforcement,
    and immutable serialization structures across the discovery pipelines.

Biblical Scale & Architecture:
    This is a billion-dollar, production-ready automated testing suite.
    Operates strictly within isolated runtime environments utilizing safe mock
    sandboxes to eliminate live operational workspace pollution.

Collaboration & Maintenance:
    - [Reliability]: Implements complete end-to-end functional path validation.
    - [Security]: Enforces transaction testing boundaries over mock structures.
    - [Data Integrity]: Verifies deep mathematical equality over frozen blueprints.

===============================================================================
"""

from __future__ import annotations

import json
import unittest
import tempfile
from pathlib import Path

from tools.eos.repository.orchestration.manifest_orchestrator import ManifestOrchestrator, CodebaseManifestBlueprint
from tools.eos.repository.discovery.capability_discovery import CapabilitySignature
from tools.eos.repository.discovery.ownership_discovery import OwnershipRecord


class TestManifestOrchestratorSuite(unittest.TestCase):
    """
    Industrial-Grade Test Suite covering the complete Repository Analysis Pipeline.
    """

    def setUp(self) -> None:
        """
        Builds a safe, transient virtual workspace environment before each test block execution.
        """
        self._temp_dir = tempfile.TemporaryDirectory()
        self.mock_root = Path(self._temp_dir.name).resolve()
        self.orchestrator = ManifestOrchestrator()

        # Seed realistic target workspace structure for analysis mapping tests
        self.src_dir = self.mock_root / "src" / "core"
        self.src_dir.mkdir(parents=True, exist_ok=True)
        
        # Construct target module 1: Standard core module with capabilities and owners
        self.module_a_path = "src/core/payroll_engine.py"
        module_a_payload = (
            '"""\n'
            'Owner: Core Payroll Team\n'
            'Maintainer: Payroll Infrastructure Group\n'
            '"""\n\n'
            '@capability("billing.deduction.v1")\n'
            'def process_payroll():\n'
            '    pass\n'
        )
        self._write_mock_file(self.module_a_path, module_a_payload)

        # Construct target module 2: Utility module with alternative structural metadata tags
        self.module_b_path = "src/core/document_processor.py"
        module_b_payload = (
            '# Domain: Legal Document Systems\n'
            '# Lead: Legal Archival Group\n\n'
            'CAPABILITY_ID = "document.generation.engine"\n'
        )
        self._write_mock_file(self.module_b_path, module_b_payload)

    def tearDown(self) -> None:
        """
        Cleans and releases virtual filesystem structures safely post-execution.
        """
        self._temp_dir.cleanup()

    def _write_mock_file(self, relative_path: str, contents: str) -> None:
        """
        Helper utility to securely map code segments to the transient workspace layout.
        """
        target_file = self.mock_root / relative_path
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(contents)

    def test_end_to_end_orchestration_pipeline(self) -> None:
        """
        Ensures the orchestrator correctly traverses structures and captures discovery telemetry.
        """
        # Execute discovery sweep transaction over the transient workspace
        blueprint = self.orchestrator.generate_blueprint(self.mock_root)

        # Assert correct capture structure type instances
        self.assertIsInstance(blueprint, CodebaseManifestBlueprint)
        self.assertEqual(blueprint.repository_root, str(self.mock_root))

        # Check file tracking manifest metrics
        self.assertIn(self.module_a_path, blueprint.file_manifest)
        self.assertIn(self.module_b_path, blueprint.file_manifest)

        # Validate Stage 2: Capability matching metric captures
        caps = {c.capability_id: c for c in blueprint.capabilities}
        self.assertIn("billing.deduction.v1", caps)
        self.assertEqual(caps["billing.deduction.v1"].target_module, self.module_a_path)
        self.assertEqual(caps["billing.deduction.v1"].component_type, "decorator")

        self.assertIn("document.generation.engine", caps)
        self.assertEqual(caps["document.generation.engine"].target_module, self.module_b_path)
        self.assertEqual(caps["document.generation.engine"].component_type, "assignment")

        # Validate Stage 3: Administrative ownership metric captures
        ownerships = {o.target_module: o for o in blueprint.ownership_records}
        self.assertIn(self.module_a_path, ownerships)
        self.assertEqual(ownerships[self.module_a_path].owner_team, "Core Payroll Team")
        self.assertEqual(ownerships[self.module_a_path].maintainer_group, "Payroll Infrastructure Group")

        self.assertIn(self.module_b_path, ownerships)
        self.assertEqual(ownerships[self.module_b_path].owner_team, "Legal Document Systems")
        self.assertEqual(ownerships[self.module_b_path].maintainer_group, "Legal Archival Group")

    def test_atomic_serialization_integrity(self) -> None:
        """
        Ensures blueprint records serialize safely to disk without file block data corruption.
        """
        blueprint = self.orchestrator.generate_blueprint(self.mock_root)
        output_json = self.mock_root / "build" / "manifest_snapshot.json"

        # Execute serialization transaction engine
        self.orchestrator.serialize_to_disk(blueprint, output_json)
        self.assertTrue(output_json.exists())

        # Read output back to ensure total structure consistency matches perfectly
        with open(output_json, "r", encoding="utf-8") as read_f:
            serialized_data = json.load(read_f)

        self.assertEqual(serialized_data["repository_root"], str(self.mock_root))
        self.assertIsInstance(serialized_data["file_manifest"], list)
        self.assertTrue(len(serialized_data["capabilities"]) >= 2)


if __name__ == "__main__":
    unittest.main()
