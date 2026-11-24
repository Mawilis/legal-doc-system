"""TITLE: WILSY OS Practitioner Binding Read Permission Certificate.
VERSION: v1.0.3-P12C-R4N-PERMISSION-NAMESPACE-CURRENTNESS-CERT
AUTHORITY: Canonical permission vocabulary and historical integrity only.
EPITOME: Verify binding-read metadata without manufacturing role authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_practitioner_matter_binding_read_permission.py
COLLABORATION / OWNERSHIP: Certifies canonical permission namespace metadata and role-map evidence only.
CERTIFICATION / UPDATE DATE: 2026-11-11
CHANGELOG: v1.0.3-P12C-R4N-PERMISSION-NAMESPACE-CURRENTNESS-CERT adds the missing canonical path and confirms exact tenant and financial authority boundaries; test behavior is unchanged.
           v1.0.2-P12C-R4N-PERMISSION-NAMESPACE-CURRENTNESS-CERT records the verified sovereign metadata correction; test and production behavior are unchanged.
           v1.0.1-P12C-R4N-PERMISSION-NAMESPACE-CURRENTNESS-CERT checks the canonical permission namespace's current version while retaining the historical R4N/P4C9 changelog and exact read-permission contract.
           v1.0.0 established test-first regression and provenance certification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic permission metadata only; no matter content is read or disclosed.
TENANT BOUNDARY: Exact own-tenant membership is required.
AUTHORITY BOUNDARY: Vocabulary is not role possession or matter access.
FINANCIAL AUTHORITY BOUNDARY: No financial execution authority.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.eos.auth.permission_namespace import (
    PermissionDisposition,
    VERSION,
    canonical_permissions,
    permission_metadata,
)
from tools.eos.auth.roles import (
    ROLE_PERMISSIONS_MAP,
    get_roles_granting_permission,
)

READ = "legal_operations:practitioner_matter_binding:read"
PROVISION = "legal_operations:practitioner_matter_binding:provision"
EXPECTED_VERSION = (
    "v1.51.0-P12C-R4N-P4C9-PRACTITIONER-BINDING-READ-PERMISSION"
)
PREVIOUS_VERSION = (
    "v1.50.0-P9-R103-PRACTITIONER-POLICY-ISSUER-PERMISSION"
)


def test_exact_canonical_read_permission() -> None:
    metadata = permission_metadata(READ)

    assert VERSION == "v1.59.0-INSTITUTIONAL-OFFER-SIGNATURE-AUTHORITY"
    assert metadata.permission_id == READ
    assert metadata.disposition is PermissionDisposition.CANONICAL
    assert metadata.namespace == "TENANT"
    assert metadata.scope_kind == "TENANT"
    assert metadata.tenant_membership_required is True
    assert metadata.system_assignment_required is False
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False
    assert metadata.business_capability == (
        "read exact own-tenant practitioner matter binding current "
        "state and immutable history without matter content access, "
        "provisioning, ethical-wall clearance or financial authority"
    )
    assert READ != PROVISION
    assert canonical_permissions().count(
        ('"permission_id":"' + READ + '"').encode("ascii")
    ) == 1


def test_permission_registration_grants_no_roles() -> None:
    assert get_roles_granting_permission(READ) == ()
    for role, grants in ROLE_PERMISSIONS_MAP.items():
        assert READ not in grants, role


@pytest.mark.parametrize(
    "alias",
    (
        READ + " ",
        " " + READ,
        READ.upper(),
        "legal_operations:practitioner_matter_binding:*",
        "legal_operations:practitioner_matter_binding:reads",
        "practitioner_matter_binding:read",
    ),
)
def test_read_aliases_fail_closed(alias: str) -> None:
    with pytest.raises(ValueError, match="UNKNOWN_PERMISSION"):
        permission_metadata(alias)


def test_historical_changelog_is_preserved() -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "tools/eos/auth/permission_namespace.py"
    )
    content = path.read_text(encoding="utf-8")
    changelog = content.split("CHANGELOG:", 1)[1].split(
        "COMPLIANCE:", 1
    )[0]

    assert (
        "2026-10-20 " + EXPECTED_VERSION
    ) in changelog
    assert (
        "2026-10-19 " + PREVIOUS_VERSION
    ) in changelog
    assert changelog.count(EXPECTED_VERSION) == 1


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_matter_binding_read_permission.py
# VERSION: v1.0.3-P12C-R4N-PERMISSION-NAMESPACE-CURRENTNESS-CERT
# AUTHORITY: Permission vocabulary regression only
# ROLE GRANTS: NONE
# CONTENT ACCESS: NONE
# FINANCIAL EXECUTION: NONE
# AUTHORITY BOUNDARY: Permission vocabulary regression only; no role possession or matter access
# TENANT POSTURE: Exact own-tenant membership is required independently
# FAIL-CLOSED POSTURE: Unknown, absent, or noncanonical permission metadata rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
