"""
===============================================================================
WILSY OS KERNEL — EXECUTION HISTORY STORE (FG173)
===============================================================================
[FILE EXPLANATION]:
    Provides institutional execution history storage, indexing, and telemetry lookup
    for Wilsy OS intelligence engines. Exports ExecutionRecord and ExecutionRecordDTO
    directly from this module to fully satisfy all test module import contracts.

[BIBLICAL FOUNDATION]:
    Proverbs 16:11 — "A just weight and balance are the Lord's..."
    Colossians 3:23 — "And whatsoever ye do, do it heartily, as to the Lord..."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Immutable Core
===============================================================================
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ExecutionRecord:
    """
    [CLASS SPECIFICATION]: ExecutionRecord
    Represents an immutable telemetry record of a system execution.
    """
    execution_id: str
    status: str = "SUCCESS"
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Additional fields for test compatibility
    health_score: float = 100.0
    artifacts_count: int = 0
    execution_checksum: str = ""
    engine_names: List[str] = field(default_factory=list)
    failure_count: int = 0
    warning_count: int = 0
    fingerprint: str = ""


# Alias ExecutionRecordDTO to ExecutionRecord for test suite compatibility
ExecutionRecordDTO = ExecutionRecord


class ExecutionHistoryStore:
    """
    [CLASS SPECIFICATION]: ExecutionHistoryStore
    Manages immutable execution telemetry records with comprehensive lookup,
    addition, indexing, and retrieval capabilities for Wilsy OS.
    """

    def __init__(self) -> None:
        """
        [CONSTRUCTOR]: Initializes an empty execution history store and record index mapping.
        """
        self.records: List[Any] = []
        self._record_map: Dict[str, Any] = {}
        logger.info("ExecutionHistoryStore initialized successfully.")

    def add_record(self, record: Any) -> None:
        """
        [METHOD]: Adds an execution record to the store and indexes it by execution ID.
        """
        self.records.append(record)
        exec_id = getattr(record, "execution_id", None)
        if exec_id:
            self._record_map[str(exec_id)] = record
        logger.debug("Added execution record: %s", exec_id or "unknown")

    def record_execution(self, record: Any) -> None:
        """
        [METHOD]: Alias for add_record to maintain backward compatibility across modules.
        """
        self.add_record(record)

    def get_record(self, execution_id: str) -> Optional[Any]:
        """
        [METHOD]: Retrieves a specific execution record by its unique identifier.
        """
        if execution_id in self._record_map:
            return self._record_map[execution_id]

        for record in self.records:
            if getattr(record, "execution_id", None) == execution_id:
                return record
            if isinstance(record, dict) and record.get("execution_id") == execution_id:
                return record

        logger.warning("Execution record not found for ID: %s", execution_id)
        return None

    def total_count(self) -> int:
        """
        [METHOD]: Returns the total number of recorded executions.
        """
        return len(self.records)

    def get_all(self) -> List[Any]:
        """
        [METHOD]: Returns all stored execution records.
        """
        return list(self.records)

    def get_all_records(self) -> List[Any]:
        """
        [METHOD]: Alias for get_all supporting institutional analyzer contracts.
        """
        return self.get_all()

    def clear(self) -> None:
        """
        [METHOD]: Clears all records and indices from the store.
        """
        self.records.clear()
        self._record_map.clear()
        logger.debug("Execution history store cleared.")
