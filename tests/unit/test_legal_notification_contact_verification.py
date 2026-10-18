"""Direct unit certificate for Legal notification-contact verification.

TITLE: Legal Notification Contact Verification Unit Certificate
VERSION: v1.0.0-L8-8H7A-LEGAL-NOTIFICATION-CONTACT-VERIFICATION-UNIT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations Certification
EPITOME: Certify the pure H7A single-use Legal notification email-control
         verification domain without persistence, API, transport, recovery
         contact reuse, dispatch, delivery, AI, Court, or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_notification_contact_verification.py
COLLABORATION / OWNERSHIP: Exercises only the H7A pure domain contract.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0 establishes direct lifecycle, chronology, digest, schema,
           immutability, fingerprint, privacy, tenant and authority-boundary
           certification for H7A.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Uses synthetic digest inputs only. No real address,
                            credential, token, tenant secret, or delivery data.
TENANT BOUNDARY: Certifies explicit tenant scoping and forbidden pseudo-tenants.
AUTHORITY BOUNDARY: Pure verification capability tests only.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import hashlib

import pytest

from tools.eos.legal_operations.domain.legal_notification_contact_verification import (
    SCHEMA,
    VERSION,
    LegalNotificationContactChannel,
    LegalNotificationContactVerification,
    LegalNotificationContactVerificationError,
    LegalNotificationContactVerificationStatus,
)


ISSUED = datetime(2026, 10, 12, 18, 0, tzinfo=timezone.utc)
EXPIRES = ISSUED + timedelta(minutes=30)
ADDRESS_DIGEST = hashlib.sha3_512(b"synthetic-legal-address").hexdigest()
TOKEN_DIGEST = hashlib.sha3_512(b"synthetic-single-use-capability").hexdigest()


def _verification(
    **overrides: object,
) -> LegalNotificationContactVerification:
    """Build one valid ACTIVE synthetic H7A verification."""

    values: dict[str, object] = {
        "tenant_id": "tenant-legal-a",
        "verification_id": "legal-verification-1",
        "principal_id": "principal-1",
        "channel": LegalNotificationContactChannel.EMAIL,
        "address_digest": ADDRESS_DIGEST,
        "token_digest": TOKEN_DIGEST,
        "issued_at": ISSUED,
        "expires_at": EXPIRES,
    }
    values.update(overrides)
    return LegalNotificationContactVerification.issue(**values)  # type: ignore[arg-type]


def _assert_code(
    code: str,
    callback: object,
) -> None:
    """Require one stable H7A domain error code."""

    assert callable(callback)
    with pytest.raises(LegalNotificationContactVerificationError) as exc:
        callback()
    assert exc.value.code == code


def test_version_schema_channel_and_initial_status_are_exact() -> None:
    """Certify the closed H7A vocabulary and ACTIVE initial state."""

    value = _verification()

    assert VERSION == "v1.0.0-L8-8H7A-LEGAL-NOTIFICATION-CONTACT-VERIFICATION"
    assert SCHEMA == "WILSY-LEGAL-NOTIFICATION-CONTACT-VERIFICATION/V1"
    assert tuple(LegalNotificationContactChannel) == (
        LegalNotificationContactChannel.EMAIL,
    )
    assert value.status is LegalNotificationContactVerificationStatus.ACTIVE


def test_issue_is_digest_only_and_contains_no_raw_contact_or_token() -> None:
    """Certify the durable value contains only digest evidence."""

    value = _verification()
    payload = value.to_dict()
    rendered = repr(payload)

    assert payload["address_digest"] == ADDRESS_DIGEST
    assert payload["token_digest"] == TOKEN_DIGEST
    assert len(str(payload["address_digest"])) == 128
    assert len(str(payload["token_digest"])) == 128
    assert "synthetic-legal-address" not in rendered
    assert "synthetic-single-use-capability" not in rendered
    assert "email" not in payload
    assert "recipient_email" not in payload
    assert "address" not in payload
    assert "raw_token" not in payload


@pytest.mark.parametrize(
    ("tenant", "expected_code"),
    (
        ("default", "L8_8H7A_TENANT_REQUIRED"),
        ("global", "L8_8H7A_TENANT_REQUIRED"),
        ("global_root", "L8_8H7A_TENANT_REQUIRED"),
        ("root", "L8_8H7A_TENANT_REQUIRED"),
        ("master", "L8_8H7A_TENANT_REQUIRED"),
        ("*", "L8_8H7A_TENANT_ID_INVALID"),
    ),
)
def test_forbidden_pseudo_tenants_fail_closed(
    tenant: str,
    expected_code: str,
) -> None:
    """Certify pseudo-global or malformed wildcard tenant authority rejects."""

    _assert_code(
        expected_code,
        lambda: _verification(tenant_id=tenant),
    )


@pytest.mark.parametrize(
    ("field", "value", "code"),
    (
        ("verification_id", "", "L8_8H7A_VERIFICATION_ID_INVALID"),
        ("verification_id", " value", "L8_8H7A_VERIFICATION_ID_INVALID"),
        ("principal_id", "", "L8_8H7A_PRINCIPAL_ID_INVALID"),
        ("principal_id", "principal 1", "L8_8H7A_PRINCIPAL_ID_INVALID"),
        ("channel", "SMS", "L8_8H7A_CHANNEL_INVALID"),
        ("address_digest", "a" * 127, "L8_8H7A_ADDRESS_DIGEST_INVALID"),
        ("address_digest", "A" * 128, "L8_8H7A_ADDRESS_DIGEST_INVALID"),
        ("token_digest", "0" * 126, "L8_8H7A_TOKEN_DIGEST_INVALID"),
        ("token_digest", "G" * 128, "L8_8H7A_TOKEN_DIGEST_INVALID"),
    ),
)
def test_invalid_identity_channel_and_digest_values_reject(
    field: str,
    value: object,
    code: str,
) -> None:
    """Certify malformed authority inputs are never normalized into truth."""

    _assert_code(code, lambda: _verification(**{field: value}))


def test_expiry_must_be_strictly_after_issue() -> None:
    """Certify invalid capability chronology rejects."""

    _assert_code(
        "L8_8H7A_EXPIRY_INVALID",
        lambda: _verification(expires_at=ISSUED),
    )
    _assert_code(
        "L8_8H7A_EXPIRY_INVALID",
        lambda: _verification(expires_at=ISSUED - timedelta(microseconds=1)),
    )


def test_naive_datetimes_fail_closed() -> None:
    """Certify H7A never silently assumes a timezone."""

    naive = datetime(2026, 10, 12, 18, 0)

    _assert_code(
        "L8_8H7A_ISSUED_AT_INVALID",
        lambda: _verification(issued_at=naive),
    )
    _assert_code(
        "L8_8H7A_EXPIRES_AT_INVALID",
        lambda: _verification(expires_at=naive),
    )


def test_equivalent_aware_timezones_canonicalize_to_utc() -> None:
    """Certify timezone-aware inputs canonicalize deterministically."""

    plus_two = timezone(timedelta(hours=2))
    issued_local = datetime(2026, 10, 12, 20, 0, tzinfo=plus_two)
    expires_local = datetime(2026, 10, 12, 20, 30, tzinfo=plus_two)

    value = _verification(
        issued_at=issued_local,
        expires_at=expires_local,
    )

    assert value.issued_at == ISSUED
    assert value.expires_at == EXPIRES
    assert value.issued_at.tzinfo is timezone.utc
    assert value.expires_at.tzinfo is timezone.utc


def test_exact_round_trip_preserves_fingerprint() -> None:
    """Certify exact serialization hydration and integrity."""

    value = _verification()
    hydrated = LegalNotificationContactVerification.from_dict(value.to_dict())

    assert hydrated == value
    assert hydrated.fingerprint == value.fingerprint
    assert len(value.fingerprint) == 128


def test_schema_addition_and_omission_reject() -> None:
    """Certify exact persisted schema only."""

    extra = _verification().to_dict()
    extra["unexpected"] = "value"

    _assert_code(
        "L8_8H7A_SCHEMA_INVALID",
        lambda: LegalNotificationContactVerification.from_dict(extra),
    )

    missing = _verification().to_dict()
    del missing["token_digest"]

    _assert_code(
        "L8_8H7A_SCHEMA_INVALID",
        lambda: LegalNotificationContactVerification.from_dict(missing),
    )


def test_payload_corruption_fails_fingerprint_verification() -> None:
    """Certify fingerprint covers semantic identity and chronology."""

    for field, replacement in (
        ("tenant_id", "tenant-legal-b"),
        ("verification_id", "legal-verification-2"),
        ("principal_id", "principal-2"),
        ("address_digest", hashlib.sha3_512(b"other-address").hexdigest()),
        ("token_digest", hashlib.sha3_512(b"other-token").hexdigest()),
        (
            "expires_at",
            (EXPIRES + timedelta(minutes=1))
            .isoformat(timespec="microseconds")
            .replace("+00:00", "Z"),
        ),
    ):
        payload = _verification().to_dict()
        payload[field] = replacement

        _assert_code(
            "L8_8H7A_FINGERPRINT_MISMATCH",
            lambda payload=payload: LegalNotificationContactVerification.from_dict(
                payload
            ),
        )


def test_consume_is_immutable_single_use_and_re_fingerprinted() -> None:
    """Certify consume produces new immutable terminal evidence."""

    original = _verification()
    consumed_at = ISSUED + timedelta(minutes=1)
    consumed = original.consume(consumed_at)

    assert original.status is LegalNotificationContactVerificationStatus.ACTIVE
    assert original.consumed_at is None
    assert consumed.status is LegalNotificationContactVerificationStatus.CONSUMED
    assert consumed.consumed_at == consumed_at
    assert consumed.fingerprint != original.fingerprint
    assert LegalNotificationContactVerification.from_dict(
        consumed.to_dict()
    ) == consumed

    _assert_code(
        "L8_8H7A_VERIFICATION_NOT_ACTIVE",
        lambda: consumed.consume(consumed_at + timedelta(seconds=1)),
    )


def test_revoke_is_immutable_terminal_and_re_fingerprinted() -> None:
    """Certify revoke terminates future verification use only."""

    original = _verification()
    revoked = original.revoke(ISSUED + timedelta(minutes=2))

    assert original.status is LegalNotificationContactVerificationStatus.ACTIVE
    assert revoked.status is LegalNotificationContactVerificationStatus.REVOKED
    assert revoked.fingerprint != original.fingerprint
    assert LegalNotificationContactVerification.from_dict(
        revoked.to_dict()
    ) == revoked

    _assert_code(
        "L8_8H7A_VERIFICATION_NOT_ACTIVE",
        lambda: revoked.assert_usable_at(ISSUED + timedelta(minutes=3)),
    )


def test_expire_requires_boundary_and_re_fingerprints() -> None:
    """Certify explicit expiry is allowed only at or after expires_at."""

    original = _verification()

    _assert_code(
        "L8_8H7A_EXPIRY_NOT_REACHED",
        lambda: original.expire(EXPIRES - timedelta(microseconds=1)),
    )

    expired = original.expire(EXPIRES)

    assert original.status is LegalNotificationContactVerificationStatus.ACTIVE
    assert expired.status is LegalNotificationContactVerificationStatus.EXPIRED
    assert expired.expired_at == EXPIRES
    assert expired.fingerprint != original.fingerprint
    assert LegalNotificationContactVerification.from_dict(
        expired.to_dict()
    ) == expired


def test_active_usability_boundaries_are_exact() -> None:
    """Certify issued_at is inclusive and expires_at is exclusive."""

    value = _verification()

    value.assert_usable_at(ISSUED)
    value.assert_usable_at(EXPIRES - timedelta(microseconds=1))

    _assert_code(
        "L8_8H7A_VERIFICATION_NOT_YET_VALID",
        lambda: value.assert_usable_at(ISSUED - timedelta(microseconds=1)),
    )
    _assert_code(
        "L8_8H7A_VERIFICATION_EXPIRED",
        lambda: value.assert_usable_at(EXPIRES),
    )


def test_terminal_states_are_mutually_exclusive() -> None:
    """Certify persisted contradictory terminal truth fails closed."""

    base = _verification().to_dict()
    base["fingerprint"] = ""
    base["consumed_at"] = (
        ISSUED + timedelta(minutes=1)
    ).isoformat(timespec="microseconds").replace("+00:00", "Z")
    base["revoked_at"] = (
        ISSUED + timedelta(minutes=2)
    ).isoformat(timespec="microseconds").replace("+00:00", "Z")

    _assert_code(
        "L8_8H7A_TERMINAL_STATE_CONFLICT",
        lambda: LegalNotificationContactVerification.from_dict(base),
    )


def test_terminal_chronology_rejects_impossible_states() -> None:
    """Certify terminal timestamps cannot contradict issuance/expiry."""

    _assert_code(
        "L8_8H7A_CONSUMED_AT_INVALID",
        lambda: LegalNotificationContactVerification(
            tenant_id="tenant-legal-a",
            verification_id="verify-consume-bad",
            principal_id="principal-1",
            channel="EMAIL",
            address_digest=ADDRESS_DIGEST,
            token_digest=TOKEN_DIGEST,
            issued_at=ISSUED,
            expires_at=EXPIRES,
            consumed_at=EXPIRES,
        ),
    )

    _assert_code(
        "L8_8H7A_REVOKED_AT_INVALID",
        lambda: LegalNotificationContactVerification(
            tenant_id="tenant-legal-a",
            verification_id="verify-revoke-bad",
            principal_id="principal-1",
            channel="EMAIL",
            address_digest=ADDRESS_DIGEST,
            token_digest=TOKEN_DIGEST,
            issued_at=ISSUED,
            expires_at=EXPIRES,
            revoked_at=ISSUED - timedelta(microseconds=1),
        ),
    )

    _assert_code(
        "L8_8H7A_EXPIRED_AT_INVALID",
        lambda: LegalNotificationContactVerification(
            tenant_id="tenant-legal-a",
            verification_id="verify-expire-bad",
            principal_id="principal-1",
            channel="EMAIL",
            address_digest=ADDRESS_DIGEST,
            token_digest=TOKEN_DIGEST,
            issued_at=ISSUED,
            expires_at=EXPIRES,
            expired_at=EXPIRES - timedelta(microseconds=1),
        ),
    )


def test_domain_is_frozen() -> None:
    """Certify callers cannot mutate established verification evidence."""

    value = _verification()

    with pytest.raises(FrozenInstanceError):
        value.principal_id = "principal-2"  # type: ignore[misc]


def test_public_payload_fields_are_exact() -> None:
    """Certify no accidental address, transport, delivery or authority fields."""

    assert set(_verification().to_dict()) == {
        "schema",
        "verification_version",
        "tenant_id",
        "verification_id",
        "principal_id",
        "channel",
        "address_digest",
        "token_digest",
        "issued_at",
        "expires_at",
        "consumed_at",
        "expired_at",
        "revoked_at",
        "fingerprint",
    }


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_notification_contact_verification.py
# VERSION: v1.0.0-L8-8H7A-LEGAL-NOTIFICATION-CONTACT-VERIFICATION-UNIT
# AUTHORITY BOUNDARY: direct H7A pure-domain certification only
# TENANT POSTURE: synthetic exact-tenant and forbidden-pseudo-tenant coverage
# FAIL-CLOSED POSTURE: malformed, corrupt, contradictory and replay state rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
