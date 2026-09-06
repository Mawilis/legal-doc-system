"""TITLE: Kennel Platform Billing Financial Execution Command
VERSION: v1.0.0-KENNEL-PLATFORM-BILLING-FINANCIAL-EXECUTION-COMMAND
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Preserve platform R3D authority before later provider execution.
EPITOME: Distinct Kennel command; never AP payable provenance.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/domain/platform_billing_financial_execution_command.py
COLLABORATION / OWNERSHIP: Kennel EOS command domain owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 establishes immutable platform command material.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque destination references only.
TENANT BOUNDARY: All command identity is tenant-bound.
AUTHORITY BOUNDARY: Derived exclusively from durable R3D.
FINANCIAL AUTHORITY BOUNDARY: No provider execution, settlement, or paid state.
TRANSACTION BOUNDARY: Pure value object; no persistence ownership.
FAIL-CLOSED POSTURE: Invalid command material is rejected.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import hashlib, json, re
from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest

class PlatformBillingFinancialExecutionCommandError(ValueError):
    """Malformed platform command material."""

@dataclass(frozen=True)
class PlatformBillingFinancialExecutionCommand:
    tenant_id: str
    execution_command_id: str
    execution_request_id: str
    release_authorization_id: str
    platform_invoice_id: str
    release_authorization_fingerprint: str
    amount_minor: int
    currency: str
    payment_destination_reference: str
    idempotency_key: str
    requested_by_principal_id: str
    authorization_basis_reference: str
    created_at: datetime

    def __post_init__(self) -> None:
        for name in ("tenant_id", "execution_command_id", "execution_request_id", "release_authorization_id", "platform_invoice_id", "payment_destination_reference", "idempotency_key", "requested_by_principal_id", "authorization_basis_reference"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip(): raise PlatformBillingFinancialExecutionCommandError(f"{name} is invalid")
        if not isinstance(self.release_authorization_fingerprint, str) or re.fullmatch(r"[0-9a-f]{128}", self.release_authorization_fingerprint) is None: raise PlatformBillingFinancialExecutionCommandError("fingerprint is invalid")
        if not isinstance(self.amount_minor, int) or isinstance(self.amount_minor, bool) or self.amount_minor <= 0: raise PlatformBillingFinancialExecutionCommandError("amount is invalid")
        if not isinstance(self.currency, str) or re.fullmatch(r"[A-Z]{3}", self.currency) is None: raise PlatformBillingFinancialExecutionCommandError("currency is invalid")
        if not isinstance(self.created_at, datetime) or self.created_at.tzinfo is None: raise PlatformBillingFinancialExecutionCommandError("created_at is invalid")

    @classmethod
    def from_request(cls, request: PlatformBillingFinancialExecutionRequest, *, created_at: datetime) -> "PlatformBillingFinancialExecutionCommand":
        if not isinstance(request, PlatformBillingFinancialExecutionRequest): raise PlatformBillingFinancialExecutionCommandError("request is invalid")
        return cls(request.tenant_id, f"platform-command-{request.execution_request_id}", request.execution_request_id, request.release_authorization_id, request.platform_invoice_id, request.release_authorization_fingerprint, request.amount_minor, request.currency, request.payment_destination_reference, request.idempotency_key, request.requested_by_principal_id, request.authorization_basis_reference, created_at)

    @property
    def fingerprint(self) -> str:
        payload = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in self.__dict__.items()}
        return hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

# ARTIFACT: platform_billing_financial_execution_command.py
# VERSION: v1.0.0-KENNEL-PLATFORM-BILLING-FINANCIAL-EXECUTION-COMMAND
# AUTHORITY BOUNDARY: Kennel command authority only; no provider execution.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
