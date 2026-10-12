"""Adversarial unit certificate for L8-8H binding lifecycle evidence.

TITLE: Legal Notification Recipient Binding Lifecycle Unit Certificate
VERSION: v1.0.0-L8-8H-BINDING-LIFECYCLE-UNIT-CERT
AUTHORITY: Wilsy OS test governance only.
EPITOME: Certifies immutable revocation/supersession lineage and chronology.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_notification_recipient_binding_lifecycle.py
COLLABORATION / OWNERSHIP: Tests L8-8H binding lifecycle domain only.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0 establishes lifecycle adversarial verification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only.
TENANT BOUNDARY: Cross-tenant successor rejection is certified.
AUTHORITY BOUNDARY: Test evidence only; no dispatch or IAM.
TRANSACTION BOUNDARY: Pure unit test; no database.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Invalid lineage or chronology fails.
"""
from datetime import datetime, timedelta, timezone
import pytest

from tools.eos.legal_operations.domain.legal_notification_recipient_binding import LegalNotificationEvent, LegalNotificationRecipientBinding
from tools.eos.legal_operations.domain.legal_notification_recipient_binding_lifecycle import LegalNotificationRecipientBindingLifecycle, LegalNotificationRecipientBindingLifecycleError, revoke_binding, supersede_binding

NOW = datetime(2026, 10, 12, 8, 0, tzinfo=timezone.utc)


def binding(identity: str, principal: str, at: datetime, tenant: str = "tenant-a") -> LegalNotificationRecipientBinding:
    """Build one synthetic immutable binding."""
    return LegalNotificationRecipientBinding(tenant_id=tenant, binding_id=identity, case_matter_id="matter-1", event=LegalNotificationEvent.RETURN_READY, recipient_principal_id=principal, effective_from=at, effective_until=None, created_by_principal_id="principal-admin", created_at=at - timedelta(seconds=1))


def test_revocation_and_supersession_are_deterministic_strict_and_contact_free() -> None:
    """Prove exact lineage round-trip and conditional successor fields."""
    first = binding("binding-1", "principal-1", NOW); second = binding("binding-2", "principal-2", NOW + timedelta(hours=1))
    revoked = revoke_binding(lifecycle_event_id="revoke-1", target=first, effective_at=NOW + timedelta(minutes=30), created_by_principal_id="principal-admin", created_at=NOW + timedelta(minutes=29))
    superseded = supersede_binding(lifecycle_event_id="supersede-1", target=first, successor=second, created_by_principal_id="principal-admin", created_at=NOW + timedelta(minutes=59))
    assert LegalNotificationRecipientBindingLifecycle.from_dict(revoked.to_dict()) == revoked
    assert LegalNotificationRecipientBindingLifecycle.from_dict(superseded.to_dict()) == superseded
    assert superseded.successor_binding_fingerprint == second.fingerprint
    assert not ({"email", "phone", "address", "provider", "message"} & set(superseded.to_dict()))


def test_lifecycle_rejects_cross_scope_backdating_and_tampering() -> None:
    """Reject foreign successor, non-forward termination and fingerprint drift."""
    first = binding("binding-1", "principal-1", NOW)
    with pytest.raises(LegalNotificationRecipientBindingLifecycleError):
        supersede_binding(lifecycle_event_id="bad", target=first, successor=binding("binding-2", "principal-2", NOW + timedelta(hours=1), "tenant-b"), created_by_principal_id="principal-admin", created_at=NOW)
    with pytest.raises(LegalNotificationRecipientBindingLifecycleError):
        revoke_binding(lifecycle_event_id="bad", target=first, effective_at=NOW, created_by_principal_id="principal-admin", created_at=NOW)
    payload = revoke_binding(lifecycle_event_id="revoke", target=first, effective_at=NOW + timedelta(hours=1), created_by_principal_id="principal-admin", created_at=NOW).to_dict()
    with pytest.raises(LegalNotificationRecipientBindingLifecycleError):
        LegalNotificationRecipientBindingLifecycle.from_dict({**payload, "target_binding_fingerprint": "b" * 128})

# ARTIFACT: test_legal_notification_recipient_binding_lifecycle.py
# VERSION: v1.0.0-L8-8H-BINDING-LIFECYCLE-UNIT-CERT
# AUTHORITY BOUNDARY: lifecycle domain verification only
# TENANT POSTURE: synthetic exact tenant scope
# FAIL-CLOSED POSTURE: invalid lineage and chronology reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
