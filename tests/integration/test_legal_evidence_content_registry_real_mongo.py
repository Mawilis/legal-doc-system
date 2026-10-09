"""Real-Mongo certificate for durable L10A2 Legal evidence content.

TITLE: WILSY OS Legal Evidence Content Registry Real-Mongo Certificate
VERSION: v1.0.0-L10A2-LEGAL-EVIDENCE-CONTENT-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Physically certify immutable tenant/matter/document-bound Legal
         evidence bytes and metadata against an isolated writable Mongo replica
         set, including transactions, exact replay, byte verification, scope
         isolation, corruption rejection, rollback and concurrent creation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_evidence_content_registry_real_mongo.py
COLLABORATION / OWNERSHIP: L10A1 owns immutable content identity; L10A2 owns
                            durable metadata/raw-byte persistence only. This
                            certificate owns disposable synthetic Mongo evidence.
                            ProcessDocument lifecycle, Court/Court Online, IAM,
                            AI and financial authority remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-29
CHANGELOG: 2026-09-29 v1.0.0-L10A2-LEGAL-EVIDENCE-CONTENT-REGISTRY-REAL-MONGO-CERT
           establishes physical topology, index, transaction, exact replay,
           BSON byte round-trip, tenant/matter/document isolation, corruption,
           rollback, divergence and competing-create evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Uses one UUID-isolated disposable database and only
                             synthetic opaque identities/content. No canonical
                             WILSY tenant documents, credentials or PII are used.
TENANT BOUNDARY: Every operational registry read/write is exercised under exact
                 tenant scope; document listing also binds matter/document.
AUTHORITY BOUNDARY: Physical Legal evidence-content persistence only. No
                    ProcessDocument/custody mutation, Court filing, service,
                    IAM, AI, client visibility or legal sufficiency is created.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Tests own every Mongo session/transaction. L10A2 must not
                      start, commit, abort or retry transactions itself.
FAIL-CLOSED DECLARATION: Replica topology, index metadata, transaction,
                         replay, corruption, isolation, rollback or concurrency
                         failure fails certification. No unavailable-runtime
                         condition is represented as a pass.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import os
from threading import Barrier
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_evidence_content import (
    LEGAL_EVIDENCE_CONTENT_FIELDS,
    LegalEvidenceContent,
    register_legal_evidence_content,
)
from tools.eos.legal_operations.registry import (
    legal_evidence_content_registry as registry,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

NOW = datetime(
    2026,
    9,
    29,
    17,
    30,
    0,
    654321,
    tzinfo=timezone.utc,
)
PDF = b"%PDF-1.7\nL10A2 real Mongo synthetic evidence\n"
SOURCE_FP = hashlib.sha3_512(b"l10a2-real-source").hexdigest()


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Yield one writable certified replica set and UUID-isolated collection."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None

    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(
                f"L10A2_MONGO_UNAVAILABLE:{type(error).__name__}"
            )

        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail("L10A2_WRONG_REPLICA_SET")

        if (
            hello.get(
                "isWritablePrimary",
                hello.get("ismaster"),
            )
            is not True
        ):
            pytest.fail("L10A2_NO_WRITABLE_PRIMARY")

        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.fail("L10A2_SESSIONS_UNAVAILABLE")

        database = client[
            f"wilsy_l10a2_legal_evidence_{uuid.uuid4().hex}"
        ]
        collection = database.get_collection(
            registry.COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )

        registry.ensure_indexes(collection)

        yield client, database, collection
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _value(
    tenant: str,
    *,
    matter: str = "matter-1",
    document: str = "document-1",
    content: bytes = PDF,
    registered_at: datetime = NOW,
    source_reference: str = "partner-upload:l10a2-real",
) -> LegalEvidenceContent:
    """Create one valid synthetic L10A1 value."""
    return register_legal_evidence_content(
        tenant_id=tenant,
        case_matter_id=matter,
        document_id=document,
        media_type="application/pdf",
        original_filename="founding-affidavit.pdf",
        content=content,
        source_evidence_reference=source_reference,
        source_evidence_fingerprint=SOURCE_FP,
        registered_at=registered_at,
    )


def _commit(
    client: MongoClient[Any],
    collection: Any,
    value: LegalEvidenceContent,
    content: bytes,
) -> LegalEvidenceContent:
    """Commit one immutable evidence-content pair in caller transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            return registry.persist_evidence_content(
                value,
                content,
                collection,
                session=session,
            )


def test_real_topology_has_writable_primary_sessions_and_transactions(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Prove the host runtime is the sanctioned writable replica set."""
    client, _, _ = mongo_context
    hello = client.admin.command("hello")

    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert (
        hello.get(
            "isWritablePrimary",
            hello.get("ismaster"),
        )
        is True
    )
    assert hello.get("logicalSessionTimeoutMinutes") is not None


def test_real_index_metadata_is_exact_and_has_no_ttl(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Physically prove exact L10A2 indexes and absence of TTL deletion."""
    _, _, collection = mongo_context

    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
        if item["name"] != "_id_"
    }

    assert set(indexes) == {
        registry.REFERENCE_INDEX_NAME,
        registry.DOCUMENT_INDEX_NAME,
        registry.CONTENT_FINGERPRINT_INDEX_NAME,
    }

    assert dict(
        indexes[registry.REFERENCE_INDEX_NAME]["key"]
    ) == {
        "tenant_id": 1,
        "content_reference": 1,
    }
    assert (
        indexes[registry.REFERENCE_INDEX_NAME].get("unique")
        is True
    )

    assert dict(
        indexes[registry.DOCUMENT_INDEX_NAME]["key"]
    ) == {
        "tenant_id": 1,
        "case_matter_id": 1,
        "document_id": 1,
        "registered_at": -1,
    }
    assert (
        indexes[registry.DOCUMENT_INDEX_NAME].get("unique")
        is not True
    )

    assert dict(
        indexes[
            registry.CONTENT_FINGERPRINT_INDEX_NAME
        ]["key"]
    ) == {
        "tenant_id": 1,
        "document_id": 1,
        "content_fingerprint": 1,
    }

    assert all(
        "expireAfterSeconds" not in item
        for item in indexes.values()
    )


def test_real_commit_exact_replay_and_bson_byte_round_trip(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Prove one immutable row, exact replay and exact raw-byte recovery."""
    client, _, collection = mongo_context
    tenant = f"tenant-replay-{uuid.uuid4().hex}"
    value = _value(tenant)

    first = _commit(
        client,
        collection,
        value,
        PDF,
    )
    replay = _commit(
        client,
        collection,
        value,
        PDF,
    )

    assert first == value
    assert replay == value
    assert collection.count_documents(
        {"tenant_id": tenant}
    ) == 1

    with client.start_session() as session:
        with session.start_transaction():
            resolved = registry.get_evidence_content(
                tenant,
                value.content_reference,
                collection,
                session=session,
            )
            content = registry.read_evidence_content_bytes(
                tenant,
                value.content_reference,
                collection,
                session=session,
            )

    assert resolved == value
    assert content == PDF

    raw = collection.find_one(
        {
            "tenant_id": tenant,
            "content_reference": value.content_reference,
        }
    )
    assert isinstance(raw, dict)
    assert bytes(raw["content_bytes"]) == PDF
    assert raw["content_fingerprint"] == hashlib.sha3_512(
        PDF
    ).hexdigest()


def test_real_active_transaction_abort_and_foreign_tenant_silence(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Prove registry owns no transaction and foreign scope remains absent."""
    client, _, collection = mongo_context
    tenant = f"tenant-abort-{uuid.uuid4().hex}"
    value = _value(tenant)

    with pytest.raises(
        registry.LegalEvidenceContentRegistryTransactionRequiredError
    ):
        registry.persist_evidence_content(
            value,
            PDF,
            collection,
            session=None,
        )

    with client.start_session() as session:
        session.start_transaction()

        registry.persist_evidence_content(
            value,
            PDF,
            collection,
            session=session,
        )

        assert (
            collection.count_documents(
                {"tenant_id": tenant},
                session=session,
            )
            == 1
        )

        session.abort_transaction()

    assert collection.count_documents(
        {"tenant_id": tenant}
    ) == 0

    _commit(
        client,
        collection,
        value,
        PDF,
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.LegalEvidenceContentRegistryNotFoundError
            ):
                registry.get_evidence_content(
                    f"foreign-{uuid.uuid4().hex}",
                    value.content_reference,
                    collection,
                    session=session,
                )


def test_real_byte_and_metadata_corruption_fail_closed(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Prove physical byte and metadata tampering cannot hydrate."""
    client, _, collection = mongo_context
    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    value = _value(tenant)

    _commit(
        client,
        collection,
        value,
        PDF,
    )

    original = deepcopy(
        collection.find_one({"tenant_id": tenant})
    )
    assert isinstance(original, dict)

    collection.update_one(
        {"tenant_id": tenant},
        {
            "$set": {
                "content_bytes": PDF + b"tampered",
            }
        },
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.LegalEvidenceContentRegistryPersistedRecordInvalidError
            ):
                registry.get_evidence_content(
                    tenant,
                    value.content_reference,
                    collection,
                    session=session,
                )

    collection.replace_one(
        {"_id": original["_id"]},
        original,
    )

    collection.update_one(
        {"tenant_id": tenant},
        {
            "$set": {
                "original_filename": "forged.pdf",
            }
        },
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.LegalEvidenceContentRegistryPersistedRecordInvalidError
            ):
                registry.read_evidence_content_bytes(
                    tenant,
                    value.content_reference,
                    collection,
                    session=session,
                )

    collection.replace_one(
        {"_id": original["_id"]},
        original,
    )


def test_real_document_listing_is_exact_scope_and_newest_first(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Prove tenant/matter/document projection cannot bleed across scope."""
    client, _, collection = mongo_context

    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"

    first_bytes = PDF + b"v1"
    second_bytes = PDF + b"v2"
    foreign_bytes = PDF + b"foreign"

    first = _value(
        tenant_a,
        content=first_bytes,
        registered_at=NOW,
        source_reference="upload:first",
    )
    second = _value(
        tenant_a,
        content=second_bytes,
        registered_at=NOW + timedelta(minutes=1),
        source_reference="upload:second",
    )
    foreign = _value(
        tenant_b,
        content=foreign_bytes,
        registered_at=NOW + timedelta(minutes=2),
        source_reference="upload:foreign",
    )

    for item, content in (
        (first, first_bytes),
        (second, second_bytes),
        (foreign, foreign_bytes),
    ):
        _commit(
            client,
            collection,
            item,
            content,
        )

    with client.start_session() as session:
        with session.start_transaction():
            listed = registry.list_document_evidence_contents(
                tenant_a,
                first.case_matter_id,
                first.document_id,
                collection,
                session=session,
            )

            foreign_scope = registry.list_document_evidence_contents(
                tenant_b,
                first.case_matter_id,
                first.document_id,
                collection,
                session=session,
            )

    assert listed == (second, first)
    assert foreign_scope == (foreign,)


def test_real_divergent_same_reference_rejects_without_mutation(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Prove immutable content reference cannot acquire divergent provenance."""
    client, _, collection = mongo_context
    tenant = f"tenant-conflict-{uuid.uuid4().hex}"
    original = _value(tenant)

    _commit(
        client,
        collection,
        original,
        PDF,
    )

    divergent = LegalEvidenceContent(
        tenant_id=original.tenant_id,
        case_matter_id=original.case_matter_id,
        document_id=original.document_id,
        content_reference=original.content_reference,
        media_type=original.media_type,
        original_filename=original.original_filename,
        content_length=original.content_length,
        content_fingerprint=original.content_fingerprint,
        source_evidence_reference="different-provenance",
        source_evidence_fingerprint=(
            original.source_evidence_fingerprint
        ),
        registered_at=original.registered_at,
    )

    before = deepcopy(
        collection.find_one({"tenant_id": tenant})
    )

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            registry.LegalEvidenceContentRegistryConflictError
        ):
            registry.persist_evidence_content(
                divergent,
                PDF,
                collection,
                session=session,
            )

        session.abort_transaction()

    assert collection.count_documents(
        {"tenant_id": tenant}
    ) == 1
    assert collection.find_one(
        {"tenant_id": tenant}
    ) == before


def test_real_competing_same_reference_commits_only_one_binding(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Prove concurrent divergent immutable creation cannot create two truths."""
    client, _, collection = mongo_context
    tenant = f"tenant-race-{uuid.uuid4().hex}"

    base = _value(tenant)

    left = base
    right = LegalEvidenceContent(
        tenant_id=base.tenant_id,
        case_matter_id=base.case_matter_id,
        document_id=base.document_id,
        content_reference=base.content_reference,
        media_type=base.media_type,
        original_filename=base.original_filename,
        content_length=base.content_length,
        content_fingerprint=base.content_fingerprint,
        source_evidence_reference="race:right",
        source_evidence_fingerprint=(
            base.source_evidence_fingerprint
        ),
        registered_at=base.registered_at,
    )

    barrier = Barrier(2)

    def contender(
        item: LegalEvidenceContent,
    ) -> str:
        with client.start_session() as session:
            session.start_transaction()
            barrier.wait()

            try:
                registry.persist_evidence_content(
                    item,
                    PDF,
                    collection,
                    session=session,
                )
                session.commit_transaction()
                return "COMMITTED"

            except (
                registry.LegalEvidenceContentRegistryRetryRequiredError
            ):
                if session.in_transaction:
                    session.abort_transaction()
                return "RETRY_REQUIRED"

            except (
                registry.LegalEvidenceContentRegistryConflictError
            ):
                if session.in_transaction:
                    session.abort_transaction()
                return "CONFLICT"

            except PyMongoError as error:
                if session.in_transaction:
                    session.abort_transaction()
                return type(error).__name__

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(
            pool.map(
                contender,
                (left, right),
            )
        )

    assert outcomes.count("COMMITTED") == 1

    losing = [
        result
        for result in outcomes
        if result != "COMMITTED"
    ]
    assert len(losing) == 1
    assert losing[0] in {
        "RETRY_REQUIRED",
        "CONFLICT",
    }

    assert collection.count_documents(
        {
            "tenant_id": tenant,
            "content_reference": base.content_reference,
        }
    ) == 1


def test_real_row_shape_contains_only_domain_metadata_bytes_and_mongo_id(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Prove persistence adds no lifecycle, Court, IAM or financial truth."""
    client, database, collection = mongo_context
    tenant = f"tenant-shape-{uuid.uuid4().hex}"
    value = _value(tenant)

    _commit(
        client,
        collection,
        value,
        PDF,
    )

    row = collection.find_one(
        {"tenant_id": tenant}
    )
    assert isinstance(row, dict)

    assert set(row) == (
        set(LEGAL_EVIDENCE_CONTENT_FIELDS)
        | {
            "_id",
            "content_bytes",
        }
    )

    forbidden = {
        "instruction_id",
        "custody_event_id",
        "process_document_state",
        "court_online_credentials",
        "court_filing_status",
        "filed_at",
        "accepted_at",
        "judicial_order",
        "legal_permission",
        "ai_authority",
        "invoice_id",
        "payment_id",
        "execution_id",
        "settlement_id",
        "paid",
        "settled",
    }

    assert forbidden.isdisjoint(row)

    assert set(database.list_collection_names()) == {
        registry.COLLECTION
    }


# ARTIFACT: test_legal_evidence_content_registry_real_mongo.py
# VERSION: v1.0.0-L10A2-LEGAL-EVIDENCE-CONTENT-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical immutable Legal evidence metadata/raw-byte persistence evidence only
# TENANT POSTURE: UUID-isolated database with exact tenant/matter/document scoping
# FAIL-CLOSED POSTURE: topology/transaction/replay/corruption/isolation/race failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
