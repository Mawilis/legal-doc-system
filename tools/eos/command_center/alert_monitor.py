"""
===============================================================================
WILSY OS KERNEL — COMMAND CENTER ALERT MONITOR
===============================================================================
[EPITOME]:
    Continuously monitors command center snapshots and predictive streams to trigger 
    enterprise alerts for critical anomalies.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for unhandled operational risks.

[BIBLICAL FOUNDATION]:
    Ezekiel 33:6 — "But if the watchman sees the sword coming and does not blow the trumpet, and the people are not warned..."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Alert Monitor
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List
from tools.eos.command_center.command_center_models import CommandCenterSnapshot


class CommandCenterAlertMonitor:
    """
    [ENGINE SPECIFICATION]: Alert Monitor
    Evaluates command center snapshots to detect anomalies and generate security/operational warnings.
    """

    def __init__(self, snapshot: CommandCenterSnapshot) -> None:
        """
        [FUNCTION EXPLANATION]:
            Initializes the CommandCenterAlertMonitor with a CommandCenterSnapshot.
        """
        self._snapshot = snapshot

    def check_alerts(self) -> List[Dict[str, Any]]:
        """
        [FUNCTION EXPLANATION]:
            Inspects snapshot metadata and metrics to compile a list of active operational alerts.
        """
        alerts = []
        
        if self._snapshot.system_status in ("ALERT", "CRITICAL"):
            alerts.append({
                "level": self._snapshot.system_status,
                "message": f"Kernel status escalated to {self._snapshot.system_status}. Critical alerts count: {self._snapshot.critical_alerts_count}.",
                "timestamp": self._snapshot.timestamp
            })

        metadata = self._snapshot.metadata
        predictions = metadata.get("predictions_summary", [])
        
        for pred in predictions:
            if pred.get("severity") in ("HIGH", "CRITICAL") or pred.get("probability", 0.0) > 0.7:
                alerts.append({
                    "level": pred.get("severity"),
                    "message": f"Predictive alert from {pred.get('predictor')}: Probability {pred.get('probability')}.",
                    "timestamp": self._snapshot.timestamp
                })

        return alerts
