"""Direct certificate for the L9C9-P1 firm-decision registry.

TITLE: WILSY OS Legal Engagement Firm Decision Registry Certificate
VERSION: v1.0.0-L9C9-P1-ENGAGEMENT-FIRM-DECISION-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify immutable tenant-scoped firm-decision persistence, replay,
         strict hydration, bounded history and authority exclusions with
         recording fakes only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_engagement_firm_decision_registry.py
COLLABORATION / OWNERSHIP: This certificate covers L9C9-P1 persistence only.
                            Currentness, Engagement, IAM, Representation,
                            Court and finance remain separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-28
TRANSACTION BOUNDARY: Synthetic recording fakes; no Mongo or network access.
FAIL-CLOSED DECLARATION: Missing transactions, collisions, corruption and
                         authority expansion fail certification.
"""
from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision import (
    LegalClientMatterEngagementFirmDecision,
)
from tools.eos.legal_operations.registry.legal_client_matter_engagement_firm_decision_registry import (
    COLLECTION,
    DECISION_ID_INDEX_NAME,
    FINGERPRINT_INDEX_NAME,
    HISTORY_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    VERSION,
    LegalClientMatterEngagementFirmDecisionRegistryConflictError,
    LegalClientMatterEngagementFirmDecisionRegistryInputError,
    LegalClientMatterEngagementFirmDecisionRegistryPersistedRecordInvalidError,
    LegalClientMatterEngagementFirmDecisionRegistryRetryRequiredError,
    LegalClientMatterEngagementFirmDecisionRegistryTransactionRequiredError,
    ensure_indexes,
    get_firm_decision,
    get_firm_decision_by_fingerprint,
    list_firm_decisions_for_context,
    persist_firm_decision,
)


BASE = datetime(2026, 9, 28, 9, 0, tzinfo=timezone.utc)


class Session:
    """Minimal active caller-owned transaction marker."""

    in_transaction = True


class InactiveSession:
    """Minimal inactive transaction marker."""

    in_transaction = False


class Cursor:
    """Small Mongo-like cursor supporting deterministic sort and limit."""

    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def sort(self, keys: list[tuple[str, int]]) -> "Cursor":
        for key, direction in reversed(keys):
            self.rows.sort(key=lambda row: cast(Any, row.get(key)), reverse=direction < 0)
        return self

    def limit(self, count: int) -> "Cursor":
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(self.rows)


class Collection:
    """Recording fake proving exact filters, sessions, indexes and writes."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[dict[str, object]] = []
        self.calls: list[tuple[str, object, dict[str, object] | None]] = []

    def with_options(self, **_: object) -> "Collection":
        return self

    def create_index(self, keys: list[tuple[str, int]], *, unique: bool, name: str) -> str:
        self.indexes.append({"keys": keys, "unique": unique, "name": name})
        return name

    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        self.calls.append(("find", session, dict(query)))
        return Cursor([dict(row) for row in self.rows if all(row.get(k) == v for k, v in query.items())])

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
        self.rows.append(dict(self.winning))
        raise DuplicateKeyError("synthetic duplicate race")


def decision(
    *,
    tenant_id: str = "tenant-l9c9",
    decision_id: str = "decision-l9c9-1",
    idempotency_key: str = "idempotency-l9c9-1",
    state: str = "ACCEPTED",
    effective_offset: int = 0,
) -> LegalClientMatterEngagementFirmDecision:
    """Build synthetic valid evidence without upstream authority reads."""
    occurred = BASE + timedelta(minutes=effective_offset)
    return LegalClientMatterEngagementFirmDecision(
        decision_id=decision_id,
        tenant_id=tenant_id,
        case_matter_id="matter-l9c9",
        matter_fingerprint="a" * 128,
        client_party_id="party-l9c9",
        subject_reference="client:subject-l9c9",
        subject_identity_fingerprint="b" * 128,
        decision=state,
        decision_actor_principal_id="principal-l9c9",
        authorization_evidence_reference="iam:l9c9:authorization",
        authorization_evidence_fingerprint="c" * 128,
        source_evidence_reference="source:l9c9:evidence",
        source_evidence_fingerprint="d" * 128,
        occurred_at=occurred,
        effective_from=occurred,
        idempotency_key=idempotency_key,
    )


def test_registry_contract_indexes_and_no_currentness() -> None:
    collection = Collection()
    ensure_indexes(collection)
    assert VERSION == "v1.0.0-L9C9-P1-ENGAGEMENT-FIRM-DECISION-REGISTRY"
    assert COLLECTION == "legal_client_matter_engagement_firm_decisions"
    assert {cast(str, item["name"]) for item in collection.indexes} == {
        DECISION_ID_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        IDEMPOTENCY_INDEX_NAME,
        HISTORY_INDEX_NAME,
    }
    assert sum(bool(item["unique"]) for item in collection.indexes) == 3
    assert all("expireAfterSeconds" not in item for item in collection.indexes)
    history = next(item for item in collection.indexes if item["name"] == HISTORY_INDEX_NAME)
    assert cast(list[tuple[str, int]], history["keys"])[-1] == ("decision_id", 1)
    source = Path("tools/eos/legal_operations/registry/legal_client_matter_engagement_firm_decision_registry.py").read_text()
    assert "project_currentness" not in source
    assert "effective_from" in source
    assert "LegalClientMatterEngagement" not in source.replace("LegalClientMatterEngagementFirmDecision", "")


def test_transaction_and_exact_domain_instance_are_required() -> None:
    value = decision()
    collection = Collection()
    with pytest.raises(LegalClientMatterEngagementFirmDecisionRegistryTransactionRequiredError):
        persist_firm_decision(value, collection, session=None)
    with pytest.raises(LegalClientMatterEngagementFirmDecisionRegistryTransactionRequiredError):
        get_firm_decision(value.tenant_id, value.decision_id, collection, session=InactiveSession())
    with pytest.raises(LegalClientMatterEngagementFirmDecisionRegistryInputError):
        persist_firm_decision(cast(Any, value.to_dict()), collection, session=Session())


def test_registration_round_trip_is_canonical_and_transaction_owned() -> None:
    collection = Collection()
    session = Session()
    value = decision()
    before = value.to_dict()
    result = persist_firm_decision(value, collection, session=session)
    assert result == value
    assert result.to_dict() == before
    assert collection.rows == [before]
    assert all(call[1] is session for call in collection.calls)
    assert all(call[0] != "start_transaction" for call in collection.calls)


def test_exact_replay_is_hydrated_and_does_not_duplicate() -> None:
    collection = Collection()
    value = decision()
    first = persist_firm_decision(value, collection, session=Session())
    second = persist_firm_decision(value, collection, session=Session())
    assert first == second == value
    assert type(second) is LegalClientMatterEngagementFirmDecision
    assert len(collection.rows) == 1


def test_divergent_replays_and_collisions_fail_closed() -> None:
    collection = Collection()
    value = decision()
    persist_firm_decision(value, collection, session=Session())
    with pytest.raises(LegalClientMatterEngagementFirmDecisionRegistryConflictError):
        persist_firm_decision(decision(state="DECLINED"), collection, session=Session())
    with pytest.raises(LegalClientMatterEngagementFirmDecisionRegistryConflictError):
        persist_firm_decision(
            decision(decision_id="decision-l9c9-2", state="DECLINED"),
            collection,
            session=Session(),
        )
    with pytest.raises(LegalClientMatterEngagementFirmDecisionRegistryConflictError):
        persist_firm_decision(
            decision(decision_id="decision-l9c9-3", idempotency_key=value.idempotency_key, state="DECLINED"),
            collection,
            session=Session(),
        )


def test_duplicate_key_exact_race_reconciles_and_divergent_race_rejects() -> None:
    value = decision()
    exact = DuplicateRaceCollection(value.to_dict())
    assert persist_firm_decision(value, exact, session=Session()) == value
    divergent = decision(state="DECLINED")
    race = DuplicateRaceCollection(value.to_dict())
    with pytest.raises(LegalClientMatterEngagementFirmDecisionRegistryConflictError):
        persist_firm_decision(divergent, race, session=Session())
    empty_race = DuplicateRaceCollection({})
    with pytest.raises(LegalClientMatterEngagementFirmDecisionRegistryRetryRequiredError):
        persist_firm_decision(value, empty_race, session=Session())


def test_corrupt_persisted_value_fails_closed() -> None:
    collection = Collection()
    value = decision()
    collection.rows.append({**value.to_dict(), "fingerprint": "0" * 128})
    with pytest.raises(LegalClientMatterEngagementFirmDecisionRegistryPersistedRecordInvalidError):
        get_firm_decision(value.tenant_id, value.decision_id, collection, session=Session())


def test_tenant_scoped_reads_and_cross_tenant_reuse_are_isolated() -> None:
    collection = Collection()
    first = decision()
    other = decision(tenant_id="tenant-l9c9-other")
    persist_firm_decision(first, collection, session=Session())
    persist_firm_decision(other, collection, session=Session())
    assert get_firm_decision(first.tenant_id, first.decision_id, collection, session=Session()) == first
    assert get_firm_decision_by_fingerprint(other.tenant_id, other.fingerprint, collection, session=Session()) == other
    queries = [call[2] for call in collection.calls if call[0] == "find"]
    assert queries and all(query is not None and query.get("tenant_id") for query in queries)


def test_history_filter_order_and_empty_history_are_exact() -> None:
    collection = Collection()
    later = decision(decision_id="decision-l9c9-2", idempotency_key="idempotency-l9c9-2", effective_offset=2)
    earlier = decision(decision_id="decision-l9c9-1", idempotency_key="idempotency-l9c9-1", effective_offset=1)
    persist_firm_decision(later, collection, session=Session())
    persist_firm_decision(earlier, collection, session=Session())
    history = list_firm_decisions_for_context(
        "tenant-l9c9",
        "matter-l9c9",
        "a" * 128,
        "party-l9c9",
        "b" * 128,
        collection,
        session=Session(),
    )
    assert history == (earlier, later)
    assert list_firm_decisions_for_context(
        "tenant-l9c9", "other-matter", "a" * 128, "party-l9c9", "b" * 128, collection, session=Session()
    ) == ()
    query = next(call[2] for call in collection.calls if call[0] == "find" and call[2] and call[2].get("case_matter_id") == "matter-l9c9")
    assert query == {
        "tenant_id": "tenant-l9c9",
        "case_matter_id": "matter-l9c9",
        "matter_fingerprint": "a" * 128,
        "client_party_id": "party-l9c9",
        "subject_identity_fingerprint": "b" * 128,
    }


def test_history_never_projects_currentness_or_forms_engagement() -> None:
    collection = Collection()
    accepted = decision()
    declined = decision(decision_id="decision-l9c9-2", idempotency_key="idempotency-l9c9-2", state="DECLINED", effective_offset=1)
    persist_firm_decision(accepted, collection, session=Session())
    persist_firm_decision(declined, collection, session=Session())
    values = list_firm_decisions_for_context("tenant-l9c9", "matter-l9c9", "a" * 128, "party-l9c9", "b" * 128, collection, session=Session())
    assert [str(getattr(item.decision, "value", item.decision)) for item in values] == [
        "ACCEPTED",
        "DECLINED",
    ]


def test_authority_import_surface_is_narrow() -> None:
    source = Path("tools/eos/legal_operations/registry/legal_client_matter_engagement_firm_decision_registry.py").read_text()
    tree = ast.parse(source)
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    imported = " ".join(ast.unparse(node) for node in imports)
    for forbidden in ("authorization", "client_acceptance", "case_matter", "legal_matter_party", "currentness", "engagement.py"):
        assert forbidden not in imported.lower()


# ARTIFACT: test_legal_client_matter_engagement_firm_decision_registry.py
# VERSION: v1.0.0-L9C9-P1-ENGAGEMENT-FIRM-DECISION-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct certificate for immutable registry persistence only
# TENANT POSTURE: all fake reads and collision probes are tenant-scoped
# FAIL-CLOSED POSTURE: missing transaction, corruption, divergence and races reject
# END OF WILSY OS SOVEREIGN ARTIFACT
