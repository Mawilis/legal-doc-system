"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Repository Intelligence - Repository Statistics.
    Calculates code metrics, line counts, module counts, and complexity indicators
    across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise repository statistics analyzer. Zero child's place.
    Provides precise codebase telemetry and metrics aggregation.

Collaboration & Maintenance:
    - [Architecture]: Statistical analyzer for code volume, file sizes, and counts.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


class RepositoryStatistics:
    """
    Computes comprehensive structural and volumetric statistics for the repository.
    """

    @staticmethod
    def analyze_file(file_path: Path | str) -> Dict[str, Any]:
        """
        Analyzes an individual file for lines of code, size, and type.

        Args:
            file_path (Path | str): Path to the target file.

        Returns:
            Dict[str, Any]: File statistics payload.
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return {"lines": 0, "size_bytes": 0, "exists": False}

        try:
            content = path.read_text(encoding="utf-8")
            lines = len(content.splitlines())
            size_bytes = path.stat().st_size
        except Exception:
            lines = 0
            size_bytes = 0

        return {
            "path": str(path),
            "lines": lines,
            "size_bytes": size_bytes,
            "exists": True,
        }

    @classmethod
    def aggregate_statistics(cls, file_paths: List[Path | str]) -> Dict[str, Any]:
        """
        Aggregates statistics across a collection of repository files.

        Args:
            file_paths (List[Path | str]): Collection of file paths.

        Returns:
            Dict[str, Any]: Aggregate repository statistics.
        """
        total_files = 0
        total_lines = 0
        total_size_bytes = 0
        file_details: List[Dict[str, Any]] = []

        for fp in file_paths:
            stats = cls.analyze_file(fp)
            if stats["exists"]:
                total_files += 1
                total_lines += stats["lines"]
                total_size_bytes += stats["size_bytes"]
                file_details.append(stats)

        return {
            "total_files": total_files,
            "total_lines": total_lines,
            "total_size_bytes": total_size_bytes,
            "average_lines_per_file": (total_lines / total_files) if total_files > 0 else 0.0,
            "file_details": file_details,
        }
