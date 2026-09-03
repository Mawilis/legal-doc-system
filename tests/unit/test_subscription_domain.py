"""WILSY OS — Subscription catalogue-provenance domain certificate.

TITLE:
    WILSY OS Subscription Catalogue Provenance Domain Certificate

VERSION:
    v1.0.0-SUBSCRIPTION-CATALOGUE-PROVENANCE-CERT

AUTHORITY:
    Wilsy OS Core Governance

PURPOSE:
    Certify that SubscriptionEntity preserves an immutable, explicitly versioned
    snapshot of previously resolved Plan catalogue truth without fabricating
    provenance for legacy subscriptions.

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

from datetime import datetime, timezone
from typing import Any

import pytest

from tools.eos.saas.domain.subscription import (
    BillingFrequency,
    PlanTiers,
    SubscriptionEntity,
    VERSION,
)


TEST_VERSION = (
    "v1.0.0-SUBSCRIPTION-CATALOGUE-PROVENANCE-CERT"
)

DOMAIN_VERSION = "v1.1.0-CATALOGUE-PROVENANCE"

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
        == "v1.0.0-SUBSCRIPTION-CATALOGUE-PROVENANCE-CERT"
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


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: tests/unit/test_subscription_domain.py
# VERSION: v1.0.0-SUBSCRIPTION-CATALOGUE-PROVENANCE-CERT
# AUTHORITY BOUNDARY: Direct SubscriptionEntity catalogue-provenance certificate
# only; no authentication, persistence, entitlement or execution authority.
# TENANT POSTURE: Synthetic tenant scope only; no access authority is created.
# FAIL-CLOSED POSTURE: Invalid catalogue coordinates and mutable snapshot
# semantics are explicit certification failures.
# FINANCIAL EXECUTION AUTHORITY: NONE — Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
