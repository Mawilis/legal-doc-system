"""
WILSY OS P14-R20R28 — Legal work completion persistence orchestration.

This suite preserves the certified R20R25 caller-owned transaction topology
and adds the R20R28 replay-first persistence contract.

Frozen topology:

    caller-owned active transaction
        -> durable completion-history replay adjudication
        -> R20R23 canonical authority composition when no completion exists
        -> R20R18 pure completion-event preparation
        -> completion registry create_or_replay

R20R28 owns persistence sequencing and replay adjudication only.

It does not:
- evaluate IAM directly;
- accept IAM repositories;
- synthesize authorization provenance;
- pass transaction/session into R20R18;
- manage transaction lifecycle;
- execute workflow, dependency, notification, legal-event or financial work.
"""

from __future__ import annotations

from datetime import datetime, timezone
import inspect
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


TENANT = "tenant-r20r25-contract"
MATTER = "matter-r20r25-contract"
WORK_ID = "work-r20r25-contract"
PRINCIPAL = "principal-r20r25-contract"

AT = datetime(
    2026,
    10,
    17,
    8,
    0,
    tzinfo=timezone.utc,
)

SOURCE_FP = "a" * 128
ASSIGNMENT_FP = "b" * 128
IAM_FP = "c" * 128
COMPLETION_FP = "d" * 128


class _Session:
    def __init__(
        self,
        active: bool = True,
    ) -> None:
        self.in_transaction = active


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
            "ISSUER_CALL_BELONGS_INSIDE_R20R23"
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
        source_reference=(
            "workflow:r20r25-contract"
        ),
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
        assignment_id=(
            "assignment-r20r25-contract"
        ),
        tenant_id=TENANT,
        case_matter_id=MATTER,
        work_item_id=WORK_ID,
        assignee_principal_id=PRINCIPAL,
        assigned_by_principal_id=(
            "principal-partner-r20r25"
        ),
        assigned_at=datetime(
            2026,
            10,
            16,
            9,
            0,
            tzinfo=timezone.utc,
        ),
        assignment_reason_reference=(
            "workflow-assignment:r20r25"
        ),
        authorization_evidence_reference=(
            "assignment-auth:r20r25"
        ),
    )


def _authority(
    work: LegalWorkItem,
) -> LegalWorkCompletionAuthorityEvidence:
    return LegalWorkCompletionAuthorityEvidence(
        completion_authority_evidence_id=(
            "completion-authority-r20r25-contract"
        ),
        tenant_id=TENANT,
        case_matter_id=MATTER,
        work_item_id=WORK_ID,
        work_item_fingerprint=work.fingerprint,
        principal_id=PRINCIPAL,
        assignment_id=(
            "assignment-r20r25-contract"
        ),
        assignment_fingerprint=ASSIGNMENT_FP,
        iam_authorization_evidence_reference=(
            "tenant-authorization:r20r25-contract"
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
            "completion:evidence:r20r25-contract"
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


def test_exact_public_surface_is_composition_boundary() -> None:
    assert tuple(
        inspect.signature(
            orchestration.record_legal_work_completion
        ).parameters
    ) == (
        "tenant_id",
        "principal_id",
        "work_item",
        "assignments",
        "completion_evidence_reference",
        "completion_evidence_fingerprint",
        "evaluated_at",
        "authorization_evidence_issuer",
        "completion_registry",
        "session",
    )


def test_iam_repositories_are_not_public_inputs() -> None:
    parameters = set(
        inspect.signature(
            orchestration.record_legal_work_completion
        ).parameters
    )

    for forbidden in (
        "principal_repository",
        "membership_repository",
        "role_assignment_repository",
        "business_role_repository",
    ):
        assert forbidden not in parameters


def test_inactive_transaction_rejects_before_any_downstream_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def fake_compose(
        **kwargs: Any,
    ):
        calls.append("compose")
        raise AssertionError(
            "COMPOSE_MUST_NOT_RUN"
        )

    monkeypatch.setattr(
        orchestration,
        "compose_legal_work_completion_authority_evidence",
        fake_compose,
    )

    with pytest.raises(
        orchestration.LegalWorkCompletionPersistenceOrchestrationError
    ):
        orchestration.record_legal_work_completion(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            work_item=_work(),
            assignments=(_assignment(),),
            completion_evidence_reference=(
                "completion:evidence:r20r25-contract"
            ),
            completion_evidence_fingerprint=COMPLETION_FP,
            evaluated_at=AT,
            authorization_evidence_issuer=(
                _AuthorizationIssuer()
            ),
            completion_registry=_Registry(),
            session=_Session(False),
        )

    assert calls == []


def test_exact_order_and_same_session_across_authority_and_persistence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    work = _work()
    authority = _authority(work)
    event = _event(
        work,
        authority,
    )

    issuer = _AuthorizationIssuer()
    registry = _Registry()
    session = _Session(True)
    assignments = (_assignment(),)

    order: list[str] = []
    compose_calls: list[
        dict[str, Any]
    ] = []
    prepare_calls: list[
        dict[str, Any]
    ] = []

    def fake_compose(
        **kwargs: Any,
    ) -> LegalWorkCompletionAuthorityEvidence:
        order.append("compose")
        compose_calls.append(kwargs)
        return authority

    def fake_prepare(
        **kwargs: Any,
    ) -> LegalWorkCompletionEvent:
        order.append("prepare")
        prepare_calls.append(kwargs)
        return event

    original_create = (
        registry.create_or_replay
    )

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
            "completion:evidence:r20r25-contract"
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

    assert len(compose_calls) == 1
    assert len(prepare_calls) == 1
    assert len(registry.calls) == 1

    assert compose_calls[0] == {
        "tenant_id": TENANT,
        "principal_id": PRINCIPAL,
        "work_item": work,
        "assignments": assignments,
        "evaluated_at": AT,
        "authorization_evidence_issuer": issuer,
        "session": session,
    }

    assert prepare_calls[0] == {
        "work_item": work,
        "completion_authority_evidence": authority,
        "completion_evidence_reference": (
            "completion:evidence:r20r25-contract"
        ),
        "completion_evidence_fingerprint": COMPLETION_FP,
    }

    persisted, persisted_session = (
        registry.calls[0]
    )

    assert persisted is event
    assert persisted_session is session


def test_r20r18_receives_no_session_or_authority_inputs_besides_r20r22(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    work = _work()
    authority = _authority(work)

    prepare_calls: list[
        dict[str, Any]
    ] = []

    def fake_compose(
        **kwargs: Any,
    ) -> LegalWorkCompletionAuthorityEvidence:
        return authority

    def fake_prepare(
        **kwargs: Any,
    ) -> LegalWorkCompletionEvent:
        prepare_calls.append(kwargs)

        for forbidden in (
            "session",
            "evaluated_at",
            "assignments",
            "tenant_id",
            "principal_id",
            "authorization_evidence_issuer",
        ):
            assert forbidden not in kwargs

        return _event(
            work,
            authority,
        )

    monkeypatch.setattr(
        orchestration,
        "compose_legal_work_completion_authority_evidence",
        fake_compose,
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
            "completion:evidence:r20r25-contract"
        ),
        completion_evidence_fingerprint=COMPLETION_FP,
        evaluated_at=AT,
        authorization_evidence_issuer=(
            _AuthorizationIssuer()
        ),
        completion_registry=_Registry(),
        session=_Session(),
    )

    assert len(prepare_calls) == 1


def test_r20r20_has_no_direct_iam_or_local_authorization_hashing() -> None:
    module_source = inspect.getsource(
        orchestration
    )

    for forbidden in (
        "authorize_tenant_operation",
        "authorize_legal_work_completion",
        "_authorization_payload",
        "_authorization_fingerprint",
        "_authorization_reference",
    ):
        assert forbidden not in module_source


def test_r20r20_does_not_manage_transaction_lifecycle() -> None:
    module_source = inspect.getsource(
        orchestration
    )

    for forbidden in (
        "start_transaction(",
        "commit_transaction(",
        "abort_transaction(",
        "with_transaction(",
    ):
        assert forbidden not in module_source


def test_r20r20_persistence_surface_is_create_or_replay_only() -> None:
    module_source = inspect.getsource(
        orchestration
    )

    assert (
        module_source.count(
            "create_or_replay("
        )
        == 2
    )

    for forbidden in (
        "insert_one(",
        "update_one(",
        "replace_one(",
        "delete_one(",
        "MongoClient(",
    ):
        assert forbidden not in module_source


def test_r20r20_has_no_adjacent_execution_authority() -> None:
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
