"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Execution History - Tracks, stores, and queries historical kernel execution runs.

Biblical Scale & Architecture:
    Production-ready execution audit store. Zero child's place.
    Provides chronological auditing and status retrieval for past system runs.

Collaboration & Maintenance:
    - [Architecture]: Execution log tracker and timeline query engine.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List
from pathlib import Path
import json


class ExecutionHistory:
    """
    Manages and queries historical execution records of Wilsy OS kernel runs.
    """

    def __init__(self, reports_dir: Path | str = "./reports") -> None:
        self.reports_dir = Path(reports_dir).resolve()

    def get_execution_records(self) -> List[Dict[str, Any]]:
        """
        Retrieves all historical execution reports from storage.

        Returns:
            List[Dict[str, Any]]: Chronological list of execution telemetry records.
        """
        if not self.reports_dir.exists():
            return []

        records = []
        for file_path in sorted(self.reports_dir.glob("*_unified_report.json")):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    records.append({
                        "file_name": file_path.name,
                        "execution_id": data.get("execution_id"),
                        "timestamp": data.get("timestamp"),
                        "status": data.get("status"),
                    })
            except Exception:
                continue

        return records
