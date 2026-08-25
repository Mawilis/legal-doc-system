"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Extension Points - Defines standardized hooks and interception interfaces for plugins.

Biblical Scale & Architecture:
    Production-ready extension point registry. Zero child's place.
    Provides structured lifecycle hooks for pre-execution, post-execution, and telemetry.

Collaboration & Maintenance:
    - [Architecture]: Hook registry and callback manager for plugin integration.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List


class ExtensionPoints:
    """
    Manages extension hooks and event callbacks across the execution pipeline.
    """

    def __init__(self) -> None:
        self._registry: Dict[str, List[Callable[..., Any]]] = {
            "pre_execution": [],
            "post_execution": [],
            "telemetry_hook": [],
        }

    def register_hook(self, hook_name: str, callback: Callable[..., Any]) -> None:
        """
        Registers a callback function to a specific extension point.

        Args:
            hook_name (str): Name of the extension hook.
            callback (Callable): Executable handler function.
        """
        if hook_name in self._registry:
            self._registry[hook_name].append(callback)

    def trigger_hook(self, hook_name: str, *args: Any, **kwargs: Any) -> List[Any]:
        """
        Executes all registered callbacks for a given hook.

        Args:
            hook_name (str): Name of the extension hook.
            *args: Positional arguments for callbacks.
            **kwargs: Keyword arguments for callbacks.

        Returns:
            List[Any]: Results returned from executed hook callbacks.
        """
        results = []
        for callback in self._registry.get(hook_name, []):
            try:
                results.append(callback(*args, **kwargs))
            except Exception as e:
                results.append({"error": str(e)})

        return results
