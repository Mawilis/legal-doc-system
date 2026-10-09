"""Direct certificate for the P2A2 lifecycle registry.

TITLE: WILSY OS Legal Client Matter Acceptance Instrument Lifecycle Registry Certificate
VERSION: v1.0.0-L9A4-P2A2-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify exact indexes, caller-owned transactions, ACTIVE baselines,
         terminal transitions, current-state derivation, successor checks,
         replay, corruption rejection and authority exclusions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_acceptance_instrument_lifecycle_registry.py
COLLABORATION / OWNERSHIP: Synthetic in-memory collections only; no Mongo or HTTP.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P2A2-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE-REGISTRY-CERT
           certifies append-only lifecycle persistence and current-state reads.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No PII, secrets, tokens, network or canonical data.
TENANT BOUNDARY: Every fake query is exact tenant/matter/instrument scoped.
AUTHORITY BOUNDARY: Lifecycle evidence only; no approval or acceptance.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
from typing import Any, Iterator

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    LegalClientMatterAcceptanceInstrument,
    record_legal_client_matter_acceptance_instrument,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument_lifecycle import (
    LegalClientMatterAcceptanceInstrumentLifecycle,
    LegalClientMatterAcceptanceInstrumentLifecycleStatus as Status,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry import (
    legal_client_matter_acceptance_instrument_lifecycle_registry as registry,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_acceptance_instrument_registry as instrument_registry,
)


UTC = timezone.utc
NOW = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=UTC)
HEX_A = hashlib.sha3_512(b"instrument-a").hexdigest()
HEX_B = hashlib.sha3_512(b"instrument-b").hexdigest()
MATTER_FP = hashlib.sha3_512(b"matter").hexdigest()
EVIDENCE_FP = hashlib.sha3_512(b"evidence").hexdigest()
SUCCESSOR_FP = hashlib.sha3_512(b"successor").hexdigest()


class Session:
    """Minimal active transaction marker with no lifecycle controls."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active
        self.start_calls = self.commit_calls = self.abort_calls = 0


class Cursor:
    """Deterministic fake Mongo cursor."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.rows)

    def sort(self, fields: list[tuple[str, int]]) -> "Cursor":
        for field, direction in reversed(fields):
            self.rows.sort(key=lambda row: row.get(field, ""), reverse=direction < 0)
        return self

    def limit(self, value: int) -> "Cursor":
        self.rows = self.rows[:value]
        return self


class Collection:
    """Fake collection recording sessions and enforcing registry indexes."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[dict[str, Any]] = []
        self.sessions: list[Any] = []
        self.update_calls = self.delete_calls = 0

    def with_options(self, **_kwargs: Any) -> "Collection":
        return self

    def create_index(self, keys: list[tuple[str, int]], **kwargs: Any) -> str:
        item = {"key": keys, **kwargs}
        self.indexes.append(item)
        return str(kwargs["name"])

    @staticmethod
    def _matches(row: dict[str, Any], query: dict[str, Any]) -> bool:
        return all(row.get(key) == expected for key, expected in query.items())

    def find(self, query: dict[str, Any], *, session: Any) -> Cursor:
        self.sessions.append(session)
        return Cursor([deepcopy(row) for row in self.rows if self._matches(row, query)])

    def insert_one(self, document: dict[str, Any], *, session: Any) -> object:
        self.sessions.append(session)
        identity = tuple(document[field] for field in ("tenant_id", "case_matter_id", "instrument_id", "version", "status"))
        fingerprint = (document["tenant_id"], document["fingerprint"])
        terminal = document["status"] != Status.ACTIVE.value
        for row in self.rows:
            if tuple(row[field] for field in ("tenant_id", "case_matter_id", "instrument_id", "version", "status")) == identity:
                raise DuplicateKeyError("synthetic lifecycle identity collision")
            if (row["tenant_id"], row["fingerprint"]) == fingerprint:
                raise DuplicateKeyError("synthetic lifecycle fingerprint collision")
            if terminal and row["status"] != Status.ACTIVE.value and tuple(row[field] for field in ("tenant_id", "case_matter_id", "instrument_id", "version")) == tuple(document[field] for field in ("tenant_id", "case_matter_id", "instrument_id", "version")):
                raise DuplicateKeyError("synthetic terminal collision")
        row = deepcopy(document)
        row["_id"] = f"lifecycle-{len(self.rows) + 1}"
        self.rows.append(row)
        return object()

    def update_one(self, query: dict[str, Any], update: dict[str, Any], *, session: Any = None) -> object:
        self.update_calls += 1
        for row in self.rows:
            if self._matches(row, query):
                row.update(update.get("$set", {}))
        return object()

    def delete_many(self, *_args: Any, **_kwargs: Any) -> object:
        self.delete_calls += 1
        return object()


class InstrumentCollection(Collection):
    """Fake instrument collection with the fields used by its certified registry."""

    def insert_one(self, document: dict[str, Any], *, session: Any) -> object:
        self.sessions.append(session)
        for row in self.rows:
            if (
                row["tenant_id"], row["instrument_id"], row["version"]
            ) == (
                document["tenant_id"], document["instrument_id"], document["version"]
            ):
                raise DuplicateKeyError("synthetic instrument collision")
        self.rows.append(deepcopy(document))
        return object()


def instrument(
    *,
    tenant: str = "tenant-law",
    matter_id: str = "matter-1",
    instrument_id: str = "instrument-1",
    version: str = "1.0.0",
    content: bytes = b"content-1",
) -> LegalClientMatterAcceptanceInstrument:
    """Build one synthetic certified instrument value."""
    matter = CaseMatter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_reference=f"REF-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"intake:{matter_id}",
    )
    return record_legal_client_matter_acceptance_instrument(
        case_matter=matter,
        instrument_id=instrument_id,
        version=version,
        instrument_kind="MATTER_REVIEW",
        title="Matter Information Review",
        review_scope=f"Bounded review scope for {instrument_id} {version}.",
        content_reference=f"artifact:{matter_id}/{instrument_id}/{version}",
        content_fingerprint=hashlib.sha3_512(content).hexdigest(),
        created_at=NOW,
        effective_from=NOW,
        approval_evidence_reference=f"approval:{matter_id}/{instrument_id}/{version}",
        approval_evidence_fingerprint=hashlib.sha3_512(f"approval-{version}".encode()).hexdigest(),
    )


def lifecycle(
    *,
    status: Status = Status.ACTIVE,
    prior_status: Status | None = None,
    instrument_id: str = "instrument-1",
    version: str = "1.0.0",
    instrument_fingerprint: str = HEX_A,
    occurred_at: datetime = NOW,
    **changes: object,
) -> LegalClientMatterAcceptanceInstrumentLifecycle:
    """Build one exact synthetic lifecycle fact."""
    values: dict[str, Any] = {
        "tenant_id": "tenant-law",
        "case_matter_id": "matter-1",
        "matter_fingerprint": MATTER_FP,
        "instrument_id": instrument_id,
        "version": version,
        "instrument_fingerprint": instrument_fingerprint,
        "status": status,
        "prior_status": prior_status,
        "occurred_at": occurred_at,
        "lifecycle_evidence_reference": f"evidence:{instrument_id}:{version}:{status.value}",
        "lifecycle_evidence_fingerprint": EVIDENCE_FP,
    }
    values.update(changes)
    return LegalClientMatterAcceptanceInstrumentLifecycle(**values)


def persist(value: LegalClientMatterAcceptanceInstrumentLifecycle, collection: Collection, instrument_collection: Collection | None = None) -> LegalClientMatterAcceptanceInstrumentLifecycle:
    """Persist through one synthetic active transaction."""
    return registry.persist_lifecycle(
        value,
        collection,
        instrument_collection=instrument_collection,
        session=Session(),
    )


def test_indexes_are_exact_and_non_expiring() -> None:
    collection = Collection()
    registry.ensure_indexes(collection)
    assert [index["name"] for index in collection.indexes] == [
        registry.IDENTITY_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.TERMINAL_INDEX_NAME,
        registry.HISTORY_INDEX_NAME,
        registry.STATE_INDEX_NAME,
    ]
    assert collection.indexes[2]["partialFilterExpression"] == {
        "status": {"$in": ["SUPERSEDED", "RETIRED", "WITHDRAWN"]}
    }
    assert not any("expireAfterSeconds" in index for index in collection.indexes)


@pytest.mark.parametrize("active", [None, False])
def test_active_caller_transaction_is_required(active: bool | None) -> None:
    session = None if active is None else Session(active)
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentLifecycleRegistryTransactionRequiredError):
        registry.persist_lifecycle(lifecycle(), Collection(), session=session)


def test_active_baseline_exact_replay_and_current_state() -> None:
    collection = Collection()
    value = lifecycle()
    assert persist(value, collection) == persist(value, collection) == value
    assert len(collection.rows) == 1
    assert registry.get_current_lifecycle("tenant-law", "matter-1", "instrument-1", "1.0.0", collection, session=Session()) == value


def test_terminal_without_baseline_and_reactivation_fail_closed() -> None:
    collection = Collection()
    retired = lifecycle(status=Status.RETIRED, prior_status=Status.ACTIVE)
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError):
        persist(retired, collection)
    persist(lifecycle(), collection)
    assert persist(retired, collection) == retired
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError):
        persist(lifecycle(), collection)


@pytest.mark.parametrize("status", [Status.RETIRED, Status.WITHDRAWN])
def test_terminal_states_and_source_evidence_are_current(status: Status) -> None:
    collection = Collection()
    active = lifecycle()
    terminal = lifecycle(status=status, prior_status=Status.ACTIVE)
    persist(active, collection)
    assert persist(terminal, collection) == terminal
    assert registry.get_current_lifecycle("tenant-law", "matter-1", "instrument-1", "1.0.0", collection, session=Session()) == terminal
    assert terminal.lifecycle_evidence_reference in str(terminal.to_dict())


def test_supersession_requires_and_verifies_successor_instrument() -> None:
    lifecycle_collection = Collection()
    instrument_collection = InstrumentCollection()
    first = instrument()
    second = instrument(version="2.0.0", content=b"successor")
    instrument_registry.persist_instrument(first, instrument_collection, session=Session())
    instrument_registry.persist_instrument(second, instrument_collection, session=Session())
    persist(lifecycle(instrument_fingerprint=first.fingerprint), lifecycle_collection)
    superseded = lifecycle(
        status=Status.SUPERSEDED,
        prior_status=Status.ACTIVE,
        instrument_fingerprint=first.fingerprint,
        superseding_version_id="instrument-1:2.0.0",
        superseding_instrument_fingerprint=second.fingerprint,
        occurred_at=NOW + timedelta(seconds=1),
        lifecycle_evidence_fingerprint=SUCCESSOR_FP,
    )
    assert persist(superseded, lifecycle_collection, instrument_collection) == superseded
    assert registry.get_current_lifecycle("tenant-law", "matter-1", "instrument-1", "1.0.0", lifecycle_collection, session=Session()) == superseded


def test_terminal_to_terminal_and_divergent_replay_reject() -> None:
    collection = Collection()
    persist(lifecycle(), collection)
    retired = lifecycle(status=Status.RETIRED, prior_status=Status.ACTIVE)
    persist(retired, collection)
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError):
        persist(lifecycle(status=Status.WITHDRAWN, prior_status=Status.ACTIVE), collection)
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentLifecycleRegistryConflictError):
        persist(lifecycle(status=Status.RETIRED, prior_status=Status.ACTIVE, lifecycle_evidence_reference="evidence:divergent"), collection)


def test_chronology_reversal_and_equal_timestamp_behavior() -> None:
    collection = Collection()
    active = lifecycle(occurred_at=NOW)
    persist(active, collection)
    equal_time_terminal = lifecycle(status=Status.RETIRED, prior_status=Status.ACTIVE, occurred_at=NOW)
    assert persist(equal_time_terminal, collection) == equal_time_terminal
    other = Collection()
    persist(lifecycle(occurred_at=NOW + timedelta(seconds=2)), other)
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError):
        registry.persist_lifecycle(
            lifecycle(status=Status.RETIRED, prior_status=Status.ACTIVE, occurred_at=NOW),
            other,
            session=Session(),
        )


def test_scope_isolation_and_no_evidence_state() -> None:
    collection = Collection()
    persist(lifecycle(), collection)
    assert registry.get_current_lifecycle("tenant-other", "matter-1", "instrument-1", "1.0.0", collection, session=Session()) is None
    assert registry.get_current_lifecycle("tenant-law", "matter-other", "instrument-1", "1.0.0", collection, session=Session()) is None
    assert registry.get_current_lifecycle("tenant-law", "matter-1", "other", "1.0.0", collection, session=Session()) is None


def test_corruption_extra_field_and_missing_field_reject() -> None:
    collection = Collection()
    value = lifecycle()
    persist(value, collection)
    collection.rows[0]["status"] = "RETIRED"
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError):
        registry.get_current_lifecycle("tenant-law", "matter-1", "instrument-1", "1.0.0", collection, session=Session())
    collection.rows[0]["status"] = value.status.value
    collection.rows[0]["unexpected"] = True
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentLifecycleRegistryPersistedRecordInvalidError):
        registry.get_current_lifecycle("tenant-law", "matter-1", "instrument-1", "1.0.0", collection, session=Session())


def test_registry_has_no_update_delete_ttl_or_broader_authority() -> None:
    source = inspect.getsource(registry)
    assert "update_one(" not in source
    assert "update_many(" not in source
    assert "delete_one(" not in source
    assert "delete_many(" not in source
    assert "expireAfterSeconds" not in source
    assert "LegalClientAcceptance" not in source
    assert "LegalClientActingCapacity" not in source
    assert "engagement.py" not in source
    assert "representation.py" not in source
    assert "pymongo" in source


def test_session_propagates_and_transaction_lifecycle_is_not_owned() -> None:
    collection = Collection()
    session = Session()
    registry.persist_lifecycle(lifecycle(), collection, session=session)
    registry.get_lifecycle_history("tenant-law", "matter-1", "instrument-1", "1.0.0", collection, session=session)
    assert all(item is session for item in collection.sessions)
    assert session.start_calls == session.commit_calls == session.abort_calls == 0
    assert collection.update_calls == collection.delete_calls == 0


# ARTIFACT: test_legal_client_matter_acceptance_instrument_lifecycle_registry.py
# VERSION: v1.0.0-L9A4-P2A2-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct append-only lifecycle registry certificate only
# TENANT POSTURE: exact synthetic tenant/matter/instrument predicates
# FAIL-CLOSED POSTURE: baseline, replay, terminal race, corruption and scope drift reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
