"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Quality Engine - Orchestrates comprehensive quality, architecture, and security assessments.

Biblical Scale & Architecture:
    Production-ready quality orchestration pipeline. Zero child's place.
    Aggregates sub-quality evaluations into a unified compliance score and report.

Collaboration & Maintenance:
    - [Architecture]: Master coordinator for repository quality audits.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List
from pathlib import Path

from .code_quality import CodeQualityChecker
from .architecture_quality import ArchitectureQualityChecker
from .security_quality import SecurityQualityChecker


class QualityEngine:
    """
    Orchestrates comprehensive quality inspections across codebases, architecture, and security vectors.
    """

    def __init__(self, workspace_root: Path | str = ".") -> None:
        self.workspace_root = Path(workspace_root).resolve()

    def run_full_audit(self) -> Dict[str, Any]:
        """
        Executes a complete quality audit across all modules.

        Returns:
            Dict[str, Any]: Comprehensive quality audit report.
        """
        code_report = CodeQualityChecker.inspect_codebase(self.workspace_root)
        arch_report = ArchitectureQualityChecker.inspect_architecture(self.workspace_root)
        sec_report = SecurityQualityChecker.inspect_security(self.workspace_root)

        is_compliant = (
            code_report.get("passed", False)
            and arch_report.get("passed", False)
            and sec_report.get("passed", False)
        )

        return {
            "audit_status": "PASSED" if is_compliant else "REVIEW_REQUIRED",
            "code_quality": code_report,
            "architecture_quality": arch_report,
            "security_quality": sec_report,
        }
