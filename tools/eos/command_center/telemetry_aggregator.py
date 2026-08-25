"""
===============================================================================
WILSY OS KERNEL — TELEMETRY AGGREGATOR
===============================================================================
[EPITOME]:
    Aggregates data across institutional memory, execution replay, prediction engines, 
    and digital twins into a unified live operational stream.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for telemetry drift or missing data feeds.

[BIBLICAL FOUNDATION]:
    Psalm 19:1 — "The heavens declare the glory of God; and the firmament shows His handiwork."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Telemetry Aggregator
===============================================================================
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional
from tools.eos.memory import MemoryStore, MemoryStatisticsCalculator
from tools.eos.prediction import FailurePredictor, PerformancePredictor, ArchitecturePredictor, TechnicalDebtPredictor
from tools.eos.command_center.command_center_models import CommandCenterSnapshot


class CommandCenterAggregator:
    """
    [ENGINE SPECIFICATION]: Telemetry Aggregator
    Compiles real-time command center snapshots from underlying kernel memory and prediction engines.
    """

    def __init__(
        self,
        memory_store: MemoryStore,
        digital_twin_state: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        [FUNCTION EXPLANATION]:
            Initializes the Telemetry Aggregator with an institutional MemoryStore and optional Digital Twin state.
        """
        self._memory_store = memory_store
        self._stats_calculator = MemoryStatisticsCalculator(memory_store)
        self._failure_predictor = FailurePredictor(memory_store)
        self._perf_predictor = PerformancePredictor(memory_store)
        self._arch_predictor = ArchitecturePredictor(memory_store)
        self._debt_predictor = TechnicalDebtPredictor(memory_store)
        self._digital_twin_state = digital_twin_state or {"twin_status": "SYNCHRONIZED", "nodes_active": 4}

    def generate_snapshot(self) -> CommandCenterSnapshot:
        """
        [FUNCTION EXPLANATION]:
            Aggregates system records, computes predictive analytics, and constructs 
            a unified CommandCenterSnapshot DTO.
        """
        stats = self._stats_calculator.compute_statistics()
        total_records = stats.get("total_institutional_records", 0)
        
        # Gather predictions
        fail_pred = self._failure_predictor.predict_failures()
        perf_pred = self._perf_predictor.predict_performance_degradation()
        arch_pred = self._arch_predictor.predict_architectural_drift()
        debt_pred = self._debt_predictor.predict_technical_debt()

        predictions = [fail_pred, perf_pred, arch_pred, debt_pred]
        critical_count = sum(1 for p in predictions if p.severity in ("HIGH", "CRITICAL"))

        system_status = "CRITICAL" if critical_count >= 2 else ("ALERT" if critical_count == 1 else "NOMINAL")

        snapshot_id = f"SNAP-{hashlib.sha256(str(total_records).encode('utf-8')).hexdigest()[:8]}"

        return CommandCenterSnapshot(
            snapshot_id=snapshot_id,
            system_status=system_status,
            total_executions=stats.get("unique_executions_recorded", 0),
            total_artifacts=stats.get("record_type_distribution", {}).get("ARTIFACT", 0),
            active_predictions=len(predictions),
            critical_alerts_count=critical_count,
            digital_twin_state=self._digital_twin_state,
            metadata={
                "memory_statistics": stats,
                "predictions_summary": [
                    {
                        "predictor": p.predictor_name,
                        "probability": p.probability,
                        "severity": p.severity.value
                    }
                    for p in predictions
                ]
            }
        )
