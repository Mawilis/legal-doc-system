"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Institutional Event Bus - Publisher Contract (FG161).
    Defines the standard publishing interface for engines emitting events across Wilsy OS.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional publisher contract. Zero child's place.
    Psalm 68:11 - "The Lord gives the word; the women who announce the news are a great host."

Collaboration & Maintenance:
    - [Architecture]: Standardized event emitter interface decoupling producers from consumers.
    - [Compliance]: Strict contract enforcement for event generation and dispatch initiation.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from tools.eos.events.event import Event
    from tools.eos.events.event_types import EventType


class Publisher(ABC):
    """
    Abstract base class representing an institutional event publisher.
    Engines that initiate actions or workflows implement this contract to emit events.
    """

    @property
    @abstractmethod
    def publisher_id(self) -> str:
        """Unique identifier for the publisher instance."""
        pass

    @abstractmethod
    def publish(
        self,
        event_type: EventType | str,
        payload: Dict[str, Any],
        execution_id: Optional[str] = None,
    ) -> Event:
        """
        Publishes an event to the institutional Event Bus.

        Args:
            event_type (EventType | str): The classification of the event.
            payload (Dict[str, Any]): Data payload accompanying the event.
            execution_id (Optional[str]): Active execution session tracking ID.

        Returns:
            Event: The fully sealed, published Event instance.
        """
        pass
