"""Direct certificate for the L9C11-P7 client-authority registry.

TITLE: WILSY OS L9C11-P7 Client Representation Authority Registry Certificate
VERSION: v1.0.0-L9C11-P7-CLIENT-REPRESENTATION-AUTHORITY-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify immutable tenant-scoped client Representation-authority
         persistence, replay, strict hydration, exact history and authority
         exclusions using recording fakes only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_representation_authority_registry.py
COLLABORATION / OWNERSHIP: P1 owns the pure authority domain; P7 owns the
                            registry certificate. IAM, currentness, lifecycle,
                            firm decision, Representation formation, Court and
                            finance remain separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-28
TRANSACTION BOUNDARY: Synthetic recording fakes; no Mongo or network access.
FAIL-CLOSED DECLARATION: Missing transactions, corruption, divergence and
                         authority expansion fail certification.
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
)
from tools.eos.legal_operations.registry.legal_client_matter_representation_authority_registry import (
    AUTHORITY_ID_INDEX_NAME,
    COLLECTION,
    FINGERPRINT_INDEX_NAME,
    HISTORY_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    VERSION,
    LegalClientMatterRepresentationAuthorityRegistryConflictError,
    LegalClientMatterRepresentationAuthorityRegistryInputError,
    LegalClientMatterRepresentationAuthorityRegistryPersistedRecordInvalidError,
    LegalClientMatterRepresentationAuthorityRegistryRetryRequiredError,
    LegalClientMatterRepresentationAuthorityRegistryTransactionRequiredError,
    ensure_indexes,
    get_representation_authority,
    get_representation_authority_by_fingerprint,
    get_representation_authority_by_idempotency_key,
    list_representation_authorities_for_context,
    persist_representation_authority,
)


BASE = datetime(2026, 9, 28, 9, 0, tzinfo=timezone.utc)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
HEX_D = "d" * 128


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


def authority(
    *,
    tenant_id: str = "tenant-l9c11",
    authority_id: str = "representation-authority-l9c11-1",
    idempotency_key: str = "idempotency-l9c11-1",
    decision: str = "APPOINTED",
    representative_principal_id: str = "principal-representative-l9c11",
    effective_offset: int = 0,
) -> LegalClientMatterRepresentationAuthority:
    """Build valid synthetic P1 evidence without upstream reads."""
    occurred = BASE + timedelta(minutes=effective_offset)
    return LegalClientMatterRepresentationAuthority(
        authority_id=authority_id,
        tenant_id=tenant_id,
        case_matter_id="matter-l9c11",
        matter_fingerprint=HEX_A,
        client_party_id="party-l9c11",
        subject_reference="client:subject-l9c11",
        subject_identity_fingerprint=HEX_B,
        engagement_id="engagement-l9c11",
        engagement_fingerprint=HEX_C,
        mandate_id="mandate-l9c11",
        mandate_fingerprint=HEX_D,
        mandate_scope_reference="scope:limited",
        mandate_scope_fingerprint=HEX_A,
        mandate_capabilities=["ADVISORY", "NEGOTIATION"],
        acting_capacity_id="capacity-l9c11",
        acting_capacity_fingerprint=HEX_B,
        representative_principal_id=representative_principal_id,
        representative_role="LEGAL_PRACTITIONER",
        representation_scope_capabilities=["ADVISORY"],
        decision=decision,
        appointing_principal_id="principal-client-l9c11",
        source_evidence_reference="evidence:appointment-l9c11",
        source_evidence_fingerprint=HEX_C,
        authorization_evidence_reference="evidence:authorization-l9c11",
        authorization_evidence_fingerprint=HEX_D,
        occurred_at=occurred,
        effective_from=occurred + timedelta(minutes=1),
        effective_until=occurred + timedelta(days=30),
        idempotency_key=idempotency_key,
    )


def test_registry_identity_indexes_and_no_ttl_or_current_pointer() -> None:
    collection = Collection()
    ensure_indexes(collection)
    assert VERSION == "v1.0.0-L9C11-P7-CLIENT-REPRESENTATION-AUTHORITY-REGISTRY"
    assert COLLECTION == "legal_client_matter_representation_authorities"
    assert {cast(str, item["name"]) for item in collection.indexes} == {
        AUTHORITY_ID_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        IDEMPOTENCY_INDEX_NAME,
        HISTORY_INDEX_NAME,
    }
    assert sum(bool(item["unique"]) for item in collection.indexes) == 3
    assert all("expireAfterSeconds" not in item for item in collection.indexes)
    history = next(item for item in collection.indexes if item["name"] == HISTORY_INDEX_NAME)
    fields = [key for key, _direction in cast(list[tuple[str, int]], history["keys"])]
    assert fields == [
        "tenant_id",
        "case_matter_id",
        "matter_fingerprint",
        "client_party_id",
        "subject_identity_fingerprint",
        "representative_principal_id",
        "effective_from",
        "occurred_at",
        "fingerprint",
        "authority_id",
    ]
    source = Path(
        "tools/eos/legal_operations/registry/legal_client_matter_representation_authority_registry.py"
    ).read_text()
    assert "currentness" not in " ".join(
        ast.unparse(node).lower()
        for node in ast.walk(ast.parse(source))
        if isinstance(node, (ast.Import, ast.ImportFrom))
    )
    assert "LegalClientMatterRepresentationAuthority" in source
    assert "CURRENT_POINTER" not in source


def test_transaction_and_exact_domain_instance_are_required() -> None:
    value = authority()
    collection = Collection()
    with pytest.raises(LegalClientMatterRepresentationAuthorityRegistryTransactionRequiredError):
        persist_representation_authority(value, collection, session=None)
    with pytest.raises(LegalClientMatterRepresentationAuthorityRegistryTransactionRequiredError):
        get_representation_authority(value.tenant_id, value.authority_id, collection, session=InactiveSession())
    with pytest.raises(LegalClientMatterRepresentationAuthorityRegistryInputError):
        persist_representation_authority(cast(Any, value.to_dict()), collection, session=Session())


def test_canonical_payload_and_active_session_are_preserved() -> None:
    collection = Collection()
    value = authority()
    before = value.to_dict()
    result = persist_representation_authority(value, collection, session=Session())
    assert result == value
    assert result.to_dict() == before
    assert collection.rows == [before]
    assert all(call[1].__class__ is Session for call in collection.calls)
    assert all(call[0] != "start_transaction" for call in collection.calls)
    assert all(call[0] != "commit_transaction" for call in collection.calls)
    assert all(call[0] != "abort_transaction" for call in collection.calls)


def test_exact_replay_is_hydrated_and_does_not_duplicate() -> None:
    collection = Collection()
    value = authority()
    first = persist_representation_authority(value, collection, session=Session())
    second = persist_representation_authority(value, collection, session=Session())
    assert first == second == value
    assert type(second) is LegalClientMatterRepresentationAuthority
    assert len(collection.rows) == 1


def test_divergent_idempotency_authority_id_and_fingerprint_fail_closed() -> None:
    collection = Collection()
    value = authority()
    persist_representation_authority(value, collection, session=Session())
    with pytest.raises(LegalClientMatterRepresentationAuthorityRegistryConflictError):
        persist_representation_authority(authority(decision="DECLINED"), collection, session=Session())
    with pytest.raises(LegalClientMatterRepresentationAuthorityRegistryConflictError):
        persist_representation_authority(
            authority(authority_id="representation-authority-l9c11-2", decision="DECLINED"),
            collection,
            session=Session(),
        )
    with pytest.raises(LegalClientMatterRepresentationAuthorityRegistryConflictError):
        persist_representation_authority(
            authority(
                authority_id="representation-authority-l9c11-3",
                idempotency_key=value.idempotency_key,
                decision="DECLINED",
            ),
            collection,
            session=Session(),
        )
    fingerprint_collision = authority(
        authority_id="representation-authority-l9c11-5",
        idempotency_key="idempotency-l9c11-5",
        decision="DECLINED",
    )
    object.__setattr__(fingerprint_collision, "fingerprint", value.fingerprint)
    with pytest.raises(LegalClientMatterRepresentationAuthorityRegistryConflictError):
        persist_representation_authority(fingerprint_collision, collection, session=Session())


def test_duplicate_key_race_exact_reconciles_and_divergent_rejects() -> None:
    value = authority()
    exact = DuplicateRaceCollection(value.to_dict())
    assert persist_representation_authority(value, exact, session=Session()) == value
    divergent = authority(decision="DECLINED")
    race = DuplicateRaceCollection(value.to_dict())
    with pytest.raises(LegalClientMatterRepresentationAuthorityRegistryConflictError):
        persist_representation_authority(divergent, race, session=Session())
    empty_race = DuplicateRaceCollection({})
    with pytest.raises(LegalClientMatterRepresentationAuthorityRegistryRetryRequiredError):
        persist_representation_authority(value, empty_race, session=Session())


def test_corrupt_persisted_value_fails_closed_and_input_is_not_mutated() -> None:
    collection = Collection()
    value = authority()
    payload = value.to_dict()
    before = dict(payload)
    collection.rows.append({**payload, "fingerprint": "0" * 128})
    with pytest.raises(LegalClientMatterRepresentationAuthorityRegistryPersistedRecordInvalidError):
        get_representation_authority(value.tenant_id, value.authority_id, collection, session=Session())
    assert payload == before


def test_tenant_scoped_identity_fingerprint_and_idempotency_reads() -> None:
    collection = Collection()
    first = authority()
    other = authority(tenant_id="tenant-l9c11-other")
    persist_representation_authority(first, collection, session=Session())
    persist_representation_authority(other, collection, session=Session())
    assert get_representation_authority(first.tenant_id, first.authority_id, collection, session=Session()) == first
    assert get_representation_authority_by_fingerprint(other.tenant_id, other.fingerprint, collection, session=Session()) == other
    assert get_representation_authority_by_idempotency_key(first.tenant_id, first.idempotency_key, collection, session=Session()) == first
    from tools.eos.legal_operations.registry.legal_client_matter_representation_authority_registry import (
        LegalClientMatterRepresentationAuthorityRegistryNotFoundError,
    )

    with pytest.raises(LegalClientMatterRepresentationAuthorityRegistryNotFoundError):
        get_representation_authority("tenant-l9c11-missing", first.authority_id, collection, session=Session())
    queries = [call[2] for call in collection.calls if call[0] == "find"]
    assert queries and all(query is not None and query.get("tenant_id") for query in queries)


def test_exact_history_order_scope_empty_history_and_multiple_rows() -> None:
    collection = Collection()
    earlier = authority(
        authority_id="representation-authority-l9c11-earlier",
        idempotency_key="idempotency-l9c11-earlier",
        effective_offset=1,
    )
    later = authority(
        authority_id="representation-authority-l9c11-later",
        idempotency_key="idempotency-l9c11-later",
        effective_offset=3,
    )
    persist_representation_authority(later, collection, session=Session())
    persist_representation_authority(earlier, collection, session=Session())
    history = list_representation_authorities_for_context(
        "tenant-l9c11",
        "matter-l9c11",
        HEX_A,
        "party-l9c11",
        HEX_B,
        "principal-representative-l9c11",
        collection,
        session=Session(),
    )
    assert history == (earlier, later)
    assert list_representation_authorities_for_context(
        "tenant-l9c11",
        "other-matter",
        HEX_A,
        "party-l9c11",
        HEX_B,
        "principal-representative-l9c11",
        collection,
        session=Session(),
    ) == ()
    query = next(
        call[2]
        for call in collection.calls
        if call[0] == "find" and call[2] and call[2].get("case_matter_id") == "matter-l9c11"
    )
    assert query == {
        "tenant_id": "tenant-l9c11",
        "case_matter_id": "matter-l9c11",
        "matter_fingerprint": HEX_A,
        "client_party_id": "party-l9c11",
        "subject_identity_fingerprint": HEX_B,
        "representative_principal_id": "principal-representative-l9c11",
    }
    assert all(item.tenant_id == "tenant-l9c11" for item in history)


def test_history_preserves_decisions_without_currentness_or_lifecycle() -> None:
    collection = Collection()
    appointed = authority()
    declined = authority(
        authority_id="representation-authority-l9c11-declined",
        idempotency_key="idempotency-l9c11-declined",
        decision="DECLINED",
        effective_offset=2,
    )
    persist_representation_authority(appointed, collection, session=Session())
    persist_representation_authority(declined, collection, session=Session())
    values = list_representation_authorities_for_context(
        "tenant-l9c11",
        "matter-l9c11",
        HEX_A,
        "party-l9c11",
        HEX_B,
        "principal-representative-l9c11",
        collection,
        session=Session(),
    )
    assert [str(getattr(item.decision, "value", item.decision)) for item in values] == [
        "APPOINTED",
        "DECLINED",
    ]
    source = Path(
        "tools/eos/legal_operations/registry/legal_client_matter_representation_authority_registry.py"
    ).read_text()
    assert "TenantAuthorization" not in source
    assert "legal_client_matter_representation_firm_decision" not in source
    assert "class LegalClientMatterRepresentation:" not in source
    assert "Court" not in " ".join(
        ast.unparse(node)
        for node in ast.walk(ast.parse(source))
        if isinstance(node, (ast.Import, ast.ImportFrom))
    )
    assert "requests" not in source
    assert "httpx" not in source


# ARTIFACT: test_legal_client_matter_representation_authority_registry.py
# VERSION: v1.0.0-L9C11-P7-CLIENT-REPRESENTATION-AUTHORITY-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct immutable registry persistence certificate only
# TENANT POSTURE: all fake reads, writes and collision probes are tenant-scoped
# FAIL-CLOSED POSTURE: transaction, corruption, divergence, race and scope failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
