# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN TEST-FIRST CERTIFICATION ARTIFACT
OFFICIAL TAXONOMY SNAPSHOT DOMAIN
===============================================================================

TITLE:
    WILSY OS Official Taxonomy Snapshot Domain Test-First Contract

VERSION:
    v1.0.2-OFFICIAL-TAXONOMY-SNAPSHOT-DOMAIN-TEST

AUTHORITY:
    Wilsy OS Core Governance

EPITOME:
    Freezes the immutable provenance envelope for one captured edition of an
    externally published official business/economic classification system.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_official_taxonomy_snapshot_domain.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering

CERTIFICATION / UPDATE DATE:
    2026-10-07

CHANGELOG:
    v1.0.2-OFFICIAL-TAXONOMY-SNAPSHOT-DOMAIN-TEST
        - Removes positional assumptions from correspondence-source evidence
          certification.
        - Requires semantic artifact identity/kind lookup so canonical ordering
          remains free to normalize equivalent source-artifact collections.
        - Preserves correspondence-source versus mapping-authority separation.
        - Preserves every provenance, integrity, typing and authority boundary
          from v1.0.1.

    v1.0.1-OFFICIAL-TAXONOMY-SNAPSHOT-DOMAIN-TEST
        - Repairs static typing of the identity-text negative certificate by
          passing the six string identity coordinates explicitly.
        - Removes heterogeneous **dict expansion that allowed Pyright to infer
          invalid string flow into date and source-artifact parameters.
        - Preserves every runtime validation, provenance, integrity and
          authority-boundary requirement from v1.0.0.
        - Adds no type ignore and weakens no static-analysis rule.

    v1.0.0-OFFICIAL-TAXONOMY-SNAPSHOT-DOMAIN-TEST
        - Initial test-first official-taxonomy snapshot contract.
        - Separates edition/source provenance from taxonomy hierarchy.
        - Separates captured correspondence artifacts from semantic mappings.
        - Freezes multi-artifact provenance, rights provenance and SHA3-512
          integrity.
        - Freezes immutable supersession rather than silent correction.
        - Excludes tenant classification, entitlement, authorization,
          service-pack activation, live-web authority and financial execution.

COMPLIANCE:
    External reference data must preserve source provenance, integrity and
    applicable rights/licensing references.

SECURITY / PRIVACY POSTURE:
    Source material is captured and digest-bound. Runtime truth never depends on
    mutable live remote content.

TENANT BOUNDARY:
    Official taxonomy snapshots are platform reference truth and must not carry
    tenant identity or tenant authority.

AUTHORITY BOUNDARY:
    Snapshot metadata and source-artifact provenance only. No category
    membership, hierarchy authority, correspondence equivalence, tenant
    classification, service activation, entitlement, permission, role or AI
    execution authority exists here.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.

FUTURE PRODUCTION PATH:
    tools/eos/saas/domain/official_taxonomy_snapshot.py
===============================================================================
"""

from __future__ import annotations

from dataclasses import fields
from datetime import date, datetime, timezone
import hashlib

import pytest

from tools.eos.saas.domain.official_taxonomy_snapshot import (
    SCHEMA_VERSION,
    VERSION,
    OfficialTaxonomyArtifactKind,
    OfficialTaxonomySourceArtifact,
    OfficialTaxonomySnapshot,
    OfficialTaxonomySnapshotError,
)


EXPECTED_VERSION = (
    "v1.0.0-WILSY-OFFICIAL-TAXONOMY-SNAPSHOT"
)

EXPECTED_SCHEMA_VERSION = (
    "wilsy.official.taxonomy.snapshot.v1"
)

NOW = datetime(
    2026,
    10,
    7,
    10,
    0,
    tzinfo=timezone.utc,
)

DIGEST_STRUCTURE = hashlib.sha3_512(
    b"official-taxonomy-structure"
).hexdigest()

DIGEST_NOTES = hashlib.sha3_512(
    b"official-taxonomy-explanatory-notes"
).hexdigest()

DIGEST_CORRESPONDENCE = hashlib.sha3_512(
    b"official-taxonomy-correspondence-source"
).hexdigest()

DIGEST_ERRATA = hashlib.sha3_512(
    b"official-taxonomy-errata-source"
).hexdigest()


def artifact(
    artifact_id: str = "ARTIFACT-STRUCTURE",
    *,
    kind: OfficialTaxonomyArtifactKind
        = OfficialTaxonomyArtifactKind.STRUCTURE,
    source_reference: str
        = "https://authority.invalid/taxonomy/structure",
    media_type: str = "text/csv",
    language_tag: str | None = "en",
    source_digest: str = DIGEST_STRUCTURE,
    size_bytes: int = 1000,
    rights_reference: str | None
        = "https://authority.invalid/terms",
) -> OfficialTaxonomySourceArtifact:
    """Build one captured official-source artifact fixture."""
    return OfficialTaxonomySourceArtifact(
        artifact_id=artifact_id,
        kind=kind,
        source_reference=source_reference,
        media_type=media_type,
        language_tag=language_tag,
        source_digest=source_digest,
        size_bytes=size_bytes,
        retrieved_at=NOW,
        rights_reference=rights_reference,
    )


def snapshot(
    *,
    snapshot_id: str = "TAXONOMY-SNAPSHOT-1",
    scheme_id: str = "ISIC",
    scheme_version: str = "REV5",
    publisher: str = "Synthetic Official Publisher",
    jurisdiction: str = "GLOBAL",
    publisher_status: str = "published",
    release_date: date = date(2026, 1, 1),
    effective_from: date = date(2026, 1, 1),
    effective_until: date | None = None,
    supersedes_snapshot_id: str | None = None,
    artifacts: tuple[
        OfficialTaxonomySourceArtifact,
        ...,
    ] | None = None,
) -> OfficialTaxonomySnapshot:
    """Build one immutable edition snapshot fixture."""
    return OfficialTaxonomySnapshot(
        snapshot_id=snapshot_id,
        scheme_id=scheme_id,
        scheme_version=scheme_version,
        publisher=publisher,
        jurisdiction=jurisdiction,
        publisher_status=publisher_status,
        release_date=release_date,
        effective_from=effective_from,
        effective_until=effective_until,
        ingested_at=NOW,
        source_artifacts=(
            artifacts
            if artifacts is not None
            else (artifact(),)
        ),
        supersedes_snapshot_id=supersedes_snapshot_id,
    )


def test_version_and_schema_are_exact() -> None:
    assert VERSION == EXPECTED_VERSION
    assert SCHEMA_VERSION == EXPECTED_SCHEMA_VERSION


def test_artifact_kind_vocabulary_is_exact() -> None:
    assert tuple(
        member.value
        for member in OfficialTaxonomyArtifactKind
    ) == (
        "structure",
        "explanatory_notes",
        "methodology",
        "release_notice",
        "errata",
        "correspondence_source",
        "other",
    )


def test_snapshot_is_platform_reference_truth_not_tenant_truth() -> None:
    names = {
        field.name
        for field in fields(
            OfficialTaxonomySnapshot
        )
    }

    assert "tenant_id" not in names
    assert "principal_id" not in names
    assert "organization_id" not in names


def test_snapshot_identity_is_scheme_edition_and_publisher_bound() -> None:
    value = snapshot()

    assert value.snapshot_id == "TAXONOMY-SNAPSHOT-1"
    assert value.scheme_id == "ISIC"
    assert value.scheme_version == "REV5"
    assert value.publisher == "Synthetic Official Publisher"
    assert value.jurisdiction == "GLOBAL"


def test_publisher_status_is_captured_source_metadata_not_wilsy_enum() -> None:
    value = snapshot(
        publisher_status="endorsed pending publication"
    )

    assert (
        value.publisher_status
        == "endorsed pending publication"
    )


@pytest.mark.parametrize(
    "field_name",
    (
        "snapshot_id",
        "scheme_id",
        "scheme_version",
        "publisher",
        "jurisdiction",
        "publisher_status",
    ),
)
def test_snapshot_identity_text_rejects_blank_or_padded_values(
    field_name: str,
) -> None:
    """Reject malformed identity text without ambiguous kwargs typing."""
    base = {
        "snapshot_id": "TAXONOMY-SNAPSHOT-1",
        "scheme_id": "ISIC",
        "scheme_version": "REV5",
        "publisher": "Publisher",
        "jurisdiction": "GLOBAL",
        "publisher_status": "published",
    }

    assert field_name in base

    for invalid in (
        "",
        " ",
        " padded",
        "padded ",
    ):
        current = dict(base)
        current[field_name] = invalid

        with pytest.raises(
            OfficialTaxonomySnapshotError
        ):
            snapshot(
                snapshot_id=current["snapshot_id"],
                scheme_id=current["scheme_id"],
                scheme_version=current["scheme_version"],
                publisher=current["publisher"],
                jurisdiction=current["jurisdiction"],
                publisher_status=current["publisher_status"],
            )


def test_snapshot_supports_multiple_official_source_artifacts() -> None:
    value = snapshot(
        artifacts=(
            artifact(),
            artifact(
                "ARTIFACT-NOTES",
                kind=OfficialTaxonomyArtifactKind.EXPLANATORY_NOTES,
                source_reference="https://authority.invalid/notes",
                media_type="application/pdf",
                source_digest=DIGEST_NOTES,
                size_bytes=2000,
            ),
            artifact(
                "ARTIFACT-ERRATA",
                kind=OfficialTaxonomyArtifactKind.ERRATA,
                source_reference="https://authority.invalid/errata",
                media_type="text/html",
                source_digest=DIGEST_ERRATA,
                size_bytes=300,
            ),
        )
    )

    assert len(value.source_artifacts) == 3


def test_captured_correspondence_file_is_not_semantic_correspondence_authority(
) -> None:
    value = snapshot(
        artifacts=(
            artifact(),
            artifact(
                "ARTIFACT-CORRESPONDENCE",
                kind=OfficialTaxonomyArtifactKind.CORRESPONDENCE_SOURCE,
                source_reference="https://authority.invalid/correspondence",
                source_digest=DIGEST_CORRESPONDENCE,
                size_bytes=500,
            ),
        )
    )

    correspondence = next(
        entry
        for entry in value.source_artifacts
        if entry.artifact_id
        == "ARTIFACT-CORRESPONDENCE"
    )

    assert (
        correspondence.kind
        is OfficialTaxonomyArtifactKind.CORRESPONDENCE_SOURCE
    )

    assert {
        entry.artifact_id
        for entry in value.source_artifacts
    } == {
        "ARTIFACT-STRUCTURE",
        "ARTIFACT-CORRESPONDENCE",
    }

    snapshot_fields = {
        field.name
        for field in fields(
            OfficialTaxonomySnapshot
        )
    }

    assert "source_code" not in snapshot_fields
    assert "target_code" not in snapshot_fields
    assert "mapping_type" not in snapshot_fields
    assert "equivalent" not in snapshot_fields


def test_source_artifact_requires_lowercase_sha3_512_digest() -> None:
    for invalid in (
        "",
        "a" * 127,
        "a" * 129,
        "A" * 128,
        "g" * 128,
    ):
        with pytest.raises(
            OfficialTaxonomySnapshotError
        ):
            artifact(
                source_digest=invalid
            )


def test_source_artifact_size_is_nonnegative_integer_not_bool() -> None:
    assert artifact(size_bytes=0).size_bytes == 0

    for invalid in (
        -1,
        10.5,
        True,
        False,
    ):
        with pytest.raises(
            OfficialTaxonomySnapshotError
        ):
            artifact(
                size_bytes=invalid  # type: ignore[arg-type]
            )


def test_source_artifact_requires_aware_retrieval_time() -> None:
    with pytest.raises(
        OfficialTaxonomySnapshotError
    ):
        OfficialTaxonomySourceArtifact(
            artifact_id="A",
            kind=OfficialTaxonomyArtifactKind.STRUCTURE,
            source_reference="source",
            media_type="text/plain",
            language_tag=None,
            source_digest=DIGEST_STRUCTURE,
            size_bytes=1,
            retrieved_at=datetime(
                2026,
                1,
                1,
            ),
            rights_reference=None,
        )


def test_source_artifact_preserves_optional_language_and_rights_provenance(
) -> None:
    value = artifact(
        language_tag="fr",
        rights_reference="https://authority.invalid/licence",
    )

    assert value.language_tag == "fr"
    assert (
        value.rights_reference
        == "https://authority.invalid/licence"
    )


def test_source_artifact_identity_must_be_unique_within_snapshot() -> None:
    first = artifact()

    with pytest.raises(
        OfficialTaxonomySnapshotError
    ):
        snapshot(
            artifacts=(
                first,
                first,
            )
        )


def test_snapshot_requires_at_least_one_source_artifact() -> None:
    with pytest.raises(
        OfficialTaxonomySnapshotError
    ):
        snapshot(
            artifacts=(),
        )


def test_effective_until_must_be_after_effective_from() -> None:
    with pytest.raises(
        OfficialTaxonomySnapshotError
    ):
        snapshot(
            effective_from=date(
                2026,
                1,
                1,
            ),
            effective_until=date(
                2026,
                1,
                1,
            ),
        )

    with pytest.raises(
        OfficialTaxonomySnapshotError
    ):
        snapshot(
            effective_from=date(
                2026,
                1,
                2,
            ),
            effective_until=date(
                2026,
                1,
                1,
            ),
        )


def test_release_date_and_effective_date_remain_distinct() -> None:
    value = snapshot(
        release_date=date(
            2025,
            12,
            1,
        ),
        effective_from=date(
            2026,
            1,
            1,
        ),
    )

    assert value.release_date != value.effective_from


def test_initial_snapshot_has_no_superseded_identity() -> None:
    value = snapshot()

    assert value.supersedes_snapshot_id is None


def test_corrected_snapshot_uses_new_identity_and_supersession() -> None:
    corrected = snapshot(
        snapshot_id="TAXONOMY-SNAPSHOT-2",
        supersedes_snapshot_id="TAXONOMY-SNAPSHOT-1",
        artifacts=(
            artifact(),
            artifact(
                "ARTIFACT-ERRATA",
                kind=OfficialTaxonomyArtifactKind.ERRATA,
                source_reference="https://authority.invalid/errata",
                source_digest=DIGEST_ERRATA,
                size_bytes=100,
            ),
        ),
    )

    assert (
        corrected.supersedes_snapshot_id
        == "TAXONOMY-SNAPSHOT-1"
    )


def test_snapshot_cannot_supersede_itself() -> None:
    with pytest.raises(
        OfficialTaxonomySnapshotError
    ):
        snapshot(
            snapshot_id="TAXONOMY-SNAPSHOT-1",
            supersedes_snapshot_id="TAXONOMY-SNAPSHOT-1",
        )


def test_snapshot_fingerprint_is_lowercase_sha3_512() -> None:
    value = snapshot()

    assert len(value.snapshot_digest) == 128
    assert (
        value.snapshot_digest
        == value.snapshot_digest.lower()
    )
    assert all(
        character in "0123456789abcdef"
        for character in value.snapshot_digest
    )


def test_artifact_digest_change_changes_snapshot_digest() -> None:
    original = snapshot()

    changed = snapshot(
        artifacts=(
            artifact(
                source_digest=DIGEST_NOTES,
            ),
        )
    )

    assert (
        original.snapshot_digest
        != changed.snapshot_digest
    )


def test_rights_reference_change_changes_snapshot_digest() -> None:
    original = snapshot()

    changed = snapshot(
        artifacts=(
            artifact(
                rights_reference=(
                    "https://authority.invalid/new-terms"
                )
            ),
        )
    )

    assert (
        original.snapshot_digest
        != changed.snapshot_digest
    )


def test_strict_round_trip_preserves_snapshot_truth() -> None:
    original = snapshot(
        artifacts=(
            artifact(),
            artifact(
                "ARTIFACT-NOTES",
                kind=OfficialTaxonomyArtifactKind.EXPLANATORY_NOTES,
                source_reference="https://authority.invalid/notes",
                media_type="application/pdf",
                source_digest=DIGEST_NOTES,
                size_bytes=2000,
            ),
        )
    )

    restored = OfficialTaxonomySnapshot.from_dict(
        original.to_dict()
    )

    assert restored == original
    assert (
        restored.snapshot_digest
        == original.snapshot_digest
    )


def test_hydration_rejects_missing_extra_and_corrupt_truth() -> None:
    payload = snapshot().to_dict()

    missing = dict(payload)
    missing.pop("publisher")

    with pytest.raises(
        OfficialTaxonomySnapshotError
    ):
        OfficialTaxonomySnapshot.from_dict(
            missing
        )

    extra = dict(payload)
    extra["surprise"] = True

    with pytest.raises(
        OfficialTaxonomySnapshotError
    ):
        OfficialTaxonomySnapshot.from_dict(
            extra
        )

    corrupt = dict(payload)
    corrupt["snapshot_digest"] = "0" * 128

    with pytest.raises(
        OfficialTaxonomySnapshotError
    ):
        OfficialTaxonomySnapshot.from_dict(
            corrupt
        )


def test_snapshot_contains_no_category_or_hierarchy_authority() -> None:
    forbidden = {
        "category_id",
        "category_code",
        "parent_id",
        "parent_code",
        "children",
        "child_ids",
        "hierarchy_level",
        "inclusions",
        "exclusions",
        "explanatory_notes",
    }

    names = {
        field.name
        for field in fields(
            OfficialTaxonomySnapshot
        )
    }

    assert forbidden.isdisjoint(
        names
    )


def test_snapshot_contains_no_tenant_commercial_or_execution_authority(
) -> None:
    forbidden = {
        "tenant_id",
        "principal_id",
        "business_activity_id",
        "classification_id",
        "plan",
        "subscription",
        "entitlement",
        "permission",
        "authorization",
        "business_role",
        "service_pack",
        "dashboard",
        "workflow",
        "ai_authority",
        "payment",
        "billing",
        "settlement",
        "financial_execution",
        "kennel_command",
    }

    snapshot_fields = {
        field.name
        for field in fields(
            OfficialTaxonomySnapshot
        )
    }

    artifact_fields = {
        field.name
        for field in fields(
            OfficialTaxonomySourceArtifact
        )
    }

    assert forbidden.isdisjoint(
        snapshot_fields | artifact_fields
    )


def test_domain_exposes_no_network_or_activation_methods() -> None:
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
        OfficialTaxonomySnapshot,
        OfficialTaxonomySourceArtifact,
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
# ARTIFACT: test_official_taxonomy_snapshot_domain.py
# VERSION: v1.0.2-OFFICIAL-TAXONOMY-SNAPSHOT-DOMAIN-TEST
# AUTHORITY BOUNDARY: official snapshot metadata/source provenance only; no
# hierarchy, correspondence semantics, tenant classification, entitlement,
# permission, service activation, AI execution or financial authority
# TENANT POSTURE: platform reference truth; no tenant identity or tenant grant
# FAIL-CLOSED POSTURE: exact source artifacts, dates, digests, hydration and
# immutable supersession are validated; corrupt fingerprints are rejected
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
