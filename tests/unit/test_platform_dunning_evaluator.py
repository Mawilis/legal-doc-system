from datetime import datetime, timezone

import pytest

from tools.eos.saas.billing.platform_dunning_evaluator import (
    PlatformDunningEvaluationError,
    aggregate_overdue_invoices,
    evaluate_platform_dunning,
    state_for_days,
)


NOW = datetime(2026, 11, 4, 12, tzinfo=timezone.utc)
POLICY = {
    "reminder_day": 3,
    "warning_day": 7,
    "critical_day": 10,
    "suspension_day": 14,
    "collections_day": 21,
    "termination_day": 30,
}


class ProjectionCollection:
    def __init__(self):
        self.documents = []

    def find_one(self, query, *, session=None):
        return next((dict(row) for row in self.documents if all(row.get(k) == v for k, v in query.items())), None)

    def find(self, query, *, session=None):
        return [dict(row) for row in self.documents if all(row.get(k) == v for k, v in query.items())]

    def insert_one(self, document, *, session=None):
        self.documents.append(dict(document))

    def update_one(self, query, update, *, session=None):
        for row in self.documents:
            if all(row.get(k) == v for k, v in query.items()):
                row.update(update["$set"])
                return type("Result", (), {"matched_count": 1})()
        return type("Result", (), {"matched_count": 0})()


def invoice(invoice_id, subscription_id, due_at, status="open", tenant="tenant-a"):
    return {
        "tenant_id": tenant,
        "subscription_id": subscription_id,
        "invoice_id": invoice_id,
        "due_at": due_at,
        "status": status,
    }


def test_multiple_invoices_aggregate_to_one_deterministic_subscription_transition():
    rows = [
        invoice("inv-newer", "sub-1", "2026-10-28T00:00:00+00:00"),
        invoice("inv-older", "sub-1", "2026-10-01T00:00:00+00:00"),
        invoice("inv-paid", "sub-1", "2026-09-01T00:00:00+00:00", status="paid"),
        invoice("inv-other-tenant", "sub-2", "2026-10-01T00:00:00+00:00", tenant="tenant-b"),
    ]
    groups = aggregate_overdue_invoices(rows, tenant_id="tenant-a", now=NOW)
    assert list(groups) == ["sub-1"]
    assert groups["sub-1"]["invoice_ids"] == ("inv-newer", "inv-older")
    assert groups["sub-1"]["days_overdue"] == 34


def test_evaluator_writes_one_projection_and_never_claims_lifecycle_mutation():
    collection = ProjectionCollection()
    rows = [
        invoice("inv-a", "sub-1", "2026-10-28T00:00:00+00:00"),
        invoice("inv-b", "sub-1", "2026-10-20T00:00:00+00:00"),
    ]
    result = evaluate_platform_dunning(
        tenant_id="tenant-a",
        invoices=rows,
        policy=POLICY,
        projection_collection=collection,
        now=NOW,
    )
    assert result["transition_count"] == 1
    assert result["transitions"][0]["state"] == "SUSPENSION_REVIEW"
    assert result["subscription_lifecycle_mutated"] is False
    assert len(collection.documents) == 1


def test_dry_run_does_not_persist():
    collection = ProjectionCollection()
    result = evaluate_platform_dunning(
        tenant_id="tenant-a",
        invoices=[invoice("inv-a", "sub-1", "2026-10-20T00:00:00+00:00")],
        policy=POLICY,
        projection_collection=collection,
        now=NOW,
        dry_run=True,
    )
    assert result["transition_count"] == 1
    assert collection.documents == []


def test_terminal_invoices_are_excluded_and_policy_must_be_monotonic():
    rows = [
        invoice("inv-void", "sub-1", "2026-10-01T00:00:00+00:00", status="void"),
        invoice("inv-draft", "sub-1", "2026-10-01T00:00:00+00:00", status="draft"),
        invoice("inv-pending", "sub-1", "2026-10-01T00:00:00+00:00", status="pending"),
        invoice("inv-unknown", "sub-1", "2026-10-01T00:00:00+00:00", status="mystery"),
    ]
    assert aggregate_overdue_invoices(rows, tenant_id="tenant-a", now=NOW) == {}
    invalid = dict(POLICY, termination_day=2)
    with pytest.raises(PlatformDunningEvaluationError, match="NOT_MONOTONIC"):
        evaluate_platform_dunning(
            tenant_id="tenant-a",
            invoices=[],
            policy=invalid,
            projection_collection=ProjectionCollection(),
            now=NOW,
        )


def test_below_warning_threshold_does_not_create_noop_active_projection():
    collection = ProjectionCollection()
    result = evaluate_platform_dunning(
        tenant_id="tenant-a",
        invoices=[invoice("inv-a", "sub-1", "2026-11-03T00:00:00+00:00")],
        policy=POLICY,
        projection_collection=collection,
        now=NOW,
    )
    assert result["evaluated_subscriptions"] == 1
    assert result["transition_count"] == 0
    assert collection.documents == []


@pytest.mark.parametrize(
    ("days", "expected"),
    [
        (2, "ACTIVE"),
        (3, "REMINDER"),
        (7, "WARNING"),
        (10, "CRITICAL"),
        (14, "SUSPENSION_REVIEW"),
        (21, "COLLECTIONS_REVIEW"),
        (30, "TERMINATION_REVIEW"),
    ],
)
def test_policy_ladder_selects_one_deterministic_collection_stage(days, expected):
    assert state_for_days(days, POLICY) == expected


def test_malformed_due_date_fails_closed():
    rows = [invoice("inv-a", "sub-1", "not-a-date")]
    with pytest.raises(PlatformDunningEvaluationError, match="DUE_AT_INVALID"):
        aggregate_overdue_invoices(rows, tenant_id="tenant-a", now=NOW)


def test_settled_invoice_resolves_existing_projection():
    collection = ProjectionCollection()
    first = evaluate_platform_dunning(
        tenant_id="tenant-a",
        invoices=[invoice("inv-a", "sub-1", "2026-10-20T00:00:00+00:00")],
        policy=POLICY,
        projection_collection=collection,
        now=NOW,
    )
    assert first["transitions"][0]["state"] == "SUSPENSION_REVIEW"
    settled = evaluate_platform_dunning(
        tenant_id="tenant-a",
        invoices=[invoice("inv-a", "sub-1", "2026-10-20T00:00:00+00:00", status="paid")],
        policy=POLICY,
        projection_collection=collection,
        now=NOW,
    )
    assert settled["transitions"][0]["state"] == "RESOLVED"
    assert collection.documents[0]["state"] == "RESOLVED"


def test_partial_settlement_can_reduce_stage_for_remaining_invoice_evidence():
    collection = ProjectionCollection()
    evaluate_platform_dunning(
        tenant_id="tenant-a",
        invoices=[
            invoice("inv-old", "sub-1", "2026-10-01T00:00:00+00:00"),
            invoice("inv-new", "sub-1", "2026-10-30T00:00:00+00:00"),
        ],
        policy=POLICY,
        projection_collection=collection,
        now=NOW,
    )
    result = evaluate_platform_dunning(
        tenant_id="tenant-a",
        invoices=[
            invoice("inv-old", "sub-1", "2026-10-01T00:00:00+00:00", status="paid"),
            invoice("inv-new", "sub-1", "2026-10-30T00:00:00+00:00"),
        ],
        policy=POLICY,
        projection_collection=collection,
        now=NOW,
    )
    assert result["transitions"][0]["state"] == "REMINDER"
    assert result["transitions"][0]["invoice_ids"] == ["inv-new"]
