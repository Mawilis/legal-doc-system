"""
Wilsy Engineering Kernel
Engineering Assurance Framework - Readiness Engine

Application orchestrator for Engineering Kernel readiness evaluation.

Collaboration Note:
Epitome of engineering. Biblical worth billions. No child's place.
This file handles readiness indexing and metric collection with 
strict transactional integrity and robust domain model resolution.
"""

from __future__ import annotations

import os
import sys

# --- ABSOLUTE PATH BOOTSTRAP GUARANTEE ---
# Ensures the billion-dollar kernel can always resolve its root imports flawlessly.
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", "..", "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# Silencing Pylance missing import diagnostic; runtime bootstrap handles actual resolution.
from tools.eos.domain.models import (  # type: ignore
    EngineeringReadiness,
    ExecutionContext,
    ReadinessEngineContract,
    RuntimeHealth,
)

from .readiness_index import ReadinessIndex
from .readiness_metrics import ReadinessMetricsCollector


class ReadinessEngine(ReadinessEngineContract):
    """
    Read-only Engineering Kernel Readiness Engine

    Responsible only for Engineering Kernel readiness evaluation.
    """

    def __init__(self) -> None:
        """
        Initialize Readiness Engine dependencies.
        """
        self._collector = ReadinessMetricsCollector()
        self._index = ReadinessIndex()

    def evaluate(
        self,
        context: ExecutionContext,
        health: RuntimeHealth,
    ) -> EngineeringReadiness:
        """
        Evaluate Engineering Kernel readiness.

        Parameters:
        context (ExecutionContext): The execution context.
        health (RuntimeHealth): The runtime health metrics.

        Returns:
        EngineeringReadiness: The readiness evaluation result.
        """
        metrics = self._collector.collect(context)

        return self._index.evaluate(metrics)
