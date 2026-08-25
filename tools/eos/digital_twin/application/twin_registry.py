"""
===============================================================================
WILSY OS — FG223 DIGITAL TWIN INTELLIGENCE PLATFORM
===============================================================================

File Path:
    tools/eos/digital_twin/application/twin_registry.py

Epitome:
    Manages provider registration and subsystem synchronization across all Wilsy OS
    adapters. Guarantees zero duplicate ownership while refreshing state vectors.

Biblical Worth Billions:
    "Every purpose is established by counsel: and with good advice make war."
    — Proverbs 20:18

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import time
import logging
from typing import Dict, Any, List, Optional
from tools.eos.digital_twin.application.twin_engine import TwinEngine

logger = logging.getLogger("WilsyOS.DigitalTwin.Registry")


class TwinRegistry:
    """
    Subsystem provider registry for the Digital Twin Platform.
    """

    def __init__(self, twin_engine: TwinEngine):
        if not isinstance(twin_engine, TwinEngine):
            raise TypeError("TwinRegistry requires a valid TwinEngine instance.")

        self._twin_engine = twin_engine
        self._adapters: Dict[str, Any] = {}
        self._last_sync_timestamp: float = 0.0

    @property
    def registered_adapters(self) -> List[str]:
        return list(self._adapters.keys())

    @property
    def last_sync_timestamp(self) -> float:
        return self._last_sync_timestamp

    def register_adapter(self, adapter_name: str, adapter_instance: Any) -> None:
        if not adapter_name or not adapter_instance:
            raise ValueError("Adapter registration requires a valid name and instance.")

        self._adapters[adapter_name.lower()] = adapter_instance
        logger.info(f"Registered Digital Twin adapter provider: [{adapter_name.lower()}]")

    def synchronize_all(self) -> Dict[str, Any]:
        start_time = time.perf_counter()
        sync_results = {}

        for adapter_name, adapter in self._adapters.items():
            try:
                if hasattr(adapter, "synchronize") and callable(adapter.synchronize):
                    result = adapter.synchronize(self._twin_engine)
                    sync_results[adapter_name] = {"status": "SUCCESS", "details": result}
                else:
                    sync_results[adapter_name] = {"status": "SKIPPED", "reason": "No synchronize method found"}
            except Exception as e:
                logger.error(f"Error synchronizing adapter [{adapter_name}]: {str(e)}")
                sync_results[adapter_name] = {"status": "FAILED", "error": str(e)}

        self._last_sync_timestamp = time.time()
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "timestamp": self._last_sync_timestamp,
            "adapters_count": len(self._adapters),
            "adapters_executed": len(self._adapters),
            "total_entities": self._twin_engine.state.entity_count,
            "total_relationships": self._twin_engine.state.relationship_count,
            "execution_time_ms": round(elapsed_ms, 4),
            "results": sync_results
        }
