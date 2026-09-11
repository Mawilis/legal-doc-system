"""WILSY OS tenant inbound provider credential-security authority domain fact.

TITLE: Tenant Inbound Provider Credential Security Authority
VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P2
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable, provider-neutral historical evidence describing the security
         eligibility of one exact tenant/provider/configuration credential version.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/tenant_inbound_provider_credential_security_authority.py
COLLABORATION / OWNERSHIP: SaaS credential-security domain owner; registry,
                            issuance, current-pointer, binding, and provider
                            adapters remain separate future owners.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3D-P2 establishes four immutable security
           states, strict half-open validity, and deterministic SHA3-512 identity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references and fingerprints only; no raw or
                             decrypted secrets, network, database, or KMS access.
TENANT BOUNDARY: tenant_id participates in identity and all future persistence
                 and currentness lookups.
AUTHORITY BOUNDARY: Historical credential-security evidence only; this fact does
                    not authorize current binding, checkout, or secret use.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement truth.
FAIL-CLOSED DECLARATION: Unknown states, schema drift, time drift, digest drift,
                          malformed identities, and unsupported versions reject.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
import hashlib
import json
import re
from typing import Any, ClassVar, Mapping, cast


VERSION = "v1.0.0-M11-R8-R3B-P8-P3D-P2"
CAMPAIGN_IDENTITY = "M11-R8-R3B-P8-P3D-P2"
SECURITY_FINGERPRINT_VERSION = "v1"
SECURITY_FINGERPRINT_SCHEMA = "WILSY-TENANT-INBOUND-PROVIDER-CREDENTIAL-SECURITY/V1"
HASH_ALGORITHM = "SHA3-512"
_SHA3_512 = re.compile(r"^[0-9a-f]{128}$")


class TenantInboundProviderCredentialSecurityAuthorityError(ValueError):
    """Raised when one immutable credential-security fact violates its schema."""


class TenantInboundProviderCredentialSecurityState(StrEnum):
    """Closed V1 meanings for immutable credential-security evidence."""

    ELIGIBLE = "ELIGIBLE"
    COMPROMISED = "COMPROMISED"
    REVOKED = "REVOKED"
    ROTATED = "ROTATED"


# Repository-facing aliases retain one canonical state vocabulary.
CredentialSecurityState = TenantInboundProviderCredentialSecurityState
InboundProviderCredentialSecurityState = TenantInboundProviderCredentialSecurityState
SecurityState = TenantInboundProviderCredentialSecurityState


def _text(name: str, value: object) -> str:
    """Require an exact non-blank authority identifier without normalization."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantInboundProviderCredentialSecurityAuthorityError(
            f"M11P3D_INVALID_{name.upper()}"
        )
    return value


def _positive_version(name: str, value: object) -> int:
    """Require a positive, non-boolean integer configuration version."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise TenantInboundProviderCredentialSecurityAuthorityError(
            f"M11P3D_INVALID_{name.upper()}"
        )
    return value


def _revision(value: object) -> int:
    """Require a non-negative, non-boolean security revision."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TenantInboundProviderCredentialSecurityAuthorityError(
            "M11P3D_INVALID_SECURITY_REVISION"
        )
    return value


def _fingerprint(name: str, value: object) -> str:
    """Require a lowercase canonical SHA3-512 hexadecimal fingerprint."""
    if not isinstance(value, str) or _SHA3_512.fullmatch(value) is None:
        raise TenantInboundProviderCredentialSecurityAuthorityError(
            f"M11P3D_INVALID_{name.upper()}"
        )
    return value


def _timestamp(name: str, value: object) -> datetime:
    """Require an aware UTC timestamp; offsets are never silently rewritten."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise TenantInboundProviderCredentialSecurityAuthorityError(
            f"M11P3D_INVALID_{name.upper()}"
        )
    if value.utcoffset() != timedelta(0):
        raise TenantInboundProviderCredentialSecurityAuthorityError(
            f"M11P3D_NON_UTC_{name.upper()}"
        )
    return value.astimezone(timezone.utc)


def _json_bytes(value: Mapping[str, object]) -> bytes:
    """Serialize semantic fields deterministically for cryptographic identity."""
    return json.dumps(
        dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def is_valid_at(valid_from: datetime, valid_until: datetime, at: datetime) -> bool:
    """Evaluate the pure half-open interval ``valid_from <= at < valid_until``.

    The predicate performs no clock, database, KMS, network, pointer, or binding
    lookup.  All three values must already be timezone-aware UTC timestamps.
    """
    start = _timestamp("valid_from", valid_from)
    end = _timestamp("valid_until", valid_until)
    instant = _timestamp("validity_check_time", at)
    if end <= start:
        raise TenantInboundProviderCredentialSecurityAuthorityError(
            "M11P3D_INVALID_VALIDITY_INTERVAL"
        )
    return start <= instant < end


@dataclass(frozen=True, slots=True)
class TenantInboundProviderCredentialSecurityAuthority:
    """Immutable historical security fact for one exact credential version.

    This value object records what a future issuance authority evaluated.  It
    never resolves ``credential_reference``, reads current privilege, interprets
    current-pointer state, contacts a provider, accesses KMS, or mutates durable
    state.  A later registry will own append-only persistence and currentness.
    """

    tenant_id: str
    provider_id: str
    merchant_configuration_id: str
    merchant_configuration_version: int
    merchant_configuration_fingerprint: str
    credential_reference: str
    credential_version: str
    security_state: TenantInboundProviderCredentialSecurityState
    security_revision: int
    valid_from: datetime
    valid_until: datetime
    evaluated_at: datetime
    authorization_decision_id: str
    authorization_evidence_fingerprint: str
    security_fingerprint_version: str = SECURITY_FINGERPRINT_VERSION
    security_fingerprint: str | None = None

    _SEMANTIC_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {
            "tenant_id",
            "provider_id",
            "merchant_configuration_id",
            "merchant_configuration_version",
            "merchant_configuration_fingerprint",
            "credential_reference",
            "credential_version",
            "security_state",
            "security_revision",
            "valid_from",
            "valid_until",
            "evaluated_at",
            "authorization_decision_id",
            "authorization_evidence_fingerprint",
            "security_fingerprint_version",
        }
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "tenant_id", _text("tenant_id", self.tenant_id))
        object.__setattr__(self, "provider_id", _text("provider_id", self.provider_id))
        object.__setattr__(
            self,
            "merchant_configuration_id",
            _text("merchant_configuration_id", self.merchant_configuration_id),
        )
        object.__setattr__(
            self,
            "merchant_configuration_version",
            _positive_version(
                "merchant_configuration_version", self.merchant_configuration_version
            ),
        )
        object.__setattr__(
            self,
            "merchant_configuration_fingerprint",
            _fingerprint(
                "merchant_configuration_fingerprint",
                self.merchant_configuration_fingerprint,
            ),
        )
        object.__setattr__(
            self, "credential_reference", _text("credential_reference", self.credential_reference)
        )
        object.__setattr__(
            self, "credential_version", _text("credential_version", self.credential_version)
        )
        if not isinstance(self.security_state, TenantInboundProviderCredentialSecurityState):
            raise TenantInboundProviderCredentialSecurityAuthorityError(
                "M11P3D_INVALID_SECURITY_STATE"
            )
        object.__setattr__(self, "security_revision", _revision(self.security_revision))
        start = _timestamp("valid_from", self.valid_from)
        end = _timestamp("valid_until", self.valid_until)
        evaluated = _timestamp("evaluated_at", self.evaluated_at)
        if end <= start:
            raise TenantInboundProviderCredentialSecurityAuthorityError(
                "M11P3D_INVALID_VALIDITY_INTERVAL"
            )
        if not start <= evaluated < end:
            raise TenantInboundProviderCredentialSecurityAuthorityError(
                "M11P3D_EVALUATED_AT_OUTSIDE_VALIDITY"
            )
        object.__setattr__(self, "valid_from", start)
        object.__setattr__(self, "valid_until", end)
        object.__setattr__(self, "evaluated_at", evaluated)
        object.__setattr__(
            self,
            "authorization_decision_id",
            _text("authorization_decision_id", self.authorization_decision_id),
        )
        object.__setattr__(
            self,
            "authorization_evidence_fingerprint",
            _fingerprint(
                "authorization_evidence_fingerprint",
                self.authorization_evidence_fingerprint,
            ),
        )
        if self.security_fingerprint_version != SECURITY_FINGERPRINT_VERSION:
            raise TenantInboundProviderCredentialSecurityAuthorityError(
                "M11P3D_INVALID_SECURITY_FINGERPRINT_VERSION"
            )
        expected = self.compute_fingerprint()
        if self.security_fingerprint is not None:
            supplied = _fingerprint("security_fingerprint", self.security_fingerprint)
            if supplied != expected:
                raise TenantInboundProviderCredentialSecurityAuthorityError(
                    "M11P3D_SECURITY_FINGERPRINT_MISMATCH"
                )
        object.__setattr__(self, "security_fingerprint", expected)

    def _semantic_payload(self) -> dict[str, object]:
        """Return every immutable authority field except its derived digest."""
        return {
            "tenant_id": self.tenant_id,
            "provider_id": self.provider_id,
            "merchant_configuration_id": self.merchant_configuration_id,
            "merchant_configuration_version": self.merchant_configuration_version,
            "merchant_configuration_fingerprint": self.merchant_configuration_fingerprint,
            "credential_reference": self.credential_reference,
            "credential_version": self.credential_version,
            "security_state": self.security_state.value,
            "security_revision": self.security_revision,
            "valid_from": self.valid_from.isoformat(),
            "valid_until": self.valid_until.isoformat(),
            "evaluated_at": self.evaluated_at.isoformat(),
            "authorization_decision_id": self.authorization_decision_id,
            "authorization_evidence_fingerprint": self.authorization_evidence_fingerprint,
            "security_fingerprint_version": self.security_fingerprint_version,
        }

    def compute_fingerprint(self) -> str:
        """Compute deterministic lowercase SHA3-512 over immutable authority data."""
        return hashlib.sha3_512(_json_bytes(self._semantic_payload())).hexdigest()

    @property
    def fingerprint(self) -> str:
        """Return the validated canonical security fingerprint."""
        assert self.security_fingerprint is not None
        return self.security_fingerprint

    @property
    def is_eligible(self) -> bool:
        """Report only the historical state label, never current binding authority."""
        return self.security_state is TenantInboundProviderCredentialSecurityState.ELIGIBLE

    def is_valid_at(self, at: datetime) -> bool:
        """Evaluate this fact's pure half-open validity interval at an explicit time."""
        return is_valid_at(self.valid_from, self.valid_until, at)

    def verify_fingerprint(self, fingerprint: str | None = None) -> bool:
        """Verify a supplied digest against canonical immutable authority data."""
        supplied = self.fingerprint if fingerprint is None else _fingerprint("security_fingerprint", fingerprint)
        return supplied == self.compute_fingerprint()

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact strict persisted schema without runtime state."""
        payload = self._semantic_payload()
        payload["security_fingerprint"] = self.fingerprint
        return payload

    to_persisted = to_dict

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "TenantInboundProviderCredentialSecurityAuthority":
        """Hydrate strictly, rejecting missing/unknown fields and digest drift."""
        expected = set(cls._SEMANTIC_FIELDS) | {"security_fingerprint"}
        if not isinstance(payload, dict) or set(payload) != expected:
            raise TenantInboundProviderCredentialSecurityAuthorityError(
                "M11P3D_INVALID_SECURITY_AUTHORITY_SCHEMA"
            )
        data = cast(dict[str, Any], payload)
        try:
            valid_from = data["valid_from"]
            valid_until = data["valid_until"]
            evaluated_at = data["evaluated_at"]
            if isinstance(valid_from, str):
                valid_from = datetime.fromisoformat(valid_from)
            if isinstance(valid_until, str):
                valid_until = datetime.fromisoformat(valid_until)
            if isinstance(evaluated_at, str):
                evaluated_at = datetime.fromisoformat(evaluated_at)
            return cls(
                tenant_id=data["tenant_id"],
                provider_id=data["provider_id"],
                merchant_configuration_id=data["merchant_configuration_id"],
                merchant_configuration_version=data["merchant_configuration_version"],
                merchant_configuration_fingerprint=data["merchant_configuration_fingerprint"],
                credential_reference=data["credential_reference"],
                credential_version=data["credential_version"],
                security_state=TenantInboundProviderCredentialSecurityState(data["security_state"]),
                security_revision=data["security_revision"],
                valid_from=valid_from,
                valid_until=valid_until,
                evaluated_at=evaluated_at,
                authorization_decision_id=data["authorization_decision_id"],
                authorization_evidence_fingerprint=data["authorization_evidence_fingerprint"],
                security_fingerprint_version=data["security_fingerprint_version"],
                security_fingerprint=data["security_fingerprint"],
            )
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, TenantInboundProviderCredentialSecurityAuthorityError):
                raise
            raise TenantInboundProviderCredentialSecurityAuthorityError(
                "M11P3D_INVALID_SECURITY_AUTHORITY"
            ) from error

    def __repr__(self) -> str:
        """Render bounded diagnostics without exposing the credential reference."""
        return (
            "TenantInboundProviderCredentialSecurityAuthority("
            f"tenant_id={self.tenant_id!r}, provider_id={self.provider_id!r}, "
            f"merchant_configuration_id={self.merchant_configuration_id!r}, "
            f"merchant_configuration_version={self.merchant_configuration_version!r}, "
            f"credential_reference='[REDACTED_REFERENCE]', "
            f"credential_version={self.credential_version!r}, "
            f"security_state={self.security_state!r}, security_revision={self.security_revision!r}, "
            f"valid_from={self.valid_from!r}, valid_until={self.valid_until!r}, "
            f"evaluated_at={self.evaluated_at!r}, authorization_decision_id={self.authorization_decision_id!r}, "
            f"authorization_evidence_fingerprint={self.authorization_evidence_fingerprint!r}, "
            f"security_fingerprint={self.fingerprint!r})"
        )


# Explicit aliases avoid parallel authority classes while supporting repository naming styles.
InboundProviderCredentialSecurityAuthority = TenantInboundProviderCredentialSecurityAuthority
TenantInboundCredentialSecurityAuthority = TenantInboundProviderCredentialSecurityAuthority


__all__ = [
    "CAMPAIGN_IDENTITY",
    "CredentialSecurityState",
    "HASH_ALGORITHM",
    "InboundProviderCredentialSecurityAuthority",
    "InboundProviderCredentialSecurityState",
    "SECURITY_FINGERPRINT_SCHEMA",
    "SECURITY_FINGERPRINT_VERSION",
    "SecurityState",
    "TenantInboundProviderCredentialSecurityAuthority",
    "TenantInboundProviderCredentialSecurityAuthorityError",
    "TenantInboundProviderCredentialSecurityState",
    "VERSION",
    "is_valid_at",
]


# ARTIFACT: tenant_inbound_provider_credential_security_authority.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P2
# AUTHORITY BOUNDARY: immutable historical credential-security evidence only; no current binding authority.
# TENANT POSTURE: tenant_id is mandatory and part of the fingerprinted identity.
# FAIL-CLOSED POSTURE: strict schema, UTC validity, four-state vocabulary, and digest validation.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
