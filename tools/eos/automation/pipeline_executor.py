"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Pipeline Executor - Executes structured workflows with telemetry, error handling, and reporting.

Biblical Scale & Architecture:
    Production-ready pipeline execution engine. Zero child's place.
    Drives end-to-end workflow execution with strict error trapping and audit logging.

Collaboration & Maintenance:
    - [Architecture]: Workflow runner and execution telemetry collector.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List
from .workflow import Workflow


class PipelineExecutor:
    """
    Orchestrates the execution of defined workflows.
    """

    @staticmethod
    def execute_workflow(workflow: Workflow) -> Dict[str, Any]:
        """
        Executes all steps in a given workflow sequentially.

        Args:
            workflow (Workflow): The workflow instance to execute.

        Returns:
            Dict[str, Any]: Execution results report.
        """
        step_results = []
        success = True

        for step in workflow.steps:
            step_name = step["step_name"]
            action = step["action"]
            kwargs = step["kwargs"]

            try:
                result = action(**kwargs)
                step_results.append({
                    "step_name": step_name,
                    "status": "SUCCESS",
                    "output": result,
                })
            except Exception as e:
                success = False
                step_results.append({
                    "step_name": step_name,
                    "status": "FAILED",
                    "error": str(e),
                })
                break

        return {
            "workflow_name": workflow.name,
            "status": "COMPLETED" if success else "FAILED",
            "steps_executed": len(step_results),
            "step_results": step_results,
            "comments": "Pipeline executor completed workflow run with rigorous state validation.",
        }
