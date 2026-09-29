"""WILSY OS Legal Evidence commercial-capacity policy contract.

TITLE: Legal Evidence Capacity Commercial Policy Contract
VERSION: v1.0.0-L10A2Q-P1A-LEGAL-EVIDENCE-CAPACITY-POLICY-CONTRACT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Own the immutable vocabulary, dimensions and integrity contract used
         by future certified Legal Evidence commercial-capacity policies,
         without inventing numeric limits or granting tenant entitlement.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/legal_evidence_capacity_policy_contract.py
COLLABORATION / OWNERSHIP: L10A2Q owns the architecture map; PlanRegistry owns
                            base commercial-plan truth; SubscriptionRegistry
                            owns subscription lifecycle; tenant product
                            entitlement owns tenant/product lifecycle; future
                            P1B owns certified capacity values; future P2 owns
                            profile resolution; Legal Operations consumes
                            capacity evidence only.
CERTIFICATION / UPDATE DATE: 2026-09-29
CHANGELOG: v1.0.0-L10A2Q-P1A establishes the closed STARTER, GROWTH,
           INSTITUTIONAL and FOUNDER_ENTERPRISE capacity-profile vocabulary,
           exact capacity dimensions, retention vocabulary, strict immutable
           descriptors, deterministic SHA3-512 fingerprints and monotonic
           cross-profile validation without assigning commercial numbers.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Pure immutable in-process policy-contract data;
                             no credentials, tenant records, filesystem,
                             MongoDB, network, provider or browser state.
TENANT BOUNDARY: Profile descriptors are global commercial-policy facts only;
                 they do not prove tenant ownership, activation or access.
AUTHORITY BOUNDARY: Capacity vocabulary, structural validation and integrity
                    evidence only. No plan resolution, entitlement, IAM,
                    storage-provider execution, retention execution, pricing,
                    payment, Court or Legal lifecycle authority.
FINANCIAL AUTHORITY BOUNDARY: No invoice, charge, payment, execution or
                               settlement truth. Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Unknown profiles, malformed capacities, unsupported
                         retention classes, non-monotonic profile progression,
                         schema drift and fingerprint drift reject.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import json
from typing import Any, Final, cast


VERSION: Final[str] = (
    "v1.0.0-L10A2Q-P1A-LEGAL-EVIDENCE-CAPACITY-POLICY-CONTRACT"
)
SCHEMA: Final[str] = "WILSY-LEGAL-EVIDENCE-CAPACITY-POLICY-CONTRACT/V1"
POLICY_IDENTITY: Final[str] = "WILSY_LEGAL_EVIDENCE_CAPACITY_POLICY"

_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "policy_version",
    "policy_identity",
    "profile",
    "single_file_max_bytes",
    "tenant_storage_limit_bytes",
    "monthly_ingress_limit_bytes",
    "max_document_versions",
    "ocr_page_allowance",
    "ai_document_processing_allowance",
    "retention_class",
    "legal_hold_available",
    "bulk_ingest_available",
    "api_ingest_available",
    "external_client_upload_available",
    "fingerprint",
)


class LegalEvidenceCapacityPolicyContractError(ValueError):
    """Stable fail-closed error for Legal Evidence capacity-policy contracts."""


class LegalEvidenceCapacityProfile(str, Enum):
    """Closed commercial-capacity profile identities."""

    STARTER = "STARTER"
    GROWTH = "GROWTH"
    INSTITUTIONAL = "INSTITUTIONAL"
    FOUNDER_ENTERPRISE = "FOUNDER_ENTERPRISE"


PROFILE_ORDER: Final[tuple[LegalEvidenceCapacityProfile, ...]] = (
    LegalEvidenceCapacityProfile.STARTER,
    LegalEvidenceCapacityProfile.GROWTH,
    LegalEvidenceCapacityProfile.INSTITUTIONAL,
    LegalEvidenceCapacityProfile.FOUNDER_ENTERPRISE,
)


class LegalEvidenceRetentionClass(str, Enum):
    """Closed retention-capability vocabulary, not retention execution."""

    STANDARD = "STANDARD"
    ENHANCED = "ENHANCED"
    GOVERNED = "GOVERNED"


_RETENTION_RANK: Final[Mapping[LegalEvidenceRetentionClass, int]] = {
    LegalEvidenceRetentionClass.STANDARD: 0,
    LegalEvidenceRetentionClass.ENHANCED: 1,
    LegalEvidenceRetentionClass.GOVERNED: 2,
}


NUMERIC_CAPACITY_FIELDS: Final[tuple[str, ...]] = (
    "single_file_max_bytes",
    "tenant_storage_limit_bytes",
    "monthly_ingress_limit_bytes",
    "max_document_versions",
    "ocr_page_allowance",
    "ai_document_processing_allowance",
)

FEATURE_CAPABILITY_FIELDS: Final[tuple[str, ...]] = (
    "legal_hold_available",
    "bulk_ingest_available",
    "api_ingest_available",
    "external_client_upload_available",
)


def _positive_integer(name: str, value: object) -> int:
    """Require one strictly positive integer commercial capacity."""
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise LegalEvidenceCapacityPolicyContractError(
            f"L10A2Q_P1A_{name.upper()}_INVALID"
        )
    return value


def _boolean(name: str, value: object) -> bool:
    """Require an exact boolean feature capability."""
    if type(value) is not bool:
        raise LegalEvidenceCapacityPolicyContractError(
            f"L10A2Q_P1A_{name.upper()}_INVALID"
        )
    return value


def _canonical_payload(
    *,
    profile: LegalEvidenceCapacityProfile,
    single_file_max_bytes: int,
    tenant_storage_limit_bytes: int,
    monthly_ingress_limit_bytes: int,
    max_document_versions: int,
    ocr_page_allowance: int,
    ai_document_processing_allowance: int,
    retention_class: LegalEvidenceRetentionClass,
    legal_hold_available: bool,
    bulk_ingest_available: bool,
    api_ingest_available: bool,
    external_client_upload_available: bool,
) -> dict[str, object]:
    """Return deterministic policy material excluding the derived fingerprint."""
    return {
        "schema": SCHEMA,
        "policy_version": VERSION,
        "policy_identity": POLICY_IDENTITY,
        "profile": profile.value,
        "single_file_max_bytes": single_file_max_bytes,
        "tenant_storage_limit_bytes": tenant_storage_limit_bytes,
        "monthly_ingress_limit_bytes": monthly_ingress_limit_bytes,
        "max_document_versions": max_document_versions,
        "ocr_page_allowance": ocr_page_allowance,
        "ai_document_processing_allowance": ai_document_processing_allowance,
        "retention_class": retention_class.value,
        "legal_hold_available": legal_hold_available,
        "bulk_ingest_available": bulk_ingest_available,
        "api_ingest_available": api_ingest_available,
        "external_client_upload_available": external_client_upload_available,
    }


def _digest(payload: Mapping[str, object]) -> str:
    """Return lowercase SHA3-512 over deterministic UTF-8 JSON."""
    return hashlib.sha3_512(
        json.dumps(
            dict(payload),
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalEvidenceCapacityPolicy:
    """One immutable sized commercial-capacity descriptor.

    This value is intentionally incapable of resolving itself from a plan,
    granting entitlement, authorizing a principal, executing retention, or
    selecting a storage provider.
    """

    profile: LegalEvidenceCapacityProfile | str
    single_file_max_bytes: int
    tenant_storage_limit_bytes: int
    monthly_ingress_limit_bytes: int
    max_document_versions: int
    ocr_page_allowance: int
    ai_document_processing_allowance: int
    retention_class: LegalEvidenceRetentionClass | str
    legal_hold_available: bool
    bulk_ingest_available: bool
    api_ingest_available: bool
    external_client_upload_available: bool
    schema: str = SCHEMA
    policy_version: str = VERSION
    policy_identity: str = POLICY_IDENTITY
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate exact contract shape and derive immutable integrity evidence."""
        try:
            profile = LegalEvidenceCapacityProfile(self.profile)
            retention = LegalEvidenceRetentionClass(self.retention_class)
        except (TypeError, ValueError) as error:
            raise LegalEvidenceCapacityPolicyContractError(
                "L10A2Q_P1A_ENUM_INVALID"
            ) from error

        if (
            self.schema != SCHEMA
            or self.policy_version != VERSION
            or self.policy_identity != POLICY_IDENTITY
        ):
            raise LegalEvidenceCapacityPolicyContractError(
                "L10A2Q_P1A_POLICY_IDENTITY_INVALID"
            )

        normalized_numeric = {
            name: _positive_integer(name, getattr(self, name))
            for name in NUMERIC_CAPACITY_FIELDS
        }
        normalized_features = {
            name: _boolean(name, getattr(self, name))
            for name in FEATURE_CAPABILITY_FIELDS
        }

        if (
            normalized_numeric["single_file_max_bytes"]
            > normalized_numeric["tenant_storage_limit_bytes"]
        ):
            raise LegalEvidenceCapacityPolicyContractError(
                "L10A2Q_P1A_FILE_EXCEEDS_STORAGE_LIMIT"
            )

        payload = _canonical_payload(
            profile=profile,
            retention_class=retention,
            **normalized_numeric,
            **normalized_features,
        )
        digest = _digest(payload)

        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            raise LegalEvidenceCapacityPolicyContractError(
                "L10A2Q_P1A_FINGERPRINT_MISMATCH"
            )

        object.__setattr__(self, "profile", profile)
        object.__setattr__(self, "retention_class", retention)
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Return one strict detached JSON-compatible policy descriptor."""
        payload = _canonical_payload(
            profile=cast(LegalEvidenceCapacityProfile, self.profile),
            single_file_max_bytes=self.single_file_max_bytes,
            tenant_storage_limit_bytes=self.tenant_storage_limit_bytes,
            monthly_ingress_limit_bytes=self.monthly_ingress_limit_bytes,
            max_document_versions=self.max_document_versions,
            ocr_page_allowance=self.ocr_page_allowance,
            ai_document_processing_allowance=self.ai_document_processing_allowance,
            retention_class=cast(
                LegalEvidenceRetentionClass,
                self.retention_class,
            ),
            legal_hold_available=self.legal_hold_available,
            bulk_ingest_available=self.bulk_ingest_available,
            api_ingest_available=self.api_ingest_available,
            external_client_upload_available=self.external_client_upload_available,
        )
        payload["fingerprint"] = self.fingerprint
        return payload

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalEvidenceCapacityPolicy":
        """Hydrate only an exact complete contract payload."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            raise LegalEvidenceCapacityPolicyContractError(
                "L10A2Q_P1A_DESCRIPTOR_SCHEMA_INVALID"
            )
        return cls(
            profile=cast(str, payload["profile"]),
            single_file_max_bytes=cast(int, payload["single_file_max_bytes"]),
            tenant_storage_limit_bytes=cast(
                int,
                payload["tenant_storage_limit_bytes"],
            ),
            monthly_ingress_limit_bytes=cast(
                int,
                payload["monthly_ingress_limit_bytes"],
            ),
            max_document_versions=cast(int, payload["max_document_versions"]),
            ocr_page_allowance=cast(int, payload["ocr_page_allowance"]),
            ai_document_processing_allowance=cast(
                int,
                payload["ai_document_processing_allowance"],
            ),
            retention_class=cast(str, payload["retention_class"]),
            legal_hold_available=cast(bool, payload["legal_hold_available"]),
            bulk_ingest_available=cast(bool, payload["bulk_ingest_available"]),
            api_ingest_available=cast(bool, payload["api_ingest_available"]),
            external_client_upload_available=cast(
                bool,
                payload["external_client_upload_available"],
            ),
            schema=cast(str, payload["schema"]),
            policy_version=cast(str, payload["policy_version"]),
            policy_identity=cast(str, payload["policy_identity"]),
            fingerprint=cast(str, payload["fingerprint"]),
        )


def validate_profile_progression(
    policies: Sequence[LegalEvidenceCapacityPolicy],
) -> tuple[LegalEvidenceCapacityPolicy, ...]:
    """Validate one complete monotonic four-profile commercial policy set.

    This proves structural differentiation only. It deliberately does not
    decide what the numeric values should be.
    """
    values = tuple(policies)
    if len(values) != len(PROFILE_ORDER):
        raise LegalEvidenceCapacityPolicyContractError(
            "L10A2Q_P1A_PROFILE_SET_INCOMPLETE"
        )

    if tuple(item.profile for item in values) != PROFILE_ORDER:
        raise LegalEvidenceCapacityPolicyContractError(
            "L10A2Q_P1A_PROFILE_ORDER_INVALID"
        )

    for lower, higher in zip(values, values[1:]):
        for field in NUMERIC_CAPACITY_FIELDS:
            if getattr(higher, field) < getattr(lower, field):
                raise LegalEvidenceCapacityPolicyContractError(
                    "L10A2Q_P1A_CAPACITY_REGRESSION"
                )

        lower_retention = cast(
            LegalEvidenceRetentionClass,
            lower.retention_class,
        )
        higher_retention = cast(
            LegalEvidenceRetentionClass,
            higher.retention_class,
        )
        if _RETENTION_RANK[higher_retention] < _RETENTION_RANK[lower_retention]:
            raise LegalEvidenceCapacityPolicyContractError(
                "L10A2Q_P1A_RETENTION_REGRESSION"
            )

        for field in FEATURE_CAPABILITY_FIELDS:
            if getattr(lower, field) and not getattr(higher, field):
                raise LegalEvidenceCapacityPolicyContractError(
                    "L10A2Q_P1A_FEATURE_REGRESSION"
                )

    return values


__all__ = [
    "FEATURE_CAPABILITY_FIELDS",
    "NUMERIC_CAPACITY_FIELDS",
    "POLICY_IDENTITY",
    "PROFILE_ORDER",
    "SCHEMA",
    "VERSION",
    "LegalEvidenceCapacityPolicy",
    "LegalEvidenceCapacityPolicyContractError",
    "LegalEvidenceCapacityProfile",
    "LegalEvidenceRetentionClass",
    "validate_profile_progression",
]

# ARTIFACT: legal_evidence_capacity_policy_contract.py
# VERSION: v1.0.0-L10A2Q-P1A-LEGAL-EVIDENCE-CAPACITY-POLICY-CONTRACT
# AUTHORITY BOUNDARY: capacity vocabulary/validation/integrity only; no plan resolution, entitlement, IAM, storage execution or finance
# TENANT POSTURE: global commercial-policy facts only; no tenant ownership implied
# FAIL-CLOSED POSTURE: malformed, unknown, regressive or fingerprint-drifted policy material rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
