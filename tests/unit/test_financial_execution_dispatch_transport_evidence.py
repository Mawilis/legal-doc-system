"""Unit certification for immutable internal transport evidence.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-DISPATCH-TRANSPORT-EVIDENCE-UNIT-CERT
AUTHORITY: Wilsy transport facts only; no provider outcome, execution truth, or settlement.
EPITOME: Certifies append-only disposition events and deterministic evidence fingerprints.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_financial_execution_dispatch_transport_evidence.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
CERTIFICATION DATE: 2026-08-28
COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque synthetic references only; no payloads or credentials.
TENANT BOUNDARY: event lineage is explicit, immutable, and tenant-scoped.
FINANCIAL AUTHORITY BOUNDARY: transport evidence is not provider execution truth or settlement.
CHANGELOG: v1.0.0 certifies dispositions, lineage, response-reference fencing, and SHA3-512 evidence integrity.
"""
from datetime import datetime, timezone
import hashlib
import json

import pytest

from tools.eos.kennel.domain.financial_execution_dispatch_transport_evidence import (
    FinancialExecutionDispatchTransportEvidence,
    FinancialExecutionDispatchTransportEvidenceError,
    TransportEvidenceDisposition,
)


NOW = datetime(2026, 8, 28, 12, tzinfo=timezone.utc)
FP = "a" * 128


def evidence(**changes: object) -> FinancialExecutionDispatchTransportEvidence:
    values: dict[str, object] = {
        "transport_evidence_id": "evidence-1",
        "tenant_id": "tenant-1",
        "execution_command_id": "command-1",
        "execution_attempt_id": "attempt-1",
        "dispatch_claim_id": "claim-1",
        "provider_name": "PAYSHAP",
        "transport_correlation_id": "correlation-1",
        "transport_material_fingerprint": FP,
        "transport_disposition": TransportEvidenceDisposition.SEND_STARTED,
        "recorded_at": NOW,
    }
    values.update(changes)
    return FinancialExecutionDispatchTransportEvidence(**values)  # type: ignore[arg-type]


def test_send_started_preserves_lineage_and_has_no_response_reference() -> None:
    value = evidence()
    assert value.transport_disposition is TransportEvidenceDisposition.SEND_STARTED
    assert value.response_evidence_reference is None
    assert (value.tenant_id, value.execution_command_id, value.execution_attempt_id, value.dispatch_claim_id) == ("tenant-1", "command-1", "attempt-1", "claim-1")
    assert value.provider_name == "PAYSHAP"
    assert value.transport_correlation_id == "correlation-1"
    assert value.transport_material_fingerprint == FP
    assert value.recorded_at == NOW


@pytest.mark.parametrize("disposition", [TransportEvidenceDisposition.SENT, TransportEvidenceDisposition.AMBIGUOUS])
def test_non_response_dispositions_are_valid_without_response_reference(disposition: TransportEvidenceDisposition) -> None:
    assert evidence(transport_disposition=disposition).transport_disposition is disposition


def test_response_received_requires_opaque_response_reference() -> None:
    value = evidence(transport_disposition=TransportEvidenceDisposition.RESPONSE_RECEIVED, response_evidence_reference="secure-response-ref")
    assert value.response_evidence_reference == "secure-response-ref"


@pytest.mark.parametrize("disposition", list(TransportEvidenceDisposition))
def test_disposition_enum_is_closed_and_provider_states_absent(disposition: TransportEvidenceDisposition) -> None:
    assert disposition.value in {"SEND_STARTED", "SENT", "RESPONSE_RECEIVED", "AMBIGUOUS"}
    assert "NOT_SENT" not in TransportEvidenceDisposition.__members__
    assert not {"ACCEPTED", "EXECUTED", "FAILED", "SETTLED", "UNKNOWN"}.intersection(TransportEvidenceDisposition.__members__)


@pytest.mark.parametrize("disposition", [TransportEvidenceDisposition.SEND_STARTED, TransportEvidenceDisposition.SENT, TransportEvidenceDisposition.AMBIGUOUS])
def test_response_reference_is_forbidden_except_on_response_received(disposition: TransportEvidenceDisposition) -> None:
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceError):
        evidence(transport_disposition=disposition, response_evidence_reference="response-ref")


def test_response_received_without_reference_fails_closed() -> None:
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceError):
        evidence(transport_disposition=TransportEvidenceDisposition.RESPONSE_RECEIVED)


@pytest.mark.parametrize("value", ["", " "])
def test_response_reference_must_be_opaque_nonblank(value: str) -> None:
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceError):
        evidence(transport_disposition=TransportEvidenceDisposition.RESPONSE_RECEIVED, response_evidence_reference=value)


@pytest.mark.parametrize("field", ["execution_command_id", "execution_attempt_id", "dispatch_claim_id", "transport_correlation_id"])
def test_evidence_identity_collisions_fail_closed(field: str) -> None:
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceError):
        evidence(transport_evidence_id="command-1" if field == "execution_command_id" else "attempt-1" if field == "execution_attempt_id" else "claim-1" if field == "dispatch_claim_id" else "correlation-1" if field == "transport_correlation_id" else "evidence-1")


@pytest.mark.parametrize("field", ["tenant_id", "execution_command_id", "execution_attempt_id", "dispatch_claim_id", "provider_name", "transport_correlation_id"])
def test_required_lineage_is_nonblank(field: str) -> None:
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceError):
        evidence(**{field: " "})


@pytest.mark.parametrize("value", ["", "x", "A" * 128, "g" * 128])
def test_transport_material_fingerprint_requires_lowercase_sha3_512(value: str) -> None:
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceError):
        evidence(transport_material_fingerprint=value)


def test_recorded_at_requires_timezone_awareness() -> None:
    with pytest.raises(FinancialExecutionDispatchTransportEvidenceError):
        evidence(recorded_at=datetime(2026, 8, 28, 12))


def test_canonical_payload_is_sorted_compact_and_explicit_null() -> None:
    value = evidence()
    payload = value.canonical_payload()
    assert list(payload) == sorted(payload)
    assert payload["response_evidence_reference"] is None
    expected = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    assert value.canonical_bytes() == expected
    assert b'"response_evidence_reference":null' in value.canonical_bytes()


def test_event_fingerprint_uses_sha3_512_and_is_replay_deterministic() -> None:
    first, second = evidence(), evidence()
    digest = hashlib.sha3_512(first.canonical_bytes()).hexdigest()
    assert first == second
    assert first.canonical_bytes() == second.canonical_bytes()
    assert first.fingerprint == second.fingerprint == digest
    assert len(digest) == 128 and digest == digest.lower() and all(c in "0123456789abcdef" for c in digest)


@pytest.mark.parametrize("field,value", [("tenant_id", "tenant-2"), ("execution_command_id", "command-2"), ("execution_attempt_id", "attempt-2"), ("dispatch_claim_id", "claim-2"), ("provider_name", "ZAPPER"), ("transport_correlation_id", "correlation-2"), ("transport_material_fingerprint", "b" * 128), ("recorded_at", datetime(2026, 8, 29, tzinfo=timezone.utc))])
def test_each_semantic_event_field_changes_fingerprint(field: str, value: object) -> None:
    changed = evidence(**{field: value})
    assert changed.canonical_bytes() != evidence().canonical_bytes()
    assert changed.fingerprint != evidence().fingerprint


def test_append_only_and_provider_outcome_boundaries() -> None:
    value = evidence()
    with pytest.raises(AttributeError):
        value.transport_disposition = TransportEvidenceDisposition.SENT  # type: ignore[misc]
    fields = set(value.__dict__)
    forbidden = {"provider_request_reference", "provider_execution_reference", "provider_evidence_reference", "provider_occurred_at", "observation_status", "executed_at", "settled_at", "payload", "headers", "body"}
    assert not fields.intersection(forbidden)
    assert "NOT_SENT" not in {item.value for item in TransportEvidenceDisposition}


# ARTIFACT: test_financial_execution_dispatch_transport_evidence.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-DISPATCH-TRANSPORT-EVIDENCE-UNIT-CERT
# AUTHORITY BOUNDARY: tests certify Wilsy internal transport evidence only.
# TENANT POSTURE: all event lineage remains explicit and tenant-scoped.
# FAIL-CLOSED POSTURE: invalid identity, response-reference, fingerprint, disposition, and timestamp inputs reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; execution is not settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
