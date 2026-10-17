"""
WILSY OS — Legal Workflow Definition Registry

VERSION: v1.0.0-P9B-LEGAL-WORKFLOW-DEFINITION-REGISTRY

EPITOME:
    Immutable durable workflow-definition revision history for the sovereign
    Legal Operations workflow authority plane.

OWNERSHIP:
    LegalWorkflowDefinition owns definition semantics and fingerprint truth.
    This registry owns persistence, exact replay, strict hydration, revision
    sequencing, owner-scope isolation, and derived latest-revision lookup.

OWNER SCOPE:
    PLATFORM definitions use owner=PLATFORM and owner_tenant_id=None.
    TENANT definitions use owner=TENANT and their exact owner_tenant_id.
    Registry lookups always bind both owner and owner_tenant_id. Tenant-owned
    definitions cannot be inferred across tenant scope.

TRANSACTION BOUNDARY:
    The caller must provide one already-active Mongo transaction. This registry
    never starts, commits, aborts, retries, or owns transaction lifecycle.

DURABILITY:
    - owner + owner_tenant_id + workflow_definition_id + definition_revision
      is uniquely durable;
    - owner + owner_tenant_id + immutable fingerprint is uniquely durable;
    - revisions are append-only and contiguous from revision 1;
    - exact replay returns the persisted value;
    - divergent replay rejects;
    - duplicate races require whole-transaction retry;
    - current/latest revision is derived from immutable history;
    - no mutable current pointer;
    - no TTL, update, replace, or delete authority.

AUTHORITY BOUNDARY:
    Persistence is not workflow activation, matter admission, workflow
    transition, gate satisfaction, work-item authority, IAM, professional
    authority, browser authority, commercial authority, or financial execution.

FINANCIAL AUTHORITY:
    None. Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

import hmac
from typing import Any, Final, NoReturn, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_workflow_definition import (
    LegalWorkflowDefinition,
    LegalWorkflowDefinitionOwner,
)

VERSION: Final[str] = (
    "v1.0.0-P9B-LEGAL-WORKFLOW-DEFINITION-REGISTRY"
)

COLLECTION_NAME: Final[str] = "legal_workflow_definitions"

IDENTITY_INDEX_NAME: Final[str] = (
    "legal_workflow_definition_identity_unique"
)
FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_workflow_definition_fingerprint_unique"
)
class LegalWorkflowDefinitionRegistryError(RuntimeError):
    """Base fail-closed workflow-definition persistence error."""


class LegalWorkflowDefinitionRegistryInputError(
    LegalWorkflowDefinitionRegistryError
):
    """Caller supplied invalid registry input or collection shape."""


class LegalWorkflowDefinitionRegistryTransactionRequiredError(
    LegalWorkflowDefinitionRegistryError
):
    """Caller omitted one already-active Mongo transaction."""


class LegalWorkflowDefinitionRegistryConflictError(
    LegalWorkflowDefinitionRegistryError
):
    """Immutable identity, replay, fingerprint, or revision conflict."""


class LegalWorkflowDefinitionRegistryNotFoundError(
    LegalWorkflowDefinitionRegistryError
):
    """Exact scoped durable definition truth does not exist."""


class LegalWorkflowDefinitionRegistryPersistedRecordInvalidError(
    LegalWorkflowDefinitionRegistryError
):
    """Persisted definition cannot be trusted or violates requested scope."""


class LegalWorkflowDefinitionRegistryRetryTransactionError(
    LegalWorkflowDefinitionRegistryError
):
    """Caller must abort and retry the complete transaction."""


class LegalWorkflowDefinitionRegistryPersistenceError(
    LegalWorkflowDefinitionRegistryError
):
    """Mongo persistence failed without a safe success determination."""


def _raise(
    error_type: type[LegalWorkflowDefinitionRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _text(name: str, value: object, *, limit: int = 160) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or not value
        or len(value) > limit
        or any(ord(char) < 32 for char in value)
    ):
        _raise(
            LegalWorkflowDefinitionRegistryInputError,
            f"P9B_{name.upper()}_INVALID",
        )
    return cast(str, value)


def _revision(value: object) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        _raise(
            LegalWorkflowDefinitionRegistryInputError,
            "P9B_DEFINITION_REVISION_INVALID",
        )
    return cast(int, value)


def _transaction(session: object) -> object:
    if session is None:
        _raise(
            LegalWorkflowDefinitionRegistryTransactionRequiredError,
            "P9B_ACTIVE_TRANSACTION_REQUIRED",
        )

    try:
        active = getattr(session, "in_transaction")
    except (AttributeError, TypeError) as error:
        _raise(
            LegalWorkflowDefinitionRegistryTransactionRequiredError,
            "P9B_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )

    if active is not True:
        _raise(
            LegalWorkflowDefinitionRegistryTransactionRequiredError,
            "P9B_ACTIVE_TRANSACTION_REQUIRED",
        )

    return session


def _owner(
    value: LegalWorkflowDefinitionOwner | str,
) -> LegalWorkflowDefinitionOwner:
    try:
        return (
            value
            if isinstance(value, LegalWorkflowDefinitionOwner)
            else LegalWorkflowDefinitionOwner(value)
        )
    except (TypeError, ValueError) as error:
        _raise(
            LegalWorkflowDefinitionRegistryInputError,
            "P9B_OWNER_INVALID",
            error,
        )


def _owner_tenant(
    owner: LegalWorkflowDefinitionOwner,
    owner_tenant_id: object,
) -> str | None:
    if owner is LegalWorkflowDefinitionOwner.PLATFORM:
        if owner_tenant_id is not None:
            _raise(
                LegalWorkflowDefinitionRegistryInputError,
                "P9B_PLATFORM_OWNER_FORBIDS_TENANT",
            )
        return None

    if owner is LegalWorkflowDefinitionOwner.TENANT:
        tenant = _text(
            "owner_tenant_id",
            owner_tenant_id,
        )
        if tenant.casefold() in {
            "default",
            "global",
            "global_root",
            "root",
            "master",
            "*",
        }:
            _raise(
                LegalWorkflowDefinitionRegistryInputError,
                "P9B_OWNER_TENANT_REQUIRED",
            )
        return tenant

    _raise(
        LegalWorkflowDefinitionRegistryInputError,
        "P9B_OWNER_INVALID",
    )


def _scope(
    owner: LegalWorkflowDefinitionOwner | str,
    owner_tenant_id: object,
) -> tuple[LegalWorkflowDefinitionOwner, str | None]:
    normalized_owner = _owner(owner)
    return (
        normalized_owner,
        _owner_tenant(
            normalized_owner,
            owner_tenant_id,
        ),
    )


def _hydrate(
    raw: object,
) -> LegalWorkflowDefinition:
    if not isinstance(raw, dict):
        _raise(
            LegalWorkflowDefinitionRegistryPersistedRecordInvalidError,
            "P9B_PERSISTED_RECORD_INVALID",
        )

    payload = {
        key: value
        for key, value in raw.items()
        if key != "_id"
    }

    try:
        return LegalWorkflowDefinition.from_dict(payload)
    except Exception as error:
        _raise(
            LegalWorkflowDefinitionRegistryPersistedRecordInvalidError,
            "P9B_PERSISTED_RECORD_INVALID",
            error,
        )


def _equal(
    left: LegalWorkflowDefinition,
    right: LegalWorkflowDefinition,
) -> bool:
    return (
        hmac.compare_digest(
            left.fingerprint,
            right.fingerprint,
        )
        and left == right
    )


def _retry(error: BaseException) -> None:
    _raise(
        LegalWorkflowDefinitionRegistryRetryTransactionError,
        "P9B_WHOLE_TRANSACTION_RETRY_REQUIRED",
        error,
    )


class LegalWorkflowDefinitionRegistry:
    """Persist immutable workflow-definition revisions and nothing else."""

    def __init__(self, collection: Any) -> None:
        if collection is None:
            _raise(
                LegalWorkflowDefinitionRegistryInputError,
                "P9B_COLLECTION_REQUIRED",
            )
        self._collection: Any = collection

    def ensure_indexes(self) -> None:
        """Create exact non-TTL indexes for immutable definition history."""

        try:
            self._collection.create_index(
                [
                    ("owner", ASCENDING),
                    ("owner_tenant_id", ASCENDING),
                    ("workflow_definition_id", ASCENDING),
                    ("definition_revision", ASCENDING),
                ],
                unique=True,
                name=IDENTITY_INDEX_NAME,
            )
            self._collection.create_index(
                [
                    ("owner", ASCENDING),
                    ("owner_tenant_id", ASCENDING),
                    ("fingerprint", ASCENDING),
                ],
                unique=True,
                name=FINGERPRINT_INDEX_NAME,
            )
        except (AttributeError, TypeError, PyMongoError) as error:
            _raise(
                LegalWorkflowDefinitionRegistryInputError,
                "P9B_INDEX_CREATION_FAILED",
                error,
            )

    @staticmethod
    def _query_scope(
        owner: LegalWorkflowDefinitionOwner | str,
        owner_tenant_id: object,
    ) -> dict[str, object]:
        normalized_owner, tenant = _scope(
            owner,
            owner_tenant_id,
        )
        return {
            "owner": normalized_owner.value,
            "owner_tenant_id": tenant,
        }

    def get_revision(
        self,
        owner: LegalWorkflowDefinitionOwner | str,
        owner_tenant_id: object,
        workflow_definition_id: str,
        definition_revision: int,
        *,
        session: object,
    ) -> LegalWorkflowDefinition:
        """Return one exact owner-scoped immutable definition revision."""

        tx = _transaction(session)
        definition_id = _text(
            "workflow_definition_id",
            workflow_definition_id,
        )
        revision = _revision(
            definition_revision
        )

        query = self._query_scope(
            owner,
            owner_tenant_id,
        )
        query.update(
            {
                "workflow_definition_id":
                    definition_id,
                "definition_revision":
                    revision,
            }
        )

        try:
            raw = self._collection.find_one(
                query,
                session=tx,
            )
        except (AttributeError, TypeError, PyMongoError) as error:
            _raise(
                LegalWorkflowDefinitionRegistryPersistenceError,
                "P9B_PERSISTENCE_UNAVAILABLE",
                error,
            )

        if raw is None:
            _raise(
                LegalWorkflowDefinitionRegistryNotFoundError,
                "P9B_REVISION_NOT_FOUND",
            )

        value = _hydrate(raw)
        expected_owner, expected_tenant = _scope(
            owner,
            owner_tenant_id,
        )

        if (
            value.owner is not expected_owner
            or value.owner_tenant_id
            != expected_tenant
            or value.workflow_definition_id
            != definition_id
            or value.definition_revision
            != revision
        ):
            _raise(
                LegalWorkflowDefinitionRegistryPersistedRecordInvalidError,
                "P9B_PERSISTED_SCOPE_MISMATCH",
            )

        return value

    def get_history_if_any(
        self,
        owner: LegalWorkflowDefinitionOwner | str,
        owner_tenant_id: object,
        workflow_definition_id: str,
        *,
        session: object,
    ) -> tuple[LegalWorkflowDefinition, ...]:
        """Return strict immutable owner-scoped history or an empty tuple."""

        tx = _transaction(session)
        definition_id = _text(
            "workflow_definition_id",
            workflow_definition_id,
        )

        query = self._query_scope(
            owner,
            owner_tenant_id,
        )
        query["workflow_definition_id"] = (
            definition_id
        )

        try:
            cursor = self._collection.find(
                query,
                session=tx,
            )
            rows = tuple(
                cursor.sort(
                    "definition_revision",
                    ASCENDING,
                )
            )
        except (AttributeError, TypeError, PyMongoError) as error:
            _raise(
                LegalWorkflowDefinitionRegistryPersistenceError,
                "P9B_PERSISTENCE_UNAVAILABLE",
                error,
            )

        values = tuple(
            _hydrate(raw)
            for raw in rows
        )

        expected_owner, expected_tenant = _scope(
            owner,
            owner_tenant_id,
        )

        for expected_revision, value in enumerate(
            values,
            start=1,
        ):
            if (
                value.owner is not expected_owner
                or value.owner_tenant_id
                != expected_tenant
                or value.workflow_definition_id
                != definition_id
            ):
                _raise(
                    LegalWorkflowDefinitionRegistryPersistedRecordInvalidError,
                    "P9B_PERSISTED_SCOPE_MISMATCH",
                )

            if (
                value.definition_revision
                != expected_revision
            ):
                _raise(
                    LegalWorkflowDefinitionRegistryPersistedRecordInvalidError,
                    "P9B_PERSISTED_REVISION_GAP",
                )

        return values

    def get_history(
        self,
        owner: LegalWorkflowDefinitionOwner | str,
        owner_tenant_id: object,
        workflow_definition_id: str,
        *,
        session: object,
    ) -> tuple[LegalWorkflowDefinition, ...]:
        """Return strict immutable definition history and reject absence."""

        values = self.get_history_if_any(
            owner,
            owner_tenant_id,
            workflow_definition_id,
            session=session,
        )

        if not values:
            _raise(
                LegalWorkflowDefinitionRegistryNotFoundError,
                "P9B_HISTORY_NOT_FOUND",
            )

        return values

    def create_or_replay(
        self,
        value: LegalWorkflowDefinition,
        *,
        session: object,
    ) -> LegalWorkflowDefinition:
        """Append exact next revision or return one exact persisted replay."""

        tx = _transaction(session)

        if not isinstance(
            value,
            LegalWorkflowDefinition,
        ):
            _raise(
                LegalWorkflowDefinitionRegistryConflictError,
                "P9B_DOMAIN_VALUE_REQUIRED",
            )

        normalized_owner = _owner(
            value.owner
        )
        normalized_tenant = _owner_tenant(
            normalized_owner,
            value.owner_tenant_id,
        )

        identity_query = {
            "owner": normalized_owner.value,
            "owner_tenant_id":
                normalized_tenant,
            "workflow_definition_id":
                value.workflow_definition_id,
            "definition_revision":
                value.definition_revision,
        }

        try:
            existing_raw = (
                self._collection.find_one(
                    identity_query,
                    session=tx,
                )
            )
        except (AttributeError, TypeError, PyMongoError) as error:
            _raise(
                LegalWorkflowDefinitionRegistryPersistenceError,
                "P9B_PERSISTENCE_UNAVAILABLE",
                error,
            )

        if existing_raw is not None:
            existing = _hydrate(
                existing_raw
            )

            if _equal(
                existing,
                value,
            ):
                return existing

            _raise(
                LegalWorkflowDefinitionRegistryConflictError,
                "P9B_DIVERGENT_REPLAY",
            )

        fingerprint_query = {
            "owner": normalized_owner.value,
            "owner_tenant_id":
                normalized_tenant,
            "fingerprint":
                value.fingerprint,
        }

        try:
            fingerprint_raw = (
                self._collection.find_one(
                    fingerprint_query,
                    session=tx,
                )
            )
        except (AttributeError, TypeError, PyMongoError) as error:
            _raise(
                LegalWorkflowDefinitionRegistryPersistenceError,
                "P9B_PERSISTENCE_UNAVAILABLE",
                error,
            )

        if fingerprint_raw is not None:
            collision = _hydrate(
                fingerprint_raw
            )

            if not _equal(
                collision,
                value,
            ):
                _raise(
                    LegalWorkflowDefinitionRegistryConflictError,
                    "P9B_FINGERPRINT_COLLISION",
                )

        history = self.get_history_if_any(
            normalized_owner,
            normalized_tenant,
            value.workflow_definition_id,
            session=tx,
        )

        if (
            value.definition_revision
            != len(history) + 1
        ):
            _raise(
                LegalWorkflowDefinitionRegistryConflictError,
                "P9B_REVISION_SEQUENCE_CONFLICT",
            )

        try:
            self._collection.insert_one(
                value.to_dict(),
                session=tx,
            )
        except DuplicateKeyError as error:
            _retry(error)
        except (AttributeError, TypeError, PyMongoError) as error:
            _raise(
                LegalWorkflowDefinitionRegistryPersistenceError,
                "P9B_PERSISTENCE_UNAVAILABLE",
                error,
            )

        return self.get_revision(
            normalized_owner,
            normalized_tenant,
            value.workflow_definition_id,
            value.definition_revision,
            session=tx,
        )

    def resolve_latest(
        self,
        owner: LegalWorkflowDefinitionOwner | str,
        owner_tenant_id: object,
        workflow_definition_id: str,
        *,
        session: object,
    ) -> LegalWorkflowDefinition | None:
        """Derive the latest immutable revision; persist no current pointer."""

        history = self.get_history_if_any(
            owner,
            owner_tenant_id,
            workflow_definition_id,
            session=session,
        )

        if not history:
            return None

        return history[-1]


def ensure_indexes(
    collection: Any,
) -> None:
    """Create Legal workflow-definition indexes."""

    LegalWorkflowDefinitionRegistry(
        collection
    ).ensure_indexes()


__all__ = [
    "COLLECTION_NAME",
    "FINGERPRINT_INDEX_NAME",
    "IDENTITY_INDEX_NAME",
    "VERSION",
    "LegalWorkflowDefinitionRegistry",
    "LegalWorkflowDefinitionRegistryConflictError",
    "LegalWorkflowDefinitionRegistryError",
    "LegalWorkflowDefinitionRegistryInputError",
    "LegalWorkflowDefinitionRegistryNotFoundError",
    "LegalWorkflowDefinitionRegistryPersistedRecordInvalidError",
    "LegalWorkflowDefinitionRegistryPersistenceError",
    "LegalWorkflowDefinitionRegistryRetryTransactionError",
    "LegalWorkflowDefinitionRegistryTransactionRequiredError",
    "ensure_indexes",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: legal_workflow_definition_registry.py
# VERSION: v1.0.0-P9B-LEGAL-WORKFLOW-DEFINITION-REGISTRY
# APPEND-ONLY IMMUTABLE REVISION HISTORY: YES
# OWNER SCOPE: PLATFORM or exact TENANT owner; never browser-derived
# CALLER-OWNED ACTIVE TRANSACTION REQUIRED: YES
# MUTABLE CURRENT POINTER: NONE
# TTL / UPDATE / REPLACE / DELETE AUTHORITY: NONE
# WORKFLOW ACTIVATION / TRANSITION / GATE / WORK-ITEM AUTHORITY: NONE
# IAM / PROFESSIONAL / COMMERCIAL AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
