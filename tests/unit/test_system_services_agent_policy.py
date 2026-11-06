import pytest

from tools.eos.system_services.agent_policy import (
    AgentEscalationReason,
    AgentWorkflow,
    SELF_SERVICE_ALLOWLIST,
    SystemServicesAgentPolicyError,
    reject_secret_material,
    require_agent_workflow,
    require_human_escalation,
)


def test_agent_has_closed_self_service_allowlist():
    assert require_agent_workflow(AgentWorkflow.PASSWORD_RECOVERY_REQUEST) is AgentWorkflow.PASSWORD_RECOVERY_REQUEST
    assert require_agent_workflow(AgentWorkflow.OWN_SESSION_REVIEW) is AgentWorkflow.OWN_SESSION_REVIEW
    assert require_agent_workflow(AgentWorkflow.OWN_CASE_STATUS) is AgentWorkflow.OWN_CASE_STATUS
    assert len(SELF_SERVICE_ALLOWLIST) == len(AgentWorkflow)


def test_agent_cannot_invent_or_escalate_unlisted_workflows():
    with pytest.raises(SystemServicesAgentPolicyError, match="AGENT_WORKFLOW_NOT_ALLOWLISTED"):
        require_agent_workflow("UNLOCK_ANY_ACCOUNT")
    with pytest.raises(SystemServicesAgentPolicyError, match="AGENT_ESCALATION_REASON_INVALID"):
        require_human_escalation("AGENT_APPROVES_OWN_ACTION")


def test_agent_must_escalate_privileged_and_compromise_cases():
    assert require_human_escalation(AgentEscalationReason.PRIVILEGED_TARGET) is AgentEscalationReason.PRIVILEGED_TARGET
    assert require_human_escalation(AgentEscalationReason.SUSPECTED_ACCOUNT_COMPROMISE) is AgentEscalationReason.SUSPECTED_ACCOUNT_COMPROMISE


@pytest.mark.parametrize("field", [
    "password", "otp", "recovery_token", "mfa_seed", "private_key",
    "session_token", "refresh_token",
])
def test_agent_rejects_credential_and_secret_fields(field):
    with pytest.raises(SystemServicesAgentPolicyError, match="AGENT_SECRET_MATERIAL_FORBIDDEN"):
        reject_secret_material([field])


def test_agent_rejects_malformed_field_set():
    with pytest.raises(SystemServicesAgentPolicyError, match="AGENT_FIELD_SET_INVALID"):
        reject_secret_material(["password", None])
