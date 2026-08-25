"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Execution Index - Institutional Indexing Engine for Execution Memory (FG163).
    Provides fast attribute-based indexing (by engine, status, timestamp)
    for historical execution records across Wilsy OS.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional indexing. Organizing records for instant recall.
    1 Chronicles 12:32 - "Of Issachar, men who had understanding of the times, to know what Israel ought to do..."

Collaboration & Maintenance:
    - [Architecture]: In-memory indexing engine supporting high-speed multi-criteria lookups.
    - [Compliance]: Thread-safe index updates synchronized with ExecutionStore.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import threading
from typing import Dict, List, Set, Tuple

from tools.eos.history.execution_store import ExecutionRecord

logger = logging.getLogger("WilsyOS.ExecutionIndex")


class ExecutionIndex:
    """
    Institutional index maintaining fast lookup structures (by engine_id, status)
    over historical execution records.
    """

    def __init__(self) -> None:
        """Initializes thread-safe index lookups."""
        self._engine_index: Dict[str, Set[str]] = {}
        self._status_index: Dict[str, Set[str]] = {}
        self._lock = threading.Lock()

    # [FUNCTION EXPLANATION]: Indexes an execution record across various attributes.
    def index_record(self, record: ExecutionRecord) -> None:
        """
        Adds an execution record to the search indices.

        Args:
            record (ExecutionRecord): The execution record to index.
        """
        with self._lock:
            eid = record.execution_id
            
            # Index by engine_id
            if record.engine_id not in self._engine_index:
                self._engine_index[record.engine_id] = set()
            self._engine_index[record.engine_id].add(eid)

            # Index by status
            if record.status not in self._status_index:
                self._status_index[record.status] = set()
            self._status_index[record.status].add(eid)

        logger.debug(f"Indexed execution record [{eid}]")

    # [FUNCTION EXPLANATION]: Removes a record from the indices.
    def remove_record(self, record: ExecutionRecord) -> None:
        """Removes an execution record from all indices."""
        with self._lock:
            eid = record.execution_id
            if record.engine_id in self._engine_index:
                self._engine_index[record.engine_id].discard(eid)
            if record.status in self._status_index:
                self._status_index[record.status].discard(eid)

    # [FUNCTION EXPLANATION]: Finds execution IDs matching a specific engine ID.
    def find_by_engine(self, engine_id: str) -> Set[str]:
        """Returns execution IDs associated with a given engine ID."""
        with self._lock:
            return set(self._engine_index.get(engine_id, set()))

    # [FUNCTION EXPLANATION]: Finds execution IDs matching a specific status.
    def find_by_status(self, status: str) -> Set[str]:
        """Returns execution IDs associated with a given status."""
        with self._lock:
            return set(self._status_index.get(status, set()))

    def clear(self) -> None:
        """Clears all index structures."""
        with self._lock:
            self._engine_index.clear()
            self._status_index.clear()
        logger.info("Execution index cleared.")
