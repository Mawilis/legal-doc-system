# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS – FINANCIAL APPROVAL POLICY EVALUATION DOMAIN                                                          ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ VERSION:        v1.0.0-FINANCIAL-APPROVAL-POLICY-EVALUATION                                                     ║
║ EPITOME:        Immutable requirements output for one tenant-local financial subject revision.                  ║
║ BIBLICAL ANCHOR: Psalm 1:3 — "And he shall be like a tree planted by the rivers of water..."                  ║
║ ABSOLUTE PATH:  /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/financial_approval_policy_evaluation.py ║
║ COLLABORATION:  Wilson Khanyezi (Founder/Chief Architect) mandated policy and payment separation.               ║
║                 AI Engineering (Codex) defined immutable resolved-policy evidence only.                         ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

FinancialApprovalPolicyEvaluation is not an approval request, decision, VendorBill projection, release
authorization, payment execution, or settlement. A future effective approval result still has zero authority to
move money; Kennel EOS remains the exclusive future execution authority.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, Optional, Tuple
from uuid import uuid4


class FinancialApprovalPolicyEvaluationDomainError(ValueError):
    """Raised when immutable resolved financial approval-policy evidence is structurally invalid."""


class FinancialApprovalPolicySubjectType(StrEnum):
    """Enumerates the deliberately narrow subjects supported by this initial policy-evaluation contract."""
    VENDOR_BILL = "VENDOR_BILL"


class FinancialApprovalRejectionRule(StrEnum):
    """Makes rejection aggregation policy explicit without inventing latest-decision semantics."""
    ANY_VALID_REJECTION_BLOCKS = "ANY_VALID_REJECTION_BLOCKS"
    REJECTION_QUORUM = "REJECTION_QUORUM"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _required_text(value: Any, field_name: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise FinancialApprovalPolicyEvaluationDomainError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise FinancialApprovalPolicyEvaluationDomainError(f"{field_name} is required")
    if len(normalized) > maximum:
        raise FinancialApprovalPolicyEvaluationDomainError(f"{field_name} exceeds {maximum} characters")
    return normalized


def _aware_utc(value: Any, field_name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise FinancialApprovalPolicyEvaluationDomainError(f"{field_name} must be a timezone-aware datetime")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class FinancialApprovalRequirement:
    """One policy-defined approval lane; actor capacity is required evidence, not actor authorization proof."""
    requirement_id: str
    actor_capacity: str
    approvals_required: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "requirement_id", _required_text(self.requirement_id, "requirement_id", 120))
        object.__setattr__(self, "actor_capacity", _required_text(self.actor_capacity, "actor_capacity", 120))
        if not isinstance(self.approvals_required, int) or isinstance(self.approvals_required, bool) or self.approvals_required < 1:
            raise FinancialApprovalPolicyEvaluationDomainError("approvals_required must be an integer of at least 1")

    def to_dict(self) -> Dict[str, Any]:
        return {"requirement_id": self.requirement_id, "actor_capacity": self.actor_capacity, "approvals_required": self.approvals_required}


def _requirements(value: Any) -> Tuple[FinancialApprovalRequirement, ...]:
    if not isinstance(value, (tuple, list)):
        raise FinancialApprovalPolicyEvaluationDomainError("approval_requirements must be a tuple or list of FinancialApprovalRequirement")
    if len(value) > 32:
        raise FinancialApprovalPolicyEvaluationDomainError("approval_requirements exceeds 32 entries")
    if not all(isinstance(item, FinancialApprovalRequirement) for item in value):
        raise FinancialApprovalPolicyEvaluationDomainError("approval_requirements must contain FinancialApprovalRequirement values")
    requirements = tuple(value)
    if len({item.requirement_id for item in requirements}) != len(requirements):
        raise FinancialApprovalPolicyEvaluationDomainError("approval_requirements requirement_id values must be unique")
    return requirements


@dataclass(frozen=True)
class FinancialApprovalPolicyEvaluation:
    """Immutable resolved approval requirements for one exact VendorBill revision and subject snapshot.

    Requirement capacities describe what the policy demands, never proof that a particular actor holds a capacity.
    A separate tenant-scoped RBAC/delegation authority must validate actors before a future aggregator can use decisions.
    """
    tenant_id: str
    evaluation_id: str
    subject_type: FinancialApprovalPolicySubjectType
    subject_id: str
    subject_revision: int
    approval_policy_reference: str
    approval_policy_version: str
    approval_required: bool
    approval_requirements: Tuple[FinancialApprovalRequirement, ...]
    rejection_rule: FinancialApprovalRejectionRule
    subject_snapshot_fingerprint: str
    evaluator_reference: str
    rejections_required: Optional[int] = None
    evaluated_at: datetime = field(default_factory=_utc_now)
    created_at: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        object.__setattr__(self, "tenant_id", _required_text(self.tenant_id, "tenant_id", 128))
        object.__setattr__(self, "evaluation_id", _required_text(self.evaluation_id, "evaluation_id", 80))
        object.__setattr__(self, "subject_id", _required_text(self.subject_id, "subject_id", 80))
        object.__setattr__(self, "approval_policy_reference", _required_text(self.approval_policy_reference, "approval_policy_reference", 240))
        object.__setattr__(self, "approval_policy_version", _required_text(self.approval_policy_version, "approval_policy_version", 120))
        object.__setattr__(self, "evaluator_reference", _required_text(self.evaluator_reference, "evaluator_reference", 240))
        if not isinstance(self.subject_type, FinancialApprovalPolicySubjectType):
            raise FinancialApprovalPolicyEvaluationDomainError("subject_type must use FinancialApprovalPolicySubjectType")
        if not isinstance(self.subject_revision, int) or isinstance(self.subject_revision, bool) or self.subject_revision < 1:
            raise FinancialApprovalPolicyEvaluationDomainError("subject_revision must be an integer of at least 1")
        if not isinstance(self.approval_required, bool):
            raise FinancialApprovalPolicyEvaluationDomainError("approval_required must be a bool")
        requirements = _requirements(self.approval_requirements)
        object.__setattr__(self, "approval_requirements", requirements)
        if self.approval_required != bool(requirements):
            raise FinancialApprovalPolicyEvaluationDomainError("approval_required must match whether approval_requirements are present")
        if not isinstance(self.rejection_rule, FinancialApprovalRejectionRule):
            raise FinancialApprovalPolicyEvaluationDomainError("rejection_rule must use FinancialApprovalRejectionRule")
        if self.rejection_rule is FinancialApprovalRejectionRule.ANY_VALID_REJECTION_BLOCKS:
            if self.rejections_required is not None:
                raise FinancialApprovalPolicyEvaluationDomainError("rejections_required must be absent for ANY_VALID_REJECTION_BLOCKS")
        elif (not isinstance(self.rejections_required, int) or isinstance(self.rejections_required, bool) or self.rejections_required < 1):
            raise FinancialApprovalPolicyEvaluationDomainError("rejections_required must be an integer of at least 1 for REJECTION_QUORUM")
        if not isinstance(self.subject_snapshot_fingerprint, str) or re.fullmatch(r"[0-9a-f]{128}", self.subject_snapshot_fingerprint) is None:
            raise FinancialApprovalPolicyEvaluationDomainError("subject_snapshot_fingerprint must be lowercase SHA3-512 hex")
        object.__setattr__(self, "evaluated_at", _aware_utc(self.evaluated_at, "evaluated_at"))
        object.__setattr__(self, "created_at", _aware_utc(self.created_at, "created_at"))

    @classmethod
    def new_id(cls) -> str:
        """Creates an opaque identity for a new immutable evaluation without implying policy resolution."""
        return str(uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Serializes policy requirements only; no decision, projection, release, or payment authority is conveyed."""
        return {"schema": "WILSY-FINANCIAL-APPROVAL-POLICY-EVALUATION/V1", "tenant_id": self.tenant_id, "evaluation_id": self.evaluation_id, "subject_type": self.subject_type.value, "subject_id": self.subject_id, "subject_revision": self.subject_revision, "approval_policy_reference": self.approval_policy_reference, "approval_policy_version": self.approval_policy_version, "approval_required": self.approval_required, "approval_requirements": [item.to_dict() for item in self.approval_requirements], "rejection_rule": self.rejection_rule.value, "rejections_required": self.rejections_required, "subject_snapshot_fingerprint": self.subject_snapshot_fingerprint, "evaluator_reference": self.evaluator_reference, "evaluated_at": self.evaluated_at.isoformat(), "created_at": self.created_at.isoformat()}
