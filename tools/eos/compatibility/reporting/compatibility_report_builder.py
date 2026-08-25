"""
===============================================================================
WILSY OS — COMPATIBILITY REPORT BUILDER (FG208)
===============================================================================
Epitome:
    Builder service responsible for transforming compatibility evaluation results 
    into cryptographically signed CompatibilityReportArtifact payloads suitable 
    for immediate publication onto the platform's Artifact Bus.

Biblical Worth Billions:
    "Let all things be done decently and in order."
    — 1 Corinthians 14:40

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/compatibility/reporting/compatibility_report_builder.py
===============================================================================
"""

from __future__ import annotations

import logging
from typing import Dict, Any

from tools.eos.compatibility.domain.compatibility_result import CompatibilityEvaluationResult
from tools.eos.compatibility.reporting.compatibility_artifact import CompatibilityReportArtifact

logger = logging.getLogger("WilsyOS.Compatibility.Reporting.ReportBuilder")


class CompatibilityReportBuilder:
    """
    Builder service for generating Artifact Bus compliant report payloads.
    """

    @staticmethod
    def build_report_artifact(
        result: CompatibilityEvaluationResult
    ) -> CompatibilityReportArtifact:
        """
        Transforms a CompatibilityEvaluationResult into a signed CompatibilityReportArtifact.
        """
        decision = result.decision

        artifact = CompatibilityReportArtifact.create(
            execution_id=decision.execution_id,
            engine_id=decision.engine_id,
            kernel_version=decision.kernel_version,
            engine_version=decision.engine_version,
            decision=decision.status.value,
            adapter=decision.adapter_selected,
            missing_capabilities=decision.missing_capabilities
        )

        logger.debug(
            "Built compatibility report artifact for execution '%s' [SHA256: %s]",
            artifact.execution_id,
            artifact.sha256
        )
        return artifact
