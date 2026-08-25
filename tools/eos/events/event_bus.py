"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Institutional Event Bus - Central Dispatcher & Publish-Subscribe Broker (FG161).
    Coordinates event publishing, subscriber registration, thread-safe dispatch,
    and failure isolation across all Wilsy OS engines and modules.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional event broker. High-performance, decoupled, and robust.
    Romans 12:5 - "So we, though many, are one body in Christ, and individually members one of another."

Collaboration & Maintenance:
    - [Architecture]: Central event broker implementing Publisher and Subscriber contracts.
    - [Compliance]: Thread-safe event distribution, failure isolation, and audit history tracking.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from tools.eos.events.event import Event
from tools.eos.events.event_types import EventType
from tools.eos.events.publisher import Publisher
from tools.eos.events.subscriber import Subscriber

logger = logging.getLogger("WilsyOS.EventBus")


class EventBus(Publisher):
    """
    Central institutional event bus facilitating decoupled publish-subscribe
    messaging across Wilsy OS kernel engines.
    """

    def __init__(self, publisher_id: str = "WilsyOS-Kernel-EventBus") -> None:
        """Initializes the Event Bus with thread-safe locks, subscriber registries, and event history."""
        self._publisher_id = publisher_id
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}
        self._subscriber_objects: Set[Subscriber] = set()
        self._event_history: List[Event] = []
        self._lock = threading.Lock()

    @property
    def publisher_id(self) -> str:
        """Returns the unique identifier for this event bus publisher instance."""
        return self._publisher_id

    # [FUNCTION EXPLANATION]: Registers an institutional subscriber contract instance.
    def register_subscriber(self, subscriber: Subscriber, event_types: List[EventType | str]) -> None:
        """
        Registers an engine implementing the Subscriber contract for specified event types.

        Args:
            subscriber (Subscriber): The engine subscriber instance.
            event_types (List[EventType | str]): List of event types to subscribe to.
        """
        with self._lock:
            self._subscriber_objects.add(subscriber)
            for et in event_types:
                type_val = et.value if isinstance(et, EventType) else et
                subscriber.subscribe(type_val)
                if type_val not in self._subscribers:
                    self._subscribers[type_val] = []
                if subscriber.notify not in self._subscribers[type_val]:
                    self._subscribers[type_val].append(subscriber.notify)
        logger.info(f"Registered subscriber [{subscriber.subscriber_id}] for event types: {event_types}")

    # [FUNCTION EXPLANATION]: Unregisters an institutional subscriber contract instance.
    def unregister_subscriber(self, subscriber: Subscriber) -> None:
        """Removes a subscriber contract instance across all event types."""
        with self._lock:
            if subscriber in self._subscriber_objects:
                self._subscriber_objects.remove(subscriber)
            for type_val, handlers in self._subscribers.items():
                self._subscribers[type_val] = [h for h in handlers if h != subscriber.notify]
        logger.info(f"Unregistered subscriber [{subscriber.subscriber_id}]")

    # [FUNCTION EXPLANATION]: Subscribes a raw handler callback to an event type.
    def subscribe_handler(self, event_type: EventType | str, handler: Callable[[Event], None]) -> None:
        """
        Registers a direct callable handler for a specific event type.

        Args:
            event_type (EventType | str): Event classification.
            handler (Callable[[Event], None]): Callback function.
        """
        type_val = event_type.value if isinstance(event_type, EventType) else event_type
        with self._lock:
            if type_val not in self._subscribers:
                self._subscribers[type_val] = []
            if handler not in self._subscribers[type_val]:
                self._subscribers[type_val].append(handler)

    # [FUNCTION EXPLANATION]: Unsubscribes a raw handler callback from an event type.
    def unsubscribe_handler(self, event_type: EventType | str, handler: Callable[[Event], None]) -> None:
        """Removes a registered direct handler callback."""
        type_val = event_type.value if isinstance(event_type, EventType) else event_type
        with self._lock:
            if type_val in self._subscribers and handler in self._subscribers[type_val]:
                self._subscribers[type_val].remove(handler)

    # [FUNCTION EXPLANATION]: Publishes an event conforming to the Publisher contract.
    def publish(
        self,
        event_type: EventType | str,
        payload: Dict[str, Any],
        execution_id: Optional[str] = None,
    ) -> Event:
        """
        Constructs and publishes an immutable Event instance across the Event Bus.

        Args:
            event_type (EventType | str): Classification of the event.
            payload (Dict[str, Any]): Immutable data payload.
            execution_id (Optional[str]): Execution session identifier.

        Returns:
            Event: The fully sealed, dispatched Event instance.
        """
        event = Event.create(
            event_type=event_type,
            producer=self._publisher_id,
            payload=payload,
            execution_id=execution_id,
        )

        if not event.verify_integrity():
            raise ValueError(f"Event cryptographic integrity check failed for event_id: {event.event_id}")

        with self._lock:
            self._event_history.append(event)

        type_val = event.event_type.value if isinstance(event.event_type, EventType) else event.event_type

        # Gather deterministic handlers for specific type and wildcard '*'
        handlers: List[Callable[[Event], None]] = []
        with self._lock:
            if type_val in self._subscribers:
                handlers.extend(self._subscribers[type_val])
            if "*" in self._subscribers:
                for h in self._subscribers["*"]:
                    if h not in handlers:
                        handlers.append(h)

        # Dispatch with complete failure isolation per subscriber
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    f"Subscriber exception isolated during dispatch of event [{event.event_id}] "
                    f"({type_val}) to handler [{handler}]: {e}"
                )

        logger.debug(f"Published and dispatched event [{event.event_id}] of type [{type_val}]")
        return event

    # [FUNCTION EXPLANATION]: Retrieves recorded event dispatch history.
    def history(self, event_type: Optional[EventType | str] = None) -> Tuple[Event, ...]:
        """
        Retrieves recorded event history, optionally filtered by event type.

        Args:
            event_type (Optional[EventType | str]): Optional event type filter.

        Returns:
            Tuple[Event, ...]: Tuple of matching dispatched Event instances.
        """
        with self._lock:
            if not event_type:
                return tuple(self._event_history)
            type_val = event_type.value if isinstance(event_type, EventType) else event_type
            filtered = [e for e in self._event_history if e.event_type == type_val]
            return tuple(filtered)

    def clear(self) -> None:
        """Clears all subscribers, objects, and event history."""
        with self._lock:
            self._subscribers.clear()
            self._subscriber_objects.clear()
            self._event_history.clear()
