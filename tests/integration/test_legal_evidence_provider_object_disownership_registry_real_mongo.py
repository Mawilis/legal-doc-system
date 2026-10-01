"""Real-Mongo certificate for provider-object disownership durability.

TITLE: Legal Evidence Provider Object Disownership Registry Real-Mongo Certificate
VERSION: v1.0.0-L10A2R-C4D6D-A2-DISOWNERSHIP-REGISTRY-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance
PURPOSE: Certify actual MongoDB replica-set indexes, caller-owned transactions,
         durable restart replay, rollback, tenant opacity, immutable divergence,
         corruption rejection and duplicate-key whole-transaction retry.
CERTIFICATION / UPDATE DATE: 2026-10-01

AUTHORITY BOUNDARY:
This certificate proves durable disownership persistence/replay only.
It grants no authorized issuance, orphan proof, retention/legal-hold conclusion,
deletion authorization or provider mutation.

Mongo transactions are owned by the test caller.
No TTL deletion is permitted.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import os
from typing import Any
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

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


MONGO_URI = os.environ.get(
    "WILSY_C4D6D_A2_MONGO_URI",
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
    "&directConnection=true",
)

AT = datetime(
    2026,
    10,
    1,
    4,
    30,
    tzinfo=timezone.utc,
)


def _value(
    *,
    tenant_id: str,
    disownership_reference: str,
    storage_reference: str = "legal-evidence/c4d6d-a2-real/object",
    object_version_reference: str = "version-c4d6d-a2-real",
    reason_reference: str = "reason:c4d6d-a2-real",
) -> LegalEvidenceProviderObjectDisownership:
    return LegalEvidenceProviderObjectDisownership(
        tenant_id=tenant_id,
        provider_name="aws_s3",
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        disownership_reference=disownership_reference,
        reason_reference=reason_reference,
        source_evidence_reference="source:c4d6d-a2-real",
        source_evidence_fingerprint="a" * 128,
        authorization_evidence_reference="authorization:c4d6d-a2-real",
        authorization_evidence_fingerprint="b" * 128,
        decided_at=AT,
    )


def _start(
    session: Any,
) -> None:
    session.start_transaction(
        read_concern=ReadConcern(
            "snapshot"
        ),
        write_concern=WriteConcern(
            w="majority",
            j=True,
        ),
    )


@pytest.fixture()
def mongo_context() -> Any:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=4000,
    )

    hello = client.admin.command(
        "hello"
    )

    assert hello.get("ok") == 1
    assert hello.get("setName") == "wilsyVendorCertRS"
    assert hello.get("isWritablePrimary") is True

    database_name = (
        "wilsy_c4d6d_a2_"
        + uuid4().hex
    )

    database = client[
        database_name
    ]
    collection = database[
        COLLECTION
    ]

    registry = LegalEvidenceProviderObjectDisownershipRegistry(
        collection
    )

    try:
        yield (
            client,
            database,
            collection,
            registry,
        )
    finally:
        client.drop_database(
            database_name
        )
        client.close()


def test_real_indexes_exact_unique_and_no_ttl(
    mongo_context: Any,
) -> None:
    _, _, collection, registry = mongo_context

    registry.ensure_indexes()

    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
    }

    assert set(
        indexes
    ) == {
        "_id_",
        INDEX_TENANT_REFERENCE,
        INDEX_TENANT_FINGERPRINT,
        INDEX_TENANT_PROVIDER_OBJECT,
    }

    reference = indexes[
        INDEX_TENANT_REFERENCE
    ]
    assert list(
        reference["key"].items()
    ) == [
        ("tenant_id", 1),
        ("disownership_reference", 1),
    ]
    assert reference.get(
        "unique"
    ) is True

    fingerprint = indexes[
        INDEX_TENANT_FINGERPRINT
    ]
    assert list(
        fingerprint["key"].items()
    ) == [
        ("tenant_id", 1),
        ("fingerprint", 1),
    ]
    assert fingerprint.get(
        "unique"
    ) is True

    provider_object = indexes[
        INDEX_TENANT_PROVIDER_OBJECT
    ]
    assert list(
        provider_object["key"].items()
    ) == [
        ("tenant_id", 1),
        ("provider_name", 1),
        ("storage_reference", 1),
        ("object_version_reference", 1),
    ]
    assert provider_object.get(
        "unique"
    ) is True

    assert all(
        "expireAfterSeconds"
        not in item
        for item in indexes.values()
    )


def test_real_bson_row_persists_decided_at_as_exact_iso_text(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    tenant = (
        "tenant-c4d6d-a2-iso-"
        + uuid4().hex
    )

    value = _value(
        tenant_id=tenant,
        disownership_reference="disownership-real-iso",
    )

    registry.ensure_indexes()

    with client.start_session() as session:
        _start(
            session
        )

        registry.create_or_replay(
            value,
            session=session,
        )

        session.commit_transaction()

    raw = collection.find_one(
        {
            "tenant_id":
                tenant,
        }
    )

    assert raw is not None
    assert isinstance(
        raw["decided_at"],
        str,
    )
    assert (
        raw["decided_at"]
        == value.decided_at.isoformat()
    )
    assert raw[
        "decided_at"
    ].endswith(
        "+00:00"
    )


def test_real_commit_restart_replay_reads_and_tenant_opacity(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    tenant = (
        "tenant-c4d6d-a2-real-"
        + uuid4().hex
    )

    value = _value(
        tenant_id=tenant,
        disownership_reference="disownership-real-replay",
    )

    registry.ensure_indexes()

    with client.start_session() as session:
        _start(
            session
        )
        created = registry.create_or_replay(
            value,
            session=session,
        )
        session.commit_transaction()

    assert created == value
    assert collection.count_documents(
        {
            "tenant_id":
                tenant,
        }
    ) == 1

    restarted = LegalEvidenceProviderObjectDisownershipRegistry(
        collection
    )

    with client.start_session() as session:
        _start(
            session
        )

        replayed = restarted.create_or_replay(
            value,
            session=session,
        )

        by_reference = restarted.get_by_reference(
            tenant_id=tenant,
            disownership_reference=value.disownership_reference,
            session=session,
        )

        by_object = restarted.get_by_provider_object(
            tenant_id=tenant,
            provider_name=value.provider_name,
            storage_reference=value.storage_reference,
            object_version_reference=value.object_version_reference,
            session=session,
        )

        with pytest.raises(
            LegalEvidenceProviderObjectDisownershipNotFoundError
        ):
            restarted.get_by_provider_object(
                tenant_id=tenant + "-other",
                provider_name=value.provider_name,
                storage_reference=value.storage_reference,
                object_version_reference=value.object_version_reference,
                session=session,
            )

        session.commit_transaction()

    assert replayed == value
    assert by_reference == value
    assert by_object == value
    assert collection.count_documents(
        {
            "tenant_id":
                tenant,
        }
    ) == 1


def test_real_inactive_transaction_rejects_before_write(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    value = _value(
        tenant_id="tenant-c4d6d-a2-inactive-" + uuid4().hex,
        disownership_reference="disownership-inactive",
    )

    with client.start_session() as session:
        with pytest.raises(
            LegalEvidenceProviderObjectDisownershipTransactionRequiredError
        ):
            registry.create_or_replay(
                value,
                session=session,
            )

    assert collection.count_documents(
        {}
    ) == 0


def test_real_aborted_transaction_leaves_no_row(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    value = _value(
        tenant_id="tenant-c4d6d-a2-abort-" + uuid4().hex,
        disownership_reference="disownership-abort",
    )

    registry.ensure_indexes()

    with client.start_session() as session:
        _start(
            session
        )

        registry.create_or_replay(
            value,
            session=session,
        )

        assert collection.count_documents(
            {
                "tenant_id":
                    value.tenant_id,
            },
            session=session,
        ) == 1

        session.abort_transaction()

    assert collection.count_documents(
        {
            "tenant_id":
                value.tenant_id,
        }
    ) == 0


def test_real_provider_object_divergence_rejects_without_second_row(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    tenant = (
        "tenant-c4d6d-a2-divergent-"
        + uuid4().hex
    )

    original = _value(
        tenant_id=tenant,
        disownership_reference="disownership-divergent-original",
    )

    divergent = _value(
        tenant_id=tenant,
        disownership_reference="disownership-divergent-other",
        reason_reference="reason:divergent-other",
    )

    registry.ensure_indexes()

    with client.start_session() as session:
        _start(
            session
        )
        registry.create_or_replay(
            original,
            session=session,
        )
        session.commit_transaction()

    with client.start_session() as session:
        _start(
            session
        )

        try:
            with pytest.raises(
                LegalEvidenceProviderObjectDisownershipConflictError
            ):
                registry.create_or_replay(
                    divergent,
                    session=session,
                )
        finally:
            if session.in_transaction:
                session.abort_transaction()

    assert collection.count_documents(
        {
            "tenant_id":
                tenant,
        }
    ) == 1


def test_real_corruption_rejects_without_healing(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    tenant = (
        "tenant-c4d6d-a2-corrupt-"
        + uuid4().hex
    )

    value = _value(
        tenant_id=tenant,
        disownership_reference="disownership-corrupt",
    )

    registry.ensure_indexes()

    with client.start_session() as session:
        _start(
            session
        )
        registry.create_or_replay(
            value,
            session=session,
        )
        session.commit_transaction()

    collection.update_one(
        {
            "tenant_id":
                tenant,
            "disownership_reference":
                value.disownership_reference,
        },
        {
            "$set": {
                "reason_reference":
                    "reason:tampered"
            }
        },
    )

    before = collection.find_one(
        {
            "tenant_id":
                tenant,
        }
    )
    assert before is not None

    with client.start_session() as session:
        _start(
            session
        )

        try:
            with pytest.raises(
                LegalEvidenceProviderObjectDisownershipPersistedRecordInvalidError
            ):
                registry.get_by_reference(
                    tenant_id=tenant,
                    disownership_reference=value.disownership_reference,
                    session=session,
                )
        finally:
            if session.in_transaction:
                session.abort_transaction()

    after = collection.find_one(
        {
            "tenant_id":
                tenant,
        }
    )

    assert after == before


def test_real_duplicate_key_requires_abort_then_fresh_transaction_replays(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    tenant = (
        "tenant-c4d6d-a2-race-"
        + uuid4().hex
    )

    value = _value(
        tenant_id=tenant,
        disownership_reference="disownership-race",
    )

    registry.ensure_indexes()

    # Commit one durable winner exactly as another transaction could have done.
    with client.start_session() as winner:
        _start(
            winner
        )
        registry.create_or_replay(
            value,
            session=winner,
        )
        winner.commit_transaction()

    # Prove the duplicate-key branch itself is fail-closed with a real
    # DuplicateKeyError by hiding the winner from the pre-read phase only.
    original_find = registry._find_identity_rows

    def hidden_rows(
        candidate: LegalEvidenceProviderObjectDisownership,
        *,
        session: Any,
    ) -> tuple[object | None, object | None, object | None]:
        return (
            None,
            None,
            None,
        )

    registry._find_identity_rows = hidden_rows

    with client.start_session() as loser:
        _start(
            loser
        )

        try:
            with pytest.raises(
                LegalEvidenceProviderObjectDisownershipConflictError,
                match=(
                    "L10A2R_C4D6D_A2_"
                    "WHOLE_TRANSACTION_RETRY_REQUIRED"
                ),
            ) as captured:
                registry.create_or_replay(
                    value,
                    session=loser,
                )

            assert isinstance(
                captured.value.__cause__,
                DuplicateKeyError,
            )
        finally:
            if loser.in_transaction:
                loser.abort_transaction()

    registry._find_identity_rows = original_find

    # Fresh caller-owned transaction can now prove ordinary exact replay.
    with client.start_session() as retry:
        _start(
            retry
        )

        replayed = registry.create_or_replay(
            value,
            session=retry,
        )

        retry.commit_transaction()

    assert replayed == value

    assert collection.count_documents(
        {
            "tenant_id":
                tenant,
        }
    ) == 1


# ARTIFACT: test_legal_evidence_provider_object_disownership_registry_real_mongo.py
# VERSION: v1.0.0-L10A2R-C4D6D-A2-DISOWNERSHIP-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: actual Mongo durability/replay evidence only
# TENANT POSTURE: exact tenant-scoped identity/read opacity
# TRANSACTION POSTURE: caller owns active transaction; duplicate race requires retry
# REPLAY POSTURE: restart-safe exact replay only
# CORRUPTION POSTURE: corrupt durable evidence rejects without healing
# TTL POSTURE: exact indexes and no TTL deletion
# ORPHAN POSTURE: durable disownership persistence is not orphan proof
# DELETION POSTURE: no delete authorization or provider mutation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
