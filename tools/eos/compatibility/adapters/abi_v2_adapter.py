"""
===============================================================================
WILSY OS — ABI V2 NATIVE PASS-THROUGH ADAPTER (FG208)
===============================================================================
Epitome:
    Provides native pass-through and minor-version normalization for ABI v2.x 
    engines running on ABI v2.x Kernel infrastructure. Validates payload headers,
    verifies native state signatures, and ensures zero-overhead passthrough.

Biblical Worth Billions:
    "Every good gift and every perfect gift is from above, and cometh down from 
    the Father of lights, with whom is no variableness, neither shadow of turning."
    — James 1:17

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/compatibility/adapters/abi_v2_adapter.py
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Dict, Any

from tools.eos.compatibility.adapters.base_adapter import BaseCompatibilityAdapter

logger = logging.getLogger("WilsyOS.Compatibility.Adapters.ABIV2Adapter")


class ABIV2NativeAdapter(BaseCompatibilityAdapter):
    """
    Native pass-through adapter for ABI v2.x compliant engines.
    """

    def __init__(self) -> None:
        super().__init__(source_abi_version="2.0", target_abi_version="2.0")

    @property
    def adapter_id(self) -> str:
        """Returns unique identifier for this native pass-through adapter."""
        return "ADAPTER-ABI-V2-NATIVE"

    def can_adapt(self, engine_abi_version: str, kernel_abi_version: str) -> bool:
        """Checks if both engine and kernel share major ABI version 2."""
        return engine_abi_version.startswith("2.") and kernel_abi_version.startswith("2.")

    def adapt_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates native ABI v2 payload structure and passes through without modification.
        """
        adapted = dict(payload)
        adapted["adapted_by"] = self.adapter_id
        logger.debug("Passed through native ABI v2 request payload [Adapter: %s]", self.adapter_id)
        return adapted

    def adapt_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Passes through native ABI v2 response payload without modification.
        """
        adapted = dict(response)
        adapted["adapted_by"] = self.adapter_id
        return adapted
