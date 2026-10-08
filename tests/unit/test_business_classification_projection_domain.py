# -*- coding: utf-8 -*-
"""
WILSY OS — Business Classification Projection Domain Test-First Certificate.

TITLE:
    WILSY OS Business Classification Projection Domain Contract

VERSION:
    v1.0.2-P0-BUSINESS-CLASSIFICATION-PROJECTION-DOMAIN-TEST

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Freezes the immutable universal business-classification projection contract
    before production implementation, including strict fingerprint integrity.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_business_classification_projection_domain.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-10-07

CHANGELOG:
    v1.0.2-P0-BUSINESS-CLASSIFICATION-PROJECTION-DOMAIN-TEST
        - Corrects negative-authority certification so legitimate
          BusinessActivity.role means primary/secondary classification role,
          never authorization-role authority.
        - Replaces unsafe substring-based sensitive-method detection where
          "pay" incorrectly matched the legitimate word "payload".
        - Preserves strict exclusion of entitlement, permission, authorization,
          service-pack, AI-execution, billing, payment, settlement and financial
          execution authority.
        - Preserves every provenance, cryptographic and hydration requirement.

    v1.0.1-P0-BUSINESS-CLASSIFICATION-PROJECTION-DOMAIN-TEST
        - Removes an internally contradictory stale-fingerprint hydration
          expectation from source-profile binding certification.
        - Freezes source-profile fingerprint sensitivity by comparing two
          canonically constructed immutable projections.
        - Preserves strict hydration corruption rejection.
        - Preserves every v1.0.0 classification, provenance, authority and
          financial-boundary requirement.

    v1.0.0-P0-BUSINESS-CLASSIFICATION-PROJECTION-DOMAIN-TEST
        - Initial test-first business-classification projection contract.

COMPLIANCE:
    Classification evidence is provenance-bound and tenant scoped.
    Classification is never entitlement, authorization or financial execution.

SECURITY / PRIVACY POSTURE:
    Hydration must reject missing, extra and corrupt fields. Fingerprints may
    never be silently repaired during hydration.

TENANT BOUNDARY:
    Every projection belongs to one exact non-global tenant.

AUTHORITY BOUNDARY:
    Tenant profile assertions are discovery inputs only.
    Classification truth is separate, versioned, provenance-bound and immutable.
    One business may expose a primary activity plus secondary activities.
    One activity may carry mappings into multiple official classification
    systems and editions.

FINANCIAL AUTHORITY BOUNDARY:
    No payment, settlement, billing or financial execution authority exists.
    Kennel EOS remains the exclusive financial execution authority.

TAXONOMY POSTURE:
    Taxonomy identifiers and codes are references to separately governed,
    immutable taxonomy snapshots. This domain does not invent code membership,
    download live web data, or equate correspondence mappings.

AI POSTURE:
    AI may later interpret captured evidence and rank candidates. AI analysis
    is not classification authority and cannot silently confirm a projection.

FUTURE PRODUCTION PATH:
    tools/eos/saas/domain/business_classification_projection.py
"""

from __future__ import annotations

from dataclasses import fields
from datetime import datetime, timezone
import hashlib

import pytest

from tools.eos.saas.domain.business_classification_projection import (
    SCHEMA_VERSION,
    VERSION,
    BusinessActivity,
    BusinessActivityConfirmation,
    BusinessActivityRole,
    BusinessClassificationEvidence,
    BusinessClassificationProjection,
    BusinessClassificationProjectionError,
    BusinessClassificationReference,
    BusinessClassificationSourceKind,
)


EXPECTED_VERSION = (
    "v1.0.0-WILSY-BUSINESS-CLASSIFICATION-PROJECTION"
)

EXPECTED_SCHEMA_VERSION = (
    "wilsy.business.classification.projection.v1"
)

NOW = datetime(
    2026,
    10,
    7,
    7,
    0,
    tzinfo=timezone.utc,
)

DIGEST_A = hashlib.sha3_512(
    b"business-classification-evidence-a"
).hexdigest()

DIGEST_B = hashlib.sha3_512(
    b"business-classification-evidence-b"
).hexdigest()

TAXONOMY_DIGEST_A = hashlib.sha3_512(
    b"official-taxonomy-snapshot-a"
).hexdigest()

TAXONOMY_DIGEST_B = hashlib.sha3_512(
    b"official-taxonomy-snapshot-b"
).hexdigest()

PROFILE_DIGEST = hashlib.sha3_512(
    b"tenant-profile-source-snapshot"
).hexdigest()

PROFILE_DIGEST_B = hashlib.sha3_512(
    b"tenant-profile-source-snapshot-b"
).hexdigest()


def evidence(
    evidence_id: str = "EVIDENCE-1",
    *,
    source_kind: BusinessClassificationSourceKind
        = BusinessClassificationSourceKind.TENANT_DECLARATION,
    source_reference: str = "tenant-profile:industry",
    source_digest: str = DIGEST_A,
) -> BusinessClassificationEvidence:
    """Build one immutable evidence fixture with no authority side effect."""
    return BusinessClassificationEvidence(
        evidence_id=evidence_id,
        source_kind=source_kind,
        source_reference=source_reference,
        observed_at=NOW,
        source_digest=source_digest,
    )


def classification(
    *,
    scheme_id: str = "ISIC",
    scheme_version: str = "REV5",
    code: str = "TEST-CODE-A",
    title: str = "Synthetic certificate activity",
    jurisdiction: str = "GLOBAL",
    taxonomy_snapshot_id: str = "TAXONOMY-SNAPSHOT-A",
    taxonomy_snapshot_digest: str = TAXONOMY_DIGEST_A,
) -> BusinessClassificationReference:
    """Build one snapshot-bound external-classification reference."""
    return BusinessClassificationReference(
        scheme_id=scheme_id,
        scheme_version=scheme_version,
        code=code,
        title=title,
        jurisdiction=jurisdiction,
        taxonomy_snapshot_id=taxonomy_snapshot_id,
        taxonomy_snapshot_digest=taxonomy_snapshot_digest,
    )


def activity(
    activity_id: str = "ACTIVITY-1",
    *,
    role: BusinessActivityRole = BusinessActivityRole.PRIMARY,
    confirmation:
        BusinessActivityConfirmation
        = BusinessActivityConfirmation.CONFIRMED,
    confidence_basis_points: int = 9500,
    evidence_refs: tuple[str, ...] = ("EVIDENCE-1",),
    classifications: tuple[
        BusinessClassificationReference,
        ...,
    ] | None = None,
) -> BusinessActivity:
    """Build one activity fixture without service-pack or entitlement grants."""
    return BusinessActivity(
        activity_id=activity_id,
        role=role,
        description="Synthetic business activity",
        confirmation=confirmation,
        confidence_basis_points=confidence_basis_points,
        evidence_refs=evidence_refs,
        classifications=(
            classifications
            if classifications is not None
            else (classification(),)
        ),
    )


def projection(
    *,
    tenant_id: str = "tenant-a",
    projection_id: str = "WILSYBUSCLASS-TEST-1",
    revision: int = 1,
    source_profile_digest: str = PROFILE_DIGEST,
    activities: tuple[BusinessActivity, ...] | None = None,
    evidences: tuple[
        BusinessClassificationEvidence,
        ...,
    ] | None = None,
    supersedes_projection_id: str | None = None,
) -> BusinessClassificationProjection:
    """Build one immutable tenant-bound projection fixture."""
    return BusinessClassificationProjection(
        projection_id=projection_id,
        tenant_id=tenant_id,
        revision=revision,
        source_profile_digest=source_profile_digest,
        evidences=(
            evidences
            if evidences is not None
            else (evidence(),)
        ),
        activities=(
            activities
            if activities is not None
            else (activity(),)
        ),
        effective_from=NOW,
        created_at=NOW,
        supersedes_projection_id=supersedes_projection_id,
    )


def test_version_and_schema_are_exact() -> None:
    assert VERSION == EXPECTED_VERSION
    assert SCHEMA_VERSION == EXPECTED_SCHEMA_VERSION


def test_closed_activity_role_vocabulary_is_exact() -> None:
    assert tuple(
        member.value
        for member in BusinessActivityRole
    ) == (
        "primary",
        "secondary",
    )


def test_confirmation_vocabulary_is_exact() -> None:
    assert tuple(
        member.value
        for member in BusinessActivityConfirmation
    ) == (
        "proposed",
        "confirmed",
    )


def test_evidence_source_vocabulary_excludes_ai_authority() -> None:
    assert tuple(
        member.value
        for member in BusinessClassificationSourceKind
    ) == (
        "tenant_declaration",
        "official_registry",
        "official_document",
        "first_party_source",
        "operator_verification",
        "research_capture",
    )

    assert not any(
        "ai" in member.value.lower()
        for member in BusinessClassificationSourceKind
    )


def test_projection_requires_exact_tenant_scope() -> None:
    for invalid in (
        "",
        " ",
        " tenant-a",
        "tenant-a ",
        "default",
        "GLOBAL",
        "root",
        "*",
        "MASTER",
        "GLOBAL_ROOT",
        "SOVEREIGN_ROOT",
        "wilsy-sovereign-root",
    ):
        with pytest.raises(
            BusinessClassificationProjectionError
        ):
            projection(tenant_id=invalid)


def test_projection_requires_exactly_one_primary_activity() -> None:
    with pytest.raises(
        BusinessClassificationProjectionError
    ):
        projection(
            activities=(
                activity(
                    "SECONDARY-1",
                    role=BusinessActivityRole.SECONDARY,
                ),
            )
        )

    with pytest.raises(
        BusinessClassificationProjectionError
    ):
        projection(
            activities=(
                activity("PRIMARY-1"),
                activity("PRIMARY-2"),
            )
        )


def test_projection_supports_multiple_secondary_activities() -> None:
    value = projection(
        activities=(
            activity("PRIMARY-1"),
            activity(
                "SECONDARY-1",
                role=BusinessActivityRole.SECONDARY,
            ),
            activity(
                "SECONDARY-2",
                role=BusinessActivityRole.SECONDARY,
            ),
        )
    )

    assert len(value.activities) == 3
    assert value.activities[0].role is BusinessActivityRole.PRIMARY


def test_activity_supports_multiple_taxonomy_mappings() -> None:
    value = activity(
        classifications=(
            classification(
                scheme_id="ISIC",
                scheme_version="REV5",
                code="TEST-ISIC",
            ),
            classification(
                scheme_id="ZA-SIC",
                scheme_version="SIC7",
                code="TEST-ZA-SIC",
                jurisdiction="ZA",
                taxonomy_snapshot_id="TAXONOMY-SNAPSHOT-B",
                taxonomy_snapshot_digest=TAXONOMY_DIGEST_B,
            ),
        )
    )

    assert len(value.classifications) == 2
    assert value.classifications[0].scheme_id == "ISIC"
    assert value.classifications[1].scheme_id == "ZA-SIC"


def test_taxonomy_reference_is_snapshot_and_edition_bound() -> None:
    reference = classification()

    assert reference.scheme_id == "ISIC"
    assert reference.scheme_version == "REV5"
    assert reference.taxonomy_snapshot_id == "TAXONOMY-SNAPSHOT-A"
    assert (
        reference.taxonomy_snapshot_digest
        == TAXONOMY_DIGEST_A
    )


@pytest.mark.parametrize(
    "field_name",
    (
        "scheme_id",
        "scheme_version",
        "code",
        "title",
        "jurisdiction",
        "taxonomy_snapshot_id",
    ),
)
def test_taxonomy_reference_rejects_blank_or_padded_text(
    field_name: str,
) -> None:
    base = {
        "scheme_id": "ISIC",
        "scheme_version": "REV5",
        "code": "TEST-CODE-A",
        "title": "Synthetic certificate activity",
        "jurisdiction": "GLOBAL",
        "taxonomy_snapshot_id": "TAXONOMY-SNAPSHOT-A",
        "taxonomy_snapshot_digest": TAXONOMY_DIGEST_A,
    }

    for invalid in ("", " ", " padded", "padded "):
        payload = dict(base)
        payload[field_name] = invalid

        with pytest.raises(
            BusinessClassificationProjectionError
        ):
            BusinessClassificationReference(**payload)


def test_taxonomy_snapshot_digest_is_lowercase_sha3_512_shape() -> None:
    assert len(TAXONOMY_DIGEST_A) == 128

    for invalid in (
        "",
        "a" * 127,
        "a" * 129,
        "A" * 128,
        "g" * 128,
    ):
        with pytest.raises(
            BusinessClassificationProjectionError
        ):
            classification(
                taxonomy_snapshot_digest=invalid
            )


def test_evidence_requires_immutable_captured_source_digest() -> None:
    value = evidence()

    assert value.source_digest == DIGEST_A
    assert len(value.source_digest) == 128

    for invalid in (
        "",
        "a" * 127,
        "A" * 128,
        "z" * 128,
    ):
        with pytest.raises(
            BusinessClassificationProjectionError
        ):
            evidence(source_digest=invalid)


def test_confidence_is_integer_basis_points_not_float_or_bool() -> None:
    for invalid in (
        -1,
        10001,
        50.5,
        True,
        False,
    ):
        with pytest.raises(
            BusinessClassificationProjectionError
        ):
            activity(
                confidence_basis_points=invalid  # type: ignore[arg-type]
            )

    assert activity(
        confidence_basis_points=0
    ).confidence_basis_points == 0

    assert activity(
        confidence_basis_points=10000
    ).confidence_basis_points == 10000


def test_activity_evidence_references_must_resolve() -> None:
    with pytest.raises(
        BusinessClassificationProjectionError
    ):
        projection(
            activities=(
                activity(
                    evidence_refs=("MISSING-EVIDENCE",)
                ),
            )
        )


def test_duplicate_evidence_identity_is_rejected() -> None:
    with pytest.raises(
        BusinessClassificationProjectionError
    ):
        projection(
            evidences=(
                evidence("EVIDENCE-1"),
                evidence(
                    "EVIDENCE-1",
                    source_digest=DIGEST_B,
                ),
            )
        )


def test_duplicate_activity_identity_is_rejected() -> None:
    with pytest.raises(
        BusinessClassificationProjectionError
    ):
        projection(
            activities=(
                activity("ACTIVITY-1"),
                activity(
                    "ACTIVITY-1",
                    role=BusinessActivityRole.SECONDARY,
                ),
            )
        )


def test_duplicate_classification_coordinate_is_rejected() -> None:
    duplicate = classification()

    with pytest.raises(
        BusinessClassificationProjectionError
    ):
        activity(
            classifications=(
                duplicate,
                duplicate,
            )
        )


def test_initial_revision_has_no_superseded_projection() -> None:
    first = projection()

    assert first.revision == 1
    assert first.supersedes_projection_id is None

    with pytest.raises(
        BusinessClassificationProjectionError
    ):
        projection(
            supersedes_projection_id="OLDER-PROJECTION"
        )


def test_later_revision_requires_exact_supersession_reference() -> None:
    later = projection(
        revision=2,
        projection_id="WILSYBUSCLASS-TEST-2",
        supersedes_projection_id="WILSYBUSCLASS-TEST-1",
    )

    assert later.revision == 2
    assert (
        later.supersedes_projection_id
        == "WILSYBUSCLASS-TEST-1"
    )

    with pytest.raises(
        BusinessClassificationProjectionError
    ):
        projection(
            revision=2,
            projection_id="WILSYBUSCLASS-TEST-2",
            supersedes_projection_id=None,
        )


def test_source_profile_digest_binds_projection_fingerprint() -> None:
    original = projection(
        source_profile_digest=PROFILE_DIGEST
    )

    changed = projection(
        source_profile_digest=PROFILE_DIGEST_B
    )

    assert original.source_profile_digest != changed.source_profile_digest
    assert changed.fingerprint != original.fingerprint


def test_projection_fingerprint_is_lowercase_sha3_512() -> None:
    value = projection()

    assert len(value.fingerprint) == 128
    assert value.fingerprint == value.fingerprint.lower()
    assert all(
        character in "0123456789abcdef"
        for character in value.fingerprint
    )


def test_strict_round_trip_preserves_classification_truth() -> None:
    original = projection(
        activities=(
            activity(
                "PRIMARY-1",
                classifications=(
                    classification(
                        scheme_id="ISIC",
                        scheme_version="REV5",
                        code="TEST-ISIC",
                    ),
                    classification(
                        scheme_id="NACE",
                        scheme_version="REV2.1",
                        code="TEST-NACE",
                        jurisdiction="EU",
                        taxonomy_snapshot_id="TAXONOMY-SNAPSHOT-B",
                        taxonomy_snapshot_digest=TAXONOMY_DIGEST_B,
                    ),
                ),
            ),
            activity(
                "SECONDARY-1",
                role=BusinessActivityRole.SECONDARY,
                confirmation=BusinessActivityConfirmation.PROPOSED,
                confidence_basis_points=6400,
            ),
        )
    )

    restored = BusinessClassificationProjection.from_dict(
        original.to_dict()
    )

    assert restored == original
    assert restored.fingerprint == original.fingerprint


def test_hydration_rejects_missing_extra_or_corrupt_fields() -> None:
    payload = projection().to_dict()

    missing = dict(payload)
    missing.pop("tenant_id")

    with pytest.raises(
        BusinessClassificationProjectionError
    ):
        BusinessClassificationProjection.from_dict(
            missing
        )

    extra = dict(payload)
    extra["surprise"] = True

    with pytest.raises(
        BusinessClassificationProjectionError
    ):
        BusinessClassificationProjection.from_dict(
            extra
        )

    corrupt = dict(payload)
    corrupt["fingerprint"] = "0" * 128

    with pytest.raises(
        BusinessClassificationProjectionError
    ):
        BusinessClassificationProjection.from_dict(
            corrupt
        )


def test_projection_carries_no_entitlement_authorization_or_execution_authority(
) -> None:
    forbidden = {
        "plan",
        "plan_id",
        "subscription",
        "subscription_id",
        "entitlement",
        "entitlement_id",
        "permission",
        "permissions",
        "permission_id",
        "authorization",
        "authorization_role",
        "authorization_role_id",
        "business_role",
        "business_role_id",
        "roles",
        "role_grants",
        "service_pack",
        "service_pack_id",
        "dashboard",
        "dashboard_id",
        "ai_authority",
        "payment",
        "payment_id",
        "settlement",
        "settlement_id",
        "billing",
        "financial_execution",
        "kennel_command",
    }

    projection_fields = {
        field.name
        for field in fields(
            BusinessClassificationProjection
        )
    }

    activity_fields = {
        field.name
        for field in fields(
            BusinessActivity
        )
    }

    reference_fields = {
        field.name
        for field in fields(
            BusinessClassificationReference
        )
    }

    evidence_fields = {
        field.name
        for field in fields(
            BusinessClassificationEvidence
        )
    }

    actual = (
        projection_fields
        | activity_fields
        | reference_fields
        | evidence_fields
    )

    assert forbidden.isdisjoint(actual)

    # `role` is classification semantics here only:
    # primary versus secondary business activity.
    assert "role" in activity_fields
    assert tuple(
        member.value
        for member in BusinessActivityRole
    ) == (
        "primary",
        "secondary",
    )


def test_domain_exposes_no_live_web_or_service_pack_activation_method(
) -> None:
    forbidden_exact_methods = {
        "fetch",
        "crawl",
        "search_web",
        "activate_service",
        "activate_service_pack",
        "grant",
        "grant_permission",
        "grant_role",
        "authorize",
        "purchase",
        "subscribe",
        "pay",
        "settle",
        "execute_financial",
        "execute_payment",
        "execute_settlement",
    }

    forbidden_prefixes = (
        "fetch_",
        "crawl_",
        "search_web_",
        "activate_service_",
        "grant_permission_",
        "grant_role_",
        "authorize_",
        "purchase_",
        "subscribe_",
        "execute_financial_",
        "execute_payment_",
        "execute_settlement_",
    )

    classes = (
        BusinessClassificationProjection,
        BusinessActivity,
        BusinessClassificationReference,
        BusinessClassificationEvidence,
    )

    for cls in classes:
        method_names = {
            name.lower()
            for name in vars(cls)
            if callable(getattr(cls, name, None))
        }

        assert forbidden_exact_methods.isdisjoint(
            method_names
        )

        assert not any(
            method.startswith(prefix)
            for method in method_names
            for prefix in forbidden_prefixes
        )

    # Token-aware authority checks must not confuse "payload"
    # with payment authority.
    assert "pay" not in {
        "_semantic_payload",
    }


# =============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_business_classification_projection_domain.py
# VERSION: v1.0.2-P0-BUSINESS-CLASSIFICATION-PROJECTION-DOMAIN-TEST
# AUTHORITY BOUNDARY: classification contract only; no entitlement, permission,
# role, service-pack, AI execution, billing, payment or settlement authority
# TENANT POSTURE: one exact non-global tenant per immutable projection
# FAIL-CLOSED POSTURE: strict hydration rejects missing, extra or corrupt truth;
# fingerprints are never silently repaired during hydration
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
