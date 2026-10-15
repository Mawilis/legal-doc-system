"""
TITLE:
    WILSY OS Current Bootstrap Authority Real-Mongo Composition Certificate
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Any
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.auth.current_system_permission_bootstrap_authority import (
    CurrentSystemPermissionBootstrapAuthorityResolver,
)

from tools.eos.auth.system_permission_bootstrap_authority import (
    SystemPermissionBootstrapAuthority,
)

from tools.eos.auth.system_permission_bootstrap_authority_registry import (
    SystemPermissionBootstrapAuthorityRegistry,
)


URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

PURPOSE = (
    "SEED_SYSTEM_PERMISSION_ASSIGNMENT_COMMAND_AUTHORITY"
)

OTHER_PURPOSE = (
    "SEED_SYSTEM_PERMISSION_REVOCATION_COMMAND_AUTHORITY"
)

NOW = datetime(
    2026,
    10,
    14,
    23,
    0,
    tzinfo=timezone.utc,
)


@pytest.fixture()
def context() -> Any:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        retryWrites=True,
    )

    hello = client.admin.command("hello")

    assert (
        hello.get("setName")
        == EXPECTED_REPLICA_SET
    )

    assert (
        hello.get(
            "logicalSessionTimeoutMinutes"
        )
        is not None
    )

    db_name = (
        "wilsy_p4_r4_d11_r4_"
        + uuid4().hex[:20]
    )

    assert db_name != "wilsy"

    database = client[db_name]

    principal_collection = database[
        "principal_authorities"
    ]

    bootstrap_collection = database[
        "system_permission_bootstrap_authorities"
    ]

    bootstrap_registry = (
        SystemPermissionBootstrapAuthorityRegistry(
            bootstrap_collection
        )
    )

    bootstrap_registry.ensure_indexes()

    resolver = (
        CurrentSystemPermissionBootstrapAuthorityResolver(
            principal_collection=principal_collection,
            bootstrap_registry=bootstrap_registry,
        )
    )

    try:
        yield {
            "client": client,
            "db_name": db_name,
            "database": database,
            "principal_collection":
                principal_collection,
            "bootstrap_collection":
                bootstrap_collection,
            "bootstrap_registry":
                bootstrap_registry,
            "resolver": resolver,
        }

    finally:
        client.drop_database(db_name)

        assert (
            db_name
            not in client.list_database_names()
        )

        client.close()


def seed_principal(
    context: Any,
    *,
    principal_id: str,
    status: str,
    session: Any = None,
) -> None:
    context[
        "principal_collection"
    ].insert_one(
        {
            "principal_id": principal_id,
            "status": status,
            "revision": 0,
        },
        session=session,
    )


def authority() -> SystemPermissionBootstrapAuthority:
    return SystemPermissionBootstrapAuthority.issue(
        bootstrap_id="bootstrap-a",
        actor_principal_id="principal-a",
        purpose=PURPOSE,
        evidence_reference="installation-evidence-a",
        issued_at=NOW,
    )


def test_real_active_principal_and_active_bootstrap_allow(
    context: Any,
) -> None:
    seed_principal(
        context,
        principal_id="principal-a",
        status="ACTIVE",
    )

    value = authority()

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        context[
            "bootstrap_registry"
        ].create_or_replay(
            value,
            idempotency_key="create-a",
            session=session,
        )

        resolved = context[
            "resolver"
        ].resolve(
            principal_id="principal-a",
            purpose=PURPOSE,
            session=session,
        )

        assert resolved == value
        session.abort_transaction()


@pytest.mark.parametrize(
    "status",
    (
        "SUSPENDED",
        "REVOKED",
    ),
)
def test_real_nonactive_principal_denies(
    context: Any,
    status: str,
) -> None:
    seed_principal(
        context,
        principal_id="principal-a",
        status=status,
    )

    assert context[
        "resolver"
    ].resolve(
        principal_id="principal-a",
        purpose=PURPOSE,
    ) is None


def test_real_missing_principal_denies(
    context: Any,
) -> None:
    assert context[
        "resolver"
    ].resolve(
        principal_id="principal-a",
        purpose=PURPOSE,
    ) is None


def test_real_missing_bootstrap_denies(
    context: Any,
) -> None:
    seed_principal(
        context,
        principal_id="principal-a",
        status="ACTIVE",
    )

    assert context[
        "resolver"
    ].resolve(
        principal_id="principal-a",
        purpose=PURPOSE,
    ) is None


def test_real_exact_purpose_isolation(
    context: Any,
) -> None:
    seed_principal(
        context,
        principal_id="principal-a",
        status="ACTIVE",
    )

    value = authority()

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        context[
            "bootstrap_registry"
        ].create_or_replay(
            value,
            idempotency_key="create-a",
            session=session,
        )

        assert context[
            "resolver"
        ].resolve(
            principal_id="principal-a",
            purpose=OTHER_PURPOSE,
            session=session,
        ) is None

        session.abort_transaction()


def test_real_same_transaction_visibility(
    context: Any,
) -> None:
    value = authority()

    with context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        seed_principal(
            context,
            principal_id="principal-a",
            status="ACTIVE",
            session=session,
        )

        context[
            "bootstrap_registry"
        ].create_or_replay(
            value,
            idempotency_key="create-a",
            session=session,
        )

        assert context[
            "resolver"
        ].resolve(
            principal_id="principal-a",
            purpose=PURPOSE,
            session=session,
        ) == value

        session.abort_transaction()

    assert (
        context[
            "bootstrap_collection"
        ].count_documents({})
        == 0
    )

    assert (
        context[
            "principal_collection"
        ].count_documents({})
        == 0
    )


def test_real_replica_set_and_database_scope(
    context: Any,
) -> None:
    hello = context[
        "client"
    ].admin.command("hello")

    assert (
        hello["setName"]
        == EXPECTED_REPLICA_SET
    )

    assert context[
        "db_name"
    ].startswith(
        "wilsy_p4_r4_d11_r4_"
    )

    assert context[
        "db_name"
    ] != "wilsy"


# =============================================================================
# WILSY OS TEST ARTIFACT SEAL
# ARTIFACT: tests/integration/test_current_system_permission_bootstrap_authority_real_mongo.py
# REAL MONGO: YES
# CURRENT PRINCIPAL REQUIRED: YES
# CURRENT EXACT BOOTSTRAP PURPOSE REQUIRED: YES
# SAME REAL SESSION: YES
# SAME TRANSACTION VISIBILITY: YES
# READ ONLY RESOLVER: YES
# CANONICAL WILSY DATABASE MUTATION: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS TEST ARTIFACT
