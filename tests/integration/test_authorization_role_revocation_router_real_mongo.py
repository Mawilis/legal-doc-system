"""
Real-Mongo authenticated HTTP certificate for ordinary authorization-role revocation.

VERSION:
v1.0.0-P1-R3D-B2-AUTHENTICATED-REAL-MONGO-HTTP-CERT

CERTIFICATION BOUNDARY:
A test-only FastAPI application mounts the production unmodified revocation
router. Authentication identity alone is overridden. X-Tenant-ID, production
RequireTenantAuthorization, real principal/membership/business-role/
authorization-role repositories, API-owned Mongo transaction lifecycle, the
unchanged certified revocation command, authorization evidence, role CAS, and
revocation evidence all execute against one UUID-isolated real Mongo database.

No production server mount is exercised or modified by this certificate.

FINANCIAL EXECUTION AUTHORITY:
None. Kennel EOS remains exclusive.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
import sys
from typing import Any, Iterator
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.api.authorization_role_revocation_router as subject
import tools.eos.api.tenant_authorization_http as authorization_http
import tools.eos.auth.authentication as authentication
import tools.eos.auth.tenant_access as tenant_access

from tools.eos.auth.authorization_role_revocation_evidence_registry import (
    COLLECTION as REVOCATION_COLLECTION,
    AuthorizationRoleRevocationEvidenceRegistry,
)
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
)
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    COLLECTION as AUTHORIZATION_COLLECTION,
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
    RoleAssignmentRepositoryError,
)
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)


VERSION = (
    "v1.0.0-P1-R3D-B2-"
    "AUTHENTICATED-REAL-MONGO-HTTP-CERT"
)

DEFAULT_URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)

EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

DATABASE_PREFIX = "wilsy_iam_p1_r3d_b2_"

ROUTE = (
    "/api/tenants/"
    "role-assignments/revocations"
)

NOW = datetime(
    2026,
    10,
    14,
    tzinfo=timezone.utc,
)


class _PrincipalReader:
    """Exact collection-bound current-principal reader precedent."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        *,
        session: Any = None,
    ) -> Any:
        return PrincipalAuthorityRepository.get(
            principal_id,
            self.collection,
            session=session,
        )


class _MembershipReader:
    """Exact collection-bound membership reader precedent."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> Any:
        return TenantMembershipRepository.resolve(
            principal_id,
            tenant_id,
            self.collection,
            session=session,
        )


class _RoleReader:
    """Exact split business-role / authorization-role HTTP reader precedent."""

    def __init__(
        self,
        authorization_collection: Any,
        business_collection: Any,
    ) -> None:
        self.authorization_collection = (
            authorization_collection
        )
        self.business_collection = (
            business_collection
        )

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> Any:
        if role_id in TENANT_ROLES:
            try:
                value = (
                    TenantBusinessRoleRepository.resolve(
                        principal_id,
                        tenant_id,
                        self.business_collection,
                        session=session,
                    )
                )
            except (
                TenantBusinessRoleNotFoundError
            ) as error:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                ) from error
            except (
                TenantBusinessRoleRepositoryError
            ) as error:
                raise RoleAssignmentRepositoryError(
                    "TENANT_BUSINESS_ROLE_"
                    "AUTHORITY_UNAVAILABLE"
                ) from error

            if value.business_role != role_id:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                )

            return value

        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            self.authorization_collection,
            session=session,
        )


def _identity(
    principal_id: str,
    tenant_id: str,
) -> SovereignIdentity:
    """Inject authentication identity only; never inject authorization."""

    return SovereignIdentity(
        identity_id=principal_id,
        tenant_id=tenant_id,
        username=principal_id,
        email=f"{principal_id}@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


@dataclass(frozen=True)
class _Fixture:
    tenant: str
    actor: str
    target: str


@pytest.fixture()
def mongo_context(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[dict[str, Any]]:
    """Yield one verified UUID-isolated majority/journaled Mongo database."""

    client = MongoClient(
        os.getenv(
            "TEST_VENDOR_MONGO_URI",
            DEFAULT_URI,
        ),
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
    )

    database: Any = None

    try:
        try:
            hello = client.admin.command(
                "hello"
            )
        except PyMongoError as error:
            pytest.fail(
                "P1_R3D_B2_MONGO_UNAVAILABLE:"
                f"{type(error).__name__}:{error}"
            )

        if (
            hello.get("setName")
            != EXPECTED_REPLICA_SET
        ):
            pytest.fail(
                "P1_R3D_B2_REPLICA_SET_MISMATCH:"
                f"{hello.get('setName')!r}"
            )

        if (
            hello.get(
                "isWritablePrimary",
                hello.get("ismaster"),
            )
            is not True
        ):
            pytest.fail(
                "P1_R3D_B2_WRITABLE_PRIMARY_UNAVAILABLE"
            )

        database = client.get_database(
            DATABASE_PREFIX
            + uuid.uuid4().hex,
            read_concern=ReadConcern(
                "majority"
            ),
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
        )

        collections = {
            "principal": database.get_collection(
                "principal_authorities"
            ),
            "membership": database.get_collection(
                "tenant_memberships"
            ),
            "business": database.get_collection(
                "tenant_business_roles"
            ),
            "role": database.get_collection(
                "role_assignments"
            ),
            "authorization": database.get_collection(
                AUTHORIZATION_COLLECTION
            ),
            "revocation": database.get_collection(
                REVOCATION_COLLECTION
            ),
        }

        PrincipalAuthorityRepository.ensure_indexes(
            collections["principal"]
        )
        TenantMembershipRepository.ensure_indexes(
            collections["membership"]
        )
        TenantBusinessRoleRepository.ensure_indexes(
            collections["business"]
        )
        RoleAssignmentRepository.ensure_indexes(
            collections["role"]
        )

        principal_reader = _PrincipalReader(
            collections["principal"]
        )
        membership_reader = _MembershipReader(
            collections["membership"]
        )
        role_reader = _RoleReader(
            collections["role"],
            collections["business"],
        )

        authorization_registry = (
            TenantAuthorizationDecisionEvidenceRegistry(
                collections["authorization"],
                principal_repository=principal_reader,
                membership_repository=membership_reader,
                role_assignment_repository=role_reader,
                business_role_repository=role_reader,
            )
        )
        authorization_registry.ensure_indexes()

        revocation_registry = (
            AuthorizationRoleRevocationEvidenceRegistry(
                collections["revocation"]
            )
        )
        revocation_registry.ensure_indexes()

        monkeypatch.setattr(
            subject,
            "get_client",
            lambda: client,
        )
        monkeypatch.setattr(
            subject,
            "get_database",
            lambda: database,
        )

        yield {
            "client": client,
            "database": database,
            "collections": collections,
        }

    finally:
        active_error = (
            sys.exc_info()[0] is not None
        )

        try:
            if database is not None:
                try:
                    client.drop_database(
                        database.name
                    )
                except PyMongoError:
                    if not active_error:
                        raise
        finally:
            client.close()


def _app(
    context: dict[str, Any],
    *,
    principal_id: str,
    identity_tenant: str,
) -> FastAPI:
    """Compose production authorization around the unmounted production router."""

    collections = context["collections"]

    app = FastAPI()

    register_error_handlers(
        app,
        debug=False,
    )

    app.dependency_overrides[
        authorization_http.get_current_identity
    ] = lambda: _identity(
        principal_id,
        identity_tenant,
    )

    app.dependency_overrides[
        authentication.get_principal_authority_repository
    ] = lambda: _PrincipalReader(
        collections["principal"]
    )

    app.dependency_overrides[
        tenant_access.get_tenant_membership_repository
    ] = lambda: _MembershipReader(
        collections["membership"]
    )

    app.dependency_overrides[
        authorization_http.get_role_assignment_repository
    ] = lambda: _RoleReader(
        collections["role"],
        collections["business"],
    )

    # Never bypass the permission/operation dependency itself.
    assert (
        subject._WRITE
        not in app.dependency_overrides
    )

    app.include_router(
        subject.router,
        prefix="/api",
    )

    return app


def _seed(
    context: dict[str, Any],
    *,
    target_role: str = "AUDITOR",
    target_status: RoleAssignmentStatus = (
        RoleAssignmentStatus.ACTIVE
    ),
    target_revision: int = 0,
    include_target: bool = True,
    actor_role_status: RoleAssignmentStatus = (
        RoleAssignmentStatus.ACTIVE
    ),
    actor_business_role: str = "tenant_admin",
) -> _Fixture:
    suffix = uuid.uuid4().hex

    fixture = _Fixture(
        tenant=f"tenant-p1-r3d-b2-{suffix}",
        actor=f"actor-p1-r3d-b2-{suffix}",
        target=f"target-p1-r3d-b2-{suffix}",
    )

    collections = context["collections"]

    PrincipalAuthorityRepository.create(
        PrincipalAuthority(
            fixture.actor,
            PrincipalStatus.ACTIVE,
            0,
        ),
        collections["principal"],
    )

    PrincipalAuthorityRepository.create(
        PrincipalAuthority(
            fixture.target,
            PrincipalStatus.ACTIVE,
            0,
        ),
        collections["principal"],
    )

    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            fixture.actor,
            fixture.tenant,
            TenantMembershipStatus.ACTIVE,
            0,
        ),
        collections["membership"],
    )

    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            fixture.actor,
            fixture.tenant,
            actor_business_role,
            TenantBusinessRoleStatus.ACTIVE,
            0,
            NOW,
            None,
        ),
        collections["business"],
    )

    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            fixture.actor,
            fixture.tenant,
            "ENTERPRISE_ADMIN",
            actor_role_status,
            0,
        ),
        collections["role"],
    )

    if include_target:
        RoleAssignmentRepository.insert(
            RoleAssignmentAuthority(
                fixture.target,
                fixture.tenant,
                target_role,
                target_status,
                target_revision,
            ),
            collections["role"],
        )

    return fixture


def _payload(
    fixture: _Fixture,
    *,
    target_role: str = "AUDITOR",
    expected_revision: int = 0,
    reason: str = "case:P1-R3D-B2",
    idempotency_key: str = "idem:P1-R3D-B2",
) -> dict[str, Any]:
    return {
        "target_principal_id": (
            fixture.target
        ),
        "target_role_id": target_role,
        "expected_target_assignment_revision": (
            expected_revision
        ),
        "reason_reference": reason,
        "idempotency_key": (
            idempotency_key
        ),
    }


def _post(
    context: dict[str, Any],
    fixture: _Fixture,
    payload: dict[str, Any],
    *,
    tenant: str | None = None,
    principal_id: str | None = None,
) -> Any:
    """Issue one actual HTTP POST through FastAPI and production dependencies."""

    with TestClient(
        _app(
            context,
            principal_id=(
                principal_id
                or fixture.actor
            ),
            identity_tenant=fixture.tenant,
        )
    ) as client:
        return client.post(
            ROUTE,
            headers={
                "X-Tenant-ID": (
                    tenant
                    or fixture.tenant
                )
            },
            json=payload,
        )


def _counts(
    context: dict[str, Any],
) -> tuple[int, int]:
    collections = context["collections"]

    return (
        collections[
            "authorization"
        ].count_documents({}),
        collections[
            "revocation"
        ].count_documents({}),
    )


def _target(
    context: dict[str, Any],
    fixture: _Fixture,
    role: str = "AUDITOR",
) -> RoleAssignmentAuthority:
    return RoleAssignmentRepository.resolve(
        fixture.target,
        fixture.tenant,
        role,
        context["collections"]["role"],
    )


def test_real_http_commit_exact_replay_and_divergence(
    mongo_context: dict[str, Any],
) -> None:
    context = mongo_context
    fixture = _seed(context)

    body = _payload(
        fixture,
        idempotency_key=(
            "idem:commit-replay"
        ),
    )

    first = _post(
        context,
        fixture,
        body,
    )

    assert first.status_code == 200
    assert (
        first.json()["data"]["state"]
        == "NEWLY_REVOKED"
    )

    assert _counts(context) == (1, 1)

    assert (
        _target(
            context,
            fixture,
        ).status
        is RoleAssignmentStatus.REVOKED
    )

    authorization_row = context[
        "collections"
    ]["authorization"].find_one({})

    revocation_row = context[
        "collections"
    ]["revocation"].find_one({})

    assert authorization_row is not None
    assert revocation_row is not None

    assert (
        revocation_row["tenant_id"]
        == fixture.tenant
    )
    assert (
        revocation_row[
            "actor_principal_id"
        ]
        == fixture.actor
    )

    replay = _post(
        context,
        fixture,
        body,
    )

    assert replay.status_code == 200
    assert (
        replay.json()["data"]["state"]
        == "EXACT_REPLAY"
    )
    assert _counts(context) == (1, 1)

    divergent = dict(body)
    divergent[
        "reason_reference"
    ] = "case:DIVERGENT"

    conflict = _post(
        context,
        fixture,
        divergent,
    )

    assert conflict.status_code == 409
    assert (
        conflict.json()["detail"]
        == "AUTHORIZATION_ROLE_REVOCATION_REPLAY_CONFLICT"
    )

    assert _counts(context) == (1, 1)


def test_real_http_current_authorization_denial_is_zero_write(
    mongo_context: dict[str, Any],
) -> None:
    context = mongo_context

    fixture = _seed(
        context,
        actor_role_status=(
            RoleAssignmentStatus.REVOKED
        ),
    )

    response = _post(
        context,
        fixture,
        _payload(
            fixture,
            idempotency_key="idem:auth-denied",
        ),
    )

    assert response.status_code == 403
    assert _counts(context) == (0, 0)

    assert (
        _target(
            context,
            fixture,
        ).status
        is RoleAssignmentStatus.ACTIVE
    )


@pytest.mark.parametrize(
    ("variant", "expected_status"),
    (
        ("missing", 404),
        ("stale", 409),
    ),
)
def test_real_http_target_validation_is_zero_write(
    mongo_context: dict[str, Any],
    variant: str,
    expected_status: int,
) -> None:
    context = mongo_context

    fixture = _seed(
        context,
        include_target=(
            variant != "missing"
        ),
    )

    response = _post(
        context,
        fixture,
        _payload(
            fixture,
            expected_revision=(
                1
                if variant == "stale"
                else 0
            ),
            idempotency_key=(
                f"idem:target:{variant}"
            ),
        ),
    )

    assert (
        response.status_code
        == expected_status
    )

    assert _counts(context) == (0, 0)

    if variant == "stale":
        assert (
            _target(
                context,
                fixture,
            ).status
            is RoleAssignmentStatus.ACTIVE
        )


@pytest.mark.parametrize(
    "role",
    (
        "ENTERPRISE_ADMIN",
        "SOVEREIGN_ARCHITECT",
    ),
)
def test_real_http_privileged_targets_remain_denied(
    mongo_context: dict[str, Any],
    role: str,
) -> None:
    context = mongo_context

    fixture = _seed(
        context,
        target_role=role,
    )

    response = _post(
        context,
        fixture,
        _payload(
            fixture,
            target_role=role,
            idempotency_key=(
                f"idem:root:{role}"
            ),
        ),
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "AUTHORIZATION_ROLE_REVOCATION_POLICY_DENIED"
    )

    assert _counts(context) == (0, 0)

    assert (
        _target(
            context,
            fixture,
            role,
        ).status
        is RoleAssignmentStatus.ACTIVE
    )


def test_real_http_foreign_tenant_denied_before_mutation(
    mongo_context: dict[str, Any],
) -> None:
    context = mongo_context
    fixture = _seed(context)

    foreign = (
        "tenant-foreign-"
        + uuid.uuid4().hex
    )

    response = _post(
        context,
        fixture,
        _payload(
            fixture,
            idempotency_key=(
                "idem:foreign-tenant"
            ),
        ),
        tenant=foreign,
    )

    assert response.status_code == 403
    assert _counts(context) == (0, 0)

    assert (
        _target(
            context,
            fixture,
        ).status
        is RoleAssignmentStatus.ACTIVE
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        (
            "actor_principal_id",
            "caller-forged-actor",
        ),
        (
            "tenant_id",
            "caller-forged-tenant",
        ),
    ),
)
def test_real_http_body_cannot_override_actor_or_tenant(
    mongo_context: dict[str, Any],
    field: str,
    value: str,
) -> None:
    context = mongo_context
    fixture = _seed(context)

    body = _payload(
        fixture,
        idempotency_key=(
            f"idem:forbidden:{field}"
        ),
    )

    body[field] = value

    response = _post(
        context,
        fixture,
        body,
    )

    assert response.status_code == 422
    assert _counts(context) == (0, 0)

    assert (
        _target(
            context,
            fixture,
        ).status
        is RoleAssignmentStatus.ACTIVE
    )


def test_real_http_business_role_denial_is_zero_write(
    mongo_context: dict[str, Any],
) -> None:
    context = mongo_context

    fixture = _seed(
        context,
        actor_business_role="tenant_auditor",
    )

    response = _post(
        context,
        fixture,
        _payload(
            fixture,
            idempotency_key=(
                "idem:business-role-denied"
            ),
        ),
    )

    assert response.status_code == 403
    assert _counts(context) == (0, 0)

    assert (
        _target(
            context,
            fixture,
        ).status
        is RoleAssignmentStatus.ACTIVE
    )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_authorization_role_revocation_router_real_mongo.py
# VERSION: v1.0.0-P1-R3D-B2-AUTHENTICATED-REAL-MONGO-HTTP-CERT
# AUTHORITY BOUNDARY: authenticated FastAPI transport plus real-Mongo host certification only; production RequireTenantAuthorization and unchanged certified revocation command retain authority
# TENANT POSTURE: identity override supplies authentication identity only; X-Tenant-ID plus real durable principal, membership, business-role, and authorization-role stores determine current tenant authority
# FAIL-CLOSED POSTURE: authorization denial, target drift, privileged target, divergent replay, foreign tenant, and forbidden caller authority produce no durable partial success
# DATABASE POSTURE: UUID-isolated majority/journaled disposable database on wilsyVendorCertRS only; exact database dropped after each test
# SERVER MOUNT POSTURE: production server mount is not required, modified, or certified by this artifact
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
