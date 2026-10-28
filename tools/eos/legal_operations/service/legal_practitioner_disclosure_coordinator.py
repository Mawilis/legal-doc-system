"""TITLE: WILSY OS Transaction-Bound Practitioner Disclosure Coordinator.
VERSION: v1.0.0-G79-TRANSACTION-BOUND-DENY-ONLY-COORDINATOR
AUTHORITY: Authenticated request projection + canonical source checks + denial only.
EPITOME: Bind the authenticated tenant/principal, caller-owned active transaction,
current ethical-wall source verification, institutional readiness and content
admission before any content reader can be invoked. No HTTP route is enabled.
SECURITY: No caller-supplied grant, no positive admission, no content release while
institutional confidentiality authority remains unratified.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol, NoReturn

from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_work_confidentiality_policy_readiness import (
    evaluate_policy_readiness,
)
from tools.eos.legal_operations.service.legal_work_ethical_wall_authorization_fence import (
    CanonicalWallAuthorizationFence,
    WallFenceUnavailable,
)
from tools.eos.legal_operations.service.legal_work_ethical_wall_enforcement import (
    EthicalWallEnforcementDenied,
    EthicalWallPolicySource,
    require_source_verified_ethical_wall_access,
)
from tools.eos.legal_operations.service.legal_work_practitioner_content_admission import (
    PractitionerContentAdmissionDenied,
    require_practitioner_content_admission,
)

VERSION = "v1.0.0-G79-TRANSACTION-BOUND-DENY-ONLY-COORDINATOR"


class PractitionerDisclosureDenied(PermissionError):
    """Stable, content-free denial from the single practitioner disclosure seam."""


class PractitionerDisclosureRetryTransaction(RuntimeError):
    """Caller must abort and retry the entire transaction from a fresh snapshot."""


class PractitionerContentReader(Protocol):
    """Internal content reader contract; not an authorization authority."""

    def read_content(
        self,
        *,
        tenant_id: str,
        case_matter_id: str,
        content_reference: str,
        session: object,
    ) -> bytes: ...


def _deny(code: str) -> NoReturn:
    raise PractitionerDisclosureDenied(code)


def _text(name: str, value: object) -> str:
    if (
        type(value) is not str
        or not value
        or value.strip() != value
        or len(value) > 256
        or any(ord(char) < 33 or ord(char) > 126 for char in value)
        or value.casefold() in {"unknown", "none", "null", "system", "default"}
    ):
        _deny("G79_REQUEST_SCOPE_INVALID")
    return value


def _active_transaction(session: object) -> None:
    try:
        active = getattr(session, "in_transaction", False)
        active = active() if callable(active) else active
    except Exception:
        active = False
    if active is not True:
        _deny("G79_ACTIVE_TRANSACTION_REQUIRED")


def read_practitioner_document_content(
    *,
    authorization_context: TenantAuthorizationContext,
    case_matter_id: str,
    content_reference: str,
    policy_id: str,
    evaluation_time: datetime,
    iam_source: object,
    binding_source: object,
    assignment_source: object,
    conflict_source: object,
    review_source: object,
    wall_source: EthicalWallPolicySource,
    authorization_fence: CanonicalWallAuthorizationFence,
    content_reader: PractitionerContentReader,
    session: object,
) -> bytes:
    """Verify the complete scoped chain before attempting any content read.

    The existing G77 source verifier is intentionally denial-only until
    institutional reviewer/admin and acknowledgement authority are ratified.
    The G63 readiness check and G72 admission guard are independent fail-closed
    backstops. Therefore the reader is currently unreachable by design. This
    coordinator is not mounted to an HTTP route and cannot grant access.
    """
    if type(authorization_context) is not TenantAuthorizationContext:
        _deny("G79_AUTHENTICATED_CONTEXT_REQUIRED")

    identity = authorization_context.identity
    tenant = _text("tenant_id", authorization_context.tenant_id)
    principal = _text("principal_id", getattr(identity, "identity_id", None))
    matter = _text("case_matter_id", case_matter_id)
    reference = _text("content_reference", content_reference)
    policy = _text("policy_id", policy_id)

    if getattr(identity, "tenant_id", None) != tenant:
        _deny("G79_AUTHENTICATED_TENANT_MISMATCH")

    decision = authorization_context.decision
    if (
        type(decision) is not TenantAuthorizationDecision
        or decision.authorized is not True
        or decision.reason is not TenantAuthorizationReason.AUTHORIZED
    ):
        _deny("G79_TENANT_AUTHORIZATION_REQUIRED")

    _active_transaction(session)

    # First contend on a policy-wide sentinel, then the exact principal fence.
    # G76 mutation uses the same policy-wide sentinel before any currentness read.
    # A retryable conflict must escape so the caller can abort/restart the full
    # transaction; it must never be downgraded to a normal denial or partial read.
    try:
        authorization_fence.contend(
            tenant_id=tenant,
            case_matter_id=matter,
            practitioner_principal_id="policy",
            policy_id=policy,
            session=session,
        )
        authorization_fence.contend(
            tenant_id=tenant,
            case_matter_id=matter,
            practitioner_principal_id=principal,
            policy_id=policy,
            session=session,
        )
    except WallFenceUnavailable as error:
        if error.retryable:
            raise PractitionerDisclosureRetryTransaction(
                "G79_RETRY_WHOLE_TRANSACTION"
            ) from error
        _deny("G79_AUTHORIZATION_FENCE_UNAVAILABLE")

    try:
        require_source_verified_ethical_wall_access(
            authenticated_principal_id=principal,
            tenant_id=tenant,
            case_matter_id=matter,
            policy_id=policy,
            evaluation_time=evaluation_time,
            iam_source=iam_source,
            binding_source=binding_source,
            assignment_source=assignment_source,
            conflict_source=conflict_source,
            review_source=review_source,
            wall_source=wall_source,
            session=session,
        )
    except EthicalWallEnforcementDenied as error:
        _deny(f"G79_SOURCE_CHAIN_DENIED:{error.code}")
    except Exception:
        _deny("G79_SOURCE_CHAIN_UNAVAILABLE")

    # Defensive backstops: even if the G77 implementation were ever changed to
    # return, institutional readiness and G72 still deny before reader access.
    readiness = evaluate_policy_readiness()
    if (
        readiness.permits_operational_access is not True
        or readiness.permits_reviewer_authorization is not True
        or readiness.permits_wall_enforcement_claim is not True
    ):
        _deny("G79_INSTITUTIONAL_AUTHORITY_UNRATIFIED")

    try:
        require_practitioner_content_admission(
            tenant_id=tenant,
            case_matter_id=matter,
            practitioner_principal_id=principal,
            content_reference=reference,
            session=session,
        )
    except PractitionerContentAdmissionDenied:
        _deny("G79_CONTENT_ADMISSION_UNAVAILABLE")
    except Exception:
        _deny("G79_CONTENT_ADMISSION_UNAVAILABLE")

    # This line is intentionally unreachable under the repository's current
    # authority contracts. Keep the exact same transaction and scoped reference
    # for any future, separately ratified implementation.
    try:
        content = content_reader.read_content(
            tenant_id=tenant,
            case_matter_id=matter,
            content_reference=reference,
            session=session,
        )
    except Exception:
        _deny("G79_CONTENT_UNAVAILABLE")
    if type(content) is not bytes:
        _deny("G79_CONTENT_INVALID")
    return content


__all__ = [
    "VERSION",
    "PractitionerDisclosureDenied",
    "PractitionerDisclosureRetryTransaction",
    "PractitionerContentReader",
    "read_practitioner_document_content",
]
