"""
===============================================================================
WILSY OS — COMPATIBILITY ADAPTER BASE INTERFACE (FG208)
===============================================================================
Epitome:
    Defines the abstract base class and interface contract for version migration 
    adapters in Wilsy OS. Enables legacy or mismatched ABI engine payloads to execute 
    seamlessly on newer kernel builds by translating execution requests, state 
    payloads, and result schemas.

Biblical Worth Billions:
    "And no man putteth new wine into old bottles; else the new wine will burst 
    the bottles, and be spilled, and the bottles shall perish. But new wine must 
    be put into new bottles; and both are preserved."
    — Luke 5:37-38

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/compatibility/adapters/base_adapter.py
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple


class BaseCompatibilityAdapter(ABC):
    """
    Abstract base class for all version migration adapters in Wilsy OS.
    
    Adapters wrap engines requiring ABI translation, allowing old ABI engines 
    (e.g., ABI v1.0) to execute on newer kernels (e.g., ABI v2.0) without 
    modifying engine source code.
    """

    def __init__(self, source_abi_version: str, target_abi_version: str) -> None:
        self.source_abi_version = source_abi_version
        self.target_abi_version = target_abi_version

    @property
    @abstractmethod
    def adapter_id(self) -> str:
        """Returns the unique identifier for this migration adapter."""
        pass

    @abstractmethod
    def can_adapt(self, engine_abi_version: str, kernel_abi_version: str) -> bool:
        """
        Determines whether this adapter can bridge the given engine ABI 
        and kernel ABI versions.
        """
        pass

    @abstractmethod
    def adapt_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translates an incoming engine execution payload from source ABI format 
        to target kernel ABI format.
        """
        pass

    @abstractmethod
    def adapt_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translates a kernel execution response back to the format expected 
        by the engine's legacy ABI contract.
        """
        pass
