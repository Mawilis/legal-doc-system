"""WILSY OS canonical Tenant Branding value-added-service policy.

TITLE: Tenant Branding VAS Policy
VERSION: v1.0.0-D21B1-TENANT-BRANDING-VAS-POLICY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Own the immutable four-tier tenant-branding capability ladder without
         granting entitlement, subscription, authorization, payment or
         financial-execution authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/tenant_branding_vas_policy.py
COLLABORATION / OWNERSHIP: Python EOS owns canonical branding package policy.
                            PlanRegistry/SubscriptionRegistry retain base
                            commercial catalogue/subscription truth; a later
                            dedicated branding entitlement authority must bind
                            a tenant to one package before presentation can use
                            tenant-specific branding. Legacy Node TenantBranding
                            remains a migration source only. WILSY OS platform
                            identity remains visible at every tier.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG: v1.0.0-D21B1-TENANT-BRANDING-VAS-POLICY establishes the previously
           approved Starter, Professional, Institutional and Enterprise
           branding packages as deterministic capability policy. Starter keeps
           WILSY OS branding only; Professional adds tenant logo, colours and
           email identity; Institutional additionally admits branded login/MFA,
           documents, invitations and favicon; Enterprise additionally admits
           custom domain, governed brand package and multiple brand profiles.
           Custom tenant CSS, JavaScript and HTML remain prohibited.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Pure immutable in-process policy. No credentials,
                             tenant documents, URLs, assets, files, network,
                             database, KMS or provider clients are accessed.
TENANT BOUNDARY: Policy descriptors are global catalogue facts only. Selecting
                 or constructing a policy never proves tenant membership,
                 subscription, entitlement, role or permission.
AUTHORITY BOUNDARY: Package/capability description only. This artifact cannot
                    activate branding, approve a tenant logo, select an asset,
                    grant custom-domain use, mutate a tenant, or authorize a
                    browser presentation.
FINANCIAL AUTHORITY BOUNDARY: No price, invoice, charge, payment, execution or
                               settlement truth is created. Kennel EOS remains
                               the exclusive financial execution authority.
FAIL-CLOSED DECLARATION: Unknown tiers, capability drift, reordered/duplicate
                         capability material, trust-mark removal, custom-code
                         enablement, malformed descriptors and fingerprint drift
                         reject deterministically.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import json
from typing import Any, Final, cast


VERSION: Final[str] = "v1.0.0-D21B1-TENANT-BRANDING-VAS-POLICY"
POLICY_SCHEMA: Final[str] = "WILSY-TENANT-BRANDING-VAS-POLICY/V1"
POLICY_IDENTITY: Final[str] = "WILSY_TENANT_BRANDING_VAS_POLICY"
PLATFORM_TRUST_MARK_CAPABILITY: Final[str] = "wilsy.brand.platform_trust_mark.v1"


class TenantBrandingVASPolicyError(ValueError):
    """Raised when a Tenant Branding VAS policy descriptor is invalid."""


class TenantBrandingTier(str, Enum):
    """Closed Tenant Branding VAS package ladder."""

    STARTER = "TENANT_BRANDING_STARTER"
    PROFESSIONAL = "TENANT_BRANDING_PROFESSIONAL"
    INSTITUTIONAL = "TENANT_BRANDING_INSTITUTIONAL"
    ENTERPRISE = "TENANT_BRANDING_ENTERPRISE"


_CANONICAL_INPUTS: Final[dict[TenantBrandingTier, dict[str, object]]] = {
    TenantBrandingTier.STARTER: {
        "label": "Tenant Branding Starter",
        "capabilities": (
            PLATFORM_TRUST_MARK_CAPABILITY,
        ),
        "value_promise": "WILSY OS platform identity only; no tenant-specific branding entitlement.",
    },
    TenantBrandingTier.PROFESSIONAL: {
        "label": "Tenant Branding Professional",
        "capabilities": (
            PLATFORM_TRUST_MARK_CAPABILITY,
            "tenant.brand.logo.v1",
            "tenant.brand.colors.v1",
            "tenant.brand.email_identity.v1",
        ),
        "value_promise": "Tenant logo, governed colours and email identity while WILSY OS trust remains visible.",
    },
    TenantBrandingTier.INSTITUTIONAL: {
        "label": "Tenant Branding Institutional",
        "capabilities": (
            PLATFORM_TRUST_MARK_CAPABILITY,
            "tenant.brand.logo.v1",
            "tenant.brand.colors.v1",
            "tenant.brand.email_identity.v1",
            "tenant.brand.auth_surfaces.v1",
            "tenant.brand.documents.v1",
            "tenant.brand.invitations.v1",
            "tenant.brand.favicon.v1",
        ),
        "value_promise": "Professional branding plus governed login/MFA, documents, invitations and favicon surfaces.",
    },
    TenantBrandingTier.ENTERPRISE: {
        "label": "Tenant Branding Enterprise",
        "capabilities": (
            PLATFORM_TRUST_MARK_CAPABILITY,
            "tenant.brand.logo.v1",
            "tenant.brand.colors.v1",
            "tenant.brand.email_identity.v1",
            "tenant.brand.auth_surfaces.v1",
            "tenant.brand.documents.v1",
            "tenant.brand.invitations.v1",
            "tenant.brand.favicon.v1",
            "tenant.brand.custom_domain.v1",
            "tenant.brand.governed_package.v1",
            "tenant.brand.multiple_profiles.v1",
        ),
        "value_promise": "Institutional branding plus governed custom domain and multiple approved brand profiles.",
    },
}

_SERIALIZED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "policy_identity",
        "policy_version",
        "tier",
        "label",
        "capabilities",
        "platform_trust_mark_required",
        "custom_code_allowed",
        "value_promise",
        "fingerprint",
    }
)


def _digest(payload: Mapping[str, object]) -> str:
    """Return lowercase SHA3-512 over deterministic UTF-8 JSON."""
    encoded = json.dumps(
        dict(payload),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _canonical_payload(
    *,
    tier: TenantBrandingTier,
    label: str,
    capabilities: tuple[str, ...],
    platform_trust_mark_required: bool,
    custom_code_allowed: bool,
    value_promise: str,
) -> dict[str, object]:
    """Return the semantic descriptor excluding its derived fingerprint."""
    return {
        "schema": POLICY_SCHEMA,
        "policy_identity": POLICY_IDENTITY,
        "policy_version": VERSION,
        "tier": tier.value,
        "label": label,
        "capabilities": list(capabilities),
        "platform_trust_mark_required": platform_trust_mark_required,
        "custom_code_allowed": custom_code_allowed,
        "value_promise": value_promise,
    }


def _text(value: object, code: str) -> str:
    """Return one non-empty exact text value or fail closed."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantBrandingVASPolicyError(code)
    return value


def _capabilities(value: object) -> tuple[str, ...]:
    """Validate exact ordered capability material without normalization."""
    if isinstance(value, str) or not isinstance(value, (tuple, list)):
        raise TenantBrandingVASPolicyError("D21B1_CAPABILITIES_INVALID")
    result = tuple(
        _text(item, "D21B1_CAPABILITY_INVALID")
        for item in value
    )
    if not result or len(set(result)) != len(result):
        raise TenantBrandingVASPolicyError("D21B1_CAPABILITIES_INVALID")
    return result


@dataclass(frozen=True, slots=True)
class TenantBrandingVASPolicy:
    """Immutable branding package policy and deterministic evidence seal."""

    tier: TenantBrandingTier | str
    label: str
    capabilities: tuple[str, ...]
    platform_trust_mark_required: bool
    custom_code_allowed: bool
    value_promise: str
    schema: str = POLICY_SCHEMA
    policy_identity: str = POLICY_IDENTITY
    policy_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate the exact canonical package and derive its SHA3-512 seal."""
        try:
            tier = TenantBrandingTier(self.tier)
        except (TypeError, ValueError) as error:
            raise TenantBrandingVASPolicyError("D21B1_UNKNOWN_TIER") from error

        if (
            self.schema != POLICY_SCHEMA
            or self.policy_identity != POLICY_IDENTITY
            or self.policy_version != VERSION
        ):
            raise TenantBrandingVASPolicyError("D21B1_POLICY_IDENTITY_INVALID")

        label = _text(self.label, "D21B1_LABEL_INVALID")
        value_promise = _text(
            self.value_promise,
            "D21B1_VALUE_PROMISE_INVALID",
        )
        capabilities = _capabilities(self.capabilities)
        canonical = _CANONICAL_INPUTS[tier]

        if label != canonical["label"]:
            raise TenantBrandingVASPolicyError("D21B1_CALLER_VALUE_OVERRIDE")
        if capabilities != canonical["capabilities"]:
            raise TenantBrandingVASPolicyError("D21B1_CALLER_VALUE_OVERRIDE")
        if value_promise != canonical["value_promise"]:
            raise TenantBrandingVASPolicyError("D21B1_CALLER_VALUE_OVERRIDE")
        if self.platform_trust_mark_required is not True:
            raise TenantBrandingVASPolicyError("D21B1_TRUST_MARK_REQUIRED")
        if self.custom_code_allowed is not False:
            raise TenantBrandingVASPolicyError("D21B1_CUSTOM_CODE_PROHIBITED")
        if capabilities[0] != PLATFORM_TRUST_MARK_CAPABILITY:
            raise TenantBrandingVASPolicyError("D21B1_TRUST_MARK_REQUIRED")

        payload = _canonical_payload(
            tier=tier,
            label=label,
            capabilities=capabilities,
            platform_trust_mark_required=True,
            custom_code_allowed=False,
            value_promise=value_promise,
        )
        digest = _digest(payload)
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            raise TenantBrandingVASPolicyError("D21B1_FINGERPRINT_MISMATCH")

        object.__setattr__(self, "tier", tier)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "capabilities", capabilities)
        object.__setattr__(self, "value_promise", value_promise)
        object.__setattr__(self, "fingerprint", digest)

    @property
    def policy_fingerprint(self) -> str:
        """Return the deterministic policy evidence fingerprint."""
        return self.fingerprint

    def permits(self, capability: str) -> bool:
        """Return whether this package describes one exact presentation capability.

        This is catalogue policy only. True does not prove tenant entitlement,
        activation, authorization or a valid branding profile.
        """
        value = _text(capability, "D21B1_CAPABILITY_INVALID")
        return value in self.capabilities

    def to_dict(self) -> dict[str, object]:
        """Return the exact detached descriptor suitable for evidence transport."""
        payload = _canonical_payload(
            tier=cast(TenantBrandingTier, self.tier),
            label=self.label,
            capabilities=self.capabilities,
            platform_trust_mark_required=self.platform_trust_mark_required,
            custom_code_allowed=self.custom_code_allowed,
            value_promise=self.value_promise,
        )
        payload["fingerprint"] = self.fingerprint
        return payload


def get_tenant_branding_vas_policy(
    tier: TenantBrandingTier | str,
) -> TenantBrandingVASPolicy:
    """Return the exact immutable package policy for one known branding tier.

    Unknown tiers fail closed. No tenant, subscription, entitlement or pricing
    inference occurs.
    """
    try:
        normalized = TenantBrandingTier(tier)
    except (TypeError, ValueError) as error:
        raise TenantBrandingVASPolicyError("D21B1_UNKNOWN_TIER") from error
    return _POLICIES[normalized]


def hydrate_tenant_branding_vas_policy(
    payload: Mapping[str, object],
) -> TenantBrandingVASPolicy:
    """Strictly hydrate one descriptor and recompute canonical integrity."""
    if not isinstance(payload, Mapping) or set(payload) != _SERIALIZED_FIELDS:
        raise TenantBrandingVASPolicyError("D21B1_DESCRIPTOR_SCHEMA_INVALID")
    raw: Mapping[str, Any] = payload
    capabilities = raw["capabilities"]
    if not isinstance(capabilities, list):
        raise TenantBrandingVASPolicyError("D21B1_DESCRIPTOR_SCHEMA_INVALID")
    return TenantBrandingVASPolicy(
        tier=raw["tier"],
        label=cast(str, raw["label"]),
        capabilities=tuple(cast(list[str], capabilities)),
        platform_trust_mark_required=cast(bool, raw["platform_trust_mark_required"]),
        custom_code_allowed=cast(bool, raw["custom_code_allowed"]),
        value_promise=cast(str, raw["value_promise"]),
        schema=cast(str, raw["schema"]),
        policy_identity=cast(str, raw["policy_identity"]),
        policy_version=cast(str, raw["policy_version"]),
        fingerprint=cast(str, raw["fingerprint"]),
    )


_POLICIES: Final[dict[TenantBrandingTier, TenantBrandingVASPolicy]] = {
    tier: TenantBrandingVASPolicy(
        tier=tier,
        label=cast(str, values["label"]),
        capabilities=cast(tuple[str, ...], values["capabilities"]),
        platform_trust_mark_required=True,
        custom_code_allowed=False,
        value_promise=cast(str, values["value_promise"]),
    )
    for tier, values in _CANONICAL_INPUTS.items()
}

__all__ = [
    "PLATFORM_TRUST_MARK_CAPABILITY",
    "POLICY_IDENTITY",
    "POLICY_SCHEMA",
    "TenantBrandingTier",
    "TenantBrandingVASPolicy",
    "TenantBrandingVASPolicyError",
    "VERSION",
    "get_tenant_branding_vas_policy",
    "hydrate_tenant_branding_vas_policy",
]

# ARTIFACT: tenant_branding_vas_policy.py
# VERSION: v1.0.0-D21B1-TENANT-BRANDING-VAS-POLICY
# AUTHORITY BOUNDARY: branding package description only; no tenant entitlement or presentation authority
# TENANT POSTURE: global policy only; no tenant identity is inferred or mutated
# FAIL-CLOSED POSTURE: unknown tiers, drift and custom-code enablement reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
