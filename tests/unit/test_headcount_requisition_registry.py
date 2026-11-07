from datetime import datetime, timezone

import pytest

from tools.eos.saas.domain.headcount_requisition import (
    HeadcountApproval, HeadcountRequisition, RequisitionDecision,
)
from tools.eos.saas.hr.headcount_requisition_registry import (
    HeadcountRequisitionNotFound, HeadcountRequisitionRegistry,
    HeadcountRequisitionRegistryConflict, HeadcountRequisitionRegistryError,
)

NOW = datetime(2026, 11, 7, 10, tzinfo=timezone.utc)
TENANT = "WILSYTENANT-4CD2FZ4O"


class Collection:
    def __init__(self):
        self.rows = []
        self.indexes = []

    def create_index(self, keys, **kwargs):
        self.indexes.append((keys, kwargs))

    def find_one(self, query, session=None):
        assert session is not None
        return next((r for r in self.rows if all(r.get(k) == v for k, v in query.items())), None)

    def insert_one(self, document, session=None):
        assert session is not None
        self.rows.append(dict(document))

    def update_one(self, query, update, session=None):
        assert session is not None
        row = self.find_one(query, session=session)
        if row is None:
            return type("Result", (), {"matched_count": 0})()
        row.update(update["$set"])
        return type("Result", (), {"matched_count": 1})()


def make_requisition(tenant=TENANT):
    return HeadcountRequisition(
        tenant_id=tenant, requisition_id="REQ-001", department_id="engineering",
        position_title="Software Engineer", employment_type="PERMANENT",
        work_location="Johannesburg", headcount=1,
        business_justification="Approved product delivery capacity",
        requested_by_principal_id="principal-requester",
    )


def make_registry():
    current, events = Collection(), Collection()
    return HeadcountRequisitionRegistry(current, events), current, events


def test_registry_requires_both_collections_and_caller_transaction():
    with pytest.raises(HeadcountRequisitionRegistryError):
        HeadcountRequisitionRegistry(None, Collection())
    registry, _, _ = make_registry()
    with pytest.raises(HeadcountRequisitionRegistryError, match="SESSION_REQUIRED"):
        registry.create_or_replay(
            make_requisition(), idempotency_key="create-1",
            actor_principal_id="principal-requester", occurred_at=NOW, session=None,
        )


def test_create_and_event_are_written_in_same_caller_transaction_and_replay_exactly():
    registry, current, events = make_registry()
    item = make_requisition()
    assert registry.create_or_replay(
        item, idempotency_key="create-1", actor_principal_id="principal-requester",
        occurred_at=NOW, session=object(),
    ) == item
    assert len(current.rows) == 1
    assert len(events.rows) == 1
    assert events.rows[0]["event_type"] == "HEADCOUNT_REQUISITION_CREATED"
    assert registry.create_or_replay(
        item, idempotency_key="create-1", actor_principal_id="principal-requester",
        occurred_at=NOW, session=object(),
    ) == item
    changed = make_requisition()
    changed = HeadcountRequisition(
        **{**changed.to_dict(), "business_justification": "Different request", "fingerprint": ""}
    )
    with pytest.raises(HeadcountRequisitionRegistryConflict):
        registry.create_or_replay(
            changed, idempotency_key="create-1", actor_principal_id="principal-requester",
            occurred_at=NOW, session=object(),
        )


def test_reads_are_exact_tenant_scoped_and_corruption_does_not_become_empty():
    registry, _, _ = make_registry()
    item = make_requisition()
    registry.create_or_replay(
        item, idempotency_key="create-1", actor_principal_id="principal-requester",
        occurred_at=NOW, session=object(),
    )
    assert registry.get(tenant_id=TENANT, requisition_id="REQ-001", session=object()) == item
    with pytest.raises(HeadcountRequisitionNotFound):
        registry.get(tenant_id="OTHER-TENANT", requisition_id="REQ-001", session=object())


def test_submit_transition_uses_revision_cas_and_appends_immutable_event():
    registry, current, events = make_registry()
    item = make_requisition()
    registry.create_or_replay(
        item, idempotency_key="create-1", actor_principal_id="principal-requester",
        occurred_at=NOW, session=object(),
    )
    submitted = item.submit(
        actor_principal_id="principal-requester", submitted_at=NOW, expected_revision=1,
    )
    saved = registry.transition(
        tenant_id=TENANT, requisition_id=item.requisition_id, expected_revision=1,
        updated=submitted, action="SUBMITTED", actor_principal_id="principal-requester",
        idempotency_key="submit-1", request_fingerprint="a" * 128, occurred_at=NOW, session=object(),
    )
    assert saved == submitted
    assert current.rows[0]["revision"] == 2
    assert len(events.rows) == 2
    replay = registry.replay_transition(
        tenant_id=TENANT, idempotency_key="submit-1",
        request_fingerprint="a" * 128, session=object(),
    )
    assert replay == submitted
    with pytest.raises(HeadcountRequisitionRegistryConflict, match="DIVERGENT"):
        registry.replay_transition(
            tenant_id=TENANT, idempotency_key="submit-1",
            request_fingerprint="z" * 128, session=object(),
        )
    with pytest.raises(HeadcountRequisitionRegistryConflict, match="REVISION_CONFLICT"):
        registry.transition(
            tenant_id=TENANT, requisition_id=item.requisition_id, expected_revision=1,
            updated=submitted, action="SUBMITTED", actor_principal_id="principal-requester",
            idempotency_key="submit-2", request_fingerprint="b" * 128, occurred_at=NOW, session=object(),
        )


def test_approval_maker_checker_and_event_revision_are_preserved():
    registry, _, events = make_registry()
    item = make_requisition()
    registry.create_or_replay(
        item, idempotency_key="create-1", actor_principal_id="principal-requester",
        occurred_at=NOW, session=object(),
    )
    submitted = item.submit(
        actor_principal_id="principal-requester", submitted_at=NOW, expected_revision=1,
    )
    registry.transition(
        tenant_id=TENANT, requisition_id=item.requisition_id, expected_revision=1,
        updated=submitted, action="SUBMITTED", actor_principal_id="principal-requester",
        idempotency_key="submit-1", request_fingerprint="d" * 128, occurred_at=NOW, session=object(),
    )
    approved = submitted.decide(
        HeadcountApproval(
            decision_id="decision-1", actor_principal_id="independent-approver",
            decision=RequisitionDecision.APPROVE, reason="Headcount approved",
            decided_at=NOW,
        ),
        expected_revision=2,
    )
    registry.transition(
        tenant_id=TENANT, requisition_id=item.requisition_id, expected_revision=2,
        updated=approved, action="APPROVED", actor_principal_id="independent-approver",
        idempotency_key="approve-1", request_fingerprint="c" * 128, occurred_at=NOW, session=object(),
    )
    assert events.rows[-1]["revision"] == 3
    assert events.rows[-1]["prior_fingerprint"] == submitted.fingerprint
    assert events.rows[-1]["result_fingerprint"] == approved.fingerprint


def test_indexes_are_tenant_first_and_event_revision_unique():
    registry, current, events = make_registry()
    registry.ensure_indexes(current, events)
    assert len(current.indexes) == 2
    assert len(events.indexes) == 2
    assert all(keys[0][0] == "tenant_id" for keys, _ in current.indexes + events.indexes)
    assert events.indexes[-1][1]["unique"] is True
