"""R66 workday summary remains explicitly non-authorizing."""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from tools.eos.api.legal_operations_router import (
    _productive_work_payload,
)


class Work:
    def __init__(self, work_id: str) -> None:
        self.work_id = work_id

    def to_dict(self) -> dict[str, str]:
        return {"work_item_id": self.work_id}


def projection(
    *,
    assigned: int = 0,
    supervised: int = 0,
    overdue: int = 0,
    due_soon: int = 0,
) -> SimpleNamespace:
    def items(prefix: str, count: int) -> tuple[Work, ...]:
        return tuple(Work(f"{prefix}-{i}") for i in range(count))

    return SimpleNamespace(
        schema="WILSY-TEST-PRODUCTIVE-WORK",
        version="test",
        tenant_id="tenant-r66",
        principal_id="principal-r66",
        as_of=datetime(2026, 10, 22, tzinfo=timezone.utc),
        operating_contexts=(),
        capability_ids=(),
        assigned_work_items=items("assigned", assigned),
        supervised_work_items=items("supervised", supervised),
        overdue_work_items=items("overdue", overdue),
        due_soon_work_items=items("due", due_soon),
    )


def payload_summary(payload: dict[str, object]) -> dict[str, object]:
    value = payload["workday_summary"]
    assert isinstance(value, dict)
    assert all(isinstance(key, str) for key in value)
    return value


def payload_items(payload: dict[str, object], name: str) -> list[object]:
    value = payload[name]
    assert isinstance(value, list)
    return value


@pytest.mark.parametrize(
    ("assigned", "supervised", "overdue", "due_soon"),
    [
        (0, 0, 0, 0),
        (1, 0, 0, 0),
        (2, 3, 1, 4),
        (8, 5, 2, 6),
    ],
)
def test_summary_matches_scoped_projection(
    assigned: int,
    supervised: int,
    overdue: int,
    due_soon: int,
) -> None:
    payload = _productive_work_payload(
        projection(
            assigned=assigned,
            supervised=supervised,
            overdue=overdue,
            due_soon=due_soon,
        )
    )

    assert payload_summary(payload) == {
        "assigned_count": assigned,
        "supervised_count": supervised,
        "overdue_count": overdue,
        "due_soon_count": due_soon,
        "execution_authority": "NOT_EVALUATED",
        "permits_execution": False,
        "permits_confidential_matter_access": False,
    }

    assert len(payload_items(payload, "assigned_work_items")) == assigned
    assert len(payload_items(payload, "supervised_work_items")) == supervised
    assert len(payload_items(payload, "overdue_work_items")) == overdue
    assert len(payload_items(payload, "due_soon_work_items")) == due_soon


def test_summary_grants_no_authority() -> None:
    payload = _productive_work_payload(
        projection(assigned=1, supervised=1)
    )
    summary = payload_summary(payload)

    assert summary["execution_authority"] == "NOT_EVALUATED"
    assert summary["permits_execution"] is False
    assert summary["permits_confidential_matter_access"] is False

    for forbidden in (
        "authorization_evidence",
        "matter_content",
        "reviewer_approval",
        "ethical_wall_clearance",
    ):
        assert forbidden not in summary
