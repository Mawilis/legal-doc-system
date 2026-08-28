"""Immutable Wilsy-internal evidence of a transport-boundary event.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-DISPATCH-TRANSPORT-EVIDENCE
TITLE: Financial Execution Dispatch Transport Evidence Domain
PURPOSE: Record internal transport facts separately from provider-originated observations.
AUTHORITY: Wilsy transport evidence only; no provider outcome, execution truth, or settlement authority.
EPITOME: Append-only events make send-boundary recovery explicit without treating delivery as acceptance.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/domain/financial_execution_dispatch_transport_evidence.py
CERTIFICATION DATE: 2026-08-28
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque references and fingerprints only; no payloads, credentials, or provider evidence.
TENANT BOUNDARY: every event binds one tenant, command, attempt, claim, and transport correlation.
FINANCIAL AUTHORITY BOUNDARY: transport evidence is not provider execution truth or settlement.
TRANSACTION BOUNDARY: pure value object; persistence and transaction ownership remain with the caller.
CHANGELOG: v1.0.0 establishes immutable provider-neutral transport dispositions and deterministic evidence fingerprints.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

VERSION = "v1.0.0-KENNEL-FINANCIAL-EXECUTION-DISPATCH-TRANSPORT-EVIDENCE"
_HEX = re.compile(r"^[0-9a-f]{128}$")


class FinancialExecutionDispatchTransportEvidenceError(ValueError):
    """Fail-closed validation error for malformed internal transport evidence."""


class TransportEvidenceDisposition(StrEnum):
    """Wilsy-owned transport facts, never provider business outcomes."""

    SEND_STARTED = "SEND_STARTED"
    SENT = "SENT"
    RESPONSE_RECEIVED = "RESPONSE_RECEIVED"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass(frozen=True)
class FinancialExecutionDispatchTransportEvidence:
    """Immutable append-only transport event bound to one dispatch claim."""

    transport_evidence_id: str
    tenant_id: str
    execution_command_id: str
    execution_attempt_id: str
    dispatch_claim_id: str
    provider_name: str
    transport_correlation_id: str
    transport_material_fingerprint: str
    transport_disposition: TransportEvidenceDisposition
    recorded_at: datetime
    response_evidence_reference: str | None = None

    def __post_init__(self) -> None:
        names = ("transport_evidence_id", "tenant_id", "execution_command_id", "execution_attempt_id", "dispatch_claim_id", "provider_name", "transport_correlation_id")
        for name in names:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise FinancialExecutionDispatchTransportEvidenceError(f"{name} must be non-empty")
        if self.transport_evidence_id in {self.execution_command_id, self.execution_attempt_id, self.dispatch_claim_id, self.transport_correlation_id}:
            raise FinancialExecutionDispatchTransportEvidenceError("evidence identity must remain distinct")
        if _HEX.fullmatch(self.transport_material_fingerprint) is None:
            raise FinancialExecutionDispatchTransportEvidenceError("transport_material_fingerprint must be lowercase SHA3-512 hex")
        if not isinstance(self.transport_disposition, TransportEvidenceDisposition):
            raise FinancialExecutionDispatchTransportEvidenceError("transport disposition is invalid")
        if not isinstance(self.recorded_at, datetime) or self.recorded_at.tzinfo is None:
            raise FinancialExecutionDispatchTransportEvidenceError("recorded_at must be timezone-aware")
        if self.response_evidence_reference is not None and (not isinstance(self.response_evidence_reference, str) or not self.response_evidence_reference.strip()):
            raise FinancialExecutionDispatchTransportEvidenceError("response_evidence_reference must be opaque")
        if self.transport_disposition is TransportEvidenceDisposition.RESPONSE_RECEIVED and self.response_evidence_reference is None:
            raise FinancialExecutionDispatchTransportEvidenceError("response receipt requires response evidence reference")
        if self.transport_disposition is not TransportEvidenceDisposition.RESPONSE_RECEIVED and self.response_evidence_reference is not None:
            raise FinancialExecutionDispatchTransportEvidenceError("response evidence is valid only for response receipt")

    def canonical_payload(self) -> dict[str, object]:
        """Return deterministic semantic event material with explicit optional null."""
        return {
            "dispatch_claim_id": self.dispatch_claim_id,
            "execution_attempt_id": self.execution_attempt_id,
            "execution_command_id": self.execution_command_id,
            "provider_name": self.provider_name,
            "recorded_at": self.recorded_at.isoformat(),
            "response_evidence_reference": self.response_evidence_reference,
            "tenant_id": self.tenant_id,
            "transport_correlation_id": self.transport_correlation_id,
            "transport_disposition": self.transport_disposition.value,
            "transport_evidence_id": self.transport_evidence_id,
            "transport_material_fingerprint": self.transport_material_fingerprint,
        }

    def canonical_bytes(self) -> bytes:
        """Serialize event evidence as compact sorted UTF-8 JSON."""
        return json.dumps(self.canonical_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

    @property
    def fingerprint(self) -> str:
        """Return the deterministic lowercase SHA3-512 event fingerprint."""
        return hashlib.sha3_512(self.canonical_bytes()).hexdigest()


# ARTIFACT: financial_execution_dispatch_transport_evidence.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-DISPATCH-TRANSPORT-EVIDENCE
# AUTHORITY BOUNDARY: Wilsy internal transport evidence only; no provider outcome, execution truth, or settlement.
# TENANT POSTURE: explicit tenant, command, attempt, claim, and correlation lineage.
# FAIL-CLOSED POSTURE: malformed identity, fingerprint, disposition, timestamp, and response-reference combinations reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; execution is not settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
