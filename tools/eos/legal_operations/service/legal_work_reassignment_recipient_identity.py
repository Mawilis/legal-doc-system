"""TITLE: WILSY OS P9 Pure Reassignment Recipient Identity Preflight.
VERSION: v1.0.0-P9-R68-RECIPIENT-IDENTITY-GREEN
AUTHORITY: Python EOS Legal Operations snapshot consistency only.
EPITOME: Verify exact principal and tenant-membership snapshot identities
    and ACTIVE states without assuming currentness or execution authority.
ABSOLUTE CANONICAL PATH:
    tools/eos/legal_operations/service/legal_work_reassignment_recipient_identity.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.0-P9-R68-RECIPIENT-IDENTITY-GREEN
    Establishes deterministic fail-closed supplied-snapshot consistency.
TENANT BOUNDARY: Exact non-pseudo tenant and recipient principal identity.
AUTHORITY BOUNDARY:
    Caller-supplied snapshots do not prove repository provenance, currentness,
    IAM authorization, professional qualification, operating-role authority,
    matter access, confidentiality clearance, supervision approval, or
    authorization to execute or persist reassignment.
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from typing import Final, NoReturn

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)

VERSION: Final[str] = "v1.0.0-P9-R68-RECIPIENT-IDENTITY-GREEN"

_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "root", "*"}
)


class LegalWorkReassignmentRecipientIdentityError(ValueError):
    """Stable fail-closed supplied-snapshot consistency error."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _fail(code: str) -> NoReturn:
    raise LegalWorkReassignmentRecipientIdentityError(code)


def validate_legal_work_reassignment_recipient_identity(
    *,
    tenant_id: str,
    recipient_principal_id: str,
    principal_authority: object,
    membership_authority: object,
) -> tuple[PrincipalAuthority, TenantMembershipAuthority]:
    """Return unchanged, matching ACTIVE snapshots; grant no authority.

    The caller must resolve both snapshots from authoritative repositories
    under the required transaction, validate their currentness separately,
    and establish all other recipient and matter authorization gates.
    """
    if (
        type(tenant_id) is not str
        or not tenant_id
        or tenant_id != tenant_id.strip()
        or tenant_id.casefold() in _FORBIDDEN_TENANTS
    ):
        _fail("P9_R68_TENANT_ID_INVALID")

    if (
        type(recipient_principal_id) is not str
        or not recipient_principal_id
        or recipient_principal_id != recipient_principal_id.strip()
    ):
        _fail("P9_R68_RECIPIENT_ID_INVALID")

    if type(principal_authority) is not PrincipalAuthority:
        _fail("P9_R68_PRINCIPAL_SNAPSHOT_INVALID")

    if type(membership_authority) is not TenantMembershipAuthority:
        _fail("P9_R68_MEMBERSHIP_SNAPSHOT_INVALID")

    if principal_authority.principal_id != recipient_principal_id:
        _fail("P9_R68_PRINCIPAL_IDENTITY_MISMATCH")

    if membership_authority.principal_id != recipient_principal_id:
        _fail("P9_R68_MEMBERSHIP_PRINCIPAL_MISMATCH")

    if membership_authority.tenant_id != tenant_id:
        _fail("P9_R68_MEMBERSHIP_TENANT_MISMATCH")

    if principal_authority.status is not PrincipalStatus.ACTIVE:
        _fail("P9_R68_PRINCIPAL_NOT_ACTIVE")

    if membership_authority.status is not TenantMembershipStatus.ACTIVE:
        _fail("P9_R68_MEMBERSHIP_NOT_ACTIVE")

    return principal_authority, membership_authority


__all__ = [
    "VERSION",
    "LegalWorkReassignmentRecipientIdentityError",
    "validate_legal_work_reassignment_recipient_identity",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_work_reassignment_recipient_identity.py
# VERSION: v1.0.0-P9-R68-RECIPIENT-IDENTITY-GREEN
# AUTHORITY BOUNDARY: supplied snapshot consistency only
# CURRENTNESS / IAM / MATTER / APPROVAL AUTHORITY: NOT GRANTED
# REASSIGNMENT EXECUTION / PERSISTENCE: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
