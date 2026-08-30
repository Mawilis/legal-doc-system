"""TITLE: WILSY OS Permission Namespace Canon Certification.
VERSION: v1.0.0-PERMISSION-NAMESPACE-CERT
AUTHORITY: Certification of immutable permission vocabulary semantics only.
EPITOME: Proves bounded namespaces, fail-closed metadata, and deterministic policy bytes.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_permission_namespace.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.0 certifies permission scope, legacy disposition, service separation, and financial exclusion.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: No credentials, JWTs, Node projections, persistence, or financial execution are processed.
TENANT BOUNDARY: Tenant metadata does not prove membership.
AUTHORITY BOUNDARY: Tests policy metadata, not assignment or authorization.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""
import json

import pytest

from tools.eos.auth.permission_namespace import PermissionDisposition, canonical_permissions, classify_legacy_permission, permission_metadata


def test_permission_canon_properties():
    rows = json.loads(canonical_permissions())
    assert len(rows) == 11
    assert {row["namespace"] for row in rows} <= {"SYSTEM", "TENANT", "SERVICE"}
    assert all(row["authorizes_by_itself"] is False for row in rows)
    assert all(row["financial_execution_capable"] is False for row in rows)
    assert permission_metadata("audit:read").namespace == "TENANT"
    assert permission_metadata("audit:read").tenant_membership_required is True
    assert permission_metadata("audit:read").cross_tenant_capable is False
    assert permission_metadata("execution:trigger").disposition is PermissionDisposition.BLOCKED_AMBIGUOUS
    assert permission_metadata("execution:trigger").financial_execution_capable is False
    assert permission_metadata("admin:all").disposition is PermissionDisposition.LEGACY_ONLY
    assert permission_metadata("admin:all").cross_tenant_capable is False
    assert permission_metadata("tenant:manage").disposition is PermissionDisposition.BLOCKED_AMBIGUOUS
    assert permission_metadata("artifacts:write").namespace == "SERVICE"
    assert permission_metadata("events:publish").namespace == "SERVICE"
    assert permission_metadata("kernel:read").system_assignment_required is True
    assert permission_metadata("kernel:write").tenant_membership_required is False
    assert permission_metadata("artifacts:read").tenant_membership_required is True
    assert permission_metadata("governance:read").namespace == "SYSTEM"
    assert permission_metadata("admin:all").authorizes_by_itself is False
    assert classify_legacy_permission("admin:all") is PermissionDisposition.LEGACY_ONLY
    assert classify_legacy_permission("execution:trigger") is PermissionDisposition.BLOCKED_AMBIGUOUS
    assert classify_legacy_permission("tenant:manage") is PermissionDisposition.BLOCKED_AMBIGUOUS
    assert classify_legacy_permission("unknown") is None
    assert classify_legacy_permission(" admin:all ") is None
    assert classify_legacy_permission(None) is None
    assert canonical_permissions() == canonical_permissions()
    assert isinstance(canonical_permissions(), bytes)
    with pytest.raises(ValueError):
        permission_metadata("unknown")
    with pytest.raises(ValueError):
        permission_metadata(" ")
    with pytest.raises((AttributeError, TypeError)):
        permission_metadata("audit:read").permission_id = "x"  # type: ignore[misc]
    assert permission_metadata("execution:trigger").business_capability != "financial execution"
    assert permission_metadata("admin:all").deprecated_or_legacy is True


def test_no_domain_profile_permissions():
    assert all(permission_metadata(row["permission_id"]).namespace not in {"DOMAIN", "PROFILE"} for row in json.loads(canonical_permissions()))


# ARTIFACT: test_permission_namespace.py
# VERSION: v1.0.0-PERMISSION-NAMESPACE-CERT
# AUTHORITY BOUNDARY: permission semantic certification only
# TENANT POSTURE: membership remains separately governed
# FAIL-CLOSED POSTURE: unknown and malformed values deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
