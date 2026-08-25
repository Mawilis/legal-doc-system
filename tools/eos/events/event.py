"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Institutional Event Bus - Immutable Event Record (FG161).
    Encapsulates event telemetry, unique IDs, execution context, timestamps, and payload data
    into a cryptographically verifiable frozen structure.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready immutable event envelope. Zero mutation after dispatch.
    Proverbs 12:17 - "Whoever speaks the truth gives honest evidence..."

Collaboration & Maintenance:
    - [Architecture]: Immutable event carrier for publisher-subscriber messaging across the Event Bus.
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

from tools.eos.events.event_types import EventType


@dataclass(frozen=True)
class Event:
    """
    Immutable event message envelope published across the institutional event bus.

    Attributes:
        event_id (str): Unique cryptographic identifier for the event instance.
        event_type (EventType | str): Institutional classification of the event.
        execution_id (str): Associated execution session identifier.
        timestamp (str): ISO-8601 UTC timestamp of emission.
        producer (str): Identifier of the engine or service emitting the event.
        payload (Dict[str, Any]): Immutable data payload carried by the event.
        checksum (str): SHA-256 cryptographic hash of event contents.
        version (str): Event schema version string.
    """

    event_id: str
    event_type: EventType | str
    execution_id: str
    timestamp: str
    producer: str
    payload: Dict[str, Any]
    checksum: str
    version: str = "1.0.0"

    # [FUNCTION EXPLANATION]: Factory constructor sealing an event with a SHA-256 cryptographic checksum.
    @classmethod
    def create(
        cls,
        event_type: EventType | str,
        producer: str,
        payload: Dict[str, Any],
        execution_id: Optional[str] = None,
        event_id: Optional[str] = None,
        version: str = "1.0.0",
    ) -> Event:
        """
        Creates an immutable Event instance with automatic ID, execution tracking, timestamp, and SHA-256 checksum generation.

        Args:
            event_type (EventType | str): Classification of the event.
            producer (str): Originating engine or publisher ID.
            payload (Dict[str, Any]): Event data dictionary.
            execution_id (Optional[str]): Active execution session ID; auto-generated if omitted.
            event_id (Optional[str]): Explicit ID override; auto-generates if omitted.
            version (str): Schema version string.

        Returns:
            Event: Sealed, immutable Event instance.
        """
        gen_event_id = event_id or f"evt-{uuid.uuid4().hex[:12]}"
        gen_execution_id = execution_id or f"exec-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        type_val = event_type.value if isinstance(event_type, EventType) else event_type

        checksum = cls._compute_checksum(gen_event_id, type_val, gen_execution_id, timestamp, producer, payload)

        return cls(
            event_id=gen_event_id,
            event_type=type_val,
            execution_id=gen_execution_id,
            timestamp=timestamp,
            producer=producer,
            payload=payload,
            checksum=checksum,
            version=version,
        )

    # [FUNCTION EXPLANATION]: Computes SHA-256 checksum over event attributes.
    @staticmethod
    def _compute_checksum(
        event_id: str,
        event_type: str,
        execution_id: str,
        timestamp: str,
        producer: str,
        payload: Dict[str, Any],
    ) -> str:
        """Calculates cryptographic SHA-256 integrity digest for the event."""
        data = {
            "event_id": event_id,
            "event_type": event_type,
            "execution_id": execution_id,
            "timestamp": timestamp,
            "producer": producer,
            "payload": payload,
        }
        serialized = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()

    # [FUNCTION EXPLANATION]: Verifies event cryptographic integrity.
    def verify_integrity(self) -> bool:
        """Validates that current event contents match the recorded cryptographic checksum."""
        type_val = self.event_type.value if isinstance(self.event_type, EventType) else self.event_type
        computed = self._compute_checksum(
            self.event_id, type_val, self.execution_id, self.timestamp, self.producer, self.payload
        )
        return computed == self.checksum
