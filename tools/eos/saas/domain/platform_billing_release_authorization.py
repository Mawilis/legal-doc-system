"""WILSY OS — PLATFORM BILLING RELEASE AUTHORIZATION DOMAIN

TITLE: Platform Billing Release Authorization Domain
VERSION: v1.1.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-DOMAIN
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Preserve immutable tenant-scoped evidence that one exact platform
billing obligation has crossed a separately established release boundary.
EPITOME: Release authorization binds commercial and authorization evidence
without authenticating a principal, executing money, or proving settlement.
ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/platform_billing_release_authorization.py
OWNERSHIP: Python EOS sovereign business / commercial authority truth.
COLLABORATION: Wilson Khanyezi — Founder / Chief Architect; AI Engineering
under WAI-VAS23R3C governance.
CERTIFICATION / UPDATE DATE: 2026-09-04
CHANGELOG:
- 2026-09-04 — v1.1.0 adds opaque destination and idempotency binding,
  deterministic release fingerprint, and strict V2 persistence evidence.
- 2026-09-04 — v1.0.0 establishes the immutable platform billing
  release-authorization evidence contract.
COMPLIANCE: POPIA §19 | GDPR Article 32 | SOC2 CC7.2.
SECURITY / PRIVACY: Opaque references and SHA3-512 fingerprints only.
TENANT BOUNDARY: Every authorization is tenant-bound and invoice-bound.
AUTHORITY BOUNDARY:
  This object records release authorization evidence only. Construction does
  not authenticate a principal, establish an RBAC grant, prove an approval,
  or independently establish upstream authorization.
FINANCIAL AUTHORITY BOUNDARY:
  APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED.
  Kennel EOS remains the exclusive financial execution authority.
  Payment destination, provider execution, settlement, ledger mutation, and
  provider credentials are deliberately absent.
TRANSACTION BOUNDARY: Pure value object; no I/O, DB, network, or Kennel call.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any, Mapping


VERSION = "v1.1.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-DOMAIN"
SCHEMA = (
    "WILSY-PLATFORM-BILLING-RELEASE-AUTHORIZATION/V2"
)

_MAX_TENANT_ID_LENGTH = 128
_MAX_RELEASE_AUTHORIZATION_ID_LENGTH = 80
_MAX_PLATFORM_INVOICE_ID_LENGTH = 80
_MAX_AUTHORIZATION_EVIDENCE_REFERENCE_LENGTH = 240
_MAX_PRINCIPAL_ID_LENGTH = 120
_MAX_AUTHORIZATION_BASIS_REFERENCE_LENGTH = 240
_MAX_DESTINATION_REFERENCE_LENGTH = 240
_MAX_IDEMPOTENCY_KEY_LENGTH = 160


class PlatformBillingReleaseAuthorizationDomainError(ValueError):
    """Reject malformed immutable release-authorization evidence."""


def _require_text(
    value: Any,
    field_name: str,
    maximum: int,
) -> str:
    """Validate required text without silently truncating evidence."""
    if not isinstance(value, str):
        raise PlatformBillingReleaseAuthorizationDomainError(
            f"{field_name} is invalid"
        )

    normalized = value.strip()

    if not normalized or len(normalized) > maximum:
        raise PlatformBillingReleaseAuthorizationDomainError(
            f"{field_name} is invalid"
        )

    return normalized


def _require_sha3_512(
    value: Any,
    field_name: str,
) -> str:
    """Require exact lowercase SHA3-512 hexadecimal evidence."""
    if (
        not isinstance(value, str)
        or re.fullmatch(r"[0-9a-f]{128}", value) is None
    ):
        raise PlatformBillingReleaseAuthorizationDomainError(
            f"{field_name} is invalid"
        )

    return value

def _require_opaque_reference(value: Any, field_name: str) -> str:
    result = _require_text(value, field_name, _MAX_DESTINATION_REFERENCE_LENGTH)
    if any(token in result.lower() for token in ("bank", "account", "card", "secret", "token", "credential", "password")):
        raise PlatformBillingReleaseAuthorizationDomainError(f"{field_name} is invalid")
    return result


def _require_aware_utc(
    value: Any,
    field_name: str,
) -> datetime:
    """Require an aware timestamp and normalize it to UTC."""
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise PlatformBillingReleaseAuthorizationDomainError(
            f"{field_name} is invalid"
        )

    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class PlatformBillingReleaseAuthorization:
    """Immutable release evidence for one exact platform billing obligation.

    The platform-invoice fingerprint binds the commercial snapshot.
    The authorization-evidence reference and fingerprint bind separately
    established upstream authority evidence.

    Neither field is self-authenticating. A future authoritative Python EOS
    issuance boundary must establish and verify those facts before persistence.

    The destination reference is opaque authorization scope only and performs
    no financial execution.
    """

    tenant_id: str
    release_authorization_id: str
    platform_invoice_id: str
    platform_invoice_evidence_fingerprint: str
    authorization_evidence_reference: str
    authorization_evidence_fingerprint: str
    authorized_amount_minor: int
    currency: str
    authorized_by_principal_id: str
    authorization_basis_reference: str
    payment_destination_reference: str
    idempotency_key: str
    authorized_at: datetime
    created_at: datetime
    release_authorization_fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate structural, evidence, monetary, and temporal invariants."""
        text_fields = (
            (
                "tenant_id",
                _MAX_TENANT_ID_LENGTH,
            ),
            (
                "release_authorization_id",
                _MAX_RELEASE_AUTHORIZATION_ID_LENGTH,
            ),
            (
                "platform_invoice_id",
                _MAX_PLATFORM_INVOICE_ID_LENGTH,
            ),
            (
                "authorization_evidence_reference",
                _MAX_AUTHORIZATION_EVIDENCE_REFERENCE_LENGTH,
            ),
            (
                "authorized_by_principal_id",
                _MAX_PRINCIPAL_ID_LENGTH,
            ),
            (
                "authorization_basis_reference",
                _MAX_AUTHORIZATION_BASIS_REFERENCE_LENGTH,
            ),
        )

        for field_name, maximum in text_fields:
            object.__setattr__(
                self,
                field_name,
                _require_text(
                    getattr(self, field_name),
                    field_name,
                    maximum,
                ),
            )

        object.__setattr__(
            self,
            "platform_invoice_evidence_fingerprint",
            _require_sha3_512(
                self.platform_invoice_evidence_fingerprint,
                "platform_invoice_evidence_fingerprint",
            ),
        )

        object.__setattr__(
            self,
            "authorization_evidence_fingerprint",
            _require_sha3_512(
                self.authorization_evidence_fingerprint,
                "authorization_evidence_fingerprint",
            ),
        )
        object.__setattr__(self, "payment_destination_reference", _require_opaque_reference(self.payment_destination_reference, "payment_destination_reference"))
        object.__setattr__(self, "idempotency_key", _require_text(self.idempotency_key, "idempotency_key", _MAX_IDEMPOTENCY_KEY_LENGTH))

        if (
            not isinstance(self.authorized_amount_minor, int)
            or isinstance(self.authorized_amount_minor, bool)
            or self.authorized_amount_minor <= 0
        ):
            raise PlatformBillingReleaseAuthorizationDomainError(
                "authorized_amount_minor is invalid"
            )

        if (
            not isinstance(self.currency, str)
            or re.fullmatch(r"[A-Z]{3}", self.currency) is None
        ):
            raise PlatformBillingReleaseAuthorizationDomainError(
                "currency is invalid"
            )

        authorized_at = _require_aware_utc(
            self.authorized_at,
            "authorized_at",
        )
        created_at = _require_aware_utc(
            self.created_at,
            "created_at",
        )

        if created_at < authorized_at:
            raise PlatformBillingReleaseAuthorizationDomainError(
                "created_at cannot precede authorized_at"
            )

        object.__setattr__(
            self,
            "authorized_at",
            authorized_at,
        )
        object.__setattr__(
            self,
            "created_at",
            created_at,
        )
        computed = self.fingerprint
        if self.release_authorization_fingerprint and self.release_authorization_fingerprint != computed:
            raise PlatformBillingReleaseAuthorizationDomainError("release_authorization_fingerprint is invalid")
        object.__setattr__(self, "release_authorization_fingerprint", computed)

    def evidence_payload(self) -> dict[str, Any]:
        """Return complete deterministic semantic authorization material."""
        return {name: value for name, value in {
            "tenant_id": self.tenant_id, "release_authorization_id": self.release_authorization_id,
            "platform_invoice_id": self.platform_invoice_id,
            "platform_invoice_evidence_fingerprint": self.platform_invoice_evidence_fingerprint,
            "authorization_evidence_reference": self.authorization_evidence_reference,
            "authorization_evidence_fingerprint": self.authorization_evidence_fingerprint,
            "authorized_amount_minor": self.authorized_amount_minor, "currency": self.currency,
            "payment_destination_reference": self.payment_destination_reference, "idempotency_key": self.idempotency_key,
            "authorized_by_principal_id": self.authorized_by_principal_id, "authorization_basis_reference": self.authorization_basis_reference,
            "authorized_at": self.authorized_at.isoformat(), "created_at": self.created_at.isoformat(),
        }.items()}

    @property
    def fingerprint(self) -> str:
        """Return deterministic lowercase SHA3-512 authorization evidence."""
        import hashlib, json
        return hashlib.sha3_512(json.dumps(self.evidence_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

    def to_persistence_dict(self) -> dict[str, Any]:
        """Return the exact BSON/JSON-safe immutable evidence shape."""
        return {
            "schema": SCHEMA,
            "tenant_id": self.tenant_id,
            "release_authorization_id":
                self.release_authorization_id,
            "platform_invoice_id":
                self.platform_invoice_id,
            "platform_invoice_evidence_fingerprint":
                self.platform_invoice_evidence_fingerprint,
            "authorization_evidence_reference":
                self.authorization_evidence_reference,
            "authorization_evidence_fingerprint":
                self.authorization_evidence_fingerprint,
            "authorized_amount_minor":
                self.authorized_amount_minor,
            "currency": self.currency,
            "authorized_by_principal_id":
                self.authorized_by_principal_id,
            "authorization_basis_reference":
                self.authorization_basis_reference,
            "payment_destination_reference": self.payment_destination_reference,
            "idempotency_key": self.idempotency_key,
            "authorized_at":
                self.authorized_at.isoformat(),
            "created_at":
                self.created_at.isoformat(),
            "release_authorization_fingerprint": self.release_authorization_fingerprint,
        }

    @classmethod
    def from_persistence_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> "PlatformBillingReleaseAuthorization":
        """Strictly hydrate persisted evidence without granting authority."""
        expected_keys = {
            field.name
            for field in fields(cls)
        } | {"schema"}

        if (
            not isinstance(payload, Mapping)
            or set(payload) != expected_keys
            or payload.get("schema") != SCHEMA
        ):
            raise PlatformBillingReleaseAuthorizationDomainError(
                "invalid persistence fields"
            )

        try:
            data = dict(payload)
            data.pop("schema")
            data["authorized_at"] = datetime.fromisoformat(
                data["authorized_at"]
            )
            data["created_at"] = datetime.fromisoformat(
                data["created_at"]
            )
            return cls(**data)
        except (
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            raise PlatformBillingReleaseAuthorizationDomainError(
                "invalid persistence payload"
            ) from error


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT:
#   platform_billing_release_authorization.py
# VERSION:
#   v1.1.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-DOMAIN
# AUTHORITY:
#   Python EOS immutable platform billing release evidence only.
# TENANT POSTURE:
#   Tenant-bound and exact platform-invoice-bound evidence.
# AUTHORITY POSTURE:
#   Upstream authorization must be independently established and fingerprinted.
# FINANCIAL EXECUTION AUTHORITY:
#   Kennel EOS exclusively.
# ARCHITECTURE:
#   APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED.
# RUNTIME:
#   PURE / NO I/O / NO DB / NO NETWORK / NO KENNEL INVOCATION.
# END OF WILSY OS SOVEREIGN ARTIFACT
