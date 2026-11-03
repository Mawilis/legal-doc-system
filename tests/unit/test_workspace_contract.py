from __future__ import annotations

import pytest

from tools.eos.auth.workspace_contract import (
    WORKSPACE_CONTRACT_VERSION,
    WorkspaceContractResolutionError,
    resolve_workspace_contract,
)


@pytest.mark.parametrize(
    ("business_role", "workspace_id"),
    [
        ("tenant_owner", "EXECUTIVE_COMMAND_CENTRE"),
        ("tenant_admin", "TENANT_ADMINISTRATION"),
        ("tenant_manager", "TENANT_OPERATIONS"),
        ("tenant_auditor", "AUDIT_REPORTING"),
        ("tenant_legal_partner", "LEGAL_PRACTICE"),
        ("tenant_legal_attorney", "LEGAL_PRACTICE"),
        ("tenant_legal_paralegal", "LEGAL_PRACTICE"),
        ("tenant_legal_secretary", "LEGAL_PRACTICE"),
        ("tenant_legal_finance", "LEGAL_FINANCE"),
        ("tenant_sheriff", "PROCESS_SERVICE"),
        ("tenant_deputy", "PROCESS_SERVICE"),
        ("tenant_legal_client", "CLIENT_PORTAL"),
    ],
)
def test_published_business_roles_resolve_to_canonical_workspaces(
    business_role: str,
    workspace_id: str,
) -> None:
    contract = resolve_workspace_contract(business_role)

    assert contract.version == WORKSPACE_CONTRACT_VERSION
    assert contract.workspace_id == workspace_id


@pytest.mark.parametrize("business_role", ["", " tenant_owner", "SUPER_ADMIN", "owner", None])
def test_unknown_or_malformed_roles_fail_closed(business_role: object) -> None:
    with pytest.raises(WorkspaceContractResolutionError):
        resolve_workspace_contract(business_role)  # type: ignore[arg-type]
