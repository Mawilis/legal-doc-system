"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Workflow - Defines multi-step sequential and parallel institutional task workflows.

Biblical Scale & Architecture:
    Production-ready workflow definition engine. Zero child's place.
    Encapsulates sequential execution steps, dependency mapping, and parameter propagation.

Collaboration & Maintenance:
    - [Architecture]: Workflow graph builder and step sequencer.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List


class Workflow:
    """
    Defines and structures an institutional execution workflow.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.steps: List[Dict[str, Any]] = []

    def add_step(self, step_name: str, action: Callable[..., Any], **kwargs: Any) -> Workflow:
        """
        Adds an execution step to the workflow.

        Args:
            step_name (str): Name of the step.
            action (Callable): Executable action handler.
            **kwargs: Default arguments for the action.

        Returns:
            Workflow: Self instance for fluent method chaining.
        """
        self.steps.append({
            "step_name": step_name,
            "action": action,
            "kwargs": kwargs,
        })
        return self
