"""WILSY OS governed platform release-authorization real-Mongo certificate.

TITLE: R3C3 M3T Distinct Real-Mongo Scenario Certificate
VERSION: v1.1.0-PLATFORM-RELEASE-ISSUANCE-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify six distinct durable issuance and rollback scenarios.
EPITOME: Real Mongo evidence for commercial, authorization, idempotency, and transaction boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_platform_billing_release_authorization_issuance_real_mongo.py
COLLABORATION / OWNERSHIP: Python EOS billing integration certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.1.0 replaces duplicated happy paths with six governed scenarios.
COMPLIANCE: POPIA section 19 | GDPR Article 32 | SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identifiers, opaque destinations, bounded cleanup.
TENANT BOUNDARY: Every durable query and fixture is tenant scoped.
AUTHORITY BOUNDARY: Release evidence only; no approval, execution, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
TRANSACTION BOUNDARY: One governed client graph and caller-owned Mongo sessions.
FAIL-CLOSED POSTURE: Missing, denied, invalid, conflicting, or unavailable state fails certification.
"""
from __future__ import annotations
import os
from datetime import datetime, timezone
from pymongo import MongoClient
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.saas.billing.platform_billing_release_authorization_issuance import PlatformBillingReleaseAuthorizationIssuanceComposition, _transaction_body
from tools.eos.saas.billing.platform_billing_release_authorization_registry import PlatformBillingReleaseAuthorizationRegistry, PlatformBillingReleaseAuthorizationIdempotencyConflictError

URI = os.getenv("TEST_VENDOR_MONGO_URI", "")

def _run(case: int) -> None:
    if not URI:
        raise RuntimeError("TEST_VENDOR_MONGO_URI is required for real-Mongo certification")
    client = MongoClient(URI, serverSelectionTimeoutMS=2000, retryWrites=True); client.admin.command("ping")
    db = client["wilsy_r3c3_m3t"]; now = datetime.now(timezone.utc)
    tenant, principal, invoice = (f"{p}-{os.urandom(8).hex()}" for p in ("T", "P", "I"))
    pc, mc, rc, bc, ic, ac = (db[n] for n in ("principal_authorities", "tenant_memberships", "role_assignments", "tenant_business_roles", "platform_invoices", "platform_billing_release_authorizations"))
    PrincipalAuthorityRepository.create(PrincipalAuthority(principal, PrincipalStatus.ACTIVE, 0), collection=pc)
    TenantMembershipRepository.insert(TenantMembershipAuthority(principal, tenant, TenantMembershipStatus.ACTIVE, 0), collection=mc)
    if case != 2: RoleAssignmentRepository.insert(RoleAssignmentAuthority(principal, tenant, "ENTERPRISE_ADMIN", RoleAssignmentStatus.REVOKED if case == 3 else RoleAssignmentStatus.ACTIVE, 0), collection=rc)
    TenantBusinessRoleRepository.insert(TenantBusinessRoleAuthority(principal, tenant, "tenant_owner", TenantBusinessRoleStatus.ACTIVE, 0, now, None), collection=bc)
    ic.insert_one({"tenant_id": tenant, "invoice_id": invoice, "status": "void" if case == 4 else "open", "amount": 100.0, "total": 100.0, "tax_amount": 0.0, "currency": "ZAR", "line_items": [], "issued_at": now, "proof_hash": "a" * 128})
    identity = SovereignIdentity(identity_id=principal, tenant_id=tenant, username=None, email=None, auth_method="certificate", status=PrincipalStatus.ACTIVE)
    rid, key = f"R-{os.urandom(8).hex()}", f"K-{os.urandom(8).hex()}"
    try:
        if case in (1, 5, 6):
            preflight = TenantBusinessRoleRepository.resolve(principal, tenant, collection=bc)
            assert preflight.principal_id == principal and preflight.tenant_id == tenant and preflight.status is TenantBusinessRoleStatus.ACTIVE
        composition = PlatformBillingReleaseAuthorizationIssuanceComposition(client, db)
        if case in (2, 3, 4):
            try: composition.issue(identity, invoice, release_authorization_id=rid, idempotency_key=key, payment_destination_reference="opaque-destination", created_at=now)
            except Exception: pass
            assert ac.find_one({"tenant_id": tenant}) is None
        elif case == 5:
            first = composition.issue(identity, invoice, release_authorization_id=rid, idempotency_key=key, payment_destination_reference="opaque-destination", created_at=now)
            retry = composition.issue(identity, invoice, release_authorization_id=rid, idempotency_key=key, payment_destination_reference="opaque-destination", created_at=now)
            assert retry.replayed
            try: composition.issue(identity, invoice, release_authorization_id=rid, idempotency_key=key, payment_destination_reference="different-destination", created_at=now)
            except PlatformBillingReleaseAuthorizationIdempotencyConflictError: pass
            else: raise AssertionError("idempotency conflict not enforced")
            assert PlatformBillingReleaseAuthorizationRegistry.get(tenant, rid, collection=ac).release_authorization_fingerprint == first.authorization.release_authorization_fingerprint
        elif case == 6:
            collections = {"invoices": ic, "principals": pc, "memberships": mc, "roles": rc, "business_roles": bc, "release_authorizations": ac}
            with client.start_session() as session:
                with session.start_transaction():
                    assert _transaction_body(identity, invoice, rid, key, "opaque-destination", now, session, collections).authorization.tenant_id == tenant
                    session.abort_transaction()
            assert ac.find_one({"tenant_id": tenant}) is None
        else:
            result = composition.issue(identity, invoice, release_authorization_id=rid, idempotency_key=key, payment_destination_reference="opaque-destination", created_at=now)
            assert PlatformBillingReleaseAuthorizationRegistry.get(tenant, rid, collection=ac).release_authorization_fingerprint == result.authorization.release_authorization_fingerprint
    finally:
        for collection, query in ((ac,{"tenant_id":tenant}), (ic,{"tenant_id":tenant}), (bc,{"tenant_id":tenant}), (rc,{"tenant_id":tenant}), (mc,{"tenant_id":tenant}), (pc,{"principal_id":principal})): collection.delete_one(query)
        client.close()

def test_rm_r3c3_1_happy() -> None: _run(1)
def test_rm_r3c3_2_authority_firewall() -> None: _run(2)
def test_rm_r3c3_3_authorization_absent() -> None: _run(3)
def test_rm_r3c3_4_commercial_invalid() -> None: _run(4)
def test_rm_r3c3_5_idempotency_conflict() -> None: _run(5)
def test_rm_r3c3_6_real_rollback() -> None: _run(6)

# ARTIFACT: test_platform_billing_release_authorization_issuance_real_mongo.py
# VERSION: v1.1.0-PLATFORM-RELEASE-ISSUANCE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: durable release evidence only; no execution or settlement
# TENANT POSTURE: synthetic tenant-isolated records and bounded delete_one cleanup
# FAIL-CLOSED POSTURE: unavailable governed Mongo is an environment failure
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
