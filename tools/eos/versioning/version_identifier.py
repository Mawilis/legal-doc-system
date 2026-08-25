"""
===============================================================================
WILSY OS — INSTITUTIONAL VERSIONING ENGINE (FG209)
MODULE: STRONGLY-TYPED VERSION IDENTIFIERS
===============================================================================
Epitome:
    Defines immutable, strongly-typed version identifiers for Kernel, Execution Engine,
    Artifact, Database Schema, and API contracts. Replaces loose version strings
    with validated URN identifiers across the entire platform.

Biblical Worth Billions:
    "He calleth his own sheep by name, and leadeth them out." — John 10:3

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/versioning/version_identifier.py
===============================================================================
"""

from __future__ import annotations

import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Union

from tools.eos.versioning.semantic_version import SemanticVersion, InvalidVersionError


class VersionKind(str, Enum):
    """Enumeration of entity categories governed by the Versioning Engine."""
    KERNEL = "kernel"
    ENGINE = "engine"
    ARTIFACT = "artifact"
    SCHEMA = "schema"
    API = "api"


URN_REGEX = re.compile(
    r"^urn:wilsy:(?P<kind>kernel|engine|artifact|schema|api):(?P<name>[a-zA-Z0-9_.-]+)@(?P<version>.+)$"
)


@dataclass(frozen=True)
class VersionIdentifier:
    """
    Strongly-typed entity version identifier in Wilsy OS.
    
    Attributes:
        kind (VersionKind): The architectural category of the entity.
        name (str): Unique namespace name of the entity (e.g. 'repository', 'wilsy_kernel').
        version (SemanticVersion): Immutable semantic version object.
    """

    kind: VersionKind
    name: str
    version: SemanticVersion

    def __post_init__(self) -> None:
        """Validates name invariants."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("VersionIdentifier name must be a non-empty string.")
        
        clean_name = self.name.strip()
        if not re.match(r"^[a-zA-Z0-9_.-]+$", clean_name):
            raise ValueError(f"Invalid characters in VersionIdentifier name: '{self.name}'")

    @property
    def urn(self) -> str:
        """Returns canonical Uniform Resource Name (URN). e.g., 'urn:wilsy:engine:repository@3.5.1'."""
        return f"urn:wilsy:{self.kind.value}:{self.name}@{self.version}"

    @property
    def short_id(self) -> str:
        """Returns short identifier representation. e.g., 'repository@3.5.1'."""
        return f"{self.name}@{self.version}"

    @classmethod
    def create(cls, kind: Union[VersionKind, str], name: str, version: Union[SemanticVersion, str]) -> VersionIdentifier:
        """
        Factory method to construct a VersionIdentifier.
        
        Args:
            kind: Entity category (VersionKind or valid string enum value).
            name: System name identifier.
            version: SemanticVersion instance or valid SemVer string.
        """
        kind_enum = VersionKind(kind) if isinstance(kind, str) else kind
        semver_obj = SemanticVersion.parse(version) if isinstance(version, str) else version
        
        return cls(kind=kind_enum, name=name.strip(), version=semver_obj)

    @classmethod
    def parse_urn(cls, urn_str: str) -> VersionIdentifier:
        """
        Parses a canonical URN string into a VersionIdentifier instance.
        
        Example: 'urn:wilsy:engine:repository@3.5.1'
        """
        if not isinstance(urn_str, str):
            raise InvalidVersionError(f"Expected string for URN parsing, got {type(urn_str).__name__}")

        match = URN_REGEX.match(urn_str.strip())
        if not match:
            raise InvalidVersionError(f"Invalid Wilsy OS Version URN format: '{urn_str}'")

        groups = match.groupdict()
        kind_enum = VersionKind(groups["kind"])
        name = groups["name"]
        semver_obj = SemanticVersion.parse(groups["version"])

        return cls(kind=kind_enum, name=name, version=semver_obj)

    def __str__(self) -> str:
        return self.urn

    def __repr__(self) -> str:
        return f"VersionIdentifier({self.urn})"
