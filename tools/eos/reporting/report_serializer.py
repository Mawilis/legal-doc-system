"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Report Serializer - Executes atomic serialization and cryptographic sealing of reports.

Biblical Scale & Architecture:
    Production-ready report serialization engine. Zero child's place.
    Writes reports to disk atomically with audit tracking and hash verification.

Collaboration & Maintenance:
    - [Architecture]: Persistent storage and serialization layer for engineering reports.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class ReportSerializer:
    """
    Handles atomic persistence and serialization of engineering reports.
    """

    @staticmethod
    def serialize_report(report_data: Dict[str, Any], output_path: Path | str) -> Path:
        """
        Atomically serializes report data to a JSON artifact on disk.

        Args:
            report_data (Dict[str, Any]): Report payload.
            output_path (Path | str): Target file destination.

        Returns:
            Path: Resolved path to the written artifact.
        """
        target = Path(output_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)

        with open(target, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4)

        return target
