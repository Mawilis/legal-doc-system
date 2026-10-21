"""TITLE: WILSY OS P9 Legal Reassignment Recipient Identity RED Certificate.
VERSION: v1.0.0-P9-R67-RECIPIENT-IDENTITY-RED
AUTHORITY: Test-only snapshot consistency preflight, never admission.
EPITOME: Match canonical principal and tenant-membership snapshots exactly.
ABSOLUTE CANONICAL PATH:
    tests/unit/test_legal_work_reassignment_recipient_identity.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.0-P9-R67-RECIPIENT-IDENTITY-RED
    Freeze snapshot checks without asserting repository provenance.
TENANT BOUNDARY: Exact recipient-principal and tenant identity.
AUTHORITY BOUNDARY: A supplied snapshot is not certified current.
    No IAM, qualification, matter access, approval, persistence or execution.
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from importlib import import_module

import pytest

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)


def _principal(
    status: PrincipalStatus = PrincipalStatus.ACTIVE,
    *,
    principal_id: str = "recipient-1",
    revision: int = 0,
) -> PrincipalAuthority:
    return PrincipalAuthority(
        principal_id=principal_id,
        status=status,
        revision=revision,
    )


def _membership(
    status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    *,
    principal_id: str = "recipient-1",
    tenant_id: str = "tenant-1",
    revision: int = 0,
) -> TenantMembershipAuthority:
    return TenantMembershipAuthority(
        principal_id=principal_id,
        tenant_id=tenant_id,
        status=status,
        revision=revision,
    )


def _check(
    *,
    tenant_id: str = "tenant-1",
    recipient_principal_id: str = "recipient-1",
    principal_authority: object = None,
    membership_authority: object = None,
) -> object:
    module = import_module(
        "tools.eos.legal_operations.service."
        "legal_work_reassignment_recipient_identity"
    )
    return module.validate_legal_work_reassignment_recipient_identity(
        tenant_id=tenant_id,
        recipient_principal_id=recipient_principal_id,
        principal_authority=principal_authority,
        membership_authority=membership_authority,
    )


@pytest.mark.parametrize("revision", (0, 5))
def test_matching_active_snapshots_preserve_both_facts(
    revision: int,
) -> None:
    principal = _principal(revision=revision)
    membership = _membership(revision=revision)
    result = _check(
        principal_authority=principal,
        membership_authority=membership,
    )
    assert result[0] is principal
    assert result[1] is membership


@pytest.mark.parametrize(
    "status",
    (PrincipalStatus.SUSPENDED, PrincipalStatus.REVOKED),
)
def test_inactive_principal_rejected(status: PrincipalStatus) -> None:
    with pytest.raises(ValueError):
        _check(
            principal_authority=_principal(status),
            membership_authority=_membership(),
        )


@pytest.mark.parametrize(
    "status",
    (TenantMembershipStatus.SUSPENDED, TenantMembershipStatus.REVOKED),
)
def test_inactive_membership_rejected(
    status: TenantMembershipStatus,
) -> None:
    with pytest.raises(ValueError):
        _check(
            principal_authority=_principal(),
            membership_authority=_membership(status),
        )


def test_membership_principal_mismatch_rejected() -> None:
    with pytest.raises(ValueError):
        _check(
            principal_authority=_principal(),
            membership_authority=_membership(principal_id="someone-else"),
        )


def test_foreign_tenant_membership_rejected() -> None:
    with pytest.raises(ValueError):
        _check(
            principal_authority=_principal(),
            membership_authority=_membership(tenant_id="tenant-foreign"),
        )


def test_requested_recipient_identity_mismatch_rejected() -> None:
    with pytest.raises(ValueError):
        _check(
            recipient_principal_id="someone-else",
            principal_authority=_principal(),
            membership_authority=_membership(),
        )


def test_missing_principal_snapshot_rejected() -> None:
    with pytest.raises(ValueError):
        _check(
            principal_authority=None,
            membership_authority=_membership(),
        )


def test_missing_membership_snapshot_rejected() -> None:
    with pytest.raises(ValueError):
        _check(
            principal_authority=_principal(),
            membership_authority=None,
        )


def test_preflight_has_no_admission_or_execution_interface() -> None:
    module = import_module(
        "tools.eos.legal_operations.service."
        "legal_work_reassignment_recipient_identity"
    )
    for name in (
        "authorize_reassignment",
        "execute_reassignment",
        "persist_reassignment",
        "grant_matter_access",
        "approve_reassignment",
        "issue_authorization",
    ):
        assert not hasattr(module, name)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_work_reassignment_recipient_identity.py
# VERSION: v1.0.0-P9-R67-RECIPIENT-IDENTITY-RED
# AUTHORITY BOUNDARY: supplied snapshot consistency only
# AUTHORITATIVE CURRENTNESS / RECIPIENT ADMISSION: NOT PROVEN
# REASSIGNMENT EXECUTION / PERSISTENCE: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
