"""Direct certificate for C4D4A durable retention-constraint registry.

TITLE: Legal Evidence Retention Constraint Registry Direct Certificate
VERSION: v1.0.0-L10A2R-C4D4A-R4-RETENTION-CONSTRAINT-REGISTRY-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
PURPOSE: Certify exact tenant-scoped durable persistence/replay behavior for
         already-valid C4D4A retention constraints without creating later
         retention, hold, orphan, deletion, provider or financial authority.
CERTIFICATION / UPDATE DATE: 2026-10-01
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_evidence_retention_constraint import (
    LegalEvidenceRetentionConstraint,
)
from tools.eos.legal_operations.registry.legal_evidence_retention_constraint_registry import (
    COLLECTION,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_PROVIDER_OBJECT,
    INDEX_TENANT_SOURCE_EVIDENCE,
    LegalEvidenceRetentionConstraintConflictError,
    LegalEvidenceRetentionConstraintNotFoundError,
    LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
    LegalEvidenceRetentionConstraintRegistry,
    LegalEvidenceRetentionConstraintTransactionRequiredError,
)


UTC = timezone.utc
BASE = datetime(
    2026,
    10,
    1,
    12,
    0,
    tzinfo=UTC,
)
SHA_A = "a" * 128


class _Session:
    def __init__(
        self,
        *,
        in_transaction: bool,
    ) -> None:
        self.in_transaction = in_transaction


class _InsertResult:
    acknowledged = True


class _Collection:
    def __init__(
        self,
    ) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[
            tuple[
                tuple[tuple[str, int], ...],
                dict[str, object],
            ]
        ] = []
        self.raise_duplicate = False

    def create_index(
        self,
        keys: list[tuple[str, int]],
        **kwargs: object,
    ) -> str:
        self.indexes.append(
            (
                tuple(keys),
                dict(kwargs),
            )
        )
        return str(
            kwargs.get(
                "name",
                "",
            )
        )

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: _Session,
    ) -> dict[str, object] | None:
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
        session: _Session,
    ) -> _InsertResult:
        assert session.in_transaction is True

        if self.raise_duplicate:
            self.raise_duplicate = False
            raise DuplicateKeyError(
                "duplicate"
            )

        self.rows.append(
            deepcopy(
                document
            )
        )

        return _InsertResult()


def _constraint(
    *,
    tenant_id: str = "tenant-c4d4a-r4",
    provider_name: str = "s3",
    storage_reference: str = "bucket-c4d4a-r4",
    object_version_reference: str = "object-version-c4d4a-r4",
    source_evidence_reference: str = "retention-source-c4d4a-r4",
    source_evidence_fingerprint: str = SHA_A,
    imposed_at: datetime = BASE,
    retain_until: datetime = BASE + timedelta(days=365),
) -> LegalEvidenceRetentionConstraint:
    return LegalEvidenceRetentionConstraint(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        source_evidence_reference=source_evidence_reference,
        source_evidence_fingerprint=source_evidence_fingerprint,
        imposed_at=imposed_at,
        retain_until=retain_until,
    )


def _registry() -> tuple[
    _Collection,
    LegalEvidenceRetentionConstraintRegistry,
    _Session,
]:
    collection = _Collection()

    registry = LegalEvidenceRetentionConstraintRegistry(
        collection
    )

    session = _Session(
        in_transaction=True
    )

    return (
        collection,
        registry,
        session,
    )


def test_collection_identity_is_dedicated() -> None:
    assert (
        COLLECTION
        == "legal_evidence_retention_constraints"
    )


def test_indexes_are_exact_and_have_no_ttl() -> None:
    collection, registry, _ = _registry()

    registry.ensure_indexes()

    assert len(
        collection.indexes
    ) == 3

    by_name = {
        str(
            kwargs["name"]
        ): (
            keys,
            kwargs,
        )
        for keys, kwargs in collection.indexes
    }

    assert set(
        by_name
    ) == {
        INDEX_TENANT_FINGERPRINT,
        INDEX_TENANT_PROVIDER_OBJECT,
        INDEX_TENANT_SOURCE_EVIDENCE,
    }

    fingerprint_keys, fingerprint_kwargs = by_name[
        INDEX_TENANT_FINGERPRINT
    ]

    assert fingerprint_keys == (
        ("tenant_id", 1),
        ("fingerprint", 1),
    )
    assert fingerprint_kwargs["unique"] is True

    object_keys, object_kwargs = by_name[
        INDEX_TENANT_PROVIDER_OBJECT
    ]

    assert object_keys == (
        ("tenant_id", 1),
        ("provider_name", 1),
        ("storage_reference", 1),
        ("object_version_reference", 1),
    )
    assert object_kwargs["unique"] is True

    source_keys, source_kwargs = by_name[
        INDEX_TENANT_SOURCE_EVIDENCE
    ]

    assert source_keys == (
        ("tenant_id", 1),
        ("source_evidence_reference", 1),
    )
    assert source_kwargs["unique"] is False

    for _, kwargs in collection.indexes:
        assert "expireAfterSeconds" not in kwargs


def test_create_requires_active_caller_transaction() -> None:
    collection = _Collection()

    registry = LegalEvidenceRetentionConstraintRegistry(
        collection
    )

    with pytest.raises(
        LegalEvidenceRetentionConstraintTransactionRequiredError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(
            _constraint(),
            session=_Session(
                in_transaction=False
            ),
        )

    assert collection.rows == []


def test_create_and_exact_replay_return_same_value() -> None:
    collection, registry, session = _registry()

    value = _constraint()

    created = registry.create_or_replay(
        value,
        session=session,
    )

    replayed = registry.create_or_replay(
        value,
        session=session,
    )

    assert created == value
    assert replayed == value
    assert len(
        collection.rows
    ) == 1


def test_provider_object_divergence_rejects_without_second_row() -> None:
    collection, registry, session = _registry()

    first = _constraint()

    divergent = _constraint(
        source_evidence_reference=(
            "retention-source-c4d4a-r4-divergent"
        ),
        retain_until=BASE + timedelta(days=730),
    )

    assert divergent.fingerprint != first.fingerprint

    registry.create_or_replay(
        first,
        session=session,
    )

    with pytest.raises(
        LegalEvidenceRetentionConstraintConflictError,
        match="IMMUTABLE_REPLAY_DIVERGENCE",
    ):
        registry.create_or_replay(
            divergent,
            session=session,
        )

    assert len(
        collection.rows
    ) == 1


def test_get_by_fingerprint_and_provider_object_are_tenant_scoped() -> None:
    _, registry, session = _registry()

    value = _constraint()

    registry.create_or_replay(
        value,
        session=session,
    )

    assert (
        registry.get_by_fingerprint(
            tenant_id=value.tenant_id,
            fingerprint=value.fingerprint,
            session=session,
        )
        == value
    )

    assert (
        registry.get_by_provider_object(
            tenant_id=value.tenant_id,
            provider_name=value.provider_name,
            storage_reference=value.storage_reference,
            object_version_reference=(
                value.object_version_reference
            ),
            session=session,
        )
        == value
    )

    with pytest.raises(
        LegalEvidenceRetentionConstraintNotFoundError,
        match="NOT_FOUND",
    ):
        registry.get_by_provider_object(
            tenant_id="tenant-c4d4a-r4-other",
            provider_name=value.provider_name,
            storage_reference=value.storage_reference,
            object_version_reference=(
                value.object_version_reference
            ),
            session=session,
        )


def test_cross_tenant_same_provider_object_remains_isolated() -> None:
    collection, registry, session = _registry()

    first = _constraint(
        tenant_id="tenant-c4d4a-r4-a"
    )

    second = _constraint(
        tenant_id="tenant-c4d4a-r4-b"
    )

    registry.create_or_replay(
        first,
        session=session,
    )

    registry.create_or_replay(
        second,
        session=session,
    )

    assert len(
        collection.rows
    ) == 2

    assert (
        registry.get_by_provider_object(
            tenant_id=first.tenant_id,
            provider_name=first.provider_name,
            storage_reference=first.storage_reference,
            object_version_reference=(
                first.object_version_reference
            ),
            session=session,
        )
        == first
    )

    assert (
        registry.get_by_provider_object(
            tenant_id=second.tenant_id,
            provider_name=second.provider_name,
            storage_reference=second.storage_reference,
            object_version_reference=(
                second.object_version_reference
            ),
            session=session,
        )
        == second
    )


def test_durable_document_uses_exact_aware_iso_chronology() -> None:
    collection, registry, session = _registry()

    value = _constraint()

    registry.create_or_replay(
        value,
        session=session,
    )

    assert len(
        collection.rows
    ) == 1

    row = collection.rows[0]

    assert row["imposed_at"] == value.imposed_at.isoformat()
    assert row["retain_until"] == value.retain_until.isoformat()

    assert isinstance(
        row["imposed_at"],
        str,
    )
    assert isinstance(
        row["retain_until"],
        str,
    )

    assert (
        registry.get_by_fingerprint(
            tenant_id=value.tenant_id,
            fingerprint=value.fingerprint,
            session=session,
        )
        == value
    )


@pytest.mark.parametrize(
    "field",
    (
        "imposed_at",
        "retain_until",
    ),
)
def test_persisted_naive_or_malformed_chronology_rejects(
    field: str,
) -> None:
    collection, registry, session = _registry()

    value = _constraint()

    registry.create_or_replay(
        value,
        session=session,
    )

    collection.rows[0][field] = (
        "2026-10-01T12:00:00"
    )

    with pytest.raises(
        LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
        match="PERSISTED_.*_INVALID",
    ):
        registry.get_by_fingerprint(
            tenant_id=value.tenant_id,
            fingerprint=value.fingerprint,
            session=session,
        )


def test_corrupt_persisted_record_rejects_without_healing() -> None:
    collection, registry, session = _registry()

    value = _constraint()

    registry.create_or_replay(
        value,
        session=session,
    )

    collection.rows[0][
        "source_evidence_fingerprint"
    ] = "0" * 128

    corrupt_before = deepcopy(
        collection.rows[0]
    )

    with pytest.raises(
        LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
        match="PERSISTED_RECORD_INVALID",
    ):
        registry.get_by_fingerprint(
            tenant_id=value.tenant_id,
            fingerprint=value.fingerprint,
            session=session,
        )

    assert collection.rows[0] == corrupt_before


def test_post_construction_tampering_rejects_before_write() -> None:
    collection, registry, session = _registry()

    value = _constraint()

    object.__setattr__(
        value,
        "fingerprint",
        "0" * 128,
    )

    with pytest.raises(
        LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
        match="VALUE_INVALID",
    ):
        registry.create_or_replay(
            value,
            session=session,
        )

    assert collection.rows == []


def test_duplicate_key_requires_whole_transaction_retry() -> None:
    collection, registry, session = _registry()

    collection.raise_duplicate = True

    with pytest.raises(
        LegalEvidenceRetentionConstraintConflictError,
        match="WHOLE_TRANSACTION_RETRY_REQUIRED",
    ):
        registry.create_or_replay(
            _constraint(),
            session=session,
        )

    assert collection.rows == []


def test_registry_surface_has_no_later_authority_or_mutators() -> None:
    source = Path(
        "tools/eos/legal_operations/registry/"
        "legal_evidence_retention_constraint_registry.py"
    ).read_text(
        encoding="utf-8"
    )

    methods = set(
        vars(
            LegalEvidenceRetentionConstraintRegistry
        )
    )

    forbidden_methods = {
        "satisfy_retention",
        "mark_retention_satisfied",
        "release_legal_hold",
        "clear_legal_hold",
        "prove_orphan",
        "authorize_delete",
        "authorize_deletion",
        "delete",
        "update",
        "remove",
    }

    assert methods.isdisjoint(
        forbidden_methods
    )

    assert ".start_transaction(" not in source
    assert ".commit_transaction(" not in source
    assert ".abort_transaction(" not in source
    assert "expireAfterSeconds" not in source
    assert ".delete_one(" not in source
    assert ".delete_many(" not in source
    assert ".update_one(" not in source
    assert ".update_many(" not in source


# ARTIFACT: test_legal_evidence_retention_constraint_registry.py
# VERSION: v1.0.0-L10A2R-C4D4A-R4-RETENTION-CONSTRAINT-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct durable persistence/replay certificate only
# TENANT POSTURE: exact tenant-scoped identities and reads
# TRANSACTION POSTURE: active caller-owned transaction required
# REPLAY POSTURE: exact immutable replay only; divergence fails closed
# CORRUPTION POSTURE: corrupt durable evidence rejects without healing
# CHRONOLOGY POSTURE: imposed_at and retain_until persist as aware ISO text
# TTL POSTURE: zero TTL
# RETENTION POSTURE: no satisfaction or legal-sufficiency authority
# LEGAL HOLD POSTURE: no issue/release/clearance authority
# ORPHAN POSTURE: no orphan proof authority
# DELETION POSTURE: no update/delete/provider mutation authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN CERTIFICATE
