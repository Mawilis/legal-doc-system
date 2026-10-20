"""
WILSY OS — ENGINEERING MERKLE CHECKPOINT REGISTRY
VERSION: 1.0.0-EMP-P21
AUTHORITY: Engineering Kernel transactional checkpoint persistence.
EPITOME: Immutable checkpoint lineage and one CAS-governed current head.
ABSOLUTE CANONICAL PATH: tools/eos/kernel/engineering_merkle_checkpoint_registry.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
CHANGELOG: P21 initial caller-owned transaction and current-head registry.
COMPLIANCE: EK-001, EK-002, EK-003, EK-005, EK-007.
SECURITY: Exact hydration, immutable history, stale CAS rejection.
TENANT BOUNDARY: Institution and evidence log exact scoping.
TRANSACTION BOUNDARY: Caller owns transaction and its rollback.
AUTHORITY BOUNDARY: No signature, approval, release or external anchoring.
FINANCIAL EXECUTION AUTHORITY: None.

A caller MUST abort its transaction on a failed advancement. The registry
never retries only a part of a multi-write transaction. Competing transaction
certification against real MongoDB remains a separate mandatory gate.
"""

from __future__ import annotations

import re
from typing import Any, Protocol

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.kernel.engineering_merkle_checkpoint import (
    EngineeringMerkleCheckpoint,
)

HISTORY_IDENTITY_INDEX = "engineering_merkle_checkpoint_history_identity_unique"
HISTORY_HASH_INDEX = "engineering_merkle_checkpoint_hash_unique"
CURRENT_IDENTITY_INDEX = "engineering_merkle_checkpoint_current_identity_unique"

_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", re.ASCII)
_HEX = re.compile(r"[0-9a-f]{64}", re.ASCII)
_POINTER_FIELDS = frozenset({
    "institution_id", "log_id", "checkpoint_hash", "leaf_count",
})


class EngineeringMerkleCheckpointTransactionRequired(RuntimeError):
    """An explicit caller-owned active transaction is mandatory."""


class EngineeringMerkleCheckpointConflict(RuntimeError):
    """A proposed checkpoint conflicts with durable canonical head."""


class EngineeringMerkleCheckpointPersistedInvalid(RuntimeError):
    """The stored checkpoint history or pointer is inconsistent."""


class EngineeringMerkleCheckpointPersistenceUnavailable(RuntimeError):
    """Mongo persistence operations failed without granting authority."""


class _Collection(Protocol):
    def create_index(self, keys: Any, **kwargs: Any) -> Any: ...
    def find_one(self, filter: Any, **kwargs: Any) -> Any: ...
    def find(self, filter: Any, **kwargs: Any) -> Any: ...
    def insert_one(self, document: Any, **kwargs: Any) -> Any: ...
    def update_one(self, filter: Any, update: Any, **kwargs: Any) -> Any: ...


def _identity(value: object, label: str) -> str:
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        raise ValueError("INVALID_" + label.upper())
    return value


def _hash(value: object) -> str:
    if type(value) is not str or _HEX.fullmatch(value) is None:
        raise ValueError("INVALID_CHECKPOINT_HASH")
    return value


def _transaction(session: Any) -> Any:
    try:
        active = getattr(session, "in_transaction", None) is True
    except Exception as exc:
        raise EngineeringMerkleCheckpointTransactionRequired(
            "ACTIVE_TRANSACTION_REQUIRED"
        ) from exc
    if not active:
        raise EngineeringMerkleCheckpointTransactionRequired(
            "ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


def _checkpoint(document: object) -> EngineeringMerkleCheckpoint:
    if type(document) is not dict:
        raise EngineeringMerkleCheckpointPersistedInvalid(
            "CHECKPOINT_DOCUMENT_INVALID"
        )
    clean = dict(document)
    clean.pop("_id", None)
    try:
        return EngineeringMerkleCheckpoint.from_dict(clean)
    except (TypeError, ValueError, KeyError) as exc:
        raise EngineeringMerkleCheckpointPersistedInvalid(
            "CHECKPOINT_INTEGRITY_INVALID"
        ) from exc


def _pointer(document: object) -> dict[str, Any]:
    if type(document) is not dict:
        raise EngineeringMerkleCheckpointPersistedInvalid(
            "CURRENT_POINTER_DOCUMENT_INVALID"
        )
    clean = dict(document)
    clean.pop("_id", None)
    if set(clean) != _POINTER_FIELDS:
        raise EngineeringMerkleCheckpointPersistedInvalid(
            "CURRENT_POINTER_FIELDS_INVALID"
        )
    try:
        _identity(clean["institution_id"], "institution_id")
        _identity(clean["log_id"], "log_id")
        _hash(clean["checkpoint_hash"])
        if type(clean["leaf_count"]) is not int or clean["leaf_count"] < 0:
            raise ValueError("INVALID_POINTER_COUNT")
    except (TypeError, ValueError) as exc:
        raise EngineeringMerkleCheckpointPersistedInvalid(
            "CURRENT_POINTER_INTEGRITY_INVALID"
        ) from exc
    return clean


class EngineeringMerkleCheckpointRegistry:
    """Caller-transactional checkpoint history plus one current-head pointer."""

    def __init__(
        self,
        history_collection: _Collection,
        current_collection: _Collection,
    ) -> None:
        self._history = history_collection
        self._current = current_collection

    def ensure_indexes(self) -> None:
        try:
            self._history.create_index(
                [
                    ("institution_id", ASCENDING),
                    ("log_id", ASCENDING),
                    ("leaf_count", ASCENDING),
                ],
                unique=True,
                name=HISTORY_IDENTITY_INDEX,
            )
            self._history.create_index(
                [
                    ("institution_id", ASCENDING),
                    ("log_id", ASCENDING),
                    ("checkpoint_hash", ASCENDING),
                ],
                unique=True,
                name=HISTORY_HASH_INDEX,
            )
            self._current.create_index(
                [
                    ("institution_id", ASCENDING),
                    ("log_id", ASCENDING),
                ],
                unique=True,
                name=CURRENT_IDENTITY_INDEX,
            )
        except PyMongoError as exc:
            raise EngineeringMerkleCheckpointPersistenceUnavailable(
                "CHECKPOINT_INDEX_CREATION_FAILED"
            ) from exc

    def _read_pointer(
        self, institution_id: str, log_id: str, session: Any = None
    ) -> dict[str, Any] | None:
        query = {"institution_id": institution_id, "log_id": log_id}
        try:
            document = self._current.find_one(query, session=session)
        except PyMongoError as exc:
            raise EngineeringMerkleCheckpointPersistenceUnavailable(
                "CURRENT_POINTER_READ_FAILED"
            ) from exc
        return None if document is None else _pointer(document)

    def get_history(
        self,
        *,
        institution_id: str,
        log_id: str,
        session: Any = None,
    ) -> tuple[EngineeringMerkleCheckpoint, ...]:
        institution = _identity(institution_id, "institution_id")
        log = _identity(log_id, "log_id")
        try:
            documents = list(
                self._history.find(
                    {"institution_id": institution, "log_id": log},
                    session=session,
                )
            )
        except PyMongoError as exc:
            raise EngineeringMerkleCheckpointPersistenceUnavailable(
                "CHECKPOINT_HISTORY_READ_FAILED"
            ) from exc

        values = [_checkpoint(document) for document in documents]
        values.sort(key=lambda value: value.leaf_count)
        if values:
            first = values[0]
            if first.previous_checkpoint_hash is not None:
                raise EngineeringMerkleCheckpointPersistedInvalid(
                    "CHECKPOINT_GENESIS_LINK_INVALID"
                )
            for previous, current in zip(values, values[1:]):
                if (
                    current.previous_checkpoint_hash != previous.checkpoint_hash
                    or current.leaf_count <= previous.leaf_count
                    or current.leaf_commitments[:previous.leaf_count]
                    != previous.leaf_commitments
                ):
                    raise EngineeringMerkleCheckpointPersistedInvalid(
                        "CHECKPOINT_HISTORY_CHAIN_INVALID"
                    )

        return tuple(values)

    def get_current(
        self,
        *,
        institution_id: str,
        log_id: str,
        session: Any = None,
    ) -> EngineeringMerkleCheckpoint | None:
        institution = _identity(institution_id, "institution_id")
        log = _identity(log_id, "log_id")
        pointer = self._read_pointer(institution, log, session=session)
        history = self.get_history(
            institution_id=institution, log_id=log, session=session
        )
        if pointer is None:
            if history:
                raise EngineeringMerkleCheckpointPersistedInvalid(
                    "ORPHAN_CHECKPOINT_HISTORY"
                )
            return None
        if not history:
            raise EngineeringMerkleCheckpointPersistedInvalid(
                "MISSING_CHECKPOINT_HISTORY"
            )
        latest = history[-1]
        if (
            pointer["checkpoint_hash"] != latest.checkpoint_hash
            or pointer["leaf_count"] != latest.leaf_count
            or pointer["institution_id"] != latest.institution_id
            or pointer["log_id"] != latest.log_id
        ):
            raise EngineeringMerkleCheckpointPersistedInvalid(
                "CURRENT_POINTER_HISTORY_MISMATCH"
            )
        return latest

    def create_genesis(
        self,
        checkpoint: EngineeringMerkleCheckpoint,
        *,
        session: Any,
    ) -> EngineeringMerkleCheckpoint:
        active = _transaction(session)
        if type(checkpoint) is not EngineeringMerkleCheckpoint:
            raise TypeError("CHECKPOINT_REQUIRED")
        if checkpoint.previous_checkpoint_hash is not None:
            raise EngineeringMerkleCheckpointConflict(
                "GENESIS_CANNOT_HAVE_PREDECESSOR"
            )
        existing = self.get_current(
            institution_id=checkpoint.institution_id,
            log_id=checkpoint.log_id,
            session=active,
        )
        if existing is not None:
            if existing == checkpoint and len(self.get_history(
                institution_id=checkpoint.institution_id,
                log_id=checkpoint.log_id,
                session=active,
            )) == 1:
                return existing
            raise EngineeringMerkleCheckpointConflict(
                "GENESIS_ALREADY_EXISTS"
            )

        pointer = {
            "institution_id": checkpoint.institution_id,
            "log_id": checkpoint.log_id,
            "checkpoint_hash": checkpoint.checkpoint_hash,
            "leaf_count": checkpoint.leaf_count,
        }
        try:
            self._history.insert_one(checkpoint.to_dict(), session=active)
            self._current.insert_one(pointer, session=active)
        except DuplicateKeyError as exc:
            raise EngineeringMerkleCheckpointConflict(
                "GENESIS_CONCURRENT_COLLISION_ABORT_TRANSACTION"
            ) from exc
        except PyMongoError as exc:
            raise EngineeringMerkleCheckpointPersistenceUnavailable(
                "GENESIS_PERSISTENCE_FAILED_ABORT_TRANSACTION"
            ) from exc
        return checkpoint

    def advance(
        self,
        checkpoint: EngineeringMerkleCheckpoint,
        *,
        expected_checkpoint_hash: str,
        session: Any,
    ) -> EngineeringMerkleCheckpoint:
        active = _transaction(session)
        if type(checkpoint) is not EngineeringMerkleCheckpoint:
            raise TypeError("CHECKPOINT_REQUIRED")
        expected = _hash(expected_checkpoint_hash)
        current = self.get_current(
            institution_id=checkpoint.institution_id,
            log_id=checkpoint.log_id,
            session=active,
        )
        if current is None or current.checkpoint_hash != expected:
            raise EngineeringMerkleCheckpointConflict(
                "CHECKPOINT_STALE_HEAD"
            )
        if (
            checkpoint.previous_checkpoint_hash != expected
            or checkpoint.leaf_count <= current.leaf_count
            or checkpoint.leaf_commitments[:current.leaf_count]
            != current.leaf_commitments
        ):
            raise EngineeringMerkleCheckpointConflict(
                "CHECKPOINT_NOT_A_VALID_EXTENSION"
            )

        pointer_filter = {
            "institution_id": checkpoint.institution_id,
            "log_id": checkpoint.log_id,
            "checkpoint_hash": expected,
            "leaf_count": current.leaf_count,
        }
        try:
            self._history.insert_one(checkpoint.to_dict(), session=active)
            outcome = self._current.update_one(
                pointer_filter,
                {"$set": {
                    "checkpoint_hash": checkpoint.checkpoint_hash,
                    "leaf_count": checkpoint.leaf_count,
                }},
                session=active,
            )
        except DuplicateKeyError as exc:
            raise EngineeringMerkleCheckpointConflict(
                "CHECKPOINT_CONCURRENT_COLLISION_ABORT_TRANSACTION"
            ) from exc
        except PyMongoError as exc:
            raise EngineeringMerkleCheckpointPersistenceUnavailable(
                "CHECKPOINT_ADVANCE_FAILED_ABORT_TRANSACTION"
            ) from exc
        if outcome.matched_count != 1:
            raise EngineeringMerkleCheckpointConflict(
                "CHECKPOINT_CAS_LOST_ABORT_TRANSACTION"
            )
        return checkpoint


# ARTIFACT: ENGINEERING MERKLE CHECKPOINT REGISTRY
# VERSION: 1.0.0-EMP-P21
# AUTHORITY BOUNDARY: TRANSACTIONAL PERSISTENCE, NO ISSUANCE
# TENANT POSTURE: INSTITUTION AND LOG ISOLATION
# FAIL-CLOSED POSTURE: CHECKPOINT LINEAGE AND CURRENT POINTER VERIFIED
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
