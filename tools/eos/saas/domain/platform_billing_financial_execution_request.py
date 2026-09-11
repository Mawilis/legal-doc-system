"""TITLE: Platform Billing Financial Execution Request
VERSION: v1.0.0-PLATFORM-BILLING-FINANCIAL-EXECUTION-REQUEST
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Durable platform billing execution intent derived from R3C3.
EPITOME: REQUEST != EXECUTION; Kennel EOS remains exclusive executor.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/platform_billing_financial_execution_request.py
COLLABORATION / OWNERSHIP: R3D platform billing domain owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 establishes immutable R3C3-derived platform intent.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque destination references; no bearer secrets.
TENANT BOUNDARY: Every request is tenant-scoped.
AUTHORITY BOUNDARY: Economic provenance derives only from durable R3C3.
FINANCIAL AUTHORITY BOUNDARY: No execution, settlement, paid, or refund truth.
TRANSACTION BOUNDARY: Persistence orchestration owns caller sessions.
FAIL-CLOSED POSTURE: Invalid or cross-domain facts are rejected.
"""
from __future__ import annotations
import hashlib, json, re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from .platform_billing_release_authorization import PlatformBillingReleaseAuthorization

class PlatformBillingFinancialExecutionRequestError(ValueError):
    """Invalid or out-of-scope platform execution request."""

@dataclass(frozen=True)
class PlatformBillingFinancialExecutionRequest:
    execution_request_id: str
    tenant_id: str
    release_authorization_id: str
    platform_invoice_id: str
    release_authorization_fingerprint: str
    amount_minor: int
    currency: str
    payment_destination_reference: str
    idempotency_key: str
    requested_by_principal_id: str
    authorization_basis_reference: str
    requested_at: datetime

    def __post_init__(self) -> None:
        for name in ("execution_request_id", "tenant_id", "release_authorization_id", "platform_invoice_id", "requested_by_principal_id", "authorization_basis_reference", "idempotency_key", "payment_destination_reference"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip(): raise PlatformBillingFinancialExecutionRequestError(f"{name} is invalid")
        if not isinstance(self.release_authorization_fingerprint, str) or re.fullmatch(r"[0-9a-f]{128}", self.release_authorization_fingerprint) is None: raise PlatformBillingFinancialExecutionRequestError("release_authorization_fingerprint is invalid")
        if not isinstance(self.amount_minor, int) or isinstance(self.amount_minor, bool) or self.amount_minor <= 0: raise PlatformBillingFinancialExecutionRequestError("amount_minor is invalid")
        if not isinstance(self.currency, str) or re.fullmatch(r"[A-Z]{3}", self.currency) is None: raise PlatformBillingFinancialExecutionRequestError("currency is invalid")
        if not isinstance(self.payment_destination_reference, str) or re.search(r"bank|account|card|secret|token|credential|password", self.payment_destination_reference, re.I): raise PlatformBillingFinancialExecutionRequestError("payment destination must be opaque")
        if not isinstance(self.requested_at, datetime) or self.requested_at.tzinfo is None: raise PlatformBillingFinancialExecutionRequestError("requested_at is invalid")
        canonical = self.requested_at.astimezone(timezone.utc).replace(microsecond=(self.requested_at.microsecond // 1000) * 1000)
        object.__setattr__(self, "requested_at", canonical)

    @classmethod
    def from_release_authorization(cls, authorization: PlatformBillingReleaseAuthorization, execution_request_id: str, requested_at: datetime) -> "PlatformBillingFinancialExecutionRequest":
        if not isinstance(authorization, PlatformBillingReleaseAuthorization): raise PlatformBillingFinancialExecutionRequestError("authorization is invalid")
        return cls(execution_request_id, authorization.tenant_id, authorization.release_authorization_id, authorization.platform_invoice_id, authorization.release_authorization_fingerprint, authorization.authorized_amount_minor, authorization.currency, authorization.payment_destination_reference, authorization.idempotency_key, authorization.authorized_by_principal_id, authorization.authorization_basis_reference, requested_at)

    @property
    def fingerprint(self) -> str:
        payload = {k: getattr(self, k).isoformat() if isinstance(getattr(self, k), datetime) else getattr(self, k) for k in self.__dataclass_fields__}
        return hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

# ARTIFACT: platform_billing_financial_execution_request.py
# VERSION: v1.0.0-PLATFORM-BILLING-FINANCIAL-EXECUTION-REQUEST
# AUTHORITY BOUNDARY: durable intent only; Kennel EOS executes
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
