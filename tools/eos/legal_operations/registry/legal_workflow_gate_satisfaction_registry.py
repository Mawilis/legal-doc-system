"""
WILSY OS — Legal Workflow Gate Satisfaction Registry

VERSION: v1.0.0-P12B-LEGAL-WORKFLOW-GATE-SATISFACTION-REGISTRY

AUTHORITY: Wilsy OS Core Governance / Legal Operations.

EPITOME:
    Persist immutable positive LegalWorkflowGateSatisfaction facts only after
    re-proving their exact durable workflow instance, topology, source stage,
    configured completion gate, and cryptographic bindings.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/
    legal_workflow_gate_satisfaction_registry.py

COLLABORATION / OWNERSHIP:
    Consumes LegalMatterWorkflowInstanceRegistry,
    LegalWorkflowTopologyRegistry, and LegalWorkflowStageRegistry inside one
    caller-owned active Mongo transaction. Transition composition may consume
    these facts later, but this registry grants no transition authority.

CERTIFICATION DATE: 2026-10-16

CHANGELOG:
    v1.0.0-P12B — Introduces tenant-scoped immutable persistence, exact replay,
    durable authority re-proof, strict hydration, non-TTL indexes, and
    whole-transaction retry classification for duplicate races.

COMPLIANCE:
    POPIA section 19 / GDPR Article 32 / SOC 2 CC7.2 tenant isolation.

SECURITY / PRIVACY POSTURE:
    Every lookup is tenant-scoped where tenant-bearing truth is addressed.
    Stored evidence references are preserved as supplied by the domain object;
    this registry does not dereference, disclose, or manufacture legal evidence.

TENANT BOUNDARY:
    tenant_id + gate_satisfaction_id is the durable identity. Cross-tenant
    absence is reported as ordinary not-found truth.

AUTHORITY BOUNDARY:
    A persisted row proves only that one configured gate was positively
    evaluated against the recorded immutable evidence bindings. It does not
    create a workflow transition, current-stage pointer, assignment, IAM,
    professional authority, commercial entitlement, or legal-service truth.

FINANCIAL AUTHORITY BOUNDARY:
    NONE. Kennel EOS remains the exclusive financial execution authority.

TRANSACTION BOUNDARY:
    Every operational read or write requires one caller-owned already-active
    Mongo transaction. This registry never starts, commits, aborts, or retries
    transaction lifecycle. Transient and duplicate races require the caller to
    restart the whole transaction from fresh state.
"""

from __future__ import annotations

from collections.abc import Mapping
import hmac
from typing import Any, Final, NoReturn, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_matter_workflow_instance import (
    LegalMatterWorkflowInstance,
)
from tools.eos.legal_operations.domain.legal_workflow_gate_satisfaction import (
    LegalWorkflowGateSatisfaction,
)
from tools.eos.legal_operations.domain.legal_workflow_stage import (
    LegalWorkflowStage,
)
from tools.eos.legal_operations.domain.legal_workflow_topology import (
    LegalWorkflowTopology,
)
from tools.eos.legal_operations.registry.legal_matter_workflow_instance_registry import (
    LegalMatterWorkflowInstanceRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_stage_registry import (
    LegalWorkflowStageRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_topology_registry import (
    LegalWorkflowTopologyRegistry,
)


VERSION: Final[str] = (
    "v1.0.0-P12B-LEGAL-WORKFLOW-GATE-SATISFACTION-REGISTRY"
)
COLLECTION_NAME: Final[str] = "legal_workflow_gate_satisfactions"
IDENTITY_INDEX_NAME: Final[str] = (
    "legal_workflow_gate_satisfaction_identity_unique"
)
FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_workflow_gate_satisfaction_fingerprint_unique"
)
INSTANCE_HISTORY_INDEX_NAME: Final[str] = (
    "legal_workflow_gate_satisfaction_instance_history"
)


class LegalWorkflowGateSatisfactionRegistryError(RuntimeError):
    """Base stable failure for immutable gate-satisfaction persistence."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalWorkflowGateSatisfactionRegistryInputError(
    LegalWorkflowGateSatisfactionRegistryError
):
    """Caller supplied malformed registry input or composition."""


class LegalWorkflowGateSatisfactionRegistryTransactionRequiredError(
    LegalWorkflowGateSatisfactionRegistryError
):
    """Caller omitted one already-active Mongo transaction."""


class LegalWorkflowGateSatisfactionRegistryConflictError(
    LegalWorkflowGateSatisfactionRegistryError
):
    """Immutable replay or durable authority binding conflicts."""


class LegalWorkflowGateSatisfactionRegistryNotFoundError(
    LegalWorkflowGateSatisfactionRegistryError
):
    """Exact tenant-scoped satisfaction truth does not exist."""


class LegalWorkflowGateSatisfactionRegistryPersistedRecordInvalidError(
    LegalWorkflowGateSatisfactionRegistryError
):
    """Persisted data failed strict domain hydration or scope proof."""


class LegalWorkflowGateSatisfactionRegistryRetryTransactionError(
    LegalWorkflowGateSatisfactionRegistryError
):
    """Caller must restart the complete transaction from fresh state."""


class LegalWorkflowGateSatisfactionRegistryPersistenceError(
    LegalWorkflowGateSatisfactionRegistryError
):
    """Mongo persistence failed without safe success evidence."""


def _raise(
    error_type: type[LegalWorkflowGateSatisfactionRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _text(name: str, value: object, *, limit: int = 320) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(character) < 32 for character in value)
    ):
        _raise(
            LegalWorkflowGateSatisfactionRegistryInputError,
            f"P12B_{name.upper()}_INVALID",
        )
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant_id = _text("tenant_id", value)
    if tenant_id.casefold() in {
        "default",
        "global",
        "global_root",
        "root",
        "master",
        "*",
    }:
        _raise(
            LegalWorkflowGateSatisfactionRegistryInputError,
            "P12B_TENANT_REQUIRED",
        )
    return tenant_id


def _fingerprint(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 128
        or value.lower() != value
    ):
        _raise(
            LegalWorkflowGateSatisfactionRegistryInputError,
            f"P12B_{name.upper()}_INVALID",
        )
    try:
        int(value, 16)
    except ValueError as error:
        _raise(
            LegalWorkflowGateSatisfactionRegistryInputError,
            f"P12B_{name.upper()}_INVALID",
            error,
        )
    return cast(str, value)


def _transaction(session: object) -> object:
    if session is None:
        _raise(
            LegalWorkflowGateSatisfactionRegistryTransactionRequiredError,
            "P12B_ACTIVE_TRANSACTION_REQUIRED",
        )
    try:
        active = getattr(session, "in_transaction")
    except (AttributeError, TypeError) as error:
        _raise(
            LegalWorkflowGateSatisfactionRegistryTransactionRequiredError,
            "P12B_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )
    if active is not True:
        _raise(
            LegalWorkflowGateSatisfactionRegistryTransactionRequiredError,
            "P12B_ACTIVE_TRANSACTION_REQUIRED",
        )
    return session


def _hydrate(raw: object) -> LegalWorkflowGateSatisfaction:
    if not isinstance(raw, Mapping):
        _raise(
            LegalWorkflowGateSatisfactionRegistryPersistedRecordInvalidError,
            "P12B_PERSISTED_RECORD_INVALID",
        )
    payload = dict(raw)
    payload.pop("_id", None)
    try:
        return LegalWorkflowGateSatisfaction.from_dict(payload)
    except Exception as error:
        _raise(
            LegalWorkflowGateSatisfactionRegistryPersistedRecordInvalidError,
            "P12B_PERSISTED_RECORD_INVALID",
            error,
        )


def _equal(
    left: LegalWorkflowGateSatisfaction,
    right: LegalWorkflowGateSatisfaction,
) -> bool:
    return hmac.compare_digest(left.fingerprint, right.fingerprint) and left == right


def _mongo_failure(error: PyMongoError) -> NoReturn:
    try:
        transient = error.has_error_label("TransientTransactionError")
    except Exception:
        transient = False
    if transient:
        _raise(
            LegalWorkflowGateSatisfactionRegistryRetryTransactionError,
            "P12B_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )
    _raise(
        LegalWorkflowGateSatisfactionRegistryPersistenceError,
        "P12B_PERSISTENCE_UNAVAILABLE",
        error,
    )


class LegalWorkflowGateSatisfactionRegistry:
    """Persist immutable positive gate facts after durable authority re-proof."""

    def __init__(
        self,
        collection: Any,
        *,
        instance_registry: LegalMatterWorkflowInstanceRegistry,
        topology_registry: LegalWorkflowTopologyRegistry,
        stage_registry: LegalWorkflowStageRegistry,
    ) -> None:
        if collection is None:
            _raise(
                LegalWorkflowGateSatisfactionRegistryInputError,
                "P12B_COLLECTION_REQUIRED",
            )
        if not isinstance(instance_registry, LegalMatterWorkflowInstanceRegistry):
            _raise(
                LegalWorkflowGateSatisfactionRegistryInputError,
                "P12B_INSTANCE_REGISTRY_REQUIRED",
            )
        if not isinstance(topology_registry, LegalWorkflowTopologyRegistry):
            _raise(
                LegalWorkflowGateSatisfactionRegistryInputError,
                "P12B_TOPOLOGY_REGISTRY_REQUIRED",
            )
        if not isinstance(stage_registry, LegalWorkflowStageRegistry):
            _raise(
                LegalWorkflowGateSatisfactionRegistryInputError,
                "P12B_STAGE_REGISTRY_REQUIRED",
            )
        self._collection = collection
        self._instance_registry = instance_registry
        self._topology_registry = topology_registry
        self._stage_registry = stage_registry

    def ensure_indexes(self) -> None:
        """Create exact tenant-scoped immutable non-TTL indexes."""
        try:
            self._collection.create_index(
                [("tenant_id", ASCENDING), ("gate_satisfaction_id", ASCENDING)],
                unique=True,
                name=IDENTITY_INDEX_NAME,
            )
            self._collection.create_index(
                [("tenant_id", ASCENDING), ("fingerprint", ASCENDING)],
                unique=True,
                name=FINGERPRINT_INDEX_NAME,
            )
            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("workflow_instance_id", ASCENDING),
                    ("source_stage_definition_id", ASCENDING),
                    ("gate_reference", ASCENDING),
                    ("evaluated_at", ASCENDING),
                    ("gate_satisfaction_id", ASCENDING),
                ],
                unique=False,
                name=INSTANCE_HISTORY_INDEX_NAME,
            )
        except (AttributeError, TypeError, PyMongoError) as error:
            _raise(
                LegalWorkflowGateSatisfactionRegistryPersistenceError,
                "P12B_INDEX_CREATION_FAILED",
                error,
            )

    @staticmethod
    def _prove_instance_binding(
        value: LegalWorkflowGateSatisfaction,
        instance: LegalMatterWorkflowInstance,
    ) -> None:
        if (
            value.tenant_id != instance.tenant_id
            or value.case_matter_id != instance.case_matter_id
            or value.workflow_instance_id != instance.workflow_instance_id
            or not hmac.compare_digest(
                value.workflow_instance_fingerprint, instance.fingerprint
            )
            or not hmac.compare_digest(
                value.workflow_topology_fingerprint,
                instance.workflow_topology_fingerprint,
            )
        ):
            _raise(
                LegalWorkflowGateSatisfactionRegistryConflictError,
                "P12B_DURABLE_INSTANCE_BINDING_MISMATCH",
            )

    @staticmethod
    def _prove_topology_binding(
        value: LegalWorkflowGateSatisfaction,
        topology: LegalWorkflowTopology,
    ) -> None:
        if not hmac.compare_digest(
            value.workflow_topology_fingerprint, topology.fingerprint
        ):
            _raise(
                LegalWorkflowGateSatisfactionRegistryConflictError,
                "P12B_DURABLE_TOPOLOGY_BINDING_MISMATCH",
            )
        topology_stage = next(
            (
                stage
                for stage in topology.stages
                if stage.stage_definition_id == value.source_stage_definition_id
            ),
            None,
        )
        if topology_stage is None:
            _raise(
                LegalWorkflowGateSatisfactionRegistryConflictError,
                "P12B_SOURCE_STAGE_NOT_IN_DURABLE_TOPOLOGY",
            )
        if not hmac.compare_digest(
            topology_stage.stage_fingerprint, value.source_stage_fingerprint
        ):
            _raise(
                LegalWorkflowGateSatisfactionRegistryConflictError,
                "P12B_TOPOLOGY_STAGE_FINGERPRINT_MISMATCH",
            )

    @staticmethod
    def _prove_stage_binding(
        value: LegalWorkflowGateSatisfaction,
        stage: LegalWorkflowStage,
        topology: LegalWorkflowTopology,
    ) -> None:
        if (
            stage.stage_definition_id != value.source_stage_definition_id
            or not hmac.compare_digest(stage.fingerprint, value.source_stage_fingerprint)
            or stage.workflow_definition_id != topology.workflow_definition_id
            or stage.definition_revision != topology.definition_revision
            or not hmac.compare_digest(
                stage.workflow_definition_fingerprint,
                topology.workflow_definition_fingerprint,
            )
        ):
            _raise(
                LegalWorkflowGateSatisfactionRegistryConflictError,
                "P12B_DURABLE_STAGE_BINDING_MISMATCH",
            )
        if value.gate_reference not in stage.completion_gate_references:
            _raise(
                LegalWorkflowGateSatisfactionRegistryConflictError,
                "P12B_GATE_NOT_CONFIGURED_ON_DURABLE_STAGE",
            )

    def _reprove(
        self,
        value: LegalWorkflowGateSatisfaction,
        *,
        session: object,
    ) -> None:
        instance = self._instance_registry.get_by_id(
            value.tenant_id,
            value.workflow_instance_id,
            session=session,
        )
        self._prove_instance_binding(value, instance)
        topology = self._topology_registry.get_by_fingerprint(
            value.workflow_topology_fingerprint,
            session=session,
        )
        self._prove_topology_binding(value, topology)
        stage = self._stage_registry.get_by_fingerprint(
            value.source_stage_fingerprint,
            session=session,
        )
        self._prove_stage_binding(value, stage, topology)

    def get_by_id(
        self,
        tenant_id: str,
        gate_satisfaction_id: str,
        *,
        session: object,
    ) -> LegalWorkflowGateSatisfaction:
        """Read one tenant-scoped fact and re-prove all durable authorities."""
        tenant = _tenant(tenant_id)
        satisfaction_id = _text("gate_satisfaction_id", gate_satisfaction_id)
        tx = _transaction(session)
        try:
            raw = self._collection.find_one(
                {
                    "tenant_id": tenant,
                    "gate_satisfaction_id": satisfaction_id,
                },
                session=tx,
            )
        except (AttributeError, TypeError) as error:
            _raise(
                LegalWorkflowGateSatisfactionRegistryPersistenceError,
                "P12B_PERSISTENCE_UNAVAILABLE",
                error,
            )
        except PyMongoError as error:
            _mongo_failure(error)
        if raw is None:
            _raise(
                LegalWorkflowGateSatisfactionRegistryNotFoundError,
                "P12B_GATE_SATISFACTION_NOT_FOUND",
            )
        value = _hydrate(raw)
        if value.tenant_id != tenant or value.gate_satisfaction_id != satisfaction_id:
            _raise(
                LegalWorkflowGateSatisfactionRegistryPersistedRecordInvalidError,
                "P12B_PERSISTED_SCOPE_MISMATCH",
            )
        self._reprove(value, session=tx)
        return value

    def create_or_replay(
        self,
        value: LegalWorkflowGateSatisfaction,
        *,
        session: object,
    ) -> LegalWorkflowGateSatisfaction:
        """Persist one exact fact or return an exact, re-proven durable replay."""
        tx = _transaction(session)
        if not isinstance(value, LegalWorkflowGateSatisfaction):
            _raise(
                LegalWorkflowGateSatisfactionRegistryInputError,
                "P12B_DOMAIN_VALUE_REQUIRED",
            )
        self._reprove(value, session=tx)
        identity = {
            "tenant_id": value.tenant_id,
            "gate_satisfaction_id": value.gate_satisfaction_id,
        }
        try:
            existing_raw = self._collection.find_one(identity, session=tx)
            if existing_raw is not None:
                existing = _hydrate(existing_raw)
                if not _equal(existing, value):
                    _raise(
                        LegalWorkflowGateSatisfactionRegistryConflictError,
                        "P12B_DIVERGENT_REPLAY",
                    )
                self._reprove(existing, session=tx)
                return existing
            collision_raw = self._collection.find_one(
                {"tenant_id": value.tenant_id, "fingerprint": value.fingerprint},
                session=tx,
            )
            if collision_raw is not None:
                collision = _hydrate(collision_raw)
                if not _equal(collision, value):
                    _raise(
                        LegalWorkflowGateSatisfactionRegistryConflictError,
                        "P12B_FINGERPRINT_COLLISION",
                    )
            self._collection.insert_one(value.to_dict(), session=tx)
        except DuplicateKeyError as error:
            _raise(
                LegalWorkflowGateSatisfactionRegistryRetryTransactionError,
                "P12B_WHOLE_TRANSACTION_RETRY_REQUIRED",
                error,
            )
        except LegalWorkflowGateSatisfactionRegistryError:
            raise
        except (AttributeError, TypeError) as error:
            _raise(
                LegalWorkflowGateSatisfactionRegistryPersistenceError,
                "P12B_PERSISTENCE_UNAVAILABLE",
                error,
            )
        except PyMongoError as error:
            _mongo_failure(error)
        return self.get_by_id(
            value.tenant_id,
            value.gate_satisfaction_id,
            session=tx,
        )


def ensure_indexes(
    collection: Any,
    *,
    instance_registry: LegalMatterWorkflowInstanceRegistry,
    topology_registry: LegalWorkflowTopologyRegistry,
    stage_registry: LegalWorkflowStageRegistry,
) -> None:
    """Create governed indexes for one explicitly composed collection."""
    LegalWorkflowGateSatisfactionRegistry(
        collection,
        instance_registry=instance_registry,
        topology_registry=topology_registry,
        stage_registry=stage_registry,
    ).ensure_indexes()


__all__ = [
    "COLLECTION_NAME",
    "FINGERPRINT_INDEX_NAME",
    "IDENTITY_INDEX_NAME",
    "INSTANCE_HISTORY_INDEX_NAME",
    "VERSION",
    "LegalWorkflowGateSatisfactionRegistry",
    "LegalWorkflowGateSatisfactionRegistryConflictError",
    "LegalWorkflowGateSatisfactionRegistryError",
    "LegalWorkflowGateSatisfactionRegistryInputError",
    "LegalWorkflowGateSatisfactionRegistryNotFoundError",
    "LegalWorkflowGateSatisfactionRegistryPersistedRecordInvalidError",
    "LegalWorkflowGateSatisfactionRegistryPersistenceError",
    "LegalWorkflowGateSatisfactionRegistryRetryTransactionError",
    "LegalWorkflowGateSatisfactionRegistryTransactionRequiredError",
    "ensure_indexes",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: legal_workflow_gate_satisfaction_registry.py
# VERSION: v1.0.0-P12B-LEGAL-WORKFLOW-GATE-SATISFACTION-REGISTRY
# AUTHORITY BOUNDARY: immutable positive gate-satisfaction persistence only
# TENANT POSTURE: exact tenant-scoped identity and reads
# INSTANCE / TOPOLOGY / STAGE RE-PROOF: REQUIRED
# CANONICAL EVIDENCE DEREFERENCE AUTHORITY: NONE
# FAIL-CLOSED POSTURE: corrupt, divergent, and drifted bindings reject
# CALLER-OWNED ACTIVE TRANSACTION REQUIRED: YES
# MUTABLE CURRENT POINTER / SUPERSESSION: NONE
# TTL / UPDATE / REPLACE / DELETE AUTHORITY: NONE
# TRANSITION / IAM / PROFESSIONAL / COMMERCIAL AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
