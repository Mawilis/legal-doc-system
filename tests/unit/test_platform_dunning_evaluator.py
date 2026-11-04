from datetime import datetime, timezone

import pytest

from tools.eos.saas.billing.platform_dunning_evaluator import (
    PlatformDunningEvaluationError,
    aggregate_overdue_invoices,
    evaluate_platform_dunning,
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
    rows = [invoice("inv-a", "sub-1", "2026-10-01T00:00:00+00:00", status="void")]
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
