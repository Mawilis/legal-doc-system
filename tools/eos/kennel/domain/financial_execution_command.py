"""WILSY OS generic family-discriminated financial command authority.

TITLE: Financial Execution Command Domain Authority
VERSION: v2.0.0-M11-P5-R2A
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Preserve immutable, family-specific authority provenance before execution transport.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/domain/financial_execution_command.py
COLLABORATION / OWNERSHIP: Kennel EOS generic command domain owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v2.0.0-M11-P5-R2A replaces authority-ambiguous generic material with closed AP/Platform Billing source variants, correlated provider projection, complete SHA3-512 coverage, and AP compatibility projections.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped opaque references only; credentials and provider payloads are forbidden.
TENANT BOUNDARY: Tenant identity is mandatory and immutable in every command and source variant.
AUTHORITY BOUNDARY: A command is an authorized instruction only; source authority is typed and family-specific.
FINANCIAL AUTHORITY BOUNDARY: No provider execution, attempt, execution truth, settlement, paid state, or receivable mutation.
TRANSACTION BOUNDARY: Pure value objects; persistence and transaction lifecycle belong to the registry/caller.
FAIL-CLOSED DECLARATION: Unknown families, incomplete provenance, mixed variants, invalid fingerprints, and provider mismatch reject.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping

VERSION = "v2.0.0-M11-P5-R2A"
_HEX = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN = re.compile(r"bank|account|card|secret|token|credential|password", re.IGNORECASE)


class FinancialExecutionCommandError(ValueError):
    """Fail-closed validation error for malformed command authority."""


class FinancialExecutionCommandFamily(StrEnum):
    """Closed generic-command authority families; no caller-defined values."""

    ACCOUNTS_PAYABLE = "ACCOUNTS_PAYABLE"
    PLATFORM_BILLING = "PLATFORM_BILLING"


def _text(name: str, value: object) -> str:
    """Require an opaque, non-empty textual authority value without normalization."""
    if not isinstance(value, str) or not value.strip() or _FORBIDDEN.search(value):
        raise FinancialExecutionCommandError(f"invalid {name}")
    return value


def _fingerprint(name: str, value: object) -> str:
    """Require lowercase SHA3-512 hexadecimal evidence."""
    text = _text(name, value)
    if _HEX.fullmatch(text) is None:
        raise FinancialExecutionCommandError(f"invalid {name}")
    return text


def _digest(payload: Mapping[str, object]) -> str:
    """Hash deterministic canonical JSON with SHA3-512."""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class AccountsPayableCommandSource:
    """Immutable AP request/selection authority consumed by a generic command."""

    execution_request_id: str
    execution_request_fingerprint: str
    selection_decision_id: str
    selection_decision_fingerprint: str
    payable_id: str
    release_authorization_id: str
    authorized_provider_name: str

    @property
    def family(self) -> FinancialExecutionCommandFamily:
        """Return the closed family fixed by this concrete source type."""
        return FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE

    def __post_init__(self) -> None:
        """Validate complete AP provenance and opaque subject references."""
        for name in ("execution_request_id", "selection_decision_id", "payable_id", "release_authorization_id", "authorized_provider_name"):
            _text(name, getattr(self, name))
        for name in ("execution_request_fingerprint", "selection_decision_fingerprint"):
            _fingerprint(name, getattr(self, name))

    def payload(self) -> dict[str, object]:
        """Return the complete persisted AP source payload."""
        return {
            "execution_request_id": self.execution_request_id,
            "execution_request_fingerprint": self.execution_request_fingerprint,
            "selection_decision_id": self.selection_decision_id,
            "selection_decision_fingerprint": self.selection_decision_fingerprint,
            "payable_id": self.payable_id,
            "release_authorization_id": self.release_authorization_id,
            "authorized_provider_name": self.authorized_provider_name,
        }

    @property
    def fingerprint(self) -> str:
        """Return a deterministic fingerprint of the complete AP source."""
        return _digest({"source_authority_kind": self.family.value, **self.payload()})


@dataclass(frozen=True, slots=True)
class PlatformBillingCommandSource:
    """Immutable Platform Billing request/routing authority for a generic command."""

    execution_request_id: str
    execution_request_fingerprint: str
    routing_decision_id: str
    routing_decision_fingerprint: str
    platform_invoice_id: str
    release_authorization_id: str
    release_authorization_fingerprint: str
    authorized_provider_name: str

    @property
    def family(self) -> FinancialExecutionCommandFamily:
        """Return the closed family fixed by this concrete source type."""
        return FinancialExecutionCommandFamily.PLATFORM_BILLING

    def __post_init__(self) -> None:
        """Validate complete Platform Billing provenance and subject references."""
        for name in ("execution_request_id", "routing_decision_id", "platform_invoice_id", "release_authorization_id", "authorized_provider_name"):
            _text(name, getattr(self, name))
        for name in ("execution_request_fingerprint", "routing_decision_fingerprint", "release_authorization_fingerprint"):
            _fingerprint(name, getattr(self, name))

    def payload(self) -> dict[str, object]:
        """Return the complete persisted Platform Billing source payload."""
        return {
            "execution_request_id": self.execution_request_id,
            "execution_request_fingerprint": self.execution_request_fingerprint,
            "routing_decision_id": self.routing_decision_id,
            "routing_decision_fingerprint": self.routing_decision_fingerprint,
            "platform_invoice_id": self.platform_invoice_id,
            "release_authorization_id": self.release_authorization_id,
            "release_authorization_fingerprint": self.release_authorization_fingerprint,
            "authorized_provider_name": self.authorized_provider_name,
        }

    @property
    def fingerprint(self) -> str:
        """Return a deterministic fingerprint of the complete Platform source."""
        return _digest({"source_authority_kind": self.family.value, **self.payload()})


CommandSource = AccountsPayableCommandSource | PlatformBillingCommandSource


@dataclass(frozen=True, slots=True)
class FinancialExecutionCommand:
    """Immutable family-discriminated authorized instruction before transport."""

    tenant_id: str
    execution_command_id: str
    idempotency_key: str
    amount_minor: int
    currency: str
    payment_destination_reference: str
    source_authority: CommandSource
    provider_name: str
    created_at: datetime
    provider_metadata_reference: str | None = None

    def __post_init__(self) -> None:
        """Validate common material, closed source type, and provider correlation."""
        for name in ("tenant_id", "execution_command_id", "idempotency_key", "payment_destination_reference"):
            _text(name, getattr(self, name))
        if not isinstance(self.amount_minor, int) or isinstance(self.amount_minor, bool) or self.amount_minor <= 0:
            raise FinancialExecutionCommandError("amount_minor must be positive")
        if not isinstance(self.currency, str) or re.fullmatch(r"[A-Z]{3}", self.currency) is None:
            raise FinancialExecutionCommandError("currency must be uppercase 3-letter code")
        if type(self.source_authority) not in (AccountsPayableCommandSource, PlatformBillingCommandSource):
            raise FinancialExecutionCommandError("source_authority is invalid")
        if not isinstance(self.provider_name, str) or not self.provider_name.strip() or _FORBIDDEN.search(self.provider_name):
            raise FinancialExecutionCommandError("provider_name is invalid")
        if self.provider_name != self.source_authority.authorized_provider_name:
            raise FinancialExecutionCommandError("provider/source provider mismatch")
        if self.provider_metadata_reference is not None and (not isinstance(self.provider_metadata_reference, str) or not self.provider_metadata_reference.strip() or _FORBIDDEN.search(self.provider_metadata_reference)):
            raise FinancialExecutionCommandError("invalid provider_metadata_reference")
        if not isinstance(self.created_at, datetime) or self.created_at.tzinfo is None:
            raise FinancialExecutionCommandError("created_at must be timezone-aware")

    @property
    def source_authority_kind(self) -> FinancialExecutionCommandFamily:
        """Return the closed persisted family discriminator."""
        return self.source_authority.family

    @property
    def family(self) -> FinancialExecutionCommandFamily:
        """Compatibility alias for the closed source-authority family."""
        return self.source_authority_kind

    @property
    def payable_id(self) -> str:
        """Project the AP payable subject for existing AP consumers only."""
        if type(self.source_authority) is not AccountsPayableCommandSource:
            raise FinancialExecutionCommandError("payable_id unavailable for Platform Billing command")
        return self.source_authority.payable_id

    @property
    def release_authorization_id(self) -> str:
        """Project the family source release authority for existing consumers."""
        return self.source_authority.release_authorization_id

    def evidence_payload(self) -> dict[str, object]:
        """Return every immutable semantic field used by command fingerprinting."""
        return {
            "tenant_id": self.tenant_id,
            "execution_command_id": self.execution_command_id,
            "idempotency_key": self.idempotency_key,
            "amount_minor": self.amount_minor,
            "currency": self.currency,
            "payment_destination_reference": self.payment_destination_reference,
            "source_authority_kind": self.source_authority_kind.value,
            "source_authority": {"source_authority_kind": self.source_authority_kind.value, **self.source_authority.payload()},
            "provider_name": self.provider_name,
            "provider_metadata_reference": self.provider_metadata_reference,
            "created_at": self.created_at.isoformat(),
        }

    @property
    def fingerprint(self) -> str:
        """Compute the complete deterministic SHA3-512 command fingerprint."""
        return _digest(self.evidence_payload())

    def to_persisted(self) -> dict[str, object]:
        """Return the strict persisted command projection including its fingerprint."""
        return {**self.evidence_payload(), "command_fingerprint": self.fingerprint}

    @classmethod
    def from_persisted(cls, mapping: Mapping[str, Any]) -> "FinancialExecutionCommand":
        """Hydrate one strict command mapping without family or provenance inference."""
        values = dict(mapping)
        values.pop("_id", None)
        stored = values.pop("command_fingerprint", None)
        allowed = {"tenant_id", "execution_command_id", "idempotency_key", "amount_minor", "currency", "payment_destination_reference", "source_authority_kind", "source_authority", "provider_name", "provider_metadata_reference", "created_at"}
        if set(values) != allowed:
            raise FinancialExecutionCommandError("persisted command fields are incomplete or unknown")
        kind = values.pop("source_authority_kind")
        source_mapping = values.pop("source_authority")
        if not isinstance(kind, str):
            raise FinancialExecutionCommandError("source_authority_kind is invalid")
        try:
            family = FinancialExecutionCommandFamily(kind)
        except (TypeError, ValueError) as error:
            raise FinancialExecutionCommandError("source_authority_kind is invalid") from error
        if not isinstance(source_mapping, Mapping):
            raise FinancialExecutionCommandError("source_authority is invalid")
        source_values = dict(source_mapping)
        if source_values.pop("source_authority_kind", None) != family.value:
            raise FinancialExecutionCommandError("source authority family mismatch")
        if family is FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE:
            source = AccountsPayableCommandSource(**source_values)
        else:
            source = PlatformBillingCommandSource(**source_values)
        created_at = values.get("created_at")
        if isinstance(created_at, str):
            try:
                values["created_at"] = datetime.fromisoformat(created_at)
            except ValueError as error:
                raise FinancialExecutionCommandError("created_at is invalid") from error
        values["source_authority"] = source
        command = cls(**values)
        if not isinstance(stored, str) or stored != command.fingerprint:
            raise FinancialExecutionCommandError("command fingerprint mismatch")
        return command


# ARTIFACT: financial_execution_command.py
# VERSION: v2.0.0-M11-P5-R2A
# AUTHORITY BOUNDARY: immutable family-authorized instruction only; no attempt, execution, truth, or settlement authority.
# TENANT POSTURE: tenant-bound identifiers and opaque references only.
# FAIL-CLOSED POSTURE: incomplete, unknown, mixed, divergent, or legacy authority material rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns later execution truth.
# END OF WILSY OS SOVEREIGN ARTIFACT
