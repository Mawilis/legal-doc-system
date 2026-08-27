"""WILSY OS Kennel EOS financial execution truth domain contract.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TRUTH-DOMAIN
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable, tenant-scoped execution evidence; execution never implies settlement.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/domain/financial_execution.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI engineering)
CHANGELOG: v1.0.0 establishes pure Kennel EOS execution-truth vocabulary.
COMPLIANCE: POPIA §19 | GDPR Art. 32 | SOC2 CC7.2
SECURITY / PRIVACY: destination is an opaque reference; no credentials or account data.
TENANT BOUNDARY: tenant_id and payable_id are mandatory and never inferred.
AUTHORITY BOUNDARY: release authorization is prerequisite evidence; Kennel EOS owns execution.
FINANCIAL AUTHORITY BOUNDARY: no payment, settlement, persistence, or network behavior.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, fields
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping

VERSION = "v1.0.0-KENNEL-FINANCIAL-EXECUTION-TRUTH-DOMAIN"
_HEX = re.compile(r"^[0-9a-f]{128}$")


class FinancialExecutionTruthError(ValueError):
    """Fail-closed validation error for immutable Kennel execution evidence."""


class FinancialExecutionStatus(StrEnum):
    """Provider execution status; none of these statuses represents settlement."""

    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class FinancialExecutionTruth:
    """Immutable tenant-scoped execution evidence owned by Kennel EOS."""

    execution_truth_id: str
    tenant_id: str
    payable_id: str
    release_authorization_id: str
    provider: str
    provider_execution_reference: str
    execution_status: FinancialExecutionStatus
    executed_amount_minor: int
    currency: str
    executed_at: datetime
    payment_destination_reference: str
    provider_evidence_reference: str
    execution_command_fingerprint: str
    execution_evidence_fingerprint: str
    created_at: datetime

    def __post_init__(self) -> None:
        """Validate identity, evidence, timestamps, and confidentiality boundaries."""
        for name in ("execution_truth_id", "tenant_id", "payable_id", "release_authorization_id", "provider", "provider_execution_reference", "payment_destination_reference", "provider_evidence_reference"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise FinancialExecutionTruthError(f"{name} must be non-empty")
        if not isinstance(self.execution_status, FinancialExecutionStatus):
            raise FinancialExecutionTruthError("execution_status is invalid")
        if not isinstance(self.executed_amount_minor, int) or isinstance(self.executed_amount_minor, bool) or self.executed_amount_minor <= 0:
            raise FinancialExecutionTruthError("executed_amount_minor must be positive")
        if not isinstance(self.currency, str) or re.fullmatch(r"[A-Z]{3}", self.currency) is None:
            raise FinancialExecutionTruthError("currency must be an uppercase 3-letter code")
        if not isinstance(self.executed_at, datetime) or self.executed_at.tzinfo is None or not isinstance(self.created_at, datetime) or self.created_at.tzinfo is None:
            raise FinancialExecutionTruthError("timestamps must be timezone-aware")
        if self.executed_at > self.created_at:
            raise FinancialExecutionTruthError("executed_at cannot be later than created_at")
        if _HEX.fullmatch(self.execution_command_fingerprint) is None or _HEX.fullmatch(self.execution_evidence_fingerprint) is None:
            raise FinancialExecutionTruthError("fingerprints must be lowercase SHA3-512 hex")

    def evidence_payload(self) -> dict[str, Any]:
        """Return deterministic immutable execution evidence, excluding runtime metadata and settlement."""
        return {name: getattr(self, name).value if isinstance(getattr(self, name), StrEnum) else (getattr(self, name).isoformat() if isinstance(getattr(self, name), datetime) else getattr(self, name)) for name in ("execution_truth_id", "tenant_id", "payable_id", "release_authorization_id", "provider", "provider_execution_reference", "execution_status", "executed_amount_minor", "currency", "executed_at", "payment_destination_reference", "provider_evidence_reference", "execution_command_fingerprint", "execution_evidence_fingerprint")}

    def to_dict(self) -> dict[str, Any]:
        """Serialize the immutable contract; no bank, payment, or settlement fields are accepted."""
        return {**self.evidence_payload(), "created_at": self.created_at.isoformat()}

    @property
    def evidence_fingerprint(self) -> str:
        """Compute canonical SHA3-512 evidence digest without claiming a signature."""
        encoded = json.dumps(self.evidence_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        return hashlib.sha3_512(encoded).hexdigest()

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "FinancialExecutionTruth":
        """Hydrate strictly and reject forbidden raw destination or settlement fields."""
        forbidden = {"bank_account", "bank_account_number", "card_number", "credentials", "paid", "settled", "settlement_id"}
        if forbidden.intersection(mapping):
            raise FinancialExecutionTruthError("forbidden financial fields")
        return cls(**dict(mapping))


# MANDATORY END SEAL
# ARTIFACT: financial_execution.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TRUTH-DOMAIN
# AUTHORITY BOUNDARY: Kennel EOS exclusively owns provider execution truth.
# TENANT POSTURE: tenant_id and payable_id required; no cross-tenant inference.
# FAIL-CLOSED POSTURE: immutable validation rejects malformed or sensitive input.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS; execution is not settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
