"""Direct certificate for canonical recovery-contact authority.

TITLE: WILSY OS Recovery Contact Authority Direct Certificate
VERSION: v1.0.0-R10E9-RECOVERY-CONTACT-AUTHORITY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies explicit recovery-contact lifecycle truth without inferring
         verification from login email, MFA, membership, or account existence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_recovery_contact.py
COLLABORATION / OWNERSHIP: Deterministic unit evidence for recovery_contact.py;
                           no database, network, SMTP, auth, or password mutation.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10E9-RECOVERY-CONTACT-AUTHORITY-CERT — Certifies exact PENDING,
    VERIFIED, REVOKED transitions, revision progression, email normalization,
    verification-method evidence, strict hydration, timestamp invariants, and
    VERIFIED-only recovery eligibility.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic addresses only; no bearer or credential material.
TENANT BOUNDARY: Exact synthetic tenant/principal bindings are preserved.
AUTHORITY BOUNDARY: Domain lifecycle evidence only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusively financial.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.saas.auth.recovery_contact import (
    SCHEMA,
    RecoveryContactAuthority,
    RecoveryContactAuthorityError,
    RecoveryContactChannel,
    RecoveryContactStatus,
    RecoveryContactVerificationMethod,
)


NOW = datetime(2026, 9, 22, 18, 0, 0, tzinfo=timezone.utc)


def _pending() -> RecoveryContactAuthority:
    return RecoveryContactAuthority.pending(
        contact_id="WILSYRECOVERYCONTACT-1",
        tenant_id="TENANT-ONE",
        principal_id="principal-one",
        address=" Person@Example.COM ",
        created_at=NOW,
    )


def test_pending_contact_has_no_verification_authority() -> None:
    contact = _pending()
    assert contact.channel is RecoveryContactChannel.EMAIL
    assert contact.address == "person@example.com"
    assert contact.status is RecoveryContactStatus.PENDING
    assert contact.revision == 0
    assert contact.verified_at is None
    assert contact.verification_method is None
    assert contact.revoked_at is None
    with pytest.raises(RecoveryContactAuthorityError) as error:
        contact.require_verified(observed_at=NOW)
    assert error.value.code == "RECOVERY_CONTACT_NOT_VERIFIED"


def test_verification_is_explicit_revisioned_and_recovery_eligible() -> None:
    verified_at = NOW + timedelta(minutes=2)
    verified = _pending().verify(
        verified_at=verified_at,
        method=RecoveryContactVerificationMethod.EMAIL_CHALLENGE,
    )
    assert verified.status is RecoveryContactStatus.VERIFIED
    assert verified.revision == 1
    assert verified.verified_at == verified_at
    assert verified.verification_method is RecoveryContactVerificationMethod.EMAIL_CHALLENGE
    assert verified.revoked_at is None
    assert verified.require_verified(observed_at=verified_at) is verified


def test_legacy_migration_method_is_explicit_not_inferred() -> None:
    verified = _pending().verify(
        verified_at=NOW + timedelta(seconds=1),
        method=RecoveryContactVerificationMethod.LEGACY_EMAIL_VERIFIED_MIGRATION,
    )
    assert verified.verification_method is RecoveryContactVerificationMethod.LEGACY_EMAIL_VERIFIED_MIGRATION
    assert "emailVerified" not in verified.to_document()
    assert "mfa" not in repr(verified).lower()


def test_revoke_pending_is_terminal_without_fabricated_verification() -> None:
    revoked = _pending().revoke(revoked_at=NOW + timedelta(minutes=1))
    assert revoked.status is RecoveryContactStatus.REVOKED
    assert revoked.revision == 1
    assert revoked.verified_at is None
    assert revoked.verification_method is None
    assert revoked.revoked_at == NOW + timedelta(minutes=1)
    with pytest.raises(RecoveryContactAuthorityError) as error:
        revoked.require_verified(observed_at=NOW + timedelta(minutes=2))
    assert error.value.code == "RECOVERY_CONTACT_NOT_VERIFIED"


def test_revoke_verified_preserves_verification_evidence_and_advances_revision() -> None:
    verified = _pending().verify(
        verified_at=NOW + timedelta(minutes=1),
        method=RecoveryContactVerificationMethod.EMAIL_CHALLENGE,
    )
    revoked = verified.revoke(revoked_at=NOW + timedelta(minutes=3))
    assert revoked.status is RecoveryContactStatus.REVOKED
    assert revoked.revision == 2
    assert revoked.verified_at == verified.verified_at
    assert revoked.verification_method is verified.verification_method
    assert revoked.revoked_at == NOW + timedelta(minutes=3)


def test_repeated_or_out_of_order_transitions_fail_closed() -> None:
    verified = _pending().verify(
        verified_at=NOW + timedelta(minutes=1),
        method=RecoveryContactVerificationMethod.EMAIL_CHALLENGE,
    )
    with pytest.raises(RecoveryContactAuthorityError) as repeated:
        verified.verify(
            verified_at=NOW + timedelta(minutes=2),
            method=RecoveryContactVerificationMethod.EMAIL_CHALLENGE,
        )
    assert repeated.value.code == "RECOVERY_CONTACT_NOT_PENDING"

    revoked = verified.revoke(revoked_at=NOW + timedelta(minutes=3))
    with pytest.raises(RecoveryContactAuthorityError) as second_revoke:
        revoked.revoke(revoked_at=NOW + timedelta(minutes=4))
    assert second_revoke.value.code == "RECOVERY_CONTACT_ALREADY_REVOKED"

    with pytest.raises(RecoveryContactAuthorityError) as before_verified:
        verified.revoke(revoked_at=NOW)
    assert before_verified.value.code == "RECOVERY_CONTACT_REVOKED_BEFORE_CURRENT_STATE"


@pytest.mark.parametrize(
    "address",
    [
        "",
        "invalid",
        "@example.com",
        "person@",
        ".person@example.com",
        "person.@example.com",
        "person@.example.com",
        "person@example.com.",
        "person @example.com",
        "person@example .com",
        7,
    ],
)
def test_invalid_recovery_addresses_are_rejected(address: object) -> None:
    with pytest.raises(RecoveryContactAuthorityError) as error:
        RecoveryContactAuthority.pending(
            contact_id="WILSYRECOVERYCONTACT-1",
            tenant_id="TENANT-ONE",
            principal_id="principal-one",
            address=address,  # type: ignore[arg-type]
            created_at=NOW,
        )
    assert error.value.code == "RECOVERY_CONTACT_ADDRESS_INVALID"


def test_timestamps_must_be_timezone_aware_and_monotonic() -> None:
    naive = datetime(2026, 9, 22, 18, 0, 0)
    with pytest.raises(RecoveryContactAuthorityError) as created:
        RecoveryContactAuthority.pending(
            contact_id="WILSYRECOVERYCONTACT-1",
            tenant_id="TENANT-ONE",
            principal_id="principal-one",
            address="person@example.com",
            created_at=naive,
        )
    assert created.value.code == "RECOVERY_CONTACT_CREATED_AT_INVALID"

    with pytest.raises(RecoveryContactAuthorityError) as verify_before_create:
        _pending().verify(
            verified_at=NOW - timedelta(seconds=1),
            method=RecoveryContactVerificationMethod.EMAIL_CHALLENGE,
        )
    assert verify_before_create.value.code == "RECOVERY_CONTACT_VERIFIED_BEFORE_CREATED"


def test_document_round_trip_is_exact_and_strict() -> None:
    verified = _pending().verify(
        verified_at=NOW + timedelta(minutes=1),
        method=RecoveryContactVerificationMethod.EMAIL_CHALLENGE,
    )
    document = verified.to_document()
    assert document["schema"] == SCHEMA
    assert RecoveryContactAuthority.from_document(document) == verified

    missing = dict(document)
    missing.pop("address")
    with pytest.raises(RecoveryContactAuthorityError) as missing_error:
        RecoveryContactAuthority.from_document(missing)
    assert missing_error.value.code == "RECOVERY_CONTACT_DOCUMENT_SHAPE_INVALID"

    extra = dict(document)
    extra["emailVerified"] = True
    with pytest.raises(RecoveryContactAuthorityError) as extra_error:
        RecoveryContactAuthority.from_document(extra)
    assert extra_error.value.code == "RECOVERY_CONTACT_DOCUMENT_SHAPE_INVALID"


def test_persisted_contradictions_fail_closed() -> None:
    pending = _pending().to_document()

    contradictory = dict(pending)
    contradictory["status"] = "VERIFIED"
    contradictory["revision"] = 1
    with pytest.raises(RecoveryContactAuthorityError):
        RecoveryContactAuthority.from_document(contradictory)

    invalid_method = dict(pending)
    invalid_method["status"] = "VERIFIED"
    invalid_method["revision"] = 1
    invalid_method["verified_at"] = (NOW + timedelta(minutes=1)).isoformat()
    invalid_method["verification_method"] = "MFA_INFERRED"
    with pytest.raises(RecoveryContactAuthorityError) as error:
        RecoveryContactAuthority.from_document(invalid_method)
    assert error.value.code == "RECOVERY_CONTACT_DOCUMENT_INVALID"


def test_error_representation_is_code_only() -> None:
    with pytest.raises(RecoveryContactAuthorityError) as captured:
        RecoveryContactAuthority.pending(
            contact_id="WILSYRECOVERYCONTACT-1",
            tenant_id="TENANT-ONE",
            principal_id="principal-one",
            address="secret-address",
            created_at=NOW,
        )
    rendered = repr(captured.value)
    assert "secret-address" not in rendered
    assert "RECOVERY_CONTACT_ADDRESS_INVALID" in rendered


# ARTIFACT: tests/unit/test_recovery_contact.py
# VERSION: v1.0.0-R10E9-RECOVERY-CONTACT-AUTHORITY-CERT
# AUTHORITY BOUNDARY: deterministic recovery-contact lifecycle evidence only
# TENANT POSTURE: exact tenant/principal bindings; no cross-tenant inference
# FAIL-CLOSED POSTURE: only explicit VERIFIED evidence is recovery-eligible
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusively financial
# END OF WILSY OS SOVEREIGN ARTIFACT
