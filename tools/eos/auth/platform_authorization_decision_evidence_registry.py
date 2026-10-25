"""Durable platform authorization decision evidence registry.

VERSION: v1.0.0-PLATFORM-AUTHORIZATION-DECISION-EVIDENCE-REGISTRY
AUTHORITY: Sovereign IAM audit persistence only; not a decision evaluator.
TENANT BOUNDARY: Every record is PLATFORM scoped; target tenant is descriptive.
TRANSACTION BOUNDARY: Registry owns a separate audit-client session and transaction.
CALLER TRANSACTION: Never accepted, joined, committed, or aborted by this registry.
FAILURE POSTURE: Audit persistence failure raises; caller must fail closed.
"""
from __future__ import annotations

from typing import Any

from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.platform_authorization_decision_evidence import (
    PlatformAuthorizationDecisionEvidence,
    PlatformAuthorizationDecisionEvidenceError,
)

VERSION = "v1.0.0-PLATFORM-AUTHORIZATION-DECISION-EVIDENCE-REGISTRY"
COLLECTION = "platform_authorization_decision_evidence"


class PlatformAuthorizationDecisionEvidenceRegistryError(RuntimeError):
    """Base fail-closed durable audit error."""


class PlatformAuthorizationDecisionEvidenceRegistryConflictError(
    PlatformAuthorizationDecisionEvidenceRegistryError
):
    """An idempotency key or decision identity conflicts with durable evidence."""


class PlatformAuthorizationDecisionEvidenceRegistryPersistenceError(
    PlatformAuthorizationDecisionEvidenceRegistryError
):
    """The independent audit transaction could not be durably completed."""


class PlatformAuthorizationDecisionEvidenceRegistry:
    """Append-only durable decision evidence writer with independent transaction.

    The audit client must be a server-owned MongoClient. The caller's active
    business session is not accepted by this API, so audit evidence cannot be
    accidentally enlisted in or rolled back with the reconciliation transaction.
    The writer owns only the audit session/transaction it creates.
    """

    def __init__(self, collection: Collection, *, audit_client: Any) -> None:
        if not callable(getattr(collection, "find_one", None)) or not callable(
            getattr(collection, "insert_one", None)
        ):
            raise PlatformAuthorizationDecisionEvidenceRegistryPersistenceError(
                "AUDIT_COLLECTION_REQUIRED"
            )
        if not callable(getattr(audit_client, "start_session", None)):
            raise PlatformAuthorizationDecisionEvidenceRegistryPersistenceError(
                "SERVER_OWNED_AUDIT_CLIENT_REQUIRED"
            )
        self._collection = collection
        self._audit_client = audit_client

    def ensure_indexes(self) -> None:
        """Create required uniqueness indexes during governed deployment setup."""
        try:
            self._collection.create_index(
                [("idempotency_key", ASCENDING)],
                unique=True,
                name="platform_auth_decision_idempotency_unique",
            )
            self._collection.create_index(
                [("decision_id", ASCENDING)],
                unique=True,
                name="platform_auth_decision_identity_unique",
            )
        except PyMongoError as error:
            raise PlatformAuthorizationDecisionEvidenceRegistryPersistenceError(
                "AUDIT_INDEX_SETUP_FAILED"
            ) from error

    @staticmethod
    def _replay_material(row: dict[str, Any]) -> dict[str, Any]:
        """Compare request disposition/provenance, not generated ID or clock."""
        return {
            key: value
            for key, value in row.items()
            if key not in {"_id", "decision_id", "evaluated_at", "evidence_fingerprint"}
        }

    @staticmethod
    def _hydrate(row: dict[str, Any]) -> PlatformAuthorizationDecisionEvidence:
        body = dict(row)
        body.pop("_id", None)
        return PlatformAuthorizationDecisionEvidence.from_persisted(body)

    def record(
        self, evidence: PlatformAuthorizationDecisionEvidence
    ) -> PlatformAuthorizationDecisionEvidence:
        """Append one decision or return its identical idempotent replay.

        A denial is written just like an allow. The caller must not proceed with
        provider access unless an ALLOW record has been durably returned. The
        record describes a decision only, never execution or commit completion.
        """
        if not isinstance(evidence, PlatformAuthorizationDecisionEvidence):
            raise PlatformAuthorizationDecisionEvidenceRegistryPersistenceError(
                "PLATFORM_DECISION_EVIDENCE_REQUIRED"
            )
        document = evidence.to_persisted()
        try:
            with self._audit_client.start_session() as audit_session:
                with audit_session.start_transaction():
                    existing = self._collection.find_one(
                        {"idempotency_key": evidence.idempotency_key},
                        session=audit_session,
                    )
                    if existing is not None:
                        historic = self._hydrate(dict(existing))
                        if self._replay_material(historic.to_persisted()) != self._replay_material(document):
                            raise PlatformAuthorizationDecisionEvidenceRegistryConflictError(
                                "AUDIT_IDEMPOTENCY_CONFLICT"
                            )
                        return historic
                    self._collection.insert_one(document, session=audit_session)
            return evidence
        except PlatformAuthorizationDecisionEvidenceRegistryConflictError:
            raise
        except DuplicateKeyError as error:
            # The competing writer may have committed after our initial read.
            try:
                existing = self._collection.find_one(
                    {"idempotency_key": evidence.idempotency_key}
                )
                if existing is None:
                    existing = self._collection.find_one(
                        {"decision_id": evidence.decision_id}
                    )
                if existing is not None:
                    historic = self._hydrate(dict(existing))
                    if self._replay_material(historic.to_persisted()) == self._replay_material(document):
                        return historic
                    raise PlatformAuthorizationDecisionEvidenceRegistryConflictError(
                        "AUDIT_IDEMPOTENCY_CONFLICT"
                    ) from error
            except PlatformAuthorizationDecisionEvidenceRegistryConflictError:
                raise
            except (PyMongoError, PlatformAuthorizationDecisionEvidenceError, TypeError, ValueError) as read_error:
                raise PlatformAuthorizationDecisionEvidenceRegistryPersistenceError(
                    "AUDIT_REPLAY_RESOLUTION_FAILED"
                ) from read_error
            raise PlatformAuthorizationDecisionEvidenceRegistryConflictError(
                "AUDIT_DECISION_ID_CONFLICT"
            ) from error
        except (
            PyMongoError,
            PlatformAuthorizationDecisionEvidenceError,
            TypeError,
            ValueError,
        ) as error:
            raise PlatformAuthorizationDecisionEvidenceRegistryPersistenceError(
                "AUDIT_DURABILITY_UNAVAILABLE"
            ) from error
        except Exception as error:
            # Driver/session/transaction adapters may raise non-PyMongo exceptions.
            # Never leak database internals or return an unrecorded decision.
            raise PlatformAuthorizationDecisionEvidenceRegistryPersistenceError(
                "AUDIT_DURABILITY_UNAVAILABLE"
            ) from error

    def get_by_idempotency_key(
        self, idempotency_key: str
    ) -> PlatformAuthorizationDecisionEvidence:
        """Read and strictly verify one durable platform decision."""
        if not isinstance(idempotency_key, str) or not idempotency_key.strip():
            raise PlatformAuthorizationDecisionEvidenceRegistryPersistenceError(
                "AUDIT_IDEMPOTENCY_KEY_INVALID"
            )
        try:
            row = self._collection.find_one({"idempotency_key": idempotency_key})
            if row is None:
                raise PlatformAuthorizationDecisionEvidenceRegistryPersistenceError(
                    "AUDIT_EVIDENCE_NOT_FOUND"
                )
            return self._hydrate(dict(row))
        except PlatformAuthorizationDecisionEvidenceRegistryPersistenceError:
            raise
        except (
            PyMongoError,
            PlatformAuthorizationDecisionEvidenceError,
            TypeError,
            ValueError,
        ) as error:
            raise PlatformAuthorizationDecisionEvidenceRegistryPersistenceError(
                "AUDIT_PERSISTED_RECORD_INVALID"
            ) from error


__all__ = [
    "VERSION",
    "COLLECTION",
    "PlatformAuthorizationDecisionEvidenceRegistry",
    "PlatformAuthorizationDecisionEvidenceRegistryError",
    "PlatformAuthorizationDecisionEvidenceRegistryConflictError",
    "PlatformAuthorizationDecisionEvidenceRegistryPersistenceError",
]
