"""
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS - STREAM REGISTRY [V1.0.0-PRODUCTION-GRADE]                                                                                 ║
║ [EPITOME: CONCURRENT CLIENT CONNECTION AND BROADCAST MANAGER]                                                                        ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ VERSION: 1.0.0-PRODUCTION-GRADE | BILLION-DOLLAR ENTERPRISE SOFTWARE | FROZEN ABI COMPLIANT                                           ║
║ ABSOLUTE PATH: server/streaming/stream_registry.py                                                                                   ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
║ • Wilson Khanyezi (Founder/CEO) - Ensured high-concurrency client handling for executive monitoring terminals.                       ║
║ • AI Engineering (Codex) - IMPLEMENTED: Lock-protected registry managing registration, cleanup, and channel broadcasts.             ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import threading
import logging
from .stream_client import StreamClient

logger = logging.getLogger("WilsyKernel.StreamRegistry")

class StreamRegistry:
    """Thread-safe registry managing active streaming client connections."""
    
    def __init__(self):
        self._clients = {}
        self._lock = threading.Lock()

    def register(self, client: StreamClient):
        """Registers a new active client connection."""
        with self._lock:
            self._clients[client.client_id] = client
            logger.info(f"[REGISTRY] Registered client '{client.client_id}' for channels: {client.subscribed_channels}")

    def unregister(self, client_id: str):
        """Unregisters and disconnects a client."""
        with self._lock:
            if client_id in self._clients:
                self._clients[client_id].disconnect()
                del self._clients[client_id]
                logger.info(f"[REGISTRY] Unregistered client '{client_id}'")

    def broadcast(self, channel: str, serialized_payload: str):
        """Broadcasts a serialized payload to all subscribed clients."""
        with self._lock:
            active_clients = list(self._clients.values())

        for client in active_clients:
            if client.is_subscribed_to(channel):
                client.push_message(serialized_payload)

    def get_client_count(self) -> int:
        """Returns count of active clients."""
        with self._lock:
            return len(self._clients)
