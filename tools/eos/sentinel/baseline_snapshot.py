"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Baseline Snapshot - Captures and maintains cryptographic hash baselines of codebase modules.

Biblical Scale & Architecture:
    Production-ready cryptographic baseline manager. Zero child's place.
    Enables secure state comparisons for tamper detection and drift prevention.

Collaboration & Maintenance:
    - [Architecture]: Cryptographic baseline state container.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict


class BaselineSnapshot:
    """
    Manages cryptographic baseline hashing for codebase integrity verification.
    """

    @staticmethod
    def compute_file_hash(file_path: Path | str) -> str:
        """
        Computes SHA-256 hash for a given file.

        Args:
            file_path (Path | str): Target file path.

        Returns:
            str: Hexadecimal SHA-256 hash digest.
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return "EXC_NOT_FOUND"

        sha256_hash = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return "EXC_READ_ERROR"

    @classmethod
    def generate_baseline(cls, file_paths: list[Path | str]) -> Dict[str, str]:
        """
        Generates a baseline mapping of file paths to their cryptographic hashes.

        Args:
            file_paths (list[Path | str]): Collection of files to baseline.

        Returns:
            Dict[str, str]: Mapping of absolute file paths to SHA-256 hashes.
        """
        baseline: Dict[str, str] = {}
        for fp in file_paths:
            path = Path(fp).resolve()
            baseline[str(path)] = cls.compute_file_hash(path)
        return baseline
