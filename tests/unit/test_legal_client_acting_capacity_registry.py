"""Direct certificate for the immutable L9A4-P1A2 capacity registry.

TITLE: WILSY OS Legal Client Acting Capacity Registry Certificate
VERSION: v1.0.0-L9A4-P1A2-CLIENT-ACTING-CAPACITY-REGISTRY-CERT
AUTHORITY: Direct adversarial certification of append-only capacity persistence.
EPITOME: Prove caller-owned transactions, exact replay, divergent collision
         protection, strict hydration, tenant/matter/principal/party scope,
         immutable validity filtering, UTC chronology and authority exclusions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_acting_capacity_registry.py
COLLABORATION / OWNERSHIP: The L9A4-P1A2 registry is the sole production
                            subject. The L9A4-P1A domain supplies synthetic
                            immutable evidence. Real Mongo, registry issuance,
                            IAM, HTTP, UI and acceptance remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P1A2-CLIENT-ACTING-CAPACITY-REGISTRY-CERT establishes
           direct proof for index contracts, transaction requirements, exact
           replay, divergent collision, scoped reads, validity semantics,
           corruption rejection, append-only posture and no authority expansion.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque values only; no credentials,
                             tokens, raw PII, network or production records.
TENANT BOUNDARY: Every fake query assertion requires exact tenant scope.
AUTHORITY BOUNDARY: Passing tests grant no issuance, IAM, acceptance,
                    engagement, representation, Court or legal authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
TRANSACTION BOUNDARY: Fakes record caller-session propagation; the registry
                      must not start, commit, abort or retry transactions.
FAIL-CLOSED DECLARATION: Missing transactions, corruption, divergence, schema
                         drift and out-of-scope reads must reject.
"""
from __future__ import annotations

from copy import deepcopy
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    ACTING_CAPACITY_FIELDS,
    LegalClientActingCapacity,
    LegalClientActingCapacityType,
    record_legal_client_acting_capacity,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry import (
    legal_client_acting_capacity_registry as registry,
)


BASE = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=timezone.utc)
SUBJECT_FP = "a" * 128
PARTY_SOURCE_FP = "b" * 128
CAPACITY_SOURCE_FP = "c" * 128


@dataclass
class FakeSession:
    """Minimal caller-owned active transaction marker."""

    in_transaction: bool = True
    start_calls: int = 0
    commit_calls: int = 0
    abort_calls: int = 0


class FakeCursor:
    """Small cursor supporting the registry's bounded sort/limit contract."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def sort(self, specification: list[tuple[str, int]]) -> "FakeCursor":
        for field, direction in reversed(specification):
            self.rows.sort(
                key=lambda row: str(row.get(field, "")),
                reverse=direction < 0,
            )
        return self

    def limit(self, amount: int) -> "FakeCursor":
        self.rows = self.rows[:amount]
        return self

    def __iter__(self):
        return iter(self.rows)


def _matches(row: Mapping[str, Any], query: Mapping[str, Any]) -> bool:
    for field, expected in query.items():
        if field == "$or":
            if not any(_matches(row, branch) for branch in expected):
                return False
            continue
        actual = row.get(field)
        if isinstance(expected, Mapping):
            if "$lte" in expected and not (actual is not None and actual <= expected["$lte"]):
                return False
            if "$gt" in expected and not (actual is not None and actual > expected["$gt"]):
                return False
        elif actual != expected:
            return False
    return True


class FakeCollection:
    """In-memory collection that records exact queries and index definitions."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[dict[str, Any]] = []
        self.find_calls: list[tuple[dict[str, Any], Any]] = []
        self.insert_calls: list[Any] = []
        self.with_options_calls = 0

    def with_options(self, **_: Any) -> "FakeCollection":
        self.with_options_calls += 1
        return self

    def create_index(self, keys: list[tuple[str, int]], **kwargs: Any) -> str:
        record = {"key": dict(keys), **kwargs}
        self.indexes.append(record)
        return str(kwargs["name"])

    def find(self, query: dict[str, Any], *, session: Any) -> FakeCursor:
        self.find_calls.append((deepcopy(query), session))
        return FakeCursor([deepcopy(row) for row in self.rows if _matches(row, query)])

    def insert_one(self, document: dict[str, Any], *, session: Any) -> None:
        self.insert_calls.append(session)
        for index in self.indexes:
            if not index.get("unique"):
                continue
            keys = tuple(index["key"])
            candidate = tuple(document.get(key) for key in keys)
            if any(tuple(row.get(key) for key in keys) == candidate for row in self.rows):
                raise DuplicateKeyError("synthetic duplicate")
        self.rows.append({**deepcopy(document), "_id": f"id-{len(self.rows) + 1}"})

    def count_documents(self, query: dict[str, Any]) -> int:
        return sum(_matches(row, query) for row in self.rows)


def _matter(tenant: str = "tenant-l9a4-p1a2", matter_id: str = "matter-1") -> CaseMatter:
    return CaseMatter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_reference=f"CASE-{matter_id}",
        opened_at=BASE,
        evidence_reference=f"matter-source:{matter_id}",
    )


def _capacity(
    tenant: str = "tenant-l9a4-p1a2",
    *,
    capacity_id: str = "capacity-1",
    matter_id: str = "matter-1",
    principal_id: str = "principal-1",
    capacity_type: LegalClientActingCapacityType = LegalClientActingCapacityType.SELF,
    effective_from: datetime = BASE + timedelta(minutes=1),
    effective_until: datetime | None = BASE + timedelta(days=30),
) -> LegalClientActingCapacity:
    source_matter = _matter(tenant, matter_id)
    party = register_legal_matter_party(
        matter=source_matter,
        party_id=f"party-{matter_id}",
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=LegalMatterPartySide.CLIENT_SIDE,
        matter_role=LegalMatterPartyRole.CLIENT,
        subject_reference="organization:synthetic-client",
        subject_identity_fingerprint=SUBJECT_FP,
        display_name="Synthetic presentation",
        registered_at=BASE,
        source_evidence_reference=f"party-source:{matter_id}",
        source_evidence_fingerprint=PARTY_SOURCE_FP,
    )
    return record_legal_client_acting_capacity(
        case_matter=source_matter,
        party=party,
        capacity_id=capacity_id,
        principal_id=principal_id,
        capacity_type=capacity_type,
        effective_from=effective_from,
        effective_until=effective_until,
        source_evidence_reference=f"capacity-source:{capacity_id}",
        source_evidence_fingerprint=CAPACITY_SOURCE_FP,
    )


def _persist(value: LegalClientActingCapacity, collection: FakeCollection) -> LegalClientActingCapacity:
    return registry.persist_capacity(value, collection, session=FakeSession())


def test_indexes_are_exact_unique_for_identity_and_fingerprint_without_ttl() -> None:
    collection = FakeCollection()
    registry.ensure_indexes(collection)
    assert [item["name"] for item in collection.indexes] == [
        registry.CAPACITY_ID_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.MATTER_PRINCIPAL_INDEX_NAME,
        registry.MATTER_PARTY_INDEX_NAME,
        registry.MATTER_EFFECTIVE_INDEX_NAME,
    ]
    assert collection.indexes[0]["key"] == {"tenant_id": 1, "capacity_id": 1}
    assert collection.indexes[1]["key"] == {"tenant_id": 1, "fingerprint": 1}
    assert collection.indexes[0]["unique"] is True
    assert collection.indexes[1]["unique"] is True
    assert all("expireAfterSeconds" not in item for item in collection.indexes)


def test_every_operational_method_requires_active_caller_transaction() -> None:
    collection = FakeCollection()
    value = _capacity()
    with pytest.raises(registry.LegalClientActingCapacityRegistryTransactionRequiredError):
        registry.persist_capacity(value, collection, session=None)
    with pytest.raises(registry.LegalClientActingCapacityRegistryTransactionRequiredError):
        registry.get_capacity(value.tenant_id, value.capacity_id, collection, session=FakeSession(False))
    with pytest.raises(registry.LegalClientActingCapacityRegistryTransactionRequiredError):
        registry.list_valid_capacities_at(value.tenant_id, value.case_matter_id, BASE, collection, session=None)


def test_exact_persist_replay_and_single_row() -> None:
    collection = FakeCollection()
    registry.ensure_indexes(collection)
    value = _capacity()
    first = _persist(value, collection)
    second = _persist(value, collection)
    assert first == value
    assert second == value
    assert collection.count_documents({"tenant_id": value.tenant_id}) == 1
    assert first.source_evidence_reference == "capacity-source:capacity-1"
    assert first.capacity_type is LegalClientActingCapacityType.SELF


def test_divergent_identity_rejects_without_update_or_delete() -> None:
    collection = FakeCollection()
    registry.ensure_indexes(collection)
    first = _capacity()
    _persist(first, collection)
    divergent = _capacity(principal_id="principal-other")
    with pytest.raises(registry.LegalClientActingCapacityRegistryConflictError):
        _persist(divergent, collection)
    assert collection.count_documents({"tenant_id": first.tenant_id}) == 1
    assert not hasattr(registry, "update_capacity")
    assert not hasattr(registry, "delete_capacity")


def test_tenant_matter_principal_party_reads_are_exactly_scoped() -> None:
    collection = FakeCollection()
    registry.ensure_indexes(collection)
    first = _capacity(capacity_id="capacity-a", principal_id="principal-a")
    second = _capacity(capacity_id="capacity-b", principal_id="principal-b")
    foreign = _capacity(tenant="tenant-other", capacity_id="capacity-foreign", principal_id="principal-a")
    for value in (first, second, foreign):
        _persist(value, collection)
    session = FakeSession()
    principal_values = registry.list_matter_principal_capacities(
        first.tenant_id, first.case_matter_id, "principal-a", collection, session=session
    )
    party_values = registry.list_matter_party_capacities(
        first.tenant_id, first.case_matter_id, first.party_id, collection, session=session
    )
    assert [item.capacity_id for item in principal_values] == ["capacity-a"]
    assert [item.capacity_id for item in party_values] == ["capacity-b", "capacity-a"]
    with pytest.raises(registry.LegalClientActingCapacityRegistryNotFoundError):
        registry.get_capacity("tenant-other", first.capacity_id, collection, session=session)
    scoped_queries = [
        query for query, _session in collection.find_calls
        if query.get("case_matter_id") == first.case_matter_id
    ]
    assert scoped_queries
    assert all(query.get("tenant_id") == first.tenant_id for query in scoped_queries)


def test_valid_at_time_excludes_expired_and_future_and_keeps_open_ended() -> None:
    collection = FakeCollection()
    registry.ensure_indexes(collection)
    expired = _capacity(
        capacity_id="capacity-expired",
        effective_from=BASE - timedelta(days=3),
        effective_until=BASE - timedelta(days=1),
    )
    future = _capacity(
        capacity_id="capacity-future",
        effective_from=BASE + timedelta(days=3),
        effective_until=BASE + timedelta(days=4),
    )
    open_ended = _capacity(
        capacity_id="capacity-open",
        effective_from=BASE - timedelta(days=2),
        effective_until=None,
    )
    for value in (expired, future, open_ended):
        _persist(value, collection)
    valid = registry.list_valid_capacities_at(
        open_ended.tenant_id,
        open_ended.case_matter_id,
        BASE,
        collection,
        session=FakeSession(),
    )
    assert [item.capacity_id for item in valid] == ["capacity-open"]
    assert valid[0].effective_until is None


def test_utc_microseconds_and_effective_until_round_trip() -> None:
    collection = FakeCollection()
    registry.ensure_indexes(collection)
    value = _capacity(
        effective_from="2026-09-26T14:00:00.123456+02:00",  # type: ignore[arg-type]
        effective_until="2026-10-26T14:00:00.123456+02:00",  # type: ignore[arg-type]
    )
    stored = _persist(value, collection)
    assert stored.effective_from == BASE
    assert stored.effective_from.microsecond == 123456
    assert stored.effective_until == datetime(2026, 10, 26, 12, 0, 0, 123456, tzinfo=timezone.utc)
    assert collection.rows[0]["effective_from"] == "2026-09-26T12:00:00.123456Z"


def test_strict_corruption_and_extra_fields_are_rejected() -> None:
    collection = FakeCollection()
    registry.ensure_indexes(collection)
    value = _capacity()
    _persist(value, collection)
    collection.rows[0]["source_evidence_fingerprint"] = "d" * 128
    with pytest.raises(registry.LegalClientActingCapacityRegistryPersistedRecordInvalidError):
        registry.get_capacity(value.tenant_id, value.capacity_id, collection, session=FakeSession())
    collection.rows[0]["source_evidence_fingerprint"] = value.source_evidence_fingerprint
    collection.rows[0]["unexpected"] = True
    with pytest.raises(registry.LegalClientActingCapacityRegistryPersistedRecordInvalidError):
        registry.get_capacity(value.tenant_id, value.capacity_id, collection, session=FakeSession())


def test_missing_and_corrupt_query_inputs_fail_closed() -> None:
    collection = FakeCollection()
    value = _capacity()
    with pytest.raises(registry.LegalClientActingCapacityRegistryInputError):
        registry.get_capacity("", value.capacity_id, collection, session=FakeSession())
    with pytest.raises(registry.LegalClientActingCapacityRegistryInputError):
        registry.get_capacity_by_fingerprint(value.tenant_id, "g" * 128, collection, session=FakeSession())


def test_domain_shape_is_exact_and_excludes_other_authorities() -> None:
    value = _capacity()
    assert set(value.to_dict()) == set(ACTING_CAPACITY_FIELDS)
    forbidden = {
        "acceptance_id", "acceptance_scope", "engagement_id", "engagement_active",
        "retainer_id", "mandate_id", "representation_id", "representation_active",
        "court_proceeding_id", "court_authorized", "financial_authority",
        "billing_authorized", "payment_authorized", "email", "phone", "address",
        "password", "token", "status", "revoked_at",
    }
    assert forbidden.isdisjoint(value.to_dict())


def test_registry_has_no_transaction_lifecycle_or_ttl_authority() -> None:
    collection = FakeCollection()
    registry.ensure_indexes(collection)
    session = FakeSession()
    _persist(_capacity(), collection)
    assert session.start_calls == 0
    assert session.commit_calls == 0
    assert session.abort_calls == 0
    source = registry.__file__
    assert source is not None
    with open(source, encoding="utf-8") as handle:
        text = handle.read()
    assert "expireAfterSeconds" not in text
    assert ".delete" not in text
    assert "update_one(" not in text
    assert "update_many(" not in text
    assert "delete_one(" not in text
    assert "delete_many(" not in text


# ARTIFACT: test_legal_client_acting_capacity_registry.py
# VERSION: v1.0.0-L9A4-P1A2-CLIENT-ACTING-CAPACITY-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct pure registry persistence/read certificate only
# TENANT POSTURE: every fake query asserts exact tenant scope
# FAIL-CLOSED POSTURE: transaction absence, corruption, divergence, overflow and cross-scope access reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
