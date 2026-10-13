"""Real-Mongo certificate for atomic tenant-workforce leaver closure.

TITLE: WILSY W3C Tenant Workforce Leaver Real-Mongo Certificate
VERSION: v1.0.0-W3C-R7-REAL-MONGO

Certifies one caller-owned Mongo transaction across:
- immutable W3B workforce ENDED revision;
- tenant membership revocation;
- all ACTIVE tenant role revocations;
- exact tenant session revocation;
- exact tenant refresh-token revocation.

Also certifies abort atomicity, exact replay, divergent replay rejection,
other-tenant preservation and global-principal preservation.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.database import Database

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import (
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentRepository,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository,
)
from tools.eos.kernel import db as kernel_db
from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceRelationshipStatus,
    WorkforceRelationshipType,
    WorkforceScopeKind,
)
from tools.eos.workforce.orchestration import (
    tenant_workforce_leaver_orchestrator as orchestrator,
)
from tools.eos.workforce.registry import (
    workforce_relationship_registry as workforce_registry,
)


URI_ENV = "TEST_VENDOR_MONGO_URI"
DEFAULT_URI = (
    "mongodb://127.0.0.1:27017/"
    "?replicaSet=wilsyVendorCertRS"
)
REPLICA_SET = "wilsyVendorCertRS"
DATABASE_PREFIX = "wilsy_w3c_r7_leaver_"

AT = datetime(
    2026,
    10,
    13,
    6,
    0,
    tzinfo=timezone.utc,
)
ENDED_AT = AT + timedelta(hours=1)

TENANT = "tenant-w3c-r7"
OTHER_TENANT = "tenant-w3c-r7-other"
PRINCIPAL = "principal-w3c-r7"
OTHER_PRINCIPAL = "principal-w3c-r7-other"
RELATIONSHIP = "employment-w3c-r7"
ROLE_ONE = "LEGAL_PARTNER"
ROLE_TWO = "AUDITOR"

TENANT_TEMPLATE: dict[str, Any] = {
    'created_at': '2026-09-22T12:00:00+00:00',
    'industry': 'Certification',
    'name': 'Synthetic certification tenant',
    'status': 'ACTIVE',
    'subscription': {
    'plan': 'BASIC'
},
    'tenant_id': '__W3C_TENANT__'
}
USER_TEMPLATE: dict[str, Any] = {
    'createdAt': datetime(2026, 9, 22, 12, 0, 0, 0, tzinfo=timezone.utc),
    'credential_revision': 0,
    'email': '__W3C_USER__@example.com',
    'firstName': 'Synthetic',
    'hasSignedCovenant': True,
    'lastName': 'Principal',
    'mfaRegistered': True,
    'passwordHash': 'bcrypt-approved-synthetic',
    'permissions': ['legal:read'],
    'role': 'USER',
    'tenantId': '__W3C_TENANT__',
    'updatedAt': datetime(2026, 9, 22, 12, 0, 0, 0, tzinfo=timezone.utc),
    'user_id': '__W3C_USER__'
}


def _tenant_document(tenant_id: str) -> dict[str, Any]:
    value = deepcopy(TENANT_TEMPLATE)
    value["tenant_id"] = tenant_id
    return value


def _user_document(
    tenant_id: str,
    user_id: str,
) -> dict[str, Any]:
    value = deepcopy(USER_TEMPLATE)

    value["user_id"] = user_id
    value["tenantId"] = tenant_id

    if "email" in value:
        value["email"] = f"{user_id}@example.com"

    if "passwordHash" in value:
        value["passwordHash"] = "bcrypt-approved-synthetic"

    if "credential_revision" in value:
        value["credential_revision"] = 0

    return value


def _relationship() -> WorkforceRelationship:
    return WorkforceRelationship(
        relationship_id=RELATIONSHIP,
        revision=1,
        scope_kind=WorkforceScopeKind.TENANT,
        scope_id=TENANT,
        principal_id=PRINCIPAL,
        relationship_type=WorkforceRelationshipType.EMPLOYEE,
        status=WorkforceRelationshipStatus.ACTIVE,
        effective_from=AT,
        effective_until=None,
        status_effective_at=AT,
        reason_reference="hire-ref",
        supersedes_fingerprint=None,
    )


class Context:
    def __init__(
        self,
        client: MongoClient[Any],
        database_name: str,
    ) -> None:
        self.client = client
        self.database_name = database_name
        self.database: Database[Any] = client[
            database_name
        ]

        self.workforce = self.database[
            workforce_registry.COLLECTION_NAME
        ]
        self.principals = self.database[
            "principal_authorities"
        ]
        self.memberships = self.database[
            "tenant_memberships"
        ]
        self.roles = self.database[
            "role_assignments"
        ]
        self.tenants = self.database[
            "tenants"
        ]
        self.users = self.database[
            "users"
        ]
        self.sessions = self.database[
            "sessions"
        ]
        self.refresh = self.database[
            "refresh_tokens"
        ]


def _open_client() -> MongoClient[Any]:
    uri = os.environ.get(
        URI_ENV,
        DEFAULT_URI,
    )

    client: MongoClient[Any] = MongoClient(
        uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
    )

    hello = client.admin.command("hello")

    if hello.get("setName") != REPLICA_SET:
        pytest.fail(
            "W3C_R7_REPLICA_SET_REQUIRED"
        )

    if not hello.get(
        "logicalSessionTimeoutMinutes"
    ):
        pytest.fail(
            "W3C_R7_MONGO_SESSIONS_REQUIRED"
        )

    return client


@pytest.fixture
def mongo_context(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[Context]:
    client = _open_client()

    name = DATABASE_PREFIX + uuid4().hex

    if name == "wilsy":
        pytest.fail(
            "W3C_R7_CANONICAL_DATABASE_FORBIDDEN"
        )

    context = Context(
        client,
        name,
    )

    monkeypatch.setattr(
        kernel_db,
        "get_database",
        lambda: context.database,
    )

    workforce_registry.ensure_indexes(
        context.workforce
    )
    TenantMembershipRepository.ensure_indexes(
        context.memberships
    )
    RoleAssignmentRepository.ensure_indexes(
        context.roles
    )

    context.tenants.insert_many(
        [
            _tenant_document(TENANT),
            _tenant_document(OTHER_TENANT),
        ]
    )

    context.users.insert_many(
        [
            _user_document(
                TENANT,
                PRINCIPAL,
            ),
            _user_document(
                OTHER_TENANT,
                OTHER_PRINCIPAL,
            ),
        ]
    )

    context.principals.insert_many(
        [
            {
                "principal_id": PRINCIPAL,
                "status": PrincipalStatus.ACTIVE.value,
                "revision": 0,
            },
            {
                "principal_id": OTHER_PRINCIPAL,
                "status": PrincipalStatus.ACTIVE.value,
                "revision": 0,
            },
        ]
    )

    context.memberships.insert_many(
        [
            {
                "principal_id": PRINCIPAL,
                "tenant_id": TENANT,
                "status": TenantMembershipStatus.ACTIVE.value,
                "revision": 0,
            },
            {
                "principal_id": OTHER_PRINCIPAL,
                "tenant_id": OTHER_TENANT,
                "status": TenantMembershipStatus.ACTIVE.value,
                "revision": 0,
            },
        ]
    )

    context.roles.insert_many(
        [
            {
                "principal_id": PRINCIPAL,
                "tenant_id": TENANT,
                "role_id": ROLE_ONE,
                "status": RoleAssignmentStatus.ACTIVE.value,
                "revision": 0,
            },
            {
                "principal_id": PRINCIPAL,
                "tenant_id": TENANT,
                "role_id": ROLE_TWO,
                "status": RoleAssignmentStatus.ACTIVE.value,
                "revision": 0,
            },
            {
                "principal_id": OTHER_PRINCIPAL,
                "tenant_id": OTHER_TENANT,
                "role_id": ROLE_ONE,
                "status": RoleAssignmentStatus.ACTIVE.value,
                "revision": 0,
            },
        ]
    )

    context.sessions.insert_many(
        [
            {
                "user_id": PRINCIPAL,
                "tenant_id": TENANT,
                "token": "session-a",
                "expires_at": ENDED_AT + timedelta(days=1),
            },
            {
                "user_id": PRINCIPAL,
                "tenant_id": TENANT,
                "token": "session-b",
                "expires_at": ENDED_AT + timedelta(days=1),
            },
            {
                "user_id": OTHER_PRINCIPAL,
                "tenant_id": OTHER_TENANT,
                "token": "session-other",
                "expires_at": ENDED_AT + timedelta(days=1),
            },
        ]
    )

    context.refresh.insert_many(
        [
            {
                "user_id": PRINCIPAL,
                "tenant_id": TENANT,
                "token": "refresh-a",
                "expires": ENDED_AT + timedelta(days=7),
            },
            {
                "user_id": PRINCIPAL,
                "tenant_id": TENANT,
                "token": "refresh-b",
                "expires": ENDED_AT + timedelta(days=7),
            },
            {
                "user_id": OTHER_PRINCIPAL,
                "tenant_id": OTHER_TENANT,
                "token": "refresh-other",
                "expires": ENDED_AT + timedelta(days=7),
            },
        ]
    )

    with client.start_session() as session:
        with session.start_transaction():
            workforce_registry.persist_revision(
                _relationship(),
                collection=context.workforce,
                session=session,
            )

    try:
        yield context
    finally:
        client.drop_database(name)
        client.close()


def _invoke(
    context: Context,
    session: Any,
    *,
    ended_at: datetime = ENDED_AT,
    reason: str = "termination-ref",
) -> orchestrator.TenantWorkforceLeaverResult:
    return orchestrator.close_tenant_workforce_access(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        relationship_id=RELATIONSHIP,
        ended_at=ended_at,
        reason_reference=reason,
        workforce_collection=context.workforce,
        membership_collection=context.memberships,
        role_assignment_collection=context.roles,
        auth_registry=AuthRegistry(),
        session=session,
    )


def _principal_row(
    context: Context,
) -> dict[str, Any]:
    row = context.principals.find_one(
        {"principal_id": PRINCIPAL},
        {"_id": 0},
    )
    assert row is not None
    return row


def _assert_precommand_state(
    context: Context,
) -> None:
    history = tuple(
        context.workforce.find(
            {
                "scope_kind": "TENANT",
                "scope_id": TENANT,
                "relationship_id": RELATIONSHIP,
            }
        ).sort("revision", 1)
    )

    assert len(history) == 1
    assert history[0]["status"] == "ACTIVE"

    membership = context.memberships.find_one(
        {
            "principal_id": PRINCIPAL,
            "tenant_id": TENANT,
        }
    )
    assert membership is not None
    assert membership["status"] == "ACTIVE"

    assignments = tuple(
        context.roles.find(
            {
                "principal_id": PRINCIPAL,
                "tenant_id": TENANT,
            }
        )
    )

    assert len(assignments) == 2
    assert all(
        row["status"] == "ACTIVE"
        for row in assignments
    )

    assert context.sessions.count_documents(
        {
            "tenant_id": TENANT,
            "user_id": PRINCIPAL,
        }
    ) == 2

    assert context.refresh.count_documents(
        {
            "tenant_id": TENANT,
            "user_id": PRINCIPAL,
        }
    ) == 2


def _assert_other_tenant_unchanged(
    context: Context,
) -> None:
    membership = context.memberships.find_one(
        {
            "principal_id": OTHER_PRINCIPAL,
            "tenant_id": OTHER_TENANT,
        }
    )
    assert membership is not None
    assert membership["status"] == "ACTIVE"

    role = context.roles.find_one(
        {
            "principal_id": OTHER_PRINCIPAL,
            "tenant_id": OTHER_TENANT,
        }
    )
    assert role is not None
    assert role["status"] == "ACTIVE"

    assert context.sessions.count_documents(
        {
            "tenant_id": OTHER_TENANT,
            "user_id": OTHER_PRINCIPAL,
        }
    ) == 1

    assert context.refresh.count_documents(
        {
            "tenant_id": OTHER_TENANT,
            "user_id": OTHER_PRINCIPAL,
        }
    ) == 1


def test_real_commit_atomically_closes_exact_tenant_authority(
    mongo_context: Context,
) -> None:
    context = mongo_context
    principal_before = _principal_row(context)

    _assert_precommand_state(context)

    with context.client.start_session() as session:
        with session.start_transaction():
            result = _invoke(
                context,
                session,
            )

    assert (
        result.relationship.status
        is WorkforceRelationshipStatus.ENDED
    )
    assert (
        result.membership.status
        is TenantMembershipStatus.REVOKED
    )
    assert set(result.revoked_role_ids) == {
        ROLE_ONE,
        ROLE_TWO,
    }
    assert result.revoked_session_count == 2
    assert result.revoked_refresh_token_count == 2
    assert result.exact_replay is False

    history = tuple(
        context.workforce.find(
            {
                "scope_kind": "TENANT",
                "scope_id": TENANT,
                "relationship_id": RELATIONSHIP,
            }
        ).sort("revision", 1)
    )

    assert len(history) == 2
    assert history[-1]["status"] == "ENDED"

    membership = context.memberships.find_one(
        {
            "principal_id": PRINCIPAL,
            "tenant_id": TENANT,
        }
    )
    assert membership is not None
    assert membership["status"] == "REVOKED"
    assert membership["revision"] == 1

    assignments = tuple(
        context.roles.find(
            {
                "principal_id": PRINCIPAL,
                "tenant_id": TENANT,
            }
        )
    )

    assert all(
        row["status"] == "REVOKED"
        and row["revision"] == 1
        for row in assignments
    )

    assert context.sessions.count_documents(
        {
            "tenant_id": TENANT,
            "user_id": PRINCIPAL,
        }
    ) == 0

    assert context.refresh.count_documents(
        {
            "tenant_id": TENANT,
            "user_id": PRINCIPAL,
        }
    ) == 0

    assert _principal_row(context) == principal_before

    _assert_other_tenant_unchanged(context)


def test_real_abort_restores_every_precommand_authority(
    mongo_context: Context,
) -> None:
    context = mongo_context
    principal_before = _principal_row(context)

    with context.client.start_session() as session:
        session.start_transaction()

        result = _invoke(
            context,
            session,
        )

        assert (
            result.relationship.status
            is WorkforceRelationshipStatus.ENDED
        )

        session.abort_transaction()

    _assert_precommand_state(context)
    assert _principal_row(context) == principal_before
    _assert_other_tenant_unchanged(context)


def test_real_exact_replay_and_divergence(
    mongo_context: Context,
) -> None:
    context = mongo_context

    with context.client.start_session() as session:
        with session.start_transaction():
            first = _invoke(
                context,
                session,
            )

    assert first.exact_replay is False

    with context.client.start_session() as session:
        with session.start_transaction():
            replay = _invoke(
                context,
                session,
            )

    assert replay.exact_replay is True
    assert replay.revoked_role_ids == ()
    assert replay.revoked_session_count == 0
    assert replay.revoked_refresh_token_count == 0

    assert context.workforce.count_documents(
        {
            "scope_kind": "TENANT",
            "scope_id": TENANT,
            "relationship_id": RELATIONSHIP,
        }
    ) == 2

    with context.client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            orchestrator.TenantWorkforceLeaverConflictError,
            match="DIVERGENT_ENDED_REPLAY",
        ):
            _invoke(
                context,
                session,
                reason="different-termination-ref",
            )

        session.abort_transaction()

    assert context.workforce.count_documents(
        {
            "scope_kind": "TENANT",
            "scope_id": TENANT,
            "relationship_id": RELATIONSHIP,
        }
    ) == 2

    _assert_other_tenant_unchanged(context)


# CERTIFICATE:
# UUID-isolated disposable real Mongo only.
# One caller transaction spans W3B + IAM + session + refresh authority.
# Abort leaves no partial tenant-leaver mutation.
# Global PrincipalAuthority is unchanged.
# Unrelated tenant authority is unchanged.
# No financial/commercial authority.
