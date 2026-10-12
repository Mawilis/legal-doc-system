"""Real-Mongo certificate for Legal return-ready notification issuance.

TITLE: Legal Operations Return-Ready Notification Issuance Real-Mongo Certificate
VERSION: v1.0.0-L8-8G-RETURN-READY-NOTIFICATION-ISSUANCE-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify exact persisted P2 ReturnOfService resolution, L8-8E derivation
         and L8-8F append/replay in one caller-owned real Mongo transaction,
         including replay, rollback, wrong-type and foreign-scope rejection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_return_ready_notification_issuance_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: Certificate only. P1/P2 own ReturnOfService truth;
                            L8-8E owns notification intent; L8-8F persistence;
                            L8-8G issuance composition.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-8G-RETURN-READY-NOTIFICATION-ISSUANCE-REAL-MONGO-CERT
           establishes durable P2 return seeding, same-transaction issuance,
           exact replay, rollback atomicity, foreign/wrong-type rejection and
           absence of recipient/transport/delivery authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants/databases and opaque
                             identifiers/fingerprints only; no PII or credentials.
TENANT BOUNDARY: Issuance succeeds only when the requested tenant owns the exact
                 P2 ReturnOfService evidence identity.
AUTHORITY BOUNDARY: Host-backed issuance composition certificate only; no
                    recipient/channel/provider/transport, return creation,
                    lifecycle mutation, Court, billing or financial authority.
TRANSACTION BOUNDARY: Certificate owns start/commit/abort. L8-8G receives one
                      already-active transaction and never owns its lifecycle.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Mongo/runtime, missing/wrong-type/foreign/corrupt source,
                         persistence, replay or rollback failure fails certificate.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    ReturnOfService,
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
)
from tools.eos.legal_operations.orchestration.legal_return_ready_notification_issuance_orchestrator import (
    LegalReturnReadyNotificationIssuanceError,
    issue_return_ready_notification,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)
from tools.eos.legal_operations.registry.legal_return_ready_notification_registry import (
    COLLECTION as NOTIFICATION_COLLECTION,
    LegalReturnReadyNotificationRegistry,
)


VERSION = "v1.0.0-L8-8G-RETURN-READY-NOTIFICATION-ISSUANCE-REAL-MONGO-CERT"

MONGO_URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

BASE = datetime(2026, 10, 12, 5, 0, tzinfo=timezone.utc)
FP = "a" * 128


@pytest.fixture()
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any, Any]]:
    """Yield UUID-isolated lifecycle and notification collections on real Mongo."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=10000,
        retryWrites=True,
    )
    client.admin.command("ping")
    hello = client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS"
    assert hello.get("isWritablePrimary", hello.get("ismaster")) is True

    database = client[f"wilsy_l8_8g_notify_{uuid4().hex}"]
    lifecycle = database.get_collection(
        "legal_operations_lifecycle_evidence",
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    notifications = database.get_collection(
        NOTIFICATION_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
    LegalReturnReadyNotificationRegistry.ensure_indexes(notifications)

    try:
        yield client, database, lifecycle, notifications
    finally:
        client.drop_database(database.name)
        client.close()


def _seed_return(
    client: MongoClient[Any],
    lifecycle: Any,
    *,
    tenant_id: str = "tenant-l8-8g-real-a",
    suffix: str = "1",
) -> tuple[ReturnOfService, str]:
    """Persist canonical attempt, execution and return; return P2 evidence identity."""
    allocated = ServiceAttempt(
        tenant_id=tenant_id,
        attempt_id=f"attempt-{suffix}",
        instruction_id=f"instruction-{suffix}",
        document_id=f"document-{suffix}",
        deputy_id=f"deputy-{suffix}",
        allocated_at=BASE,
        allocation_evidence_reference=f"allocation-{suffix}",
    )
    attempted = allocated.transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference=f"attempt-evidence-{suffix}",
        occurred_at=BASE + timedelta(minutes=1),
    )
    terminal = attempted.transition_to(
        ServiceAttemptState.COMPLETED,
        evidence_reference=f"service-evidence-{suffix}",
        evidence_fingerprint=FP,
        occurred_at=BASE + timedelta(minutes=2),
    )
    execution = ServiceExecution.from_attempt(
        attempt=terminal,
        service_execution_id=f"execution-{suffix}",
        executed_at=BASE + timedelta(minutes=3),
    )
    returned = ReturnOfService.from_service_execution(
        instruction_id=terminal.instruction_id,
        service_execution=execution,
        return_id=f"return-{suffix}",
        generated_at=BASE + timedelta(minutes=4),
    )

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        for snapshot in (allocated, attempted, terminal):
            LegalOperationsLifecycleRegistry.create(
                snapshot,
                lifecycle,
                session=session,
            )
        LegalOperationsLifecycleRegistry.create(
            execution,
            lifecycle,
            session=session,
            source_attempt=terminal,
        )
        LegalOperationsLifecycleRegistry.create(
            returned,
            lifecycle,
            session=session,
            source_attempt=terminal,
            source_execution=execution,
        )
        session.commit_transaction()

    row = lifecycle.find_one(
        {
            "tenant_id": tenant_id,
            "entity_type": "ReturnOfService",
            "entity_identity": returned.return_id,
        }
    )
    assert row is not None
    evidence_identity = row["evidence_identity"]
    assert isinstance(evidence_identity, str)
    return returned, evidence_identity


def test_real_issue_resolves_p2_return_and_replays(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    client, _, lifecycle, notifications = mongo_context
    returned, evidence_identity = _seed_return(client, lifecycle)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        first = issue_return_ready_notification(
            tenant_id=returned.tenant_id,
            return_evidence_identity=evidence_identity,
            notification_id="notification-real-1",
            lifecycle_collection=lifecycle,
            notification_collection=notifications,
            session=session,
        )
        replay = issue_return_ready_notification(
            tenant_id=returned.tenant_id,
            return_evidence_identity=evidence_identity,
            notification_id="notification-real-1",
            lifecycle_collection=lifecycle,
            notification_collection=notifications,
            session=session,
        )
        session.commit_transaction()

    assert first == replay
    assert first.return_id == returned.return_id
    assert first.return_fingerprint == returned.fingerprint
    assert notifications.count_documents(
        {
            "tenant_id": returned.tenant_id,
            "notification_id": "notification-real-1",
        }
    ) == 1


def test_real_issue_abort_rolls_back_notification_only(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    client, _, lifecycle, notifications = mongo_context
    returned, evidence_identity = _seed_return(
        client,
        lifecycle,
        suffix="abort",
    )

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        value = issue_return_ready_notification(
            tenant_id=returned.tenant_id,
            return_evidence_identity=evidence_identity,
            notification_id="notification-real-abort",
            lifecycle_collection=lifecycle,
            notification_collection=notifications,
            session=session,
        )
        assert notifications.count_documents(
            {
                "tenant_id": returned.tenant_id,
                "notification_id": value.notification_id,
            },
            session=session,
        ) == 1
        session.abort_transaction()

    assert notifications.count_documents(
        {
            "tenant_id": returned.tenant_id,
            "notification_id": "notification-real-abort",
        }
    ) == 0
    assert lifecycle.count_documents(
        {
            "tenant_id": returned.tenant_id,
            "entity_type": "ReturnOfService",
            "entity_identity": returned.return_id,
        }
    ) == 1


def test_real_foreign_tenant_return_evidence_rejects_without_write(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    client, _, lifecycle, notifications = mongo_context
    _, evidence_identity = _seed_return(client, lifecycle)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        with pytest.raises(
            LegalReturnReadyNotificationIssuanceError,
            match="L8_8G_RETURN_UNAVAILABLE",
        ):
            issue_return_ready_notification(
                tenant_id="tenant-l8-8g-real-b",
                return_evidence_identity=evidence_identity,
                notification_id="notification-real-foreign",
                lifecycle_collection=lifecycle,
                notification_collection=notifications,
                session=session,
            )
        session.abort_transaction()

    assert notifications.count_documents({}) == 0


def test_real_wrong_p2_entity_type_rejects_without_write(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    client, _, lifecycle, notifications = mongo_context
    matter = CaseMatter(
        tenant_id="tenant-l8-8g-real-a",
        case_matter_id="matter-wrong-type",
        matter_reference="MAT-WRONG",
        opened_at=BASE,
        evidence_reference="matter-evidence",
    )
    LegalOperationsLifecycleRegistry.create(matter, lifecycle)
    row = lifecycle.find_one(
        {
            "tenant_id": matter.tenant_id,
            "entity_type": "CaseMatter",
            "entity_identity": matter.case_matter_id,
        }
    )
    assert row is not None
    evidence_identity = row["evidence_identity"]
    assert isinstance(evidence_identity, str)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        with pytest.raises(
            LegalReturnReadyNotificationIssuanceError,
            match="L8_8G_RETURN_TYPE_INVALID",
        ):
            issue_return_ready_notification(
                tenant_id=matter.tenant_id,
                return_evidence_identity=evidence_identity,
                notification_id="notification-real-wrong-type",
                lifecycle_collection=lifecycle,
                notification_collection=notifications,
                session=session,
            )
        session.abort_transaction()

    assert notifications.count_documents({}) == 0


def test_real_durable_row_contains_no_delivery_authority(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    client, _, lifecycle, notifications = mongo_context
    returned, evidence_identity = _seed_return(
        client,
        lifecycle,
        suffix="shape",
    )

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        value = issue_return_ready_notification(
            tenant_id=returned.tenant_id,
            return_evidence_identity=evidence_identity,
            notification_id="notification-real-shape",
            lifecycle_collection=lifecycle,
            notification_collection=notifications,
            session=session,
        )
        session.commit_transaction()

    row = notifications.find_one(
        {
            "tenant_id": returned.tenant_id,
            "notification_id": value.notification_id,
        }
    )
    assert row is not None

    forbidden = {
        "recipient",
        "recipient_id",
        "recipient_email",
        "phone",
        "channel",
        "provider",
        "provider_id",
        "message",
        "message_body",
        "template",
        "attempt_count",
        "last_attempt_at",
        "delivered_at",
        "sent_at",
        "transport_secret",
        "return_created",
        "service_completed",
        "invoice_id",
        "payment",
        "settlement",
    }
    assert not forbidden.intersection(row)


# ARTIFACT: test_legal_return_ready_notification_issuance_orchestrator_real_mongo.py
# VERSION: v1.0.0-L8-8G-RETURN-READY-NOTIFICATION-ISSUANCE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: host-backed exact P2 ReturnOfService -> L8-8E intent -> L8-8F persistence certificate only
# TENANT POSTURE: exact tenant must own exact P2 return evidence identity
# TRANSACTION POSTURE: certificate owns start/commit/abort; issuance receives active transaction
# DELIVERY POSTURE: no recipient/channel/provider/message/transport/delivery authority
# FAIL-CLOSED POSTURE: wrong-type/foreign/missing source, rollback or Mongo failure rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
