"""Direct certificate for L8-8D legal conflict screening evidence.

VERSION: v1.0.0-L8-8D-LEGAL-CONFLICT-SCREENING-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_conflict_screening.py
AUTHORITY BOUNDARY: Pure exact-subject screening semantics only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.domain.legal_conflict_screening import (
    SCREENING_FIELDS,
    LegalConflictMatchKind,
    LegalConflictMatchSignal,
    LegalConflictScreeningError,
    LegalConflictScreeningResult,
    LegalConflictScreeningStatus,
    build_legal_conflict_screening,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterParty,
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter


NOW = datetime(2026, 9, 25, 16, 0, tzinfo=timezone.utc)
FP_SUBJECT = "a" * 128
FP_EVIDENCE = "b" * 128
FP_OTHER = "c" * 128


def matter(tenant: str, matter_id: str) -> CaseMatter:
    return CaseMatter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_reference=f"REF-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"intake:{matter_id}",
    )


def party(
    *,
    tenant: str = "tenant-law",
    matter_id: str = "matter-1",
    party_id: str = "party-1",
    side: LegalMatterPartySide = LegalMatterPartySide.CLIENT_SIDE,
    subject_fp: str = FP_SUBJECT,
    display_name: str = "Acme Legal",
) -> LegalMatterParty:
    return register_legal_matter_party(
        matter=matter(tenant, matter_id),
        party_id=party_id,
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=side,
        matter_role=(
            LegalMatterPartyRole.CLIENT
            if side is LegalMatterPartySide.CLIENT_SIDE
            else LegalMatterPartyRole.RESPONDENT
        ),
        subject_reference="organization:acme",
        subject_identity_fingerprint=subject_fp,
        display_name=display_name,
        registered_at=NOW,
        source_evidence_reference=f"party-source:{party_id}",
        source_evidence_fingerprint=FP_EVIDENCE,
    )


def screening(
    source: LegalMatterParty,
    occurrences: tuple[LegalMatterParty, ...],
) -> LegalConflictScreeningResult:
    return build_legal_conflict_screening(
        source_party=source,
        occurrences=occurrences,
        screening_id="screening-1",
        screened_at=NOW,
        source_evidence_reference="screening-request:1",
        source_evidence_fingerprint=FP_EVIDENCE,
    )


def test_no_additional_exact_match_is_no_match_found_not_clearance() -> None:
    source = party()
    result = screening(source, (source,))
    assert result.status is LegalConflictScreeningStatus.NO_MATCH_FOUND
    assert result.matches == ()
    assert "CLEAR" not in result.status.value
    assert set(LegalConflictScreeningStatus) == {
        LegalConflictScreeningStatus.NO_MATCH_FOUND,
        LegalConflictScreeningStatus.REVIEW_REQUIRED,
    }


def test_cross_matter_same_side_match_requires_review() -> None:
    source = party()
    matched = party(
        matter_id="matter-2",
        party_id="party-2",
        side=LegalMatterPartySide.CLIENT_SIDE,
    )
    result = screening(source, (source, matched))
    assert result.status is LegalConflictScreeningStatus.REVIEW_REQUIRED
    assert len(result.matches) == 1
    assert (
        result.matches[0].match_kind
        is LegalConflictMatchKind.CROSS_MATTER_EXACT_SUBJECT_MATCH
    )


def test_cross_matter_client_adverse_match_is_opposing_side_signal() -> None:
    source = party()
    matched = party(
        matter_id="matter-2",
        party_id="party-2",
        side=LegalMatterPartySide.ADVERSE_SIDE,
    )
    result = screening(source, (matched, source))
    assert result.status is LegalConflictScreeningStatus.REVIEW_REQUIRED
    assert (
        result.matches[0].match_kind
        is LegalConflictMatchKind.OPPOSING_SIDE_EXACT_SUBJECT_MATCH
    )


def test_match_order_and_screening_fingerprint_are_deterministic() -> None:
    source = party()
    left = party(matter_id="matter-3", party_id="party-3")
    right = party(matter_id="matter-2", party_id="party-2")
    first = screening(source, (source, left, right))
    second = screening(source, (right, source, left))
    assert first == second
    assert first.fingerprint == second.fingerprint
    assert [
        item.matched_case_matter_id for item in first.matches
    ] == ["matter-2", "matter-3"]


def test_round_trip_verifies_exact_screening_integrity() -> None:
    source = party()
    matched = party(
        matter_id="matter-2",
        party_id="party-2",
        side=LegalMatterPartySide.ADVERSE_SIDE,
    )
    value = screening(source, (source, matched))
    payload = value.to_dict()
    assert set(payload) == set(SCREENING_FIELDS)
    assert LegalConflictScreeningResult.from_dict(payload) == value


def test_foreign_tenant_occurrence_rejects() -> None:
    source = party()
    foreign = party(
        tenant="tenant-other",
        matter_id="matter-2",
        party_id="party-2",
    )
    with pytest.raises(LegalConflictScreeningError) as raised:
        screening(source, (source, foreign))
    assert raised.value.code == "L8_8D_TENANT_MISMATCH"


def test_mismatched_subject_identity_rejects() -> None:
    source = party()
    other = party(
        matter_id="matter-2",
        party_id="party-2",
        subject_fp=FP_OTHER,
    )
    with pytest.raises(LegalConflictScreeningError) as raised:
        screening(source, (source, other))
    assert raised.value.code == "L8_8D_SUBJECT_IDENTITY_MISMATCH"


def test_same_matter_duplicate_subject_fact_rejects() -> None:
    source = party()
    duplicate = party(
        matter_id="matter-1",
        party_id="party-2",
    )
    with pytest.raises(LegalConflictScreeningError) as raised:
        screening(source, (source, duplicate))
    assert raised.value.code == "L8_8D_SAME_MATTER_SUBJECT_DUPLICATE"


def test_divergent_self_occurrence_rejects() -> None:
    source = party()
    divergent = party(
        matter_id="matter-1",
        party_id="party-1",
        display_name="Different Name",
    )
    with pytest.raises(LegalConflictScreeningError) as raised:
        screening(source, (divergent,))
    assert raised.value.code == "L8_8D_SOURCE_PARTY_DIVERGENCE"


def test_non_party_occurrence_rejects() -> None:
    source = party()
    with pytest.raises(LegalConflictScreeningError) as raised:
        build_legal_conflict_screening(
            source_party=source,
            occurrences=(source, object()),  # type: ignore[arg-type]
            screening_id="screening-1",
            screened_at=NOW,
            source_evidence_reference="screening-request:1",
            source_evidence_fingerprint=FP_EVIDENCE,
        )
    assert raised.value.code == "L8_8D_OCCURRENCE_INVALID"


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("screening_id", " screening-1", "L8_8D_SCREENING_ID_INVALID"),
        ("screened_at", datetime(2026, 9, 25, 16, 0), "L8_8D_SCREENED_AT_INVALID"),
        ("source_evidence_fingerprint", "A" * 128, "L8_8D_SOURCE_EVIDENCE_FINGERPRINT_INVALID"),
    ],
)
def test_screening_metadata_is_strict(
    field: str,
    value: object,
    code: str,
) -> None:
    source = party()
    inputs = {
        "source_party": source,
        "occurrences": (source,),
        "screening_id": "screening-1",
        "screened_at": NOW,
        "source_evidence_reference": "screening-request:1",
        "source_evidence_fingerprint": FP_EVIDENCE,
    }
    inputs[field] = value
    with pytest.raises(LegalConflictScreeningError) as raised:
        build_legal_conflict_screening(**inputs)  # type: ignore[arg-type]
    assert raised.value.code == code


def test_result_contains_no_display_name_or_raw_pii_fields() -> None:
    source = party(display_name="Sensitive Name")
    matched = party(
        matter_id="matter-2",
        party_id="party-2",
        display_name="Other Sensitive Name",
    )
    payload = screening(source, (source, matched)).to_dict()
    forbidden = {
        "display_name",
        "name",
        "email",
        "phone",
        "address",
        "id_number",
        "passport_number",
        "tax_number",
        "identifier",
        "description",
        "legal_advice",
        "clearance",
        "waiver",
        "resolution",
    }
    assert forbidden.isdisjoint(payload)
    assert forbidden.isdisjoint(payload["matches"][0])


def test_tampered_round_trip_fingerprint_rejects() -> None:
    source = party()
    matched = party(matter_id="matter-2", party_id="party-2")
    payload = screening(source, (source, matched)).to_dict()
    payload["screening_id"] = "screening-tampered"
    with pytest.raises(LegalConflictScreeningError) as raised:
        LegalConflictScreeningResult.from_dict(payload)
    assert raised.value.code == "L8_8D_FINGERPRINT_MISMATCH"


def test_status_and_match_cardinality_cannot_diverge() -> None:
    source = party()
    matched = party(matter_id="matter-2", party_id="party-2")
    valid = screening(source, (source, matched))
    with pytest.raises(LegalConflictScreeningError) as raised:
        replace(
            valid,
            status=LegalConflictScreeningStatus.NO_MATCH_FOUND,
            fingerprint="",
        )
    assert raised.value.code == "L8_8D_STATUS_MATCH_MISMATCH"


def test_duplicate_match_party_ids_reject() -> None:
    source = party()
    matched = party(matter_id="matter-2", party_id="party-2")
    valid = screening(source, (source, matched))
    with pytest.raises(LegalConflictScreeningError) as raised:
        replace(
            valid,
            matches=(valid.matches[0], valid.matches[0]),
            fingerprint="",
        )
    assert raised.value.code == "L8_8D_DUPLICATE_MATCH_INVALID"


def test_screening_result_and_match_signal_are_frozen() -> None:
    source = party()
    matched = party(matter_id="matter-2", party_id="party-2")
    result = screening(source, (source, matched))
    with pytest.raises(FrozenInstanceError):
        result.screening_id = "mutated"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.matches[0].matched_party_id = "mutated"  # type: ignore[misc]


# ARTIFACT: test_legal_conflict_screening.py
# VERSION: v1.0.0-L8-8D-LEGAL-CONFLICT-SCREENING-CERT
# AUTHORITY BOUNDARY: pure exact-subject screening evidence only
# TENANT POSTURE: source and occurrences must share exact tenant/subject identity
# FAIL-CLOSED POSTURE: no-match is never clearance; foreign/divergent/duplicate/tampered evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
