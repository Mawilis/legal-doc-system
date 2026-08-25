"""
===============================================================================
WILSY ENGINEERING KERNEL — EXECUTION TIMELINE
===============================================================================
Epitome:
    Constructs chronological execution timelines for auditability and event inspection.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Foundation:
    Ephesians 5:16 — "Redeeming the time, because the days are evil."

Collaboration & Maintenance:
    - Founder & Lead Architect: Wilson Khanyezi
    - Maintainers: Wilsy OS Core Engineering Team
===============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field


class TimelineEventDTO(BaseModel):
    """
    [DTO EXPLANATION]: Immutable timeline event record.
    """
    model_config = ConfigDict(frozen=True)

    timestamp: str = Field(description="ISO timestamp of event occurrence.")
    event_name: str = Field(description="Name of the kernel stage or event.")
    details: str = Field(description="Detailed event description.")


class ExecutionTimelineBuilder:
    """
    [CLASS EXPLANATION]: Builds chronological event timelines from execution telemetry.
    """

    @staticmethod
    def build_timeline(stages: List[Dict[str, str]]) -> List[TimelineEventDTO]:
        """
        [FUNCTION EXPLANATION]: Converts raw stage dicts into immutable TimelineEventDTO objects.
        """
        timeline = []
        for stage in stages:
            timeline.append(
                TimelineEventDTO(
                    timestamp=stage.get("timestamp", ""),
                    event_name=stage.get("event_name", ""),
                    details=stage.get("details", "")
                )
            )
        return timeline
