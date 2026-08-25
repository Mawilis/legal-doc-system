"""
===============================================================================
WILSY OS KERNEL — INSTITUTIONAL MEMORY INDEX
===============================================================================
[EPITOME]:
    Maintains multi-dimensional indexes of institutional memory records by category, 
    tags, record types, and execution IDs to enable lightning-fast retrieval.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for unindexed traversals.

[BIBLICAL FOUNDATION]:
    1 Chronicles 12:32 — "men who had understanding of the times, to know what Israel ought to do..."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Memory Index
===============================================================================
"""

from __future__ import annotations

from typing import Dict, List, Set
from tools.eos.memory.memory_record import MemoryRecord


class MemoryIndex:
    """
    [ENGINE SPECIFICATION]: Institutional Memory Index
    Builds and maintains inverted indexes over memory records for high-speed multi-attribute querying.
    """

    def __init__(self) -> None:
        self._type_index: Dict[str, Set[str]] = {}
        self._tag_index: Dict[str, Set[str]] = {}
        self._execution_index: Dict[str, Set[str]] = {}

    def index_record(self, record: MemoryRecord) -> None:
        """
        [FUNCTION EXPLANATION]:
            Indexes a MemoryRecord across type, tags, and execution ID dimensions.
        """
        # Type index
        if record.record_type not in self._type_index:
            self._type_index[record.record_type] = set()
        self._type_index[record.record_type].add(record.record_id)

        # Execution index
        if record.execution_id not in self._execution_index:
            self._execution_index[record.execution_id] = set()
        self._execution_index[record.execution_id].add(record.record_id)

        # Tag index
        for tag in record.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = set()
            self._tag_index[tag].add(record.record_id)

    def get_record_ids_by_type(self, record_type: str) -> Set[str]:
        """
        [FUNCTION EXPLANATION]:
            Returns all record IDs matching the specified record type.
        """
        return self._type_index.get(record_type, set())

    def get_record_ids_by_tag(self, tag: str) -> Set[str]:
        """
        [FUNCTION EXPLANATION]:
            Returns all record IDs matching the specified categorization tag.
        """
        return self._tag_index.get(tag, set())

    def get_record_ids_by_execution(self, execution_id: str) -> Set[str]:
        """
        [FUNCTION EXPLANATION]:
            Returns all record IDs associated with the specified execution ID.
        """
        return self._execution_index.get(execution_id, set())

    def clear(self) -> None:
        """
        [FUNCTION EXPLANATION]:
            Clears all indexing structures.
        """
        self._type_index.clear()
        self._tag_index.clear()
        self._execution_index.clear()
