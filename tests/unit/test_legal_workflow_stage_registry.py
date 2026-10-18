"""Direct certificate for P11B Legal Workflow Stage Registry."""

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
from tests.unit.test_legal_workflow_topology_registry import (
    make_topology,
)
from tools.eos.legal_operations.domain.legal_workflow_definition import (
    LegalWorkflowDefinition,
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
from tools.eos.legal_operations.registry.legal_workflow_stage_registry import (
    COLLECTION_NAME,
    DEFINITION_LOOKUP_INDEX_NAME,
    FINGERPRINT_INDEX_NAME,
    IDENTITY_INDEX_NAME,
    VERSION,
    LegalWorkflowStageRegistry,
    LegalWorkflowStageRegistryConflictError,
    LegalWorkflowStageRegistryNotFoundError,
    LegalWorkflowStageRegistryPersistedRecordInvalidError,
    LegalWorkflowStageRegistryRetryTransactionError,
    LegalWorkflowStageRegistryTransactionRequiredError,
)
from tools.eos.legal_operations.registry.legal_workflow_topology_registry import (
    LegalWorkflowTopologyRegistry,
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


class FakeTopologyRegistry:
    def __init__(
        self,
        durable: LegalWorkflowTopology,
    ) -> None:
        self.durable = durable
        self.calls: list[str] = []

    def get_by_definition_fingerprint(
        self,
        workflow_definition_fingerprint,
        *,
        session,
    ) -> LegalWorkflowTopology:
        assert session.in_transaction is True

        self.calls.append(
            workflow_definition_fingerprint
        )

        if (
            workflow_definition_fingerprint
            != self.durable.workflow_definition_fingerprint
        ):
            raise RuntimeError(
                "topology not found"
            )

        return self.durable


def stage_value(
    durable: LegalWorkflowDefinition,
    *,
    stage_definition_id: str = "s1",
    is_entry_stage: bool = True,
    is_terminal_stage: bool = False,
    successor_stage_ids: tuple[str, ...] = ("s2",),
) -> LegalWorkflowStage:
    return stage(
        durable,
        stage_definition_id=
            stage_definition_id,
        is_entry_stage=
            is_entry_stage,
        is_terminal_stage=
            is_terminal_stage,
        successor_stage_ids=
            successor_stage_ids,
    )


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
    topology = make_topology(
        durable
    )
    value = stage_value(
        durable
    )

    collection = FakeCollection()
    definitions = FakeDefinitionRegistry(
        durable
    )
    topologies = FakeTopologyRegistry(
        topology
    )

    registry = object.__new__(
        LegalWorkflowStageRegistry
    )
    registry._collection = collection
    registry._definition_registry = cast(
        LegalWorkflowDefinitionRegistry,
        definitions,
    )
    registry._topology_registry = cast(
        LegalWorkflowTopologyRegistry,
        topologies,
    )

    session = FakeSession(
        in_transaction=True
    )

    return (
        durable,
        topology,
        value,
        collection,
        definitions,
        topologies,
        registry,
        session,
    )


def test_identity_is_exact() -> None:
    assert (
        VERSION
        == "v1.0.0-P11B-LEGAL-WORKFLOW-STAGE-REGISTRY"
    )
    assert (
        COLLECTION_NAME
        == "legal_workflow_stages"
    )


def test_indexes_are_exact_and_non_ttl() -> None:
    (
        _,
        _,
        _,
        collection,
        _,
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
        IDENTITY_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        DEFINITION_LOOKUP_INDEX_NAME,
    }

    assert (
        indexes[
            IDENTITY_INDEX_NAME
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
        _,
        value,
        _,
        _,
        _,
        registry,
        _,
    ) = context()

    with pytest.raises(
        LegalWorkflowStageRegistryTransactionRequiredError,
        match="P11B_ACTIVE_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(
            value,
            owner="PLATFORM",
            owner_tenant_id=None,
            session=FakeSession(
                in_transaction=False
            ),
        )


def test_create_replay_reproves_definition_and_topology() -> None:
    (
        durable,
        _,
        value,
        collection,
        definitions,
        topologies,
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

    assert len(topologies.calls) >= 2
    assert all(
        item == durable.fingerprint
        for item in topologies.calls
    )


def test_tenant_scope_resolves_definition_but_is_not_persisted() -> None:
    (
        durable,
        _,
        value,
        collection,
        definitions,
        _,
        registry,
        session,
    ) = context(
        owner="TENANT",
        owner_tenant_id="tenant-stage-1",
    )

    created = registry.create_or_replay(
        value,
        owner="TENANT",
        owner_tenant_id="tenant-stage-1",
        session=session,
    )

    assert created == value

    assert definitions.calls == [
        (
            "TENANT",
            "tenant-stage-1",
            durable.workflow_definition_id,
            durable.definition_revision,
        )
    ]

    persisted = collection.rows[0]
    assert "owner" not in persisted
    assert "owner_tenant_id" not in persisted
    assert "tenant_id" not in persisted
    assert (
        "workflow_topology_fingerprint"
        not in persisted
    )


def test_durable_definition_binding_mismatch_rejects() -> None:
    (
        _,
        topology,
        value,
        collection,
        _,
        topologies,
        registry,
        session,
    ) = context()

    other = definition(
        workflow_definition_id=
            "workflow-other",
    )

    registry._definition_registry = cast(
        LegalWorkflowDefinitionRegistry,
        FakeDefinitionRegistry(
            other,
            enforce_lookup_identity=False,
        ),
    )

    registry._topology_registry = cast(
        LegalWorkflowTopologyRegistry,
        topologies,
    )

    with pytest.raises(
        LegalWorkflowStageRegistryConflictError,
        match=(
            "P11B_DURABLE_DEFINITION_BINDING_MISMATCH"
        ),
    ):
        registry.create_or_replay(
            value,
            owner="PLATFORM",
            owner_tenant_id=None,
            session=session,
        )

    assert topology is not None
    assert collection.rows == []


def test_stage_not_in_durable_topology_rejects() -> None:
    (
        _,
        _,
        _,
        collection,
        _,
        _,
        registry,
        session,
    ) = context()

    durable = definition()
    outsider = stage_value(
        durable,
        stage_definition_id="outside",
        is_entry_stage=False,
        is_terminal_stage=True,
        successor_stage_ids=(),
    )

    with pytest.raises(
        LegalWorkflowStageRegistryConflictError,
        match="P11B_STAGE_NOT_IN_DURABLE_TOPOLOGY",
    ):
        registry.create_or_replay(
            outsider,
            owner="PLATFORM",
            owner_tenant_id=None,
            session=session,
        )

    assert collection.rows == []


def test_stage_fingerprint_mismatch_rejects() -> None:
    (
        durable,
        _,
        _,
        collection,
        _,
        _,
        registry,
        session,
    ) = context()

    changed = stage_value(
        durable,
        stage_definition_id="s1",
        is_entry_stage=True,
        is_terminal_stage=False,
        successor_stage_ids=("s3",),
    )

    with pytest.raises(
        LegalWorkflowStageRegistryConflictError,
        match="P11B_STAGE_FINGERPRINT_MISMATCH",
    ):
        registry.create_or_replay(
            changed,
            owner="PLATFORM",
            owner_tenant_id=None,
            session=session,
        )

    assert collection.rows == []


def test_exact_reads_reprove_topology_membership() -> None:
    (
        _,
        _,
        value,
        _,
        _,
        topologies,
        registry,
        session,
    ) = context()

    registry.create_or_replay(
        value,
        owner="PLATFORM",
        owner_tenant_id=None,
        session=session,
    )

    before = len(
        topologies.calls
    )

    assert (
        registry.get_by_definition_stage(
            value.workflow_definition_fingerprint,
            value.stage_definition_id,
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

    assert len(
        topologies.calls
    ) >= before + 2


def test_missing_stage_rejects() -> None:
    (
        _,
        _,
        value,
        _,
        _,
        _,
        registry,
        session,
    ) = context()

    with pytest.raises(
        LegalWorkflowStageRegistryNotFoundError,
        match="P11B_STAGE_NOT_FOUND",
    ):
        registry.get_by_definition_stage(
            value.workflow_definition_fingerprint,
            "missing-stage",
            session=session,
        )


def test_corrupt_persisted_stage_rejects() -> None:
    (
        _,
        _,
        value,
        collection,
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

    collection.rows[0][
        "fingerprint"
    ] = "f" * 128

    with pytest.raises(
        LegalWorkflowStageRegistryPersistedRecordInvalidError,
        match="P11B_PERSISTED_RECORD_INVALID",
    ):
        registry.get_by_definition_stage(
            value.workflow_definition_fingerprint,
            value.stage_definition_id,
            session=session,
        )


def test_duplicate_race_requires_whole_transaction_retry() -> None:
    (
        _,
        _,
        value,
        collection,
        _,
        _,
        registry,
        session,
    ) = context()

    collection.duplicate_on_insert = True

    with pytest.raises(
        LegalWorkflowStageRegistryRetryTransactionError,
        match="P11B_WHOLE_TRANSACTION_RETRY_REQUIRED",
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
# ARTIFACT: test_legal_workflow_stage_registry.py
# VERSION: v1.0.0-P11B-LEGAL-WORKFLOW-STAGE-REGISTRY-CERT
# DEFINITION AUTHORITY REPROVED: YES
# DURABLE TOPOLOGY MEMBERSHIP REPROVED: YES
# STAGE OWNER / TENANT FIELD INVENTED: NO
# STAGE TOPOLOGY FIELD INVENTED: NO
# EXACT REPLAY / BINDING / CORRUPTION / RACE: CERTIFIED
# ACTIVE CALLER TRANSACTION REQUIRED: YES
# MONGO CONTACT: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
