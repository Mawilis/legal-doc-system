"""
Wilsy Engineering Kernel

Engineering Assurance Framework

Assurance Index

Deterministic evaluation of Engineering Assurance.
"""

from __future__ import annotations

from ..domain.models import (
    AssuranceFinding,
    AssuranceStatus,
    EngineeringAssurance,
    ExecutionAuthorization,
)
from .assurance_metrics import AssuranceMetrics


class AssuranceIndex:
    """
    Evaluate immutable assurance metrics and produce an immutable
    EngineeringAssurance assessment.
    """

    def evaluate(
        self,
        metrics: AssuranceMetrics,
    ) -> EngineeringAssurance:
        """
        Evaluate Engineering Assurance.
        """

        findings: list[AssuranceFinding] = []

        score = 100

        if metrics.health_status != "HEALTHY":
            findings.append(
                AssuranceFinding(
                    identifier="EK-ASSURE-001",
                    message="Engineering Kernel health is not HEALTHY.",
                )
            )
            score -= 50

        if metrics.readiness_status != "READY":
            findings.append(
                AssuranceFinding(
                    identifier="EK-ASSURE-002",
                    message="Engineering Kernel readiness is not READY.",
                )
            )
            score -= 50

        if score == 100:
            status = AssuranceStatus.ASSURED
            execution = ExecutionAuthorization.AUTHORIZED
        elif score >= 50:
            status = AssuranceStatus.WARNING
            execution = ExecutionAuthorization.DENIED
        else:
            status = AssuranceStatus.FAILED
            execution = ExecutionAuthorization.DENIED

        return EngineeringAssurance(
            status=status,
            execution=execution,
            score=score,
            findings=findings,
        )
