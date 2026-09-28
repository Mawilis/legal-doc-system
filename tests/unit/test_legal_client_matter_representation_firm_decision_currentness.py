"""Direct certificate for L9C11-P22 firm Representation decision currentness.

TITLE: WILSY OS Legal Firm Representation Decision Currentness Certificate
VERSION: v1.0.0-L9C11-P22-FIRM-REPRESENTATION-DECISION-CURRENTNESS-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify pure exact-lineage P2 projection, explicit-time behavior,
         duplicate normalization, ambiguity, corruption blocking, deterministic
         integrity and authority-boundary exclusions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_representation_firm_decision_currentness.py
COLLABORATION / OWNERSHIP: P2 and P9 remain read-only precedents. This test
                            exercises only the P22 pure domain.
CERTIFICATION / UPDATE DATE: 2026-09-28
TRANSACTION BOUNDARY: Pure in-memory synthetic values; no network or Mongo.
FAIL-CLOSED DECLARATION: Invalid, cross-lineage, contradictory or corrupt
                         evidence never becomes accepted currentness.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from itertools import permutations
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    LegalClientMatterRepresentationAuthority,
    LegalClientMatterRepresentationAuthorityDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import (
    LegalClientMatterRepresentationFirmDecision,
    LegalClientMatterRepresentationFirmDecisionType,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision_currentness import (
    CURRENTNESS_FIELDS,
    SCHEMA,
    VERSION,
    LegalClientMatterRepresentationFirmDecisionCurrentness,
    LegalClientMatterRepresentationFirmDecisionCurrentnessError,
    LegalClientMatterRepresentationFirmDecisionCurrentnessState,
    project_legal_client_matter_representation_firm_decision_currentness,
)


BASE = datetime(2026, 9, 28, 10, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-l9c11-p22"
MATTER = "matter-l9c11-p22"
PARTY = "party-l9c11-p22"
SUBJECT = "b" * 128
MATTER_FP = "a" * 128
AUTHORITY_FP = "c" * 128


def authority(**overrides: object) -> LegalClientMatterRepresentationAuthority:
    """Build one valid immutable P1 authority for synthetic P2 values."""
    values: dict[str, object] = {
        "authority_id": "authority-l9c11-p22",
        "tenant_id": TENANT,
        "case_matter_id": MATTER,
        "matter_fingerprint": MATTER_FP,
        "client_party_id": PARTY,
        "subject_reference": "client:subject-l9c11-p22",
        "subject_identity_fingerprint": SUBJECT,
        "engagement_id": "engagement-l9c11-p22",
        "engagement_fingerprint": "d" * 128,
        "mandate_id": "mandate-l9c11-p22",
        "mandate_fingerprint": "e" * 128,
        "mandate_scope_reference": "scope:l9c11:p22",
        "mandate_scope_fingerprint": "f" * 128,
        "mandate_capabilities": ("ADVISORY", "NEGOTIATION"),
        "acting_capacity_id": "capacity-l9c11-p22",
        "acting_capacity_fingerprint": "1" * 128,
        "representative_principal_id": "principal-l9c11-p22",
        "representative_role": "LEGAL_PRACTITIONER",
        "representation_scope_capabilities": ("ADVISORY",),
        "decision": LegalClientMatterRepresentationAuthorityDecision.APPOINTED,
        "appointing_principal_id": "principal-client-l9c11-p22",
        "source_evidence_reference": "evidence:appointment-p22",
        "source_evidence_fingerprint": "2" * 128,
        "authorization_evidence_reference": "evidence:authorization-p22",
        "authorization_evidence_fingerprint": "3" * 128,
        "occurred_at": BASE,
        "effective_from": BASE,
        "effective_until": BASE + timedelta(days=30),
        "idempotency_key": "idempotency:appointment-p22",
    }
    values.update(overrides)
    return LegalClientMatterRepresentationAuthority(**cast(Any, values))


def decision(
    *,
    source_authority: LegalClientMatterRepresentationAuthority | None = None,
    decision_value: str = "ACCEPTED",
    suffix: str = "one",
    effective_from: datetime = BASE,
    **overrides: object,
) -> LegalClientMatterRepresentationFirmDecision:
    """Build one canonical P2 value through its public constructor."""
    source_authority = source_authority or authority()
    values: dict[str, object] = {
        "client_authority": source_authority,
        "decision": decision_value,
        "decision_actor_principal_id": f"principal-firm-{suffix}",
        "authorization_evidence_reference": f"evidence:firm-authorization-{suffix}",
        "authorization_evidence_fingerprint": AUTHORITY_FP,
        "source_evidence_reference": f"evidence:firm-decision-{suffix}",
        "source_evidence_fingerprint": "4" * 128,
        "occurred_at": effective_from,
        "effective_from": effective_from,
        "idempotency_key": f"idempotency:firm-decision-{suffix}",
    }
    values.update(overrides)
    return LegalClientMatterRepresentationFirmDecision.from_client_authority(**cast(Any, values))


def project(
    values: tuple[LegalClientMatterRepresentationFirmDecision, ...],
    *,
    at: datetime = BASE + timedelta(hours=1),
    **context: object,
) -> LegalClientMatterRepresentationFirmDecisionCurrentness:
    """Project synthetic P2 values through the public P22 function."""
    return project_legal_client_matter_representation_firm_decision_currentness(
        tenant_id=cast(str, context.get("tenant_id", TENANT)),
        case_matter_id=cast(str, context.get("case_matter_id", MATTER)),
        matter_fingerprint=cast(str, context.get("matter_fingerprint", MATTER_FP)),
        client_party_id=cast(str, context.get("client_party_id", PARTY)),
        subject_identity_fingerprint=cast(str, context.get("subject_identity_fingerprint", SUBJECT)),
        representation_authority_id=cast(str, context.get("representation_authority_id", "authority-l9c11-p22")),
        representation_authority_fingerprint=cast(str, context.get("representation_authority_fingerprint", authority().fingerprint)),
        representative_principal_id=cast(str, context.get("representative_principal_id", "principal-l9c11-p22")),
        representative_role=cast(str, context.get("representative_role", "LEGAL_PRACTITIONER")),
        evaluated_at=at,
        decisions=values,
    )


def test_version_schema_states_immutability_and_fields() -> None:
    result = project(())
    assert VERSION == "v1.0.0-L9C11-P22-FIRM-REPRESENTATION-DECISION-CURRENTNESS"
    assert SCHEMA == "WILSY-LEGAL-CLIENT-MATTER-REPRESENTATION-FIRM-DECISION-CURRENTNESS/V1"
    assert set(result.to_dict()) == set(CURRENTNESS_FIELDS)
    assert [item.value for item in LegalClientMatterRepresentationFirmDecisionCurrentnessState] == [
        "NO_DECISION", "ACCEPTED", "DECLINED", "REQUIRES_REVIEW", "AMBIGUOUS", "CORRUPT_BLOCKED"
    ]
    with pytest.raises(FrozenInstanceError):
        setattr(result, "state", "ACCEPTED")


def test_explicit_aware_time_and_zero_clock_reads() -> None:
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionCurrentnessError):
        project((), at=datetime(2026, 9, 28, 10, 0))
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_representation_firm_decision_currentness.py").read_text()
    assert "datetime.now" not in source
    assert "datetime.utcnow" not in source


def test_empty_history_is_no_decision() -> None:
    result = project(())
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.NO_DECISION
    assert result.candidate_decision_ids == ()


def test_single_accepted_binds_exact_p2_p1_representative_and_scope() -> None:
    value = decision()
    result = project((value,))
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.ACCEPTED
    assert result.is_currently_accepted is True
    assert result.decisive_decision_id == value.decision_id
    assert result.decisive_decision_fingerprint == value.fingerprint
    assert result.representation_authority_id == value.representation_authority_id
    assert result.representation_authority_fingerprint == value.representation_authority_fingerprint
    assert result.representative_principal_id == value.representative_principal_id
    assert result.decisive_representation_scope_capabilities == value.representation_scope_capabilities


@pytest.mark.parametrize("decision_value,expected", [("DECLINED", "DECLINED"), ("REQUIRES_REVIEW", "REQUIRES_REVIEW")])
def test_single_non_positive_state_hides_selected_p2(decision_value: str, expected: str) -> None:
    result = project((decision(decision_value=decision_value),))
    assert str(getattr(result.state, "value", result.state)) == expected
    assert result.is_currently_accepted is False
    assert result.decisive_decision_id is None
    assert result.decisive_decision_fingerprint is None


def test_only_accepted_is_positive() -> None:
    assert project((decision(),)).is_usable is True
    assert project((decision(decision_value="DECLINED"),)).is_usable is False
    assert project((decision(decision_value="REQUIRES_REVIEW"),)).is_usable is False


@pytest.mark.parametrize("decision_value", ["ACCEPTED", "DECLINED", "REQUIRES_REVIEW"])
def test_future_rows_are_excluded(decision_value: str) -> None:
    future = BASE + timedelta(days=1)
    result = project((decision(decision_value=decision_value, effective_from=future),), at=BASE)
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.NO_DECISION
    assert result.normalized_decision_count == 1


@pytest.mark.parametrize("decision_value", ["ACCEPTED", "DECLINED", "REQUIRES_REVIEW"])
def test_exact_duplicates_are_one_semantic_decision(decision_value: str) -> None:
    value = decision(decision_value=decision_value)
    result = project((value, value, value))
    assert result.normalized_decision_count == 1
    assert result.eligible_decision_count == 1
    assert str(getattr(result.state, "value", result.state)) == decision_value


@pytest.mark.parametrize(
    "left,right", [("ACCEPTED", "ACCEPTED"), ("ACCEPTED", "DECLINED"), ("ACCEPTED", "REQUIRES_REVIEW"), ("DECLINED", "REQUIRES_REVIEW"), ("DECLINED", "DECLINED")],
)
def test_distinct_eligible_rows_are_ambiguous_without_precedence(left: str, right: str) -> None:
    result = project((decision(decision_value=left, suffix="left"), decision(decision_value=right, suffix="right")))
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.AMBIGUOUS
    assert result.is_currently_accepted is False


def test_later_effective_row_does_not_supersede_earlier() -> None:
    result = project((decision(suffix="early", effective_from=BASE + timedelta(minutes=1)), decision(decision_value="DECLINED", suffix="late", effective_from=BASE + timedelta(minutes=2))), at=BASE + timedelta(minutes=3))
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.AMBIGUOUS


def test_same_effective_distinct_rows_are_ambiguous() -> None:
    result = project((decision(suffix="a"), decision(suffix="b")))
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.AMBIGUOUS


def test_p1_authority_identity_difference_isolated() -> None:
    other = authority(authority_id="authority-other")
    result = project((decision(source_authority=other),))
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.CORRUPT_BLOCKED


@pytest.mark.parametrize(
    "field,value",
    [
        ("tenant_id", "tenant-other"),
        ("case_matter_id", "matter-other"),
        ("client_party_id", "party-other"),
        ("subject_identity_fingerprint", "9" * 128),
        ("representation_authority_fingerprint", "8" * 128),
    ],
)
def test_every_exact_lineage_mismatch_is_corrupt_blocked(field: str, value: str) -> None:
    context: dict[str, object] = {}
    if field == "representation_authority_fingerprint":
        candidate = decision()
        context[field] = value
    else:
        candidate = decision()
        object.__setattr__(candidate, field, value)
    result = project((candidate,), **cast(Any, context))
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.CORRUPT_BLOCKED


def test_representative_principal_and_role_difference_isolated() -> None:
    other = authority(representative_principal_id="principal-other", representative_role="COUNSEL")
    result = project((decision(source_authority=other),))
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.CORRUPT_BLOCKED


def test_scope_difference_is_distinct_truth() -> None:
    broad = authority(representation_scope_capabilities=("ADVISORY", "NEGOTIATION"))
    left = decision(source_authority=broad, suffix="left")
    right = decision(source_authority=broad, suffix="right", representation_scope_capabilities=("ADVISORY",))
    result = project((left, right), representation_authority_id=broad.authority_id, representation_authority_fingerprint=broad.fingerprint)
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.AMBIGUOUS
    assert len(result.candidate_decision_fingerprints) == 2


def test_corrupt_type_and_mixed_valid_corrupt_fail_closed() -> None:
    blocked = project((cast(Any, object()),))
    assert blocked.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.CORRUPT_BLOCKED
    corrupt = cast(Any, decision())
    object.__setattr__(corrupt, "fingerprint", "not-a-fingerprint")
    mixed = project((decision(), corrupt))
    assert mixed.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.CORRUPT_BLOCKED


def test_divergent_duplicate_decision_id_is_corrupt() -> None:
    first = decision(suffix="one")
    second = decision(suffix="two")
    object.__setattr__(second, "decision_id", first.decision_id)
    result = project((first, second))
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.CORRUPT_BLOCKED


def test_divergent_duplicate_fingerprint_is_corrupt() -> None:
    first = decision(suffix="one")
    second = decision(suffix="two")
    object.__setattr__(second, "fingerprint", first.fingerprint)
    result = project((first, second))
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.CORRUPT_BLOCKED


def test_non_positive_projection_retains_only_unselected_candidate_evidence() -> None:
    result = project((decision(decision_value="DECLINED"),))
    assert result.candidate_decision_ids
    assert result.decisive_decision is None
    assert result.decisive_representation_scope_capabilities == ()


def test_future_and_current_rows_are_evaluated_at_supplied_boundary() -> None:
    current = decision(effective_from=BASE)
    future = decision(suffix="future", effective_from=BASE + timedelta(hours=2))
    result = project((current, future), at=BASE + timedelta(hours=1))
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.ACCEPTED
    assert result.candidate_decision_ids == (current.decision_id,)


def test_order_independence_and_deterministic_fingerprint() -> None:
    values = (decision(suffix="a"), decision(decision_value="DECLINED", suffix="b"), decision(suffix="future", effective_from=BASE + timedelta(days=1)))
    results = [project(order) for order in permutations(values)]
    assert all(item == results[0] for item in results)
    assert all(item.fingerprint == results[0].fingerprint for item in results)


def test_serialization_hydration_and_strict_schema() -> None:
    result = project((decision(),))
    assert LegalClientMatterRepresentationFirmDecisionCurrentness.from_dict(result.to_dict()) == result
    invalid = result.to_dict(); invalid["unexpected"] = True
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionCurrentnessError):
        LegalClientMatterRepresentationFirmDecisionCurrentness.from_dict(invalid)
    tampered = result.to_dict(); tampered["state"] = "DECLINED"
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionCurrentnessError):
        LegalClientMatterRepresentationFirmDecisionCurrentness.from_dict(tampered)


def test_no_lifecycle_or_downstream_authority_is_created() -> None:
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_representation_firm_decision_currentness.py").read_text()
    tree = ast.parse(source)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert "datetime" in names
    assert "revocation" in source.lower()
    assert "supersession" in source.lower()
    assert "latest-wins" in source.lower()
    assert "MongoClient" not in source
    assert "RepresentationFirmDecisionRegistry" not in source


# ARTIFACT: test_legal_client_matter_representation_firm_decision_currentness.py
# VERSION: v1.0.0-L9C11-P22-FIRM-REPRESENTATION-DECISION-CURRENTNESS-CERT
# AUTHORITY BOUNDARY: direct pure-domain P22 certificate only
# TENANT POSTURE: exact P1 and representative-specific lineage
# FAIL-CLOSED POSTURE: corruption and multiplicity never become accepted
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
