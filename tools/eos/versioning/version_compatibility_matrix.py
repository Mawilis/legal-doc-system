"""
===============================================================================
WILSY OS — INSTITUTIONAL VERSIONING ENGINE (FG209)
MODULE: CROSS-COMPONENT COMPATIBILITY MATRIX
===============================================================================
Epitome:
    Evaluates system-wide cross-component dependency metrics. Ensures that
    combinations of Kernel, Execution Engine, Database Schema, and API contracts
    satisfy precise interoperability bounds before boot or deployment.

Biblical Worth Billions:
    "Can two walk together, except they be agreed?" — Amos 3:3

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/versioning/version_compatibility_matrix.py
===============================================================================
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from tools.eos.versioning.version_identifier import VersionIdentifier, VersionKind
from tools.eos.versioning.version_constraints import VersionConstraintSpec


class IncompatibleComponentError(Exception):
    """Raised when a set of components violates platform compatibility rules."""
    pass


@dataclass(frozen=True)
class DependencyRequirement:
    """Represents a prerequisite dependency constraint on another system module."""
    target_kind: VersionKind
    target_name: str
    constraint_spec: VersionConstraintSpec


@dataclass
class CompatibilityRule:
    """Defines dependency requirements for a specific source VersionIdentifier."""
    source_identifier: VersionIdentifier
    dependencies: List[DependencyRequirement] = field(default_factory=list)


class VersionCompatibilityMatrix:
    """
    Thread-safe engine for registering and validating cross-component compatibility.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._rules: Dict[str, CompatibilityRule] = {}

    def register_rule(self, source_urn: str, dependencies: List[Tuple[VersionKind, str, str]]) -> None:
        """
        Registers dependency constraints for a given source URN.
        
        Args:
            source_urn: URN of the subject entity (e.g., 'urn:wilsy:engine:repository@3.5.1').
            dependencies: List of tuples (target_kind, target_name, constraint_string)
                          e.g., [(VersionKind.KERNEL, "wilsy_kernel", ">=2.0.0 <3.0.0")]
        """
        source_id = VersionIdentifier.parse_urn(source_urn)
        reqs: List[DependencyRequirement] = []

        for kind, name, spec_str in dependencies:
            spec = VersionConstraintSpec.parse(spec_str)
            reqs.append(DependencyRequirement(target_kind=kind, target_name=name, constraint_spec=spec))

        with self._lock:
            self._rules[source_id.urn] = CompatibilityRule(
                source_identifier=source_id,
                dependencies=reqs
            )

    def validate_cluster(self, active_urns: List[str]) -> Tuple[bool, List[str]]:
        """
        Validates a collection of active platform URNs against registered matrix rules.
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_violation_messages)
        """
        with self._lock:
            parsed_active = [VersionIdentifier.parse_urn(u) for u in active_urns]
            lookup: Dict[Tuple[VersionKind, str], VersionIdentifier] = {
                (item.kind, item.name): item for item in parsed_active
            }

            violations: List[str] = []

            for item in parsed_active:
                if item.urn not in self._rules:
                    continue

                rule = self._rules[item.urn]
                for req in rule.dependencies:
                    key = (req.target_kind, req.target_name)
                    if key not in lookup:
                        violations.append(
                            f"Missing required dependency '{req.target_name}' ({req.target_kind.value}) "
                            f"specified by '{item.urn}'."
                        )
                        continue

                    active_target = lookup[key]
                    if not req.constraint_spec.is_satisfied_by(active_target.version):
                        violations.append(
                            f"Incompatibility detected: '{item.urn}' requires {req.target_name} "
                            f"satisfying '{req.constraint_spec}', but active version is '{active_target.version}'."
                        )

            return len(violations) == 0, violations
