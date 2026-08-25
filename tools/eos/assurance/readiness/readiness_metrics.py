"""
Wilsy Engineering Kernel

Engineering Assurance Framework

Readiness Metrics

Read-only collection of Engineering Kernel readiness metrics.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..domain.models import RuntimeHealth


@dataclass(frozen=True)
class ReadinessMetrics:
    """
    Immutable readiness metrics derived from runtime health.
    """

    health_status: str
    health_score: int
    finding_count: int


class ReadinessMetricsCollector:
    """
    Collect immutable readiness metrics.

    This collector performs read-only inspection of the immutable
    RuntimeHealth produced by the Health subsystem.
    """

    def collect(
        self,
        runtime_health: RuntimeHealth,
    ) -> ReadinessMetrics:
        """
        Collect immutable readiness metrics.
        """

        return ReadinessMetrics(
            health_status=runtime_health.status.value,
            health_score=runtime_health.score,
            finding_count=len(runtime_health.findings),
        )
