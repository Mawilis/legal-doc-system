"""Adversarial unit certificate for L8-8H recipient-binding authority.

TITLE: Legal Notification Recipient Binding Unit Certificate
VERSION: v1.1.0-L8-8H-RECIPIENT-BINDING-UNIT-CERT
AUTHORITY: Wilsy OS test governance only.
EPITOME: Certifies strict immutable, contact-free recipient selection evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_notification_recipient_binding.py
COLLABORATION / OWNERSHIP: Tests the L8-8H domain only.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.1.0 certifies removal of unverifiable source-authority fields.
           v1.0.0 establishes deterministic hydration, interval and adversarial checks.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only.
TENANT BOUNDARY: Includes forbidden-tenant rejection.
AUTHORITY BOUNDARY: Test evidence only; no dispatch or contact authority.
TRANSACTION BOUNDARY: Pure unit test; no database.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Any unexpected acceptance fails this certificate.
"""
from datetime import datetime, timedelta, timezone
from dataclasses import FrozenInstanceError

import pytest

from tools.eos.legal_operations.domain.legal_notification_recipient_binding import LegalNotificationEvent, LegalNotificationRecipientBinding, LegalNotificationRecipientBindingError

NOW = datetime(2026, 10, 12, 8, 0, tzinfo=timezone.utc)


def binding(**overrides: object) -> LegalNotificationRecipientBinding:
    """Build one valid synthetic explicit decision, accepting bounded overrides."""
    values: dict[str, object] = {
        "tenant_id": "tenant-a", "binding_id": "binding-1", "case_matter_id": "matter-1",
        "event": LegalNotificationEvent.RETURN_READY, "recipient_principal_id": "principal-1",
        "effective_from": NOW, "effective_until": None, "created_by_principal_id": "principal-admin",
        "created_at": NOW - timedelta(seconds=1),
    }
    values.update(overrides)
    return LegalNotificationRecipientBinding(**values)  # type: ignore[arg-type]


def test_binding_is_deterministic_strict_immutable_and_contact_free() -> None:
    """Prove exact round-trip, immutable state and absence of contact fields."""
    value = binding()
    assert LegalNotificationRecipientBinding.from_dict(value.to_dict()) == value
    assert value.is_effective_at(NOW)
    assert not value.is_effective_at(NOW - timedelta(microseconds=1))
    assert not ({"email", "phone", "address", "channel", "provider", "message"} & set(value.to_dict()))
    with pytest.raises(FrozenInstanceError):
        value.binding_id = "changed"  # type: ignore[misc]


@pytest.mark.parametrize("overrides", [
    {"tenant_id": "global"}, {"effective_from": NOW.replace(tzinfo=None)},
    {"effective_until": NOW}, {"created_at": NOW + timedelta(seconds=1)},
    {"fingerprint": "A" * 128}, {"event": "DELIVER_NOW"},
])
def test_binding_rejects_authority_widening(overrides: dict[str, object]) -> None:
    """Reject pseudo-tenants, non-UTC time, invalid intervals and invented events."""
    with pytest.raises(LegalNotificationRecipientBindingError):
        binding(**overrides)


def test_hydration_rejects_extra_fields_and_tampering() -> None:
    """Reject schema widening and deterministic-fingerprint divergence."""
    payload = binding().to_dict()
    with pytest.raises(LegalNotificationRecipientBindingError):
        LegalNotificationRecipientBinding.from_dict({**payload, "email": "hidden@example.invalid"})
    with pytest.raises(LegalNotificationRecipientBindingError):
        LegalNotificationRecipientBinding.from_dict({**payload, "recipient_principal_id": "substitute"})

# ARTIFACT: test_legal_notification_recipient_binding.py
# VERSION: v1.1.0-L8-8H-RECIPIENT-BINDING-UNIT-CERT
# AUTHORITY BOUNDARY: adversarial domain verification only
# TENANT POSTURE: synthetic exact tenant scope
# FAIL-CLOSED POSTURE: unexpected acceptance fails
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
