"""WILSY OS canonical tenant branding current-profile selection fact.

TITLE: Tenant Branding Profile Selection Domain
VERSION: v1.0.0-D21B4A-TENANT-BRANDING-PROFILE-SELECTION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Own immutable tenant branding profile-selection evidence that proves
         one approved D21B3 profile matched the exact current ACTIVE D21B2
         entitlement snapshot at selection time without granting persistence,
         browser, asset-resolution, IAM or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/tenant_branding_profile_selection.py
COLLABORATION / OWNERSHIP: D21B1 owns package capabilities; D21B2 owns tenant
                            branding entitlement lifecycle; D21B3 owns approved
                            profile evidence; this domain owns immutable profile
                            selection facts. D21B4B will own durable selection
                            history/current-pointer CAS. Runtime projection must
                            re-check the current D21B2 entitlement again.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B4A-TENANT-BRANDING-PROFILE-SELECTION establishes
           immutable revisioned selection evidence, exact D21B3 profile and
           ACTIVE D21B2 snapshot correlation, deterministic prior-selection
           lineage, timezone-aware selection evidence and SHA3-512 integrity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Stores opaque identifiers, evidence references and
                             fingerprints only. No asset bytes, URL/path/base64,
                             credentials, network, MongoDB, KMS or browser state.
TENANT BOUNDARY: Profile and entitlement tenant identities must equal the
                 selection tenant exactly; cross-tenant composition rejects.
AUTHORITY BOUNDARY: Historical profile-selection evidence only. It does not
                    prove the selection remains current, that the entitlement
                    remains ACTIVE, or that any browser may render branding.
FINANCIAL AUTHORITY BOUNDARY: No price, bank, tax, invoice, charge, payment,
                               execution or settlement truth. Kennel EOS remains
                               the exclusive financial execution authority.
FAIL-CLOSED DECLARATION: Inactive/mismatched entitlement, profile/entitlement
                         provenance drift, malformed revision/lineage/evidence,
                         schema drift and fingerprint corruption reject.
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

from tools.eos.saas.billing.tenant_branding_vas_policy import TenantBrandingTier
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlement,
    TenantBrandingEntitlementState,
)
from tools.eos.saas.domain.tenant_branding_profile import TenantBrandingProfile


VERSION: Final[str] = "v1.0.0-D21B4A-TENANT-BRANDING-PROFILE-SELECTION"
SCHEMA: Final[str] = "WILSY-TENANT-BRANDING-PROFILE-SELECTION/V1"
_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "selection_version",
    "tenant_id",
    "selection_id",
    "selection_revision",
    "profile_id",
    "profile_fingerprint",
    "branding_entitlement_id",
    "branding_entitlement_revision",
    "branding_entitlement_fingerprint",
    "branding_tier",
    "prior_selection_id",
    "prior_selection_fingerprint",
    "selected_at",
    "selection_evidence_reference",
    "selection_evidence_fingerprint",
    "fingerprint",
)
SELECTION_FIELDS: Final[tuple[str, ...]] = _FIELDS
_HEX_DIGITS: Final[frozenset[str]] = frozenset("0123456789abcdef")


class TenantBrandingProfileSelectionError(ValueError):
    """Raised when tenant branding profile-selection evidence is invalid."""


def _text(name: str, value: object, *, limit: int = 256) -> str:
    """Return one exact bounded NFC text value without inventing content."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantBrandingProfileSelectionError(
            f"D21B4A_INVALID_{name.upper()}"
        )
    normalized = unicodedata.normalize("NFC", value)
    if (
        not normalized
        or len(normalized) > limit
        or any(ord(character) < 32 for character in normalized)
    ):
        raise TenantBrandingProfileSelectionError(
            f"D21B4A_INVALID_{name.upper()}"
        )
    return normalized


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512-shaped evidence fingerprint."""
    if (
        not isinstance(value, str)
        or len(value) != 128
        or any(character not in _HEX_DIGITS for character in value)
    ):
        raise TenantBrandingProfileSelectionError(
            f"D21B4A_INVALID_{name.upper()}"
        )
    return value


def _when(name: str, value: object) -> datetime:
    """Normalize one required timezone-aware event time into UTC."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            raise TenantBrandingProfileSelectionError(
                f"D21B4A_INVALID_{name.upper()}"
            ) from error
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        raise TenantBrandingProfileSelectionError(
            f"D21B4A_INVALID_{name.upper()}"
        )
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    """Project exact domain values into deterministic JSON-compatible form."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, TenantBrandingTier):
        return value.value
    return value


@dataclass(frozen=True, slots=True)
class TenantBrandingProfileSelection:
    """Immutable historical selection fact for one tenant branding profile.

    This value proves only that one approved profile matched one exact ACTIVE
    D21B2 entitlement snapshot when the selection fact was created. Durable
    currentness and runtime entitlement freshness belong to later authorities.
    """

    tenant_id: str
    selection_id: str
    selection_revision: int
    profile_id: str
    profile_fingerprint: str
    branding_entitlement_id: str
    branding_entitlement_revision: int
    branding_entitlement_fingerprint: str
    branding_tier: TenantBrandingTier | str
    prior_selection_id: str | None
    prior_selection_fingerprint: str | None
    selected_at: datetime
    selection_evidence_reference: str
    selection_evidence_fingerprint: str
    schema: str = SCHEMA
    selection_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate lineage/provenance shape and derive deterministic integrity."""
        tenant_id = _text("tenant_id", self.tenant_id, limit=160)
        selection_id = _text("selection_id", self.selection_id, limit=160)
        profile_id = _text("profile_id", self.profile_id, limit=160)
        profile_fingerprint = _fingerprint(
            "profile_fingerprint",
            self.profile_fingerprint,
        )
        entitlement_id = _text(
            "branding_entitlement_id",
            self.branding_entitlement_id,
            limit=160,
        )
        entitlement_fingerprint = _fingerprint(
            "branding_entitlement_fingerprint",
            self.branding_entitlement_fingerprint,
        )
        try:
            branding_tier = TenantBrandingTier(self.branding_tier)
        except (TypeError, ValueError) as error:
            raise TenantBrandingProfileSelectionError(
                "D21B4A_BRANDING_TIER_INVALID"
            ) from error

        if self.schema != SCHEMA or self.selection_version != VERSION:
            raise TenantBrandingProfileSelectionError(
                "D21B4A_IDENTITY_INVALID"
            )
        if (
            isinstance(self.selection_revision, bool)
            or not isinstance(self.selection_revision, int)
            or self.selection_revision < 1
        ):
            raise TenantBrandingProfileSelectionError(
                "D21B4A_SELECTION_REVISION_INVALID"
            )
        if (
            isinstance(self.branding_entitlement_revision, bool)
            or not isinstance(self.branding_entitlement_revision, int)
            or self.branding_entitlement_revision < 1
        ):
            raise TenantBrandingProfileSelectionError(
                "D21B4A_ENTITLEMENT_REVISION_INVALID"
            )

        prior_id: str | None
        prior_fingerprint: str | None
        if self.selection_revision == 1:
            if (
                self.prior_selection_id is not None
                or self.prior_selection_fingerprint is not None
            ):
                raise TenantBrandingProfileSelectionError(
                    "D21B4A_INITIAL_LINEAGE_INVALID"
                )
            prior_id = None
            prior_fingerprint = None
        else:
            prior_id = _text(
                "prior_selection_id",
                self.prior_selection_id,
                limit=160,
            )
            prior_fingerprint = _fingerprint(
                "prior_selection_fingerprint",
                self.prior_selection_fingerprint,
            )

        selected_at = _when("selected_at", self.selected_at)
        evidence_reference = _text(
            "selection_evidence_reference",
            self.selection_evidence_reference,
        )
        evidence_fingerprint = _fingerprint(
            "selection_evidence_fingerprint",
            self.selection_evidence_fingerprint,
        )

        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "selection_id", selection_id)
        object.__setattr__(self, "profile_id", profile_id)
        object.__setattr__(self, "profile_fingerprint", profile_fingerprint)
        object.__setattr__(self, "branding_entitlement_id", entitlement_id)
        object.__setattr__(
            self,
            "branding_entitlement_fingerprint",
            entitlement_fingerprint,
        )
        object.__setattr__(self, "branding_tier", branding_tier)
        object.__setattr__(self, "prior_selection_id", prior_id)
        object.__setattr__(
            self,
            "prior_selection_fingerprint",
            prior_fingerprint,
        )
        object.__setattr__(self, "selected_at", selected_at)
        object.__setattr__(
            self,
            "selection_evidence_reference",
            evidence_reference,
        )
        object.__setattr__(
            self,
            "selection_evidence_fingerprint",
            evidence_fingerprint,
        )

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
            raise TenantBrandingProfileSelectionError(
                "D21B4A_FINGERPRINT_MISMATCH"
            )
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact immutable selection evidence document."""
        return {
            field: _json_value(getattr(self, field))
            for field in _FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "TenantBrandingProfileSelection":
        """Hydrate only the exact selection schema and verify stored integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            raise TenantBrandingProfileSelectionError(
                "D21B4A_SCHEMA_INVALID"
            )
        values = dict(payload)
        stored_fingerprint = values.pop("fingerprint")
        item = cls(**cast(Any, values))
        if (
            not isinstance(stored_fingerprint, str)
            or not hmac.compare_digest(stored_fingerprint, item.fingerprint)
        ):
            raise TenantBrandingProfileSelectionError(
                "D21B4A_FINGERPRINT_MISMATCH"
            )
        return item


def select_tenant_branding_profile(
    *,
    profile: TenantBrandingProfile,
    current_entitlement: TenantBrandingEntitlement,
    selection_id: str,
    selection_revision: int,
    selected_at: datetime,
    selection_evidence_reference: str,
    selection_evidence_fingerprint: str,
    prior_selection: TenantBrandingProfileSelection | None = None,
) -> TenantBrandingProfileSelection:
    """Create one historical selection fact from exact current authorities.

    The caller must provide the currently read D21B2 entitlement snapshot. It
    must still be ACTIVE and must exactly equal the entitlement snapshot embedded
    in the approved D21B3 profile. This proves selection-time freshness only;
    runtime presentation must re-check D21B2 again.
    """
    if type(profile) is not TenantBrandingProfile:
        raise TenantBrandingProfileSelectionError(
            "D21B4A_PROFILE_REQUIRED"
        )
    if type(current_entitlement) is not TenantBrandingEntitlement:
        raise TenantBrandingProfileSelectionError(
            "D21B4A_ENTITLEMENT_REQUIRED"
        )
    if (
        current_entitlement.lifecycle_state
        is not TenantBrandingEntitlementState.ACTIVE
    ):
        raise TenantBrandingProfileSelectionError(
            "D21B4A_ACTIVE_ENTITLEMENT_REQUIRED"
        )
    embedded = cast(
        TenantBrandingEntitlement,
        profile.branding_entitlement,
    )
    if (
        profile.tenant_id != current_entitlement.tenant_id
        or embedded.to_dict() != current_entitlement.to_dict()
    ):
        raise TenantBrandingProfileSelectionError(
            "D21B4A_PROFILE_ENTITLEMENT_MISMATCH"
        )

    if prior_selection is None:
        if selection_revision != 1:
            raise TenantBrandingProfileSelectionError(
                "D21B4A_PRIOR_SELECTION_REQUIRED"
            )
        prior_id = None
        prior_fingerprint = None
    else:
        if type(prior_selection) is not TenantBrandingProfileSelection:
            raise TenantBrandingProfileSelectionError(
                "D21B4A_PRIOR_SELECTION_INVALID"
            )
        if (
            prior_selection.tenant_id != profile.tenant_id
            or selection_revision != prior_selection.selection_revision + 1
        ):
            raise TenantBrandingProfileSelectionError(
                "D21B4A_PRIOR_SELECTION_MISMATCH"
            )
        prior_id = prior_selection.selection_id
        prior_fingerprint = prior_selection.fingerprint

    tier = cast(TenantBrandingTier, current_entitlement.branding_tier)
    return TenantBrandingProfileSelection(
        tenant_id=profile.tenant_id,
        selection_id=selection_id,
        selection_revision=selection_revision,
        profile_id=profile.profile_id,
        profile_fingerprint=profile.fingerprint,
        branding_entitlement_id=current_entitlement.entitlement_id,
        branding_entitlement_revision=current_entitlement.lifecycle_revision,
        branding_entitlement_fingerprint=current_entitlement.fingerprint,
        branding_tier=tier,
        prior_selection_id=prior_id,
        prior_selection_fingerprint=prior_fingerprint,
        selected_at=selected_at,
        selection_evidence_reference=selection_evidence_reference,
        selection_evidence_fingerprint=selection_evidence_fingerprint,
    )


__all__ = [
    "SCHEMA",
    "SELECTION_FIELDS",
    "TenantBrandingProfileSelection",
    "TenantBrandingProfileSelectionError",
    "VERSION",
    "select_tenant_branding_profile",
]

# ARTIFACT: tenant_branding_profile_selection.py
# VERSION: v1.0.0-D21B4A-TENANT-BRANDING-PROFILE-SELECTION
# AUTHORITY BOUNDARY: immutable historical profile-selection evidence only; no durable currentness, browser, IAM or financial authority
# TENANT POSTURE: exact profile/current-ACTIVE-entitlement tenant and provenance correlation
# FAIL-CLOSED POSTURE: inactive/mismatched entitlement, lineage drift, malformed evidence, schema drift and corruption reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
