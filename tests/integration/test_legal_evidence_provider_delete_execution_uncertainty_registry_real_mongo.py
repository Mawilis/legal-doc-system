"""Real-Mongo certificate for provider-delete execution uncertainty registry.

A3-P4-P6C certifies:
- exact real Mongo indexes and no TTL;
- committed durability across a restarted registry;
- exact replay;
- transaction abort writes zero;
- tenant isolation;
- divergent replay fail-closed behavior;
- persisted corruption rejection;
- a real duplicate-key race requiring abort plus fresh transaction restart;
- no provider execution, retry or reconciliation authority.

No provider delete call occurs in this certificate.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_uncertainty import (
    LegalEvidenceProviderDeleteExecutionUncertainty,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_delete_execution_uncertainty_registry import (
    COLLECTION,
    INDEX_TENANT_COMMAND,
    INDEX_TENANT_EXECUTION_EVIDENCE,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_PROVIDER_OBJECT,
    INDEX_TENANT_UNCERTAINTY_ID,
    LegalEvidenceProviderDeleteExecutionUncertaintyRegistry,
    LegalEvidenceProviderDeleteExecutionUncertaintyRegistryIntegrityError,
    LegalEvidenceProviderDeleteExecutionUncertaintyRegistryRetryRequiredError,
)


URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS&directConnection=true"
)
AT = datetime(2026, 10, 2, 16, 0, tzinfo=timezone.utc)
TENANT = "tenant-p6c"
OTHER_TENANT = "tenant-p6c-other"


def _value(
    *,
    uncertainty_id: str = "uncertainty-p6c",
    tenant_id: str = TENANT,
    execution_evidence_id: str = "execution-p6c",
    command_id: str = "command-p6c",
    storage_reference: str = "opaque/storage/p6c",
    object_version_reference: str = "version-p6c",
    command_fingerprint: str = "a" * 128,
    cleanup_authorization_fingerprint: str = "b" * 128,
    execution_evidence_fingerprint: str = "c" * 128,
    recorded_offset_seconds: int = 1,
) -> LegalEvidenceProviderDeleteExecutionUncertainty:
    return LegalEvidenceProviderDeleteExecutionUncertainty(
        uncertainty_id=uncertainty_id,
        tenant_id=tenant_id,
        execution_evidence_id=execution_evidence_id,
        command_id=command_id,
        cleanup_authorization_id="authorization-p6c",
        provider_name="aws_s3",
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        command_fingerprint=command_fingerprint,
        cleanup_authorization_fingerprint=
            cleanup_authorization_fingerprint,
        execution_evidence_fingerprint=
            execution_evidence_fingerprint,
        delete_marker=None,
        delete_marker_version_reference=None,
        executed_at=AT,
        uncertainty_recorded_at=(
            AT + timedelta(seconds=recorded_offset_seconds)
        ),
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

    # Intentionally short: Mongo database names are limited to 63 bytes.
    db_name = f"wilsy_p6c_{uuid4().hex[:20]}"
    database = client[db_name]
    collection = database[COLLECTION]
    registry = (
        LegalEvidenceProviderDeleteExecutionUncertaintyRegistry(
            collection
        )
    )
    registry.ensure_indexes()

    try:
        yield client, database, collection, registry
    finally:
        client.drop_database(db_name)
        client.close()


def test_real_indexes_and_no_ttl(mongo_context: Any) -> None:
    _, _, collection, _ = mongo_context

    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
    }

    expected = {
        INDEX_TENANT_UNCERTAINTY_ID,
        INDEX_TENANT_FINGERPRINT,
        INDEX_TENANT_COMMAND,
        INDEX_TENANT_EXECUTION_EVIDENCE,
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
    value = _value()

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

    restarted = (
        LegalEvidenceProviderDeleteExecutionUncertaintyRegistry(
            collection
        )
    )

    with client.start_session() as session:
        session.start_transaction()

        replay = restarted.create_or_replay(
            value,
            session=session,
        )

        by_id = restarted.get_by_uncertainty_id(
            tenant_id=value.tenant_id,
            uncertainty_id=value.uncertainty_id,
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
        by_execution = restarted.get_by_execution_evidence_id(
            tenant_id=value.tenant_id,
            execution_evidence_id=value.execution_evidence_id,
            session=session,
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
    assert by_id == value
    assert by_fingerprint == value
    assert by_command == value
    assert by_execution == value
    assert by_object == value


def test_real_transaction_abort_writes_zero(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context
    value = _value()

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
            "uncertainty_id": value.uncertainty_id,
        }
    ) == 0


def test_real_cross_tenant_reads_are_absent(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context
    value = _value()

    with client.start_session() as session:
        session.start_transaction()
        registry.create_or_replay(
            value,
            session=session,
        )
        session.commit_transaction()

    with client.start_session() as session:
        session.start_transaction()

        assert registry.get_by_uncertainty_id(
            tenant_id=OTHER_TENANT,
            uncertainty_id=value.uncertainty_id,
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
        assert registry.get_by_execution_evidence_id(
            tenant_id=OTHER_TENANT,
            execution_evidence_id=value.execution_evidence_id,
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


def test_real_divergent_replay_fails_closed(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context
    first = _value()

    second = _value(
        uncertainty_id="uncertainty-p6c-divergent",
        execution_evidence_id="execution-p6c-divergent",
        command_id=first.command_id,
        storage_reference="opaque/storage/p6c-divergent",
        object_version_reference="version-p6c-divergent",
        command_fingerprint="d" * 128,
        execution_evidence_fingerprint="e" * 128,
        recorded_offset_seconds=2,
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
            LegalEvidenceProviderDeleteExecutionUncertaintyRegistryIntegrityError,
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
    value = _value()

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
            "uncertainty_id": value.uncertainty_id,
        },
        {
            "$set": {
                "execution_evidence_fingerprint": "f" * 128,
            }
        },
    )

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            LegalEvidenceProviderDeleteExecutionUncertaintyRegistryIntegrityError,
            match="PERSISTED_DOCUMENT_CORRUPT",
        ):
            registry.get_by_uncertainty_id(
                tenant_id=value.tenant_id,
                uncertainty_id=value.uncertainty_id,
                session=session,
            )

        session.abort_transaction()


class _DuplicateRaceCollection:
    """Inject one competing committed row immediately before insert."""

    def __init__(
        self,
        collection: Any,
        competing: LegalEvidenceProviderDeleteExecutionUncertainty,
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


def test_real_duplicate_key_race_requires_fresh_transaction_restart(
    mongo_context: Any,
) -> None:
    client, _, collection, _ = mongo_context
    value = _value()

    racing = (
        LegalEvidenceProviderDeleteExecutionUncertaintyRegistry(
            _DuplicateRaceCollection(
                collection,
                value,
            )
        )
    )

    with client.start_session() as failed_session:
        failed_session.start_transaction()

        with pytest.raises(
            LegalEvidenceProviderDeleteExecutionUncertaintyRegistryRetryRequiredError,
            match="WHOLE_TRANSACTION_RETRY_REQUIRED",
        ):
            racing.create_or_replay(
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

    fresh = (
        LegalEvidenceProviderDeleteExecutionUncertaintyRegistry(
            collection
        )
    )

    with client.start_session() as fresh_session:
        fresh_session.start_transaction()

        replay = fresh.create_or_replay(
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


def test_real_registry_has_no_provider_execution_surface(
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
    }

    public = {
        name
        for name in dir(
            LegalEvidenceProviderDeleteExecutionUncertaintyRegistry
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
