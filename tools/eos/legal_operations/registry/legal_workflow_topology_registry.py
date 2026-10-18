"""
WILSY OS — Legal Workflow Topology Registry

VERSION: v1.0.0-P10B-LEGAL-WORKFLOW-TOPOLOGY-REGISTRY

EPITOME:
    Immutable persistence for one LegalWorkflowTopology bound to one already
    durable LegalWorkflowDefinition revision.

AUTHORITY COMPOSITION:
    LegalWorkflowTopology owns graph semantics.
    LegalWorkflowDefinitionRegistry owns definition owner scope and durable
    definition truth.

    This registry NEVER invents tenant or owner fields for topology. Instead,
    every write resolves the exact durable workflow definition under caller-
    supplied owner scope and proves:

      topology.workflow_definition_id == durable definition identity
      topology.definition_revision == durable definition revision
      topology.workflow_definition_fingerprint == durable definition fingerprint

    The immutable definition fingerprint therefore carries owner/tenant scope
    into topology identity without duplicating ownership into the topology
    domain contract.

TRANSACTION BOUNDARY:
    Caller provides one already-active Mongo transaction. This registry never
    starts, commits, aborts, retries, or owns transaction lifecycle.

DURABILITY:
    - workflow_definition_fingerprint uniquely identifies one topology authority;
    - topology fingerprint is independently unique;
    - exact replay returns durable truth;
    - divergent topology for the same definition fingerprint rejects;
    - duplicate races require whole-transaction retry;
    - strict hydration rejects corrupt persistence;
    - no mutable current pointer;
    - no TTL, update, replace, or delete authority.

AUTHORITY BOUNDARY:
    Persistence does not create workflow-definition, activation, matter,
    transition, gate, work-item, IAM, professional, commercial, browser, or
    financial authority.
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
from tools.eos.legal_operations.domain.legal_workflow_topology import (
    LegalWorkflowTopology,
)
from tools.eos.legal_operations.registry.legal_workflow_definition_registry import (
    LegalWorkflowDefinitionRegistry,
)

VERSION: Final[str] = (
    "v1.0.0-P10B-LEGAL-WORKFLOW-TOPOLOGY-REGISTRY"
)

COLLECTION_NAME: Final[str] = "legal_workflow_topologies"

DEFINITION_FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_workflow_topology_definition_fingerprint_unique"
)

FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_workflow_topology_fingerprint_unique"
)

DEFINITION_LOOKUP_INDEX_NAME: Final[str] = (
    "legal_workflow_topology_definition_lookup"
)


class LegalWorkflowTopologyRegistryError(RuntimeError):
    """Base fail-closed topology persistence error."""


class LegalWorkflowTopologyRegistryInputError(
    LegalWorkflowTopologyRegistryError
):
    """Caller supplied invalid registry input."""


class LegalWorkflowTopologyRegistryTransactionRequiredError(
    LegalWorkflowTopologyRegistryError
):
    """Caller omitted one already-active Mongo transaction."""


class LegalWorkflowTopologyRegistryConflictError(
    LegalWorkflowTopologyRegistryError
):
    """Immutable identity or replay conflict."""


class LegalWorkflowTopologyRegistryNotFoundError(
    LegalWorkflowTopologyRegistryError
):
    """Exact durable topology truth does not exist."""


class LegalWorkflowTopologyRegistryPersistedRecordInvalidError(
    LegalWorkflowTopologyRegistryError
):
    """Durable topology cannot be trusted."""


class LegalWorkflowTopologyRegistryRetryTransactionError(
    LegalWorkflowTopologyRegistryError
):
    """Caller must restart the whole transaction."""


class LegalWorkflowTopologyRegistryPersistenceError(
    LegalWorkflowTopologyRegistryError
):
    """Mongo persistence failed without safe success evidence."""


def _raise(
    error_type: type[LegalWorkflowTopologyRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(code)

    if cause is None:
        raise error

    raise error from cause


def _text(
    name: str,
    value: object,
    *,
    limit: int = 160,
) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or not value
        or len(value) > limit
        or any(ord(char) < 32 for char in value)
    ):
        _raise(
            LegalWorkflowTopologyRegistryInputError,
            f"P10B_{name.upper()}_INVALID",
        )

    return cast(str, value)


def _fingerprint(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 128
        or value.lower() != value
    ):
        _raise(
            LegalWorkflowTopologyRegistryInputError,
            f"P10B_{name.upper()}_INVALID",
        )

    try:
        int(value, 16)
    except ValueError as error:
        _raise(
            LegalWorkflowTopologyRegistryInputError,
            f"P10B_{name.upper()}_INVALID",
            error,
        )

    return cast(str, value)


def _revision(value: object) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        _raise(
            LegalWorkflowTopologyRegistryInputError,
            "P10B_DEFINITION_REVISION_INVALID",
        )

    return cast(int, value)


def _transaction(
    session: object,
) -> object:
    if session is None:
        _raise(
            LegalWorkflowTopologyRegistryTransactionRequiredError,
            "P10B_ACTIVE_TRANSACTION_REQUIRED",
        )

    try:
        active = getattr(
            session,
            "in_transaction",
        )
    except (AttributeError, TypeError) as error:
        _raise(
            LegalWorkflowTopologyRegistryTransactionRequiredError,
            "P10B_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )

    if active is not True:
        _raise(
            LegalWorkflowTopologyRegistryTransactionRequiredError,
            "P10B_ACTIVE_TRANSACTION_REQUIRED",
        )

    return session


def _hydrate(
    raw: object,
) -> LegalWorkflowTopology:
    if not isinstance(raw, dict):
        _raise(
            LegalWorkflowTopologyRegistryPersistedRecordInvalidError,
            "P10B_PERSISTED_RECORD_INVALID",
        )

    payload = {
        key: value
        for key, value in raw.items()
        if key != "_id"
    }

    try:
        return LegalWorkflowTopology.from_dict(
            payload
        )
    except Exception as error:
        _raise(
            LegalWorkflowTopologyRegistryPersistedRecordInvalidError,
            "P10B_PERSISTED_RECORD_INVALID",
            error,
        )


def _equal(
    left: LegalWorkflowTopology,
    right: LegalWorkflowTopology,
) -> bool:
    return (
        hmac.compare_digest(
            left.fingerprint,
            right.fingerprint,
        )
        and left == right
    )


class LegalWorkflowTopologyRegistry:
    """Persist exact topology truth bound to durable definition authority."""

    def __init__(
        self,
        collection: Any,
        *,
        definition_registry: LegalWorkflowDefinitionRegistry,
    ) -> None:
        if collection is None:
            _raise(
                LegalWorkflowTopologyRegistryInputError,
                "P10B_COLLECTION_REQUIRED",
            )

        if not isinstance(
            definition_registry,
            LegalWorkflowDefinitionRegistry,
        ):
            _raise(
                LegalWorkflowTopologyRegistryInputError,
                "P10B_DEFINITION_REGISTRY_REQUIRED",
            )

        self._collection: Any = collection
        self._definition_registry = (
            definition_registry
        )

    def ensure_indexes(self) -> None:
        """Create immutable non-TTL topology indexes."""

        try:
            self._collection.create_index(
                [
                    (
                        "workflow_definition_fingerprint",
                        ASCENDING,
                    ),
                ],
                unique=True,
                name=(
                    DEFINITION_FINGERPRINT_INDEX_NAME
                ),
            )

            self._collection.create_index(
                [
                    ("fingerprint", ASCENDING),
                ],
                unique=True,
                name=FINGERPRINT_INDEX_NAME,
            )

            self._collection.create_index(
                [
                    (
                        "workflow_definition_id",
                        ASCENDING,
                    ),
                    (
                        "definition_revision",
                        ASCENDING,
                    ),
                ],
                unique=False,
                name=DEFINITION_LOOKUP_INDEX_NAME,
            )
        except (
            AttributeError,
            TypeError,
            PyMongoError,
        ) as error:
            _raise(
                LegalWorkflowTopologyRegistryInputError,
                "P10B_INDEX_CREATION_FAILED",
                error,
            )

    def _durable_definition(
        self,
        *,
        owner: LegalWorkflowDefinitionOwner | str,
        owner_tenant_id: object,
        workflow_definition_id: str,
        definition_revision: int,
        session: object,
    ) -> LegalWorkflowDefinition:
        return (
            self._definition_registry.get_revision(
                owner,
                owner_tenant_id,
                _text(
                    "workflow_definition_id",
                    workflow_definition_id,
                ),
                _revision(
                    definition_revision
                ),
                session=session,
            )
        )

    @staticmethod
    def _prove_binding(
        topology: LegalWorkflowTopology,
        definition: LegalWorkflowDefinition,
    ) -> None:
        if (
            topology.workflow_definition_id
            != definition.workflow_definition_id
            or topology.definition_revision
            != definition.definition_revision
            or not hmac.compare_digest(
                topology.workflow_definition_fingerprint,
                definition.fingerprint,
            )
        ):
            _raise(
                LegalWorkflowTopologyRegistryConflictError,
                "P10B_DURABLE_DEFINITION_BINDING_MISMATCH",
            )

    def get_by_definition_fingerprint(
        self,
        workflow_definition_fingerprint: str,
        *,
        session: object,
    ) -> LegalWorkflowTopology:
        """Return exact topology bound to one immutable definition fingerprint."""

        tx = _transaction(session)
        durable_fingerprint = _fingerprint(
            "workflow_definition_fingerprint",
            workflow_definition_fingerprint,
        )

        try:
            raw = self._collection.find_one(
                {
                    "workflow_definition_fingerprint":
                        durable_fingerprint,
                },
                session=tx,
            )
        except (
            AttributeError,
            TypeError,
            PyMongoError,
        ) as error:
            _raise(
                LegalWorkflowTopologyRegistryPersistenceError,
                "P10B_PERSISTENCE_UNAVAILABLE",
                error,
            )

        if raw is None:
            _raise(
                LegalWorkflowTopologyRegistryNotFoundError,
                "P10B_TOPOLOGY_NOT_FOUND",
            )

        value = _hydrate(raw)

        if not hmac.compare_digest(
            value.workflow_definition_fingerprint,
            durable_fingerprint,
        ):
            _raise(
                LegalWorkflowTopologyRegistryPersistedRecordInvalidError,
                "P10B_PERSISTED_SCOPE_MISMATCH",
            )

        return value

    def get_by_fingerprint(
        self,
        topology_fingerprint: str,
        *,
        session: object,
    ) -> LegalWorkflowTopology:
        """Return one exact immutable topology fingerprint."""

        tx = _transaction(session)
        requested = _fingerprint(
            "topology_fingerprint",
            topology_fingerprint,
        )

        try:
            raw = self._collection.find_one(
                {
                    "fingerprint":
                        requested,
                },
                session=tx,
            )
        except (
            AttributeError,
            TypeError,
            PyMongoError,
        ) as error:
            _raise(
                LegalWorkflowTopologyRegistryPersistenceError,
                "P10B_PERSISTENCE_UNAVAILABLE",
                error,
            )

        if raw is None:
            _raise(
                LegalWorkflowTopologyRegistryNotFoundError,
                "P10B_TOPOLOGY_NOT_FOUND",
            )

        value = _hydrate(raw)

        if not hmac.compare_digest(
            value.fingerprint,
            requested,
        ):
            _raise(
                LegalWorkflowTopologyRegistryPersistedRecordInvalidError,
                "P10B_PERSISTED_SCOPE_MISMATCH",
            )

        return value

    def create_or_replay(
        self,
        value: LegalWorkflowTopology,
        *,
        owner: LegalWorkflowDefinitionOwner | str,
        owner_tenant_id: object,
        session: object,
    ) -> LegalWorkflowTopology:
        """Persist one topology only after re-proving durable definition truth."""

        tx = _transaction(session)

        if not isinstance(
            value,
            LegalWorkflowTopology,
        ):
            _raise(
                LegalWorkflowTopologyRegistryConflictError,
                "P10B_DOMAIN_VALUE_REQUIRED",
            )

        definition = self._durable_definition(
            owner=owner,
            owner_tenant_id=
                owner_tenant_id,
            workflow_definition_id=
                value.workflow_definition_id,
            definition_revision=
                value.definition_revision,
            session=tx,
        )

        self._prove_binding(
            value,
            definition,
        )

        identity_query = {
            "workflow_definition_fingerprint":
                value.workflow_definition_fingerprint,
        }

        try:
            existing_raw = (
                self._collection.find_one(
                    identity_query,
                    session=tx,
                )
            )
        except (
            AttributeError,
            TypeError,
            PyMongoError,
        ) as error:
            _raise(
                LegalWorkflowTopologyRegistryPersistenceError,
                "P10B_PERSISTENCE_UNAVAILABLE",
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
                LegalWorkflowTopologyRegistryConflictError,
                "P10B_DIVERGENT_REPLAY",
            )

        try:
            fingerprint_raw = (
                self._collection.find_one(
                    {
                        "fingerprint":
                            value.fingerprint,
                    },
                    session=tx,
                )
            )
        except (
            AttributeError,
            TypeError,
            PyMongoError,
        ) as error:
            _raise(
                LegalWorkflowTopologyRegistryPersistenceError,
                "P10B_PERSISTENCE_UNAVAILABLE",
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
                    LegalWorkflowTopologyRegistryConflictError,
                    "P10B_FINGERPRINT_COLLISION",
                )

        try:
            self._collection.insert_one(
                value.to_dict(),
                session=tx,
            )
        except DuplicateKeyError as error:
            _raise(
                LegalWorkflowTopologyRegistryRetryTransactionError,
                "P10B_WHOLE_TRANSACTION_RETRY_REQUIRED",
                error,
            )
        except (
            AttributeError,
            TypeError,
            PyMongoError,
        ) as error:
            _raise(
                LegalWorkflowTopologyRegistryPersistenceError,
                "P10B_PERSISTENCE_UNAVAILABLE",
                error,
            )

        return self.get_by_definition_fingerprint(
            value.workflow_definition_fingerprint,
            session=tx,
        )


def ensure_indexes(
    collection: Any,
    *,
    definition_registry: LegalWorkflowDefinitionRegistry,
) -> None:
    """Create Legal workflow topology indexes."""

    LegalWorkflowTopologyRegistry(
        collection,
        definition_registry=
            definition_registry,
    ).ensure_indexes()


__all__ = [
    "COLLECTION_NAME",
    "DEFINITION_FINGERPRINT_INDEX_NAME",
    "DEFINITION_LOOKUP_INDEX_NAME",
    "FINGERPRINT_INDEX_NAME",
    "VERSION",
    "LegalWorkflowTopologyRegistry",
    "LegalWorkflowTopologyRegistryConflictError",
    "LegalWorkflowTopologyRegistryError",
    "LegalWorkflowTopologyRegistryInputError",
    "LegalWorkflowTopologyRegistryNotFoundError",
    "LegalWorkflowTopologyRegistryPersistedRecordInvalidError",
    "LegalWorkflowTopologyRegistryPersistenceError",
    "LegalWorkflowTopologyRegistryRetryTransactionError",
    "LegalWorkflowTopologyRegistryTransactionRequiredError",
    "ensure_indexes",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: legal_workflow_topology_registry.py
# VERSION: v1.0.0-P10B-LEGAL-WORKFLOW-TOPOLOGY-REGISTRY
# DEFINITION AUTHORITY: exact durable P9B definition revision
# TOPOLOGY OWNER / TENANT FIELD INVENTED: NO
# SCOPE ANCHOR: immutable workflow_definition_fingerprint
# EXACT REPLAY / DIVERGENT REPLAY: governed
# CALLER-OWNED ACTIVE TRANSACTION REQUIRED: YES
# MUTABLE CURRENT POINTER: NONE
# TTL / UPDATE / REPLACE / DELETE AUTHORITY: NONE
# ACTIVATION / TRANSITION / GATE / WORK-ITEM AUTHORITY: NONE
# IAM / PROFESSIONAL / COMMERCIAL AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
