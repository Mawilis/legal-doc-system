"""Evidence authority for terminal service-attempt outcomes.

TITLE: Wilsy OS Process-Service Attempt Outcome Authority
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-AUTHORITY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Bind an evidenced ATTEMPTED -> COMPLETED or NOT_COMPLETED outcome to
         one validated P1 ServiceAttempt and its derived ServiceExecution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/process_service_attempt_outcome_authority.py
COLLABORATION / OWNERSHIP: P5 outcome authority only; P1 owns lifecycle and
                            ServiceExecution factories, P2 owns persistence,
                            callers own sessions and transactions.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-AUTHORITY
           establishes fail-closed terminal outcome evidence without creating
           ReturnOfService or financial truth.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Evidence references and SHA3-512 fingerprints are
                             opaque; GPS, photos, signatures, and providers do
                             not self-authenticate legal service.
TENANT BOUNDARY: Tenant and all legal identities derive from the exact P1
                 source attempt; pseudo/global tenants reject.
AUTHORITY BOUNDARY: Terminal outcome evidence and ServiceExecution binding only;
                    no ReturnOfService, invoice, payment, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Exact P1 type/state, terminal evidence, chronology,
                         source fingerprint, and private payload proof are mandatory.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import json
import re
from typing import Callable, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt, ServiceAttemptState

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-AUTHORITY"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-ATTEMPT-OUTCOME-AUTHORITY/V1"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})


class ProcessServiceAttemptOutcomeAuthorityError(ValueError):
    """Stable fail-closed terminal-outcome authority error."""

    def __init__(self, code: str) -> None:
        """Create one governed error carrying its stable code."""
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise ProcessServiceAttemptOutcomeAuthorityError(code)


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"P5E_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("P5E_TENANT_INVALID")
    return tenant


def _timestamp(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        _fail(f"P5E_{name.upper()}_INVALID")
    return value


def _reference(value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail("P5E_EVIDENCE_REFERENCE_INVALID")
    return value


def _sha3(value: object) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail("P5E_EVIDENCE_FINGERPRINT_INVALID")
    return value


def _digest(payload: object) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _proof_contract() -> tuple[Callable[[str], object], Callable[[object], bool], Callable[[object], str | None]]:
    """Create a closure-bound payload proof unavailable to ordinary callers."""
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


def _payload(*, tenant_id: str, attempt_id: str, instruction_id: str, document_id: str, deputy_id: str, source_attempt_fingerprint: str, outcome: ServiceAttemptState, evidence_identity: str, evidence_reference: str, evidence_fingerprint: str, occurred_at: datetime, service_execution_id: str, executed_at: datetime) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "entity_type": "ProcessServiceAttemptOutcomeDecision",
        "tenant_id": tenant_id,
        "attempt_id": attempt_id,
        "instruction_id": instruction_id,
        "document_id": document_id,
        "deputy_id": deputy_id,
        "source_attempt_fingerprint": source_attempt_fingerprint,
        "outcome": outcome.value,
        "evidence_identity": evidence_identity,
        "evidence_reference": evidence_reference,
        "evidence_fingerprint": evidence_fingerprint,
        "occurred_at": occurred_at.isoformat(),
        "service_execution_id": service_execution_id,
        "executed_at": executed_at.isoformat(),
    }


@dataclass(frozen=True, slots=True)
class ProcessServiceAttemptOutcomeDecision:
    """Immutable evidence binding for one terminal P1 attempt outcome."""

    tenant_id: str
    attempt_id: str
    instruction_id: str
    document_id: str
    deputy_id: str
    source_attempt_fingerprint: str
    outcome: ServiceAttemptState
    evidence_identity: str
    evidence_reference: str
    evidence_fingerprint: str
    occurred_at: datetime
    service_execution_id: str
    executed_at: datetime
    _construction_proof: object = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Reject direct construction or any altered proof-bound payload."""
        if not _is_proof(self._construction_proof):
            _fail("P5E_DECISION_FACTORY_REQUIRED")
        _tenant(self.tenant_id)
        for name in ("attempt_id", "instruction_id", "document_id", "deputy_id", "service_execution_id"):
            _identity(name, getattr(self, name))
        _sha3(self.source_attempt_fingerprint)
        _sha3(self.evidence_identity)
        _reference(self.evidence_reference)
        _sha3(self.evidence_fingerprint)
        if self.outcome not in {ServiceAttemptState.COMPLETED, ServiceAttemptState.NOT_COMPLETED}:
            _fail("P5E_OUTCOME_INVALID")
        _timestamp("occurred_at", self.occurred_at)
        _timestamp("executed_at", self.executed_at)
        if self.executed_at < self.occurred_at:
            _fail("P5E_CHRONOLOGY_INVALID")
        payload = self.to_dict()
        if _proof_digest(self._construction_proof) != _digest(payload):
            _fail("P5E_SOURCE_BINDING_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Return deterministic canonical terminal-outcome evidence."""
        return _payload(
            tenant_id=self.tenant_id,
            attempt_id=self.attempt_id,
            instruction_id=self.instruction_id,
            document_id=self.document_id,
            deputy_id=self.deputy_id,
            source_attempt_fingerprint=self.source_attempt_fingerprint,
            outcome=self.outcome,
            evidence_identity=self.evidence_identity,
            evidence_reference=self.evidence_reference,
            evidence_fingerprint=self.evidence_fingerprint,
            occurred_at=self.occurred_at,
            service_execution_id=self.service_execution_id,
            executed_at=self.executed_at,
        )

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 over the complete canonical payload."""
        return _digest(self.to_dict())


def authorize_process_service_attempt_outcome(*, current_attempt: ServiceAttempt, outcome: ServiceAttemptState, evidence_reference: str, evidence_fingerprint: str, occurred_at: datetime, service_execution_id: str, executed_at: datetime) -> ProcessServiceAttemptOutcomeDecision:
    """Authorize one evidenced ATTEMPTED -> terminal outcome and execution binding.

    The exact P1 source attempt supplies all legal identities and chronology.
    The caller supplies only an explicitly evidenced terminal outcome, opaque
    evidence, and the P1-approved execution locator/time; no ReturnOfService or
    financial authority is created here.
    """
    if type(current_attempt) is not ServiceAttempt:
        _fail("P5E_SOURCE_ATTEMPT_REQUIRED")
    try:
        current_attempt.__post_init__()
    except Exception as error:
        raise ProcessServiceAttemptOutcomeAuthorityError("P5E_SOURCE_ATTEMPT_INVALID") from error
    if current_attempt.state is not ServiceAttemptState.ATTEMPTED:
        _fail("P5E_SOURCE_STATE_INVALID")
    if outcome not in {ServiceAttemptState.COMPLETED, ServiceAttemptState.NOT_COMPLETED}:
        _fail("P5E_OUTCOME_INVALID")
    reference = _reference(evidence_reference)
    evidence_hash = _sha3(evidence_fingerprint)
    occurred = _timestamp("occurred_at", occurred_at)
    execution_id = _identity("service_execution_id", service_execution_id)
    executed = _timestamp("executed_at", executed_at)
    if occurred < current_attempt.transition_history[-1].occurred_at or executed < occurred:
        _fail("P5E_CHRONOLOGY_INVALID")
    source_fingerprint = current_attempt.fingerprint
    evidence_identity = _digest({
        "schema": SCHEMA,
        "version": VERSION,
        "tenant_id": current_attempt.tenant_id,
        "attempt_id": current_attempt.attempt_id,
        "source_attempt_fingerprint": source_fingerprint,
        "outcome": outcome.value,
        "evidence_reference": reference,
        "evidence_fingerprint": evidence_hash,
        "occurred_at": occurred.isoformat(),
        "service_execution_id": execution_id,
        "executed_at": executed.isoformat(),
    })
    payload = _payload(
        tenant_id=current_attempt.tenant_id,
        attempt_id=current_attempt.attempt_id,
        instruction_id=current_attempt.instruction_id,
        document_id=current_attempt.document_id,
        deputy_id=current_attempt.deputy_id,
        source_attempt_fingerprint=source_fingerprint,
        outcome=outcome,
        evidence_identity=evidence_identity,
        evidence_reference=reference,
        evidence_fingerprint=evidence_hash,
        occurred_at=occurred,
        service_execution_id=execution_id,
        executed_at=executed,
    )
    return ProcessServiceAttemptOutcomeDecision(
        tenant_id=current_attempt.tenant_id,
        attempt_id=current_attempt.attempt_id,
        instruction_id=current_attempt.instruction_id,
        document_id=current_attempt.document_id,
        deputy_id=current_attempt.deputy_id,
        source_attempt_fingerprint=source_fingerprint,
        outcome=outcome,
        evidence_identity=evidence_identity,
        evidence_reference=reference,
        evidence_fingerprint=evidence_hash,
        occurred_at=occurred,
        service_execution_id=execution_id,
        executed_at=executed,
        _construction_proof=_issue_proof(_digest(payload)),
    )


def _parse_timestamp(value: object) -> datetime:
    if not isinstance(value, str):
        _fail("P5E_PERSISTED_PAYLOAD_INVALID")
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise ProcessServiceAttemptOutcomeAuthorityError("P5E_PERSISTED_PAYLOAD_INVALID") from error


def hydrate_process_service_attempt_outcome_decision(payload: object) -> ProcessServiceAttemptOutcomeDecision:
    """Strictly hydrate persisted outcome evidence without granting new authority."""
    if not isinstance(payload, dict):
        _fail("P5E_PERSISTED_PAYLOAD_INVALID")
    required = {"schema", "version", "entity_type", "tenant_id", "attempt_id", "instruction_id", "document_id", "deputy_id", "source_attempt_fingerprint", "outcome", "evidence_identity", "evidence_reference", "evidence_fingerprint", "occurred_at", "service_execution_id", "executed_at"}
    if set(payload) != required or payload.get("schema") != SCHEMA or payload.get("version") != VERSION or payload.get("entity_type") != "ProcessServiceAttemptOutcomeDecision":
        _fail("P5E_PERSISTED_PAYLOAD_INVALID")
    try:
        outcome = ServiceAttemptState(cast(str, payload["outcome"]))
    except (KeyError, ValueError, TypeError) as error:
        raise ProcessServiceAttemptOutcomeAuthorityError("P5E_PERSISTED_PAYLOAD_INVALID") from error
    if outcome not in {ServiceAttemptState.COMPLETED, ServiceAttemptState.NOT_COMPLETED}:
        _fail("P5E_PERSISTED_PAYLOAD_INVALID")
    values = {
        "tenant_id": _tenant(payload["tenant_id"]),
        "attempt_id": _identity("attempt_id", payload["attempt_id"]),
        "instruction_id": _identity("instruction_id", payload["instruction_id"]),
        "document_id": _identity("document_id", payload["document_id"]),
        "deputy_id": _identity("deputy_id", payload["deputy_id"]),
        "source_attempt_fingerprint": _sha3(payload["source_attempt_fingerprint"]),
        "outcome": outcome,
        "evidence_identity": _sha3(payload["evidence_identity"]),
        "evidence_reference": _reference(payload["evidence_reference"]),
        "evidence_fingerprint": _sha3(payload["evidence_fingerprint"]),
        "occurred_at": _timestamp("occurred_at", _parse_timestamp(payload["occurred_at"])),
        "service_execution_id": _identity("service_execution_id", payload["service_execution_id"]),
        "executed_at": _timestamp("executed_at", _parse_timestamp(payload["executed_at"])),
    }
    typed_values = {
        "tenant_id": cast(str, values["tenant_id"]),
        "attempt_id": cast(str, values["attempt_id"]),
        "instruction_id": cast(str, values["instruction_id"]),
        "document_id": cast(str, values["document_id"]),
        "deputy_id": cast(str, values["deputy_id"]),
        "source_attempt_fingerprint": cast(str, values["source_attempt_fingerprint"]),
        "outcome": cast(ServiceAttemptState, values["outcome"]),
        "evidence_identity": cast(str, values["evidence_identity"]),
        "evidence_reference": cast(str, values["evidence_reference"]),
        "evidence_fingerprint": cast(str, values["evidence_fingerprint"]),
        "occurred_at": cast(datetime, values["occurred_at"]),
        "service_execution_id": cast(str, values["service_execution_id"]),
        "executed_at": cast(datetime, values["executed_at"]),
    }
    canonical = _payload(**typed_values)
    return ProcessServiceAttemptOutcomeDecision(_construction_proof=_issue_proof(_digest(canonical)), **typed_values)


__all__ = ["SCHEMA", "VERSION", "ProcessServiceAttemptOutcomeAuthorityError", "ProcessServiceAttemptOutcomeDecision", "authorize_process_service_attempt_outcome", "hydrate_process_service_attempt_outcome_decision"]


# ARTIFACT: process_service_attempt_outcome_authority.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-AUTHORITY
# AUTHORITY BOUNDARY: terminal outcome evidence and execution binding only.
# TENANT POSTURE: all identities derive from one validated tenant-scoped P1 attempt.
# FAIL-CLOSED POSTURE: malformed, stale, terminal, and divergent evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
