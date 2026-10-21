"""TITLE: R62 Practitioner Professional Standing Evidence Certificate.
VERSION: v1.0.0-R62-INSTITUTIONAL-PROFESSIONAL-EVIDENCE-CERT
AUTHORITY: Direct adversarial certificate for evidence-only Python/EOS scope.
EPITOME: Prove immutable provenance, strict scope, stale/revoked/contradictory
    denial, unsupported-jurisdiction denial, and permanent non-authorization.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_practitioner_professional_standing_evidence.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Governance and Legal Operations.
CERTIFICATION / UPDATE DATE: 2026-10-21
CHANGELOG:
    2026-10-21 v1.0.0-R62-INSTITUTIONAL-PROFESSIONAL-EVIDENCE-CERT
    Establishes the direct R62 adversarial evidence-only certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no client data.
TENANT BOUNDARY: Cross-tenant evidence must deny without disclosure.
AUTHORITY BOUNDARY: Tests no professional, reviewer, confidentiality, access,
    supervision, approval, reassignment, persistence, or execution authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.legal_practitioner_professional_standing_evidence import (
    RATIFICATION_DECISIONS_REQUIRED,
    LegalPractitionerProfessionalStandingEvidence,
    OperationalAccessRatificationDecision,
    ProfessionalEvidenceKind,
    ProfessionalStandingCurrentnessState,
    ProfessionalStandingEvidenceError,
    project_professional_standing_currentness,
)


NOW = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)


def record(**overrides: object) -> LegalPractitionerProfessionalStandingEvidence:
    values: dict[str, object] = {
        "evidence_id": "professional-evidence-1",
        "tenant_id": "tenant-a",
        "practitioner_principal_id": "principal-a",
        "verified_subject_id": "lpc-subject-106800",
        "issuer_source_id": "legal-practice-council-public-directory",
        "jurisdiction": "ZA",
        "evidence_kind": "PRACTISING_STATUS",
        "outcome": "VERIFIED_CURRENT",
        "verification_method": "PUBLIC_WEB_OBSERVATION",
        "evidence_reference": "observation-r62-1",
        "source_uri": "https://lpc.org.za/members-of-the-public/search-practitioners/",
        "observed_at": NOW,
        "valid_until": NOW + timedelta(days=1),
    }
    values.update(overrides)
    return LegalPractitionerProfessionalStandingEvidence(**values)  # type: ignore[arg-type]


def project(*items: LegalPractitionerProfessionalStandingEvidence, **overrides: object):
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "practitioner_principal_id": "principal-a",
        "jurisdiction": "ZA",
        "evidence_kind": ProfessionalEvidenceKind.PRACTISING_STATUS,
        "evaluation_time": NOW,
        "evidence": items,
    }
    values.update(overrides)
    return project_professional_standing_currentness(**values)  # type: ignore[arg-type]


def test_evidence_is_immutable_and_sha3_512_deterministic() -> None:
    item = record()
    assert len(item.fingerprint) == 128
    assert item.fingerprint == record().fingerprint
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        setattr(item, "outcome", "REVOKED")


def test_provenance_tampering_is_corrupt_blocked() -> None:
    item = record()
    object.__setattr__(item, "source_uri", "https://attacker.invalid/")
    assert project(item).state is ProfessionalStandingCurrentnessState.CORRUPT_BLOCKED


def test_duplicate_reference_is_blocked() -> None:
    second = record(evidence_id="professional-evidence-2")
    assert project(record(), second).state is ProfessionalStandingCurrentnessState.DUPLICATE_BLOCKED


def test_contradictory_current_evidence_is_blocked() -> None:
    negative = record(
        evidence_id="professional-evidence-2",
        evidence_reference="observation-r62-2",
        outcome="NOT_CURRENT",
    )
    assert project(record(), negative).state is ProfessionalStandingCurrentnessState.CONTRADICTORY_BLOCKED


def test_wrong_tenant_is_scope_mismatch_blocked() -> None:
    assert project(record(tenant_id="tenant-b")).state is ProfessionalStandingCurrentnessState.SCOPE_MISMATCH_BLOCKED


def test_expired_evidence_is_blocked() -> None:
    current = project(record(), evaluation_time=NOW + timedelta(days=2))
    assert current.state is ProfessionalStandingCurrentnessState.EXPIRED_BLOCKED


def test_revoked_evidence_is_blocked() -> None:
    item = record(outcome="REVOKED", revoked_at=NOW)
    assert project(item).state is ProfessionalStandingCurrentnessState.REVOKED_BLOCKED


def test_unsupported_jurisdiction_is_blocked() -> None:
    current = project(record(jurisdiction="GB"), jurisdiction="GB")
    assert current.state is ProfessionalStandingCurrentnessState.UNSUPPORTED_JURISDICTION_BLOCKED


def test_unverified_observation_never_becomes_allow() -> None:
    current = project(record(outcome="UNVERIFIED"))
    assert current.state is ProfessionalStandingCurrentnessState.UNVERIFIED_BLOCKED
    assert current.permits_operational_access is False


def test_verified_observation_remains_documentary_only() -> None:
    current = project(record())
    assert current.state is ProfessionalStandingCurrentnessState.VERIFIED_DOCUMENTARY_ONLY
    assert current.permits_operational_access is False
    assert current.permits_reassignment_execution is False


def test_professional_status_and_ffc_are_not_interchangeable() -> None:
    ffc = record(evidence_kind="FIDELITY_FUND_CERTIFICATE_STATUS")
    assert project(ffc).state is ProfessionalStandingCurrentnessState.SCOPE_MISMATCH_BLOCKED


def test_missing_evidence_is_not_positive_eligibility() -> None:
    assert project().state is ProfessionalStandingCurrentnessState.NO_EVIDENCE


@pytest.mark.parametrize(
    "field,value",
    [
        ("tenant_id", "default"),
        ("jurisdiction", "za"),
        ("verified_subject_id", ""),
        ("source_uri", " LPC "),
        ("observed_at", NOW.replace(tzinfo=None)),
        ("valid_until", NOW),
        ("outcome", "ALLOW"),
    ],
)
def test_noncanonical_or_authority_inventing_input_is_rejected(field: str, value: object) -> None:
    with pytest.raises(ProfessionalStandingEvidenceError):
        record(**{field: value})


def test_revocation_requires_time() -> None:
    with pytest.raises(ProfessionalStandingEvidenceError) as error:
        record(outcome="REVOKED")
    assert error.value.code == "REVOCATION_TIME_REQUIRED"


def test_lack_of_reviewer_acknowledgment_and_supervision_remains_explicit() -> None:
    current = project(record())
    required = set(current.ratification_decisions_required)
    assert required == set(RATIFICATION_DECISIONS_REQUIRED)
    assert OperationalAccessRatificationDecision.REVIEWER_ELIGIBILITY_AND_APPROVAL_AUTHORITY in required
    assert OperationalAccessRatificationDecision.CURRENT_ACKNOWLEDGMENT_AUTHORITY in required
    assert OperationalAccessRatificationDecision.SUPERVISION_APPROVAL_AUTHORITY in required
    assert OperationalAccessRatificationDecision.ETHICAL_WALL_CLEARANCE_AUTHORITY in required
    assert OperationalAccessRatificationDecision.OPERATIONAL_ACCESS_ISSUANCE_AUTHORITY in required


def test_caller_cannot_supply_access_or_review_authority_fields() -> None:
    for field in (
        "reviewer_authorized", "acknowledged", "supervision_approved",
        "ethical_wall_cleared", "operational_access_allowed",
    ):
        with pytest.raises(TypeError):
            record(**{field: True})


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_professional_standing_evidence.py
# VERSION: v1.0.0-R62-INSTITUTIONAL-PROFESSIONAL-EVIDENCE-CERT
# AUTHORITY BOUNDARY: adversarial evidence-only certificate; no access grant
# TENANT POSTURE: exact tenant; cross-tenant evidence denies
# FAIL-CLOSED POSTURE: all missing or invalid prerequisites remain blocked
# REASSIGNMENT / FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
