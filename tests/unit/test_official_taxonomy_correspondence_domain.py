# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN TEST-FIRST CERTIFICATION ARTIFACT
OFFICIAL TAXONOMY CORRESPONDENCE DOMAIN
===============================================================================

TITLE:
    WILSY OS Official Taxonomy Correspondence Test-First Contract

VERSION:
    v1.0.0-OFFICIAL-TAXONOMY-CORRESPONDENCE-DOMAIN-TEST

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Freezes immutable set-to-set official classification correspondence truth
    between two already-certified taxonomy hierarchies without reducing splits,
    merges or many-to-many changes to misleading pairwise equivalence.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_official_taxonomy_correspondence_domain.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-10-08

CHANGELOG:
    v1.0.0-OFFICIAL-TAXONOMY-CORRESPONDENCE-DOMAIN-TEST
        - Initial set-to-set correspondence authority contract.
        - Binds exact source and target snapshot/hierarchy coordinates.
        - Uses certified hierarchy objects as category-resolution authority.
        - Supports one-to-one, one-to-many, many-to-one and many-to-many.
        - Derives cardinality from relation set sizes.
        - Forbids caller-asserted cardinality.
        - Preserves publisher change type and publisher description separately
          from structural cardinality.
        - Does not infer semantic equivalence from one-to-one structure.
        - Canonicalizes relation, category-set and source-reference ordering.
        - Rejects unresolved source/target category identities.
        - Excludes tenant classification, regulatory, service activation,
          entitlement, authorization, AI, network and financial authority.

TENANT BOUNDARY:
    Platform reference truth only. No tenant or principal identity exists here.

AUTHORITY BOUNDARY:
    Official correspondence relationships only. Source and target taxonomy
    hierarchy truth remains owned by OfficialTaxonomyHierarchy.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.

FUTURE PRODUCTION PATH:
    tools/eos/saas/domain/official_taxonomy_correspondence.py
===============================================================================
"""

from __future__ import annotations

from dataclasses import fields
import hashlib

import pytest

from tools.eos.saas.domain.official_taxonomy_correspondence import (
    SCHEMA_VERSION,
    VERSION,
    OfficialTaxonomyCorrespondence,
    OfficialTaxonomyCorrespondenceCardinality,
    OfficialTaxonomyCorrespondenceError,
    OfficialTaxonomyCorrespondenceRelation,
)

from tools.eos.saas.domain.official_taxonomy_hierarchy import (
    OfficialTaxonomyCategory,
    OfficialTaxonomyCategoryText,
    OfficialTaxonomyHierarchy,
    OfficialTaxonomyHierarchyLevel,
)


EXPECTED_VERSION = (
    "v1.0.0-WILSY-OFFICIAL-TAXONOMY-CORRESPONDENCE"
)

EXPECTED_SCHEMA_VERSION = (
    "wilsy.official.taxonomy.correspondence.v1"
)

SOURCE_SNAPSHOT_DIGEST = hashlib.sha3_512(
    b"source-snapshot"
).hexdigest()

TARGET_SNAPSHOT_DIGEST = hashlib.sha3_512(
    b"target-snapshot"
).hexdigest()


def category_text(
    title: str,
) -> OfficialTaxonomyCategoryText:
    """Build one category text fixture."""
    return OfficialTaxonomyCategoryText(
        language_tag="en",
        title=title,
        definition=None,
        explanatory_notes=(),
        inclusions=(),
        exclusions=(),
        source_artifact_refs=("STRUCTURE",),
    )


def category(
    category_id: str,
    level_id: str,
    code: str,
    parent_category_id: str | None,
    terminal: bool,
) -> OfficialTaxonomyCategory:
    """Build one category fixture."""
    return OfficialTaxonomyCategory(
        category_id=category_id,
        level_id=level_id,
        code=code,
        parent_category_id=parent_category_id,
        terminal=terminal,
        source_artifact_refs=("STRUCTURE",),
        texts=(
            category_text(
                category_id,
            ),
        ),
    )


def hierarchy(
    *,
    hierarchy_id: str,
    snapshot_id: str,
    snapshot_digest: str,
    scheme_id: str,
    scheme_version: str,
    jurisdiction: str = "GLOBAL",
    root_code: str = "A",
    child_codes: tuple[str, ...] = (
        "01",
        "02",
    ),
) -> OfficialTaxonomyHierarchy:
    """Build one two-level certified hierarchy fixture."""
    root_id = (
        hierarchy_id
        + "-ROOT"
    )

    children = tuple(
        category(
            hierarchy_id
            + "-C"
            + str(index),
            "CHILD",
            code,
            root_id,
            True,
        )
        for index, code in enumerate(
            child_codes,
            start=1,
        )
    )

    return OfficialTaxonomyHierarchy(
        hierarchy_id=hierarchy_id,
        snapshot_id=snapshot_id,
        snapshot_digest=snapshot_digest,
        scheme_id=scheme_id,
        scheme_version=scheme_version,
        jurisdiction=jurisdiction,
        source_artifact_refs=(
            "STRUCTURE",
        ),
        levels=(
            OfficialTaxonomyHierarchyLevel(
                level_id="ROOT",
                rank=0,
                title="Root",
                source_artifact_refs=(
                    "STRUCTURE",
                ),
            ),
            OfficialTaxonomyHierarchyLevel(
                level_id="CHILD",
                rank=1,
                title="Child",
                source_artifact_refs=(
                    "STRUCTURE",
                ),
            ),
        ),
        categories=(
            category(
                root_id,
                "ROOT",
                root_code,
                None,
                False,
            ),
            *children,
        ),
    )


def source_hierarchy() -> OfficialTaxonomyHierarchy:
    """Build source hierarchy fixture."""
    return hierarchy(
        hierarchy_id="SOURCE-H",
        snapshot_id="SOURCE-S",
        snapshot_digest=SOURCE_SNAPSHOT_DIGEST,
        scheme_id="ISIC",
        scheme_version="REV4",
    )


def target_hierarchy() -> OfficialTaxonomyHierarchy:
    """Build target hierarchy fixture."""
    return hierarchy(
        hierarchy_id="TARGET-H",
        snapshot_id="TARGET-S",
        snapshot_digest=TARGET_SNAPSHOT_DIGEST,
        scheme_id="ISIC",
        scheme_version="REV5",
        child_codes=(
            "11",
            "12",
            "13",
        ),
    )


def relation(
    relationship_id: str = "R1",
    *,
    source_ids: tuple[str, ...] = (
        "SOURCE-H-C1",
    ),
    target_ids: tuple[str, ...] = (
        "TARGET-H-C1",
    ),
    publisher_change_type: str = "publisher supplied change type",
    publisher_description: str | None = (
        "publisher supplied description"
    ),
    source_refs: tuple[str, ...] = (
        "CORRESPONDENCE",
    ),
) -> OfficialTaxonomyCorrespondenceRelation:
    """Build one set-to-set correspondence relation fixture."""
    return OfficialTaxonomyCorrespondenceRelation(
        relationship_id=relationship_id,
        source_category_ids=source_ids,
        target_category_ids=target_ids,
        publisher_change_type=publisher_change_type,
        publisher_description=publisher_description,
        source_artifact_refs=source_refs,
    )


def correspondence(
    *,
    source: OfficialTaxonomyHierarchy | None = None,
    target: OfficialTaxonomyHierarchy | None = None,
    relations: tuple[
        OfficialTaxonomyCorrespondenceRelation,
        ...,
    ] | None = None,
    source_refs: tuple[str, ...] = (
        "CORRESPONDENCE",
    ),
) -> OfficialTaxonomyCorrespondence:
    """Build one complete correspondence aggregate fixture."""
    return OfficialTaxonomyCorrespondence(
        correspondence_id="CORR-1",
        source_hierarchy=(
            source
            if source is not None
            else source_hierarchy()
        ),
        target_hierarchy=(
            target
            if target is not None
            else target_hierarchy()
        ),
        source_artifact_refs=source_refs,
        relations=(
            relations
            if relations is not None
            else (
                relation(),
            )
        ),
    )


def test_version_and_schema_are_exact() -> None:
    assert VERSION == EXPECTED_VERSION
    assert SCHEMA_VERSION == EXPECTED_SCHEMA_VERSION


def test_cardinality_vocabulary_is_exact() -> None:
    assert tuple(
        item.value
        for item in OfficialTaxonomyCorrespondenceCardinality
    ) == (
        "one_to_one",
        "one_to_many",
        "many_to_one",
        "many_to_many",
    )


def test_correspondence_is_platform_reference_not_tenant_truth() -> None:
    actual = {
        item.name
        for item in fields(
            OfficialTaxonomyCorrespondence
        )
    }

    assert "tenant_id" not in actual
    assert "principal_id" not in actual
    assert "organization_id" not in actual


def test_source_and_target_coordinates_are_derived_from_hierarchies() -> None:
    source = source_hierarchy()
    target = target_hierarchy()

    value = correspondence(
        source=source,
        target=target,
    )

    assert value.source_snapshot_id == source.snapshot_id
    assert value.source_snapshot_digest == source.snapshot_digest
    assert value.source_hierarchy_id == source.hierarchy_id
    assert value.source_hierarchy_digest == source.hierarchy_digest
    assert value.source_scheme_id == source.scheme_id
    assert value.source_scheme_version == source.scheme_version
    assert value.source_jurisdiction == source.jurisdiction

    assert value.target_snapshot_id == target.snapshot_id
    assert value.target_snapshot_digest == target.snapshot_digest
    assert value.target_hierarchy_id == target.hierarchy_id
    assert value.target_hierarchy_digest == target.hierarchy_digest
    assert value.target_scheme_id == target.scheme_id
    assert value.target_scheme_version == target.scheme_version
    assert value.target_jurisdiction == target.jurisdiction


def test_hierarchy_objects_are_not_duplicated_into_serialized_truth() -> None:
    payload = correspondence().to_dict()

    assert "source_hierarchy" not in payload
    assert "target_hierarchy" not in payload
    assert "source_categories" not in payload
    assert "target_categories" not in payload


def test_one_to_one_cardinality_is_derived() -> None:
    value = relation(
        source_ids=("SOURCE-H-C1",),
        target_ids=("TARGET-H-C1",),
    )

    assert (
        value.cardinality
        is OfficialTaxonomyCorrespondenceCardinality.ONE_TO_ONE
    )


def test_one_to_many_cardinality_is_derived() -> None:
    value = relation(
        source_ids=("SOURCE-H-C1",),
        target_ids=(
            "TARGET-H-C1",
            "TARGET-H-C2",
        ),
    )

    assert (
        value.cardinality
        is OfficialTaxonomyCorrespondenceCardinality.ONE_TO_MANY
    )


def test_many_to_one_cardinality_is_derived() -> None:
    value = relation(
        source_ids=(
            "SOURCE-H-C1",
            "SOURCE-H-C2",
        ),
        target_ids=("TARGET-H-C1",),
    )

    assert (
        value.cardinality
        is OfficialTaxonomyCorrespondenceCardinality.MANY_TO_ONE
    )


def test_many_to_many_cardinality_is_derived() -> None:
    value = relation(
        source_ids=(
            "SOURCE-H-C1",
            "SOURCE-H-C2",
        ),
        target_ids=(
            "TARGET-H-C1",
            "TARGET-H-C2",
        ),
    )

    assert (
        value.cardinality
        is OfficialTaxonomyCorrespondenceCardinality.MANY_TO_MANY
    )


def test_cardinality_is_not_caller_asserted_field() -> None:
    actual = {
        item.name
        for item in fields(
            OfficialTaxonomyCorrespondenceRelation
        )
    }

    assert "cardinality" not in actual


def test_source_set_cannot_be_empty() -> None:
    with pytest.raises(
        OfficialTaxonomyCorrespondenceError
    ):
        relation(
            source_ids=(),
        )


def test_target_set_cannot_be_empty() -> None:
    with pytest.raises(
        OfficialTaxonomyCorrespondenceError
    ):
        relation(
            target_ids=(),
        )


def test_source_category_ids_are_unique() -> None:
    with pytest.raises(
        OfficialTaxonomyCorrespondenceError
    ):
        relation(
            source_ids=(
                "SOURCE-H-C1",
                "SOURCE-H-C1",
            ),
        )


def test_target_category_ids_are_unique() -> None:
    with pytest.raises(
        OfficialTaxonomyCorrespondenceError
    ):
        relation(
            target_ids=(
                "TARGET-H-C1",
                "TARGET-H-C1",
            ),
        )


def test_category_set_order_is_canonicalized() -> None:
    one = relation(
        source_ids=(
            "SOURCE-H-C1",
            "SOURCE-H-C2",
        ),
        target_ids=(
            "TARGET-H-C1",
            "TARGET-H-C2",
        ),
    )

    two = relation(
        source_ids=(
            "SOURCE-H-C2",
            "SOURCE-H-C1",
        ),
        target_ids=(
            "TARGET-H-C2",
            "TARGET-H-C1",
        ),
    )

    assert one == two


def test_source_category_refs_must_resolve_in_source_hierarchy() -> None:
    with pytest.raises(
        OfficialTaxonomyCorrespondenceError
    ):
        correspondence(
            relations=(
                relation(
                    source_ids=(
                        "SOURCE-H-MISSING",
                    ),
                ),
            )
        )


def test_target_category_refs_must_resolve_in_target_hierarchy() -> None:
    with pytest.raises(
        OfficialTaxonomyCorrespondenceError
    ):
        correspondence(
            relations=(
                relation(
                    target_ids=(
                        "TARGET-H-MISSING",
                    ),
                ),
            )
        )


def test_source_ref_cannot_resolve_against_target_only() -> None:
    with pytest.raises(
        OfficialTaxonomyCorrespondenceError
    ):
        correspondence(
            relations=(
                relation(
                    source_ids=(
                        "TARGET-H-C1",
                    ),
                ),
            )
        )


def test_target_ref_cannot_resolve_against_source_only() -> None:
    with pytest.raises(
        OfficialTaxonomyCorrespondenceError
    ):
        correspondence(
            relations=(
                relation(
                    target_ids=(
                        "SOURCE-H-C1",
                    ),
                ),
            )
        )


def test_relationship_ids_are_unique() -> None:
    with pytest.raises(
        OfficialTaxonomyCorrespondenceError
    ):
        correspondence(
            relations=(
                relation("R1"),
                relation("R1"),
            )
        )


def test_correspondence_requires_at_least_one_relation() -> None:
    with pytest.raises(
        OfficialTaxonomyCorrespondenceError
    ):
        correspondence(
            relations=(),
        )


def test_publisher_change_type_is_captured_source_metadata() -> None:
    value = relation(
        publisher_change_type=(
            "partial recode according to publisher"
        )
    )

    assert (
        value.publisher_change_type
        == "partial recode according to publisher"
    )


def test_publisher_description_is_first_class_and_optional() -> None:
    populated = relation(
        publisher_description="Detailed publisher note"
    )

    absent = relation(
        publisher_description=None
    )

    assert (
        populated.publisher_description
        == "Detailed publisher note"
    )
    assert absent.publisher_description is None


def test_one_to_one_does_not_create_equivalence_authority() -> None:
    value = relation()

    assert (
        value.cardinality
        is OfficialTaxonomyCorrespondenceCardinality.ONE_TO_ONE
    )

    actual = {
        item.name
        for item in fields(
            OfficialTaxonomyCorrespondenceRelation
        )
    }

    assert "equivalent" not in actual
    assert "equivalence" not in actual
    assert "equivalence_confidence" not in actual


def test_partial_scope_does_not_require_fake_percentage() -> None:
    value = relation(
        publisher_change_type="partial",
        publisher_description=(
            "Only part of the source activity is represented."
        ),
    )

    actual = {
        item.name
        for item in fields(
            OfficialTaxonomyCorrespondenceRelation
        )
    }

    assert value.publisher_change_type == "partial"
    assert "percentage" not in actual
    assert "weight" not in actual
    assert "confidence" not in actual


def test_relation_source_artifact_refs_are_canonicalized() -> None:
    value = relation(
        source_refs=(
            "TABLE-B",
            "TABLE-A",
        )
    )

    assert value.source_artifact_refs == (
        "TABLE-A",
        "TABLE-B",
    )


def test_relation_source_refs_must_resolve_to_aggregate_source_set() -> None:
    with pytest.raises(
        OfficialTaxonomyCorrespondenceError
    ):
        correspondence(
            source_refs=(
                "CORRESPONDENCE",
            ),
            relations=(
                relation(
                    source_refs=(
                        "MISSING",
                    ),
                ),
            ),
        )


def test_same_scheme_different_version_is_supported() -> None:
    value = correspondence()

    assert value.source_scheme_id == value.target_scheme_id
    assert (
        value.source_scheme_version
        != value.target_scheme_version
    )


def test_different_schemes_are_supported() -> None:
    target = hierarchy(
        hierarchy_id="NAICS-H",
        snapshot_id="NAICS-S",
        snapshot_digest=TARGET_SNAPSHOT_DIGEST,
        scheme_id="NAICS",
        scheme_version="2022",
        jurisdiction="US",
        child_codes=(
            "111110",
            "111120",
        ),
    )

    value = correspondence(
        target=target,
        relations=(
            relation(
                target_ids=(
                    "NAICS-H-C1",
                ),
            ),
        ),
    )

    assert value.source_scheme_id == "ISIC"
    assert value.target_scheme_id == "NAICS"


def test_exact_same_hierarchy_self_correspondence_is_rejected() -> None:
    source = source_hierarchy()

    with pytest.raises(
        OfficialTaxonomyCorrespondenceError
    ):
        correspondence(
            source=source,
            target=source,
            relations=(
                relation(
                    source_ids=(
                        "SOURCE-H-C1",
                    ),
                    target_ids=(
                        "SOURCE-H-C2",
                    ),
                ),
            ),
        )


def test_relation_order_does_not_change_correspondence_digest() -> None:
    first = relation(
        "R-A",
        source_ids=("SOURCE-H-C1",),
        target_ids=("TARGET-H-C1",),
    )

    second = relation(
        "R-B",
        source_ids=("SOURCE-H-C2",),
        target_ids=(
            "TARGET-H-C2",
            "TARGET-H-C3",
        ),
    )

    one = correspondence(
        relations=(
            first,
            second,
        )
    )

    two = correspondence(
        relations=(
            second,
            first,
        )
    )

    assert one.relations == two.relations
    assert (
        one.correspondence_digest
        == two.correspondence_digest
    )


def test_aggregate_source_ref_order_does_not_change_digest() -> None:
    first = relation(
        source_refs=(
            "TABLE-A",
            "TABLE-B",
        )
    )

    second = relation(
        source_refs=(
            "TABLE-B",
            "TABLE-A",
        )
    )

    one = correspondence(
        source_refs=(
            "TABLE-A",
            "TABLE-B",
        ),
        relations=(
            first,
        ),
    )

    two = correspondence(
        source_refs=(
            "TABLE-B",
            "TABLE-A",
        ),
        relations=(
            second,
        ),
    )

    assert one == two
    assert (
        one.correspondence_digest
        == two.correspondence_digest
    )


def test_correspondence_digest_is_lowercase_sha3_512() -> None:
    value = correspondence()

    assert len(
        value.correspondence_digest
    ) == 128

    assert (
        value.correspondence_digest
        == value.correspondence_digest.lower()
    )

    assert all(
        character in "0123456789abcdef"
        for character in value.correspondence_digest
    )


def test_semantic_relation_change_changes_digest() -> None:
    original = correspondence()

    changed = correspondence(
        relations=(
            relation(
                publisher_description=(
                    "changed official publisher description"
                )
            ),
        )
    )

    assert (
        original.correspondence_digest
        != changed.correspondence_digest
    )


def test_strict_round_trip_requires_same_bound_hierarchies() -> None:
    source = source_hierarchy()
    target = target_hierarchy()

    original = correspondence(
        source=source,
        target=target,
    )

    restored = OfficialTaxonomyCorrespondence.from_dict(
        original.to_dict(),
        source_hierarchy=source,
        target_hierarchy=target,
    )

    assert restored == original
    assert (
        restored.correspondence_digest
        == original.correspondence_digest
    )


def test_hydration_rejects_wrong_source_hierarchy_binding() -> None:
    original = correspondence()

    wrong_source = hierarchy(
        hierarchy_id="WRONG-H",
        snapshot_id="WRONG-S",
        snapshot_digest=hashlib.sha3_512(
            b"wrong"
        ).hexdigest(),
        scheme_id="ISIC",
        scheme_version="REV4",
    )

    with pytest.raises(
        OfficialTaxonomyCorrespondenceError
    ):
        OfficialTaxonomyCorrespondence.from_dict(
            original.to_dict(),
            source_hierarchy=wrong_source,
            target_hierarchy=target_hierarchy(),
        )


def test_hydration_rejects_missing_extra_and_corrupt_truth() -> None:
    source = source_hierarchy()
    target = target_hierarchy()

    payload = correspondence(
        source=source,
        target=target,
    ).to_dict()

    missing = dict(payload)
    missing.pop("source_scheme_id")

    with pytest.raises(
        OfficialTaxonomyCorrespondenceError
    ):
        OfficialTaxonomyCorrespondence.from_dict(
            missing,
            source_hierarchy=source,
            target_hierarchy=target,
        )

    extra = dict(payload)
    extra["surprise"] = True

    with pytest.raises(
        OfficialTaxonomyCorrespondenceError
    ):
        OfficialTaxonomyCorrespondence.from_dict(
            extra,
            source_hierarchy=source,
            target_hierarchy=target,
        )

    corrupt = dict(payload)
    corrupt["correspondence_digest"] = "0" * 128

    with pytest.raises(
        OfficialTaxonomyCorrespondenceError
    ):
        OfficialTaxonomyCorrespondence.from_dict(
            corrupt,
            source_hierarchy=source,
            target_hierarchy=target,
        )


def test_correspondence_contains_no_tenant_regulatory_or_commercial_authority(
) -> None:
    forbidden = {
        "tenant_id",
        "principal_id",
        "organization_id",
        "subscription_id",
        "entitlement",
        "permission",
        "authorization",
        "business_role",
        "service_pack",
        "workflow",
        "classification_confirmation",
        "regulatory_status",
        "ai_authority",
        "payment",
        "billing",
        "settlement",
        "financial_execution",
        "kennel_command",
    }

    actual: set[str] = set()

    for cls in (
        OfficialTaxonomyCorrespondence,
        OfficialTaxonomyCorrespondenceRelation,
    ):
        actual.update(
            item.name
            for item in fields(cls)
        )

    assert forbidden.isdisjoint(
        actual
    )


def test_domain_exposes_no_network_classification_or_activation_methods(
) -> None:
    forbidden_exact = {
        "fetch",
        "download",
        "crawl",
        "search_web",
        "classify_tenant",
        "activate_service",
        "grant",
        "authorize",
        "pay",
        "settle",
        "execute_financial",
    }

    forbidden_prefixes = (
        "fetch_",
        "download_",
        "crawl_",
        "search_web_",
        "classify_tenant_",
        "activate_service_",
        "grant_",
        "authorize_",
        "execute_payment_",
        "execute_settlement_",
        "execute_financial_",
    )

    for cls in (
        OfficialTaxonomyCorrespondence,
        OfficialTaxonomyCorrespondenceRelation,
    ):
        methods = {
            name.lower()
            for name in vars(cls)
            if callable(
                getattr(
                    cls,
                    name,
                    None,
                )
            )
        }

        assert forbidden_exact.isdisjoint(
            methods
        )

        assert not any(
            method.startswith(prefix)
            for method in methods
            for prefix in forbidden_prefixes
        )


# =============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_official_taxonomy_correspondence_domain.py
# VERSION: v1.0.0-OFFICIAL-TAXONOMY-CORRESPONDENCE-DOMAIN-TEST
# AUTHORITY BOUNDARY: set-to-set official taxonomy correspondence only; source
# and target hierarchy truth remain owned by OfficialTaxonomyHierarchy
# TENANT POSTURE: platform reference truth; no tenant identity or tenant grant
# FAIL-CLOSED POSTURE: category membership, relation identity, cardinality,
# hierarchy binding, source provenance, hydration and cryptographic integrity
# are validated without inventing equivalence or percentages
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
