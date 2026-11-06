from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.system_services.security_incident_duty import (
    DutyRouteStatus, SecurityIncidentDutyError, SecurityIncidentDutyPolicy,
    SecurityIncidentDutyWindow,
)


def test_duty_policy_routes_only_one_active_explicit_responder():
    now = datetime(2026, 11, 5, 10, tzinfo=timezone.utc)
    policy = SecurityIncidentDutyPolicy(
        policy_id="platform-duty-v1", acknowledgement_minutes=15,
        windows=(SecurityIncidentDutyWindow(
            responder_principal_id="platform-responder-01",
            starts_at=now - timedelta(minutes=30),
            ends_at=now + timedelta(minutes=30),
        ),),
    )
    result = policy.resolve(now=now)
    assert result.status is DutyRouteStatus.ROUTED
    assert result.responder_principal_id == "platform-responder-01"
    assert result.acknowledgement_deadline_at == now + timedelta(minutes=15)
    assert result.policy_id == "platform-duty-v1"


def test_duty_policy_returns_out_of_hours_without_inventing_responder():
    now = datetime(2026, 11, 5, 10, tzinfo=timezone.utc)
    next_shift = now + timedelta(hours=4)
    policy = SecurityIncidentDutyPolicy(
        policy_id="platform-duty-v1", acknowledgement_minutes=20,
        windows=(SecurityIncidentDutyWindow(
            responder_principal_id="platform-responder-02",
            starts_at=next_shift, ends_at=next_shift + timedelta(hours=8),
        ),),
    )
    result = policy.resolve(now=now)
    assert result.status is DutyRouteStatus.OUT_OF_HOURS
    assert result.responder_principal_id is None
    assert result.next_coverage_at == next_shift
    assert result.acknowledgement_deadline_at == now + timedelta(minutes=20)


def test_duty_policy_returns_unstaffed_when_no_rota_is_configured():
    now = datetime(2026, 11, 5, 10, tzinfo=timezone.utc)
    result = SecurityIncidentDutyPolicy(
        policy_id="platform-duty-unconfigured", acknowledgement_minutes=30, windows=(),
    ).resolve(now=now)
    assert result.status is DutyRouteStatus.UNSTAFFED
    assert result.responder_principal_id is None
    assert result.next_coverage_at is None


def test_duty_policy_rejects_overlapping_active_rota_entries():
    now = datetime(2026, 11, 5, 10, tzinfo=timezone.utc)
    policy = SecurityIncidentDutyPolicy(
        policy_id="platform-duty-v1", acknowledgement_minutes=15,
        windows=(
            SecurityIncidentDutyWindow("responder-a", now - timedelta(hours=1), now + timedelta(hours=1)),
            SecurityIncidentDutyWindow("responder-b", now - timedelta(minutes=5), now + timedelta(hours=2)),
        ),
    )
    with pytest.raises(SecurityIncidentDutyError, match="DUTY_ROSTER_OVERLAP_CONFLICT"):
        policy.resolve(now=now)


def test_duty_policy_requires_aware_time_and_bounded_acknowledgement_sla():
    with pytest.raises(SecurityIncidentDutyError, match="DUTY_ACKNOWLEDGEMENT_SLA_INVALID"):
        SecurityIncidentDutyPolicy(policy_id="platform-duty-v1", acknowledgement_minutes=0, windows=())
    policy = SecurityIncidentDutyPolicy(
        policy_id="platform-duty-v1", acknowledgement_minutes=15, windows=(),
    )
    with pytest.raises(SecurityIncidentDutyError, match="DUTY_RESOLUTION_TIME_INVALID"):
        policy.resolve(now=datetime(2026, 11, 5, 10))
