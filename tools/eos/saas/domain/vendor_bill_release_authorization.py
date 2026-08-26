"""WILSY OS — VENDOR BILL RELEASE AUTHORIZATION DOMAIN
Version: v1.0.0-VENDOR-BILL-RELEASE-AUTHORIZATION-DOMAIN
Authority: Wilsy OS Core Governance
Classification: Institutional Artifact — Production Only

EPITOME: Immutable tenant-scoped authorization evidence permitting a specific
approved VendorBill revision to cross the release boundary toward future
Kennel EOS execution without moving money or proving execution or settlement.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/vendor_bill_release_authorization.py
ARCHITECTURE LOCK: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
KENNEL EOS: exclusive financial execution authority.
COLLABORATION: Wilson Khanyezi — Founder / Chief Architect; AI Engineering
(Codex) — governed implementation under R2B-01; Date: 2026-08-26
CHANGELOG: 2026-08-26 — v1.0.0 initial immutable contract.
COMPLIANCE: POPIA §19 | GDPR §32 | SOC2 CC7.2
"""

from __future__ import annotations

import re
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any, Mapping

VERSION = "v1.0.0-VENDOR-BILL-RELEASE-AUTHORIZATION-DOMAIN"
SCHEMA = "WILSY-VENDOR-BILL-RELEASE-AUTHORIZATION/V1"
_MAX_TENANT_ID_LENGTH = 128
_MAX_RELEASE_AUTHORIZATION_ID_LENGTH = 80
_MAX_PAYABLE_ID_LENGTH = 80
_MAX_EFFECTIVE_RESULT_ID_LENGTH = 80
_MAX_ACTOR_ID_LENGTH = 120
_MAX_AUTHORIZATION_BASIS_REFERENCE_LENGTH = 240


class VendorBillReleaseAuthorizationDomainError(ValueError):
    """Description: invalid immutable release evidence.

    Collaboration: Codex implementation under the R2B-01 governance mandate.
    Institutional: rejecting malformed evidence prevents unsafe authority
    from crossing tenant or lifecycle boundaries.
    """


def _require_text(value: Any, field_name: str, maximum: int) -> str:
    """Validate required text without silently truncating caller evidence."""
    if not isinstance(value, str):
        raise VendorBillReleaseAuthorizationDomainError(f"{field_name} is invalid")
    normalized = value.strip()
    if not normalized or len(normalized) > maximum:
        raise VendorBillReleaseAuthorizationDomainError(f"{field_name} is invalid")
    return normalized


def _require_aware_utc(value: Any, field_name: str) -> datetime:
    """Require an aware timestamp and normalize it for deterministic comparison."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise VendorBillReleaseAuthorizationDomainError(f"{field_name} is invalid")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class VendorBillReleaseAuthorization:
    """Description: immutable evidence for one approved bill revision.

    Collaboration: Founder authority defines the separation from execution.
    Institutional: tenant_id prevents cross-tenant authority; payable_id binds
    the canonical AP obligation; revision prevents authority drifting across
    revisions; result ID and fingerprint bind immutable approval evidence.
    Amount and currency define authorization scope only, never execution proof.
    No payment destination exists by design; Kennel EOS owns execution.
    """

    tenant_id: str
    release_authorization_id: str
    payable_id: str
    vendor_bill_revision: int
    approval_effective_result_id: str
    approval_effective_result_fingerprint: str
    authorized_amount_minor: int
    currency: str
    authorized_by_actor_id: str
    authorization_basis_reference: str
    authorized_at: datetime
    created_at: datetime

    def __post_init__(self) -> None:
        """Validate structural, evidence, and temporal invariants."""
        text_fields = (
            ("tenant_id", _MAX_TENANT_ID_LENGTH),
            ("release_authorization_id", _MAX_RELEASE_AUTHORIZATION_ID_LENGTH),
            ("payable_id", _MAX_PAYABLE_ID_LENGTH),
            ("approval_effective_result_id", _MAX_EFFECTIVE_RESULT_ID_LENGTH),
            ("authorized_by_actor_id", _MAX_ACTOR_ID_LENGTH),
            ("authorization_basis_reference", _MAX_AUTHORIZATION_BASIS_REFERENCE_LENGTH),
        )
        for field_name, maximum in text_fields:
            object.__setattr__(self, field_name, _require_text(getattr(self, field_name), field_name, maximum))

        for field_name, minimum in (("vendor_bill_revision", 1), ("authorized_amount_minor", 1)):
            value = getattr(self, field_name)
            # bool is an int subclass, but is never valid financial evidence.
            if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
                raise VendorBillReleaseAuthorizationDomainError(f"{field_name} is invalid")

        # Caller currency is not auto-uppercased: normalization could hide bad input.
        if not isinstance(self.currency, str) or re.fullmatch(r"[A-Z]{3}", self.currency) is None:
            raise VendorBillReleaseAuthorizationDomainError("currency is invalid")
        # Exact lowercase SHA3-512 hex binds approval evidence without ambiguity.
        if not isinstance(self.approval_effective_result_fingerprint, str) or re.fullmatch(
            r"[0-9a-f]{128}", self.approval_effective_result_fingerprint
        ) is None:
            raise VendorBillReleaseAuthorizationDomainError("approval_effective_result_fingerprint is invalid")

        # UTC normalization makes comparisons deterministic across jurisdictions.
        authorized_at = _require_aware_utc(self.authorized_at, "authorized_at")
        created_at = _require_aware_utc(self.created_at, "created_at")
        # Creation cannot precede the authorization it records.
        if created_at < authorized_at:
            raise VendorBillReleaseAuthorizationDomainError("created_at cannot precede authorized_at")
        object.__setattr__(self, "authorized_at", authorized_at)
        object.__setattr__(self, "created_at", created_at)

    def to_persistence_dict(self) -> dict[str, Any]:
        """Description: emit deterministic persistence evidence.

        Collaboration: consumed by the future tenant-scoped
        release-authorization registry and forensic evidence surfaces;
        serialization itself performs no I/O.
        Institutional: a fixed shape prevents schema drift and deliberately
        contains no destination or execution data.
        Returns: exact BSON/JSON-safe field mapping.
        """
        return {
            "schema": SCHEMA,
            "tenant_id": self.tenant_id,
            "release_authorization_id": self.release_authorization_id,
            "payable_id": self.payable_id,
            "vendor_bill_revision": self.vendor_bill_revision,
            "approval_effective_result_id": self.approval_effective_result_id,
            "approval_effective_result_fingerprint": self.approval_effective_result_fingerprint,
            "authorized_amount_minor": self.authorized_amount_minor,
            "currency": self.currency,
            "authorized_by_actor_id": self.authorized_by_actor_id,
            "authorization_basis_reference": self.authorization_basis_reference,
            "authorized_at": self.authorized_at.isoformat(),
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_persistence_dict(cls, payload: Mapping[str, Any]) -> "VendorBillReleaseAuthorization":
        """Description: strictly hydrate persisted evidence.

        Collaboration: used by the future tenant-scoped release-authorization
        registry to reconstruct durable evidence; hydration never invokes
        Kennel EOS or grants execution authority.
        Institutional: exact key equality rejects missing and unexpected fields;
        hydration reconstructs evidence but never grants execution authority.
        Args: payload, persisted mapping with the canonical schema.
        Returns: validated immutable authorization.
        Raises: VendorBillReleaseAuthorizationDomainError for any mismatch.
        """
        expected_keys = {field.name for field in fields(cls)} | {"schema"}
        if not isinstance(payload, Mapping) or set(payload) != expected_keys or payload.get("schema") != SCHEMA:
            raise VendorBillReleaseAuthorizationDomainError("invalid persistence fields")
        try:
            data = dict(payload)
            data.pop("schema")
            data["authorized_at"] = datetime.fromisoformat(data["authorized_at"])
            data["created_at"] = datetime.fromisoformat(data["created_at"])
            return cls(**data)
        except (KeyError, TypeError, ValueError) as error:
            raise VendorBillReleaseAuthorizationDomainError("invalid persistence payload") from error


# INSTITUTIONAL CERTIFICATION SEAL
# File: vendor_bill_release_authorization.py
# Version: v1.0.0-VENDOR-BILL-RELEASE-AUTHORIZATION-DOMAIN
# Status: SOVEREIGN DOMAIN CONTRACT — R2B-01 | Authority: Wilsy OS Core Governance
# Architecture: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
# Tenant isolation; SHA3-512 approval binding; Kennel EOS execution ownership.
# Runtime posture: PURE / NO I/O / NO DB / NO NETWORK
# POPIA §19 | GDPR §32 | SOC2 CC7.2 | Certification date: 2026-08-26
