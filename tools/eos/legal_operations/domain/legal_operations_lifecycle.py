"""Canonical, provider-neutral Legal Operations lifecycle evidence.

TITLE: Wilsy OS Legal Operations Lifecycle Contract
VERSION: v1.0.0-LEGAL-OPERATIONS-LIFECYCLE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable tenant-scoped legal-operations identities, monotonic
         lifecycle snapshots, and custody/service evidence without transport,
         persistence, billing, payment, or settlement authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_operations_lifecycle.py
COLLABORATION / OWNERSHIP: Python Legal Operations domain authority; callers
                            provide explicit evidence and own persistence and
                            transaction boundaries in later bounded gates.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: 2026-09-13 v1.0.0-LEGAL-OPERATIONS-LIFECYCLE establishes immutable
           LegalInstruction, CaseMatter, ProcessDocument, District,
           SheriffOffice, Deputy, DocumentCustodyEvent, ServiceAttempt,
           ServiceExecution, and ReturnOfService contracts with strict
           identity, timestamp, evidence, and monotonic-transition validation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped opaque references only; no raw
                             provider payloads, credentials, or PII expansion.
TENANT BOUNDARY: Every operational entity carries an explicit non-default
                 tenant_id; cross-tenant inference is rejected.
AUTHORITY BOUNDARY: This module owns legal-operations lifecycle facts and
                    evidence shape only; it does not authorize service,
                    transport, billing, payment, or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; legal-service evidence never
                              creates invoice or payment truth.
FAIL-CLOSED DECLARATION: Invalid identities, timestamps, evidence, transitions,
                         chronology, and custody chains raise governed errors.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, fields, replace
from datetime import datetime
from enum import StrEnum
from typing import Any, Final, Iterable, Mapping, TypeVar, cast


VERSION: Final[str] = "v1.0.0-LEGAL-OPERATIONS-LIFECYCLE"
SCHEMA: Final[str] = "WILSY-LEGAL-OPERATIONS-LIFECYCLE/V1"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})
_T = TypeVar("_T")


class LegalOperationsLifecycleError(ValueError):
    """Fail-closed validation, chronology, custody, or transition error."""


class LegalInstructionState(StrEnum):
    """Monotonic instruction states; none represents service or payment."""

    REGISTERED = "REGISTERED"
    ACCEPTED = "ACCEPTED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class CaseMatterState(StrEnum):
    """Case/matter lifecycle states."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"


class ProcessDocumentState(StrEnum):
    """Explicit document lifecycle snapshots; custody remains event evidence."""

    REGISTERED = "REGISTERED"
    RECEIVED = "RECEIVED"
    ALLOCATED_TO_DEPUTY = "ALLOCATED_TO_DEPUTY"
    RETURNED_TO_CLIENT = "RETURNED_TO_CLIENT"


class DocumentCustodyEventType(StrEnum):
    """Append-only custody facts; no field here is a mutable current location."""

    REGISTERED = "REGISTERED"
    RECEIVED_IN_OFFICE = "RECEIVED_IN_OFFICE"
    ALLOCATED_TO_DEPUTY = "ALLOCATED_TO_DEPUTY"
    TRANSFERRED = "TRANSFERRED"
    RETURNED_TO_CLIENT = "RETURNED_TO_CLIENT"


class ServiceAttemptState(StrEnum):
    """Attempt states kept distinct from certified service outcomes."""

    ALLOCATED = "ALLOCATED"
    ATTEMPTED = "ATTEMPTED"
    COMPLETED = "COMPLETED"
    NOT_COMPLETED = "NOT_COMPLETED"
    CANCELLED = "CANCELLED"


class ServiceExecutionOutcome(StrEnum):
    """Explicit certified service/non-service conclusions."""

    COMPLETED = "COMPLETED"
    NOT_COMPLETED = "NOT_COMPLETED"


class ReturnOfServiceState(StrEnum):
    """Return-of-service lifecycle; generation is separate from invoicing."""

    GENERATED = "GENERATED"


@dataclass(frozen=True, slots=True)
class LifecycleTransitionEvidence:
    """One immutable, ordered lifecycle transition-evidence record."""

    prior_state: StrEnum
    resulting_state: StrEnum
    occurred_at: datetime
    evidence_reference: str
    evidence_fingerprint: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.prior_state, StrEnum) or not isinstance(self.resulting_state, StrEnum):
            raise LegalOperationsLifecycleError("transition states are invalid")
        if type(self.prior_state) is not type(self.resulting_state):
            raise LegalOperationsLifecycleError("transition states must share one lifecycle vocabulary")
        if self.prior_state is self.resulting_state:
            raise LegalOperationsLifecycleError("transition must change lifecycle state")
        _timestamp("occurred_at", self.occurred_at)
        _text("evidence_reference", self.evidence_reference)
        if self.evidence_fingerprint is not None and re.fullmatch(r"[0-9a-f]{128}", self.evidence_fingerprint) is None:
            raise LegalOperationsLifecycleError("evidence_fingerprint must be lowercase SHA3-512 hex")


def _validate_transition_history(
    *,
    initial_state: StrEnum,
    current_state: StrEnum,
    history: tuple[LifecycleTransitionEvidence, ...],
    allowed: Mapping[StrEnum, frozenset[StrEnum]],
    baseline: datetime,
    terminal_states_require_fingerprint: frozenset[StrEnum] = frozenset(),
) -> None:
    """Validate a complete contiguous history from its canonical initial state."""
    if not isinstance(history, tuple):
        raise LegalOperationsLifecycleError("transition history must be an immutable tuple")
    _timestamp("baseline", baseline)
    state: StrEnum = initial_state
    previous_at = baseline
    for event in history:
        if not isinstance(event, LifecycleTransitionEvidence):
            raise LegalOperationsLifecycleError("transition history contains invalid evidence")
        if event.prior_state is not state:
            raise LegalOperationsLifecycleError("transition history contains a state gap or reversal")
        if event.resulting_state not in allowed.get(state, frozenset()):
            raise LegalOperationsLifecycleError("transition history contains an illegal transition")
        if event.occurred_at < previous_at:
            raise LegalOperationsLifecycleError("transition history chronology is invalid")
        if event.resulting_state in terminal_states_require_fingerprint and event.evidence_fingerprint is None:
            raise LegalOperationsLifecycleError("terminal transition evidence fingerprint is required")
        state = event.resulting_state
        previous_at = event.occurred_at
    if state is not current_state:
        raise LegalOperationsLifecycleError("current state does not match complete transition history")


def _identity(name: str, value: object) -> str:
    """Validate one canonical opaque identity without inventing defaults."""
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        raise LegalOperationsLifecycleError(f"{name} must be a canonical non-empty identity")
    return value


def _tenant(value: object) -> str:
    """Validate explicit tenant scope and reject pseudo/global tenants."""
    tenant_id = _identity("tenant_id", value)
    if tenant_id.casefold() in _FORBIDDEN_TENANTS:
        raise LegalOperationsLifecycleError("tenant_id may not be a pseudo or global tenant")
    return tenant_id


def _text(name: str, value: object) -> str:
    """Validate a required human/reference string without trimming semantics."""
    if not isinstance(value, str) or value != value.strip() or not value:
        raise LegalOperationsLifecycleError(f"{name} must be non-empty text")
    if unicodedata.normalize("NFC", value) != value:
        raise LegalOperationsLifecycleError(f"{name} must be NFC-normalized")
    return value


def _optional_text(name: str, value: object) -> None:
    """Validate an optional opaque reference when supplied."""
    if value is not None:
        _text(name, value)


def _timestamp(name: str, value: object) -> datetime:
    """Require an aware timestamp with an unambiguous UTC offset."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise LegalOperationsLifecycleError(f"{name} must be timezone-aware")
    return value


def _positive_int(name: str, value: object) -> int:
    """Require a genuine positive integer, excluding bool."""
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise LegalOperationsLifecycleError(f"{name} must be a positive integer")
    return value


def _canonical_value(value: object) -> object:
    """Convert immutable domain values into deterministic JSON-safe values."""
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_canonical_value(item) for item in value]
    if isinstance(value, list):
        return [_canonical_value(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _canonical_value(item) for key, item in value.items()}
    if isinstance(value, LifecycleTransitionEvidence):
        return {
            "prior_state": _canonical_value(value.prior_state),
            "resulting_state": _canonical_value(value.resulting_state),
            "occurred_at": _canonical_value(value.occurred_at),
            "evidence_reference": value.evidence_reference,
            "evidence_fingerprint": value.evidence_fingerprint,
        }
    return value


class _EvidenceMixin:
    """Shared deterministic serialization and SHA3-512 evidence behavior."""

    def to_dict(self) -> dict[str, object]:
        """Return the complete authority-bearing lifecycle snapshot."""
        payload: dict[str, object] = {
            "schema": SCHEMA,
            "version": VERSION,
            "entity_type": type(self).__name__,
        }
        payload.update(
            {
                field.name: _canonical_value(getattr(self, field.name))
                for field in fields(cast(Any, self))
                if not field.name.startswith("_")
            }
        )
        return payload

    @property
    def fingerprint(self) -> str:
        """Return the deterministic lowercase SHA3-512 lifecycle fingerprint."""
        canonical = json.dumps(
            self.to_dict(), ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return hashlib.sha3_512(canonical).hexdigest()


def _transition(
    current: _T,
    target: StrEnum,
    allowed: Mapping[StrEnum, frozenset[StrEnum]],
    *,
    evidence_reference: str | None,
    evidence_fingerprint: str | None = None,
    occurred_at: datetime | None,
    baseline: datetime,
    state_field: str = "state",
) -> _T:
    """Apply one explicit monotonic transition with evidence and chronology."""
    if not isinstance(target, type(getattr(current, state_field))):
        raise LegalOperationsLifecycleError("target lifecycle state is invalid")
    current_state = getattr(current, state_field)
    if target is current_state:
        raise LegalOperationsLifecycleError("transition must advance to a distinct state")
    if target not in allowed.get(current_state, frozenset()):
        raise LegalOperationsLifecycleError("illegal non-monotonic lifecycle transition")
    if evidence_reference is None:
        raise LegalOperationsLifecycleError("lifecycle transition evidence is required")
    _text("evidence_reference", evidence_reference)
    if isinstance(current_state, ServiceAttemptState) and target in {
        ServiceAttemptState.COMPLETED,
        ServiceAttemptState.NOT_COMPLETED,
    }:
        if evidence_fingerprint is None or re.fullmatch(r"[0-9a-f]{128}", evidence_fingerprint) is None:
            raise LegalOperationsLifecycleError("terminal transition evidence fingerprint is required")
    if occurred_at is None:
        raise LegalOperationsLifecycleError("lifecycle transition timestamp is required")
    transition_at = _timestamp("occurred_at", occurred_at)
    current_history = getattr(current, "transition_history", ())
    event = LifecycleTransitionEvidence(
        prior_state=current_state,
        resulting_state=target,
        occurred_at=transition_at,
        evidence_reference=evidence_reference,
        evidence_fingerprint=evidence_fingerprint,
    )
    updates: dict[str, object] = {
        state_field: target,
        "transition_history": (*current_history, event),
    }
    return cast(_T, replace(
        cast(Any, current),
        **updates,
    ))


@dataclass(frozen=True, slots=True)
class LegalInstruction(_EvidenceMixin):
    """Immutable tenant instruction registration, distinct from service."""

    tenant_id: str
    instruction_id: str
    case_matter_id: str
    document_id: str
    registered_at: datetime
    evidence_reference: str
    state: LegalInstructionState = LegalInstructionState.REGISTERED
    transition_history: tuple[LifecycleTransitionEvidence, ...] = ()

    def __post_init__(self) -> None:
        _tenant(self.tenant_id)
        for name in ("instruction_id", "case_matter_id", "document_id"):
            _identity(name, getattr(self, name))
        _timestamp("registered_at", self.registered_at)
        _text("evidence_reference", self.evidence_reference)
        if not isinstance(self.state, LegalInstructionState):
            raise LegalOperationsLifecycleError("instruction state is invalid")
        _validate_transition_history(
            initial_state=LegalInstructionState.REGISTERED,
            current_state=self.state,
            history=self.transition_history,
            allowed={
                LegalInstructionState.REGISTERED: frozenset({LegalInstructionState.ACCEPTED, LegalInstructionState.CANCELLED}),
                LegalInstructionState.ACCEPTED: frozenset({LegalInstructionState.CLOSED, LegalInstructionState.CANCELLED}),
            },
            baseline=self.registered_at,
        )

    def transition_to(self, state: LegalInstructionState, *, evidence_reference: str, occurred_at: datetime) -> "LegalInstruction":
        """Return a new explicitly evidenced monotonic instruction snapshot."""
        return _transition(
            self,
            state,
            {
                LegalInstructionState.REGISTERED: frozenset({LegalInstructionState.ACCEPTED, LegalInstructionState.CANCELLED}),
                LegalInstructionState.ACCEPTED: frozenset({LegalInstructionState.CLOSED, LegalInstructionState.CANCELLED}),
            },
            evidence_reference=evidence_reference,
            occurred_at=occurred_at,
            baseline=self.registered_at,
        )


@dataclass(frozen=True, slots=True)
class CaseMatter(_EvidenceMixin):
    """Immutable tenant matter identity with explicit open/close evidence."""

    tenant_id: str
    case_matter_id: str
    matter_reference: str
    opened_at: datetime
    evidence_reference: str
    state: CaseMatterState = CaseMatterState.OPEN
    transition_history: tuple[LifecycleTransitionEvidence, ...] = ()

    def __post_init__(self) -> None:
        _tenant(self.tenant_id)
        _identity("case_matter_id", self.case_matter_id)
        _text("matter_reference", self.matter_reference)
        _timestamp("opened_at", self.opened_at)
        _text("evidence_reference", self.evidence_reference)
        if not isinstance(self.state, CaseMatterState):
            raise LegalOperationsLifecycleError("case state is invalid")
        _validate_transition_history(
            initial_state=CaseMatterState.OPEN,
            current_state=self.state,
            history=self.transition_history,
            allowed={CaseMatterState.OPEN: frozenset({CaseMatterState.CLOSED})},
            baseline=self.opened_at,
        )

    def transition_to(self, state: CaseMatterState, *, evidence_reference: str, occurred_at: datetime) -> "CaseMatter":
        """Close an open matter once with explicit evidence; reopening is forbidden."""
        return _transition(
            self,
            state,
            {CaseMatterState.OPEN: frozenset({CaseMatterState.CLOSED})},
            evidence_reference=evidence_reference,
            occurred_at=occurred_at,
            baseline=self.opened_at,
        )


@dataclass(frozen=True, slots=True)
class ProcessDocument(_EvidenceMixin):
    """Immutable process-document lifecycle snapshot; custody is event evidence."""

    tenant_id: str
    document_id: str
    case_matter_id: str
    document_type: str
    registered_at: datetime
    registration_evidence_reference: str
    state: ProcessDocumentState = ProcessDocumentState.REGISTERED
    transition_history: tuple[LifecycleTransitionEvidence, ...] = ()

    def __post_init__(self) -> None:
        _tenant(self.tenant_id)
        for name in ("document_id", "case_matter_id"):
            _identity(name, getattr(self, name))
        _text("document_type", self.document_type)
        _timestamp("registered_at", self.registered_at)
        _text("registration_evidence_reference", self.registration_evidence_reference)
        if not isinstance(self.state, ProcessDocumentState):
            raise LegalOperationsLifecycleError("document state is invalid")
        _validate_transition_history(
            initial_state=ProcessDocumentState.REGISTERED,
            current_state=self.state,
            history=self.transition_history,
            allowed={
                ProcessDocumentState.REGISTERED: frozenset({ProcessDocumentState.RECEIVED}),
                ProcessDocumentState.RECEIVED: frozenset({ProcessDocumentState.ALLOCATED_TO_DEPUTY}),
                ProcessDocumentState.ALLOCATED_TO_DEPUTY: frozenset({ProcessDocumentState.RETURNED_TO_CLIENT}),
            },
            baseline=self.registered_at,
        )

    def transition_to(self, state: ProcessDocumentState, *, evidence_reference: str, occurred_at: datetime) -> "ProcessDocument":
        """Advance registration/receipt/allocation/return only with evidence."""
        return _transition(
            self,
            state,
            {
                ProcessDocumentState.REGISTERED: frozenset({ProcessDocumentState.RECEIVED}),
                ProcessDocumentState.RECEIVED: frozenset({ProcessDocumentState.ALLOCATED_TO_DEPUTY}),
                ProcessDocumentState.ALLOCATED_TO_DEPUTY: frozenset({ProcessDocumentState.RETURNED_TO_CLIENT}),
            },
            evidence_reference=evidence_reference,
            occurred_at=occurred_at,
            baseline=self.registered_at,
        )


@dataclass(frozen=True, slots=True)
class District(_EvidenceMixin):
    """Immutable tenant-scoped jurisdiction identity."""

    tenant_id: str
    district_id: str
    name: str
    jurisdiction_code: str
    evidence_reference: str

    def __post_init__(self) -> None:
        _tenant(self.tenant_id)
        _identity("district_id", self.district_id)
        _text("name", self.name)
        _text("jurisdiction_code", self.jurisdiction_code)
        _text("evidence_reference", self.evidence_reference)


@dataclass(frozen=True, slots=True)
class SheriffOffice(_EvidenceMixin):
    """Immutable sheriff-office identity under one tenant and district."""

    tenant_id: str
    sheriff_office_id: str
    district_id: str
    name: str
    evidence_reference: str

    def __post_init__(self) -> None:
        _tenant(self.tenant_id)
        _identity("sheriff_office_id", self.sheriff_office_id)
        _identity("district_id", self.district_id)
        _text("name", self.name)
        _text("evidence_reference", self.evidence_reference)


@dataclass(frozen=True, slots=True)
class Deputy(_EvidenceMixin):
    """Immutable deputy reference; it grants no service or financial authority."""

    tenant_id: str
    deputy_id: str
    sheriff_office_id: str
    display_name: str
    badge_reference: str
    evidence_reference: str

    def __post_init__(self) -> None:
        _tenant(self.tenant_id)
        _identity("deputy_id", self.deputy_id)
        _identity("sheriff_office_id", self.sheriff_office_id)
        _text("display_name", self.display_name)
        _text("badge_reference", self.badge_reference)
        _text("evidence_reference", self.evidence_reference)


@dataclass(frozen=True, slots=True)
class DocumentCustodyEvent(_EvidenceMixin):
    """Immutable append-only custody fact; no mutable current-location field."""

    tenant_id: str
    custody_event_id: str
    document_id: str
    event_type: DocumentCustodyEventType
    occurred_at: datetime
    sequence_number: int
    evidence_reference: str
    from_holder_reference: str | None = None
    to_holder_reference: str | None = None

    def __post_init__(self) -> None:
        _tenant(self.tenant_id)
        _identity("custody_event_id", self.custody_event_id)
        _identity("document_id", self.document_id)
        if not isinstance(self.event_type, DocumentCustodyEventType):
            raise LegalOperationsLifecycleError("custody event type is invalid")
        _timestamp("occurred_at", self.occurred_at)
        _positive_int("sequence_number", self.sequence_number)
        _text("evidence_reference", self.evidence_reference)
        _optional_text("from_holder_reference", self.from_holder_reference)
        _optional_text("to_holder_reference", self.to_holder_reference)
        if self.event_type in {
            DocumentCustodyEventType.RECEIVED_IN_OFFICE,
            DocumentCustodyEventType.ALLOCATED_TO_DEPUTY,
            DocumentCustodyEventType.RETURNED_TO_CLIENT,
            DocumentCustodyEventType.TRANSFERRED,
        } and self.to_holder_reference is None:
            raise LegalOperationsLifecycleError("custody destination evidence is required")


def validate_custody_event_chain(events: Iterable[DocumentCustodyEvent]) -> tuple[DocumentCustodyEvent, ...]:
    """Validate one tenant/document custody chain with explicit chronology."""
    chain = tuple(events)
    if not chain:
        raise LegalOperationsLifecycleError("custody event evidence is required")
    tenant_id, document_id = chain[0].tenant_id, chain[0].document_id
    if chain[0].sequence_number != 1:
        raise LegalOperationsLifecycleError("custody chain must begin at sequence one")
    event_ids: set[str] = set()
    previous: DocumentCustodyEvent | None = None
    for event in chain:
        if not isinstance(event, DocumentCustodyEvent):
            raise LegalOperationsLifecycleError("custody chain contains invalid evidence")
        if event.tenant_id != tenant_id or event.document_id != document_id:
            raise LegalOperationsLifecycleError("custody chain crosses tenant or document scope")
        if event.custody_event_id in event_ids:
            raise LegalOperationsLifecycleError("custody chain contains duplicate event identity")
        event_ids.add(event.custody_event_id)
        if previous is not None:
            if event.sequence_number != previous.sequence_number + 1 or event.occurred_at < previous.occurred_at:
                raise LegalOperationsLifecycleError("custody chain chronology is invalid")
        previous = event
    if chain[0].event_type is not DocumentCustodyEventType.REGISTERED:
        raise LegalOperationsLifecycleError("custody chain must begin with registration evidence")
    return chain


@dataclass(frozen=True, slots=True)
class ServiceAttempt(_EvidenceMixin):
    """Immutable service attempt whose attempted state never implies service."""

    tenant_id: str
    attempt_id: str
    instruction_id: str
    document_id: str
    deputy_id: str
    allocated_at: datetime
    allocation_evidence_reference: str
    state: ServiceAttemptState = ServiceAttemptState.ALLOCATED
    transition_history: tuple[LifecycleTransitionEvidence, ...] = ()

    def __post_init__(self) -> None:
        _tenant(self.tenant_id)
        for name in ("attempt_id", "instruction_id", "document_id", "deputy_id"):
            _identity(name, getattr(self, name))
        _timestamp("allocated_at", self.allocated_at)
        _text("allocation_evidence_reference", self.allocation_evidence_reference)
        if not isinstance(self.state, ServiceAttemptState):
            raise LegalOperationsLifecycleError("attempt state is invalid")
        _validate_transition_history(
            initial_state=ServiceAttemptState.ALLOCATED,
            current_state=self.state,
            history=self.transition_history,
            allowed={
                ServiceAttemptState.ALLOCATED: frozenset({ServiceAttemptState.ATTEMPTED, ServiceAttemptState.CANCELLED}),
                ServiceAttemptState.ATTEMPTED: frozenset({ServiceAttemptState.COMPLETED, ServiceAttemptState.NOT_COMPLETED}),
            },
            baseline=self.allocated_at,
            terminal_states_require_fingerprint=frozenset({ServiceAttemptState.COMPLETED, ServiceAttemptState.NOT_COMPLETED}),
        )

    def transition_to(
        self,
        state: ServiceAttemptState,
        *,
        evidence_reference: str,
        occurred_at: datetime,
        evidence_fingerprint: str | None = None,
    ) -> "ServiceAttempt":
        """Advance an attempt; completion requires explicit service evidence."""
        return _transition(
            self,
            state,
            {
                ServiceAttemptState.ALLOCATED: frozenset({ServiceAttemptState.ATTEMPTED, ServiceAttemptState.CANCELLED}),
                ServiceAttemptState.ATTEMPTED: frozenset({ServiceAttemptState.COMPLETED, ServiceAttemptState.NOT_COMPLETED}),
            },
            evidence_reference=evidence_reference,
            evidence_fingerprint=evidence_fingerprint,
            occurred_at=occurred_at,
            baseline=self.allocated_at,
        )


@dataclass(frozen=True, slots=True, init=False)
class ServiceExecution(_EvidenceMixin):
    """Immutable certified service/non-service fact derived from an attempt."""

    tenant_id: str
    service_execution_id: str
    attempt_id: str
    instruction_id: str
    document_id: str
    outcome: ServiceExecutionOutcome
    executed_at: datetime
    evidence_reference: str
    evidence_fingerprint: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Reject documentary construction; use :meth:`from_attempt`."""
        raise LegalOperationsLifecycleError("service execution requires an evidenced service-attempt factory")

    def _validate(self) -> None:
        _tenant(self.tenant_id)
        for name in ("service_execution_id", "attempt_id", "instruction_id", "document_id"):
            _identity(name, getattr(self, name))
        if not isinstance(self.outcome, ServiceExecutionOutcome):
            raise LegalOperationsLifecycleError("service execution outcome is invalid")
        _timestamp("executed_at", self.executed_at)
        _text("evidence_reference", self.evidence_reference)
        if not isinstance(self.evidence_fingerprint, str) or re.fullmatch(r"[0-9a-f]{128}", self.evidence_fingerprint) is None:
            raise LegalOperationsLifecycleError("evidence_fingerprint must be lowercase SHA3-512 hex")

    @classmethod
    def from_attempt(
        cls,
        *,
        attempt: ServiceAttempt,
        service_execution_id: str,
        executed_at: datetime,
    ) -> "ServiceExecution":
        """Create executable service/non-service truth from one terminal attempt.

        Tenant, instruction/document/attempt identities, outcome, and source
        evidence are derived from the validated attempt; callers cannot supply
        arbitrary identifiers or hashes to manufacture service truth.
        """
        if not isinstance(attempt, ServiceAttempt):
            raise LegalOperationsLifecycleError("terminal service-attempt evidence is required")
        attempt.__post_init__()
        if attempt.state not in {ServiceAttemptState.COMPLETED, ServiceAttemptState.NOT_COMPLETED}:
            raise LegalOperationsLifecycleError("terminal service-attempt evidence is required")
        terminal_event = attempt.transition_history[-1] if attempt.transition_history else None
        if terminal_event is None or terminal_event.resulting_state is not attempt.state:
            raise LegalOperationsLifecycleError("terminal service-attempt evidence is incomplete")
        if terminal_event.evidence_fingerprint is None:
            raise LegalOperationsLifecycleError("terminal service-attempt fingerprint is required")
        execution = cast(Any, object.__new__(cls))
        object.__setattr__(execution, "tenant_id", attempt.tenant_id)
        object.__setattr__(execution, "service_execution_id", _identity("service_execution_id", service_execution_id))
        object.__setattr__(execution, "attempt_id", attempt.attempt_id)
        object.__setattr__(execution, "instruction_id", attempt.instruction_id)
        object.__setattr__(execution, "document_id", attempt.document_id)
        object.__setattr__(
            execution,
            "outcome",
            ServiceExecutionOutcome.COMPLETED
            if attempt.state is ServiceAttemptState.COMPLETED
            else ServiceExecutionOutcome.NOT_COMPLETED,
        )
        timestamp = _timestamp("executed_at", executed_at)
        if timestamp < terminal_event.occurred_at:
            raise LegalOperationsLifecycleError("service execution chronology is invalid")
        object.__setattr__(execution, "executed_at", timestamp)
        object.__setattr__(execution, "evidence_reference", terminal_event.evidence_reference)
        object.__setattr__(execution, "evidence_fingerprint", terminal_event.evidence_fingerprint)
        execution._validate()
        return cast("ServiceExecution", execution)


@dataclass(frozen=True, slots=True, init=False)
class ReturnOfService(_EvidenceMixin):
    """Immutable return evidence eligible only after certified service facts."""

    tenant_id: str
    return_id: str
    instruction_id: str
    document_id: str
    attempt_id: str
    service_execution_id: str
    service_outcome: ServiceExecutionOutcome
    service_evidence_reference: str
    service_evidence_fingerprint: str
    generated_at: datetime
    state: ReturnOfServiceState = ReturnOfServiceState.GENERATED

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Reject documentary construction; use :meth:`from_service_execution`."""
        raise LegalOperationsLifecycleError("return requires a validated service-execution factory")

    def _validate(self) -> None:
        _tenant(self.tenant_id)
        for name in ("return_id", "instruction_id", "document_id", "attempt_id", "service_execution_id"):
            _identity(name, getattr(self, name))
        if not isinstance(self.service_outcome, ServiceExecutionOutcome):
            raise LegalOperationsLifecycleError("return service outcome is invalid")
        _text("service_evidence_reference", self.service_evidence_reference)
        if re.fullmatch(r"[0-9a-f]{128}", self.service_evidence_fingerprint) is None:
            raise LegalOperationsLifecycleError("service evidence fingerprint must be lowercase SHA3-512 hex")
        _timestamp("generated_at", self.generated_at)
        if self.state is not ReturnOfServiceState.GENERATED:
            raise LegalOperationsLifecycleError("return state is invalid")

    @classmethod
    def from_service_execution(
        cls,
        *,
        instruction_id: str,
        service_execution: ServiceExecution,
        return_id: str,
        generated_at: datetime,
    ) -> "ReturnOfService":
        """Generate return evidence only from an explicit certified outcome."""
        if not isinstance(service_execution, ServiceExecution):
            raise LegalOperationsLifecycleError("certified service execution evidence is required")
        service_execution._validate()
        generated = _timestamp("generated_at", generated_at)
        if generated < service_execution.executed_at:
            raise LegalOperationsLifecycleError("return generation chronology is invalid")
        canonical_instruction_id = _identity("instruction_id", instruction_id)
        if canonical_instruction_id != service_execution.instruction_id:
            raise LegalOperationsLifecycleError("return instruction binding is invalid")
        result = cast(Any, object.__new__(cls))
        object.__setattr__(result, "tenant_id", service_execution.tenant_id)
        object.__setattr__(result, "return_id", _identity("return_id", return_id))
        object.__setattr__(result, "instruction_id", canonical_instruction_id)
        object.__setattr__(result, "document_id", service_execution.document_id)
        object.__setattr__(result, "attempt_id", service_execution.attempt_id)
        object.__setattr__(result, "service_execution_id", service_execution.service_execution_id)
        object.__setattr__(result, "service_outcome", service_execution.outcome)
        object.__setattr__(result, "service_evidence_reference", service_execution.evidence_reference)
        object.__setattr__(result, "service_evidence_fingerprint", service_execution.evidence_fingerprint)
        object.__setattr__(result, "generated_at", generated)
        object.__setattr__(result, "state", ReturnOfServiceState.GENERATED)
        result._validate()
        return cast("ReturnOfService", result)


__all__ = [
    "VERSION",
    "SCHEMA",
    "LegalOperationsLifecycleError",
    "LegalInstructionState",
    "CaseMatterState",
    "ProcessDocumentState",
    "DocumentCustodyEventType",
    "ServiceAttemptState",
    "ServiceExecutionOutcome",
    "ReturnOfServiceState",
    "LifecycleTransitionEvidence",
    "LegalInstruction",
    "CaseMatter",
    "ProcessDocument",
    "District",
    "SheriffOffice",
    "Deputy",
    "DocumentCustodyEvent",
    "validate_custody_event_chain",
    "ServiceAttempt",
    "ServiceExecution",
    "ReturnOfService",
]


# ARTIFACT: legal_operations_lifecycle.py
# VERSION: v1.0.0-LEGAL-OPERATIONS-LIFECYCLE
# AUTHORITY BOUNDARY: canonical legal-operations lifecycle evidence only.
# TENANT POSTURE: explicit tenant identity on every entity; no cross-tenant inference.
# FAIL-CLOSED POSTURE: invalid evidence, chronology, custody, or transitions reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
