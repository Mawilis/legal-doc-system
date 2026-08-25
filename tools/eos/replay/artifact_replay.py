"""
===============================================================================
WILSY OS KERNEL — ARTIFACT REPLAY ENGINE
===============================================================================
[EPITOME]:
    Isolates and replays all generated artifacts and system specifications produced 
    during any historic execution run.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for artifact corruption or missing telemetry.

[BIBLICAL FOUNDATION]:
    Proverbs 27:23 — "Be diligent to know the state of your flocks, and set your heart on your herds."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Artifact Replay
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List
from tools.eos.memory import MemoryStore, MemoryRecord


class ArtifactReplayEngine:
    """
    [ENGINE SPECIFICATION]: Artifact Replay Engine
    Extracts and replays all artifact records generated during execution runs.
    """

    def __init__(self, memory_store: MemoryStore) -> None:
        """
        [FUNCTION EXPLANATION]:
            Initializes the ArtifactReplayEngine with an institutional MemoryStore.
        """
        self._memory_store = memory_store

    def replay_artifacts(self, execution_id: str) -> List[MemoryRecord]:
        """
        [FUNCTION EXPLANATION]:
            Retrieves all ARTIFACT type memory records for a specific execution run.
        """
        records = self._memory_store.get_records_by_execution(execution_id)
        return [r for r in records if r.record_type == "ARTIFACT"]

    def get_artifact_payloads(self, execution_id: str) -> List[Dict[str, Any]]:
        """
        [FUNCTION EXPLANATION]:
            Extracts raw structured payloads from all replayed execution artifacts.
        """
        artifacts = self.replay_artifacts(execution_id)
        return [a.payload for a in artifacts]
