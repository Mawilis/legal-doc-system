"""
===============================================================================
WILSY OS — FG220 PLUGIN RUNTIME DESCRIPTOR & LIFECYCLE MANAGER
===============================================================================

Epitome:
    Runtime descriptor and state lifecycle manager for FG220 marketplace plugins.
    Tracks active plugin instances, entrypoint module bindings, execution telemetry,
    latency records, isolation parameters, and state transition histories across
    the Wilsy OS platform runtime.

Biblical Worth Billions:
    "For which of you, intending to build a tower, sitteth not down first, and counteth 
    the cost, whether he have sufficient to finish it?"
    — Luke 14:28

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
    - File Path: tools/eos/marketplace/plugin_descriptor.py
===============================================================================
"""

import time
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from tools.eos.marketplace import logger
from tools.eos.marketplace.manifest import PluginManifest


class PluginState(str, Enum):
    """
    Authoritative lifecycle state enum for Wilsy OS marketplace plugins.
    """
    REGISTERED = "REGISTERED"
    VERIFIED = "VERIFIED"
    LOADING = "LOADING"
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    ERROR = "ERROR"


class StateTransitionError(Exception):
    """Exception raised when an invalid plugin state transition is attempted."""
    pass


# Allowed State Transition Map
VALID_TRANSITIONS: Dict[PluginState, List[PluginState]] = {
    PluginState.REGISTERED: [PluginState.VERIFIED, PluginState.ERROR, PluginState.DISABLED],
    PluginState.VERIFIED: [PluginState.LOADING, PluginState.ERROR, PluginState.DISABLED],
    PluginState.LOADING: [PluginState.ACTIVE, PluginState.ERROR, PluginState.DISABLED],
    PluginState.ACTIVE: [PluginState.DISABLED, PluginState.ERROR],
    PluginState.DISABLED: [PluginState.LOADING, PluginState.REGISTERED, PluginState.ERROR],
    PluginState.ERROR: [PluginState.REGISTERED, PluginState.DISABLED]
}


@dataclass
class PluginDescriptor:
    """
    Holds active runtime state, telemetry metrics, and descriptor details for an installed plugin.
    """
    manifest: PluginManifest
    install_path: str
    entrypoint: str = "main.py"
    state: PluginState = PluginState.REGISTERED
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    activated_at: Optional[str] = None
    error_message: Optional[str] = None
    execution_count: int = 0
    total_execution_latency_ms: float = 0.0
    last_execution_latency_ms: float = 0.0
    transition_history: List[Dict[str, Any]] = field(default_factory=list)

    def transition_to(self, new_state: PluginState, reason: Optional[str] = None) -> None:
        """
        Safely transitions the plugin lifecycle state while auditing history.

        Args:
            new_state (PluginState): Target state to transition into.
            reason (Optional[str]): Operational reason or error details for transition.

        Raises:
            StateTransitionError: If the transition path violates lifecycle rules.
        """
        allowed = VALID_TRANSITIONS.get(self.state, [])
        if new_state not in allowed:
            raise StateTransitionError(
                f"Invalid lifecycle state transition for plugin '{self.manifest.id}': "
                f"Cannot transition from {self.state.value} to {new_state.value}."
            )

        previous_state = self.state
        self.state = new_state
        timestamp = datetime.now(timezone.utc).isoformat()

        if new_state == PluginState.ACTIVE:
            self.activated_at = timestamp
            self.error_message = None
        elif new_state == PluginState.ERROR and reason:
            self.error_message = reason

        record = {
            "from_state": previous_state.value,
            "to_state": new_state.value,
            "timestamp": timestamp,
            "reason": reason or "Normal state transition"
        }
        self.transition_history.append(record)
        logger.info(
            f"[PLUGIN-STATE] '{self.manifest.id}' transitioned: "
            f"{previous_state.value} -> {new_state.value} ({reason or 'OK'})"
        )

    def record_execution(self, latency_ms: float) -> None:
        """
        Updates runtime execution statistics and latency metrics for telemetry reporting.

        Args:
            latency_ms (float): Execution duration in milliseconds.
        """
        self.execution_count += 1
        self.last_execution_latency_ms = round(latency_ms, 4)
        self.total_execution_latency_ms += latency_ms

    @property
    def average_latency_ms(self) -> float:
        """Calculates mean execution latency across all invocations."""
        if self.execution_count == 0:
            return 0.0
        return round(self.total_execution_latency_ms / self.execution_count, 4)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes descriptor details for market catalog, dashboard, and IPC telemetry.
        """
        return {
            "id": self.manifest.id,
            "vendor": self.manifest.vendor,
            "version": self.manifest.version,
            "abi": self.manifest.abi,
            "state": self.state.value,
            "install_path": self.install_path,
            "entrypoint": self.entrypoint,
            "registered_at": self.registered_at,
            "activated_at": self.activated_at,
            "error_message": self.error_message,
            "telemetry": {
                "execution_count": self.execution_count,
                "last_latency_ms": self.last_execution_latency_ms,
                "average_latency_ms": self.average_latency_ms
            },
            "manifest": self.manifest.to_dict(),
            "history_length": len(self.transition_history)
        }
