"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Institutional Intelligence - Master Advisor (FG160).
    Unifies Architecture Reasoning, Performance Optimization, and Automated Decision
    Synthesis into a single executive institutional briefing.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready institutional advisor. Zero child's place.
    Proverbs 11:14 - "Where there is no guidance, a people falls, but in an abundance of counselors there is safety."

Collaboration & Maintenance:
    - [Architecture]: Master executive intelligence coordinator and advisory synthesizer.
    - [Compliance]: Guarantees proactive, sovereign institutional self-governance.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from tools.eos.intelligence.architecture_reasoner import ArchitectureReasoner
from tools.eos.intelligence.decision_engine import DecisionEngine
from tools.eos.intelligence.optimization_engine import OptimizationEngine
from tools.eos.observability.telemetry import TelemetryCollector
from tools.eos.twin.digital_twin import DigitalTwin

logger = logging.getLogger("WilsyOS.InstitutionalAdvisor")


class InstitutionalAdvisor:
    """
    Master coordinator that orchestrates structural reasoning, performance optimization,
    and decision synthesis into a unified executive advisory briefing.
    """

    def __init__(
        self,
        digital_twin: DigitalTwin,
        telemetry_collector: TelemetryCollector,
    ) -> None:
        """
        Initializes the advisor with required kernel subsystems.

        Args:
            digital_twin (DigitalTwin): In-memory repository authority.
            telemetry_collector (TelemetryCollector): Active metrics collector.
        """
        self.architecture_reasoner = ArchitectureReasoner(digital_twin)
        self.optimization_engine = OptimizationEngine(telemetry_collector)
        self.decision_engine = DecisionEngine()

    # [FUNCTION EXPLANATION]: Generates a comprehensive executive intelligence briefing across all subsystems.
    def generate_advisory_report(self) -> Dict[str, Any]:
        """
        Synthesizes architectural audits and performance metrics into a complete executive briefing.

        Returns:
            Dict[str, Any]: Comprehensive institutional advisory report.
        """
        logger.info("Generating master institutional advisory report...")

        arch_report = self.architecture_reasoner.evaluate_architecture()
        opt_report = self.optimization_engine.analyze_performance()
        decision_report = self.decision_engine.synthesize_decisions(arch_report, opt_report)

        return {
            "briefing_title": "WilsyOS Executive Institutional Intelligence Briefing",
            "status": decision_report.get("institutional_status", "OPERATIONAL"),
            "architecture_audit": arch_report,
            "performance_optimization": opt_report,
            "institutional_decisions": decision_report,
        }

    def generate_advisory_json(self) -> str:
        """Exports the executive briefing as a pretty-printed JSON string."""
        report = self.generate_advisory_report()
        return json.dumps(report, indent=2, sort_keys=True)
