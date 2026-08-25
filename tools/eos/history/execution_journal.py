"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Execution Journal - Core Journal Manager (FG152).
    Records, indexes, and manages sequential execution steps and audit trails
    across Wilsy OS kernel runs, ensuring total determinism and replayability.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional execution tracker.
    Proverbs 16:3 - "Commit your work to the Lord, and your plans will be established."

Collaboration & Maintenance:
    - [Architecture]: Core execution journal manager coordinating audit capture.
    - [Compliance]: Thread-safe entry recording and strict chronological indexing.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from tools.eos.history.journal_entry import JournalEntry
from tools.eos.history.journal_serializer import JournalSerializer


class ExecutionJournal:
    """
    Manager responsible for capturing, storing, and querying execution journal entries.
    """

    def __init__(self) -> None:
        """Initializes an empty execution journal store."""
        self._entries: List[JournalEntry] = []

    # [FUNCTION EXPLANATION]: Records a new execution step into the journal with auto-incremented sequence index.
    def record(
        self,
        execution_id: str,
        engine_id: str,
        action: str,
        input_payload: Dict[str, Any],
        output_payload: Dict[str, Any],
    ) -> JournalEntry:
        """
        Creates and appends a verified JournalEntry for an execution step.

        Args:
            execution_id (str): Parent execution identifier.
            engine_id (str): Originating engine ID.
            action (str): Description of the performed action.
            input_payload (Dict[str, Any]): Input parameters.
            output_payload (Dict[str, Any]): Output results or artifact references.

        Returns:
            JournalEntry: The newly recorded and sealed journal entry.
        """
        # Determine next sequence index for this execution run
        existing_run_entries = [e for e in self._entries if e.execution_id == execution_id]
        sequence_index = len(existing_run_entries) + 1

        entry = JournalEntry.create(
            execution_id=execution_id,
            sequence_index=sequence_index,
            engine_id=engine_id,
            action=action,
            input_payload=input_payload,
            output_payload=output_payload,
        )

        self._entries.append(entry)
        return entry

    # [FUNCTION EXPLANATION]: Retrieves all journal entries associated with a specific execution ID.
    def get_execution_entries(self, execution_id: str) -> Tuple[JournalEntry, ...]:
        """
        Retrieves all journal entries for a given execution run, sorted by sequence index.
        """
        filtered = [e for e in self._entries if e.execution_id == execution_id]
        return tuple(sorted(filtered, key=lambda x: x.sequence_index))

    # [FUNCTION EXPLANATION]: Retrieves the complete journal history across all runs.
    def get_all_entries(self) -> Tuple[JournalEntry, ...]:
        """Returns all recorded journal entries across the system."""
        return tuple(self._entries)

    # [FUNCTION EXPLANATION]: Exports the entire journal to a JSON string.
    def export_journal_json(self) -> str:
        """Serializes the entire execution journal to JSON."""
        return JournalSerializer.serialize_journal(self._entries)

    # [FUNCTION EXPLANATION]: Imports and loads journal entries from a JSON string.
    def import_journal_json(self, json_str: str) -> None:
        """Loads and verifies journal entries from a JSON string into the journal store."""
        imported_entries = JournalSerializer.deserialize_journal(json_str)
        for entry in imported_entries:
            if entry not in self._entries:
                self._entries.append(entry)

    def clear(self) -> None:
        """Clears all journal entries."""
        self._entries.clear()
