"""WILSY OS — Subscription catalogue-provenance domain certificate.

TITLE:
    WILSY OS Subscription Catalogue Provenance + Calendar Billing Domain Certificate

VERSION:
    v1.1.1-SUBSCRIPTION-CALENDAR-BILLING-CERT

AUTHORITY:
    Wilsy OS Core Governance

PURPOSE:
    Certify that SubscriptionEntity preserves canonical Plan catalogue evidence
    while the domain derives deterministic timezone-aware calendar billing
    coordinates without granting caller pricing or financial execution authority.

EPITOME:
    A subscription may preserve catalogue evidence; it may not become the
    catalogue authority that created that evidence.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_subscription_domain.py

OWNERSHIP / COLLABORATION:
    Python EOS SaaS domain certification.
    PlanEntity / PlanRegistry remain canonical commercial catalogue authorities.

CERTIFICATION / UPDATE DATE:
    2026-09-03

CHANGELOG:
    2026-09-03 v1.1.1-SUBSCRIPTION-CALENDAR-BILLING-CERT
        - Closes adversarial P2 coverage gaps for first-day, last-day and
          period-end proration boundary semantics.
        - Certifies a real DST-changing IANA timezone using ZoneInfo.
        - Certifies explicit December-to-January monthly and cross-year
          quarterly calendar rollover.
        - Leaves the production v1.2.0 calendar foundation unchanged.

    2026-09-03 v1.1.0-SUBSCRIPTION-CALENDAR-BILLING-CERT
        - Certifies first-of-month calendar anchoring.
        - Certifies actual 28/29/30/31-day monthly denominators.
        - Certifies leap-year quarterly and annual calendar spans.
        - Certifies timezone-aware input and timezone preservation.
        - Certifies deterministic non-monetary proration coordinates.
        - Re-runs every v1.0.0 catalogue-provenance assertion unchanged.

    2026-09-03 v1.0.0-SUBSCRIPTION-CATALOGUE-PROVENANCE-CERT
        - Certifies explicit legacy-unknown catalogue provenance.
        - Certifies positive-integer current catalogue coordinates.
        - Certifies immutable/detached feature snapshots.
        - Certifies deterministic proof binding of plan name, features and
          catalogue version.
        - Certifies serialization, invoice seed and evidence projections.

COMPLIANCE:
    POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.

SECURITY / PRIVACY POSTURE:
    Synthetic commercial values only. No production tenant or customer data.

TENANT BOUNDARY:
    This certificate tests value semantics only and grants no tenant authority.

AUTHORITY BOUNDARY:
    Domain evidence only; no authentication, permission, entitlement, catalogue
    mutation, HTTP authorization or persistence authority.

FINANCIAL AUTHORITY BOUNDARY:
    No payment authorization, release, execution or settlement.
    Kennel EOS remains exclusive.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import pytest

from tools.eos.saas.domain.subscription import (
    BillingFrequency,
    PlanTiers,
    SubscriptionEntity,
    VERSION,
    calendar_period_bounds,
    calendar_proration_coordinate,
)


TEST_VERSION = (
    "v1.1.1-SUBSCRIPTION-CALENDAR-BILLING-CERT"
)

DOMAIN_VERSION = "v1.2.0-CALENDAR-BILLING-FOUNDATION"

STAMP = datetime(
    2026,
    9,
    3,
    10,
    0,
    tzinfo=timezone.utc,
)


def _subscription(
    **changes: Any,
) -> SubscriptionEntity:
    values: dict[str, Any] = {
        "tenant_id": "TENANT-C3",
        "plan_id": "WILSYPLAN-ENTERPRISE",
        "plan": PlanTiers.ENTERPRISE,
        "amount": 499.0,
        "currency": "ZAR",
        "billing_frequency": BillingFrequency.MONTHLY,
        "start_date": STAMP,
        "current_period_start": STAMP,
        "current_period_end": datetime(
            2026,
            10,
            3,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        "idempotency_key": "C3-DOMAIN-IDEMPOTENCY",
        "subscription_id": "WILSYSUB-C3ABCDEF",
        "plan_name": "Enterprise",
        "plan_features": [
            "crm.core",
            "legal.documents",
        ],
        "plan_catalogue_version": 7,
        "seal_nonce": "C3-DOMAIN-SEAL",
        "tier": PlanTiers.ENTERPRISE,
    }

    values.update(
        changes
    )

    return SubscriptionEntity(
        **values
    )


def test_versions_are_exact() -> None:
    assert VERSION == DOMAIN_VERSION
    assert (
        TEST_VERSION
        == "v1.1.1-SUBSCRIPTION-CALENDAR-BILLING-CERT"
    )


def test_legacy_unknown_catalogue_version_remains_explicit_none() -> None:
    subscription = _subscription(
        plan_catalogue_version=None,
    )

    assert (
        subscription.plan_catalogue_version
        is None
    )

    assert (
        subscription.to_dict()[
            "plan_catalogue_version"
        ]
        is None
    )


@pytest.mark.parametrize(
    "value",
    [
        True,
        False,
        0,
        -1,
        1.5,
        "1",
    ],
)
def test_invalid_catalogue_version_fails_closed(
    value: Any,
) -> None:
    with pytest.raises(
        (TypeError, ValueError),
    ):
        _subscription(
            plan_catalogue_version=value,
        )


def test_plan_feature_snapshot_is_immutable_and_projection_detached() -> None:
    source_features = [
        "crm.core",
        "legal.documents",
    ]

    subscription = _subscription(
        plan_features=source_features,
    )

    source_features.append(
        "caller.mutation"
    )

    assert subscription.plan_features == (
        "crm.core",
        "legal.documents",
    )

    projected = subscription.to_dict()

    projected[
        "plan_features"
    ].append(
        "projection.mutation"
    )

    assert subscription.plan_features == (
        "crm.core",
        "legal.documents",
    )


def test_catalogue_snapshot_round_trip_preserves_coordinate() -> None:
    original = _subscription()

    restored = SubscriptionEntity.from_dict(
        original.to_dict()
    )

    assert (
        restored.plan_catalogue_version
        == original.plan_catalogue_version
    )

    assert (
        restored.plan_features
        == original.plan_features
    )

    assert (
        restored.plan_name
        == original.plan_name
    )


def test_identical_canonical_state_generates_stable_proof() -> None:
    subscription = _subscription()

    assert (
        subscription.generate_proof()
        == subscription.generate_proof()
    )


def test_catalogue_coordinate_changes_subscription_proof() -> None:
    first = _subscription(
        plan_catalogue_version=7,
    )

    second = _subscription(
        plan_catalogue_version=8,
    )

    assert (
        first.proof_hash
        != second.proof_hash
    )


def test_plan_name_changes_subscription_proof() -> None:
    first = _subscription(
        plan_name="Enterprise",
    )

    second = _subscription(
        plan_name="Enterprise Plus",
    )

    assert (
        first.proof_hash
        != second.proof_hash
    )


def test_plan_features_change_subscription_proof() -> None:
    first = _subscription(
        plan_features=(
            "crm.core",
            "legal.documents",
        ),
    )

    second = _subscription(
        plan_features=(
            "crm.core",
            "legal.documents",
            "wilsy.ai",
        ),
    )

    assert (
        first.proof_hash
        != second.proof_hash
    )


def test_catalogue_coordinate_projects_to_invoice_and_evidence() -> None:
    subscription = _subscription()

    invoice = (
        subscription
        .to_platform_invoice_seed()
    )

    evidence = (
        subscription
        .generate_evidence_package()
    )

    assert (
        invoice["planCatalogueVersion"]
        == 7
    )

    assert (
        evidence["planCatalogueVersion"]
        == 7
    )

    assert invoice[
        "planFeatures"
    ] == [
        "crm.core",
        "legal.documents",
    ]

    assert evidence[
        "planFeatures"
    ] == [
        "crm.core",
        "legal.documents",
    ]



@pytest.mark.parametrize(
    (
        "reference",
        "expected_start",
        "expected_end",
        "expected_days",
    ),
    [
        (
            datetime(
                2026, 9, 3, 17, 45,
                tzinfo=timezone.utc,
            ),
            datetime(
                2026, 9, 1,
                tzinfo=timezone.utc,
            ),
            datetime(
                2026, 10, 1,
                tzinfo=timezone.utc,
            ),
            30,
        ),
        (
            datetime(
                2026, 1, 31, 23, 59,
                tzinfo=timezone.utc,
            ),
            datetime(
                2026, 1, 1,
                tzinfo=timezone.utc,
            ),
            datetime(
                2026, 2, 1,
                tzinfo=timezone.utc,
            ),
            31,
        ),
        (
            datetime(
                2027, 2, 14, 8, 0,
                tzinfo=timezone.utc,
            ),
            datetime(
                2027, 2, 1,
                tzinfo=timezone.utc,
            ),
            datetime(
                2027, 3, 1,
                tzinfo=timezone.utc,
            ),
            28,
        ),
        (
            datetime(
                2028, 2, 29, 8, 0,
                tzinfo=timezone.utc,
            ),
            datetime(
                2028, 2, 1,
                tzinfo=timezone.utc,
            ),
            datetime(
                2028, 3, 1,
                tzinfo=timezone.utc,
            ),
            29,
        ),
    ],
)
def test_monthly_calendar_period_uses_actual_month_length(
    reference: datetime,
    expected_start: datetime,
    expected_end: datetime,
    expected_days: int,
) -> None:
    start, end, total_days = (
        calendar_period_bounds(
            reference,
            BillingFrequency.MONTHLY,
        )
    )

    assert start == expected_start
    assert end == expected_end
    assert total_days == expected_days


def test_quarterly_calendar_period_spans_three_real_months() -> None:
    start, end, total_days = (
        calendar_period_bounds(
            datetime(
                2028,
                1,
                20,
                12,
                0,
                tzinfo=timezone.utc,
            ),
            BillingFrequency.QUARTERLY,
        )
    )

    assert start == datetime(
        2028,
        1,
        1,
        tzinfo=timezone.utc,
    )

    assert end == datetime(
        2028,
        4,
        1,
        tzinfo=timezone.utc,
    )

    # Leap-year January + February + March:
    # 31 + 29 + 31.
    assert total_days == 91


def test_annual_calendar_period_preserves_leap_year_truth() -> None:
    start, end, total_days = (
        calendar_period_bounds(
            datetime(
                2028,
                2,
                29,
                18,
                0,
                tzinfo=timezone.utc,
            ),
            BillingFrequency.ANNUAL,
        )
    )

    assert start == datetime(
        2028,
        2,
        1,
        tzinfo=timezone.utc,
    )

    assert end == datetime(
        2029,
        2,
        1,
        tzinfo=timezone.utc,
    )

    assert total_days == 366


def test_calendar_period_requires_explicit_timezone() -> None:
    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        calendar_period_bounds(
            datetime(
                2028,
                2,
                10,
                12,
                0,
            ),
            BillingFrequency.MONTHLY,
        )


def test_calendar_period_preserves_explicit_timezone() -> None:
    za = timezone(
        timedelta(
            hours=2,
        )
    )

    start, end, total_days = (
        calendar_period_bounds(
            datetime(
                2026,
                9,
                18,
                20,
                30,
                tzinfo=za,
            ),
            BillingFrequency.MONTHLY,
        )
    )

    assert start == datetime(
        2026,
        9,
        1,
        tzinfo=za,
    )

    assert end == datetime(
        2026,
        10,
        1,
        tzinfo=za,
    )

    assert start.utcoffset() == timedelta(
        hours=2,
    )

    assert end.utcoffset() == timedelta(
        hours=2,
    )

    assert total_days == 30


def test_calendar_proration_coordinate_uses_actual_calendar_denominator() -> None:
    coordinate = (
        calendar_proration_coordinate(
            datetime(
                2026,
                9,
                16,
                14,
                30,
                tzinfo=timezone.utc,
            ),
            BillingFrequency.MONTHLY,
        )
    )

    assert coordinate[
        "period_start"
    ] == datetime(
        2026,
        9,
        1,
        tzinfo=timezone.utc,
    )

    assert coordinate[
        "period_end"
    ] == datetime(
        2026,
        10,
        1,
        tzinfo=timezone.utc,
    )

    assert coordinate[
        "total_days"
    ] == 30

    assert coordinate[
        "days_elapsed"
    ] == 15

    assert coordinate[
        "days_remaining"
    ] == 15

    assert coordinate[
        "proration_factor"
    ] == pytest.approx(
        0.5
    )


def test_calendar_proration_coordinate_is_non_monetary() -> None:
    coordinate = (
        calendar_proration_coordinate(
            datetime(
                2028,
                2,
                15,
                9,
                0,
                tzinfo=timezone.utc,
            ),
            BillingFrequency.MONTHLY,
        )
    )

    assert set(
        coordinate
    ) == {
        "period_start",
        "period_end",
        "total_days",
        "days_elapsed",
        "days_remaining",
        "proration_factor",
    }

    assert "amount" not in coordinate
    assert "credit" not in coordinate
    assert "charge" not in coordinate
    assert "payment" not in coordinate



def test_calendar_proration_first_day_is_full_remaining_period() -> None:
    coordinate = (
        calendar_proration_coordinate(
            datetime(
                2026,
                9,
                1,
                12,
                0,
                tzinfo=timezone.utc,
            ),
            BillingFrequency.MONTHLY,
        )
    )

    assert coordinate["total_days"] == 30
    assert coordinate["days_elapsed"] == 0
    assert coordinate["days_remaining"] == 30

    assert coordinate[
        "proration_factor"
    ] == pytest.approx(
        1.0
    )


def test_calendar_proration_last_day_has_one_calendar_day_remaining() -> None:
    coordinate = (
        calendar_proration_coordinate(
            datetime(
                2026,
                9,
                30,
                23,
                59,
                tzinfo=timezone.utc,
            ),
            BillingFrequency.MONTHLY,
        )
    )

    assert coordinate["total_days"] == 30
    assert coordinate["days_elapsed"] == 29
    assert coordinate["days_remaining"] == 1

    assert coordinate[
        "proration_factor"
    ] == pytest.approx(
        1 / 30
    )


def test_calendar_proration_period_end_enters_next_half_open_period() -> None:
    coordinate = (
        calendar_proration_coordinate(
            datetime(
                2026,
                10,
                1,
                0,
                0,
                tzinfo=timezone.utc,
            ),
            BillingFrequency.MONTHLY,
        )
    )

    assert coordinate[
        "period_start"
    ] == datetime(
        2026,
        10,
        1,
        tzinfo=timezone.utc,
    )

    assert coordinate[
        "period_end"
    ] == datetime(
        2026,
        11,
        1,
        tzinfo=timezone.utc,
    )

    assert coordinate["total_days"] == 31
    assert coordinate["days_elapsed"] == 0
    assert coordinate["days_remaining"] == 31

    assert coordinate[
        "proration_factor"
    ] == pytest.approx(
        1.0
    )


def test_calendar_period_real_dst_zone_preserves_local_calendar_denominator() -> None:
    new_york = ZoneInfo(
        "America/New_York"
    )

    start, end, total_days = (
        calendar_period_bounds(
            datetime(
                2026,
                3,
                15,
                12,
                0,
                tzinfo=new_york,
            ),
            BillingFrequency.MONTHLY,
        )
    )

    assert start == datetime(
        2026,
        3,
        1,
        tzinfo=new_york,
    )

    assert end == datetime(
        2026,
        4,
        1,
        tzinfo=new_york,
    )

    assert start.tzinfo is new_york
    assert end.tzinfo is new_york

    # March 2026 crosses the US spring-forward boundary.
    assert start.utcoffset() != end.utcoffset()

    # Calendar truth remains 31 local dates regardless of the
    # elapsed UTC-hour count across the DST transition.
    assert total_days == 31


def test_december_monthly_period_rolls_into_next_year() -> None:
    start, end, total_days = (
        calendar_period_bounds(
            datetime(
                2026,
                12,
                20,
                10,
                0,
                tzinfo=timezone.utc,
            ),
            BillingFrequency.MONTHLY,
        )
    )

    assert start == datetime(
        2026,
        12,
        1,
        tzinfo=timezone.utc,
    )

    assert end == datetime(
        2027,
        1,
        1,
        tzinfo=timezone.utc,
    )

    assert total_days == 31


def test_cross_year_quarterly_period_uses_three_calendar_months() -> None:
    start, end, total_days = (
        calendar_period_bounds(
            datetime(
                2026,
                11,
                18,
                9,
                0,
                tzinfo=timezone.utc,
            ),
            BillingFrequency.QUARTERLY,
        )
    )

    assert start == datetime(
        2026,
        11,
        1,
        tzinfo=timezone.utc,
    )

    assert end == datetime(
        2027,
        2,
        1,
        tzinfo=timezone.utc,
    )

    # November + December + January.
    assert total_days == (
        30 + 31 + 31
    )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: tests/unit/test_subscription_domain.py
# VERSION: v1.1.1-SUBSCRIPTION-CALENDAR-BILLING-CERT
# AUTHORITY BOUNDARY: Direct SubscriptionEntity catalogue-provenance and
# calendar-billing value certificate only; no authentication, persistence,
# entitlement, pricing mutation, payment or execution authority.
# TENANT POSTURE: Synthetic tenant scope only; no access authority is created.
# FAIL-CLOSED POSTURE: Invalid catalogue coordinates and mutable snapshot
# semantics are explicit certification failures.
# FINANCIAL EXECUTION AUTHORITY: NONE — Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
