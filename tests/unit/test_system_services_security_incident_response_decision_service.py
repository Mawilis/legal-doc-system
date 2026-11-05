from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from tools.eos.system_services.security_incident_response_decision import (
    SecurityIncidentResponseAction,
    SecurityIncidentResponseDecision,
)
from tools.eos.system_services.security_incident_response_decision_service import (
    SecurityIncidentResponseDecisionService,
    SecurityIncidentResponseDecisionServiceError,
)


NOW = datetime(2026, 11, 5, 10, 0, tzinfo=timezone.utc)


def pending():
    return SecurityIncidentResponseDecision(
        decision_id="decision-1",
        incident_id="incident-1",
        tenant_id="tenant-1",
        target_principal_id="reporter-principal",
        action=SecurityIncidentResponseAction.PASSWORD_RESET,
        requested_by_principal_id="responder-principal",
        requested_at=NOW,
        request_evidence_reference="incident-evidence-1",
    )


def service_with_mocks():
    value = object.__new__(SecurityIncidentResponseDecisionService)
    value._decisions = Mock()
    value._incidents = Mock()
    value._authorizer = Mock()
    return value


def test_request_requires_current_escalation_permission_and_incident_target_binding():
    value = service_with_mocks()
    incident = SimpleNamespace(
        incident_id="incident-1",
        tenant_id="tenant-1",
        reporter_principal_id="reporter-principal",
    )
    value._incidents.get_by_id.return_value = incident
    decision = pending()
    value._decisions.create.return_value = decision

    result = value.request(
        actor_principal_id="responder-principal",
        decision=decision,
        session="caller-owned-transaction",
    )

    assert result is decision
    value._authorizer.require.assert_called_once_with(
        principal_id="responder-principal",
        permission_id="system_services:incident:escalate",
        session="caller-owned-transaction",
    )
    value._incidents.get_by_id.assert_called_once_with(
        incident_id="incident-1",
        session="caller-owned-transaction",
    )
    value._decisions.create.assert_called_once_with(
        decision,
        session="caller-owned-transaction",
    )


def test_request_cannot_target_a_different_principal_or_tenant():
    value = service_with_mocks()
    value._incidents.get_by_id.return_value = SimpleNamespace(
        incident_id="incident-1",
        tenant_id="tenant-other",
        reporter_principal_id="different-principal",
    )

    with pytest.raises(
        SecurityIncidentResponseDecisionServiceError,
        match="RESPONSE_TARGET_INCIDENT_BINDING_INVALID",
    ):
        value.request(
            actor_principal_id="responder-principal",
            decision=pending(),
            session="caller-owned-transaction",
        )
    value._decisions.create.assert_not_called()


def test_decision_requires_independent_current_response_decide_permission():
    value = service_with_mocks()
    approved = pending().decide(
        approved=True,
        decided_by_principal_id="independent-approver",
        decided_at=NOW + timedelta(minutes=1),
        decision_evidence_reference="approval-evidence-1",
        expected_revision=0,
    )
    value._decisions.decide.return_value = approved

    result = value.decide(
        "decision-1",
        actor_principal_id="independent-approver",
        approved=True,
        decided_at=NOW + timedelta(minutes=1),
        decision_evidence_reference="approval-evidence-1",
        expected_revision=0,
        session="caller-owned-transaction",
    )

    assert result is approved
    value._authorizer.require.assert_called_once_with(
        principal_id="independent-approver",
        permission_id="system_services:incident:response:decide",
        session="caller-owned-transaction",
    )
    value._decisions.decide.assert_called_once_with(
        "decision-1",
        approved=True,
        decided_by_principal_id="independent-approver",
        decided_at=NOW + timedelta(minutes=1),
        decision_evidence_reference="approval-evidence-1",
        expected_revision=0,
        session="caller-owned-transaction",
    )
