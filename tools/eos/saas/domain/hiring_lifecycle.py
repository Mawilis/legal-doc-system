"""Privacy-conscious candidate and employment-offer lifecycle domains.

Candidate PII remains in the governed candidate/HR source; this domain stores
only opaque profile references. Offer acceptance is evidence of consent only:
it never creates an employee, global principal, tenant membership, capacity,
IAM grant, payroll record, or payment instruction.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Final

VERSION: Final[str] = "v1.0.0-HR-CANDIDATE-OFFER"
SCHEMA: Final[str] = "wilsy.hr.hiring_lifecycle.v1"
_HEX_512 = re.compile(r"^[0-9a-f]{128}$")
_CURRENCY = re.compile(r"^[A-Z]{3}$")


class HiringLifecycleError(ValueError):
    """Invalid candidate or offer lifecycle state."""


def _required(name: str, value: object, maximum: int = 240) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > maximum:
        raise HiringLifecycleError(f"HIRING_{name.upper()}_INVALID")
    return value


def _aware(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise HiringLifecycleError("HIRING_TIMESTAMP_MUST_BE_TIMEZONE_AWARE")
    return value.astimezone(timezone.utc)


def _fingerprint(payload: dict[str, object]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha3_512(raw).hexdigest()


class CandidateStage(StrEnum):
    APPLIED = "APPLIED"
    SCREENING = "SCREENING"
    INTERVIEW = "INTERVIEW"
    REFERENCE_CHECK = "REFERENCE_CHECK"
    SELECTED = "SELECTED"
    DECLINED = "DECLINED"
    WITHDRAWN = "WITHDRAWN"


_CANDIDATE_NEXT = {
    CandidateStage.APPLIED: {CandidateStage.SCREENING},
    CandidateStage.SCREENING: {CandidateStage.INTERVIEW},
    CandidateStage.INTERVIEW: {CandidateStage.REFERENCE_CHECK},
    CandidateStage.REFERENCE_CHECK: {CandidateStage.SELECTED},
    CandidateStage.SELECTED: set(),
    CandidateStage.DECLINED: set(),
    CandidateStage.WITHDRAWN: set(),
}


@dataclass(frozen=True, slots=True)
class CandidateStageEvidence:
    actor_principal_id: str
    target_stage: CandidateStage | str
    reason: str
    evidence_reference: str
    evidence_fingerprint: str
    occurred_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "actor_principal_id", _required("candidate_actor", self.actor_principal_id))
        object.__setattr__(self, "reason", _required("candidate_stage_reason", self.reason, 2000))
        object.__setattr__(self, "evidence_reference", _required("candidate_evidence_reference", self.evidence_reference))
        if not isinstance(self.evidence_fingerprint, str) or not _HEX_512.fullmatch(self.evidence_fingerprint):
            raise HiringLifecycleError("HIRING_CANDIDATE_EVIDENCE_FINGERPRINT_INVALID")
        try:
            object.__setattr__(self, "target_stage", CandidateStage(self.target_stage))
        except (TypeError, ValueError) as error:
            raise HiringLifecycleError("HIRING_CANDIDATE_STAGE_INVALID") from error
        object.__setattr__(self, "occurred_at", _aware(self.occurred_at))

    def to_dict(self) -> dict[str, object]:
        return {
            "actor_principal_id": self.actor_principal_id,
            "target_stage": self.target_stage.value,
            "reason": self.reason,
            "evidence_reference": self.evidence_reference,
            "evidence_fingerprint": self.evidence_fingerprint,
            "occurred_at": self.occurred_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class CandidateApplication:
    tenant_id: str
    candidate_id: str
    requisition_id: str
    candidate_profile_reference: str
    source: str
    created_by_principal_id: str
    created_at: datetime
    stage: CandidateStage | str = CandidateStage.APPLIED
    history: tuple[CandidateStageEvidence, ...] = ()
    revision: int = 1
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        for name in ("tenant_id", "candidate_id", "requisition_id", "candidate_profile_reference", "source", "created_by_principal_id"):
            object.__setattr__(self, name, _required(name, getattr(self, name)))
        object.__setattr__(self, "created_at", _aware(self.created_at))
        try:
            stage = CandidateStage(self.stage)
        except (TypeError, ValueError) as error:
            raise HiringLifecycleError("HIRING_CANDIDATE_STAGE_INVALID") from error
        object.__setattr__(self, "stage", stage)
        if self.schema != SCHEMA or self.version != VERSION:
            raise HiringLifecycleError("HIRING_SCHEMA_VERSION_INVALID")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 1:
            raise HiringLifecycleError("HIRING_CANDIDATE_REVISION_INVALID")
        if not isinstance(self.history, tuple) or len(self.history) != self.revision - 1:
            raise HiringLifecycleError("HIRING_CANDIDATE_HISTORY_REVISION_MISMATCH")
        if len(self.history) > 8 or any(not isinstance(x, CandidateStageEvidence) for x in self.history):
            raise HiringLifecycleError("HIRING_CANDIDATE_HISTORY_INVALID")
        expected = self.history[-1].target_stage if self.history else CandidateStage.APPLIED
        if stage is not expected:
            raise HiringLifecycleError("HIRING_CANDIDATE_STAGE_HISTORY_MISMATCH")
        digest = self._digest()
        if self.fingerprint and (not _HEX_512.fullmatch(self.fingerprint) or not hmac.compare_digest(self.fingerprint, digest)):
            raise HiringLifecycleError("HIRING_CANDIDATE_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def _payload(self) -> dict[str, object]:
        return {
            "tenant_id": self.tenant_id, "candidate_id": self.candidate_id,
            "requisition_id": self.requisition_id,
            "candidate_profile_reference": self.candidate_profile_reference,
            "source": self.source, "created_by_principal_id": self.created_by_principal_id,
            "created_at": self.created_at.isoformat(), "stage": self.stage.value,
            "history": [item.to_dict() for item in self.history],
            "revision": self.revision, "schema": self.schema, "version": self.version,
        }

    def _digest(self) -> str:
        return _fingerprint(self._payload())

    def to_dict(self) -> dict[str, object]:
        return {**self._payload(), "fingerprint": self.fingerprint}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "CandidateApplication":
        expected = {
            "tenant_id", "candidate_id", "requisition_id", "candidate_profile_reference",
            "source", "created_by_principal_id", "created_at", "stage", "history",
            "revision", "schema", "version", "fingerprint",
        }
        if not isinstance(payload, dict) or set(payload) != expected:
            raise HiringLifecycleError("HIRING_CANDIDATE_PERSISTED_SCHEMA_INVALID")
        raw_history = payload["history"]
        if not isinstance(raw_history, list):
            raise HiringLifecycleError("HIRING_CANDIDATE_HISTORY_INVALID")
        history = []
        for raw in raw_history:
            if not isinstance(raw, dict) or set(raw) != {
                "actor_principal_id", "target_stage", "reason", "evidence_reference",
                "evidence_fingerprint", "occurred_at",
            }:
                raise HiringLifecycleError("HIRING_CANDIDATE_EVIDENCE_SCHEMA_INVALID")
            values = dict(raw)
            values["occurred_at"] = datetime.fromisoformat(str(values["occurred_at"]))
            history.append(CandidateStageEvidence(**values))
        values = dict(payload)
        values["created_at"] = datetime.fromisoformat(str(values["created_at"]))
        values["history"] = tuple(history)
        try:
            return cls(**values)
        except TypeError as error:
            raise HiringLifecycleError("HIRING_CANDIDATE_PERSISTED_SCHEMA_INVALID") from error

    def advance(
        self, target_stage: CandidateStage | str, evidence: CandidateStageEvidence,
        *, expected_revision: int,
    ) -> "CandidateApplication":
        if expected_revision != self.revision:
            raise HiringLifecycleError("HIRING_CANDIDATE_REVISION_CONFLICT")
        target = CandidateStage(target_stage)
        if target not in _CANDIDATE_NEXT[self.stage] and target not in {CandidateStage.DECLINED, CandidateStage.WITHDRAWN}:
            raise HiringLifecycleError("HIRING_CANDIDATE_TRANSITION_NOT_ALLOWED")
        if evidence.target_stage is not target:
            raise HiringLifecycleError("HIRING_CANDIDATE_EVIDENCE_STAGE_MISMATCH")
        return CandidateApplication(
            tenant_id=self.tenant_id, candidate_id=self.candidate_id,
            requisition_id=self.requisition_id,
            candidate_profile_reference=self.candidate_profile_reference,
            source=self.source, created_by_principal_id=self.created_by_principal_id,
            created_at=self.created_at, stage=target,
            history=(*self.history, evidence), revision=self.revision + 1,
        )


class OfferStatus(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    WITHDRAWN = "WITHDRAWN"
    EXPIRED = "EXPIRED"


@dataclass(frozen=True, slots=True)
class OfferTerms:
    position_title: str
    employment_type: str
    work_location: str
    currency: str
    gross_compensation_minor: int
    pay_frequency: str
    start_date: date
    expires_at: datetime

    def __post_init__(self) -> None:
        for name in ("position_title", "employment_type", "work_location", "pay_frequency"):
            object.__setattr__(self, name, _required(f"offer_{name}", getattr(self, name)))
        if not isinstance(self.currency, str) or not _CURRENCY.fullmatch(self.currency):
            raise HiringLifecycleError("HIRING_OFFER_CURRENCY_INVALID")
        if isinstance(self.gross_compensation_minor, bool) or not isinstance(self.gross_compensation_minor, int) or self.gross_compensation_minor <= 0:
            raise HiringLifecycleError("HIRING_OFFER_COMPENSATION_INVALID")
        if not isinstance(self.start_date, date) or isinstance(self.start_date, datetime):
            raise HiringLifecycleError("HIRING_OFFER_START_DATE_INVALID")
        object.__setattr__(self, "expires_at", _aware(self.expires_at))

    def to_dict(self) -> dict[str, object]:
        return {
            "position_title": self.position_title, "employment_type": self.employment_type,
            "work_location": self.work_location, "currency": self.currency,
            "gross_compensation_minor": self.gross_compensation_minor,
            "pay_frequency": self.pay_frequency, "start_date": self.start_date.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class OfferDecision:
    decision_id: str
    actor_principal_id: str
    approved: bool
    reason: str
    decided_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "decision_id", _required("offer_decision_id", self.decision_id))
        object.__setattr__(self, "actor_principal_id", _required("offer_approver", self.actor_principal_id))
        object.__setattr__(self, "reason", _required("offer_decision_reason", self.reason, 2000))
        if type(self.approved) is not bool:
            raise HiringLifecycleError("HIRING_OFFER_DECISION_INVALID")
        object.__setattr__(self, "decided_at", _aware(self.decided_at))

    def to_dict(self) -> dict[str, object]:
        return {
            "decision_id": self.decision_id, "actor_principal_id": self.actor_principal_id,
            "approved": self.approved, "reason": self.reason,
            "decided_at": self.decided_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class OfferAcceptanceEvidence:
    evidence_reference: str
    evidence_fingerprint: str
    accepted_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence_reference", _required("offer_acceptance_reference", self.evidence_reference))
        if not isinstance(self.evidence_fingerprint, str) or not _HEX_512.fullmatch(self.evidence_fingerprint):
            raise HiringLifecycleError("HIRING_OFFER_ACCEPTANCE_FINGERPRINT_INVALID")
        object.__setattr__(self, "accepted_at", _aware(self.accepted_at))

    def to_dict(self) -> dict[str, object]:
        return {
            "evidence_reference": self.evidence_reference,
            "evidence_fingerprint": self.evidence_fingerprint,
            "accepted_at": self.accepted_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class EmploymentOffer:
    tenant_id: str
    offer_id: str
    requisition_id: str
    candidate_id: str
    terms: OfferTerms
    prepared_by_principal_id: str
    created_at: datetime
    status: OfferStatus | str = OfferStatus.DRAFT
    submitted_at: datetime | None = None
    decision: OfferDecision | None = None
    sent_at: datetime | None = None
    acceptance: OfferAcceptanceEvidence | None = None
    revision: int = 1
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        for name in ("tenant_id", "offer_id", "requisition_id", "candidate_id", "prepared_by_principal_id"):
            object.__setattr__(self, name, _required(name, getattr(self, name)))
        if not isinstance(self.terms, OfferTerms):
            raise HiringLifecycleError("HIRING_OFFER_TERMS_REQUIRED")
        object.__setattr__(self, "created_at", _aware(self.created_at))
        try:
            status = OfferStatus(self.status)
        except (TypeError, ValueError) as error:
            raise HiringLifecycleError("HIRING_OFFER_STATUS_INVALID") from error
        object.__setattr__(self, "status", status)
        if self.schema != SCHEMA or self.version != VERSION:
            raise HiringLifecycleError("HIRING_SCHEMA_VERSION_INVALID")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 1:
            raise HiringLifecycleError("HIRING_OFFER_REVISION_INVALID")
        if self.submitted_at is not None:
            object.__setattr__(self, "submitted_at", _aware(self.submitted_at))
        if self.sent_at is not None:
            object.__setattr__(self, "sent_at", _aware(self.sent_at))
        if status is OfferStatus.DRAFT and any((self.submitted_at, self.decision, self.sent_at, self.acceptance)):
            raise HiringLifecycleError("HIRING_OFFER_DRAFT_EVIDENCE_INVALID")
        if status in {OfferStatus.SUBMITTED, OfferStatus.APPROVED, OfferStatus.REJECTED, OfferStatus.SENT, OfferStatus.ACCEPTED, OfferStatus.DECLINED, OfferStatus.EXPIRED, OfferStatus.WITHDRAWN} and self.submitted_at is None:
            raise HiringLifecycleError("HIRING_OFFER_SUBMISSION_EVIDENCE_REQUIRED")
        if status in {OfferStatus.APPROVED, OfferStatus.REJECTED, OfferStatus.SENT, OfferStatus.ACCEPTED, OfferStatus.DECLINED, OfferStatus.EXPIRED, OfferStatus.WITHDRAWN} and self.decision is None:
            raise HiringLifecycleError("HIRING_OFFER_DECISION_EVIDENCE_REQUIRED")
        if self.decision is not None:
            expected = status is not OfferStatus.REJECTED
            if self.decision.approved is not expected:
                raise HiringLifecycleError("HIRING_OFFER_DECISION_STATUS_MISMATCH")
            if self.decision.actor_principal_id == self.prepared_by_principal_id:
                raise HiringLifecycleError("HIRING_OFFER_MAKER_CHECKER_VIOLATION")
        if status in {OfferStatus.SENT, OfferStatus.ACCEPTED, OfferStatus.DECLINED, OfferStatus.EXPIRED} and self.sent_at is None:
            raise HiringLifecycleError("HIRING_OFFER_SENT_EVIDENCE_REQUIRED")
        if status is OfferStatus.ACCEPTED and self.acceptance is None:
            raise HiringLifecycleError("HIRING_OFFER_ACCEPTANCE_EVIDENCE_REQUIRED")
        if status is not OfferStatus.ACCEPTED and self.acceptance is not None:
            raise HiringLifecycleError("HIRING_OFFER_ACCEPTANCE_STATUS_MISMATCH")
        digest = self._digest()
        if self.fingerprint and (not _HEX_512.fullmatch(self.fingerprint) or not hmac.compare_digest(self.fingerprint, digest)):
            raise HiringLifecycleError("HIRING_OFFER_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def _payload(self) -> dict[str, object]:
        return {
            "tenant_id": self.tenant_id, "offer_id": self.offer_id,
            "requisition_id": self.requisition_id, "candidate_id": self.candidate_id,
            "terms": self.terms.to_dict(), "prepared_by_principal_id": self.prepared_by_principal_id,
            "created_at": self.created_at.isoformat(), "status": self.status.value,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "decision": self.decision.to_dict() if self.decision else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "acceptance": self.acceptance.to_dict() if self.acceptance else None,
            "revision": self.revision, "schema": self.schema, "version": self.version,
        }

    def _digest(self) -> str:
        return _fingerprint(self._payload())

    def to_dict(self) -> dict[str, object]:
        return {**self._payload(), "fingerprint": self.fingerprint}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "EmploymentOffer":
        expected = {
            "tenant_id", "offer_id", "requisition_id", "candidate_id", "terms",
            "prepared_by_principal_id", "created_at", "status", "submitted_at",
            "decision", "sent_at", "acceptance", "revision", "schema", "version",
            "fingerprint",
        }
        if not isinstance(payload, dict) or set(payload) != expected:
            raise HiringLifecycleError("HIRING_OFFER_PERSISTED_SCHEMA_INVALID")
        values = dict(payload)
        terms = values.pop("terms")
        if not isinstance(terms, dict) or set(terms) != {
            "position_title", "employment_type", "work_location", "currency",
            "gross_compensation_minor", "pay_frequency", "start_date", "expires_at",
        }:
            raise HiringLifecycleError("HIRING_OFFER_TERMS_SCHEMA_INVALID")
        terms_values = dict(terms)
        terms_values["start_date"] = date.fromisoformat(str(terms_values["start_date"]))
        terms_values["expires_at"] = datetime.fromisoformat(str(terms_values["expires_at"]))
        values["terms"] = OfferTerms(**terms_values)
        values["created_at"] = datetime.fromisoformat(str(values["created_at"]))
        values["submitted_at"] = None if values["submitted_at"] is None else datetime.fromisoformat(str(values["submitted_at"]))
        values["sent_at"] = None if values["sent_at"] is None else datetime.fromisoformat(str(values["sent_at"]))
        decision = values["decision"]
        if decision is not None:
            if not isinstance(decision, dict) or set(decision) != {
                "decision_id", "actor_principal_id", "approved", "reason", "decided_at",
            }:
                raise HiringLifecycleError("HIRING_OFFER_DECISION_SCHEMA_INVALID")
            decision_values = dict(decision)
            decision_values["decided_at"] = datetime.fromisoformat(str(decision_values["decided_at"]))
            values["decision"] = OfferDecision(**decision_values)
        acceptance = values["acceptance"]
        if acceptance is not None:
            if not isinstance(acceptance, dict) or set(acceptance) != {
                "evidence_reference", "evidence_fingerprint", "accepted_at",
            }:
                raise HiringLifecycleError("HIRING_OFFER_ACCEPTANCE_SCHEMA_INVALID")
            acceptance_values = dict(acceptance)
            acceptance_values["accepted_at"] = datetime.fromisoformat(str(acceptance_values["accepted_at"]))
            values["acceptance"] = OfferAcceptanceEvidence(**acceptance_values)
        try:
            return cls(**values)
        except TypeError as error:
            raise HiringLifecycleError("HIRING_OFFER_PERSISTED_SCHEMA_INVALID") from error

    def submit(self, *, actor_principal_id: str, submitted_at: datetime, expected_revision: int) -> "EmploymentOffer":
        if expected_revision != self.revision:
            raise HiringLifecycleError("HIRING_OFFER_REVISION_CONFLICT")
        if self.status is not OfferStatus.DRAFT or actor_principal_id != self.prepared_by_principal_id:
            raise HiringLifecycleError("HIRING_OFFER_SUBMISSION_NOT_ALLOWED")
        return EmploymentOffer(
            tenant_id=self.tenant_id, offer_id=self.offer_id, requisition_id=self.requisition_id,
            candidate_id=self.candidate_id, terms=self.terms,
            prepared_by_principal_id=self.prepared_by_principal_id, created_at=self.created_at,
            status=OfferStatus.SUBMITTED, submitted_at=submitted_at, revision=self.revision + 1,
        )

    def decide(self, decision: OfferDecision, *, expected_revision: int) -> "EmploymentOffer":
        if expected_revision != self.revision:
            raise HiringLifecycleError("HIRING_OFFER_REVISION_CONFLICT")
        if self.status is not OfferStatus.SUBMITTED:
            raise HiringLifecycleError("HIRING_OFFER_ONLY_SUBMITTED_CAN_BE_DECIDED")
        if decision.actor_principal_id == self.prepared_by_principal_id:
            raise HiringLifecycleError("HIRING_OFFER_MAKER_CHECKER_VIOLATION")
        return EmploymentOffer(
            tenant_id=self.tenant_id, offer_id=self.offer_id, requisition_id=self.requisition_id,
            candidate_id=self.candidate_id, terms=self.terms,
            prepared_by_principal_id=self.prepared_by_principal_id, created_at=self.created_at,
            status=OfferStatus.APPROVED if decision.approved else OfferStatus.REJECTED,
            submitted_at=self.submitted_at, decision=decision, revision=self.revision + 1,
        )

    def send(self, *, actor_principal_id: str, sent_at: datetime, expected_revision: int) -> "EmploymentOffer":
        if expected_revision != self.revision:
            raise HiringLifecycleError("HIRING_OFFER_REVISION_CONFLICT")
        if self.status is not OfferStatus.APPROVED:
            raise HiringLifecycleError("HIRING_OFFER_MUST_BE_APPROVED_BEFORE_SEND")
        _required("offer_sender", actor_principal_id)
        if _aware(sent_at) >= self.terms.expires_at:
            raise HiringLifecycleError("HIRING_OFFER_EXPIRED_BEFORE_SEND")
        return EmploymentOffer(
            tenant_id=self.tenant_id, offer_id=self.offer_id, requisition_id=self.requisition_id,
            candidate_id=self.candidate_id, terms=self.terms,
            prepared_by_principal_id=self.prepared_by_principal_id, created_at=self.created_at,
            status=OfferStatus.SENT, submitted_at=self.submitted_at, decision=self.decision,
            sent_at=sent_at, revision=self.revision + 1,
        )

    def accept(self, evidence: OfferAcceptanceEvidence, *, expected_revision: int) -> "EmploymentOffer":
        if expected_revision != self.revision:
            raise HiringLifecycleError("HIRING_OFFER_REVISION_CONFLICT")
        if self.status is not OfferStatus.SENT:
            raise HiringLifecycleError("HIRING_OFFER_MUST_BE_SENT_BEFORE_ACCEPTANCE")
        if evidence.accepted_at >= self.terms.expires_at:
            raise HiringLifecycleError("HIRING_OFFER_ACCEPTANCE_AFTER_EXPIRY")
        return EmploymentOffer(
            tenant_id=self.tenant_id, offer_id=self.offer_id, requisition_id=self.requisition_id,
            candidate_id=self.candidate_id, terms=self.terms,
            prepared_by_principal_id=self.prepared_by_principal_id, created_at=self.created_at,
            status=OfferStatus.ACCEPTED, submitted_at=self.submitted_at, decision=self.decision,
            sent_at=self.sent_at, acceptance=evidence, revision=self.revision + 1,
        )


__all__ = [
    "VERSION", "SCHEMA", "HiringLifecycleError", "CandidateStage",
    "CandidateStageEvidence", "CandidateApplication", "OfferStatus",
    "OfferTerms", "OfferDecision", "OfferAcceptanceEvidence", "EmploymentOffer",
]
