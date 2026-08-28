"""Canonical provider-neutral semantic material for one financial send.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TRANSPORT-MATERIAL
TITLE: Financial Execution Transport Material Domain
PURPOSE: Bind immutable financial and routing semantics before provider I/O.
AUTHORITY: Pre-transport semantic authority only; no credentials, wire payload, provider outcome, truth, or settlement.
EPITOME: Deterministic reconstruction lets a dispatch claim and future transport evidence prove the exact intended send.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/domain/financial_execution_transport_material.py
CERTIFICATION DATE: 2026-08-28
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque references and fingerprints only; credentials and provider payloads are forbidden.
TENANT BOUNDARY: tenant, command, attempt, destination, and transport correlation are explicit and immutable.
FINANCIAL AUTHORITY BOUNDARY: semantic send material only; Kennel EOS owns execution truth and settlement remains separate.
TRANSACTION BOUNDARY: pure value object; no persistence, network, retry, CAS, or transaction lifecycle ownership.
CHANGELOG: v1.0.0 establishes deterministic secret-free transport material and SHA3-512 reconstruction authority.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass

VERSION = "v1.0.0-KENNEL-FINANCIAL-EXECUTION-TRANSPORT-MATERIAL"
_HEX = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN = re.compile(r"bank|account|card|secret|token|credential|password|private[_ -]?key|api[_ -]?key", re.IGNORECASE)


class FinancialExecutionTransportMaterialError(ValueError):
    """Fail-closed validation error for malformed semantic transport material."""


def _opaque(value: object, name: str, *, required: bool = True) -> str | None:
    if value is None and not required:
        return None
    if not isinstance(value, str) or not value.strip() or _FORBIDDEN.search(value):
        raise FinancialExecutionTransportMaterialError(f"{name} is invalid")
    return value


def _fingerprint(value: object, name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        raise FinancialExecutionTransportMaterialError(f"{name} must be lowercase SHA3-512 hex")
    return value


@dataclass(frozen=True)
class FinancialExecutionTransportMaterial:
    """Immutable semantic send authority, distinct from provider wire bytes and outcomes."""

    tenant_id: str
    execution_command_id: str
    execution_attempt_id: str
    provider_name: str
    transport_correlation_id: str
    amount_minor: int
    currency: str
    payment_destination_reference: str
    destination_fingerprint: str | None = None
    provider_metadata_reference: str | None = None
    provider_configuration_reference: str | None = None
    provider_configuration_fingerprint: str | None = None

    def __post_init__(self) -> None:
        for name in ("tenant_id", "execution_command_id", "execution_attempt_id", "provider_name", "transport_correlation_id", "payment_destination_reference"):
            _opaque(getattr(self, name), name)
        if self.execution_command_id == self.execution_attempt_id:
            raise FinancialExecutionTransportMaterialError("command and attempt identities must differ")
        if not isinstance(self.amount_minor, int) or isinstance(self.amount_minor, bool) or self.amount_minor <= 0:
            raise FinancialExecutionTransportMaterialError("amount_minor must be positive")
        if not isinstance(self.currency, str) or re.fullmatch(r"[A-Z]{3}", self.currency) is None:
            raise FinancialExecutionTransportMaterialError("currency must be uppercase 3-letter code")
        _opaque(self.provider_metadata_reference, "provider_metadata_reference", required=False)
        _opaque(self.provider_configuration_reference, "provider_configuration_reference", required=False)
        _fingerprint(self.destination_fingerprint, "destination_fingerprint")
        _fingerprint(self.provider_configuration_fingerprint, "provider_configuration_fingerprint")

    def canonical_payload(self) -> dict[str, object]:
        """Return the explicit, deterministic semantic payload with stable null handling."""
        return {
            "amount_minor": self.amount_minor,
            "currency": self.currency,
            "destination_fingerprint": self.destination_fingerprint,
            "execution_attempt_id": self.execution_attempt_id,
            "execution_command_id": self.execution_command_id,
            "payment_destination_reference": self.payment_destination_reference,
            "provider_configuration_fingerprint": self.provider_configuration_fingerprint,
            "provider_configuration_reference": self.provider_configuration_reference,
            "provider_metadata_reference": self.provider_metadata_reference,
            "provider_name": self.provider_name,
            "tenant_id": self.tenant_id,
            "transport_correlation_id": self.transport_correlation_id,
        }

    def canonical_bytes(self) -> bytes:
        """Serialize semantic material as compact sorted UTF-8 JSON."""
        return json.dumps(self.canonical_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

    @property
    def fingerprint(self) -> str:
        """Return the canonical lowercase SHA3-512 semantic-material fingerprint."""
        return hashlib.sha3_512(self.canonical_bytes()).hexdigest()


# ARTIFACT: financial_execution_transport_material.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TRANSPORT-MATERIAL
# AUTHORITY BOUNDARY: canonical pre-transport semantics only; no wire, provider, truth, or settlement authority.
# TENANT POSTURE: all identities and opaque references are explicit and immutable.
# FAIL-CLOSED POSTURE: malformed identity, amount, currency, reference, or fingerprint is rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; execution is not settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
