"""Direct certificate for the L9C10-P1 immutable Engagement registry.

TITLE: WILSY OS Legal Client Matter Engagement Registry Direct Certificate
VERSION: v1.0.0-L9C10-P2-CLIENT-MATTER-ENGAGEMENT-REGISTRY-DIRECT-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify immutable tenant-scoped Engagement persistence, replay,
         strict hydration, bounded history and authority exclusions using
         deterministic recording fakes only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_engagement_registry.py
COLLABORATION / OWNERSHIP: This certificate covers the L9C10-P1 registry
                            only. Real Mongo, formation IAM, formation,
                            currentness, Representation, Court and finance
                            remain separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-28
TRANSACTION BOUNDARY: Synthetic collection/session fakes; no Mongo or network.
FAIL-CLOSED DECLARATION: Missing transactions, corruption, divergence,
                         duplicate races and authority expansion fail tests.
"""
from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    ENGAGEMENT_FIELDS,
    LegalClientMatterEngagement,
)
from tools.eos.legal_operations.registry.legal_client_matter_engagement_registry import (
    COLLECTION,
    ENGAGEMENT_ID_INDEX_NAME,
    FINGERPRINT_INDEX_NAME,
    HISTORY_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    VERSION,
    LegalClientMatterEngagementRegistryConflictError,
    LegalClientMatterEngagementRegistryInputError,
    LegalClientMatterEngagementRegistryNotFoundError,
    LegalClientMatterEngagementRegistryPersistedRecordInvalidError,
    LegalClientMatterEngagementRegistryRetryRequiredError,
    LegalClientMatterEngagementRegistryTransactionRequiredError,
    ensure_indexes,
    get_engagement,
    get_engagement_by_fingerprint,
    get_engagement_by_idempotency_key,
    list_engagements_for_context,
    persist_engagement,
)


BASE = datetime(2026, 9, 28, 9, 0, tzinfo=timezone.utc)
HEX = "a" * 128
SUBJECT_HEX = "b" * 128


class Session:
    """Minimal active caller-owned transaction marker."""

    in_transaction = True


class InactiveSession:
    """Minimal inactive transaction marker."""

    in_transaction = False


class Cursor:
    """Mongo-like cursor supporting deterministic sort and limit."""

    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def sort(self, keys: list[tuple[str, int]]) -> "Cursor":
        for key, direction in reversed(keys):
            self.rows.sort(
                key=lambda row: cast(Any, row.get(key)),
                reverse=direction < 0,
            )
        return self

    def limit(self, count: int) -> "Cursor":
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(self.rows)


class Collection:
    """Recording fake proving filters, sessions, indexes and writes."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[dict[str, object]] = []
        self.calls: list[tuple[str, object, dict[str, object] | None]] = []

    def with_options(self, **_: object) -> "Collection":
        return self

    def create_index(
        self,
        keys: list[tuple[str, int]],
        *,
        unique: bool,
        name: str,
    ) -> str:
        record = {"keys": keys, "unique": unique, "name": name}
        self.indexes = [item for item in self.indexes if item["name"] != name]
        self.indexes.append(record)
        return name

    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        self.calls.append(("find", session, dict(query)))
        return Cursor(
            [
                dict(row)
                for row in self.rows
                if all(row.get(key) == value for key, value in query.items())
            ]
        )

    def insert_one(self, document: dict[str, object], *, session: object) -> object:
        self.calls.append(("insert_one", session, None))
        self.rows.append(dict(document))
        return object()


class DuplicateRaceCollection(Collection):
    """Fake where a concurrent insert wins between preflight and insert."""

    def __init__(self, winning: dict[str, object]) -> None:
        super().__init__()
        self.winning = dict(winning)
        self.hidden = True

    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        if self.hidden:
            return Cursor([])
        return super().find(query, session=session)

    def insert_one(self, document: dict[str, object], *, session: object) -> object:
        self.hidden = False
        if self.winning:
            self.rows.append(dict(self.winning))
        raise DuplicateKeyError("synthetic duplicate race")


def engagement(
    *,
    tenant_id: str = "tenant-l9c10",
    engagement_id: str = "engagement-l9c10-1",
    idempotency_key: str = "idempotency-l9c10-1",
    offset: int = 0,
) -> LegalClientMatterEngagement:
    """Build valid synthetic Engagement evidence through the live domain API."""
    effective = BASE + timedelta(minutes=offset)
    return LegalClientMatterEngagement(
        engagement_id=engagement_id,
        tenant_id=tenant_id,
        case_matter_id="matter-l9c10",
        matter_fingerprint=HEX,
        client_party_id="party-l9c10",
        subject_reference="client:subject-l9c10",
        subject_identity_fingerprint=SUBJECT_HEX,
        acting_capacity_id="capacity-l9c10",
        acting_capacity_fingerprint=HEX,
        client_acceptance_id="acceptance-l9c10",
        client_acceptance_fingerprint=HEX,
        instrument_id="instrument-l9c10",
        version="1",
        instrument_fingerprint=HEX,
        content_fingerprint=HEX,
        mandate_id="mandate-l9c10",
        mandate_scope="scope:l9c10",
        mandate_fingerprint=HEX,
        conflict_disposition_id="disposition-l9c10",
        conflict_disposition_fingerprint=HEX,
        firm_decision_id="decision-l9c10",
        decision_actor_principal_id="principal-l9c10",
        firm_decision_fingerprint=HEX,
        authorization_evidence_reference="authorization:l9c10",
        authorization_evidence_fingerprint=HEX,
        source_evidence_reference="source:l9c10",
        source_evidence_fingerprint=HEX,
        effective_from=effective,
        idempotency_key=idempotency_key,
    )


def test_registry_identity_indexes_and_no_ttl_or_current_pointer() -> None:
    collection = Collection()
    ensure_indexes(collection)
    first = list(collection.indexes)
    ensure_indexes(collection)
    assert collection.indexes == first
    assert VERSION == "v1.0.0-L9C10-P1-CLIENT-MATTER-ENGAGEMENT-REGISTRY"
    assert COLLECTION == "legal_client_matter_engagements"
    assert {cast(str, item["name"]) for item in collection.indexes} == {
        ENGAGEMENT_ID_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        IDEMPOTENCY_INDEX_NAME,
        HISTORY_INDEX_NAME,
    }
    assert sum(bool(item["unique"]) for item in collection.indexes) == 3
    assert all("expireAfterSeconds" not in item for item in collection.indexes)
    history = next(item for item in collection.indexes if item["name"] == HISTORY_INDEX_NAME)
    assert history["keys"] == [
        ("tenant_id", 1),
        ("case_matter_id", 1),
        ("matter_fingerprint", 1),
        ("client_party_id", 1),
        ("subject_identity_fingerprint", 1),
        ("effective_from", 1),
        ("fingerprint", 1),
        ("engagement_id", 1),
    ]


def test_transaction_contract_and_exact_domain_input() -> None:
    value = engagement()
    collection = Collection()
    with pytest.raises(LegalClientMatterEngagementRegistryTransactionRequiredError):
        persist_engagement(value, collection, session=None)
    with pytest.raises(LegalClientMatterEngagementRegistryTransactionRequiredError):
        get_engagement(value.tenant_id, value.engagement_id, collection, session=InactiveSession())
    with pytest.raises(LegalClientMatterEngagementRegistryInputError):
        persist_engagement(cast(Any, value.to_dict()), collection, session=Session())
    with pytest.raises(LegalClientMatterEngagementRegistryInputError):
        persist_engagement(cast(Any, object()), collection, session=Session())


def test_active_transaction_accepts_exact_payload_without_lifecycle_calls() -> None:
    collection = Collection()
    session = Session()
    value = engagement()
    before = value.to_dict()
    result = persist_engagement(value, collection, session=session)
    assert result == value
    assert result.to_dict() == before
    assert collection.rows == [before]
    assert all(call[1] is session for call in collection.calls)
    assert all(call[0] not in {"start_transaction", "commit", "abort"} for call in collection.calls)
    assert set(collection.rows[0]) == set(ENGAGEMENT_FIELDS)


def test_exact_replay_is_strictly_hydrated_and_does_not_duplicate() -> None:
    collection = Collection()
    value = engagement()
    first = persist_engagement(value, collection, session=Session())
    second = persist_engagement(value, collection, session=Session())
    assert first == second == value
    assert type(second) is LegalClientMatterEngagement
    assert len(collection.rows) == 1


def test_divergent_idempotency_and_engagement_id_collisions_fail_closed() -> None:
    collection = Collection()
    value = engagement()
    persist_engagement(value, collection, session=Session())
    with pytest.raises(LegalClientMatterEngagementRegistryConflictError):
        persist_engagement(engagement(engagement_id="engagement-l9c10-2", idempotency_key=value.idempotency_key), collection, session=Session())
    with pytest.raises(LegalClientMatterEngagementRegistryConflictError):
        persist_engagement(engagement(idempotency_key="idempotency-l9c10-2"), collection, session=Session())


def test_fingerprint_corruption_fails_closed() -> None:
    collection = Collection()
    value = engagement()
    collection.rows.append({**value.to_dict(), "mandate_scope": "corrupt-scope"})
    with pytest.raises(LegalClientMatterEngagementRegistryPersistedRecordInvalidError):
        get_engagement_by_fingerprint(value.tenant_id, value.fingerprint, collection, session=Session())


def test_duplicate_key_exact_and_divergent_races_are_reconciled() -> None:
    value = engagement()
    exact = DuplicateRaceCollection(value.to_dict())
    assert persist_engagement(value, exact, session=Session()) == value
    divergent = engagement(offset=1)
    race = DuplicateRaceCollection(value.to_dict())
    with pytest.raises(LegalClientMatterEngagementRegistryConflictError):
        persist_engagement(divergent, race, session=Session())
    empty_race = DuplicateRaceCollection({})
    with pytest.raises(LegalClientMatterEngagementRegistryRetryRequiredError):
        persist_engagement(value, empty_race, session=Session())


def test_tenant_scoped_id_fingerprint_and_idempotency_reads_isolate_rows() -> None:
    collection = Collection()
    first = engagement()
    other = engagement(tenant_id="tenant-l9c10-other")
    persist_engagement(first, collection, session=Session())
    persist_engagement(other, collection, session=Session())
    assert get_engagement(first.tenant_id, first.engagement_id, collection, session=Session()) == first
    assert get_engagement_by_fingerprint(other.tenant_id, other.fingerprint, collection, session=Session()) == other
    assert get_engagement_by_idempotency_key(other.tenant_id, other.idempotency_key, collection, session=Session()) == other
    with pytest.raises(LegalClientMatterEngagementRegistryNotFoundError):
        get_engagement("tenant-l9c10-wrong", first.engagement_id, collection, session=Session())
    with pytest.raises(LegalClientMatterEngagementRegistryNotFoundError):
        get_engagement_by_fingerprint("tenant-l9c10-wrong", first.fingerprint, collection, session=Session())
    with pytest.raises(LegalClientMatterEngagementRegistryNotFoundError):
        get_engagement_by_idempotency_key("tenant-l9c10-wrong", first.idempotency_key, collection, session=Session())
    queries = [call[2] for call in collection.calls if call[0] == "find"]
    assert queries and all(query is not None and query.get("tenant_id") for query in queries)


def test_history_filter_order_empty_tuple_and_multiple_immutable_rows() -> None:
    collection = Collection()
    later = engagement(engagement_id="engagement-l9c10-2", idempotency_key="idempotency-l9c10-2", offset=2)
    earlier = engagement(engagement_id="engagement-l9c10-1", idempotency_key="idempotency-l9c10-1", offset=1)
    persist_engagement(later, collection, session=Session())
    persist_engagement(earlier, collection, session=Session())
    history = list_engagements_for_context(
        "tenant-l9c10", "matter-l9c10", HEX, "party-l9c10", SUBJECT_HEX,
        collection, session=Session(),
    )
    assert history == (earlier, later)
    assert len(collection.rows) == 2
    assert list_engagements_for_context(
        "tenant-l9c10", "other-matter", HEX, "party-l9c10", SUBJECT_HEX,
        collection, session=Session(),
    ) == ()
    query = next(
        call[2] for call in collection.calls
        if call[0] == "find" and call[2] and call[2].get("case_matter_id") == "matter-l9c10"
    )
    assert query == {
        "tenant_id": "tenant-l9c10",
        "case_matter_id": "matter-l9c10",
        "matter_fingerprint": HEX,
        "client_party_id": "party-l9c10",
        "subject_identity_fingerprint": SUBJECT_HEX,
    }


def test_input_is_not_mutated_and_corrupt_schema_is_rejected() -> None:
    collection = Collection()
    value = engagement()
    before = value.to_dict()
    persist_engagement(value, collection, session=Session())
    assert value.to_dict() == before
    collection.rows[0].pop("mandate_scope")
    with pytest.raises(LegalClientMatterEngagementRegistryPersistedRecordInvalidError):
        get_engagement(value.tenant_id, value.engagement_id, collection, session=Session())


def test_authority_import_surface_is_narrow_and_excludes_formation() -> None:
    source = Path("tools/eos/legal_operations/registry/legal_client_matter_engagement_registry.py").read_text()
    tree = ast.parse(source)
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    imported = " ".join(ast.unparse(node) for node in imports).lower()
    assert "legal_client_matter_engagement" in imported
    for forbidden in (
        "case_matter",
        "legal_matter_party",
        "acting_capacity",
        "client_acceptance",
        "acceptance_instrument",
        "conflict_currentness",
        "mandate_currentness",
        "firm_decision_currentness",
        "authorization",
        "representation",
        "court",
        "jwt",
        "http",
    ):
        assert forbidden not in imported
    assert "TTL" in source
    assert "current pointer" in source.lower()


# ARTIFACT: test_legal_client_matter_engagement_registry.py
# VERSION: v1.0.0-L9C10-P2-CLIENT-MATTER-ENGAGEMENT-REGISTRY-DIRECT-CERT
# AUTHORITY BOUNDARY: direct certificate for immutable registry persistence only
# TENANT POSTURE: all fake reads and collision probes are tenant-scoped
# FAIL-CLOSED POSTURE: missing transaction, corruption, divergence and races reject
# END OF WILSY OS SOVEREIGN ARTIFACT
