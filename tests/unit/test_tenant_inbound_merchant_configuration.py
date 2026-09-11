"""Wilsy OS direct certificate for tenant inbound merchant configuration P8-P2.

TITLE: Tenant Inbound Merchant Configuration Unit Certificate
VERSION: v1.2.2-M11-R8-R3B-P8-P2-P0-R1-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Host-free proof of immutable configuration identity, strict persistence, and fail-closed lifecycle CAS.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_inbound_merchant_configuration.py
COLLABORATION / OWNERSHIP: SaaS configuration domain and registry certificate owner.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.2.2-M11-R8-R3B-P8-P2-P0-R1-CERT certifies the same-document
lifecycle idempotency projection and exact tenant-wide unique index while
preserving canonical history and strict hydration.
v1.2.1-M11-R8-R3B-P8-P3B-I2-R1-R1-CERT certifies tenant-wide
lifecycle-key lookup aligned with uniqueness and divergent cross-configuration
replay rejection; prior idempotency coverage remains intact.
v1.2.0-M11-R8-R3B-P8-P3B-I2-R1-CERT certifies tenant-scoped
lifecycle-event idempotency, exact replay, and replay-before-CAS behavior;
the initial registration contract remains unchanged.
v1.1.0-M11-R8-R3B-P8-P3B-R1-CERT certifies durable initial
registration authorization provenance in addition to the existing immutable
configuration and append-only lifecycle contract without Mongo or provider calls.
v1.0.0-M11-R8-R3B-P8-P2-TENANT-INBOUND-MERCHANT-CONFIGURATION-CERT certifies the 76-gate immutable configuration and append-only lifecycle contract without Mongo or provider calls.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; raw credentials never appear in fixtures or output.
TENANT BOUNDARY: Every fixture and fake persistence predicate carries tenant_id.
AUTHORITY BOUNDARY: Certificate only; no policy, binding, checkout, payment, settlement, or paid-state authority.
TRANSACTION BOUNDARY: Fake collection accepts caller sessions and performs no network or database work.
FAIL-CLOSED DECLARATION: Tests assert strict schema, provider, fingerprint, replay, eligibility, and CAS rejection.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import dataclasses

import pytest

from tools.eos.saas.billing.tenant_inbound_merchant_configuration_registry import (
    EnablementState,
    TenantInboundMerchantConfigurationNotFoundError,
    TenantInboundMerchantConfigurationRegistry,
    TenantInboundMerchantConfigurationPersistedRecordInvalidError,
    TenantInboundMerchantConfigurationRegistryError,
    TenantInboundMerchantConfigurationReplayConflictError,
    TenantInboundMerchantConfigurationTransitionConflictError,
)
from tools.eos.saas.domain.tenant_inbound_merchant_configuration import (
    InboundMerchantProviderId,
    TenantInboundMerchantConfiguration,
    TenantInboundMerchantConfigurationError,
)


STAMP = datetime(2026, 9, 9, 8, 30, tzinfo=timezone.utc)
AUTH_FP = "a" * 128
AUTH_REF = "tenant-authorization-decision:decision-1"


class _Result:
    def __init__(self, matched_count: int = 1) -> None:
        self.matched_count = matched_count


def _read_path(row: dict[str, object], path: str) -> object:
    value: object = row
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _matches_path(value: object, parts: list[str], expected: object) -> bool:
    if not parts:
        if isinstance(value, list):
            return any(item == expected for item in value)
        return value == expected
    if isinstance(value, list):
        if len(parts) == 1:
            return any(item == expected for item in value)
        return any(_matches_path(item, parts, expected) for item in value)
    if not isinstance(value, dict):
        return False
    return _matches_path(value.get(parts[0]), parts[1:], expected)


class FakeCollection:
    """Small host-free Mongo-shaped fake; it records sessions and preserves documents."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.sessions: list[object] = []
        self.indexes: list[dict[str, object]] = []

    def create_index(self, *_args: object, **_kwargs: object) -> str:
        self.indexes.append({"key": _args[0] if _args else None, **_kwargs})
        return str(_kwargs.get("name", "index"))

    def find_one(self, query: dict[str, object], *, session: object = None) -> dict[str, object] | None:
        self.sessions.append(session)
        for row in self.rows:
            if all(_matches_path(row, key.split("."), value) for key, value in query.items()):
                return deepcopy(row)
        return None

    def insert_one(self, document: dict[str, object], *, session: object = None) -> object:
        self.sessions.append(session)
        self.rows.append(deepcopy(document))
        return object()

    def update_one(self, query: dict[str, object], update: dict[str, object], *, session: object = None) -> _Result:
        self.sessions.append(session)
        for row in self.rows:
            if all(_matches_path(row, key.split("."), value) for key, value in query.items()):
                lifecycle = update["$set"]["lifecycle"]  # type: ignore[index]
                event = update["$push"]["lifecycle_history"]  # type: ignore[index]
                projection_key = update["$push"]["lifecycle_idempotency_keys"]  # type: ignore[index]
                row["lifecycle"] = deepcopy(lifecycle)  # type: ignore[assignment]
                cast_history = row["lifecycle_history"]
                assert isinstance(cast_history, list)
                cast_history.append(deepcopy(event))
                cast_projection = row["lifecycle_idempotency_keys"]
                assert isinstance(cast_projection, list)
                cast_projection.append(deepcopy(projection_key))
                return _Result(1)
        return _Result(0)


def config(**changes: object) -> TenantInboundMerchantConfiguration:
    values: dict[str, object] = {
        "merchant_configuration_id": "config-1",
        "tenant_id": "tenant-a",
        "provider_id": InboundMerchantProviderId.PAYFAST,
        "merchant_account_id": "merchant-account-1",
        "merchant_configuration_version": 1,
        "non_secret_provider_options": {"mode": "sandbox", "currency": "ZAR"},
        "credential_secret_reference": "vault://tenant-a/payfast/primary",
        "created_at": STAMP,
    }
    values.update(changes)
    return TenantInboundMerchantConfiguration(**values)  # type: ignore[arg-type]


def test_valid_typed_payfast_identity_is_immutable_and_tenant_scoped() -> None:
    value = config()
    assert value.provider_id is InboundMerchantProviderId.PAYFAST
    assert value.tenant_id == "tenant-a"
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError, TypeError)):
        value.merchant_account_id = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        value.non_secret_provider_options["mode"] = "live"  # type: ignore[index]


@pytest.mark.parametrize("field,value", [("provider_id", "PAYFAST"), ("provider_id", "PAYSHAP"), ("tenant_id", ""), ("merchant_configuration_id", ""), ("merchant_account_id", ""), ("credential_secret_reference", "")])
def test_identity_and_provider_inputs_are_strict(field: str, value: object) -> None:
    with pytest.raises(TenantInboundMerchantConfigurationError):
        config(**{field: value})


@pytest.mark.parametrize("version", [0, -1, True, "1", "v1"])
def test_configuration_version_is_positive_typed_integer(version: object) -> None:
    with pytest.raises(TenantInboundMerchantConfigurationError):
        config(merchant_configuration_version=version)


def test_created_at_requires_aware_utc_and_domain_does_not_capture_clock() -> None:
    with pytest.raises(TenantInboundMerchantConfigurationError):
        config(created_at=datetime(2026, 9, 9))
    assert config(created_at=datetime(2026, 9, 9, 10, 30, tzinfo=timezone(timedelta(hours=2)))).created_at.tzinfo == timezone.utc


@pytest.mark.parametrize("options", [{"api_key": "x"}, {"password": "x"}, {"nested": {"value": "x"}}, {"mode": 1}, {"secret_reference": "x"}])
def test_non_secret_options_are_flat_closed_and_secret_shaped_keys_reject(options: object) -> None:
    with pytest.raises(TenantInboundMerchantConfigurationError):
        config(non_secret_provider_options=options)


def test_fingerprint_is_sha3_lowercase_deterministic_and_secret_lifecycle_neutral() -> None:
    one = config(non_secret_provider_options={"currency": "ZAR", "mode": "sandbox"})
    two = config(non_secret_provider_options={"mode": "sandbox", "currency": "ZAR"})
    assert one.fingerprint == two.fingerprint
    assert len(one.fingerprint) == 128 and one.fingerprint == one.fingerprint.lower()
    assert "secret" not in str(one._semantic_payload()).lower() or one.credential_secret_reference in str(one._semantic_payload())
    assert config(credential_secret_reference="vault://tenant-a/payfast/rotated").fingerprint != one.fingerprint
    assert one.verify_fingerprint(one.fingerprint)


def test_strict_round_trip_rejects_missing_unknown_and_forged_digest_without_autofill() -> None:
    payload = config().to_dict()
    assert TenantInboundMerchantConfiguration.from_dict(payload) == config()
    for malformed in [
        {key: value for key, value in payload.items() if key != "merchant_configuration_fingerprint"},
        {**payload, "lifecycle": "DISABLED"},
        {**payload, "merchant_configuration_fingerprint": "b" * 128},
        {**payload, "provider_id": "PAYSHAP"},
    ]:
        with pytest.raises(TenantInboundMerchantConfigurationError):
            TenantInboundMerchantConfiguration.from_dict(malformed)


def test_registry_indexes_are_tenant_scoped_and_create_starts_disabled() -> None:
    collection = FakeCollection()
    TenantInboundMerchantConfigurationRegistry.ensure_indexes(collection)  # type: ignore[arg-type]
    record = TenantInboundMerchantConfigurationRegistry.create(config(), collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    assert record.state is EnablementState.DISABLED and record.revision == 0
    assert len(record.history) == 1 and record.history[0].new_state is EnablementState.DISABLED
    assert record.history[0].authorization_reference == AUTH_REF
    assert record.history[0].authorization_evidence_fingerprint == AUTH_FP
    assert collection.rows[0]["lifecycle_idempotency_keys"] == []


def test_projection_is_derived_only_from_non_null_canonical_history_keys() -> None:
    collection = FakeCollection()
    TenantInboundMerchantConfigurationRegistry.create(config(), collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    assert collection.rows[0]["lifecycle_idempotency_keys"] == []
    TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 0, EnablementState.DISABLED, EnablementState.ENABLED, STAMP, STAMP, "approved", "auth-ref", AUTH_FP, "life-1", collection)  # type: ignore[arg-type]
    TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 1, EnablementState.ENABLED, EnablementState.SUSPENDED, STAMP, STAMP, "review", "auth-ref-2", AUTH_FP, "life-2", collection)  # type: ignore[arg-type]
    row = collection.rows[0]
    assert row["lifecycle_idempotency_keys"] == ["life-1", "life-2"]
    history = row["lifecycle_history"]
    assert isinstance(history, list)
    assert [item["lifecycle_idempotency_key"] for item in history if item["lifecycle_idempotency_key"] is not None] == row["lifecycle_idempotency_keys"]


def test_projection_index_replaces_defective_history_multikey_index() -> None:
    collection = FakeCollection()
    TenantInboundMerchantConfigurationRegistry.ensure_indexes(collection)  # type: ignore[arg-type]
    lifecycle_indexes = [index for index in collection.indexes if "lifecycle" in str(index.get("name"))]
    assert len(lifecycle_indexes) == 1
    index = lifecycle_indexes[0]
    assert index["name"] == "tenant_lifecycle_idempotency_projection_unique"
    assert index["key"] == [("configuration.tenant_id", 1), ("lifecycle_idempotency_keys", 1)]
    assert index["unique"] is True
    assert index["partialFilterExpression"] == {"lifecycle_idempotency_keys.0": {"$exists": True}}
    assert "lifecycle_history.lifecycle_idempotency_key" not in str(index["key"])


@pytest.mark.parametrize("projection", [None, "life-1", [None], [1], [""], ["   "], ["life-1", "life-1"], ["other"]])
def test_projection_is_strictly_required_and_cannot_be_forged(projection: object) -> None:
    collection = FakeCollection()
    TenantInboundMerchantConfigurationRegistry.create(config(), collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 0, EnablementState.DISABLED, EnablementState.ENABLED, STAMP, STAMP, "approved", "auth-ref", AUTH_FP, "life-1", collection)  # type: ignore[arg-type]
    collection.rows[0]["lifecycle_idempotency_keys"] = projection
    with pytest.raises(TenantInboundMerchantConfigurationPersistedRecordInvalidError):
        TenantInboundMerchantConfigurationRegistry.get("tenant-a", "config-1", 1, collection)  # type: ignore[arg-type]


def test_missing_projection_key_fails_closed_without_auto_repair() -> None:
    collection = FakeCollection()
    TenantInboundMerchantConfigurationRegistry.create(config(), collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    collection.rows[0].pop("lifecycle_idempotency_keys")
    with pytest.raises(TenantInboundMerchantConfigurationPersistedRecordInvalidError):
        TenantInboundMerchantConfigurationRegistry.get("tenant-a", "config-1", 1, collection)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "authorization_reference,authorization_evidence_fingerprint",
    [("", AUTH_FP), (AUTH_REF, ""), (AUTH_REF, "z" * 128), (AUTH_REF, "a" * 127)],
)
def test_create_requires_strict_registration_authorization_provenance(
    authorization_reference: str, authorization_evidence_fingerprint: str
) -> None:
    collection = FakeCollection()
    with pytest.raises(TenantInboundMerchantConfigurationRegistryError):
        TenantInboundMerchantConfigurationRegistry.create(
            config(),
            collection,  # type: ignore[arg-type]
            idempotency_key="create-1",
            authorization_reference=authorization_reference,
            authorization_evidence_fingerprint=authorization_evidence_fingerprint,
        )


def test_create_replay_is_exact_and_preserves_current_lifecycle_and_revision() -> None:
    collection = FakeCollection()
    value = config()
    first = TenantInboundMerchantConfigurationRegistry.create(value, collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    second = TenantInboundMerchantConfigurationRegistry.create(value, collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    assert second == first
    enabled = TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 0, EnablementState.DISABLED, EnablementState.ENABLED, STAMP, STAMP, "approved", "auth-ref", AUTH_FP, "life-1", collection)  # type: ignore[arg-type]
    replay = TenantInboundMerchantConfigurationRegistry.create(value, collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    assert replay.state is enabled.state and replay.revision == enabled.revision
    with pytest.raises(TenantInboundMerchantConfigurationReplayConflictError):
        TenantInboundMerchantConfigurationRegistry.create(config(merchant_account_id="other"), collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    with pytest.raises(TenantInboundMerchantConfigurationReplayConflictError):
        TenantInboundMerchantConfigurationRegistry.create(value, collection, idempotency_key="create-1", authorization_reference=AUTH_REF + "-different", authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]


def test_historical_get_all_states_and_cross_tenant_isolation() -> None:
    collection = FakeCollection()
    TenantInboundMerchantConfigurationRegistry.create(config(), collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    for state in (EnablementState.ENABLED, EnablementState.DISABLED, EnablementState.SUSPENDED, EnablementState.COMPROMISED, EnablementState.RETIRED):
        current = TenantInboundMerchantConfigurationRegistry.get("tenant-a", "config-1", 1, collection)  # type: ignore[arg-type]
        assert current is not None
        if current.state is EnablementState.RETIRED:
            break
        if state is current.state:
            continue
        allowed = state in {EnablementState.ENABLED, EnablementState.COMPROMISED, EnablementState.SUSPENDED, EnablementState.RETIRED} if current.state is EnablementState.DISABLED else state in {EnablementState.DISABLED, EnablementState.RETIRED}
        if allowed:
            TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, current.revision, current.state, state, STAMP, STAMP, "review", "auth-ref", AUTH_FP, f"life-{current.revision + 1}", collection)  # type: ignore[arg-type]
    assert TenantInboundMerchantConfigurationRegistry.get("tenant-a", "config-1", 1, collection) is not None  # type: ignore[arg-type]
    assert TenantInboundMerchantConfigurationRegistry.get("tenant-b", "config-1", 1, collection) is None  # type: ignore[arg-type]


def test_current_eligibility_requires_enabled_exact_revision_and_aware_trusted_time() -> None:
    collection = FakeCollection()
    TenantInboundMerchantConfigurationRegistry.create(config(), collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    with pytest.raises(TenantInboundMerchantConfigurationNotFoundError):
        TenantInboundMerchantConfigurationRegistry.get_current_eligible("tenant-a", "config-1", 1, STAMP, collection)  # type: ignore[arg-type]
    TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 0, EnablementState.DISABLED, EnablementState.ENABLED, STAMP, STAMP, "approved", "auth-ref", AUTH_FP, "life-1", collection)  # type: ignore[arg-type]
    assert TenantInboundMerchantConfigurationRegistry.get_current_eligible("tenant-a", "config-1", 1, STAMP, collection).state is EnablementState.ENABLED  # type: ignore[arg-type]
    with pytest.raises(TenantInboundMerchantConfigurationRegistryError):
        TenantInboundMerchantConfigurationRegistry.get_current_eligible("tenant-a", "config-1", 1, datetime(2026, 9, 9), collection)  # type: ignore[arg-type]
    with pytest.raises(TenantInboundMerchantConfigurationNotFoundError):
        TenantInboundMerchantConfigurationRegistry.get_current_eligible("tenant-b", "config-1", 1, STAMP, collection)  # type: ignore[arg-type]


def test_enablement_cas_requires_auth_provenance_appends_history_and_rejects_stale_or_illegal() -> None:
    collection = FakeCollection()
    TenantInboundMerchantConfigurationRegistry.create(config(), collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    with pytest.raises(TenantInboundMerchantConfigurationTransitionConflictError):
        TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 9, EnablementState.DISABLED, EnablementState.ENABLED, STAMP, STAMP, "approved", "auth-ref", AUTH_FP, "life-stale", collection)  # type: ignore[arg-type]
    with pytest.raises(TenantInboundMerchantConfigurationTransitionConflictError):
        TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 0, EnablementState.DISABLED, EnablementState.ENABLED, STAMP, STAMP, "approved", "", AUTH_FP, "life-invalid", collection)  # type: ignore[arg-type]
    changed = TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 0, EnablementState.DISABLED, EnablementState.ENABLED, STAMP, STAMP, "approved", "auth-ref", AUTH_FP, "life-1", collection)  # type: ignore[arg-type]
    assert changed.revision == 1 and len(changed.history) == 2
    assert changed.configuration.fingerprint == config().fingerprint
    with pytest.raises(TenantInboundMerchantConfigurationTransitionConflictError):
        TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 0, EnablementState.DISABLED, EnablementState.DISABLED, STAMP, STAMP, "stale", "auth-ref", AUTH_FP, "life-stale-2", collection)  # type: ignore[arg-type]
    TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 1, EnablementState.ENABLED, EnablementState.COMPROMISED, STAMP, STAMP, "incident", "auth-ref", AUTH_FP, "life-2", collection)  # type: ignore[arg-type]
    with pytest.raises(TenantInboundMerchantConfigurationTransitionConflictError):
        TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 2, EnablementState.COMPROMISED, EnablementState.ENABLED, STAMP, STAMP, "resurrect", "auth-ref", AUTH_FP, "life-3", collection)  # type: ignore[arg-type]


def test_lifecycle_idempotency_is_required_stored_fingerprinted_and_tenant_scoped() -> None:
    collection = FakeCollection()
    TenantInboundMerchantConfigurationRegistry.create(config(), collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    with pytest.raises(TenantInboundMerchantConfigurationTransitionConflictError):
        TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 0, EnablementState.DISABLED, EnablementState.ENABLED, STAMP, STAMP, "approved", "auth-ref", AUTH_FP, "", collection)  # type: ignore[arg-type]
    changed = TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 0, EnablementState.DISABLED, EnablementState.ENABLED, STAMP, STAMP, "approved", "auth-ref", AUTH_FP, "life-1", collection)  # type: ignore[arg-type]
    event = changed.history[-1]
    assert event.lifecycle_idempotency_key == "life-1"
    assert "lifecycle_idempotency_key" in event.to_dict()
    assert TenantInboundMerchantConfigurationRegistry.get_lifecycle_event_by_idempotency_key("tenant-a", "life-1", collection)[1] == event  # type: ignore[index,arg-type]
    assert TenantInboundMerchantConfigurationRegistry.get_lifecycle_event_by_idempotency_key("tenant-b", "life-1", collection) is None  # type: ignore[arg-type]


@pytest.mark.parametrize("key", ["", " ", "\t", None, 1])
def test_lifecycle_idempotency_key_rejects_empty_and_malformed_values(key: object) -> None:
    collection = FakeCollection()
    TenantInboundMerchantConfigurationRegistry.create(config(), collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    with pytest.raises(TenantInboundMerchantConfigurationTransitionConflictError):
        TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 0, EnablementState.DISABLED, EnablementState.ENABLED, STAMP, STAMP, "approved", "auth-ref", AUTH_FP, key, collection)  # type: ignore[arg-type]


def test_exact_lifecycle_replay_is_read_only_and_later_history_wins() -> None:
    collection = FakeCollection()
    TenantInboundMerchantConfigurationRegistry.create(config(), collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    first = TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 0, EnablementState.DISABLED, EnablementState.ENABLED, STAMP, STAMP, "approved", "auth-ref", AUTH_FP, "life-1", collection)  # type: ignore[arg-type]
    later = TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 1, EnablementState.ENABLED, EnablementState.SUSPENDED, STAMP, STAMP, "review", "auth-ref-2", AUTH_FP, "life-2", collection)  # type: ignore[arg-type]
    before = deepcopy(collection.rows[0])
    replay = TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 0, EnablementState.DISABLED, EnablementState.ENABLED, STAMP, STAMP, "approved", "auth-ref", AUTH_FP, "life-1", collection)  # type: ignore[arg-type]
    assert replay == later
    assert replay.revision == 2 and replay.state is EnablementState.SUSPENDED
    assert len(replay.history) == 3 and replay.history[1] == first.history[1]
    assert collection.rows[0] == before


def test_tenant_wide_key_collision_hits_original_config_and_never_enters_fresh_path() -> None:
    collection = FakeCollection()
    TenantInboundMerchantConfigurationRegistry.create(config(), collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 0, EnablementState.DISABLED, EnablementState.ENABLED, STAMP, STAMP, "approved", "auth-ref", AUTH_FP, "life-1", collection)  # type: ignore[arg-type]
    TenantInboundMerchantConfigurationRegistry.create(config(merchant_configuration_id="config-b"), collection, idempotency_key="create-2", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    before = deepcopy(collection.rows)
    with pytest.raises(TenantInboundMerchantConfigurationReplayConflictError):
        TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-b", 1, 0, EnablementState.DISABLED, EnablementState.ENABLED, STAMP, STAMP, "approved", "new-auth", AUTH_FP, "life-1", collection)  # type: ignore[arg-type]
    assert collection.rows == before


@pytest.mark.parametrize(
    "changes",
    [
        {"expected_revision": 9},
        {"expected_prior_state": EnablementState.ENABLED},
        {"new_state": EnablementState.SUSPENDED},
        {"reason_reference": "different"},
        {"authorization_reference": "different-auth"},
        {"authorization_evidence_fingerprint": "b" * 128},
        {"lifecycle_idempotency_key": "life-other"},
    ],
)
def test_divergent_lifecycle_replay_intent_or_provenance_fails_closed(changes: dict[str, object]) -> None:
    collection = FakeCollection()
    TenantInboundMerchantConfigurationRegistry.create(config(), collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 0, EnablementState.DISABLED, EnablementState.ENABLED, STAMP, STAMP, "approved", "auth-ref", AUTH_FP, "life-1", collection)  # type: ignore[arg-type]
    args: dict[str, object] = {"expected_revision": 0, "expected_prior_state": EnablementState.DISABLED, "new_state": EnablementState.ENABLED, "reason_reference": "approved", "authorization_reference": "auth-ref", "authorization_evidence_fingerprint": AUTH_FP, "lifecycle_idempotency_key": "life-1"}
    args.update(changes)
    with pytest.raises((TenantInboundMerchantConfigurationReplayConflictError, TenantInboundMerchantConfigurationTransitionConflictError)):
        TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, args["expected_revision"], args["expected_prior_state"], args["new_state"], STAMP, STAMP, args["reason_reference"], args["authorization_reference"], args["authorization_evidence_fingerprint"], args["lifecycle_idempotency_key"], collection)  # type: ignore[arg-type]


def test_hydration_rejects_altered_or_legacy_event_without_key_and_never_backfills() -> None:
    collection = FakeCollection()
    TenantInboundMerchantConfigurationRegistry.create(config(), collection, idempotency_key="create-1", authorization_reference=AUTH_REF, authorization_evidence_fingerprint=AUTH_FP)  # type: ignore[arg-type]
    TenantInboundMerchantConfigurationRegistry.transition_enablement("tenant-a", "config-1", 1, 0, EnablementState.DISABLED, EnablementState.ENABLED, STAMP, STAMP, "approved", "auth-ref", AUTH_FP, "life-1", collection)  # type: ignore[arg-type]
    collection.rows[0]["lifecycle_history"][1]["lifecycle_idempotency_key"] = "tampered"  # type: ignore[index]
    with pytest.raises(TenantInboundMerchantConfigurationPersistedRecordInvalidError):
        TenantInboundMerchantConfigurationRegistry.get("tenant-a", "config-1", 1, collection)  # type: ignore[arg-type]
    collection.rows[0]["lifecycle_history"][1].pop("lifecycle_idempotency_key")  # type: ignore[index]
    with pytest.raises(TenantInboundMerchantConfigurationPersistedRecordInvalidError):
        TenantInboundMerchantConfigurationRegistry.get("tenant-a", "config-1", 1, collection)  # type: ignore[arg-type]


def test_security_and_authority_boundaries_are_structural() -> None:
    import pathlib
    domain_text = pathlib.Path(__file__).parents[2].joinpath("tools/eos/saas/domain/tenant_inbound_merchant_configuration.py").read_text()
    registry_text = pathlib.Path(__file__).parents[2].joinpath("tools/eos/saas/billing/tenant_inbound_merchant_configuration_registry.py").read_text()
    for text in (domain_text, registry_text):
        assert "billing_registry" not in text
        assert "payfastService" not in text.lower()
        assert "payshap" not in text.lower()
        assert "ClientInvoice" not in text
        assert "connect_db()" not in text
    assert "provider_policy" not in domain_text.lower()


# ARTIFACT: test_tenant_inbound_merchant_configuration.py
# VERSION: v1.2.2-M11-R8-R3B-P8-P2-P0-R1-CERT
# AUTHORITY BOUNDARY: host-free evidence only; no admin, routing, provider, payment, or settlement authority.
# FAIL-CLOSED POSTURE: all malformed identity, replay, lifecycle, tenant, and security inputs are rejected.
# END OF WILSY OS SOVEREIGN ARTIFACT
