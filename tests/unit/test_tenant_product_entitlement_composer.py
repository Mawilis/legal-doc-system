"""Direct certificate for the D22B3 tenant-product entitlement composer.

TITLE: Tenant Product Entitlement Composer Direct Certificate
VERSION: v1.0.0-D22B3-TENANT-PRODUCT-ENTITLEMENT-COMPOSER-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify deterministic lineage, canonical commercial proof, derived
         evidence, lifecycle replay/closure and caller transaction ownership.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_product_entitlement_composer.py
COLLABORATION / OWNERSHIP: Bounded dependency doubles exercise D22B3 composition;
                            real Mongo is certified separately.
CERTIFICATION / UPDATE DATE: 2026-10-09
CHANGELOG: v1.0.0-D22B3-TENANT-PRODUCT-ENTITLEMENT-COMPOSER-CERT establishes
           adversarial coverage for all positive, replay and fail-closed paths.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic tenants and evidence only.
TENANT BOUNDARY: Every fake read records exact tenant and caller session.
AUTHORITY BOUNDARY: Direct composer semantics only; no external mutation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import inspect
import re
from typing import Any

import pytest

from tools.eos.saas.domain.subscription import (
    BillingFrequency,
    PlanTiers,
    SubscriptionEntity,
    SubscriptionStatus,
)
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlement,
    TenantProductEntitlementState,
    create_tenant_product_entitlement,
)
from tools.eos.saas.entitlement import tenant_product_entitlement_composer as composer
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    TenantProductEntitlementPersistenceOutcome,
    TenantProductEntitlementPersistenceResult,
    TenantProductEntitlementRegistryNotFoundError,
)


NOW = datetime(2026, 10, 9, 10, 0, tzinfo=timezone.utc)


class Session:
    """Minimal caller-owned active transaction marker."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


def subscription(
    *,
    tenant_id: str = "tenant-a",
    subscription_id: str = "subscription-a",
    features: tuple[str, ...] = ("legal.core",),
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
    plan_id: str = "plan-a",
    catalogue_version: int = 1,
) -> SubscriptionEntity:
    """Build canonical immutable subscription evidence."""
    return SubscriptionEntity(
        tenant_id=tenant_id,
        plan_id=plan_id,
        plan=PlanTiers.PROFESSIONAL,
        amount=100.0,
        currency="ZAR",
        billing_frequency=BillingFrequency.MONTHLY,
        start_date=NOW,
        current_period_start=NOW,
        current_period_end=NOW + timedelta(days=30),
        idempotency_key=f"idempotency-{subscription_id}",
        subscription_id=subscription_id,
        plan_features=features,
        plan_catalogue_version=catalogue_version,
        status=status,
        seal_nonce=f"seal-{subscription_id}",
    )


class Registry:
    """Exact SubscriptionRegistry list seam double."""

    items: tuple[SubscriptionEntity, ...] = ()
    calls: list[tuple[str | None, object, object]] = []

    @classmethod
    def list_entities(
        cls,
        tenant_id_header: str | None = None,
        *,
        collection: object = None,
        session: object = None,
    ) -> tuple[SubscriptionEntity, ...]:
        cls.calls.append((tenant_id_header, collection, session))
        return cls.items


def invoke(**changes: object) -> composer.TenantProductEntitlementCompositionResult:
    """Invoke the public composer with explicit inert collection sentinels."""
    values: dict[str, Any] = {
        "tenant_id": "tenant-a",
        "product_id": TenantProductId.LEGAL_OPERATIONS,
        "occurred_at": NOW,
        "subscription_collection": object(),
        "entitlement_history_collection": object(),
        "entitlement_current_collection": object(),
        "session": Session(),
        "subscription_registry": Registry,
    }
    values.update(changes)
    return composer.compose_tenant_product_entitlement(**values)


def install_flow(
    monkeypatch: pytest.MonkeyPatch,
    *,
    current: TenantProductEntitlement | None = None,
) -> list[tuple[str, object]]:
    """Install bounded D22B2 doubles and return recorded mutations."""
    calls: list[tuple[str, object]] = []

    def get(*_: object, **__: object) -> TenantProductEntitlement:
        if current is None:
            raise TenantProductEntitlementRegistryNotFoundError()
        return current

    def create(
        value: TenantProductEntitlement,
        *_: object,
        **__: object,
    ) -> TenantProductEntitlementPersistenceResult:
        calls.append(("create", value))
        return TenantProductEntitlementPersistenceResult(
            TenantProductEntitlementPersistenceOutcome.CREATED,
            value,
        )

    def activate(*_: object, **kwargs: object) -> TenantProductEntitlementPersistenceResult:
        calls.append(("transition", dict(kwargs)))
        base = current
        if base is None:
            base = calls[0][1]
        assert isinstance(base, TenantProductEntitlement)
        transitioned = base.transition(
            TenantProductEntitlementState.ACTIVE,
            expected_revision=base.lifecycle_revision,
            evidence_reference=str(kwargs["evidence_reference"]),
            evidence_fingerprint=str(kwargs["evidence_fingerprint"]),
            occurred_at=kwargs["occurred_at"],  # type: ignore[arg-type]
        )
        return TenantProductEntitlementPersistenceResult(
            TenantProductEntitlementPersistenceOutcome.TRANSITIONED,
            transitioned,
        )

    monkeypatch.setattr(composer, "get_current", get)
    monkeypatch.setattr(composer, "create_or_replay", create)
    monkeypatch.setattr(composer, "transition", activate)
    return calls


def test_deterministic_entitlement_identity_contract() -> None:
    """Exact tenant/product canonical JSON produces stable lowercase SHA3 ID."""
    first = composer.derive_tenant_product_entitlement_id(
        "tenant-a", TenantProductId.LEGAL_OPERATIONS
    )
    assert first.startswith("tpe-")
    assert re.fullmatch(r"tpe-[0-9a-f]{128}", first)
    assert first == composer.derive_tenant_product_entitlement_id(
        "tenant-a", TenantProductId.LEGAL_OPERATIONS
    )
    assert first != composer.derive_tenant_product_entitlement_id(
        "tenant-b", TenantProductId.LEGAL_OPERATIONS
    )
    assert first != composer.derive_tenant_product_entitlement_id(
        "tenant-a", TenantProductId.CRM
    )


def test_public_composer_has_no_entitlement_or_subscription_identity_injection() -> None:
    """Caller supplies neither entitlement ID nor selected subscription ID."""
    parameters = inspect.signature(
        composer.compose_tenant_product_entitlement
    ).parameters
    assert "entitlement_id" not in parameters
    assert "subscription_id" not in parameters
    with pytest.raises(TypeError):
        invoke(entitlement_id="caller-injected")


@pytest.mark.parametrize(
    "product_id",
    [TenantProductId.CRM, TenantProductId.BILLING, TenantProductId.HR, "UNKNOWN"],
)
def test_only_legal_operations_is_operationally_composable(product_id: object) -> None:
    """CRM duplicate truth, Billing, HR and unknown products reject."""
    Registry.items = (subscription(),)
    with pytest.raises(composer.TenantProductEntitlementComposerInputError):
        invoke(product_id=product_id)


@pytest.mark.parametrize(
    ("items", "code"),
    [
        ((), "D22B3_ACTIVE_SUBSCRIPTION_NOT_FOUND"),
        (
            (subscription(subscription_id="one"), subscription(subscription_id="two")),
            "D22B3_ACTIVE_SUBSCRIPTION_AMBIGUOUS",
        ),
        (
            (subscription(features=("other.feature",)),),
            "D22B3_COMMERCIAL_FEATURE_ABSENT",
        ),
    ],
)
def test_invalid_commercial_cardinality_or_feature_causes_no_writes(
    monkeypatch: pytest.MonkeyPatch,
    items: tuple[SubscriptionEntity, ...],
    code: str,
) -> None:
    """Zero/multiple ACTIVE or missing legal.core reject before D22B2 access."""
    Registry.items = items
    monkeypatch.setattr(
        composer,
        "get_current",
        lambda *_args, **_kwargs: pytest.fail("entitlement read occurred"),
    )
    with pytest.raises(composer.TenantProductEntitlementComposerError) as raised:
        invoke()
    assert raised.value.code == code


def test_invalid_canonical_subscription_proof_rejects_before_writes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A SHA3-shaped but non-canonical proof cannot authorize composition."""
    Registry.items = (replace(subscription(), proof_hash="f" * 128),)
    monkeypatch.setattr(
        composer,
        "get_current",
        lambda *_args, **_kwargs: pytest.fail("entitlement read occurred"),
    )
    with pytest.raises(composer.TenantProductEntitlementComposerCommercialError) as raised:
        invoke()
    assert raised.value.code == "D22B3_SUBSCRIPTION_PROOF_INVALID"


def test_no_current_creates_pending_then_activates_with_server_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exact commercial proof yields revision zero then ACTIVE revision one."""
    Registry.items = (subscription(),)
    calls = install_flow(monkeypatch)
    result = invoke()
    assert result.outcome is composer.TenantProductEntitlementCompositionOutcome.COMPOSED
    assert result.creation_outcome is TenantProductEntitlementPersistenceOutcome.CREATED
    assert result.activation_outcome is TenantProductEntitlementPersistenceOutcome.TRANSITIONED
    assert result.entitlement.lifecycle_state is TenantProductEntitlementState.ACTIVE
    assert result.entitlement.lifecycle_revision == 1
    pending = calls[0][1]
    assert isinstance(pending, TenantProductEntitlement)
    assert pending.lifecycle_state is TenantProductEntitlementState.PENDING_SOURCE
    assert pending.entitlement_id == composer.derive_tenant_product_entitlement_id(
        "tenant-a", TenantProductId.LEGAL_OPERATIONS
    )
    transition_call = calls[1][1]
    assert isinstance(transition_call, dict)
    assert transition_call["occurred_at"] == NOW
    assert pending.source_evidence_fingerprint != transition_call["evidence_fingerprint"]
    assert pending.source_evidence_reference.startswith("tpe-source:subscription-a:")
    assert str(transition_call["evidence_reference"]).startswith(
        "tpe-activation:subscription-a:"
    )


def test_subscription_coordinates_change_evidence_not_lineage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Subscription/plan proof changes cannot fork tenant-product identity."""
    captured: list[TenantProductEntitlement] = []
    for item in (
        subscription(subscription_id="one", plan_id="plan-one", catalogue_version=1),
        subscription(subscription_id="two", plan_id="plan-two", catalogue_version=2),
    ):
        Registry.items = (item,)
        calls = install_flow(monkeypatch)
        invoke()
        pending = calls[0][1]
        assert isinstance(pending, TenantProductEntitlement)
        captured.append(pending)
    assert captured[0].entitlement_id == captured[1].entitlement_id
    assert captured[0].source_evidence_fingerprint != captured[1].source_evidence_fingerprint


def test_exact_pending_is_activated_without_second_create(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exact pending currentness advances through its own current revision."""
    Registry.items = (subscription(),)
    initial_calls = install_flow(monkeypatch)
    invoke()
    pending = initial_calls[0][1]
    assert isinstance(pending, TenantProductEntitlement)
    calls = install_flow(monkeypatch, current=pending)
    result = invoke()
    assert [name for name, _ in calls] == ["transition"]
    assert result.outcome is composer.TenantProductEntitlementCompositionOutcome.PENDING_ACTIVATED


def test_exact_active_is_zero_write_replay(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exact ACTIVE currentness returns replay without illegal ACTIVE transition."""
    Registry.items = (subscription(),)
    first_calls = install_flow(monkeypatch)
    active = invoke().entitlement
    calls = install_flow(monkeypatch, current=active)
    result = invoke()
    assert calls == []
    assert result.exact_active_replay is True
    assert result.outcome is composer.TenantProductEntitlementCompositionOutcome.ACTIVE_REPLAY


@pytest.mark.parametrize(
    "state",
    [TenantProductEntitlementState.SUSPENDED, TenantProductEntitlementState.REVOKED],
)
def test_terminal_lifecycle_cannot_be_resurrected(
    monkeypatch: pytest.MonkeyPatch,
    state: TenantProductEntitlementState,
) -> None:
    """Suspended and revoked lineages reject without creating a second ID."""
    Registry.items = (subscription(),)
    first_calls = install_flow(monkeypatch)
    active = invoke().entitlement
    terminal = active.transition(
        state,
        expected_revision=1,
        evidence_reference=f"terminal-{state.value}",
        evidence_fingerprint="f" * 128,
        occurred_at=NOW,
    )
    calls = install_flow(monkeypatch, current=terminal)
    with pytest.raises(composer.TenantProductEntitlementComposerConflictError):
        invoke()
    assert calls == []


def test_divergent_pending_and_active_evidence_reject(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Source or activation drift can never be hidden as replay success."""
    Registry.items = (subscription(),)
    first_calls = install_flow(monkeypatch)
    active = invoke().entitlement
    pending = first_calls[0][1]
    assert isinstance(pending, TenantProductEntitlement)
    divergent_pending = replace(
        pending,
        source_evidence_reference="different-source",
        fingerprint="",
    )
    install_flow(monkeypatch, current=divergent_pending)
    with pytest.raises(composer.TenantProductEntitlementComposerConflictError) as source:
        invoke()
    assert source.value.code == "D22B3_CURRENT_SOURCE_DIVERGENCE"
    divergent_active = replace(
        active,
        activation_evidence_reference="different-activation",
        fingerprint="",
    )
    install_flow(monkeypatch, current=divergent_active)
    with pytest.raises(composer.TenantProductEntitlementComposerConflictError) as activation:
        invoke()
    assert activation.value.code == "D22B3_ACTIVE_ACTIVATION_DIVERGENCE"


def test_time_and_transaction_fail_before_authoritative_reads() -> None:
    """Naive time and inactive transaction never reach subscription authority."""
    Registry.items = (subscription(),)
    Registry.calls = []
    with pytest.raises(composer.TenantProductEntitlementComposerTransactionRequiredError):
        invoke(session=Session(False))
    with pytest.raises(composer.TenantProductEntitlementComposerInputError):
        invoke(occurred_at=NOW.replace(tzinfo=None))
    assert Registry.calls == []


def test_transaction_is_propagated_and_never_owned(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exact caller session reaches subscription and D22B2 without lifecycle APIs."""
    Registry.items = (subscription(),)
    Registry.calls = []
    session = Session()
    install_flow(monkeypatch)
    invoke(session=session)
    assert Registry.calls[0][2] is session
    source = inspect.getsource(composer)
    assert "start_transaction(" not in source
    assert "commit_transaction(" not in source
    assert "abort_transaction(" not in source
    assert "datetime.now(" not in source


def test_source_imports_exclude_forbidden_authorities_and_result_is_immutable() -> None:
    """No classification, IAM, router/client, payment or reconciliation dependency."""
    tree = ast.parse(inspect.getsource(composer))
    modules = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    forbidden = ("business_classification", "iam", "router", "client", "payment")
    assert all(part not in module.casefold() for module in modules for part in forbidden)
    assert "reconcile" not in set(composer.__all__)
    Registry.items = (subscription(),)
    value = composer.TenantProductEntitlementCompositionResult(
        composer.TenantProductEntitlementCompositionOutcome.ACTIVE_REPLAY,
        create_tenant_product_entitlement(
            tenant_id="tenant-a",
            entitlement_id="entitlement-a",
            product_id=TenantProductId.LEGAL_OPERATIONS,
            source_evidence_reference="source",
            source_evidence_fingerprint="a" * 128,
        ),
        None,
        None,
        True,
    )
    with pytest.raises(FrozenInstanceError):
        value.exact_active_replay = False  # type: ignore[misc]


# ARTIFACT: test_tenant_product_entitlement_composer.py
# VERSION: v1.0.0-D22B3-TENANT-PRODUCT-ENTITLEMENT-COMPOSER-CERT
# AUTHORITY BOUNDARY: direct composer behavior only; no external commercial, IAM, route or financial authority
# TENANT POSTURE: synthetic exact-tenant dependency calls only
# FAIL-CLOSED POSTURE: cardinality, proof, evidence divergence, terminal lifecycle and transaction absence reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
