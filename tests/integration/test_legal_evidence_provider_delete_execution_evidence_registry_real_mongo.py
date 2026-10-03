"""Real-Mongo certificate for provider-delete execution-evidence registry.

AUTHORITY BOUNDARY: Durable provider-delete execution evidence only. This
certificate proves Mongo durability, exact replay, tenant isolation, corruption
rejection, rollback and concurrent duplicate-race posture. It does not execute
provider deletion or claim provider/Mongo atomicity, reconciliation, cleanup
completion, physical absence or financial truth.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.legal_operations.domain.legal_evidence_provider_delete_execution_evidence import (
    LegalEvidenceProviderDeleteExecutionEvidence,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_delete_execution_evidence_registry import (
    COLLECTION,
    INDEX_TENANT_COMMAND,
    INDEX_TENANT_EXECUTION_EVIDENCE_ID,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_PROVIDER_OBJECT,
    LegalEvidenceProviderDeleteExecutionEvidenceRegistry,
    LegalEvidenceProviderDeleteExecutionEvidenceRegistryIntegrityError,
    LegalEvidenceProviderDeleteExecutionEvidenceRegistryRetryRequiredError,
)


URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
TENANT = "tenant-p5c-real"
OTHER_TENANT = "tenant-p5c-real-other"
AT = datetime(2026, 10, 2, 16, 30, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context():
    client = MongoClient(
        URI,
        serverSelectionTimeoutMS=4000,
        connectTimeoutMS=4000,
    )
    client.admin.command("ping")

    database_name = (
        "wilsy_p5c_del_exec_"
        + uuid.uuid4().hex
    )
    database = client[database_name]
    collection = database[COLLECTION]
    registry = LegalEvidenceProviderDeleteExecutionEvidenceRegistry(
        collection
    )
    registry.ensure_indexes()

    try:
        yield client, database, collection, registry
    finally:
        client.drop_database(database_name)
        client.close()


def _evidence(**overrides: object):
    values: dict[str, object] = {
        "execution_evidence_id": "execution-p5c",
        "tenant_id": TENANT,
        "command_id": "command-p5c",
        "cleanup_authorization_id": "cleanup-auth-p5c",
        "provider_name": "aws_s3",
        "storage_reference": "opaque/storage/p5c",
        "object_version_reference": "version-p5c",
        "command_fingerprint": "c" * 128,
        "cleanup_authorization_fingerprint": "d" * 128,
        "delete_marker": False,
        "delete_marker_version_reference": None,
        "executed_at": AT,
    }
    values.update(overrides)
    return LegalEvidenceProviderDeleteExecutionEvidence(**values)  # type: ignore[arg-type]


def test_real_indexes_and_no_ttl(mongo_context):
    _, _, collection, _ = mongo_context
    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
    }

    expected = {
        INDEX_TENANT_EXECUTION_EVIDENCE_ID,
        INDEX_TENANT_FINGERPRINT,
        INDEX_TENANT_COMMAND,
        INDEX_TENANT_PROVIDER_OBJECT,
    }

    assert expected <= set(indexes)

    for name in expected:
        assert indexes[name]["unique"] is True
        assert "expireAfterSeconds" not in indexes[name]


def test_real_create_commit_restart_and_exact_replay(mongo_context):
    client, database, _, registry = mongo_context
    value = _evidence()

    with client.start_session() as session:
        session.start_transaction()
        created = registry.create_or_replay(
            value,
            session=session,
        )
        session.commit_transaction()

    assert created == value

    restarted = LegalEvidenceProviderDeleteExecutionEvidenceRegistry(
        database[COLLECTION]
    )

    with client.start_session() as session:
        session.start_transaction()
        replay = restarted.create_or_replay(
            value,
            session=session,
        )
        by_id = restarted.get_by_execution_evidence_id(
            tenant_id=TENANT,
            execution_evidence_id=value.execution_evidence_id,
            session=session,
        )
        by_command = restarted.get_by_command_id(
            tenant_id=TENANT,
            command_id=value.command_id,
            session=session,
        )
        by_object = restarted.get_by_provider_object(
            tenant_id=TENANT,
            provider_name=value.provider_name,
            storage_reference=value.storage_reference,
            object_version_reference=value.object_version_reference,
            session=session,
        )
        session.commit_transaction()

    assert replay == value
    assert by_id == value
    assert by_command == value
    assert by_object == value


def test_real_transaction_abort_writes_zero(mongo_context):
    client, _, collection, registry = mongo_context
    value = _evidence(
        execution_evidence_id="execution-abort",
        command_id="command-abort",
        storage_reference="opaque/storage/abort",
        object_version_reference="version-abort",
    )

    with client.start_session() as session:
        session.start_transaction()
        registry.create_or_replay(
            value,
            session=session,
        )
        assert session.in_transaction is True
        session.abort_transaction()

    assert collection.count_documents(
        {"execution_evidence_id": value.execution_evidence_id}
    ) == 0


def test_real_cross_tenant_reads_are_absent(mongo_context):
    client, _, _, registry = mongo_context
    value = _evidence(
        execution_evidence_id="execution-tenant",
        command_id="command-tenant",
        storage_reference="opaque/storage/tenant",
        object_version_reference="version-tenant",
    )

    with client.start_session() as session:
        session.start_transaction()
        registry.create_or_replay(
            value,
            session=session,
        )
        session.commit_transaction()

    with client.start_session() as session:
        session.start_transaction()
        assert registry.get_by_execution_evidence_id(
            tenant_id=OTHER_TENANT,
            execution_evidence_id=value.execution_evidence_id,
            session=session,
        ) is None
        assert registry.get_by_command_id(
            tenant_id=OTHER_TENANT,
            command_id=value.command_id,
            session=session,
        ) is None
        session.commit_transaction()


def test_real_divergent_replay_fails_closed(mongo_context):
    client, _, _, registry = mongo_context
    value = _evidence(
        execution_evidence_id="execution-divergent",
        command_id="command-divergent",
        storage_reference="opaque/storage/divergent",
        object_version_reference="version-divergent",
    )

    with client.start_session() as session:
        session.start_transaction()
        registry.create_or_replay(value, session=session)
        session.commit_transaction()

    divergent = _evidence(
        execution_evidence_id=value.execution_evidence_id,
        command_id=value.command_id,
        storage_reference="opaque/storage/different",
        object_version_reference="version-different",
    )

    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(
            LegalEvidenceProviderDeleteExecutionEvidenceRegistryIntegrityError
        ):
            registry.create_or_replay(
                divergent,
                session=session,
            )
        session.abort_transaction()


def test_real_persisted_corruption_rejects(mongo_context):
    client, _, collection, registry = mongo_context
    value = _evidence(
        execution_evidence_id="execution-corrupt",
        command_id="command-corrupt",
        storage_reference="opaque/storage/corrupt",
        object_version_reference="version-corrupt",
    )

    with client.start_session() as session:
        session.start_transaction()
        registry.create_or_replay(value, session=session)
        session.commit_transaction()

    collection.update_one(
        {"execution_evidence_id": value.execution_evidence_id},
        {"$set": {"storage_reference": "tampered/storage"}},
    )

    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(
            LegalEvidenceProviderDeleteExecutionEvidenceRegistryIntegrityError
        ):
            registry.get_by_execution_evidence_id(
                tenant_id=TENANT,
                execution_evidence_id=value.execution_evidence_id,
                session=session,
            )
        session.abort_transaction()


class _DuplicateRaceCollection:
    """Inject one committed competing insert after pre-read and before insert."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        self._collection = collection
        self._seeded = False

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: Any,
    ) -> Any:
        return self._collection.find_one(
            query,
            session=session,
        )

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: Any,
    ) -> Any:
        if not self._seeded:
            self._collection.insert_one(
                dict(document)
            )
            self._seeded = True

        return self._collection.insert_one(
            dict(document),
            session=session,
        )


def test_real_duplicate_key_race_requires_fresh_transaction_restart(
    mongo_context,
):
    client, _, collection, _ = mongo_context
    value = _evidence(
        execution_evidence_id="execution-race",
        command_id="command-race",
        storage_reference="opaque/storage/race",
        object_version_reference="version-race",
    )

    racing = LegalEvidenceProviderDeleteExecutionEvidenceRegistry(
        _DuplicateRaceCollection(collection)
    )

    with client.start_session() as failed_session:
        failed_session.start_transaction()

        with pytest.raises(
            LegalEvidenceProviderDeleteExecutionEvidenceRegistryRetryRequiredError,
            match="WHOLE_TRANSACTION_RETRY_REQUIRED",
        ):
            racing.create_or_replay(
                value,
                session=failed_session,
            )

        assert failed_session.in_transaction is True
        failed_session.abort_transaction()

    assert collection.count_documents({}) == 1

    fresh = LegalEvidenceProviderDeleteExecutionEvidenceRegistry(
        collection
    )

    with client.start_session() as fresh_session:
        fresh_session.start_transaction()

        replay = fresh.create_or_replay(
            value,
            session=fresh_session,
        )

        fresh_session.commit_transaction()

    assert replay == value
    assert collection.count_documents({}) == 1


def test_real_registry_has_no_provider_execution_surface(mongo_context):
    _, _, _, registry = mongo_context

    public = {
        name
        for name in dir(registry)
        if not name.startswith("_")
        and callable(getattr(registry, name))
    }

    assert "delete" not in public
    assert "delete_object" not in public
    assert "reconcile" not in public
    assert "mark_completed" not in public
