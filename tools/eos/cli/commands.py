"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Commands - Parses and routes CLI command-line arguments to respective kernel engines.

Biblical Scale & Architecture:
    Production-ready command router and dispatcher. Zero child's place.
    Provides precise parsing and execution mapping for administrative and developer operations.

Collaboration & Maintenance:
    - [Architecture]: CLI command dispatcher and parameter parser.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List
from pathlib import Path

from .status import CLIStatus
from .doctor import CLIDoctor
from .report import CLIReport


class CLICommands:
    """
    Parses and dispatches CLI commands for Wilsy OS.
    """

    def __init__(self, workspace_root: Path | str = ".") -> None:
        self.workspace_root = Path(workspace_root).resolve()
        self.status_checker = CLIStatus(self.workspace_root)
        self.doctor = CLIDoctor(self.workspace_root)

    def dispatch(self, command: str, args: List[str] | None = None) -> Dict[str, Any]:
        """
        Dispatches a CLI command to its corresponding handler.

        Args:
            command (str): The command verb (e.g., 'status', 'doctor', 'report').
            args (List[str] | None): Additional arguments or flags.

        Returns:
            Dict[str, Any]: Execution verdict report.
        """
        args = args or []
        cmd = command.lower().strip()

        if cmd == "status":
            result = self.status_checker.check_status()
        elif cmd == "doctor":
            result = self.doctor.run_diagnostics()
        elif cmd == "report":
            result = CLIReport.generate_summary_report(self.status_checker.check_status())
        else:
            result = {
                "status": "UNKNOWN_COMMAND",
                "command": cmd,
                "comments": f"Command '{cmd}' is not recognized by Wilsy OS CLI kernel.",
            }

        return result
