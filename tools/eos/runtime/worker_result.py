"""Canonical worker execution-result evidence contract.

TITLE: WILSY Runtime Worker Result
VERSION: v1.0.0-WILSY-RUNTIME-WORKER-RESULT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Fail-closed, validated execution-result evidence for the runtime worker boundary.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/runtime/worker_result.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.0 establishes a fail-closed FAILED default, nonblank task identity, finite nonnegative duration, and canonical result aliases while preserving mutable nested output semantics and all existing status values without adding authority.
COMPLIANCE: Explicit execution evidence; POPIA section 19, GDPR Article 32, SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Validates shape only; error details remain caller-supplied operational evidence.
TENANT BOUNDARY: task_id is execution correlation evidence, never tenant identity or authorization.
AUTHORITY BOUNDARY: No authentication, tenant authorization, principal authority, or KEXEC issuance.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

VERSION = "v1.0.0-WILSY-RUNTIME-WORKER-RESULT"


class WorkerExecutionStatusEnum(str, Enum):
    """Canonical terminal worker statuses; FAILURE aliases FAILED."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    FAILURE = "FAILED"
    CANCELLED = "CANCELLED"


class WorkerResultDTO(BaseModel):
    """Immutable-at-field-level execution evidence with fail-closed defaults.

    Omitted status is FAILED, never synthetic success. ``task_id`` must be a
    nonblank string and duration must be finite and nonnegative. Pydantic's
    frozen model prevents field reassignment, while nested ``output`` values
    remain mutable by design. This DTO owns no tenant, authentication, KEXEC,
    persistence, transaction, or financial authority.
    """

    model_config = ConfigDict(frozen=True)

    task_id: str = Field(description="Nonblank execution task identifier.")
    status: WorkerExecutionStatusEnum = Field(
        default=WorkerExecutionStatusEnum.FAILED,
        description="Worker terminal outcome; omission fails closed.",
    )
    execution_duration_ms: float = Field(
        ge=0.0,
        description="Finite nonnegative execution duration in milliseconds.",
    )
    output: Dict[str, Any] = Field(
        default_factory=dict,
        description="Caller-supplied execution output evidence.",
    )
    error_details: Optional[str] = Field(
        default=None,
        description="Optional caller-supplied operational failure evidence.",
    )

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, value: str) -> str:
        """Reject empty identity while preserving exact nonblank input."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("TASK_ID_REQUIRED")
        return value

    @field_validator("execution_duration_ms")
    @classmethod
    def validate_finite_duration(cls, value: float) -> float:
        """Reject non-finite duration evidence after numeric coercion."""
        if not math.isfinite(value):
            raise ValueError("EXECUTION_DURATION_MUST_BE_FINITE")
        return value


# Backward-compatible canonical aliases.
EngineWorkerResultDTO = WorkerResultDTO
WorkerExecutionResult = WorkerResultDTO


# ARTIFACT: worker_result.py
# VERSION: v1.0.0-WILSY-RUNTIME-WORKER-RESULT
# AUTHORITY BOUNDARY: execution-result evidence shape only.
# TENANT POSTURE: task_id is correlation evidence, never tenant authority.
# FAIL-CLOSED POSTURE: omitted status is FAILED; invalid identity/duration is rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
