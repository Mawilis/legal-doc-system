"""Direct certificate for trusted Legal Evidence provider coverage verification.

VERSION: v1.1.0-L10A2R-C4D6C-B-TRUSTED-COVERAGE-VERIFICATION-CERT
AUTHORITY: Wilsy OS Core Governance
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG: v1.0.0-L10A2R-C4D6C-B certifies service-owned origin traversal,
           exact scope/kind/time binding, cycle rejection, deterministic
           verification evidence and private-capability issuance.
"""

from __future__ import annotations

from datetime import datetime, timezone
import inspect
from typing import Any

import pytest

from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectIntentMetadataState,
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceIncompleteWriteSessionObservation,
    LegalEvidenceProviderDiscoveryScope,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_enumeration_port import (
    LegalEvidenceProviderCoverageEnumerationError,
    LegalEvidenceProviderCoverageEnumerationPort,
    LegalEvidenceProviderEnumerationKind,
    LegalEvidenceProviderEnumerationPage,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_verification_service import (
    LegalEvidenceProviderCoverageVerification,
    LegalEvidenceProviderCoverageVerificationError,
    LegalEvidenceProviderCoverageVerificationService,
)

AT = datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc)
SHA_A = "a" * 128
SHA_B = "b" * 128


def _scope() -> LegalEvidenceProviderDiscoveryScope:
    return LegalEvidenceProviderDiscoveryScope(
        tenant_id="tenant-c4d6cb",
        tenant_scope_fingerprint=SHA_A,
    )


def _incomplete(
    *,
    reference: str = "upload-1",
) -> LegalEvidenceIncompleteWriteSessionObservation:
    return LegalEvidenceIncompleteWriteSessionObservation(
        tenant_id="tenant-c4d6cb",
        provider_name="aws_s3",
        storage_reference="opaque/storage/a",
        write_session_reference=reference,
        initiated_at=AT,
        observed_at=AT,
    )


def _completed(
    *,
    reference: str = "version-1",
) -> LegalEvidenceCompletedObjectObservation:
    return LegalEvidenceCompletedObjectObservation(
        tenant_id="tenant-c4d6cb",
        provider_name="aws_s3",
        storage_reference="opaque/storage/b",
        object_version_reference=reference,
        provider_integrity_reference='"etag"',
        content_length=7,
        last_modified_at=AT,
        observed_at=AT,
        write_intent_metadata_state=(
            LegalEvidenceCompletedObjectIntentMetadataState
            .ABSENT
        ),
        write_intent_fingerprint=None,
    )


def _page(
    *,
    kind: LegalEvidenceProviderEnumerationKind,
    observations: tuple[Any, ...],
    continuation: str | None,
) -> LegalEvidenceProviderEnumerationPage:
    return LegalEvidenceProviderEnumerationPage(
        tenant_id="tenant-c4d6cb",
        tenant_scope_fingerprint=SHA_A,
        provider_name="aws_s3",
        enumeration_kind=kind,
        observed_at=AT,
        observations=observations,
        next_page_reference=continuation,
    )


class _Provider:
    def __init__(
        self,
        *,
        incomplete: list[LegalEvidenceProviderEnumerationPage] | None = None,
        completed: list[LegalEvidenceProviderEnumerationPage] | None = None,
    ) -> None:
        self.incomplete = list(
            incomplete
            or [
                _page(
                    kind=(
                        LegalEvidenceProviderEnumerationKind
                        .INCOMPLETE_WRITE_SESSIONS
                    ),
                    observations=(),
                    continuation=None,
                )
            ]
        )
        self.completed = list(
            completed
            or [
                _page(
                    kind=(
                        LegalEvidenceProviderEnumerationKind
                        .COMPLETED_OBJECT_VERSIONS
                    ),
                    observations=(),
                    continuation=None,
                )
            ]
        )
        self.calls: list[
            tuple[
                str,
                str | None,
                datetime,
            ]
        ] = []

    def list_incomplete_write_session_page(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
        page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        self.calls.append(
            (
                "incomplete",
                page_reference,
                observed_at,
            )
        )
        if not self.incomplete:
            raise AssertionError(
                "unexpected incomplete traversal"
            )
        return self.incomplete.pop(0)

    def list_completed_object_version_page(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
        page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        self.calls.append(
            (
                "completed",
                page_reference,
                observed_at,
            )
        )
        if not self.completed:
            raise AssertionError(
                "unexpected completed traversal"
            )
        return self.completed.pop(0)


def _service(
    provider: _Provider,
) -> LegalEvidenceProviderCoverageVerificationService:
    assert isinstance(
        provider,
        LegalEvidenceProviderCoverageEnumerationPort,
    )
    return LegalEvidenceProviderCoverageVerificationService(
        provider=provider,
    )


def test_service_owns_first_page_reference_and_traverses_both_kinds() -> None:
    provider = _Provider(
        incomplete=[
            _page(
                kind=(
                    LegalEvidenceProviderEnumerationKind
                    .INCOMPLETE_WRITE_SESSIONS
                ),
                observations=(_incomplete(),),
                continuation="next-i",
            ),
            _page(
                kind=(
                    LegalEvidenceProviderEnumerationKind
                    .INCOMPLETE_WRITE_SESSIONS
                ),
                observations=(),
                continuation=None,
            ),
        ],
        completed=[
            _page(
                kind=(
                    LegalEvidenceProviderEnumerationKind
                    .COMPLETED_OBJECT_VERSIONS
                ),
                observations=(_completed(),),
                continuation="next-c",
            ),
            _page(
                kind=(
                    LegalEvidenceProviderEnumerationKind
                    .COMPLETED_OBJECT_VERSIONS
                ),
                observations=(),
                continuation=None,
            ),
        ],
    )

    verified = _service(provider).verify_coverage(
        scope=_scope(),
        provider_name="aws_s3",
        observed_at=AT,
    )

    assert provider.calls == [
        ("incomplete", None, AT),
        ("incomplete", "next-i", AT),
        ("completed", None, AT),
        ("completed", "next-c", AT),
    ]
    assert verified.incomplete_page_count == 2
    assert verified.completed_page_count == 2
    assert verified.incomplete_observation_count == 1
    assert verified.completed_observation_count == 1


def test_verify_api_accepts_no_caller_page_reference() -> None:
    parameters = inspect.signature(
        LegalEvidenceProviderCoverageVerificationService.verify_coverage
    ).parameters

    assert "page_reference" not in parameters
    assert "continuation" not in parameters
    assert "next_page_reference" not in parameters


def test_same_observed_at_is_forwarded_to_every_page() -> None:
    provider = _Provider()
    _service(provider).verify_coverage(
        scope=_scope(),
        provider_name="aws_s3",
        observed_at=AT,
    )

    assert provider.calls
    assert {
        call[2]
        for call in provider.calls
    } == {AT}


def test_post_construction_page_tampering_fails_closed() -> None:
    page = _page(
        kind=(
            LegalEvidenceProviderEnumerationKind
            .INCOMPLETE_WRITE_SESSIONS
        ),
        observations=(),
        continuation=None,
    )

    original_fingerprint = page.fingerprint

    object.__setattr__(
        page,
        "provider_name",
        "tampered-provider",
    )

    assert page.fingerprint == original_fingerprint

    provider = _Provider(
        incomplete=[page],
    )

    with pytest.raises(
        LegalEvidenceProviderCoverageEnumerationError,
        match="L10A2R_C4D6B_FINGERPRINT_MISMATCH",
    ):
        _service(provider).verify_coverage(
            scope=_scope(),
            provider_name="tampered-provider",
            observed_at=AT,
        )

    assert provider.calls == [
        (
            "incomplete",
            None,
            AT,
        )
    ]


def test_page_scope_divergence_fails_closed() -> None:
    bad = LegalEvidenceProviderEnumerationPage(
        tenant_id="tenant-c4d6cb",
        tenant_scope_fingerprint=SHA_B,
        provider_name="aws_s3",
        enumeration_kind=(
            LegalEvidenceProviderEnumerationKind
            .INCOMPLETE_WRITE_SESSIONS
        ),
        observed_at=AT,
        observations=(),
        next_page_reference=None,
    )

    provider = _Provider(
        incomplete=[bad],
    )

    with pytest.raises(
        LegalEvidenceProviderCoverageVerificationError,
        match="L10A2R_C4D6C_B_PAGE_SCOPE_MISMATCH",
    ):
        _service(provider).verify_coverage(
            scope=_scope(),
            provider_name="aws_s3",
            observed_at=AT,
        )


def test_page_kind_divergence_fails_closed() -> None:
    provider = _Provider(
        incomplete=[
            _page(
                kind=(
                    LegalEvidenceProviderEnumerationKind
                    .COMPLETED_OBJECT_VERSIONS
                ),
                observations=(),
                continuation=None,
            )
        ],
    )

    with pytest.raises(
        LegalEvidenceProviderCoverageVerificationError,
        match="L10A2R_C4D6C_B_PAGE_SCOPE_MISMATCH",
    ):
        _service(provider).verify_coverage(
            scope=_scope(),
            provider_name="aws_s3",
            observed_at=AT,
        )


def test_page_time_divergence_fails_closed() -> None:
    later = AT.replace(hour=1)

    bad = LegalEvidenceProviderEnumerationPage(
        tenant_id="tenant-c4d6cb",
        tenant_scope_fingerprint=SHA_A,
        provider_name="aws_s3",
        enumeration_kind=(
            LegalEvidenceProviderEnumerationKind
            .INCOMPLETE_WRITE_SESSIONS
        ),
        observed_at=later,
        observations=(),
        next_page_reference=None,
    )

    with pytest.raises(
        LegalEvidenceProviderCoverageVerificationError,
        match="L10A2R_C4D6C_B_PAGE_SCOPE_MISMATCH",
    ):
        _service(
            _Provider(
                incomplete=[bad],
            )
        ).verify_coverage(
            scope=_scope(),
            provider_name="aws_s3",
            observed_at=AT,
        )


def test_repeated_continuation_cycle_fails_closed() -> None:
    first = _page(
        kind=(
            LegalEvidenceProviderEnumerationKind
            .INCOMPLETE_WRITE_SESSIONS
        ),
        observations=(),
        continuation="cycle",
    )
    second = _page(
        kind=(
            LegalEvidenceProviderEnumerationKind
            .INCOMPLETE_WRITE_SESSIONS
        ),
        observations=(),
        continuation="cycle",
    )

    with pytest.raises(
        LegalEvidenceProviderCoverageVerificationError,
        match="L10A2R_C4D6C_B_CONTINUATION_CYCLE",
    ):
        _service(
            _Provider(
                incomplete=[first, second],
            )
        ).verify_coverage(
            scope=_scope(),
            provider_name="aws_s3",
            observed_at=AT,
        )


def test_provider_failure_propagates_and_no_verification_is_issued() -> None:
    class _Failing(_Provider):
        def list_incomplete_write_session_page(
            self,
            scope: LegalEvidenceProviderDiscoveryScope,
            *,
            observed_at: datetime,
            page_reference: str | None,
        ) -> LegalEvidenceProviderEnumerationPage:
            raise RuntimeError("provider unavailable")

    service = _service(_Failing())

    with pytest.raises(
        RuntimeError,
        match="provider unavailable",
    ):
        service.verify_coverage(
            scope=_scope(),
            provider_name="aws_s3",
            observed_at=AT,
        )


def test_verification_public_construction_is_forbidden() -> None:
    with pytest.raises(
        LegalEvidenceProviderCoverageVerificationError,
        match=(
            "L10A2R_C4D6C_B_"
            "COVERAGE_VERIFICATION_FACTORY_REQUIRED"
        ),
    ):
        LegalEvidenceProviderCoverageVerification(
            tenant_id="tenant-c4d6cb",
            tenant_scope_fingerprint=SHA_A,
            provider_name="aws_s3",
            observed_at=AT,
            incomplete_page_count=1,
            completed_page_count=1,
            incomplete_observation_count=0,
            completed_observation_count=0,
            incomplete_page_fingerprints=(SHA_A,),
            completed_page_fingerprints=(SHA_B,),
            fingerprint=SHA_A,
        )


def test_verification_is_bound_to_exact_issuing_service() -> None:
    provider_a = _Provider()
    provider_b = _Provider()

    service_a = _service(provider_a)
    service_b = _service(provider_b)

    verified = service_a.verify_coverage(
        scope=_scope(),
        provider_name="aws_s3",
        observed_at=AT,
    )

    assert service_a.accepts_verification(
        verified
    )
    assert not service_b.accepts_verification(
        verified
    )
    assert not service_a.accepts_verification(
        object()
    )


def test_completed_observation_membership_is_exact_and_private() -> None:
    completed = _completed(
        reference="member-version"
    )

    service = _service(
        _Provider(
            completed=[
                _page(
                    kind=(
                        LegalEvidenceProviderEnumerationKind
                        .COMPLETED_OBJECT_VERSIONS
                    ),
                    observations=(completed,),
                    continuation=None,
                )
            ]
        )
    )

    verified = service.verify_coverage(
        scope=_scope(),
        provider_name="aws_s3",
        observed_at=AT,
    )

    assert service.contains_completed_observation(
        verified=verified,
        observation=completed,
    )

    assert len(
        verified.completed_observation_fingerprints
    ) == 1

    outsider = _completed(
        reference="outsider-version"
    )

    assert not service.contains_completed_observation(
        verified=verified,
        observation=outsider,
    )


def test_completed_observation_membership_rejects_cross_service_verification() -> None:
    completed = _completed(
        reference="cross-service-version"
    )

    service_a = _service(
        _Provider(
            completed=[
                _page(
                    kind=(
                        LegalEvidenceProviderEnumerationKind
                        .COMPLETED_OBJECT_VERSIONS
                    ),
                    observations=(completed,),
                    continuation=None,
                )
            ]
        )
    )

    service_b = _service(
        _Provider()
    )

    verified = service_a.verify_coverage(
        scope=_scope(),
        provider_name="aws_s3",
        observed_at=AT,
    )

    assert not service_b.contains_completed_observation(
        verified=verified,
        observation=completed,
    )


def test_completed_observation_membership_participates_in_verification_fingerprint() -> None:
    first = _completed(
        reference="membership-a"
    )
    second = _completed(
        reference="membership-b"
    )

    verified_a = _service(
        _Provider(
            completed=[
                _page(
                    kind=(
                        LegalEvidenceProviderEnumerationKind
                        .COMPLETED_OBJECT_VERSIONS
                    ),
                    observations=(first,),
                    continuation=None,
                )
            ]
        )
    ).verify_coverage(
        scope=_scope(),
        provider_name="aws_s3",
        observed_at=AT,
    )

    verified_b = _service(
        _Provider(
            completed=[
                _page(
                    kind=(
                        LegalEvidenceProviderEnumerationKind
                        .COMPLETED_OBJECT_VERSIONS
                    ),
                    observations=(second,),
                    continuation=None,
                )
            ]
        )
    ).verify_coverage(
        scope=_scope(),
        provider_name="aws_s3",
        observed_at=AT,
    )

    assert (
        verified_a.completed_observation_fingerprints
        != verified_b.completed_observation_fingerprints
    )
    assert verified_a.fingerprint != verified_b.fingerprint


def test_verification_fingerprint_is_deterministic() -> None:
    first = _service(
        _Provider()
    ).verify_coverage(
        scope=_scope(),
        provider_name="aws_s3",
        observed_at=AT,
    )

    second = _service(
        _Provider()
    ).verify_coverage(
        scope=_scope(),
        provider_name="aws_s3",
        observed_at=AT,
    )

    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 128


def test_verification_contains_no_later_authority() -> None:
    verified = _service(
        _Provider()
    ).verify_coverage(
        scope=_scope(),
        provider_name="aws_s3",
        observed_at=AT,
    )

    forbidden = {
        "owned",
        "ownership_proven",
        "disowned",
        "disownership_proven",
        "orphan",
        "orphan_proven",
        "retention_expired",
        "legal_hold_released",
        "abort_authorized",
        "deletion_authorized",
        "provider_delete_authorized",
    }

    public = {
        name
        for name in dir(verified)
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(
        public
    )


def test_public_service_surface_excludes_delete_abort_and_disownership() -> None:
    public = {
        name
        for name in dir(
            LegalEvidenceProviderCoverageVerificationService
        )
        if not name.startswith("_")
    }

    forbidden = {
        "abort",
        "delete",
        "delete_object",
        "delete_objects",
        "prove_orphan",
        "prove_disownership",
        "authorize_delete",
    }

    assert forbidden.isdisjoint(
        public
    )


# ARTIFACT: test_legal_evidence_provider_coverage_verification_service.py
# VERSION: v1.1.0-L10A2R-C4D6C-B-TRUSTED-COVERAGE-VERIFICATION-CERT
# AUTHORITY BOUNDARY: trusted traversal / private verification issuance only
# START POSTURE: callers cannot supply continuation origin
# COVERAGE POSTURE: terminal traversal of both C4D6B kinds only
# ANTI-FABRICATION POSTURE: public construction and cross-service reuse fail closed
# OWNERSHIP POSTURE: no ownership or durable disownership authority
# ORPHAN POSTURE: no orphan proof
# RETENTION / HOLD POSTURE: no retention or legal-hold authority
# DELETION POSTURE: no abort or deletion authority
# PERSISTENCE POSTURE: no durable state
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
