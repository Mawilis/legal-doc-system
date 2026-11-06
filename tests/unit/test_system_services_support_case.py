from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.system_services.support_case import (
    SupportCase,
    SupportCaseCategory,
    SupportCaseError,
    SupportCaseEvent,
    SupportCaseScope,
    SupportCaseStatus,
)

NOW = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)


def _case(*, scope=SupportCaseScope.SYSTEM, tenant_id=None):
    return SupportCase(
        case_id="case-001",
        scope=scope,
        tenant_id=tenant_id,
        principal_id="principal-001",
        category=SupportCaseCategory.ACCOUNT_ACCESS,
        created_at=NOW,
        updated_at=NOW,
    )


def test_system_case_has_no_tenant_and_round_trips_sanitized_state():
    case = _case()
    assert case.to_document()["tenant_id"] is None
    assert SupportCase.from_document(case.to_document()) == case
    assert "password" not in case.to_document()
    assert "token" not in case.to_document()
    assert "mfa_secret" not in case.to_document()


def test_tenant_case_requires_exact_tenant_binding():
    with pytest.raises(SupportCaseError, match="TENANT_ID_REQUIRED"):
        _case(scope=SupportCaseScope.TENANT)
    case = _case(scope=SupportCaseScope.TENANT, tenant_id="tenant-a")
    assert case.tenant_id == "tenant-a"


def test_system_case_rejects_tenant_binding():
    with pytest.raises(SupportCaseError, match="SYSTEM_CASE_MUST_NOT_BIND_TENANT"):
        _case(tenant_id="tenant-a")


def test_case_lifecycle_requires_identity_verification_before_sensitive_action():
    case = _case()
    triaged = case.transition(SupportCaseStatus.TRIAGED, observed_at=NOW + timedelta(seconds=1))
    with pytest.raises(SupportCaseError, match="CASE_TRANSITION_NOT_ALLOWED"):
        triaged.transition(SupportCaseStatus.ACTION_EXECUTED, observed_at=NOW + timedelta(seconds=2))
    verified = triaged.transition(SupportCaseStatus.IDENTITY_VERIFIED, observed_at=NOW + timedelta(seconds=2))
    pending = verified.transition(SupportCaseStatus.ACTION_PENDING_APPROVAL, observed_at=NOW + timedelta(seconds=3))
    executed = pending.transition(SupportCaseStatus.ACTION_EXECUTED, observed_at=NOW + timedelta(seconds=4))
    assert executed.revision == 4
    assert executed.status is SupportCaseStatus.ACTION_EXECUTED


def test_case_lifecycle_rejects_time_regression_and_terminal_mutation():
    case = _case()
    with pytest.raises(SupportCaseError, match="CASE_TRANSITION_TIME_REGRESSION"):
        case.transition(SupportCaseStatus.TRIAGED, observed_at=NOW - timedelta(seconds=1))
    cancelled = case.transition(SupportCaseStatus.CANCELLED, observed_at=NOW)
    with pytest.raises(SupportCaseError, match="CASE_TRANSITION_NOT_ALLOWED"):
        cancelled.transition(SupportCaseStatus.TRIAGED, observed_at=NOW)


def test_event_requires_actor_idempotency_and_case_binding_fields():
    event = SupportCaseEvent(
        event_id="event-001",
        case_id="case-001",
        actor_principal_id="principal-001",
        idempotency_key="request-001",
        from_status=None,
        to_status=SupportCaseStatus.OPEN,
        action="CASE_CREATED",
        occurred_at=NOW,
        evidence_reference="evidence-001",
    )
    assert event.to_document()["to_status"] == "OPEN"
    assert SupportCaseEvent.from_document(event.to_document()) == event
    with pytest.raises(SupportCaseError, match="CASE_EVENT_IDEMPOTENCY_INVALID"):
        SupportCaseEvent(
            event_id="event-002",
            case_id="case-001",
            actor_principal_id="principal-001",
            idempotency_key=" ",
            from_status=None,
            to_status=SupportCaseStatus.OPEN,
            action="CASE_CREATED",
            occurred_at=NOW,
        )


def test_persisted_schema_and_unknown_state_fail_closed():
    payload = _case().to_document()
    payload["schema"] = "OTHER"
    with pytest.raises(SupportCaseError, match="CASE_SCHEMA_INVALID"):
        SupportCase.from_document(payload)
    payload = _case().to_document()
    payload["password"] = "must-never-persist"
    with pytest.raises(SupportCaseError, match="CASE_PERSISTED_FIELDS_INVALID"):
        SupportCase.from_document(payload)
    payload = _case().to_document()
    payload["status"] = "UNLOCK_EVERYTHING"
    with pytest.raises(SupportCaseError, match="CASE_PERSISTED_STATE_INVALID"):
        SupportCase.from_document(payload)
