"""
===============================================================================
WILSY OS — INSTITUTIONAL VERSIONING ENGINE (FG209)
MODULE: RELATIVE VERSION COMPARATOR & COMPATIBILITY EVALUATOR
===============================================================================
Epitome:
    High-level comparator engine for evaluating version trajectories, breaking change
    boundaries, same-major generations, forward/backward compatibility, and
    upgrade safety metrics between two semantic versions.

Biblical Worth Billions:
    "Iron sharpeneth iron; so a man sharpeneth the countenance of his friend." 
    — Proverbs 27:17

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/versioning/version_comparator.py
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from tools.eos.versioning.semantic_version import SemanticVersion


@dataclass(frozen=True)
class VersionDiffSummary:
    """Detailed summary of the architectural gap between two versions."""
    base_version: SemanticVersion
    target_version: SemanticVersion
    is_newer: bool
    is_older: bool
    is_equal: bool
    same_major: bool
    same_minor: bool
    is_breaking_change: bool
    is_backwards_compatible: bool
    is_forwards_compatible: bool


class VersionComparator:
    """
    Stateless evaluation service for comparing semantic versions.
    """

    @staticmethod
    def _to_semver(ver: Union[SemanticVersion, str]) -> SemanticVersion:
        if isinstance(ver, SemanticVersion):
            return ver
        return SemanticVersion.parse(ver)

    @classmethod
    def is_newer(cls, base: Union[SemanticVersion, str], target: Union[SemanticVersion, str]) -> bool:
        """Returns True if target is newer than base."""
        return cls._to_semver(target) > cls._to_semver(base)

    @classmethod
    def is_older(cls, base: Union[SemanticVersion, str], target: Union[SemanticVersion, str]) -> bool:
        """Returns True if target is older than base."""
        return cls._to_semver(target) < cls._to_semver(base)

    @classmethod
    def same_major(cls, base: Union[SemanticVersion, str], target: Union[SemanticVersion, str]) -> bool:
        """Returns True if both versions share the exact same major version integer."""
        b = cls._to_semver(base)
        t = cls._to_semver(target)
        return b.major == t.major

    @classmethod
    def is_breaking_change(cls, base: Union[SemanticVersion, str], target: Union[SemanticVersion, str]) -> bool:
        """
        Determines if upgrading from base to target introduces a breaking change.
        Per SemVer 2.0.0, any increment in Major version (for major >= 1) is breaking.
        For 0.y.z versions, any increment in Minor version is treated as breaking.
        """
        b = cls._to_semver(base)
        t = cls._to_semver(target)

        if b.major >= 1:
            return t.major > b.major
        # Zero major versioning (0.x.x)
        return (t.major > 0) or (t.minor > b.minor)

    @classmethod
    def is_backwards_compatible(cls, base: Union[SemanticVersion, str], target: Union[SemanticVersion, str]) -> bool:
        """
        Returns True if target version is backwards compatible with base version.
        Requires target >= base and no breaking changes between them.
        """
        b = cls._to_semver(base)
        t = cls._to_semver(target)
        if t < b:
            return False
        return not cls.is_breaking_change(b, t)

    @classmethod
    def is_forwards_compatible(cls, base: Union[SemanticVersion, str], target: Union[SemanticVersion, str]) -> bool:
        """
        Returns True if base version can accept data/code compiled for target version
        assuming target is within the same minor release generation.
        """
        b = cls._to_semver(base)
        t = cls._to_semver(target)
        if t.major != b.major:
            return False
        return t.minor == b.minor

    @classmethod
    def analyze_diff(cls, base: Union[SemanticVersion, str], target: Union[SemanticVersion, str]) -> VersionDiffSummary:
        """
        Generates a comprehensive VersionDiffSummary object comparing base and target.
        """
        b = cls._to_semver(base)
        t = cls._to_semver(target)

        return VersionDiffSummary(
            base_version=b,
            target_version=t,
            is_newer=t > b,
            is_older=t < b,
            is_equal=t == b,
            same_major=b.major == t.major,
            same_minor=(b.major == t.major and b.minor == t.minor),
            is_breaking_change=cls.is_breaking_change(b, t),
            is_backwards_compatible=cls.is_backwards_compatible(b, t),
            is_forwards_compatible=cls.is_forwards_compatible(b, t)
        )
