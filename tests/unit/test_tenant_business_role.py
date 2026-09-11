"""TITLE: WILSY OS Tenant Business-Role Authority Certificate.
VERSION: v1.0.0-TENANT-BUSINESS-ROLE-AUTHORITY-CERT
AUTHORITY: Pure value-contract certification only.
EPITOME: Certifies immutable, explicit, scope-bound business-role evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_business_role.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-05.
CHANGELOG: v1.0.0 certifies the initial business-role authority value contract.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY/PRIVACY POSTURE: No persistence, credentials, network, or fabricated authority.
TENANT BOUNDARY: Explicit principal and tenant identifiers are retained exactly.
AUTHORITY BOUNDARY: Certification does not grant authorization or execution capability.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import pytest

from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus

STAMP = datetime(2026, 9, 1, tzinfo=timezone.utc)


def make(**overrides: object) -> TenantBusinessRoleAuthority:
    values: dict[str, object] = {"principal_id": "principal-1", "tenant_id": "tenant-1", "business_role": "tenant_owner", "status": TenantBusinessRoleStatus.ACTIVE, "revision": 0, "effective_at": STAMP, "revoked_at": None}
    values.update(overrides)
    return TenantBusinessRoleAuthority(**cast(dict[str, Any], values))


@pytest.mark.parametrize("role", ("tenant_owner", "tenant_admin", "tenant_manager", "tenant_auditor"))
def test_all_canonical_business_roles_are_retained(role: str) -> None:
    value = make(business_role=role)
    assert (value.principal_id, value.tenant_id, value.business_role, value.status, value.revision, value.effective_at, value.revoked_at) == ("principal-1", "tenant-1", role, TenantBusinessRoleStatus.ACTIVE, 0, STAMP, None)


def test_valid_revoked_authority() -> None:
    revoked = STAMP + timedelta(seconds=1)
    assert make(status=TenantBusinessRoleStatus.REVOKED, revision=2, revoked_at=revoked).revoked_at == revoked


@pytest.mark.parametrize("field", ("principal_id", "tenant_id"))
@pytest.mark.parametrize("value", ("", " ", "\t"))
def test_invalid_identifiers_reject(field: str, value: str) -> None:
    with pytest.raises(ValueError):
        make(**{field: value})


@pytest.mark.parametrize("role", ("ENTERPRISE_ADMIN", "AUDITOR", "owner", "unknown_role"))
def test_authorization_roles_and_unknown_roles_reject(role: str) -> None:
    with pytest.raises(ValueError):
        make(business_role=role)


@pytest.mark.parametrize("revision", (-1, True))
def test_invalid_revision_rejects(revision: object) -> None:
    with pytest.raises(ValueError):
        make(revision=revision)


def test_positive_revision_is_valid() -> None:
    assert make(revision=4).revision == 4


def test_naive_timestamps_reject() -> None:
    with pytest.raises(ValueError):
        make(effective_at=datetime(2026, 9, 1))
    with pytest.raises(ValueError):
        make(status=TenantBusinessRoleStatus.REVOKED, revoked_at=datetime(2026, 9, 2))


def test_lifecycle_contradictions_reject() -> None:
    with pytest.raises(ValueError):
        make(revoked_at=STAMP)
    with pytest.raises(ValueError):
        make(status=TenantBusinessRoleStatus.REVOKED)
    with pytest.raises(ValueError):
        make(status=TenantBusinessRoleStatus.REVOKED, revoked_at=STAMP - timedelta(seconds=1))


def test_value_is_immutable_and_has_slots() -> None:
    value = make()
    with pytest.raises((AttributeError, TypeError)):
        cast(Any, value).tenant_id = "other"
    with pytest.raises(AttributeError):
        cast(Any, value).extra = "forbidden"
    assert not hasattr(value, "__dict__")


def test_no_authorization_or_execution_methods() -> None:
    forbidden = {"authorize", "can", "has_permission", "execute", "dispatch", "persist", "pay", "settle"}
    assert forbidden.isdisjoint(dir(TenantBusinessRoleAuthority))


# ARTIFACT: test_tenant_business_role.py
# VERSION: v1.0.0-TENANT-BUSINESS-ROLE-AUTHORITY-CERT
# AUTHORITY BOUNDARY: pure value-contract certification only; no authority grant
# TENANT POSTURE: explicit principal/tenant scope and canonical business-role values
# FAIL-CLOSED POSTURE: malformed identifiers, roles, revisions, timestamps, and lifecycle states reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
