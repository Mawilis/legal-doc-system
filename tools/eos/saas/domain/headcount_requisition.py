"""Governed WILSY workforce headcount requisition domain.

This domain models headcount approval only. It does not create candidates,
offers, employee records, global principals, tenant memberships, capacities,
IAM grants, payroll commitments, or financial execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Final


VERSION: Final[str] = "v1.0.0-HR-HEADCOUNT-REQUISITION"
SCHEMA: Final[str] = "wilsy.hr.headcount_requisition.v1"
_HEX_512 = re.compile(r"^[0-9a-f]{128}$")


class RequisitionError(ValueError):
    """Invalid requisition state or transition."""


class RequisitionStatus(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class RequisitionDecision(StrEnum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"


def _required(name: str, value: object, *, maximum: int = 180) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > maximum:
        raise RequisitionError(f"REQUISITION_{name.upper()}_INVALID")
    return value


def _timestamp(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise RequisitionError("REQUISITION_TIMESTAMP_MUST_BE_TIMEZONE_AWARE")
    return value.astimezone(timezone.utc)


def _parse_timestamp(value: object) -> datetime:
    if isinstance(value, datetime):
        return _timestamp(value)
    if isinstance(value, str):
        try:
            return _timestamp(datetime.fromisoformat(value))
        except ValueError as error:
            raise RequisitionError("REQUISITION_TIMESTAMP_INVALID") from error
    raise RequisitionError("REQUISITION_TIMESTAMP_INVALID")


@dataclass(frozen=True, slots=True)
class HeadcountApproval:
    decision_id: str
    actor_principal_id: str
    decision: RequisitionDecision | str
    reason: str
    decided_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "decision_id", _required("decision_id", self.decision_id))
        object.__setattr__(self, "actor_principal_id", _required("approver", self.actor_principal_id))
        object.__setattr__(self, "reason", _required("decision_reason", self.reason, maximum=2000))
        try:
            decision = RequisitionDecision(self.decision)
        except (TypeError, ValueError) as error:
            raise RequisitionError("REQUISITION_DECISION_INVALID") from error
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "decided_at", _timestamp(self.decided_at))


@dataclass(frozen=True, slots=True)
class HeadcountRequisition:
    tenant_id: str
    requisition_id: str
    department_id: str
    position_title: str
    employment_type: str
    work_location: str
    headcount: int
    business_justification: str
    requested_by_principal_id: str
    status: RequisitionStatus | str = RequisitionStatus.DRAFT
    approval: HeadcountApproval | None = None
    submitted_by_principal_id: str | None = None
    submitted_at: datetime | None = None
    revision: int = 1
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        for name in ("tenant_id", "requisition_id", "department_id", "position_title",
                     "employment_type", "work_location", "requested_by_principal_id"):
            object.__setattr__(self, name, _required(name, getattr(self, name)))
        object.__setattr__(self, "business_justification",
                           _required("business_justification", self.business_justification, maximum=4000))
        if isinstance(self.headcount, bool) or not isinstance(self.headcount, int) or not 1 <= self.headcount <= 50:
            raise RequisitionError("REQUISITION_HEADCOUNT_OUT_OF_RANGE")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 1:
            raise RequisitionError("REQUISITION_REVISION_INVALID")
        try:
            status = RequisitionStatus(self.status)
        except (TypeError, ValueError) as error:
            raise RequisitionError("REQUISITION_STATUS_INVALID") from error
        object.__setattr__(self, "status", status)
        if self.schema != SCHEMA or self.version != VERSION:
            raise RequisitionError("REQUISITION_SCHEMA_VERSION_INVALID")
        if status is RequisitionStatus.SUBMITTED and (self.submitted_by_principal_id is None or self.submitted_at is None):
            raise RequisitionError("REQUISITION_SUBMISSION_EVIDENCE_REQUIRED")
        if status is RequisitionStatus.DRAFT and (self.submitted_by_principal_id is not None or self.submitted_at is not None):
            raise RequisitionError("REQUISITION_SUBMISSION_EVIDENCE_NOT_ALLOWED")
        if self.submitted_by_principal_id is not None:
            object.__setattr__(self, "submitted_by_principal_id", _required("submitter", self.submitted_by_principal_id))
            object.__setattr__(self, "submitted_at", _timestamp(self.submitted_at))
        if status in {RequisitionStatus.APPROVED, RequisitionStatus.REJECTED}:
            if self.submitted_by_principal_id is None or self.submitted_at is None:
                raise RequisitionError("REQUISITION_SUBMISSION_EVIDENCE_REQUIRED")
            if self.approval is None:
                raise RequisitionError("REQUISITION_DECISION_EVIDENCE_REQUIRED")
            if self.approval.actor_principal_id in {self.requested_by_principal_id, self.submitted_by_principal_id}:
                raise RequisitionError("REQUISITION_MAKER_CHECKER_VIOLATION")
            expected = RequisitionDecision.APPROVE if status is RequisitionStatus.APPROVED else RequisitionDecision.REJECT
            if self.approval.decision is not expected:
                raise RequisitionError("REQUISITION_DECISION_STATUS_MISMATCH")
        elif self.approval is not None:
            raise RequisitionError("REQUISITION_DECISION_NOT_VALID_FOR_STATUS")
        digest = self._digest()
        if self.fingerprint and (not _HEX_512.fullmatch(self.fingerprint) or not hmac.compare_digest(self.fingerprint, digest)):
            raise RequisitionError("REQUISITION_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def _payload(self) -> dict[str, object]:
        approval = None if self.approval is None else {
            "decision_id": self.approval.decision_id,
            "actor_principal_id": self.approval.actor_principal_id,
            "decision": self.approval.decision.value,
            "reason": self.approval.reason,
            "decided_at": self.approval.decided_at.isoformat(),
        }
        return {
            "tenant_id": self.tenant_id, "requisition_id": self.requisition_id,
            "department_id": self.department_id, "position_title": self.position_title,
            "employment_type": self.employment_type, "work_location": self.work_location,
            "headcount": self.headcount, "business_justification": self.business_justification,
            "requested_by_principal_id": self.requested_by_principal_id,
            "status": self.status.value, "approval": approval,
            "submitted_by_principal_id": self.submitted_by_principal_id,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "revision": self.revision,
            "schema": self.schema, "version": self.version,
        }

    def _digest(self) -> str:
        return hashlib.sha3_512(json.dumps(self._payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def to_dict(self) -> dict[str, object]:
        return {**self._payload(), "fingerprint": self.fingerprint}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "HeadcountRequisition":
        expected = {
            "tenant_id", "requisition_id", "department_id", "position_title",
            "employment_type", "work_location", "headcount", "business_justification",
            "requested_by_principal_id", "status", "approval",
            "submitted_by_principal_id", "submitted_at", "revision",
            "schema", "version", "fingerprint",
        }
        if not isinstance(payload, dict) or set(payload) != expected:
            raise RequisitionError("REQUISITION_PERSISTED_SCHEMA_INVALID")
        values = dict(payload)
        approval_data = values.pop("approval")
        if approval_data is not None:
            if not isinstance(approval_data, dict) or set(approval_data) != {
                "decision_id", "actor_principal_id", "decision", "reason", "decided_at"
            }:
                raise RequisitionError("REQUISITION_APPROVAL_SCHEMA_INVALID")
            approval_values = dict(approval_data)
            approval_values["decided_at"] = _parse_timestamp(approval_values["decided_at"])
            values["approval"] = HeadcountApproval(**approval_values)
        submitted_at = values.get("submitted_at")
        values["submitted_at"] = None if submitted_at is None else _parse_timestamp(submitted_at)
        try:
            return cls(**values)
        except TypeError as error:
            raise RequisitionError("REQUISITION_PERSISTED_SCHEMA_INVALID") from error

    def submit(self, *, actor_principal_id: str, submitted_at: datetime, expected_revision: int) -> "HeadcountRequisition":
        self._expect_revision(expected_revision)
        if self.status is not RequisitionStatus.DRAFT:
            raise RequisitionError("REQUISITION_ONLY_DRAFT_CAN_BE_SUBMITTED")
        actor = _required("submitter", actor_principal_id)
        if actor != self.requested_by_principal_id:
            raise RequisitionError("REQUISITION_SUBMISSION_ACTOR_MISMATCH")
        return HeadcountRequisition(
            tenant_id=self.tenant_id, requisition_id=self.requisition_id,
            department_id=self.department_id, position_title=self.position_title,
            employment_type=self.employment_type, work_location=self.work_location,
            headcount=self.headcount, business_justification=self.business_justification,
            requested_by_principal_id=self.requested_by_principal_id,
            status=RequisitionStatus.SUBMITTED, submitted_by_principal_id=actor,
            submitted_at=submitted_at, revision=self.revision + 1,
        )

    def decide(self, approval: HeadcountApproval, *, expected_revision: int) -> "HeadcountRequisition":
        self._expect_revision(expected_revision)
        if self.status is not RequisitionStatus.SUBMITTED:
            raise RequisitionError("REQUISITION_ONLY_SUBMITTED_CAN_BE_DECIDED")
        if approval.actor_principal_id in {self.requested_by_principal_id, self.submitted_by_principal_id}:
            raise RequisitionError("REQUISITION_MAKER_CHECKER_VIOLATION")
        status = RequisitionStatus.APPROVED if approval.decision is RequisitionDecision.APPROVE else RequisitionStatus.REJECTED
        return HeadcountRequisition(
            tenant_id=self.tenant_id, requisition_id=self.requisition_id,
            department_id=self.department_id, position_title=self.position_title,
            employment_type=self.employment_type, work_location=self.work_location,
            headcount=self.headcount, business_justification=self.business_justification,
            requested_by_principal_id=self.requested_by_principal_id, status=status,
            approval=approval, submitted_by_principal_id=self.submitted_by_principal_id,
            submitted_at=self.submitted_at, revision=self.revision + 1,
        )

    def _expect_revision(self, expected_revision: int) -> None:
        if expected_revision != self.revision:
            raise RequisitionError("REQUISITION_REVISION_CONFLICT")


__all__ = ["VERSION", "SCHEMA", "HeadcountApproval", "HeadcountRequisition",
           "RequisitionDecision", "RequisitionError", "RequisitionStatus"]
