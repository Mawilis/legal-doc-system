"""TITLE: Platform Billing Financial Execution Request Issuance
VERSION: v1.0.0-PLATFORM-BILLING-FINANCIAL-EXECUTION-REQUEST-ISSUANCE
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Compose durable R3C3-derived platform execution intent.
EPITOME: Trusted infrastructure boundary; no execution is performed.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/platform_billing_financial_execution_request_issuance.py
COLLABORATION / OWNERSHIP: R3D issuance/composition owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 establishes caller-owned transactional issuance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Caller cannot inject authority or economic facts.
TENANT BOUNDARY: Hydration and persistence are explicitly tenant-scoped.
AUTHORITY BOUNDARY: Canonical R3C3 is hydrated internally.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes funds.
TRANSACTION BOUNDARY: One caller-owned session covers durable write.
FAIL-CLOSED POSTURE: Missing or conflicting authority aborts issuance.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from pymongo import MongoClient
from tools.eos.saas.billing.platform_billing_release_authorization_registry import PlatformBillingReleaseAuthorizationRegistry
from tools.eos.saas.billing.platform_billing_financial_execution_request_registry import PlatformBillingFinancialExecutionRequestRegistry
from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest

def issue_platform_billing_financial_execution_request(client: MongoClient, database: Any, tenant_id: str, release_authorization_id: str, *, execution_request_id: str, requested_at: datetime) -> tuple[PlatformBillingFinancialExecutionRequest, bool]:
    authorization = PlatformBillingReleaseAuthorizationRegistry.get(tenant_id, release_authorization_id, collection=database["platform_billing_release_authorizations"])
    request = PlatformBillingFinancialExecutionRequest.from_release_authorization(authorization, execution_request_id, requested_at.astimezone(timezone.utc))
    collection = database["platform_billing_financial_execution_requests"]
    PlatformBillingFinancialExecutionRequestRegistry.ensure_indexes(collection)
    with client.start_session() as session:
        with session.start_transaction():
            return PlatformBillingFinancialExecutionRequestRegistry.create(request, collection, session=session)

# ARTIFACT: platform_billing_financial_execution_request_issuance.py
# VERSION: v1.0.0-PLATFORM-BILLING-FINANCIAL-EXECUTION-REQUEST-ISSUANCE
# AUTHORITY BOUNDARY: derives durable intent; no authorization or execution
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
