"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Policy Models - Institutional Rule Data Structures (FG165).
    Defines policy definitions, violation reports, and compliance evaluation results.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional governance rules. Righteous standards and laws.
    Psalm 19:7 - "The law of the Lord is perfect, reviving the soul..."

Collaboration & Maintenance:
    - [Architecture]: Immutable dataclasses for policy rules and violations.
    - [Compliance]: Structured data models for institutional governance.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class PolicyRule:
    """Immutable definition of a governance policy rule."""
    rule_id: str
    name: str
    category: str  # e.g., 'size', 'complexity', 'naming', 'release'
    severity: str  # e.g., 'ERROR', 'WARNING', 'INFO'
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyViolation:
    """Details of a specific policy violation."""
    rule_id: str
    target: str
    message: str
    severity: str


@dataclass(frozen=True)
class PolicyEvaluationResult:
    """Result of evaluating policies against a target asset."""
    target_id: str
    passed: bool
    violations: Tuple[PolicyViolation, ...] = field(default_factory=tuple)
    warnings: Tuple[PolicyViolation, ...] = field(default_factory=tuple)
