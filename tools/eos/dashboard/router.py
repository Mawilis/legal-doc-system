"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Institutional Executive Dashboard Router Engine (FG170).
    Provides FastAPI endpoints for the real-time control room, enabling live state
    queries across all 9 core platform engines.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready control room gateway routes. Zero child's place.
    Habakkuk 2:2 - "And the Lord answered me, and said, Write the vision, and make
                   it plain upon tables, that he may run that readeth it."

Collaboration & Maintenance:
    - [Architecture]: APIRouter exposing full executive dashboard & engine sub-routes.
    - [Performance]: Non-blocking async endpoints returning strongly-typed DTO responses.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, status

from .contracts import ExecutiveDashboardDTO
from .engine import DashboardControlRoomEngine

logger = logging.getLogger("WilsyOS.Dashboard.Router")

router = APIRouter(prefix="/dashboard", tags=["Executive Control Room"])
_engine = DashboardControlRoomEngine()


# [FUNCTION EXPLANATION]: Fetches the live control room snapshot across all 9 platform engines.
@router.get(
    "/live",
    response_model=ExecutiveDashboardDTO,
    status_code=status.HTTP_200_OK,
    summary="Fetch live executive control room snapshot",
    description="Aggregates real-time metrics across Execution, Telemetry, Repository, Digital Twin, AI, Sentinel, Knowledge Graph, Artifacts, and Reports."
)
async def get_live_control_room() -> ExecutiveDashboardDTO:
    """
    Returns the unified ExecutiveDashboardDTO aggregating state across all 9 kernel engines.
    """
    try:
        snapshot = await _engine.generate_snapshot()
        return snapshot
    except Exception as exc:
        logger.error(f"Failed to generate executive control room snapshot: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Control room aggregation error: {str(exc)}"
        )


# [FUNCTION EXPLANATION]: Fetches telemetry specific to a single named kernel engine.
@router.get(
    "/engine/{engine_name}",
    status_code=status.HTTP_200_OK,
    summary="Query individual kernel engine metrics",
    description="Retrieves granular control room telemetry for a specific kernel engine."
)
async def get_engine_metrics(engine_name: str):
    """
    Returns telemetry for the specified engine name.
    """
    valid_engines = {
        "execution": _engine._fetch_execution_summary,
        "telemetry": _engine._fetch_telemetry_summary,
        "repository": _engine._fetch_repository_summary,
        "digital_twin": _engine._fetch_digital_twin_summary,
        "ai": _engine._fetch_ai_summary,
        "sentinel": _engine._fetch_sentinel_summary,
        "knowledge_graph": _engine._fetch_knowledge_graph_summary,
        "artifacts": _engine._fetch_artifacts_summary,
        "reports": _engine._fetch_reports_summary,
    }

    normalized = engine_name.lower().replace("-", "_")
    if normalized not in valid_engines:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Engine '{engine_name}' not recognized. Valid options: {list(valid_engines.keys())}"
        )

    try:
        fetcher = valid_engines[normalized]
        metrics = await fetcher()
        return {"engine": normalized, "metrics": metrics.model_dump()}
    except Exception as exc:
        logger.error(f"Failed to fetch metrics for engine '{engine_name}': {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Engine query error: {str(exc)}"
        )
