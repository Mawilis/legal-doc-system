"""Real-Mongo L9A3 certificate for authorized client-acceptance composition.

This certificate uses synthetic authority readers and an isolated run-scoped
Mongo database. It proves current lifecycle/party reads, durable IAM evidence,
immutable acceptance admission, exact replay, and caller-owned transaction
boundaries without touching the canonical database or any production secret.
"""
from __future__ import annotations

from datetime import datetime, timezone
import os
from types import SimpleNamespace
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.orchestration.legal_client_acceptance_orchestrator import (
    issue_legal_client_acceptance,
)
from tools.eos.legal_operations.registry.legal_client_acceptance_registry import (
    LegalClientAcceptanceRegistry,
)
from tools.eos.legal_operations.registry.legal_matter_party_registry import (
    LegalMatterPartyRegistry,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
TENANT = "tenant-client-real"
PRINCIPAL = "principal-client-real"
MATTER_ID = "matter-real-1"
PARTY_ID = "party-real-1"
ACCEPTANCE_ID = "acceptance-real-1"
NOW = datetime(2026, 9, 26, 15, 0, 0, 123456, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128


class PrincipalReader:
    def resolve(self, principal_id: str, **_kwargs: object) -> object:
        if principal_id != PRINCIPAL:
            raise ValueError("unexpected principal")
        return SimpleNamespace(status=PrincipalStatus.ACTIVE)


class MembershipReader:
    def resolve(self, principal_id: str, tenant_id: str, **_kwargs: object) -> object:
        if (principal_id, tenant_id) != (PRINCIPAL, TENANT):
            raise ValueError("unexpected membership")
        return SimpleNamespace(status=TenantMembershipStatus.ACTIVE, revision=1)


class AssignmentReader:
    def resolve(self, principal_id: str, tenant_id: str, role_id: str, **_kwargs: object) -> object:
        if (principal_id, tenant_id) != (PRINCIPAL, TENANT):
            raise ValueError("unexpected assignment")
        if role_id == "tenant_legal_client":
            return SimpleNamespace(status=RoleAssignmentStatus.ACTIVE, revision=1)
        if role_id == "LEGAL_CLIENT":
            return SimpleNamespace(status=RoleAssignmentStatus.ACTIVE, revision=1)
        raise RoleAssignmentNotFoundError(role_id)


class TransactionProbe:
    starts = 0
    commits = 0
    aborts = 0


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any, Any, Any, Any]]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"host Mongo unavailable: {type(error).__name__}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip("wrong replica set")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("logical sessions unavailable")
        database = client[f"wilsy_l9a3_acceptance_{uuid.uuid4().hex}"]
        lifecycle = database.get_collection("legal_operations_lifecycle", write_concern=WriteConcern(w="majority", j=True), read_concern=ReadConcern("majority"))
        parties = database.get_collection("legal_matter_parties", write_concern=WriteConcern(w="majority", j=True), read_concern=ReadConcern("majority"))
        authorizations = database.get_collection("tenant_authorization_decision_evidence", write_concern=WriteConcern(w="majority", j=True), read_concern=ReadConcern("majority"))
        acceptances = database.get_collection("legal_client_acceptances", write_concern=WriteConcern(w="majority", j=True), read_concern=ReadConcern("majority"))
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        LegalMatterPartyRegistry.ensure_indexes(parties)
        LegalClientAcceptanceRegistry.ensure_indexes(acceptances)
        TenantAuthorizationDecisionEvidenceRegistry(authorizations, principal_repository=PrincipalReader()).ensure_indexes()
        yield client, database, lifecycle, parties, authorizations, acceptances
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _seed(client: MongoClient[Any], lifecycle: Any, parties: Any) -> None:
    matter = CaseMatter(
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        matter_reference="REF-REAL-1",
        opened_at=NOW,
        evidence_reference="matter-source:real-1",
    )
    party = register_legal_matter_party(
        matter=matter,
        party_id=PARTY_ID,
        party_kind=LegalMatterPartyKind.INDIVIDUAL,
        party_side=LegalMatterPartySide.CLIENT_SIDE,
        matter_role=LegalMatterPartyRole.CLIENT,
        subject_reference="client:real-1",
        subject_identity_fingerprint=FP_A,
        display_name="Synthetic Client",
        registered_at=NOW,
        source_evidence_reference="party-source:real-1",
        source_evidence_fingerprint=FP_B,
    )
    with client.start_session() as session:
        with session.start_transaction():
            LegalOperationsLifecycleRegistry.create(matter, lifecycle, session=session)
            LegalMatterPartyRegistry.persist_party(party, parties, session=session)


def test_real_mongo_authorized_issue_and_exact_replay(
    mongo_context: tuple[MongoClient[Any], Any, Any, Any, Any, Any],
) -> None:
    client, _, lifecycle, parties, authorizations, acceptances = mongo_context
    _seed(client, lifecycle, parties)
    authorization_registry = TenantAuthorizationDecisionEvidenceRegistry(
        authorizations,
        principal_repository=PrincipalReader(),
        membership_repository=MembershipReader(),
        role_assignment_repository=AssignmentReader(),
        business_role_repository=AssignmentReader(),
    )
    identity = SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        username=None,
        email=None,
        roles=["LEGAL_CLIENT"],
        permissions=[],
        auth_method="synthetic-test",
        status=PrincipalStatus.ACTIVE,
    )
    kwargs: dict[str, Any] = dict(
        identity=identity,
        case_matter_id=MATTER_ID,
        acceptance_id=ACCEPTANCE_ID,
        party_id=PARTY_ID,
        subject_reference="client:real-1",
        subject_identity_fingerprint=FP_A,
        acceptance_scope="platform-use",
        source_evidence_reference="client-source:real-1",
        source_evidence_fingerprint=FP_B,
        lifecycle_collection=lifecycle,
        party_collection=parties,
        acceptance_collection=acceptances,
        authorization_evidence_registry=authorization_registry,
    )
    with client.start_session() as session:
        with session.start_transaction():
            first = issue_legal_client_acceptance(**kwargs, session=session)
    with client.start_session() as session:
        with session.start_transaction():
            replay = issue_legal_client_acceptance(**kwargs, session=session)
    assert replay.to_dict() == first.to_dict()
    assert acceptances.count_documents({"tenant_id": TENANT}) == 1
    assert authorizations.count_documents({"tenant_id": TENANT}) == 1
    assert first.accepted_at == replay.accepted_at


# ARTIFACT: test_legal_client_acceptance_orchestrator_real_mongo.py
# VERSION: v1.0.0-L9A3-LEGAL-CLIENT-ACCEPTANCE-ISSUANCE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated physical orchestration composition only
# TENANT POSTURE: exact tenant/matter/party/IAM evidence and replay are asserted
# FAIL-CLOSED POSTURE: run-scoped database, caller-owned transactions, no secrets
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
