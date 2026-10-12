"""Direct unit certificate for L8-8H binding lifecycle registry.

TITLE: Legal Notification Recipient Binding Lifecycle Registry Unit Certificate
VERSION: v1.0.0-L8-8H-BINDING-LIFECYCLE-REGISTRY-UNIT-CERT
AUTHORITY: Wilsy OS test governance only.
EPITOME: Certifies transaction, replay, scope, corruption and non-TTL contracts.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_notification_recipient_binding_lifecycle_registry.py
COLLABORATION / OWNERSHIP: Tests the L8-8H lifecycle registry only.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0 establishes direct registry adversarial verification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque evidence only.
TENANT BOUNDARY: Exact tenant-scope reads are asserted.
AUTHORITY BOUNDARY: Test evidence only; no currentness or dispatch authority.
TRANSACTION BOUNDARY: Active caller-owned transaction contract is exercised.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Misuse, divergence and corruption fail.
"""
from datetime import datetime, timedelta, timezone
from typing import Any
import pytest

from tools.eos.legal_operations.domain.legal_notification_recipient_binding import LegalNotificationEvent, LegalNotificationRecipientBinding
from tools.eos.legal_operations.domain.legal_notification_recipient_binding_lifecycle import revoke_binding
from tools.eos.legal_operations.registry.legal_notification_recipient_binding_lifecycle_registry import LegalNotificationRecipientBindingLifecycleRegistry, LegalNotificationRecipientBindingLifecycleRegistryError

NOW = datetime(2026, 10, 12, 8, 0, tzinfo=timezone.utc)


class Session:
    """Minimal active transaction witness."""
    in_transaction = True


class Collection:
    """Bounded in-memory collection double."""
    def __init__(self) -> None: self.rows: list[dict[str, Any]] = []; self.indexes: list[dict[str, Any]] = []
    def create_index(self, keys: Any, **kwargs: Any) -> str: self.indexes.append(kwargs); return str(kwargs["name"])
    def find_one(self, query: dict[str, Any], *, session: Any) -> dict[str, Any] | None: return next((row for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)
    def insert_one(self, document: dict[str, Any], *, session: Any) -> object: self.rows.append(dict(document)); return object()
    def find(self, query: dict[str, Any], *, session: Any) -> list[dict[str, Any]]: return [row for row in self.rows if all(row.get(k) == v for k, v in query.items())]


def event() -> Any:
    """Build one valid immutable revocation event."""
    target = LegalNotificationRecipientBinding(tenant_id="tenant-a", binding_id="binding-1", case_matter_id="matter-1", event=LegalNotificationEvent.RETURN_READY, recipient_principal_id="principal-1", effective_from=NOW, effective_until=None, created_by_principal_id="principal-admin", created_at=NOW - timedelta(seconds=1))
    return revoke_binding(lifecycle_event_id="revoke-1", target=target, effective_at=NOW + timedelta(hours=1), created_by_principal_id="principal-admin", created_at=NOW + timedelta(minutes=59))


def test_lifecycle_registry_requires_transaction_replays_and_has_no_ttl() -> None:
    """Prove exact replay, scope reads, transaction enforcement and durable indexes."""
    collection = Collection(); registry = LegalNotificationRecipientBindingLifecycleRegistry(collection); registry.ensure_indexes(); value = event()
    with pytest.raises(LegalNotificationRecipientBindingLifecycleRegistryError, match="ACTIVE_TRANSACTION_REQUIRED"): registry.create_or_replay(value, session=None)
    assert registry.create_or_replay(value, session=Session()) == value
    assert registry.create_or_replay(value, session=Session()) == value and len(collection.rows) == 1
    assert registry.list_scope("tenant-a", "matter-1", LegalNotificationEvent.RETURN_READY, session=Session()) == (value,)
    assert registry.list_scope("tenant-b", "matter-1", LegalNotificationEvent.RETURN_READY, session=Session()) == ()
    assert all("expireAfterSeconds" not in item for item in collection.indexes)


def test_lifecycle_registry_rejects_corrupt_history() -> None:
    """Reject persisted fingerprint drift before returning lifecycle evidence."""
    collection = Collection(); registry = LegalNotificationRecipientBindingLifecycleRegistry(collection); value = event(); registry.create_or_replay(value, session=Session()); collection.rows[0]["fingerprint"] = "b" * 128
    with pytest.raises(LegalNotificationRecipientBindingLifecycleRegistryError, match="PERSISTED_RECORD_INVALID"): registry.list_scope("tenant-a", "matter-1", LegalNotificationEvent.RETURN_READY, session=Session())

# ARTIFACT: test_legal_notification_recipient_binding_lifecycle_registry.py
# VERSION: v1.0.0-L8-8H-BINDING-LIFECYCLE-REGISTRY-UNIT-CERT
# AUTHORITY BOUNDARY: lifecycle registry verification only
# TENANT POSTURE: exact synthetic tenant scope
# FAIL-CLOSED POSTURE: misuse, divergence and corruption reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
