"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engineering Assurance Framework - Health Engine.
    Application orchestrator for Engineering Kernel health evaluation.
    Consumes the immutable ExecutionContext directly.

Biblical Scale & Architecture:
    Production-ready enterprise health engine. Enforces strict contract adherence,
    exposing explicit naming and versioning telemetry. Zero child's play.

Collaboration & Maintenance:
    - [Dependency Injection]: Consumes unified ExecutionContext.
    - [Contract Compliance]: Implements HealthEngineContract & EngineContract.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from ..domain.contracts import HealthEngineContract
from ..domain.models import RuntimeHealth
from ...runtime.context import ExecutionContext

from .health_index import HealthIndex
from .health_metrics import HealthMetricsCollector


class HealthEngine(HealthEngineContract):
    """
    Read-only Engineering Kernel Health Engine.

    Responsible only for orchestrating runtime health evaluation utilizing
    the immutable ExecutionContext matrix.
    """

    @property
    def name(self) -> str:
        """The canonical string identifier of the engine subsystem."""
        return "WilsyOS.Assurance.HealthEngine"

    @property
    def version(self) -> str:
        """The semantic version release tag of the engine implementation."""
        return "1.0.0"

    def __init__(self) -> None:
        """
        Initialize Health Engine dependencies.
        """
        self._collector = HealthMetricsCollector()
        self._index = HealthIndex()

    def evaluate(
        self,
        context: ExecutionContext,
    ) -> RuntimeHealth:
        """
        Evaluate Engineering Kernel runtime health using the shared execution context.

        Args:
            context (ExecutionContext): The unified, immutable runtime context.

        Returns:
            RuntimeHealth: The institutional runtime health assessment.
        """
        metrics = self._collector.collect(context)

        return self._index.evaluate(metrics)
