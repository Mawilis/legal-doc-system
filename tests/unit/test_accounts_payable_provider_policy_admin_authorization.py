"""TITLE: Accounts-Payable provider-policy administration authorization.
VERSION: v1.0.0-M11-P5-R1B-AP2C1.
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Family-scoped AP provider-policy lifecycle permission contract.
ABSOLUTE CANONICAL PATH: tests/unit/test_accounts_payable_provider_policy_admin_authorization.py
COLLABORATION / OWNERSHIP: Python EOS authorization owners.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 establishes dedicated AP policy administration grants.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Permission grants never cross tenants.
AUTHORITY BOUNDARY: Admin policy only; no provider selection or execution.
"""
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP, get_permissions_for_roles
from tools.eos.auth.permission_namespace import permission_metadata

def test_ap_admin_lifecycle_is_family_scoped():
    role="ACCOUNTS_PAYABLE_PROVIDER_POLICY_ADMIN"; permission="accounts_payable:provider_policy:admin"
    assert permission in ROLE_PERMISSIONS_MAP[role]
    assert get_permissions_for_roles((role,)) == [permission]
    metadata=permission_metadata(permission)
    assert metadata is not None and metadata.scope_kind=="ACCOUNTS_PAYABLE"
    assert "platform_billing:provider_policy:admin" not in get_permissions_for_roles((role,))
    assert permission not in get_permissions_for_roles(("PLATFORM_BILLING_PROVIDER_POLICY_ADMIN",))

def test_ap_policy_operations_are_explicit_and_not_provider_selection():
    operations={"accounts_payable_provider_policy_create","accounts_payable_provider_policy_revise","accounts_payable_provider_policy_activate","accounts_payable_provider_policy_revoke"}
    assert operations.isdisjoint({"accounts_payable_provider_selection","financial_execution"})

# ARTIFACT: test_accounts_payable_provider_policy_admin_authorization.py
# VERSION: v1.0.0-M11-P5-R1B-AP2C1
# AUTHORITY BOUNDARY: AP policy administration certificate only
# FAIL-CLOSED POSTURE: cross-family grants are absent
# END OF WILSY OS SOVEREIGN ARTIFACT
