"""Canonical pure-Python process-service assignment authority.

TITLE: Wilsy OS Process-Service Assignment Authority
VERSION: v1.0.0-PROCESS-SERVICE-ASSIGNMENT-AUTHORITY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Decide whether one accepted legal instruction and received process
         document may be assigned to one deputy through an exact,
         tenant-scoped District -> SheriffOffice -> Deputy lineage.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/process_service_assignment_authority.py
COLLABORATION / OWNERSHIP: Legal P3 assignment-authority owner; P1 lifecycle
                            objects remain sovereign lifecycle/evidence facts.
                            Callers own persistence and all later custody or
                            service workflows.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: 2026-09-13 v1.0.0-PROCESS-SERVICE-ASSIGNMENT-AUTHORITY establishes
           immutable tenant-scoped assignment decisions with exact P1 source
           fingerprints, strict state, lineage, evidence, and chronology
           binding.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque tenant and evidence references only; no
                             network, provider, credential, location, or PII
                             expansion.
TENANT BOUNDARY: Every P1 input and resulting decision carries one explicit,
                 non-default tenant; cross-tenant composition is rejected.
AUTHORITY BOUNDARY: This module owns assignment-decision truth only. It does
                    not mutate P1 values or create custody, document,
                    attempt, service, return, IAM, or transport authority.
FINANCIAL AUTHORITY BOUNDARY: Assignment is not billing, invoicing, payment,
                              settlement, accounting, or financial execution;
                              Kennel EOS remains exclusively authoritative for
                              financial execution and settlement.
FAIL-CLOSED DECLARATION: Invalid P1 evidence, states, identities, lineage,
                         timestamps, tenant bindings, or chronology reject
                         through the governed P3 exception.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
import hashlib
import json
import re
import unicodedata
from typing import Callable, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    Deputy,
    District,
    LegalInstruction,
    LegalInstructionState,
    LegalOperationsLifecycleError,
    LifecycleTransitionEvidence,
    ProcessDocument,
    ProcessDocumentState,
    SheriffOffice,
)


VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-ASSIGNMENT-AUTHORITY"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-ASSIGNMENT-AUTHORITY/V1"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})


class ProcessServiceAssignmentAuthorityError(ValueError):
    """Governed failure for tenant-scoped P3 assignment evidence.

    The exception reports fail-closed validation of P1 identity, lifecycle
    state, District -> SheriffOffice -> Deputy lineage, explicit evidence, or
    chronology. It signals no mutation and grants no custody, service, IAM,
    transport, or assignment side effect. Assignment authority is distinct
    from financial authority; Kennel EOS remains exclusively authoritative for
    financial execution and settlement.
    """


def _fail(code: str) -> NoReturn:
    """Raise one governed assignment failure without inventing authority."""
    raise ProcessServiceAssignmentAuthorityError(code)


def _identity(name: str, value: object) -> str:
    """Validate one explicit opaque identity used by assignment evidence."""
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"P3_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Validate one explicit tenant and reject pseudo/global aliases."""
    tenant_id = _identity("tenant_id", value)
    if tenant_id.casefold() in _FORBIDDEN_TENANTS:
        _fail("P3_TENANT_INVALID")
    return tenant_id


def _text(name: str, value: object) -> str:
    """Validate explicit NFC-normalized evidence text."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"P3_{name.upper()}_INVALID")
    text = cast(str, value)
    if unicodedata.normalize("NFC", text) != text:
        _fail(f"P3_{name.upper()}_INVALID")
    return text


def _utc_timestamp(name: str, value: object) -> datetime:
    """Require an explicit aware UTC datetime, never a wall-clock default."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        _fail(f"P3_{name.upper()}_INVALID")
    return cast(datetime, value)


def _fingerprint(name: str, value: object) -> str:
    """Require one exact lowercase SHA3-512 source fingerprint."""
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail(f"P3_{name.upper()}_INVALID")
    return cast(str, value)


def _validate_p1(value: object, expected: type[object]) -> None:
    """Revalidate an exact canonical P1 runtime type and its evidence."""
    if type(value) is not expected:
        _fail("P3_P1_VALUE_REQUIRED")
    try:
        if expected is LegalInstruction:
            cast(LegalInstruction, value).__post_init__()
        elif expected is ProcessDocument:
            cast(ProcessDocument, value).__post_init__()
        elif expected is District:
            cast(District, value).__post_init__()
        elif expected is SheriffOffice:
            cast(SheriffOffice, value).__post_init__()
        elif expected is Deputy:
            cast(Deputy, value).__post_init__()
        else:
            _fail("P3_P1_VALUE_REQUIRED")
    except LegalOperationsLifecycleError as error:
        raise ProcessServiceAssignmentAuthorityError("P3_P1_EVIDENCE_INVALID") from error


def _transition_time(
    history: tuple[LifecycleTransitionEvidence, ...],
    resulting_state: StrEnum,
) -> datetime:
    """Return the unique validated timestamp proving one required state."""
    matches = tuple(event for event in history if event.resulting_state is resulting_state)
    if len(matches) != 1:
        _fail("P3_REQUIRED_TRANSITION_EVIDENCE_MISSING")
    return matches[0].occurred_at


def _canonical(value: object) -> object:
    """Convert assignment values to deterministic JSON-safe primitives."""
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _decision_payload(
    *,
    tenant_id: str,
    assignment_decision_id: str,
    instruction_id: str,
    case_matter_id: str,
    document_id: str,
    district_id: str,
    sheriff_office_id: str,
    deputy_id: str,
    instruction_fingerprint: str,
    document_fingerprint: str,
    district_fingerprint: str,
    sheriff_office_fingerprint: str,
    deputy_fingerprint: str,
    assignment_evidence_reference: str,
    decided_at: datetime,
) -> dict[str, object]:
    """Build the complete semantic payload used by serialization and proof."""
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "entity_type": "ProcessServiceAssignmentDecision",
        "tenant_id": tenant_id,
        "assignment_decision_id": assignment_decision_id,
        "instruction_id": instruction_id,
        "case_matter_id": case_matter_id,
        "document_id": document_id,
        "district_id": district_id,
        "sheriff_office_id": sheriff_office_id,
        "deputy_id": deputy_id,
        "instruction_fingerprint": instruction_fingerprint,
        "document_fingerprint": document_fingerprint,
        "district_fingerprint": district_fingerprint,
        "sheriff_office_fingerprint": sheriff_office_fingerprint,
        "deputy_fingerprint": deputy_fingerprint,
        "assignment_evidence_reference": assignment_evidence_reference,
        "decided_at": _canonical(decided_at),
    }


def _digest(payload: object) -> str:
    """Hash one deterministic JSON payload with lowercase SHA3-512."""
    encoded = json.dumps(
        payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _make_proof_contract() -> tuple[
    Callable[[str], object],
    Callable[[object], bool],
    Callable[[object], str | None],
]:
    """Create a private proof type, issuer, validator, and digest accessor."""

    @dataclass(frozen=True, slots=True)
    class _Proof:
        payload_digest: str

    def issue(payload_digest: str) -> object:
        return _Proof(payload_digest)

    def validate(value: object) -> bool:
        return isinstance(value, _Proof)

    def digest(value: object) -> str | None:
        if not isinstance(value, _Proof):
            return None
        return value.payload_digest

    return issue, validate, digest


_issue_proof, _is_proof, _proof_digest = _make_proof_contract()


@dataclass(frozen=True, slots=True)
class ProcessServiceAssignmentDecision:
    """Immutable assignment decision bound to validated P1 and lineage facts.

    The decision is tenant-scoped evidence only. Construction validates its own
    identity, evidence, and timestamp shape; the public factory below is the
    only operation that composes it from eligible P1 lifecycle and lineage
    values. A private payload-bound construction proof is required, so ordinary
    construction fails closed; Python has no absolute private-constructor
    primitive, therefore deliberate reflective access to private module symbols
    remains a language limitation. Reusing a proof with changed fields fails.
    The decision performs no mutation or persistence and carries no financial,
    custody, service, IAM, or transport authority.
    """

    tenant_id: str
    assignment_decision_id: str
    instruction_id: str
    case_matter_id: str
    document_id: str
    district_id: str
    sheriff_office_id: str
    deputy_id: str
    instruction_fingerprint: str
    document_fingerprint: str
    district_fingerprint: str
    sheriff_office_fingerprint: str
    deputy_fingerprint: str
    assignment_evidence_reference: str
    decided_at: datetime
    _construction_proof: object = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Fail closed on malformed immutable decision evidence."""
        proof = self._construction_proof
        if not _is_proof(proof):
            _fail("P3_DECISION_FACTORY_REQUIRED")
        _tenant(self.tenant_id)
        for name in (
            "assignment_decision_id",
            "instruction_id",
            "case_matter_id",
            "document_id",
            "district_id",
            "sheriff_office_id",
            "deputy_id",
        ):
            _identity(name, getattr(self, name))
        for name in (
            "instruction_fingerprint",
            "document_fingerprint",
            "district_fingerprint",
            "sheriff_office_fingerprint",
            "deputy_fingerprint",
        ):
            _fingerprint(name, getattr(self, name))
        _text("assignment_evidence_reference", self.assignment_evidence_reference)
        _utc_timestamp("decided_at", self.decided_at)
        if _proof_digest(proof) != _digest(self.to_dict()):
            _fail("P3_DECISION_SOURCE_BINDING_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Return complete immutable, tenant-scoped assignment evidence.

        The mapping contains the exact source-bound P1 fingerprints and every
        assignment decision field, serialized deterministically without
        mutation or persistence. It represents assignment-decision evidence
        only; it cannot create custody, service, IAM, transport, billing, or
        payment truth. Invalid source-bound state is rejected before this
        representation exists, and Kennel EOS remains the exclusive financial
        execution and settlement authority.
        """
        return _decision_payload(
            tenant_id=self.tenant_id,
            assignment_decision_id=self.assignment_decision_id,
            instruction_id=self.instruction_id,
            case_matter_id=self.case_matter_id,
            document_id=self.document_id,
            district_id=self.district_id,
            sheriff_office_id=self.sheriff_office_id,
            deputy_id=self.deputy_id,
            instruction_fingerprint=self.instruction_fingerprint,
            document_fingerprint=self.document_fingerprint,
            district_fingerprint=self.district_fingerprint,
            sheriff_office_fingerprint=self.sheriff_office_fingerprint,
            deputy_fingerprint=self.deputy_fingerprint,
            assignment_evidence_reference=self.assignment_evidence_reference,
            decided_at=self.decided_at,
        )

    @property
    def fingerprint(self) -> str:
        """Return deterministic lowercase SHA3-512 assignment evidence.

        The digest covers the complete canonical tenant-scoped decision payload,
        including all five exact P1 source fingerprints. Computing it is pure
        and non-mutating; the digest is evidence integrity, not authorization,
        custody, service, billing, payment, or settlement authority. Any
        malformed source-bound decision fails closed during construction, while
        Kennel EOS remains exclusively authoritative for financial execution
        and settlement.
        """
        return _digest(self.to_dict())


def authorize_process_service_assignment(
    *,
    instruction: LegalInstruction,
    document: ProcessDocument,
    district: District,
    sheriff_office: SheriffOffice,
    deputy: Deputy,
    assignment_decision_id: str,
    assignment_evidence_reference: str,
    decided_at: datetime,
) -> ProcessServiceAssignmentDecision:
    """Create one eligible assignment decision from exact validated P1 facts.

    Tenant identity, instruction/document bindings, accepted/received state,
    District -> SheriffOffice -> Deputy lineage, explicit evidence, and UTC
    chronology are all checked fail closed. Inputs are never mutated. The
    result is an immutable evidence decision, not a custody event, document
    allocation transition, service attempt, service execution, return,
    authorization-role assignment, or financial action; Kennel EOS remains the
    exclusive financial execution and settlement authority.
    """
    _validate_p1(instruction, LegalInstruction)
    _validate_p1(document, ProcessDocument)
    _validate_p1(district, District)
    _validate_p1(sheriff_office, SheriffOffice)
    _validate_p1(deputy, Deputy)

    tenant = _tenant(instruction.tenant_id)
    for value in (document, district, sheriff_office, deputy):
        if _tenant(value.tenant_id) != tenant:
            _fail("P3_TENANT_MISMATCH")

    if instruction.document_id != document.document_id or instruction.case_matter_id != document.case_matter_id:
        _fail("P3_INSTRUCTION_DOCUMENT_MISMATCH")
    if instruction.state is not LegalInstructionState.ACCEPTED:
        _fail("P3_INSTRUCTION_NOT_ACCEPTED")
    if document.state is not ProcessDocumentState.RECEIVED:
        _fail("P3_DOCUMENT_NOT_RECEIVED")
    if sheriff_office.district_id != district.district_id:
        _fail("P3_DISTRICT_OFFICE_LINEAGE_MISMATCH")
    if deputy.sheriff_office_id != sheriff_office.sheriff_office_id:
        _fail("P3_OFFICE_DEPUTY_LINEAGE_MISMATCH")

    decision_at = _utc_timestamp("decided_at", decided_at)
    accepted_at = _transition_time(instruction.transition_history, LegalInstructionState.ACCEPTED)
    received_at = _transition_time(document.transition_history, ProcessDocumentState.RECEIVED)
    if decision_at < instruction.registered_at or decision_at < document.registered_at:
        _fail("P3_ASSIGNMENT_CHRONOLOGY_INVALID")
    if decision_at < accepted_at or decision_at < received_at:
        _fail("P3_ASSIGNMENT_CHRONOLOGY_INVALID")

    instruction_fingerprint = _fingerprint("instruction_fingerprint", instruction.fingerprint)
    document_fingerprint = _fingerprint("document_fingerprint", document.fingerprint)
    district_fingerprint = _fingerprint("district_fingerprint", district.fingerprint)
    sheriff_office_fingerprint = _fingerprint("sheriff_office_fingerprint", sheriff_office.fingerprint)
    deputy_fingerprint = _fingerprint("deputy_fingerprint", deputy.fingerprint)
    decision_id = _identity("assignment_decision_id", assignment_decision_id)
    evidence_reference = _text("assignment_evidence_reference", assignment_evidence_reference)
    payload = _decision_payload(
        tenant_id=tenant,
        assignment_decision_id=decision_id,
        instruction_id=instruction.instruction_id,
        case_matter_id=instruction.case_matter_id,
        document_id=document.document_id,
        district_id=district.district_id,
        sheriff_office_id=sheriff_office.sheriff_office_id,
        deputy_id=deputy.deputy_id,
        instruction_fingerprint=instruction_fingerprint,
        document_fingerprint=document_fingerprint,
        district_fingerprint=district_fingerprint,
        sheriff_office_fingerprint=sheriff_office_fingerprint,
        deputy_fingerprint=deputy_fingerprint,
        assignment_evidence_reference=evidence_reference,
        decided_at=decision_at,
    )
    return ProcessServiceAssignmentDecision(
        tenant_id=tenant,
        assignment_decision_id=decision_id,
        instruction_id=instruction.instruction_id,
        case_matter_id=instruction.case_matter_id,
        document_id=document.document_id,
        district_id=district.district_id,
        sheriff_office_id=sheriff_office.sheriff_office_id,
        deputy_id=deputy.deputy_id,
        instruction_fingerprint=instruction_fingerprint,
        document_fingerprint=document_fingerprint,
        district_fingerprint=district_fingerprint,
        sheriff_office_fingerprint=sheriff_office_fingerprint,
        deputy_fingerprint=deputy_fingerprint,
        assignment_evidence_reference=evidence_reference,
        decided_at=decision_at,
        _construction_proof=_issue_proof(_digest(payload)),
    )


__all__ = [
    "SCHEMA",
    "VERSION",
    "ProcessServiceAssignmentAuthorityError",
    "ProcessServiceAssignmentDecision",
    "authorize_process_service_assignment",
]


# ARTIFACT: process_service_assignment_authority.py
# VERSION: v1.0.0-PROCESS-SERVICE-ASSIGNMENT-AUTHORITY
# AUTHORITY BOUNDARY: pure P3 assignment-decision evidence only; no custody or service authority.
# TENANT POSTURE: exact explicit tenant binding; cross-tenant composition fails closed.
# FAIL-CLOSED POSTURE: malformed P1 facts, lineage, evidence, and chronology reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
