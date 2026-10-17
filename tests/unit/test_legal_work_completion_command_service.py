"""
WILSY OS P14-R20R24 — Legal work completion event preparation contract.

This suite supersedes the retired R20R16-oriented R20R18 contract.

R20R18 is now a pure consumer of one already-composed R20R22
LegalWorkCompletionAuthorityEvidence value.

Authority evaluation, IAM repository reads, historical assignment resolution,
transaction ownership and authority-evidence issuance belong upstream.

R20R18:
- correlates exact work identity/fingerprint;
- maps R20R22 principal -> completion actor;
- maps R20R22 evaluated_at -> completed_at;
- maps R20R22 reference/fingerprint -> event authorization provenance;
- accepts separate completion-outcome evidence;
- constructs no persistence or adjacent authority.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import inspect

import pytest

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
from tools.eos.legal_operations.service import (
    legal_work_completion_command_service as service,
)


TENANT = "tenant-r20r24-contract"
MATTER = "matter-r20r24-contract"
WORK_ID = "work-r20r24-contract"
PRINCIPAL = "principal-r20r24-contract"

NOW = datetime(
    2026,
    10,
    17,
    7,
    0,
    tzinfo=timezone.utc,
)

SOURCE_FP = "a" * 128
ASSIGNMENT_FP = "b" * 128
IAM_FP = "c" * 128
COMPLETION_FP = "d" * 128


def _work() -> LegalWorkItem:
    return LegalWorkItem(
        work_item_id=WORK_ID,
        tenant_id=TENANT,
        case_matter_id=MATTER,
        title="Complete governed daily legal work",
        source_kind="LEGAL_MATTER_WORKFLOW",
        source_reference="workflow:r20r24-contract",
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


def _authority(
    *,
    work: LegalWorkItem | None = None,
    principal_id: str = PRINCIPAL,
    evaluated_at: datetime = NOW,
) -> LegalWorkCompletionAuthorityEvidence:
    selected = (
        _work()
        if work is None
        else work
    )

    return LegalWorkCompletionAuthorityEvidence(
        completion_authority_evidence_id=(
            "completion-authority-r20r24-contract"
        ),
        tenant_id=selected.tenant_id,
        case_matter_id=selected.case_matter_id,
        work_item_id=selected.work_item_id,
        work_item_fingerprint=selected.fingerprint,
        principal_id=principal_id,
        assignment_id="assignment-r20r24-contract",
        assignment_fingerprint=ASSIGNMENT_FP,
        iam_authorization_evidence_reference=(
            "tenant-authorization:r20r24-contract"
        ),
        iam_authorization_evidence_fingerprint=IAM_FP,
        evaluated_at=evaluated_at,
    )


def _prepare(
    *,
    work: LegalWorkItem | None = None,
    authority: LegalWorkCompletionAuthorityEvidence | None = None,
    completion_reference: str = "completion:evidence:r20r24-contract",
    completion_fingerprint: str = COMPLETION_FP,
) -> LegalWorkCompletionEvent:
    selected_work = (
        _work()
        if work is None
        else work
    )

    selected_authority = (
        _authority(
            work=selected_work,
        )
        if authority is None
        else authority
    )

    return service.prepare_legal_work_completion_event(
        work_item=selected_work,
        completion_authority_evidence=selected_authority,
        completion_evidence_reference=completion_reference,
        completion_evidence_fingerprint=completion_fingerprint,
    )


def test_exact_public_surface_is_r20r22_consumer_only() -> None:
    assert tuple(
        inspect.signature(
            service.prepare_legal_work_completion_event
        ).parameters
    ) == (
        "work_item",
        "completion_authority_evidence",
        "completion_evidence_reference",
        "completion_evidence_fingerprint",
    )


def test_returns_exact_completion_event_type() -> None:
    value = _prepare()

    assert type(value) is LegalWorkCompletionEvent


def test_exact_work_identity_is_preserved() -> None:
    work = _work()

    value = _prepare(
        work=work,
    )

    assert value.tenant_id == work.tenant_id
    assert value.case_matter_id == work.case_matter_id
    assert value.work_item_id == work.work_item_id

    assert (
        value.work_item_fingerprint
        == work.fingerprint
    )


def test_actor_is_derived_from_r20r22_principal() -> None:
    authority = _authority(
        principal_id=PRINCIPAL,
    )

    value = _prepare(
        authority=authority,
    )

    assert (
        value.actor_principal_id
        == authority.principal_id
    )


def test_completed_at_is_exact_r20r22_evaluated_at() -> None:
    instant = (
        NOW
        + timedelta(minutes=17)
    )

    authority = _authority(
        evaluated_at=instant,
    )

    value = _prepare(
        authority=authority,
    )

    assert value.completed_at == instant


def test_event_authorization_provenance_is_exact_r20r22_identity() -> None:
    authority = _authority()

    value = _prepare(
        authority=authority,
    )

    assert (
        value.authorization_evidence_reference
        == authority.completion_authority_evidence_reference
    )

    assert (
        value.authorization_evidence_fingerprint
        == authority.fingerprint
    )


def test_completion_outcome_evidence_is_preserved_exactly() -> None:
    value = _prepare(
        completion_reference=(
            "completion:evidence:specific"
        ),
        completion_fingerprint="e" * 128,
    )

    assert (
        value.completion_evidence_reference
        == "completion:evidence:specific"
    )

    assert (
        value.completion_evidence_fingerprint
        == "e" * 128
    )


def test_exact_same_inputs_are_deterministic() -> None:
    work = _work()
    authority = _authority(
        work=work,
    )

    first = _prepare(
        work=work,
        authority=authority,
    )

    second = _prepare(
        work=work,
        authority=authority,
    )

    assert (
        first.completion_event_id
        == second.completion_event_id
    )

    assert first.fingerprint == second.fingerprint

    assert (
        first.authorization_evidence_reference
        == second.authorization_evidence_reference
    )

    assert (
        first.authorization_evidence_fingerprint
        == second.authorization_evidence_fingerprint
    )


def test_completion_evidence_changes_event_not_authority_identity() -> None:
    work = _work()
    authority = _authority(
        work=work,
    )

    first = _prepare(
        work=work,
        authority=authority,
        completion_reference="completion:evidence:one",
        completion_fingerprint="d" * 128,
    )

    second = _prepare(
        work=work,
        authority=authority,
        completion_reference="completion:evidence:two",
        completion_fingerprint="e" * 128,
    )

    assert (
        first.authorization_evidence_reference
        == second.authorization_evidence_reference
        == authority.completion_authority_evidence_reference
    )

    assert (
        first.authorization_evidence_fingerprint
        == second.authorization_evidence_fingerprint
        == authority.fingerprint
    )

    assert (
        first.completion_event_id
        != second.completion_event_id
    )

    assert first.fingerprint != second.fingerprint


@pytest.mark.parametrize(
    "field,replacement",
    (
        ("tenant_id", "tenant-wrong"),
        ("case_matter_id", "matter-wrong"),
        ("work_item_id", "work-wrong"),
        ("work_item_fingerprint", "f" * 128),
    ),
)
def test_r20r22_scope_or_work_fingerprint_mismatch_rejects(
    field: str,
    replacement: str,
) -> None:
    authority = replace(
        _authority(),
        **{
            field: replacement,
        },
    )

    with pytest.raises(
        service.LegalWorkCompletionCommandError
    ):
        _prepare(
            authority=authority,
        )


def test_invalid_completion_fingerprint_fails_closed() -> None:
    with pytest.raises(Exception):
        _prepare(
            completion_fingerprint=(
                "not-a-fingerprint"
            ),
        )


def test_missing_completion_reference_fails_closed() -> None:
    with pytest.raises(Exception):
        _prepare(
            completion_reference="",
        )


def test_r20r18_accepts_no_caller_raw_authorization_fields() -> None:
    parameters = set(
        inspect.signature(
            service.prepare_legal_work_completion_event
        ).parameters
    )

    for forbidden in (
        "authorization_evidence_reference",
        "authorization_evidence_fingerprint",
        "authorized_at",
        "tenant_id",
        "principal_id",
        "evaluated_at",
        "assignments",
        "session",
    ):
        assert forbidden not in parameters


def test_r20r18_has_no_authority_or_persistence_dependencies() -> None:
    module_source = inspect.getsource(
        service
    )

    for forbidden in (
        "authorize_legal_work_completion",
        "authorize_tenant_operation",
        "_authorization_payload",
        "_authorization_fingerprint",
        "_authorization_reference",
        "principal_repository",
        "membership_repository",
        "role_assignment_repository",
        "business_role_repository",
        "MongoClient(",
        "insert_one(",
        "update_one(",
        "replace_one(",
        "delete_one(",
        "create_or_replay(",
        "start_transaction(",
        "commit_transaction(",
        "abort_transaction(",
    ):
        assert forbidden not in module_source


def test_r20r18_has_no_adjacent_execution_authority() -> None:
    parameters = set(
        inspect.signature(
            service.prepare_legal_work_completion_event
        ).parameters
    )

    for forbidden in (
        "workflow_id",
        "workflow_transition_id",
        "dependency_id",
        "supervisor_principal_id",
        "invoice_id",
        "payment_id",
        "settlement_id",
        "notification_id",
        "legal_event_id",
    ):
        assert forbidden not in parameters
