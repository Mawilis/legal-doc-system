"""Real-Mongo certificate for the LEGAL_CLIENT matter projection API.

TITLE: WILSY OS Legal Client Matter Read API Real-Mongo Certificate
VERSION: v1.0.0-L8-7D6-CLIENT-MATTER-READ-API-RM-CERT
AUTHORITY: Host-backed certification of D6 authenticated snapshot HTTP composition.
EPITOME: Prove on the verified Mongo replica set that GET
         /legal-operations/client/matters resolves durable current LEGAL_CLIENT
         IAM, opens one API-owned snapshot, composes D5 ACTIVE visibility with
         current CaseMatter truth, suppresses revoked visibility, and denies a
         revoked client assignment before snapshot projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_http_real_mongo.py
COLLABORATION / OWNERSHIP: D4 owns authorization, D5 owns safe projection,
                            canonical IAM/L8-7B/P2 own durable truth, D6 owns
                            only authenticated transport and snapshot lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-7D6-CLIENT-MATTER-READ-API-RM-CERT establishes
           live durable IAM admission, real snapshot D5 delegation, current
           OPEN/CLOSED projection, append-only visibility revocation
           suppression, revoked final-role denial before projection, and exact
           safe response shape with no internal/financial evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenant/client/matter data.
TENANT BOUNDARY: X-Tenant-ID selects scope only; durable IAM and visibility prove it.
AUTHORITY BOUNDARY: Real HTTP projection certificate only; no lifecycle mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: D6 owns one read-only snapshot transaction per successful route.
FAIL-CLOSED DECLARATION: Durable IAM denial, visibility/matter failure or Mongo
                         transaction failure cannot become client projection data.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
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

import tools.eos.api.legal_operations_router as legal_router
import tools.eos.api.tenant_authorization_http as authorization_http
import tools.eos.auth.authentication as authentication
import tools.eos.auth.tenant_access as tenant_access
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
)
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.domain.legal_client_matter_visibility_binding import (
    LegalClientMatterVisibilityBinding,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.registry.legal_client_matter_visibility_registry import (
    COLLECTION as VISIBILITY_COLLECTION,
    LegalClientMatterVisibilityRegistry,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-7D6-CLIENT-MATTER-READ-API-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 23, 22, 15, tzinfo=timezone.utc)


class _PrincipalReader:
    """Adapt canonical principal persistence to HTTP/D5 current reads."""

    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, *, session: Any = None) -> object:
        return PrincipalAuthorityRepository.get(
            principal_id,
            self.collection,
            session=session,
        )


class _MembershipReader:
    """Adapt canonical membership persistence to HTTP/D5 current reads."""

    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> object:
        return TenantMembershipRepository.resolve(
            principal_id,
            tenant_id,
            self.collection,
            session=session,
        )


class _RoleReader:
    """Route business/final role reads to their separate canonical stores."""

    def __init__(self, role_collection: Any, business_collection: Any) -> None:
        self.role_collection = role_collection
        self.business_collection = business_collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> object:
        if role_id.startswith("tenant_"):
            value = TenantBusinessRoleRepository.resolve(
                principal_id,
                tenant_id,
                self.business_collection,
                session=session,
            )
            if value.business_role != role_id:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                )
            return value
        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            self.role_collection,
            session=session,
        )


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield one verified writable isolated replica-set database."""
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
                f"L8_7D6_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_7D6_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_7D6_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client[f"legal_ops_l8_7d6_{uuid.uuid4().hex}"]
        collections = {
            "lifecycle": database.get_collection(
                LIFECYCLE_COLLECTION,
                write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            ),
            "visibility": database.get_collection(
                VISIBILITY_COLLECTION,
                write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            ),
            "principal": database.get_collection(
                "principal_authorities",
                write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            ),
            "membership": database.get_collection(
                "tenant_memberships",
                write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            ),
            "business": database.get_collection(
                "tenant_business_roles",
                write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            ),
            "role": database.get_collection(
                "role_assignments",
                write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            ),
        }
        LegalOperationsLifecycleRegistry.ensure_indexes(collections["lifecycle"])
        LegalClientMatterVisibilityRegistry.ensure_indexes(collections["visibility"])
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


def _identity(tenant: str, principal: str) -> SovereignIdentity:
    """Build the authenticated transport identity only."""
    return SovereignIdentity(
        identity_id=principal,
        tenant_id=tenant,
        username="client",
        email="client@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


def _seed_client(
    collections: dict[str, Any],
    *,
    tenant: str,
    principal: str,
    final_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
) -> None:
    """Persist current tenant_legal_client + LEGAL_CLIENT truth."""
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(principal, PrincipalStatus.ACTIVE, 0),
        collections["principal"],
    )
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal,
            tenant,
            TenantMembershipStatus.ACTIVE,
            0,
        ),
        collections["membership"],
    )
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            principal,
            tenant,
            "tenant_legal_client",
            TenantBusinessRoleStatus.ACTIVE,
            0,
            NOW,
            None,
        ),
        collections["business"],
    )
    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            principal,
            tenant,
            "LEGAL_CLIENT",
            final_status,
            0,
        ),
        collections["role"],
    )


def _matter(tenant: str, matter_id: str) -> CaseMatter:
    """Build one canonical client-visible matter."""
    return CaseMatter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_reference=f"CLIENT-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"matter-{matter_id}",
    )


def _grant(
    collections: dict[str, Any],
    *,
    principal: str,
    matter: CaseMatter,
) -> LegalClientMatterVisibilityBinding:
    """Persist one ACTIVE visibility relation."""
    value = LegalClientMatterVisibilityBinding.grant(
        client_principal_id=principal,
        case_matter=matter,
        granted_by_principal_id="principal-provisioner",
        granted_at=NOW + timedelta(minutes=1),
        evidence_reference=f"visibility-{matter.case_matter_id}",
    )
    return LegalClientMatterVisibilityRegistry.grant(
        value,
        collections["visibility"],
    )


def _app(
    mongo_context: dict[str, Any],
    *,
    tenant: str,
    principal: str,
    monkeypatch: pytest.MonkeyPatch,
    snapshot_calls: list[str],
) -> FastAPI:
    """Mount the real D6 dependency chain against isolated durable stores."""
    collections = mongo_context["collections"]
    principal_reader = _PrincipalReader(collections["principal"])
    membership_reader = _MembershipReader(collections["membership"])
    role_reader = _RoleReader(collections["role"], collections["business"])

    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.dependency_overrides[authorization_http.get_current_identity] = (
        lambda: _identity(tenant, principal)
    )
    app.dependency_overrides[
        authentication.get_principal_authority_repository
    ] = lambda: principal_reader
    app.dependency_overrides[
        tenant_access.get_tenant_membership_repository
    ] = lambda: membership_reader
    app.dependency_overrides[
        authorization_http.get_role_assignment_repository
    ] = lambda: role_reader

    real_client = mongo_context["client"]
    real_database = mongo_context["database"]

    class _TracingClient:
        def start_session(self) -> Any:
            snapshot_calls.append("start_session")
            return real_client.start_session()

    monkeypatch.setattr(
        legal_router,
        "_db_handles",
        lambda: (_TracingClient(), real_database),
    )
    app.include_router(legal_router.router, prefix="/api")
    return app


def test_real_http_projects_only_current_visible_client_matters(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Live IAM + D6 snapshot + D5 returns exact current safe matter cards."""
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"client-{uuid.uuid4().hex}"
    _seed_client(collections, tenant=tenant, principal=principal)

    opened = _matter(tenant, "matter-a")
    other = _matter(tenant, "matter-b")
    LegalOperationsLifecycleRegistry.create(opened, collections["lifecycle"])
    LegalOperationsLifecycleRegistry.create(other, collections["lifecycle"])
    _grant(collections, principal=principal, matter=opened)
    _grant(collections, principal=principal, matter=other)

    closed = opened.transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="matter-closed",
        occurred_at=NOW + timedelta(hours=1),
    )
    LegalOperationsLifecycleRegistry.create(closed, collections["lifecycle"])

    snapshots: list[str] = []
    app = _app(
        mongo_context,
        tenant=tenant,
        principal=principal,
        monkeypatch=monkeypatch,
        snapshot_calls=snapshots,
    )
    with TestClient(app) as http:
        response = http.get(
            "/api/legal-operations/client/matters",
            headers={"X-Tenant-ID": tenant},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == tenant
    assert body["visibility"] == "LEGAL_CLIENT_EXPLICIT_MATTERS"
    assert body["matters"] == [
        {
            "case_matter_id": "matter-a",
            "matter_reference": "CLIENT-matter-a",
            "opened_at": NOW.isoformat(),
            "state": "CLOSED",
        },
        {
            "case_matter_id": "matter-b",
            "matter_reference": "CLIENT-matter-b",
            "opened_at": NOW.isoformat(),
            "state": "OPEN",
        },
    ]
    assert snapshots == ["start_session"]

    forbidden = {
        "principal_id",
        "client_principal_id",
        "evidence_reference",
        "fingerprint",
        "transition_history",
        "instruction_id",
        "document_id",
        "deputy_id",
        "attempt_id",
        "service_execution_id",
        "return_id",
        "invoice_id",
        "payment_id",
        "settlement_id",
    }
    assert forbidden.isdisjoint(body)
    for item in body["matters"]:
        assert forbidden.isdisjoint(item)


def test_real_http_revoked_visibility_yields_empty_projection(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Durable ACTIVE+REVOKED history does not leak stale matter access."""
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"client-{uuid.uuid4().hex}"
    _seed_client(collections, tenant=tenant, principal=principal)

    matter = _matter(tenant, "matter-revoked")
    LegalOperationsLifecycleRegistry.create(matter, collections["lifecycle"])
    active = _grant(collections, principal=principal, matter=matter)
    revoked = active.revoke(
        revoked_by_principal_id="principal-provisioner",
        revoked_at=NOW + timedelta(minutes=2),
        evidence_reference="visibility-revoked",
    )
    LegalClientMatterVisibilityRegistry.revoke(
        revoked,
        collections["visibility"],
    )

    snapshots: list[str] = []
    app = _app(
        mongo_context,
        tenant=tenant,
        principal=principal,
        monkeypatch=monkeypatch,
        snapshot_calls=snapshots,
    )
    with TestClient(app) as http:
        response = http.get(
            "/api/legal-operations/client/matters",
            headers={"X-Tenant-ID": tenant},
        )

    assert response.status_code == 200
    assert response.json()["matters"] == []
    assert snapshots == ["start_session"]


def test_real_http_revoked_legal_client_role_denies_before_snapshot(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """HTTP D4 admission denies revoked LEGAL_CLIENT before D6 opens Mongo snapshot."""
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"client-{uuid.uuid4().hex}"
    _seed_client(
        mongo_context["collections"],
        tenant=tenant,
        principal=principal,
        final_status=RoleAssignmentStatus.REVOKED,
    )

    snapshots: list[str] = []
    app = _app(
        mongo_context,
        tenant=tenant,
        principal=principal,
        monkeypatch=monkeypatch,
        snapshot_calls=snapshots,
    )
    with TestClient(app) as http:
        response = http.get(
            "/api/legal-operations/client/matters",
            headers={"X-Tenant-ID": tenant},
        )

    assert response.status_code == 403
    assert snapshots == []
    assert VERSION == "v1.0.0-L8-7D6-CLIENT-MATTER-READ-API-RM-CERT"
    assert legal_router.VERSION == "v1.6.0-L8-7D6-CLIENT-MATTER-READ-API"


# SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_client_matter_http_real_mongo.py
# VERSION: v1.0.0-L8-7D6-CLIENT-MATTER-READ-API-RM-CERT
# AUTHORITY BOUNDARY: real-Mongo D6 authenticated snapshot client-matter HTTP certificate only
# TENANT POSTURE: explicit tenant scope plus durable current LEGAL_CLIENT IAM and ACTIVE visibility
# FAIL-CLOSED POSTURE: revoked IAM/visibility or Mongo failure cannot become client projection data
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
