from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from tools.eos.api import system_services_router as routes
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.system_services.security_incident_response_decision import (
    SecurityIncidentResponseAction,
    SecurityIncidentResponseDecision,
    SecurityIncidentResponseDecisionStatus,
)
from tools.eos.system_services.security_incident_response_execution import (
    SecurityIncidentResponseExecutionError,
)


NOW = datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc)
SESSION = object()


def _decision():
    return SecurityIncidentResponseDecision(
        decision_id="decision-password-reset-route",
        incident_id="incident-password-reset-route",
        tenant_id="tenant-password-reset-route",
        target_principal_id="target-password-reset-route",
        action=SecurityIncidentResponseAction.PASSWORD_RESET,
        requested_by_principal_id="requester-password-reset-route",
        requested_at=NOW,
        request_evidence_reference="incident-evidence-password-reset-route",
    ).decide(
        approved=True,
        decided_by_principal_id="approver-password-reset-route",
        decided_at=NOW + timedelta(minutes=1),
        decision_evidence_reference="independent-approval-password-reset-route",
        expected_revision=0,
    )


def _harness(monkeypatch, *, replay=None, execute_error=None):
    decision = _decision()
    registry = Mock()
    registry.get.return_value = decision
    registry.find_execution.return_value = replay
    incidents = Mock()
    incidents.get_by_id.return_value = SimpleNamespace(
        tenant_id=decision.tenant_id,
        reporter_principal_id=decision.target_principal_id,
    )
    executor = Mock()
    executor.execute_password_reset.side_effect = lambda *args, **kwargs: (
        kwargs["transaction_completion"](
            SESSION, decision.tenant_id, decision.target_principal_id, 8
        ),
        SimpleNamespace(status="PASSWORD_RESET_COMMITTED"),
    )[1]
    if execute_error is not None:
        executor.execute_password_reset.side_effect = execute_error
    monkeypatch.setattr(
        routes,
        "_response_runtime",
        lambda request: (registry, Mock(), executor, Mock()),
    )
    monkeypatch.setattr(
        routes,
        "_assignment_runtime",
        lambda request: (incidents, Mock()),
    )
    monkeypatch.setattr(
        routes,
        "_run_transaction",
        lambda callback: callback(SESSION),
    )
    identity = SimpleNamespace(
        identity_id="independent-executor-password-reset-route",
        status=PrincipalStatus.ACTIVE,
    )
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace()))
    payload = routes.SecurityIncidentPasswordResetExecutionRequest(
        expected_revision=1,
        recovery_token="one-time-recovery-capability",
        new_password="Transient-Strong-Passphrase-2026!",
    )
    return decision, registry, incidents, executor, identity, request, payload


def test_password_reset_route_records_receipt_inside_canonical_transaction(monkeypatch):
    decision, registry, incidents, executor, identity, request, payload = _harness(monkeypatch)

    result = routes.execute_approved_password_reset(
        decision.decision_id,
        payload,
        request,
        "reset-execution-idempotency-1",
        identity,
    )

    assert result == {
        "decisionId": decision.decision_id,
        "status": "PASSWORD_RESET_COMMITTED",
        "replayed": False,
    }
    executor.authorize_password_reset_replay.assert_called_once_with(
        decision,
        actor_principal_id=identity.identity_id,
        session=SESSION,
    )
    executor.execute_password_reset.assert_called_once()
    registry.record_execution.assert_called_once()
    receipt = registry.record_execution.call_args.kwargs
    assert receipt["decision"] is decision
    assert receipt["actor_principal_id"] == identity.identity_id
    assert receipt["result_status"] == "PASSWORD_RESET_COMPLETED"
    assert receipt["result_revision"] == 8
    assert receipt["session"] is SESSION


def test_password_reset_route_replays_only_after_current_execution_authority(monkeypatch):
    replay = {
        "result_status": "PASSWORD_RESET_COMPLETED",
        "result_revision": 8,
    }
    decision, registry, _, executor, identity, request, payload = _harness(
        monkeypatch, replay=replay,
    )

    result = routes.execute_approved_password_reset(
        decision.decision_id,
        payload,
        request,
        "reset-execution-idempotency-1",
        identity,
    )

    assert result == {
        "decisionId": decision.decision_id,
        "status": "PASSWORD_RESET_COMPLETED",
        "credentialRevision": 8,
        "replayed": True,
    }
    executor.authorize_password_reset_replay.assert_called_once()
    executor.execute_password_reset.assert_not_called()


def test_password_reset_route_denies_replay_before_receipt_lookup_without_authority(monkeypatch):
    decision, registry, _, executor, identity, request, payload = _harness(
        monkeypatch,
        execute_error=SecurityIncidentResponseExecutionError(
            "INDEPENDENT_RESPONSE_EXECUTOR_REQUIRED"
        ),
    )
    executor.authorize_password_reset_replay.side_effect = SecurityIncidentResponseExecutionError(
        "INDEPENDENT_RESPONSE_EXECUTOR_REQUIRED"
    )

    with pytest.raises(HTTPException) as captured:
        routes.execute_approved_password_reset(
            decision.decision_id,
            payload,
            request,
            "reset-execution-idempotency-1",
            identity,
        )

    assert captured.value.status_code == 403
    registry.find_execution.assert_not_called()
    executor.execute_password_reset.assert_not_called()
