"""WILSY OS canonical approved tenant branding profile domain.

TITLE: Tenant Branding Profile Domain
VERSION: v1.0.0-D21B3-TENANT-BRANDING-PROFILE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Own immutable approved tenant branding presentation evidence bound to
         an exact ACTIVE D21B2 entitlement and D21B1 capability policy without
         granting current-profile selection, browser, IAM or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/tenant_branding_profile.py
COLLABORATION / OWNERSHIP: D21B1 owns branding capability policy; D21B2 owns
                            tenant/package entitlement lifecycle truth; this
                            domain owns one approved presentation profile
                            snapshot. A later registry must own durable profile
                            persistence/current selection and re-check current
                            entitlement before any workspace projection. An
                            asset authority must resolve opaque asset references.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B3-TENANT-BRANDING-PROFILE establishes immutable approved
           profile evidence bound to an exact ACTIVE D21B2 entitlement snapshot,
           tier-gates logo/colour/email-display/favicon fields through D21B1,
           requires opaque asset references plus SHA3-512 evidence, preserves the
           mandatory WILSY OS trust mark, and excludes raw URLs/paths/base64,
           custom code, banking/legal-identity/commercial/financial fields.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No credentials, files, raw image bytes, URLs,
                             filesystem paths, CSS, JavaScript, HTML, network,
                             MongoDB, KMS, provider clients or browser state.
TENANT BOUNDARY: Profile tenant_id must exactly match its embedded ACTIVE D21B2
                 entitlement snapshot. Pseudo-tenants are already rejected by
                 D21B2 and cannot be reintroduced here.
AUTHORITY BOUNDARY: Approved presentation-profile evidence only. A profile does
                    not select itself as current, authorize workspace/browser
                    use, prove principal access, or establish legal/commercial
                    identity. Asset references require separate resolution.
FINANCIAL AUTHORITY BOUNDARY: No bank, tax, price, invoice, charge, payment,
                               execution or settlement truth. Kennel EOS remains
                               the exclusive financial execution authority.
FAIL-CLOSED DECLARATION: Non-ACTIVE entitlement snapshots, tenant mismatch,
                         D21B1 capability violations, raw asset locations,
                         malformed colours/evidence, trust-mark removal, schema
                         drift and fingerprint corruption reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
import unicodedata
from typing import Any, Final, cast

from tools.eos.saas.billing.tenant_branding_vas_policy import (
    PLATFORM_TRUST_MARK_CAPABILITY,
    TenantBrandingTier,
    get_tenant_branding_vas_policy,
)
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlement,
    TenantBrandingEntitlementState,
)


VERSION: Final[str] = "v1.0.0-D21B3-TENANT-BRANDING-PROFILE"
SCHEMA: Final[str] = "WILSY-TENANT-BRANDING-PROFILE/V1"
_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "profile_version",
    "tenant_id",
    "profile_id",
    "profile_label",
    "branding_entitlement",
    "platform_trust_mark_required",
    "logo_asset_reference",
    "logo_asset_fingerprint",
    "primary_color",
    "secondary_color",
    "accent_color",
    "email_display_name",
    "favicon_asset_reference",
    "favicon_asset_fingerprint",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "approved_at",
    "approval_evidence_reference",
    "approval_evidence_fingerprint",
    "fingerprint",
)
PROFILE_FIELDS: Final[tuple[str, ...]] = _FIELDS
_HEX_DIGITS: Final[frozenset[str]] = frozenset("0123456789abcdef")
_COLOR_PATTERN: Final[re.Pattern[str]] = re.compile(r"^#[0-9A-F]{6}$")
_ASSET_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^asset:[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"
)


class TenantBrandingProfileError(ValueError):
    """Raised when approved tenant branding profile evidence is invalid."""


def _text(name: str, value: object, *, limit: int = 512) -> str:
    """Return one exact NFC text value without trimming or inventing content."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantBrandingProfileError(f"D21B3_INVALID_{name.upper()}")
    normalized = unicodedata.normalize("NFC", value)
    if (
        not normalized
        or len(normalized) > limit
        or any(ord(character) < 32 for character in normalized)
    ):
        raise TenantBrandingProfileError(f"D21B3_INVALID_{name.upper()}")
    return normalized


def _optional_text(
    name: str,
    value: object,
    *,
    limit: int = 160,
) -> str | None:
    """Return one optional exact bounded text value."""
    if value is None:
        return None
    return _text(name, value, limit=limit)


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512-shaped evidence fingerprint."""
    if (
        not isinstance(value, str)
        or len(value) != 128
        or any(character not in _HEX_DIGITS for character in value)
    ):
        raise TenantBrandingProfileError(f"D21B3_INVALID_{name.upper()}")
    return value


def _when(name: str, value: object) -> datetime:
    """Normalize one required timezone-aware approval time into UTC."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            raise TenantBrandingProfileError(
                f"D21B3_INVALID_{name.upper()}"
            ) from error
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        raise TenantBrandingProfileError(f"D21B3_INVALID_{name.upper()}")
    return parsed.astimezone(timezone.utc)


def _asset_pair(
    name: str,
    reference: object,
    fingerprint: object,
) -> tuple[str | None, str | None]:
    """Validate an optional opaque asset reference/fingerprint pair atomically."""
    if reference is None and fingerprint is None:
        return None, None
    if not isinstance(reference, str) or not _ASSET_PATTERN.fullmatch(reference):
        raise TenantBrandingProfileError(f"D21B3_INVALID_{name.upper()}")
    return reference, _fingerprint(f"{name}_fingerprint", fingerprint)


def _color(name: str, value: object) -> str | None:
    """Require canonical uppercase six-digit hex colour text when present."""
    if value is None:
        return None
    if not isinstance(value, str) or not _COLOR_PATTERN.fullmatch(value):
        raise TenantBrandingProfileError(f"D21B3_INVALID_{name.upper()}")
    return value


def _entitlement(
    value: object,
) -> TenantBrandingEntitlement:
    """Hydrate one exact immutable D21B2 entitlement snapshot."""
    if isinstance(value, TenantBrandingEntitlement):
        return value
    if isinstance(value, Mapping):
        try:
            return TenantBrandingEntitlement.from_dict(
                cast(Mapping[str, object], value)
            )
        except (TypeError, ValueError) as error:
            raise TenantBrandingProfileError(
                "D21B3_ENTITLEMENT_INVALID"
            ) from error
    raise TenantBrandingProfileError("D21B3_ENTITLEMENT_INVALID")


def _json_value(value: object) -> object:
    """Project exact domain values into deterministic JSON-compatible form."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, TenantBrandingEntitlement):
        return value.to_dict()
    return value


@dataclass(frozen=True, slots=True)
class TenantBrandingProfile:
    """Immutable approved tenant branding presentation evidence.

    Approval proves the profile content passed this domain contract at one point
    in time against an ACTIVE D21B2 entitlement snapshot. Runtime presentation
    must still re-check the current entitlement and current-profile selection.
    """

    tenant_id: str
    profile_id: str
    profile_label: str
    branding_entitlement: TenantBrandingEntitlement | Mapping[str, object]
    source_evidence_reference: str
    source_evidence_fingerprint: str
    approved_at: datetime
    approval_evidence_reference: str
    approval_evidence_fingerprint: str
    logo_asset_reference: str | None = None
    logo_asset_fingerprint: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    accent_color: str | None = None
    email_display_name: str | None = None
    favicon_asset_reference: str | None = None
    favicon_asset_fingerprint: str | None = None
    platform_trust_mark_required: bool = True
    schema: str = SCHEMA
    profile_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate entitlement/capability bindings and derive integrity seal."""
        tenant_id = _text("tenant_id", self.tenant_id, limit=160)
        profile_id = _text("profile_id", self.profile_id, limit=160)
        profile_label = _text("profile_label", self.profile_label, limit=160)
        entitlement = _entitlement(self.branding_entitlement)

        if (
            entitlement.lifecycle_state
            is not TenantBrandingEntitlementState.ACTIVE
        ):
            raise TenantBrandingProfileError(
                "D21B3_ACTIVE_ENTITLEMENT_REQUIRED"
            )
        if entitlement.tenant_id != tenant_id:
            raise TenantBrandingProfileError("D21B3_TENANT_MISMATCH")
        if self.schema != SCHEMA or self.profile_version != VERSION:
            raise TenantBrandingProfileError("D21B3_IDENTITY_INVALID")
        if self.platform_trust_mark_required is not True:
            raise TenantBrandingProfileError("D21B3_TRUST_MARK_REQUIRED")

        policy = get_tenant_branding_vas_policy(
            cast(TenantBrandingTier, entitlement.branding_tier)
        )
        if (
            PLATFORM_TRUST_MARK_CAPABILITY not in policy.capabilities
            or not policy.platform_trust_mark_required
            or policy.custom_code_allowed
        ):
            raise TenantBrandingProfileError("D21B3_POLICY_INVALID")

        logo_reference, logo_fingerprint = _asset_pair(
            "logo_asset_reference",
            self.logo_asset_reference,
            self.logo_asset_fingerprint,
        )
        favicon_reference, favicon_fingerprint = _asset_pair(
            "favicon_asset_reference",
            self.favicon_asset_reference,
            self.favicon_asset_fingerprint,
        )
        primary_color = _color("primary_color", self.primary_color)
        secondary_color = _color("secondary_color", self.secondary_color)
        accent_color = _color("accent_color", self.accent_color)
        email_display_name = _optional_text(
            "email_display_name",
            self.email_display_name,
        )

        if logo_reference is not None and not policy.permits("tenant.brand.logo.v1"):
            raise TenantBrandingProfileError("D21B3_LOGO_NOT_ENTITLED")
        if (
            any(
                value is not None
                for value in (
                    primary_color,
                    secondary_color,
                    accent_color,
                )
            )
            and not policy.permits("tenant.brand.colors.v1")
        ):
            raise TenantBrandingProfileError("D21B3_COLORS_NOT_ENTITLED")
        if (
            email_display_name is not None
            and not policy.permits("tenant.brand.email_identity.v1")
        ):
            raise TenantBrandingProfileError(
                "D21B3_EMAIL_IDENTITY_NOT_ENTITLED"
            )
        if (
            favicon_reference is not None
            and not policy.permits("tenant.brand.favicon.v1")
        ):
            raise TenantBrandingProfileError("D21B3_FAVICON_NOT_ENTITLED")

        source_reference = _text(
            "source_evidence_reference",
            self.source_evidence_reference,
        )
        source_fingerprint = _fingerprint(
            "source_evidence_fingerprint",
            self.source_evidence_fingerprint,
        )
        approved_at = _when("approved_at", self.approved_at)
        approval_reference = _text(
            "approval_evidence_reference",
            self.approval_evidence_reference,
        )
        approval_fingerprint = _fingerprint(
            "approval_evidence_fingerprint",
            self.approval_evidence_fingerprint,
        )

        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "profile_id", profile_id)
        object.__setattr__(self, "profile_label", profile_label)
        object.__setattr__(self, "branding_entitlement", entitlement)
        object.__setattr__(self, "logo_asset_reference", logo_reference)
        object.__setattr__(self, "logo_asset_fingerprint", logo_fingerprint)
        object.__setattr__(self, "primary_color", primary_color)
        object.__setattr__(self, "secondary_color", secondary_color)
        object.__setattr__(self, "accent_color", accent_color)
        object.__setattr__(self, "email_display_name", email_display_name)
        object.__setattr__(self, "favicon_asset_reference", favicon_reference)
        object.__setattr__(self, "favicon_asset_fingerprint", favicon_fingerprint)
        object.__setattr__(self, "source_evidence_reference", source_reference)
        object.__setattr__(self, "source_evidence_fingerprint", source_fingerprint)
        object.__setattr__(self, "approved_at", approved_at)
        object.__setattr__(self, "approval_evidence_reference", approval_reference)
        object.__setattr__(self, "approval_evidence_fingerprint", approval_fingerprint)

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
            raise TenantBrandingProfileError("D21B3_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact approved profile evidence document."""
        return {
            field: _json_value(getattr(self, field))
            for field in _FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "TenantBrandingProfile":
        """Hydrate only the exact profile schema and verify stored integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            raise TenantBrandingProfileError("D21B3_SCHEMA_INVALID")
        values = dict(payload)
        stored_fingerprint = values.pop("fingerprint")
        item = cls(**cast(Any, values))
        if (
            not isinstance(stored_fingerprint, str)
            or not hmac.compare_digest(stored_fingerprint, item.fingerprint)
        ):
            raise TenantBrandingProfileError("D21B3_FINGERPRINT_MISMATCH")
        return item


def approve_tenant_branding_profile(
    *,
    entitlement: TenantBrandingEntitlement,
    profile_id: str,
    profile_label: str,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
    approved_at: datetime,
    approval_evidence_reference: str,
    approval_evidence_fingerprint: str,
    logo_asset_reference: str | None = None,
    logo_asset_fingerprint: str | None = None,
    primary_color: str | None = None,
    secondary_color: str | None = None,
    accent_color: str | None = None,
    email_display_name: str | None = None,
    favicon_asset_reference: str | None = None,
    favicon_asset_fingerprint: str | None = None,
) -> TenantBrandingProfile:
    """Approve one immutable profile against an exact ACTIVE entitlement.

    The returned value is evidence, not current-profile selection or browser
    authorization. Asset references remain opaque and require a separate asset
    authority before bytes may be resolved or rendered.
    """
    return TenantBrandingProfile(
        tenant_id=entitlement.tenant_id,
        profile_id=profile_id,
        profile_label=profile_label,
        branding_entitlement=entitlement,
        source_evidence_reference=source_evidence_reference,
        source_evidence_fingerprint=source_evidence_fingerprint,
        approved_at=approved_at,
        approval_evidence_reference=approval_evidence_reference,
        approval_evidence_fingerprint=approval_evidence_fingerprint,
        logo_asset_reference=logo_asset_reference,
        logo_asset_fingerprint=logo_asset_fingerprint,
        primary_color=primary_color,
        secondary_color=secondary_color,
        accent_color=accent_color,
        email_display_name=email_display_name,
        favicon_asset_reference=favicon_asset_reference,
        favicon_asset_fingerprint=favicon_asset_fingerprint,
    )


__all__ = [
    "PROFILE_FIELDS",
    "SCHEMA",
    "TenantBrandingProfile",
    "TenantBrandingProfileError",
    "VERSION",
    "approve_tenant_branding_profile",
]

# ARTIFACT: tenant_branding_profile.py
# VERSION: v1.0.0-D21B3-TENANT-BRANDING-PROFILE
# AUTHORITY BOUNDARY: approved branding-profile evidence only; no current-profile, asset-resolution, browser, IAM or financial authority
# TENANT POSTURE: exact tenant binding to embedded ACTIVE D21B2 entitlement evidence
# FAIL-CLOSED POSTURE: inactive entitlement, capability mismatch, raw asset location, malformed evidence and corruption reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
