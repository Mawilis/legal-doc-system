"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Institutional Event Bus - Subscriber Contract (FG161).
    Defines the standard subscriber interface for asynchronous or synchronous
    event consumption across all Wilsy OS engines.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional subscriber contract. Zero child's place.
    Proverbs 18:15 - "An intelligent heart acquires knowledge, and the ear of the wise seeks knowledge."

Collaboration & Maintenance:
    - [Architecture]: Standardized event listener interface ensuring plug-and-play engine integration.
    - [Compliance]: Strict contract enforcement for event dispatch handling.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tools.eos.events.event import Event


class Subscriber(ABC):
    """
    Abstract base class representing an institutional event subscriber.
    All engines wishing to receive published events from the Event Bus must implement this contract.
    """

    @property
    @abstractmethod
    def subscriber_id(self) -> str:
        """Unique identifier for the subscriber instance."""
        pass

    @abstractmethod
    def subscribe(self, event_type: str) -> None:
        """Registers interest in a specific event type."""
        pass

    @abstractmethod
    def unsubscribe(self, event_type: str) -> None:
        """Removes interest in a specific event type."""
        pass

    @abstractmethod
    def notify(self, event: Event) -> None:
        """
        Receives and handles a dispatched event.
        Must isolate failures to prevent subscriber exceptions from crashing the Event Bus.
        """
        pass
