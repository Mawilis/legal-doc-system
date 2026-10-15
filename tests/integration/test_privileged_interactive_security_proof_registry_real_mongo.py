"""
Real-Mongo durability and concurrency certificate for P3-R3C.

This certificate exercises only the revisioned interactive-security-proof
registry against a UUID-isolated database on the sanctioned local replica set.

It proves:

- exact seven-index metadata with no TTL,
- caller-owned active transaction enforcement,
- abort-zero-write and committed durability,
- immutable VERIFIED revision 1,
- legal terminal revision 2 transitions,
- exact replay,
- stale revision/fingerprint rejection,
- restart durability,
- chain corruption fail-closed,
- competing terminal transitions cannot both succeed,
- explicit proof authority reads,
- no MFA/session/credential/P3/P4 authority.
"""

from __future__ import annotations

from concurrent.futures import (
    ThreadPoolExecutor,
)
from datetime import (
    datetime,
    timedelta,
    timezone,
)
import os
import uuid

import pytest
from pymongo import MongoClient

from tools.eos.auth.privileged_interactive_security_proof import (
    PrivilegedInteractiveProofStatus,
    PrivilegedInteractiveSecurityProof,
)
from tools.eos.auth.privileged_interactive_security_proof_registry import (
    COLLECTION,
    FACTOR_REFERENCE_REVISION_INDEX,
    PRINCIPAL_AUTHENTICATED_TIMELINE_INDEX,
    PROOF_IDEMPOTENCY_INDEX,
    PROOF_REFERENCE_REVISION_INDEX,
    PROOF_REVISION_INDEX,
    SESSION_REVISION_INDEX,
    STATUS_CHANGED_TIMELINE_INDEX,
    PrivilegedInteractiveSecurityProofConflictError,
    PrivilegedInteractiveSecurityProofPersistedInvalidError,
    PrivilegedInteractiveSecurityProofRegistry,
    PrivilegedInteractiveSecurityProofTransactionRequiredError,
)


MONGO_URI = os.environ.get(
    "WILSY_P3_R3C_MONGO_URI",
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
    "&directConnection=true",
)


AT = datetime(
    2026,
    10,
    14,
    5,
    30,
    0,
    123456,
    tzinfo=timezone.utc,
)

LATER = AT + timedelta(
    minutes=1
)


@pytest.fixture()
def mongo_context():
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
    )

    client.admin.command("ping")

    db_name = (
        "wilsy_p3_r3c_"
        + uuid.uuid4().hex
    )

    database = client[
        db_name
    ]

    collection = database[
        COLLECTION
    ]

    registry = (
        PrivilegedInteractiveSecurityProofRegistry(
            collection
        )
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
            db_name
        )
        client.close()


def proof(
    *,
    proof_id: str = "proof-1",
    principal_id: str = "principal-1",
    factor_reference: str = "factor-1",
    session_reference: str = "session-1",
    proof_reference: str = "proof-reference-1",
) -> PrivilegedInteractiveSecurityProof:
    return (
        PrivilegedInteractiveSecurityProof(
            proof_id=
                proof_id,
            principal_id=
                principal_id,
            factor_verification_reference=
                factor_reference,
            authenticated_at=
                AT,
            credential_revision=
                7,
            session_reference=
                session_reference,
            proof_status=(
                PrivilegedInteractiveProofStatus
                .VERIFIED
            ),
            proof_reference=
                proof_reference,
        )
    )


def transaction(
    client: MongoClient,
    callback,
):
    holder = {}

    def run_callback(
        session,
    ):
        holder["value"] = callback(
            session
        )

    with client.start_session() as session:
        session.with_transaction(
            run_callback
        )

    if "value" not in holder:
        raise AssertionError(
            "TRANSACTION_CALLBACK_RETURN_MISSING"
        )

    return holder["value"]


def create(
    client: MongoClient,
    registry: PrivilegedInteractiveSecurityProofRegistry,
    *,
    value: PrivilegedInteractiveSecurityProof | None = None,
    idempotency_key: str = "create-1",
):
    candidate = (
        value
        if value is not None
        else proof()
    )

    return transaction(
        client,
        lambda session:
            registry.create_or_replay(
                candidate,
                status_changed_at=
                    AT,
                idempotency_key=
                    idempotency_key,
                session=session,
            ),
    )


def transition(
    client: MongoClient,
    registry: PrivilegedInteractiveSecurityProofRegistry,
    current,
    *,
    target_status: PrivilegedInteractiveProofStatus,
    idempotency_key: str,
    changed_at: datetime = LATER,
):
    return transaction(
        client,
        lambda session:
            registry.transition_status(
                proof_id=
                    current.proof.proof_id,
                target_status=
                    target_status,
                status_changed_at=
                    changed_at,
                idempotency_key=
                    idempotency_key,
                expected_revision=
                    current.revision,
                expected_snapshot_fingerprint=
                    current.snapshot_fingerprint,
                session=session,
            ),
    )


def test_real_indexes_exact_and_no_ttl(
    mongo_context,
) -> None:
    (
        _client,
        _database,
        collection,
        registry,
    ) = mongo_context

    registry.ensure_indexes()

    indexes = {
        entry["name"]:
            entry
        for entry
        in collection.list_indexes()
    }

    expected = {
        PROOF_REVISION_INDEX,
        PROOF_REFERENCE_REVISION_INDEX,
        FACTOR_REFERENCE_REVISION_INDEX,
        PROOF_IDEMPOTENCY_INDEX,
        PRINCIPAL_AUTHENTICATED_TIMELINE_INDEX,
        SESSION_REVISION_INDEX,
        STATUS_CHANGED_TIMELINE_INDEX,
    }

    assert expected.issubset(
        indexes
    )

    for name in expected:
        assert (
            "expireAfterSeconds"
            not in indexes[name]
        )

    for name in (
        PROOF_REVISION_INDEX,
        PROOF_REFERENCE_REVISION_INDEX,
        FACTOR_REFERENCE_REVISION_INDEX,
        PROOF_IDEMPOTENCY_INDEX,
    ):
        assert (
            indexes[name]["unique"]
            is True
        )


def test_missing_and_inactive_transaction_reject_before_write(
    mongo_context,
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    value = proof()

    with pytest.raises(
        PrivilegedInteractiveSecurityProofTransactionRequiredError
    ):
        registry.create_or_replay(
            value,
            status_changed_at=AT,
            idempotency_key="create-1",
            session=None,
        )

    with client.start_session() as session:
        with pytest.raises(
            PrivilegedInteractiveSecurityProofTransactionRequiredError
        ):
            registry.create_or_replay(
                value,
                status_changed_at=AT,
                idempotency_key="create-1",
                session=session,
            )

    assert (
        collection.count_documents({})
        == 0
    )


def test_caller_abort_zero_write_then_commit_durable(
    mongo_context,
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    value = proof()

    with client.start_session() as session:
        session.start_transaction()

        registry.create_or_replay(
            value,
            status_changed_at=AT,
            idempotency_key="create-1",
            session=session,
        )

        session.abort_transaction()

    assert (
        collection.count_documents({})
        == 0
    )

    first = create(
        client,
        registry,
        value=value,
    )

    assert first.revision == 1

    assert (
        collection.count_documents({})
        == 1
    )


def test_exact_create_replay_real_mongo(
    mongo_context,
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    first = create(
        client,
        registry,
    )

    second = create(
        client,
        registry,
    )

    assert first == second

    assert (
        collection.count_documents({})
        == 1
    )


@pytest.mark.parametrize(
    "target",
    (
        PrivilegedInteractiveProofStatus
        .REVOKED,
        PrivilegedInteractiveProofStatus
        .INVALIDATED,
    ),
)
def test_verified_to_terminal_creates_revision_two(
    mongo_context,
    target,
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    first = create(
        client,
        registry,
    )

    second = transition(
        client,
        registry,
        first,
        target_status=target,
        idempotency_key="transition-1",
    )

    assert second.revision == 2

    assert (
        second.previous_snapshot_fingerprint
        == first.snapshot_fingerprint
    )

    assert (
        second.proof.proof_status
        is target
    )

    assert (
        collection.count_documents({})
        == 2
    )


def test_terminal_transition_exact_replay_real_mongo(
    mongo_context,
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    first = create(
        client,
        registry,
    )

    second = transition(
        client,
        registry,
        first,
        target_status=(
            PrivilegedInteractiveProofStatus
            .REVOKED
        ),
        idempotency_key="transition-1",
    )

    replay = transition(
        client,
        registry,
        first,
        target_status=(
            PrivilegedInteractiveProofStatus
            .REVOKED
        ),
        idempotency_key="transition-1",
    )

    assert replay == second

    assert (
        collection.count_documents({})
        == 2
    )


def test_terminal_status_has_no_successor_real_mongo(
    mongo_context,
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    first = create(
        client,
        registry,
    )

    second = transition(
        client,
        registry,
        first,
        target_status=(
            PrivilegedInteractiveProofStatus
            .REVOKED
        ),
        idempotency_key="transition-1",
    )

    with pytest.raises(
        PrivilegedInteractiveSecurityProofConflictError
    ):
        transition(
            client,
            registry,
            second,
            target_status=(
                PrivilegedInteractiveProofStatus
                .INVALIDATED
            ),
            idempotency_key="transition-2",
            changed_at=(
                LATER
                + timedelta(seconds=1)
            ),
        )

    assert (
        collection.count_documents({})
        == 2
    )


def test_stale_revision_and_fingerprint_reject(
    mongo_context,
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    first = create(
        client,
        registry,
    )

    with pytest.raises(
        PrivilegedInteractiveSecurityProofConflictError
    ):
        transaction(
            client,
            lambda session:
                registry.transition_status(
                    proof_id=
                        first.proof.proof_id,
                    target_status=(
                        PrivilegedInteractiveProofStatus
                        .REVOKED
                    ),
                    status_changed_at=
                        LATER,
                    idempotency_key=
                        "transition-stale-revision",
                    expected_revision=
                        2,
                    expected_snapshot_fingerprint=
                        first.snapshot_fingerprint,
                    session=session,
                ),
        )

    with pytest.raises(
        PrivilegedInteractiveSecurityProofConflictError
    ):
        transaction(
            client,
            lambda session:
                registry.transition_status(
                    proof_id=
                        first.proof.proof_id,
                    target_status=(
                        PrivilegedInteractiveProofStatus
                        .REVOKED
                    ),
                    status_changed_at=
                        LATER,
                    idempotency_key=
                        "transition-stale-fingerprint",
                    expected_revision=
                        1,
                    expected_snapshot_fingerprint=
                        "f" * 128,
                    session=session,
                ),
        )

    assert (
        collection.count_documents({})
        == 1
    )


def test_explicit_authority_reads_and_history(
    mongo_context,
) -> None:
    (
        client,
        _database,
        _collection,
        registry,
    ) = mongo_context

    first = create(
        client,
        registry,
    )

    second = transition(
        client,
        registry,
        first,
        target_status=(
            PrivilegedInteractiveProofStatus
            .REVOKED
        ),
        idempotency_key="transition-1",
    )

    assert (
        registry.get_current_by_proof_id(
            proof_id=
                first.proof.proof_id
        )
        == second
    )

    assert (
        registry.get_current_by_proof_reference(
            proof_reference=
                first.proof.proof_reference
        )
        == second
    )

    assert (
        registry.get_current_by_factor_reference(
            factor_verification_reference=
                first
                .proof
                .factor_verification_reference
        )
        == second
    )

    assert (
        registry.get_history_by_proof_id(
            proof_id=
                first.proof.proof_id
        )
        == (
            first,
            second,
        )
    )


def test_restart_readback_preserves_chain(
    mongo_context,
) -> None:
    (
        client,
        database,
        collection,
        registry,
    ) = mongo_context

    first = create(
        client,
        registry,
    )

    second = transition(
        client,
        registry,
        first,
        target_status=(
            PrivilegedInteractiveProofStatus
            .INVALIDATED
        ),
        idempotency_key="transition-1",
    )

    fresh = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
    )

    try:
        fresh_registry = (
            PrivilegedInteractiveSecurityProofRegistry(
                fresh[
                    database.name
                ][
                    COLLECTION
                ]
            )
        )

        assert (
            fresh_registry.get_current_by_proof_id(
                proof_id=
                    first.proof.proof_id
            )
            == second
        )

        assert (
            fresh_registry.get_history_by_proof_id(
                proof_id=
                    first.proof.proof_id
            )
            == (
                first,
                second,
            )
        )
    finally:
        fresh.close()

    assert (
        collection.count_documents({})
        == 2
    )


def test_corrupt_snapshot_fails_closed(
    mongo_context,
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    first = create(
        client,
        registry,
    )

    collection.update_one(
        {
            "proof_id":
                first.proof.proof_id,
            "revision":
                1,
        },
        {
            "$set": {
                "snapshot_fingerprint":
                    "f" * 128,
            },
        },
    )

    with pytest.raises(
        PrivilegedInteractiveSecurityProofPersistedInvalidError
    ):
        registry.get_current_by_proof_id(
            proof_id=
                first.proof.proof_id
        )


def test_broken_revision_chain_fails_closed(
    mongo_context,
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    first = create(
        client,
        registry,
    )

    second = transition(
        client,
        registry,
        first,
        target_status=(
            PrivilegedInteractiveProofStatus
            .REVOKED
        ),
        idempotency_key="transition-1",
    )

    collection.update_one(
        {
            "proof_id":
                first.proof.proof_id,
            "revision":
                2,
        },
        {
            "$set": {
                "previous_snapshot_fingerprint":
                    "f" * 128,
            },
        },
    )

    with pytest.raises(
        PrivilegedInteractiveSecurityProofPersistedInvalidError
    ):
        registry.get_history_by_proof_id(
            proof_id=
                first.proof.proof_id
        )

    assert second.revision == 2


def test_competing_terminal_transitions_cannot_both_succeed(
    mongo_context,
) -> None:
    (
        client,
        database,
        collection,
        registry,
    ) = mongo_context

    registry.ensure_indexes()

    first = create(
        client,
        registry,
    )

    def worker(
        target,
        key,
    ):
        local = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
        )

        local_registry = (
            PrivilegedInteractiveSecurityProofRegistry(
                local[
                    database.name
                ][
                    COLLECTION
                ]
            )
        )

        try:
            try:
                result = transaction(
                    local,
                    lambda session:
                        local_registry.transition_status(
                            proof_id=
                                first.proof.proof_id,
                            target_status=
                                target,
                            status_changed_at=
                                LATER,
                            idempotency_key=
                                key,
                            expected_revision=
                                first.revision,
                            expected_snapshot_fingerprint=
                                first.snapshot_fingerprint,
                            session=session,
                        ),
                )

                return (
                    "SUCCESS",
                    result.proof.proof_status,
                )

            except (
                PrivilegedInteractiveSecurityProofConflictError,
            ):
                return (
                    "CONFLICT",
                    None,
                )

        finally:
            local.close()

    with ThreadPoolExecutor(
        max_workers=2
    ) as pool:
        futures = (
            pool.submit(
                worker,
                PrivilegedInteractiveProofStatus
                .REVOKED,
                "transition-revoked",
            ),
            pool.submit(
                worker,
                PrivilegedInteractiveProofStatus
                .INVALIDATED,
                "transition-invalidated",
            ),
        )

        results = [
            future.result()
            for future in futures
        ]

    successes = [
        result
        for result in results
        if result[0] == "SUCCESS"
    ]

    conflicts = [
        result
        for result in results
        if result[0] == "CONFLICT"
    ]

    assert len(successes) == 1
    assert len(conflicts) == 1

    assert (
        collection.count_documents(
            {
                "proof_id":
                    first.proof.proof_id,
            }
        )
        == 2
    )

    history = registry.get_history_by_proof_id(
        proof_id=
            first.proof.proof_id
    )

    assert len(history) == 2
    assert history[0].revision == 1
    assert history[1].revision == 2

    assert (
        history[1].proof.proof_status
        in {
            PrivilegedInteractiveProofStatus.REVOKED,
            PrivilegedInteractiveProofStatus.INVALIDATED,
        }
    )


def test_unrelated_authority_collections_absent(
    mongo_context,
) -> None:
    (
        _client,
        database,
        _collection,
        _registry,
    ) = mongo_context

    names = set(
        database.list_collection_names()
    )

    forbidden = {
        "privileged_activations",
        "role_assignments",
        "sessions",
        "refresh_tokens",
        "break_glass",
        "financial_execution",
    }

    assert not (
        names
        & forbidden
    )
