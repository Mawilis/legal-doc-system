"""
WILSY OS — Legal Workflow Stage Registry

VERSION: v1.0.0-P11B-LEGAL-WORKFLOW-STAGE-REGISTRY

EPITOME:
    Immutable persistence for LegalWorkflowStage truth admitted only when the
    stage is bound to one already-durable workflow definition and is an exact
    member of the already-durable certified workflow topology.

AUTHORITY COMPOSITION:
    LegalWorkflowDefinitionRegistry owns durable definition owner scope.
    LegalWorkflowTopologyRegistry owns durable whole-graph certification.
    LegalWorkflowStage owns stage semantics and immutable fingerprint truth.

    This registry NEVER invents owner, tenant, or topology fields inside the
    stage domain contract.

    Every write proves:
      stage.workflow_definition_id == durable definition identity
      stage.definition_revision == durable definition revision
      stage.workflow_definition_fingerprint == durable definition fingerprint

    Then the durable topology is resolved by that immutable definition
    fingerprint and the registry proves:
      stage.stage_definition_id exists in topology.stages
      topology stage.stage_fingerprint == stage.fingerprint

TRANSACTION BOUNDARY:
    Caller supplies one already-active Mongo transaction. This registry never
    starts, commits, aborts, retries, or owns transaction lifecycle.

DURABILITY:
    - workflow_definition_fingerprint + stage_definition_id is uniquely durable;
    - immutable stage fingerprint is independently unique;
    - exact replay returns durable truth;
    - divergent identity or topology-membership drift rejects;
    - corrupt persistence rejects;
    - duplicate races require whole-transaction retry;
    - no mutable current pointer;
    - no TTL, update, replace, or delete authority.

AUTHORITY BOUNDARY:
    Stage persistence creates no activation, workflow-instance, transition,
    gate-satisfaction, work-item, IAM, professional, browser, commercial, or
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
from tools.eos.legal_operations.domain.legal_workflow_stage import (
    LegalWorkflowStage,
)
from tools.eos.legal_operations.domain.legal_workflow_topology import (
    LegalWorkflowTopology,
)
from tools.eos.legal_operations.registry.legal_workflow_definition_registry import (
    LegalWorkflowDefinitionRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_topology_registry import (
    LegalWorkflowTopologyRegistry,
)

VERSION: Final[str] = (
    "v1.0.0-P11B-LEGAL-WORKFLOW-STAGE-REGISTRY"
)

COLLECTION_NAME: Final[str] = "legal_workflow_stages"

IDENTITY_INDEX_NAME: Final[str] = (
    "legal_workflow_stage_definition_identity_unique"
)

FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_workflow_stage_fingerprint_unique"
)

DEFINITION_LOOKUP_INDEX_NAME: Final[str] = (
    "legal_workflow_stage_definition_lookup"
)


class LegalWorkflowStageRegistryError(RuntimeError):
    """Base fail-closed stage-persistence error."""


class LegalWorkflowStageRegistryInputError(
    LegalWorkflowStageRegistryError
):
    """Caller supplied invalid registry input."""


class LegalWorkflowStageRegistryTransactionRequiredError(
    LegalWorkflowStageRegistryError
):
    """Caller omitted one already-active Mongo transaction."""


class LegalWorkflowStageRegistryConflictError(
    LegalWorkflowStageRegistryError
):
    """Immutable stage identity, binding, or replay conflict."""


class LegalWorkflowStageRegistryNotFoundError(
    LegalWorkflowStageRegistryError
):
    """Exact durable stage truth does not exist."""


class LegalWorkflowStageRegistryPersistedRecordInvalidError(
    LegalWorkflowStageRegistryError
):
    """Persisted stage cannot be trusted."""


class LegalWorkflowStageRegistryRetryTransactionError(
    LegalWorkflowStageRegistryError
):
    """Caller must restart the complete transaction."""


class LegalWorkflowStageRegistryPersistenceError(
    LegalWorkflowStageRegistryError
):
    """Mongo persistence failed without safe success evidence."""


def _raise(
    error_type: type[LegalWorkflowStageRegistryError],
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
            LegalWorkflowStageRegistryInputError,
            f"P11B_{name.upper()}_INVALID",
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
            LegalWorkflowStageRegistryInputError,
            f"P11B_{name.upper()}_INVALID",
        )

    try:
        int(value, 16)
    except ValueError as error:
        _raise(
            LegalWorkflowStageRegistryInputError,
            f"P11B_{name.upper()}_INVALID",
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
            LegalWorkflowStageRegistryInputError,
            "P11B_DEFINITION_REVISION_INVALID",
        )

    return cast(int, value)


def _transaction(
    session: object,
) -> object:
    if session is None:
        _raise(
            LegalWorkflowStageRegistryTransactionRequiredError,
            "P11B_ACTIVE_TRANSACTION_REQUIRED",
        )

    try:
        active = getattr(
            session,
            "in_transaction",
        )
    except (AttributeError, TypeError) as error:
        _raise(
            LegalWorkflowStageRegistryTransactionRequiredError,
            "P11B_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )

    if active is not True:
        _raise(
            LegalWorkflowStageRegistryTransactionRequiredError,
            "P11B_ACTIVE_TRANSACTION_REQUIRED",
        )

    return session


def _hydrate(
    raw: object,
) -> LegalWorkflowStage:
    if not isinstance(raw, dict):
        _raise(
            LegalWorkflowStageRegistryPersistedRecordInvalidError,
            "P11B_PERSISTED_RECORD_INVALID",
        )

    payload = {
        key: value
        for key, value in raw.items()
        if key != "_id"
    }

    try:
        return LegalWorkflowStage.from_dict(
            payload
        )
    except Exception as error:
        _raise(
            LegalWorkflowStageRegistryPersistedRecordInvalidError,
            "P11B_PERSISTED_RECORD_INVALID",
            error,
        )


def _equal(
    left: LegalWorkflowStage,
    right: LegalWorkflowStage,
) -> bool:
    return (
        hmac.compare_digest(
            left.fingerprint,
            right.fingerprint,
        )
        and left == right
    )


class LegalWorkflowStageRegistry:
    """Persist only stages certified by durable definition and topology truth."""

    def __init__(
        self,
        collection: Any,
        *,
        definition_registry: LegalWorkflowDefinitionRegistry,
        topology_registry: LegalWorkflowTopologyRegistry,
    ) -> None:
        if collection is None:
            _raise(
                LegalWorkflowStageRegistryInputError,
                "P11B_COLLECTION_REQUIRED",
            )

        if not isinstance(
            definition_registry,
            LegalWorkflowDefinitionRegistry,
        ):
            _raise(
                LegalWorkflowStageRegistryInputError,
                "P11B_DEFINITION_REGISTRY_REQUIRED",
            )

        if not isinstance(
            topology_registry,
            LegalWorkflowTopologyRegistry,
        ):
            _raise(
                LegalWorkflowStageRegistryInputError,
                "P11B_TOPOLOGY_REGISTRY_REQUIRED",
            )

        self._collection: Any = collection
        self._definition_registry = (
            definition_registry
        )
        self._topology_registry = (
            topology_registry
        )

    def ensure_indexes(self) -> None:
        """Create immutable non-TTL stage indexes."""

        try:
            self._collection.create_index(
                [
                    (
                        "workflow_definition_fingerprint",
                        ASCENDING,
                    ),
                    (
                        "stage_definition_id",
                        ASCENDING,
                    ),
                ],
                unique=True,
                name=IDENTITY_INDEX_NAME,
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
                LegalWorkflowStageRegistryInputError,
                "P11B_INDEX_CREATION_FAILED",
                error,
            )

    def _durable_definition(
        self,
        *,
        owner: LegalWorkflowDefinitionOwner | str,
        owner_tenant_id: object,
        value: LegalWorkflowStage,
        session: object,
    ) -> LegalWorkflowDefinition:
        return self._definition_registry.get_revision(
            owner,
            owner_tenant_id,
            _text(
                "workflow_definition_id",
                value.workflow_definition_id,
            ),
            _revision(
                value.definition_revision
            ),
            session=session,
        )

    @staticmethod
    def _prove_definition_binding(
        stage: LegalWorkflowStage,
        definition: LegalWorkflowDefinition,
    ) -> None:
        if (
            stage.workflow_definition_id
            != definition.workflow_definition_id
            or stage.definition_revision
            != definition.definition_revision
            or not hmac.compare_digest(
                stage.workflow_definition_fingerprint,
                definition.fingerprint,
            )
        ):
            _raise(
                LegalWorkflowStageRegistryConflictError,
                "P11B_DURABLE_DEFINITION_BINDING_MISMATCH",
            )

    def _durable_topology(
        self,
        workflow_definition_fingerprint: str,
        *,
        session: object,
    ) -> LegalWorkflowTopology:
        return (
            self._topology_registry
            .get_by_definition_fingerprint(
                _fingerprint(
                    "workflow_definition_fingerprint",
                    workflow_definition_fingerprint,
                ),
                session=session,
            )
        )

    @staticmethod
    def _prove_topology_membership(
        stage: LegalWorkflowStage,
        topology: LegalWorkflowTopology,
    ) -> None:
        if (
            stage.workflow_definition_id
            != topology.workflow_definition_id
            or stage.definition_revision
            != topology.definition_revision
            or not hmac.compare_digest(
                stage.workflow_definition_fingerprint,
                topology.workflow_definition_fingerprint,
            )
        ):
            _raise(
                LegalWorkflowStageRegistryConflictError,
                "P11B_STAGE_TOPOLOGY_BINDING_MISMATCH",
            )

        topology_stage = None

        for value in topology.stages:
            if (
                value.stage_definition_id
                == stage.stage_definition_id
            ):
                topology_stage = value
                break

        if topology_stage is None:
            _raise(
                LegalWorkflowStageRegistryConflictError,
                "P11B_STAGE_NOT_IN_DURABLE_TOPOLOGY",
            )

        if not hmac.compare_digest(
            topology_stage.stage_fingerprint,
            stage.fingerprint,
        ):
            _raise(
                LegalWorkflowStageRegistryConflictError,
                "P11B_STAGE_FINGERPRINT_MISMATCH",
            )

    def _reprove_topology_membership(
        self,
        value: LegalWorkflowStage,
        *,
        session: object,
    ) -> None:
        topology = self._durable_topology(
            value.workflow_definition_fingerprint,
            session=session,
        )

        self._prove_topology_membership(
            value,
            topology,
        )

    def get_by_definition_stage(
        self,
        workflow_definition_fingerprint: str,
        stage_definition_id: str,
        *,
        session: object,
    ) -> LegalWorkflowStage:
        """Return exact durable stage and re-prove current immutable topology."""

        tx = _transaction(session)
        definition_fingerprint = _fingerprint(
            "workflow_definition_fingerprint",
            workflow_definition_fingerprint,
        )
        stage_id = _text(
            "stage_definition_id",
            stage_definition_id,
        )

        try:
            raw = self._collection.find_one(
                {
                    "workflow_definition_fingerprint":
                        definition_fingerprint,
                    "stage_definition_id":
                        stage_id,
                },
                session=tx,
            )
        except (
            AttributeError,
            TypeError,
            PyMongoError,
        ) as error:
            _raise(
                LegalWorkflowStageRegistryPersistenceError,
                "P11B_PERSISTENCE_UNAVAILABLE",
                error,
            )

        if raw is None:
            _raise(
                LegalWorkflowStageRegistryNotFoundError,
                "P11B_STAGE_NOT_FOUND",
            )

        value = _hydrate(raw)

        if (
            value.stage_definition_id
            != stage_id
            or not hmac.compare_digest(
                value.workflow_definition_fingerprint,
                definition_fingerprint,
            )
        ):
            _raise(
                LegalWorkflowStageRegistryPersistedRecordInvalidError,
                "P11B_PERSISTED_SCOPE_MISMATCH",
            )

        self._reprove_topology_membership(
            value,
            session=tx,
        )

        return value

    def get_by_fingerprint(
        self,
        stage_fingerprint: str,
        *,
        session: object,
    ) -> LegalWorkflowStage:
        """Return exact immutable stage fingerprint with topology re-proof."""

        tx = _transaction(session)
        requested = _fingerprint(
            "stage_fingerprint",
            stage_fingerprint,
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
                LegalWorkflowStageRegistryPersistenceError,
                "P11B_PERSISTENCE_UNAVAILABLE",
                error,
            )

        if raw is None:
            _raise(
                LegalWorkflowStageRegistryNotFoundError,
                "P11B_STAGE_NOT_FOUND",
            )

        value = _hydrate(raw)

        if not hmac.compare_digest(
            value.fingerprint,
            requested,
        ):
            _raise(
                LegalWorkflowStageRegistryPersistedRecordInvalidError,
                "P11B_PERSISTED_SCOPE_MISMATCH",
            )

        self._reprove_topology_membership(
            value,
            session=tx,
        )

        return value

    def create_or_replay(
        self,
        value: LegalWorkflowStage,
        *,
        owner: LegalWorkflowDefinitionOwner | str,
        owner_tenant_id: object,
        session: object,
    ) -> LegalWorkflowStage:
        """Persist one exact stage only after full durable authority re-proof."""

        tx = _transaction(session)

        if not isinstance(
            value,
            LegalWorkflowStage,
        ):
            _raise(
                LegalWorkflowStageRegistryConflictError,
                "P11B_DOMAIN_VALUE_REQUIRED",
            )

        definition = self._durable_definition(
            owner=owner,
            owner_tenant_id=
                owner_tenant_id,
            value=value,
            session=tx,
        )

        self._prove_definition_binding(
            value,
            definition,
        )

        topology = self._durable_topology(
            value.workflow_definition_fingerprint,
            session=tx,
        )

        self._prove_topology_membership(
            value,
            topology,
        )

        identity_query = {
            "workflow_definition_fingerprint":
                value.workflow_definition_fingerprint,
            "stage_definition_id":
                value.stage_definition_id,
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
                LegalWorkflowStageRegistryPersistenceError,
                "P11B_PERSISTENCE_UNAVAILABLE",
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
                self._prove_topology_membership(
                    existing,
                    topology,
                )
                return existing

            _raise(
                LegalWorkflowStageRegistryConflictError,
                "P11B_DIVERGENT_REPLAY",
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
                LegalWorkflowStageRegistryPersistenceError,
                "P11B_PERSISTENCE_UNAVAILABLE",
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
                    LegalWorkflowStageRegistryConflictError,
                    "P11B_FINGERPRINT_COLLISION",
                )

        try:
            self._collection.insert_one(
                value.to_dict(),
                session=tx,
            )
        except DuplicateKeyError as error:
            _raise(
                LegalWorkflowStageRegistryRetryTransactionError,
                "P11B_WHOLE_TRANSACTION_RETRY_REQUIRED",
                error,
            )
        except (
            AttributeError,
            TypeError,
            PyMongoError,
        ) as error:
            _raise(
                LegalWorkflowStageRegistryPersistenceError,
                "P11B_PERSISTENCE_UNAVAILABLE",
                error,
            )

        return self.get_by_definition_stage(
            value.workflow_definition_fingerprint,
            value.stage_definition_id,
            session=tx,
        )


def ensure_indexes(
    collection: Any,
    *,
    definition_registry: LegalWorkflowDefinitionRegistry,
    topology_registry: LegalWorkflowTopologyRegistry,
) -> None:
    """Create exact Legal workflow stage indexes."""

    LegalWorkflowStageRegistry(
        collection,
        definition_registry=
            definition_registry,
        topology_registry=
            topology_registry,
    ).ensure_indexes()


__all__ = [
    "COLLECTION_NAME",
    "DEFINITION_LOOKUP_INDEX_NAME",
    "FINGERPRINT_INDEX_NAME",
    "IDENTITY_INDEX_NAME",
    "VERSION",
    "LegalWorkflowStageRegistry",
    "LegalWorkflowStageRegistryConflictError",
    "LegalWorkflowStageRegistryError",
    "LegalWorkflowStageRegistryInputError",
    "LegalWorkflowStageRegistryNotFoundError",
    "LegalWorkflowStageRegistryPersistedRecordInvalidError",
    "LegalWorkflowStageRegistryPersistenceError",
    "LegalWorkflowStageRegistryRetryTransactionError",
    "LegalWorkflowStageRegistryTransactionRequiredError",
    "ensure_indexes",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: legal_workflow_stage_registry.py
# VERSION: v1.0.0-P11B-LEGAL-WORKFLOW-STAGE-REGISTRY
# DEFINITION AUTHORITY: exact durable P9B definition revision
# TOPOLOGY AUTHORITY: exact durable P10B topology membership
# STAGE OWNER / TENANT FIELD INVENTED: NO
# STAGE TOPOLOGY FIELD INVENTED: NO
# SCOPE ANCHOR: workflow_definition_fingerprint + stage_definition_id
# EXACT REPLAY / DIVERGENT REPLAY: governed
# CALLER-OWNED ACTIVE TRANSACTION REQUIRED: YES
# MUTABLE CURRENT POINTER: NONE
# TTL / UPDATE / REPLACE / DELETE AUTHORITY: NONE
# ACTIVATION / TRANSITION / GATE / WORK-ITEM AUTHORITY: NONE
# IAM / PROFESSIONAL / COMMERCIAL AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
