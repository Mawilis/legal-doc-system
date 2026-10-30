"""G78 append-only Mongo registry for wall membership and acknowledgement evidence."""
from __future__ import annotations

from dataclasses import fields, replace
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_work_ethical_wall_membership_acknowledgement import (
    WallMembershipEvidence, WallAcknowledgementEvidence,
)

VERSION: Final[str] = "v1.0.0-G78-WALL-MEMBERSHIP-ACK-REGISTRY"
MEMBERSHIP_COLLECTION: Final[str] = "legal_work_ethical_wall_membership_evidence"
ACKNOWLEDGEMENT_COLLECTION: Final[str] = "legal_work_ethical_wall_acknowledgement_evidence"
MAX_HISTORY: Final[int] = 128


class WallEvidenceRegistryError(RuntimeError):
    pass


class WallEvidenceTransactionRequired(WallEvidenceRegistryError):
    pass


class WallEvidenceConflict(WallEvidenceRegistryError):
    pass


class WallEvidenceNotFound(WallEvidenceRegistryError):
    pass


class WallEvidencePersistedInvalid(WallEvidenceRegistryError):
    pass


class WallEvidenceRetryTransaction(WallEvidenceRegistryError):
    pass


class WallEvidencePersistenceUnavailable(WallEvidenceRegistryError):
    pass


def _tx(session: object) -> object:
    try:
        active = getattr(session, "in_transaction", False)
        active = active() if callable(active) else active
    except Exception:
        active = False
    if active is not True:
        raise WallEvidenceTransactionRequired("G78_WALL_TRANSACTION_REQUIRED")
    return session


def _fields(cls: type) -> tuple[str, ...]:
    return tuple(item.name for item in fields(cls))


def _encode(value: object, cls: type) -> dict[str, object]:
    if type(value) is not cls:
        raise WallEvidencePersistedInvalid("G78_WALL_EVIDENCE_TYPE_INVALID")
    try:
        canonical = replace(value)
    except Exception as error:
        raise WallEvidencePersistedInvalid("G78_WALL_EVIDENCE_INVALID") from error
    if canonical != value:
        raise WallEvidencePersistedInvalid("G78_WALL_EVIDENCE_INVALID")
    return {name: getattr(value, name) for name in _fields(cls)}


def _decode(raw: object, cls: type) -> object:
    if type(raw) is not dict:
        raise WallEvidencePersistedInvalid("G78_WALL_DOCUMENT_INVALID")
    document = dict(raw)
    document.pop("_id", None)
    names = set(_fields(cls))
    if set(document) != names:
        raise WallEvidencePersistedInvalid("G78_WALL_DOCUMENT_SHAPE_INVALID")
    try:
        value = cls(**{name: document[name] for name in names if name != "fingerprint"})
    except Exception as error:
        raise WallEvidencePersistedInvalid("G78_WALL_DOCUMENT_INVALID") from error
    if value.fingerprint != document["fingerprint"]:
        raise WallEvidencePersistedInvalid("G78_WALL_FINGERPRINT_INVALID")
    return value


class WallMembershipAcknowledgementRegistry:
    """Immutable history reads/writes; no current pointer and no access authority."""

    def __init__(self, membership_collection: Any, acknowledgement_collection: Any) -> None:
        self._memberships = membership_collection
        self._acknowledgements = acknowledgement_collection

    def ensure_indexes(self) -> None:
        for collection, prefix in (
            (self._memberships, "g78_wall_membership"),
            (self._acknowledgements, "g78_wall_acknowledgement"),
        ):
            collection.create_index(
                [("tenant_id", ASCENDING), ("case_matter_id", ASCENDING),
                 ("policy_id", ASCENDING), ("practitioner_principal_id", ASCENDING),
                 ("revision", ASCENDING)],
                name=prefix + "_revision_unique", unique=True,
            )
            collection.create_index(
                [("tenant_id", ASCENDING), ("fingerprint", ASCENDING)],
                name=prefix + "_fingerprint_unique", unique=True,
            )

    def _history(self, collection: Any, scope: dict[str, str], cls: type, session: object) -> tuple[object, ...]:
        tx = _tx(session)
        try:
            rows = tuple(collection.find(scope, session=tx).sort("revision", ASCENDING).limit(MAX_HISTORY + 1))
        except Exception as error:
            if isinstance(error, PyMongoError) and error.has_error_label("TransientTransactionError"):
                raise WallEvidenceRetryTransaction("G78_WALL_RETRY_TRANSACTION") from error
            raise WallEvidencePersistenceUnavailable("G78_WALL_READ_UNAVAILABLE") from error
        if len(rows) > MAX_HISTORY:
            raise WallEvidencePersistedInvalid("G78_WALL_HISTORY_OVERLONG")
        values = tuple(_decode(row, cls) for row in rows)
        if values:
            first = values[0]
            if any(
                getattr(item, key) != scope[key]
                for item in values
                for key in ("tenant_id", "case_matter_id", "policy_id", "practitioner_principal_id")
            ):
                raise WallEvidencePersistedInvalid("G78_WALL_SCOPE_MISMATCH")
            if [item.revision for item in values] != list(range(1, len(values) + 1)):
                raise WallEvidencePersistedInvalid("G78_WALL_REVISION_GAP")
            identity_name = "membership_id" if cls is WallMembershipEvidence else "acknowledgement_id"
            if any(getattr(item, identity_name) != getattr(first, identity_name) for item in values):
                raise WallEvidencePersistedInvalid("G78_WALL_IDENTITY_DRIFT")
            for previous, current in zip(values, values[1:]):
                previous_time = getattr(previous, "effective_at", getattr(previous, "acknowledged_at", None))
                current_time = getattr(current, "effective_at", getattr(current, "acknowledged_at", None))
                if current.predecessor_fingerprint != previous.fingerprint or current_time <= previous_time:
                    raise WallEvidencePersistedInvalid("G78_WALL_LINEAGE_INVALID")
        return values

    def list_membership_history(self, tenant_id: str, case_matter_id: str, policy_id: str,
                                 practitioner_principal_id: str, *, session: object) -> tuple[WallMembershipEvidence, ...]:
        scope = {"tenant_id": tenant_id, "case_matter_id": case_matter_id,
                 "policy_id": policy_id, "practitioner_principal_id": practitioner_principal_id}
        return self._history(self._memberships, scope, WallMembershipEvidence, session)  # type: ignore[return-value]

    def list_acknowledgement_history(self, tenant_id: str, case_matter_id: str, policy_id: str,
                                     practitioner_principal_id: str, *, session: object) -> tuple[WallAcknowledgementEvidence, ...]:
        scope = {"tenant_id": tenant_id, "case_matter_id": case_matter_id,
                 "policy_id": policy_id, "practitioner_principal_id": practitioner_principal_id}
        return self._history(self._acknowledgements, scope, WallAcknowledgementEvidence, session)  # type: ignore[return-value]

    def _append(self, collection: Any, value: object, cls: type, session: object) -> object:
        tx = _tx(session)
        document = _encode(value, cls)
        scope = {key: document[key] for key in (
            "tenant_id", "case_matter_id", "policy_id", "practitioner_principal_id"
        )}
        identity = {**scope, "revision": document["revision"]}
        try:
            history = self._history(collection, scope, cls, tx)
            existing = collection.find_one(identity, session=tx)
            if existing is not None:
                prior = _decode(existing, cls)
                if prior != value:
                    raise WallEvidenceConflict("G78_WALL_DIVERGENT_REPLAY")
                return prior
            if not history:
                if document["revision"] != 1 or document["predecessor_fingerprint"] is not None:
                    raise WallEvidenceConflict("G78_WALL_ORPHAN_REVISION")
            else:
                leaf = history[-1]
                if document["revision"] != leaf.revision + 1 or document["predecessor_fingerprint"] != leaf.fingerprint:
                    raise WallEvidenceConflict("G78_WALL_STALE_REVISION")
                leaf_state = getattr(leaf, "state", None)
                if getattr(leaf_state, "value", leaf_state) == "REVOKED":
                    raise WallEvidenceConflict("G78_WALL_TERMINAL_REVOKED")
            collection.insert_one(document, session=tx)
        except (WallEvidenceConflict, WallEvidencePersistedInvalid, WallEvidenceRetryTransaction):
            raise
        except DuplicateKeyError as error:
            raise WallEvidenceRetryTransaction("G78_WALL_CONCURRENT_APPEND_RETRY") from error
        except Exception as error:
            if isinstance(error, PyMongoError) and error.has_error_label("TransientTransactionError"):
                raise WallEvidenceRetryTransaction("G78_WALL_RETRY_TRANSACTION") from error
            raise WallEvidencePersistenceUnavailable("G78_WALL_WRITE_UNAVAILABLE") from error
        return value

    def append_membership(self, value: WallMembershipEvidence, *, session: object) -> WallMembershipEvidence:
        return self._append(self._memberships, value, WallMembershipEvidence, session)  # type: ignore[return-value]

    def append_acknowledgement(self, value: WallAcknowledgementEvidence, *, session: object) -> WallAcknowledgementEvidence:
        return self._append(self._acknowledgements, value, WallAcknowledgementEvidence, session)  # type: ignore[return-value]


__all__ = [
    "VERSION", "MEMBERSHIP_COLLECTION", "ACKNOWLEDGEMENT_COLLECTION", "MAX_HISTORY",
    "WallEvidenceRegistryError", "WallEvidenceTransactionRequired", "WallEvidenceConflict",
    "WallEvidenceNotFound", "WallEvidencePersistedInvalid", "WallEvidenceRetryTransaction",
    "WallEvidencePersistenceUnavailable", "WallMembershipAcknowledgementRegistry",
]
