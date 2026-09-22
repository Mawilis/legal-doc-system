"""Direct certificate for WILSY OS recovery-contact verification state.

TITLE: WILSY OS Recovery Contact Verification Domain Direct Certificate
VERSION: v1.0.1-R10E47-RECOVERY-CONTACT-VERIFICATION-DOMAIN-TYPE-CLOSURE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies immutable digest-only email-control verification lifecycle,
         exact tenant/principal binding, single-use transitions, strict UTC,
         and secret-free hydration.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_recovery_contact_verification.py
COLLABORATION / OWNERSHIP: Exercises password_recovery_contact_verification.py
                           only; no Mongo, delivery, HTTP, or credential mutation.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.1-R10E47-RECOVERY-CONTACT-VERIFICATION-DOMAIN-TYPE-CLOSURE introduces
           issuance, consume/revoke/expire, replay, expiry-boundary, malformed
           identifier/digest/time, contradictory terminal-state, serialization,
           hydration, and raw-secret exclusion evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic digests only; raw email/token excluded.
TENANT BOUNDARY: Exact tenant/principal binding is asserted.
AUTHORITY BOUNDARY: Domain test evidence only; no verified-contact creation,
                    password reset, session, JWT, MFA, HTTP, or delivery.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from tools.eos.saas.auth.password_recovery_contact_verification import (
    RecoveryContactVerification,
    RecoveryContactVerificationError,
    RecoveryContactVerificationStatus,
    SCHEMA,
)

ISSUED = datetime(2026, 9, 22, 18, 0, tzinfo=timezone.utc)
EXPIRES = ISSUED + timedelta(minutes=30)
ADDRESS_DIGEST = hashlib.sha3_512(b"verified.user@example.com").hexdigest()
TOKEN_DIGEST = hashlib.sha3_512(b"synthetic-verification-token").hexdigest()


def _active() -> RecoveryContactVerification:
    return RecoveryContactVerification.issue(
        verification_id="WILSYRECOVERYVERIFY-CERT-1",
        tenant_id="WILSY-TENANT-VERIFY-CERT",
        principal_id="WILSY-PRINCIPAL-VERIFY-CERT",
        address_digest=ADDRESS_DIGEST,
        token_digest=TOKEN_DIGEST,
        issued_at=ISSUED,
        expires_at=EXPIRES,
    )


def test_issue_produces_exact_active_digest_only_state() -> None:
    value = _active()

    assert value.status is RecoveryContactVerificationStatus.ACTIVE
    assert value.tenant_id == "WILSY-TENANT-VERIFY-CERT"
    assert value.principal_id == "WILSY-PRINCIPAL-VERIFY-CERT"
    assert value.address_digest == ADDRESS_DIGEST
    assert value.token_digest == TOKEN_DIGEST
    assert value.consumed_at is None
    assert value.expired_at is None
    assert value.revoked_at is None


def test_consume_is_single_use_and_pre_expiry_only() -> None:
    active = _active()
    consumed_at = ISSUED + timedelta(minutes=5)

    consumed = active.consume(consumed_at)

    assert consumed.status is RecoveryContactVerificationStatus.CONSUMED
    assert consumed.consumed_at == consumed_at
    assert active.status is RecoveryContactVerificationStatus.ACTIVE

    with pytest.raises(RecoveryContactVerificationError) as replay:
        consumed.consume(consumed_at + timedelta(seconds=1))
    assert str(replay.value) == "VERIFICATION_NOT_ACTIVE"


def test_revoke_is_terminal_and_pre_expiry_only() -> None:
    revoked = _active().revoke(ISSUED + timedelta(minutes=10))

    assert revoked.status is RecoveryContactVerificationStatus.REVOKED
    assert revoked.revoked_at == ISSUED + timedelta(minutes=10)

    with pytest.raises(RecoveryContactVerificationError) as replay:
        revoked.revoke(ISSUED + timedelta(minutes=11))
    assert str(replay.value) == "VERIFICATION_NOT_ACTIVE"


def test_expire_requires_boundary_and_becomes_terminal() -> None:
    active = _active()

    with pytest.raises(RecoveryContactVerificationError) as early:
        active.expire(EXPIRES - timedelta(microseconds=1))
    assert str(early.value) == "EXPIRY_BOUNDARY_NOT_REACHED"

    expired = active.expire(EXPIRES)
    assert expired.status is RecoveryContactVerificationStatus.EXPIRED
    assert expired.expired_at == EXPIRES

    with pytest.raises(RecoveryContactVerificationError) as replay:
        expired.expire(EXPIRES + timedelta(seconds=1))
    assert str(replay.value) == "VERIFICATION_NOT_ACTIVE"


def test_assert_usable_rejects_before_issue_and_at_expiry() -> None:
    active = _active()

    with pytest.raises(RecoveryContactVerificationError) as before:
        active.assert_usable_at(ISSUED - timedelta(microseconds=1))
    assert str(before.value) == "OBSERVED_AT_BEFORE_ISSUANCE"

    active.assert_usable_at(EXPIRES - timedelta(microseconds=1))

    with pytest.raises(RecoveryContactVerificationError) as expired:
        active.assert_usable_at(EXPIRES)
    assert str(expired.value) == "VERIFICATION_EXPIRED"


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("verification_id", "", "VERIFICATION_ID_INVALID"),
        ("tenant_id", " tenant", "TENANT_ID_INVALID"),
        ("principal_id", "principal\n", "PRINCIPAL_ID_INVALID"),
        ("address_digest", "0" * 127, "ADDRESS_DIGEST_INVALID"),
        ("address_digest", "G" * 128, "ADDRESS_DIGEST_INVALID"),
        ("token_digest", "0" * 127, "TOKEN_DIGEST_INVALID"),
        ("token_digest", "A" * 128, "TOKEN_DIGEST_INVALID"),
        ("issued_at", datetime(2026, 9, 22, 18, 0), "ISSUED_AT_INVALID"),
    ],
)
def test_malformed_immutable_fields_fail_closed(field, value, code) -> None:
    kwargs: dict[str, Any] = dict(
        verification_id="WILSYRECOVERYVERIFY-CERT-1",
        tenant_id="WILSY-TENANT-VERIFY-CERT",
        principal_id="WILSY-PRINCIPAL-VERIFY-CERT",
        address_digest=ADDRESS_DIGEST,
        token_digest=TOKEN_DIGEST,
        issued_at=ISSUED,
        expires_at=EXPIRES,
    )
    kwargs[field] = value

    with pytest.raises(RecoveryContactVerificationError) as captured:
        RecoveryContactVerification.issue(**kwargs)

    assert str(captured.value) == code


def test_expiry_must_follow_issuance() -> None:
    with pytest.raises(RecoveryContactVerificationError) as captured:
        RecoveryContactVerification.issue(
            verification_id="WILSYRECOVERYVERIFY-CERT-1",
            tenant_id="WILSY-TENANT-VERIFY-CERT",
            principal_id="WILSY-PRINCIPAL-VERIFY-CERT",
            address_digest=ADDRESS_DIGEST,
            token_digest=TOKEN_DIGEST,
            issued_at=ISSUED,
            expires_at=ISSUED,
        )
    assert str(captured.value) == "EXPIRY_NOT_AFTER_ISSUANCE"


def test_serialization_contains_no_raw_email_or_token_fields() -> None:
    document = _active().to_document()

    assert document["schema"] == SCHEMA
    assert set(document) == {
        "schema",
        "verification_id",
        "tenant_id",
        "principal_id",
        "address_digest",
        "token_digest",
        "issued_at",
        "expires_at",
        "status",
        "consumed_at",
        "expired_at",
        "revoked_at",
    }
    assert all("email" not in key.lower() for key in document)
    assert "raw_token" not in document
    assert "token" not in document
    assert document["token_digest"] == TOKEN_DIGEST


def test_round_trip_hydration_preserves_exact_state() -> None:
    active = _active()
    assert RecoveryContactVerification.from_document(active.to_document()) == active

    consumed = active.consume(ISSUED + timedelta(minutes=1))
    assert RecoveryContactVerification.from_document(consumed.to_document()) == consumed


def test_hydration_rejects_unknown_or_raw_secret_fields() -> None:
    document = _active().to_document()
    document["email"] = "verified.user@example.com"

    with pytest.raises(RecoveryContactVerificationError) as captured:
        RecoveryContactVerification.from_document(document)

    assert str(captured.value) == "PERSISTED_VERIFICATION_SHAPE_INVALID"


def test_contradictory_terminal_state_is_rejected() -> None:
    document = _active().to_document()
    document["status"] = "CONSUMED"
    document["consumed_at"] = (ISSUED + timedelta(minutes=1)).isoformat()
    document["revoked_at"] = (ISSUED + timedelta(minutes=2)).isoformat()

    with pytest.raises(RecoveryContactVerificationError) as captured:
        RecoveryContactVerification.from_document(document)

    assert str(captured.value) == "MULTIPLE_TERMINAL_TIMESTAMPS"


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_password_recovery_contact_verification.py
# VERSION: v1.0.1-R10E47-RECOVERY-CONTACT-VERIFICATION-DOMAIN-TYPE-CLOSURE
# AUTHORITY BOUNDARY: immutable verification-domain test evidence only
# TENANT POSTURE: exact tenant/principal/address/token digest binding certified
# FAIL-CLOSED POSTURE: malformed, replayed, expired, revoked state rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
