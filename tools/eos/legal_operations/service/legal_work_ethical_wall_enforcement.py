"""TITLE: WILSY OS Source-Verified Ethical-Wall Enforcement Boundary.
VERSION: v1.0.0-G77-SOURCE-VERIFIED-NEGATIVE-ENFORCEMENT
AUTHORITY: Transaction-bound canonical source verification and denial only.
EPITOME: Re-read current IAM, binding, assignment, conflict, review and wall
    sources in one caller-owned transaction, apply restriction/revocation
    precedence, and deny until institutional reviewer/admin authority and
    acknowledgment ownership are independently ratified.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_work_ethical_wall_enforcement.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering / Legal Operations;
    canonical repositories own evidence and disclosure points own enforcement.
CERTIFICATION / UPDATE DATE: 2026-10-21.
CHANGELOG: 2026-10-21 v1.0.0 introduces ordered canonical source verification
    with no positive authorization or content-delivery return path.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Stable content-free denials; no evidence identifiers logged.
TENANT BOUNDARY: Exact authenticated tenant, matter and principal on every source.
TRANSACTION BOUNDARY: Caller owns active transaction, abort and whole retry.
AUTHORITY BOUNDARY: Role titles, booleans and recorded approvals never authorize.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import re
from typing import Any, Final, NoReturn, Protocol

from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition_currentness import (
    LegalClientMatterConflictDispositionCurrentness as ConflictCurrentness,
    LegalClientMatterConflictDispositionCurrentnessState as ConflictState,
)
from tools.eos.legal_operations.domain.legal_practitioner_matter_binding import (
    LegalPractitionerMatterBinding as Binding,
    PractitionerMatterBindingStatus,
)
from tools.eos.legal_operations.domain.legal_work_assignment import LegalWorkAssignment
from tools.eos.legal_operations.domain.legal_work_ethical_wall_policy import (
    EthicalWallAccessState,
    EthicalWallPolicyRevision,
    EthicalWallPolicyStatus,
    InstitutionalRatificationState,
    evaluate_ethical_wall_access,
)
from tools.eos.legal_operations.domain.legal_work_practitioner_confidentiality_review_decision import (
    ConfidentialityReviewDecision,
    ConfidentialityReviewDecisionState,
)

VERSION: Final[str] = "v1.0.0-G77-SOURCE-VERIFIED-NEGATIVE-ENFORCEMENT"
SOURCE_VERIFIED_CLEARANCE: Final[bool] = False
OPERATIONAL_ACCESS_ENABLED: Final[bool] = False
_ID: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,199}\Z")


class EthicalWallEnforcementDenied(PermissionError):
    """Stable non-sensitive denial from the G77 enforcement boundary."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class EthicalWallPolicySource(Protocol):
    """Exact G76-B read contract consumed inside the caller transaction."""

    def get_current(
        self, tenant_id: str, case_matter_id: str, policy_id: str, *, session: object,
    ) -> EthicalWallPolicyRevision: ...

    def list_history(
        self, tenant_id: str, case_matter_id: str, policy_id: str, *, session: object,
    ) -> tuple[EthicalWallPolicyRevision, ...]: ...


def _deny(code: str) -> NoReturn:
    raise EthicalWallEnforcementDenied(code)


def _identity(value: object) -> str:
    if type(value) is not str or _ID.fullmatch(value) is None:
        _deny("G77_SCOPE_INVALID")
    if value.casefold() in {"default", "global", "root", "*"}:
        _deny("G77_SCOPE_INVALID")
    return value


def _time(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        _deny("G77_EVALUATION_TIME_INVALID")
    result = value.astimezone(timezone.utc)
    if result.microsecond or result != value:
        _deny("G77_EVALUATION_TIME_INVALID")
    return result


def _transaction(session: object) -> object:
    try:
        active = getattr(session, "in_transaction", False)
        active = active() if callable(active) else active
    except Exception:
        active = False
    if active is not True:
        _deny("G77_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _resolve(source: object, code: str, **scope: object) -> object:
    resolver = getattr(source, "resolve_current", None)
    if not callable(resolver):
        _deny(code)
    try:
        return resolver(**scope)
    except EthicalWallEnforcementDenied:
        raise
    except Exception:
        _deny(code)


def _verify_iam(value: object) -> None:
    if type(value) is not TenantAuthorizationDecision:
        _deny("G77_IAM_INVALID")
    if value.authorized is not True or value.reason is not TenantAuthorizationReason.AUTHORIZED:
        _deny("G77_IAM_DENIED")


def _verify_binding(value: object, tenant: str, matter: str, principal: str) -> None:
    if type(value) is not Binding:
        _deny("G77_BINDING_INVALID")
    try:
        canonical = Binding.from_dict(value.to_dict())
    except Exception:
        _deny("G77_BINDING_INVALID")
    if (
        canonical != value
        or canonical.tenant_id != tenant
        or canonical.case_matter_id != matter
        or canonical.practitioner_principal_id != principal
        or canonical.status is not PractitionerMatterBindingStatus.ACTIVE
        or canonical.authorizes_matter_access is not False
    ):
        _deny("G77_BINDING_INVALID")


def _verify_assignments(value: object, tenant: str, matter: str, principal: str) -> None:
    if type(value) is not tuple or not value:
        _deny("G77_ASSIGNMENT_REQUIRED")
    matches = 0
    for item in value:
        if type(item) is not LegalWorkAssignment:
            _deny("G77_ASSIGNMENT_INVALID")
        try:
            canonical = replace(item)
        except Exception:
            _deny("G77_ASSIGNMENT_INVALID")
        if canonical != item:
            _deny("G77_ASSIGNMENT_INVALID")
        if (
            item.tenant_id == tenant
            and item.case_matter_id == matter
            and item.assignee_principal_id == principal
        ):
            matches += 1
        elif item.tenant_id != tenant or item.case_matter_id != matter:
            _deny("G77_ASSIGNMENT_SCOPE_INVALID")
    if matches < 1:
        _deny("G77_ASSIGNMENT_REQUIRED")


def _verify_conflict(value: object, tenant: str, matter: str) -> ConflictCurrentness:
    if type(value) is not ConflictCurrentness:
        _deny("G77_CONFLICT_INVALID")
    try:
        canonical = ConflictCurrentness.from_dict(value.to_dict())
    except Exception:
        _deny("G77_CONFLICT_INVALID")
    if (
        canonical != value
        or value.tenant_id != tenant
        or value.case_matter_id != matter
        or value.state is not ConflictState.ENGAGEMENT_PERMITTED
    ):
        _deny("G77_CONFLICT_BLOCKED")
    return value


def _verify_review(
    value: object, tenant: str, matter: str, principal: str, at: datetime,
) -> ConfidentialityReviewDecision:
    if type(value) is not ConfidentialityReviewDecision:
        _deny("G77_REVIEW_INVALID")
    try:
        canonical = replace(value)
    except Exception:
        _deny("G77_REVIEW_INVALID")
    if (
        canonical != value
        or value.tenant_id != tenant
        or value.case_matter_id != matter
        or value.practitioner_principal_id != principal
        or value.reviewer_principal_id == principal
    ):
        _deny("G77_REVIEW_INVALID")
    if value.decision is not ConfidentialityReviewDecisionState.APPROVED:
        _deny("G77_REVIEW_DENIED")
    if value.decided_at > at or at >= value.expires_at:
        _deny("G77_REVIEW_EXPIRED")
    if value.permits_operational_access is not False:
        _deny("G77_REVIEW_INVALID")
    return value


def require_source_verified_ethical_wall_access(
    *, authenticated_principal_id: str, tenant_id: str, case_matter_id: str,
    policy_id: str, evaluation_time: datetime, iam_source: object,
    binding_source: object, assignment_source: object, conflict_source: object,
    review_source: object, wall_source: EthicalWallPolicySource, session: object,
) -> NoReturn:
    """Verify every currently available source and always end in bounded denial.

    The service intentionally has no success return while institutional reviewer,
    administrator, exemption, emergency-denial and wall-acknowledgment authority
    are unratified. Callers cannot provide booleans, titles, fingerprints or mock
    decisions as substitutes for canonical source objects.
    """
    tx = _transaction(session)
    principal = _identity(authenticated_principal_id)
    tenant = _identity(tenant_id)
    matter = _identity(case_matter_id)
    policy = _identity(policy_id)
    at = _time(evaluation_time)
    scope = {
        "tenant_id": tenant, "case_matter_id": matter,
        "practitioner_principal_id": principal, "session": tx,
    }

    iam = _resolve(iam_source, "G77_IAM_UNAVAILABLE", **scope)
    _verify_iam(iam)
    binding = _resolve(binding_source, "G77_BINDING_UNAVAILABLE", **scope)
    _verify_binding(binding, tenant, matter, principal)
    assignments = _resolve(assignment_source, "G77_ASSIGNMENT_UNAVAILABLE", **scope)
    _verify_assignments(assignments, tenant, matter, principal)
    conflict = _verify_conflict(
        _resolve(conflict_source, "G77_CONFLICT_UNAVAILABLE", **scope), tenant, matter,
    )
    review = _verify_review(
        _resolve(review_source, "G77_REVIEW_UNAVAILABLE", **scope),
        tenant, matter, principal, at,
    )
    if review.conflict_disposition_fingerprint not in conflict.decisive_disposition_fingerprints:
        _deny("G77_REVIEW_CONFLICT_MISMATCH")

    try:
        current = wall_source.get_current(tenant, matter, policy, session=tx)
        history = wall_source.list_history(tenant, matter, policy, session=tx)
    except Exception:
        _deny("G77_WALL_SOURCE_UNAVAILABLE")
    if type(current) is not EthicalWallPolicyRevision or type(history) is not tuple:
        _deny("G77_WALL_SOURCE_INVALID")
    if not history or history[-1] != current:
        _deny("G77_WALL_POINTER_INVALID")
    if (
        current.tenant_id != tenant
        or current.case_matter_id != matter
        or current.policy_id != policy
        or current.status is EthicalWallPolicyStatus.REVOKED
        or current.ratification_state is InstitutionalRatificationState.REVOKED
    ):
        _deny("G77_WALL_REVOKED_OR_SCOPE_INVALID")
    # D02 negative control: a recorded wall administrator cannot review the
    # same practitioner's confidentiality decision. This is a denial-only
    # separation check, not evidence that either identity is institutionally
    # authorized to hold the recorded role.
    if review.reviewer_principal_id == current.administrator_principal_id:
        _deny("G77_REVIEW_ADMIN_SEPARATION_INVALID")
    if (
        review.ethical_wall_policy_reference != current.policy_id
        or review.ethical_wall_policy_fingerprint != current.fingerprint
    ):
        _deny("G77_REVIEW_POLICY_MISMATCH")
    decision = evaluate_ethical_wall_access(
        tenant_id=tenant, case_matter_id=matter,
        practitioner_principal_id=principal, evaluation_time=at,
        revisions=history,
    )
    if decision.state is EthicalWallAccessState.DENIED_RESTRICTED:
        _deny("G77_EXPLICITLY_RESTRICTED")
    if decision.state is not EthicalWallAccessState.ALLOW_RECORDED_UNVERIFIED:
        _deny("G77_WALL_NOT_SATISFIED")
    if decision.permits_operational_access is not False:
        _deny("G77_WALL_SOURCE_INVALID")

    # The repository contains no ratified canonical source for reviewer/admin
    # eligibility or ethical-wall acknowledgment. Recorded fingerprints cannot
    # fill that institutional gap, so a favorable documentary chain still denies.
    _deny("G77_INSTITUTIONAL_AUTHORITY_UNRATIFIED")


__all__ = [
    "VERSION", "SOURCE_VERIFIED_CLEARANCE", "OPERATIONAL_ACCESS_ENABLED",
    "EthicalWallPolicySource", "EthicalWallEnforcementDenied",
    "require_source_verified_ethical_wall_access",
]

# ARTIFACT: legal_work_ethical_wall_enforcement.py
# VERSION: v1.0.0-G77-SOURCE-VERIFIED-NEGATIVE-ENFORCEMENT
# AUTHORITY BOUNDARY: canonical negative verification only; no access grant
# TENANT POSTURE: exact authenticated tenant/matter/principal on every source
# FAIL-CLOSED POSTURE: absent, stale, revoked, corrupt or unratified always denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
