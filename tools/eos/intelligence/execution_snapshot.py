"""
===============================================================================
WILSY ENGINEERING KERNEL — EXECUTION SNAPSHOT
===============================================================================
Epitome:
    Creates immutable point-in-time snapshots encompassing the entire runtime state,
    knowledge graph, sentinel status, and dashboard metrics.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Foundation:
    Proverbs 27:23 — "Be thou diligent to know the state of thy flocks, and look well to thy herds."

Collaboration & Maintenance:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class ExecutionSnapshotDTO(BaseModel):
    """
    [DTO EXPLANATION]: Immutable institutional snapshot capturing complete runtime
    context and subsystem states at the exact moment of execution completion.
    """
    model_config = ConfigDict(frozen=True)

    execution_id: str = Field(description="Associated execution identifier.")
    snapshot_timestamp: str = Field(description="ISO timestamp when the snapshot was captured.")
    runtime_context: Dict[str, Any] = Field(description="Runtime environment and configuration state.")
    repository_session: Dict[str, Any] = Field(description="Repository scan state and module count.")
    knowledge_graph_snapshot: Dict[str, Any] = Field(description="Knowledge graph node and edge states.")
    sentinel_snapshot: Dict[str, Any] = Field(description="Sentinel security and compliance status.")
    dashboard_snapshot: Dict[str, Any] = Field(description="Live dashboard cache state and task counts.")
    execution_plan: Dict[str, Any] = Field(description="Execution plan stages and parameters.")
    scheduler_results: Dict[str, Any] = Field(description="Scheduler execution outcomes.")
    event_summary: Dict[str, Any] = Field(description="Event bus message distribution summary.")
    artifact_summary: Dict[str, Any] = Field(description="Indexed artifact catalog summary.")
    unified_report_reference: str = Field(description="Storage path to the serialized unified report.")
