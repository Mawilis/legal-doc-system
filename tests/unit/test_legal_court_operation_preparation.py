"""Direct certificate for L9C12-P1 Court Operation Preparation domain.

TITLE: WILSY OS Legal Court Operation Preparation Certificate
VERSION: v1.0.0-L9C12-P1-COURT-OPERATION-PREPARATION-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify immutable preparation-only Court intent, exact P24 lineage,
         bounded scope, deterministic identity, chronology and non-authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_court_operation_preparation.py
COLLABORATION / OWNERSHIP: P24 is read-only prerequisite truth; this
                            certificate exercises pure P1 preparation only.
CERTIFICATION / UPDATE DATE: 2026-09-28
TRANSACTION BOUNDARY: Pure in-memory synthetic values; no Mongo or network.
FAIL-CLOSED DECLARATION: Judicial, professional, financial and external
                         Court claims cannot be represented by this domain.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_court_operation_preparation import (
    COURT_OPERATION_PREPARATION_FIELDS,
    SCHEMA,
    VERSION,
    LegalCourtOperationPreparation,
    LegalCourtOperationPreparationError,
    LegalCourtOperationPreparationState,
    LegalCourtOperationType,
)


BASE = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)
HEX = "a" * 128


def preparation(**overrides: object) -> LegalCourtOperationPreparation:
    values: dict[str, object] = {
        "tenant_id": "tenant-p1-court",
        "case_matter_id": "matter-p1-court",
        "matter_fingerprint": HEX,
        "final_representation_id": "final-representation:p1-court",
        "final_representation_fingerprint": HEX,
        "operation_type": LegalCourtOperationType.COURT_FILING_PREPARATION,
        "target_court_reference": "court:external-opaque-1",
        "target_jurisdiction_reference": "jurisdiction:za-gp-1",
        "document_evidence_lineage": ("document:evidence-2", "document:evidence-1"),
        "requested_scope_capabilities": ("COURT_FILING_PREPARATION",),
        "preparation_state": LegalCourtOperationPreparationState.PREPARATION_REQUIRED,
        "source_evidence_reference": "evidence:preparation-p1",
        "source_evidence_fingerprint": HEX,
        "provenance_reference": "provenance:p1-court",
        "prepared_at": BASE,
        "occurred_at": BASE + timedelta(minutes=1),
        "idempotency_key": "idempotency:p1-court",
    }
    values.update(overrides)
    return LegalCourtOperationPreparation(**cast(Any, values))


def test_version_schema_fields_and_frozen_immutability() -> None:
    value = preparation()
    assert VERSION == "v1.0.0-L9C12-P1-COURT-OPERATION-PREPARATION"
    assert SCHEMA == "WILSY-LEGAL-COURT-OPERATION-PREPARATION/V1"
    assert set(value.to_dict()) == set(COURT_OPERATION_PREPARATION_FIELDS)
    assert value.operation_type is LegalCourtOperationType.COURT_FILING_PREPARATION
    assert value.preparation_state is LegalCourtOperationPreparationState.PREPARATION_REQUIRED
    with pytest.raises(FrozenInstanceError):
        setattr(value, "tenant_id", "tenant-other")


def test_deterministic_identity_fingerprint_and_replay() -> None:
    first = preparation()
    second = preparation()
    assert first.operation_preparation_id == second.operation_preparation_id
    assert first.fingerprint == second.fingerprint
    assert first.to_dict() == second.to_dict()
    changed = preparation(target_court_reference="court:external-opaque-2")
    assert changed.operation_preparation_id != first.operation_preparation_id
    assert changed.fingerprint != first.fingerprint


def test_tenant_matter_fingerprint_and_p24_lineage_are_bound() -> None:
    value = preparation()
    assert value.tenant_id == "tenant-p1-court"
    assert value.case_matter_id == "matter-p1-court"
    assert value.matter_fingerprint == HEX
    assert value.final_representation_id == "final-representation:p1-court"
    assert value.final_representation_fingerprint == HEX


def test_operation_target_lineage_scope_and_state_are_canonical() -> None:
    value = preparation()
    assert value.operation_type == LegalCourtOperationType.COURT_FILING_PREPARATION
    assert value.target_court_reference == "court:external-opaque-1"
    assert value.target_jurisdiction_reference == "jurisdiction:za-gp-1"
    assert value.document_evidence_lineage == ("document:evidence-1", "document:evidence-2")
    assert value.requested_scope_capabilities == ("COURT_FILING_PREPARATION",)
    assert value.preparation_state is LegalCourtOperationPreparationState.PREPARATION_REQUIRED


@pytest.mark.parametrize("operation_type", ["FILED", "COURT_APPEARANCE_PREPARATION", "SUBMIT_NOTICE", "SERVE_DOCUMENT"])
def test_unsupported_operation_types_reject(operation_type: str) -> None:
    with pytest.raises(LegalCourtOperationPreparationError):
        preparation(operation_type=operation_type)


@pytest.mark.parametrize("scope", [("ADVISORY",), ("COURT_APPEARANCE_PREPARATION",), ("PAYMENT_EXECUTION",), ("BILLING",), ("COURT_FILING_PREPARATION", "ADVISORY")])
def test_scope_widening_finance_billing_and_unrelated_capabilities_reject(scope: tuple[str, ...]) -> None:
    with pytest.raises(LegalCourtOperationPreparationError):
        preparation(requested_scope_capabilities=scope)


def test_lineage_is_sorted_and_duplicate_lineage_rejects() -> None:
    assert preparation(document_evidence_lineage=["z:2", "z:1"]).document_evidence_lineage == ("z:1", "z:2")
    with pytest.raises(LegalCourtOperationPreparationError):
        preparation(document_evidence_lineage=("document:same", "document:same"))


@pytest.mark.parametrize("timestamp", [BASE.replace(tzinfo=None), "not-a-time"])
def test_aware_utc_timestamps_required(timestamp: object) -> None:
    with pytest.raises(LegalCourtOperationPreparationError):
        preparation(prepared_at=timestamp)


def test_invalid_chronology_rejects() -> None:
    with pytest.raises(LegalCourtOperationPreparationError):
        preparation(occurred_at=BASE - timedelta(seconds=1))


def test_all_internal_states_are_non_judicial_snapshots() -> None:
    for state in LegalCourtOperationPreparationState:
        value = preparation(preparation_state=state)
        assert value.preparation_state is state


def test_persistence_and_external_authority_fields_are_absent() -> None:
    value = preparation()
    payload = value.to_dict()
    for forbidden in ("filed_at", "accepted_at", "issued_at", "served_at", "hearing_result", "order_granted", "external_success", "court_online_credentials", "attorney_of_record", "professional_admission", "judicial_order"):
        assert forbidden not in payload
    source = Path("tools/eos/legal_operations/domain/legal_court_operation_preparation.py").read_text()
    assert "COURT_APPEARANCE_PREPARATION =" not in source
    assert "start_transaction" not in source


def test_no_expiry_revocation_supersession_or_latest_wins_contract() -> None:
    source = Path("tools/eos/legal_operations/domain/legal_court_operation_preparation.py").read_text().lower()
    assert "effective_until" not in source
    assert "revocation" not in source
    assert "supersession" not in source
    assert "latest-wins" not in source
    assert "current_pointer" not in source


def test_no_professional_admission_attorney_record_judicial_or_financial_authority() -> None:
    source = Path("tools/eos/legal_operations/domain/legal_court_operation_preparation.py").read_text().lower()
    assert "attorney-of-record" in source
    assert "judicial" in source
    assert "financial" in source
    assert preparation().requested_scope_capabilities == ("COURT_FILING_PREPARATION",)


def test_from_dict_requires_exact_schema_and_integrity() -> None:
    value = preparation()
    assert LegalCourtOperationPreparation.from_dict(value.to_dict()) == value
    malformed = dict(value.to_dict())
    malformed["unexpected"] = True
    with pytest.raises(LegalCourtOperationPreparationError):
        LegalCourtOperationPreparation.from_dict(malformed)
    corrupted = dict(value.to_dict())
    corrupted["fingerprint"] = "0" * 128
    with pytest.raises(LegalCourtOperationPreparationError):
        LegalCourtOperationPreparation.from_dict(corrupted)


# ARTIFACT: test_legal_court_operation_preparation.py
# VERSION: v1.0.0-L9C12-P1-COURT-OPERATION-PREPARATION-CERT
# AUTHORITY BOUNDARY: direct immutable preparation-domain certificate only
# FAIL-CLOSED POSTURE: identity, scope, chronology and external-authority assertions are mandatory
# END OF WILSY OS SOVEREIGN ARTIFACT
