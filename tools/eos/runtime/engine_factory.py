"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Factory - Institutional Component Instantiation Registry (FG162).
    Constructs and configures Wilsy OS engines with injected Event Bus and
    Lifecycle management.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional factory pattern. Clean separation of creation and use.
    Ephesians 2:10 - "For we are his workmanship, created in Christ Jesus for good works..."

Collaboration & Maintenance:
    - [Architecture]: Central factory pattern for dynamic engine creation.
    - [Compliance]: Strict dependency injection and lifecycle registration.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Type

from tools.eos.events.event_bus import EventBus
from tools.eos.runtime.lifecycle_manager import LifecycleManager, ManagedEngine

logger = logging.getLogger("WilsyOS.EngineFactory")


class EngineFactory:
    """
    Institutional factory responsible for instantiating Wilsy OS engines
    and wiring them into the Event Bus and Lifecycle Manager.
    """

    def __init__(self, event_bus: EventBus, lifecycle_manager: LifecycleManager) -> None:
        """Initializes the Engine Factory with shared kernel infrastructure."""
        self._event_bus = event_bus
        self._lifecycle_manager = lifecycle_manager
        self._engine_classes: Dict[str, Type[Any]] = {}

    # [FUNCTION EXPLANATION]: Registers an engine class template into the factory catalog.
    def register_engine_class(self, engine_name: str, engine_cls: Type[Any]) -> None:
        """Registers a concrete engine class under a canonical name."""
        self._engine_classes[engine_name] = engine_cls
        logger.info(f"Registered engine class template: [{engine_name}]")

    # [FUNCTION EXPLANATION]: Instantiates and registers an engine instance.
    def create_engine(self, engine_name: str, **kwargs: Any) -> ManagedEngine:
        """
        Instantiates a registered engine class, injecting kernel dependencies,
        and registers it with the LifecycleManager.

        Args:
            engine_name (str): Canonical name of the engine.
            **kwargs: Additional runtime configuration arguments.

        Returns:
            ManagedEngine: The fully instantiated and registered engine instance.
        """
        if engine_name not in self._engine_classes:
            raise ValueError(f"Engine class [{engine_name}] is not registered in EngineFactory.")

        engine_cls = self._engine_classes[engine_name]
        
        # Instantiate engine with event_bus injection if expected, else standard init
        try:
            engine = engine_cls(event_bus=self._event_bus, **kwargs)
        except TypeError:
            engine = engine_cls(**kwargs)

        if not hasattr(engine, "engine_id"):
            raise TypeError(f"Instantiated engine [{engine_name}] lacks required 'engine_id' attribute.")

        self._lifecycle_manager.register_engine(engine)
        logger.info(f"Engine created and registered via factory: [{engine_name}] -> ID: [{engine.engine_id}]")
        return engine
