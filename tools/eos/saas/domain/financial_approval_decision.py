# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS – CANONICAL FINANCIAL APPROVAL DECISION DOMAIN                                                         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ VERSION:        v1.0.0-FINANCIAL-APPROVAL-DECISION                                                              ║
║ EPITOME:        Immutable tenant-scoped evidence of a completed financial approval decision.                    ║
║ BIBLICAL ANCHOR: Psalm 1:3 — "And he shall be like a tree planted by the rivers of water..."                  ║
║ ABSOLUTE PATH:  /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/financial_approval_decision.py    ║
║ COLLABORATION:  Wilson Khanyezi (Founder/Chief Architect) mandated separated approval authority.                ║
║                 AI Engineering (Codex) defined decision evidence without release or execution authority.       ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

An APPROVED decision is not payment release, a payment request, Kennel execution, or settlement.
This object has zero authority to move money; Kennel EOS remains the exclusive future execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, Optional, Tuple
from uuid import uuid4


class FinancialApprovalDecisionDomainError(ValueError):
    """Raised when completed financial approval evidence violates its immutable contract."""


class FinancialApprovalSubjectType(StrEnum):
    """Enumerates the deliberately narrow subject types governed by this decision contract."""
    VENDOR_BILL = "VENDOR_BILL"


class FinancialApprovalDecisionType(StrEnum):
    """Enumerates completed decisions; workflow PENDING is intentionally not a decision."""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


def _utc_now() -> datetime:
    """Returns the canonical aware UTC timestamp for immutable financial decision evidence."""
    return datetime.now(timezone.utc)


def _required_text(value: Any, field_name: str, maximum: int) -> str:
    """Normalizes a required bounded textual evidence field without coercing arbitrary objects."""
    if not isinstance(value, str):
        raise FinancialApprovalDecisionDomainError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise FinancialApprovalDecisionDomainError(f"{field_name} is required")
    if len(normalized) > maximum:
        raise FinancialApprovalDecisionDomainError(f"{field_name} exceeds {maximum} characters")
    return normalized


def _optional_text(value: Any, field_name: str, maximum: int) -> Optional[str]:
    """Normalizes optional bounded policy-version evidence without inventing a version convention."""
    if value is None:
        return None
    return _required_text(value, field_name, maximum)


def _aware_utc(value: Any, field_name: str) -> datetime:
    """Requires timezone-aware timestamps and canonicalizes them to UTC for durable evidence equality."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise FinancialApprovalDecisionDomainError(f"{field_name} must be a timezone-aware datetime")
    return value.astimezone(timezone.utc)


def _evidence_references(value: Any) -> Tuple[str, ...]:
    """Accepts only bounded textual reference identifiers and stores them as immutable ordered evidence."""
    if value is None:
        return ()
    if not isinstance(value, (tuple, list)):
        raise FinancialApprovalDecisionDomainError("evidence_references must be a tuple or list of strings")
    if len(value) > 32:
        raise FinancialApprovalDecisionDomainError("evidence_references exceeds 32 entries")
    normalized = tuple(_required_text(item, "evidence_reference", 240) for item in value)
    if len(set(normalized)) != len(normalized):
        raise FinancialApprovalDecisionDomainError("evidence_references must not contain duplicates")
    return normalized


@dataclass(frozen=True)
class FinancialApprovalDecision:
    """Immutable completed decision evidence for a tenant-local financial subject.

    The first supported subject is ``VENDOR_BILL`` whose ``subject_id`` is the immutable payable ID.
    This contract records the approver's identity, capacity, policy, rationale, revision evaluated, and
    references to supporting evidence. It does not grant release, execution, settlement, or cash-movement power.
    """

    tenant_id: str
    decision_id: str
    subject_type: FinancialApprovalSubjectType
    subject_id: str
    decision: FinancialApprovalDecisionType
    actor_id: str
    actor_capacity: str
    reason: str
    approval_policy_reference: str
    subject_revision: int
    approval_policy_version: Optional[str] = None
    decided_at: datetime = field(default_factory=_utc_now)
    created_at: datetime = field(default_factory=_utc_now)
    evidence_references: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Validates and freezes the complete decision evidence envelope at creation time."""
        object.__setattr__(self, "tenant_id", _required_text(self.tenant_id, "tenant_id", 128))
        object.__setattr__(self, "decision_id", _required_text(self.decision_id, "decision_id", 80))
        object.__setattr__(self, "subject_id", _required_text(self.subject_id, "subject_id", 80))
        object.__setattr__(self, "actor_id", _required_text(self.actor_id, "actor_id", 128))
        object.__setattr__(self, "actor_capacity", _required_text(self.actor_capacity, "actor_capacity", 120))
        object.__setattr__(self, "reason", _required_text(self.reason, "reason", 2_000))
        object.__setattr__(self, "approval_policy_reference", _required_text(self.approval_policy_reference, "approval_policy_reference", 240))
        object.__setattr__(self, "approval_policy_version", _optional_text(self.approval_policy_version, "approval_policy_version", 120))
        if not isinstance(self.subject_type, FinancialApprovalSubjectType):
            raise FinancialApprovalDecisionDomainError("subject_type must use FinancialApprovalSubjectType")
        if not isinstance(self.decision, FinancialApprovalDecisionType):
            raise FinancialApprovalDecisionDomainError("decision must use FinancialApprovalDecisionType")
        if not isinstance(self.subject_revision, int) or isinstance(self.subject_revision, bool) or self.subject_revision < 1:
            raise FinancialApprovalDecisionDomainError("subject_revision must be an integer of at least 1")
        object.__setattr__(self, "decided_at", _aware_utc(self.decided_at, "decided_at"))
        object.__setattr__(self, "created_at", _aware_utc(self.created_at, "created_at"))
        object.__setattr__(self, "evidence_references", _evidence_references(self.evidence_references))

    @classmethod
    def new_id(cls) -> str:
        """Creates an opaque decision identifier without making registry idempotency part of domain state."""
        return str(uuid4())

    def evidence_payload(self) -> Dict[str, Any]:
        """Returns immutable decision evidence without command receipts, release, execution, or settlement data."""
        return {
            "schema": "WILSY-FINANCIAL-APPROVAL-DECISION/V1",
            "tenant_id": self.tenant_id,
            "decision_id": self.decision_id,
            "subject_type": self.subject_type.value,
            "subject_id": self.subject_id,
            "decision": self.decision.value,
            "actor_id": self.actor_id,
            "actor_capacity": self.actor_capacity,
            "reason": self.reason,
            "approval_policy_reference": self.approval_policy_reference,
            "approval_policy_version": self.approval_policy_version,
            "subject_revision": self.subject_revision,
            "decided_at": self.decided_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "evidence_references": list(self.evidence_references),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serializes completed decision evidence without granting any payment or release authority."""
        return self.evidence_payload()
