"""
Real-Mongo durability certificate for P3 security-assurance evidence registry.

The certificate uses only a UUID-isolated disposable database on the sanctioned
local replica set. It proves durability, index metadata, transaction semantics,
exact replay, corruption rejection, restart readback, and concurrent insertion.

Historic sufficient evidence is audit only and never current assurance.

No proof-source implementation, MFA verification, session creation, token
issuance, role assignment, privileged activation, break glass, or financial
authority is exercised.
"""

from __future__ import annotations

from concurrent.futures import (
    ThreadPoolExecutor,
)
from datetime import (
    datetime,
    timezone,
)
import os
import uuid

import pytest
from pymongo import (
    MongoClient,
)

from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssuranceChannel,
    PrivilegedAssurancePurpose,
    PrivilegedAssuranceReason,
)
from tools.eos.auth.privileged_security_assurance_evidence import (
    PrivilegedSecurityAssuranceEvidence,
)
from tools.eos.auth.privileged_security_assurance_evidence_registry import (
    ASSURANCE_EVIDENCE_ID_INDEX,
    COLLECTION,
    PRINCIPAL_CHANNEL_TIMELINE_INDEX,
    PRINCIPAL_PURPOSE_TIMELINE_INDEX,
    SCOPE_IDEMPOTENCY_INDEX,
    PrivilegedSecurityAssuranceEvidenceConflictError,
    PrivilegedSecurityAssuranceEvidencePersistedInvalidError,
    PrivilegedSecurityAssuranceEvidenceRegistry,
    PrivilegedSecurityAssuranceEvidenceTransactionRequiredError,
)


MONGO_URI = os.environ.get(
    "WILSY_P3_A3_MONGO_URI",
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
    "&directConnection=true",
)


@pytest.fixture()
def mongo_context():
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
    )

    client.admin.command(
        "ping"
    )

    db_name = (
        "wilsy_p3_r2_a3_"
        + uuid.uuid4().hex
    )

    database = client[
        db_name
    ]

    collection = database[
        COLLECTION
    ]

    registry = (
        PrivilegedSecurityAssuranceEvidenceRegistry(
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


AT = datetime(
    2026,
    10,
    14,
    2,
    15,
    0,
    654321,
    tzinfo=timezone.utc,
)


def evidence(
    *,
    evidence_id: str = "assurance-evidence-1",
    principal_id: str = "principal-1",
    channel: PrivilegedAssuranceChannel = (
        PrivilegedAssuranceChannel
        .INTERACTIVE_STRONG_AUTH
    ),
    purpose: PrivilegedAssurancePurpose = (
        PrivilegedAssurancePurpose
        .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
    ),
    idempotency_key: str = "idem-1",
    sufficient: bool = True,
    reason: PrivilegedAssuranceReason = (
        PrivilegedAssuranceReason
        .SUFFICIENT
    ),
) -> PrivilegedSecurityAssuranceEvidence:
    interactive = (
        channel
        is PrivilegedAssuranceChannel
        .INTERACTIVE_STRONG_AUTH
    )

    return (
        PrivilegedSecurityAssuranceEvidence(
            assurance_evidence_id=
                evidence_id,
            principal_id=
                principal_id,
            assurance_channel=
                channel,
            assurance_purpose=
                purpose,
            principal_current=
                True,
            credential_current=
                True,
            assurance_proof_current=
                True,
            session_current=
                True
                if interactive
                else None,
            factor_verification_current=
                True
                if interactive
                else None,
            authentication_recency_current=
                True
                if interactive
                else None,
            workload_proof_current=
                None
                if interactive
                else True,
            workload_proof_reference=
                None
                if interactive
                else "workload-proof:001",
            sufficient=
                sufficient,
            reason=
                reason,
            evaluated_at=
                AT,
            idempotency_key=
                idempotency_key,
        )
    )


def persist(
    client: MongoClient,
    registry: PrivilegedSecurityAssuranceEvidenceRegistry,
    value: PrivilegedSecurityAssuranceEvidence,
):
    holder = {}

    def callback(
        session,
    ):
        holder["value"] = (
            registry.create_or_replay(
                value,
                session=session,
            )
        )

    with client.start_session() as session:
        session.with_transaction(
            callback
        )

    return holder["value"]


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

    assert (
        ASSURANCE_EVIDENCE_ID_INDEX
        in indexes
    )

    assert (
        SCOPE_IDEMPOTENCY_INDEX
        in indexes
    )

    assert (
        PRINCIPAL_PURPOSE_TIMELINE_INDEX
        in indexes
    )

    assert (
        PRINCIPAL_CHANNEL_TIMELINE_INDEX
        in indexes
    )

    assert (
        indexes[
            ASSURANCE_EVIDENCE_ID_INDEX
        ]["unique"]
        is True
    )

    assert (
        indexes[
            SCOPE_IDEMPOTENCY_INDEX
        ]["unique"]
        is True
    )

    assert "expireAfterSeconds" not in indexes[
        ASSURANCE_EVIDENCE_ID_INDEX
    ]

    assert "expireAfterSeconds" not in indexes[
        SCOPE_IDEMPOTENCY_INDEX
    ]

    assert "expireAfterSeconds" not in indexes[
        PRINCIPAL_PURPOSE_TIMELINE_INDEX
    ]

    assert "expireAfterSeconds" not in indexes[
        PRINCIPAL_CHANNEL_TIMELINE_INDEX
    ]


def test_missing_and_inactive_transaction_reject_before_write(
    mongo_context,
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    value = evidence()

    with pytest.raises(
        PrivilegedSecurityAssuranceEvidenceTransactionRequiredError
    ):
        registry.create_or_replay(
            value,
            session=None,
        )

    assert (
        collection.count_documents(
            {}
        )
        == 0
    )

    with client.start_session() as session:
        with pytest.raises(
            PrivilegedSecurityAssuranceEvidenceTransactionRequiredError
        ):
            registry.create_or_replay(
                value,
                session=session,
            )

    assert (
        collection.count_documents(
            {}
        )
        == 0
    )


def test_caller_abort_zero_durable_write_and_commit_durable(
    mongo_context,
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    value = evidence()

    with client.start_session() as session:
        session.start_transaction()

        registry.create_or_replay(
            value,
            session=session,
        )

        session.abort_transaction()

    assert (
        collection.count_documents(
            {}
        )
        == 0
    )

    persist(
        client,
        registry,
        value,
    )

    assert (
        collection.count_documents(
            {}
        )
        == 1
    )


def test_exact_replay_is_historic_and_unchanged(
    mongo_context,
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    value = evidence()

    first = persist(
        client,
        registry,
        value,
    )

    second = persist(
        client,
        registry,
        value,
    )

    assert first == value
    assert second == value

    assert (
        collection.count_documents(
            {}
        )
        == 1
    )


def test_divergent_replay_and_identity_collision_preserve_original(
    mongo_context,
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    original = evidence()

    persist(
        client,
        registry,
        original,
    )

    divergent = evidence(
        evidence_id=
            "assurance-evidence-2",
        sufficient=False,
        reason=(
            PrivilegedAssuranceReason
            .AUTHENTICATION_NOT_RECENT
        ),
    )

    with pytest.raises(
        PrivilegedSecurityAssuranceEvidenceConflictError
    ):
        persist(
            client,
            registry,
            divergent,
        )

    collision = evidence(
        principal_id=
            "principal-2",
        idempotency_key=
            "idem-2",
    )

    with pytest.raises(
        PrivilegedSecurityAssuranceEvidenceConflictError
    ):
        persist(
            client,
            registry,
            collision,
        )

    assert (
        collection.count_documents(
            {}
        )
        == 1
    )

    assert (
        registry.get(
            assurance_evidence_id=
                original.assurance_evidence_id
        )
        == original
    )


def test_channel_purpose_and_principal_scopes_are_distinct(
    mongo_context,
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    values = (
        evidence(),
        evidence(
            evidence_id=
                "assurance-evidence-2",
            channel=(
                PrivilegedAssuranceChannel
                .NONINTERACTIVE_WORKLOAD_PROOF
            ),
        ),
        evidence(
            evidence_id=
                "assurance-evidence-3",
            purpose=(
                PrivilegedAssurancePurpose
                .PRIVILEGED_ACTIVATION_USE
            ),
        ),
        evidence(
            evidence_id=
                "assurance-evidence-4",
            principal_id=
                "principal-2",
        ),
    )

    for value in values:
        persist(
            client,
            registry,
            value,
        )

    assert (
        collection.count_documents(
            {}
        )
        == 4
    )


def test_sufficient_and_insufficient_evidence_both_persist(
    mongo_context,
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    sufficient = evidence()

    insufficient = evidence(
        evidence_id=
            "assurance-evidence-2",
        idempotency_key=
            "idem-2",
        sufficient=False,
        reason=(
            PrivilegedAssuranceReason
            .AUTHENTICATION_NOT_RECENT
        ),
    )

    persist(
        client,
        registry,
        sufficient,
    )

    persist(
        client,
        registry,
        insufficient,
    )

    assert (
        collection.count_documents(
            {
                "sufficient": True,
            }
        )
        == 1
    )

    assert (
        collection.count_documents(
            {
                "sufficient": False,
            }
        )
        == 1
    )


def test_corrupt_historic_row_fails_closed(
    mongo_context,
) -> None:
    (
        client,
        _database,
        collection,
        registry,
    ) = mongo_context

    value = evidence()

    persist(
        client,
        registry,
        value,
    )

    collection.update_one(
        {
            "assurance_evidence_id":
                value.assurance_evidence_id,
        },
        {
            "$set": {
                "assurance_evidence_fingerprint":
                    "f" * 128,
            },
        },
    )

    with pytest.raises(
        PrivilegedSecurityAssuranceEvidencePersistedInvalidError
    ):
        registry.get(
            assurance_evidence_id=
                value.assurance_evidence_id
        )


def test_fresh_client_registry_restart_readback(
    mongo_context,
) -> None:
    (
        client,
        database,
        collection,
        registry,
    ) = mongo_context

    value = evidence()

    persist(
        client,
        registry,
        value,
    )

    db_name = database.name

    fresh_client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
    )

    try:
        fresh_registry = (
            PrivilegedSecurityAssuranceEvidenceRegistry(
                fresh_client[
                    db_name
                ][
                    COLLECTION
                ]
            )
        )

        assert (
            fresh_registry.get(
                assurance_evidence_id=
                    value.assurance_evidence_id
            )
            == value
        )
    finally:
        fresh_client.close()

    assert (
        collection.count_documents(
            {}
        )
        == 1
    )


def test_competing_identical_consumers_converge_to_one_row(
    mongo_context,
) -> None:
    (
        _client,
        database,
        collection,
        registry,
    ) = mongo_context

    registry.ensure_indexes()

    value = evidence()

    def worker():
        local_client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
        )

        local_registry = (
            PrivilegedSecurityAssuranceEvidenceRegistry(
                local_client[
                    database.name
                ][
                    COLLECTION
                ]
            )
        )

        try:
            return persist(
                local_client,
                local_registry,
                value,
            )
        except Exception:
            # A losing Mongo transaction may require host-level whole
            # transaction retry. Re-run one fresh transaction exactly.
            return persist(
                local_client,
                local_registry,
                value,
            )
        finally:
            local_client.close()

    with ThreadPoolExecutor(
        max_workers=2
    ) as pool:
        results = list(
            pool.map(
                lambda _:
                    worker(),
                range(2),
            )
        )

    assert results == [
        value,
        value,
    ]

    assert (
        collection.count_documents(
            {}
        )
        == 1
    )


def test_competing_divergent_consumers_cannot_both_succeed(
    mongo_context,
) -> None:
    (
        _client,
        database,
        collection,
        registry,
    ) = mongo_context

    registry.ensure_indexes()

    first = evidence()

    second = evidence(
        evidence_id=
            "assurance-evidence-2",
        sufficient=False,
        reason=(
            PrivilegedAssuranceReason
            .AUTHENTICATION_NOT_RECENT
        ),
    )

    def worker(
        value,
    ):
        local_client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
        )

        local_registry = (
            PrivilegedSecurityAssuranceEvidenceRegistry(
                local_client[
                    database.name
                ][
                    COLLECTION
                ]
            )
        )

        try:
            try:
                return (
                    "SUCCESS",
                    persist(
                        local_client,
                        local_registry,
                        value,
                    ),
                )
            except (
                PrivilegedSecurityAssuranceEvidenceConflictError,
            ):
                return (
                    "CONFLICT",
                    None,
                )
        finally:
            local_client.close()

    with ThreadPoolExecutor(
        max_workers=2
    ) as pool:
        results = list(
            pool.map(
                worker,
                (
                    first,
                    second,
                ),
            )
        )

    successes = [
        item
        for item in results
        if item[0]
        == "SUCCESS"
    ]

    conflicts = [
        item
        for item in results
        if item[0]
        == "CONFLICT"
    ]

    assert len(
        successes
    ) == 1

    assert len(
        conflicts
    ) == 1

    assert (
        collection.count_documents(
            {}
        )
        == 1
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
        "privileged_activation",
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


def test_registry_source_owns_no_forbidden_authority() -> None:
    import inspect
    import tools.eos.auth.privileged_security_assurance_evidence_registry as module

    source = inspect.getsource(
        module
    )

    forbidden = (
        "start_transaction(",
        "commit_transaction(",
        "abort_transaction(",
        "role_assignment",
        "privileged_activation",
        "break_glass",
        "financial_execution",
        "expireAfterSeconds",
        "sequence_number",
        "previous_fingerprint",
    )

    for token in forbidden:
        assert (
            token
            not in source
        )
