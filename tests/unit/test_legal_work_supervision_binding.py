"""Direct certificate for G7F-R4 Legal Work Supervision Binding."""
from __future__ import annotations

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

from tools.eos.legal_operations.domain.legal_work_supervision_binding import (
    SCHEMA,
    VERSION,
    LegalSupervisionControlLevel,
    LegalSupervisionScope,
    LegalWorkSupervisionBinding,
    LegalWorkSupervisionBindingError,
)


START = datetime(
    2026,
    10,
    12,
    21,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)


def binding(
    *,
    supervision_binding_id: str = "supervision-1",
    tenant_id: str = "tenant-1",
    case_matter_id: str = "matter-1",
    scope: LegalSupervisionScope | str = "WORK_ITEM",
    work_item_id: str | None = "work-1",
    supervisee_principal_id: str = "principal-junior-1",
    supervisor_principal_id: str = "principal-supervisor-1",
    control_level: LegalSupervisionControlLevel | str = "REVIEW_REQUIRED",
    supervision_plan_reference: str = "plan-1",
    supervision_basis_reference: str = "basis-1",
    effective_from: datetime = START,
    effective_until: datetime | None = None,
    supersedes_supervision_binding_id: str | None = None,
) -> LegalWorkSupervisionBinding:
    return LegalWorkSupervisionBinding(
        supervision_binding_id=supervision_binding_id,
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        scope=scope,
        work_item_id=work_item_id,
        supervisee_principal_id=supervisee_principal_id,
        supervisor_principal_id=supervisor_principal_id,
        control_level=control_level,
        supervision_plan_reference=supervision_plan_reference,
        supervision_basis_reference=supervision_basis_reference,
        effective_from=effective_from,
        effective_until=effective_until,
        supersedes_supervision_binding_id=
            supersedes_supervision_binding_id,
    )


def test_identity_is_exact() -> None:
    assert (
        VERSION
        == "v1.0.1-G7F-R4-LEGAL-WORK-SUPERVISION-BINDING"
    )
    assert (
        SCHEMA
        == "WILSY-LEGAL-WORK-SUPERVISION-BINDING/V1"
    )


def test_work_item_supervision_is_exact() -> None:
    value = binding()

    assert (
        value.scope
        is LegalSupervisionScope.WORK_ITEM
    )
    assert value.work_item_id == "work-1"
    assert (
        value.control_level
        is LegalSupervisionControlLevel.REVIEW_REQUIRED
    )
    assert value.effective_from.microsecond == 123456
    assert len(value.fingerprint) == 128


def test_matter_supervision_is_supported() -> None:
    value = binding(
        scope="MATTER",
        work_item_id=None,
        control_level="OVERSIGHT",
    )

    assert (
        value.scope
        is LegalSupervisionScope.MATTER
    )
    assert value.work_item_id is None


@pytest.mark.parametrize(
    "tenant",
    (
        "default",
        "global",
        "root",
        "*",
    ),
)
def test_pseudo_tenants_reject(
    tenant: str,
) -> None:
    with pytest.raises(
        LegalWorkSupervisionBindingError,
        match="G7F_R4_TENANT_REQUIRED",
    ):
        binding(
            tenant_id=tenant,
        )


def test_work_item_scope_requires_work_item() -> None:
    with pytest.raises(
        LegalWorkSupervisionBindingError,
        match=(
            "G7F_R4_WORK_ITEM_SCOPE_REQUIRES_WORK_ITEM"
        ),
    ):
        binding(
            work_item_id=None,
        )


def test_matter_scope_forbids_work_item() -> None:
    with pytest.raises(
        LegalWorkSupervisionBindingError,
        match=(
            "G7F_R4_MATTER_SCOPE_FORBIDS_WORK_ITEM"
        ),
    ):
        binding(
            scope="MATTER",
            work_item_id="work-1",
        )


def test_self_supervision_rejects() -> None:
    with pytest.raises(
        LegalWorkSupervisionBindingError,
        match="G7F_R4_SELF_SUPERVISION_INVALID",
    ):
        binding(
            supervisee_principal_id="principal-1",
            supervisor_principal_id="principal-1",
        )


@pytest.mark.parametrize(
    "level",
    (
        "OVERSIGHT",
        "REVIEW_REQUIRED",
        "PRIOR_APPROVAL_REQUIRED",
    ),
)
def test_all_control_levels_are_supported(
    level: str,
) -> None:
    value = binding(
        control_level=level,
    )

    assert (
        LegalSupervisionControlLevel(
            value.control_level
        ).value
        == level
    )


def test_unknown_control_level_rejects() -> None:
    with pytest.raises(
        LegalWorkSupervisionBindingError,
        match="G7F_R4_CONTROL_LEVEL_INVALID",
    ):
        binding(
            control_level="OPTIONAL",
        )


def test_invalid_effective_period_rejects() -> None:
    with pytest.raises(
        LegalWorkSupervisionBindingError,
        match="G7F_R4_EFFECTIVE_PERIOD_INVALID",
    ):
        binding(
            effective_until=START,
        )


def test_bounded_effective_period_is_preserved() -> None:
    end = START + timedelta(days=90)

    value = binding(
        effective_until=end,
    )

    assert value.effective_until == end


def test_self_supersession_rejects() -> None:
    with pytest.raises(
        LegalWorkSupervisionBindingError,
        match="G7F_R4_SELF_SUPERSESSION_INVALID",
    ):
        binding(
            supervision_binding_id="supervision-1",
            supersedes_supervision_binding_id=
                "supervision-1",
        )


def test_supersession_history_is_supported() -> None:
    value = binding(
        supervision_binding_id="supervision-2",
        supersedes_supervision_binding_id=
            "supervision-1",
    )

    assert (
        value.supersedes_supervision_binding_id
        == "supervision-1"
    )


def test_no_iam_assignment_or_commercial_authority() -> None:
    keys = set(
        binding().to_dict()
    )

    forbidden = {
        "permission",
        "permissions",
        "authorization_role",
        "business_role",
        "assignment_id",
        "assigned_by_principal_id",
        "plan_id",
        "subscription_id",
        "entitlement_id",
        "price",
        "invoice_id",
        "payment_id",
        "financial_execution",
    }

    assert not keys & forbidden


def test_no_self_declared_currentness() -> None:
    keys = set(
        binding().to_dict()
    )

    assert "is_current" not in keys
    assert "current" not in keys
    assert "active" not in keys
    assert "status" not in keys


def test_round_trip_preserves_exact_truth() -> None:
    original = binding()

    restored = (
        LegalWorkSupervisionBinding.from_dict(
            original.to_dict()
        )
    )

    assert restored == original


def test_corrupt_fingerprint_rejects() -> None:
    payload = binding().to_dict()
    payload["fingerprint"] = "a" * 128

    with pytest.raises(
        LegalWorkSupervisionBindingError,
        match="G7F_R4_FINGERPRINT_MISMATCH",
    ):
        LegalWorkSupervisionBinding.from_dict(
            payload
        )


def test_extra_or_missing_field_rejects() -> None:
    payload = binding().to_dict()
    payload["extra"] = "x"

    with pytest.raises(
        LegalWorkSupervisionBindingError,
        match="G7F_R4_PAYLOAD_SCHEMA_INVALID",
    ):
        LegalWorkSupervisionBinding.from_dict(
            payload
        )

    payload = binding().to_dict()
    del payload["control_level"]

    with pytest.raises(
        LegalWorkSupervisionBindingError,
        match="G7F_R4_PAYLOAD_SCHEMA_INVALID",
    ):
        LegalWorkSupervisionBinding.from_dict(
            payload
        )


# ARTIFACT: test_legal_work_supervision_binding.py
# VERSION: v1.0.1-G7F-R4-LEGAL-WORK-SUPERVISION-BINDING-CERT
