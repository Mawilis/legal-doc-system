"""
Wilsy Engineering Kernel

Institutional Validation Domain

Immutable validation models.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import List


class ValidationSeverity(str, Enum):
    """
    Severity assigned to a validation finding.
    """

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ValidationStatus(str, Enum):
    """
    Overall validation state.
    """

    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    NOT_EVALUATED = "NOT_EVALUATED"


@dataclass(frozen=True)
class ValidationRule:
    """
    Immutable validation rule.
    """

    identifier: str
    name: str
    description: str


@dataclass(frozen=True)
class ValidationFinding:
    """
    Immutable validation finding.
    """

    rule: ValidationRule
    severity: ValidationSeverity
    message: str


@dataclass(frozen=True)
class ValidationResult:
    """
    Immutable validation result.
    """

    rule: ValidationRule
    passed: bool
    finding: ValidationFinding | None = None


@dataclass(frozen=True)
class ValidationReport:
    """
    Immutable Engineering Kernel validation report.
    """

    results: List[ValidationResult] = field(default_factory=list)
    status: ValidationStatus = ValidationStatus.NOT_EVALUATED
