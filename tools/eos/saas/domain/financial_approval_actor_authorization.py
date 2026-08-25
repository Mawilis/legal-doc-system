# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS – FINANCIAL APPROVAL ACTOR AUTHORIZATION EVIDENCE                                                     ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ VERSION:        v1.0.0-FINANCIAL-APPROVAL-ACTOR-AUTHORIZATION                                                  ║
║ EPITOME:        Immutable tenant-scoped proof of an actor's capacity for one policy requirement and revision.   ║
║ ABSOLUTE PATH:  /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/financial_approval_actor_authorization.py ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

This contract records authorization evidence; it does not authenticate an actor, create an RBAC grant, make an
approval decision, compute an effective approval result, authorize release, authorize execution, or settle payment.
Equality between actor_capacity text and a policy requirement never proves authorization. Distinct-actor counting and
quorum semantics belong to a later aggregator contract.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from .financial_approval_policy_evaluation import FinancialApprovalPolicySubjectType


class FinancialApprovalActorAuthorizationDomainError(ValueError):
    """Raised when immutable actor-authorization evidence is structurally invalid."""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _required_text(value: Any, field_name: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise FinancialApprovalActorAuthorizationDomainError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise FinancialApprovalActorAuthorizationDomainError(f"{field_name} is required")
    if len(normalized) > maximum:
        raise FinancialApprovalActorAuthorizationDomainError(f"{field_name} exceeds {maximum} characters")
    return normalized


def _aware_utc(value: Any, field_name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise FinancialApprovalActorAuthorizationDomainError(f"{field_name} must be a timezone-aware datetime")
    return value.astimezone(timezone.utc)


def _fingerprint(value: Any) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{128}", value) is None:
        raise FinancialApprovalActorAuthorizationDomainError("authorization_evidence_fingerprint must be lowercase SHA3-512 hex")
    return value


@dataclass(frozen=True)
class FinancialApprovalActorAuthorization:
    """Immutable evidence that an actor held a required capacity in one exact policy context.

    The referenced authority remains responsible for authentication and grant semantics. This object only binds
    that evidence to a tenant, VendorBill revision, policy evaluation, requirement lane, actor, and validity window.
    It is not a decision, effective approval, release authorization, execution authorization, or settlement record.
    """

    tenant_id: str
    authorization_id: str
    subject_type: FinancialApprovalPolicySubjectType
    subject_id: str
    subject_revision: int
    evaluation_id: str
    approval_policy_reference: str
    approval_policy_version: str
    requirement_id: str
    actor_id: str
    actor_capacity: str
    authorization_source_reference: str
    authorization_basis_reference: str
    authorized_at: datetime
    authorization_evidence_fingerprint: str
    valid_until: Optional[datetime] = None
    created_at: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        for field_name, maximum in (("tenant_id", 128), ("authorization_id", 80), ("subject_id", 80),
                                    ("evaluation_id", 80), ("approval_policy_reference", 240),
                                    ("approval_policy_version", 120), ("requirement_id", 120),
                                    ("actor_id", 128), ("actor_capacity", 120),
                                    ("authorization_source_reference", 240), ("authorization_basis_reference", 240)):
            object.__setattr__(self, field_name, _required_text(getattr(self, field_name), field_name, maximum))
        if not isinstance(self.subject_type, FinancialApprovalPolicySubjectType):
            raise FinancialApprovalActorAuthorizationDomainError("subject_type must use FinancialApprovalPolicySubjectType")
        if not isinstance(self.subject_revision, int) or isinstance(self.subject_revision, bool) or self.subject_revision < 1:
            raise FinancialApprovalActorAuthorizationDomainError("subject_revision must be an integer of at least 1")
        authorized_at = _aware_utc(self.authorized_at, "authorized_at")
        valid_until = None if self.valid_until is None else _aware_utc(self.valid_until, "valid_until")
        if valid_until is not None and valid_until < authorized_at:
            raise FinancialApprovalActorAuthorizationDomainError("valid_until must be at or after authorized_at")
        object.__setattr__(self, "authorized_at", authorized_at)
        object.__setattr__(self, "valid_until", valid_until)
        object.__setattr__(self, "authorization_evidence_fingerprint", _fingerprint(self.authorization_evidence_fingerprint))
        object.__setattr__(self, "created_at", _aware_utc(self.created_at, "created_at"))

    @classmethod
    def new_id(cls) -> str:
        return str(uuid4())

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "WILSY-FINANCIAL-APPROVAL-ACTOR-AUTHORIZATION/V1",
            "tenant_id": self.tenant_id,
            "authorization_id": self.authorization_id,
            "subject_type": self.subject_type.value,
            "subject_id": self.subject_id,
            "subject_revision": self.subject_revision,
            "evaluation_id": self.evaluation_id,
            "approval_policy_reference": self.approval_policy_reference,
            "approval_policy_version": self.approval_policy_version,
            "requirement_id": self.requirement_id,
            "actor_id": self.actor_id,
            "actor_capacity": self.actor_capacity,
            "authorization_source_reference": self.authorization_source_reference,
            "authorization_basis_reference": self.authorization_basis_reference,
            "authorized_at": self.authorized_at.isoformat(),
            "valid_until": self.valid_until.isoformat() if self.valid_until is not None else None,
            "authorization_evidence_fingerprint": self.authorization_evidence_fingerprint,
            "created_at": self.created_at.isoformat(),
        }
