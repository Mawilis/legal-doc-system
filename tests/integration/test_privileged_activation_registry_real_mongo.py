"""
TITLE:
    WILSY OS Privileged Activation Registry Real-Mongo Certificate

VERSION:
    v1.0.0-P4-R3-PRIVILEGED-ACTIVATION-REGISTRY-REAL-MONGO

AUTHORITY:
    Wilsy OS Sovereign IAM

PURPOSE:
    Certify the P4 privileged activation durable registry against a writable
    Mongo replica set using caller-owned transactions, immutable activation
    history, exact replay, exact scope isolation, revocation, temporal expiry,
    corruption rejection, BSON UTC hydration and authority-boundary absence.

CERTIFICATION DATE:
    2026-10-14

CHANGELOG:
    v1.0.0-P4-R3-PRIVILEGED-ACTIVATION-REGISTRY-REAL-MONGO
        Initial real-Mongo certificate for the P4-R2 registry. Certifies the
        canonical target-class contract: TENANT_PRIVILEGED requires an exact
        tenant; PLATFORM_SYSTEM_ROOT forbids tenant material and uses tenant_id
        None. Creates no activation issuance, P5 use, break-glass, or financial
        authority.

AUTHORITY BOUNDARY:
    Persistence certification only. P4 activation issuance/orchestration remains
    unauthorized.

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

from tools.eos.auth.privileged_activation import (
    PrivilegedActivation,
)
from tools.eos.auth.privileged_activation_registry import (
    PrivilegedActivationConflictError,
    PrivilegedActivationPersistedInvalidError,
    PrivilegedActivationRegistry,
    PrivilegedActivationRegistryError,
)
from tools.eos.auth.privileged_eligibility import (
    PrivilegedTargetClass,
)
from tools.eos.auth.privileged_security_assurance import (
    PrivilegedAssurancePurpose,
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
    12,
    0,
    0,
    tzinfo=timezone.utc,
)

COLLECTION = "privileged_activations"


def activation(
    *,
    activation_id: str = "activation-a",
    tenant_id: str | None = "tenant-a",
    principal_id: str = "principal-a",
    actor_principal_id: str = "principal-a",
    privileged_role_id: str = "ENTERPRISE_ADMIN",
    target_class: PrivilegedTargetClass = (
        PrivilegedTargetClass.TENANT_PRIVILEGED
    ),
    eligibility_evidence_id: str = "eligibility-a",
    eligibility_evidence_fingerprint: str = "a" * 128,
    assurance_evidence_id: str = "assurance-a",
    assurance_evidence_fingerprint: str = "b" * 128,
    activated_at: datetime = NOW,
    effective_until: datetime = (
        NOW + timedelta(minutes=15)
    ),
    issuance_idempotency_key: str = "issue-a",
) -> PrivilegedActivation:
    return PrivilegedActivation.issue(
        activation_id=activation_id,
        tenant_id=tenant_id,
        principal_id=principal_id,
        actor_principal_id=actor_principal_id,
        privileged_role_id=privileged_role_id,
        target_class=target_class,
        eligibility_evidence_id=
            eligibility_evidence_id,
        eligibility_evidence_fingerprint=
            eligibility_evidence_fingerprint,
        assurance_evidence_id=
            assurance_evidence_id,
        assurance_evidence_fingerprint=
            assurance_evidence_fingerprint,
        creation_assurance_purpose=(
            PrivilegedAssurancePurpose
            .PRIVILEGED_ELIGIBILITY_TO_ACTIVATION
        ),
        activated_at=activated_at,
        effective_until=effective_until,
        issuance_idempotency_key=
            issuance_idempotency_key,
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

    assert (
        hello.get("setName")
        == EXPECTED_REPLICA_SET
    )
    assert (
        hello.get("isWritablePrimary")
        is True
    )
    assert (
        hello.get("logicalSessionTimeoutMinutes")
        is not None
    )

    db_name = (
        "wilsy_p4_r3_"
        + uuid4().hex[:20]
    )

    database = client[db_name]
    collection = database[COLLECTION]

    registry = PrivilegedActivationRegistry(
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
    value: PrivilegedActivation,
) -> PrivilegedActivation:
    with context["client"].start_session() as session:
        session.start_transaction()

        result = context[
            "registry"
        ].create_or_replay(
            value,
            session=session,
        )

        session.commit_transaction()

    return result


def _commit_revoke(
    context: Any,
    value: PrivilegedActivation,
    *,
    key: str,
) -> PrivilegedActivation:
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


def _current(
    context: Any,
    *,
    tenant_id: str | None = "tenant-a",
    principal_id: str = "principal-a",
    privileged_role_id: str = "ENTERPRISE_ADMIN",
    target_class: PrivilegedTargetClass = (
        PrivilegedTargetClass.TENANT_PRIVILEGED
    ),
    at: datetime = NOW,
) -> PrivilegedActivation | None:
    return context[
        "registry"
    ].resolve_current(
        tenant_id=tenant_id,
        principal_id=principal_id,
        privileged_role_id=privileged_role_id,
        target_class=target_class,
        at=at,
    )


def test_real_index_contract_and_no_ttl(
    mongo_context: Any,
) -> None:
    indexes = list(
        mongo_context[
            "collection"
        ].list_indexes()
    )

    assert len(indexes) == 4

    custom = [
        index
        for index in indexes
        if index["name"] != "_id_"
    ]

    assert len(custom) == 3

    assert all(
        "expireAfterSeconds"
        not in index
        for index in custom
    )


def test_real_active_create_hydrate_and_exact_replay(
    mongo_context: Any,
) -> None:
    value = activation()

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
                "activation_id":
                    value.activation_id,
            }
        )
    )

    assert len(rows) == 1

    raw = rows[0]

    assert isinstance(
        raw["activated_at"],
        datetime,
    )

    assert raw["activated_at"].tzinfo is None

    loaded = mongo_context[
        "registry"
    ].get_history(
        value.activation_id
    )

    assert loaded == (value,)

    assert (
        loaded[0].activated_at.tzinfo
        is timezone.utc
    )


def test_real_divergent_replay_denied(
    mongo_context: Any,
) -> None:
    first = activation()

    _commit_create(
        mongo_context,
        first,
    )

    divergent = activation(
        activation_id="activation-b",
        assurance_evidence_id="assurance-b",
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            PrivilegedActivationConflictError,
            match="IDEMPOTENCY_KEY_DIVERGENT_REPLAY",
        ):
            mongo_context[
                "registry"
            ].create_or_replay(
                divergent,
                session=session,
            )

        session.abort_transaction()

    assert (
        mongo_context[
            "collection"
        ].count_documents({})
        == 1
    )


def test_real_activation_id_collision_denied(
    mongo_context: Any,
) -> None:
    first = activation()

    _commit_create(
        mongo_context,
        first,
    )

    collision = activation(
        issuance_idempotency_key="issue-b",
        assurance_evidence_id="assurance-b",
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        with pytest.raises(
            PrivilegedActivationConflictError,
            match="ACTIVATION_ID_COLLISION",
        ):
            mongo_context[
                "registry"
            ].create_or_replay(
                collision,
                session=session,
            )

        session.abort_transaction()


def test_real_tenant_scope_isolation_and_expiry(
    mongo_context: Any,
) -> None:
    value = activation()

    _commit_create(
        mongo_context,
        value,
    )

    assert _current(
        mongo_context,
        at=(
            value.effective_until
            - timedelta(microseconds=1)
        ),
    ) == value

    assert _current(
        mongo_context,
        at=value.effective_until,
    ) is None

    assert _current(
        mongo_context,
        tenant_id="tenant-b",
    ) is None

    assert _current(
        mongo_context,
        principal_id="principal-b",
    ) is None

    assert _current(
        mongo_context,
        privileged_role_id="SOVEREIGN_ARCHITECT",
    ) is None

    assert (
        mongo_context[
            "collection"
        ].count_documents(
            {
                "activation_id":
                    value.activation_id,
            }
        )
        == 1
    )


def test_real_platform_scope_forbids_tenant_material(
    mongo_context: Any,
) -> None:
    with pytest.raises(
        PrivilegedActivationRegistryError,
        match="PLATFORM_SCOPE_TENANT_FORBIDDEN",
    ):
        _current(
            mongo_context,
            tenant_id="tenant-a",
            principal_id="principal-a",
            privileged_role_id="SOVEREIGN_ARCHITECT",
            target_class=(
                PrivilegedTargetClass
                .PLATFORM_SYSTEM_ROOT
            ),
        )


def test_real_platform_scope_is_exact_and_isolated(
    mongo_context: Any,
) -> None:
    assert _current(
        mongo_context,
        tenant_id=None,
        principal_id="principal-a",
        privileged_role_id="SOVEREIGN_ARCHITECT",
        target_class=(
            PrivilegedTargetClass
            .PLATFORM_SYSTEM_ROOT
        ),
    ) is None


def test_real_revocation_history_and_replay(
    mongo_context: Any,
) -> None:
    active = activation()

    _commit_create(
        mongo_context,
        active,
    )

    revoked = active.revoke(
        revoked_at=(
            NOW
            + timedelta(minutes=1)
        )
    )

    first = _commit_revoke(
        mongo_context,
        revoked,
        key="revoke-a",
    )

    second = _commit_revoke(
        mongo_context,
        revoked,
        key="revoke-a",
    )

    assert first == second == revoked

    history = mongo_context[
        "registry"
    ].get_history(
        active.activation_id
    )

    assert history == (
        active,
        revoked,
    )

    assert _current(
        mongo_context,
        at=NOW,
    ) is None

    assert (
        mongo_context[
            "collection"
        ].count_documents(
            {
                "activation_id":
                    active.activation_id,
            }
        )
        == 2
    )


def test_real_caller_abort_create_leaves_zero_rows(
    mongo_context: Any,
) -> None:
    value = activation(
        activation_id="abort-create",
        issuance_idempotency_key="abort-create",
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        result = mongo_context[
            "registry"
        ].create_or_replay(
            value,
            session=session,
        )

        assert result == value

        assert (
            mongo_context[
                "collection"
            ].count_documents(
                {
                    "activation_id":
                        value.activation_id,
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
                "activation_id":
                    value.activation_id,
            }
        )
        == 0
    )


def test_real_caller_abort_revocation_preserves_active(
    mongo_context: Any,
) -> None:
    active = activation()

    _commit_create(
        mongo_context,
        active,
    )

    revoked = active.revoke(
        revoked_at=(
            NOW
            + timedelta(minutes=1)
        )
    )

    with mongo_context[
        "client"
    ].start_session() as session:
        session.start_transaction()

        result = mongo_context[
            "registry"
        ].revoke_or_replay(
            revoked,
            revocation_idempotency_key="abort-revoke",
            session=session,
        )

        assert result == revoked

        session.abort_transaction()

    history = mongo_context[
        "registry"
    ].get_history(
        active.activation_id
    )

    assert history == (active,)

    assert _current(
        mongo_context,
        at=NOW,
    ) == active


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("status", "BROKEN"),
        ("activated_at", "not-time"),
        ("revision", 7),
        (
            "activation_fingerprint",
            "0" * 128,
        ),
    ),
)
def test_real_corrupt_persisted_state_fails_closed(
    mongo_context: Any,
    field: str,
    value: object,
) -> None:
    active = activation()

    _commit_create(
        mongo_context,
        active,
    )

    mongo_context[
        "collection"
    ].update_one(
        {
            "activation_id":
                active.activation_id,
        },
        {
            "$set": {
                field: value,
            }
        },
    )

    with pytest.raises(
        PrivilegedActivationPersistedInvalidError
    ):
        mongo_context[
            "registry"
        ].get_history(
            active.activation_id
        )


def test_real_no_ttl_secrets_or_forbidden_authority(
    mongo_context: Any,
) -> None:
    active = activation()

    _commit_create(
        mongo_context,
        active,
    )

    row = mongo_context[
        "collection"
    ].find_one(
        {
            "activation_id":
                active.activation_id,
        }
    )

    assert row is not None

    lowered = {
        str(key).casefold()
        for key in row
    }

    for forbidden in (
        "password",
        "otp",
        "mfa_secret",
        "jwt",
        "bearer",
        "private_key",
        "raw_signature",
        "workload_secret",
    ):
        assert all(
            forbidden not in key
            for key in lowered
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

    collections = set(
        mongo_context[
            "database"
        ].list_collection_names()
    )

    forbidden_collections = {
        name
        for name in collections
        if (
            "break_glass" in name
            or "financial" in name
            or "payment" in name
            or "settlement" in name
            or "privileged_activation_use"
            in name
        )
    }

    assert forbidden_collections == set()


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

    assert (
        mongo_context[
            "db_name"
        ].startswith(
            "wilsy_p4_r3_"
        )
    )


# =============================================================================
# WILSY OS TEST ARTIFACT SEAL
# ARTIFACT: test_privileged_activation_registry_real_mongo.py
# VERSION: v1.0.0-P4-R3-PRIVILEGED-ACTIVATION-REGISTRY-REAL-MONGO
# PRODUCTION AUTHORITY: NONE
# P4 ACTIVATION ISSUANCE AUTHORITY: NONE
# P5 PRIVILEGED USE AUTHORITY: NONE
# P7 BREAK-GLASS AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS TEST ARTIFACT
