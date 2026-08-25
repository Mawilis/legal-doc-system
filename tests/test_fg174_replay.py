"""
===============================================================================
WILSY OS KERNEL — FG174 EXECUTION REPLAY TEST SUITE
===============================================================================
[EPITOME]:
    Validates the Execution Replay Engine (FG174), ensuring deterministic execution replay, 
    artifact isolation, decision auditing, and chronological timeline reconstruction.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for regression or unverified replays.

[BIBLICAL FOUNDATION]:
    Job 8:8 — "For inquire, please, of the former age, and consider the things searched out by their fathers."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Replay Test Suite
===============================================================================
"""

from __future__ import annotations

import unittest
import hashlib
from tools.eos.memory import MemoryStore, MemoryRecord
from tools.eos.replay import (
    ExecutionReplayEngine,
    ArtifactReplayEngine,
    DecisionReplayEngine,
    ExecutionTimelineReplay,
)


class TestFG174ExecutionReplay(unittest.TestCase):
    """
    [TEST SUITE]: FG174 Execution Replay Engine Verification
    """

    def setUp(self) -> None:
        """
        [FUNCTION EXPLANATION]: Sets up fresh memory store and replay engines with seeded telemetry records.
        """
        self.store = MemoryStore()
        self.replay_engine = ExecutionReplayEngine(self.store)
        self.artifact_engine = ArtifactReplayEngine(self.store)
        self.decision_engine = DecisionReplayEngine(self.store)
        self.timeline_engine = ExecutionTimelineReplay(self.store)

        checksum = hashlib.sha256(b"replay-test-payload").hexdigest()

        # Seed records for execution EXEC-REPLAY-999
        self.rec_1 = MemoryRecord(
            record_id="REC-R-001",
            execution_id="EXEC-REPLAY-999",
            record_type="EXECUTION",
            producer="Scheduler",
            title="Execution Dispatched",
            payload={"status": "STARTED"},
            tags=["dispatch", "execution"],
            checksum=checksum,
            timestamp="2026-07-22T08:00:00Z"
        )

        self.rec_2 = MemoryRecord(
            record_id="REC-R-002",
            execution_id="EXEC-REPLAY-999",
            record_type="DECISION",
            producer="DecisionEngine",
            title="Institutional Strategy Selected",
            payload={"strategy_id": "STG-001"},
            tags=["decision", "strategy"],
            checksum=checksum,
            timestamp="2026-07-22T08:00:05Z"
        )

        self.rec_3 = MemoryRecord(
            record_id="REC-R-003",
            execution_id="EXEC-REPLAY-999",
            record_type="ARTIFACT",
            producer="ArtifactPipeline",
            title="Generated System PDF Specification",
            payload={"format": "pdf", "size_kb": 1024},
            tags=["artifact", "pdf"],
            checksum=checksum,
            timestamp="2026-07-22T08:00:10Z"
        )

        self.store.store(self.rec_1)
        self.store.store(self.rec_2)
        self.store.store(self.rec_3)

    def test_01_execution_replay_and_summary(self) -> None:
        """
        [TEST]: Verifies chronological execution replay and summary generation.
        """
        replayed = self.replay_engine.replay_execution("EXEC-REPLAY-999")
        self.assertEqual(len(replayed), 3)
        self.assertEqual(replayed[0].record_id, "REC-R-001")
        self.assertEqual(replayed[-1].record_id, "REC-R-003")

        summary = self.replay_engine.summarize_execution("EXEC-REPLAY-999")
        self.assertEqual(summary["status"], "REPLAY_READY")
        self.assertEqual(summary["total_records"], 3)
        self.assertIn("DecisionEngine", summary["producers"])

    def test_02_artifact_replay(self) -> None:
        """
        [TEST]: Verifies artifact replay engine isolates generated artifacts and payloads.
        """
        artifacts = self.artifact_engine.replay_artifacts("EXEC-REPLAY-999")
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].record_id, "REC-R-003")

        payloads = self.artifact_engine.get_artifact_payloads("EXEC-REPLAY-999")
        self.assertEqual(len(payloads), 1)
        self.assertEqual(payloads[0]["format"], "pdf")

    def test_03_decision_replay(self) -> None:
        """
        [TEST]: Verifies decision replay engine isolates and audits institutional decisions.
        """
        decisions = self.decision_engine.replay_decisions("EXEC-REPLAY-999")
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0].record_id, "REC-R-002")

        summaries = self.decision_engine.get_decision_summaries("EXEC-REPLAY-999")
        self.assertEqual(len(summaries), 1)
        self.assertEqual(summaries[0]["title"], "Institutional Strategy Selected")

    def test_04_execution_timeline_replay(self) -> None:
        """
        [TEST]: Verifies chronological execution timeline sequence generation.
        """
        timeline = self.timeline_engine.build_timeline("EXEC-REPLAY-999")
        self.assertEqual(len(timeline), 3)
        self.assertEqual(timeline[0]["sequence_index"], 1)
        self.assertEqual(timeline[0]["record_id"], "REC-R-001")
        self.assertEqual(timeline[2]["sequence_index"], 3)
        self.assertEqual(timeline[2]["record_id"], "REC-R-003")


if __name__ == "__main__":
    unittest.main()
