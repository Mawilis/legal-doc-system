"""
WILSY OS P14-R20R24 — R20R18 pure R20R22 consumption RED.

Frozen architecture:

    R20R20 caller-transaction composition boundary
        -> R20R23 authority composition
        -> R20R18 pure event construction from R20R22
        -> completion registry persistence

R20R18 must not:
- evaluate IAM;
- resolve historical assignments;
- accept IAM repositories;
- accept a transaction/session;
- accept a second evaluated_at;
- synthesize authorization provenance.

The event's authorization reference/fingerprint identify the complete
R20R22 authority artifact.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
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


TENANT = "tenant-r20r24"
MATTER = "matter-r20r24"
WORK = "work-r20r24"
PRINCIPAL = "principal-r20r24"

AT = datetime(
    2026,
    10,
    17,
    6,
    30,
    tzinfo=timezone.utc,
)

WORK_SOURCE_FP = "a" * 128
ASSIGNMENT_FP = "b" * 128
IAM_FP = "c" * 128
COMPLETION_FP = "d" * 128


def _work() -> LegalWorkItem:
    return LegalWorkItem(
        work_item_id=WORK,
        tenant_id=TENANT,
        case_matter_id=MATTER,
        title="Complete governed Legal work",
        source_kind="LEGAL_MATTER_WORKFLOW",
        source_reference="workflow:r20r24",
        source_evidence_fingerprint=WORK_SOURCE_FP,
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
    tenant_id: str = TENANT,
    case_matter_id: str = MATTER,
    work_item_id: str = WORK,
    work_item_fingerprint: str | None = None,
    principal_id: str = PRINCIPAL,
    evaluated_at: datetime = AT,
) -> LegalWorkCompletionAuthorityEvidence:
    work = _work()

    return LegalWorkCompletionAuthorityEvidence(
        completion_authority_evidence_id=(
            "completion-authority-r20r24"
        ),
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        work_item_id=work_item_id,
        work_item_fingerprint=(
            work.fingerprint
            if work_item_fingerprint is None
            else work_item_fingerprint
        ),
        principal_id=principal_id,
        assignment_id="assignment-r20r24",
        assignment_fingerprint=ASSIGNMENT_FP,
        iam_authorization_evidence_reference=(
            "tenant-authorization:r20r24"
        ),
        iam_authorization_evidence_fingerprint=IAM_FP,
        evaluated_at=evaluated_at,
    )


def _prepare(
    *,
    work_item: LegalWorkItem | None = None,
    authority: LegalWorkCompletionAuthorityEvidence | None = None,
    completion_reference: str = "completion:evidence:r20r24",
    completion_fingerprint: str = COMPLETION_FP,
) -> LegalWorkCompletionEvent:
    return service.prepare_legal_work_completion_event(
        work_item=(
            _work()
            if work_item is None
            else work_item
        ),
        completion_authority_evidence=(
            _authority()
            if authority is None
            else authority
        ),
        completion_evidence_reference=completion_reference,
        completion_evidence_fingerprint=completion_fingerprint,
    )


def test_r20r18_exact_pure_r20r22_consumer_surface() -> None:
    parameters = tuple(
        inspect.signature(
            service.prepare_legal_work_completion_event
        ).parameters
    )

    assert parameters == (
        "work_item",
        "completion_authority_evidence",
        "completion_evidence_reference",
        "completion_evidence_fingerprint",
    )


def test_r20r18_has_no_legacy_authority_inputs() -> None:
    parameters = set(
        inspect.signature(
            service.prepare_legal_work_completion_event
        ).parameters
    )

    for forbidden in (
        "tenant_id",
        "principal_id",
        "assignments",
        "evaluated_at",
        "principal_repository",
        "membership_repository",
        "role_assignment_repository",
        "business_role_repository",
        "session",
        "authorization_evidence_reference",
        "authorization_evidence_fingerprint",
    ):
        assert forbidden not in parameters


def test_event_consumes_exact_r20r22_provenance() -> None:
    authority = _authority()

    value = _prepare(
        authority=authority,
    )

    assert type(value) is LegalWorkCompletionEvent

    assert (
        value.authorization_evidence_reference
        == authority.completion_authority_evidence_reference
    )

    assert (
        value.authorization_evidence_fingerprint
        == authority.fingerprint
    )


def test_actor_and_completion_time_are_authority_derived() -> None:
    authority = _authority()

    value = _prepare(
        authority=authority,
    )

    assert (
        value.actor_principal_id
        == authority.principal_id
    )

    assert (
        value.completed_at
        == authority.evaluated_at
    )


@pytest.mark.parametrize(
    "field,replacement",
    (
        ("tenant_id", "wrong-tenant"),
        ("case_matter_id", "wrong-matter"),
        ("work_item_id", "wrong-work"),
        ("work_item_fingerprint", "e" * 128),
    ),
)
def test_authority_work_scope_mismatch_fails_closed(
    field: str,
    replacement: str,
) -> None:
    authority = replace(
        _authority(),
        **{
            field: replacement,
        },
    )

    with pytest.raises(Exception):
        _prepare(
            authority=authority,
        )


def test_completion_evidence_does_not_change_authority_identity() -> None:
    authority = _authority()

    first = _prepare(
        authority=authority,
        completion_reference="completion:evidence:one",
        completion_fingerprint="d" * 128,
    )

    second = _prepare(
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


def test_r20r18_contains_no_r20r16_or_authority_hashing() -> None:
    source = inspect.getsource(service)

    for forbidden in (
        "authorize_legal_work_completion",
        "_authorization_payload",
        "_authorization_fingerprint",
        "_authorization_reference",
        "authorize_tenant_operation",
    ):
        assert forbidden not in source


def test_r20r18_remains_pure_event_construction_only() -> None:
    source = inspect.getsource(service)

    for forbidden in (
        "MongoClient(",
        "insert_one(",
        "update_one(",
        "replace_one(",
        "delete_one(",
        "create_or_replay(",
        "start_transaction(",
        "commit_transaction(",
        "abort_transaction(",
        "invoice",
        "payment",
        "settlement",
    ):
        assert forbidden not in source
