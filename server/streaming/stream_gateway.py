"""
╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS - STREAMING GATEWAY CORE [V1.0.0-PRODUCTION-GRADE]                                                                          ║
║ [EPITOME: TRANSPORT LAYER ORCHESTRATOR CONNECTING KERNEL BUSES TO CLIENT STREAMS]                                                    ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ VERSION: 1.0.0-PRODUCTION-GRADE | BILLION-DOLLAR ENTERPRISE SOFTWARE | FROZEN ABI COMPLIANT                                           ║
║ ABSOLUTE PATH: server/streaming/stream_gateway.py                                                                                    ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
║ • Wilson Khanyezi (Founder/CEO) - Strict rule: Gateway must ONLY stream, NEVER alter kernel state or compute metrics.               ║
║ • AI Engineering (Codex) - IMPLEMENTED: Core gateway coordinating event intake, serialization, and registry broadcast.               ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import time
import logging
from .stream_registry import StreamRegistry
from .stream_serializer import serialize_delta
from .stream_channels import StreamChannels
from .stream_events import StreamEventRouter

logger = logging.getLogger("WilsyKernel.StreamingGateway")

class StreamingGateway:
    """Core transport gateway for Wilsy OS real-time stream delivery."""
    
    def __init__(self):
        self.registry = StreamRegistry()
        self.router = StreamEventRouter()
        self._setup_internal_routing()

    def _setup_internal_routing(self):
        """Subscribes gateway broadcast method to all valid channels in event router."""
        for ch in StreamChannels.all_channels():
            self.router.subscribe(ch, self.publish_update)

    def publish_update(self, channel: str, payload: dict) -> str:
        """
        Receives state delta, serializes it, and broadcasts to subscribed clients.
        
        :param channel: Channel endpoint string.
        :param payload: Update dictionary slice.
        :return: Serialized JSON payload string.
        """
        if not StreamChannels.validate_channel(channel):
            logger.warning(f"[GATEWAY-WARN] Attempted publish to invalid channel '{channel}'")

        serialized = serialize_delta(channel, payload)
        self.registry.broadcast(channel, serialized)
        return serialized
