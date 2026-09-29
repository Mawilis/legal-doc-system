"""WILSY OS canonical Legal Evidence commercial-capacity policy.

TITLE: Legal Evidence Capacity Commercial Policy
VERSION: v1.0.0-L10A2Q-P1B-LEGAL-EVIDENCE-CAPACITY-COMMERCIAL-POLICY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Publish the first immutable production Legal Evidence capacity
         profiles for STARTER, GROWTH, INSTITUTIONAL and FOUNDER_ENTERPRISE
         without granting tenant entitlement, IAM or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/legal_evidence_capacity_commercial_policy.py
COLLABORATION / OWNERSHIP: P1A owns structural policy vocabulary and
                            validation. This module owns exact capacity values.
                            PlanRegistry retains base-plan price truth;
                            SubscriptionRegistry derives subscription commercial
                            truth; future P2 resolves tenant subscription
                            evidence to one profile; Legal Operations consumes
                            resulting capacity evidence.
CERTIFICATION / UPDATE DATE: 2026-09-29
CHANGELOG: v1.0.0-L10A2Q-P1B establishes generous production evidence-vault,
           per-file, monthly-ingress, version, OCR, AI-processing, retention
           and ingestion capabilities. Founder Enterprise receives the
           strongest Founder profile without creating or modifying price truth.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Pure immutable policy values; no credentials,
                             tenant records, persistence, network, provider,
                             bucket, filesystem or browser state.
TENANT BOUNDARY: Global catalogue facts only. A profile does not prove that
                 any tenant owns or may consume it.
AUTHORITY BOUNDARY: Exact capacity-policy values only. No plan resolution,
                    subscription mutation, entitlement, IAM, storage execution,
                    legal hold execution, Court lifecycle or Legal lifecycle.
FINANCIAL AUTHORITY BOUNDARY: No prices, charges, payments, execution or
                               settlement. Founder zero-rating remains canonical
                               PlanRegistry / SubscriptionRegistry truth.
FAIL-CLOSED DECLARATION: Unknown profiles, policy drift, structural regression
                         and fingerprint drift reject through the P1A contract.
"""
from __future__ import annotations

from types import MappingProxyType
from typing import Final, Mapping

from tools.eos.saas.billing.legal_evidence_capacity_policy_contract import (
    LegalEvidenceCapacityPolicy,
    LegalEvidenceCapacityPolicyContractError,
    LegalEvidenceCapacityProfile,
    LegalEvidenceRetentionClass,
    validate_profile_progression,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2Q-P1B-LEGAL-EVIDENCE-CAPACITY-COMMERCIAL-POLICY"
)

GIB: Final[int] = 1024**3
TIB: Final[int] = 1024**4


_CANONICAL_POLICIES: Final[
    Mapping[LegalEvidenceCapacityProfile, LegalEvidenceCapacityPolicy]
] = MappingProxyType(
    {
        LegalEvidenceCapacityProfile.STARTER:
            LegalEvidenceCapacityPolicy(
                profile=LegalEvidenceCapacityProfile.STARTER,
                single_file_max_bytes=2 * GIB,
                tenant_storage_limit_bytes=250 * GIB,
                monthly_ingress_limit_bytes=100 * GIB,
                max_document_versions=25,
                ocr_page_allowance=2_000,
                ai_document_processing_allowance=500,
                retention_class=LegalEvidenceRetentionClass.STANDARD,
                legal_hold_available=False,
                bulk_ingest_available=False,
                api_ingest_available=False,
                external_client_upload_available=True,
            ),
        LegalEvidenceCapacityProfile.GROWTH:
            LegalEvidenceCapacityPolicy(
                profile=LegalEvidenceCapacityProfile.GROWTH,
                single_file_max_bytes=15 * GIB,
                tenant_storage_limit_bytes=1 * TIB,
                monthly_ingress_limit_bytes=500 * GIB,
                max_document_versions=100,
                ocr_page_allowance=10_000,
                ai_document_processing_allowance=2_500,
                retention_class=LegalEvidenceRetentionClass.ENHANCED,
                legal_hold_available=False,
                bulk_ingest_available=True,
                api_ingest_available=True,
                external_client_upload_available=True,
            ),
        LegalEvidenceCapacityProfile.INSTITUTIONAL:
            LegalEvidenceCapacityPolicy(
                profile=LegalEvidenceCapacityProfile.INSTITUTIONAL,
                single_file_max_bytes=50 * GIB,
                tenant_storage_limit_bytes=5 * TIB,
                monthly_ingress_limit_bytes=2 * TIB,
                max_document_versions=250,
                ocr_page_allowance=50_000,
                ai_document_processing_allowance=15_000,
                retention_class=LegalEvidenceRetentionClass.GOVERNED,
                legal_hold_available=True,
                bulk_ingest_available=True,
                api_ingest_available=True,
                external_client_upload_available=True,
            ),
        LegalEvidenceCapacityProfile.FOUNDER_ENTERPRISE:
            LegalEvidenceCapacityPolicy(
                profile=LegalEvidenceCapacityProfile.FOUNDER_ENTERPRISE,
                single_file_max_bytes=150 * GIB,
                tenant_storage_limit_bytes=5 * TIB,
                monthly_ingress_limit_bytes=5 * TIB,
                max_document_versions=500,
                ocr_page_allowance=100_000,
                ai_document_processing_allowance=30_000,
                retention_class=LegalEvidenceRetentionClass.GOVERNED,
                legal_hold_available=True,
                bulk_ingest_available=True,
                api_ingest_available=True,
                external_client_upload_available=True,
            ),
    }
)

POLICIES: Final[
    Mapping[LegalEvidenceCapacityProfile, LegalEvidenceCapacityPolicy]
] = _CANONICAL_POLICIES

# Validate the complete policy set at import time so a regressive edit cannot
# silently become canonical runtime policy.
validate_profile_progression(tuple(_CANONICAL_POLICIES.values()))


def get_legal_evidence_capacity_policy(
    profile: LegalEvidenceCapacityProfile | str,
) -> LegalEvidenceCapacityPolicy:
    """Return the exact immutable capacity policy for one known profile.

    This lookup does not resolve plans, subscriptions, tenants or principals.
    """
    try:
        normalized = LegalEvidenceCapacityProfile(profile)
        return _CANONICAL_POLICIES[normalized]
    except (TypeError, ValueError, KeyError) as error:
        raise LegalEvidenceCapacityPolicyContractError(
            "L10A2Q_P1B_UNKNOWN_PROFILE"
        ) from error


__all__ = [
    "GIB",
    "POLICIES",
    "TIB",
    "VERSION",
    "get_legal_evidence_capacity_policy",
]

# ARTIFACT: legal_evidence_capacity_commercial_policy.py
# VERSION: v1.0.0-L10A2Q-P1B-LEGAL-EVIDENCE-CAPACITY-COMMERCIAL-POLICY
# AUTHORITY BOUNDARY: exact Legal Evidence capacity values only; no entitlement, IAM, storage execution or finance
# TENANT POSTURE: global catalogue facts only; tenant ownership requires canonical upstream evidence
# FAIL-CLOSED POSTURE: unknown profile and structural policy regression reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; Founder base-plan zero-rating remains PlanRegistry truth
# END OF WILSY OS SOVEREIGN ARTIFACT
