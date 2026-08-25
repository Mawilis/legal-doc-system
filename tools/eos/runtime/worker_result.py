"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Worker Execution Result Data Transfer Object & Execution Enums (FG171C).
    Defines execution status states and the immutable output DTO returned by workers.
    Billion-dollar software architecture: secure, robust, immutable, and future-proof.

Biblical Scale & Architecture:
    Production-ready result model. Zero child's place.
    Proverbs 24:3-4 - "Through wisdom is an house builded; and by understanding it is established..."

Collaboration & Maintenance:
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class WorkerExecutionStatusEnum(str, Enum):
    """Execution status enum for worker execution results."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    FAILURE = "FAILED"  # Alias for backward compatibility & typing stability
    CANCELLED = "CANCELLED"


class WorkerResultDTO(BaseModel):
    """Immutable execution outcome DTO produced by engine workers."""
    model_config = ConfigDict(frozen=True)

    task_id: str = Field(description="Target execution task ID.")
    status: WorkerExecutionStatusEnum = Field(
        default=WorkerExecutionStatusEnum.SUCCESS,
        description="Execution outcome state."
    )
    execution_duration_ms: float = Field(
        ge=0.0,
        description="Execution duration benchmark in milliseconds."
    )
    output: Dict[str, Any] = Field(
        default_factory=dict,
        description="Execution output dictionary."
    )
    error_details: Optional[str] = Field(
        default=None,
        description="Detailed error trace if execution failed."
    )


# [FUNCTION EXPLANATION]: Type aliases ensuring backward compatibility across all runtime worker modules
EngineWorkerResultDTO = WorkerResultDTO
WorkerExecutionResult = WorkerResultDTO
