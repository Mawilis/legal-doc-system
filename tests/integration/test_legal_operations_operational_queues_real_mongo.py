"""Host-backed certificate for Legal Operations operational queues.

TITLE: WILSY OS Legal Operations Operational Queue Real-Mongo Certificate
VERSION: v1.0.0-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES-RM-CERT
AUTHORITY: Host-backed certification of evidence-derived L8-5C queue projection.
EPITOME: Prove real-Mongo tenant-scoped office-receipt, deputy-assignment, and
         active-attempt queues from deterministic current lifecycle state only,
         including snapshot-session compatibility, historical supersession,
         tenant isolation, corruption rejection, deterministic ordering, and
         explicit exclusion of unsupported and financial queue truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_operational_queues_real_mongo.py
COLLABORATION / OWNERSHIP: Host certificate for L8-5C only. P1/P2/L8-0/L8-5
                            remain lifecycle, persistence, current-selection,
                            and entity-read authorities. HTTP/IAM and later
                            queue families remain separate bounded gates.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES-RM-CERT
           establishes real replica-set proof for exact state-derived queue
           membership, current-over-history behavior, caller snapshot-session
           propagation, foreign isolation, corrupt P2/L8-5 evidence rejection,
           bounded serialization, and production-version binding.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants and opaque legal
                             identities only; no real customer, provider,
                             credential, secret, geospatial, or payment data.
TENANT BOUNDARY: All writes and queue reads bind exact UUID-isolated tenants;
                 foreign durable evidence is never admitted to local queues.
AUTHORITY BOUNDARY: Certificate and projection only. Queue visibility grants no
                    receipt, assignment, attempt, service, return, billing,
                    invoice, payment, execution, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
TRANSACTION BOUNDARY: The certificate owns its Mongo session/transaction; L8-5C
                      forwards it and never starts, commits, aborts, or retries.
FAIL-CLOSED DECLARATION: Wrong/unavailable Mongo runtime, corrupt evidence,
                         tenant drift, state drift, or unsupported inference
                         fails certification rather than creating queue truth.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import sys
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ProcessDocument,
    ProcessDocumentState,
    ServiceAttempt,
    ServiceAttemptState,
)
from tools.eos.legal_operations.domain.legal_operations_operational_queues import (
    VERSION as PRODUCTION_VERSION,
    LegalOperationsOperationalQueueError,
    get_operational_queues,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 23, 12, 30, tzinfo=timezone.utc)
HEX_A = "a" * 128


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield one verified writable isolated database; runtime failure is fatal."""
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        retryWrites=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(
                f"L8_5C_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_5C_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_5C_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client[f"legal_ops_l8_5c_queues_{uuid.uuid4().hex}"]
        lifecycle = database.get_collection(
            COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        yield {
            "client": client,
            "database": database,
            "lifecycle": lifecycle,
        }
    finally:
        active_error = sys.exc_info()[0] is not None
        try:
            if database is not None:
                try:
                    client.drop_database(database.name)
                except PyMongoError:
                    if not active_error:
                        raise
        finally:
            client.close()


def _document(
    tenant_id: str,
    document_id: str,
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
    tenant_id: str,
    attempt_id: str,
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


def _persist(value: Any, collection: Any, *, session: Any = None) -> None:
    """Persist one exact P1 snapshot through canonical P2."""
    LegalOperationsLifecycleRegistry.create(
        value,
        collection,
        session=session,
    )


def test_real_mongo_exact_state_membership_and_snapshot_session(
    mongo_context: dict[str, Any],
) -> None:
    """Real durable state yields only the three certified queue families."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant = f"tenant-{uuid.uuid4().hex}"

    for value in (
        _document(tenant, "document-z", ProcessDocumentState.RETURNED_TO_CLIENT),
        _document(tenant, "document-b"),
        _document(tenant, "document-c", ProcessDocumentState.RECEIVED),
        _document(tenant, "document-a"),
        _document(tenant, "document-d", ProcessDocumentState.ALLOCATED_TO_DEPUTY),
        _attempt(tenant, "attempt-b"),
        _attempt(tenant, "attempt-a", ServiceAttemptState.ATTEMPTED),
        _attempt(tenant, "attempt-c", ServiceAttemptState.COMPLETED),
        _attempt(tenant, "attempt-d", ServiceAttemptState.NOT_COMPLETED),
        _attempt(tenant, "attempt-e", ServiceAttemptState.CANCELLED),
    ):
        _persist(value, lifecycle)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        queues = get_operational_queues(
            tenant_id=tenant,
            lifecycle_collection=lifecycle,
            session=session,
        )
        session.commit_transaction()

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
    assert set(queues.to_dict()) == {
        "tenant_id",
        "office_receipt",
        "deputy_assignment",
        "active_attempts",
    }


def test_real_mongo_current_state_supersedes_history_and_foreign_scope(
    mongo_context: dict[str, Any],
) -> None:
    """Historical and foreign rows cannot create stale or cross-tenant queues."""
    lifecycle = mongo_context["lifecycle"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    foreign = f"tenant-{uuid.uuid4().hex}"

    registered = _document(tenant, "document-1")
    received = registered.transition_to(
        ProcessDocumentState.RECEIVED,
        evidence_reference="receipt-1",
        occurred_at=NOW + timedelta(minutes=1),
    )
    allocated = _attempt(tenant, "attempt-1")
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
    foreign_document = _document(foreign, "document-foreign")
    foreign_attempt = _attempt(foreign, "attempt-foreign")
    for value in (
        registered,
        received,
        allocated,
        attempted,
        completed,
        foreign_document,
        foreign_attempt,
    ):
        _persist(value, lifecycle)

    local = get_operational_queues(
        tenant_id=tenant,
        lifecycle_collection=lifecycle,
    )
    assert local.office_receipt == ()
    assert [model.entity_identity for model in local.deputy_assignment] == [
        "document-1",
    ]
    assert local.active_attempts == ()
    assert all(
        model.tenant_id == tenant
        for model in local.deputy_assignment
    )

    foreign_queues = get_operational_queues(
        tenant_id=foreign,
        lifecycle_collection=lifecycle,
    )
    assert [model.entity_identity for model in foreign_queues.office_receipt] == [
        "document-foreign",
    ]
    assert [model.entity_identity for model in foreign_queues.active_attempts] == [
        "attempt-foreign",
    ]


def test_real_mongo_corrupt_source_rejects_whole_queue_projection(
    mongo_context: dict[str, Any],
) -> None:
    """Corrupt matching P2 evidence never yields partial operational queues."""
    lifecycle = mongo_context["lifecycle"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    document = _document(tenant, "document-1")
    attempt = _attempt(tenant, "attempt-1")
    _persist(document, lifecycle)
    _persist(attempt, lifecycle)

    result = lifecycle.update_one(
        {
            "tenant_id": tenant,
            "entity_type": "ProcessDocument",
            "entity_identity": "document-1",
        },
        {"$set": {"p1_fingerprint": "f" * 128}},
    )
    assert result.matched_count == 1

    with pytest.raises(LegalOperationsOperationalQueueError) as caught:
        get_operational_queues(
            tenant_id=tenant,
            lifecycle_collection=lifecycle,
        )
    assert caught.value.code == "L8_5C_READ_MODEL_UNAVAILABLE"
    assert caught.value.__cause__ is not None


def test_real_mongo_projection_excludes_unsupported_and_financial_truth(
    mongo_context: dict[str, Any],
) -> None:
    """Serialized queues contain no unsupported queue or financial authority."""
    lifecycle = mongo_context["lifecycle"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    _persist(_document(tenant, "document-1"), lifecycle)
    _persist(_attempt(tenant, "attempt-1"), lifecycle)

    queues = get_operational_queues(
        tenant_id=tenant,
        lifecycle_collection=lifecycle,
    )
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
        "bank_execution",
        "provider_execution",
    ):
        assert forbidden not in serialized

    assert PRODUCTION_VERSION == (
        "v1.0.1-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES"
    )
    assert VERSION == (
        "v1.0.0-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES-RM-CERT"
    )


# ARTIFACT: test_legal_operations_operational_queues_real_mongo.py
# VERSION: v1.0.0-L8-5C-LEGAL-OPERATIONS-OPERATIONAL-QUEUES-RM-CERT
# AUTHORITY BOUNDARY: host-backed L8-5C state-derived queue projection certificate only
# TENANT POSTURE: UUID-isolated exact tenant scope with caller snapshot-session compatibility
# FAIL-CLOSED POSTURE: runtime, corruption, tenant/state drift, and unsupported inference fail
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
