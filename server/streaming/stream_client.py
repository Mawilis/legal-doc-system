"""
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS - STREAM CLIENT REPRESENTATION [V1.0.0-PRODUCTION-GRADE]                                                                     ║
║ [EPITOME: THREAD-SAFE CONCURRENT SUBSCRIBER CONNECTION MODEL WITH QUEUE ISOLATION]                                                   ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ VERSION: 1.0.0-PRODUCTION-GRADE | BILLION-DOLLAR ENTERPRISE SOFTWARE | FROZEN ABI COMPLIANT                                           ║
║ ABSOLUTE PATH: server/streaming/stream_client.py                                                                                     ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
║ • Wilson Khanyezi (Founder/CEO) - Demanded isolated client message queues to prevent slow-reader lockups.                             ║
║ • AI Engineering (Codex) - IMPLEMENTED: Queue-backed client model with thread-safe message flushing.                                 ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import queue
import time

class StreamClient:
    """Represents an active client streaming connection."""
    
    def __init__(self, client_id: str, subscribed_channels: list, max_queue_size: int = 1000):
        self.client_id = client_id
        self.subscribed_channels = list(subscribed_channels)
        self.connected_at = time.time()
        self.queue = queue.Queue(maxsize=max_queue_size)
        self.is_active = True

    def is_subscribed_to(self, channel: str) -> bool:
        """Checks if client is listening to a given channel or global dashboard."""
        return channel in self.subscribed_channels or "/stream/dashboard" in self.subscribed_channels

    def push_message(self, message: str):
        """Pushes a serialized delta payload to the client's output queue."""
        if not self.is_active:
            return
        try:
            self.queue.put_nowait(message)
        except queue.Full:
            # Drop oldest to maintain real-time pressure
            try:
                self.queue.get_nowait()
                self.queue.put_nowait(message)
            except Exception:
                pass

    def get_pending_messages(self) -> list:
        """Flushes and returns all accumulated pending messages."""
        messages = []
        while not self.queue.empty():
            try:
                messages.append(self.queue.get_nowait())
            except queue.Empty:
                break
        return messages

    def disconnect(self):
        """Marks client connection as closed."""
        self.is_active = False
