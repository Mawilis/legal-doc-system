"""
===============================================================================
WILSY OS — INSTITUTIONAL VERSIONING ENGINE (FG209)
MODULE: AUTHORITATIVE VERSION REGISTRY
===============================================================================
Epitome:
    Authoritative state registry for versioning across Wilsy OS. Tracks active
    kernel versions, registered engine versions, schema versions, and their
    institutional classifications (Supported, Deprecated, Experimental, Removed).

Biblical Worth Billions:
    "The house of God, which is the church of the living God, the pillar and ground 
     of the truth." — 1 Timothy 3:15

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/versioning/version_registry.py
===============================================================================
"""

from __future__ import annotations

import threading
from typing import Dict, Set, Optional, List
from dataclasses import dataclass, field

from tools.eos.versioning.semantic_version import SemanticVersion
from tools.eos.versioning.version_identifier import VersionIdentifier, VersionKind


class VersionNotFoundError(KeyError):
    """Raised when a queried version is not found in the authoritative registry."""
    pass


class VersionAlreadyRegisteredError(ValueError):
    """Raised when attempting to register a duplicate entity version identifier."""
    pass


@dataclass
class RegisteredEntityRecord:
    """Immutable metadata record stored in the Version Registry for a given entity."""
    identifier: VersionIdentifier
    is_active: bool = True
    is_deprecated: bool = False
    is_experimental: bool = False
    is_removed: bool = False
    deprecation_reason: Optional[str] = None


class VersionRegistry:
    """
    Thread-safe, authoritative repository for all version knowledge in Wilsy OS.
    """

    def __init__(self, current_kernel_version: str = "2.0.0") -> None:
        self._lock = threading.RLock()
        self._current_kernel_version = SemanticVersion.parse(current_kernel_version)
        self._records: Dict[str, RegisteredEntityRecord] = {}

        # Pre-register current kernel
        kernel_id = VersionIdentifier.create(
            kind=VersionKind.KERNEL,
            name="wilsy_kernel",
            version=self._current_kernel_version
        )
        self._records[kernel_id.urn] = RegisteredEntityRecord(identifier=kernel_id)

    @property
    def current_kernel_version(self) -> SemanticVersion:
        """Returns the active kernel version."""
        with self._lock:
            return self._current_kernel_version

    def set_kernel_version(self, version: str) -> SemanticVersion:
        """Updates active kernel version in the registry."""
        with self._lock:
            parsed = SemanticVersion.parse(version)
            self._current_kernel_version = parsed
            kernel_id = VersionIdentifier.create(
                kind=VersionKind.KERNEL,
                name="wilsy_kernel",
                version=parsed
            )
            self._records[kernel_id.urn] = RegisteredEntityRecord(identifier=kernel_id)
            return parsed

    def register_entity(
        self,
        identifier: VersionIdentifier,
        is_experimental: bool = False,
        is_deprecated: bool = False,
        deprecation_reason: Optional[str] = None
    ) -> RegisteredEntityRecord:
        """
        Registers an entity version identifier with the authoritative registry.
        """
        with self._lock:
            urn = identifier.urn
            if urn in self._records:
                raise VersionAlreadyRegisteredError(f"Entity version '{urn}' is already registered.")

            record = RegisteredEntityRecord(
                identifier=identifier,
                is_active=True,
                is_deprecated=is_deprecated,
                is_experimental=is_experimental,
                is_removed=False,
                deprecation_reason=deprecation_reason
            )
            self._records[urn] = record
            return record

    def mark_deprecated(self, urn_or_identifier: str, reason: str) -> RegisteredEntityRecord:
        """Marks a registered entity version as deprecated."""
        with self._lock:
            urn = urn_or_identifier if isinstance(urn_or_identifier, str) else urn_or_identifier.urn
            if urn not in self._records:
                raise VersionNotFoundError(f"Version URN '{urn}' not registered.")

            rec = self._records[urn]
            updated = RegisteredEntityRecord(
                identifier=rec.identifier,
                is_active=rec.is_active,
                is_deprecated=True,
                is_experimental=rec.is_experimental,
                is_removed=rec.is_removed,
                deprecation_reason=reason
            )
            self._records[urn] = updated
            return updated

    def mark_removed(self, urn_or_identifier: str) -> RegisteredEntityRecord:
        """Marks a registered entity version as removed."""
        with self._lock:
            urn = urn_or_identifier if isinstance(urn_or_identifier, str) else urn_or_identifier.urn
            if urn not in self._records:
                raise VersionNotFoundError(f"Version URN '{urn}' not registered.")

            rec = self._records[urn]
            updated = RegisteredEntityRecord(
                identifier=rec.identifier,
                is_active=False,
                is_deprecated=rec.is_deprecated,
                is_experimental=rec.is_experimental,
                is_removed=True,
                deprecation_reason=rec.deprecation_reason
            )
            self._records[urn] = updated
            return updated

    def get_record(self, urn_or_identifier: str) -> RegisteredEntityRecord:
        """Retrieves record for a given URN."""
        with self._lock:
            urn = urn_or_identifier if isinstance(urn_or_identifier, str) else urn_or_identifier.urn
            if urn not in self._records:
                raise VersionNotFoundError(f"Version URN '{urn}' is not registered.")
            return self._records[urn]

    def list_registered_versions(self, kind: Optional[VersionKind] = None) -> List[RegisteredEntityRecord]:
        """Lists all registered version records, optionally filtered by VersionKind."""
        with self._lock:
            if kind is None:
                return list(self._records.values())
            return [r for r in self._records.values() if r.identifier.kind == kind]

    def clear(self) -> None:
        """Resets registry to initial state."""
        with self._lock:
            self._records.clear()
            kernel_id = VersionIdentifier.create(
                kind=VersionKind.KERNEL,
                name="wilsy_kernel",
                version=self._current_kernel_version
            )
            self._records[kernel_id.urn] = RegisteredEntityRecord(identifier=kernel_id)
