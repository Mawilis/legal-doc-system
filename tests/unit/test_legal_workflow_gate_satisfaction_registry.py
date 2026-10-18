"""
WILSY OS — P12B Legal Workflow Gate Satisfaction Registry Unit Certificate

VERSION: v1.0.0-P12B-LEGAL-WORKFLOW-GATE-SATISFACTION-REGISTRY-UNIT
AUTHORITY: Wilsy OS Core Governance / Legal Operations.
EPITOME: Certify immutable replay, transaction, tenant, index, hydration, and
durable workflow-authority re-proof semantics without claiming Mongo truth.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/
    test_legal_workflow_gate_satisfaction_registry.py
CERTIFICATION DATE: 2026-10-16
CHANGELOG: v1.0.0-P12B — Initial deterministic unit certificate.
COMPLIANCE: POPIA section 19 / GDPR Article 32 / SOC 2 CC7.2.
TENANT BOUNDARY: Every identity read is tenant-scoped.
AUTHORITY BOUNDARY: Tests persistence composition, not transition authority.
FINANCIAL AUTHORITY BOUNDARY: NONE.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tests.unit.test_legal_workflow_gate_satisfaction import (
    authorities,
    evidence,
    satisfaction,
)
from tools.eos.legal_operations.registry.legal_matter_workflow_instance_registry import (
    LegalMatterWorkflowInstanceRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_gate_satisfaction_registry import (
    FINGERPRINT_INDEX_NAME,
    IDENTITY_INDEX_NAME,
    INSTANCE_HISTORY_INDEX_NAME,
    LegalWorkflowGateSatisfactionRegistry,
    LegalWorkflowGateSatisfactionRegistryConflictError,
    LegalWorkflowGateSatisfactionRegistryNotFoundError,
    LegalWorkflowGateSatisfactionRegistryPersistedRecordInvalidError,
    LegalWorkflowGateSatisfactionRegistryRetryTransactionError,
    LegalWorkflowGateSatisfactionRegistryTransactionRequiredError,
)
from tools.eos.legal_operations.registry.legal_workflow_stage_registry import (
    LegalWorkflowStageRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_topology_registry import (
    LegalWorkflowTopologyRegistry,
)


VERSION = "v1.0.0-P12B-LEGAL-WORKFLOW-GATE-SATISFACTION-REGISTRY-UNIT"


class Session:
    """Minimal caller-owned transaction signal for deterministic unit tests."""

    in_transaction = True


class Collection:
    """Exact in-memory collection surface used by the registry."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, object]]] = []
        self.duplicate = False

    def create_index(self, keys, **options):
        self.indexes.append((list(keys), dict(options)))
        return options["name"]

    def find_one(self, query, *, session):
        assert session.in_transaction is True
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return deepcopy(row)
        return None

    def insert_one(self, document, *, session):
        assert session.in_transaction is True
        if self.duplicate:
            raise DuplicateKeyError("synthetic duplicate race")
        self.rows.append(deepcopy(document))
        return object()


class InstanceRegistry(LegalMatterWorkflowInstanceRegistry):
    """Type-valid authority double returning one immutable instance."""

    def __init__(self, value) -> None:
        self.value = value

    def get_by_id(self, tenant_id, workflow_instance_id, *, session):
        assert getattr(session, "in_transaction", False) is True
        return self.value


class TopologyRegistry(LegalWorkflowTopologyRegistry):
    """Type-valid authority double returning one immutable topology."""

    def __init__(self, value) -> None:
        self.value = value

    def get_by_fingerprint(self, topology_fingerprint, *, session):
        assert getattr(session, "in_transaction", False) is True
        return self.value


class StageRegistry(LegalWorkflowStageRegistry):
    """Type-valid authority double returning one immutable source stage."""

    def __init__(self, value) -> None:
        self.value = value

    def get_by_fingerprint(self, stage_fingerprint, *, session):
        assert getattr(session, "in_transaction", False) is True
        return self.value


def registry(collection: Collection | None = None):
    """Compose a registry with exact domain authorities."""
    instance, topology, stage = authorities()
    actual_collection = collection or Collection()
    return (
        LegalWorkflowGateSatisfactionRegistry(
            actual_collection,
            instance_registry=InstanceRegistry(instance),
            topology_registry=TopologyRegistry(topology),
            stage_registry=StageRegistry(stage),
        ),
        actual_collection,
    )


def test_indexes_are_exact_unique_and_non_ttl() -> None:
    subject, collection = registry()
    subject.ensure_indexes()
    by_name = {options["name"]: options for _, options in collection.indexes}
    assert by_name[IDENTITY_INDEX_NAME]["unique"] is True
    assert by_name[FINGERPRINT_INDEX_NAME]["unique"] is True
    assert by_name[INSTANCE_HISTORY_INDEX_NAME]["unique"] is False
    assert all("expireAfterSeconds" not in options for options in by_name.values())


def test_create_exact_replay_and_tenant_scoped_read() -> None:
    subject, collection = registry()
    value = satisfaction()
    created = subject.create_or_replay(value, session=Session())
    replayed = subject.create_or_replay(value, session=Session())
    read = subject.get_by_id(
        value.tenant_id, value.gate_satisfaction_id, session=Session()
    )
    assert created == value
    assert replayed == value
    assert read == value
    assert len(collection.rows) == 1


def test_active_transaction_is_mandatory() -> None:
    subject, _ = registry()
    with pytest.raises(
        LegalWorkflowGateSatisfactionRegistryTransactionRequiredError,
        match="P12B_ACTIVE_TRANSACTION_REQUIRED",
    ):
        subject.create_or_replay(satisfaction(), session=object())


def test_divergent_same_identity_replay_fails_closed() -> None:
    subject, _ = registry()
    subject.create_or_replay(satisfaction(), session=Session())
    divergent = satisfaction(
        canonical_evidence=(
            evidence(reference="conflict-currentness:changed", fingerprint="b" * 128),
        )
    )
    with pytest.raises(
        LegalWorkflowGateSatisfactionRegistryConflictError,
        match="P12B_DIVERGENT_REPLAY",
    ):
        subject.create_or_replay(divergent, session=Session())


def test_cross_tenant_lookup_is_ordinary_not_found() -> None:
    subject, _ = registry()
    subject.create_or_replay(satisfaction(), session=Session())
    with pytest.raises(
        LegalWorkflowGateSatisfactionRegistryNotFoundError,
        match="P12B_GATE_SATISFACTION_NOT_FOUND",
    ):
        subject.get_by_id("tenant-other", "gate-satisfaction-1", session=Session())


def test_corrupt_persisted_fingerprint_fails_closed() -> None:
    subject, collection = registry()
    subject.create_or_replay(satisfaction(), session=Session())
    collection.rows[0]["fingerprint"] = "f" * 128
    with pytest.raises(
        LegalWorkflowGateSatisfactionRegistryPersistedRecordInvalidError,
        match="P12B_PERSISTED_RECORD_INVALID",
    ):
        subject.get_by_id("tenant-1", "gate-satisfaction-1", session=Session())


def test_durable_instance_drift_fails_closed() -> None:
    value = satisfaction()
    _, topology, stage = authorities()
    wrong_instance, _, _ = authorities()
    object.__setattr__(wrong_instance, "case_matter_id", "matter-drifted")
    subject = LegalWorkflowGateSatisfactionRegistry(
        Collection(),
        instance_registry=InstanceRegistry(wrong_instance),
        topology_registry=TopologyRegistry(topology),
        stage_registry=StageRegistry(stage),
    )
    with pytest.raises(
        LegalWorkflowGateSatisfactionRegistryConflictError,
        match="P12B_DURABLE_INSTANCE_BINDING_MISMATCH",
    ):
        subject.create_or_replay(value, session=Session())


def test_durable_topology_drift_fails_closed() -> None:
    value = satisfaction()
    instance, topology, stage = authorities()
    object.__setattr__(topology, "fingerprint", "c" * 128)
    subject = LegalWorkflowGateSatisfactionRegistry(
        Collection(),
        instance_registry=InstanceRegistry(instance),
        topology_registry=TopologyRegistry(topology),
        stage_registry=StageRegistry(stage),
    )
    with pytest.raises(
        LegalWorkflowGateSatisfactionRegistryConflictError,
        match="P12B_DURABLE_TOPOLOGY_BINDING_MISMATCH",
    ):
        subject.create_or_replay(value, session=Session())


def test_durable_stage_drift_fails_closed() -> None:
    value = satisfaction()
    instance, topology, stage = authorities()
    object.__setattr__(stage, "completion_gate_references", ("gate:other",))
    subject = LegalWorkflowGateSatisfactionRegistry(
        Collection(),
        instance_registry=InstanceRegistry(instance),
        topology_registry=TopologyRegistry(topology),
        stage_registry=StageRegistry(stage),
    )
    with pytest.raises(
        LegalWorkflowGateSatisfactionRegistryConflictError,
        match="P12B_GATE_NOT_CONFIGURED_ON_DURABLE_STAGE",
    ):
        subject.create_or_replay(value, session=Session())


def test_embedded_canonical_evidence_is_preserved_without_invented_registry() -> None:
    subject, collection = registry()
    value = satisfaction()
    subject.create_or_replay(value, session=Session())
    assert collection.rows[0]["canonical_evidence"] == [
        item.to_dict() for item in value.canonical_evidence
    ]
    assert not hasattr(subject, "_canonical_evidence_registry")


def test_duplicate_insert_requires_whole_transaction_retry() -> None:
    collection = Collection()
    collection.duplicate = True
    subject, _ = registry(collection)
    with pytest.raises(
        LegalWorkflowGateSatisfactionRegistryRetryTransactionError,
        match="P12B_WHOLE_TRANSACTION_RETRY_REQUIRED",
    ):
        subject.create_or_replay(satisfaction(), session=Session())


# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: test_legal_workflow_gate_satisfaction_registry.py
# VERSION: v1.0.0-P12B-LEGAL-WORKFLOW-GATE-SATISFACTION-REGISTRY-UNIT
# TENANT POSTURE: exact tenant-scoped lookup certified
# FAIL-CLOSED POSTURE: replay, corruption, binding drift, and races certified
# REAL-MONGO AUTHORITY: NOT CLAIMED BY THIS UNIT ARTIFACT
# TRANSITION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
