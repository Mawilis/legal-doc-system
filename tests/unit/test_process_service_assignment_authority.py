"""Direct adversarial certificate for the Legal P3 assignment authority.

TITLE: Wilsy OS Process-Service Assignment Authority Certificate
VERSION: v1.0.0-PROCESS-SERVICE-ASSIGNMENT-AUTHORITY-CERT
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify exact P1 source binding, assignment eligibility, tenant and
         lineage isolation, chronology, deterministic evidence, and the
         fail-closed constructor/factory boundary for LEGAL_P3.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_process_service_assignment_authority.py
COLLABORATION / OWNERSHIP: Direct unit certificate for P3 only; P1 remains
                            lifecycle/evidence authority and no persistence,
                            transport, custody, or service caller is created.
CERTIFICATION DATE: 2026-09-13
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every fixture uses explicit synthetic tenant identities and
                 rejects cross-tenant composition.
AUTHORITY BOUNDARY: Assignment-decision evidence only; the certificate proves
                    no custody, service, IAM, transport, or financial action.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
FAIL-CLOSED DECLARATION: Any malformed P1 evidence, state, identity, lineage,
                         chronology, source binding, or authority mechanism
                         fails the certificate.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
import json
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    Deputy,
    District,
    LegalInstruction,
    LegalInstructionState,
    ProcessDocument,
    ProcessDocumentState,
    SheriffOffice,
)
from tools.eos.legal_operations.domain.process_service_assignment_authority import (
    SCHEMA,
    VERSION as PRODUCTION_VERSION,
    ProcessServiceAssignmentAuthorityError,
    ProcessServiceAssignmentDecision,
    authorize_process_service_assignment,
)


VERSION = "v1.0.0-PROCESS-SERVICE-ASSIGNMENT-AUTHORITY-CERT"
BASE = datetime(2026, 9, 14, 9, 0, tzinfo=timezone.utc)
TENANT = "tenant-p3-certificate"
OTHER_TENANT = "tenant-p3-other"


class InstructionProxy(LegalInstruction):
    """Subclass used to prove exact canonical P1 runtime-type enforcement."""


class DocumentProxy(ProcessDocument):
    """Subclass used to prove exact canonical P1 runtime-type enforcement."""


class DistrictProxy(District):
    """Subclass used to prove exact canonical P1 runtime-type enforcement."""


class OfficeProxy(SheriffOffice):
    """Subclass used to prove exact canonical P1 runtime-type enforcement."""


class DeputyProxy(Deputy):
    """Subclass used to prove exact canonical P1 runtime-type enforcement."""


def _instruction(
    tenant_id: str = TENANT,
    *,
    instruction_id: str = "instruction-1",
    case_matter_id: str = "matter-1",
    document_id: str = "document-1",
    evidence_reference: str = "instruction-registration",
    accepted_at: datetime = BASE + timedelta(minutes=1),
) -> LegalInstruction:
    """Build an explicit P1 instruction and its legitimate ACCEPTED snapshot."""
    registered = LegalInstruction(
        tenant_id=tenant_id,
        instruction_id=instruction_id,
        case_matter_id=case_matter_id,
        document_id=document_id,
        registered_at=BASE,
        evidence_reference=evidence_reference,
    )
    return registered.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="instruction-acceptance",
        occurred_at=accepted_at,
    )


def _document(
    tenant_id: str = TENANT,
    *,
    document_id: str = "document-1",
    case_matter_id: str = "matter-1",
    registered_at: datetime = BASE,
    evidence_reference: str = "document-registration",
    received_at: datetime | None = None,
) -> ProcessDocument:
    """Build an explicit P1 document and its legitimate RECEIVED snapshot."""
    registered = ProcessDocument(
        tenant_id=tenant_id,
        document_id=document_id,
        case_matter_id=case_matter_id,
        document_type="summons",
        registered_at=registered_at,
        registration_evidence_reference=evidence_reference,
    )
    return registered.transition_to(
        ProcessDocumentState.RECEIVED,
        evidence_reference="document-receipt",
        occurred_at=received_at or registered_at + timedelta(minutes=1),
    )


def _district(
    tenant_id: str = TENANT,
    *,
    district_id: str = "district-1",
    name: str = "Johannesburg District",
) -> District:
    """Build one explicit tenant-scoped P1 district."""
    return District(
        tenant_id=tenant_id,
        district_id=district_id,
        name=name,
        jurisdiction_code="ZA-GP-1",
        evidence_reference="district-evidence",
    )


def _office(
    tenant_id: str = TENANT,
    *,
    sheriff_office_id: str = "office-1",
    district_id: str = "district-1",
    name: str = "Central Sheriff Office",
) -> SheriffOffice:
    """Build one explicit office bound to a district identifier."""
    return SheriffOffice(
        tenant_id=tenant_id,
        sheriff_office_id=sheriff_office_id,
        district_id=district_id,
        name=name,
        evidence_reference="office-evidence",
    )


def _deputy(
    tenant_id: str = TENANT,
    *,
    deputy_id: str = "deputy-1",
    sheriff_office_id: str = "office-1",
    display_name: str = "Deputy One",
) -> Deputy:
    """Build one explicit deputy bound to an office identifier."""
    return Deputy(
        tenant_id=tenant_id,
        deputy_id=deputy_id,
        sheriff_office_id=sheriff_office_id,
        display_name=display_name,
        badge_reference="badge-1",
        evidence_reference="deputy-evidence",
    )


def _valid_inputs() -> dict[str, Any]:
    """Return one complete eligible P1 composition and explicit decision data."""
    return {
        "instruction": _instruction(),
        "document": _document(),
        "district": _district(),
        "sheriff_office": _office(),
        "deputy": _deputy(),
        "assignment_decision_id": "assignment-1",
        "assignment_evidence_reference": "assignment-evidence",
        "decided_at": BASE + timedelta(minutes=3),
    }


def _decision(**overrides: object) -> ProcessServiceAssignmentDecision:
    """Create a valid decision through the public P3 factory."""
    values = _valid_inputs()
    values.update(overrides)
    return authorize_process_service_assignment(**values)


def _expect_code(code: str, **overrides: object) -> None:
    """Require one exact governed P3 error code."""
    with pytest.raises(ProcessServiceAssignmentAuthorityError) as caught:
        _decision(**overrides)
    assert str(caught.value) == code


def test_valid_factory_binds_all_fields_and_source_fingerprints() -> None:
    """The happy path returns exact P1-bound immutable assignment evidence."""
    values = _valid_inputs()
    decision = authorize_process_service_assignment(**values)
    instruction = values["instruction"]
    document = values["document"]
    district = values["district"]
    office = values["sheriff_office"]
    deputy = values["deputy"]
    payload = decision.to_dict()
    assert payload == {
        "schema": SCHEMA,
        "version": PRODUCTION_VERSION,
        "entity_type": "ProcessServiceAssignmentDecision",
        "tenant_id": TENANT,
        "assignment_decision_id": "assignment-1",
        "instruction_id": instruction.instruction_id,
        "case_matter_id": instruction.case_matter_id,
        "document_id": document.document_id,
        "district_id": district.district_id,
        "sheriff_office_id": office.sheriff_office_id,
        "deputy_id": deputy.deputy_id,
        "instruction_fingerprint": instruction.fingerprint,
        "document_fingerprint": document.fingerprint,
        "district_fingerprint": district.fingerprint,
        "sheriff_office_fingerprint": office.fingerprint,
        "deputy_fingerprint": deputy.fingerprint,
        "assignment_evidence_reference": "assignment-evidence",
        "decided_at": (BASE + timedelta(minutes=3)).isoformat(),
    }
    assert decision.tenant_id == TENANT
    assert decision.assignment_decision_id == "assignment-1"
    assert decision.assignment_evidence_reference == "assignment-evidence"
    assert decision.decided_at == BASE + timedelta(minutes=3)


@pytest.mark.parametrize("source", ("instruction", "document", "district", "sheriff_office", "deputy"))
def test_each_authoritative_source_snapshot_changes_p3_fingerprint(source: str) -> None:
    """Each source fingerprint materially contributes to P3 evidence identity."""
    baseline = _valid_inputs()
    variants = dict(baseline)
    if source == "instruction":
        variants[source] = _instruction(evidence_reference="instruction-registration-alt")
    elif source == "document":
        variants[source] = _document(evidence_reference="document-registration-alt")
    elif source == "district":
        variants[source] = _district(name="Pretoria District")
    elif source == "sheriff_office":
        variants[source] = _office(name="Northern Sheriff Office")
    else:
        variants[source] = _deputy(display_name="Deputy Two")
    original = baseline[source]
    changed = variants[source]
    assert original.tenant_id == changed.tenant_id
    assert getattr(original, f"{ {'instruction': 'instruction_id', 'document': 'document_id', 'district': 'district_id', 'sheriff_office': 'sheriff_office_id', 'deputy': 'deputy_id'}[source] }") == getattr(changed, f"{ {'instruction': 'instruction_id', 'document': 'document_id', 'district': 'district_id', 'sheriff_office': 'sheriff_office_id', 'deputy': 'deputy_id'}[source] }")
    assert original.fingerprint != changed.fingerprint
    first = authorize_process_service_assignment(**baseline)
    second = authorize_process_service_assignment(**variants)
    fingerprint_field = f"{source}_fingerprint"
    assert first.to_dict()[fingerprint_field] != second.to_dict()[fingerprint_field]
    assert first.fingerprint != second.fingerprint


@pytest.mark.parametrize(
    ("field", "replacement"),
    (
        ("document", _document(OTHER_TENANT)),
        ("district", _district(OTHER_TENANT)),
        ("sheriff_office", _office(OTHER_TENANT)),
        ("deputy", _deputy(OTHER_TENANT)),
    ),
)
def test_each_foreign_p1_tenant_is_rejected(field: str, replacement: object) -> None:
    """Every individual foreign P1 input fails tenant isolation."""
    _expect_code("P3_TENANT_MISMATCH", **{field: replacement})


@pytest.mark.parametrize(
    ("document_id", "case_matter_id"),
    (("document-other", "matter-1"), ("document-1", "matter-other")),
)
def test_instruction_document_bindings_are_exact(document_id: str, case_matter_id: str) -> None:
    """Document and case-matter references cannot be substituted."""
    _expect_code(
        "P3_INSTRUCTION_DOCUMENT_MISMATCH",
        document=_document(document_id=document_id, case_matter_id=case_matter_id),
    )


@pytest.mark.parametrize("state_name", ("REGISTERED", "CANCELLED", "CLOSED"))
def test_only_accepted_instruction_is_assignable(state_name: str) -> None:
    """Registered, cancelled, and closed instructions are not eligible."""
    registered = LegalInstruction(
        tenant_id=TENANT,
        instruction_id="instruction-1",
        case_matter_id="matter-1",
        document_id="document-1",
        registered_at=BASE,
        evidence_reference="instruction-registration",
    )
    if state_name == "REGISTERED":
        value = registered
    elif state_name == "CANCELLED":
        value = registered.transition_to(
            LegalInstructionState.CANCELLED,
            evidence_reference="instruction-cancellation",
            occurred_at=BASE + timedelta(minutes=1),
        )
    else:
        accepted = registered.transition_to(
            LegalInstructionState.ACCEPTED,
            evidence_reference="instruction-acceptance",
            occurred_at=BASE + timedelta(minutes=1),
        )
        value = accepted.transition_to(
            LegalInstructionState.CLOSED,
            evidence_reference="instruction-closure",
            occurred_at=BASE + timedelta(minutes=2),
        )
    _expect_code("P3_INSTRUCTION_NOT_ACCEPTED", instruction=value)


@pytest.mark.parametrize("state_name", ("REGISTERED", "ALLOCATED_TO_DEPUTY", "RETURNED_TO_CLIENT"))
def test_only_received_document_is_assignable(state_name: str) -> None:
    """Registered, allocated, and returned documents are not assignable."""
    registered = ProcessDocument(
        tenant_id=TENANT,
        document_id="document-1",
        case_matter_id="matter-1",
        document_type="summons",
        registered_at=BASE,
        registration_evidence_reference="document-registration",
    )
    if state_name == "REGISTERED":
        value = registered
    else:
        received = registered.transition_to(
            ProcessDocumentState.RECEIVED,
            evidence_reference="document-receipt",
            occurred_at=BASE + timedelta(minutes=1),
        )
        allocated = received.transition_to(
            ProcessDocumentState.ALLOCATED_TO_DEPUTY,
            evidence_reference="document-allocation",
            occurred_at=BASE + timedelta(minutes=2),
        )
        value = allocated if state_name == "ALLOCATED_TO_DEPUTY" else allocated.transition_to(
            ProcessDocumentState.RETURNED_TO_CLIENT,
            evidence_reference="document-return",
            occurred_at=BASE + timedelta(minutes=3),
        )
    _expect_code("P3_DOCUMENT_NOT_RECEIVED", document=value)


def test_district_to_office_lineage_is_exact() -> None:
    """An office reference to another district fails closed."""
    _expect_code("P3_DISTRICT_OFFICE_LINEAGE_MISMATCH", sheriff_office=_office(district_id="district-other"))


def test_office_to_deputy_lineage_is_exact() -> None:
    """A deputy reference to another office fails closed."""
    _expect_code("P3_OFFICE_DEPUTY_LINEAGE_MISMATCH", deputy=_deputy(sheriff_office_id="office-other"))


@pytest.mark.parametrize(
    ("assignment_decision_id", "expected"),
    (("", "P3_ASSIGNMENT_DECISION_ID_INVALID"), (" ", "P3_ASSIGNMENT_DECISION_ID_INVALID"), ("bad/id", "P3_ASSIGNMENT_DECISION_ID_INVALID")),
)
def test_assignment_identity_is_explicit_and_canonical(assignment_decision_id: str, expected: str) -> None:
    """Blank, whitespace, and malformed assignment identities reject."""
    _expect_code(expected, assignment_decision_id=assignment_decision_id)


@pytest.mark.parametrize("assignment_evidence_reference", ("", " ", "\t"))
def test_assignment_evidence_reference_is_mandatory(assignment_evidence_reference: str) -> None:
    """Evidence reference cannot be omitted or normalized into authority."""
    _expect_code("P3_ASSIGNMENT_EVIDENCE_REFERENCE_INVALID", assignment_evidence_reference=assignment_evidence_reference)


@pytest.mark.parametrize(
    "decided_at",
    (
        BASE.replace(tzinfo=None),
        BASE.replace(tzinfo=timezone(timedelta(hours=2))),
    ),
)
def test_decided_at_requires_aware_utc_datetime(decided_at: datetime) -> None:
    """Naive and non-UTC-aware timestamps fail closed."""
    _expect_code("P3_DECIDED_AT_INVALID", decided_at=decided_at)


@pytest.mark.parametrize(
    "values",
    (
        {"decided_at": BASE - timedelta(minutes=1)},
        {
            "decided_at": BASE + timedelta(minutes=3),
            "document": _document(registered_at=BASE + timedelta(minutes=5)),
        },
        {
            "decided_at": BASE + timedelta(minutes=2),
            "instruction": _instruction(accepted_at=BASE + timedelta(minutes=3)),
            "document": _document(received_at=BASE + timedelta(minutes=1)),
        },
        {
            "decided_at": BASE + timedelta(minutes=1, seconds=30),
            "document": _document(received_at=BASE + timedelta(minutes=3)),
        },
    ),
)
def test_assignment_chronology_rejects_each_earlier_boundary(values: dict[str, object]) -> None:
    """Registration, acceptance, and receipt chronology are independently enforced."""
    _expect_code("P3_ASSIGNMENT_CHRONOLOGY_INVALID", **values)


@pytest.mark.parametrize(
    ("field", "replacement"),
    (
        ("instruction", InstructionProxy),
        ("document", DocumentProxy),
        ("district", DistrictProxy),
        ("sheriff_office", OfficeProxy),
        ("deputy", DeputyProxy),
    ),
)
def test_subclasses_cannot_satisfy_exact_canonical_p1_type(field: str, replacement: Any) -> None:
    """Each P1 authority input requires the exact canonical runtime class."""
    values = _valid_inputs()
    if field == "instruction":
        base = values[field]
        replacement_value = replacement(
            tenant_id=base.tenant_id,
            instruction_id=base.instruction_id,
            case_matter_id=base.case_matter_id,
            document_id=base.document_id,
            registered_at=base.registered_at,
            evidence_reference=base.evidence_reference,
            state=base.state,
            transition_history=base.transition_history,
        )
    elif field == "document":
        base = values[field]
        replacement_value = replacement(
            tenant_id=base.tenant_id,
            document_id=base.document_id,
            case_matter_id=base.case_matter_id,
            document_type=base.document_type,
            registered_at=base.registered_at,
            registration_evidence_reference=base.registration_evidence_reference,
            state=base.state,
            transition_history=base.transition_history,
        )
    elif field == "district":
        base = values[field]
        replacement_value = replacement(
            tenant_id=base.tenant_id,
            district_id=base.district_id,
            name=base.name,
            jurisdiction_code=base.jurisdiction_code,
            evidence_reference=base.evidence_reference,
        )
    elif field == "sheriff_office":
        base = values[field]
        replacement_value = replacement(
            tenant_id=base.tenant_id,
            sheriff_office_id=base.sheriff_office_id,
            district_id=base.district_id,
            name=base.name,
            evidence_reference=base.evidence_reference,
        )
    else:
        base = values[field]
        replacement_value = replacement(
            tenant_id=base.tenant_id,
            deputy_id=base.deputy_id,
            sheriff_office_id=base.sheriff_office_id,
            display_name=base.display_name,
            badge_reference=base.badge_reference,
            evidence_reference=base.evidence_reference,
        )
    values[field] = replacement_value
    _expect_code("P3_P1_VALUE_REQUIRED", **values)


def test_corrupted_p1_history_is_revalidated_before_assignment() -> None:
    """Malformed P1 history cannot be promoted into P3 authority."""
    values = _valid_inputs()
    instruction = values["instruction"]
    object.__setattr__(instruction, "transition_history", ())
    _expect_code("P3_P1_EVIDENCE_INVALID", **values)


def test_direct_decision_constructor_requires_factory_proof() -> None:
    """Arbitrary IDs and source text cannot manufacture a canonical decision."""
    values = _valid_inputs()
    with pytest.raises(ProcessServiceAssignmentAuthorityError) as caught:
        ProcessServiceAssignmentDecision(
            tenant_id=TENANT,
            assignment_decision_id="assignment-1",
            instruction_id="instruction-1",
            case_matter_id="matter-1",
            document_id="document-1",
            district_id="district-1",
            sheriff_office_id="office-1",
            deputy_id="deputy-1",
            instruction_fingerprint=values["instruction"].fingerprint,
            document_fingerprint=values["document"].fingerprint,
            district_fingerprint=values["district"].fingerprint,
            sheriff_office_fingerprint=values["sheriff_office"].fingerprint,
            deputy_fingerprint=values["deputy"].fingerprint,
            assignment_evidence_reference="assignment-evidence",
            decided_at=BASE + timedelta(minutes=3),
        )
    assert str(caught.value) == "P3_DECISION_FACTORY_REQUIRED"


def test_determinism_serialization_and_immutability() -> None:
    """Exact inputs yield stable values, complete payload, and frozen fields."""
    first = _decision()
    second = _decision()
    assert first == second
    assert first.to_dict() == second.to_dict()
    assert first.fingerprint == second.fingerprint
    assert re_full_sha3(first.fingerprint)
    assert "_construction_proof" not in first.to_dict()
    assert set(first.to_dict()) == {
        "schema", "version", "entity_type", "tenant_id", "assignment_decision_id",
        "instruction_id", "case_matter_id", "document_id", "district_id",
        "sheriff_office_id", "deputy_id", "instruction_fingerprint",
        "document_fingerprint", "district_fingerprint", "sheriff_office_fingerprint",
        "deputy_fingerprint", "assignment_evidence_reference", "decided_at",
    }
    canonical = json.dumps(first.to_dict(), ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
    assert hashlib.sha3_512(canonical.encode("utf-8")).hexdigest() == first.fingerprint
    with pytest.raises(FrozenInstanceError):
        first.tenant_id = "tenant-other"  # type: ignore[misc]


def re_full_sha3(value: object) -> bool:
    """Check the public fingerprint shape without importing private validators."""
    return isinstance(value, str) and len(value) == 128 and value == value.lower() and all(char in "0123456789abcdef" for char in value)


def test_factory_does_not_mutate_p1_inputs_or_expose_forbidden_authority() -> None:
    """P1 snapshots remain unchanged and P3 payload has no downstream authority."""
    values = _valid_inputs()
    before = {key: values[key].to_dict() for key in ("instruction", "document", "district", "sheriff_office", "deputy")}
    decision = authorize_process_service_assignment(**values)
    after = {key: values[key].to_dict() for key in before}
    assert before == after
    forbidden = {
        "custody", "attempt", "service_execution", "return", "invoice", "payment",
        "settlement", "accounting", "financial_execution",
    }
    assert forbidden.isdisjoint(decision.to_dict())
    assert "Kennel EOS" not in decision.to_dict()


def test_source_has_no_forbidden_operational_mechanisms() -> None:
    """AST inspection locks the pure, deterministic, provider-neutral boundary."""
    source = inspect.getsource(__import__("tools.eos.legal_operations.domain.process_service_assignment_authority", fromlist=["VERSION"]))
    tree = ast.parse(source)
    calls: set[str] = set()

    def dotted(node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            prefix = dotted(node.value)
            return f"{prefix}.{node.attr}" if prefix else node.attr
        return ""

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            calls.add(dotted(node.func))
    forbidden_calls = {
        "object.__new__", "uuid.uuid4", "datetime.now", "datetime.utcnow",
        "os.getenv", "MongoClient", "requests.get", "requests.post",
    }
    assert calls.isdisjoint(forbidden_calls)
    imported_modules = {
        alias.name.split(".")[0]
        for node in tree.body
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert imported_modules.isdisjoint({"os", "uuid", "pymongo", "requests", "httpx"})


# ARTIFACT: test_process_service_assignment_authority.py
# VERSION: v1.0.0-PROCESS-SERVICE-ASSIGNMENT-AUTHORITY-CERT
# AUTHORITY BOUNDARY: direct P3 assignment-decision evidence certificate only.
# TENANT POSTURE: explicit synthetic tenants; cross-tenant composition is denied.
# FAIL-CLOSED POSTURE: malformed source evidence, lineage, chronology, or authority rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
