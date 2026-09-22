"""Direct certificate for recovery-contact verification challenge state.

TITLE: WILSY OS Recovery Contact Verification Domain Certificate
VERSION: v1.0.0-R10E12-RECOVERY-CONTACT-VERIFICATION-DOMAIN-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies digest-only email-possession challenge lifecycle semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_recovery_contact_verification.py
COLLABORATION / OWNERSHIP: Deterministic unit evidence for the R10E12 domain only.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10E12-RECOVERY-CONTACT-VERIFICATION-DOMAIN-CERT — Certifies issuance,
    exact binding, digest validation, consume/expire/revoke transitions, replay
    rejection, strict hydration, and raw-token exclusion.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic digest/address only; no raw challenge is persisted.
TENANT BOUNDARY: Exact tenant/principal/contact/address binding.
AUTHORITY BOUNDARY: Domain lifecycle evidence only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusively financial.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.saas.auth.recovery_contact_verification import (
    SCHEMA,
    RecoveryContactVerificationChallenge,
    RecoveryContactVerificationError,
    RecoveryContactVerificationStatus,
)


NOW = datetime(2026, 9, 22, 19, 0, 0, tzinfo=timezone.utc)
RAW = "synthetic-contact-verification-value-0123456789"
DIGEST = hashlib.sha3_512(RAW.encode("utf-8")).hexdigest()


def _active() -> RecoveryContactVerificationChallenge:
    return RecoveryContactVerificationChallenge.issue(
        challenge_id="verification-one",
        tenant_id="tenant-one",
        principal_id="principal-one",
        contact_id="contact-one",
        address=" Person@Example.COM ",
        token_digest=DIGEST,
        issued_at=NOW,
        expires_at=NOW + timedelta(minutes=15),
    )


def test_issue_normalizes_address_and_keeps_digest_only() -> None:
    challenge = _active()
    assert challenge.address == "person@example.com"
    assert challenge.status is RecoveryContactVerificationStatus.ACTIVE
    assert challenge.token_digest == DIGEST
    assert RAW not in repr(challenge)
    assert "raw_token" not in challenge.to_document()


def test_consume_before_expiry_is_single_terminal_transition() -> None:
    consumed = _active().consume(NOW + timedelta(minutes=3))
    assert consumed.status is RecoveryContactVerificationStatus.CONSUMED
    assert consumed.consumed_at == NOW + timedelta(minutes=3)
    with pytest.raises(RecoveryContactVerificationError) as replay:
        consumed.consume(NOW + timedelta(minutes=4))
    assert replay.value.code == "RECOVERY_CONTACT_VERIFICATION_NOT_ACTIVE"


def test_expire_only_at_or_after_boundary() -> None:
    challenge = _active()
    with pytest.raises(RecoveryContactVerificationError) as early:
        challenge.expire(NOW + timedelta(minutes=14))
    assert early.value.code == "RECOVERY_CONTACT_VERIFICATION_EXPIRY_BOUNDARY_NOT_REACHED"
    expired = challenge.expire(NOW + timedelta(minutes=15))
    assert expired.status is RecoveryContactVerificationStatus.EXPIRED


def test_revoke_before_expiry_is_terminal() -> None:
    revoked = _active().revoke(NOW + timedelta(minutes=2))
    assert revoked.status is RecoveryContactVerificationStatus.REVOKED
    assert revoked.revoked_at == NOW + timedelta(minutes=2)
    with pytest.raises(RecoveryContactVerificationError):
        revoked.consume(NOW + timedelta(minutes=3))


@pytest.mark.parametrize(
    "digest",
    [
        "",
        "a" * 127,
        "A" * 128,
        "g" * 128,
        7,
    ],
)
def test_invalid_digests_are_rejected(digest: object) -> None:
    with pytest.raises(RecoveryContactVerificationError) as error:
        RecoveryContactVerificationChallenge.issue(
            challenge_id="verification-one",
            tenant_id="tenant-one",
            principal_id="principal-one",
            contact_id="contact-one",
            address="person@example.com",
            token_digest=digest,  # type: ignore[arg-type]
            issued_at=NOW,
            expires_at=NOW + timedelta(minutes=15),
        )
    assert error.value.code == "RECOVERY_CONTACT_VERIFICATION_DIGEST_INVALID"


def test_consume_at_expiry_boundary_rejects() -> None:
    with pytest.raises(RecoveryContactVerificationError) as error:
        _active().consume(NOW + timedelta(minutes=15))
    assert error.value.code == "RECOVERY_CONTACT_VERIFICATION_EXPIRED"


def test_document_round_trip_and_shape_are_strict() -> None:
    consumed = _active().consume(NOW + timedelta(minutes=1))
    document = consumed.to_document()
    assert document["schema"] == SCHEMA
    assert RecoveryContactVerificationChallenge.from_document(document) == consumed

    extra = dict(document)
    extra["recovery_token"] = RAW
    with pytest.raises(RecoveryContactVerificationError) as error:
        RecoveryContactVerificationChallenge.from_document(extra)
    assert error.value.code == "RECOVERY_CONTACT_VERIFICATION_DOCUMENT_SHAPE_INVALID"


def test_contradictory_status_timestamps_fail_closed() -> None:
    document = _active().to_document()
    document["status"] = "CONSUMED"
    with pytest.raises(RecoveryContactVerificationError) as error:
        RecoveryContactVerificationChallenge.from_document(document)
    assert error.value.code == "RECOVERY_CONTACT_VERIFICATION_STATUS_TIMESTAMP_MISMATCH"


def test_error_repr_is_code_only() -> None:
    with pytest.raises(RecoveryContactVerificationError) as captured:
        RecoveryContactVerificationChallenge.issue(
            challenge_id="verification-one",
            tenant_id="tenant-one",
            principal_id="principal-one",
            contact_id="contact-one",
            address="secret-address",
            token_digest=DIGEST,
            issued_at=NOW,
            expires_at=NOW + timedelta(minutes=15),
        )
    assert "secret-address" not in repr(captured.value)


# ARTIFACT: tests/unit/test_recovery_contact_verification.py
# VERSION: v1.0.0-R10E12-RECOVERY-CONTACT-VERIFICATION-DOMAIN-CERT
# AUTHORITY BOUNDARY: deterministic verification-challenge lifecycle evidence only
# TENANT POSTURE: exact tenant/principal/contact/address binding
# FAIL-CLOSED POSTURE: malformed, replayed, expired, revoked, and contradictory challenge state rejects
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusively financial
# END OF WILSY OS SOVEREIGN ARTIFACT
