"""Closed self-service action policy for the WILSY System Services Agent.

This module defines allowed workflow identifiers and escalation triggers only.
It grants no identity, account, session, MFA, recovery, or IAM authority.
"""
from __future__ import annotations

from enum import StrEnum
from typing import Final

VERSION: Final[str] = "v1.0.0-SYSTEM-SERVICES-AGENT-SELF-SERVICE-POLICY"


class AgentWorkflow(StrEnum):
    HELP_CONTENT = "HELP_CONTENT"
    PASSWORD_RECOVERY_REQUEST = "PASSWORD_RECOVERY_REQUEST"
    RECOVERY_CONTACT_VERIFICATION_REQUEST = "RECOVERY_CONTACT_VERIFICATION_REQUEST"
    MFA_ENROLLMENT_GUIDANCE = "MFA_ENROLLMENT_GUIDANCE"
    MFA_CHALLENGE_GUIDANCE = "MFA_CHALLENGE_GUIDANCE"
    SIGN_IN_ACTIVITY_REVIEW = "SIGN_IN_ACTIVITY_REVIEW"
    OWN_SESSION_REVIEW = "OWN_SESSION_REVIEW"
    OWN_SESSION_REVOCATION_REQUEST = "OWN_SESSION_REVOCATION_REQUEST"
    OWN_DEVICE_REVIEW = "OWN_DEVICE_REVIEW"
    SUPPORT_CASE_CREATE = "SUPPORT_CASE_CREATE"
    OWN_CASE_STATUS = "OWN_CASE_STATUS"


class AgentEscalationReason(StrEnum):
    IDENTITY_PROOFING_FAILED = "IDENTITY_PROOFING_FAILED"
    VERIFIED_FACTOR_UNAVAILABLE = "VERIFIED_FACTOR_UNAVAILABLE"
    SUSPECTED_ACCOUNT_COMPROMISE = "SUSPECTED_ACCOUNT_COMPROMISE"
    PRIVILEGED_TARGET = "PRIVILEGED_TARGET"
    SELF_SERVICE_DEPENDENCY_UNAVAILABLE = "SELF_SERVICE_DEPENDENCY_UNAVAILABLE"
    POLICY_REQUIRES_HUMAN_APPROVAL = "POLICY_REQUIRES_HUMAN_APPROVAL"
    REPEATED_RECOVERY_FAILURE = "REPEATED_RECOVERY_FAILURE"
    OUT_OF_SCOPE_REQUEST = "OUT_OF_SCOPE_REQUEST"


SELF_SERVICE_ALLOWLIST: Final[frozenset[AgentWorkflow]] = frozenset(AgentWorkflow)
ESCALATION_REQUIRED: Final[frozenset[AgentEscalationReason]] = frozenset(AgentEscalationReason)

FORBIDDEN_AGENT_MATERIAL: Final[frozenset[str]] = frozenset({
    "password",
    "current_password",
    "new_password",
    "otp",
    "one_time_password",
    "recovery_token",
    "recovery_capability",
    "mfa_seed",
    "mfa_secret",
    "private_key",
    "session_token",
    "refresh_token",
})


class SystemServicesAgentPolicyError(ValueError):
    """Stable fail-closed rejection of an unlisted agent workflow or secret field."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def require_agent_workflow(value: object) -> AgentWorkflow:
    if not isinstance(value, AgentWorkflow) or value not in SELF_SERVICE_ALLOWLIST:
        raise SystemServicesAgentPolicyError("AGENT_WORKFLOW_NOT_ALLOWLISTED")
    return value


def require_human_escalation(value: object) -> AgentEscalationReason:
    if not isinstance(value, AgentEscalationReason) or value not in ESCALATION_REQUIRED:
        raise SystemServicesAgentPolicyError("AGENT_ESCALATION_REASON_INVALID")
    return value


def reject_secret_material(fields: object) -> None:
    if not isinstance(fields, (tuple, list, set, frozenset)):
        raise SystemServicesAgentPolicyError("AGENT_FIELD_SET_INVALID")
    normalized = {
        item.strip().lower()
        for item in fields
        if isinstance(item, str)
    }
    if len(normalized) != len(fields):
        raise SystemServicesAgentPolicyError("AGENT_FIELD_SET_INVALID")
    if normalized & FORBIDDEN_AGENT_MATERIAL:
        raise SystemServicesAgentPolicyError("AGENT_SECRET_MATERIAL_FORBIDDEN")


__all__ = [
    "VERSION", "AgentWorkflow", "AgentEscalationReason",
    "SELF_SERVICE_ALLOWLIST", "ESCALATION_REQUIRED",
    "FORBIDDEN_AGENT_MATERIAL", "SystemServicesAgentPolicyError",
    "require_agent_workflow", "require_human_escalation",
    "reject_secret_material",
]
