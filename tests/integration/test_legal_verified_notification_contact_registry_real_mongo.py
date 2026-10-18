"""Real-Mongo certificate for the durable H7D verified Legal contact registry.

TITLE: WILSY OS Verified Legal Notification Contact Registry Real-Mongo Certificate
VERSION: v1.0.0-L8-8H7D-VERIFIED-LEGAL-NOTIFICATION-CONTACT-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Direct physical certification of H7D persistence/read/revocation.
EPITOME: Prove sanctioned replica-set topology, exact partial unique indexes,
         digest-only persistence, consumed-verification provenance uniqueness,
         tenant isolation, ACTIVE address scope, caller-owned transactions,
         atomic revocation, rollback, corruption rejection and race safety.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_verified_notification_contact_registry_real_mongo.py
COLLABORATION / OWNERSHIP: H7B owns verified-contact semantics; H7D owns only
                            durable persistence/read/revocation. H7E is not
                            invoked and no contact elevation occurs here.
CERTIFICATION / UPDATE DATE: 2026-10-12
SECURITY / PRIVACY POSTURE: UUID-isolated disposable database; synthetic
                             opaque identifiers and digests only; no raw
                             address, raw token, credential or message body.
TENANT BOUNDARY: Every operational assertion uses exact tenant predicates.
AUTHORITY BOUNDARY: H7D physical persistence evidence only. No H7A issuance,
                    IAM, HTTP, dispatch, delivery, Court or AI authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Callers own every session and transaction.
FAIL-CLOSED DECLARATION: Topology, indexes, duplicate authority, corruption,
                         rollback, stale CAS or race failure rejects.
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
)
from tools.eos.legal_operations.domain.legal_verified_notification_contact import (
    VerifiedLegalNotificationContact,
    VerifiedLegalNotificationContactStatus,
)
from tools.eos.legal_operations.registry.legal_verified_notification_contact_registry import (
    ACTIVE_SCOPE_INDEX,
    COLLECTION,
    CONTACT_ID_INDEX,
    PRINCIPAL_SCOPE_INDEX,
    VERIFICATION_INDEX,
    VerifiedLegalNotificationContactRegistry,
    VerifiedLegalNotificationContactRegistryConflictError,
    VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError,
    VerifiedLegalNotificationContactRegistryPersistenceError,
    VerifiedLegalNotificationContactRegistryRetryTransactionError,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

NOW = datetime(2026, 10, 12, 20, 30, 0, 654321, tzinfo=timezone.utc)
CONSUMED = NOW + timedelta(minutes=5)
VERIFIED = CONSUMED
EXPIRES = NOW + timedelta(minutes=30)

ADDRESS_DIGEST = "a" * 128
TOKEN_DIGEST = "b" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Provide sanctioned replica-set persistence in one disposable UUID DB."""

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
            pytest.fail(f"L8_8H7D_MONGO_UNAVAILABLE:{type(error).__name__}")

        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail("L8_8H7D_WRONG_REPLICA_SET")

        if hello.get(
            "isWritablePrimary",
            hello.get("ismaster"),
        ) is not True:
            pytest.fail("L8_8H7D_NO_WRITABLE_PRIMARY")

        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.fail("L8_8H7D_SESSIONS_UNAVAILABLE")

        database = client[
            f"wilsy_h7d_vc_{uuid.uuid4().hex}"
        ]

        collection = database.get_collection(
            COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )

        VerifiedLegalNotificationContactRegistry(
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
    address_digest: str = ADDRESS_DIGEST,
    token_digest: str = TOKEN_DIGEST,
    consumed_at: datetime = CONSUMED,
) -> LegalNotificationContactVerification:
    value = LegalNotificationContactVerification.issue(
        tenant_id=tenant_id,
        verification_id=verification_id,
        principal_id=principal_id,
        channel=LegalNotificationContactChannel.EMAIL,
        address_digest=address_digest,
        token_digest=token_digest,
        issued_at=NOW,
        expires_at=EXPIRES,
    )
    return value.consume(consumed_at)


def _contact(
    tenant_id: str,
    *,
    contact_id: str = "legal-contact-1",
    verification_id: str = "legal-verification-1",
    principal_id: str = "principal-1",
    address_digest: str = ADDRESS_DIGEST,
    token_digest: str = TOKEN_DIGEST,
    consumed_at: datetime = CONSUMED,
    verified_at: datetime = VERIFIED,
) -> VerifiedLegalNotificationContact:
    verification = _verification(
        tenant_id,
        verification_id=verification_id,
        principal_id=principal_id,
        address_digest=address_digest,
        token_digest=token_digest,
        consumed_at=consumed_at,
    )
    return VerifiedLegalNotificationContact.from_consumed_verification(
        contact_id=contact_id,
        verification=verification,
        verified_at=verified_at,
    )


def _commit_create(
    client: MongoClient[Any],
    collection: Any,
    value: VerifiedLegalNotificationContact,
) -> VerifiedLegalNotificationContact:
    registry = VerifiedLegalNotificationContactRegistry(collection)

    with client.start_session() as session:
        with session.start_transaction():
            return registry.create(
                value,
                session=session,
            )


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


def test_real_index_metadata_is_exact_partial_unique_and_has_no_ttl(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context

    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
        if item["name"] != "_id_"
    }

    assert set(indexes) == {
        CONTACT_ID_INDEX,
        VERIFICATION_INDEX,
        ACTIVE_SCOPE_INDEX,
        PRINCIPAL_SCOPE_INDEX,
    }

    assert dict(indexes[CONTACT_ID_INDEX]["key"]) == {
        "tenant_id": 1,
        "contact_id": 1,
    }
    assert indexes[CONTACT_ID_INDEX].get("unique") is True

    assert dict(indexes[VERIFICATION_INDEX]["key"]) == {
        "tenant_id": 1,
        "verification_fingerprint": 1,
    }
    assert indexes[VERIFICATION_INDEX].get("unique") is True

    assert dict(indexes[ACTIVE_SCOPE_INDEX]["key"]) == {
        "tenant_id": 1,
        "principal_id": 1,
        "channel": 1,
        "address_digest": 1,
    }
    assert indexes[ACTIVE_SCOPE_INDEX].get("unique") is True
    assert indexes[ACTIVE_SCOPE_INDEX].get(
        "partialFilterExpression"
    ) == {"revoked_at": None}

    assert dict(indexes[PRINCIPAL_SCOPE_INDEX]["key"]) == {
        "tenant_id": 1,
        "principal_id": 1,
        "channel": 1,
        "verified_at": 1,
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
    value = _contact(tenant)

    assert _commit_create(client, collection, value) == value
    assert _commit_create(client, collection, value) == value
    assert collection.count_documents({"tenant_id": tenant}) == 1

    raw = collection.find_one({"tenant_id": tenant})
    assert isinstance(raw, dict)

    expected = value.to_dict()
    assert set(raw) == set(expected) | {"_id"}

    assert {
        key: item
        for key, item in raw.items()
        if key != "_id"
    } == expected

    assert "email" not in raw
    assert "address" not in raw
    assert "raw_email" not in raw
    assert "raw_token" not in raw
    assert "token_digest" not in raw

    registry = VerifiedLegalNotificationContactRegistry(collection)

    with client.start_session() as session:
        with session.start_transaction():
            readback = registry.get_by_id(
                tenant,
                value.contact_id,
                session=session,
            )

    assert readback == value
    assert readback is not None
    assert readback.verification_consumed_at.microsecond == 654321
    assert readback.verification_expires_at.microsecond == 654321
    assert readback.verified_at.microsecond == 654321


def test_real_tenant_provenance_active_and_history_reads_are_exact(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = VerifiedLegalNotificationContactRegistry(collection)

    tenant_a = f"tenant-a-{uuid.uuid4().hex}"
    tenant_b = f"tenant-b-{uuid.uuid4().hex}"

    first = _contact(
        tenant_a,
        contact_id="contact-a1",
        verification_id="verification-a1",
        token_digest="c" * 128,
    )
    second = _contact(
        tenant_a,
        contact_id="contact-a2",
        verification_id="verification-a2",
        token_digest="d" * 128,
        consumed_at=CONSUMED + timedelta(seconds=1),
        verified_at=VERIFIED + timedelta(seconds=1),
    )
    foreign = _contact(
        tenant_b,
        contact_id="contact-b1",
        verification_id="verification-b1",
        token_digest="e" * 128,
    )

    for value in (first, foreign):
        assert _commit_create(client, collection, value) == value

    with client.start_session() as session:
        with session.start_transaction():
            revoked = registry.revoke(
                first,
                VERIFIED + timedelta(minutes=1),
                session=session,
            )

    assert revoked.status is VerifiedLegalNotificationContactStatus.REVOKED
    assert _commit_create(client, collection, second) == second

    with client.start_session() as session:
        with session.start_transaction():
            assert registry.get_by_id(
                tenant_a,
                second.contact_id,
                session=session,
            ) == second

            assert registry.get_by_id(
                tenant_a,
                foreign.contact_id,
                session=session,
            ) is None

            assert registry.get_by_verification_fingerprint(
                tenant_a,
                second.verification_fingerprint,
                session=session,
            ) == second

            assert registry.get_active(
                tenant_a,
                second.principal_id,
                second.channel,
                second.address_digest,
                session=session,
            ) == second

            history = registry.list_principal_scope(
                tenant_a,
                second.principal_id,
                second.channel,
                session=session,
            )

    assert history == (revoked, second)
    assert collection.count_documents({"tenant_id": tenant_a}) == 2
    assert collection.count_documents({"tenant_id": tenant_b}) == 1


def test_real_active_partial_unique_scope_blocks_two_active_contacts(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context

    tenant = f"tenant-active-{uuid.uuid4().hex}"

    first = _contact(
        tenant,
        contact_id="contact-1",
        verification_id="verification-1",
        token_digest="1" * 128,
    )
    second = _contact(
        tenant,
        contact_id="contact-2",
        verification_id="verification-2",
        token_digest="2" * 128,
        consumed_at=CONSUMED + timedelta(seconds=1),
        verified_at=VERIFIED + timedelta(seconds=1),
    )

    _commit_create(client, collection, first)

    registry = VerifiedLegalNotificationContactRegistry(collection)

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            VerifiedLegalNotificationContactRegistryRetryTransactionError
        ):
            registry.create(
                second,
                session=session,
            )

        if session.in_transaction:
            session.abort_transaction()

    assert collection.count_documents({"tenant_id": tenant}) == 1


def test_real_consumed_verification_provenance_cannot_elevate_twice(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = VerifiedLegalNotificationContactRegistry(collection)

    tenant = f"tenant-provenance-{uuid.uuid4().hex}"
    verification = _verification(tenant)

    first = VerifiedLegalNotificationContact.from_consumed_verification(
        contact_id="contact-1",
        verification=verification,
        verified_at=VERIFIED,
    )
    second = VerifiedLegalNotificationContact.from_consumed_verification(
        contact_id="contact-2",
        verification=verification,
        verified_at=VERIFIED,
    )

    _commit_create(client, collection, first)

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            VerifiedLegalNotificationContactRegistryConflictError
        ) as captured:
            registry.create(
                second,
                session=session,
            )

        assert (
            captured.value.code
            == "L8_8H7D_VERIFICATION_ALREADY_ELEVATED"
        )
        session.abort_transaction()

    assert collection.count_documents({"tenant_id": tenant}) == 1


def test_real_caller_abort_leaves_zero_rows(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = VerifiedLegalNotificationContactRegistry(collection)

    tenant = f"tenant-abort-{uuid.uuid4().hex}"
    value = _contact(tenant)

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


def test_real_revoke_cas_exact_replay_and_stale_divergence(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = VerifiedLegalNotificationContactRegistry(collection)

    tenant = f"tenant-revoke-{uuid.uuid4().hex}"
    source = _contact(tenant)
    _commit_create(client, collection, source)

    revoked_at = VERIFIED + timedelta(minutes=1)

    with client.start_session() as session:
        with session.start_transaction():
            revoked = registry.revoke(
                source,
                revoked_at,
                session=session,
            )

    assert revoked.status is VerifiedLegalNotificationContactStatus.REVOKED
    assert revoked.revoked_at == revoked_at

    with client.start_session() as session:
        with session.start_transaction():
            replay = registry.revoke(
                source,
                revoked_at,
                session=session,
            )

    assert replay == revoked

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            VerifiedLegalNotificationContactRegistryConflictError
        ) as captured:
            registry.revoke(
                source,
                revoked_at + timedelta(microseconds=1),
                session=session,
            )

        assert captured.value.code == "L8_8H7D_STALE_SOURCE_CONFLICT"
        session.abort_transaction()


def test_real_persisted_corruption_is_rejected_before_projection(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = VerifiedLegalNotificationContactRegistry(collection)

    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    value = _contact(tenant)
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
                VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError
            ):
                registry.get_by_id(
                    tenant,
                    value.contact_id,
                    session=session,
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
                VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError
            ):
                registry.get_by_id(
                    tenant,
                    value.contact_id,
                    session=session,
                )


def test_real_divergent_same_identity_replay_does_not_mutate_row(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = VerifiedLegalNotificationContactRegistry(collection)

    tenant = f"tenant-divergent-{uuid.uuid4().hex}"
    first = _contact(tenant)
    _commit_create(client, collection, first)

    before = deepcopy(
        collection.find_one({"tenant_id": tenant})
    )

    divergent = _contact(
        tenant,
        verification_id="verification-other",
        token_digest="3" * 128,
    )

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            VerifiedLegalNotificationContactRegistryConflictError
        ) as captured:
            registry.create(
                divergent,
                session=session,
            )

        assert captured.value.code == "L8_8H7D_DIVERGENT_REPLAY"
        session.abort_transaction()

    assert collection.count_documents({"tenant_id": tenant}) == 1
    assert collection.find_one({"tenant_id": tenant}) == before


def test_real_competing_create_consumers_produce_one_durable_row(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context

    tenant = f"tenant-race-{uuid.uuid4().hex}"
    value = _contact(tenant)
    barrier = Barrier(2)

    def contender(_: int) -> str:
        registry = VerifiedLegalNotificationContactRegistry(collection)

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
                VerifiedLegalNotificationContactRegistryRetryTransactionError,
                VerifiedLegalNotificationContactRegistryPersistenceError,
            ):
                if session.in_transaction:
                    session.abort_transaction()
                return "RETRY_OR_TRANSIENT_FAILURE"

            except VerifiedLegalNotificationContactRegistryConflictError:
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


def test_real_database_contains_only_h7d_collection_and_no_other_authority(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, database, collection = mongo_context

    tenant = f"tenant-shape-{uuid.uuid4().hex}"
    value = _contact(tenant)
    _commit_create(client, collection, value)

    raw = collection.find_one({"tenant_id": tenant})
    assert isinstance(raw, dict)

    assert set(raw) == set(value.to_dict()) | {"_id"}

    assert not {
        "token_digest",
        "raw_token",
        "email",
        "address",
        "dispatch_id",
        "delivery_id",
        "message_id",
        "iam_permission",
        "court_authority",
        "financial_authority",
        "payment_id",
        "settlement_id",
    } & set(raw)

    assert set(database.list_collection_names()) == {COLLECTION}


# ARTIFACT: test_legal_verified_notification_contact_registry_real_mongo.py
# VERSION: v1.0.0-L8-8H7D-VERIFIED-LEGAL-NOTIFICATION-CONTACT-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical H7D verified-contact persistence/read/revocation evidence only
# TENANT POSTURE: UUID-isolated database and exact tenant-scoped operations
# TRANSACTION POSTURE: callers own every active transaction and commit/abort
# FAIL-CLOSED POSTURE: topology/index/corruption/replay/CAS/race failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
