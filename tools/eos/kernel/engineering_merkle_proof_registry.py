"""
WILSY OS — ENGINEERING MERKLE PROOF REGISTRY
VERSION: 1.0.0-EMP-P10
AUTHORITY: Engineering Kernel immutable evidence persistence.
EPITOME: Transaction-required, institution-scoped proof-record storage.
ABSOLUTE CANONICAL PATH: tools/eos/kernel/engineering_merkle_proof_registry.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
CHANGELOG: 1.0.0-EMP-P10 — Initial insert-only registry.
COMPLIANCE: EK-001, EK-002, EK-003, EK-005, EK-006, EK-007.
SECURITY: Fail closed on inactive transactions, conflicts and corruption.
TENANT BOUNDARY: Explicit institutional scope on every identity lookup.
AUTHORITY BOUNDARY: Persistence only; no authentication or approval.
FINANCIAL AUTHORITY BOUNDARY: None.

The caller owns transactions and all admission authorization.
The registry neither starts sessions nor commits transactions.
A persisted proof is not an authenticated institutional checkpoint.
"""

from __future__ import annotations

from typing import Any, Protocol

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.kernel.engineering_merkle_proof_record import (
    EngineeringMerkleProofRecord,
)

SCHEMA = "WILSY-ENGINEERING-MERKLE-PROOF-RECORD/V1"
IDENTITY_INDEX = "engineering_merkle_institution_release_evidence_unique"
RELEASE_INDEX = "engineering_merkle_institution_release_read"


class EngineeringMerkleProofRegistryError(Exception):
    """Base exception for failed evidence persistence contracts."""


class EngineeringMerkleProofTransactionRequired(
    EngineeringMerkleProofRegistryError
):
    """Raised before writes without an active caller-owned transaction."""


class EngineeringMerkleProofConflict(
    EngineeringMerkleProofRegistryError
):
    """Raised on divergent replay or immutable identity collision."""


class EngineeringMerkleProofPersistedInvalid(
    EngineeringMerkleProofRegistryError
):
    """Raised when persisted evidence violates cryptographic integrity."""


class EngineeringMerkleProofPersistenceUnavailable(
    EngineeringMerkleProofRegistryError
):
    """Raised when storage operations cannot be completed reliably."""


class Collection(Protocol):
    """Minimal injected Mongo-compatible persistence interface."""

    def create_index(
        self, keys: Any, **kwargs: Any
    ) -> Any:
        """Create a specified deterministic persistence index."""
        ...

    def find_one(
        self, filter: Any, **kwargs: Any
    ) -> Any:
        """Read a proof by explicit identity."""
        ...

    def insert_one(
        self, document: Any, **kwargs: Any
    ) -> Any:
        """Insert a new immutable proof record."""
        ...


def _transaction(session: object) -> object:
    """Require an active caller-owned Mongo transaction."""
    if (
        session is None
        or getattr(session, "in_transaction", False) is not True
    ):
        raise EngineeringMerkleProofTransactionRequired(
            "ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


def _identity(
    *, institution_id: str, release_id: str, evidence_id: str
) -> dict[str, str]:
    """Validate exact institutional identifiers before querying storage."""
    import re

    identifier = re.compile(
        r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", re.ASCII
    )
    result = {
        "institution_id": institution_id,
        "release_id": release_id,
        "evidence_id": evidence_id,
    }

    for key, value in result.items():
        if type(value) is not str or identifier.fullmatch(value) is None:
            raise ValueError("INVALID_" + key.upper())

    return result


def _hydrate(document: object) -> EngineeringMerkleProofRecord:
    """Validate exact persisted schema and recompute provenance."""
    if type(document) is not dict:
        raise EngineeringMerkleProofPersistedInvalid(
            "INVALID_PERSISTED_DOCUMENT"
        )

    row = dict(document)

    # Mongo's document key is transport metadata, not semantic evidence.
    row.pop("_id", None)

    try:
        return EngineeringMerkleProofRecord.from_dict(row)
    except (TypeError, ValueError) as error:
        raise EngineeringMerkleProofPersistedInvalid(
            "PERSISTED_RECORD_INTEGRITY_FAILURE"
        ) from error


class EngineeringMerkleProofRegistry:
    """Insert-only, transaction-bound registry for immutable proof claims.

    This storage adapter does not authenticate an operator, authorize a
    release, verify signatures, or create institutional checkpoints.
    """

    def __init__(self, collection: Collection) -> None:
        """Inject an independently provisioned Mongo-compatible collection."""
        if collection is None:
            raise TypeError("COLLECTION_REQUIRED")
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create unique proof identity and scoped release-read indexes.

        Index installation belongs to controlled infrastructure startup.
        No expiration or TTL index is authorized for engineering proofs.
        """
        try:
            self._collection.create_index(
                [
                    ("institution_id", ASCENDING),
                    ("release_id", ASCENDING),
                    ("evidence_id", ASCENDING),
                ],
                name=IDENTITY_INDEX,
                unique=True,
            )
            self._collection.create_index(
                [
                    ("institution_id", ASCENDING),
                    ("release_id", ASCENDING),
                ],
                name=RELEASE_INDEX,
            )
        except PyMongoError as error:
            raise EngineeringMerkleProofPersistenceUnavailable(
                "INDEX_INSTALLATION_FAILED"
            ) from error

    def get_by_identity(
        self,
        *,
        institution_id: str,
        release_id: str,
        evidence_id: str,
        session: object = None,
    ) -> EngineeringMerkleProofRecord | None:
        """Read and validate one exact scoped proof, without implicit access.

        Access authorization must occur in the caller's institutional
        service before this method is invoked.
        """
        query = _identity(
            institution_id=institution_id,
            release_id=release_id,
            evidence_id=evidence_id,
        )

        try:
            document = self._collection.find_one(
                query, session=session
            )
        except PyMongoError as error:
            raise EngineeringMerkleProofPersistenceUnavailable(
                "PROOF_READ_FAILED"
            ) from error

        if document is None:
            return None

        value = _hydrate(document)

        if (
            value.institution_id != institution_id
            or value.release_id != release_id
            or value.evidence_id != evidence_id
        ):
            raise EngineeringMerkleProofPersistedInvalid(
                "PERSISTED_IDENTITY_MISMATCH"
            )

        return value

    def create_or_replay(
        self,
        record: EngineeringMerkleProofRecord,
        *,
        session: object,
    ) -> EngineeringMerkleProofRecord:
        """Insert new evidence or return an exact immutable replay.

        Caller owns transaction lifecycle. Concurrent identity races must
        be resolved by the database unique index, not by a prior read.
        Divergent replay is never accepted.
        """
        tx = _transaction(session)

        if type(record) is not EngineeringMerkleProofRecord:
            raise TypeError("EXACT_PROOF_RECORD_REQUIRED")

        # Re-hydrate before persistence to detect forged object fields.
        validated = EngineeringMerkleProofRecord.from_dict(
            record.to_dict()
        )

        existing = self.get_by_identity(
            institution_id=validated.institution_id,
            release_id=validated.release_id,
            evidence_id=validated.evidence_id,
            session=tx,
        )

        if existing is not None:
            if existing == validated:
                return existing
            raise EngineeringMerkleProofConflict(
                "DIVERGENT_EVIDENCE_REPLAY"
            )

        try:
            self._collection.insert_one(
                validated.to_dict(),
                session=tx,
            )
        except DuplicateKeyError as error:
            # A concurrent transaction may win. No write-side inference
            # or retry within an already-failed transaction is allowed.
            raise EngineeringMerkleProofConflict(
                "CONCURRENT_PROOF_IDENTITY_CONFLICT"
            ) from error
        except PyMongoError as error:
            raise EngineeringMerkleProofPersistenceUnavailable(
                "PROOF_INSERT_FAILED"
            ) from error

        return validated


# ARTIFACT: ENGINEERING MERKLE PROOF REGISTRY
# VERSION: 1.0.0-EMP-P10
# AUTHORITY BOUNDARY: TRANSACTIONAL PERSISTENCE, NOT ADMISSION
# TENANT POSTURE: EXPLICIT INSTITUTIONAL SCOPE REQUIRED
# FAIL-CLOSED POSTURE: INACTIVE TRANSACTION, CONFLICT, CORRUPTION REJECT
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
