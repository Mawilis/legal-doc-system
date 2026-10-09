"""Direct certificate for L9C9-P3 firm-decision currentness.

TITLE: WILSY OS Legal Engagement Firm Decision Currentness Certificate
VERSION: v1.0.0-L9C9-P3-ENGAGEMENT-FIRM-DECISION-CURRENTNESS-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the pure currentness projection for exact lineage, explicit
         time, effective-time precedence, ambiguity, corruption, deterministic
         integrity and authority exclusions using synthetic immutable values.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_engagement_firm_decision_currentness.py
COLLABORATION / OWNERSHIP: This certificate covers pure L9C9-P3 projection
                            only. Registry, composer, Engagement, IAM,
                            Representation, Court and finance remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-28
TRANSACTION BOUNDARY: Pure in-memory synthetic values; no Mongo or network.
FAIL-CLOSED DECLARATION: Invalid time, lineage, corruption and ambiguity fail
                         closed and never select arbitrary authority.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from itertools import permutations
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision import (
    LegalClientMatterEngagementFirmDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision_currentness import (
    VERSION,
    LegalClientMatterEngagementFirmDecisionCurrentness,
    LegalClientMatterEngagementFirmDecisionCurrentnessError,
    LegalClientMatterEngagementFirmDecisionCurrentnessState,
    project_legal_client_matter_engagement_firm_decision_currentness,
)


BASE = datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128
FP_D = "d" * 128


def decision(
    *,
    tenant_id: str = "tenant-l9c9",
    decision_id: str = "decision-l9c9-1",
    idempotency_key: str = "idempotency-l9c9-1",
    state: str = "ACCEPTED",
    effective_offset: int = 0,
    occurred_offset: int | None = None,
    matter_id: str = "matter-l9c9",
    matter_fingerprint: str = FP_A,
    party_id: str = "party-l9c9",
    subject_fingerprint: str = FP_B,
) -> LegalClientMatterEngagementFirmDecision:
    """Build one valid immutable decision without persistence or authority reads."""
    occurred = BASE + timedelta(minutes=occurred_offset if occurred_offset is not None else effective_offset)
    effective = BASE + timedelta(minutes=effective_offset)
    return LegalClientMatterEngagementFirmDecision(
        decision_id=decision_id,
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        matter_fingerprint=matter_fingerprint,
        client_party_id=party_id,
        subject_reference="client:subject-l9c9",
        subject_identity_fingerprint=subject_fingerprint,
        decision=state,
        decision_actor_principal_id="principal-l9c9",
        authorization_evidence_reference="iam:l9c9:authorization",
        authorization_evidence_fingerprint=FP_C,
        source_evidence_reference="source:l9c9:evidence",
        source_evidence_fingerprint=FP_D,
        occurred_at=occurred,
        effective_from=effective,
        idempotency_key=idempotency_key,
    )


def project(
    values: tuple[LegalClientMatterEngagementFirmDecision, ...],
    *,
    at: datetime = BASE + timedelta(hours=1),
    **context: object,
) -> LegalClientMatterEngagementFirmDecisionCurrentness:
    return project_legal_client_matter_engagement_firm_decision_currentness(
        tenant_id=cast(str, context.get("tenant_id", "tenant-l9c9")),
        case_matter_id=cast(str, context.get("case_matter_id", "matter-l9c9")),
        matter_fingerprint=cast(str, context.get("matter_fingerprint", FP_A)),
        client_party_id=cast(str, context.get("client_party_id", "party-l9c9")),
        subject_identity_fingerprint=cast(str, context.get("subject_identity_fingerprint", FP_B)),
        evaluated_at=at,
        decisions=values,
    )


def test_version_states_projection_shape_and_immutability() -> None:
    result = project(())
    assert VERSION == "v1.0.0-L9C9-P3-ENGAGEMENT-FIRM-DECISION-CURRENTNESS"
    assert [state.value for state in LegalClientMatterEngagementFirmDecisionCurrentnessState] == [
        "NO_DECISION", "ACCEPTED", "DECLINED", "REQUIRES_REVIEW", "AMBIGUOUS", "CORRUPT_BLOCKED"
    ]
    assert result.state is LegalClientMatterEngagementFirmDecisionCurrentnessState.NO_DECISION
    with pytest.raises(FrozenInstanceError):
        setattr(result, "state", "ACCEPTED")


def test_explicit_aware_evaluation_time_and_no_internal_clock() -> None:
    with pytest.raises(LegalClientMatterEngagementFirmDecisionCurrentnessError):
        project((), at=datetime(2026, 9, 28, 10, 0))
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_engagement_firm_decision_currentness.py").read_text()
    assert "datetime.now" not in source
    assert "datetime.utcnow" not in source


@pytest.mark.parametrize("state", ["ACCEPTED", "DECLINED", "REQUIRES_REVIEW"])
def test_single_decision_state_and_positive_helper(state: str) -> None:
    result = project((decision(state=state),))
    assert str(getattr(result.state, "value", result.state)) == state
    assert result.is_engagement_permitted is (state == "ACCEPTED")
    assert result.is_usable is (state == "ACCEPTED")


@pytest.mark.parametrize("state", ["ACCEPTED", "DECLINED", "REQUIRES_REVIEW"])
def test_future_only_decisions_produce_no_decision(state: str) -> None:
    result = project((decision(state=state),), at=BASE - timedelta(minutes=1))
    assert result.state is LegalClientMatterEngagementFirmDecisionCurrentnessState.NO_DECISION
    assert result.decisive_decision_ids == ()


def test_empty_history_produces_no_decision() -> None:
    result = project(())
    assert result.state is LegalClientMatterEngagementFirmDecisionCurrentnessState.NO_DECISION
    assert result.decisive_effective_from is None
    assert result.decisive_decision_ids == ()


@pytest.mark.parametrize(
    ("older", "later", "expected"),
    [
        ("ACCEPTED", "DECLINED", "DECLINED"),
        ("ACCEPTED", "REQUIRES_REVIEW", "REQUIRES_REVIEW"),
        ("DECLINED", "ACCEPTED", "ACCEPTED"),
        ("REQUIRES_REVIEW", "ACCEPTED", "ACCEPTED"),
    ],
)
def test_later_effective_decision_supersedes_older(older: str, later: str, expected: str) -> None:
    result = project(
        (
            decision(state=older, decision_id="older", idempotency_key="older-key", effective_offset=1),
            decision(state=later, decision_id="later", idempotency_key="later-key", effective_offset=2),
        )
    )
    assert str(getattr(result.state, "value", result.state)) == expected
    assert result.decisive_decision_ids == ("later",)


def test_same_effective_same_state_duplicates_are_unambiguous() -> None:
    values = (
        decision(decision_id="accepted-a", idempotency_key="accepted-a-key"),
        decision(decision_id="accepted-b", idempotency_key="accepted-b-key"),
    )
    result = project(values)
    assert result.state is LegalClientMatterEngagementFirmDecisionCurrentnessState.ACCEPTED
    assert len(result.decisive_decision_ids) == 2


@pytest.mark.parametrize(
    "left,right",
    [("ACCEPTED", "DECLINED"), ("ACCEPTED", "REQUIRES_REVIEW"), ("DECLINED", "REQUIRES_REVIEW")],
)
def test_same_effective_conflicting_states_are_ambiguous(left: str, right: str) -> None:
    result = project(
        (
            decision(state=left, decision_id="left", idempotency_key="left-key"),
            decision(state=right, decision_id="right", idempotency_key="right-key"),
        )
    )
    assert result.state is LegalClientMatterEngagementFirmDecisionCurrentnessState.AMBIGUOUS
    assert result.is_engagement_permitted is False


def test_three_way_conflict_and_older_conflict_are_handled_by_effective_time() -> None:
    older_conflict = (
        decision(state="ACCEPTED", decision_id="old-a", idempotency_key="old-a-key", effective_offset=1),
        decision(state="DECLINED", decision_id="old-d", idempotency_key="old-d-key", effective_offset=1),
    )
    later = decision(state="ACCEPTED", decision_id="later", idempotency_key="later-key", effective_offset=2)
    assert project(older_conflict + (later,)).state is LegalClientMatterEngagementFirmDecisionCurrentnessState.ACCEPTED
    three_way = (
        decision(state="ACCEPTED", decision_id="a", idempotency_key="a-key"),
        decision(state="DECLINED", decision_id="d", idempotency_key="d-key"),
        decision(state="REQUIRES_REVIEW", decision_id="r", idempotency_key="r-key"),
    )
    assert project(three_way).state is LegalClientMatterEngagementFirmDecisionCurrentnessState.AMBIGUOUS


def test_lineage_mismatch_is_corrupt_blocked() -> None:
    base = decision()
    for context in (
        {"tenant_id": "other-tenant"},
        {"case_matter_id": "other-matter"},
        {"matter_fingerprint": "e" * 128},
        {"client_party_id": "other-party"},
        {"subject_identity_fingerprint": "f" * 128},
    ):
        result = project_legal_client_matter_engagement_firm_decision_currentness(
            tenant_id=cast(str, context.get("tenant_id", "tenant-l9c9")),
            case_matter_id=cast(str, context.get("case_matter_id", "matter-l9c9")),
            matter_fingerprint=cast(str, context.get("matter_fingerprint", FP_A)),
            client_party_id=cast(str, context.get("client_party_id", "party-l9c9")),
            subject_identity_fingerprint=cast(str, context.get("subject_identity_fingerprint", FP_B)),
            evaluated_at=BASE + timedelta(hours=1),
            decisions=(base,),
        )
        assert result.state is LegalClientMatterEngagementFirmDecisionCurrentnessState.CORRUPT_BLOCKED


def test_malformed_domain_value_is_corrupt_blocked() -> None:
    value = decision()
    object.__setattr__(value, "fingerprint", "0" * 128)
    result = project((value,))
    assert result.state is LegalClientMatterEngagementFirmDecisionCurrentnessState.CORRUPT_BLOCKED
    assert result.corruption_evidence_fingerprints


def test_exact_duplicate_is_semantic_noop_and_contradictory_duplicate_is_blocked() -> None:
    value = decision()
    assert project((value, value)).to_dict() == project((value,)).to_dict()
    contradictory = decision(state="DECLINED")
    object.__setattr__(contradictory, "decision_id", value.decision_id)
    result = project((value, contradictory))
    assert result.state is LegalClientMatterEngagementFirmDecisionCurrentnessState.CORRUPT_BLOCKED


def test_order_independence_and_projection_fingerprint_determinism() -> None:
    values = (
        decision(state="ACCEPTED", decision_id="a", idempotency_key="a-key"),
        decision(state="DECLINED", decision_id="d", idempotency_key="d-key"),
    )
    projections = [project(order) for order in permutations(values)]
    assert all(item.to_dict() == projections[0].to_dict() for item in projections)
    assert project((values[0],), at=BASE + timedelta(minutes=1)).fingerprint != project(
        (values[0],), at=BASE + timedelta(minutes=2)
    ).fingerprint


def test_occurred_time_ids_and_fingerprints_do_not_override_effective_time() -> None:
    earlier_effective = decision(
        state="ACCEPTED",
        decision_id="accepted",
        idempotency_key="accepted-key",
        effective_offset=1,
        occurred_offset=0,
    )
    later_effective = decision(
        state="DECLINED",
        decision_id="declined",
        idempotency_key="declined-key",
        effective_offset=2,
        occurred_offset=1,
    )
    result = project((later_effective, earlier_effective))
    assert result.state is LegalClientMatterEngagementFirmDecisionCurrentnessState.DECLINED
    assert result.decisive_effective_from == later_effective.effective_from


def test_projection_round_trip_and_fingerprint_changes_with_decisive_evidence() -> None:
    result = project((decision(),))
    restored = LegalClientMatterEngagementFirmDecisionCurrentness.from_dict(result.to_dict())
    assert restored == result
    changed = project((decision(state="DECLINED"),))
    assert changed.fingerprint != result.fingerprint


def test_pure_authority_surface_has_no_persistence_or_foreign_authority() -> None:
    source_path = Path("tools/eos/legal_operations/domain/legal_client_matter_engagement_firm_decision_currentness.py")
    tree = ast.parse(source_path.read_text())
    imports = " ".join(ast.unparse(node) for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))
    lowered = imports.lower()
    for forbidden in (
        "pymongo", "registry", "authorization", "principal_status", "clientacceptance",
        "acting_capacity", "conflict_currentness", "mandate_currentness", "engagement.py",
        "representation", "court", "financial", "http",
    ):
        assert forbidden not in lowered
    assert "LegalClientMatterEngagement(" not in source_path.read_text()


# ARTIFACT: test_legal_client_matter_engagement_firm_decision_currentness.py
# VERSION: v1.0.0-L9C9-P3-ENGAGEMENT-FIRM-DECISION-CURRENTNESS-CERT
# AUTHORITY BOUNDARY: direct certificate for pure currentness only
# TENANT POSTURE: exact lineage and explicit evaluation time
# FAIL-CLOSED POSTURE: corruption and ambiguity never select arbitrary authority
# END OF WILSY OS SOVEREIGN ARTIFACT
