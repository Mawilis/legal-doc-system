"""Direct certificate for complete Legal Evidence P3C usage retrieval.

TITLE: Legal Evidence Usage Observation Registry P3C Direct Certificate
VERSION: v1.0.0-L10A2Q-P3C-B-COMPLETE-USAGE-RETRIEVAL-CERT
AUTHORITY: WILSY OS Core Governance
PURPOSE:
    Prove that P3C complete-window evidence is derived from one exhaustive,
    tenant-scoped, strictly hydrated observation stream inside one caller-owned
    active transaction.

EPITOME:
    DURABLE P3 OBSERVATIONS
    -> EXHAUSTIVE TENANT RETRIEVAL
    -> STRICT HYDRATION
    -> COMPLETE P3C USAGE WINDOW
    != REMAINING CAPACITY
    != CAPACITY RESERVED
    != STORAGE ADMISSION

COMPLETENESS POSTURE:
    Mongo time predicates are deliberately forbidden for the completeness read.
    Every row belonging to the tenant must be hydrated before as_of/month/document
    accounting so malformed persisted timestamps cannot disappear from evidence.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

import pytest

from tools.eos.legal_operations.domain.legal_evidence_content import (
    register_legal_evidence_content,
)
from tools.eos.legal_operations.domain.legal_evidence_usage_observation import (
    LegalEvidenceUsageObservation,
    observe_legal_evidence_usage,
)
from tools.eos.legal_operations.domain.legal_evidence_usage_window import (
    LegalEvidenceUsageWindow,
)
from tools.eos.legal_operations.registry.legal_evidence_usage_observation_registry import (
    LegalEvidenceUsageObservationRegistry,
    LegalEvidenceUsageObservationRegistryError,
    LegalEvidenceUsageObservationTransactionRequiredError,
)


AS_OF = datetime(2026, 9, 30, 18, 45, tzinfo=timezone.utc)
FP = "a" * 128


class _Session:
    def __init__(self, *, in_transaction: bool = True) -> None:
        self.in_transaction = in_transaction


class _Cursor:
    """Small deterministic cursor double supporting Mongo-style sort."""

    def __init__(self, rows: Iterable[dict[str, Any]]) -> None:
        self._rows = [dict(row) for row in rows]

    def sort(self, keys: list[tuple[str, int]]) -> "_Cursor":
        def key(row: dict[str, Any]) -> tuple[Any, ...]:
            return tuple(row.get(field) for field, _ in keys)

        self._rows.sort(key=key)
        return self

    def __iter__(self):
        return iter(self._rows)


class _Collection:
    def __init__(self, rows: Iterable[dict[str, Any]] = ()) -> None:
        self.rows = [dict(row) for row in rows]
        self.find_calls: list[tuple[dict[str, Any], Any]] = []

    def find(
        self,
        query: dict[str, Any],
        *,
        session: Any,
    ) -> _Cursor:
        self.find_calls.append((dict(query), session))

        selected = [
            row
            for row in self.rows
            if all(row.get(key) == value for key, value in query.items())
        ]
        return _Cursor(selected)


def _observation(
    *,
    tenant_id: str = "tenant-p3c-b",
    document_id: str,
    occurred_at: datetime,
    content: bytes,
) -> LegalEvidenceUsageObservation:
    canonical = register_legal_evidence_content(
        tenant_id=tenant_id,
        case_matter_id="matter-p3c-b",
        document_id=document_id,
        media_type="application/pdf",
        original_filename=f"{document_id}.pdf",
        content=content,
        source_evidence_reference=f"source:{document_id}:{occurred_at.isoformat()}",
        source_evidence_fingerprint=FP,
        registered_at=occurred_at,
    )
    return observe_legal_evidence_usage(content=canonical)


def _row(
    item: LegalEvidenceUsageObservation,
    *,
    idempotency_key: str,
) -> dict[str, Any]:
    """Construct one persisted-shape row for direct retrieval testing."""
    import hashlib
    import json

    command_payload = {
        "tenant_id": item.tenant_id,
        "idempotency_key": idempotency_key,
        "observation": item.to_dict(),
    }
    command_fingerprint = hashlib.sha3_512(
        json.dumps(
            command_payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    payload = item.to_dict()
    payload["idempotency_key"] = idempotency_key
    payload["command_fingerprint"] = command_fingerprint
    return payload


def test_complete_window_derives_three_distinct_metric_scopes() -> None:
    prior_target = _observation(
        document_id="document-target",
        occurred_at=datetime(2026, 8, 20, 9, tzinfo=timezone.utc),
        content=b"prior-target",
    )
    current_target = _observation(
        document_id="document-target",
        occurred_at=datetime(2026, 9, 10, 9, tzinfo=timezone.utc),
        content=b"current-target",
    )
    current_other = _observation(
        document_id="document-other",
        occurred_at=datetime(2026, 9, 12, 9, tzinfo=timezone.utc),
        content=b"current-other-document",
    )
    future_target = _observation(
        document_id="document-target",
        occurred_at=datetime(2026, 10, 1, 9, tzinfo=timezone.utc),
        content=b"future-target",
    )
    neighbor = _observation(
        tenant_id="tenant-neighbor",
        document_id="document-target",
        occurred_at=datetime(2026, 9, 11, 9, tzinfo=timezone.utc),
        content=b"neighbor",
    )

    collection = _Collection(
        [
            _row(current_other, idempotency_key="current-other"),
            _row(future_target, idempotency_key="future"),
            _row(prior_target, idempotency_key="prior-target"),
            _row(neighbor, idempotency_key="neighbor"),
            _row(current_target, idempotency_key="current-target"),
        ]
    )
    registry = LegalEvidenceUsageObservationRegistry(collection)
    session = _Session()

    window = registry.get_complete_window_for_p4(
        tenant_id="tenant-p3c-b",
        document_id="document-target",
        as_of=AS_OF,
        session=session,
    )

    assert type(window) is LegalEvidenceUsageWindow

    # Tenant storage is cumulative for every tenant observation through as_of.
    assert window.tenant_observation_count == 3
    assert window.tenant_storage_bytes_added == (
        prior_target.storage_bytes_added
        + current_target.storage_bytes_added
        + current_other.storage_bytes_added
    )

    # Monthly ingress is tenant-wide but only current UTC month through as_of.
    assert window.monthly_observation_count == 2
    assert window.monthly_ingress_bytes_added == (
        current_target.monthly_ingress_bytes
        + current_other.monthly_ingress_bytes
    )

    # Version capacity is cumulative for the requested document only.
    assert window.document_observation_count == 2
    assert window.document_versions_added == (
        prior_target.document_versions_added
        + current_target.document_versions_added
    )

    assert window.tenant_id == "tenant-p3c-b"
    assert window.document_id == "document-target"
    assert window.as_of == AS_OF
    assert window.monthly_window_start == datetime(
        2026,
        9,
        1,
        tzinfo=timezone.utc,
    )
    assert window.monthly_window_end == AS_OF
    assert len(window.source_observation_set_fingerprint) == 128
    int(window.source_observation_set_fingerprint, 16)


def test_complete_window_queries_entire_tenant_not_time_bounded_subset() -> None:
    item = _observation(
        document_id="document-target",
        occurred_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
        content=b"tenant-query",
    )
    collection = _Collection([_row(item, idempotency_key="tenant-query")])
    registry = LegalEvidenceUsageObservationRegistry(collection)
    session = _Session()

    registry.get_complete_window_for_p4(
        tenant_id=item.tenant_id,
        document_id=item.document_id,
        as_of=AS_OF,
        session=session,
    )

    assert collection.find_calls == [
        (
            {
                "tenant_id": item.tenant_id,
            },
            session,
        )
    ]


def test_legitimate_empty_complete_window_is_explicit_evidence() -> None:
    collection = _Collection()
    registry = LegalEvidenceUsageObservationRegistry(collection)

    window = registry.get_complete_window_for_p4(
        tenant_id="tenant-p3c-b",
        document_id="document-empty",
        as_of=AS_OF,
        session=_Session(),
    )

    assert window.tenant_observation_count == 0
    assert window.monthly_observation_count == 0
    assert window.document_observation_count == 0
    assert window.tenant_storage_bytes_added == 0
    assert window.monthly_ingress_bytes_added == 0
    assert window.document_versions_added == 0
    assert len(window.source_observation_set_fingerprint) == 128


def test_inactive_transaction_rejects_before_collection_access() -> None:
    collection = _Collection()
    registry = LegalEvidenceUsageObservationRegistry(collection)

    with pytest.raises(
        LegalEvidenceUsageObservationTransactionRequiredError,
        match="L10A2Q_P3B_TRANSACTION_REQUIRED",
    ):
        registry.get_complete_window_for_p4(
            tenant_id="tenant-p3c-b",
            document_id="document-target",
            as_of=AS_OF,
            session=_Session(in_transaction=False),
        )

    assert collection.find_calls == []


def test_corrupt_target_tenant_row_rejects_even_when_future_or_prior() -> None:
    prior = _observation(
        document_id="document-prior",
        occurred_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
        content=b"prior-corrupt",
    )
    future = _observation(
        document_id="document-future",
        occurred_at=datetime(2026, 10, 5, tzinfo=timezone.utc),
        content=b"future-corrupt",
    )

    for item, key in (
        (prior, "prior-corrupt"),
        (future, "future-corrupt"),
    ):
        row = _row(item, idempotency_key=key)
        row["occurred_at"] = "not-a-timestamp"

        registry = LegalEvidenceUsageObservationRegistry(
            _Collection([row])
        )

        with pytest.raises(
            LegalEvidenceUsageObservationRegistryError,
            match="L10A2Q_P3B_CORRUPT_OBSERVATION",
        ):
            registry.get_complete_window_for_p4(
                tenant_id=item.tenant_id,
                document_id=item.document_id,
                as_of=AS_OF,
                session=_Session(),
            )


def test_source_set_fingerprint_is_deterministic_across_insertion_order() -> None:
    early = _observation(
        document_id="document-target",
        occurred_at=datetime(2026, 9, 2, tzinfo=timezone.utc),
        content=b"early",
    )
    late = _observation(
        document_id="document-target",
        occurred_at=datetime(2026, 9, 20, tzinfo=timezone.utc),
        content=b"late",
    )

    first = LegalEvidenceUsageObservationRegistry(
        _Collection(
            [
                _row(late, idempotency_key="late"),
                _row(early, idempotency_key="early"),
            ]
        )
    ).get_complete_window_for_p4(
        tenant_id=early.tenant_id,
        document_id=early.document_id,
        as_of=AS_OF,
        session=_Session(),
    )

    second = LegalEvidenceUsageObservationRegistry(
        _Collection(
            [
                _row(early, idempotency_key="early"),
                _row(late, idempotency_key="late"),
            ]
        )
    ).get_complete_window_for_p4(
        tenant_id=early.tenant_id,
        document_id=early.document_id,
        as_of=AS_OF,
        session=_Session(),
    )

    assert first == second
    assert (
        first.source_observation_set_fingerprint
        == second.source_observation_set_fingerprint
    )


def test_complete_window_contains_no_remaining_or_reservation_authority() -> None:
    registry = LegalEvidenceUsageObservationRegistry(_Collection())

    window = registry.get_complete_window_for_p4(
        tenant_id="tenant-p3c-b",
        document_id="document-target",
        as_of=AS_OF,
        session=_Session(),
    )

    keys = set(window.to_dict())

    forbidden = {
        "remaining_storage_bytes",
        "remaining_ingress_bytes",
        "remaining_document_versions",
        "storage_exhausted",
        "ingress_exhausted",
        "versions_exhausted",
        "reservation_id",
        "reserved_bytes",
        "admitted",
        "price",
        "amount",
        "currency",
        "invoice",
        "payment",
        "settlement",
        "execution",
        "overage",
    }

    assert forbidden.isdisjoint(keys)


# ARTIFACT: test_legal_evidence_usage_observation_registry_p3c.py
# VERSION: v1.0.0-L10A2Q-P3C-B-COMPLETE-USAGE-RETRIEVAL-CERT
# AUTHORITY BOUNDARY: complete P3 observation aggregation only
# COMPLETENESS POSTURE: exhaustive tenant stream hydrated before temporal filtering
# TENANT POSTURE: exact tenant/document binding
# TRANSACTION POSTURE: caller-owned active transaction required
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
