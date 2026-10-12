"""WILSY OS append-only Legal recipient-binding lifecycle registry.

TITLE: Legal Notification Recipient Binding Lifecycle Registry
VERSION: v1.0.0-L8-8H-RECIPIENT-BINDING-LIFECYCLE-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Persists exact replay-safe revocation/supersession evidence and lists
         complete exact-scope history for deterministic currentness.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_notification_recipient_binding_lifecycle_registry.py
COLLABORATION / OWNERSHIP: Lifecycle domain owns semantics; resolver owns projection.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0 establishes transaction-required append-only lifecycle storage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque identifiers/fingerprints only; no contact data.
TENANT BOUNDARY: Every query includes exact tenant and matter scope.
AUTHORITY BOUNDARY: Lifecycle persistence only; no currentness selection or dispatch.
TRANSACTION BOUNDARY: Caller owns one active transaction and all retry behavior.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing transaction, replay drift, race or corruption rejects.
"""
from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any, Final, Mapping, NoReturn, cast
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError

from tools.eos.legal_operations.domain.legal_notification_recipient_binding import LegalNotificationEvent
from tools.eos.legal_operations.domain.legal_notification_recipient_binding_lifecycle import LegalNotificationRecipientBindingLifecycle, LegalNotificationRecipientBindingLifecycleError

VERSION: Final[str] = "v1.0.0-L8-8H-RECIPIENT-BINDING-LIFECYCLE-REGISTRY"
COLLECTION: Final[str] = "legal_notification_recipient_binding_lifecycle"
IDENTITY_INDEX: Final[str] = "legal_notification_recipient_binding_lifecycle_identity_unique"
TARGET_INDEX: Final[str] = "legal_notification_recipient_binding_lifecycle_target_unique"
SCOPE_INDEX: Final[str] = "legal_notification_recipient_binding_lifecycle_scope"
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset({"default", "global", "global_root", "root", "master", "*"})


class LegalNotificationRecipientBindingLifecycleRegistryError(RuntimeError):
    """Stable code-only lifecycle registry failure."""
    def __init__(self, code: str) -> None: self.code = code; super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    error = LegalNotificationRecipientBindingLifecycleRegistryError(code)
    if cause is None: raise error
    raise error from cause


def _active(session: Any) -> Any:
    active = None if session is None else getattr(session, "in_transaction", False)
    if callable(active): active = active()
    if active is not True: _fail("L8_8H_LIFECYCLE_REGISTRY_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _identity(name: str, value: object, *, tenant: bool = False) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None or (tenant and value.casefold() in _FORBIDDEN_TENANTS):
        _fail(f"L8_8H_LIFECYCLE_REGISTRY_{name.upper()}_INVALID")
    return value


def _hydrate(row: Mapping[str, object]) -> LegalNotificationRecipientBindingLifecycle:
    payload = {key: value for key, value in row.items() if key != "_id"}
    for field in ("effective_at", "created_at"):
        value = payload.get(field)
        if isinstance(value, datetime) and value.tzinfo is None: payload[field] = value.replace(tzinfo=timezone.utc)
    try: return LegalNotificationRecipientBindingLifecycle.from_dict(payload)
    except LegalNotificationRecipientBindingLifecycleError as error: _fail("L8_8H_LIFECYCLE_REGISTRY_PERSISTED_RECORD_INVALID", error)


def _document(value: LegalNotificationRecipientBindingLifecycle) -> dict[str, object]:
    result = value.to_dict(); result["effective_at"] = value.effective_at; result["created_at"] = value.created_at; return result


class LegalNotificationRecipientBindingLifecycleRegistry:
    """Append and enumerate immutable lifecycle evidence without selecting a winner."""
    def __init__(self, collection: Any) -> None:
        if collection is None: _fail("L8_8H_LIFECYCLE_REGISTRY_COLLECTION_REQUIRED")
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create deterministic identity, single-target and history indexes without TTL."""
        try:
            self._collection.create_index([("tenant_id", ASCENDING), ("lifecycle_event_id", ASCENDING)], unique=True, name=IDENTITY_INDEX)
            self._collection.create_index([("tenant_id", ASCENDING), ("target_binding_id", ASCENDING)], unique=True, name=TARGET_INDEX)
            self._collection.create_index([("tenant_id", ASCENDING), ("case_matter_id", ASCENDING), ("event", ASCENDING), ("effective_at", ASCENDING)], unique=False, name=SCOPE_INDEX)
        except PyMongoError as error: _fail("L8_8H_LIFECYCLE_REGISTRY_INDEX_FAILED", error)

    def create_or_replay(self, value: LegalNotificationRecipientBindingLifecycle, *, session: Any) -> LegalNotificationRecipientBindingLifecycle:
        """Append one termination event or replay the exact same evidence."""
        tx = _active(session)
        if type(value) is not LegalNotificationRecipientBindingLifecycle: _fail("L8_8H_LIFECYCLE_REGISTRY_VALUE_REQUIRED")
        query = {"tenant_id": value.tenant_id, "lifecycle_event_id": value.lifecycle_event_id}
        try:
            existing = self._collection.find_one(query, session=tx)
            if existing is not None:
                replay = _hydrate(cast(Mapping[str, object], existing))
                if replay != value: _fail("L8_8H_LIFECYCLE_REGISTRY_REPLAY_CONFLICT")
                return replay
            self._collection.insert_one(_document(value), session=tx)
            persisted = self._collection.find_one(query, session=tx)
        except DuplicateKeyError as error: _fail("L8_8H_LIFECYCLE_REGISTRY_RETRY_TRANSACTION_REQUIRED", error)
        except LegalNotificationRecipientBindingLifecycleRegistryError: raise
        except PyMongoError as error:
            labels = getattr(error, "has_error_label", lambda _: False)
            if labels("TransientTransactionError") or isinstance(error, OperationFailure) and error.code in {112, 244, 251}: _fail("L8_8H_LIFECYCLE_REGISTRY_RETRY_TRANSACTION_REQUIRED", error)
            _fail("L8_8H_LIFECYCLE_REGISTRY_PERSISTENCE_UNAVAILABLE", error)
        if persisted is None: _fail("L8_8H_LIFECYCLE_REGISTRY_PERSISTENCE_UNAVAILABLE")
        hydrated = _hydrate(cast(Mapping[str, object], persisted))
        if hydrated != value: _fail("L8_8H_LIFECYCLE_REGISTRY_PERSISTED_RECORD_INVALID")
        return hydrated

    def list_scope(self, tenant_id: str, case_matter_id: str, event: LegalNotificationEvent | str, *, session: Any) -> tuple[LegalNotificationRecipientBindingLifecycle, ...]:
        """Return complete exact-scope history without sorting or implicit selection."""
        tx = _active(session)
        tenant = _identity("tenant_id", tenant_id, tenant=True); matter = _identity("case_matter_id", case_matter_id)
        try: event_value = LegalNotificationEvent(event)
        except (TypeError, ValueError) as error: _fail("L8_8H_LIFECYCLE_REGISTRY_EVENT_INVALID", error)
        query = {"tenant_id": tenant, "case_matter_id": matter, "event": event_value.value}
        try: rows = list(self._collection.find(query, session=tx))
        except PyMongoError as error: _fail("L8_8H_LIFECYCLE_REGISTRY_PERSISTENCE_UNAVAILABLE", error)
        values = tuple(_hydrate(cast(Mapping[str, object], row)) for row in rows)
        if any((value.tenant_id, value.case_matter_id, value.event) != (tenant, matter, event_value) for value in values): _fail("L8_8H_LIFECYCLE_REGISTRY_PERSISTED_RECORD_INVALID")
        return values


__all__ = ["COLLECTION", "IDENTITY_INDEX", "SCOPE_INDEX", "TARGET_INDEX", "VERSION", "LegalNotificationRecipientBindingLifecycleRegistry", "LegalNotificationRecipientBindingLifecycleRegistryError"]

# ARTIFACT: legal_notification_recipient_binding_lifecycle_registry.py
# VERSION: v1.0.0-L8-8H-RECIPIENT-BINDING-LIFECYCLE-REGISTRY
# AUTHORITY BOUNDARY: append/replay and complete exact-scope lifecycle reads only
# TENANT POSTURE: exact tenant/matter/event predicates; no global lookup
# FAIL-CLOSED POSTURE: transaction misuse, conflict, race, corruption and outage reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
