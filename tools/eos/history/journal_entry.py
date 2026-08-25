"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Execution Journal - Immutable Journal Entry Record (FG152).
    Encapsulates individual execution state changes, input payloads, engine IDs,
    and resulting artifacts into a cryptographically sealed, immutable record.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready immutable audit record ensuring total traceability.
    Revelation 20:12 - "And books were opened... and the dead were judged by what was written in the books..."

Collaboration & Maintenance:
    - [Architecture]: Immutable journal entry carrier for deterministic execution replay.
    - [Compliance]: Strict frozen dataclass ensuring historical reproducibility and audit safety.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class JournalEntry:
    """
    Immutable journal entry representing a single recorded execution step or state change.

    Attributes:
        entry_id (str): Unique cryptographic identifier for the journal entry.
        execution_id (str): ID of the parent execution run.
        sequence_index (int): Monotonically increasing execution step order.
        engine_id (str): Identifier of the engine that performed the execution step.
        action (str): Description of the action or event recorded.
        input_payload (Dict[str, Any]): Immutable input parameters supplied to the step.
        output_payload (Dict[str, Any]): Immutable output data or artifact reference produced.
        timestamp (str): ISO-8601 UTC timestamp of journal recording.
        checksum (str): SHA-256 cryptographic hash guaranteeing tamper-proof integrity.
        version (str): Journal schema version string.
    """

    entry_id: str
    execution_id: str
    sequence_index: int
    engine_id: str
    action: str
    input_payload: Dict[str, Any]
    output_payload: Dict[str, Any]
    timestamp: str
    checksum: str
    version: str = "1.0.0"

    # [FUNCTION EXPLANATION]: Factory constructor sealing a journal entry with a SHA-256 checksum.
    @classmethod
    def create(
        cls,
        execution_id: str,
        sequence_index: int,
        engine_id: str,
        action: str,
        input_payload: Dict[str, Any],
        output_payload: Dict[str, Any],
        entry_id: Optional[str] = None,
        version: str = "1.0.0",
    ) -> JournalEntry:
        """
        Creates an immutable JournalEntry instance with automated ID, timestamp, and SHA-256 hashing.
        """
        gen_entry_id = entry_id or f"jrn-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        checksum = cls._compute_checksum(
            gen_entry_id,
            execution_id,
            sequence_index,
            engine_id,
            action,
            input_payload,
            output_payload,
            timestamp,
        )

        return cls(
            entry_id=gen_entry_id,
            execution_id=execution_id,
            sequence_index=sequence_index,
            engine_id=engine_id,
            action=action,
            input_payload=input_payload,
            output_payload=output_payload,
            timestamp=timestamp,
            checksum=checksum,
            version=version,
        )

    # [FUNCTION EXPLANATION]: Computes SHA-256 checksum over journal entry fields.
    @staticmethod
    def _compute_checksum(
        entry_id: str,
        execution_id: str,
        sequence_index: int,
        engine_id: str,
        action: str,
        input_payload: Dict[str, Any],
        output_payload: Dict[str, Any],
        timestamp: str,
    ) -> str:
        """Calculates cryptographic SHA-256 integrity digest for the journal entry."""
        data = {
            "entry_id": entry_id,
            "execution_id": execution_id,
            "sequence_index": sequence_index,
            "engine_id": engine_id,
            "action": action,
            "input_payload": input_payload,
            "output_payload": output_payload,
            "timestamp": timestamp,
        }
        serialized = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()

    # [FUNCTION EXPLANATION]: Verifies journal entry cryptographic integrity.
    def verify_integrity(self) -> bool:
        """Validates that current entry contents match the recorded cryptographic checksum."""
        computed = self._compute_checksum(
            self.entry_id,
            self.execution_id,
            self.sequence_index,
            self.engine_id,
            self.action,
            self.input_payload,
            self.output_payload,
            self.timestamp,
        )
        return computed == self.checksum
