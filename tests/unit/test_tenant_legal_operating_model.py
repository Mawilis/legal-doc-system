
"""Direct certificate for G7B Tenant Legal Operating Model."""
from __future__ import annotations

# TITLE: Tenant Legal Operating Model Direct Domain Certificate
# VERSION: v1.0.1-G7B-TENANT-LEGAL-OPERATING-MODEL-CERT
# AUTHORITY: Direct proof of immutable exact-tenant Legal operating-model configuration semantics only.
# EPITOME: Certify canonical catalogue selection, tenant isolation, revision integrity, round-trip truth, and authority exclusions.
# ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_legal_operating_model.py
# COLLABORATION / OWNERSHIP: G7B pure-domain certificate only; registry, service, IAM, workflow, commercial, and financial authorities remain external.
# CLASSIFICATION: SOVEREIGN DOMAIN CERTIFICATE
# CHANGELOG: v1.0.1 completes sovereign certificate metadata and terminal sealing without changing behavioral assertions.
# COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
# SECURITY / PRIVACY POSTURE: Synthetic opaque tenant identifiers only; no credentials, customer PII, or authority-bearing secrets.
# TENANT BOUNDARY: Exact non-pseudo synthetic tenant identities only.
# AUTHORITY BOUNDARY: Configuration proof only; no authentication, IAM, professional, matter, workflow, assignment, supervision, entitlement, billing, payment, settlement, or execution authority.
# FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively executes or settles.


from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.domain.legal_operating_catalogue import (
    CATALOGUE_FINGERPRINT,
)
from tools.eos.legal_operations.domain.tenant_legal_operating_model import (
    SCHEMA,
    VERSION,
    TenantLegalOperatingModel,
    TenantLegalOperatingModelError,
)


NOW = datetime(
    2026,
    10,
    12,
    21,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)


def model(**changes: object) -> TenantLegalOperatingModel:
    values: dict[str, object] = {
        "tenant_id": "tenant-legal-global-1",
        "operating_model_id": "lom-1",
        "revision": 1,
        "activated_item_ids": (
            "PERSONA_PARTNER",
            "PRACTICE_DISPUTES",
            "RISK_CONFLICTS",
        ),
        "effective_from": NOW,
        "supersedes_operating_model_id": None,
    }
    values.update(changes)
    return TenantLegalOperatingModel(**values)  # type: ignore[arg-type]


def test_identity_is_exact() -> None:
    assert VERSION == "v1.0.1-G7B-TENANT-LEGAL-OPERATING-MODEL"
    assert SCHEMA == "WILSY-TENANT-LEGAL-OPERATING-MODEL/V1"


def test_valid_model_is_immutable_and_canonical() -> None:
    value = model(
        activated_item_ids=(
            "RISK_CONFLICTS",
            "PERSONA_PARTNER",
            "PRACTICE_DISPUTES",
        )
    )
    assert value.activated_item_ids == (
        "PERSONA_PARTNER",
        "PRACTICE_DISPUTES",
        "RISK_CONFLICTS",
    )
    assert value.effective_from.microsecond == 123456
    assert value.catalogue_fingerprint == CATALOGUE_FINGERPRINT
    assert len(value.fingerprint) == 128


@pytest.mark.parametrize(
    "tenant_id",
    ("default", "global", "root", "*"),
)
def test_pseudo_tenants_reject(
    tenant_id: str,
) -> None:
    with pytest.raises(
        TenantLegalOperatingModelError,
        match="G7B_TENANT_REQUIRED",
    ):
        model(tenant_id=tenant_id)


def test_unknown_catalogue_item_rejects() -> None:
    with pytest.raises(
        TenantLegalOperatingModelError,
        match="G7B_ACTIVATED_ITEM_UNKNOWN",
    ):
        model(
            activated_item_ids=(
                "PERSONA_PARTNER",
                "NOT_REAL",
            )
        )


def test_duplicate_catalogue_item_rejects() -> None:
    with pytest.raises(
        TenantLegalOperatingModelError,
        match="G7B_ACTIVATED_ITEM_DUPLICATE",
    ):
        model(
            activated_item_ids=(
                "PERSONA_PARTNER",
                "PERSONA_PARTNER",
            )
        )


@pytest.mark.parametrize(
    "revision",
    (0, -1, True),
)
def test_revision_rejects_invalid_values(
    revision: object,
) -> None:
    with pytest.raises(
        TenantLegalOperatingModelError,
        match="G7B_REVISION_INVALID",
    ):
        model(revision=revision)


def test_naive_time_rejects() -> None:
    with pytest.raises(
        TenantLegalOperatingModelError,
        match="G7B_EFFECTIVE_FROM_INVALID",
    ):
        model(
            effective_from=datetime(
                2026,
                10,
                12,
                21,
                0,
                0,
            )
        )


def test_microseconds_are_preserved() -> None:
    value = model()
    assert value.effective_from.isoformat().endswith(
        "21:00:00.123456+00:00"
    )


def test_self_supersession_rejects() -> None:
    with pytest.raises(
        TenantLegalOperatingModelError,
        match="G7B_SUPERSESSION_INVALID",
    ):
        model(
            operating_model_id="lom-1",
            supersedes_operating_model_id="lom-1",
        )


def test_catalogue_fingerprint_drift_rejects() -> None:
    with pytest.raises(
        TenantLegalOperatingModelError,
        match="G7B_CATALOGUE_BINDING_INVALID",
    ):
        model(
            catalogue_fingerprint="a" * 128,
        )


def test_round_trip_preserves_exact_truth() -> None:
    original = model()
    restored = TenantLegalOperatingModel.from_dict(
        original.to_dict()
    )
    assert restored == original


def test_extra_field_rejects() -> None:
    payload = model().to_dict()
    payload["extra"] = "x"

    with pytest.raises(
        TenantLegalOperatingModelError,
        match="G7B_PAYLOAD_SCHEMA_INVALID",
    ):
        TenantLegalOperatingModel.from_dict(payload)


def test_missing_field_rejects() -> None:
    payload = model().to_dict()
    del payload["revision"]

    with pytest.raises(
        TenantLegalOperatingModelError,
        match="G7B_PAYLOAD_SCHEMA_INVALID",
    ):
        TenantLegalOperatingModel.from_dict(payload)


def test_corrupt_fingerprint_rejects() -> None:
    payload = model().to_dict()
    payload["fingerprint"] = "b" * 128

    with pytest.raises(
        TenantLegalOperatingModelError,
        match="G7B_FINGERPRINT_MISMATCH",
    ):
        TenantLegalOperatingModel.from_dict(payload)


def test_model_contains_no_principal_or_iam_authority() -> None:
    keys = set(model().to_dict())
    forbidden = {
        "principal_id",
        "role_id",
        "business_role",
        "permission",
        "authorization",
        "professional_status",
        "regulatory_appointment",
        "plan_id",
        "subscription_id",
        "entitlement_id",
        "price",
        "payment",
        "financial_execution",
    }
    assert not keys & forbidden


def test_empty_activation_is_valid_configuration() -> None:
    value = model(activated_item_ids=())
    assert value.activated_item_ids == ()


# ARTIFACT: test_tenant_legal_operating_model.py
# VERSION: v1.0.1-G7B-TENANT-LEGAL-OPERATING-MODEL-CERT
# END OF WILSY OS SOVEREIGN CERTIFICATE
