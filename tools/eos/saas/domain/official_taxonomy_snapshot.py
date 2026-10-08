# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN PRODUCTION ARTIFACT
OFFICIAL TAXONOMY SNAPSHOT DOMAIN
===============================================================================

TITLE:
    WILSY OS Official Taxonomy Snapshot Domain

VERSION:
    v1.0.0-WILSY-OFFICIAL-TAXONOMY-SNAPSHOT

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Immutable platform-reference provenance envelope for one captured edition of
    an externally published official business or economic classification
    system. Publisher identity, edition metadata, lifecycle dates, rights
    provenance and captured source artifacts are bound to deterministic
    SHA3-512 integrity without inventing hierarchy, correspondence, tenant
    classification, commercial, authorization, AI or financial truth.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/official_taxonomy_snapshot.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-10-07

CHANGELOG:
    v1.0.0-WILSY-OFFICIAL-TAXONOMY-SNAPSHOT
        - Introduces immutable official-taxonomy snapshot reference truth.
        - Captures scheme, edition, publisher, jurisdiction and
          publisher-supplied publication status.
        - Separates release date from effective validity.
        - Captures multiple official source artifacts per snapshot.
        - Captures artifact kind, media type, language tag, byte size,
          retrieval instant, rights reference and lowercase SHA3-512 digest.
        - Canonicalizes artifact ordering by immutable artifact identity so
          retrieval order cannot alter snapshot identity.
        - Supports immutable correction/supersession lineage.
        - Provides strict serialization, hydration and digest verification.
        - Treats correspondence files as source evidence only, never semantic
          mapping authority.
        - Excludes category hierarchy, tenant classification, service-pack
          activation, entitlement, authorization, live-network and financial
          execution authority.

COMPLIANCE:
    External reference material preserves provenance, source integrity and
    rights-reference coordinates for governed downstream ingestion.

SECURITY / PRIVACY POSTURE:
    Runtime reference truth is bound to captured immutable source material,
    never mutable remote content. Missing, widened, malformed or
    cryptographically corrupt hydration fails closed.

TENANT BOUNDARY:
    Official taxonomy snapshots are platform reference truth and contain no
    tenant, organization, membership, principal, role, permission or tenant
    classification authority.

AUTHORITY BOUNDARY:
    Snapshot metadata and captured source-artifact provenance only. No taxonomy
    category, hierarchy, correspondence equivalence, business classification,
    service activation, entitlement, authorization, workflow or AI execution
    authority exists in this module.

FINANCIAL AUTHORITY BOUNDARY:
    No billing, payment, settlement, accounting, banking, tender or provider
    execution authority exists here. Kennel EOS remains the exclusive financial
    execution authority.

NETWORK BOUNDARY:
    This pure domain performs no HTTP request, download, crawl, search or live
    remote resolution.

RUNTIME SIDE EFFECTS:
    None. Pure domain only.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
import hashlib
import json
from typing import Any, Final, Mapping

VERSION: Final[str] = (
    "v1.0.0-WILSY-OFFICIAL-TAXONOMY-SNAPSHOT"
)

SCHEMA_VERSION: Final[str] = (
    "wilsy.official.taxonomy.snapshot.v1"
)

_SHA3_512_HEX_LENGTH: Final[int] = 128

_LOWER_HEX: Final[frozenset[str]] = frozenset(
    "0123456789abcdef"
)


class OfficialTaxonomySnapshotError(ValueError):
    """Represent fail-closed taxonomy snapshot validation/integrity failure.

    This exception creates no hierarchy, correspondence, tenant classification,
    entitlement, authorization, AI, network or financial authority.
    """


class OfficialTaxonomyArtifactKind(str, Enum):
    """Identify the provenance role of one captured official source artifact.

    CORRESPONDENCE_SOURCE records only that the publisher supplied such an
    artifact. It does not accept or interpret mappings within that source.
    """

    STRUCTURE = "structure"
    EXPLANATORY_NOTES = "explanatory_notes"
    METHODOLOGY = "methodology"
    RELEASE_NOTICE = "release_notice"
    ERRATA = "errata"
    CORRESPONDENCE_SOURCE = "correspondence_source"
    OTHER = "other"


def _exact_text(
    name: str,
    value: object,
) -> str:
    """Return exact non-empty non-padded text or fail closed."""
    if not isinstance(
        value,
        str,
    ):
        raise OfficialTaxonomySnapshotError(
            f"OFFICIAL_TAXONOMY_{name.upper()}_INVALID"
        )

    if (
        not value
        or value != value.strip()
    ):
        raise OfficialTaxonomySnapshotError(
            f"OFFICIAL_TAXONOMY_{name.upper()}_INVALID"
        )

    return value


def _optional_exact_text(
    name: str,
    value: object,
) -> str | None:
    """Return optional exact text without silently normalizing source truth."""
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
    """Validate canonical lowercase SHA3-512 hexadecimal shape."""
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
        raise OfficialTaxonomySnapshotError(
            f"OFFICIAL_TAXONOMY_{name.upper()}_INVALID"
        )

    return digest


def _aware_utc(
    name: str,
    value: object,
) -> datetime:
    """Validate an aware datetime and normalize its represented instant to UTC."""
    if (
        not isinstance(
            value,
            datetime,
        )
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise OfficialTaxonomySnapshotError(
            f"OFFICIAL_TAXONOMY_{name.upper()}_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _exact_date(
    name: str,
    value: object,
) -> date:
    """Validate a calendar date while rejecting datetime masquerading as date."""
    if (
        not isinstance(
            value,
            date,
        )
        or isinstance(
            value,
            datetime,
        )
    ):
        raise OfficialTaxonomySnapshotError(
            f"OFFICIAL_TAXONOMY_{name.upper()}_INVALID"
        )

    return value


def _optional_exact_date(
    name: str,
    value: object,
) -> date | None:
    """Validate an optional exact calendar date."""
    if value is None:
        return None

    return _exact_date(
        name,
        value,
    )


def _nonnegative_integer(
    name: str,
    value: object,
) -> int:
    """Validate a true nonnegative integer while rejecting bool and float."""
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
        raise OfficialTaxonomySnapshotError(
            f"OFFICIAL_TAXONOMY_{name.upper()}_INVALID"
        )

    return value


def _artifact_kind(
    value: object,
) -> OfficialTaxonomyArtifactKind:
    """Resolve an exact source-artifact kind from the closed vocabulary."""
    if isinstance(
        value,
        OfficialTaxonomyArtifactKind,
    ):
        return value

    if not isinstance(
        value,
        str,
    ):
        raise OfficialTaxonomySnapshotError(
            "OFFICIAL_TAXONOMY_ARTIFACT_KIND_INVALID"
        )

    try:
        return OfficialTaxonomyArtifactKind(
            value
        )
    except ValueError as error:
        raise OfficialTaxonomySnapshotError(
            "OFFICIAL_TAXONOMY_ARTIFACT_KIND_INVALID"
        ) from error


def _strict_mapping(
    value: object,
    *,
    expected_keys: frozenset[str],
    surface: str,
) -> Mapping[str, Any]:
    """Require one exact serialized mapping shape for strict hydration."""
    if not isinstance(
        value,
        Mapping,
    ):
        raise OfficialTaxonomySnapshotError(
            f"OFFICIAL_TAXONOMY_{surface}_INVALID"
        )

    if (
        frozenset(
            value.keys()
        )
        != expected_keys
    ):
        raise OfficialTaxonomySnapshotError(
            f"OFFICIAL_TAXONOMY_{surface}_SHAPE_INVALID"
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class OfficialTaxonomySourceArtifact:
    """Capture immutable provenance for one official taxonomy source artifact.

    This object records captured source evidence only. It performs no network
    access and creates no hierarchy, correspondence, tenant classification,
    authorization, entitlement, service-pack or financial authority.
    """

    artifact_id: str
    kind: OfficialTaxonomyArtifactKind
    source_reference: str
    media_type: str
    language_tag: str | None
    source_digest: str
    size_bytes: int
    retrieved_at: datetime
    rights_reference: str | None

    def __post_init__(
        self,
    ) -> None:
        """Validate source-artifact provenance and immutable integrity."""
        object.__setattr__(
            self,
            "artifact_id",
            _exact_text(
                "artifact_id",
                self.artifact_id,
            ),
        )

        object.__setattr__(
            self,
            "kind",
            _artifact_kind(
                self.kind
            ),
        )

        object.__setattr__(
            self,
            "source_reference",
            _exact_text(
                "source_reference",
                self.source_reference,
            ),
        )

        object.__setattr__(
            self,
            "media_type",
            _exact_text(
                "media_type",
                self.media_type,
            ),
        )

        object.__setattr__(
            self,
            "language_tag",
            _optional_exact_text(
                "language_tag",
                self.language_tag,
            ),
        )

        object.__setattr__(
            self,
            "source_digest",
            _lower_sha3_512(
                "source_digest",
                self.source_digest,
            ),
        )

        object.__setattr__(
            self,
            "size_bytes",
            _nonnegative_integer(
                "size_bytes",
                self.size_bytes,
            ),
        )

        object.__setattr__(
            self,
            "retrieved_at",
            _aware_utc(
                "retrieved_at",
                self.retrieved_at,
            ),
        )

        object.__setattr__(
            self,
            "rights_reference",
            _optional_exact_text(
                "rights_reference",
                self.rights_reference,
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """Serialize exact immutable source-artifact provenance."""
        return {
            "artifact_id": self.artifact_id,
            "kind": self.kind.value,
            "source_reference": self.source_reference,
            "media_type": self.media_type,
            "language_tag": self.language_tag,
            "source_digest": self.source_digest,
            "size_bytes": self.size_bytes,
            "retrieved_at": self.retrieved_at.isoformat(),
            "rights_reference": self.rights_reference,
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> OfficialTaxonomySourceArtifact:
        """Hydrate one exact source artifact and reject shape widening."""
        expected = frozenset(
            {
                "artifact_id",
                "kind",
                "source_reference",
                "media_type",
                "language_tag",
                "source_digest",
                "size_bytes",
                "retrieved_at",
                "rights_reference",
            }
        )

        value = _strict_mapping(
            payload,
            expected_keys=expected,
            surface="SOURCE_ARTIFACT",
        )

        try:
            retrieved_at = datetime.fromisoformat(
                value[
                    "retrieved_at"
                ]
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            raise OfficialTaxonomySnapshotError(
                "OFFICIAL_TAXONOMY_RETRIEVED_AT_INVALID"
            ) from error

        return cls(
            artifact_id=value[
                "artifact_id"
            ],
            kind=value[
                "kind"
            ],
            source_reference=value[
                "source_reference"
            ],
            media_type=value[
                "media_type"
            ],
            language_tag=value[
                "language_tag"
            ],
            source_digest=value[
                "source_digest"
            ],
            size_bytes=value[
                "size_bytes"
            ],
            retrieved_at=retrieved_at,
            rights_reference=value[
                "rights_reference"
            ],
        )


@dataclass(
    frozen=True,
    slots=True,
)
class OfficialTaxonomySnapshot:
    """Represent one immutable captured edition of an official taxonomy.

    This is platform reference truth. It captures publisher-supplied edition
    metadata and immutable source artifacts, but does not contain taxonomy
    category/hierarchy semantics, semantic correspondence, or classify tenants.

    A corrected or later edition receives a new snapshot identity and may
    supersede a prior immutable snapshot rather than rewriting history.
    """

    snapshot_id: str
    scheme_id: str
    scheme_version: str
    publisher: str
    jurisdiction: str
    publisher_status: str
    release_date: date
    effective_from: date
    effective_until: date | None
    ingested_at: datetime
    source_artifacts: tuple[
        OfficialTaxonomySourceArtifact,
        ...,
    ]
    supersedes_snapshot_id: str | None = None
    snapshot_digest: str = field(
        init=False,
        compare=True,
    )

    def __post_init__(
        self,
    ) -> None:
        """Validate immutable snapshot provenance and compute integrity evidence."""
        for field_name in (
            "snapshot_id",
            "scheme_id",
            "scheme_version",
            "publisher",
            "jurisdiction",
            "publisher_status",
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
            "release_date",
            _exact_date(
                "release_date",
                self.release_date,
            ),
        )

        object.__setattr__(
            self,
            "effective_from",
            _exact_date(
                "effective_from",
                self.effective_from,
            ),
        )

        object.__setattr__(
            self,
            "effective_until",
            _optional_exact_date(
                "effective_until",
                self.effective_until,
            ),
        )

        if (
            self.effective_until
            is not None
            and self.effective_until
            <= self.effective_from
        ):
            raise OfficialTaxonomySnapshotError(
                "OFFICIAL_TAXONOMY_EFFECTIVE_RANGE_INVALID"
            )

        object.__setattr__(
            self,
            "ingested_at",
            _aware_utc(
                "ingested_at",
                self.ingested_at,
            ),
        )

        object.__setattr__(
            self,
            "supersedes_snapshot_id",
            _optional_exact_text(
                "supersedes_snapshot_id",
                self.supersedes_snapshot_id,
            ),
        )

        if (
            self.supersedes_snapshot_id
            == self.snapshot_id
        ):
            raise OfficialTaxonomySnapshotError(
                "OFFICIAL_TAXONOMY_SELF_SUPERSESSION_FORBIDDEN"
            )

        if not isinstance(
            self.source_artifacts,
            (tuple, list),
        ):
            raise OfficialTaxonomySnapshotError(
                "OFFICIAL_TAXONOMY_SOURCE_ARTIFACTS_INVALID"
            )

        artifacts = tuple(
            self.source_artifacts
        )

        if not artifacts:
            raise OfficialTaxonomySnapshotError(
                "OFFICIAL_TAXONOMY_SOURCE_ARTIFACTS_EMPTY"
            )

        if not all(
            isinstance(
                entry,
                OfficialTaxonomySourceArtifact,
            )
            for entry in artifacts
        ):
            raise OfficialTaxonomySnapshotError(
                "OFFICIAL_TAXONOMY_SOURCE_ARTIFACTS_INVALID"
            )

        artifact_ids = tuple(
            entry.artifact_id
            for entry in artifacts
        )

        if (
            len(artifact_ids)
            != len(
                set(artifact_ids)
            )
        ):
            raise OfficialTaxonomySnapshotError(
                "OFFICIAL_TAXONOMY_SOURCE_ARTIFACT_ID_DUPLICATE"
            )

        canonical_artifacts = tuple(
            sorted(
                artifacts,
                key=lambda entry: entry.artifact_id,
            )
        )

        object.__setattr__(
            self,
            "source_artifacts",
            canonical_artifacts,
        )

        object.__setattr__(
            self,
            "snapshot_digest",
            self._compute_snapshot_digest(),
        )

    def _semantic_payload(
        self,
    ) -> dict[str, Any]:
        """Return semantic snapshot truth covered by SHA3-512 integrity."""
        return {
            "schema_version": SCHEMA_VERSION,
            "snapshot_id": self.snapshot_id,
            "scheme_id": self.scheme_id,
            "scheme_version": self.scheme_version,
            "publisher": self.publisher,
            "jurisdiction": self.jurisdiction,
            "publisher_status": self.publisher_status,
            "release_date": self.release_date.isoformat(),
            "effective_from": self.effective_from.isoformat(),
            "effective_until": (
                self.effective_until.isoformat()
                if self.effective_until is not None
                else None
            ),
            "ingested_at": self.ingested_at.isoformat(),
            "source_artifacts": [
                entry.to_dict()
                for entry in self.source_artifacts
            ],
            "supersedes_snapshot_id": (
                self.supersedes_snapshot_id
            ),
        }

    def _compute_snapshot_digest(
        self,
    ) -> str:
        """Compute deterministic lowercase SHA3-512 over snapshot truth."""
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
        """Serialize strict snapshot truth including integrity evidence."""
        return {
            **self._semantic_payload(),
            "snapshot_digest": self.snapshot_digest,
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, Any],
    ) -> OfficialTaxonomySnapshot:
        """Hydrate strict snapshot truth and reject corruption or widening."""
        expected = frozenset(
            {
                "schema_version",
                "snapshot_id",
                "scheme_id",
                "scheme_version",
                "publisher",
                "jurisdiction",
                "publisher_status",
                "release_date",
                "effective_from",
                "effective_until",
                "ingested_at",
                "source_artifacts",
                "supersedes_snapshot_id",
                "snapshot_digest",
            }
        )

        value = _strict_mapping(
            payload,
            expected_keys=expected,
            surface="SNAPSHOT",
        )

        if (
            value[
                "schema_version"
            ]
            != SCHEMA_VERSION
        ):
            raise OfficialTaxonomySnapshotError(
                "OFFICIAL_TAXONOMY_SCHEMA_VERSION_INVALID"
            )

        supplied_digest = _lower_sha3_512(
            "snapshot_digest",
            value[
                "snapshot_digest"
            ],
        )

        try:
            release_date = date.fromisoformat(
                value[
                    "release_date"
                ]
            )

            effective_from = date.fromisoformat(
                value[
                    "effective_from"
                ]
            )

            raw_effective_until = value[
                "effective_until"
            ]

            effective_until = (
                None
                if raw_effective_until
                is None
                else date.fromisoformat(
                    raw_effective_until
                )
            )

            ingested_at = datetime.fromisoformat(
                value[
                    "ingested_at"
                ]
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            raise OfficialTaxonomySnapshotError(
                "OFFICIAL_TAXONOMY_DATE_OR_TIME_INVALID"
            ) from error

        raw_artifacts = value[
            "source_artifacts"
        ]

        if not isinstance(
            raw_artifacts,
            (list, tuple),
        ):
            raise OfficialTaxonomySnapshotError(
                "OFFICIAL_TAXONOMY_SOURCE_ARTIFACTS_INVALID"
            )

        restored = cls(
            snapshot_id=value[
                "snapshot_id"
            ],
            scheme_id=value[
                "scheme_id"
            ],
            scheme_version=value[
                "scheme_version"
            ],
            publisher=value[
                "publisher"
            ],
            jurisdiction=value[
                "jurisdiction"
            ],
            publisher_status=value[
                "publisher_status"
            ],
            release_date=release_date,
            effective_from=effective_from,
            effective_until=effective_until,
            ingested_at=ingested_at,
            source_artifacts=tuple(
                OfficialTaxonomySourceArtifact.from_dict(
                    entry
                )
                for entry in raw_artifacts
            ),
            supersedes_snapshot_id=value[
                "supersedes_snapshot_id"
            ],
        )

        if (
            restored.snapshot_digest
            != supplied_digest
        ):
            raise OfficialTaxonomySnapshotError(
                "OFFICIAL_TAXONOMY_SNAPSHOT_DIGEST_MISMATCH"
            )

        return restored


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: official_taxonomy_snapshot.py
# VERSION: v1.0.0-WILSY-OFFICIAL-TAXONOMY-SNAPSHOT
# AUTHORITY BOUNDARY: immutable official-taxonomy snapshot metadata and source
# provenance only; no category hierarchy, correspondence semantics, tenant
# classification, service-pack activation, entitlement, permission, role,
# workflow, AI, billing, payment, settlement or execution authority
# TENANT POSTURE: platform reference truth; no tenant identity or tenant grant
# FAIL-CLOSED POSTURE: exact source artifacts, publisher metadata, dates,
# digests, supersession, hydration and snapshot integrity are validated;
# corrupt or widened truth is rejected
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
