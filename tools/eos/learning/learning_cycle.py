from __future__ import annotations

"""
===============================================================================
WILSY OS LEARNING — LEARNING CYCLE STATE MACHINE & PHASES
===============================================================================
Epitome:
    Defines the four canonical phases of institutional learning: Observation,
    Replay, Inference, and Evolution. Transforms raw execution metrics into
    predictive organizational knowledge.

Biblical Worth Billions:
    "Remember the days of old, consider the years of many generations: ask thy father,
    and he will shew thee; thy elders, and they will tell thee." — Deuteronomy 32:7
    Institutional memory ensures the system never repeats past execution failures and
    continuously accelerates operational performance.

Collaboration & Ownership:
    - Founder & Lead Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Institutional Learning Engine
    - Phase / Milestone: Institutional Learning Engine
    - Target Directory: tools/eos/learning/
    - File Path: tools/eos/learning/learning_cycle.py
    - Runtime Alignment: Python 3.10+ Production Environment
===============================================================================
"""

import enum
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class LearningCyclePhase(str, enum.Enum):
    """
    Canonical lifecycle phases for institutional learning transformation.
    """
    OBSERVATION = "OBSERVATION"  # Memory becomes learning: Capturing raw pipeline execution Telemetry
    REPLAY = "REPLAY"            # Replay becomes experience: Simulating past executions vs current outcomes
    INFERENCE = "INFERENCE"      # Prediction becomes knowledge: Extracting statistical patterns & rules
    EVOLUTION = "EVOLUTION"      # Knowledge evolution: Updating confidence scores and system defaults


@dataclass
class LearningCycleRecord:
    """
    Captures the full state and metrics generated during a single iteration of the Learning Cycle.
    """
    cycle_id: str
    phase: LearningCyclePhase = LearningCyclePhase.OBSERVATION
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    observations_processed: int = 0
    inferences_generated: int = 0
    evolved_knowledge_nodes: int = 0
    insights: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def complete_cycle(self) -> None:
        """Marks the learning cycle as complete."""
        self.end_time = time.time()

    @property
    def duration_ms(self) -> float:
        """Calculates total wall-clock duration of the learning cycle in milliseconds."""
        end = self.end_time if self.end_time is not None else time.time()
        return (end - self.start_time) * 1000.0

    def to_dict(self) -> Dict[str, Any]:
        """Serializes learning cycle telemetry for audit logging."""
        return {
            "cycle_id": self.cycle_id,
            "phase": self.phase.value,
            "duration_ms": round(self.duration_ms, 3),
            "observations_processed": self.observations_processed,
            "inferences_generated": self.inferences_generated,
            "evolved_knowledge_nodes": self.evolved_knowledge_nodes,
            "insights": self.insights,
            "errors": self.errors,
        }


__all__ = ["LearningCyclePhase", "LearningCycleRecord"]
