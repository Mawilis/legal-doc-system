"""WILSY OS — immutable Executive Workflow intent boundary.

TITLE: WILSY Executive Workflow Intent Engine
VERSION: v1.0.0-WILSY-EXECUTIVE-WORKFLOW-INTENT
AUTHORITY: Wilsy OS Core Governance; Kennel EOS / Python sovereign truth
PURPOSE: Bind one validated Executive Planning result into an immutable workflow-intent envelope without dispatching or executing anything.
EPITOME: Workflow preserves Planning provenance as inert intent; it creates no evidence, outcome, approval, authorization, release, payment, transfer, settlement, or execution truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/executive/intelligence/executive_workflow_engine.py
CONTRACT DATE: 2026-09-02

TENANT BOUNDARY: Identity derives only through the supplied ExecutivePlanningResult lineage.
AUTHORITY BOUNDARY: Workflow intent is advisory coordination metadata only and grants no approval, authorization, dispatch, release, or execution authority.
EVIDENCE BOUNDARY: NO EVIDENCE = NO FACT; Workflow preserves the exact Planning evidence-reference tuple and creates no evidence.
PLANNING BOUNDARY: ExecutivePlanningResult is the sole executive upstream input and remains the source of plan intent and ordered plan steps.
STATE BOUNDARY: Stateless and non-persistent; no runtime history, cache, database, network, filesystem, or subprocess side effect.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512

from tools.eos.executive.intelligence.executive_planning_engine import (
    ExecutivePlanningResult,
)


VERSION = "v1.0.0-WILSY-EXECUTIVE-WORKFLOW-INTENT"


class ExecutiveWorkflowError(ValueError):
    """Stable private-safe Workflow contract error."""


def _frame_text(value: str) -> bytes:
    raw = value.encode("utf-8")
    return len(raw).to_bytes(8, "big") + raw


def _workflow_id(
    planning: ExecutivePlanningResult,
    defined_at: datetime,
) -> str:
    hasher = sha3_512()

    for component in (
        planning.tenant_id,
        planning.principal_id,
        planning.request_id,
        planning.correlation_id,
        planning.decision_id,
        planning.plan_id,
        planning.target_domain,
        planning.plan_intent,
    ):
        hasher.update(
            _frame_text(component)
        )

    hasher.update(
        len(planning.plan_steps).to_bytes(
            8,
            "big",
        )
    )

    for step in planning.plan_steps:
        hasher.update(
            _frame_text(step)
        )

    hasher.update(
        _frame_text(
            defined_at.isoformat()
        )
    )

    return (
        "WORKFLOW-"
        + hasher.hexdigest()[:16]
    )


def _validate_defined_at(
    defined_at: datetime,
) -> None:
    if (
        not isinstance(
            defined_at,
            datetime,
        )
        or defined_at.tzinfo is None
        or defined_at.utcoffset() is None
    ):
        raise ExecutiveWorkflowError(
            "INVALID_DEFINED_AT"
        )


def _revalidate_planning(
    planning: ExecutivePlanningResult,
) -> None:
    if type(planning) is not ExecutivePlanningResult:
        raise ExecutiveWorkflowError(
            "INVALID_PLANNING_TYPE"
        )

    try:
        ExecutivePlanningResult(
            planning.plan_id,
            planning.planned_at,
            planning.plan_intent,
            planning.plan_steps,
            planning.decision,
            planning.evidence_references,
            planning.status,
        )
    except Exception:
        raise ExecutiveWorkflowError(
            "INVALID_PLANNING_PROVENANCE"
        ) from None


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutiveWorkflowIntent:
    """Immutable non-executing Workflow intent bound to verified Planning."""

    workflow_id: str
    defined_at: datetime
    planning: ExecutivePlanningResult
    evidence_references: tuple[object, ...]
    status: str

    def __post_init__(self) -> None:
        _revalidate_planning(
            self.planning
        )

        _validate_defined_at(
            self.defined_at
        )

        if (
            not isinstance(
                self.workflow_id,
                str,
            )
            or len(
                self.workflow_id
            )
            != 25
            or not self.workflow_id.startswith(
                "WORKFLOW-"
            )
            or any(
                character
                not in "0123456789abcdef"
                for character
                in self.workflow_id[9:]
            )
            or self.workflow_id
            != _workflow_id(
                self.planning,
                self.defined_at,
            )
        ):
            raise ExecutiveWorkflowError(
                "INVALID_WORKFLOW_ID"
            )

        if (
            self.evidence_references
            is not self.planning.evidence_references
        ):
            raise ExecutiveWorkflowError(
                "EVIDENCE_REFERENCE_MISMATCH"
            )

        expected_status = (
            "NO_EVIDENCE"
            if self.planning.evidence_count == 0
            else "EVIDENCE_BOUND"
        )

        if self.status != expected_status:
            raise ExecutiveWorkflowError(
                "INVALID_WORKFLOW_STATUS"
            )

    @property
    def decision(self) -> object:
        return self.planning.decision

    @property
    def plan_intent(self) -> str:
        return self.planning.plan_intent

    @property
    def plan_steps(
        self,
    ) -> tuple[str, ...]:
        return self.planning.plan_steps

    @property
    def tenant_id(self) -> str:
        return self.planning.tenant_id

    @property
    def principal_id(self) -> str:
        return self.planning.principal_id

    @property
    def request_id(self) -> str:
        return self.planning.request_id

    @property
    def correlation_id(self) -> str:
        return self.planning.correlation_id

    @property
    def decision_id(self) -> str:
        return self.planning.decision_id

    @property
    def target_domain(self) -> str:
        return self.planning.target_domain

    @property
    def plan_id(self) -> str:
        return self.planning.plan_id

    @property
    def evidence_count(self) -> int:
        return self.planning.evidence_count


class ExecutiveWorkflowEngine:
    """Stateless builder for immutable non-executing Workflow intent."""

    __slots__ = ()

    def build_workflow(
        self,
        planning: ExecutivePlanningResult,
        *,
        defined_at: datetime | None = None,
    ) -> ExecutiveWorkflowIntent:
        """Build one deterministic Workflow intent from verified Planning."""

        _revalidate_planning(
            planning
        )

        at = (
            datetime.now(
                timezone.utc
            )
            if defined_at is None
            else defined_at
        )

        _validate_defined_at(at)

        status = (
            "NO_EVIDENCE"
            if planning.evidence_count == 0
            else "EVIDENCE_BOUND"
        )

        return ExecutiveWorkflowIntent(
            workflow_id=_workflow_id(
                planning,
                at,
            ),
            defined_at=at,
            planning=planning,
            evidence_references=(
                planning.evidence_references
            ),
            status=status,
        )


executive_workflow_engine = (
    ExecutiveWorkflowEngine()
)


__all__ = (
    "VERSION",
    "ExecutiveWorkflowError",
    "ExecutiveWorkflowIntent",
    "ExecutiveWorkflowEngine",
    "executive_workflow_engine",
)


# AUTHORITY BOUNDARY: Workflow carries verified Planning intent only; it cannot authorize, dispatch, release, or execute.
# EVIDENCE POSTURE: NO EVIDENCE = NO FACT; exact Planning evidence references are preserved without manufacturing evidence.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS EXECUTIVE WORKFLOW INTENT ENGINE
