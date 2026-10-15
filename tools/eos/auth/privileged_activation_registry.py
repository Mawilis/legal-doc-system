"""TITLE: WILSY OS Durable Privileged Activation Registry.
VERSION: v1.0.0-P4-R2-DURABLE-PRIVILEGED-ACTIVATION-REGISTRY
AUTHORITY: Persistence, replay classification, history integrity and exact-scope current resolution only.
EPITOME: Persists immutable P4 activation revisions without issuing privilege,
evaluating P2/P3, authorizing use, or owning transaction lifecycle.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/privileged_activation_registry.py
COLLABORATION / OWNERSHIP: P4-R1 activation domain; future P4 issuance and
revocation orchestration; future P5 privileged-use composition.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0-P4-R2 establishes immutable revision history, exact replay,
divergence and identity-collision rejection, exact-scope temporal resolution,
caller-owned active write transactions, BSON-aware UTC hydration, corruption
rejection, transient-error propagation, and a no-TTL durable-history posture.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Persists identifiers, timestamps and SHA3-512
lineage only; secrets, credentials, bearers, proof material and keys forbidden.
TENANT BOUNDARY: Every scope lookup binds target class, normalized tenant,
principal and privileged role; no principal-only or tenantless fallback.
AUTHORITY BOUNDARY: Persistence != issuance != permission != privileged use.
FINANCIAL AUTHORITY BOUNDARY: No payment, release, execution, or settlement.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hmac
from typing import Any, Final, Mapping

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.privileged_activation import (
    PrivilegedActivation,
    PrivilegedActivationError,
    PrivilegedActivationStatus,
)
from tools.eos.auth.privileged_eligibility import PrivilegedTargetClass
from tools.eos.auth.privileged_security_assurance import PrivilegedAssurancePurpose


VERSION: Final[str] = "v1.0.0-P4-R2-DURABLE-PRIVILEGED-ACTIVATION-REGISTRY"
COLLECTION: Final[str] = "privileged_activations"
ACTIVATION_REVISION_INDEX: Final[str] = "privileged_activation_revision_unique"
SCOPE_OPERATION_IDEMPOTENCY_INDEX: Final[str] = "privileged_activation_scope_operation_idempotency_unique"
SCOPE_TIMELINE_INDEX: Final[str] = "privileged_activation_scope_timeline"

_ISSUE: Final[str] = "ISSUE"
_REVOKE: Final[str] = "REVOKE"
_INTERNAL_FIELDS: Final[frozenset[str]] = frozenset(
    {"_id", "_scope_tenant_key", "_operation_kind", "_operation_idempotency_key", "activation_fingerprint"}
)


class PrivilegedActivationRegistryError(RuntimeError):
    """Base structured P4 registry failure carrying a stable code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class PrivilegedActivationTransactionRequiredError(PrivilegedActivationRegistryError):
    """A write was attempted without a caller-owned active transaction."""


class PrivilegedActivationConflictError(PrivilegedActivationRegistryError):
    """Replay, identity, revision, chain, or competing-current state conflicted."""


class PrivilegedActivationNotFoundError(PrivilegedActivationRegistryError):
    """The requested exact activation history was absent."""


class PrivilegedActivationPersistedInvalidError(PrivilegedActivationRegistryError):
    """Persisted activation material failed strict hydration or integrity."""


class PrivilegedActivationPersistenceError(PrivilegedActivationRegistryError):
    """Mongo persistence was unavailable or exposed an invalid interface."""


def _tenant_key(value: str | None) -> str:
    return "" if value is None else value


def _identifier(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or "*" in value:
        raise PrivilegedActivationRegistryError(name + "_INVALID")
    return value


def _timestamp(name: str, value: object) -> datetime:
    if not isinstance(value, datetime):
        raise PrivilegedActivationPersistedInvalidError(name + "_INVALID")
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _active_transaction(session: object) -> object:
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise PrivilegedActivationTransactionRequiredError("ACTIVE_TRANSACTION_REQUIRED")
    return session


def _scope_query(
    *,
    tenant_id: str | None,
    principal_id: str,
    privileged_role_id: str,
    target_class: PrivilegedTargetClass,
) -> dict[str, object]:
    if not isinstance(target_class, PrivilegedTargetClass):
        raise PrivilegedActivationRegistryError("TARGET_CLASS_INVALID")
    if target_class is PrivilegedTargetClass.TENANT_PRIVILEGED:
        tenant = _identifier("TENANT_ID", tenant_id)
    elif tenant_id is not None:
        raise PrivilegedActivationRegistryError("PLATFORM_SCOPE_TENANT_FORBIDDEN")
    else:
        tenant = None
    return {
        "target_class": target_class.value,
        "_scope_tenant_key": _tenant_key(tenant),
        "principal_id": _identifier("PRINCIPAL_ID", principal_id),
        "privileged_role_id": _identifier("PRIVILEGED_ROLE_ID", privileged_role_id),
    }


def _document(
    value: PrivilegedActivation,
    *,
    operation_kind: str,
    operation_idempotency_key: str,
) -> dict[str, object]:
    """Build one Mongo document without changing sealed authority semantics.

    The pure P4 domain deliberately serializes authority timestamps to canonical
    ISO text for deterministic fingerprinting. Mongo persistence, however, owns
    BSON datetime representation so default PyMongo hydration returns datetime
    values that the registry can normalize back to aware UTC.

    This conversion changes representation only. It does not change activation
    identity, fingerprint inputs, scope, lifetime, lifecycle, idempotency, or
    authority.
    """

    payload = value.authority_payload()
    payload["activated_at"] = value.activated_at
    payload["effective_until"] = value.effective_until
    payload["revoked_at"] = value.revoked_at

    return {
        **payload,
        "activation_fingerprint": value.activation_fingerprint,
        "_scope_tenant_key": _tenant_key(value.tenant_id),
        "_operation_kind": operation_kind,
        "_operation_idempotency_key": operation_idempotency_key,
    }


def _hydrate(row: object) -> PrivilegedActivation:
    if not isinstance(row, Mapping):
        raise PrivilegedActivationPersistedInvalidError("PERSISTED_RECORD_INVALID")
    expected = set(PrivilegedActivation.__dataclass_fields__) | {
        "schema", "version", "activation_fingerprint", "_scope_tenant_key",
        "_operation_kind", "_operation_idempotency_key",
    }
    clean = dict(row)
    clean.pop("_id", None)
    if set(clean) != expected:
        raise PrivilegedActivationPersistedInvalidError("PERSISTED_SHAPE_INVALID")
    if clean.get("schema") != "WILSY-PRIVILEGED-ACTIVATION/V1" or clean.get("version") != "v1.0.0-P4-R1-PRIVILEGED-ACTIVATION-DOMAIN":
        raise PrivilegedActivationPersistedInvalidError("PERSISTED_SCHEMA_VERSION_INVALID")
    if clean.get("_scope_tenant_key") != _tenant_key(clean.get("tenant_id")):  # type: ignore[arg-type]
        raise PrivilegedActivationPersistedInvalidError("PERSISTED_SCOPE_KEY_INVALID")
    if clean.get("_operation_kind") not in {_ISSUE, _REVOKE}:
        raise PrivilegedActivationPersistedInvalidError("PERSISTED_OPERATION_INVALID")
    _identifier("OPERATION_IDEMPOTENCY_KEY", clean.get("_operation_idempotency_key"))
    stored = clean.get("activation_fingerprint")
    try:
        value = PrivilegedActivation(
            activation_id=clean["activation_id"],  # type: ignore[arg-type]
            tenant_id=clean["tenant_id"],  # type: ignore[arg-type]
            principal_id=clean["principal_id"],  # type: ignore[arg-type]
            actor_principal_id=clean["actor_principal_id"],  # type: ignore[arg-type]
            privileged_role_id=clean["privileged_role_id"],  # type: ignore[arg-type]
            target_class=PrivilegedTargetClass(clean["target_class"]),
            eligibility_evidence_id=clean["eligibility_evidence_id"],  # type: ignore[arg-type]
            eligibility_evidence_fingerprint=clean["eligibility_evidence_fingerprint"],  # type: ignore[arg-type]
            assurance_evidence_id=clean["assurance_evidence_id"],  # type: ignore[arg-type]
            assurance_evidence_fingerprint=clean["assurance_evidence_fingerprint"],  # type: ignore[arg-type]
            creation_assurance_purpose=PrivilegedAssurancePurpose(clean["creation_assurance_purpose"]),
            activated_at=_timestamp("ACTIVATED_AT", clean["activated_at"]),
            effective_until=_timestamp("EFFECTIVE_UNTIL", clean["effective_until"]),
            status=PrivilegedActivationStatus(clean["status"]),
            revoked_at=None if clean["revoked_at"] is None else _timestamp("REVOKED_AT", clean["revoked_at"]),
            revision=clean["revision"],  # type: ignore[arg-type]
            previous_activation_fingerprint=clean["previous_activation_fingerprint"],  # type: ignore[arg-type]
            issuance_idempotency_key=clean["issuance_idempotency_key"],  # type: ignore[arg-type]
        )
    except (KeyError, TypeError, ValueError, PrivilegedActivationError) as error:
        raise PrivilegedActivationPersistedInvalidError("PERSISTED_RECORD_INVALID") from error
    if not isinstance(stored, str) or not value.fingerprint_matches(stored):
        raise PrivilegedActivationPersistedInvalidError("PERSISTED_FINGERPRINT_INVALID")
    return value


def _propagate_transient(error: PyMongoError) -> None:
    if error.has_error_label("TransientTransactionError"):
        raise error


class PrivilegedActivationRegistry:
    """Persist and resolve exact immutable P4 activation histories.

    Writes require an already-active caller transaction. The registry never
    starts, commits, aborts, or retries one and never evaluates issuance policy.
    """

    def __init__(self, collection: Any) -> None:
        """Bind one Mongo-compatible activation collection."""
        if collection is None:
            raise PrivilegedActivationPersistenceError("COLLECTION_REQUIRED")
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create exactly three sanctioned indexes, none with TTL semantics."""
        specs = (
            ([('activation_id', ASCENDING), ('revision', ASCENDING)], True, ACTIVATION_REVISION_INDEX),
            ([('target_class', ASCENDING), ('_scope_tenant_key', ASCENDING), ('principal_id', ASCENDING), ('privileged_role_id', ASCENDING), ('_operation_idempotency_key', ASCENDING)], True, SCOPE_OPERATION_IDEMPOTENCY_INDEX),
            ([('target_class', ASCENDING), ('_scope_tenant_key', ASCENDING), ('principal_id', ASCENDING), ('privileged_role_id', ASCENDING), ('activated_at', ASCENDING), ('activation_id', ASCENDING), ('revision', ASCENDING)], False, SCOPE_TIMELINE_INDEX),
        )
        try:
            for keys, unique, name in specs:
                self._collection.create_index(keys, unique=unique, name=name)
        except AttributeError as error:
            raise PrivilegedActivationPersistenceError("COLLECTION_INTERFACE_INVALID") from error
        except PyMongoError as error:
            _propagate_transient(error)
            raise PrivilegedActivationPersistenceError("INDEX_CREATION_FAILED") from error

    def _find_one(self, query: Mapping[str, object], *, session: object = None) -> Mapping[str, object] | None:
        try:
            return self._collection.find_one(dict(query), session=session)
        except AttributeError as error:
            raise PrivilegedActivationPersistenceError("COLLECTION_INTERFACE_INVALID") from error
        except PyMongoError as error:
            _propagate_transient(error)
            raise PrivilegedActivationPersistenceError("PERSISTENCE_UNAVAILABLE") from error

    def _find(self, query: Mapping[str, object], *, session: object = None) -> list[Mapping[str, object]]:
        try:
            return list(self._collection.find(dict(query), session=session))
        except AttributeError as error:
            raise PrivilegedActivationPersistenceError("COLLECTION_INTERFACE_INVALID") from error
        except PyMongoError as error:
            _propagate_transient(error)
            raise PrivilegedActivationPersistenceError("PERSISTENCE_UNAVAILABLE") from error

    def _insert(self, value: PrivilegedActivation, *, operation_kind: str, operation_idempotency_key: str, session: object) -> None:
        try:
            self._collection.insert_one(
                _document(value, operation_kind=operation_kind, operation_idempotency_key=operation_idempotency_key),
                session=session,
            )
        except DuplicateKeyError as error:
            if error.has_error_label("TransientTransactionError"):
                raise
            raise PrivilegedActivationConflictError("DUPLICATE_KEY_CONFLICT") from error
        except AttributeError as error:
            raise PrivilegedActivationPersistenceError("COLLECTION_INTERFACE_INVALID") from error
        except PyMongoError as error:
            _propagate_transient(error)
            raise PrivilegedActivationPersistenceError("PERSISTENCE_UNAVAILABLE") from error

    def get_history(self, activation_id: str, *, session: object = None) -> tuple[PrivilegedActivation, ...]:
        """Return and validate the complete exact activation revision chain."""
        identity = _identifier("ACTIVATION_ID", activation_id)
        values = [_hydrate(row) for row in self._find({"activation_id": identity}, session=session)]
        values.sort(key=lambda item: item.revision)
        if not values:
            return ()
        if values[0].revision != 1 or values[0].status is not PrivilegedActivationStatus.ACTIVE:
            raise PrivilegedActivationPersistedInvalidError("PERSISTED_CHAIN_INVALID")
        for expected, value in enumerate(values, start=1):
            if value.revision != expected:
                raise PrivilegedActivationPersistedInvalidError("PERSISTED_CHAIN_INVALID")
            if expected > 1:
                prior = values[expected - 2]
                if value.previous_activation_fingerprint != prior.activation_fingerprint:
                    raise PrivilegedActivationPersistedInvalidError("PERSISTED_CHAIN_INVALID")
                if value.activation_id != prior.activation_id or value.tenant_id != prior.tenant_id or value.principal_id != prior.principal_id or value.actor_principal_id != prior.actor_principal_id or value.privileged_role_id != prior.privileged_role_id or value.target_class is not prior.target_class or value.activated_at != prior.activated_at or value.effective_until != prior.effective_until or value.eligibility_evidence_id != prior.eligibility_evidence_id or value.eligibility_evidence_fingerprint != prior.eligibility_evidence_fingerprint or value.assurance_evidence_id != prior.assurance_evidence_id or value.assurance_evidence_fingerprint != prior.assurance_evidence_fingerprint or value.issuance_idempotency_key != prior.issuance_idempotency_key:
                    raise PrivilegedActivationPersistedInvalidError("PERSISTED_CHAIN_DIVERGENT")
        if len(values) > 2 or (len(values) == 2 and values[-1].status is not PrivilegedActivationStatus.REVOKED):
            raise PrivilegedActivationPersistedInvalidError("PERSISTED_CHAIN_INVALID")
        return tuple(values)

    def create_or_replay(self, activation: PrivilegedActivation, *, session: object) -> PrivilegedActivation:
        """Persist revision-one ACTIVE authority or return its exact replay."""
        tx = _active_transaction(session)
        if type(activation) is not PrivilegedActivation:
            raise PrivilegedActivationPersistenceError("ACTIVATION_REQUIRED")
        if activation.status is not PrivilegedActivationStatus.ACTIVE or activation.revision != 1:
            raise PrivilegedActivationConflictError("INITIAL_ACTIVE_REVISION_REQUIRED")
        scope = _scope_query(tenant_id=activation.tenant_id, principal_id=activation.principal_id, privileged_role_id=activation.privileged_role_id, target_class=activation.target_class)
        replay_row = self._find_one({**scope, "_operation_idempotency_key": activation.issuance_idempotency_key}, session=tx)
        if replay_row is not None:
            replay = _hydrate(replay_row)
            if replay == activation and replay_row.get("_operation_kind") == _ISSUE:
                return replay
            raise PrivilegedActivationConflictError("IDEMPOTENCY_KEY_DIVERGENT_REPLAY")
        if self.get_history(activation.activation_id, session=tx):
            raise PrivilegedActivationConflictError("ACTIVATION_ID_COLLISION")
        self._insert(activation, operation_kind=_ISSUE, operation_idempotency_key=activation.issuance_idempotency_key, session=tx)
        return activation

    def revoke_or_replay(self, activation: PrivilegedActivation, *, revocation_idempotency_key: str, session: object) -> PrivilegedActivation:
        """Persist an exact caller-created terminal successor or replay it."""
        tx = _active_transaction(session)
        replay_key = _identifier("REVOCATION_IDEMPOTENCY_KEY", revocation_idempotency_key)
        if type(activation) is not PrivilegedActivation or activation.status is not PrivilegedActivationStatus.REVOKED:
            raise PrivilegedActivationConflictError("REVOKED_ACTIVATION_REQUIRED")
        scope = _scope_query(tenant_id=activation.tenant_id, principal_id=activation.principal_id, privileged_role_id=activation.privileged_role_id, target_class=activation.target_class)
        replay_row = self._find_one({**scope, "_operation_idempotency_key": replay_key}, session=tx)
        if replay_row is not None:
            replay = _hydrate(replay_row)
            if replay == activation and replay_row.get("_operation_kind") == _REVOKE:
                return replay
            raise PrivilegedActivationConflictError("IDEMPOTENCY_KEY_DIVERGENT_REPLAY")
        history = self.get_history(activation.activation_id, session=tx)
        if not history:
            raise PrivilegedActivationNotFoundError("ACTIVATION_NOT_FOUND")
        current = history[-1]
        if current.status is PrivilegedActivationStatus.REVOKED:
            raise PrivilegedActivationConflictError("ACTIVATION_TERMINAL")
        if activation.revision != current.revision + 1 or activation.previous_activation_fingerprint != current.activation_fingerprint:
            raise PrivilegedActivationConflictError("STALE_OR_DIVERGENT_REVISION")
        expected = current.revoke(revoked_at=activation.revoked_at)  # type: ignore[arg-type]
        if expected != activation:
            raise PrivilegedActivationConflictError("REVOCATION_DIVERGENT")
        self._insert(activation, operation_kind=_REVOKE, operation_idempotency_key=replay_key, session=tx)
        return activation

    def resolve_current(
        self,
        *,
        tenant_id: str | None,
        principal_id: str,
        privileged_role_id: str,
        target_class: PrivilegedTargetClass,
        at: datetime,
        session: object = None,
    ) -> PrivilegedActivation | None:
        """Return the sole exact-scope current activation at explicit time."""
        observed = _timestamp("AT", at)
        scope = _scope_query(tenant_id=tenant_id, principal_id=principal_id, privileged_role_id=privileged_role_id, target_class=target_class)
        rows = self._find(scope, session=session)
        identities = {row.get("activation_id") for row in rows}
        if any(not isinstance(identity, str) for identity in identities):
            raise PrivilegedActivationPersistedInvalidError("PERSISTED_IDENTITY_INVALID")
        current: list[PrivilegedActivation] = []
        for identity in sorted(identities):  # type: ignore[type-var]
            history = self.get_history(identity, session=session)
            latest = history[-1]
            if latest.is_current(at=observed, tenant_id=tenant_id, principal_id=principal_id, privileged_role_id=privileged_role_id, target_class=target_class):
                current.append(latest)
        if len(current) > 1:
            raise PrivilegedActivationConflictError("MULTIPLE_CURRENT_ACTIVATIONS")
        return None if not current else current[0]


__all__ = [
    "VERSION", "COLLECTION", "ACTIVATION_REVISION_INDEX",
    "SCOPE_OPERATION_IDEMPOTENCY_INDEX", "SCOPE_TIMELINE_INDEX",
    "PrivilegedActivationRegistryError", "PrivilegedActivationTransactionRequiredError",
    "PrivilegedActivationConflictError", "PrivilegedActivationNotFoundError",
    "PrivilegedActivationPersistedInvalidError", "PrivilegedActivationPersistenceError",
    "PrivilegedActivationRegistry",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: privileged_activation_registry.py
# VERSION: v1.0.0-P4-R2-DURABLE-PRIVILEGED-ACTIVATION-REGISTRY
# AUTHORITY BOUNDARY: persistence/replay/current resolution only; no issuance/use
# TENANT POSTURE: exact target/tenant/principal/role scope; no fallback
# HISTORY: immutable ACTIVE revision plus optional terminal REVOKED revision
# TRANSACTION: caller-owned active transaction required for writes
# BSON TIME: valid naive datetime normalized to aware UTC; malformed rejects
# TTL: none; expired and revoked history remains durable
# BREAK GLASS / P5 / FINANCIAL AUTHORITY: none
# FAIL-CLOSED POSTURE: divergence, collision, corruption and concurrency deny
# END OF WILSY OS SOVEREIGN ARTIFACT
