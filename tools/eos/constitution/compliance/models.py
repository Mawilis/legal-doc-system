"""
Wilsy Engineering Kernel
Engineering Constitution Manager

Compliance Domain Models

Immutable institutional models used by the Constitution Compliance Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ComplianceStatus(str, Enum):
    """
    Institutional compliance state.
    """

    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    WARNING = "WARNING"
    NOT_EVALUATED = "NOT_EVALUATED"


@dataclass(frozen=True)
class ComplianceRule:
    """
    Immutable constitutional compliance rule.
    """

    identifier: str
    title: str
    description: str


@dataclass(frozen=True)
class ComplianceFinding:
    """
    Immutable compliance finding.
    """

    rule: ComplianceRule
    status: ComplianceStatus
    evidence: List[str] = field(default_factory=list)
    rationale: str = ""


@dataclass(frozen=True)
class ComplianceReport:
    """
    Immutable Engineering Kernel compliance report.
    """

    evaluated_rules: List[ComplianceRule] = field(default_factory=list)
    findings: List[ComplianceFinding] = field(default_factory=list)
    status: ComplianceStatus = ComplianceStatus.NOT_EVALUATED
