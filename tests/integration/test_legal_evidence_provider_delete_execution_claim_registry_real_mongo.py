"""Real-Mongo certificate for provider-delete pre-execution claim registry.

A3-P4-P6D4 certifies:
- exact real Mongo unique indexes and no TTL;
- committed durability across registry restart;
- exact immutable replay;
- transaction abort writes zero;
- exact tenant isolation;
- divergent command/provider-object claims fail closed;
- persisted corruption rejects;
- a genuine competing durable claim race leaves exactly one committed claim;
- the losing transaction must abort and restart from fresh state;
- no provider execution, retry, reconciliation, release or absence authority.

No provider call occurs in this certificate.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_claim import (
    LegalEvidenceProviderDeleteExecutionClaim,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_delete_execution_claim_registry import (
    COLLECTION,
    INDEX_TENANT_CLAIM_ID,
    INDEX_TENANT_CLEANUP_AUTHORIZATION,
    INDEX_TENANT_COMMAND,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_PROVIDER_OBJECT,
    LegalEvidenceProviderDeleteExecutionClaimRegistry,
    LegalEvidenceProviderDeleteExecutionClaimRegistryIntegrityError,
    LegalEvidenceProviderDeleteExecutionClaimRegistryRetryRequiredError,
)


URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS&directConnection=true"
)

AT = datetime(2026, 10, 2, 16, 0, tzinfo=timezone.utc)
TENANT = "tenant-p6d4"
OTHER_TENANT = "tenant-p6d4-other"


def _claim(
    *,
    claim_id: str = "claim-p6d4",
    tenant_id: str = TENANT,
    command_id: str = "command-p6d4",
    cleanup_authorization_id: str = "authorization-p6d4",
    storage_reference: str = "opaque/storage/p6d4",
    object_version_reference: str = "version-p6d4",
    command_fingerprint: str = "a" * 128,
    cleanup_authorization_fingerprint: str = "b" * 128,
    claimed_offset_seconds: int = 1,
) -> LegalEvidenceProviderDeleteExecutionClaim:
    return LegalEvidenceProviderDeleteExecutionClaim(
        claim_id=claim_id,
        tenant_id=tenant_id,
        command_id=command_id,
        cleanup_authorization_id=cleanup_authorization_id,
        provider_name="aws_s3",
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        command_fingerprint=command_fingerprint,
        cleanup_authorization_fingerprint=
            cleanup_authorization_fingerprint,
        claimed_at=AT + timedelta(seconds=claimed_offset_seconds),
    )


@pytest.fixture()
def mongo_context() -> Any:
    client = MongoClient(
        URI,
        serverSelectionTimeoutMS=3000,
        retryWrites=True,
    )

    hello = client.admin.command("hello")
    assert hello["setName"] == "wilsyVendorCertRS"
    assert hello["isWritablePrimary"] is True

    db_name = f"wilsy_p6d4_{uuid4().hex[:18]}"
    database = client[db_name]
    collection = database[COLLECTION]

    registry = LegalEvidenceProviderDeleteExecutionClaimRegistry(
        collection
    )
    registry.ensure_indexes()

    try:
        yield client, database, collection, registry
    finally:
        client.drop_database(db_name)
        client.close()


def test_real_indexes_and_no_ttl(
    mongo_context: Any,
) -> None:
    _, _, collection, _ = mongo_context

    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
    }

    expected = {
        INDEX_TENANT_CLAIM_ID,
        INDEX_TENANT_FINGERPRINT,
        INDEX_TENANT_COMMAND,
        INDEX_TENANT_CLEANUP_AUTHORIZATION,
        INDEX_TENANT_PROVIDER_OBJECT,
    }

    assert expected <= set(indexes)

    for name in expected:
        assert indexes[name]["unique"] is True
        assert "expireAfterSeconds" not in indexes[name]

    assert all(
        "expireAfterSeconds" not in item
        for item in indexes.values()
    )


def test_real_create_commit_restart_and_exact_replay(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context
    value = _claim()

    with client.start_session() as session:
        session.start_transaction()

        created = registry.create_or_replay(
            value,
            session=session,
        )

        session.commit_transaction()

    assert created == value
    assert collection.count_documents(
        {
            "tenant_id": value.tenant_id,
            "command_id": value.command_id,
        }
    ) == 1

    restarted = LegalEvidenceProviderDeleteExecutionClaimRegistry(
        collection
    )

    with client.start_session() as session:
        session.start_transaction()

        replay = restarted.create_or_replay(
            value,
            session=session,
        )

        by_claim = restarted.get_by_claim_id(
            tenant_id=value.tenant_id,
            claim_id=value.claim_id,
            session=session,
        )
        by_fingerprint = restarted.get_by_fingerprint(
            tenant_id=value.tenant_id,
            fingerprint=value.fingerprint,
            session=session,
        )
        by_command = restarted.get_by_command_id(
            tenant_id=value.tenant_id,
            command_id=value.command_id,
            session=session,
        )
        by_authorization = (
            restarted.get_by_cleanup_authorization_id(
                tenant_id=value.tenant_id,
                cleanup_authorization_id=
                    value.cleanup_authorization_id,
                session=session,
            )
        )
        by_object = restarted.get_by_provider_object(
            tenant_id=value.tenant_id,
            provider_name=value.provider_name,
            storage_reference=value.storage_reference,
            object_version_reference=
                value.object_version_reference,
            session=session,
        )

        session.commit_transaction()

    assert replay == value
    assert by_claim == value
    assert by_fingerprint == value
    assert by_command == value
    assert by_authorization == value
    assert by_object == value


def test_real_transaction_abort_writes_zero(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context
    value = _claim()

    with client.start_session() as session:
        session.start_transaction()

        registry.create_or_replay(
            value,
            session=session,
        )

        assert session.in_transaction is True
        session.abort_transaction()

    assert collection.count_documents(
        {
            "tenant_id": value.tenant_id,
            "claim_id": value.claim_id,
        }
    ) == 0


def test_real_cross_tenant_reads_are_absent(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context
    value = _claim()

    with client.start_session() as session:
        session.start_transaction()
        registry.create_or_replay(
            value,
            session=session,
        )
        session.commit_transaction()

    with client.start_session() as session:
        session.start_transaction()

        assert registry.get_by_claim_id(
            tenant_id=OTHER_TENANT,
            claim_id=value.claim_id,
            session=session,
        ) is None

        assert registry.get_by_fingerprint(
            tenant_id=OTHER_TENANT,
            fingerprint=value.fingerprint,
            session=session,
        ) is None

        assert registry.get_by_command_id(
            tenant_id=OTHER_TENANT,
            command_id=value.command_id,
            session=session,
        ) is None

        assert registry.get_by_cleanup_authorization_id(
            tenant_id=OTHER_TENANT,
            cleanup_authorization_id=
                value.cleanup_authorization_id,
            session=session,
        ) is None

        assert registry.get_by_provider_object(
            tenant_id=OTHER_TENANT,
            provider_name=value.provider_name,
            storage_reference=value.storage_reference,
            object_version_reference=
                value.object_version_reference,
            session=session,
        ) is None

        session.commit_transaction()


def test_real_divergent_command_claim_fails_closed(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    first = _claim()

    second = _claim(
        claim_id="claim-p6d4-divergent",
        command_id=first.command_id,
        cleanup_authorization_id="authorization-p6d4-other",
        storage_reference="opaque/storage/p6d4-other",
        object_version_reference="version-p6d4-other",
        command_fingerprint="c" * 128,
        cleanup_authorization_fingerprint="d" * 128,
        claimed_offset_seconds=2,
    )

    with client.start_session() as session:
        session.start_transaction()
        registry.create_or_replay(
            first,
            session=session,
        )
        session.commit_transaction()

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            LegalEvidenceProviderDeleteExecutionClaimRegistryIntegrityError,
            match="REPLAY_CONFLICT",
        ):
            registry.create_or_replay(
                second,
                session=session,
            )

        session.abort_transaction()

    assert collection.count_documents(
        {
            "tenant_id": first.tenant_id,
            "command_id": first.command_id,
        }
    ) == 1


def test_real_persisted_corruption_rejects(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context
    value = _claim()

    with client.start_session() as session:
        session.start_transaction()
        registry.create_or_replay(
            value,
            session=session,
        )
        session.commit_transaction()

    collection.update_one(
        {
            "tenant_id": value.tenant_id,
            "claim_id": value.claim_id,
        },
        {
            "$set": {
                "command_fingerprint": "f" * 128,
            }
        },
    )

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            LegalEvidenceProviderDeleteExecutionClaimRegistryIntegrityError,
            match="PERSISTED_DOCUMENT_CORRUPT",
        ):
            registry.get_by_claim_id(
                tenant_id=value.tenant_id,
                claim_id=value.claim_id,
                session=session,
            )

        session.abort_transaction()


class _CompetingClaimCollection:
    """Commit one competing claim immediately before caller insert."""

    def __init__(
        self,
        collection: Any,
        competing: LegalEvidenceProviderDeleteExecutionClaim,
    ) -> None:
        self._collection = collection
        self._competing = competing
        self._injected = False

    def __getattr__(self, name: str) -> Any:
        return getattr(self._collection, name)

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: Any,
    ) -> Any:
        if not self._injected:
            self._collection.insert_one(
                self._competing.to_document()
            )
            self._injected = True

        return self._collection.insert_one(
            document,
            session=session,
        )


def test_real_competing_claim_race_leaves_exactly_one_durable_claim(
    mongo_context: Any,
) -> None:
    client, _, collection, _ = mongo_context
    value = _claim()

    racing_registry = LegalEvidenceProviderDeleteExecutionClaimRegistry(
        _CompetingClaimCollection(
            collection,
            value,
        )
    )

    with client.start_session() as failed_session:
        failed_session.start_transaction()

        with pytest.raises(
            LegalEvidenceProviderDeleteExecutionClaimRegistryRetryRequiredError,
            match="WHOLE_TRANSACTION_RETRY_REQUIRED",
        ):
            racing_registry.create_or_replay(
                value,
                session=failed_session,
            )

        assert failed_session.in_transaction is True
        failed_session.abort_transaction()

    assert collection.count_documents(
        {
            "tenant_id": value.tenant_id,
            "command_id": value.command_id,
        }
    ) == 1

    assert collection.count_documents(
        {
            "tenant_id": value.tenant_id,
            "provider_name": value.provider_name,
            "storage_reference": value.storage_reference,
            "object_version_reference":
                value.object_version_reference,
        }
    ) == 1

    fresh_registry = LegalEvidenceProviderDeleteExecutionClaimRegistry(
        collection
    )

    with client.start_session() as fresh_session:
        fresh_session.start_transaction()

        replay = fresh_registry.create_or_replay(
            value,
            session=fresh_session,
        )

        fresh_session.commit_transaction()

    assert replay == value

    assert collection.count_documents(
        {
            "tenant_id": value.tenant_id,
            "command_id": value.command_id,
        }
    ) == 1


def test_real_registry_has_no_provider_execution_or_claim_release_surface(
    mongo_context: Any,
) -> None:
    _, _, collection, _ = mongo_context

    forbidden = {
        "execute_delete",
        "delete_object",
        "delete_objects",
        "retry_delete",
        "authorize_retry",
        "reconcile",
        "release",
        "delete_claim",
        "expire",
    }

    public = {
        name
        for name in dir(
            LegalEvidenceProviderDeleteExecutionClaimRegistry
        )
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(public)

    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
    }

    assert all(
        "expireAfterSeconds" not in item
        for item in indexes.values()
    )
