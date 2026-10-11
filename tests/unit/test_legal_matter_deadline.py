"""Direct certificate for the D1 pure legal-matter deadline domain.

TITLE: Wilsy OS Legal Matter Deadline Pure Domain Certificate
VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D1-DEADLINE-DOMAIN-CERT
AUTHORITY: Wilsy OS Core Governance / direct pure-domain certificate
EPITOME: Prove exact tenant/matter/source binding, immutable SHA3-512 evidence,
         strict hydration, and non-authoritative temporal observation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_matter_deadline.py
COLLABORATION / OWNERSHIP: Direct certificate for legal_matter_deadline.py only;
                            D2 persistence and later API/client wiring are absent.
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0-LEGAL-OPS-COMPLETION-D1-DEADLINE-DOMAIN-CERT
           establishes adversarial pure-domain and authority-boundary evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque values only; no real legal data.
TENANT BOUNDARY: Every fixture binds one explicit tenant and matter.
AUTHORITY BOUNDARY: Pure deadline evidence certificate; no court, filing,
                    service, representation, persistence, calendar, or AI power.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Any semantic, schema, time, or digest drift fails.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone
import hashlib
import json
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_matter_deadline import (
    DEADLINE_FIELDS,
    LegalMatterDeadline,
    LegalMatterDeadlineError,
    LegalMatterDeadlineKind,
    LegalMatterDeadlineSourceType,
    LegalMatterDeadlineStatus,
    LegalMatterDeadlineTemporalPosture,
)


VERSION = "v1.0.0-LEGAL-OPS-COMPLETION-D1-DEADLINE-DOMAIN-CERT"
CREATED = datetime(2026, 10, 11, 8, 0, tzinfo=timezone.utc)
DUE = datetime(2026, 10, 18, 8, 0, tzinfo=timezone.utc)
SOURCE_FINGERPRINT = "a" * 128


def _deadline(**overrides: object) -> LegalMatterDeadline:
    values: dict[str, object] = {
        "tenant_id": "tenant-legal-a",
        "case_matter_id": "matter-001",
        "deadline_id": "deadline-001",
        "deadline_kind": LegalMatterDeadlineKind.FILING,
        "title": "Evidenced filing deadline",
        "due_at": DUE,
        "source_type": LegalMatterDeadlineSourceType.COURT_ORDER,
        "source_reference": "evidence://court-order/order-001",
        "source_evidence_fingerprint": SOURCE_FINGERPRINT,
        "jurisdiction_reference": "jurisdiction://court/example",
        "created_at": CREATED,
        "supersedes_deadline_id": None,
        "status": LegalMatterDeadlineStatus.ACTIVE,
    }
    values.update(overrides)
    return LegalMatterDeadline(**values)  # type: ignore[arg-type]


def test_canonical_deadline_is_exact_utc_immutable_sha3_512_evidence() -> None:
    value = _deadline(
        due_at=DUE.astimezone(timezone(timedelta(hours=2))),
        created_at=CREATED.astimezone(timezone(timedelta(hours=-4))),
    )
    assert value.tenant_id == "tenant-legal-a"
    assert value.case_matter_id == "matter-001"
    assert value.due_at == DUE
    assert value.created_at == CREATED
    assert len(value.fingerprint) == 128
    int(value.fingerprint, 16)
    with pytest.raises(FrozenInstanceError):
        value.title = "mutated"  # type: ignore[misc]


def test_fingerprint_is_deterministic_and_matches_canonical_sha3_512() -> None:
    first = _deadline()
    second = _deadline()
    payload = first.to_dict()
    fingerprint = payload.pop("fingerprint")
    expected = hashlib.sha3_512(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=False,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    assert first.fingerprint == second.fingerprint == fingerprint == expected


@pytest.mark.parametrize(
    "change",
    (
        {"tenant_id": "tenant-legal-b"},
        {"case_matter_id": "matter-002"},
        {"due_at": DUE + timedelta(seconds=1)},
        {"source_evidence_fingerprint": "b" * 128},
        {"status": LegalMatterDeadlineStatus.SATISFIED},
        {"supersedes_deadline_id": "deadline-earlier"},
    ),
)
def test_authority_bearing_semantic_changes_change_fingerprint(
    change: dict[str, object],
) -> None:
    assert _deadline(**change).fingerprint != _deadline().fingerprint


@pytest.mark.parametrize("field", ("due_at", "created_at"))
def test_naive_datetime_is_rejected(field: str) -> None:
    with pytest.raises(LegalMatterDeadlineError):
        _deadline(**{field: datetime(2026, 10, 11, 8, 0)})


@pytest.mark.parametrize(
    ("change", "code"),
    (
        ({"tenant_id": ""}, "D1_TENANT_ID_INVALID"),
        ({"case_matter_id": ""}, "D1_CASE_MATTER_ID_INVALID"),
        ({"deadline_id": ""}, "D1_DEADLINE_ID_INVALID"),
        ({"title": ""}, "D1_TITLE_INVALID"),
        ({"source_reference": ""}, "D1_SOURCE_REFERENCE_INVALID"),
        ({"jurisdiction_reference": ""}, "D1_JURISDICTION_REFERENCE_INVALID"),
        ({"source_evidence_fingerprint": "bad"}, "D1_SOURCE_EVIDENCE_FINGERPRINT_INVALID"),
        ({"supersedes_deadline_id": ""}, "D1_SUPERSEDES_DEADLINE_ID_INVALID"),
        ({"supersedes_deadline_id": "deadline-001"}, "D1_SELF_SUPERSESSION_FORBIDDEN"),
    ),
)
def test_malformed_required_material_fails_closed(
    change: dict[str, object], code: str
) -> None:
    with pytest.raises(LegalMatterDeadlineError, match=code):
        _deadline(**change)


@pytest.mark.parametrize(
    "change",
    (
        {"deadline_kind": "UNKNOWN"},
        {"source_type": "INFERRED_BY_AI"},
        {"status": "OVERDUE"},
    ),
)
def test_unknown_closed_vocabulary_is_rejected(change: dict[str, object]) -> None:
    with pytest.raises(LegalMatterDeadlineError, match="D1_CLASSIFICATION_INVALID"):
        _deadline(**change)


def test_temporal_posture_is_pure_and_requires_explicit_aware_time() -> None:
    value = _deadline()
    assert value.temporal_posture(DUE - timedelta(microseconds=1)) is LegalMatterDeadlineTemporalPosture.UPCOMING
    assert value.temporal_posture(DUE) is LegalMatterDeadlineTemporalPosture.DUE
    assert value.temporal_posture(DUE + timedelta(microseconds=1)) is LegalMatterDeadlineTemporalPosture.OVERDUE
    assert value.status is LegalMatterDeadlineStatus.ACTIVE
    with pytest.raises(LegalMatterDeadlineError, match="D1_OBSERVATION_AT_INVALID"):
        value.temporal_posture(datetime(2026, 10, 18, 8, 0))


@pytest.mark.parametrize(
    "status",
    (
        LegalMatterDeadlineStatus.SATISFIED,
        LegalMatterDeadlineStatus.SUPERSEDED,
        LegalMatterDeadlineStatus.CANCELLED,
    ),
)
def test_inactive_lifecycle_facts_never_become_overdue_authority(
    status: LegalMatterDeadlineStatus,
) -> None:
    value = _deadline(status=status)
    assert value.temporal_posture(DUE + timedelta(days=100)) is LegalMatterDeadlineTemporalPosture.INACTIVE
    assert value.status is status


def test_exact_serialization_hydration_round_trip_and_corruption_rejection() -> None:
    value = _deadline(supersedes_deadline_id="deadline-earlier")
    payload = value.to_dict()
    assert set(payload) == DEADLINE_FIELDS
    assert LegalMatterDeadline.from_dict(payload) == value
    corrupted = dict(payload)
    corrupted["title"] = "corrupted"
    with pytest.raises(LegalMatterDeadlineError, match="D1_FINGERPRINT_MISMATCH"):
        LegalMatterDeadline.from_dict(corrupted)
    extra = dict(payload)
    extra["payment_authority"] = True
    with pytest.raises(LegalMatterDeadlineError, match="D1_SCHEMA_INVALID"):
        LegalMatterDeadline.from_dict(extra)


def test_caller_supplied_fingerprint_mismatch_is_rejected() -> None:
    with pytest.raises(LegalMatterDeadlineError, match="D1_FINGERPRINT_MISMATCH"):
        _deadline(fingerprint="f" * 128)


def test_domain_exposes_no_financial_ai_or_inferred_authority_fields() -> None:
    names = {field.name for field in fields(LegalMatterDeadline)}
    forbidden = {
        "payment",
        "settlement",
        "paid_state",
        "financial_execution",
        "ai_generated",
        "ai_inferred_due_at",
        "filing_completed",
        "service_completed",
        "court_authority",
    }
    assert names.isdisjoint(forbidden)
    assert "OVERDUE" not in {status.value for status in LegalMatterDeadlineStatus}


# ARTIFACT: test_legal_matter_deadline.py
# VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D1-DEADLINE-DOMAIN-CERT
# AUTHORITY BOUNDARY: direct pure-domain deadline evidence certificate only
# TENANT POSTURE: every fixture binds one exact tenant_id and case_matter_id
# FAIL-CLOSED POSTURE: malformed semantic, schema, chronology, and fingerprint material reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
