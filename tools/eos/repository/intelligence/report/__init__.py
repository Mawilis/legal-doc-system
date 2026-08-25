"""
================================================================================
WILSY OS - ENTERPRISE OPERATING SYSTEM
================================================================================
FILE: tools/eos/repository/intelligence/report/__init__.py
MODULE: Intelligence Executive Report Engine Package Initialization
VERSION: 1.0.0
AUTHOR: Wilson Khanyezi & Wilsy OS Core Engineering Architecture Team
PURPOSE:
    Declares the report engine directory as an importable Python package,
    exposing the FG231CReportEngine for static analysis and runtime resolution.

EPITOME / ARCHITECTURAL INTENT:
    Establishes the report engine as a first-class citizen within the intelligence
    system, ensuring seamless integration and discovery across the entire platform.
================================================================================
"""

try:
    from.fg231c_report_engine import FG231CReportEngine  # type: ignore
    __all__ = ["FG231CReportEngine"]
except ImportError:
    __all__ = []
