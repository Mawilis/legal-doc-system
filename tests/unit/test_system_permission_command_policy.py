"""TITLE: D12 system permission command policy certificate.
VERSION: v1.3.0-L10A2R-C4D7-RECONCILIATION-READ-GOVERNED-DELEGATION-CERT
AUTHORITY: Direct closed-policy proof.
EPITOME: Prove the exact bootstrap mappings and three-permission ongoing SYSTEM delegation allowlists.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_system_permission_command_policy.py
COLLABORATION / OWNERSHIP: D12 command services and P7 lawful assignment prerequisite.
CERTIFICATION DATE: 2026-10-15
CHANGELOG: v1.3.0-L10A2R-C4D7-RECONCILIATION-READ-GOVERNED-DELEGATION-CERT certifies exact reconciliation-read assignment/revocation eligibility while proving command permissions, arbitrary SYSTEM permissions, wildcard, tenant, and financial permissions remain denied.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Pure immutable policy assertions; no identity data.
TENANT BOUNDARY: SYSTEM only; tenant permissions reject.
AUTHORITY BOUNDARY: No authority grant, wildcard, recursion, tenant, or finance.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively executes finance.
"""
from types import MappingProxyType
from json import loads
import pytest
from tools.eos.auth.system_permission_command_policy import *
from tools.eos.auth.permission_namespace import canonical_permissions


def test_exact_bootstrap_mappings_and_immutable_policy() -> None:
    assert isinstance(BOOTSTRAP_PERMISSION_BY_PURPOSE, MappingProxyType)
    assert bootstrap_seed_permission(ASSIGN_BOOTSTRAP_PURPOSE) == ASSIGN_COMMAND_PERMISSION
    assert bootstrap_seed_permission(REVOKE_BOOTSTRAP_PURPOSE) == REVOKE_COMMAND_PERMISSION
    require_bootstrap_seed(ASSIGN_BOOTSTRAP_PURPOSE, ASSIGN_COMMAND_PERMISSION)
    require_bootstrap_seed(REVOKE_BOOTSTRAP_PURPOSE, REVOKE_COMMAND_PERMISSION)


def test_exact_ongoing_sets_exclude_recursive_command_authority() -> None:
    exact = frozenset({PRIVILEGED_ACTIVATION_ISSUE_PERMISSION, "privileged_activation:break_glass", LEGAL_EVIDENCE_PROVIDER_RECONCILIATION_READ_PERMISSION})
    assert ONGOING_ASSIGNABLE_PERMISSIONS == exact
    assert ONGOING_REVOCABLE_PERMISSIONS == exact
    for permission in exact:
        require_ongoing_assignment(permission)
        require_ongoing_revocation(permission)
    system_permissions = {row["permission_id"] for row in loads(canonical_permissions()) if row["scope_kind"] == "SYSTEM"}
    assert exact < system_permissions
    for denied in system_permissions - exact:
        with pytest.raises(SystemPermissionCommandPolicyError):
            require_ongoing_assignment(denied)
        with pytest.raises(SystemPermissionCommandPolicyError):
            require_ongoing_revocation(denied)



def test_reconciliation_read_is_explicitly_delegable_but_not_command_authority() -> None:
    permission = LEGAL_EVIDENCE_PROVIDER_RECONCILIATION_READ_PERMISSION
    assert permission in ONGOING_ASSIGNABLE_PERMISSIONS
    assert permission in ONGOING_REVOCABLE_PERMISSIONS
    require_ongoing_assignment(permission)
    require_ongoing_revocation(permission)
    assert ASSIGN_COMMAND_PERMISSION not in ONGOING_ASSIGNABLE_PERMISSIONS
    assert REVOKE_COMMAND_PERMISSION not in ONGOING_ASSIGNABLE_PERMISSIONS
    assert ASSIGN_COMMAND_PERMISSION not in ONGOING_REVOCABLE_PERMISSIONS
    assert REVOKE_COMMAND_PERMISSION not in ONGOING_REVOCABLE_PERMISSIONS

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
# VERSION: v1.3.0-L10A2R-C4D7-RECONCILIATION-READ-GOVERNED-DELEGATION-CERT
# AUTHORITY BOUNDARY: POLICY CERTIFICATE ONLY
# TENANT POSTURE: SYSTEM ONLY; TENANT PERMISSIONS REJECT
# FAIL-CLOSED POSTURE: EXACT THREE-PERMISSION ALLOWLIST; NO WILDCARD OR RECURSION
# FINANCIAL EXECUTION AUTHORITY: KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
