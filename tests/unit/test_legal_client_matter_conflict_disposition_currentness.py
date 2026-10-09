"""Direct certificate for the L9C5 conflict-disposition currentness projection.

TITLE: WILSY OS Legal Client Matter Conflict Disposition Currentness Certificate
VERSION: v1.0.0-L9C5-CONFLICT-DISPOSITION-CURRENTNESS-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify deterministic, immutable, exact-scope disposition currentness
         without registry, database, IAM, Engagement or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_conflict_disposition_currentness.py
COLLABORATION / OWNERSHIP: The disposition domain owns historical evidence; a
                            future composer owns registry reads and transactions.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9C5-CONFLICT-DISPOSITION-CURRENTNESS-CERT covers the six
           states, effective-time precedence, corruption blocking, exact scope,
           lineage retention, strict hydration and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TRANSACTION BOUNDARY: Synthetic immutable values only; no Mongo or network.
FAIL-CLOSED DECLARATION: No disposition, ambiguity, corruption, malformed or
                         cross-scope evidence can become positive authority.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from datetime import timedelta, timezone
from pathlib import Path

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition import (
    LegalClientMatterConflictDispositionType,
)
from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition_currentness import (
    CURRENTNESS_FIELDS,
    SCHEMA,
    VERSION,
    LegalClientMatterConflictDispositionCurrentness,
    LegalClientMatterConflictDispositionCurrentnessError,
    LegalClientMatterConflictDispositionCurrentnessReason,
    LegalClientMatterConflictDispositionCurrentnessState,
    project_legal_client_matter_conflict_disposition_currentness,
)
from tests.unit.test_legal_client_matter_conflict_disposition import BASE, TENANT, bundle


MATTER = "matter-l9b2"
MATTER_FP = bundle()[0].matter_fingerprint
PARTY = bundle()[0].client_party_id
SUBJECT = bundle()[0].subject_identity_fingerprint
AT = BASE + timedelta(hours=1)


def disposition(*, state=LegalClientMatterConflictDispositionType.ENGAGEMENT_PERMITTED, effective=None, occurred=None, suffix="a"):
    value = bundle(disposition=state)[0]
    return replace(
        value,
        disposition_id=f"disposition-l9c5-{suffix}",
        effective_from=effective or value.effective_from,
        occurred_at=occurred or (effective - timedelta(minutes=1) if effective is not None else value.occurred_at),
        idempotency_key=f"idempotency:l9c5:{suffix}",
        fingerprint="",
    )


def project(*values, evaluation_time=AT, **scope):
    if not values:
        values = (disposition(),)
    return project_legal_client_matter_conflict_disposition_currentness(
        tenant_id=scope.pop("tenant_id", TENANT),
        case_matter_id=scope.pop("case_matter_id", MATTER),
        matter_fingerprint=scope.pop("matter_fingerprint", MATTER_FP),
        client_party_id=scope.pop("client_party_id", PARTY),
        subject_identity_fingerprint=scope.pop("subject_identity_fingerprint", SUBJECT),
        evaluation_time=evaluation_time,
        dispositions=values,
    )


def test_schema_vocabulary_and_positive_predicate():
    value = project()
    assert value.schema == SCHEMA and value.currentness_version == VERSION
    assert value.state is LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PERMITTED
    assert value.reason_code is LegalClientMatterConflictDispositionCurrentnessReason.ENGAGEMENT_PERMITTED
    assert value.is_engagement_permitted and value.is_usable
    assert set(value.to_dict()) == CURRENTNESS_FIELDS
    assert {item.value for item in LegalClientMatterConflictDispositionCurrentnessState} == {
        "NO_DISPOSITION", "ENGAGEMENT_PERMITTED", "ENGAGEMENT_PROHIBITED",
        "ENGAGEMENT_UNRESOLVED", "AMBIGUOUS", "CORRUPT_BLOCKED",
    }


def test_empty_and_future_only_history_are_not_positive():
    assert project().state is LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PERMITTED
    empty = project(*(), evaluation_time=AT - timedelta(days=1))
    assert empty.state is LegalClientMatterConflictDispositionCurrentnessState.NO_DISPOSITION
    assert not empty.is_engagement_permitted and empty.decisive_effective_from is None


def test_latest_effective_time_not_occurred_or_identifier_order():
    earlier = disposition(effective=BASE + timedelta(minutes=10), occurred=BASE + timedelta(minutes=10), suffix="z")
    later = disposition(state=LegalClientMatterConflictDispositionType.ENGAGEMENT_UNRESOLVED, effective=BASE + timedelta(minutes=20), occurred=BASE + timedelta(minutes=19), suffix="a")
    value = project(later, earlier)
    assert value.state is LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_UNRESOLVED
    assert value.decisive_effective_from == later.effective_from
    assert value.decisive_disposition_ids == (later.disposition_id,)


@pytest.mark.parametrize("state", list(LegalClientMatterConflictDispositionType))
def test_single_state_and_same_effective_duplicates_resolve_to_that_state(state):
    first = disposition(state=state, effective=BASE + timedelta(minutes=30), suffix="a")
    second = disposition(state=state, effective=BASE + timedelta(minutes=30), suffix="b")
    value = project(second, first)
    assert value.state is LegalClientMatterConflictDispositionCurrentnessState(state.value)
    assert set(value.decisive_disposition_ids) == {first.disposition_id, second.disposition_id}
    assert not (value.state is LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PERMITTED) or value.is_engagement_permitted


@pytest.mark.parametrize("states", [
    (LegalClientMatterConflictDispositionType.ENGAGEMENT_PERMITTED, LegalClientMatterConflictDispositionType.ENGAGEMENT_PROHIBITED),
    (LegalClientMatterConflictDispositionType.ENGAGEMENT_PERMITTED, LegalClientMatterConflictDispositionType.ENGAGEMENT_UNRESOLVED),
    (LegalClientMatterConflictDispositionType.ENGAGEMENT_PROHIBITED, LegalClientMatterConflictDispositionType.ENGAGEMENT_UNRESOLVED),
])
def test_same_effective_different_states_are_ambiguous(states):
    value = project(*(disposition(state=state, effective=BASE + timedelta(minutes=40), suffix=str(index)) for index, state in enumerate(states)))
    assert value.state is LegalClientMatterConflictDispositionCurrentnessState.AMBIGUOUS
    assert not value.is_engagement_permitted


def test_three_way_conflict_and_shuffling_are_deterministic():
    values = tuple(disposition(state=state, effective=BASE + timedelta(minutes=50), suffix=str(index)) for index, state in enumerate(LegalClientMatterConflictDispositionType))
    first = project(*values)
    second = project(*reversed(values))
    assert first.state is second.state is LegalClientMatterConflictDispositionCurrentnessState.AMBIGUOUS
    assert first.fingerprint == second.fingerprint


@pytest.mark.parametrize("field", ["tenant_id", "case_matter_id", "matter_fingerprint", "client_party_id", "subject_identity_fingerprint"])
def test_cross_scope_evidence_is_corrupt_blocked(field):
    value = disposition(suffix="scope")
    changes = {field: "other-tenant" if field in {"tenant_id", "case_matter_id", "client_party_id"} else "f" * 128}
    corrupted = replace(value, fingerprint="")
    object.__setattr__(corrupted, field, changes[field])
    result = project(corrupted)
    assert result.state is LegalClientMatterConflictDispositionCurrentnessState.CORRUPT_BLOCKED
    assert not result.is_engagement_permitted and result.corruption_evidence_fingerprints


def test_malformed_evidence_is_corrupt_and_not_skipped():
    result = project(object())  # type: ignore[arg-type]
    assert result.state is LegalClientMatterConflictDispositionCurrentnessState.CORRUPT_BLOCKED
    assert not result.is_engagement_permitted


def test_lineage_is_retained_without_reinterpretation():
    value = project()
    source = disposition()
    assert value.decisive_screening_ids == (source.screening_id,)
    assert value.decisive_screening_fingerprints == (source.screening_fingerprint,)
    assert value.decisive_conflict_review_ids == (source.conflict_review_id,)
    assert value.decisive_conflict_review_fingerprints == (source.conflict_review_fingerprint,)
    assert value.decisive_review_outcomes == (getattr(source.review_outcome, "value", source.review_outcome),)


def test_immutability_determinism_and_digest_shape():
    first = project()
    second = project()
    assert first == second and len(first.fingerprint) == 128 and first.fingerprint.islower()
    with pytest.raises(FrozenInstanceError):
        first.state = LegalClientMatterConflictDispositionCurrentnessState.AMBIGUOUS  # type: ignore[misc]
    assert first.to_dict()["fingerprint"] == first.fingerprint
    assert project(evaluation_time=AT + timedelta(seconds=1)).fingerprint != first.fingerprint


def test_strict_hydration_rejects_unknown_missing_and_tampered_payloads():
    value = project()
    assert LegalClientMatterConflictDispositionCurrentness.from_dict(value.to_dict()) == value
    with pytest.raises(LegalClientMatterConflictDispositionCurrentnessError) as raised:
        LegalClientMatterConflictDispositionCurrentness.from_dict({**value.to_dict(), "extra": 1})
    assert raised.value.code == "L9C5_SCHEMA_INVALID"
    payload = value.to_dict()
    payload["state"] = "UNKNOWN"
    with pytest.raises(LegalClientMatterConflictDispositionCurrentnessError):
        LegalClientMatterConflictDispositionCurrentness.from_dict(payload)
    payload = value.to_dict()
    payload["fingerprint"] = "0" * 128
    with pytest.raises(LegalClientMatterConflictDispositionCurrentnessError):
        LegalClientMatterConflictDispositionCurrentness.from_dict(payload)


def test_explicit_aware_time_and_no_hidden_clock():
    aware = project(evaluation_time=AT.replace(tzinfo=timezone(timedelta(hours=2))))
    assert aware.evaluation_time.tzinfo is timezone.utc
    with pytest.raises(LegalClientMatterConflictDispositionCurrentnessError):
        project(evaluation_time=AT.replace(tzinfo=None))


def test_source_is_not_mutated_and_no_forbidden_authority_imports():
    source = disposition()
    before = source.to_dict()
    project(source)
    assert source.to_dict() == before
    module = ast.parse(Path("tools/eos/legal_operations/domain/legal_client_matter_conflict_disposition_currentness.py").read_text())
    imported = {node.module.split(".")[0] for node in ast.walk(module) if isinstance(node, ast.ImportFrom) and node.module}
    imported.update(alias.name.split(".")[0] for node in ast.walk(module) if isinstance(node, ast.Import) for alias in node.names)
    assert imported.isdisjoint({"pymongo", "motor", "mongo", "registry", "jwt", "requests", "httpx", "time"})
    text = Path("tools/eos/legal_operations/domain/legal_client_matter_conflict_disposition_currentness.py").read_text()
    assert "datetime.now" not in text and "utcnow" not in text


def test_state_evidence_consistency_rejects_impossible_manual_projection():
    value = project()
    with pytest.raises(LegalClientMatterConflictDispositionCurrentnessError):
        LegalClientMatterConflictDispositionCurrentness(
            **{**value.to_dict(), "state": "NO_DISPOSITION", "reason": "NO_DISPOSITION", "fingerprint": ""}
        )


def test_public_contract_has_no_downstream_authority():
    payload = project().to_dict()
    assert all(name not in payload for name in ("engagement", "iam", "representation", "court", "financial"))
    assert all(not isinstance(value, (bytes, bytearray)) for value in payload.values())


# ARTIFACT: test_legal_client_matter_conflict_disposition_currentness.py
# VERSION: v1.0.0-L9C5-CONFLICT-DISPOSITION-CURRENTNESS-CERT
# AUTHORITY BOUNDARY: direct pure currentness certificate only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
