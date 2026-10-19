"""P7 RED: completion-aware active productive-work visibility.

Completion authority remains immutable and separate.
This certificate does not create work completion or IAM truth.
"""

from tests.unit import (
    test_legal_profile_productive_work_read_service as fixture
)
from tools.eos.legal_operations.service.legal_profile_productive_work_read_service import (
    LegalProductiveWorkReadService,
)

class CompletionHistoryReader:
    """Minimal observable completion history boundary."""

    def __init__(self):
        self.calls = []

    def list_work_history(self, tenant_id, work_item_id, *, session):
        self.calls.append((tenant_id, work_item_id, session))
        # RED fixture: completion truth is injected via the
        # existing canonical registry boundary, not via work.status.
        return ()

def test_productive_work_requires_completion_history_boundary():
    work = fixture._work("p7-completion-work")
    assignment = fixture._assignment(
        "p7-assignment", "p7-completion-work"
    )
    reader = CompletionHistoryReader()

    service = LegalProductiveWorkReadService(
        work_item_registry=fixture._WorkItemRegistry((work,)),
        assignment_registry=fixture._AssignmentRegistry(
            (assignment,)
        ),
        supervision_registry=fixture._SupervisionRegistry(()),
        operating_context_hydrator=(
            fixture._OperatingContextHydrator(
                (fixture._context(),)
            )
        ),
        completion_registry=reader,
    )

    session = fixture._session()
    projection = service.project(
        tenant_id=fixture.TENANT,
        principal_id=fixture.PRINCIPAL,
        as_of=fixture.NOW,
        session=session,
    )

    assert tuple(
        item.work_item_id
        for item in projection.assigned_work_items
    ) == ("p7-completion-work",)

    assert reader.calls == [
        (fixture.TENANT, "p7-completion-work", session)
    ]

# P7_R9_GENUINE_COMPLETION_EVENT_CERTIFICATE

from datetime import timedelta
import pytest

from tests.unit.test_legal_work_completion_currentness import (
    completion as make_completion,
)
from tools.eos.legal_operations.service.legal_profile_productive_work_read_service import (
    LegalProductiveWorkReadServiceError,
)


class CompletionEvidenceRegistry:
    def __init__(self, events):
        self.events = events
        self.calls = []

    def list_work_history(self, tenant_id, work_item_id, *, session):
        self.calls.append((tenant_id, work_item_id, session))
        return self.events


def project_with_events(events_factory, *, at=None):
    work = fixture._work("p7-real-completion")
    assignment = fixture._assignment(
        "p7-real-assignment", work.work_item_id
    )
    reader = CompletionEvidenceRegistry(events_factory(work))
    service = LegalProductiveWorkReadService(
        work_item_registry=fixture._WorkItemRegistry((work,)),
        assignment_registry=fixture._AssignmentRegistry((assignment,)),
        supervision_registry=fixture._SupervisionRegistry(()),
        operating_context_hydrator=fixture._OperatingContextHydrator(
            (fixture._context(),)
        ),
        completion_registry=reader,
    )
    session = fixture._session()
    projection = service.project(
        tenant_id=fixture.TENANT,
        principal_id=fixture.PRINCIPAL,
        as_of=at or fixture.NOW + timedelta(hours=2),
        session=session,
    )
    return work, assignment, projection, reader, session


def test_completed_event_excludes_active_assigned_work():
    work, assignment, projection, reader, session = project_with_events(
        lambda item: (
            make_completion(
                item,
                completed_at=fixture.NOW + timedelta(hours=1),
                actor_principal_id=fixture.PRINCIPAL,
            ),
        )
    )
    assert projection.assigned_work_items == ()
    assert projection.overdue_work_items == ()
    assert projection.due_soon_work_items == ()
    assert str(work.status) in ("OPEN", "LegalWorkItemStatus.OPEN")
    assert assignment.work_item_id == work.work_item_id
    assert reader.calls == [
        (fixture.TENANT, work.work_item_id, session)
    ]


def test_future_completion_does_not_hide_work():
    work, _, projection, _, _ = project_with_events(
        lambda item: (
            make_completion(
                item,
                completed_at=fixture.NOW + timedelta(hours=3),
                actor_principal_id=fixture.PRINCIPAL,
            ),
        ),
        at=fixture.NOW + timedelta(hours=2),
    )
    assert [
        item.work_item_id
        for item in projection.assigned_work_items
    ] == [work.work_item_id]


def test_corrupt_completion_binding_fails_closed():
    with pytest.raises(
        (LegalProductiveWorkReadServiceError, ValueError)
    ):
        project_with_events(
            lambda item: (
                make_completion(
                    item,
                    work_item_id="different-work",
                    completed_at=fixture.NOW + timedelta(hours=1),
                ),
            )
        )


def test_divergent_completion_evidence_fails_closed():
    with pytest.raises(
        (LegalProductiveWorkReadServiceError, ValueError)
    ):
        project_with_events(
            lambda item: (
                make_completion(
                    item,
                    completion_evidence_reference="evidence:one",
                    completed_at=fixture.NOW + timedelta(hours=1),
                ),
                make_completion(
                    item,
                    completion_evidence_reference="evidence:two",
                    completed_at=fixture.NOW + timedelta(hours=1),
                ),
            )
        )
