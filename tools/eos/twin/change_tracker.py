"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Digital Twin - Change Tracker & Delta Registry (FG159).
    Tracks file modifications, additions, and deletions against the in-memory Digital Twin
    snapshot without requiring disk traversal.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready change tracking engine. Zero child's place.
    Lamentations 3:23 - "The steadfast love of the Lord never ceases; his mercies never come to an end; they are new every morning."

Collaboration & Maintenance:
    - [Architecture]: In-memory delta engine detecting modified, added, and deleted files.
    - [Compliance]: Guarantees instantaneous change auditing without filesystem I/O.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Set


@dataclass(frozen=True)
class ChangeDelta:
    """
    Immutable summary of repository changes detected against the Digital Twin baseline.
    """
    added_files: List[str] = field(default_factory=list)
    modified_files: List[str] = field(default_factory=list)
    deleted_files: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def has_changes(self) -> bool:
        """Returns True if any additions, modifications, or deletions occurred."""
        return bool(self.added_files or self.modified_files or self.deleted_files)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes change delta into a dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Serializes change delta into formatted JSON."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


class ChangeTracker:
    """
    Evaluates current states against the Digital Twin repository snapshot
    to compute precise deltas in memory.
    """

    # [FUNCTION EXPLANATION]: Computes added, modified, and deleted files purely from memory maps.
    @staticmethod
    def compute_delta(
        baseline_files: Set[str],
        current_files: Set[str],
        baseline_hashes: Dict[str, str],
        current_hashes: Dict[str, str],
    ) -> ChangeDelta:
        """
        Computes repository deltas between baseline and current states without disk I/O.
        """
        baseline_set = set(baseline_files)
        current_set = set(current_files)

        added = sorted(list(current_set - baseline_set))
        deleted = sorted(list(baseline_set - current_set))
        
        intersection = baseline_set.intersection(current_set)
        modified = []
        for path in sorted(list(intersection)):
            if baseline_hashes.get(path) != current_hashes.get(path):
                modified.append(path)

        return ChangeDelta(
            added_files=added,
            modified_files=modified,
            deleted_files=deleted,
        )
