"""TITLE: WILSY EOS hiring registry tenant-scoped page regressions.
VERSION: v1.0.1-BOUNDED-TENANT-PAGES-CERT
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Proves candidate and offer list reads remain tenant-scoped,
         deterministic, bounded, transaction-bound, and fail closed.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hiring_lifecycle_registry_pages.py
COLLABORATION / OWNERSHIP: Direct regression coverage for hiring_lifecycle_registry.py.
CERTIFICATION / UPDATE DATE: 2026-11-12.
CHANGELOG: v1.0.1-BOUNDED-TENANT-PAGES-CERT aligns the first certified header, changelog and seal versions; test assertions are unchanged. v1.0.0-BOUNDED-TENANT-PAGES establishes page isolation, order, bounds, corruption, and database-failure tests.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic tenant and aggregate identifiers only; no network or database writes.
TENANT BOUNDARY: Each page must filter by one exact tenant and ignore other-tenant records.
AUTHORITY BOUNDARY: Tests persistence reads only; the HTTP caller remains responsible for authorization.
FINANCIAL AUTHORITY BOUNDARY: No payroll, payment, execution, or settlement authority.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import PyMongoError

from tools.eos.saas.domain.hiring_lifecycle import (
    CandidateApplication,
    EmploymentOffer,
    OfferTerms,
)
from tools.eos.saas.hr.hiring_lifecycle_registry import (
    HiringLifecycleRegistry,
    HiringLifecycleRegistryError,
)

NOW = datetime(2026, 11, 12, 10, tzinfo=timezone.utc)


class _Cursor:
    """Small deterministic cursor double for read-only page behavior."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def sort(self, ordering: list[tuple[str, int]]) -> _Cursor:
        for field, direction in reversed(ordering):
            self._rows.sort(
                key=lambda row: row[field],
                reverse=direction == DESCENDING,
            )
        return self

    def skip(self, count: int) -> _Cursor:
        self._rows = self._rows[count:]
        return self

    def limit(self, count: int) -> _Cursor:
        self._rows = self._rows[:count]
        return self

    def __iter__(self):
        return iter(self._rows)


class _Collection:
    """Tenant-filtering collection double with observable session use."""

    def __init__(self, rows: list[dict[str, Any]] | None = None,
                 *, fail_count: bool = False) -> None:
        self.rows = rows or []
        self.fail_count = fail_count
        self.calls: list[tuple[str, dict[str, object], object]] = []

    def count_documents(self, query: dict[str, object], *, session: object) -> int:
        self.calls.append(("count", query, session))
        if self.fail_count:
            raise PyMongoError("test database unavailable")
        return sum(all(row.get(key) == value for key, value in query.items()) for row in self.rows)

    def find(self, query: dict[str, object], *, session: object) -> _Cursor:
        self.calls.append(("find", query, session))
        matched = [
            dict(row) for row in self.rows
            if all(row.get(key) == value for key, value in query.items())
        ]
        return _Cursor(matched)


def _candidate(tenant_id: str, candidate_id: str, created_at: datetime) -> CandidateApplication:
    """Build one synthetic candidate with source-valid canonical fields."""
    return CandidateApplication(
        tenant_id=tenant_id,
        candidate_id=candidate_id,
        requisition_id="REQ-TEST-1",
        candidate_profile_reference=f"candidate-profile://opaque/{candidate_id}",
        source="TEST_FIXTURE",
        created_by_principal_id="principal-test-hr",
        created_at=created_at,
    )


def _offer(tenant_id: str, offer_id: str, created_at: datetime) -> EmploymentOffer:
    """Build one synthetic offer without transmitting personal data."""
    return EmploymentOffer(
        tenant_id=tenant_id,
        offer_id=offer_id,
        requisition_id="REQ-TEST-1",
        candidate_id="CAN-TEST-1",
        terms=OfferTerms(
            position_title="Test Engineer",
            employment_type="PERMANENT",
            work_location="Johannesburg",
            currency="ZAR",
            gross_compensation_minor=100000,
            pay_frequency="MONTHLY",
            start_date=date(2027, 1, 1),
            expires_at=created_at + timedelta(days=21),
        ),
        prepared_by_principal_id="principal-test-hr",
        created_at=created_at,
    )


def _registry(candidates: _Collection | None = None,
              offers: _Collection | None = None) -> HiringLifecycleRegistry:
    """Compose registry against read-only test doubles."""
    return HiringLifecycleRegistry(
        candidates or _Collection(),
        offers or _Collection(),
        _Collection(),
    )


def test_candidate_pages_filter_exact_tenant_and_sort_stably_with_caller_session() -> None:
    """Candidate pages exclude other tenants and share the supplied read session."""
    tenant = "tenant-hiring-page-a"
    session = object()
    older = _candidate(tenant, "CAN-OLDER", NOW - timedelta(hours=1))
    newer = _candidate(tenant, "CAN-NEWER", NOW)
    other = _candidate("tenant-hiring-page-b", "CAN-OTHER", NOW + timedelta(hours=1))
    collection = _Collection([older.to_dict(), newer.to_dict(), other.to_dict()])
    registry = _registry(candidates=collection)

    first, total = registry.list_candidates(
        tenant_id=tenant, limit=1, offset=0, session=session,
    )
    second, second_total = registry.list_candidates(
        tenant_id=tenant, limit=1, offset=1, session=session,
    )

    assert first == [newer]
    assert second == [older]
    assert total == second_total == 2
    assert collection.calls == [
        ("count", {"tenant_id": tenant}, session),
        ("find", {"tenant_id": tenant}, session),
        ("count", {"tenant_id": tenant}, session),
        ("find", {"tenant_id": tenant}, session),
    ]


def test_offer_pages_filter_exact_tenant_and_do_not_expose_other_tenant_terms() -> None:
    """Offer pages return only the requested tenant's source-owned records."""
    tenant = "tenant-offer-page-a"
    session = object()
    current = _offer(tenant, "OFFER-CURRENT", NOW)
    other = _offer("tenant-offer-page-b", "OFFER-OTHER", NOW + timedelta(days=1))
    collection = _Collection([other.to_dict(), current.to_dict()])
    registry = _registry(offers=collection)

    values, total = registry.list_offers(
        tenant_id=tenant, limit=20, offset=0, session=session,
    )

    assert values == [current]
    assert total == 1
    assert collection.calls == [
        ("count", {"tenant_id": tenant}, session),
        ("find", {"tenant_id": tenant}, session),
    ]


@pytest.mark.parametrize(
    ("limit", "offset", "code"),
    [
        (0, 0, "HIRING_PAGE_LIMIT_INVALID"),
        (101, 0, "HIRING_PAGE_LIMIT_INVALID"),
        (True, 0, "HIRING_PAGE_LIMIT_INVALID"),
        (10, -1, "HIRING_PAGE_OFFSET_INVALID"),
        (10, 1_000_001, "HIRING_PAGE_OFFSET_INVALID"),
    ],
)
def test_candidate_pages_reject_invalid_bounds_before_database_access(
    limit: int, offset: int, code: str,
) -> None:
    """Invalid pagination cannot cause unbounded or ambiguous reads."""
    collection = _Collection()
    with pytest.raises(HiringLifecycleRegistryError) as captured:
        _registry(candidates=collection).list_candidates(
            tenant_id="tenant-hiring-page-a",
            limit=limit,
            offset=offset,
            session=object(),
        )
    assert captured.value.code == code
    assert collection.calls == []


def test_candidate_pages_fail_closed_on_corrupt_records_and_database_errors() -> None:
    """Invalid persisted fingerprints and Mongo read failures stay unavailable."""
    tenant = "tenant-hiring-page-a"
    session = object()
    corrupt = _candidate(tenant, "CAN-CORRUPT", NOW).to_dict()
    corrupt["fingerprint"] = "0" * 128
    with pytest.raises(HiringLifecycleRegistryError) as corrupt_error:
        _registry(candidates=_Collection([corrupt])).list_candidates(
            tenant_id=tenant, limit=10, offset=0, session=session,
        )
    assert corrupt_error.value.code == "HIRING_CANDIDATE_DOCUMENT_CORRUPT"

    with pytest.raises(HiringLifecycleRegistryError) as read_error:
        _registry(candidates=_Collection(fail_count=True)).list_candidates(
            tenant_id=tenant, limit=10, offset=0, session=session,
        )
    assert read_error.value.code == "HIRING_LIST_READ_UNAVAILABLE"


# ARTIFACT: tests/unit/test_hiring_lifecycle_registry_pages.py
# VERSION: v1.0.1-BOUNDED-TENANT-PAGES-CERT
# AUTHORITY BOUNDARY: Registry page behavior only; HTTP authorization is outside this test.
# TENANT POSTURE: Synthetic exact-tenant scope and records only.
# FAIL-CLOSED POSTURE: Invalid bounds, corrupt records, and database errors reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
