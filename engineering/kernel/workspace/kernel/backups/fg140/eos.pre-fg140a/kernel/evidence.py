"""
Wilsy Engineering Kernel

Kernel Foundation Services

Repository Evidence Service

Read-only production of immutable repository evidence.
"""

from __future__ import annotations

from pathlib import Path

from .contracts import RepositoryEvidence


class EvidenceService:
    """
    Produce immutable repository evidence.

    This service never modifies repository artifacts.
    """

    def create(
        self,
        command: str,
        path: Path,
        output: str,
        verified: bool,
        timestamp: str,
    ) -> RepositoryEvidence:
        """
        Create immutable repository evidence.
        """

        return RepositoryEvidence(
            command=command,
            output=f"{path}:{output}",
            verified=verified,
            timestamp=timestamp,
        )
