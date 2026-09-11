"""Direct certificate for the tenant inbound provider-policy registry.

TITLE: Tenant Inbound Provider Policy Registry Direct Certificate
VERSION: v1.1.0-M11-R8-R3B-P8-P3C-P2-R2
AUTHORITY: Wilsy OS Core Governance
EPITOME: Host-free proof of strict persistence, tenant isolation, and exact
         replay for the immutable provider-policy registry.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_inbound_provider_policy_registry.py
COLLABORATION / OWNERSHIP: Direct unit owner for the paired SaaS billing registry.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.1.0-M11-R8-R3B-P8-P3C-P2-R2 preserves the prior certificate and
           adds bounded predecessor selection, strict hydration, and zero-write proofs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Test data uses opaque references and deterministic digests only.
TENANT BOUNDARY: Every fixture and lookup carries an explicit tenant identity.
AUTHORITY BOUNDARY: Registry persistence only; no authoring, activation, binding, or checkout.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement.
FAIL-CLOSED DECLARATION: Tests require rejection rather than inferred or repaired durable truth.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.billing.tenant_inbound_provider_policy_registry import (
    COLLECTION,
    TenantInboundProviderPolicyNotFoundError,
    TenantInboundProviderPolicyPersistedRecordInvalidError,
    TenantInboundProviderPolicyRegistry,
    TenantInboundProviderPolicyRegistryError,
    TenantInboundProviderPolicyReplayConflictError,
    _hydrate,
)
from tools.eos.saas.domain.tenant_inbound_merchant_configuration import InboundMerchantProviderId
from tools.eos.saas.domain.tenant_inbound_provider_policy import (
    TenantInboundProviderPolicy,
    TenantInboundProviderPolicyScope,
)


class FakeSession:
    """Identity-bearing caller session used to prove exact forwarding."""


class FakeCursor:
    """Minimal cursor supporting the registry's deterministic sort and limit."""

    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows
        self.sort_calls: list[list[tuple[str, int]]] = []
        self.limit_calls: list[int] = []

    def sort(self, keys: list[tuple[str, int]]) -> "FakeCursor":
        self.sort_calls.append(list(keys))
        for key, direction in reversed(keys):
            self.rows.sort(key=lambda row: cast(int, row.get(key, 0)), reverse=direction < 0)
        return self

    def limit(self, count: int) -> "FakeCursor":
        self.limit_calls.append(count)
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(self.rows)


class FakeCollection:
    """Minimal host-free collection recording reads, writes, and indexes."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.calls: list[tuple[str, dict[str, object], dict[str, object]]] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, object]]] = []
        self.cursors: list[FakeCursor] = []
        self.duplicate_on_insert = False

    def create_index(self, keys: list[tuple[str, int]], **kwargs: object) -> str:
        self.indexes.append((keys, dict(kwargs)))
        return str(kwargs.get("name", ""))

    def find_one(self, query: dict[str, object], **kwargs: object) -> dict[str, object] | None:
        self.calls.append(("find_one", dict(query), dict(kwargs)))
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return dict(row)
        return None

    def find(self, query: dict[str, object], **kwargs: object) -> FakeCursor:
        self.calls.append(("find", dict(query), dict(kwargs)))
        rows: list[dict[str, object]] = []
        for row in self.rows:
            matches = True
            for key, expected in query.items():
                if isinstance(expected, dict) and "$lt" in expected:
                    if not isinstance(row.get(key), int) or row[key] >= expected["$lt"]:
                        matches = False
                elif row.get(key) != expected:
                    matches = False
            if matches:
                rows.append(dict(row))
        cursor = FakeCursor(rows)
        self.cursors.append(cursor)
        return cursor

    def insert_one(self, document: dict[str, object], **kwargs: object) -> object:
        self.calls.append(("insert_one", dict(document), dict(kwargs)))
        if self.duplicate_on_insert:
            raise DuplicateKeyError("duplicate policy identity")
        self.rows.append(dict(document))
        return object()


def _policy(**overrides: object) -> TenantInboundProviderPolicy:
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "provider_policy_id": "policy-1",
        "policy_version": 1,
        "policy_scope": TenantInboundProviderPolicyScope.INBOUND_COLLECTION,
        "provider_id": InboundMerchantProviderId.PAYFAST,
        "merchant_configuration_id": "merchant-config-1",
        "merchant_configuration_version": 1,
        "merchant_configuration_fingerprint": "a" * 128,
        "authoring_authorization_reference": "authz-1",
        "authoring_authorization_evidence_fingerprint": "b" * 128,
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
    values.update(overrides)
    return TenantInboundProviderPolicy(**cast(dict[str, Any], values))


def _last(collection: FakeCollection, operation: str) -> tuple[str, dict[str, object], dict[str, object]]:
    return next(call for call in reversed(collection.calls) if call[0] == operation)


def test_collection_and_identity_index_are_frozen() -> None:
    collection = FakeCollection()
    TenantInboundProviderPolicyRegistry.ensure_indexes(collection)
    assert COLLECTION == "tenant_inbound_provider_policies"
    assert collection.indexes == [
        (
            [("tenant_id", 1), ("provider_policy_id", 1), ("policy_version", 1)],
            {"unique": True, "name": "tenant_inbound_provider_policy_identity_unique"},
        )
    ]
    assert all("activation" not in key and "current" not in key for key, _ in collection.indexes[0][0])


def test_create_get_round_trip_and_session_forwarding() -> None:
    collection = FakeCollection()
    session = FakeSession()
    policy = _policy()
    assert TenantInboundProviderPolicyRegistry.create(policy, collection, session=session) == policy
    assert TenantInboundProviderPolicyRegistry.get("tenant-a", "policy-1", 1, collection, session=session) == policy
    assert _last(collection, "find_one")[2]["session"] is session
    assert _last(collection, "insert_one")[2]["session"] is session
    assert set(collection.rows[0]) == set(policy.to_dict())


def test_create_without_session_is_supported_without_transaction_creation() -> None:
    collection = FakeCollection()
    policy = _policy()
    TenantInboundProviderPolicyRegistry.create(policy, collection)
    assert _last(collection, "find_one")[2] == {}
    assert _last(collection, "insert_one")[2] == {}


def test_exact_replay_returns_canonical_without_second_write() -> None:
    collection = FakeCollection()
    policy = _policy()
    TenantInboundProviderPolicyRegistry.create(policy, collection)
    calls_before = len(collection.calls)
    replay = TenantInboundProviderPolicyRegistry.create(policy, collection)
    assert replay == policy
    assert len(collection.calls) == calls_before + 1
    assert not any(call[0] == "insert_one" for call in collection.calls[calls_before:])


@pytest.mark.parametrize(
    "field, value",
    [
        ("merchant_configuration_id", "merchant-config-2"),
        ("merchant_configuration_version", 2),
        ("merchant_configuration_fingerprint", "c" * 128),
        ("authoring_authorization_reference", "authz-2"),
        ("authoring_authorization_evidence_fingerprint", "d" * 128),
        ("created_at", datetime(2026, 1, 2, tzinfo=timezone.utc)),
        ("policy_scope", TenantInboundProviderPolicyScope.INBOUND_COLLECTION),
        ("provider_id", InboundMerchantProviderId.PAYFAST),
    ],
)
def test_divergent_immutable_replay_rejects_without_overwrite(field: str, value: object) -> None:
    collection = FakeCollection()
    original = _policy()
    TenantInboundProviderPolicyRegistry.create(original, collection)
    divergent = _policy(**{field: value})
    if divergent == original:
        divergent = _policy(authoring_authorization_reference="authz-different")
    with pytest.raises(TenantInboundProviderPolicyReplayConflictError):
        TenantInboundProviderPolicyRegistry.create(divergent, collection)
    assert len(collection.rows) == 1
    assert not any(call[0] == "update_one" for call in collection.calls)


def test_policy_version_is_part_of_identity_and_old_row_is_unchanged() -> None:
    collection = FakeCollection()
    first = _policy(policy_version=1)
    second = _policy(policy_version=2)
    TenantInboundProviderPolicyRegistry.create(first, collection)
    TenantInboundProviderPolicyRegistry.create(second, collection)
    assert len(collection.rows) == 2
    assert TenantInboundProviderPolicyRegistry.get("tenant-a", "policy-1", 1, collection) == first
    assert TenantInboundProviderPolicyRegistry.get("tenant-a", "policy-1", 2, collection) == second


@pytest.mark.parametrize("mutation", [
    lambda row: row.pop("policy_fingerprint"),
    lambda row: row.update({"unknown": "drift"}),
    lambda row: row.update({"policy_fingerprint": "e" * 128}),
    lambda row: row.update({"merchant_configuration_fingerprint": "f" * 128}),
    lambda row: row.update({"authoring_authorization_evidence_fingerprint": "0" * 128}),
    lambda row: row.update({"policy_fingerprint_version": "v2"}),
])
def test_strict_hydration_rejects_schema_and_integrity_corruption(mutation: Any) -> None:
    collection = FakeCollection()
    collection.rows.append(_policy().to_dict())
    mutation(collection.rows[0])
    with pytest.raises(TenantInboundProviderPolicyPersistedRecordInvalidError):
        TenantInboundProviderPolicyRegistry.get("tenant-a", "policy-1", 1, collection)


@pytest.mark.parametrize("field", ["tenant_id", "provider_policy_id", "policy_version"])
def test_strict_hydration_rejects_missing_identity_field(field: str) -> None:
    collection = FakeCollection()
    row = _policy().to_dict()
    row.pop(field)
    collection.rows.append(row)
    with pytest.raises(TenantInboundProviderPolicyPersistedRecordInvalidError):
        _hydrate(row)


def test_strict_hydration_rejects_malformed_policy_fingerprint() -> None:
    collection = FakeCollection()
    row = _policy().to_dict()
    row["policy_fingerprint"] = "not-a-sha3"
    collection.rows.append(row)
    with pytest.raises(TenantInboundProviderPolicyPersistedRecordInvalidError):
        TenantInboundProviderPolicyRegistry.get("tenant-a", "policy-1", 1, collection)


def test_provider_divergence_fails_closed_before_replay_write() -> None:
    collection = FakeCollection()
    TenantInboundProviderPolicyRegistry.create(_policy(), collection)
    collection.rows[0]["provider_id"] = "PAYSHAP"
    with pytest.raises(TenantInboundProviderPolicyPersistedRecordInvalidError):
        TenantInboundProviderPolicyRegistry.create(_policy(), collection)
    assert len(collection.rows) == 1


def test_divergent_policy_fingerprint_replay_fails_closed_before_write() -> None:
    collection = FakeCollection()
    TenantInboundProviderPolicyRegistry.create(_policy(), collection)
    collection.rows[0]["policy_fingerprint"] = "e" * 128
    with pytest.raises(TenantInboundProviderPolicyPersistedRecordInvalidError):
        TenantInboundProviderPolicyRegistry.create(_policy(), collection)
    assert len(collection.rows) == 1


def test_create_rejects_non_policy_without_persistence() -> None:
    collection = FakeCollection()
    with pytest.raises(TenantInboundProviderPolicyReplayConflictError):
        TenantInboundProviderPolicyRegistry.create(cast(Any, {"tenant_id": "tenant-a"}), collection)
    assert collection.rows == []


def test_duplicate_key_propagates_without_same_transaction_recovery() -> None:
    collection = FakeCollection()
    collection.duplicate_on_insert = True
    with pytest.raises(DuplicateKeyError):
        TenantInboundProviderPolicyRegistry.create(_policy(), collection, session=FakeSession())
    assert len(collection.rows) == 0


def test_missing_identity_is_not_found_and_lookup_is_exact() -> None:
    collection = FakeCollection()
    with pytest.raises(TenantInboundProviderPolicyNotFoundError):
        TenantInboundProviderPolicyRegistry.get("tenant-a", "missing", 1, collection)
    query = _last(collection, "find_one")[1]
    assert query == {"tenant_id": "tenant-a", "provider_policy_id": "missing", "policy_version": 1}


@pytest.mark.parametrize("tenant", ["tenant-a", "tenant-b"])
def test_same_policy_identity_isolated_by_tenant(tenant: str) -> None:
    collection = FakeCollection()
    policy_a = _policy(tenant_id="tenant-a")
    policy_b = _policy(tenant_id="tenant-b")
    TenantInboundProviderPolicyRegistry.create(policy_a, collection)
    TenantInboundProviderPolicyRegistry.create(policy_b, collection)
    assert TenantInboundProviderPolicyRegistry.get(tenant, "policy-1", 1, collection) == (policy_a if tenant == "tenant-a" else policy_b)
    other = "tenant-b" if tenant == "tenant-a" else "tenant-a"
    assert TenantInboundProviderPolicyRegistry.get(other, "policy-1", 1, collection) != (policy_a if tenant == "tenant-a" else policy_b)


def test_payfast_is_persistable_and_registry_has_no_authorization_or_activation_api() -> None:
    collection = FakeCollection()
    policy = _policy()
    assert TenantInboundProviderPolicyRegistry.create(policy, collection) == policy
    public = set(dir(TenantInboundProviderPolicyRegistry))
    assert not {"authorize", "activate", "deactivate", "get_latest_active_policy", "resolve_provider"} & public
    assert {"policy_fingerprint", "authoring_authorization_reference"} <= set(collection.rows[0])
    assert not {"activation_state", "current_pointer", "credential_security_fact"} & set(collection.rows[0])


def test_payshap_is_not_representable_and_registry_does_not_infer_provider() -> None:
    with pytest.raises(ValueError):
        _policy(provider_id="PAYSHAP")


def test_registry_has_no_commercial_or_execution_imports_or_persisted_keys() -> None:
    source = open("tools/eos/saas/billing/tenant_inbound_provider_policy_registry.py", encoding="utf-8").read()
    assert "ClientInvoice" not in source
    assert "CommercialReceivable" not in source
    assert "payment_state" not in source
    assert "settlement_state" not in source


@pytest.mark.parametrize("value", ["", " tenant-a", "tenant-a "])
def test_lookup_tenant_is_fail_closed(value: str) -> None:
    with pytest.raises(TenantInboundProviderPolicyRegistryError):
        TenantInboundProviderPolicyRegistry.get(value, "policy-1", 1, FakeCollection())


@pytest.mark.parametrize("value", [0, -1, True, "1"])
def test_lookup_version_is_positive_integer(value: object) -> None:
    with pytest.raises(TenantInboundProviderPolicyRegistryError):
        TenantInboundProviderPolicyRegistry.get("tenant-a", "policy-1", cast(int, value), FakeCollection())


def test_predecessor_target_without_rows_returns_none() -> None:
    assert TenantInboundProviderPolicyRegistry.get_predecessor_policy(
        "tenant-a", "policy-1", 2, FakeCollection()
    ) is None


def test_predecessor_returns_same_tenant_policy_v1_for_target_v2() -> None:
    collection = FakeCollection()
    first = _policy(policy_version=1)
    TenantInboundProviderPolicyRegistry.create(first, collection)
    assert TenantInboundProviderPolicyRegistry.get_predecessor_policy(
        "tenant-a", "policy-1", 2, collection
    ) == first


def test_predecessor_returns_highest_lower_version_for_non_contiguous_target() -> None:
    collection = FakeCollection()
    versions = [_policy(policy_version=value) for value in (1, 3, 4)]
    for policy in versions:
        TenantInboundProviderPolicyRegistry.create(policy, collection)
    assert TenantInboundProviderPolicyRegistry.get_predecessor_policy(
        "tenant-a", "policy-1", 5, collection
    ) == versions[-1]
    query = _last(collection, "find")[1]
    assert query == {
        "tenant_id": "tenant-a",
        "provider_policy_id": "policy-1",
        "policy_version": {"$lt": 5},
    }
    assert collection.cursors[-1].sort_calls == [[("policy_version", -1)]]
    assert collection.cursors[-1].limit_calls == [1]


def test_predecessor_excludes_same_and_higher_versions() -> None:
    collection = FakeCollection()
    TenantInboundProviderPolicyRegistry.create(_policy(policy_version=2), collection)
    TenantInboundProviderPolicyRegistry.create(_policy(policy_version=3), collection)
    assert TenantInboundProviderPolicyRegistry.get_predecessor_policy(
        "tenant-a", "policy-1", 2, collection
    ) is None


def test_predecessor_excludes_other_tenant_and_policy_id() -> None:
    collection = FakeCollection()
    TenantInboundProviderPolicyRegistry.create(_policy(tenant_id="tenant-b"), collection)
    TenantInboundProviderPolicyRegistry.create(_policy(provider_policy_id="policy-2"), collection)
    assert TenantInboundProviderPolicyRegistry.get_predecessor_policy(
        "tenant-a", "policy-1", 2, collection
    ) is None


def test_predecessor_forwards_caller_session_and_performs_no_write() -> None:
    collection = FakeCollection()
    policy = _policy()
    TenantInboundProviderPolicyRegistry.create(policy, collection)
    calls_before = len(collection.calls)
    session = FakeSession()
    assert TenantInboundProviderPolicyRegistry.get_predecessor_policy(
        "tenant-a", "policy-1", 2, collection, session=session
    ) == policy
    call = _last(collection, "find")
    assert call[2]["session"] is session
    assert len(collection.calls) == calls_before + 1
    assert not any(operation in {"insert_one", "update_one", "delete_one", "create_index"} for operation, _, _ in collection.calls[calls_before:])


@pytest.mark.parametrize(
    "mutation",
    [
        lambda row: row.update({"policy_fingerprint": "e" * 128}),
        lambda row: row.update({"merchant_configuration_fingerprint": "f" * 128}),
        lambda row: row.update({"authoring_authorization_evidence_fingerprint": "0" * 128}),
    ],
)
def test_corrupt_highest_predecessor_fails_closed(mutation: Any) -> None:
    collection = FakeCollection()
    older = _policy(policy_version=1)
    highest = _policy(policy_version=3)
    TenantInboundProviderPolicyRegistry.create(older, collection)
    TenantInboundProviderPolicyRegistry.create(highest, collection)
    mutation(collection.rows[1])
    with pytest.raises(TenantInboundProviderPolicyPersistedRecordInvalidError):
        TenantInboundProviderPolicyRegistry.get_predecessor_policy(
            "tenant-a", "policy-1", 5, collection
        )


def test_corrupt_highest_predecessor_is_not_skipped_for_older_valid_row() -> None:
    collection = FakeCollection()
    TenantInboundProviderPolicyRegistry.create(_policy(policy_version=1), collection)
    TenantInboundProviderPolicyRegistry.create(_policy(policy_version=3), collection)
    collection.rows[1]["policy_fingerprint"] = "e" * 128
    with pytest.raises(TenantInboundProviderPolicyPersistedRecordInvalidError):
        TenantInboundProviderPolicyRegistry.get_predecessor_policy(
            "tenant-a", "policy-1", 5, collection
        )


@pytest.mark.parametrize(
    "tenant_id, policy_id, target",
    [("", "policy-1", 2), ("tenant-a", "", 2), ("tenant-a", "policy-1", 1), ("tenant-a", "policy-1", 0), ("tenant-a", "policy-1", True), ("tenant-a", "policy-1", "2")],
)
def test_predecessor_rejects_malformed_inputs(tenant_id: object, policy_id: object, target: object) -> None:
    with pytest.raises(TenantInboundProviderPolicyRegistryError):
        TenantInboundProviderPolicyRegistry.get_predecessor_policy(
            cast(str, tenant_id), cast(str, policy_id), cast(int, target), FakeCollection()
        )


def test_predecessor_does_not_create_session_or_transaction() -> None:
    collection = FakeCollection()
    assert TenantInboundProviderPolicyRegistry.get_predecessor_policy(
        "tenant-a", "policy-1", 2, collection
    ) is None
    assert not hasattr(TenantInboundProviderPolicyRegistry, "start_transaction")
    assert not hasattr(TenantInboundProviderPolicyRegistry, "commit")
    assert not hasattr(TenantInboundProviderPolicyRegistry, "abort")


def test_existing_exact_read_and_replay_contract_remain_unchanged() -> None:
    collection = FakeCollection()
    policy = _policy()
    TenantInboundProviderPolicyRegistry.create(policy, collection)
    before = len(collection.calls)
    assert TenantInboundProviderPolicyRegistry.get("tenant-a", "policy-1", 1, collection) == policy
    replay = TenantInboundProviderPolicyRegistry.create(policy, collection)
    assert replay == policy
    assert not any(operation == "insert_one" for operation, _, _ in collection.calls[before:])


def test_predecessor_public_api_does_not_add_active_or_authority_resolution() -> None:
    public = set(dir(TenantInboundProviderPolicyRegistry))
    assert not {
        "get_latest_active_policy",
        "get_current_policy",
        "resolve_provider",
        "activate",
        "deactivate",
        "authorize",
    } & public


# ARTIFACT: test_tenant_inbound_provider_policy_registry.py
# VERSION: v1.1.0-M11-R8-R3B-P8-P3C-P2-R2
# AUTHORITY BOUNDARY: direct host-free persistence and replay certificate only.
# TENANT POSTURE: tests assert tenant-scoped identity and cross-tenant isolation.
# FAIL-CLOSED POSTURE: corruption, divergence, unsupported providers, and bad lookups reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
