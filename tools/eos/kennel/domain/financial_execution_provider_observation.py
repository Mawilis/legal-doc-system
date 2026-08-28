# -*- coding: utf-8 -*-
"""Provider-neutral immutable asynchronous execution observation contract.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-PROVIDER-OBSERVATION
AUTHORITY: observation evidence only; no lifecycle, truth, or settlement authority.
CHANGELOG: v1.0.0 establishes tenant-bound observations, orthogonal transport disposition, and deterministic fingerprints.
"""
from __future__ import annotations
import hashlib, json, re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

VERSION = "v1.0.0-KENNEL-FINANCIAL-EXECUTION-PROVIDER-OBSERVATION"
_HEX = re.compile(r"^[0-9a-f]{128}$")

class ObservationError(ValueError): pass
class ObservationStatus(StrEnum):
    REQUESTED="REQUESTED"; INITIATED="INITIATED"; ACCEPTED="ACCEPTED"; PENDING="PENDING"; EXECUTED="EXECUTED"; FAILED="FAILED"; CANCELLED="CANCELLED"; UNKNOWN="UNKNOWN"; CONFLICT="CONFLICT"
class TransportDisposition(StrEnum):
    NOT_SENT="NOT_SENT"; SEND_STARTED="SEND_STARTED"; SENT="SENT"; RESPONSE_RECEIVED="RESPONSE_RECEIVED"; AMBIGUOUS="AMBIGUOUS"
class EvidenceStrength(StrEnum):
    UNAUTHENTICATED="UNAUTHENTICATED"; AUTHENTICATED="AUTHENTICATED"; CORROBORATED="CORROBORATED"; CONFLICTING="CONFLICTING"

@dataclass(frozen=True)
class FinancialExecutionProviderObservation:
    observation_id: str
    tenant_id: str
    execution_attempt_id: str
    provider_name: str
    observation_status: ObservationStatus
    observed_at: datetime
    provider_request_reference: str | None = None
    provider_execution_reference: str | None = None
    provider_evidence_reference: str | None = None
    provider_occurred_at: datetime | None = None
    evidence_strength: EvidenceStrength = EvidenceStrength.UNAUTHENTICATED
    transport_disposition: TransportDisposition = TransportDisposition.RESPONSE_RECEIVED
    correlation_fingerprint: str | None = None

    def __post_init__(self) -> None:
        for n in ("observation_id","tenant_id","execution_attempt_id","provider_name"):
            if not isinstance(getattr(self,n),str) or not getattr(self,n).strip(): raise ObservationError(f"{n} must be non-empty")
        if self.observation_id == self.execution_attempt_id: raise ObservationError("observation and attempt identities must differ")
        if not isinstance(self.observation_status,ObservationStatus) or not isinstance(self.evidence_strength,EvidenceStrength) or not isinstance(self.transport_disposition,TransportDisposition): raise ObservationError("observation vocabulary is invalid")
        for n in ("provider_request_reference","provider_execution_reference","provider_evidence_reference"):
            v=getattr(self,n)
            if v is not None and (not isinstance(v,str) or not v.strip()): raise ObservationError(f"{n} must be opaque")
        if not isinstance(self.observed_at,datetime) or self.observed_at.tzinfo is None: raise ObservationError("observed_at must be timezone-aware")
        if self.provider_occurred_at is not None and (not isinstance(self.provider_occurred_at,datetime) or self.provider_occurred_at.tzinfo is None): raise ObservationError("provider_occurred_at must be timezone-aware")
        if self.correlation_fingerprint is not None and _HEX.fullmatch(self.correlation_fingerprint) is None: raise ObservationError("correlation_fingerprint is invalid")

    def to_dict(self) -> dict[str, object]:
        return {k:(v.value if isinstance(v,StrEnum) else v.isoformat() if isinstance(v,datetime) else v) for k,v in self.__dict__.items()}
    @property
    def fingerprint(self) -> str:
        return hashlib.sha3_512(json.dumps(self.to_dict(),sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

# ARTIFACT: financial_execution_provider_observation.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-PROVIDER-OBSERVATION
# END OF WILSY OS SOVEREIGN ARTIFACT
