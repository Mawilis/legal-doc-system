"""
Wilsy Engineering Kernel

Engineering Assurance Framework

Assurance Domain Models

Canonical immutable institutional models shared by the Engineering
Assurance Framework.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import List


class HealthStatus(str, Enum):
    """
    Institutional runtime health.
    """

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


class ReadinessStatus(str, Enum):
    """
    Institutional readiness.
    """

    READY = "READY"
    NOT_READY = "NOT_READY"
    BLOCKED = "BLOCKED"


class AssuranceStatus(str, Enum):
    """
    Overall Engineering Assurance state.
    """

    ASSURED = "ASSURED"
    WARNING = "WARNING"
    FAILED = "FAILED"


class ExecutionAuthorization(str, Enum):
    """
    Execution permission granted by the Engineering Kernel.
    """

    AUTHORIZED = "AUTHORIZED"
    DENIED = "DENIED"


@dataclass(frozen=True)
class HealthFinding:
    """
    Immutable runtime health finding.
    """

    identifier: str
    message: str


@dataclass(frozen=True)
class RuntimeHealth:
    """
    Immutable runtime health assessment.
    """

    status: HealthStatus
    score: int
    findings: List[HealthFinding] = field(default_factory=list)


@dataclass(frozen=True)
class ReadinessFinding:
    """
    Immutable readiness finding.
    """

    identifier: str
    message: str


@dataclass(frozen=True)
class EngineeringReadiness:
    """
    Immutable Engineering Kernel readiness assessment.
    """

    status: ReadinessStatus
    score: int
    findings: List[ReadinessFinding] = field(default_factory=list)


@dataclass(frozen=True)
class AssuranceFinding:
    """
    Immutable assurance finding.
    """

    identifier: str
    message: str


@dataclass(frozen=True)
class EngineeringAssurance:
    """
    Immutable institutional assurance assessment.
    """

    status: AssuranceStatus
    execution: ExecutionAuthorization
    score: int
    findings: List[AssuranceFinding] = field(default_factory=list)


@dataclass(frozen=True)
class EngineeringAssuranceReport:
    """
    Canonical Engineering Kernel institutional assurance report.

    This object represents the authoritative execution contract
    produced by the Engineering Assurance Framework.
    """

    health: RuntimeHealth
    readiness: EngineeringReadiness
    assurance: EngineeringAssurance
    generated_at: str
