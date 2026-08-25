"""
Wilsy Engineering Kernel

Kernel Foundation Registry

Provides stable access to Engineering Kernel Foundation Services.
"""

from __future__ import annotations

from .evidence import EvidenceService
from .filesystem import FilesystemService


class KernelRegistry:
    """
    Registry of Engineering Kernel Foundation Services.

    The registry owns no business logic.
    """

    def __init__(self) -> None:
        self._filesystem = FilesystemService()
        self._evidence = EvidenceService()

    @property
    def filesystem(self) -> FilesystemService:
        """
        Access the read-only filesystem service.
        """

        return self._filesystem

    @property
    def evidence(self) -> EvidenceService:
        """
        Access the repository evidence service.
        """

        return self._evidence
