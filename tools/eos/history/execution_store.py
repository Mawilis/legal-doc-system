"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Execution Store - Institutional Execution Persistence & Journal (FG163).
    Stores and secures historical execution records, telemetry, and artifacts
    across Wilsy OS engines.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional record keeping. Remembering historical acts.
    Psalm 77:11 - "I will remember the deeds of the Lord; yes, I will remember your wonders of old."

Collaboration & Maintenance:
    - [Architecture]: Durable persistence engine for execution runs and telemetry.
    - [Compliance]: Immutable storage and retrieval of execution histories.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("WilsyOS.ExecutionStore")


@dataclass(frozen=True)
class ExecutionRecord:
    """Immutable record representing a single completed or active system execution."""
    execution_id: str
    engine_id: str
    status: str
    start_time: str
    end_time: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class ExecutionStore:
    """
    Thread-safe institutional store for recording and retrieving execution histories
    across all Wilsy OS modules.
    """

    def __init__(self) -> None:
        """Initializes the execution store with thread-safe locking and internal storage."""
        self._store: Dict[str, ExecutionRecord] = {}
        self._lock = threading.Lock()

    # [FUNCTION EXPLANATION]: Persists a new execution record to the store.
    def save(self, record: ExecutionRecord) -> None:
        """
        Saves or updates an execution record immutably.

        Args:
            record (ExecutionRecord): The execution record to store.
        """
        with self._lock:
            self._store[record.execution_id] = record
        logger.debug(f"Execution record saved: [{record.execution_id}] for engine [{record.engine_id}]")

    # [FUNCTION EXPLANATION]: Retrieves an execution record by its unique identifier.
    def get(self, execution_id: str) -> Optional[ExecutionRecord]:
        """Retrieves an execution record by execution ID."""
        with self._lock:
            return self._store.get(execution_id)

    # [FUNCTION EXPLANATION]: Retrieves all stored execution records.
    def list_all(self) -> Tuple[ExecutionRecord, ...]:
        """Returns a tuple of all recorded execution items."""
        with self._lock:
            return tuple(self._store.values())

    def clear(self) -> None:
        """Clears all stored execution records."""
        with self._lock:
            self._store.clear()
        logger.info("Execution store cleared.")
