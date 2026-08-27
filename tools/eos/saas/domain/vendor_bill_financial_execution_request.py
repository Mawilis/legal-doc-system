"""AP-owned request boundary for handing release-authorized obligations to Kennel EOS.

VERSION: v1.0.0-VENDOR-BILL-FINANCIAL-EXECUTION-REQUEST
AUTHORITY: Wilsy OS Core Governance
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from tools.eos.kennel.orchestration.financial_execution_orchestrator import FinancialExecutionCommand
from .vendor_bill_release_authorization import VendorBillReleaseAuthorization


class VendorBillFinancialExecutionRequestError(ValueError):
    """Raised when AP execution-request evidence is invalid or out of scope."""


@dataclass(frozen=True)
class VendorBillFinancialExecutionRequest:
    """Immutable AP request that validates release scope and builds a Kennel command."""

    execution_command_id: str
    tenant_id: str
    payable_id: str
    release_authorization_id: str
    idempotency_key: str
    amount_minor: int
    currency: str
    payment_destination_reference: str
    requested_by_actor_id: str
    requested_at: datetime

    def __post_init__(self) -> None:
        for name in ("execution_command_id", "tenant_id", "payable_id", "release_authorization_id", "idempotency_key", "payment_destination_reference", "requested_by_actor_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise VendorBillFinancialExecutionRequestError(f"{name} is invalid")
        if not isinstance(self.amount_minor, int) or isinstance(self.amount_minor, bool) or self.amount_minor <= 0:
            raise VendorBillFinancialExecutionRequestError("amount_minor is invalid")
        if not isinstance(self.currency, str) or re.fullmatch(r"[A-Z]{3}", self.currency) is None:
            raise VendorBillFinancialExecutionRequestError("currency is invalid")
        if not isinstance(self.payment_destination_reference, str) or re.search(r"bank|account|card|secret|token|credential|password", self.payment_destination_reference, re.I):
            raise VendorBillFinancialExecutionRequestError("payment destination must be opaque")
        if not isinstance(self.requested_at, datetime) or self.requested_at.tzinfo is None:
            raise VendorBillFinancialExecutionRequestError("requested_at is invalid")

    def to_financial_execution_command(self, authorization: VendorBillReleaseAuthorization) -> FinancialExecutionCommand:
        """Validate AP release scope and construct the canonical Kennel command without I/O."""
        if not isinstance(authorization, VendorBillReleaseAuthorization):
            raise VendorBillFinancialExecutionRequestError("authorization is invalid")
        if (self.tenant_id != authorization.tenant_id or self.payable_id != authorization.payable_id or self.release_authorization_id != authorization.release_authorization_id or self.currency != authorization.currency or self.amount_minor > authorization.authorized_amount_minor):
            raise VendorBillFinancialExecutionRequestError("release authorization scope mismatch")
        return FinancialExecutionCommand(self.tenant_id, self.payable_id, self.release_authorization_id, self.execution_command_id, self.idempotency_key, self.amount_minor, self.currency, self.payment_destination_reference)

    @property
    def fingerprint(self) -> str:
        """Return deterministic SHA3-512 evidence for this originating request."""
        payload: dict[str, Any] = {"execution_command_id": self.execution_command_id, "tenant_id": self.tenant_id, "payable_id": self.payable_id, "release_authorization_id": self.release_authorization_id, "idempotency_key": self.idempotency_key, "amount_minor": self.amount_minor, "currency": self.currency, "payment_destination_reference": self.payment_destination_reference, "requested_by_actor_id": self.requested_by_actor_id, "requested_at": self.requested_at.isoformat()}
        return hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


# END OF WILSY OS SOVEREIGN ARTIFACT
