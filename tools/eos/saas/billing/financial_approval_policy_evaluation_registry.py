# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS – FINANCIAL APPROVAL POLICY EVALUATION REGISTRY FOUNDATION                                              ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ VERSION:        v1.4.1-POLICY-EVALUATION-SHARED-SESSION-READ                                                   ║
║ EPITOME:        Frozen tenant-scoped immutable policy-evaluation evidence and VendorBill snapshot binding.      ║
║ BIBLICAL ANCHOR: Psalm 1:3 — "And he shall be like a tree planted by the rivers of water..."                  ║
║ ABSOLUTE PATH:  /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/financial_approval_policy_evaluation_registry.py ║
║ COLLABORATION:  Wilson Khanyezi (Founder/Chief Architect) mandated AP policy/evidence separation.               ║
║                 AI Engineering (Codex) established deterministic snapshot evidence only.                        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

This frozen registry owns immutable policy-evaluation evidence, tenant-scoped persistence and retrieval, subject
snapshot/revision validation, and create idempotency. It does not select policy, authorize actors, aggregate
decisions, project approval onto VendorBills, authorize release, invoke Kennel EOS, execute payment, or settle.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from typing import Mapping, Optional, Sequence
from typing import Any, Dict
from pymongo import ASCENDING, WriteConcern
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.read_concern import ReadConcern
from pymongo.errors import DuplicateKeyError, PyMongoError
from dataclasses import dataclass
from enum import StrEnum

from ...kernel.db import get_database
from ..domain.billing import parse_datetime
from ..domain.financial_approval_policy_evaluation import FinancialApprovalPolicyEvaluation, FinancialApprovalPolicyEvaluationDomainError, FinancialApprovalRequirement, FinancialApprovalPolicySubjectType, FinancialApprovalRejectionRule
from ..domain.vendor_bill import VendorBill, VendorBillObligationState
from .vendor_bill_registry import VENDOR_BILL_COLLECTION, VendorBillRegistry

FINANCIAL_APPROVAL_POLICY_EVALUATION_COLLECTION = "financial_approval_policy_evaluations"
FINANCIAL_APPROVAL_POLICY_EVALUATION_MAX_LIST_LIMIT = 250
FINANCIAL_WRITE_CONCERN = WriteConcern(w="majority", j=True, wtimeout=10_000)
FINANCIAL_READ_CONCERN = ReadConcern("majority")


class FinancialApprovalPolicyEvaluationRegistryError(RuntimeError):
    """Base structured failure for future immutable financial approval policy-evaluation persistence."""


class FinancialApprovalPolicyEvaluationPersistedRecordInvalidError(FinancialApprovalPolicyEvaluationRegistryError):
    """Raised when persisted policy-evaluation truth cannot be canonically trusted."""


class FinancialApprovalPolicySubjectRevisionConflictError(FinancialApprovalPolicyEvaluationRegistryError):
    """Raised when a policy evaluation is bound to a stale VendorBill revision."""


class FinancialApprovalPolicySubjectSnapshotMismatchError(FinancialApprovalPolicyEvaluationRegistryError):
    """Raised when the supplied policy-evaluation snapshot does not match canonical VendorBill truth."""


class FinancialApprovalPolicyReferenceMismatchError(FinancialApprovalPolicyEvaluationRegistryError):
    """Raised when an evaluation policy reference differs from the subject VendorBill policy reference."""


class FinancialApprovalPolicySubjectIneligibleError(FinancialApprovalPolicyEvaluationRegistryError):
    """Raised when a VendorBill state is not eligible for policy evaluation."""

class FinancialApprovalPolicyEvaluationCreateConflictError(FinancialApprovalPolicyEvaluationRegistryError): pass
class FinancialApprovalPolicyEvaluationIdempotencyKeyReuseError(FinancialApprovalPolicyEvaluationRegistryError): pass
class FinancialApprovalPolicyEvaluationNotFoundError(FinancialApprovalPolicyEvaluationRegistryError): pass
class FinancialApprovalPolicyEvaluationCreateOutcome(StrEnum):
    CREATED = "CREATED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"
@dataclass(frozen=True)
class FinancialApprovalPolicyEvaluationCreateResult:
    outcome: FinancialApprovalPolicyEvaluationCreateOutcome
    evaluation: FinancialApprovalPolicyEvaluation


def _collection_or_raise(collection: Optional[Collection] = None) -> Collection:
    target = collection
    if target is None:
        database = get_database()
        if database is None:
            raise FinancialApprovalPolicyEvaluationRegistryError("FINANCIAL_APPROVAL_POLICY_EVALUATION_PERSISTENCE_UNAVAILABLE")
        target = database[FINANCIAL_APPROVAL_POLICY_EVALUATION_COLLECTION]
    return target.with_options(write_concern=FINANCIAL_WRITE_CONCERN, read_concern=FINANCIAL_READ_CONCERN)


def _timestamp(value: Any) -> datetime:
    parsed = parse_datetime(value)
    if parsed is None or parsed.tzinfo is None:
        raise FinancialApprovalPolicyEvaluationPersistedRecordInvalidError("FINANCIAL_APPROVAL_POLICY_EVALUATION_PERSISTED_RECORD_INVALID")
    return parsed


def _required(document: Mapping[str, Any], field: str) -> Any:
    if field not in document:
        raise FinancialApprovalPolicyEvaluationPersistedRecordInvalidError("FINANCIAL_APPROVAL_POLICY_EVALUATION_PERSISTED_RECORD_INVALID")
    return document[field]


def _hydrate_persisted_evaluation(document: Mapping[str, Any]) -> FinancialApprovalPolicyEvaluation:
    """Strictly hydrates canonical ISO-timestamp persisted evaluation evidence; unknown fields follow billing registries and are ignored."""
    try:
        fingerprint, key = _required(document, "create_fingerprint"), _required(document, "create_idempotency_key")
        if not isinstance(fingerprint, str) or re.fullmatch(r"[0-9a-f]{128}", fingerprint) is None or not isinstance(key, str) or not key.strip() or len(key) > 128 or key != key.strip():
            raise FinancialApprovalPolicyEvaluationPersistedRecordInvalidError("FINANCIAL_APPROVAL_POLICY_EVALUATION_PERSISTED_RECORD_INVALID")
        raw_requirements = _required(document, "approval_requirements")
        if not isinstance(raw_requirements, list):
            raise FinancialApprovalPolicyEvaluationPersistedRecordInvalidError("FINANCIAL_APPROVAL_POLICY_EVALUATION_PERSISTED_RECORD_INVALID")
        requirements = tuple(FinancialApprovalRequirement(**item) if isinstance(item, dict) and set(item) == {"requirement_id", "actor_capacity", "approvals_required"} else (_ for _ in ()).throw(FinancialApprovalPolicyEvaluationPersistedRecordInvalidError("FINANCIAL_APPROVAL_POLICY_EVALUATION_PERSISTED_RECORD_INVALID")) for item in raw_requirements)
        return FinancialApprovalPolicyEvaluation(tenant_id=_required(document,"tenant_id"), evaluation_id=_required(document,"evaluation_id"), subject_type=FinancialApprovalPolicySubjectType(_required(document,"subject_type")), subject_id=_required(document,"subject_id"), subject_revision=_required(document,"subject_revision"), approval_policy_reference=_required(document,"approval_policy_reference"), approval_policy_version=_required(document,"approval_policy_version"), approval_required=_required(document,"approval_required"), approval_requirements=requirements, rejection_rule=FinancialApprovalRejectionRule(_required(document,"rejection_rule")), rejections_required=_required(document,"rejections_required"), subject_snapshot_fingerprint=_required(document,"subject_snapshot_fingerprint"), evaluator_reference=_required(document,"evaluator_reference"), evaluated_at=_timestamp(_required(document,"evaluated_at")), created_at=_timestamp(_required(document,"created_at")))
    except (TypeError, ValueError, FinancialApprovalPolicyEvaluationDomainError) as error:
        if isinstance(error, FinancialApprovalPolicyEvaluationPersistedRecordInvalidError):
            raise
        raise FinancialApprovalPolicyEvaluationPersistedRecordInvalidError("FINANCIAL_APPROVAL_POLICY_EVALUATION_PERSISTED_RECORD_INVALID") from error


class FinancialApprovalPolicyEvaluationRegistry:
    """Collection/index and strict-hydration foundation; create/read/list are intentionally introduced in later slices."""
    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        target = _collection_or_raise(collection)
        target.create_index([("tenant_id", ASCENDING), ("evaluation_id", ASCENDING)], unique=True, name="tenant_financial_approval_policy_evaluation_identity_unique")
        target.create_index([("tenant_id", ASCENDING), ("subject_type", ASCENDING), ("subject_id", ASCENDING)], name="tenant_financial_approval_policy_subject")
        target.create_index([("tenant_id", ASCENDING), ("subject_type", ASCENDING), ("subject_id", ASCENDING), ("subject_revision", ASCENDING), ("created_at", ASCENDING)], name="tenant_financial_approval_policy_subject_revision_created")
        target.create_index([("tenant_id", ASCENDING), ("approval_policy_reference", ASCENDING), ("approval_policy_version", ASCENDING), ("created_at", ASCENDING)], name="tenant_financial_approval_policy_reference_version_created")
        target.create_index([("tenant_id", ASCENDING), ("created_at", ASCENDING)], name="tenant_financial_approval_policy_created")

    @staticmethod
    def create(evaluation: FinancialApprovalPolicyEvaluation, idempotency_key: str, collection: Optional[Collection] = None) -> FinancialApprovalPolicyEvaluationCreateResult:
        if not isinstance(evaluation, FinancialApprovalPolicyEvaluation): raise FinancialApprovalPolicyEvaluationDomainError("evaluation must be a FinancialApprovalPolicyEvaluation")
        if not isinstance(idempotency_key, str) or not idempotency_key.strip() or len(idempotency_key.strip()) > 128: raise FinancialApprovalPolicyEvaluationDomainError("idempotency_key must be a non-empty string of at most 128 characters")
        target, key = _collection_or_raise(collection), idempotency_key.strip()
        bill = VendorBillRegistry.get(evaluation.tenant_id, evaluation.subject_id, target.database[VENDOR_BILL_COLLECTION])
        if bill.revision != evaluation.subject_revision: raise FinancialApprovalPolicySubjectRevisionConflictError("FINANCIAL_APPROVAL_POLICY_SUBJECT_REVISION_CONFLICT")
        if bill.obligation_state is not VendorBillObligationState.OPEN: raise FinancialApprovalPolicySubjectIneligibleError("FINANCIAL_APPROVAL_POLICY_SUBJECT_INELIGIBLE")
        if not bill.approval_policy_reference or bill.approval_policy_reference != evaluation.approval_policy_reference: raise FinancialApprovalPolicyReferenceMismatchError("FINANCIAL_APPROVAL_POLICY_REFERENCE_MISMATCH")
        if _compute_vendor_bill_policy_snapshot_fingerprint(bill) != evaluation.subject_snapshot_fingerprint: raise FinancialApprovalPolicySubjectSnapshotMismatchError("FINANCIAL_APPROVAL_POLICY_SUBJECT_SNAPSHOT_MISMATCH")
        document = {**evaluation.to_dict(), "create_idempotency_key": key}
        document["create_fingerprint"] = hashlib.sha3_512(json.dumps({**evaluation.to_dict(), "idempotency_key": key}, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()
        try: target.insert_one(document)
        except DuplicateKeyError as error:
            persisted = target.find_one({"tenant_id": evaluation.tenant_id, "evaluation_id": evaluation.evaluation_id})
            if persisted is None:
                raise FinancialApprovalPolicyEvaluationCreateConflictError("FINANCIAL_APPROVAL_POLICY_EVALUATION_CREATE_CONFLICT") from error
            persisted_evaluation = _hydrate_persisted_evaluation(persisted)
            persisted_fingerprint = persisted.get("create_fingerprint")
            persisted_key = persisted.get("create_idempotency_key")
            if persisted_key == key and persisted_fingerprint == document["create_fingerprint"]:
                return FinancialApprovalPolicyEvaluationCreateResult(FinancialApprovalPolicyEvaluationCreateOutcome.IDEMPOTENT_REPLAY, persisted_evaluation)
            if persisted_key == key:
                raise FinancialApprovalPolicyEvaluationIdempotencyKeyReuseError("FINANCIAL_APPROVAL_POLICY_EVALUATION_IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_COMMAND") from error
            raise FinancialApprovalPolicyEvaluationCreateConflictError("FINANCIAL_APPROVAL_POLICY_EVALUATION_CREATE_CONFLICT") from error
        except PyMongoError as error: raise FinancialApprovalPolicyEvaluationRegistryError("FINANCIAL_APPROVAL_POLICY_EVALUATION_CREATE_FAILED") from error
        return FinancialApprovalPolicyEvaluationCreateResult(FinancialApprovalPolicyEvaluationCreateOutcome.CREATED, evaluation)

    @staticmethod
    def get(tenant_id: str, evaluation_id: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> FinancialApprovalPolicyEvaluation:
        if not isinstance(tenant_id, str) or not tenant_id.strip() or not isinstance(evaluation_id, str) or not evaluation_id.strip():
            raise FinancialApprovalPolicyEvaluationDomainError("tenant_id and evaluation_id are required strings")
        document = _collection_or_raise(collection).find_one({"tenant_id": tenant_id.strip(), "evaluation_id": evaluation_id.strip()}, session=session)
        if document is None:
            raise FinancialApprovalPolicyEvaluationNotFoundError("FINANCIAL_APPROVAL_POLICY_EVALUATION_NOT_FOUND")
        return _hydrate_persisted_evaluation(document)

    @staticmethod
    def list_for_subject(tenant_id: str, subject_type: FinancialApprovalPolicySubjectType, subject_id: str, limit: int = 100, collection: Optional[Collection] = None) -> Sequence[FinancialApprovalPolicyEvaluation]:
        if not isinstance(tenant_id, str) or not tenant_id.strip() or not isinstance(subject_id, str) or not subject_id.strip():
            raise FinancialApprovalPolicyEvaluationDomainError("tenant_id and subject_id are required strings")
        if not isinstance(subject_type, FinancialApprovalPolicySubjectType):
            raise FinancialApprovalPolicyEvaluationDomainError("subject_type must use FinancialApprovalPolicySubjectType")
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1 or limit > FINANCIAL_APPROVAL_POLICY_EVALUATION_MAX_LIST_LIMIT:
            raise FinancialApprovalPolicyEvaluationDomainError(f"limit must be an integer from 1 to {FINANCIAL_APPROVAL_POLICY_EVALUATION_MAX_LIST_LIMIT}")
        rows = _collection_or_raise(collection).find({"tenant_id": tenant_id.strip(), "subject_type": subject_type.value, "subject_id": subject_id.strip()}).sort([("created_at", -1), ("evaluation_id", 1)]).limit(limit)
        return tuple(_hydrate_persisted_evaluation(row) for row in rows)


def _serialize_vendor_bill_policy_snapshot(bill: VendorBill) -> str:
    """Serializes only policy-relevant VendorBill truth in stable canonical JSON, excluding storage metadata."""
    if not isinstance(bill, VendorBill):
        raise TypeError("bill must be a VendorBill")
    payload: Dict[str, Any] = {
        "tenant_id": bill.tenant_id,
        "payable_id": bill.payable_id,
        "vendor_id": bill.vendor_id,
        "currency": bill.currency,
        "gross_amount_minor": bill.gross_amount_minor,
        "outstanding_amount_minor": bill.outstanding_amount_minor,
        "issue_date": bill.issue_date.isoformat(),
        "received_at": bill.received_at.isoformat(),
        "due_date": bill.due_date.isoformat(),
        "obligation_state": bill.obligation_state.value,
        "approval_policy_reference": bill.approval_policy_reference,
        "revision": bill.revision,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _compute_vendor_bill_policy_snapshot_fingerprint(bill: VendorBill) -> str:
    """Returns lowercase SHA3-512 evidence for canonical policy-relevant VendorBill truth."""
    return hashlib.sha3_512(_serialize_vendor_bill_policy_snapshot(bill).encode("utf-8")).hexdigest()
