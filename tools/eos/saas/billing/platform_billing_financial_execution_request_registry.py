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
import hmac
from datetime import datetime, timezone
from typing import Any, Optional
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import DuplicateKeyError
from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest

COLLECTION = "platform_billing_financial_execution_requests"
class PlatformBillingFinancialExecutionRequestConflictError(RuntimeError): pass
class PlatformBillingFinancialExecutionRequestNotFoundError(RuntimeError): pass
class PlatformBillingFinancialExecutionRequestPersistedRecordInvalidError(RuntimeError): pass

class PlatformBillingFinancialExecutionRequestRegistry:
    @staticmethod
    def ensure_indexes(collection: Collection) -> None:
        collection.create_index([("tenant_id", 1), ("execution_request_id", 1)], unique=True)
        collection.create_index([("tenant_id", 1), ("idempotency_key", 1)], unique=True)
    @staticmethod
    def _hydrate(document: dict[str, Any]) -> PlatformBillingFinancialExecutionRequest:
        try:
            body = dict(document); body.pop("_id", None)
            required = ("provider_policy_runtime_binding_id", "provider_policy_runtime_binding_fingerprint", "provider_policy_id", "provider_policy_revision", "provider_policy_fingerprint")
            if any(field not in body for field in required): raise ValueError("missing policy provenance")
            stored = body.pop("request_fingerprint")
            requested_at = body.get("requested_at")
            if isinstance(requested_at, datetime) and requested_at.tzinfo is None:
                body["requested_at"] = requested_at.replace(tzinfo=timezone.utc)
            value = PlatformBillingFinancialExecutionRequest(**body)
            if not isinstance(stored, str) or not hmac.compare_digest(stored, value.fingerprint):
                raise ValueError("fingerprint")
            return value
        except (KeyError, TypeError, ValueError) as error:
            raise PlatformBillingFinancialExecutionRequestPersistedRecordInvalidError("PLATFORM_BILLING_EXECUTION_REQUEST_PERSISTED_RECORD_INVALID") from error
    @staticmethod
    def get(tenant_id: str, execution_request_id: str, collection: Collection, *, session: Optional[ClientSession] = None) -> PlatformBillingFinancialExecutionRequest:
        if not isinstance(tenant_id, str) or not tenant_id.strip() or not isinstance(execution_request_id, str) or not execution_request_id.strip():
            raise PlatformBillingFinancialExecutionRequestNotFoundError("PLATFORM_BILLING_EXECUTION_REQUEST_NOT_FOUND")
        document = collection.find_one({"tenant_id": tenant_id, "execution_request_id": execution_request_id}, session=session)
        if document is None:
            raise PlatformBillingFinancialExecutionRequestNotFoundError("PLATFORM_BILLING_EXECUTION_REQUEST_NOT_FOUND")
        return PlatformBillingFinancialExecutionRequestRegistry._hydrate(document)
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
