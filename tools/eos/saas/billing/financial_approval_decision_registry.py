# -*- coding: utf-8 -*-
"""Immutable, tenant-scoped FinancialApprovalDecision persistence; v1.1.0 adds bounded keyset pagination."""

from __future__ import annotations

import hashlib
import json
import re
import base64
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Mapping, Optional, Tuple

from pymongo import ASCENDING, ReturnDocument, WriteConcern
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern

from ...kernel.db import get_database
from ..domain.billing import parse_datetime
from ..domain.financial_approval_decision import FinancialApprovalDecision, FinancialApprovalDecisionDomainError, FinancialApprovalDecisionType, FinancialApprovalSubjectType
from ..domain.vendor_bill import VendorBillObligationState
from .vendor_bill_registry import VENDOR_BILL_COLLECTION, VendorBillNotFoundError, VendorBillPersistedRecordInvalidError, VendorBillRegistry

FINANCIAL_APPROVAL_DECISION_COLLECTION = "financial_approval_decisions"
FINANCIAL_WRITE_CONCERN = WriteConcern(w="majority", j=True, wtimeout=10_000)
FINANCIAL_READ_CONCERN = ReadConcern("majority")
MAX_PAGE_SIZE = 250


class FinancialApprovalDecisionRegistryError(RuntimeError):
    """Base structured error for immutable financial approval decision persistence."""


class FinancialApprovalDecisionPersistedRecordInvalidError(FinancialApprovalDecisionRegistryError):
    """Raised when persisted decision evidence cannot satisfy the canonical domain and receipt contract."""


class FinancialApprovalDecisionIdempotencyKeyReuseError(FinancialApprovalDecisionRegistryError):
    """Raised when an occupied decision identity/key carries a different immutable create command."""


class FinancialApprovalDecisionCreateConflictError(FinancialApprovalDecisionRegistryError):
    """Raised when an occupied decision identity carries a different immutable decision command."""


class FinancialApprovalSubjectRevisionConflictError(FinancialApprovalDecisionRegistryError):
    """Raised when an approval decision is bound to a stale payable revision."""


class FinancialApprovalSubjectIneligibleError(FinancialApprovalDecisionRegistryError):
    """Raised when a valid payable state cannot receive completed approval evidence."""


class FinancialApprovalDecisionCreateOutcome(StrEnum):
    CREATED = "CREATED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


@dataclass(frozen=True)
class FinancialApprovalDecisionCreateResult:
    outcome: FinancialApprovalDecisionCreateOutcome
    decision: FinancialApprovalDecision

@dataclass(frozen=True)
class FinancialApprovalDecisionPage:
    items: Tuple[FinancialApprovalDecision, ...]
    next_cursor: Optional[str]


def _collection_or_raise(collection: Optional[Collection] = None) -> Collection:
    target = collection
    if target is None:
        database = get_database()
        if database is None:
            raise FinancialApprovalDecisionRegistryError("FINANCIAL_APPROVAL_DECISION_PERSISTENCE_UNAVAILABLE")
        target = database[FINANCIAL_APPROVAL_DECISION_COLLECTION]
    return target.with_options(write_concern=FINANCIAL_WRITE_CONCERN, read_concern=FINANCIAL_READ_CONCERN)


def _idempotency_key(value: Any) -> str:
    if not isinstance(value, str):
        raise FinancialApprovalDecisionDomainError("idempotency_key must be a non-empty string of at most 128 characters")
    normalized = value.strip()
    if not normalized or len(normalized) > 128:
        raise FinancialApprovalDecisionDomainError("idempotency_key must be a non-empty string of at most 128 characters")
    return normalized


def _fingerprint(decision: FinancialApprovalDecision, idempotency_key: str) -> str:
    payload = {**decision.evidence_payload(), "idempotency_key": idempotency_key}
    return hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()


def _document(decision: FinancialApprovalDecision, idempotency_key: str, fingerprint: str) -> Dict[str, Any]:
    return {**decision.evidence_payload(), "create_idempotency_key": idempotency_key, "create_fingerprint": fingerprint}


def _persisted_value(document: Mapping[str, Any], field: str) -> Any:
    """Returns a persisted field or a validator-rejected sentinel without weakening strict hydration."""
    return document[field] if field in document else ""


def _hydrate(document: Mapping[str, Any]) -> tuple[FinancialApprovalDecision, str, str]:
    try:
        fingerprint, key = document.get("create_fingerprint"), document.get("create_idempotency_key")
        if not isinstance(fingerprint, str) or re.fullmatch(r"[0-9a-f]{128}", fingerprint) is None:
            raise FinancialApprovalDecisionPersistedRecordInvalidError("FINANCIAL_APPROVAL_DECISION_PERSISTED_RECORD_INVALID")
        key = _idempotency_key(key)
        raw_references = document.get("evidence_references")
        if not isinstance(raw_references, list):
            raise FinancialApprovalDecisionPersistedRecordInvalidError("FINANCIAL_APPROVAL_DECISION_PERSISTED_RECORD_INVALID")
        decision = FinancialApprovalDecision(
            tenant_id=_persisted_value(document, "tenant_id"), decision_id=_persisted_value(document, "decision_id"),
            subject_type=FinancialApprovalSubjectType(_persisted_value(document, "subject_type")), subject_id=_persisted_value(document, "subject_id"),
            decision=FinancialApprovalDecisionType(_persisted_value(document, "decision")), actor_id=_persisted_value(document, "actor_id"),
            actor_capacity=_persisted_value(document, "actor_capacity"), reason=_persisted_value(document, "reason"),
            approval_policy_reference=_persisted_value(document, "approval_policy_reference"), approval_policy_version=document.get("approval_policy_version"),
            subject_revision=_persisted_value(document, "subject_revision"), decided_at=_timestamp(document.get("decided_at")),
            created_at=_timestamp(document.get("created_at")), evidence_references=tuple(raw_references),
        )
        return decision, key, fingerprint
    except (TypeError, ValueError, FinancialApprovalDecisionDomainError) as error:
        if isinstance(error, FinancialApprovalDecisionPersistedRecordInvalidError):
            raise
        raise FinancialApprovalDecisionPersistedRecordInvalidError("FINANCIAL_APPROVAL_DECISION_PERSISTED_RECORD_INVALID") from error


def _timestamp(value: Any) -> datetime:
    parsed = parse_datetime(value)
    if parsed is None or parsed.tzinfo is None:
        raise FinancialApprovalDecisionPersistedRecordInvalidError("FINANCIAL_APPROVAL_DECISION_PERSISTED_RECORD_INVALID")
    return parsed


def _validate_subject(decision: FinancialApprovalDecision, target: Collection) -> None:
    if decision.subject_type is not FinancialApprovalSubjectType.VENDOR_BILL:
        raise FinancialApprovalDecisionRegistryError("FINANCIAL_APPROVAL_SUBJECT_TYPE_UNSUPPORTED")
    bill = VendorBillRegistry.get(decision.tenant_id, decision.subject_id, target.database[VENDOR_BILL_COLLECTION])
    if bill.revision != decision.subject_revision:
        raise FinancialApprovalSubjectRevisionConflictError("FINANCIAL_APPROVAL_SUBJECT_REVISION_CONFLICT")
    if bill.obligation_state is not VendorBillObligationState.OPEN:
        raise FinancialApprovalSubjectIneligibleError("FINANCIAL_APPROVAL_SUBJECT_INELIGIBLE")


class FinancialApprovalDecisionRegistry:
    """Append-only decision evidence registry; it intentionally does not project approval or authorize payment actions."""

    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        target = _collection_or_raise(collection)
        target.create_index([("tenant_id", ASCENDING), ("decision_id", ASCENDING)], unique=True, name="tenant_financial_approval_decision_identity_unique")
        target.create_index([("tenant_id", ASCENDING), ("subject_type", ASCENDING), ("subject_id", ASCENDING)], name="tenant_financial_approval_subject")
        target.create_index([("tenant_id", ASCENDING), ("subject_type", ASCENDING), ("subject_id", ASCENDING), ("created_at", ASCENDING)], name="tenant_financial_approval_subject_created")
        target.create_index([("tenant_id", ASCENDING), ("subject_type", ASCENDING), ("subject_id", ASCENDING), ("created_at", ASCENDING), ("decision_id", ASCENDING)], name="tenant_financial_approval_subject_created_identity")
        target.create_index([("tenant_id", ASCENDING), ("decision", ASCENDING), ("created_at", ASCENDING)], name="tenant_financial_approval_decision_created")
        target.create_index([("tenant_id", ASCENDING), ("actor_id", ASCENDING), ("created_at", ASCENDING)], name="tenant_financial_approval_actor_created")

    @staticmethod
    def create(decision: FinancialApprovalDecision, idempotency_key: str, collection: Optional[Collection] = None) -> FinancialApprovalDecisionCreateResult:
        if not isinstance(decision, FinancialApprovalDecision):
            raise FinancialApprovalDecisionDomainError("decision must be a FinancialApprovalDecision")
        target, key = _collection_or_raise(collection), _idempotency_key(idempotency_key)
        _validate_subject(decision, target)
        fingerprint = _fingerprint(decision, key)
        try:
            target.insert_one(_document(decision, key, fingerprint))
        except DuplicateKeyError as error:
            existing = target.find_one({"tenant_id": decision.tenant_id, "decision_id": decision.decision_id})
            if existing is None:
                raise FinancialApprovalDecisionRegistryError("FINANCIAL_APPROVAL_DECISION_CREATE_RECONCILIATION_FAILED") from error
            persisted, persisted_key, persisted_fingerprint = _hydrate(existing)
            if persisted_key == key and persisted_fingerprint == fingerprint:
                return FinancialApprovalDecisionCreateResult(FinancialApprovalDecisionCreateOutcome.IDEMPOTENT_REPLAY, persisted)
            if persisted_key == key:
                raise FinancialApprovalDecisionIdempotencyKeyReuseError("FINANCIAL_APPROVAL_DECISION_IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_COMMAND") from error
            raise FinancialApprovalDecisionCreateConflictError("FINANCIAL_APPROVAL_DECISION_CREATE_CONFLICT") from error
        except PyMongoError as error:
            raise FinancialApprovalDecisionRegistryError("FINANCIAL_APPROVAL_DECISION_CREATE_FAILED") from error
        return FinancialApprovalDecisionCreateResult(FinancialApprovalDecisionCreateOutcome.CREATED, decision)

    @staticmethod
    def get(tenant_id: str, decision_id: str, collection: Optional[Collection] = None) -> FinancialApprovalDecision:
        document = _collection_or_raise(collection).find_one({"tenant_id": str(tenant_id).strip(), "decision_id": str(decision_id).strip()})
        if document is None:
            raise FinancialApprovalDecisionRegistryError("FINANCIAL_APPROVAL_DECISION_NOT_FOUND")
        return _hydrate(document)[0]

    @staticmethod
    def list_for_subject(tenant_id: str, subject_type: FinancialApprovalSubjectType, subject_id: str, limit: int = 100, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> List[FinancialApprovalDecision]:
        if not isinstance(subject_type, FinancialApprovalSubjectType):
            raise FinancialApprovalDecisionDomainError("subject_type must use FinancialApprovalSubjectType")
        bounded = min(max(int(limit), 1), MAX_PAGE_SIZE)
        rows = _collection_or_raise(collection).find({"tenant_id": str(tenant_id).strip(), "subject_type": subject_type.value, "subject_id": str(subject_id).strip()}, session=session).sort([("created_at", ASCENDING), ("decision_id", ASCENDING)]).limit(bounded)
        return [_hydrate(row)[0] for row in rows]

    @staticmethod
    def list_for_subject_page(tenant_id: str, subject_type: FinancialApprovalSubjectType, subject_id: str, page_size: int = MAX_PAGE_SIZE, cursor: Optional[str] = None, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> FinancialApprovalDecisionPage:
        if not isinstance(subject_type, FinancialApprovalSubjectType):
            raise FinancialApprovalDecisionDomainError("subject_type must use FinancialApprovalSubjectType")
        if not isinstance(page_size, int) or isinstance(page_size, bool) or page_size < 1 or page_size > MAX_PAGE_SIZE:
            raise FinancialApprovalDecisionDomainError("page_size must be an integer between 1 and 250")
        predicate: Dict[str, Any] = {"tenant_id": str(tenant_id).strip(), "subject_type": subject_type.value, "subject_id": str(subject_id).strip()}
        if cursor is not None:
            if not isinstance(cursor, str) or not cursor.strip() or len(cursor) > 512:
                raise FinancialApprovalDecisionDomainError("cursor is invalid")
            try:
                raw = base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")
                payload = json.loads(raw)
                if not isinstance(payload, dict) or set(payload) != {"created_at", "decision_id"} or not isinstance(payload["created_at"], str) or not isinstance(payload["decision_id"], str) or not payload["decision_id"].strip():
                    raise ValueError("cursor shape")
                _timestamp(payload["created_at"])
                created_at = payload["created_at"]
                predicate["$or"] = [{"created_at": {"$gt": created_at}}, {"created_at": created_at, "decision_id": {"$gt": payload["decision_id"]}}]
            except Exception as error:
                raise FinancialApprovalDecisionDomainError("cursor is invalid") from error
        rows = list(_collection_or_raise(collection).find(predicate, session=session).sort([("created_at", ASCENDING), ("decision_id", ASCENDING)]).limit(page_size + 1))
        items = tuple(_hydrate(row)[0] for row in rows[:page_size])
        next_cursor = None
        if len(rows) > page_size:
            last = items[-1]
            next_cursor = base64.urlsafe_b64encode(json.dumps({"created_at": last.created_at.isoformat(), "decision_id": last.decision_id}, separators=(",", ":")).encode()).decode()
        return FinancialApprovalDecisionPage(items=items, next_cursor=next_cursor)
