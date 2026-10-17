"""
WILSY OS P14-R20R23 — single-evaluation Legal work completion
authority provenance composer RED contract.

Frozen topology:

    active caller transaction
    -> exact historical assignment
    -> server-derived IAM subject and replay identity
    -> one canonical IAM evidence issuance
    -> strict evidence correlation
    -> R20R22 full completion-authority evidence

No caller-supplied IAM idempotency authority exists.
No second authorize_tenant_operation evaluation is permitted.
"""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha3_512
import inspect
import json
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.tenant_authorization_decision_evidence import (
    TenantAuthorizationDecisionEvidence,
)
from tools.eos.auth import (
    permission_namespace,
    roles,
    tenant_authority_policy,
)
from tools.eos.auth import tenant_authorization as tenant_authorization_module

from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)
from tools.eos.legal_operations.domain.legal_work_item import (
    LegalWorkItem,
    LegalWorkItemStatus,
)


TENANT = "tenant-r20r23"
MATTER = "matter-r20r23"
WORK_ID = "work-r20r23"
PRINCIPAL = "principal-r20r23"
ASSIGNMENT_ID = "assignment-r20r23"

AT = datetime(
    2026,
    10,
    17,
    15,
    0,
    tzinfo=timezone.utc,
)

SOURCE_FP = "a" * 128
IAM_FP = "b" * 128


def _module():
    try:
        from tools.eos.legal_operations.service import (
            legal_work_completion_authority_composer
            as module,
        )
    except ImportError as error:
        pytest.fail(
            "P14_R20R23_COMPLETION_AUTHORITY_"
            "COMPOSER_MISSING:"
            + str(error),
            pytrace=False,
        )

    return module


def _work(
    *,
    fingerprint_source: str = SOURCE_FP,
) -> LegalWorkItem:
    return LegalWorkItem(
        work_item_id=WORK_ID,
        tenant_id=TENANT,
        case_matter_id=MATTER,
        title="Complete governed Legal work",
        source_kind="LEGAL_MATTER_WORKFLOW",
        source_reference="workflow:r20r23",
        source_evidence_fingerprint=fingerprint_source,
        status=LegalWorkItemStatus.IN_PROGRESS,
        created_at=datetime(
            2026,
            10,
            10,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )


def _assignment(
    *,
    principal_id: str = PRINCIPAL,
    assigned_at: datetime | None = None,
) -> LegalWorkAssignment:
    return LegalWorkAssignment(
        assignment_id=ASSIGNMENT_ID,
        tenant_id=TENANT,
        case_matter_id=MATTER,
        work_item_id=WORK_ID,
        assignee_principal_id=principal_id,
        assigned_by_principal_id="partner-r20r23",
        assigned_at=(
            assigned_at
            if assigned_at is not None
            else datetime(
                2026,
                10,
                16,
                9,
                0,
                tzinfo=timezone.utc,
            )
        ),
        assignment_reason_reference=(
            "workflow-assignment:r20r23"
        ),
        authorization_evidence_reference=(
            "assignment-authorization:r20r23"
        ),
    )


class _Session:
    in_transaction = True


class _InactiveSession:
    in_transaction = False


class _Issuer:
    def __init__(self) -> None:
        self.calls: list[
            dict[str, Any]
        ] = []

        self.result: Any = None

    def issue(
        self,
        **kwargs: Any,
    ) -> Any:
        self.calls.append(
            dict(kwargs)
        )

        if self.result is None:
            subject_reference = kwargs[
                "subject_reference"
            ]

            subject_fingerprint = kwargs[
                "subject_evidence_fingerprint"
            ]

            self.result = TenantAuthorizationDecisionEvidence(
                tenant_id=TENANT,
                authorization_decision_id=(
                    "authorization-r20r23"
                ),
                principal_id=PRINCIPAL,
                operation=(
                    "legal_work_item_complete"
                ),
                permission=(
                    "legal_operations:"
                    "work_item:complete"
                ),
                business_role=(
                    "tenant_legal_attorney"
                ),
                authorization_role=(
                    "LEGAL_ATTORNEY"
                ),
                membership_revision=1,
                role_assignment_revision=1,
                subject_reference=subject_reference,
                subject_evidence_fingerprint=(
                    subject_fingerprint
                ),
                permission_namespace_version=(
                    permission_namespace.VERSION
                ),
                authorization_role_policy_version=(
                    roles.VERSION
                ),
                tenant_business_role_policy_version=(
                    tenant_authority_policy.VERSION
                ),
                tenant_authorization_composition_version=(
                    tenant_authorization_module.VERSION
                ),
                idempotency_key=kwargs[
                    "idempotency_key"
                ],
                authorized_at=datetime(
                    2026,
                    10,
                    17,
                    14,
                    59,
                    59,
                    tzinfo=timezone.utc,
                ),
            )

        return self.result


def _compose(
    *,
    issuer: _Issuer | None = None,
    work: LegalWorkItem | None = None,
    assignments: tuple[
        LegalWorkAssignment,
        ...,
    ] | None = None,
    principal_id: str = PRINCIPAL,
    evaluated_at: datetime = AT,
    session: object | None = None,
):
    module = _module()

    selected_issuer = (
        issuer
        if issuer is not None
        else _Issuer()
    )

    selected_work = (
        work
        if work is not None
        else _work()
    )

    selected_assignments = (
        assignments
        if assignments is not None
        else (
            _assignment(
                principal_id=principal_id,
            ),
        )
    )

    selected_session = (
        session
        if session is not None
        else _Session()
    )

    value = (
        module.compose_legal_work_completion_authority_evidence(
            tenant_id=TENANT,
            principal_id=principal_id,
            work_item=selected_work,
            assignments=selected_assignments,
            evaluated_at=evaluated_at,
            authorization_evidence_issuer=selected_issuer,
            session=selected_session,
        )
    )

    return (
        value,
        selected_issuer,
    )


def _canonical_digest(
    value: dict[str, object],
) -> str:
    raw = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    return sha3_512(
        raw
    ).hexdigest()


def test_exact_public_surface_and_no_caller_idempotency():
    module = _module()

    signature = inspect.signature(
        module.compose_legal_work_completion_authority_evidence
    )

    assert tuple(
        signature.parameters
    ) == (
        "tenant_id",
        "principal_id",
        "work_item",
        "assignments",
        "evaluated_at",
        "authorization_evidence_issuer",
        "session",
    )

    assert (
        module.COMPLETION_OPERATION
        == "legal_work_item_complete"
    )

    assert (
        module.COMPLETION_PERMISSION
        == "legal_operations:work_item:complete"
    )

    assert (
        module.AUTHORIZATION_SUBJECT_PREFIX
        == "legal-work-completion"
    )


def test_inactive_transaction_rejects_before_issuer():
    module = _module()

    issuer = _Issuer()

    with pytest.raises(
        module.LegalWorkCompletionAuthorityCompositionError
    ):
        _compose(
            issuer=issuer,
            session=_InactiveSession(),
        )

    assert issuer.calls == []


def test_one_iam_issue_only_and_same_exact_session():
    issuer = _Issuer()
    session = _Session()

    _compose(
        issuer=issuer,
        session=session,
    )

    assert len(
        issuer.calls
    ) == 1

    assert (
        issuer.calls[0]["session"]
        is session
    )


def test_server_derives_exact_subject_reference():
    _, issuer = _compose()

    call = issuer.calls[0]

    assert (
        call["subject_reference"]
        == (
            "legal-work-completion:"
            + TENANT
            + ":"
            + MATTER
            + ":"
            + WORK_ID
        )
    )


def test_server_derives_target_stable_iam_idempotency():
    _, issuer = _compose()

    expected_digest = _canonical_digest(
        {
            "tenant_id": TENANT,
            "work_item_id": WORK_ID,
        }
    )

    assert (
        issuer.calls[0][
            "idempotency_key"
        ]
        == (
            "legal-work-completion:"
            "iam:"
            + expected_digest
        )
    )


def test_subject_fingerprint_binds_full_pre_iam_authority_basis():
    work = _work()
    assignment = _assignment()

    _, issuer = _compose(
        work=work,
        assignments=(
            assignment,
        ),
    )

    expected = _canonical_digest(
        {
            "tenant_id":
                TENANT,
            "case_matter_id":
                MATTER,
            "work_item_id":
                WORK_ID,
            "work_item_fingerprint":
                work.fingerprint,
            "principal_id":
                PRINCIPAL,
            "assignment_id":
                assignment.assignment_id,
            "assignment_fingerprint":
                assignment.fingerprint,
            "evaluated_at":
                AT.isoformat(),
        }
    )

    assert (
        issuer.calls[0][
            "subject_evidence_fingerprint"
        ]
        == expected
    )


def test_issuer_receives_exact_operation_permission_identity():
    _, issuer = _compose()

    call = issuer.calls[0]

    assert (
        call["tenant_id"]
        == TENANT
    )

    assert (
        call["principal_id"]
        == PRINCIPAL
    )

    assert (
        call["operation"]
        == "legal_work_item_complete"
    )

    assert (
        call["permission"]
        == "legal_operations:work_item:complete"
    )


def test_output_is_first_class_r20r22_evidence():
    from tools.eos.legal_operations.domain.legal_work_completion_authority_evidence import (
        LegalWorkCompletionAuthorityEvidence,
    )

    work = _work()
    assignment = _assignment()

    value, issuer = _compose(
        work=work,
        assignments=(
            assignment,
        ),
    )

    assert type(
        value
    ) is LegalWorkCompletionAuthorityEvidence

    assert value.tenant_id == TENANT
    assert value.case_matter_id == MATTER
    assert value.work_item_id == WORK_ID

    assert (
        value.work_item_fingerprint
        == work.fingerprint
    )

    assert (
        value.principal_id
        == PRINCIPAL
    )

    assert (
        value.assignment_id
        == assignment.assignment_id
    )

    assert (
        value.assignment_fingerprint
        == assignment.fingerprint
    )

    assert (
        value.iam_authorization_evidence_reference
        == issuer.result.authorization_evidence_reference
    )

    assert (
        value.iam_authorization_evidence_fingerprint
        == issuer.result.authorization_evidence_fingerprint
    )

    assert value.evaluated_at == AT


def test_completion_authority_evidence_id_is_server_derived():
    first, _ = _compose()
    second, _ = _compose()

    assert (
        first.completion_authority_evidence_id
        == second.completion_authority_evidence_id
    )

    assert (
        first.completion_authority_evidence_id
        .startswith(
            "legal-work-completion-authority:"
        )
    )


@pytest.mark.parametrize(
    "field",
    (
        "tenant_id",
        "principal_id",
        "operation",
        "permission",
        "subject_reference",
        "subject_evidence_fingerprint",
    ),
)
def test_iam_evidence_correlation_mismatch_fails_closed(
    field: str,
):
    module = _module()

    issuer = _Issuer()

    _, baseline_issuer = _compose()

    baseline = (
        baseline_issuer.result
    )

    replacement: object

    if field == "subject_evidence_fingerprint":
        replacement = "f" * 128
    else:
        replacement = "wrong"

    values = {
        name: getattr(
            baseline,
            name,
        )
        for name in baseline.__dataclass_fields__
    }

    values[
        field
    ] = replacement

    issuer.result = TenantAuthorizationDecisionEvidence(
        **values
    )

    with pytest.raises(
        module.LegalWorkCompletionAuthorityCompositionError
    ):
        _compose(
            issuer=issuer,
        )


def test_noncanonical_iam_evidence_reference_spoof_fails_closed():
    module = _module()

    issuer = _Issuer()

    _, baseline_issuer = _compose()

    baseline = baseline_issuer.result

    issuer.result = SimpleNamespace(
        tenant_id=baseline.tenant_id,
        principal_id=baseline.principal_id,
        operation=baseline.operation,
        permission=baseline.permission,
        subject_reference=baseline.subject_reference,
        subject_evidence_fingerprint=(
            baseline.subject_evidence_fingerprint
        ),
        authorization_evidence_reference="spoofed-reference",
        authorization_evidence_fingerprint=(
            baseline.authorization_evidence_fingerprint
        ),
    )

    with pytest.raises(
        module.LegalWorkCompletionAuthorityCompositionError
    ):
        _compose(
            issuer=issuer,
        )


def test_noncanonical_iam_evidence_fingerprint_spoof_fails_closed():
    module = _module()

    issuer = _Issuer()

    _, baseline_issuer = _compose()

    baseline = baseline_issuer.result

    issuer.result = SimpleNamespace(
        tenant_id=baseline.tenant_id,
        principal_id=baseline.principal_id,
        operation=baseline.operation,
        permission=baseline.permission,
        subject_reference=baseline.subject_reference,
        subject_evidence_fingerprint=(
            baseline.subject_evidence_fingerprint
        ),
        authorization_evidence_reference=(
            baseline.authorization_evidence_reference
        ),
        authorization_evidence_fingerprint="f" * 128,
    )

    with pytest.raises(
        module.LegalWorkCompletionAuthorityCompositionError
    ):
        _compose(
            issuer=issuer,
        )


def test_wrong_historical_assignee_fails_before_iam_issue():
    module = _module()

    issuer = _Issuer()

    with pytest.raises(
        module.LegalWorkCompletionAuthorityCompositionError
    ):
        _compose(
            issuer=issuer,
            assignments=(
                _assignment(
                    principal_id="someone-else",
                ),
            ),
        )

    assert issuer.calls == []


def test_future_assignment_is_not_completion_authority():
    module = _module()

    issuer = _Issuer()

    with pytest.raises(
        module.LegalWorkCompletionAuthorityCompositionError
    ):
        _compose(
            issuer=issuer,
            assignments=(
                _assignment(
                    assigned_at=datetime(
                        2026,
                        10,
                        18,
                        9,
                        0,
                        tzinfo=timezone.utc,
                    )
                ),
            ),
        )

    assert issuer.calls == []


def test_composer_has_no_direct_iam_or_persistence_authority():
    module = _module()

    source = inspect.getsource(
        module
    )

    assert (
        "authorize_tenant_operation("
        not in source
    )

    for forbidden in (
        "insert_one(",
        "update_one(",
        "replace_one(",
        "delete_one(",
        "MongoClient(",
        "LegalWorkCompletionEvent(",
        "create_or_replay(",
        "invoice",
        "payment",
        "settlement",
    ):
        assert forbidden not in source
