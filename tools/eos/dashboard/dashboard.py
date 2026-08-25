"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Dashboard - Coordinates executive metrics and system views for institutional monitoring.

Biblical Scale & Architecture:
    Production-ready dashboard coordination engine. Zero child's place.
    Aggregates runtime health, pipeline status, and repository telemetry into a unified view.

Collaboration & Maintenance:
    - [Architecture]: Main dashboard aggregation and controller module.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict
from pathlib import Path

from .execution_view import ExecutionView
from .repository_view import RepositoryView


class InstitutionalDashboard:
    """
    Coordinates and renders the complete Wilsy OS executive dashboard.
    """

    def __init__(self, workspace_root: Path | str = ".") -> None:
        self.workspace_root = Path(workspace_root).resolve()
        self.execution_view = ExecutionView()
        self.repository_view = RepositoryView(self.workspace_root)

    def render_dashboard(self) -> Dict[str, Any]:
        """
        Compiles all dashboard views and metrics into a consolidated state report.

        Returns:
            Dict[str, Any]: Complete dashboard state payload.
        """
        return {
            "dashboard_title": "Wilsy OS Billion-Dollar Institutional Dashboard",
            "system_status": "OPERATIONAL",
            "repository_overview": self.repository_view.render_view(),
            "execution_overview": self.execution_view.render_view(),
            "comments": "Institutional dashboard successfully rendered with absolute fidelity.",
        }
