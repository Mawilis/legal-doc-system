"""Real-Mongo certificate for Legal return-ready notification registry.

TITLE: Legal Operations Return-Ready Notification Registry Real-Mongo Certificate
VERSION: v1.0.0-L8-8F-RETURN-READY-NOTIFICATION-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify physical no-TTL indexes, append-only replay, transaction
         commit/abort, tenant isolation, divergent-return rejection, corruption
         rejection and delivery-authority exclusion against real Mongo.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_return_ready_notification_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Certificate only. L8-8E owns immutable RETURN_READY
                            intent semantics; L8-8F owns durable persistence.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-8F-RETURN-READY-NOTIFICATION-REGISTRY-REAL-MONGO-CERT
           establishes exact physical index metadata, commit/replay/read,
           rollback atomicity, foreign-tenant absence, divergent return replay,
           persisted corruption rejection and absence of delivery-authority fields.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenant/database and opaque
                             identifiers/fingerprints only; no PII or credentials.
TENANT BOUNDARY: Every registry operation and assertion is exact tenant scoped.
AUTHORITY BOUNDARY: Persistence certificate only; no recipient, channel,
                    transport, delivery, lifecycle mutation, Court or finance.
TRANSACTION BOUNDARY: Certificate owns start/commit/abort; registry receives one
                      already-active caller transaction and never owns lifecycle.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Mongo/runtime, corruption, replay, scope or rollback
                         failures fail this certificate.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ReturnOfService,
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
)
from tools.eos.legal_operations.domain.legal_return_ready_notification import (
    create_return_ready_notification,
)
from tools.eos.legal_operations.registry.legal_return_ready_notification_registry import (
    COLLECTION,
    INDEX_TENANT_DOCUMENT_OCCURRED,
    INDEX_TENANT_NOTIFICATION,
    INDEX_TENANT_RETURN,
    LegalReturnReadyNotificationRegistry,
    LegalReturnReadyNotificationRegistryConflictError,
    LegalReturnReadyNotificationRegistryError,
    ensure_indexes,
)


VERSION = "v1.0.0-L8-8F-RETURN-READY-NOTIFICATION-REGISTRY-REAL-MONGO-CERT"

MONGO_URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

BASE = datetime(2026, 10, 12, 5, 0, tzinfo=timezone.utc)
FP = "a" * 128


@pytest.fixture()
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Yield one UUID-isolated majority/journal notification-intent collection."""
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

    database = client[f"wilsy_l8_8f_notify_{uuid4().hex}"]
    collection = database.get_collection(
        COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    ensure_indexes(collection)

    try:
        yield client, database, collection
    finally:
        client.drop_database(database.name)
        client.close()


def canonical_return(
    *,
    return_id: str = "return-real-1",
) -> ReturnOfService:
    allocated = ServiceAttempt(
        tenant_id="tenant-l8-8f-real-a",
        attempt_id="attempt-real-1",
        instruction_id="instruction-real-1",
        document_id="document-real-1",
        deputy_id="deputy-real-1",
        allocated_at=BASE,
        allocation_evidence_reference="allocation-real-1",
    )
    attempted = allocated.transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference="attempt-real-1",
        occurred_at=BASE + timedelta(minutes=1),
    )
    completed = attempted.transition_to(
        ServiceAttemptState.COMPLETED,
        evidence_reference="service-evidence-real-1",
        evidence_fingerprint=FP,
        occurred_at=BASE + timedelta(minutes=2),
    )
    execution = ServiceExecution.from_attempt(
        attempt=completed,
        service_execution_id="execution-real-1",
        executed_at=BASE + timedelta(minutes=3),
    )
    return ReturnOfService.from_service_execution(
        instruction_id="instruction-real-1",
        service_execution=execution,
        return_id=return_id,
        generated_at=BASE + timedelta(minutes=4),
    )


def notice(
    *,
    notification_id: str = "notification-real-1",
    return_id: str = "return-real-1",
):
    return create_return_ready_notification(
        return_of_service=canonical_return(return_id=return_id),
        notification_id=notification_id,
    )


def test_real_indexes_are_exact_unique_and_have_no_ttl(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context
    indexes = {entry["name"]: entry for entry in collection.list_indexes()}

    by_notification = indexes[INDEX_TENANT_NOTIFICATION]
    assert by_notification["key"] == {
        "tenant_id": 1,
        "notification_id": 1,
    }
    assert by_notification["unique"] is True

    by_return = indexes[INDEX_TENANT_RETURN]
    assert by_return["key"] == {
        "tenant_id": 1,
        "return_id": 1,
    }
    assert by_return["unique"] is True

    by_document = indexes[INDEX_TENANT_DOCUMENT_OCCURRED]
    assert by_document["key"] == {
        "tenant_id": 1,
        "document_id": 1,
        "occurred_at": 1,
    }
    assert by_document.get("unique") is not True

    assert all(
        "expireAfterSeconds" not in entry
        for entry in indexes.values()
    )


def test_real_transaction_create_replay_read_and_cross_tenant_absence(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalReturnReadyNotificationRegistry(collection)
    value = notice()

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        first = registry.create_or_replay(value, session=session)
        replay = registry.create_or_replay(value, session=session)
        exact = registry.get_by_notification_id(
            tenant_id=value.tenant_id,
            notification_id=value.notification_id,
            session=session,
        )
        foreign = registry.get_by_notification_id(
            tenant_id="tenant-l8-8f-real-b",
            notification_id=value.notification_id,
            session=session,
        )
        by_return = registry.get_by_return_id(
            tenant_id=value.tenant_id,
            return_id=value.return_id,
            session=session,
        )
        session.commit_transaction()

    assert first == value
    assert replay == value
    assert exact == value
    assert foreign is None
    assert by_return == value
    assert collection.count_documents(
        {
            "tenant_id": value.tenant_id,
            "notification_id": value.notification_id,
        }
    ) == 1


def test_real_abort_leaves_zero_notification(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalReturnReadyNotificationRegistry(collection)
    value = notice()

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        registry.create_or_replay(value, session=session)
        assert collection.count_documents(
            {
                "tenant_id": value.tenant_id,
                "notification_id": value.notification_id,
            },
            session=session,
        ) == 1
        session.abort_transaction()

    assert collection.count_documents({}) == 0


def test_real_divergent_return_identity_rejects_without_second_write(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalReturnReadyNotificationRegistry(collection)

    first = notice()
    second = notice(
        notification_id="notification-real-2",
        return_id="return-real-1",
    )

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        registry.create_or_replay(first, session=session)
        session.commit_transaction()

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        with pytest.raises(
            LegalReturnReadyNotificationRegistryConflictError,
            match="L8_8F_DIVERGENT_RETURN_IDENTITY",
        ):
            registry.create_or_replay(second, session=session)
        session.abort_transaction()

    assert collection.count_documents({}) == 1


def test_real_persisted_corruption_and_delivery_injection_reject(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalReturnReadyNotificationRegistry(collection)
    value = notice()

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        registry.create_or_replay(value, session=session)
        session.commit_transaction()

    pristine = collection.find_one(
        {
            "tenant_id": value.tenant_id,
            "notification_id": value.notification_id,
        }
    )
    assert pristine is not None

    corrupted = deepcopy(pristine)
    corrupted["recipient_email"] = "person@example.invalid"
    collection.replace_one({"_id": pristine["_id"]}, corrupted)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        with pytest.raises(
            LegalReturnReadyNotificationRegistryError,
            match="L8_8F_CORRUPT_NOTIFICATION",
        ):
            registry.get_by_notification_id(
                tenant_id=value.tenant_id,
                notification_id=value.notification_id,
                session=session,
            )
        session.abort_transaction()


def test_real_durable_row_contains_no_delivery_authority_fields(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalReturnReadyNotificationRegistry(collection)
    value = notice()

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        registry.create_or_replay(value, session=session)
        session.commit_transaction()

    row = collection.find_one(
        {
            "tenant_id": value.tenant_id,
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
    }
    assert not forbidden.intersection(row)


# ARTIFACT: test_legal_return_ready_notification_registry_real_mongo.py
# VERSION: v1.0.0-L8-8F-RETURN-READY-NOTIFICATION-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo append-only RETURN_READY intent persistence certificate only
# TENANT POSTURE: exact tenant-scoped commit/replay/read/foreign-absence certified
# TRANSACTION POSTURE: certificate owns start/commit/abort; registry receives active transaction
# DELIVERY POSTURE: no recipient/channel/provider/message/attempt/delivery lifecycle state
# TTL POSTURE: no TTL index certified in physical Mongo metadata
# FAIL-CLOSED POSTURE: corruption, divergence, rollback or Mongo failure rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
