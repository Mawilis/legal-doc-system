"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Risk Report - Institutional Risk Audit & Recovery Serialization (FG154).
    Aggregates Risk Scores and Failure Predictions into a cryptographically 
    identifiable, immutable compliance document. Automatically generates 
    recovery strategies based on failure thresholds.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready risk reporting and recovery engine. Zero child's place.
    Luke 14:28 - "For which of you, desiring to build a tower, does not first sit down and count the cost, whether he has enough to complete it?"

Collaboration & Maintenance:
    - [Architecture]: Immutable data structure aggregating risk telemetry.
    - [Compliance]: Generates audit-ready JSON serializable reports with embedded recovery strategies.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from tools.eos.risk.risk_prediction import FailurePrediction
from tools.eos.risk.risk_score import RiskScore, RiskLevel


@dataclass(frozen=True)
class RiskReport:
    """
    Immutable risk assessment report combining risk scores, predictions, and recovery strategies.
    """
    report_id: str
    timestamp: str
    schema_version: str
    module: str
    status: str
    risk_score_data: Dict[str, Any]
    failure_prediction_data: Dict[str, Any]
    recovery_strategy: List[str]

    # [FUNCTION EXPLANATION]: Factory constructor to generate a finalized risk report from raw components.
    @classmethod
    def generate_report(
        cls, 
        risk_score: RiskScore, 
        failure_prediction: FailurePrediction, 
        module_context: str = "Wilsy OS Risk Governance"
    ) -> RiskReport:
        """
        Synthesizes a finalized RiskReport from computed risk components, deriving actionable
        recovery strategies based on the identified severity.

        Args:
            risk_score (RiskScore): Computed risk score object.
            failure_prediction (FailurePrediction): Computed failure prediction object.
            module_context (str): Identifier for the executing module.

        Returns:
            RiskReport: Finalized immutable risk report.
        """
        report_id = f"risk-rep-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Formulate dynamic recovery strategy based on impact severity
        recovery_strategy: List[str] = []
        if failure_prediction.impact_severity == "CATASTROPHIC":
            status = "CRITICAL_DANGER"
            recovery_strategy.extend([
                "IMMEDIATE HALT: Abort execution pipeline instantly.",
                "TRIGGER: Initiate automated rollback to last known good state.",
                "ESCALATE: Require Human-in-the-Loop (HITL) cryptographic authorization to proceed."
            ])
        elif failure_prediction.impact_severity == "HIGH":
            status = "WARNING_ELEVATED_RISK"
            recovery_strategy.extend([
                "PAUSE: Suspend execution and verify external dependencies.",
                "RETRY: Attempt exponential backoff sequence (max 3 retries).",
                "AUDIT: Log full payload state to Execution Journal for offline review."
            ])
        else:
            status = "SECURE"
            recovery_strategy.append("PROCEED: Operational parameters within safe tolerances. No recovery action needed.")

        return cls(
            report_id=report_id,
            timestamp=timestamp,
            schema_version="1.0.0",
            module=module_context,
            status=status,
            risk_score_data={
                "score": risk_score.score,
                "confidence": risk_score.confidence,
                "level": risk_score.risk_level.value
            },
            failure_prediction_data={
                "probability": failure_prediction.failure_probability,
                "mode": failure_prediction.predicted_failure_mode,
                "impact": failure_prediction.impact_severity,
                "factors": failure_prediction.contributing_factors
            },
            recovery_strategy=recovery_strategy
        )

    # [FUNCTION EXPLANATION]: Serializes the report payload into a canonical JSON dictionary.
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the immutable dataclass into a dictionary suitable for JSON serialization and audit storage.
        """
        return asdict(self)

    # [FUNCTION EXPLANATION]: Serializes the report payload into a formatted JSON string.
    def to_json(self) -> str:
        """
        Converts the report into a formatted JSON string.
        """
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)
