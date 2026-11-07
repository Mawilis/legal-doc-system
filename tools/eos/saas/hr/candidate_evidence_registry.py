"""Caller-transaction metadata registry for candidate evidence objects.

Binary bytes remain in the provider object plane. This registry persists only
strict immutable metadata and append-only custody events.
"""
from __future__ import annotations

from typing import Any
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.domain.candidate_evidence import (
    CandidateEvidenceError,
    CandidateEvidenceObjectMetadata,
)

COLLECTION = "wilsy_hr_candidate_evidence_metadata"
EVENT_COLLECTION = "wilsy_hr_candidate_evidence_events"


class CandidateEvidenceRegistryError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class CandidateEvidenceRegistryConflict(CandidateEvidenceRegistryError):
    pass


class CandidateEvidenceRegistryNotFound(CandidateEvidenceRegistryError):
    pass


def _tx(session: object) -> object:
    if session is None:
        raise CandidateEvidenceRegistryError("CANDIDATE_EVIDENCE_TRANSACTION_REQUIRED")
    return session


def _scope(value: object, code: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise CandidateEvidenceRegistryError(code)
    return value


class CandidateEvidenceRegistry:
    __slots__ = ("_metadata", "_events")

    def __init__(self, metadata: Any, events: Any) -> None:
        if metadata is None or events is None:
            raise CandidateEvidenceRegistryError("CANDIDATE_EVIDENCE_COLLECTION_REQUIRED")
        self._metadata, self._events = metadata, events

    @staticmethod
    def ensure_indexes(metadata: Any, events: Any) -> None:
        try:
            metadata.create_index(
                [("tenant_id", ASCENDING), ("candidate_id", ASCENDING), ("evidence_id", ASCENDING), ("evidence_version_id", ASCENDING)],
                unique=True, name="uq_candidate_evidence_tenant_candidate_identity_version",
            )
            metadata.create_index(
                [("tenant_id", ASCENDING), ("candidate_id", ASCENDING), ("evidence_kind", ASCENDING), ("created_at", ASCENDING)],
                name="ix_candidate_evidence_candidate_kind_created",
            )
            events.create_index(
                [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
                unique=True, name="uq_candidate_evidence_event_idempotency",
            )
            events.create_index(
                [("tenant_id", ASCENDING), ("candidate_id", ASCENDING), ("evidence_id", ASCENDING), ("evidence_version_id", ASCENDING)],
                unique=True, name="uq_candidate_evidence_event_identity",
            )
        except PyMongoError as error:
            raise CandidateEvidenceRegistryError("CANDIDATE_EVIDENCE_INDEX_UNAVAILABLE") from error

    def register(
        self, value: CandidateEvidenceObjectMetadata, *, actor_principal_id: str,
        idempotency_key: str, session: object,
    ) -> CandidateEvidenceObjectMetadata:
        tx = _tx(session)
        if type(value) is not CandidateEvidenceObjectMetadata:
            raise CandidateEvidenceRegistryError("CANDIDATE_EVIDENCE_METADATA_REQUIRED")
        actor = _scope(actor_principal_id, "CANDIDATE_EVIDENCE_ACTOR_INVALID")
        key = _scope(idempotency_key, "CANDIDATE_EVIDENCE_IDEMPOTENCY_KEY_INVALID")
        try:
            prior = self._events.find_one({"tenant_id": value.tenant_id, "idempotency_key": key}, session=tx)
            if prior is not None:
                if prior.get("fingerprint") != value.fingerprint or prior.get("evidence_id") != value.evidence_id:
                    raise CandidateEvidenceRegistryConflict("CANDIDATE_EVIDENCE_DIVERGENT_REPLAY")
                return CandidateEvidenceObjectMetadata.from_dict(prior["snapshot"])
            self._metadata.insert_one(value.to_dict(), session=tx)
            self._events.insert_one({
                "tenant_id": value.tenant_id,
                "candidate_id": value.candidate_id,
                "evidence_id": value.evidence_id,
                "evidence_version_id": value.evidence_version_id,
                "idempotency_key": key,
                "actor_principal_id": actor,
                "action": "CANDIDATE_EVIDENCE_OBJECT_REGISTERED",
                "fingerprint": value.fingerprint,
                "snapshot": value.to_dict(),
                "schema": "wilsy.hr.candidate_evidence_event.v1",
            }, session=tx)
            return value
        except CandidateEvidenceRegistryConflict:
            raise
        except DuplicateKeyError as error:
            raise CandidateEvidenceRegistryConflict("CANDIDATE_EVIDENCE_ALREADY_REGISTERED") from error
        except PyMongoError as error:
            raise CandidateEvidenceRegistryError("CANDIDATE_EVIDENCE_WRITE_UNAVAILABLE") from error

    def get(
        self, *, tenant_id: str, candidate_id: str, evidence_id: str,
        evidence_version_id: str, session: object,
    ) -> CandidateEvidenceObjectMetadata:
        tx = _tx(session)
        scope = {
            "tenant_id": _scope(tenant_id, "CANDIDATE_EVIDENCE_TENANT_INVALID"),
            "candidate_id": _scope(candidate_id, "CANDIDATE_EVIDENCE_CANDIDATE_INVALID"),
            "evidence_id": _scope(evidence_id, "CANDIDATE_EVIDENCE_ID_INVALID"),
            "evidence_version_id": _scope(evidence_version_id, "CANDIDATE_EVIDENCE_VERSION_INVALID"),
        }
        try:
            row = self._metadata.find_one(scope, session=tx)
        except PyMongoError as error:
            raise CandidateEvidenceRegistryError("CANDIDATE_EVIDENCE_READ_UNAVAILABLE") from error
        if row is None:
            raise CandidateEvidenceRegistryNotFound("CANDIDATE_EVIDENCE_NOT_FOUND")
        row.pop("_id", None)
        try:
            return CandidateEvidenceObjectMetadata.from_dict(row)
        except CandidateEvidenceError as error:
            raise CandidateEvidenceRegistryError("CANDIDATE_EVIDENCE_RECORD_CORRUPT") from error

    def list_candidate(
        self, *, tenant_id: str, candidate_id: str, session: object, limit: int = 100,
    ) -> tuple[CandidateEvidenceObjectMetadata, ...]:
        tx = _tx(session)
        if type(limit) is not int or not 1 <= limit <= 250:
            raise CandidateEvidenceRegistryError("CANDIDATE_EVIDENCE_LIMIT_INVALID")
        scope = {
            "tenant_id": _scope(tenant_id, "CANDIDATE_EVIDENCE_TENANT_INVALID"),
            "candidate_id": _scope(candidate_id, "CANDIDATE_EVIDENCE_CANDIDATE_INVALID"),
        }
        try:
            rows = list(self._metadata.find(scope, session=tx).sort("created_at", ASCENDING).limit(limit))
        except PyMongoError as error:
            raise CandidateEvidenceRegistryError("CANDIDATE_EVIDENCE_READ_UNAVAILABLE") from error
        result = []
        for row in rows:
            row.pop("_id", None)
            try:
                result.append(CandidateEvidenceObjectMetadata.from_dict(row))
            except CandidateEvidenceError as error:
                raise CandidateEvidenceRegistryError("CANDIDATE_EVIDENCE_RECORD_CORRUPT") from error
        return tuple(result)


__all__ = [
    "COLLECTION", "EVENT_COLLECTION", "CandidateEvidenceRegistry",
    "CandidateEvidenceRegistryError", "CandidateEvidenceRegistryConflict",
    "CandidateEvidenceRegistryNotFound",
]
