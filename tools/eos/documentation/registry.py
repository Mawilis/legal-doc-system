"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG210 INSTITUTIONAL DOCUMENTATION ENGINE
FILE: tools/eos/documentation/registry.py
===============================================================================
Epitome:
    Central sovereign registry and catalog repository for all DocumentationEntity
    contracts in Wilsy OS. Provides thread-safe registration, URN index lookups,
    kind query filters, dependency graph traversals, and lifecycle management.

Biblical Worth Billions:
    "Set thee up waymarks, make thee high heaps: set thine heart toward the highway..."
    — Jeremiah 31:21

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/documentation/registry.py
===============================================================================
"""

import threading
from typing import Dict, List, Optional, Set
from tools.eos.documentation.documentation_contract import (
    DocumentationEntity,
    EntityKind,
    VerificationStatus,
)


class DocumentationRegistry:
    """
    Sovereign in-memory documentation entity registry for Wilsy OS.
    Ensures thread-safe registration and deterministic query resolution.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DocumentationRegistry, cls).__new__(cls)
                cls._instance._registry: Dict[str, DocumentationEntity] = {}
                cls._instance._urn_index: Set[str] = set()
            return cls._instance

    def register(self, entity: DocumentationEntity) -> None:
        """
        Registers a DocumentationEntity into the global sovereign index.

        Args:
            entity: Validated DocumentationEntity contract instance.
        """
        with self._lock:
            self._registry[entity.urn] = entity
            self._urn_index.add(entity.urn)

    def get_by_urn(self, urn: str) -> Optional[DocumentationEntity]:
        """
        Retrieves a DocumentationEntity by its unique URN.

        Args:
            urn: Documentation entity URN string.

        Returns:
            DocumentationEntity instance or None if not registered.
        """
        with self._lock:
            return self._registry.get(urn)

    def list_all(self) -> List[DocumentationEntity]:
        """
        Returns all registered DocumentationEntity contracts in the registry.

        Returns:
            List of DocumentationEntity contracts.
        """
        with self._lock:
            return list(self._registry.values())

    def filter_by_kind(self, kind: EntityKind) -> List[DocumentationEntity]:
        """
        Filters registered entities by EntityKind classification.

        Args:
            kind: Target EntityKind enum value.

        Returns:
            List of matching DocumentationEntity contracts.
        """
        with self._lock:
            return [e for e in self._registry.values() if e.kind == kind]

    def filter_by_verification_status(self, status: VerificationStatus) -> List[DocumentationEntity]:
        """
        Filters registered entities by VerificationStatus.

        Args:
            status: Target VerificationStatus enum value.

        Returns:
            List of matching DocumentationEntity contracts.
        """
        with self._lock:
            return [e for e in self._registry.values() if e.verification_status == status]

    def count(self) -> int:
        """
        Returns the total number of registered documentation entities.

        Returns:
            Integer total count.
        """
        with self._lock:
            return len(self._registry)

    def clear(self) -> None:
        """
        Clears all registered entities from the sovereign registry.
        Used for system resets and testing cycles.
        """
        with self._lock:
            self._registry.clear()
            self._urn_index.clear()
