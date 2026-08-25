# -*- coding: utf-8 -*-
"""
WILSY OS – FINANCIAL APPROVAL EFFECTIVE RESULT DOMAIN
VERSION: v1.0.1-FINANCIAL-APPROVAL-EFFECTIVE-RESULT

Immutable evidence produced by a future deterministic aggregation run. Quorum counts distinct authorized actors;
one decision maps to one requirement lane; duplicate actor decisions use the latest valid decision (decided_at DESC,
decision_id ASC); policy versions are strict; rejection conditions take precedence over approval. This object does
not aggregate, mutate VendorBill.approval_state, authorize release, invoke Kennel EOS, execute, or settle payment.
Maker-checker enforcement is unavailable because VendorBill has no canonical maker identity.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Mapping, Optional, Tuple

from .financial_approval_policy_evaluation import FinancialApprovalPolicySubjectType

MAX_EXCLUDED_DECISIONS = 250

class FinancialApprovalEffectiveResultDomainError(ValueError):
    """Raised when immutable aggregation evidence violates its structural contract."""

class FinancialApprovalEffectiveState(StrEnum):
    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class FinancialApprovalDecisionExclusionReason(StrEnum):
    WRONG_TENANT = "WRONG_TENANT"
    WRONG_SUBJECT = "WRONG_SUBJECT"
    WRONG_SUBJECT_REVISION = "WRONG_SUBJECT_REVISION"
    POLICY_REFERENCE_MISMATCH = "POLICY_REFERENCE_MISMATCH"
    POLICY_VERSION_MISSING = "POLICY_VERSION_MISSING"
    POLICY_VERSION_MISMATCH = "POLICY_VERSION_MISMATCH"
    NO_MATCHING_REQUIREMENT = "NO_MATCHING_REQUIREMENT"
    UNAUTHORIZED_ACTOR = "UNAUTHORIZED_ACTOR"
    AUTHORIZATION_NOT_YET_VALID = "AUTHORIZATION_NOT_YET_VALID"
    AUTHORIZATION_EXPIRED = "AUTHORIZATION_EXPIRED"
    ACTOR_CAPACITY_MISMATCH = "ACTOR_CAPACITY_MISMATCH"
    DUPLICATE_ACTOR_DECISION = "DUPLICATE_ACTOR_DECISION"
    SUPERSEDED_BY_LATER_DECISION = "SUPERSEDED_BY_LATER_DECISION"
    AMBIGUOUS_REQUIREMENT_MAPPING = "AMBIGUOUS_REQUIREMENT_MAPPING"

def _now() -> datetime:
    return datetime.now(timezone.utc)

def _text(value: Any, name: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise FinancialApprovalEffectiveResultDomainError(f"{name} must be a string")
    value = value.strip()
    if not value:
        raise FinancialApprovalEffectiveResultDomainError(f"{name} is required")
    if len(value) > maximum:
        raise FinancialApprovalEffectiveResultDomainError(f"{name} exceeds {maximum} characters")
    return value

def _time(value: Any, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise FinancialApprovalEffectiveResultDomainError(f"{name} must be timezone-aware")
    return value.astimezone(timezone.utc)

def _unique(values: Any, name: str) -> Tuple[str, ...]:
    if not isinstance(values, (tuple, list)):
        raise FinancialApprovalEffectiveResultDomainError(f"{name} must be a tuple or list")
    normalized = tuple(_text(item, name[:-1] if name.endswith("s") else name, 128) for item in values)
    if len(set(normalized)) != len(normalized):
        raise FinancialApprovalEffectiveResultDomainError(f"{name} must contain unique IDs")
    return normalized

@dataclass(frozen=True)
class FinancialApprovalRequirementResult:
    requirement_id: str
    actor_capacity: str
    approvals_required: int
    approvals_counted: int
    satisfied: bool
    counted_actor_ids: Tuple[str, ...] = ()
    counted_decision_ids: Tuple[str, ...] = ()
    counted_authorization_ids: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "requirement_id", _text(self.requirement_id, "requirement_id", 120))
        object.__setattr__(self, "actor_capacity", _text(self.actor_capacity, "actor_capacity", 120))
        for name in ("approvals_required", "approvals_counted"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < (1 if name == "approvals_required" else 0):
                raise FinancialApprovalEffectiveResultDomainError(f"{name} is invalid")
        actors = _unique(self.counted_actor_ids, "counted_actor_ids")
        decisions = _unique(self.counted_decision_ids, "counted_decision_ids")
        authorizations = _unique(self.counted_authorization_ids, "counted_authorization_ids")
        if self.approvals_counted != len(actors) or self.approvals_counted > len(actors):
            raise FinancialApprovalEffectiveResultDomainError("approvals_counted must equal distinct counted actors")
        if not isinstance(self.satisfied, bool) or self.satisfied != (self.approvals_counted >= self.approvals_required):
            raise FinancialApprovalEffectiveResultDomainError("satisfied is inconsistent with approval counts")
        object.__setattr__(self, "counted_actor_ids", actors)
        object.__setattr__(self, "counted_decision_ids", decisions)
        object.__setattr__(self, "counted_authorization_ids", authorizations)

@dataclass(frozen=True)
class FinancialApprovalExcludedDecision:
    decision_id: str
    actor_id: str
    reason: FinancialApprovalDecisionExclusionReason
    requirement_id: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "decision_id", _text(self.decision_id, "decision_id", 80))
        object.__setattr__(self, "actor_id", _text(self.actor_id, "actor_id", 128))
        if not isinstance(self.reason, FinancialApprovalDecisionExclusionReason):
            raise FinancialApprovalEffectiveResultDomainError("reason must use FinancialApprovalDecisionExclusionReason")
        if self.requirement_id is not None:
            object.__setattr__(self, "requirement_id", _text(self.requirement_id, "requirement_id", 120))

@dataclass(frozen=True)
class FinancialApprovalEffectiveResult:
    tenant_id: str
    result_id: str
    subject_type: FinancialApprovalPolicySubjectType
    subject_id: str
    subject_revision: int
    evaluation_id: str
    approval_policy_reference: str
    approval_policy_version: str
    effective_state: FinancialApprovalEffectiveState
    evaluated_at: datetime
    created_at: datetime
    requirement_results: Tuple[FinancialApprovalRequirementResult, ...] = ()
    counted_decision_ids: Tuple[str, ...] = ()
    counted_authorization_ids: Tuple[str, ...] = ()
    rejection_decision_ids: Tuple[str, ...] = ()
    rejection_actor_ids: Tuple[str, ...] = ()
    rejections_required: Optional[int] = None
    rejections_counted: int = 0
    excluded_decisions: Tuple[FinancialApprovalExcludedDecision, ...] = ()
    source_evidence_fingerprint: str = ""

    PERSISTENCE_SCHEMA = "WILSY-FINANCIAL-APPROVAL-EFFECTIVE-RESULT/V1"

    def to_persistence_dict(self) -> dict[str, Any]:
        """Return the complete deterministic BSON/JSON-safe immutable representation."""
        return {
            "schema": self.PERSISTENCE_SCHEMA,
            "tenant_id": self.tenant_id, "result_id": self.result_id,
            "subject_type": self.subject_type.value, "subject_id": self.subject_id,
            "subject_revision": self.subject_revision, "evaluation_id": self.evaluation_id,
            "approval_policy_reference": self.approval_policy_reference,
            "approval_policy_version": self.approval_policy_version,
            "effective_state": self.effective_state.value,
            "evaluated_at": self.evaluated_at.isoformat(), "created_at": self.created_at.isoformat(),
            "requirement_results": [{"requirement_id": r.requirement_id, "actor_capacity": r.actor_capacity, "approvals_required": r.approvals_required, "approvals_counted": r.approvals_counted, "satisfied": r.satisfied, "counted_actor_ids": list(r.counted_actor_ids), "counted_decision_ids": list(r.counted_decision_ids), "counted_authorization_ids": list(r.counted_authorization_ids)} for r in self.requirement_results],
            "counted_decision_ids": list(self.counted_decision_ids), "counted_authorization_ids": list(self.counted_authorization_ids),
            "rejection_decision_ids": list(self.rejection_decision_ids), "rejection_actor_ids": list(self.rejection_actor_ids),
            "rejections_required": self.rejections_required, "rejections_counted": self.rejections_counted,
            "excluded_decisions": [{"decision_id": e.decision_id, "actor_id": e.actor_id, "reason": e.reason.value, "requirement_id": e.requirement_id} for e in self.excluded_decisions],
            "source_evidence_fingerprint": self.source_evidence_fingerprint,
        }

    @classmethod
    def from_persistence_dict(cls, payload: Mapping[str, Any]) -> "FinancialApprovalEffectiveResult":
        """Strictly hydrate a canonical persistence payload without retaining mutable input."""
        if not isinstance(payload, Mapping) or payload.get("schema") != cls.PERSISTENCE_SCHEMA:
            raise FinancialApprovalEffectiveResultDomainError("invalid effective-result persistence schema")
        required = {"schema", "tenant_id", "result_id", "subject_type", "subject_id", "subject_revision", "evaluation_id", "approval_policy_reference", "approval_policy_version", "effective_state", "evaluated_at", "created_at", "requirement_results", "counted_decision_ids", "counted_authorization_ids", "rejection_decision_ids", "rejection_actor_ids", "rejections_required", "rejections_counted", "excluded_decisions", "source_evidence_fingerprint"}
        if set(payload) != required:
            raise FinancialApprovalEffectiveResultDomainError("effective-result persistence fields are incomplete")
        try:
            requirements = tuple(FinancialApprovalRequirementResult(r["requirement_id"], r["actor_capacity"], r["approvals_required"], r["approvals_counted"], r["satisfied"], tuple(r["counted_actor_ids"]), tuple(r["counted_decision_ids"]), tuple(r["counted_authorization_ids"])) for r in payload["requirement_results"])
            exclusions = tuple(FinancialApprovalExcludedDecision(e["decision_id"], e["actor_id"], FinancialApprovalDecisionExclusionReason(e["reason"]), e.get("requirement_id")) for e in payload["excluded_decisions"])
            return cls(tenant_id=payload["tenant_id"], result_id=payload["result_id"], subject_type=FinancialApprovalPolicySubjectType(payload["subject_type"]), subject_id=payload["subject_id"], subject_revision=payload["subject_revision"], evaluation_id=payload["evaluation_id"], approval_policy_reference=payload["approval_policy_reference"], approval_policy_version=payload["approval_policy_version"], effective_state=FinancialApprovalEffectiveState(payload["effective_state"]), evaluated_at=datetime.fromisoformat(payload["evaluated_at"]), created_at=datetime.fromisoformat(payload["created_at"]), requirement_results=requirements, counted_decision_ids=tuple(payload["counted_decision_ids"]), counted_authorization_ids=tuple(payload["counted_authorization_ids"]), rejection_decision_ids=tuple(payload["rejection_decision_ids"]), rejection_actor_ids=tuple(payload["rejection_actor_ids"]), rejections_required=payload["rejections_required"], rejections_counted=payload["rejections_counted"], excluded_decisions=exclusions, source_evidence_fingerprint=payload["source_evidence_fingerprint"])
        except (KeyError, TypeError, ValueError, OverflowError) as error:
            raise FinancialApprovalEffectiveResultDomainError("invalid effective-result persistence payload") from error

    def __post_init__(self) -> None:
        for name, maximum in (("tenant_id",128),("result_id",80),("subject_id",80),("evaluation_id",80),("approval_policy_reference",240),("approval_policy_version",120)):
            object.__setattr__(self, name, _text(getattr(self,name), name, maximum))
        if not isinstance(self.subject_type, FinancialApprovalPolicySubjectType) or not isinstance(self.effective_state, FinancialApprovalEffectiveState):
            raise FinancialApprovalEffectiveResultDomainError("invalid subject_type or effective_state")
        if not isinstance(self.subject_revision, int) or isinstance(self.subject_revision, bool) or self.subject_revision < 1:
            raise FinancialApprovalEffectiveResultDomainError("subject_revision must be an integer of at least 1")
        object.__setattr__(self, "evaluated_at", _time(self.evaluated_at, "evaluated_at"))
        object.__setattr__(self, "created_at", _time(self.created_at, "created_at"))
        requirements = tuple(self.requirement_results)
        if not isinstance(self.requirement_results, (tuple,list)) or len({r.requirement_id for r in requirements}) != len(requirements) or not all(isinstance(r, FinancialApprovalRequirementResult) for r in requirements):
            raise FinancialApprovalEffectiveResultDomainError("requirement_results are invalid")
        counted_decisions = _unique(self.counted_decision_ids, "counted_decision_ids")
        counted_auth = _unique(self.counted_authorization_ids, "counted_authorization_ids")
        rejection_decisions = _unique(self.rejection_decision_ids, "rejection_decision_ids")
        rejection_actors = _unique(self.rejection_actor_ids, "rejection_actor_ids")
        exclusions = tuple(self.excluded_decisions)
        if len(exclusions) > MAX_EXCLUDED_DECISIONS or not all(isinstance(e, FinancialApprovalExcludedDecision) for e in exclusions):
            raise FinancialApprovalEffectiveResultDomainError("excluded_decisions are invalid or oversized")
        if not isinstance(self.rejections_counted,int) or isinstance(self.rejections_counted,bool) or self.rejections_counted < 0 or self.rejections_counted != len(rejection_actors):
            raise FinancialApprovalEffectiveResultDomainError("rejections_counted must equal distinct rejection actors")
        if self.rejections_required is not None and (not isinstance(self.rejections_required,int) or isinstance(self.rejections_required,bool) or self.rejections_required < 1):
            raise FinancialApprovalEffectiveResultDomainError("rejections_required is invalid")
        if not isinstance(self.source_evidence_fingerprint,str) or re.fullmatch(r"[0-9a-f]{128}",self.source_evidence_fingerprint) is None:
            raise FinancialApprovalEffectiveResultDomainError("source_evidence_fingerprint must be lowercase SHA3-512 hex")
        if self.effective_state is FinancialApprovalEffectiveState.NOT_REQUIRED:
            if any((requirements,counted_decisions,counted_auth,rejection_decisions,rejection_actors)):
                raise FinancialApprovalEffectiveResultDomainError("NOT_REQUIRED cannot contain evidence")
        elif self.effective_state is FinancialApprovalEffectiveState.APPROVED:
            if not requirements or not all(r.satisfied for r in requirements) or (rejection_decisions and (self.rejections_required is None or self.rejections_counted >= self.rejections_required)):
                raise FinancialApprovalEffectiveResultDomainError("APPROVED evidence is inconsistent")
        elif self.effective_state is FinancialApprovalEffectiveState.PENDING:
            if not requirements or all(r.satisfied for r in requirements) or (rejection_decisions and (self.rejections_required is None or self.rejections_counted >= self.rejections_required)):
                raise FinancialApprovalEffectiveResultDomainError("PENDING evidence is inconsistent")
        else:
            if not rejection_decisions or not rejection_actors:
                raise FinancialApprovalEffectiveResultDomainError("REJECTED requires rejection evidence")
            if self.rejections_required is not None and self.rejections_counted < self.rejections_required:
                raise FinancialApprovalEffectiveResultDomainError("REJECTED requires satisfied rejection quorum")
        object.__setattr__(self, "requirement_results", requirements)
        object.__setattr__(self, "counted_decision_ids", counted_decisions)
        object.__setattr__(self, "counted_authorization_ids", counted_auth)
        object.__setattr__(self, "rejection_decision_ids", rejection_decisions)
        object.__setattr__(self, "rejection_actor_ids", rejection_actors)
        object.__setattr__(self, "excluded_decisions", exclusions)
