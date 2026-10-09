"""Direct certificate for durable provider-object disownership registry.

VERSION: v1.0.0-L10A2R-C4D6D-A2-DISOWNERSHIP-REGISTRY-CERT
AUTHORITY: WILSY OS Core Governance
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG: v1.0.0-L10A2R-C4D6D-A2 certifies exact tenant-scoped unique
           identities, active transaction ownership, immutable exact replay,
           strict corruption rejection, zero TTL and no orphan/delete authority.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_evidence_provider_object_disownership import (
    LegalEvidenceProviderObjectDisownership,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_object_disownership_registry import (
    COLLECTION,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_PROVIDER_OBJECT,
    INDEX_TENANT_REFERENCE,
    LegalEvidenceProviderObjectDisownershipConflictError,
    LegalEvidenceProviderObjectDisownershipNotFoundError,
    LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError,
    LegalEvidenceProviderObjectDisownershipRegistry,
    LegalEvidenceProviderObjectDisownershipTransactionRequiredError,
)


AT = datetime(
    2026,
    10,
    1,
    4,
    0,
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
        self.rows: list[
            dict[str, object]
        ] = []
        self.indexes: list[
            tuple[
                tuple[tuple[str, int], ...],
                bool,
                str,
                dict[str, object],
            ]
        ] = []
        self.raise_duplicate = False

    def create_index(
        self,
        keys: list[tuple[str, int]],
        *,
        unique: bool,
        name: str,
        **kwargs: object,
    ) -> str:
        self.indexes.append(
            (
                tuple(keys),
                unique,
                name,
                dict(kwargs),
            )
        )
        return name

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: Any,
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
        session: Any,
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


def _value(
    *,
    tenant_id: str = "tenant-c4d6d-a2",
    provider_name: str = "aws_s3",
    storage_reference: str = "legal-evidence/c4d6d-a2/object",
    object_version_reference: str = "version-c4d6d-a2",
    disownership_reference: str = "disownership-c4d6d-a2",
    reason_reference: str = "reason:c4d6d-a2",
) -> LegalEvidenceProviderObjectDisownership:
    return LegalEvidenceProviderObjectDisownership(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        disownership_reference=disownership_reference,
        reason_reference=reason_reference,
        source_evidence_reference="source:c4d6d-a2",
        source_evidence_fingerprint="a" * 128,
        authorization_evidence_reference="authorization:c4d6d-a2",
        authorization_evidence_fingerprint="b" * 128,
        decided_at=AT,
    )


def _registry() -> tuple[
    LegalEvidenceProviderObjectDisownershipRegistry,
    _FakeCollection,
]:
    collection = _FakeCollection()
    return (
        LegalEvidenceProviderObjectDisownershipRegistry(
            collection
        ),
        collection,
    )


def _tx() -> _Session:
    return _Session(
        in_transaction=True
    )


def test_collection_identity_is_dedicated() -> None:
    assert (
        COLLECTION
        == "legal_evidence_provider_object_disownerships"
    )


def test_indexes_are_exact_unique_and_have_no_ttl() -> None:
    registry, collection = _registry()
    registry.ensure_indexes()

    by_name = {
        name: (
            keys,
            unique,
            kwargs,
        )
        for keys, unique, name, kwargs
        in collection.indexes
    }

    assert set(
        by_name
    ) == {
        INDEX_TENANT_REFERENCE,
        INDEX_TENANT_FINGERPRINT,
        INDEX_TENANT_PROVIDER_OBJECT,
    }

    reference = by_name[
        INDEX_TENANT_REFERENCE
    ]
    assert reference[0] == (
        ("tenant_id", 1),
        ("disownership_reference", 1),
    )
    assert reference[1] is True

    fingerprint = by_name[
        INDEX_TENANT_FINGERPRINT
    ]
    assert fingerprint[0] == (
        ("tenant_id", 1),
        ("fingerprint", 1),
    )
    assert fingerprint[1] is True

    provider_object = by_name[
        INDEX_TENANT_PROVIDER_OBJECT
    ]
    assert provider_object[0] == (
        ("tenant_id", 1),
        ("provider_name", 1),
        ("storage_reference", 1),
        ("object_version_reference", 1),
    )
    assert provider_object[1] is True

    for _, _, kwargs in by_name.values():
        assert "expireAfterSeconds" not in kwargs


@pytest.mark.parametrize(
    "session",
    [
        None,
        _Session(
            in_transaction=False
        ),
    ],
)
def test_create_requires_active_caller_transaction(
    session: object,
) -> None:
    registry, _ = _registry()

    with pytest.raises(
        LegalEvidenceProviderObjectDisownershipTransactionRequiredError
    ):
        registry.create_or_replay(
            _value(),
            session=session,
        )


def test_create_and_exact_replay_return_same_value() -> None:
    registry, collection = _registry()
    value = _value()

    created = registry.create_or_replay(
        value,
        session=_tx(),
    )
    replayed = registry.create_or_replay(
        value,
        session=_tx(),
    )

    assert created == value
    assert replayed == value
    assert len(collection.rows) == 1


@pytest.mark.parametrize(
    "changes",
    [
        {
            "reason_reference":
                "reason:divergent"
        },
        {
            "disownership_reference":
                "disownership-divergent"
        },
    ],
)
def test_provider_object_divergence_rejects_without_second_row(
    changes: dict[str, str],
) -> None:
    registry, collection = _registry()
    original = _value()

    registry.create_or_replay(
        original,
        session=_tx(),
    )

    divergent = _value(
        **changes
    )

    with pytest.raises(
        LegalEvidenceProviderObjectDisownershipConflictError
    ):
        registry.create_or_replay(
            divergent,
            session=_tx(),
        )

    assert len(collection.rows) == 1


def test_reference_reuse_for_other_provider_object_rejects() -> None:
    registry, collection = _registry()

    original = _value()
    registry.create_or_replay(
        original,
        session=_tx(),
    )

    divergent = _value(
        storage_reference="legal-evidence/other",
        object_version_reference="other-version",
    )

    with pytest.raises(
        LegalEvidenceProviderObjectDisownershipConflictError
    ):
        registry.create_or_replay(
            divergent,
            session=_tx(),
        )

    assert len(collection.rows) == 1


def test_get_by_reference_and_provider_object_are_tenant_scoped() -> None:
    registry, _ = _registry()
    value = _value()

    registry.create_or_replay(
        value,
        session=_tx(),
    )

    assert (
        registry.get_by_reference(
            tenant_id=value.tenant_id,
            disownership_reference=value.disownership_reference,
            session=_tx(),
        )
        == value
    )

    assert (
        registry.get_by_provider_object(
            tenant_id=value.tenant_id,
            provider_name=value.provider_name,
            storage_reference=value.storage_reference,
            object_version_reference=value.object_version_reference,
            session=_tx(),
        )
        == value
    )

    with pytest.raises(
        LegalEvidenceProviderObjectDisownershipNotFoundError
    ):
        registry.get_by_provider_object(
            tenant_id="tenant-other",
            provider_name=value.provider_name,
            storage_reference=value.storage_reference,
            object_version_reference=value.object_version_reference,
            session=_tx(),
        )


def test_durable_document_uses_exact_aware_iso_datetime_text() -> None:
    registry, collection = _registry()
    value = _value()

    registry.create_or_replay(
        value,
        session=_tx(),
    )

    assert len(collection.rows) == 1

    persisted = collection.rows[0][
        "decided_at"
    ]

    assert isinstance(
        persisted,
        str,
    )
    assert persisted == value.decided_at.isoformat()
    assert persisted.endswith(
        "+00:00"
    )


@pytest.mark.parametrize(
    "persisted",
    [
        datetime(
            2026,
            10,
            1,
            4,
            0,
        ),
        "2026-10-01T04:00:00",
        "not-a-datetime",
    ],
)
def test_persisted_naive_or_malformed_decided_at_rejects(
    persisted: object,
) -> None:
    registry, collection = _registry()
    value = _value()

    registry.create_or_replay(
        value,
        session=_tx(),
    )

    collection.rows[0][
        "decided_at"
    ] = persisted

    before = deepcopy(
        collection.rows[0]
    )

    with pytest.raises(
        LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError
    ):
        registry.get_by_reference(
            tenant_id=value.tenant_id,
            disownership_reference=value.disownership_reference,
            session=_tx(),
        )

    assert collection.rows[0] == before


def test_corrupt_persisted_record_rejects_without_healing() -> None:
    registry, collection = _registry()
    value = _value()

    registry.create_or_replay(
        value,
        session=_tx(),
    )

    collection.rows[0][
        "reason_reference"
    ] = "reason:tampered"

    before = deepcopy(
        collection.rows[0]
    )

    with pytest.raises(
        LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError
    ):
        registry.get_by_reference(
            tenant_id=value.tenant_id,
            disownership_reference=value.disownership_reference,
            session=_tx(),
        )

    assert collection.rows[0] == before


def test_post_construction_value_tampering_rejects_before_write() -> None:
    registry, collection = _registry()
    value = _value()

    object.__setattr__(
        value,
        "provider_name",
        "tampered-provider",
    )

    with pytest.raises(
        LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError
    ):
        registry.create_or_replay(
            value,
            session=_tx(),
        )

    assert collection.rows == []


def test_duplicate_key_requires_whole_transaction_retry() -> None:
    registry, collection = _registry()
    collection.raise_duplicate = True

    with pytest.raises(
        LegalEvidenceProviderObjectDisownershipConflictError,
        match=(
            "L10A2R_C4D6D_A2_"
            "WHOLE_TRANSACTION_RETRY_REQUIRED"
        ),
    ):
        registry.create_or_replay(
            _value(),
            session=_tx(),
        )

    assert collection.rows == []


def test_registry_surface_has_no_orphan_delete_or_update_mutators() -> None:
    forbidden = {
        "authorize_delete",
        "authorize_deletion",
        "delete",
        "delete_object",
        "prove_orphan",
        "provider_delete",
        "update",
        "release_hold",
        "satisfy_retention",
    }

    assert forbidden.isdisjoint(
        dir(
            LegalEvidenceProviderObjectDisownershipRegistry
        )
    )


# ARTIFACT: test_legal_evidence_provider_object_disownership_registry.py
# VERSION: v1.0.0-L10A2R-C4D6D-A2-DISOWNERSHIP-REGISTRY-CERT
# AUTHORITY BOUNDARY: durable persistence/replay certificate only
# TRANSACTION POSTURE: active caller-owned transaction required
# REPLAY POSTURE: exact replay only; divergence fails closed
# CORRUPTION POSTURE: corrupt durable evidence rejects without healing
# TTL POSTURE: zero TTL
# ORPHAN POSTURE: persistence is not orphan proof
# DELETION POSTURE: no update/delete/provider mutation authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
