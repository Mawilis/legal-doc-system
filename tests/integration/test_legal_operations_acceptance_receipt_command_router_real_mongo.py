"""Host-backed authenticated acceptance/receipt command certificate.

TITLE: WILSY OS Legal Operations Acceptance Receipt Command Real-Mongo Certificate
VERSION: v1.0.0-L8-3-LEGAL-OPERATIONS-RECEIPT-COMMAND-RM-CERT
AUTHORITY: Host-backed certification of authenticated L8-3 acceptance/receipt transport.
EPITOME: Prove live split-store IAM, actual FastAPI POST dispatch, sheriff-only
         own-tenant instruction acceptance plus office receipt, exact replay,
         denial-before-mutation, foreign-scope rejection, body-authority
         exclusion, bounded absence/partial-state errors, and non-financial
         durable evidence against the writable Wilsy Mongo replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_acceptance_receipt_command_router_real_mongo.py
COLLABORATION / OWNERSHIP: Tenant authorization owns principal/membership/
                            business-role/granting-role admission; command API
                            owns HTTP/transaction composition; L8-1/L8-2 provide
                            canonical prerequisites; L8-3 owns acceptance and
                            physical office receipt; P1/P2/L8-0 own lifecycle,
                            persistence, custody history, and current projection.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-3-LEGAL-OPERATIONS-RECEIPT-COMMAND-RM-CERT
           establishes live legal_operations:receipt:write evidence proving
           SHERIFF-only admission, exact tenant scope, create/replay, deputy/
           legal-practice/revoked-sheriff denial, foreign request denial,
           caller tenant-field rejection, missing-office 404, partial-state
           422 with no healing, and non-financial durable evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic principals, tenants, legal
                             identities, and evidence references only; no real
                             customer, credential, provider, payment, or secret.
TENANT BOUNDARY: X-Tenant-ID is request scope only. ACTIVE principal,
                 membership, tenant_sheriff business role, and ACTIVE SHERIFF
                 granting role must all resolve for the same tenant before L8-3
                 may read or mutate lifecycle evidence.
AUTHORITY BOUNDARY: Certificate only. ACCEPTED is not service; RECEIVED and
                    RECEIVED_IN_OFFICE are not allocation, deputy possession,
                    attempt, service execution, return, invoice, payment,
                    execution, settlement, or accounting truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement. Receipt command evidence is
                              explicitly non-financial.
TRANSACTION BOUNDARY: Production command API starts/commits/aborts one Mongo
                      transaction; L8-3/P2 receive that exact session and own
                      no transaction lifecycle.
FAIL-CLOSED DECLARATION: Unavailable/wrong Mongo runtime, IAM mismatch,
                         foreign scope, unauthorized/revoked role, caller
                         tenant authority, missing office, partial durable
                         transition, rollback leakage, or financial leakage fails.
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
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    LegalInstructionState,
)
from tools.eos.legal_operations.orchestration.process_service_directory_provisioning_orchestrator import (
    provision_district,
    provision_sheriff_office,
)
from tools.eos.legal_operations.orchestration.process_service_intake_registration_orchestrator import (
    register_process_service_intake,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-3-LEGAL-OPERATIONS-RECEIPT-COMMAND-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 23, 10, 0, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield one verified writable isolated database; host failure fails certification."""
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
                f"L8_3C_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_3C_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_3C_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client[f"legal_ops_l8_3c_receipt_http_{uuid.uuid4().hex}"]
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
    """Resolve durable principal truth without mutation authority."""

    def __init__(self, collection: Any) -> None:
        self._collection = collection

    def resolve(self, principal_id: str, *, session: Any = None) -> Any:
        return PrincipalAuthorityRepository.get(
            principal_id,
            self._collection,
            session=session,
        )


class _MembershipReader:
    """Resolve durable exact-tenant membership truth without mutation authority."""

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


class _SplitRoleReader:
    """Resolve business and granting roles from the canonical split stores."""

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
        username="receipt-operator",
        email="receipt@example.test",
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
    """Persist exact split-IAM truth for one tenant principal."""
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
    """Issue one actual L8-3 receipt POST through production IAM and router."""
    with TestClient(
        _app(
            context,
            tenant_id=tenant_id,
            principal_id=principal_id,
        )
    ) as client:
        return client.post(
            "/api/legal-operations/intake/acceptance-receipts",
            json=payload,
            headers={"X-Tenant-ID": request_tenant or tenant_id},
        )


def _transaction(client: Any) -> Any:
    """Start one caller-owned snapshot/majority transaction for prerequisite seeding."""
    session = client.start_session()
    session.start_transaction(
        read_concern=ReadConcern("snapshot"),
        write_concern=WriteConcern(w="majority", j=True),
    )
    return session


def _seed_prerequisites(
    context: dict[str, Any],
    *,
    tenant_id: str,
    suffix: str,
    include_office: bool = True,
) -> Any:
    """Seed canonical L8-1/L8-2 prerequisites without bypassing domain authority."""
    client = context["client"]
    lifecycle = context["collections"]["lifecycle"]
    session = _transaction(client)
    try:
        if include_office:
            provision_district(
                tenant_id=tenant_id,
                district_id=f"district-{suffix}",
                name="Johannesburg Central",
                jurisdiction_code="ZA-GP-JHB",
                evidence_reference=f"district-source-{suffix}",
                lifecycle_collection=lifecycle,
                session=session,
            )
            provision_sheriff_office(
                tenant_id=tenant_id,
                sheriff_office_id=f"office-{suffix}",
                district_id=f"district-{suffix}",
                name="Sheriff Johannesburg Central",
                evidence_reference=f"office-source-{suffix}",
                lifecycle_collection=lifecycle,
                session=session,
            )
        intake = register_process_service_intake(
            tenant_id=tenant_id,
            case_matter_id=f"matter-{suffix}",
            matter_reference=f"CASE-2026-{suffix}",
            case_opened_at=BASE,
            matter_evidence_reference=f"matter-source-{suffix}",
            instruction_id=f"instruction-{suffix}",
            instruction_registered_at=BASE + timedelta(minutes=1),
            instruction_evidence_reference=f"instruction-source-{suffix}",
            document_id=f"document-{suffix}",
            document_type="summons",
            document_registered_at=BASE + timedelta(minutes=2),
            document_registration_evidence_reference=f"document-source-{suffix}",
            registration_custody_event_id=f"custody-registration-{suffix}",
            lifecycle_collection=lifecycle,
            session=session,
        )
        session.commit_transaction()
        return intake
    finally:
        session.end_session()


def _payload(suffix: str) -> dict[str, object]:
    """Return one bounded L8-3 HTTP command body with no tenant authority."""
    return {
        "instruction_id": f"instruction-{suffix}",
        "document_id": f"document-{suffix}",
        "sheriff_office_id": f"office-{suffix}",
        "accepted_at": (BASE + timedelta(minutes=10)).isoformat(),
        "acceptance_evidence_reference": f"acceptance-source-{suffix}",
        "received_at": (BASE + timedelta(minutes=15)).isoformat(),
        "receipt_evidence_reference": f"receipt-source-{suffix}",
        "receipt_custody_event_id": f"custody-received-{suffix}",
    }


def _all_key_names(item: Any) -> set[str]:
    """Collect nested durable mapping keys for financial-boundary assertions."""
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


def test_real_mongo_sheriff_accepts_receipt_and_exact_replay_is_no_write(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Live sheriff IAM creates exactly three L8-3 facts then exact-replays."""
    tenant_id = f"tenant-receipt-{uuid.uuid4().hex}"
    principal_id = f"principal-receipt-{uuid.uuid4().hex}"
    suffix = uuid.uuid4().hex
    collections = mongo_context["collections"]

    _seed_prerequisites(
        mongo_context,
        tenant_id=tenant_id,
        suffix=suffix,
    )
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
    payload = _payload(suffix)

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
    assert first.json()["accepted_instruction"]["state"] == "ACCEPTED"
    assert first.json()["received_document"]["state"] == "RECEIVED"
    assert (
        first.json()["receipt_custody_event"]["event_type"]
        == "RECEIVED_IN_OFFICE"
    )
    assert collections["lifecycle"].count_documents({"tenant_id": tenant_id}) == 9


def test_real_mongo_receipt_denials_precede_l8_3_mutation(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deputy, legal partner, and revoked sheriff cannot create receipt truth."""
    collections = mongo_context["collections"]
    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (mongo_context["client"], mongo_context["database"]),
    )

    for business_role, granting_role, revoke in (
        ("tenant_deputy", "DEPUTY", False),
        ("tenant_legal_partner", "LEGAL_PARTNER", False),
        ("tenant_sheriff", "SHERIFF", True),
    ):
        tenant_id = f"tenant-deny-{uuid.uuid4().hex}"
        principal_id = f"principal-deny-{uuid.uuid4().hex}"
        suffix = uuid.uuid4().hex
        _seed_prerequisites(
            mongo_context,
            tenant_id=tenant_id,
            suffix=suffix,
        )
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
        before = collections["lifecycle"].count_documents({"tenant_id": tenant_id})
        response = _post(
            mongo_context,
            tenant_id=tenant_id,
            principal_id=principal_id,
            payload=_payload(suffix),
        )
        assert response.status_code == 403
        assert collections["lifecycle"].count_documents(
            {"tenant_id": tenant_id}
        ) == before


def test_real_mongo_foreign_scope_and_body_tenant_fail_before_receipt_write(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Foreign request scope and caller body tenant authority cannot mutate L8-3."""
    tenant_id = f"tenant-scope-{uuid.uuid4().hex}"
    principal_id = f"principal-scope-{uuid.uuid4().hex}"
    suffix = uuid.uuid4().hex
    foreign = f"tenant-foreign-{uuid.uuid4().hex}"
    collections = mongo_context["collections"]

    _seed_prerequisites(
        mongo_context,
        tenant_id=tenant_id,
        suffix=suffix,
    )
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
    before = collections["lifecycle"].count_documents({"tenant_id": tenant_id})

    foreign_response = _post(
        mongo_context,
        tenant_id=tenant_id,
        principal_id=principal_id,
        payload=_payload(suffix),
        request_tenant=foreign,
    )
    assert foreign_response.status_code == 403
    assert collections["lifecycle"].count_documents({"tenant_id": tenant_id}) == before

    hostile = _payload(suffix)
    hostile["tenant_id"] = foreign
    body_response = _post(
        mongo_context,
        tenant_id=tenant_id,
        principal_id=principal_id,
        payload=hostile,
    )
    assert body_response.status_code == 422
    assert collections["lifecycle"].count_documents({"tenant_id": tenant_id}) == before


def test_real_mongo_missing_office_is_404_and_partial_state_is_not_healed(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Canonical office absence and partial transition remain bounded no-heal errors."""
    collections = mongo_context["collections"]
    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: (mongo_context["client"], mongo_context["database"]),
    )

    missing_tenant = f"tenant-missing-{uuid.uuid4().hex}"
    missing_principal = f"principal-missing-{uuid.uuid4().hex}"
    missing_suffix = uuid.uuid4().hex
    _seed_prerequisites(
        mongo_context,
        tenant_id=missing_tenant,
        suffix=missing_suffix,
        include_office=False,
    )
    _persist_iam(
        collections,
        tenant_id=missing_tenant,
        principal_id=missing_principal,
        business_role="tenant_sheriff",
        granting_role="SHERIFF",
    )
    missing_before = collections["lifecycle"].count_documents(
        {"tenant_id": missing_tenant}
    )
    missing = _post(
        mongo_context,
        tenant_id=missing_tenant,
        principal_id=missing_principal,
        payload=_payload(missing_suffix),
    )
    assert missing.status_code == 404
    assert collections["lifecycle"].count_documents(
        {"tenant_id": missing_tenant}
    ) == missing_before

    partial_tenant = f"tenant-partial-{uuid.uuid4().hex}"
    partial_principal = f"principal-partial-{uuid.uuid4().hex}"
    partial_suffix = uuid.uuid4().hex
    intake = _seed_prerequisites(
        mongo_context,
        tenant_id=partial_tenant,
        suffix=partial_suffix,
    )
    _persist_iam(
        collections,
        tenant_id=partial_tenant,
        principal_id=partial_principal,
        business_role="tenant_sheriff",
        granting_role="SHERIFF",
    )
    seed = _transaction(mongo_context["client"])
    try:
        accepted = intake.instruction.transition_to(
            LegalInstructionState.ACCEPTED,
            evidence_reference=f"acceptance-source-{partial_suffix}",
            occurred_at=BASE + timedelta(minutes=10),
        )
        LegalOperationsLifecycleRegistry.create(
            accepted,
            collections["lifecycle"],
            session=seed,
        )
        seed.commit_transaction()
    finally:
        seed.end_session()

    partial_before = collections["lifecycle"].count_documents(
        {"tenant_id": partial_tenant}
    )
    partial = _post(
        mongo_context,
        tenant_id=partial_tenant,
        principal_id=partial_principal,
        payload=_payload(partial_suffix),
    )
    assert partial.status_code == 422
    assert collections["lifecycle"].count_documents(
        {"tenant_id": partial_tenant}
    ) == partial_before


def test_real_mongo_receipt_rows_exclude_allocation_service_and_financial_authority(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Successful receipt persists only L8-3 truth and binds command API v1.3."""
    tenant_id = f"tenant-boundary-{uuid.uuid4().hex}"
    principal_id = f"principal-boundary-{uuid.uuid4().hex}"
    suffix = uuid.uuid4().hex
    collections = mongo_context["collections"]

    _seed_prerequisites(
        mongo_context,
        tenant_id=tenant_id,
        suffix=suffix,
    )
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
    response = _post(
        mongo_context,
        tenant_id=tenant_id,
        principal_id=principal_id,
        payload=_payload(suffix),
    )
    assert response.status_code == 200, response.text

    rows = list(collections["lifecycle"].find({"tenant_id": tenant_id}))
    assert len(rows) == 9
    serialized = str(rows)
    for forbidden_state in (
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
        "v1.3.0-L8-3-LEGAL-OPERATIONS-RECEIPT-COMMAND-API"
    )
    assert VERSION == (
        "v1.0.0-L8-3-LEGAL-OPERATIONS-RECEIPT-COMMAND-RM-CERT"
    )


# ARTIFACT: test_legal_operations_acceptance_receipt_command_router_real_mongo.py
# VERSION: v1.0.0-L8-3-LEGAL-OPERATIONS-RECEIPT-COMMAND-RM-CERT
# AUTHORITY BOUNDARY: host-backed live-IAM L8-3 acceptance/receipt command certificate only
# TENANT POSTURE: exact tenant with ACTIVE split-store sheriff IAM truth
# FAIL-CLOSED POSTURE: runtime/IAM/scope/body/absence/partial-state failures deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
