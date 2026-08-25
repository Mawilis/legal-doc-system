"""
===============================================================================
WILSY OS — INSTITUTIONAL VERSIONING ENGINE (FG209)
MODULE: ENTERPRISE VERSION CONSTRAINTS & SPECIFICATION EVALUATOR
===============================================================================
Epitome:
    Enterprise-grade version constraint parser and range evaluator. Supports
    exact bounds (=), inequality comparisons (>, >=, <, <=), caret ranges (^),
    tilde ranges (~), wildcards (*, 2.x), and compound logical specs (>=2.0.0 <3.0.0).

Biblical Worth Billions:
    "Remove not the ancient landmark, which thy fathers have set." — Proverbs 22:28

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/versioning/version_constraints.py
===============================================================================
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import List, Tuple, Union, Optional

from tools.eos.versioning.semantic_version import SemanticVersion, InvalidVersionError


class InvalidConstraintError(ValueError):
    """Raised when a version constraint specification is malformed."""
    pass


class BaseVersionConstraint(ABC):
    """Abstract base class for individual version constraints."""

    @abstractmethod
    def is_satisfied_by(self, version: SemanticVersion) -> bool:
        """Evaluates whether a target version satisfies this constraint."""
        pass


class WildcardConstraint(BaseVersionConstraint):
    """Matches any version (* or wildcards like 2.x)."""

    def __init__(self, prefix: Optional[Tuple[int, ...]] = None) -> None:
        self.prefix = prefix or ()

    def is_satisfied_by(self, version: SemanticVersion) -> bool:
        if not self.prefix:
            return True
        version_parts = (version.major, version.minor, version.patch)
        for p, v in zip(self.prefix, version_parts):
            if p != v:
                return False
        return True

    def __str__(self) -> str:
        if not self.prefix:
            return "*"
        return ".".join(str(p) for p in self.prefix) + ".*"


class ComparisonConstraint(BaseVersionConstraint):
    """Handles standard comparison operators: =, ==, >, >=, <, <=."""

    def __init__(self, operator: str, target: SemanticVersion) -> None:
        if operator not in ("=", "==", ">", ">=", "<", "<="):
            raise InvalidConstraintError(f"Unsupported comparison operator: '{operator}'")
        self.operator = operator
        self.target = target

    def is_satisfied_by(self, version: SemanticVersion) -> bool:
        if self.operator in ("=", "=="):
            return version == self.target
        elif self.operator == ">":
            return version > self.target
        elif self.operator == ">=":
            return version >= self.target
        elif self.operator == "<":
            return version < self.target
        elif self.operator == "<=":
            return version <= self.target
        return False

    def __str__(self) -> str:
        return f"{self.operator}{self.target}"


class CaretConstraint(BaseVersionConstraint):
    """
    Caret range operator (^): Allows changes that do not modify the left-most non-zero element.
    ^1.2.3  => >=1.2.3 <2.0.0
    ^0.2.3  => >=0.2.3 <0.3.0
    ^0.0.3  => ==0.0.3
    """

    def __init__(self, target: SemanticVersion) -> None:
        self.target = target
        if target.major != 0:
            self.upper_bound = SemanticVersion(target.major + 1, 0, 0)
        elif target.minor != 0:
            self.upper_bound = SemanticVersion(0, target.minor + 1, 0)
        else:
            self.upper_bound = SemanticVersion(0, 0, target.patch + 1)

    def is_satisfied_by(self, version: SemanticVersion) -> bool:
        return self.target <= version < self.upper_bound

    def __str__(self) -> str:
        return f"^{self.target}"


class TildeConstraint(BaseVersionConstraint):
    """
    Tilde range operator (~): Allows patch-level changes if minor is specified.
    ~1.2.3  => >=1.2.3 <1.3.0
    """

    def __init__(self, target: SemanticVersion) -> None:
        self.target = target
        self.upper_bound = SemanticVersion(target.major, target.minor + 1, 0)

    def is_satisfied_by(self, version: SemanticVersion) -> bool:
        return self.target <= version < self.upper_bound

    def __str__(self) -> str:
        return f"~{self.target}"


class VersionConstraintSpec:
    """
    Evaluates complex composite version constraint expressions.
    Example expressions: ">=2.0.0 <3.0.0", "^2.4", "~2.8.1", "2.x", ">=1.0.0, <=2.0.0"
    """

    def __init__(self, raw_spec: str) -> None:
        self.raw_spec = raw_spec.strip()
        self.constraints: List[BaseVersionConstraint] = self._parse_spec(self.raw_spec)

    @classmethod
    def parse(cls, raw_spec: str) -> VersionConstraintSpec:
        return cls(raw_spec)

    def is_satisfied_by(self, version: Union[SemanticVersion, str]) -> bool:
        target_ver = version if isinstance(version, SemanticVersion) else SemanticVersion.parse(version)
        if not self.constraints:
            return True
        return all(c.is_satisfied_by(target_ver) for c in self.constraints)

    def _parse_spec(self, spec_str: str) -> List[BaseVersionConstraint]:
        if not spec_str or spec_str == "*":
            return [WildcardConstraint()]

        parsed: List[BaseVersionConstraint] = []
        clean = spec_str.replace(",", " ")
        tokens = [t.strip() for t in clean.split() if t.strip()]

        for token in tokens:
            if token == "*":
                parsed.append(WildcardConstraint())
                continue

            wildcard_match = re.match(r"^(\d+)(?:\.(x|X|\*))?(?:\.(x|X|\*))?$", token)
            if wildcard_match:
                prefix_val = int(wildcard_match.group(1))
                parsed.append(WildcardConstraint(prefix=(prefix_val,)))
                continue

            if token.startswith("^"):
                ver = SemanticVersion.parse(token[1:])
                parsed.append(CaretConstraint(ver))
            elif token.startswith("~"):
                ver = SemanticVersion.parse(token[1:])
                parsed.append(TildeConstraint(ver))
            elif token.startswith((">=", "<=", "==", ">", "<", "=")):
                match = re.match(r"^(>=|<=|==|>|<|=)(.+)$", token)
                if not match:
                    raise InvalidConstraintError(f"Malformed constraint token: '{token}'")
                op, ver_str = match.groups()
                ver = SemanticVersion.parse(ver_str)
                parsed.append(ComparisonConstraint(op, ver))
            else:
                ver = SemanticVersion.parse(token)
                parsed.append(ComparisonConstraint("=", ver))

        return parsed

    def __str__(self) -> str:
        return self.raw_spec

    def __repr__(self) -> str:
        return f"VersionConstraintSpec('{self.raw_spec}')"
