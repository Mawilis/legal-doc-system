"""Live-IAM real-Mongo certificate for sheriff deputy-binding commands.

TITLE: WILSY OS Deputy Principal Binding HTTP Live-IAM Real-Mongo Certificate
VERSION: v1.0.2-L8-6B-DEPUTY-PRINCIPAL-BINDING-HTTP-RM-CERT
AUTHORITY: Host-backed certification of actor IAM + target L8-6B composition.
EPITOME: Prove an independently authorized SHERIFF actor may invoke the binding
         command while the target principal must separately satisfy ACTIVE
         principal, membership, tenant_deputy business role, DEPUTY assignment,
         and canonical Deputy truth before one immutable binding is committed.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_deputy_principal_binding_http_real_mongo.py
COLLABORATION / OWNERSHIP: Host HTTP certificate only. Tenant authorization owns
                            actor admission; L8-6B owns target identity proof.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.2-L8-6B-DEPUTY-PRINCIPAL-BINDING-HTTP-RM-CERT
           rebinds the live-IAM HTTP certificate to production v1.4.1 after
           sovereign authority-declaration alignment; runtime evidence is unchanged.
           2026-09-23 v1.0.1-L8-6B-DEPUTY-PRINCIPAL-BINDING-HTTP-RM-CERT
           scopes the command-router DB-handle patch to each pytest test via
           MonkeyPatch so no dropped fixture database can leak across tests.
           2026-09-23 v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-HTTP-RM-CERT
           establishes sheriff actor allow, deputy actor denial, valid target
           commit/replay, wrong-target-role denial, foreign Deputy absence,
           exact tenant scope, and non-authorizing response evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic actors/targets/deputies.
TENANT BOUNDARY: Actor authorization, target authorities, Deputy and binding all
                 resolve under the exact request tenant; foreign evidence denies.
AUTHORITY BOUNDARY: HTTP host certificate only; binding does not grant access.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Real command API owns session start/commit/abort.
FAIL-CLOSED DECLARATION: Actor IAM, target IAM, Deputy scope, conflict, runtime,
                         or persistence failure denies without identity fiction.
"""
from __future__ import annotations

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

import tools.eos.api.legal_operations_command_router as command_api
import tools.eos.api.tenant_authorization_http as authorization_http
import tools.eos.auth.authentication as authentication
import tools.eos.auth.tenant_access as tenant_access
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
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
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.domain.legal_operations_lifecycle import Deputy
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    COLLECTION as BINDING_COLLECTION,
    DeputyPrincipalBindingRegistry,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.2-L8-6B-DEPUTY-PRINCIPAL-BINDING-HTTP-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 23, 18, 0, tzinfo=timezone.utc)


class _PrincipalReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, *, session: Any = None) -> Any:
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
    """Resolve actor business/granting roles through canonical split stores."""

    def __init__(
        self,
        authorization_collection: Any,
        business_collection: Any,
    ) -> None:
        self.authorization_collection = authorization_collection
        self.business_collection = business_collection

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


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield a verified isolated majority/journaled command database."""
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        retryWrites=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(
                f"L8_6B_HTTP_MONGO_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_6B_HTTP_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_6B_HTTP_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client.get_database(
            f"l8_6b_http_{uuid.uuid4().hex}",
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        collections = {
            "lifecycle": database.get_collection(LIFECYCLE_COLLECTION),
            "binding": database.get_collection(BINDING_COLLECTION),
            "principal": database.get_collection("principal_authorities"),
            "membership": database.get_collection("tenant_memberships"),
            "business": database.get_collection("tenant_business_roles"),
            "role": database.get_collection("role_assignments"),
        }
        LegalOperationsLifecycleRegistry.ensure_indexes(collections["lifecycle"])
        DeputyPrincipalBindingRegistry.ensure_indexes(collections["binding"])
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        TenantBusinessRoleRepository.ensure_indexes(collections["business"])
        RoleAssignmentRepository.ensure_indexes(collections["role"])
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
                    client.drop_database(database.name)
                except PyMongoError:
                    if not active_error:
                        raise
        finally:
            client.close()


def _seed_principal(
    collections: dict[str, Any],
    *,
    principal_id: str,
    tenant_id: str,
    business_role: str,
    authorization_role: str,
) -> None:
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0),
        collections["principal"],
    )
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal_id,
            tenant_id,
            TenantMembershipStatus.ACTIVE,
            0,
        ),
        collections["membership"],
    )
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            principal_id,
            tenant_id,
            business_role,
            TenantBusinessRoleStatus.ACTIVE,
            0,
            NOW,
            None,
        ),
        collections["business"],
    )
    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            principal_id,
            tenant_id,
            authorization_role,
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        collections["role"],
    )


def _seed_deputy(
    collections: dict[str, Any],
    *,
    tenant_id: str,
    deputy_id: str,
) -> Deputy:
    value = Deputy(
        tenant_id=tenant_id,
        deputy_id=deputy_id,
        sheriff_office_id="office-1",
        display_name="Deputy One",
        badge_reference="badge-1",
        evidence_reference="directory-deputy",
    )
    LegalOperationsLifecycleRegistry.create(value, collections["lifecycle"])
    return value


def _identity(principal_id: str, tenant_id: str) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=principal_id,
        tenant_id=tenant_id,
        username=principal_id,
        email=f"{principal_id}@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


def _app(
    context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    *,
    actor_principal: str,
    tenant_id: str,
) -> FastAPI:
    """Mount real directory authorization and real API-owned transaction."""
    app = FastAPI()
    register_error_handlers(app, debug=False)
    collections = context["collections"]

    app.dependency_overrides[authorization_http.get_current_identity] = (
        lambda: _identity(actor_principal, tenant_id)
    )
    app.dependency_overrides[
        authentication.get_principal_authority_repository
    ] = lambda: _PrincipalReader(collections["principal"])
    app.dependency_overrides[
        tenant_access.get_tenant_membership_repository
    ] = lambda: _MembershipReader(collections["membership"])
    app.dependency_overrides[
        authorization_http.get_role_assignment_repository
    ] = lambda: _RoleReader(
        collections["role"],
        collections["business"],
    )

    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (context["client"], context["database"]),
    )
    assert command_api._DIRECTORY not in app.dependency_overrides
    app.include_router(command_api.router, prefix="/api")
    return app


def _request(
    context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    *,
    actor_principal: str,
    tenant_id: str,
    target_principal: str,
    deputy_id: str,
) -> Any:
    with TestClient(
        _app(
            context,
            monkeypatch,
            actor_principal=actor_principal,
            tenant_id=tenant_id,
        )
    ) as client:
        return client.post(
            "/api/legal-operations/directory/deputy-principal-bindings",
            headers={"X-Tenant-ID": tenant_id},
            json={
                "principal_id": target_principal,
                "deputy_id": deputy_id,
                "bound_at": NOW.isoformat(),
                "evidence_reference": "sheriff-binding-evidence",
            },
        )


def test_real_sheriff_actor_binds_valid_deputy_target_and_exact_replays(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sheriff actor authority and target deputy authority remain independent."""
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    sheriff = f"sheriff-{uuid.uuid4().hex}"
    target = f"principal-{uuid.uuid4().hex}"
    deputy_id = f"deputy-{uuid.uuid4().hex}"
    source = _seed_deputy(collections, tenant_id=tenant, deputy_id=deputy_id)
    _seed_principal(
        collections,
        principal_id=sheriff,
        tenant_id=tenant,
        business_role="tenant_sheriff",
        authorization_role="SHERIFF",
    )
    _seed_principal(
        collections,
        principal_id=target,
        tenant_id=tenant,
        business_role="tenant_deputy",
        authorization_role="DEPUTY",
    )

    first = _request(
        mongo_context,
        monkeypatch,
        actor_principal=sheriff,
        tenant_id=tenant,
        target_principal=target,
        deputy_id=deputy_id,
    )
    replay = _request(
        mongo_context,
        monkeypatch,
        actor_principal=sheriff,
        tenant_id=tenant,
        target_principal=target,
        deputy_id=deputy_id,
    )

    assert first.status_code == 200
    assert replay.status_code == 200
    assert first.json() == replay.json()
    assert first.json()["tenant_id"] == tenant
    assert first.json()["principal_id"] == target
    assert first.json()["deputy_id"] == deputy_id
    assert first.json()["deputy_fingerprint"] == source.fingerprint
    assert collections["binding"].count_documents(
        {"tenant_id": tenant, "principal_id": target}
    ) == 1


def test_real_deputy_actor_cannot_create_bindings(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Target-style DEPUTY authority never substitutes for sheriff directory IAM."""
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    deputy_actor = f"principal-{uuid.uuid4().hex}"
    deputy_id = f"deputy-{uuid.uuid4().hex}"
    _seed_deputy(collections, tenant_id=tenant, deputy_id=deputy_id)
    _seed_principal(
        collections,
        principal_id=deputy_actor,
        tenant_id=tenant,
        business_role="tenant_deputy",
        authorization_role="DEPUTY",
    )

    response = _request(
        mongo_context,
        monkeypatch,
        actor_principal=deputy_actor,
        tenant_id=tenant,
        target_principal=deputy_actor,
        deputy_id=deputy_id,
    )

    assert response.status_code == 403
    assert collections["binding"].count_documents({}) == 0


def test_real_sheriff_cannot_bind_target_without_deputy_current_authority(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sheriff actor admission cannot manufacture target DEPUTY identity authority."""
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    sheriff = f"sheriff-{uuid.uuid4().hex}"
    target = f"principal-{uuid.uuid4().hex}"
    deputy_id = f"deputy-{uuid.uuid4().hex}"
    _seed_deputy(collections, tenant_id=tenant, deputy_id=deputy_id)
    _seed_principal(
        collections,
        principal_id=sheriff,
        tenant_id=tenant,
        business_role="tenant_sheriff",
        authorization_role="SHERIFF",
    )
    _seed_principal(
        collections,
        principal_id=target,
        tenant_id=tenant,
        business_role="tenant_legal_partner",
        authorization_role="LEGAL_PARTNER",
    )

    response = _request(
        mongo_context,
        monkeypatch,
        actor_principal=sheriff,
        tenant_id=tenant,
        target_principal=target,
        deputy_id=deputy_id,
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "LEGAL_OPERATIONS_COMMAND_INVALID"
    assert collections["binding"].count_documents({}) == 0


def test_real_foreign_deputy_is_bounded_absence_and_response_has_no_grant_truth(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Foreign Deputy cannot bind; valid response contains identity evidence only."""
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    foreign = f"tenant-{uuid.uuid4().hex}"
    sheriff = f"sheriff-{uuid.uuid4().hex}"
    target = f"principal-{uuid.uuid4().hex}"
    foreign_deputy = f"deputy-{uuid.uuid4().hex}"
    _seed_deputy(
        collections,
        tenant_id=foreign,
        deputy_id=foreign_deputy,
    )
    _seed_principal(
        collections,
        principal_id=sheriff,
        tenant_id=tenant,
        business_role="tenant_sheriff",
        authorization_role="SHERIFF",
    )
    _seed_principal(
        collections,
        principal_id=target,
        tenant_id=tenant,
        business_role="tenant_deputy",
        authorization_role="DEPUTY",
    )

    foreign_response = _request(
        mongo_context,
        monkeypatch,
        actor_principal=sheriff,
        tenant_id=tenant,
        target_principal=target,
        deputy_id=foreign_deputy,
    )
    assert foreign_response.status_code == 404
    assert collections["binding"].count_documents({"tenant_id": tenant}) == 0

    local_deputy = f"deputy-{uuid.uuid4().hex}"
    _seed_deputy(collections, tenant_id=tenant, deputy_id=local_deputy)
    valid = _request(
        mongo_context,
        monkeypatch,
        actor_principal=sheriff,
        tenant_id=tenant,
        target_principal=target,
        deputy_id=local_deputy,
    )
    assert valid.status_code == 200
    keys = set(valid.json())
    for forbidden in {
        "permission",
        "role_id",
        "business_role",
        "authorized",
        "queue",
        "attempt_id",
        "invoice",
        "payment",
        "settlement",
        "bank_execution",
        "provider_execution",
    }:
        assert forbidden not in keys

    assert command_api.VERSION == (
        "v1.4.1-L8-6B-DEPUTY-PRINCIPAL-BINDING-COMMAND-API"
    )
    assert VERSION == (
        "v1.0.2-L8-6B-DEPUTY-PRINCIPAL-BINDING-HTTP-RM-CERT"
    )


# ARTIFACT: test_deputy_principal_binding_http_real_mongo.py
# VERSION: v1.0.2-L8-6B-DEPUTY-PRINCIPAL-BINDING-HTTP-RM-CERT
# AUTHORITY BOUNDARY: live-IAM real-Mongo sheriff actor + target deputy binding HTTP certificate only
# TENANT POSTURE: actor IAM, target IAM, Deputy and binding all exact-tenant scoped
# FAIL-CLOSED POSTURE: deputy actor, wrong target role, foreign Deputy, runtime/persistence failures deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
