"""
===============================================================================
WILSY OS — INSTITUTIONAL VERSIONING ENGINE (FG209)
MODULE: SEMANTIC VERSION IMPLEMENTATION
===============================================================================
Epitome:
    Single, immutable, canonical implementation of Semantic Versioning (SemVer 2.0.0)
    for Wilsy OS. Enforces unified string parsing, strict normalization, 
    pre-release precedence rules, build metadata isolation, and deterministic 
    ordering. No other subsystem or module parses version strings independently.

Biblical Worth Billions:
    "I am Alpha and Omega, the beginning and the ending, saith the Lord, which is, 
     and which was, and which is to come, the Almighty." — Revelation 1:8

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/versioning/semantic_version.py
===============================================================================
"""

from __future__ import annotations

import re
import functools
from dataclasses import dataclass
from typing import Tuple, Union, List


# SemVer 2.0.0 Official Specification Regular Expression
SEMVER_REGEX = re.compile(
    r"^(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


class InvalidVersionError(ValueError):
    """Raised when a version string violates SemVer 2.0.0 specification rules."""
    pass


@functools.total_ordering
@dataclass(frozen=True)
class SemanticVersion:
    """
    Immutable representation of a SemVer 2.0.0 compliant version identifier.
    
    Attributes:
        major (int): Major release version (breaking API changes).
        minor (int): Minor release version (backwards-compatible functionality).
        patch (int): Patch release version (backwards-compatible bug fixes).
        prerelease (Tuple[Union[int, str], ...]): Pre-release identifiers.
        build (Tuple[str, ...]): Build metadata identifiers (ignored in comparison).
    """

    major: int
    minor: int
    patch: int
    prerelease: Tuple[Union[int, str], ...] = ()
    build: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Enforces strict invariants upon instantiation."""
        if self.major < 0 or self.minor < 0 or self.patch < 0:
            raise InvalidVersionError(
                f"Version numbers cannot be negative: {self.major}.{self.minor}.{self.patch}"
            )

    @classmethod
    def parse(cls, version_str: str) -> SemanticVersion:
        """
        Parses a raw string into a canonical, strongly-typed SemanticVersion instance.
        
        Args:
            version_str (str): Raw version string (e.g., "2.7.3-alpha.1+sha.123abc").
            
        Returns:
            SemanticVersion: Immutable parsed version object.
            
        Raises:
            InvalidVersionError: If string does not conform strictly to SemVer 2.0.0.
        """
        if not isinstance(version_str, str):
            raise InvalidVersionError(f"Expected string for version parsing, got {type(version_str).__name__}")
            
        clean_str = version_str.strip()
        if clean_str.startswith("v") or clean_str.startswith("V"):
            clean_str = clean_str[1:]

        match = SEMVER_REGEX.match(clean_str)
        if not match:
            raise InvalidVersionError(
                f"Invalid SemVer 2.0.0 string format: '{version_str}'"
            )

        groups = match.groupdict()
        major = int(groups["major"])
        minor = int(groups["minor"])
        patch = int(groups["patch"])

        prerelease_tuple: Tuple[Union[int, str], ...] = ()
        if groups["prerelease"]:
            raw_prerelease = groups["prerelease"].split(".")
            parsed_pre: List[Union[int, str]] = []
            for item in raw_prerelease:
                if item.isdigit():
                    parsed_pre.append(int(item))
                else:
                    parsed_pre.append(item)
            prerelease_tuple = tuple(parsed_pre)

        build_tuple: Tuple[str, ...] = ()
        if groups["build"]:
            build_tuple = tuple(groups["build"].split("."))

        return cls(
            major=major,
            minor=minor,
            patch=patch,
            prerelease=prerelease_tuple,
            build=build_tuple
        )

    @property
    def is_stable(self) -> bool:
        """Returns True if major >= 1 and no pre-release tags exist."""
        return self.major >= 1 and len(self.prerelease) == 0

    @property
    def is_prerelease(self) -> bool:
        """Returns True if pre-release tags exist."""
        return len(self.prerelease) > 0

    def bump_major(self) -> SemanticVersion:
        """Increments major version and resets minor, patch, prerelease, and build."""
        return SemanticVersion(major=self.major + 1, minor=0, patch=0)

    def bump_minor(self) -> SemanticVersion:
        """Increments minor version and resets patch, prerelease, and build."""
        return SemanticVersion(major=self.major, minor=self.minor + 1, patch=0)

    def bump_patch(self) -> SemanticVersion:
        """Increments patch version and resets prerelease and build."""
        return SemanticVersion(major=self.major, minor=self.minor, patch=self.patch + 1)

    def with_prerelease(self, prerelease_str: str) -> SemanticVersion:
        """Returns new SemanticVersion with updated pre-release tags."""
        dummy = SemanticVersion.parse(f"{self.major}.{self.minor}.{self.patch}-{prerelease_str}")
        return SemanticVersion(
            major=self.major,
            minor=self.minor,
            patch=self.patch,
            prerelease=dummy.prerelease,
            build=self.build
        )

    def with_build(self, build_str: str) -> SemanticVersion:
        """Returns new SemanticVersion with updated build metadata."""
        dummy = SemanticVersion.parse(f"{self.major}.{self.minor}.{self.patch}+{build_str}")
        return SemanticVersion(
            major=self.major,
            minor=self.minor,
            patch=self.patch,
            prerelease=self.prerelease,
            build=dummy.build
        )

    def __eq__(self, other: object) -> bool:
        """
        Two versions are equal if major, minor, patch, and prerelease fields match.
        Build metadata is explicitly ignored per SemVer 2.0.0 Section 10.
        """
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.prerelease == other.prerelease
        )

    def __lt__(self, other: object) -> bool:
        """
        Strict implementation of SemVer 2.0.0 Precedence Rules (Section 11).
        Pylance type-safe explicit narrowing.
        """
        if not isinstance(other, SemanticVersion):
            return NotImplemented

        # 1. Compare numeric triples (Major, Minor, Patch)
        if (self.major, self.minor, self.patch) != (other.major, other.minor, other.patch):
            return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

        # 2. Normal version vs Pre-release version
        if not self.prerelease and other.prerelease:
            return False
        if self.prerelease and not other.prerelease:
            return True

        # 3. Compare pre-release identifiers element by element with explicit type narrowing
        for self_part, other_part in zip(self.prerelease, other.prerelease):
            if self_part == other_part:
                continue

            if isinstance(self_part, int) and isinstance(other_part, int):
                return self_part < other_part
            if isinstance(self_part, str) and isinstance(other_part, str):
                return self_part < other_part
            if isinstance(self_part, int) and isinstance(other_part, str):
                return True  # Numeric identifiers have lower precedence than non-numeric
            if isinstance(self_part, str) and isinstance(other_part, int):
                return False

        # 4. Larger set of pre-release fields has higher precedence
        return len(self.prerelease) < len(other.prerelease)

    def __str__(self) -> str:
        """Formats canonical string representation."""
        res = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            res += f"-{'.'.join(str(p) for p in self.prerelease)}"
        if self.build:
            res += f"+{'.'.join(self.build)}"
        return res

    def __repr__(self) -> str:
        return f"SemanticVersion({str(self)})"
