# -*- coding: utf-8 -*-
"""WILSY OS — CANONICAL VENDORBILL REGISTRY

TITLE: Tenant-scoped VendorBill persistence and coordination boundary
VERSION: v1.4.0-RELEASE-AUTHORITY-GUARD-CAS
AUTHORITY: Wilsy OS Core Governance
EPITOME: Owns obligation truth, approval projection coordination, durable
idempotency evidence, and release-authority guard coordination. Execution and
settlement remain exclusively outside this registry and belong to Kennel EOS.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/vendor_bill_registry.py
COLLABORATION: Wilson Khanyezi (Founder/Chief Architect) and AI Engineering (Codex)
CERTIFICATION DATE: 2026-08-27
CHANGELOG: v1.4.0-RELEASE-AUTHORITY-GUARD-CAS — sovereign artifact structural
certification; preserves post-CAS durable receipt reconciliation semantics.
COMPLIANCE: POPIA §19 | GDPR Article 32 | SOC 2 CC7.2; fail-closed validation,
tenant isolation, majority/journal durability, structured errors, SHA3-512
fingerprints, and caller-owned transaction boundaries.
FINANCIAL BOUNDARY: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED.
No payment destination, bank, provider, settlement, or paid-state authority.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Any, Dict, List, Mapping, Optional

from pymongo import ASCENDING, DESCENDING, ReturnDocument, WriteConcern
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern

from ...kernel.db import get_database
from ..domain.billing import parse_datetime
from ..domain.vendor_bill import VendorBill, VendorBillApprovalState, VendorBillDomainError, VendorBillObligationState
from .vendor_registry import VENDOR_COLLECTION

VENDOR_BILL_COLLECTION = "vendor_bills"
FINANCIAL_WRITE_CONCERN = WriteConcern(w="majority", j=True, wtimeout=10_000)
FINANCIAL_READ_CONCERN = ReadConcern("majority")


class VendorBillRegistryError(RuntimeError):
    """Base structured persistence failure for the canonical VendorBill registry."""


class VendorBillNotFoundError(VendorBillRegistryError):
    """Raised without cross-tenant disclosure when a tenant-local VendorBill is absent."""


class VendorBillPersistedRecordInvalidError(VendorBillRegistryError):
    """Raised when stored BSON cannot prove the canonical VendorBill contract."""


class VendorBillAlreadyExistsError(VendorBillRegistryError):
    """Raised when a tenant attempts to create a duplicate payable identity."""


class VendorBillVendorNotFoundError(VendorBillRegistryError):
    """Raised when a bill references no Vendor owned by the requesting tenant."""


class VendorBillRevisionConflictError(VendorBillRegistryError):
    """Raised when a VendorBill mutation loses its tenant-scoped optimistic concurrency predicate."""

class VendorBillApprovalProjectionConflictError(VendorBillRegistryError):
    """Raised when an approval projection loses its obligation/projection CAS."""

class VendorBillApprovalProjectionReferenceError(VendorBillRegistryError):
    """Raised when an immutable effective result is not bound to this VendorBill."""


class VendorBillReleaseAuthorityGuardConflictError(VendorBillRegistryError):
    """Raised when release-authority freshness or lifecycle predicates fail."""

class VendorBillApprovalProjectionIdempotencyKeyReuseError(VendorBillRegistryError):
    """Raised when a projection idempotency key is reused for a different command."""


class VendorBillCreateConflictError(VendorBillRegistryError):
    """Raised when an existing payable identity carries different immutable creation evidence."""


class VendorBillIdempotencyKeyReuseError(VendorBillRegistryError):
    """Raised when one caller-owned idempotency key is reused for a different OPEN_BILL command."""


class VendorBillCreateOutcome(StrEnum):
    CREATED = "CREATED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


@dataclass(frozen=True)
class VendorBillCreateResult:
    outcome: VendorBillCreateOutcome
    vendor_bill: VendorBill
    payable_id: str
    create_fingerprint: str


class VendorBillMutationOutcome(StrEnum):
    """Discriminates an OPEN_BILL commit from a durable exact-command replay."""
    COMMITTED = "COMMITTED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


@dataclass(frozen=True)
class VendorBillMutationResult:
    """Returns canonical persisted VendorBill truth for a commit or its exact durable replay."""
    outcome: VendorBillMutationOutcome
    vendor_bill: VendorBill
    committed_revision: int
    current_revision: int
    idempotency_key: str

    @property
    def revision(self) -> int:
        """Provides read-only compatibility for callers that consume a revision directly."""
        return self.vendor_bill.revision


def _create_fingerprint(bill: VendorBill) -> str:
    """Seals only caller-controlled VendorBill creation semantics with canonical SHA3-512 JSON."""
    payload = {"tenant_id": bill.tenant_id, "payable_id": bill.payable_id, "vendor_id": bill.vendor_id, "vendor_reference": bill.vendor_reference, "source_document_reference": bill.source_document_reference, "currency": bill.currency, "gross_amount_minor": bill.gross_amount_minor, "outstanding_amount_minor": bill.outstanding_amount_minor, "issue_date": bill.issue_date.isoformat(), "received_at": bill.received_at.astimezone().isoformat(), "due_date": bill.due_date.isoformat(), "obligation_state": bill.obligation_state.value, "approval_state": bill.approval_state.value, "approval_policy_reference": bill.approval_policy_reference}
    return hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()


def _open_bill_command_receipt(tenant_id: str, payable_id: str, expected_revision: int, idempotency_key: str) -> Dict[str, Any]:
    """Builds immutable caller-command evidence for the one explicit DRAFT-to-OPEN mutation."""
    key = idempotency_key.strip() if isinstance(idempotency_key, str) else ""
    if not key or len(key) > 128:
        raise VendorBillDomainError("idempotency_key must be a non-empty string of at most 128 characters")
    payload = {"tenant_id": tenant_id, "payable_id": payable_id, "expected_revision": expected_revision, "operation": "OPEN_BILL", "idempotency_key": key}
    fingerprint = hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()
    return {"tenant_id": tenant_id, "payable_id": payable_id, "operation": "OPEN_BILL", "idempotency_key": key, "command_fingerprint": fingerprint, "expected_revision": expected_revision}


def _hydrate_command_receipts(document: Mapping[str, Any], current_revision: int) -> List[Dict[str, Any]]:
    """Validates durable VendorBill command evidence before replay or conflict classification consumes it."""
    raw = document.get("command_receipts", [])
    if not isinstance(raw, list):
        raise VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID")
    receipts: List[Dict[str, Any]] = []
    seen_keys = set()
    for item in raw:
        if not isinstance(item, dict):
            raise VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID")
        tenant_id, payable_id, operation = item.get("tenant_id"), item.get("payable_id"), item.get("operation")
        key, fingerprint = item.get("idempotency_key"), item.get("command_fingerprint")
        expected, committed = item.get("expected_revision"), item.get("committed_revision")
        projection_revision = item.get("expected_approval_projection_revision")
        if (tenant_id != document.get("tenant_id") or payable_id != document.get("payable_id") or operation not in {"OPEN_BILL", "PROJECT_FINANCIAL_APPROVAL_RESULT"}
                or not isinstance(key, str) or not key.strip() or len(key) > 128 or key in seen_keys
                or not isinstance(fingerprint, str) or re.fullmatch(r"[0-9a-f]{128}", fingerprint) is None
                or not isinstance(expected, int) or isinstance(expected, bool) or expected < 1
                or not isinstance(committed, int) or isinstance(committed, bool)
                or (operation == "OPEN_BILL" and (committed != expected + 1 or committed > current_revision))
                or (operation == "PROJECT_FINANCIAL_APPROVAL_RESULT" and committed != expected)):
            raise VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID")
        if operation == "PROJECT_FINANCIAL_APPROVAL_RESULT" and (not isinstance(projection_revision, int) or isinstance(projection_revision, bool) or projection_revision < 0):
            raise VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID")
        _aware_timestamp(item.get("created_at"))
        receipts.append(dict(item)); seen_keys.add(key)
    return receipts


def _hydrate_persisted_vendor_bill_with_receipts(document: Mapping[str, Any]) -> tuple[VendorBill, List[Dict[str, Any]]]:
    """Hydrates the canonical obligation and its replay evidence through one strict persisted truth boundary."""
    bill = _hydrate_persisted_vendor_bill(document)
    return bill, _hydrate_command_receipts(document, bill.revision)


def _collection_or_raise(collection: Optional[Collection] = None) -> Collection:
    """Binds the dedicated collection to the same majority/journal durability policy as financial registries."""
    target = collection
    if target is None:
        database = get_database()
        if database is None:
            raise VendorBillRegistryError("VENDOR_BILL_PERSISTENCE_UNAVAILABLE")
        target = database[VENDOR_BILL_COLLECTION]
    return target.with_options(write_concern=FINANCIAL_WRITE_CONCERN, read_concern=FINANCIAL_READ_CONCERN)


def _required_text(document: Mapping[str, Any], field: str) -> str:
    value = document.get(field)
    if not isinstance(value, str) or not value.strip():
        raise VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID")
    return value.strip()


def _optional_text(document: Mapping[str, Any], field: str) -> Optional[str]:
    value = document.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        raise VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID")
    return value


def _date_only(value: Any) -> date:
    if isinstance(value, str):
        try:
            value = date.fromisoformat(value)
        except ValueError:
            value = None
    if not isinstance(value, date) or isinstance(value, datetime):
        raise VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID")
    return value


def _aware_timestamp(value: Any) -> datetime:
    parsed = parse_datetime(value)
    if parsed is None or parsed.tzinfo is None:
        raise VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID")
    return parsed


def _hydrate_persisted_vendor_bill(document: Mapping[str, Any]) -> VendorBill:
    """The sole persisted VendorBill trust boundary used by all registry reader surfaces."""
    try:
        revision = document.get("revision")
        projection_revision = document.get("approval_projection_revision", 0)
        projection_result_id = document.get("approval_effective_result_id")
        guard_revision = document.get("release_authority_guard_revision", 0)
        fingerprint = document.get("create_fingerprint")
        gross_amount_minor, outstanding_amount_minor = document.get("gross_amount_minor"), document.get("outstanding_amount_minor")
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
            raise VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID")
        if not isinstance(projection_revision, int) or isinstance(projection_revision, bool) or projection_revision < 0:
            raise VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID")
        if not isinstance(guard_revision, int) or isinstance(guard_revision, bool) or guard_revision < 0:
            raise VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID")
        if projection_revision == 0 and projection_result_id is not None:
            raise VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID")
        if projection_revision > 0 and (not isinstance(projection_result_id, str) or not projection_result_id.strip()):
            raise VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID")
        if (not isinstance(gross_amount_minor, int) or isinstance(gross_amount_minor, bool)
                or not isinstance(outstanding_amount_minor, int) or isinstance(outstanding_amount_minor, bool)):
            raise VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID")
        if not isinstance(fingerprint, str) or re.fullmatch(r"[0-9a-f]{128}", fingerprint) is None:
            raise VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID")
        bill = VendorBill(
            tenant_id=_required_text(document, "tenant_id"), payable_id=_required_text(document, "payable_id"), vendor_id=_required_text(document, "vendor_id"),
            vendor_reference=_optional_text(document, "vendor_reference"), source_document_reference=_optional_text(document, "source_document_reference"),
            currency=_required_text(document, "currency"), gross_amount_minor=gross_amount_minor, outstanding_amount_minor=outstanding_amount_minor,
            issue_date=_date_only(document.get("issue_date")), due_date=_date_only(document.get("due_date")), received_at=_aware_timestamp(document.get("received_at")),
            obligation_state=VendorBillObligationState(document.get("obligation_state")), approval_state=VendorBillApprovalState(document.get("approval_state")),
            approval_policy_reference=_optional_text(document, "approval_policy_reference"), revision=revision, created_at=_aware_timestamp(document.get("created_at")), updated_at=_aware_timestamp(document.get("updated_at")), proof_hash=_required_text(document, "proof_hash"),
            approval_projection_revision=projection_revision, approval_effective_result_id=projection_result_id,
            release_authority_guard_revision=guard_revision,
        )
        _hydrate_command_receipts(document, bill.revision)
        return bill
    except (TypeError, ValueError, VendorBillDomainError) as error:
        if isinstance(error, VendorBillPersistedRecordInvalidError):
            raise
        raise VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID") from error


def _document_from_vendor_bill(bill: VendorBill, create_fingerprint: str) -> Dict[str, Any]:
    """Serializes one canonical obligation without release, execution, or payment-destination fields."""
    return {"tenant_id": bill.tenant_id, "payable_id": bill.payable_id, "vendor_id": bill.vendor_id, "vendor_reference": bill.vendor_reference, "vendor_reference_normalized": (bill.vendor_reference or "").strip().casefold() or None, "source_document_reference": bill.source_document_reference, "currency": bill.currency, "gross_amount_minor": bill.gross_amount_minor, "outstanding_amount_minor": bill.outstanding_amount_minor, "issue_date": bill.issue_date.isoformat(), "due_date": bill.due_date.isoformat(), "received_at": bill.received_at.isoformat(), "obligation_state": bill.obligation_state.value, "approval_state": bill.approval_state.value, "approval_projection_revision": bill.approval_projection_revision, "approval_effective_result_id": bill.approval_effective_result_id, "release_authority_guard_revision": bill.release_authority_guard_revision, "approval_policy_reference": bill.approval_policy_reference, "revision": bill.revision, "created_at": bill.created_at.isoformat(), "updated_at": bill.updated_at.isoformat(), "proof_hash": bill.proof_hash, "create_fingerprint": create_fingerprint, "command_receipts": []}


class VendorBillRegistry:
    """Persist and coordinate tenant-scoped VendorBill obligation truth.

    The registry enforces strict hydration, durable command receipts, CAS
    projection coordination, and release-authority guard freshness. It never
    executes, settles, or owns payment transactions; Kennel EOS is exclusive
    financial execution authority. Caller-owned sessions control transactions.
    """
    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        target = _collection_or_raise(collection)
        target.create_index([("tenant_id", ASCENDING), ("payable_id", ASCENDING)], unique=True, name="tenant_payable_identity_unique")
        target.create_index([("tenant_id", ASCENDING), ("vendor_id", ASCENDING)], name="tenant_vendor_bills")
        target.create_index([("tenant_id", ASCENDING), ("due_date", ASCENDING)], name="tenant_due_date")
        target.create_index([("tenant_id", ASCENDING), ("obligation_state", ASCENDING)], name="tenant_obligation_state")
        target.create_index([("tenant_id", ASCENDING), ("approval_state", ASCENDING)], name="tenant_approval_state")
        target.create_index([("tenant_id", ASCENDING), ("created_at", DESCENDING)], name="tenant_created_at")
        target.create_index([("tenant_id", ASCENDING), ("vendor_id", ASCENDING), ("vendor_reference_normalized", ASCENDING)], name="tenant_vendor_reference_signal")

    @staticmethod
    def create(bill: VendorBill, collection: Optional[Collection] = None) -> VendorBillCreateResult:
        if not isinstance(bill, VendorBill):
            raise VendorBillDomainError("bill must be a VendorBill")
        target = _collection_or_raise(collection)
        if target.database[VENDOR_COLLECTION].find_one({"tenant_id": bill.tenant_id, "vendor_id": bill.vendor_id}) is None:
            raise VendorBillVendorNotFoundError("VENDOR_NOT_FOUND")
        fingerprint = _create_fingerprint(bill)
        try:
            target.insert_one(_document_from_vendor_bill(bill, fingerprint))
        except DuplicateKeyError as error:
            existing = target.find_one({"tenant_id": bill.tenant_id, "payable_id": bill.payable_id})
            if existing is None:
                raise VendorBillRegistryError("VENDOR_BILL_CREATE_RECONCILIATION_FAILED") from error
            persisted = _hydrate_persisted_vendor_bill(existing)
            if existing.get("create_fingerprint") != fingerprint:
                raise VendorBillCreateConflictError("VENDOR_BILL_CREATE_CONFLICT") from error
            return VendorBillCreateResult(VendorBillCreateOutcome.IDEMPOTENT_REPLAY, persisted, persisted.payable_id, fingerprint)
        except PyMongoError as error:
            raise VendorBillRegistryError("VENDOR_BILL_CREATE_FAILED") from error
        return VendorBillCreateResult(VendorBillCreateOutcome.CREATED, bill, bill.payable_id, fingerprint)

    @staticmethod
    def get(tenant_id: str, payable_id: str, collection: Optional[Collection] = None) -> VendorBill:
        document = _collection_or_raise(collection).find_one({"tenant_id": str(tenant_id).strip(), "payable_id": str(payable_id).strip()})
        if document is None:
            raise VendorBillNotFoundError("VENDOR_BILL_NOT_FOUND")
        return _hydrate_persisted_vendor_bill(document)

    @staticmethod
    def open_bill(tenant_id: str, payable_id: str, expected_revision: int, idempotency_key: str, collection: Optional[Collection] = None) -> VendorBillMutationResult:
        """Atomically commits or exactly replays one tenant-scoped DRAFT-to-OPEN command and its durable receipt."""
        if not isinstance(expected_revision, int) or isinstance(expected_revision, bool) or expected_revision < 1:
            raise VendorBillRevisionConflictError("VENDOR_BILL_REVISION_CONFLICT")
        target = _collection_or_raise(collection)
        tenant, payable = str(tenant_id).strip(), str(payable_id).strip()
        receipt = _open_bill_command_receipt(tenant, payable, expected_revision, idempotency_key)
        current_document = target.find_one({"tenant_id": tenant, "payable_id": payable})
        if current_document is None:
            raise VendorBillNotFoundError("VENDOR_BILL_NOT_FOUND")
        current, receipts = _hydrate_persisted_vendor_bill_with_receipts(current_document)
        for prior in receipts:
            if prior["idempotency_key"] == receipt["idempotency_key"]:
                if prior["command_fingerprint"] != receipt["command_fingerprint"]:
                    raise VendorBillIdempotencyKeyReuseError("VENDOR_BILL_IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_COMMAND")
                return VendorBillMutationResult(VendorBillMutationOutcome.IDEMPOTENT_REPLAY, current, prior["committed_revision"], current.revision, receipt["idempotency_key"])
        now = datetime.now().astimezone().isoformat()
        receipt["committed_revision"] = expected_revision + 1
        receipt["created_at"] = now
        document = target.find_one_and_update(
            {"tenant_id": tenant, "payable_id": payable, "revision": expected_revision, "obligation_state": VendorBillObligationState.DRAFT.value},
            {"$set": {"obligation_state": VendorBillObligationState.OPEN.value, "updated_at": now}, "$inc": {"revision": 1}, "$push": {"command_receipts": receipt}},
            return_document=ReturnDocument.AFTER,
        )
        if document is not None:
            persisted = _hydrate_persisted_vendor_bill(document)
            return VendorBillMutationResult(VendorBillMutationOutcome.COMMITTED, persisted, persisted.revision, persisted.revision, receipt["idempotency_key"])
        existing = target.find_one({"tenant_id": tenant, "payable_id": payable})
        if existing is None:
            raise VendorBillNotFoundError("VENDOR_BILL_NOT_FOUND")
        persisted, replay_receipts = _hydrate_persisted_vendor_bill_with_receipts(existing)
        for prior in replay_receipts:
            if prior["idempotency_key"] == receipt["idempotency_key"]:
                if prior["command_fingerprint"] != receipt["command_fingerprint"]:
                    raise VendorBillIdempotencyKeyReuseError("VENDOR_BILL_IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_COMMAND")
                return VendorBillMutationResult(VendorBillMutationOutcome.IDEMPOTENT_REPLAY, persisted, prior["committed_revision"], persisted.revision, receipt["idempotency_key"])
        if persisted.revision != expected_revision:
            raise VendorBillRevisionConflictError("VENDOR_BILL_REVISION_CONFLICT")
        raise VendorBillRevisionConflictError("VENDOR_BILL_REVISION_CONFLICT")

    @staticmethod
    def acquire_release_authority_guard(
        tenant_id: str,
        payable_id: str,
        expected_revision: int,
        expected_approval_projection_revision: int,
        expected_approval_effective_result_id: str,
        expected_release_authority_guard_revision: int,
        collection: Optional[Collection] = None,
        *,
        session: Optional[ClientSession] = None,
    ) -> VendorBill:
        """Advance the release-authority guard through a caller-owned CAS write."""
        tenant, payable = str(tenant_id).strip(), str(payable_id).strip()
        if not tenant or not payable:
            raise VendorBillReleaseAuthorityGuardConflictError("VENDOR_BILL_RELEASE_AUTHORITY_GUARD_INVALID_IDENTITY")
        if (not isinstance(expected_revision, int) or isinstance(expected_revision, bool) or expected_revision < 1
                or not isinstance(expected_approval_projection_revision, int) or isinstance(expected_approval_projection_revision, bool) or expected_approval_projection_revision < 1
                or not isinstance(expected_release_authority_guard_revision, int) or isinstance(expected_release_authority_guard_revision, bool) or expected_release_authority_guard_revision < 0
                or not isinstance(expected_approval_effective_result_id, str) or not expected_approval_effective_result_id.strip()):
            raise VendorBillReleaseAuthorityGuardConflictError("VENDOR_BILL_RELEASE_AUTHORITY_GUARD_INVALID_INPUT")
        target = _collection_or_raise(collection)
        predicate = {
            "tenant_id": tenant,
            "payable_id": payable,
            "revision": expected_revision,
            "approval_projection_revision": expected_approval_projection_revision,
            "approval_effective_result_id": expected_approval_effective_result_id.strip(),
            "release_authority_guard_revision": expected_release_authority_guard_revision,
            "obligation_state": VendorBillObligationState.OPEN.value,
            "approval_state": VendorBillApprovalState.APPROVED.value,
        }
        document = target.find_one_and_update(
            predicate,
            {"$inc": {"release_authority_guard_revision": 1}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}},
            return_document=ReturnDocument.AFTER,
            session=session,
        )
        if document is not None:
            return _hydrate_persisted_vendor_bill(document)
        existing = target.find_one({"tenant_id": tenant, "payable_id": payable}, session=session)
        if existing is None:
            raise VendorBillNotFoundError("VENDOR_BILL_NOT_FOUND")
        current = _hydrate_persisted_vendor_bill(existing)
        if current.revision != expected_revision:
            raise VendorBillRevisionConflictError("VENDOR_BILL_REVISION_CONFLICT")
        if current.approval_projection_revision != expected_approval_projection_revision:
            raise VendorBillApprovalProjectionConflictError("VENDOR_BILL_APPROVAL_PROJECTION_CONFLICT")
        if current.approval_effective_result_id != expected_approval_effective_result_id.strip():
            raise VendorBillApprovalProjectionReferenceError("VENDOR_BILL_APPROVAL_PROJECTION_REFERENCE_MISMATCH")
        if current.obligation_state is not VendorBillObligationState.OPEN:
            raise VendorBillReleaseAuthorityGuardConflictError("VENDOR_BILL_RELEASE_AUTHORITY_GUARD_INVALID_OBLIGATION_STATE")
        if current.approval_state is not VendorBillApprovalState.APPROVED:
            raise VendorBillReleaseAuthorityGuardConflictError("VENDOR_BILL_RELEASE_AUTHORITY_GUARD_APPROVAL_NOT_APPROVED")
        raise VendorBillReleaseAuthorityGuardConflictError("VENDOR_BILL_RELEASE_AUTHORITY_GUARD_STALE")

    @staticmethod
    def project_financial_approval_result(tenant_id: str, payable_id: str, effective_result_id: str, expected_revision: int, expected_approval_projection_revision: int, idempotency_key: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> VendorBillMutationResult:
        """CAS-projects a persisted effective result without changing the VendorBill obligation revision."""
        if not isinstance(expected_revision, int) or isinstance(expected_revision, bool) or expected_revision < 1 or not isinstance(expected_approval_projection_revision, int) or isinstance(expected_approval_projection_revision, bool) or expected_approval_projection_revision < 0:
            raise VendorBillApprovalProjectionConflictError("VENDOR_BILL_APPROVAL_PROJECTION_CONFLICT")
        tenant, payable, result_id = str(tenant_id).strip(), str(payable_id).strip(), str(effective_result_id).strip()
        if not result_id:
            raise VendorBillApprovalProjectionReferenceError("VENDOR_BILL_APPROVAL_PROJECTION_REFERENCE_MISMATCH")
        target = _collection_or_raise(collection)
        from .financial_approval_effective_result_registry import FinancialApprovalEffectiveResultRegistry, FinancialApprovalEffectiveResultNotFoundError
        try:
            result = FinancialApprovalEffectiveResultRegistry.get(tenant, result_id, target.database["financial_approval_effective_results"], session=session)
        except FinancialApprovalEffectiveResultNotFoundError as error:
            raise VendorBillApprovalProjectionReferenceError("VENDOR_BILL_APPROVAL_PROJECTION_REFERENCE_MISMATCH") from error
        if result.subject_type.value != "VENDOR_BILL" or result.subject_id != payable or result.tenant_id != tenant or result.subject_revision != expected_revision:
            raise VendorBillApprovalProjectionReferenceError("VENDOR_BILL_APPROVAL_PROJECTION_REFERENCE_MISMATCH")
        current_document = target.find_one({"tenant_id": tenant, "payable_id": payable}, session=session)
        if current_document is None:
            raise VendorBillNotFoundError("VENDOR_BILL_NOT_FOUND")
        current, receipts = _hydrate_persisted_vendor_bill_with_receipts(current_document)
        payload = {"tenant_id": tenant, "payable_id": payable, "expected_revision": expected_revision, "expected_approval_projection_revision": expected_approval_projection_revision, "effective_result_id": result_id, "operation": "PROJECT_FINANCIAL_APPROVAL_RESULT", "idempotency_key": idempotency_key.strip() if isinstance(idempotency_key, str) else ""}
        if not payload["idempotency_key"] or len(payload["idempotency_key"]) > 128:
            raise VendorBillDomainError("idempotency_key must be a non-empty string of at most 128 characters")
        receipt = {**payload, "command_fingerprint": hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest(), "committed_revision": expected_revision, "created_at": datetime.now().astimezone().isoformat()}
        for prior in receipts:
            if prior["idempotency_key"] == receipt["idempotency_key"]:
                if prior["command_fingerprint"] != receipt["command_fingerprint"]:
                    raise VendorBillApprovalProjectionIdempotencyKeyReuseError("VENDOR_BILL_APPROVAL_PROJECTION_IDEMPOTENCY_KEY_REUSED")
                return VendorBillMutationResult(VendorBillMutationOutcome.IDEMPOTENT_REPLAY, current, current.revision, current.revision, receipt["idempotency_key"])
        if current.approval_effective_result_id == result_id and current.approval_projection_revision >= expected_approval_projection_revision:
            return VendorBillMutationResult(VendorBillMutationOutcome.IDEMPOTENT_REPLAY, current, current.revision, current.revision, receipt["idempotency_key"])
        now = datetime.now().astimezone().isoformat()
        document = target.find_one_and_update({"tenant_id": tenant, "payable_id": payable, "revision": expected_revision, "approval_projection_revision": expected_approval_projection_revision, "obligation_state": VendorBillObligationState.OPEN.value}, {"$set": {"approval_state": result.effective_state.value, "approval_effective_result_id": result.result_id, "updated_at": now}, "$inc": {"approval_projection_revision": 1}, "$push": {"command_receipts": receipt}}, return_document=ReturnDocument.AFTER, session=session)
        if document is not None:
            persisted = _hydrate_persisted_vendor_bill(document)
            return VendorBillMutationResult(VendorBillMutationOutcome.COMMITTED, persisted, persisted.revision, persisted.revision, receipt["idempotency_key"])
        existing = target.find_one({"tenant_id": tenant, "payable_id": payable}, session=session)
        if existing is None:
            raise VendorBillNotFoundError("VENDOR_BILL_NOT_FOUND")
        persisted, persisted_receipts = _hydrate_persisted_vendor_bill_with_receipts(existing)
        for prior in persisted_receipts:
            if prior["idempotency_key"] == receipt["idempotency_key"]:
                if prior["command_fingerprint"] != receipt["command_fingerprint"]:
                    raise VendorBillApprovalProjectionIdempotencyKeyReuseError("VENDOR_BILL_APPROVAL_PROJECTION_IDEMPOTENCY_KEY_REUSED")
                return VendorBillMutationResult(VendorBillMutationOutcome.IDEMPOTENT_REPLAY, persisted, persisted.revision, persisted.revision, receipt["idempotency_key"])
        raise VendorBillApprovalProjectionConflictError("VENDOR_BILL_APPROVAL_PROJECTION_CONFLICT")

    @staticmethod
    def list(tenant_id: str, limit: int = 100, collection: Optional[Collection] = None) -> List[VendorBill]:
        bounded = min(max(int(limit), 1), 250)
        rows = _collection_or_raise(collection).find({"tenant_id": str(tenant_id).strip()}).sort([("due_date", ASCENDING), ("created_at", DESCENDING), ("payable_id", ASCENDING)]).limit(bounded)
        return [_hydrate_persisted_vendor_bill(row) for row in rows]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: vendor_bill_registry.py
# VERSION: v1.4.0-RELEASE-AUTHORITY-GUARD-CAS
# AUTHORITY BOUNDARY: tenant-scoped VendorBill persistence and coordination only
# TENANT POSTURE: every read, mutation, receipt, and conflict is tenant-scoped
# FAIL-CLOSED POSTURE: malformed persisted truth and unknown conflicts are rejected
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; this registry never executes or settles
# END OF WILSY OS SOVEREIGN ARTIFACT
