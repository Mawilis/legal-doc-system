"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG210 INSTITUTIONAL DOCUMENTATION ENGINE
FILE: tools/eos/documentation/documentation_registry.py
===============================================================================
Epitome:
    Centralized, thread-safe registry maintaining every documented entity across
    the Wilsy OS sovereign operating system. Serves as the authoritative source
    of truth for subsystem cataloging, searching, indexing, and coverage audit.

Biblical Worth Billions:
    "Every thing shall live whither the river cometh." — Ezekiel 47:9

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/documentation/documentation_registry.py
===============================================================================
"""

import threading
from typing import Dict, List, Optional, Any
from tools.eos.documentation.documentation_contract import DocumentationEntity, EntityKind, VerificationStatus


class DocumentationRegistry:
    """
    Thread-safe institutional registry for indexing, querying, and searching
    all documented components in Wilsy OS.
    """

    _instance: Optional["DocumentationRegistry"] = None
    _lock: threading.Lock = threading.Lock()

    def __init__(self) -> None:
        self._registry: Dict[str, DocumentationEntity] = {}
        self._rw_lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> "DocumentationRegistry":
        """Retrieves or initializes the global singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def register(self, entity: DocumentationEntity) -> bool:
        """
        Registers a documented entity into the central catalog after schema validation.

        Args:
            entity: Validated DocumentationEntity contract instance.

        Returns:
            True if successfully registered.

        Raises:
            ValueError: If validation fails.
        """
        entity.validate()
        with self._rw_lock:
            self._registry[entity.urn] = entity
            return True

    def get_by_urn(self, urn: str) -> Optional[DocumentationEntity]:
        """Retrieves an entity by its unique documentation URN."""
        with self._rw_lock:
            return self._registry.get(urn)

    def get_by_kind(self, kind: EntityKind) -> List[DocumentationEntity]:
        """Filters all entities matching a specific EntityKind."""
        with self._rw_lock:
            return [e for e in self._registry.values() if e.kind == kind]

    def search(self, query: str) -> List[DocumentationEntity]:
        """
        Performs full-text case-insensitive searching across titles, purposes,
        module paths, and URNs.
        """
        q = query.lower().strip()
        if not q:
            return []
        with self._rw_lock:
            return [
                e for e in self._registry.values()
                if q in e.title.lower() or q in e.purpose.lower() or q in e.module_path.lower() or q in e.urn.lower()
            ]

    def list_all(self) -> List[DocumentationEntity]:
        """Returns a complete list of all registered documentation entities."""
        with self._rw_lock:
            return list(self._registry.values())

    def count(self) -> int:
        """Returns total registered entity count."""
        with self._rw_lock:
            return len(self._registry)

    def clear(self) -> None:
        """Clears the registry state (primarily used in test suites)."""
        with self._rw_lock:
            self._registry.clear()
