"""
================================================================================
WILSY OS - ENTERPRISE OPERATING SYSTEM
================================================================================
FILE: conftest.py
MODULE: Root Pytest Test Discovery & Module Path Resolution Engine
VERSION: 1.0.0
AUTHOR: Wilson Khanyezi & Wilsy OS Core Engineering Architecture Team
PURPOSE:
    Guarantees that the repository root directory is injected into sys.path
    prior to pytest collecting any test modules across the workspace.

EPITOME / ARCHITECTURAL INTENT:
    Fixes top-level package resolution for dynamic test execution, preventing
    ModuleNotFoundError during test module AST parsing and collection phase.
================================================================================
"""

import os
import sys

# Force project root directory to head of sys.path prior to test collection
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
