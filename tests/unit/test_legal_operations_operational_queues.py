"""Direct certificate for Legal Operations evidence-backed queues.

TITLE: WILSY OS Legal Operations Operational Queue Projection Certificate
VERSION: v1.0.1-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES-CERT
AUTHORITY: Direct adversarial certification of L8-5C queue projection.
EPITOME: Prove that operational queue membership is derived only from exact
         canonical current lifecycle state, preserves tenant/session scope,
         ignores superseded historical states, fails closed on corrupt read
         evidence, and does not invent urgency, distance, billing, return,
         ownership, priority, service, or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_operations_operational_queues.py
COLLABORATION / OWNERSHIP: Certificate for the L8-5C queue projection only.
                            P1/P2/L8-0/L8-5 remain canonical lifecycle,
                            persistence, current-selection, and entity-read
                            authorities. HTTP/IAM and later queue families
                            remain separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.1-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES-CERT
           adds direct rejection of pseudo-tenant scope for both an empty
           public aggregate and the queue entrypoint before any persistence read.
           2026-09-23 v1.0.0-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES-CERT
           establishes direct proofs for REGISTERED document office-receipt
           membership, RECEIVED document deputy-assignment membership,
           ALLOCATED/ATTEMPTED active-attempt membership, historical
           supersession, deterministic ordering, tenant/session isolation,
           corruption translation, aggregate self-validation, and explicit
           exclusion of unsupported queue truth.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identities only; no provider,
                             credential, secret, customer, geospatial, or
                             financial data access.
TENANT BOUNDARY: Every durable row and queue read is explicitly tenant-scoped;
                 foreign evidence is represented only by absence.
AUTHORITY BOUNDARY: Certificate only. Queue membership grants no receipt,
                    allocation, attempt, service, return, billing, invoice,
                    payment, execution, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
TRANSACTION BOUNDARY: Caller-owned session markers are forwarded through L8-5;
                      no test helper starts, commits, aborts, or retries.
FAIL-CLOSED DECLARATION: Corrupt evidence, type drift, tenant drift, invalid
                         queue membership, or unsupported inference fails.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import fields
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ProcessDocument,
    ProcessDocumentState,
    ServiceAttempt,
    ServiceAttemptState,
)
from tools.eos.legal_operations.domain.legal_operations_operational_queues import (
    VERSION as PRODUCTION_VERSION,
    LegalOperationsOperationalQueueError,
    LegalOperationsOperationalQueues,
    get_operational_queues,
)
from tools.eos.legal_operations.domain.legal_operations_read_model import (
    get_entity_read_model,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.1-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES-CERT"
NOW = datetime(2026, 9, 23, 12, 0, tzinfo=timezone.utc)
TENANT = "tenant-l8-5c"
FOREIGN = "tenant-l8-5c-foreign"
HEX_A = "a" * 128


class FakeSession:
    """Opaque caller-owned session marker used only for propagation proof."""


def _lookup(document: dict[str, Any], key: str) -> Any:
    """Resolve a Mongo-style dotted key inside one fake durable row."""
    value: Any = document
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


class FakeCollection:
    """Minimal Mongo-compatible collection preserving exact read/session scope."""

    def __init__(self) -> None:
        self.docs: list[dict[str, Any]] = []
        self.calls: list[tuple[str, object, dict[str, object]]] = []

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> dict[str, Any] | None:
        """Return the first exact match while recording caller session."""
        self.calls.append(("find_one", session, deepcopy(query)))
        for document in self.docs:
            if all(_lookup(document, key) == value for key, value in query.items()):
                return deepcopy(document)
        return None

    def find(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> list[dict[str, Any]]:
        """Return all exact matches while recording caller session."""
        self.calls.append(("find", session, deepcopy(query)))
        return [
            deepcopy(document)
            for document in self.docs
            if all(_lookup(document, key) == value for key, value in query.items())
        ]

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object = None,
    ) -> object:
        """Persist one immutable fake P2 row without extra semantics."""
        self.calls.append(("insert_one", session, deepcopy(document)))
        self.docs.append(deepcopy(cast(dict[str, Any], document)))
        return object()


def _document(
    document_id: str,
    *,
    tenant_id: str = TENANT,
    state: ProcessDocumentState = ProcessDocumentState.REGISTERED,
) -> ProcessDocument:
    """Build one canonical process document in an explicit reachable state."""
    suffix = document_id.rsplit("-", 1)[-1]
    value = ProcessDocument(
        tenant_id=tenant_id,
        document_id=document_id,
        case_matter_id=f"matter-{suffix}",
        document_type="summons",
        registered_at=NOW,
        registration_evidence_reference=f"registration-{suffix}",
    )
    if state is ProcessDocumentState.REGISTERED:
        return value
    value = value.transition_to(
        ProcessDocumentState.RECEIVED,
        evidence_reference=f"receipt-{suffix}",
        occurred_at=NOW + timedelta(minutes=1),
    )
    if state is ProcessDocumentState.RECEIVED:
        return value
    value = value.transition_to(
        ProcessDocumentState.ALLOCATED_TO_DEPUTY,
        evidence_reference=f"allocation-{suffix}",
        occurred_at=NOW + timedelta(minutes=2),
    )
    if state is ProcessDocumentState.ALLOCATED_TO_DEPUTY:
        return value
    if state is ProcessDocumentState.RETURNED_TO_CLIENT:
        return value.transition_to(
            ProcessDocumentState.RETURNED_TO_CLIENT,
            evidence_reference=f"returned-{suffix}",
            occurred_at=NOW + timedelta(minutes=3),
        )
    raise AssertionError("unsupported test document state")


def _attempt(
    attempt_id: str,
    *,
    tenant_id: str = TENANT,
    state: ServiceAttemptState = ServiceAttemptState.ALLOCATED,
) -> ServiceAttempt:
    """Build one canonical service attempt in an explicit reachable state."""
    suffix = attempt_id.rsplit("-", 1)[-1]
    value = ServiceAttempt(
        tenant_id=tenant_id,
        attempt_id=attempt_id,
        instruction_id=f"instruction-{suffix}",
        document_id=f"document-{suffix}",
        deputy_id=f"deputy-{suffix}",
        allocated_at=NOW,
        allocation_evidence_reference=f"allocation-{suffix}",
    )
    if state is ServiceAttemptState.ALLOCATED:
        return value
    if state is ServiceAttemptState.CANCELLED:
        return value.transition_to(
            ServiceAttemptState.CANCELLED,
            evidence_reference=f"cancelled-{suffix}",
            occurred_at=NOW + timedelta(minutes=1),
        )
    value = value.transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference=f"attempted-{suffix}",
        occurred_at=NOW + timedelta(minutes=1),
    )
    if state is ServiceAttemptState.ATTEMPTED:
        return value
    if state in {
        ServiceAttemptState.COMPLETED,
        ServiceAttemptState.NOT_COMPLETED,
    }:
        return value.transition_to(
            state,
            evidence_reference=f"terminal-{suffix}",
            evidence_fingerprint=HEX_A,
            occurred_at=NOW + timedelta(minutes=2),
        )
    raise AssertionError("unsupported test attempt state")


def _persist(value: object, collection: FakeCollection, *, session: object = None) -> None:
    """Persist one canonical P1 snapshot through the real P2 registry."""
    LegalOperationsLifecycleRegistry.create(
        cast(Any, value),
        collection,
        session=session,
    )


def _expect(code: str, operation: Any) -> None:
    """Assert one stable L8-5C failure code."""
    with pytest.raises(LegalOperationsOperationalQueueError) as caught:
        operation()
    assert caught.value.code == code
    assert str(caught.value) == code


def test_exact_current_state_membership_is_deterministic_and_non_inventing() -> None:
    """Only direct canonical current-state predicates create queue membership."""
    collection = FakeCollection()
    values = (
        _document("document-z", state=ProcessDocumentState.RETURNED_TO_CLIENT),
        _document("document-b"),
        _document("document-c", state=ProcessDocumentState.RECEIVED),
        _document("document-a"),
        _document("document-d", state=ProcessDocumentState.ALLOCATED_TO_DEPUTY),
        _attempt("attempt-b"),
        _attempt("attempt-a", state=ServiceAttemptState.ATTEMPTED),
        _attempt("attempt-c", state=ServiceAttemptState.COMPLETED),
        _attempt("attempt-d", state=ServiceAttemptState.NOT_COMPLETED),
        _attempt("attempt-e", state=ServiceAttemptState.CANCELLED),
    )
    for value in values:
        _persist(value, collection)

    queues = get_operational_queues(
        tenant_id=TENANT,
        lifecycle_collection=collection,
    )

    assert [model.entity_identity for model in queues.office_receipt] == [
        "document-a",
        "document-b",
    ]
    assert [model.entity_identity for model in queues.deputy_assignment] == [
        "document-c",
    ]
    assert [model.entity_identity for model in queues.active_attempts] == [
        "attempt-a",
        "attempt-b",
    ]
    payload = queues.to_dict()
    assert set(payload) == {
        "tenant_id",
        "office_receipt",
        "deputy_assignment",
        "active_attempts",
    }
    serialized = str(payload).casefold()
    for forbidden in (
        "same_day",
        "urgent",
        "distance",
        "billing_readiness",
        "return_generation",
        "payment",
        "settlement",
        "invoice",
    ):
        assert forbidden not in serialized


def test_superseded_historical_states_do_not_remain_in_queues() -> None:
    """Queue membership follows L8-0 current truth, never any historical snapshot."""
    collection = FakeCollection()
    registered = _document("document-1")
    received = registered.transition_to(
        ProcessDocumentState.RECEIVED,
        evidence_reference="receipt-1",
        occurred_at=NOW + timedelta(minutes=1),
    )
    allocated = _attempt("attempt-1")
    attempted = allocated.transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference="attempted-1",
        occurred_at=NOW + timedelta(minutes=1),
    )
    completed = attempted.transition_to(
        ServiceAttemptState.COMPLETED,
        evidence_reference="completed-1",
        evidence_fingerprint=HEX_A,
        occurred_at=NOW + timedelta(minutes=2),
    )
    for value in (registered, received, allocated, attempted, completed):
        _persist(value, collection)

    queues = get_operational_queues(
        tenant_id=TENANT,
        lifecycle_collection=collection,
    )

    assert queues.office_receipt == ()
    assert [model.entity_identity for model in queues.deputy_assignment] == [
        "document-1",
    ]
    assert queues.active_attempts == ()


def test_tenant_isolation_and_caller_session_propagate_to_both_enumerations() -> None:
    """Both source enumerations remain exact-tenant and caller-session bound."""
    collection = FakeCollection()
    session = FakeSession()
    _persist(_document("document-own"), collection, session=session)
    _persist(_attempt("attempt-own"), collection, session=session)
    _persist(_document("document-foreign", tenant_id=FOREIGN), collection)
    _persist(_attempt("attempt-foreign", tenant_id=FOREIGN), collection)
    collection.calls.clear()

    queues = get_operational_queues(
        tenant_id=TENANT,
        lifecycle_collection=collection,
        session=session,
    )

    assert [model.entity_identity for model in queues.office_receipt] == [
        "document-own",
    ]
    assert [model.entity_identity for model in queues.active_attempts] == [
        "attempt-own",
    ]
    assert collection.calls == [
        (
            "find",
            session,
            {
                "tenant_id": TENANT,
                "entity_type": "ProcessDocument",
            },
        ),
        (
            "find",
            session,
            {
                "tenant_id": TENANT,
                "entity_type": "ServiceAttempt",
            },
        ),
    ]


def test_empty_aggregate_and_entrypoint_reject_pseudo_tenant_before_read() -> None:
    """Pseudo/global tenant scope rejects even when every queue would be empty."""
    collection = FakeCollection()

    _expect(
        "L8_5C_TENANT_INVALID",
        lambda: LegalOperationsOperationalQueues(
            tenant_id="global",
            office_receipt=(),
            deputy_assignment=(),
            active_attempts=(),
        ),
    )
    _expect(
        "L8_5C_TENANT_INVALID",
        lambda: get_operational_queues(
            tenant_id="global",
            lifecycle_collection=collection,
        ),
    )
    assert collection.calls == []


def test_corrupt_l8_5_source_fails_whole_projection_without_partial_queue() -> None:
    """P2/L8-5 corruption is translated once and no partial queue is returned."""
    collection = FakeCollection()
    _persist(_document("document-1"), collection)
    _persist(_attempt("attempt-1"), collection)
    document_row = next(
        row for row in collection.docs if row["entity_type"] == "ProcessDocument"
    )
    document_row["p1_fingerprint"] = "f" * 128

    with pytest.raises(LegalOperationsOperationalQueueError) as caught:
        get_operational_queues(
            tenant_id=TENANT,
            lifecycle_collection=collection,
        )

    assert caught.value.code == "L8_5C_READ_MODEL_UNAVAILABLE"
    assert caught.value.__cause__ is not None


def test_aggregate_constructor_rejects_wrong_queue_membership() -> None:
    """Public queue aggregate revalidates membership instead of trusting callers."""
    collection = FakeCollection()
    _persist(_document("document-1"), collection)
    model = get_entity_read_model(
        tenant_id=TENANT,
        entity_type="ProcessDocument",
        entity_identity="document-1",
        lifecycle_collection=collection,
    )

    _expect(
        "L8_5C_DEPUTY_ASSIGNMENT_MEMBERSHIP_INVALID",
        lambda: LegalOperationsOperationalQueues(
            tenant_id=TENANT,
            office_receipt=(),
            deputy_assignment=(model,),
            active_attempts=(),
        ),
    )


def test_public_shape_and_version_exclude_unsupported_queue_authority() -> None:
    """L8-5C exposes only the three evidence-backed queue families."""
    assert PRODUCTION_VERSION == (
        "v1.0.1-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES"
    )
    assert VERSION == (
        "v1.0.1-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES-CERT"
    )
    assert {field.name for field in fields(LegalOperationsOperationalQueues)} == {
        "tenant_id",
        "office_receipt",
        "deputy_assignment",
        "active_attempts",
    }
    documentation = (get_operational_queues.__doc__ or "").casefold()
    for required_exclusion in (
        "urgency",
        "distance",
        "billing",
        "return",
        "financial",
    ):
        assert required_exclusion in documentation


# ARTIFACT: test_legal_operations_operational_queues.py
# VERSION: v1.0.1-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES-CERT
# AUTHORITY BOUNDARY: direct L8-5C state-derived queue projection certificate only
# TENANT POSTURE: exact tenant/session-scoped ProcessDocument and ServiceAttempt evidence
# FAIL-CLOSED POSTURE: corruption, drift, invalid membership, and unsupported inference reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
