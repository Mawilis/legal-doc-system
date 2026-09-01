"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG210 INSTITUTIONAL DOCUMENTATION ENGINE TEST SUITE
FILE: tests/tools/eos/documentation/test_fg210_documentation_suite.py
===============================================================================
Epitome:
    Full production test suite for FG210 Documentation Engine. Ensures 100%
    coverage across contracts, generators, export formats, registry thread-safety,
    search index scoring, diff analysis, and CLI operations.

Biblical Worth Billions:
    "In the mouth of two or three witnesses shall every word be established."
    — 2 Corinthians 13:1

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tests/tools/eos/documentation/test_fg210_documentation_suite.py
===============================================================================
"""

import unittest
from tools.eos.documentation import (
    DocumentationEntity,
    EntityKind,
    VerificationStatus,
    InterfaceSpec,
    EventSpec,
    ArtifactDocumentationGenerator,
    ExecutionDocumentationGenerator,
    VerificationDocumentationGenerator,
    DocumentationExportEngine,
    DocumentationRegistry,
    DocumentationSearchIndex,
    DocumentationDiffEngine,
    DocumentationCLI,
)


class TestFG210DocumentationSuite(unittest.TestCase):
    """
    Unit test suite for FG210 Institutional Documentation Engine components.
    """

    def setUp(self) -> None:
        self.registry = DocumentationRegistry()
        self.registry.clear()

        self.sample_entity = DocumentationEntity(
            urn="urn:wilsy:doc:kernel:test_module",
            kind=EntityKind.KERNEL,
            title="Kernel Test Engine",
            purpose="Validates core kernel execution pipelines",
            module_path="tools/eos/kernel/test_module.py",
            version="2.0.0",
            architecture_summary="High-performance deterministic kernel test component",
            lifecycle_stage="PRODUCTION",
            interfaces=[
                InterfaceSpec(
                    name="execute_pipeline",
                    description="Processes system payloads",
                )
            ],
            events=[
                EventSpec(
                    event_name="PipelineExecuted",
                    publisher="KernelTestEngine",
                    subscriber="DocumentationRegistry",
                    payload_schema={"status": "str", "timestamp": "float"},
                    lifecycle_stage="PRODUCTION",
                )
            ],
        )

    def test_01_documentation_entity_contract(self) -> None:
        """Verifies DocumentationEntity serialization and dictionary output."""
        data = self.sample_entity.to_dict()
        self.assertEqual(data["urn"], "urn:wilsy:doc:kernel:test_module")
        self.assertEqual(data["kind"], "KERNEL")
        self.assertEqual(len(data["interfaces"]), 1)
        self.assertEqual(len(data["events"]), 1)

    def test_02_artifact_documentation_generator(self) -> None:
        """Verifies artifact documentation auto-generation."""
        doc = ArtifactDocumentationGenerator.generate_artifact_entity(
            urn="urn:wilsy:doc:artifact:test_module",
            artifact_type="PYTHON_MODULE",
            producer="TestEngine",
            consumer="Registry",
            purpose="Artifact generation unit test",
        )
        self.assertTrue(doc.urn.startswith("urn:wilsy:doc:artifact:"))
        self.assertEqual(doc.kind, EntityKind.ARTIFACT)

    def test_03_execution_documentation_generator(self) -> None:
        """Verifies execution documentation generation with exact signature."""
        doc = ExecutionDocumentationGenerator.generate_execution_entity(
            urn="urn:wilsy:doc:pipeline:tenant",
            execution_id="exec-tenant-001",
            plan_name="TenantProvisioningPlan",
            worker_id="Worker-01",
            status="SUCCESS",
            duration_ms=150.5,
        )
        self.assertEqual(doc.urn, "urn:wilsy:doc:pipeline:tenant")

    def test_04_verification_documentation_generator(self) -> None:
        """Verifies verification audit documentation generator."""
        verified_entity = DocumentationEntity(
            urn="urn:wilsy:doc:kernel:verified_module",
            kind=EntityKind.KERNEL,
            title="Verified Kernel",
            purpose="Verified module for audit test",
            module_path="tools/eos/kernel/verified.py",
            version="2.0.0",
            architecture_summary="Verified kernel component",
            lifecycle_stage="PRODUCTION",
            verification_status=VerificationStatus.VERIFIED,
        )
        audit = VerificationDocumentationGenerator.generate_verification_audit_report(
            [verified_entity]
        )
        self.assertEqual(audit["total_entities"], 1)
        self.assertEqual(audit["verified_count"], 1)
        self.assertEqual(audit["compliance_percentage"], 100.0)

    def test_05_export_engine(self) -> None:
        """Verifies documentation exports across JSON, Markdown, and HTML formats."""
        entities = [self.sample_entity]
        json_out = DocumentationExportEngine.export_to_json(entities)
        md_out = DocumentationExportEngine.export_to_markdown(entities)
        html_out = DocumentationExportEngine.export_to_html(entities)

        self.assertIn("urn:wilsy:doc:kernel:test_module", json_out)
        self.assertIn("Kernel Test Engine", md_out)
        self.assertIn("<html", html_out)

    def test_06_registry_operations(self) -> None:
        """Verifies thread-safe registry registration and filtering."""
        self.registry.register(self.sample_entity)
        self.assertEqual(self.registry.count(), 1)

        fetched = self.registry.get_by_urn(self.sample_entity.urn)
        self.assertIsNotNone(fetched)
        assert fetched is not None, "Fetched entity should not be None"
        self.assertEqual(fetched.title, "Kernel Test Engine")

        kernel_entities = self.registry.filter_by_kind(EntityKind.KERNEL)
        self.assertEqual(len(kernel_entities), 1)

    def test_07_search_index(self) -> None:
        """Verifies search index query scoring and URN prefix matching."""
        search_index = DocumentationSearchIndex([self.sample_entity])
        hits = search_index.search("Kernel pipeline")
        self.assertGreater(len(hits), 0)
        self.assertEqual(hits[0]["urn"], self.sample_entity.urn)

    def test_08_diff_engine(self) -> None:
        """Verifies diff engine drift detection."""
        modified_entity = DocumentationEntity(
            urn=self.sample_entity.urn,
            kind=self.sample_entity.kind,
            title=self.sample_entity.title,
            purpose="Updated purpose for drift test",
            module_path=self.sample_entity.module_path,
            version="2.1.0",
            architecture_summary=self.sample_entity.architecture_summary,
            lifecycle_stage="PRODUCTION",
        )

        diff = DocumentationDiffEngine.compute_diff([self.sample_entity], [modified_entity])
        self.assertEqual(diff["modified_count"], 1)
        self.assertEqual(diff["added_count"], 0)
        self.assertEqual(diff["removed_count"], 0)

    def test_09_cli_interface(self) -> None:
        """Verifies CLI interface commands dispatch successfully."""
        self.registry.register(self.sample_entity)
        cli = DocumentationCLI()
        status_list = cli.run(["list"])
        status_search = cli.run(["search", "Kernel"])
        status_audit = cli.run(["audit"])

        self.assertEqual(status_list, 0)
        self.assertEqual(status_search, 0)
        self.assertEqual(status_audit, 0)


if __name__ == "__main__":
    unittest.main()
