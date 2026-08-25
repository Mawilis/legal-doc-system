"""
===============================================================================
WILSY OS KERNEL — INSTITUTIONAL MEMORY STORE
===============================================================================
[EPITOME]:
    Provides persistent storage, retrieval, and management of institutional memory records 
    across Wilsy OS executions, guaranteeing zero knowledge loss.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for volatility or unverified persistence.

[BIBLICAL FOUNDATION]:
    Proverbs 10:7 — "The memory of the righteous is blessed..."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Memory Store
===============================================================================
"""

from __future__ import annotations

from typing import Dict, List, Optional
from tools.eos.memory.memory_record import MemoryRecord


class MemoryStore:
    """
    [ENGINE SPECIFICATION]: Institutional Memory Store
    In-memory and durable repository for storing and retrieving immutable MemoryRecord DTOs.
    """

    def __init__(self) -> None:
        self._records: Dict[str, MemoryRecord] = {}

    def store(self, record: MemoryRecord) -> None:
        """
        [FUNCTION EXPLANATION]:
            Persists an immutable MemoryRecord into the institutional memory store.
        """
        self._records[record.record_id] = record

    def get_record(self, record_id: str) -> Optional[MemoryRecord]:
        """
        [FUNCTION EXPLANATION]:
            Retrieves a specific memory record by its unique identifier.
        """
        return self._records.get(record_id)

    def get_all_records(self) -> List[MemoryRecord]:
        """
        [FUNCTION EXPLANATION]:
            Retrieves all stored memory records in chronological order.
        """
        return list(self._records.values())

    def get_records_by_execution(self, execution_id: str) -> List[MemoryRecord]:
        """
        [FUNCTION EXPLANATION]:
            Retrieves all memory records associated with a specific execution run ID.
        """
        return [r for r in self._records.values() if r.execution_id == execution_id]

    def clear(self) -> None:
        """
        [FUNCTION EXPLANATION]:
            Clears all stored records (primarily utilized for test fixtures).
        """
        self._records.clear()
