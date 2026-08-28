"""Immutable provider-neutral command material for Kennel execution.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-COMMAND
TITLE: Financial Execution Command Domain Authority
PURPOSE: Preserve authorized execution material before provider transport.
AUTHORITY: Immutable command instruction only; no attempt, observation, truth, or settlement authority.
EPITOME: Separates business instruction from transport lifecycle and provider outcome.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/domain/financial_execution_command.py
CERTIFICATION DATE: 2026-08-28
CHANGELOG: v1.0.0 establishes tenant-bound immutable command material compatible with synchronous command fingerprints.
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque destination and metadata references only; credentials and payloads are forbidden.
TENANT BOUNDARY: all command identities and business references are tenant-bound and immutable.
FINANCIAL AUTHORITY BOUNDARY: authorized instruction only; no execution result, settlement, ledger, or payable mutation.
TRANSACTION BOUNDARY: pure value object; no persistence or transaction lifecycle ownership.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime

VERSION = "v1.0.0-KENNEL-FINANCIAL-EXECUTION-COMMAND"
_FORBIDDEN = re.compile(r"bank|account|card|secret|token|credential|password", re.IGNORECASE)


class FinancialExecutionCommandError(ValueError):
    """Fail-closed validation error for malformed command material."""


@dataclass(frozen=True)
class FinancialExecutionCommand:
    """Immutable authorized instruction preserved before asynchronous transport."""

    tenant_id: str
    payable_id: str
    release_authorization_id: str
    execution_command_id: str
    idempotency_key: str
    amount_minor: int
    currency: str
    payment_destination_reference: str
    created_at: datetime
    provider_name: str | None = None
    provider_metadata_reference: str | None = None

    def __post_init__(self) -> None:
        for name in ("tenant_id", "payable_id", "release_authorization_id", "execution_command_id", "idempotency_key", "payment_destination_reference"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip() or _FORBIDDEN.search(value):
                raise FinancialExecutionCommandError(f"invalid {name}")
        if self.provider_name is not None and (not isinstance(self.provider_name, str) or not self.provider_name.strip()):
            raise FinancialExecutionCommandError("invalid provider_name")
        if self.provider_metadata_reference is not None and (not isinstance(self.provider_metadata_reference, str) or not self.provider_metadata_reference.strip() or _FORBIDDEN.search(self.provider_metadata_reference)):
            raise FinancialExecutionCommandError("invalid provider_metadata_reference")
        if not isinstance(self.amount_minor, int) or isinstance(self.amount_minor, bool) or self.amount_minor <= 0:
            raise FinancialExecutionCommandError("amount_minor must be positive")
        if not isinstance(self.currency, str) or re.fullmatch(r"[A-Z]{3}", self.currency) is None:
            raise FinancialExecutionCommandError("currency must be uppercase 3-letter code")
        if not isinstance(self.created_at, datetime) or self.created_at.tzinfo is None:
            raise FinancialExecutionCommandError("created_at must be timezone-aware")

    def evidence_payload(self) -> dict[str, object]:
        """Return the exact semantic payload used by the frozen synchronous command fingerprint."""
        return {
            "tenant_id": self.tenant_id,
            "payable_id": self.payable_id,
            "release_authorization_id": self.release_authorization_id,
            "execution_command_id": self.execution_command_id,
            "idempotency_key": self.idempotency_key,
            "amount_minor": self.amount_minor,
            "currency": self.currency,
            "payment_destination_reference": self.payment_destination_reference,
            "requested_provider": self.provider_name,
            "provider_metadata_reference": self.provider_metadata_reference,
        }

    @property
    def fingerprint(self) -> str:
        """Compute the deterministic SHA3-512 authorized-command fingerprint."""
        encoded = json.dumps(self.evidence_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        return hashlib.sha3_512(encoded).hexdigest()


# ARTIFACT: financial_execution_command.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-COMMAND
# AUTHORITY BOUNDARY: immutable execution instruction; no attempt, observation, truth, or settlement authority.
# TENANT POSTURE: tenant-bound identifiers and opaque references only.
# FAIL-CLOSED POSTURE: malformed identity, amount, currency, reference, or timestamp is rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS owns execution authority; this object does not execute or settle.
# END OF WILSY OS SOVEREIGN ARTIFACT
