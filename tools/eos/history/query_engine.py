"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Query Engine - Institutional Search & Historical Intelligence Interface (FG163).
    Combines Execution Store and Execution Index to provide advanced multi-criteria
    searching, filtering, and telemetry analytics across Wilsy OS.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional query processing. Searching truth across records.
    Proverbs 25:2 - "It is the glory of God to conceal things, but the glory of kings is to search things out."

Collaboration & Maintenance:
    - [Architecture]: High-performance search interface unifying store and index.
    - [Compliance]: Thread-safe filtering, aggregation, and analytical telemetry.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple, Set

from tools.eos.history.execution_store import ExecutionStore, ExecutionRecord
from tools.eos.history.execution_index import ExecutionIndex

logger = logging.getLogger("WilsyOS.QueryEngine")


class QueryEngine:
    """
    Institutional search and analytics engine enabling complex queries
    over historical execution records.
    """

    def __init__(self, store: ExecutionStore, index: ExecutionIndex) -> None:
        """
        Initializes the Query Engine with store and index references.

        Args:
            store (ExecutionStore): Persistence store instance.
            index (ExecutionIndex): Indexing engine instance.
        """
        self._store = store
        self._index = index

    # [FUNCTION EXPLANATION]: Persists and indexes a record transactionally.
    def record_and_index(self, record: ExecutionRecord) -> None:
        """Saves an execution record into the store and updates all search indices."""
        self._store.save(record)
        self._index.index_record(record)
        logger.debug(f"Recorded and indexed execution ID: [{record.execution_id}]")

    # [FUNCTION EXPLANATION]: Searches execution records based on multiple filter criteria.
    def query(
        self,
        engine_id: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> Tuple[ExecutionRecord, ...]:
        """
        Queries historical execution records with optional filters for engine ID,
        status, and payload keyword search.

        Args:
            engine_id (Optional[str]): Filter by originating engine ID.
            status (Optional[str]): Filter by execution status.
            keyword (Optional[str]): Optional keyword search term within payload or error.

        Returns:
            Tuple[ExecutionRecord, ...]: Filtered tuple of matching ExecutionRecords.
        """
        candidate_ids: Optional[Set[str]] = None

        if engine_id:
            engine_matches = self._index.find_by_engine(engine_id)
            candidate_ids = engine_matches if candidate_ids is None else candidate_ids.intersection(engine_matches)

        if status:
            status_matches = self._index.find_by_status(status)
            candidate_ids = status_matches if candidate_ids is None else candidate_ids.intersection(status_matches)

        # Retrieve records from store based on filtered candidates or all records with strict type narrowing
        if candidate_ids is not None:
            fetched = [self._store.get(eid) for eid in candidate_ids]
            records: List[ExecutionRecord] = [r for r in fetched if r is not None]
        else:
            records = list(self._store.list_all())

        # Apply secondary keyword filtering if requested
        if keyword:
            kw_lower = keyword.lower()
            filtered_records: List[ExecutionRecord] = []
            for rec in records:
                payload_str = str(rec.payload).lower()
                error_str = (rec.error or "").lower()
                if kw_lower in payload_str or kw_lower in error_str or kw_lower in rec.execution_id.lower():
                    filtered_records.append(rec)
            records = filtered_records

        # Sort chronologically by start_time
        records.sort(key=lambda r: r.start_time)
        return tuple(records)

    # [FUNCTION EXPLANATION]: Computes statistical metrics across historical executions.
    def get_statistics(self) -> Dict[str, Any]:
        """
        Computes aggregate metrics including total runs, success rates,
        and status distributions across historical execution memory.

        Returns:
            Dict[str, Any]: Summary statistics dictionary.
        """
        all_records = self._store.list_all()
        total_runs = len(all_records)
        if total_runs == 0:
            return {"total_runs": 0, "success_rate": 0.0, "status_breakdown": {}}

        status_counts: Dict[str, int] = {}
        for rec in all_records:
            status_counts[rec.status] = status_counts.get(rec.status, 0) + 1

        success_count = status_counts.get("success", 0) + status_counts.get("completed", 0)
        success_rate = (success_count / total_runs) * 100.0

        return {
            "total_runs": total_runs,
            "success_rate": round(success_rate, 2),
            "status_breakdown": status_counts,
        }
