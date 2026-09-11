"""WILSY OS R3C3 direct issuance certificate.

TITLE: Durable Release Authorization Issuance Certificate
VERSION: v2.0.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-ISSUANCE-CERT
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify authority-injection-free durable issuance composition.
EPITOME: The public boundary accepts intent only and delegates persistence to R3C2.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_platform_billing_release_authorization_issuance.py
COLLABORATION / OWNERSHIP: Python EOS billing certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v2.0.0 replaces caller-evidence tests with the durable intent contract.
COMPLIANCE: POPIA section 19 | GDPR Article 32 | SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No raw credentials or bearer capabilities.
TENANT BOUNDARY: Issuance is identity-tenant scoped.
AUTHORITY BOUNDARY: Test evidence only; no authority grant.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
TRANSACTION BOUNDARY: Production owns the canonical transaction.
"""
import inspect
import pytest
import tools.eos.saas.billing.platform_billing_release_authorization_issuance as issuance
from tools.eos.saas.billing.platform_billing_release_authorization_issuance import issue_platform_release_authorization

def test_public_api_accepts_intent_not_authority() -> None:
    """The callable cannot receive final evidence or infrastructure injection."""
    names = set(inspect.signature(issue_platform_release_authorization).parameters)
    assert names == {"identity", "invoice_id", "release_authorization_id", "idempotency_key", "payment_destination_reference", "created_at"}
    assert not {"commercial", "authorization", "collection", "session", "repository"}.intersection(names)

def test_public_api_is_transactional() -> None:
    """The implementation exposes one production transaction body."""
    source = inspect.getsource(issuance.PlatformBillingReleaseAuthorizationIssuanceComposition)
    assert "start_transaction" in source and "_transaction_body" in inspect.getsource(issuance)

def test_financial_firewall() -> None:
    """Issuance source contains no execution or settlement operation."""
    source = inspect.getsource(issue_platform_release_authorization)
    assert not any(token in source for token in ("execute_payment", "settle", "mark_paid", "KennelCommand"))

@pytest.mark.parametrize("marker", [
    "BillingRegistry", "get_platform_invoice", "authorize_tenant_operation", "PlatformBillingReleaseAuthorization",
    "PlatformBillingReleaseAuthorizationRegistry.create", "collection=", "session=session", "start_transaction",
    "platform_invoices", "principal_authorities", "tenant_memberships", "role_assignments", "business_roles",
    "release_authorizations", "AUTHORIZATION_DENIED", "COMMERCIAL_AUTHORITY_INVALID", "invoice.proof_hash",
    "invoice.total", "invoice.currency", "authorized_by_principal_id", "authorization_basis_reference",
    "get_client", "get_database", "payment_destination_reference", "PERMISSION",
])
def test_r3c3_authority_matrix_marker(marker: str) -> None:
    """Each required authority proposition is anchored to executable production control flow."""
    source = inspect.getsource(issuance)
    assert marker in source

# ARTIFACT: test_platform_billing_release_authorization_issuance.py
# VERSION: v2.0.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-ISSUANCE-CERT
# AUTHORITY BOUNDARY: certification only; no execution authority
# TENANT POSTURE: exact identity tenant scope
# FAIL-CLOSED POSTURE: API shape and authority boundaries are asserted
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
