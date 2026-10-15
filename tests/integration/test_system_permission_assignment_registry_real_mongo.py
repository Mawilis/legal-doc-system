"""
TITLE:
    WILSY OS System Permission Assignment Registry Real-Mongo Certificate

VERSION:
    v1.0.0-P4-R4-D8-SYSTEM-PERMISSION-ASSIGNMENT-REGISTRY-REAL-MONGO

AUTHORITY:
    Wilsy OS Sovereign IAM certification only.

PURPOSE:
    Certify the D7 durable SYSTEM permission-assignment registry against a real
    writable Mongo replica set using caller-owned transactions, exact replay,
    immutable revision history, strict scope isolation, BSON datetime hydration,
    transaction abort semantics and fail-closed corruption handling.

AUTHORITY BOUNDARY:
    Persistence certification only. This certificate creates no assignment
    command authority, current-principal authority, final permission
    authorization, P4 activation, P5 use, break-glass, or financial authority.

FINANCIAL AUTHORITY BOUNDARY:
    NONE.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.auth.system_permission_assignment import (
    SystemPermissionAssignment,
)
from tools.eos.auth.system_permission_assignment_registry import (
    SystemPermissionAssignmentConflictError,
    SystemPermissionAssignmentPersistedInvalidError,
    SystemPermissionAssignmentRegistry,
)


URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

NOW = datetime(
    2026,
    10,
    14,
    16,
    30,
    tzinfo=timezone.utc,
)

PERMISSION = "privileged_activation:issue"

COLLECTION = "system_permission_assignments"


def assignment(
    *,
    assignment_id: str = "assignment-a",
    principal_id: str = "principal-a",
    assigned_by_principal_id: str = "grantor-a",
    assigned_at: datetime = NOW,
) -> SystemPermissionAssignment:
    return SystemPermissionAssignment.assign(
        assignment_id=assignment_id,
        principal_id=principal_id,
        permission_id=PERMISSION,
        assigned_by_principal_id=assigned_by_principal_id,
        assigned_at=assigned_at,
        assignment_evidence_reference="assignment-evidence",
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

    hello = client.admin.command("hello")

    assert hello.get("setName") == EXPECTED_REPLICA_SET
    assert hello.get("isWritablePrimary") is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None

    db_name = (
        "wilsy_p4_r4_d8_"
        + uuid4().hex[:20]
    )

    database = client[db_name]
    collection = database[COLLECTION]

    registry = SystemPermissionAssignmentRegistry(
        collection
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
        client.drop_database(db_name)

        assert (
            db_name
            not in client.list_database_names()
        )

        client.close()


def _commit_create(
    context: Any,
    value: SystemPermissionAssignment,
    *,
    key: str = "create-a",
) -> SystemPermissionAssignment:
    with context["client"].start_session() as session:
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


def _commit_revoke(
    context: Any,
    value: SystemPermissionAssignment,
    *,
    key: str = "revoke-a",
) -> SystemPermissionAssignment:
    with context["client"].start_session() as session:
        session.start_transaction()

        result = context[
            "registry"
        ].revoke_or_replay(
            value,
            revocation_idempotency_key=key,
            session=session,
        )

        session.commit_transaction()

    return result


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

    assert len(indexes) == 4

    revision = indexes[
        "system_permission_assignment_revision_unique"
    ]
    replay = indexes[
        "system_permission_assignment_scope_operation_idempotency_unique"
    ]
    history = indexes[
        "system_permission_assignment_scope_history"
    ]

    assert revision["key"] == {
        "assignment_id": 1,
        "revision": 1,
    }
    assert revision.get("unique") is True

    assert replay["key"] == {
        "principal_id": 1,
        "permission_id": 1,
        "_operation_idempotency_key": 1,
    }
    assert replay.get("unique") is True

    assert history["key"] == {
        "principal_id": 1,
        "permission_id": 1,
        "assigned_at": 1,
        "assignment_id": 1,
        "revision": 1,
    }
    assert history.get("unique") is not True

    assert all(
        "expireAfterSeconds"
        not in entry
        for entry in indexes.values()
    )


def test_real_active_create_hydrate_and_exact_replay(
    mongo_context: Any,
) -> None:
    value = assignment()

    first = _commit_create(
        mongo_context,
        value,
    )

    second = _commit_create(
        mongo_context,
        value,
    )

    assert first == second == value

    rows = list(
        mongo_context[
            "collection"
        ].find(
            {
                "assignment_id":
                    value.assignment_id,
            }
        )
    )

    assert len(rows) == 1

    raw = rows[0]

    assert isinstance(
        raw["assigned_at"],
        datetime,
    )

    assert raw["assigned_at"].tzinfo is None

    history = mongo_context[
        "registry"
    ].get_history(
        value.assignment_id
    )

    assert history == (value,)
    assert (
        history[0].assigned_at.tzinfo
        is timezone.utc
    )


def test_real_divergent_create_replay_denied(
    mongo_context: Any,
) -> None:
    first = assignment(
        assignment_id="assignment-a",
    )

    _commit_create(
        mongo_context,
        first,
        key="create-a",
    )

    divergent = assignment(
        assignment_id="assignment-b",
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            SystemPermissionAssignmentConflictError,
            match="IDEMPOTENCY_KEY_DIVERGENT_REPLAY",
        ):
            mongo_context[
                "registry"
            ].create_or_replay(
                divergent,
                idempotency_key="create-a",
                session=session,
            )

        session.abort_transaction()

    assert (
        mongo_context[
            "collection"
        ].count_documents({})
        == 1
    )


def test_real_assignment_id_collision_denied(
    mongo_context: Any,
) -> None:
    first = assignment()

    _commit_create(
        mongo_context,
        first,
        key="create-a",
    )

    collision = assignment(
        principal_id="principal-b",
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            SystemPermissionAssignmentConflictError,
            match="ASSIGNMENT_ID_COLLISION",
        ):
            mongo_context[
                "registry"
            ].create_or_replay(
                collision,
                idempotency_key="create-b",
                session=session,
            )

        session.abort_transaction()


def test_real_exact_scope_isolation_and_active_resolution(
    mongo_context: Any,
) -> None:
    value = assignment()

    _commit_create(
        mongo_context,
        value,
    )

    assert mongo_context[
        "registry"
    ].resolve_current(
        principal_id="principal-a",
        permission_id=PERMISSION,
    ) == value

    assert mongo_context[
        "registry"
    ].resolve_current(
        principal_id="principal-b",
        permission_id=PERMISSION,
    ) is None


def test_real_revocation_append_only_history_and_replay(
    mongo_context: Any,
) -> None:
    active = assignment()

    _commit_create(
        mongo_context,
        active,
    )

    revoked = active.revoke(
        revoked_by_principal_id="revoker-a",
        revoked_at=(
            NOW
            + timedelta(minutes=1)
        ),
        revocation_evidence_reference=
            "revocation-evidence",
    )

    first = _commit_revoke(
        mongo_context,
        revoked,
    )

    second = _commit_revoke(
        mongo_context,
        revoked,
    )

    assert first == second == revoked

    history = mongo_context[
        "registry"
    ].get_history(
        active.assignment_id
    )

    assert history == (
        active,
        revoked,
    )

    assert (
        mongo_context[
            "registry"
        ].resolve_current(
            principal_id="principal-a",
            permission_id=PERMISSION,
        )
        is None
    )

    assert (
        mongo_context[
            "collection"
        ].count_documents(
            {
                "assignment_id":
                    active.assignment_id,
            }
        )
        == 2
    )


def test_real_caller_abort_create_leaves_zero_rows(
    mongo_context: Any,
) -> None:
    value = assignment(
        assignment_id="abort-create",
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
                    "assignment_id":
                        value.assignment_id,
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
                "assignment_id":
                    value.assignment_id,
            }
        )
        == 0
    )


def test_real_caller_abort_revocation_preserves_active(
    mongo_context: Any,
) -> None:
    active = assignment()

    _commit_create(
        mongo_context,
        active,
    )

    revoked = active.revoke(
        revoked_by_principal_id="revoker-a",
        revoked_at=(
            NOW
            + timedelta(minutes=1)
        ),
        revocation_evidence_reference=
            "revocation-evidence",
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        result = mongo_context[
            "registry"
        ].revoke_or_replay(
            revoked,
            revocation_idempotency_key=
                "abort-revoke",
            session=session,
        )

        assert result == revoked

        session.abort_transaction()

    history = mongo_context[
        "registry"
    ].get_history(
        active.assignment_id
    )

    assert history == (active,)

    assert mongo_context[
        "registry"
    ].resolve_current(
        principal_id="principal-a",
        permission_id=PERMISSION,
    ) == active


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("status", "BROKEN"),
        ("assigned_at", "not-time"),
        ("revision", 7),
        (
            "assignment_fingerprint",
            "0" * 128,
        ),
    ),
)
def test_real_corrupt_persisted_material_fails_closed(
    mongo_context: Any,
    field: str,
    value: object,
) -> None:
    active = assignment()

    _commit_create(
        mongo_context,
        active,
    )

    mongo_context[
        "collection"
    ].update_one(
        {
            "assignment_id":
                active.assignment_id,
        },
        {
            "$set": {
                field: value,
            }
        },
    )

    with pytest.raises(
        SystemPermissionAssignmentPersistedInvalidError
    ):
        mongo_context[
            "registry"
        ].get_history(
            active.assignment_id
        )


def test_real_corrupt_chain_fails_closed(
    mongo_context: Any,
) -> None:
    active = assignment()

    _commit_create(
        mongo_context,
        active,
    )

    revoked = active.revoke(
        revoked_by_principal_id="revoker-a",
        revoked_at=(
            NOW
            + timedelta(minutes=1)
        ),
        revocation_evidence_reference=
            "revocation-evidence",
    )

    _commit_revoke(
        mongo_context,
        revoked,
    )

    mongo_context[
        "collection"
    ].update_one(
        {
            "assignment_id":
                active.assignment_id,
            "revision": 2,
        },
        {
            "$set": {
                "previous_assignment_fingerprint":
                    "c" * 128,
            }
        },
    )

    with pytest.raises(
        SystemPermissionAssignmentPersistedInvalidError
    ):
        mongo_context[
            "registry"
        ].get_history(
            active.assignment_id
        )


def test_real_no_ttl_delete_or_forbidden_authority(
    mongo_context: Any,
) -> None:
    active = assignment()

    _commit_create(
        mongo_context,
        active,
    )

    indexes = list(
        mongo_context[
            "collection"
        ].list_indexes()
    )

    assert all(
        "expireAfterSeconds"
        not in index
        for index in indexes
    )

    registry = mongo_context[
        "registry"
    ]

    for forbidden in (
        "delete",
        "purge",
        "authorize",
        "is_authorized",
        "assign_permission",
        "revoke_permission",
        "activate",
        "issue_activation",
        "resolve_principal",
    ):
        assert not hasattr(
            registry,
            forbidden,
        )


def test_real_replica_set_and_database_scope(
    mongo_context: Any,
) -> None:
    hello = mongo_context[
        "client"
    ].admin.command("hello")

    assert (
        hello["setName"]
        == EXPECTED_REPLICA_SET
    )

    assert mongo_context[
        "db_name"
    ].startswith(
        "wilsy_p4_r4_d8_"
    )

    assert mongo_context[
        "db_name"
    ] != "wilsy"


# =============================================================================
# WILSY OS TEST ARTIFACT SEAL
# ARTIFACT: test_system_permission_assignment_registry_real_mongo.py
# VERSION: v1.0.0-P4-R4-D8-SYSTEM-PERMISSION-ASSIGNMENT-REGISTRY-REAL-MONGO
# PRODUCTION AUTHORITY: NONE
# CURRENT PRINCIPAL AUTHORITY: NONE
# FINAL PERMISSION AUTHORIZATION: NONE
# ASSIGNMENT COMMAND AUTHORITY: NONE
# PRIVILEGED ACTIVATION AUTHORITY: NONE
# P5 PRIVILEGED USE AUTHORITY: NONE
# BREAK-GLASS AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS TEST ARTIFACT
