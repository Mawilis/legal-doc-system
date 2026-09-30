"""Direct certificate for the C4D5C binary write-intent registry."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from tools.eos.legal_operations.registry.legal_evidence_binary_write_intent_registry import (
    COLLECTION,
    INDEX_TENANT_DOCUMENT_REGISTERED,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_INGESTION,
    LegalEvidenceBinaryWriteIntentConflictError,
    LegalEvidenceBinaryWriteIntentNotFoundError,
    LegalEvidenceBinaryWriteIntentPersistedRecordInvalidError,
    LegalEvidenceBinaryWriteIntentRegistry,
    LegalEvidenceBinaryWriteIntentTransactionRequiredError,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryWriteIntent,
)


REGISTERED_AT = datetime(
    2026,
    9,
    30,
    16,
    45,
    12,
    345678,
    tzinfo=timezone.utc,
)


class _Session:
    def __init__(
        self,
        *,
        in_transaction: bool,
    ) -> None:
        self.in_transaction = in_transaction


class _InsertResult:
    acknowledged = True


class _FakeCollection:
    def __init__(
        self,
    ) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[
            tuple[
                tuple[tuple[str, int], ...],
                bool,
                str,
            ]
        ] = []

    def create_index(
        self,
        keys: list[tuple[str, int]],
        *,
        unique: bool,
        name: str,
    ) -> str:
        self.indexes.append(
            (
                tuple(keys),
                unique,
                name,
            )
        )
        return name

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: Any,
    ) -> dict[str, Any] | None:
        assert session.in_transaction is True

        for row in self.rows:
            if all(
                row.get(key) == value
                for key, value in query.items()
            ):
                return deepcopy(
                    row
                )

        return None

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: Any,
    ) -> _InsertResult:
        assert session.in_transaction is True
        self.rows.append(
            deepcopy(
                document
            )
        )
        return _InsertResult()


def _intent(
    *,
    tenant_id: str = "tenant-c4d5c",
    ingestion_reference: str = "ingestion-c4d5c",
    original_filename: str = "evidence.pdf",
) -> LegalEvidenceBinaryWriteIntent:
    return LegalEvidenceBinaryWriteIntent(
        tenant_id=tenant_id,
        case_matter_id="matter-c4d5c",
        document_id="document-c4d5c",
        ingestion_reference=ingestion_reference,
        media_type="application/pdf",
        original_filename=original_filename,
        admitted_max_content_length=4096,
    )


def _registry() -> tuple[
    LegalEvidenceBinaryWriteIntentRegistry,
    _FakeCollection,
]:
    collection = _FakeCollection()
    return (
        LegalEvidenceBinaryWriteIntentRegistry(
            collection
        ),
        collection,
    )


def _tx() -> _Session:
    return _Session(
        in_transaction=True
    )


def test_collection_identity_is_dedicated_and_non_provider() -> None:
    assert COLLECTION == "legal_evidence_binary_write_intents"
    assert "provider" not in COLLECTION


def test_indexes_are_exact_unique_and_have_no_ttl() -> None:
    registry, collection = _registry()

    registry.ensure_indexes()

    by_name = {
        name: (
            keys,
            unique,
        )
        for keys, unique, name in collection.indexes
    }

    assert (
        by_name[
            INDEX_TENANT_INGESTION
        ]
        == (
            (
                (
                    "tenant_id",
                    1,
                ),
                (
                    "ingestion_reference",
                    1,
                ),
            ),
            True,
        )
    )

    assert (
        by_name[
            INDEX_TENANT_FINGERPRINT
        ][1]
        is True
    )

    assert (
        by_name[
            INDEX_TENANT_DOCUMENT_REGISTERED
        ][1]
        is False
    )

    assert all(
        "expireAfterSeconds"
        not in repr(value)
        for value in collection.indexes
    )


def test_missing_active_transaction_rejects_before_read_or_write() -> None:
    registry, collection = _registry()

    with pytest.raises(
        LegalEvidenceBinaryWriteIntentTransactionRequiredError,
        match="TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(
            _intent(),
            registered_at=REGISTERED_AT,
            session=_Session(
                in_transaction=False
            ),
        )

    assert collection.rows == []


def test_create_persists_exact_immutable_canonical_intent() -> None:
    registry, collection = _registry()
    intent = _intent()

    record = registry.create_or_replay(
        intent,
        registered_at=REGISTERED_AT,
        session=_tx(),
    )

    assert record.intent == intent
    assert record.registered_at == REGISTERED_AT
    assert len(record.record_fingerprint) == 128
    assert len(collection.rows) == 1

    row = collection.rows[0]

    assert row["tenant_id"] == intent.tenant_id
    assert (
        row["ingestion_reference"]
        == intent.ingestion_reference
    )
    assert (
        row["write_intent_fingerprint"]
        == intent.fingerprint
    )

    assert "provider_name" not in row
    assert "storage_reference" not in row
    assert "object_version_reference" not in row


def test_exact_replay_returns_same_record_without_duplicate() -> None:
    registry, collection = _registry()
    intent = _intent()
    session = _tx()

    first = registry.create_or_replay(
        intent,
        registered_at=REGISTERED_AT,
        session=session,
    )

    second = registry.create_or_replay(
        intent,
        registered_at=REGISTERED_AT,
        session=session,
    )

    assert second == first
    assert len(collection.rows) == 1


def test_same_ingestion_reference_with_divergent_intent_rejects() -> None:
    registry, _ = _registry()
    session = _tx()

    registry.create_or_replay(
        _intent(),
        registered_at=REGISTERED_AT,
        session=session,
    )

    with pytest.raises(
        LegalEvidenceBinaryWriteIntentConflictError,
        match="DIVERGENT_INGESTION_REFERENCE",
    ):
        registry.create_or_replay(
            _intent(
                original_filename="different.pdf"
            ),
            registered_at=REGISTERED_AT,
            session=session,
        )


def test_same_intent_with_divergent_registration_time_rejects() -> None:
    registry, _ = _registry()
    intent = _intent()
    session = _tx()

    registry.create_or_replay(
        intent,
        registered_at=REGISTERED_AT,
        session=session,
    )

    with pytest.raises(
        LegalEvidenceBinaryWriteIntentConflictError,
        match="DIVERGENT_INGESTION_REFERENCE",
    ):
        registry.create_or_replay(
            intent,
            registered_at=(
                REGISTERED_AT
                + timedelta(
                    microseconds=1
                )
            ),
            session=session,
        )


def test_get_by_ingestion_reference_is_exact_tenant_scoped() -> None:
    registry, _ = _registry()
    intent = _intent()
    session = _tx()

    expected = registry.create_or_replay(
        intent,
        registered_at=REGISTERED_AT,
        session=session,
    )

    actual = registry.get_by_ingestion_reference(
        tenant_id=intent.tenant_id,
        ingestion_reference=intent.ingestion_reference,
        session=session,
    )

    assert actual == expected

    with pytest.raises(
        LegalEvidenceBinaryWriteIntentNotFoundError,
        match="WRITE_INTENT_NOT_FOUND",
    ):
        registry.get_by_ingestion_reference(
            tenant_id="tenant-other",
            ingestion_reference=intent.ingestion_reference,
            session=session,
        )


def test_get_by_fingerprint_supports_provider_metadata_reconciliation() -> None:
    registry, _ = _registry()
    intent = _intent()
    session = _tx()

    expected = registry.create_or_replay(
        intent,
        registered_at=REGISTERED_AT,
        session=session,
    )

    actual = registry.get_by_fingerprint(
        tenant_id=intent.tenant_id,
        write_intent_fingerprint=intent.fingerprint,
        session=session,
    )

    assert actual == expected


def test_strict_hydration_rejects_corrupt_durable_intent() -> None:
    registry, collection = _registry()
    intent = _intent()
    session = _tx()

    registry.create_or_replay(
        intent,
        registered_at=REGISTERED_AT,
        session=session,
    )

    collection.rows[0][
        "media_type"
    ] = "text/plain"

    with pytest.raises(
        LegalEvidenceBinaryWriteIntentPersistedRecordInvalidError,
        match="PERSISTED_RECORD_INVALID",
    ):
        registry.get_by_ingestion_reference(
            tenant_id=intent.tenant_id,
            ingestion_reference=intent.ingestion_reference,
            session=session,
        )


def test_registered_at_normalizes_to_utc_without_precision_loss() -> None:
    registry, _ = _registry()

    plus_two = REGISTERED_AT.astimezone(
        timezone(
            timedelta(
                hours=2
            )
        )
    )

    record = registry.create_or_replay(
        _intent(),
        registered_at=plus_two,
        session=_tx(),
    )

    assert record.registered_at == REGISTERED_AT
    assert (
        record.registered_at.microsecond
        == 345678
    )


def test_pseudo_global_tenant_lookup_rejects() -> None:
    registry, _ = _registry()

    with pytest.raises(
        Exception,
        match="TENANT_REQUIRED",
    ):
        registry.get_by_ingestion_reference(
            tenant_id="global",
            ingestion_reference="ingestion-c4d5c",
            session=_tx(),
        )


def test_registry_surface_has_no_provider_or_delete_mutators() -> None:
    public = {
        name
        for name in dir(
            LegalEvidenceBinaryWriteIntentRegistry
        )
        if not name.startswith("_")
    }

    forbidden = {
        "begin",
        "complete",
        "abort",
        "delete",
        "delete_object",
        "authorize_delete",
        "authorize_deletion",
        "prove_orphan",
        "provider_delete",
        "update",
    }

    assert forbidden.isdisjoint(
        public
    )


# ARTIFACT: test_legal_evidence_binary_write_intent_registry.py
# VERSION: v1.0.0-L10A2R-C4D5C-BINARY-WRITE-INTENT-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct durable original-intent registry evidence only
# TENANT POSTURE: exact tenant-scoped registration/read behavior
# PROVIDER POSTURE: no provider begin/upload/completion assertion
# COVERAGE POSTURE: absence alone is never orphan proof
# DELETION POSTURE: no orphan proof or deletion authorization
# END OF WILSY OS SOVEREIGN ARTIFACT
