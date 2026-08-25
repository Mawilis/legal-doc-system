"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Reporting Framework Package Initialization.
    Exposes unified report, serializer, dashboard, and artifact catalog modules.

Biblical Scale & Architecture:
    Production-ready automated institutional reporting suite. Zero child's place.
    Enforces exhaustive telemetry aggregation, serialization, and executive visualization across Wilsy OS.

Collaboration & Maintenance:
    - [Architecture]: Package entrypoint for institutional analytics and reporting subsystems.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from .unified_report import UnifiedReport
from .report_serializer import ReportSerializer
from .report_dashboard import ReportDashboard
from .artifact_catalog import ArtifactCatalog

__all__ = [
    "UnifiedReport",
    "ReportSerializer",
    "ReportDashboard",
    "ArtifactCatalog",
]
