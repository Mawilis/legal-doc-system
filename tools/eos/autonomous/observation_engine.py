"""
===============================================================================
WILSY OS — OBSERVATION ENGINE (FG196)
===============================================================================
Epitome:
    Consumes multi-source sovereign inputs (Telemetry, Events, Dashboard, Memory, 
    Digital Twin, Repository) and synthesizes actionable system observations 
    such as repository growth velocity, AI latency, memory fragmentation, review 
    backlogs, CPU load, and technical debt accumulation.

Biblical Worth Billions:
    "And he shall be like a tree planted by the rivers of water, that bringeth 
    forth his fruit in his season; his leaf also shall not wither; and whatsoever 
    he doeth shall prosper." 
    — Psalm 1:3

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/autonomous/observation_engine.py
===============================================================================
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger("WilsyOS.Autonomous.Observation")


@dataclass(frozen=True)
class SovereignObservation:
    """Immutable observation record produced by the FG196 Observation Engine."""
    observation_id: str
    source_domain: str  # TELEMETRY, EVENTS, DASHBOARD, MEMORY, DIGITAL_TWIN, REPOSITORY
    metric_name: str
    observed_value: Any
    severity: str  # INFO, WARNING, CRITICAL
    description: str
    timestamp: str


class ObservationEngine:
    """
    FG196 Observation Engine for Wilsy OS.
    
    Ingests raw operational data across 6 sovereign channels and produces 
    structured, immutable observations for downstream prediction and governance.
    """

    def __init__(self, engine_id: str = "WILSY-OBS-ENGINE-01") -> None:
        self.engine_id = engine_id
        logger.info("ObservationEngine initialized: %s", self.engine_id)

    def ingest_and_observe(
        self,
        telemetry: Optional[Dict[str, Any]] = None,
        events: Optional[List[Dict[str, Any]]] = None,
        dashboard: Optional[Dict[str, Any]] = None,
        memory: Optional[Dict[str, Any]] = None,
        digital_twin: Optional[Dict[str, Any]] = None,
        repository: Optional[Dict[str, Any]] = None,
    ) -> List[SovereignObservation]:
        """
        Consumes multi-source inputs and produces synthesized observations.
        """
        sast_tz = timezone(timedelta(hours=2))
        timestamp_str = datetime.now(sast_tz).strftime("%Y-%m-%d %H:%M:%S SAST")
        observations: List[SovereignObservation] = []

        # 1. Repository Channel Analysis
        if repository:
            growth_rate = repository.get("commit_velocity_per_hour", 0)
            if growth_rate > 15:
                observations.append(SovereignObservation(
                    observation_id=f"OBS-REPO-{int(datetime.now(timezone.utc).timestamp())}",
                    source_domain="REPOSITORY",
                    metric_name="commit_velocity",
                    observed_value=growth_rate,
                    severity="INFO",
                    description="Repository growing quickly; high commit velocity detected.",
                    timestamp=timestamp_str,
                ))
            backlog_count = repository.get("review_backlog_count", 0)
            if backlog_count > 5:
                observations.append(SovereignObservation(
                    observation_id=f"OBS-REV-{int(datetime.now(timezone.utc).timestamp())}",
                    source_domain="REPOSITORY",
                    metric_name="review_backlog",
                    observed_value=backlog_count,
                    severity="WARNING",
                    description="Review backlog elevated; pending pull requests require attention.",
                    timestamp=timestamp_str,
                ))

        # 2. Telemetry & Dashboard Channel Analysis
        if telemetry or dashboard:
            cpu_load = telemetry.get("cpu_usage_pct", dashboard.get("avg_cpu_pct", 0.0))
            if cpu_load > 80.0:
                observations.append(SovereignObservation(
                    observation_id=f"OBS-CPU-{int(datetime.now(timezone.utc).timestamp())}",
                    source_domain="TELEMETRY",
                    metric_name="cpu_load_pct",
                    observed_value=cpu_load,
                    severity="CRITICAL",
                    description="High CPU utilization detected across worker nodes.",
                    timestamp=timestamp_str,
                ))
            ai_latency = telemetry.get("ai_latency_ms", 0.0)
            if ai_latency > 250.0:
                observations.append(SovereignObservation(
                    observation_id=f"OBS-AI-{int(datetime.now(timezone.utc).timestamp())}",
                    source_domain="DASHBOARD",
                    metric_name="ai_latency_ms",
                    observed_value=ai_latency,
                    severity="WARNING",
                    description="AI inference latency increasing above nominal thresholds.",
                    timestamp=timestamp_str,
                ))

        # 3. Memory Channel Analysis
        if memory:
            fragmentation = memory.get("fragmentation_ratio", 0.0)
            if fragmentation > 0.15:
                observations.append(SovereignObservation(
                    observation_id=f"OBS-MEM-{int(datetime.now(timezone.utc).timestamp())}",
                    source_domain="MEMORY",
                    metric_name="fragmentation_ratio",
                    observed_value=fragmentation,
                    severity="WARNING",
                    description="Memory fragmentation exceeding optimal operational limits.",
                    timestamp=timestamp_str,
                ))

        # 4. Digital Twin Channel Analysis
        if digital_twin:
            tech_debt_score = digital_twin.get("technical_debt_score", 0.0)
            if tech_debt_score > 50.0:
                observations.append(SovereignObservation(
                    observation_id=f"OBS-DT-{int(datetime.now(timezone.utc).timestamp())}",
                    source_domain="DIGITAL_TWIN",
                    metric_name="technical_debt_score",
                    observed_value=tech_debt_score,
                    severity="WARNING",
                    description="Technical debt rising within digital twin architectural models.",
                    timestamp=timestamp_str,
                ))

        logger.info("ObservationEngine generated %d sovereign observations.", len(observations))
        return observations
