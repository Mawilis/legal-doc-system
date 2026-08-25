"""
Wilsy Engineering Kernel

Engineering Assurance Framework

Readiness Index

Deterministic evaluation of Engineering Kernel readiness.
"""

from __future__ import annotations

from ..domain.models import (
    EngineeringReadiness,
    ReadinessFinding,
    ReadinessStatus,
)
from .readiness_metrics import ReadinessMetrics


class ReadinessIndex:
    """
    Evaluate immutable readiness metrics and produce an immutable
    EngineeringReadiness assessment.
    """

    def evaluate(
        self,
        metrics: ReadinessMetrics,
    ) -> EngineeringReadiness:
        """
        Evaluate Engineering Kernel readiness.
        """

        findings: list[ReadinessFinding] = []

        score = 100

        if metrics.health_status != "HEALTHY":
            findings.append(
                ReadinessFinding(
                    identifier="EK-READY-001",
                    message="Engineering Kernel health is not HEALTHY.",
                )
            )
            score -= 50

        if metrics.finding_count > 0:
            findings.append(
                ReadinessFinding(
                    identifier="EK-READY-002",
                    message="Engineering Kernel health contains outstanding findings.",
                )
            )
            score -= 50

        if score == 100:
            status = ReadinessStatus.READY
        elif score >= 50:
            status = ReadinessStatus.NOT_READY
        else:
            status = ReadinessStatus.BLOCKED

        return EngineeringReadiness(
            status=status,
            score=score,
            findings=findings,
        )
