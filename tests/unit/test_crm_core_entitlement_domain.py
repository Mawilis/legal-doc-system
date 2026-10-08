"""
TITLE: WILSY OS CRM Core Entitlement Domain Direct Certificate
VERSION: v1.0.1-CRM-P9D-R4-CORE-ENTITLEMENT-SUBSCRIPTION-PROOF-CONVERGENCE-CERT
AUTHORITY: Direct certificate for immutable tenant-scoped crm.core entitlement evidence.
EPITOME:
    Freezes the pure CRM entitlement value contract before production
    implementation. Authorization, business role, subscription commercial
    evidence, entitlement and quota remain separate conjuncts.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_crm_core_entitlement_domain.py
COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE:
    2026-10-06

COMMERCIAL AUTHORITY:
    The only core CRM feature identifier certified here is ``crm.core``.
    Plan feature membership, subscription plan labels and browser feature flags
    do not themselves establish entitlement.

SOURCE EVIDENCE:
    An ACTIVE entitlement must bind exact already-derived subscription
    commercial evidence:
      - tenant identity,
      - subscription identity,
      - plan identity,
      - plan catalogue version,
      - canonical subscription proof hash,
      - exact feature id ``crm.core``.

AUTHORITY BOUNDARY:
    This domain owns entitlement evidence only. It does not authenticate a
    principal, grant permissions, choose business roles, establish IAM
    assignments, meter usage, mutate subscriptions, execute CRM commands,
    expose HTTP routes, grant AI authority or execute financially.

CHANGELOG:
    - 2026-10-07 v1.0.1-CRM-P9D-R4-CORE-ENTITLEMENT-SUBSCRIPTION-PROOF-CONVERGENCE-CERT: converges the direct certificate with the canonical SubscriptionEntity uppercase SHA3-512 proof representation; lowercase, mixed-case, malformed-length and non-hex subscription proofs remain fail-closed. Entitlement-local fingerprints and lifecycle evidence digest semantics are unchanged.
    2026-10-06 v1.0.0 establishes the test-first CRM Core entitlement
    contract from the certified crm.core Plan/Subscription commercial
    provenance and the revisioned immutable entitlement pattern.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from hashlib import sha3_512
from typing import Any

import pytest

from tools.eos.crm.domain.crm_core_entitlement import (
    CRM_CORE_ENTITLEMENT_SCHEMA,
    CRM_CORE_ENTITLEMENT_VERSION,
    CRM_CORE_FEATURE_ID,
    CrmCoreEntitlement,
    CrmCoreEntitlementError,
    CrmCoreEntitlementState,
)


EXPECTED_VERSION = "v1.0.1-CRM-CORE-ENTITLEMENT-SUBSCRIPTION-PROOF-CONVERGENCE"
EXPECTED_SCHEMA = "WILSY-CRM-CORE-ENTITLEMENT/V1"
EXPECTED_FEATURE = "crm.core"

TENANT = "TENANT-CRM-ENTITLEMENT-A"
SUBSCRIPTION = "WILSYSUB-CRMCORE01"
PLAN = "WILSYPLAN-CRMCORE01"
ENTITLEMENT = "WILSYCRM-ENT-CORE-0001"

SUBSCRIPTION_PROOF = "A" * 128
ACTIVATION_EVIDENCE = "b" * 128
SUSPENSION_EVIDENCE = "c" * 128
REVOCATION_EVIDENCE = "d" * 128

T0 = datetime(2026, 10, 6, 10, 0, tzinfo=timezone.utc)
T1 = T0 + timedelta(hours=1)
T2 = T1 + timedelta(hours=1)


def _pending(**changes: Any) -> CrmCoreEntitlement:
    values: dict[str, Any] = {
        "tenant_id": TENANT,
        "entitlement_id": ENTITLEMENT,
        "feature_id": EXPECTED_FEATURE,
        "subscription_id": SUBSCRIPTION,
        "plan_id": PLAN,
        "plan_catalogue_version": 7,
        "subscription_proof_hash": SUBSCRIPTION_PROOF,
        "lifecycle_state": CrmCoreEntitlementState.PENDING_SOURCE,
        "lifecycle_revision": 0,
    }
    values.update(changes)
    return CrmCoreEntitlement(**values)


def _active() -> CrmCoreEntitlement:
    return _pending().transition(
        CrmCoreEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="subscription:WILSYSUB-CRMCORE01:crm.core",
        evidence_fingerprint=ACTIVATION_EVIDENCE,
        occurred_at=T0,
    )


def test_version_schema_and_feature_id_are_exact() -> None:
    assert CRM_CORE_ENTITLEMENT_VERSION == EXPECTED_VERSION
    assert CRM_CORE_ENTITLEMENT_SCHEMA == EXPECTED_SCHEMA
    assert CRM_CORE_FEATURE_ID == EXPECTED_FEATURE


def test_closed_lifecycle_states_are_exact() -> None:
    assert tuple(state.value for state in CrmCoreEntitlementState) == (
        "PENDING_SOURCE",
        "ACTIVE",
        "SUSPENDED",
        "REVOKED",
    )


def test_pending_entitlement_is_immutable_and_fingerprinted() -> None:
    value = _pending()

    assert value.tenant_id == TENANT
    assert value.entitlement_id == ENTITLEMENT
    assert value.feature_id == EXPECTED_FEATURE
    assert value.subscription_id == SUBSCRIPTION
    assert value.plan_id == PLAN
    assert value.plan_catalogue_version == 7
    assert value.subscription_proof_hash == SUBSCRIPTION_PROOF
    assert value.lifecycle_state is CrmCoreEntitlementState.PENDING_SOURCE
    assert value.lifecycle_revision == 0
    assert len(value.fingerprint) == 128
    assert set(value.fingerprint) <= set("0123456789abcdef")

    with pytest.raises(FrozenInstanceError):
        value.feature_id = "crm.other"  # type: ignore[misc]


@pytest.mark.parametrize(
    "tenant",
    (
        "",
        " ",
        " TENANT-A",
        "TENANT-A ",
        "default",
        "GLOBAL",
        "root",
        "*",
        "MASTER",
        "GLOBAL_ROOT",
        "SOVEREIGN_ROOT",
        "wilsy-sovereign-root",
    ),
)
def test_tenant_identity_fails_closed(tenant: str) -> None:
    with pytest.raises(CrmCoreEntitlementError):
        _pending(tenant_id=tenant)


@pytest.mark.parametrize(
    "feature",
    (
        "",
        " ",
        "crm",
        "crm.*",
        "crm.lead",
        "crm.leads.core",
        "CRM.CORE",
        "crm.core ",
        " crm.core",
    ),
)
def test_feature_identifier_is_exactly_crm_core(feature: str) -> None:
    with pytest.raises(CrmCoreEntitlementError):
        _pending(feature_id=feature)


@pytest.mark.parametrize(
    "field,value",
    (
        ("entitlement_id", ""),
        ("entitlement_id", " ENT-1"),
        ("subscription_id", ""),
        ("subscription_id", " WILSYSUB-1"),
        ("plan_id", ""),
        ("plan_id", " WILSYPLAN-1"),
    ),
)
def test_identifiers_are_exact_nonempty_text(
    field: str,
    value: str,
) -> None:
    with pytest.raises(CrmCoreEntitlementError):
        _pending(**{field: value})


@pytest.mark.parametrize(
    "version",
    (
        True,
        False,
        -1,
        0,
        1.5,
        "7",
        None,
    ),
)
def test_catalogue_provenance_requires_positive_integer_version(
    version: object,
) -> None:
    with pytest.raises(CrmCoreEntitlementError):
        _pending(plan_catalogue_version=version)


@pytest.mark.parametrize(
    "digest",
    (
        "",
        "A" * 127,
        "A" * 129,
        "a" * 128,
        ("A" * 64) + ("a" * 64),
        "G" * 128,
    ),
)
def test_subscription_proof_requires_canonical_uppercase_sha3_512_shape(
    digest: str,
) -> None:
    with pytest.raises(CrmCoreEntitlementError):
        _pending(subscription_proof_hash=digest)


def test_pending_shape_has_no_activation_or_terminal_evidence() -> None:
    value = _pending()

    assert value.activated_at is None
    assert value.activation_evidence_reference is None
    assert value.activation_evidence_fingerprint is None
    assert value.suspended_at is None
    assert value.suspension_evidence_reference is None
    assert value.suspension_evidence_fingerprint is None
    assert value.revoked_at is None
    assert value.revocation_evidence_reference is None
    assert value.revocation_evidence_fingerprint is None


def test_activation_is_revisioned_and_evidence_bound() -> None:
    pending = _pending()

    active = pending.transition(
        CrmCoreEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference="subscription:WILSYSUB-CRMCORE01:crm.core",
        evidence_fingerprint=ACTIVATION_EVIDENCE,
        occurred_at=T0,
    )

    assert active.lifecycle_state is CrmCoreEntitlementState.ACTIVE
    assert active.lifecycle_revision == 1
    assert active.activated_at == T0
    assert (
        active.activation_evidence_reference
        == "subscription:WILSYSUB-CRMCORE01:crm.core"
    )
    assert active.activation_evidence_fingerprint == ACTIVATION_EVIDENCE
    assert active.fingerprint != pending.fingerprint


def test_active_requires_exact_source_evidence_shape() -> None:
    pending = _pending()

    with pytest.raises(CrmCoreEntitlementError):
        pending.transition(
            CrmCoreEntitlementState.ACTIVE,
            expected_revision=0,
            evidence_reference="",
            evidence_fingerprint=ACTIVATION_EVIDENCE,
            occurred_at=T0,
        )

    with pytest.raises(CrmCoreEntitlementError):
        pending.transition(
            CrmCoreEntitlementState.ACTIVE,
            expected_revision=0,
            evidence_reference="subscription:WILSYSUB-CRMCORE01:crm.core",
            evidence_fingerprint="x" * 128,
            occurred_at=T0,
        )


def test_stale_revision_fails_closed() -> None:
    pending = _pending()

    with pytest.raises(CrmCoreEntitlementError):
        pending.transition(
            CrmCoreEntitlementState.ACTIVE,
            expected_revision=1,
            evidence_reference="subscription:WILSYSUB-CRMCORE01:crm.core",
            evidence_fingerprint=ACTIVATION_EVIDENCE,
            occurred_at=T0,
        )


def test_lifecycle_transitions_are_closed_and_terminal() -> None:
    active = _active()

    suspended = active.transition(
        CrmCoreEntitlementState.SUSPENDED,
        expected_revision=1,
        evidence_reference="commercial:suspension:1",
        evidence_fingerprint=SUSPENSION_EVIDENCE,
        occurred_at=T1,
    )

    assert suspended.lifecycle_state is CrmCoreEntitlementState.SUSPENDED
    assert suspended.lifecycle_revision == 2
    assert suspended.suspended_at == T1

    with pytest.raises(CrmCoreEntitlementError):
        suspended.transition(
            CrmCoreEntitlementState.ACTIVE,
            expected_revision=2,
            evidence_reference="commercial:resume:1",
            evidence_fingerprint=ACTIVATION_EVIDENCE,
            occurred_at=T2,
        )

    active_again = _active()

    revoked = active_again.transition(
        CrmCoreEntitlementState.REVOKED,
        expected_revision=1,
        evidence_reference="commercial:revocation:1",
        evidence_fingerprint=REVOCATION_EVIDENCE,
        occurred_at=T1,
    )

    assert revoked.lifecycle_state is CrmCoreEntitlementState.REVOKED
    assert revoked.lifecycle_revision == 2
    assert revoked.revoked_at == T1

    with pytest.raises(CrmCoreEntitlementError):
        revoked.transition(
            CrmCoreEntitlementState.ACTIVE,
            expected_revision=2,
            evidence_reference="commercial:reactivation:1",
            evidence_fingerprint=ACTIVATION_EVIDENCE,
            occurred_at=T2,
        )


def test_pending_cannot_skip_directly_to_terminal_state() -> None:
    pending = _pending()

    for target in (
        CrmCoreEntitlementState.SUSPENDED,
        CrmCoreEntitlementState.REVOKED,
    ):
        with pytest.raises(CrmCoreEntitlementError):
            pending.transition(
                target,
                expected_revision=0,
                evidence_reference="illegal-transition",
                evidence_fingerprint=SUSPENSION_EVIDENCE,
                occurred_at=T0,
            )


def test_transition_chronology_fails_closed() -> None:
    active = _active()

    with pytest.raises(CrmCoreEntitlementError):
        active.transition(
            CrmCoreEntitlementState.SUSPENDED,
            expected_revision=1,
            evidence_reference="commercial:suspension:old",
            evidence_fingerprint=SUSPENSION_EVIDENCE,
            occurred_at=T0 - timedelta(seconds=1),
        )


def test_strict_round_trip_preserves_exact_entitlement_truth() -> None:
    value = _active()

    payload = value.to_dict()
    restored = CrmCoreEntitlement.from_dict(payload)

    assert restored == value
    assert restored.fingerprint == value.fingerprint
    assert restored.to_dict() == payload


def test_hydration_rejects_missing_extra_or_corrupt_fields() -> None:
    payload = _active().to_dict()

    missing = dict(payload)
    missing.pop("feature_id")

    with pytest.raises(CrmCoreEntitlementError):
        CrmCoreEntitlement.from_dict(missing)

    extra = dict(payload)
    extra["tier"] = "ENTERPRISE"

    with pytest.raises(CrmCoreEntitlementError):
        CrmCoreEntitlement.from_dict(extra)

    corrupt = dict(payload)
    corrupt["subscription_proof_hash"] = "e" * 128

    with pytest.raises(CrmCoreEntitlementError):
        CrmCoreEntitlement.from_dict(corrupt)


def test_fingerprint_binds_commercial_source_coordinates() -> None:
    baseline = _pending()

    variants = (
        _pending(subscription_id="WILSYSUB-OTHER"),
        _pending(plan_id="WILSYPLAN-OTHER"),
        _pending(plan_catalogue_version=8),
        _pending(subscription_proof_hash="F" * 128),
    )

    assert all(
        candidate.fingerprint != baseline.fingerprint
        for candidate in variants
    )


def test_no_tier_permission_role_quota_ai_or_financial_fields_exist() -> None:
    payload = _pending().to_dict()

    forbidden = {
        "tier",
        "plan_tier",
        "permission",
        "permissions",
        "business_role",
        "authorization_role",
        "quota",
        "usage_limit",
        "usage_consumed",
        "ai_model",
        "provider",
        "payment_status",
        "payment_id",
        "invoice_id",
        "settlement_id",
        "financial_execution",
    }

    assert forbidden.isdisjoint(payload)


def test_fingerprint_is_sha3_512_deterministic_shape() -> None:
    first = _pending()
    second = _pending()

    assert first.fingerprint == second.fingerprint

    # Certificate only proves the persisted fingerprint has SHA3-512 shape and
    # stable deterministic semantics. Production source remains free to define
    # its exact canonical byte envelope.
    assert len(first.fingerprint) == len(
        sha3_512(b"").hexdigest()
    )


# ARTIFACT: test_crm_core_entitlement_domain.py
# VERSION: v1.0.1-CRM-P9D-R4-CORE-ENTITLEMENT-SUBSCRIPTION-PROOF-CONVERGENCE-CERT
# AUTHORITY BOUNDARY: direct entitlement-domain certificate only
# TENANT POSTURE: entitlement evidence is exact-tenant and fail-closed
# COMMERCIAL POSTURE: crm.core source evidence required; tier is not authority
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
