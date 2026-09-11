"""TITLE: Vendor Bill Financial Execution Request Issuance.
VERSION: v1.0.0-M11-P5-R1B-AP2A.
AUTHORITY: Wilsy OS Core Governance / SaaS AP.
EPITOME: Caller-owned transactional AP request issuance.
ABSOLUTE CANONICAL PATH: tools/eos/saas/billing/vendor_bill_financial_execution_request_issuance.py
COLLABORATION / OWNERSHIP: AP release-to-request orchestration.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes release-correlated durable AP requests.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Release and request identities are exact tenant scope.
AUTHORITY BOUNDARY: Request only; no provider selection or execution.
"""
from datetime import datetime
from typing import Any
from tools.eos.saas.domain.vendor_bill_financial_execution_request import VendorBillFinancialExecutionRequest
from tools.eos.saas.billing.vendor_bill_financial_execution_request_registry import VendorBillFinancialExecutionRequestRegistry
from tools.eos.saas.billing.vendor_bill_release_authorization_registry import VendorBillReleaseAuthorizationRegistry

def issue_vendor_bill_financial_execution_request(tenant_id: str, release_authorization_id: str, *, execution_command_id: str, idempotency_key: str, amount_minor: int, currency: str, payment_destination_reference: str, payable_id: str, requested_by_actor_id: str, requested_at: datetime, collection: Any, release_collection: Any, session: Any = None) -> tuple[VendorBillFinancialExecutionRequest, bool]:
    """Create a durable AP request after exact release-authority validation."""
    if session is None or getattr(session,"in_transaction",False) is not True: raise RuntimeError("ACTIVE_TRANSACTION_REQUIRED")
    release=VendorBillReleaseAuthorizationRegistry.get(tenant_id,release_authorization_id,release_collection,session=session)
    if release.payable_id!=payable_id or release.currency!=currency or amount_minor>release.authorized_amount_minor: raise RuntimeError("RELEASE_SCOPE_MISMATCH")
    value=VendorBillFinancialExecutionRequest(execution_command_id,tenant_id,payable_id,release_authorization_id,idempotency_key,amount_minor,currency,payment_destination_reference,requested_by_actor_id,requested_at)
    return VendorBillFinancialExecutionRequestRegistry.create(value,collection,session=session)

# ARTIFACT: vendor_bill_financial_execution_request_issuance.py
# VERSION: v1.0.0-M11-P5-R1B-AP2A
# AUTHORITY BOUNDARY: AP request evidence only
# FAIL-CLOSED POSTURE: missing or mismatched release rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
