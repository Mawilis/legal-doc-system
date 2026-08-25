"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Widgets - Generates modular UI components and telemetry widgets for the dashboard.

Biblical Scale & Architecture:
    Production-ready widget generation utility. Zero child's place.
    Provides metric cards, status badges, and summary blocks for institutional telemetry.

Collaboration & Maintenance:
    - [Architecture]: Dashboard widget component generator.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict


class DashboardWidgets:
    """
    Constructs modular widget representations for dashboard integration.
    """

    @staticmethod
    def create_metric_card(title: str, value: Any, status: str = "NORMAL") -> Dict[str, Any]:
        """
        Generates a standard metric card widget.

        Args:
            title (str): Metric title.
            value (Any): Metric value.
            status (str): Operational status indicator.

        Returns:
            Dict[str, Any]: Widget component schema.
        """
        return {
            "widget_type": "METRIC_CARD",
            "title": title,
            "value": value,
            "status": status,
        }

    @staticmethod
    def create_status_badge(component_name: str, health: str) -> Dict[str, Any]:
        """
        Generates a subsystem status badge widget.

        Args:
            component_name (str): Name of the subsystem.
            health (str): Health state.

        Returns:
            Dict[str, Any]: Status badge schema.
        """
        return {
            "widget_type": "STATUS_BADGE",
            "component": component_name,
            "health": health,
        }
