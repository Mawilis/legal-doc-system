"""WILSY OS durable Legal notification recipient-binding registry.

TITLE: Legal Notification Recipient Binding Registry
VERSION: v1.1.0-L8-8H-RECIPIENT-BINDING-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persists and resolves explicit recipient-binding evidence within one
         caller-owned active Mongo transaction, with exact replay semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_notification_recipient_binding_registry.py
COLLABORATION / OWNERSHIP: The L8-8H domain owns binding semantics; the L8-8H
                            resolver owns current source and IAM revalidation.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.1.0 adopts the binding v1.1 schema with redundant
           unverifiable source-authority fields removed.
           2026-10-12 v1.0.0 establishes transaction-required append-only
           storage, strict hydration, exact replay and effective scoped reads.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Persists opaque authority identifiers only; no raw
                            contact, credential, provider or message data.
TENANT BOUNDARY: Every write and read predicate includes exact tenant scope.
AUTHORITY BOUNDARY: Durable recipient-selection evidence only; no dispatch.
TRANSACTION BOUNDARY: Caller owns an already-active transaction; this registry
                      never starts, commits, aborts or retries it.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Absence, corruption, divergent replay, ambiguous data,
                         persistence failure and transaction misuse reject.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Final, Mapping, NoReturn, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError

from tools.eos.legal_operations.domain.legal_notification_recipient_binding import (
    LegalNotificationEvent,
    LegalNotificationRecipientBinding,
    LegalNotificationRecipientBindingError,
)

VERSION: Final[str] = "v1.1.0-L8-8H-RECIPIENT-BINDING-REGISTRY"
COLLECTION: Final[str] = "legal_notification_recipient_bindings"
BINDING_IDENTITY_INDEX: Final[str] = "legal_notification_recipient_binding_identity_unique"
EFFECTIVE_SCOPE_INDEX: Final[str] = "legal_notification_recipient_binding_effective_scope"
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset({"default", "global", "global_root", "root", "master", "*"})


class LegalNotificationRecipientBindingRegistryError(RuntimeError):
    """Stable fail-closed registry failure carrying a code only."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalNotificationRecipientBindingRegistryError(code)
    if cause is None:
        raise error
    raise error from cause


def _active(session: Any) -> Any:
    if session is None:
        _fail("L8_8H_REGISTRY_ACTIVE_TRANSACTION_REQUIRED")
    active = getattr(session, "in_transaction", False)
    if callable(active):
        active = active()
    if active is not True:
        _fail("L8_8H_REGISTRY_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _identity(name: str, value: object, *, tenant: bool = False) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"L8_8H_REGISTRY_{name.upper()}_INVALID")
    if tenant and value.casefold() in _FORBIDDEN_TENANTS:
        _fail("L8_8H_REGISTRY_TENANT_INVALID")
    return value


def _utc(value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("L8_8H_REGISTRY_RESOLUTION_TIME_INVALID")
    canonical = value.astimezone(timezone.utc)
    if canonical != value or canonical.tzinfo != timezone.utc:
        _fail("L8_8H_REGISTRY_RESOLUTION_TIME_INVALID")
    return canonical


def _hydrate(row: Mapping[str, object]) -> LegalNotificationRecipientBinding:
    payload = {key: value for key, value in row.items() if key != "_id"}
    # PyMongo's default BSON decoder returns UTC instants without tzinfo.
    # Restore UTC only at this known persistence boundary; arbitrary naive
    # domain inputs remain forbidden.
    for field in ("effective_from", "effective_until", "created_at"):
        value = payload.get(field)
        if isinstance(value, datetime) and value.tzinfo is None:
            payload[field] = value.replace(tzinfo=timezone.utc)
    try:
        return LegalNotificationRecipientBinding.from_dict(payload)
    except LegalNotificationRecipientBindingError as error:
        _fail("L8_8H_REGISTRY_PERSISTED_RECORD_INVALID", error)


def _document(value: LegalNotificationRecipientBinding) -> dict[str, object]:
    """Serialize canonical evidence with BSON-native UTC validity timestamps."""
    document = value.to_dict()
    document["effective_from"] = value.effective_from
    document["effective_until"] = value.effective_until
    document["created_at"] = value.created_at
    return document


def _retryable(error: BaseException) -> bool:
    labels = getattr(error, "has_error_label", None)
    if callable(labels) and (labels("TransientTransactionError") or labels("UnknownTransactionCommitResult")):
        return True
    return isinstance(error, OperationFailure) and error.code in {112, 244, 251}


class LegalNotificationRecipientBindingRegistry:
    """Append and read immutable recipient bindings without transport authority."""

    def __init__(self, collection: Any) -> None:
        if collection is None:
            _fail("L8_8H_REGISTRY_COLLECTION_REQUIRED")
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create deterministic durable indexes; no TTL is permitted."""
        try:
            self._collection.create_index(
                [("tenant_id", ASCENDING), ("binding_id", ASCENDING)],
                unique=True,
                name=BINDING_IDENTITY_INDEX,
            )
            self._collection.create_index(
                [("tenant_id", ASCENDING), ("case_matter_id", ASCENDING), ("event", ASCENDING), ("effective_from", ASCENDING), ("effective_until", ASCENDING)],
                unique=False,
                name=EFFECTIVE_SCOPE_INDEX,
            )
        except PyMongoError as error:
            _fail("L8_8H_REGISTRY_INDEX_FAILED", error)

    def create_or_replay(self, value: LegalNotificationRecipientBinding, *, session: Any) -> LegalNotificationRecipientBinding:
        """Append once or return exact replay inside the caller transaction."""
        tx = _active(session)
        if type(value) is not LegalNotificationRecipientBinding:
            _fail("L8_8H_REGISTRY_BINDING_REQUIRED")
        document = _document(value)
        query = {"tenant_id": value.tenant_id, "binding_id": value.binding_id}
        try:
            existing = self._collection.find_one(query, session=tx)
            if existing is not None:
                replay = _hydrate(cast(Mapping[str, object], existing))
                if replay != value:
                    _fail("L8_8H_REGISTRY_REPLAY_CONFLICT")
                return replay
            self._collection.insert_one(document, session=tx)
            persisted = self._collection.find_one(query, session=tx)
        except DuplicateKeyError as error:
            _fail("L8_8H_REGISTRY_RETRY_TRANSACTION_REQUIRED", error)
        except LegalNotificationRecipientBindingRegistryError:
            raise
        except PyMongoError as error:
            if _retryable(error):
                _fail("L8_8H_REGISTRY_RETRY_TRANSACTION_REQUIRED", error)
            _fail("L8_8H_REGISTRY_PERSISTENCE_UNAVAILABLE", error)
        if persisted is None:
            _fail("L8_8H_REGISTRY_PERSISTENCE_UNAVAILABLE")
        hydrated = _hydrate(cast(Mapping[str, object], persisted))
        if hydrated != value:
            _fail("L8_8H_REGISTRY_PERSISTED_RECORD_INVALID")
        return hydrated

    def list_effective(self, tenant_id: str, case_matter_id: str, event: LegalNotificationEvent | str, at: datetime, *, session: Any) -> tuple[LegalNotificationRecipientBinding, ...]:
        """Return all effective exact-scope bindings; never select among them."""
        tx = _active(session)
        tenant = _identity("tenant_id", tenant_id, tenant=True)
        matter = _identity("case_matter_id", case_matter_id)
        try:
            event_value = LegalNotificationEvent(event)
        except (TypeError, ValueError) as error:
            _fail("L8_8H_REGISTRY_EVENT_INVALID", error)
        current = _utc(at)
        query = {
            "tenant_id": tenant,
            "case_matter_id": matter,
            "event": event_value.value,
            "effective_from": {"$lte": current},
            "$or": [{"effective_until": None}, {"effective_until": {"$gt": current}}],
        }
        try:
            rows = list(self._collection.find(query, session=tx))
        except PyMongoError as error:
            _fail("L8_8H_REGISTRY_PERSISTENCE_UNAVAILABLE", error)
        values = tuple(_hydrate(cast(Mapping[str, object], row)) for row in rows)
        for value in values:
            if value.tenant_id != tenant or value.case_matter_id != matter or value.event is not event_value or not value.is_effective_at(current):
                _fail("L8_8H_REGISTRY_PERSISTED_RECORD_INVALID")
        return values

    def list_scope(self, tenant_id: str, case_matter_id: str, event: LegalNotificationEvent | str, *, session: Any) -> tuple[LegalNotificationRecipientBinding, ...]:
        """Return complete immutable exact-scope history for currentness projection."""
        tx = _active(session); tenant = _identity("tenant_id", tenant_id, tenant=True); matter = _identity("case_matter_id", case_matter_id)
        try: event_value = LegalNotificationEvent(event)
        except (TypeError, ValueError) as error: _fail("L8_8H_REGISTRY_EVENT_INVALID", error)
        try: rows = list(self._collection.find({"tenant_id": tenant, "case_matter_id": matter, "event": event_value.value}, session=tx))
        except PyMongoError as error: _fail("L8_8H_REGISTRY_PERSISTENCE_UNAVAILABLE", error)
        values = tuple(_hydrate(cast(Mapping[str, object], row)) for row in rows)
        if any((value.tenant_id, value.case_matter_id, value.event) != (tenant, matter, event_value) for value in values): _fail("L8_8H_REGISTRY_PERSISTED_RECORD_INVALID")
        return values


__all__ = ["BINDING_IDENTITY_INDEX", "COLLECTION", "EFFECTIVE_SCOPE_INDEX", "VERSION", "LegalNotificationRecipientBindingRegistry", "LegalNotificationRecipientBindingRegistryError"]

# ARTIFACT: legal_notification_recipient_binding_registry.py
# VERSION: v1.1.0-L8-8H-RECIPIENT-BINDING-REGISTRY
# AUTHORITY BOUNDARY: append/replay and exact effective-scope reads only; no recipient inference or dispatch
# TENANT POSTURE: exact tenant predicate on every operation
# FAIL-CLOSED POSTURE: transaction absence, corruption, conflict, race and outage reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
