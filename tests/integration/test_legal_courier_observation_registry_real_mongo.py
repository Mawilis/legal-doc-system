"""Real-Mongo certificate for durable Legal courier observation evidence.

TITLE: Legal Operations Courier Observation Registry Real-Mongo Certificate
VERSION: v1.0.0-L8-8B-COURIER-OBSERVATION-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove L8-8B courier observation durability against a writable MongoDB
         replica set using physical indexes, caller-owned transactions, exact
         replay, rollback, tenant isolation, provider-event uniqueness, strict
         corruption rejection and explicit no-TTL posture.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_courier_observation_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Certificate only. L8-8A owns observation semantics;
                            L8-8B owns append-only persistence/read semantics.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-8B-COURIER-OBSERVATION-REGISTRY-REAL-MONGO-CERT
           establishes physical-index/no-TTL proof, transactional durability,
           exact replay, rollback, cross-tenant absence, provider-event
           divergence/uniqueness, persisted corruption rejection and
           non-authority field exclusion against real MongoDB.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants and opaque courier
                             references only; no customer, credential, address,
                             GPS, signature image, document bytes or payment data.
TENANT BOUNDARY: Every certified operational read/write is exact tenant scoped.
AUTHORITY BOUNDARY: Persistence evidence only; provider delivery remains an
                    external observation and cannot create service, return,
                    custody, Court, notification, invoice or financial truth.
TRANSACTION BOUNDARY: Test owns session start/commit/abort. Registry receives
                      one already-active transaction and never owns lifecycle.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive for execution;
                              settlement remains separately evidenced.
FAIL-CLOSED DECLARATION: Mongo availability, index drift, transaction failure,
                         replay divergence, corruption and scope leakage fail
                         the certificate; unavailable infrastructure is not PASS.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_courier_observation import (
    LegalCourierObservationKind,
    create_legal_courier_observation,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    ProcessDocument,
)
from tools.eos.legal_operations.registry.legal_courier_observation_registry import (
    COLLECTION,
    INDEX_TENANT_DOCUMENT_OBSERVED,
    INDEX_TENANT_OBSERVATION,
    INDEX_TENANT_PROVIDER_EVENT,
    INDEX_TENANT_TRACKING_OBSERVED,
    LegalCourierObservationRegistry,
    LegalCourierObservationRegistryConflictError,
    LegalCourierObservationRegistryError,
    ensure_indexes,
)


VERSION = "v1.0.0-L8-8B-COURIER-OBSERVATION-REGISTRY-REAL-MONGO-CERT"

MONGO_URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

BASE = datetime(2026, 10, 12, 5, 0, tzinfo=timezone.utc)
FP = "a" * 128


@pytest.fixture()
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Yield one UUID-isolated majority/journal courier-observation collection."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        retryWrites=True,
    )

    client.admin.command("ping")
    hello = client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS"
    assert hello.get("isWritablePrimary", hello.get("ismaster")) is True

    database = client[
        f"wilsy_l8_8b_courier_{uuid4().hex}"
    ]
    collection = database.get_collection(
        COLLECTION,
        write_concern=WriteConcern("majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    ensure_indexes(collection)

    try:
        yield client, database, collection
    finally:
        client.drop_database(database.name)
        client.close()


def _case_matter(
    *,
    tenant_id: str = "tenant-l8-8b-real-a",
) -> CaseMatter:
    return CaseMatter(
        tenant_id=tenant_id,
        case_matter_id="matter-l8-8b-real",
        matter_reference="MAT-L8-8B-REAL",
        opened_at=BASE,
        evidence_reference="matter-registration-real",
    )


def _process_document(
    *,
    tenant_id: str = "tenant-l8-8b-real-a",
) -> ProcessDocument:
    return ProcessDocument(
        tenant_id=tenant_id,
        document_id="document-l8-8b-real",
        case_matter_id="matter-l8-8b-real",
        document_type="SUMMONS",
        registered_at=BASE + timedelta(minutes=1),
        registration_evidence_reference="document-registration-real",
    )


def _observation(
    *,
    observation_id: str = "obs-l8-8b-real-1",
    provider_event_reference: str = "provider-event-l8-8b-real-1",
    observed_at: datetime | None = None,
):
    return create_legal_courier_observation(
        case_matter=_case_matter(),
        process_document=_process_document(),
        observation_id=observation_id,
        provider_key="provider-alpha",
        tracking_reference="tracking-l8-8b-real",
        provider_event_reference=provider_event_reference,
        event_kind=LegalCourierObservationKind.IN_TRANSIT,
        provider_status="IN_TRANSIT",
        observed_at=observed_at or BASE + timedelta(minutes=2),
        source_evidence_reference="provider-webhook-real",
        source_evidence_fingerprint=FP,
    )


def _index_key(index: dict[str, Any]) -> dict[str, Any]:
    return dict(index["key"])


def test_real_indexes_are_exact_unique_and_have_no_ttl(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context

    indexes = {
        entry["name"]: entry
        for entry in collection.list_indexes()
    }

    observation = indexes[INDEX_TENANT_OBSERVATION]
    provider_event = indexes[INDEX_TENANT_PROVIDER_EVENT]
    document = indexes[INDEX_TENANT_DOCUMENT_OBSERVED]
    tracking = indexes[INDEX_TENANT_TRACKING_OBSERVED]

    assert _index_key(observation) == {
        "tenant_id": 1,
        "observation_id": 1,
    }
    assert observation["unique"] is True

    assert _index_key(provider_event) == {
        "tenant_id": 1,
        "provider_key": 1,
        "provider_event_reference": 1,
    }
    assert provider_event["unique"] is True

    assert _index_key(document) == {
        "tenant_id": 1,
        "case_matter_id": 1,
        "document_id": 1,
        "observed_at": 1,
    }
    assert document.get("unique") is not True

    assert _index_key(tracking) == {
        "tenant_id": 1,
        "provider_key": 1,
        "tracking_reference": 1,
        "observed_at": 1,
    }
    assert tracking.get("unique") is not True

    assert not any(
        "expireAfterSeconds" in entry
        for entry in indexes.values()
    )


def test_real_transaction_create_replay_read_and_cross_tenant_absence(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalCourierObservationRegistry(collection)
    value = _observation()

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )

        first = registry.create_or_replay(value, session=session)
        replay = registry.create_or_replay(value, session=session)
        own = registry.get_by_observation_id(
            tenant_id=value.tenant_id,
            observation_id=value.observation_id,
            session=session,
        )
        foreign = registry.get_by_observation_id(
            tenant_id="tenant-l8-8b-real-neighbor",
            observation_id=value.observation_id,
            session=session,
        )

        session.commit_transaction()

    assert first == value
    assert replay == value
    assert own == value
    assert foreign is None
    assert collection.count_documents(
        {
            "tenant_id": value.tenant_id,
            "observation_id": value.observation_id,
        }
    ) == 1


def test_real_document_history_is_durable_and_chronological(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalCourierObservationRegistry(collection)

    later = _observation(
        observation_id="obs-l8-8b-real-2",
        provider_event_reference="provider-event-l8-8b-real-2",
        observed_at=BASE + timedelta(minutes=4),
    )
    earlier = _observation(
        observation_id="obs-l8-8b-real-1",
        provider_event_reference="provider-event-l8-8b-real-1",
        observed_at=BASE + timedelta(minutes=2),
    )

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        registry.create_or_replay(later, session=session)
        registry.create_or_replay(earlier, session=session)
        session.commit_transaction()

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        history = registry.list_document_observations(
            tenant_id="tenant-l8-8b-real-a",
            case_matter_id="matter-l8-8b-real",
            document_id="document-l8-8b-real",
            session=session,
        )
        session.commit_transaction()

    assert [item.observation_id for item in history] == [
        "obs-l8-8b-real-1",
        "obs-l8-8b-real-2",
    ]


def test_real_abort_leaves_no_observation(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalCourierObservationRegistry(collection)
    value = _observation()

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        registry.create_or_replay(value, session=session)
        assert collection.count_documents(
            {"tenant_id": value.tenant_id},
            session=session,
        ) == 1
        session.abort_transaction()

    assert collection.count_documents(
        {"tenant_id": value.tenant_id}
    ) == 0


def test_real_provider_event_divergence_rejects_without_second_write(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalCourierObservationRegistry(collection)

    first = _observation()
    divergent = _observation(
        observation_id="obs-l8-8b-real-divergent",
        provider_event_reference=first.provider_event_reference,
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
            LegalCourierObservationRegistryConflictError,
            match="L8_8B_DIVERGENT_PROVIDER_EVENT",
        ):
            registry.create_or_replay(divergent, session=session)
        session.abort_transaction()

    assert collection.count_documents(
        {"tenant_id": first.tenant_id}
    ) == 1


def test_real_physical_provider_event_uniqueness(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context
    first = _observation()
    second = _observation(
        observation_id="obs-l8-8b-real-physical-duplicate",
        provider_event_reference=first.provider_event_reference,
    )

    collection.insert_one(first.to_dict())

    with pytest.raises(DuplicateKeyError):
        collection.insert_one(second.to_dict())

    assert collection.count_documents(
        {
            "tenant_id": first.tenant_id,
            "provider_key": first.provider_key,
            "provider_event_reference": first.provider_event_reference,
        }
    ) == 1


def test_real_persisted_corruption_and_authority_injection_reject(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalCourierObservationRegistry(collection)
    value = _observation()

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
            "observation_id": value.observation_id,
        }
    )
    assert pristine is not None

    corrupted = deepcopy(pristine)
    corrupted["service_completed"] = True
    collection.replace_one({"_id": pristine["_id"]}, corrupted)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        with pytest.raises(
            LegalCourierObservationRegistryError,
            match="L8_8B_CORRUPT_OBSERVATION",
        ):
            registry.get_by_observation_id(
                tenant_id=value.tenant_id,
                observation_id=value.observation_id,
                session=session,
            )
        session.abort_transaction()


def test_real_durable_row_contains_no_downstream_authority_fields(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalCourierObservationRegistry(collection)
    value = _observation()

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
            "observation_id": value.observation_id,
        }
    )
    assert row is not None

    forbidden = {
        "service_completed",
        "service_execution_id",
        "return_id",
        "custody_state",
        "invoice_id",
        "payment",
        "paid_state",
        "billing_execution",
        "settlement",
        "court_filing",
        "notification_sent",
    }
    assert not forbidden.intersection(row)


# ARTIFACT: test_legal_courier_observation_registry_real_mongo.py
# VERSION: v1.0.0-L8-8B-COURIER-OBSERVATION-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo persistence certificate only; no provider, lifecycle, Court, notification or financial authority
# TENANT POSTURE: exact tenant-scoped durability, replay, history and absence certified
# TRANSACTION POSTURE: test owns start/commit/abort; registry receives only active caller transactions
# TTL POSTURE: physical Mongo index metadata certifies no TTL deletion index
# FAIL-CLOSED POSTURE: infrastructure, index, transaction, scope, corruption and uniqueness failures fail the certificate
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
