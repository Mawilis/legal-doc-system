"""L7C host-backed certificate for billing read projections.

TITLE: Legal Operations Billing Read Real-Mongo Certificate
VERSION: v1.1.0-L7C-LIVE-IAM-BILLING-READ-RM-CERT
AUTHORITY: Host certificate for authenticated GET projections only.
EPITOME: Persists the canonical P6A/P6B/P6D/P6F chain through existing
         authorities, then proves actual FastAPI reads are tenant-scoped and
         side-effect free.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_billing_read_real_mongo.py
COLLABORATION / OWNERSHIP: Certificate owns isolated host fixture and observations.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: v1.1.0 certifies actual FastAPI GET transport through live
           RequireTenantAuthorization, durable IAM truth, the permitted
           payment_terms_days projection, zero read side effects, and
           corruption/partial-state rejection. v1.0.0 established the
           canonical P6 projection path.
TENANT BOUNDARY: Every source and HTTP read is bound to the authorized tenant.
AUTHORITY BOUNDARY: P1-P6F and IAM remain canonical; this certificate creates no authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
FAIL-CLOSED DECLARATION: Only pre-hello runtime unavailability may skip; all
                         post-hello product and persistence failures fail.
"""
from __future__ import annotations

from datetime import timedelta
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

import tools.eos.api.legal_operations_billing_read_router as billing_api
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tests.integration.test_process_service_client_invoice_issuance_real_mongo import BASE, _issue, _seed_sources


URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
REPLICA_SET = "wilsyVendorCertRS"
VERSION = "v1.1.0-L7C-LIVE-IAM-BILLING-READ-RM-CERT"


class _PrincipalReader:
    """Resolve durable principal truth through the canonical repository."""

    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, *, session: Any = None) -> Any:
        return PrincipalAuthorityRepository.get(principal_id, self.collection, session=session)


class _MembershipReader:
    """Resolve durable membership truth through the canonical repository."""

    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, tenant_id: str, *, session: Any = None) -> Any:
        return TenantMembershipRepository.resolve(principal_id, tenant_id, self.collection, session=session)


class _RoleReader:
    """Resolve durable business and granting role assignments."""

    def __init__(self, collection: Any, business_collection: Any) -> None:
        self.collection = collection
        self.business_collection = business_collection

    def resolve(self, principal_id: str, tenant_id: str, role_id: str | None = None, *, session: Any = None) -> Any:
        if role_id is None:
            return TenantBusinessRoleRepository.resolve(principal_id, tenant_id, self.business_collection, session=session)
        return RoleAssignmentRepository.resolve(principal_id, tenant_id, role_id, self.collection, session=session)


def _identity_projection(principal_id: str, tenant_id: str) -> SovereignIdentity:
    """Inject authentication identity only; durable IAM remains authoritative."""
    return SovereignIdentity(
        identity_id=principal_id, tenant_id=tenant_id, username="l7c-operator",
        email="operator@example.test", auth_method="TEST", status=PrincipalStatus.ACTIVE,
    )


@pytest.fixture()
def mongo() -> Iterator[tuple[MongoClient, Any]]:
    client = MongoClient(URI, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000, replicaSet=REPLICA_SET, retryWrites=True)
    database: Any = None
    active_error = False
    cleanup_error: BaseException | None = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"MONGO_RUNTIME_UNAVAILABLE: {type(error).__name__}")
        if hello.get("setName") != REPLICA_SET:
            pytest.skip(f"MONGO_REPLICA_SET_UNAVAILABLE: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("MONGO_WRITABLE_PRIMARY_UNAVAILABLE")
        database = client.get_database(
            "l7c_" + uuid4().hex[:20],
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        yield client, database
    except BaseException:
        active_error = True
        raise
    finally:
        try:
            if database is not None:
                try:
                    client.drop_database(database.name)
                except BaseException as error:
                    cleanup_error = error
        finally:
            client.close()
        if cleanup_error is not None and not active_error:
            raise cleanup_error


def _app(database: Any, tenant: str, principal_id: str) -> FastAPI:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    import tools.eos.api.tenant_authorization_http as authorization_http
    import tools.eos.auth.authentication as authentication
    import tools.eos.auth.authorization as authorization
    import tools.eos.auth.tenant_access as tenant_access

    collections = {
        "principal": database.get_collection("principal_authorities"),
        "membership": database.get_collection("tenant_memberships"),
        "roles": database.get_collection("role_assignments"),
        "business": database.get_collection("tenant_business_roles"),
    }
    app.dependency_overrides[authorization_http.get_current_identity] = lambda: _identity_projection(principal_id, tenant)
    app.dependency_overrides[authentication.get_principal_authority_repository] = lambda: _PrincipalReader(collections["principal"])
    app.dependency_overrides[tenant_access.get_tenant_membership_repository] = lambda: _MembershipReader(collections["membership"])
    app.dependency_overrides[authorization.get_role_assignment_repository] = lambda: _RoleReader(collections["roles"], collections["business"])
    assert billing_api._BILLING_READ not in app.dependency_overrides
    assert billing_api._INVOICE_READ not in app.dependency_overrides
    app.dependency_overrides[billing_api.get_tariff_collection] = lambda: database.get_collection("tariff_assessments")
    app.dependency_overrides[billing_api.get_eligibility_collection] = lambda: database.get_collection("billing_eligibility")
    app.dependency_overrides[billing_api.get_invoice_collection] = lambda: database.get_collection("client_invoices")
    app.dependency_overrides[billing_api.get_issuance_collection] = lambda: database.get_collection("issuance")
    app.include_router(billing_api.router, prefix="/api")
    return app


def _ensure_iam_indexes(database: Any) -> dict[str, Any]:
    """Ensure canonical IAM indexes and return isolated collections."""
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
    return collections


def _seed_iam(database: Any, *, principal_id: str, tenant: str, business_role: str, granting_role: str, principal_status: PrincipalStatus = PrincipalStatus.ACTIVE, membership_status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE, granting_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE) -> None:
    """Persist one complete current-truth IAM tuple through canonical repositories."""
    collections = _ensure_iam_indexes(database)
    PrincipalAuthorityRepository.create(PrincipalAuthority(principal_id, principal_status, 0), collections["principal"])
    TenantMembershipRepository.insert(TenantMembershipAuthority(principal_id, tenant, membership_status, 0), collections["membership"])
    TenantBusinessRoleRepository.insert(TenantBusinessRoleAuthority(principal_id, tenant, business_role, TenantBusinessRoleStatus.ACTIVE, 0, BASE, None), collections["business"])
    RoleAssignmentRepository.insert(RoleAssignmentAuthority(principal_id, tenant, business_role, RoleAssignmentStatus.ACTIVE, 0), collections["roles"])
    RoleAssignmentRepository.insert(RoleAssignmentAuthority(principal_id, tenant, granting_role, granting_status, 0), collections["roles"])


def _tenant_snapshot(database: Any, tenant: str) -> dict[str, tuple[int, tuple[str, ...]]]:
    """Capture immutable row counts and evidence identities for read-side-effect proof."""
    names = ("tariff_assessments", "billing_eligibility", "billing_profiles", "billing_bindings", "client_invoices", "issuance")
    snapshot: dict[str, tuple[int, tuple[str, ...]]] = {}
    for name in names:
        rows = list(database.get_collection(name).find({"tenant_id": tenant}))
        identities = tuple(sorted(str(row.get("evidence_identity", row.get("fingerprint", ""))) for row in rows))
        snapshot[name] = (len(rows), identities)
    return snapshot


def test_real_mongo_canonical_billing_reads_are_exact_and_side_effect_free(mongo: tuple[MongoClient, Any]) -> None:
    client, database = mongo
    sources = _seed_sources(client, database, tenant="tenant-l7c", prefix="l7c")
    _seed_iam(database, principal_id="l7c-principal", tenant=sources["tenant"], business_role="tenant_legal_partner", granting_role="LEGAL_PARTNER")
    invoices = database.get_collection("client_invoices")
    issuance = database.get_collection("issuance")
    invoice, evidence = _issue(client, sources, invoices, issuance, clock=lambda: BASE + timedelta(hours=1))
    assessment = sources["assessments"].find_one({"tenant_id": sources["tenant"], "entity_type": "TariffAssessment"})
    eligibility = sources["eligibility"].find_one({"tenant_id": sources["tenant"], "entity_type": "ProcessServiceBillingEligibility"})
    assert assessment is not None and eligibility is not None
    before = _tenant_snapshot(database, sources["tenant"])
    headers = {"X-Tenant-ID": sources["tenant"]}
    with TestClient(_app(database, sources["tenant"], "l7c-principal")) as http:
        assessment_response = http.get(f"/api/legal-operations/tariff-assessments/{assessment['entity_identity']}", headers=headers)
        eligibility_response = http.get(f"/api/legal-operations/billing-eligibilities/{eligibility['entity_identity']}", headers=headers)
        invoice_response = http.get(f"/api/legal-operations/invoices/{invoice.invoice_id}", headers=headers)
    with TestClient(_app(database, "tenant-foreign", "l7c-principal")) as foreign_http:
        foreign_response = foreign_http.get(f"/api/legal-operations/invoices/{invoice.invoice_id}", headers={"X-Tenant-ID": "tenant-foreign"})
    assert assessment_response.status_code == 200
    assert eligibility_response.status_code == 200
    assert invoice_response.status_code == 200
    assert foreign_response.status_code == 403
    assert invoice.invoice_id not in foreign_response.text
    assert set(assessment_response.json()["data"]) == {
        "tariff_assessment_id", "return_id", "service_execution_id", "attempt_id", "instruction_id",
        "document_id", "district_id", "jurisdiction_code", "sheriff_office_id", "service_outcome",
        "tariff_schedule_id", "tariff_version_id", "fee_lines", "currency", "assessed_total_minor_units", "assessment_at",
    }
    assert set(eligibility_response.json()["data"]) == {
        "billing_eligibility_id", "tariff_assessment_id", "return_id", "service_execution_id", "attempt_id",
        "instruction_id", "document_id", "district_id", "jurisdiction_code", "sheriff_office_id", "service_outcome",
        "tariff_schedule_id", "tariff_version_id", "currency", "eligible_minor_units", "eligibility_at",
    }
    invoice_data = invoice_response.json()["data"]
    assert set(invoice_data) == {
        "invoice_id", "customer_id", "customer_name", "currency", "exact_money_lines", "subtotal_minor",
        "tax_amount_minor", "total_minor", "tax_type", "payment_terms_days", "collection_method", "issued_at",
        "due_at", "billing_eligibility_id", "tariff_assessment_id", "return_id", "service_execution_id", "attempt_id",
        "instruction_id", "document_id", "district_id", "jurisdiction_code", "sheriff_office_id",
    }
    assert invoice_data["total_minor"] == evidence.total_minor
    assert isinstance(invoice_data["total_minor"], int)
    assert type(invoice_data["payment_terms_days"]) is int
    assert invoice_data["payment_terms_days"] == 14
    assert "customer_email" not in invoice_data and "customer_tax_id" not in invoice_data
    assert not any(key in invoice_data for key in ("payment", "settlement", "paid_state", "refund", "invoice_payment", "billing_execution"))
    after = _tenant_snapshot(database, sources["tenant"])
    assert after == before

    eligibility_row = database.get_collection("billing_eligibility").find_one({"tenant_id": sources["tenant"], "entity_identity": eligibility["entity_identity"]})
    assert eligibility_row is not None
    database.get_collection("billing_eligibility").update_one({"_id": eligibility_row["_id"]}, {"$set": {"fingerprint": "c" * 128}})
    try:
        with TestClient(_app(database, sources["tenant"], "l7c-principal")) as http:
            assert http.get(f"/api/legal-operations/billing-eligibilities/{eligibility['entity_identity']}", headers=headers).status_code == 503
    finally:
        database.get_collection("billing_eligibility").replace_one({"_id": eligibility_row["_id"]}, eligibility_row)

    issuance_row = issuance.find_one({"tenant_id": sources["tenant"], "payload.invoice_id": invoice.invoice_id})
    assert issuance_row is not None
    issuance.delete_one({"_id": issuance_row["_id"]})
    try:
        with TestClient(_app(database, sources["tenant"], "l7c-principal")) as http:
            assert http.get(f"/api/legal-operations/invoices/{invoice.invoice_id}", headers=headers).status_code == 503
    finally:
        issuance.insert_one(issuance_row)

    negative_cases = (
        ("revoked-principal", "tenant_legal_partner", "LEGAL_PARTNER", PrincipalStatus.ACTIVE, TenantMembershipStatus.ACTIVE, RoleAssignmentStatus.REVOKED),
        ("inactive-principal", "tenant_legal_partner", "LEGAL_PARTNER", PrincipalStatus.SUSPENDED, TenantMembershipStatus.ACTIVE, RoleAssignmentStatus.ACTIVE),
        ("inactive-membership", "tenant_legal_partner", "LEGAL_PARTNER", PrincipalStatus.ACTIVE, TenantMembershipStatus.SUSPENDED, RoleAssignmentStatus.ACTIVE),
        ("legal-client", "tenant_legal_client", "LEGAL_CLIENT", PrincipalStatus.ACTIVE, TenantMembershipStatus.ACTIVE, RoleAssignmentStatus.ACTIVE),
        ("least-authority", "tenant_sheriff", "SHERIFF", PrincipalStatus.ACTIVE, TenantMembershipStatus.ACTIVE, RoleAssignmentStatus.ACTIVE),
    )
    for principal_id, business_role, granting_role, principal_status, membership_status, granting_status in negative_cases:
        _seed_iam(database, principal_id=principal_id, tenant=sources["tenant"], business_role=business_role, granting_role=granting_role, principal_status=principal_status, membership_status=membership_status, granting_status=granting_status)
        with TestClient(_app(database, sources["tenant"], principal_id)) as denied_http:
            denied = denied_http.get(f"/api/legal-operations/invoices/{invoice.invoice_id}", headers=headers)
        assert denied.status_code == 403
        assert invoice.invoice_id not in denied.text
    assert _tenant_snapshot(database, sources["tenant"]) == before


# ARTIFACT: test_legal_operations_billing_read_real_mongo.py
# VERSION: v1.1.0-L7C-LIVE-IAM-BILLING-READ-RM-CERT
# AUTHORITY BOUNDARY: host GET projection certificate only; no issuance/payment.
# TENANT POSTURE: isolated database and exact authorized tenant predicates.
# FAIL-CLOSED POSTURE: only pre-hello availability may skip.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
