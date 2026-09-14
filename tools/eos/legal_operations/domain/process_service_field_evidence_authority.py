"""Sovereign offline field-observation command and sync-receipt authority.

TITLE: Wilsy OS Process-Service Offline Field Evidence Authority
VERSION: v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Bind an immutable device observation to an already canonical P1/P2
         ServiceAttempt without declaring an attempt, service, execution, or return.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/process_service_field_evidence_authority.py
COLLABORATION / OWNERSHIP: P5 mobile evidence only; P1 owns legal lifecycle,
                            P2 owns durable lifecycle snapshots, and callers
                            own Mongo sessions and transactions.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE establishes
           immutable attempt-bound observation commands and sync receipts.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Canonical tenant, attempt, instruction, document, and deputy
                 identities derive only from an exact validated ServiceAttempt.
AUTHORITY BOUNDARY: Evidence acceptance only; mobile observations are not legal
                     service truth and never invoke P5 lifecycle authorities.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution,
                              payment, and settlement.
FAIL-CLOSED DECLARATION: Exact P1 type, immutable payload proof, identities,
                         chronology, evidence reference, and SHA3-512 are required.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import json
import re
from typing import Callable, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationReceipt,
)

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE/V1"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})


class ProcessServiceFieldEvidenceAuthorityError(ValueError):
    """Stable fail-closed error for offline observation authority."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise ProcessServiceFieldEvidenceAuthorityError(code)


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"P5M_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("P5M_TENANT_INVALID")
    return tenant


def _timestamp(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        _fail(f"P5M_{name.upper()}_INVALID")
    return value


def _fingerprint(value: object, name: str) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail(f"P5M_{name.upper()}_INVALID")
    return value


def _reference(value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or not value:
        _fail("P5M_EVIDENCE_REFERENCE_INVALID")
    return value


def _digest(payload: object) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _proof_contract() -> tuple[Callable[[str], object], Callable[[object], bool], Callable[[object], str | None]]:
    @dataclass(frozen=True, slots=True)
    class _Proof:
        digest: str

    def issue(digest: str) -> object:
        return _Proof(digest)

    def valid(value: object) -> bool:
        return isinstance(value, _Proof)

    def digest(value: object) -> str | None:
        return value.digest if isinstance(value, _Proof) else None

    return issue, valid, digest


_issue_proof, _is_proof, _proof_digest = _proof_contract()


def _command_payload(*, tenant_id: str, attempt_id: str, instruction_id: str, document_id: str, deputy_id: str, district_id: str, sheriff_office_id: str, source_attempt_fingerprint: str, device_id: str, event_id: str, sequence_number: int, occurred_at: datetime, evidence_reference: str, evidence_fingerprint: str, previous_event_fingerprint: str | None) -> dict[str, object]:
    return {"schema": SCHEMA, "version": VERSION, "entity_type": "OfflineFieldEvidenceCommand", "tenant_id": tenant_id, "attempt_id": attempt_id, "instruction_id": instruction_id, "document_id": document_id, "deputy_id": deputy_id, "district_id": district_id, "sheriff_office_id": sheriff_office_id, "source_attempt_fingerprint": source_attempt_fingerprint, "device_id": device_id, "event_id": event_id, "sequence_number": sequence_number, "occurred_at": occurred_at.isoformat(), "evidence_reference": evidence_reference, "evidence_fingerprint": evidence_fingerprint, "previous_event_fingerprint": previous_event_fingerprint}


@dataclass(frozen=True, slots=True)
class OfflineFieldEvidenceCommand:
    """Immutable device observation derived from one validated ServiceAttempt."""

    tenant_id: str
    attempt_id: str
    instruction_id: str
    document_id: str
    deputy_id: str
    district_id: str
    sheriff_office_id: str
    source_attempt_fingerprint: str
    device_id: str
    event_id: str
    sequence_number: int
    occurred_at: datetime
    evidence_reference: str
    evidence_fingerprint: str
    previous_event_fingerprint: str | None = None
    _construction_proof: object = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not _is_proof(self._construction_proof):
            _fail("P5M_COMMAND_FACTORY_REQUIRED")
        _tenant(self.tenant_id)
        for name in ("attempt_id", "instruction_id", "document_id", "deputy_id", "district_id", "sheriff_office_id", "device_id", "event_id"):
            _identity(name, getattr(self, name))
        _fingerprint(self.source_attempt_fingerprint, "source_attempt_fingerprint")
        if not isinstance(self.sequence_number, int) or isinstance(self.sequence_number, bool) or self.sequence_number < 1:
            _fail("P5M_SEQUENCE_NUMBER_INVALID")
        _timestamp("occurred_at", self.occurred_at)
        _reference(self.evidence_reference)
        _fingerprint(self.evidence_fingerprint, "evidence_fingerprint")
        if self.sequence_number == 1 and self.previous_event_fingerprint is not None:
            _fail("P5M_SEQUENCE_PREDECESSOR_INVALID")
        if self.sequence_number > 1:
            _fingerprint(self.previous_event_fingerprint, "previous_event_fingerprint")
        if _proof_digest(self._construction_proof) != _digest(self.to_dict()):
            _fail("P5M_COMMAND_BINDING_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Return deterministic canonical observation evidence."""
        return _command_payload(tenant_id=self.tenant_id, attempt_id=self.attempt_id, instruction_id=self.instruction_id, document_id=self.document_id, deputy_id=self.deputy_id, district_id=self.district_id, sheriff_office_id=self.sheriff_office_id, source_attempt_fingerprint=self.source_attempt_fingerprint, device_id=self.device_id, event_id=self.event_id, sequence_number=self.sequence_number, occurred_at=self.occurred_at, evidence_reference=self.evidence_reference, evidence_fingerprint=self.evidence_fingerprint, previous_event_fingerprint=self.previous_event_fingerprint)

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 over the canonical observation payload."""
        return _digest(self.to_dict())


def create_offline_field_evidence_command(*, attempt: ServiceAttempt, allocation_receipt: ProcessServiceAllocationReceipt, allocation_current: ProcessServiceAllocationCurrent, device_id: str, event_id: str, sequence_number: int, occurred_at: datetime, evidence_reference: str, evidence_fingerprint: str, previous_event_fingerprint: str | None = None) -> OfflineFieldEvidenceCommand:
    """Create one observation command from exact P1 attempt context.

    All legal identities and the source fingerprint derive from ``attempt``;
    device and evidence values are provenance supplied by the field channel.
    This function does not transition the attempt or create legal service truth.
    """
    if type(attempt) is not ServiceAttempt or type(allocation_receipt) is not ProcessServiceAllocationReceipt or type(allocation_current) is not ProcessServiceAllocationCurrent:
        _fail("P5M_SOURCE_ATTEMPT_REQUIRED")
    try:
        attempt.__post_init__()
        allocation_receipt.__post_init__()
        allocation_current.__post_init__()
    except Exception as error:
        raise ProcessServiceFieldEvidenceAuthorityError("P5M_SOURCE_ATTEMPT_INVALID") from error
    occurred = _timestamp("occurred_at", occurred_at)
    if occurred < attempt.allocated_at:
        _fail("P5M_CHRONOLOGY_INVALID")
    if allocation_receipt.tenant_id != attempt.tenant_id or allocation_receipt.instruction_id != attempt.instruction_id or allocation_receipt.document_id != attempt.document_id or allocation_receipt.deputy_id != attempt.deputy_id or allocation_receipt.allocation_evidence_reference != attempt.allocation_evidence_reference:
        _fail("P5M_ALLOCATION_CORRELATION_INVALID")
    if allocation_current.tenant_id != allocation_receipt.tenant_id or allocation_current.document_id != allocation_receipt.document_id or allocation_current.process_document_fingerprint != allocation_receipt.allocated_document_fingerprint or allocation_current.custody_chain_fingerprint != allocation_receipt.result_custody_chain_fingerprint or allocation_current.custody_head_event_id != allocation_receipt.allocation_custody_event_id or allocation_current.custody_head_fingerprint != allocation_receipt.allocation_custody_event_fingerprint or allocation_current.custody_head_sequence_number != allocation_receipt.prior_custody_head_sequence_number + 1 or allocation_current.current_holder_reference != allocation_receipt.to_holder_reference or allocation_receipt.to_holder_reference != allocation_receipt.deputy_id or allocation_current.authority_evidence_reference != allocation_receipt.allocation_command_id or allocation_current.authority_evidence_fingerprint != allocation_receipt.fingerprint:
        _fail("P5M_ALLOCATION_CORRELATION_INVALID")
    values = dict(tenant_id=attempt.tenant_id, attempt_id=attempt.attempt_id, instruction_id=attempt.instruction_id, document_id=attempt.document_id, deputy_id=attempt.deputy_id, district_id=allocation_receipt.district_id, sheriff_office_id=allocation_receipt.sheriff_office_id, source_attempt_fingerprint=attempt.fingerprint, device_id=_identity("device_id", device_id), event_id=_identity("event_id", event_id), sequence_number=sequence_number, occurred_at=occurred, evidence_reference=_reference(evidence_reference), evidence_fingerprint=_fingerprint(evidence_fingerprint, "evidence_fingerprint"), previous_event_fingerprint=previous_event_fingerprint)
    payload = _command_payload(**cast(dict[str, object], values))  # pyright: ignore[reportArgumentType]
    return OfflineFieldEvidenceCommand(_construction_proof=_issue_proof(_digest(payload)), **cast(dict[str, object], values))  # pyright: ignore[reportArgumentType]


def hydrate_offline_field_evidence_command(payload: object) -> OfflineFieldEvidenceCommand:
    """Strictly hydrate one persisted observation command."""
    required = {"schema", "version", "entity_type", "tenant_id", "attempt_id", "instruction_id", "document_id", "deputy_id", "district_id", "sheriff_office_id", "source_attempt_fingerprint", "device_id", "event_id", "sequence_number", "occurred_at", "evidence_reference", "evidence_fingerprint", "previous_event_fingerprint"}
    if not isinstance(payload, dict) or set(payload) != required or payload.get("schema") != SCHEMA or payload.get("version") != VERSION or payload.get("entity_type") != "OfflineFieldEvidenceCommand":
        _fail("P5M_COMMAND_PAYLOAD_INVALID")
    try:
        occurred = datetime.fromisoformat(cast(str, payload["occurred_at"]))
        values = dict(tenant_id=_tenant(payload["tenant_id"]), attempt_id=_identity("attempt_id", payload["attempt_id"]), instruction_id=_identity("instruction_id", payload["instruction_id"]), document_id=_identity("document_id", payload["document_id"]), deputy_id=_identity("deputy_id", payload["deputy_id"]), district_id=_identity("district_id", payload["district_id"]), sheriff_office_id=_identity("sheriff_office_id", payload["sheriff_office_id"]), source_attempt_fingerprint=_fingerprint(payload["source_attempt_fingerprint"], "source_attempt_fingerprint"), device_id=_identity("device_id", payload["device_id"]), event_id=_identity("event_id", payload["event_id"]), sequence_number=payload["sequence_number"], occurred_at=_timestamp("occurred_at", occurred), evidence_reference=_reference(payload["evidence_reference"]), evidence_fingerprint=_fingerprint(payload["evidence_fingerprint"], "evidence_fingerprint"), previous_event_fingerprint=payload["previous_event_fingerprint"])
        canonical = _command_payload(**cast(dict[str, object], values))  # pyright: ignore[reportArgumentType]
        return OfflineFieldEvidenceCommand(_construction_proof=_issue_proof(_digest(canonical)), **cast(dict[str, object], values))  # pyright: ignore[reportArgumentType]
    except ProcessServiceFieldEvidenceAuthorityError:
        raise
    except Exception as error:
        raise ProcessServiceFieldEvidenceAuthorityError("P5M_COMMAND_PAYLOAD_INVALID") from error


def _receipt_payload(*, tenant_id: str, receipt_id: str, event_id: str, device_id: str, sequence_number: int, attempt_id: str, instruction_id: str, document_id: str, deputy_id: str, district_id: str, sheriff_office_id: str, evidence_reference: str, evidence_fingerprint: str, command_fingerprint: str, accepted_at: datetime, evidence_identity: str) -> dict[str, object]:
    return {"schema": SCHEMA, "version": VERSION, "entity_type": "OfflineFieldEvidenceSyncReceipt", "tenant_id": tenant_id, "receipt_id": receipt_id, "event_id": event_id, "device_id": device_id, "sequence_number": sequence_number, "attempt_id": attempt_id, "instruction_id": instruction_id, "document_id": document_id, "deputy_id": deputy_id, "district_id": district_id, "sheriff_office_id": sheriff_office_id, "evidence_reference": evidence_reference, "evidence_fingerprint": evidence_fingerprint, "command_fingerprint": command_fingerprint, "accepted_at": accepted_at.isoformat(), "evidence_identity": evidence_identity}


@dataclass(frozen=True, slots=True)
class OfflineFieldEvidenceSyncReceipt:
    """Immutable acknowledgement that one observation entered the evidence journal."""

    tenant_id: str
    receipt_id: str
    event_id: str
    device_id: str
    sequence_number: int
    attempt_id: str
    instruction_id: str
    document_id: str
    deputy_id: str
    district_id: str
    sheriff_office_id: str
    evidence_reference: str
    evidence_fingerprint: str
    command_fingerprint: str
    accepted_at: datetime
    evidence_identity: str
    _construction_proof: object = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not _is_proof(self._construction_proof):
            _fail("P5M_RECEIPT_FACTORY_REQUIRED")
        _tenant(self.tenant_id)
        for name in ("receipt_id", "event_id", "device_id", "attempt_id", "instruction_id", "document_id", "deputy_id", "district_id", "sheriff_office_id"):
            _identity(name, getattr(self, name))
        if not isinstance(self.sequence_number, int) or isinstance(self.sequence_number, bool) or self.sequence_number < 1:
            _fail("P5M_SEQUENCE_NUMBER_INVALID")
        _reference(self.evidence_reference)
        _fingerprint(self.evidence_fingerprint, "evidence_fingerprint")
        _fingerprint(self.command_fingerprint, "command_fingerprint")
        _timestamp("accepted_at", self.accepted_at)
        _fingerprint(self.evidence_identity, "evidence_identity")
        if _proof_digest(self._construction_proof) != _digest(self.to_dict()):
            _fail("P5M_RECEIPT_BINDING_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Return deterministic canonical sync-receipt evidence."""
        return _receipt_payload(tenant_id=self.tenant_id, receipt_id=self.receipt_id, event_id=self.event_id, device_id=self.device_id, sequence_number=self.sequence_number, attempt_id=self.attempt_id, instruction_id=self.instruction_id, document_id=self.document_id, deputy_id=self.deputy_id, district_id=self.district_id, sheriff_office_id=self.sheriff_office_id, evidence_reference=self.evidence_reference, evidence_fingerprint=self.evidence_fingerprint, command_fingerprint=self.command_fingerprint, accepted_at=self.accepted_at, evidence_identity=self.evidence_identity)

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 over the canonical receipt payload."""
        return _digest(self.to_dict())


def _issue_sync_receipt(*, command: OfflineFieldEvidenceCommand, receipt_id: str, accepted_at: datetime) -> OfflineFieldEvidenceSyncReceipt:
    if type(command) is not OfflineFieldEvidenceCommand:
        _fail("P5M_COMMAND_REQUIRED")
    command.__post_init__()
    accepted = _timestamp("accepted_at", accepted_at)
    if accepted < command.occurred_at:
        _fail("P5M_CHRONOLOGY_INVALID")
    result_id = _identity("receipt_id", receipt_id)
    identity = _digest({"schema": SCHEMA, "version": VERSION, "tenant_id": command.tenant_id, "event_id": command.event_id, "device_id": command.device_id, "sequence_number": command.sequence_number, "command_fingerprint": command.fingerprint, "receipt_id": result_id})
    payload = _receipt_payload(tenant_id=command.tenant_id, receipt_id=result_id, event_id=command.event_id, device_id=command.device_id, sequence_number=command.sequence_number, attempt_id=command.attempt_id, instruction_id=command.instruction_id, document_id=command.document_id, deputy_id=command.deputy_id, district_id=command.district_id, sheriff_office_id=command.sheriff_office_id, evidence_reference=command.evidence_reference, evidence_fingerprint=command.evidence_fingerprint, command_fingerprint=command.fingerprint, accepted_at=accepted, evidence_identity=identity)
    return OfflineFieldEvidenceSyncReceipt(tenant_id=command.tenant_id, receipt_id=result_id, event_id=command.event_id, device_id=command.device_id, sequence_number=command.sequence_number, attempt_id=command.attempt_id, instruction_id=command.instruction_id, document_id=command.document_id, deputy_id=command.deputy_id, district_id=command.district_id, sheriff_office_id=command.sheriff_office_id, evidence_reference=command.evidence_reference, evidence_fingerprint=command.evidence_fingerprint, command_fingerprint=command.fingerprint, accepted_at=accepted, evidence_identity=identity, _construction_proof=_issue_proof(_digest(payload)))


def hydrate_offline_field_evidence_sync_receipt(payload: object) -> OfflineFieldEvidenceSyncReceipt:
    """Strictly hydrate one persisted sync receipt."""
    required = {"schema", "version", "entity_type", "tenant_id", "receipt_id", "event_id", "device_id", "sequence_number", "attempt_id", "instruction_id", "document_id", "deputy_id", "district_id", "sheriff_office_id", "evidence_reference", "evidence_fingerprint", "command_fingerprint", "accepted_at", "evidence_identity"}
    if not isinstance(payload, dict) or set(payload) != required or payload.get("schema") != SCHEMA or payload.get("version") != VERSION or payload.get("entity_type") != "OfflineFieldEvidenceSyncReceipt":
        _fail("P5M_RECEIPT_PAYLOAD_INVALID")
    try:
        accepted = datetime.fromisoformat(cast(str, payload["accepted_at"]))
        values = dict(tenant_id=_tenant(payload["tenant_id"]), receipt_id=_identity("receipt_id", payload["receipt_id"]), event_id=_identity("event_id", payload["event_id"]), device_id=_identity("device_id", payload["device_id"]), sequence_number=payload["sequence_number"], attempt_id=_identity("attempt_id", payload["attempt_id"]), instruction_id=_identity("instruction_id", payload["instruction_id"]), document_id=_identity("document_id", payload["document_id"]), deputy_id=_identity("deputy_id", payload["deputy_id"]), district_id=_identity("district_id", payload["district_id"]), sheriff_office_id=_identity("sheriff_office_id", payload["sheriff_office_id"]), evidence_reference=_reference(payload["evidence_reference"]), evidence_fingerprint=_fingerprint(payload["evidence_fingerprint"], "evidence_fingerprint"), command_fingerprint=_fingerprint(payload["command_fingerprint"], "command_fingerprint"), accepted_at=_timestamp("accepted_at", accepted), evidence_identity=_fingerprint(payload["evidence_identity"], "evidence_identity"))
        canonical = _receipt_payload(**cast(dict[str, object], values))  # pyright: ignore[reportArgumentType]
        return OfflineFieldEvidenceSyncReceipt(_construction_proof=_issue_proof(_digest(canonical)), **cast(dict[str, object], values))  # pyright: ignore[reportArgumentType]
    except ProcessServiceFieldEvidenceAuthorityError:
        raise
    except Exception as error:
        raise ProcessServiceFieldEvidenceAuthorityError("P5M_RECEIPT_PAYLOAD_INVALID") from error


__all__ = ["SCHEMA", "VERSION", "ProcessServiceFieldEvidenceAuthorityError", "OfflineFieldEvidenceCommand", "OfflineFieldEvidenceSyncReceipt", "create_offline_field_evidence_command", "hydrate_offline_field_evidence_command", "hydrate_offline_field_evidence_sync_receipt"]


# ARTIFACT: process_service_field_evidence_authority.py
# VERSION: v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE
# AUTHORITY BOUNDARY: immutable mobile observation and sync acknowledgement only.
# TENANT POSTURE: canonical identities derive from exact ServiceAttempt context.
# FAIL-CLOSED POSTURE: malformed, divergent, and chronologically invalid evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
