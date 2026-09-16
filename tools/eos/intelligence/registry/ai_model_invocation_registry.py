"""WILSY OS durable model-invocation evidence registry.

TITLE: WILSY AI Model Invocation Evidence Registry
VERSION: v1.0.0-WILSY-AI-MODEL-INVOCATION-REGISTRY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persists immutable provider-neutral model-compute evidence exactly
         once per tenant and invocation identity, with strict replay and
         transport-boundary hydration.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/registry/ai_model_invocation_registry.py
COLLABORATION / OWNERSHIP: The future reasoning orchestrator supplies already
                            authorized evidence; this registry adapts Mongo
                            persistence only; callers own sessions and
                            transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0 establishes the dedicated tenant-scoped collection,
           deterministic identity index, exact replay, divergent replay
           rejection, strict corruption handling, and caller-session passthrough.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Only bounded evidence fields are persisted; Mongo
                             transport metadata is removed at this boundary.
TENANT BOUNDARY: Every read and write predicates on the supplied tenant_id.
AUTHORITY BOUNDARY: Persistence adaptation only; no authentication,
                    authorization, entitlement, provider selection, legal,
                    usage, billing, payment, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
TRANSACTION BOUNDARY: The caller supplies the session and transaction. This
                      registry never starts, commits, aborts, retries, or stores
                      a Mongo client.
FAIL-CLOSED DECLARATION: Unknown fields, corrupt fingerprints, divergent
                         replay, duplicate races, and Mongo failures surface
                         as stable registry errors rather than absence.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.intelligence.domain.ai_model_execution import (
    ModelExecutionError,
    ModelInvocationEvidence,
)


VERSION: Final[str] = "v1.0.0-WILSY-AI-MODEL-INVOCATION-REGISTRY"
SCHEMA: Final[str] = "WILSY-AI-MODEL-INVOCATION-REGISTRY/V1"
COLLECTION: Final[str] = "wilsy_ai_model_invocations"
IDENTITY_INDEX_NAME: Final[str] = "wilsy_ai_model_invocation_tenant_identity_unique"
WRITE_CONCERN = WriteConcern(w="majority", j=True)
READ_CONCERN = ReadConcern("majority")


class AIModelInvocationRegistryError(RuntimeError):
    """Base fail-closed persistence or hydration error."""

    default_code = "C1A_REGISTRY_ERROR"

    def __init__(self, code: str | None = None) -> None:
        """Create a deterministic error carrying only its stable code."""
        self.code = code or self.default_code
        super().__init__(self.code)


class AIModelInvocationRegistryConflictError(AIModelInvocationRegistryError):
    """The tenant-scoped invocation identity already has divergent evidence."""

    default_code = "C1A_DIVERGENT_REPLAY"


class AIModelInvocationRegistryNotFoundError(AIModelInvocationRegistryError):
    """The exact tenant-scoped invocation evidence is absent."""

    default_code = "C1A_INVOCATION_NOT_FOUND"


class AIModelInvocationRegistryPersistenceError(AIModelInvocationRegistryError):
    """Mongo transport is unavailable or rejected the persistence operation."""

    default_code = "C1A_PERSISTENCE_UNAVAILABLE"


def _target(collection: Any) -> Any:
    """Apply majority concerns when the injected collection supports options."""
    try:
        return collection.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN)
    except AttributeError:
        return collection


def ensure_indexes(collection: Any) -> None:
    """Create only the evidenced tenant/invocation uniqueness index."""
    target = _target(collection)
    target.create_index(
        [("tenant_id", ASCENDING), ("invocation_id", ASCENDING)],
        unique=True,
        name=IDENTITY_INDEX_NAME,
    )


def _strip_transport_id(document: Mapping[str, object]) -> dict[str, object]:
    """Remove Mongo's sole transport field before strict domain hydration."""
    if not isinstance(document, Mapping):
        raise AIModelInvocationRegistryError("C1A_CORRUPT_EVIDENCE")
    return {key: value for key, value in document.items() if key != "_id"}


def _hydrate(document: Mapping[str, object]) -> ModelInvocationEvidence:
    """Hydrate strict evidence and translate domain corruption to registry error."""
    try:
        return ModelInvocationEvidence.from_dict(_strip_transport_id(document))
    except (AIModelInvocationRegistryError, ModelExecutionError, KeyError, TypeError) as error:
        raise AIModelInvocationRegistryError("C1A_CORRUPT_EVIDENCE") from error


class AIModelInvocationRegistry:
    """Append-only tenant-scoped model-evidence persistence adapter."""

    __slots__ = ("_collection",)

    def __init__(self, collection: Any) -> None:
        """Bind one injected Mongo collection without creating a client/session."""
        if collection is None:
            raise AIModelInvocationRegistryError("C1A_COLLECTION_REQUIRED")
        self._collection = _target(collection)

    def create_or_replay(self, evidence: ModelInvocationEvidence, *, session: Any) -> ModelInvocationEvidence:
        """Insert once or return exact replay while preserving caller session."""
        if not isinstance(evidence, ModelInvocationEvidence) or session is None:
            raise AIModelInvocationRegistryError("C1A_INPUT_INVALID")
        query = {"tenant_id": evidence.tenant_id, "invocation_id": evidence.invocation_id}
        try:
            existing = self._collection.find_one(query, session=session)
        except PyMongoError as error:
            raise AIModelInvocationRegistryPersistenceError() from error
        if existing is not None:
            persisted = _hydrate(existing)
            if persisted.to_dict() != evidence.to_dict():
                raise AIModelInvocationRegistryConflictError()
            return persisted
        try:
            self._collection.insert_one(evidence.to_dict(), session=session)
        except DuplicateKeyError as error:
            raise AIModelInvocationRegistryConflictError("C1A_DUPLICATE_RACE") from error
        except PyMongoError as error:
            raise AIModelInvocationRegistryPersistenceError() from error
        return evidence

    def get(self, *, tenant_id: str, invocation_id: str, session: Any) -> ModelInvocationEvidence:
        """Return one exact tenant-scoped evidence record with strict hydration."""
        if not isinstance(tenant_id, str) or not tenant_id.strip() or not isinstance(invocation_id, str) or not invocation_id.strip() or session is None:
            raise AIModelInvocationRegistryError("C1A_INPUT_INVALID")
        try:
            row = self._collection.find_one(
                {"tenant_id": tenant_id, "invocation_id": invocation_id},
                session=session,
            )
        except PyMongoError as error:
            raise AIModelInvocationRegistryPersistenceError() from error
        if row is None:
            raise AIModelInvocationRegistryNotFoundError()
        return _hydrate(row)


__all__ = [
    "VERSION",
    "SCHEMA",
    "COLLECTION",
    "IDENTITY_INDEX_NAME",
    "WRITE_CONCERN",
    "READ_CONCERN",
    "AIModelInvocationRegistry",
    "AIModelInvocationRegistryError",
    "AIModelInvocationRegistryConflictError",
    "AIModelInvocationRegistryNotFoundError",
    "AIModelInvocationRegistryPersistenceError",
    "ensure_indexes",
]

# ARTIFACT: ai_model_invocation_registry.py
# VERSION: v1.0.0-WILSY-AI-MODEL-INVOCATION-REGISTRY
# AUTHORITY BOUNDARY: append-only model-invocation evidence persistence
# TENANT POSTURE: exact tenant predicate on every operation
# FAIL-CLOSED POSTURE: strict hydration and divergent replay rejection
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
