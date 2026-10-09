"""Direct certificate for C4D6B provider coverage enumeration contract.

TITLE: Legal Evidence Provider Coverage Enumeration Contract Certificate
VERSION: v1.0.0-L10A2R-C4D6B-PROVIDER-COVERAGE-ENUMERATION-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
PURPOSE:
    Certify immutable page identity, exact scope/type correlation, deterministic
    SHA3-512 evidence, opaque continuation handling and zero orphan/deletion
    authority for the sibling coverage-enumeration contract.
CERTIFICATION / UPDATE DATE: 2026-10-01
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectIntentMetadataState,
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceIncompleteWriteSessionObservation,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_enumeration_port import (
    VERSION,
    LegalEvidenceProviderCoverageEnumerationError,
    LegalEvidenceProviderCoverageEnumerationPort,
    LegalEvidenceProviderEnumerationKind,
    LegalEvidenceProviderEnumerationPage,
)


AT = datetime(
    2026,
    10,
    1,
    0,
    0,
    tzinfo=timezone.utc,
)

SCOPE = "a" * 128


def _incomplete(
    *,
    tenant: str = "tenant-c4d6b",
    provider: str = "aws_s3",
) -> LegalEvidenceIncompleteWriteSessionObservation:
    return LegalEvidenceIncompleteWriteSessionObservation(
        tenant_id=tenant,
        provider_name=provider,
        storage_reference="legal-evidence/c4d6b/incomplete",
        write_session_reference="upload-c4d6b",
        initiated_at=AT,
        observed_at=AT,
    )


def _completed(
    *,
    tenant: str = "tenant-c4d6b",
    provider: str = "aws_s3",
) -> LegalEvidenceCompletedObjectObservation:
    return LegalEvidenceCompletedObjectObservation(
        tenant_id=tenant,
        provider_name=provider,
        storage_reference="legal-evidence/c4d6b/completed",
        object_version_reference="version-c4d6b",
        provider_integrity_reference="etag-c4d6b",
        content_length=17,
        last_modified_at=AT,
        observed_at=AT,
        write_intent_metadata_state=(
            LegalEvidenceCompletedObjectIntentMetadataState
            .PRESENT
        ),
        write_intent_fingerprint="b" * 128,
    )


def _page(
    *,
    observations=(),
    kind=(
        LegalEvidenceProviderEnumerationKind
        .COMPLETED_OBJECT_VERSIONS
    ),
    continuation=None,
) -> LegalEvidenceProviderEnumerationPage:
    return LegalEvidenceProviderEnumerationPage(
        tenant_id="tenant-c4d6b",
        tenant_scope_fingerprint=SCOPE,
        provider_name="aws_s3",
        enumeration_kind=kind,
        observed_at=AT,
        observations=observations,
        next_page_reference=continuation,
    )


def test_completed_page_is_immutable_and_deterministic() -> None:
    first = _page(
        observations=(
            _completed(),
        ),
    )
    second = _page(
        observations=(
            _completed(),
        ),
    )

    assert first == second
    assert len(first.fingerprint) == 128
    assert first.fingerprint == second.fingerprint
    assert first.enumeration_page_version == VERSION

    with pytest.raises(FrozenInstanceError):
        first.provider_name = "other"  # type: ignore[misc]


def test_incomplete_page_accepts_only_incomplete_observations() -> None:
    page = _page(
        observations=(
            _incomplete(),
        ),
        kind=(
            LegalEvidenceProviderEnumerationKind
            .INCOMPLETE_WRITE_SESSIONS
        ),
    )

    assert page.observations == (
        _incomplete(),
    )


@pytest.mark.parametrize(
    ("kind", "observations"),
    (
        (
            LegalEvidenceProviderEnumerationKind
            .INCOMPLETE_WRITE_SESSIONS,
            (
                _completed(),
            ),
        ),
        (
            LegalEvidenceProviderEnumerationKind
            .COMPLETED_OBJECT_VERSIONS,
            (
                _incomplete(),
            ),
        ),
    ),
)
def test_observation_kind_mismatch_rejects(
    kind: LegalEvidenceProviderEnumerationKind,
    observations: tuple[object, ...],
) -> None:
    with pytest.raises(
        LegalEvidenceProviderCoverageEnumerationError,
        match="L10A2R_C4D6B_OBSERVATION_KIND_MISMATCH",
    ):
        _page(
            observations=observations,
            kind=kind,
        )


@pytest.mark.parametrize(
    "observation",
    (
        _completed(
            tenant="tenant-other",
        ),
        _completed(
            provider="provider-other",
        ),
    ),
)
def test_observation_scope_mismatch_rejects(
    observation: LegalEvidenceCompletedObjectObservation,
) -> None:
    with pytest.raises(
        LegalEvidenceProviderCoverageEnumerationError,
        match="L10A2R_C4D6B_OBSERVATION_SCOPE_MISMATCH",
    ):
        _page(
            observations=(
                observation,
            ),
        )


def test_opaque_continuation_participates_in_fingerprint() -> None:
    first = _page(
        observations=(
            _completed(),
        ),
        continuation="opaque-next-page-a",
    )
    second = _page(
        observations=(
            _completed(),
        ),
        continuation="opaque-next-page-b",
    )

    assert first.fingerprint != second.fingerprint


def test_empty_page_is_valid_but_does_not_claim_completeness() -> None:
    page = _page()

    assert page.observations == ()
    assert page.next_page_reference is None

    forbidden = {
        "complete",
        "complete_coverage",
        "coverage_complete",
        "orphan_proven",
        "provider_delete_authorized",
        "abort_authorized",
        "retention_satisfied",
        "legal_hold_released",
        "disowned",
    }

    assert forbidden.isdisjoint(
        page.__dataclass_fields__
    )


def test_fingerprint_tampering_rejects() -> None:
    page = _page(
        observations=(
            _completed(),
        ),
    )

    with pytest.raises(
        LegalEvidenceProviderCoverageEnumerationError,
        match="L10A2R_C4D6B_FINGERPRINT_MISMATCH",
    ):
        LegalEvidenceProviderEnumerationPage(
            tenant_id=page.tenant_id,
            tenant_scope_fingerprint=(
                page.tenant_scope_fingerprint
            ),
            provider_name=page.provider_name,
            enumeration_kind=page.enumeration_kind,
            observed_at=page.observed_at,
            observations=page.observations,
            next_page_reference=page.next_page_reference,
            fingerprint="f" * 128,
        )


def test_public_contract_is_protocol_only_and_non_authorizing() -> None:
    assert getattr(
        LegalEvidenceProviderCoverageEnumerationPort,
        "_is_protocol",
        False,
    )

    forbidden = {
        "delete",
        "abort",
        "orphan",
        "authorize",
        "retention",
        "hold",
    }

    public = {
        name
        for name in dir(
            LegalEvidenceProviderCoverageEnumerationPort
        )
        if not name.startswith("_")
    }

    assert all(
        all(
            token not in name.casefold()
            for token in forbidden
        )
        for name in public
    )


# ARTIFACT: test_legal_evidence_provider_coverage_enumeration_port.py
# VERSION: v1.0.0-L10A2R-C4D6B-PROVIDER-COVERAGE-ENUMERATION-CERT
# AUTHORITY BOUNDARY: C4D6B non-authorizing page contract certificate only
# COVERAGE POSTURE: no exhaustive-coverage attestation is certified here
# ORPHAN POSTURE: no orphan proof
# DELETION POSTURE: no provider deletion or authorization
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
