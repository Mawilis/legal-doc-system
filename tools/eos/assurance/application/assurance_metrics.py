"""
Wilsy Engineering Kernel

Engineering Assurance Framework

Assurance Metrics

Read-only collection of Engineering Assurance metrics.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..domain.models import EngineeringReadiness
from ..domain.models import RuntimeHealth


@dataclass(frozen=True)
class AssuranceMetrics:
    """
    Immutable Engineering Assurance metrics.

    These metrics combine the institutional outputs of the Health
    and Readiness subsystems.
    """

    health_status: str
    health_score: int
    readiness_status: str
    readiness_score: int
    total_findings: int


class AssuranceMetricsCollector:
    """
    Collect immutable Engineering Assurance metrics.

    This collector performs read-only inspection of immutable
    RuntimeHealth and EngineeringReadiness models.
    """

    def collect(
        self,
        health: RuntimeHealth,
        readiness: EngineeringReadiness,
    ) -> AssuranceMetrics:
        """
        Collect immutable Engineering Assurance metrics.
        """

        return AssuranceMetrics(
            health_status=health.status.value,
            health_score=health.score,
            readiness_status=readiness.status.value,
            readiness_score=readiness.score,
            total_findings=(
                len(health.findings)
                + len(readiness.findings)
            ),
        )
