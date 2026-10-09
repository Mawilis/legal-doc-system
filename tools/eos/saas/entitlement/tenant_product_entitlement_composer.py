"""WILSY OS positive tenant-product entitlement composition authority.

TITLE: Tenant Product Entitlement Composer
VERSION: v1.0.0-D22B3-TENANT-PRODUCT-ENTITLEMENT-COMPOSER
AUTHORITY: Wilsy OS Core Governance
EPITOME: Derive and persist one Legal Operations entitlement lineage from one
         exact canonical ACTIVE subscription carrying sealed legal.core truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/entitlement/tenant_product_entitlement_composer.py
COLLABORATION / OWNERSHIP: SubscriptionRegistry owns subscription truth; D22A
                            owns product identity; Product Commercial Feature
                            owns mapping metadata; D22B1 owns lifecycle; D22B2
                            owns persistence. This composer correlates them only.
CERTIFICATION / UPDATE DATE: 2026-10-09
CHANGELOG: v1.0.0-D22B3-TENANT-PRODUCT-ENTITLEMENT-COMPOSER establishes stable
           tenant/product lineage IDs, server-derived source/activation evidence,
           exact ACTIVE subscription cardinality, positive Legal composition,
           pending/active replay and terminal-lifecycle rejection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Persists only opaque canonical evidence coordinates;
                             no price, payment instrument, principal or browser data.
TENANT BOUNDARY: Every subscription read and entitlement operation is bound to
                 the exact caller-provided tenant inside one active transaction.
AUTHORITY BOUNDARY: Positive Legal Operations entitlement composition only; no
                    subscription/plan mutation, reconciliation, IAM, route,
                    classification, Branding, WILSY AI or CRM authority.
TRANSACTION BOUNDARY: Caller owns session, transaction, commit, abort and whole-
                      transaction retry. Composer requires and propagates only.
FINANCIAL AUTHORITY BOUNDARY: No pricing, payment, execution or settlement truth.
                               Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing/ambiguous subscription truth, invalid proof,
                         absent feature, divergent evidence, unsupported product,
                         terminal lifecycle, stale CAS and persistence failure reject.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Final, NoReturn

from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.domain.subscription import (
    SubscriptionEntity,
    SubscriptionStatus,
    verify_subscription_integrity,
)
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlement,
    TenantProductEntitlementState,
    create_tenant_product_entitlement,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.product_commercial_feature import (
    get_product_commercial_feature,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    TenantProductEntitlementPersistenceOutcome,
    TenantProductEntitlementRegistryError,
    TenantProductEntitlementRegistryNotFoundError,
    TenantProductEntitlementRegistryRetryRequiredError,
    create_or_replay,
    get_current,
    transition,
)


VERSION: Final[str] = "v1.0.0-D22B3-TENANT-PRODUCT-ENTITLEMENT-COMPOSER"
ENTITLEMENT_ID_NAMESPACE: Final[str] = "WILSY-TENANT-PRODUCT-ENTITLEMENT-ID/V1"
SOURCE_EVIDENCE_SCHEMA: Final[str] = "WILSY-TENANT-PRODUCT-ENTITLEMENT-SOURCE/V1"
ACTIVATION_EVIDENCE_SCHEMA: Final[str] = (
    "WILSY-TENANT-PRODUCT-ENTITLEMENT-ACTIVATION/V1"
)
_SHA3: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")


class TenantProductEntitlementComposerError(RuntimeError):
    """Base fail-closed composer failure carrying a deterministic code."""

    def __init__(self, code: str) -> None:
        """Create one governed failure without manufacturing authority."""
        self.code = code
        super().__init__(code)


class TenantProductEntitlementComposerTransactionRequiredError(
    TenantProductEntitlementComposerError
):
    """An active caller-owned transaction was not supplied."""


class TenantProductEntitlementComposerInputError(
    TenantProductEntitlementComposerError
):
    """Trusted orchestration input is malformed or unsupported."""


class TenantProductEntitlementComposerCommercialError(
    TenantProductEntitlementComposerError
):
    """Canonical subscription truth does not authorize positive composition."""


class TenantProductEntitlementComposerConflictError(
    TenantProductEntitlementComposerError
):
    """Existing lifecycle evidence conflicts with the canonical composition."""


class TenantProductEntitlementComposerRetryRequiredError(
    TenantProductEntitlementComposerError
):
    """Caller must restart the entire transaction from fresh state."""


class TenantProductEntitlementComposerPersistenceError(
    TenantProductEntitlementComposerError
):
    """A governed dependency failed without eligible retry classification."""


class TenantProductEntitlementCompositionOutcome(StrEnum):
    """Explicit final positive-composition result without commercial inference."""

    COMPOSED = "COMPOSED"
    PENDING_ACTIVATED = "PENDING_ACTIVATED"
    ACTIVE_REPLAY = "ACTIVE_REPLAY"


@dataclass(frozen=True, slots=True)
class TenantProductEntitlementCompositionResult:
    """Final entitlement plus exact persistence and activation outcomes."""

    outcome: TenantProductEntitlementCompositionOutcome
    entitlement: TenantProductEntitlement
    creation_outcome: TenantProductEntitlementPersistenceOutcome | None
    activation_outcome: TenantProductEntitlementPersistenceOutcome | None
    exact_active_replay: bool


def _raise(
    error_type: type[TenantProductEntitlementComposerError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one typed failure while preserving the dependency cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _active_transaction(session: Any) -> Any:
    """Require active caller transaction before any authoritative dependency."""
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _raise(
            TenantProductEntitlementComposerTransactionRequiredError,
            "D22B3_ACTIVE_TRANSACTION_REQUIRED",
        )
    return session


def _text(name: str, value: object) -> str:
    """Require one exact bounded non-whitespace identity."""
    if not isinstance(value, str) or not value or value != value.strip():
        _raise(
            TenantProductEntitlementComposerInputError,
            f"D22B3_{name.upper()}_INVALID",
        )
    return value


def _canonical_json(payload: dict[str, object]) -> bytes:
    """Serialize exact evidence with the frozen deterministic JSON contract."""
    return json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest(payload: dict[str, object]) -> str:
    """Return lowercase SHA3-512 for exact canonical evidence."""
    return hashlib.sha3_512(_canonical_json(payload)).hexdigest()


def derive_tenant_product_entitlement_id(
    tenant_id: str,
    product_id: TenantProductId | str,
) -> str:
    """Derive one permanent lineage ID from exact tenant and D22A product only.

    Subscription, plan, mapping, catalogue, timestamp and composer-version
    coordinates are intentionally excluded so commercial change cannot fork the
    permanent tenant/product lineage.
    """
    tenant = _text("tenant_id", tenant_id)
    try:
        product = TenantProductId(product_id)
    except (TypeError, ValueError) as error:
        _raise(
            TenantProductEntitlementComposerInputError,
            "D22B3_PRODUCT_UNKNOWN",
            error,
        )
    digest = _digest(
        {
            "namespace": ENTITLEMENT_ID_NAMESPACE,
            "product_id": product.value,
            "tenant_id": tenant,
        }
    )
    return f"tpe-{digest}"


def _occurred_at(value: object) -> datetime:
    """Require an aware trusted orchestration time and normalize it to UTC."""
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _raise(
            TenantProductEntitlementComposerInputError,
            "D22B3_OCCURRED_AT_INVALID",
        )
    return value.astimezone(timezone.utc)


def _subscription(
    tenant_id: str,
    collection: Any,
    session: Any,
    registry: type[SubscriptionRegistry],
) -> SubscriptionEntity:
    """Resolve exactly one canonical ACTIVE subscription for the tenant."""
    try:
        items = registry.list_entities(
            tenant_id,
            collection=collection,
            session=session,
        )
    except Exception as error:
        _raise(
            TenantProductEntitlementComposerPersistenceError,
            "D22B3_SUBSCRIPTION_REGISTRY_UNAVAILABLE",
            error,
        )
    active = tuple(item for item in items if item.status is SubscriptionStatus.ACTIVE)
    if not active:
        _raise(
            TenantProductEntitlementComposerCommercialError,
            "D22B3_ACTIVE_SUBSCRIPTION_NOT_FOUND",
        )
    if len(active) != 1:
        _raise(
            TenantProductEntitlementComposerCommercialError,
            "D22B3_ACTIVE_SUBSCRIPTION_AMBIGUOUS",
        )
    item = active[0]
    if (
        type(item) is not SubscriptionEntity
        or item.tenant_id != tenant_id
        or not _text("subscription_id", item.subscription_id)
        or not _text("plan_id", item.plan_id)
        or isinstance(item.plan_catalogue_version, bool)
        or not isinstance(item.plan_catalogue_version, int)
        or item.plan_catalogue_version < 1
        or not isinstance(item.proof_hash, str)
        or _SHA3.fullmatch(item.proof_hash.casefold()) is None
        or not verify_subscription_integrity(item)
    ):
        _raise(
            TenantProductEntitlementComposerCommercialError,
            "D22B3_SUBSCRIPTION_PROOF_INVALID",
        )
    return item


def _evidence(
    tenant_id: str,
    subscription: SubscriptionEntity,
    product_id: TenantProductId,
    feature_id: str,
    mapping_fingerprint: str,
    catalogue_fingerprint: str,
) -> tuple[str, str, str, str]:
    """Derive distinct deterministic source and activation evidence contracts."""
    source_payload: dict[str, object] = {
        "schema": SOURCE_EVIDENCE_SCHEMA,
        "tenant_id": tenant_id,
        "subscription_id": subscription.subscription_id,
        "plan_id": subscription.plan_id,
        "plan_catalogue_version": subscription.plan_catalogue_version,
        "subscription_proof_hash": subscription.proof_hash,
        "product_id": product_id.value,
        "commercial_feature_id": feature_id,
        "mapping_fingerprint": mapping_fingerprint,
        "product_catalogue_fingerprint": catalogue_fingerprint,
    }
    source_fingerprint = _digest(source_payload)
    source_reference = (
        f"tpe-source:{subscription.subscription_id}:{product_id.value}:"
        f"{source_fingerprint}"
    )
    activation_payload: dict[str, object] = {
        "schema": ACTIVATION_EVIDENCE_SCHEMA,
        "source_evidence_fingerprint": source_fingerprint,
        "subscription_proof_hash": subscription.proof_hash,
        "product_id": product_id.value,
        "commercial_feature_id": feature_id,
        "mapping_fingerprint": mapping_fingerprint,
        "target_lifecycle_state": TenantProductEntitlementState.ACTIVE.value,
    }
    activation_fingerprint = _digest(activation_payload)
    activation_reference = (
        f"tpe-activation:{subscription.subscription_id}:{product_id.value}:"
        f"{activation_fingerprint}"
    )
    return (
        source_reference,
        source_fingerprint,
        activation_reference,
        activation_fingerprint,
    )


def _correlates_source(
    entitlement: TenantProductEntitlement,
    *,
    tenant_id: str,
    entitlement_id: str,
    product_id: TenantProductId,
    catalogue_fingerprint: str,
    source_reference: str,
    source_fingerprint: str,
) -> bool:
    """Compare every canonical lineage and source coordinate exactly."""
    return (
        entitlement.tenant_id == tenant_id
        and entitlement.entitlement_id == entitlement_id
        and entitlement.product_id is product_id
        and hmac.compare_digest(
            entitlement.product_catalogue_fingerprint,
            catalogue_fingerprint,
        )
        and entitlement.source_evidence_reference == source_reference
        and hmac.compare_digest(
            entitlement.source_evidence_fingerprint,
            source_fingerprint,
        )
    )


def compose_tenant_product_entitlement(
    *,
    tenant_id: str,
    product_id: TenantProductId | str,
    occurred_at: datetime,
    subscription_collection: Any,
    entitlement_history_collection: Any,
    entitlement_current_collection: Any,
    session: Any,
    subscription_registry: type[SubscriptionRegistry] = SubscriptionRegistry,
) -> TenantProductEntitlementCompositionResult:
    """Compose exact positive Legal entitlement truth in caller transaction.

    The caller cannot provide subscription identity, entitlement identity or
    evidence. This function never starts, commits, aborts or retries a Mongo
    transaction and never reconciles later commercial loss.
    """
    tx = _active_transaction(session)
    tenant = _text("tenant_id", tenant_id)
    when = _occurred_at(occurred_at)
    try:
        product = TenantProductId(product_id)
    except (TypeError, ValueError) as error:
        _raise(
            TenantProductEntitlementComposerInputError,
            "D22B3_PRODUCT_UNKNOWN",
            error,
        )
    if product is not TenantProductId.LEGAL_OPERATIONS:
        _raise(
            TenantProductEntitlementComposerInputError,
            "D22B3_PRODUCT_NOT_AUTHORIZED",
        )

    mapping = get_product_commercial_feature(product)
    subscription = _subscription(
        tenant,
        subscription_collection,
        tx,
        subscription_registry,
    )
    if mapping.feature_id not in subscription.plan_features:
        _raise(
            TenantProductEntitlementComposerCommercialError,
            "D22B3_COMMERCIAL_FEATURE_ABSENT",
        )

    entitlement_id = derive_tenant_product_entitlement_id(tenant, product)
    (
        source_reference,
        source_fingerprint,
        activation_reference,
        activation_fingerprint,
    ) = _evidence(
        tenant,
        subscription,
        product,
        mapping.feature_id,
        mapping.fingerprint,
        mapping.product_catalogue_fingerprint,
    )

    try:
        current = get_current(
            tenant,
            entitlement_id,
            entitlement_history_collection,
            entitlement_current_collection,
            session=tx,
        )
    except TenantProductEntitlementRegistryNotFoundError:
        current = None
    except TenantProductEntitlementRegistryRetryRequiredError as error:
        _raise(
            TenantProductEntitlementComposerRetryRequiredError,
            "D22B3_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )
    except TenantProductEntitlementRegistryError as error:
        _raise(
            TenantProductEntitlementComposerPersistenceError,
            "D22B3_ENTITLEMENT_PERSISTENCE_FAILED",
            error,
        )

    creation_outcome: TenantProductEntitlementPersistenceOutcome | None = None
    if current is None:
        pending = create_tenant_product_entitlement(
            tenant_id=tenant,
            entitlement_id=entitlement_id,
            product_id=product,
            source_evidence_reference=source_reference,
            source_evidence_fingerprint=source_fingerprint,
        )
        try:
            created = create_or_replay(
                pending,
                entitlement_history_collection,
                entitlement_current_collection,
                session=tx,
            )
        except TenantProductEntitlementRegistryRetryRequiredError as error:
            _raise(
                TenantProductEntitlementComposerRetryRequiredError,
                "D22B3_WHOLE_TRANSACTION_RETRY_REQUIRED",
                error,
            )
        except TenantProductEntitlementRegistryError as error:
            _raise(
                TenantProductEntitlementComposerPersistenceError,
                "D22B3_ENTITLEMENT_PERSISTENCE_FAILED",
                error,
            )
        creation_outcome = created.outcome
        current = created.entitlement

    if not _correlates_source(
        current,
        tenant_id=tenant,
        entitlement_id=entitlement_id,
        product_id=product,
        catalogue_fingerprint=mapping.product_catalogue_fingerprint,
        source_reference=source_reference,
        source_fingerprint=source_fingerprint,
    ):
        _raise(
            TenantProductEntitlementComposerConflictError,
            "D22B3_CURRENT_SOURCE_DIVERGENCE",
        )

    if current.lifecycle_state is TenantProductEntitlementState.ACTIVE:
        if (
            current.activation_evidence_reference != activation_reference
            or current.activation_evidence_fingerprint is None
            or not hmac.compare_digest(
                current.activation_evidence_fingerprint,
                activation_fingerprint,
            )
        ):
            _raise(
                TenantProductEntitlementComposerConflictError,
                "D22B3_ACTIVE_ACTIVATION_DIVERGENCE",
            )
        return TenantProductEntitlementCompositionResult(
            TenantProductEntitlementCompositionOutcome.ACTIVE_REPLAY,
            current,
            creation_outcome,
            None,
            True,
        )
    if current.lifecycle_state is TenantProductEntitlementState.SUSPENDED:
        _raise(
            TenantProductEntitlementComposerConflictError,
            "D22B3_SUSPENDED_LIFECYCLE_CLOSED",
        )
    if current.lifecycle_state is TenantProductEntitlementState.REVOKED:
        _raise(
            TenantProductEntitlementComposerConflictError,
            "D22B3_REVOKED_LIFECYCLE_CLOSED",
        )
    if current.lifecycle_state is not TenantProductEntitlementState.PENDING_SOURCE:
        _raise(
            TenantProductEntitlementComposerConflictError,
            "D22B3_LIFECYCLE_INVALID",
        )

    try:
        activated = transition(
            tenant_id=tenant,
            entitlement_id=entitlement_id,
            target_state=TenantProductEntitlementState.ACTIVE,
            expected_revision=current.lifecycle_revision,
            evidence_reference=activation_reference,
            evidence_fingerprint=activation_fingerprint,
            occurred_at=when,
            history_collection=entitlement_history_collection,
            current_collection=entitlement_current_collection,
            session=tx,
        )
    except TenantProductEntitlementRegistryRetryRequiredError as error:
        _raise(
            TenantProductEntitlementComposerRetryRequiredError,
            "D22B3_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )
    except TenantProductEntitlementRegistryError as error:
        _raise(
            TenantProductEntitlementComposerPersistenceError,
            "D22B3_ENTITLEMENT_PERSISTENCE_FAILED",
            error,
        )
    outcome = (
        TenantProductEntitlementCompositionOutcome.COMPOSED
        if creation_outcome is not None
        else TenantProductEntitlementCompositionOutcome.PENDING_ACTIVATED
    )
    return TenantProductEntitlementCompositionResult(
        outcome,
        activated.entitlement,
        creation_outcome,
        activated.outcome,
        False,
    )


__all__ = [
    "ACTIVATION_EVIDENCE_SCHEMA",
    "ENTITLEMENT_ID_NAMESPACE",
    "SOURCE_EVIDENCE_SCHEMA",
    "TenantProductEntitlementComposerCommercialError",
    "TenantProductEntitlementComposerConflictError",
    "TenantProductEntitlementComposerError",
    "TenantProductEntitlementComposerInputError",
    "TenantProductEntitlementComposerPersistenceError",
    "TenantProductEntitlementComposerRetryRequiredError",
    "TenantProductEntitlementComposerTransactionRequiredError",
    "TenantProductEntitlementCompositionOutcome",
    "TenantProductEntitlementCompositionResult",
    "VERSION",
    "compose_tenant_product_entitlement",
    "derive_tenant_product_entitlement_id",
]

# ARTIFACT: tenant_product_entitlement_composer.py
# VERSION: v1.0.0-D22B3-TENANT-PRODUCT-ENTITLEMENT-COMPOSER
# AUTHORITY BOUNDARY: positive Legal Operations subscription-to-entitlement composition only; no commercial mutation, reconciliation, IAM, route or classification authority
# TENANT POSTURE: exact tenant-scoped subscription read and entitlement lineage inside one caller-owned transaction
# FAIL-CLOSED POSTURE: invalid/ambiguous commercial proof, divergent evidence, terminal lifecycle, stale CAS and persistence failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
