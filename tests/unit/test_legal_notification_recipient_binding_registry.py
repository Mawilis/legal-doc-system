"""Direct unit certificate for the L8-8H durable binding registry.

TITLE: Legal Notification Recipient Binding Registry Unit Certificate
VERSION: v1.1.0-L8-8H-RECIPIENT-BINDING-REGISTRY-UNIT-CERT
AUTHORITY: Wilsy OS test governance only.
EPITOME: Certifies transaction enforcement, replay, conflict, effective reads and indexes.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_notification_recipient_binding_registry.py
COLLABORATION / OWNERSHIP: Tests the L8-8H registry with an in-memory collection double.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.1.0 adopts the contact-free binding v1.1 schema.
           v1.0.0 establishes direct adversarial registry verification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only.
TENANT BOUNDARY: Foreign-tenant absence is asserted.
AUTHORITY BOUNDARY: Persistence contract test only; no delivery.
TRANSACTION BOUNDARY: Active-session contract is explicitly exercised.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Replay divergence and corruption reject.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_notification_recipient_binding import LegalNotificationEvent, LegalNotificationRecipientBinding
from tools.eos.legal_operations.registry.legal_notification_recipient_binding_registry import LegalNotificationRecipientBindingRegistry, LegalNotificationRecipientBindingRegistryError

NOW = datetime(2026, 10, 12, 8, 0, tzinfo=timezone.utc)


class Session:
    """Minimal active-transaction test witness."""
    in_transaction = True


class Result:
    """Minimal insert result."""
    inserted_id = "synthetic"


class Collection:
    """Exact bounded collection double supporting registry predicates."""
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[tuple[Any, dict[str, Any]]] = []

    def create_index(self, keys: Any, **kwargs: Any) -> str:
        self.indexes.append((keys, kwargs)); return str(kwargs["name"])

    def find_one(self, query: dict[str, Any], *, session: Any) -> dict[str, Any] | None:
        return next((row for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)

    def insert_one(self, document: dict[str, Any], *, session: Any) -> Result:
        self.rows.append(dict(document)); return Result()

    def find(self, query: dict[str, Any], *, session: Any) -> list[dict[str, Any]]:
        result = []
        at = query["effective_from"]["$lte"]
        for row in self.rows:
            if row["tenant_id"] == query["tenant_id"] and row["case_matter_id"] == query["case_matter_id"] and row["event"] == query["event"] and row["effective_from"] <= at and (row["effective_until"] is None or row["effective_until"] > at):
                result.append(row)
        return result


def value(**overrides: object) -> LegalNotificationRecipientBinding:
    """Build a valid binding for registry tests."""
    fields: dict[str, object] = {"tenant_id": "tenant-a", "binding_id": "binding-1", "case_matter_id": "matter-1", "event": LegalNotificationEvent.RETURN_READY, "recipient_principal_id": "principal-1", "effective_from": NOW, "effective_until": None, "created_by_principal_id": "principal-admin", "created_at": NOW - timedelta(seconds=1)}
    fields.update(overrides)
    return LegalNotificationRecipientBinding(**fields)  # type: ignore[arg-type]


def test_registry_indexes_replay_effective_scope_and_tenant_absence() -> None:
    """Prove durable non-TTL indexes, exact replay and exact tenant reads."""
    collection = Collection(); registry = LegalNotificationRecipientBindingRegistry(collection); registry.ensure_indexes()
    original = value()
    assert registry.create_or_replay(original, session=Session()) == original
    assert registry.create_or_replay(original, session=Session()) == original
    assert len(collection.rows) == 1
    assert registry.list_effective("tenant-a", "matter-1", LegalNotificationEvent.RETURN_READY, NOW, session=Session()) == (original,)
    assert registry.list_effective("tenant-b", "matter-1", LegalNotificationEvent.RETURN_READY, NOW, session=Session()) == ()
    assert all("expireAfterSeconds" not in options for _, options in collection.indexes)


def test_registry_rejects_missing_transaction_divergence_and_corruption() -> None:
    """Fail closed on transaction misuse, replay substitution and corrupt rows."""
    collection = Collection(); registry = LegalNotificationRecipientBindingRegistry(collection); original = value()
    with pytest.raises(LegalNotificationRecipientBindingRegistryError, match="ACTIVE_TRANSACTION_REQUIRED"):
        registry.create_or_replay(original, session=None)
    registry.create_or_replay(original, session=Session())
    with pytest.raises(LegalNotificationRecipientBindingRegistryError, match="REPLAY_CONFLICT"):
        registry.create_or_replay(value(recipient_principal_id="principal-2"), session=Session())
    collection.rows[0]["fingerprint"] = "b" * 128
    with pytest.raises(LegalNotificationRecipientBindingRegistryError, match="PERSISTED_RECORD_INVALID"):
        registry.list_effective("tenant-a", "matter-1", LegalNotificationEvent.RETURN_READY, NOW, session=Session())

# ARTIFACT: test_legal_notification_recipient_binding_registry.py
# VERSION: v1.1.0-L8-8H-RECIPIENT-BINDING-REGISTRY-UNIT-CERT
# AUTHORITY BOUNDARY: direct registry verification only
# TENANT POSTURE: exact synthetic tenant scopes
# FAIL-CLOSED POSTURE: misuse and corrupt evidence fail
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
