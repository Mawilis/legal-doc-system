"""Wilsy OS M13-P5A immutable WILSY AI usage-observation fact.

TITLE: WILSY AI Usage Observation
VERSION: v1.0.0-M13-P5A
AUTHORITY: Wilsy OS Core Governance
EPITOME: Record only source-evidenced AI resource consumption; never infer
         entitlement, quota, billing, execution, or settlement truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/wilsy_ai_usage_observation.py
COLLABORATION / OWNERSHIP: P3 owns commercial policy; P4 owns entitlement
                            lifecycle; P5A owns this immutable observation
                            fact; P5B will own persistence; Kennel EOS owns
                            financial execution and settlement.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M13-P5A establishes strict V1 observation evidence,
           deterministic SHA3-512 identity, and source-only consumption facts.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No secrets, clients, network, persistence, or
                             identity authority.
TENANT BOUNDARY: Every observation carries an explicit tenant_id and exact
                 entitlement/module references.
AUTHORITY BOUNDARY: Observed resource consumption only; no access grant,
                    quota, invoice, payment, execution, or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
FAIL-CLOSED DECLARATION: Missing/extra fields, invalid quantities/timestamps,
                         malformed evidence, and fingerprint drift reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import unicodedata
from typing import Any, Final, cast

VERSION: Final[str] = "v1.0.0-M13-P5A"
SCHEMA: Final[str] = "WILSY-AI-USAGE-OBSERVATION/V1"
_FIELDS: Final[tuple[str, ...]] = (
    "schema", "observation_version", "tenant_id", "usage_observation_id",
    "entitlement_id", "entitlement_revision", "entitlement_fingerprint",
    "module_id", "request_units", "input_tokens", "output_tokens",
    "automation_actions", "occurred_at", "source_evidence_reference",
    "source_evidence_fingerprint", "fingerprint",
)
_HEX = frozenset("0123456789abcdef")


class WilsyAIUsageObservationError(ValueError):
    """Raised when an observed-consumption fact violates the closed contract."""


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise WilsyAIUsageObservationError(f"M13P5A_INVALID_{name.upper()}")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or any(ord(char) < 32 for char in normalized):
        raise WilsyAIUsageObservationError(f"M13P5A_INVALID_{name.upper()}")
    return normalized


def _digest(name: str, value: object) -> str:
    text = _text(name, value)
    if len(text) != 128 or not set(text) <= _HEX:
        raise WilsyAIUsageObservationError(f"M13P5A_INVALID_{name.upper()}")
    return text


def _nonnegative(name: str, value: object, *, positive: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0 or (positive and value <= 0):
        raise WilsyAIUsageObservationError(f"M13P5A_INVALID_{name.upper()}")
    return value


def _occurred(value: object) -> datetime:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise WilsyAIUsageObservationError("M13P5A_INVALID_OCCURRED_AT") from error
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise WilsyAIUsageObservationError("M13P5A_INVALID_OCCURRED_AT")
    return value.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return value


@dataclass(frozen=True, slots=True)
class WilsyAIUsageObservation:
    """Immutable source-evidenced resource-consumption observation."""

    tenant_id: str
    usage_observation_id: str
    entitlement_id: str
    entitlement_revision: int
    entitlement_fingerprint: str
    module_id: str
    request_units: int
    input_tokens: int
    output_tokens: int
    automation_actions: int
    occurred_at: datetime
    source_evidence_reference: str
    source_evidence_fingerprint: str
    schema: str = SCHEMA
    observation_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _text("tenant_id", self.tenant_id)
        if tenant.lower() in {"default", "global", "root", "*", "global_root"}:
            raise WilsyAIUsageObservationError("M13P5A_TENANT_REQUIRED")
        values = {
            "usage_observation_id": _text("usage_observation_id", self.usage_observation_id),
            "entitlement_id": _text("entitlement_id", self.entitlement_id),
            "module_id": _text("module_id", self.module_id),
        }
        if self.schema != SCHEMA or self.observation_version != VERSION:
            raise WilsyAIUsageObservationError("M13P5A_IDENTITY_INVALID")
        revision = _nonnegative("entitlement_revision", self.entitlement_revision)
        entitlement_fp = _digest("entitlement_fingerprint", self.entitlement_fingerprint)
        request_units = _nonnegative("request_units", self.request_units, positive=True)
        input_tokens = _nonnegative("input_tokens", self.input_tokens)
        output_tokens = _nonnegative("output_tokens", self.output_tokens)
        actions = _nonnegative("automation_actions", self.automation_actions)
        occurred = _occurred(self.occurred_at)
        source_ref = _text("source_evidence_reference", self.source_evidence_reference)
        source_fp = _digest("source_evidence_fingerprint", self.source_evidence_fingerprint)
        object.__setattr__(self, "tenant_id", tenant); object.__setattr__(self, "entitlement_revision", revision)
        object.__setattr__(self, "entitlement_fingerprint", entitlement_fp); object.__setattr__(self, "request_units", request_units)
        object.__setattr__(self, "input_tokens", input_tokens); object.__setattr__(self, "output_tokens", output_tokens)
        object.__setattr__(self, "automation_actions", actions); object.__setattr__(self, "occurred_at", occurred)
        object.__setattr__(self, "source_evidence_reference", source_ref); object.__setattr__(self, "source_evidence_fingerprint", source_fp)
        for field, value in values.items(): object.__setattr__(self, field, value)
        payload = {key: _json_value(getattr(self, key)) for key in _FIELDS[:-1]}
        digest = hashlib.sha3_512(json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=False, separators=(",", ":")).encode("utf-8")).hexdigest()
        if self.fingerprint and (len(self.fingerprint) != 128 or set(self.fingerprint) > _HEX or not hmac.compare_digest(self.fingerprint, digest)):
            raise WilsyAIUsageObservationError("M13P5A_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize all and only authority-bearing observation fields."""
        return {key: _json_value(getattr(self, key)) for key in _FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "WilsyAIUsageObservation":
        """Strictly hydrate a persisted/transport observation and verify its digest."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            raise WilsyAIUsageObservationError("M13P5A_SCHEMA_INVALID")
        values = dict(payload); stored = values.pop("fingerprint")
        observation = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, observation.fingerprint):
            raise WilsyAIUsageObservationError("M13P5A_FINGERPRINT_MISMATCH")
        return observation


__all__ = ["SCHEMA", "VERSION", "WilsyAIUsageObservation", "WilsyAIUsageObservationError"]

# ARTIFACT: wilsy_ai_usage_observation.py
# VERSION: v1.0.0-M13-P5A
# AUTHORITY BOUNDARY: observed resource consumption only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
