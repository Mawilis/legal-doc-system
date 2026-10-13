"""Pure workforce-currentness admission policy.

VERSION: v1.0.0-W3D-R8A-WORKFORCE-ADMISSION-POLICY

AUTHORITY BOUNDARY:
This module evaluates one explicit permission prerequisite against already
derived tenant-principal workforce currentness.  It does not read persistence,
open transactions, resolve IAM assignments, authorize an operation, grant a
permission, infer workforce status from role names, or create financial
authority.

SEMANTIC LOCK:
WORKFORCE ADMISSION != AUTHORIZATION.
"""

from __future__ import annotations

from enum import StrEnum

from tools.eos.auth.permission_namespace import PermissionMetadata
from tools.eos.auth.workforce_authorization_currentness import (
    TenantPrincipalWorkforceCurrentness,
)


VERSION = "v1.0.0-W3D-R8A-WORKFORCE-ADMISSION-POLICY"


class WorkforceAdmissionDisposition(StrEnum):
    """Closed workforce-prerequisite evaluation vocabulary."""

    NOT_REQUIRED = "NOT_REQUIRED"
    SATISFIED = "SATISFIED"
    NOT_CURRENT = "NOT_CURRENT"


class WorkforceAdmissionPolicyError(ValueError):
    """Raised when admission inputs cannot be trusted."""


def evaluate_workforce_admission(
    metadata: PermissionMetadata,
    currentness: TenantPrincipalWorkforceCurrentness | None,
) -> WorkforceAdmissionDisposition:
    """Evaluate workforce prerequisite only; never authorize.

    Non-workforce permissions skip workforce currentness completely.

    A workforce-required permission is satisfied only when the supplied exact
    tenant-principal projection contains at least one currently active canonical
    workforce relationship.  Relationship type does not itself grant business
    role or permission authority.
    """

    if not isinstance(
        metadata,
        PermissionMetadata,
    ):
        raise WorkforceAdmissionPolicyError(
            "PERMISSION_METADATA_INVALID"
        )

    if (
        metadata.workforce_currentness_required
        is not True
    ):
        if currentness is not None:
            raise WorkforceAdmissionPolicyError(
                "UNEXPECTED_WORKFORCE_CURRENTNESS"
            )

        return (
            WorkforceAdmissionDisposition.NOT_REQUIRED
        )

    if not isinstance(
        currentness,
        TenantPrincipalWorkforceCurrentness,
    ):
        return (
            WorkforceAdmissionDisposition.NOT_CURRENT
        )

    if not currentness.has_active_relationship:
        return (
            WorkforceAdmissionDisposition.NOT_CURRENT
        )

    return WorkforceAdmissionDisposition.SATISFIED


__all__ = [
    "VERSION",
    "WorkforceAdmissionDisposition",
    "WorkforceAdmissionPolicyError",
    "evaluate_workforce_admission",
]


# ARTIFACT: workforce_admission_policy.py
# AUTHORITY BOUNDARY: workforce prerequisite fact only; never authorization.
# FINANCIAL EXECUTION AUTHORITY: NO.
