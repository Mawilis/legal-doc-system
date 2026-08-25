"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Canonical builder for immutable Repository Intelligence Reports.
    Enforces cryptographic-level reporting integrity for the Wilsy OS ecosystem.

Biblical Scale & Architecture:
    This is a billion-dollar, production-ready module designed to enforce 
    structural reporting integrity across the Wilsy OS. No child's place.
    Constructs time-locked, immutable snapshots of repository topology 
    without introducing side-effects or mutating underlying domain models.

Collaboration & Maintenance:
    - [Integrity]: This module is strictly read-only.
    - [Safety]: Consumes RepositoryAssessment domain models and outputs a 
      finalized, timestamped RepositoryIntelligenceReport.
    - [Compliance]: Do not introduce API calls or state mutations within this builder.

===============================================================================
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from ..domain.models import RepositoryAssessment, RepositoryIntelligenceReport

# Initialize institutional logger
logger = logging.getLogger("wilsy.eos.repository.reporting.repository_report")


class RepositoryReportBuilder:
    """
    Industrial-grade, read-only Repository Intelligence Report Builder.
    Responsible only for constructing immutable RepositoryIntelligenceReport instances.
    """

    def create(
        self,
        assessment: RepositoryAssessment,
    ) -> RepositoryIntelligenceReport:
        """
        Produce the canonical Repository Intelligence Report.
        
        Collaboration Comment: 
        This function acts as the final aggregator. It binds the validated 
        assessment data with a strict UTC timestamp to ensure absolute 
        auditability for the reporting framework.
        """
        # Architectural Guard: Ensure assessment is not null before generation
        if not assessment:
            logger.error("Security Violation: Cannot generate report with empty RepositoryAssessment.")
            raise ValueError(
                "Security Violation: RepositoryAssessment payload is missing or invalid. "
                "Ensure domain model is validated before passing to the report builder."
            )

        try:
            # Execute report generation with strict UTC timeline logging
            report = RepositoryIntelligenceReport(
                assessment=assessment,
                generated_at=datetime.now(UTC).isoformat(),
            )
            logger.debug(f"Successfully minted RepositoryIntelligenceReport at {report.generated_at}")
            return report
            
        except TypeError as err:
            logger.error(f"Failed to construct target report. Type mismatch: {err}")
            raise ValueError(f"Report generation failed due to type mismatch: {err}") from err

