"""TITLE: D12 system permission command policy certificate.
VERSION: v1.0.0-D12-COMMAND-POLICY-CERT
AUTHORITY: Direct closed-policy proof.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_system_permission_command_policy.py
CERTIFICATION DATE: 2026-10-14
CHANGELOG: v1.0.0 certifies exact seed and ongoing sets.
BOUNDARY: No authority grant, wildcard, recursion, tenant, or finance.
"""
from types import MappingProxyType
import pytest
from tools.eos.auth.system_permission_command_policy import *


def test_exact_bootstrap_mappings_and_immutable_policy() -> None:
    assert isinstance(BOOTSTRAP_PERMISSION_BY_PURPOSE, MappingProxyType)
    assert bootstrap_seed_permission(ASSIGN_BOOTSTRAP_PURPOSE) == ASSIGN_COMMAND_PERMISSION
    assert bootstrap_seed_permission(REVOKE_BOOTSTRAP_PURPOSE) == REVOKE_COMMAND_PERMISSION
    require_bootstrap_seed(ASSIGN_BOOTSTRAP_PURPOSE, ASSIGN_COMMAND_PERMISSION)
    require_bootstrap_seed(REVOKE_BOOTSTRAP_PURPOSE, REVOKE_COMMAND_PERMISSION)


def test_exact_ongoing_sets_exclude_recursive_command_authority() -> None:
    assert ONGOING_ASSIGNABLE_PERMISSIONS == frozenset({PRIVILEGED_ACTIVATION_ISSUE_PERMISSION})
    assert ONGOING_REVOCABLE_PERMISSIONS == frozenset({PRIVILEGED_ACTIVATION_ISSUE_PERMISSION})
    require_ongoing_assignment(PRIVILEGED_ACTIVATION_ISSUE_PERMISSION)
    require_ongoing_revocation(PRIVILEGED_ACTIVATION_ISSUE_PERMISSION)
    for denied in (ASSIGN_COMMAND_PERMISSION, REVOKE_COMMAND_PERMISSION):
        with pytest.raises(SystemPermissionCommandPolicyError):
            require_ongoing_assignment(denied)
        with pytest.raises(SystemPermissionCommandPolicyError):
            require_ongoing_revocation(denied)


@pytest.mark.parametrize("denied", ["unknown", "*", "privileged_activation:*", " privileged_activation:issue", "Privileged_activation:issue", "tenant:profile:write", "financial:execute", "governance:evaluate", "kernel:write"])
def test_arbitrary_alias_wildcard_tenant_financial_governance_kernel_denied(denied: str) -> None:
    with pytest.raises(SystemPermissionCommandPolicyError):
        require_ongoing_assignment(denied)
    with pytest.raises(SystemPermissionCommandPolicyError):
        require_ongoing_revocation(denied)


def test_bootstrap_mismatch_denied() -> None:
    with pytest.raises(SystemPermissionCommandPolicyError, match="BOOTSTRAP_SEED_PERMISSION_MISMATCH"):
        require_bootstrap_seed(ASSIGN_BOOTSTRAP_PURPOSE, REVOKE_COMMAND_PERMISSION)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_system_permission_command_policy.py
# VERSION: v1.0.0-D12-COMMAND-POLICY-CERT
# AUTHORITY BOUNDARY: POLICY CERTIFICATE ONLY
# END OF WILSY OS SOVEREIGN ARTIFACT
