"""
===============================================================================
WILSY OS KERNEL — COMMAND CENTER MODELS
===============================================================================
[EPITOME]:
    Defines immutable data models for command center snapshots and associated DTOs.
    Engineered to billion-dollar enterprise production standards.

[BIBLICAL FOUNDATION]:
    Proverbs 24:3-4 — "Through wisdom a house is built..."

[COLLABORATION & MAINTENANCE]:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
    - Classification: Billion-Dollar Production Grade / Command Center
===============================================================================
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CommandCenterSnapshot(BaseModel):
    """
    [MODEL SPECIFICATION]: Command Center Snapshot
    Immutable snapshot of the command center state at a point in time.
    """
    model_config = ConfigDict(frozen=True)

    snapshot_id: str = Field(description="Unique snapshot identifier.")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of the snapshot."
    )
    system_status: str = Field(default="OPERATIONAL", description="Overall system status.")
    total_executions: int = Field(default=0, ge=0, description="Total number of executions.")
    total_artifacts: int = Field(default=0, ge=0, description="Total number of artifacts.")
    active_predictions: int = Field(default=0, ge=0, description="Number of active predictions.")
    critical_alerts_count: int = Field(default=0, ge=0, description="Number of critical alerts.")
    digital_twin_state: Dict[str, Any] = Field(default_factory=dict, description="Digital twin state.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata.")

    def dict(self, **kwargs) -> Dict[str, Any]:
        """Override to ensure compatibility with older code."""
        return super().model_dump(**kwargs)
