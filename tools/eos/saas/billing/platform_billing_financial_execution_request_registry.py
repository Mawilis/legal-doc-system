"""TITLE: Platform Billing Financial Execution Request Registry
VERSION: v1.0.0-PLATFORM-BILLING-FINANCIAL-EXECUTION-REQUEST-REGISTRY
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Persist immutable tenant-scoped R3D intent.
EPITOME: Durable idempotency without execution authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/platform_billing_financial_execution_request_registry.py
COLLABORATION / OWNERSHIP: R3D durable registry owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 establishes explicit indexes and conflict law.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped exact-key persistence.
TENANT BOUNDARY: All keys include tenant_id.
AUTHORITY BOUNDARY: Registry never grants authority.
FINANCIAL AUTHORITY BOUNDARY: No provider, Kennel, settlement, or paid mutation.
TRANSACTION BOUNDARY: Caller supplies session; DDL occurs before transactions.
FAIL-CLOSED POSTURE: Material conflicts and duplicate races raise typed errors.
"""
from __future__ import annotations
from typing import Any, Optional
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import DuplicateKeyError
from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest

COLLECTION = "platform_billing_financial_execution_requests"
class PlatformBillingFinancialExecutionRequestConflictError(RuntimeError): pass

class PlatformBillingFinancialExecutionRequestRegistry:
    @staticmethod
    def ensure_indexes(collection: Collection) -> None:
        collection.create_index([("tenant_id", 1), ("execution_request_id", 1)], unique=True)
        collection.create_index([("tenant_id", 1), ("idempotency_key", 1)], unique=True)
    @staticmethod
    def create(value: PlatformBillingFinancialExecutionRequest, collection: Collection, *, session: Optional[ClientSession] = None) -> tuple[PlatformBillingFinancialExecutionRequest, bool]:
        document = {**value.__dict__, "requested_at": value.requested_at, "request_fingerprint": value.fingerprint}
        existing = collection.find_one({"tenant_id": value.tenant_id, "idempotency_key": value.idempotency_key}, session=session)
        if existing is not None:
            if existing.get("request_fingerprint") == value.fingerprint:
                return value, True
            raise PlatformBillingFinancialExecutionRequestConflictError("PLATFORM_BILLING_EXECUTION_REQUEST_IDEMPOTENCY_CONFLICT")
        try:
            collection.insert_one(document, session=session); return value, False
        except DuplicateKeyError as error:
            raise PlatformBillingFinancialExecutionRequestConflictError("PLATFORM_BILLING_EXECUTION_REQUEST_IDEMPOTENCY_CONFLICT") from error

# ARTIFACT: platform_billing_financial_execution_request_registry.py
# VERSION: v1.0.0-PLATFORM-BILLING-FINANCIAL-EXECUTION-REQUEST-REGISTRY
# AUTHORITY BOUNDARY: durable intent only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
