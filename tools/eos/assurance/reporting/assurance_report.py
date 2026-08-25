"""
Wilsy Engineering Kernel

Engineering Assurance Reporting

Assurance Report

Canonical builder for immutable Engineering Assurance Reports.
"""

from __future__ import annotations

from datetime import UTC
from datetime import datetime

from ..domain.contracts import AssuranceReportContract
from ..domain.models import EngineeringAssurance
from ..domain.models import EngineeringAssuranceReport
from ..domain.models import EngineeringReadiness
from ..domain.models import RuntimeHealth


class AssuranceReportBuilder(AssuranceReportContract):
    """
    Read-only Engineering Assurance Report Builder.

    Responsible only for constructing immutable
    EngineeringAssuranceReport instances.
    """

    def create(
        self,
        health: RuntimeHealth,
        readiness: EngineeringReadiness,
        assurance: EngineeringAssurance,
    ) -> EngineeringAssuranceReport:
        """
        Produce the canonical Engineering Assurance Report.
        """

        return EngineeringAssuranceReport(
            health=health,
            readiness=readiness,
            assurance=assurance,
            generated_at=datetime.now(
                UTC,
            ).isoformat(),
        )
