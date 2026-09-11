"""WILSY OS tenant inbound provider-policy immutable authority.

TITLE: Tenant Inbound Provider Policy
VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable, tenant-scoped policy fact binding one representable inbound
         provider to one exact merchant-configuration identity.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/tenant_inbound_provider_policy.py
COLLABORATION / OWNERSHIP: SaaS provider-policy domain owner; persistence,
                            authoring authorization, activation, and runtime
                            binding remain separate owners.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3C-P1 establishes strict immutable V1 inbound
           collection policy facts with deterministic SHA3-512 identity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references and fingerprints only; no raw
                             secret, credential bytes, KMS, or provider transport.
TENANT BOUNDARY: Every policy and referenced configuration is explicitly tenant scoped.
AUTHORITY BOUNDARY: Policy authoring fact only; no currentness, activation,
                    credential eligibility, provider binding, or checkout authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement.
TRANSACTION BOUNDARY: Pure frozen value object; callers own persistence and transactions.
FAIL-CLOSED DECLARATION: Unknown scope/provider, malformed identity, non-UTC time,
                          schema drift, or fingerprint mismatch rejects.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
import hashlib
import json
import re
from typing import Any, ClassVar, Mapping, cast

from .tenant_inbound_merchant_configuration import InboundMerchantProviderId


VERSION = "v1.0.0-M11-R8-R3B-P8-P3C-P1"
POLICY_FINGERPRINT_VERSION = "v1"
_SHA3_512 = re.compile(r"^[0-9a-f]{128}$")


class TenantInboundProviderPolicyError(ValueError):
    """Raised when an immutable inbound provider-policy fact is invalid."""


class TenantInboundProviderPolicyScope(StrEnum):
    """Closed V1 policy family; no outbound or multi-provider scope is representable."""

    INBOUND_COLLECTION = "INBOUND_COLLECTION"


# Concise repository-facing aliases preserve one canonical enum implementation.
PolicyScope = TenantInboundProviderPolicyScope
InboundProviderPolicyScope = TenantInboundProviderPolicyScope


def _required_text(name: str, value: object) -> str:
    """Require an opaque identifier without silently normalizing authority data."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantInboundProviderPolicyError(f"M11R8_INVALID_{name.upper()}")
    return value


def _positive_version(name: str, value: object) -> int:
    """Require a positive, non-boolean integer version."""
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise TenantInboundProviderPolicyError(f"M11R8_INVALID_{name.upper()}")
    return value


def _sha3_fingerprint(name: str, value: object) -> str:
    """Require an existing lowercase SHA3-512 hexadecimal fingerprint."""
    if not isinstance(value, str) or _SHA3_512.fullmatch(value) is None:
        raise TenantInboundProviderPolicyError(f"M11R8_INVALID_{name.upper()}")
    return value


def _utc_timestamp(name: str, value: object) -> datetime:
    """Require an aware UTC timestamp; offsets are not silently rewritten."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise TenantInboundProviderPolicyError(f"M11R8_INVALID_{name.upper()}")
    if value.utcoffset() != timedelta(0):
        raise TenantInboundProviderPolicyError(f"M11R8_NON_UTC_{name.upper()}")
    return value


def _canonical_json_bytes(value: Mapping[str, object]) -> bytes:
    """Serialize the semantic payload with deterministic canonical JSON."""
    return json.dumps(
        dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


@dataclass(frozen=True, slots=True)
class TenantInboundProviderPolicy:
    """Immutable V1 policy fact for exactly one inbound provider/configuration pair."""

    tenant_id: str
    provider_policy_id: str
    policy_version: int
    policy_scope: TenantInboundProviderPolicyScope
    provider_id: InboundMerchantProviderId
    merchant_configuration_id: str
    merchant_configuration_version: int
    merchant_configuration_fingerprint: str
    authoring_authorization_reference: str
    authoring_authorization_evidence_fingerprint: str
    created_at: datetime
    policy_fingerprint_version: str = POLICY_FINGERPRINT_VERSION
    policy_fingerprint: str | None = None

    _SEMANTIC_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {
            "tenant_id",
            "provider_policy_id",
            "policy_version",
            "policy_scope",
            "provider_id",
            "merchant_configuration_id",
            "merchant_configuration_version",
            "merchant_configuration_fingerprint",
            "authoring_authorization_reference",
            "authoring_authorization_evidence_fingerprint",
            "created_at",
            "policy_fingerprint_version",
        }
    )

    def __post_init__(self) -> None:
        tenant = _required_text("tenant_id", self.tenant_id)
        policy_id = _required_text("provider_policy_id", self.provider_policy_id)
        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "provider_policy_id", policy_id)
        object.__setattr__(self, "policy_version", _positive_version("policy_version", self.policy_version))
        if not isinstance(self.policy_scope, TenantInboundProviderPolicyScope):
            raise TenantInboundProviderPolicyError("M11R8_INVALID_POLICY_SCOPE")
        if self.policy_scope is not TenantInboundProviderPolicyScope.INBOUND_COLLECTION:
            raise TenantInboundProviderPolicyError("M11R8_INVALID_POLICY_SCOPE")
        if not isinstance(self.provider_id, InboundMerchantProviderId):
            raise TenantInboundProviderPolicyError("M11R8_UNKNOWN_PROVIDER")
        if self.provider_id is not InboundMerchantProviderId.PAYFAST:
            raise TenantInboundProviderPolicyError("M11R8_UNSUPPORTED_PROVIDER")
        object.__setattr__(self, "merchant_configuration_id", _required_text("merchant_configuration_id", self.merchant_configuration_id))
        object.__setattr__(self, "merchant_configuration_version", _positive_version("merchant_configuration_version", self.merchant_configuration_version))
        object.__setattr__(self, "merchant_configuration_fingerprint", _sha3_fingerprint("merchant_configuration_fingerprint", self.merchant_configuration_fingerprint))
        object.__setattr__(self, "authoring_authorization_reference", _required_text("authoring_authorization_reference", self.authoring_authorization_reference))
        object.__setattr__(self, "authoring_authorization_evidence_fingerprint", _sha3_fingerprint("authoring_authorization_evidence_fingerprint", self.authoring_authorization_evidence_fingerprint))
        object.__setattr__(self, "created_at", _utc_timestamp("created_at", self.created_at))
        if self.policy_fingerprint_version != POLICY_FINGERPRINT_VERSION:
            raise TenantInboundProviderPolicyError("M11R8_INVALID_POLICY_FINGERPRINT_VERSION")
        expected = self.compute_fingerprint()
        if self.policy_fingerprint is not None:
            if _SHA3_512.fullmatch(self.policy_fingerprint) is None or self.policy_fingerprint != expected:
                raise TenantInboundProviderPolicyError("M11R8_POLICY_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "policy_fingerprint", expected)

    def _semantic_payload(self) -> dict[str, object]:
        """Return every immutable authority-bearing field, excluding its digest."""
        return {
            "tenant_id": self.tenant_id,
            "provider_policy_id": self.provider_policy_id,
            "policy_version": self.policy_version,
            "policy_scope": self.policy_scope.value,
            "provider_id": self.provider_id.value,
            "merchant_configuration_id": self.merchant_configuration_id,
            "merchant_configuration_version": self.merchant_configuration_version,
            "merchant_configuration_fingerprint": self.merchant_configuration_fingerprint,
            "authoring_authorization_reference": self.authoring_authorization_reference,
            "authoring_authorization_evidence_fingerprint": self.authoring_authorization_evidence_fingerprint,
            "created_at": self.created_at.isoformat(),
            "policy_fingerprint_version": self.policy_fingerprint_version,
        }

    def compute_fingerprint(self) -> str:
        """Compute deterministic lowercase SHA3-512 policy identity."""
        return hashlib.sha3_512(_canonical_json_bytes(self._semantic_payload())).hexdigest()

    @property
    def fingerprint(self) -> str:
        """Expose the canonical immutable policy fingerprint."""
        assert self.policy_fingerprint is not None
        return self.policy_fingerprint

    def verify_fingerprint(self, fingerprint: str | None = None) -> bool:
        """Verify a supplied digest against canonical immutable policy data."""
        supplied = self.fingerprint if fingerprint is None else _sha3_fingerprint("policy_fingerprint", fingerprint)
        return supplied == self.compute_fingerprint()

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact strict immutable policy schema."""
        payload = self._semantic_payload()
        payload["policy_fingerprint"] = self.fingerprint
        return payload

    to_persisted = to_dict

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "TenantInboundProviderPolicy":
        """Hydrate strictly, rejecting schema drift and caller-supplied digest drift."""
        expected_fields = set(cls._SEMANTIC_FIELDS) | {"policy_fingerprint"}
        if not isinstance(payload, dict) or set(payload) != expected_fields:
            raise TenantInboundProviderPolicyError("M11R8_INVALID_POLICY_SCHEMA")
        data = cast(dict[str, Any], payload)
        try:
            scope = TenantInboundProviderPolicyScope(data["policy_scope"])
            provider = InboundMerchantProviderId(data["provider_id"])
            created_at = data["created_at"]
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            return cls(
                tenant_id=data["tenant_id"],
                provider_policy_id=data["provider_policy_id"],
                policy_version=data["policy_version"],
                policy_scope=scope,
                provider_id=provider,
                merchant_configuration_id=data["merchant_configuration_id"],
                merchant_configuration_version=data["merchant_configuration_version"],
                merchant_configuration_fingerprint=data["merchant_configuration_fingerprint"],
                authoring_authorization_reference=data["authoring_authorization_reference"],
                authoring_authorization_evidence_fingerprint=data["authoring_authorization_evidence_fingerprint"],
                created_at=created_at,
                policy_fingerprint_version=data["policy_fingerprint_version"],
                policy_fingerprint=data["policy_fingerprint"],
            )
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, TenantInboundProviderPolicyError):
                raise
            raise TenantInboundProviderPolicyError("M11R8_INVALID_POLICY") from error


# Explicit aliases avoid parallel authority classes while accommodating domain naming conventions.
InboundProviderPolicy = TenantInboundProviderPolicy
TenantInboundProviderPolicyAuthority = TenantInboundProviderPolicy


# ARTIFACT: tenant_inbound_provider_policy.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P1
# AUTHORITY BOUNDARY: immutable policy authoring fact only; no activation, binding, or checkout.
# TENANT POSTURE: exact tenant and merchant-configuration identity are mandatory.
# FAIL-CLOSED POSTURE: strict schema, provider, UTC timestamp, provenance, and digest validation.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
