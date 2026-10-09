"""Real-Mongo certificate for metadata-only Legal Evidence object persistence.

TITLE: Legal Evidence Object Metadata Registry Real-Mongo Certificate
VERSION: v1.1.0-L10A2R-C2R1-PROVIDER-OBJECT-LOOKUP-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Physically prove on one disposable Mongo replica-set database that C2
    persists immutable C1 LegalEvidenceObjectMetadata only, with exact tenant
    isolation, replay, transaction rollback and corruption rejection.

EPITOME:
    VERIFIED OBJECT-BACKED CANONICAL METADATA
    -> METADATA-ONLY MONGO DURABILITY
    != RAW-BYTE BSON STORAGE
    != PROVIDER EXECUTION
    != RESERVATION CONSUMPTION
    != AUTHORIZED AVAILABILITY

DATABASE SAFETY:
    Only loopback wilsyVendorCertRS is accepted. Every run uses one UUID-isolated
    disposable database. Canonical database "wilsy" is forbidden and never used.

TRANSACTION POSTURE:
    Test callers own every Mongo session and transaction. The registry never
    starts, commits, aborts or retries transaction lifecycle.

TENANT POSTURE:
    Reads/writes are exact-tenant scoped. Cross-tenant absence is represented as
    ordinary not-found without resource disclosure.

FAIL CLOSED:
    Wrong topology, index drift, TTL presence, raw-byte persistence, divergent
    replay, corruption, rollback leakage or tenant-scope failure fails the
    certificate.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import uuid
from typing import Any, Iterator

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_evidence_content import (
    register_legal_evidence_content,
)
from tools.eos.legal_operations.domain.legal_evidence_object_metadata import (
    LegalEvidenceObjectMetadata,
    bind_legal_evidence_object_metadata,
)
from tools.eos.legal_operations.registry import (
    legal_evidence_object_metadata_registry as registry,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryWriteIntent,
)


URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)
REPLICA_SET = "wilsyVendorCertRS"
DATABASE_PREFIX = "wilsy_l10a2r_c2_cert_"

AT = datetime(
    2026,
    9,
    30,
    9,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)
SOURCE_FP = hashlib.sha3_512(
    b"wilsy-l10a2r-c2-real-source"
).hexdigest()


class MongoContext:
    """Own one isolated C2 certification database."""

    def __init__(
        self,
        client: MongoClient[Any],
        database_name: str,
    ) -> None:
        self.client = client
        self.database_name = database_name
        self.database = client.get_database(
            database_name,
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
        )
        self.collection = self.database.get_collection(
            registry.COLLECTION,
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
        )
        self.registry = (
            registry.LegalEvidenceObjectMetadataRegistry(
                self.collection
            )
        )
        self.registry.ensure_indexes()


def _fresh_context() -> MongoContext:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        socketTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )

    try:
        hello = client.admin.command("hello")
        address = client.address

        if (
            address is None
            or address[0] not in {
                "127.0.0.1",
                "localhost",
            }
        ):
            raise RuntimeError(
                "L10A2R_C2_CERT_MONGO_NOT_LOOPBACK"
            )

        if hello.get("setName") != REPLICA_SET:
            raise RuntimeError(
                "L10A2R_C2_CERT_REPLICA_SET_MISMATCH"
            )

        if hello.get(
            "isWritablePrimary",
            hello.get("ismaster"),
        ) is not True:
            raise RuntimeError(
                "L10A2R_C2_CERT_WRITABLE_PRIMARY_REQUIRED"
            )

        if hello.get(
            "logicalSessionTimeoutMinutes"
        ) is None:
            raise RuntimeError(
                "L10A2R_C2_CERT_SESSIONS_REQUIRED"
            )

        database_name = (
            DATABASE_PREFIX
            + uuid.uuid4().hex
        )

        if (
            database_name == "wilsy"
            or not database_name.startswith(
                DATABASE_PREFIX
            )
            or len(database_name) > 63
        ):
            raise RuntimeError(
                "L10A2R_C2_CERT_DATABASE_GUARD_FAILED"
            )

        return MongoContext(
            client,
            database_name,
        )

    except BaseException:
        client.close()
        raise


@pytest.fixture(scope="module")
def mongo_context() -> Iterator[MongoContext]:
    """Yield then destroy only one UUID-isolated certification database."""
    context = _fresh_context()

    try:
        yield context
    finally:
        context.client.drop_database(
            context.database_name
        )
        assert (
            context.database_name
            not in context.client.list_database_names()
        )
        context.client.close()


def _value(
    *,
    tenant_id: str,
    case_matter_id: str = "matter-c2-real",
    document_id: str = "document-c2-real",
    ingestion_reference: str = "ingestion-c2-real",
    storage_reference: str = "legal-evidence/v1/c2-real",
    object_version_reference: str = "version-c2-real",
    registered_at: datetime = AT,
) -> LegalEvidenceObjectMetadata:
    body = (
        b"%PDF-1.7\n"
        + tenant_id.encode("utf-8")
        + b"\nsynthetic-c2-real-mongo\n"
    )

    content = register_legal_evidence_content(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        document_id=document_id,
        media_type="application/pdf",
        original_filename="synthetic-evidence.pdf",
        content=body,
        source_evidence_reference=(
            "source-c2-real"
        ),
        source_evidence_fingerprint=SOURCE_FP,
        registered_at=registered_at,
    )

    intent = LegalEvidenceBinaryWriteIntent(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        document_id=document_id,
        ingestion_reference=ingestion_reference,
        media_type=content.media_type,
        original_filename=content.original_filename,
        admitted_max_content_length=content.content_length,
    )

    evidence = LegalEvidenceBinaryObjectEvidence(
        provider_name="aws-s3",
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        provider_integrity_reference='"etag-c2-real"',
        write_intent_fingerprint=intent.fingerprint,
        content_length=content.content_length,
        content_fingerprint=content.content_fingerprint,
    )

    return bind_legal_evidence_object_metadata(
        content=content,
        intent=intent,
        object_evidence=evidence,
    )


def _commit(
    context: MongoContext,
    value: LegalEvidenceObjectMetadata,
) -> LegalEvidenceObjectMetadata:
    with context.client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
        )
        try:
            result = context.registry.create_or_replay(
                value,
                session=session,
            )
            session.commit_transaction()
            return result
        except BaseException:
            if session.in_transaction:
                session.abort_transaction()
            raise


def test_real_topology_and_exact_indexes_have_no_ttl(
    mongo_context: MongoContext,
) -> None:
    hello = mongo_context.client.admin.command(
        "hello"
    )

    assert hello["setName"] == REPLICA_SET
    assert hello.get(
        "isWritablePrimary",
        hello.get("ismaster"),
    ) is True
    assert hello.get(
        "logicalSessionTimeoutMinutes"
    ) is not None

    indexes = {
        item["name"]: item
        for item in mongo_context.collection.list_indexes()
        if item["name"] != "_id_"
    }

    assert set(indexes) == {
        registry.REFERENCE_INDEX_NAME,
        registry.DOCUMENT_INDEX_NAME,
        registry.CONTENT_FINGERPRINT_INDEX_NAME,
        registry.PROVIDER_OBJECT_INDEX_NAME,
    }

    assert dict(
        indexes[
            registry.REFERENCE_INDEX_NAME
        ]["key"]
    ) == {
        "tenant_id": 1,
        "content_reference": 1,
    }
    assert (
        indexes[
            registry.REFERENCE_INDEX_NAME
        ].get("unique")
        is True
    )

    assert dict(
        indexes[
            registry.DOCUMENT_INDEX_NAME
        ]["key"]
    ) == {
        "tenant_id": 1,
        "case_matter_id": 1,
        "document_id": 1,
        "registered_at": -1,
    }

    assert dict(
        indexes[
            registry.CONTENT_FINGERPRINT_INDEX_NAME
        ]["key"]
    ) == {
        "tenant_id": 1,
        "content_fingerprint": 1,
    }

    assert dict(
        indexes[
            registry.PROVIDER_OBJECT_INDEX_NAME
        ]["key"]
    ) == {
        "tenant_id": 1,
        "provider_name": 1,
        "storage_reference": 1,
        "object_version_reference": 1,
    }
    assert (
        indexes[
            registry.PROVIDER_OBJECT_INDEX_NAME
        ].get(
            "unique",
            False,
        )
        is False
    )

    assert all(
        "expireAfterSeconds" not in item
        for item in indexes.values()
    )


def test_real_commit_replay_get_list_and_bson_are_metadata_only(
    mongo_context: MongoContext,
) -> None:
    tenant = (
        "tenant-c2-real-replay-"
        + uuid.uuid4().hex
    )
    value = _value(
        tenant_id=tenant,
    )

    first = _commit(
        mongo_context,
        value,
    )
    second = _commit(
        mongo_context,
        value,
    )

    assert first == second == value

    raw = mongo_context.collection.find_one(
        {
            "tenant_id": tenant,
            "content_reference": value.content_reference,
        }
    )
    assert raw is not None

    persisted = dict(raw)
    persisted.pop("_id", None)

    expected = value.to_dict()
    expected["registered_at"] = value.registered_at.isoformat()

    assert persisted == expected
    assert persisted["registered_at"] == (
        value.registered_at.isoformat()
    )
    assert persisted["registered_at"].endswith(
        ".123456+00:00"
    )

    forbidden = {
        "content_bytes",
        "content",
        "bytes",
        "body",
        "binary_body",
    }
    assert forbidden.isdisjoint(
        persisted
    )
    assert all(
        not isinstance(
            item,
            (
                bytes,
                bytearray,
            ),
        )
        for item in persisted.values()
    )

    assert (
        mongo_context.collection.count_documents(
            {
                "tenant_id": tenant,
                "content_reference": value.content_reference,
            }
        )
        == 1
    )

    with mongo_context.client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
        )
        try:
            observed = mongo_context.registry.get(
                tenant_id=tenant,
                content_reference=value.content_reference,
                session=session,
            )
            listed = (
                mongo_context.registry.list_document_metadata(
                    tenant_id=tenant,
                    case_matter_id=value.case_matter_id,
                    document_id=value.document_id,
                    session=session,
                )
            )
            provider_loaded = (
                mongo_context.registry.get_provider_object(
                    tenant_id=tenant,
                    provider_name=value.provider_name,
                    storage_reference=value.storage_reference,
                    object_version_reference=(
                        value.object_version_reference
                    ),
                    session=session,
                )
            )
            session.commit_transaction()
        except BaseException:
            if session.in_transaction:
                session.abort_transaction()
            raise

    assert observed == value
    assert listed == (
        value,
    )
    assert provider_loaded == value


def test_real_cross_tenant_provider_object_lookup_is_opaque(
    mongo_context: MongoContext,
) -> None:
    tenant = (
        "tenant-c2-real-provider-"
        + uuid.uuid4().hex
    )

    value = _value(
        tenant_id=tenant,
        ingestion_reference="ingestion-c2-real-provider",
        storage_reference="legal-evidence/v1/c2-real-provider",
        object_version_reference="version-c2-real-provider",
    )

    _commit(
        mongo_context,
        value,
    )

    with mongo_context.client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
        )

        try:
            with pytest.raises(
                registry.LegalEvidenceObjectMetadataRegistryNotFoundError,
                match="L10A2R_C2_PROVIDER_OBJECT_NOT_FOUND",
            ):
                mongo_context.registry.get_provider_object(
                    tenant_id=(
                        "tenant-neighbor-"
                        + uuid.uuid4().hex
                    ),
                    provider_name=value.provider_name,
                    storage_reference=value.storage_reference,
                    object_version_reference=(
                        value.object_version_reference
                    ),
                    session=session,
                )
        finally:
            if session.in_transaction:
                session.abort_transaction()


def test_real_cross_tenant_absence_and_divergent_replay_fail_closed(
    mongo_context: MongoContext,
) -> None:
    tenant = (
        "tenant-c2-real-scope-"
        + uuid.uuid4().hex
    )
    value = _value(
        tenant_id=tenant,
        ingestion_reference="ingestion-c2-real-scope",
        storage_reference="legal-evidence/v1/c2-real-scope",
        object_version_reference="version-c2-real-scope",
    )

    _commit(
        mongo_context,
        value,
    )

    with mongo_context.client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
        )
        try:
            with pytest.raises(
                registry.LegalEvidenceObjectMetadataRegistryNotFoundError,
                match="L10A2R_C2_METADATA_NOT_FOUND",
            ):
                mongo_context.registry.get(
                    tenant_id=(
                        "tenant-neighbor-"
                        + uuid.uuid4().hex
                    ),
                    content_reference=value.content_reference,
                    session=session,
                )
        finally:
            if session.in_transaction:
                session.abort_transaction()

    payload = value.to_dict()
    payload[
        "provider_integrity_reference"
    ] = '"divergent-etag"'
    payload["fingerprint"] = ""

    divergent = LegalEvidenceObjectMetadata(
        **payload,  # type: ignore[arg-type]
    )

    with mongo_context.client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
        )
        try:
            with pytest.raises(
                registry.LegalEvidenceObjectMetadataRegistryConflictError,
                match="L10A2R_C2_DIVERGENT_CONTENT_REFERENCE",
            ):
                mongo_context.registry.create_or_replay(
                    divergent,
                    session=session,
                )
        finally:
            if session.in_transaction:
                session.abort_transaction()

    assert (
        mongo_context.collection.count_documents(
            {
                "tenant_id": tenant,
                "content_reference": value.content_reference,
            }
        )
        == 1
    )


def test_real_aborted_transaction_leaves_no_metadata_row(
    mongo_context: MongoContext,
) -> None:
    tenant = (
        "tenant-c2-real-abort-"
        + uuid.uuid4().hex
    )
    value = _value(
        tenant_id=tenant,
        ingestion_reference="ingestion-c2-real-abort",
        storage_reference="legal-evidence/v1/c2-real-abort",
        object_version_reference="version-c2-real-abort",
    )

    with mongo_context.client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
        )

        mongo_context.registry.create_or_replay(
            value,
            session=session,
        )

        assert session.in_transaction is True
        session.abort_transaction()

    assert (
        mongo_context.collection.count_documents(
            {
                "tenant_id": tenant,
                "content_reference": value.content_reference,
            }
        )
        == 0
    )


def test_real_persisted_corruption_rejects_without_healing(
    mongo_context: MongoContext,
) -> None:
    tenant = (
        "tenant-c2-real-corrupt-"
        + uuid.uuid4().hex
    )
    value = _value(
        tenant_id=tenant,
        ingestion_reference="ingestion-c2-real-corrupt",
        storage_reference="legal-evidence/v1/c2-real-corrupt",
        object_version_reference="version-c2-real-corrupt",
    )

    _commit(
        mongo_context,
        value,
    )

    result = mongo_context.collection.update_one(
        {
            "tenant_id": tenant,
            "content_reference": value.content_reference,
        },
        {
            "$set": {
                "content_bytes": b"forbidden"
            }
        },
    )
    assert result.modified_count == 1

    with mongo_context.client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
        )
        try:
            with pytest.raises(
                registry.LegalEvidenceObjectMetadataRegistryError,
                match="L10A2R_C2_CORRUPT_METADATA",
            ):
                mongo_context.registry.get(
                    tenant_id=tenant,
                    content_reference=value.content_reference,
                    session=session,
                )
        finally:
            if session.in_transaction:
                session.abort_transaction()

    raw = mongo_context.collection.find_one(
        {
            "tenant_id": tenant,
            "content_reference": value.content_reference,
        }
    )
    assert raw is not None
    assert bytes(
        raw["content_bytes"]
    ) == b"forbidden"


# ARTIFACT: test_legal_evidence_object_metadata_registry_real_mongo.py
# VERSION: v1.1.0-L10A2R-C2R1-PROVIDER-OBJECT-LOOKUP-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical metadata-only Mongo durability certificate
# DATABASE POSTURE: disposable UUID database on loopback wilsyVendorCertRS only
# CONTROL-PLANE POSTURE: valid C2 writes persist no raw binary body
# CORRUPTION POSTURE: forbidden/raw-byte drift rejects without healing
# TENANT POSTURE: exact tenant scope; foreign scope is ordinary not-found
# TRANSACTION POSTURE: caller owns start/commit/abort
# TTL POSTURE: exact indexes and no TTL
# AVAILABILITY POSTURE: persistence does not authorize availability
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
