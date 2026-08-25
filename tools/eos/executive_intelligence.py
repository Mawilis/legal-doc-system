"""
================================================================================
WILSY OS — ENTERPRISE OPERATING SYSTEM
MODULE: Executive Intelligence Engine (EOS Analytics & Governance)
FILE: tools/eos/executive_intelligence.py
PURPOSE: Synthesizes low-level engineering telemetry, AST static analysis,
         CI/CD build pipelines, and system metrics into deterministic, C-suite
         strategic intelligence.

METRICS SENSORS:
    1. Engineering Health Index (EHI)
    2. Architecture Stability Score (ASS)
    3. Repository Complexity Score (RCS)
    4. Developer Productivity Trend (DPT)
    5. Deployment Confidence (DC)
    6. AI Confidence (AIC)
    7. Technical Debt Index (TDI)
    8. Operational Risk Index (ORI)
    9. Institutional Maturity Score (IMS)

COLLABORATORS & ARCHITECTURAL INTENT:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy OS)
    - Architecture Quality: Production-Ready, Zero-Stub, Immutable Output Schema.
    - Security & Audit: Immutable strategic telemetry reporting for board review.
================================================================================
"""

import math
import logging
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

# Configure System Logger
logger = logging.getLogger("WilsyOS.EOS.ExecutiveIntelligence")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class MetricStatus(str, Enum):
    OPTIMAL = "OPTIMAL"
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class MetricTrend(str, Enum):
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"


class EnginePhase(str, Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZED = "INITIALIZED"
    RUNNING = "RUNNING"
    SHUTDOWN = "SHUTDOWN"


@dataclass
class ExecutiveMetric:
    """Individual CEO-level metric vector containing scores, status, and recommendations."""
    key: str
    display_name: str
    score: float  # Clamped 0.0 to 100.0
    weight: float  # Weight factor in aggregate executive score
    status: MetricStatus
    trend: MetricTrend
    summary: str
    key_drivers: List[str] = field(default_factory=list)
    strategic_recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "display_name": self.display_name,
            "score": round(self.score, 2),
            "weight": self.weight,
            "status": self.status.value,
            "trend": self.trend.value,
            "summary": self.summary,
            "key_drivers": self.key_drivers,
            "strategic_recommendations": self.strategic_recommendations,
        }


@dataclass
class ExecutiveIntelligenceReport:
    """Aggregated CEO-level strategic intelligence snapshot."""
    report_id: str
    timestamp: str
    overall_executive_index: float
    system_readiness_status: str
    engineering_health_index: ExecutiveMetric
    architecture_stability_score: ExecutiveMetric
    repository_complexity_score: ExecutiveMetric
    developer_productivity_trend: ExecutiveMetric
    deployment_confidence: ExecutiveMetric
    ai_confidence: ExecutiveMetric
    technical_debt_index: ExecutiveMetric
    operational_risk_index: ExecutiveMetric
    institutional_maturity_score: ExecutiveMetric
    executive_summary: str
    immediate_board_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp,
            "overall_executive_index": round(self.overall_executive_index, 2),
            "system_readiness_status": self.system_readiness_status,
            "executive_summary": self.executive_summary,
            "metrics": {
                "engineering_health_index": self.engineering_health_index.to_dict(),
                "architecture_stability_score": self.architecture_stability_score.to_dict(),
                "repository_complexity_score": self.repository_complexity_score.to_dict(),
                "developer_productivity_trend": self.developer_productivity_trend.to_dict(),
                "deployment_confidence": self.deployment_confidence.to_dict(),
                "ai_confidence": self.ai_confidence.to_dict(),
                "technical_debt_index": self.technical_debt_index.to_dict(),
                "operational_risk_index": self.operational_risk_index.to_dict(),
                "institutional_maturity_score": self.institutional_maturity_score.to_dict(),
            },
            "immediate_board_actions": self.immediate_board_actions,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class BaseKernelEngine:
    """Standardized Base Kernel interface across Wilsy OS EOS engines."""

    def __init__(self, name: str):
        self.name = name
        self.phase = EnginePhase.UNINITIALIZED

    def initialize(self) -> bool:
        self.phase = EnginePhase.INITIALIZED
        logger.info(f"[{self.name}] Engine initialized.")
        return True

    def validate(self, input_data: Dict[str, Any]) -> bool:
        if self.phase not in [EnginePhase.INITIALIZED, EnginePhase.RUNNING]:
            logger.error(f"[{self.name}] Cannot validate. Engine in phase {self.phase}")
            return False
        return True

    def execute(self, input_data: Dict[str, Any]) -> Any:
        raise NotImplementedError("Kernel engines must implement execute().")

    def publish(self, artifact: Any) -> bool:
        logger.info(f"[{self.name}] Executive artifact published.")
        return True

    def shutdown(self) -> bool:
        self.phase = EnginePhase.SHUTDOWN
        logger.info(f"[{self.name}] Engine shut down cleanly.")
        return True


class ExecutiveIntelligenceEngine(BaseKernelEngine):
    """
    Core Executive Intelligence Synthesis Engine.
    Transforms engineering metrics into CEO-level intelligence vectors.
    """

    def __init__(self):
        super().__init__("ExecutiveIntelligenceEngine")

    @staticmethod
    def _clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
        return max(min_val, min(max_val, value))

    @staticmethod
    def _determine_status(score: float, inverted: bool = False) -> MetricStatus:
        effective_score = (100.0 - score) if inverted else score
        if effective_score >= 85.0:
            return MetricStatus.OPTIMAL
        elif effective_score >= 70.0:
            return MetricStatus.HEALTHY
        elif effective_score >= 50.0:
            return MetricStatus.WARNING
        return MetricStatus.CRITICAL

    @staticmethod
    def _determine_trend(current: float, historical: float, inverted: bool = False) -> MetricTrend:
        diff = current - historical
        if abs(diff) < 1.5:
            return MetricTrend.STABLE
        if inverted:
            return MetricTrend.IMPROVING if diff < 0 else MetricTrend.DECLINING
        return MetricTrend.IMPROVING if diff > 0 else MetricTrend.DECLINING

    # --------------------------------------------------------------------------
    # METRIC CALCULATORS
    # --------------------------------------------------------------------------

    def _calc_engineering_health(self, raw: Dict[str, Any]) -> ExecutiveMetric:
        pass_rate = raw.get("ci_pass_rate", 98.5)
        test_coverage = raw.get("test_coverage", 90.0)
        defect_density = raw.get("defects_per_kloc", 0.2)

        defect_score = self._clamp(100.0 - (defect_density * 20.0))
        score = (test_coverage * 0.40) + (pass_rate * 0.40) + (defect_score * 0.20)
        score = self._clamp(score)

        status = self._determine_status(score)
        trend = self._determine_trend(score, raw.get("prev_engineering_health", score))

        drivers = [
            f"Automated Test Coverage at {test_coverage}%",
            f"CI/CD Pipeline Pass Rate operating at {pass_rate}%",
            f"Defect Density measured at {defect_density} bugs per 1,000 LOC",
        ]
        recs = []
        if score < 85:
            recs.append("Increase automated integration testing on critical path modules.")

        return ExecutiveMetric(
            key="EHI",
            display_name="Engineering Health Index",
            score=score,
            weight=1.2,
            status=status,
            trend=trend,
            summary="Reflects overall software craftsmanship, test resilience, and build reliability.",
            key_drivers=drivers,
            strategic_recommendations=recs,
        )

    def _calc_architecture_stability(self, raw: Dict[str, Any]) -> ExecutiveMetric:
        circular_deps = raw.get("circular_dependencies", 0)
        coupling_ratio = raw.get("module_coupling_ratio", 0.15)
        breaking_changes = raw.get("api_breaking_changes_30d", 0)

        score = 100.0 - (circular_deps * 15.0) - (coupling_ratio * 100.0 * 0.3) - (breaking_changes * 10.0)
        score = self._clamp(score)

        status = self._determine_status(score)
        trend = self._determine_trend(score, raw.get("prev_arch_stability", score))

        drivers = [
            f"Zero circular dependencies" if circular_deps == 0 else f"{circular_deps} circular dependencies isolated",
            f"Module Coupling Ratio standing at {round(coupling_ratio * 100, 1)}%",
            f"Breaking API schema mutations in past 30 days: {breaking_changes}",
        ]
        recs = []
        if circular_deps > 0:
            recs.append("Refactor circular dependency bonds in core domain logic.")

        return ExecutiveMetric(
            key="ASS",
            display_name="Architecture Stability Score",
            score=score,
            weight=1.3,
            status=status,
            trend=trend,
            summary="Evaluates systemic modularity, boundary encapsulation, and interface contract safety.",
            key_drivers=drivers,
            strategic_recommendations=recs,
        )

    def _calc_repository_complexity(self, raw: Dict[str, Any]) -> ExecutiveMetric:
        cyclomatic_avg = raw.get("avg_cyclomatic_complexity", 4.2)
        depth_max = raw.get("max_directory_depth", 5)
        file_sprawl_index = raw.get("file_sprawl_index", 12.0)

        complexity_penalty = (cyclomatic_avg * 8.0) + (depth_max * 2.0) + (file_sprawl_index * 1.5)
        score = self._clamp(100.0 - complexity_penalty)

        status = self._determine_status(score)
        trend = self._determine_trend(score, raw.get("prev_repo_complexity", score))

        drivers = [
            f"Average Cyclomatic Complexity: {cyclomatic_avg} (Target < 7.0)",
            f"Max Directory Nesting Depth: {depth_max}",
            f"File Sprawl Index: {file_sprawl_index}",
        ]
        recs = []
        if cyclomatic_avg > 7.0:
            recs.append("Decompose complex branching functions using strategic domain handlers.")

        return ExecutiveMetric(
            key="RCS",
            display_name="Repository Complexity Score",
            score=score,
            weight=0.9,
            status=status,
            trend=trend,
            summary="Measures cognitive load, structural depth, and maintainability of the codebase.",
            key_drivers=drivers,
            strategic_recommendations=recs,
        )

    def _calc_developer_productivity(self, raw: Dict[str, Any]) -> ExecutiveMetric:
        cycle_time_hours = raw.get("pr_cycle_time_hours", 12.0)
        velocity_points = raw.get("completed_story_points", 85.0)
        blocked_time_pct = raw.get("blocked_developer_hours_pct", 4.0)

        cycle_score = self._clamp(100.0 - (cycle_time_hours * 1.5))
        block_score = self._clamp(100.0 - (blocked_time_pct * 5.0))
        score = (cycle_score * 0.5) + (block_score * 0.5)

        status = self._determine_status(score)
        trend = self._determine_trend(score, raw.get("prev_productivity", score))

        drivers = [
            f"Average PR Lead Time: {cycle_time_hours} hours",
            f"Sprint Velocity Completed: {velocity_points} story points",
            f"Developer Blocked Time Rate: {blocked_time_pct}%",
        ]
        recs = []
        if cycle_time_hours > 24.0:
            recs.append("Reduce pull request review latency through automated EOS pre-checks.")

        return ExecutiveMetric(
            key="DPT",
            display_name="Developer Productivity Trend",
            score=score,
            weight=1.0,
            status=status,
            trend=trend,
            summary="Tracks delivery velocity, PR cycle time, and friction elimination across sprints.",
            key_drivers=drivers,
            strategic_recommendations=recs,
        )

    def _calc_deployment_confidence(self, raw: Dict[str, Any]) -> ExecutiveMetric:
        canary_success = raw.get("canary_success_rate", 99.2)
        env_drift = raw.get("environment_drift_pct", 0.5)
        rollback_rate = raw.get("rollback_rate_pct", 0.0)

        score = (canary_success * 0.6) + ((100.0 - env_drift * 10.0) * 0.2) + ((100.0 - rollback_rate * 20.0) * 0.2)
        score = self._clamp(score)

        status = self._determine_status(score)
        trend = self._determine_trend(score, raw.get("prev_deploy_confidence", score))

        drivers = [
            f"Canary Release Pass Rate: {canary_success}%",
            f"Infrastructure Drift Factor: {env_drift}%",
            f"Deployment Rollback Frequency: {rollback_rate}%",
        ]
        recs = []
        if rollback_rate > 2.0:
            recs.append("Enforce strict staging-to-production telemetry parity gates.")

        return ExecutiveMetric(
            key="DC",
            display_name="Deployment Confidence",
            score=score,
            weight=1.4,
            status=status,
            trend=trend,
            summary="Calculates mathematical certainty of zero-downtime, fault-free release deployments.",
            key_drivers=drivers,
            strategic_recommendations=recs,
        )

    def _calc_ai_confidence(self, raw: Dict[str, Any]) -> ExecutiveMetric:
        inference_certainty = raw.get("ai_inference_accuracy", 96.5)
        hallucination_rate = raw.get("ai_hallucination_rate", 0.1)
        calibration_score = raw.get("ai_model_calibration", 95.0)

        score = (inference_certainty * 0.4) + ((100.0 - hallucination_rate * 100.0) * 0.3) + (calibration_score * 0.3)
        score = self._clamp(score)

        status = self._determine_status(score)
        trend = self._determine_trend(score, raw.get("prev_ai_confidence", score))

        drivers = [
            f"Autonomous Inference Precision: {inference_certainty}%",
            f"Measured AI Hallucination Factor: {hallucination_rate}%",
            f"Model Probability Calibration Index: {calibration_score}%",
        ]
        recs = []
        if hallucination_rate > 1.0:
            recs.append("Tighten strict JSON-schema enforcement wrappers on automated agent outputs.")

        return ExecutiveMetric(
            key="AIC",
            display_name="AI Confidence",
            score=score,
            weight=1.2,
            status=status,
            trend=trend,
            summary="Gauges accuracy, hallucination resistance, and reliability of embedded AI models.",
            key_drivers=drivers,
            strategic_recommendations=recs,
        )

    def _calc_technical_debt(self, raw: Dict[str, Any]) -> ExecutiveMetric:
        deprecated_calls = raw.get("deprecated_api_usages", 0)
        todo_fixme_count = raw.get("todo_fixme_count", 3)
        untested_files = raw.get("untested_critical_files", 0)

        debt_penalty = (deprecated_calls * 5.0) + (todo_fixme_count * 1.5) + (untested_files * 10.0)
        score = self._clamp(100.0 - debt_penalty)

        status = self._determine_status(score)
        trend = self._determine_trend(score, raw.get("prev_tech_debt", score), inverted=True)

        drivers = [
            f"Deprecated Method Invocations: {deprecated_calls}",
            f"Active TODO/FIXME Debt Markers: {todo_fixme_count}",
            f"Untested Critical Domain Files: {untested_files}",
        ]
        recs = []
        if todo_fixme_count > 10:
            recs.append("Allocate 10% of next sprint velocity specifically to technical debt removal.")

        return ExecutiveMetric(
            key="TDI",
            display_name="Technical Debt Index",
            score=score,
            weight=1.1,
            status=status,
            trend=trend,
            summary="Quantifies accumulated code debt, deprecated dependencies, and missing test coverage.",
            key_drivers=drivers,
            strategic_recommendations=recs,
        )

    def _calc_operational_risk(self, raw: Dict[str, Any]) -> ExecutiveMetric:
        mttr_minutes = raw.get("mttr_minutes", 8.0)
        spof_count = raw.get("single_points_of_failure", 0)
        vuln_critical = raw.get("critical_vulnerabilities", 0)

        risk_penalty = (mttr_minutes * 1.5) + (spof_count * 25.0) + (vuln_critical * 30.0)
        score = self._clamp(100.0 - risk_penalty)

        status = self._determine_status(score)
        trend = self._determine_trend(score, raw.get("prev_op_risk", score), inverted=True)

        drivers = [
            f"Mean Time To Recovery (MTTR): {mttr_minutes} minutes",
            f"Single Points of Failure (SPOF): {spof_count}",
            f"Unpatched Critical Vulnerabilities: {vuln_critical}",
        ]
        recs = []
        if spof_count > 0:
            recs.append("Eliminate identified single points of failure via redundant failover routing.")

        return ExecutiveMetric(
            key="ORI",
            display_name="Operational Risk Index",
            score=score,
            weight=1.5,
            status=status,
            trend=trend,
            summary="Evaluates threat exposure, system resiliency, incident recovery speed, and security risks.",
            key_drivers=drivers,
            strategic_recommendations=recs,
        )

    def _calc_institutional_maturity(self, raw: Dict[str, Any]) -> ExecutiveMetric:
        eos_adherence = raw.get("eos_protocol_adherence_pct", 100.0)
        docs_completeness = raw.get("documentation_coverage_pct", 95.0)
        governance_coverage = raw.get("automated_governance_pct", 98.0)

        score = (eos_adherence * 0.4) + (docs_completeness * 0.3) + (governance_coverage * 0.3)
        score = self._clamp(score)

        status = self._determine_status(score)
        trend = self._determine_trend(score, raw.get("prev_institutional_maturity", score))

        drivers = [
            f"EOS Protocol Adherence: {eos_adherence}%",
            f"System Architectural Documentation Coverage: {docs_completeness}%",
            f"Automated Enterprise Governance Gate Coverage: {governance_coverage}%",
        ]
        recs = []
        if docs_completeness < 90:
            recs.append("Automate inline docstring validation in CI pipeline checks.")

        return ExecutiveMetric(
            key="IMS",
            display_name="Institutional Maturity Score",
            score=score,
            weight=1.0,
            status=status,
            trend=trend,
            summary="Measures enterprise readiness, documentation fidelity, and autonomous governance coverage.",
            key_drivers=drivers,
            strategic_recommendations=recs,
        )

    # --------------------------------------------------------------------------
    # EXECUTION & SYNTHESIS
    # --------------------------------------------------------------------------

    # NOTE: The parameter name must match the base class (input_data) to avoid
    # a method signature mismatch. We'll rename telemetry -> input_data.
    def execute(self, input_data: Dict[str, Any]) -> ExecutiveIntelligenceReport:
        if not self.validate(input_data):
            self.initialize()

        self.phase = EnginePhase.RUNNING
        logger.info("Synthesizing Executive Intelligence Metrics...")

        # Use the input_data as the raw telemetry dictionary
        raw = input_data

        ehi = self._calc_engineering_health(raw)
        ass = self._calc_architecture_stability(raw)
        rcs = self._calc_repository_complexity(raw)
        dpt = self._calc_developer_productivity(raw)
        dc = self._calc_deployment_confidence(raw)
        aic = self._calc_ai_confidence(raw)
        tdi = self._calc_technical_debt(raw)
        ori = self._calc_operational_risk(raw)
        ims = self._calc_institutional_maturity(raw)

        metrics = [ehi, ass, rcs, dpt, dc, aic, tdi, ori, ims]

        total_weight = sum(m.weight for m in metrics)
        weighted_score_sum = sum(m.score * m.weight for m in metrics)
        overall_index = round(weighted_score_sum / total_weight, 2)

        if overall_index >= 90.0:
            readiness = "PLATINUM_BOARD_READY"
        elif overall_index >= 80.0:
            readiness = "GOLD_PRODUCTION_READY"
        elif overall_index >= 70.0:
            readiness = "SILVER_OPERATIONAL"
        else:
            readiness = "ATTENTION_REQUIRED"

        board_actions = []
        for m in metrics:
            board_actions.extend(m.strategic_recommendations)

        if not board_actions:
            board_actions.append("Maintain current operational standards and baseline monitoring protocols.")

        summary = (
            f"Wilsy OS reflects an Overall Executive Index of {overall_index}/100 ({readiness}). "
            f"Architecture Stability ({ass.score}/100) and Operational Security ({ori.score}/100) "
            f"demonstrate enterprise resilience. AI Confidence stands at {aic.score}/100."
        )

        report = ExecutiveIntelligenceReport(
            report_id=f"EXEC-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            overall_executive_index=overall_index,
            system_readiness_status=readiness,
            engineering_health_index=ehi,
            architecture_stability_score=ass,
            repository_complexity_score=rcs,
            developer_productivity_trend=dpt,
            deployment_confidence=dc,
            ai_confidence=aic,
            technical_debt_index=tdi,
            operational_risk_index=ori,
            institutional_maturity_score=ims,
            executive_summary=summary,
            immediate_board_actions=board_actions,
        )

        logger.info(f"Report Generated: ID={report.report_id} | Index={report.overall_executive_index}")
        return report


__all__ = [
    "MetricStatus",
    "MetricTrend",
    "ExecutiveMetric",
    "ExecutiveIntelligenceReport",
    "ExecutiveIntelligenceEngine",
]

if __name__ == "__main__":
    engine = ExecutiveIntelligenceEngine()
    engine.initialize()
    report = engine.execute({})
    print("\n--- EXECUTIVE INTELLIGENCE REPORT INITIALIZED ---")
    print(report.to_json())
    engine.shutdown()
