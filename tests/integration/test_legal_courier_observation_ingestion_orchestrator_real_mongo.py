"""Real-Mongo certificate for Legal courier observation ingestion.

TITLE: Legal Operations Courier Observation Ingestion Real-Mongo Certificate
VERSION: v1.0.0-L8-8C-COURIER-OBSERVATION-INGESTION-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify current canonical CaseMatter/ProcessDocument resolution,
         L8-8A normalization and L8-8B append/replay in one caller-owned Mongo
         transaction with real rollback and scope-failure behavior.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_courier_observation_ingestion_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: Certificate only. P1/P2 own lifecycle evidence;
                            L8-0 owns current projection; L8-8A observation
                            semantics; L8-8B durability; L8-8C composition.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-8C-COURIER-OBSERVATION-INGESTION-REAL-MONGO-CERT
           establishes real current-scope resolution, exact replay, transaction
           rollback, missing-document rejection and tenant/matter isolation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenant/database and opaque
                             provider references only; no customer PII/secrets.
TENANT BOUNDARY: Canonical P1 histories and courier persistence are exact tenant
                 scoped; foreign or mismatched scope cannot create evidence.
AUTHORITY BOUNDARY: Correlation/normalization/persistence certificate only;
                    provider observations do not create service, return,
                    notification, Court, billing or financial truth.
TRANSACTION BOUNDARY: Certificate owns start/commit/abort; L8-8C receives one
                      already-active transaction and never owns its lifecycle.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Mongo/runtime, current-history, scope, replay,
                         rollback or persistence failures fail this certificate.
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

from tools.eos.legal_operations.domain.legal_courier_observation import (
    LegalCourierObservationKind,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    ProcessDocument,
)
from tools.eos.legal_operations.orchestration.legal_courier_observation_ingestion_orchestrator import (
    LegalCourierObservationIngestionError,
    ingest_legal_courier_observation,
)
from tools.eos.legal_operations.registry.legal_courier_observation_registry import (
    COLLECTION as COURIER_COLLECTION,
    LegalCourierObservationRegistry,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-8C-COURIER-OBSERVATION-INGESTION-REAL-MONGO-CERT"

MONGO_URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

BASE = datetime(2026, 10, 12, 5, 0, tzinfo=timezone.utc)
FP = "a" * 128


@pytest.fixture()
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any, Any]]:
    """Yield UUID-isolated lifecycle and courier collections on real Mongo."""
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

    database = client[f"wilsy_l8_8c_courier_{uuid4().hex}"]
    lifecycle = database.get_collection(
        "legal_operations_lifecycle_evidence",
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    courier = database.get_collection(
        COURIER_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )

    LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
    LegalCourierObservationRegistry.ensure_indexes(courier)

    try:
        yield client, database, lifecycle, courier
    finally:
        client.drop_database(database.name)
        client.close()


def _matter(
    *,
    tenant_id: str = "tenant-l8-8c-real-a",
    case_matter_id: str = "matter-l8-8c-real",
) -> CaseMatter:
    return CaseMatter(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        matter_reference="MAT-L8-8C-REAL",
        opened_at=BASE,
        evidence_reference="matter-registration-real",
    )


def _document(
    *,
    tenant_id: str = "tenant-l8-8c-real-a",
    case_matter_id: str = "matter-l8-8c-real",
    document_id: str = "document-l8-8c-real",
) -> ProcessDocument:
    return ProcessDocument(
        tenant_id=tenant_id,
        document_id=document_id,
        case_matter_id=case_matter_id,
        document_type="SUMMONS",
        registered_at=BASE + timedelta(minutes=1),
        registration_evidence_reference="document-registration-real",
    )


def _seed(
    lifecycle: Any,
    *,
    matter_value: CaseMatter | None = None,
    document_value: ProcessDocument | None = None,
) -> tuple[CaseMatter, ProcessDocument]:
    matter = matter_value or _matter()
    document = document_value or _document()
    LegalOperationsLifecycleRegistry.create(matter, lifecycle)
    LegalOperationsLifecycleRegistry.create(document, lifecycle)
    return matter, document


def _ingest(
    *,
    lifecycle: Any,
    courier: Any,
    session: Any,
    tenant_id: str = "tenant-l8-8c-real-a",
    case_matter_id: str = "matter-l8-8c-real",
    document_id: str = "document-l8-8c-real",
    observation_id: str = "obs-l8-8c-real-1",
    provider_event_reference: str = "provider-event-l8-8c-real-1",
):
    return ingest_legal_courier_observation(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        document_id=document_id,
        observation_id=observation_id,
        provider_key="provider-alpha",
        tracking_reference="tracking-l8-8c-real",
        provider_event_reference=provider_event_reference,
        event_kind=LegalCourierObservationKind.DELIVERY_REPORTED,
        provider_status="DELIVERED",
        observed_at=BASE + timedelta(minutes=2),
        source_evidence_reference="provider-webhook-real",
        source_evidence_fingerprint=FP,
        lifecycle_collection=lifecycle,
        courier_observation_collection=courier,
        session=session,
    )


def test_real_ingest_resolves_current_scope_and_replays(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    client, _, lifecycle, courier = mongo_context
    matter, document = _seed(lifecycle)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        first = _ingest(
            lifecycle=lifecycle,
            courier=courier,
            session=session,
        )
        replay = _ingest(
            lifecycle=lifecycle,
            courier=courier,
            session=session,
        )
        session.commit_transaction()

    assert first == replay
    assert first.tenant_id == matter.tenant_id
    assert first.case_matter_id == matter.case_matter_id
    assert first.document_id == document.document_id
    assert first.matter_fingerprint == matter.fingerprint
    assert first.document_fingerprint == document.fingerprint
    assert first.event_kind is LegalCourierObservationKind.DELIVERY_REPORTED
    assert courier.count_documents(
        {
            "tenant_id": matter.tenant_id,
            "observation_id": first.observation_id,
        }
    ) == 1


def test_real_ingest_abort_rolls_back_observation_only(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    client, _, lifecycle, courier = mongo_context
    matter, _ = _seed(lifecycle)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        value = _ingest(
            lifecycle=lifecycle,
            courier=courier,
            session=session,
        )
        assert courier.count_documents(
            {
                "tenant_id": matter.tenant_id,
                "observation_id": value.observation_id,
            },
            session=session,
        ) == 1
        session.abort_transaction()

    assert courier.count_documents(
        {"tenant_id": matter.tenant_id}
    ) == 0

    assert LegalOperationsLifecycleRegistry.get_entity_history(
        matter.tenant_id,
        "CaseMatter",
        matter.case_matter_id,
        lifecycle,
    )


def test_real_missing_current_document_rejects_without_write(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    client, _, lifecycle, courier = mongo_context
    matter = _matter()
    LegalOperationsLifecycleRegistry.create(matter, lifecycle)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        with pytest.raises(
            LegalCourierObservationIngestionError,
            match="L8_8C_PROCESS_DOCUMENT_UNAVAILABLE",
        ):
            _ingest(
                lifecycle=lifecycle,
                courier=courier,
                session=session,
            )
        session.abort_transaction()

    assert courier.count_documents({}) == 0


def test_real_foreign_tenant_scope_rejects_without_write(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    client, _, lifecycle, courier = mongo_context
    _seed(lifecycle)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        with pytest.raises(
            LegalCourierObservationIngestionError,
            match="L8_8C_CASE_MATTER_UNAVAILABLE",
        ):
            _ingest(
                lifecycle=lifecycle,
                courier=courier,
                session=session,
                tenant_id="tenant-l8-8c-real-neighbor",
            )
        session.abort_transaction()

    assert courier.count_documents({}) == 0


def test_real_mismatched_document_matter_rejects_without_write(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    client, _, lifecycle, courier = mongo_context
    matter = _matter()
    wrong_document = _document(case_matter_id="matter-l8-8c-other")
    LegalOperationsLifecycleRegistry.create(matter, lifecycle)
    LegalOperationsLifecycleRegistry.create(wrong_document, lifecycle)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        with pytest.raises(
            LegalCourierObservationIngestionError,
            match="L8_8C_PROCESS_DOCUMENT_SCOPE_MISMATCH",
        ):
            _ingest(
                lifecycle=lifecycle,
                courier=courier,
                session=session,
            )
        session.abort_transaction()

    assert courier.count_documents({}) == 0


def test_real_durable_delivery_report_is_observation_not_service_truth(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any],
) -> None:
    client, _, lifecycle, courier = mongo_context
    matter, _ = _seed(lifecycle)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        value = _ingest(
            lifecycle=lifecycle,
            courier=courier,
            session=session,
        )
        session.commit_transaction()

    row = courier.find_one(
        {
            "tenant_id": matter.tenant_id,
            "observation_id": value.observation_id,
        }
    )
    assert row is not None
    assert row["event_kind"] == "DELIVERY_REPORTED"

    forbidden = {
        "service_completed",
        "service_execution_id",
        "return_id",
        "custody_state",
        "court_filing",
        "notification_sent",
        "invoice_id",
        "payment",
        "settlement",
    }
    assert not forbidden.intersection(row)


# ARTIFACT: test_legal_courier_observation_ingestion_orchestrator_real_mongo.py
# VERSION: v1.0.0-L8-8C-COURIER-OBSERVATION-INGESTION-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo composition certificate only; no provider/HTTP/IAM/lifecycle/financial authority
# TENANT POSTURE: current canonical matter/document scope and durable observation are exact tenant scoped
# TRANSACTION POSTURE: test owns start/commit/abort; L8-8C receives one active transaction
# FAIL-CLOSED POSTURE: missing current evidence, foreign scope, matter mismatch and rollback failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
