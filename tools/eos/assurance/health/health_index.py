"""
Wilsy Engineering Kernel

Engineering Assurance Framework

Health Index

Deterministic evaluation of Engineering Kernel runtime health.
"""

from __future__ import annotations

from ..domain.models import (
    HealthFinding,
    HealthStatus,
    RuntimeHealth,
)
from .health_metrics import HealthMetrics


class HealthIndex:
    """
    Evaluate immutable runtime metrics and produce an immutable
    RuntimeHealth assessment.
    """

    def evaluate(
        self,
        metrics: HealthMetrics,
    ) -> RuntimeHealth:
        """
        Evaluate Engineering Kernel runtime health.
        """

        findings: list[HealthFinding] = []

        score = 100

        if not metrics.kernel_initialized:
            findings.append(
                HealthFinding(
                    identifier="EK-HEALTH-001",
                    message="Engineering Kernel is not initialized.",
                )
            )
            score -= 50

        if not metrics.registry_available:
            findings.append(
                HealthFinding(
                    identifier="EK-HEALTH-002",
                    message="Kernel Foundation Registry is unavailable.",
                )
            )
            score -= 50

        if score == 100:
            status = HealthStatus.HEALTHY
        elif score >= 50:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.FAILED

        return RuntimeHealth(
            status=status,
            score=score,
            findings=findings,
        )
