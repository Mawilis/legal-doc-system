"""
===============================================================================
WILSY OS KERNEL — OPERATIONAL DASHBOARD
===============================================================================
[EPITOME]:
    Renders structured executive summaries, live status tables, and diagnostic views 
    for the Wilsy OS Engineering Command Center.
    Engineered to billion-dollar enterprise production standards with zero tolerance 
    for unformatted telemetry output.

[BIBLICAL FOUNDATION]:
    Proverbs 24:3-4 — "Through wisdom a house is built, and by understanding it is established; by knowledge the rooms are filled with all precious and pleasant riches."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Operational Dashboard
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from tools.eos.command_center.command_center_models import CommandCenterSnapshot


class OperationalDashboard:
    """
    [ENGINE SPECIFICATION]: Operational Dashboard
    Transforms raw command center snapshots into structured executive reports and displays.
    Uses safe attribute access to handle missing fields.
    """

    def __init__(self, snapshot: Optional[CommandCenterSnapshot] = None) -> None:
        """
        [FUNCTION EXPLANATION]:
            Initializes the OperationalDashboard with an optional CommandCenterSnapshot.
        """
        self._snapshot = snapshot

    @staticmethod
    def _safe_get(obj: Any, attr: str, default: Any = None) -> Any:
        """Safely get attribute from object, returning default if not present."""
        return getattr(obj, attr, default)

    def render_executive_summary(self) -> Dict[str, Any]:
        """
        [FUNCTION EXPLANATION]:
            Produces a structured executive summary dictionary for live command center displays.
            Handles missing fields gracefully.
        """
        if self._snapshot is None:
            return {
                "snapshot_id": "NO_SNAPSHOT",
                "timestamp": "",
                "system_status": "UNAVAILABLE",
                "metrics": {
                    "total_executions": 0,
                    "total_artifacts": 0,
                    "active_predictions": 0,
                    "critical_alerts": 0,
                },
                "digital_twin": {},
                "telemetry": {}
            }

        return {
            "snapshot_id": self._safe_get(self._snapshot, 'snapshot_id', 'UNKNOWN'),
            "timestamp": self._safe_get(self._snapshot, 'timestamp', ''),
            "system_status": self._safe_get(self._snapshot, 'system_status', 'UNKNOWN'),
            "metrics": {
                "total_executions": self._safe_get(self._snapshot, 'total_executions', 0),
                "total_artifacts": self._safe_get(self._snapshot, 'total_artifacts', 0),
                "active_predictions": self._safe_get(self._snapshot, 'active_predictions', 0),
                "critical_alerts": self._safe_get(self._snapshot, 'critical_alerts_count', 0),
            },
            "digital_twin": self._safe_get(self._snapshot, 'digital_twin_state', {}),
            "telemetry": self._safe_get(self._snapshot, 'metadata', {})
        }

    def render_text_display(self) -> str:
        """
        [FUNCTION EXPLANATION]:
            Renders a formatted text-based ASCII dashboard view for terminal inspection.
        """
        summary = self.render_executive_summary()
        metrics = summary["metrics"]
        
        lines = [
            "=" * 75,
            " WILSY OS KERNEL — ENGINEERING COMMAND CENTER LIVE DASHBOARD",
            "=" * 75,
            f" Snapshot ID   : {summary['snapshot_id']}",
            f" Timestamp     : {summary['timestamp']}",
            f" System Status : {summary['system_status']}",
            "-" * 75,
            " LIVE OPERATIONAL METRICS:",
            f"   • Total Executions     : {metrics['total_executions']}",
            f"   • Total Artifacts      : {metrics['total_artifacts']}",
            f"   • Active Predictions   : {metrics['active_predictions']}",
            f"   • Critical Alerts      : {metrics['critical_alerts']}",
            "-" * 75,
            f" DIGITAL TWIN STATE : {summary['digital_twin']}",
            "=" * 75
        ]
        return "\n".join(lines)
