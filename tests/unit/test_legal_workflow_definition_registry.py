"""Direct certificate for P9B Legal Workflow Definition Registry."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_operating_catalogue import (
    CATALOGUE_FINGERPRINT,
)
from tools.eos.legal_operations.domain.legal_workflow_definition import (
    LegalWorkflowDefinition,
)
from tools.eos.legal_operations.registry.legal_workflow_definition_registry import (
    COLLECTION_NAME,
    FINGERPRINT_INDEX_NAME,
    IDENTITY_INDEX_NAME,
    VERSION,
    LegalWorkflowDefinitionRegistry,
    LegalWorkflowDefinitionRegistryConflictError,
    LegalWorkflowDefinitionRegistryNotFoundError,
    LegalWorkflowDefinitionRegistryPersistedRecordInvalidError,
    LegalWorkflowDefinitionRegistryRetryTransactionError,
    LegalWorkflowDefinitionRegistryTransactionRequiredError,
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


class FakeCursor:
    def __init__(
        self,
        rows: list[dict[str, Any]],
    ) -> None:
        self._rows = rows

    def sort(
        self,
        field: str,
        _direction: int,
    ) -> "FakeCursor":
        self._rows.sort(
            key=lambda row: row[field]
        )
        return self

    def __iter__(self):
        return iter(
            deepcopy(self._rows)
        )


def _matches(
    row: dict[str, Any],
    query: dict[str, Any],
) -> bool:
    return all(
        row.get(key) == value
        for key, value in query.items()
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
            if _matches(
                row,
                query,
            ):
                return deepcopy(row)
        return None

    def find(
        self,
        query,
        *,
        session,
    ) -> FakeCursor:
        assert session.in_transaction is True
        return FakeCursor(
            [
                deepcopy(row)
                for row in self.rows
                if _matches(
                    row,
                    query,
                )
            ]
        )

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


def definition(
    *,
    workflow_definition_id: str = "workflow-litigation-core",
    definition_revision: int = 1,
    owner: str = "PLATFORM",
    owner_tenant_id: str | None = None,
    name: str = "Litigation Core",
) -> LegalWorkflowDefinition:
    return LegalWorkflowDefinition(
        workflow_definition_id=
            workflow_definition_id,
        definition_revision=
            definition_revision,
        owner=owner,
        owner_tenant_id=
            owner_tenant_id,
        name=name,
        description_reference=(
            "workflow-description:"
            + workflow_definition_id
            + ":"
            + str(definition_revision)
        ),
        required_operating_item_ids=(
            "PRACTICE_DISPUTES",
        ),
        jurisdiction_references=(),
        catalogue_fingerprint=
            CATALOGUE_FINGERPRINT,
    )


def registry():
    collection = FakeCollection()
    return (
        collection,
        LegalWorkflowDefinitionRegistry(
            collection
        ),
        FakeSession(
            in_transaction=True
        ),
    )


def test_identity_is_exact() -> None:
    assert (
        VERSION
        == "v1.0.0-P9B-LEGAL-WORKFLOW-DEFINITION-REGISTRY"
    )
    assert (
        COLLECTION_NAME
        == "legal_workflow_definitions"
    )


def test_indexes_are_exact_and_have_no_ttl() -> None:
    collection, value_registry, _ = registry()

    value_registry.ensure_indexes()

    names = {
        item[2]
        for item in collection.indexes
    }

    assert names == {
        IDENTITY_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
    }

    identity = next(
        item
        for item in collection.indexes
        if item[2]
        == IDENTITY_INDEX_NAME
    )
    fingerprint = next(
        item
        for item in collection.indexes
        if item[2]
        == FINGERPRINT_INDEX_NAME
    )

    assert identity[1] is True
    assert fingerprint[1] is True

    assert all(
        "expireAfterSeconds"
        not in repr(item)
        for item in collection.indexes
    )


def test_active_transaction_is_required() -> None:
    _, value_registry, _ = registry()

    with pytest.raises(
        LegalWorkflowDefinitionRegistryTransactionRequiredError,
        match="P9B_ACTIVE_TRANSACTION_REQUIRED",
    ):
        value_registry.create_or_replay(
            definition(),
            session=FakeSession(
                in_transaction=False
            ),
        )


def test_platform_definition_create_exact_replay_and_latest() -> None:
    collection, value_registry, session = registry()
    value_registry.ensure_indexes()

    first = definition()

    created = value_registry.create_or_replay(
        first,
        session=session,
    )
    replayed = value_registry.create_or_replay(
        first,
        session=session,
    )

    assert created == first
    assert replayed == first
    assert len(collection.rows) == 1

    assert (
        value_registry.resolve_latest(
            "PLATFORM",
            None,
            first.workflow_definition_id,
            session=session,
        )
        == first
    )


def test_tenant_scope_is_exact() -> None:
    _, value_registry, session = registry()

    tenant_value = definition(
        workflow_definition_id=
            "tenant-workflow-1",
        owner="TENANT",
        owner_tenant_id="tenant-1",
    )

    value_registry.create_or_replay(
        tenant_value,
        session=session,
    )

    assert (
        value_registry.get_revision(
            "TENANT",
            "tenant-1",
            "tenant-workflow-1",
            1,
            session=session,
        )
        == tenant_value
    )

    with pytest.raises(
        LegalWorkflowDefinitionRegistryNotFoundError,
        match="P9B_REVISION_NOT_FOUND",
    ):
        value_registry.get_revision(
            "TENANT",
            "tenant-2",
            "tenant-workflow-1",
            1,
            session=session,
        )


def test_platform_and_tenant_scopes_do_not_alias() -> None:
    _, value_registry, session = registry()

    platform = definition(
        workflow_definition_id="shared-id",
    )
    tenant = definition(
        workflow_definition_id="shared-id",
        owner="TENANT",
        owner_tenant_id="tenant-1",
        name="Tenant Shared ID",
    )

    value_registry.create_or_replay(
        platform,
        session=session,
    )
    value_registry.create_or_replay(
        tenant,
        session=session,
    )

    assert (
        value_registry.get_revision(
            "PLATFORM",
            None,
            "shared-id",
            1,
            session=session,
        )
        == platform
    )
    assert (
        value_registry.get_revision(
            "TENANT",
            "tenant-1",
            "shared-id",
            1,
            session=session,
        )
        == tenant
    )


def test_revision_history_is_contiguous_and_latest_is_derived() -> None:
    _, value_registry, session = registry()

    first = definition()
    second = definition(
        definition_revision=2,
        name="Litigation Core R2",
    )

    value_registry.create_or_replay(
        first,
        session=session,
    )
    value_registry.create_or_replay(
        second,
        session=session,
    )

    history = value_registry.get_history(
        "PLATFORM",
        None,
        first.workflow_definition_id,
        session=session,
    )

    assert history == (
        first,
        second,
    )

    assert (
        value_registry.resolve_latest(
            "PLATFORM",
            None,
            first.workflow_definition_id,
            session=session,
        )
        == second
    )


def test_revision_gap_rejects() -> None:
    _, value_registry, session = registry()

    with pytest.raises(
        LegalWorkflowDefinitionRegistryConflictError,
        match="P9B_REVISION_SEQUENCE_CONFLICT",
    ):
        value_registry.create_or_replay(
            definition(
                definition_revision=2,
            ),
            session=session,
        )


def test_divergent_replay_rejects() -> None:
    _, value_registry, session = registry()

    original = definition()
    divergent = definition(
        name="Different semantics",
    )

    value_registry.create_or_replay(
        original,
        session=session,
    )

    with pytest.raises(
        LegalWorkflowDefinitionRegistryConflictError,
        match="P9B_DIVERGENT_REPLAY",
    ):
        value_registry.create_or_replay(
            divergent,
            session=session,
        )


def test_corrupt_persisted_row_rejects() -> None:
    collection, value_registry, session = registry()

    value = definition()
    value_registry.create_or_replay(
        value,
        session=session,
    )

    collection.rows[0][
        "fingerprint"
    ] = "f" * 128

    with pytest.raises(
        LegalWorkflowDefinitionRegistryPersistedRecordInvalidError,
        match="P9B_PERSISTED_RECORD_INVALID",
    ):
        value_registry.get_revision(
            "PLATFORM",
            None,
            value.workflow_definition_id,
            1,
            session=session,
        )


def test_corrupt_persisted_revision_gap_rejects() -> None:
    collection, value_registry, session = registry()

    second = definition(
        definition_revision=2,
        name="Litigation Core R2",
    )

    # Persist one internally valid revision-2 domain snapshot while revision 1
    # is absent. Hydration must succeed first so the registry, rather than the
    # domain fingerprint validator, adjudicates the durable history gap.
    collection.rows.append(
        second.to_dict()
    )

    with pytest.raises(
        LegalWorkflowDefinitionRegistryPersistedRecordInvalidError,
        match="P9B_PERSISTED_REVISION_GAP",
    ):
        value_registry.get_history(
            "PLATFORM",
            None,
            second.workflow_definition_id,
            session=session,
        )


def test_duplicate_race_requires_whole_transaction_retry() -> None:
    collection, value_registry, session = registry()

    collection.duplicate_on_insert = True

    with pytest.raises(
        LegalWorkflowDefinitionRegistryRetryTransactionError,
        match="P9B_WHOLE_TRANSACTION_RETRY_REQUIRED",
    ):
        value_registry.create_or_replay(
            definition(),
            session=session,
        )


# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: test_legal_workflow_definition_registry.py
# VERSION: v1.0.0-P9B-LEGAL-WORKFLOW-DEFINITION-REGISTRY-CERT
# DIRECT FAKE-COLLECTION CERTIFICATE: YES
# ACTIVE TRANSACTION REQUIRED: YES
# PLATFORM / TENANT OWNER ISOLATION: YES
# EXACT REPLAY / REVISION HISTORY / CORRUPTION / RACE: CERTIFIED
# MONGO CONTACT: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
