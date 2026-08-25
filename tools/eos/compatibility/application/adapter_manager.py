"""
===============================================================================
WILSY OS — COMPATIBILITY ADAPTER MANAGER (FG208)
===============================================================================
Epitome:
    Provides registry management, lookup, and resolution for version migration 
    adapters in Wilsy OS. Enables the Compatibility Engine to resolve, wrap, and 
    execute legacy or forward-spec engine payloads dynamically across kernel 
    ABI boundaries.

Biblical Worth Billions:
    "Ask, and it shall be given you; seek, and ye shall find; knock, and it shall 
    be opened unto you."
    — Matthew 7:7

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/compatibility/application/adapter_manager.py
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Any

from tools.eos.compatibility.adapters.base_adapter import BaseCompatibilityAdapter
from tools.eos.compatibility.adapters.abi_v1_adapter import ABIV1ToV2Adapter
from tools.eos.compatibility.adapters.abi_v2_adapter import ABIV2NativeAdapter

logger = logging.getLogger("WilsyOS.Compatibility.AdapterManager")


class AdapterManager:
    """
    Application service managing compatibility adapter discovery and selection.
    """

    def __init__(self) -> None:
        self._adapters: List[BaseCompatibilityAdapter] = []
        self._bootstrap_default_adapters()

    def _bootstrap_default_adapters(self) -> None:
        """Registers default platform migration adapters."""
        self.register_adapter(ABIV1ToV2Adapter())
        self.register_adapter(ABIV2NativeAdapter())

    def register_adapter(self, adapter: BaseCompatibilityAdapter) -> None:
        """Registers a compatibility adapter into the manager registry."""
        self._adapters.append(adapter)
        logger.debug("Registered compatibility adapter: %s", adapter.adapter_id)

    def resolve_adapter(
        self,
        engine_abi_version: str,
        kernel_abi_version: str
    ) -> Optional[BaseCompatibilityAdapter]:
        """
        Resolves the appropriate migration adapter capable of bridging 
        engine_abi_version to kernel_abi_version.
        
        Returns:
            Matching BaseCompatibilityAdapter instance or None if no adapter exists.
        """
        for adapter in self._adapters:
            if adapter.can_adapt(engine_abi_version, kernel_abi_version):
                logger.info(
                    "Resolved adapter [%s] for engine ABI '%s' -> Kernel ABI '%s'",
                    adapter.adapter_id,
                    engine_abi_version,
                    kernel_abi_version
                )
                return adapter

        logger.warning(
            "No compatible adapter found for engine ABI '%s' -> Kernel ABI '%s'",
            engine_abi_version,
            kernel_abi_version
        )
        return None

    def get_registered_adapters(self) -> List[str]:
        """Returns list of registered adapter IDs."""
        return [adapter.adapter_id for adapter in self._adapters]
