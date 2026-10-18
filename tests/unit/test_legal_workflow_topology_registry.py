"""Direct certificate for P10B Legal Workflow Topology Registry."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, cast

import pytest

from tests.unit.test_legal_workflow_definition import (
    definition,
)
from tests.unit.test_legal_workflow_topology import (
    stage,
)
from tools.eos.legal_operations.domain.legal_workflow_definition import (
    LegalWorkflowDefinition,
)
from tools.eos.legal_operations.domain.legal_workflow_topology import (
    LegalWorkflowTopology,
)
from tools.eos.legal_operations.registry.legal_workflow_definition_registry import (
    LegalWorkflowDefinitionRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_topology_registry import (
    COLLECTION_NAME,
    DEFINITION_FINGERPRINT_INDEX_NAME,
    DEFINITION_LOOKUP_INDEX_NAME,
    FINGERPRINT_INDEX_NAME,
    VERSION,
    LegalWorkflowTopologyRegistry,
    LegalWorkflowTopologyRegistryConflictError,
    LegalWorkflowTopologyRegistryNotFoundError,
    LegalWorkflowTopologyRegistryPersistedRecordInvalidError,
    LegalWorkflowTopologyRegistryRetryTransactionError,
    LegalWorkflowTopologyRegistryTransactionRequiredError,
)


class FakeSession:
    def __init__(
        self,
        *,
        in_transaction: bool,
    ) -> None:
        self.in_transaction = (
            in_transaction
        )


class FakeCollection:
    def __init__(self) -> None:
        self.rows: list[
            dict[str, Any]
        ] = []
        self.indexes: list[
            tuple[
                tuple[tuple[str, int], ...],
                bool,
                str,
            ]
        ] = []
        self.duplicate_on_insert = False

    def create_index(
        self,
        keys,
        *,
        unique: bool = False,
        name: str,
    ) -> str:
        self.indexes.append(
            (
                tuple(keys),
                unique,
                name,
            )
        )
        return name

    def find_one(
        self,
        query,
        *,
        session,
    ):
        assert session.in_transaction is True

        for row in self.rows:
            if all(
                row.get(key) == value
                for key, value in query.items()
            ):
                return deepcopy(row)

        return None

    def insert_one(
        self,
        document,
        *,
        session,
    ) -> object:
        assert session.in_transaction is True

        if self.duplicate_on_insert:
            from pymongo.errors import (
                DuplicateKeyError,
            )

            raise DuplicateKeyError(
                "synthetic duplicate race"
            )

        self.rows.append(
            deepcopy(document)
        )
        return object()


def make_topology(
    workflow_definition: LegalWorkflowDefinition,
    *,
    variant: str = "linear",
) -> LegalWorkflowTopology:
    """Build valid topology truth through the existing certified stage helper."""

    if variant == "linear":
        stages = (
            stage(
                workflow_definition,
                stage_definition_id="s1",
                is_entry_stage=True,
                is_terminal_stage=False,
                successor_stage_ids=("s2",),
            ),
            stage(
                workflow_definition,
                stage_definition_id="s2",
                is_entry_stage=False,
                is_terminal_stage=False,
                successor_stage_ids=("s3",),
            ),
            stage(
                workflow_definition,
                stage_definition_id="s3",
                is_entry_stage=False,
                is_terminal_stage=True,
                successor_stage_ids=(),
            ),
        )
    elif variant == "short":
        stages = (
            stage(
                workflow_definition,
                stage_definition_id="s1",
                is_entry_stage=True,
                is_terminal_stage=False,
                successor_stage_ids=("s3",),
            ),
            stage(
                workflow_definition,
                stage_definition_id="s3",
                is_entry_stage=False,
                is_terminal_stage=True,
                successor_stage_ids=(),
            ),
        )
    else:
        raise AssertionError(
            f"UNKNOWN_TOPOLOGY_VARIANT:{variant}"
        )

    return LegalWorkflowTopology.from_definition_and_stages(
        workflow_definition=workflow_definition,
        stages=stages,
    )


class FakeDefinitionRegistry:
    def __init__(
        self,
        durable: LegalWorkflowDefinition,
        *,
        enforce_lookup_identity: bool = True,
    ) -> None:
        self.durable = durable
        self.enforce_lookup_identity = (
            enforce_lookup_identity
        )
        self.calls: list[
            tuple[
                object,
                object,
                str,
                int,
            ]
        ] = []

    def get_revision(
        self,
        owner,
        owner_tenant_id,
        workflow_definition_id,
        definition_revision,
        *,
        session,
    ) -> LegalWorkflowDefinition:
        assert session.in_transaction is True

        self.calls.append(
            (
                owner,
                owner_tenant_id,
                workflow_definition_id,
                definition_revision,
            )
        )

        if (
            self.enforce_lookup_identity
            and (
                workflow_definition_id
                != self.durable.workflow_definition_id
                or definition_revision
                != self.durable.definition_revision
            )
        ):
            raise RuntimeError(
                "definition not found"
            )

        return self.durable


def context(
    *,
    owner: str = "PLATFORM",
    owner_tenant_id: str | None = None,
):
    durable = definition(
        owner=owner,
        owner_tenant_id=
            owner_tenant_id,
    )

    value = make_topology(
        durable
    )

    collection = FakeCollection()
    definitions = FakeDefinitionRegistry(
        durable
    )

    # Constructor requires the production registry type. Bypass only for the
    # direct fake dependency while preserving the exact public behavior under
    # test; no production source is altered.
    registry = object.__new__(
        LegalWorkflowTopologyRegistry
    )
    registry._collection = collection
    registry._definition_registry = cast(
        LegalWorkflowDefinitionRegistry,
        definitions,
    )

    session = FakeSession(
        in_transaction=True
    )

    return (
        durable,
        value,
        collection,
        definitions,
        registry,
        session,
    )


def test_identity_is_exact() -> None:
    assert (
        VERSION
        == "v1.0.0-P10B-LEGAL-WORKFLOW-TOPOLOGY-REGISTRY"
    )
    assert (
        COLLECTION_NAME
        == "legal_workflow_topologies"
    )


def test_indexes_are_exact_and_non_ttl() -> None:
    (
        _,
        _,
        collection,
        _,
        registry,
        _,
    ) = context()

    registry.ensure_indexes()

    indexes = {
        item[2]: item
        for item in collection.indexes
    }

    assert set(indexes) == {
        DEFINITION_FINGERPRINT_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        DEFINITION_LOOKUP_INDEX_NAME,
    }

    assert (
        indexes[
            DEFINITION_FINGERPRINT_INDEX_NAME
        ][1]
        is True
    )
    assert (
        indexes[
            FINGERPRINT_INDEX_NAME
        ][1]
        is True
    )
    assert (
        indexes[
            DEFINITION_LOOKUP_INDEX_NAME
        ][1]
        is False
    )

    assert all(
        "expireAfterSeconds"
        not in repr(item)
        for item in collection.indexes
    )


def test_active_transaction_is_required() -> None:
    (
        _,
        value,
        _,
        _,
        registry,
        _,
    ) = context()

    with pytest.raises(
        LegalWorkflowTopologyRegistryTransactionRequiredError,
        match="P10B_ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(
            value,
            owner="PLATFORM",
            owner_tenant_id=None,
            session=FakeSession(
                in_transaction=False
            ),
        )


def test_create_replays_and_reproves_durable_definition() -> None:
    (
        durable,
        value,
        collection,
        definitions,
        registry,
        session,
    ) = context()

    created = registry.create_or_replay(
        value,
        owner="PLATFORM",
        owner_tenant_id=None,
        session=session,
    )
    replayed = registry.create_or_replay(
        value,
        owner="PLATFORM",
        owner_tenant_id=None,
        session=session,
    )

    assert created == value
    assert replayed == value
    assert len(collection.rows) == 1

    assert definitions.calls == [
        (
            "PLATFORM",
            None,
            durable.workflow_definition_id,
            durable.definition_revision,
        ),
        (
            "PLATFORM",
            None,
            durable.workflow_definition_id,
            durable.definition_revision,
        ),
    ]


def test_tenant_owner_scope_is_used_only_to_resolve_definition() -> None:
    (
        durable,
        value,
        collection,
        definitions,
        registry,
        session,
    ) = context(
        owner="TENANT",
        owner_tenant_id="tenant-1",
    )

    created = registry.create_or_replay(
        value,
        owner="TENANT",
        owner_tenant_id="tenant-1",
        session=session,
    )

    assert created == value

    assert definitions.calls == [
        (
            "TENANT",
            "tenant-1",
            durable.workflow_definition_id,
            durable.definition_revision,
        )
    ]

    persisted = collection.rows[0]

    assert "owner" not in persisted
    assert "owner_tenant_id" not in persisted
    assert "tenant_id" not in persisted


def test_definition_binding_mismatch_rejects() -> None:
    (
        _,
        value,
        collection,
        _,
        registry,
        session,
    ) = context()

    other_definition = definition(
        workflow_definition_id=
            "workflow-other",
    )

    registry._definition_registry = cast(
        LegalWorkflowDefinitionRegistry,
        FakeDefinitionRegistry(
            other_definition,
            enforce_lookup_identity=False,
        ),
    )

    with pytest.raises(
        LegalWorkflowTopologyRegistryConflictError,
        match="P10B_DURABLE_DEFINITION_BINDING_MISMATCH",
    ):
        registry.create_or_replay(
            value,
            owner="PLATFORM",
            owner_tenant_id=None,
            session=session,
        )

    assert collection.rows == []


def test_divergent_replay_rejects() -> None:
    (
        durable,
        value,
        _,
        _,
        registry,
        session,
    ) = context()

    registry.create_or_replay(
        value,
        owner="PLATFORM",
        owner_tenant_id=None,
        session=session,
    )

    payload = value.to_dict()
    payload["fingerprint"] = (
        "f" * 128
    )

    from tools.eos.legal_operations.domain.legal_workflow_topology import (
        LegalWorkflowTopology,
    )

    with pytest.raises(Exception):
        LegalWorkflowTopology.from_dict(
            payload
        )

    # Valid divergent topology for the same durable definition is constructed
    # through the certified domain composition path with different graph
    # semantics and the same durable definition fingerprint.
    divergent = make_topology(
        durable,
        variant="short",
    )

    assert divergent != value
    assert (
        divergent.workflow_definition_fingerprint
        == value.workflow_definition_fingerprint
    )

    with pytest.raises(
        LegalWorkflowTopologyRegistryConflictError,
        match="P10B_DIVERGENT_REPLAY",
    ):
        registry.create_or_replay(
            divergent,
            owner="PLATFORM",
            owner_tenant_id=None,
            session=session,
        )


def test_exact_reads_by_both_fingerprints() -> None:
    (
        _,
        value,
        _,
        _,
        registry,
        session,
    ) = context()

    registry.create_or_replay(
        value,
        owner="PLATFORM",
        owner_tenant_id=None,
        session=session,
    )

    assert (
        registry.get_by_definition_fingerprint(
            value.workflow_definition_fingerprint,
            session=session,
        )
        == value
    )

    assert (
        registry.get_by_fingerprint(
            value.fingerprint,
            session=session,
        )
        == value
    )


def test_missing_topology_rejects() -> None:
    (
        _,
        value,
        _,
        _,
        registry,
        session,
    ) = context()

    with pytest.raises(
        LegalWorkflowTopologyRegistryNotFoundError,
        match="P10B_TOPOLOGY_NOT_FOUND",
    ):
        registry.get_by_definition_fingerprint(
            value.workflow_definition_fingerprint,
            session=session,
        )


def test_corrupt_persisted_topology_rejects() -> None:
    (
        _,
        value,
        collection,
        _,
        registry,
        session,
    ) = context()

    registry.create_or_replay(
        value,
        owner="PLATFORM",
        owner_tenant_id=None,
        session=session,
    )

    collection.rows[0][
        "fingerprint"
    ] = "f" * 128

    with pytest.raises(
        LegalWorkflowTopologyRegistryPersistedRecordInvalidError,
        match="P10B_PERSISTED_RECORD_INVALID",
    ):
        registry.get_by_definition_fingerprint(
            value.workflow_definition_fingerprint,
            session=session,
        )


def test_duplicate_race_requires_whole_transaction_retry() -> None:
    (
        _,
        value,
        collection,
        _,
        registry,
        session,
    ) = context()

    collection.duplicate_on_insert = True

    with pytest.raises(
        LegalWorkflowTopologyRegistryRetryTransactionError,
        match="P10B_WHOLE_TRANSACTION_RETRY_REQUIRED",
    ):
        registry.create_or_replay(
            value,
            owner="PLATFORM",
            owner_tenant_id=None,
            session=session,
        )


# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: test_legal_workflow_topology_registry.py
# VERSION: v1.0.0-P10B-LEGAL-WORKFLOW-TOPOLOGY-REGISTRY-CERT
# DEFINITION AUTHORITY REPROVED: YES
# TOPOLOGY OWNER / TENANT FIELDS INVENTED: NO
# EXACT REPLAY / DIVERGENT REPLAY / CORRUPTION / RACE: CERTIFIED
# ACTIVE CALLER TRANSACTION REQUIRED: YES
# MONGO CONTACT: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
