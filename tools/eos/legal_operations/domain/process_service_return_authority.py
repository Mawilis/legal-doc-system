"""Evidence authority for generating ReturnOfService from ServiceExecution.

TITLE: Wilsy OS Process-Service Return Authority
VERSION: v1.0.0-PROCESS-SERVICE-RETURN-AUTHORITY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Bind one immutable return identity and generation timestamp to an
         exact validated P1 ServiceExecution without deriving financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/process_service_return_authority.py
COLLABORATION / OWNERSHIP: P5 return authority only; P1 owns ReturnOfService
                            factory semantics, P2 owns persistence, callers own
                            sessions and transactions.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-RETURN-AUTHORITY establishes
           fail-closed return-generation provenance from canonical execution.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Tenant, attempt, instruction, document, and outcome derive
                 exclusively from exact P1 ServiceExecution.
AUTHORITY BOUNDARY: Return-generation evidence only; no invoice, payment,
                    settlement, or financial execution authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Exact P1 type, validated execution, return identity,
                         chronology, and private payload proof are mandatory.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import json
import re
from typing import Callable, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceExecution, ServiceExecutionOutcome

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-RETURN-AUTHORITY"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-RETURN-AUTHORITY/V1"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})


class ProcessServiceReturnAuthorityError(ValueError):
    """Stable fail-closed return-generation authority error."""

    def __init__(self, code: str) -> None:
        """Create one governed error."""
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise ProcessServiceReturnAuthorityError(code)


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"P5F_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("P5F_TENANT_INVALID")
    return tenant


def _timestamp(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        _fail(f"P5F_{name.upper()}_INVALID")
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


def _payload(*, tenant_id: str, service_execution_id: str, attempt_id: str, instruction_id: str, document_id: str, outcome: ServiceExecutionOutcome, source_execution_fingerprint: str, return_id: str, generated_at: datetime, evidence_identity: str) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "entity_type": "ProcessServiceReturnDecision",
        "tenant_id": tenant_id,
        "service_execution_id": service_execution_id,
        "attempt_id": attempt_id,
        "instruction_id": instruction_id,
        "document_id": document_id,
        "outcome": outcome.value,
        "source_execution_fingerprint": source_execution_fingerprint,
        "return_id": return_id,
        "generated_at": generated_at.isoformat(),
        "evidence_identity": evidence_identity,
    }


@dataclass(frozen=True, slots=True)
class ProcessServiceReturnDecision:
    """Immutable return-generation authority derived from one execution."""

    tenant_id: str
    service_execution_id: str
    attempt_id: str
    instruction_id: str
    document_id: str
    outcome: ServiceExecutionOutcome
    source_execution_fingerprint: str
    return_id: str
    generated_at: datetime
    evidence_identity: str
    _construction_proof: object = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Reject direct construction or altered payload proofs."""
        if not _is_proof(self._construction_proof):
            _fail("P5F_DECISION_FACTORY_REQUIRED")
        _tenant(self.tenant_id)
        for name in ("service_execution_id", "attempt_id", "instruction_id", "document_id", "return_id"):
            _identity(name, getattr(self, name))
        if not isinstance(self.outcome, ServiceExecutionOutcome):
            _fail("P5F_OUTCOME_INVALID")
        if not isinstance(self.source_execution_fingerprint, str) or _SHA3.fullmatch(self.source_execution_fingerprint) is None:
            _fail("P5F_SOURCE_FINGERPRINT_INVALID")
        _timestamp("generated_at", self.generated_at)
        if not isinstance(self.evidence_identity, str) or _SHA3.fullmatch(self.evidence_identity) is None:
            _fail("P5F_EVIDENCE_IDENTITY_INVALID")
        if _proof_digest(self._construction_proof) != _digest(self.to_dict()):
            _fail("P5F_SOURCE_BINDING_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Return deterministic canonical return authority evidence."""
        return _payload(tenant_id=self.tenant_id, service_execution_id=self.service_execution_id, attempt_id=self.attempt_id, instruction_id=self.instruction_id, document_id=self.document_id, outcome=self.outcome, source_execution_fingerprint=self.source_execution_fingerprint, return_id=self.return_id, generated_at=self.generated_at, evidence_identity=self.evidence_identity)

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 over the canonical authority payload."""
        return _digest(self.to_dict())


def authorize_process_service_return(*, service_execution: ServiceExecution, return_id: str, generated_at: datetime) -> ProcessServiceReturnDecision:
    """Authorize one return from exact validated P1 ServiceExecution.

    Tenant, attempt, instruction, document, outcome, and source evidence are
    derived from the execution. The caller can provide only return identity and
    generation time; P1 remains the sole ReturnOfService factory.
    """
    if type(service_execution) is not ServiceExecution:
        _fail("P5F_SOURCE_EXECUTION_REQUIRED")
    try:
        service_execution._validate()
    except Exception as error:
        raise ProcessServiceReturnAuthorityError("P5F_SOURCE_EXECUTION_INVALID") from error
    result_id = _identity("return_id", return_id)
    generated = _timestamp("generated_at", generated_at)
    source_fingerprint = service_execution.fingerprint
    evidence_identity = _digest({"schema": SCHEMA, "version": VERSION, "tenant_id": service_execution.tenant_id, "service_execution_id": service_execution.service_execution_id, "source_execution_fingerprint": source_fingerprint, "return_id": result_id, "generated_at": generated.isoformat()})
    payload = _payload(tenant_id=service_execution.tenant_id, service_execution_id=service_execution.service_execution_id, attempt_id=service_execution.attempt_id, instruction_id=service_execution.instruction_id, document_id=service_execution.document_id, outcome=service_execution.outcome, source_execution_fingerprint=source_fingerprint, return_id=result_id, generated_at=generated, evidence_identity=evidence_identity)
    return ProcessServiceReturnDecision(tenant_id=service_execution.tenant_id, service_execution_id=service_execution.service_execution_id, attempt_id=service_execution.attempt_id, instruction_id=service_execution.instruction_id, document_id=service_execution.document_id, outcome=service_execution.outcome, source_execution_fingerprint=source_fingerprint, return_id=result_id, generated_at=generated, evidence_identity=evidence_identity, _construction_proof=_issue_proof(_digest(payload)))


def _parse_timestamp(value: object) -> datetime:
    if not isinstance(value, str):
        _fail("P5F_PERSISTED_PAYLOAD_INVALID")
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise ProcessServiceReturnAuthorityError("P5F_PERSISTED_PAYLOAD_INVALID") from error


def hydrate_process_service_return_decision(payload: object) -> ProcessServiceReturnDecision:
    """Strictly hydrate persisted return authority evidence."""
    required = {"schema", "version", "entity_type", "tenant_id", "service_execution_id", "attempt_id", "instruction_id", "document_id", "outcome", "source_execution_fingerprint", "return_id", "generated_at", "evidence_identity"}
    if not isinstance(payload, dict) or set(payload) != required or payload.get("schema") != SCHEMA or payload.get("version") != VERSION or payload.get("entity_type") != "ProcessServiceReturnDecision":
        _fail("P5F_PERSISTED_PAYLOAD_INVALID")
    try:
        tenant_id = _tenant(payload["tenant_id"])
        service_execution_id = _identity("service_execution_id", payload["service_execution_id"])
        attempt_id = _identity("attempt_id", payload["attempt_id"])
        instruction_id = _identity("instruction_id", payload["instruction_id"])
        document_id = _identity("document_id", payload["document_id"])
        outcome = ServiceExecutionOutcome(cast(str, payload["outcome"]))
        source_execution_fingerprint = cast(str, payload["source_execution_fingerprint"])
        return_id = _identity("return_id", payload["return_id"])
        generated_at = _timestamp("generated_at", _parse_timestamp(payload["generated_at"]))
        evidence_identity = cast(str, payload["evidence_identity"])
    except (KeyError, ValueError, TypeError) as error:
        raise ProcessServiceReturnAuthorityError("P5F_PERSISTED_PAYLOAD_INVALID") from error
    canonical = _payload(
        tenant_id=tenant_id,
        service_execution_id=service_execution_id,
        attempt_id=attempt_id,
        instruction_id=instruction_id,
        document_id=document_id,
        outcome=outcome,
        source_execution_fingerprint=source_execution_fingerprint,
        return_id=return_id,
        generated_at=generated_at,
        evidence_identity=evidence_identity,
    )
    return ProcessServiceReturnDecision(
        tenant_id=tenant_id,
        service_execution_id=service_execution_id,
        attempt_id=attempt_id,
        instruction_id=instruction_id,
        document_id=document_id,
        outcome=outcome,
        source_execution_fingerprint=source_execution_fingerprint,
        return_id=return_id,
        generated_at=generated_at,
        evidence_identity=evidence_identity,
        _construction_proof=_issue_proof(_digest(canonical)),
    )


__all__ = ["SCHEMA", "VERSION", "ProcessServiceReturnAuthorityError", "ProcessServiceReturnDecision", "authorize_process_service_return", "hydrate_process_service_return_decision"]


# ARTIFACT: process_service_return_authority.py
# VERSION: v1.0.0-PROCESS-SERVICE-RETURN-AUTHORITY
# AUTHORITY BOUNDARY: return-generation evidence from canonical execution only.
# TENANT POSTURE: all identities derive from one validated ServiceExecution.
# FAIL-CLOSED POSTURE: malformed, divergent, and chronologically invalid evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
