"""TITLE: WILSY OS Legal Workflow Registries Real-Mongo Certificate.

VERSION: v1.0.0-G7G-P0-LEGAL-WORKFLOW-REGISTRIES-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations.
EPITOME: Physically certify immutable activation, workflow-instance,
         transition, and work-item persistence on a writable Mongo replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_workflow_registries_real_mongo.py
COLLABORATION / OWNERSHIP: The four G7G registries are production subjects;
                            this certificate owns UUID-isolated synthetic data.
CERTIFICATION / UPDATE DATE: 2026-10-15
CHANGELOG: v1.0.0-G7G-P0 establishes the combined sanctioned certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identities; no customer data.
TENANT BOUNDARY: Every operational assertion uses exact tenant predicates.
AUTHORITY BOUNDARY: Persistence proof grants no IAM, transition, assignment,
                    supervision, completion, or Legal-event authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Tests own start, commit, abort, and whole retry.
FAIL-CLOSED DECLARATION: Topology, index, corruption, replay, isolation,
                         rollback, or restart failure fails certification.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tests.unit.test_legal_matter_workflow_instance_registry import instance
from tests.unit.test_legal_matter_workflow_transition import context, transition
from tests.unit.test_legal_matter_workflow_transition_registry import second
from tests.unit.test_legal_work_item import item
from tests.unit.test_tenant_legal_workflow_activation_registry import activation
from tools.eos.legal_operations.domain.legal_work_item import LegalWorkItemStatus
from tools.eos.legal_operations.registry import legal_matter_workflow_instance_registry as instances
from tools.eos.legal_operations.registry import legal_matter_workflow_transition_registry as transitions
from tools.eos.legal_operations.registry import legal_work_item_registry as work_items
from tools.eos.legal_operations.registry import tenant_legal_workflow_activation_registry as activations


MONGO_URI = os.getenv(
    "TEST_LEGAL_WORKFLOW_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyLegalWorkflowCertRS",
)
EXPECTED_REPLICA_SET = os.getenv(
    "TEST_LEGAL_WORKFLOW_MONGO_REPLICA_SET",
    "wilsyLegalWorkflowCertRS",
)


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, dict[str, Any]]]:
    """Yield one disposable database after strict replica-set preflight."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    hello: dict[str, Any] = {}
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(f"G7G_P0_MONGO_UNAVAILABLE:{type(error).__name__}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail("G7G_P0_WRONG_REPLICA_SET")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("G7G_P0_NO_WRITABLE_PRIMARY")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.fail("G7G_P0_LOGICAL_SESSIONS_UNAVAILABLE")

        database = client[f"wilsy_g7g_p0_workflow_{uuid.uuid4().hex}"]
        options = {
            "write_concern": WriteConcern(w="majority", j=True),
            "read_concern": ReadConcern("majority"),
        }
        collections = {
            "activations": database.get_collection(activations.COLLECTION_NAME, **options),
            "instances": database.get_collection(instances.COLLECTION_NAME, **options),
            "transitions": database.get_collection(transitions.COLLECTION_NAME, **options),
            "work_items": database.get_collection(work_items.COLLECTION_NAME, **options),
        }
        activations.TenantLegalWorkflowActivationRegistry(collections["activations"]).ensure_indexes()
        instances.LegalMatterWorkflowInstanceRegistry(collections["instances"]).ensure_indexes()
        transitions.LegalMatterWorkflowTransitionRegistry(collections["transitions"]).ensure_indexes()
        work_items.LegalWorkItemRegistry(collections["work_items"]).ensure_indexes()
        yield client, database, collections
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def commit(client: MongoClient[Any], registry: Any, value: Any) -> Any:
    """Commit one registry call while preserving caller transaction ownership."""
    with client.start_session() as session:
        with session.start_transaction():
            return registry.create_or_replay(value, session=session)


def test_topology_and_exact_tenant_first_non_ttl_indexes(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Prove physical topology and each registry's exact index contract."""
    client, _database, collections = mongo_context
    hello = client.admin.command("hello")
    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    expected = {
        "activations": {
            activations.IDENTITY_INDEX_NAME,
            activations.FINGERPRINT_INDEX_NAME,
            activations.HISTORY_INDEX_NAME,
            activations.CURRENTNESS_INDEX_NAME,
        },
        "instances": {
            instances.IDENTITY_INDEX_NAME,
            instances.FINGERPRINT_INDEX_NAME,
            instances.MATTER_HISTORY_INDEX_NAME,
            instances.DEFINITION_HISTORY_INDEX_NAME,
        },
        "transitions": {
            transitions.IDENTITY_INDEX_NAME,
            transitions.FINGERPRINT_INDEX_NAME,
            transitions.SEQUENCE_INDEX_NAME,
            transitions.MATTER_HISTORY_INDEX_NAME,
        },
        "work_items": {
            work_items.IDENTITY_INDEX_NAME,
            work_items.FINGERPRINT_INDEX_NAME,
            work_items.MATTER_INDEX_NAME,
            work_items.STATUS_INDEX_NAME,
            work_items.SOURCE_INDEX_NAME,
        },
    }
    for name, collection in collections.items():
        indexes = {row["name"]: row for row in collection.list_indexes() if row["name"] != "_id_"}
        assert set(indexes) == expected[name]
        assert all(next(iter(dict(row["key"]))) == "tenant_id" for row in indexes.values())
        assert all("expireAfterSeconds" not in row for row in indexes.values())


def test_commit_replay_abort_and_restart_readback_across_all_registries(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Prove durable exact replay, rollback, and new-client readback."""
    client, database, collections = mongo_context
    values_and_registries = (
        (activation(), activations.TenantLegalWorkflowActivationRegistry(collections["activations"])),
        (instance(), instances.LegalMatterWorkflowInstanceRegistry(collections["instances"])),
        (transition(), transitions.LegalMatterWorkflowTransitionRegistry(collections["transitions"])),
        (item(), work_items.LegalWorkItemRegistry(collections["work_items"])),
    )
    for value, target in values_and_registries:
        assert commit(client, target, value) == value
        assert commit(client, target, value) == value

    aborted = item(work_item_id="work-aborted")
    with client.start_session() as session:
        session.start_transaction()
        work_items.LegalWorkItemRegistry(collections["work_items"]).create_or_replay(aborted, session=session)
        assert session.in_transaction is True
        session.abort_transaction()
    assert collections["work_items"].count_documents({"work_item_id": "work-aborted"}) == 0

    fresh: MongoClient[Any] = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, tz_aware=True)
    try:
        fresh_collection = fresh[database.name][work_items.COLLECTION_NAME]
        with fresh.start_session() as session:
            with session.start_transaction():
                assert work_items.LegalWorkItemRegistry(fresh_collection).get_by_id(
                    "tenant-1", "work-1", session=session
                ) == item()
    finally:
        fresh.close()


def test_activation_lineage_currentness_and_tenant_non_disclosure(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Prove immutable lineage, derived currentness, and exact tenant absence."""
    client, _database, collections = mongo_context
    target = activations.TenantLegalWorkflowActivationRegistry(collections["activations"])
    first = activation()
    follow = activation(
        activation_id="activation-2",
        revision=2,
        effective_hour=10,
        supersedes=first.activation_id,
    )
    commit(client, target, first)
    commit(client, target, follow)
    with client.start_session() as session:
        with session.start_transaction():
            assert target.resolve_current(
                first.tenant_id,
                first.workflow_definition_id,
                datetime(2026, 10, 15, 9, 30, tzinfo=timezone.utc),
                session=session,
            ) == first
            assert target.resolve_current(
                first.tenant_id,
                first.workflow_definition_id,
                datetime(2026, 10, 15, 10, 0, tzinfo=timezone.utc),
                session=session,
            ) == follow
            with pytest.raises(activations.TenantLegalWorkflowActivationRegistryNotFoundError):
                target.get_by_id("foreign-tenant", first.activation_id, session=session)


def test_transition_history_currentness_and_work_queue_queries(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
) -> None:
    """Prove complete transition derivation and tenant-scoped queue reads."""
    client, _database, collections = mongo_context
    transition_registry = transitions.LegalMatterWorkflowTransitionRegistry(collections["transitions"])
    first = transition()
    follow = second(first)
    commit(client, transition_registry, first)
    commit(client, transition_registry, follow)
    workflow_instance, *_ = context()
    open_item = item()
    closed_item = item(
        work_item_id="work-2",
        status=LegalWorkItemStatus.COMPLETED,
        completed_at=item().created_at,
        completion_evidence_reference="completion-2",
        completion_evidence_fingerprint="b" * 128,
    )
    work_registry = work_items.LegalWorkItemRegistry(collections["work_items"])
    commit(client, work_registry, open_item)
    commit(client, work_registry, closed_item)
    with client.start_session() as session:
        with session.start_transaction():
            current = transition_registry.derive_currentness(
                "current-1", workflow_instance, session=session
            )
            assert current.transition_count == 2
            assert current.head_transition_id == follow.transition_id
            assert work_registry.list_matter(
                open_item.tenant_id, open_item.case_matter_id, session=session
            ) == (open_item, closed_item)
            assert work_registry.list_status(
                open_item.tenant_id, LegalWorkItemStatus.OPEN, session=session
            ) == (open_item,)
            assert work_registry.list_status(
                "foreign-tenant", LegalWorkItemStatus.OPEN, session=session
            ) == ()


@pytest.mark.parametrize(
    ("collection_name", "registry_factory", "query", "read"),
    (
        (
            "activations",
            activations.TenantLegalWorkflowActivationRegistry,
            {"tenant_id": "tenant-a", "activation_id": "activation-1"},
            lambda target, session: target.get_by_id("tenant-a", "activation-1", session=session),
        ),
        (
            "instances",
            instances.LegalMatterWorkflowInstanceRegistry,
            {"tenant_id": instance().tenant_id, "workflow_instance_id": "instance-1"},
            lambda target, session: target.get_by_id(instance().tenant_id, "instance-1", session=session),
        ),
        (
            "transitions",
            transitions.LegalMatterWorkflowTransitionRegistry,
            {"tenant_id": transition().tenant_id, "transition_id": transition().transition_id},
            lambda target, session: target.list_history(transition().tenant_id, transition().workflow_instance_id, session=session),
        ),
        (
            "work_items",
            work_items.LegalWorkItemRegistry,
            {"tenant_id": "tenant-1", "work_item_id": "work-1"},
            lambda target, session: target.get_by_id("tenant-1", "work-1", session=session),
        ),
    ),
)
def test_persisted_corruption_rejects_fail_closed(
    mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]],
    collection_name: str,
    registry_factory: Any,
    query: dict[str, str],
    read: Any,
) -> None:
    """Prove strict hydration rejects a fingerprint-corrupt durable row."""
    client, _database, collections = mongo_context
    values = {
        "activations": activation(),
        "instances": instance(),
        "transitions": transition(),
        "work_items": item(),
    }
    target = registry_factory(collections[collection_name])
    commit(client, target, values[collection_name])
    original = deepcopy(collections[collection_name].find_one(query))
    assert isinstance(original, dict)
    collections[collection_name].update_one(query, {"$set": {"fingerprint": "0" * 128}})
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(RuntimeError):
                read(target, session)


# ARTIFACT: test_legal_workflow_registries_real_mongo.py
# VERSION: v1.0.0-G7G-P0-LEGAL-WORKFLOW-REGISTRIES-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical persistence verification only; no runtime authority
# TENANT POSTURE: exact tenant-first writes, reads, history, and non-disclosure
# FAIL-CLOSED POSTURE: topology, indexes, replay, rollback, corruption, and restart required
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
