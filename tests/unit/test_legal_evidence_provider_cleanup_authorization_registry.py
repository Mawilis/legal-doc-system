"""Direct certificate for cleanup-authorization durable registry.

VERSION: v1.0.0-L10A2R-C4D6E-A2-PROVIDER-CLEANUP-AUTHORIZATION-REGISTRY-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
PURPOSE:
    Certify the immutable C4D6E-A2 registry contract independently of Mongo.

AUTHORITY BOUNDARY:
    Test evidence only. No provider mutation, deletion execution, IAM binding,
    HTTP/API routing, billing, payment, financial execution or settlement.

TRANSACTION POSTURE:
    Registry methods require a caller-owned active transaction.

TENANT POSTURE:
    All identities and durable reads remain tenant scoped.

TTL POSTURE:
    No TTL deletion index is authorized or expected.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from tools.eos.legal_operations.registry.legal_evidence_provider_cleanup_authorization_registry import (
    COLLECTION,
    INDEX_TENANT_AUTHORIZATION_ID,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_PROVIDER_OBJECT,
    VERSION,
    LegalEvidenceProviderCleanupAuthorizationRegistry,
    LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError,
    LegalEvidenceProviderCleanupAuthorizationRegistryTransactionError,
)

import tests.unit.test_legal_evidence_provider_cleanup_authorization as domain_cert


class _Session:
    def __init__(
        self,
        active: bool = True,
    ) -> None:
        self.in_transaction = active


class _InsertResult:
    inserted_id = "inserted"


class _DuplicateKeyError(Exception):
    pass


_DuplicateKeyError.__name__ = "DuplicateKeyError"


class _Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[dict[str, object]] = []
        self.raise_duplicate_once = False

    def create_index(
        self,
        keys: list[tuple[str, int]],
        *,
        unique: bool,
        name: str,
    ) -> str:
        self.indexes.append(
            {
                "keys": list(keys),
                "unique": unique,
                "name": name,
            }
        )
        return name

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object,
    ) -> dict[str, object] | None:
        assert getattr(session, "in_transaction", False) is True

        for row in self.rows:
            if all(
                row.get(key) == value
                for key, value in query.items()
            ):
                return deepcopy(row)

        return None

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object,
    ) -> _InsertResult:
        assert getattr(session, "in_transaction", False) is True

        if self.raise_duplicate_once:
            self.raise_duplicate_once = False
            raise _DuplicateKeyError("duplicate")

        self.rows.append(deepcopy(document))
        return _InsertResult()


def _authorization():
    return domain_cert._authorize()


def _registry():
    collection = _Collection()
    return (
        LegalEvidenceProviderCleanupAuthorizationRegistry(
            collection
        ),
        collection,
        _Session(),
    )


def test_constants_and_exact_indexes_have_no_ttl() -> None:
    assert VERSION == (
        "v1.0.0-L10A2R-C4D6E-A2-"
        "PROVIDER-CLEANUP-AUTHORIZATION-REGISTRY"
    )
    assert COLLECTION == (
        "legal_evidence_provider_cleanup_authorizations"
    )

    registry, collection, _ = _registry()

    registry.ensure_indexes()

    assert collection.indexes == [
        {
            "keys": [
                ("tenant_id", 1),
                ("authorization_id", 1),
            ],
            "unique": True,
            "name": INDEX_TENANT_AUTHORIZATION_ID,
        },
        {
            "keys": [
                ("tenant_id", 1),
                ("fingerprint", 1),
            ],
            "unique": True,
            "name": INDEX_TENANT_FINGERPRINT,
        },
        {
            "keys": [
                ("tenant_id", 1),
                ("provider_name", 1),
                ("storage_reference", 1),
                ("object_version_reference", 1),
            ],
            "unique": True,
            "name": INDEX_TENANT_PROVIDER_OBJECT,
        },
    ]

    assert all(
        "expireAfterSeconds" not in index
        for index in collection.indexes
    )


def test_create_exact_replay_and_all_lookup_paths() -> None:
    registry, collection, session = _registry()
    authorization = _authorization()

    first = registry.create_or_replay(
        authorization,
        session=session,
    )
    second = registry.create_or_replay(
        authorization,
        session=session,
    )

    assert first == authorization
    assert second == authorization
    assert len(collection.rows) == 1

    assert registry.get_by_authorization_id(
        tenant_id=authorization.tenant_id,
        authorization_id=authorization.authorization_id,
        session=session,
    ) == authorization

    assert registry.get_by_fingerprint(
        tenant_id=authorization.tenant_id,
        fingerprint=authorization.fingerprint,
        session=session,
    ) == authorization

    assert registry.get_by_provider_object(
        tenant_id=authorization.tenant_id,
        provider_name=authorization.provider_name,
        storage_reference=authorization.storage_reference,
        object_version_reference=(
            authorization.object_version_reference
        ),
        session=session,
    ) == authorization


def test_cross_tenant_known_identity_is_absent() -> None:
    registry, _, session = _registry()
    authorization = _authorization()

    registry.create_or_replay(
        authorization,
        session=session,
    )

    assert registry.get_by_authorization_id(
        tenant_id="tenant-neighbor",
        authorization_id=authorization.authorization_id,
        session=session,
    ) is None

    assert registry.get_by_fingerprint(
        tenant_id="tenant-neighbor",
        fingerprint=authorization.fingerprint,
        session=session,
    ) is None

    assert registry.get_by_provider_object(
        tenant_id="tenant-neighbor",
        provider_name=authorization.provider_name,
        storage_reference=authorization.storage_reference,
        object_version_reference=(
            authorization.object_version_reference
        ),
        session=session,
    ) is None


@pytest.mark.parametrize(
    "method",
    (
        "create",
        "get_id",
        "get_fp",
        "get_object",
    ),
)
def test_inactive_transaction_rejects(
    method: str,
) -> None:
    registry, _, _ = _registry()
    authorization = _authorization()
    inactive = _Session(False)

    with pytest.raises(
        LegalEvidenceProviderCleanupAuthorizationRegistryTransactionError,
        match=(
            "L10A2R_C4D6E_A2_"
            "ACTIVE_TRANSACTION_REQUIRED"
        ),
    ):
        if method == "create":
            registry.create_or_replay(
                authorization,
                session=inactive,
            )
        elif method == "get_id":
            registry.get_by_authorization_id(
                tenant_id=authorization.tenant_id,
                authorization_id=authorization.authorization_id,
                session=inactive,
            )
        elif method == "get_fp":
            registry.get_by_fingerprint(
                tenant_id=authorization.tenant_id,
                fingerprint=authorization.fingerprint,
                session=inactive,
            )
        else:
            registry.get_by_provider_object(
                tenant_id=authorization.tenant_id,
                provider_name=authorization.provider_name,
                storage_reference=authorization.storage_reference,
                object_version_reference=(
                    authorization.object_version_reference
                ),
                session=inactive,
            )


def test_same_authorization_id_divergent_evidence_rejects() -> None:
    registry, _, session = _registry()
    original = _authorization()

    registry.create_or_replay(
        original,
        session=session,
    )

    divergent = domain_cert._authorize(
        authorization_id=original.authorization_id,
        reason_reference="different-valid-reason",
    )

    assert divergent.authorization_id == original.authorization_id
    assert divergent.fingerprint != original.fingerprint

    with pytest.raises(
        LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError,
        match="L10A2R_C4D6E_A2_REPLAY_CONFLICT",
    ):
        registry.create_or_replay(
            divergent,
            session=session,
        )


def test_same_provider_object_different_authorization_rejects() -> None:
    registry, _, session = _registry()
    original = _authorization()

    registry.create_or_replay(
        original,
        session=session,
    )

    divergent = domain_cert._authorize(
        authorization_id="cleanup-authorization-a2-other",
        reason_reference="different-valid-reason",
    )

    assert divergent.authorization_id != original.authorization_id
    assert divergent.tenant_id == original.tenant_id
    assert divergent.provider_name == original.provider_name
    assert divergent.storage_reference == original.storage_reference
    assert (
        divergent.object_version_reference
        == original.object_version_reference
    )
    assert divergent.fingerprint != original.fingerprint

    with pytest.raises(
        LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError,
        match="L10A2R_C4D6E_A2_REPLAY_CONFLICT",
    ):
        registry.create_or_replay(
            divergent,
            session=session,
        )


def test_corrupt_persisted_row_rejects() -> None:
    registry, collection, session = _registry()
    authorization = _authorization()

    registry.create_or_replay(
        authorization,
        session=session,
    )

    collection.rows[0]["reason_reference"] = "corrupt"

    with pytest.raises(
        LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError,
        match=(
            "L10A2R_C4D6E_A2_"
            "PERSISTED_DOCUMENT_CORRUPT"
        ),
    ):
        registry.get_by_authorization_id(
            tenant_id=authorization.tenant_id,
            authorization_id=authorization.authorization_id,
            session=session,
        )


def test_authority_injection_persisted_row_rejects() -> None:
    registry, collection, session = _registry()
    authorization = _authorization()

    registry.create_or_replay(
        authorization,
        session=session,
    )

    collection.rows[0]["provider_delete_authorized"] = True

    with pytest.raises(
        LegalEvidenceProviderCleanupAuthorizationRegistryIntegrityError,
        match=(
            "L10A2R_C4D6E_A2_"
            "PERSISTED_DOCUMENT_CORRUPT"
        ),
    ):
        registry.get_by_authorization_id(
            tenant_id=authorization.tenant_id,
            authorization_id=authorization.authorization_id,
            session=session,
        )


def test_duplicate_key_race_requires_exact_replay() -> None:
    registry, collection, session = _registry()
    authorization = _authorization()

    collection.rows.append(
        deepcopy(
            authorization.to_document()
        )
    )
    collection.raise_duplicate_once = True

    replay = registry.create_or_replay(
        authorization,
        session=session,
    )

    assert replay == authorization
    assert len(collection.rows) == 1


def test_no_provider_execution_methods() -> None:
    registry, _, _ = _registry()

    assert not hasattr(registry, "delete")
    assert not hasattr(registry, "delete_object")
    assert not hasattr(registry, "delete_objects")
    assert not hasattr(registry, "execute")
    assert not hasattr(registry, "authorize_actor")


# ARTIFACT: test_legal_evidence_provider_cleanup_authorization_registry.py
# VERSION: v1.0.0-L10A2R-C4D6E-A2-PROVIDER-CLEANUP-AUTHORIZATION-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct durable-registry certificate only
# TENANT POSTURE: exact tenant-scoped identities and absence
# TRANSACTION POSTURE: caller-owned active transaction required
# TTL POSTURE: no TTL deletion index
# PROVIDER MUTATION POSTURE: none
# DELETION EXECUTION POSTURE: none
# FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
