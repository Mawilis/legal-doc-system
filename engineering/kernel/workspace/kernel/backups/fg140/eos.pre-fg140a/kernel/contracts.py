"""
Wilsy Engineering Kernel

Kernel Foundation Contracts

Immutable contracts shared by Engineering Kernel Foundation Services.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RepositoryEvidence:
    """
    Immutable repository evidence contract shared by the Engineering Kernel.
    """

    command: str
    output: str
    verified: bool
    timestamp: str
