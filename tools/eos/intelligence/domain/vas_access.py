"""WILSY OS — sovereign WILSY AI VAS access contract.

TITLE: WILSY AI Value-Added-Service Access Contract
VERSION: v1.0.0-WILSY-AI-VAS-ACCESS
AUTHORITY: Wilsy OS Core Governance
PURPOSE:
    Package an already-authorized tenant AI entitlement, business profile,
    dashboard context, domain scope, and usage budget into one immutable,
    deterministic access envelope before WILSY AI computation.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/domain/vas_access.py

AUTHORITY BOUNDARY:
    This artifact does not authenticate a principal, establish tenant
    membership, sell a subscription, activate a VAS, price usage, retrieve
    business evidence, run AI, mutate business state, or execute money.

    Identity, membership, permission, subscription, entitlement, business
    profile, dashboard context, and usage facts must already have been resolved
    by their respective sovereign Python authorities before construction.

FINANCIAL AUTHORITY:
    Kennel EOS remains the exclusive financial execution authority.

JAVASCRIPT MIGRATION POSTURE:
    Existing JS AI licensing, entitlement, metering, and dashboard surfaces are
    migration sources/projections only. They are not sovereign authority for
    this contract and are to be retired incrementally after certified Python
    replacement.

CONSTITUTION:
    NO EVIDENCE = NO FACT.
    NO ENTITLEMENT = NO AI COMPUTE.
    OBSERVED FACT != AI INFERENCE != RECOMMENDATION
                  != AUTHORIZATION != EXECUTION.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


VERSION = "v1.0.0-WILSY-AI-VAS-ACCESS"

ADVISORY_AI_CAPABILITIES = frozenset(
    {
        "EXPLAIN",
        "RECOMMEND",
        "SUMMARIZE",
    }
)


def _identifier(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{field_name} must be non-blank")

    if len(normalized) > 256:
        raise ValueError(
            f"{field_name} exceeds maximum length 256"
        )

    if any(character.isspace() for character in normalized):
        raise ValueError(
            f"{field_name} must not contain whitespace"
        )

    return normalized


def _label(
    value: Any,
    field_name: str,
    *,
    max_length: int = 256,
) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{field_name} must be non-blank")

    if len(normalized) > max_length:
        raise ValueError(
            f"{field_name} exceeds maximum length {max_length}"
        )

    return normalized


def _utc_timestamp(value: Any, field_name: str) -> str:
    raw = _label(
        value,
        field_name,
        max_length=128,
    )

    candidate = (
        raw[:-1] + "+00:00"
        if raw.endswith("Z")
        else raw
    )

    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as error:
        raise ValueError(
            f"{field_name} must be ISO-8601"
        ) from error

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(
            f"{field_name} must include timezone information"
        )

    return parsed.astimezone(timezone.utc).isoformat()


def _references(
    values: Any,
    field_name: str,
) -> tuple[str, ...]:
    if (
        isinstance(values, (str, bytes))
        or not isinstance(values, (tuple, list))
    ):
        raise ValueError(
            f"{field_name} must be a tuple or list"
        )

    normalized = tuple(
        _identifier(value, field_name)
        for value in values
    )

    if not normalized:
        raise ValueError(
            f"{field_name} must contain at least one reference"
        )

    if len(set(normalized)) != len(normalized):
        raise ValueError(
            f"{field_name} must not contain duplicates"
        )

    return normalized


def _domains(values: Any) -> tuple[str, ...]:
    normalized = tuple(
        value.upper()
        for value in _references(
            values,
            "allowed_domains",
        )
    )

    if tuple(sorted(normalized)) != normalized:
        raise ValueError(
            "allowed_domains must be supplied in canonical sorted order"
        )

    return normalized


def _capabilities(values: Any) -> tuple[str, ...]:
    normalized = tuple(
        value.upper()
        for value in _references(
            values,
            "allowed_capabilities",
        )
    )

    if tuple(sorted(normalized)) != normalized:
        raise ValueError(
            "allowed_capabilities must be supplied in canonical sorted order"
        )

    unsupported = tuple(
        capability
        for capability in normalized
        if capability not in ADVISORY_AI_CAPABILITIES
    )

    if unsupported:
        raise ValueError(
            "UNSUPPORTED_AI_CAPABILITY"
        )

    return normalized


def _non_negative_integer(
    value: Any,
    field_name: str,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            f"{field_name} must be an integer"
        )

    if value < 0:
        raise ValueError(
            f"{field_name} must be non-negative"
        )

    return value


def _checksum(payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")

    return (
        "sha3-512:"
        + hashlib.sha3_512(canonical).hexdigest()
    )


@dataclass(frozen=True, slots=True)
class WilsyAIVASAccess:
    """Immutable envelope of previously resolved WILSY AI access facts."""

    tenant_id: str
    principal_id: str
    scope_ref: str

    entitlement_ref: str
    subscription_ref: str
    entitlement_evidence_refs: tuple[str, ...]
    usage_evidence_refs: tuple[str, ...]

    business_profile_ref: str
    business_profile_evidence_refs: tuple[str, ...]
    business_type: str

    dashboard_id: str
    dashboard_domain: str

    allowed_domains: tuple[str, ...]
    allowed_capabilities: tuple[str, ...]

    usage_limit: int
    usage_consumed: int

    evaluated_at: str

    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "tenant_id",
            _identifier(self.tenant_id, "tenant_id"),
        )
        object.__setattr__(
            self,
            "principal_id",
            _identifier(self.principal_id, "principal_id"),
        )
        object.__setattr__(
            self,
            "scope_ref",
            _identifier(self.scope_ref, "scope_ref"),
        )

        object.__setattr__(
            self,
            "entitlement_ref",
            _identifier(
                self.entitlement_ref,
                "entitlement_ref",
            ),
        )
        object.__setattr__(
            self,
            "subscription_ref",
            _identifier(
                self.subscription_ref,
                "subscription_ref",
            ),
        )
        object.__setattr__(
            self,
            "entitlement_evidence_refs",
            _references(
                self.entitlement_evidence_refs,
                "entitlement_evidence_refs",
            ),
        )
        object.__setattr__(
            self,
            "usage_evidence_refs",
            _references(
                self.usage_evidence_refs,
                "usage_evidence_refs",
            ),
        )

        object.__setattr__(
            self,
            "business_profile_ref",
            _identifier(
                self.business_profile_ref,
                "business_profile_ref",
            ),
        )
        object.__setattr__(
            self,
            "business_profile_evidence_refs",
            _references(
                self.business_profile_evidence_refs,
                "business_profile_evidence_refs",
            ),
        )
        object.__setattr__(
            self,
            "business_type",
            _label(
                self.business_type,
                "business_type",
            ),
        )

        object.__setattr__(
            self,
            "dashboard_id",
            _identifier(
                self.dashboard_id,
                "dashboard_id",
            ),
        )
        object.__setattr__(
            self,
            "dashboard_domain",
            _identifier(
                self.dashboard_domain,
                "dashboard_domain",
            ).upper(),
        )

        object.__setattr__(
            self,
            "allowed_domains",
            _domains(self.allowed_domains),
        )
        object.__setattr__(
            self,
            "allowed_capabilities",
            _capabilities(
                self.allowed_capabilities
            ),
        )

        object.__setattr__(
            self,
            "usage_limit",
            _non_negative_integer(
                self.usage_limit,
                "usage_limit",
            ),
        )
        object.__setattr__(
            self,
            "usage_consumed",
            _non_negative_integer(
                self.usage_consumed,
                "usage_consumed",
            ),
        )

        if self.usage_limit == 0:
            raise ValueError(
                "usage_limit must be greater than zero"
            )

        if self.usage_consumed >= self.usage_limit:
            raise ValueError(
                "NO_ENTITLEMENT_CAPACITY"
            )

        if self.dashboard_domain not in self.allowed_domains:
            raise ValueError(
                "DASHBOARD_DOMAIN_NOT_ENTITLED"
            )

        object.__setattr__(
            self,
            "evaluated_at",
            _utc_timestamp(
                self.evaluated_at,
                "evaluated_at",
            ),
        )

        payload = {
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "scope_ref": self.scope_ref,
            "entitlement_ref": self.entitlement_ref,
            "subscription_ref": self.subscription_ref,
            "entitlement_evidence_refs":
                self.entitlement_evidence_refs,
            "usage_evidence_refs":
                self.usage_evidence_refs,
            "business_profile_ref":
                self.business_profile_ref,
            "business_profile_evidence_refs":
                self.business_profile_evidence_refs,
            "business_type": self.business_type,
            "dashboard_id": self.dashboard_id,
            "dashboard_domain":
                self.dashboard_domain,
            "allowed_domains": self.allowed_domains,
            "allowed_capabilities":
                self.allowed_capabilities,
            "usage_limit": self.usage_limit,
            "usage_consumed":
                self.usage_consumed,
            "evaluated_at": self.evaluated_at,
        }

        object.__setattr__(
            self,
            "checksum",
            _checksum(payload),
        )

    @property
    def usage_remaining(self) -> int:
        return self.usage_limit - self.usage_consumed

    def permits_domain(self, domain: str) -> bool:
        if not isinstance(domain, str):
            return False

        normalized = domain.strip().upper()

        if not normalized:
            return False

        return normalized in self.allowed_domains

    def permits_capability(self, capability: str) -> bool:
        if not isinstance(capability, str):
            return False

        normalized = capability.strip().upper()

        if not normalized:
            return False

        return normalized in self.allowed_capabilities

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "scope_ref": self.scope_ref,
            "entitlement_ref": self.entitlement_ref,
            "subscription_ref": self.subscription_ref,
            "entitlement_evidence_refs":
                list(self.entitlement_evidence_refs),
            "usage_evidence_refs":
                list(self.usage_evidence_refs),
            "business_profile_ref":
                self.business_profile_ref,
            "business_profile_evidence_refs":
                list(self.business_profile_evidence_refs),
            "business_type": self.business_type,
            "dashboard_id": self.dashboard_id,
            "dashboard_domain":
                self.dashboard_domain,
            "allowed_domains":
                list(self.allowed_domains),
            "allowed_capabilities":
                list(self.allowed_capabilities),
            "usage_limit": self.usage_limit,
            "usage_consumed":
                self.usage_consumed,
            "usage_remaining":
                self.usage_remaining,
            "evaluated_at": self.evaluated_at,
            "checksum": self.checksum,
        }


__all__ = [
    "ADVISORY_AI_CAPABILITIES",
    "VERSION",
    "WilsyAIVASAccess",
]
