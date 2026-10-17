"""
WILSY OS P14-R20R25 — R20R20 completion composition RED.

Frozen production topology:

    caller-owned active transaction
        -> R20R23 compose first-class R20R22 authority evidence
        -> R20R18 construct completion event
        -> completion registry create_or_replay

Exactly the same caller-owned session must span all three operations.

R20R20 must not:
- evaluate IAM directly;
- construct authorization provenance itself;
- manage transaction lifecycle;
- bypass R20R23;
- bypass R20R18;
- mutate adjacent workflow/dependency/financial state.
"""

from __future__ import annotations

from datetime import datetime, timezone
import inspect
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.domain.legal_work_completion_authority_evidence import (
    LegalWorkCompletionAuthorityEvidence,
)
from tools.eos.legal_operations.domain.legal_work_completion_event import (
    LegalWorkCompletionEvent,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
    LegalWorkItemStatus,
)
from tools.eos.legal_operations.orchestration import (
    legal_work_completion_persistence_orchestrator as orchestration,
)


TENANT = "tenant-r20r25"
MATTER = "matter-r20r25"
WORK_ID = "work-r20r25"
PRINCIPAL = "principal-r20r25"

AT = datetime(
    2026,
    10,
    17,
    7,
    30,
    tzinfo=timezone.utc,
)

SOURCE_FP = "a" * 128
ASSIGNMENT_FP = "b" * 128
IAM_FP = "c" * 128
COMPLETION_FP = "d" * 128


class _Session:
    in_transaction = True


class _InactiveSession:
    in_transaction = False


class _AuthorizationIssuer:
    def issue(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        operation: str,
        permission: str,
        subject_reference: str,
        subject_evidence_fingerprint: str,
        idempotency_key: str,
        session: object,
    ):
        raise AssertionError(
            "TEST_DOUBLE_ISSUE_MUST_NOT_BE_CALLED_DIRECTLY"
        )


class _Registry:
    def __init__(self) -> None:
        self.calls: list[
            tuple[
                LegalWorkCompletionEvent,
                object,
            ]
        ] = []

    def list_work_history(
        self,
        tenant_id: str,
        work_item_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalWorkCompletionEvent,
        ...,
    ]:
        """
        Satisfy the R20R28 read-only registry protocol for this R20R23 scenario.

        These historical orchestration tests exercise the no-prior-completion
        path, so the compatibility fake returns an empty immutable history.
        """
        return ()

    def create_or_replay(
        self,
        value: LegalWorkCompletionEvent,
        *,
        session: object,
    ) -> LegalWorkCompletionEvent:
        self.calls.append(
            (
                value,
                session,
            )
        )

        return value


def _work() -> LegalWorkItem:
    return LegalWorkItem(
        work_item_id=WORK_ID,
        tenant_id=TENANT,
        case_matter_id=MATTER,
        title="Complete governed legal work",
        source_kind="LEGAL_MATTER_WORKFLOW",
        source_reference="workflow:r20r25",
        source_evidence_fingerprint=SOURCE_FP,
        status=LegalWorkItemStatus.IN_PROGRESS,
        created_at=datetime(
            2026,
            10,
            10,
            8,
            0,
            tzinfo=timezone.utc,
        ),
    )


def _assignment() -> LegalWorkAssignment:
    return LegalWorkAssignment(
        assignment_id="assignment-r20r25",
        tenant_id=TENANT,
        case_matter_id=MATTER,
        work_item_id=WORK_ID,
        assignee_principal_id=PRINCIPAL,
        assigned_by_principal_id="principal-partner-r20r25",
        assigned_at=datetime(
            2026,
            10,
            16,
            9,
            0,
            tzinfo=timezone.utc,
        ),
        assignment_reason_reference="workflow-assignment:r20r25",
        authorization_evidence_reference="assignment-auth:r20r25",
    )


def _authority(
    work: LegalWorkItem,
) -> LegalWorkCompletionAuthorityEvidence:
    return LegalWorkCompletionAuthorityEvidence(
        completion_authority_evidence_id=(
            "completion-authority-r20r25"
        ),
        tenant_id=TENANT,
        case_matter_id=MATTER,
        work_item_id=WORK_ID,
        work_item_fingerprint=work.fingerprint,
        principal_id=PRINCIPAL,
        assignment_id="assignment-r20r25",
        assignment_fingerprint=ASSIGNMENT_FP,
        iam_authorization_evidence_reference=(
            "tenant-authorization:r20r25"
        ),
        iam_authorization_evidence_fingerprint=IAM_FP,
        evaluated_at=AT,
    )


def _event(
    work: LegalWorkItem,
    authority: LegalWorkCompletionAuthorityEvidence,
) -> LegalWorkCompletionEvent:
    return LegalWorkCompletionEvent(
        tenant_id=TENANT,
        case_matter_id=MATTER,
        work_item_id=WORK_ID,
        work_item_fingerprint=work.fingerprint,
        completion_evidence_reference=(
            "completion:evidence:r20r25"
        ),
        completion_evidence_fingerprint=COMPLETION_FP,
        completed_at=authority.evaluated_at,
        actor_principal_id=authority.principal_id,
        authorization_evidence_reference=(
            authority.completion_authority_evidence_reference
        ),
        authorization_evidence_fingerprint=(
            authority.fingerprint
        ),
    )


def test_r20r20_surface_uses_authorization_evidence_issuer_not_iam_repositories():
    parameters = set(
        inspect.signature(
            orchestration.record_legal_work_completion
        ).parameters
    )

    assert "authorization_evidence_issuer" in parameters

    for forbidden in (
        "principal_repository",
        "membership_repository",
        "role_assignment_repository",
        "business_role_repository",
    ):
        assert forbidden not in parameters


def test_inactive_transaction_rejects_before_composition(
    monkeypatch: pytest.MonkeyPatch,
):
    composer_calls: list[dict[str, Any]] = []

    def fake_compose(**kwargs: Any):
        composer_calls.append(kwargs)
        raise AssertionError(
            "COMPOSER_MUST_NOT_RUN"
        )

    monkeypatch.setattr(
        orchestration,
        "compose_legal_work_completion_authority_evidence",
        fake_compose,
        raising=False,
    )

    with pytest.raises(Exception):
        orchestration.record_legal_work_completion(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            work_item=_work(),
            assignments=(_assignment(),),
            completion_evidence_reference=(
                "completion:evidence:r20r25"
            ),
            completion_evidence_fingerprint=COMPLETION_FP,
            evaluated_at=AT,
            authorization_evidence_issuer=(
                _AuthorizationIssuer()
            ),
            completion_registry=_Registry(),
            session=_InactiveSession(),
        )

    assert composer_calls == []


def test_one_composer_one_prepare_one_registry_same_exact_session(
    monkeypatch: pytest.MonkeyPatch,
):
    session = _Session()
    issuer = _AuthorizationIssuer()
    registry = _Registry()

    work = _work()
    assignments = (_assignment(),)
    authority = _authority(work)
    event = _event(
        work,
        authority,
    )

    composer_calls: list[
        dict[str, Any]
    ] = []

    prepare_calls: list[
        dict[str, Any]
    ] = []

    order: list[str] = []

    def fake_compose(
        **kwargs: Any,
    ) -> LegalWorkCompletionAuthorityEvidence:
        order.append("compose")
        composer_calls.append(kwargs)
        return authority

    def fake_prepare(
        **kwargs: Any,
    ) -> LegalWorkCompletionEvent:
        order.append("prepare")
        prepare_calls.append(kwargs)
        return event

    original_create = registry.create_or_replay

    def observed_create(
        value: LegalWorkCompletionEvent,
        *,
        session: object,
    ) -> LegalWorkCompletionEvent:
        order.append("persist")
        return original_create(
            value,
            session=session,
        )

    registry.create_or_replay = observed_create  # type: ignore[method-assign]

    monkeypatch.setattr(
        orchestration,
        "compose_legal_work_completion_authority_evidence",
        fake_compose,
        raising=False,
    )

    monkeypatch.setattr(
        orchestration,
        "prepare_legal_work_completion_event",
        fake_prepare,
    )

    result = orchestration.record_legal_work_completion(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        work_item=work,
        assignments=assignments,
        completion_evidence_reference=(
            "completion:evidence:r20r25"
        ),
        completion_evidence_fingerprint=COMPLETION_FP,
        evaluated_at=AT,
        authorization_evidence_issuer=issuer,
        completion_registry=registry,
        session=session,
    )

    assert result is event
    assert order == [
        "compose",
        "prepare",
        "persist",
    ]

    assert len(composer_calls) == 1
    assert len(prepare_calls) == 1
    assert len(registry.calls) == 1

    compose_call = composer_calls[0]

    assert compose_call == {
        "tenant_id": TENANT,
        "principal_id": PRINCIPAL,
        "work_item": work,
        "assignments": assignments,
        "evaluated_at": AT,
        "authorization_evidence_issuer": issuer,
        "session": session,
    }

    prepare_call = prepare_calls[0]

    assert prepare_call == {
        "work_item": work,
        "completion_authority_evidence": authority,
        "completion_evidence_reference": (
            "completion:evidence:r20r25"
        ),
        "completion_evidence_fingerprint": COMPLETION_FP,
    }

    persisted, persisted_session = registry.calls[0]

    assert persisted is event
    assert persisted_session is session


def test_r20r20_does_not_pass_session_into_pure_r20r18(
    monkeypatch: pytest.MonkeyPatch,
):
    work = _work()
    authority = _authority(work)

    observed: list[
        dict[str, Any]
    ] = []

    def fake_compose(
        **kwargs: Any,
    ) -> LegalWorkCompletionAuthorityEvidence:
        return authority

    def fake_prepare(
        **kwargs: Any,
    ) -> LegalWorkCompletionEvent:
        observed.append(kwargs)

        assert "session" not in kwargs
        assert "evaluated_at" not in kwargs
        assert "assignments" not in kwargs
        assert "principal_id" not in kwargs
        assert "tenant_id" not in kwargs

        return _event(
            work,
            authority,
        )

    monkeypatch.setattr(
        orchestration,
        "compose_legal_work_completion_authority_evidence",
        fake_compose,
        raising=False,
    )

    monkeypatch.setattr(
        orchestration,
        "prepare_legal_work_completion_event",
        fake_prepare,
    )

    orchestration.record_legal_work_completion(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        work_item=work,
        assignments=(_assignment(),),
        completion_evidence_reference=(
            "completion:evidence:r20r25"
        ),
        completion_evidence_fingerprint=COMPLETION_FP,
        evaluated_at=AT,
        authorization_evidence_issuer=(
            _AuthorizationIssuer()
        ),
        completion_registry=_Registry(),
        session=_Session(),
    )

    assert len(observed) == 1


def test_r20r20_contains_no_direct_iam_evaluation_or_provenance_hashing():
    source = inspect.getsource(
        orchestration
    )

    for forbidden in (
        "authorize_tenant_operation",
        "authorize_legal_work_completion",
        "_authorization_payload",
        "_authorization_fingerprint",
        "_authorization_reference",
    ):
        assert forbidden not in source


def test_r20r20_does_not_manage_transaction_lifecycle():
    source = inspect.getsource(
        orchestration
    )

    for forbidden in (
        "start_transaction(",
        "commit_transaction(",
        "abort_transaction(",
        "with_transaction(",
    ):
        assert forbidden not in source


def test_r20r20_has_no_adjacent_execution_authority():
    parameters = set(
        inspect.signature(
            orchestration.record_legal_work_completion
        ).parameters
    )

    for forbidden in (
        "workflow_transition_id",
        "dependency_id",
        "supervisor_principal_id",
        "notification_id",
        "legal_event_id",
        "invoice_id",
        "payment_id",
        "settlement_id",
    ):
        assert forbidden not in parameters
