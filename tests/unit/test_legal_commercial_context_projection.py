"""Direct certificate for the Legal commercial-context projection."""
from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.saas.domain.subscription import (
    BillingFrequency,
    PlanTiers,
    SubscriptionEntity,
    SubscriptionStatus,
)
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
)
from tools.eos.saas.entitlement import legal_commercial_context_projection as projection
from tools.eos.saas.entitlement.product_catalogue import TenantProductId


TENANT = "tenant-legal-commercial-a"


def availability(
    *,
    active: bool = True,
    state: TenantProductEntitlementState | None = (
        TenantProductEntitlementState.ACTIVE
    ),
) -> SimpleNamespace:
    return SimpleNamespace(
        tenant_id=TENANT,
        product_id=TenantProductId.LEGAL_OPERATIONS,
        workspace_key="legal-operations",
        entitlement_id="tpe-legal-a",
        lifecycle_state=state,
        available=active,
    )


def subscription(
    *,
    tenant_id: str = TENANT,
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
    features: tuple[str, ...] = ("legal.core",),
    plan: PlanTiers = PlanTiers.PROFESSIONAL,
    frequency: BillingFrequency = BillingFrequency.MONTHLY,
    amount: float = 1200.0,
) -> SubscriptionEntity:
    now = datetime(2026, 10, 1, tzinfo=timezone.utc)
    return SubscriptionEntity(
        tenant_id=tenant_id,
        plan_id="WILSYPLAN-LEGAL-PRO",
        plan=plan,
        plan_name="Legal Professional",
        plan_features=features,
        plan_catalogue_version=7,
        amount=amount,
        currency="ZAR",
        billing_frequency=frequency,
        start_date=now,
        current_period_start=now,
        current_period_end=datetime(2026, 11, 1, tzinfo=timezone.utc),
        idempotency_key="commercial-context-cert",
        subscription_id="WILSYSUB-LEGAL-A",
        status=status,
    )


def invoke(
    monkeypatch: pytest.MonkeyPatch,
    *,
    available_value: Any | None = None,
    subscriptions: tuple[SubscriptionEntity, ...] = (),
) -> projection.LegalCommercialContextProjection:
    monkeypatch.setattr(
        projection,
        "resolve_legal_product_availability",
        lambda *_a, **_k: (
            available_value
            if available_value is not None
            else availability()
        ),
    )
    monkeypatch.setattr(
        projection.SubscriptionRegistry,
        "list_entities",
        lambda *_a, **_k: subscriptions,
    )
    return projection.resolve_legal_commercial_context(
        TENANT,
        object(),
        object(),
        object(),
        session=object(),
    )


def test_active_legal_subscription_projects_canonical_commercial_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = invoke(
        monkeypatch,
        subscriptions=(subscription(),),
    )
    assert result.product_id is TenantProductId.LEGAL_OPERATIONS
    assert result.product_available is True
    assert result.subscription_id == "WILSYSUB-LEGAL-A"
    assert result.plan_id == "WILSYPLAN-LEGAL-PRO"
    assert result.plan_tier is PlanTiers.PROFESSIONAL
    assert result.plan_name == "Legal Professional"
    assert result.plan_features == ("legal.core",)
    assert result.plan_catalogue_version == 7
    assert result.amount == 1200.0
    assert result.currency == "ZAR"
    assert result.billing_frequency is BillingFrequency.MONTHLY
    assert result.monthly_equivalent_amount == 1200.0


@pytest.mark.parametrize(
    ("frequency", "amount", "monthly"),
    [
        (BillingFrequency.MONTHLY, 1200.0, 1200.0),
        (BillingFrequency.QUARTERLY, 3600.0, 1200.0),
        (BillingFrequency.ANNUAL, 14400.0, 1200.0),
    ],
)
def test_monthly_equivalent_is_server_derived(
    monkeypatch: pytest.MonkeyPatch,
    frequency: BillingFrequency,
    amount: float,
    monthly: float,
) -> None:
    result = invoke(
        monkeypatch,
        subscriptions=(
            subscription(
                frequency=frequency,
                amount=amount,
            ),
        ),
    )
    assert result.monthly_equivalent_amount == monthly


def test_lawful_absence_requires_both_sources_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = invoke(
        monkeypatch,
        available_value=availability(active=False, state=None),
        subscriptions=(),
    )
    assert result.product_available is False
    assert result.subscription_id is None
    assert result.plan_id is None
    assert result.amount is None


def test_active_entitlement_without_subscription_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(
        projection.LegalCommercialContextProjectionError,
        match="LEGAL_COMMERCIAL_ENTITLEMENT_WITHOUT_ACTIVE_SUBSCRIPTION",
    ):
        invoke(monkeypatch, subscriptions=())


def test_active_subscription_without_entitlement_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(
        projection.LegalCommercialContextProjectionError,
        match="LEGAL_COMMERCIAL_ACTIVE_SUBSCRIPTION_WITHOUT_ENTITLEMENT",
    ):
        invoke(
            monkeypatch,
            available_value=availability(
                active=False,
                state=TenantProductEntitlementState.SUSPENDED,
            ),
            subscriptions=(subscription(),),
        )


def test_multiple_active_legal_subscriptions_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(
        projection.LegalCommercialContextProjectionError,
        match="LEGAL_COMMERCIAL_ACTIVE_SUBSCRIPTION_AMBIGUOUS",
    ):
        invoke(
            monkeypatch,
            subscriptions=(
                subscription(),
                subscription(amount=1300.0),
            ),
        )


def test_non_legal_or_inactive_subscriptions_do_not_become_legal_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = invoke(
        monkeypatch,
        available_value=availability(active=False, state=None),
        subscriptions=(
            subscription(
                status=SubscriptionStatus.PAUSED,
            ),
            subscription(
                features=("crm.core",),
            ),
        ),
    )
    assert result.product_available is False
    assert result.subscription_id is None


def test_foreign_subscription_tenant_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(
        projection.LegalCommercialContextProjectionError,
        match="LEGAL_COMMERCIAL_SUBSCRIPTION_TENANT_MISMATCH",
    ):
        invoke(
            monkeypatch,
            subscriptions=(
                subscription(tenant_id="tenant-foreign"),
            ),
        )


def test_projection_is_immutable_and_bounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = invoke(
        monkeypatch,
        subscriptions=(subscription(),),
    )
    assert {field.name for field in fields(result)} == {
        "tenant_id",
        "product_id",
        "workspace_key",
        "entitlement_id",
        "entitlement_state",
        "product_available",
        "subscription_id",
        "subscription_status",
        "plan_id",
        "plan_tier",
        "plan_name",
        "plan_features",
        "plan_catalogue_version",
        "amount",
        "currency",
        "billing_frequency",
        "monthly_equivalent_amount",
        "current_period_end",
    }
    with pytest.raises(FrozenInstanceError):
        result.product_available = False  # type: ignore[misc]


def test_client_cannot_supply_product_plan_price_or_entitlement_selector() -> None:
    import inspect

    parameters = inspect.signature(
        projection.resolve_legal_commercial_context
    ).parameters
    forbidden = {
        "product_id",
        "entitlement_id",
        "subscription_id",
        "plan_id",
        "plan",
        "price",
        "amount",
        "currency",
        "billing_frequency",
        "feature",
    }
    assert forbidden.isdisjoint(parameters)


def test_projection_contains_no_http_iam_or_payment_execution_authority() -> None:
    from pathlib import Path

    source = Path(projection.__file__).read_text(encoding="utf-8")
    forbidden = (
        "APIRouter",
        "HTTPException",
        "RequireTenantAuthorization",
        "payment_method",
        "execute_payment",
        "def settle(",
        "settle_payment(",
        "execute_settlement(",
        "authorize_settlement(",
        "commit_transaction",
        "start_transaction",
        "abort_transaction",
        "TenantProductId.CRM",
        "TenantProductId.BILLING",
        "TenantProductId.HR",
    )
    assert not [token for token in forbidden if token in source]


# ARTIFACT: test_legal_commercial_context_projection.py
# PRODUCT: LEGAL_OPERATIONS
# CLIENT PLAN INFERENCE: FORBIDDEN
# PAYMENT EXECUTION AUTHORITY: NONE
