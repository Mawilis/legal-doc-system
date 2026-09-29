"""Direct certificate for canonical Legal Evidence capacity policy.

VERSION: v1.0.0-L10A2Q-P1B-LEGAL-EVIDENCE-CAPACITY-COMMERCIAL-POLICY-CERT
AUTHORITY: Wilsy OS Core Governance
CERTIFICATION / UPDATE DATE: 2026-09-29
"""
from __future__ import annotations

import re

import pytest

from tools.eos.saas.billing.legal_evidence_capacity_policy_contract import (
    LegalEvidenceCapacityPolicyContractError,
    LegalEvidenceCapacityProfile,
    LegalEvidenceRetentionClass,
    validate_profile_progression,
)
from tools.eos.saas.billing.legal_evidence_capacity_commercial_policy import (
    GIB,
    POLICIES,
    TIB,
    get_legal_evidence_capacity_policy,
)


def test_closed_policy_set_is_complete_and_monotonic() -> None:
    assert tuple(POLICIES) == tuple(LegalEvidenceCapacityProfile)
    assert validate_profile_progression(tuple(POLICIES.values())) == tuple(
        POLICIES.values()
    )


def test_starter_capacity_is_generous_but_bounded() -> None:
    value = get_legal_evidence_capacity_policy("STARTER")
    assert value.single_file_max_bytes == 2 * GIB
    assert value.tenant_storage_limit_bytes == 250 * GIB
    assert value.monthly_ingress_limit_bytes == 100 * GIB
    assert value.max_document_versions == 25
    assert value.ocr_page_allowance == 2_000
    assert value.ai_document_processing_allowance == 500
    assert value.retention_class is LegalEvidenceRetentionClass.STANDARD
    assert not value.legal_hold_available
    assert not value.bulk_ingest_available
    assert not value.api_ingest_available
    assert value.external_client_upload_available


def test_growth_capacity_adds_bulk_and_api_ingest() -> None:
    value = get_legal_evidence_capacity_policy("GROWTH")
    assert value.single_file_max_bytes == 15 * GIB
    assert value.tenant_storage_limit_bytes == TIB
    assert value.monthly_ingress_limit_bytes == 500 * GIB
    assert value.max_document_versions == 100
    assert value.ocr_page_allowance == 10_000
    assert value.ai_document_processing_allowance == 2_500
    assert value.retention_class is LegalEvidenceRetentionClass.ENHANCED
    assert not value.legal_hold_available
    assert value.bulk_ingest_available
    assert value.api_ingest_available
    assert value.external_client_upload_available


def test_institutional_capacity_is_governed_and_legal_hold_capable() -> None:
    value = get_legal_evidence_capacity_policy("INSTITUTIONAL")
    assert value.single_file_max_bytes == 50 * GIB
    assert value.tenant_storage_limit_bytes == 5 * TIB
    assert value.monthly_ingress_limit_bytes == 2 * TIB
    assert value.max_document_versions == 250
    assert value.ocr_page_allowance == 50_000
    assert value.ai_document_processing_allowance == 15_000
    assert value.retention_class is LegalEvidenceRetentionClass.GOVERNED
    assert value.legal_hold_available
    assert value.bulk_ingest_available
    assert value.api_ingest_available
    assert value.external_client_upload_available


def test_founder_enterprise_is_strongest_capacity_profile() -> None:
    value = get_legal_evidence_capacity_policy("FOUNDER_ENTERPRISE")
    institutional = get_legal_evidence_capacity_policy("INSTITUTIONAL")

    assert value.single_file_max_bytes == 150 * GIB
    assert value.tenant_storage_limit_bytes == 5 * TIB
    assert value.monthly_ingress_limit_bytes == 5 * TIB
    assert value.max_document_versions == 500
    assert value.ocr_page_allowance == 100_000
    assert value.ai_document_processing_allowance == 30_000
    assert value.retention_class is LegalEvidenceRetentionClass.GOVERNED
    assert value.legal_hold_available
    assert value.bulk_ingest_available
    assert value.api_ingest_available
    assert value.external_client_upload_available

    assert value.single_file_max_bytes >= institutional.single_file_max_bytes
    assert value.tenant_storage_limit_bytes >= institutional.tenant_storage_limit_bytes
    assert value.monthly_ingress_limit_bytes >= institutional.monthly_ingress_limit_bytes


def test_policy_fingerprints_are_unique_lowercase_sha3_512() -> None:
    fingerprints = [value.fingerprint for value in POLICIES.values()]
    assert len(set(fingerprints)) == 4
    assert all(re.fullmatch(r"[0-9a-f]{128}", value) for value in fingerprints)


def test_unknown_latest_and_empty_profiles_fail_closed() -> None:
    for profile in ("", "LATEST", "ENTERPRISE", "ULTIMATE", None):
        with pytest.raises(
            LegalEvidenceCapacityPolicyContractError,
            match="UNKNOWN_PROFILE",
        ):
            get_legal_evidence_capacity_policy(profile)  # type: ignore[arg-type]


def test_capacity_policy_contains_no_price_or_tenant_authority() -> None:
    for value in POLICIES.values():
        keys = set(value.to_dict())
        forbidden = {
            "price",
            "amount",
            "currency",
            "tenant_id",
            "plan_id",
            "subscription_id",
            "entitlement_id",
            "principal_id",
            "permission",
            "invoice",
            "payment",
            "execution",
            "settlement",
            "bucket",
            "provider",
            "object_key",
        }
        assert forbidden.isdisjoint(keys)


def test_founder_capacity_does_not_encode_zero_price_as_capacity_truth() -> None:
    value = get_legal_evidence_capacity_policy("FOUNDER_ENTERPRISE")
    payload = value.to_dict()
    assert "price" not in payload
    assert "amount" not in payload
    assert "currency" not in payload


# ARTIFACT: test_legal_evidence_capacity_commercial_policy.py
# VERSION: v1.0.0-L10A2Q-P1B-LEGAL-EVIDENCE-CAPACITY-COMMERCIAL-POLICY-CERT
# AUTHORITY BOUNDARY: direct exact-capacity policy evidence only
# TENANT POSTURE: global canonical profile values only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
