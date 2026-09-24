"""Direct certificate for the D22B1 tenant product entitlement domain.

TITLE: Tenant Product Entitlement Direct Certificate
VERSION: v1.0.0-D22B1-TENANT-PRODUCT-ENTITLEMENT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove exact catalogue binding, tenant isolation, source-evidence
         requirements, lifecycle transitions, integrity and authority firewalls.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_product_entitlement.py
COLLABORATION / OWNERSHIP: Evidence-only direct certificate for the D22B1
                            entitlement domain.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG: v1.0.0-D22B1-TENANT-PRODUCT-ENTITLEMENT-CERT establishes direct
           evidence for pending/active/suspended/revoked lifecycle semantics,
           D22A catalogue fingerprint binding and strict separation from plan,
           subscription, VAS, IAM, workspace-routing and financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic tenant and evidence identifiers only.
TENANT BOUNDARY: Cross-tenant or pseudo-tenant authority is never inferred.
AUTHORITY BOUNDARY: Direct domain evidence only; no persistence or IAM.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
import re
from typing import Any, cast

import pytest

from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlement,
    TenantProductEntitlementError,
    TenantProductEntitlementState,
    create_tenant_product_entitlement,
)
from tools.eos.saas.entitlement.product_catalogue import (
    TenantProductId,
    get_tenant_product,
)


NOW = datetime(2026, 9, 24, 10, 0, tzinfo=timezone.utc)
FP = "a" * 128


def entitlement(**changes: object) -> TenantProductEntitlement:
    """Return one valid pending synthetic entitlement with optional changes."""
    product = get_tenant_product(TenantProductId.LEGAL_OPERATIONS)
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "entitlement_id": "ent-legal-a",
        "product_id": TenantProductId.LEGAL_OPERATIONS,
        "product_catalogue_fingerprint": product.fingerprint,
        "lifecycle_state": TenantProductEntitlementState.PENDING_SOURCE,
        "source_evidence_reference": "onboarding-composition-1",
        "source_evidence_fingerprint": FP,
    }
    values.update(changes)
    return TenantProductEntitlement(**cast(Any, values))


def test_factory_binds_exact_d22a_catalogue_fingerprint_and_stays_pending() -> None:
    value = create_tenant_product_entitlement(
        tenant_id="tenant-a",
        entitlement_id="ent-billing-a",
        product_id=TenantProductId.BILLING,
        source_evidence_reference="composition-1",
        source_evidence_fingerprint=FP,
    )
    assert value.product_id is TenantProductId.BILLING
    assert value.product_catalogue_fingerprint == get_tenant_product(
        TenantProductId.BILLING
    ).fingerprint
    assert value.lifecycle_state is TenantProductEntitlementState.PENDING_SOURCE


def test_pending_entitlement_is_not_active_by_existence() -> None:
    value = entitlement()
    assert value.lifecycle_state is TenantProductEntitlementState.PENDING_SOURCE
    assert value.activated_at is None
    assert value.activation_evidence_reference is None


@pytest.mark.parametrize("product_id", list(TenantProductId))
def test_every_d22a_product_can_be_bound_exactly(product_id: TenantProductId) -> None:
    product = get_tenant_product(product_id)
    value = create_tenant_product_entitlement(
        tenant_id="tenant-a",
        entitlement_id=f"ent-{product_id.value.lower()}",
        product_id=product_id,
        source_evidence_reference="composition-1",
        source_evidence_fingerprint=FP,
    )
    assert value.product_id is product_id
    assert value.product_catalogue_fingerprint == product.fingerprint


def test_catalogue_fingerprint_drift_fails_closed() -> None:
    with pytest.raises(
        TenantProductEntitlementError,
        match="D22B1_CATALOGUE_BINDING_INVALID",
    ):
        entitlement(product_catalogue_fingerprint="b" * 128)


@pytest.mark.parametrize("tenant_id", ["", "default", "global", "root", "*"])
def test_missing_or_pseudo_tenant_fails_closed(tenant_id: str) -> None:
    with pytest.raises(TenantProductEntitlementError):
        entitlement(tenant_id=tenant_id)


def test_unknown_product_fails_closed() -> None:
    with pytest.raises(
        TenantProductEntitlementError,
        match="D22B1_ENUM_INVALID",
    ):
        entitlement(product_id="WILSY_AI")


def test_source_evidence_reference_and_fingerprint_are_mandatory() -> None:
    with pytest.raises(TenantProductEntitlementError):
        entitlement(source_evidence_reference="")
    with pytest.raises(TenantProductEntitlementError):
        entitlement(source_evidence_fingerprint="not-a-digest")


def test_active_suspended_and_revoked_shapes_require_exact_evidence() -> None:
    active = entitlement(
        lifecycle_state=TenantProductEntitlementState.ACTIVE,
        activated_at=NOW,
        activation_evidence_reference="activate-1",
        activation_evidence_fingerprint=FP,
    )
    assert active.lifecycle_state is TenantProductEntitlementState.ACTIVE

    suspended = entitlement(
        lifecycle_state=TenantProductEntitlementState.SUSPENDED,
        activated_at=NOW,
        activation_evidence_reference="activate-1",
        activation_evidence_fingerprint=FP,
        suspended_at=NOW,
        suspension_evidence_reference="suspend-1",
        suspension_evidence_fingerprint=FP,
    )
    assert suspended.lifecycle_state is TenantProductEntitlementState.SUSPENDED

    revoked = entitlement(
        lifecycle_state=TenantProductEntitlementState.REVOKED,
        activated_at=NOW,
        activation_evidence_reference="activate-1",
        activation_evidence_fingerprint=FP,
        revoked_at=NOW,
        revocation_evidence_reference="revoke-1",
        revocation_evidence_fingerprint=FP,
    )
    assert revoked.lifecycle_state is TenantProductEntitlementState.REVOKED


def test_invalid_lifecycle_shape_and_chronology_fail_closed() -> None:
    with pytest.raises(
        TenantProductEntitlementError,
        match="D22B1_ACTIVE_SHAPE_INVALID",
    ):
        entitlement(lifecycle_state=TenantProductEntitlementState.ACTIVE)

    with pytest.raises(
        TenantProductEntitlementError,
        match="D22B1_CHRONOLOGY_INVALID",
    ):
        entitlement(
            lifecycle_state=TenantProductEntitlementState.SUSPENDED,
            activated_at=NOW,
            activation_evidence_reference="activate-1",
            activation_evidence_fingerprint=FP,
            suspended_at=NOW.replace(year=2025),
            suspension_evidence_reference="suspend-1",
            suspension_evidence_fingerprint=FP,
        )


def test_revisioned_transitions_are_closed_and_evidence_backed() -> None:
    pending = entitlement()
    active = pending.transition(
        TenantProductEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activate-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
    )
    assert active.lifecycle_revision == 1
    assert active.activation_evidence_reference == "activate-1"

    suspended = active.transition(
        TenantProductEntitlementState.SUSPENDED,
        expected_revision=1,
        evidence_reference="suspend-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
    )
    assert suspended.lifecycle_revision == 2

    with pytest.raises(
        TenantProductEntitlementError,
        match="D22B1_STALE_REVISION",
    ):
        pending.transition(
            TenantProductEntitlementState.ACTIVE,
            expected_revision=99,
            evidence_reference="x",
            evidence_fingerprint=FP,
            occurred_at=NOW,
        )

    with pytest.raises(
        TenantProductEntitlementError,
        match="D22B1_ILLEGAL_TRANSITION",
    ):
        suspended.transition(
            TenantProductEntitlementState.ACTIVE,
            expected_revision=2,
            evidence_reference="resume",
            evidence_fingerprint=FP,
            occurred_at=NOW,
        )


def test_revoked_is_terminal() -> None:
    active = entitlement().transition(
        TenantProductEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="activate-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
    )
    revoked = active.transition(
        TenantProductEntitlementState.REVOKED,
        expected_revision=1,
        evidence_reference="revoke-1",
        evidence_fingerprint=FP,
        occurred_at=NOW,
    )
    with pytest.raises(
        TenantProductEntitlementError,
        match="D22B1_ILLEGAL_TRANSITION",
    ):
        revoked.transition(
            TenantProductEntitlementState.ACTIVE,
            expected_revision=2,
            evidence_reference="reactivate",
            evidence_fingerprint=FP,
            occurred_at=NOW,
        )


def test_fingerprint_is_deterministic_lowercase_sha3_512_and_mutation_sensitive() -> None:
    first = entitlement()
    second = entitlement()
    assert first.fingerprint == second.fingerprint
    assert re.fullmatch(r"[0-9a-f]{128}", first.fingerprint)
    assert replace(
        first,
        tenant_id="tenant-b",
        fingerprint="",
    ).fingerprint != first.fingerprint


def test_strict_round_trip_and_unknown_missing_corrupt_payloads_fail_closed() -> None:
    value = entitlement()
    payload = value.to_dict()
    assert TenantProductEntitlement.from_dict(payload) == value

    with pytest.raises(
        TenantProductEntitlementError,
        match="D22B1_SCHEMA_INVALID",
    ):
        TenantProductEntitlement.from_dict({**payload, "extra": "x"})

    missing = dict(payload)
    missing.pop("product_id")
    with pytest.raises(
        TenantProductEntitlementError,
        match="D22B1_SCHEMA_INVALID",
    ):
        TenantProductEntitlement.from_dict(missing)

    corrupt = dict(payload)
    corrupt["fingerprint"] = "f" * 128
    with pytest.raises(
        TenantProductEntitlementError,
        match="D22B1_FINGERPRINT_MISMATCH",
    ):
        TenantProductEntitlement.from_dict(corrupt)


def test_immutability_and_authority_firewalls() -> None:
    value = entitlement()
    with pytest.raises((FrozenInstanceError, AttributeError)):
        value.tenant_id = "tenant-b"  # type: ignore[misc]

    forbidden = {
        "plan",
        "plan_id",
        "subscription_id",
        "price",
        "amount",
        "currency",
        "principal_id",
        "role",
        "permission",
        "workspace_access",
        "wilsy_ai",
        "branding",
        "invoice",
        "payment",
        "execution",
        "settlement",
    }
    assert forbidden.isdisjoint(value.to_dict())


def test_no_runtime_side_effect_imports() -> None:
    import sys

    assert "requests" not in sys.modules
    assert "boto3" not in sys.modules


# ARTIFACT: test_tenant_product_entitlement.py
# VERSION: v1.0.0-D22B1-TENANT-PRODUCT-ENTITLEMENT-CERT
# AUTHORITY BOUNDARY: direct entitlement-domain evidence only; no persistence or IAM
# TENANT POSTURE: synthetic tenant/product bindings only
# FAIL-CLOSED POSTURE: catalogue drift, malformed evidence and illegal transitions reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
