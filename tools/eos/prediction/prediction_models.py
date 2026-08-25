"""
===============================================================================
WILSY OS KERNEL — PREDICTION MODELS & DTOS
===============================================================================
[EPITOME]:
    Defines immutable prediction DTOs, severity levels, and risk metrics for 
    proactive predictive intelligence across Wilsy OS.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for unverified heuristics or data drift.

[BIBLICAL FOUNDATION]:
    Proverbs 22:3 — "A prudent man foresees evil and hides himself, but the simple pass on and are punished."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Prediction Models
===============================================================================
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PredictionSeverityEnum(str, Enum):
    """
    [ENUM SPECIFICATION]: Prediction Severity Levels
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PredictionResult(BaseModel):
    """
    [DTO SPECIFICATION]: Prediction Result Record
    Immutable DTO capturing predictive analytics, failure probabilities, 
    estimated time horizons, and actionable engineering rationales.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    prediction_id: str = Field(description="Unique prediction identifier.")
    predictor_name: str = Field(description="Engine or predictor that generated the forecast.")
    target_entity: str = Field(description="System component, module, or execution target being evaluated.")
    probability: float = Field(description="Probability score of predicted event occurring (0.0 to 1.0).")
    estimated_days_to_event: Optional[float] = Field(default=None, description="Estimated time horizon in days until predicted event occurs.")
    severity: PredictionSeverityEnum = Field(description="Severity classification of the prediction.")
    rationale: str = Field(description="Institutional engineering rationale backing the prediction.")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="ISO timestamp of prediction generation.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Detailed prediction telemetry and metrics.")
