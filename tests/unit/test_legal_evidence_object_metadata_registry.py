"""Direct certificate for metadata-only Legal Evidence object persistence.

TITLE: Legal Evidence Object Metadata Registry Certificate
VERSION: v1.0.0-L10A2R-C2-LEGAL-EVIDENCE-OBJECT-METADATA-REGISTRY-CERT
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Freeze the Mongo control-plane registry contract for immutable C1
    LegalEvidenceObjectMetadata values without persisting raw binary bodies.

EPITOME:
    OBJECT-BACKED CANONICAL METADATA
    -> METADATA-ONLY MONGO DURABILITY
    != RAW-BYTE STORAGE
    != PROVIDER EXECUTION
    != RESERVATION CONSUMPTION
    != AUTHORIZED AVAILABILITY

TRANSACTION:
    Operational reads/writes require one already-active caller-owned Mongo
    transaction. The registry never starts, commits, aborts or retries it.

REPLAY:
    Exact tenant/content-reference replay of the exact C1 value succeeds.
    Any divergence under the same immutable identity fails closed.

TENANT:
    Every read/write begins with exact tenant scope. Cross-tenant absence is
    indistinguishable from not found.

FAIL CLOSED:
    Missing transactions, malformed inputs, unknown persisted fields,
    fingerprint corruption, divergent replay, duplicate races and Mongo
    failures reject without healing inferred truth.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from tools.eos.legal_operations.domain.legal_evidence_content import (
    register_legal_evidence_content,
)
from tools.eos.legal_operations.domain.legal_evidence_object_metadata import (
    LegalEvidenceObjectMetadata,
    bind_legal_evidence_object_metadata,
)
from tools.eos.legal_operations.registry.legal_evidence_object_metadata_registry import (
    COLLECTION,
    CONTENT_FINGERPRINT_INDEX_NAME,
    DOCUMENT_INDEX_NAME,
    REFERENCE_INDEX_NAME,
    LegalEvidenceObjectMetadataRegistry,
    LegalEvidenceObjectMetadataRegistryConflictError,
    LegalEvidenceObjectMetadataRegistryError,
    LegalEvidenceObjectMetadataRegistryNotFoundError,
    LegalEvidenceObjectMetadataRegistryTransactionRequiredError,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryWriteIntent,
)


AT = datetime(
    2026,
    9,
    30,
    8,
    30,
    0,
    123456,
    tzinfo=timezone.utc,
)
SHA_A = "a" * 128


class Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class InsertResult:
    inserted_id = "inserted"


class Cursor:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def sort(self, *args: object, **kwargs: object) -> Cursor:
        del args, kwargs
        return self

    def limit(self, value: int) -> Cursor:
        self.rows = self.rows[:value]
        return self

    def __iter__(self):
        return iter(self.rows)


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[object, dict[str, object]]] = []

    def create_index(
        self,
        keys: object,
        **kwargs: object,
    ) -> str:
        self.indexes.append((keys, dict(kwargs)))
        return str(kwargs.get("name", "index"))

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> dict[str, object] | None:
        del session
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return dict(row)
        return None

    def find(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> Cursor:
        del session
        rows = [
            dict(row)
            for row in self.rows
            if all(row.get(key) == value for key, value in query.items())
        ]
        return Cursor(rows)

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object,
    ) -> InsertResult:
        del session
        self.rows.append(dict(document))
        return InsertResult()


def _value(
    *,
    tenant_id: str = "tenant-c2",
    case_matter_id: str = "matter-c2",
    document_id: str = "document-c2",
    ingestion_reference: str = "ingestion-c2",
    storage_reference: str = "legal-evidence/v1/c2",
    object_version_reference: str = "version-c2",
) -> LegalEvidenceObjectMetadata:
    content = register_legal_evidence_content(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        document_id=document_id,
        media_type="application/pdf",
        original_filename="evidence.pdf",
        content=b"object-backed-content",
        source_evidence_reference="source-c2",
        source_evidence_fingerprint=SHA_A,
        registered_at=AT,
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
        provider_integrity_reference='"etag-c2"',
        write_intent_fingerprint=intent.fingerprint,
        content_length=content.content_length,
        content_fingerprint=content.content_fingerprint,
    )

    return bind_legal_evidence_object_metadata(
        content=content,
        intent=intent,
        object_evidence=evidence,
    )


def test_collection_identity_is_dedicated_metadata_control_plane() -> None:
    assert COLLECTION == "legal_evidence_object_metadata"


def test_indexes_are_exact_and_have_no_ttl() -> None:
    collection = Collection()
    registry = LegalEvidenceObjectMetadataRegistry(collection)

    registry.ensure_indexes()

    assert len(collection.indexes) == 3

    by_name = {
        kwargs["name"]: (keys, kwargs)
        for keys, kwargs in collection.indexes
    }

    assert set(by_name) == {
        REFERENCE_INDEX_NAME,
        DOCUMENT_INDEX_NAME,
        CONTENT_FINGERPRINT_INDEX_NAME,
    }

    reference_keys, reference_kwargs = by_name[
        REFERENCE_INDEX_NAME
    ]
    assert reference_keys == [
        ("tenant_id", 1),
        ("content_reference", 1),
    ]
    assert reference_kwargs["unique"] is True

    document_keys, document_kwargs = by_name[
        DOCUMENT_INDEX_NAME
    ]
    assert document_keys == [
        ("tenant_id", 1),
        ("case_matter_id", 1),
        ("document_id", 1),
        ("registered_at", -1),
    ]
    assert document_kwargs["unique"] is False

    fingerprint_keys, fingerprint_kwargs = by_name[
        CONTENT_FINGERPRINT_INDEX_NAME
    ]
    assert fingerprint_keys == [
        ("tenant_id", 1),
        ("content_fingerprint", 1),
    ]
    assert fingerprint_kwargs["unique"] is False

    for _, kwargs in collection.indexes:
        assert "expireAfterSeconds" not in kwargs


def test_missing_active_transaction_rejects_before_read_or_write() -> None:
    collection = MagicMock()
    registry = LegalEvidenceObjectMetadataRegistry(collection)

    with pytest.raises(
        LegalEvidenceObjectMetadataRegistryTransactionRequiredError,
        match="L10A2R_C2_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(
            _value(),
            session=Session(False),
        )

    collection.find_one.assert_not_called()
    collection.insert_one.assert_not_called()


def test_create_persists_exact_metadata_only_surface() -> None:
    collection = Collection()
    registry = LegalEvidenceObjectMetadataRegistry(collection)
    value = _value()

    result = registry.create_or_replay(
        value,
        session=Session(),
    )

    assert result == value
    assert len(collection.rows) == 1

    persisted = collection.rows[0]
    expected = value.to_dict()
    expected["registered_at"] = value.registered_at.isoformat()

    assert persisted == expected
    assert persisted["registered_at"] == (
        "2026-09-30T08:30:00.123456+00:00"
    )

    forbidden = {
        "content_bytes",
        "content",
        "bytes",
        "body",
        "binary_body",
    }

    assert forbidden.isdisjoint(persisted)
    assert all(
        not isinstance(item, (bytes, bytearray))
        for item in persisted.values()
    )


def test_exact_replay_returns_without_second_insert() -> None:
    collection = Collection()
    registry = LegalEvidenceObjectMetadataRegistry(collection)
    value = _value()

    first = registry.create_or_replay(
        value,
        session=Session(),
    )
    second = registry.create_or_replay(
        value,
        session=Session(),
    )

    assert first == second == value
    assert len(collection.rows) == 1


def test_divergent_same_reference_rejects() -> None:
    collection = Collection()
    registry = LegalEvidenceObjectMetadataRegistry(collection)
    first = _value()

    registry.create_or_replay(
        first,
        session=Session(),
    )

    payload = first.to_dict()
    payload["provider_integrity_reference"] = '"different-etag"'
    payload["fingerprint"] = ""

    divergent = LegalEvidenceObjectMetadata(
        **payload,  # type: ignore[arg-type]
    )

    with pytest.raises(
        LegalEvidenceObjectMetadataRegistryConflictError,
        match="L10A2R_C2_DIVERGENT_CONTENT_REFERENCE",
    ):
        registry.create_or_replay(
            divergent,
            session=Session(),
        )

    assert len(collection.rows) == 1


def test_exact_tenant_scoped_get_and_cross_tenant_not_found() -> None:
    collection = Collection()
    registry = LegalEvidenceObjectMetadataRegistry(collection)
    value = _value()

    registry.create_or_replay(
        value,
        session=Session(),
    )

    assert (
        registry.get(
            tenant_id=value.tenant_id,
            content_reference=value.content_reference,
            session=Session(),
        )
        == value
    )

    with pytest.raises(
        LegalEvidenceObjectMetadataRegistryNotFoundError,
        match="L10A2R_C2_METADATA_NOT_FOUND",
    ):
        registry.get(
            tenant_id="tenant-neighbor",
            content_reference=value.content_reference,
            session=Session(),
        )


def test_document_list_is_exact_scope_and_deterministic() -> None:
    collection = Collection()
    registry = LegalEvidenceObjectMetadataRegistry(collection)

    first = _value(
        ingestion_reference="ingestion-c2-a",
        storage_reference="legal-evidence/v1/c2-a",
        object_version_reference="version-c2-a",
    )

    second_payload = first.to_dict()
    second_payload["content_reference"] = (
        first.content_reference + "-second"
    )
    second_payload["registered_at"] = AT.replace(
        microsecond=123457
    )
    second_payload["storage_reference"] = (
        "legal-evidence/v1/c2-b"
    )
    second_payload["object_version_reference"] = (
        "version-c2-b"
    )
    second_payload["fingerprint"] = ""

    second = LegalEvidenceObjectMetadata(
        **second_payload,  # type: ignore[arg-type]
    )

    registry.create_or_replay(
        first,
        session=Session(),
    )
    registry.create_or_replay(
        second,
        session=Session(),
    )

    rows = registry.list_document_metadata(
        tenant_id=first.tenant_id,
        case_matter_id=first.case_matter_id,
        document_id=first.document_id,
        session=Session(),
    )

    assert rows == (
        second,
        first,
    )


def test_persisted_unknown_field_rejects_fail_closed() -> None:
    collection = Collection()
    value = _value()
    corrupted = value.to_dict()
    corrupted["content_bytes"] = b"forbidden"

    collection.rows.append(corrupted)
    registry = LegalEvidenceObjectMetadataRegistry(collection)

    with pytest.raises(
        LegalEvidenceObjectMetadataRegistryError,
        match="L10A2R_C2_CORRUPT_METADATA",
    ):
        registry.get(
            tenant_id=value.tenant_id,
            content_reference=value.content_reference,
            session=Session(),
        )


def test_persisted_fingerprint_corruption_rejects_fail_closed() -> None:
    collection = Collection()
    value = _value()
    corrupted = value.to_dict()
    corrupted["fingerprint"] = "f" * 128

    collection.rows.append(corrupted)
    registry = LegalEvidenceObjectMetadataRegistry(collection)

    with pytest.raises(
        LegalEvidenceObjectMetadataRegistryError,
        match="L10A2R_C2_CORRUPT_METADATA",
    ):
        registry.get(
            tenant_id=value.tenant_id,
            content_reference=value.content_reference,
            session=Session(),
        )


def test_public_surface_has_no_raw_byte_provider_or_later_authority() -> None:
    public = {
        name.lower()
        for name in dir(
            LegalEvidenceObjectMetadataRegistry
        )
        if not name.startswith("_")
    }

    forbidden = {
        "read_evidence_content_bytes",
        "get_bytes",
        "read_bytes",
        "upload",
        "begin",
        "write_chunk",
        "complete",
        "abort",
        "consume",
        "release",
        "expire",
        "authorize_availability",
        "invoice",
        "payment",
        "settlement",
    }

    assert forbidden.isdisjoint(public)


# ARTIFACT: test_legal_evidence_object_metadata_registry.py
# VERSION: v1.0.0-L10A2R-C2-LEGAL-EVIDENCE-OBJECT-METADATA-REGISTRY-CERT
# AUTHORITY BOUNDARY: immutable metadata-only Mongo durability
# CONTROL-PLANE POSTURE: no raw binary body persisted or returned
# OBJECT-PLANE POSTURE: no provider execution exists in registry
# TENANT POSTURE: exact tenant-scoped reads and immutable identity
# REPLAY POSTURE: exact replay succeeds; divergent identity rejects
# TTL POSTURE: no TTL index
# AVAILABILITY POSTURE: persistence does not authorize availability
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
