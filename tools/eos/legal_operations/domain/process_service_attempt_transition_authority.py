"""Canonical field-attempt evidence authority for the P5 transition slice.

TITLE: Wilsy OS Process-Service Attempt Transition Authority
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-AUTHORITY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Bind one tenant-scoped, evidence-backed ALLOCATED -> ATTEMPTED
         transition to an already validated P1 ServiceAttempt without creating
         service-completion, execution, return, billing, or settlement truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/process_service_attempt_transition_authority.py
COLLABORATION / OWNERSHIP: P5 field-attempt authority only. P1 owns lifecycle
                            semantics; P2 owns immutable lifecycle persistence;
                            callers own sessions and transactions.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-AUTHORITY
           establishes fail-closed field evidence for exactly ALLOCATED to
           ATTEMPTED while preserving ATTEMPT != SERVICE.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque tenant, identity, and evidence references;
                             raw GPS, photographs, signatures, and provider
                             payloads are never treated as legal truth.
TENANT BOUNDARY: Tenant and all P1 identities are derived from the exact
                 validated source attempt; pseudo/global tenants reject.
AUTHORITY BOUNDARY: Evidence authorization only. This module does not persist,
                    transition, execute service, generate returns, or authorize
                    custody, IAM, transport, billing, payment, or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
FAIL-CLOSED DECLARATION: Exact P1 runtime type, ALLOCATED state, chronology,
                         evidence reference/fingerprint, and private payload
                         proof are mandatory.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import json
import re
from typing import Callable, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ServiceAttempt,
    ServiceAttemptState,
)


VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-AUTHORITY"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-ATTEMPT-TRANSITION-AUTHORITY/V1"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})


class ProcessServiceAttemptTransitionAuthorityError(ValueError):
    """Stable fail-closed P5 field-attempt evidence error."""

    def __init__(self, code: str) -> None:
        """Create an error carrying only its governed code."""
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    """Raise one deterministic authority failure."""
    raise ProcessServiceAttemptTransitionAuthorityError(code)


def _identity(name: str, value: object) -> str:
    """Require one canonical opaque identity."""
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"P5D_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require an explicit non-pseudo tenant."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("P5D_TENANT_INVALID")
    return tenant


def _timestamp(name: str, value: object) -> datetime:
    """Require an aware UTC datetime."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timedelta(0):
        _fail(f"P5D_{name.upper()}_INVALID")
    return value


def _reference(value: object) -> str:
    """Require a non-empty opaque evidence reference."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail("P5D_EVIDENCE_REFERENCE_INVALID")
    return value


def _fingerprint(value: object) -> str:
    """Require a lowercase SHA3-512 evidence fingerprint."""
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail("P5D_EVIDENCE_FINGERPRINT_INVALID")
    return value


def _digest(payload: object) -> str:
    """Hash deterministic canonical JSON using lowercase SHA3-512."""
    encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _proof_contract() -> tuple[Callable[[str], object], Callable[[object], bool], Callable[[object], str | None]]:
    """Create a closure-bound payload proof that callers cannot manufacture."""
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


def _payload(
    *, tenant_id: str, attempt_id: str, instruction_id: str, document_id: str,
    deputy_id: str, source_attempt_fingerprint: str, evidence_identity: str,
    evidence_reference: str, evidence_fingerprint: str, occurred_at: datetime,
) -> dict[str, object]:
    """Build the complete immutable semantic decision payload."""
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "entity_type": "ProcessServiceAttemptTransitionDecision",
        "tenant_id": tenant_id,
        "attempt_id": attempt_id,
        "instruction_id": instruction_id,
        "document_id": document_id,
        "deputy_id": deputy_id,
        "source_attempt_fingerprint": source_attempt_fingerprint,
        "evidence_identity": evidence_identity,
        "evidence_reference": evidence_reference,
        "evidence_fingerprint": evidence_fingerprint,
        "occurred_at": occurred_at.isoformat(),
        "from_state": ServiceAttemptState.ALLOCATED.value,
        "to_state": ServiceAttemptState.ATTEMPTED.value,
    }


@dataclass(frozen=True, slots=True)
class ProcessServiceAttemptTransitionDecision:
    """Immutable evidence binding for exactly one ALLOCATED -> ATTEMPTED fact.

    The decision derives every P1 identity from a validated source attempt and
    carries only opaque evidence references/fingerprints. It does not itself
    mutate P1/P2, create ServiceExecution or ReturnOfService, or own a Mongo
    session/transaction. Direct construction is rejected without the private
    payload-bound proof issued by :func:`authorize_process_service_attempt_transition`.
    """

    tenant_id: str
    attempt_id: str
    instruction_id: str
    document_id: str
    deputy_id: str
    source_attempt_fingerprint: str
    evidence_identity: str
    evidence_reference: str
    evidence_fingerprint: str
    occurred_at: datetime
    _construction_proof: object = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Reject malformed or proof-divergent immutable evidence."""
        if not _is_proof(self._construction_proof):
            _fail("P5D_DECISION_FACTORY_REQUIRED")
        _tenant(self.tenant_id)
        for name in ("attempt_id", "instruction_id", "document_id", "deputy_id"):
            _identity(name, getattr(self, name))
        _fingerprint(self.source_attempt_fingerprint)
        _fingerprint(self.evidence_identity)
        _reference(self.evidence_reference)
        _fingerprint(self.evidence_fingerprint)
        _timestamp("occurred_at", self.occurred_at)
        payload = _payload(
            tenant_id=self.tenant_id,
            attempt_id=self.attempt_id,
            instruction_id=self.instruction_id,
            document_id=self.document_id,
            deputy_id=self.deputy_id,
            source_attempt_fingerprint=self.source_attempt_fingerprint,
            evidence_identity=self.evidence_identity,
            evidence_reference=self.evidence_reference,
            evidence_fingerprint=self.evidence_fingerprint,
            occurred_at=self.occurred_at,
        )
        if _proof_digest(self._construction_proof) != _digest(payload):
            _fail("P5D_DECISION_SOURCE_BINDING_INVALID")

    def to_dict(self) -> dict[str, object]:
        """Return deterministic canonical field-attempt evidence."""
        return _payload(
            tenant_id=self.tenant_id,
            attempt_id=self.attempt_id,
            instruction_id=self.instruction_id,
            document_id=self.document_id,
            deputy_id=self.deputy_id,
            source_attempt_fingerprint=self.source_attempt_fingerprint,
            evidence_identity=self.evidence_identity,
            evidence_reference=self.evidence_reference,
            evidence_fingerprint=self.evidence_fingerprint,
            occurred_at=self.occurred_at,
        )

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 over the complete canonical payload."""
        return _digest(self.to_dict())


def authorize_process_service_attempt_transition(
    *, current_attempt: ServiceAttempt, evidence_reference: str,
    evidence_fingerprint: str, occurred_at: datetime,
) -> ProcessServiceAttemptTransitionDecision:
    """Authorize one evidence-backed ALLOCATED -> ATTEMPTED transition.

    The exact P1 runtime type and its own validation are replayed before any
    field is derived. Only the source attempt supplies tenant, attempt,
    instruction, document, and deputy identity. The caller supplies opaque
    evidence reference/fingerprint and an aware UTC occurrence time; no raw
    mobile/provider payload is accepted as legal truth.
    """
    if type(current_attempt) is not ServiceAttempt:
        _fail("P5D_SOURCE_ATTEMPT_REQUIRED")
    try:
        current_attempt.__post_init__()
    except Exception as error:
        raise ProcessServiceAttemptTransitionAuthorityError("P5D_SOURCE_ATTEMPT_INVALID") from error
    if current_attempt.state is not ServiceAttemptState.ALLOCATED:
        _fail("P5D_SOURCE_STATE_INVALID")
    reference = _reference(evidence_reference)
    evidence_hash = _fingerprint(evidence_fingerprint)
    occurred = _timestamp("occurred_at", occurred_at)
    if occurred < current_attempt.allocated_at:
        _fail("P5D_CHRONOLOGY_INVALID")
    source_fingerprint = current_attempt.fingerprint
    evidence_identity = _digest({
        "schema": SCHEMA,
        "version": VERSION,
        "tenant_id": current_attempt.tenant_id,
        "attempt_id": current_attempt.attempt_id,
        "source_attempt_fingerprint": source_fingerprint,
        "evidence_reference": reference,
        "evidence_fingerprint": evidence_hash,
        "occurred_at": occurred.isoformat(),
        "from_state": ServiceAttemptState.ALLOCATED.value,
        "to_state": ServiceAttemptState.ATTEMPTED.value,
    })
    payload = _payload(
        tenant_id=current_attempt.tenant_id,
        attempt_id=current_attempt.attempt_id,
        instruction_id=current_attempt.instruction_id,
        document_id=current_attempt.document_id,
        deputy_id=current_attempt.deputy_id,
        source_attempt_fingerprint=source_fingerprint,
        evidence_identity=evidence_identity,
        evidence_reference=reference,
        evidence_fingerprint=evidence_hash,
        occurred_at=occurred,
    )
    return ProcessServiceAttemptTransitionDecision(
        tenant_id=current_attempt.tenant_id,
        attempt_id=current_attempt.attempt_id,
        instruction_id=current_attempt.instruction_id,
        document_id=current_attempt.document_id,
        deputy_id=current_attempt.deputy_id,
        source_attempt_fingerprint=source_fingerprint,
        evidence_identity=evidence_identity,
        evidence_reference=reference,
        evidence_fingerprint=evidence_hash,
        occurred_at=occurred,
        _construction_proof=_issue_proof(_digest(payload)),
    )


def hydrate_process_service_attempt_transition_decision(payload: object) -> ProcessServiceAttemptTransitionDecision:
    """Strictly hydrate one persisted P5D decision payload without new authority."""
    if not isinstance(payload, dict):
        _fail("P5D_PERSISTED_PAYLOAD_INVALID")
    required = set(ProcessServiceAttemptTransitionDecision.__dataclass_fields__) - {"_construction_proof"}
    if set(payload) != {"schema", "version", "entity_type", "tenant_id", "attempt_id", "instruction_id", "document_id", "deputy_id", "source_attempt_fingerprint", "evidence_identity", "evidence_reference", "evidence_fingerprint", "occurred_at", "from_state", "to_state"}:
        _fail("P5D_PERSISTED_PAYLOAD_INVALID")
    if payload.get("schema") != SCHEMA or payload.get("version") != VERSION or payload.get("entity_type") != "ProcessServiceAttemptTransitionDecision":
        _fail("P5D_PERSISTED_PAYLOAD_INVALID")
    occurred = _timestamp("occurred_at", _parse_timestamp(payload.get("occurred_at")))
    values = {key: payload[key] for key in payload if key not in {"schema", "version", "entity_type", "from_state", "to_state"}}
    values["occurred_at"] = occurred
    try:
        for key in ("tenant_id", "attempt_id", "instruction_id", "document_id", "deputy_id"):
            _identity(key, values[key])
        _tenant(values["tenant_id"])
        _fingerprint(values["source_attempt_fingerprint"])
        _fingerprint(values["evidence_identity"])
        _reference(values["evidence_reference"])
        _fingerprint(values["evidence_fingerprint"])
    except ProcessServiceAttemptTransitionAuthorityError:
        raise
    typed_values = {
        "tenant_id": cast(str, values["tenant_id"]),
        "attempt_id": cast(str, values["attempt_id"]),
        "instruction_id": cast(str, values["instruction_id"]),
        "document_id": cast(str, values["document_id"]),
        "deputy_id": cast(str, values["deputy_id"]),
        "source_attempt_fingerprint": cast(str, values["source_attempt_fingerprint"]),
        "evidence_identity": cast(str, values["evidence_identity"]),
        "evidence_reference": cast(str, values["evidence_reference"]),
        "evidence_fingerprint": cast(str, values["evidence_fingerprint"]),
        "occurred_at": cast(datetime, values["occurred_at"]),
    }
    canonical = _payload(**typed_values)
    proof = _issue_proof(_digest(canonical))
    return ProcessServiceAttemptTransitionDecision(_construction_proof=proof, **typed_values)


def _parse_timestamp(value: object) -> datetime:
    """Parse one persisted ISO-8601 timestamp."""
    if not isinstance(value, str):
        _fail("P5D_PERSISTED_PAYLOAD_INVALID")
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise ProcessServiceAttemptTransitionAuthorityError("P5D_PERSISTED_PAYLOAD_INVALID") from error


__all__ = [
    "SCHEMA",
    "VERSION",
    "ProcessServiceAttemptTransitionAuthorityError",
    "ProcessServiceAttemptTransitionDecision",
    "authorize_process_service_attempt_transition",
    "hydrate_process_service_attempt_transition_decision",
]


# ARTIFACT: process_service_attempt_transition_authority.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-TRANSITION-AUTHORITY
# AUTHORITY BOUNDARY: immutable evidence for ALLOCATED -> ATTEMPTED only.
# TENANT POSTURE: all identities derive from one validated tenant-scoped P1 attempt.
# FAIL-CLOSED POSTURE: malformed, mismatched, stale, terminal, or divergent evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
