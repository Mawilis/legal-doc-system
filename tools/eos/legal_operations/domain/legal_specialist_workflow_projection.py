"""
WILSY OS — Legal Specialist Workflow Projection.

PURPOSE
-------
Project explanatory workflow state onto Legal work that has already been
admitted by the canonical LegalProductiveWorkProjection.

AUTHORITY CEILING
-----------------
LegalProductiveWorkProjection is absolute. Workflow evidence can enrich an
already-visible work item but can never introduce work, assignment,
supervision, IAM authority, professional authority, workflow-transition
authority, deadline truth, payment authority or settlement authority.

This module is pure, immutable and read-only.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Iterable

from tools.eos.legal_operations.domain.legal_profile_productive_work import (
    LegalProductiveWorkProjection,
)


VERSION: Final[str] = "v1.0.0-P0-LEGAL-SPECIALIST-WORKFLOW-PROJECTION"
SCHEMA: Final[str] = "WILSY-LEGAL-SPECIALIST-WORKFLOW-PROJECTION/V1"

READINESS_ACTIONABLE: Final[str] = "ACTIONABLE"
READINESS_BLOCKED_DEPENDENCY: Final[str] = "BLOCKED_DEPENDENCY"
READINESS_BLOCKED_GATE: Final[str] = "BLOCKED_GATE"
READINESS_BLOCKED_DEPENDENCY_AND_GATE: Final[str] = (
    "BLOCKED_DEPENDENCY_AND_GATE"
)

READINESS_VALUES: Final[frozenset[str]] = frozenset(
    {
        READINESS_ACTIONABLE,
        READINESS_BLOCKED_DEPENDENCY,
        READINESS_BLOCKED_GATE,
        READINESS_BLOCKED_DEPENDENCY_AND_GATE,
    }
)


class LegalSpecialistWorkflowProjectionError(ValueError):
    """Fail-closed specialist workflow projection contract error."""


def _require_text(value: object, *, field: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        raise LegalSpecialistWorkflowProjectionError(
            f"INVALID_{field.upper()}"
        )
    return value


def _require_optional_text(
    value: object,
    *,
    field: str,
) -> str | None:
    if value is None:
        return None
    return _require_text(
        value,
        field=field,
    )


def _require_text_tuple(
    value: object,
    *,
    field: str,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise LegalSpecialistWorkflowProjectionError(
            f"INVALID_{field.upper()}"
        )

    validated = tuple(
        _require_text(
            item,
            field=field,
        )
        for item in value
    )

    if len(set(validated)) != len(validated):
        raise LegalSpecialistWorkflowProjectionError(
            f"DUPLICATE_{field.upper()}"
        )

    return validated


@dataclass(frozen=True, slots=True)
class LegalSpecialistWorkflowContext:
    """Explanatory workflow evidence; never an authorization object."""

    tenant_id: str
    work_item_id: str
    case_matter_id: str
    workflow_instance_id: str
    workflow_definition_id: str
    stage_definition_id: str
    blocking_dependency_work_item_ids: tuple[str, ...]
    unsatisfied_gate_references: tuple[str, ...]
    materialization_transition_id: str | None
    materialization_receipt_id: str | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "tenant_id",
            _require_text(
                self.tenant_id,
                field="tenant_id",
            ),
        )
        object.__setattr__(
            self,
            "work_item_id",
            _require_text(
                self.work_item_id,
                field="work_item_id",
            ),
        )
        object.__setattr__(
            self,
            "case_matter_id",
            _require_text(
                self.case_matter_id,
                field="case_matter_id",
            ),
        )
        object.__setattr__(
            self,
            "workflow_instance_id",
            _require_text(
                self.workflow_instance_id,
                field="workflow_instance_id",
            ),
        )
        object.__setattr__(
            self,
            "workflow_definition_id",
            _require_text(
                self.workflow_definition_id,
                field="workflow_definition_id",
            ),
        )
        object.__setattr__(
            self,
            "stage_definition_id",
            _require_text(
                self.stage_definition_id,
                field="stage_definition_id",
            ),
        )
        object.__setattr__(
            self,
            "blocking_dependency_work_item_ids",
            _require_text_tuple(
                self.blocking_dependency_work_item_ids,
                field="blocking_dependency_work_item_ids",
            ),
        )
        object.__setattr__(
            self,
            "unsatisfied_gate_references",
            _require_text_tuple(
                self.unsatisfied_gate_references,
                field="unsatisfied_gate_references",
            ),
        )
        object.__setattr__(
            self,
            "materialization_transition_id",
            _require_optional_text(
                self.materialization_transition_id,
                field="materialization_transition_id",
            ),
        )
        object.__setattr__(
            self,
            "materialization_receipt_id",
            _require_optional_text(
                self.materialization_receipt_id,
                field="materialization_receipt_id",
            ),
        )


@dataclass(frozen=True, slots=True)
class LegalSpecialistWorkflowRow:
    """Read-only workflow explanation for one already-visible work item."""

    work_item_id: str
    case_matter_id: str
    workflow_instance_id: str
    workflow_definition_id: str
    stage_definition_id: str
    readiness: str
    blocking_dependency_work_item_ids: tuple[str, ...]
    unsatisfied_gate_references: tuple[str, ...]
    materialization_transition_id: str | None
    materialization_receipt_id: str | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "work_item_id",
            _require_text(
                self.work_item_id,
                field="work_item_id",
            ),
        )
        object.__setattr__(
            self,
            "case_matter_id",
            _require_text(
                self.case_matter_id,
                field="case_matter_id",
            ),
        )
        object.__setattr__(
            self,
            "workflow_instance_id",
            _require_text(
                self.workflow_instance_id,
                field="workflow_instance_id",
            ),
        )
        object.__setattr__(
            self,
            "workflow_definition_id",
            _require_text(
                self.workflow_definition_id,
                field="workflow_definition_id",
            ),
        )
        object.__setattr__(
            self,
            "stage_definition_id",
            _require_text(
                self.stage_definition_id,
                field="stage_definition_id",
            ),
        )

        if self.readiness not in READINESS_VALUES:
            raise LegalSpecialistWorkflowProjectionError(
                "READINESS_NOT_CANONICAL"
            )

        object.__setattr__(
            self,
            "blocking_dependency_work_item_ids",
            _require_text_tuple(
                self.blocking_dependency_work_item_ids,
                field="blocking_dependency_work_item_ids",
            ),
        )
        object.__setattr__(
            self,
            "unsatisfied_gate_references",
            _require_text_tuple(
                self.unsatisfied_gate_references,
                field="unsatisfied_gate_references",
            ),
        )
        object.__setattr__(
            self,
            "materialization_transition_id",
            _require_optional_text(
                self.materialization_transition_id,
                field="materialization_transition_id",
            ),
        )
        object.__setattr__(
            self,
            "materialization_receipt_id",
            _require_optional_text(
                self.materialization_receipt_id,
                field="materialization_receipt_id",
            ),
        )


@dataclass(frozen=True, slots=True)
class LegalSpecialistWorkflowProjection:
    """Immutable specialist projection with no independent authority."""

    tenant_id: str
    principal_id: str
    as_of: object
    rows: tuple[LegalSpecialistWorkflowRow, ...]
    schema: str = SCHEMA
    version: str = VERSION

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "tenant_id",
            _require_text(
                self.tenant_id,
                field="tenant_id",
            ),
        )
        object.__setattr__(
            self,
            "principal_id",
            _require_text(
                self.principal_id,
                field="principal_id",
            ),
        )

        if not isinstance(self.rows, tuple):
            raise LegalSpecialistWorkflowProjectionError(
                "ROWS_NOT_TUPLE"
            )

        if not all(
            isinstance(
                row,
                LegalSpecialistWorkflowRow,
            )
            for row in self.rows
        ):
            raise LegalSpecialistWorkflowProjectionError(
                "ROWS_INVALID"
            )


def _readiness_for(
    context: LegalSpecialistWorkflowContext,
) -> str:
    dependency_blocked = bool(
        context.blocking_dependency_work_item_ids
    )
    gate_blocked = bool(
        context.unsatisfied_gate_references
    )

    if dependency_blocked and gate_blocked:
        return READINESS_BLOCKED_DEPENDENCY_AND_GATE

    if dependency_blocked:
        return READINESS_BLOCKED_DEPENDENCY

    if gate_blocked:
        return READINESS_BLOCKED_GATE

    return READINESS_ACTIONABLE


def _productive_work_item_ids(
    productive_work: LegalProductiveWorkProjection,
) -> frozenset[str]:
    """
    Derive the ceiling only from rows already admitted by productive work.

    No workflow evidence participates in this calculation.
    """

    groups: tuple[Iterable[object], ...] = (
        productive_work.assigned_work_items,
        productive_work.supervised_work_items,
        productive_work.overdue_work_items,
        productive_work.due_soon_work_items,
    )

    identities: set[str] = set()

    for group in groups:
        for work_item in group:
            work_item_id = getattr(
                work_item,
                "work_item_id",
                None,
            )

            identities.add(
                _require_text(
                    work_item_id,
                    field="work_item_id",
                )
            )

    return frozenset(identities)


def compose_legal_specialist_workflow_projection(
    *,
    productive_work: LegalProductiveWorkProjection,
    workflow_contexts: tuple[
        LegalSpecialistWorkflowContext,
        ...,
    ],
) -> LegalSpecialistWorkflowProjection:
    """
    Enrich only productive work already visible to the principal.

    This function never authorizes, assigns, supervises, transitions,
    calculates deadline truth, executes payment, or settles anything.
    """

    if not isinstance(
        productive_work,
        LegalProductiveWorkProjection,
    ):
        raise LegalSpecialistWorkflowProjectionError(
            "PRODUCTIVE_WORK_INVALID"
        )

    if not isinstance(
        workflow_contexts,
        tuple,
    ):
        raise LegalSpecialistWorkflowProjectionError(
            "WORKFLOW_CONTEXTS_NOT_TUPLE"
        )

    for context in workflow_contexts:
        if not isinstance(
            context,
            LegalSpecialistWorkflowContext,
        ):
            raise LegalSpecialistWorkflowProjectionError(
                "WORKFLOW_CONTEXT_INVALID"
            )

        if (
            context.tenant_id
            != productive_work.tenant_id
        ):
            raise LegalSpecialistWorkflowProjectionError(
                "TENANT_MISMATCH"
            )

    visible_work_item_ids = (
        _productive_work_item_ids(
            productive_work
        )
    )

    rows_by_work_item: dict[
        str,
        LegalSpecialistWorkflowRow,
    ] = {}

    for context in workflow_contexts:
        if (
            context.work_item_id
            not in visible_work_item_ids
        ):
            continue

        row = LegalSpecialistWorkflowRow(
            work_item_id=context.work_item_id,
            case_matter_id=context.case_matter_id,
            workflow_instance_id=context.workflow_instance_id,
            workflow_definition_id=context.workflow_definition_id,
            stage_definition_id=context.stage_definition_id,
            readiness=_readiness_for(context),
            blocking_dependency_work_item_ids=(
                context.blocking_dependency_work_item_ids
            ),
            unsatisfied_gate_references=(
                context.unsatisfied_gate_references
            ),
            materialization_transition_id=(
                context.materialization_transition_id
            ),
            materialization_receipt_id=(
                context.materialization_receipt_id
            ),
        )

        existing = rows_by_work_item.get(
            context.work_item_id
        )

        if (
            existing is not None
            and existing != row
        ):
            raise LegalSpecialistWorkflowProjectionError(
                "WORKFLOW_CONTEXT_AMBIGUOUS"
            )

        rows_by_work_item[
            context.work_item_id
        ] = row

    rows = tuple(
        rows_by_work_item[
            work_item_id
        ]
        for work_item_id in sorted(
            rows_by_work_item
        )
    )

    return LegalSpecialistWorkflowProjection(
        tenant_id=productive_work.tenant_id,
        principal_id=productive_work.principal_id,
        as_of=productive_work.as_of,
        rows=rows,
    )


PUBLIC_CONTRACT = MappingProxyType(
    {
        "schema": SCHEMA,
        "version": VERSION,
        "authority_ceiling": "LegalProductiveWorkProjection",
        "readiness_values": tuple(
            sorted(
                READINESS_VALUES
            )
        ),
        "creates_authority": False,
    }
)


__all__ = (
    "LegalSpecialistWorkflowContext",
    "LegalSpecialistWorkflowProjection",
    "LegalSpecialistWorkflowProjectionError",
    "LegalSpecialistWorkflowRow",
    "PUBLIC_CONTRACT",
    "READINESS_VALUES",
    "SCHEMA",
    "VERSION",
    "compose_legal_specialist_workflow_projection",
)
