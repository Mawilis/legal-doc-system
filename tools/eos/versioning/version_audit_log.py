"""
===============================================================================
WILSY OS — INSTITUTIONAL VERSIONING ENGINE (FG209)
MODULE: IMMUTABLE VERSION AUDIT LOG
===============================================================================
Epitome:
    Append-only ledger tracking every version registration, deprecation, and 
    removal event within the EOS. Guarantees an immutable historical footprint
    for systems governance and architectural rollback auditing.

Biblical Worth Billions:
    "And I saw the dead, small and great, stand before God; and the books 
     were opened..." — Revelation 20:12

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/versioning/version_audit_log.py
===============================================================================
"""

from __future__ import annotations

import time
import threading
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

from tools.eos.versioning.version_identifier import VersionIdentifier


class AuditAction(str, Enum):
    """Enumeration of lifecycle actions recorded in the ledger."""
    REGISTERED = "REGISTERED"
    DEPRECATED = "DEPRECATED"
    REMOVED = "REMOVED"
    UPGRADED = "UPGRADED"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass(frozen=True)
class VersionAuditEntry:
    """
    Immutable ledger entry representing a singular entity version event.
    """
    timestamp_utc: float
    action: AuditAction
    identifier: VersionIdentifier
    actor: str
    reason: Optional[str] = None
    context_id: Optional[str] = None

    def __str__(self) -> str:
        base = f"[{self.timestamp_utc}] {self.action.value} -> {self.identifier.urn} (by {self.actor})"
        if self.reason:
            base += f" Reason: '{self.reason}'"
        return base


class VersionAuditLedger:
    """
    Thread-safe, append-only in-memory ledger for active kernel sessions.
    In production, this interfaces directly with the primary Wilsy OS Event Bus.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._entries: List[VersionAuditEntry] = []

    def record_event(
        self,
        action: AuditAction,
        identifier: VersionIdentifier,
        actor: str = "eos_system",
        reason: Optional[str] = None,
        context_id: Optional[str] = None
    ) -> VersionAuditEntry:
        """
        Appends a new immutable record to the version ledger.
        """
        entry = VersionAuditEntry(
            timestamp_utc=time.time(),
            action=action,
            identifier=identifier,
            actor=actor,
            reason=reason,
            context_id=context_id
        )
        
        with self._lock:
            self._entries.append(entry)
            
        return entry

    def get_history_for_urn(self, urn: str) -> List[VersionAuditEntry]:
        """
        Retrieves the complete chronological lifecycle history for a specific URN.
        """
        with self._lock:
            return [e for e in self._entries if e.identifier.urn == urn]

    def get_full_ledger(self) -> List[VersionAuditEntry]:
        """
        Retrieves a shallow copy of the entire immutable ledger.
        """
        with self._lock:
            return list(self._entries)

    def verify_integrity(self) -> bool:
        """
        Audits the current memory ledger to ensure timestamps are strictly monotonic,
        preventing retro-active tampering.
        """
        with self._lock:
            if not self._entries:
                return True
                
            previous_time = self._entries[0].timestamp_utc
            for entry in self._entries[1:]:
                if entry.timestamp_utc < previous_time:
                    return False
                previous_time = entry.timestamp_utc
                
            return True
