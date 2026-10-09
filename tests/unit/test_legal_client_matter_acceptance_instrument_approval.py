"""Direct certificate for the L9A4-P2B1 approval evidence domain.

TITLE: WILSY OS Legal Client Matter Acceptance Instrument Approval Certificate
VERSION: v1.0.0-L9A4-P2B1-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify immutable APPROVED/REJECTED evidence, exact CaseMatter and
         instrument binding, dual fingerprints, chronology, strict hydration,
         and the absence of currentness, acceptance, engagement, Court, and
         financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_acceptance_instrument_approval.py
COLLABORATION / OWNERSHIP: Synthetic in-memory evidence only; this certificate
                            does not create a registry, IAM path, service,
                            currentness composer, API, UI, or Mongo state.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P2B1-MATTER-ACCEPTANCE-INSTRUMENT-APPROVAL-CERT proves
           valid decisions, exact subject derivation, immutable evidence,
           chronology, idempotency, strict hydration, tamper rejection, and
           authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only;
                             no PII, secrets, tokens, raw document body,
                             network, persistence, or financial execution.
TENANT BOUNDARY: Fixtures use one exact synthetic tenant and CaseMatter.
AUTHORITY BOUNDARY: Pure historical approval-decision evidence only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import fields
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain import (
    legal_client_matter_acceptance_instrument_approval as approval,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    record_legal_client_matter_acceptance_instrument,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter


UTC = timezone.utc
NOW = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=UTC)
MATTER_FINGERPRINT = hashlib.sha3_512(b"approval-matter").hexdigest()
CONTENT_FINGERPRINT = hashlib.sha3_512(b"approval-content").hexdigest()
AUTHORIZATION_FINGERPRINT = hashlib.sha3_512(b"approval-authorization").hexdigest()
EVIDENCE_FINGERPRINT = hashlib.sha3_512(b"approval-evidence").hexdigest()

MATTER = CaseMatter(
    tenant_id="tenant-approval",
    case_matter_id="matter-approval-001",
    matter_reference="matter-reference-001",
    opened_at=NOW,
    evidence_reference="evidence:matter-open-001",
)


def _instrument(**changes: object):
    """Build one certified predecessor instrument with synthetic evidence."""
    values: dict[str, object] = {
        "case_matter": MATTER,
        "instrument_id": "instrument-approval-001",
        "version": "1.0.0",
        "instrument_kind": "CLIENT_REVIEW",
        "title": "Matter review instrument",
        "review_scope": "Review this exact bounded matter material.",
        "content_reference": "artifact:matter-approval-001/instrument/v1",
        "content_fingerprint": CONTENT_FINGERPRINT,
        "created_at": NOW,
        "effective_from": NOW,
        "approval_evidence_reference": "provenance:authoring-001",
        "approval_evidence_fingerprint": EVIDENCE_FINGERPRINT,
    }
    values.update(changes)
    return record_legal_client_matter_acceptance_instrument(**cast(Any, values))


def _approval(**changes: object) -> approval.LegalClientMatterAcceptanceInstrumentApproval:
    """Build one exact approval from canonical CaseMatter/instrument fixtures."""
    values: dict[str, object] = {
        "case_matter": MATTER,
        "instrument": _instrument(),
        "approval_id": "approval-001",
        "decision": approval.LegalClientMatterAcceptanceInstrumentApprovalDecision.APPROVED,
        "approver_principal_id": "principal-approver-001",
        "approver_capacity_reference": "capacity:firm-approval-001",
        "authorization_evidence_reference": "authorization:approval-001",
        "authorization_evidence_fingerprint": AUTHORIZATION_FINGERPRINT,
        "approval_evidence_reference": "decision-evidence:approval-001",
        "approval_evidence_fingerprint": EVIDENCE_FINGERPRINT,
        "occurred_at": NOW,
        "effective_from": NOW,
        "idempotency_key": "idempotency:approval-001",
    }
    values.update(changes)
    return approval.record_legal_client_matter_acceptance_instrument_approval(
        **cast(Any, values)
    )


def _reject(**changes: object) -> None:
    """Assert one bounded approval-domain rejection."""
    with pytest.raises(approval.LegalClientMatterAcceptanceInstrumentApprovalError):
        _approval(**changes)


def test_valid_approved_and_rejected_decisions_are_distinct_immutable_evidence() -> None:
    approved = _approval()
    rejected = _approval(
        approval_id="approval-002",
        decision=approval.LegalClientMatterAcceptanceInstrumentApprovalDecision.REJECTED,
        approval_evidence_reference="decision-evidence:approval-002",
        idempotency_key="idempotency:approval-002",
    )
    assert approved.decision is approval.LegalClientMatterAcceptanceInstrumentApprovalDecision.APPROVED
    assert rejected.decision is approval.LegalClientMatterAcceptanceInstrumentApprovalDecision.REJECTED
    assert approved.fingerprint != rejected.fingerprint
    with pytest.raises((AttributeError, TypeError)):
        approved.decision = approval.LegalClientMatterAcceptanceInstrumentApprovalDecision.REJECTED  # type: ignore[misc]


def test_exact_subject_and_dual_fingerprint_binding() -> None:
    value = _approval()
    instrument = _instrument()
    assert value.tenant_id == MATTER.tenant_id
    assert value.case_matter_id == MATTER.case_matter_id
    assert value.matter_fingerprint == MATTER.fingerprint
    assert value.instrument_id == instrument.instrument_id
    assert value.version == instrument.version
    assert value.instrument_fingerprint == instrument.fingerprint
    assert value.content_fingerprint == instrument.content_fingerprint
    assert value.version_id == "instrument-approval-001:1.0.0"


def test_factory_derives_canonical_subject_and_requires_open_matter() -> None:
    value = _approval()
    assert value.tenant_id == MATTER.tenant_id
    assert value.matter_fingerprint == MATTER.fingerprint

    closed = MATTER.transition_to(
        type(MATTER.state).CLOSED,
        evidence_reference="evidence:matter-closed-001",
        occurred_at=NOW + timedelta(minutes=1),
    )
    with pytest.raises(approval.LegalClientMatterAcceptanceInstrumentApprovalError):
        approval.record_legal_client_matter_acceptance_instrument_approval(
            case_matter=closed,
            instrument=_instrument(),
            approval_id="approval-closed",
            decision="APPROVED",
            approver_principal_id="principal-approver-001",
            approver_capacity_reference="capacity:firm-approval-001",
            authorization_evidence_reference="authorization:approval-closed",
            authorization_evidence_fingerprint=AUTHORIZATION_FINGERPRINT,
            approval_evidence_reference="decision-evidence:approval-closed",
            approval_evidence_fingerprint=EVIDENCE_FINGERPRINT,
            occurred_at=NOW,
            effective_from=NOW,
            idempotency_key="idempotency:approval-closed",
        )


def test_factory_rejects_cross_matter_instrument() -> None:
    other = CaseMatter(
        tenant_id="tenant-other",
        case_matter_id="matter-other",
        matter_reference="matter-reference-other",
        opened_at=NOW,
        evidence_reference="evidence:matter-other",
    )
    with pytest.raises(approval.LegalClientMatterAcceptanceInstrumentApprovalError):
        approval.record_legal_client_matter_acceptance_instrument_approval(
            case_matter=other,
            instrument=_instrument(),
            approval_id="approval-cross-matter",
            decision="APPROVED",
            approver_principal_id="principal-approver-001",
            approver_capacity_reference="capacity:firm-approval-001",
            authorization_evidence_reference="authorization:cross-matter",
            authorization_evidence_fingerprint=AUTHORIZATION_FINGERPRINT,
            approval_evidence_reference="decision-evidence:cross-matter",
            approval_evidence_fingerprint=EVIDENCE_FINGERPRINT,
            occurred_at=NOW,
            effective_from=NOW,
            idempotency_key="idempotency:cross-matter",
        )


def test_utc_normalization_preserves_microseconds_and_naive_is_rejected() -> None:
    offset = timezone(timedelta(hours=2))
    value = _approval(
        occurred_at=datetime(2026, 9, 26, 14, 0, 0, 123456, tzinfo=offset),
        effective_from=datetime(2026, 9, 26, 14, 0, 0, 123456, tzinfo=offset),
    )
    assert value.occurred_at == NOW
    assert value.effective_from.microsecond == 123456
    assert value.to_dict()["occurred_at"] == "2026-09-26T12:00:00.123456Z"
    _reject(occurred_at=datetime(2026, 9, 26, 12, 0, 0, 123456))
    _reject(effective_from=datetime(2026, 9, 26, 12, 0, 0, 123456))


def test_effective_from_cannot_precede_decision() -> None:
    _reject(effective_from=NOW - timedelta(microseconds=1))


def test_idempotency_and_actor_evidence_are_bound_without_authentication() -> None:
    value = _approval()
    assert value.approval_id == "approval-001"
    assert value.approver_principal_id == "principal-approver-001"
    assert value.approver_capacity_reference == "capacity:firm-approval-001"
    assert value.authorization_evidence_reference.startswith("authorization:")
    assert value.authorization_evidence_fingerprint == AUTHORIZATION_FINGERPRINT
    assert value.approval_evidence_reference.startswith("decision-evidence:")
    assert value.approval_evidence_fingerprint == EVIDENCE_FINGERPRINT
    assert value.idempotency_key == "idempotency:approval-001"
    assert "currentness" in (inspect.getdoc(value.__class__) or "").lower()


def test_fingerprint_is_deterministic_and_semantic_mutations_change_it() -> None:
    first = _approval()
    second = _approval()
    assert first.fingerprint == second.fingerprint
    for field, replacement in (
        ("approval_id", "approval-mutated"),
        ("decision", "REJECTED"),
        ("approver_principal_id", "principal-other"),
        ("idempotency_key", "idempotency-other"),
    ):
        assert _approval(**{field: replacement}).fingerprint != first.fingerprint
    changed_instrument = _instrument(
        content_fingerprint=hashlib.sha3_512(b"other-content").hexdigest()
    )
    assert _approval(instrument=changed_instrument).fingerprint != first.fingerprint


def test_exact_hydration_round_trip() -> None:
    value = _approval(
        decision=approval.LegalClientMatterAcceptanceInstrumentApprovalDecision.REJECTED
    )
    hydrated = approval.LegalClientMatterAcceptanceInstrumentApproval.from_dict(
        value.to_dict()
    )
    assert hydrated == value
    assert hydrated.to_dict() == value.to_dict()


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("tenant_id", "default"),
        ("tenant_id", ""),
        ("case_matter_id", "bad matter"),
        ("matter_fingerprint", "g" * 128),
        ("approval_id", "bad approval"),
        ("instrument_id", "bad instrument"),
        ("version", ""),
        ("instrument_fingerprint", "bad"),
        ("content_fingerprint", "A" * 128),
        ("approver_principal_id", "bad principal"),
        ("approver_capacity_reference", "capacity:\ninvalid"),
        ("authorization_evidence_reference", "authorization:\x00invalid"),
        ("authorization_evidence_fingerprint", "bad"),
        ("approval_evidence_reference", "decision:\ud800invalid"),
        ("approval_evidence_fingerprint", "bad"),
        ("idempotency_key", "idempotency:\ninvalid"),
    ],
)
def test_malformed_subject_actor_or_evidence_rejects(
    field: str,
    replacement: object,
) -> None:
    payload = _approval().to_dict()
    payload[field] = replacement
    with pytest.raises(approval.LegalClientMatterAcceptanceInstrumentApprovalError):
        approval.LegalClientMatterAcceptanceInstrumentApproval.from_dict(payload)


def test_invalid_decision_rejects() -> None:
    _reject(decision="PENDING")
    _reject(decision="WITHDRAWN")


def test_schema_version_and_fingerprint_tampering_reject() -> None:
    value = _approval()
    payload = value.to_dict()
    payload["schema"] = approval.SCHEMA + "/tampered"
    with pytest.raises(approval.LegalClientMatterAcceptanceInstrumentApprovalError):
        approval.LegalClientMatterAcceptanceInstrumentApproval.from_dict(payload)
    payload = value.to_dict()
    payload["approval_version"] = approval.VERSION + "-tampered"
    with pytest.raises(approval.LegalClientMatterAcceptanceInstrumentApprovalError):
        approval.LegalClientMatterAcceptanceInstrumentApproval.from_dict(payload)
    payload = value.to_dict()
    payload["fingerprint"] = "0" * 128
    with pytest.raises(approval.LegalClientMatterAcceptanceInstrumentApprovalError):
        approval.LegalClientMatterAcceptanceInstrumentApproval.from_dict(payload)


def test_strict_hydration_rejects_missing_extra_and_invalid_enum_fields() -> None:
    value = _approval().to_dict()
    missing = deepcopy(value)
    del missing["approval_id"]
    with pytest.raises(approval.LegalClientMatterAcceptanceInstrumentApprovalError):
        approval.LegalClientMatterAcceptanceInstrumentApproval.from_dict(missing)
    extra = deepcopy(value)
    extra["status"] = "ACTIVE"
    with pytest.raises(approval.LegalClientMatterAcceptanceInstrumentApprovalError):
        approval.LegalClientMatterAcceptanceInstrumentApproval.from_dict(extra)
    invalid = deepcopy(value)
    invalid["decision"] = "PENDING"
    with pytest.raises(approval.LegalClientMatterAcceptanceInstrumentApprovalError):
        approval.LegalClientMatterAcceptanceInstrumentApproval.from_dict(invalid)


def test_no_lifecycle_expiry_or_client_authority_fields_exist() -> None:
    names = {field.name for field in fields(approval.LegalClientMatterAcceptanceInstrumentApproval)}
    assert "status" not in names
    assert "prior_status" not in names
    assert "effective_until" not in names
    assert "expires_at" not in names
    assert "party_id" not in names
    assert "subject_reference" not in names
    assert "client_principal_id" not in names
    assert "engagement_id" not in names
    assert "representation_id" not in names
    assert "court_authority_reference" not in names


def test_public_surface_has_no_persistence_or_transport_authority() -> None:
    source = inspect.getsource(approval)
    forbidden = (
        "pymongo",
        "MongoClient",
        "requests.",
        "httpx.",
        "jwt.",
    )
    assert not any(token in source for token in forbidden)
    assert "currentness" in (inspect.getdoc(approval.LegalClientMatterAcceptanceInstrumentApproval) or "").lower()


def test_no_client_pii_or_raw_content_is_required() -> None:
    names = {field.name for field in fields(approval.LegalClientMatterAcceptanceInstrumentApproval)}
    assert "email" not in names
    assert "address" not in names
    assert "identity_number" not in names
    assert "content" not in names
    assert _approval().to_dict()["content_fingerprint"] == CONTENT_FINGERPRINT
