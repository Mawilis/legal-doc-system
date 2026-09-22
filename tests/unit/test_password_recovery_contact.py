"""Direct certificate for verified password-recovery contact authority.

TITLE: WILSY OS Verified Recovery Contact Domain Certificate
VERSION: v1.0.0-R10E5-VERIFIED-RECOVERY-CONTACT-DOMAIN-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies digest-only tenant/principal recovery-contact authority,
         lifecycle integrity, strict hydration, and raw-address exclusion.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_recovery_contact.py
COLLABORATION / OWNERSHIP: Exercises R10E1 only; no Mongo, mail, HTTP, password,
                           token, or authentication runtime is invoked.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10E5-VERIFIED-RECOVERY-CONTACT-DOMAIN-CERT introduces direct
           issue/revoke/hydration/corruption/privacy/tenant-binding evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic SHA3-512 digests only; no address stored.
TENANT BOUNDARY: Exact tenant/principal bindings are asserted.
AUTHORITY BOUNDARY: Deterministic domain certificate only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Malformed or contradictory state must raise stable errors.
"""

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.saas.auth.password_recovery_contact import (
    SCHEMA,
    VerifiedRecoveryContact,
    VerifiedRecoveryContactChannel,
    VerifiedRecoveryContactError,
    VerifiedRecoveryContactStatus,
)

NOW = datetime(2026, 9, 22, 16, 0, tzinfo=timezone.utc)
DIGEST = "a" * 128


def _contact() -> VerifiedRecoveryContact:
    return VerifiedRecoveryContact.issue(
        contact_id="CONTACT-1",
        tenant_id="TENANT-1",
        principal_id="PRINCIPAL-1",
        channel=VerifiedRecoveryContactChannel.EMAIL,
        address_digest=DIGEST,
        verified_at=NOW,
    )


def test_issue_is_active_digest_only_and_exactly_bound() -> None:
    contact = _contact()
    assert contact.status is VerifiedRecoveryContactStatus.ACTIVE
    assert contact.tenant_id == "TENANT-1"
    assert contact.principal_id == "PRINCIPAL-1"
    assert contact.channel is VerifiedRecoveryContactChannel.EMAIL
    assert contact.address_digest == DIGEST
    rendered = repr(contact).lower()
    assert "@" not in rendered
    assert "email=" not in rendered


def test_revoke_returns_new_terminal_state_without_mutating_original() -> None:
    contact = _contact()
    revoked = contact.revoke(NOW + timedelta(hours=1))
    assert contact.status is VerifiedRecoveryContactStatus.ACTIVE
    assert contact.revoked_at is None
    assert revoked.status is VerifiedRecoveryContactStatus.REVOKED
    assert revoked.revoked_at == NOW + timedelta(hours=1)


def test_document_round_trip_is_exact_and_has_no_raw_address_field() -> None:
    contact = _contact()
    document = contact.to_document()
    assert document["schema"] == SCHEMA
    assert set(document) == {
        "schema",
        "contact_id",
        "tenant_id",
        "principal_id",
        "channel",
        "address_digest",
        "verified_at",
        "status",
        "revoked_at",
    }
    assert VerifiedRecoveryContact.from_document(document) == contact


@pytest.mark.parametrize(
    "mutation,code",
    [
        ({"raw_email": "operator@example.com"}, "PERSISTED_CONTACT_SHAPE_INVALID"),
        ({"address_digest": "A" * 128}, "ADDRESS_DIGEST_INVALID"),
        ({"address_digest": "not-hex"}, "ADDRESS_DIGEST_INVALID"),
        ({"tenant_id": " TENANT-1"}, "TENANT_ID_INVALID"),
        ({"principal_id": ""}, "PRINCIPAL_ID_INVALID"),
    ],
)
def test_hydration_rejects_malformed_or_raw_address_state(mutation, code) -> None:
    document = _contact().to_document()
    if "raw_email" in mutation:
        document.update(mutation)
    else:
        document.update(mutation)
    with pytest.raises(VerifiedRecoveryContactError) as error:
        VerifiedRecoveryContact.from_document(document)
    assert str(error.value) == code


def test_revoked_state_requires_consistent_terminal_timestamp() -> None:
    document = _contact().to_document()
    document["status"] = VerifiedRecoveryContactStatus.REVOKED.value
    with pytest.raises(VerifiedRecoveryContactError) as error:
        VerifiedRecoveryContact.from_document(document)
    assert str(error.value) == "STATUS_TIMESTAMP_MISMATCH"


def test_revoke_before_verification_fails_closed() -> None:
    with pytest.raises(VerifiedRecoveryContactError) as error:
        _contact().revoke(NOW - timedelta(seconds=1))
    assert str(error.value) == "REVOKED_AT_BEFORE_VERIFIED_AT"


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_password_recovery_contact.py
# VERSION: v1.0.0-R10E5-VERIFIED-RECOVERY-CONTACT-DOMAIN-CERT
# AUTHORITY BOUNDARY: deterministic domain certificate only
# TENANT POSTURE: synthetic exact tenant/principal binding
# FAIL-CLOSED POSTURE: malformed, contradictory, and raw-address state rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
