"""Direct certificate for the L9B10-P2 acknowledgment projection.

TITLE: WILSY OS Legal Client Matter Mandate Acknowledgment Currentness Certificate
VERSION: v1.0.0-L9B10-P2-FIRM-MANDATE-ACKNOWLEDGMENT-CURRENTNESS-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify immutable state-safe acknowledgment currentness output,
         exact grant lineage, evidence binding, strict hydration and authority
         exclusions without reading persistence history.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_mandate_acknowledgment_currentness.py
COLLABORATION / OWNERSHIP: This certificate covers only the pure projection;
                            registry history selection, currentness composition,
                            IAM, mandate, Engagement, Court and finance remain
                            separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-27
TRANSACTION BOUNDARY: Pure in-memory certificate; no Mongo, network or clock.
FAIL-CLOSED DECLARATION: Invalid states, evidence, lineage, timestamps,
                         schemas and fingerprints must reject.
"""
from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment_currentness import (
    SCHEMA,
    VERSION,
    LegalClientMatterMandateAcknowledgmentCurrentness,
    LegalClientMatterMandateAcknowledgmentCurrentnessError,
    LegalClientMatterMandateAcknowledgmentCurrentnessReason,
    LegalClientMatterMandateAcknowledgmentCurrentnessState,
    project_legal_client_matter_mandate_acknowledgment_currentness,
)


BASE = datetime(2026, 9, 27, 12, 0, 0, 123456, tzinfo=timezone.utc)
GRANT_FP = "a" * 128
MATTER_FP = "b" * 128
SUBJECT_FP = "c" * 128
ACK_FP_1 = "d" * 128
ACK_FP_2 = "e" * 128
CORRUPTION_FP = "f" * 128


def projection(
    *,
    state: LegalClientMatterMandateAcknowledgmentCurrentnessState | str = LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED,
    reason: LegalClientMatterMandateAcknowledgmentCurrentnessReason | str | None = None,
    evaluation_time: datetime = BASE,
    evidence: tuple[str, ...] | None = None,
    decisive_ids: tuple[str, ...] | None = None,
    decisive_fingerprints: tuple[str, ...] | None = None,
    decisive_decisions: tuple[str, ...] | None = None,
    corruption: tuple[str, ...] = (),
    **overrides: object,
) -> LegalClientMatterMandateAcknowledgmentCurrentness:
    """Build one synthetic projection with bounded opaque evidence."""
    parsed = LegalClientMatterMandateAcknowledgmentCurrentnessState(state)
    if reason is None:
        reason = {
            LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED: "ACKNOWLEDGED",
            LegalClientMatterMandateAcknowledgmentCurrentnessState.DECLINED: "DECLINED",
            LegalClientMatterMandateAcknowledgmentCurrentnessState.REQUIRES_REVIEW: "REQUIRES_REVIEW",
            LegalClientMatterMandateAcknowledgmentCurrentnessState.NO_DECISION: "NO_DECISION",
            LegalClientMatterMandateAcknowledgmentCurrentnessState.AMBIGUOUS: "AMBIGUOUS_DECISIONS",
            LegalClientMatterMandateAcknowledgmentCurrentnessState.CORRUPT_BLOCKED: "CORRUPT_EVIDENCE",
        }[parsed]
    defaults: dict[str, object] = {
        "currentness_id": "ack-currentness-l9b10-1",
        "tenant_id": "tenant-l9b10",
        "client_grant_id": "client-grant-l9b10",
        "client_grant_fingerprint": GRANT_FP,
        "case_matter_id": "matter-l9b10",
        "matter_fingerprint": MATTER_FP,
        "client_party_id": "party-l9b10",
        "subject_identity_fingerprint": SUBJECT_FP,
        "evaluation_time": evaluation_time,
        "state": parsed,
        "reason": reason,
        "acknowledgment_evidence_fingerprints": evidence if evidence is not None else (ACK_FP_1,),
        "decisive_acknowledgment_ids": decisive_ids if decisive_ids is not None else ("ack-l9b10-1",),
        "decisive_acknowledgment_fingerprints": decisive_fingerprints if decisive_fingerprints is not None else (ACK_FP_1,),
        "decisive_decisions": decisive_decisions if decisive_decisions is not None else (parsed.value,),
        "corruption_evidence_fingerprints": corruption,
    }
    if parsed is LegalClientMatterMandateAcknowledgmentCurrentnessState.NO_DECISION:
        if evidence is None:
            defaults["acknowledgment_evidence_fingerprints"] = ()
        if decisive_ids is None:
            defaults["decisive_acknowledgment_ids"] = ()
        if decisive_fingerprints is None:
            defaults["decisive_acknowledgment_fingerprints"] = ()
        if decisive_decisions is None:
            defaults["decisive_decisions"] = ()
    if parsed is LegalClientMatterMandateAcknowledgmentCurrentnessState.AMBIGUOUS:
        if evidence is None:
            defaults["acknowledgment_evidence_fingerprints"] = (ACK_FP_1, ACK_FP_2)
        if decisive_ids is None:
            defaults["decisive_acknowledgment_ids"] = ("ack-l9b10-1", "ack-l9b10-2")
        if decisive_fingerprints is None:
            defaults["decisive_acknowledgment_fingerprints"] = (ACK_FP_1, ACK_FP_2)
        if decisive_decisions is None:
            defaults["decisive_decisions"] = ("ACKNOWLEDGED", "DECLINED")
    if parsed is LegalClientMatterMandateAcknowledgmentCurrentnessState.CORRUPT_BLOCKED:
        if evidence is None:
            defaults["acknowledgment_evidence_fingerprints"] = ()
        if decisive_ids is None:
            defaults["decisive_acknowledgment_ids"] = ()
        if decisive_fingerprints is None:
            defaults["decisive_acknowledgment_fingerprints"] = ()
        if decisive_decisions is None:
            defaults["decisive_decisions"] = ()
        if not corruption:
            defaults["corruption_evidence_fingerprints"] = (CORRUPTION_FP,)
    defaults.update(overrides)
    return project_legal_client_matter_mandate_acknowledgment_currentness(**defaults)


def assert_code(code: str, operation: Any) -> None:
    """Assert one bounded non-sensitive projection error code."""
    with pytest.raises(LegalClientMatterMandateAcknowledgmentCurrentnessError) as raised:
        operation()
    assert raised.value.code == code


@pytest.mark.parametrize(
    ("state", "positive"),
    [
        ("ACKNOWLEDGED", True),
        ("DECLINED", False),
        ("REQUIRES_REVIEW", False),
    ],
)
def test_decision_states_and_only_acknowledged_is_positive(
    state: str, positive: bool
) -> None:
    value = projection(state=state)
    assert value.is_acknowledged is positive
    assert value.is_usable is positive
    assert str(value.state) == state


def test_no_decision_has_no_fabricated_decisive_reference() -> None:
    value = projection(state="NO_DECISION")
    assert value.reason is LegalClientMatterMandateAcknowledgmentCurrentnessReason.NO_DECISION
    assert value.acknowledgment_evidence_fingerprints == ()
    assert value.decisive_acknowledgment_ids == ()
    assert value.decisive_acknowledgment_fingerprints == ()
    assert value.decisive_decisions == ()
    assert_code(
        "L9B10_P2_DECISIVE_EVIDENCE_LENGTH_MISMATCH",
        lambda: projection(state="NO_DECISION", decisive_ids=("ack-fabricated",)),
    )


def test_ambiguous_binds_incompatible_decisive_evidence_without_winner() -> None:
    value = projection(state="AMBIGUOUS")
    assert value.is_acknowledged is False
    assert value.decisive_acknowledgment_ids == ("ack-l9b10-1", "ack-l9b10-2")
    assert set(value.decisive_decisions) == {"ACKNOWLEDGED", "DECLINED"}
    assert_code(
        "L9B10_P2_AMBIGUITY_EVIDENCE_REQUIRED",
        lambda: projection(state="AMBIGUOUS", decisive_decisions=("ACKNOWLEDGED", "ACKNOWLEDGED")),
    )


def test_corrupt_blocked_has_no_trusted_positive_evidence() -> None:
    value = projection(state="CORRUPT_BLOCKED")
    assert value.is_acknowledged is False
    assert value.corruption_evidence_fingerprints == (CORRUPTION_FP,)
    assert value.decisive_acknowledgment_ids == ()
    assert_code(
        "L9B10_P2_DECISIVE_EVIDENCE_LENGTH_MISMATCH",
        lambda: projection(state="CORRUPT_BLOCKED", decisive_ids=("ack-trusted",)),
    )


def test_exact_lineage_and_aware_utc_evaluation_time_are_bound() -> None:
    value = projection(evaluation_time=BASE.replace(tzinfo=timezone(timedelta(hours=2))))
    assert value.tenant_id == "tenant-l9b10"
    assert value.client_grant_id == "client-grant-l9b10"
    assert value.client_grant_fingerprint == GRANT_FP
    assert value.case_matter_id == "matter-l9b10"
    assert value.matter_fingerprint == MATTER_FP
    assert value.client_party_id == "party-l9b10"
    assert value.subject_identity_fingerprint == SUBJECT_FP
    assert value.evaluation_time.tzinfo is timezone.utc
    assert_code(
        "L9B10_P2_EVALUATION_TIME_INVALID",
        lambda: projection(evaluation_time=BASE.replace(tzinfo=None)),
    )


def test_same_effective_same_decision_evidence_is_not_ambiguous() -> None:
    value = projection(
        evidence=(ACK_FP_1, ACK_FP_2),
        decisive_ids=("ack-l9b10-1", "ack-l9b10-2"),
        decisive_fingerprints=(ACK_FP_1, ACK_FP_2),
        decisive_decisions=("ACKNOWLEDGED", "ACKNOWLEDGED"),
    )
    assert value.is_acknowledged is True
    assert len(value.decisive_acknowledgment_fingerprints) == 2


def test_state_specific_decisive_evidence_is_required() -> None:
    assert_code(
        "L9B10_P2_DECISIVE_EVIDENCE_LENGTH_MISMATCH",
        lambda: projection(state="ACKNOWLEDGED", decisive_ids=()),
    )
    assert_code(
        "L9B10_P2_STATE_EVIDENCE_MISMATCH",
        lambda: projection(state="DECLINED", decisive_decisions=("ACKNOWLEDGED",)),
    )
    assert_code(
        "L9B10_P2_STATE_EVIDENCE_MISMATCH",
        lambda: projection(state="REQUIRES_REVIEW", decisive_decisions=("DECLINED",)),
    )


def test_fingerprint_is_deterministic_and_semantic_changes_diverge() -> None:
    first = projection()
    equivalent = projection()
    changed = projection(evaluation_time=BASE + timedelta(seconds=1))
    assert first.fingerprint == equivalent.fingerprint
    assert first.fingerprint != changed.fingerprint


def test_strict_roundtrip_rejects_unknown_fields_and_tampering() -> None:
    value = projection()
    restored = LegalClientMatterMandateAcknowledgmentCurrentness.from_dict(value.to_dict())
    assert restored == value
    assert_code(
        "L9B10_P2_SCHEMA_INVALID",
        lambda: LegalClientMatterMandateAcknowledgmentCurrentness.from_dict({**value.to_dict(), "extra": "x"}),
    )
    assert_code(
        "L9B10_P2_FINGERPRINT_MISMATCH",
        lambda: LegalClientMatterMandateAcknowledgmentCurrentness.from_dict({**value.to_dict(), "fingerprint": "0" * 128}),
    )
    with pytest.raises(ValueError):
        projection(state="UNKNOWN")
    assert_code(
        "L9B10_P2_ACKNOWLEDGMENT_EVIDENCE_FINGERPRINTS_INVALID",
        lambda: projection(evidence=("not-a-fingerprint",)),
    )


def test_schema_and_authority_exclusions_are_exact() -> None:
    value = projection()
    assert value.schema == SCHEMA
    assert value.currentness_version == VERSION
    payload = value.to_dict()
    assert "status" not in payload
    assert "mandate" not in payload
    assert "engagement" not in payload
    assert all("@" not in str(item) for item in payload.values())
    source = Path(
        "tools/eos/legal_operations/domain/legal_client_matter_mandate_acknowledgment_currentness.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert imports <= {"__future__", "collections.abc", "dataclasses", "datetime", "enum", "typing"}
    assert not any(name in source for name in ("pymongo", "MongoClient", "get_database", "tenant_authorization"))
    assert "TODO" not in source
    assert "FIXME" not in source
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source


# ARTIFACT: test_legal_client_matter_mandate_acknowledgment_currentness.py
# VERSION: v1.0.0-L9B10-P2-FIRM-MANDATE-ACKNOWLEDGMENT-CURRENTNESS-CERT
# AUTHORITY BOUNDARY: pure acknowledgment currentness projection certificate only
# END OF WILSY OS SOVEREIGN ARTIFACT
