"""Direct certificate for the L9A4-P1B2 matter-instrument registry.

TITLE: WILSY OS Legal Client Matter Acceptance Instrument Registry Certificate
VERSION: v1.0.0-L9A4-P1B2-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify exact indexes, caller-owned transactions, replay, collision,
         tenant/matter isolation, supersession, effective selection,
         corruption rejection and authority exclusions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_acceptance_instrument_registry.py
COLLABORATION / OWNERSHIP: Registry-only certificate with synthetic opaque fixtures.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P1B2-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT-REGISTRY-CERT
           proves immutable append-only instrument persistence and safe reads.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No live database, network, credentials, tokens or PII.
TENANT BOUNDARY: Every fake query uses exact tenant and matter predicates.
AUTHORITY BOUNDARY: Durable instrument evidence only; no acceptance or finance.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
from typing import Any, Iterator

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    LegalClientMatterAcceptanceInstrument,
    record_legal_client_matter_acceptance_instrument,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry import (
    legal_client_matter_acceptance_instrument_registry as registry,
)

UTC = timezone.utc
NOW = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=UTC)


class Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active
        self.start_calls = self.commit_calls = self.abort_calls = 0


class Cursor:
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
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[dict[str, Any]] = []
        self.sessions: list[Any] = []
        self.update_calls = self.delete_calls = 0

    def with_options(self, **_kwargs: Any) -> "Collection":
        return self

    def create_index(self, keys: list[tuple[str, int]], *, unique: bool, name: str) -> str:
        self.indexes.append({"key": keys, "unique": unique, "name": name})
        return name

    @staticmethod
    def _matches(row: dict[str, Any], query: dict[str, Any]) -> bool:
        for key, expected in query.items():
            if key == "$or":
                if not any(Collection._matches(row, item) for item in expected):
                    return False
                continue
            actual = row.get(key)
            if isinstance(expected, dict):
                if "$lte" in expected and not actual <= expected["$lte"]:
                    return False
                if "$gt" in expected and not actual > expected["$gt"]:
                    return False
            elif actual != expected:
                return False
        return True

    def find(self, query: dict[str, Any], *, session: Any) -> Cursor:
        self.sessions.append(session)
        return Cursor([deepcopy(row) for row in self.rows if self._matches(row, query)])

    def insert_one(self, document: dict[str, Any], *, session: Any) -> object:
        self.sessions.append(session)
        identity = (document["tenant_id"], document["instrument_id"], document["version"])
        fingerprint = (document["tenant_id"], document["fingerprint"])
        if any(
            (row["tenant_id"], row["instrument_id"], row["version"]) == identity
            or (row["tenant_id"], row["fingerprint"]) == fingerprint
            for row in self.rows
        ):
            from pymongo.errors import DuplicateKeyError
            raise DuplicateKeyError("synthetic unique collision")
        row = deepcopy(document)
        row["_id"] = f"id-{len(self.rows) + 1}"
        self.rows.append(row)
        return object()

    def update_one(self, *_args: Any, **_kwargs: Any) -> None:
        self.update_calls += 1

    def delete_many(self, *_args: Any, **_kwargs: Any) -> None:
        self.delete_calls += 1


def matter(tenant: str = "tenant-law", matter_id: str = "matter-1") -> CaseMatter:
    return CaseMatter(
        tenant_id=tenant, case_matter_id=matter_id,
        matter_reference=f"REF-{matter_id}", opened_at=NOW,
        evidence_reference=f"intake:{matter_id}",
    )


def instrument(
    *, tenant: str = "tenant-law", matter_id: str = "matter-1",
    instrument_id: str = "instrument-1", version: str = "1.0.0",
    kind: str = "MATTER_REVIEW", effective_from: datetime = NOW,
    supersedes: str | None = None, content: bytes = b"content-1",
) -> LegalClientMatterAcceptanceInstrument:
    return record_legal_client_matter_acceptance_instrument(
        case_matter=matter(tenant, matter_id), instrument_id=instrument_id,
        version=version, instrument_kind=kind, title="Matter Information Review",
        review_scope=f"Bounded review scope for {instrument_id} {version}.",
        content_reference=f"artifact:{matter_id}/{instrument_id}/{version}",
        content_fingerprint=hashlib.sha3_512(content).hexdigest(),
        created_at=NOW, effective_from=effective_from,
        approval_evidence_reference=f"approval:{matter_id}/{instrument_id}/{version}",
        approval_evidence_fingerprint=hashlib.sha3_512(f"approval-{version}".encode()).hexdigest(),
        supersedes_version_id=supersedes,
    )


def persist(value: LegalClientMatterAcceptanceInstrument, collection: Collection) -> LegalClientMatterAcceptanceInstrument:
    return registry.persist_instrument(value, collection, session=Session())


def test_indexes_are_exact_unique_and_have_no_ttl() -> None:
    collection = Collection()
    registry.ensure_indexes(collection)
    assert collection.indexes == [
        {"key": [("tenant_id", 1), ("instrument_id", 1), ("version", 1)], "unique": True, "name": registry.IDENTITY_INDEX_NAME},
        {"key": [("tenant_id", 1), ("fingerprint", 1)], "unique": True, "name": registry.FINGERPRINT_INDEX_NAME},
        {"key": [("tenant_id", 1), ("case_matter_id", 1), ("instrument_id", 1), ("effective_from", -1), ("version", -1)], "unique": False, "name": registry.MATTER_INSTRUMENT_INDEX_NAME},
        {"key": [("tenant_id", 1), ("case_matter_id", 1), ("instrument_kind", 1), ("effective_from", -1)], "unique": False, "name": registry.MATTER_KIND_INDEX_NAME},
        {"key": [("tenant_id", 1), ("case_matter_id", 1), ("effective_from", -1)], "unique": False, "name": registry.MATTER_EFFECTIVE_INDEX_NAME},
    ]
    assert not any("expireAfterSeconds" in index for index in collection.indexes)


@pytest.mark.parametrize("active", [False, None])
def test_persist_requires_active_caller_transaction(active: bool | None) -> None:
    session = Session(active) if active is not None else None
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentRegistryTransactionRequiredError):
        registry.persist_instrument(instrument(), Collection(), session=session)


def test_exact_persist_replay_and_one_row() -> None:
    collection = Collection()
    value = instrument()
    assert persist(value, collection) == persist(value, collection) == value
    assert len(collection.rows) == 1
    assert collection.rows[0]["created_at"] == "2026-09-26T12:00:00.123456Z"


def test_divergent_same_version_rejects_without_update_or_delete() -> None:
    collection = Collection()
    persist(instrument(), collection)
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentRegistryConflictError):
        persist(instrument(content=b"different"), collection)
    assert len(collection.rows) == 1
    assert collection.update_calls == collection.delete_calls == 0


def test_exact_tenant_matter_version_fingerprint_and_kind_reads() -> None:
    collection = Collection()
    first = instrument()
    second = instrument(version="2.0.0", effective_from=NOW + timedelta(days=1), supersedes=first.version_id)
    other_matter = instrument(matter_id="matter-2", instrument_id="other-instrument")
    other_tenant = instrument(tenant="tenant-other", instrument_id="other-tenant-instrument")
    for value in (first, second, other_matter, other_tenant):
        persist(value, collection)
    session = Session()
    assert registry.get_instrument("tenant-law", "matter-1", "instrument-1", "1.0.0", collection, session=session) == first
    assert registry.get_instrument_by_fingerprint("tenant-law", first.fingerprint, collection, session=session) == first
    assert [v.version for v in registry.list_instrument_versions("tenant-law", "matter-1", "instrument-1", collection, session=session)] == ["2.0.0", "1.0.0"]
    assert len(registry.list_matter_instruments_by_kind("tenant-law", "matter-1", "MATTER_REVIEW", collection, session=session)) == 2
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentRegistryNotFoundError):
        registry.get_instrument("tenant-other", "matter-1", "instrument-1", "1.0.0", collection, session=session)


def test_supersession_requires_existing_same_tenant_matter_instrument_chain() -> None:
    collection = Collection()
    first = instrument()
    persist(first, collection)
    assert persist(instrument(version="2.0.0", supersedes=first.version_id), collection)
    for value in (
        instrument(tenant="tenant-other", version="2.0.0", supersedes=first.version_id),
        instrument(matter_id="matter-2", version="2.0.0", supersedes=first.version_id),
        instrument(version="3.0.0", supersedes="instrument-1:9.0.0"),
    ):
        with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentRegistryConflictError):
            persist(value, collection)


def test_latest_effective_excludes_future_and_respects_supersession() -> None:
    collection = Collection()
    first = instrument()
    second = instrument(version="2.0.0", effective_from=NOW + timedelta(days=1), supersedes=first.version_id)
    future = instrument(version="3.0.0", effective_from=NOW + timedelta(days=3))
    for value in (first, second, future):
        persist(value, collection)
    assert registry.get_latest_effective_version("tenant-law", "matter-1", "instrument-1", NOW + timedelta(hours=1), collection, session=Session()) == first
    assert registry.get_latest_effective_version("tenant-law", "matter-1", "instrument-1", NOW + timedelta(days=2), collection, session=Session()) == second
    assert registry.get_latest_effective_version("tenant-law", "matter-1", "instrument-1", NOW - timedelta(seconds=1), collection, session=Session()) is None


def test_same_effective_instant_is_deterministic() -> None:
    collection = Collection()
    persist(instrument(), collection)
    second = instrument(version="2.0.0", content=b"content-2")
    persist(second, collection)
    assert registry.get_latest_effective_version("tenant-law", "matter-1", "instrument-1", NOW, collection, session=Session()) == second


def test_corruption_extra_fields_and_utc_are_rejected() -> None:
    collection = Collection()
    value = instrument()
    persist(value, collection)
    collection.rows[0]["title"] = "tampered"
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError):
        registry.get_instrument("tenant-law", "matter-1", "instrument-1", "1.0.0", collection, session=Session())
    collection.rows[0]["title"] = value.title
    collection.rows[0]["unexpected"] = True
    with pytest.raises(registry.LegalClientMatterAcceptanceInstrumentRegistryPersistedRecordInvalidError):
        registry.get_instrument("tenant-law", "matter-1", "instrument-1", "1.0.0", collection, session=Session())


def test_registry_has_no_update_delete_ttl_or_other_authority() -> None:
    source = inspect.getsource(registry)
    assert all(token not in source for token in ("update_one(", "update_many(", "delete_one(", "delete_many(", "expireAfterSeconds"))
    assert "legal_client_acceptance" not in source
    assert "legal_client_acting_capacity" not in source
    assert "engagement.py" not in source
    assert "representation.py" not in source


def test_session_is_propagated_and_transaction_lifecycle_is_not_owned() -> None:
    collection = Collection()
    session = Session()
    registry.persist_instrument(instrument(), collection, session=session)
    registry.get_instrument("tenant-law", "matter-1", "instrument-1", "1.0.0", collection, session=session)
    assert all(item is session for item in collection.sessions)
    assert session.start_calls == session.commit_calls == session.abort_calls == 0


# ARTIFACT: test_legal_client_matter_acceptance_instrument_registry.py
# VERSION: v1.0.0-L9A4-P1B2-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct immutable instrument persistence/read certificate only
# TENANT POSTURE: exact tenant/matter fake-query assertions
# FAIL-CLOSED POSTURE: transaction/corruption/divergence/supersession authority rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
