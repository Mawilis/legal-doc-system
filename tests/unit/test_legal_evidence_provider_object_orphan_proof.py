"""Direct certificate for exact Legal Evidence provider-object orphan proof.

VERSION: v1.0.1-L10A2R-C4D6D-B1-PROVIDER-OBJECT-ORPHAN-PROOF-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG: v1.0.1-L10A2R-C4D6D-B1-PROVIDER-OBJECT-ORPHAN-PROOF-CERT aligns the observation-tamper certificate
           with the authoritative fail-closed membership boundary: a mutated
           completed-object observation is rejected as OBSERVATION_NOT_VERIFIED
           before it can be promoted into orphan-proof evidence.
           v1.0.0-L10A2R-C4D6D-B1-PROVIDER-OBJECT-ORPHAN-PROOF-CERT certified
           immutable exact-object orphan proof, strict hydration integrity,
           same-service sealed coverage membership, durable authorized
           disownership correlation, chronology, fail-closed prerequisite
           tamper handling and downstream-authority exclusion.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone
import inspect
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_evidence_provider_object_disownership import (
    LegalEvidenceProviderObjectDisownership,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_object_orphan_proof import (
    SCHEMA,
    VERSION,
    LegalEvidenceProviderObjectOrphanProof,
    LegalEvidenceProviderObjectOrphanProofError,
    prove_legal_evidence_provider_object_orphan,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectIntentMetadataState,
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceProviderDiscoveryScope,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_enumeration_port import (
    LegalEvidenceProviderCoverageEnumerationPort,
    LegalEvidenceProviderEnumerationKind,
    LegalEvidenceProviderEnumerationPage,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_verification_service import (
    LegalEvidenceProviderCoverageVerification,
    LegalEvidenceProviderCoverageVerificationService,
)


AT = datetime(
    2026,
    10,
    1,
    10,
    0,
    tzinfo=timezone.utc,
)

SHA_A = "a" * 128
SHA_B = "b" * 128


def _scope(
    *,
    tenant_id: str = "tenant-b1-cert",
) -> LegalEvidenceProviderDiscoveryScope:
    return LegalEvidenceProviderDiscoveryScope(
        tenant_id=tenant_id,
        tenant_scope_fingerprint=SHA_A,
    )


def _completed(
    *,
    tenant_id: str = "tenant-b1-cert",
    provider_name: str = "aws_s3",
    storage_reference: str = "opaque/storage/b1-cert",
    object_version_reference: str = "version-b1-cert",
    observed_at: datetime = AT,
) -> LegalEvidenceCompletedObjectObservation:
    return LegalEvidenceCompletedObjectObservation(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        provider_integrity_reference='"etag-b1-cert"',
        content_length=17,
        last_modified_at=observed_at,
        observed_at=observed_at,
        write_intent_metadata_state=(
            LegalEvidenceCompletedObjectIntentMetadataState
            .ABSENT
        ),
        write_intent_fingerprint=None,
    )


def _page(
    *,
    scope: LegalEvidenceProviderDiscoveryScope,
    kind: LegalEvidenceProviderEnumerationKind,
    observations: tuple[Any, ...] = (),
) -> LegalEvidenceProviderEnumerationPage:
    return LegalEvidenceProviderEnumerationPage(
        tenant_id=scope.tenant_id,
        tenant_scope_fingerprint=scope.tenant_scope_fingerprint,
        provider_name="aws_s3",
        enumeration_kind=kind,
        observed_at=AT,
        observations=observations,
        next_page_reference=None,
    )


class _Provider:
    def __init__(
        self,
        *,
        scope: LegalEvidenceProviderDiscoveryScope,
        completed: tuple[LegalEvidenceCompletedObjectObservation, ...] = (),
    ) -> None:
        self.scope = scope
        self.completed = completed

    def list_incomplete_write_session_page(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
        page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        assert scope == self.scope
        assert observed_at == AT
        assert page_reference is None

        return _page(
            scope=scope,
            kind=(
                LegalEvidenceProviderEnumerationKind
                .INCOMPLETE_WRITE_SESSIONS
            ),
        )

    def list_completed_object_version_page(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
        page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        assert scope == self.scope
        assert observed_at == AT
        assert page_reference is None

        return _page(
            scope=scope,
            kind=(
                LegalEvidenceProviderEnumerationKind
                .COMPLETED_OBJECT_VERSIONS
            ),
            observations=cast(
                tuple[Any, ...],
                self.completed,
            ),
        )


def _service(
    *,
    scope: LegalEvidenceProviderDiscoveryScope,
    completed: tuple[LegalEvidenceCompletedObjectObservation, ...] = (),
) -> LegalEvidenceProviderCoverageVerificationService:
    provider = _Provider(
        scope=scope,
        completed=completed,
    )

    assert isinstance(
        provider,
        LegalEvidenceProviderCoverageEnumerationPort,
    )

    return LegalEvidenceProviderCoverageVerificationService(
        provider=provider,
    )


def _disownership(
    *,
    tenant_id: str = "tenant-b1-cert",
    provider_name: str = "aws_s3",
    storage_reference: str = "opaque/storage/b1-cert",
    object_version_reference: str = "version-b1-cert",
    decided_at: datetime = AT - timedelta(minutes=5),
    reference: str = "disownership-b1-cert",
) -> LegalEvidenceProviderObjectDisownership:
    return LegalEvidenceProviderObjectDisownership(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        disownership_reference=reference,
        reason_reference="reason-b1-cert",
        source_evidence_reference="source-b1-cert",
        source_evidence_fingerprint=SHA_A,
        authorization_evidence_reference="authorization-b1-cert",
        authorization_evidence_fingerprint=SHA_B,
        decided_at=decided_at,
    )


def _issued_prerequisites() -> tuple[
    LegalEvidenceProviderCoverageVerificationService,
    LegalEvidenceProviderCoverageVerification,
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceProviderObjectDisownership,
]:
    scope = _scope()

    observation = _completed()

    service = _service(
        scope=scope,
        completed=(observation,),
    )

    verification = service.verify_coverage(
        scope=scope,
        provider_name="aws_s3",
        observed_at=AT,
    )

    disownership = _disownership()

    return (
        service,
        verification,
        observation,
        disownership,
    )


def _proof(
    *,
    reference: str = "orphan-proof-b1-cert",
    proved_at: datetime = AT + timedelta(minutes=1),
) -> LegalEvidenceProviderObjectOrphanProof:
    (
        service,
        verification,
        observation,
        disownership,
    ) = _issued_prerequisites()

    return prove_legal_evidence_provider_object_orphan(
        coverage_service=service,
        verification=verification,
        observation=observation,
        disownership=disownership,
        orphan_proof_reference=reference,
        proved_at=proved_at,
    )


def test_orphan_proof_shape_is_frozen_slots_factory_only_and_exact() -> None:
    expected_fields = [
        "tenant_id",
        "provider_name",
        "storage_reference",
        "object_version_reference",
        "orphan_proof_reference",
        "coverage_verification_fingerprint",
        "completed_observation_membership_fingerprint",
        "disownership_reference",
        "disownership_fingerprint",
        "provider_observed_at",
        "disownership_decided_at",
        "proved_at",
        "schema",
        "version",
        "fingerprint",
    ]

    assert [
        field.name
        for field in fields(
            LegalEvidenceProviderObjectOrphanProof
        )
    ] == expected_fields

    assert "__slots__" in vars(
        LegalEvidenceProviderObjectOrphanProof
    )

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofError,
        match="L10A2R_C4D6D_B1_ORPHAN_PROOF_FACTORY_REQUIRED",
    ):
        LegalEvidenceProviderObjectOrphanProof()

    proof = _proof()

    assert not hasattr(
        proof,
        "__dict__",
    )

    with pytest.raises(
        FrozenInstanceError,
    ):
        proof.tenant_id = "mutated"  # type: ignore[misc]


def test_positive_exact_proof_is_deterministic_correlated_and_round_trips() -> None:
    (
        service,
        verification,
        observation,
        disownership,
    ) = _issued_prerequisites()

    membership = (
        service
        .completed_observation_membership_fingerprint(
            verified=verification,
            observation=observation,
        )
    )

    assert membership is not None

    first = prove_legal_evidence_provider_object_orphan(
        coverage_service=service,
        verification=verification,
        observation=observation,
        disownership=disownership,
        orphan_proof_reference="orphan-proof-positive",
        proved_at=AT + timedelta(minutes=1),
    )

    second = prove_legal_evidence_provider_object_orphan(
        coverage_service=service,
        verification=verification,
        observation=observation,
        disownership=disownership,
        orphan_proof_reference="orphan-proof-positive",
        proved_at=AT + timedelta(minutes=1),
    )

    assert first == second
    assert first.fingerprint == second.fingerprint

    assert first.tenant_id == verification.tenant_id
    assert first.provider_name == verification.provider_name
    assert first.storage_reference == observation.storage_reference
    assert (
        first.object_version_reference
        == observation.object_version_reference
    )

    assert (
        first.coverage_verification_fingerprint
        == verification.fingerprint
    )

    assert (
        first.completed_observation_membership_fingerprint
        == membership
    )

    assert (
        first.disownership_reference
        == disownership.disownership_reference
    )

    assert (
        first.disownership_fingerprint
        == disownership.fingerprint
    )

    assert first.provider_observed_at == AT

    assert (
        first.disownership_decided_at
        == AT - timedelta(minutes=5)
    )

    assert (
        first.proved_at
        == AT + timedelta(minutes=1)
    )

    assert first.schema == SCHEMA
    assert first.version == VERSION

    assert len(first.fingerprint) == 128
    assert first.fingerprint == first.fingerprint.lower()

    hydrated = (
        LegalEvidenceProviderObjectOrphanProof
        .from_dict(
            first.to_dict()
        )
    )

    assert hydrated == first
    assert hydrated.to_dict() == first.to_dict()


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        (
            lambda document: document.__setitem__(
                "unexpected",
                "value",
            ),
            "L10A2R_C4D6D_B1_DOCUMENT_FIELDS_INVALID",
        ),
        (
            lambda document: document.pop(
                "provider_name"
            ),
            "L10A2R_C4D6D_B1_DOCUMENT_FIELDS_INVALID",
        ),
        (
            lambda document: document.__setitem__(
                "schema",
                "wrong.schema",
            ),
            "L10A2R_C4D6D_B1_SCHEMA_INVALID",
        ),
        (
            lambda document: document.__setitem__(
                "version",
                "wrong-version",
            ),
            "L10A2R_C4D6D_B1_VERSION_INVALID",
        ),
        (
            lambda document: document.__setitem__(
                "fingerprint",
                "f" * 128,
            ),
            "L10A2R_C4D6D_B1_FINGERPRINT_MISMATCH",
        ),
    ],
)
def test_strict_hydration_rejects_field_metadata_and_fingerprint_drift(
    mutation: Any,
    error: str,
) -> None:
    document = _proof().to_dict()

    mutation(
        document
    )

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofError,
        match=error,
    ):
        LegalEvidenceProviderObjectOrphanProof.from_dict(
            document
        )


@pytest.mark.parametrize(
    ("field_name", "bad_value", "error"),
    [
        (
            "tenant_id",
            7,
            "L10A2R_C4D6D_B1_TENANT_ID_INVALID",
        ),
        (
            "orphan_proof_reference",
            " invalid ",
            "L10A2R_C4D6D_B1_ORPHAN_PROOF_REFERENCE_INVALID",
        ),
        (
            "coverage_verification_fingerprint",
            "A" * 128,
            "L10A2R_C4D6D_B1_COVERAGE_VERIFICATION_FINGERPRINT_INVALID",
        ),
        (
            "proved_at",
            datetime(
                2026,
                10,
                1,
                11,
                0,
            ),
            "L10A2R_C4D6D_B1_PROVED_AT_INVALID",
        ),
    ],
)
def test_strict_hydration_rejects_malformed_identity_digest_and_timestamp(
    field_name: str,
    bad_value: object,
    error: str,
) -> None:
    document = _proof().to_dict()

    document[
        field_name
    ] = bad_value

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofError,
        match=error,
    ):
        LegalEvidenceProviderObjectOrphanProof.from_dict(
            document
        )


def test_foreign_service_verification_rejects() -> None:
    (
        service_a,
        verification,
        observation,
        disownership,
    ) = _issued_prerequisites()

    assert service_a.accepts_verification(
        verification
    )

    service_b = _service(
        scope=_scope(),
        completed=(observation,),
    )

    assert not service_b.accepts_verification(
        verification
    )

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofError,
        match="L10A2R_C4D6D_B1_VERIFICATION_NOT_ACCEPTED",
    ):
        prove_legal_evidence_provider_object_orphan(
            coverage_service=service_b,
            verification=verification,
            observation=observation,
            disownership=disownership,
            orphan_proof_reference="orphan-proof-foreign-service",
            proved_at=AT + timedelta(minutes=1),
        )


def test_unsealed_completed_observation_rejects() -> None:
    scope = _scope()

    member = _completed(
        object_version_reference="member-version",
    )

    outsider = _completed(
        object_version_reference="outsider-version",
    )

    service = _service(
        scope=scope,
        completed=(member,),
    )

    verification = service.verify_coverage(
        scope=scope,
        provider_name="aws_s3",
        observed_at=AT,
    )

    outsider_disownership = _disownership(
        object_version_reference="outsider-version",
        reference="disownership-outsider",
    )

    assert (
        service
        .completed_observation_membership_fingerprint(
            verified=verification,
            observation=outsider,
        )
        is None
    )

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofError,
        match="L10A2R_C4D6D_B1_OBSERVATION_NOT_VERIFIED",
    ):
        prove_legal_evidence_provider_object_orphan(
            coverage_service=service,
            verification=verification,
            observation=outsider,
            disownership=outsider_disownership,
            orphan_proof_reference="orphan-proof-outsider",
            proved_at=AT + timedelta(minutes=1),
        )


@pytest.mark.parametrize(
    ("disownership", "error"),
    [
        (
            _disownership(
                tenant_id="tenant-other",
                reference="disownership-tenant-mismatch",
            ),
            "L10A2R_C4D6D_B1_TENANT_SCOPE_MISMATCH",
        ),
        (
            _disownership(
                provider_name="other_provider",
                reference="disownership-provider-mismatch",
            ),
            "L10A2R_C4D6D_B1_PROVIDER_SCOPE_MISMATCH",
        ),
        (
            _disownership(
                storage_reference="opaque/storage/other",
                reference="disownership-storage-mismatch",
            ),
            "L10A2R_C4D6D_B1_STORAGE_REFERENCE_MISMATCH",
        ),
        (
            _disownership(
                object_version_reference="version-other",
                reference="disownership-version-mismatch",
            ),
            "L10A2R_C4D6D_B1_OBJECT_VERSION_MISMATCH",
        ),
    ],
)
def test_exact_disownership_identity_correlation_rejects_divergence(
    disownership: LegalEvidenceProviderObjectDisownership,
    error: str,
) -> None:
    (
        service,
        verification,
        observation,
        _,
    ) = _issued_prerequisites()

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofError,
        match=error,
    ):
        prove_legal_evidence_provider_object_orphan(
            coverage_service=service,
            verification=verification,
            observation=observation,
            disownership=disownership,
            orphan_proof_reference="orphan-proof-identity-mismatch",
            proved_at=AT + timedelta(minutes=1),
        )


def test_disownership_after_provider_observation_rejects() -> None:
    (
        service,
        verification,
        observation,
        _,
    ) = _issued_prerequisites()

    late_disownership = _disownership(
        decided_at=AT + timedelta(seconds=1),
        reference="disownership-late",
    )

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofError,
        match="L10A2R_C4D6D_B1_DISOWNERSHIP_AFTER_OBSERVATION",
    ):
        prove_legal_evidence_provider_object_orphan(
            coverage_service=service,
            verification=verification,
            observation=observation,
            disownership=late_disownership,
            orphan_proof_reference="orphan-proof-late-disownership",
            proved_at=AT + timedelta(minutes=1),
        )


def test_proof_time_before_provider_observation_rejects() -> None:
    (
        service,
        verification,
        observation,
        disownership,
    ) = _issued_prerequisites()

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofError,
        match="L10A2R_C4D6D_B1_PROOF_CHRONOLOGY_INVALID",
    ):
        prove_legal_evidence_provider_object_orphan(
            coverage_service=service,
            verification=verification,
            observation=observation,
            disownership=disownership,
            orphan_proof_reference="orphan-proof-too-early",
            proved_at=AT - timedelta(seconds=1),
        )


def test_post_issuance_coverage_verification_fingerprint_tamper_rejects() -> None:
    (
        service,
        verification,
        observation,
        disownership,
    ) = _issued_prerequisites()

    original = verification.fingerprint

    object.__setattr__(
        verification,
        "fingerprint",
        (
            "f" * 128
            if original != "f" * 128
            else "e" * 128
        ),
    )

    assert not service.accepts_verification(
        verification
    )

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofError,
        match="L10A2R_C4D6D_B1_VERIFICATION_NOT_ACCEPTED",
    ):
        prove_legal_evidence_provider_object_orphan(
            coverage_service=service,
            verification=verification,
            observation=observation,
            disownership=disownership,
            orphan_proof_reference="orphan-proof-verification-tamper",
            proved_at=AT + timedelta(minutes=1),
        )


def test_post_construction_observation_tamper_rejects() -> None:
    (
        service,
        verification,
        observation,
        disownership,
    ) = _issued_prerequisites()

    object.__setattr__(
        observation,
        "provider_name",
        "tampered_provider",
    )

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofError,
        match="L10A2R_C4D6D_B1_OBSERVATION_NOT_VERIFIED",
    ):
        prove_legal_evidence_provider_object_orphan(
            coverage_service=service,
            verification=verification,
            observation=observation,
            disownership=disownership,
            orphan_proof_reference="orphan-proof-observation-tamper",
            proved_at=AT + timedelta(minutes=1),
        )


def test_post_construction_disownership_tamper_rejects() -> None:
    (
        service,
        verification,
        observation,
        disownership,
    ) = _issued_prerequisites()

    original = disownership.fingerprint

    object.__setattr__(
        disownership,
        "fingerprint",
        (
            "f" * 128
            if original != "f" * 128
            else "e" * 128
        ),
    )

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofError,
        match="L10A2R_C4D6D_B1_PREREQUISITE_INVALID",
    ):
        prove_legal_evidence_provider_object_orphan(
            coverage_service=service,
            verification=verification,
            observation=observation,
            disownership=disownership,
            orphan_proof_reference="orphan-proof-disownership-tamper",
            proved_at=AT + timedelta(minutes=1),
        )


def test_absent_write_intent_metadata_never_substitutes_for_disownership() -> None:
    (
        service,
        verification,
        observation,
        _,
    ) = _issued_prerequisites()

    assert (
        observation.write_intent_metadata_state
        is LegalEvidenceCompletedObjectIntentMetadataState.ABSENT
    )

    parameters = inspect.signature(
        prove_legal_evidence_provider_object_orphan
    ).parameters

    assert "disownership" in parameters

    wrong_disownership = cast(
        LegalEvidenceProviderObjectDisownership,
        object(),
    )

    with pytest.raises(
        LegalEvidenceProviderObjectOrphanProofError,
        match="L10A2R_C4D6D_B1_DISOWNERSHIP_REQUIRED",
    ):
        prove_legal_evidence_provider_object_orphan(
            coverage_service=service,
            verification=verification,
            observation=observation,
            disownership=wrong_disownership,
            orphan_proof_reference="orphan-proof-no-disownership",
            proved_at=AT + timedelta(minutes=1),
        )


def test_orphan_proof_grants_no_retention_hold_abort_delete_or_financial_authority() -> None:
    proof = _proof()

    forbidden = {
        "retention_satisfied",
        "retention_expired",
        "legal_hold_released",
        "hold_released",
        "abort_authorized",
        "delete_authorized",
        "deletion_authorized",
        "provider_delete_authorized",
        "delete_object",
        "delete_objects",
        "billing_authorized",
        "payment_authorized",
        "settlement_authorized",
    }

    public_value_surface = {
        name
        for name in dir(
            proof
        )
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(
        public_value_surface
    )

    public_factory_surface = {
        name
        for name in dir(
            LegalEvidenceProviderObjectOrphanProof
        )
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(
        public_factory_surface
    )


# ARTIFACT: test_legal_evidence_provider_object_orphan_proof.py
# VERSION: v1.0.1-L10A2R-C4D6D-B1-PROVIDER-OBJECT-ORPHAN-PROOF-CERT
# AUTHORITY BOUNDARY: exact positive provider-object orphan-proof evidence only
# COVERAGE POSTURE: exact same-service sealed completed-observation membership required
# DISOWNERSHIP POSTURE: explicit authorized disownership evidence remains prerequisite
# METADATA POSTURE: ABSENT / NOT_OBSERVED write-intent metadata is never orphan authority
# TIME POSTURE: disownership <= provider observation <= proof time
# RETENTION / HOLD POSTURE: no retention satisfaction or legal-hold release authority
# DELETION POSTURE: no abort, deletion authorization or provider deletion authority
# PERSISTENCE POSTURE: no registry or durable persistence authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# FAIL-CLOSED POSTURE: malformed, divergent, stale, foreign or tampered prerequisites reject
# END OF WILSY OS SOVEREIGN ARTIFACT
