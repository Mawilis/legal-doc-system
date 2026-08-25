"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Patch Engine - Orchestrates atomic code patching, planning, validation, and execution.

Biblical Scale & Architecture:
    Production-ready patch orchestration pipeline. Zero child's place.
    Guarantees safe, transactional updates to production codebases with rollback capabilities.

Collaboration & Maintenance:
    - [Architecture]: Master coordinator for automated repository patching operations.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List
from pathlib import Path

from .patch_plan import PatchPlan
from .patch_validator import PatchValidator
from .patch_executor import PatchExecutor


class PatchEngine:
    """
    Orchestrates the full lifecycle of repository patching from planning to transactional execution.
    """

    def __init__(self, workspace_root: Path | str = ".") -> None:
        self.workspace_root = Path(workspace_root).resolve()

    def execute_patch_pipeline(self, patch_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the end-to-end patch pipeline for a given specification.

        Args:
            patch_spec (Dict[str, Any]): Specification containing target files and modifications.

        Returns:
            Dict[str, Any]: Execution result report.
        """
        plan = PatchPlan.create_plan(patch_spec)
        validation_result = PatchValidator.validate_plan(plan, self.workspace_root)

        if not validation_result.get("valid", False):
            return {
                "status": "REJECTED",
                "reason": validation_result.get("error", "Validation failed"),
                "plan": plan,
            }

        execution_result = PatchExecutor.apply_patch(plan, self.workspace_root)
        return {
            "status": "APPLIED" if execution_result.get("success", False) else "FAILED",
            "execution_details": execution_result,
        }
