"""
===============================================================================
WILSY OS KERNEL — FG173 INSTITUTIONAL MEMORY TEST SUITE
===============================================================================
[EPITOME]:
    Validates the Institutional Memory Engine (FG173), ensuring immutable record archival, 
    multi-dimensional indexing, keyword search accuracy, and statistical telemetry computation.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for regression or unverified memory retrieval.

[BIBLICAL FOUNDATION]:
    Psalm 77:11 — "I will remember the works of the Lord; surely I will remember thy wonders of old."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Institutional Memory Tests
===============================================================================
"""

from __future__ import annotations

import unittest
import hashlib
from tools.eos.memory import (
    MemoryRecord,
    MemoryStore,
    MemoryIndex,
    MemorySearchEngine,
    MemoryStatisticsCalculator,
)


class TestFG173InstitutionalMemory(unittest.TestCase):
    """
    [TEST SUITE]: FG173 Institutional Memory Engine Verification
    """

    def setUp(self) -> None:
        """
        [FUNCTION EXPLANATION]: Sets up fresh memory store, index, search, and stats engines.
        """
        self.store = MemoryStore()
        self.index = MemoryIndex()
        self.search_engine = MemorySearchEngine(self.store, self.index)
        self.stats_calculator = MemoryStatisticsCalculator(self.store)

        # Seed sample immutable memory records
        raw_payload = "exec_id:EXEC-MEM-001:decision"
        checksum = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

        self.record_1 = MemoryRecord(
            record_id="REC-001",
            execution_id="EXEC-MEM-001",
            record_type="DECISION",
            producer="DecisionEngine",
            title="Institutional Architecture Decision",
            payload={"strategy": "AggressiveOptimization"},
            tags=["architecture", "decision", "fg173"],
            checksum=checksum
        )

        self.record_2 = MemoryRecord(
            record_id="REC-002",
            execution_id="EXEC-MEM-001",
            record_type="ARTIFACT",
            producer="ArtifactPipeline",
            title="Generated System Specification Artifact",
            payload={"format": "pdf"},
            tags=["artifact", "spec", "fg173"],
            checksum=checksum
        )

        self.store.store(self.record_1)
        self.index.index_record(self.record_1)

        self.store.store(self.record_2)
        self.index.index_record(self.record_2)

    def test_01_memory_record_immutability(self) -> None:
        """
        [TEST]: Verifies MemoryRecord DTO immutability (frozen config).
        """
        self.assertEqual(self.record_1.record_id, "REC-001")
        with self.assertRaises(Exception):
            self.record_1.title = "Tampered Title"

    def test_02_memory_store_retrieval(self) -> None:
        """
        [TEST]: Verifies MemoryStore storage and record retrieval functions.
        """
        retrieved = self.store.get_record("REC-001")
        self.assertIsNotNone(retrieved)
        assert retrieved is not None, "Retrieved record should not be None"
        self.assertEqual(retrieved.title, "Institutional Architecture Decision")
        
        exec_records = self.store.get_records_by_execution("EXEC-MEM-001")
        self.assertEqual(len(exec_records), 2)

    def test_03_memory_index_lookup(self) -> None:
        """
        [TEST]: Verifies MemoryIndex multi-dimensional set lookups.
        """
        decision_ids = self.index.get_record_ids_by_type("DECISION")
        self.assertIn("REC-001", decision_ids)

        tag_ids = self.index.get_record_ids_by_tag("architecture")
        self.assertIn("REC-001", tag_ids)

        exec_ids = self.index.get_record_ids_by_execution("EXEC-MEM-001")
        self.assertEqual(len(exec_ids), 2)

    def test_04_memory_search_engine(self) -> None:
        """
        [TEST]: Verifies MemorySearchEngine filters and keyword queries.
        """
        results_by_type = self.search_engine.search(record_type="ARTIFACT")
        self.assertEqual(len(results_by_type), 1)
        self.assertEqual(results_by_type[0].record_id, "REC-002")

        results_by_keyword = self.search_engine.search(query_text="Architecture")
        self.assertEqual(len(results_by_keyword), 1)
        self.assertEqual(results_by_keyword[0].record_id, "REC-001")

    def test_05_memory_statistics(self) -> None:
        """
        [TEST]: Verifies MemoryStatisticsCalculator computes accurate executive metrics.
        """
        stats = self.stats_calculator.compute_statistics()
        self.assertEqual(stats["total_institutional_records"], 2)
        self.assertEqual(stats["unique_executions_recorded"], 1)
        self.assertEqual(stats["record_type_distribution"]["DECISION"], 1)
        self.assertEqual(stats["record_type_distribution"]["ARTIFACT"], 1)
        self.assertIn("architecture", stats["tag_distribution"])


if __name__ == "__main__":
    unittest.main()
