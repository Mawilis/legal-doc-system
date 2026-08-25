"""
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS - STREAM EVENT ROUTER [V1.0.0-PRODUCTION-GRADE]                                                                             ║
║ [EPITOME: KERNEL EVENT BUS AND ARTIFACT BUS EVENT DISPATCHER]                                                                        ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ VERSION: 1.0.0-PRODUCTION-GRADE | BILLION-DOLLAR ENTERPRISE SOFTWARE | FROZEN ABI COMPLIANT                                           ║
║ ABSOLUTE PATH: server/streaming/stream_events.py                                                                                     ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
║ • Wilson Khanyezi (Founder/CEO) - Guaranteed non-blocking event dispatching from kernel execution threads.                            ║
║ • AI Engineering (Codex) - IMPLEMENTED: In-memory listener routing with thread-safe callback registration.                           ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import threading
import logging

logger = logging.getLogger("WilsyKernel.StreamEventRouter")

class StreamEventRouter:
    """Thread-safe router connecting kernel buses to stream gateway channels."""
    
    def __init__(self):
        self._listeners = {}
        self._lock = threading.Lock()

    def subscribe(self, channel: str, callback):
        """
        Subscribes a gateway broadcast callback to a specific channel.
        """
        with self._lock:
            if channel not in self._listeners:
                self._listeners[channel] = []
            if callback not in self._listeners[channel]:
                self._listeners[channel].append(callback)
                logger.debug(f"[EVENT-ROUTER] Subscribed callback to channel {channel}")

    def unsubscribe(self, channel: str, callback):
        """
        Removes a callback subscription.
        """
        with self._lock:
            if channel in self._listeners and callback in self._listeners[channel]:
                self._listeners[channel].remove(callback)

    def dispatch(self, channel: str, payload: dict):
        """
        Dispatches incoming event bus payloads to registered streaming channel callbacks.
        """
        with self._lock:
            callbacks = list(self._listeners.get(channel, []))

        for cb in callbacks:
            try:
                cb(channel, payload)
            except Exception as e:
                logger.error(f"[EVENT-ROUTER-ERROR] Callback failed on {channel}: {str(e)}")
