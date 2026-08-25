"""
===============================================================================
WILSY ENGINEERING KERNEL — INSTITUTIONAL MEMORY
===============================================================================
Epitome:
    Long-term institutional memory engine providing historical comparisons across
    Execution #1 through Execution #N.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Foundation:
    Deuteronomy 32:7 — "Remember the days of old, consider the years of many generations..."

Collaboration & Maintenance:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from tools.eos.intelligence.execution_history import ExecutionRecordDTO, ExecutionHistoryStore
from tools.eos.intelligence.execution_snapshot import ExecutionSnapshotDTO

logger = logging.getLogger("WilsyOS.Intelligence.Memory")


class InstitutionalMemory:
    """
    [CLASS EXPLANATION]: Manages long-term institutional memory, enabling cross-execution
    auditing, comparative trend analysis, and historical retrieval.
    """

    def __init__(self, history_store: ExecutionHistoryStore) -> None:
        self.history_store = history_store
        self._snapshots: Dict[str, ExecutionSnapshotDTO] = {}
        logger.info("Initialized InstitutionalMemory.")

    def store_snapshot(self, snapshot: ExecutionSnapshotDTO) -> None:
        """
        [FUNCTION EXPLANATION]: Stores an immutable execution snapshot in long-term memory.
        """
        self._snapshots[snapshot.execution_id] = snapshot
        logger.info(f"Stored institutional snapshot for execution [{snapshot.execution_id}].")

    def get_snapshot(self, execution_id: str) -> Optional[ExecutionSnapshotDTO]:
        """
        [FUNCTION EXPLANATION]: Retrieves a historical snapshot by execution ID.
        """
        return self._snapshots.get(execution_id)

    def compare_executions(self, exec_id_a: str, exec_id_b: str) -> Dict[str, Any]:
        """
        [FUNCTION EXPLANATION]: Performs a rigorous comparative delta analysis between
        two historical executions across memory.
        """
        rec_a = self.history_store.get_record(exec_id_a)
        rec_b = self.history_store.get_record(exec_id_b)

        if not rec_a or not rec_b:
            logger.warning(f"Comparison failed: one or both records [{exec_id_a}, {exec_id_b}] missing.")
            return {"error": "One or both execution records not found in institutional memory."}

        # Use getattr with defaults to avoid missing attribute errors
        duration_a = getattr(rec_a, "duration_ms", 0.0)
        duration_b = getattr(rec_b, "duration_ms", 0.0)
        health_a = getattr(rec_a, "health_score", 100.0)
        health_b = getattr(rec_b, "health_score", 100.0)
        artifacts_a = getattr(rec_a, "artifacts_count", 0)
        artifacts_b = getattr(rec_b, "artifacts_count", 0)
        checksum_a = getattr(rec_a, "execution_checksum", "")
        checksum_b = getattr(rec_b, "execution_checksum", "")

        return {
            "comparison": {
                "execution_a": exec_id_a,
                "execution_b": exec_id_b,
                "duration_delta_ms": round(duration_b - duration_a, 2),
                "health_score_delta": round(health_b - health_a, 2),
                "artifact_count_delta": artifacts_b - artifacts_a,
                "checksum_changed": checksum_a != checksum_b
            }
        }
