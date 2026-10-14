"""
Pure privileged-eligibility domain for WILSY IAM.

VERSION:
v1.0.0-P2-R1-PRIVILEGED-ELIGIBILITY-DOMAIN

EPITOME:
Evaluate structural eligibility to enter a later privileged lifecycle for
ENTERPRISE_ADMIN or SOVEREIGN_ARCHITECT from caller-supplied trusted/current
facts. Eligibility is not assignment, activation, authorization, permission,
session authority, break glass, security assurance, or financial authority.

AUTHORITY BOUNDARY:
This module performs no I/O and owns no persistence. It does not authenticate,
read IAM repositories, assign roles, activate privileges, create or revoke
sessions, validate MFA, manufacture security assurance, or execute financial
operations.

PRINCIPAL-KIND POSTURE:
Durable principal authority does not canonically classify principals as human,
machine, service, or AI. This policy therefore performs no principal-kind
discrimination and must not deny machine/AI principals by assumption.

ROOT-SCOPE POSTURE:
ENTERPRISE_ADMIN is treated as tenant-privileged.
SOVEREIGN_ARCHITECT is treated as platform/system-root and is never tenant
delegation.

PLATFORM CURRENTNESS POSTURE:
The currently certified workforce-currentness projection is tenant scoped.
This domain therefore requires an explicit caller-supplied platform prerequisite
fact before SOVEREIGN_ARCHITECT can be structurally eligible. The domain does
not derive or invent that fact.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Final, cast


VERSION: Final[str] = (
    "v1.0.0-P2-R1-"
    "PRIVILEGED-ELIGIBILITY-DOMAIN"
)

ENTERPRISE_ADMIN: Final[str] = (
    "ENTERPRISE_ADMIN"
)

SOVEREIGN_ARCHITECT: Final[str] = (
    "SOVEREIGN_ARCHITECT"
)


class PrivilegedTargetClass(StrEnum):
    TENANT_PRIVILEGED = (
        "TENANT_PRIVILEGED"
    )
    PLATFORM_SYSTEM_ROOT = (
        "PLATFORM_SYSTEM_ROOT"
    )


class PrivilegedEligibilityReason(StrEnum):
    ELIGIBLE = "ELIGIBLE"
    MALFORMED_INPUT = "MALFORMED_INPUT"
    UNKNOWN_PRIVILEGED_TARGET = (
        "UNKNOWN_PRIVILEGED_TARGET"
    )
    PRINCIPAL_NOT_CURRENT = (
        "PRINCIPAL_NOT_CURRENT"
    )
    TENANT_SCOPE_REQUIRED = (
        "TENANT_SCOPE_REQUIRED"
    )
    TENANT_MEMBERSHIP_NOT_CURRENT = (
        "TENANT_MEMBERSHIP_NOT_CURRENT"
    )
    TENANT_WORKFORCE_NOT_CURRENT = (
        "TENANT_WORKFORCE_NOT_CURRENT"
    )
    PLATFORM_SCOPE_MUST_NOT_CARRY_TENANT = (
        "PLATFORM_SCOPE_MUST_NOT_CARRY_TENANT"
    )
    PLATFORM_PREREQUISITE_NOT_PROVEN = (
        "PLATFORM_PREREQUISITE_NOT_PROVEN"
    )


@dataclass(frozen=True, slots=True)
class PrivilegedEligibilityDecision:
    principal_id: str
    privileged_role_id: str
    target_class: PrivilegedTargetClass | None
    tenant_id: str | None
    principal_current: bool
    tenant_membership_current: bool | None
    workforce_required: bool
    tenant_workforce_current: bool | None
    platform_prerequisite_proven: bool | None
    eligible: bool
    reason: PrivilegedEligibilityReason


def _nonblank(
    value: object,
) -> str | None:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        return None
    return value


def _decision(
    *,
    principal_id: str,
    privileged_role_id: str,
    target_class: PrivilegedTargetClass | None,
    tenant_id: str | None,
    principal_current: bool,
    tenant_membership_current: bool | None,
    workforce_required: bool,
    tenant_workforce_current: bool | None,
    platform_prerequisite_proven: bool | None,
    eligible: bool,
    reason: PrivilegedEligibilityReason,
) -> PrivilegedEligibilityDecision:
    return PrivilegedEligibilityDecision(
        principal_id=principal_id,
        privileged_role_id=privileged_role_id,
        target_class=target_class,
        tenant_id=tenant_id,
        principal_current=principal_current,
        tenant_membership_current=tenant_membership_current,
        workforce_required=workforce_required,
        tenant_workforce_current=tenant_workforce_current,
        platform_prerequisite_proven=platform_prerequisite_proven,
        eligible=eligible,
        reason=reason,
    )


def evaluate_privileged_eligibility(
    *,
    principal_id: object,
    privileged_role_id: object,
    principal_current: object,
    tenant_id: object = None,
    tenant_membership_current: object = None,
    workforce_required: object = False,
    tenant_workforce_current: object = None,
    platform_prerequisite_proven: object = None,
) -> PrivilegedEligibilityDecision:
    """Evaluate structural eligibility only.

    Every currentness/prerequisite input is a fact already proved by a caller.
    This function does not establish or refresh those facts.

    ENTERPRISE_ADMIN:
      - exact tenant scope required;
      - current principal required;
      - current tenant membership required;
      - when workforce_required is true, current tenant workforce required.

    SOVEREIGN_ARCHITECT:
      - tenant scope is forbidden;
      - current principal required;
      - an explicit platform prerequisite must already be proven by a later
        canonical source;
      - tenant membership/workforce facts are forbidden because system-root
        authority is not tenant delegation.

    No existing target-role assignment is required. Eligibility is merely
    admission to a later privileged lifecycle.
    """

    principal = _nonblank(
        principal_id
    )

    role = _nonblank(
        privileged_role_id
    )

    malformed = (
        principal is None
        or role is None
        or not isinstance(
            principal_current,
            bool,
        )
        or not isinstance(
            workforce_required,
            bool,
        )
        or (
            tenant_id is not None
            and _nonblank(
                tenant_id
            ) is None
        )
        or (
            tenant_membership_current
            is not None
            and not isinstance(
                tenant_membership_current,
                bool,
            )
        )
        or (
            tenant_workforce_current
            is not None
            and not isinstance(
                tenant_workforce_current,
                bool,
            )
        )
        or (
            platform_prerequisite_proven
            is not None
            and not isinstance(
                platform_prerequisite_proven,
                bool,
            )
        )
    )

    safe_principal = (
        principal
        if principal is not None
        else ""
    )

    safe_role = (
        role
        if role is not None
        else ""
    )

    safe_tenant = (
        tenant_id
        if isinstance(
            tenant_id,
            str,
        )
        else None
    )

    safe_principal_current = (
        principal_current
        if isinstance(
            principal_current,
            bool,
        )
        else False
    )

    safe_workforce_required = (
        workforce_required
        if isinstance(
            workforce_required,
            bool,
        )
        else False
    )

    if malformed:
        return _decision(
            principal_id=safe_principal,
            privileged_role_id=safe_role,
            target_class=None,
            tenant_id=safe_tenant,
            principal_current=safe_principal_current,
            tenant_membership_current=(
                tenant_membership_current
                if isinstance(
                    tenant_membership_current,
                    bool,
                )
                else None
            ),
            workforce_required=(
                safe_workforce_required
            ),
            tenant_workforce_current=(
                tenant_workforce_current
                if isinstance(
                    tenant_workforce_current,
                    bool,
                )
                else None
            ),
            platform_prerequisite_proven=(
                platform_prerequisite_proven
                if isinstance(
                    platform_prerequisite_proven,
                    bool,
                )
                else None
            ),
            eligible=False,
            reason=(
                PrivilegedEligibilityReason
                .MALFORMED_INPUT
            ),
        )

    assert principal is not None
    assert role is not None
    assert isinstance(
        principal_current,
        bool,
    )
    assert isinstance(
        workforce_required,
        bool,
    )

    # Runtime validation above proves these optional caller facts are now
    # exactly bool | None. Preserve the public fail-closed object inputs while
    # giving the static type checker the same post-validation knowledge.
    membership_current = cast(
        bool | None,
        tenant_membership_current,
    )
    workforce_current = cast(
        bool | None,
        tenant_workforce_current,
    )
    platform_prerequisite = cast(
        bool | None,
        platform_prerequisite_proven,
    )

    if role not in {
        ENTERPRISE_ADMIN,
        SOVEREIGN_ARCHITECT,
    }:
        return _decision(
            principal_id=principal,
            privileged_role_id=role,
            target_class=None,
            tenant_id=safe_tenant,
            principal_current=principal_current,
            tenant_membership_current=(
                membership_current
            ),
            workforce_required=workforce_required,
            tenant_workforce_current=(
                workforce_current
            ),
            platform_prerequisite_proven=(
                platform_prerequisite
            ),
            eligible=False,
            reason=(
                PrivilegedEligibilityReason
                .UNKNOWN_PRIVILEGED_TARGET
            ),
        )

    target_class = (
        PrivilegedTargetClass
        .TENANT_PRIVILEGED
        if role == ENTERPRISE_ADMIN
        else PrivilegedTargetClass
        .PLATFORM_SYSTEM_ROOT
    )

    if not principal_current:
        return _decision(
            principal_id=principal,
            privileged_role_id=role,
            target_class=target_class,
            tenant_id=safe_tenant,
            principal_current=False,
            tenant_membership_current=(
                membership_current
            ),
            workforce_required=workforce_required,
            tenant_workforce_current=(
                workforce_current
            ),
            platform_prerequisite_proven=(
                platform_prerequisite
            ),
            eligible=False,
            reason=(
                PrivilegedEligibilityReason
                .PRINCIPAL_NOT_CURRENT
            ),
        )

    if role == ENTERPRISE_ADMIN:
        tenant = _nonblank(
            tenant_id
        )

        if tenant is None:
            return _decision(
                principal_id=principal,
                privileged_role_id=role,
                target_class=target_class,
                tenant_id=None,
                principal_current=True,
                tenant_membership_current=(
                    membership_current
                ),
                workforce_required=(
                    workforce_required
                ),
                tenant_workforce_current=(
                    workforce_current
                ),
                platform_prerequisite_proven=(
                    platform_prerequisite
                ),
                eligible=False,
                reason=(
                    PrivilegedEligibilityReason
                    .TENANT_SCOPE_REQUIRED
                ),
            )

        if (
            membership_current
            is not True
        ):
            return _decision(
                principal_id=principal,
                privileged_role_id=role,
                target_class=target_class,
                tenant_id=tenant,
                principal_current=True,
                tenant_membership_current=(
                    membership_current
                ),
                workforce_required=(
                    workforce_required
                ),
                tenant_workforce_current=(
                    workforce_current
                ),
                platform_prerequisite_proven=(
                    platform_prerequisite
                ),
                eligible=False,
                reason=(
                    PrivilegedEligibilityReason
                    .TENANT_MEMBERSHIP_NOT_CURRENT
                ),
            )

        if (
            workforce_required
            and workforce_current
            is not True
        ):
            return _decision(
                principal_id=principal,
                privileged_role_id=role,
                target_class=target_class,
                tenant_id=tenant,
                principal_current=True,
                tenant_membership_current=True,
                workforce_required=True,
                tenant_workforce_current=(
                    workforce_current
                ),
                platform_prerequisite_proven=(
                    platform_prerequisite
                ),
                eligible=False,
                reason=(
                    PrivilegedEligibilityReason
                    .TENANT_WORKFORCE_NOT_CURRENT
                ),
            )

        return _decision(
            principal_id=principal,
            privileged_role_id=role,
            target_class=target_class,
            tenant_id=tenant,
            principal_current=True,
            tenant_membership_current=True,
            workforce_required=(
                workforce_required
            ),
            tenant_workforce_current=(
                workforce_current
            ),
            platform_prerequisite_proven=None,
            eligible=True,
            reason=(
                PrivilegedEligibilityReason
                .ELIGIBLE
            ),
        )

    # SOVEREIGN_ARCHITECT is system root, never tenant delegation.
    if (
        tenant_id is not None
        or membership_current
        is not None
        or workforce_current
        is not None
        or workforce_required
    ):
        return _decision(
            principal_id=principal,
            privileged_role_id=role,
            target_class=target_class,
            tenant_id=safe_tenant,
            principal_current=True,
            tenant_membership_current=(
                membership_current
            ),
            workforce_required=(
                workforce_required
            ),
            tenant_workforce_current=(
                workforce_current
            ),
            platform_prerequisite_proven=(
                platform_prerequisite
            ),
            eligible=False,
            reason=(
                PrivilegedEligibilityReason
                .PLATFORM_SCOPE_MUST_NOT_CARRY_TENANT
            ),
        )

    if (
        platform_prerequisite
        is not True
    ):
        return _decision(
            principal_id=principal,
            privileged_role_id=role,
            target_class=target_class,
            tenant_id=None,
            principal_current=True,
            tenant_membership_current=None,
            workforce_required=False,
            tenant_workforce_current=None,
            platform_prerequisite_proven=(
                platform_prerequisite
            ),
            eligible=False,
            reason=(
                PrivilegedEligibilityReason
                .PLATFORM_PREREQUISITE_NOT_PROVEN
            ),
        )

    return _decision(
        principal_id=principal,
        privileged_role_id=role,
        target_class=target_class,
        tenant_id=None,
        principal_current=True,
        tenant_membership_current=None,
        workforce_required=False,
        tenant_workforce_current=None,
        platform_prerequisite_proven=True,
        eligible=True,
        reason=(
            PrivilegedEligibilityReason
            .ELIGIBLE
        ),
    )


__all__ = [
    "VERSION",
    "ENTERPRISE_ADMIN",
    "SOVEREIGN_ARCHITECT",
    "PrivilegedTargetClass",
    "PrivilegedEligibilityReason",
    "PrivilegedEligibilityDecision",
    "evaluate_privileged_eligibility",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: privileged_eligibility.py
# VERSION: v1.0.0-P2-R1-PRIVILEGED-ELIGIBILITY-DOMAIN
# AUTHORITY BOUNDARY: pure structural eligibility decision only; no assignment,
# activation, authentication, authorization, persistence, HTTP, security
# assurance, session, break-glass, or financial-execution authority
# PRINCIPAL POSTURE: no human/machine/AI discrimination is inferred
# TENANT POSTURE: ENTERPRISE_ADMIN eligibility is tenant scoped
# ROOT POSTURE: SOVEREIGN_ARCHITECT is system-root and never tenant delegation
# PLATFORM POSTURE: platform prerequisite is caller-proved; never invented here
# END OF WILSY OS SOVEREIGN ARTIFACT
