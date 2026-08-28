# -*- coding: utf-8 -*-
"""Pure PayShap destination, request, status, and evidence contracts.

VERSION: v1.0.0-KENNEL-PAYSHAP-DESTINATION-EVIDENCE-CONTRACT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Provider capability metadata only; no HTTP, persistence, execution, or settlement.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/providers/payshap_contract.py
COLLABORATION: Wilson Khanyezi (Founder/Chief Architect); Codex (AI Engineering)
CHANGELOG: v1.0.0 defines safe PayShap routing, command mapping, idempotency limits, ambiguity, and evidence boundaries.
COMPLIANCE: POPIA §19 | GDPR Art. 32 | SOC2 CC7.2
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping, Protocol

from ..domain.financial_execution import FinancialExecutionStatus
from ..orchestration.financial_execution_orchestrator import FinancialExecutionCommand
from ..domain.payment_destination import PaymentDestination

VERSION = "v1.0.0-KENNEL-PAYSHAP-DESTINATION-EVIDENCE-CONTRACT"
_OPAQUE_FORBIDDEN = re.compile(r"bank[_ -]?account|account[_ -]?number|card[_ -]?number|cvv|credential|password|secret|private[_ -]?key|access[_ -]?token|refresh[_ -]?token|api[_ -]?key", re.I)


class PayShapContractError(ValueError):
    """Raised when a PayShap adapter contract value is malformed or unsafe."""


class PayShapStatus(StrEnum):
    """Provider status vocabulary; status does not imply settlement."""

    REQUESTED = "REQUESTED"
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class PayShapResolvedDestination:
    """Safe provider-routing metadata resolved from an approved destination."""

    payment_destination_id: str
    tenant_id: str
    beneficiary_id: str
    destination_reference: str
    provider_metadata_reference: str
    merchant_profile_reference: str
    routing_profile_reference: str | None = None

    def __post_init__(self) -> None:
        for name in ("payment_destination_id", "tenant_id", "beneficiary_id", "destination_reference", "provider_metadata_reference", "merchant_profile_reference"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip() or _OPAQUE_FORBIDDEN.search(value):
                raise PayShapContractError(f"{name} is invalid or sensitive")
        if self.routing_profile_reference is not None and (not isinstance(self.routing_profile_reference, str) or not self.routing_profile_reference.strip() or _OPAQUE_FORBIDDEN.search(self.routing_profile_reference)):
            raise PayShapContractError("routing_profile_reference is invalid or sensitive")

    @classmethod
    def from_destination(cls, destination: PaymentDestination, merchant_profile_reference: str, routing_profile_reference: str | None = None) -> "PayShapResolvedDestination":
        if not isinstance(destination, PaymentDestination) or not destination.is_execution_eligible:
            raise PayShapContractError("destination must be ACTIVE and VERIFIED")
        if not destination.provider_metadata_reference:
            raise PayShapContractError("PayShap provider metadata reference is required")
        return cls(destination.payment_destination_id, destination.tenant_id, destination.beneficiary_id, destination.destination_reference, destination.provider_metadata_reference, merchant_profile_reference, routing_profile_reference)


class PayShapDestinationResolver(Protocol):
    """Injected resolver for tenant-validated, execution-safe PayShap metadata."""

    def resolve_for_payshap(self, tenant_id: str, destination_reference: str, beneficiary_id: str | None = None) -> PayShapResolvedDestination: ...


@dataclass(frozen=True)
class PayShapConfig:
    """Non-secret adapter configuration; secrets remain behind a resolver."""

    base_url: str
    timeout_ms: int
    return_url: str
    notify_url: str
    api_key_reference: str | None = None
    webhook_secret_reference: str | None = None

    def __post_init__(self) -> None:
        for name in ("base_url", "return_url", "notify_url"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise PayShapContractError(f"{name} is required")
        if not isinstance(self.timeout_ms, int) or isinstance(self.timeout_ms, bool) or self.timeout_ms <= 0:
            raise PayShapContractError("timeout_ms must be positive")
        for name in ("api_key_reference", "webhook_secret_reference"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip() or _OPAQUE_FORBIDDEN.search(value)):
                raise PayShapContractError(f"{name} must be an opaque reference")


class PayShapSecretResolver(Protocol):
    """Execution-time secret boundary; returned secrets never enter canonical truth."""

    def resolve_secret(self, secret_reference: str) -> str: ...


@dataclass(frozen=True)
class PayShapProviderRequest:
    """Deterministic provider request derived from a Kennel command and safe metadata."""

    amount_minor: int
    currency: str
    provider_reference: str
    description: str
    return_url: str
    notify_url: str
    tenant_id: str
    execution_command_id: str
    provider_idempotency_key: str | None
    destination_reference: str
    merchant_profile_reference: str

    @classmethod
    def from_command(cls, command: FinancialExecutionCommand, destination: PayShapResolvedDestination, config: PayShapConfig) -> "PayShapProviderRequest":
        if command.tenant_id != destination.tenant_id:
            raise PayShapContractError("tenant mismatch")
        return cls(command.amount_minor, command.currency, command.execution_command_id, f"Execution {command.execution_command_id}", config.return_url, config.notify_url, command.tenant_id, command.execution_command_id, None, destination.destination_reference, destination.merchant_profile_reference)

    def evidence_payload(self) -> dict[str, Any]:
        return {"amount_minor": self.amount_minor, "currency": self.currency, "provider_reference": self.provider_reference, "description": self.description, "return_url": self.return_url, "notify_url": self.notify_url, "tenant_id": self.tenant_id, "execution_command_id": self.execution_command_id, "provider_idempotency_key": self.provider_idempotency_key, "destination_reference": self.destination_reference, "merchant_profile_reference": self.merchant_profile_reference}

    @property
    def fingerprint(self) -> str:
        return hashlib.sha3_512(json.dumps(self.evidence_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PayShapProviderEvidence:
    """Immutable opaque evidence metadata; raw provider payload is deliberately absent."""

    provider_name: str
    provider_request_reference: str
    provider_execution_reference: str | None
    provider_status: PayShapStatus
    request_fingerprint: str
    response_fingerprint: str | None
    provider_event_id: str | None
    observed_at: datetime
    provider_timestamp: datetime | None
    evidence_reference: str

    def __post_init__(self) -> None:
        for name in ("provider_name", "provider_request_reference", "evidence_reference"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise PayShapContractError(f"{name} is required")
        if not isinstance(self.provider_status, PayShapStatus) or not isinstance(self.observed_at, datetime) or self.observed_at.tzinfo is None:
            raise PayShapContractError("provider evidence is invalid")
        for value in (self.provider_timestamp,):
            if value is not None and (not isinstance(value, datetime) or value.tzinfo is None):
                raise PayShapContractError("provider timestamp is invalid")

    def to_dict(self) -> dict[str, Any]:
        return {"provider_name": self.provider_name, "provider_request_reference": self.provider_request_reference, "provider_execution_reference": self.provider_execution_reference, "provider_status": self.provider_status.value, "request_fingerprint": self.request_fingerprint, "response_fingerprint": self.response_fingerprint, "provider_event_id": self.provider_event_id, "observed_at": self.observed_at.isoformat(), "provider_timestamp": self.provider_timestamp.isoformat() if self.provider_timestamp else None, "evidence_reference": self.evidence_reference}


class PayShapEvidenceStore(Protocol):
    """Injected protected evidence store; implementation is outside this contract."""

    def store(self, evidence: Mapping[str, Any]) -> str: ...


@dataclass(frozen=True)
class PayShapWebhookEvidence:
    """Verified-webhook metadata shape without invoice or settlement mutation."""

    provider_event_id: str
    provider_reference: str
    status: PayShapStatus
    amount_minor: int
    currency: str
    tenant_id: str
    observed_at: datetime
    provider_timestamp: datetime | None
    payload_fingerprint: str
    evidence_reference: str

    def __post_init__(self) -> None:
        if not all(isinstance(getattr(self, n), str) and getattr(self, n).strip() for n in ("provider_event_id", "provider_reference", "tenant_id", "payload_fingerprint", "evidence_reference")) or not isinstance(self.status, PayShapStatus) or not isinstance(self.amount_minor, int) or isinstance(self.amount_minor, bool) or self.amount_minor <= 0 or not isinstance(self.observed_at, datetime) or self.observed_at.tzinfo is None:
            raise PayShapContractError("webhook evidence is invalid")


def map_status(status: PayShapStatus, executed_at: datetime | None = None) -> FinancialExecutionStatus:
    """Map only evidenced execution; initiation success and PAID never imply settlement."""
    if status is PayShapStatus.EXECUTED:
        if executed_at is None or executed_at.tzinfo is None:
            raise PayShapContractError("executed status requires reliable timestamp evidence")
        return FinancialExecutionStatus.EXECUTED
    if status is PayShapStatus.FAILED or status is PayShapStatus.CANCELLED:
        return FinancialExecutionStatus.FAILED
    raise PayShapContractError("PayShap outcome is not an evidenced execution result")


# ARTIFACT: payshap_contract.py
# VERSION: v1.0.0-KENNEL-PAYSHAP-DESTINATION-EVIDENCE-CONTRACT
# AUTHORITY BOUNDARY: capability contract only; no provider, invoice, execution, or settlement authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
