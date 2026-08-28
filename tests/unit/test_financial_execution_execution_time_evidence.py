# -*- coding: utf-8 -*-
"""Unit certification for explicit execution-time authority evidence.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TIME-EVIDENCE-UNIT-CERT
PURPOSE: certify explicit, provider-neutral execution timestamps without inference.
AUTHORITY: pure domain certification; no persistence, truth, or settlement authority.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
DATE: 2026-08-28 | COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: opaque references only; no credentials or payloads.
TENANT BOUNDARY: all identities are explicit and tenant-bound.
TRUTH / SETTLEMENT BOUNDARY: the contract creates no FinancialExecutionTruth and defines no settlement.
DETERMINISM: fixed aware timestamps; no I/O, clocks, randomness, or external services.
CHANGELOG: v1.0.0 establishes execution-time evidence authority unit certification.
"""
from datetime import datetime, timedelta, timezone
import inspect
from typing import Any, cast

import pytest

from tools.eos.kennel.domain.financial_execution_execution_time_evidence import (
    ExecutionTimeAuthorityKind,
    FinancialExecutionTimeEvidence,
    FinancialExecutionTimeEvidenceError,
)
from tools.eos.kennel.domain.financial_execution_provider_observation import EvidenceStrength

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)


def evidence(**changes):
    """Build deterministic valid execution-time evidence."""
    values = {
        "tenant_id": "tenant",
        "execution_attempt_id": "attempt",
        "provider_name": "provider",
        "provider_execution_reference": "provider-execution",
        "evidence_reference": "evidence",
        "executed_at": NOW,
        "authority_kind": ExecutionTimeAuthorityKind.PROVIDER_EXECUTION_CONFIRMATION,
        "evidence_strength": EvidenceStrength.AUTHENTICATED,
    }
    values.update(changes)
    return FinancialExecutionTimeEvidence(**values)


def test_valid_construction_and_field_preservation():
    item = evidence()
    assert item.tenant_id == "tenant"
    assert item.execution_attempt_id == "attempt"
    assert item.provider_name == "provider"
    assert item.provider_execution_reference == "provider-execution"
    assert item.evidence_reference == "evidence"
    assert item.executed_at == NOW


def test_aware_datetime_accepted_and_naive_rejected():
    assert evidence(executed_at=datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=2))))
    with pytest.raises(FinancialExecutionTimeEvidenceError):
        evidence(executed_at=datetime(2026, 1, 1))


@pytest.mark.parametrize(
    "field",
    [
        "tenant_id",
        "execution_attempt_id",
        "provider_name",
        "provider_execution_reference",
        "evidence_reference",
    ],
)
def test_identity_fields_reject_blank(field):
    with pytest.raises(FinancialExecutionTimeEvidenceError):
        evidence(**{field: " "})


def test_authority_kind_and_strength_matrix():
    for kind in ExecutionTimeAuthorityKind:
        assert evidence(authority_kind=kind)
    for strength in (EvidenceStrength.AUTHENTICATED, EvidenceStrength.CORROBORATED):
        assert evidence(evidence_strength=strength)
    with pytest.raises(FinancialExecutionTimeEvidenceError):
        evidence(authority_kind="PROVIDER_TIMESTAMP")
    with pytest.raises(FinancialExecutionTimeEvidenceError):
        evidence(evidence_strength=EvidenceStrength.UNAUTHENTICATED)
    with pytest.raises(FinancialExecutionTimeEvidenceError):
        evidence(evidence_strength=EvidenceStrength.CONFLICTING)


def test_immutable_and_fingerprint_determinism():
    first = evidence()
    second = evidence()
    assert first == second
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 128
    assert all(char in "0123456789abcdef" for char in first.fingerprint)
    with pytest.raises(AttributeError):
        setattr(cast(Any, first), "executed_at", NOW)
    assert first.fingerprint != evidence(evidence_reference="other").fingerprint
    assert first.fingerprint != evidence(executed_at=NOW + timedelta(seconds=1)).fingerprint


def test_no_generic_observation_promotion_or_implicit_timestamp():
    signature = inspect.signature(FinancialExecutionTimeEvidence)
    assert signature.parameters["executed_at"].default is inspect.Parameter.empty
    names = set(signature.parameters)
    assert "observed_at" not in names
    assert "provider_occurred_at" not in names
    assert not hasattr(FinancialExecutionTimeEvidence, "from_provider_observation")


def test_provider_neutral_truth_and_settlement_boundaries():
    item = evidence()
    public = set(name for name in dir(item) if not name.startswith("_"))
    assert not {"create_truth", "settle", "mark_paid", "post_ledger"} & public
    assert "FinancialExecutionTruth" not in {member.value for member in ExecutionTimeAuthorityKind}
    assert all(rail not in ExecutionTimeAuthorityKind.__members__ for rail in ("PAYSHAP", "ZAPPER"))


# ARTIFACT: test_financial_execution_execution_time_evidence.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TIME-EVIDENCE-UNIT-CERT
# AUTHORITY BOUNDARY: unit evidence only; no truth or settlement authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
