"""WILSY OS positive tenant-product entitlement issuance orchestration.

TITLE: Tenant Product Entitlement Issuance Orchestrator
VERSION: v1.0.0-D22B3-P25-POSITIVE-ISSUANCE-ORCHESTRATOR
AUTHORITY: Wilsy OS Core Governance
EPITOME: Bind an active sovereign identity to durable issuance authorization
         evidence before invoking the sealed Legal Operations composer.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/entitlement/tenant_product_entitlement_issuance_orchestrator.py
COLLABORATION / OWNERSHIP: SovereignIdentity owns authenticated tenant/principal
                            projection; IAM owns authorization evidence; D22B3
                            composer owns subscription-backed entitlement truth.
CERTIFICATION / UPDATE DATE: 2026-10-09
CHANGELOG: v1.0.0-D22B3-P25-POSITIVE-ISSUANCE-ORCHESTRATOR establishes exact
           ENTERPRISE_ADMIN issuance evidence, deterministic replay namespaces,
           strict evidence correlation and caller-session propagation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Accepts no token, credential, caller tenant,
                             principal, role, authorization ID or provenance.
TENANT BOUNDARY: Tenant and principal derive only from one active identity;
                 every durable operation receives the same caller session.
AUTHORITY BOUNDARY: Authorization evidence is necessary but does not replace
                    the sealed composer's canonical commercial-source checks.
COMMERCIAL-SOURCE BOUNDARY: Subscription, plan, feature mapping and catalogue
                            provenance remain exclusively composer-derived.
TRANSACTION BOUNDARY: Caller owns session, transaction, commit, abort, unknown-
                      commit handling and whole-transaction retry.
FINANCIAL AUTHORITY BOUNDARY: No payment, execution or settlement authority;
                              Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Invalid identity/input, absent transaction, denial,
                         divergent evidence, composer failure and uncertainty reject.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
from typing import Any, Final, NoReturn

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization_decision_evidence import (
    TenantAuthorizationDecisionEvidence,
)
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceAuthorizationDeniedError,
    TenantAuthorizationDecisionEvidenceConflictError,
    TenantAuthorizationDecisionEvidencePersistenceError,
    TenantAuthorizationDecisionEvidenceRegistryError,
    TenantAuthorizationDecisionEvidenceTransactionRequiredError,
)
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
    TenantProductEntitlementComposerError,
    TenantProductEntitlementCompositionResult,
    compose_tenant_product_entitlement,
    derive_tenant_product_entitlement_id,
)


VERSION: Final[str] = "v1.0.0-D22B3-P25-POSITIVE-ISSUANCE-ORCHESTRATOR"
OPERATION: Final[str] = "tenant_product_entitlement_issue"
PERMISSION: Final[str] = "tenant_product_entitlement:issue"
AUTHORIZATION_ROLE: Final[str] = "ENTERPRISE_ADMIN"
ALLOWED_BUSINESS_ROLES: Final[frozenset[str]] = frozenset(
    {"tenant_owner", "tenant_admin", "tenant_manager"}
)
AUTHORIZATION_SUBJECT_NAMESPACE: Final[str] = "tenant-product-entitlement"
AUTHORIZATION_IDEMPOTENCY_NAMESPACE: Final[str] = (
    "tenant-product-entitlement-authorization"
)
_MAX_CALLER_IDEMPOTENCY_LENGTH: Final[int] = 64


class TenantProductEntitlementIssuanceOrchestratorError(RuntimeError):
    """Base bounded issuance failure with no supplied data in its message."""

    def __init__(self, code: str) -> None:
        """Create a stable fail-closed code while causes remain internal."""
        self.code = code
        super().__init__(code)


class TenantProductEntitlementIssuanceTransactionRequiredError(
    TenantProductEntitlementIssuanceOrchestratorError
):
    """An already-active caller-owned transaction was not supplied."""


class TenantProductEntitlementIssuanceInputError(
    TenantProductEntitlementIssuanceOrchestratorError
):
    """Identity, product, replay key or trusted orchestration input is invalid."""


class TenantProductEntitlementIssuanceAuthorizationError(
    TenantProductEntitlementIssuanceOrchestratorError
):
    """Authorization was denied, conflicted or returned divergent evidence."""


class TenantProductEntitlementIssuanceEvidenceError(
    TenantProductEntitlementIssuanceOrchestratorError
):
    """Authorization evidence issuance or hydration is unavailable/corrupt."""


class TenantProductEntitlementIssuanceCompositionError(
    TenantProductEntitlementIssuanceOrchestratorError
):
    """The sealed commercial-source composer failed closed."""


@dataclass(frozen=True, slots=True)
class TenantProductEntitlementIssuanceResult:
    """Immutable authorization provenance plus sealed composition result.

    This value duplicates no entitlement state and grants no financial or
    transaction authority. Durability remains transaction-pending until the
    caller successfully commits.
    """

    authorization_evidence: TenantAuthorizationDecisionEvidence
    composition: TenantProductEntitlementCompositionResult


def _raise(
    error_type: type[TenantProductEntitlementIssuanceOrchestratorError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one bounded failure while retaining an optional internal cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _active_transaction(session: Any) -> Any:
    """Require caller ownership of an already-active transaction before reads."""
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _raise(
            TenantProductEntitlementIssuanceTransactionRequiredError,
            "D22B3_P25_ACTIVE_TRANSACTION_REQUIRED",
        )
    return session


def _text(name: str, value: object, *, maximum: int = 256) -> str:
    """Require exact bounded non-whitespace text without coercion or repair."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > maximum
    ):
        _raise(
            TenantProductEntitlementIssuanceInputError,
            f"D22B3_P25_{name.upper()}_INVALID",
        )
    return value


def _identity(identity: SovereignIdentity) -> tuple[str, str]:
    """Derive tenant and principal solely from an active SovereignIdentity."""
    if not isinstance(identity, SovereignIdentity):
        _raise(
            TenantProductEntitlementIssuanceInputError,
            "D22B3_P25_IDENTITY_REQUIRED",
        )
    if identity.status is not PrincipalStatus.ACTIVE:
        _raise(
            TenantProductEntitlementIssuanceInputError,
            "D22B3_P25_PRINCIPAL_INACTIVE",
        )
    return _text("tenant_id", identity.tenant_id), _text(
        "principal_id", identity.identity_id
    )


def _product(product_id: TenantProductId | str) -> TenantProductId:
    """Accept only the frozen positive Legal Operations product."""
    try:
        product = TenantProductId(product_id)
    except (TypeError, ValueError) as error:
        _raise(
            TenantProductEntitlementIssuanceInputError,
            "D22B3_P25_PRODUCT_UNKNOWN",
            error,
        )
    if product is not TenantProductId.LEGAL_OPERATIONS:
        _raise(
            TenantProductEntitlementIssuanceInputError,
            "D22B3_P25_PRODUCT_NOT_AUTHORIZED",
        )
    return product


def _authorization_fingerprint(payload: dict[str, str]) -> str:
    """Return SHA3-512 over the exact frozen seven-field canonical payload."""
    raw = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(raw).hexdigest()


def _correlate(
    evidence: TenantAuthorizationDecisionEvidence,
    *,
    tenant_id: str,
    principal_id: str,
    subject_reference: str,
    subject_evidence_fingerprint: str,
    authorization_idempotency_key: str,
) -> None:
    """Require exact evidence/request agreement before commercial composition."""
    if not isinstance(evidence, TenantAuthorizationDecisionEvidence):
        _raise(
            TenantProductEntitlementIssuanceEvidenceError,
            "D22B3_P25_AUTHORIZATION_EVIDENCE_INVALID",
        )
    exact = (
        evidence.tenant_id == tenant_id
        and evidence.principal_id == principal_id
        and evidence.operation == OPERATION
        and evidence.permission == PERMISSION
        and evidence.subject_reference == subject_reference
        and hmac.compare_digest(
            evidence.subject_evidence_fingerprint,
            subject_evidence_fingerprint,
        )
        and evidence.idempotency_key == authorization_idempotency_key
    )
    if not exact:
        _raise(
            TenantProductEntitlementIssuanceAuthorizationError,
            "D22B3_P25_AUTHORIZATION_EVIDENCE_DIVERGENCE",
        )
    if evidence.authorization_role != AUTHORIZATION_ROLE:
        _raise(
            TenantProductEntitlementIssuanceAuthorizationError,
            "D22B3_P25_AUTHORIZATION_ROLE_REQUIRED",
        )
    if evidence.business_role not in ALLOWED_BUSINESS_ROLES:
        _raise(
            TenantProductEntitlementIssuanceAuthorizationError,
            "D22B3_P25_BUSINESS_ROLE_REQUIRED",
        )


def issue_tenant_product_entitlement(
    *,
    identity: SovereignIdentity,
    product_id: TenantProductId | str,
    idempotency_key: str,
    occurred_at: Any,
    subscription_collection: Any,
    entitlement_history_collection: Any,
    entitlement_current_collection: Any,
    authorization_evidence_registry: Any,
    session: Any,
    subscription_registry: type[SubscriptionRegistry] = SubscriptionRegistry,
) -> TenantProductEntitlementIssuanceResult:
    """Authorize then compose one positive Legal entitlement atomically.

    Tenant/principal derive only from ``identity``. The caller supplies and owns
    the active transaction and all commit, abort, retry and unknown-commit
    handling. This function issues authorization evidence and invokes the sealed
    composer with that exact session; it does not execute financial activity.
    """
    tx = _active_transaction(session)
    tenant_id, principal_id = _identity(identity)
    product = _product(product_id)
    caller_idempotency_key = _text(
        "idempotency_key",
        idempotency_key,
        maximum=_MAX_CALLER_IDEMPOTENCY_LENGTH,
    )
    entitlement_id = derive_tenant_product_entitlement_id(tenant_id, product)
    subject_reference = (
        f"{AUTHORIZATION_SUBJECT_NAMESPACE}:{tenant_id}:"
        f"{product.value}:{entitlement_id}"
    )
    fingerprint = _authorization_fingerprint(
        {
            "tenant_id": tenant_id,
            "principal_id": principal_id,
            "product_id": product.value,
            "entitlement_id": entitlement_id,
            "operation": OPERATION,
            "permission": PERMISSION,
            "idempotency_key": caller_idempotency_key,
        }
    )
    authorization_idempotency_key = (
        f"{AUTHORIZATION_IDEMPOTENCY_NAMESPACE}:{entitlement_id}:"
        f"{caller_idempotency_key}"
    )
    try:
        evidence = authorization_evidence_registry.issue(
            tenant_id=tenant_id,
            principal_id=principal_id,
            operation=OPERATION,
            permission=PERMISSION,
            subject_reference=subject_reference,
            subject_evidence_fingerprint=fingerprint,
            idempotency_key=authorization_idempotency_key,
            session=tx,
        )
    except TenantAuthorizationDecisionEvidenceAuthorizationDeniedError as error:
        _raise(
            TenantProductEntitlementIssuanceAuthorizationError,
            "D22B3_P25_AUTHORIZATION_DENIED",
            error,
        )
    except TenantAuthorizationDecisionEvidenceConflictError as error:
        _raise(
            TenantProductEntitlementIssuanceAuthorizationError,
            "D22B3_P25_AUTHORIZATION_REPLAY_CONFLICT",
            error,
        )
    except TenantAuthorizationDecisionEvidenceTransactionRequiredError as error:
        _raise(
            TenantProductEntitlementIssuanceTransactionRequiredError,
            "D22B3_P25_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    except (
        TenantAuthorizationDecisionEvidencePersistenceError,
        TenantAuthorizationDecisionEvidenceRegistryError,
    ) as error:
        _raise(
            TenantProductEntitlementIssuanceEvidenceError,
            "D22B3_P25_AUTHORIZATION_EVIDENCE_UNAVAILABLE",
            error,
        )
    _correlate(
        evidence,
        tenant_id=tenant_id,
        principal_id=principal_id,
        subject_reference=subject_reference,
        subject_evidence_fingerprint=fingerprint,
        authorization_idempotency_key=authorization_idempotency_key,
    )
    try:
        composition = compose_tenant_product_entitlement(
            tenant_id=tenant_id,
            product_id=product,
            occurred_at=occurred_at,
            subscription_collection=subscription_collection,
            entitlement_history_collection=entitlement_history_collection,
            entitlement_current_collection=entitlement_current_collection,
            session=tx,
            subscription_registry=subscription_registry,
        )
    except TenantProductEntitlementComposerError as error:
        _raise(
            TenantProductEntitlementIssuanceCompositionError,
            "D22B3_P25_COMPOSITION_FAILED",
            error,
        )
    return TenantProductEntitlementIssuanceResult(evidence, composition)


__all__ = [
    "ALLOWED_BUSINESS_ROLES",
    "AUTHORIZATION_IDEMPOTENCY_NAMESPACE",
    "AUTHORIZATION_ROLE",
    "AUTHORIZATION_SUBJECT_NAMESPACE",
    "OPERATION",
    "PERMISSION",
    "TenantProductEntitlementIssuanceAuthorizationError",
    "TenantProductEntitlementIssuanceCompositionError",
    "TenantProductEntitlementIssuanceEvidenceError",
    "TenantProductEntitlementIssuanceInputError",
    "TenantProductEntitlementIssuanceOrchestratorError",
    "TenantProductEntitlementIssuanceResult",
    "TenantProductEntitlementIssuanceTransactionRequiredError",
    "VERSION",
    "issue_tenant_product_entitlement",
]

# ARTIFACT: tenant_product_entitlement_issuance_orchestrator.py
# VERSION: v1.0.0-D22B3-P25-POSITIVE-ISSUANCE-ORCHESTRATOR
# AUTHORITY BOUNDARY: exact issuance authorization evidence followed by sealed positive Legal Operations composition only
# TENANT POSTURE: tenant and principal derive solely from active SovereignIdentity and remain bound to one caller session
# FAIL-CLOSED POSTURE: invalid identity/input, transaction absence, denial, evidence divergence and composition failure reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
