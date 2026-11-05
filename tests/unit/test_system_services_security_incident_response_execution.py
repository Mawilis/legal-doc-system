from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from tools.eos.auth.system_permission_command_evidence import (
    SystemPermissionCommandEvidence,
    SystemPermissionCommandOperation,
)
from tools.eos.system_services.security_incident_response_decision import (
    SecurityIncidentResponseAction,
    SecurityIncidentResponseDecision,
)
from tools.eos.system_services.security_incident_response_execution import (
    SecurityIncidentResponseCanonicalExecutor,
    SecurityIncidentResponseExecutionError,
)


NOW = datetime(2026, 11, 5, 10, 0, tzinfo=timezone.utc)


def approved(action, *, assignment_id=None, permission_id=None):
    return SecurityIncidentResponseDecision(
        decision_id="decision-1",
        incident_id="incident-1",
        tenant_id="tenant-1",
        target_principal_id="target-principal",
        action=action,
        requested_by_principal_id="requester-principal",
        requested_at=NOW,
        request_evidence_reference="incident-evidence-1",
        target_assignment_id=assignment_id,
        target_permission_id=permission_id,
    ).decide(
        approved=True,
        decided_by_principal_id="independent-approver",
        decided_at=NOW + timedelta(minutes=1),
        decision_evidence_reference="governance-approval-1",
        expected_revision=0,
    )


def executor_with_mocks():
    value = object.__new__(SecurityIncidentResponseCanonicalExecutor)
    value._password_reset = Mock()
    value._permission_revocation = Mock()
    value._authorizer = Mock()
    return value


def test_password_reset_delegates_only_approved_decision_to_canonical_service():
    value = executor_with_mocks()
    decision = approved(SecurityIncidentResponseAction.PASSWORD_RESET)
    value._password_reset.reset_password.return_value = "canonical-receipt"

    result = value.execute_password_reset(
        decision,
        actor_principal_id="independent-executor",
        session="caller-owned-transaction",
        recovery_token="transient-single-use-capability",
        new_password="Transient-Strong-Passphrase-2026!",
        context_terms=("WILSY",),
    )

    assert result == "canonical-receipt"
    value._authorizer.require.assert_called_once_with(
        principal_id="independent-executor",
        permission_id="system_services:incident:response:execute",
        session="caller-owned-transaction",
    )
    value._password_reset.reset_password.assert_called_once_with(
        tenant_id="tenant-1",
        recovery_token="transient-single-use-capability",
        new_password="Transient-Strong-Passphrase-2026!",
        context_terms=("WILSY",),
    )


def test_password_reset_executor_must_be_distinct_from_requester_approver_and_target():
    value = executor_with_mocks()
    decision = approved(SecurityIncidentResponseAction.PASSWORD_RESET)

    for actor in ("requester-principal", "independent-approver", "target-principal"):
        with pytest.raises(
            SecurityIncidentResponseExecutionError,
            match="INDEPENDENT_RESPONSE_EXECUTOR_REQUIRED",
        ):
            value.execute_password_reset(
                decision,
                actor_principal_id=actor,
                session="caller-owned-transaction",
                recovery_token="single-use-capability",
                new_password="Transient-Strong-Passphrase-2026!",
            )

    value._authorizer.require.assert_not_called()
    value._password_reset.reset_password.assert_not_called()


def test_password_reset_executor_requires_current_execute_permission():
    value = executor_with_mocks()
    decision = approved(SecurityIncidentResponseAction.PASSWORD_RESET)
    value._authorizer.require.side_effect = PermissionError("CURRENT_SYSTEM_PERMISSION_REQUIRED")

    with pytest.raises(PermissionError, match="CURRENT_SYSTEM_PERMISSION_REQUIRED"):
        value.execute_password_reset(
            decision,
            actor_principal_id="independent-executor",
            session="caller-owned-transaction",
            recovery_token="single-use-capability",
            new_password="Transient-Strong-Passphrase-2026!",
        )

    value._password_reset.reset_password.assert_not_called()


def test_password_reset_decision_does_not_replace_canonical_recovery_capability():
    value = executor_with_mocks()
    decision = approved(SecurityIncidentResponseAction.PASSWORD_RESET)
    value._password_reset.reset_password.side_effect = RuntimeError("RECOVERY_INVALID")

    with pytest.raises(RuntimeError, match="RECOVERY_INVALID"):
        value.execute_password_reset(
            decision,
            actor_principal_id="independent-executor",
            session="caller-owned-transaction",
            recovery_token="invalid-capability",
            new_password="Transient-Strong-Passphrase-2026!",
        )
    value._password_reset.reset_password.assert_called_once()


def test_pending_or_wrong_action_cannot_reach_canonical_service():
    value = executor_with_mocks()
    pending = SecurityIncidentResponseDecision(
        decision_id="decision-2",
        incident_id="incident-2",
        tenant_id="tenant-1",
        target_principal_id="target-principal",
        action=SecurityIncidentResponseAction.PASSWORD_RESET,
        requested_by_principal_id="requester-principal",
        requested_at=NOW,
        request_evidence_reference="incident-evidence-2",
    )
    with pytest.raises(SecurityIncidentResponseExecutionError, match="APPROVED_RESPONSE_DECISION_REQUIRED"):
        value.execute_password_reset(
            pending,
            actor_principal_id="independent-executor",
            session="caller-owned-transaction",
            recovery_token="token",
            new_password="Transient-Strong-Passphrase-2026!",
        )
    with pytest.raises(SecurityIncidentResponseExecutionError, match="RESPONSE_DECISION_ACTION_MISMATCH"):
        value.execute_system_permission_revocation(
            approved(SecurityIncidentResponseAction.PASSWORD_RESET),
            evidence=Mock(),
            session=object(),
        )
    value._password_reset.reset_password.assert_not_called()
    value._permission_revocation.revoke.assert_not_called()


def test_permission_revocation_delegates_exact_approved_lineage_to_canonical_service():
    value = executor_with_mocks()
    decision = approved(
        SecurityIncidentResponseAction.SYSTEM_PERMISSION_REVOCATION,
        assignment_id="assignment-1",
        permission_id="privileged_activation:issue",
    )
    evidence = SystemPermissionCommandEvidence(
        operation=SystemPermissionCommandOperation.REVOKE,
        actor_principal_id="authorized-revocation-operator",
        target_principal_id="target-principal",
        permission_id="privileged_activation:issue",
        evidence_reference="security-incident-response-decision:decision-1",
        occurred_at=NOW + timedelta(minutes=2),
        idempotency_key="revocation-idempotency-1",
        assignment_id="assignment-1",
    )
    value._permission_revocation.revoke.return_value = "canonical-revocation"

    result = value.execute_system_permission_revocation(
        decision,
        evidence=evidence,
        session="caller-owned-transaction",
    )

    assert result == "canonical-revocation"
    value._permission_revocation.revoke.assert_called_once_with(
        evidence,
        session="caller-owned-transaction",
    )
    value._authorizer.require.assert_called_once_with(
        principal_id="authorized-revocation-operator",
        permission_id="system_services:incident:response:execute",
        session="caller-owned-transaction",
    )


def test_permission_revocation_executor_must_be_distinct_from_requester_and_approver():
    value = executor_with_mocks()
    decision = approved(
        SecurityIncidentResponseAction.SYSTEM_PERMISSION_REVOCATION,
        assignment_id="assignment-1",
        permission_id="privileged_activation:issue",
    )
    evidence = SystemPermissionCommandEvidence(
        operation=SystemPermissionCommandOperation.REVOKE,
        actor_principal_id="independent-approver",
        target_principal_id="target-principal",
        permission_id="privileged_activation:issue",
        evidence_reference="security-incident-response-decision:decision-1",
        occurred_at=NOW + timedelta(minutes=2),
        idempotency_key="revocation-idempotency-approver",
        assignment_id="assignment-1",
    )
    with pytest.raises(
        SecurityIncidentResponseExecutionError,
        match="CANONICAL_REVOCATION_EVIDENCE_BINDING_INVALID",
    ):
        value.execute_system_permission_revocation(
            decision,
            evidence=evidence,
            session="caller-owned-transaction",
        )
    value._permission_revocation.revoke.assert_not_called()


def test_permission_revocation_target_cannot_execute_own_containment():
    value = executor_with_mocks()
    decision = approved(
        SecurityIncidentResponseAction.SYSTEM_PERMISSION_REVOCATION,
        assignment_id="assignment-1",
        permission_id="privileged_activation:issue",
    )
    evidence = SystemPermissionCommandEvidence(
        operation=SystemPermissionCommandOperation.REVOKE,
        actor_principal_id="target-principal",
        target_principal_id="target-principal",
        permission_id="privileged_activation:issue",
        evidence_reference="security-incident-response-decision:decision-1",
        occurred_at=NOW + timedelta(minutes=2),
        idempotency_key="revocation-idempotency-target",
        assignment_id="assignment-1",
    )
    with pytest.raises(
        SecurityIncidentResponseExecutionError,
        match="CANONICAL_REVOCATION_EVIDENCE_BINDING_INVALID",
    ):
        value.execute_system_permission_revocation(
            decision,
            evidence=evidence,
            session="caller-owned-transaction",
        )
    value._permission_revocation.revoke.assert_not_called()


def test_permission_revocation_mismatch_fails_before_canonical_service():
    value = executor_with_mocks()
    decision = approved(
        SecurityIncidentResponseAction.SYSTEM_PERMISSION_REVOCATION,
        assignment_id="assignment-approved",
        permission_id="privileged_activation:issue",
    )
    evidence = SystemPermissionCommandEvidence(
        operation=SystemPermissionCommandOperation.REVOKE,
        actor_principal_id="authorized-revocation-operator",
        target_principal_id="target-principal",
        permission_id="privileged_activation:issue",
        evidence_reference="security-incident-response-decision:decision-1",
        occurred_at=NOW + timedelta(minutes=2),
        idempotency_key="revocation-idempotency-2",
        assignment_id="different-assignment",
    )

    with pytest.raises(
        SecurityIncidentResponseExecutionError,
        match="CANONICAL_REVOCATION_EVIDENCE_BINDING_INVALID",
    ):
        value.execute_system_permission_revocation(
            decision,
            evidence=evidence,
            session="caller-owned-transaction",
        )
    value._permission_revocation.revoke.assert_not_called()
