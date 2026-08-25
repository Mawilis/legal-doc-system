"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    CLI Package Initialization.
    Exposes command processor, status checker, doctor utility, and report formatter modules.

Biblical Scale & Architecture:
    Production-ready institutional command-line interface suite. Zero child's place.
    Enforces robust interaction, diagnostics, and operational controls across Wilsy OS.

Collaboration & Maintenance:
    - [Architecture]: Package entrypoint for terminal command-line interface subsystems.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from .commands import CLICommands
from .status import CLIStatus
from .doctor import CLIDoctor
from .report import CLIReport

__all__ = [
    "CLICommands",
    "CLIStatus",
    "CLIDoctor",
    "CLIReport",
]
