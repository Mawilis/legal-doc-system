"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Lifecycle Manager - Institutional Engine State & Transition Controller (FG162).
    Manages the complete lifecycle (initialization, startup, execution, shutdown,
    and health monitoring) of all Wilsy OS kernel engines.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional governance. Orderly transitions and state control.
    Ecclesiastes 3:1 - "For everything there is a season, and a time for every matter under heaven."

Collaboration & Maintenance:
    - [Architecture]: Centralized engine lifecycle orchestrator replacing direct instantiation.
    - [Compliance]: Thread-safe state tracking, fault isolation, and audit readiness.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import threading
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

logger = logging.getLogger("WilsyOS.LifecycleManager")


class EngineState(str, Enum):
    """Canonical lifecycle states for Wilsy OS engines."""
    UNINITIALIZED = "eos.engine.state.uninitialized"
    INITIALIZING = "eos.engine.state.initializing"
    READY = "eos.engine.state.ready"
    RUNNING = "eos.engine.state.running"
    STOPPED = "eos.engine.state.stopped"
    FAILED = "eos.engine.state.failed"


@runtime_checkable
class ManagedEngine(Protocol):
    """Protocol defining the standard interface for engines managed by the lifecycle system."""

    @property
    def engine_id(self) -> str:
        """Unique identifier for the engine."""
        ...

    def initialize(self) -> None:
        """Initializes engine resources and dependencies."""
        ...

    def start(self) -> None:
        """Starts engine execution or event listening."""
        ...

    def stop(self) -> None:
        """Gracefully stops the engine and releases resources."""
        ...

    def health_check(self) -> bool:
        """Returns True if the engine is operating correctly."""
        ...


class LifecycleManager:
    """
    Central institutional manager controlling engine registration, state transitions,
    startup sequences, and health monitoring across Wilsy OS.
    """

    def __init__(self) -> None:
        """Initializes the Lifecycle Manager with thread-safe registries and state tracking."""
        self._engines: Dict[str, ManagedEngine] = {}
        self._states: Dict[str, EngineState] = {}
        self._lock = threading.Lock()

    # [FUNCTION EXPLANATION]: Registers a managed engine into the lifecycle control registry.
    def register_engine(self, engine: ManagedEngine) -> None:
        """
        Registers an engine instance with the lifecycle manager.

        Args:
            engine (ManagedEngine): The engine conforming to the ManagedEngine protocol.
        """
        with self._lock:
            eid = engine.engine_id
            self._engines[eid] = engine
            self._states[eid] = EngineState.UNINITIALIZED
        logger.info(f"Engine registered in LifecycleManager: [{eid}]")

    # [FUNCTION EXPLANATION]: Retrieves the current lifecycle state of a registered engine.
    def get_engine_state(self, engine_id: str) -> Optional[EngineState]:
        """Returns the current state for a given engine ID."""
        with self._lock:
            return self._states.get(engine_id)

    # [FUNCTION EXPLANATION]: Initializes a specific registered engine.
    def initialize_engine(self, engine_id: str) -> None:
        """Transitions an engine from UNINITIALIZED to READY."""
        with self._lock:
            engine = self._engines.get(engine_id)
            if not engine:
                raise ValueError(f"Engine [{engine_id}] not registered.")
            self._states[engine_id] = EngineState.INITIALIZING

        try:
            engine.initialize()
            with self._lock:
                self._states[engine_id] = EngineState.READY
            logger.info(f"Engine initialized successfully: [{engine_id}]")
        except Exception as e:
            with self._lock:
                self._states[engine_id] = EngineState.FAILED
            logger.error(f"Engine initialization failed for [{engine_id}]: {e}")
            raise

    # [FUNCTION EXPLANATION]: Starts a specific ready engine.
    def start_engine(self, engine_id: str) -> None:
        """Transitions an engine from READY to RUNNING."""
        with self._lock:
            engine = self._engines.get(engine_id)
            if not engine:
                raise ValueError(f"Engine [{engine_id}] not registered.")
            state = self._states.get(engine_id)
            if state != EngineState.READY:
                raise RuntimeError(f"Engine [{engine_id}] cannot start from state [{state}]. Must be READY.")

        try:
            engine.start()
            with self._lock:
                self._states[engine_id] = EngineState.RUNNING
            logger.info(f"Engine started successfully: [{engine_id}]")
        except Exception as e:
            with self._lock:
                self._states[engine_id] = EngineState.FAILED
            logger.error(f"Engine start failed for [{engine_id}]: {e}")
            raise

    # [FUNCTION EXPLANATION]: Gracefully stops a running engine.
    def stop_engine(self, engine_id: str) -> None:
        """Transitions an engine to STOPPED state."""
        with self._lock:
            engine = self._engines.get(engine_id)
            if not engine:
                raise ValueError(f"Engine [{engine_id}] not registered.")

        try:
            engine.stop()
            with self._lock:
                self._states[engine_id] = EngineState.STOPPED
            logger.info(f"Engine stopped gracefully: [{engine_id}]")
        except Exception as e:
            with self._lock:
                self._states[engine_id] = EngineState.FAILED
            logger.error(f"Engine stop error for [{engine_id}]: {e}")
            raise

    # [FUNCTION EXPLANATION]: Executes health checks across all registered engines.
    def health_check_all(self) -> Dict[str, bool]:
        """
        Performs health checks on all active engines.

        Returns:
            Dict[str, bool]: Mapping of engine IDs to health status flags.
        """
        results: Dict[str, bool] = {}
        with self._lock:
            items = list(self._engines.items())

        for eid, engine in items:
            try:
                results[eid] = engine.health_check()
            except Exception as e:
                logger.error(f"Health check exception for engine [{eid}]: {e}")
                results[eid] = False
        return results
