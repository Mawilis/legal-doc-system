"""WILSY P47-R95 operational practitioner/matter access lifecycle.

VERSION: v1.0.0-P47-R95-G10-TEST-FIRST
CONTRACT: Immutable access events and fail-closed currentness.
NO IAM, ISSUER, MATTER ADMISSION OR EXECUTION AUTHORITY.
"""

from datetime import datetime, timezone, timedelta

import pytest

from tools.eos.legal_operations.domain.legal_work_operational_matter_access import (
    LegalWorkMatterAccessEvent,
    LegalWorkMatterAccessError,
    project_legal_work_matter_access_currentness,
)

NOW = datetime(2026, 10, 21, 8, 0, tzinfo=timezone.utc)

def event(
    *,
    tenant_id="tenant-001",
    case_matter_id="matter-001",
    principal_id="practitioner-001",
    decision="GRANTED",
    event_id="event-001",
    predecessor_event_id=None,
    at=NOW,
):
    return LegalWorkMatterAccessEvent(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        practitioner_principal_id=principal_id,
        event_id=event_id,
        predecessor_event_id=predecessor_event_id,
        decision=decision,
        occurred_at=at,
        issuer_principal_id="partner-001",
        issuer_authorization_evidence_reference="issuer-proof-001",
        reason_reference="matter-team-appointment-001",
    )

def project(history):
    return project_legal_work_matter_access_currentness(
        tenant_id="tenant-001",
        case_matter_id="matter-001",
        practitioner_principal_id="practitioner-001",
        evaluation_time=NOW + timedelta(minutes=2),
        events=history,
    )

def test_empty_history_does_not_establish_access():
    result = project(())
    assert result.state == "NO_GRANT"
    assert result.permits_operational_access is False

def test_historical_grant_is_not_self_authorizing():
    result = project((event(),))
    assert result.state == "GRANTED_UNVERIFIED"
    assert result.permits_operational_access is False

def test_revocation_blocks_historical_grant():
    result = project((
        event(),
        event(
            decision="REVOKED",
            event_id="event-002",
            predecessor_event_id="event-001",
            at=NOW + timedelta(minutes=1),
        ),
    ))
    assert result.state == "REVOKED"
    assert result.permits_operational_access is False

@pytest.mark.parametrize("overrides", [
    {"tenant_id": "tenant-foreign"},
    {"case_matter_id": "matter-foreign"},
    {"principal_id": "practitioner-foreign"},
])
def test_cross_scope_history_fails_closed(overrides):
    result = project((event(**overrides),))
    assert result.state == "CORRUPT_BLOCKED"
    assert result.permits_operational_access is False

def test_forged_or_missing_issuer_reference_rejected():
    with pytest.raises(LegalWorkMatterAccessError):
        event().__class__(
            tenant_id="tenant-001",
            case_matter_id="matter-001",
            practitioner_principal_id="practitioner-001",
            event_id="event-bad",
            predecessor_event_id=None,
            decision="GRANTED",
            occurred_at=NOW,
            issuer_principal_id="partner-001",
            issuer_authorization_evidence_reference="",
            reason_reference="reason-001",
        )

def test_divergent_same_predecessor_fails_closed():
    result = project((
        event(event_id="event-001"),
        event(
            event_id="event-002",
            predecessor_event_id="event-001",
            at=NOW + timedelta(minutes=1),
        ),
        event(
            event_id="event-003",
            predecessor_event_id="event-001",
            at=NOW + timedelta(minutes=1),
        ),
    ))
    assert result.state == "CORRUPT_BLOCKED"
    assert result.permits_operational_access is False

def test_future_grant_is_not_current():
    result = project((
        event(at=NOW + timedelta(hours=1)),
    ))
    assert result.state == "NO_GRANT"
    assert result.permits_operational_access is False


def test_revoked_grant_cannot_be_resurrected():
    from datetime import timedelta

    result = project((
        event(),
        event(
            decision="REVOKED",
            event_id="event-002",
            predecessor_event_id="event-001",
            at=NOW + timedelta(minutes=1),
        ),
        event(
            decision="GRANTED",
            event_id="event-003",
            predecessor_event_id="event-002",
            at=NOW + timedelta(minutes=2),
        ),
    ))
    assert result.state == "CORRUPT_BLOCKED"
    assert result.permits_operational_access is False


def test_future_successor_cannot_resurrect_revocation():
    from datetime import timedelta

    result = project((
        event(),
        event(
            decision="REVOKED",
            event_id="event-002",
            predecessor_event_id="event-001",
            at=NOW + timedelta(minutes=1),
        ),
        event(
            decision="GRANTED",
            event_id="event-003",
            predecessor_event_id="event-002",
            at=NOW + timedelta(hours=1),
        ),
    ))
    assert result.state == "CORRUPT_BLOCKED"
    assert result.permits_operational_access is False


def test_mutated_historical_event_fails_integrity():
    recorded = event()
    object.__setattr__(recorded, "reason_reference", "tampered-reason")
    result = project((recorded,))
    assert result.state == "CORRUPT_BLOCKED"
    assert result.permits_operational_access is False
