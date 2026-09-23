"""Host-backed authenticated intake command certificate for Legal Operations.

TITLE: WILSY OS Legal Operations Intake Command API Real-Mongo Certificate
VERSION: v1.0.1-L8-2-LEGAL-OPERATIONS-INTAKE-COMMAND-RM-CERT
AUTHORITY: Host-backed certificate for authenticated L8-2 intake command composition.
EPITOME: Prove live split-store IAM, actual FastAPI POST dispatch, exact
         own-tenant CaseMatter -> LegalInstruction -> ProcessDocument ->
         REGISTERED custody creation/replay, least-privilege legal-role admission,
         cross-tenant denial, partial-state rejection, body-authority exclusion,
         and bounded durable output against the writable Wilsy Mongo replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_intake_command_router_real_mongo.py
COLLABORATION / OWNERSHIP: Command API owns HTTP/transaction composition;
                            tenant authorization owns principal/membership/
                            business-role/granting-role admission; L8-2 owns
                            canonical intake registration; P1/P2/L8-0 own
                            underlying lifecycle, persistence, and history truth.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.1-L8-2-LEGAL-OPERATIONS-INTAKE-COMMAND-RM-CERT
           binds the host certificate to command API v1.2.1 after the
           non-semantic HTTP 422 status-alias cleanup; all live IAM, transaction,
           replay, tenant, partial-state, and non-financial assertions remain.
           2026-09-23 v1.0.0-L8-2-LEGAL-OPERATIONS-INTAKE-COMMAND-RM-CERT
           establishes live instruction-write intake evidence with canonical
           tenant_business_roles + role_assignments IAM, exact replay,
           partner/attorney/paralegal admission, secretary/client/sheriff denial,
           foreign-scope denial, body tenant exclusion, partial-state rejection,
           transaction-safe failure, and non-financial durable rows.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic identifiers and legal
                             references only; no real customer, credential,
                             browser secret, provider, payment, or external data.
TENANT BOUNDARY: X-Tenant-ID is request scope only. Durable ACTIVE principal,
                 membership, an eligible legal-practice business role, and a
                 granting role carrying legal_operations:instruction:write must
                 all resolve for the same tenant before registration.
AUTHORITY BOUNDARY: Certificate only. HTTP registration cannot manufacture
                    instruction acceptance, office receipt, allocation, attempt,
                    service, return, invoice, payment, execution, settlement, or
                    accounting truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement. Intake rows remain non-financial.
TRANSACTION BOUNDARY: Production command API starts/commits/aborts one Mongo
                      transaction; L8-2/P2 receive that session and own no
                      transaction lifecycle.
FAIL-CLOSED DECLARATION: Unavailable/wrong Mongo runtime, IAM mismatch,
                         foreign scope, unauthorized role, caller-supplied tenant,
                         partial/divergent registration, or partial-write leakage
                         fails the certificate.
"""
from __future__ import annotations

from collections.abc import Mapping
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
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.1-L8-2-LEGAL-OPERATIONS-INTAKE-COMMAND-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 23, 8, 30, tzinfo=timezone.utc)


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
                f"L8_2C_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_2C_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_2C_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client[f"legal_ops_l8_2c_intake_http_{uuid.uuid4().hex}"]
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
    """Resolve business roles and granting roles from canonical split stores."""

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
        username="intake-operator",
        email="intake@example.test",
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
            BASE,
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
    """Compose production command router with canonical split-IAM readers."""
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
    payload: Mapping[str, object],
    request_tenant: str | None = None,
) -> Any:
    """Issue one actual intake POST through production IAM and router."""
    with TestClient(
        _app(
            context,
            tenant_id=tenant_id,
            principal_id=principal_id,
        )
    ) as client:
        return client.post(
            "/api/legal-operations/intake/registrations",
            json=payload,
            headers={"X-Tenant-ID": request_tenant or tenant_id},
        )


def _payload(suffix: str) -> dict[str, object]:
    """Return one complete linked synthetic intake command body."""
    return {
        "case_matter_id": f"matter-{suffix}",
        "matter_reference": f"CASE-2026-{suffix}",
        "case_opened_at": BASE.isoformat(),
        "matter_evidence_reference": f"matter-source-{suffix}",
        "instruction_id": f"instruction-{suffix}",
        "instruction_registered_at": (BASE + timedelta(minutes=1)).isoformat(),
        "instruction_evidence_reference": f"instruction-source-{suffix}",
        "document_id": f"document-{suffix}",
        "document_type": "summons",
        "document_registered_at": (BASE + timedelta(minutes=2)).isoformat(),
        "document_registration_evidence_reference": f"document-source-{suffix}",
        "registration_custody_event_id": f"custody-{suffix}",
    }


def _all_key_names(item: Any) -> set[str]:
    """Collect nested mapping keys for explicit financial-boundary assertions."""
    if isinstance(item, dict):
        names = set(item)
        for child in item.values():
            names.update(_all_key_names(child))
        return names
    if isinstance(item, list):
        names: set[str] = set()
        for child in item:
            names.update(_all_key_names(child))
        return names
    return set()


@pytest.mark.parametrize(
    ("business_role", "granting_role"),
    (
        ("tenant_legal_partner", "LEGAL_PARTNER"),
        ("tenant_legal_attorney", "LEGAL_ATTORNEY"),
        ("tenant_legal_paralegal", "LEGAL_PARALEGAL"),
    ),
)
def test_real_mongo_authorized_legal_roles_can_register_intake(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    business_role: str,
    granting_role: str,
) -> None:
    """Each intended legal-practice role can create one exact own-tenant intake."""
    tenant_id = f"tenant-intake-{uuid.uuid4().hex}"
    principal_id = f"principal-intake-{uuid.uuid4().hex}"
    collections = mongo_context["collections"]
    _persist_iam(
        collections,
        tenant_id=tenant_id,
        principal_id=principal_id,
        business_role=business_role,
        granting_role=granting_role,
    )
    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (mongo_context["client"], mongo_context["database"]),
    )

    response = _post(
        mongo_context,
        tenant_id=tenant_id,
        principal_id=principal_id,
        payload=_payload(uuid.uuid4().hex),
    )

    assert response.status_code == 200, response.text
    assert response.json()["disposition"] == "CREATED"
    assert collections["lifecycle"].count_documents({"tenant_id": tenant_id}) == 4
    assert {
        row["entity_type"]
        for row in collections["lifecycle"].find({"tenant_id": tenant_id})
    } == {
        "CaseMatter",
        "LegalInstruction",
        "ProcessDocument",
        "DocumentCustodyEvent",
    }


def test_real_mongo_intake_exact_replay_has_no_duplicate_rows(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exact repeated HTTP intake command replays without durable duplication."""
    tenant_id = f"tenant-replay-{uuid.uuid4().hex}"
    principal_id = f"principal-replay-{uuid.uuid4().hex}"
    collections = mongo_context["collections"]
    _persist_iam(
        collections,
        tenant_id=tenant_id,
        principal_id=principal_id,
        business_role="tenant_legal_partner",
        granting_role="LEGAL_PARTNER",
    )
    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (mongo_context["client"], mongo_context["database"]),
    )
    payload = _payload(uuid.uuid4().hex)

    first = _post(
        mongo_context,
        tenant_id=tenant_id,
        principal_id=principal_id,
        payload=payload,
    )
    replay = _post(
        mongo_context,
        tenant_id=tenant_id,
        principal_id=principal_id,
        payload=payload,
    )

    assert first.status_code == 200, first.text
    assert replay.status_code == 200, replay.text
    assert first.json()["disposition"] == "CREATED"
    assert replay.json()["disposition"] == "REPLAYED"
    assert collections["lifecycle"].count_documents({"tenant_id": tenant_id}) == 4


def test_real_mongo_intake_denials_precede_legal_writes(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Secretary, client, sheriff, revoked partner, and foreign scope cannot intake."""
    collections = mongo_context["collections"]
    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (mongo_context["client"], mongo_context["database"]),
    )

    cases = (
        ("tenant_legal_secretary", "LEGAL_SECRETARY", False),
        ("tenant_legal_client", "LEGAL_CLIENT", False),
        ("tenant_sheriff", "SHERIFF", False),
        ("tenant_legal_partner", "LEGAL_PARTNER", True),
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
        response = _post(
            mongo_context,
            tenant_id=tenant_id,
            principal_id=principal_id,
            payload=_payload(uuid.uuid4().hex),
        )
        assert response.status_code == 403
        assert collections["lifecycle"].count_documents(
            {"tenant_id": tenant_id}
        ) == 0

    tenant_id = f"tenant-cross-{uuid.uuid4().hex}"
    principal_id = f"principal-cross-{uuid.uuid4().hex}"
    foreign_tenant = f"tenant-foreign-{uuid.uuid4().hex}"
    _persist_iam(
        collections,
        tenant_id=tenant_id,
        principal_id=principal_id,
        business_role="tenant_legal_partner",
        granting_role="LEGAL_PARTNER",
    )
    response = _post(
        mongo_context,
        tenant_id=tenant_id,
        principal_id=principal_id,
        payload=_payload(uuid.uuid4().hex),
        request_tenant=foreign_tenant,
    )
    assert response.status_code == 403
    assert collections["lifecycle"].count_documents({"tenant_id": tenant_id}) == 0
    assert collections["lifecycle"].count_documents(
        {"tenant_id": foreign_tenant}
    ) == 0


def test_real_mongo_body_tenant_and_partial_registration_fail_closed(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Body tenant authority is forbidden and partial durable state is not healed."""
    tenant_id = f"tenant-partial-{uuid.uuid4().hex}"
    principal_id = f"principal-partial-{uuid.uuid4().hex}"
    collections = mongo_context["collections"]
    _persist_iam(
        collections,
        tenant_id=tenant_id,
        principal_id=principal_id,
        business_role="tenant_legal_partner",
        granting_role="LEGAL_PARTNER",
    )
    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (mongo_context["client"], mongo_context["database"]),
    )

    hostile = _payload(uuid.uuid4().hex)
    hostile["tenant_id"] = f"foreign-{uuid.uuid4().hex}"
    rejected = _post(
        mongo_context,
        tenant_id=tenant_id,
        principal_id=principal_id,
        payload=hostile,
    )
    assert rejected.status_code == 422
    assert collections["lifecycle"].count_documents({"tenant_id": tenant_id}) == 0

    suffix = uuid.uuid4().hex
    payload = _payload(suffix)
    partial_case = CaseMatter(
        tenant_id=tenant_id,
        case_matter_id=str(payload["case_matter_id"]),
        matter_reference=str(payload["matter_reference"]),
        opened_at=BASE,
        evidence_reference=str(payload["matter_evidence_reference"]),
    )
    LegalOperationsLifecycleRegistry.create(
        partial_case,
        collections["lifecycle"],
    )
    assert collections["lifecycle"].count_documents({"tenant_id": tenant_id}) == 1

    partial = _post(
        mongo_context,
        tenant_id=tenant_id,
        principal_id=principal_id,
        payload=payload,
    )
    assert partial.status_code == 422
    assert collections["lifecycle"].count_documents({"tenant_id": tenant_id}) == 1


def test_real_mongo_intake_rows_exclude_downstream_and_financial_authority(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Successful intake persists registration truth only, never downstream state."""
    tenant_id = f"tenant-boundary-{uuid.uuid4().hex}"
    principal_id = f"principal-boundary-{uuid.uuid4().hex}"
    collections = mongo_context["collections"]
    _persist_iam(
        collections,
        tenant_id=tenant_id,
        principal_id=principal_id,
        business_role="tenant_legal_partner",
        granting_role="LEGAL_PARTNER",
    )
    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (mongo_context["client"], mongo_context["database"]),
    )

    response = _post(
        mongo_context,
        tenant_id=tenant_id,
        principal_id=principal_id,
        payload=_payload(uuid.uuid4().hex),
    )
    assert response.status_code == 200, response.text

    rows = list(collections["lifecycle"].find({"tenant_id": tenant_id}))
    assert len(rows) == 4
    serialized = str(rows)
    for forbidden_state in (
        "ACCEPTED",
        "RECEIVED_IN_OFFICE",
        "ALLOCATED_TO_DEPUTY",
        "ServiceAttempt",
        "ServiceExecution",
        "ReturnOfService",
    ):
        assert forbidden_state not in serialized

    forbidden_keys = {
        "payment",
        "settlement",
        "paid_state",
        "refund",
        "invoice",
        "billing_execution",
        "bank_execution",
        "provider_execution",
    }
    for row in rows:
        assert forbidden_keys.isdisjoint(_all_key_names(row))

    assert command_api.VERSION == (
        "v1.2.1-L8-2-LEGAL-OPERATIONS-INTAKE-COMMAND-API"
    )
    assert VERSION == (
        "v1.0.1-L8-2-LEGAL-OPERATIONS-INTAKE-COMMAND-RM-CERT"
    )


# ARTIFACT: test_legal_operations_intake_command_router_real_mongo.py
# VERSION: v1.0.1-L8-2-LEGAL-OPERATIONS-INTAKE-COMMAND-RM-CERT
# AUTHORITY BOUNDARY: host-backed live-IAM intake command certificate only
# TENANT POSTURE: exact tenant with ACTIVE split-store legal-practice IAM truth
# FAIL-CLOSED POSTURE: runtime/IAM/scope/body/partial/divergence failures deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT