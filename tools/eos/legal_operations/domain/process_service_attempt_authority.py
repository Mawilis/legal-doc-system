"""Canonical pure-Python process-service attempt-authorization evidence.

TITLE: Wilsy OS Process-Service Attempt Authority
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Bind one explicit process-service attempt authorization to a validated
         P4 allocation receipt and current pointer without constructing or
         transitioning any later service lifecycle fact.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/process_service_attempt_authority.py
COLLABORATION / OWNERSHIP: P5A owns immutable attempt-authorization evidence;
                            P4B owns allocation receipt/current evidence; later
                            callers own persistence and ServiceAttempt
                            lifecycle transitions.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY establishes
           strict P4 receipt/current correlation and payload-bound immutable
           attempt-authorization evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque tenant, identity, custody, and evidence
                             references only; no network, provider, credential,
                             location, or personal-data expansion.
TENANT BOUNDARY: Tenant identity is derived only from the validated P4 receipt
                 and current pointer; cross-tenant composition fails closed.
AUTHORITY BOUNDARY: Attempt-authorization evidence only. This module does not
                    construct or transition ServiceAttempt, ServiceExecution,
                    ReturnOfService, custody, persistence, IAM, or transport
                    truth.
FINANCIAL AUTHORITY BOUNDARY: Attempt authorization is not invoicing, payment,
                              execution, or settlement; Kennel EOS exclusively
                              owns financial execution and settlement.
FAIL-CLOSED DECLARATION: Exact P4 runtime types, P4 validation contracts,
                         tenant/document correlation, custody lineage,
                         evidence bindings, UTC chronology, and immutable
                         payload proof are mandatory; malformed or forged
                         authority is rejected through stable P5A errors.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import json
import re
from typing import Callable, Final, NoReturn, cast

from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationReceipt,
)


VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-ATTEMPT-AUTHORITY/V1"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})


class ProcessServiceAttemptAuthorityError(ValueError):
    """Governed fail-closed error for P5A attempt-authorization evidence.

    The stable ``code`` identifies malformed inputs or a broken P4 binding.
    Raising this exception performs no persistence, lifecycle transition,
    custody mutation, service execution, return generation, billing, payment,
    or settlement. Kennel EOS remains the exclusive financial execution and
    settlement authority.
    """

    def __init__(self, code: str) -> None:
        """Create one structured, deterministic P5A validation failure."""
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    """Raise one stable P5A failure without manufacturing authority."""
    raise ProcessServiceAttemptAuthorityError(code)


def _identity(name: str, value: object) -> str:
    """Require one explicit canonical opaque identity."""
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"P5A_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require a real tenant and reject pseudo or global aliases."""
    tenant_id = _identity("tenant_id", value)
    if tenant_id.casefold() in _FORBIDDEN_TENANTS:
        _fail("P5A_TENANT_INVALID")
    return tenant_id


def _fingerprint(name: str, value: object) -> str:
    """Require one exact lowercase SHA3-512 digest."""
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail(f"P5A_{name.upper()}_INVALID")
    return cast(str, value)


def _utc_timestamp(name: str, value: object) -> datetime:
    """Require an explicit timezone-aware UTC timestamp."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        _fail(f"P5A_{name.upper()}_INVALID")
    return cast(datetime, value)


def _canonical(value: object) -> object:
    """Convert supported evidence values to deterministic JSON primitives."""
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _digest(payload: object) -> str:
    """Hash deterministic canonical JSON with lowercase SHA3-512."""
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _make_proof_contract() -> tuple[
    Callable[[str], object],
    Callable[[object], bool],
    Callable[[object], str | None],
]:
    """Create a private payload-bound proof issuer and validator."""

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


def _decision_payload(
    *,
    tenant_id: str,
    attempt_authority_id: str,
    attempt_id: str,
    instruction_id: str,
    document_id: str,
    deputy_id: str,
    allocation_command_id: str,
    allocation_receipt_evidence_identity: str,
    allocation_receipt_fingerprint: str,
    allocation_current_fingerprint: str,
    allocated_at: datetime,
    authorized_at: datetime,
) -> dict[str, object]:
    """Build the complete semantic P5A payload used by proof and serialization."""
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "entity_type": "ProcessServiceAttemptAuthorityDecision",
        "tenant_id": tenant_id,
        "attempt_authority_id": attempt_authority_id,
        "attempt_id": attempt_id,
        "instruction_id": instruction_id,
        "document_id": document_id,
        "deputy_id": deputy_id,
        "allocation_command_id": allocation_command_id,
        "allocation_receipt_evidence_identity": allocation_receipt_evidence_identity,
        "allocation_receipt_fingerprint": allocation_receipt_fingerprint,
        "allocation_current_fingerprint": allocation_current_fingerprint,
        "allocated_at": _canonical(allocated_at),
        "authorized_at": _canonical(authorized_at),
    }


def _validate_p4(value: object, expected: type[object], code: str) -> None:
    """Re-run the exact P4 value contract before deriving any P5A field."""
    if type(value) is not expected:
        _fail(code)
    try:
        cast(ProcessServiceAllocationReceipt | ProcessServiceAllocationCurrent, value).__post_init__()
    except Exception as error:
        raise ProcessServiceAttemptAuthorityError(code) from error


@dataclass(frozen=True, slots=True)
class ProcessServiceAttemptAuthorityDecision:
    """Immutable tenant-scoped P5A attempt-authorization evidence.

    The decision is derived exclusively from one validated P4 allocation
    receipt/current pair. Its payload contains no caller-supplied tenant,
    custody, assignment, or allocation-result claims. Direct construction is
    rejected without the private payload-bound factory proof, and reusing a
    proof after changing any field is rejected. The object is pure evidence:
    it does not construct or transition a ``ServiceAttempt`` and carries no
    persistence, IAM, transport, invoice, payment, execution, or settlement
    authority.
    """

    tenant_id: str
    attempt_authority_id: str
    attempt_id: str
    instruction_id: str
    document_id: str
    deputy_id: str
    allocation_command_id: str
    allocation_receipt_evidence_identity: str
    allocation_receipt_fingerprint: str
    allocation_current_fingerprint: str
    allocated_at: datetime
    authorized_at: datetime
    _construction_proof: object = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Reject forged, malformed, or proof-mismatched immutable evidence."""
        proof = self._construction_proof
        if not _is_proof(proof):
            _fail("P5A_DECISION_FACTORY_REQUIRED")
        _tenant(self.tenant_id)
        for name in (
            "attempt_authority_id",
            "attempt_id",
            "instruction_id",
            "document_id",
            "deputy_id",
            "allocation_command_id",
        ):
            _identity(name, getattr(self, name))
        _fingerprint("allocation_receipt_evidence_identity", self.allocation_receipt_evidence_identity)
        _fingerprint("allocation_receipt_fingerprint", self.allocation_receipt_fingerprint)
        _fingerprint("allocation_current_fingerprint", self.allocation_current_fingerprint)
        _utc_timestamp("allocated_at", self.allocated_at)
        _utc_timestamp("authorized_at", self.authorized_at)
        if self.authorized_at < self.allocated_at:
            _fail("P5A_AUTHORIZATION_CHRONOLOGY_INVALID")
        if _proof_digest(proof) != _digest(self.to_dict()):
            _fail("P5A_DECISION_SOURCE_BINDING_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Serialize complete immutable P5A evidence deterministically.

        The mapping is a canonical, tenant-scoped evidence payload. It carries
        no persistence or lifecycle mutation command and does not assert that a
        service attempt, service execution, return, invoice, payment, or
        settlement occurred. ``fingerprint`` exposes its SHA3-512 digest.
        """
        return _decision_payload(
            tenant_id=self.tenant_id,
            attempt_authority_id=self.attempt_authority_id,
            attempt_id=self.attempt_id,
            instruction_id=self.instruction_id,
            document_id=self.document_id,
            deputy_id=self.deputy_id,
            allocation_command_id=self.allocation_command_id,
            allocation_receipt_evidence_identity=self.allocation_receipt_evidence_identity,
            allocation_receipt_fingerprint=self.allocation_receipt_fingerprint,
            allocation_current_fingerprint=self.allocation_current_fingerprint,
            allocated_at=self.allocated_at,
            authorized_at=self.authorized_at,
        )

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 over the complete canonical P5A payload."""
        return _digest(self.to_dict())


def authorize_process_service_attempt(
    *,
    allocation_receipt: ProcessServiceAllocationReceipt,
    allocation_current: ProcessServiceAllocationCurrent,
    attempt_authority_id: str,
    attempt_id: str,
    authorized_at: datetime,
) -> ProcessServiceAttemptAuthorityDecision:
    """Authorize one attempt from exact correlated P4 allocation evidence.

    P4 receipt/current objects are revalidated by exact runtime type and their
    own validation contract. Tenant, instruction, document, deputy,
    allocation command, custody references, receipt/current fingerprints, and
    allocation chronology are then derived from those validated objects. The
    result is immutable attempt-authorization evidence only; callers retain all
    persistence/session/transaction ownership and must separately traverse the
    P1 ``ServiceAttempt`` lifecycle before any service execution or return.
    """
    _validate_p4(
        allocation_receipt,
        ProcessServiceAllocationReceipt,
        "P5A_RECEIPT_REQUIRED",
    )
    _validate_p4(
        allocation_current,
        ProcessServiceAllocationCurrent,
        "P5A_CURRENT_REQUIRED",
    )
    receipt = cast(ProcessServiceAllocationReceipt, allocation_receipt)
    current = cast(ProcessServiceAllocationCurrent, allocation_current)
    authorized = _utc_timestamp("authorized_at", authorized_at)
    if authorized < receipt.allocated_at:
        _fail("P5A_AUTHORIZATION_CHRONOLOGY_INVALID")

    if receipt.tenant_id != current.tenant_id or receipt.document_id != current.document_id:
        _fail("P5A_RECEIPT_CURRENT_TENANT_DOCUMENT_MISMATCH")
    if current.process_document_fingerprint != receipt.allocated_document_fingerprint:
        _fail("P5A_PROCESS_DOCUMENT_FINGERPRINT_MISMATCH")
    if current.custody_chain_fingerprint != receipt.result_custody_chain_fingerprint:
        _fail("P5A_CUSTODY_CHAIN_FINGERPRINT_MISMATCH")
    if current.custody_head_event_id != receipt.allocation_custody_event_id:
        _fail("P5A_CUSTODY_HEAD_EVENT_MISMATCH")
    if current.custody_head_fingerprint != receipt.allocation_custody_event_fingerprint:
        _fail("P5A_CUSTODY_HEAD_FINGERPRINT_MISMATCH")
    if current.custody_head_sequence_number != receipt.prior_custody_head_sequence_number + 1:
        _fail("P5A_CUSTODY_HEAD_SEQUENCE_MISMATCH")
    if receipt.to_holder_reference != receipt.deputy_id:
        _fail("P5A_RECEIPT_HOLDER_DEPUTY_MISMATCH")
    if current.current_holder_reference != receipt.to_holder_reference:
        _fail("P5A_CURRENT_HOLDER_MISMATCH")
    if current.authority_evidence_reference != receipt.allocation_command_id:
        _fail("P5A_AUTHORITY_REFERENCE_MISMATCH")
    if current.authority_evidence_fingerprint != receipt.fingerprint:
        _fail("P5A_AUTHORITY_FINGERPRINT_MISMATCH")

    authority_id = _identity("attempt_authority_id", attempt_authority_id)
    attempt_identity = _identity("attempt_id", attempt_id)
    current_fingerprint = _digest(current.to_dict())
    payload = _decision_payload(
        tenant_id=_tenant(receipt.tenant_id),
        attempt_authority_id=authority_id,
        attempt_id=attempt_identity,
        instruction_id=_identity("instruction_id", receipt.instruction_id),
        document_id=_identity("document_id", receipt.document_id),
        deputy_id=_identity("deputy_id", receipt.deputy_id),
        allocation_command_id=_identity("allocation_command_id", receipt.allocation_command_id),
        allocation_receipt_evidence_identity=_fingerprint(
            "allocation_receipt_evidence_identity", receipt.evidence_identity
        ),
        allocation_receipt_fingerprint=_fingerprint("allocation_receipt_fingerprint", receipt.fingerprint),
        allocation_current_fingerprint=_fingerprint("allocation_current_fingerprint", current_fingerprint),
        allocated_at=receipt.allocated_at,
        authorized_at=authorized,
    )
    return ProcessServiceAttemptAuthorityDecision(
        tenant_id=cast(str, payload["tenant_id"]),
        attempt_authority_id=authority_id,
        attempt_id=attempt_identity,
        instruction_id=cast(str, payload["instruction_id"]),
        document_id=cast(str, payload["document_id"]),
        deputy_id=cast(str, payload["deputy_id"]),
        allocation_command_id=cast(str, payload["allocation_command_id"]),
        allocation_receipt_evidence_identity=cast(
            str, payload["allocation_receipt_evidence_identity"]
        ),
        allocation_receipt_fingerprint=cast(str, payload["allocation_receipt_fingerprint"]),
        allocation_current_fingerprint=cast(str, payload["allocation_current_fingerprint"]),
        allocated_at=receipt.allocated_at,
        authorized_at=authorized,
        _construction_proof=_issue_proof(_digest(payload)),
    )


__all__ = [
    "SCHEMA",
    "VERSION",
    "ProcessServiceAttemptAuthorityError",
    "ProcessServiceAttemptAuthorityDecision",
    "authorize_process_service_attempt",
]


# ARTIFACT: process_service_attempt_authority.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY
# AUTHORITY BOUNDARY: canonical P5A attempt-authorization evidence only
# TENANT POSTURE: explicit tenant derived from correlated P4 allocation evidence
# FAIL-CLOSED POSTURE: exact P4 validation, binding, chronology, and proof required
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
