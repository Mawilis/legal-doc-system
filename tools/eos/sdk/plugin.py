"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Plugin Base Contract (FG166).
    Defines the abstract base class and interface for all Wilsy OS plugins.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready abstract base class. Zero child's place.
    Colossians 3:23 - "Whatever you do, work heartily, as for the Lord and not for men..."

Collaboration & Maintenance:
    - [Architecture]: Defines the rigid execution contract for external engines.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class WilsyPlugin(ABC):
    """
    Abstract base class for all Wilsy OS Engine plugins.
    Ensures institutional rigor and consistent execution interfaces across all modules.
    """

    # [FUNCTION EXPLANATION]: Initializes the plugin identity and versioning.
    def __init__(self, plugin_id: str, version: str) -> None:
        """
        Args:
            plugin_id (str): Unique identifier for the plugin.
            version (str): Semantic version string.
        """
        self.plugin_id = plugin_id
        self.version = version
        self._initialized = False

    # [FUNCTION EXPLANATION]: Prepares the plugin for execution. Must be overridden.
    @abstractmethod
    def initialize(self, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Initializes the plugin with the given context.
        
        Args:
            context (Optional[Dict[str, Any]]): Startup context parameters.
            
        Returns:
            bool: True if successfully initialized, False otherwise.
        """
        pass

    # [FUNCTION EXPLANATION]: Core engine execution logic. Must be overridden.
    @abstractmethod
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the core engine logic.
        
        Args:
            payload (Dict[str, Any]): The input data payload for the engine.
            
        Returns:
            Dict[str, Any]: The engine execution results.
        """
        pass

    # [FUNCTION EXPLANATION]: Safely terminates the plugin lifecycle. Must be overridden.
    @abstractmethod
    def shutdown(self) -> bool:
        """
        Safely terminates the plugin and releases resources.
        
        Returns:
            bool: True if shut down successfully, False otherwise.
        """
        pass
