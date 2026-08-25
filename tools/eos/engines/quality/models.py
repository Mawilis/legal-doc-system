"""
===============================================================================
WILSY OS QUALITY ENGINE: VALIDATION MODELS
===============================================================================
Epitome:
    The standard-bearer of Wilsy OS. These models define the criteria for 
    production readiness. It is the yardstick by which all engineering 
    excellence is measured.

Biblical Scale & Architecture:
    Quality is not an afterthought; it is a mandate. These models enforce 
    strict adherence to testing coverage, security compliance, and architectural 
    integrity. 

Collaboration & Maintenance:
    - QualityReport: The final verdict (Pass/Fail/Flag).
    - ValidationMetric: The specific KPI being measured (Security, Performance, etc).
===============================================================================
"""

from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass(frozen=True)
class QualityReport:
    """
    The final verification status for a given code artifact.
    """
    artifact_id: str
    status: str  # "PASSED", "FAILED", "WARNING"
    score: float
    violations: List[str]
    metadata: Dict[str, Any]

@dataclass(frozen=True)
class ValidationMetric:
    """
    Individual metrics contributing to the overall quality score.
    """
    name: str
    value: float
    threshold: float
    passed: bool
