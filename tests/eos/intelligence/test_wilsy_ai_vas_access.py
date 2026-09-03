"""WILSY AI VAS access contract certificate."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from tools.eos.intelligence.domain.vas_access import (
    VERSION,
    WilsyAIVASAccess,
)


def _access(**changes: object) -> WilsyAIVASAccess:
    values = {
        "tenant_id": "TENANT-001",
        "principal_id": "PRINCIPAL-001",
        "scope_ref": "SCOPE-001",
        "entitlement_ref": "ENTITLEMENT-001",
        "subscription_ref": "SUBSCRIPTION-001",
        "entitlement_evidence_refs": (
            "EVIDENCE-ENTITLEMENT-001",
        ),
        "usage_evidence_refs": (
            "EVIDENCE-USAGE-SNAPSHOT-001",
        ),
        "business_profile_ref": "BUSINESS-PROFILE-001",
        "business_profile_evidence_refs": (
            "EVIDENCE-BUSINESS-PROFILE-001",
        ),
        "business_type": "Legal Practice",
        "dashboard_id": "DASHBOARD-LEGAL-001",
        "dashboard_domain": "LEGAL",
        "allowed_domains": (
            "BILLING",
            "CRM",
            "LEGAL",
        ),
        "allowed_capabilities": (
            "EXPLAIN",
            "RECOMMEND",
            "SUMMARIZE",
        ),
        "usage_limit": 1000,
        "usage_consumed": 125,
        "evaluated_at":
            "2026-09-03T12:00:00+02:00",
    }

    values.update(changes)

    return WilsyAIVASAccess(**values)  # type: ignore[arg-type]


def test_version_is_exact() -> None:
    assert VERSION == "v1.0.0-WILSY-AI-VAS-ACCESS"


def test_access_is_explicit_and_deterministic() -> None:
    first = _access()
    second = _access()

    assert first == second
    assert first.checksum == second.checksum
    assert first.checksum.startswith("sha3-512:")
    assert first.usage_remaining == 875
    assert (
        first.evaluated_at
        == "2026-09-03T10:00:00+00:00"
    )


def test_access_is_immutable() -> None:
    access = _access()

    with pytest.raises(FrozenInstanceError):
        access.tenant_id = "OTHER"  # type: ignore[misc]


def test_entitlement_evidence_is_mandatory() -> None:
    with pytest.raises(
        ValueError,
        match="entitlement_evidence_refs",
    ):
        _access(entitlement_evidence_refs=())


def test_usage_snapshot_evidence_is_mandatory() -> None:
    with pytest.raises(
        ValueError,
        match="usage_evidence_refs",
    ):
        _access(usage_evidence_refs=())


def test_business_profile_evidence_is_mandatory() -> None:
    with pytest.raises(
        ValueError,
        match="business_profile_evidence_refs",
    ):
        _access(business_profile_evidence_refs=())


def test_exhausted_usage_fails_closed() -> None:
    with pytest.raises(
        ValueError,
        match="^NO_ENTITLEMENT_CAPACITY$",
    ):
        _access(
            usage_limit=100,
            usage_consumed=100,
        )


def test_dashboard_domain_must_be_entitled() -> None:
    with pytest.raises(
        ValueError,
        match="^DASHBOARD_DOMAIN_NOT_ENTITLED$",
    ):
        _access(
            dashboard_domain="PAYROLL",
        )


def test_domains_and_capabilities_are_explicit() -> None:
    access = _access()

    assert access.permits_domain("legal")
    assert access.permits_domain("CRM")
    assert not access.permits_domain("PAYROLL")

    assert access.permits_capability("explain")
    assert access.permits_capability("RECOMMEND")
    assert not access.permits_capability("EXECUTE")


def test_non_advisory_capability_fails_closed() -> None:
    for capability in (
        "APPROVE",
        "AUTHORIZE",
        "EXECUTE",
        "PAY",
        "RELEASE",
        "SETTLE",
    ):
        with pytest.raises(
            ValueError,
            match="^UNSUPPORTED_AI_CAPABILITY$",
        ):
            _access(
                allowed_capabilities=(capability,),
            )


def test_canonical_order_is_required() -> None:
    with pytest.raises(
        ValueError,
        match="canonical sorted order",
    ):
        _access(
            allowed_domains=(
                "LEGAL",
                "CRM",
            )
        )


def test_no_identity_or_time_defaults_exist() -> None:
    with pytest.raises(TypeError):
        WilsyAIVASAccess()  # type: ignore[call-arg]


def test_projection_does_not_create_execution_authority() -> None:
    projected = _access().to_dict()

    assert "execute" not in projected
    assert "payment" not in projected
    assert "release" not in projected
    assert "settlement" not in projected


def test_business_type_and_dashboard_are_context_not_authority() -> None:
    access = _access()

    assert access.business_type == "Legal Practice"
    assert access.dashboard_domain == "LEGAL"

    # They refine assistance only. The explicit domain entitlement
    # remains independently mandatory.
    assert access.dashboard_domain in access.allowed_domains
