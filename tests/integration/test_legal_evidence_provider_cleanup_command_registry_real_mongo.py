"""Real-Mongo certificate for cleanup-command durable registry.

TITLE: Legal Evidence Provider Cleanup Command Registry Real-Mongo Certificate
VERSION: v1.0.1-L10A2R-C4D6E-A3-P3-P2-CLEANUP-COMMAND-REGISTRY-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the cleanup-command registry against the live Mongo replica
         set with real unique indexes, transactions, rollback, exact replay,
         tenant isolation, corruption rejection and duplicate-race restart.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_evidence_provider_cleanup_command_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Legal Operations / Legal Evidence
CERTIFICATION / UPDATE DATE: 2026-10-02
CHANGELOG:
    v1.0.1 certifies the repaired TransientTransactionError / WriteConflict
    boundary as requiring caller abort plus fresh whole-transaction restart.
    v1.0.0 establishes operational persistence certification against
    wilsyVendorCertRS for immutable cleanup-command intent evidence.
COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE:
    Uses UUID-isolated disposable databases and opaque test identities only.
TENANT BOUNDARY:
    All durable registry identities and reads remain exact tenant scoped.
AUTHORITY BOUNDARY:
    Certifies persistence of cleanup-command intent only. No provider delete,
    provider mutation, storage execution or deletion-truth authority exists.
FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.
"""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha3_512
import json
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_command import (
    LegalEvidenceProviderCleanupCommand,
    SCHEMA as COMMAND_SCHEMA,
    VERSION as COMMAND_VERSION,
)
from tools.eos.legal_operations.registry.legal_evidence_provider_cleanup_command_registry import (
    INDEX_TENANT_CLEANUP_AUTHORIZATION,
    INDEX_TENANT_COMMAND_ID,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_PROVIDER_OBJECT,
    LegalEvidenceProviderCleanupCommandRegistry,
    LegalEvidenceProviderCleanupCommandRegistryIntegrityError,
    LegalEvidenceProviderCleanupCommandRegistryRetryRequiredError,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
REPLICA_SET = "wilsyVendorCertRS"
TENANT = "tenant-p3-p2-real"
OTHER_TENANT = "tenant-p3-p2-real-other"


def _command(
    *,
    tenant_id: str = TENANT,
    command_id: str = "cleanup-command-p3-p2-real",
    cleanup_authorization_id: str = "cleanup-auth-p3-p2-real",
    provider_name: str = "aws_s3",
    storage_reference: str = "opaque/storage/p3-p2-real",
    object_version_reference: str = "version-p3-p2-real",
    reason_reference: str = "reason-p3-p2-real",
) -> LegalEvidenceProviderCleanupCommand:
    payload: dict[str, object] = {
        "schema": COMMAND_SCHEMA,
        "command_version": COMMAND_VERSION,
        "command_id": command_id,
        "tenant_id": tenant_id,
        "principal_id": "principal-p3-p2-real",
        "provider_name": provider_name,
        "storage_reference": storage_reference,
        "object_version_reference": object_version_reference,
        "cleanup_authorization_id": cleanup_authorization_id,
        "cleanup_authorization_fingerprint": "a" * 128,
        "tenant_authorization_decision_id": "decision-p3-p2-real",
        "tenant_authorization_evidence_fingerprint": "b" * 128,
        "issued_at": datetime(
            2026,
            10,
            2,
            12,
            30,
            0,
            tzinfo=timezone.utc,
        ).isoformat(),
        "reason_reference": reason_reference,
    }

    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")

    payload["fingerprint"] = sha3_512(raw).hexdigest()

    return LegalEvidenceProviderCleanupCommand.from_dict(
        payload
    )


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[MongoClient[Any], Any, Any, LegalEvidenceProviderCleanupCommandRegistry]
]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5_000,
        connectTimeoutMS=5_000,
        retryWrites=True,
    )

    hello = client.admin.command("hello")
    assert hello["setName"] == REPLICA_SET
    assert hello["isWritablePrimary"] is True

    database = client[
        f"wilsy_p3_p2_cleanup_command_{uuid.uuid4().hex}"
    ]
    collection = database[
        "legal_evidence_provider_cleanup_commands"
    ]
    registry = LegalEvidenceProviderCleanupCommandRegistry(
        collection
    )
    registry.ensure_indexes()

    try:
        yield client, database, collection, registry
    finally:
        client.drop_database(database.name)
        client.close()


def test_real_topology_and_exact_indexes(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalEvidenceProviderCleanupCommandRegistry,
    ],
) -> None:
    client, _, collection, _ = mongo_context

    hello = client.admin.command("hello")
    assert hello["setName"] == REPLICA_SET
    assert hello["isWritablePrimary"] is True
    assert hello["me"] == "127.0.0.1:27027"

    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
    }

    expected = {
        INDEX_TENANT_COMMAND_ID,
        INDEX_TENANT_FINGERPRINT,
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
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalEvidenceProviderCleanupCommandRegistry,
    ],
) -> None:
    client, database, collection, registry = mongo_context
    value = _command()

    with client.start_session() as session:
        session.start_transaction()
        created = registry.create_or_replay(
            value,
            session=session,
        )
        session.commit_transaction()

    assert created == value
    assert collection.count_documents({}) == 1

    restarted_collection = database[
        "legal_evidence_provider_cleanup_commands"
    ]
    restarted = LegalEvidenceProviderCleanupCommandRegistry(
        restarted_collection
    )

    with client.start_session() as session:
        session.start_transaction()

        replay = restarted.create_or_replay(
            value,
            session=session,
        )

        by_id = restarted.get_by_command_id(
            tenant_id=value.tenant_id,
            command_id=value.command_id,
            session=session,
        )
        by_fingerprint = restarted.get_by_fingerprint(
            tenant_id=value.tenant_id,
            fingerprint=value.fingerprint,
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
    assert by_id == value
    assert by_fingerprint == value
    assert by_authorization == value
    assert by_object == value
    assert collection.count_documents({}) == 1


def test_real_abort_leaves_zero_durable_rows(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalEvidenceProviderCleanupCommandRegistry,
    ],
) -> None:
    client, _, collection, registry = mongo_context

    with client.start_session() as session:
        session.start_transaction()

        registry.create_or_replay(
            _command(),
            session=session,
        )

        assert session.in_transaction is True
        session.abort_transaction()

    assert collection.count_documents({}) == 0


def test_real_cross_tenant_reads_remain_absent(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalEvidenceProviderCleanupCommandRegistry,
    ],
) -> None:
    client, _, _, registry = mongo_context
    value = _command()

    with client.start_session() as session:
        session.start_transaction()
        registry.create_or_replay(
            value,
            session=session,
        )
        session.commit_transaction()

    with client.start_session() as session:
        session.start_transaction()

        assert registry.get_by_command_id(
            tenant_id=OTHER_TENANT,
            command_id=value.command_id,
            session=session,
        ) is None

        assert registry.get_by_fingerprint(
            tenant_id=OTHER_TENANT,
            fingerprint=value.fingerprint,
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


def test_real_divergent_replay_fails_closed(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalEvidenceProviderCleanupCommandRegistry,
    ],
) -> None:
    client, _, collection, registry = mongo_context
    value = _command()

    with client.start_session() as session:
        session.start_transaction()
        registry.create_or_replay(
            value,
            session=session,
        )
        session.commit_transaction()

    divergent = _command(
        command_id="different-command-real",
        cleanup_authorization_id=
            value.cleanup_authorization_id,
        storage_reference="different/storage/real",
        object_version_reference="different-version-real",
        reason_reference="different-reason-real",
    )

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            LegalEvidenceProviderCleanupCommandRegistryIntegrityError,
            match="REPLAY_CONFLICT",
        ):
            registry.create_or_replay(
                divergent,
                session=session,
            )

        session.abort_transaction()

    assert collection.count_documents({}) == 1


def test_real_persisted_corruption_rejects(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalEvidenceProviderCleanupCommandRegistry,
    ],
) -> None:
    client, _, collection, registry = mongo_context
    value = _command()

    collection.insert_one(
        value.to_document()
    )
    collection.update_one(
        {
            "tenant_id": value.tenant_id,
            "command_id": value.command_id,
        },
        {
            "$set": {
                "reason_reference": "tampered-after-persist",
            }
        },
    )

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            LegalEvidenceProviderCleanupCommandRegistryIntegrityError,
            match="PERSISTED_DOCUMENT_CORRUPT",
        ):
            registry.get_by_command_id(
                tenant_id=value.tenant_id,
                command_id=value.command_id,
                session=session,
            )

        session.abort_transaction()


class _DuplicateRaceCollection:
    """Inject one real committed competing row at registry insert time."""

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
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalEvidenceProviderCleanupCommandRegistry,
    ],
) -> None:
    client, _, collection, _ = mongo_context
    value = _command()

    racing = LegalEvidenceProviderCleanupCommandRegistry(
        _DuplicateRaceCollection(collection)
    )

    with client.start_session() as failed_session:
        failed_session.start_transaction()

        with pytest.raises(
            LegalEvidenceProviderCleanupCommandRegistryRetryRequiredError,
            match="WHOLE_TRANSACTION_RETRY_REQUIRED",
        ):
            racing.create_or_replay(
                value,
                session=failed_session,
            )

        assert failed_session.in_transaction is True
        failed_session.abort_transaction()

    assert collection.count_documents({}) == 1

    fresh = LegalEvidenceProviderCleanupCommandRegistry(
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


def test_real_registry_has_no_provider_execution_surface(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
        LegalEvidenceProviderCleanupCommandRegistry,
    ],
) -> None:
    _, _, collection, registry = mongo_context

    for attribute in (
        "delete",
        "delete_object",
        "delete_objects",
        "execute",
        "cleanup_execute",
    ):
        assert not hasattr(registry, attribute)

    assert all(
        "expireAfterSeconds" not in item
        for item in collection.list_indexes()
    )


# ARTIFACT: test_legal_evidence_provider_cleanup_command_registry_real_mongo.py
# VERSION: v1.0.1-L10A2R-C4D6E-A3-P3-P2-CLEANUP-COMMAND-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: operational durable cleanup-command registry certificate only
# TENANT POSTURE: every durable identity, replay and lookup is tenant scoped
# TRANSACTION POSTURE: caller-owned real Mongo transactions certified
# IDEMPOTENCY POSTURE: exact replay only; divergent durable command rejects
# RETRY POSTURE: real duplicate-key race requires abort + fresh transaction restart
# TTL POSTURE: real Mongo index metadata contains no TTL index
# PROVIDER MUTATION POSTURE: none
# DELETION EXECUTION POSTURE: none
# FAIL-CLOSED POSTURE: corruption, collision, transaction and duplicate-race failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
