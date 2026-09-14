"""Durable journal for immutable offline process-service field evidence.

TITLE: Wilsy OS Process-Service Offline Field-Evidence Registry
VERSION: v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persist and strictly hydrate P5 mobile observation commands and sync
         receipts without deriving legal-service or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/process_service_field_evidence_registry.py
COLLABORATION / OWNERSHIP: P5 evidence journal only; P1/P2 remain lifecycle
                            authorities and callers own sessions/transactions.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-REGISTRY
           establishes strict append-only evidence persistence and replay.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every read, write, replay, and sequence check is tenant scoped.
AUTHORITY BOUNDARY: Persistence/hydration only; no lifecycle transition or
                     legal-service derivation is performed here.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution,
                              payment, and settlement.
TRANSACTION BOUNDARY: Caller supplies and owns sessions/transactions; this
                      registry never starts, commits, aborts, or retries them.
FAIL-CLOSED DECLARATION: Schema drift, corruption, duplicate divergence,
                         sequence gaps, and persistence failures reject.
"""
from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
import re
from typing import Any, Final, NoReturn, cast

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.process_service_field_evidence_authority import (
    OfflineFieldEvidenceCommand,
    OfflineFieldEvidenceSyncReceipt,
    SCHEMA as EVIDENCE_SCHEMA,
    VERSION as EVIDENCE_VERSION,
    hydrate_offline_field_evidence_command,
    hydrate_offline_field_evidence_sync_receipt,
)

VERSION: Final[str] = "v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-REGISTRY"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-REGISTRY/V1"
COLLECTION: Final[str] = "process_service_field_evidence"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_RECORD_FIELDS = frozenset(
    {
        "schema",
        "version",
        "entity_type",
        "tenant_id",
        "event_id",
        "receipt_id",
        "device_id",
        "sequence_number",
        "attempt_id",
        "district_id",
        "sheriff_office_id",
        "evidence_identity",
        "command_payload",
        "command_fingerprint",
        "receipt_payload",
        "receipt_fingerprint",
    }
)


class ProcessServiceFieldEvidenceRegistryError(RuntimeError):
    """Stable fail-closed error for journal persistence and hydration.

    Errors never disclose records from another tenant.  The registry performs
    no transaction lifecycle operation; callers must retry whole transactions
    when ``P5M_RETRY_TRANSACTION_REQUIRED`` is returned.
    """

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = ProcessServiceFieldEvidenceRegistryError(code)
    if cause is None:
        raise error
    raise error from cause


def _tenant(value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail("P5M_INVALID_TENANT")
    result = cast(str, value)
    if result.casefold() in {"default", "global", "global_root", "root", "master", "*"}:
        _fail("P5M_INVALID_TENANT")
    return result


def _sha3(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha3_512(encoded.encode("utf-8")).hexdigest()


def _fingerprint(value: object, code: str) -> str:
    if not isinstance(value, str) or _SHA3.fullmatch(value) is None:
        _fail(code)
    return value


def _identity(value: object, code: str) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(code)
    return value


def _active_transaction(session: Any) -> bool:
    return session is not None and bool(getattr(session, "in_transaction", False))


def _record_without_id(document: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(document)
    result.pop("_id", None)
    return result


def _expected_identity(command: OfflineFieldEvidenceCommand, receipt: OfflineFieldEvidenceSyncReceipt) -> str:
    return _sha3(
        {
            "schema": EVIDENCE_SCHEMA,
            "version": EVIDENCE_VERSION,
            "tenant_id": command.tenant_id,
            "event_id": command.event_id,
            "device_id": command.device_id,
            "sequence_number": command.sequence_number,
            "command_fingerprint": command.fingerprint,
            "receipt_id": receipt.receipt_id,
        }
    )


def _record_for(command: OfflineFieldEvidenceCommand, receipt: OfflineFieldEvidenceSyncReceipt) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "entity_type": "OfflineFieldEvidenceSyncReceipt",
        "tenant_id": command.tenant_id,
        "event_id": command.event_id,
        "receipt_id": receipt.receipt_id,
        "device_id": command.device_id,
        "sequence_number": command.sequence_number,
        "attempt_id": command.attempt_id,
        "district_id": command.district_id,
        "sheriff_office_id": command.sheriff_office_id,
        "evidence_identity": receipt.evidence_identity,
        "command_payload": command.to_dict(),
        "command_fingerprint": command.fingerprint,
        "receipt_payload": receipt.to_dict(),
        "receipt_fingerprint": receipt.fingerprint,
    }


def _hydrate_record(document: Mapping[str, Any]) -> OfflineFieldEvidenceSyncReceipt:
    record = _record_without_id(document)
    if set(record) != _RECORD_FIELDS:
        _fail("P5M_RECORD_SCHEMA_INVALID")
    if record["schema"] != SCHEMA or record["version"] != VERSION or record["entity_type"] != "OfflineFieldEvidenceSyncReceipt":
        _fail("P5M_RECORD_VERSION_UNSUPPORTED")
    tenant = _tenant(record["tenant_id"])
    event_id = _identity(record["event_id"], "P5M_EVENT_ID_INVALID")
    receipt_id = _identity(record["receipt_id"], "P5M_RECEIPT_ID_INVALID")
    device_id = _identity(record["device_id"], "P5M_DEVICE_ID_INVALID")
    attempt_id = _identity(record["attempt_id"], "P5M_ATTEMPT_ID_INVALID")
    district_id = _identity(record["district_id"], "P5M_DISTRICT_ID_INVALID")
    sheriff_office_id = _identity(record["sheriff_office_id"], "P5M_SHERIFF_OFFICE_ID_INVALID")
    if not isinstance(record["sequence_number"], int) or isinstance(record["sequence_number"], bool) or record["sequence_number"] < 1:
        _fail("P5M_SEQUENCE_NUMBER_INVALID")
    command_payload = record["command_payload"]
    receipt_payload = record["receipt_payload"]
    if not isinstance(command_payload, Mapping) or not isinstance(receipt_payload, Mapping):
        _fail("P5M_SOURCE_PAYLOAD_INVALID")
    command = hydrate_offline_field_evidence_command(command_payload)
    receipt = hydrate_offline_field_evidence_sync_receipt(receipt_payload)
    if command.tenant_id != tenant or receipt.tenant_id != tenant:
        _fail("P5M_TENANT_MISMATCH")
    if command.event_id != event_id or receipt.event_id != event_id or receipt.receipt_id != receipt_id:
        _fail("P5M_BINDING_MISMATCH")
    if command.device_id != device_id or receipt.device_id != device_id or command.attempt_id != attempt_id or receipt.attempt_id != attempt_id or command.district_id != district_id or receipt.district_id != district_id or command.sheriff_office_id != sheriff_office_id or receipt.sheriff_office_id != sheriff_office_id:
        _fail("P5M_BINDING_MISMATCH")
    if command.sequence_number != record["sequence_number"] or receipt.sequence_number != record["sequence_number"]:
        _fail("P5M_BINDING_MISMATCH")
    if _fingerprint(record["command_fingerprint"], "P5M_COMMAND_FINGERPRINT_INVALID") != command.fingerprint:
        _fail("P5M_COMMAND_FINGERPRINT_MISMATCH")
    if _fingerprint(record["receipt_fingerprint"], "P5M_RECEIPT_FINGERPRINT_INVALID") != receipt.fingerprint:
        _fail("P5M_RECEIPT_FINGERPRINT_MISMATCH")
    if _fingerprint(record["evidence_identity"], "P5M_EVIDENCE_IDENTITY_INVALID") != receipt.evidence_identity:
        _fail("P5M_EVIDENCE_IDENTITY_MISMATCH")
    if _expected_identity(command, receipt) != receipt.evidence_identity:
        _fail("P5M_EVIDENCE_IDENTITY_MISMATCH")
    expected = _record_for(command, receipt)
    if _record_without_id(document) != expected:
        _fail("P5M_RECORD_BINDING_MISMATCH")
    return receipt


class ProcessServiceFieldEvidenceRegistry:
    """Persist immutable offline evidence using caller-owned Mongo resources.

    ``persist`` performs one insert and strict replay reconciliation.  It
    never starts, commits, aborts, or retains a Mongo client/transaction.
    ``get`` is exact tenant-scoped and reports foreign evidence as not found.
    """

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Create deterministic tenant-scoped uniqueness indexes."""
        try:
            collection.create_index([("tenant_id", 1), ("evidence_identity", 1)], unique=True, name="process_service_field_evidence_identity_unique")
            collection.create_index([("tenant_id", 1), ("event_id", 1)], unique=True, name="process_service_field_evidence_event_unique")
            collection.create_index([("tenant_id", 1), ("attempt_id", 1), ("device_id", 1), ("sequence_number", 1)], unique=True, name="process_service_field_evidence_sequence_unique")
            collection.create_index([("tenant_id", 1), ("attempt_id", 1), ("device_id", 1)], unique=False, name="process_service_field_evidence_sequence_history")
        except PyMongoError as error:
            _fail("P5M_PERSISTENCE_UNAVAILABLE", error)

    @staticmethod
    def persist(command: OfflineFieldEvidenceCommand, receipt: OfflineFieldEvidenceSyncReceipt, collection: Any, *, session: Any = None) -> OfflineFieldEvidenceSyncReceipt:
        """Insert one journal row or return exact replay; no overwrite/upsert."""
        if type(command) is not OfflineFieldEvidenceCommand or type(receipt) is not OfflineFieldEvidenceSyncReceipt:
            _fail("P5M_VALUE_REQUIRED")
        try:
            command.__post_init__()
            receipt.__post_init__()
        except Exception as error:
            _fail("P5M_VALUE_INVALID", error)
        if receipt.tenant_id != command.tenant_id or receipt.command_fingerprint != command.fingerprint or receipt.evidence_identity != _expected_identity(command, receipt):
            _fail("P5M_BINDING_MISMATCH")
        record = _record_for(command, receipt)
        identity_query = {"tenant_id": command.tenant_id, "evidence_identity": receipt.evidence_identity}
        event_query = {"tenant_id": command.tenant_id, "event_id": command.event_id}
        sequence_query = {"tenant_id": command.tenant_id, "attempt_id": command.attempt_id, "device_id": command.device_id, "sequence_number": command.sequence_number}
        try:
            existing = collection.find_one(identity_query, session=session)
            if existing is None:
                existing = collection.find_one(event_query, session=session)
            if existing is None:
                existing = collection.find_one(sequence_query, session=session)
        except PyMongoError as error:
            _fail("P5M_PERSISTENCE_UNAVAILABLE", error)
        if existing is not None:
            hydrated = _hydrate_record(existing)
            if _record_without_id(existing) == record:
                return hydrated
            _fail("P5M_REPLAY_CONFLICT")
        if command.sequence_number > 1:
            try:
                prior_rows = collection.find({"tenant_id": command.tenant_id, "attempt_id": command.attempt_id, "device_id": command.device_id}, session=session)
                rows = [_hydrate_record(row) for row in prior_rows]
            except PyMongoError as error:
                _fail("P5M_PERSISTENCE_UNAVAILABLE", error)
            prior = [row for row in rows if row.sequence_number == command.sequence_number - 1]
            if len(prior) != 1 or prior[0].evidence_fingerprint != command.previous_event_fingerprint:
                _fail("P5M_SEQUENCE_GAP")
            if any(row.sequence_number >= command.sequence_number for row in rows):
                _fail("P5M_SEQUENCE_ORDER_INVALID")
        else:
            try:
                prior_rows = collection.find({"tenant_id": command.tenant_id, "attempt_id": command.attempt_id, "device_id": command.device_id}, session=session)
                if any(_hydrate_record(row).sequence_number >= 1 for row in prior_rows):
                    _fail("P5M_SEQUENCE_ORDER_INVALID")
            except PyMongoError as error:
                _fail("P5M_PERSISTENCE_UNAVAILABLE", error)
        try:
            collection.insert_one(record, session=session)
        except DuplicateKeyError as error:
            if _active_transaction(session):
                _fail("P5M_RETRY_TRANSACTION_REQUIRED", error)
            try:
                raced = collection.find_one(identity_query, session=session) or collection.find_one(event_query, session=session) or collection.find_one(sequence_query, session=session)
            except PyMongoError as read_error:
                _fail("P5M_PERSISTENCE_UNAVAILABLE", read_error)
            if raced is None:
                _fail("P5M_REPLAY_CONFLICT", error)
            hydrated = _hydrate_record(raced)
            if _record_without_id(raced) == record:
                return hydrated
            _fail("P5M_REPLAY_CONFLICT", error)
        except PyMongoError as error:
            if _active_transaction(session) and error.has_error_label("TransientTransactionError") and not error.has_error_label("UnknownTransactionCommitResult"):
                _fail("P5M_RETRY_TRANSACTION_REQUIRED", error)
            _fail("P5M_PERSISTENCE_UNAVAILABLE", error)
        return _hydrate_record(record)

    @staticmethod
    def get(tenant_id: str, evidence_identity: str, collection: Any, *, session: Any = None) -> OfflineFieldEvidenceSyncReceipt:
        """Hydrate one exact tenant-scoped journal receipt or not-found."""
        tenant = _tenant(tenant_id)
        _fingerprint(evidence_identity, "P5M_EVIDENCE_IDENTITY_INVALID")
        try:
            document = collection.find_one({"tenant_id": tenant, "evidence_identity": evidence_identity}, session=session)
        except PyMongoError as error:
            _fail("P5M_PERSISTENCE_UNAVAILABLE", error)
        if document is None:
            _fail("P5M_EVIDENCE_NOT_FOUND")
        receipt = _hydrate_record(document)
        if receipt.tenant_id != tenant:
            _fail("P5M_TENANT_MISMATCH")
        return receipt


__all__ = ["COLLECTION", "SCHEMA", "VERSION", "ProcessServiceFieldEvidenceRegistry", "ProcessServiceFieldEvidenceRegistryError"]


# ARTIFACT: process_service_field_evidence_registry.py
# VERSION: v1.0.0-PROCESS-SERVICE-OFFLINE-FIELD-EVIDENCE-REGISTRY
# AUTHORITY BOUNDARY: durable immutable evidence journal and strict hydration only.
# TENANT POSTURE: every operation is exact tenant scoped; foreign existence is hidden.
# FAIL-CLOSED POSTURE: corruption, divergence, gaps, and conflicts reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
