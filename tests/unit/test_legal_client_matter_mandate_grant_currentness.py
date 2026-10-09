"""Direct certificate for the L9B9-P1 pure grant-currentness projection.

TITLE: WILSY OS Legal Client Matter Mandate Grant Currentness Certificate
VERSION: v1.0.0-L9B9-P1-CLIENT-MANDATE-GRANT-CURRENTNESS-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify immutable state/evidence binding, strict hydration,
         deterministic integrity, and the absence of repository or downstream
         legal authority in the client-mandate grant currentness projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_mandate_grant_currentness.py
COLLABORATION / OWNERSHIP: Synthetic direct certificate for the L9B9-P1
                            projection domain only; the future composer owns
                            evidence selection and caller-owned transactions.
CERTIFICATION / UPDATE DATE: 2026-09-27
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TRANSACTION BOUNDARY: In-memory synthetic values only; no Mongo or network.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_currentness import (
    CURRENTNESS_FIELDS,
    SCHEMA,
    VERSION,
    LegalClientMatterMandateGrantCurrentness,
    LegalClientMatterMandateGrantCurrentnessError,
    LegalClientMatterMandateGrantCurrentnessReason,
    LegalClientMatterMandateGrantCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatterState


BASE = datetime(2026, 9, 27, 12, 0, 0, 123456, tzinfo=timezone.utc)
FP = "a" * 128
FP2 = "b" * 128
FP3 = "c" * 128


def projection(**changes: object) -> LegalClientMatterMandateGrantCurrentness:
    """Build one synthetic CURRENT projection unless overrides change it."""
    values: dict[str, Any] = {
        "currentness_id": "currentness-l9b9-1",
        "tenant_id": "tenant-l9b9",
        "client_grant_id": "grant-l9b9",
        "client_grant_fingerprint": FP,
        "case_matter_id": "matter-l9b9",
        "matter_fingerprint": FP2,
        "client_party_id": "party-l9b9",
        "subject_identity_fingerprint": FP3,
        "evaluation_time": BASE,
        "state": LegalClientMatterMandateGrantCurrentnessState.CURRENT,
        "reason": LegalClientMatterMandateGrantCurrentnessReason.CURRENT,
        "matter_state": CaseMatterState.OPEN,
        "matter_state_evidence_fingerprint": FP2,
        "formation_fingerprint": FP,
        "lifecycle_evidence_fingerprints": (),
        "decisive_lifecycle_evidence_fingerprints": (),
    }
    values.update(changes)
    return cast(Any, LegalClientMatterMandateGrantCurrentness)(**values)


def expect_code(code: str, **changes: object) -> None:
    """Assert one stable, non-sensitive projection error code."""
    with pytest.raises(LegalClientMatterMandateGrantCurrentnessError) as raised:
        projection(**changes)
    assert raised.value.code == code
    assert str(raised.value) == code


def invalid_state(
    state: LegalClientMatterMandateGrantCurrentnessState,
    reason: LegalClientMatterMandateGrantCurrentnessReason,
    **changes: object,
) -> LegalClientMatterMandateGrantCurrentness:
    """Build a valid non-CURRENT state with its required bounded evidence."""
    values: dict[str, Any] = {
        "state": state,
        "reason": reason,
        "lifecycle_evidence_fingerprints": (FP3,),
        "decisive_lifecycle_evidence_fingerprints": (FP3,),
    }
    values.update(changes)
    return projection(**values)


def test_current_projection_binds_identity_and_only_current_is_usable() -> None:
    value = projection()
    assert value.schema == SCHEMA
    assert value.currentness_version == VERSION
    assert value.state is LegalClientMatterMandateGrantCurrentnessState.CURRENT
    assert value.is_current is True and value.is_usable is True
    assert value.reason_code is LegalClientMatterMandateGrantCurrentnessReason.CURRENT
    assert value.client_grant_fingerprint == value.formation_fingerprint == FP
    assert value.matter_state is CaseMatterState.OPEN
    assert value.fingerprint == value.to_dict()["fingerprint"]


def test_all_bounded_non_current_states_are_explicit_and_not_usable() -> None:
    cases = (
        (LegalClientMatterMandateGrantCurrentnessState.NOT_YET_EFFECTIVE,
         LegalClientMatterMandateGrantCurrentnessReason.NOT_YET_EFFECTIVE),
        (LegalClientMatterMandateGrantCurrentnessState.EXPIRED,
         LegalClientMatterMandateGrantCurrentnessReason.EXPIRED),
        (LegalClientMatterMandateGrantCurrentnessState.REVOKED,
         LegalClientMatterMandateGrantCurrentnessReason.REVOKED),
        (LegalClientMatterMandateGrantCurrentnessState.SUPERSEDED,
         LegalClientMatterMandateGrantCurrentnessReason.SUPERSEDED),
    )
    for state, reason in cases:
        extra = (
            {"successor_client_grant_id": "grant-l9b9-successor", "successor_client_grant_fingerprint": FP2}
            if state is LegalClientMatterMandateGrantCurrentnessState.SUPERSEDED
            else {}
        )
        value = invalid_state(state, reason, **extra)
        assert value.is_current is False and value.is_usable is False

    closed = projection(
        state=LegalClientMatterMandateGrantCurrentnessState.MATTER_CLOSED,
        reason=LegalClientMatterMandateGrantCurrentnessReason.MATTER_CLOSED,
        matter_state=CaseMatterState.CLOSED,
        lifecycle_evidence_fingerprints=(),
        decisive_lifecycle_evidence_fingerprints=(),
    )
    assert closed.is_usable is False


def test_formation_absent_has_no_fabricated_formation_evidence() -> None:
    value = projection(
        client_grant_fingerprint=None,
        matter_fingerprint=None,
        subject_identity_fingerprint=None,
        formation_fingerprint=None,
        matter_state=None,
        matter_state_evidence_fingerprint=None,
        state=LegalClientMatterMandateGrantCurrentnessState.FORMATION_ABSENT,
        reason=LegalClientMatterMandateGrantCurrentnessReason.FORMATION_ABSENT,
    )
    assert value.client_grant_fingerprint is None
    assert value.formation_fingerprint is None
    assert value.is_usable is False
    expect_code(
        "L9B9_P1_FORMATION_ABSENT_EVIDENCE_FORBIDDEN",
        state=LegalClientMatterMandateGrantCurrentnessState.FORMATION_ABSENT,
        reason=LegalClientMatterMandateGrantCurrentnessReason.FORMATION_ABSENT,
        client_grant_fingerprint=FP,
        matter_fingerprint=None,
        subject_identity_fingerprint=None,
        formation_fingerprint=None,
        matter_state=None,
        matter_state_evidence_fingerprint=None,
    )


def test_corrupt_blocked_cannot_treat_source_as_trusted_formation() -> None:
    value = projection(
        state=LegalClientMatterMandateGrantCurrentnessState.CORRUPT_BLOCKED,
        reason=LegalClientMatterMandateGrantCurrentnessReason.CORRUPT_EVIDENCE,
        client_grant_fingerprint=None,
        formation_fingerprint=None,
        lifecycle_evidence_fingerprints=(FP3,),
        decisive_lifecycle_evidence_fingerprints=(),
    )
    assert value.is_usable is False
    expect_code(
        "L9B9_P1_CORRUPT_TRUSTED_EVIDENCE_FORBIDDEN",
        state=LegalClientMatterMandateGrantCurrentnessState.CORRUPT_BLOCKED,
        reason=LegalClientMatterMandateGrantCurrentnessReason.CORRUPT_EVIDENCE,
        client_grant_fingerprint=FP,
        formation_fingerprint=FP,
        lifecycle_evidence_fingerprints=(),
        decisive_lifecycle_evidence_fingerprints=(),
    )


def test_revocation_and_supersession_bind_decisive_evidence() -> None:
    revoked = invalid_state(
        LegalClientMatterMandateGrantCurrentnessState.REVOKED,
        LegalClientMatterMandateGrantCurrentnessReason.REVOKED,
    )
    assert revoked.decisive_lifecycle_evidence_fingerprints == (FP3,)
    superseded = invalid_state(
        LegalClientMatterMandateGrantCurrentnessState.SUPERSEDED,
        LegalClientMatterMandateGrantCurrentnessReason.SUPERSEDED,
        successor_client_grant_id="grant-l9b9-successor",
        successor_client_grant_fingerprint=FP2,
    )
    assert superseded.successor_client_grant_id == "grant-l9b9-successor"
    expect_code(
        "L9B9_P1_REVOCATION_EVIDENCE_REQUIRED",
        state=LegalClientMatterMandateGrantCurrentnessState.REVOKED,
        reason=LegalClientMatterMandateGrantCurrentnessReason.REVOKED,
        lifecycle_evidence_fingerprints=(),
        decisive_lifecycle_evidence_fingerprints=(),
    )
    expect_code(
        "L9B9_P1_SUPERSESSION_EVIDENCE_REQUIRED",
        state=LegalClientMatterMandateGrantCurrentnessState.SUPERSEDED,
        reason=LegalClientMatterMandateGrantCurrentnessReason.SUPERSEDED,
        lifecycle_evidence_fingerprints=(),
        decisive_lifecycle_evidence_fingerprints=(),
        successor_client_grant_id=None,
        successor_client_grant_fingerprint=None,
    )


def test_ambiguity_retains_all_conflicting_evidence_without_a_winner() -> None:
    value = projection(
        state=LegalClientMatterMandateGrantCurrentnessState.AMBIGUOUS,
        reason=LegalClientMatterMandateGrantCurrentnessReason.AMBIGUOUS_LIFECYCLE,
        lifecycle_evidence_fingerprints=(FP, FP2),
        decisive_lifecycle_evidence_fingerprints=(FP, FP2),
    )
    assert value.decisive_lifecycle_evidence_fingerprints == (FP, FP2)
    assert value.successor_client_grant_id is None
    expect_code(
        "L9B9_P1_AMBIGUITY_EVIDENCE_REQUIRED",
        state=LegalClientMatterMandateGrantCurrentnessState.AMBIGUOUS,
        reason=LegalClientMatterMandateGrantCurrentnessReason.AMBIGUOUS_LIFECYCLE,
        lifecycle_evidence_fingerprints=(FP,),
        decisive_lifecycle_evidence_fingerprints=(FP,),
    )


def test_matter_closed_requires_closed_matter_evidence() -> None:
    expect_code(
        "L9B9_P1_MATTER_CLOSED_EVIDENCE_INVALID",
        state=LegalClientMatterMandateGrantCurrentnessState.MATTER_CLOSED,
        reason=LegalClientMatterMandateGrantCurrentnessReason.MATTER_CLOSED,
        matter_state=CaseMatterState.OPEN,
        lifecycle_evidence_fingerprints=(),
        decisive_lifecycle_evidence_fingerprints=(),
    )
    expect_code(
        "L9B9_P1_CURRENT_EVIDENCE_INVALID",
        matter_state=CaseMatterState.CLOSED,
    )


def test_explicit_aware_utc_evaluation_is_required_and_canonicalized() -> None:
    value = projection(evaluation_time=BASE.replace(tzinfo=timezone(timedelta(hours=2))))
    assert value.evaluation_time.tzinfo is timezone.utc
    assert value.evaluation_time.microsecond == BASE.microsecond
    expect_code("L9B9_P1_EVALUATION_TIME_INVALID", evaluation_time=BASE.replace(tzinfo=None))


def test_deterministic_fingerprint_and_semantic_mutation() -> None:
    first = projection()
    second = projection()
    assert first.fingerprint == second.fingerprint
    changed = projection(evaluation_time=BASE + timedelta(seconds=1))
    assert changed.fingerprint != first.fingerprint
    assert len(first.fingerprint) == 128


def test_strict_round_trip_tamper_unknown_fields_and_malformed_state() -> None:
    original = projection()
    payload = original.to_dict()
    assert set(payload) == set(CURRENTNESS_FIELDS)
    assert LegalClientMatterMandateGrantCurrentness.from_dict(payload) == original
    tampered = dict(payload)
    tampered["evaluation_time"] = (BASE + timedelta(seconds=1)).isoformat()
    with pytest.raises(LegalClientMatterMandateGrantCurrentnessError):
        LegalClientMatterMandateGrantCurrentness.from_dict(tampered)
    unknown = dict(payload)
    unknown["extra"] = "x"
    with pytest.raises(LegalClientMatterMandateGrantCurrentnessError):
        LegalClientMatterMandateGrantCurrentness.from_dict(unknown)
    malformed = dict(payload)
    malformed["state"] = "ACTIVE"
    with pytest.raises(LegalClientMatterMandateGrantCurrentnessError):
        LegalClientMatterMandateGrantCurrentness.from_dict(malformed)
    bad_fp = dict(payload)
    bad_fp["fingerprint"] = "0" * 128
    with pytest.raises(LegalClientMatterMandateGrantCurrentnessError):
        LegalClientMatterMandateGrantCurrentness.from_dict(bad_fp)


def test_immutable_no_status_no_raw_pii_and_no_downstream_authority() -> None:
    value = projection()
    with pytest.raises(FrozenInstanceError):
        value.state = LegalClientMatterMandateGrantCurrentnessState.REVOKED  # type: ignore[misc]
    assert not any(name in CURRENTNESS_FIELDS for name in ("status", "active", "valid", "invalid"))
    assert "person@example" not in repr(value)
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_mandate_grant_currentness.py")
    tree = ast.parse(source.read_text())
    imported = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not any(
        token in module
        for module in imported
        for token in ("pymongo", "fastapi", "jwt", "requests", "registry", "orchestration")
    )
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"now", "utcnow"}
        for node in ast.walk(tree)
    )


# ARTIFACT: test_legal_client_matter_mandate_grant_currentness.py
# VERSION: v1.0.0-L9B9-P1-CLIENT-MANDATE-GRANT-CURRENTNESS-CERT
# RESULT: bounded synthetic unit certificate only
# END OF WILSY OS SOVEREIGN ARTIFACT
