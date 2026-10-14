"""
Real-Mongo certificate for privileged-eligibility evidence registry.

VERSION:
v1.0.0-P2-R2-A3-PRIVILEGED-ELIGIBILITY-EVIDENCE-REGISTRY-REAL-MONGO

Requires the sanctioned local writable replica set used by WILSY IAM
certification:
    127.0.0.1:27027
    replica set: wilsyVendorCertRS

The certificate uses a UUID-isolated disposable database and drops only that
database.

AUTHORITY BOUNDARY:
Eligibility evidence is historic audit material. It creates no role,
activation, current authority, security assurance, session, break glass,
or financial execution authority.
"""

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timezone
from threading import Barrier
from typing import Any, Iterator
import os
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.auth.privileged_eligibility import (
    ENTERPRISE_ADMIN,
    SOVEREIGN_ARCHITECT,
    evaluate_privileged_eligibility,
)
from tools.eos.auth.privileged_eligibility_evidence import (
    PrivilegedEligibilityEvidence,
)
from tools.eos.auth.privileged_eligibility_evidence_registry import (
    COLLECTION,
    ELIGIBILITY_ID_INDEX,
    PRINCIPAL_TIMELINE_INDEX,
    ROLE_TIMELINE_INDEX,
    SCOPE_IDEMPOTENCY_INDEX,
    PrivilegedEligibilityEvidenceConflictError,
    PrivilegedEligibilityEvidencePersistedInvalidError,
    PrivilegedEligibilityEvidenceRegistry,
    PrivilegedEligibilityEvidenceRegistryError,
    PrivilegedEligibilityEvidenceTransactionRequiredError,
)


MONGO_URI = os.environ.get(
    "WILSY_VENDOR_CERT_MONGO_URI",
    (
        "mongodb://127.0.0.1:27027/"
        "?replicaSet=wilsyVendorCertRS"
    ),
)

EXPECTED_REPLICA_SET = (
    "wilsyVendorCertRS"
)

DATABASE_PREFIX = (
    "wilsy_p2_r2_a3_"
)

NOW = datetime(
    2026,
    10,
    14,
    1,
    30,
    tzinfo=timezone.utc,
)

UNRELATED_COLLECTIONS = (
    "role_assignments",
    "tenant_memberships",
    "tenant_business_roles",
    "auth_sessions",
    "session_registry",
    "refresh_tokens",
    "privileged_activations",
    "break_glass_activations",
    "financial_executions",
)


def _client() -> MongoClient[Any]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5_000,
        retryWrites=True,
        tz_aware=True,
    )

    hello = client.admin.command(
        "hello"
    )

    assert (
        hello.get("setName")
        == EXPECTED_REPLICA_SET
    )

    assert bool(
        hello.get(
            "isWritablePrimary",
            hello.get(
                "ismaster",
                False,
            ),
        )
    )

    assert (
        hello.get(
            "logicalSessionTimeoutMinutes"
        )
        is not None
    )

    return client


def _tenant_evidence(
    *,
    evidence_id: str = "eligibility-a3-001",
    idempotency_key: str = "idem-a3-001",
    principal_id: str = "principal-a3",
    tenant_id: str = "tenant-a3",
    eligible: bool = True,
) -> PrivilegedEligibilityEvidence:
    decision = (
        evaluate_privileged_eligibility(
            principal_id=principal_id,
            privileged_role_id=
                ENTERPRISE_ADMIN,
            principal_current=True,
            tenant_id=tenant_id,
            tenant_membership_current=True,
            workforce_required=True,
            tenant_workforce_current=True,
        )
        if eligible
        else evaluate_privileged_eligibility(
            principal_id=principal_id,
            privileged_role_id=
                ENTERPRISE_ADMIN,
            principal_current=False,
            tenant_id=tenant_id,
            tenant_membership_current=True,
            workforce_required=True,
            tenant_workforce_current=True,
        )
    )

    return (
        PrivilegedEligibilityEvidence
        .from_decision(
            eligibility_evidence_id=
                evidence_id,
            decision=decision,
            evaluated_at=NOW,
            idempotency_key=
                idempotency_key,
        )
    )


def _platform_evidence(
    *,
    evidence_id: str = "eligibility-a3-root",
    idempotency_key: str = "idem-a3-root",
    principal_id: str = "principal-a3-root",
) -> PrivilegedEligibilityEvidence:
    decision = (
        evaluate_privileged_eligibility(
            principal_id=principal_id,
            privileged_role_id=
                SOVEREIGN_ARCHITECT,
            principal_current=True,
            platform_prerequisite_proven=True,
        )
    )

    return (
        PrivilegedEligibilityEvidence
        .from_decision(
            eligibility_evidence_id=
                evidence_id,
            decision=decision,
            evaluated_at=NOW,
            idempotency_key=
                idempotency_key,
            platform_prerequisite_id=
                "platform-prerequisite-root",
            platform_prerequisite_revision=
                1,
            platform_prerequisite_fingerprint=
                "a" * 128,
            platform_prerequisite_source_evidence_reference=
                "core-governance-root",
        )
    )


def _commit(
    client: MongoClient[Any],
    registry: PrivilegedEligibilityEvidenceRegistry,
    value: PrivilegedEligibilityEvidence,
) -> PrivilegedEligibilityEvidence:
    with client.start_session() as session:
        session.start_transaction()

        try:
            result = (
                registry.create_or_replay(
                    value,
                    session=session,
                )
            )

            session.commit_transaction()

            return result

        except BaseException:
            if session.in_transaction:
                session.abort_transaction()

            raise


def _retryable(
    error: BaseException,
) -> bool:
    current: BaseException | None = error

    while current is not None:
        if (
            isinstance(
                current,
                PyMongoError,
            )
            and current.has_error_label(
                "TransientTransactionError"
            )
        ):
            return True

        current = current.__cause__

    return False


def _compete(
    database_name: str,
    value: PrivilegedEligibilityEvidence,
    barrier: Barrier,
) -> str:
    client = _client()

    registry = (
        PrivilegedEligibilityEvidenceRegistry(
            client[
                database_name
            ][COLLECTION]
        )
    )

    first = True

    try:
        for _attempt in range(5):
            with client.start_session() as session:
                session.start_transaction()

                try:
                    if first:
                        first = False
                        barrier.wait(
                            timeout=15
                        )

                    result = (
                        registry.create_or_replay(
                            value,
                            session=session,
                        )
                    )

                    session.commit_transaction()

                    return (
                        "SUCCESS:"
                        + result
                        .eligibility_evidence_fingerprint
                    )

                except (
                    PrivilegedEligibilityEvidenceConflictError
                ) as error:
                    if session.in_transaction:
                        session.abort_transaction()

                    if (
                        error.code
                        == "WHOLE_TRANSACTION_RETRY_REQUIRED"
                        or _retryable(
                            error
                        )
                    ):
                        continue

                    return (
                        "CONFLICT:"
                        + error.code
                    )

                except (
                    PrivilegedEligibilityEvidenceRegistryError
                ) as error:
                    if session.in_transaction:
                        session.abort_transaction()

                    if _retryable(
                        error
                    ):
                        continue

                    return (
                        "FAIL_CLOSED:"
                        + error.code
                    )

                except PyMongoError as error:
                    if session.in_transaction:
                        session.abort_transaction()

                    if _retryable(
                        error
                    ):
                        continue

                    return (
                        "DRIVER_FAIL_CLOSED:"
                        + type(error).__name__
                    )

        return (
            "WHOLE_TRANSACTION_RETRY_EXHAUSTED"
        )

    finally:
        client.close()


@pytest.fixture()
def mongo_context() -> Iterator[
    tuple[
        MongoClient[Any],
        Any,
        Any,
        PrivilegedEligibilityEvidenceRegistry,
    ]
]:
    client = _client()

    database_name = (
        DATABASE_PREFIX
        + uuid.uuid4().hex
    )

    assert database_name.startswith(
        DATABASE_PREFIX
    )

    database = client[
        database_name
    ]

    collection = database[
        COLLECTION
    ]

    registry = (
        PrivilegedEligibilityEvidenceRegistry(
            collection
        )
    )

    registry.ensure_indexes()

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


def test_real_collection_and_physical_indexes(
    mongo_context: tuple[Any, ...],
) -> None:
    (
        client,
        database,
        collection,
        registry,
    ) = mongo_context

    hello = client.admin.command(
        "hello"
    )

    assert (
        hello["setName"]
        == EXPECTED_REPLICA_SET
    )

    assert collection.name == COLLECTION

    assert database.name.startswith(
        DATABASE_PREFIX
    )

    registry.ensure_indexes()
    registry.ensure_indexes()

    indexes = {
        str(item["name"]):
            dict(item)
        for item
        in collection.list_indexes()
    }

    assert set(indexes) == {
        "_id_",
        ELIGIBILITY_ID_INDEX,
        SCOPE_IDEMPOTENCY_INDEX,
        ROLE_TIMELINE_INDEX,
        PRINCIPAL_TIMELINE_INDEX,
    }

    assert dict(
        indexes[
            ELIGIBILITY_ID_INDEX
        ]["key"]
    ) == {
        "eligibility_evidence_id": 1
    }

    assert (
        indexes[
            ELIGIBILITY_ID_INDEX
        ].get(
            "unique"
        )
        is True
    )

    assert dict(
        indexes[
            SCOPE_IDEMPOTENCY_INDEX
        ]["key"]
    ) == {
        "target_class": 1,
        "_scope_tenant_key": 1,
        "principal_id": 1,
        "privileged_role_id": 1,
        "idempotency_key": 1,
    }

    assert (
        indexes[
            SCOPE_IDEMPOTENCY_INDEX
        ].get(
            "unique"
        )
        is True
    )

    assert dict(
        indexes[
            ROLE_TIMELINE_INDEX
        ]["key"]
    ) == {
        "target_class": 1,
        "_scope_tenant_key": 1,
        "principal_id": 1,
        "privileged_role_id": 1,
        "evaluated_at": 1,
    }

    assert (
        indexes[
            ROLE_TIMELINE_INDEX
        ].get(
            "unique",
            False,
        )
        is False
    )

    assert dict(
        indexes[
            PRINCIPAL_TIMELINE_INDEX
        ]["key"]
    ) == {
        "target_class": 1,
        "_scope_tenant_key": 1,
        "principal_id": 1,
        "evaluated_at": 1,
    }

    assert (
        indexes[
            PRINCIPAL_TIMELINE_INDEX
        ].get(
            "unique",
            False,
        )
        is False
    )

    assert all(
        "expireAfterSeconds"
        not in item
        for item
        in indexes.values()
    )


def test_missing_and_inactive_transaction_reject_before_persistence(
    mongo_context: tuple[Any, ...],
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    value = _tenant_evidence()

    before = collection.count_documents(
        {}
    )

    with pytest.raises(
        PrivilegedEligibilityEvidenceTransactionRequiredError
    ):
        registry.create_or_replay(
            value,
            session=None,
        )

    assert (
        collection.count_documents(
            {}
        )
        == before
    )

    with client.start_session() as session:
        assert (
            session.in_transaction
            is False
        )

        with pytest.raises(
            PrivilegedEligibilityEvidenceTransactionRequiredError
        ):
            registry.create_or_replay(
                value,
                session=session,
            )

    assert (
        collection.count_documents(
            {}
        )
        == before
    )


def test_caller_abort_and_commit(
    mongo_context: tuple[Any, ...],
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    value = _tenant_evidence()

    with client.start_session() as session:
        session.start_transaction()

        assert (
            registry.create_or_replay(
                value,
                session=session,
            )
            == value
        )

        assert (
            collection.count_documents(
                {
                    "eligibility_evidence_id":
                        value
                        .eligibility_evidence_id
                },
                session=session,
            )
            == 1
        )

        assert (
            collection.count_documents(
                {
                    "eligibility_evidence_id":
                        value
                        .eligibility_evidence_id
                }
            )
            == 0
        )

        session.abort_transaction()

    assert (
        collection.count_documents(
            {
                "eligibility_evidence_id":
                    value
                    .eligibility_evidence_id
            }
        )
        == 0
    )

    assert (
        _commit(
            client,
            registry,
            value,
        )
        == value
    )

    assert (
        collection.count_documents(
            {
                "eligibility_evidence_id":
                    value
                    .eligibility_evidence_id
            }
        )
        == 1
    )


def test_exact_replay_returns_historic_unchanged(
    mongo_context: tuple[Any, ...],
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    value = _tenant_evidence()

    assert (
        _commit(
            client,
            registry,
            value,
        )
        == value
    )

    before = collection.find_one(
        {
            "eligibility_evidence_id":
                value
                .eligibility_evidence_id
        }
    )

    assert (
        _commit(
            client,
            registry,
            value,
        )
        == value
    )

    assert (
        collection.count_documents(
            {
                "target_class":
                    value.target_class.value,
                "_scope_tenant_key":
                    value.tenant_id,
                "principal_id":
                    value.principal_id,
                "privileged_role_id":
                    value.privileged_role_id,
                "idempotency_key":
                    value.idempotency_key,
            }
        )
        == 1
    )

    assert (
        collection.find_one(
            {
                "eligibility_evidence_id":
                    value
                    .eligibility_evidence_id
            }
        )
        == before
    )


def test_divergent_replay_and_identity_collision_preserve_original(
    mongo_context: tuple[Any, ...],
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    original = _tenant_evidence()

    _commit(
        client,
        registry,
        original,
    )

    before = collection.find_one(
        {
            "eligibility_evidence_id":
                original
                .eligibility_evidence_id
        }
    )

    divergent = _tenant_evidence(
        evidence_id=
            "eligibility-a3-divergent",
    )

    with pytest.raises(
        PrivilegedEligibilityEvidenceConflictError
    ) as replay:
        _commit(
            client,
            registry,
            divergent,
        )

    assert (
        replay.value.code
        == "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"
    )

    collision = _tenant_evidence(
        evidence_id=
            original
            .eligibility_evidence_id,
        idempotency_key=
            "idem-a3-other",
        principal_id=
            "principal-a3-other",
    )

    with pytest.raises(
        PrivilegedEligibilityEvidenceConflictError
    ) as identity:
        _commit(
            client,
            registry,
            collision,
        )

    assert (
        identity.value.code
        == "ELIGIBILITY_EVIDENCE_ID_COLLISION"
    )

    assert (
        collection.find_one(
            {
                "eligibility_evidence_id":
                    original
                    .eligibility_evidence_id
            }
        )
        == before
    )

    assert (
        collection.count_documents(
            {}
        )
        == 1
    )


def test_tenant_and_platform_scope_are_distinct(
    mongo_context: tuple[Any, ...],
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    tenant = _tenant_evidence(
        idempotency_key="same-key",
    )

    platform = _platform_evidence(
        idempotency_key="same-key",
    )

    _commit(
        client,
        registry,
        tenant,
    )

    _commit(
        client,
        registry,
        platform,
    )

    assert (
        collection.count_documents(
            {}
        )
        == 2
    )

    assert (
        registry.get_by_scope_idempotency(
            target_class=
                tenant.target_class.value,
            tenant_id=
                tenant.tenant_id,
            principal_id=
                tenant.principal_id,
            privileged_role_id=
                tenant.privileged_role_id,
            idempotency_key=
                tenant.idempotency_key,
        )
        == tenant
    )

    assert (
        registry.get_by_scope_idempotency(
            target_class=
                platform.target_class.value,
            tenant_id=None,
            principal_id=
                platform.principal_id,
            privileged_role_id=
                platform.privileged_role_id,
            idempotency_key=
                platform.idempotency_key,
        )
        == platform
    )


def test_eligible_and_ineligible_evidence_both_persist(
    mongo_context: tuple[Any, ...],
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    eligible = _tenant_evidence(
        evidence_id=
            "eligibility-a3-eligible",
        idempotency_key=
            "idem-a3-eligible",
        eligible=True,
    )

    ineligible = _tenant_evidence(
        evidence_id=
            "eligibility-a3-ineligible",
        idempotency_key=
            "idem-a3-ineligible",
        eligible=False,
    )

    _commit(
        client,
        registry,
        eligible,
    )

    _commit(
        client,
        registry,
        ineligible,
    )

    assert (
        registry.get(
            eligibility_evidence_id=
                eligible
                .eligibility_evidence_id
        )
        == eligible
    )

    assert (
        registry.get(
            eligibility_evidence_id=
                ineligible
                .eligibility_evidence_id
        )
        == ineligible
    )

    assert (
        collection.count_documents(
            {}
        )
        == 2
    )


def test_corrupt_historic_rows_fail_closed(
    mongo_context: tuple[Any, ...],
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    value = _tenant_evidence()

    _commit(
        client,
        registry,
        value,
    )

    assert (
        collection.update_one(
            {
                "eligibility_evidence_id":
                    value
                    .eligibility_evidence_id
            },
            {
                "$set": {
                    "eligibility_evidence_fingerprint":
                        "f" * 128
                }
            },
        ).modified_count
        == 1
    )

    with pytest.raises(
        PrivilegedEligibilityEvidencePersistedInvalidError
    ):
        registry.get(
            eligibility_evidence_id=
                value
                .eligibility_evidence_id
        )

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            PrivilegedEligibilityEvidencePersistedInvalidError
        ):
            registry.create_or_replay(
                value,
                session=session,
            )

        session.abort_transaction()

    assert (
        collection.count_documents(
            {}
        )
        == 1
    )


def test_fresh_client_and_registry_preserve_replay(
    mongo_context: tuple[Any, ...],
) -> None:
    (
        client,
        database,
        collection,
        registry,
    ) = mongo_context

    value = _tenant_evidence()

    _commit(
        client,
        registry,
        value,
    )

    fresh_registry = (
        PrivilegedEligibilityEvidenceRegistry(
            collection
        )
    )

    assert (
        fresh_registry.get(
            eligibility_evidence_id=
                value
                .eligibility_evidence_id
        )
        == value
    )

    fresh_client = _client()

    try:
        restarted = (
            PrivilegedEligibilityEvidenceRegistry(
                fresh_client[
                    database.name
                ][COLLECTION]
            )
        )

        assert (
            restarted.get(
                eligibility_evidence_id=
                    value
                    .eligibility_evidence_id
            )
            == value
        )

        assert (
            _commit(
                fresh_client,
                restarted,
                value,
            )
            == value
        )

        assert (
            fresh_client[
                database.name
            ][COLLECTION]
            .count_documents(
                {}
            )
            == 1
        )

    finally:
        fresh_client.close()


def test_competing_identical_requests_converge_to_one_row(
    mongo_context: tuple[Any, ...],
) -> None:
    (
        _client_owner,
        database,
        collection,
        _registry,
    ) = mongo_context

    value = _tenant_evidence()

    barrier = Barrier(2)

    with ThreadPoolExecutor(
        max_workers=2
    ) as pool:
        futures = (
            pool.submit(
                _compete,
                database.name,
                value,
                barrier,
            ),
            pool.submit(
                _compete,
                database.name,
                value,
                barrier,
            ),
        )

        outcomes = tuple(
            future.result(
                timeout=45
            )
            for future
            in futures
        )

    assert any(
        outcome.startswith(
            "SUCCESS:"
        )
        for outcome in outcomes
    )

    assert all(
        (
            outcome.startswith(
                "SUCCESS:"
            )
            or outcome
            == "WHOLE_TRANSACTION_RETRY_EXHAUSTED"
        )
        for outcome
        in outcomes
    )

    assert (
        collection.count_documents(
            {
                "target_class":
                    value
                    .target_class.value,
                "_scope_tenant_key":
                    value.tenant_id,
                "principal_id":
                    value.principal_id,
                "privileged_role_id":
                    value.privileged_role_id,
                "idempotency_key":
                    value.idempotency_key,
            }
        )
        == 1
    )


def test_competing_divergent_requests_cannot_both_succeed(
    mongo_context: tuple[Any, ...],
) -> None:
    (
        _client_owner,
        database,
        collection,
        _registry,
    ) = mongo_context

    left = _tenant_evidence(
        evidence_id=
            "eligibility-a3-left",
    )

    right = _tenant_evidence(
        evidence_id=
            "eligibility-a3-right",
    )

    barrier = Barrier(2)

    with ThreadPoolExecutor(
        max_workers=2
    ) as pool:
        futures = (
            pool.submit(
                _compete,
                database.name,
                left,
                barrier,
            ),
            pool.submit(
                _compete,
                database.name,
                right,
                barrier,
            ),
        )

        outcomes = tuple(
            future.result(
                timeout=45
            )
            for future
            in futures
        )

    assert (
        sum(
            outcome.startswith(
                "SUCCESS:"
            )
            for outcome
            in outcomes
        )
        == 1
    )

    assert any(
        outcome.startswith(
            "CONFLICT:"
            "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"
        )
        for outcome in outcomes
    )

    assert (
        collection.count_documents(
            {
                "target_class":
                    left.target_class.value,
                "_scope_tenant_key":
                    left.tenant_id,
                "principal_id":
                    left.principal_id,
                "privileged_role_id":
                    left.privileged_role_id,
                "idempotency_key":
                    left.idempotency_key,
            }
        )
        == 1
    )


def test_unrelated_authority_collections_remain_absent_and_unmutated(
    mongo_context: tuple[Any, ...],
) -> None:
    (
        client,
        database,
        _collection,
        registry,
    ) = mongo_context

    before = {
        name:
            database[
                name
            ].count_documents(
                {}
            )
        for name
        in UNRELATED_COLLECTIONS
    }

    assert before == {
        name: 0
        for name
        in UNRELATED_COLLECTIONS
    }

    _commit(
        client,
        registry,
        _tenant_evidence(),
    )

    after = {
        name:
            database[
                name
            ].count_documents(
                {}
            )
        for name
        in UNRELATED_COLLECTIONS
    }

    assert after == before

    assert set(
        database.list_collection_names()
    ) == {
        COLLECTION
    }


def test_registry_source_owns_no_forbidden_lifecycle_or_authority() -> None:
    from pathlib import Path

    source = Path(
        "tools/eos/auth/"
        "privileged_eligibility_evidence_registry.py"
    ).read_text(
        encoding="utf-8"
    ).casefold()

    for forbidden in (
        ".start_session(",
        ".start_transaction(",
        ".commit_transaction(",
        ".abort_transaction(",
        ".update_one(",
        ".replace_one(",
        ".delete_one(",
        ".delete_many(",
        ".compare_and_swap(",
        "role_assignment_repository",
        "tenant_membership_repository",
        "refresh_token",
        "privileged_activation",
        "break_glass",
        "financial_execution_repository",
        "fastapi",
    ):
        assert forbidden not in source


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT:
# test_privileged_eligibility_evidence_registry_real_mongo.py
# VERSION:
# v1.0.0-P2-R2-A3-PRIVILEGED-ELIGIBILITY-EVIDENCE-REGISTRY-REAL-MONGO
# MONGO: genuine writable local replica set
# DATABASE: UUID-isolated disposable namespace
# TRANSACTION: caller-owned
# INDEXES: exact unique/replay/timeline set, no TTL
# REPLAY: exact, divergent, collision, restart durability
# CONCURRENCY: identical convergence + divergent fencing
# AUTHORITY: no assignment/activation/session/break-glass/finance
# END OF WILSY OS SOVEREIGN ARTIFACT
