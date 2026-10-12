"""Direct adversarial certificate for the Legal courier observation registry.

TITLE: Legal Operations Courier Observation Registry Direct Certificate
VERSION: v1.0.0-L8-8B-COURIER-OBSERVATION-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify append-only tenant-scoped courier observation persistence,
         deterministic indexes, exact replay, strict hydration, bounded history,
         active caller-transaction enforcement, cross-tenant absence and
         whole-transaction retry classification for duplicate-key races.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_courier_observation_registry.py
COLLABORATION / OWNERSHIP: Certificate only. L8-8A owns observation semantics;
                            L8-8B owns persistence/read semantics.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-8B-COURIER-OBSERVATION-REGISTRY-CERT
           establishes direct adversarial coverage for index shape, replay,
           conflicts, corruption, tenant isolation, history bounds and retry.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only.
TENANT BOUNDARY: Every read/write assertion is exact-tenant scoped.
AUTHORITY BOUNDARY: Persistence certificate only; no provider, lifecycle,
                    service, return, Court, notification or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing transaction, corruption, divergence, overflow,
                         cross-scope leakage and duplicate races must reject.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_courier_observation import (
    LegalCourierObservation,
    LegalCourierObservationKind,
    create_legal_courier_observation,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    ProcessDocument,
)
from tools.eos.legal_operations.registry.legal_courier_observation_registry import (
    INDEX_TENANT_DOCUMENT_OBSERVED,
    INDEX_TENANT_OBSERVATION,
    INDEX_TENANT_PROVIDER_EVENT,
    INDEX_TENANT_TRACKING_OBSERVED,
    MAX_DOCUMENT_OBSERVATIONS,
    LegalCourierObservationRegistry,
    LegalCourierObservationRegistryConflictError,
    LegalCourierObservationRegistryError,
    LegalCourierObservationRegistryRetryTransactionError,
    LegalCourierObservationRegistryTransactionRequiredError,
    ensure_indexes,
)


BASE = datetime(2026, 10, 12, 5, 0, tzinfo=timezone.utc)
FP = "a" * 128


class Session:
    in_transaction = True


class Cursor(list[dict[str, object]]):
    def limit(self, count: int) -> "Cursor":
        return Cursor(self[:count])


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, object]]] = []
        self.calls: list[tuple[str, object]] = []
        self.duplicate = False

    def create_index(self, keys: list[tuple[str, int]], **kwargs: object) -> str:
        self.indexes.append((keys, dict(kwargs)))
        return str(kwargs.get("name"))

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> dict[str, object] | None:
        self.calls.append(("find_one", session))
        return next(
            (
                row
                for row in self.rows
                if all(row.get(key) == value for key, value in query.items())
            ),
            None,
        )

    def find(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> Cursor:
        self.calls.append(("find", session))
        return Cursor(
            [
                row
                for row in self.rows
                if all(row.get(key) == value for key, value in query.items())
            ]
        )

    def insert_one(
        self,
        row: dict[str, object],
        *,
        session: object = None,
    ) -> None:
        self.calls.append(("insert_one", session))
        if self.duplicate:
            raise DuplicateKeyError("duplicate")
        self.rows.append(deepcopy(row))


def case_matter(tenant: str = "tenant-a") -> CaseMatter:
    return CaseMatter(
        tenant_id=tenant,
        case_matter_id="matter-1",
        matter_reference="MAT-001",
        opened_at=BASE,
        evidence_reference="matter-registration-1",
    )


def process_document(tenant: str = "tenant-a") -> ProcessDocument:
    return ProcessDocument(
        tenant_id=tenant,
        document_id="document-1",
        case_matter_id="matter-1",
        document_type="SUMMONS",
        registered_at=BASE + timedelta(minutes=1),
        registration_evidence_reference="document-registration-1",
    )


def observation(
    *,
    observation_id: str = "obs-1",
    provider_event_reference: str = "provider-event-1",
    observed_at: datetime | None = None,
) -> LegalCourierObservation:
    return create_legal_courier_observation(
        case_matter=case_matter(),
        process_document=process_document(),
        observation_id=observation_id,
        provider_key="provider-alpha",
        tracking_reference="tracking-123",
        provider_event_reference=provider_event_reference,
        event_kind=LegalCourierObservationKind.IN_TRANSIT,
        provider_status="IN_TRANSIT",
        observed_at=observed_at or BASE + timedelta(minutes=2),
        source_evidence_reference="provider-webhook",
        source_evidence_fingerprint=FP,
    )


def test_indexes_are_exact_and_have_no_ttl() -> None:
    collection = Collection()
    ensure_indexes(collection)

    by_name = {str(options["name"]): (keys, options) for keys, options in collection.indexes}

    assert by_name[INDEX_TENANT_OBSERVATION][0] == [
        ("tenant_id", 1),
        ("observation_id", 1),
    ]
    assert by_name[INDEX_TENANT_OBSERVATION][1]["unique"] is True

    assert by_name[INDEX_TENANT_PROVIDER_EVENT][0] == [
        ("tenant_id", 1),
        ("provider_key", 1),
        ("provider_event_reference", 1),
    ]
    assert by_name[INDEX_TENANT_PROVIDER_EVENT][1]["unique"] is True

    assert by_name[INDEX_TENANT_DOCUMENT_OBSERVED][0] == [
        ("tenant_id", 1),
        ("case_matter_id", 1),
        ("document_id", 1),
        ("observed_at", 1),
    ]
    assert by_name[INDEX_TENANT_TRACKING_OBSERVED][0] == [
        ("tenant_id", 1),
        ("provider_key", 1),
        ("tracking_reference", 1),
        ("observed_at", 1),
    ]
    assert all("expireAfterSeconds" not in options for _, options in collection.indexes)


def test_active_transaction_is_required_before_any_write() -> None:
    collection = Collection()
    registry = LegalCourierObservationRegistry(collection)

    with pytest.raises(
        LegalCourierObservationRegistryTransactionRequiredError,
        match="L8_8B_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(observation(), session=None)

    assert collection.rows == []
    assert collection.calls == []


def test_create_exact_replay_and_session_propagation() -> None:
    collection = Collection()
    registry = LegalCourierObservationRegistry(collection)
    session = Session()
    value = observation()

    first = registry.create_or_replay(value, session=session)
    second = registry.create_or_replay(value, session=session)

    assert first == value
    assert second == value
    assert len(collection.rows) == 1
    assert all(call_session is session for _, call_session in collection.calls)


def test_divergent_observation_identity_rejects() -> None:
    collection = Collection()
    registry = LegalCourierObservationRegistry(collection)
    session = Session()

    registry.create_or_replay(observation(), session=session)
    divergent = observation(
        observation_id="obs-1",
        provider_event_reference="provider-event-2",
    )

    with pytest.raises(
        LegalCourierObservationRegistryConflictError,
        match="L8_8B_DIVERGENT_OBSERVATION_IDENTITY",
    ):
        registry.create_or_replay(divergent, session=session)


def test_divergent_provider_event_rejects() -> None:
    collection = Collection()
    registry = LegalCourierObservationRegistry(collection)
    session = Session()

    registry.create_or_replay(observation(), session=session)
    divergent = observation(
        observation_id="obs-2",
        provider_event_reference="provider-event-1",
    )

    with pytest.raises(
        LegalCourierObservationRegistryConflictError,
        match="L8_8B_DIVERGENT_PROVIDER_EVENT",
    ):
        registry.create_or_replay(divergent, session=session)


def test_duplicate_key_requires_whole_transaction_retry() -> None:
    collection = Collection()
    collection.duplicate = True
    registry = LegalCourierObservationRegistry(collection)

    with pytest.raises(
        LegalCourierObservationRegistryRetryTransactionError,
        match="L8_8B_RETRY_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(observation(), session=Session())

    assert collection.rows == []


def test_get_is_exact_tenant_scoped_and_foreign_absence() -> None:
    collection = Collection()
    registry = LegalCourierObservationRegistry(collection)
    session = Session()
    value = observation()
    registry.create_or_replay(value, session=session)

    assert (
        registry.get_by_observation_id(
            tenant_id="tenant-a",
            observation_id="obs-1",
            session=session,
        )
        == value
    )
    assert (
        registry.get_by_observation_id(
            tenant_id="tenant-b",
            observation_id="obs-1",
            session=session,
        )
        is None
    )


def test_corrupt_persisted_row_rejects() -> None:
    collection = Collection()
    registry = LegalCourierObservationRegistry(collection)
    session = Session()
    value = observation()
    registry.create_or_replay(value, session=session)

    collection.rows[0]["service_completed"] = True

    with pytest.raises(
        LegalCourierObservationRegistryError,
        match="L8_8B_CORRUPT_OBSERVATION",
    ):
        registry.get_by_observation_id(
            tenant_id="tenant-a",
            observation_id="obs-1",
            session=session,
        )


def test_document_history_is_bounded_sorted_and_scope_checked() -> None:
    collection = Collection()
    registry = LegalCourierObservationRegistry(collection)
    session = Session()

    later = observation(
        observation_id="obs-2",
        provider_event_reference="provider-event-2",
        observed_at=BASE + timedelta(minutes=4),
    )
    earlier = observation(
        observation_id="obs-1",
        provider_event_reference="provider-event-1",
        observed_at=BASE + timedelta(minutes=2),
    )

    registry.create_or_replay(later, session=session)
    registry.create_or_replay(earlier, session=session)

    history = registry.list_document_observations(
        tenant_id="tenant-a",
        case_matter_id="matter-1",
        document_id="document-1",
        session=session,
    )
    assert [item.observation_id for item in history] == ["obs-1", "obs-2"]

    assert (
        registry.list_document_observations(
            tenant_id="tenant-b",
            case_matter_id="matter-1",
            document_id="document-1",
            session=session,
        )
        == ()
    )


def test_document_history_overflow_rejects() -> None:
    collection = Collection()
    registry = LegalCourierObservationRegistry(collection)
    session = Session()
    template = observation().to_dict()

    for index in range(MAX_DOCUMENT_OBSERVATIONS + 1):
        row = deepcopy(template)
        row["observation_id"] = f"obs-{index}"
        row["provider_event_reference"] = f"event-{index}"
        row["fingerprint"] = ""
        rebuilt = LegalCourierObservation.from_dict(row)
        collection.rows.append(rebuilt.to_dict())

    with pytest.raises(
        LegalCourierObservationRegistryError,
        match="L8_8B_DOCUMENT_HISTORY_LIMIT_EXCEEDED",
    ):
        registry.list_document_observations(
            tenant_id="tenant-a",
            case_matter_id="matter-1",
            document_id="document-1",
            session=session,
        )


# ARTIFACT: test_legal_courier_observation_registry.py
# VERSION: v1.0.0-L8-8B-COURIER-OBSERVATION-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct persistence certificate only
# TENANT POSTURE: exact tenant-scoped replay/read/history behavior certified
# FAIL-CLOSED POSTURE: missing transaction, corruption, divergence, duplicate race and overflow reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
