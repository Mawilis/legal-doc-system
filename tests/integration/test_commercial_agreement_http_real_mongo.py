"""Authenticated real-Mongo HTTP certificate for commercial agreements.

The test exercises FastAPI routing, durable IAM repositories, tenant scope,
the agreement router's transaction boundary and real replica-set persistence.
Only synthetic tenants and contract metadata are used.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.api.commercial_agreement_router as agreement_api
import tools.eos.api.tenant_authorization_http as authorization_http
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth import authentication, tenant_access
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.saas.entitlement.commercial_agreement_registry import (
    CURRENT_COLLECTION,
    HISTORY_COLLECTION,
)

URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 11, 6, 12, 0, tzinfo=timezone.utc)


class _PrincipalReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, *, session: Any = None) -> Any:
        return PrincipalAuthorityRepository.get(principal_id, self.collection, session=session)


class _MembershipReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, tenant_id: str, *, session: Any = None) -> Any:
        return TenantMembershipRepository.resolve(principal_id, tenant_id, self.collection, session=session)


class _RoleReader:
    def __init__(self, role_collection: Any, business_collection: Any) -> None:
        self.role_collection = role_collection
        self.business_collection = business_collection

    def resolve(self, principal_id: str, tenant_id: str, role_id: str, *, session: Any = None) -> Any:
        if role_id in TENANT_ROLES:
            return TenantBusinessRoleRepository.resolve(
                principal_id, tenant_id, self.business_collection, session=session
            )
        return RoleAssignmentRepository.resolve(
            principal_id, tenant_id, role_id, self.role_collection, session=session
        )


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    client: MongoClient[Any] = MongoClient(
        URI, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000,
        retryWrites=True, tz_aware=True,
    )
    database = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"host Mongo unavailable before fixture yield: {type(error).__name__}")
        if hello.get("setName") != REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("replica set has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.fail("replica set does not support logical sessions")
        database = client.get_database(
            f"ca_http_{uuid4().hex}",
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        collections = {
            "principal": database.get_collection("principal_authorities"),
            "membership": database.get_collection("tenant_memberships"),
            "roles": database.get_collection("role_assignments"),
            "business": database.get_collection("tenant_business_roles"),
        }
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        RoleAssignmentRepository.ensure_indexes(collections["roles"])
        TenantBusinessRoleRepository.ensure_indexes(collections["business"])
        yield {"client": client, "database": database, "collections": collections}
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _seed_actor(
    context: dict[str, Any], *, tenant: str, principal: str,
    business_role: str, grant_role: str,
) -> None:
    c = context["collections"]
    with context["client"].start_session() as session:
        with session.start_transaction():
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(principal, PrincipalStatus.ACTIVE, 0),
                c["principal"], session=session,
            )
            TenantMembershipRepository.insert(
                TenantMembershipAuthority(principal, tenant, TenantMembershipStatus.ACTIVE, 0),
                c["membership"], session=session,
            )
            TenantBusinessRoleRepository.insert(
                TenantBusinessRoleAuthority(
                    principal, tenant, business_role, TenantBusinessRoleStatus.ACTIVE,
                    0, NOW, None,
                ),
                c["business"], session=session,
            )
            RoleAssignmentRepository.insert(
                RoleAssignmentAuthority(principal, tenant, grant_role, RoleAssignmentStatus.ACTIVE, 0),
                c["roles"], session=session,
            )


def _identity(principal: str, tenant: str) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=principal, tenant_id=tenant, username="commercial-operator",
        email="commercial-operator@example.test", auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


def _client(context: dict[str, Any], monkeypatch: pytest.MonkeyPatch, *, tenant: str, principal: str) -> TestClient:
    c = context["collections"]
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.dependency_overrides[authorization_http.get_current_identity] = lambda: _identity(principal, tenant)
    app.dependency_overrides[authentication.get_principal_authority_repository] = lambda: _PrincipalReader(c["principal"])
    app.dependency_overrides[tenant_access.get_tenant_membership_repository] = lambda: _MembershipReader(c["membership"])
    app.dependency_overrides[authorization_http.get_role_assignment_repository] = lambda: _RoleReader(c["roles"], c["business"])
    app.include_router(agreement_api.router, prefix="/api")
    monkeypatch.setattr(agreement_api, "get_client", lambda: context["client"])
    monkeypatch.setattr(agreement_api, "get_database", lambda: context["database"])
    return TestClient(app)


def _draft_payload(agreement_id: str = "agreement-http-1") -> dict[str, object]:
    return {
        "agreement_id": agreement_id,
        "offer_id": "LEGAL_OPERATIONS_STANDALONE",
        "contract_reference": f"contract-{agreement_id}",
        "contract_version": "2026-11-01",
        "counterparty_legal_name": "Synthetic Counterparty (Pty) Ltd",
        "effective_at": NOW.isoformat(),
        "expires_at": (NOW + timedelta(days=365)).isoformat(),
        "renewal_mode": "MANUAL",
        "notice_days": 30,
        "termination_terms_reference": "terms-http-1",
    }


def test_authenticated_owner_can_create_read_and_list_durable_agreement_history(
    mongo_context: dict[str, Any], monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed_actor(mongo_context, tenant=tenant, principal=principal, business_role="tenant_owner", grant_role="ENTERPRISE_ADMIN")
    headers = {"X-Tenant-ID": tenant}
    with _client(mongo_context, monkeypatch, tenant=tenant, principal=principal) as http:
        created = http.post("/api/commercial/agreements", headers=headers, json=_draft_payload())
        assert created.status_code == 201, created.text
        body = created.json()
        assert body["outcome"] == "CREATED"
        assert body["agreement"]["tenant_id"] == tenant
        assert body["agreement"]["lifecycle_state"] == "DRAFT"
        current = http.get("/api/commercial/agreements/agreement-http-1", headers=headers)
        history = http.get("/api/commercial/agreements/agreement-http-1/history", headers=headers)
    assert current.status_code == 200, current.text
    assert history.status_code == 200, history.text
    assert current.json()["agreement"] == body["agreement"]
    assert history.json()["tenant_id"] == tenant
    assert len(history.json()["revisions"]) == 1
    assert mongo_context["database"][HISTORY_COLLECTION].count_documents({"tenant_id": tenant}) == 1
    assert mongo_context["database"][CURRENT_COLLECTION].count_documents({"tenant_id": tenant}) == 1


def test_authenticated_owner_replay_is_idempotent_and_conflict_is_rejected(
    mongo_context: dict[str, Any], monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed_actor(mongo_context, tenant=tenant, principal=principal, business_role="tenant_owner", grant_role="ENTERPRISE_ADMIN")
    headers = {"X-Tenant-ID": tenant}
    with _client(mongo_context, monkeypatch, tenant=tenant, principal=principal) as http:
        first = http.post("/api/commercial/agreements", headers=headers, json=_draft_payload())
        replay = http.post("/api/commercial/agreements", headers=headers, json=_draft_payload())
        conflict_payload = _draft_payload()
        conflict_payload["counterparty_legal_name"] = "Different Counterparty (Pty) Ltd"
        conflict = http.post("/api/commercial/agreements", headers=headers, json=conflict_payload)
    assert first.status_code == 201
    assert replay.status_code == 201
    assert replay.json()["outcome"] == "IDEMPOTENT_REPLAY"
    assert conflict.status_code == 409


def test_foreign_tenant_scope_and_legal_partner_cannot_read_owner_commercial_agreements(
    mongo_context: dict[str, Any], monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    foreign_tenant = f"tenant-{uuid4().hex}"
    _seed_actor(mongo_context, tenant=tenant, principal=principal, business_role="tenant_owner", grant_role="ENTERPRISE_ADMIN")
    headers = {"X-Tenant-ID": tenant}
    with _client(mongo_context, monkeypatch, tenant=tenant, principal=principal) as owner:
        created = owner.post("/api/commercial/agreements", headers=headers, json=_draft_payload())
        assert created.status_code == 201
    foreign_scope = {"X-Tenant-ID": foreign_tenant}
    with _client(mongo_context, monkeypatch, tenant=tenant, principal=principal) as owner:
        denied_scope = owner.get("/api/commercial/agreements/agreement-http-1", headers=foreign_scope)
    assert denied_scope.status_code == 403

    partner, partner_principal = f"tenant-{uuid4().hex}", f"principal-{uuid4().hex}"
    _seed_actor(mongo_context, tenant=partner, principal=partner_principal, business_role="tenant_legal_partner", grant_role="LEGAL_PARTNER")
    with _client(mongo_context, monkeypatch, tenant=partner, principal=partner_principal) as legal_partner:
        denied_role = legal_partner.get(
            "/api/commercial/agreements/agreement-http-1",
            headers={"X-Tenant-ID": partner},
        )
    assert denied_role.status_code == 403
