"""TITLE: Accounts Payable Provider Selection Decision Registry Certificate.
VERSION: v1.0.1-M11-P5-R1B-AP2D-R2A.
AUTHORITY: Direct unit certification of AP2D durable persistence.
EPITOME: Proves tenant/session safety, strict hydration, replay, and corruption rejection.
ABSOLUTE CANONICAL PATH: tests/unit/test_accounts_payable_provider_selection_decision_registry.py
COLLABORATION / OWNERSHIP: Kennel EOS AP2D registry certification.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.1 certifies tenant/request uniqueness, race adjudication, replay, and strict hydration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Synthetic tenant-scoped persistence fixtures only.
AUTHORITY BOUNDARY: Certificate evidence only; no orchestration, provider, or Mongo runtime.
"""
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.kennel.domain.accounts_payable_provider_selection_decision import (
    AccountsPayableProviderSelectionDecision,
)
from tools.eos.kennel.registry.accounts_payable_provider_selection_decision_registry import (
    AccountsPayableProviderSelectionDecisionRegistry,
    AccountsPayableProviderSelectionDecisionRegistryError,
)


FINGERPRINT_A = "a" * 128
FINGERPRINT_B = "b" * 128
FINGERPRINT_C = "c" * 128


class Session:
    """Minimal caller-owned transaction marker used by the direct certificate."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class InsertResult:
    """Minimal insert result marker for the persistence fixture."""


class Collection:
    """Deterministic in-memory collection that records all caller sessions."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.sessions: list[object] = []
        self.indexes: list[dict[str, object]] = []
        self.duplicate_on_insert = False
        self.duplicate_winner: dict[str, object] | None = None

    def create_index(self, keys: list[tuple[str, int]], **kwargs: object) -> str:
        self.indexes.append({"keys": keys, **kwargs})
        return str(kwargs.get("name", "index"))

    def find_one(self, query: dict[str, object], *, session: object = None) -> dict[str, object] | None:
        self.sessions.append(session)
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return row
        return None

    def find(self, query: dict[str, object], *, session: object = None) -> list[dict[str, object]]:
        self.sessions.append(session)
        return [row for row in self.rows if all(row.get(key) == value for key, value in query.items())]

    def insert_one(self, row: dict[str, object], *, session: object = None) -> InsertResult:
        self.sessions.append(session)
        if self.duplicate_on_insert:
            if self.duplicate_winner is not None:
                self.rows.append(dict(self.duplicate_winner))
            raise DuplicateKeyError("request-level duplicate")
        self.rows.append(dict(row))
        return InsertResult()


def make_decision(**overrides: object) -> AccountsPayableProviderSelectionDecision:
    """Build only synthetic persisted values; production registry owns all semantics."""
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "execution_request_id": "request-a",
        "execution_request_fingerprint": FINGERPRINT_A,
        "runtime_binding_id": "binding-a",
        "runtime_binding_revision": 1,
        "runtime_binding_fingerprint": FINGERPRINT_B,
        "provider_policy_id": "policy-a",
        "provider_policy_revision": 1,
        "provider_policy_fingerprint": FINGERPRINT_C,
        "selected_provider": "PAYSHAP",
    }
    values.update(overrides)
    return AccountsPayableProviderSelectionDecision(**values)  # type: ignore[arg-type]


def setup() -> tuple[Collection, Session, AccountsPayableProviderSelectionDecision]:
    """Return an empty collection, active caller session, and canonical decision."""
    collection = Collection()
    session = Session()
    decision = make_decision()
    return collection, session, decision


def test_canonical_persist_and_readback() -> None:
    collection, session, decision = setup()
    stored, replayed = AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    readback = AccountsPayableProviderSelectionDecisionRegistry.get(decision.tenant_id, decision.selection_decision_id, collection, session=session)
    assert stored == decision and replayed is False and readback == decision


def test_unique_index_is_tenant_and_selection_identity() -> None:
    collection, _, _ = setup()
    AccountsPayableProviderSelectionDecisionRegistry.ensure_indexes(collection)
    assert collection.indexes == [
        {"keys": [("tenant_id", 1), ("selection_decision_id", 1)], "unique": True, "name": "accounts_payable_provider_selection_decision_unique"},
        {"keys": [("tenant_id", 1), ("execution_request_id", 1)], "unique": True, "name": "accounts_payable_provider_selection_request_unique"},
    ]


def test_insert_and_read_propagate_caller_session() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    AccountsPayableProviderSelectionDecisionRegistry.get(decision.tenant_id, decision.selection_decision_id, collection, session=session)
    assert collection.sessions == [session, session, session, session]


@pytest.mark.parametrize("operation", ["create", "get", "get_by_request"])
def test_missing_transaction_rejects(operation: str) -> None:
    collection, _, decision = setup()
    with pytest.raises(AccountsPayableProviderSelectionDecisionRegistryError, match="ACTIVE_TRANSACTION_REQUIRED"):
        if operation == "create":
            AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection)
        elif operation == "get":
            AccountsPayableProviderSelectionDecisionRegistry.get("tenant-a", decision.selection_decision_id, collection)
        else:
            AccountsPayableProviderSelectionDecisionRegistry.get_by_request("tenant-a", decision.execution_request_id, collection)


@pytest.mark.parametrize("operation", ["create", "get", "get_by_request"])
def test_inactive_transaction_rejects(operation: str) -> None:
    collection, session, decision = setup()
    session.in_transaction = False
    with pytest.raises(AccountsPayableProviderSelectionDecisionRegistryError, match="ACTIVE_TRANSACTION_REQUIRED"):
        if operation == "create":
            AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
        elif operation == "get":
            AccountsPayableProviderSelectionDecisionRegistry.get("tenant-a", decision.selection_decision_id, collection, session=session)
        else:
            AccountsPayableProviderSelectionDecisionRegistry.get_by_request("tenant-a", decision.execution_request_id, collection, session=session)


def test_exact_replay_returns_existing_canonical_fact_without_second_row() -> None:
    collection, session, decision = setup()
    first, first_replayed = AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    second, second_replayed = AccountsPayableProviderSelectionDecisionRegistry.create(make_decision(), collection, session=session)
    assert first_replayed is False and second_replayed is True
    assert second == first and len(collection.rows) == 1


def test_exact_replay_does_not_mutate_existing_row() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    before = dict(collection.rows[0])
    AccountsPayableProviderSelectionDecisionRegistry.create(make_decision(), collection, session=session)
    assert collection.rows[0] == before


def test_get_by_request_returns_exact_canonical_selection_with_session() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    readback = AccountsPayableProviderSelectionDecisionRegistry.get_by_request(
        "tenant-a", "request-a", collection, session=session
    )
    assert readback == decision
    assert collection.sessions[-1] is session


def test_get_by_request_is_exactly_tenant_scoped() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    assert AccountsPayableProviderSelectionDecisionRegistry.get_by_request(
        "tenant-b", "request-a", collection, session=session
    ) is None
    assert AccountsPayableProviderSelectionDecisionRegistry.get_by_request(
        "tenant-a", "request-b", collection, session=session
    ) is None


def test_same_request_different_binding_is_rejected_without_overwrite() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    successor = make_decision(runtime_binding_id="binding-b", runtime_binding_revision=2)
    with pytest.raises(
        AccountsPayableProviderSelectionDecisionRegistryError,
        match="REQUEST_ALREADY_HAS_CANONICAL_SELECTION",
    ):
        AccountsPayableProviderSelectionDecisionRegistry.create(successor, collection, session=session)
    assert len(collection.rows) == 1 and collection.rows[0]["runtime_binding_id"] == "binding-a"


def test_same_request_different_policy_is_rejected_without_overwrite() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    successor = make_decision(provider_policy_id="policy-b", provider_policy_revision=2)
    with pytest.raises(
        AccountsPayableProviderSelectionDecisionRegistryError,
        match="REQUEST_ALREADY_HAS_CANONICAL_SELECTION",
    ):
        AccountsPayableProviderSelectionDecisionRegistry.create(successor, collection, session=session)
    assert len(collection.rows) == 1 and collection.rows[0]["provider_policy_id"] == "policy-a"


def test_same_request_same_provider_new_binding_is_still_rejected() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    successor = make_decision(runtime_binding_id="binding-b", runtime_binding_revision=2, selected_provider="PAYSHAP")
    with pytest.raises(
        AccountsPayableProviderSelectionDecisionRegistryError,
        match="REQUEST_ALREADY_HAS_CANONICAL_SELECTION",
    ):
        AccountsPayableProviderSelectionDecisionRegistry.create(successor, collection, session=session)


def test_cross_tenant_same_request_has_independent_canonical_selection() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    other_tenant = make_decision(tenant_id="tenant-b")
    stored, replayed = AccountsPayableProviderSelectionDecisionRegistry.create(other_tenant, collection, session=session)
    assert stored == other_tenant and replayed is False and len(collection.rows) == 2


def test_multiple_request_rows_reject_without_first_or_latest_fallback() -> None:
    collection, session, decision = setup()
    first = decision.to_persisted()
    second = make_decision(runtime_binding_id="binding-b", runtime_binding_revision=2).to_persisted()
    collection.rows.extend([first, second])
    with pytest.raises(
        AccountsPayableProviderSelectionDecisionRegistryError,
        match="MULTIPLE_REQUEST_SELECTION_ROWS",
    ):
        AccountsPayableProviderSelectionDecisionRegistry.get_by_request("tenant-a", "request-a", collection, session=session)


def test_request_lookup_fingerprint_corruption_rejects_strictly() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    collection.rows[0]["selection_decision_fingerprint"] = "f" * 128
    with pytest.raises(AccountsPayableProviderSelectionDecisionRegistryError, match="PERSISTED_RECORD_INVALID"):
        AccountsPayableProviderSelectionDecisionRegistry.get_by_request("tenant-a", "request-a", collection, session=session)


def test_request_lookup_covered_field_corruption_rejects_strictly() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    collection.rows[0]["selected_provider"] = "CARD"
    with pytest.raises(AccountsPayableProviderSelectionDecisionRegistryError, match="PERSISTED_RECORD_INVALID"):
        AccountsPayableProviderSelectionDecisionRegistry.get_by_request("tenant-a", "request-a", collection, session=session)


def test_request_lookup_missing_field_rejects_without_default() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    del collection.rows[0]["provider_policy_fingerprint"]
    with pytest.raises(AccountsPayableProviderSelectionDecisionRegistryError, match="PERSISTED_RECORD_INVALID"):
        AccountsPayableProviderSelectionDecisionRegistry.get_by_request("tenant-a", "request-a", collection, session=session)


def test_request_lookup_decision_id_corruption_rejects_strictly() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    collection.rows[0]["selection_decision_id"] = "f" * 128
    with pytest.raises(AccountsPayableProviderSelectionDecisionRegistryError, match="PERSISTED_RECORD_INVALID"):
        AccountsPayableProviderSelectionDecisionRegistry.get_by_request("tenant-a", "request-a", collection, session=session)


def test_duplicate_request_race_rejects_loser_and_preserves_winner() -> None:
    collection, session, winner = setup()
    loser = make_decision(runtime_binding_id="binding-b", runtime_binding_revision=2)
    collection.duplicate_on_insert = True
    collection.duplicate_winner = winner.to_persisted()
    with pytest.raises(
        AccountsPayableProviderSelectionDecisionRegistryError,
        match="REQUEST_ALREADY_HAS_CANONICAL_SELECTION",
    ):
        AccountsPayableProviderSelectionDecisionRegistry.create(loser, collection, session=session)
    assert len(collection.rows) == 1 and collection.rows[0]["selection_decision_id"] == winner.selection_decision_id


def test_duplicate_request_race_exact_winner_is_exact_replay() -> None:
    collection, session, decision = setup()
    collection.duplicate_on_insert = True
    collection.duplicate_winner = decision.to_persisted()
    stored, replayed = AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    assert stored == decision and replayed is True and len(collection.rows) == 1


def test_duplicate_request_race_same_slot_divergent_fingerprint_rejects() -> None:
    collection, session, winner = setup()
    loser = make_decision(selected_provider="CARD")
    assert loser.selection_decision_id == winner.selection_decision_id
    collection.duplicate_on_insert = True
    collection.duplicate_winner = winner.to_persisted()
    with pytest.raises(
        AccountsPayableProviderSelectionDecisionRegistryError,
        match="REPLAY_CONFLICT",
    ):
        AccountsPayableProviderSelectionDecisionRegistry.create(loser, collection, session=session)
    assert len(collection.rows) == 1 and collection.rows[0]["selected_provider"] == "PAYSHAP"


def test_duplicate_request_without_readable_winner_fails_closed() -> None:
    collection, session, decision = setup()
    collection.duplicate_on_insert = True
    with pytest.raises(
        AccountsPayableProviderSelectionDecisionRegistryError,
        match="PERSISTENCE_FAILED",
    ):
        AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    assert collection.rows == []


def test_divergent_same_slot_different_provider_rejects_without_second_row() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    divergent = make_decision(selected_provider="CARD")
    assert divergent.selection_decision_id == decision.selection_decision_id
    assert divergent.selection_decision_fingerprint != decision.selection_decision_fingerprint
    with pytest.raises(AccountsPayableProviderSelectionDecisionRegistryError, match="REPLAY_CONFLICT"):
        AccountsPayableProviderSelectionDecisionRegistry.create(divergent, collection, session=session)
    assert len(collection.rows) == 1 and collection.rows[0]["selected_provider"] == "PAYSHAP"


def test_divergent_replay_does_not_mutate_provider_or_use_last_write_wins() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    with pytest.raises(AccountsPayableProviderSelectionDecisionRegistryError):
        AccountsPayableProviderSelectionDecisionRegistry.create(make_decision(selected_provider="CARD"), collection, session=session)
    assert collection.rows[0]["selected_provider"] == "PAYSHAP"


def test_durable_selection_fingerprint_corruption_rejects_without_rewrite() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    collection.rows[0]["selection_decision_fingerprint"] = "f" * 128
    with pytest.raises(AccountsPayableProviderSelectionDecisionRegistryError, match="PERSISTED_RECORD_INVALID"):
        AccountsPayableProviderSelectionDecisionRegistry.get("tenant-a", decision.selection_decision_id, collection, session=session)
    assert collection.rows[0]["selection_decision_fingerprint"] == "f" * 128


def test_fingerprint_covered_field_corruption_rejects_without_normalization() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    collection.rows[0]["selected_provider"] = "CARD"
    with pytest.raises(AccountsPayableProviderSelectionDecisionRegistryError, match="PERSISTED_RECORD_INVALID"):
        AccountsPayableProviderSelectionDecisionRegistry.get("tenant-a", decision.selection_decision_id, collection, session=session)
    assert collection.rows[0]["selected_provider"] == "CARD"


def test_stored_selection_id_corruption_rejects() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    collection.rows[0]["selection_decision_id"] = "f" * 128
    with pytest.raises(AccountsPayableProviderSelectionDecisionRegistryError, match="PERSISTED_RECORD_INVALID"):
        AccountsPayableProviderSelectionDecisionRegistry._hydrate(collection.rows[0])


def test_missing_mandatory_persisted_field_rejects_without_default() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    del collection.rows[0]["provider_policy_fingerprint"]
    with pytest.raises(AccountsPayableProviderSelectionDecisionRegistryError, match="PERSISTED_RECORD_INVALID"):
        AccountsPayableProviderSelectionDecisionRegistry.get("tenant-a", decision.selection_decision_id, collection, session=session)
    assert "provider_policy_fingerprint" not in collection.rows[0]


def test_cross_tenant_lookup_does_not_leak_selection() -> None:
    collection, session, decision = setup()
    AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    assert AccountsPayableProviderSelectionDecisionRegistry.get("tenant-b", decision.selection_decision_id, collection, session=session) is None


def test_same_request_different_binding_is_identity_only_not_issuance_authority() -> None:
    first = make_decision(runtime_binding_id="binding-a", runtime_binding_revision=1)
    second = make_decision(runtime_binding_id="binding-b", runtime_binding_revision=2)
    assert first.selection_decision_id != second.selection_decision_id


def test_registry_does_not_select_provider_or_resolve_external_authority() -> None:
    collection, session, decision = setup()
    stored, _ = AccountsPayableProviderSelectionDecisionRegistry.create(decision, collection, session=session)
    assert stored.selected_provider == decision.selected_provider
    assert set(collection.rows[0]) == set(decision.to_persisted())


# ARTIFACT: test_accounts_payable_provider_selection_decision_registry.py
# VERSION: v1.0.1-M11-P5-R1B-AP2D-R2A
# AUTHORITY BOUNDARY: direct AP selection-registry certificate only
# TENANT POSTURE: synthetic tenant-scoped fixtures; no Mongo
# FAIL-CLOSED POSTURE: corruption, missing transaction, and divergent replay reject
# END OF WILSY OS SOVEREIGN ARTIFACT
