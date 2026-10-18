"""
TITLE: WILSY OS Legal Specialist Workflow Read Service

VERSION: v1.0.0-P1-LEGAL-SPECIALIST-WORKFLOW-READ-SERVICE

PURPOSE:
    Assemble explanatory workflow context for Legal work already admitted by
    LegalProductiveWorkProjection, then delegate the final projection to the
    sovereign pure specialist workflow composer.

AUTHORITY BOUNDARY:
    Read orchestration only. This service creates no work, assignment,
    supervision, completion, workflow transition, IAM, professional,
    deadline, billing, payment, settlement, AI-execution or financial truth.

TRANSACTION BOUNDARY:
    The caller owns one already-active transaction. The same session is passed
    unchanged to every durable registry read.

VISIBILITY BOUNDARY:
    LegalProductiveWorkProjection is absolute. Durable workflow evidence may
    enrich only work already visible in that projection.

CORRELATION BOUNDARY:
    LegalWorkItem contains no workflow pointer. Workflow identity is correlated
    only through exact immutable materialization-receipt output, transition
    evidence, workflow-instance evidence and complete transition currentness.

FINANCIAL AUTHORITY:
    None. Kennel EOS remains exclusive financial execution authority.
"""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha3_512
import json
from types import MappingProxyType
from typing import Any, Final, NoReturn, Protocol

from tools.eos.legal_operations.domain.legal_matter_workflow_instance import (
    LegalMatterWorkflowInstance,
)
from tools.eos.legal_operations.domain.legal_matter_workflow_currentness import (
    LegalMatterWorkflowCurrentness,
)
from tools.eos.legal_operations.domain.legal_profile_productive_work import (
    LegalProductiveWorkProjection,
)
from tools.eos.legal_operations.domain.legal_specialist_workflow_projection import (
    LegalSpecialistWorkflowContext,
    LegalSpecialistWorkflowProjection,
    compose_legal_specialist_workflow_projection,
)
from tools.eos.legal_operations.domain.legal_transition_work_materialization_receipt import (
    LegalTransitionWorkMaterializationReceipt,
)
from tools.eos.legal_operations.domain.legal_work_completion_currentness import (
    LegalWorkCompletionCurrentnessState,
    project_legal_work_completion_currentness,
)
from tools.eos.legal_operations.domain.legal_work_completion_event import (
    LegalWorkCompletionEvent,
)
from tools.eos.legal_operations.domain.legal_work_dependency_edge import (
    LegalWorkDependencyEdge,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
)
from tools.eos.legal_operations.domain.legal_workflow_gate_satisfaction import (
    LegalWorkflowGateSatisfaction,
)
from tools.eos.legal_operations.domain.legal_workflow_stage import (
    LegalWorkflowStage,
)


VERSION: Final[str] = (
    "v1.0.0-P1-LEGAL-SPECIALIST-WORKFLOW-READ-SERVICE"
)

WORKFLOW_CORRELATION_MODEL: Final[str] = (
    "VISIBLE_WORK_ITEM_ID"
    "->MATERIALIZATION_RECEIPT_OUTPUT"
    "->TRANSITION_ID"
    "->WORKFLOW_INSTANCE"
)


class LegalSpecialistWorkflowReadServiceError(
    RuntimeError
):
    """Base fail-closed specialist workflow read-service error."""


class LegalSpecialistWorkflowReadServiceTransactionRequiredError(
    LegalSpecialistWorkflowReadServiceError
):
    """Caller omitted one already-active transaction."""


def _fail(
    error_type: type[
        LegalSpecialistWorkflowReadServiceError
    ],
    code: str,
) -> NoReturn:
    raise error_type(
        code
    )


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 320
    ):
        _fail(
            LegalSpecialistWorkflowReadServiceError,
            f"P1_{name.upper()}_INVALID",
        )

    return value


def _moment(
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(
            LegalSpecialistWorkflowReadServiceError,
            "P1_AS_OF_INVALID",
        )

    return value.astimezone(
        timezone.utc
    )


def _transaction(
    session: Any,
) -> Any:
    if session is None:
        _fail(
            LegalSpecialistWorkflowReadServiceTransactionRequiredError,
            "P1_ACTIVE_CALLER_TRANSACTION_REQUIRED",
        )

    marker = getattr(
        session,
        "in_transaction",
        None,
    )

    try:
        active = (
            marker()
            if callable(marker)
            else marker
        )
    except Exception:
        active = False

    if active is not True:
        _fail(
            LegalSpecialistWorkflowReadServiceTransactionRequiredError,
            "P1_ACTIVE_CALLER_TRANSACTION_REQUIRED",
        )

    return session


def _currentness_id(
    *,
    tenant_id: str,
    workflow_instance_id: str,
    as_of: datetime,
) -> str:
    raw = json.dumps(
        {
            "tenant_id":
                tenant_id,
            "workflow_instance_id":
                workflow_instance_id,
            "as_of":
                as_of.isoformat(),
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode(
        "utf-8"
    )

    return sha3_512(
        raw
    ).hexdigest()


class _WorkItemReader(Protocol):
    def get_by_id(
        self,
        tenant_id: str,
        work_item_id: str,
        *,
        session: object,
    ) -> LegalWorkItem:
        ...


class _ReceiptReader(Protocol):
    def list_matter(
        self,
        tenant_id: str,
        case_matter_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalTransitionWorkMaterializationReceipt,
        ...,
    ]:
        ...


class _WorkflowInstanceReader(Protocol):
    def list_matter_instances(
        self,
        tenant_id: str,
        case_matter_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalMatterWorkflowInstance,
        ...,
    ]:
        ...


class _WorkflowTransitionReader(Protocol):
    def list_history(
        self,
        tenant_id: str,
        workflow_instance_id: str,
        *,
        session: object,
    ) -> tuple[object, ...]:
        ...

    def derive_currentness(
        self,
        currentness_id: str,
        workflow_instance: LegalMatterWorkflowInstance,
        *,
        session: object,
    ) -> LegalMatterWorkflowCurrentness:
        ...


class _WorkflowStageReader(Protocol):
    def get_by_definition_stage(
        self,
        workflow_definition_fingerprint: str,
        stage_definition_id: str,
        *,
        session: object,
    ) -> LegalWorkflowStage:
        ...


class _DependencyReader(Protocol):
    def list_predecessors(
        self,
        tenant_id: str,
        successor_work_item_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalWorkDependencyEdge,
        ...,
    ]:
        ...


class _CompletionReader(Protocol):
    def list_work_history(
        self,
        tenant_id: str,
        work_item_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalWorkCompletionEvent,
        ...,
    ]:
        ...


class _GateSatisfactionReader(Protocol):
    def list_workflow_stage(
        self,
        tenant_id: str,
        workflow_instance_id: str,
        source_stage_definition_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalWorkflowGateSatisfaction,
        ...,
    ]:
        ...


class LegalSpecialistWorkflowReadService:
    """
    Compose specialist workflow explanation from certified durable reads only.

    No registry exposed here is ever mutated by this service.
    """

    def __init__(
        self,
        *,
        work_item_registry: _WorkItemReader,
        receipt_registry: _ReceiptReader,
        workflow_instance_registry: _WorkflowInstanceReader,
        workflow_transition_registry: _WorkflowTransitionReader,
        workflow_stage_registry: _WorkflowStageReader,
        dependency_registry: _DependencyReader,
        completion_registry: _CompletionReader,
        gate_satisfaction_registry: _GateSatisfactionReader,
    ) -> None:
        self._work_items = work_item_registry
        self._receipts = receipt_registry
        self._instances = workflow_instance_registry
        self._transitions = workflow_transition_registry
        self._stages = workflow_stage_registry
        self._dependencies = dependency_registry
        self._completions = completion_registry
        self._gates = gate_satisfaction_registry

    @staticmethod
    def _visible_work(
        productive_work: LegalProductiveWorkProjection,
    ) -> tuple[
        LegalWorkItem,
        ...,
    ]:
        groups = (
            productive_work.assigned_work_items,
            productive_work.supervised_work_items,
            productive_work.overdue_work_items,
            productive_work.due_soon_work_items,
        )

        by_id: dict[
            str,
            LegalWorkItem,
        ] = {}

        for group in groups:
            for item in group:
                if type(item) is not LegalWorkItem:
                    _fail(
                        LegalSpecialistWorkflowReadServiceError,
                        "P1_PRODUCTIVE_WORK_ITEM_INVALID",
                    )

                existing = by_id.get(
                    item.work_item_id
                )

                if (
                    existing is not None
                    and existing != item
                ):
                    _fail(
                        LegalSpecialistWorkflowReadServiceError,
                        "P1_VISIBLE_WORK_IDENTITY_COLLISION",
                    )

                by_id[
                    item.work_item_id
                ] = item

        return tuple(
            by_id[key]
            for key in sorted(
                by_id
            )
        )

    def _receipt_for_work(
        self,
        *,
        tenant_id: str,
        work_item: LegalWorkItem,
        session: object,
    ) -> LegalTransitionWorkMaterializationReceipt | None:
        receipts = self._receipts.list_matter(
            tenant_id,
            work_item.case_matter_id,
            session=session,
        )

        matches = []

        for receipt in receipts:
            if (
                receipt.tenant_id != tenant_id
                or receipt.case_matter_id
                != work_item.case_matter_id
            ):
                _fail(
                    LegalSpecialistWorkflowReadServiceError,
                    "P1_RECEIPT_SCOPE_MISMATCH",
                )

            matching_outputs = tuple(
                output
                for output in receipt.outputs
                if (
                    output.work_item_id
                    == work_item.work_item_id
                    and output.work_item_fingerprint
                    == work_item.fingerprint
                )
            )

            if matching_outputs:
                if len(matching_outputs) != 1:
                    _fail(
                        LegalSpecialistWorkflowReadServiceError,
                        "P1_RECEIPT_OUTPUT_AMBIGUOUS",
                    )

                matches.append(
                    receipt
                )

        if not matches:
            return None

        if len(matches) != 1:
            _fail(
                LegalSpecialistWorkflowReadServiceError,
                "P1_WORK_MATERIALIZATION_AMBIGUOUS",
            )

        return matches[
            0
        ]

    def _instance_for_receipt(
        self,
        *,
        tenant_id: str,
        receipt: LegalTransitionWorkMaterializationReceipt,
        session: object,
    ) -> LegalMatterWorkflowInstance:
        instances = (
            self._instances.list_matter_instances(
                tenant_id,
                receipt.case_matter_id,
                session=session,
            )
        )

        matches: list[
            LegalMatterWorkflowInstance
        ] = []

        for instance in instances:
            if (
                instance.tenant_id != tenant_id
                or instance.case_matter_id
                != receipt.case_matter_id
            ):
                _fail(
                    LegalSpecialistWorkflowReadServiceError,
                    "P1_WORKFLOW_INSTANCE_SCOPE_MISMATCH",
                )

            history = (
                self._transitions.list_history(
                    tenant_id,
                    instance.workflow_instance_id,
                    session=session,
                )
            )

            transition_matches = tuple(
                transition
                for transition in history
                if (
                    getattr(
                        transition,
                        "transition_id",
                        None,
                    )
                    == receipt.transition_id
                    and getattr(
                        transition,
                        "fingerprint",
                        None,
                    )
                    == receipt.transition_fingerprint
                )
            )

            if len(
                transition_matches
            ) > 1:
                _fail(
                    LegalSpecialistWorkflowReadServiceError,
                    "P1_TRANSITION_CORRELATION_AMBIGUOUS",
                )

            if transition_matches:
                transition = transition_matches[
                    0
                ]

                if (
                    getattr(
                        transition,
                        "workflow_instance_id",
                        None,
                    )
                    != instance.workflow_instance_id
                    or receipt.workflow_definition_id
                    != instance.workflow_definition_id
                ):
                    _fail(
                        LegalSpecialistWorkflowReadServiceError,
                        "P1_TRANSITION_INSTANCE_CORRELATION_INVALID",
                    )

                matches.append(
                    instance
                )

        if len(matches) != 1:
            _fail(
                LegalSpecialistWorkflowReadServiceError,
                (
                    "P1_TRANSITION_CORRELATION_NOT_UNIQUE"
                    if not matches
                    else
                    "P1_WORKFLOW_INSTANCE_AMBIGUOUS"
                ),
            )

        return matches[
            0
        ]

    def _blocking_predecessors(
        self,
        *,
        tenant_id: str,
        as_of: datetime,
        work_item: LegalWorkItem,
        session: object,
    ) -> tuple[str, ...]:
        edges = (
            self._dependencies.list_predecessors(
                tenant_id,
                work_item.work_item_id,
                session=session,
            )
        )

        blocked: set[
            str
        ] = set()

        for edge in edges:
            if (
                edge.tenant_id != tenant_id
                or edge.case_matter_id
                != work_item.case_matter_id
                or edge.successor_work_item_id
                != work_item.work_item_id
                or edge.successor_work_item_fingerprint
                != work_item.fingerprint
            ):
                _fail(
                    LegalSpecialistWorkflowReadServiceError,
                    "P1_DEPENDENCY_SCOPE_MISMATCH",
                )

            predecessor = (
                self._work_items.get_by_id(
                    tenant_id,
                    edge.predecessor_work_item_id,
                    session=session,
                )
            )

            if (
                predecessor.tenant_id
                != tenant_id
                or predecessor.case_matter_id
                != work_item.case_matter_id
                or predecessor.work_item_id
                != edge.predecessor_work_item_id
                or predecessor.fingerprint
                != edge.predecessor_work_item_fingerprint
            ):
                _fail(
                    LegalSpecialistWorkflowReadServiceError,
                    "P1_PREDECESSOR_SCOPE_MISMATCH",
                )

            events = (
                self._completions.list_work_history(
                    tenant_id,
                    predecessor.work_item_id,
                    session=session,
                )
            )

            currentness = (
                project_legal_work_completion_currentness(
                    work_item=predecessor,
                    completion_events=tuple(
                        events
                    ),
                    evaluated_at=as_of,
                )
            )

            state = (
                LegalWorkCompletionCurrentnessState(
                    currentness.state
                )
            )

            if (
                state
                is LegalWorkCompletionCurrentnessState.COMPLETED
            ):
                continue

            if (
                state
                is LegalWorkCompletionCurrentnessState.NOT_COMPLETED
            ):
                blocked.add(
                    predecessor.work_item_id
                )
                continue

            _fail(
                LegalSpecialistWorkflowReadServiceError,
                "P1_PREDECESSOR_COMPLETION_NOT_DECISIVE",
            )

        return tuple(
            sorted(
                blocked
            )
        )

    def _context_for_work(
        self,
        *,
        tenant_id: str,
        as_of: datetime,
        work_item: LegalWorkItem,
        session: object,
    ) -> LegalSpecialistWorkflowContext | None:
        receipt = self._receipt_for_work(
            tenant_id=tenant_id,
            work_item=work_item,
            session=session,
        )

        if receipt is None:
            return None

        instance = self._instance_for_receipt(
            tenant_id=tenant_id,
            receipt=receipt,
            session=session,
        )

        currentness = (
            self._transitions.derive_currentness(
                _currentness_id(
                    tenant_id=tenant_id,
                    workflow_instance_id=
                        instance.workflow_instance_id,
                    as_of=as_of,
                ),
                instance,
                session=session,
            )
        )

        if (
            currentness.tenant_id != tenant_id
            or currentness.case_matter_id
            != work_item.case_matter_id
            or currentness.workflow_instance_id
            != instance.workflow_instance_id
            or currentness.workflow_instance_fingerprint
            != instance.fingerprint
            or currentness.workflow_topology_fingerprint
            != instance.workflow_topology_fingerprint
        ):
            _fail(
                LegalSpecialistWorkflowReadServiceError,
                "P1_WORKFLOW_CURRENTNESS_SCOPE_MISMATCH",
            )

        stage = (
            self._stages.get_by_definition_stage(
                instance.workflow_definition_fingerprint,
                currentness.current_stage_definition_id,
                session=session,
            )
        )

        if (
            stage.workflow_definition_id
            != instance.workflow_definition_id
            or stage.stage_definition_id
            != currentness.current_stage_definition_id
        ):
            _fail(
                LegalSpecialistWorkflowReadServiceError,
                "P1_STAGE_SCOPE_MISMATCH",
            )

        satisfactions = (
            self._gates.list_workflow_stage(
                tenant_id,
                instance.workflow_instance_id,
                stage.stage_definition_id,
                session=session,
            )
        )

        satisfied: set[
            str
        ] = set()

        configured = set(
            stage.completion_gate_references
        )

        for satisfaction in satisfactions:
            if (
                satisfaction.tenant_id
                != tenant_id
                or satisfaction.workflow_instance_id
                != instance.workflow_instance_id
                or satisfaction.source_stage_definition_id
                != stage.stage_definition_id
            ):
                _fail(
                    LegalSpecialistWorkflowReadServiceError,
                    "P1_GATE_SCOPE_MISMATCH",
                )

            if (
                satisfaction.gate_reference
                not in configured
            ):
                _fail(
                    LegalSpecialistWorkflowReadServiceError,
                    "P1_GATE_NOT_CONFIGURED",
                )

            satisfied.add(
                satisfaction.gate_reference
            )

        unsatisfied = tuple(
            sorted(
                configured
                - satisfied
            )
        )

        blocking = (
            self._blocking_predecessors(
                tenant_id=tenant_id,
                as_of=as_of,
                work_item=work_item,
                session=session,
            )
        )

        return LegalSpecialistWorkflowContext(
            tenant_id=tenant_id,
            work_item_id=
                work_item.work_item_id,
            case_matter_id=
                work_item.case_matter_id,
            workflow_instance_id=
                instance.workflow_instance_id,
            workflow_definition_id=
                instance.workflow_definition_id,
            stage_definition_id=
                stage.stage_definition_id,
            blocking_dependency_work_item_ids=
                blocking,
            unsatisfied_gate_references=
                unsatisfied,
            materialization_transition_id=
                receipt.transition_id,
            materialization_receipt_id=
                receipt.receipt_id,
        )

    def project(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        as_of: datetime,
        productive_work: LegalProductiveWorkProjection,
        session: Any,
    ) -> LegalSpecialistWorkflowProjection:
        """
        Read durable workflow explanation and delegate to the pure composer.
        """
        tx = _transaction(
            session
        )

        tenant = _text(
            "tenant_id",
            tenant_id,
        )

        principal = _text(
            "principal_id",
            principal_id,
        )

        moment = _moment(
            as_of
        )

        if type(
            productive_work
        ) is not LegalProductiveWorkProjection:
            _fail(
                LegalSpecialistWorkflowReadServiceError,
                "P1_PRODUCTIVE_WORK_REQUIRED",
            )

        if (
            productive_work.tenant_id
            != tenant
            or productive_work.principal_id
            != principal
        ):
            _fail(
                LegalSpecialistWorkflowReadServiceError,
                "P1_PRODUCTIVE_WORK_SCOPE_MISMATCH",
            )

        if (
            productive_work.as_of
            != as_of
        ):
            _fail(
                LegalSpecialistWorkflowReadServiceError,
                "P1_PRODUCTIVE_WORK_AS_OF_MISMATCH",
            )

        contexts = []

        for work_item in self._visible_work(
            productive_work
        ):
            if (
                work_item.tenant_id
                != tenant
            ):
                _fail(
                    LegalSpecialistWorkflowReadServiceError,
                    "P1_VISIBLE_WORK_TENANT_SCOPE_MISMATCH",
                )

            context = self._context_for_work(
                tenant_id=tenant,
                as_of=moment,
                work_item=work_item,
                session=tx,
            )

            if context is not None:
                contexts.append(
                    context
                )

        return compose_legal_specialist_workflow_projection(
            productive_work=productive_work,
            workflow_contexts=tuple(
                contexts
            ),
        )


PUBLIC_CONTRACT = MappingProxyType(
    {
        "version": VERSION,
        "authority_ceiling":
            "LegalProductiveWorkProjection",
        "creates_authority": False,
        "caller_owned_transaction": True,
        "work_creation_authority": False,
        "assignment_authority": False,
        "supervision_authority": False,
        "completion_authority": False,
        "transition_authority": False,
        "iam_authority": False,
        "financial_authority": False,
    }
)


__all__ = (
    "VERSION",
    "WORKFLOW_CORRELATION_MODEL",
    "PUBLIC_CONTRACT",
    "LegalSpecialistWorkflowReadService",
    "LegalSpecialistWorkflowReadServiceError",
    "LegalSpecialistWorkflowReadServiceTransactionRequiredError",
)

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: legal_specialist_workflow_read_service.py
# VERSION: v1.0.0-P1-LEGAL-SPECIALIST-WORKFLOW-READ-SERVICE
# READ-ONLY DURABLE ORCHESTRATION: YES
# PRODUCTIVE-WORK VISIBILITY CEILING: ABSOLUTE
# WORK-ITEM DIRECT WORKFLOW POINTER: NONE
# MATERIALIZATION CORRELATION: EXACT RECEIPT OUTPUT + TRANSITION
# CURRENT STAGE: DERIVED FROM COMPLETE TRANSITION HISTORY
# DEPENDENCY EDGE != COMPLETION: YES
# DEPENDENCY BLOCKING: CANONICAL COMPLETION CURRENTNESS ONLY
# GATE BLOCKING: CONFIGURATION MINUS POSITIVE SATISFACTION EVIDENCE
# CALLER-OWNED ACTIVE TRANSACTION REQUIRED: YES
# MUTABLE CURRENT POINTER: NONE
# PERSISTENCE AUTHORITY: NONE
# WORK / ASSIGNMENT / SUPERVISION / COMPLETION / TRANSITION AUTHORITY: NONE
# IAM / PROFESSIONAL AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
