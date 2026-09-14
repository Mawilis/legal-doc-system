"""Direct adversarial certificate for the pure P5A attempt authority.

TITLE: Wilsy OS Process-Service Attempt Authority Certificate
VERSION: v1.1.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify immutable, tenant-scoped P5A attempt-authorization evidence
         and every fail-closed P4 correlation boundary without persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_process_service_attempt_authority.py
COLLABORATION / OWNERSHIP: Direct P5A certificate; P4B remains allocation
                            evidence authority and P5A production remains the
                            attempt-authorization evidence owner.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.1.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY-CERT certifies
           exact P4 allocation-evidence provenance propagation and its
           canonical payload/fingerprint binding while retaining all prior
           proof-gate, correlation, tenant, chronology, immutability, and
           authority-boundary certification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no network,
                             Mongo runtime, provider, credential, location, or
                             personal-data access.
TENANT BOUNDARY: Every assertion is explicitly tenant-scoped; cross-tenant
                 receipt/current composition must fail closed.
AUTHORITY BOUNDARY: This certificate verifies P5A attempt-authorization
                    evidence only. It does not construct service lifecycle,
                    custody, persistence, IAM, transport, or financial truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; this certificate introduces no
                              invoice, payment, billing, or settlement claim.
FAIL-CLOSED DECLARATION: Assertions reject malformed P4 values, every
                         implemented correlation mismatch, forged construction,
                         chronology violations, and forbidden authority surface.
"""
from __future__ import annotations

from dataclasses import fields, replace
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
import json
from typing import Any, cast

import pytest

import tools.eos.legal_operations.domain.process_service_attempt_authority as authority
from tools.eos.legal_operations.domain.process_service_attempt_authority import (
    ProcessServiceAttemptAuthorityDecision,
    ProcessServiceAttemptAuthorityError,
    authorize_process_service_attempt,
)
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationReceipt,
)


VERSION = "v1.1.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY-CERT"
TENANT = "tenant-alpha"
BASE = datetime(2026, 9, 14, 8, 0, tzinfo=timezone.utc)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
HEX_D = "d" * 128
HEX_E = "e" * 128
HEX_F = "f" * 128


def _receipt(**changes: Any) -> ProcessServiceAllocationReceipt:
    """Build one valid deterministic P4 allocation receipt."""
    values: dict[str, Any] = {
        "tenant_id": TENANT,
        "allocation_command_id": "allocation-command-1",
        "idempotency_key": "allocation-idempotency-1",
        "instruction_id": "instruction-1",
        "case_matter_id": "matter-1",
        "document_id": "document-1",
        "district_id": "district-1",
        "sheriff_office_id": "office-1",
        "deputy_id": "deputy-1",
        "assignment_decision_id": "assignment-1",
        "assignment_decision_fingerprint": HEX_A,
        "source_instruction_fingerprint": HEX_B,
        "source_document_fingerprint": HEX_C,
        "source_district_fingerprint": HEX_D,
        "source_sheriff_office_fingerprint": HEX_E,
        "source_deputy_fingerprint": HEX_F,
        "prior_custody_chain_fingerprint": HEX_A,
        "prior_custody_head_event_id": "custody-head-1",
        "prior_custody_head_fingerprint": HEX_B,
        "prior_custody_head_sequence_number": 7,
        "from_holder_reference": "office-1",
        "to_holder_reference": "deputy-1",
        "allocation_custody_event_id": "custody-allocation-1",
        "allocation_evidence_reference": "allocation-evidence-1",
        "allocated_at": BASE + timedelta(minutes=5),
        "allocated_document_fingerprint": HEX_C,
        "allocation_custody_event_fingerprint": HEX_D,
        "result_custody_chain_fingerprint": HEX_E,
    }
    values.update(changes)
    return ProcessServiceAllocationReceipt(**values)


def _current(receipt: ProcessServiceAllocationReceipt, **changes: Any) -> ProcessServiceAllocationCurrent:
    """Build the exact P4 current pointer correlated to a receipt."""
    values: dict[str, Any] = {
        "tenant_id": receipt.tenant_id,
        "document_id": receipt.document_id,
        "process_document_fingerprint": receipt.allocated_document_fingerprint,
        "custody_chain_fingerprint": receipt.result_custody_chain_fingerprint,
        "custody_head_event_id": receipt.allocation_custody_event_id,
        "custody_head_fingerprint": receipt.allocation_custody_event_fingerprint,
        "custody_head_sequence_number": receipt.prior_custody_head_sequence_number + 1,
        "current_holder_reference": receipt.to_holder_reference,
        "authority_evidence_reference": receipt.allocation_command_id,
        "authority_evidence_fingerprint": receipt.fingerprint,
    }
    values.update(changes)
    return ProcessServiceAllocationCurrent(**values)


def _tampered(value: Any, **changes: Any) -> Any:
    """Build a frozen P4 corruption fixture for the P5A revalidation gate."""
    clone = object.__new__(type(value))
    for item in fields(value):
        object.__setattr__(clone, item.name, changes.get(item.name, getattr(value, item.name)))
    return clone


def _decision(receipt: ProcessServiceAllocationReceipt | None = None) -> ProcessServiceAttemptAuthorityDecision:
    """Compose a valid decision through the public P5A factory."""
    source = receipt or _receipt()
    return authorize_process_service_attempt(
        allocation_receipt=source,
        allocation_current=_current(source),
        attempt_authority_id="attempt-authority-1",
        attempt_id="attempt-1",
        authorized_at=source.allocated_at + timedelta(minutes=2),
    )


def _assert_code(call: Any, expected: str) -> None:
    """Assert one public operation raises the exact governed code."""
    with pytest.raises(ProcessServiceAttemptAuthorityError) as caught:
        call()
    assert caught.value.code == expected


def test_happy_path_derives_every_authority_field_and_is_deterministic() -> None:
    """P5A derives all fields from validated P4 evidence exactly."""
    receipt = _receipt()
    current = _current(receipt)
    before_receipt = receipt.to_dict()
    before_current = current.to_dict()
    decision = authorize_process_service_attempt(
        allocation_receipt=receipt,
        allocation_current=current,
        attempt_authority_id="attempt-authority-1",
        attempt_id="attempt-1",
        authorized_at=receipt.allocated_at + timedelta(minutes=2),
    )
    assert type(decision) is ProcessServiceAttemptAuthorityDecision
    assert decision.tenant_id == receipt.tenant_id == TENANT
    assert decision.attempt_authority_id == "attempt-authority-1"
    assert decision.attempt_id == "attempt-1"
    assert decision.instruction_id == receipt.instruction_id
    assert decision.document_id == receipt.document_id
    assert decision.deputy_id == receipt.deputy_id
    assert decision.allocation_command_id == receipt.allocation_command_id
    assert decision.allocation_evidence_reference == receipt.allocation_evidence_reference
    assert decision.allocation_receipt_evidence_identity == receipt.evidence_identity
    assert decision.allocation_receipt_fingerprint == receipt.fingerprint
    assert decision.allocation_current_fingerprint == hashlib.sha3_512(
        json.dumps(current.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    assert decision.allocated_at == receipt.allocated_at
    assert decision.authorized_at == receipt.allocated_at + timedelta(minutes=2)
    assert decision.to_dict() == decision.to_dict()
    assert decision.to_dict()["allocation_evidence_reference"] == "allocation-evidence-1"
    assert decision.fingerprint == decision.fingerprint
    assert len(decision.fingerprint) == 128
    assert decision.fingerprint == decision.fingerprint.lower()
    assert receipt.to_dict() == before_receipt
    assert current.to_dict() == before_current


def test_fingerprint_is_independently_recomputed_and_changes_with_semantics() -> None:
    """Canonical SHA3-512 evidence is independently reproducible and sensitive."""
    decision = _decision()
    payload = decision.to_dict()
    expected = hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    assert decision.fingerprint == expected
    changed = dict(payload)
    changed["attempt_id"] = "attempt-2"
    changed_digest = hashlib.sha3_512(
        json.dumps(changed, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    assert changed_digest != decision.fingerprint
    other = authorize_process_service_attempt(
        allocation_receipt=_receipt(),
        allocation_current=_current(_receipt()),
        attempt_authority_id="attempt-authority-1",
        attempt_id="attempt-2",
        authorized_at=_receipt().allocated_at + timedelta(minutes=2),
    )
    assert other.fingerprint != decision.fingerprint


def test_allocation_provenance_is_canonical_and_fingerprint_bound() -> None:
    """The exact P4 allocation provenance is serialized and integrity-bound."""
    decision = _decision()
    payload = decision.to_dict()
    assert payload["allocation_evidence_reference"] == "allocation-evidence-1"
    changed = dict(payload)
    changed["allocation_evidence_reference"] = "allocation-evidence-2"
    changed_digest = hashlib.sha3_512(
        json.dumps(changed, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    assert changed_digest != decision.fingerprint


def test_allocation_provenance_has_no_caller_authority_input() -> None:
    """Callers cannot supply or override the P4 allocation provenance field."""
    signature = inspect.signature(authorize_process_service_attempt)
    assert "allocation_evidence_reference" not in signature.parameters
    with pytest.raises(TypeError):
        authorize_process_service_attempt(  # type: ignore[call-arg]
            allocation_receipt=_receipt(),
            allocation_current=_current(_receipt()),
            attempt_authority_id="attempt-authority-1",
            attempt_id="attempt-1",
            authorized_at=BASE,
            allocation_evidence_reference="caller-forged",  # type: ignore[call-arg]
        )


def test_direct_construction_and_proof_reuse_fail_closed() -> None:
    """Only the payload-bound factory proof may construct a decision snapshot."""
    decision = _decision()
    kwargs = {item.name: getattr(decision, item.name) for item in fields(decision) if not item.name.startswith("_")}
    _assert_code(lambda: ProcessServiceAttemptAuthorityDecision(**kwargs), "P5A_DECISION_FACTORY_REQUIRED")
    _assert_code(lambda: replace(decision, attempt_id="altered-attempt"), "P5A_DECISION_SOURCE_BINDING_INVALID")
    _assert_code(lambda: replace(decision, tenant_id="tenant-beta"), "P5A_DECISION_SOURCE_BINDING_INVALID")


def test_exact_p4_runtime_types_and_p4_validation_are_required() -> None:
    """Wrong types, subclasses, and malformed P4 values are rejected."""
    receipt = _receipt()
    current = _current(receipt)

    class ReceiptSubclass(ProcessServiceAllocationReceipt):
        pass

    class CurrentSubclass(ProcessServiceAllocationCurrent):
        pass

    subclass_receipt = ReceiptSubclass(**receipt.__dict__) if hasattr(receipt, "__dict__") else None
    if subclass_receipt is None:
        subclass_receipt = ReceiptSubclass(
            **{item.name: getattr(receipt, item.name) for item in fields(receipt)}
        )
    subclass_current = CurrentSubclass(
        **{item.name: getattr(current, item.name) for item in fields(current)}
    )
    _assert_code(
        lambda: authorize_process_service_attempt(
            allocation_receipt=cast(Any, object()),
            allocation_current=current,
            attempt_authority_id="authority-1",
            attempt_id="attempt-1",
            authorized_at=receipt.allocated_at,
        ),
        "P5A_RECEIPT_REQUIRED",
    )
    _assert_code(
        lambda: authorize_process_service_attempt(
            allocation_receipt=subclass_receipt,
            allocation_current=current,
            attempt_authority_id="authority-1",
            attempt_id="attempt-1",
            authorized_at=receipt.allocated_at,
        ),
        "P5A_RECEIPT_REQUIRED",
    )
    _assert_code(
        lambda: authorize_process_service_attempt(
            allocation_receipt=receipt,
            allocation_current=cast(Any, object()),
            attempt_authority_id="authority-1",
            attempt_id="attempt-1",
            authorized_at=receipt.allocated_at,
        ),
        "P5A_CURRENT_REQUIRED",
    )
    _assert_code(
        lambda: authorize_process_service_attempt(
            allocation_receipt=receipt,
            allocation_current=subclass_current,
            attempt_authority_id="authority-1",
            attempt_id="attempt-1",
            authorized_at=receipt.allocated_at,
        ),
        "P5A_CURRENT_REQUIRED",
    )
    malformed = _tampered(receipt, allocation_command_id="")
    _assert_code(
        lambda: authorize_process_service_attempt(
            allocation_receipt=malformed,
            allocation_current=current,
            attempt_authority_id="authority-1",
            attempt_id="attempt-1",
            authorized_at=receipt.allocated_at,
        ),
        "P5A_RECEIPT_REQUIRED",
    )


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"tenant_id": "tenant-beta"}, "P5A_RECEIPT_CURRENT_TENANT_DOCUMENT_MISMATCH"),
        ({"document_id": "document-2"}, "P5A_RECEIPT_CURRENT_TENANT_DOCUMENT_MISMATCH"),
    ],
)
def test_receipt_current_tenant_and_document_correlation(changes: dict[str, object], expected: str) -> None:
    """Tenant and document identity correlation are independently fail-closed."""
    receipt = _receipt()
    _assert_code(
        lambda: authorize_process_service_attempt(
            allocation_receipt=receipt,
            allocation_current=_current(receipt, **changes),
            attempt_authority_id="authority-1",
            attempt_id="attempt-1",
            authorized_at=receipt.allocated_at,
        ),
        expected,
    )


@pytest.mark.parametrize(
    ("receipt_changes", "current_changes", "expected"),
    [
        ({"allocated_document_fingerprint": HEX_A}, {}, "P5A_PROCESS_DOCUMENT_FINGERPRINT_MISMATCH"),
        ({"result_custody_chain_fingerprint": HEX_A}, {}, "P5A_CUSTODY_CHAIN_FINGERPRINT_MISMATCH"),
        ({"allocation_custody_event_id": "custody-allocation-2"}, {}, "P5A_CUSTODY_HEAD_EVENT_MISMATCH"),
        ({"allocation_custody_event_fingerprint": HEX_A}, {}, "P5A_CUSTODY_HEAD_FINGERPRINT_MISMATCH"),
        ({}, {"custody_head_sequence_number": 9}, "P5A_CUSTODY_HEAD_SEQUENCE_MISMATCH"),
        ({"to_holder_reference": "holder-1"}, {}, "P5A_RECEIPT_HOLDER_DEPUTY_MISMATCH"),
        ({}, {"current_holder_reference": "other-holder"}, "P5A_CURRENT_HOLDER_MISMATCH"),
        ({}, {"authority_evidence_reference": "allocation-command-2"}, "P5A_AUTHORITY_REFERENCE_MISMATCH"),
        ({}, {"authority_evidence_fingerprint": HEX_A}, "P5A_AUTHORITY_FINGERPRINT_MISMATCH"),
    ],
)
def test_each_receipt_current_correlation_predicate_fails_independently(
    receipt_changes: dict[str, object], current_changes: dict[str, object], expected: str
) -> None:
    """Every implemented custody, holder, and authority predicate is covered."""
    original = _receipt()
    receipt = _receipt(**receipt_changes)
    _assert_code(
        lambda: authorize_process_service_attempt(
            allocation_receipt=receipt,
            allocation_current=_current(original, **current_changes),
            attempt_authority_id="authority-1",
            attempt_id="attempt-1",
            authorized_at=receipt.allocated_at,
        ),
        expected,
    )


@pytest.mark.parametrize(
    ("name", "value", "expected"),
    [
        ("attempt_authority_id", "", "P5A_ATTEMPT_AUTHORITY_ID_INVALID"),
        ("attempt_authority_id", " bad", "P5A_ATTEMPT_AUTHORITY_ID_INVALID"),
        ("attempt_authority_id", "*", "P5A_ATTEMPT_AUTHORITY_ID_INVALID"),
        ("attempt_id", "", "P5A_ATTEMPT_ID_INVALID"),
        ("attempt_id", "bad value", "P5A_ATTEMPT_ID_INVALID"),
        ("attempt_id", "*", "P5A_ATTEMPT_ID_INVALID"),
    ],
)
def test_public_identity_inputs_fail_closed(name: str, value: str, expected: str) -> None:
    """Caller-controlled attempt identities require canonical non-empty syntax."""
    receipt = _receipt()
    kwargs: dict[str, Any] = {
        "allocation_receipt": receipt,
        "allocation_current": _current(receipt),
        "attempt_authority_id": "authority-1",
        "attempt_id": "attempt-1",
        "authorized_at": receipt.allocated_at,
    }
    kwargs[name] = value
    _assert_code(lambda: authorize_process_service_attempt(**kwargs), expected)


@pytest.mark.parametrize(
    ("authorized_at", "expected"),
    [
        (BASE.replace(tzinfo=None), "P5A_AUTHORIZED_AT_INVALID"),
        (BASE.replace(tzinfo=timezone(timedelta(hours=1))), "P5A_AUTHORIZED_AT_INVALID"),
        (BASE, "P5A_AUTHORIZATION_CHRONOLOGY_INVALID"),
        ("2026-09-14T08:00:00Z", "P5A_AUTHORIZED_AT_INVALID"),
    ],
)
def test_authorized_timestamp_is_explicit_utc_and_monotonic(authorized_at: object, expected: str) -> None:
    """Naive, non-UTC, malformed, and pre-allocation timestamps reject."""
    receipt = _receipt()
    _assert_code(
        lambda: authorize_process_service_attempt(
            allocation_receipt=receipt,
            allocation_current=_current(receipt),
            attempt_authority_id="authority-1",
            attempt_id="attempt-1",
            authorized_at=authorized_at,  # type: ignore[arg-type]
        ),
        expected,
    )


def test_pseudo_tenant_and_cross_tenant_pairing_cannot_become_authority() -> None:
    """P4 tenant validation and exact pair correlation prevent tenant forgery."""
    valid = _receipt()
    pseudo = _tampered(valid, tenant_id="global")
    _assert_code(
        lambda: authorize_process_service_attempt(
            allocation_receipt=pseudo,
            allocation_current=_current(valid),
            attempt_authority_id="authority-1",
            attempt_id="attempt-1",
            authorized_at=pseudo.allocated_at,
        ),
        "P5A_RECEIPT_REQUIRED",
    )
    receipt = _receipt()
    foreign = _receipt(tenant_id="tenant-beta")
    _assert_code(
        lambda: authorize_process_service_attempt(
            allocation_receipt=receipt,
            allocation_current=_current(foreign),
            attempt_authority_id="authority-1",
            attempt_id="attempt-1",
            authorized_at=receipt.allocated_at,
        ),
        "P5A_RECEIPT_CURRENT_TENANT_DOCUMENT_MISMATCH",
    )


def test_decision_is_frozen_and_serialization_cannot_mutate_it() -> None:
    """Frozen authority fields and defensive serialization remain immutable."""
    decision = _decision()
    with pytest.raises((AttributeError, TypeError)):
        decision.tenant_id = "tenant-beta"  # type: ignore[misc]
    serialized = decision.to_dict()
    serialized["tenant_id"] = "tenant-beta"
    assert decision.tenant_id == TENANT
    assert decision.to_dict()["tenant_id"] == TENANT
    assert decision.fingerprint == decision.fingerprint


def test_authority_surface_excludes_later_lifecycle_and_financial_truth() -> None:
    """Exact public fields/APIs contain evidence only, never later authority."""
    decision_fields = {item.name for item in fields(ProcessServiceAttemptAuthorityDecision)}
    assert decision_fields == {
        "tenant_id",
        "attempt_authority_id",
        "attempt_id",
        "instruction_id",
        "document_id",
        "deputy_id",
        "allocation_command_id",
        "allocation_evidence_reference",
        "allocation_receipt_evidence_identity",
        "allocation_receipt_fingerprint",
        "allocation_current_fingerprint",
        "allocated_at",
        "authorized_at",
        "_construction_proof",
    }
    assert not hasattr(authority, "ServiceAttempt")
    assert not hasattr(authority, "ServiceExecution")
    assert not hasattr(authority, "ReturnOfService")
    assert not hasattr(authority, "MongoClient")
    assert not hasattr(authority, "start_transaction")
    assert not hasattr(authority, "commit_transaction")
    assert not hasattr(authority, "abort_transaction")
    assert not hasattr(authority, "invoice")
    assert not hasattr(authority, "payment")
    assert not hasattr(authority, "settlement")


# ARTIFACT: test_process_service_attempt_authority.py
# VERSION: v1.1.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY-CERT
# AUTHORITY BOUNDARY: direct P5A evidence certificate only
# TENANT POSTURE: synthetic explicit tenant scope; no cross-tenant disclosure
# FAIL-CLOSED POSTURE: production contract is tested without mutation or Mongo
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
