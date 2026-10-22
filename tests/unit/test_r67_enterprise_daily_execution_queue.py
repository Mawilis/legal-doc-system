"""TITLE: R67 Enterprise Daily Execution Queue Adversarial Certificate.
VERSION: v1.0.0-R67-ENTERPRISE-DAILY-EXECUTION-QUEUE-CERT
AUTHORITY: Authenticated read-projection certification only.
EPITOME: Prove deterministic prioritization, visibility provenance, overlap
    deduplication and explicit non-authorizing daily-work semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_r67_enterprise_daily_execution_queue.py
COLLABORATION / OWNERSHIP: Legal Operations productive-work HTTP projection.
CERTIFICATION / UPDATE DATE: 2026-10-22
CHANGELOG: 2026-10-22 v1.0.0 establishes the R67 queue certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Synthetic exact-tenant and exact-principal projection only.
AUTHORITY BOUNDARY: No matter access, assignment, completion or execution grant.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from tools.eos.api.legal_operations_router import _productive_work_payload
from tools.eos.legal_operations.service.legal_profile_productive_work_read_service import (
    LegalProductiveWorkReadServiceError,
)


NOW = datetime(2026, 10, 22, 12, 0, tzinfo=UTC)


class Work:
    """Provide the bounded LegalWorkItem projection surface used by HTTP."""

    def __init__(
        self,
        work_item_id: str,
        *,
        status: str = "OPEN",
        due_at: datetime | None = None,
    ) -> None:
        self.work_item_id = work_item_id
        self.status = status
        self.due_at = due_at

    def to_dict(self) -> dict[str, object]:
        """Return the already-authorized bounded work projection."""
        return {
            "work_item_id": self.work_item_id,
            "case_matter_id": f"matter-{self.work_item_id}",
            "status": self.status,
            "due_at": self.due_at.isoformat() if self.due_at else None,
            "fingerprint": self.work_item_id.ljust(128, "a")[:128],
        }


def projection(
    *,
    assigned: tuple[Work, ...],
    supervised: tuple[Work, ...],
    overdue: tuple[Work, ...],
    due_soon: tuple[Work, ...],
) -> SimpleNamespace:
    """Build one exact-scope productive-work projection."""
    return SimpleNamespace(
        schema="WILSY-LEGAL-PROFILE-PRODUCTIVE-WORK/V1",
        version="test",
        tenant_id="tenant-r67",
        principal_id="principal-r67",
        as_of=NOW,
        operating_contexts=(),
        capability_ids=(),
        assigned_work_items=assigned,
        supervised_work_items=supervised,
        overdue_work_items=overdue,
        due_soon_work_items=due_soon,
    )


def test_queue_deduplicates_overlap_and_prioritizes_operational_exceptions() -> None:
    """Prove overdue, due-soon, blocked, scheduled and unscheduled ordering."""
    overdue = Work("overdue", due_at=NOW - timedelta(hours=1))
    due = Work("due", due_at=NOW + timedelta(hours=2))
    blocked = Work("blocked", status="BLOCKED")
    scheduled = Work("scheduled", due_at=NOW + timedelta(days=4))
    unscheduled = Work("unscheduled")

    payload = _productive_work_payload(
        projection(
            assigned=(unscheduled, due, overdue, blocked),
            supervised=(scheduled, overdue),
            overdue=(overdue,),
            due_soon=(due,),
        )
    )
    queue = payload["daily_execution_queue"]
    assert isinstance(queue, dict)
    items = queue["items"]
    assert isinstance(items, list)

    assert [item["work_item_id"] for item in items] == [
        "overdue",
        "due",
        "blocked",
        "scheduled",
        "unscheduled",
    ]
    assert [item["urgency"] for item in items] == [
        "OVERDUE",
        "DUE_SOON",
        "BLOCKED",
        "SCHEDULED",
        "UNSCHEDULED",
    ]
    assert items[0]["visibility_sources"] == ["ASSIGNMENT", "SUPERVISION"]
    assert queue["unique_active_count"] == 5
    assert queue["assignment_supervision_overlap_count"] == 1


def test_queue_is_deterministic_and_explicitly_non_authorizing() -> None:
    """Prove stable evidence identity and absence of implied authority."""
    first = Work("first", due_at=NOW + timedelta(hours=3))
    second = Work("second")
    value = projection(
        assigned=(second, first),
        supervised=(),
        overdue=(),
        due_soon=(first,),
    )

    left = _productive_work_payload(value)["daily_execution_queue"]
    right = _productive_work_payload(value)["daily_execution_queue"]
    assert left == right
    assert isinstance(left, dict)
    assert len(left["projection_fingerprint"]) == 128
    assert left["fact_classification"] == "DERIVED_OPERATIONAL_PROJECTION"
    assert left["execution_authority"] == "NOT_EVALUATED"
    assert left["permits_execution"] is False
    assert left["permits_assignment_mutation"] is False
    assert left["permits_confidential_matter_access"] is False


def test_queue_contains_no_clearance_or_command_evidence() -> None:
    """Prove the report cannot be confused with an authorization decision."""
    work = Work("bounded")
    serialized = repr(
        _productive_work_payload(
            projection(
                assigned=(work,),
                supervised=(),
                overdue=(),
                due_soon=(),
            )
        )["daily_execution_queue"]
    ).casefold()
    for forbidden in (
        "ethical_wall_clearance",
        "matter_access_authorized",
        "reviewer_approval",
        "assignment_authorized",
        "completion_authorized",
        "financial_execution",
    ):
        assert forbidden not in serialized


def test_divergent_same_identity_projection_fails_closed() -> None:
    """Prove inconsistent assignment and supervision snapshots cannot merge."""
    assigned = Work("collision", status="OPEN")
    supervised = Work("collision", status="BLOCKED")
    with pytest.raises(
        LegalProductiveWorkReadServiceError,
        match="R67_WORK_ITEM_PROJECTION_DIVERGENT",
    ):
        _productive_work_payload(
            projection(
                assigned=(assigned,),
                supervised=(supervised,),
                overdue=(),
                due_soon=(),
            )
        )


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_r67_enterprise_daily_execution_queue.py
# VERSION: v1.0.0-R67-ENTERPRISE-DAILY-EXECUTION-QUEUE-CERT
# AUTHORITY BOUNDARY: authenticated read projection certification only
# TENANT POSTURE: exact tenant and principal; no cross-scope fallback
# FAIL-CLOSED POSTURE: divergent or malformed work projection must reject
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
