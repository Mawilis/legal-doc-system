"""Real-Mongo authenticated certificate for the D3B1 legal matter deadline router.

TITLE: Wilsy OS Legal Matter Deadline HTTP Real-Mongo Certificate
VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D3B1-DEADLINE-HTTP-RM-CERT
AUTHORITY: Wilsy OS Core Governance / authenticated FastAPI transport evidence.
EPITOME: Prove live durable tenant authorization, API-owned transactions, D3A
         orchestration, D2 persistence, replay, bounded reads, and role denials.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_matter_deadline_http_real_mongo.py
COLLABORATION / OWNERSHIP: Certificate owns only UUID-isolated fixtures and observations.
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0-LEGAL-OPS-COMPLETION-D3B1-DEADLINE-HTTP-RM-CERT
           establishes host-backed POST/GET transport over live IAM and Mongo.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque fixtures only.
TENANT BOUNDARY: Every IAM, matter, and deadline record is exact tenant scoped.
AUTHORITY BOUNDARY: Transport evidence only; D1/D2/D3A and durable IAM remain canonical.
TRANSACTION BOUNDARY: HTTP owns one Mongo transaction and passes its active session to D3A.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Infrastructure, IAM, matter, replay, conflict, and scope drift fail.
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

import tools.eos.api.legal_matter_deadline_router as deadline_api
import tools.eos.api.tenant_authorization_http as authorization_http
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth import authentication, tenant_access
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    COLLECTION as PRINCIPAL_COLLECTION,
    PrincipalAuthorityRepository,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    COLLECTION as ROLE_COLLECTION,
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
    COLLECTION as BUSINESS_ROLE_COLLECTION,
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    COLLECTION as MEMBERSHIP_COLLECTION,
    TenantMembershipRepository,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
    LegalOperationsLifecycleRegistry,
)
from tools.eos.legal_operations.registry.legal_matter_deadline_registry import (
    COLLECTION as DEADLINE_COLLECTION,
    LegalMatterDeadlineRegistry,
)


URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
NOW = datetime(2026, 10, 11, 10, 0, tzinfo=timezone.utc)
DUE = NOW + timedelta(days=7)
FP = "a" * 128


class _PrincipalReader:
    def __init__(self, collection: Any) -> None:
        self._collection = collection

    def resolve(self, principal_id: str, *, session: Any = None) -> Any:
        return PrincipalAuthorityRepository.get(
            principal_id,
            self._collection,
            session=session,
        )


class _MembershipReader:
    def __init__(self, collection: Any) -> None:
        self._collection = collection

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
            self._collection,
            session=session,
        )


class _RoleReader:
    def __init__(self, authorization_collection: Any, business_collection: Any) -> None:
        self._authorization_collection = authorization_collection
        self._business_collection = business_collection

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
                    self._business_collection,
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
                raise RoleAssignmentNotFoundError("TENANT_BUSINESS_ROLE_NOT_FOUND")
            return value
        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            self._authorization_collection,
            session=session,
        )


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(f"D3B1_MONGO_UNAVAILABLE:{type(error).__name__}")
        assert hello.get("setName") == "wilsyVendorCertRS"
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        database = client.get_database(
            f"wilsy_deadline_d3b1_{uuid4().hex}",
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        collections = {
            "principal": database.get_collection(PRINCIPAL_COLLECTION),
            "membership": database.get_collection(MEMBERSHIP_COLLECTION),
            "roles": database.get_collection(ROLE_COLLECTION),
            "business": database.get_collection(BUSINESS_ROLE_COLLECTION),
            "matter": database.get_collection(LIFECYCLE_COLLECTION),
            "deadline": database.get_collection(DEADLINE_COLLECTION),
        }
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        RoleAssignmentRepository.ensure_indexes(collections["roles"])
        TenantBusinessRoleRepository.ensure_indexes(collections["business"])
        LegalOperationsLifecycleRegistry.ensure_indexes(collections["matter"])
        LegalMatterDeadlineRegistry.ensure_indexes(collections["deadline"])
        yield {"client": client, "database": database, "collections": collections}
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _seed_actor(
    context: dict[str, Any],
    *,
    tenant: str,
    principal: str,
    business_role: str,
    grant_role: str,
) -> None:
    collections = context["collections"]
    with context["client"].start_session() as session:
        session.start_transaction()
        PrincipalAuthorityRepository.create(
            PrincipalAuthority(principal, PrincipalStatus.ACTIVE, 0),
            collections["principal"],
            session=session,
        )
        TenantMembershipRepository.insert(
            TenantMembershipAuthority(
                principal,
                tenant,
                TenantMembershipStatus.ACTIVE,
                0,
            ),
            collections["membership"],
            session=session,
        )
        TenantBusinessRoleRepository.insert(
            TenantBusinessRoleAuthority(
                principal,
                tenant,
                business_role,
                TenantBusinessRoleStatus.ACTIVE,
                0,
                NOW,
                None,
            ),
            collections["business"],
            session=session,
        )
        RoleAssignmentRepository.insert(
            RoleAssignmentAuthority(
                principal,
                tenant,
                grant_role,
                RoleAssignmentStatus.ACTIVE,
                0,
            ),
            collections["roles"],
            session=session,
        )
        session.commit_transaction()


def _seed_matter(context: dict[str, Any], tenant: str, matter_id: str) -> None:
    with context["client"].start_session() as session:
        session.start_transaction()
        LegalOperationsLifecycleRegistry.create(
            CaseMatter(
                tenant_id=tenant,
                case_matter_id=matter_id,
                matter_reference=f"MAT:{matter_id}",
                opened_at=NOW,
                evidence_reference=f"matter:{matter_id}",
            ),
            context["collections"]["matter"],
            session=session,
        )
        session.commit_transaction()


def _identity(principal: str, tenant: str) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=principal,
        tenant_id=tenant,
        username="deadline-operator",
        email="deadline-operator@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


def _client(
    context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    *,
    tenant: str,
    principal: str,
) -> TestClient:
    collections = context["collections"]
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.dependency_overrides[authorization_http.get_current_identity] = (
        lambda: _identity(principal, tenant)
    )
    app.dependency_overrides[
        authentication.get_principal_authority_repository
    ] = lambda: _PrincipalReader(collections["principal"])
    app.dependency_overrides[
        tenant_access.get_tenant_membership_repository
    ] = lambda: _MembershipReader(collections["membership"])
    app.dependency_overrides[
        authorization_http.get_role_assignment_repository
    ] = lambda: _RoleReader(collections["roles"], collections["business"])
    app.include_router(deadline_api.router, prefix="/api")
    monkeypatch.setattr(
        deadline_api,
        "_db_handles",
        lambda: (context["client"], context["database"]),
    )
    return TestClient(app)


def _payload(*, title: str = "Evidenced deadline") -> dict[str, object]:
    return {
        "deadline_id": "deadline-1",
        "deadline_kind": "FILING",
        "title": title,
        "due_at": DUE.isoformat(),
        "source_type": "COURT_ORDER",
        "source_reference": "evidence://court-order/1",
        "source_evidence_fingerprint": FP,
        "jurisdiction_reference": "jurisdiction://court/example",
        "created_at": NOW.isoformat(),
        "status": "ACTIVE",
    }


def test_real_partner_post_get_list_replay_conflict_and_cross_tenant_absence(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, principal, matter = "tenant-a", "principal-a", "matter-1"
    _seed_actor(
        mongo_context,
        tenant=tenant,
        principal=principal,
        business_role="tenant_legal_partner",
        grant_role="LEGAL_PARTNER",
    )
    _seed_matter(mongo_context, tenant, matter)
    client = _client(
        mongo_context,
        monkeypatch,
        tenant=tenant,
        principal=principal,
    )
    headers = {"X-Tenant-ID": tenant}
    route = f"/api/legal-operations/matters/{matter}/deadlines"

    first = client.post(route, json=_payload(), headers=headers)
    replay = client.post(route, json=_payload(), headers=headers)
    divergent = client.post(
        route,
        json=_payload(title="Divergent"),
        headers=headers,
    )
    detail = client.get(f"{route}/deadline-1", headers=headers)
    listing = client.get(route, headers=headers)

    assert first.status_code == 200, first.text
    assert replay.status_code == 200, replay.text
    assert replay.json() == first.json()
    assert divergent.status_code == 409, divergent.text
    assert detail.status_code == 200, detail.text
    assert listing.status_code == 200, listing.text
    assert detail.json()["data"]["deadline_id"] == "deadline-1"
    assert listing.json()["data"] == [detail.json()["data"]]
    deadlines = mongo_context["collections"]["deadline"]
    assert deadlines.count_documents({"tenant_id": tenant}) == 1

    foreign_client = _client(
        mongo_context,
        monkeypatch,
        tenant="tenant-foreign",
        principal=principal,
    )
    denied = foreign_client.get(
        f"/api/legal-operations/matters/{matter}/deadlines/deadline-1",
        headers={"X-Tenant-ID": "tenant-foreign"},
    )
    assert denied.status_code == 403
    assert deadlines.count_documents({"tenant_id": tenant}) == 1


def test_real_secretary_reads_but_write_denies(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant, matter = "tenant-secretary", "matter-1"
    partner = "principal-partner"
    secretary = "principal-secretary"
    _seed_actor(
        mongo_context,
        tenant=tenant,
        principal=partner,
        business_role="tenant_legal_partner",
        grant_role="LEGAL_PARTNER",
    )
    _seed_matter(mongo_context, tenant, matter)
    partner_client = _client(
        mongo_context,
        monkeypatch,
        tenant=tenant,
        principal=partner,
    )
    headers = {"X-Tenant-ID": tenant}
    created = partner_client.post(
        f"/api/legal-operations/matters/{matter}/deadlines",
        json=_payload(),
        headers=headers,
    )
    assert created.status_code == 200, created.text

    _seed_actor(
        mongo_context,
        tenant=tenant,
        principal=secretary,
        business_role="tenant_legal_secretary",
        grant_role="LEGAL_SECRETARY",
    )
    secretary_client = _client(
        mongo_context,
        monkeypatch,
        tenant=tenant,
        principal=secretary,
    )
    read = secretary_client.get(
        f"/api/legal-operations/matters/{matter}/deadlines/deadline-1",
        headers=headers,
    )
    write = secretary_client.post(
        f"/api/legal-operations/matters/{matter}/deadlines",
        json={**_payload(), "deadline_id": "deadline-secretary"},
        headers=headers,
    )
    assert read.status_code == 200, read.text
    assert write.status_code == 403
    assert mongo_context["collections"]["deadline"].count_documents(
        {"tenant_id": tenant, "deadline_id": "deadline-secretary"}
    ) == 0


# ARTIFACT: test_legal_matter_deadline_http_real_mongo.py
# VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D3B1-DEADLINE-HTTP-RM-CERT
# AUTHORITY BOUNDARY: authenticated host-backed HTTP evidence only; D1/D2/D3A/IAM remain canonical
# TENANT POSTURE: UUID-isolated database and exact tenant predicates
# FAIL-CLOSED POSTURE: IAM denial, replay divergence, foreign scope, and persistence drift reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
