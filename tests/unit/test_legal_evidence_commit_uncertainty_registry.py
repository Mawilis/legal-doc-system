"""Direct certificate for durable Legal Evidence commit uncertainty.

TITLE: Legal Evidence Commit Uncertainty Registry Certificate
VERSION: v1.0.0-L10A2R-C4B-COMMIT-UNCERTAINTY-REGISTRY-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Freeze durable tenant-scoped persistence for immutable C4A commit-
    uncertainty evidence so provider-success/C3-outcome uncertainty survives
    process restart and remains available for later reconciliation.

EPITOME:
    C4A COMMIT UNCERTAINTY
    -> DURABLE MONGO CONTROL-PLANE EVIDENCE
    != ORPHAN PROVEN
    != RECONCILIATION PERFORMED
    != RESERVATION RELEASED
    != PROVIDER DELETION AUTHORIZED
    != AUTHORIZED AVAILABILITY

TRANSACTION:
    Every operational read/write requires one already-active caller-owned Mongo
    transaction. The registry never starts, commits, aborts or retries it.

REPLAY:
    Exact immutable replay succeeds. Divergence under the same uncertainty or
    ingestion identity fails closed.

TENANT:
    Every operational read begins with exact tenant scope. Cross-tenant absence
    is indistinguishable from not-found.

TTL:
    Commit uncertainty is reconciliation evidence. No TTL index is permitted.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
from unittest.mock import MagicMock

import pytest

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
)
from tools.eos.legal_operations.domain.legal_evidence_commit_uncertainty import (
    LegalEvidenceCommitUncertainty,
    open_legal_evidence_commit_uncertainty,
)
from tools.eos.legal_operations.registry.legal_evidence_commit_uncertainty_registry import (
    COLLECTION,
    DETECTED_INDEX_NAME,
    INGESTION_INDEX_NAME,
    PROVIDER_OBJECT_INDEX_NAME,
    UNCERTAINTY_INDEX_NAME,
    LegalEvidenceCommitUncertaintyRegistry,
    LegalEvidenceCommitUncertaintyRegistryConflictError,
    LegalEvidenceCommitUncertaintyRegistryError,
    LegalEvidenceCommitUncertaintyRegistryNotFoundError,
    LegalEvidenceCommitUncertaintyRegistryTransactionRequiredError,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryWriteIntent,
)


AT = datetime(
    2026,
    9,
    30,
    13,
    30,
    0,
    123456,
    tzinfo=timezone.utc,
)

CONTENT = b"c4b-provider-completed-content"
CONTENT_FP = hashlib.sha3_512(CONTENT).hexdigest()
SOURCE_FP = hashlib.sha3_512(
    b"c4b-source-evidence"
).hexdigest()


class Session:
    def __init__(
        self,
        active: bool = True,
    ) -> None:
        self.in_transaction = active


class InsertResult:
    inserted_id = "inserted"


class Cursor:
    def __init__(
        self,
        rows: list[dict[str, object]],
    ) -> None:
        self.rows = rows

    def limit(
        self,
        value: int,
    ) -> "Cursor":
        self.rows = self.rows[:value]
        return self

    def __iter__(self):
        return iter(self.rows)


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[
            tuple[
                object,
                dict[str, object],
            ]
        ] = []

    def create_index(
        self,
        keys: object,
        **kwargs: object,
    ) -> str:
        self.indexes.append(
            (
                keys,
                dict(kwargs),
            )
        )
        return str(
            kwargs.get(
                "name",
                "index",
            )
        )

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> dict[str, object] | None:
        del session

        for row in self.rows:
            if all(
                row.get(key) == value
                for key, value in query.items()
            ):
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
            if all(
                row.get(key) == value
                for key, value in query.items()
            )
        ]

        return Cursor(
            rows
        )

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object,
    ) -> InsertResult:
        del session

        self.rows.append(
            dict(document)
        )

        return InsertResult()


def _intent(
    *,
    tenant_id: str = "tenant-c4b",
    matter_id: str = "matter-c4b",
    document_id: str = "document-c4b",
    ingestion_reference: str = "ingestion-c4b",
) -> LegalEvidenceBinaryWriteIntent:
    return LegalEvidenceBinaryWriteIntent(
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        document_id=document_id,
        ingestion_reference=ingestion_reference,
        media_type="application/pdf",
        original_filename="evidence.pdf",
        admitted_max_content_length=4096,
    )


def _reservation(
    *,
    tenant_id: str = "tenant-c4b",
    document_id: str = "document-c4b",
    ingestion_intent_id: str = "ingestion-c4b",
    reservation_id: str = "reservation-c4b",
) -> LegalEvidenceCapacityReservation:
    return LegalEvidenceCapacityReservation(
        tenant_id=tenant_id,
        document_id=document_id,
        reservation_id=reservation_id,
        ingestion_intent_id=ingestion_intent_id,
        remaining_capacity_fingerprint="a" * 128,
        reserved_storage_bytes=len(CONTENT),
        reserved_ingress_bytes=len(CONTENT),
        reserved_document_versions=1,
        reserved_at=AT - timedelta(minutes=5),
        expires_at=AT + timedelta(minutes=20),
    )


def _uncertainty(
    *,
    tenant_id: str = "tenant-c4b",
    matter_id: str = "matter-c4b",
    document_id: str = "document-c4b",
    ingestion_reference: str = "ingestion-c4b",
    reservation_id: str = "reservation-c4b",
    storage_reference: str = "legal-evidence/v1/c4b",
    object_version_reference: str = "version-c4b",
    detected_at: datetime = AT,
) -> LegalEvidenceCommitUncertainty:
    intent = _intent(
        tenant_id=tenant_id,
        matter_id=matter_id,
        document_id=document_id,
        ingestion_reference=ingestion_reference,
    )

    reservation = _reservation(
        tenant_id=tenant_id,
        document_id=document_id,
        ingestion_intent_id=ingestion_reference,
        reservation_id=reservation_id,
    )

    object_evidence = (
        LegalEvidenceBinaryObjectEvidence(
            provider_name="aws_s3",
            storage_reference=storage_reference,
            object_version_reference=object_version_reference,
            provider_integrity_reference='"etag-c4b"',
            write_intent_fingerprint=intent.fingerprint,
            content_length=len(CONTENT),
            content_fingerprint=CONTENT_FP,
        )
    )

    return open_legal_evidence_commit_uncertainty(
        reservation=reservation,
        intent=intent,
        object_evidence=object_evidence,
        observed_content_length=len(CONTENT),
        observed_content_fingerprint=CONTENT_FP,
        source_evidence_reference="source-c4b",
        source_evidence_fingerprint=SOURCE_FP,
        detected_at=detected_at,
    )


def test_collection_identity_is_dedicated_uncertainty_control_plane() -> None:
    assert COLLECTION == (
        "legal_evidence_commit_uncertainties"
    )


def test_indexes_are_exact_and_have_no_ttl() -> None:
    collection = Collection()
    registry = (
        LegalEvidenceCommitUncertaintyRegistry(
            collection
        )
    )

    registry.ensure_indexes()

    assert len(collection.indexes) == 4

    by_name = {
        kwargs["name"]: (
            keys,
            kwargs,
        )
        for keys, kwargs
        in collection.indexes
    }

    assert set(by_name) == {
        UNCERTAINTY_INDEX_NAME,
        INGESTION_INDEX_NAME,
        PROVIDER_OBJECT_INDEX_NAME,
        DETECTED_INDEX_NAME,
    }

    uncertainty_keys, uncertainty_kwargs = (
        by_name[
            UNCERTAINTY_INDEX_NAME
        ]
    )
    assert uncertainty_keys == [
        (
            "tenant_id",
            1,
        ),
        (
            "uncertainty_id",
            1,
        ),
    ]
    assert (
        uncertainty_kwargs["unique"]
        is True
    )

    ingestion_keys, ingestion_kwargs = (
        by_name[
            INGESTION_INDEX_NAME
        ]
    )
    assert ingestion_keys == [
        (
            "tenant_id",
            1,
        ),
        (
            "ingestion_intent_id",
            1,
        ),
    ]
    assert (
        ingestion_kwargs["unique"]
        is True
    )

    provider_keys, provider_kwargs = (
        by_name[
            PROVIDER_OBJECT_INDEX_NAME
        ]
    )
    assert provider_keys == [
        (
            "tenant_id",
            1,
        ),
        (
            "provider_name",
            1,
        ),
        (
            "storage_reference",
            1,
        ),
        (
            "object_version_reference",
            1,
        ),
    ]
    assert (
        provider_kwargs["unique"]
        is True
    )

    detected_keys, detected_kwargs = (
        by_name[
            DETECTED_INDEX_NAME
        ]
    )
    assert detected_keys == [
        (
            "tenant_id",
            1,
        ),
        (
            "detected_at",
            -1,
        ),
        (
            "uncertainty_id",
            1,
        ),
    ]
    assert (
        detected_kwargs["unique"]
        is False
    )

    for _, kwargs in collection.indexes:
        assert (
            "expireAfterSeconds"
            not in kwargs
        )


def test_missing_active_transaction_rejects_before_read_or_write() -> None:
    collection = MagicMock()
    registry = (
        LegalEvidenceCommitUncertaintyRegistry(
            collection
        )
    )

    with pytest.raises(
        LegalEvidenceCommitUncertaintyRegistryTransactionRequiredError,
        match="L10A2R_C4B_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(
            _uncertainty(),
            session=Session(False),
        )

    collection.find_one.assert_not_called()
    collection.insert_one.assert_not_called()


def test_create_persists_exact_immutable_uncertainty_only() -> None:
    collection = Collection()
    registry = (
        LegalEvidenceCommitUncertaintyRegistry(
            collection
        )
    )
    value = _uncertainty()

    result = registry.create_or_replay(
        value,
        session=Session(),
    )

    assert result == value
    assert len(collection.rows) == 1

    persisted = collection.rows[0]
    expected = value.to_dict()
    expected["detected_at"] = (
        value.detected_at.isoformat()
    )

    assert persisted == expected
    assert persisted["detected_at"] == (
        "2026-09-30T13:30:00.123456+00:00"
    )

    forbidden = {
        "content",
        "content_bytes",
        "body",
        "raw_bytes",
        "orphan",
        "mongo_commit_failed",
        "metadata_missing",
        "resolved",
        "reconciled",
        "deleted",
        "available",
        "authorized_availability",
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


def test_exact_replay_returns_without_second_insert() -> None:
    collection = Collection()
    registry = (
        LegalEvidenceCommitUncertaintyRegistry(
            collection
        )
    )
    value = _uncertainty()

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


def test_divergent_same_uncertainty_identity_rejects() -> None:
    collection = Collection()
    registry = (
        LegalEvidenceCommitUncertaintyRegistry(
            collection
        )
    )
    first = _uncertainty()

    registry.create_or_replay(
        first,
        session=Session(),
    )

    divergent = replace(
        first,
        provider_integrity_reference=(
            '"different-etag"'
        ),
        fingerprint="",
    )

    assert (
        divergent.uncertainty_id
        == first.uncertainty_id
    )
    assert divergent != first

    with pytest.raises(
        LegalEvidenceCommitUncertaintyRegistryConflictError,
        match="L10A2R_C4B_DIVERGENT_UNCERTAINTY_IDENTITY",
    ):
        registry.create_or_replay(
            divergent,
            session=Session(),
        )

    assert len(collection.rows) == 1


def test_same_ingestion_cannot_bind_second_provider_object() -> None:
    collection = Collection()
    registry = (
        LegalEvidenceCommitUncertaintyRegistry(
            collection
        )
    )

    first = _uncertainty()

    second = _uncertainty(
        storage_reference=(
            "legal-evidence/v1/c4b-second"
        ),
        object_version_reference=(
            "version-c4b-second"
        ),
    )

    assert (
        first.ingestion_intent_id
        == second.ingestion_intent_id
    )
    assert (
        first.uncertainty_id
        != second.uncertainty_id
    )

    registry.create_or_replay(
        first,
        session=Session(),
    )

    with pytest.raises(
        LegalEvidenceCommitUncertaintyRegistryConflictError,
        match="L10A2R_C4B_DIVERGENT_INGESTION_IDENTITY",
    ):
        registry.create_or_replay(
            second,
            session=Session(),
        )

    assert len(collection.rows) == 1


def test_exact_tenant_scoped_get_and_cross_tenant_not_found() -> None:
    collection = Collection()
    registry = (
        LegalEvidenceCommitUncertaintyRegistry(
            collection
        )
    )
    value = _uncertainty()

    registry.create_or_replay(
        value,
        session=Session(),
    )

    assert (
        registry.get(
            tenant_id=value.tenant_id,
            uncertainty_id=value.uncertainty_id,
            session=Session(),
        )
        == value
    )

    with pytest.raises(
        LegalEvidenceCommitUncertaintyRegistryNotFoundError,
        match="L10A2R_C4B_UNCERTAINTY_NOT_FOUND",
    ):
        registry.get(
            tenant_id="tenant-neighbor",
            uncertainty_id=value.uncertainty_id,
            session=Session(),
        )


def test_tenant_list_is_bounded_and_deterministic() -> None:
    collection = Collection()
    registry = (
        LegalEvidenceCommitUncertaintyRegistry(
            collection
        )
    )

    first = _uncertainty(
        ingestion_reference="ingestion-c4b-a",
        reservation_id="reservation-c4b-a",
        storage_reference="legal-evidence/v1/c4b-a",
        object_version_reference="version-c4b-a",
        detected_at=AT,
    )

    second = _uncertainty(
        ingestion_reference="ingestion-c4b-b",
        reservation_id="reservation-c4b-b",
        storage_reference="legal-evidence/v1/c4b-b",
        object_version_reference="version-c4b-b",
        detected_at=(
            AT + timedelta(
                microseconds=1
            )
        ),
    )

    registry.create_or_replay(
        first,
        session=Session(),
    )
    registry.create_or_replay(
        second,
        session=Session(),
    )

    rows = registry.list_tenant_uncertainties(
        tenant_id="tenant-c4b",
        session=Session(),
    )

    assert rows == (
        second,
        first,
    )


def test_persisted_unknown_field_and_fingerprint_corruption_reject() -> None:
    value = _uncertainty()

    for mutation in (
        {
            "unexpected": "field",
        },
        {
            "fingerprint": "f" * 128,
        },
    ):
        collection = Collection()
        corrupted = value.to_dict()
        corrupted.update(
            mutation
        )
        collection.rows.append(
            corrupted
        )

        registry = (
            LegalEvidenceCommitUncertaintyRegistry(
                collection
            )
        )

        with pytest.raises(
            LegalEvidenceCommitUncertaintyRegistryError,
            match="L10A2R_C4B_CORRUPT_UNCERTAINTY",
        ):
            registry.get(
                tenant_id=value.tenant_id,
                uncertainty_id=value.uncertainty_id,
                session=Session(),
            )


def test_public_surface_has_no_reconciliation_provider_or_deletion_authority() -> None:
    public = {
        name.lower()
        for name in dir(
            LegalEvidenceCommitUncertaintyRegistry
        )
        if not name.startswith("_")
    }

    forbidden = {
        "inspect",
        "begin",
        "write_chunk",
        "complete",
        "abort",
        "delete",
        "reconcile",
        "resolve",
        "consume",
        "release",
        "expire",
        "authorize_availability",
        "make_available",
        "publish",
        "invoice",
        "payment",
        "settlement",
    }

    assert forbidden.isdisjoint(
        public
    )


# ARTIFACT: test_legal_evidence_commit_uncertainty_registry.py
# VERSION: v1.0.0-L10A2R-C4B-COMMIT-UNCERTAINTY-REGISTRY-CERT
# AUTHORITY BOUNDARY: immutable uncertainty durability only
# TENANT POSTURE: exact tenant-scoped write/replay/read/list identity
# REPLAY POSTURE: exact replay only; divergent uncertainty/ingestion rejects
# PROVIDER POSTURE: no provider execution
# RECONCILIATION POSTURE: durable uncertainty is not reconciliation outcome
# TTL POSTURE: no TTL; reconciliation evidence is never wall-clock deleted
# DELETION POSTURE: no provider-object deletion authority
# AVAILABILITY POSTURE: no availability authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
