"""Evidence-backed operational queues for Legal Operations.

TITLE: WILSY OS Legal Operations Operational Queue Projection
VERSION: v1.0.1-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES
AUTHORITY: Wilsy OS Legal Operations deterministic queue projection.
EPITOME: Derive only those tenant-scoped operational queues whose membership
         is directly proven by canonical L8-5 current lifecycle state, without
         inventing urgency, due dates, distance, billing readiness, ownership,
         priority, service, return, or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_operations_operational_queues.py
COLLABORATION / OWNERSHIP: P1 owns lifecycle facts; P2 owns immutable durable
                            evidence; L8-0 owns current-state selection; L8-5
                            owns entity read models; L8-5C owns queue projection
                            only. HTTP/IAM, search, billing, notifications,
                            Intelligence, and client rendering remain separate
                            bounded gates.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.1-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES
           makes the exported aggregate and queue entrypoint validate canonical
           non-pseudo tenant identity even when every queue is empty; queue
           membership semantics and authority boundaries are unchanged.
           2026-09-23 v1.0.0-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES
           establishes three exact evidence-backed queues: REGISTERED process
           documents awaiting office receipt, RECEIVED process documents
           awaiting deputy allocation, and ALLOCATED/ATTEMPTED service attempts
           with active attempt work. Return-generation, same-day/urgent,
           distance, and billing-readiness queues are deliberately excluded
           because current canonical fields or atomic correlation do not yet
           prove those memberships safely.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Read-only projection of canonical opaque lifecycle
                             evidence; no credentials, raw provider payloads,
                             geospatial expansion, or new person/customer data.
TENANT BOUNDARY: Every source enumeration is exact-tenant scoped through L8-5;
                 every returned model is rechecked against the requested tenant.
AUTHORITY BOUNDARY: Projection only. Queue membership does not authorize
                    receipt, assignment, attempt, service, return generation,
                    billing, invoicing, payment, execution, or settlement.
FINANCIAL AUTHORITY BOUNDARY: No queue is financial truth or payment authority;
                              Kennel EOS exclusively owns financial execution
                              and settlement.
TRANSACTION BOUNDARY: Caller-owned sessions are forwarded unchanged to L8-5.
                      This module starts, commits, aborts, and retries nothing.
                      No cross-entity absence is used as queue truth.
FAIL-CLOSED DECLARATION: Read-model failure, type drift, tenant drift, or
                         unsupported current-state evidence rejects without
                         fallback, guessed queue membership, or partial output.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ProcessDocument,
    ProcessDocumentState,
    ServiceAttempt,
    ServiceAttemptState,
)
from tools.eos.legal_operations.domain.legal_operations_read_model import (
    LegalOperationsEntityReadModel,
    LegalOperationsReadModelError,
    list_entity_read_models,
)


VERSION: Final[str] = "v1.0.1-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})


class LegalOperationsOperationalQueueError(RuntimeError):
    """Stable L8-5C queue-projection failure with no mutation authority."""

    def __init__(self, code: str) -> None:
        """Create one bounded queue failure code without exposing internals."""
        self.code = code
        super().__init__(code)


def _fail(
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one stable queue-projection error while retaining root cause."""
    error = LegalOperationsOperationalQueueError(code)
    if cause is None:
        raise error
    raise error from cause


def _tenant(value: object) -> str:
    """Require one canonical explicit tenant even for an empty queue result."""
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        _fail("L8_5C_TENANT_INVALID")
    tenant_id = cast(str, value)
    if tenant_id.casefold() in _FORBIDDEN_TENANTS:
        _fail("L8_5C_TENANT_INVALID")
    return tenant_id


def _validate_tenant(
    tenant_id: str,
    models: tuple[LegalOperationsEntityReadModel, ...],
) -> None:
    """Require canonical tenant scope and every model to remain inside it."""
    tenant = _tenant(tenant_id)
    if any(model.tenant_id != tenant for model in models):
        _fail("L8_5C_TENANT_MISMATCH")


def _process_document_queues(
    tenant_id: str,
    models: tuple[LegalOperationsEntityReadModel, ...],
) -> tuple[
    tuple[LegalOperationsEntityReadModel, ...],
    tuple[LegalOperationsEntityReadModel, ...],
]:
    """Partition document models using only canonical current lifecycle state."""
    _validate_tenant(tenant_id, models)
    office_receipt: list[LegalOperationsEntityReadModel] = []
    deputy_assignment: list[LegalOperationsEntityReadModel] = []
    for model in models:
        if model.entity_type != "ProcessDocument" or type(model.current) is not ProcessDocument:
            _fail("L8_5C_DOCUMENT_MODEL_INVALID")
        current = cast(ProcessDocument, model.current)
        if current.state is ProcessDocumentState.REGISTERED:
            office_receipt.append(model)
        elif current.state is ProcessDocumentState.RECEIVED:
            deputy_assignment.append(model)
        elif current.state in {
            ProcessDocumentState.ALLOCATED_TO_DEPUTY,
            ProcessDocumentState.RETURNED_TO_CLIENT,
        }:
            continue
        else:
            _fail("L8_5C_DOCUMENT_STATE_UNSUPPORTED")
    return tuple(office_receipt), tuple(deputy_assignment)


def _active_attempt_queue(
    tenant_id: str,
    models: tuple[LegalOperationsEntityReadModel, ...],
) -> tuple[LegalOperationsEntityReadModel, ...]:
    """Select active attempt work from explicit ALLOCATED/ATTEMPTED state only."""
    _validate_tenant(tenant_id, models)
    active: list[LegalOperationsEntityReadModel] = []
    for model in models:
        if model.entity_type != "ServiceAttempt" or type(model.current) is not ServiceAttempt:
            _fail("L8_5C_ATTEMPT_MODEL_INVALID")
        current = cast(ServiceAttempt, model.current)
        if current.state in {
            ServiceAttemptState.ALLOCATED,
            ServiceAttemptState.ATTEMPTED,
        }:
            active.append(model)
        elif current.state in {
            ServiceAttemptState.COMPLETED,
            ServiceAttemptState.NOT_COMPLETED,
            ServiceAttemptState.CANCELLED,
        }:
            continue
        else:
            _fail("L8_5C_ATTEMPT_STATE_UNSUPPORTED")
    return tuple(active)


@dataclass(frozen=True, slots=True)
class LegalOperationsOperationalQueues:
    """Immutable evidence-backed L8-5C operational queue projection.

    office_receipt contains only current REGISTERED ProcessDocument models.
    deputy_assignment contains only current RECEIVED ProcessDocument models.
    active_attempts contains only current ALLOCATED or ATTEMPTED
    ServiceAttempt models. Empty queues are valid.

    The projection deliberately contains no urgent/same-day, distance,
    billing-readiness, return-generation, priority, SLA, due-date, or inferred
    ownership queue because current canonical evidence does not yet prove those
    memberships safely. Queue presence never grants command or financial
    authority.
    """

    tenant_id: str
    office_receipt: tuple[LegalOperationsEntityReadModel, ...]
    deputy_assignment: tuple[LegalOperationsEntityReadModel, ...]
    active_attempts: tuple[LegalOperationsEntityReadModel, ...]

    def __post_init__(self) -> None:
        """Revalidate tenant/type/state membership for every projected queue."""
        documents = self.office_receipt + self.deputy_assignment
        _validate_tenant(self.tenant_id, documents + self.active_attempts)
        for model in self.office_receipt:
            if model.entity_type != "ProcessDocument" or type(model.current) is not ProcessDocument:
                _fail("L8_5C_DOCUMENT_MODEL_INVALID")
            if cast(ProcessDocument, model.current).state is not ProcessDocumentState.REGISTERED:
                _fail("L8_5C_OFFICE_RECEIPT_MEMBERSHIP_INVALID")
        for model in self.deputy_assignment:
            if model.entity_type != "ProcessDocument" or type(model.current) is not ProcessDocument:
                _fail("L8_5C_DOCUMENT_MODEL_INVALID")
            if cast(ProcessDocument, model.current).state is not ProcessDocumentState.RECEIVED:
                _fail("L8_5C_DEPUTY_ASSIGNMENT_MEMBERSHIP_INVALID")
        for model in self.active_attempts:
            if model.entity_type != "ServiceAttempt" or type(model.current) is not ServiceAttempt:
                _fail("L8_5C_ATTEMPT_MODEL_INVALID")
            if cast(ServiceAttempt, model.current).state not in {
                ServiceAttemptState.ALLOCATED,
                ServiceAttemptState.ATTEMPTED,
            }:
                _fail("L8_5C_ACTIVE_ATTEMPT_MEMBERSHIP_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Serialize canonical read models without inventing additional fields."""
        return {
            "tenant_id": self.tenant_id,
            "office_receipt": [model.to_dict() for model in self.office_receipt],
            "deputy_assignment": [
                model.to_dict() for model in self.deputy_assignment
            ],
            "active_attempts": [model.to_dict() for model in self.active_attempts],
        }


def get_operational_queues(
    *,
    tenant_id: str,
    lifecycle_collection: Any,
    session: Any = None,
) -> LegalOperationsOperationalQueues:
    """Return the first evidence-backed operational queues for one tenant.

    L8-5 enumerates deterministic current-plus-history models for
    ProcessDocument and ServiceAttempt while preserving the caller-owned
    session. L8-5C then applies only exact canonical current-state predicates:

    * REGISTERED ProcessDocument -> office receipt queue;
    * RECEIVED ProcessDocument -> deputy assignment queue;
    * ALLOCATED/ATTEMPTED ServiceAttempt -> active attempt queue.

    No cross-entity absence, time arithmetic, SLA, urgency, distance, billing,
    return, assignment-authority, custody-holder, or financial inference is
    performed. Any upstream read-model failure rejects the whole projection.
    """
    tenant = _tenant(tenant_id)
    try:
        documents = list_entity_read_models(
            tenant_id=tenant,
            entity_type="ProcessDocument",
            lifecycle_collection=lifecycle_collection,
            session=session,
        )
        attempts = list_entity_read_models(
            tenant_id=tenant,
            entity_type="ServiceAttempt",
            lifecycle_collection=lifecycle_collection,
            session=session,
        )
    except LegalOperationsReadModelError as error:
        _fail("L8_5C_READ_MODEL_UNAVAILABLE", error)

    office_receipt, deputy_assignment = _process_document_queues(
        tenant,
        documents,
    )
    active_attempts = _active_attempt_queue(
        tenant,
        attempts,
    )
    return LegalOperationsOperationalQueues(
        tenant_id=tenant,
        office_receipt=office_receipt,
        deputy_assignment=deputy_assignment,
        active_attempts=active_attempts,
    )


__all__ = [
    "VERSION",
    "LegalOperationsOperationalQueueError",
    "LegalOperationsOperationalQueues",
    "get_operational_queues",
]


# ARTIFACT: legal_operations_operational_queues.py
# VERSION: v1.0.1-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES
# AUTHORITY BOUNDARY: deterministic evidence-backed queue projection only; no command or financial authority
# TENANT POSTURE: exact L8-5 tenant-scoped ProcessDocument and ServiceAttempt models only
# FAIL-CLOSED POSTURE: read-model/type/tenant/state drift rejects without guessed or partial queue truth
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
