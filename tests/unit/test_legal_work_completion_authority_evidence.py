"""
WILSY OS P14-R20R22 — first-class Legal work completion
authority evidence contract.

This artifact records the already-proven conjunction:

    canonical tenant IAM authorization evidence
    ∩ exact Legal work item
    ∩ exact historical Legal work assignment
    ∩ acting principal
    ∩ explicit evaluation instant

It grants no authority and performs no persistence.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from typing import Any

import pytest


AT = datetime(
    2026,
    10,
    17,
    14,
    0,
    tzinfo=timezone.utc,
)

HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128


def _module():
    try:
        from tools.eos.legal_operations.domain import (
            legal_work_completion_authority_evidence as module,
        )
    except ImportError as error:
        pytest.fail(
            "P14_R20R22_COMPLETION_AUTHORITY_"
            "EVIDENCE_DOMAIN_MISSING:"
            + str(error),
            pytrace=False,
        )

    return module


def _value(**overrides: object):
    module = _module()

    values: dict[str, Any] = {
        "completion_authority_evidence_id":
            "completion-authority-evidence-1",
        "tenant_id":
            "tenant-a",
        "case_matter_id":
            "matter-a",
        "work_item_id":
            "work-a",
        "work_item_fingerprint":
            HEX_A,
        "principal_id":
            "principal-a",
        "assignment_id":
            "assignment-a",
        "assignment_fingerprint":
            HEX_B,
        "iam_authorization_evidence_reference":
            "tenant-authorization:decision-a",
        "iam_authorization_evidence_fingerprint":
            HEX_C,
        "evaluated_at":
            AT,
    }

    values.update(overrides)

    return module.LegalWorkCompletionAuthorityEvidence(
        **values
    )


def test_schema_version_and_exact_public_fields():
    module = _module()

    value = _value()

    assert isinstance(module.SCHEMA, str)
    assert module.SCHEMA
    assert isinstance(module.VERSION, str)
    assert module.VERSION

    assert set(value.to_dict()) == {
        "schema",
        "version",
        "completion_authority_evidence_id",
        "tenant_id",
        "case_matter_id",
        "work_item_id",
        "work_item_fingerprint",
        "principal_id",
        "assignment_id",
        "assignment_fingerprint",
        "iam_authorization_evidence_reference",
        "iam_authorization_evidence_fingerprint",
        "evaluated_at",
        "completion_authority_evidence_reference",
        "fingerprint",
    }


def test_evidence_is_frozen_immutable():
    value = _value()

    with pytest.raises(
        FrozenInstanceError
    ):
        value.principal_id = "other"  # type: ignore[misc]


def test_exact_scope_and_lineage_are_preserved():
    value = _value()

    assert value.tenant_id == "tenant-a"
    assert value.case_matter_id == "matter-a"
    assert value.work_item_id == "work-a"
    assert value.work_item_fingerprint == HEX_A

    assert value.principal_id == "principal-a"

    assert value.assignment_id == "assignment-a"
    assert value.assignment_fingerprint == HEX_B

    assert (
        value.iam_authorization_evidence_reference
        == "tenant-authorization:decision-a"
    )

    assert (
        value.iam_authorization_evidence_fingerprint
        == HEX_C
    )

    assert value.evaluated_at == AT


def test_reference_and_fingerprint_are_server_derived():
    value = _value()

    assert isinstance(
        value.completion_authority_evidence_reference,
        str,
    )

    assert (
        value.completion_authority_evidence_reference
    )

    assert isinstance(
        value.fingerprint,
        str,
    )

    assert len(
        value.fingerprint
    ) == 128

    int(
        value.fingerprint,
        16,
    )

    assert (
        value.fingerprint
        == value.fingerprint.lower()
    )


def test_fingerprint_is_deterministic_for_same_semantics():
    first = _value()
    second = _value()

    assert (
        first.fingerprint
        == second.fingerprint
    )

    assert (
        first.completion_authority_evidence_reference
        == second.completion_authority_evidence_reference
    )


@pytest.mark.parametrize(
    "field,replacement",
    (
        (
            "work_item_fingerprint",
            "d" * 128,
        ),
        (
            "assignment_fingerprint",
            "e" * 128,
        ),
        (
            "iam_authorization_evidence_fingerprint",
            "f" * 128,
        ),
        (
            "principal_id",
            "principal-b",
        ),
        (
            "evaluated_at",
            datetime(
                2026,
                10,
                17,
                14,
                0,
                1,
                tzinfo=timezone.utc,
            ),
        ),
    ),
)
def test_every_material_authority_input_changes_identity(
    field: str,
    replacement: object,
):
    baseline = _value()

    changed = _value(
        **{
            field:
                replacement,
        }
    )

    assert (
        changed.fingerprint
        != baseline.fingerprint
    )

    assert (
        changed.completion_authority_evidence_reference
        != baseline.completion_authority_evidence_reference
    )


@pytest.mark.parametrize(
    "field",
    (
        "work_item_fingerprint",
        "assignment_fingerprint",
        "iam_authorization_evidence_fingerprint",
    ),
)
def test_fingerprints_require_lowercase_sha3_512(
    field: str,
):
    module = _module()

    with pytest.raises(
        module.LegalWorkCompletionAuthorityEvidenceError
    ):
        _value(
            **{
                field:
                    "ABC",
            }
        )


@pytest.mark.parametrize(
    "field",
    (
        "completion_authority_evidence_id",
        "tenant_id",
        "case_matter_id",
        "work_item_id",
        "principal_id",
        "assignment_id",
        "iam_authorization_evidence_reference",
    ),
)
def test_identity_text_is_required(
    field: str,
):
    module = _module()

    with pytest.raises(
        module.LegalWorkCompletionAuthorityEvidenceError
    ):
        _value(
            **{
                field:
                    "",
            }
        )


def test_naive_evaluated_at_fails_closed():
    module = _module()

    with pytest.raises(
        module.LegalWorkCompletionAuthorityEvidenceError
    ):
        _value(
            evaluated_at=datetime(
                2026,
                10,
                17,
                14,
                0,
            )
        )


def test_round_trip_is_exact_and_strict():
    module = _module()

    value = _value()

    restored = (
        module.LegalWorkCompletionAuthorityEvidence.from_dict(
            value.to_dict()
        )
    )

    assert restored == value

    malformed = dict(
        value.to_dict()
    )

    malformed["extra"] = True

    with pytest.raises(
        module.LegalWorkCompletionAuthorityEvidenceError
    ):
        module.LegalWorkCompletionAuthorityEvidence.from_dict(
            malformed
        )


def test_evidence_has_no_authority_or_execution_surface():
    module = _module()

    forbidden = {
        "authorize",
        "execute",
        "persist",
        "save",
        "insert",
        "update",
        "delete",
        "complete",
        "transition",
        "invoice",
        "bill",
        "pay",
        "settle",
    }

    public = {
        name.lower()
        for name in vars(
            module.LegalWorkCompletionAuthorityEvidence
        )
        if not name.startswith("_")
    }

    assert not (
        public
        & forbidden
    )
