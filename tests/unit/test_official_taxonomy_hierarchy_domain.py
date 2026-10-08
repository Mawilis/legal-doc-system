# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN TEST-FIRST CERTIFICATION ARTIFACT
OFFICIAL TAXONOMY HIERARCHY DOMAIN
===============================================================================

TITLE:
    WILSY OS Official Taxonomy Hierarchy Aggregate Test-First Contract

VERSION:
    v1.1.0-OFFICIAL-TAXONOMY-HIERARCHY-DOMAIN-TEST

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Freezes immutable snapshot-bound category hierarchy truth for an official
    classification system as one aggregate capable of proving category
    uniqueness, parent resolution, level transitions, acyclicity, terminal
    semantics and deterministic integrity.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_official_taxonomy_hierarchy_domain.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-10-08

CHANGELOG:
    v1.1.0-OFFICIAL-TAXONOMY-HIERARCHY-DOMAIN-TEST
        - Initial aggregate hierarchy contract.
        - Binds hierarchy to one immutable official-taxonomy snapshot.
        - Keeps hierarchy levels scheme-defined rather than ISIC-specific.
        - Treats publisher codes as opaque exact strings.
        - Supports alphabetic, numeric and range-shaped publisher codes.
        - Supports multiple roots.
        - Requires explicit parent relationships and valid adjacent level
          transitions.
        - Rejects orphan parents, self-parenting and cycles.
        - Requires category identifiers and code coordinates to be unambiguous.
        - Freezes multilingual category text and per-text source provenance.
        - Freezes definitions, explanatory notes, inclusions and exclusions.
        - Canonicalizes unordered inputs before SHA3-512 integrity.
        - Excludes correspondence, tenant classification, service activation,
          entitlement, authorization, network and financial execution authority.

    v1.1.0-OFFICIAL-TAXONOMY-HIERARCHY-DOMAIN-TEST
        - Freezes v1.1.0 pure-domain snapshot-binding validation.
        - Adds exact snapshot identity, digest, scheme, version and
          jurisdiction binding requirements.
        - Makes hierarchy source_artifact_refs explicitly resolve to
          authoritative Snapshot source artifact_id values.
        - Requires validation to remain pure, non-mutating and
          serialization-neutral.

TENANT BOUNDARY:
    Platform reference truth only. No tenant or principal identity exists here.

AUTHORITY BOUNDARY:
    Official category/hierarchy semantics only. No cross-taxonomy
    correspondence, tenant classification, service-pack activation,
    entitlement, permission, user authorization, AI execution or finance.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.

FUTURE PRODUCTION PATH:
    tools/eos/saas/domain/official_taxonomy_hierarchy.py
===============================================================================
"""

from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib


from dataclasses import fields
import hashlib

import pytest

from tools.eos.saas.domain.official_taxonomy_snapshot import (
    OfficialTaxonomyArtifactKind,
    OfficialTaxonomySnapshot,
    OfficialTaxonomySourceArtifact,
)

from tools.eos.saas.domain.official_taxonomy_hierarchy import (
    SCHEMA_VERSION,
    VERSION,
    OfficialTaxonomyCategory,
    OfficialTaxonomyCategoryText,
    OfficialTaxonomyHierarchy,
    OfficialTaxonomyHierarchyError,
    OfficialTaxonomyHierarchyLevel,
)


EXPECTED_VERSION = (
    "v1.1.0-WILSY-OFFICIAL-TAXONOMY-HIERARCHY"
)

EXPECTED_SCHEMA_VERSION = (
    "wilsy.official.taxonomy.hierarchy.v1"
)

SNAPSHOT_DIGEST = hashlib.sha3_512(
    b"official-taxonomy-snapshot"
).hexdigest()


def level(
    level_id: str,
    rank: int,
    title: str,
    source_refs: tuple[str, ...] = ("STRUCTURE",),
) -> OfficialTaxonomyHierarchyLevel:
    """Build one scheme-defined hierarchy-level fixture."""
    return OfficialTaxonomyHierarchyLevel(
        level_id=level_id,
        rank=rank,
        title=title,
        source_artifact_refs=source_refs,
    )


def text_value(
    language_tag: str = "en",
    *,
    title: str = "Category",
    definition: str | None = None,
    notes: tuple[str, ...] = (),
    inclusions: tuple[str, ...] = (),
    exclusions: tuple[str, ...] = (),
    source_refs: tuple[str, ...] = ("STRUCTURE",),
) -> OfficialTaxonomyCategoryText:
    """Build one localized official category-text fixture."""
    return OfficialTaxonomyCategoryText(
        language_tag=language_tag,
        title=title,
        definition=definition,
        explanatory_notes=notes,
        inclusions=inclusions,
        exclusions=exclusions,
        source_artifact_refs=source_refs,
    )


def category(
    category_id: str,
    level_id: str,
    code: str,
    parent_category_id: str | None,
    terminal: bool,
    *,
    texts: tuple[
        OfficialTaxonomyCategoryText,
        ...,
    ] | None = None,
    source_refs: tuple[str, ...] = ("STRUCTURE",),
) -> OfficialTaxonomyCategory:
    """Build one official category fixture."""
    return OfficialTaxonomyCategory(
        category_id=category_id,
        level_id=level_id,
        code=code,
        parent_category_id=parent_category_id,
        terminal=terminal,
        source_artifact_refs=source_refs,
        texts=(
            texts
            if texts is not None
            else (
                text_value(
                    title=category_id,
                ),
            )
        ),
    )


def hierarchy(
    *,
    hierarchy_id: str = "HIERARCHY-1",
    snapshot_id: str = "SNAPSHOT-1",
    snapshot_digest: str = SNAPSHOT_DIGEST,
    scheme_id: str = "ISIC",
    scheme_version: str = "REV5",
    jurisdiction: str = "GLOBAL",
    levels: tuple[
        OfficialTaxonomyHierarchyLevel,
        ...,
    ] | None = None,
    categories: tuple[
        OfficialTaxonomyCategory,
        ...,
    ] | None = None,
    source_refs: tuple[str, ...] = (
        "STRUCTURE",
        "NOTES",
    ),
) -> OfficialTaxonomyHierarchy:
    """Build one complete snapshot-bound hierarchy fixture."""
    actual_levels = (
        levels
        if levels is not None
        else (
            level(
                "SECTION",
                0,
                "Section",
            ),
            level(
                "DIVISION",
                1,
                "Division",
            ),
        )
    )

    actual_categories = (
        categories
        if categories is not None
        else (
            category(
                "CAT-A",
                "SECTION",
                "A",
                None,
                False,
            ),
            category(
                "CAT-01",
                "DIVISION",
                "01",
                "CAT-A",
                True,
            ),
        )
    )

    return OfficialTaxonomyHierarchy(
        hierarchy_id=hierarchy_id,
        snapshot_id=snapshot_id,
        snapshot_digest=snapshot_digest,
        scheme_id=scheme_id,
        scheme_version=scheme_version,
        jurisdiction=jurisdiction,
        source_artifact_refs=source_refs,
        levels=actual_levels,
        categories=actual_categories,
    )


def test_version_and_schema_are_exact() -> None:
    assert VERSION == EXPECTED_VERSION
    assert SCHEMA_VERSION == EXPECTED_SCHEMA_VERSION


def test_hierarchy_is_platform_reference_truth_not_tenant_truth() -> None:
    names = {
        item.name
        for item in fields(
            OfficialTaxonomyHierarchy
        )
    }

    assert "tenant_id" not in names
    assert "principal_id" not in names
    assert "organization_id" not in names


def test_hierarchy_is_exactly_bound_to_snapshot_coordinates() -> None:
    value = hierarchy()

    assert value.snapshot_id == "SNAPSHOT-1"
    assert value.snapshot_digest == SNAPSHOT_DIGEST
    assert value.scheme_id == "ISIC"
    assert value.scheme_version == "REV5"
    assert value.jurisdiction == "GLOBAL"


def test_snapshot_digest_requires_lowercase_sha3_512() -> None:
    for invalid in (
        "",
        "a" * 127,
        "a" * 129,
        "A" * 128,
        "g" * 128,
    ):
        with pytest.raises(
            OfficialTaxonomyHierarchyError
        ):
            OfficialTaxonomyHierarchy(
                hierarchy_id="H",
                snapshot_id="S",
                snapshot_digest=invalid,
                scheme_id="X",
                scheme_version="1",
                jurisdiction="GLOBAL",
                source_artifact_refs=("STRUCTURE",),
                levels=(
                    level(
                        "ROOT",
                        0,
                        "Root",
                    ),
                ),
                categories=(
                    category(
                        "C",
                        "ROOT",
                        "A",
                        None,
                        True,
                    ),
                ),
            )


def test_hierarchy_levels_are_scheme_defined_not_isic_hardcoded() -> None:
    value = hierarchy(
        levels=(
            level(
                "SECTOR",
                0,
                "Sector",
            ),
            level(
                "SUBSECTOR",
                1,
                "Subsector",
            ),
            level(
                "NATIONAL_INDUSTRY",
                2,
                "National Industry",
            ),
        ),
        categories=(
            category(
                "C-31-33",
                "SECTOR",
                "31-33",
                None,
                False,
            ),
            category(
                "C-311",
                "SUBSECTOR",
                "311",
                "C-31-33",
                False,
            ),
            category(
                "C-311111",
                "NATIONAL_INDUSTRY",
                "311111",
                "C-311",
                True,
            ),
        ),
    )

    assert tuple(
        item.level_id
        for item in value.levels
    ) == (
        "SECTOR",
        "SUBSECTOR",
        "NATIONAL_INDUSTRY",
    )


def test_level_rank_is_nonnegative_integer_not_bool() -> None:
    assert level(
        "ROOT",
        0,
        "Root",
    ).rank == 0

    for invalid in (
        -1,
        True,
        False,
        1.5,
    ):
        with pytest.raises(
            OfficialTaxonomyHierarchyError
        ):
            level(
                "ROOT",
                invalid,  # type: ignore[arg-type]
                "Root",
            )


def test_level_ids_are_unique() -> None:
    duplicate = level(
        "LEVEL",
        1,
        "Duplicate",
    )

    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        hierarchy(
            levels=(
                level(
                    "LEVEL",
                    0,
                    "Root",
                ),
                duplicate,
            ),
            categories=(
                category(
                    "ROOT",
                    "LEVEL",
                    "A",
                    None,
                    True,
                ),
            ),
        )


def test_level_ranks_are_unique_and_contiguous_from_zero() -> None:
    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        hierarchy(
            levels=(
                level(
                    "ROOT",
                    0,
                    "Root",
                ),
                level(
                    "CHILD",
                    2,
                    "Child",
                ),
            ),
            categories=(
                category(
                    "ROOT-CAT",
                    "ROOT",
                    "A",
                    None,
                    True,
                ),
            ),
        )

    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        hierarchy(
            levels=(
                level(
                    "ROOT",
                    0,
                    "Root",
                ),
                level(
                    "OTHER",
                    0,
                    "Other",
                ),
            ),
            categories=(
                category(
                    "ROOT-CAT",
                    "ROOT",
                    "A",
                    None,
                    True,
                ),
            ),
        )


def test_codes_are_opaque_exact_text_and_range_codes_survive() -> None:
    value = hierarchy(
        levels=(
            level(
                "ROOT",
                0,
                "Root",
            ),
        ),
        categories=(
            category(
                "RANGE",
                "ROOT",
                "31-33",
                None,
                True,
            ),
        ),
    )

    assert value.categories[0].code == "31-33"


def test_alphabetic_codes_survive_without_normalization() -> None:
    value = hierarchy(
        levels=(
            level(
                "ROOT",
                0,
                "Root",
            ),
        ),
        categories=(
            category(
                "ALPHA",
                "ROOT",
                "A",
                None,
                True,
            ),
        ),
    )

    assert value.categories[0].code == "A"


def test_code_ancestry_is_explicit_not_inferred_from_text_shape() -> None:
    value = hierarchy(
        levels=(
            level(
                "ROOT",
                0,
                "Root",
            ),
            level(
                "CHILD",
                1,
                "Child",
            ),
        ),
        categories=(
            category(
                "PARENT",
                "ROOT",
                "31-33",
                None,
                False,
            ),
            category(
                "CHILD",
                "CHILD",
                "999999",
                "PARENT",
                True,
            ),
        ),
    )

    child = next(
        item
        for item in value.categories
        if item.category_id == "CHILD"
    )

    assert child.parent_category_id == "PARENT"


def test_multiple_root_categories_are_supported() -> None:
    value = hierarchy(
        levels=(
            level(
                "ROOT",
                0,
                "Root",
            ),
        ),
        categories=(
            category(
                "ROOT-A",
                "ROOT",
                "A",
                None,
                True,
            ),
            category(
                "ROOT-B",
                "ROOT",
                "B",
                None,
                True,
            ),
        ),
    )

    assert {
        item.category_id
        for item in value.categories
        if item.parent_category_id is None
    } == {
        "ROOT-A",
        "ROOT-B",
    }


def test_root_categories_must_use_lowest_rank_and_have_no_parent() -> None:
    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        hierarchy(
            categories=(
                category(
                    "INVALID",
                    "DIVISION",
                    "01",
                    None,
                    True,
                ),
            ),
        )


def test_non_root_categories_require_parent() -> None:
    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        hierarchy(
            categories=(
                category(
                    "ROOT",
                    "SECTION",
                    "A",
                    None,
                    True,
                ),
                category(
                    "ORPHAN-SHAPE",
                    "DIVISION",
                    "01",
                    None,
                    True,
                ),
            ),
        )


def test_parent_reference_must_resolve() -> None:
    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        hierarchy(
            categories=(
                category(
                    "ROOT",
                    "SECTION",
                    "A",
                    None,
                    False,
                ),
                category(
                    "CHILD",
                    "DIVISION",
                    "01",
                    "MISSING",
                    True,
                ),
            ),
        )


def test_self_parenting_is_rejected() -> None:
    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        hierarchy(
            categories=(
                category(
                    "ROOT",
                    "SECTION",
                    "A",
                    None,
                    False,
                ),
                category(
                    "SELF",
                    "DIVISION",
                    "01",
                    "SELF",
                    True,
                ),
            ),
        )


def test_parent_must_be_at_immediately_previous_level_rank() -> None:
    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        hierarchy(
            levels=(
                level(
                    "L0",
                    0,
                    "L0",
                ),
                level(
                    "L1",
                    1,
                    "L1",
                ),
                level(
                    "L2",
                    2,
                    "L2",
                ),
            ),
            categories=(
                category(
                    "ROOT",
                    "L0",
                    "A",
                    None,
                    False,
                ),
                category(
                    "SKIP",
                    "L2",
                    "A1",
                    "ROOT",
                    True,
                ),
            ),
        )


def test_cycles_are_rejected_fail_closed() -> None:
    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        hierarchy(
            levels=(
                level(
                    "L0",
                    0,
                    "L0",
                ),
                level(
                    "L1",
                    1,
                    "L1",
                ),
            ),
            categories=(
                category(
                    "A",
                    "L0",
                    "A",
                    "B",
                    False,
                ),
                category(
                    "B",
                    "L1",
                    "B",
                    "A",
                    False,
                ),
            ),
        )


def test_category_ids_are_unique() -> None:
    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        hierarchy(
            levels=(
                level(
                    "ROOT",
                    0,
                    "Root",
                ),
            ),
            categories=(
                category(
                    "DUP",
                    "ROOT",
                    "A",
                    None,
                    True,
                ),
                category(
                    "DUP",
                    "ROOT",
                    "B",
                    None,
                    True,
                ),
            ),
        )


def test_category_codes_are_unique_within_snapshot_bound_hierarchy() -> None:
    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        hierarchy(
            levels=(
                level(
                    "ROOT",
                    0,
                    "Root",
                ),
            ),
            categories=(
                category(
                    "A",
                    "ROOT",
                    "X",
                    None,
                    True,
                ),
                category(
                    "B",
                    "ROOT",
                    "X",
                    None,
                    True,
                ),
            ),
        )


def test_terminal_flag_must_match_graph_leaf_state() -> None:
    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        hierarchy(
            categories=(
                category(
                    "ROOT",
                    "SECTION",
                    "A",
                    None,
                    True,
                ),
                category(
                    "CHILD",
                    "DIVISION",
                    "01",
                    "ROOT",
                    True,
                ),
            ),
        )

    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        hierarchy(
            levels=(
                level(
                    "ROOT",
                    0,
                    "Root",
                ),
            ),
            categories=(
                category(
                    "LEAF",
                    "ROOT",
                    "A",
                    None,
                    False,
                ),
            ),
        )


def test_category_supports_multilingual_text_variants() -> None:
    value = hierarchy(
        levels=(
            level(
                "ROOT",
                0,
                "Root",
            ),
        ),
        categories=(
            category(
                "A",
                "ROOT",
                "A",
                None,
                True,
                texts=(
                    text_value(
                        "en",
                        title="Agriculture",
                        source_refs=(
                            "STRUCTURE",
                            "NOTES",
                        ),
                    ),
                    text_value(
                        "fr",
                        title="Agriculture FR",
                        source_refs=(
                            "NOTES-FR",
                        ),
                    ),
                ),
            ),
        ),
        source_refs=(
            "STRUCTURE",
            "NOTES",
            "NOTES-FR",
        ),
    )

    category_value = value.categories[0]

    assert {
        item.language_tag
        for item in category_value.texts
    } == {
        "en",
        "fr",
    }


def test_category_text_language_tags_are_unique() -> None:
    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        category(
            "A",
            "ROOT",
            "A",
            None,
            True,
            texts=(
                text_value(
                    "en",
                    title="One",
                ),
                text_value(
                    "en",
                    title="Two",
                ),
            ),
        )


def test_definition_notes_inclusions_and_exclusions_are_first_class() -> None:
    value = text_value(
        title="Retail",
        definition="Official definition",
        notes=(
            "Official explanatory note",
        ),
        inclusions=(
            "Includes official activity",
        ),
        exclusions=(
            "Excludes official activity",
        ),
    )

    assert value.definition == "Official definition"
    assert value.explanatory_notes == (
        "Official explanatory note",
    )
    assert value.inclusions == (
        "Includes official activity",
    )
    assert value.exclusions == (
        "Excludes official activity",
    )


def test_textual_semantics_preserve_source_artifact_provenance() -> None:
    value = text_value(
        source_refs=(
            "STRUCTURE",
            "NOTES",
        )
    )

    assert value.source_artifact_refs == (
        "NOTES",
        "STRUCTURE",
    )


def test_all_local_source_artifact_refs_must_resolve_to_hierarchy_source_set(
) -> None:
    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        hierarchy(
            levels=(
                level(
                    "ROOT",
                    0,
                    "Root",
                    source_refs=(
                        "MISSING",
                    ),
                ),
            ),
            categories=(
                category(
                    "A",
                    "ROOT",
                    "A",
                    None,
                    True,
                ),
            ),
        )


def test_level_input_order_does_not_change_hierarchy_digest() -> None:
    l0 = level(
        "ROOT",
        0,
        "Root",
    )
    l1 = level(
        "CHILD",
        1,
        "Child",
    )

    categories = (
        category(
            "A",
            "ROOT",
            "A",
            None,
            False,
        ),
        category(
            "A1",
            "CHILD",
            "A1",
            "A",
            True,
        ),
    )

    one = hierarchy(
        levels=(
            l0,
            l1,
        ),
        categories=categories,
    )

    two = hierarchy(
        levels=(
            l1,
            l0,
        ),
        categories=categories,
    )

    assert one.levels == two.levels
    assert one.hierarchy_digest == two.hierarchy_digest


def test_category_input_order_does_not_change_hierarchy_digest() -> None:
    root = category(
        "A",
        "SECTION",
        "A",
        None,
        False,
    )
    child = category(
        "01",
        "DIVISION",
        "01",
        "A",
        True,
    )

    one = hierarchy(
        categories=(
            root,
            child,
        )
    )

    two = hierarchy(
        categories=(
            child,
            root,
        )
    )

    assert one.categories == two.categories
    assert one.hierarchy_digest == two.hierarchy_digest


def test_text_and_reference_input_order_are_canonicalized() -> None:
    en = text_value(
        "en",
        title="English",
        source_refs=(
            "NOTES",
            "STRUCTURE",
        ),
    )
    fr = text_value(
        "fr",
        title="French",
        source_refs=(
            "STRUCTURE",
            "NOTES",
        ),
    )

    one = hierarchy(
        levels=(
            level(
                "ROOT",
                0,
                "Root",
                source_refs=(
                    "STRUCTURE",
                    "NOTES",
                ),
            ),
        ),
        categories=(
            category(
                "A",
                "ROOT",
                "A",
                None,
                True,
                texts=(
                    en,
                    fr,
                ),
                source_refs=(
                    "STRUCTURE",
                    "NOTES",
                ),
            ),
        ),
        source_refs=(
            "STRUCTURE",
            "NOTES",
        ),
    )

    two = hierarchy(
        levels=(
            level(
                "ROOT",
                0,
                "Root",
                source_refs=(
                    "NOTES",
                    "STRUCTURE",
                ),
            ),
        ),
        categories=(
            category(
                "A",
                "ROOT",
                "A",
                None,
                True,
                texts=(
                    fr,
                    en,
                ),
                source_refs=(
                    "NOTES",
                    "STRUCTURE",
                ),
            ),
        ),
        source_refs=(
            "NOTES",
            "STRUCTURE",
        ),
    )

    assert one == two
    assert one.hierarchy_digest == two.hierarchy_digest


def test_hierarchy_digest_is_lowercase_sha3_512() -> None:
    value = hierarchy()

    assert len(value.hierarchy_digest) == 128
    assert value.hierarchy_digest == value.hierarchy_digest.lower()
    assert all(
        item in "0123456789abcdef"
        for item in value.hierarchy_digest
    )


def test_semantic_change_changes_hierarchy_digest() -> None:
    original = hierarchy()

    changed = hierarchy(
        categories=(
            category(
                "CAT-A",
                "SECTION",
                "A",
                None,
                False,
            ),
            category(
                "CAT-01",
                "DIVISION",
                "01",
                "CAT-A",
                True,
                texts=(
                    text_value(
                        title="Changed official title",
                    ),
                ),
            ),
        )
    )

    assert (
        original.hierarchy_digest
        != changed.hierarchy_digest
    )


def test_strict_round_trip_preserves_hierarchy_truth() -> None:
    original = hierarchy()

    restored = OfficialTaxonomyHierarchy.from_dict(
        original.to_dict()
    )

    assert restored == original
    assert (
        restored.hierarchy_digest
        == original.hierarchy_digest
    )


def test_hydration_rejects_missing_extra_and_corrupt_truth() -> None:
    payload = hierarchy().to_dict()

    missing = dict(payload)
    missing.pop("scheme_id")

    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        OfficialTaxonomyHierarchy.from_dict(
            missing
        )

    extra = dict(payload)
    extra["surprise"] = True

    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        OfficialTaxonomyHierarchy.from_dict(
            extra
        )

    corrupt = dict(payload)
    corrupt["hierarchy_digest"] = "0" * 128

    with pytest.raises(
        OfficialTaxonomyHierarchyError
    ):
        OfficialTaxonomyHierarchy.from_dict(
            corrupt
        )


def test_hierarchy_contains_no_correspondence_authority() -> None:
    forbidden = {
        "source_code",
        "target_code",
        "mapping_type",
        "relationship_type",
        "equivalent",
        "correspondence_set_id",
    }

    actual: set[str] = set()

    for cls in (
        OfficialTaxonomyHierarchy,
        OfficialTaxonomyHierarchyLevel,
        OfficialTaxonomyCategory,
        OfficialTaxonomyCategoryText,
    ):
        actual.update(
            item.name
            for item in fields(cls)
        )

    assert forbidden.isdisjoint(
        actual
    )


def test_hierarchy_contains_no_tenant_commercial_or_execution_authority(
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
        "ai_authority",
        "payment",
        "billing",
        "settlement",
        "financial_execution",
        "kennel_command",
    }

    actual: set[str] = set()

    for cls in (
        OfficialTaxonomyHierarchy,
        OfficialTaxonomyHierarchyLevel,
        OfficialTaxonomyCategory,
        OfficialTaxonomyCategoryText,
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
        OfficialTaxonomyHierarchy,
        OfficialTaxonomyHierarchyLevel,
        OfficialTaxonomyCategory,
        OfficialTaxonomyCategoryText,
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


def binding_source_artifact(
    artifact_id: str,
) -> OfficialTaxonomySourceArtifact:
    """Build one authoritative snapshot source artifact for binding tests."""
    return OfficialTaxonomySourceArtifact(
        artifact_id=artifact_id,
        kind=next(
            iter(
                OfficialTaxonomyArtifactKind
            )
        ),
        source_reference=(
            "https://example.invalid/"
            + artifact_id.lower()
        ),
        media_type="text/csv",
        language_tag="en",
        source_digest=hashlib.sha3_512(
            artifact_id.encode(
                "utf-8"
            )
        ).hexdigest(),
        size_bytes=100,
        retrieved_at=datetime(
            2026,
            10,
            8,
            0,
            0,
            tzinfo=timezone.utc,
        ),
        rights_reference=(
            "official publisher terms"
        ),
    )


def binding_snapshot(
    *,
    snapshot_id: str = "SNAPSHOT-1",
    scheme_id: str = "ISIC",
    scheme_version: str = "REV5",
    jurisdiction: str = "GLOBAL",
    artifact_ids: tuple[str, ...] = (
        "STRUCTURE",
        "NOTES",
    ),
) -> OfficialTaxonomySnapshot:
    """Build one authoritative snapshot for hierarchy-binding certification."""
    return OfficialTaxonomySnapshot(
        snapshot_id=snapshot_id,
        scheme_id=scheme_id,
        scheme_version=scheme_version,
        publisher="United Nations",
        jurisdiction=jurisdiction,
        publisher_status="official",
        release_date=date(
            2025,
            1,
            1,
        ),
        effective_from=date(
            2025,
            1,
            1,
        ),
        effective_until=None,
        ingested_at=datetime(
            2026,
            10,
            8,
            0,
            1,
            tzinfo=timezone.utc,
        ),
        source_artifacts=tuple(
            binding_source_artifact(
                artifact_id
            )
            for artifact_id in artifact_ids
        ),
        supersedes_snapshot_id=None,
    )


def hierarchy_bound_to(
    snapshot: OfficialTaxonomySnapshot,
    *,
    source_refs: tuple[str, ...] = (
        "STRUCTURE",
        "NOTES",
    ),
) -> OfficialTaxonomyHierarchy:
    """Build hierarchy coordinates bound exactly to one snapshot."""
    return hierarchy(
        snapshot_id=snapshot.snapshot_id,
        snapshot_digest=snapshot.snapshot_digest,
        scheme_id=snapshot.scheme_id,
        scheme_version=snapshot.scheme_version,
        jurisdiction=snapshot.jurisdiction,
        source_refs=source_refs,
    )


def test_validate_snapshot_binding_accepts_exact_authoritative_snapshot() -> None:
    snapshot = binding_snapshot()
    value = hierarchy_bound_to(
        snapshot
    )

    assert (
        value.validate_snapshot_binding(
            snapshot
        )
        is None
    )


def test_validate_snapshot_binding_rejects_snapshot_id_mismatch() -> None:
    snapshot = binding_snapshot()

    value = hierarchy(
        snapshot_id="SNAPSHOT-OTHER",
        snapshot_digest=snapshot.snapshot_digest,
    )

    with pytest.raises(
        OfficialTaxonomyHierarchyError,
        match=(
            "OFFICIAL_TAXONOMY_HIERARCHY_"
            "SNAPSHOT_ID_MISMATCH"
        ),
    ):
        value.validate_snapshot_binding(
            snapshot
        )


def test_validate_snapshot_binding_rejects_snapshot_digest_mismatch() -> None:
    snapshot = binding_snapshot()

    mismatched_digest = (
        "0" * 128
        if snapshot.snapshot_digest
        != "0" * 128
        else "1" * 128
    )

    value = hierarchy(
        snapshot_digest=mismatched_digest
    )

    with pytest.raises(
        OfficialTaxonomyHierarchyError,
        match=(
            "OFFICIAL_TAXONOMY_HIERARCHY_"
            "SNAPSHOT_DIGEST_MISMATCH"
        ),
    ):
        value.validate_snapshot_binding(
            snapshot
        )


def test_validate_snapshot_binding_rejects_scheme_id_mismatch() -> None:
    snapshot = binding_snapshot()

    value = hierarchy(
        snapshot_digest=snapshot.snapshot_digest,
        scheme_id="OTHER-SCHEME",
    )

    with pytest.raises(
        OfficialTaxonomyHierarchyError,
        match=(
            "OFFICIAL_TAXONOMY_HIERARCHY_"
            "SCHEME_ID_MISMATCH"
        ),
    ):
        value.validate_snapshot_binding(
            snapshot
        )


def test_validate_snapshot_binding_rejects_scheme_version_mismatch() -> None:
    snapshot = binding_snapshot()

    value = hierarchy(
        snapshot_digest=snapshot.snapshot_digest,
        scheme_version="OTHER-VERSION",
    )

    with pytest.raises(
        OfficialTaxonomyHierarchyError,
        match=(
            "OFFICIAL_TAXONOMY_HIERARCHY_"
            "SCHEME_VERSION_MISMATCH"
        ),
    ):
        value.validate_snapshot_binding(
            snapshot
        )


def test_validate_snapshot_binding_rejects_jurisdiction_mismatch() -> None:
    snapshot = binding_snapshot()

    value = hierarchy(
        snapshot_digest=snapshot.snapshot_digest,
        jurisdiction="OTHER",
    )

    with pytest.raises(
        OfficialTaxonomyHierarchyError,
        match=(
            "OFFICIAL_TAXONOMY_HIERARCHY_"
            "JURISDICTION_MISMATCH"
        ),
    ):
        value.validate_snapshot_binding(
            snapshot
        )


def test_validate_snapshot_binding_rejects_unresolved_source_artifact_ref() -> None:
    snapshot = binding_snapshot()

    value = hierarchy_bound_to(
        snapshot,
        source_refs=(
            "STRUCTURE",
            "NOTES",
            "MISSING",
        ),
    )

    with pytest.raises(
        OfficialTaxonomyHierarchyError,
        match=(
            "OFFICIAL_TAXONOMY_HIERARCHY_"
            "SOURCE_ARTIFACT_REF_UNRESOLVED"
        ),
    ):
        value.validate_snapshot_binding(
            snapshot
        )


def test_validate_snapshot_binding_allows_extra_snapshot_artifacts() -> None:
    snapshot = binding_snapshot(
        artifact_ids=(
            "STRUCTURE",
            "NOTES",
            "EXTRA",
        )
    )

    value = hierarchy_bound_to(
        snapshot
    )

    assert (
        value.validate_snapshot_binding(
            snapshot
        )
        is None
    )


def test_validate_snapshot_binding_rejects_invalid_snapshot_type() -> None:
    value = hierarchy()

    with pytest.raises(
        OfficialTaxonomyHierarchyError,
        match=(
            "OFFICIAL_TAXONOMY_HIERARCHY_"
            "SNAPSHOT_BINDING_TYPE_INVALID"
        ),
    ):
        value.validate_snapshot_binding(
            object()  # type: ignore[arg-type]
        )


def test_validate_snapshot_binding_does_not_mutate_or_change_digest() -> None:
    snapshot = binding_snapshot()

    value = hierarchy_bound_to(
        snapshot
    )

    before_payload = value.to_dict()
    before_digest = value.hierarchy_digest

    value.validate_snapshot_binding(
        snapshot
    )

    assert value.to_dict() == before_payload
    assert value.hierarchy_digest == before_digest


def test_validate_snapshot_binding_preserves_serialization_and_roundtrip() -> None:
    snapshot = binding_snapshot()

    value = hierarchy_bound_to(
        snapshot
    )

    before = value.to_dict()

    value.validate_snapshot_binding(
        snapshot
    )

    after = value.to_dict()

    assert after == before

    restored = (
        OfficialTaxonomyHierarchy.from_dict(
            after
        )
    )

    assert restored == value
    assert (
        restored.hierarchy_digest
        == value.hierarchy_digest
    )


# WILSY OS SOVEREIGN CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_official_taxonomy_hierarchy_domain.py
# VERSION: v1.1.0-OFFICIAL-TAXONOMY-HIERARCHY-DOMAIN-TEST
# AUTHORITY BOUNDARY: official snapshot-bound category hierarchy only; no
# correspondence, tenant classification, commercial, user, network, AI or
# financial execution authority
# TENANT POSTURE: platform reference truth; no tenant identity or tenant grant
# FAIL-CLOSED POSTURE: duplicate/unresolved categories, invalid levels, invalid
# parent transitions, cycles, inconsistent terminal semantics, corrupt hydration
# and widened serialized truth are rejected
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
