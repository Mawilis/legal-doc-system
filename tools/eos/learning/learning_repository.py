from __future__ import annotations

"""
===============================================================================
WILSY OS LEARNING — INSTITUTIONAL LEARNING REPOSITORY
===============================================================================
Epitome:
    High-performance, thread-safe memory repository storing historical build
    telemetry, layout benchmarks, and defect patterns. Provides fast query APIs
    to answer core optimization questions across Wilsy OS.

Biblical Worth Billions:
    "The heart of the prudent getteth knowledge; and the ear of the wise seeketh
    knowledge." — Proverbs 18:15
    A billion-dollar codebase remembers every build run, every failure mode, and
    every layout efficiency gain across time.

Collaboration & Ownership:
    - Founder & Lead Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Institutional Learning Engine
    - Phase / Milestone: Institutional Learning Engine
    - Target Directory: tools/eos/learning/
    - File Path: tools/eos/learning/learning_repository.py
    - Runtime Alignment: Python 3.10+ Production Environment
===============================================================================
"""

import json
import logging
import threading
from typing import Any, Dict, List, Optional

logger = logging.getLogger("WilsyOS.Learning.Repository")


class LearningRepository:
    """
    Thread-safe persistent store for institutional execution telemetry,
    architectural decision outcomes, and defect reduction patterns.
    """

    def __init__(self, storage_filepath: Optional[str] = None) -> None:
        self.storage_filepath = storage_filepath
        self._lock = threading.RLock()
        self._observations: List[Dict[str, Any]] = []
        self._build_benchmarks: Dict[str, List[float]] = {}
        self._layout_performance: Dict[str, Dict[str, Any]] = {}
        self._defect_logs: List[Dict[str, Any]] = []

    def record_observation(self, observation: Dict[str, Any]) -> None:
        """Stores a raw execution observation record."""
        with self._lock:
            self._observations.append(observation)

            # Categorize build benchmarks
            pipeline_id = observation.get("pipeline_id", "unknown")
            duration_ms = observation.get("statistics", {}).get("duration_ms", 0.0)
            if duration_ms > 0:
                if pipeline_id not in self._build_benchmarks:
                    self._build_benchmarks[pipeline_id] = []
                self._build_benchmarks[pipeline_id].append(duration_ms)

            # Categorize repository layout performance
            layout_id = observation.get("repository_layout", "default_monorepo")
            if layout_id not in self._layout_performance:
                self._layout_performance[layout_id] = {
                    "total_runs": 0,
                    "total_duration_ms": 0.0,
                    "success_count": 0,
                    "defect_count": 0,
                }

            layout_stats = self._layout_performance[layout_id]
            layout_stats["total_runs"] += 1
            layout_stats["total_duration_ms"] += duration_ms
            status = observation.get("status", "FAILED")
            if status == "COMPLETED":
                layout_stats["success_count"] += 1
            else:
                layout_stats["defect_count"] += 1

            # Log defect patterns if execution failed
            errors = observation.get("errors", [])
            if errors:
                self._defect_logs.append({
                    "pipeline_id": pipeline_id,
                    "layout_id": layout_id,
                    "errors": errors,
                    "architectural_config": observation.get("config", {}),
                })

    def query_fastest_builds(self) -> Dict[str, Any]:
        """
        Answers: 'What has historically produced the fastest builds?'
        """
        with self._lock:
            if not self._build_benchmarks:
                return {"fastest_pipeline": None, "avg_duration_ms": 0.0, "sample_size": 0}

            fastest_pipeline = None
            min_avg_duration = float("inf")

            for p_id, durations in self._build_benchmarks.items():
                avg_dur = sum(durations) / len(durations)
                if avg_dur < min_avg_duration:
                    min_avg_duration = avg_dur
                    fastest_pipeline = p_id

            return {
                "fastest_pipeline": fastest_pipeline,
                "avg_duration_ms": round(min_avg_duration, 3) if fastest_pipeline else 0.0,
                "sample_size": len(self._build_benchmarks.get(fastest_pipeline, [])),
            }

    def query_defect_reducing_decisions(self) -> Dict[str, Any]:
        """
        Answers: 'Which architectural decisions reduced defects?'
        """
        with self._lock:
            total_defects = len(self._defect_logs)
            layout_defect_rates = {}

            for layout_id, stats in self._layout_performance.items():
                total = stats["total_runs"]
                defects = stats["defect_count"]
                defect_rate = (defects / total) if total > 0 else 0.0
                layout_defect_rates[layout_id] = defect_rate

            best_layout = min(layout_defect_rates, key=layout_defect_rates.get) if layout_defect_rates else None

            return {
                "total_defects_logged": total_defects,
                "layout_defect_rates": layout_defect_rates,
                "lowest_defect_layout": best_layout,
            }

    def query_optimal_repository_layout(self) -> Dict[str, Any]:
        """
        Answers: 'Which repository layout consistently performs best?'
        """
        with self._lock:
            if not self._layout_performance:
                return {"optimal_layout": "default_monorepo", "score": 0.0, "reason": "No execution data yet."}

            best_layout = None
            highest_score = -1.0

            for layout_id, stats in self._layout_performance.items():
                total = stats["total_runs"]
                if total == 0:
                    continue
                avg_duration = stats["total_duration_ms"] / total
                success_rate = stats["success_count"] / total
                # Scoring formula balancing success rate (80%) and speed efficiency (20%)
                speed_score = max(0.0, 1.0 - (avg_duration / 60000.0))
                composite_score = (success_rate * 0.8) + (speed_score * 0.2)

                if composite_score > highest_score:
                    highest_score = composite_score
                    best_layout = layout_id

            return {
                "optimal_layout": best_layout,
                "composite_score": round(highest_score, 4),
                "metrics": self._layout_performance.get(best_layout, {}),
            }


__all__ = ["LearningRepository"]
