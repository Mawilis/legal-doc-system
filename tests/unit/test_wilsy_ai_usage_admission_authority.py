"""WILSY AI admission single-held capacity certificate.

TITLE: WILSY OS AI Admission Capacity Unit Certificate
VERSION: v1.0.0-C1B-SINGLE-HELD-ACCOUNTING
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify that P6 completed-usage capacity and C1B holds are
         considered once, in the registry's atomic transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_usage_admission_authority.py
COLLABORATION / OWNERSHIP: C1B admission authority contract with the
                           capacity orchestrator and reservation registry.
CERTIFICATION / UPDATE DATE: 2026-11-21
CHANGELOG: v1.0.0-C1B-SINGLE-HELD-ACCOUNTING certifies canonical daily
           remaining capacity handoff and fail-closed dependency behaviour.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic tenant, no provider API or personal data.
TENANT BOUNDARY: Exact tenant and entitlement are never inferred from caller role.
AUTHORITY BOUNDARY: Mocked reservation only, no actual database write or grant.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
FAIL-CLOSED DECLARATION: Rejects invalid units and inaccessible capacity.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from tools.eos.saas.billing.wilsy_ai_usage_admission_authority import (
    WilsyAIUsageAdmissionAuthority,
    WilsyAIUsageAdmissionAuthorityError,
)

AT = datetime(2026, 11, 21, 11, tzinfo=timezone.utc)


@pytest.mark.parametrize(("daily_remaining", "already_held"), [
    (450, 0), (450, 6), (7, 6), (6, 6),
])
def test_atomic_registry_receives_capacity_without_double_subtraction(
    daily_remaining: int, already_held: int,
) -> None:
    """Registry owns the only held subtraction, including boundary capacity."""
    capacity = Mock()
    capacity.derive_capacity.return_value = SimpleNamespace(
        daily_window_start=AT,
        daily_window_end=AT + timedelta(days=1),
        daily_remaining_request_units=daily_remaining,
        module_id="WILSY_AI_REASONING",
        entitlement_revision=1,
        entitlement_fingerprint="a" * 128,
    )
    registry = Mock()
    registry.held_request_units.return_value = already_held
    registry.reserve.side_effect = lambda admission, *, available_request_units, session: admission
    authority = WilsyAIUsageAdmissionAuthority(
        capacity_orchestrator=capacity, admission_registry=registry,
    )
    session = object()
    evidence = authority.reserve(
        tenant_id="tenant-capacity-cert",
        entitlement_id="wai-" + "b" * 128,
        idempotency_key="key-capacity-cert",
        admission_id="admission-capacity-cert",
        as_of=AT,
        session=session,
    )
    assert evidence.reserved_request_units == 1
    assert registry.reserve.call_args.kwargs["available_request_units"] == daily_remaining
    assert registry.reserve.call_args.kwargs["session"] is session
    assert evidence.tenant_id == "tenant-capacity-cert"
    assert evidence.entitlement_id == "wai-" + "b" * 128
    registry.held_request_units.assert_not_called()
    capacity.derive_capacity.assert_called_once()


def test_capacity_failure_never_writes_reservation() -> None:
    """Fail closed before reservation when P6 capacity is unavailable."""
    capacity = Mock()
    capacity.derive_capacity.side_effect = RuntimeError("internal transport")
    registry = Mock()
    authority = WilsyAIUsageAdmissionAuthority(
        capacity_orchestrator=capacity, admission_registry=registry,
    )
    with pytest.raises(WilsyAIUsageAdmissionAuthorityError, match="C1B_ADMISSION_REJECTED"):
        authority.reserve(
            tenant_id="tenant-capacity-cert",
            entitlement_id="wai-" + "b" * 128,
            idempotency_key="key-capacity-cert",
            as_of=AT,
            session=object(),
        )
    registry.reserve.assert_not_called()


# ARTIFACT: test_wilsy_ai_usage_admission_authority.py
# VERSION: v1.0.0-C1B-SINGLE-HELD-ACCOUNTING
# AUTHORITY BOUNDARY: synthetic admission-capacity contract only
# TENANT POSTURE: exact synthetic tenant; no privilege inference
# FAIL-CLOSED POSTURE: no reservation after source failure
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
