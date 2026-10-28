"""TITLE: WILSY OS Transactional Ethical Wall Policy Registry.
VERSION: v1.0.0-G76-B-TRANSACTIONAL-WALL-REGISTRY
AUTHORITY: Immutable policy-evidence persistence and CAS currentness only.
EPITOME: Persists exact tenant/matter/policy revisions with deterministic
    current pointers, strict hydration, terminal revocation and whole-transaction
    retry signalling while never converting recorded evidence into access.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_work_ethical_wall_policy_registry.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering / Legal Operations;
    callers own Mongo transaction lifecycle and future enforcement owns reads.
CERTIFICATION / UPDATE DATE: 2026-10-21.
CHANGELOG: 2026-10-21 v1.0.0 introduces immutable revision persistence,
    independent current-pointer CAS, strict corruption detection and retry codes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque identities and fingerprints; no matter content.
TENANT BOUNDARY: Every identity, read, write and pointer is tenant/matter scoped.
TRANSACTION BOUNDARY: Active caller-owned transaction required; no fallback.
AUTHORITY BOUNDARY: Recorded ratification and membership never authorize access.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

from dataclasses import fields, replace
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.service.legal_work_ethical_wall_authorization_fence import (
    CanonicalWallAuthorizationFence,
    WallFenceUnavailable,
)

from tools.eos.legal_operations.domain.legal_work_ethical_wall_policy import (
    EthicalWallPolicyRevision as Revision,
    EthicalWallPolicyStatus,
    evaluate_ethical_wall_access,
)

VERSION: Final[str] = "v1.0.0-G76-B-TRANSACTIONAL-WALL-REGISTRY"
REVISION_COLLECTION: Final[str] = "legal_work_ethical_wall_policy_revisions"
CURRENT_COLLECTION: Final[str] = "legal_work_ethical_wall_policy_currentness"
IDENTITY_INDEX: Final[str] = "g76_wall_tenant_matter_policy_revision_unique"
ROOT_INDEX: Final[str] = "g76_wall_tenant_matter_policy_root_unique"
SUCCESSOR_INDEX: Final[str] = "g76_wall_tenant_matter_policy_successor_unique"
FINGERPRINT_INDEX: Final[str] = "g76_wall_tenant_fingerprint_unique"
HISTORY_INDEX: Final[str] = "g76_wall_tenant_matter_effective_history"
CURRENT_INDEX: Final[str] = "g76_wall_tenant_matter_policy_current_unique"
INDEX_NAMES: Final[tuple[str, ...]] = (
    IDENTITY_INDEX, ROOT_INDEX, SUCCESSOR_INDEX, FINGERPRINT_INDEX,
    HISTORY_INDEX, CURRENT_INDEX,
)
MAX_HISTORY: Final[int] = 256


class EthicalWallPolicyRegistryError(RuntimeError):
    """Base content-free G76-B registry failure."""


class EthicalWallPolicyTransactionRequired(EthicalWallPolicyRegistryError):
    """An active caller-owned transaction is mandatory."""


class EthicalWallPolicyConflict(EthicalWallPolicyRegistryError):
    """Replay, revision, lineage or terminal-state conflict."""


class EthicalWallPolicyNotFound(EthicalWallPolicyRegistryError):
    """No exact tenant/matter/policy evidence exists."""


class EthicalWallPolicyPersistedInvalid(EthicalWallPolicyRegistryError):
    """Durable revision history or currentness is malformed or contradictory."""


class EthicalWallPolicyRetryTransaction(EthicalWallPolicyRegistryError):
    """The caller must abort and retry the complete transaction from fresh state."""


class EthicalWallPolicyPersistenceUnavailable(EthicalWallPolicyRegistryError):
    """Mongo persistence is unavailable without a safe committed outcome."""


def _transaction(session: object) -> object:
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise EthicalWallPolicyTransactionRequired("G76_WALL_TRANSACTION_REQUIRED")
    return session


def _identity(name: str, value: object) -> str:
    from tools.eos.legal_operations.domain.legal_work_ethical_wall_policy import (
        _id as canonical_id,
    )

    try:
        return canonical_id(name, value)
    except Exception as error:
        raise EthicalWallPolicyRegistryError("G76_WALL_IDENTITY_INVALID") from error


_REVISION_FIELDS: Final[tuple[str, ...]] = tuple(item.name for item in fields(Revision))
_REVISION_INPUTS: Final[tuple[str, ...]] = tuple(
    name for name in _REVISION_FIELDS if name != "fingerprint"
)
_POINTER_FIELDS: Final[frozenset[str]] = frozenset({
    "tenant_id", "case_matter_id", "policy_id", "revision", "fingerprint",
    "status", "effective_from",
})


def _valid_revision(value: object) -> Revision:
    if type(value) is not Revision:
        raise EthicalWallPolicyPersistedInvalid("G76_WALL_REVISION_INVALID")
    try:
        canonical = replace(value)
        if canonical.fingerprint != value.fingerprint:
            raise ValueError("FINGERPRINT_MISMATCH")
        return canonical
    except Exception as error:
        raise EthicalWallPolicyPersistedInvalid("G76_WALL_REVISION_INVALID") from error


def _encode(value: Revision) -> dict[str, Any]:
    item = _valid_revision(value)
    document = {name: getattr(item, name) for name in _REVISION_FIELDS}
    for name in (
        "protected_subject_fingerprints", "restricted_principal_ids",
        "permitted_principal_ids",
    ):
        document[name] = list(document[name])
    return document


def _decode(document: object) -> Revision:
    if type(document) is not dict:
        raise EthicalWallPolicyPersistedInvalid("G76_WALL_DOCUMENT_INVALID")
    allowed = set(_REVISION_FIELDS) | {"_id"}
    if set(document) - allowed or not set(_REVISION_FIELDS).issubset(document):
        raise EthicalWallPolicyPersistedInvalid("G76_WALL_DOCUMENT_SHAPE_INVALID")
    try:
        values = {name: document[name] for name in _REVISION_INPUTS}
        for name in (
            "protected_subject_fingerprints", "restricted_principal_ids",
            "permitted_principal_ids",
        ):
            if type(values[name]) is not list:
                raise ValueError("STORED_ARRAY_INVALID")
            values[name] = tuple(values[name])
        item = Revision(**values)
        if item.fingerprint != document["fingerprint"]:
            raise ValueError("STORED_FINGERPRINT_MISMATCH")
        return item
    except Exception as error:
        raise EthicalWallPolicyPersistedInvalid("G76_WALL_DOCUMENT_INVALID") from error


def _scope(tenant_id: object, case_matter_id: object, policy_id: object) -> dict[str, str]:
    return {
        "tenant_id": _identity("tenant_id", tenant_id),
        "case_matter_id": _identity("case_matter_id", case_matter_id),
        "policy_id": _identity("policy_id", policy_id),
    }


def _pointer(value: Revision) -> dict[str, object]:
    return {
        "tenant_id": value.tenant_id,
        "case_matter_id": value.case_matter_id,
        "policy_id": value.policy_id,
        "revision": value.revision,
        "fingerprint": value.fingerprint,
        "status": EthicalWallPolicyStatus(value.status).value,
        "effective_from": value.effective_from,
    }


def _decode_pointer(document: object, scope: dict[str, str]) -> dict[str, object]:
    if type(document) is not dict:
        raise EthicalWallPolicyPersistedInvalid("G76_WALL_CURRENT_POINTER_INVALID")
    allowed = set(_POINTER_FIELDS) | {"_id"}
    if set(document) - allowed or not _POINTER_FIELDS.issubset(document):
        raise EthicalWallPolicyPersistedInvalid("G76_WALL_CURRENT_POINTER_INVALID")
    if any(document[name] != value for name, value in scope.items()):
        raise EthicalWallPolicyPersistedInvalid("G76_WALL_CURRENT_SCOPE_INVALID")
    if type(document["revision"]) is not int or document["revision"] < 1:
        raise EthicalWallPolicyPersistedInvalid("G76_WALL_CURRENT_REVISION_INVALID")
    try:
        EthicalWallPolicyStatus(document["status"])
    except (TypeError, ValueError) as error:
        raise EthicalWallPolicyPersistedInvalid("G76_WALL_CURRENT_STATUS_INVALID") from error
    return document


def _retryable(error: BaseException) -> bool:
    return isinstance(error, PyMongoError) and any(
        bool(error.has_error_label(label))
        for label in ("TransientTransactionError", "UnknownTransactionCommitResult")
    )


class EthicalWallPolicyRegistry:
    """Persist immutable wall evidence and transaction-coupled current pointers.

    Mutation semantics: append-only revisions plus compare-and-swap pointer.
    Idempotency: an exact same revision is returned; divergent reuse rejects.
    Transaction ownership: caller starts, commits, aborts and retries Mongo work.
    Authority: neither this registry nor its pointer grants content access.
    """

    def __init__(
        self, revision_collection: Any, current_collection: Any,
        authorization_fence: CanonicalWallAuthorizationFence,
    ) -> None:
        if authorization_fence is None:
            raise ValueError("G76_WALL_AUTHORIZATION_FENCE_REQUIRED")
        self._revisions = revision_collection
        self._current = current_collection
        self._authorization_fence = authorization_fence

    def ensure_indexes(self) -> None:
        """Install five uniqueness constraints and one non-TTL read index."""
        scope = [("tenant_id", ASCENDING), ("case_matter_id", ASCENDING),
                 ("policy_id", ASCENDING)]
        self._revisions.create_index(
            scope + [("revision", ASCENDING)], name=IDENTITY_INDEX, unique=True,
        )
        self._revisions.create_index(
            scope, name=ROOT_INDEX, unique=True,
            partialFilterExpression={"revision": 1},
        )
        self._revisions.create_index(
            scope + [("predecessor_fingerprint", ASCENDING)],
            name=SUCCESSOR_INDEX, unique=True,
            partialFilterExpression={"predecessor_fingerprint": {"$type": "string"}},
        )
        self._revisions.create_index(
            [("tenant_id", ASCENDING), ("fingerprint", ASCENDING)],
            name=FINGERPRINT_INDEX, unique=True,
        )
        self._revisions.create_index(
            [("tenant_id", ASCENDING), ("case_matter_id", ASCENDING),
             ("effective_from", ASCENDING), ("policy_id", ASCENDING)],
            name=HISTORY_INDEX,
        )
        self._current.create_index(scope, name=CURRENT_INDEX, unique=True)

    def list_history(
        self, tenant_id: str, case_matter_id: str, policy_id: str, *, session: object,
    ) -> tuple[Revision, ...]:
        """Return a complete exact-scope lineage or reject durable corruption."""
        active = _transaction(session)
        scope = _scope(tenant_id, case_matter_id, policy_id)
        try:
            documents = tuple(
                self._revisions.find(scope, session=active)
                .sort("revision", ASCENDING).limit(MAX_HISTORY + 1)
            )
        except Exception as error:
            if _retryable(error):
                raise EthicalWallPolicyRetryTransaction("G76_WALL_RETRY_TRANSACTION") from error
            raise EthicalWallPolicyPersistenceUnavailable("G76_WALL_READ_UNAVAILABLE") from error
        if len(documents) > MAX_HISTORY:
            raise EthicalWallPolicyPersistedInvalid("G76_WALL_HISTORY_OVERLONG")
        history = tuple(_decode(document) for document in documents)
        if any(
            item.tenant_id != scope["tenant_id"]
            or item.case_matter_id != scope["case_matter_id"]
            or item.policy_id != scope["policy_id"]
            for item in history
        ):
            raise EthicalWallPolicyPersistedInvalid("G76_WALL_SCOPE_MISMATCH")
        if history:
            at = max(item.effective_from for item in history)
            decision = evaluate_ethical_wall_access(
                tenant_id=scope["tenant_id"], case_matter_id=scope["case_matter_id"],
                practitioner_principal_id="g76-registry-lineage-probe",
                evaluation_time=at, revisions=history,
            )
            if decision.state.value == "DENIED_CORRUPT":
                raise EthicalWallPolicyPersistedInvalid("G76_WALL_HISTORY_CORRUPT")
        return history

    def get_current(
        self, tenant_id: str, case_matter_id: str, policy_id: str, *, session: object,
    ) -> Revision:
        """Resolve a pointer only when it exactly names the validated history leaf."""
        active = _transaction(session)
        scope = _scope(tenant_id, case_matter_id, policy_id)
        try:
            raw_pointer = self._current.find_one(scope, session=active)
        except Exception as error:
            if _retryable(error):
                raise EthicalWallPolicyRetryTransaction("G76_WALL_RETRY_TRANSACTION") from error
            raise EthicalWallPolicyPersistenceUnavailable("G76_WALL_CURRENT_READ_UNAVAILABLE") from error
        history = self.list_history(**scope, session=active)
        if raw_pointer is None:
            if history:
                raise EthicalWallPolicyPersistedInvalid("G76_WALL_CURRENT_POINTER_MISSING")
            raise EthicalWallPolicyNotFound("G76_WALL_POLICY_NOT_FOUND")
        pointer = _decode_pointer(raw_pointer, scope)
        if not history:
            raise EthicalWallPolicyPersistedInvalid("G76_WALL_CURRENT_WITHOUT_HISTORY")
        leaf = history[-1]
        if (
            pointer["revision"] != leaf.revision
            or pointer["fingerprint"] != leaf.fingerprint
            or pointer["status"] != EthicalWallPolicyStatus(leaf.status).value
            or pointer["effective_from"] != leaf.effective_from
        ):
            raise EthicalWallPolicyPersistedInvalid("G76_WALL_CURRENT_POINTER_MISMATCH")
        return leaf

    def append(self, value: Revision, *, session: object) -> Revision:
        """Append one next revision or exact replay, preserving terminal revocation."""
        active = _transaction(session)
        item = _valid_revision(value)
        scope = _scope(item.tenant_id, item.case_matter_id, item.policy_id)
        # Policy-wide sentinel fence is acquired before any revision/currentness
        # read. Every disclosure transaction contends on this same key, so a
        # concurrent revocation cannot authorize content from an older snapshot.
        try:
            self._authorization_fence.contend(
                tenant_id=item.tenant_id,
                case_matter_id=item.case_matter_id,
                practitioner_principal_id="policy",
                policy_id=item.policy_id,
                session=active,
            )
        except WallFenceUnavailable as error:
            if error.retryable:
                raise EthicalWallPolicyRetryTransaction("G76_WALL_RETRY_TRANSACTION") from error
            raise EthicalWallPolicyPersistenceUnavailable("G76_WALL_AUTHORIZATION_FENCE_UNAVAILABLE") from error
        identity = {**scope, "revision": item.revision}
        try:
            same_identity = self._revisions.find_one(identity, session=active)
        except Exception as error:
            if _retryable(error):
                raise EthicalWallPolicyRetryTransaction("G76_WALL_RETRY_TRANSACTION") from error
            raise EthicalWallPolicyPersistenceUnavailable("G76_WALL_IDENTITY_READ_UNAVAILABLE") from error
        if same_identity is not None:
            if _decode(same_identity) != item:
                raise EthicalWallPolicyConflict("G76_WALL_DIVERGENT_REPLAY")
            self.get_current(**scope, session=active)
            return item

        history = self.list_history(**scope, session=active)
        if not history:
            if item.revision != 1 or item.predecessor_fingerprint is not None:
                raise EthicalWallPolicyConflict("G76_WALL_ORPHAN_REVISION")
            try:
                self._revisions.insert_one(_encode(item), session=active)
                self._current.insert_one(_pointer(item), session=active)
            except DuplicateKeyError as error:
                raise EthicalWallPolicyRetryTransaction("G76_WALL_CONCURRENT_ROOT_RETRY") from error
            except Exception as error:
                if _retryable(error):
                    raise EthicalWallPolicyRetryTransaction("G76_WALL_RETRY_TRANSACTION") from error
                raise EthicalWallPolicyPersistenceUnavailable("G76_WALL_WRITE_UNAVAILABLE") from error
            return item

        current = self.get_current(**scope, session=active)
        if current.status is EthicalWallPolicyStatus.REVOKED:
            raise EthicalWallPolicyConflict("G76_WALL_TERMINAL_REVOKED")
        if (
            item.revision != current.revision + 1
            or item.predecessor_fingerprint != current.fingerprint
        ):
            raise EthicalWallPolicyConflict("G76_WALL_STALE_REVISION")
        try:
            self._revisions.insert_one(_encode(item), session=active)
            result = self._current.update_one(
                {**scope, "revision": current.revision,
                 "fingerprint": current.fingerprint,
                 "status": EthicalWallPolicyStatus(current.status).value,
                 "effective_from": current.effective_from},
                {"$set": {"revision": item.revision, "fingerprint": item.fingerprint,
                          "status": EthicalWallPolicyStatus(item.status).value,
                          "effective_from": item.effective_from}},
                session=active,
            )
        except DuplicateKeyError as error:
            raise EthicalWallPolicyRetryTransaction("G76_WALL_CONCURRENT_REVISION_RETRY") from error
        except Exception as error:
            if _retryable(error):
                raise EthicalWallPolicyRetryTransaction("G76_WALL_RETRY_TRANSACTION") from error
            raise EthicalWallPolicyPersistenceUnavailable("G76_WALL_WRITE_UNAVAILABLE") from error
        if result.modified_count != 1:
            raise EthicalWallPolicyRetryTransaction("G76_WALL_CURRENT_CAS_RETRY")
        return item


__all__ = [
    "VERSION", "REVISION_COLLECTION", "CURRENT_COLLECTION", "INDEX_NAMES",
    "IDENTITY_INDEX", "ROOT_INDEX", "SUCCESSOR_INDEX", "FINGERPRINT_INDEX",
    "HISTORY_INDEX", "CURRENT_INDEX", "MAX_HISTORY",
    "EthicalWallPolicyRegistryError", "EthicalWallPolicyTransactionRequired",
    "EthicalWallPolicyConflict", "EthicalWallPolicyNotFound",
    "EthicalWallPolicyPersistedInvalid", "EthicalWallPolicyRetryTransaction",
    "EthicalWallPolicyPersistenceUnavailable", "EthicalWallPolicyRegistry",
]

# ARTIFACT: legal_work_ethical_wall_policy_registry.py
# VERSION: v1.0.0-G76-B-TRANSACTIONAL-WALL-REGISTRY
# AUTHORITY BOUNDARY: immutable evidence persistence and CAS currentness only
# TENANT POSTURE: exact tenant/matter/policy; malformed or ambiguous truth blocks
# FAIL-CLOSED POSTURE: stale, forked, revoked, corrupt or unavailable never grants
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
