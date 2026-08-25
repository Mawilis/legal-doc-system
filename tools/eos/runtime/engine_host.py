"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Host - Master Runtime Orchestrator (FG162).
    Coordinates bootstrap, sequenced startup, active health supervision,
    and graceful teardown of all institutional engines across Wilsy OS.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional orchestration. Unified coordination and resilience.
    Colossians 1:17 - "And he is before all things, and in him all things hold together."

Collaboration & Maintenance:
    - [Architecture]: Master runtime supervisor orchestrating Lifecycle Manager and Event Bus.
    - [Compliance]: Complete sequence management, fault detection, and graceful shutdown.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import time
from typing import Any, List, Optional

from tools.eos.events.event_bus import EventBus
from tools.eos.events.event_types import EventType
from tools.eos.runtime.engine_factory import EngineFactory
from tools.eos.runtime.lifecycle_manager import LifecycleManager, EngineState

logger = logging.getLogger("WilsyOS.EngineHost")


class EngineHost:
    """
    Master institutional runtime host managing the bootstrap, startup,
    monitoring, and shutdown sequence for all Wilsy OS engines.
    """

    def __init__(self) -> None:
        """Initializes the master kernel infrastructure (EventBus, LifecycleManager, EngineFactory)."""
        self.event_bus = EventBus(publisher_id="WilsyOS-Kernel-Host")
        self.lifecycle_manager = LifecycleManager()
        self.factory = EngineFactory(event_bus=self.event_bus, lifecycle_manager=self.lifecycle_manager)
        self._registered_engine_ids: List[str] = []

    # [FUNCTION EXPLANATION]: Registers and tracks an engine through the host.
    def register(self, engine_name: str, **kwargs: Any) -> Any:
        """
        Instantiates and registers an engine via the factory.

        Args:
            engine_name (str): Canonical engine class name.
            **kwargs: Engine configuration arguments.

        Returns:
            Any: The created engine instance.
        """
        engine = self.factory.create_engine(engine_name, **kwargs)
        self._registered_engine_ids.append(engine.engine_id)
        return engine

    # [FUNCTION EXPLANATION]: Bootstraps all registered engines (Initialize -> Start).
    def bootstrap(self) -> None:
        """
        Sequentially initializes and starts all registered engines,
        publishing system startup telemetry via the Event Bus.
        """
        logger.info("Starting Wilsy OS EngineHost bootstrap sequence...")

        # 1. Initialize phase
        for eid in self._registered_engine_ids:
            logger.info(f"Initializing engine: [{eid}]")
            self.lifecycle_manager.initialize_engine(eid)

        # 2. Start phase
        for eid in self._registered_engine_ids:
            logger.info(f"Starting engine: [{eid}]")
            self.lifecycle_manager.start_engine(eid)

        # Publish system alert / startup complete event
        self.event_bus.publish(
            event_type=EventType.EXECUTION_STARTED,
            payload={"status": "EngineHost bootstrap complete", "engines": self._registered_engine_ids},
            execution_id="exec-host-bootstrap"
        )
        logger.info("Wilsy OS EngineHost bootstrap sequence successfully completed.")

    # [FUNCTION EXPLANATION]: Performs runtime health supervision across all engines.
    def supervise(self) -> bool:
        """
        Runs health checks across all managed engines.

        Returns:
            bool: True if all engines are healthy, False otherwise.
        """
        health_status = self.lifecycle_manager.health_check_all()
        all_healthy = True
        for eid, healthy in health_status.items():
            if not healthy:
                all_healthy = False
                logger.error(f"Health check FAILED for engine: [{eid}]")
                self.event_bus.publish(
                    event_type=EventType.SYSTEM_ALERT,
                    payload={"alert": f"Engine [{eid}] health check failed"},
                    execution_id="exec-host-supervision"
                )
        return all_healthy

    # [FUNCTION EXPLANATION]: Gracefully shuts down all managed engines.
    def shutdown(self) -> None:
        """Gracefully stops all running engines in reverse order of startup."""
        logger.info("Initiating Wilsy OS EngineHost graceful shutdown...")
        for eid in reversed(self._registered_engine_ids):
            try:
                state = self.lifecycle_manager.get_engine_state(eid)
                if state == EngineState.RUNNING:
                    logger.info(f"Stopping engine: [{eid}]")
                    self.lifecycle_manager.stop_engine(eid)
            except Exception as e:
                logger.error(f"Error stopping engine [{eid}]: {e}")

        self.event_bus.publish(
            event_type=EventType.EXECUTION_COMPLETED,
            payload={"status": "EngineHost shutdown complete"},
            execution_id="exec-host-shutdown"
        )
        logger.info("Wilsy OS EngineHost shutdown complete.")
