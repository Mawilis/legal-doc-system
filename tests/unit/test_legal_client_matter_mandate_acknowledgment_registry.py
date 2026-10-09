"""Direct certificate for the L9B10 acknowledgment registry.

TITLE: WILSY OS Legal Client Matter Mandate Acknowledgment Registry Certificate
VERSION: v1.0.0-L9B10-FIRM-MANDATE-ACKNOWLEDGMENT-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify tenant-scoped append-only acknowledgment persistence, exact
         replay, strict hydration, deterministic history and authority fences.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_mandate_acknowledgment_registry.py
COLLABORATION / OWNERSHIP: This certificate covers only acknowledgment
                            evidence persistence. Currentness, IAM, mandate,
                            Engagement, Representation, Court and finance are
                            separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-27
TRANSACTION BOUNDARY: Recording fakes only; no Mongo, network or canonical DB.
FAIL-CLOSED DECLARATION: Missing transactions, collisions, corruption and
                         authority expansion fail certification.
"""
from __future__ import annotations

import ast
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment import (
    LegalClientMatterMandateAcknowledgment,
)
from tools.eos.legal_operations.registry.legal_client_matter_mandate_acknowledgment_registry import (
    ACKNOWLEDGMENT_ID_INDEX_NAME,
    COLLECTION,
    DECISION_INDEX_NAME,
    FINGERPRINT_INDEX_NAME,
    HISTORY_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    LegalClientMatterMandateAcknowledgmentRegistryConflictError,
    LegalClientMatterMandateAcknowledgmentRegistryNotFoundError,
    LegalClientMatterMandateAcknowledgmentRegistryPersistedRecordInvalidError,
    LegalClientMatterMandateAcknowledgmentRegistryTransactionRequiredError,
    ensure_indexes,
    get_acknowledgment,
    get_acknowledgment_by_fingerprint,
    list_acknowledgments_for_grant,
    persist_acknowledgment,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment import (
    LegalClientMatterMandateAcknowledgmentDecision,
)
from tests.unit.test_legal_client_matter_mandate_grant import BASE, grant


class Session:
    """Minimal active caller-owned transaction marker."""

    in_transaction = True


class Cursor:
    """Small Mongo-like cursor for deterministic registry reads."""

    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def sort(self, keys: list[tuple[str, int]]) -> "Cursor":
        for key, direction in reversed(keys):
            self.rows.sort(key=lambda row: row.get(key), reverse=direction < 0)  # type: ignore[no-any-return]
        return self

    def limit(self, count: int) -> "Cursor":
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(self.rows)


class Collection:
    """Recording fake proving session propagation and append-only writes."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[dict[str, object]] = []
        self.calls: list[tuple[str, object]] = []

    def with_options(self, **_: object) -> "Collection":
        return self

    def create_index(
        self, keys: list[tuple[str, int]], *, unique: bool, name: str
    ) -> str:
        self.indexes.append({"keys": keys, "unique": unique, "name": name})
        return name

    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        self.calls.append(("find", session))
        return Cursor(
            [
                dict(row)
                for row in self.rows
                if all(row.get(key) == value for key, value in query.items())
            ]
        )

    def insert_one(self, document: dict[str, object], *, session: object) -> object:
        self.calls.append(("insert_one", session))
        self.rows.append(dict(document))
        return object()


def acknowledgment(
    *,
    decision: LegalClientMatterMandateAcknowledgmentDecision | str = LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED,
    acknowledgment_id: str = "ack-l9b10-1",
    idempotency_key: str = "ack-idempotency-l9b10-1",
    effective_offset: int = 0,
    client_grant: Any | None = None,
) -> LegalClientMatterMandateAcknowledgment:
    """Build synthetic acknowledgment evidence from one canonical grant."""
    occurred = BASE + timedelta(minutes=effective_offset)
    return LegalClientMatterMandateAcknowledgment.from_client_grant(
        client_grant=client_grant or grant(),
        acknowledgment_id=acknowledgment_id,
        decision=decision,
        decision_actor_principal_id="principal-firm-l9b10",
        authorization_evidence_reference="iam-acknowledgment:l9b10",
        authorization_evidence_fingerprint="d" * 128,
        source_evidence_reference="firm-decision:l9b10",
        source_evidence_fingerprint="e" * 128,
        occurred_at=occurred,
        effective_from=occurred,
        idempotency_key=idempotency_key,
    )


def test_collection_indexes_are_exact_and_have_no_ttl() -> None:
    collection = Collection()
    ensure_indexes(collection)
    assert COLLECTION == "legal_client_matter_mandate_acknowledgments"
    assert {index["name"] for index in collection.indexes} == {
        ACKNOWLEDGMENT_ID_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        IDEMPOTENCY_INDEX_NAME,
        HISTORY_INDEX_NAME,
        DECISION_INDEX_NAME,
    }
    assert not any("expireAfterSeconds" in index for index in collection.indexes)
    assert sum(bool(index["unique"]) for index in collection.indexes) == 3
    by_name: dict[str, Any] = {
        str(index["name"]): index for index in collection.indexes
    }
    assert by_name[ACKNOWLEDGMENT_ID_INDEX_NAME]["keys"] == [
        ("tenant_id", 1),
        ("acknowledgment_id", 1),
    ]
    assert by_name[HISTORY_INDEX_NAME]["keys"][-1] == ("fingerprint", 1)
    assert by_name[DECISION_INDEX_NAME]["keys"][-2:] == [
        ("effective_from", -1),
        ("decision", 1),
    ]


def test_active_transaction_is_required() -> None:
    value = acknowledgment()
    with pytest.raises(LegalClientMatterMandateAcknowledgmentRegistryTransactionRequiredError):
        persist_acknowledgment(value, Collection(), session=None)
    with pytest.raises(LegalClientMatterMandateAcknowledgmentRegistryTransactionRequiredError):
        get_acknowledgment(
            value.tenant_id,
            value.acknowledgment_id,
            Collection(),
            session=type("Inactive", (), {"in_transaction": False})(),
        )


@pytest.mark.parametrize(
    "decision",
    [
        LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED,
        LegalClientMatterMandateAcknowledgmentDecision.DECLINED,
        LegalClientMatterMandateAcknowledgmentDecision.REQUIRES_REVIEW,
    ],
)
def test_each_decision_round_trips_with_exact_session(decision: LegalClientMatterMandateAcknowledgmentDecision) -> None:
    collection = Collection()
    session = Session()
    value = acknowledgment(decision=decision, acknowledgment_id=f"ack-{decision.lower()}", idempotency_key=f"key-{decision.lower()}")
    assert persist_acknowledgment(value, collection, session=session) == value
    assert get_acknowledgment(value.tenant_id, value.acknowledgment_id, collection, session=session) == value
    assert all(call_session is session for _, call_session in collection.calls)


def test_exact_replay_by_id_fingerprint_and_idempotency_is_single_row() -> None:
    collection = Collection()
    value = acknowledgment()
    assert persist_acknowledgment(value, collection, session=Session()) == value
    assert persist_acknowledgment(value, collection, session=Session()) == value
    assert get_acknowledgment_by_fingerprint(value.tenant_id, value.fingerprint, collection, session=Session()) == value
    assert len(collection.rows) == 1


def test_divergent_id_and_idempotency_collisions_fail_closed() -> None:
    collection = Collection()
    value = acknowledgment()
    persist_acknowledgment(value, collection, session=Session())
    with pytest.raises(LegalClientMatterMandateAcknowledgmentRegistryConflictError):
        persist_acknowledgment(
            acknowledgment(decision="DECLINED"), collection, session=Session()
        )
    with pytest.raises(LegalClientMatterMandateAcknowledgmentRegistryConflictError):
        persist_acknowledgment(
            acknowledgment(
                acknowledgment_id="ack-other",
                idempotency_key=value.idempotency_key,
            ),
            collection,
            session=Session(),
        )
    assert len(collection.rows) == 1


def test_multiple_decisions_for_one_grant_are_retained_and_ordered() -> None:
    collection = Collection()
    values = (
        acknowledgment(decision="REQUIRES_REVIEW", effective_offset=0),
        acknowledgment(decision="ACKNOWLEDGED", acknowledgment_id="ack-l9b10-2", idempotency_key="ack-idempotency-l9b10-2", effective_offset=1),
        acknowledgment(decision="DECLINED", acknowledgment_id="ack-l9b10-3", idempotency_key="ack-idempotency-l9b10-3", effective_offset=2),
    )
    for value in values:
        persist_acknowledgment(value, collection, session=Session())
    history = list_acknowledgments_for_grant(values[0].tenant_id, values[0].client_grant_id, collection, session=Session())
    assert [item.decision for item in history] == [
        LegalClientMatterMandateAcknowledgmentDecision.REQUIRES_REVIEW,
        LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED,
        LegalClientMatterMandateAcknowledgmentDecision.DECLINED,
    ]
    assert len(collection.rows) == 3


def test_tenant_isolation_has_no_cross_tenant_existence_oracle() -> None:
    collection = Collection()
    value = acknowledgment()
    persist_acknowledgment(value, collection, session=Session())
    with pytest.raises(LegalClientMatterMandateAcknowledgmentRegistryNotFoundError):
        get_acknowledgment("tenant-other", value.acknowledgment_id, collection, session=Session())
    assert all(row["tenant_id"] == value.tenant_id for row in collection.rows)


def test_strict_hydration_rejects_corrupt_rows_and_duplicate_identity() -> None:
    collection = Collection()
    value = acknowledgment()
    corrupt = value.to_dict()
    corrupt["unexpected"] = "tamper"
    collection.rows.append(corrupt)
    with pytest.raises(LegalClientMatterMandateAcknowledgmentRegistryPersistedRecordInvalidError):
        get_acknowledgment(value.tenant_id, value.acknowledgment_id, collection, session=Session())
    collection.rows.clear()
    collection.rows.extend([value.to_dict(), value.to_dict()])
    with pytest.raises(LegalClientMatterMandateAcknowledgmentRegistryPersistedRecordInvalidError):
        get_acknowledgment(value.tenant_id, value.acknowledgment_id, collection, session=Session())


def test_registry_has_no_currentness_iam_or_downstream_mutation_authority() -> None:
    source = Path(
        "tools/eos/legal_operations/registry/legal_client_matter_mandate_acknowledgment_registry.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert any(module.endswith("legal_client_matter_mandate_acknowledgment") for module in imports)
    assert not any("currentness" in module or "tenant_authorization" in module for module in imports)
    assert "def get_current_acknowledgment" not in source
    assert "def is_acknowledged" not in source
    assert "def latest_acknowledgment" not in source
    assert "update_one" not in source
    assert "delete_many" not in source
    assert "start_transaction" not in source
    assert "commit_transaction" not in source
    assert "abort_transaction" not in source


def test_persisted_domain_shape_contains_no_raw_pii_or_bearer_authority() -> None:
    value = acknowledgment()
    assert set(value.to_dict()) == set(
        LegalClientMatterMandateAcknowledgment.__dataclass_fields__
    )
    assert all(not key.endswith(("email", "password", "token", "jwt")) for key in value.to_dict())


# ARTIFACT: test_legal_client_matter_mandate_acknowledgment_registry.py
# VERSION: v1.0.0-L9B10-FIRM-MANDATE-ACKNOWLEDGMENT-REGISTRY-CERT
# AUTHORITY BOUNDARY: synthetic certificate for append-only acknowledgment evidence only
# END OF WILSY OS SOVEREIGN ARTIFACT
