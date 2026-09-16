"""TITLE: WILSY AI Usage Admission Domain.
VERSION: v1.0.0-C1B-R2
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Immutable tenant-scoped reservations that gate future reasoning
         execution without becoming usage, provider, billing, or settlement truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/wilsy_ai_usage_admission.py
COLLABORATION / OWNERSHIP: C1B admission authority; P4/P6 capacity remain
                            canonical; callers own Mongo transactions.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1B-R2 establishes deterministic admission identity,
           held-capacity states, reconciliation uncertainty, and strict replay.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No prompts, secrets, provider responses, or PII.
TENANT BOUNDARY: Every identity and replay value is tenant-bound.
AUTHORITY BOUNDARY: Reservation evidence only; no provider execution or usage.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Invalid chronology, state, identity, binding, or
                         fingerprint rejects deterministically.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Final, cast

VERSION: Final[str] = "v1.0.0-C1B-R2"
SCHEMA: Final[str] = "WILSY-AI-USAGE-ADMISSION/V1"
_HEX = frozenset("0123456789abcdef")
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_FORBIDDEN = frozenset({"default", "global", "root", "*", "global_root"})


class WilsyAIUsageAdmissionError(ValueError):
    """Raised when immutable admission evidence violates its contract."""


class WilsyAIUsageAdmissionState(StrEnum):
    """Closed reservation lifecycle; only server authority may transition it."""

    RESERVED = "RESERVED"
    CLAIMED = "CLAIMED"
    COMPLETED = "COMPLETED"
    RELEASED = "RELEASED"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"


def canonical_json(value: object) -> str:
    """Return deterministic canonical JSON for command and evidence hashing."""
    def convert(item: object) -> object:
        if isinstance(item, datetime):
            return item.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        if isinstance(item, StrEnum):
            return item.value
        if isinstance(item, tuple):
            return [convert(v) for v in item]
        if isinstance(item, Mapping):
            return {str(k): convert(v) for k, v in item.items()}
        return item
    try:
        return json.dumps(convert(value), ensure_ascii=False, allow_nan=False,
                          sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as error:
        raise WilsyAIUsageAdmissionError("C1B_ADMISSION_SERIALIZATION_INVALID") from error


def sha3_512_fingerprint(value: object) -> str:
    """Hash canonical admission semantics with SHA3-512."""
    return hashlib.sha3_512(canonical_json(value).encode("utf-8")).hexdigest()


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        raise WilsyAIUsageAdmissionError(f"C1B_ADMISSION_{name.upper()}_INVALID")
    return value


def _digest(name: str, value: object) -> str:
    if not isinstance(value, str) or len(value) != 128 or not set(value) <= _HEX:
        raise WilsyAIUsageAdmissionError(f"C1B_ADMISSION_{name.upper()}_INVALID")
    return value


def _when(name: str, value: object) -> datetime:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise WilsyAIUsageAdmissionError(f"C1B_ADMISSION_{name.upper()}_INVALID") from error
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise WilsyAIUsageAdmissionError(f"C1B_ADMISSION_{name.upper()}_INVALID")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class WilsyAIUsageAdmission:
    """Immutable reservation evidence; reservation is never an observation."""

    tenant_id: str
    admission_id: str
    idempotency_key: str
    entitlement_id: str
    module_id: str
    entitlement_revision: int
    entitlement_fingerprint: str
    window_start: datetime
    window_end: datetime
    reserved_request_units: int = 1
    state: WilsyAIUsageAdmissionState | str = WilsyAIUsageAdmissionState.RESERVED
    created_at: datetime | None = None
    updated_at: datetime | None = None
    evidence_reference: str | None = None
    schema: str = SCHEMA
    admission_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _identity("tenant_id", self.tenant_id)
        if tenant.casefold() in _FORBIDDEN:
            raise WilsyAIUsageAdmissionError("C1B_ADMISSION_TENANT_REQUIRED")
        for name in ("admission_id", "idempotency_key", "entitlement_id", "module_id"):
            _identity(name, getattr(self, name))
        if self.schema != SCHEMA or self.admission_version != VERSION:
            raise WilsyAIUsageAdmissionError("C1B_ADMISSION_IDENTITY_INVALID")
        if isinstance(self.entitlement_revision, bool) or not isinstance(self.entitlement_revision, int) or self.entitlement_revision < 0:
            raise WilsyAIUsageAdmissionError("C1B_ADMISSION_REVISION_INVALID")
        _digest("entitlement_fingerprint", self.entitlement_fingerprint)
        if isinstance(self.reserved_request_units, bool) or not isinstance(self.reserved_request_units, int) or self.reserved_request_units <= 0:
            raise WilsyAIUsageAdmissionError("C1B_ADMISSION_UNITS_INVALID")
        try:
            state = WilsyAIUsageAdmissionState(self.state)
        except (TypeError, ValueError) as error:
            raise WilsyAIUsageAdmissionError("C1B_ADMISSION_STATE_INVALID") from error
        start, end = _when("window_start", self.window_start), _when("window_end", self.window_end)
        if start >= end:
            raise WilsyAIUsageAdmissionError("C1B_ADMISSION_WINDOW_INVALID")
        created = _when("created_at", self.created_at or start)
        updated = _when("updated_at", self.updated_at or created)
        if updated < created:
            raise WilsyAIUsageAdmissionError("C1B_ADMISSION_CHRONOLOGY_INVALID")
        if self.evidence_reference is not None:
            _identity("evidence_reference", self.evidence_reference)
        object.__setattr__(self, "tenant_id", tenant); object.__setattr__(self, "state", state)
        object.__setattr__(self, "window_start", start); object.__setattr__(self, "window_end", end)
        object.__setattr__(self, "created_at", created); object.__setattr__(self, "updated_at", updated)
        payload = {k: getattr(self, k) for k in self._semantic_fields()}
        digest = sha3_512_fingerprint(payload)
        if self.fingerprint and (not hmac.compare_digest(self.fingerprint, digest)):
            raise WilsyAIUsageAdmissionError("C1B_ADMISSION_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @staticmethod
    def _semantic_fields() -> tuple[str, ...]:
        return ("schema", "admission_version", "tenant_id", "admission_id", "idempotency_key", "entitlement_id", "module_id", "entitlement_revision", "entitlement_fingerprint", "window_start", "window_end", "reserved_request_units", "state", "created_at", "updated_at", "evidence_reference")

    def to_dict(self) -> dict[str, object]:
        """Serialize exact durable admission evidence."""
        return {key: getattr(self, key) for key in (*self._semantic_fields(), "fingerprint")}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "WilsyAIUsageAdmission":
        """Hydrate and verify exact immutable evidence."""
        expected = set(cls._semantic_fields()) | {"fingerprint"}
        if not isinstance(payload, Mapping) or set(payload) != expected:
            raise WilsyAIUsageAdmissionError("C1B_ADMISSION_SCHEMA_INVALID")
        values = dict(payload); stored = values.pop("fingerprint")
        item = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, item.fingerprint):
            raise WilsyAIUsageAdmissionError("C1B_ADMISSION_FINGERPRINT_MISMATCH")
        return item

    def transition(self, target_state: WilsyAIUsageAdmissionState | str, *, occurred_at: datetime, evidence_reference: str) -> "WilsyAIUsageAdmission":
        """Return one legal immutable transition; no transaction is owned."""
        try:
            target = WilsyAIUsageAdmissionState(target_state)
        except (TypeError, ValueError) as error:
            raise WilsyAIUsageAdmissionError("C1B_ADMISSION_STATE_INVALID") from error
        legal = {
            WilsyAIUsageAdmissionState.RESERVED: {WilsyAIUsageAdmissionState.CLAIMED, WilsyAIUsageAdmissionState.RELEASED, WilsyAIUsageAdmissionState.RECONCILIATION_REQUIRED},
            WilsyAIUsageAdmissionState.CLAIMED: {WilsyAIUsageAdmissionState.COMPLETED, WilsyAIUsageAdmissionState.RECONCILIATION_REQUIRED},
            WilsyAIUsageAdmissionState.RECONCILIATION_REQUIRED: {WilsyAIUsageAdmissionState.RELEASED},
            WilsyAIUsageAdmissionState.COMPLETED: set(), WilsyAIUsageAdmissionState.RELEASED: set(),
        }
        current_state = WilsyAIUsageAdmissionState(self.state)
        if target not in legal[current_state]:
            raise WilsyAIUsageAdmissionError("C1B_ADMISSION_ILLEGAL_TRANSITION")
        values = {key: getattr(self, key) for key in self._semantic_fields()}
        values.update(state=target, updated_at=_when("occurred_at", occurred_at), evidence_reference=_identity("evidence_reference", evidence_reference), fingerprint="")
        return WilsyAIUsageAdmission(**cast(Any, values))


__all__ = ["VERSION", "SCHEMA", "WilsyAIUsageAdmission", "WilsyAIUsageAdmissionError", "WilsyAIUsageAdmissionState", "canonical_json", "sha3_512_fingerprint"]

# ARTIFACT: wilsy_ai_usage_admission.py
# VERSION: v1.0.0-C1B-R2
# AUTHORITY BOUNDARY: immutable capacity reservation evidence only
# TENANT POSTURE: explicit tenant identity on every admission
# FAIL-CLOSED POSTURE: strict state, chronology, replay and digest validation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
