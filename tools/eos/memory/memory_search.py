"""
===============================================================================
WILSY OS KERNEL — INSTITUTIONAL MEMORY SEARCH ENGINE
===============================================================================
[EPITOME]:
    Provides high-performance multi-criteria querying, keyword matching, and filtered 
    search over institutional memory records.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for query latency or unverified filters.

[BIBLICAL FOUNDATION]:
    Proverbs 25:2 — "It is the glory of God to conceal a matter, but the glory of kings is to search out a matter."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Memory Search
===============================================================================
"""

from __future__ import annotations

from typing import List, Optional
from tools.eos.memory.memory_store import MemoryStore
from tools.eos.memory.memory_index import MemoryIndex
from tools.eos.memory.memory_record import MemoryRecord


class MemorySearchEngine:
    """
    [ENGINE SPECIFICATION]: Institutional Memory Search Engine
    Executes advanced queries against the MemoryStore utilizing MemoryIndex accelerations.
    """

    def __init__(self, store: MemoryStore, index: MemoryIndex) -> None:
        """
        [FUNCTION EXPLANATION]:
            Initializes the MemorySearchEngine with a MemoryStore and MemoryIndex instance.
        """
        self._store = store
        self._index = index

    def search(
        self,
        query_text: Optional[str] = None,
        record_type: Optional[str] = None,
        execution_id: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[MemoryRecord]:
        """
        [FUNCTION EXPLANATION]:
            Searches institutional memory records matching optional text keywords, 
            record types, execution IDs, and tags.
        """
        candidate_ids: Optional[set[str]] = None

        if record_type:
            type_matches = self._index.get_record_ids_by_type(record_type)
            candidate_ids = type_matches if candidate_ids is None else candidate_ids.intersection(type_matches)

        if execution_id:
            exec_matches = self._index.get_record_ids_by_execution(execution_id)
            candidate_ids = exec_matches if candidate_ids is None else candidate_ids.intersection(exec_matches)

        if tag:
            tag_matches = self._index.get_record_ids_by_tag(tag)
            candidate_ids = tag_matches if candidate_ids is None else candidate_ids.intersection(tag_matches)

        if candidate_ids is not None:
            records = [self._store.get_record(rid) for rid in candidate_ids]
            results = [r for r in records if r is not None]
        else:
            results = self._store.get_all_records()

        # Apply text filter if provided
        if query_text:
            query_lower = query_text.lower()
            filtered = []
            for r in results:
                if (
                    query_lower in r.title.lower()
                    or query_lower in r.producer.lower()
                    or any(query_lower in t.lower() for t in r.tags)
                ):
                    filtered.append(r)
            results = filtered

        return results
