"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Dashboard Package Initialization & Control Room Export Engine (FG170).
    Exposes dashboard coordinator, widgets, execution view, repository view modules,
    and the real-time executive control room engine & contracts.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional dashboard suite. Zero child's place.
    Enforces real-time system monitoring, visual metrics, and operational overview across Wilsy OS.

Collaboration & Maintenance:
    - [Architecture]: Unified package entrypoint for institutional control room & views.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from .contracts import ExecutiveDashboardDTO, SystemStatusEnum
from .engine import DashboardControlRoomEngine
from .router import router as dashboard_router

# Preserve legacy/existing view abstractions safely
try:
    from .dashboard import InstitutionalDashboard
except ImportError:
    InstitutionalDashboard = None  # type: ignore

try:
    from .widgets import DashboardWidgets
except ImportError:
    DashboardWidgets = None  # type: ignore

try:
    from .execution_view import ExecutionView
except ImportError:
    ExecutionView = None  # type: ignore

try:
    from .repository_view import RepositoryView
except ImportError:
    RepositoryView = None  # type: ignore


__all__ = [
    "ExecutiveDashboardDTO",
    "SystemStatusEnum",
    "DashboardControlRoomEngine",
    "dashboard_router",
    "InstitutionalDashboard",
    "DashboardWidgets",
    "ExecutionView",
    "RepositoryView",
]
