"""TITLE: WILSY OS G78 Canonical Source Adapters Real-Mongo Certificate.
VERSION: v1.0.0-G78-SOURCE-ADAPTERS-REAL-MONGO-CERT
AUTHORITY: Disposable transaction-bound source-read evidence only.
EPITOME: Certifies physical binding, assignment, review and wall reads plus
revocation and corruption denial without operational access.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_work_ethical_wall_source_adapters_real_mongo.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering / Legal Operations.
CERTIFICATION / UPDATE DATE: 2026-10-21.
CHANGELOG: 2026-10-21 v1.0.0 establishes G78 physical source evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: UUID database and exact tenant/matter/practitioner scope.
AUTHORITY BOUNDARY: Evidence reads only; no content access.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from datetime import UTC, datetime, timedelta
import os
import uuid
from typing import Any

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.domain.legal_practitioner_matter_binding import LegalPractitionerMatterBinding
from tools.eos.legal_operations.domain.legal_work_assignment import LegalWorkAssignment
from tools.eos.legal_operations.domain.legal_work_ethical_wall_policy import EthicalWallPolicyRevision
from tools.eos.legal_operations.domain.legal_work_practitioner_confidentiality_review_decision import ConfidentialityReviewDecision
from tools.eos.legal_operations.registry import legal_practitioner_matter_binding_registry as binding_registry
from tools.eos.legal_operations.registry.legal_work_assignment_registry import LegalWorkAssignmentRegistry
from tools.eos.legal_operations.registry.legal_work_ethical_wall_policy_registry import EthicalWallPolicyRegistry
from tools.eos.legal_operations.service import legal_work_ethical_wall_source_adapters as adapters
from tests.unit.test_legal_work_ethical_wall_policy_registry import revision as wall_revision
from tests.unit.test_legal_work_ethical_wall_source_adapters import assignment, binding, review

URI = os.environ["WILSY_G78_REAL_MONGO_URI"]
NOW = datetime(2026, 10, 21, 16, 0, tzinfo=UTC)


@pytest.fixture()
def context() -> Any:
    client: MongoClient[Any] = MongoClient(
        URI, serverSelectionTimeoutMS=5000, tz_aware=True, tzinfo=UTC,
    )
    hello = client.admin.command("hello")
    assert hello.get("isWritablePrimary") is True and hello.get("setName")
    database = client["wilsy_g78_" + uuid.uuid4().hex]
    bindings = database[binding_registry.COLLECTION_NAME]
    assignments = database["legal_work_assignments"]
    reviews = database["legal_work_confidentiality_reviews"]
    revisions = database["legal_work_ethical_wall_policy_revisions"]
    pointers = database["legal_work_ethical_wall_policy_currentness"]
    binding_registry.ensure_indexes(bindings)
    assignment_registry = LegalWorkAssignmentRegistry(assignments)
    assignment_registry.ensure_indexes()
    wall_registry = EthicalWallPolicyRegistry(revisions, pointers)
    wall_registry.ensure_indexes()
    try:
        yield client, database, bindings, assignment_registry, reviews, wall_registry
    finally:
        client.drop_database(database.name)
        client.close()


def test_real_multisource_current_reads(context: Any) -> None:
    client, _, bindings, assignments, reviews, walls = context
    bind, work, adjudication, wall = binding(), assignment(), review(), wall_revision()
    with client.start_session() as session:
        with session.start_transaction():
            binding_registry.append_binding(binding=bind, collection=bindings, session=session)
            assignments.persist(work, session=session)
            reviews.insert_one(adapters.encode_confidentiality_review(adjudication), session=session)
            walls.append(wall, session=session)
    with client.start_session() as session:
        with session.start_transaction():
            assert adapters.CanonicalPractitionerBindingSource(bindings).resolve_current(
                tenant_id="tenant-a", case_matter_id="matter-a",
                practitioner_principal_id="practitioner-a", session=session,
            ) == bind
            assert adapters.CanonicalMatterAssignmentSource(assignments).resolve_current(
                tenant_id="tenant-a", case_matter_id="matter-a",
                practitioner_principal_id="practitioner-a", session=session,
            ) == (work,)
            assert adapters.CanonicalConfidentialityReviewSource(reviews, NOW).resolve_current(
                tenant_id="tenant-a", case_matter_id="matter-a",
                practitioner_principal_id="practitioner-a", session=session,
            ) == adjudication
            source = adapters.CanonicalEthicalWallPolicySource(walls)
            assert source.get_current("tenant-a", "matter-a", "wall-1", session=session) == wall
            assert source.list_history("tenant-a", "matter-a", "wall-1", session=session) == (wall,)


def test_real_revocation_blocks_binding_currentness(context: Any) -> None:
    client, _, bindings, _, _, _ = context
    active = binding()
    revoked = active.revoke(
        revoked_by_principal_id="partner-a", revoked_at=NOW,
        evidence_reference="revocation-a",
    )
    with client.start_session() as session:
        with session.start_transaction():
            binding_registry.append_binding(binding=active, collection=bindings, session=session)
            binding_registry.append_binding(binding=revoked, collection=bindings, session=session)
    with pytest.raises(adapters.EthicalWallSourceUnavailable, match="BINDING_REVOKED"):
        with client.start_session() as session:
            with session.start_transaction():
                adapters.CanonicalPractitionerBindingSource(bindings).resolve_current(
                    tenant_id="tenant-a", case_matter_id="matter-a",
                    practitioner_principal_id="practitioner-a", session=session,
                )


def test_real_forged_review_and_cross_tenant_reads_deny(context: Any) -> None:
    client, _, bindings, _, reviews, _ = context
    bind = binding()
    document = adapters.encode_confidentiality_review(review())
    document["reviewer_principal_id"] = "practitioner-a"
    bindings.insert_one(bind.to_dict())
    reviews.insert_one(document)
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(adapters.EthicalWallSourceUnavailable, match="BINDING_NOT_FOUND"):
                adapters.CanonicalPractitionerBindingSource(bindings).resolve_current(
                    tenant_id="tenant-b", case_matter_id="matter-a",
                    practitioner_principal_id="practitioner-a", session=session,
                )
            with pytest.raises(adapters.EthicalWallSourceUnavailable, match="REVIEW_INVALID"):
                adapters.CanonicalConfidentialityReviewSource(reviews, NOW).resolve_current(
                    tenant_id="tenant-a", case_matter_id="matter-a",
                    practitioner_principal_id="practitioner-a", session=session,
                )


# ARTIFACT: test_legal_work_ethical_wall_source_adapters_real_mongo.py
# VERSION: v1.0.0-G78-SOURCE-ADAPTERS-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable source-read evidence only; no access grant
# TENANT POSTURE: exact tenant/matter/practitioner and UUID database
# FAIL-CLOSED POSTURE: revocation, forgery, absence and foreign scope reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
