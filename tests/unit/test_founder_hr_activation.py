"""TITLE: WILSY OS Founder HR Activation Operator Direct Certificate
VERSION: v1.1.0-DIRECTOR-OPT-IN-BOOTSTRAP-CERT
AUTHORITY: In-memory tests of governed activation ordering, tenant fence and failure.
EPITOME: Prove no HR success is emitted until entitlement, role, capacity and
         bounded source checks complete; no real issuer or database is invoked.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_founder_hr_activation.py
COLLABORATION / OWNERSHIP: Founder HR activation operator and IAM preflight.
CERTIFICATION / UPDATE DATE: 2026-11-27
CHANGELOG: v1.1.0-DIRECTOR-OPT-IN-BOOTSTRAP-CERT verifies opt-in Director sequencing and negative Director readback without issuing HR authority.
           v1.0.0-FOUNDER-HR-OPERATOR-CERT adds fail-closed stage and tenant tests.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic non-secret identities and inert database.
TENANT BOUNDARY: Exact canonical Founder employer, no alias.
AUTHORITY BOUNDARY: Tests only; no roles or product entitlements are granted.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.ops import founder_hr_activation as subject
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID


def _identity(tenant: str = WILSY_COMPANY_TENANT_ID) -> Any:
    return SimpleNamespace(tenant_id=tenant)


def test_exact_canonical_tenant_required_before_any_issuance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def deny(*_args: Any, **_kwargs: Any) -> None:
        pytest.fail("unverified issuer call")
    monkeypatch.setattr(subject, "_issue_hr_entitlement", deny)
    with pytest.raises(subject.FounderHRActivationError, match="TENANT_DENIED"):
        subject.activate_founder_hr(_identity("foreign"), object(), object())


def test_activation_orders_source_governed_stages_and_retains_http_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        subject, "_issue_hr_entitlement",
        lambda *_args: calls.append("entitlement"),
    )
    monkeypatch.setattr(
        subject, "_activate_manager_assignment",
        lambda *_args: calls.append("invitation"),
    )
    monkeypatch.setattr(
        subject, "_activate_manager_capacity",
        lambda *_args: calls.append("capacity"),
    )
    monkeypatch.setattr(
        subject, "inspect_founder_hr_prerequisites",
        lambda *_args: {
            "hr_manager_capacity_active": True,
            "hr_manager_authorization_role_active": True,
            "tenant_owner_capacity_active": True,
        },
    )
    result = subject.activate_founder_hr(_identity(), object(), object())
    assert calls == ["entitlement", "invitation", "capacity"]
    assert result["authenticated_http_verified"] is False
    assert result["employee_admission"] == "NOT_ISSUED"
    assert result["hr_director"] == "NOT_ISSUED"
    assert result["next"] == "REAUTHENTICATE_AND_VERIFY_FOUR_HR_ROUTES"
    assert "principal_id" not in result


@pytest.mark.parametrize("failed_stage", [
    "_issue_hr_entitlement",
    "_activate_manager_assignment",
    "_activate_manager_capacity",
])
def test_any_issuer_failure_stops_without_claiming_success(
    monkeypatch: pytest.MonkeyPatch,
    failed_stage: str,
) -> None:
    calls: list[str] = []
    stage_names = [
        "_issue_hr_entitlement",
        "_activate_manager_assignment",
        "_activate_manager_capacity",
    ]
    for name in stage_names:
        def callback(*_args: Any, stage: str = name) -> None:
            calls.append(stage)
            if stage == failed_stage:
                raise subject.FounderHRActivationError("ISSUANCE_DENIED")
        monkeypatch.setattr(subject, name, callback)
    with pytest.raises(subject.FounderHRActivationError, match="ISSUANCE_DENIED"):
        subject.activate_founder_hr(_identity(), object(), object())
    assert calls == stage_names[:stage_names.index(failed_stage) + 1]


def test_missing_durable_role_readback_never_claims_hr_activation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in (
        "_issue_hr_entitlement",
        "_activate_manager_assignment",
        "_activate_manager_capacity",
    ):
        monkeypatch.setattr(subject, name, lambda *_args: None)
    monkeypatch.setattr(
        subject, "inspect_founder_hr_prerequisites",
        lambda *_args: {
            "tenant_owner_capacity_active": True,
            "hr_manager_capacity_active": False,
            "hr_manager_authorization_role_active": True,
        },
    )
    with pytest.raises(subject.FounderHRActivationError, match="READBACK_FAILED"):
        subject.activate_founder_hr(_identity(), object(), object())


def test_director_bootstrap_explicit_opt_in_preserves_other_authorities(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    for name in (
        "_issue_hr_entitlement", "_activate_manager_assignment",
        "_activate_manager_capacity", "_activate_director_assignment",
        "_activate_director_capacity",
    ):
        monkeypatch.setattr(
            subject, name, lambda *_args, stage=name: calls.append(stage),
        )
    monkeypatch.setattr(
        subject, "inspect_founder_hr_prerequisites",
        lambda *_args: {
            "tenant_owner_capacity_active": True,
            "hr_manager_capacity_active": True,
            "hr_manager_authorization_role_active": True,
            "hr_director_capacity_active": True,
            "hr_director_authorization_role_active": True,
        },
    )
    result = subject.activate_founder_hr(
        _identity(), object(), object(), activate_director=True,
    )
    assert calls == [
        "_issue_hr_entitlement", "_activate_manager_assignment",
        "_activate_manager_capacity", "_activate_director_assignment",
        "_activate_director_capacity",
    ]
    assert result["hr_director"] == "ACTIVE_DURABLE_READBACK"
    assert result["founder_owner_preserved"] is True
    assert result["independent_self_approval"] == "NOT_AUTHORIZED"
    assert result["employee_admission"] == "NOT_ISSUED"
    assert result["authenticated_http_verified"] is False


def test_director_stage_failure_prevents_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in (
        "_issue_hr_entitlement", "_activate_manager_assignment",
        "_activate_manager_capacity", "_activate_director_assignment",
        "_activate_director_capacity",
    ):
        monkeypatch.setattr(subject, name, lambda *_args: None)
    monkeypatch.setattr(
        subject, "inspect_founder_hr_prerequisites",
        lambda *_args: {
            "tenant_owner_capacity_active": True,
            "hr_manager_capacity_active": True,
            "hr_manager_authorization_role_active": True,
            "hr_director_capacity_active": False,
            "hr_director_authorization_role_active": True,
        },
    )
    with pytest.raises(subject.FounderHRActivationError, match="DIRECTOR_IAM_READBACK_FAILED"):
        subject.activate_founder_hr(
            _identity(), object(), object(), activate_director=True,
        )


# ARTIFACT: tests/unit/test_founder_hr_activation.py
# VERSION: v1.1.0-DIRECTOR-OPT-IN-BOOTSTRAP-CERT
# AUTHORITY BOUNDARY: Synthetic orchestration tests; no identity or tenant mutations.
# TENANT POSTURE: Exact canonical employer; cross-tenant operations fail before issuer calls.
# FAIL-CLOSED POSTURE: No incomplete stage produces activated HR result.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
