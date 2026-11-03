"""Canonical EOS workspace contract.

The resolver converts an already-verified durable tenant business role into a
presentation workspace identifier. It grants no permission and performs no
resource authorization. Unknown roles fail closed rather than selecting a
browser default.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from tools.eos.auth.hr_business_role_catalog import ALL_HR_BUSINESS_ROLES

WORKSPACE_CONTRACT_VERSION: Final[str] = "v1.0.0-WILSY-EOS-WORKSPACE-CONTRACT"


class WorkspaceContractResolutionError(ValueError):
    """The current durable business role has no published workspace contract."""


@dataclass(frozen=True, slots=True)
class WorkspaceContract:
    """Bounded presentation contract derived from current EOS business-role truth."""

    version: str
    workspace_id: str


_ROLE_WORKSPACES: Final[dict[str, str]] = {
    "tenant_owner": "EXECUTIVE_COMMAND_CENTRE",
    "tenant_admin": "TENANT_ADMINISTRATION",
    "tenant_manager": "TENANT_OPERATIONS",
    "tenant_auditor": "AUDIT_REPORTING",
    "tenant_legal_partner": "LEGAL_PRACTICE",
    "tenant_legal_attorney": "LEGAL_PRACTICE",
    "tenant_legal_paralegal": "LEGAL_PRACTICE",
    "tenant_legal_secretary": "LEGAL_PRACTICE",
    "tenant_legal_finance": "LEGAL_FINANCE",
    "tenant_sheriff": "PROCESS_SERVICE",
    "tenant_deputy": "PROCESS_SERVICE",
    "tenant_legal_client": "CLIENT_PORTAL",
    "tenant_platform_billing_provider_policy_admin": "PLATFORM_OPERATIONS",
    "tenant_inbound_collection_authorization_admin": "PLATFORM_FINANCE_OPERATIONS",
    "tenant_inbound_merchant_configuration_admin": "PLATFORM_FINANCE_OPERATIONS",
    "tenant_inbound_provider_security_admin": "PLATFORM_SECURITY_OPERATIONS",
    "tenant_inbound_provider_policy_admin": "PLATFORM_SECURITY_OPERATIONS",
    "tenant_inbound_provider_policy_activation_admin": "PLATFORM_SECURITY_OPERATIONS",
}

# HR capacities share the HR workspace shell; every action inside it remains
# subject to the exact role/permission and employee-resource authorization.
for _role in ALL_HR_BUSINESS_ROLES:
    _ROLE_WORKSPACES[_role] = "HR_OPERATIONS"


def resolve_workspace_contract(business_role: str) -> WorkspaceContract:
    """Resolve one workspace from an exact canonical business-role identifier."""
    if not isinstance(business_role, str) or business_role != business_role.strip():
        raise WorkspaceContractResolutionError("WORKSPACE_ROLE_INVALID")
    workspace_id = _ROLE_WORKSPACES.get(business_role)
    if workspace_id is None:
        raise WorkspaceContractResolutionError("WORKSPACE_ROLE_UNMAPPED")
    return WorkspaceContract(
        version=WORKSPACE_CONTRACT_VERSION,
        workspace_id=workspace_id,
    )


__all__ = [
    "WORKSPACE_CONTRACT_VERSION",
    "WorkspaceContract",
    "WorkspaceContractResolutionError",
    "resolve_workspace_contract",
]
