"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Risk Engine - Immutable Risk Score & Confidence Envelope (FG154).
    Quantifies operational risk and confidence metrics for institutional executions.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready risk quantification wrapper. Zero child's place.
    Proverbs 22:3 - "The prudent sees danger and hides himself, but the simple go on and suffer for it."

Collaboration & Maintenance:
    - [Architecture]: Immutable risk scoring dataclass and confidence envelope.
    - [Compliance]: Strict value bounds validation (0.0 to 1.0) for score and confidence.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class RiskLevel(str, Enum):
    """Categorical classification of computed operational risk."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class RiskScore:
    """
    Immutable risk score and confidence rating for an institutional execution run.

    Attributes:
        score (float): Numerical risk metric from 0.0 (zero risk) to 1.0 (maximum risk).
        confidence (float): Statistical confidence metric from 0.0 to 1.0.
        risk_level (RiskLevel): Categorical severity classification.
        metadata (Dict[str, Any]): Additional scoring parameters and indicators.
    """

    score: float
    confidence: float
    risk_level: RiskLevel
    metadata: Dict[str, Any]

    def __post_init__(self) -> None:
        """Validates score and confidence boundaries upon instantiation."""
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"Risk score must be between 0.0 and 1.0, got {self.score}")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence score must be between 0.0 and 1.0, got {self.confidence}")

    # [FUNCTION EXPLANATION]: Factory constructor deriving risk level from score thresholds.
    @classmethod
    def calculate(cls, score: float, confidence: float, metadata: Dict[str, Any] | None = None) -> RiskScore:
        """
        Factory method to compute risk level dynamically from raw score values.
        """
        clamped_score = max(0.0, min(1.0, score))
        clamped_conf = max(0.0, min(1.0, confidence))

        if clamped_score < 0.25:
            level = RiskLevel.LOW
        elif clamped_score < 0.55:
            level = RiskLevel.MEDIUM
        elif clamped_score < 0.85:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.CRITICAL

        return cls(
            score=clamped_score,
            confidence=clamped_conf,
            risk_level=level,
            metadata=metadata or {},
        )
