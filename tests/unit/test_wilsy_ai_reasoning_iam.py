"""TITLE: C1B reasoning IAM direct certificate.
VERSION: v1.0.0-C1B-R2
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Certify the dedicated reasoning permission and least privilege.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_reasoning_iam.py
CHANGELOG: v1.0.0-C1B-R2 certifies spelling, grants, denials, and closed unknowns.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
import pytest

from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP, get_roles_granting_permission
from tools.eos.auth.tenant_authority_policy import tenant_role_operation_eligibility


def test_reasoning_identity_and_metadata_are_exact() -> None:
    metadata = permission_metadata("wilsy_ai:reasoning:execute")
    assert metadata.namespace == "TENANT" and metadata.tenant_membership_required
    assert get_roles_granting_permission("wilsy_ai:reasoning:execute") == ("ENTERPRISE_ADMIN",)


def test_least_privilege_and_unknowns_deny() -> None:
    assert "wilsy_ai:reasoning:execute" in ROLE_PERMISSIONS_MAP["ENTERPRISE_ADMIN"]
    assert "wilsy_ai:reasoning:execute" not in ROLE_PERMISSIONS_MAP["AUDITOR"]
    assert tenant_role_operation_eligibility("tenant_owner", "wilsy_ai_reasoning_execute") == "ELIGIBLE"
    assert tenant_role_operation_eligibility("tenant_auditor", "wilsy_ai_reasoning_execute") == "DENY"
    assert tenant_role_operation_eligibility("tenant_owner", "unknown") == "DENY"
    with pytest.raises(ValueError):
        permission_metadata("unknown:reasoning")


# ARTIFACT: test_wilsy_ai_reasoning_iam.py
# VERSION: v1.0.0-C1B-R2
# END OF WILSY OS SOVEREIGN ARTIFACT
