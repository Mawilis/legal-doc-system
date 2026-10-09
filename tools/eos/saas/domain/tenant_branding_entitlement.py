"""WILSY OS canonical tenant branding entitlement domain.

TITLE: Tenant Branding Entitlement Domain
VERSION: v1.0.0-D21B2-TENANT-BRANDING-ENTITLEMENT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Own immutable tenant/branding-package entitlement lifecycle evidence
         bound to the canonical D21B1 policy without granting brand-asset,
         browser, IAM, subscription-payment or financial-execution authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/tenant_branding_entitlement.py
COLLABORATION / OWNERSHIP: D21B1 owns global branding package/capability policy;
                            this domain owns tenant/package entitlement lifecycle
                            facts. A later governed branding-profile authority
                            must approve exact tenant assets before any browser,
                            document, auth surface or custom domain may consume
                            tenant-specific branding. PlanRegistry and
                            SubscriptionRegistry retain commercial truth; IAM
                            retains principal authority.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B2-TENANT-BRANDING-ENTITLEMENT establishes immutable
           tenant-scoped branding entitlement evidence, exact D21B1 tier/policy
           fingerprint binding, mandatory source evidence, revisioned closed
           lifecycle transitions and deterministic SHA3-512 integrity. ACTIVE
           proves package entitlement only and never approves a logo, colour,
           email identity, favicon, login skin, document skin, domain or other
           tenant branding asset for presentation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No credentials, brand assets, URLs, files, CSS,
                             JavaScript, HTML, network, MongoDB, KMS, provider
                             clients or browser state are accessed or embedded.
TENANT BOUNDARY: Every entitlement is bound to one explicit tenant_id and one
                 exact D21B1 branding tier. Pseudo-tenants fail closed.
AUTHORITY BOUNDARY: Tenant branding-package entitlement lifecycle evidence only.
                    ACTIVE does not approve a brand profile, authorize browser
                    presentation, prove user access, or grant role/permission.
FINANCIAL AUTHORITY BOUNDARY: No price, invoice, charge, payment, execution or
                               settlement truth. Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Unknown tiers, pseudo-tenants, D21B1 policy drift,
                         malformed source/lifecycle evidence, stale revisions,
                         illegal transitions and fingerprint drift reject.
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

from tools.eos.saas.billing.tenant_branding_vas_policy import (
    TenantBrandingTier,
    get_tenant_branding_vas_policy,
)


VERSION: Final[str] = "v1.0.0-D21B2-TENANT-BRANDING-ENTITLEMENT"
SCHEMA: Final[str] = "WILSY-TENANT-BRANDING-ENTITLEMENT/V1"
_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "entitlement_version",
    "lifecycle_revision",
    "tenant_id",
    "entitlement_id",
    "branding_tier",
    "policy_fingerprint",
    "lifecycle_state",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "activated_at",
    "activation_evidence_reference",
    "activation_evidence_fingerprint",
    "suspended_at",
    "suspension_evidence_reference",
    "suspension_evidence_fingerprint",
    "revoked_at",
    "revocation_evidence_reference",
    "revocation_evidence_fingerprint",
    "fingerprint",
)
ENTITLEMENT_FIELDS: Final[tuple[str, ...]] = _FIELDS
_HEX_DIGITS: Final[frozenset[str]] = frozenset("0123456789abcdef")


class TenantBrandingEntitlementError(ValueError):
    """Raised when tenant branding entitlement evidence violates the contract."""


class TenantBrandingEntitlementState(str, Enum):
    """Closed tenant-branding entitlement lifecycle states."""

    PENDING_SOURCE = "PENDING_SOURCE"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"


def _text(name: str, value: object) -> str:
    """Normalize one bounded identity/reference string without inventing truth."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantBrandingEntitlementError(f"D21B2_INVALID_{name.upper()}")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or any(ord(character) < 32 for character in normalized):
        raise TenantBrandingEntitlementError(f"D21B2_INVALID_{name.upper()}")
    return normalized


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512-shaped evidence fingerprint."""
    if (
        not isinstance(value, str)
        or len(value) != 128
        or any(character not in _HEX_DIGITS for character in value)
    ):
        raise TenantBrandingEntitlementError(f"D21B2_INVALID_{name.upper()}")
    return value


def _when(name: str, value: object) -> datetime | None:
    """Normalize one optional timezone-aware lifecycle time into UTC."""
    if value is None:
        return None
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            raise TenantBrandingEntitlementError(
                f"D21B2_INVALID_{name.upper()}"
            ) from error
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        raise TenantBrandingEntitlementError(f"D21B2_INVALID_{name.upper()}")
    return parsed.astimezone(timezone.utc)


def _reference_pair(
    name: str,
    reference: object,
    fingerprint: object,
) -> tuple[str | None, str | None]:
    """Validate one optional evidence reference/fingerprint pair atomically."""
    if reference is None and fingerprint is None:
        return None, None
    return (
        _text(name, reference),
        _fingerprint(f"{name}_fingerprint", fingerprint),
    )


def _json_value(value: object) -> object:
    """Project exact domain values into deterministic JSON-compatible form."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, Enum):
        return value.value
    return value


@dataclass(frozen=True, slots=True)
class TenantBrandingEntitlement:
    """Immutable tenant branding-package entitlement lifecycle evidence.

    ACTIVE means only that the tenant has the exact D21B1 branding package
    entitlement. It does not approve any tenant-specific brand profile or asset,
    grant a principal access, admit a browser route, or create financial truth.
    """

    tenant_id: str
    entitlement_id: str
    branding_tier: TenantBrandingTier | str
    policy_fingerprint: str
    lifecycle_state: TenantBrandingEntitlementState | str
    source_evidence_reference: str
    source_evidence_fingerprint: str
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
        """Validate canonical policy binding/lifecycle shape and derive integrity."""
        tenant_id = _text("tenant_id", self.tenant_id)
        if tenant_id.casefold() in {"default", "global", "root", "*"}:
            raise TenantBrandingEntitlementError("D21B2_TENANT_REQUIRED")
        entitlement_id = _text("entitlement_id", self.entitlement_id)

        try:
            branding_tier = TenantBrandingTier(self.branding_tier)
            lifecycle_state = TenantBrandingEntitlementState(self.lifecycle_state)
        except (TypeError, ValueError) as error:
            raise TenantBrandingEntitlementError("D21B2_ENUM_INVALID") from error

        if self.schema != SCHEMA or self.entitlement_version != VERSION:
            raise TenantBrandingEntitlementError("D21B2_IDENTITY_INVALID")
        if (
            isinstance(self.lifecycle_revision, bool)
            or not isinstance(self.lifecycle_revision, int)
            or self.lifecycle_revision < 0
        ):
            raise TenantBrandingEntitlementError("D21B2_REVISION_INVALID")

        policy = get_tenant_branding_vas_policy(branding_tier)
        policy_fingerprint = _fingerprint(
            "policy_fingerprint",
            self.policy_fingerprint,
        )
        if not hmac.compare_digest(
            policy.policy_fingerprint,
            policy_fingerprint,
        ):
            raise TenantBrandingEntitlementError(
                "D21B2_POLICY_BINDING_INVALID"
            )

        source_reference = _text(
            "source_evidence_reference",
            self.source_evidence_reference,
        )
        source_fingerprint = _fingerprint(
            "source_evidence_fingerprint",
            self.source_evidence_fingerprint,
        )

        activated_at = _when("activated_at", self.activated_at)
        activation_reference, activation_fingerprint = _reference_pair(
            "activation_evidence_reference",
            self.activation_evidence_reference,
            self.activation_evidence_fingerprint,
        )
        suspended_at = _when("suspended_at", self.suspended_at)
        suspension_reference, suspension_fingerprint = _reference_pair(
            "suspension_evidence_reference",
            self.suspension_evidence_reference,
            self.suspension_evidence_fingerprint,
        )
        revoked_at = _when("revoked_at", self.revoked_at)
        revocation_reference, revocation_fingerprint = _reference_pair(
            "revocation_evidence_reference",
            self.revocation_evidence_reference,
            self.revocation_evidence_fingerprint,
        )

        if lifecycle_state is TenantBrandingEntitlementState.PENDING_SOURCE:
            if any(
                value is not None
                for value in (
                    activated_at,
                    activation_reference,
                    suspended_at,
                    suspension_reference,
                    revoked_at,
                    revocation_reference,
                )
            ):
                raise TenantBrandingEntitlementError(
                    "D21B2_PENDING_SHAPE_INVALID"
                )

        elif lifecycle_state is TenantBrandingEntitlementState.ACTIVE:
            if (
                activated_at is None
                or activation_reference is None
                or suspended_at is not None
                or suspension_reference is not None
                or revoked_at is not None
                or revocation_reference is not None
            ):
                raise TenantBrandingEntitlementError(
                    "D21B2_ACTIVE_SHAPE_INVALID"
                )

        elif lifecycle_state is TenantBrandingEntitlementState.SUSPENDED:
            if (
                activated_at is None
                or activation_reference is None
                or suspended_at is None
                or suspension_reference is None
                or revoked_at is not None
                or revocation_reference is not None
            ):
                raise TenantBrandingEntitlementError(
                    "D21B2_SUSPENDED_SHAPE_INVALID"
                )

        elif (
            activated_at is None
            or activation_reference is None
            or revoked_at is None
            or revocation_reference is None
            or suspended_at is not None
            or suspension_reference is not None
        ):
            raise TenantBrandingEntitlementError(
                "D21B2_REVOKED_SHAPE_INVALID"
            )

        if (
            activated_at is not None
            and suspended_at is not None
            and suspended_at < activated_at
        ):
            raise TenantBrandingEntitlementError(
                "D21B2_CHRONOLOGY_INVALID"
            )
        if (
            activated_at is not None
            and revoked_at is not None
            and revoked_at < activated_at
        ):
            raise TenantBrandingEntitlementError(
                "D21B2_CHRONOLOGY_INVALID"
            )

        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "entitlement_id", entitlement_id)
        object.__setattr__(self, "branding_tier", branding_tier)
        object.__setattr__(self, "policy_fingerprint", policy_fingerprint)
        object.__setattr__(self, "lifecycle_state", lifecycle_state)
        object.__setattr__(self, "source_evidence_reference", source_reference)
        object.__setattr__(self, "source_evidence_fingerprint", source_fingerprint)
        object.__setattr__(self, "activated_at", activated_at)
        object.__setattr__(self, "activation_evidence_reference", activation_reference)
        object.__setattr__(self, "activation_evidence_fingerprint", activation_fingerprint)
        object.__setattr__(self, "suspended_at", suspended_at)
        object.__setattr__(self, "suspension_evidence_reference", suspension_reference)
        object.__setattr__(self, "suspension_evidence_fingerprint", suspension_fingerprint)
        object.__setattr__(self, "revoked_at", revoked_at)
        object.__setattr__(self, "revocation_evidence_reference", revocation_reference)
        object.__setattr__(self, "revocation_evidence_fingerprint", revocation_fingerprint)

        payload = {
            field: _json_value(getattr(self, field))
            for field in _FIELDS[:-1]
        }
        digest = hashlib.sha3_512(
            json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=False,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            raise TenantBrandingEntitlementError(
                "D21B2_FINGERPRINT_MISMATCH"
            )
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact entitlement evidence document."""
        return {
            field: _json_value(getattr(self, field))
            for field in _FIELDS
        }

    def transition(
        self,
        target_state: TenantBrandingEntitlementState | str,
        *,
        expected_revision: int,
        evidence_reference: str,
        evidence_fingerprint: str,
        occurred_at: datetime,
    ) -> "TenantBrandingEntitlement":
        """Return one legal revisioned transition without mutating this value.

        Caller transaction ownership and persistence/CAS are outside this domain.
        SUSPENDED and REVOKED are terminal under this V1 lifecycle.
        """
        if (
            isinstance(expected_revision, bool)
            or not isinstance(expected_revision, int)
            or expected_revision != self.lifecycle_revision
        ):
            raise TenantBrandingEntitlementError("D21B2_STALE_REVISION")
        try:
            target = TenantBrandingEntitlementState(target_state)
        except (TypeError, ValueError) as error:
            raise TenantBrandingEntitlementError(
                "D21B2_TRANSITION_INVALID"
            ) from error

        legal = {
            TenantBrandingEntitlementState.PENDING_SOURCE: {
                TenantBrandingEntitlementState.ACTIVE,
            },
            TenantBrandingEntitlementState.ACTIVE: {
                TenantBrandingEntitlementState.SUSPENDED,
                TenantBrandingEntitlementState.REVOKED,
            },
            TenantBrandingEntitlementState.SUSPENDED: set(),
            TenantBrandingEntitlementState.REVOKED: set(),
        }
        current = cast(TenantBrandingEntitlementState, self.lifecycle_state)
        if target not in legal[current]:
            raise TenantBrandingEntitlementError(
                "D21B2_ILLEGAL_TRANSITION"
            )

        reference = _text("evidence_reference", evidence_reference)
        evidence_digest = _fingerprint(
            "evidence_fingerprint",
            evidence_fingerprint,
        )
        occurred = _when("occurred_at", occurred_at)
        assert occurred is not None

        changes: dict[str, object] = {
            "lifecycle_state": target,
            "lifecycle_revision": self.lifecycle_revision + 1,
            "fingerprint": "",
        }
        if target is TenantBrandingEntitlementState.ACTIVE:
            changes.update(
                activated_at=occurred,
                activation_evidence_reference=reference,
                activation_evidence_fingerprint=evidence_digest,
            )
        elif target is TenantBrandingEntitlementState.SUSPENDED:
            changes.update(
                suspended_at=occurred,
                suspension_evidence_reference=reference,
                suspension_evidence_fingerprint=evidence_digest,
            )
        else:
            changes.update(
                revoked_at=occurred,
                revocation_evidence_reference=reference,
                revocation_evidence_fingerprint=evidence_digest,
            )

        values = {
            field: getattr(self, field)
            for field in _FIELDS[:-1]
        }
        values.update(changes)
        return TenantBrandingEntitlement(**cast(Any, values))

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "TenantBrandingEntitlement":
        """Hydrate exact authority fields and verify stored integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            raise TenantBrandingEntitlementError("D21B2_SCHEMA_INVALID")
        values = dict(payload)
        stored_fingerprint = values.pop("fingerprint")
        item = cls(**cast(Any, values))
        if (
            not isinstance(stored_fingerprint, str)
            or not hmac.compare_digest(stored_fingerprint, item.fingerprint)
        ):
            raise TenantBrandingEntitlementError(
                "D21B2_FINGERPRINT_MISMATCH"
            )
        return item


def create_tenant_branding_entitlement(
    *,
    tenant_id: str,
    entitlement_id: str,
    branding_tier: TenantBrandingTier | str,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
) -> TenantBrandingEntitlement:
    """Create one pending entitlement bound to canonical D21B1 policy evidence.

    Creation never activates tenant branding and never approves any brand
    profile or asset. A separate evidence-backed transition is required before
    package entitlement may become ACTIVE.
    """
    policy = get_tenant_branding_vas_policy(branding_tier)
    return TenantBrandingEntitlement(
        tenant_id=tenant_id,
        entitlement_id=entitlement_id,
        branding_tier=policy.tier,
        policy_fingerprint=policy.policy_fingerprint,
        lifecycle_state=TenantBrandingEntitlementState.PENDING_SOURCE,
        source_evidence_reference=source_evidence_reference,
        source_evidence_fingerprint=source_evidence_fingerprint,
    )


__all__ = [
    "ENTITLEMENT_FIELDS",
    "SCHEMA",
    "TenantBrandingEntitlement",
    "TenantBrandingEntitlementError",
    "TenantBrandingEntitlementState",
    "VERSION",
    "create_tenant_branding_entitlement",
]

# ARTIFACT: tenant_branding_entitlement.py
# VERSION: v1.0.0-D21B2-TENANT-BRANDING-ENTITLEMENT
# AUTHORITY BOUNDARY: tenant branding-package entitlement lifecycle evidence only; no brand-profile, IAM or workspace authority
# TENANT POSTURE: exact tenant/D21B1-tier binding; pseudo-tenants reject
# FAIL-CLOSED POSTURE: policy drift, malformed evidence, stale revisions and illegal transitions reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
