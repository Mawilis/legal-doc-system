"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Institutional Kernel Runtime Integration Contracts & Schema Engine (FG171).
    Defines strongly-typed, schema-validated, and cryptographically traceable
    DTO contracts for unified multi-engine orchestration (`ExecutionContext`,
    `ExecutionPlan`, and `RuntimeExecutionResult`).
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready kernel runtime contracts. Zero child's place.
    Colossians 1:17 - "And he is before all things, and by him all things consist."
    Proverbs 16:3 - "Commit thy works unto the Lord, and thy thoughts shall be established."

Collaboration & Maintenance:
    - [Architecture]: Unified runtime pipeline contracts connecting all 9+ platform engines.
    - [Integrity]: Immutable Pydantic V2 models for zero-drift payload serialization.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class RuntimeStatusEnum(str, Enum):
    """Execution lifecycle status classification."""
    PENDING = "PENDING"
    PLANNING = "PLANNING"
    SCHEDULING = "SCHEDULING"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ExecutionContextDTO(BaseModel):
    """
    Encapsulates the raw inbound execution request, tenant state, and environmental security context.
    """
    model_config = ConfigDict(frozen=True)

    request_id: str = Field(description="Unique tracing identifier for the inbound execution request.")
    tenant_id: str = Field(default="tenant-institutional-primary", description="Tenant isolation boundary.")
    actor: str = Field(default="system-kernel", description="Initiating actor or automated scheduler.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Payload parameters and configuration variables.")
    created_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="UTC timestamp when the context was initialized."
    )


class ExecutionPlanStepDTO(BaseModel):
    """Defines a single scheduled execution step across registered engine workers."""
    model_config = ConfigDict(frozen=True)

    step_id: str = Field(description="Deterministic step identifier.")
    target_engine: str = Field(description="Target engine worker (e.g., repository, ai, quality, sentinel).")
    action: str = Field(description="Specific operation to execute within the target engine.")
    dependencies: List[str] = Field(default_factory=list, description="Step IDs that must complete prior to this step.")


class ExecutionPlanDTO(BaseModel):
    """
    The structured, dependency-resolved execution roadmap generated from the ExecutionContext.
    """
    model_config = ConfigDict(frozen=True)

    plan_id: str = Field(description="Unique identifier for this execution plan.")
    request_id: str = Field(description="Associated inbound request ID.")
    steps: List[ExecutionPlanStepDTO] = Field(default_factory=list, description="Ordered sequence of engine execution steps.")
    total_steps: int = Field(ge=0, description="Total count of execution steps in the plan.")


class RuntimeExecutionResultDTO(BaseModel):
    """
    The final synthesized output of the complete runtime pipeline,
    including event publication, artifact bus registers, reports, and dashboard snapshots.
    """
    model_config = ConfigDict(frozen=True)

    execution_id: str = Field(description="Unique identifier for the completed runtime run.")
    request_id: str = Field(description="Original inbound request ID.")
    status: RuntimeStatusEnum = Field(description="Final execution lifecycle status.")
    execution_duration_ms: float = Field(ge=0.0, description="Total pipeline execution duration in milliseconds.")
    
    # Subsystem Integration Outputs
    plan: ExecutionPlanDTO = Field(description="The execution plan that was executed.")
    emitted_events_count: int = Field(ge=0, description="Number of events published to the Event Bus.")
    registered_artifacts: List[str] = Field(default_factory=list, description="Artifact IDs registered on the Artifact Bus.")
    unified_report_id: Optional[str] = Field(default=None, description="Generated unified report artifact ID.")
    dashboard_snapshot_id: Optional[str] = Field(default=None, description="Control room snapshot reference ID.")
    
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="UTC completion timestamp."
    )
