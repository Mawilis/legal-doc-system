"""WILSY OS durable authorization-role revocation evidence registry.

TITLE: Authorization Role Revocation Evidence Registry
VERSION: v1.1.0-P1-R3C-E1-AUTHORIZATION-ROLE-REVOCATION-EVIDENCE-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Sovereign IAM Design
EPITOME: Persist and strictly replay immutable authorization-role revocation evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/authorization_role_revocation_evidence_registry.py
COLLABORATION / OWNERSHIP: P1-R3B-E1 owns evidence semantics; G1 owns only
                            append-only storage, strict hydration, scoped replay,
                            deterministic indexes, and bounded persistence errors.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: v1.1.0-P1-R3C-E1 adds an optional-session, exact tenant/idempotency
           historical read with strict hydration and explicit None absence;
           v1.0.0-P1-R3B-G1 established exact-tenant reads, caller-owned active
           transaction enforcement, immutable create-or-replay, duplicate-key
           classification, and three sanctioned indexes without TTL.
COMPLIANCE: NIST privileged-access lifecycle principles; POPIA section 19;
            GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Strict E1 hydration, exact tenant predicates,
                             bounded errors, and no corruption repair.
TENANT BOUNDARY: Every operational lookup binds an exact non-pseudo tenant;
                 no default, global-root, or cross-tenant inference exists.
AUTHORITY BOUNDARY: Durable authorization-role-revocation evidence persistence
                    only. The registry does not grant or prove current authority,
                    evaluate revocation policy, mutate role assignments, own
                    command atomicity, root rotation, break glass, privileged
                    activation, or execute financial operations.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial
                              execution and settlement.
TRANSACTION BOUNDARY: The caller owns every session and transaction lifecycle;
                      this registry never starts, commits, aborts, or retries one.
FAIL-CLOSED DECLARATION: Invalid scope/type, absent transaction, missing or
                         corrupt evidence, replay divergence, identity collision,
                         duplicate race, and persistence outage reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.authorization_role_revocation_evidence import (
    AuthorizationRoleRevocationEvidence,
    AuthorizationRoleRevocationEvidenceError,
)


VERSION: Final[str] = "v1.1.0-P1-R3C-E1-AUTHORIZATION-ROLE-REVOCATION-EVIDENCE-REGISTRY"
COLLECTION: Final[str] = "authorization_role_revocation_evidence"
REVOCATION_ID_INDEX: Final[str] = "authorization_role_revocation_identity_unique"
TENANT_IDEMPOTENCY_INDEX: Final[str] = "authorization_role_revocation_tenant_idempotency_unique"
TARGET_ROLE_TIMELINE_INDEX: Final[str] = "authorization_role_revocation_target_role_timeline"


class AuthorizationRoleRevocationEvidenceRegistryError(RuntimeError):
    """Base bounded registry failure containing one stable non-secret code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class AuthorizationRoleRevocationEvidenceTransactionRequiredError(
    AuthorizationRoleRevocationEvidenceRegistryError
):
    """Caller omitted an already-active transaction."""


class AuthorizationRoleRevocationEvidenceNotFoundError(
    AuthorizationRoleRevocationEvidenceRegistryError
):
    """No exact tenant-scoped revocation evidence exists."""


class AuthorizationRoleRevocationEvidenceConflictError(
    AuthorizationRoleRevocationEvidenceRegistryError
):
    """Idempotency, durable identity, or concurrent insertion conflicts."""


class AuthorizationRoleRevocationEvidencePersistedRecordInvalidError(
    AuthorizationRoleRevocationEvidenceRegistryError
):
    """Persisted evidence failed strict E1 hydration or scope correlation."""


class AuthorizationRoleRevocationEvidencePersistenceError(
    AuthorizationRoleRevocationEvidenceRegistryError
):
    """Persistence failed without a safe success classification."""


def _raise(
    error_type: type[AuthorizationRoleRevocationEvidenceRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one stable registry error while retaining its private cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _identifier(name: str, value: object) -> str:
    """Require one exact bounded identifier without normalization."""
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 256:
        _raise(AuthorizationRoleRevocationEvidencePersistenceError, f"{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    """Require one explicit non-pseudo tenant boundary."""
    tenant_id = _identifier("tenant_id", value)
    if tenant_id.casefold() in {"default", "global", "global_root", "root", "master", "*"}:
        _raise(AuthorizationRoleRevocationEvidencePersistenceError, "TENANT_ID_INVALID")
    return tenant_id


def _active_transaction(session: Any) -> Any:
    """Require the exact caller-owned active transaction before any read."""
    if session is None:
        _raise(AuthorizationRoleRevocationEvidenceTransactionRequiredError, "ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError) as error:
        _raise(AuthorizationRoleRevocationEvidenceTransactionRequiredError, "ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _raise(AuthorizationRoleRevocationEvidenceTransactionRequiredError, "ACTIVE_TRANSACTION_REQUIRED")
    return session


def _hydrate(raw: object) -> AuthorizationRoleRevocationEvidence:
    """Strictly hydrate one persisted row without repairing stored evidence."""
    if not isinstance(raw, Mapping):
        _raise(AuthorizationRoleRevocationEvidencePersistedRecordInvalidError, "PERSISTED_RECORD_INVALID")
    body = dict(raw)
    body.pop("_id", None)
    try:
        return AuthorizationRoleRevocationEvidence.from_persisted(body)
    except (AuthorizationRoleRevocationEvidenceError, TypeError, ValueError, KeyError) as error:
        _raise(AuthorizationRoleRevocationEvidencePersistedRecordInvalidError, "PERSISTED_RECORD_INVALID", error)


def _exact(
    historic: AuthorizationRoleRevocationEvidence,
    requested: AuthorizationRoleRevocationEvidence,
) -> bool:
    """Compare the complete deterministic durable evidence shape."""
    return historic.to_persisted() == requested.to_persisted()


class AuthorizationRoleRevocationEvidenceRegistry:
    """Append-only exact-tenant revocation evidence persistence facade.

    The registry owns no authorization, policy decision, assignment mutation,
    session, transaction lifecycle, update/delete/purge path, current pointer,
    root lifecycle, privileged activation, break glass, or financial execution.
    """

    def __init__(self, collection: Any) -> None:
        """Bind one explicit collection without opening persistence lifecycle."""
        if collection is None:
            _raise(AuthorizationRoleRevocationEvidencePersistenceError, "COLLECTION_REQUIRED")
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create exactly the three sanctioned indexes; no fingerprint or TTL."""
        indexes = (
            ([('revocation_id', ASCENDING)], True, REVOCATION_ID_INDEX),
            ([('tenant_id', ASCENDING), ('idempotency_key', ASCENDING)], True, TENANT_IDEMPOTENCY_INDEX),
            ([('tenant_id', ASCENDING), ('target_principal_id', ASCENDING), ('target_role_id', ASCENDING), ('revoked_at', ASCENDING)], False, TARGET_ROLE_TIMELINE_INDEX),
        )
        try:
            for keys, unique, name in indexes:
                self._collection.create_index(keys, unique=unique, name=name)
        except AttributeError as error:
            _raise(AuthorizationRoleRevocationEvidencePersistenceError, "COLLECTION_INTERFACE_INVALID", error)
        except PyMongoError as error:
            _raise(AuthorizationRoleRevocationEvidencePersistenceError, "INDEX_CREATION_FAILED", error)

    def get(
        self,
        *,
        tenant_id: str,
        revocation_id: str,
        session: Any = None,
    ) -> AuthorizationRoleRevocationEvidence:
        """Read and strictly hydrate one exact tenant/revocation identity.

        The optional session is passed through unchanged. This method creates no
        session or transaction and grants no authority.
        """
        tenant = _tenant(tenant_id)
        identity = _identifier("revocation_id", revocation_id)
        try:
            raw = self._collection.find_one(
                {"tenant_id": tenant, "revocation_id": identity},
                session=session,
            )
        except AttributeError as error:
            _raise(AuthorizationRoleRevocationEvidencePersistenceError, "COLLECTION_INTERFACE_INVALID", error)
        except PyMongoError as error:
            _raise(AuthorizationRoleRevocationEvidencePersistenceError, "PERSISTENCE_UNAVAILABLE", error)
        if raw is None:
            _raise(AuthorizationRoleRevocationEvidenceNotFoundError, "REVOCATION_EVIDENCE_NOT_FOUND")
        value = _hydrate(raw)
        if value.tenant_id != tenant or value.revocation_id != identity:
            _raise(AuthorizationRoleRevocationEvidencePersistedRecordInvalidError, "PERSISTED_SCOPE_MISMATCH")
        return value

    def get_by_tenant_idempotency(
        self,
        *,
        tenant_id: str,
        idempotency_key: str,
        session: Any = None,
    ) -> AuthorizationRoleRevocationEvidence | None:
        """Return strictly hydrated historic evidence for one scoped replay key.

        Absence is the ordinary ``None`` result so a future caller can distinguish
        replay preflight absence from persistence or corruption failure. The
        supplied optional session is forwarded unchanged; this read creates no
        session, transaction, retry, authority, evidence, or mutation. A historic
        row is evidence only and does not prove current authorization. The future
        command remains responsible for exact-replay or divergence classification.
        """
        tenant = _tenant(tenant_id)
        replay_key = _identifier("idempotency_key", idempotency_key)
        try:
            raw = self._collection.find_one(
                {"tenant_id": tenant, "idempotency_key": replay_key},
                session=session,
            )
        except AttributeError as error:
            _raise(AuthorizationRoleRevocationEvidencePersistenceError, "COLLECTION_INTERFACE_INVALID", error)
        except PyMongoError as error:
            _raise(AuthorizationRoleRevocationEvidencePersistenceError, "PERSISTENCE_UNAVAILABLE", error)
        if raw is None:
            return None
        value = _hydrate(raw)
        if value.tenant_id != tenant or value.idempotency_key != replay_key:
            _raise(AuthorizationRoleRevocationEvidencePersistedRecordInvalidError, "PERSISTED_SCOPE_MISMATCH")
        return value

    def _classify_existing(
        self,
        requested: AuthorizationRoleRevocationEvidence,
        *,
        session: Any,
    ) -> AuthorizationRoleRevocationEvidence | None:
        """Classify scoped idempotency and global revocation-ID durable state."""
        by_key = self._collection.find_one(
            {"tenant_id": requested.tenant_id, "idempotency_key": requested.idempotency_key},
            session=session,
        )
        if by_key is not None:
            historic = _hydrate(by_key)
            if historic.tenant_id != requested.tenant_id:
                _raise(AuthorizationRoleRevocationEvidencePersistedRecordInvalidError, "PERSISTED_SCOPE_MISMATCH")
            if _exact(historic, requested):
                return historic
            _raise(AuthorizationRoleRevocationEvidenceConflictError, "IDEMPOTENCY_KEY_DIVERGENT_REPLAY")

        by_identity = self._collection.find_one(
            {"revocation_id": requested.revocation_id},
            session=session,
        )
        if by_identity is not None:
            historic = _hydrate(by_identity)
            if _exact(historic, requested):
                return historic
            _raise(AuthorizationRoleRevocationEvidenceConflictError, "REVOCATION_ID_COLLISION")
        return None

    def create_or_replay(
        self,
        evidence: AuthorizationRoleRevocationEvidence,
        *,
        session: Any,
    ) -> AuthorizationRoleRevocationEvidence:
        """Insert immutable evidence or return an exact historic replay.

        An active caller-owned transaction is required before the first read.
        Every operation uses that exact session. Duplicate-key races are
        reclassified only when the caller's transaction remains readable;
        otherwise the caller must abort and retry the whole future command in a
        fresh transaction. This method never commits, aborts, starts, or retries.
        """
        tx = _active_transaction(session)
        if type(evidence) is not AuthorizationRoleRevocationEvidence:
            _raise(AuthorizationRoleRevocationEvidencePersistenceError, "EVIDENCE_REQUIRED")
        try:
            historic = self._classify_existing(evidence, session=tx)
            if historic is not None:
                return historic
            self._collection.insert_one(evidence.to_persisted(), session=tx)
            return evidence
        except AuthorizationRoleRevocationEvidenceRegistryError:
            raise
        except DuplicateKeyError as error:
            try:
                historic = self._classify_existing(evidence, session=tx)
            except AuthorizationRoleRevocationEvidenceRegistryError:
                raise
            except (PyMongoError, AttributeError) as classify_error:
                _raise(
                    AuthorizationRoleRevocationEvidenceConflictError,
                    "WHOLE_TRANSACTION_RETRY_REQUIRED",
                    classify_error,
                )
            if historic is not None:
                return historic
            _raise(AuthorizationRoleRevocationEvidenceConflictError, "DUPLICATE_KEY_CONFLICT", error)
        except AttributeError as error:
            _raise(AuthorizationRoleRevocationEvidencePersistenceError, "COLLECTION_INTERFACE_INVALID", error)
        except PyMongoError as error:
            _raise(AuthorizationRoleRevocationEvidencePersistenceError, "PERSISTENCE_UNAVAILABLE", error)


__all__ = [
    "VERSION", "COLLECTION", "REVOCATION_ID_INDEX", "TENANT_IDEMPOTENCY_INDEX",
    "TARGET_ROLE_TIMELINE_INDEX", "AuthorizationRoleRevocationEvidenceRegistry",
    "AuthorizationRoleRevocationEvidenceRegistryError",
    "AuthorizationRoleRevocationEvidenceTransactionRequiredError",
    "AuthorizationRoleRevocationEvidenceNotFoundError",
    "AuthorizationRoleRevocationEvidenceConflictError",
    "AuthorizationRoleRevocationEvidencePersistedRecordInvalidError",
    "AuthorizationRoleRevocationEvidencePersistenceError",
]

# ARTIFACT: authorization_role_revocation_evidence_registry.py
# VERSION: v1.1.0-P1-R3C-E1-AUTHORIZATION-ROLE-REVOCATION-EVIDENCE-REGISTRY
# AUTHORITY BOUNDARY: durable revocation evidence persistence only; no authority, policy, role mutation, command atomicity, root lifecycle, break glass, activation, or finance
# TENANT POSTURE: exact tenant-scoped reads and idempotency; no default, global-root, or cross-tenant inference
# FAIL-CLOSED POSTURE: transaction absence, corruption, divergence, identity collision, duplicate race, and persistence outage reject
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# TTL INDEX: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
