"""WILSY OS durable internal-service workload credential authority registry.

TITLE: Internal-Service Workload Credential Authority Registry
VERSION: v1.0.0-P3-R3G-S6-A1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Append-only credential lifecycle evidence with one CAS-protected current pointer per service/key.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/internal_service_workload_credential_registry.py
COLLABORATION / OWNERSHIP: Workload credential domain and verified workload-proof orchestration.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0-P3-R3G-S6-A1 establishes immutable history, exact replay, current pointers, rotation, and terminal transitions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Persists only nonsecret identifiers and SHA3-512 evidence; no TTL.
TENANT BOUNDARY: Platform/internal only; no tenant identity or authorization.
AUTHORITY BOUNDARY: Credential binding/currentness persistence only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Every read/write requires the caller's active Mongo transaction.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.internal_service_workload_credential_authority import (
    PLATFORM_INTERNAL_SCOPE,
    InternalServiceWorkloadCredentialAuthority,
    InternalServiceWorkloadCredentialAuthorityError,
    WorkloadCredentialLifecycleStatus,
)

VERSION: Final[str] = "v1.0.0-P3-R3G-S6-A1"
COLLECTION: Final[str] = "internal_service_workload_credential_authority_history"
POINTER_COLLECTION: Final[str] = "internal_service_workload_credential_authority_current"


class InternalServiceWorkloadCredentialRegistryError(RuntimeError):
    """Base bounded registry failure without secret or cross-identity disclosure."""


class InternalServiceWorkloadCredentialTransactionRequiredError(InternalServiceWorkloadCredentialRegistryError):
    """Caller did not supply an active transaction."""


class InternalServiceWorkloadCredentialNotCurrentError(InternalServiceWorkloadCredentialRegistryError):
    """Exact service/key binding is absent, terminal, stale, or corrupt."""


class InternalServiceWorkloadCredentialConflictError(InternalServiceWorkloadCredentialRegistryError):
    """Idempotency, uniqueness, or concurrent currentness mutation conflict."""


class InternalServiceWorkloadCredentialPersistedInvalidError(InternalServiceWorkloadCredentialRegistryError):
    """Persisted authority history or pointer failed strict validation."""


def _tx(session: object) -> Any:
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise InternalServiceWorkloadCredentialTransactionRequiredError("ACTIVE_TRANSACTION_REQUIRED")
    return session


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise InternalServiceWorkloadCredentialRegistryError(f"INVALID_{name.upper()}")
    return value


class InternalServiceWorkloadCredentialRegistry:
    """Own immutable history and one exact current service/key pointer.

    The class never starts, commits, aborts, or retries a transaction and never
    receives or stores raw HMAC secrets.
    """

    def __init__(self, history_collection: Any, pointer_collection: Any) -> None:
        self._history = history_collection
        self._pointers = pointer_collection

    def ensure_indexes(self) -> None:
        """Create explicit non-TTL uniqueness, replay, and lookup indexes."""
        self._history.create_index(
            [("service_id", ASCENDING), ("key_id", ASCENDING), ("credential_revision", ASCENDING), ("lifecycle_revision", ASCENDING)],
            unique=True, name="internal_workload_credential_lifecycle_unique",
        )
        self._history.create_index(
            [("authority_fingerprint", ASCENDING)], unique=True, name="internal_workload_credential_fingerprint_unique",
        )
        self._history.create_index(
            [("service_id", ASCENDING), ("key_id", ASCENDING), ("status_changed_at", ASCENDING)],
            name="internal_workload_credential_timeline",
        )
        self._pointers.create_index(
            [("service_id", ASCENDING), ("key_id", ASCENDING)], unique=True, name="internal_workload_credential_current_unique",
        )
        self._pointers.create_index(
            [("principal_id", ASCENDING), ("credential_scope", ASCENDING)], name="internal_workload_credential_principal_scope",
        )

    def _hydrate(self, row: object) -> InternalServiceWorkloadCredentialAuthority:
        if not isinstance(row, dict):
            raise InternalServiceWorkloadCredentialPersistedInvalidError("AUTHORITY_ROW_INVALID")
        try:
            return InternalServiceWorkloadCredentialAuthority.from_persisted(row)
        except InternalServiceWorkloadCredentialAuthorityError as error:
            raise InternalServiceWorkloadCredentialPersistedInvalidError("AUTHORITY_ROW_INVALID") from error

    def _history_by_fingerprint(self, fingerprint: str, *, session: object) -> InternalServiceWorkloadCredentialAuthority | None:
        tx = _tx(session)
        try:
            row = self._history.find_one({"authority_fingerprint": fingerprint}, session=tx)
        except PyMongoError as error:
            raise InternalServiceWorkloadCredentialRegistryError("AUTHORITY_READ_FAILED") from error
        return None if row is None else self._hydrate(row)

    def resolve_current(self, *, service_id: str, key_id: str, session: object) -> InternalServiceWorkloadCredentialAuthority:
        """Resolve exactly one CURRENT binding; return identical denial for absence or terminal state."""
        tx = _tx(session)
        service = _text("service_id", service_id)
        key = _text("key_id", key_id)
        try:
            pointer = self._pointers.find_one({"service_id": service, "key_id": key}, session=tx)
        except PyMongoError as error:
            raise InternalServiceWorkloadCredentialRegistryError("AUTHORITY_READ_FAILED") from error
        if not isinstance(pointer, dict):
            raise InternalServiceWorkloadCredentialNotCurrentError("WORKLOAD_CREDENTIAL_NOT_CURRENT")
        required = {"service_id", "key_id", "principal_id", "credential_scope", "credential_revision", "lifecycle_revision", "lifecycle_status", "authority_fingerprint"}
        clean = {name: value for name, value in pointer.items() if name != "_id"}
        if set(clean) != required:
            raise InternalServiceWorkloadCredentialPersistedInvalidError("CURRENT_POINTER_INVALID")
        if clean["lifecycle_status"] != WorkloadCredentialLifecycleStatus.CURRENT.value:
            raise InternalServiceWorkloadCredentialNotCurrentError("WORKLOAD_CREDENTIAL_NOT_CURRENT")
        fingerprint = clean["authority_fingerprint"]
        if not isinstance(fingerprint, str):
            raise InternalServiceWorkloadCredentialPersistedInvalidError("CURRENT_POINTER_INVALID")
        authority = self._history_by_fingerprint(fingerprint, session=tx)
        if authority is None or authority.lifecycle_status is not WorkloadCredentialLifecycleStatus.CURRENT:
            raise InternalServiceWorkloadCredentialPersistedInvalidError("CURRENT_HISTORY_INVALID")
        for name in required - {"authority_fingerprint", "lifecycle_status"}:
            if clean[name] != getattr(authority, name):
                raise InternalServiceWorkloadCredentialPersistedInvalidError("CURRENT_POINTER_MISMATCH")
        return authority

    def create_or_replay(self, authority: InternalServiceWorkloadCredentialAuthority, *, session: object) -> InternalServiceWorkloadCredentialAuthority:
        """Create the first CURRENT generation or return an exact immutable replay."""
        tx = _tx(session)
        if not isinstance(authority, InternalServiceWorkloadCredentialAuthority):
            raise InternalServiceWorkloadCredentialRegistryError("AUTHORITY_REQUIRED")
        if authority.lifecycle_status is not WorkloadCredentialLifecycleStatus.CURRENT or authority.lifecycle_revision != 1:
            raise InternalServiceWorkloadCredentialConflictError("INITIAL_AUTHORITY_INVALID")
        existing = self._history_by_fingerprint(authority.authority_fingerprint or "", session=tx)
        if existing is not None:
            if existing == authority:
                current = self.resolve_current(service_id=authority.service_id, key_id=authority.key_id, session=tx)
                if current == authority:
                    return current
            raise InternalServiceWorkloadCredentialConflictError("DIVERGENT_REPLAY")
        pointer = self._pointer(authority)
        try:
            self._history.insert_one(authority.to_persisted(), session=tx)
            self._pointers.insert_one(pointer, session=tx)
        except DuplicateKeyError as error:
            raise InternalServiceWorkloadCredentialConflictError("AUTHORITY_CONFLICT") from error
        except PyMongoError as error:
            if error.has_error_label("TransientTransactionError"):
                raise
            raise InternalServiceWorkloadCredentialRegistryError("AUTHORITY_PERSISTENCE_FAILED") from error
        return authority

    @staticmethod
    def _pointer(authority: InternalServiceWorkloadCredentialAuthority) -> dict[str, object]:
        return {
            "service_id": authority.service_id, "key_id": authority.key_id, "principal_id": authority.principal_id,
            "credential_scope": authority.credential_scope, "credential_revision": authority.credential_revision,
            "lifecycle_revision": authority.lifecycle_revision, "lifecycle_status": authority.lifecycle_status.value,
            "authority_fingerprint": authority.authority_fingerprint,
        }

    def transition(
        self, *, service_id: str, key_id: str, target_status: WorkloadCredentialLifecycleStatus,
        changed_at: datetime, session: object,
    ) -> InternalServiceWorkloadCredentialAuthority:
        """Append one terminal snapshot and CAS the current pointer."""
        tx = _tx(session)
        if target_status not in {WorkloadCredentialLifecycleStatus.REVOKED, WorkloadCredentialLifecycleStatus.ROTATED, WorkloadCredentialLifecycleStatus.INVALIDATED}:
            raise InternalServiceWorkloadCredentialConflictError("TERMINAL_STATUS_REQUIRED")
        current = self.resolve_current(service_id=service_id, key_id=key_id, session=tx)
        terminal = InternalServiceWorkloadCredentialAuthority(
            service_id=current.service_id, key_id=current.key_id, principal_id=current.principal_id,
            credential_scope=current.credential_scope, credential_revision=current.credential_revision,
            lifecycle_revision=current.lifecycle_revision + 1, lifecycle_status=target_status,
            status_changed_at=changed_at, previous_fingerprint=current.authority_fingerprint,
        )
        try:
            self._history.insert_one(terminal.to_persisted(), session=tx)
            result = self._pointers.replace_one(
                {"service_id": current.service_id, "key_id": current.key_id, "authority_fingerprint": current.authority_fingerprint},
                self._pointer(terminal), session=tx,
            )
        except DuplicateKeyError as error:
            raise InternalServiceWorkloadCredentialConflictError("AUTHORITY_CONFLICT") from error
        except PyMongoError as error:
            if error.has_error_label("TransientTransactionError"):
                raise
            raise InternalServiceWorkloadCredentialRegistryError("AUTHORITY_PERSISTENCE_FAILED") from error
        if getattr(result, "matched_count", 0) != 1:
            raise InternalServiceWorkloadCredentialConflictError("CURRENTNESS_CONFLICT")
        return terminal

    def rotate(
        self, *, service_id: str, key_id: str, next_key_id: str, changed_at: datetime, session: object,
    ) -> InternalServiceWorkloadCredentialAuthority:
        """Terminate the old generation as ROTATED and create the next exact key generation."""
        tx = _tx(session)
        old = self.resolve_current(service_id=service_id, key_id=key_id, session=tx)
        self.transition(service_id=service_id, key_id=key_id, target_status=WorkloadCredentialLifecycleStatus.ROTATED, changed_at=changed_at, session=tx)
        next_authority = InternalServiceWorkloadCredentialAuthority(
            service_id=old.service_id, key_id=_text("next_key_id", next_key_id), principal_id=old.principal_id,
            credential_scope=PLATFORM_INTERNAL_SCOPE, credential_revision=old.credential_revision + 1,
            lifecycle_revision=1, lifecycle_status=WorkloadCredentialLifecycleStatus.CURRENT,
            status_changed_at=changed_at,
        )
        return self.create_or_replay(next_authority, session=tx)


__all__ = [
    "VERSION", "COLLECTION", "POINTER_COLLECTION", "InternalServiceWorkloadCredentialRegistryError",
    "InternalServiceWorkloadCredentialTransactionRequiredError", "InternalServiceWorkloadCredentialNotCurrentError",
    "InternalServiceWorkloadCredentialConflictError", "InternalServiceWorkloadCredentialPersistedInvalidError",
    "InternalServiceWorkloadCredentialRegistry",
]

# ARTIFACT: internal_service_workload_credential_registry.py
# VERSION: v1.0.0-P3-R3G-S6-A1
# AUTHORITY BOUNDARY: Secret-free internal credential history and current-pointer persistence only.
# TENANT POSTURE: Platform/internal; no tenant authority.
# FAIL-CLOSED POSTURE: Active transaction, exact current pointer, immutable history, and CAS are mandatory.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
