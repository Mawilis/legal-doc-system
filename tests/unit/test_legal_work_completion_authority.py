"""
TITLE:
    WILSY OS P14-R20R15 Legal Work Completion Authority Certificate

VERSION:
    v1.0.0-P14-R20R15-WORK-COMPLETION-AUTHORITY-RED

PURPOSE:
    Certify that Legal work completion admission is the conjunction of current
    tenant IAM and exact historical work assignment at one explicit evaluation
    instant.

AUTHORITY BOUNDARY:
    This service may decide only whether one acting principal is admitted to
    request completion of one exact immutable LegalWorkItem.

    It does not complete the work item, persist a completion event, mutate work,
    satisfy dependencies, advance workflow, prove a source legal event, grant
    supervision authority, execute AI, invoice, bill, pay or settle.

TEMPORAL BOUNDARY:
    TenantAuthorizationDecision contains no authoritative timestamp. Therefore
    evaluated_at is an explicit timezone-aware server-side evaluation instant.
    It is never represented as IAM authorized_at.

EXCLUDED MODELS:
    Operating role titles, operating capabilities, LEGAL_WORK_COMPLETE,
    MATTER/WORK_ITEM/TENANT role-scope labels and supervisor identity are not
    completion-authority inputs.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import importlib
from types import ModuleType

import pytest

from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
    LegalWorkItemStatus,
)


TENANT = "tenant-law"
MATTER = "matter-1"
WORK_ID = "work-1"

PRINCIPAL_A = "principal-a"
PRINCIPAL_B = "principal-b"

NOW = datetime(
    2026,
    10,
    17,
    12,
    0,
    tzinfo=timezone.utc,
)

COMPLETION_PERMISSION = (
    "legal_operations:work_item:complete"
)

COMPLETION_OPERATION = (
    "legal_work_item_complete"
)

SOURCE_FP = "a" * 128


class _Session:
    def __init__(
        self,
        active: bool = True,
    ) -> None:
        self.in_transaction = active


def _service() -> ModuleType:
    try:
        return importlib.import_module(
            "tools.eos.legal_operations.service."
            "legal_work_completion_authority"
        )
    except ModuleNotFoundError as exc:
        pytest.fail(
            "P14_R20R16_COMPLETION_AUTHORITY_SERVICE_MISSING",
            pytrace=False,
        )


def _work(
    *,
    tenant_id: str = TENANT,
    matter_id: str = MATTER,
    work_item_id: str = WORK_ID,
) -> LegalWorkItem:
    return LegalWorkItem(
        work_item_id=work_item_id,
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        title="Prepare governed filing package",
        source_kind="LEGAL_MATTER_WORKFLOW",
        source_reference="workflow:instance-1:stage-2",
        source_evidence_fingerprint=SOURCE_FP,
        status=LegalWorkItemStatus.IN_PROGRESS,
        created_at=NOW - timedelta(days=10),
    )


def _assignment(
    assignment_id: str,
    principal_id: str,
    assigned_at: datetime,
    *,
    supersedes: str | None = None,
    tenant_id: str = TENANT,
    matter_id: str = MATTER,
    work_item_id: str = WORK_ID,
) -> LegalWorkAssignment:
    return LegalWorkAssignment(
        assignment_id=assignment_id,
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        work_item_id=work_item_id,
        assignee_principal_id=principal_id,
        assigned_by_principal_id="principal-assigner",
        assigned_at=assigned_at,
        assignment_reason_reference="reason:staffing",
        authorization_evidence_reference="authz:assignment",
        supersedes_assignment_id=supersedes,
    )


def _history() -> tuple[
    LegalWorkAssignment,
    ...,
]:
    first = _assignment(
        "assignment-1",
        PRINCIPAL_A,
        NOW - timedelta(days=3),
    )

    second = _assignment(
        "assignment-2",
        PRINCIPAL_B,
        NOW - timedelta(days=1),
        supersedes=first.assignment_id,
    )

    return (
        first,
        second,
    )


def _authorized(
    *,
    business_role: str = "tenant_legal_attorney",
    authorization_role: str = "LEGAL_ATTORNEY",
) -> TenantAuthorizationDecision:
    return TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        business_role,
        authorization_role,
    )


def _denied() -> TenantAuthorizationDecision:
    return TenantAuthorizationDecision(
        False,
        TenantAuthorizationReason.PERMISSION_NOT_GRANTED,
        "tenant_legal_attorney",
        None,
    )


def _install_iam(
    monkeypatch: pytest.MonkeyPatch,
    module: ModuleType,
    decision: TenantAuthorizationDecision,
) -> list[dict[str, object]]:
    calls: list[
        dict[str, object]
    ] = []

    def fake_authorize_tenant_operation(
        **kwargs: object,
    ) -> TenantAuthorizationDecision:
        calls.append(
            dict(kwargs)
        )
        return decision

    monkeypatch.setattr(
        module,
        "authorize_tenant_operation",
        fake_authorize_tenant_operation,
    )

    return calls


def _call(
    module: ModuleType,
    *,
    monkeypatch: pytest.MonkeyPatch,
    principal_id: str = PRINCIPAL_A,
    work_item: LegalWorkItem | None = None,
    assignments: tuple[
        LegalWorkAssignment,
        ...,
    ] | None = None,
    evaluated_at: datetime | None = None,
    decision: TenantAuthorizationDecision | None = None,
    session: object | None = None,
):
    iam_calls = _install_iam(
        monkeypatch,
        module,
        decision or _authorized(),
    )

    result = module.authorize_legal_work_completion(
        tenant_id=TENANT,
        principal_id=principal_id,
        work_item=work_item or _work(),
        assignments=(
            assignments
            if assignments is not None
            else _history()
        ),
        evaluated_at=(
            evaluated_at
            if evaluated_at is not None
            else NOW - timedelta(days=2)
        ),
        principal_repository=object(),
        membership_repository=object(),
        role_assignment_repository=object(),
        business_role_repository=object(),
        session=(
            session
            if session is not None
            else _Session(True)
        ),
    )

    return (
        result,
        iam_calls,
    )


def test_completion_constants_are_exact_and_no_operating_capability_exists() -> None:
    module = _service()

    assert (
        module.COMPLETION_PERMISSION
        == COMPLETION_PERMISSION
    )
    assert (
        module.COMPLETION_OPERATION
        == COMPLETION_OPERATION
    )

    assert not hasattr(
        module,
        "COMPLETION_CAPABILITY_ID",
    )
    assert not hasattr(
        module,
        "LEGAL_WORK_COMPLETE",
    )


def test_exact_conjunction_authorizes_historical_assignee(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _service()

    result, iam_calls = _call(
        module,
        monkeypatch=monkeypatch,
        principal_id=PRINCIPAL_A,
        evaluated_at=(
            NOW - timedelta(days=2)
        ),
    )

    assert len(iam_calls) == 1

    call = iam_calls[0]

    assert (
        call["tenant_id"]
        == TENANT
    )
    assert (
        call["principal_id"]
        == PRINCIPAL_A
    )
    assert (
        call["permission_id"]
        == COMPLETION_PERMISSION
    )
    assert (
        call["operation"]
        == COMPLETION_OPERATION
    )

    raw = result.to_dict()

    assert raw["tenant_id"] == TENANT
    assert raw["case_matter_id"] == MATTER
    assert raw["work_item_id"] == WORK_ID
    assert raw["principal_id"] == PRINCIPAL_A

    assert (
        raw["work_item_fingerprint"]
        == _work().fingerprint
    )

    assert (
        raw["assignment_id"]
        == "assignment-1"
    )

    assert (
        raw["evaluated_at"]
        == (
            NOW - timedelta(days=2)
        ).isoformat()
    )

    assert (
        "supervisor_principal_id"
        not in raw
    )
    assert (
        "capability_id"
        not in raw
    )
    assert (
        "payment_id"
        not in raw
    )
    assert (
        "settlement_id"
        not in raw
    )


def test_evidence_is_immutable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _service()

    result, _ = _call(
        module,
        monkeypatch=monkeypatch,
    )

    with pytest.raises(
        (
            FrozenInstanceError,
            AttributeError,
        )
    ):
        result.principal_id = PRINCIPAL_B


def test_reassignment_changes_completion_principal_at_exact_historical_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _service()
    history = _history()

    before, _ = _call(
        module,
        monkeypatch=monkeypatch,
        principal_id=PRINCIPAL_A,
        assignments=history,
        evaluated_at=(
            history[1].assigned_at
            - timedelta(microseconds=1)
        ),
    )

    assert (
        before.assignment_id
        == "assignment-1"
    )

    at_boundary, _ = _call(
        module,
        monkeypatch=monkeypatch,
        principal_id=PRINCIPAL_B,
        assignments=history,
        evaluated_at=history[1].assigned_at,
    )

    assert (
        at_boundary.assignment_id
        == "assignment-2"
    )


def test_wrong_assignee_fails_closed_even_with_authorized_iam(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _service()

    with pytest.raises(
        module.LegalWorkCompletionAuthorityDeniedError,
        match="P14_R20R15_ASSIGNEE_MISMATCH",
    ):
        _call(
            module,
            monkeypatch=monkeypatch,
            principal_id=PRINCIPAL_B,
            evaluated_at=(
                NOW - timedelta(days=2)
            ),
        )


def test_no_assignment_at_evaluation_instant_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _service()

    history = _history()

    with pytest.raises(
        module.LegalWorkCompletionAuthorityDeniedError,
        match="P14_R20R15_ASSIGNMENT_REQUIRED",
    ):
        _call(
            module,
            monkeypatch=monkeypatch,
            assignments=history,
            evaluated_at=(
                history[0].assigned_at
                - timedelta(seconds=1)
            ),
        )


def test_denied_iam_never_becomes_completion_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _service()

    with pytest.raises(
        module.LegalWorkCompletionAuthorityDeniedError,
        match="P14_R20R15_IAM_DENIED",
    ):
        _call(
            module,
            monkeypatch=monkeypatch,
            decision=_denied(),
        )


def test_assignment_scope_mismatch_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _service()

    bad = (
        _assignment(
            "assignment-other",
            PRINCIPAL_A,
            NOW - timedelta(days=3),
            tenant_id="tenant-other",
        ),
    )

    with pytest.raises(
        module.LegalWorkCompletionAuthorityDeniedError,
    ):
        _call(
            module,
            monkeypatch=monkeypatch,
            assignments=bad,
        )


def test_cross_matter_assignment_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _service()

    bad = (
        _assignment(
            "assignment-other",
            PRINCIPAL_A,
            NOW - timedelta(days=3),
            matter_id="matter-other",
        ),
    )

    with pytest.raises(
        module.LegalWorkCompletionAuthorityDeniedError,
    ):
        _call(
            module,
            monkeypatch=monkeypatch,
            assignments=bad,
        )


def test_cross_work_item_assignment_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _service()

    bad = (
        _assignment(
            "assignment-other",
            PRINCIPAL_A,
            NOW - timedelta(days=3),
            work_item_id="work-other",
        ),
    )

    with pytest.raises(
        module.LegalWorkCompletionAuthorityDeniedError,
    ):
        _call(
            module,
            monkeypatch=monkeypatch,
            assignments=bad,
        )


def test_naive_evaluation_time_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _service()

    with pytest.raises(
        module.LegalWorkCompletionAuthorityDeniedError,
    ):
        _call(
            module,
            monkeypatch=monkeypatch,
            evaluated_at=datetime(
                2026,
                10,
                17,
                12,
                0,
            ),
        )


def test_inactive_transaction_rejects_before_iam(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _service()

    iam_calls = _install_iam(
        monkeypatch,
        module,
        _authorized(),
    )

    with pytest.raises(
        module.LegalWorkCompletionAuthorityDeniedError,
        match="P14_R20R15_ACTIVE_TRANSACTION_REQUIRED",
    ):
        module.authorize_legal_work_completion(
            tenant_id=TENANT,
            principal_id=PRINCIPAL_A,
            work_item=_work(),
            assignments=_history(),
            evaluated_at=NOW,
            principal_repository=object(),
            membership_repository=object(),
            role_assignment_repository=object(),
            business_role_repository=object(),
            session=_Session(False),
        )

    assert iam_calls == []


def test_same_caller_transaction_is_forwarded_into_iam(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _service()

    session = _Session(True)

    _, calls = _call(
        module,
        monkeypatch=monkeypatch,
        session=session,
    )

    assert len(calls) == 1
    assert calls[0]["session"] is session


def test_completed_or_cancelled_work_does_not_gain_completion_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _service()

    completed = LegalWorkItem(
        work_item_id=WORK_ID,
        tenant_id=TENANT,
        case_matter_id=MATTER,
        title="Completed work",
        source_kind="LEGAL_MATTER_WORKFLOW",
        source_reference="workflow:completed",
        source_evidence_fingerprint=SOURCE_FP,
        status=LegalWorkItemStatus.COMPLETED,
        created_at=NOW - timedelta(days=10),
        completion_evidence_reference="completion:event-1",
        completion_evidence_fingerprint="b" * 128,
        completed_at=NOW - timedelta(days=1),
    )

    with pytest.raises(
        module.LegalWorkCompletionAuthorityDeniedError,
    ):
        _call(
            module,
            monkeypatch=monkeypatch,
            work_item=completed,
        )

    cancelled = LegalWorkItem(
        work_item_id=WORK_ID,
        tenant_id=TENANT,
        case_matter_id=MATTER,
        title="Cancelled work",
        source_kind="LEGAL_MATTER_WORKFLOW",
        source_reference="workflow:cancelled",
        source_evidence_fingerprint=SOURCE_FP,
        status=LegalWorkItemStatus.CANCELLED,
        created_at=NOW - timedelta(days=10),
        cancellation_reason_reference="reason:cancel",
        cancelled_at=NOW - timedelta(days=1),
    )

    with pytest.raises(
        module.LegalWorkCompletionAuthorityDeniedError,
    ):
        _call(
            module,
            monkeypatch=monkeypatch,
            work_item=cancelled,
        )


def test_role_title_supervision_and_operating_capability_are_not_inputs() -> None:
    module = _service()

    import inspect

    parameters = tuple(
        inspect.signature(
            module.authorize_legal_work_completion
        ).parameters
    )

    for forbidden in (
        "operating_role_id",
        "operating_role_revision",
        "capability_id",
        "role_scope",
        "supervisor_principal_id",
        "authorized_at",
        "payment_id",
        "settlement_id",
    ):
        assert forbidden not in parameters


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_work_completion_authority.py
# VERSION: v1.0.0-P14-R20R15-WORK-COMPLETION-AUTHORITY-RED
# IAM AUTHORITY: exact current tenant authorization required inside caller tx
# TEMPORAL INPUT: explicit timezone-aware evaluated_at; not IAM authorized_at
# ASSIGNMENT: exact historical assignment current at evaluated_at
# ASSIGNEE: exact acting principal only
# TENANT / MATTER / WORK ITEM: exact immutable lineage required
# OPERATING ROLE AUTHORITY: NONE
# OPERATING CAPABILITY AUTHORITY: NONE
# SUPERVISION AUTHORITY: NONE
# COMPLETION EVENT AUTHORITY: NONE
# DEPENDENCY SATISFACTION AUTHORITY: NONE
# WORKFLOW RELEASE AUTHORITY: NONE
# LEGAL EVENT AUTHORITY: NONE
# AI EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
