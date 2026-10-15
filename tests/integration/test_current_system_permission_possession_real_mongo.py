"""
TITLE:
    WILSY OS Current System Permission Possession Real-Mongo Certificate

VERSION:
    v1.0.0-P4-R4-D10-CURRENT-SYSTEM-PERMISSION-POSSESSION-REAL-MONGO

AUTHORITY:
    Wilsy OS Sovereign IAM certification only.

PURPOSE:
    Certify that current SYSTEM permission possession is true only when an exact
    principal is currently ACTIVE and an exact SYSTEM permission assignment is
    currently ACTIVE, with the same caller-owned ClientSession propagated to both
    authoritative real-Mongo reads.

AUTHORITY BOUNDARY:
    Certification only. This file creates no assignment-command authority,
    privileged eligibility, security assurance, privileged activation, P4
    issuance authorization, break-glass authority, or financial authority.

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

from tools.eos.auth.current_system_permission_possession import (
    CurrentSystemPermissionPossessionError,
    CurrentSystemPermissionPossessionResolver,
)
from tools.eos.auth.principal_authority import (
    PrincipalAuthority,
)
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityRepository,
)
from tools.eos.auth.principal_status import (
    PrincipalStatus,
)
from tools.eos.auth.system_permission_assignment import (
    SystemPermissionAssignment,
)
from tools.eos.auth.system_permission_assignment_registry import (
    SystemPermissionAssignmentRegistry,
)


URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

PERMISSION = "privileged_activation:issue"

NOW = datetime(
    2026,
    10,
    14,
    18,
    0,
    tzinfo=timezone.utc,
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
        "wilsy_p4_r4_d10_"
        + uuid4().hex[:20]
    )

    assert db_name != "wilsy"

    database = client[db_name]

    principal_collection = database[
        "principal_authorities"
    ]

    assignment_collection = database[
        "system_permission_assignments"
    ]

    assignment_registry = (
        SystemPermissionAssignmentRegistry(
            assignment_collection
        )
    )

    assignment_registry.ensure_indexes()

    resolver = (
        CurrentSystemPermissionPossessionResolver(
            principal_collection=
                principal_collection,
            assignment_registry=
                assignment_registry,
        )
    )

    try:
        yield {
            "client": client,
            "database": database,
            "db_name": db_name,
            "principal_collection":
                principal_collection,
            "assignment_collection":
                assignment_collection,
            "assignment_registry":
                assignment_registry,
            "resolver": resolver,
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


def principal(
    *,
    principal_id: str = "principal-a",
    status: PrincipalStatus =
        PrincipalStatus.ACTIVE,
    revision: int = 1,
) -> PrincipalAuthority:
    return PrincipalAuthority(
        principal_id,
        status,
        revision,
    )


def assignment(
    *,
    assignment_id: str = "assignment-a",
    principal_id: str = "principal-a",
) -> SystemPermissionAssignment:
    return SystemPermissionAssignment.assign(
        assignment_id=assignment_id,
        principal_id=principal_id,
        permission_id=PERMISSION,
        assigned_by_principal_id="grantor-a",
        assigned_at=NOW,
        assignment_evidence_reference=
            "assignment-evidence",
    )


def _persist_principal(
    context: Any,
    value: PrincipalAuthority,
) -> None:
    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        PrincipalAuthorityRepository.create(
            value,
            collection=context[
                "principal_collection"
            ],
            session=session,
        )

        session.commit_transaction()


def _persist_assignment(
    context: Any,
    value: SystemPermissionAssignment,
    *,
    key: str = "create-a",
) -> None:
    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        context[
            "assignment_registry"
        ].create_or_replay(
            value,
            idempotency_key=key,
            session=session,
        )

        session.commit_transaction()


def _persist_revocation(
    context: Any,
    value: SystemPermissionAssignment,
    *,
    key: str = "revoke-a",
) -> None:
    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        context[
            "assignment_registry"
        ].revoke_or_replay(
            value,
            revocation_idempotency_key=
                key,
            session=session,
        )

        session.commit_transaction()


def test_active_principal_plus_active_assignment_allows(
    mongo_context: Any,
) -> None:
    _persist_principal(
        mongo_context,
        principal(),
    )

    active = assignment()

    _persist_assignment(
        mongo_context,
        active,
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        observed = mongo_context[
            "resolver"
        ].resolve(
            principal_id="principal-a",
            permission_id=PERMISSION,
            session=session,
        )

        assert observed == active

        session.abort_transaction()


def test_missing_principal_denies(
    mongo_context: Any,
) -> None:
    _persist_assignment(
        mongo_context,
        assignment(),
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        assert mongo_context[
            "resolver"
        ].possesses(
            principal_id="principal-a",
            permission_id=PERMISSION,
            session=session,
        ) is False

        session.abort_transaction()


@pytest.mark.parametrize(
    "status",
    (
        PrincipalStatus.SUSPENDED,
        PrincipalStatus.REVOKED,
    ),
)
def test_nonactive_principal_denies(
    mongo_context: Any,
    status: PrincipalStatus,
) -> None:
    _persist_principal(
        mongo_context,
        principal(
            status=status,
        ),
    )

    _persist_assignment(
        mongo_context,
        assignment(),
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        assert mongo_context[
            "resolver"
        ].possesses(
            principal_id="principal-a",
            permission_id=PERMISSION,
            session=session,
        ) is False

        session.abort_transaction()


def test_active_principal_missing_assignment_denies(
    mongo_context: Any,
) -> None:
    _persist_principal(
        mongo_context,
        principal(),
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        assert mongo_context[
            "resolver"
        ].possesses(
            principal_id="principal-a",
            permission_id=PERMISSION,
            session=session,
        ) is False

        session.abort_transaction()


def test_active_principal_revoked_assignment_denies(
    mongo_context: Any,
) -> None:
    _persist_principal(
        mongo_context,
        principal(),
    )

    active = assignment()

    _persist_assignment(
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

    _persist_revocation(
        mongo_context,
        revoked,
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        assert mongo_context[
            "resolver"
        ].possesses(
            principal_id="principal-a",
            permission_id=PERMISSION,
            session=session,
        ) is False

        session.abort_transaction()


def test_exact_principal_scope_isolation(
    mongo_context: Any,
) -> None:
    _persist_principal(
        mongo_context,
        principal(
            principal_id="principal-a",
        ),
    )

    _persist_principal(
        mongo_context,
        principal(
            principal_id="principal-b",
        ),
    )

    _persist_assignment(
        mongo_context,
        assignment(
            principal_id="principal-a",
        ),
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        assert mongo_context[
            "resolver"
        ].possesses(
            principal_id="principal-b",
            permission_id=PERMISSION,
            session=session,
        ) is False

        session.abort_transaction()


def test_non_system_permission_rejected(
    mongo_context: Any,
) -> None:
    _persist_principal(
        mongo_context,
        principal(),
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            CurrentSystemPermissionPossessionError
        ):
            mongo_context[
                "resolver"
            ].resolve(
                principal_id="principal-a",
                permission_id=
                    "tenant:profile:read",
                session=session,
            )

        session.abort_transaction()


def test_same_session_observes_uncommitted_principal_and_assignment(
    mongo_context: Any,
) -> None:
    value = principal()
    active = assignment()

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        PrincipalAuthorityRepository.create(
            value,
            collection=mongo_context[
                "principal_collection"
            ],
            session=session,
        )

        mongo_context[
            "assignment_registry"
        ].create_or_replay(
            active,
            idempotency_key=
                "same-session-create",
            session=session,
        )

        observed = mongo_context[
            "resolver"
        ].resolve(
            principal_id="principal-a",
            permission_id=PERMISSION,
            session=session,
        )

        assert observed == active

        session.abort_transaction()

    assert mongo_context[
        "principal_collection"
    ].count_documents({}) == 0

    assert mongo_context[
        "assignment_collection"
    ].count_documents({}) == 0


def test_resolver_writes_zero_rows(
    mongo_context: Any,
) -> None:
    _persist_principal(
        mongo_context,
        principal(),
    )

    active = assignment()

    _persist_assignment(
        mongo_context,
        active,
    )

    before_principals = mongo_context[
        "principal_collection"
    ].count_documents({})

    before_assignments = mongo_context[
        "assignment_collection"
    ].count_documents({})

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        assert mongo_context[
            "resolver"
        ].resolve(
            principal_id="principal-a",
            permission_id=PERMISSION,
            session=session,
        ) == active

        session.abort_transaction()

    assert mongo_context[
        "principal_collection"
    ].count_documents({}) == before_principals

    assert mongo_context[
        "assignment_collection"
    ].count_documents({}) == before_assignments


def test_no_authority_creation_surface(
    mongo_context: Any,
) -> None:
    resolver = mongo_context[
        "resolver"
    ]

    for forbidden in (
        "assign",
        "grant",
        "revoke",
        "activate",
        "issue",
        "create",
        "persist",
        "authorize_p4",
        "break_glass",
        "execute_financial",
    ):
        assert not hasattr(
            resolver,
            forbidden,
        )


def test_replica_set_and_isolated_database(
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
        "wilsy_p4_r4_d10_"
    )

    assert mongo_context[
        "db_name"
    ] != "wilsy"


# =============================================================================
# WILSY OS TEST ARTIFACT SEAL
# ARTIFACT: tests/integration/test_current_system_permission_possession_real_mongo.py
# VERSION: v1.0.0-P4-R4-D10-CURRENT-SYSTEM-PERMISSION-POSSESSION-REAL-MONGO
# CURRENT PRINCIPAL: REQUIRED
# CURRENT SYSTEM ASSIGNMENT: REQUIRED
# SAME REAL ClientSession: REQUIRED
# RESOLVER WRITES: NONE
# TRANSACTION OWNERSHIP: CALLER
# ASSIGNMENT COMMAND AUTHORITY: NONE
# P4 ISSUANCE AUTHORIZATION: NONE
# PRIVILEGED ACTIVATION AUTHORITY: NONE
# BREAK-GLASS AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS TEST ARTIFACT
