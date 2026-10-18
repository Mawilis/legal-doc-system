"""
Mounted sovereign runtime + real-Mongo HTTP certificate for ordinary
authorization-role revocation.

VERSION:
v1.0.0-P1-R3D-B4-MOUNTED-SOVEREIGN-RUNTIME-REAL-MONGO-HTTP-CERT

EPITOME:
Exercise the production route through the actual WilsyAPIServer composition
root. No test app mounts the revocation router. Authentication identity only
is overridden; X-Tenant-ID and production RequireTenantAuthorization remain
effective. Durable principal, membership, business-role, authorization-role,
authorization-evidence, CAS, and revocation-evidence state live in one
UUID-isolated real Mongo replica-set database.

FINANCIAL EXECUTION AUTHORITY:
None. Kennel EOS remains exclusive.
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
import sys
from typing import Any, Iterator
import uuid

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.api.authorization_role_revocation_router as revocation_router
import tools.eos.api.server as server_module
import tools.eos.api.tenant_authorization_http as authorization_http
import tools.eos.auth.authentication as authentication
import tools.eos.auth.tenant_access as tenant_access

from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.authorization_role_revocation_evidence_registry import (
    COLLECTION as REVOCATION_COLLECTION,
    AuthorizationRoleRevocationEvidenceRegistry,
)
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthority,
    PrincipalAuthorityRepository,
    PrincipalStatus,
)
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentAuthority,
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
    RoleAssignmentRepositoryError,
    RoleAssignmentStatus,
)
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    COLLECTION as AUTHORIZATION_COLLECTION,
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipAuthority,
    TenantMembershipRepository,
    TenantMembershipStatus,
)
from tools.eos.auth.authentication import SovereignIdentity


VERSION = (
    "v1.0.0-P1-R3D-B4-"
    "MOUNTED-SOVEREIGN-RUNTIME-REAL-MONGO-HTTP-CERT"
)

DEFAULT_URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)

EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

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
    def __init__(self, collection: Any) -> None:
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
    def __init__(self, collection: Any) -> None:
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
                value = TenantBusinessRoleRepository.resolve(
                    principal_id,
                    tenant_id,
                    self.business_collection,
                    session=session,
                )
            except TenantBusinessRoleNotFoundError as error:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                ) from error
            except TenantBusinessRoleRepositoryError as error:
                raise RoleAssignmentRepositoryError(
                    "TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE"
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
    return SovereignIdentity(
        identity_id=principal_id,
        tenant_id=tenant_id,
        username=principal_id,
        email=f"{principal_id}@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


@pytest.fixture()
def context(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[dict[str, Any]]:
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
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(
                "P1_R3D_B4_MONGO_UNAVAILABLE:"
                f"{type(error).__name__}:{error}"
            )

        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                "P1_R3D_B4_REPLICA_SET_MISMATCH:"
                f"{hello.get('setName')!r}"
            )

        if hello.get(
            "isWritablePrimary",
            hello.get("ismaster"),
        ) is not True:
            pytest.fail(
                "P1_R3D_B4_WRITABLE_PRIMARY_UNAVAILABLE"
            )

        database = client.get_database(
            "wilsy_iam_p1_r3d_b4_"
            + uuid.uuid4().hex,
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
        )

        collections = {
            "principal": database[
                "principal_authorities"
            ],
            "membership": database[
                "tenant_memberships"
            ],
            "business": database[
                "tenant_business_roles"
            ],
            "role": database[
                "role_assignments"
            ],
            "authorization": database[
                AUTHORIZATION_COLLECTION
            ],
            "revocation": database[
                REVOCATION_COLLECTION
            ],
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

        TenantAuthorizationDecisionEvidenceRegistry(
            collections["authorization"],
            principal_repository=principal_reader,
            membership_repository=membership_reader,
            role_assignment_repository=role_reader,
            business_role_repository=role_reader,
        ).ensure_indexes()

        AuthorizationRoleRevocationEvidenceRegistry(
            collections["revocation"]
        ).ensure_indexes()

        monkeypatch.setattr(
            revocation_router,
            "get_client",
            lambda: client,
        )
        monkeypatch.setattr(
            revocation_router,
            "get_database",
            lambda: database,
        )

        # Prevent the canonical server startup hook from reconnecting the
        # global kernel database during this isolated certificate. The route
        # itself still uses its production-mounted router and real Mongo.
        monkeypatch.setattr(
            server_module,
            "connect_db",
            lambda: (True, "B4_CERT_DATABASE_BOUND"),
        )
        monkeypatch.setattr(
            server_module,
            "disconnect_db",
            lambda: None,
        )
        monkeypatch.setattr(
            server_module,
            "get_client",
            lambda: client,
        )
        monkeypatch.setattr(
            server_module,
            "get_database",
            lambda: database,
        )

        monkeypatch.setenv(
            "WILSY_DUNNING_SCHEDULER_ENABLED",
            "false",
        )

        yield {
            "client": client,
            "database": database,
            "collections": collections,
        }

    finally:
        active_error = sys.exc_info()[0] is not None

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


def _seed(
    context: dict[str, Any],
) -> tuple[str, str, str]:
    suffix = uuid.uuid4().hex

    tenant = f"tenant-b4-{suffix}"
    actor = f"actor-b4-{suffix}"
    target = f"target-b4-{suffix}"

    collections = context["collections"]

    PrincipalAuthorityRepository.create(
        PrincipalAuthority(
            actor,
            PrincipalStatus.ACTIVE,
            0,
        ),
        collections["principal"],
    )

    PrincipalAuthorityRepository.create(
        PrincipalAuthority(
            target,
            PrincipalStatus.ACTIVE,
            0,
        ),
        collections["principal"],
    )

    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            actor,
            tenant,
            TenantMembershipStatus.ACTIVE,
            0,
        ),
        collections["membership"],
    )

    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            actor,
            tenant,
            "tenant_admin",
            TenantBusinessRoleStatus.ACTIVE,
            0,
            NOW,
            None,
        ),
        collections["business"],
    )

    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            actor,
            tenant,
            "ENTERPRISE_ADMIN",
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        collections["role"],
    )

    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            target,
            tenant,
            "AUDITOR",
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        collections["role"],
    )

    return tenant, actor, target


def _mounted_app(
    context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    *,
    tenant: str,
    actor: str,
) -> Any:
    collections = context["collections"]

    app = server_module.WilsyAPIServer(
        reasoning_provider_binding=None,
    ).get_app()

    app.dependency_overrides[
        authorization_http.get_current_identity
    ] = lambda: _identity(
        actor,
        tenant,
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

    assert (
        revocation_router._WRITE
        not in app.dependency_overrides
    )

    schema = app.openapi()

    assert ROUTE in schema["paths"]
    assert set(
        key.lower()
        for key in schema["paths"][ROUTE]
        if key.lower()
        in {
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "head",
            "options",
            "trace",
        }
    ) == {"post"}

    return app


def test_mounted_runtime_real_http_commit_and_exact_replay(
    context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, actor, target = _seed(
        context
    )

    app = _mounted_app(
        context,
        monkeypatch,
        tenant=tenant,
        actor=actor,
    )

    body = {
        "target_principal_id": target,
        "target_role_id": "AUDITOR",
        "expected_target_assignment_revision": 0,
        "reason_reference": "case:P1-R3D-B4",
        "idempotency_key": "idem:P1-R3D-B4",
    }

    with TestClient(app) as client:
        first = client.post(
            ROUTE,
            headers={
                "X-Tenant-ID": tenant,
            },
            json=body,
        )

        assert first.status_code == 200
        assert (
            first.json()["data"]["state"]
            == "NEWLY_REVOKED"
        )

        replay = client.post(
            ROUTE,
            headers={
                "X-Tenant-ID": tenant,
            },
            json=body,
        )

        assert replay.status_code == 200
        assert (
            replay.json()["data"]["state"]
            == "EXACT_REPLAY"
        )

    collections = context["collections"]

    assert (
        collections["authorization"]
        .count_documents({})
        == 1
    )

    assert (
        collections["revocation"]
        .count_documents({})
        == 1
    )

    resulting = RoleAssignmentRepository.resolve(
        target,
        tenant,
        "AUDITOR",
        collections["role"],
    )

    assert (
        resulting.status
        is RoleAssignmentStatus.REVOKED
    )

    assert resulting.revision == 1


def test_mounted_runtime_foreign_tenant_denied_zero_write(
    context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, actor, target = _seed(
        context
    )

    app = _mounted_app(
        context,
        monkeypatch,
        tenant=tenant,
        actor=actor,
    )

    body = {
        "target_principal_id": target,
        "target_role_id": "AUDITOR",
        "expected_target_assignment_revision": 0,
        "reason_reference": "case:P1-R3D-B4-FOREIGN",
        "idempotency_key": "idem:P1-R3D-B4-FOREIGN",
    }

    foreign = (
        "tenant-foreign-"
        + uuid.uuid4().hex
    )

    with TestClient(app) as client:
        response = client.post(
            ROUTE,
            headers={
                "X-Tenant-ID": foreign,
            },
            json=body,
        )

    assert response.status_code == 403

    collections = context["collections"]

    assert (
        collections["authorization"]
        .count_documents({})
        == 0
    )

    assert (
        collections["revocation"]
        .count_documents({})
        == 0
    )

    resulting = RoleAssignmentRepository.resolve(
        target,
        tenant,
        "AUDITOR",
        collections["role"],
    )

    assert (
        resulting.status
        is RoleAssignmentStatus.ACTIVE
    )


def test_mounted_runtime_body_authority_override_rejected(
    context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, actor, target = _seed(
        context
    )

    app = _mounted_app(
        context,
        monkeypatch,
        tenant=tenant,
        actor=actor,
    )

    body = {
        "target_principal_id": target,
        "target_role_id": "AUDITOR",
        "expected_target_assignment_revision": 0,
        "reason_reference": "case:P1-R3D-B4-FORGED",
        "idempotency_key": "idem:P1-R3D-B4-FORGED",
        "actor_principal_id": "forged-actor",
        "tenant_id": "forged-tenant",
    }

    with TestClient(app) as client:
        response = client.post(
            ROUTE,
            headers={
                "X-Tenant-ID": tenant,
            },
            json=body,
        )

    assert response.status_code == 422

    collections = context["collections"]

    assert (
        collections["authorization"]
        .count_documents({})
        == 0
    )
    assert (
        collections["revocation"]
        .count_documents({})
        == 0
    )

    resulting = RoleAssignmentRepository.resolve(
        target,
        tenant,
        "AUDITOR",
        collections["role"],
    )

    assert (
        resulting.status
        is RoleAssignmentStatus.ACTIVE
    )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_authorization_role_revocation_mounted_runtime_real_mongo.py
# VERSION: v1.0.0-P1-R3D-B4-MOUNTED-SOVEREIGN-RUNTIME-REAL-MONGO-HTTP-CERT
# AUTHORITY BOUNDARY: actual WilsyAPIServer mounted HTTP composition plus real-Mongo transport certification only; production RequireTenantAuthorization and certified revocation command remain authority
# TENANT POSTURE: authentication identity only is overridden; X-Tenant-ID and real durable principal, membership, business-role, and authorization-role stores determine current authority
# FAIL-CLOSED POSTURE: foreign tenant and caller-forged actor/tenant body authority produce zero revocation writes
# DATABASE POSTURE: UUID-isolated majority/journaled disposable wilsyVendorCertRS database
# SERVER POSTURE: route is consumed only from the already-mounted canonical WilsyAPIServer; this certificate performs no include_router call
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
