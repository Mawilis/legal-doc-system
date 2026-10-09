"""WILSY OS subscription-active Legal entitlement composition service.

TITLE: Subscription Active Entitlement Composition Service
VERSION: v1.0.0-D22B3-P42-SUBSCRIPTION-ACTIVE-ENTITLEMENT-COMPOSITION-SERVICE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Atomically compose canonical subscription lifecycle mutation with
         positive Legal Operations tenant-product entitlement issuance.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/subscription_active_entitlement_composition_service.py
COLLABORATION / OWNERSHIP: SubscriptionRegistry owns commercial lifecycle;
                            D22B3 P25 owns authorization and entitlement
                            issuance; this service alone owns their shared
                            Mongo transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-10-09
CHANGELOG: v1.0.0-D22B3-P42-SUBSCRIPTION-ACTIVE-ENTITLEMENT-COMPOSITION-SERVICE
           establishes create, resume and reactivate composition, deterministic
           lifecycle-derived issuance replay keys, bounded whole-transaction
           retry and fail-closed unknown-commit classification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Tenant and principal scope derive solely from an
                             active SovereignIdentity; no credentials or PII
                             are logged or returned.
TENANT BOUNDARY: Every commercial mutation and entitlement issuance is bound
                 to identity.tenant_id and the exact same active session.
AUTHORITY BOUNDARY: Composes existing commercial and positive Legal Operations
                    authorities without replacing catalogue, CRM, IAM, router,
                    composer or issuance authority.
TRANSACTION BOUNDARY: This service exclusively starts, commits, aborts and
                      safely retries the complete commercial-plus-entitlement
                      transaction. Participants never own transaction lifecycle.
FINANCIAL AUTHORITY BOUNDARY: No payment execution, financial execution or
                              settlement authority; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Invalid input, unavailable dependencies, commercial or
                         issuance failure, retry exhaustion and uncertain commit
                         reject without synthetic success.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Final, NoReturn

from pymongo.errors import PyMongoError

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    COLLECTION as AUTHORIZATION_EVIDENCE_COLLECTION,
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.kernel.db import get_client, get_database
from tools.eos.saas.billing.subscription_registry import (
    SubscriptionRegistry,
    SubscriptionRegistryError,
)
from tools.eos.saas.domain.subscription import (
    AuditAction,
    SubscriptionEntity,
    SubscriptionStatus,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_issuance_orchestrator import (
    TenantProductEntitlementIssuanceOrchestratorError,
    TenantProductEntitlementIssuanceResult,
    issue_tenant_product_entitlement,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION as ENTITLEMENT_CURRENT_COLLECTION,
    HISTORY_COLLECTION as ENTITLEMENT_HISTORY_COLLECTION,
)


VERSION: Final[str] = (
    "v1.0.0-D22B3-P42-SUBSCRIPTION-ACTIVE-ENTITLEMENT-COMPOSITION-SERVICE"
)
SUBSCRIPTION_COLLECTION: Final[str] = "subscriptions"
LEGAL_FEATURE: Final[str] = "legal.core"
IDEMPOTENCY_NAMESPACE: Final[str] = "d22b3-p42"
MAX_TRANSACTION_ATTEMPTS: Final[int] = 3


class SubscriptionActiveEntitlementCompositionServiceError(RuntimeError):
    """Base typed P42 failure carrying one stable non-sensitive code."""

    default_code = "D22B3_P42_SERVICE_ERROR"

    def __init__(self, code: str | None = None) -> None:
        """Create one fail-closed service error without widening authority."""
        self.code = code or self.default_code
        super().__init__(self.code)


class SubscriptionActiveEntitlementCompositionInputError(
    SubscriptionActiveEntitlementCompositionServiceError
):
    """Public service input or identity is invalid."""

    default_code = "D22B3_P42_INPUT_INVALID"


class SubscriptionActiveEntitlementCompositionDependencyError(
    SubscriptionActiveEntitlementCompositionServiceError
):
    """Canonical Mongo runtime or required dependency is unavailable."""

    default_code = "D22B3_P42_RUNTIME_DEPENDENCY_UNAVAILABLE"


class SubscriptionActiveEntitlementCompositionLifecycleError(
    SubscriptionActiveEntitlementCompositionServiceError
):
    """Canonical subscription lifecycle mutation failed closed."""

    default_code = "D22B3_P42_SUBSCRIPTION_LIFECYCLE_FAILED"


class SubscriptionActiveEntitlementCompositionIssuanceError(
    SubscriptionActiveEntitlementCompositionServiceError
):
    """Sealed positive Legal Operations issuance failed closed."""

    default_code = "D22B3_P42_ENTITLEMENT_ISSUANCE_FAILED"


class SubscriptionActiveEntitlementCompositionRetryExhaustedError(
    SubscriptionActiveEntitlementCompositionServiceError
):
    """Bounded safe whole-transaction retries were exhausted."""

    default_code = "D22B3_P42_TRANSACTION_RETRY_EXHAUSTED"


class SubscriptionActiveEntitlementCompositionUnknownCommitError(
    SubscriptionActiveEntitlementCompositionServiceError
):
    """Commit outcome is uncertain and commercial mutation is not replayed."""

    default_code = "D22B3_P42_TRANSACTION_COMMIT_UNCERTAIN"


@dataclass(frozen=True, slots=True)
class SubscriptionActiveEntitlementCompositionResult:
    """Immutable post-commit commercial and Legal entitlement projection.

    ``commercial_result`` preserves the registry response needed by later HTTP
    wiring. ``subscription`` is the canonical resulting entity. Entitlement
    applicability is exact and the issuance result is present only after the
    shared transaction committed successfully.
    """

    commercial_result: dict[str, Any]
    subscription: SubscriptionEntity
    legal_entitlement_applicable: bool
    entitlement_issuance_result: TenantProductEntitlementIssuanceResult | None


def _raise(
    error_type: type[SubscriptionActiveEntitlementCompositionServiceError],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise a typed boundary failure while retaining its internal cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(identity: SovereignIdentity) -> SovereignIdentity:
    """Require an active identity as the sole tenant/principal authority."""
    if not isinstance(identity, SovereignIdentity):
        _raise(SubscriptionActiveEntitlementCompositionInputError)
    if identity.status is not PrincipalStatus.ACTIVE:
        _raise(
            SubscriptionActiveEntitlementCompositionInputError,
            "D22B3_P42_ACTIVE_IDENTITY_REQUIRED",
        )
    if not identity.tenant_id or identity.tenant_id != identity.tenant_id.strip():
        _raise(
            SubscriptionActiveEntitlementCompositionInputError,
            "D22B3_P42_IDENTITY_TENANT_INVALID",
        )
    if not identity.identity_id or identity.identity_id != identity.identity_id.strip():
        _raise(
            SubscriptionActiveEntitlementCompositionInputError,
            "D22B3_P42_IDENTITY_PRINCIPAL_INVALID",
        )
    return identity


def _text(value: object, code: str) -> str:
    """Require bounded exact text without coercion or whitespace repair."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 256
    ):
        _raise(SubscriptionActiveEntitlementCompositionInputError, code)
    return value


def _has_label(error: BaseException, label: str) -> bool:
    """Inspect a bounded causal chain for one exact PyMongo error label."""
    current: BaseException | None = error
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        checker = getattr(current, "has_error_label", None)
        if callable(checker):
            try:
                if checker(label) is True:
                    return True
            except Exception:
                pass
        current = current.__cause__ or current.__context__
    return False


def _write_conflict(error: BaseException) -> bool:
    """Classify only repository-precedent safe whole-transaction retry errors."""
    current: BaseException | None = error
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, PyMongoError) and (
            _has_label(current, "TransientTransactionError")
            or getattr(current, "code", None) == 112
        ):
            return True
        current = current.__cause__ or current.__context__
    return False


def _abort_if_active(session: Any) -> None:
    """Best-effort abort without replacing the authoritative primary failure."""
    try:
        marker = getattr(session, "in_transaction", False)
        active = marker() if callable(marker) else marker
        if active is True:
            session.abort_transaction()
    except Exception:
        pass


def _subscription(commercial_result: object) -> SubscriptionEntity:
    """Require a successful registry result containing canonical entity truth."""
    if not isinstance(commercial_result, dict) or commercial_result.get("success") is not True:
        _raise(SubscriptionActiveEntitlementCompositionLifecycleError)
    entity = commercial_result.get("subscription")
    if not isinstance(entity, SubscriptionEntity):
        _raise(
            SubscriptionActiveEntitlementCompositionLifecycleError,
            "D22B3_P42_SUBSCRIPTION_RESULT_INVALID",
        )
    return entity


def _issuance_idempotency(operation: str, entity: SubscriptionEntity) -> str:
    """Derive a bounded replay key from resulting immutable lifecycle evidence."""
    if not entity.audit_trail:
        _raise(
            SubscriptionActiveEntitlementCompositionLifecycleError,
            "D22B3_P42_LIFECYCLE_AUDIT_REQUIRED",
        )
    latest = entity.audit_trail[-1]
    expected = {
        "create": AuditAction.CREATE,
        "resume": AuditAction.RESUME,
        "reactivate": AuditAction.REACTIVATE,
    }[operation]
    if latest.action is not expected or not latest.proof_hash or not entity.proof_hash:
        _raise(
            SubscriptionActiveEntitlementCompositionLifecycleError,
            "D22B3_P42_LIFECYCLE_COORDINATE_INVALID",
        )
    material = json.dumps(
        {
            "namespace": IDEMPOTENCY_NAMESPACE,
            "operation": operation,
            "tenant_id": entity.tenant_id,
            "subscription_id": entity.subscription_id,
            "subscription_create_idempotency": entity.idempotency_key,
            "subscription_proof_hash": entity.proof_hash,
            "audit_action": latest.action.value,
            "audit_timestamp": latest.timestamp.isoformat(),
            "audit_proof_hash": latest.proof_hash,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    digest = hashlib.sha3_512(material).hexdigest()
    prefix = f"{IDEMPOTENCY_NAMESPACE}:{operation}:"
    return prefix + digest[: 64 - len(prefix)]


def _authorization_registry(database: Any) -> TenantAuthorizationDecisionEvidenceRegistry:
    """Construct canonical IAM evidence issuance without inventing authority."""
    return TenantAuthorizationDecisionEvidenceRegistry(
        database[AUTHORIZATION_EVIDENCE_COLLECTION],
        principal_repository=PrincipalAuthorityRepository,
        membership_repository=TenantMembershipRepository,
        role_assignment_repository=RoleAssignmentRepository,
        business_role_repository=RoleAssignmentRepository,
    )


def _run(
    operation: str,
    identity: SovereignIdentity,
    *,
    payload: dict[str, Any] | None = None,
    subscription_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> SubscriptionActiveEntitlementCompositionResult:
    """Execute one bounded whole-transaction commercial/entitlement operation."""
    authority = _identity(identity)
    for attempt in range(MAX_TRANSACTION_ATTEMPTS):
        client = get_client()
        database = get_database()
        if client is None or database is None:
            _raise(SubscriptionActiveEntitlementCompositionDependencyError)
        try:
            subscriptions = database[SUBSCRIPTION_COLLECTION]
            history = database[ENTITLEMENT_HISTORY_COLLECTION]
            current = database[ENTITLEMENT_CURRENT_COLLECTION]
            authorization_registry = _authorization_registry(database)
            session_context = client.start_session()
        except Exception as error:
            _raise(
                SubscriptionActiveEntitlementCompositionDependencyError,
                cause=error,
            )
        with session_context as session:
            try:
                session.start_transaction()
                if operation == "create":
                    if payload is None:
                        _raise(SubscriptionActiveEntitlementCompositionInputError)
                    commercial = SubscriptionRegistry.create(
                        payload,
                        authority.tenant_id,
                        collection=subscriptions,
                        session=session,
                    )
                elif operation == "resume":
                    if subscription_id is None:
                        _raise(SubscriptionActiveEntitlementCompositionInputError)
                    commercial = SubscriptionRegistry.resume(
                        subscription_id,
                        authority.tenant_id,
                        metadata,
                        collection=subscriptions,
                        session=session,
                    )
                else:
                    if subscription_id is None:
                        _raise(SubscriptionActiveEntitlementCompositionInputError)
                    commercial = SubscriptionRegistry.reactivate(
                        subscription_id,
                        authority.tenant_id,
                        metadata,
                        collection=subscriptions,
                        session=session,
                    )
                entity = _subscription(commercial)
                applicable = (
                    entity.status is SubscriptionStatus.ACTIVE
                    and LEGAL_FEATURE in entity.plan_features
                )
                issuance: TenantProductEntitlementIssuanceResult | None = None
                if applicable:
                    try:
                        issuance = issue_tenant_product_entitlement(
                            identity=authority,
                            product_id=TenantProductId.LEGAL_OPERATIONS,
                            idempotency_key=_issuance_idempotency(operation, entity),
                            occurred_at=datetime.now(timezone.utc),
                            subscription_collection=subscriptions,
                            entitlement_history_collection=history,
                            entitlement_current_collection=current,
                            authorization_evidence_registry=authorization_registry,
                            session=session,
                            subscription_registry=SubscriptionRegistry,
                        )
                    except TenantProductEntitlementIssuanceOrchestratorError as error:
                        _raise(
                            SubscriptionActiveEntitlementCompositionIssuanceError,
                            cause=error,
                        )
                session.commit_transaction()
                return SubscriptionActiveEntitlementCompositionResult(
                    commercial_result=dict(commercial),
                    subscription=entity,
                    legal_entitlement_applicable=applicable,
                    entitlement_issuance_result=issuance,
                )
            except Exception as error:
                if _has_label(error, "UnknownTransactionCommitResult"):
                    _abort_if_active(session)
                    _raise(
                        SubscriptionActiveEntitlementCompositionUnknownCommitError,
                        cause=error,
                    )
                _abort_if_active(session)
                if _write_conflict(error):
                    if attempt + 1 < MAX_TRANSACTION_ATTEMPTS:
                        continue
                    _raise(
                        SubscriptionActiveEntitlementCompositionRetryExhaustedError,
                        cause=error,
                    )
                if isinstance(error, SubscriptionActiveEntitlementCompositionServiceError):
                    raise
                if isinstance(error, SubscriptionRegistryError):
                    _raise(
                        SubscriptionActiveEntitlementCompositionLifecycleError,
                        cause=error,
                    )
                _raise(
                    SubscriptionActiveEntitlementCompositionLifecycleError,
                    cause=error,
                )
    _raise(SubscriptionActiveEntitlementCompositionRetryExhaustedError)


class SubscriptionActiveEntitlementCompositionService:
    """Public P42 transaction owner for create/resume/reactivate composition.

    Tenant and principal authority are explicit through ``SovereignIdentity``.
    Public callers cannot supply product, session, transaction, database or
    financial authority.
    """

    @staticmethod
    def create(
        payload: dict[str, Any],
        identity: SovereignIdentity,
    ) -> SubscriptionActiveEntitlementCompositionResult:
        """Create commercial truth and conditionally issue Legal entitlement."""
        if not isinstance(payload, dict):
            _raise(SubscriptionActiveEntitlementCompositionInputError)
        return _run("create", identity, payload=dict(payload))

    @staticmethod
    def resume(
        subscription_id: str,
        metadata: dict[str, Any] | None,
        identity: SovereignIdentity,
    ) -> SubscriptionActiveEntitlementCompositionResult:
        """Resume PAUSED commercial truth and conditionally issue Legal entitlement."""
        identifier = _text(subscription_id, "D22B3_P42_SUBSCRIPTION_ID_INVALID")
        if metadata is not None and not isinstance(metadata, dict):
            _raise(SubscriptionActiveEntitlementCompositionInputError)
        return _run("resume", identity, subscription_id=identifier, metadata=metadata)

    @staticmethod
    def reactivate(
        subscription_id: str,
        metadata: dict[str, Any] | None,
        identity: SovereignIdentity,
    ) -> SubscriptionActiveEntitlementCompositionResult:
        """Reactivate CANCELLED truth and conditionally issue Legal entitlement."""
        identifier = _text(subscription_id, "D22B3_P42_SUBSCRIPTION_ID_INVALID")
        if metadata is not None and not isinstance(metadata, dict):
            _raise(SubscriptionActiveEntitlementCompositionInputError)
        return _run(
            "reactivate",
            identity,
            subscription_id=identifier,
            metadata=metadata,
        )


__all__ = [
    "SubscriptionActiveEntitlementCompositionDependencyError",
    "SubscriptionActiveEntitlementCompositionInputError",
    "SubscriptionActiveEntitlementCompositionIssuanceError",
    "SubscriptionActiveEntitlementCompositionLifecycleError",
    "SubscriptionActiveEntitlementCompositionResult",
    "SubscriptionActiveEntitlementCompositionRetryExhaustedError",
    "SubscriptionActiveEntitlementCompositionService",
    "SubscriptionActiveEntitlementCompositionServiceError",
    "SubscriptionActiveEntitlementCompositionUnknownCommitError",
    "VERSION",
]

# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: subscription_active_entitlement_composition_service.py
# VERSION: v1.0.0-D22B3-P42-SUBSCRIPTION-ACTIVE-ENTITLEMENT-COMPOSITION-SERVICE
# AUTHORITY BOUNDARY: transaction composition of subscription lifecycle and positive Legal Operations entitlement only
# TENANT POSTURE: exact SovereignIdentity tenant/principal scope and one active session
# FAIL-CLOSED POSTURE: invalid input, dependency, lifecycle, issuance, retry exhaustion and uncertain commit reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
