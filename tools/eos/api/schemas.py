"""
===============================================================================
WILSY OS — SOVEREIGN OPERATING SYSTEM
MODULE: FG211 INSTITUTIONAL REST API - PANDANTIC SCHEMAS
FILE: tools/eos/api/schemas.py
===============================================================================
Epitome:
    Strict Pydantic data contracts for request validation and OpenAPI response
    serialization across the FG211 Kernel Gateway.

Biblical Worth Billions:
    "In the mouth of two or three witnesses shall every word be established."
    — 2 Corinthians 13:1

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/api/schemas.py
===============================================================================
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExecutionRequest(BaseModel):
    execution_id: str = Field(..., description="Unique sovereign execution identifier (e.g. KEXEC-FG211-API)")
    module_code: str = Field(..., description="Target kernel module code (e.g. FG211)")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Execution payload parameters")


class SchedulerTriggerRequest(BaseModel):
    task_name: str = Field(..., description="Name of the kernel background task or workflow")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task execution parameters")


class GovernanceEvaluationRequest(BaseModel):
    artifact_id: str = Field(..., description="Artifact or contract ID to evaluate")
    ruleset: str = Field(default="SOVEREIGN_GOLD", description="Target compliance ruleset")


class CompatibilityCheckRequest(BaseModel):
    source_abi_version: str = Field(..., description="Source kernel ABI version")
    target_abi_version: str = Field(..., description="Target kernel ABI version")


class StandardApiResponse(BaseModel):
    success: bool = Field(..., description="Indicates whether the operation succeeded")
    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Descriptive status message")
    data: Optional[Any] = Field(None, description="Payload data or resulting entity")
    timestamp: str = Field(..., description="ISO 8601 SAST timestamp")
    execution_id: str = Field(..., description="Traceable request execution ID")
