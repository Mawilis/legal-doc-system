"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Execution Journal - Journal Serializer & Deserializer (FG152).
    Provides robust, deterministic JSON serialization and cryptographic integrity
    validation for JournalEntry objects and complete execution journals.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready serialization engine ensuring data fidelity across persistence layers.
    Psalm 119:160 - "The sum of your word is truth, and every one of your righteous rules endures forever."

Collaboration & Maintenance:
    - [Architecture]: Serialization and deserialization contract for execution history.
    - [Compliance]: Strict type safety and cryptographic checksum verification upon load.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from tools.eos.history.journal_entry import JournalEntry


class JournalSerializer:
    """
    Serializer and deserializer for JournalEntry instances and execution journals.
    """

    # [FUNCTION EXPLANATION]: Serializes a single JournalEntry into a JSON-formatted string.
    @staticmethod
    def serialize_entry(entry: JournalEntry) -> str:
        """
        Converts an immutable JournalEntry into a canonical, sorted JSON string.

        Args:
            entry (JournalEntry): The entry to serialize.

        Returns:
            str: JSON representation of the journal entry.
        """
        data = {
            "entry_id": entry.entry_id,
            "execution_id": entry.execution_id,
            "sequence_index": entry.sequence_index,
            "engine_id": entry.engine_id,
            "action": entry.action,
            "input_payload": entry.input_payload,
            "output_payload": entry.output_payload,
            "timestamp": entry.timestamp,
            "checksum": entry.checksum,
            "version": entry.version,
        }
        return json.dumps(data, sort_keys=True, default=str)

    # [FUNCTION EXPLANATION]: Deserializes and verifies a JSON string into a JournalEntry instance.
    @staticmethod
    def deserialize_entry(json_str: str) -> JournalEntry:
        """
        Parses a JSON string into a JournalEntry and verifies its cryptographic checksum.

        Args:
            json_str (str): JSON-formatted string representing a journal entry.

        Returns:
            JournalEntry: Reconstituted, verified immutable JournalEntry.

        Raises:
            ValueError: If the entry checksum fails integrity verification.
        """
        data = json.loads(json_str)

        entry = JournalEntry(
            entry_id=data["entry_id"],
            execution_id=data["execution_id"],
            sequence_index=data["sequence_index"],
            engine_id=data["engine_id"],
            action=data["action"],
            input_payload=data["input_payload"],
            output_payload=data["output_payload"],
            timestamp=data["timestamp"],
            checksum=data["checksum"],
            version=data.get("version", "1.0.0"),
        )

        if not entry.verify_integrity():
            raise ValueError(f"Integrity violation detected for journal entry: {entry.entry_id}")

        return entry

    # [FUNCTION EXPLANATION]: Serializes an entire list of journal entries into a JSON array string.
    @staticmethod
    def serialize_journal(entries: List[JournalEntry]) -> str:
        """
        Serializes a sequence of journal entries into a formatted JSON array string.
        """
        serialized_entries = [json.loads(JournalSerializer.serialize_entry(e)) for e in entries]
        return json.dumps(serialized_entries, sort_keys=True, default=str, indent=2)

    # [FUNCTION EXPLANATION]: Deserializes a JSON array string into a list of verified JournalEntry instances.
    @staticmethod
    def deserialize_journal(json_str: str) -> List[JournalEntry]:
        """
        Parses a JSON array string into a list of verified JournalEntry instances.
        """
        raw_list = json.loads(json_str)
        return [JournalSerializer.deserialize_entry(json.dumps(item)) for item in raw_list]
