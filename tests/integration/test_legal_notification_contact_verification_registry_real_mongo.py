"""Real-Mongo certificate for H7C Legal notification-contact verification.

TITLE: WILSY OS Legal Notification Contact Verification Registry Real-Mongo Certificate
VERSION: v1.0.0-L8-8H7C-LEGAL-NOTIFICATION-CONTACT-VERIFICATION-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Direct physical certification of H7C verification persistence.
EPITOME: Prove sanctioned replica-set topology, caller-owned transactions,
         exact non-TTL indexes, digest-only persistence, exact replay,
         tenant/token/principal isolation, microsecond preservation, lifecycle
         CAS, abort durability, corruption rejection and competing create safety.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_notification_contact_verification_registry_real_mongo.py
COLLABORATION / OWNERSHIP: H7C registry is the production subject; this
                           certificate owns only synthetic UUID-isolated Mongo
                           evidence. H7B contact authority is never created.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0-L8-8H7C-LEGAL-NOTIFICATION-CONTACT-VERIFICATION-REGISTRY-REAL-MONGO-CERT
           establishes physical topology, index, transaction, replay, scope,
           microsecond, lifecycle CAS, rollback, corruption and race evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic SHA3-shaped digests only. Raw contact
                             addresses and raw verification tokens are absent.
TENANT BOUNDARY: All operational queries are exact synthetic tenant scoped.
AUTHORITY BOUNDARY: H7C persistence evidence only. No H7B contact authority,
                    IAM, HTTP, SMTP, dispatch, delivery or Court authority.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Every operational registry call executes inside a
                      caller-owned already-active Mongo transaction.
FAIL-CLOSED DECLARATION: Wrong topology, missing sessions, index drift,
                         corruption, replay divergence, rollback failure or
                         unsafe concurrency fails certification. No skips.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from threading import Barrier
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_notification_contact_verification import (
    LegalNotificationContactChannel,
    LegalNotificationContactVerification,
    LegalNotificationContactVerificationStatus,
)
from tools.eos.legal_operations.registry.legal_notification_contact_verification_registry import (
    COLLECTION,
    IDENTITY_INDEX,
    PRINCIPAL_SCOPE_INDEX,
    TOKEN_INDEX,
    LegalNotificationContactVerificationRegistry,
    LegalNotificationContactVerificationRegistryConflictError,
    LegalNotificationContactVerificationRegistryPersistedRecordInvalidError,
    LegalNotificationContactVerificationRegistryPersistenceError,
    LegalNotificationContactVerificationRegistryRetryTransactionError,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

NOW = datetime(2026, 10, 12, 19, 15, 0, 654321, tzinfo=timezone.utc)
EXPIRES = NOW + timedelta(minutes=30)
ADDRESS_DIGEST = "a" * 128
TOKEN_DIGEST = "b" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Provide one sanctioned replica set and destroy only its UUID database."""

    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None

    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(f"L8_8H7C_MONGO_UNAVAILABLE:{type(error).__name__}")

        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail("L8_8H7C_WRONG_REPLICA_SET")

        if hello.get(
            "isWritablePrimary",
            hello.get("ismaster"),
        ) is not True:
            pytest.fail("L8_8H7C_NO_WRITABLE_PRIMARY")

        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.fail("L8_8H7C_SESSIONS_UNAVAILABLE")

        database = client[
            f"wilsy_h7c_nv_{uuid.uuid4().hex}"
        ]

        collection = database.get_collection(
            COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )

        LegalNotificationContactVerificationRegistry(
            collection
        ).ensure_indexes()

        yield client, database, collection

    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _verification(
    tenant_id: str,
    *,
    verification_id: str = "legal-verification-1",
    principal_id: str = "principal-1",
    token_digest: str = TOKEN_DIGEST,
    issued_at: datetime = NOW,
    expires_at: datetime = EXPIRES,
) -> LegalNotificationContactVerification:
    """Create one synthetic immutable H7A verification."""

    return LegalNotificationContactVerification.issue(
        tenant_id=tenant_id,
        verification_id=verification_id,
        principal_id=principal_id,
        channel=LegalNotificationContactChannel.EMAIL,
        address_digest=ADDRESS_DIGEST,
        token_digest=token_digest,
        issued_at=issued_at,
        expires_at=expires_at,
    )


def _commit_create(
    client: MongoClient[Any],
    collection: Any,
    value: LegalNotificationContactVerification,
) -> LegalNotificationContactVerification:
    """Persist one verification inside a caller-owned transaction."""

    registry = LegalNotificationContactVerificationRegistry(collection)

    with client.start_session() as session:
        with session.start_transaction():
            return registry.create(value, session=session)


def test_real_topology_is_writable_replica_set_with_sessions(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, _ = mongo_context

    hello = client.admin.command("hello")

    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert hello.get(
        "isWritablePrimary",
        hello.get("ismaster"),
    ) is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None


def test_real_index_metadata_is_exact_unique_and_has_no_ttl(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context

    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
        if item["name"] != "_id_"
    }

    assert set(indexes) == {
        IDENTITY_INDEX,
        TOKEN_INDEX,
        PRINCIPAL_SCOPE_INDEX,
    }

    assert dict(indexes[IDENTITY_INDEX]["key"]) == {
        "tenant_id": 1,
        "verification_id": 1,
    }
    assert indexes[IDENTITY_INDEX].get("unique") is True

    assert dict(indexes[TOKEN_INDEX]["key"]) == {
        "tenant_id": 1,
        "token_digest": 1,
    }
    assert indexes[TOKEN_INDEX].get("unique") is True

    assert dict(indexes[PRINCIPAL_SCOPE_INDEX]["key"]) == {
        "tenant_id": 1,
        "principal_id": 1,
        "channel": 1,
        "issued_at": 1,
    }
    assert indexes[PRINCIPAL_SCOPE_INDEX].get("unique") is not True

    assert all(
        "expireAfterSeconds" not in item
        for item in indexes.values()
    )


def test_real_commit_exact_replay_digest_only_shape_and_microseconds(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-replay-{uuid.uuid4().hex}"
    value = _verification(tenant)

    assert _commit_create(client, collection, value) == value
    assert _commit_create(client, collection, value) == value

    assert collection.count_documents({"tenant_id": tenant}) == 1

    raw = collection.find_one({"tenant_id": tenant})
    assert isinstance(raw, dict)

    expected = value.to_dict()

    assert set(raw) == set(expected) | {"_id"}
    assert {
        key: value
        for key, value in raw.items()
        if key != "_id"
    } == expected

    assert "email" not in raw
    assert "address" not in raw
    assert "raw_email" not in raw
    assert "raw_token" not in raw

    registry = LegalNotificationContactVerificationRegistry(collection)

    with client.start_session() as session:
        with session.start_transaction():
            readback = registry.get_by_id(
                tenant,
                value.verification_id,
                session=session,
            )

    assert readback == value
    assert readback is not None
    assert readback.issued_at.microsecond == 654321
    assert readback.expires_at.microsecond == EXPIRES.microsecond
    assert raw["issued_at"] == expected["issued_at"]
    assert raw["expires_at"] == expected["expires_at"]


def test_real_tenant_token_and_principal_reads_are_exactly_scoped(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalNotificationContactVerificationRegistry(collection)

    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"

    first = _verification(
        tenant_a,
        verification_id="legal-verification-a1",
        principal_id="principal-a",
        token_digest="c" * 128,
    )
    second = _verification(
        tenant_a,
        verification_id="legal-verification-a2",
        principal_id="principal-a",
        token_digest="d" * 128,
        issued_at=NOW + timedelta(seconds=1),
        expires_at=EXPIRES + timedelta(seconds=1),
    )
    foreign = _verification(
        tenant_b,
        verification_id="legal-verification-b1",
        principal_id="principal-a",
        token_digest="e" * 128,
    )

    for value in (first, second, foreign):
        assert _commit_create(client, collection, value) == value

    with client.start_session() as session:
        with session.start_transaction():
            assert registry.get_by_id(
                tenant_a,
                first.verification_id,
                session=session,
            ) == first

            assert registry.get_by_id(
                tenant_a,
                foreign.verification_id,
                session=session,
            ) is None

            assert registry.get_by_token_digest(
                tenant_a,
                first.token_digest,
                session=session,
            ) == first

            assert registry.get_by_token_digest(
                tenant_a,
                foreign.token_digest,
                session=session,
            ) is None

            principal_values = registry.list_principal_scope(
                tenant_a,
                "principal-a",
                LegalNotificationContactChannel.EMAIL,
                session=session,
            )

    assert principal_values == (first, second)
    assert collection.count_documents({"tenant_id": tenant_a}) == 2
    assert collection.count_documents({"tenant_id": tenant_b}) == 1


def test_real_caller_abort_leaves_zero_rows(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalNotificationContactVerificationRegistry(collection)

    tenant = f"tenant-abort-{uuid.uuid4().hex}"
    value = _verification(tenant)

    with client.start_session() as session:
        session.start_transaction()

        registry.create(
            value,
            session=session,
        )

        assert collection.count_documents(
            {"tenant_id": tenant},
            session=session,
        ) == 1

        session.abort_transaction()

    assert collection.count_documents({"tenant_id": tenant}) == 0


def test_real_consume_cas_exact_replay_and_divergent_stale_rejection(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalNotificationContactVerificationRegistry(collection)

    tenant = f"tenant-consume-{uuid.uuid4().hex}"
    source = _verification(tenant)
    _commit_create(client, collection, source)

    consumed_at = NOW + timedelta(
        minutes=1,
        microseconds=123456,
    )

    with client.start_session() as session:
        with session.start_transaction():
            consumed = registry.consume(
                source,
                consumed_at,
                session=session,
            )

    assert (
        consumed.status
        is LegalNotificationContactVerificationStatus.CONSUMED
    )
    assert consumed.consumed_at == consumed_at

    with client.start_session() as session:
        with session.start_transaction():
            replay = registry.consume(
                source,
                consumed_at,
                session=session,
            )

    assert replay == consumed

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            LegalNotificationContactVerificationRegistryConflictError
        ) as captured:
            registry.consume(
                source,
                consumed_at + timedelta(microseconds=1),
                session=session,
            )

        assert captured.value.code == "L8_8H7C_STALE_SOURCE_CONFLICT"
        session.abort_transaction()

    raw = collection.find_one({"tenant_id": tenant})
    assert isinstance(raw, dict)
    assert raw["consumed_at"] == consumed.to_dict()["consumed_at"]


def test_real_revoke_and_expire_persist_exact_terminal_state(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalNotificationContactVerificationRegistry(collection)

    revoke_tenant = f"tenant-revoke-{uuid.uuid4().hex}"
    revoking = _verification(
        revoke_tenant,
        verification_id="verification-revoke",
        token_digest="f" * 128,
    )
    _commit_create(client, collection, revoking)

    revoked_at = NOW + timedelta(minutes=2)

    with client.start_session() as session:
        with session.start_transaction():
            revoked = registry.revoke(
                revoking,
                revoked_at,
                session=session,
            )

    assert (
        revoked.status
        is LegalNotificationContactVerificationStatus.REVOKED
    )
    assert revoked.revoked_at == revoked_at

    expire_tenant = f"tenant-expire-{uuid.uuid4().hex}"
    expiring = _verification(
        expire_tenant,
        verification_id="verification-expire",
        token_digest="1" * 128,
    )
    _commit_create(client, collection, expiring)

    with client.start_session() as session:
        with session.start_transaction():
            expired = registry.expire(
                expiring,
                EXPIRES,
                session=session,
            )

    assert (
        expired.status
        is LegalNotificationContactVerificationStatus.EXPIRED
    )
    assert expired.expired_at == EXPIRES


def test_real_persisted_corruption_is_rejected_before_projection(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalNotificationContactVerificationRegistry(collection)

    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    value = _verification(tenant)
    _commit_create(client, collection, value)

    original = deepcopy(
        collection.find_one({"tenant_id": tenant})
    )
    assert isinstance(original, dict)

    collection.update_one(
        {"tenant_id": tenant},
        {"$set": {"principal_id": "corrupt-principal"}},
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalNotificationContactVerificationRegistryPersistedRecordInvalidError
            ) as captured:
                registry.get_by_id(
                    tenant,
                    value.verification_id,
                    session=session,
                )

            assert (
                captured.value.code
                == "L8_8H7C_PERSISTED_RECORD_INVALID"
            )

    collection.replace_one(
        {"_id": original["_id"]},
        original,
    )

    collection.update_one(
        {"tenant_id": tenant},
        {"$set": {"unexpected_field": True}},
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalNotificationContactVerificationRegistryPersistedRecordInvalidError
            ):
                registry.get_by_id(
                    tenant,
                    value.verification_id,
                    session=session,
                )


def test_real_divergent_same_identity_replay_does_not_mutate_row(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalNotificationContactVerificationRegistry(collection)

    tenant = f"tenant-divergent-{uuid.uuid4().hex}"
    first = _verification(tenant)
    _commit_create(client, collection, first)

    before = deepcopy(
        collection.find_one({"tenant_id": tenant})
    )

    divergent = _verification(
        tenant,
        token_digest="2" * 128,
    )

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            LegalNotificationContactVerificationRegistryConflictError
        ) as captured:
            registry.create(
                divergent,
                session=session,
            )

        assert captured.value.code == "L8_8H7C_DIVERGENT_REPLAY"
        session.abort_transaction()

    assert collection.count_documents({"tenant_id": tenant}) == 1
    assert collection.find_one({"tenant_id": tenant}) == before


def test_real_competing_create_consumers_produce_one_durable_row(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    tenant = f"tenant-race-{uuid.uuid4().hex}"
    value = _verification(tenant)
    barrier = Barrier(2)

    def contender(_: int) -> str:
        registry = LegalNotificationContactVerificationRegistry(
            collection
        )

        with client.start_session() as session:
            session.start_transaction()
            barrier.wait()

            try:
                registry.create(
                    value,
                    session=session,
                )
                session.commit_transaction()
                return "COMMITTED"

            except (
                LegalNotificationContactVerificationRegistryRetryTransactionError,
                LegalNotificationContactVerificationRegistryPersistenceError,
            ):
                if session.in_transaction:
                    session.abort_transaction()
                return "RETRY_OR_TRANSIENT_FAILURE"

            except LegalNotificationContactVerificationRegistryConflictError:
                if session.in_transaction:
                    session.abort_transaction()
                return "CONFLICT"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(
            pool.map(
                contender,
                (1, 2),
            )
        )

    assert "COMMITTED" in outcomes
    assert all(
        outcome in {
            "COMMITTED",
            "RETRY_OR_TRANSIENT_FAILURE",
            "CONFLICT",
        }
        for outcome in outcomes
    )
    assert collection.count_documents({"tenant_id": tenant}) == 1


def test_real_database_contains_only_h7c_collection_and_no_other_authority(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, database, collection = mongo_context

    tenant = f"tenant-shape-{uuid.uuid4().hex}"
    value = _verification(tenant)
    _commit_create(client, collection, value)

    raw = collection.find_one({"tenant_id": tenant})
    assert isinstance(raw, dict)

    assert set(raw) == set(value.to_dict()) | {"_id"}

    assert not {
        "contact_id",
        "verified_at",
        "delivery_id",
        "dispatch_id",
        "message_id",
        "iam_permission",
        "court_authority",
        "financial_authority",
        "payment_id",
        "settlement_id",
    } & set(raw)

    assert set(database.list_collection_names()) == {COLLECTION}


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_notification_contact_verification_registry_real_mongo.py
# VERSION: v1.0.0-L8-8H7C-LEGAL-NOTIFICATION-CONTACT-VERIFICATION-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical H7C verification-persistence evidence only
# TENANT POSTURE: UUID-isolated database and exact tenant-scoped operations
# TRANSACTION POSTURE: caller owns every active transaction and commit/abort
# FAIL-CLOSED POSTURE: topology/index/corruption/replay/race failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
