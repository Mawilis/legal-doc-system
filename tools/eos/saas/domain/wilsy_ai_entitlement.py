"""Wilsy OS M13-P4 canonical WILSY AI entitlement authority.

TITLE: WILSY AI Entitlement Domain
VERSION: v1.0.0-M13-P4
AUTHORITY: Wilsy OS Core Governance
EPITOME: Own immutable tenant/module entitlement lifecycle facts bound to the
         certified P3 commercial-policy fingerprint.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/wilsy_ai_entitlement.py
COLLABORATION / OWNERSHIP: P3 owns commercial policy; this domain owns
                            entitlement truth; the registry owns persistence;
                            WilsyAIVASAccess is a projection and Kennel EOS
                            owns financial execution and settlement.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M13-P4 establishes strict immutable entitlement evidence,
           revisioned legal transitions, chronology validation, and deterministic
           SHA3-512 identity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No secrets, clients, network, KMS, usage, or
                             payment state.
TENANT BOUNDARY: Every entitlement is explicitly tenant-scoped.
AUTHORITY BOUNDARY: Entitlement lifecycle evidence only; no entitlement
                    inference, metering, invoicing, execution, or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
FAIL-CLOSED DECLARATION: Unknown fields, altered P3 binding, malformed
                         lifecycle evidence, and fingerprint drift reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import hmac
import json
import unicodedata
from typing import Any, Final, cast

from tools.eos.saas.billing.wilsy_ai_commercial_policy import (
    WilsyAITier,
    get_wilsy_ai_commercial_policy,
)

VERSION: Final[str] = "v1.0.0-M13-P4"
SCHEMA: Final[str] = "WILSY-AI-ENTITLEMENT/V1"
_FIELDS: Final[tuple[str, ...]] = (
    "schema", "entitlement_version", "lifecycle_revision", "tenant_id", "entitlement_id", "module_id",
    "module_name", "tier", "policy_fingerprint", "lifecycle_state", "source_requirements",
    "capability_grants", "source_readiness_evidence_reference",
    "source_readiness_evidence_fingerprint", "activated_at", "activation_evidence_reference",
    "activation_evidence_fingerprint", "suspended_at", "suspension_evidence_reference",
    "suspension_evidence_fingerprint", "revoked_at", "revocation_evidence_reference",
    "revocation_evidence_fingerprint", "fingerprint",
)
ENTITLEMENT_FIELDS: Final[tuple[str, ...]] = _FIELDS
_DIGEST = frozenset("0123456789abcdef")
_HEX128 = lambda v: isinstance(v, str) and len(v) == 128 and set(v) <= _DIGEST


class WilsyAIEntitlementError(ValueError):
    """Raised when an entitlement violates its closed authority contract."""


class WilsyAIEntitlementState(str, Enum):
    """Closed entitlement lifecycle states."""

    PENDING_SOURCE = "PENDING_SOURCE"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise WilsyAIEntitlementError(f"M13P4_INVALID_{name.upper()}")
    value = unicodedata.normalize("NFC", value)
    if not value or any(ord(c) < 32 for c in value):
        raise WilsyAIEntitlementError(f"M13P4_INVALID_{name.upper()}")
    return value


def _when(name: str, value: object) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise WilsyAIEntitlementError(f"M13P4_INVALID_{name.upper()}") from error
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise WilsyAIEntitlementError(f"M13P4_INVALID_{name.upper()}")
    return value.astimezone(timezone.utc)


def _ref(name: str, value: object, fingerprint: object) -> tuple[str | None, str | None]:
    if value is None and fingerprint is None:
        return None, None
    ref = _text(name, value)
    if not _HEX128(fingerprint):
        raise WilsyAIEntitlementError(f"M13P4_INVALID_{name}_FINGERPRINT")
    return ref, cast(str, fingerprint)


def _items(name: str, value: object) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)) or not value:
        raise WilsyAIEntitlementError(f"M13P4_INVALID_{name.upper()}")
    result = tuple(_text(name, item) for item in value)
    if len(set(result)) != len(result):
        raise WilsyAIEntitlementError(f"M13P4_DUPLICATE_{name.upper()}")
    return result


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, tuple):
        return [_json_value(v) for v in value]
    return value


@dataclass(frozen=True, slots=True)
class WilsyAIEntitlement:
    """Immutable tenant/module entitlement lifecycle evidence."""

    tenant_id: str
    entitlement_id: str
    module_id: str
    module_name: str
    tier: WilsyAITier | str
    policy_fingerprint: str
    lifecycle_state: WilsyAIEntitlementState | str
    source_requirements: tuple[str, ...]
    capability_grants: tuple[str, ...]
    source_readiness_evidence_reference: str | None = None
    source_readiness_evidence_fingerprint: str | None = None
    activated_at: datetime | None = None
    activation_evidence_reference: str | None = None
    activation_evidence_fingerprint: str | None = None
    suspended_at: datetime | None = None
    suspension_evidence_reference: str | None = None
    suspension_evidence_fingerprint: str | None = None
    revoked_at: datetime | None = None
    revocation_evidence_reference: str | None = None
    revocation_evidence_fingerprint: str | None = None
    schema: str = SCHEMA
    entitlement_version: str = VERSION
    lifecycle_revision: int = 0
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _text("tenant_id", self.tenant_id)
        if tenant.lower() in {"default", "global", "root", "*"}:
            raise WilsyAIEntitlementError("M13P4_TENANT_REQUIRED")
        entitlement = _text("entitlement_id", self.entitlement_id)
        module = _text("module_id", self.module_id)
        name = _text("module_name", self.module_name)
        try:
            tier = WilsyAITier(self.tier)
            state = WilsyAIEntitlementState(self.lifecycle_state)
        except (TypeError, ValueError) as error:
            raise WilsyAIEntitlementError("M13P4_ENUM_INVALID") from error
        if self.schema != SCHEMA or self.entitlement_version != VERSION:
            raise WilsyAIEntitlementError("M13P4_IDENTITY_INVALID")
        if isinstance(self.lifecycle_revision, bool) or not isinstance(self.lifecycle_revision, int) or self.lifecycle_revision < 0:
            raise WilsyAIEntitlementError("M13P4_REVISION_INVALID")
        policy = get_wilsy_ai_commercial_policy(tier)
        if self.policy_fingerprint != policy.policy_fingerprint or not _HEX128(self.policy_fingerprint):
            raise WilsyAIEntitlementError("M13P4_POLICY_BINDING_INVALID")
        requirements = _items("source_requirements", self.source_requirements)
        grants = _items("capability_grants", self.capability_grants)
        readiness_ref, readiness_fp = _ref("source_readiness_evidence_reference", self.source_readiness_evidence_reference, self.source_readiness_evidence_fingerprint)
        activated = _when("activated_at", self.activated_at)
        activation_ref, activation_fp = _ref("activation_evidence_reference", self.activation_evidence_reference, self.activation_evidence_fingerprint)
        suspended = _when("suspended_at", self.suspended_at)
        suspension_ref, suspension_fp = _ref("suspension_evidence_reference", self.suspension_evidence_reference, self.suspension_evidence_fingerprint)
        revoked = _when("revoked_at", self.revoked_at)
        revocation_ref, revocation_fp = _ref("revocation_evidence_reference", self.revocation_evidence_reference, self.revocation_evidence_fingerprint)
        if readiness_ref is None or readiness_fp is None:
            raise WilsyAIEntitlementError("M13P4_SOURCE_READINESS_REQUIRED")
        if state is WilsyAIEntitlementState.PENDING_SOURCE and any(v is not None for v in (activated, activation_ref, suspended, suspension_ref, revoked, revocation_ref)):
            raise WilsyAIEntitlementError("M13P4_PENDING_SHAPE_INVALID")
        if state is WilsyAIEntitlementState.ACTIVE and (activated is None or activation_ref is None or suspended is not None or revoked is not None or suspension_ref is not None or revocation_ref is not None):
            raise WilsyAIEntitlementError("M13P4_ACTIVE_SHAPE_INVALID")
        if state is WilsyAIEntitlementState.SUSPENDED and (activated is None or activation_ref is None or suspended is None or suspension_ref is None or revoked is not None or revocation_ref is not None):
            raise WilsyAIEntitlementError("M13P4_SUSPENDED_SHAPE_INVALID")
        if state is WilsyAIEntitlementState.REVOKED and (activated is None or activation_ref is None or revoked is None or revocation_ref is None or suspended is not None or suspension_ref is not None):
            raise WilsyAIEntitlementError("M13P4_REVOKED_SHAPE_INVALID")
        if activated is not None and suspended is not None and suspended < activated:
            raise WilsyAIEntitlementError("M13P4_CHRONOLOGY_INVALID")
        if activated is not None and revoked is not None and revoked < activated:
            raise WilsyAIEntitlementError("M13P4_CHRONOLOGY_INVALID")
        object.__setattr__(self, "tenant_id", tenant); object.__setattr__(self, "entitlement_id", entitlement)
        object.__setattr__(self, "module_id", module); object.__setattr__(self, "module_name", name)
        object.__setattr__(self, "tier", tier); object.__setattr__(self, "lifecycle_state", state)
        object.__setattr__(self, "source_requirements", requirements); object.__setattr__(self, "capability_grants", grants)
        for field, value in (("source_readiness_evidence_reference", readiness_ref), ("source_readiness_evidence_fingerprint", readiness_fp), ("activated_at", activated), ("activation_evidence_reference", activation_ref), ("activation_evidence_fingerprint", activation_fp), ("suspended_at", suspended), ("suspension_evidence_reference", suspension_ref), ("suspension_evidence_fingerprint", suspension_fp), ("revoked_at", revoked), ("revocation_evidence_reference", revocation_ref), ("revocation_evidence_fingerprint", revocation_fp)):
            object.__setattr__(self, field, value)
        payload = {k: _json_value(getattr(self, k)) for k in _FIELDS[:-1]}
        digest = hashlib.sha3_512(json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=False, separators=(",", ":")).encode("utf-8")).hexdigest()
        if self.fingerprint and (not _HEX128(self.fingerprint) or not hmac.compare_digest(self.fingerprint, digest)):
            raise WilsyAIEntitlementError("M13P4_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact strict entitlement evidence document."""
        return {k: _json_value(getattr(self, k)) for k in _FIELDS}

    def transition(
        self,
        target_state: WilsyAIEntitlementState | str,
        *,
        expected_revision: int,
        evidence_reference: str,
        evidence_fingerprint: str,
        occurred_at: datetime,
    ) -> "WilsyAIEntitlement":
        """Return one legal revisioned transition; never mutates this value."""
        if isinstance(expected_revision, bool) or not isinstance(expected_revision, int) or expected_revision != self.lifecycle_revision:
            raise WilsyAIEntitlementError("M13P4_STALE_REVISION")
        try:
            target = WilsyAIEntitlementState(target_state)
        except (TypeError, ValueError) as error:
            raise WilsyAIEntitlementError("M13P4_TRANSITION_INVALID") from error
        legal = {
            WilsyAIEntitlementState.PENDING_SOURCE: {WilsyAIEntitlementState.ACTIVE},
            WilsyAIEntitlementState.ACTIVE: {WilsyAIEntitlementState.SUSPENDED, WilsyAIEntitlementState.REVOKED},
            WilsyAIEntitlementState.SUSPENDED: set(),
            WilsyAIEntitlementState.REVOKED: set(),
        }
        if target not in legal[cast(WilsyAIEntitlementState, self.lifecycle_state)]:
            raise WilsyAIEntitlementError("M13P4_ILLEGAL_TRANSITION")
        reference = _text("evidence_reference", evidence_reference)
        if not _HEX128(evidence_fingerprint):
            raise WilsyAIEntitlementError("M13P4_EVIDENCE_FINGERPRINT_INVALID")
        when = _when("occurred_at", occurred_at)
        assert when is not None
        changes: dict[str, object] = {
            "lifecycle_state": target,
            "lifecycle_revision": self.lifecycle_revision + 1,
            "fingerprint": "",
        }
        if target is WilsyAIEntitlementState.ACTIVE:
            changes.update(activated_at=when, activation_evidence_reference=reference, activation_evidence_fingerprint=evidence_fingerprint)
        elif target is WilsyAIEntitlementState.SUSPENDED:
            changes.update(suspended_at=when, suspension_evidence_reference=reference, suspension_evidence_fingerprint=evidence_fingerprint)
        else:
            changes.update(revoked_at=when, revocation_evidence_reference=reference, revocation_evidence_fingerprint=evidence_fingerprint)
        values = {field: getattr(self, field) for field in _FIELDS[:-1]}
        values.update(changes)
        return WilsyAIEntitlement(**cast(Any, values))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "WilsyAIEntitlement":
        """Hydrate exactly the authority fields and verify fingerprint."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            raise WilsyAIEntitlementError("M13P4_SCHEMA_INVALID")
        values = dict(payload); stored = values.pop("fingerprint")
        item = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, item.fingerprint):
            raise WilsyAIEntitlementError("M13P4_FINGERPRINT_MISMATCH")
        return item


def create_wilsy_ai_entitlement(**kwargs: Any) -> WilsyAIEntitlement:
    """Construct an entitlement using only the canonical P3 policy fingerprint."""
    tier = WilsyAITier(kwargs["tier"])
    kwargs["policy_fingerprint"] = get_wilsy_ai_commercial_policy(tier).policy_fingerprint
    return WilsyAIEntitlement(**kwargs)


__all__ = ["WilsyAIEntitlement", "WilsyAIEntitlementError", "WilsyAIEntitlementState", "WilsyAITier", "ENTITLEMENT_FIELDS", "create_wilsy_ai_entitlement"]

# ARTIFACT: wilsy_ai_entitlement.py
# VERSION: v1.0.0-M13-P4
# AUTHORITY BOUNDARY: tenant entitlement lifecycle evidence only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
