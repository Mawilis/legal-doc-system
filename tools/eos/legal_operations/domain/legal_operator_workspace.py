"""WILSY OS Legal Operations law-firm operator workspace projection.

TITLE: WILSY OS Legal Operator Current Workspace Projection
VERSION: v1.0.0-L8-7D11-LEGAL-OPERATOR-WORKSPACE
AUTHORITY: Wilsy OS Legal Operations deterministic read-only composition.
EPITOME: Compose already-certified L8-5 current read models into one coherent
         own-tenant law-firm operator workspace spanning matters, instructions,
         process documents, custody, service attempts, certified executions,
         and Returns of Service without creating new lifecycle or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_operator_workspace.py
COLLABORATION / OWNERSHIP: P1 owns lifecycle facts; P2 owns durable hydration;
                            L8-0 owns current selection; L8-5 owns entity read
                            models. This module owns only graph-coherent operator
                            presentation composition. HTTP/IAM remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG: 2026-09-24 v1.0.0-L8-7D11-LEGAL-OPERATOR-WORKSPACE establishes
           deterministic current workspace composition, exact tenant/type
           validation, complete matter/instruction/document graph checks,
           document custody-chain validation, attempt/execution/return lineage
           checks, deterministic ordering, and a curated browser-safe serializer
           that excludes raw evidence references/fingerprints and all financial
           execution or settlement truth.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Projection exposes only canonical operational fields
                             already present in P1. It introduces no client/person
                             identity, credentials, provider payloads, GPS, AI,
                             payment, or settlement data.
TENANT BOUNDARY: Every L8-5 enumeration binds one explicit tenant and every
                 projected entity is revalidated against that tenant.
AUTHORITY BOUNDARY: Read-only composition. This module cannot authorize, mutate,
                    register, accept, receive, allocate, attempt, serve, return,
                    bill, invoice, pay, execute financially, or settle.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive; this projection
                              contains no payment or settlement state.
TRANSACTION BOUNDARY: Caller-owned session is forwarded unchanged to L8-5.
                      This module never starts, commits, aborts, or retries.
FAIL-CLOSED DECLARATION: Missing graph members, cross-tenant/type drift,
                         malformed custody, attempt/execution/return divergence,
                         partial terminal service evidence, or upstream read-model
                         failure rejects the complete workspace without fallback.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    DocumentCustodyEvent,
    LegalInstruction,
    ProcessDocument,
    ReturnOfService,
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
    ServiceExecutionOutcome,
    validate_custody_event_chain,
)
from tools.eos.legal_operations.domain.legal_operations_read_model import (
    LegalOperationsReadModelError,
    list_entity_read_models,
)


VERSION: Final[str] = "v1.0.0-L8-7D11-LEGAL-OPERATOR-WORKSPACE"
SCHEMA: Final[str] = "WILSY-LEGAL-OPERATOR-WORKSPACE/V1"
VISIBILITY: Final[str] = "LEGAL_OPERATOR_CURRENT_WORKSPACE"


class LegalOperatorWorkspaceError(RuntimeError):
    """Stable fail-closed operator-workspace composition failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalOperatorWorkspaceError(code)
    if cause is None:
        raise error
    raise error from cause


def _values(
    *,
    tenant_id: str,
    entity_type: str,
    expected_type: type[Any],
    lifecycle_collection: Any,
    session: Any,
) -> tuple[Any, ...]:
    """Enumerate one exact tenant/type current class through L8-5 only."""
    try:
        models = list_entity_read_models(
            tenant_id=tenant_id,
            entity_type=entity_type,
            lifecycle_collection=lifecycle_collection,
            session=session,
        )
    except LegalOperationsReadModelError as error:
        _fail("L8_7D11_READ_MODEL_UNAVAILABLE", error)

    values: list[Any] = []
    for model in models:
        if (
            model.tenant_id != tenant_id
            or model.entity_type != entity_type
            or type(model.current) is not expected_type
            or model.current.tenant_id != tenant_id
        ):
            _fail("L8_7D11_READ_MODEL_SCOPE_INVALID")
        values.append(model.current)
    return tuple(values)


@dataclass(frozen=True, slots=True)
class LegalOperatorWorkspaceProjection:
    """One coherent current Legal Operations workspace for a law-firm operator."""

    tenant_id: str
    matters: tuple[CaseMatter, ...]
    instructions: tuple[LegalInstruction, ...]
    documents: tuple[ProcessDocument, ...]
    custody_events: tuple[DocumentCustodyEvent, ...]
    attempts: tuple[ServiceAttempt, ...]
    executions: tuple[ServiceExecution, ...]
    returns: tuple[ReturnOfService, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.tenant_id, str) or not self.tenant_id:
            _fail("L8_7D11_TENANT_INVALID")

        typed = (
            (self.matters, CaseMatter),
            (self.instructions, LegalInstruction),
            (self.documents, ProcessDocument),
            (self.custody_events, DocumentCustodyEvent),
            (self.attempts, ServiceAttempt),
            (self.executions, ServiceExecution),
            (self.returns, ReturnOfService),
        )
        for values, expected in typed:
            if type(values) is not tuple:
                _fail("L8_7D11_COLLECTION_INVALID")
            for value in values:
                if type(value) is not expected or value.tenant_id != self.tenant_id:
                    _fail("L8_7D11_SCOPE_INVALID")

        matter_by_id = {value.case_matter_id: value for value in self.matters}
        document_by_id = {value.document_id: value for value in self.documents}
        instruction_by_id = {value.instruction_id: value for value in self.instructions}
        attempt_by_id = {value.attempt_id: value for value in self.attempts}
        execution_by_id = {
            value.service_execution_id: value for value in self.executions
        }

        if (
            len(matter_by_id) != len(self.matters)
            or len(document_by_id) != len(self.documents)
            or len(instruction_by_id) != len(self.instructions)
            or len(attempt_by_id) != len(self.attempts)
            or len(execution_by_id) != len(self.executions)
        ):
            _fail("L8_7D11_DUPLICATE_IDENTITY")

        for document in self.documents:
            if document.case_matter_id not in matter_by_id:
                _fail("L8_7D11_DOCUMENT_MATTER_MISSING")

        for instruction in self.instructions:
            matter = matter_by_id.get(instruction.case_matter_id)
            document = document_by_id.get(instruction.document_id)
            if (
                matter is None
                or document is None
                or document.case_matter_id != instruction.case_matter_id
            ):
                _fail("L8_7D11_INSTRUCTION_GRAPH_INVALID")

        custody_by_document: dict[str, list[DocumentCustodyEvent]] = {}
        for event in self.custody_events:
            if event.document_id not in document_by_id:
                _fail("L8_7D11_CUSTODY_DOCUMENT_MISSING")
            custody_by_document.setdefault(event.document_id, []).append(event)

        for document in self.documents:
            events = custody_by_document.get(document.document_id)
            if not events:
                _fail("L8_7D11_CUSTODY_REQUIRED")
            events.sort(
                key=lambda value: (
                    value.sequence_number,
                    value.occurred_at,
                    value.custody_event_id,
                )
            )
            try:
                validate_custody_event_chain(tuple(events))
            except Exception as error:
                _fail("L8_7D11_CUSTODY_INVALID", error)

        terminal_states = {
            ServiceAttemptState.COMPLETED,
            ServiceAttemptState.NOT_COMPLETED,
        }
        execution_by_attempt: dict[str, ServiceExecution] = {}
        for execution in self.executions:
            attempt = attempt_by_id.get(execution.attempt_id)
            instruction = instruction_by_id.get(execution.instruction_id)
            document = document_by_id.get(execution.document_id)
            if (
                attempt is None
                or instruction is None
                or document is None
                or attempt.instruction_id != execution.instruction_id
                or attempt.document_id != execution.document_id
                or instruction.document_id != execution.document_id
                or attempt.state not in terminal_states
                or (
                    attempt.state is ServiceAttemptState.COMPLETED
                    and execution.outcome is not ServiceExecutionOutcome.COMPLETED
                )
                or (
                    attempt.state is ServiceAttemptState.NOT_COMPLETED
                    and execution.outcome is not ServiceExecutionOutcome.NOT_COMPLETED
                )
                or execution.attempt_id in execution_by_attempt
            ):
                _fail("L8_7D11_EXECUTION_GRAPH_INVALID")
            execution_by_attempt[execution.attempt_id] = execution

        for attempt in self.attempts:
            instruction = instruction_by_id.get(attempt.instruction_id)
            document = document_by_id.get(attempt.document_id)
            if (
                instruction is None
                or document is None
                or instruction.document_id != attempt.document_id
            ):
                _fail("L8_7D11_ATTEMPT_GRAPH_INVALID")
            if (
                attempt.state in terminal_states
                and attempt.attempt_id not in execution_by_attempt
            ):
                _fail("L8_7D11_TERMINAL_EXECUTION_REQUIRED")

        return_ids: set[str] = set()
        for value in self.returns:
            execution = execution_by_id.get(value.service_execution_id)
            if (
                value.return_id in return_ids
                or execution is None
                or value.attempt_id != execution.attempt_id
                or value.instruction_id != execution.instruction_id
                or value.document_id != execution.document_id
                or value.service_outcome is not execution.outcome
            ):
                _fail("L8_7D11_RETURN_GRAPH_INVALID")
            return_ids.add(value.return_id)

    def to_dict(self) -> dict[str, object]:
        """Serialize only bounded operational presentation fields."""
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "tenant_id": self.tenant_id,
            "visibility": VISIBILITY,
            "matters": [
                {
                    "case_matter_id": value.case_matter_id,
                    "matter_reference": value.matter_reference,
                    "opened_at": value.opened_at.isoformat(),
                    "state": value.state.value,
                }
                for value in self.matters
            ],
            "instructions": [
                {
                    "instruction_id": value.instruction_id,
                    "case_matter_id": value.case_matter_id,
                    "document_id": value.document_id,
                    "registered_at": value.registered_at.isoformat(),
                    "state": value.state.value,
                }
                for value in self.instructions
            ],
            "documents": [
                {
                    "document_id": value.document_id,
                    "case_matter_id": value.case_matter_id,
                    "document_type": value.document_type,
                    "registered_at": value.registered_at.isoformat(),
                    "state": value.state.value,
                }
                for value in self.documents
            ],
            "custody_events": [
                {
                    "custody_event_id": value.custody_event_id,
                    "document_id": value.document_id,
                    "event_type": value.event_type.value,
                    "occurred_at": value.occurred_at.isoformat(),
                    "sequence_number": value.sequence_number,
                    "from_holder_reference": value.from_holder_reference,
                    "to_holder_reference": value.to_holder_reference,
                }
                for value in self.custody_events
            ],
            "attempts": [
                {
                    "attempt_id": value.attempt_id,
                    "instruction_id": value.instruction_id,
                    "document_id": value.document_id,
                    "deputy_id": value.deputy_id,
                    "allocated_at": value.allocated_at.isoformat(),
                    "state": value.state.value,
                }
                for value in self.attempts
            ],
            "executions": [
                {
                    "service_execution_id": value.service_execution_id,
                    "attempt_id": value.attempt_id,
                    "instruction_id": value.instruction_id,
                    "document_id": value.document_id,
                    "outcome": value.outcome.value,
                    "executed_at": value.executed_at.isoformat(),
                }
                for value in self.executions
            ],
            "returns": [
                {
                    "return_id": value.return_id,
                    "instruction_id": value.instruction_id,
                    "document_id": value.document_id,
                    "attempt_id": value.attempt_id,
                    "service_execution_id": value.service_execution_id,
                    "service_outcome": value.service_outcome.value,
                    "generated_at": value.generated_at.isoformat(),
                    "state": value.state.value,
                }
                for value in self.returns
            ],
        }


def get_legal_operator_workspace(
    *,
    tenant_id: str,
    lifecycle_collection: Any,
    session: Any = None,
) -> LegalOperatorWorkspaceProjection:
    """Return one graph-coherent current law-firm operator workspace."""
    matters = cast(
        tuple[CaseMatter, ...],
        _values(
            tenant_id=tenant_id,
            entity_type="CaseMatter",
            expected_type=CaseMatter,
            lifecycle_collection=lifecycle_collection,
            session=session,
        ),
    )
    instructions = cast(
        tuple[LegalInstruction, ...],
        _values(
            tenant_id=tenant_id,
            entity_type="LegalInstruction",
            expected_type=LegalInstruction,
            lifecycle_collection=lifecycle_collection,
            session=session,
        ),
    )
    documents = cast(
        tuple[ProcessDocument, ...],
        _values(
            tenant_id=tenant_id,
            entity_type="ProcessDocument",
            expected_type=ProcessDocument,
            lifecycle_collection=lifecycle_collection,
            session=session,
        ),
    )
    custody_events = cast(
        tuple[DocumentCustodyEvent, ...],
        _values(
            tenant_id=tenant_id,
            entity_type="DocumentCustodyEvent",
            expected_type=DocumentCustodyEvent,
            lifecycle_collection=lifecycle_collection,
            session=session,
        ),
    )
    attempts = cast(
        tuple[ServiceAttempt, ...],
        _values(
            tenant_id=tenant_id,
            entity_type="ServiceAttempt",
            expected_type=ServiceAttempt,
            lifecycle_collection=lifecycle_collection,
            session=session,
        ),
    )
    executions = cast(
        tuple[ServiceExecution, ...],
        _values(
            tenant_id=tenant_id,
            entity_type="ServiceExecution",
            expected_type=ServiceExecution,
            lifecycle_collection=lifecycle_collection,
            session=session,
        ),
    )
    returns = cast(
        tuple[ReturnOfService, ...],
        _values(
            tenant_id=tenant_id,
            entity_type="ReturnOfService",
            expected_type=ReturnOfService,
            lifecycle_collection=lifecycle_collection,
            session=session,
        ),
    )

    ordered_custody = tuple(
        sorted(
            custody_events,
            key=lambda value: (
                value.document_id,
                value.sequence_number,
                value.occurred_at,
                value.custody_event_id,
            ),
        )
    )
    return LegalOperatorWorkspaceProjection(
        tenant_id=tenant_id,
        matters=matters,
        instructions=instructions,
        documents=documents,
        custody_events=ordered_custody,
        attempts=attempts,
        executions=executions,
        returns=returns,
    )


__all__ = [
    "VERSION",
    "SCHEMA",
    "VISIBILITY",
    "LegalOperatorWorkspaceError",
    "LegalOperatorWorkspaceProjection",
    "get_legal_operator_workspace",
]


# ARTIFACT: legal_operator_workspace.py
# VERSION: v1.0.0-L8-7D11-LEGAL-OPERATOR-WORKSPACE
# AUTHORITY BOUNDARY: graph-coherent current operator projection only; no mutation or authorization
# TENANT POSTURE: every source read and projected entity remains exact-tenant scoped
# FAIL-CLOSED POSTURE: partial/divergent/cross-scope lifecycle graphs reject without fallback
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
