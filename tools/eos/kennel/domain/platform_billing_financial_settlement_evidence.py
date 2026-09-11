"""WILSY OS — canonical platform settlement evidence.

TITLE: Platform Billing Financial Settlement Evidence
VERSION: v1.0.0-M11E2D5R3A-R2
AUTHORITY: Kennel EOS / Wilsy OS Core Governance
EPITOME: Immutable full-settlement evidence derived from durable settlement-observation provenance.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/domain/platform_billing_financial_settlement_evidence.py
COLLABORATION / OWNERSHIP: Kennel EOS settlement-evidence domain owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11E2D5R3A-R2 canonicalizes the complete artifact structure without semantic change.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: opaque provider references; no credentials or raw payloads.
TENANT BOUNDARY: all evidence is tenant-scoped and immutable.
AUTHORITY BOUNDARY: Kennel settlement evidence only; no R3F or receivable mutation.
FINANCIAL AUTHORITY BOUNDARY: full settlement evidence, never paid truth.
TRANSACTION BOUNDARY: persistence is caller-session-owned by the registry.
FAIL-CLOSED DECLARATION: missing provenance, corruption, and non-executed truth reject.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime

from .platform_billing_financial_execution_truth import (
    PlatformBillingFinancialExecutionTruth,
    PlatformExecutionStatus,
)


class PlatformBillingFinancialSettlementEvidenceError(ValueError):
    """Fail-closed validation error for settlement evidence."""


@dataclass(frozen=True)
class PlatformBillingFinancialSettlementEvidence:
    """Immutable, tenant-scoped full-settlement evidence."""

    tenant_id: str
    settlement_evidence_id: str
    platform_execution_truth_id: str
    platform_invoice_id: str
    execution_request_id: str
    execution_command_id: str
    release_authorization_id: str
    settled_amount_minor: int
    currency: str
    settlement_reference: str
    provider_settlement_evidence_reference: str
    settled_at: datetime
    created_at: datetime
    source_financial_settlement_observation_id: str
    source_financial_settlement_observation_fingerprint: str

    def __post_init__(self) -> None:
        for name in (
            "tenant_id", "settlement_evidence_id", "platform_execution_truth_id",
            "platform_invoice_id", "execution_request_id", "execution_command_id",
            "release_authorization_id", "settlement_reference",
            "provider_settlement_evidence_reference",
            "source_financial_settlement_observation_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise PlatformBillingFinancialSettlementEvidenceError(f"{name} is invalid")
        if re.fullmatch(r"[0-9a-f]{128}", self.source_financial_settlement_observation_fingerprint) is None:
            raise PlatformBillingFinancialSettlementEvidenceError("source observation fingerprint is invalid")
        if not isinstance(self.settled_amount_minor, int) or isinstance(self.settled_amount_minor, bool) or self.settled_amount_minor <= 0:
            raise PlatformBillingFinancialSettlementEvidenceError("amount is invalid")
        if re.fullmatch(r"[A-Z]{3}", self.currency) is None:
            raise PlatformBillingFinancialSettlementEvidenceError("currency is invalid")
        for name in ("settled_at", "created_at"):
            value = getattr(self, name)
            if not isinstance(value, datetime) or value.tzinfo is None:
                raise PlatformBillingFinancialSettlementEvidenceError("timestamp is invalid")

    @classmethod
    def from_execution_truth(
        cls,
        truth: PlatformBillingFinancialExecutionTruth,
        settlement_reference: str,
        provider_settlement_evidence_reference: str,
        settled_at: datetime,
        created_at: datetime,
        *,
        source_financial_settlement_observation_id: str,
        source_financial_settlement_observation_fingerprint: str,
    ) -> "PlatformBillingFinancialSettlementEvidence":
        """Construct full evidence from executed platform truth and durable observation provenance."""
        if truth.execution_status is not PlatformExecutionStatus.EXECUTED:
            raise PlatformBillingFinancialSettlementEvidenceError("EXECUTED truth required")
        return cls(
            truth.tenant_id,
            f"platform-settlement-{truth.execution_request_id}",
            f"platform-truth-{truth.execution_request_id}",
            truth.platform_invoice_id,
            truth.execution_request_id,
            truth.execution_command_id,
            truth.release_authorization_id,
            truth.executed_amount_minor,
            truth.currency,
            settlement_reference,
            provider_settlement_evidence_reference,
            settled_at,
            created_at,
            source_financial_settlement_observation_id,
            source_financial_settlement_observation_fingerprint,
        )

    def to_dict(self) -> dict[str, object]:
        """Return deterministic persisted representation."""
        return {key: value.isoformat() if isinstance(value, datetime) else value for key, value in self.__dict__.items()}

    @property
    def fingerprint(self) -> str:
        """Return canonical SHA3-512 evidence fingerprint."""
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        return hashlib.sha3_512(payload).hexdigest()


# ARTIFACT: platform_billing_financial_settlement_evidence.py
# VERSION: v1.0.0-M11E2D5R3A-R2
# AUTHORITY BOUNDARY: Kennel settlement evidence only; no commercial projection.
# TENANT POSTURE: immutable tenant-scoped observation provenance.
# FAIL-CLOSED POSTURE: provenance and integrity failures reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
