"""TITLE: Platform Billing Financial Execution Truth
VERSION: v2.0.0-M11-P5-R2D-R1
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Project one neutral execution fact and one canonical Platform command into immutable platform evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/domain/platform_billing_financial_execution_truth.py
COLLABORATION / OWNERSHIP: Kennel EOS Platform Billing execution-evidence owner.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v2.0.0-M11-P5-R2D-R1 replaces legacy generic-truth adaptation with strict neutral-fact and Platform-command projection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references only; no credentials or provider payloads.
TENANT BOUNDARY: Every source, command, fact, and projected truth is tenant-correlated.
AUTHORITY BOUNDARY: Canonical Platform generic command plus authenticated neutral execution fact only.
FINANCIAL AUTHORITY BOUNDARY: Evidence projection does not execute, settle, mark paid, or close receivables.
TRANSACTION BOUNDARY: Frozen value object; caller-owned persistence/session remains external.
FAIL-CLOSED DECLARATION: Unknown, missing, mixed-family, divergent, or legacy authority rejects.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, fields
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping

from .financial_execution import FinancialExecutionFact
from .financial_execution_command import FinancialExecutionCommand, FinancialExecutionCommandFamily, PlatformBillingCommandSource

VERSION = "v2.0.0-M11-P5-R2D-R1"
_HEX = re.compile(r"^[0-9a-f]{128}$")


class PlatformBillingFinancialExecutionTruthError(ValueError):
    """Fail-closed validation error for Platform execution evidence."""


class PlatformExecutionStatus(StrEnum):
    """Platform projection of neutral execution status; settlement is absent."""

    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


def _digest(payload: Mapping[str, object]) -> str:
    """Hash deterministic canonical JSON with SHA3-512."""
    return hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def _text(name: str, value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise PlatformBillingFinancialExecutionTruthError(f"{name} is invalid")


@dataclass(frozen=True, slots=True)
class PlatformBillingFinancialExecutionTruth:
    """Immutable tenant-scoped Platform evidence projected from canonical sources."""

    tenant_id: str
    execution_truth_id: str
    platform_invoice_id: str
    execution_request_id: str
    execution_request_fingerprint: str
    execution_command_id: str
    release_authorization_id: str
    release_authorization_fingerprint: str
    routing_decision_id: str
    routing_decision_fingerprint: str
    provider: str
    provider_execution_reference: str
    execution_status: PlatformExecutionStatus
    executed_amount_minor: int
    currency: str
    executed_at: datetime | None
    payment_destination_reference: str
    provider_evidence_reference: str
    execution_command_fingerprint: str
    execution_evidence_fingerprint: str
    created_at: datetime
    source_execution_fact_id: str
    source_execution_fact_fingerprint: str

    def __post_init__(self) -> None:
        for name in ("tenant_id", "execution_truth_id", "platform_invoice_id", "execution_request_id", "execution_command_id", "release_authorization_id", "routing_decision_id", "provider", "provider_execution_reference", "payment_destination_reference", "provider_evidence_reference", "source_execution_fact_id"):
            _text(name, getattr(self, name))
        for name in ("execution_request_fingerprint", "release_authorization_fingerprint", "routing_decision_fingerprint", "execution_command_fingerprint", "execution_evidence_fingerprint", "source_execution_fact_fingerprint"):
            if _HEX.fullmatch(getattr(self, name)) is None:
                raise PlatformBillingFinancialExecutionTruthError(f"{name} is invalid")
        if not isinstance(self.execution_status, PlatformExecutionStatus):
            raise PlatformBillingFinancialExecutionTruthError("execution_status is invalid")
        if not isinstance(self.executed_amount_minor, int) or isinstance(self.executed_amount_minor, bool) or self.executed_amount_minor <= 0:
            raise PlatformBillingFinancialExecutionTruthError("executed_amount_minor is invalid")
        if not isinstance(self.currency, str) or re.fullmatch(r"[A-Z]{3}", self.currency) is None:
            raise PlatformBillingFinancialExecutionTruthError("currency is invalid")
        if not isinstance(self.created_at, datetime) or self.created_at.tzinfo is None:
            raise PlatformBillingFinancialExecutionTruthError("created_at is invalid")
        if self.execution_status is PlatformExecutionStatus.EXECUTED and (not isinstance(self.executed_at, datetime) or self.executed_at.tzinfo is None):
            raise PlatformBillingFinancialExecutionTruthError("EXECUTED requires executed_at")
        if self.execution_status is not PlatformExecutionStatus.EXECUTED and self.executed_at is not None:
            raise PlatformBillingFinancialExecutionTruthError("non-EXECUTED cannot carry executed_at")
        if self.execution_truth_id != f"platform-truth-{self.execution_request_id}":
            raise PlatformBillingFinancialExecutionTruthError("execution_truth_id is not canonical")

    @property
    def source_financial_execution_truth_id(self) -> str:
        """Compatibility alias for settlement consumers; value is the neutral fact ID."""
        return self.source_execution_fact_id

    @property
    def source_financial_execution_truth_fingerprint(self) -> str:
        """Compatibility alias for settlement consumers; value is the neutral fact digest."""
        return self.source_execution_fact_fingerprint

    def to_dict(self) -> dict[str, Any]:
        """Serialize only the canonical Platform schema."""
        return {field.name: (value.value if isinstance(value, StrEnum) else value.isoformat() if isinstance(value, datetime) else value) for field in fields(self) for value in (getattr(self, field.name),)}

    @property
    def fingerprint(self) -> str:
        """Return deterministic SHA3-512 over all projected evidence."""
        return _digest(self.to_dict())

    @classmethod
    def from_execution_fact(cls, execution_fact: FinancialExecutionFact, command: FinancialExecutionCommand, *, created_at: datetime | None = None) -> "PlatformBillingFinancialExecutionTruth":
        """Project a neutral fact through an exact typed Platform generic command."""
        if not isinstance(execution_fact, FinancialExecutionFact):
            raise PlatformBillingFinancialExecutionTruthError("execution_fact is invalid")
        if not isinstance(command, FinancialExecutionCommand) or command.source_authority_kind is not FinancialExecutionCommandFamily.PLATFORM_BILLING or type(command.source_authority) is not PlatformBillingCommandSource:
            raise PlatformBillingFinancialExecutionTruthError("Platform Billing command authority is required")
        source = command.source_authority
        if (execution_fact.tenant_id, execution_fact.execution_command_id, execution_fact.execution_command_fingerprint, execution_fact.provider, execution_fact.executed_amount_minor, execution_fact.currency, execution_fact.payment_destination_reference) != (command.tenant_id, command.execution_command_id, command.fingerprint, command.provider_name, command.amount_minor, command.currency, command.payment_destination_reference):
            raise PlatformBillingFinancialExecutionTruthError("fact/command correlation mismatch")
        if created_at is None:
            created_at = command.created_at
        if not isinstance(created_at, datetime) or created_at.tzinfo is None:
            raise PlatformBillingFinancialExecutionTruthError("created_at is invalid")
        return cls(command.tenant_id, f"platform-truth-{source.execution_request_id}", source.platform_invoice_id, source.execution_request_id, source.execution_request_fingerprint, command.execution_command_id, source.release_authorization_id, source.release_authorization_fingerprint, source.routing_decision_id, source.routing_decision_fingerprint, execution_fact.provider, execution_fact.provider_execution_reference, PlatformExecutionStatus(execution_fact.execution_status.value), execution_fact.executed_amount_minor, execution_fact.currency, execution_fact.executed_at, execution_fact.payment_destination_reference, execution_fact.provider_evidence_reference, execution_fact.execution_command_fingerprint, execution_fact.execution_evidence_fingerprint, created_at, execution_fact.execution_fact_id, execution_fact.fingerprint)

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "PlatformBillingFinancialExecutionTruth":
        """Hydrate exactly the current schema; unknown or legacy fields fail closed."""
        allowed = set(cls.__dataclass_fields__)
        values = dict(mapping)
        if set(values) != allowed:
            raise PlatformBillingFinancialExecutionTruthError("persisted Platform truth fields are incomplete or unknown")
        try:
            if isinstance(values["execution_status"], str):
                values["execution_status"] = PlatformExecutionStatus(values["execution_status"])
            for name in ("executed_at", "created_at"):
                if isinstance(values[name], str):
                    values[name] = datetime.fromisoformat(values[name])
            return cls(**values)
        except (TypeError, ValueError) as error:
            raise PlatformBillingFinancialExecutionTruthError("invalid persisted Platform truth") from error


# ARTIFACT: platform_billing_financial_execution_truth.py
# VERSION: v2.0.0-M11-P5-R2D-R1
# AUTHORITY BOUNDARY: Platform execution-evidence projection only; no provider or settlement authority.
# TENANT POSTURE: all projected identities and source correlations are tenant-scoped.
# FAIL-CLOSED POSTURE: legacy, mixed-family, unknown, missing, and divergent material rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; execution remains distinct from settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
