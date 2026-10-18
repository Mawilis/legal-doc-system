"""Direct unit certificate for verified Legal notification-contact authority.

TITLE: Verified Legal Notification Contact Unit Certificate
VERSION: v1.0.0-L8-8H7B-VERIFIED-LEGAL-NOTIFICATION-CONTACT-UNIT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations Certification
EPITOME: Certify H7B immutable verified Legal notification-contact authority,
         exact H7A consumed-verification provenance, lifecycle, chronology,
         privacy, tenant isolation, deterministic integrity, and authority
         boundaries without persistence, API, transport, dispatch, or delivery.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_verified_notification_contact.py
COLLABORATION / OWNERSHIP: Exercises only H7A-to-H7B pure-domain authority
                           composition. It creates no registry/API/service truth.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0 establishes direct H7B authority/provenance, immutable revoke,
           corruption rejection, chronology, schema, digest-only privacy,
           pseudo-tenant rejection, and no-dispatch/no-delivery certification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic digest evidence only; no real contact,
                            token, credential, provider, or delivery material.
TENANT BOUNDARY: Exact explicit tenant/principal provenance only.
AUTHORITY BOUNDARY: Verified Legal notification-contact authority tests only.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_notification_contact_verification import (
    LegalNotificationContactChannel,
    LegalNotificationContactVerification,
)
from tools.eos.legal_operations.domain.legal_verified_notification_contact import (
    SCHEMA,
    VERSION,
    VerifiedLegalNotificationContact,
    VerifiedLegalNotificationContactError,
    VerifiedLegalNotificationContactStatus,
)


ISSUED = datetime(2026, 10, 12, 18, 0, tzinfo=timezone.utc)
EXPIRES = ISSUED + timedelta(minutes=30)
CONSUMED = ISSUED + timedelta(minutes=5)
VERIFIED = CONSUMED

ADDRESS_DIGEST = hashlib.sha3_512(b"synthetic-legal-contact").hexdigest()
TOKEN_DIGEST = hashlib.sha3_512(b"synthetic-verification-token").hexdigest()


def _active_verification() -> LegalNotificationContactVerification:
    """Build one valid ACTIVE H7A capability."""

    return LegalNotificationContactVerification.issue(
        tenant_id="tenant-legal-a",
        verification_id="legal-verification-1",
        principal_id="principal-1",
        channel=LegalNotificationContactChannel.EMAIL,
        address_digest=ADDRESS_DIGEST,
        token_digest=TOKEN_DIGEST,
        issued_at=ISSUED,
        expires_at=EXPIRES,
    )


def _consumed_verification() -> LegalNotificationContactVerification:
    """Build one valid CONSUMED H7A capability."""

    return _active_verification().consume(CONSUMED)


def _contact(
    **overrides: object,
) -> VerifiedLegalNotificationContact:
    """Build one valid ACTIVE H7B authority from consumed H7A provenance."""

    verification = _consumed_verification()
    contact_id = str(overrides.pop("contact_id", "legal-contact-1"))
    verified_at = overrides.pop("verified_at", VERIFIED)

    if overrides:
        raise AssertionError(f"unsupported helper override: {sorted(overrides)}")

    return VerifiedLegalNotificationContact.from_consumed_verification(
        contact_id=contact_id,
        verification=verification,
        verified_at=verified_at,  # type: ignore[arg-type]
    )


def _assert_code(code: str, callback: Any) -> None:
    """Require one exact stable H7B fail-closed code."""

    with pytest.raises(VerifiedLegalNotificationContactError) as exc:
        callback()
    assert exc.value.code == code


def test_version_schema_and_initial_status_are_exact() -> None:
    """Certify closed H7B schema/version and initial ACTIVE lifecycle."""

    value = _contact()

    assert VERSION == "v1.0.0-L8-8H7B-VERIFIED-LEGAL-NOTIFICATION-CONTACT"
    assert SCHEMA == "WILSY-VERIFIED-LEGAL-NOTIFICATION-CONTACT/V1"
    assert value.status is VerifiedLegalNotificationContactStatus.ACTIVE


def test_active_h7a_cannot_create_verified_contact_authority() -> None:
    """Certify verification capability is not itself verified-contact authority."""

    _assert_code(
        "L8_8H7B_VERIFICATION_NOT_CONSUMED",
        lambda: VerifiedLegalNotificationContact.from_consumed_verification(
            contact_id="legal-contact-1",
            verification=_active_verification(),
            verified_at=VERIFIED,
        ),
    )


def test_consumed_h7a_provenance_is_bound_exactly() -> None:
    """Certify H7B copies exact consumed H7A authority provenance."""

    verification = _consumed_verification()

    contact = VerifiedLegalNotificationContact.from_consumed_verification(
        contact_id="legal-contact-1",
        verification=verification,
        verified_at=VERIFIED,
    )

    assert contact.tenant_id == verification.tenant_id
    assert contact.principal_id == verification.principal_id
    assert contact.channel == verification.channel
    assert contact.address_digest == verification.address_digest
    assert contact.verification_id == verification.verification_id
    assert contact.verification_fingerprint == verification.fingerprint
    assert contact.verification_consumed_at == verification.consumed_at
    assert contact.verification_expires_at == verification.expires_at


def test_verified_contact_is_digest_only() -> None:
    """Certify raw address/token/transport data cannot appear in H7B payload."""

    payload = _contact().to_dict()
    rendered = repr(payload)

    assert "synthetic-legal-contact" not in rendered
    assert "synthetic-verification-token" not in rendered
    assert payload["address_digest"] == ADDRESS_DIGEST

    forbidden = {
        "email",
        "recipient_email",
        "raw_token",
        "delivery_status",
        "provider_message_id",
        "transport",
        "dispatch_id",
    }
    assert forbidden.isdisjoint(payload)


@pytest.mark.parametrize(
    ("tenant", "expected"),
    (
        ("default", "L8_8H7B_TENANT_REQUIRED"),
        ("global", "L8_8H7B_TENANT_REQUIRED"),
        ("global_root", "L8_8H7B_TENANT_REQUIRED"),
        ("root", "L8_8H7B_TENANT_REQUIRED"),
        ("master", "L8_8H7B_TENANT_REQUIRED"),
        ("*", "L8_8H7B_TENANT_ID_INVALID"),
    ),
)
def test_pseudo_or_wildcard_tenants_fail_closed(
    tenant: str,
    expected: str,
) -> None:
    """Certify global/pseudo/wildcard tenant authority cannot hydrate."""

    payload = _contact().to_dict()
    payload["tenant_id"] = tenant
    payload["fingerprint"] = ""

    _assert_code(
        expected,
        lambda: VerifiedLegalNotificationContact.from_dict(payload),
    )


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    (
        ("contact_id", "", "L8_8H7B_CONTACT_ID_INVALID"),
        ("contact_id", " contact-1", "L8_8H7B_CONTACT_ID_INVALID"),
        ("principal_id", "", "L8_8H7B_PRINCIPAL_ID_INVALID"),
        ("principal_id", "principal 1", "L8_8H7B_PRINCIPAL_ID_INVALID"),
        ("channel", "SMS", "L8_8H7B_CHANNEL_INVALID"),
        ("address_digest", "a" * 127, "L8_8H7B_ADDRESS_DIGEST_INVALID"),
        (
            "verification_fingerprint",
            "A" * 128,
            "L8_8H7B_VERIFICATION_FINGERPRINT_INVALID",
        ),
    ),
)
def test_invalid_identity_channel_and_digest_values_reject(
    field: str,
    value: object,
    expected: str,
) -> None:
    """Certify malformed authority values cannot be normalized into truth."""

    payload = _contact().to_dict()
    payload[field] = value
    payload["fingerprint"] = ""

    _assert_code(
        expected,
        lambda: VerifiedLegalNotificationContact.from_dict(payload),
    )


def test_verification_consumption_must_precede_verification_expiry() -> None:
    """Certify consumed provenance cannot occur at/after capability expiry."""

    payload = _contact().to_dict()
    payload["verification_consumed_at"] = EXPIRES.isoformat().replace("+00:00", "Z")
    payload["fingerprint"] = ""

    _assert_code(
        "L8_8H7B_VERIFICATION_CHRONOLOGY_INVALID",
        lambda: VerifiedLegalNotificationContact.from_dict(payload),
    )


def test_verified_at_cannot_predate_h7a_consumption() -> None:
    """Certify contact authority cannot precede proof consumption."""

    payload = _contact().to_dict()
    payload["verified_at"] = (
        CONSUMED - timedelta(microseconds=1)
    ).isoformat().replace("+00:00", "Z")
    payload["fingerprint"] = ""

    _assert_code(
        "L8_8H7B_VERIFIED_AT_INVALID",
        lambda: VerifiedLegalNotificationContact.from_dict(payload),
    )


def test_revocation_cannot_predate_verified_authority() -> None:
    """Certify H7B lifecycle chronology fails closed."""

    payload = _contact().to_dict()
    payload["revoked_at"] = (
        VERIFIED - timedelta(microseconds=1)
    ).isoformat().replace("+00:00", "Z")
    payload["fingerprint"] = ""

    _assert_code(
        "L8_8H7B_REVOKED_AT_INVALID",
        lambda: VerifiedLegalNotificationContact.from_dict(payload),
    )


def test_exact_roundtrip_preserves_integrity() -> None:
    """Certify exact hydration and deterministic SHA3-512 fingerprint."""

    value = _contact()
    hydrated = VerifiedLegalNotificationContact.from_dict(value.to_dict())

    assert hydrated == value
    assert hydrated.fingerprint == value.fingerprint
    assert len(value.fingerprint) == 128


def test_schema_addition_and_omission_reject() -> None:
    """Certify only the exact H7B persisted schema is accepted."""

    extra = _contact().to_dict()
    extra["unexpected"] = "value"

    _assert_code(
        "L8_8H7B_SCHEMA_INVALID",
        lambda: VerifiedLegalNotificationContact.from_dict(extra),
    )

    missing = _contact().to_dict()
    del missing["address_digest"]

    _assert_code(
        "L8_8H7B_SCHEMA_INVALID",
        lambda: VerifiedLegalNotificationContact.from_dict(missing),
    )


@pytest.mark.parametrize(
    ("field", "replacement"),
    (
        ("tenant_id", "tenant-legal-b"),
        ("contact_id", "legal-contact-2"),
        ("principal_id", "principal-2"),
        ("address_digest", hashlib.sha3_512(b"other-address").hexdigest()),
        ("verification_id", "legal-verification-2"),
        (
            "verification_fingerprint",
            hashlib.sha3_512(b"other-verification").hexdigest(),
        ),
    ),
)
def test_semantic_payload_corruption_rejects(
    field: str,
    replacement: object,
) -> None:
    """Certify H7B fingerprint covers exact semantic authority payload."""

    payload = _contact().to_dict()
    payload[field] = replacement

    _assert_code(
        "L8_8H7B_FINGERPRINT_MISMATCH",
        lambda: VerifiedLegalNotificationContact.from_dict(payload),
    )


def test_revoke_is_immutable_and_re_fingerprinted() -> None:
    """Certify revoke creates new terminal evidence without mutating original."""

    original = _contact()
    revoked_at = VERIFIED + timedelta(minutes=1)
    revoked = original.revoke(revoked_at)

    assert original.status is VerifiedLegalNotificationContactStatus.ACTIVE
    assert original.revoked_at is None

    assert revoked.status is VerifiedLegalNotificationContactStatus.REVOKED
    assert revoked.revoked_at == revoked_at
    assert revoked.fingerprint != original.fingerprint

    assert VerifiedLegalNotificationContact.from_dict(
        revoked.to_dict()
    ) == revoked


def test_revocation_replay_fails_closed() -> None:
    """Certify revoked authority cannot be revoked a second time."""

    revoked = _contact().revoke(VERIFIED + timedelta(minutes=1))

    _assert_code(
        "L8_8H7B_CONTACT_NOT_ACTIVE",
        lambda: revoked.revoke(VERIFIED + timedelta(minutes=2)),
    )


def test_domain_is_frozen() -> None:
    """Certify callers cannot mutate established H7B authority."""

    value = _contact()

    with pytest.raises(FrozenInstanceError):
        value.principal_id = "principal-2"  # type: ignore[misc]


def test_public_payload_fields_are_exact() -> None:
    """Certify no accidental transport/delivery/financial fields exist."""

    assert set(_contact().to_dict()) == {
        "schema",
        "contact_version",
        "tenant_id",
        "contact_id",
        "principal_id",
        "channel",
        "address_digest",
        "verification_id",
        "verification_fingerprint",
        "verification_consumed_at",
        "verification_expires_at",
        "verified_at",
        "revoked_at",
        "fingerprint",
    }


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_verified_notification_contact.py
# VERSION: v1.0.0-L8-8H7B-VERIFIED-LEGAL-NOTIFICATION-CONTACT-UNIT
# AUTHORITY BOUNDARY: direct H7B pure-domain certification only
# TENANT POSTURE: exact synthetic tenant/principal/provenance coverage
# FAIL-CLOSED POSTURE: malformed, corrupt, contradictory, replayed authority rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
