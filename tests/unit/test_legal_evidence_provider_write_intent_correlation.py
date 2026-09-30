"""Direct certificate for C4D5D2 provider/write-intent correlation evidence.

VERSION: v1.0.0-L10A2R-C4D5D2-PROVIDER-WRITE-INTENT-CORRELATION-CERT
CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.domain.legal_evidence_provider_write_intent_correlation import (
    LegalEvidenceProviderWriteIntentCorrelationError,
    LegalEvidenceProviderWriteIntentCorrelationState,
    correlate_legal_evidence_provider_write_intent,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryWriteIntent,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectIntentMetadataState,
    LegalEvidenceCompletedObjectObservation,
)


AT = datetime(
    2026,
    9,
    30,
    21,
    40,
    tzinfo=timezone.utc,
)


def _intent(
    *,
    tenant_id: str = "tenant-c4d5d2",
    document_id: str = "document-c4d5d2",
) -> LegalEvidenceBinaryWriteIntent:
    return LegalEvidenceBinaryWriteIntent(
        tenant_id=tenant_id,
        case_matter_id="matter-c4d5d2",
        document_id=document_id,
        ingestion_reference="ingestion-c4d5d2",
        media_type="application/pdf",
        original_filename="evidence.pdf",
        admitted_max_content_length=4096,
    )


def _observation(
    state: LegalEvidenceCompletedObjectIntentMetadataState,
    fingerprint: str | None,
) -> LegalEvidenceCompletedObjectObservation:
    return LegalEvidenceCompletedObjectObservation(
        tenant_id="tenant-c4d5d2",
        provider_name="aws_s3",
        storage_reference=(
            "legal-evidence/c4d5d2/object"
        ),
        object_version_reference="version-c4d5d2",
        provider_integrity_reference='"etag-c4d5d2"',
        content_length=100,
        last_modified_at=AT,
        observed_at=AT,
        write_intent_metadata_state=state,
        write_intent_fingerprint=fingerprint,
    )


def test_not_observed_is_explicit_non_authorizing_evidence() -> None:
    result = correlate_legal_evidence_provider_write_intent(
        observation=_observation(
            LegalEvidenceCompletedObjectIntentMetadataState.NOT_OBSERVED,
            None,
        ),
        registry_lookup_performed=False,
    )

    assert result.correlation_state is (
        LegalEvidenceProviderWriteIntentCorrelationState
        .METADATA_NOT_OBSERVED
    )
    assert result.provider_write_intent_fingerprint is None
    assert result.orphan_proven is False
    assert result.provider_delete_authorized is False


def test_absent_is_explicit_non_authorizing_evidence() -> None:
    result = correlate_legal_evidence_provider_write_intent(
        observation=_observation(
            LegalEvidenceCompletedObjectIntentMetadataState.ABSENT,
            None,
        ),
        registry_lookup_performed=False,
    )

    assert result.correlation_state is (
        LegalEvidenceProviderWriteIntentCorrelationState
        .METADATA_ABSENT
    )
    assert result.orphan_proven is False
    assert result.provider_delete_authorized is False


@pytest.mark.parametrize(
    "state",
    [
        LegalEvidenceCompletedObjectIntentMetadataState.NOT_OBSERVED,
        LegalEvidenceCompletedObjectIntentMetadataState.ABSENT,
    ],
)
def test_non_present_metadata_rejects_registry_evidence(
    state,
) -> None:
    with pytest.raises(
        LegalEvidenceProviderWriteIntentCorrelationError,
        match="L10A2R_C4D5D2_NON_PRESENT_REGISTRY_EVIDENCE_FORBIDDEN",
    ):
        correlate_legal_evidence_provider_write_intent(
            observation=_observation(
                state,
                None,
            ),
            registry_lookup_performed=True,
        )


def test_present_requires_completed_registry_lookup() -> None:
    intent = _intent()

    with pytest.raises(
        LegalEvidenceProviderWriteIntentCorrelationError,
        match="L10A2R_C4D5D2_PRESENT_REQUIRES_REGISTRY_LOOKUP",
    ):
        correlate_legal_evidence_provider_write_intent(
            observation=_observation(
                LegalEvidenceCompletedObjectIntentMetadataState.PRESENT,
                intent.fingerprint,
            ),
            registry_lookup_performed=False,
        )


def test_present_registry_not_found_is_not_orphan_proof() -> None:
    intent = _intent()

    result = correlate_legal_evidence_provider_write_intent(
        observation=_observation(
            LegalEvidenceCompletedObjectIntentMetadataState.PRESENT,
            intent.fingerprint,
        ),
        registry_lookup_performed=True,
    )

    assert result.correlation_state is (
        LegalEvidenceProviderWriteIntentCorrelationState
        .PRESENT_REGISTRY_NOT_FOUND
    )
    assert result.provider_write_intent_fingerprint == intent.fingerprint
    assert result.registered_intent_fingerprint is None
    assert result.orphan_proven is False
    assert result.provider_delete_authorized is False


def test_present_exact_registration_match_is_non_authorizing() -> None:
    intent = _intent()
    record_fingerprint = "b" * 128

    result = correlate_legal_evidence_provider_write_intent(
        observation=_observation(
            LegalEvidenceCompletedObjectIntentMetadataState.PRESENT,
            intent.fingerprint,
        ),
        registry_lookup_performed=True,
        registered_intent=intent,
        registration_record_fingerprint=record_fingerprint,
        registered_at=AT,
    )

    assert result.correlation_state is (
        LegalEvidenceProviderWriteIntentCorrelationState
        .PRESENT_REGISTRY_MATCH
    )
    assert result.provider_write_intent_fingerprint == intent.fingerprint
    assert result.registered_intent_fingerprint == intent.fingerprint
    assert result.registration_record_fingerprint == record_fingerprint
    assert result.registered_at == AT
    assert result.orphan_proven is False
    assert result.provider_delete_authorized is False


def test_cross_tenant_registered_intent_fails_closed() -> None:
    provider_intent = _intent()
    other_tenant = _intent(
        tenant_id="tenant-other",
    )

    with pytest.raises(
        LegalEvidenceProviderWriteIntentCorrelationError,
        match="L10A2R_C4D5D2_REGISTERED_INTENT_MISMATCH",
    ):
        correlate_legal_evidence_provider_write_intent(
            observation=_observation(
                LegalEvidenceCompletedObjectIntentMetadataState.PRESENT,
                provider_intent.fingerprint,
            ),
            registry_lookup_performed=True,
            registered_intent=other_tenant,
            registration_record_fingerprint="c" * 128,
            registered_at=AT,
        )


def test_wrong_registered_intent_fingerprint_fails_closed() -> None:
    provider_intent = _intent()
    different_intent = _intent(
        document_id="document-different",
    )

    with pytest.raises(
        LegalEvidenceProviderWriteIntentCorrelationError,
        match="L10A2R_C4D5D2_REGISTERED_INTENT_MISMATCH",
    ):
        correlate_legal_evidence_provider_write_intent(
            observation=_observation(
                LegalEvidenceCompletedObjectIntentMetadataState.PRESENT,
                provider_intent.fingerprint,
            ),
            registry_lookup_performed=True,
            registered_intent=different_intent,
            registration_record_fingerprint="d" * 128,
            registered_at=AT,
        )


@pytest.mark.parametrize(
    "record_fingerprint",
    [
        "",
        "a" * 127,
        "a" * 129,
        "A" * 128,
        "g" * 128,
    ],
)
def test_match_requires_exact_record_sha3_512(
    record_fingerprint: str,
) -> None:
    intent = _intent()

    with pytest.raises(
        LegalEvidenceProviderWriteIntentCorrelationError,
        match="L10A2R_C4D5D2_REGISTRATION_RECORD_FINGERPRINT_INVALID",
    ):
        correlate_legal_evidence_provider_write_intent(
            observation=_observation(
                LegalEvidenceCompletedObjectIntentMetadataState.PRESENT,
                intent.fingerprint,
            ),
            registry_lookup_performed=True,
            registered_intent=intent,
            registration_record_fingerprint=record_fingerprint,
            registered_at=AT,
        )


def test_match_requires_utc_aware_registration_time() -> None:
    intent = _intent()

    with pytest.raises(
        LegalEvidenceProviderWriteIntentCorrelationError,
        match="L10A2R_C4D5D2_REGISTERED_AT_INVALID",
    ):
        correlate_legal_evidence_provider_write_intent(
            observation=_observation(
                LegalEvidenceCompletedObjectIntentMetadataState.PRESENT,
                intent.fingerprint,
            ),
            registry_lookup_performed=True,
            registered_intent=intent,
            registration_record_fingerprint="e" * 128,
            registered_at=datetime(
                2026,
                9,
                30,
                21,
                40,
            ),
        )


@pytest.mark.parametrize(
    ("record_fingerprint", "registered_at"),
    [
        (None, AT),
        ("f" * 128, None),
        (None, None),
    ],
)
def test_match_requires_complete_registration_evidence(
    record_fingerprint,
    registered_at,
) -> None:
    intent = _intent()

    with pytest.raises(
        LegalEvidenceProviderWriteIntentCorrelationError,
        match="L10A2R_C4D5D2_MATCH_REGISTRATION_EVIDENCE_REQUIRED",
    ):
        correlate_legal_evidence_provider_write_intent(
            observation=_observation(
                LegalEvidenceCompletedObjectIntentMetadataState.PRESENT,
                intent.fingerprint,
            ),
            registry_lookup_performed=True,
            registered_intent=intent,
            registration_record_fingerprint=record_fingerprint,
            registered_at=registered_at,
        )


def test_registry_not_found_rejects_fabricated_registration_fields() -> None:
    intent = _intent()

    with pytest.raises(
        LegalEvidenceProviderWriteIntentCorrelationError,
        match="L10A2R_C4D5D2_NOT_FOUND_REGISTRATION_EVIDENCE_FORBIDDEN",
    ):
        correlate_legal_evidence_provider_write_intent(
            observation=_observation(
                LegalEvidenceCompletedObjectIntentMetadataState.PRESENT,
                intent.fingerprint,
            ),
            registry_lookup_performed=True,
            registration_record_fingerprint="f" * 128,
            registered_at=AT,
        )


def test_correlation_evidence_is_immutable_and_deterministic() -> None:
    intent = _intent()

    first = correlate_legal_evidence_provider_write_intent(
        observation=_observation(
            LegalEvidenceCompletedObjectIntentMetadataState.PRESENT,
            intent.fingerprint,
        ),
        registry_lookup_performed=True,
    )
    second = correlate_legal_evidence_provider_write_intent(
        observation=_observation(
            LegalEvidenceCompletedObjectIntentMetadataState.PRESENT,
            intent.fingerprint,
        ),
        registry_lookup_performed=True,
    )

    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 128

    with pytest.raises(FrozenInstanceError):
        first.tenant_id = "tenant-mutated"  # type: ignore[misc]


def test_public_surface_contains_no_later_authority_commands() -> None:
    module = __import__(
        "tools.eos.legal_operations.domain."
        "legal_evidence_provider_write_intent_correlation",
        fromlist=["*"],
    )

    public = {
        name.lower()
        for name in dir(module)
        if not name.startswith("_")
    }

    forbidden = {
        "delete",
        "delete_object",
        "abort",
        "prove_orphan",
        "authorize_delete",
        "authorize_deletion",
        "payment",
        "settlement",
    }

    assert public.isdisjoint(
        forbidden
    )


# ARTIFACT: test_legal_evidence_provider_write_intent_correlation.py
# VERSION: v1.0.0-L10A2R-C4D5D2-PROVIDER-WRITE-INTENT-CORRELATION-CERT
# AUTHORITY BOUNDARY: direct pure correlation evidence only
# REGISTRY POSTURE: no Mongo or durable registry IO
# COVERAGE POSTURE: not-found is evidence of lookup result only, not orphan proof
# ORPHAN POSTURE: no orphan proof
# DELETION POSTURE: no deletion authorization
# END OF WILSY OS SOVEREIGN ARTIFACT
