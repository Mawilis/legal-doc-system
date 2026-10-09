"""Direct certificate for the L9C11-P9 firm-decision registry.

TITLE: WILSY OS Legal Client Matter Representation Firm Decision Registry Certificate
VERSION: v1.0.0-L9C11-P9-FIRM-REPRESENTATION-DECISION-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove immutable tenant-scoped persistence, strict BSON hydration,
         exact replay/collision handling, bounded client-authority lineage and
         authority exclusions with recording fakes only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_representation_firm_decision_registry.py
COLLABORATION / OWNERSHIP: This certificate covers L9C11-P9 persistence only;
                            IAM, currentness, formation, Court and finance
                            remain separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P9 covers exact P2 instances, tenant identities,
           BSON capability-array normalization, immutable replay, bounded
           history and explicit authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TRANSACTION BOUNDARY: Synthetic recording fakes; no Mongo or network access.
FAIL-CLOSED DECLARATION: Missing transactions, corruption, divergent races
                         and authority expansion fail certification.
"""
from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    LegalClientMatterRepresentationAuthority,
    LegalClientMatterRepresentationAuthorityDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import (
    REPRESENTATION_FIRM_DECISION_FIELDS,
    LegalClientMatterRepresentationFirmDecision,
    LegalClientMatterRepresentationFirmDecisionType,
)
from tools.eos.legal_operations.registry.legal_client_matter_representation_firm_decision_registry import (
    COLLECTION,
    DECISION_ID_INDEX_NAME,
    FINGERPRINT_INDEX_NAME,
    HISTORY_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    VERSION,
    LegalClientMatterRepresentationFirmDecisionRegistryConflictError,
    LegalClientMatterRepresentationFirmDecisionRegistryInputError,
    LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError,
    LegalClientMatterRepresentationFirmDecisionRegistryRetryRequiredError,
    LegalClientMatterRepresentationFirmDecisionRegistryTransactionRequiredError,
    ensure_indexes,
    get_firm_decision,
    get_firm_decision_by_fingerprint,
    get_firm_decision_by_idempotency_key,
    list_firm_decisions_for_context,
    persist_firm_decision,
)


HEX = "a" * 128
BASE = datetime(2026, 9, 28, 8, 0, tzinfo=timezone.utc)


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
        self.indexes.append({"keys": keys, "unique": unique, "name": name})
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


class BsonArrayCollection(Collection):
    """Fake BSON codec that materializes immutable capability tuples as arrays."""

    def insert_one(self, document: dict[str, object], *, session: object) -> object:
        self.calls.append(("insert_one", session, None))
        stored = dict(document)
        for field in (
            "client_authority_scope_capabilities",
            "mandate_capabilities",
            "representation_scope_capabilities",
        ):
            if isinstance(stored[field], tuple):
                stored[field] = list(cast(tuple[object, ...], stored[field]))
        self.rows.append(stored)
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


def _authority(**overrides: object) -> LegalClientMatterRepresentationAuthority:
    values: dict[str, object] = {
        "authority_id": "representation-authority-p9-1",
        "tenant_id": "tenant-p9",
        "case_matter_id": "matter-p9",
        "matter_fingerprint": HEX,
        "client_party_id": "party-p9",
        "subject_reference": "client:subject-p9",
        "subject_identity_fingerprint": HEX,
        "engagement_id": "engagement-p9",
        "engagement_fingerprint": HEX,
        "mandate_id": "mandate-p9",
        "mandate_fingerprint": HEX,
        "mandate_scope_reference": "scope:p9",
        "mandate_scope_fingerprint": HEX,
        "mandate_capabilities": ["ADVISORY", "NEGOTIATION"],
        "acting_capacity_id": "capacity-p9",
        "acting_capacity_fingerprint": HEX,
        "representative_principal_id": "principal-representative-p9",
        "representative_role": "LEGAL_PRACTITIONER",
        "representation_scope_capabilities": ["ADVISORY"],
        "decision": LegalClientMatterRepresentationAuthorityDecision.APPOINTED,
        "appointing_principal_id": "principal-client-p9",
        "source_evidence_reference": "evidence:appointment-p9",
        "source_evidence_fingerprint": HEX,
        "authorization_evidence_reference": "evidence:authorization-p9",
        "authorization_evidence_fingerprint": HEX,
        "occurred_at": BASE,
        "effective_from": BASE + timedelta(minutes=1),
        "effective_until": BASE + timedelta(days=30),
        "idempotency_key": "idempotency:authority-p9",
    }
    values.update(overrides)
    return LegalClientMatterRepresentationAuthority(**cast(Any, values))


def decision(
    *,
    authority: LegalClientMatterRepresentationAuthority | None = None,
    state: str = "ACCEPTED",
    offset: int = 0,
    idempotency_key: str = "idempotency:decision-p9-1",
) -> LegalClientMatterRepresentationFirmDecision:
    """Build one valid P2 decision without any registry or IAM reads."""
    authority = authority or _authority()
    occurred = BASE + timedelta(minutes=2 + offset)
    return LegalClientMatterRepresentationFirmDecision.from_client_authority(
        client_authority=authority,
        decision=state,
        decision_actor_principal_id="principal-firm-p9",
        authorization_evidence_reference="evidence:firm-authorization-p9",
        authorization_evidence_fingerprint=HEX,
        source_evidence_reference="evidence:firm-decision-p9",
        source_evidence_fingerprint=HEX,
        occurred_at=occurred,
        effective_from=occurred + timedelta(minutes=1),
        idempotency_key=idempotency_key,
    )


def test_contract_indexes_are_exact_and_no_ttl_or_current_pointer() -> None:
    collection = Collection()
    ensure_indexes(collection)
    assert VERSION == "v1.0.0-L9C11-P9-FIRM-REPRESENTATION-DECISION-REGISTRY"
    assert COLLECTION == "legal_client_matter_representation_firm_decisions"
    assert {cast(str, item["name"]) for item in collection.indexes} == {
        DECISION_ID_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        IDEMPOTENCY_INDEX_NAME,
        HISTORY_INDEX_NAME,
    }
    assert sum(bool(item["unique"]) for item in collection.indexes) == 3
    assert all("expireAfterSeconds" not in item for item in collection.indexes)
    history = next(item for item in collection.indexes if item["name"] == HISTORY_INDEX_NAME)
    assert cast(list[tuple[str, int]], history["keys"]) == [
        ("tenant_id", 1),
        ("case_matter_id", 1),
        ("matter_fingerprint", 1),
        ("client_party_id", 1),
        ("subject_identity_fingerprint", 1),
        ("representation_authority_id", 1),
        ("representation_authority_fingerprint", 1),
        ("representative_principal_id", 1),
        ("effective_from", 1),
        ("occurred_at", 1),
        ("fingerprint", 1),
        ("decision_id", 1),
    ]
    source = Path(
        "tools/eos/legal_operations/registry/"
        "legal_client_matter_representation_firm_decision_registry.py"
    ).read_text()
    assert "project_currentness" not in source
    assert "TTL" not in source


def test_exact_domain_active_transaction_and_explicit_collection_are_required() -> None:
    value = decision()
    collection = Collection()
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionRegistryTransactionRequiredError):
        persist_firm_decision(value, collection, session=None)
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionRegistryTransactionRequiredError):
        get_firm_decision(value.tenant_id, value.decision_id, collection, session=InactiveSession())
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionRegistryInputError):
        persist_firm_decision(cast(Any, value.to_dict()), collection, session=Session())


def test_persistence_is_exact_session_propagated_and_registry_owns_no_transaction() -> None:
    collection = Collection()
    session = Session()
    value = decision()
    result = persist_firm_decision(value, collection, session=session)
    assert result == value
    assert collection.rows == [value.to_dict()]
    assert all(call[1] is session for call in collection.calls)
    assert all(call[0] not in {"start_transaction", "commit_transaction", "abort_transaction"} for call in collection.calls)


def test_bson_arrays_round_trip_and_wrong_shape_or_corruption_fail_closed() -> None:
    collection = BsonArrayCollection()
    value = decision()
    assert persist_firm_decision(value, collection, session=Session()) == value
    for field in (
        "client_authority_scope_capabilities",
        "mandate_capabilities",
        "representation_scope_capabilities",
    ):
        assert isinstance(collection.rows[0][field], list)
    assert persist_firm_decision(value, collection, session=Session()) == value
    assert len(collection.rows) == 1
    collection.rows[0]["representation_scope_capabilities"] = "ADVISORY"
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError):
        get_firm_decision(value.tenant_id, value.decision_id, collection, session=Session())
    collection.rows[0]["representation_scope_capabilities"] = ["UNKNOWN"]
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError):
        get_firm_decision(value.tenant_id, value.decision_id, collection, session=Session())
    collection.rows[0]["representation_scope_capabilities"] = {"ADVISORY"}
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError):
        get_firm_decision(value.tenant_id, value.decision_id, collection, session=Session())
    collection.rows[0] = {**value.to_dict(), "fingerprint": "0" * 128}
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError):
        get_firm_decision(value.tenant_id, value.decision_id, collection, session=Session())


def test_exact_replay_and_all_divergent_identity_collisions_fail_closed() -> None:
    collection = Collection()
    value = decision()
    assert persist_firm_decision(value, collection, session=Session()) == value
    assert persist_firm_decision(value, collection, session=Session()) == value
    assert len(collection.rows) == 1
    idempotency_divergent = decision(
        authority=_authority(authority_id="representation-authority-p9-2"),
        idempotency_key=value.idempotency_key,
    )
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionRegistryConflictError):
        persist_firm_decision(idempotency_divergent, collection, session=Session())
    forced_id = decision(offset=1, idempotency_key="idempotency:decision-p9-id")
    object.__setattr__(forced_id, "decision_id", value.decision_id)
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionRegistryConflictError):
        persist_firm_decision(forced_id, collection, session=Session())
    forced_fingerprint = decision(offset=2, idempotency_key="idempotency:decision-p9-fp")
    object.__setattr__(forced_fingerprint, "fingerprint", value.fingerprint)
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionRegistryConflictError):
        persist_firm_decision(forced_fingerprint, collection, session=Session())


def test_duplicate_key_race_reconciles_exact_only_and_divergence_rejects() -> None:
    value = decision()
    exact = DuplicateRaceCollection(value.to_dict())
    assert persist_firm_decision(value, exact, session=Session()) == value
    divergent = decision(
        authority=_authority(authority_id="representation-authority-p9-race"),
        idempotency_key=value.idempotency_key,
    )
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionRegistryConflictError):
        persist_firm_decision(divergent, DuplicateRaceCollection(value.to_dict()), session=Session())
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionRegistryRetryRequiredError):
        persist_firm_decision(value, DuplicateRaceCollection({}), session=Session())


def test_tenant_scoped_id_fingerprint_and_idempotency_reads_do_not_leak() -> None:
    collection = Collection()
    value = decision()
    other = decision(authority=_authority(tenant_id="tenant-p9-other", authority_id="authority-p9-other"), idempotency_key="idempotency:other")
    persist_firm_decision(value, collection, session=Session())
    persist_firm_decision(other, collection, session=Session())
    assert get_firm_decision(value.tenant_id, value.decision_id, collection, session=Session()) == value
    assert get_firm_decision_by_fingerprint(other.tenant_id, other.fingerprint, collection, session=Session()) == other
    assert get_firm_decision_by_idempotency_key(value.tenant_id, value.idempotency_key, collection, session=Session()) == value
    with pytest.raises(Exception):
        get_firm_decision("tenant-p9-wrong", value.decision_id, collection, session=Session())
    queries = [call[2] for call in collection.calls if call[0] == "find"]
    assert queries and all(query is not None and query.get("tenant_id") for query in queries)


def test_exact_lineage_history_is_bounded_deterministic_and_allows_multiple_rows() -> None:
    collection = Collection()
    later = decision(offset=2, idempotency_key="idempotency:later")
    earlier = decision(offset=1, idempotency_key="idempotency:earlier")
    persist_firm_decision(later, collection, session=Session())
    persist_firm_decision(earlier, collection, session=Session())
    args = (
        "tenant-p9",
        "matter-p9",
        HEX,
        "party-p9",
        HEX,
        "representation-authority-p9-1",
        _authority().fingerprint,
        "principal-representative-p9",
    )
    history = list_firm_decisions_for_context(*args, collection, session=Session())
    assert history == (earlier, later)
    assert list_firm_decisions_for_context(
        "tenant-p9", "other-matter", HEX, "party-p9", HEX,
        "representation-authority-p9-1", _authority().fingerprint,
        "principal-representative-p9", collection, session=Session()
    ) == ()
    assert list_firm_decisions_for_context(
        *args, collection, session=Session(), limit=2
    ) == (earlier, later)
    query = next(
        call[2] for call in collection.calls
        if call[0] == "find" and call[2] and call[2].get("case_matter_id") == "matter-p9"
    )
    assert query == {
        "tenant_id": "tenant-p9",
        "case_matter_id": "matter-p9",
        "matter_fingerprint": HEX,
        "client_party_id": "party-p9",
        "subject_identity_fingerprint": HEX,
        "representation_authority_id": "representation-authority-p9-1",
        "representation_authority_fingerprint": _authority().fingerprint,
        "representative_principal_id": "principal-representative-p9",
    }


def test_authority_exclusions_are_structural_and_no_currentness_or_formation() -> None:
    source = Path(
        "tools/eos/legal_operations/registry/"
        "legal_client_matter_representation_firm_decision_registry.py"
    ).read_text()
    tree = ast.parse(source)
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    imported = " ".join(ast.unparse(node) for node in imports).lower()
    for forbidden in (
        "iam",
        "authorization_registry",
        "currentness",
        "client_matter_representation_authority_registry",
        "matter_assignment",
        "court",
        "finance",
    ):
        assert forbidden not in imported
    assert "start_transaction" not in source
    assert "commit_transaction" not in source
    assert "abort_transaction" not in source
    assert "project_currentness" not in source
    assert "expireAfterSeconds" not in source


# ARTIFACT: test_legal_client_matter_representation_firm_decision_registry.py
# VERSION: v1.0.0-L9C11-P9-FIRM-REPRESENTATION-DECISION-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct certificate for immutable firm-decision registry only
# TENANT POSTURE: all fake reads, replay probes and history are tenant-scoped
# FAIL-CLOSED POSTURE: missing transaction, BSON corruption, collisions and races reject
# END OF WILSY OS SOVEREIGN ARTIFACT
