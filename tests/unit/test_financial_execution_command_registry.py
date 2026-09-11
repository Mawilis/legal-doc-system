"""Direct unit certificate for strict generic-command persistence.

TITLE: Financial Execution Command Registry Unit Certification
VERSION: v2.1.0-M11-P5-R2B-R1
AUTHORITY: Certification evidence only; Kennel EOS owns execution truth.
EPITOME: Prove immutable tenant-scoped persistence of complete typed command authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_financial_execution_command_registry.py
COLLABORATION / OWNERSHIP: Kennel EOS generic command registry certification.
CERTIFICATION / UPDATE DATE: 2026-09-08
CHANGELOG: v2.1.0-M11-P5-R2B-R1 certifies family-scoped source-request uniqueness, strict lookup, and duplicate-key race protection without Mongo.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every fake collection query is tenant-scoped.
FINANCIAL TRUTH BOUNDARY: No execution, provider, attempt, truth, settlement, or receivable mutation.
AUTHORITY BOUNDARY: Certification evidence only; the registry grants no provider or execution authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution truth; this test creates no financial truth.
TRANSACTION BOUNDARY: Fake caller sessions are observed; registry owns no transaction lifecycle.
"""
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import pytest

from pymongo.errors import DuplicateKeyError

from tools.eos.kennel.domain.financial_execution_command import AccountsPayableCommandSource, FinancialExecutionCommand, FinancialExecutionCommandFamily, PlatformBillingCommandSource
from tools.eos.kennel.registry.financial_execution_command_registry import (
    FinancialExecutionCommandCreateConflictError,
    FinancialExecutionCommandNotFoundError,
    FinancialExecutionCommandPersistedRecordInvalidError,
    FinancialExecutionCommandRegistryError,
    FinancialExecutionCommandRegistry,
)

NOW = datetime(2026, 9, 7, 10, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128


def ap_source(**changes: object) -> AccountsPayableCommandSource:
    values: dict[str, Any] = {"execution_request_id": "ap-request", "execution_request_fingerprint": FP_A, "selection_decision_id": "selection-1", "selection_decision_fingerprint": FP_B, "payable_id": "payable-1", "release_authorization_id": "release-1", "authorized_provider_name": "PAYSHAP"}
    values.update(changes)
    return AccountsPayableCommandSource(**values)


def platform_source(**changes: object) -> PlatformBillingCommandSource:
    values: dict[str, Any] = {"execution_request_id": "platform-request", "execution_request_fingerprint": FP_A, "routing_decision_id": "routing-1", "routing_decision_fingerprint": FP_B, "platform_invoice_id": "invoice-1", "release_authorization_id": "release-platform", "release_authorization_fingerprint": FP_C, "authorized_provider_name": "STRIPE"}
    values.update(changes)
    return PlatformBillingCommandSource(**values)


def command(**changes: object) -> FinancialExecutionCommand:
    source: Any = changes.pop("source_authority", ap_source())
    values: dict[str, Any] = {"tenant_id": "tenant-1", "execution_command_id": "command-1", "idempotency_key": "idem-1", "amount_minor": 1000, "currency": "ZAR", "payment_destination_reference": "destination-ref", "source_authority": source, "provider_name": source.authorized_provider_name, "created_at": NOW, "provider_metadata_reference": "metadata-ref"}
    values.update(changes)
    return FinancialExecutionCommand(**values)


def dotted(row: dict[str, Any], path: str) -> Any:
    value: Any = row
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def matches(row: dict[str, Any], query: dict[str, Any]) -> bool:
    return all(dotted(row, key) == value for key, value in query.items())


class Cursor:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def sort(self, keys: list[tuple[str, int]]) -> "Cursor":
        for key, direction in reversed(keys):
            self.rows.sort(key=lambda row: dotted(row, key), reverse=direction < 0)
        return self

    def limit(self, amount: int) -> list[dict[str, Any]]:
        return self.rows[:amount]

    def __iter__(self):
        return iter(self.rows)


class Result:
    def __init__(self, upserted_id: object) -> None:
        self.upserted_id = upserted_id


class FakeCollection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[tuple[Any, ...]] = []
        self.sessions: list[object] = []
        self.transactions = 0
        self.duplicate_source_once = False
        self.hide_source_reads = 0
        self.race_winner: dict[str, Any] | None = None

    def create_index(self, keys: Any, **kwargs: Any) -> str:
        self.indexes.append((keys, kwargs))
        return str(kwargs.get("name", "index"))

    def update_one(self, query: dict[str, Any], update: dict[str, Any], *, upsert: bool, session: object = None) -> Result:
        self.sessions.append(session)
        if self.duplicate_source_once:
            self.duplicate_source_once = False
            if self.race_winner is not None:
                self.rows.append(deepcopy(self.race_winner))
            raise DuplicateKeyError("duplicate source-request key")
        for row in self.rows:
            if matches(row, query):
                return Result(None)
        row = deepcopy(update["$setOnInsert"])
        row["_id"] = f"id-{len(self.rows) + 1}"
        self.rows.append(row)
        return Result(row["_id"])

    def find_one(self, query: dict[str, Any], *, session: object = None) -> dict[str, Any] | None:
        self.sessions.append(session)
        for row in self.rows:
            if matches(row, query):
                return deepcopy(row)
        return None

    def find(self, query: dict[str, Any], *, session: object = None) -> Cursor:
        self.sessions.append(session)
        if "source_authority.execution_request_id" in query and self.hide_source_reads:
            self.hide_source_reads -= 1
            return Cursor([])
        return Cursor([deepcopy(row) for row in self.rows if matches(row, query)])


def test_indexes_preserve_identity_and_timeline() -> None:
    collection = FakeCollection()
    FinancialExecutionCommandRegistry.ensure_indexes(collection)  # type: ignore[arg-type]
    names = {kwargs["name"] for _, kwargs in collection.indexes}
    assert names == {"tenant_execution_command_identity_unique", "tenant_family_source_execution_request_unique", "tenant_payable_commands_timeline", "tenant_release_authorization_commands_timeline"}
    source_spec = next(spec for spec in collection.indexes if spec[1]["name"] == "tenant_family_source_execution_request_unique")
    assert source_spec[0] == [("tenant_id", 1), ("source_authority_kind", 1), ("source_authority.execution_request_id", 1)]
    assert source_spec[1]["unique"] is True


def test_create_and_get_ap() -> None:
    collection = FakeCollection()
    item = command()
    assert FinancialExecutionCommandRegistry.create(item, collection).outcome == "CREATED"  # type: ignore[arg-type]
    assert FinancialExecutionCommandRegistry.get("tenant-1", "command-1", collection) == item  # type: ignore[arg-type]


def test_create_and_get_platform() -> None:
    collection = FakeCollection()
    item = command(source_authority=platform_source(), provider_name="STRIPE")
    FinancialExecutionCommandRegistry.create(item, collection)  # type: ignore[arg-type]
    assert FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection) == item  # type: ignore[arg-type]


def test_exact_replay_does_not_add_row() -> None:
    collection = FakeCollection()
    item = command()
    FinancialExecutionCommandRegistry.create(item, collection)  # type: ignore[arg-type]
    assert FinancialExecutionCommandRegistry.create(item, collection).outcome == "IDEMPOTENT_REPLAY"  # type: ignore[arg-type]
    assert len(collection.rows) == 1


@pytest.mark.parametrize("change", [{"amount_minor": 2}, {"family": "PLATFORM_BILLING"}, {"provider_name": "OTHER"}])
def test_divergent_replay_rejected(change: dict[str, object]) -> None:
    collection = FakeCollection()
    item = command()
    FinancialExecutionCommandRegistry.create(item, collection)  # type: ignore[arg-type]
    with pytest.raises((FinancialExecutionCommandCreateConflictError, ValueError)):
        if "family" in change:
            other = command(source_authority=platform_source(), provider_name="STRIPE")
        else:
            other = command(**change)
        FinancialExecutionCommandRegistry.create(other, collection)  # type: ignore[arg-type]


def test_same_command_id_is_tenant_scoped() -> None:
    collection = FakeCollection()
    FinancialExecutionCommandRegistry.create(command(), collection)  # type: ignore[arg-type]
    FinancialExecutionCommandRegistry.create(command(tenant_id="tenant-2"), collection)  # type: ignore[arg-type]
    assert len(collection.rows) == 2


def test_missing_tenant_command_is_not_found() -> None:
    with pytest.raises(FinancialExecutionCommandNotFoundError):
        FinancialExecutionCommandRegistry.get("tenant-2", "missing", FakeCollection())  # type: ignore[arg-type]


def test_list_for_payable_uses_nested_ap_subject() -> None:
    collection = FakeCollection()
    FinancialExecutionCommandRegistry.create(command(execution_command_id="a"), collection)  # type: ignore[arg-type]
    FinancialExecutionCommandRegistry.create(command(execution_command_id="b", created_at=NOW.replace(hour=11), source_authority=ap_source(execution_request_id="ap-request-b")), collection)  # type: ignore[arg-type]
    FinancialExecutionCommandRegistry.create(command(execution_command_id="c", source_authority=ap_source(payable_id="other", execution_request_id="ap-request-c")), collection)  # type: ignore[arg-type]
    rows = FinancialExecutionCommandRegistry.list_for_payable("tenant-1", "payable-1", collection=collection)  # type: ignore[arg-type]
    assert [row.execution_command_id for row in rows] == ["a", "b"]


@pytest.mark.parametrize("limit", [0, 251, True, "10"])
def test_list_bounds_fail_closed(limit: object) -> None:
    with pytest.raises(Exception):
        FinancialExecutionCommandRegistry.list_for_payable("tenant-1", "payable-1", limit=limit, collection=FakeCollection())  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["command_fingerprint", "currency", "source_authority_kind", "source_authority"])
def test_corruption_fails_on_get(field: str) -> None:
    collection = FakeCollection()
    item = command()
    FinancialExecutionCommandRegistry.create(item, collection)  # type: ignore[arg-type]
    if field == "command_fingerprint":
        collection.rows[0][field] = "f" * 128
    elif field == "currency":
        collection.rows[0][field] = "BAD"
    elif field == "source_authority_kind":
        collection.rows[0][field] = "UNKNOWN"
    else:
        collection.rows[0][field] = {"source_authority_kind": "ACCOUNTS_PAYABLE"}
    with pytest.raises(FinancialExecutionCommandPersistedRecordInvalidError):
        FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection)  # type: ignore[arg-type]


@pytest.mark.parametrize("mutation", [lambda row: row.pop("source_authority_kind"), lambda row: row["source_authority"].pop("selection_decision_id"), lambda row: row["source_authority"].update({"source_authority_kind": "PLATFORM_BILLING"}), lambda row: row.update({"requested_provider": "PAYSHAP"}), lambda row: row.update({"unknown": 1})])
def test_incomplete_unknown_mixed_and_legacy_rows_rejected(mutation: object) -> None:
    collection = FakeCollection()
    item = command()
    FinancialExecutionCommandRegistry.create(item, collection)  # type: ignore[arg-type]
    mutation(collection.rows[0])  # type: ignore[operator]
    with pytest.raises(FinancialExecutionCommandPersistedRecordInvalidError):
        FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection)  # type: ignore[arg-type]


def test_platform_missing_routing_or_invoice_is_rejected() -> None:
    collection = FakeCollection()
    item = command(source_authority=platform_source(), provider_name="STRIPE")
    FinancialExecutionCommandRegistry.create(item, collection)  # type: ignore[arg-type]
    collection.rows[0]["source_authority"].pop("routing_decision_id")
    with pytest.raises(FinancialExecutionCommandPersistedRecordInvalidError):
        FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection)  # type: ignore[arg-type]


def test_session_is_propagated_and_registry_does_not_start_transactions() -> None:
    collection = FakeCollection()
    session = object()
    item = command()
    FinancialExecutionCommandRegistry.create(item, collection, session=session)  # type: ignore[arg-type]
    FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection, session=session)  # type: ignore[arg-type]
    assert collection.sessions == [session, session, session]
    assert collection.transactions == 0


def test_platform_rows_do_not_gain_ap_payable_subject() -> None:
    item = command(source_authority=platform_source(), provider_name="STRIPE")
    assert "payable_id" not in item.to_persisted()["source_authority"]  # type: ignore[operator]


def test_no_client_invoice_or_settlement_fields_are_persisted() -> None:
    row = command().to_persisted()
    assert "client_invoice_id" not in row
    assert "settlement_state" not in row


@pytest.mark.parametrize("field", ["idempotency_key", "amount_minor", "currency", "payment_destination_reference", "provider_name", "provider_metadata_reference", "created_at"])
def test_missing_common_persisted_field_is_rejected(field: str) -> None:
    collection = FakeCollection()
    item = command()
    FinancialExecutionCommandRegistry.create(item, collection)  # type: ignore[arg-type]
    collection.rows[0].pop(field)
    with pytest.raises(FinancialExecutionCommandPersistedRecordInvalidError):
        FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["tenant_id", "execution_command_id"])
def test_identity_corruption_is_a_lookup_miss_not_hydration_proof(field: str) -> None:
    collection = FakeCollection()
    item = command()
    FinancialExecutionCommandRegistry.create(item, collection)  # type: ignore[arg-type]
    collection.rows[0].pop(field)
    with pytest.raises(FinancialExecutionCommandNotFoundError):
        FinancialExecutionCommandRegistry.get(item.tenant_id, item.execution_command_id, collection)  # type: ignore[arg-type]


def test_source_request_index_contains_exact_tenant_family_request_paths() -> None:
    collection = FakeCollection()
    FinancialExecutionCommandRegistry.ensure_indexes(collection)  # type: ignore[arg-type]
    source = next(spec for spec in collection.indexes if spec[1]["name"] == "tenant_family_source_execution_request_unique")
    assert [path for path, _ in source[0]] == ["tenant_id", "source_authority_kind", "source_authority.execution_request_id"]


def test_ap_and_platform_same_source_request_id_are_independent() -> None:
    collection = FakeCollection()
    FinancialExecutionCommandRegistry.create(command(source_authority=ap_source(execution_request_id="same")), collection)  # type: ignore[arg-type]
    FinancialExecutionCommandRegistry.create(command(execution_command_id="platform-command", source_authority=platform_source(execution_request_id="same"), provider_name="STRIPE"), collection)  # type: ignore[arg-type]
    assert len(collection.rows) == 2


def test_same_source_request_different_tenants_are_independent() -> None:
    collection = FakeCollection()
    FinancialExecutionCommandRegistry.create(command(source_authority=ap_source(execution_request_id="same")), collection)  # type: ignore[arg-type]
    FinancialExecutionCommandRegistry.create(command(tenant_id="tenant-2", execution_command_id="tenant-2-command", source_authority=ap_source(execution_request_id="same")), collection)  # type: ignore[arg-type]
    assert len(collection.rows) == 2


def test_ap_source_lookup_is_exact_and_session_scoped() -> None:
    collection = FakeCollection()
    session = object()
    item = command(source_authority=ap_source(execution_request_id="lookup"))
    FinancialExecutionCommandRegistry.create(item, collection, session=session)  # type: ignore[arg-type]
    found = FinancialExecutionCommandRegistry.get_by_source_request("tenant-1", FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE, "lookup", collection, session=session)  # type: ignore[arg-type]
    assert found == item
    assert collection.sessions[-1] is session


def test_platform_source_lookup_is_family_exact() -> None:
    collection = FakeCollection()
    item = command(execution_command_id="platform-command", source_authority=platform_source(execution_request_id="lookup"), provider_name="STRIPE")
    FinancialExecutionCommandRegistry.create(item, collection)  # type: ignore[arg-type]
    assert FinancialExecutionCommandRegistry.get_by_source_request("tenant-1", FinancialExecutionCommandFamily.PLATFORM_BILLING, "lookup", collection) == item  # type: ignore[arg-type]
    assert FinancialExecutionCommandRegistry.get_by_source_request("tenant-1", FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE, "lookup", collection) is None  # type: ignore[arg-type]


def test_source_lookup_zero_rows_is_absence() -> None:
    assert FinancialExecutionCommandRegistry.get_by_source_request("tenant-1", FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE, "missing", FakeCollection()) is None  # type: ignore[arg-type]


def test_source_lookup_multiple_rows_rejects_without_selection() -> None:
    collection = FakeCollection()
    first = command(source_authority=ap_source(execution_request_id="duplicate"))
    second = command(execution_command_id="second", source_authority=ap_source(execution_request_id="duplicate", selection_decision_id="selection-2"))
    collection.rows.extend([first.to_persisted(), second.to_persisted()])
    with pytest.raises(FinancialExecutionCommandRegistryError, match="MULTIPLE_SOURCE_REQUEST_ROWS"):
        FinancialExecutionCommandRegistry.get_by_source_request("tenant-1", FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE, "duplicate", collection)  # type: ignore[arg-type]


@pytest.mark.parametrize("change", [{"execution_command_id": "other"}, {"source_authority": ap_source(execution_request_id="conflict", authorized_provider_name="OTHER"), "provider_name": "OTHER"}, {"source_authority": ap_source(execution_request_id="conflict", selection_decision_id="other")}, {"source_authority": ap_source(execution_request_id="conflict", execution_request_fingerprint=FP_C)}, {"amount_minor": 2000}])
def test_same_source_request_divergence_rejects(change: dict[str, object]) -> None:
    collection = FakeCollection()
    item = command(source_authority=ap_source(execution_request_id="conflict"))
    FinancialExecutionCommandRegistry.create(item, collection)  # type: ignore[arg-type]
    values: dict[str, object] = {"source_authority": ap_source(execution_request_id="conflict")}
    values.update(change)
    candidate = command(**values)  # type: ignore[arg-type]
    with pytest.raises(FinancialExecutionCommandCreateConflictError):
        FinancialExecutionCommandRegistry.create(candidate, collection)  # type: ignore[arg-type]
    assert len(collection.rows) == 1


def test_source_request_duplicate_race_rejects_loser_without_overwrite() -> None:
    collection = FakeCollection()
    winner = command(source_authority=ap_source(execution_request_id="race"))
    collection.race_winner = winner.to_persisted()
    collection.hide_source_reads = 1
    collection.duplicate_source_once = True
    loser = command(execution_command_id="loser", source_authority=ap_source(execution_request_id="race", selection_decision_id="loser-selection"))
    with pytest.raises(FinancialExecutionCommandCreateConflictError):
        FinancialExecutionCommandRegistry.create(loser, collection)  # type: ignore[arg-type]
    assert len(collection.rows) == 1
    assert collection.rows[0]["execution_command_id"] == "command-1"


def test_same_canonical_command_duplicate_race_is_exact_replay() -> None:
    collection = FakeCollection()
    winner = command(source_authority=ap_source(execution_request_id="race"))
    collection.race_winner = winner.to_persisted()
    collection.hide_source_reads = 1
    collection.duplicate_source_once = True
    result = FinancialExecutionCommandRegistry.create(winner, collection)  # type: ignore[arg-type]
    assert result.outcome == "IDEMPOTENT_REPLAY"
    assert len(collection.rows) == 1


def test_duplicate_key_readback_corruption_rejects() -> None:
    collection = FakeCollection()
    winner = command(source_authority=ap_source(execution_request_id="race"))
    broken = winner.to_persisted()
    broken["command_fingerprint"] = FP_C
    collection.race_winner = broken
    collection.hide_source_reads = 1
    collection.duplicate_source_once = True
    with pytest.raises(FinancialExecutionCommandPersistedRecordInvalidError):
        FinancialExecutionCommandRegistry.create(winner, collection)  # type: ignore[arg-type]


def test_source_lookup_rejects_free_form_family() -> None:
    with pytest.raises(FinancialExecutionCommandRegistryError, match="SOURCE_REQUEST_FAMILY_INVALID"):
        FinancialExecutionCommandRegistry.get_by_source_request("tenant-1", "ACCOUNTS_PAYABLE", "request", FakeCollection())  # type: ignore[arg-type]


@pytest.mark.parametrize("mutation", [lambda row: row["source_authority"].pop("source_authority_kind"), lambda row: row["source_authority"].pop("selection_decision_id"), lambda row: row["source_authority"].update({"source_authority_kind": "UNKNOWN"}), lambda row: row.update({"unknown": 1})])
def test_source_lookup_strictly_rejects_missing_unknown_or_legacy_provenance(mutation: object) -> None:
    collection = FakeCollection()
    item = command(source_authority=ap_source(execution_request_id="strict"))
    collection.rows.append(item.to_persisted())
    mutation(collection.rows[0])  # type: ignore[operator]
    with pytest.raises(FinancialExecutionCommandPersistedRecordInvalidError):
        FinancialExecutionCommandRegistry.get_by_source_request("tenant-1", FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE, "strict", collection)  # type: ignore[arg-type]


def test_source_lookup_rejects_provider_source_mismatch() -> None:
    collection = FakeCollection()
    item = command(source_authority=ap_source(execution_request_id="provider"))
    row = item.to_persisted()
    row["provider_name"] = "STRIPE"
    collection.rows.append(row)
    with pytest.raises(FinancialExecutionCommandPersistedRecordInvalidError):
        FinancialExecutionCommandRegistry.get_by_source_request("tenant-1", FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE, "provider", collection)  # type: ignore[arg-type]


def test_registry_accepts_domain_command_id_without_deriving_one() -> None:
    collection = FakeCollection()
    item = command(execution_command_id="bridge-supplied-id", source_authority=ap_source(execution_request_id="identity"))
    FinancialExecutionCommandRegistry.create(item, collection)  # type: ignore[arg-type]
    assert collection.rows[0]["execution_command_id"] == "bridge-supplied-id"


def test_tenant_isolation_source_lookup_never_returns_other_tenant() -> None:
    collection = FakeCollection()
    item = command(tenant_id="tenant-a", source_authority=ap_source(execution_request_id="tenant-request"))
    FinancialExecutionCommandRegistry.create(item, collection)  # type: ignore[arg-type]
    assert FinancialExecutionCommandRegistry.get_by_source_request("tenant-b", FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE, "tenant-request", collection) is None  # type: ignore[arg-type]


def test_source_identity_contains_no_client_invoice_or_receivable_subject() -> None:
    item = command(source_authority=ap_source(execution_request_id="identity"))
    row = item.to_persisted()
    assert "client_invoice_id" not in row
    assert "customer_id" not in row
    assert "client_receivable_id" not in row


def test_registry_does_not_create_attempt_execution_or_settlement_fields() -> None:
    item = command(source_authority=ap_source(execution_request_id="boundary"))
    row = item.to_persisted()
    assert all(name not in row for name in ("attempt_id", "execution_status", "settlement_state", "paid_at"))


# ARTIFACT: test_financial_execution_command_registry.py
# VERSION: v2.1.0-M11-P5-R2B-R1
# AUTHORITY BOUNDARY: certification evidence only; no execution or settlement authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
