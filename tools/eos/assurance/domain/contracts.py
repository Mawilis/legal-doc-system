"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engineering Assurance Framework - Assurance Domain Contracts.
    Institutional contracts implemented by the Engineering Assurance Framework,
    enforcing immutable ExecutionContext injection across all evaluation pipelines.

Biblical Scale & Architecture:
    This is a billion-dollar production-ready architecture. No child's place.
    Every engine receives the unified ExecutionContext directly, eliminating
    redundant discovery loops, Graph DB reconnections, and Sentinel polls.

Collaboration & Maintenance:
    - [Dependency Injection]: Strict passing of ExecutionContext matrix.
    - [Immutability]: Contract signatures guarantee frozen state processing.
    - [Extensibility]: Unified base EngineContract tracking name and version telemetry.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ...runtime.context import ExecutionContext
from .models import (
    EngineeringAssurance,
    EngineeringAssuranceReport,
    EngineeringReadiness,
    RuntimeHealth,
)


class EngineContract(ABC):
    """
    Base institutional contract for all Wilsy OS engine implementations.
    Guarantees runtime identification and version compliance tracking.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The canonical string identifier of the engine subsystem."""
        raise NotImplementedError

    @property
    @abstractmethod
    def version(self) -> str:
        """The semantic version release tag of the engine implementation."""
        raise NotImplementedError


class HealthEngineContract(EngineContract):
    """
    Institutional contract implemented by every Health Engine.
    """

    @abstractmethod
    def evaluate(
        self,
        context: ExecutionContext,
    ) -> RuntimeHealth:
        """
        Produce an immutable runtime health assessment using the shared execution context.
        """
        raise NotImplementedError


class ReadinessEngineContract(EngineContract):
    """
    Institutional contract implemented by every Readiness Engine.
    """

    @abstractmethod
    def evaluate(
        self,
        context: ExecutionContext,
        health: RuntimeHealth,
    ) -> EngineeringReadiness:
        """
        Produce an immutable readiness assessment using shared context and health metrics.
        """
        raise NotImplementedError


class AssuranceEngineContract(EngineContract):
    """
    Institutional contract implemented by every Assurance Engine.
    """

    @abstractmethod
    def evaluate(
        self,
        context: ExecutionContext,
        health: RuntimeHealth,
        readiness: EngineeringReadiness,
    ) -> EngineeringAssurance:
        """
        Produce an immutable institutional assurance assessment.
        """
        raise NotImplementedError


class AssuranceReportContract(EngineContract):
    """
    Institutional contract implemented by every Assurance Report producer.
    """

    @abstractmethod
    def create(
        self,
        context: ExecutionContext,
        health: RuntimeHealth,
        readiness: EngineeringReadiness,
        assurance: EngineeringAssurance,
    ) -> EngineeringAssuranceReport:
        """
        Produce the canonical Engineering Assurance Report.
        """
        raise NotImplementedError
