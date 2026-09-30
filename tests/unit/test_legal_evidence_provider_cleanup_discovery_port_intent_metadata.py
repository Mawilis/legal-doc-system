"""Direct certificate for C4D2R1 completed-object intent metadata evidence."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectIntentMetadataState,
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceProviderCleanupDiscoveryError,
)


AT = datetime(
    2026,
    9,
    30,
    18,
    30,
    45,
    123456,
    tzinfo=timezone.utc,
)

FP = "a" * 128


def _observation(
    **overrides: object,
) -> LegalEvidenceCompletedObjectObservation:
    values: dict[str, object] = {
        "tenant_id": "tenant-c4d2r1",
        "provider_name": "aws_s3",
        "storage_reference": "opaque/provider/object",
        "object_version_reference": "version-c4d2r1",
        "provider_integrity_reference": "etag-c4d2r1",
        "content_length": 4096,
        "last_modified_at": AT - timedelta(seconds=1),
        "observed_at": AT,
    }
    values.update(overrides)
    return LegalEvidenceCompletedObjectObservation(**values)  # type: ignore[arg-type]


def test_existing_constructor_defaults_to_metadata_not_observed() -> None:
    value = _observation()

    assert (
        value.write_intent_metadata_state
        is LegalEvidenceCompletedObjectIntentMetadataState.NOT_OBSERVED
    )
    assert value.write_intent_fingerprint is None


def test_explicit_absent_metadata_preserves_completed_object_observation() -> None:
    value = _observation(
        write_intent_metadata_state=(
            LegalEvidenceCompletedObjectIntentMetadataState.ABSENT
        ),
    )

    assert (
        value.write_intent_metadata_state
        is LegalEvidenceCompletedObjectIntentMetadataState.ABSENT
    )
    assert value.write_intent_fingerprint is None


def test_present_metadata_requires_exact_sha3_512() -> None:
    value = _observation(
        write_intent_metadata_state=(
            LegalEvidenceCompletedObjectIntentMetadataState.PRESENT
        ),
        write_intent_fingerprint=FP,
    )

    assert (
        value.write_intent_metadata_state
        is LegalEvidenceCompletedObjectIntentMetadataState.PRESENT
    )
    assert value.write_intent_fingerprint == FP


@pytest.mark.parametrize(
    "fingerprint",
    [
        None,
        "",
        "a" * 127,
        "a" * 129,
        "A" * 128,
        "g" * 128,
    ],
)
def test_present_metadata_rejects_missing_or_malformed_fingerprint(
    fingerprint: str | None,
) -> None:
    with pytest.raises(
        LegalEvidenceProviderCleanupDiscoveryError,
        match="INTENT_FINGERPRINT_INVALID",
    ):
        _observation(
            write_intent_metadata_state=(
                LegalEvidenceCompletedObjectIntentMetadataState.PRESENT
            ),
            write_intent_fingerprint=fingerprint,
        )


@pytest.mark.parametrize(
    "state",
    [
        LegalEvidenceCompletedObjectIntentMetadataState.NOT_OBSERVED,
        LegalEvidenceCompletedObjectIntentMetadataState.ABSENT,
    ],
)
def test_non_present_state_rejects_fingerprint(
    state: LegalEvidenceCompletedObjectIntentMetadataState,
) -> None:
    with pytest.raises(
        LegalEvidenceProviderCleanupDiscoveryError,
        match="INTENT_METADATA_STATE_MISMATCH",
    ):
        _observation(
            write_intent_metadata_state=state,
            write_intent_fingerprint=FP,
        )


def test_raw_string_state_rejects_even_when_value_matches_enum() -> None:
    with pytest.raises(
        LegalEvidenceProviderCleanupDiscoveryError,
        match="INTENT_METADATA_STATE_INVALID",
    ):
        _observation(
            write_intent_metadata_state="PRESENT",
            write_intent_fingerprint=FP,
        )


def test_metadata_state_adds_no_orphan_or_delete_authority() -> None:
    value = _observation(
        write_intent_metadata_state=(
            LegalEvidenceCompletedObjectIntentMetadataState.PRESENT
        ),
        write_intent_fingerprint=FP,
    )

    assert not hasattr(value, "orphan_proven")
    assert not hasattr(value, "deletion_authorized")
    assert not hasattr(value, "provider_delete_authorized")


# ARTIFACT: test_legal_evidence_provider_cleanup_discovery_port_intent_metadata.py
# VERSION: v1.0.0-L10A2R-C4D2R1-PROVIDER-INTENT-METADATA-CONTRACT-CERT
# AUTHORITY BOUNDARY: completed-object provider metadata observation only
# TENANT POSTURE: exact tenant-bound observation contract
# COVERAGE POSTURE: NOT_OBSERVED and ABSENT never imply orphan status
# DELETION POSTURE: no orphan proof or deletion authority
# END OF WILSY OS SOVEREIGN ARTIFACT
