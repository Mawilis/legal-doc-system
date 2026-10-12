"""WILSY OS immutable Legal Storefront public-intent evidence.

TITLE: Legal Storefront Public Intent
VERSION: v1.0.0-L8-9A-LEGAL-STOREFRONT-PUBLIC-INTENT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Capture one bounded pre-tenant public request to explore Legal
         Operations without creating tenant, identity, subscription,
         entitlement, Legal lifecycle, billing, payment, or settlement truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_storefront_public_intent.py
COLLABORATION / OWNERSHIP: Storefront owns public presentation only. This domain
                            owns immutable public-intent evidence. Identity,
                            pre-tenant bootstrap, tenant genesis, subscription,
                            entitlement and Legal Operations admission remain
                            separately governed downstream authorities.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-9A-LEGAL-STOREFRONT-PUBLIC-INTENT establishes
           bounded organization/contact/industry/region public-intent evidence,
           strict exact-field hydration, deterministic SHA3-512 fingerprinting
           and an explicit no-authority boundary.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Stores only bounded organization/contact request
                             metadata required for public acquisition evidence.
                             No password, credential, secret, API key, payment
                             coordinate, or authenticated principal is accepted.
TENANT BOUNDARY: Pre-tenant by definition. No tenant identifier exists in this
                 artifact and no public input may establish tenant scope.
AUTHORITY BOUNDARY: Public intent evidence only. It cannot create or select a
                    tenant, principal, membership, role, plan, subscription,
                    entitlement, LegalInstruction, CaseMatter, ProcessDocument,
                    billing authority, payment execution, or settlement truth.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Final, Mapping, NoReturn

VERSION: Final[str] = "v1.0.0-L8-9A-LEGAL-STOREFRONT-PUBLIC-INTENT"
SCHEMA: Final[str] = "WILSY-LEGAL-STOREFRONT-PUBLIC-INTENT/V1"
INTENT_KIND: Final[str] = "LEGAL_OPERATIONS_ACQUISITION"

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_EMAIL: Final[re.Pattern[str]] = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)
_FINGERPRINT: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_REGION: Final[re.Pattern[str]] = re.compile(
    r"^[A-Z][A-Z0-9_-]{1,31}$"
)

_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "intent_version",
    "intent_kind",
    "intent_id",
    "organization_name",
    "contact_email",
    "industry",
    "region",
    "submitted_at",
    "fingerprint",
)


class LegalStorefrontPublicIntentError(ValueError):
    """Fail-closed public-intent validation error.

    This exception represents malformed or authority-bearing public input only.
    It grants no tenant, identity, Legal Operations, commercial, or financial
    authority and carries no persistence or retry semantics.
    """


def _fail(code: str) -> NoReturn:
    """Raise one stable fail-closed public-intent error code."""
    raise LegalStorefrontPublicIntentError(code)


def _bounded_text(
    name: str,
    value: object,
    *,
    minimum: int,
    maximum: int,
) -> str:
    """Normalize one bounded, trimmed public metadata field."""
    if not isinstance(value, str):
        _fail(f"L8_9A_{name.upper()}_INVALID")
    normalized = value.strip()
    if normalized != value or not minimum <= len(normalized) <= maximum:
        _fail(f"L8_9A_{name.upper()}_INVALID")
    if any(ord(character) < 32 for character in normalized):
        _fail(f"L8_9A_{name.upper()}_INVALID")
    return normalized


def _intent_id(value: object) -> str:
    """Validate one server-issued opaque public-intent identity."""
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        _fail("L8_9A_INTENT_ID_INVALID")
    return value


def _email(value: object) -> str:
    """Normalize one bounded public contact email without identity authority."""
    normalized = _bounded_text(
        "contact_email",
        value,
        minimum=3,
        maximum=254,
    ).lower()
    if _EMAIL.fullmatch(normalized) is None:
        _fail("L8_9A_CONTACT_EMAIL_INVALID")
    local, domain = normalized.rsplit("@", 1)
    if not local or not domain or len(local) > 64:
        _fail("L8_9A_CONTACT_EMAIL_INVALID")
    return normalized


def _industry(value: object) -> str:
    """Validate descriptive industry metadata without product authority."""
    return _bounded_text(
        "industry",
        value,
        minimum=2,
        maximum=80,
    )


def _region(value: object) -> str:
    """Validate one descriptive public acquisition region label."""
    normalized = _bounded_text(
        "region",
        value,
        minimum=2,
        maximum=32,
    ).upper()
    if _REGION.fullmatch(normalized) is None:
        _fail("L8_9A_REGION_INVALID")
    return normalized


def _utc_datetime(value: object) -> datetime:
    """Require one timezone-aware UTC timestamp with stable precision."""
    if not isinstance(value, datetime):
        _fail("L8_9A_SUBMITTED_AT_INVALID")
    if value.tzinfo is None or value.utcoffset() is None:
        _fail("L8_9A_SUBMITTED_AT_INVALID")
    return value.astimezone(timezone.utc)


def _timestamp(value: datetime) -> str:
    """Serialize one UTC timestamp deterministically."""
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _parse_timestamp(value: object) -> datetime:
    """Strictly hydrate one persisted UTC timestamp."""
    if not isinstance(value, str) or not value.endswith("Z"):
        _fail("L8_9A_SUBMITTED_AT_INVALID")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        _fail("L8_9A_SUBMITTED_AT_INVALID")
    normalized = _utc_datetime(parsed)
    if _timestamp(normalized) != value:
        _fail("L8_9A_SUBMITTED_AT_INVALID")
    return normalized


def _fingerprint_payload(
    *,
    intent_id: str,
    organization_name: str,
    contact_email: str,
    industry: str,
    region: str,
    submitted_at: datetime,
) -> dict[str, object]:
    """Build the exact semantic payload covered by the SHA3-512 fingerprint."""
    return {
        "schema": SCHEMA,
        "intent_version": VERSION,
        "intent_kind": INTENT_KIND,
        "intent_id": intent_id,
        "organization_name": organization_name,
        "contact_email": contact_email,
        "industry": industry,
        "region": region,
        "submitted_at": _timestamp(submitted_at),
    }


def _compute_fingerprint(
    *,
    intent_id: str,
    organization_name: str,
    contact_email: str,
    industry: str,
    region: str,
    submitted_at: datetime,
) -> str:
    """Derive deterministic lowercase SHA3-512 public-intent evidence."""
    encoded = json.dumps(
        _fingerprint_payload(
            intent_id=intent_id,
            organization_name=organization_name,
            contact_email=contact_email,
            industry=industry,
            region=region,
            submitted_at=submitted_at,
        ),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalStorefrontPublicIntent:
    """Immutable pre-tenant Legal Operations acquisition intent.

    This value records only bounded public request metadata. Construction,
    serialization, hydration, replay, or possession never authenticates a
    principal, creates tenant scope, selects a plan, provisions a subscription
    or entitlement, admits a Legal Operations lifecycle command, or establishes
    billing/payment/settlement authority.

    Persistence, idempotency, public HTTP admission, identity verification and
    reviewed handoff to deployment-rooted tenant genesis are deliberately
    outside this domain artifact.
    """

    schema: str
    intent_version: str
    intent_kind: str
    intent_id: str
    organization_name: str
    contact_email: str
    industry: str
    region: str
    submitted_at: datetime
    fingerprint: str

    def __post_init__(self) -> None:
        """Validate exact immutable state and recompute semantic integrity."""
        if self.schema != SCHEMA:
            _fail("L8_9A_SCHEMA_INVALID")
        if self.intent_version != VERSION:
            _fail("L8_9A_VERSION_INVALID")
        if self.intent_kind != INTENT_KIND:
            _fail("L8_9A_INTENT_KIND_INVALID")

        intent_id = _intent_id(self.intent_id)
        organization_name = _bounded_text(
            "organization_name",
            self.organization_name,
            minimum=2,
            maximum=200,
        )
        contact_email = _email(self.contact_email)
        industry = _industry(self.industry)
        region = _region(self.region)
        submitted_at = _utc_datetime(self.submitted_at)

        expected = _compute_fingerprint(
            intent_id=intent_id,
            organization_name=organization_name,
            contact_email=contact_email,
            industry=industry,
            region=region,
            submitted_at=submitted_at,
        )
        if (
            not isinstance(self.fingerprint, str)
            or _FINGERPRINT.fullmatch(self.fingerprint) is None
            or self.fingerprint != expected
        ):
            _fail("L8_9A_FINGERPRINT_INVALID")

        object.__setattr__(self, "intent_id", intent_id)
        object.__setattr__(self, "organization_name", organization_name)
        object.__setattr__(self, "contact_email", contact_email)
        object.__setattr__(self, "industry", industry)
        object.__setattr__(self, "region", region)
        object.__setattr__(self, "submitted_at", submitted_at)

    def to_dict(self) -> dict[str, object]:
        """Return the exact persisted-safe public-intent mapping.

        The mapping contains no tenant, principal, credential, role, commercial
        authority, Legal lifecycle authority, payment, or settlement fields.
        """
        return {
            "schema": self.schema,
            "intent_version": self.intent_version,
            "intent_kind": self.intent_kind,
            "intent_id": self.intent_id,
            "organization_name": self.organization_name,
            "contact_email": self.contact_email,
            "industry": self.industry,
            "region": self.region,
            "submitted_at": _timestamp(self.submitted_at),
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalStorefrontPublicIntent":
        """Strictly hydrate one exact public-intent artifact.

        Extra or missing fields fail closed, preventing legacy Storefront input
        from smuggling tenant, credential, plan, subscription, entitlement,
        Legal lifecycle, billing, payment, or settlement authority.
        """
        if not isinstance(payload, Mapping):
            _fail("L8_9A_PAYLOAD_INVALID")
        if set(payload.keys()) != set(_FIELDS):
            _fail("L8_9A_FIELDS_INVALID")

        submitted_at = _parse_timestamp(payload["submitted_at"])
        return cls(
            schema=str(payload["schema"]),
            intent_version=str(payload["intent_version"]),
            intent_kind=str(payload["intent_kind"]),
            intent_id=str(payload["intent_id"]),
            organization_name=str(payload["organization_name"]),
            contact_email=str(payload["contact_email"]),
            industry=str(payload["industry"]),
            region=str(payload["region"]),
            submitted_at=submitted_at,
            fingerprint=str(payload["fingerprint"]),
        )


def create_legal_storefront_public_intent(
    *,
    intent_id: str,
    organization_name: str,
    contact_email: str,
    industry: str,
    region: str,
    submitted_at: datetime,
) -> LegalStorefrontPublicIntent:
    """Create one immutable pre-tenant Legal Operations public intent.

    ``intent_id`` and ``submitted_at`` are orchestration inputs expected to be
    server-issued by a later public-admission boundary. The remaining values are
    public request metadata only. This factory performs no authentication,
    tenant genesis, identity creation, role assignment, subscription,
    entitlement, Legal lifecycle admission, persistence, billing, payment,
    settlement, notification, or external-provider work.
    """
    normalized_intent_id = _intent_id(intent_id)
    normalized_organization = _bounded_text(
        "organization_name",
        organization_name,
        minimum=2,
        maximum=200,
    )
    normalized_email = _email(contact_email)
    normalized_industry = _industry(industry)
    normalized_region = _region(region)
    normalized_submitted_at = _utc_datetime(submitted_at)

    fingerprint = _compute_fingerprint(
        intent_id=normalized_intent_id,
        organization_name=normalized_organization,
        contact_email=normalized_email,
        industry=normalized_industry,
        region=normalized_region,
        submitted_at=normalized_submitted_at,
    )

    return LegalStorefrontPublicIntent(
        schema=SCHEMA,
        intent_version=VERSION,
        intent_kind=INTENT_KIND,
        intent_id=normalized_intent_id,
        organization_name=normalized_organization,
        contact_email=normalized_email,
        industry=normalized_industry,
        region=normalized_region,
        submitted_at=normalized_submitted_at,
        fingerprint=fingerprint,
    )


__all__ = [
    "INTENT_KIND",
    "SCHEMA",
    "VERSION",
    "LegalStorefrontPublicIntent",
    "LegalStorefrontPublicIntentError",
    "create_legal_storefront_public_intent",
]

# ARTIFACT: legal_storefront_public_intent.py
# VERSION: v1.0.0-L8-9A-LEGAL-STOREFRONT-PUBLIC-INTENT
# AUTHORITY BOUNDARY: immutable pre-tenant public-intent evidence only; no tenant, identity, subscription, entitlement, Legal lifecycle, billing, payment, or settlement authority
# TENANT POSTURE: pre-tenant by definition; this artifact contains no tenant identifier and cannot create tenant scope
# FAIL-CLOSED POSTURE: malformed, extra-field, naive-time, noncanonical-region, email, schema, version, kind, identity, or fingerprint divergence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
