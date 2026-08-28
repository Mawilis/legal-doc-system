# -*- coding: utf-8 -*-
"""Explicit provider-neutral authority for execution-time evidence.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TIME-EVIDENCE
TITLE: Financial Execution Time Evidence
PURPOSE: Immutable, tenant-bound evidence whose timestamp is explicitly authoritative for execution.
AUTHORITY: domain evidence contract only; no persistence, orchestration, truth, or settlement authority.
EPITOME: Prevents provider occurrence or transport timestamps from being promoted into executed_at implicitly.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/domain/financial_execution_execution_time_evidence.py
DATE: 2026-08-28 | COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque references only; no payloads, credentials, or provider secrets.
TENANT BOUNDARY: tenant_id, execution_attempt_id, and provider identity are mandatory and immutable.
FINANCIAL TRUTH BOUNDARY: THIS MODULE DOES NOT CREATE FINANCIAL EXECUTION TRUTH.
SETTLEMENT BOUNDARY: THIS MODULE DOES NOT DEFINE SETTLEMENT.
TIME BOUNDARY: THIS MODULE DOES NOT INFER EXECUTION TIME FROM PROVIDER OCCURRENCE TIME.
CHANGELOG: v1.0.0 establishes explicit execution-time authority without provider-specific coupling.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .financial_execution_provider_observation import EvidenceStrength

VERSION = "v1.0.0-KENNEL-FINANCIAL-EXECUTION-TIME-EVIDENCE"
_HEX = re.compile(r"^[0-9a-f]{128}$")


class FinancialExecutionTimeEvidenceError(ValueError):
    """Fail-closed validation error for execution-time authority evidence."""


class ExecutionTimeAuthorityKind(StrEnum):
    """Closed provider-neutral reasons an execution timestamp may be authoritative."""

    PROVIDER_EXECUTION_CONFIRMATION = "PROVIDER_EXECUTION_CONFIRMATION"
    SIGNED_EXECUTION_RECEIPT = "SIGNED_EXECUTION_RECEIPT"
    CORROBORATED_EXECUTION_EVIDENCE = "CORROBORATED_EXECUTION_EVIDENCE"


@dataclass(frozen=True)
class FinancialExecutionTimeEvidence:
    """Immutable explicit execution-time authority for later pure terminalization policy."""

    tenant_id: str
    execution_attempt_id: str
    provider_name: str
    provider_execution_reference: str
    evidence_reference: str
    executed_at: datetime
    authority_kind: ExecutionTimeAuthorityKind
    evidence_strength: EvidenceStrength

    def __post_init__(self) -> None:
        for name in (
            "tenant_id",
            "execution_attempt_id",
            "provider_name",
            "provider_execution_reference",
            "evidence_reference",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise FinancialExecutionTimeEvidenceError(f"{name} must be non-empty")
        if not isinstance(self.executed_at, datetime) or self.executed_at.tzinfo is None:
            raise FinancialExecutionTimeEvidenceError("executed_at must be timezone-aware")
        if not isinstance(self.authority_kind, ExecutionTimeAuthorityKind):
            raise FinancialExecutionTimeEvidenceError("authority_kind is invalid")
        if self.evidence_strength not in {
            EvidenceStrength.AUTHENTICATED,
            EvidenceStrength.CORROBORATED,
        }:
            raise FinancialExecutionTimeEvidenceError(
                "execution-time evidence must be authenticated or corroborated"
            )

    def to_dict(self) -> dict[str, object]:
        """Return deterministic semantic fields without mutable runtime metadata."""
        return {
            "tenant_id": self.tenant_id,
            "execution_attempt_id": self.execution_attempt_id,
            "provider_name": self.provider_name,
            "provider_execution_reference": self.provider_execution_reference,
            "evidence_reference": self.evidence_reference,
            "executed_at": self.executed_at.isoformat(),
            "authority_kind": self.authority_kind.value,
            "evidence_strength": self.evidence_strength.value,
        }

    @property
    def fingerprint(self) -> str:
        """Compute the deterministic SHA3-512 fingerprint of immutable evidence."""
        return hashlib.sha3_512(
            json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
        ).hexdigest()


# ARTIFACT: financial_execution_execution_time_evidence.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TIME-EVIDENCE
# AUTHORITY BOUNDARY: explicit execution-time evidence only; no truth or settlement authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
