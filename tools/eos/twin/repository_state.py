"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Digital Twin - Repository State Model (FG159).
    Encapsulates the immutable in-memory snapshot of the entire repository structure,
    file hashes, sizes, and operational metadata. Eliminates filesystem traversal overhead.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready repository state model. Zero child's place.
    1 Chronicles 28:12 - "And the plan of all that he had by the spirit, of the courts of the house of the Lord..."

Collaboration & Maintenance:
    - [Architecture]: Immutable repository snapshot and file metadata representation.
    - [Compliance]: Guarantees instantaneous in-memory code inspection without disk I/O.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class FileSnapshot:
    """
    Immutable in-memory record of an individual file within the repository.
    """
    file_path: str
    content_hash: str
    size_bytes: int
    line_count: int
    language: str
    last_modified_unix: float
    symbols: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes file snapshot into a dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class RepositoryState:
    """
    Immutable in-memory Digital Twin snapshot of the entire repository.
    """
    snapshot_id: str
    root_path: str
    total_files: int
    total_size_bytes: int
    files: Dict[str, FileSnapshot] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # [FUNCTION EXPLANATION]: Retrieves a file snapshot by its relative path from memory.
    def get_file(self, file_path: str) -> Optional[FileSnapshot]:
        """
        Retrieves a file snapshot from memory without disk access.
        """
        return self.files.get(file_path)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes repository state into a dictionary."""
        return {
            "snapshot_id": self.snapshot_id,
            "root_path": self.root_path,
            "total_files": self.total_files,
            "total_size_bytes": self.total_size_bytes,
            "timestamp": self.timestamp,
            "files": {path: f.to_dict() for path, f in self.files.items()},
        }

    def to_json(self) -> str:
        """Serializes repository state into formatted JSON."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)
