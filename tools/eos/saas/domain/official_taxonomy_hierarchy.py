# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN PRODUCTION ARTIFACT
OFFICIAL TAXONOMY HIERARCHY DOMAIN
===============================================================================

TITLE:
    WILSY OS Official Taxonomy Hierarchy Aggregate Domain

VERSION:
    v1.1.0-WILSY-OFFICIAL-TAXONOMY-HIERARCHY

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Immutable snapshot-bound aggregate for official taxonomy levels, categories,
    parent relationships, multilingual explanatory semantics and source
    provenance. The aggregate validates whole-graph integrity rather than
    inferring hierarchy from publisher code shape.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/official_taxonomy_hierarchy.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-10-08

CHANGELOG:
    v1.0.0-WILSY-OFFICIAL-TAXONOMY-HIERARCHY
        - Introduces immutable taxonomy hierarchy aggregate truth.
        - Binds hierarchy to an exact official taxonomy snapshot identity and
          snapshot digest.
        - Supports scheme-defined contiguous hierarchy levels.
        - Treats category codes as opaque exact publisher coordinates.
        - Supports multiple roots and explicit parent relationships.
        - Rejects unresolved parents, self-parenting, invalid level transitions
          and cycles.
        - Validates terminal flags against actual graph leaf state.
        - Supports multilingual category text, definitions, explanatory notes,
          inclusions and exclusions.
        - Binds structural and textual semantics to captured source-artifact
          references.
        - Canonicalizes levels, categories, localized texts and source-reference
          sets before deterministic SHA3-512 integrity.
        - Excludes correspondence, tenant classification, service activation,
          entitlement, authorization, network and financial authority.

    v1.1.0-WILSY-OFFICIAL-TAXONOMY-HIERARCHY
        - Adds pure validate_snapshot_binding() cross-object validation.
        - Requires exact Snapshot identity, digest, scheme, version and
          jurisdiction correspondence.
        - Defines hierarchy source_artifact_refs as references to exact
          authoritative Snapshot source_artifacts[].artifact_id values.
        - Allows additional Snapshot artifacts that this hierarchy does
          not consume.
        - Preserves schema, serialization and hierarchy digest semantics.

TENANT BOUNDARY:
    Platform reference truth only. No tenant or principal identity exists here.

AUTHORITY BOUNDARY:
    Official snapshot-bound category hierarchy semantics only. No cross-taxonomy
    correspondence, tenant classification, service-pack activation, entitlement,
    permission, user authorization, AI execution or finance.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.

NETWORK BOUNDARY:
    No fetch, download, crawl, search or remote resolution occurs here.

RUNTIME SIDE EFFECTS:
    None. Pure immutable domain aggregate.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Final, Mapping
from .official_taxonomy_snapshot import OfficialTaxonomySnapshot

VERSION: Final[str] = (
    "v1.1.0-WILSY-OFFICIAL-TAXONOMY-HIERARCHY"
)

SCHEMA_VERSION: Final[str] = (
    "wilsy.official.taxonomy.hierarchy.v1"
)

_SHA3_512_HEX_LENGTH: Final[int] = 128

_LOWER_HEX: Final[frozenset[str]] = frozenset(
    "0123456789abcdef"
)


class OfficialTaxonomyHierarchyError(ValueError):
    """Represent fail-closed hierarchy validation or integrity failure."""


def _exact_text(
    name: str,
    value: object,
) -> str:
    """Return exact non-empty non-padded text or fail closed."""
    if not isinstance(
        value,
        str,
    ):
        raise OfficialTaxonomyHierarchyError(
            f"OFFICIAL_TAXONOMY_HIERARCHY_{name.upper()}_INVALID"
        )

    if (
        not value
        or value != value.strip()
    ):
        raise OfficialTaxonomyHierarchyError(
            f"OFFICIAL_TAXONOMY_HIERARCHY_{name.upper()}_INVALID"
        )

    return value


def _optional_exact_text(
    name: str,
    value: object,
) -> str | None:
    """Return optional exact text without normalization."""
    if value is None:
        return None

    return _exact_text(
        name,
        value,
    )


def _lower_sha3_512(
    name: str,
    value: object,
) -> str:
    """Validate lowercase SHA3-512 hexadecimal shape."""
    digest = _exact_text(
        name,
        value,
    )

    if (
        len(digest)
        != _SHA3_512_HEX_LENGTH
        or any(
            character not in _LOWER_HEX
            for character in digest
        )
    ):
        raise OfficialTaxonomyHierarchyError(
            f"OFFICIAL_TAXONOMY_HIERARCHY_{name.upper()}_INVALID"
        )

    return digest


def _nonnegative_integer(
    name: str,
    value: object,
) -> int:
    """Validate a true nonnegative integer, excluding bool."""
    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            int,
        )
        or value < 0
    ):
        raise OfficialTaxonomyHierarchyError(
            f"OFFICIAL_TAXONOMY_HIERARCHY_{name.upper()}_INVALID"
        )

    return value


def _exact_bool(
    name: str,
    value: object,
) -> bool:
    """Validate a literal bool."""
    if not isinstance(
        value,
        bool,
    ):
        raise OfficialTaxonomyHierarchyError(
            f"OFFICIAL_TAXONOMY_HIERARCHY_{name.upper()}_INVALID"
        )

    return value


def _canonical_text_tuple(
    name: str,
    value: object,
    *,
    allow_empty: bool,
) -> tuple[str, ...]:
    """Validate unique exact text and canonicalize lexical ordering."""
    if not isinstance(
        value,
        (tuple, list),
    ):
        raise OfficialTaxonomyHierarchyError(
            f"OFFICIAL_TAXONOMY_HIERARCHY_{name.upper()}_INVALID"
        )

    values = tuple(
        _exact_text(
            name,
            entry,
        )
        for entry in value
    )

    if (
        not allow_empty
        and not values
    ):
        raise OfficialTaxonomyHierarchyError(
            f"OFFICIAL_TAXONOMY_HIERARCHY_{name.upper()}_EMPTY"
        )

    if len(values) != len(
        set(values)
    ):
        raise OfficialTaxonomyHierarchyError(
            f"OFFICIAL_TAXONOMY_HIERARCHY_{name.upper()}_DUPLICATE"
        )

    return tuple(
        sorted(
            values
        )
    )


def _strict_mapping(
    value: object,
    *,
    expected_keys: frozenset[str],
    surface: str,
) -> Mapping[str, Any]:
    """Require one exact serialized mapping shape."""
    if not isinstance(
        value,
        Mapping,
    ):
        raise OfficialTaxonomyHierarchyError(
            f"OFFICIAL_TAXONOMY_HIERARCHY_{surface}_INVALID"
        )

    if (
        frozenset(
            value.keys()
        )
        != expected_keys
    ):
        raise OfficialTaxonomyHierarchyError(
            f"OFFICIAL_TAXONOMY_HIERARCHY_{surface}_SHAPE_INVALID"
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class OfficialTaxonomyHierarchyLevel:
    """Represent one scheme-defined hierarchy level."""

    level_id: str
    rank: int
    title: str
    source_artifact_refs: tuple[str, ...]

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "level_id",
            _exact_text(
                "level_id",
                self.level_id,
            ),
        )

        object.__setattr__(
            self,
            "rank",
            _nonnegative_integer(
                "rank",
                self.rank,
            ),
        )

        object.__setattr__(
            self,
            "title",
            _exact_text(
                "level_title",
                self.title,
            ),
        )

        object.__setattr__(
            self,
            "source_artifact_refs",
            _canonical_text_tuple(
                "source_artifact_refs",
                self.source_artifact_refs,
                allow_empty=False,
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "level_id": self.level_id,
            "rank": self.rank,
            "title": self.title,
            "source_artifact_refs": list(
                self.source_artifact_refs
            ),
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> OfficialTaxonomyHierarchyLevel:
        expected = frozenset(
            {
                "level_id",
                "rank",
                "title",
                "source_artifact_refs",
            }
        )

        value = _strict_mapping(
            payload,
            expected_keys=expected,
            surface="LEVEL",
        )

        raw_refs = value[
            "source_artifact_refs"
        ]

        if not isinstance(
            raw_refs,
            (list, tuple),
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_SOURCE_ARTIFACT_REFS_INVALID"
            )

        return cls(
            level_id=value[
                "level_id"
            ],
            rank=value[
                "rank"
            ],
            title=value[
                "title"
            ],
            source_artifact_refs=tuple(
                raw_refs
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class OfficialTaxonomyCategoryText:
    """Represent one localized official category semantic surface."""

    language_tag: str
    title: str
    definition: str | None
    explanatory_notes: tuple[str, ...]
    inclusions: tuple[str, ...]
    exclusions: tuple[str, ...]
    source_artifact_refs: tuple[str, ...]

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "language_tag",
            _exact_text(
                "language_tag",
                self.language_tag,
            ),
        )

        object.__setattr__(
            self,
            "title",
            _exact_text(
                "category_title",
                self.title,
            ),
        )

        object.__setattr__(
            self,
            "definition",
            _optional_exact_text(
                "definition",
                self.definition,
            ),
        )

        for field_name in (
            "explanatory_notes",
            "inclusions",
            "exclusions",
        ):
            object.__setattr__(
                self,
                field_name,
                _canonical_text_tuple(
                    field_name,
                    getattr(
                        self,
                        field_name,
                    ),
                    allow_empty=True,
                ),
            )

        object.__setattr__(
            self,
            "source_artifact_refs",
            _canonical_text_tuple(
                "source_artifact_refs",
                self.source_artifact_refs,
                allow_empty=False,
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "language_tag": self.language_tag,
            "title": self.title,
            "definition": self.definition,
            "explanatory_notes": list(
                self.explanatory_notes
            ),
            "inclusions": list(
                self.inclusions
            ),
            "exclusions": list(
                self.exclusions
            ),
            "source_artifact_refs": list(
                self.source_artifact_refs
            ),
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> OfficialTaxonomyCategoryText:
        expected = frozenset(
            {
                "language_tag",
                "title",
                "definition",
                "explanatory_notes",
                "inclusions",
                "exclusions",
                "source_artifact_refs",
            }
        )

        value = _strict_mapping(
            payload,
            expected_keys=expected,
            surface="CATEGORY_TEXT",
        )

        sequence_fields = (
            "explanatory_notes",
            "inclusions",
            "exclusions",
            "source_artifact_refs",
        )

        for field_name in sequence_fields:
            if not isinstance(
                value[
                    field_name
                ],
                (list, tuple),
            ):
                raise OfficialTaxonomyHierarchyError(
                    f"OFFICIAL_TAXONOMY_HIERARCHY_{field_name.upper()}_INVALID"
                )

        return cls(
            language_tag=value[
                "language_tag"
            ],
            title=value[
                "title"
            ],
            definition=value[
                "definition"
            ],
            explanatory_notes=tuple(
                value[
                    "explanatory_notes"
                ]
            ),
            inclusions=tuple(
                value[
                    "inclusions"
                ]
            ),
            exclusions=tuple(
                value[
                    "exclusions"
                ]
            ),
            source_artifact_refs=tuple(
                value[
                    "source_artifact_refs"
                ]
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class OfficialTaxonomyCategory:
    """Represent one immutable category node inside a hierarchy aggregate."""

    category_id: str
    level_id: str
    code: str
    parent_category_id: str | None
    terminal: bool
    source_artifact_refs: tuple[str, ...]
    texts: tuple[
        OfficialTaxonomyCategoryText,
        ...,
    ]

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "category_id",
            _exact_text(
                "category_id",
                self.category_id,
            ),
        )

        object.__setattr__(
            self,
            "level_id",
            _exact_text(
                "level_id",
                self.level_id,
            ),
        )

        object.__setattr__(
            self,
            "code",
            _exact_text(
                "category_code",
                self.code,
            ),
        )

        object.__setattr__(
            self,
            "parent_category_id",
            _optional_exact_text(
                "parent_category_id",
                self.parent_category_id,
            ),
        )

        object.__setattr__(
            self,
            "terminal",
            _exact_bool(
                "terminal",
                self.terminal,
            ),
        )

        object.__setattr__(
            self,
            "source_artifact_refs",
            _canonical_text_tuple(
                "source_artifact_refs",
                self.source_artifact_refs,
                allow_empty=False,
            ),
        )

        if not isinstance(
            self.texts,
            (tuple, list),
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_TEXTS_INVALID"
            )

        texts = tuple(
            self.texts
        )

        if not texts:
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_TEXTS_EMPTY"
            )

        if not all(
            isinstance(
                entry,
                OfficialTaxonomyCategoryText,
            )
            for entry in texts
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_TEXTS_INVALID"
            )

        language_tags = tuple(
            entry.language_tag
            for entry in texts
        )

        if len(language_tags) != len(
            set(language_tags)
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_LANGUAGE_TAG_DUPLICATE"
            )

        object.__setattr__(
            self,
            "texts",
            tuple(
                sorted(
                    texts,
                    key=lambda entry: entry.language_tag,
                )
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "category_id": self.category_id,
            "level_id": self.level_id,
            "code": self.code,
            "parent_category_id": self.parent_category_id,
            "terminal": self.terminal,
            "source_artifact_refs": list(
                self.source_artifact_refs
            ),
            "texts": [
                entry.to_dict()
                for entry in self.texts
            ],
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> OfficialTaxonomyCategory:
        expected = frozenset(
            {
                "category_id",
                "level_id",
                "code",
                "parent_category_id",
                "terminal",
                "source_artifact_refs",
                "texts",
            }
        )

        value = _strict_mapping(
            payload,
            expected_keys=expected,
            surface="CATEGORY",
        )

        raw_refs = value[
            "source_artifact_refs"
        ]
        raw_texts = value[
            "texts"
        ]

        if not isinstance(
            raw_refs,
            (list, tuple),
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_SOURCE_ARTIFACT_REFS_INVALID"
            )

        if not isinstance(
            raw_texts,
            (list, tuple),
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_TEXTS_INVALID"
            )

        return cls(
            category_id=value[
                "category_id"
            ],
            level_id=value[
                "level_id"
            ],
            code=value[
                "code"
            ],
            parent_category_id=value[
                "parent_category_id"
            ],
            terminal=value[
                "terminal"
            ],
            source_artifact_refs=tuple(
                raw_refs
            ),
            texts=tuple(
                OfficialTaxonomyCategoryText.from_dict(
                    entry
                )
                for entry in raw_texts
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class OfficialTaxonomyHierarchy:
    """Represent complete category hierarchy truth for one taxonomy snapshot."""

    hierarchy_id: str
    snapshot_id: str
    snapshot_digest: str
    scheme_id: str
    scheme_version: str
    jurisdiction: str
    source_artifact_refs: tuple[str, ...]
    levels: tuple[
        OfficialTaxonomyHierarchyLevel,
        ...,
    ]
    categories: tuple[
        OfficialTaxonomyCategory,
        ...,
    ]
    hierarchy_digest: str = field(
        init=False,
        compare=True,
    )

    def __post_init__(
        self,
    ) -> None:
        for field_name in (
            "hierarchy_id",
            "snapshot_id",
            "scheme_id",
            "scheme_version",
            "jurisdiction",
        ):
            object.__setattr__(
                self,
                field_name,
                _exact_text(
                    field_name,
                    getattr(
                        self,
                        field_name,
                    ),
                ),
            )

        object.__setattr__(
            self,
            "snapshot_digest",
            _lower_sha3_512(
                "snapshot_digest",
                self.snapshot_digest,
            ),
        )

        object.__setattr__(
            self,
            "source_artifact_refs",
            _canonical_text_tuple(
                "source_artifact_refs",
                self.source_artifact_refs,
                allow_empty=False,
            ),
        )

        if not isinstance(
            self.levels,
            (tuple, list),
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_LEVELS_INVALID"
            )

        levels = tuple(
            self.levels
        )

        if not levels:
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_LEVELS_EMPTY"
            )

        if not all(
            isinstance(
                entry,
                OfficialTaxonomyHierarchyLevel,
            )
            for entry in levels
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_LEVELS_INVALID"
            )

        level_ids = tuple(
            entry.level_id
            for entry in levels
        )

        if len(level_ids) != len(
            set(level_ids)
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_LEVEL_ID_DUPLICATE"
            )

        ranks = tuple(
            entry.rank
            for entry in levels
        )

        if len(ranks) != len(
            set(ranks)
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_LEVEL_RANK_DUPLICATE"
            )

        expected_ranks = tuple(
            range(
                len(levels)
            )
        )

        if (
            tuple(
                sorted(
                    ranks
                )
            )
            != expected_ranks
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_LEVEL_RANK_SEQUENCE_INVALID"
            )

        canonical_levels = tuple(
            sorted(
                levels,
                key=lambda entry: (
                    entry.rank,
                    entry.level_id,
                ),
            )
        )

        object.__setattr__(
            self,
            "levels",
            canonical_levels,
        )

        if not isinstance(
            self.categories,
            (tuple, list),
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_CATEGORIES_INVALID"
            )

        categories = tuple(
            self.categories
        )

        if not categories:
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_CATEGORIES_EMPTY"
            )

        if not all(
            isinstance(
                entry,
                OfficialTaxonomyCategory,
            )
            for entry in categories
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_CATEGORIES_INVALID"
            )

        category_ids = tuple(
            entry.category_id
            for entry in categories
        )

        if len(category_ids) != len(
            set(category_ids)
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_CATEGORY_ID_DUPLICATE"
            )

        codes = tuple(
            entry.code
            for entry in categories
        )

        if len(codes) != len(
            set(codes)
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_CATEGORY_CODE_DUPLICATE"
            )

        level_by_id = {
            entry.level_id: entry
            for entry in canonical_levels
        }

        category_by_id = {
            entry.category_id: entry
            for entry in categories
        }

        hierarchy_sources = set(
            self.source_artifact_refs
        )

        # All local provenance refs must be declared at aggregate scope.
        for entry in canonical_levels:
            if not set(
                entry.source_artifact_refs
            ).issubset(
                hierarchy_sources
            ):
                raise OfficialTaxonomyHierarchyError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_LEVEL_SOURCE_REF_UNRESOLVED"
                )

        for entry in categories:
            if (
                entry.level_id
                not in level_by_id
            ):
                raise OfficialTaxonomyHierarchyError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_CATEGORY_LEVEL_UNRESOLVED"
                )

            if not set(
                entry.source_artifact_refs
            ).issubset(
                hierarchy_sources
            ):
                raise OfficialTaxonomyHierarchyError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_CATEGORY_SOURCE_REF_UNRESOLVED"
                )

            for text in entry.texts:
                if not set(
                    text.source_artifact_refs
                ).issubset(
                    hierarchy_sources
                ):
                    raise OfficialTaxonomyHierarchyError(
                        "OFFICIAL_TAXONOMY_HIERARCHY_TEXT_SOURCE_REF_UNRESOLVED"
                    )

        # Explicit parent and level semantics.
        for entry in categories:
            level = level_by_id[
                entry.level_id
            ]

            if level.rank == 0:
                if (
                    entry.parent_category_id
                    is not None
                ):
                    raise OfficialTaxonomyHierarchyError(
                        "OFFICIAL_TAXONOMY_HIERARCHY_ROOT_PARENT_INVALID"
                    )

                continue

            if (
                entry.parent_category_id
                is None
            ):
                raise OfficialTaxonomyHierarchyError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_PARENT_REQUIRED"
                )

            if (
                entry.parent_category_id
                == entry.category_id
            ):
                raise OfficialTaxonomyHierarchyError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_SELF_PARENT_FORBIDDEN"
                )

            parent = category_by_id.get(
                entry.parent_category_id
            )

            if parent is None:
                raise OfficialTaxonomyHierarchyError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_PARENT_UNRESOLVED"
                )

            parent_level = level_by_id[
                parent.level_id
            ]

            if (
                parent_level.rank
                != level.rank - 1
            ):
                raise OfficialTaxonomyHierarchyError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_LEVEL_TRANSITION_INVALID"
                )

        # Whole-graph cycle detection. Although valid adjacent ranks make cycles
        # impossible in a valid graph, this remains an explicit fail-closed
        # invariant instead of relying on that implication.
        for start in categories:
            seen: set[str] = set()
            current = start

            while (
                current.parent_category_id
                is not None
            ):
                if current.category_id in seen:
                    raise OfficialTaxonomyHierarchyError(
                        "OFFICIAL_TAXONOMY_HIERARCHY_CYCLE_DETECTED"
                    )

                seen.add(
                    current.category_id
                )

                parent = category_by_id.get(
                    current.parent_category_id
                )

                if parent is None:
                    break

                current = parent

        child_counts = {
            entry.category_id: 0
            for entry in categories
        }

        for entry in categories:
            if (
                entry.parent_category_id
                is not None
                and entry.parent_category_id
                in child_counts
            ):
                child_counts[
                    entry.parent_category_id
                ] += 1

        for entry in categories:
            actual_leaf = (
                child_counts[
                    entry.category_id
                ]
                == 0
            )

            if entry.terminal != actual_leaf:
                raise OfficialTaxonomyHierarchyError(
                    "OFFICIAL_TAXONOMY_HIERARCHY_TERMINAL_GRAPH_MISMATCH"
                )

        canonical_categories = tuple(
            sorted(
                categories,
                key=lambda entry: (
                    level_by_id[
                        entry.level_id
                    ].rank,
                    entry.code,
                    entry.category_id,
                ),
            )
        )

        object.__setattr__(
            self,
            "categories",
            canonical_categories,
        )

        object.__setattr__(
            self,
            "hierarchy_digest",
            self._compute_hierarchy_digest(),
        )

    def validate_snapshot_binding(
        self,
        snapshot: OfficialTaxonomySnapshot,
    ) -> None:
        """Validate this hierarchy against one authoritative taxonomy snapshot.

        This is pure domain validation. The caller supplies the authoritative
        snapshot; this method performs no persistence lookup, network access,
        parsing, tenant classification or mutation.
        """
        if not isinstance(
            snapshot,
            OfficialTaxonomySnapshot,
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_"
                "SNAPSHOT_BINDING_TYPE_INVALID"
            )

        if self.snapshot_id != snapshot.snapshot_id:
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_"
                "SNAPSHOT_ID_MISMATCH"
            )

        if self.snapshot_digest != snapshot.snapshot_digest:
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_"
                "SNAPSHOT_DIGEST_MISMATCH"
            )

        if self.scheme_id != snapshot.scheme_id:
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_"
                "SCHEME_ID_MISMATCH"
            )

        if self.scheme_version != snapshot.scheme_version:
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_"
                "SCHEME_VERSION_MISMATCH"
            )

        if self.jurisdiction != snapshot.jurisdiction:
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_"
                "JURISDICTION_MISMATCH"
            )

        snapshot_artifact_ids = {
            artifact.artifact_id
            for artifact in snapshot.source_artifacts
        }

        if not set(
            self.source_artifact_refs
        ).issubset(
            snapshot_artifact_ids
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_"
                "SOURCE_ARTIFACT_REF_UNRESOLVED"
            )

    def _semantic_payload(
        self,
    ) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "hierarchy_id": self.hierarchy_id,
            "snapshot_id": self.snapshot_id,
            "snapshot_digest": self.snapshot_digest,
            "scheme_id": self.scheme_id,
            "scheme_version": self.scheme_version,
            "jurisdiction": self.jurisdiction,
            "source_artifact_refs": list(
                self.source_artifact_refs
            ),
            "levels": [
                entry.to_dict()
                for entry in self.levels
            ],
            "categories": [
                entry.to_dict()
                for entry in self.categories
            ],
        }

    def _compute_hierarchy_digest(
        self,
    ) -> str:
        encoded = json.dumps(
            self._semantic_payload(),
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            ensure_ascii=False,
        ).encode(
            "utf-8"
        )

        return hashlib.sha3_512(
            encoded
        ).hexdigest()

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            **self._semantic_payload(),
            "hierarchy_digest": self.hierarchy_digest,
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> OfficialTaxonomyHierarchy:
        expected = frozenset(
            {
                "schema_version",
                "hierarchy_id",
                "snapshot_id",
                "snapshot_digest",
                "scheme_id",
                "scheme_version",
                "jurisdiction",
                "source_artifact_refs",
                "levels",
                "categories",
                "hierarchy_digest",
            }
        )

        value = _strict_mapping(
            payload,
            expected_keys=expected,
            surface="AGGREGATE",
        )

        if (
            value[
                "schema_version"
            ]
            != SCHEMA_VERSION
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_SCHEMA_VERSION_INVALID"
            )

        supplied_digest = _lower_sha3_512(
            "hierarchy_digest",
            value[
                "hierarchy_digest"
            ],
        )

        raw_refs = value[
            "source_artifact_refs"
        ]
        raw_levels = value[
            "levels"
        ]
        raw_categories = value[
            "categories"
        ]

        if not isinstance(
            raw_refs,
            (list, tuple),
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_SOURCE_ARTIFACT_REFS_INVALID"
            )

        if not isinstance(
            raw_levels,
            (list, tuple),
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_LEVELS_INVALID"
            )

        if not isinstance(
            raw_categories,
            (list, tuple),
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_CATEGORIES_INVALID"
            )

        restored = cls(
            hierarchy_id=value[
                "hierarchy_id"
            ],
            snapshot_id=value[
                "snapshot_id"
            ],
            snapshot_digest=value[
                "snapshot_digest"
            ],
            scheme_id=value[
                "scheme_id"
            ],
            scheme_version=value[
                "scheme_version"
            ],
            jurisdiction=value[
                "jurisdiction"
            ],
            source_artifact_refs=tuple(
                raw_refs
            ),
            levels=tuple(
                OfficialTaxonomyHierarchyLevel.from_dict(
                    entry
                )
                for entry in raw_levels
            ),
            categories=tuple(
                OfficialTaxonomyCategory.from_dict(
                    entry
                )
                for entry in raw_categories
            ),
        )

        if (
            restored.hierarchy_digest
            != supplied_digest
        ):
            raise OfficialTaxonomyHierarchyError(
                "OFFICIAL_TAXONOMY_HIERARCHY_DIGEST_MISMATCH"
            )

        return restored


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: official_taxonomy_hierarchy.py
# VERSION: v1.1.0-WILSY-OFFICIAL-TAXONOMY-HIERARCHY
# AUTHORITY BOUNDARY: immutable snapshot-bound official category hierarchy only;
# no correspondence, tenant classification, service activation, entitlement,
# permission, user authorization, AI, billing, payment or financial execution
# TENANT POSTURE: platform reference truth; no tenant identity or tenant grant
# FAIL-CLOSED POSTURE: levels, parents, graph integrity, provenance, terminal
# semantics, canonical ordering, hydration and SHA3-512 integrity are validated
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
