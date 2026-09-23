"""Host-backed authenticated directory command certificate for Legal Operations.

TITLE: WILSY OS Legal Operations Directory Command API Real-Mongo Certificate
VERSION: v1.0.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-COMMAND-RM-CERT
AUTHORITY: Host-backed certificate for authenticated L8-1 directory command composition.
EPITOME: Prove live split-store IAM, actual FastAPI POST dispatch, exact
         own-tenant District -> SheriffOffice -> Deputy provisioning, replay,
         least-privilege denial, cross-tenant denial, parent absence, and
         bounded durable output against the writable Wilsy Mongo replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_directory_command_router_real_mongo.py
COLLABORATION / OWNERSHIP: Command API owns HTTP/transaction composition;
                            tenant authorization owns principal/membership/
                            business-role/granting-role admission; L8-1 owns
                            canonical directory provisioning; P1/P2/L8-0 own
                            underlying immutable truth.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-COMMAND-RM-CERT
           establishes live sheriff-only directory command evidence with the
           canonical tenant_business_roles + role_assignments IAM split,
           exact replay, foreign-scope denial, deputy/client exclusion,
           parent absence, transaction-safe failure, and non-financial rows.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic identifiers only; no real
                             customer, provider, credential, browser secret,
                             payment, or external-service data is used.
TENANT BOUNDARY: X-Tenant-ID is request scope only. Durable ACTIVE principal,
                 membership, tenant_sheriff business role, and SHERIFF granting
                 role must all resolve for the same tenant before provisioning.
AUTHORITY BOUNDARY: Certificate only. HTTP cannot manufacture tenant authority,
                    allocation, attempt, service, return, invoice, payment,
                    execution, settlement, or accounting truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement. Directory rows remain non-financial.
TRANSACTION BOUNDARY: Production command API starts/commits/aborts one Mongo
                      transaction; L8-1/P2 receive that session and own no
                      transaction lifecycle.
FAIL-CLOSED DECLARATION: Unavailable/wrong Mongo runtime, IAM mismatch,
                         foreign scope, unauthorized role, missing parent,
                         divergent directory identity, or partial-write leakage
                         fails the certificate.
"""
from __future__ import annotations

from collections.abc import Mapping
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
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-COMMAND-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 23, 8, 0, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield a verified writable isolated database; host failure fails certification."""
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
                f"L8_1C_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_1C_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_1C_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client[f"legal_ops_l8_1c_directory_http_{uuid.uuid4().hex}"]
        concerns = {
            "write_concern": WriteConcern(w="majority", j=True),
            "read_concern": ReadConcern("majority"),
        }
        collections = {
            "lifecycle": database.get_collection(COLLECTION, **concerns),
            "principal": database.get_collection("principal_authorities", **concerns),
            "membership": database.get_collection("tenant_memberships", **concerns),
            "roles": database.get_collection("role_assignments", **concerns),
            "business_roles": database.get_collection("tenant_business_roles", **concerns),
        }
        LegalOperationsLifecycleRegistry.ensure_indexes(collections["lifecycle"])
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        RoleAssignmentRepository.ensure_indexes(collections["roles"])
        TenantBusinessRoleRepository.ensure_indexes(collections["business_roles"])
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


class _PrincipalReader:
    """Delegate durable principal resolution to the canonical repository."""

    def __init__(self, collection: Any) -> None:
        self._collection = collection

    def resolve(self, principal_id: str, *, session: Any = None) -> Any:
        """Resolve exact durable principal truth."""
        return PrincipalAuthorityRepository.get(
            principal_id,
            self._collection,
            session=session,
        )


class _MembershipReader:
    """Delegate durable membership resolution to the canonical repository."""

    def __init__(self, collection: Any) -> None:
        self._collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> Any:
        """Resolve exact durable membership truth."""
        return TenantMembershipRepository.resolve(
            principal_id,
            tenant_id,
            self._collection,
            session=session,
        )


class _SplitRoleReader:
    """Resolve business roles and granting roles from their canonical stores."""

    def __init__(
        self,
        authorization_collection: Any,
        business_collection: Any,
    ) -> None:
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
        """Resolve one exact business or granting role without merging stores."""
        from tools.eos.auth.tenant_authority_policy import TENANT_ROLES

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
            if value.business_role != role_id:
                raise RoleAssignmentNotFoundError(
                    "TENANT_BUSINESS_ROLE_NOT_FOUND"
                )
            return value

        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            self._authorization_collection,
            session=session,
        )


def _identity(principal_id: str, tenant_id: str) -> SovereignIdentity:
    """Return authentication projection only; authorization remains durable."""
    return SovereignIdentity(
        identity_id=principal_id,
        tenant_id=tenant_id,
        username="directory-operator",
        email="operator@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )


def _persist_iam(
    collections: dict[str, Any],
    *,
    tenant_id: str,
    principal_id: str,
    business_role: str,
    granting_role: str,
) -> None:
    """Persist split IAM truth for one isolated tenant/operator."""
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
        collections["business_roles"],
    )
    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            principal_id,
            tenant_id,
            granting_role,
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        collections["roles"],
    )


def _app(
    context: dict[str, Any],
    *,
    tenant_id: str,
    principal_id: str,
) -> FastAPI:
    """Compose the production command router with canonical split IAM readers."""
    import tools.eos.api.tenant_authorization_http as authorization_http
    import tools.eos.auth.authentication as authentication
    import tools.eos.auth.tenant_access as tenant_access

    collections = context["collections"]
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.dependency_overrides[authorization_http.get_current_identity] = (
        lambda: _identity(principal_id, tenant_id)
    )
    app.dependency_overrides[authentication.get_principal_authority_repository] = (
        lambda: _PrincipalReader(collections["principal"])
    )
    app.dependency_overrides[tenant_access.get_tenant_membership_repository] = (
        lambda: _MembershipReader(collections["membership"])
    )
    app.dependency_overrides[authorization_http.get_role_assignment_repository] = (
        lambda: _SplitRoleReader(
            collections["roles"],
            collections["business_roles"],
        )
    )
    app.include_router(command_api.router, prefix="/api")
    return app


def _post(
    context: dict[str, Any],
    *,
    tenant_id: str,
    principal_id: str,
    path: str,
    payload: Mapping[str, object],
    request_tenant: str | None = None,
) -> Any:
    """Issue one actual HTTP POST through production authorization and router."""
    with TestClient(
        _app(
            context,
            tenant_id=tenant_id,
            principal_id=principal_id,
        )
    ) as client:
        return client.post(
            path,
            json=payload,
            headers={"X-Tenant-ID": request_tenant or tenant_id},
        )


def _provision_payloads(suffix: str) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Return one linked synthetic District/Office/Deputy command set."""
    district_id = f"district-{suffix}"
    office_id = f"office-{suffix}"
    deputy_id = f"deputy-{suffix}"
    district = {
        "district_id": district_id,
        "name": "Johannesburg Central",
        "jurisdiction_code": "ZA-GP-JHB",
        "evidence_reference": f"district-source-{suffix}",
    }
    office = {
        "sheriff_office_id": office_id,
        "district_id": district_id,
        "name": "Sheriff Johannesburg Central",
        "evidence_reference": f"office-source-{suffix}",
    }
    deputy = {
        "deputy_id": deputy_id,
        "sheriff_office_id": office_id,
        "display_name": "Deputy One",
        "badge_reference": f"badge-{suffix}",
        "evidence_reference": f"deputy-source-{suffix}",
    }
    return district, office, deputy


def test_real_mongo_sheriff_can_provision_and_replay_full_directory(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Live split IAM admits sheriff and exact replay creates no duplicate rows."""
    tenant_id = f"tenant-sheriff-{uuid.uuid4().hex}"
    principal_id = f"principal-sheriff-{uuid.uuid4().hex}"
    suffix = uuid.uuid4().hex
    collections = mongo_context["collections"]
    _persist_iam(
        collections,
        tenant_id=tenant_id,
        principal_id=principal_id,
        business_role="tenant_sheriff",
        granting_role="SHERIFF",
    )
    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (mongo_context["client"], mongo_context["database"]),
    )
    district, office, deputy = _provision_payloads(suffix)

    first = (
        _post(
            mongo_context,
            tenant_id=tenant_id,
            principal_id=principal_id,
            path="/api/legal-operations/directory/districts",
            payload=district,
        ),
        _post(
            mongo_context,
            tenant_id=tenant_id,
            principal_id=principal_id,
            path="/api/legal-operations/directory/sheriff-offices",
            payload=office,
        ),
        _post(
            mongo_context,
            tenant_id=tenant_id,
            principal_id=principal_id,
            path="/api/legal-operations/directory/deputies",
            payload=deputy,
        ),
    )
    assert [response.status_code for response in first] == [200, 200, 200]
    assert [response.json()["disposition"] for response in first] == [
        "CREATED",
        "CREATED",
        "CREATED",
    ]
    assert collections["lifecycle"].count_documents({"tenant_id": tenant_id}) == 3

    replay = (
        _post(
            mongo_context,
            tenant_id=tenant_id,
            principal_id=principal_id,
            path="/api/legal-operations/directory/districts",
            payload=district,
        ),
        _post(
            mongo_context,
            tenant_id=tenant_id,
            principal_id=principal_id,
            path="/api/legal-operations/directory/sheriff-offices",
            payload=office,
        ),
        _post(
            mongo_context,
            tenant_id=tenant_id,
            principal_id=principal_id,
            path="/api/legal-operations/directory/deputies",
            payload=deputy,
        ),
    )
    assert [response.status_code for response in replay] == [200, 200, 200]
    assert [response.json()["disposition"] for response in replay] == [
        "REPLAYED",
        "REPLAYED",
        "REPLAYED",
    ]
    assert collections["lifecycle"].count_documents({"tenant_id": tenant_id}) == 3


def test_real_mongo_directory_command_denials_precede_legal_writes(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deputy, client, revoked sheriff, and foreign scope cannot provision."""
    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (mongo_context["client"], mongo_context["database"]),
    )
    collections = mongo_context["collections"]

    cases = (
        ("tenant_deputy", "DEPUTY", False),
        ("tenant_legal_client", "LEGAL_CLIENT", False),
        ("tenant_sheriff", "SHERIFF", True),
    )
    for business_role, granting_role, revoke in cases:
        tenant_id = f"tenant-deny-{uuid.uuid4().hex}"
        principal_id = f"principal-deny-{uuid.uuid4().hex}"
        _persist_iam(
            collections,
            tenant_id=tenant_id,
            principal_id=principal_id,
            business_role=business_role,
            granting_role=granting_role,
        )
        if revoke:
            RoleAssignmentRepository.compare_and_swap(
                RoleAssignmentAuthority(
                    principal_id,
                    tenant_id,
                    granting_role,
                    RoleAssignmentStatus.REVOKED,
                    1,
                ),
                0,
                collections["roles"],
            )
        district, _, _ = _provision_payloads(uuid.uuid4().hex)
        response = _post(
            mongo_context,
            tenant_id=tenant_id,
            principal_id=principal_id,
            path="/api/legal-operations/directory/districts",
            payload=district,
        )
        assert response.status_code == 403
        assert collections["lifecycle"].count_documents(
            {"tenant_id": tenant_id}
        ) == 0

    tenant_id = f"tenant-cross-{uuid.uuid4().hex}"
    principal_id = f"principal-cross-{uuid.uuid4().hex}"
    _persist_iam(
        collections,
        tenant_id=tenant_id,
        principal_id=principal_id,
        business_role="tenant_sheriff",
        granting_role="SHERIFF",
    )
    foreign = f"tenant-foreign-{uuid.uuid4().hex}"
    district, _, _ = _provision_payloads(uuid.uuid4().hex)
    response = _post(
        mongo_context,
        tenant_id=tenant_id,
        principal_id=principal_id,
        path="/api/legal-operations/directory/districts",
        payload=district,
        request_tenant=foreign,
    )
    assert response.status_code == 403
    assert collections["lifecycle"].count_documents({"tenant_id": tenant_id}) == 0
    assert collections["lifecycle"].count_documents({"tenant_id": foreign}) == 0


def test_real_mongo_missing_parent_and_body_tenant_override_fail_closed(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing parent is bounded absence and tenant_id in body is rejected."""
    tenant_id = f"tenant-parent-{uuid.uuid4().hex}"
    principal_id = f"principal-parent-{uuid.uuid4().hex}"
    collections = mongo_context["collections"]
    _persist_iam(
        collections,
        tenant_id=tenant_id,
        principal_id=principal_id,
        business_role="tenant_sheriff",
        granting_role="SHERIFF",
    )
    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (mongo_context["client"], mongo_context["database"]),
    )
    district, office, _ = _provision_payloads(uuid.uuid4().hex)

    missing_parent = _post(
        mongo_context,
        tenant_id=tenant_id,
        principal_id=principal_id,
        path="/api/legal-operations/directory/sheriff-offices",
        payload=office,
    )
    assert missing_parent.status_code == 404
    assert collections["lifecycle"].count_documents({"tenant_id": tenant_id}) == 0

    hostile = dict(district)
    hostile["tenant_id"] = f"foreign-{uuid.uuid4().hex}"
    rejected = _post(
        mongo_context,
        tenant_id=tenant_id,
        principal_id=principal_id,
        path="/api/legal-operations/directory/districts",
        payload=hostile,
    )
    assert rejected.status_code == 422
    assert collections["lifecycle"].count_documents({"tenant_id": tenant_id}) == 0


def test_real_mongo_directory_rows_exclude_financial_authority(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Successful HTTP provisioning persists only legal directory evidence."""
    tenant_id = f"tenant-financial-{uuid.uuid4().hex}"
    principal_id = f"principal-financial-{uuid.uuid4().hex}"
    collections = mongo_context["collections"]
    _persist_iam(
        collections,
        tenant_id=tenant_id,
        principal_id=principal_id,
        business_role="tenant_sheriff",
        granting_role="SHERIFF",
    )
    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (mongo_context["client"], mongo_context["database"]),
    )
    district, office, deputy = _provision_payloads(uuid.uuid4().hex)
    for path, payload in (
        ("/api/legal-operations/directory/districts", district),
        ("/api/legal-operations/directory/sheriff-offices", office),
        ("/api/legal-operations/directory/deputies", deputy),
    ):
        response = _post(
            mongo_context,
            tenant_id=tenant_id,
            principal_id=principal_id,
            path=path,
            payload=payload,
        )
        assert response.status_code == 200, response.text

    forbidden = {
        "payment",
        "settlement",
        "paid_state",
        "refund",
        "invoice",
        "billing_execution",
        "bank_execution",
        "provider_execution",
    }
    for row in collections["lifecycle"].find({"tenant_id": tenant_id}):
        assert forbidden.isdisjoint(set(row))
    assert command_api.VERSION == (
        "v1.1.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-COMMAND-API"
    )
    assert VERSION == (
        "v1.0.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-COMMAND-RM-CERT"
    )


# ARTIFACT: test_legal_operations_directory_command_router_real_mongo.py
# VERSION: v1.0.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-COMMAND-RM-CERT
# AUTHORITY BOUNDARY: host-backed live-IAM directory command certificate only
# TENANT POSTURE: exact tenant with ACTIVE split-store sheriff IAM truth
# FAIL-CLOSED POSTURE: runtime/IAM/scope/parent/body-override failures deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT