"""
Direct certificate for the pure privileged-eligibility domain.

VERSION:
v1.0.0-P2-R1-PRIVILEGED-ELIGIBILITY-DIRECT-CERT
"""

from dataclasses import FrozenInstanceError
import inspect

import pytest

from tools.eos.auth.privileged_eligibility import (
    ENTERPRISE_ADMIN,
    SOVEREIGN_ARCHITECT,
    PrivilegedEligibilityDecision,
    PrivilegedEligibilityReason,
    PrivilegedTargetClass,
    evaluate_privileged_eligibility,
)


def test_enterprise_admin_current_tenant_principal_is_structurally_eligible() -> None:
    decision = evaluate_privileged_eligibility(
        principal_id="principal-1",
        privileged_role_id=ENTERPRISE_ADMIN,
        principal_current=True,
        tenant_id="tenant-1",
        tenant_membership_current=True,
        workforce_required=False,
    )

    assert decision.eligible is True
    assert (
        decision.target_class
        is PrivilegedTargetClass.TENANT_PRIVILEGED
    )
    assert (
        decision.reason
        is PrivilegedEligibilityReason.ELIGIBLE
    )


def test_enterprise_admin_workforce_required_fails_closed_when_not_current() -> None:
    decision = evaluate_privileged_eligibility(
        principal_id="principal-1",
        privileged_role_id=ENTERPRISE_ADMIN,
        principal_current=True,
        tenant_id="tenant-1",
        tenant_membership_current=True,
        workforce_required=True,
        tenant_workforce_current=False,
    )

    assert decision.eligible is False
    assert (
        decision.reason
        is PrivilegedEligibilityReason
        .TENANT_WORKFORCE_NOT_CURRENT
    )


def test_enterprise_admin_requires_current_membership() -> None:
    for current in (
        False,
        None,
    ):
        decision = evaluate_privileged_eligibility(
            principal_id="principal-1",
            privileged_role_id=ENTERPRISE_ADMIN,
            principal_current=True,
            tenant_id="tenant-1",
            tenant_membership_current=current,
        )

        assert decision.eligible is False
        assert (
            decision.reason
            is PrivilegedEligibilityReason
            .TENANT_MEMBERSHIP_NOT_CURRENT
        )


def test_enterprise_admin_requires_exact_tenant_scope() -> None:
    decision = evaluate_privileged_eligibility(
        principal_id="principal-1",
        privileged_role_id=ENTERPRISE_ADMIN,
        principal_current=True,
        tenant_membership_current=True,
    )

    assert decision.eligible is False
    assert (
        decision.reason
        is PrivilegedEligibilityReason
        .TENANT_SCOPE_REQUIRED
    )


def test_inactive_principal_denies_both_privileged_classes() -> None:
    tenant = evaluate_privileged_eligibility(
        principal_id="principal-1",
        privileged_role_id=ENTERPRISE_ADMIN,
        principal_current=False,
        tenant_id="tenant-1",
        tenant_membership_current=True,
    )

    root = evaluate_privileged_eligibility(
        principal_id="principal-1",
        privileged_role_id=SOVEREIGN_ARCHITECT,
        principal_current=False,
        platform_prerequisite_proven=True,
    )

    assert tenant.eligible is False
    assert root.eligible is False

    assert (
        tenant.reason
        is PrivilegedEligibilityReason
        .PRINCIPAL_NOT_CURRENT
    )

    assert (
        root.reason
        is PrivilegedEligibilityReason
        .PRINCIPAL_NOT_CURRENT
    )


def test_sovereign_architect_requires_proven_platform_prerequisite() -> None:
    for proven in (
        False,
        None,
    ):
        decision = evaluate_privileged_eligibility(
            principal_id="principal-1",
            privileged_role_id=SOVEREIGN_ARCHITECT,
            principal_current=True,
            platform_prerequisite_proven=proven,
        )

        assert decision.eligible is False
        assert (
            decision.target_class
            is PrivilegedTargetClass
            .PLATFORM_SYSTEM_ROOT
        )
        assert (
            decision.reason
            is PrivilegedEligibilityReason
            .PLATFORM_PREREQUISITE_NOT_PROVEN
        )


def test_sovereign_architect_never_accepts_tenant_authority_material() -> None:
    decision = evaluate_privileged_eligibility(
        principal_id="principal-1",
        privileged_role_id=SOVEREIGN_ARCHITECT,
        principal_current=True,
        tenant_id="tenant-1",
        tenant_membership_current=True,
        tenant_workforce_current=True,
        platform_prerequisite_proven=True,
    )

    assert decision.eligible is False
    assert (
        decision.reason
        is PrivilegedEligibilityReason
        .PLATFORM_SCOPE_MUST_NOT_CARRY_TENANT
    )


def test_sovereign_architect_can_be_structurally_eligible_only_with_platform_fact() -> None:
    decision = evaluate_privileged_eligibility(
        principal_id="principal-machine-or-human",
        privileged_role_id=SOVEREIGN_ARCHITECT,
        principal_current=True,
        platform_prerequisite_proven=True,
    )

    assert decision.eligible is True
    assert (
        decision.target_class
        is PrivilegedTargetClass
        .PLATFORM_SYSTEM_ROOT
    )
    assert decision.tenant_id is None


@pytest.mark.parametrize(
    "role",
    (
        "AUDITOR",
        "SERVICE_WORKER",
        "SUPER_ADMIN",
        "FOUNDER",
        "GLOBAL_ROOT",
        "",
        " ENTERPRISE_ADMIN",
    ),
)
def test_unknown_or_legacy_root_targets_fail_closed(
    role: str,
) -> None:
    decision = evaluate_privileged_eligibility(
        principal_id="principal-1",
        privileged_role_id=role,
        principal_current=True,
        tenant_id="tenant-1",
        tenant_membership_current=True,
    )

    assert decision.eligible is False

    assert decision.reason in {
        PrivilegedEligibilityReason
        .UNKNOWN_PRIVILEGED_TARGET,
        PrivilegedEligibilityReason
        .MALFORMED_INPUT,
    }


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("principal_id", ""),
        ("principal_id", " principal-1"),
        ("principal_current", "yes"),
        ("tenant_id", ""),
        ("tenant_membership_current", "yes"),
        ("workforce_required", "yes"),
        ("tenant_workforce_current", "yes"),
        ("platform_prerequisite_proven", "yes"),
    ),
)
def test_malformed_input_fails_closed(
    field: str,
    value: object,
) -> None:
    kwargs: dict[str, object] = {
        "principal_id": "principal-1",
        "privileged_role_id": ENTERPRISE_ADMIN,
        "principal_current": True,
        "tenant_id": "tenant-1",
        "tenant_membership_current": True,
    }

    kwargs[field] = value

    decision = evaluate_privileged_eligibility(
        **kwargs
    )

    assert decision.eligible is False
    assert (
        decision.reason
        is PrivilegedEligibilityReason
        .MALFORMED_INPUT
    )


def test_decision_is_immutable() -> None:
    decision = evaluate_privileged_eligibility(
        principal_id="principal-1",
        privileged_role_id=ENTERPRISE_ADMIN,
        principal_current=True,
        tenant_id="tenant-1",
        tenant_membership_current=True,
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        decision.eligible = False  # type: ignore[misc]


def test_module_exposes_no_assignment_activation_or_authorization_api() -> None:
    import tools.eos.auth.privileged_eligibility as module

    forbidden = {
        "assign",
        "grant",
        "activate",
        "authorize",
        "revoke",
        "persist",
        "create_session",
        "break_glass",
        "execute",
    }

    names = set(dir(module))

    assert not names.intersection(
        forbidden
    )


def test_domain_signature_contains_no_principal_kind_mfa_session_or_finance() -> None:
    parameters = set(
        inspect.signature(
            evaluate_privileged_eligibility
        ).parameters
    )

    forbidden = {
        "principal_kind",
        "is_service_account",
        "human",
        "machine",
        "ai",
        "mfa_registered",
        "security_assurance",
        "activation_id",
        "session_id",
        "refresh_token",
        "financial_authority",
    }

    assert not parameters.intersection(
        forbidden
    )


def test_domain_has_no_io_import_surface() -> None:
    import tools.eos.auth.privileged_eligibility as module

    source = inspect.getsource(module)

    for forbidden in (
        "pymongo",
        "fastapi",
        "requests",
        "httpx",
        "get_database",
        "get_client",
        "RoleAssignmentRepository",
        "TenantMembershipRepository",
        "AuthRegistry",
    ):
        assert forbidden not in source


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_privileged_eligibility.py
# VERSION: v1.0.0-P2-R1-PRIVILEGED-ELIGIBILITY-DIRECT-CERT
# AUTHORITY BOUNDARY: pure eligibility semantics only
# PRINCIPAL POSTURE: no principal-kind discrimination
# TENANT POSTURE: ENTERPRISE_ADMIN is tenant scoped
# ROOT POSTURE: SOVEREIGN_ARCHITECT is platform/system-root scoped
# PLATFORM POSTURE: explicit prerequisite fact required; no source invented
# FINANCIAL EXECUTION AUTHORITY: None
# END OF WILSY OS SOVEREIGN ARTIFACT
