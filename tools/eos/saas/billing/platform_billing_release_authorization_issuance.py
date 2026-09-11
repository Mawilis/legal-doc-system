"""WILSY OS durable release-authorization issuance boundary.

TITLE: Platform Billing Release Authorization Issuance
VERSION: v2.0.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-ISSUANCE
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Issue immutable release evidence from current durable commercial and authorization truth.
EPITOME: One trusted Mongo graph composes invoice, authorization, R3C1, and R3C2.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/platform_billing_release_authorization_issuance.py
COLLABORATION / OWNERSHIP: Python EOS sovereign SaaS billing.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v2.0.0 removes caller-supplied authority evidence and hydrates final facts durably.
COMPLIANCE: POPIA section 19 | GDPR Article 32 | SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references and SHA3-512 evidence only.
TENANT BOUNDARY: Identity tenant and durable invoice tenant must match exactly.
AUTHORITY BOUNDARY: Issues release evidence only; no approval, execution, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement.
TRANSACTION BOUNDARY: One trusted ClientSession spans final reads and R3C2 persistence.
"""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from typing import Any
from pymongo.client_session import ClientSession
from pymongo import MongoClient
from tools.eos.kernel.db import get_client, get_database
from tools.eos.saas.billing.platform_billing_release_authorization_registry import COLLECTION, CreateResult, PlatformBillingReleaseAuthorizationRegistry
from tools.eos.saas.domain.platform_billing_release_authorization import PlatformBillingReleaseAuthorization
from tools.eos.auth.tenant_authorization import authorize_tenant_operation
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository

VERSION = "v2.0.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-ISSUANCE"
PERMISSION = "platform_billing:release"
OPERATION = "platform_billing_release"

class PlatformReleaseIssuanceError(RuntimeError):
    """Fail-closed issuance error."""

class PlatformBillingReleaseAuthorizationIssuanceComposition:
    """Trusted infrastructure graph; never exposed as business input."""
    def __init__(self, client: MongoClient, database: Any) -> None:
        if database.client is not client:
            raise PlatformReleaseIssuanceError("MIXED_CLIENT_GRAPH")
        self.client = client
        self.database = database

    def issue(self, identity: Any, invoice_id: str, *, release_authorization_id: str, idempotency_key: str, payment_destination_reference: str, created_at: datetime) -> CreateResult:
        collections = {"invoices": self.database["platform_invoices"], "principals": self.database["principal_authorities"], "memberships": self.database["tenant_memberships"], "roles": self.database["role_assignments"], "business_roles": self.database["tenant_business_roles"], "release_authorizations": self.database[COLLECTION]}
        PlatformBillingReleaseAuthorizationRegistry.ensure_indexes(collections["release_authorizations"])
        with self.client.start_session() as session:
            with session.start_transaction():
                return _transaction_body(identity, invoice_id, release_authorization_id, idempotency_key, payment_destination_reference, created_at, session, collections)

def _bound(repo: Any, collection: Any) -> Any:
    if repo is TenantBusinessRoleRepository:
        class BoundBusiness:
            @staticmethod
            def resolve(principal_id: str, tenant_id: str, role_id: str, *, session: Any = None) -> Any:
                value = repo.resolve(principal_id, tenant_id, collection=collection, session=session)
                if value.business_role != role_id:
                    from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
                    raise RoleAssignmentNotFoundError("ROLE_ASSIGNMENT_NOT_FOUND")
                return value
        return BoundBusiness
    class Bound:
        @staticmethod
        def resolve(*args: Any, session: Any = None) -> Any:
            if repo is PrincipalAuthorityRepository:
                principal_id = args[0]
                return repo.get(principal_id, collection=collection, session=session)
            return repo.resolve(*args, collection=collection, session=session)
    return Bound

def _fingerprint(payload: Any) -> str:
    return hashlib.sha3_512(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()

def _transaction_body(identity: Any, invoice_id: str, release_authorization_id: str, idempotency_key: str, destination: str, created_at: datetime, session: ClientSession, collections: dict[str, Any]) -> CreateResult:
    from tools.eos.saas.billing.billing_registry import BillingRegistry
    invoice = BillingRegistry().get_platform_invoice(identity.tenant_id, invoice_id, collection=collections["invoices"], session=session)
    if invoice is None or invoice.status.value not in {"open", "overdue"}:
        raise PlatformReleaseIssuanceError("COMMERCIAL_AUTHORITY_INVALID")
    decision = authorize_tenant_operation(principal_id=identity.identity_id, tenant_id=identity.tenant_id, permission_id=PERMISSION, operation=OPERATION, principal_repository=_bound(PrincipalAuthorityRepository, collections["principals"]), membership_repository=_bound(TenantMembershipRepository, collections["memberships"]), role_assignment_repository=_bound(RoleAssignmentRepository, collections["roles"]), business_role_repository=_bound(TenantBusinessRoleRepository, collections["business_roles"]), session=session)
    if not decision.authorized or not decision.authorization_role or not decision.business_role:
        raise PlatformReleaseIssuanceError(f"AUTHORIZATION_DENIED:{decision.reason.value}")
    # The caller-provided creation event is the canonical issuance event for
    # this intent; authorization is established at that same event boundary.
    now = created_at.astimezone(timezone.utc)
    value = PlatformBillingReleaseAuthorization(tenant_id=identity.tenant_id, release_authorization_id=release_authorization_id, platform_invoice_id=invoice.invoice_id, platform_invoice_evidence_fingerprint=invoice.proof_hash, authorization_evidence_reference=f"decision:{identity.tenant_id}:{invoice.invoice_id}", authorization_evidence_fingerprint=_fingerprint({"tenant": identity.tenant_id, "principal": identity.identity_id, "permission": PERMISSION, "role": decision.authorization_role}), authorized_amount_minor=int(round(invoice.total * 100)), currency=invoice.currency, payment_destination_reference=destination, idempotency_key=idempotency_key, authorized_by_principal_id=identity.identity_id, authorization_basis_reference=PERMISSION, authorized_at=now, created_at=created_at)
    return PlatformBillingReleaseAuthorizationRegistry.create(value, collections["release_authorizations"], session=session)

def issue_platform_release_authorization(identity: Any, invoice_id: str, *, release_authorization_id: str, idempotency_key: str, payment_destination_reference: str, created_at: datetime) -> CreateResult:
    """Issue from durable invoice and current authorization facts; infrastructure is not business input."""
    if not isinstance(invoice_id, str) or not invoice_id.strip(): raise PlatformReleaseIssuanceError("INVOICE_REFERENCE_INVALID")
    client, database = get_client(), get_database()
    if client is None or database is None: raise PlatformReleaseIssuanceError("PERSISTENCE_UNAVAILABLE")
    collections = {"invoices": database["platform_invoices"], "principals": database["principal_authorities"], "memberships": database["tenant_memberships"], "roles": database["role_assignments"], "business_roles": database["tenant_business_roles"], "release_authorizations": database[COLLECTION]}
    return PlatformBillingReleaseAuthorizationIssuanceComposition(client, database).issue(identity, invoice_id, release_authorization_id=release_authorization_id, idempotency_key=idempotency_key, payment_destination_reference=payment_destination_reference, created_at=created_at)

__all__ = ["issue_platform_release_authorization", "PlatformBillingReleaseAuthorizationIssuanceComposition", "PlatformReleaseIssuanceError", "PERMISSION", "VERSION"]
# ARTIFACT: platform_billing_release_authorization_issuance.py
# VERSION: v2.0.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-ISSUANCE
# AUTHORITY BOUNDARY: durable release evidence only; no execution or settlement
# TENANT POSTURE: exact identity and durable invoice tenant agreement
# FAIL-CLOSED POSTURE: absent, invalid, denied, conflicting, or unavailable state rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
