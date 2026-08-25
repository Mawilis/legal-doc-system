"""
===============================================================================
WILSY OS — FG221 CLUSTER ORCHESTRATOR SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/domain/worker_capabilities.py

Epitome:
    Thread-safe domain wrapper managing functional workload capabilities advertised 
    by compute workers for capability-based scheduling dispatch.

Biblical Worth Billions:
    "For unto one he gave five talents, to another two, and to another one; 
    to every man according to his several ability."
    — Matthew 25:15

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import threading
from typing import Set, Iterable, Union, List, Any


class StandardCapability:
    """Standard system capabilities advertised across Wilsy OS kernel workers."""
    REPOSITORY = "REPOSITORY"
    DOCUMENTATION = "DOCUMENTATION"
    VERSIONING = "VERSIONING"
    PREDICTION = "PREDICTION"
    AI = "AI"
    DIGITAL_TWIN = "DIGITAL_TWIN"
    MARKETPLACE = "MARKETPLACE"
    GOVERNANCE = "GOVERNANCE"
    COMPATIBILITY = "COMPATIBILITY"


class WorkerCapabilities:
    """
    Thread-safe container holding functional capability tags for a worker node.
    Supports seamless conversions to set/list representations for Pylance safety.
    """

    def __init__(self, initial_capabilities: Union[Set[str], List[str], Iterable[str], None] = None) -> None:
        self._lock = threading.RLock()
        self._capabilities: Set[str] = set()

        if initial_capabilities:
            if isinstance(initial_capabilities, (set, list, tuple)):
                self._capabilities.update(str(c).upper() for c in initial_capabilities)
            elif isinstance(initial_capabilities, WorkerCapabilities):
                self._capabilities.update(initial_capabilities.to_set())
            elif hasattr(initial_capabilities, "__iter__"):
                for cap in initial_capabilities:
                    self._capabilities.add(str(cap).upper())

    def add(self, capability: str) -> None:
        """Adds a capability tag."""
        with self._lock:
            self._capabilities.add(capability.upper())

    def remove(self, capability: str) -> None:
        """Removes a capability tag."""
        with self._lock:
            self._capabilities.discard(capability.upper())

    def has(self, capability: str) -> bool:
        """Checks if a single capability is present."""
        with self._lock:
            return capability.upper() in self._capabilities

    def contains_all(self, required_capabilities: Iterable[str]) -> bool:
        """Checks if all required capabilities are satisfied."""
        with self._lock:
            req_set = {str(c).upper() for c in required_capabilities}
            return req_set.issubset(self._capabilities)

    def to_set(self) -> Set[str]:
        """Returns a snapshot of capabilities as a set."""
        with self._lock:
            return set(self._capabilities)

    def to_list(self) -> List[str]:
        """Returns a snapshot of capabilities as a list."""
        with self._lock:
            return sorted(list(self._capabilities))

    def __iter__(self):
        """Allows direct iteration over capability strings."""
        with self._lock:
            return iter(list(self._capabilities))

    def __len__(self) -> int:
        with self._lock:
            return len(self._capabilities)

    def __repr__(self) -> str:
        with self._lock:
            return f"<WorkerCapabilities {sorted(list(self._capabilities))}>"
