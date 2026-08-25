"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Runtime integration and orchestration engine for Repository Intelligence Reporting.
    Acts as the primary execution facade for generating canonical intelligence payloads.

Biblical Scale & Architecture:
    This is a billion-dollar, production-ready coordination layer. No child's place.
    It isolates the outer runtime environment from the internal complexities of 
    the RepositoryReportBuilder, maintaining a strict facade pattern to ensure
    architectural purity and threat-safe generation.

Collaboration & Maintenance:
    - [Safety]: Strictly read-only coordination. Does not mutate domain state.
    - [Performance]: Leverages pre-instantiated builders to avoid overhead.
    - [Compliance]: Must be used as the sole entry point for publishing repository reports.

===============================================================================
"""

from __future__ import annotations

import logging

from ..domain.models import RepositoryAssessment, RepositoryIntelligenceReport
from .repository_report import RepositoryReportBuilder

# Initialize institutional logger
logger = logging.getLogger("wilsy.eos.repository.reporting.runtime_repository_reporting")


class RuntimeRepositoryReporting:
    """
    Industrial-grade Runtime Repository Reporting Coordinator.
    Responsible only for delegating and coordinating immutable 
    Repository Intelligence Report generation.
    """

    def __init__(self) -> None:
        """
        Initialize Runtime Repository Reporting dependencies.
        
        Collaboration Comment: 
        Pre-allocates the RepositoryReportBuilder to maintain high throughput 
        during consecutive publishing cycles.
        """
        self._report_builder = RepositoryReportBuilder()
        logger.debug("RuntimeRepositoryReporting orchestrated and builder instantiated.")

    def publish(
        self,
        assessment: RepositoryAssessment,
    ) -> RepositoryIntelligenceReport:
        """
        Generate the canonical Repository Intelligence Report.
        
        Collaboration Comment: 
        This orchestrates the final publishing workflow. Ensure the incoming 
        assessment is fully validated before it hits this pipeline.
        """
        # Architectural Guard: Prevent processing of empty payloads
        if not assessment:
            logger.error("Security Violation: Assessment payload is missing at the runtime layer.")
            raise ValueError(
                "Security Violation: Cannot publish a report from a null or invalid "
                "RepositoryAssessment."
            )

        logger.debug("Initiating runtime publication of Repository Intelligence Report.")
        
        try:
            # Delegate to the read-only builder
            report = self._report_builder.create(assessment=assessment)
            logger.info("Successfully published intelligence report via runtime orchestrator.")
            return report
            
        except Exception as err:
            logger.error(f"Critical failure during runtime report publication: {err}")
            raise RuntimeError(f"Failed to publish Repository Intelligence Report: {err}") from err

