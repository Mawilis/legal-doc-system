"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Integrity Monitor - Detects file modifications and drift against known baselines.

Biblical Scale & Architecture:
    Production-ready integrity monitoring engine. Zero child's place.
    Performs real-time diff checking between active files and cryptographic baselines.

Collaboration & Maintenance:
    - [Architecture]: Drift detection engine for codebase integrity assurance.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .baseline_snapshot import BaselineSnapshot


class IntegrityMonitor:
    """
    Monitors repository files for modifications, additions, and deletions against a baseline.
    """

    @staticmethod
    def check_integrity(baseline: Dict[str, str]) -> Dict[str, Any]:
        """
        Checks active files against a saved baseline to detect drift or modification.

        Args:
            baseline (Dict[str, str]): Mapping of file paths to expected baseline hashes.

        Returns:
            Dict[str, Any]: Integrity verification report detailing modified or missing files.
        """
        modified_files: List[str] = []
        missing_files: List[str] = []
        checked_count = 0

        for file_path_str, expected_hash in baseline.items():
            path = Path(file_path_str)
            checked_count += 1
            if not path.exists():
                missing_files.append(file_path_str)
                continue

            current_hash = BaselineSnapshot.compute_file_hash(path)
            if current_hash != expected_hash:
                modified_files.append(file_path_str)

        is_intact = len(modified_files) == 0 and len(missing_files) == 0

        return {
            "is_intact": is_intact,
            "checked_count": checked_count,
            "modified_files": modified_files,
            "missing_files": missing_files,
        }
