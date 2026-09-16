"""Wilsy OS M13-P6B complete usage-window evidence contract.

TITLE: WILSY AI Usage Window Evidence
VERSION: v1.0.0-M13-P6B
AUTHORITY: Wilsy OS Core Governance
EPITOME: Bind an exhaustive, tenant-scoped usage-observation snapshot so
         proven absence can safely derive zero consumption without inventing
         a usage event.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/wilsy_ai_usage_window.py
COLLABORATION / OWNERSHIP: P5A owns source observations; P5B owns the
                            authoritative retrieval that constructs this
                            evidence; P6A consumes it for capacity derivation.
                            No entitlement, IAM, billing, payment, or
                            settlement authority is granted here.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-M13-P6B establishes deterministic complete-window identity,
           strict observation binding, and valid empty-window evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Immutable in-memory evidence; no secrets,
                             clients, persistence, or provider authority.
TENANT BOUNDARY: Tenant, entitlement, module, revision, and fingerprint are
                 bound on every observation and on the window fingerprint.
AUTHORITY BOUNDARY: Completeness of one canonical P6B registry snapshot only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
FAIL-CLOSED DECLARATION: Unknown fields, malformed observations, duplicate
                         evidence, binding drift, chronology drift, and
                         fingerprint mismatch reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import unicodedata
from typing import Any, Final, cast

from tools.eos.saas.domain.wilsy_ai_usage_observation import (
    WilsyAIUsageObservation,
    WilsyAIUsageObservationError,
)

VERSION: Final[str] = "v1.0.0-M13-P6B"
SCHEMA: Final[str] = "WILSY-AI-USAGE-WINDOW/V1"
_FIELDS: Final[tuple[str, ...]] = (
    "schema", "window_version", "tenant_id", "entitlement_id", "module_id",
    "entitlement_revision", "entitlement_fingerprint", "as_of", "window_start",
    "window_end", "observation_count", "observation_fingerprints",
    "observations", "fingerprint",
)
_HEX: Final[frozenset[str]] = frozenset("0123456789abcdef")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset({"default", "global", "root", "*", "global_root"})


class WilsyAIUsageWindowEvidenceError(ValueError):
    """Raised when complete-window evidence cannot be proven or hydrated."""


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise WilsyAIUsageWindowEvidenceError(f"M13P6B_WINDOW_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or any(ord(char) < 32 for char in normalized):
        raise WilsyAIUsageWindowEvidenceError(f"M13P6B_WINDOW_{name.upper()}_INVALID")
    return normalized


def _digest(name: str, value: object) -> str:
    text = _text(name, value)
    if len(text) != 128 or not set(text) <= _HEX:
        raise WilsyAIUsageWindowEvidenceError(f"M13P6B_WINDOW_{name.upper()}_INVALID")
    return text


def _aware(name: str, value: object) -> datetime:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise WilsyAIUsageWindowEvidenceError(f"M13P6B_WINDOW_{name.upper()}_INVALID") from error
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise WilsyAIUsageWindowEvidenceError(f"M13P6B_WINDOW_{name.upper()}_INVALID")
    return value.astimezone(timezone.utc)


def _next_month(start: datetime) -> datetime:
    if start.month == 12:
        return start.replace(year=start.year + 1, month=1)
    return start.replace(month=start.month + 1)


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, WilsyAIUsageObservation):
        return value.to_dict()
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class WilsyAIUsageWindowEvidence:
    """Immutable complete P6B retrieval snapshot, including legitimate emptiness."""

    tenant_id: str
    entitlement_id: str
    module_id: str
    entitlement_revision: int
    entitlement_fingerprint: str
    as_of: datetime
    window_start: datetime
    window_end: datetime
    observation_count: int
    observation_fingerprints: tuple[str, ...]
    observations: tuple[WilsyAIUsageObservation, ...]
    schema: str = SCHEMA
    window_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.window_version != VERSION:
            raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_IDENTITY_INVALID")
        tenant = _text("tenant_id", self.tenant_id)
        if tenant.lower() in _FORBIDDEN_TENANTS:
            raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_TENANT_REQUIRED")
        entitlement_id = _text("entitlement_id", self.entitlement_id)
        module_id = _text("module_id", self.module_id)
        if isinstance(self.entitlement_revision, bool) or not isinstance(self.entitlement_revision, int) or self.entitlement_revision < 0:
            raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_REVISION_INVALID")
        entitlement_fp = _digest("entitlement_fingerprint", self.entitlement_fingerprint)
        as_of = _aware("as_of", self.as_of)
        window_start = _aware("window_start", self.window_start)
        window_end = _aware("window_end", self.window_end)
        expected_start = as_of.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        expected_end = _next_month(expected_start)
        if window_start != expected_start or window_end != as_of or as_of >= expected_end or window_start > window_end:
            raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_BOUNDARY_INVALID")
        if isinstance(self.observation_count, bool) or not isinstance(self.observation_count, int) or self.observation_count < 0:
            raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_COUNT_INVALID")
        if not isinstance(self.observations, tuple) or not isinstance(self.observation_fingerprints, tuple):
            raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_OBSERVATIONS_INVALID")
        if self.observation_count != len(self.observations) or len(self.observation_fingerprints) != self.observation_count:
            raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_COUNT_INVALID")
        seen_ids: set[str] = set()
        seen_fps: set[str] = set()
        validated: list[WilsyAIUsageObservation] = []
        for item in self.observations:
            if not isinstance(item, WilsyAIUsageObservation):
                raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_OBSERVATION_INVALID")
            try:
                observation = WilsyAIUsageObservation.from_dict(item.to_dict())
            except WilsyAIUsageObservationError as error:
                raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_OBSERVATION_INVALID") from error
            if (
                observation.tenant_id != tenant
                or observation.entitlement_id != entitlement_id
                or observation.module_id != module_id
                or observation.entitlement_revision != self.entitlement_revision
                or observation.entitlement_fingerprint != entitlement_fp
                or observation.occurred_at < window_start
                or observation.occurred_at > window_end
            ):
                raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_BINDING_CONFLICT")
            if observation.usage_observation_id in seen_ids or observation.fingerprint in seen_fps:
                raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_DUPLICATE_EVIDENCE")
            seen_ids.add(observation.usage_observation_id)
            seen_fps.add(observation.fingerprint)
            validated.append(observation)
        ordered = tuple(sorted(validated, key=lambda item: (item.occurred_at, item.usage_observation_id)))
        if ordered != tuple(validated):
            raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_ORDER_INVALID")
        expected_fps = tuple(item.fingerprint for item in ordered)
        if self.observation_fingerprints != expected_fps:
            raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_FINGERPRINTS_INVALID")
        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "entitlement_id", entitlement_id)
        object.__setattr__(self, "module_id", module_id)
        object.__setattr__(self, "entitlement_fingerprint", entitlement_fp)
        object.__setattr__(self, "as_of", as_of)
        object.__setattr__(self, "window_start", window_start)
        object.__setattr__(self, "window_end", window_end)
        payload = {_field: _json_value(getattr(self, _field)) for _field in _FIELDS[:-1]}
        digest = hashlib.sha3_512(json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=False, separators=(",", ":")).encode("utf-8")).hexdigest()
        if self.fingerprint and (not isinstance(self.fingerprint, str) or not hmac.compare_digest(self.fingerprint, digest)):
            raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact complete-window evidence contract."""
        return {_field: _json_value(getattr(self, _field)) for _field in _FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "WilsyAIUsageWindowEvidence":
        """Strictly hydrate complete-window evidence and verify its digest."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        for field in ("as_of", "window_start", "window_end"):
            if isinstance(values.get(field), str):
                values[field] = _aware(field, values[field])
        raw_observations = values.get("observations")
        raw_fingerprints = values.get("observation_fingerprints")
        if not isinstance(raw_observations, (list, tuple)) or not isinstance(raw_fingerprints, (list, tuple)):
            raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_OBSERVATIONS_INVALID")
        hydrated: list[WilsyAIUsageObservation] = []
        for raw in raw_observations:
            if isinstance(raw, WilsyAIUsageObservation):
                hydrated.append(raw)
            elif isinstance(raw, Mapping):
                try:
                    hydrated.append(WilsyAIUsageObservation.from_dict(raw))
                except WilsyAIUsageObservationError as error:
                    raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_OBSERVATION_INVALID") from error
            else:
                raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_OBSERVATION_INVALID")
        values["observations"] = tuple(hydrated)
        values["observation_fingerprints"] = tuple(cast(Any, raw_fingerprints))
        item = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, item.fingerprint):
            raise WilsyAIUsageWindowEvidenceError("M13P6B_WINDOW_FINGERPRINT_MISMATCH")
        return item


__all__ = ["SCHEMA", "VERSION", "WilsyAIUsageWindowEvidence", "WilsyAIUsageWindowEvidenceError"]

# ARTIFACT: wilsy_ai_usage_window.py
# VERSION: v1.0.0-M13-P6B
# AUTHORITY BOUNDARY: complete P6B usage-window evidence only
# TENANT POSTURE: explicit tenant/entitlement/module binding
# FAIL-CLOSED POSTURE: strict immutable validation and deterministic SHA3-512
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
