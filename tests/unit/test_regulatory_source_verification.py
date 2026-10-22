"""TITLE: R64 Regulatory Source Verification Adversarial Certificate.
VERSION: v1.0.0-R64-AUTHENTICATED-REGULATORY-VERIFICATION-CERT
AUTHORITY: Pure non-ingesting verification-boundary certification only.
EPITOME: Prove capture integrity, exact scope, freshness, FFC validity,
    deterministic replay, trust-root denial, and unforgeable no-authority output.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_regulatory_source_verification.py
COLLABORATION / OWNERSHIP: Legal Operations, R62 evidence, R63 source identity,
    and canonical principal lifecycle contracts; no registry or route consumer.
CERTIFICATION / UPDATE DATE: 2026-10-22
CHANGELOG:
    2026-10-22 v1.0.0-R64-AUTHENTICATED-REGULATORY-VERIFICATION-CERT
    Establishes the complete R64 denial, integrity, replay, and forgery suite.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 controls.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers; raw captures must
    never cross the decision boundary.
TENANT BOUNDARY: Exact tenant, actor, subject, kind, issuer and URI matching.
AUTHORITY BOUNDARY: No ingestion, practice, matter access, ethical-wall
    clearance, supervision, reassignment, registry mutation, or LPC API claim.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import fields, replace
from datetime import datetime, timedelta, timezone
from hashlib import sha3_512

import pytest

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.legal_operations.domain.legal_practitioner_professional_standing_evidence import (
    LegalPractitionerProfessionalStandingEvidence as Evidence,
    ProfessionalEvidenceKind,
)
from tools.eos.legal_operations.registry.legal_practitioner_professional_standing_evidence_registry import (
    AUTHORITATIVE_PUBLIC_SOURCES,
)
from tools.eos.legal_operations.service.regulatory_source_verification import (
    IssuerVerificationState,
    RegulatoryFreshnessPolicy,
    RegulatorySourceCapture,
    RegulatorySourceState,
    RegulatorySourceVerificationError,
    RegulatoryVerificationDecision,
    RegulatoryVerificationReason,
    verify_regulatory_source,
)


NOW = datetime(2026, 10, 22, 12, 0, tzinfo=timezone.utc)
PAYLOAD = b'{"synthetic":"public-record"}'
DIGEST = sha3_512(PAYLOAD).hexdigest()


def evidence(**overrides: object) -> Evidence:
    """Build one canonical synthetic R62 evidence fixture."""
    source = AUTHORITATIVE_PUBLIC_SOURCES[ProfessionalEvidenceKind.PRACTISING_STATUS]
    values: dict[str, object] = {
        "evidence_id": "r64-evidence-1",
        "tenant_id": "tenant-a",
        "practitioner_principal_id": "practitioner-a",
        "verified_subject_id": "lpc-subject-1",
        "issuer_source_id": source[0],
        "jurisdiction": "ZA",
        "evidence_kind": ProfessionalEvidenceKind.PRACTISING_STATUS,
        "outcome": "VERIFIED_CURRENT",
        "verification_method": "PUBLIC_WEB_OBSERVATION",
        "evidence_reference": "r64-observation-1",
        "source_uri": source[1],
        "observed_at": NOW - timedelta(hours=1),
        "valid_until": NOW + timedelta(days=1),
    }
    values.update(overrides)
    return Evidence(**values)  # type: ignore[arg-type]


def capture(**overrides: object) -> RegulatorySourceCapture:
    """Build one canonical transient public-record capture."""
    source = AUTHORITATIVE_PUBLIC_SOURCES[ProfessionalEvidenceKind.PRACTISING_STATUS]
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "actor_principal_id": "verifier-a",
        "submitted_by_principal_id": "verifier-a",
        "subject_id": "lpc-subject-1",
        "jurisdiction": "ZA",
        "evidence_kind": ProfessionalEvidenceKind.PRACTISING_STATUS,
        "issuer_source_id": source[0],
        "source_uri": source[1],
        "checked_at": NOW - timedelta(minutes=5),
        "source_state": RegulatorySourceState.HUMAN_OBSERVED_PUBLIC_RECORD,
        "issuer_verification_state": IssuerVerificationState.HUMAN_OBSERVATION_ONLY,
        "issuer_verification_reference": "r64-verification-1",
        "capture_digest": DIGEST,
        "captured_payload": PAYLOAD,
    }
    values.update(overrides)
    return RegulatorySourceCapture(**values)  # type: ignore[arg-type]


def policy(**overrides: object) -> RegulatoryFreshnessPolicy:
    """Build distinct practising-status and FFC capture-age policies."""
    values: dict[str, object] = {
        "policy_id": "r64-policy-1",
        "practising_status_max_age": timedelta(hours=24),
        "ffc_capture_max_age": timedelta(hours=1),
    }
    values.update(overrides)
    return RegulatoryFreshnessPolicy(**values)  # type: ignore[arg-type]


def verify(
    *,
    item: Evidence | None = None,
    source_capture: RegulatorySourceCapture | None = None,
    authority: PrincipalAuthority | None = None,
    freshness: RegulatoryFreshnessPolicy | None = None,
) -> RegulatoryVerificationDecision:
    """Evaluate one exact-scope R64 decision without persistence."""
    return verify_regulatory_source(
        evidence=item or evidence(),
        capture=source_capture or capture(),
        actor_authority=authority
        or PrincipalAuthority("verifier-a", PrincipalStatus.ACTIVE, 7),
        policy=freshness or policy(),
        evaluated_at=NOW,
    )


def test_fresh_public_observation_is_still_non_ingesting_and_has_no_raw_payload() -> None:
    """Prove the strongest ordinary result remains a content-free denial."""
    decision = verify()
    assert decision.reason is RegulatoryVerificationReason.R63_INGESTION_PERMISSION_UNAVAILABLE
    assert decision.ingestion_authorized is False
    assert decision.permits_operational_access is False
    assert decision.permits_professional_practice is False
    assert decision.permits_reassignment_execution is False
    assert "captured_payload" not in {item.name for item in fields(decision)}
    assert PAYLOAD not in repr(decision).encode("utf-8")


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"capture_digest": "0" * 128}, RegulatoryVerificationReason.CAPTURE_TAMPERED),
        ({"issuer_source_id": "forged-issuer"}, RegulatoryVerificationReason.SOURCE_IMPERSONATION),
        ({"source_uri": "https://forged.invalid/"}, RegulatoryVerificationReason.SOURCE_IMPERSONATION),
        ({"evidence_kind": ProfessionalEvidenceKind.FIDELITY_FUND_CERTIFICATE_STATUS}, RegulatoryVerificationReason.ACTOR_SCOPE_MISMATCH),
        ({"tenant_id": "tenant-b"}, RegulatoryVerificationReason.ACTOR_SCOPE_MISMATCH),
        ({"actor_principal_id": "verifier-b"}, RegulatoryVerificationReason.ACTOR_SCOPE_MISMATCH),
        ({"subject_id": "lpc-subject-2"}, RegulatoryVerificationReason.ACTOR_SCOPE_MISMATCH),
        ({"source_state": RegulatorySourceState.UNAVAILABLE_SOURCE}, RegulatoryVerificationReason.SOURCE_UNAVAILABLE),
        ({"source_state": RegulatorySourceState.DISPUTED_EVIDENCE}, RegulatoryVerificationReason.SOURCE_DISPUTED),
        ({"source_state": RegulatorySourceState.STALE_RESPONSE}, RegulatoryVerificationReason.EVIDENCE_STALE),
    ],
)
def test_tampering_forgery_scope_and_negative_source_states_deny(
    changes: dict[str, object], reason: RegulatoryVerificationReason
) -> None:
    """Prove digest, issuer, kind, tenant, actor, subject and source-state gates."""
    assert verify(source_capture=capture(**changes)).reason is reason


@pytest.mark.parametrize("status", [PrincipalStatus.SUSPENDED, PrincipalStatus.REVOKED])
def test_inactive_or_revoked_actor_denies(status: PrincipalStatus) -> None:
    """Prove only a current ACTIVE principal snapshot reaches source gates."""
    decision = verify(authority=PrincipalAuthority("verifier-a", status, 8))
    assert decision.reason is RegulatoryVerificationReason.ACTOR_INACTIVE


def test_self_attestation_and_attested_r62_document_deny() -> None:
    """Prove neither submitter identity nor R62 document review self-authenticates."""
    self_capture = capture(submitted_by_principal_id="practitioner-a")
    assert verify(source_capture=self_capture).reason is RegulatoryVerificationReason.SELF_ATTESTATION
    attested = evidence(verification_method="ATTESTED_DOCUMENT_REVIEW")
    assert verify(item=attested).reason is RegulatoryVerificationReason.SELF_ATTESTATION


@pytest.mark.parametrize(
    "checked_at", [NOW + timedelta(seconds=1), NOW - timedelta(days=2)]
)
def test_future_or_stale_capture_denies(checked_at: datetime) -> None:
    """Prove future observations and captures beyond governed age are stale."""
    decision = verify(source_capture=capture(checked_at=checked_at))
    assert decision.reason is RegulatoryVerificationReason.EVIDENCE_STALE
    assert decision.source_state is RegulatorySourceState.STALE_RESPONSE


def test_missing_kind_specific_freshness_policy_denies() -> None:
    """Prove absence of the applicable policy is not a permissive default."""
    decision = verify(freshness=policy(practising_status_max_age=None))
    assert decision.reason is RegulatoryVerificationReason.FRESHNESS_POLICY_UNKNOWN


@pytest.mark.parametrize(
    ("valid_until", "reason"),
    [
        (None, RegulatoryVerificationReason.FFC_SOURCE_VALIDITY_REQUIRED),
        (NOW, RegulatoryVerificationReason.FFC_SOURCE_VALIDITY_EXPIRED),
    ],
)
def test_ffc_requires_current_independent_source_validity(
    valid_until: datetime | None, reason: RegulatoryVerificationReason
) -> None:
    """Prove FFC capture age never substitutes for source-record validity."""
    kind = ProfessionalEvidenceKind.FIDELITY_FUND_CERTIFICATE_STATUS
    source = AUTHORITATIVE_PUBLIC_SOURCES[kind]
    item = evidence(
        evidence_kind=kind, issuer_source_id=source[0], source_uri=source[1]
    )
    source_capture = capture(
        evidence_kind=kind,
        issuer_source_id=source[0],
        source_uri=source[1],
        source_record_valid_until=valid_until,
    )
    assert verify(item=item, source_capture=source_capture).reason is reason


def test_claimed_cryptographic_authentication_denies_without_trust_root() -> None:
    """Prove a transport claim cannot manufacture a ratified regulator root."""
    decision = verify(
        source_capture=capture(
            source_state=RegulatorySourceState.AUTHENTICATED_RESPONSE,
            issuer_verification_state=IssuerVerificationState.CRYPTOGRAPHICALLY_VERIFIED,
        )
    )
    assert decision.reason is RegulatoryVerificationReason.AUTHENTICATED_ISSUER_TRUST_ROOT_UNAVAILABLE
    assert decision.ingestion_authorized is False


def test_unknown_issuer_verification_state_is_rejected() -> None:
    """Prove unknown provenance cannot enter the closed capture vocabulary."""
    with pytest.raises(RegulatorySourceVerificationError) as error:
        capture(issuer_verification_state="REGULATOR_SIGNED")
    assert error.value.code == "R64_SOURCE_ENUM_INVALID"


def test_exact_input_replay_identity_is_deterministic_and_semantically_bound() -> None:
    """Prove exact replay equality and changed capture identity inequality."""
    first = verify()
    second = verify()
    changed = verify(
        source_capture=capture(issuer_verification_reference="r64-verification-2")
    )
    assert first.replay_identity == second.replay_identity
    assert len(first.replay_identity) == 128
    assert changed.replay_identity != first.replay_identity


def test_decision_constructor_and_dataclass_replace_cannot_forge_authority() -> None:
    """Prove public construction and replacement cannot mint positive outcomes."""
    decision = verify()
    with pytest.raises(RegulatorySourceVerificationError) as direct:
        RegulatoryVerificationDecision()
    assert direct.value.code == "R64_VERIFICATION_DECISION_DIRECT_CONSTRUCTION_FORBIDDEN"
    with pytest.raises(RegulatorySourceVerificationError) as forged:
        replace(
            decision,
            reason=RegulatoryVerificationReason.R63_INGESTION_PERMISSION_UNAVAILABLE,
        )
    assert forged.value.code == "R64_VERIFICATION_DECISION_DIRECT_CONSTRUCTION_FORBIDDEN"
    with pytest.raises((AttributeError, TypeError)):
        setattr(decision, "ingestion_authorized", True)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_regulatory_source_verification.py
# VERSION: v1.0.0-R64-AUTHENTICATED-REGULATORY-VERIFICATION-CERT
# AUTHORITY BOUNDARY: pure adversarial non-ingesting verification certificate
# TENANT POSTURE: exact scope; cross-tenant inputs deny without disclosure
# FAIL-CLOSED POSTURE: forgery, tampering, stale, disputed, absent policy,
# unratified authentication, invalid FFC validity, and construction all deny
# PROFESSIONAL PRACTICE / MATTER ACCESS / REASSIGNMENT AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
