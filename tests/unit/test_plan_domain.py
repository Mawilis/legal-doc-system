"""
WILSY OS — Plan Domain Commercial Contract Direct Certificate

TITLE:
    Plan Domain Commercial Contract Direct Certificate

VERSION:
    v1.0.10-PLAN-DOMAIN-CERT

AUTHORITY:
    Wilsy OS Core Governance

PURPOSE:
    Certify plan identity, commercial validation, deterministic evidence,
    immutable state, tamper rejection and protected commercial evolution.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_plan_domain.py

PRODUCTION OWNER:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/plan.py

TENANT BOUNDARY:
    No authentication, membership, role or permission authority is created.

AUTHORITY BOUNDARY:
    Domain construction validates commercial truth but does not authorize who
    may publish or mutate catalogue truth.

FINANCIAL AUTHORITY:
    No payment, collection, release or settlement authority.
    Kennel EOS remains the exclusive financial execution authority.

SECURITY / PRIVACY:
    Invalid commercial state and inconsistent persisted evidence fail closed.

CHANGELOG:
    2026-09-03 v1.0.10-PLAN-DOMAIN-CERT
        - Certifies explicit LEGACY_UNVERSIONED_CONTENT_UNVERIFIED provenance
          for marker-free, evidence-free historical migration.
        - Certifies that the provenance classification survives current-v2
          serialization and strict hydration.
        - Preserves sealed legacy-envelope classification and all prior trust
          boundary certificates.
    2026-09-03 v1.0.9-PLAN-DOMAIN-CERT
        - Certifies fail-closed legacy rejection of both state_history and
          stateHistory current-schema markers.
        - Preserves all P1R5H/P1R5I verified-state and audit certificates.
    2026-09-03 v1.0.8-PLAN-DOMAIN-CERT
        - Aligns the historical-lineage tamper certificate with the earlier
          verified-state-history rejection boundary introduced by P1R5H.
        - Production Plan Domain and PlanRegistry bytes remain unchanged.
    2026-09-03 v1.0.7-PLAN-DOMAIN-CERT
        - Certifies canonical historical-state preimages and derived contiguous
          state-proof lineage.
        - Certifies rejection of incomplete/fabricated/gapped/future/out-of-order
          persisted state history.
        - Certifies complete persisted current-audit material.
        - Expands invalid catalogue-version and alias-direction coverage.
        - Certifies accurate in-memory PlanRegistry ownership wording.
    2026-09-03 v1.0.6-PLAN-DOMAIN-CERT
        - Certifies explicit current audit catalogue-version evidence.
        - Certifies conflicting and equal catalogue-version aliases.
        - Expands plan and audit proof-version alias tests across both conflict
          directions and equal-dual current values.
        - Certifies removal of the historical false Merkle terminology.
    2026-09-03 v1.0.5-PLAN-DOMAIN-CERT
        - Certifies rejection of contradictory plan proof-version aliases.
        - Certifies rejection of contradictory audit proof-version aliases.
        - Certifies that current-v2 AuditEntry evidence cannot cross the
          explicit legacy migration boundary.
    2026-09-03 v1.0.4-PLAN-DOMAIN-CERT
        - Repairs the P1R5 certificate-only AuditEntry import.
        - Routes legacy identity collision certification through the explicit
          migrate_legacy_dict trust boundary.
        - Aligns compatibility-alias tamper expectation with canonical
          integrity-root terminology.
        - Production Plan Domain and PlanRegistry bytes remain unchanged.
    2026-09-03 v1.0.3-PLAN-DOMAIN-CERT
        - Certifies strict current-v2 hydration and explicit legacy migration.
        - Certifies audit-to-state lineage resolution and trust-class isolation.
        - Certifies integrity-root terminology and signed-zero canonicalization.
        - Certifies Registry raw-price passthrough into PlanEntity validation.
    2026-09-03 v1.0.2-PLAN-DOMAIN-CERT
        - Adds adversarial certification for all five Codex findings:
          legacy proof migration, legacy identity collision resistance,
          lossless float pricing, chained audit evidence and current
          PlanRegistry user-context compatibility.
    2026-09-03 v1.0.1-PLAN-DOMAIN-CERT
        - Corrects certificate fixture timestamps so creation evidence is
          unambiguously historical before runtime-generated update evidence.
        - Production commercial semantics are unchanged.
    2026-09-03 v1.0.0-PLAN-DOMAIN-CERT
        - Initial direct commercial plan-domain certificate.

COMPLIANCE:
    POPIA §19 | GDPR Art. 32 | SOC2 CC7.2 | ISO 27001

WILSY OS — ALL OR NOTHING.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha3_512
from typing import Any, cast

import pytest

from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.domain.plan import (
    AuditAction,
    AuditEntry,
    PlanEntity,
    PlanFrequency,
    PlanTiers,
    parse_datetime,
)

def _plan(
    **overrides: Any,
) -> PlanEntity:
    payload: dict[str, Any] = {
        "name": "Professional",
        "price": 3000,
        "currency": "zar",
        "billing_frequency": PlanFrequency.MONTHLY,
        "plan_type": PlanTiers.PROFESSIONAL,
        "idempotency_key": "PLAN-CERT-001",
        "plan_id": "WILSYPLAN-A1B2C3D4",
        "description": "Professional operating plan",
        "trial_days": 14,
        "features": [
            "FEATURE_A",
            "FEATURE_B",
            "FEATURE_A",
        ],
        "active": True,
        "catalogue_version": 1,
        "tenant_id": None,
        "kennel_shard": "EOS_PRIMARY",
        "seal_nonce": "plan-cert-seal",
        "metadata": {
            "market": "ZA",
            "nested": {
                "channel": "DIRECT",
            },
        },
        "tags": [
            "sellable",
            "public",
            "sellable",
        ],
        "created_at": datetime(
            2026,
            1,
            2,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        "updated_at": datetime(
            2026,
            1,
            2,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    }

    payload.update(
        overrides
    )

    return PlanEntity(
        **payload
    )


def test_canonical_normalization() -> None:
    plan = _plan()

    assert plan.currency == "ZAR"
    assert plan.price == 3000.0
    assert plan.catalogue_version == 1

    assert plan.features == (
        "FEATURE_A",
        "FEATURE_B",
    )

    assert plan.tags == (
        "sellable",
        "public",
    )


def test_frozen_identity() -> None:
    unsafe = cast(
        Any,
        _plan(),
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        unsafe.plan_id = (
            "WILSYPLAN-FFFFFFFF"
        )


@pytest.mark.parametrize(
    ("field", "value", "error_type"),
    (
        ("name", "   ", ValueError),
        ("price", -0.01, ValueError),
        ("price", float("inf"), ValueError),
        ("price", True, TypeError),
        ("currency", "ZA", ValueError),
        ("trial_days", -1, ValueError),
        ("trial_days", 1.5, TypeError),
        ("catalogue_version", 0, ValueError),
        ("active", "yes", TypeError),
        ("features", "FEATURE_A", TypeError),
    ),
)
def test_invalid_commercial_state_fails_closed(
    field: str,
    value: Any,
    error_type: type[BaseException],
) -> None:
    with pytest.raises(
        error_type
    ):
        _plan(
            **{
                field: value
            }
        )


def test_invalid_datetime_fails_closed() -> None:
    with pytest.raises(
        ValueError
    ):
        parse_datetime(
            "not-a-date"
        )


def test_invalid_datetime_type_fails_closed() -> None:
    with pytest.raises(
        TypeError
    ):
        parse_datetime(
            42
        )


def test_naive_datetime_normalizes_utc() -> None:
    parsed = parse_datetime(
        datetime(
            2026,
            9,
            3,
            12,
            0,
        )
    )

    assert (
        parsed.tzinfo
        == timezone.utc
    )


def test_updated_at_cannot_precede_created_at() -> None:
    with pytest.raises(
        ValueError,
        match="updated_at",
    ):
        _plan(
            updated_at=datetime(
                2026,
                1,
                1,
                10,
                0,
                tzinfo=timezone.utc,
            )
        )


def test_metadata_deep_frozen() -> None:
    original = {
        "market": "ZA",
        "nested": {
            "channel": "DIRECT",
        },
    }

    plan = _plan(
        metadata=original
    )

    original["market"] = "US"

    cast(
        dict[str, Any],
        original["nested"],
    )["channel"] = "PARTNER"

    assert (
        plan.metadata["market"]
        == "ZA"
    )

    nested = cast(
        Any,
        plan.metadata["nested"],
    )

    assert (
        nested["channel"]
        == "DIRECT"
    )

    with pytest.raises(
        TypeError
    ):
        cast(
            Any,
            plan.metadata,
        )["market"] = "GB"

    with pytest.raises(
        TypeError
    ):
        nested["channel"] = "MUTATED"


def test_proof_replay_deterministic() -> None:
    first = _plan()
    second = _plan()

    assert (
        first.proof_hash
        == second.proof_hash
    )

    assert (
        first.generate_proof()
        == first.proof_hash
    )

    assert (
        first.generate_proof()
        == first.generate_proof()
    )

    assert len(
        first.proof_hash
    ) == 128


@pytest.mark.parametrize(
    ("field", "value"),
    (
        (
            "price",
            3000.01,
        ),
        (
            "features",
            [
                "FEATURE_A",
                "FEATURE_B",
                "FEATURE_C",
            ],
        ),
        (
            "metadata",
            {
                "market": "ZA",
                "nested": {
                    "channel": "PARTNER",
                },
            },
        ),
        (
            "tags",
            [
                "sellable",
                "private",
            ],
        ),
    ),
)
def test_commercial_material_is_bound_into_proof(
    field: str,
    value: Any,
) -> None:
    original = _plan()

    changed = _plan(
        **{
            field: value
        }
    )

    assert (
        changed.proof_hash
        != original.proof_hash
    )


def test_round_trip_preserves_evidence() -> None:
    original = _plan()

    hydrated = PlanEntity.from_dict(
        original.to_dict()
    )

    assert (
        hydrated.to_dict()
        == original.to_dict()
    )

    assert (
        hydrated.proof_hash
        == original.proof_hash
    )

    assert (
        hydrated.integrity_root
        == original.integrity_root
    )

    assert (
        hydrated.merkle_root
        == original.integrity_root
    )

    assert (
        hydrated.state_proof_lineage
        == original.state_proof_lineage
    )

@pytest.mark.parametrize(
    ("field", "value", "match"),
    (
        (
            "price",
            1,
            "proof_hash",
        ),
        (
            "features",
            [
                "FEATURE_A",
                "FEATURE_TAMPER",
            ],
            "proof_hash",
        ),
        (
            "merkle_root",
            "A" * 128,
            "integrity root and compatibility merkle alias disagree",
        ),
    ),
)
def test_tampered_persisted_evidence_rejected(
    field: str,
    value: Any,
    match: str,
) -> None:
    payload = _plan().to_dict()

    payload[field] = value

    with pytest.raises(
        ValueError,
        match=match,
    ):
        PlanEntity.from_dict(
            payload
        )

@pytest.mark.parametrize(
    "field",
    (
        "plan_id",
        "idempotency_key",
        "tenant_id",
        "kennel_shard",
        "seal_nonce",
        "proof_hash",
        "merkle_root",
        "catalogue_version",
        "created_at",
    ),
)
def test_protected_fields_cannot_update(
    field: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="protected or unknown",
    ):
        _plan().update(
            {
                field: "FORBIDDEN"
            }
        )


def test_unknown_field_cannot_update() -> None:
    with pytest.raises(
        ValueError,
        match="protected or unknown",
    ):
        _plan().update(
            {
                "callerPriceAuthority":
                    True
            }
        )


def test_commercial_update_versions_state() -> None:
    original = _plan()

    updated = original.update(
        {
            "price": 3500,
            "features": [
                "FEATURE_A",
                "FEATURE_B",
                "FEATURE_C",
            ],
        }
    )

    assert (
        updated.plan_id
        == original.plan_id
    )

    assert (
        updated.idempotency_key
        == original.idempotency_key
    )

    assert (
        updated.catalogue_version
        == 2
    )

    assert (
        updated.price
        == 3500.0
    )

    assert (
        updated.proof_hash
        != original.proof_hash
    )


def test_empty_update_returns_same_value() -> None:
    plan = _plan()

    assert (
        plan.update({})
        is plan
    )


def test_audit_append_preserves_state_proof() -> None:
    original = _plan()

    audited = original.add_audit_entry(
        AuditAction.UPDATE,
        user="PLAN-CERT",
        reason="commercial review",
    )

    assert len(
        audited.audit_trail
    ) == 1

    assert (
        audited.audit_trail[0].state_proof_hash
        == original.proof_hash
    )

    assert (
        audited.proof_hash
        == original.proof_hash
    )

    assert (
        audited.integrity_root
        != original.integrity_root
    )

    assert (
        audited.audit_trail[0].integrity_status
        == "CURRENT_V2_CHAIN_CONSISTENT"
    )

def test_legacy_missing_identity_is_deterministic() -> None:
    payload = {
        "name": "Legacy",
        "price": 999,
        "currency": "ZAR",
        "billing_frequency": "monthly",
        "plan_type": "PROFESSIONAL",
        "created_at":
            "2026-09-03T00:00:00+00:00",
        "updated_at":
            "2026-09-03T00:00:00+00:00",
    }

    first = PlanEntity.migrate_legacy_dict(
        payload
    )

    second = PlanEntity.migrate_legacy_dict(
        payload
    )

    assert first.plan_id == second.plan_id
    assert (
        first.idempotency_key
        == second.idempotency_key
    )
    assert (
        first.seal_nonce
        == second.seal_nonce
    )
    assert (
        first.proof_hash
        == second.proof_hash
    )
    assert (
        first.integrity_root
        == second.integrity_root
    )

def test_dual_case_legacy_hydration() -> None:
    payload = {
        "name": "Legacy Camel",
        "price": 1250,
        "currency": "zar",
        "billingFrequency": "annual",
        "planType": "ENTERPRISE",
        "trialDays": 7,
        "tenantId": "TENANT-CERT",
        "kennelShard": "EOS_PRIMARY",
        "createdAt":
            "2026-09-03T00:00:00+00:00",
        "updatedAt":
            "2026-09-03T00:00:00+00:00",
    }

    plan = PlanEntity.migrate_legacy_dict(
        payload
    )

    assert (
        plan.billing_frequency
        is PlanFrequency.ANNUAL
    )

    assert (
        plan.plan_type
        is PlanTiers.ENTERPRISE
    )

    assert plan.trial_days == 7
    assert plan.tenant_id == "TENANT-CERT"

def test_evidence_package_redacts_sensitive_metadata() -> None:
    plan = _plan(
        metadata={
            "market": "ZA",
            "email":
                "private@example.invalid",
            "phone": "000",
            "pii": "secret",
        }
    )

    evidence = (
        plan.generate_evidence_package()
    )

    assert (
        evidence[
            "catalogueVersion"
        ]
        == 1
    )

    assert (
        evidence["features"]
        == [
            "FEATURE_A",
            "FEATURE_B",
        ]
    )

    assert (
        evidence["metadata"]
        == {
            "market": "ZA"
        }
    )

    assert len(
        evidence[
            "evidenceSeal"
        ]
    ) == 128


@pytest.mark.parametrize(
    "value",
    (
        Decimal("1.0000000000000001"),
        "1.0000000000000001",
        Decimal("1e-400"),
        "1e-400",
    ),
)
def test_lossy_float_price_projection_fails_closed(
    value: Any,
) -> None:
    with pytest.raises(
        ValueError,
        match="losslessly",
    ):
        _plan(
            price=value
        )


def test_exact_decimal_price_survives_float_boundary() -> None:
    plan = _plan(
        price=Decimal("0.1")
    )

    assert plan.price == 0.1


def test_legacy_identity_binds_tenant_and_complete_state() -> None:
    base: dict[str, Any] = {
        "name": "Legacy Identity",
        "price": 100,
        "currency": "ZAR",
        "billing_frequency": "monthly",
        "plan_type": "PROFESSIONAL",
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
    }

    tenant_a = PlanEntity.migrate_legacy_dict(
        {
            **base,
            "tenant_id": "TENANT-A",
            "features": [
                "FEATURE_A",
            ],
        }
    )

    tenant_b = PlanEntity.migrate_legacy_dict(
        {
            **base,
            "tenant_id": "TENANT-B",
            "features": [
                "FEATURE_A",
            ],
        }
    )

    feature_variant = PlanEntity.migrate_legacy_dict(
        {
            **base,
            "tenant_id": "TENANT-A",
            "features": [
                "FEATURE_B",
            ],
        }
    )

    assert (
        tenant_a.plan_id
        != tenant_b.plan_id
    )

    assert (
        tenant_a.plan_id
        != feature_variant.plan_id
    )

    assert (
        tenant_a.idempotency_key
        != tenant_b.idempotency_key
    )

    assert (
        tenant_a.idempotency_key
        != feature_variant.idempotency_key
    )

def _legacy_evidence_payload() -> dict[str, Any]:
    tenant_id = "TENANT-LEGACY"
    seal_nonce = "legacy-seal"
    legacy_proof = "A" * 128

    legacy_merkle = sha3_512(
        (
            f"{tenant_id}"
            f"|{legacy_proof}"
            f"|{seal_nonce}"
        ).encode(
            "utf-8"
        )
    ).hexdigest().upper()

    return {
        "plan_id": "WILSYPLAN-AAAABBBB",
        "name": "Legacy Provenance",
        "price": 100,
        "currency": "ZAR",
        "billing_frequency": "monthly",
        "plan_type": "PROFESSIONAL",
        "idempotency_key": "LEGACY-IDEMPOTENCY",
        "tenant_id": tenant_id,
        "seal_nonce": seal_nonce,
        "proof_hash": legacy_proof,
        "merkle_root": legacy_merkle,
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
    }


def test_legacy_proof_is_migrated_not_treated_as_current() -> None:
    payload = _legacy_evidence_payload()

    plan = PlanEntity.migrate_legacy_dict(
        payload
    )

    assert plan.proof_version == 2

    assert (
        plan.legacy_proof_hash
        == payload["proof_hash"]
    )

    assert (
        plan.legacy_envelope_digest
        == payload["merkle_root"]
    )

    assert (
        plan.proof_hash
        != payload["proof_hash"]
    )

    assert (
        plan.integrity_root
        != payload["merkle_root"]
    )

    assert (
        plan.legacy_evidence_status
        == "LEGACY_V1_ENVELOPE_CONSISTENT_CONTENT_UNVERIFIED"
    )

def test_invalid_legacy_merkle_fails_closed() -> None:
    payload = _legacy_evidence_payload()

    payload["merkle_root"] = (
        "B" * 128
    )

    with pytest.raises(
        ValueError,
        match="legacy envelope",
    ):
        PlanEntity.migrate_legacy_dict(
            payload
        )

@pytest.mark.parametrize(
    ("field", "value"),
    (
        (
            "user",
            "MALLORY",
        ),
        (
            "timestamp",
            "2000-01-01T00:00:00+00:00",
        ),
        (
            "reason",
            "forged reason",
        ),
        (
            "metadata",
            {
                "forged": True,
            },
        ),
        (
            "proofHash",
            "F" * 128,
        ),
    ),
)
def test_current_audit_event_tamper_fails_closed(
    field: str,
    value: Any,
) -> None:
    audited = _plan().add_audit_entry(
        AuditAction.UPDATE,
        user="ALICE",
        reason="review",
        metadata={
            "source": "certificate",
        },
    )

    payload = audited.to_dict()

    payload[
        "audit_trail"
    ][0][field] = value

    with pytest.raises(
        ValueError,
    ):
        PlanEntity.from_dict(
            payload
        )


def test_audit_reordering_fails_closed() -> None:
    first = _plan().add_audit_entry(
        AuditAction.UPDATE,
        user="ALICE",
        reason="first",
    )

    second = first.add_audit_entry(
        AuditAction.UPDATE,
        user="BOB",
        reason="second",
    )

    payload = second.to_dict()

    payload["audit_trail"] = list(
        reversed(
            payload["audit_trail"]
        )
    )

    with pytest.raises(
        ValueError,
        match="predecessor",
    ):
        PlanEntity.from_dict(
            payload
        )


def test_audit_truncation_fails_closed() -> None:
    first = _plan().add_audit_entry(
        AuditAction.UPDATE,
        user="ALICE",
        reason="first",
    )

    second = first.add_audit_entry(
        AuditAction.UPDATE,
        user="BOB",
        reason="second",
    )

    payload = second.to_dict()

    payload["audit_trail"] = (
        payload["audit_trail"][:1]
    )

    with pytest.raises(
        ValueError,
        match="integrity_root",
    ):
        PlanEntity.from_dict(
            payload
        )

def test_legacy_audit_is_separated_from_current_trust_class() -> None:
    payload = _legacy_evidence_payload()

    payload["audit_trail"] = [
        {
            "action": "update",
            "timestamp":
                "2025-12-31T00:00:00+00:00",
            "user": "LEGACY-ACTOR",
            "reason": "legacy event",
            "metadata": {
                "source": "legacy",
            },
            "proofHash": "C" * 128,
        }
    ]

    plan = PlanEntity.migrate_legacy_dict(
        payload
    )

    assert plan.audit_trail == ()
    assert len(
        plan.legacy_audit_trail
    ) == 1

    assert (
        plan.legacy_audit_trail[0]["user"]
        == "LEGACY-ACTOR"
    )

    persisted = plan.to_dict()

    persisted[
        "legacy_audit_trail"
    ][0]["user"] = "MALLORY"

    with pytest.raises(
        ValueError,
        match="proof_hash",
    ):
        PlanEntity.from_dict(
            persisted
        )

def test_current_plan_registry_user_context_compatibility() -> None:
    PlanRegistry._plans.clear()

    try:
        created = PlanRegistry.create(
            {
                "name": "Registry Compatibility",
                "price": 100,
                "currency": "ZAR",
                "billingFrequency": "monthly",
                "planType": "PROFESSIONAL",
                "idempotencyKey": "P1R4-REGISTRY-COMPAT",
            }
        )

        assert (
            created["success"]
            is True
        )

        plan = created["plan"]

        updated = PlanRegistry.update(
            plan.plan_id,
            {
                "price": 200,
                "user": "OPERATOR",
            },
        )

        assert (
            updated["success"]
            is True
        )

        updated_plan = (
            updated["plan"]
        )

        assert (
            updated_plan.price
            == 200.0
        )

        assert (
            updated_plan.catalogue_version
            == 2
        )

        assert (
            updated_plan.audit_trail[-1].user
            == "OPERATOR"
        )

        assert (
            "user"
            not in updated_plan.to_dict()
        )

    finally:
        PlanRegistry._plans.clear()



def test_from_dict_requires_explicit_current_version() -> None:
    payload = _plan().to_dict()
    payload.pop("proof_version")

    with pytest.raises(
        ValueError,
        match="explicit legacy migration",
    ):
        PlanEntity.from_dict(payload)


def test_explicit_v1_plan_downgrade_is_rejected() -> None:
    payload = _plan().to_dict()
    payload["proof_version"] = 1

    with pytest.raises(
        ValueError,
        match="unsupported persisted plan proof version",
    ):
        PlanEntity.from_dict(payload)


@pytest.mark.parametrize(
    "field",
    (
        "proof_hash",
        "integrity_root",
        "state_proof_lineage",
    ),
)
def test_current_hydration_requires_complete_evidence(
    field: str,
) -> None:
    payload = _plan().to_dict()
    payload.pop(field)

    if field == "integrity_root":
        payload.pop("merkle_root")

    with pytest.raises(ValueError):
        PlanEntity.from_dict(payload)


def test_current_audit_cannot_be_relabelled_legacy() -> None:
    plan = _plan().add_audit_entry(
        AuditAction.UPDATE,
        user="ALICE",
        reason="current event",
    )

    payload = plan.to_dict()
    payload["audit_trail"][0]["proofVersion"] = 1

    with pytest.raises(
        ValueError,
        match="proofVersion 2",
    ):
        PlanEntity.from_dict(payload)


def test_arbitrary_audit_state_hash_is_rejected() -> None:
    plan = _plan()

    arbitrary = AuditEntry(
        action=AuditAction.UPDATE,
        timestamp=datetime.now(
            timezone.utc
        ),
        user="MALLORY",
        reason="forged state",
        metadata={},
        proof_version=2,
        plan_id=plan.plan_id,
        state_proof_hash="A" * 128,
        catalogue_version=
            plan.catalogue_version,
        previous_proof_hash="",
    )

    with pytest.raises(
        ValueError,
        match="does not resolve",
    ):
        replace(
            plan,
            audit_trail=(arbitrary,),
            integrity_root="",
        )


def test_state_proof_lineage_tracks_commercial_versions() -> None:
    first = _plan()

    second = first.update(
        {
            "price": 2000,
        }
    )

    third = second.update(
        {
            "price": 3000,
        }
    )

    assert first.state_proof_lineage == (
        (
            1,
            first.proof_hash,
        ),
    )

    assert second.state_proof_lineage == (
        (
            1,
            first.proof_hash,
        ),
        (
            2,
            second.proof_hash,
        ),
    )

    assert third.state_proof_lineage == (
        (
            1,
            first.proof_hash,
        ),
        (
            2,
            second.proof_hash,
        ),
        (
            3,
            third.proof_hash,
        ),
    )


def test_audit_event_resolves_to_catalogue_lineage() -> None:
    updated = _plan().update(
        {
            "price": 2000,
        }
    )

    audited = updated.add_audit_entry(
        AuditAction.UPDATE,
        user="ALICE",
        reason="version two review",
    )

    entry = audited.audit_trail[-1]

    assert entry.catalogue_version == 2

    assert (
        entry.state_proof_hash
        == dict(
            audited.state_proof_lineage
        )[2]
    )


def test_state_lineage_tamper_fails_closed() -> None:
    plan = _plan().update(
        {
            "price": 2000,
        }
    )

    payload = plan.to_dict()

    payload[
        "state_proof_lineage"
    ][0]["proofHash"] = "A" * 128

    with pytest.raises(
        ValueError,
        match="state proof lineage does not match verified state history",
    ):
        PlanEntity.from_dict(
            payload
        )

def test_legacy_migration_rejects_current_schema_record() -> None:
    payload = _plan().to_dict()
    payload.pop("proof_version")

    with pytest.raises(
        ValueError,
        match="current-schema markers",
    ):
        PlanEntity.migrate_legacy_dict(
            payload
        )


def test_registry_preserves_high_precision_price_for_domain_rejection() -> None:
    PlanRegistry._plans.clear()

    try:
        result = PlanRegistry.create(
            {
                "name":
                    "Precision Rejection",
                "price":
                    Decimal(
                        "1.0000000000000000001"
                    ),
                "currency":
                    "ZAR",
                "billingFrequency":
                    "monthly",
                "planType":
                    "PROFESSIONAL",
                "idempotencyKey":
                    "P1R5-PRECISION",
            }
        )

        assert result["success"] is False
        assert "losslessly" in result["error"]

    finally:
        PlanRegistry._plans.clear()


def test_signed_zero_canonicalizes_to_positive_zero() -> None:
    negative = _plan(
        price=Decimal("-0")
    )

    positive = _plan(
        price=Decimal("0")
    )

    assert negative.price == 0.0
    assert str(negative.price) == "0.0"

    assert (
        negative.proof_hash
        == positive.proof_hash
    )


def test_integrity_root_semantics_are_explicitly_non_merkle() -> None:
    plan = _plan()

    package = (
        plan.generate_evidence_package()
    )

    assert (
        package["integrityRoot"]
        == plan.integrity_root
    )

    assert (
        package[
            "integrityRootSemantics"
        ]
        == "SHA3_512_FLAT_ENVELOPE_DIGEST_NOT_MERKLE_TREE"
    )

    assert (
        plan.merkle_root
        == plan.integrity_root
    )


def test_registry_health_version_matches_governance() -> None:
    health = PlanRegistry.health_check()

    assert (
        health["version"]
        == "v1.0.3-DOMAIN-PRICE-PASSTHROUGH"
    )

@pytest.mark.parametrize(
    ("snake_version", "camel_version"),
    (
        (
            2,
            1,
        ),
        (
            1,
            2,
        ),
    ),
)
def test_conflicting_plan_proof_version_aliases_fail_closed(
    snake_version: int,
    camel_version: int,
) -> None:
    payload = _plan().to_dict()

    payload["proof_version"] = (
        snake_version
    )

    payload["proofVersion"] = (
        camel_version
    )

    with pytest.raises(
        ValueError,
        match="conflicting plan proof-version aliases",
    ):
        PlanEntity.from_dict(
            payload
        )

@pytest.mark.parametrize(
    ("camel_version", "snake_version"),
    (
        (
            2,
            1,
        ),
        (
            1,
            2,
        ),
    ),
)
def test_conflicting_audit_proof_version_aliases_fail_closed(
    camel_version: int,
    snake_version: int,
) -> None:
    plan = _plan().add_audit_entry(
        AuditAction.UPDATE,
        user="ALICE",
        reason="alias-conflict",
    )

    audit_payload = (
        plan.audit_trail[0].to_dict()
    )

    audit_payload["proofVersion"] = (
        camel_version
    )

    audit_payload["proof_version"] = (
        snake_version
    )

    with pytest.raises(
        ValueError,
        match="conflicting audit proof-version aliases",
    ):
        AuditEntry.from_dict(
            audit_payload
        )

def test_legacy_migration_rejects_embedded_current_v2_audit() -> None:
    current = _plan().add_audit_entry(
        AuditAction.UPDATE,
        user="ALICE",
        reason="current-v2",
    )

    legacy_payload: dict[str, Any] = {
        "name": "Legacy Outer",
        "price": 100,
        "currency": "ZAR",
        "billingFrequency": "monthly",
        "planType": "PROFESSIONAL",
        "createdAt": "2026-01-01T00:00:00+00:00",
        "updatedAt": "2026-01-01T00:00:00+00:00",
        "auditTrail": [
            current.audit_trail[0].to_dict()
        ],
    }

    with pytest.raises(
        ValueError,
        match="current-v2 audit evidence",
    ):
        PlanEntity.migrate_legacy_dict(
            legacy_payload
        )


def test_equal_dual_plan_and_audit_proof_version_aliases_are_current() -> None:
    plan_payload = _plan().to_dict()

    plan_payload["proofVersion"] = 2

    hydrated_plan = PlanEntity.from_dict(
        plan_payload
    )

    assert (
        hydrated_plan.proof_version
        == 2
    )

    audited = _plan().add_audit_entry(
        AuditAction.UPDATE,
        user="ALICE",
        reason="equal-version-aliases",
    )

    audit_payload = (
        audited.audit_trail[0].to_dict()
    )

    audit_payload["proof_version"] = 2

    hydrated_audit = AuditEntry.from_dict(
        audit_payload
    )

    assert (
        hydrated_audit.proof_version
        == 2
    )


def test_current_audit_requires_explicit_catalogue_version() -> None:
    audited = _plan().add_audit_entry(
        AuditAction.UPDATE,
        user="ALICE",
        reason="catalogue-required",
    )

    payload = (
        audited.audit_trail[0].to_dict()
    )

    payload.pop(
        "catalogueVersion"
    )

    with pytest.raises(
        ValueError,
        match="requires catalogueVersion",
    ):
        AuditEntry.from_dict(
            payload
        )


@pytest.mark.parametrize(
    ("camel_version", "snake_version"),
    (
        (
            1,
            2,
        ),
        (
            2,
            1,
        ),
    ),
)
def test_conflicting_audit_catalogue_version_aliases_fail_closed(
    camel_version: int,
    snake_version: int,
) -> None:
    audited = _plan().add_audit_entry(
        AuditAction.UPDATE,
        user="ALICE",
        reason="catalogue-conflict",
    )

    payload = (
        audited.audit_trail[0].to_dict()
    )

    payload["catalogueVersion"] = (
        camel_version
    )

    payload["catalogue_version"] = (
        snake_version
    )

    with pytest.raises(
        ValueError,
        match="conflicting audit catalogue-version aliases",
    ):
        AuditEntry.from_dict(
            payload
        )

def test_equal_dual_audit_catalogue_version_aliases_are_accepted() -> None:
    audited = _plan().add_audit_entry(
        AuditAction.UPDATE,
        user="ALICE",
        reason="catalogue-equal",
    )

    payload = (
        audited.audit_trail[0].to_dict()
    )

    payload["catalogue_version"] = (
        payload["catalogueVersion"]
    )

    hydrated = AuditEntry.from_dict(
        payload
    )

    assert (
        hydrated.catalogue_version
        == payload["catalogueVersion"]
    )


@pytest.mark.parametrize(
    "catalogue_value",
    (
        None,
        True,
        1.5,
        0,
        -1,
    ),
)
def test_invalid_current_audit_catalogue_values_fail_closed(
    catalogue_value: Any,
) -> None:
    audited = _plan().add_audit_entry(
        AuditAction.UPDATE,
        user="ALICE",
        reason="invalid-catalogue",
    )

    payload = (
        audited.audit_trail[0].to_dict()
    )

    payload["catalogueVersion"] = (
        catalogue_value
    )

    with pytest.raises(
        (
            TypeError,
            ValueError,
        )
    ):
        AuditEntry.from_dict(
            payload
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "user",
        "reason",
        "metadata",
        "previousProofHash",
    ),
)
def test_current_audit_requires_complete_persisted_material(
    field_name: str,
) -> None:
    audited = _plan().add_audit_entry(
        AuditAction.UPDATE,
        user="ALICE",
        reason="complete-material",
        metadata={
            "source": "certificate",
        },
    )

    payload = (
        audited.audit_trail[0].to_dict()
    )

    payload.pop(
        field_name
    )

    with pytest.raises(
        ValueError,
        match="requires",
    ):
        AuditEntry.from_dict(
            payload
        )


def test_current_hydration_requires_state_history() -> None:
    payload = _plan().to_dict()

    payload.pop(
        "state_history"
    )

    with pytest.raises(
        ValueError,
        match="canonical state history",
    ):
        PlanEntity.from_dict(
            payload
        )


def test_fabricated_historical_hash_fails_closed() -> None:
    plan = (
        _plan()
        .update(
            {
                "price": 2000,
            }
        )
        .update(
            {
                "price": 3000,
            }
        )
    )

    payload = plan.to_dict()

    payload[
        "state_history"
    ][0]["proofHash"] = "A" * 128

    with pytest.raises(
        ValueError,
        match="state history proof",
    ):
        PlanEntity.from_dict(
            payload
        )


def test_historical_state_preimage_tamper_fails_closed() -> None:
    plan = (
        _plan()
        .update(
            {
                "price": 2000,
            }
        )
        .update(
            {
                "price": 3000,
            }
        )
    )

    payload = plan.to_dict()

    payload[
        "state_history"
    ][0]["state"]["price"] = 9999

    with pytest.raises(
        ValueError,
        match="state history proof",
    ):
        PlanEntity.from_dict(
            payload
        )


def test_gapped_state_history_fails_closed() -> None:
    plan = (
        _plan()
        .update(
            {
                "price": 2000,
            }
        )
        .update(
            {
                "price": 3000,
            }
        )
    )

    payload = plan.to_dict()

    payload["state_history"] = [
        payload[
            "state_history"
        ][0],
        payload[
            "state_history"
        ][2],
    ]

    with pytest.raises(
        ValueError,
        match="contiguous",
    ):
        PlanEntity.from_dict(
            payload
        )


def test_out_of_order_state_history_fails_closed() -> None:
    plan = (
        _plan()
        .update(
            {
                "price": 2000,
            }
        )
        .update(
            {
                "price": 3000,
            }
        )
    )

    payload = plan.to_dict()

    payload[
        "state_history"
    ] = list(
        reversed(
            payload[
                "state_history"
            ]
        )
    )

    with pytest.raises(
        ValueError,
        match="contiguous",
    ):
        PlanEntity.from_dict(
            payload
        )


def test_future_state_history_fails_closed() -> None:
    version_two = (
        _plan().update(
            {
                "price": 2000,
            }
        )
    )

    version_three = (
        version_two.update(
            {
                "price": 3000,
            }
        )
    )

    payload = (
        version_two.to_dict()
    )

    payload["state_history"] = (
        version_three.to_dict()[
            "state_history"
        ]
    )

    payload[
        "state_proof_lineage"
    ] = (
        version_three.to_dict()[
            "state_proof_lineage"
        ]
    )

    with pytest.raises(
        ValueError,
        match="future catalogue version",
    ):
        PlanEntity.from_dict(
            payload
        )


def test_state_history_is_deep_frozen_and_serialization_detached() -> None:
    original = _plan().update(
        {
            "price": 2000,
        }
    )

    payload = (
        original.to_dict()
    )

    hydrated = (
        PlanEntity.from_dict(
            payload
        )
    )

    payload[
        "state_history"
    ][0]["state"]["metadata"]["market"] = "MUTATED"

    historical_state = (
        hydrated.state_history[0][
            "state"
        ]
    )

    assert (
        historical_state[
            "metadata"
        ][
            "market"
        ]
        == "ZA"
    )

    with pytest.raises(
        TypeError
    ):
        historical_state[
            "metadata"
        ][
            "market"
        ] = "MUTATED"


@pytest.mark.parametrize(
    "state_history_field",
    (
        "state_history",
        "stateHistory",
    ),
)
def test_legacy_migration_rejects_current_state_history_markers(
    state_history_field: str,
) -> None:
    payload: dict[str, Any] = {
        "name": "Legacy State History Boundary",
        "price": 100,
        "currency": "ZAR",
        "billing_frequency": "monthly",
        "plan_type": "PROFESSIONAL",
        "created_at":
            "2026-01-01T00:00:00+00:00",
        "updated_at":
            "2026-01-01T00:00:00+00:00",
        state_history_field: [
            {
                "catalogueVersion": 99,
                "proofHash": "A" * 128,
                "state": {
                    "fabricated": True,
                },
            }
        ],
    }

    with pytest.raises(
        ValueError,
        match="current-schema markers",
    ):
        PlanEntity.migrate_legacy_dict(
            payload
        )


def test_unsealed_legacy_provenance_survives_current_round_trip() -> None:
    payload: dict[str, Any] = {
        "name": "Unsealed Historical Plan",
        "price": 100,
        "currency": "ZAR",
        "billing_frequency": "monthly",
        "plan_type": "PROFESSIONAL",
        "created_at":
            "2026-01-01T00:00:00+00:00",
        "updated_at":
            "2026-01-01T00:00:00+00:00",
    }

    migrated = (
        PlanEntity.migrate_legacy_dict(
            payload
        )
    )

    assert (
        migrated.legacy_evidence_status
        == "LEGACY_UNVERSIONED_CONTENT_UNVERIFIED"
    )

    assert (
        migrated.legacy_proof_hash
        == ""
    )

    assert (
        migrated.legacy_envelope_digest
        == ""
    )

    hydrated = (
        PlanEntity.from_dict(
            migrated.to_dict()
        )
    )

    assert (
        hydrated.legacy_evidence_status
        == "LEGACY_UNVERSIONED_CONTENT_UNVERIFIED"
    )

    assert (
        hydrated.legacy_proof_hash
        == ""
    )

    assert (
        hydrated.legacy_envelope_digest
        == ""
    )

    assert (
        hydrated.proof_hash
        == migrated.proof_hash
    )

    assert (
        hydrated.integrity_root
        == migrated.integrity_root
    )


"""
INSTITUTIONAL CERTIFICATION SEAL

Artifact:
    tests/unit/test_plan_domain.py

Version:
    v1.0.10-PLAN-DOMAIN-CERT

Scope:
    PlanEntity commercial value contract only.

Production owner:
    tools/eos/saas/domain/plan.py

Tenant authority:
    NONE.

Financial execution:
    NONE — Kennel EOS remains exclusive.

Status:
    DIRECT CERTIFICATE SOURCE.

Certification date:
    2026-09-03

Pending work:
    None within this bounded certificate.

WILSY OS — ALL OR NOTHING.
"""
