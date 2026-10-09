"""Direct certificate for the Legal Evidence capacity-policy contract.

VERSION: v1.0.0-L10A2Q-P1A-LEGAL-EVIDENCE-CAPACITY-POLICY-CONTRACT-CERT
AUTHORITY: Wilsy OS Core Governance
CERTIFICATION / UPDATE DATE: 2026-09-29
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import re

import pytest

from tools.eos.saas.billing.legal_evidence_capacity_policy_contract import (
    FEATURE_CAPABILITY_FIELDS,
    NUMERIC_CAPACITY_FIELDS,
    POLICY_IDENTITY,
    PROFILE_ORDER,
    SCHEMA,
    VERSION,
    LegalEvidenceCapacityPolicy,
    LegalEvidenceCapacityPolicyContractError,
    LegalEvidenceCapacityProfile,
    LegalEvidenceRetentionClass,
    validate_profile_progression,
)


def policy(
    profile: LegalEvidenceCapacityProfile,
    *,
    scale: int,
    retention: LegalEvidenceRetentionClass,
    legal_hold: bool = False,
    bulk: bool = False,
    api: bool = False,
    external: bool = False,
) -> LegalEvidenceCapacityPolicy:
    """Build synthetic sizing evidence; numbers are not canonical commerce."""
    return LegalEvidenceCapacityPolicy(
        profile=profile,
        single_file_max_bytes=scale * 10,
        tenant_storage_limit_bytes=scale * 100,
        monthly_ingress_limit_bytes=scale * 50,
        max_document_versions=scale,
        ocr_page_allowance=scale * 20,
        ai_document_processing_allowance=scale * 5,
        retention_class=retention,
        legal_hold_available=legal_hold,
        bulk_ingest_available=bulk,
        api_ingest_available=api,
        external_client_upload_available=external,
    )


def valid_set() -> tuple[LegalEvidenceCapacityPolicy, ...]:
    return (
        policy(
            LegalEvidenceCapacityProfile.STARTER,
            scale=1,
            retention=LegalEvidenceRetentionClass.STANDARD,
        ),
        policy(
            LegalEvidenceCapacityProfile.GROWTH,
            scale=2,
            retention=LegalEvidenceRetentionClass.ENHANCED,
            external=True,
        ),
        policy(
            LegalEvidenceCapacityProfile.INSTITUTIONAL,
            scale=4,
            retention=LegalEvidenceRetentionClass.GOVERNED,
            legal_hold=True,
            bulk=True,
            api=True,
            external=True,
        ),
        policy(
            LegalEvidenceCapacityProfile.FOUNDER_ENTERPRISE,
            scale=4,
            retention=LegalEvidenceRetentionClass.GOVERNED,
            legal_hold=True,
            bulk=True,
            api=True,
            external=True,
        ),
    )


def test_closed_profile_and_retention_vocabularies() -> None:
    assert tuple(LegalEvidenceCapacityProfile) == PROFILE_ORDER
    assert tuple(LegalEvidenceRetentionClass) == (
        LegalEvidenceRetentionClass.STANDARD,
        LegalEvidenceRetentionClass.ENHANCED,
        LegalEvidenceRetentionClass.GOVERNED,
    )


def test_contract_dimensions_match_l10a2q_map() -> None:
    assert NUMERIC_CAPACITY_FIELDS == (
        "single_file_max_bytes",
        "tenant_storage_limit_bytes",
        "monthly_ingress_limit_bytes",
        "max_document_versions",
        "ocr_page_allowance",
        "ai_document_processing_allowance",
    )
    assert FEATURE_CAPABILITY_FIELDS == (
        "legal_hold_available",
        "bulk_ingest_available",
        "api_ingest_available",
        "external_client_upload_available",
    )


def test_descriptor_has_deterministic_sha3_512_round_trip() -> None:
    value = valid_set()[1]
    assert re.fullmatch(r"[0-9a-f]{128}", value.fingerprint)
    assert LegalEvidenceCapacityPolicy.from_dict(value.to_dict()) == value
    assert value.to_dict()["schema"] == SCHEMA
    assert value.to_dict()["policy_version"] == VERSION
    assert value.to_dict()["policy_identity"] == POLICY_IDENTITY


@pytest.mark.parametrize(
    "field",
    NUMERIC_CAPACITY_FIELDS,
)
def test_numeric_capacity_requires_positive_integer(field: str) -> None:
    value = valid_set()[0]
    with pytest.raises(LegalEvidenceCapacityPolicyContractError):
        replace(value, **{field: 0}, fingerprint="")
    with pytest.raises(LegalEvidenceCapacityPolicyContractError):
        replace(value, **{field: True}, fingerprint="")


@pytest.mark.parametrize(
    "field",
    FEATURE_CAPABILITY_FIELDS,
)
def test_feature_capability_requires_exact_boolean(field: str) -> None:
    value = valid_set()[0]
    with pytest.raises(LegalEvidenceCapacityPolicyContractError):
        replace(value, **{field: 1}, fingerprint="")


def test_single_file_cannot_exceed_tenant_storage_limit() -> None:
    value = valid_set()[0]
    with pytest.raises(
        LegalEvidenceCapacityPolicyContractError,
        match="FILE_EXCEEDS_STORAGE_LIMIT",
    ):
        replace(
            value,
            single_file_max_bytes=value.tenant_storage_limit_bytes + 1,
            fingerprint="",
        )


def test_complete_profile_progression_is_monotonic() -> None:
    assert validate_profile_progression(valid_set()) == valid_set()


def test_numeric_regression_fails_closed() -> None:
    values = list(valid_set())
    values[2] = replace(
        values[2],
        monthly_ingress_limit_bytes=1,
        fingerprint="",
    )
    with pytest.raises(
        LegalEvidenceCapacityPolicyContractError,
        match="CAPACITY_REGRESSION",
    ):
        validate_profile_progression(values)


def test_feature_regression_fails_closed() -> None:
    values = list(valid_set())
    values[3] = replace(
        values[3],
        api_ingest_available=False,
        fingerprint="",
    )
    with pytest.raises(
        LegalEvidenceCapacityPolicyContractError,
        match="FEATURE_REGRESSION",
    ):
        validate_profile_progression(values)


def test_retention_regression_fails_closed() -> None:
    values = list(valid_set())
    values[3] = replace(
        values[3],
        retention_class=LegalEvidenceRetentionClass.STANDARD,
        fingerprint="",
    )
    with pytest.raises(
        LegalEvidenceCapacityPolicyContractError,
        match="RETENTION_REGRESSION",
    ):
        validate_profile_progression(values)


def test_missing_duplicate_or_wrong_order_profile_set_rejects() -> None:
    values = valid_set()
    with pytest.raises(
        LegalEvidenceCapacityPolicyContractError,
        match="PROFILE_SET_INCOMPLETE",
    ):
        validate_profile_progression(values[:-1])

    wrong = (values[1], values[0], values[2], values[3])
    with pytest.raises(
        LegalEvidenceCapacityPolicyContractError,
        match="PROFILE_ORDER_INVALID",
    ):
        validate_profile_progression(wrong)


def test_unknown_profile_retention_and_schema_fail_closed() -> None:
    value = valid_set()[0]
    with pytest.raises(LegalEvidenceCapacityPolicyContractError):
        replace(value, profile="ULTIMATE", fingerprint="")
    with pytest.raises(LegalEvidenceCapacityPolicyContractError):
        replace(value, retention_class="FOREVER", fingerprint="")
    with pytest.raises(
        LegalEvidenceCapacityPolicyContractError,
        match="POLICY_IDENTITY_INVALID",
    ):
        replace(value, policy_version="latest", fingerprint="")


def test_strict_hydration_rejects_missing_extra_and_corrupt_fingerprint() -> None:
    payload = valid_set()[0].to_dict()

    missing = dict(payload)
    missing.pop("profile")
    with pytest.raises(
        LegalEvidenceCapacityPolicyContractError,
        match="DESCRIPTOR_SCHEMA_INVALID",
    ):
        LegalEvidenceCapacityPolicy.from_dict(missing)

    extra = dict(payload)
    extra["price"] = 1
    with pytest.raises(
        LegalEvidenceCapacityPolicyContractError,
        match="DESCRIPTOR_SCHEMA_INVALID",
    ):
        LegalEvidenceCapacityPolicy.from_dict(extra)

    corrupt = dict(payload)
    corrupt["fingerprint"] = "f" * 128
    with pytest.raises(
        LegalEvidenceCapacityPolicyContractError,
        match="FINGERPRINT_MISMATCH",
    ):
        LegalEvidenceCapacityPolicy.from_dict(corrupt)


def test_descriptor_is_immutable() -> None:
    value = valid_set()[0]
    with pytest.raises((FrozenInstanceError, AttributeError)):
        value.single_file_max_bytes = 999  # type: ignore[misc]


def test_authority_firewall_excludes_prices_entitlement_iam_storage_and_court() -> None:
    keys = set(valid_set()[0].to_dict())
    forbidden = {
        "price",
        "amount",
        "currency",
        "plan_id",
        "subscription_id",
        "tenant_id",
        "entitlement_id",
        "principal_id",
        "role",
        "permission",
        "bucket",
        "object_key",
        "provider",
        "payment",
        "execution",
        "settlement",
        "court_filing",
    }
    assert forbidden.isdisjoint(keys)


# ARTIFACT: test_legal_evidence_capacity_policy_contract.py
# VERSION: v1.0.0-L10A2Q-P1A-LEGAL-EVIDENCE-CAPACITY-POLICY-CONTRACT-CERT
# AUTHORITY BOUNDARY: direct structural policy-contract evidence only
# TENANT POSTURE: synthetic global policy descriptors only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
