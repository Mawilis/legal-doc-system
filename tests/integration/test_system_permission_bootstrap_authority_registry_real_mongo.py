"""
TITLE:
    WILSY OS System Permission Bootstrap Authority Registry Real-Mongo Certificate

VERSION:
    v1.0.0-P4-R4-D11-R3-BOOTSTRAP-AUTHORITY-REGISTRY-REAL-MONGO

AUTHORITY:
    Wilsy OS Sovereign IAM certification only.

PURPOSE:
    Certify the bootstrap authority durable registry against a real writable
    MongoDB replica set with caller-owned transactions, immutable history,
    exact replay, scope isolation, transaction abort semantics, corruption
    rejection, BSON datetime hydration, and absence of TTL/delete authority.

AUTHORITY BOUNDARY:
    Persistence certification only. This file creates no offline installation
    trust authority, SYSTEM permission grant/revocation authority, assignment
    command authority, privileged activation authority, break-glass authority,
    or financial authority.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.auth.system_permission_bootstrap_authority import (
    SystemPermissionBootstrapAuthority,
)

from tools.eos.auth.system_permission_bootstrap_authority_registry import (
    SystemPermissionBootstrapAuthorityConflictError,
    SystemPermissionBootstrapAuthorityPersistedInvalidError,
    SystemPermissionBootstrapAuthorityRegistry,
)


URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

COLLECTION = "system_permission_bootstrap_authorities"

NOW = datetime(
    2026,
    10,
    14,
    21,
    0,
    tzinfo=timezone.utc,
)

ASSIGN_PURPOSE = (
    "SEED_SYSTEM_PERMISSION_ASSIGNMENT_COMMAND_AUTHORITY"
)

REVOKE_PURPOSE = (
    "SEED_SYSTEM_PERMISSION_REVOCATION_COMMAND_AUTHORITY"
)


def authority(
    *,
    bootstrap_id: str = "bootstrap-a",
    actor: str = "principal-a",
    purpose: str = ASSIGN_PURPOSE,
    evidence: str = "installation-evidence-a",
) -> SystemPermissionBootstrapAuthority:
    return SystemPermissionBootstrapAuthority.issue(
        bootstrap_id=bootstrap_id,
        actor_principal_id=actor,
        purpose=purpose,
        evidence_reference=evidence,
        issued_at=NOW,
    )


@pytest.fixture()
def mongo_context() -> Any:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        retryWrites=True,
    )

    hello = client.admin.command(
        "hello"
    )

    assert (
        hello.get("setName")
        == EXPECTED_REPLICA_SET
    )
    assert hello.get(
        "isWritablePrimary"
    ) is True
    assert (
        hello.get(
            "logicalSessionTimeoutMinutes"
        )
        is not None
    )

    db_name = (
        "wilsy_p4_r4_d11_r3_"
        + uuid4().hex[:20]
    )

    assert db_name != "wilsy"

    database = client[
        db_name
    ]

    collection = database[
        COLLECTION
    ]

    registry = (
        SystemPermissionBootstrapAuthorityRegistry(
            collection
        )
    )

    registry.ensure_indexes()

    try:
        yield {
            "client": client,
            "database": database,
            "db_name": db_name,
            "collection": collection,
            "registry": registry,
        }

    finally:
        client.drop_database(
            db_name
        )

        assert (
            db_name
            not in client.list_database_names()
        )

        client.close()


def commit_create(
    context: Any,
    value: SystemPermissionBootstrapAuthority,
    *,
    key: str,
) -> SystemPermissionBootstrapAuthority:
    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        result = context[
            "registry"
        ].create_or_replay(
            value,
            idempotency_key=key,
            session=session,
        )

        session.commit_transaction()

    return result


def commit_retire(
    context: Any,
    value: SystemPermissionBootstrapAuthority,
    *,
    key: str,
) -> SystemPermissionBootstrapAuthority:
    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        result = context[
            "registry"
        ].retire_or_replay(
            value,
            retirement_idempotency_key=key,
            session=session,
        )

        session.commit_transaction()

    return result


def test_real_replica_set_sessions_and_isolated_database(
    mongo_context: Any,
) -> None:
    hello = mongo_context[
        "client"
    ].admin.command(
        "hello"
    )

    assert (
        hello["setName"]
        == EXPECTED_REPLICA_SET
    )

    assert (
        hello.get(
            "logicalSessionTimeoutMinutes"
        )
        is not None
    )

    assert mongo_context[
        "db_name"
    ].startswith(
        "wilsy_p4_r4_d11_r3_"
    )

    assert (
        mongo_context[
            "db_name"
        ]
        != "wilsy"
    )


def test_real_index_metadata_exact_and_no_ttl(
    mongo_context: Any,
) -> None:
    indexes = {
        entry["name"]: entry
        for entry
        in mongo_context[
            "collection"
        ].list_indexes()
    }

    assert len(indexes) == 5

    revision = indexes[
        "system_permission_bootstrap_revision_unique"
    ]

    replay = indexes[
        "system_permission_bootstrap_scope_operation_idempotency_unique"
    ]

    history = indexes[
        "system_permission_bootstrap_principal_purpose_history"
    ]

    status = indexes[
        "system_permission_bootstrap_status_issued_timeline"
    ]

    assert revision["key"] == {
        "bootstrap_id": 1,
        "revision": 1,
    }

    assert revision.get(
        "unique"
    ) is True

    assert replay["key"] == {
        "actor_principal_id": 1,
        "purpose": 1,
        "_operation_idempotency_key": 1,
    }

    assert replay.get(
        "unique"
    ) is True

    assert history["key"] == {
        "actor_principal_id": 1,
        "purpose": 1,
        "revision": 1,
    }

    assert history.get(
        "unique"
    ) is not True

    assert status["key"] == {
        "status": 1,
        "issued_at": 1,
    }

    assert status.get(
        "unique"
    ) is not True

    assert all(
        "expireAfterSeconds"
        not in entry
        for entry in indexes.values()
    )


def test_real_active_create_hydrate_exact_replay_and_utc(
    mongo_context: Any,
) -> None:
    value = authority()

    first = commit_create(
        mongo_context,
        value,
        key="create-a",
    )

    replay = commit_create(
        mongo_context,
        value,
        key="create-a",
    )

    assert first == replay == value

    rows = list(
        mongo_context[
            "collection"
        ].find(
            {
                "bootstrap_id":
                    value.bootstrap_id,
            }
        )
    )

    assert len(rows) == 1

    assert isinstance(
        rows[0]["issued_at"],
        datetime,
    )

    assert (
        rows[0]["issued_at"].tzinfo
        is None
    )

    history = mongo_context[
        "registry"
    ].get_history(
        value.bootstrap_id
    )

    assert history == (
        value,
    )

    assert (
        history[0].issued_at.tzinfo
        is timezone.utc
    )


def test_real_divergent_create_replay_denied(
    mongo_context: Any,
) -> None:
    commit_create(
        mongo_context,
        authority(
            bootstrap_id="bootstrap-a",
        ),
        key="same-key",
    )

    divergent = authority(
        bootstrap_id="bootstrap-b",
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            SystemPermissionBootstrapAuthorityConflictError,
            match="IDEMPOTENCY_KEY_DIVERGENT_REPLAY",
        ):
            mongo_context[
                "registry"
            ].create_or_replay(
                divergent,
                idempotency_key="same-key",
                session=session,
            )

        session.abort_transaction()

    assert (
        mongo_context[
            "collection"
        ].count_documents({})
        == 1
    )


def test_real_bootstrap_id_collision_denied(
    mongo_context: Any,
) -> None:
    commit_create(
        mongo_context,
        authority(),
        key="create-a",
    )

    collision = authority(
        actor="principal-b",
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            SystemPermissionBootstrapAuthorityConflictError,
            match="BOOTSTRAP_ID_COLLISION",
        ):
            mongo_context[
                "registry"
            ].create_or_replay(
                collision,
                idempotency_key="create-b",
                session=session,
            )

        session.abort_transaction()


def test_real_actor_and_purpose_scope_isolation(
    mongo_context: Any,
) -> None:
    value = authority()

    commit_create(
        mongo_context,
        value,
        key="create-a",
    )

    registry = mongo_context[
        "registry"
    ]

    assert registry.resolve_current(
        actor_principal_id="principal-a",
        purpose=ASSIGN_PURPOSE,
    ) == value

    assert registry.resolve_current(
        actor_principal_id="principal-b",
        purpose=ASSIGN_PURPOSE,
    ) is None

    assert registry.resolve_current(
        actor_principal_id="principal-a",
        purpose=REVOKE_PURPOSE,
    ) is None


def test_real_active_to_retired_history_exact_replay(
    mongo_context: Any,
) -> None:
    active = authority()

    commit_create(
        mongo_context,
        active,
        key="create-a",
    )

    retired = active.retire(
        retired_at=(
            NOW
            + timedelta(minutes=1)
        ),
        retirement_evidence_reference=(
            "retirement-evidence-a"
        ),
    )

    first = commit_retire(
        mongo_context,
        retired,
        key="retire-a",
    )

    replay = commit_retire(
        mongo_context,
        retired,
        key="retire-a",
    )

    assert first == replay == retired

    history = mongo_context[
        "registry"
    ].get_history(
        active.bootstrap_id
    )

    assert history == (
        active,
        retired,
    )

    assert mongo_context[
        "registry"
    ].resolve_current(
        actor_principal_id=(
            active.actor_principal_id
        ),
        purpose=active.purpose,
    ) is None

    assert (
        mongo_context[
            "collection"
        ].count_documents(
            {
                "bootstrap_id":
                    active.bootstrap_id,
            }
        )
        == 2
    )


def test_real_divergent_retire_replay_denied(
    mongo_context: Any,
) -> None:
    active = authority()

    commit_create(
        mongo_context,
        active,
        key="create-a",
    )

    retired = active.retire(
        retired_at=(
            NOW
            + timedelta(minutes=1)
        ),
        retirement_evidence_reference="retire-a",
    )

    commit_retire(
        mongo_context,
        retired,
        key="same-retire-key",
    )

    divergent = active.retire(
        retired_at=(
            NOW
            + timedelta(minutes=2)
        ),
        retirement_evidence_reference="retire-b",
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            SystemPermissionBootstrapAuthorityConflictError,
            match="IDEMPOTENCY_KEY_DIVERGENT_REPLAY",
        ):
            mongo_context[
                "registry"
            ].retire_or_replay(
                divergent,
                retirement_idempotency_key=(
                    "same-retire-key"
                ),
                session=session,
            )

        session.abort_transaction()


def test_real_abort_create_leaves_zero_rows(
    mongo_context: Any,
) -> None:
    value = authority(
        bootstrap_id="abort-create",
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        result = mongo_context[
            "registry"
        ].create_or_replay(
            value,
            idempotency_key="abort-create",
            session=session,
        )

        assert result == value

        assert (
            mongo_context[
                "collection"
            ].count_documents(
                {
                    "bootstrap_id":
                        value.bootstrap_id,
                },
                session=session,
            )
            == 1
        )

        session.abort_transaction()

    assert (
        mongo_context[
            "collection"
        ].count_documents(
            {
                "bootstrap_id":
                    value.bootstrap_id,
            }
        )
        == 0
    )


def test_real_abort_retire_preserves_active(
    mongo_context: Any,
) -> None:
    active = authority()

    commit_create(
        mongo_context,
        active,
        key="create-a",
    )

    retired = active.retire(
        retired_at=(
            NOW
            + timedelta(minutes=1)
        ),
        retirement_evidence_reference="retire-a",
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        result = mongo_context[
            "registry"
        ].retire_or_replay(
            retired,
            retirement_idempotency_key=(
                "abort-retire"
            ),
            session=session,
        )

        assert result == retired

        session.abort_transaction()

    assert mongo_context[
        "registry"
    ].get_history(
        active.bootstrap_id
    ) == (
        active,
    )

    assert mongo_context[
        "registry"
    ].resolve_current(
        actor_principal_id=(
            active.actor_principal_id
        ),
        purpose=active.purpose,
    ) == active


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("status", "BROKEN"),
        ("issued_at", "not-time"),
        ("revision", 7),
        (
            "authority_fingerprint",
            "0" * 128,
        ),
    ),
)
def test_real_corrupt_persisted_material_fails_closed(
    mongo_context: Any,
    field: str,
    value: object,
) -> None:
    active = authority()

    commit_create(
        mongo_context,
        active,
        key="create-a",
    )

    mongo_context[
        "collection"
    ].update_one(
        {
            "bootstrap_id":
                active.bootstrap_id,
        },
        {
            "$set": {
                field: value,
            }
        },
    )

    with pytest.raises(
        SystemPermissionBootstrapAuthorityPersistedInvalidError
    ):
        mongo_context[
            "registry"
        ].get_history(
            active.bootstrap_id
        )


def test_real_corrupt_chain_fails_closed(
    mongo_context: Any,
) -> None:
    active = authority()

    commit_create(
        mongo_context,
        active,
        key="create-a",
    )

    retired = active.retire(
        retired_at=(
            NOW
            + timedelta(minutes=1)
        ),
        retirement_evidence_reference="retire-a",
    )

    commit_retire(
        mongo_context,
        retired,
        key="retire-a",
    )

    mongo_context[
        "collection"
    ].update_one(
        {
            "bootstrap_id":
                active.bootstrap_id,
            "revision": 2,
        },
        {
            "$set": {
                "previous_fingerprint":
                    "c" * 128,
            }
        },
    )

    with pytest.raises(
        SystemPermissionBootstrapAuthorityPersistedInvalidError
    ):
        mongo_context[
            "registry"
        ].get_history(
            active.bootstrap_id
        )


def test_real_no_ttl_delete_or_forbidden_authority_surface(
    mongo_context: Any,
) -> None:
    indexes = list(
        mongo_context[
            "collection"
        ].list_indexes()
    )

    assert all(
        "expireAfterSeconds"
        not in entry
        for entry in indexes
    )

    registry = mongo_context[
        "registry"
    ]

    for forbidden in (
        "delete",
        "purge",
        "authorize",
        "is_authorized",
        "grant_permission",
        "revoke_permission",
        "assign_permission",
        "issue_activation",
        "break_glass",
        "execute_financial",
        "resolve_principal",
    ):
        assert not hasattr(
            registry,
            forbidden,
        )


# =============================================================================
# WILSY OS TEST ARTIFACT SEAL
# ARTIFACT:
# tests/integration/test_system_permission_bootstrap_authority_registry_real_mongo.py
# VERSION: v1.0.0-P4-R4-D11-R3-BOOTSTRAP-AUTHORITY-REGISTRY-REAL-MONGO
# REAL MONGO: YES
# REPLICA SET REQUIRED: YES
# UUID ISOLATED DATABASE: YES
# CANONICAL WILSY DATABASE MUTATION: NONE
# CALLER-OWNED TRANSACTION: YES
# ABORT SEMANTICS CERTIFIED: YES
# TTL: NONE
# DELETE AUTHORITY: NONE
# OFFLINE INSTALLATION TRUST AUTHORITY: NONE
# SYSTEM PERMISSION GRANT AUTHORITY: NONE
# SYSTEM PERMISSION REVOCATION AUTHORITY: NONE
# ASSIGNMENT COMMAND AUTHORITY: NONE
# REVOCATION COMMAND AUTHORITY: NONE
# PRIVILEGED ACTIVATION AUTHORITY: NONE
# BREAK-GLASS AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS TEST ARTIFACT
