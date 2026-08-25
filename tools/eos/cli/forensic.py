#!/usr/bin/env python3
"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Forensic Grep - High-performance recursive code auditor and compliance scanner.

Biblical Scale & Architecture:
    Production-ready forensic scanner for Wilsy OS. Zero child's place.
    Validates codebase integrity, collaboration comments, and pattern matching
    with buffer-safe file export and summary rendering.
    Proverbs 15:3 - "The eyes of the Lord are everywhere, keeping watch on the wicked and the good."

Collaboration & Maintenance:
    - [Architecture]: Recursive forensic file scanning and telemetry auditor.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import os
import sys
import re
import json
import time
from pathlib import Path
from typing import List, Dict, Any

# Collaboration & Architecture Metadata defining the sovereign namespace
__author__ = "Wilson Khanyezi"
__version__ = "1.1.0-billion-dollar-release"
__epitome__ = "Institutional-grade forensic grep with buffer-safe report export."


class ForensicGrep:
    """
    Class Name: ForensicGrep
    Purpose: Recursively scans workspace files for pattern matching and exports safe audit reports.
    Collaboration Note: Billion-dollar architectural standard preventing terminal buffer overflows.
    """

    def __init__(self, workspace_root: Path | str = ".", exclude_dirs: List[str] = None) -> None:
        """
        Function Name: __init__
        Purpose: Initializes the ForensicGrep auditor with workspace path and exclusions.
        Args:
            workspace_root (Path | str): Root directory to scan.
            exclude_dirs (List[str]): Directories to ignore during traversal.
        Collaboration Note: Establishes base path resolution and ignore lists for clean traversal.
        """
        # [COLLABORATION COMMENT]: Set up absolute workspace path and standard exclusions
        self.workspace_root = Path(workspace_root).resolve()
        self.exclude_dirs = exclude_dirs or [".venv", "venv", ".git", "__pycache__", "reports", "build", "dist", "node_modules"]

    def scan_files(self, pattern: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Function Name: scan_files
        Purpose: Recursively searches all project files for a given regular expression pattern.
        Args:
            pattern (str): Regular expression pattern to search for across files.
        Returns:
            Dict[str, List[Dict[str, Any]]]: Mapping of file paths to matched lines and details.
        Collaboration Note: Core scanning algorithm ensuring 100% codebase transparency.
        """
        # [COLLABORATION COMMENT]: Compile regex pattern with case-insensitive support
        # [FUNCTION EXPLANATION]: Walks directory tree, skips ignored folders, matches pattern line-by-line
        compiled_pattern = re.compile(pattern, re.IGNORECASE)
        results: Dict[str, List[Dict[str, Any]]] = {}

        for root, dirs, files in os.walk(self.workspace_root):
            # Prune excluded directories in-place to optimize traversal speed
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                file_path = Path(root) / file
                # Skip binary, compiled, or archive extensions
                if file_path.suffix.lower() in [".pyc", ".png", ".jpg", ".jpeg", ".pdf", ".lock", ".zip", ".tar", ".gz"]:
                    continue

                matches = []
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, start=1):
                            if compiled_pattern.search(line):
                                matches.append({
                                    "line_number": line_num,
                                    "content": line.strip()
                                })
                except Exception as e:
                    matches.append({
                        "line_number": 0,
                        "content": f"[ERROR READING FILE]: {str(e)}"
                    })

                if matches:
                    rel_path = str(file_path.relative_to(self.workspace_root))
                    results[rel_path] = matches

        return results

    def render_audit_report(self, pattern: str) -> None:
        """
        Function Name: render_audit_report
        Purpose: Executes forensic scan, writes full payload to disk, and renders a safe summary to console.
        Args:
            pattern (str): Pattern to search for.
        Collaboration Note: Protects operator terminals from buffer overflow during broad searches.
        """
        # [COLLABORATION COMMENT]: Invoke scan engine and write detailed payload safely to disk
        print("==================================================")
        print("       WILSY OS: FORENSIC CODE AUDIT SCANNER      ")
        print("       Billion-Dollar Sovereign Architecture      ")
        print("==================================================")
        print(f" Target Pattern : '{pattern}'")
        print(f" Workspace Root : {self.workspace_root}")
        print("------------------------------------------------==")

        results = self.scan_files(pattern)
        total_matches = sum(len(m) for m in results.values())

        # Ensure reports directory exists and save full audit payload atomically
        reports_dir = self.workspace_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        report_filename = f"forensic_audit_{int(time.time())}.json"
        report_path = reports_dir / report_filename

        audit_payload = {
            "pattern": pattern,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "total_files_matched": len(results),
            "total_matches": total_matches,
            "results": results
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(audit_payload, f, indent=4)

        # Render safe summary table to console to prevent terminal crash
        if not results:
            print(" [+] Status : ZERO MATCHES FOUND (Clean Codebase)")
        else:
            print(f" [+] Found matches across {len(results)} file(s). Total instances: {total_matches}")
            print("\n --- Top Matching Files (Summary) ---")
            for file_path, matches in list(results.items())[:15]:
                print(f"   [FILE] {file_path:<40} : {len(matches)} match(es)")
            if len(results) > 15:
                print(f"   ... and {len(results) - 15} more file(s).")

        print("==================================================")
        print(f" [+] Detailed audit report saved safely to:")
        print(f"     {report_path}")
        print("==================================================")


if __name__ == "__main__":
    # [COLLABORATION COMMENT]: Accept pattern from command line or default to auditing collaboration tags
    target_pattern = sys.argv[1] if len(sys.argv) > 1 else "COLLABORATION"
    auditor = ForensicGrep()
    auditor.render_audit_report(target_pattern)
    sys.exit(0)
