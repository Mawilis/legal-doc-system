"""WILSY OS tenant inbound provider-policy activation lifecycle facts.

TITLE: Tenant Inbound Provider Policy Activation Domain Fact
VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P5
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable, tenant-scoped historical facts for activation-slot transitions;
         persistence, current-pointer authority, and orchestration remain external.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/tenant_inbound_provider_policy_activation.py
COLLABORATION / OWNERSHIP: P5 activation-domain owner; P4 policy authoring and
                            future P6 registry/orchestration are separate owners.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3C-P5 establishes immutable activation,
           supersession, deactivation, and emergency-disable event facts.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque authorization references and fingerprints only;
                             no credentials, KMS data, binding, or checkout claims.
TENANT BOUNDARY: tenant_id and policy_scope are mandatory event identity fields.
AUTHORITY BOUNDARY: historical activation fact only; no authorization, persistence,
                    current pointer, currentness, or configuration-state authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement.
TRANSACTION BOUNDARY: callers own sessions, transactions, commits, and aborts.
FAIL-CLOSED DECLARATION: malformed schema, shape, provenance, timestamp, or digest rejects.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
import hashlib
import json
import re
from typing import Any, ClassVar, Mapping, cast

from .tenant_inbound_merchant_configuration import InboundMerchantProviderId
from .tenant_inbound_provider_policy import TenantInboundProviderPolicyScope


VERSION = "v1.0.0-M11-R8-R3B-P8-P3C-P5"
CAMPAIGN_IDENTITY = "M11-R8-R3B-P8-P3C-P5"
ACTIVATION_EVENT_FINGERPRINT_VERSION = "v1"
ACTIVATION_EVENT_FINGERPRINT_SCHEMA = (
    "WILSY-TENANT-INBOUND-PROVIDER-POLICY-ACTIVATION-EVENT/V1"
)
_SHA3_512 = re.compile(r"^[0-9a-f]{128}$")


class TenantInboundProviderPolicyActivationError(ValueError):
    """Raised when an immutable activation fact violates its closed schema."""


class TenantInboundProviderPolicyActivationEventKind(StrEnum):
    """The four distinct V1 meanings of an active-policy slot event."""

    ACTIVATE = "ACTIVATE"
    SUPERSEDE = "SUPERSEDE"
    DEACTIVATE = "DEACTIVATE"
    EMERGENCY_DISABLE = "EMERGENCY_DISABLE"


def _text(name: str, value: object) -> str:
    """Require a non-blank opaque authority identifier without normalization."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantInboundProviderPolicyActivationError(f"M11P5_INVALID_{name.upper()}")
    return value


def _revision(value: object) -> int:
    """Require a non-boolean, non-negative activation-history position."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TenantInboundProviderPolicyActivationError("M11P5_INVALID_ACTIVATION_REVISION")
    return value


def _fingerprint(name: str, value: object) -> str:
    """Require a lowercase SHA3-512 hexadecimal evidence fingerprint."""
    if not isinstance(value, str) or _SHA3_512.fullmatch(value) is None:
        raise TenantInboundProviderPolicyActivationError(f"M11P5_INVALID_{name.upper()}")
    return value


def _utc(value: object) -> datetime:
    """Require an aware UTC timestamp; offsets are never silently rewritten."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise TenantInboundProviderPolicyActivationError("M11P5_INVALID_OCCURRED_AT")
    if value.utcoffset() != timedelta(0):
        raise TenantInboundProviderPolicyActivationError("M11P5_NON_UTC_OCCURRED_AT")
    return value


def _json_bytes(value: Mapping[str, object]) -> bytes:
    """Serialize semantic fields deterministically for cryptographic identity."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


@dataclass(frozen=True, slots=True)
class TenantInboundProviderPolicyReference:
    """Immutable exact policy/configuration identity snapshotted by an event."""

    provider_policy_id: str
    policy_version: int
    policy_fingerprint: str
    provider_id: InboundMerchantProviderId
    merchant_configuration_id: str
    merchant_configuration_version: int
    merchant_configuration_fingerprint: str

    _SEMANTIC_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {
            "provider_policy_id",
            "policy_version",
            "policy_fingerprint",
            "provider_id",
            "merchant_configuration_id",
            "merchant_configuration_version",
            "merchant_configuration_fingerprint",
        }
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "provider_policy_id", _text("provider_policy_id", self.provider_policy_id))
        if isinstance(self.policy_version, bool) or not isinstance(self.policy_version, int) or self.policy_version < 1:
            raise TenantInboundProviderPolicyActivationError("M11P5_INVALID_POLICY_VERSION")
        object.__setattr__(self, "policy_fingerprint", _fingerprint("policy_fingerprint", self.policy_fingerprint))
        if not isinstance(self.provider_id, InboundMerchantProviderId):
            raise TenantInboundProviderPolicyActivationError("M11P5_INVALID_PROVIDER_ID")
        object.__setattr__(self, "merchant_configuration_id", _text("merchant_configuration_id", self.merchant_configuration_id))
        if isinstance(self.merchant_configuration_version, bool) or not isinstance(self.merchant_configuration_version, int) or self.merchant_configuration_version < 1:
            raise TenantInboundProviderPolicyActivationError("M11P5_INVALID_MERCHANT_CONFIGURATION_VERSION")
        object.__setattr__(self, "merchant_configuration_fingerprint", _fingerprint("merchant_configuration_fingerprint", self.merchant_configuration_fingerprint))

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact seven-field immutable reference snapshot."""
        return {
            "provider_policy_id": self.provider_policy_id,
            "policy_version": self.policy_version,
            "policy_fingerprint": self.policy_fingerprint,
            "provider_id": self.provider_id.value,
            "merchant_configuration_id": self.merchant_configuration_id,
            "merchant_configuration_version": self.merchant_configuration_version,
            "merchant_configuration_fingerprint": self.merchant_configuration_fingerprint,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "TenantInboundProviderPolicyReference":
        """Hydrate strictly, rejecting unknown or missing reference fields."""
        if not isinstance(payload, dict) or set(payload) != set(cls._SEMANTIC_FIELDS):
            raise TenantInboundProviderPolicyActivationError("M11P5_INVALID_POLICY_REFERENCE_SCHEMA")
        data = cast(dict[str, Any], payload)
        try:
            return cls(
                provider_policy_id=data["provider_policy_id"],
                policy_version=data["policy_version"],
                policy_fingerprint=data["policy_fingerprint"],
                provider_id=InboundMerchantProviderId(data["provider_id"]),
                merchant_configuration_id=data["merchant_configuration_id"],
                merchant_configuration_version=data["merchant_configuration_version"],
                merchant_configuration_fingerprint=data["merchant_configuration_fingerprint"],
            )
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, TenantInboundProviderPolicyActivationError):
                raise
            raise TenantInboundProviderPolicyActivationError("M11P5_INVALID_POLICY_REFERENCE") from error


@dataclass(frozen=True, slots=True)
class TenantInboundProviderPolicyActivationEvent:
    """Immutable historical transition fact for one tenant/scope active slot."""

    tenant_id: str
    policy_scope: TenantInboundProviderPolicyScope
    activation_event_id: str
    activation_revision: int
    event_kind: TenantInboundProviderPolicyActivationEventKind
    lifecycle_idempotency_key: str
    prior_active_policy: TenantInboundProviderPolicyReference | None
    target_active_policy: TenantInboundProviderPolicyReference | None
    authorization_reference: str
    authorization_evidence_fingerprint: str
    reason_reference: str
    occurred_at: datetime
    activation_event_fingerprint_version: str = ACTIVATION_EVENT_FINGERPRINT_VERSION
    activation_event_fingerprint: str | None = None

    _SEMANTIC_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {
            "tenant_id",
            "policy_scope",
            "activation_event_id",
            "activation_revision",
            "event_kind",
            "lifecycle_idempotency_key",
            "prior_active_policy",
            "target_active_policy",
            "authorization_reference",
            "authorization_evidence_fingerprint",
            "reason_reference",
            "occurred_at",
            "activation_event_fingerprint_version",
        }
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "tenant_id", _text("tenant_id", self.tenant_id))
        if not isinstance(self.policy_scope, TenantInboundProviderPolicyScope) or self.policy_scope is not TenantInboundProviderPolicyScope.INBOUND_COLLECTION:
            raise TenantInboundProviderPolicyActivationError("M11P5_INVALID_POLICY_SCOPE")
        object.__setattr__(self, "activation_event_id", _text("activation_event_id", self.activation_event_id))
        object.__setattr__(self, "activation_revision", _revision(self.activation_revision))
        if not isinstance(self.event_kind, TenantInboundProviderPolicyActivationEventKind):
            raise TenantInboundProviderPolicyActivationError("M11P5_INVALID_EVENT_KIND")
        object.__setattr__(self, "lifecycle_idempotency_key", _text("lifecycle_idempotency_key", self.lifecycle_idempotency_key))
        if self.prior_active_policy is not None and not isinstance(self.prior_active_policy, TenantInboundProviderPolicyReference):
            raise TenantInboundProviderPolicyActivationError("M11P5_INVALID_PRIOR_ACTIVE_POLICY")
        if self.target_active_policy is not None and not isinstance(self.target_active_policy, TenantInboundProviderPolicyReference):
            raise TenantInboundProviderPolicyActivationError("M11P5_INVALID_TARGET_ACTIVE_POLICY")
        self._validate_shape()
        object.__setattr__(self, "authorization_reference", _text("authorization_reference", self.authorization_reference))
        object.__setattr__(self, "authorization_evidence_fingerprint", _fingerprint("authorization_evidence_fingerprint", self.authorization_evidence_fingerprint))
        object.__setattr__(self, "reason_reference", _text("reason_reference", self.reason_reference))
        object.__setattr__(self, "occurred_at", _utc(self.occurred_at))
        if self.activation_event_fingerprint_version != ACTIVATION_EVENT_FINGERPRINT_VERSION:
            raise TenantInboundProviderPolicyActivationError("M11P5_INVALID_EVENT_FINGERPRINT_VERSION")
        expected = self.compute_fingerprint()
        if self.activation_event_fingerprint is not None:
            if _SHA3_512.fullmatch(self.activation_event_fingerprint) is None or self.activation_event_fingerprint != expected:
                raise TenantInboundProviderPolicyActivationError("M11P5_EVENT_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "activation_event_fingerprint", expected)

    def _validate_shape(self) -> None:
        """Enforce the four closed transition shapes without touching persistence."""
        kind = self.event_kind
        if kind is TenantInboundProviderPolicyActivationEventKind.ACTIVATE:
            valid = self.prior_active_policy is None and self.target_active_policy is not None
        elif kind is TenantInboundProviderPolicyActivationEventKind.SUPERSEDE:
            valid = (
                self.prior_active_policy is not None
                and self.target_active_policy is not None
                and self.prior_active_policy != self.target_active_policy
            )
        else:
            valid = self.prior_active_policy is not None and self.target_active_policy is None
        if not valid:
            raise TenantInboundProviderPolicyActivationError("M11P5_INVALID_EVENT_TRANSITION_SHAPE")

    def _semantic_payload(self) -> dict[str, object]:
        """Return all immutable authority-bearing fields, excluding the digest."""
        return {
            "schema": ACTIVATION_EVENT_FINGERPRINT_SCHEMA,
            "tenant_id": self.tenant_id,
            "policy_scope": self.policy_scope.value,
            "activation_event_id": self.activation_event_id,
            "activation_revision": self.activation_revision,
            "event_kind": self.event_kind.value,
            "lifecycle_idempotency_key": self.lifecycle_idempotency_key,
            "prior_active_policy": None if self.prior_active_policy is None else self.prior_active_policy.to_dict(),
            "target_active_policy": None if self.target_active_policy is None else self.target_active_policy.to_dict(),
            "authorization_reference": self.authorization_reference,
            "authorization_evidence_fingerprint": self.authorization_evidence_fingerprint,
            "reason_reference": self.reason_reference,
            "occurred_at": self.occurred_at.isoformat(),
            "activation_event_fingerprint_version": self.activation_event_fingerprint_version,
        }

    def compute_fingerprint(self) -> str:
        """Compute deterministic SHA3-512 identity over canonical event JSON."""
        return hashlib.sha3_512(_json_bytes(self._semantic_payload())).hexdigest()

    @property
    def fingerprint(self) -> str:
        """Expose the canonical immutable event fingerprint."""
        assert self.activation_event_fingerprint is not None
        return self.activation_event_fingerprint

    def verify_fingerprint(self, fingerprint: str | None = None) -> bool:
        """Verify a supplied digest against the immutable event payload."""
        supplied = self.fingerprint if fingerprint is None else _fingerprint("activation_event_fingerprint", fingerprint)
        return supplied == self.compute_fingerprint()

    def to_dict(self) -> dict[str, object]:
        """Serialize exact event schema with nested immutable references."""
        payload = self._semantic_payload()
        # The schema label is the fingerprint domain separator, not a persisted
        # authority field; the versioned field below is the strict wire schema.
        payload.pop("schema", None)
        payload["activation_event_fingerprint"] = self.fingerprint
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "TenantInboundProviderPolicyActivationEvent":
        """Hydrate strictly and reject schema, shape, timestamp, or digest drift."""
        expected = set(cls._SEMANTIC_FIELDS) | {"activation_event_fingerprint"}
        if not isinstance(payload, dict) or set(payload) != expected:
            raise TenantInboundProviderPolicyActivationError("M11P5_INVALID_EVENT_SCHEMA")
        data = cast(dict[str, Any], payload)
        try:
            occurred_at = data["occurred_at"]
            if isinstance(occurred_at, str):
                occurred_at = datetime.fromisoformat(occurred_at)
            prior = data["prior_active_policy"]
            target = data["target_active_policy"]
            return cls(
                tenant_id=data["tenant_id"],
                policy_scope=TenantInboundProviderPolicyScope(data["policy_scope"]),
                activation_event_id=data["activation_event_id"],
                activation_revision=data["activation_revision"],
                event_kind=TenantInboundProviderPolicyActivationEventKind(data["event_kind"]),
                lifecycle_idempotency_key=data["lifecycle_idempotency_key"],
                prior_active_policy=None if prior is None else TenantInboundProviderPolicyReference.from_dict(prior),
                target_active_policy=None if target is None else TenantInboundProviderPolicyReference.from_dict(target),
                authorization_reference=data["authorization_reference"],
                authorization_evidence_fingerprint=data["authorization_evidence_fingerprint"],
                reason_reference=data["reason_reference"],
                occurred_at=occurred_at,
                activation_event_fingerprint_version=data["activation_event_fingerprint_version"],
                activation_event_fingerprint=data["activation_event_fingerprint"],
            )
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, TenantInboundProviderPolicyActivationError):
                raise
            raise TenantInboundProviderPolicyActivationError("M11P5_INVALID_EVENT") from error


# Repository-facing aliases preserve one canonical implementation.
ActivationEventKind = TenantInboundProviderPolicyActivationEventKind
PolicyActivationEventKind = TenantInboundProviderPolicyActivationEventKind
PolicyReference = TenantInboundProviderPolicyReference
ActivationEvent = TenantInboundProviderPolicyActivationEvent
TenantInboundProviderPolicyActivation = TenantInboundProviderPolicyActivationEvent
TenantInboundProviderPolicyActivationReference = TenantInboundProviderPolicyReference

__all__ = [
    "ACTIVATION_EVENT_FINGERPRINT_SCHEMA",
    "ACTIVATION_EVENT_FINGERPRINT_VERSION",
    "CAMPAIGN_IDENTITY",
    "VERSION",
    "ActivationEvent",
    "ActivationEventKind",
    "PolicyActivationEventKind",
    "PolicyReference",
    "TenantInboundProviderPolicyActivationError",
    "TenantInboundProviderPolicyActivation",
    "TenantInboundProviderPolicyActivationEvent",
    "TenantInboundProviderPolicyActivationEventKind",
    "TenantInboundProviderPolicyActivationReference",
    "TenantInboundProviderPolicyReference",
]


# ARTIFACT: tenant_inbound_provider_policy_activation.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P5
# AUTHORITY BOUNDARY: immutable activation-history facts only; no auth, persistence, pointer, binding, or checkout.
# TENANT POSTURE: every event is explicitly scoped by tenant_id and INBOUND_COLLECTION policy_scope.
# FAIL-CLOSED POSTURE: strict references, transition shapes, UTC timestamps, provenance, and digest validation.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
