"""Wilsy OS Kennel EOS provider-neutral financial execution orchestration.

TITLE: Financial Execution Orchestrator and Provider SPI
VERSION: v1.1.0-KENNEL-FINANCIAL-EXECUTION-ORCHESTRATOR-TERMINAL-RESULT-CONTRACT
AUTHORITY: Wilsy OS Core Governance
ARCHITECTURE LOCK: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
FINANCIAL AUTHORITY: Kennel EOS exclusively owns execution truth.
SCOPE: provider invocation evidence and immutable execution persistence only.
DOMAIN CONTRACT: v1.0.1-KENNEL-FINANCIAL-EXECUTION-TRUTH-DOMAIN-PERSISTENCE-HYDRATION
REGISTRY CONTRACT: v1.0.4-KENNEL-FINANCIAL-EXECUTION-TRUTH-REGISTRY-CALLER-TRANSACTION-REPLAY
REGISTRY CERTIFICATION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TRUTH-REGISTRY-REAL-MONGO-CERT
COMPLIANCE: POPIA §19 | GDPR Art. 32 | SOC2 CC7.2
SECURITY: opaque destination references; raw credentials rejected.
TRANSACTION OWNERSHIP: caller-owned sessions; orchestrator never commits or aborts.
CHANGELOG: v1.0.0 establishes provider-neutral command, SPI, replay protection, and truth persistence; v1.0.1 introduces a narrow injected registry port and production delegation adapter without changing financial or persistence semantics; v1.1.0 restricts synchronous provider results to terminal EXECUTED or FAILED outcomes with status-specific timestamp validation.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional, Protocol

from pymongo.collection import Collection
from pymongo.client_session import ClientSession

from ..domain.financial_execution import FinancialExecutionStatus, FinancialExecutionTruth
from ..registry.financial_execution_registry import (
    FinancialExecutionCreateOutcome,
    FinancialExecutionCreateResult,
    FinancialExecutionTruthRegistry,
)

VERSION = "v1.1.0-KENNEL-FINANCIAL-EXECUTION-ORCHESTRATOR-TERMINAL-RESULT-CONTRACT"
_HEX = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN = re.compile(r"(?:bank_account|account_number|branch_code|card_number|card_pan|cvv|credentials|password|secret|access_token|refresh_token|api_key)", re.I)


class FinancialExecutionOrchestratorError(RuntimeError):
    """Base fail-closed orchestration error."""


class FinancialExecutionCommandInvalidError(FinancialExecutionOrchestratorError):
    """Raised when provider-neutral execution intent is malformed or sensitive."""


class FinancialExecutionProviderContractError(FinancialExecutionOrchestratorError):
    """Raised when a provider returns invalid execution evidence."""


class FinancialExecutionPreInvocationIdempotencyConflictError(FinancialExecutionOrchestratorError):
    """Raised when an existing immutable truth diverges from requested intent."""


@dataclass(frozen=True)
class FinancialExecutionCommand:
    """Immutable provider-neutral execution intent."""

    tenant_id: str
    payable_id: str
    release_authorization_id: str
    execution_command_id: str
    idempotency_key: str
    amount_minor: int
    currency: str
    payment_destination_reference: str
    requested_provider: Optional[str] = None
    provider_metadata_reference: Optional[str] = None

    def __post_init__(self) -> None:
        for name in ("tenant_id", "payable_id", "release_authorization_id", "execution_command_id", "idempotency_key", "payment_destination_reference"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip() or _FORBIDDEN.search(value):
                raise FinancialExecutionCommandInvalidError(f"invalid {name}")
        if not isinstance(self.amount_minor, int) or isinstance(self.amount_minor, bool) or self.amount_minor <= 0:
            raise FinancialExecutionCommandInvalidError("amount_minor must be positive")
        if not isinstance(self.currency, str) or re.fullmatch(r"[A-Z]{3}", self.currency) is None:
            raise FinancialExecutionCommandInvalidError("currency must be uppercase 3-letter code")

    def evidence_payload(self) -> dict[str, Any]:
        """Return deterministic semantic intent, excluding runtime details."""
        return {"tenant_id": self.tenant_id, "payable_id": self.payable_id, "release_authorization_id": self.release_authorization_id, "execution_command_id": self.execution_command_id, "idempotency_key": self.idempotency_key, "amount_minor": self.amount_minor, "currency": self.currency, "payment_destination_reference": self.payment_destination_reference, "requested_provider": self.requested_provider, "provider_metadata_reference": self.provider_metadata_reference}

    @property
    def fingerprint(self) -> str:
        """Compute canonical SHA3-512 execution-intent fingerprint."""
        encoded = json.dumps(self.evidence_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        return hashlib.sha3_512(encoded).hexdigest()


@dataclass(frozen=True)
class FinancialExecutionProviderResult:
    """Immutable provider execution evidence; never settlement."""

    provider: str
    provider_execution_reference: str
    execution_status: FinancialExecutionStatus
    provider_evidence_reference: str
    executed_at: datetime | None

    def __post_init__(self) -> None:
        if not isinstance(self.provider, str) or not self.provider.strip() or not isinstance(self.provider_execution_reference, str) or not self.provider_execution_reference.strip() or not isinstance(self.provider_evidence_reference, str) or not self.provider_evidence_reference.strip():
            raise FinancialExecutionProviderContractError("provider evidence identifiers are invalid")
        if not isinstance(self.execution_status, FinancialExecutionStatus):
            raise FinancialExecutionProviderContractError("provider execution evidence is invalid")
        if self.execution_status not in (FinancialExecutionStatus.EXECUTED, FinancialExecutionStatus.FAILED):
            raise FinancialExecutionProviderContractError("provider result must be terminal")
        if self.execution_status is FinancialExecutionStatus.EXECUTED and (not isinstance(self.executed_at, datetime) or self.executed_at.tzinfo is None):
            raise FinancialExecutionProviderContractError("EXECUTED requires timezone-aware executed_at")
        if self.execution_status is FinancialExecutionStatus.FAILED and self.executed_at is not None:
            raise FinancialExecutionProviderContractError("FAILED must not carry executed_at")


class FinancialExecutionProvider(Protocol):
    """Provider-neutral SPI implemented by future provider adapters."""

    provider_name: str

    def execute(self, command: FinancialExecutionCommand) -> FinancialExecutionProviderResult:
        """Execute intent and return immutable provider evidence."""
        ...


class FinancialExecutionRegistryPort(Protocol):
    """Minimal domain-level persistence dependency required by orchestration."""

    def get_by_idempotency_key(self, tenant_id: str, payable_id: str, idempotency_key: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> Optional[FinancialExecutionTruth]: ...
    def create(self, execution_truth: FinancialExecutionTruth, idempotency_key: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> FinancialExecutionCreateResult: ...


class FinancialExecutionRegistryAdapter:
    """Delegates orchestration persistence directly to the frozen registry."""

    def get_by_idempotency_key(self, tenant_id: str, payable_id: str, idempotency_key: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> Optional[FinancialExecutionTruth]:
        return FinancialExecutionTruthRegistry.get_by_idempotency_key(tenant_id, payable_id, idempotency_key, collection, session=session)

    def create(self, execution_truth: FinancialExecutionTruth, idempotency_key: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> FinancialExecutionCreateResult:
        return FinancialExecutionTruthRegistry.create(execution_truth, idempotency_key, collection, session=session)


@dataclass(frozen=True)
class FinancialExecutionOrchestrationResult:
    """Separates provider invocation from registry persistence outcome."""

    provider_invoked: bool
    registry_outcome: FinancialExecutionCreateOutcome
    execution_truth: FinancialExecutionTruth


class FinancialExecutionOrchestrator:
    """Coordinates provider evidence into immutable Kennel execution truth."""

    def __init__(self, provider: FinancialExecutionProvider, registry: Optional[FinancialExecutionRegistryPort] = None) -> None:
        self._provider = provider
        self._registry = registry if registry is not None else FinancialExecutionRegistryAdapter()

    def authorize(self, command: FinancialExecutionCommand, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> FinancialExecutionOrchestrationResult:
        """Preflight replay, invoke provider once, and persist immutable truth."""
        if not isinstance(command, FinancialExecutionCommand):
            raise FinancialExecutionCommandInvalidError("command must be FinancialExecutionCommand")
        existing = self._registry.get_by_idempotency_key(command.tenant_id, command.payable_id, command.idempotency_key, collection, session=session)
        if existing is not None:
            if existing.release_authorization_id != command.release_authorization_id or existing.executed_amount_minor != command.amount_minor or existing.currency != command.currency or existing.payment_destination_reference != command.payment_destination_reference or existing.execution_command_fingerprint != command.fingerprint:
                raise FinancialExecutionPreInvocationIdempotencyConflictError("FINANCIAL_EXECUTION_IDEMPOTENCY_CONFLICT")
            return FinancialExecutionOrchestrationResult(False, FinancialExecutionCreateOutcome.IDEMPOTENT_REPLAY, existing)
        if session is not None and session.in_transaction:
            raise FinancialExecutionOrchestratorError("provider invocation forbidden inside active caller transaction")
        result = self._provider.execute(command)
        if not isinstance(result, FinancialExecutionProviderResult):
            raise FinancialExecutionProviderContractError("provider returned invalid evidence")
        if command.requested_provider is not None and result.provider != command.requested_provider:
            raise FinancialExecutionProviderContractError("provider mismatch")
        truth = FinancialExecutionTruth(execution_truth_id=command.execution_command_id, tenant_id=command.tenant_id, payable_id=command.payable_id, release_authorization_id=command.release_authorization_id, provider=result.provider, provider_execution_reference=result.provider_execution_reference, execution_status=result.execution_status, executed_amount_minor=command.amount_minor, currency=command.currency, executed_at=result.executed_at, payment_destination_reference=command.payment_destination_reference, provider_evidence_reference=result.provider_evidence_reference, execution_command_fingerprint=command.fingerprint, execution_evidence_fingerprint=_evidence_fingerprint(command, result), created_at=datetime.now(timezone.utc))
        persisted = self._registry.create(truth, command.idempotency_key, collection, session=session)
        return FinancialExecutionOrchestrationResult(True, persisted.outcome, persisted.execution_truth)


def _evidence_fingerprint(command: FinancialExecutionCommand, result: FinancialExecutionProviderResult) -> str:
    """Hash immutable command/provider evidence without settlement semantics."""
    payload = {"command_fingerprint": command.fingerprint, "provider": result.provider, "provider_execution_reference": result.provider_execution_reference, "execution_status": result.execution_status.value, "provider_evidence_reference": result.provider_evidence_reference, "executed_at": result.executed_at.isoformat() if result.executed_at is not None else None}
    return hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()


# ARTIFACT: financial_execution_orchestrator.py
# VERSION: v1.1.0-KENNEL-FINANCIAL-EXECUTION-ORCHESTRATOR-TERMINAL-RESULT-CONTRACT
# ARCHITECTURE LOCK: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
# FINANCIAL AUTHORITY: Kennel EOS exclusively owns financial execution truth
# TRANSACTION POSTURE: caller-owned sessions; no lifecycle ownership
# SCOPE LIMITATION: provider execution evidence only; no settlement or paid state
# END OF WILSY OS SOVEREIGN ARTIFACT
