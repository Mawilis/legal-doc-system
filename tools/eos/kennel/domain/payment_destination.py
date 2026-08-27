# -*- coding: utf-8 -*-
"""WILSY OS provider-independent payment destination authority contract.

VERSION: v1.0.0-KENNEL-PAYMENT-DESTINATION-AUTHORITY-DOMAIN
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable tenant/beneficiary-bound destination identity; no credentials or execution.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/domain/payment_destination.py
COLLABORATION: Wilson Khanyezi (Founder/Chief Architect); Codex (AI Engineering)
CHANGELOG: v1.0.0 establishes provider-independent destination identity, verification, revocation, and evidence.
COMPLIANCE: POPIA §19 | GDPR Art. 32 | SOC2 CC7.2
SECURITY: opaque references only; raw credentials are rejected.
AUTHORITY BOUNDARY: destination eligibility only; Kennel EOS owns financial execution.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping

VERSION = "v1.0.0-KENNEL-PAYMENT-DESTINATION-AUTHORITY-DOMAIN"
_OPAQUE_FORBIDDEN = re.compile(r"bank[_ -]?account|account[_ -]?number|branch[_ -]?code|card[_ -]?number|card[_ -]?pan|cvv|credential|password|secret|private[_ -]?key|access[_ -]?token|refresh[_ -]?token|api[_ -]?key", re.I)


class PaymentDestinationError(ValueError):
    """Raised when destination identity, ownership, lifecycle, or evidence is invalid."""


class PaymentDestinationStatus(StrEnum):
    """Lifecycle state describing whether a destination may be considered for use."""

    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class PaymentDestinationVerificationState(StrEnum):
    """Verification state; existence never implies external verification."""

    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 240:
        raise PaymentDestinationError(f"{name} is invalid")
    return value.strip()


def _opaque(value: Any, name: str) -> str:
    result = _text(value, name)
    if _OPAQUE_FORBIDDEN.search(result):
        raise PaymentDestinationError(f"{name} must be opaque")
    return result


def _aware(value: Any, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise PaymentDestinationError(f"{name} must be timezone-aware")
    return value


@dataclass(frozen=True)
class PaymentDestination:
    """Immutable tenant-scoped destination identity with no provider or settlement authority."""

    payment_destination_id: str
    tenant_id: str
    beneficiary_id: str
    destination_reference: str
    status: PaymentDestinationStatus
    verification_state: PaymentDestinationVerificationState
    created_at: datetime
    destination_type: str | None = None
    provider_metadata_reference: str | None = None
    verified_at: datetime | None = None
    revoked_at: datetime | None = None

    def __post_init__(self) -> None:
        for name in ("payment_destination_id", "tenant_id", "beneficiary_id"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        object.__setattr__(self, "destination_reference", _opaque(self.destination_reference, "destination_reference"))
        if not isinstance(self.status, PaymentDestinationStatus) or not isinstance(self.verification_state, PaymentDestinationVerificationState):
            raise PaymentDestinationError("destination lifecycle state is invalid")
        object.__setattr__(self, "created_at", _aware(self.created_at, "created_at"))
        if self.destination_type is not None:
            object.__setattr__(self, "destination_type", _opaque(self.destination_type, "destination_type"))
        if self.provider_metadata_reference is not None:
            object.__setattr__(self, "provider_metadata_reference", _opaque(self.provider_metadata_reference, "provider_metadata_reference"))
        if self.verified_at is not None:
            object.__setattr__(self, "verified_at", _aware(self.verified_at, "verified_at"))
        if self.revoked_at is not None:
            object.__setattr__(self, "revoked_at", _aware(self.revoked_at, "revoked_at"))
        if self.status is PaymentDestinationStatus.REVOKED and self.revoked_at is None:
            raise PaymentDestinationError("revoked destination requires revoked_at")

    @property
    def is_execution_eligible(self) -> bool:
        """Return whether a resolver may consider this destination, without authorizing execution."""
        return self.status is PaymentDestinationStatus.ACTIVE and self.verification_state is PaymentDestinationVerificationState.VERIFIED

    def evidence_payload(self) -> dict[str, Any]:
        """Return deterministic non-secret destination truth for fingerprinting."""
        return {"payment_destination_id": self.payment_destination_id, "tenant_id": self.tenant_id, "beneficiary_id": self.beneficiary_id, "destination_reference": self.destination_reference, "status": self.status.value, "verification_state": self.verification_state.value, "created_at": self.created_at.isoformat(), "destination_type": self.destination_type, "provider_metadata_reference": self.provider_metadata_reference, "verified_at": self.verified_at.isoformat() if self.verified_at else None, "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None}

    @property
    def fingerprint(self) -> str:
        """Return canonical SHA3-512 evidence, distinct from credentials and authorization."""
        return hashlib.sha3_512(json.dumps(self.evidence_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()

    def to_persistence_dict(self) -> dict[str, Any]:
        """Serialize only provider-independent, non-secret destination state."""
        return self.evidence_payload()

    @classmethod
    def from_persistence_dict(cls, value: Mapping[str, Any]) -> "PaymentDestination":
        """Hydrate strict enums and aware timestamps, rejecting malformed persisted truth."""
        try:
            data = dict(value)
            for key in ("created_at", "verified_at", "revoked_at"):
                if isinstance(data.get(key), str):
                    data[key] = datetime.fromisoformat(data[key])
            data["status"] = PaymentDestinationStatus(data["status"])
            data["verification_state"] = PaymentDestinationVerificationState(data["verification_state"])
            forbidden = {"account_number", "bank_account", "card_number", "cvv", "secret", "token", "password", "private_key"}
            if forbidden.intersection(data):
                raise PaymentDestinationError("forbidden destination fields")
            return cls(**data)
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, PaymentDestinationError):
                raise
            raise PaymentDestinationError("invalid persisted payment destination") from error


# ARTIFACT: payment_destination.py
# VERSION: v1.0.0-KENNEL-PAYMENT-DESTINATION-AUTHORITY-DOMAIN
# AUTHORITY BOUNDARY: destination identity and eligibility only; no execution or settlement.
# TENANT POSTURE: tenant_id and beneficiary_id are mandatory and immutable.
# FAIL-CLOSED POSTURE: malformed, revoked, unverified, or sensitive input is rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution truth.
# END OF WILSY OS SOVEREIGN ARTIFACT
