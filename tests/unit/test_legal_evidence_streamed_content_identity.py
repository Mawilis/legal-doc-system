"""Certificate for stream-derived canonical Legal Evidence content identity.

TITLE: Legal Evidence Stream-Derived Content Identity Certificate
VERSION: v1.0.0-L10A2R-C3A-STREAM-DERIVED-CONTENT-IDENTITY-CERT
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Freeze the pure-domain seam that creates canonical LegalEvidenceContent
    metadata from WILSY-observed stream length and SHA3-512 identity without
    requiring whole-object byte materialization.

EPITOME:
    WILSY-OBSERVED STREAM LENGTH
    + WILSY-OBSERVED SHA3-512
    -> CANONICAL LEGAL EVIDENCE CONTENT IDENTITY
    != RAW-BYTE STORAGE
    != CAPACITY ADMISSION
    != PROVIDER SUCCESS
    != METADATA COMMIT
    != AUTHORIZED AVAILABILITY

LEGACY COMPATIBILITY:
    The existing whole-byte register_legal_evidence_content path retains its
    existing bounded byte-registration behavior. The streamed identity seam is
    an additional path for already-observed stream evidence.

AUTHORITY:
    This pure domain does not decide whether a caller is entitled to supply the
    observations. C3 orchestration must obtain them only from the certified
    StreamingSHA3512/provider-correlation sequence.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import inspect

import pytest

from tools.eos.legal_operations.domain.legal_evidence_content import (
    MAX_CONTENT_BYTES,
    LegalEvidenceContent,
    LegalEvidenceContentError,
    register_legal_evidence_content,
    register_observed_legal_evidence_content,
)


AT = datetime(
    2026,
    9,
    30,
    10,
    45,
    0,
    123456,
    tzinfo=timezone.utc,
)

SOURCE_FP = hashlib.sha3_512(
    b"c3a-source-evidence"
).hexdigest()

BODY = b"canonical streamed evidence identity"
BODY_FP = hashlib.sha3_512(
    BODY
).hexdigest()


def _observed(
    *,
    content_length: int = len(BODY),
    content_fingerprint: str = BODY_FP,
) -> LegalEvidenceContent:
    return register_observed_legal_evidence_content(
        tenant_id="tenant-c3a",
        case_matter_id="matter-c3a",
        document_id="document-c3a",
        media_type="application/pdf",
        original_filename="evidence.pdf",
        observed_content_length=content_length,
        observed_content_fingerprint=content_fingerprint,
        source_evidence_reference="source-c3a",
        source_evidence_fingerprint=SOURCE_FP,
        registered_at=AT,
    )


def test_streamed_factory_requires_no_raw_content_parameter() -> None:
    parameters = inspect.signature(
        register_observed_legal_evidence_content
    ).parameters

    assert "content" not in parameters
    assert "content_bytes" not in parameters
    assert "observed_content_length" in parameters
    assert "observed_content_fingerprint" in parameters


def test_streamed_identity_matches_legacy_identity_for_same_bytes() -> None:
    legacy = register_legal_evidence_content(
        tenant_id="tenant-c3a",
        case_matter_id="matter-c3a",
        document_id="document-c3a",
        media_type="application/pdf",
        original_filename="evidence.pdf",
        content=BODY,
        source_evidence_reference="source-c3a",
        source_evidence_fingerprint=SOURCE_FP,
        registered_at=AT,
    )

    observed = _observed()

    assert observed == legacy
    assert observed.content_reference == legacy.content_reference
    assert observed.content_fingerprint == BODY_FP
    assert observed.content_length == len(BODY)
    assert observed.fingerprint == legacy.fingerprint


def test_streamed_identity_can_exceed_legacy_inline_byte_ceiling() -> None:
    observed_length = MAX_CONTENT_BYTES + 1

    value = _observed(
        content_length=observed_length,
    )

    assert value.content_length == observed_length
    assert value.content_fingerprint == BODY_FP


@pytest.mark.parametrize(
    ("content_length", "content_fingerprint"),
    (
        (0, BODY_FP),
        (-1, BODY_FP),
        (True, BODY_FP),
        (len(BODY), ""),
        (len(BODY), "A" * 128),
        (len(BODY), "f" * 127),
        (len(BODY), "g" * 128),
    ),
)
def test_invalid_stream_observations_reject(
    content_length: int,
    content_fingerprint: str,
) -> None:
    with pytest.raises(
        LegalEvidenceContentError,
    ):
        _observed(
            content_length=content_length,
            content_fingerprint=content_fingerprint,
        )


def test_streamed_identity_preserves_existing_scope_and_content_guards() -> None:
    with pytest.raises(
        LegalEvidenceContentError,
    ):
        register_observed_legal_evidence_content(
            tenant_id="global",
            case_matter_id="matter-c3a",
            document_id="document-c3a",
            media_type="application/pdf",
            original_filename="evidence.pdf",
            observed_content_length=len(BODY),
            observed_content_fingerprint=BODY_FP,
            source_evidence_reference="source-c3a",
            source_evidence_fingerprint=SOURCE_FP,
            registered_at=AT,
        )

    with pytest.raises(
        LegalEvidenceContentError,
    ):
        register_observed_legal_evidence_content(
            tenant_id="tenant-c3a",
            case_matter_id="matter-c3a",
            document_id="document-c3a",
            media_type="text/html",
            original_filename="evidence.pdf",
            observed_content_length=len(BODY),
            observed_content_fingerprint=BODY_FP,
            source_evidence_reference="source-c3a",
            source_evidence_fingerprint=SOURCE_FP,
            registered_at=AT,
        )

    with pytest.raises(
        LegalEvidenceContentError,
    ):
        register_observed_legal_evidence_content(
            tenant_id="tenant-c3a",
            case_matter_id="matter-c3a",
            document_id="document-c3a",
            media_type="application/pdf",
            original_filename="../evidence.pdf",
            observed_content_length=len(BODY),
            observed_content_fingerprint=BODY_FP,
            source_evidence_reference="source-c3a",
            source_evidence_fingerprint=SOURCE_FP,
            registered_at=AT,
        )


def test_streamed_identity_is_deterministic_and_round_trips() -> None:
    first = _observed()
    second = _observed()

    assert first == second
    assert first.fingerprint == second.fingerprint

    restored = LegalEvidenceContent.from_dict(
        first.to_dict()
    )

    assert restored == first
    assert restored.fingerprint == first.fingerprint


def test_streamed_serialization_contains_no_raw_binary_body() -> None:
    serialized = _observed().to_dict()

    forbidden = {
        "content",
        "content_bytes",
        "bytes",
        "body",
        "binary_body",
    }

    assert forbidden.isdisjoint(
        serialized
    )
    assert all(
        not isinstance(
            value,
            (
                bytes,
                bytearray,
            ),
        )
        for value in serialized.values()
    )


def test_streamed_identity_creates_no_later_authority() -> None:
    serialized = _observed().to_dict()

    forbidden = {
        "provider_name",
        "storage_reference",
        "object_version_reference",
        "reservation_id",
        "reservation_consumed",
        "usage_committed",
        "available",
        "authorized_availability",
        "iam_authorized",
        "legal_hold",
        "retention_authorized",
        "invoice",
        "payment",
        "settlement",
    }

    assert forbidden.isdisjoint(
        serialized
    )


# ARTIFACT: test_legal_evidence_streamed_content_identity.py
# VERSION: v1.0.0-L10A2R-C3A-STREAM-DERIVED-CONTENT-IDENTITY-CERT
# AUTHORITY BOUNDARY: pure canonical stream-observation -> content identity only
# LEGACY POSTURE: whole-byte registration ceiling remains separately enforced
# STREAMING POSTURE: no full-object byte parameter or materialization required
# INTEGRITY POSTURE: canonical WILSY SHA3-512 remains content identity
# AVAILABILITY POSTURE: content identity does not authorize availability
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
