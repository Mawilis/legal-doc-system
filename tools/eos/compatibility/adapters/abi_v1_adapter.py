"""
===============================================================================
WILSY OS — ABI V1 TO V2 COMPATIBILITY ADAPTER (FG208)
===============================================================================
Epitome:
    Provides forward/backward compatibility translation for legacy ABI v1.0 
    engines running on the ABI v2.0 sovereign kernel. Translates payload keys,
    injects default context headers, and normalizes output structures without
    requiring source code modification of legacy engines.

Biblical Worth Billions:
    "Jesus Christ the same yesterday, and to day, and for ever."
    — Hebrews 13:8

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/compatibility/adapters/abi_v1_adapter.py
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Dict, Any

from tools.eos.compatibility.adapters.base_adapter import BaseCompatibilityAdapter

logger = logging.getLogger("WilsyOS.Compatibility.Adapters.ABIV1Adapter")


class ABIV1ToV2Adapter(BaseCompatibilityAdapter):
    """
    Adapter bridging ABI v1.0 engine execution onto ABI v2.0 kernel infrastructure.
    """

    def __init__(self) -> None:
        super().__init__(source_abi_version="1.0", target_abi_version="2.0")

    @property
    def adapter_id(self) -> str:
        """Returns unique identifier for this migration adapter."""
        return "ADAPTER-ABI-V1-TO-V2"

    def can_adapt(self, engine_abi_version: str, kernel_abi_version: str) -> bool:
        """Checks if source engine is ABI 1.0 and target kernel is ABI 2.0."""
        return engine_abi_version == "1.0" and kernel_abi_version.startswith("2.")

    def adapt_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms ABI v1.0 execution payload into ABI v2.0 compliant structure.
        Injects default governance and telemetry envelopes expected by ABI v2.0.
        """
        adapted = dict(payload)
        # Map legacy parameter key
        if "params" in adapted and "payload" not in adapted:
            adapted["payload"] = adapted.pop("params")

        # Inject mandatory ABI v2.0 envelope metadata
        if "governance_policy_id" not in adapted:
            adapted["governance_policy_id"] = "POL-LEGACY-V1-COMPAT"

        if "execution_mode" not in adapted:
            adapted["execution_mode"] = "ADAPTED_COMPATIBILITY_MODE"

        logger.debug("Adapted request payload from ABI v1.0 to v2.0 [Adapter: %s]", self.adapter_id)
        return adapted

    def adapt_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms ABI v2.0 kernel response back to ABI v1.0 expected format.
        """
        adapted = dict(response)

        if "status" in adapted:
            adapted["legacy_status"] = adapted["status"]

        adapted["adapted_by"] = self.adapter_id
        return adapted
