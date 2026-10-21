"""WILSY P9-R103R8 Partner-only practitioner issuer IAM certificate.
VERSION: v1.0.0-P9-R103R8-ISSUER-IAM-RED
ABSOLUTE CANONICAL PATH: tests/unit/test_legal_practitioner_matter_access_issuer_iam.py
AUTHORITY: Static policy and operation binding only, no access grant.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG: Dedicated least-authority issuer tests.
"""
import pytest
from tools.eos.auth.permission_namespace import permission_metadata,PermissionDisposition
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP,get_roles_granting_permission
from tools.eos.auth.tenant_authority_policy import (
 ELIGIBLE,DENY,TENANT_ROLES,OPERATIONS,
 tenant_role_operation_eligibility,permission_for_business_role_operation,
 requires_system_authority,SystemAuthorityClassification,
)
from tools.eos.auth.tenant_authorization import _BINDINGS
P="legal_operations:practitioner_matter_access_policy:issue"
O="legal_practitioner_matter_access_policy_issue"

def test_exact_canonical_permission():
 m=permission_metadata(P)
 assert m.disposition is PermissionDisposition.CANONICAL
 assert m.namespace=="TENANT" and m.scope_kind=="TENANT"
 assert m.tenant_membership_required is True
 assert m.cross_tenant_capable is False
 assert m.financial_execution_capable is False
 assert m.authorizes_by_itself is False

def test_partner_only_static_permission():
 assert get_roles_granting_permission(P)==("LEGAL_PARTNER",)
 for role,grants in ROLE_PERMISSIONS_MAP.items():
  assert grants.count(P)==(1 if role=="LEGAL_PARTNER" else 0)

def test_partner_only_business_eligibility():
 assert O in OPERATIONS
 for role in TENANT_ROLES:
  assert tenant_role_operation_eligibility(role,O)==(
   ELIGIBLE if role=="tenant_legal_partner" else DENY
  )

def test_exact_operation_pair():
 assert permission_for_business_role_operation(O)==P
 assert _BINDINGS[O]==P

def test_reassignment_separation():
 assert _BINDINGS["legal_work_item_reassign"]!=P

def test_no_system_shortcut():
 assert requires_system_authority(O) is SystemAuthorityClassification.SYSTEM_NOT_INHERENTLY_REQUIRED

@pytest.mark.parametrize("bad",[O.upper()," "+O,O+" ",O+"_override"])
def test_alias_denied(bad):
 assert tenant_role_operation_eligibility("tenant_legal_partner",bad)==DENY
 assert _BINDINGS.get(bad) is None

# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_matter_access_issuer_iam.py
# VERSION: v1.0.0-P9-R103R8-ISSUER-IAM-RED
# END OF WILSY OS SOVEREIGN ARTIFACT
