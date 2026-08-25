"""
===============================================================================
WILSY OS KERNEL — DECISION REPLAY ENGINE
===============================================================================
[EPITOME]:
    Reconstructs and audits every institutional engineering decision and strategy choice 
    made during past execution cycles.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for unverified decision telemetry.

[BIBLICAL FOUNDATION]:
    Proverbs 16:3 — "Commit your works to the Lord, and your thoughts will be established."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Decision Replay
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List
from tools.eos.memory import MemoryStore, MemoryRecord


class DecisionReplayEngine:
    """
    [ENGINE SPECIFICATION]: Decision Replay Engine
    Extracts and audits all DECISION type memory records across execution runs.
    """

    def __init__(self, memory_store: MemoryStore) -> None:
        """
        [FUNCTION EXPLANATION]:
            Initializes the DecisionReplayEngine with an institutional MemoryStore.
        """
        self._memory_store = memory_store

    def replay_decisions(self, execution_id: str) -> List[MemoryRecord]:
        """
        [FUNCTION EXPLANATION]:
            Retrieves all DECISION type memory records for a specific execution run.
        """
        records = self._memory_store.get_records_by_execution(execution_id)
        return [r for r in records if r.record_type == "DECISION"]

    def get_decision_summaries(self, execution_id: str) -> List[Dict[str, Any]]:
        """
        [FUNCTION EXPLANATION]:
            Extracts decision titles, checksums, and structured payloads for executive review.
        """
        decisions = self.replay_decisions(execution_id)
        return [
            {
                "record_id": d.record_id,
                "title": d.title,
                "producer": d.producer,
                "checksum": d.checksum,
                "payload": d.payload
            }
            for d in decisions
        ]
