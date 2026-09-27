"""Direct certificate for the L9C3 conflict-disposition registry.

TITLE: WILSY OS Legal Client Matter Conflict Disposition Registry Certificate
VERSION: v1.0.0-L9C3-CONFLICT-DISPOSITION-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify tenant-scoped append-only disposition evidence persistence,
         exact replay/collision behavior, strict hydration, bounded history and
         authority exclusions using recording fakes only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_conflict_disposition_registry.py
COLLABORATION / OWNERSHIP: This certificate covers L9C3 persistence only.
                            Currentness, IAM, Engagement, Representation, Court
                            and finance remain separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-27
TRANSACTION BOUNDARY: Synthetic recording fakes; no Mongo, network or
                      canonical database access.
FAIL-CLOSED DECLARATION: Missing transactions, collisions, corruption and
                         authority expansion fail certification.
"""
from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition import (
    LegalClientMatterConflictDisposition,
)
from tools.eos.legal_operations.registry.legal_client_matter_conflict_disposition_registry import (
    CLIENT_PARTY_HISTORY_INDEX_NAME,
    COLLECTION,
    DISPOSITION_ID_INDEX_NAME,
    FINGERPRINT_INDEX_NAME,
    HISTORY_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    MATTER_FINGERPRINT_HISTORY_INDEX_NAME,
    REVIEW_LINEAGE_INDEX_NAME,
    SUBJECT_HISTORY_INDEX_NAME,
    LegalClientMatterConflictDispositionRegistryConflictError,
    LegalClientMatterConflictDispositionRegistryNotFoundError,
    LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError,
    LegalClientMatterConflictDispositionRegistryTransactionRequiredError,
    ensure_indexes,
    get_disposition,
    get_disposition_by_fingerprint,
    list_dispositions_for_context,
    list_dispositions_for_matter,
    persist_disposition,
)


BASE = datetime(2026, 9, 27, 8, 0, tzinfo=timezone.utc)


class Session:
    """Minimal active caller-owned transaction marker."""

    in_transaction = True


class Cursor:
    """Small Mongo-like cursor with deterministic sort and bounded limit."""

    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def sort(self, keys: list[tuple[str, int]]) -> "Cursor":
        for key, direction in reversed(keys):
            self.rows.sort(
                key=lambda row: cast(str, row.get(key)),
                reverse=direction < 0,
            )
        return self

    def limit(self, count: int) -> "Cursor":
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(self.rows)


class Collection:
    """Recording fake proving exact session/query propagation and inserts."""

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


def disposition(
    *,
    disposition_id: str = "disp-l9c3-1",
    idempotency_key: str = "disp-idempotency-l9c3-1",
    conflict_review_id: str = "review-l9c3-1",
    conflict_review_fingerprint: str = "b" * 128,
    occurred_offset: int = 0,
) -> LegalClientMatterConflictDisposition:
    """Build synthetic valid disposition evidence without upstream authority."""
    occurred = BASE + timedelta(minutes=occurred_offset)
    return LegalClientMatterConflictDisposition(
        disposition_id=disposition_id,
        tenant_id="tenant-l9c3",
        case_matter_id="matter-l9c3",
        matter_fingerprint="a" * 128,
        screening_id="screening-l9c3",
        screening_fingerprint="c" * 128,
        conflict_review_id=conflict_review_id,
        conflict_review_fingerprint=conflict_review_fingerprint,
        review_outcome="NO_CONFLICT_IDENTIFIED",
        client_party_id="party-l9c3",
        subject_identity_fingerprint="d" * 128,
        disposition="ENGAGEMENT_PERMITTED",
        decision_actor_principal_id="principal-l9c3",
        authorization_evidence_reference="iam:l9c3:authorization",
        authorization_evidence_fingerprint="e" * 128,
        supporting_evidence_reference="review:l9c3:evidence",
        supporting_evidence_fingerprint="f" * 128,
        occurred_at=occurred,
        effective_from=occurred,
        idempotency_key=idempotency_key,
    )


def test_registry_contract_and_indexes_are_exact_without_ttl() -> None:
    collection = Collection()
    ensure_indexes(collection)
    assert COLLECTION == "legal_client_matter_conflict_dispositions"
    assert {index["name"] for index in collection.indexes} == {
        DISPOSITION_ID_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        IDEMPOTENCY_INDEX_NAME,
        REVIEW_LINEAGE_INDEX_NAME,
        HISTORY_INDEX_NAME,
        MATTER_FINGERPRINT_HISTORY_INDEX_NAME,
        CLIENT_PARTY_HISTORY_INDEX_NAME,
        SUBJECT_HISTORY_INDEX_NAME,
    }
    assert sum(bool(index["unique"]) for index in collection.indexes) == 4
    assert not any("expireAfterSeconds" in index for index in collection.indexes)
    by_name: dict[str, dict[str, object]] = {
        cast(str, index["name"]): index for index in collection.indexes
    }
    assert by_name[REVIEW_LINEAGE_INDEX_NAME]["keys"] == [
        ("tenant_id", 1),
        ("conflict_review_id", 1),
        ("conflict_review_fingerprint", 1),
    ]
    assert cast(list[tuple[str, int]], by_name[HISTORY_INDEX_NAME]["keys"])[-1] == (
        "fingerprint",
        1,
    )


def test_active_transaction_is_required_and_inactive_is_rejected() -> None:
    value = disposition()
    with pytest.raises(LegalClientMatterConflictDispositionRegistryTransactionRequiredError):
        persist_disposition(value, Collection(), session=None)
    with pytest.raises(LegalClientMatterConflictDispositionRegistryTransactionRequiredError):
        get_disposition(
            value.tenant_id,
            value.disposition_id,
            Collection(),
            session=type("Inactive", (), {"in_transaction": False})(),
        )


def test_valid_persistence_round_trips_exact_domain_and_session() -> None:
    collection = Collection()
    session = Session()
    value = disposition()
    before = value.to_dict()
    assert persist_disposition(value, collection, session=session) == value
    assert get_disposition(value.tenant_id, value.disposition_id, collection, session=session) == value
    assert get_disposition_by_fingerprint(value.tenant_id, value.fingerprint, collection, session=session) == value
    assert value.to_dict() == before
    assert all(call_session is session for _, call_session, _ in collection.calls)
    assert len(collection.rows) == 1


def test_exact_replay_is_single_row_and_returns_hydrated_evidence() -> None:
    collection = Collection()
    value = disposition()
    first = persist_disposition(value, collection, session=Session())
    second = persist_disposition(value, collection, session=Session())
    assert first == second == value
    assert type(second) is LegalClientMatterConflictDisposition
    assert len(collection.rows) == 1


def test_divergent_disposition_id_collision_fails_closed() -> None:
    collection = Collection()
    value = disposition()
    persist_disposition(value, collection, session=Session())
    divergent = disposition(
        idempotency_key="different-idempotency",
        conflict_review_id="different-review",
        conflict_review_fingerprint="1" * 128,
    )
    with pytest.raises(LegalClientMatterConflictDispositionRegistryConflictError) as error:
        persist_disposition(divergent, collection, session=Session())
    assert error.value.code == "L9C3_DISPOSITION_ID_COLLISION"
    assert len(collection.rows) == 1


def test_divergent_idempotency_collision_fails_closed() -> None:
    collection = Collection()
    value = disposition()
    persist_disposition(value, collection, session=Session())
    divergent = disposition(
        disposition_id="different-disposition",
        idempotency_key=value.idempotency_key,
        conflict_review_id="different-review",
        conflict_review_fingerprint="1" * 128,
    )
    with pytest.raises(LegalClientMatterConflictDispositionRegistryConflictError) as error:
        persist_disposition(divergent, collection, session=Session())
    assert error.value.code == "L9C3_IDEMPOTENCY_KEY_COLLISION"


def test_divergent_review_lineage_collision_fails_closed() -> None:
    collection = Collection()
    value = disposition()
    persist_disposition(value, collection, session=Session())
    divergent = disposition(
        disposition_id="different-disposition",
        idempotency_key="different-idempotency",
    )
    with pytest.raises(LegalClientMatterConflictDispositionRegistryConflictError) as error:
        persist_disposition(divergent, collection, session=Session())
    assert error.value.code == "L9C3_REVIEW_LINEAGE_COLLISION"


def test_same_fingerprint_corruption_fails_closed_before_replay() -> None:
    collection = Collection()
    value = disposition()
    row = value.to_dict()
    row["supporting_evidence_reference"] = "tampered-but-schema-valid"
    row["fingerprint"] = value.fingerprint
    collection.rows.append(row)
    with pytest.raises(LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError):
        persist_disposition(value, collection, session=Session())


def test_distinct_later_review_lineage_is_retained() -> None:
    collection = Collection()
    first = disposition()
    later = disposition(
        disposition_id="disp-l9c3-2",
        idempotency_key="disp-idempotency-l9c3-2",
        conflict_review_id="review-l9c3-2",
        conflict_review_fingerprint="1" * 128,
        occurred_offset=1,
    )
    assert persist_disposition(first, collection, session=Session()) == first
    assert persist_disposition(later, collection, session=Session()) == later
    assert len(collection.rows) == 2


def test_exact_tenant_reads_have_no_cross_tenant_oracle() -> None:
    collection = Collection()
    value = disposition()
    persist_disposition(value, collection, session=Session())
    with pytest.raises(LegalClientMatterConflictDispositionRegistryNotFoundError):
        get_disposition("tenant-other", value.disposition_id, collection, session=Session())
    with pytest.raises(LegalClientMatterConflictDispositionRegistryNotFoundError):
        get_disposition_by_fingerprint("tenant-other", value.fingerprint, collection, session=Session())
    assert all(row["tenant_id"] == value.tenant_id for row in collection.rows)


def test_bounded_matter_and_context_history_are_exact_and_not_currentness() -> None:
    collection = Collection()
    first = disposition()
    later = disposition(
        disposition_id="disp-l9c3-2",
        idempotency_key="disp-idempotency-l9c3-2",
        conflict_review_id="review-l9c3-2",
        conflict_review_fingerprint="1" * 128,
        occurred_offset=1,
    )
    persist_disposition(first, collection, session=Session())
    persist_disposition(later, collection, session=Session())
    history = list_dispositions_for_matter(
        first.tenant_id,
        first.case_matter_id,
        first.client_party_id,
        collection,
        session=Session(),
    )
    exact = list_dispositions_for_context(
        first.tenant_id,
        first.case_matter_id,
        first.matter_fingerprint,
        first.client_party_id,
        first.subject_identity_fingerprint,
        collection,
        session=Session(),
    )
    assert history == exact == (first, later)
    source = Path(
        "tools/eos/legal_operations/registry/legal_client_matter_conflict_disposition_registry.py"
    ).read_text(encoding="utf-8")
    assert "get_current_disposition" not in source
    assert "latest_effective" not in source


def test_history_is_tenant_and_context_scoped() -> None:
    collection = Collection()
    value = disposition()
    persist_disposition(value, collection, session=Session())
    assert list_dispositions_for_matter(
        "tenant-other",
        value.case_matter_id,
        value.client_party_id,
        collection,
        session=Session(),
    ) == ()
    assert list_dispositions_for_context(
        value.tenant_id,
        "matter-other",
        value.matter_fingerprint,
        value.client_party_id,
        value.subject_identity_fingerprint,
        collection,
        session=Session(),
    ) == ()


def test_history_limit_is_bounded_and_rejects_overflow() -> None:
    collection = Collection()
    value = disposition()
    persist_disposition(value, collection, session=Session())
    with pytest.raises(Exception) as error:
        list_dispositions_for_matter(
            value.tenant_id,
            value.case_matter_id,
            value.client_party_id,
            collection,
            session=Session(),
            limit=0,
        )
    assert "LIMIT_INVALID" in str(error.value)


def test_strict_hydration_rejects_extra_fields_and_malformed_fingerprint() -> None:
    collection = Collection()
    value = disposition()
    corrupt = value.to_dict()
    corrupt["unexpected"] = "tamper"
    collection.rows.append(corrupt)
    with pytest.raises(LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError):
        get_disposition(value.tenant_id, value.disposition_id, collection, session=Session())
    collection.rows.clear()
    malformed = value.to_dict()
    malformed["fingerprint"] = "not-a-sha3"
    collection.rows.append(malformed)
    with pytest.raises(LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError):
        get_disposition(value.tenant_id, value.disposition_id, collection, session=Session())


def test_duplicate_identity_rows_fail_closed() -> None:
    collection = Collection()
    value = disposition()
    collection.rows.extend([value.to_dict(), value.to_dict()])
    with pytest.raises(LegalClientMatterConflictDispositionRegistryPersistedRecordInvalidError):
        get_disposition(value.tenant_id, value.disposition_id, collection, session=Session())


def test_registry_has_no_mutable_or_downstream_authority() -> None:
    source_path = Path(
        "tools/eos/legal_operations/registry/legal_client_matter_conflict_disposition_registry.py"
    )
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    assert any(module.endswith("legal_client_matter_conflict_disposition") for module in imports)
    assert not any(
        forbidden in module
        for module in imports
        for forbidden in ("iam", "engagement", "representation", "court", "finance", "currentness")
    )
    for forbidden in (
        "update_one",
        "replace_one",
        "delete_many",
        "start_transaction",
        "commit_transaction",
        "abort_transaction",
    ):
        assert forbidden not in source
    assert "def get_current_disposition" not in source
    assert "current_pointer" not in source


def test_persisted_domain_shape_contains_no_raw_bearer_or_pii_fields() -> None:
    value = disposition()
    assert set(value.to_dict()) == set(
        LegalClientMatterConflictDisposition.__dataclass_fields__
    )
    assert all(
        not key.endswith(("email", "password", "token", "jwt"))
        for key in value.to_dict()
    )


# ARTIFACT: test_legal_client_matter_conflict_disposition_registry.py
# VERSION: v1.0.0-L9C3-CONFLICT-DISPOSITION-REGISTRY-CERT
# AUTHORITY BOUNDARY: synthetic certificate for immutable disposition evidence only
# END OF WILSY OS SOVEREIGN ARTIFACT
