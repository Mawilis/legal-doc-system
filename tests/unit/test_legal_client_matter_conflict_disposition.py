"""Direct certificate for the pure L9B2 conflict-disposition domain.

TITLE: WILSY OS Legal Client Matter Conflict Disposition Certificate
VERSION: v1.0.0-L9B2-CONFLICT-DISPOSITION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify exact immutable disposition evidence without creating a
         registry, waiver, ethical wall, recusal, Engagement, Representation,
         Court or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_conflict_disposition.py
COLLABORATION / OWNERSHIP: L9B2 certifies only the pure value object;
                            currentness, IAM, mandate, Engagement and legacy
                            Node interlock remain future gates.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B2-CONFLICT-DISPOSITION-CERT certifies vocabulary,
           lineage, tenant/subject binding, chronology, strict hydration,
           deterministic integrity and fail-closed compatibility.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identities and fingerprints only;
                             no PII, credentials, tokens, network or Mongo.
TENANT BOUNDARY: Every fixture and assertion is exact tenant/matter/subject
                 scoped; no cross-tenant inference is permitted.
AUTHORITY BOUNDARY: Certificate evidence only; no test grants legal authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
TRANSACTION BOUNDARY: Pure in-memory unit tests only.
FAIL-CLOSED DECLARATION: Tampering, drift, incompatible review outcomes and
                         authority expansion must reject.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition import (
    DISPOSITION_FIELDS,
    SCHEMA,
    VERSION,
    LegalClientMatterConflictDisposition,
    LegalClientMatterConflictDispositionError,
    LegalClientMatterConflictDispositionType,
)
from tools.eos.legal_operations.domain.legal_conflict_review import (
    LegalConflictReviewOutcome,
    determine_legal_conflict_review,
)
from tools.eos.legal_operations.domain.legal_conflict_screening import (
    LegalConflictMatchKind,
    LegalConflictMatchSignal,
    LegalConflictScreeningResult,
    LegalConflictScreeningStatus,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter


BASE = datetime(2026, 9, 27, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-l9b2"
SUBJECT_FP = "a" * 128
MATCHED_FP = "b" * 128
EVIDENCE_FP = "c" * 128
AUTH_FP = "d" * 128
SUPPORT_FP = "e" * 128


def matter(*, tenant_id: str = TENANT, matter_id: str = "matter-l9b2") -> CaseMatter:
    return CaseMatter(
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        matter_reference="CASE-L9B2-001",
        opened_at=BASE,
        evidence_reference="matter-registration:l9b2",
    )


def party(*, source_matter: CaseMatter | None = None, party_id: str = "party-l9b2"):
    source = source_matter or matter()
    return register_legal_matter_party(
        matter=source,
        party_id=party_id,
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=LegalMatterPartySide.CLIENT_SIDE,
        matter_role=LegalMatterPartyRole.CLIENT,
        subject_reference="organization:client-l9b2",
        subject_identity_fingerprint=SUBJECT_FP,
        display_name="Synthetic client presentation",
        registered_at=BASE,
        source_evidence_reference="matter-party:l9b2",
        source_evidence_fingerprint=EVIDENCE_FP,
    )


def screening(*, source_matter: CaseMatter | None = None, status=LegalConflictScreeningStatus.REVIEW_REQUIRED):
    source = source_matter or matter()
    source_party = party(source_matter=source)
    matches = ()
    if status is LegalConflictScreeningStatus.REVIEW_REQUIRED:
        matches = (
            LegalConflictMatchSignal(
                tenant_id=source.tenant_id,
                subject_identity_fingerprint=SUBJECT_FP,
                source_party_id=source_party.party_id,
                source_case_matter_id=source.case_matter_id,
                source_party_fingerprint=source_party.fingerprint,
                matched_party_id="party-adverse-l9b2",
                matched_case_matter_id="matter-adverse-l9b2",
                matched_party_fingerprint=MATCHED_FP,
                match_kind=LegalConflictMatchKind.CROSS_MATTER_EXACT_SUBJECT_MATCH,
            ),
        )
    return LegalConflictScreeningResult(
        tenant_id=source.tenant_id,
        screening_id="screening-l9b2",
        source_party_id=source_party.party_id,
        source_case_matter_id=source.case_matter_id,
        source_party_fingerprint=source_party.fingerprint,
        subject_identity_fingerprint=SUBJECT_FP,
        screened_at=BASE + timedelta(minutes=1),
        status=status,
        matches=matches,
        source_evidence_reference="screening-evidence:l9b2",
        source_evidence_fingerprint=EVIDENCE_FP,
    )


def review_for(
    source: LegalConflictScreeningResult,
    outcome: LegalConflictReviewOutcome,
):
    return determine_legal_conflict_review(
        screening=source,
        review_id="review-l9b2",
        reviewer_principal_id="principal-reviewer-l9b2",
        reviewer_authorization_reference="iam-review:l9b2",
        reviewer_authorization_fingerprint=AUTH_FP,
        outcome=outcome,
        review_reason_reference="review-reason:l9b2",
        reviewed_at=BASE + timedelta(minutes=2),
        source_evidence_reference="review-evidence:l9b2",
        source_evidence_fingerprint=SUPPORT_FP,
    )


def bundle(
    *,
    outcome: LegalConflictReviewOutcome = LegalConflictReviewOutcome.NO_CONFLICT_IDENTIFIED,
    disposition: LegalClientMatterConflictDispositionType = LegalClientMatterConflictDispositionType.ENGAGEMENT_PERMITTED,
    screening_status: LegalConflictScreeningStatus = LegalConflictScreeningStatus.REVIEW_REQUIRED,
):
    source_matter = matter()
    source_party = party(source_matter=source_matter)
    source_screening = screening(source_matter=source_matter, status=screening_status)
    source_review = review_for(source_screening, outcome)
    value = LegalClientMatterConflictDisposition.from_canonical(
        disposition_id="disposition-l9b2",
        case_matter=source_matter,
        party=source_party,
        screening=source_screening,
        conflict_review=source_review,
        disposition=disposition,
        decision_actor_principal_id="principal-partner-l9b2",
        authorization_evidence_reference="iam-disposition:l9b2",
        authorization_evidence_fingerprint=AUTH_FP,
        supporting_evidence_reference="supporting-disposition:l9b2",
        supporting_evidence_fingerprint=SUPPORT_FP,
        occurred_at=BASE + timedelta(minutes=3),
        effective_from=BASE + timedelta(minutes=4),
        idempotency_key="idempotency:disposition-l9b2",
    )
    return value, source_matter, source_party, source_screening, source_review


def test_valid_permitted_requires_explicit_disposition_over_no_conflict() -> None:
    value, _, _, _, review = bundle()
    assert value.disposition is LegalClientMatterConflictDispositionType.ENGAGEMENT_PERMITTED
    assert review.outcome is LegalConflictReviewOutcome.NO_CONFLICT_IDENTIFIED
    assert value.conflict_review_id == review.review_id
    assert len(value.fingerprint) == 128


@pytest.mark.parametrize(
    "disposition",
    [
        LegalClientMatterConflictDispositionType.ENGAGEMENT_PROHIBITED,
        LegalClientMatterConflictDispositionType.ENGAGEMENT_UNRESOLVED,
    ],
)
def test_bounded_non_permitted_decisions_are_constructible(disposition) -> None:
    value, *_ = bundle(disposition=disposition)
    assert value.disposition is disposition


@pytest.mark.parametrize(
    "outcome,disposition",
    [
        (LegalConflictReviewOutcome.CONFLICT_IDENTIFIED, LegalClientMatterConflictDispositionType.ENGAGEMENT_PERMITTED),
        (LegalConflictReviewOutcome.ESCALATION_REQUIRED, LegalClientMatterConflictDispositionType.ENGAGEMENT_PERMITTED),
    ],
)
def test_identified_or_escalated_review_cannot_permit_engagement(outcome, disposition) -> None:
    with pytest.raises(LegalClientMatterConflictDispositionError) as raised:
        bundle(outcome=outcome, disposition=disposition)
    assert raised.value.code == "L9B2_REVIEW_DISPOSITION_INCOMPATIBLE"


def test_identified_conflict_allows_only_prohibited_or_unresolved() -> None:
    for decision in (
        LegalClientMatterConflictDispositionType.ENGAGEMENT_PROHIBITED,
        LegalClientMatterConflictDispositionType.ENGAGEMENT_UNRESOLVED,
    ):
        value, *_ = bundle(
            outcome=LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
            disposition=decision,
        )
        assert value.disposition is decision


def test_escalation_allows_only_unresolved() -> None:
    value, *_ = bundle(
        outcome=LegalConflictReviewOutcome.ESCALATION_REQUIRED,
        disposition=LegalClientMatterConflictDispositionType.ENGAGEMENT_UNRESOLVED,
    )
    assert value.disposition is LegalClientMatterConflictDispositionType.ENGAGEMENT_UNRESOLVED


def test_no_match_review_can_explicitly_remain_unresolved_or_permit() -> None:
    permitted, *_ = bundle(screening_status=LegalConflictScreeningStatus.NO_MATCH_FOUND)
    unresolved, *_ = bundle(
        screening_status=LegalConflictScreeningStatus.NO_MATCH_FOUND,
        disposition=LegalClientMatterConflictDispositionType.ENGAGEMENT_UNRESOLVED,
    )
    assert permitted.disposition is LegalClientMatterConflictDispositionType.ENGAGEMENT_PERMITTED
    assert unresolved.disposition is LegalClientMatterConflictDispositionType.ENGAGEMENT_UNRESOLVED


def test_frozen_and_exact_bindings_are_present() -> None:
    value, source_matter, source_party, source_screening, source_review = bundle()
    assert value.tenant_id == source_matter.tenant_id
    assert value.case_matter_id == source_matter.case_matter_id
    assert value.matter_fingerprint == source_matter.fingerprint
    assert value.screening_id == source_screening.screening_id
    assert value.screening_fingerprint == source_screening.fingerprint
    assert value.conflict_review_id == source_review.review_id
    assert value.conflict_review_fingerprint == source_review.fingerprint
    assert value.client_party_id == source_party.party_id
    assert value.subject_identity_fingerprint == source_party.subject_identity_fingerprint
    with pytest.raises(FrozenInstanceError):
        value.disposition_id = "other"  # type: ignore[misc]


def test_two_chronology_fields_are_utc_and_microsecond_preserving() -> None:
    value, *_ = bundle()
    assert value.occurred_at.tzinfo is timezone.utc
    assert value.effective_from.tzinfo is timezone.utc
    assert value.occurred_at.microsecond == 123456
    assert value.effective_from >= value.occurred_at


def test_deterministic_fingerprint_and_exact_hydration() -> None:
    value, *_ = bundle()
    hydrated = LegalClientMatterConflictDisposition.from_dict(value.to_dict())
    assert hydrated == value
    assert set(value.to_dict()) == DISPOSITION_FIELDS
    changed = value.to_dict()
    changed["supporting_evidence_reference"] = "supporting-disposition:changed"
    changed["fingerprint"] = value.fingerprint
    with pytest.raises(LegalClientMatterConflictDispositionError) as raised:
        LegalClientMatterConflictDisposition.from_dict(changed)
    assert raised.value.code == "L9B2_FINGERPRINT_MISMATCH"


def test_schema_and_fingerprint_tampering_reject() -> None:
    value, *_ = bundle()
    for field, replacement in (("schema", "other-schema"), ("disposition_version", "other-version")):
        payload = value.to_dict()
        payload[field] = replacement
        with pytest.raises(LegalClientMatterConflictDispositionError):
            LegalClientMatterConflictDisposition.from_dict(payload)
    payload = value.to_dict()
    payload["fingerprint"] = "0" * 128
    with pytest.raises(LegalClientMatterConflictDispositionError) as raised:
        LegalClientMatterConflictDisposition.from_dict(payload)
    assert raised.value.code == "L9B2_FINGERPRINT_MISMATCH"


def test_strict_hydration_rejects_missing_extra_unknown_and_invalid_values() -> None:
    value, *_ = bundle()
    for mutation in (
        lambda payload: payload.pop("screening_id"),
        lambda payload: payload.__setitem__("unexpected", "value"),
        lambda payload: payload.__setitem__("disposition", "WAIVED"),
        lambda payload: payload.__setitem__("screening_fingerprint", "not-hex"),
        lambda payload: payload.__setitem__("occurred_at", "2026-09-27T12:00:00"),
    ):
        payload = value.to_dict()
        mutation(payload)
        with pytest.raises(LegalClientMatterConflictDispositionError):
            LegalClientMatterConflictDisposition.from_dict(payload)


@pytest.mark.parametrize("field", ["tenant_id", "case_matter_id", "screening_id", "conflict_review_id", "client_party_id"])
def test_factory_rejects_cross_scope_or_lineage(field: str) -> None:
    value, source_matter, source_party, source_screening, source_review = bundle()
    kwargs: dict[str, Any] = dict(
        disposition_id="disposition-other",
        case_matter=source_matter,
        party=source_party,
        screening=source_screening,
        conflict_review=source_review,
        disposition=LegalClientMatterConflictDispositionType.ENGAGEMENT_PERMITTED,
        decision_actor_principal_id="principal-partner-l9b2",
        authorization_evidence_reference="iam-disposition:l9b2",
        authorization_evidence_fingerprint=AUTH_FP,
        supporting_evidence_reference="supporting-disposition:l9b2",
        supporting_evidence_fingerprint=SUPPORT_FP,
        occurred_at=BASE + timedelta(minutes=3),
        effective_from=BASE + timedelta(minutes=4),
        idempotency_key="idempotency:other",
    )
    if field == "tenant_id":
        kwargs["case_matter"] = matter(tenant_id="tenant-other")
    elif field == "case_matter_id":
        kwargs["case_matter"] = matter(matter_id="matter-other")
    elif field == "screening_id":
        kwargs["screening"] = replace(
            source_screening,
            screening_id="screening-other",
            fingerprint="",
        )
    elif field == "conflict_review_id":
        other_screening = replace(
            source_screening,
            screening_id="screening-other",
            fingerprint="",
        )
        kwargs["conflict_review"] = review_for(
            other_screening,
            LegalConflictReviewOutcome.NO_CONFLICT_IDENTIFIED,
        )
    else:
        kwargs["party"] = party(source_matter=source_matter, party_id="party-other")
    with pytest.raises(LegalClientMatterConflictDispositionError):
        LegalClientMatterConflictDisposition.from_canonical(**kwargs)


def test_mismatched_review_lineage_and_subject_reject() -> None:
    value, source_matter, source_party, source_screening, source_review = bundle()
    other_screening = replace(
        source_screening,
        screening_id="screening-other",
        fingerprint="",
    )
    with pytest.raises(LegalClientMatterConflictDispositionError) as raised:
        LegalClientMatterConflictDisposition.from_canonical(
            disposition_id="disposition-mismatch",
            case_matter=source_matter,
            party=source_party,
            screening=other_screening,
            conflict_review=source_review,
            disposition=LegalClientMatterConflictDispositionType.ENGAGEMENT_UNRESOLVED,
            decision_actor_principal_id="principal-partner-l9b2",
            authorization_evidence_reference="iam-disposition:l9b2",
            authorization_evidence_fingerprint=AUTH_FP,
            supporting_evidence_reference="supporting-disposition:l9b2",
            supporting_evidence_fingerprint=SUPPORT_FP,
            occurred_at=BASE + timedelta(minutes=3),
            effective_from=BASE + timedelta(minutes=4),
            idempotency_key="idempotency:mismatch",
        )
    assert raised.value.code == "L9B2_REVIEW_CORRELATION_MISMATCH"


def test_effective_time_cannot_precede_occurrence() -> None:
    value, *_ = bundle()
    payload = value.to_dict()
    payload["effective_from"] = BASE.isoformat().replace("+00:00", "Z")
    payload["occurred_at"] = (BASE + timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
    payload.pop("fingerprint")
    with pytest.raises(LegalClientMatterConflictDispositionError):
        LegalClientMatterConflictDisposition(**payload)  # type: ignore[arg-type]


def test_public_artifact_excludes_forbidden_authorities_and_pii() -> None:
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_conflict_disposition.py").read_text()
    tree = ast.parse(source)
    imports = {
        node.names[0].name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
    }
    assert "pymongo" not in imports
    assert "requests" not in imports
    assert "server.models.Conflict" not in source
    assert "waiver" in source.lower()
    assert "ethical wall" in source.lower()
    assert "recusal" in source.lower()
    assert "financial" in source.lower()
    assert "TODO" not in source
    assert "FIXME" not in source
    assert "PII_REQUIRED" not in source


def test_constants_and_authority_exclusions_are_explicit() -> None:
    assert VERSION == "v1.0.0-L9B2-CONFLICT-DISPOSITION"
    assert SCHEMA == "WILSY-LEGAL-CLIENT-MATTER-CONFLICT-DISPOSITION/V1"
    assert {item.value for item in LegalClientMatterConflictDispositionType} == {
        "ENGAGEMENT_PERMITTED",
        "ENGAGEMENT_PROHIBITED",
        "ENGAGEMENT_UNRESOLVED",
    }
    assert all(
        forbidden not in LegalClientMatterConflictDispositionType.__members__
        for forbidden in ("WAIVED", "ETHICAL_WALL", "RECUSED", "CLEARED", "CONSENTED")
    )


# ARTIFACT: test_legal_client_matter_conflict_disposition.py
# VERSION: v1.0.0-L9B2-CONFLICT-DISPOSITION-CERT
# AUTHORITY BOUNDARY: pure-domain certification evidence only
# FAIL-CLOSED POSTURE: no authority expansion and no external side effects
# END OF WILSY OS SOVEREIGN ARTIFACT
