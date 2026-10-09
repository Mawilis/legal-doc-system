"""Direct certificate for the L9B12-P1 mandate-currentness projection.

TITLE: WILSY OS Legal Client Matter Mandate Currentness Certificate
VERSION: v1.0.0-L9B12-P1-CLIENT-MATTER-MANDATE-CURRENTNESS-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the pure immutable projection that decides whether one
         historical mandate remains usable at one explicit instant.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_mandate_currentness.py
COLLABORATION / OWNERSHIP: The mandate domain and grant/acknowledgment
                            currentness projections remain upstream authorities;
                            a later composer owns repository reads and caller
                            transactions. This file certifies only this pure
                            projection.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B12-P1-CLIENT-MATTER-MANDATE-CURRENTNESS-CERT covers the
           closed state vocabulary, exact lineage, chronology, strict
           hydration, deterministic integrity and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TRANSACTION BOUNDARY: Synthetic in-memory values only; no Mongo, registry,
                       network, clock or external authority.
FAIL-CLOSED DECLARATION: Missing, corrupt, ambiguous, stale, divergent or
                         malformed evidence is never CURRENT.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_mandate import (
    LegalClientMatterMandate,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment_currentness import (
    LegalClientMatterMandateAcknowledgmentCurrentness,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_currentness import (
    CURRENTNESS_FIELDS,
    SCHEMA,
    VERSION,
    LegalClientMatterMandateCurrentness,
    LegalClientMatterMandateCurrentnessError,
    LegalClientMatterMandateCurrentnessReason,
    LegalClientMatterMandateCurrentnessState,
    project_legal_client_matter_mandate_currentness,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_currentness import (
    LegalClientMatterMandateGrantCurrentness,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatterState

from tests.unit.test_legal_client_matter_mandate import mandate, matter


BASE = datetime(2026, 9, 27, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-l9b12"
GRANT_FP = "d" * 128
ACK_FP = "e" * 128
CORRUPTION_FP = "f" * 128


def source_mandate(**changes: object) -> LegalClientMatterMandate:
    """Return a valid synthetic historical mandate with controlled lineage."""
    tenant_id = cast(str, changes.pop("tenant_id", TENANT))
    values: dict[str, object] = {
        "client_grant_fingerprint": GRANT_FP,
        "firm_acknowledgment_fingerprint": ACK_FP,
    }
    values["case_matter"] = matter(tenant_id=tenant_id)
    values.update(changes)
    return mandate(**values)


def grant_projection(
    *,
    state: str = "CURRENT",
    tenant_id: str = TENANT,
    client_grant_id: str = "client-grant:l9b3",
    client_grant_fingerprint: str | None = GRANT_FP,
    case_matter_id: str | None = "matter-l9b3",
    matter_fingerprint: str | None = None,
    client_party_id: str | None = "party-l9b3",
    subject_identity_fingerprint: str | None = None,
    lifecycle: tuple[str, ...] = (),
    decisive_lifecycle: tuple[str, ...] = (),
) -> LegalClientMatterMandateGrantCurrentness:
    """Build a synthetic upstream grant-currentness value."""
    source = source_mandate()
    return LegalClientMatterMandateGrantCurrentness(
        currentness_id="grant-currentness-l9b12",
        tenant_id=tenant_id,
        client_grant_id=client_grant_id,
        client_grant_fingerprint=None if state == "CORRUPT_BLOCKED" else client_grant_fingerprint,
        case_matter_id=case_matter_id,
        matter_fingerprint=matter_fingerprint or source.matter_fingerprint,
        client_party_id=client_party_id,
        subject_identity_fingerprint=subject_identity_fingerprint or source.subject_identity_fingerprint,
        evaluation_time=BASE,
        state=state,
        reason=(
            "CORRUPT_EVIDENCE" if state == "CORRUPT_BLOCKED"
            else "AMBIGUOUS_LIFECYCLE" if state == "AMBIGUOUS"
            else state
        ),
        matter_state=CaseMatterState.OPEN if state != "CORRUPT_BLOCKED" else None,
        matter_state_evidence_fingerprint=source.matter_fingerprint if state != "CORRUPT_BLOCKED" else None,
        formation_fingerprint=None if state == "CORRUPT_BLOCKED" else client_grant_fingerprint,
        lifecycle_evidence_fingerprints=lifecycle,
        decisive_lifecycle_evidence_fingerprints=decisive_lifecycle,
    )


def acknowledgment_projection(
    *,
    state: str = "ACKNOWLEDGED",
    tenant_id: str = TENANT,
    client_grant_id: str = "client-grant:l9b3",
    client_grant_fingerprint: str = GRANT_FP,
    case_matter_id: str = "matter-l9b3",
    matter_fingerprint: str | None = None,
    client_party_id: str = "party-l9b3",
    subject_identity_fingerprint: str | None = None,
    decisive_ids: tuple[str, ...] | None = None,
    decisive_fingerprints: tuple[str, ...] | None = None,
) -> LegalClientMatterMandateAcknowledgmentCurrentness:
    """Build a synthetic upstream acknowledgment-currentness value."""
    source = source_mandate()
    parsed = state
    if decisive_ids is None:
        decisive_ids = () if state in {"NO_DECISION", "CORRUPT_BLOCKED"} else ("firm-ack:l9b3",)
    if decisive_fingerprints is None:
        decisive_fingerprints = () if state in {"NO_DECISION", "CORRUPT_BLOCKED"} else (ACK_FP,)
    evidence = () if state == "CORRUPT_BLOCKED" else decisive_fingerprints
    return LegalClientMatterMandateAcknowledgmentCurrentness(
        currentness_id="ack-currentness-l9b12",
        tenant_id=tenant_id,
        client_grant_id=client_grant_id,
        client_grant_fingerprint=client_grant_fingerprint,
        case_matter_id=case_matter_id,
        matter_fingerprint=matter_fingerprint or source.matter_fingerprint,
        client_party_id=client_party_id,
        subject_identity_fingerprint=subject_identity_fingerprint or source.subject_identity_fingerprint,
        evaluation_time=BASE,
        state=parsed,
        reason=(
            "CORRUPT_EVIDENCE" if state == "CORRUPT_BLOCKED"
            else "AMBIGUOUS_DECISIONS" if state == "AMBIGUOUS"
            else state
        ),
        acknowledgment_evidence_fingerprints=evidence,
        decisive_acknowledgment_ids=decisive_ids,
        decisive_acknowledgment_fingerprints=decisive_fingerprints,
        decisive_decisions=(
            () if state in {"NO_DECISION", "CORRUPT_BLOCKED"}
            else ("ACKNOWLEDGED", "DECLINED") if state == "AMBIGUOUS"
            else tuple(state for _ in decisive_ids)
        ),
        corruption_evidence_fingerprints=(CORRUPTION_FP,) if state == "CORRUPT_BLOCKED" else (),
    )


def project(**changes: object) -> LegalClientMatterMandateCurrentness:
    """Build one synthetic projection with exact CURRENT upstream evidence."""
    source = cast(LegalClientMatterMandate, changes.pop("mandate", source_mandate()))
    values: dict[str, object] = {
        "tenant_id": source.tenant_id if source is not None else TENANT,
        "mandate_id": source.mandate_id if source is not None else "mandate-l9b3",
        "mandate": source,
        "grant_currentness": grant_projection(),
        "acknowledgment_currentness": acknowledgment_projection(),
        "evaluation_time": BASE + timedelta(hours=3),
    }
    values.update(changes)
    return project_legal_client_matter_mandate_currentness(**cast(Any, values))


def assert_code(code: str, operation: Any) -> None:
    """Assert one stable non-sensitive error code."""
    with pytest.raises(LegalClientMatterMandateCurrentnessError) as raised:
        operation()
    assert raised.value.code == code
    assert str(raised.value) == code


def test_schema_states_and_only_current_is_positive() -> None:
    value = project()
    assert value.schema == SCHEMA and value.currentness_version == VERSION
    assert value.state is LegalClientMatterMandateCurrentnessState.CURRENT
    assert value.reason_code is LegalClientMatterMandateCurrentnessReason.CURRENT
    assert value.is_current and value.is_usable
    assert set(value.to_dict()) == CURRENTNESS_FIELDS
    assert {state.value for state in LegalClientMatterMandateCurrentnessState} == {
        "FORMATION_ABSENT", "NOT_YET_EFFECTIVE", "EXPIRED", "GRANT_NOT_CURRENT",
        "ACKNOWLEDGMENT_NOT_CURRENT", "LINEAGE_MISMATCH", "AMBIGUOUS",
        "CORRUPT_BLOCKED", "CURRENT",
    }


def test_currentness_is_immutable_and_deterministic() -> None:
    first = project()
    second = project()
    assert first == second and first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 128
    assert first.to_dict()["fingerprint"] == first.fingerprint
    with pytest.raises(FrozenInstanceError):
        first.state = LegalClientMatterMandateCurrentnessState.EXPIRED  # type: ignore[misc]
    assert project(evaluation_time=BASE + timedelta(seconds=1)).fingerprint != first.fingerprint


def test_formation_absence_has_no_fabricated_evidence() -> None:
    value = project(mandate=None, grant_currentness=None, acknowledgment_currentness=None)
    assert value.state is LegalClientMatterMandateCurrentnessState.FORMATION_ABSENT
    assert not value.is_usable and value.mandate_fingerprint is None
    assert_code(
        "L9B12_P1_FORMATION_ABSENT_UPSTREAM_FORBIDDEN",
        lambda: project(mandate=None),
    )


@pytest.mark.parametrize(
    ("evaluation_time", "expected"),
    [
        (BASE + timedelta(hours=1), "NOT_YET_EFFECTIVE"),
        (BASE + timedelta(days=31), "EXPIRED"),
    ],
)
def test_temporal_states_are_explicit(evaluation_time: datetime, expected: str) -> None:
    value = project(evaluation_time=evaluation_time)
    assert str(value.state) == expected and not value.is_current


def test_grant_non_current_ambiguous_and_corrupt_states_fail_closed() -> None:
    assert str(project(grant_currentness=grant_projection(state="REVOKED", lifecycle=("a" * 128,), decisive_lifecycle=("a" * 128,))).state) == "GRANT_NOT_CURRENT"
    assert str(project(grant_currentness=grant_projection(state="AMBIGUOUS", lifecycle=("a" * 128, "b" * 128), decisive_lifecycle=("a" * 128, "b" * 128))).state) == "AMBIGUOUS"
    assert str(project(grant_currentness=grant_projection(state="CORRUPT_BLOCKED", lifecycle=("a" * 128,))).state) == "CORRUPT_BLOCKED"


@pytest.mark.parametrize("state", ["NO_DECISION", "DECLINED", "REQUIRES_REVIEW"])
def test_acknowledgment_non_positive_states_fail_closed(state: str) -> None:
    value = project(acknowledgment_currentness=acknowledgment_projection(state=state))
    assert str(value.state) == "ACKNOWLEDGMENT_NOT_CURRENT" and not value.is_current


def test_acknowledgment_ambiguity_and_corruption_have_precedence() -> None:
    ambiguous = project(acknowledgment_currentness=acknowledgment_projection(state="AMBIGUOUS", decisive_ids=("ack-1", "ack-2"), decisive_fingerprints=("a" * 128, "b" * 128)))
    corrupt = project(acknowledgment_currentness=acknowledgment_projection(state="CORRUPT_BLOCKED"))
    assert str(ambiguous.state) == "AMBIGUOUS"
    assert str(corrupt.state) == "CORRUPT_BLOCKED"


@pytest.mark.parametrize(
    "changes",
    [
        {"grant_currentness": grant_projection(tenant_id="other-tenant")},
        {"mandate": source_mandate(client_grant_fingerprint="a" * 128)},
        {"mandate": source_mandate(firm_acknowledgment_fingerprint="a" * 128)},
        {"grant_currentness": grant_projection(client_grant_id="other-grant")},
        {"grant_currentness": grant_projection(client_grant_fingerprint="a" * 128)},
        {"grant_currentness": grant_projection(case_matter_id="other-matter")},
        {"grant_currentness": grant_projection(client_party_id="other-party")},
        {"grant_currentness": grant_projection(subject_identity_fingerprint="b" * 128)},
        {"acknowledgment_currentness": acknowledgment_projection(tenant_id="other-tenant")},
        {"acknowledgment_currentness": acknowledgment_projection(client_grant_id="other-grant")},
        {"acknowledgment_currentness": acknowledgment_projection(client_grant_fingerprint="a" * 128)},
        {"acknowledgment_currentness": acknowledgment_projection(case_matter_id="other-matter")},
        {"acknowledgment_currentness": acknowledgment_projection(client_party_id="other-party")},
        {"acknowledgment_currentness": acknowledgment_projection(subject_identity_fingerprint="b" * 128)},
        {"acknowledgment_currentness": acknowledgment_projection(decisive_ids=("new-ack",), decisive_fingerprints=("a" * 128,))},
    ],
)
def test_exact_scope_and_lineage_mismatches_are_not_current(changes: dict[str, object]) -> None:
    value = project(**changes)
    assert value.state is LegalClientMatterMandateCurrentnessState.LINEAGE_MISMATCH
    assert not value.is_current


def test_later_acknowledgment_identity_invalidates_historical_mandate() -> None:
    value = project(
        acknowledgment_currentness=acknowledgment_projection(
            decisive_ids=("firm-ack:l9b3-successor",),
            decisive_fingerprints=("a" * 128,),
        )
    )
    assert value.state is LegalClientMatterMandateCurrentnessState.LINEAGE_MISMATCH


def test_precedence_is_deterministic_and_corruption_wins() -> None:
    value = project(
        acknowledgment_currentness=acknowledgment_projection(state="CORRUPT_BLOCKED"),
        evaluation_time=BASE + timedelta(hours=1),
    )
    assert value.state is LegalClientMatterMandateCurrentnessState.CORRUPT_BLOCKED


def test_strict_hydration_rejects_unknown_missing_malformed_and_tampered_payloads() -> None:
    value = project()
    restored = LegalClientMatterMandateCurrentness.from_dict(value.to_dict())
    assert restored == value
    assert_code("L9B12_P1_SCHEMA_INVALID", lambda: LegalClientMatterMandateCurrentness.from_dict({**value.to_dict(), "extra": 1}))
    missing = value.to_dict()
    del missing["state"]
    assert_code("L9B12_P1_SCHEMA_INVALID", lambda: LegalClientMatterMandateCurrentness.from_dict(missing))
    tampered = value.to_dict()
    tampered["reason"] = "EXPIRED"
    assert_code("L9B12_P1_REASON_STATE_MISMATCH", lambda: LegalClientMatterMandateCurrentness.from_dict(tampered))
    assert_code("L9B12_P1_STATE_INVALID", lambda: LegalClientMatterMandateCurrentness.from_dict({**value.to_dict(), "state": "UNKNOWN", "fingerprint": value.fingerprint}))


def test_aware_evaluation_time_and_no_hidden_clock_are_required() -> None:
    assert project(evaluation_time=BASE.replace(tzinfo=timezone(timedelta(hours=2)))).evaluation_time.tzinfo is timezone.utc
    assert_code("L9B12_P1_EVALUATION_TIME_INVALID", lambda: project(evaluation_time=BASE.replace(tzinfo=None)))


def test_source_mandate_is_not_mutated_and_no_external_authority_is_imported() -> None:
    source = source_mandate()
    before = source.to_dict()
    project(mandate=source)
    assert source.to_dict() == before
    module = ast.parse(Path("tools/eos/legal_operations/domain/legal_client_matter_mandate_currentness.py").read_text())
    forbidden = {"pymongo", "motor", "mongo", "registry", "time", "requests", "httpx", "jwt"}
    imported = {
        node.module.split(".")[0]
        for node in ast.walk(module)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    imported.update(alias.name.split(".")[0] for node in ast.walk(module) if isinstance(node, ast.Import) for alias in node.names)
    assert imported.isdisjoint(forbidden)
    source_text = Path("tools/eos/legal_operations/domain/legal_client_matter_mandate_currentness.py").read_text()
    assert "datetime.now" not in source_text and "utcnow" not in source_text


def test_public_contract_does_not_expose_downstream_authority() -> None:
    payload = project().to_dict()
    assert "engagement" not in payload and "acceptance" not in payload and "financial" not in payload
    assert all(not isinstance(value, (bytes, bytearray)) for value in payload.values())


# ARTIFACT: test_legal_client_matter_mandate_currentness.py
# VERSION: v1.0.0-L9B12-P1-CLIENT-MATTER-MANDATE-CURRENTNESS-CERT
# AUTHORITY BOUNDARY: direct pure projection certificate only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
