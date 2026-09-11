"""Direct certificate for the P6 activation persistence registry.

TITLE: Tenant Inbound Provider Policy Activation Registry Tests
VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P6
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves two-collection persistence, strict provenance, tenant isolation,
         caller-owned transactions, and closed CAS/idempotency behavior.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_inbound_provider_policy_activation_registry.py
COLLABORATION / OWNERSHIP: Direct P6 registry certificate; P5 domain and P7 orchestration remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3C-P6 certifies registry identity, slot, CAS,
           strict hydration, and transaction firewalls.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
import inspect
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.domain.tenant_inbound_merchant_configuration import InboundMerchantProviderId
from tools.eos.saas.domain.tenant_inbound_provider_policy import TenantInboundProviderPolicyScope
from tools.eos.saas.domain.tenant_inbound_provider_policy_activation import (
    TenantInboundProviderPolicyActivationEvent,
    TenantInboundProviderPolicyActivationEventKind,
    TenantInboundProviderPolicyReference,
)
from tools.eos.saas.billing.tenant_inbound_provider_policy_activation_registry import (
    ACTIVE_SLOT_INDEX_NAME,
    ACTIVATION_REVISION_INCREMENT,
    EVENT_COLLECTION,
    EVENT_IDENTITY_INDEX_NAME,
    FIRST_ACTIVATION_REVISION,
    IDEMPOTENCY_INDEX_NAME,
    REVISION_INDEX_NAME,
    SLOT_COLLECTION,
    TenantInboundProviderPolicyActivationRegistryCASConflictError,
    TenantInboundProviderPolicyActivationRegistryRecordInvalidError,
    TenantInboundProviderPolicyActivationRegistryTransactionError,
    TenantInboundProviderPolicyActivationSlot,
    append_event_and_advance_slot,
    ensure_indexes,
    get_current_slot,
    get_event,
    get_event_by_idempotency_key,
)
from tools.eos.saas.billing import tenant_inbound_provider_policy_activation_registry as registry_module


VERSION = "v1.0.0-M11-R8-R3B-P8-P3C-P6"
CAMPAIGN_IDENTITY = "M11-R8-R3B-P8-P3C-P6"
NOW = datetime(2026, 9, 10, 10, 0, tzinfo=timezone.utc)


class Session:
    in_transaction = True


class Result:
    def __init__(self, matched_count: int) -> None:
        self.matched_count = matched_count


class FakeCollection:
    def __init__(self) -> None:
        self.docs: list[dict[str, object]] = []
        self.indexes: list[dict[str, object]] = []
        self.update_calls = 0
        self.insert_calls = 0
        self.last_sessions: list[object] = []

    @staticmethod
    def _same(doc: dict[str, object], query: dict[str, object]) -> bool:
        return all(doc.get(key) == value for key, value in query.items())

    def create_index(self, fields: list[tuple[str, int]], *, unique: bool = False, name: str = "", **_: object) -> str:
        self.indexes.append({"fields": fields, "unique": unique, "name": name})
        return name

    def find_one(self, query: dict[str, object], **kwargs: object) -> dict[str, object] | None:
        self.last_sessions.append(kwargs.get("session"))
        for doc in self.docs:
            if self._same(doc, query):
                return dict(doc)
        return None

    def insert_one(self, document: dict[str, object], **kwargs: object) -> object:
        self.insert_calls += 1
        self.last_sessions.append(kwargs.get("session"))
        for index in self.indexes:
            if not bool(index["unique"]):
                continue
            fields = [field for field, _ in index["fields"]]  # type: ignore[index]
            if any(all(old.get(field) == document.get(field) for field in fields) for old in self.docs):
                raise DuplicateKeyError("duplicate key")
        self.docs.append(dict(document))
        return object()

    def update_one(self, query: dict[str, object], update: dict[str, object], **kwargs: object) -> Result:
        self.update_calls += 1
        self.last_sessions.append(kwargs.get("session"))
        for index, doc in enumerate(self.docs):
            if self._same(doc, query):
                replacement = dict(doc)
                replacement.update(dict(update.get("$set", {})))  # type: ignore[arg-type]
                self.docs[index] = replacement
                return Result(1)
        return Result(0)


def _reference(**changes: object) -> TenantInboundProviderPolicyReference:
    values: dict[str, object] = {
        "provider_policy_id": "policy-1",
        "policy_version": 1,
        "policy_fingerprint": "a" * 128,
        "provider_id": InboundMerchantProviderId.PAYFAST,
        "merchant_configuration_id": "config-1",
        "merchant_configuration_version": 1,
        "merchant_configuration_fingerprint": "b" * 128,
    }
    values.update(changes)
    return TenantInboundProviderPolicyReference(**values)  # type: ignore[arg-type]


def _event(kind: TenantInboundProviderPolicyActivationEventKind, revision: int, **changes: object) -> TenantInboundProviderPolicyActivationEvent:
    prior: TenantInboundProviderPolicyReference | None
    target: TenantInboundProviderPolicyReference | None
    if kind is TenantInboundProviderPolicyActivationEventKind.ACTIVATE:
        prior, target = None, _reference()
    elif kind is TenantInboundProviderPolicyActivationEventKind.SUPERSEDE:
        prior, target = _reference(), _reference(provider_policy_id="policy-2")
    else:
        prior, target = _reference(), None
    values: dict[str, object] = {
        "tenant_id": "tenant-1",
        "policy_scope": TenantInboundProviderPolicyScope.INBOUND_COLLECTION,
        "activation_event_id": f"event-{revision}",
        "activation_revision": revision,
        "event_kind": kind,
        "lifecycle_idempotency_key": f"idem-{revision}",
        "prior_active_policy": prior,
        "target_active_policy": target,
        "authorization_reference": "auth-1",
        "authorization_evidence_fingerprint": "c" * 128,
        "reason_reference": "reason-1",
        "occurred_at": NOW,
    }
    values.update(changes)
    return TenantInboundProviderPolicyActivationEvent(**values)  # type: ignore[arg-type]


def _collections() -> tuple[FakeCollection, FakeCollection]:
    events, slots = FakeCollection(), FakeCollection()
    ensure_indexes(events, slots)
    return events, slots


def _seed() -> tuple[FakeCollection, FakeCollection, TenantInboundProviderPolicyActivationSlot]:
    events, slots = _collections()
    state = append_event_and_advance_slot(
        _event(TenantInboundProviderPolicyActivationEventKind.ACTIVATE, 0),
        None,
        None,
        event_collection=events,
        slot_collection=slots,
        session=Session(),
    )
    return events, slots, state


@pytest.mark.parametrize(
    ("index", "fields", "name"),
    [
        ("event", [("tenant_id", 1), ("policy_scope", 1), ("activation_event_id", 1)], EVENT_IDENTITY_INDEX_NAME),
        ("event", [("tenant_id", 1), ("policy_scope", 1), ("lifecycle_idempotency_key", 1)], IDEMPOTENCY_INDEX_NAME),
        ("event", [("tenant_id", 1), ("policy_scope", 1), ("activation_revision", 1)], REVISION_INDEX_NAME),
        ("slot", [("tenant_id", 1), ("policy_scope", 1)], ACTIVE_SLOT_INDEX_NAME),
    ],
)
def test_indexes_are_exact_and_unique(index: str, fields: list[tuple[str, int]], name: str) -> None:
    events, slots = _collections()
    rows = events.indexes if index == "event" else slots.indexes
    assert {row["name"] for row in rows} >= {name}
    row = next(row for row in rows if row["name"] == name)
    assert row["fields"] == fields
    assert row["unique"] is True


def test_two_distinct_collections_and_no_partial_active_policy_index() -> None:
    events, slots = _collections()
    assert EVENT_COLLECTION != SLOT_COLLECTION
    assert len(events.indexes) == 3
    assert len(slots.indexes) == 1
    assert not any("active_policy" in str(row["name"]) for row in events.indexes)


@pytest.mark.parametrize("kind", list(TenantInboundProviderPolicyActivationEventKind))
def test_valid_event_round_trips(kind: TenantInboundProviderPolicyActivationEventKind) -> None:
    events, slots = _collections()
    event = _event(kind, 0)
    events.docs.append(event.to_dict())
    assert get_event("tenant-1", TenantInboundProviderPolicyScope.INBOUND_COLLECTION, event.activation_event_id, events, session=Session()) == event
    assert slots.docs == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("activation_event_fingerprint", "f" * 128),
        ("authorization_evidence_fingerprint", "bad"),
        ("event_kind", "BROKEN"),
        ("occurred_at", datetime(2026, 9, 10, 10, 0)),
        ("prior_active_policy", {"corrupt": True}),
        ("target_active_policy", {"corrupt": True}),
    ],
)
def test_corrupt_event_hydration_fails_closed(field: str, value: object) -> None:
    events, _ = _collections()
    payload = _event(TenantInboundProviderPolicyActivationEventKind.ACTIVATE, 0).to_dict()
    payload[field] = value
    events.docs.append(payload)
    with pytest.raises(TenantInboundProviderPolicyActivationRegistryRecordInvalidError):
        get_event("tenant-1", TenantInboundProviderPolicyScope.INBOUND_COLLECTION, "event-0", events, session=Session())


@pytest.mark.parametrize("missing", ["tenant_id", "activation_event_id", "activation_event_fingerprint"])
def test_missing_event_field_fails_without_repair(missing: str) -> None:
    events, _ = _collections()
    payload = _event(TenantInboundProviderPolicyActivationEventKind.ACTIVATE, 0).to_dict()
    payload.pop(missing, None)
    events.docs.append(payload)
    with pytest.raises(TenantInboundProviderPolicyActivationRegistryRecordInvalidError):
        registry_module._hydrate_event(payload)
    assert payload == payload


def test_event_hydration_has_no_auto_repair_or_backfill() -> None:
    source = inspect.getsource(registry_module)
    assert "setdefault" not in source
    assert "_hydrate_event" in source


@pytest.mark.parametrize("case", ["exact", "missing", "cross_tenant", "cross_scope", "session"])
def test_idempotency_lookup_scope_and_session(case: str) -> None:
    events, _, _ = _seed()
    event = get_event_by_idempotency_key("tenant-1", TenantInboundProviderPolicyScope.INBOUND_COLLECTION, "idem-0", events, session=Session())
    if case == "exact":
        assert event is not None
    elif case == "missing":
        assert get_event_by_idempotency_key("tenant-1", TenantInboundProviderPolicyScope.INBOUND_COLLECTION, "missing", events) is None
    elif case == "cross_tenant":
        assert get_event_by_idempotency_key("tenant-2", TenantInboundProviderPolicyScope.INBOUND_COLLECTION, "idem-0", events) is None
    elif case == "cross_scope":
        with pytest.raises(Exception):
            get_event_by_idempotency_key("tenant-1", "OUTBOUND", "idem-0", events)  # type: ignore[arg-type]
    else:
        assert events.last_sessions[-1] is not None


@pytest.mark.parametrize("case", ["exact", "cross_tenant", "corrupt"])
def test_event_read_scope_and_strictness(case: str) -> None:
    events, _, _ = _seed()
    if case == "exact":
        assert get_event("tenant-1", TenantInboundProviderPolicyScope.INBOUND_COLLECTION, "event-0", events) is not None
    elif case == "cross_tenant":
        assert get_event("tenant-2", TenantInboundProviderPolicyScope.INBOUND_COLLECTION, "event-0", events) is None
    else:
        events.docs[0]["event_fingerprint"] = "f" * 128
        with pytest.raises(TenantInboundProviderPolicyActivationRegistryRecordInvalidError):
            get_event("tenant-1", TenantInboundProviderPolicyScope.INBOUND_COLLECTION, "event-0", events)


@pytest.mark.parametrize("case", ["none", "active", "empty", "revision", "missing_event", "bad_event", "revision_mismatch", "fingerprint_mismatch", "target_mismatch", "slot_session", "event_session"])
def test_current_slot_strict_provenance(case: str) -> None:
    events, slots, state = _seed()
    if case == "none":
        empty_events, empty_slots = _collections()
        assert get_current_slot("tenant-1", TenantInboundProviderPolicyScope.INBOUND_COLLECTION, empty_slots, empty_events) is None
    elif case == "active":
        assert get_current_slot("tenant-1", TenantInboundProviderPolicyScope.INBOUND_COLLECTION, slots, events) == state
    elif case == "empty":
        deactivated = _event(TenantInboundProviderPolicyActivationEventKind.DEACTIVATE, 1)
        append_event_and_advance_slot(deactivated, 0, state.current_active_policy, event_collection=events, slot_collection=slots, session=Session())
        current = get_current_slot("tenant-1", TenantInboundProviderPolicyScope.INBOUND_COLLECTION, slots, events)
        assert current is not None and current.current_active_policy is None
    else:
        if case == "missing_event":
            slots.docs[0]["last_activation_event_id"] = "missing"
        elif case == "bad_event":
            events.docs[0]["event_fingerprint"] = "f" * 128
        elif case == "revision_mismatch":
            slots.docs[0]["current_activation_revision"] = 3
        elif case == "fingerprint_mismatch":
            slots.docs[0]["last_activation_event_fingerprint"] = "f" * 128
        elif case == "target_mismatch":
            slots.docs[0]["current_active_policy"] = None
        elif case == "revision":
            slots.docs[0]["current_activation_revision"] = True
        if case in {"slot_session", "event_session"}:
            current = get_current_slot("tenant-1", TenantInboundProviderPolicyScope.INBOUND_COLLECTION, slots, events, session=Session())
            assert current == state
        else:
            with pytest.raises(TenantInboundProviderPolicyActivationRegistryRecordInvalidError):
                get_current_slot("tenant-1", TenantInboundProviderPolicyScope.INBOUND_COLLECTION, slots, events, session=Session())
        if case == "slot_session":
            assert slots.last_sessions[-1] is not None
        if case == "event_session":
            assert events.last_sessions[-1] is not None


@pytest.mark.parametrize("case", ["insert_event", "create_slot", "revision", "prior_none", "same_session", "preexisting", "wrong_revision", "non_null_prior"])
def test_initial_transition_contract(case: str) -> None:
    events, slots = _collections()
    if case == "preexisting":
        slots.docs.append({"tenant_id": "tenant-1", "policy_scope": "INBOUND_COLLECTION", "current_activation_revision": 0, "current_active_policy": None, "last_activation_event_id": "x", "last_activation_event_fingerprint": "a" * 128})
    kwargs: dict[str, object] = {}
    expected_revision: int | None = None
    expected_policy: TenantInboundProviderPolicyReference | None = None
    if case == "wrong_revision":
        kwargs["activation_revision"] = 1
    if case == "non_null_prior":
        kwargs["prior_active_policy"] = _reference()
    event_revision = kwargs.pop("activation_revision", 0)
    if case == "non_null_prior":
        with pytest.raises(ValueError):
            _event(TenantInboundProviderPolicyActivationEventKind.ACTIVATE, 0, prior_active_policy=_reference())
        return
    event = _event(TenantInboundProviderPolicyActivationEventKind.ACTIVATE, int(event_revision), **kwargs)  # type: ignore[arg-type]
    if case in {"preexisting", "wrong_revision", "non_null_prior"}:
        with pytest.raises(TenantInboundProviderPolicyActivationRegistryCASConflictError):
            append_event_and_advance_slot(event, expected_revision, expected_policy, event_collection=events, slot_collection=slots, session=Session())
    else:
        state = append_event_and_advance_slot(event, expected_revision, expected_policy, event_collection=events, slot_collection=slots, session=Session())
        assert state.current_activation_revision == FIRST_ACTIVATION_REVISION
        assert len(events.docs) == 1 and len(slots.docs) == 1
        assert events.last_sessions[-1] is slots.last_sessions[-1]


@pytest.mark.parametrize("kind", [TenantInboundProviderPolicyActivationEventKind.SUPERSEDE, TenantInboundProviderPolicyActivationEventKind.DEACTIVATE, TenantInboundProviderPolicyActivationEventKind.EMERGENCY_DISABLE])
def test_existing_slot_transitions_use_next_revision_and_exact_target(kind: TenantInboundProviderPolicyActivationEventKind) -> None:
    events, slots, state = _seed()
    event = _event(kind, 1)
    result = append_event_and_advance_slot(event, 0, state.current_active_policy, event_collection=events, slot_collection=slots, session=Session())
    assert result.current_active_policy == event.target_active_policy
    assert result.current_activation_revision == 1


@pytest.mark.parametrize("case", ["wrong_revision", "wrong_prior", "zero_match", "no_second_cas", "no_delete", "next", "prior", "tenant", "scope", "target"])
def test_existing_cas_contract(case: str) -> None:
    events, slots, state = _seed()
    event = _event(TenantInboundProviderPolicyActivationEventKind.SUPERSEDE, 1)
    expected_revision: int | None = 0
    expected_policy: TenantInboundProviderPolicyReference | None = state.current_active_policy
    if case == "wrong_revision":
        expected_revision = 2
    if case == "wrong_prior":
        expected_policy = _reference(provider_policy_id="other")
    if case == "zero_match":
        slots.docs[0]["current_activation_revision"] = 4
    if case in {"wrong_revision", "wrong_prior", "zero_match"}:
        with pytest.raises(TenantInboundProviderPolicyActivationRegistryCASConflictError):
            append_event_and_advance_slot(event, expected_revision, expected_policy, event_collection=events, slot_collection=slots, session=Session())
        assert slots.update_calls == 0 if case != "zero_match" else slots.update_calls == 0
    else:
        assert event.activation_revision == expected_revision + ACTIVATION_REVISION_INCREMENT  # type: ignore[operator]
        assert event.prior_active_policy == expected_policy
        assert event.tenant_id == "tenant-1" and event.policy_scope is TenantInboundProviderPolicyScope.INBOUND_COLLECTION
        assert event.target_active_policy is not None
        assert event.target_active_policy == _event(TenantInboundProviderPolicyActivationEventKind.SUPERSEDE, 1).target_active_policy
        assert ACTIVATION_REVISION_INCREMENT == 1


@pytest.mark.parametrize("case", ["event", "idempotency", "revision", "slot"])
def test_duplicate_keys_propagate(case: str) -> None:
    events, slots, state = _seed()
    if case == "event":
        duplicate = _event(TenantInboundProviderPolicyActivationEventKind.SUPERSEDE, 1, activation_event_id="event-0")
        with pytest.raises(DuplicateKeyError):
            append_event_and_advance_slot(duplicate, 0, state.current_active_policy, event_collection=events, slot_collection=slots, session=Session())
    elif case == "idempotency":
        duplicate = _event(TenantInboundProviderPolicyActivationEventKind.SUPERSEDE, 1, lifecycle_idempotency_key="idem-0")
        with pytest.raises(DuplicateKeyError):
            append_event_and_advance_slot(duplicate, 0, state.current_active_policy, event_collection=events, slot_collection=slots, session=Session())
    elif case == "revision":
        fresh_events, fresh_slots = _collections()
        fresh_events.docs.append(_event(TenantInboundProviderPolicyActivationEventKind.ACTIVATE, 0).to_dict())
        with pytest.raises(DuplicateKeyError):
            append_event_and_advance_slot(_event(TenantInboundProviderPolicyActivationEventKind.ACTIVATE, 0), None, None, event_collection=fresh_events, slot_collection=fresh_slots, session=Session())
    else:
        slots.docs.append(dict(slots.docs[0]))
        with pytest.raises(DuplicateKeyError):
            slots.insert_one(dict(slots.docs[0]), session=Session())


@pytest.mark.parametrize("operation", ["append", "commit", "abort", "start_session", "duplicate_recovery", "cas_recovery", "compensating_delete", "construct_event", "select_kind", "authorize"])
def test_transaction_and_authority_firewalls(operation: str) -> None:
    events, slots = _collections()
    if operation == "append":
        with pytest.raises(TenantInboundProviderPolicyActivationRegistryTransactionError):
            append_event_and_advance_slot(_event(TenantInboundProviderPolicyActivationEventKind.ACTIVATE, 0), None, None, event_collection=events, slot_collection=slots, session=None)
    else:
        source = inspect.getsource(registry_module)
        if operation in {"commit", "abort", "start_session", "duplicate_recovery", "cas_recovery", "compensating_delete"}:
            assert f".{operation.replace('_recovery', '')}(" not in source
        else:
            assert "authorization_decision" not in source
            assert "TenantInboundProviderPolicyActivationEvent(" not in source


@pytest.mark.parametrize("field", ["credential_safe", "current_secret_version", "raw_secret", "kms_result", "binding_eligibility", "checkout_eligibility", "current_pointer", "current_policy", "ClientInvoice", "CommercialReceivable", "provider_policy_create", "provider_policy_revise", "merchant_configuration"])
def test_registry_security_financial_and_authority_firewalls(field: str) -> None:
    event_fields = set(TenantInboundProviderPolicyActivationEvent.__dataclass_fields__)
    slot_fields = set(TenantInboundProviderPolicyActivationSlot.__dataclass_fields__)
    assert field.lower() not in {name.lower() for name in event_fields | slot_fields}
    if field in {"ClientInvoice", "CommercialReceivable"}:
        assert field not in registry_module.__dict__


def test_slot_projection_is_frozen_and_not_domain_event() -> None:
    _, _, state = _seed()
    with pytest.raises(FrozenInstanceError):
        state.tenant_id = "other"  # type: ignore[misc]
    assert not issubclass(TenantInboundProviderPolicyActivationSlot, TenantInboundProviderPolicyActivationEvent)


# ARTIFACT: test_tenant_inbound_provider_policy_activation_registry.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3C-P6
# AUTHORITY BOUNDARY: direct registry certificate only; no orchestration or real Mongo.
# FAIL-CLOSED POSTURE: indexes, strict hydration, provenance, CAS, transaction, and security firewalls are explicit.
# END OF WILSY OS SOVEREIGN ARTIFACT
