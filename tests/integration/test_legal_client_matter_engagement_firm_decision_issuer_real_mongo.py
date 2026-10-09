"""L9C8 real-Mongo certificate for Engagement firm-decision issuance.

TITLE: WILSY OS Engagement Firm-Decision Issuer Real-Mongo Certificate
VERSION: v1.0.2-L9C8-ENGAGEMENT-FIRM-DECISION-ISSUANCE-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove the published issuer against a UUID-isolated Mongo replica-set
         database, including caller-owned transactions, exact source reads,
         durable authorization evidence, replay, rollback and non-persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_engagement_firm_decision_issuer_real_mongo.py
COLLABORATION / OWNERSHIP: The issuer, CaseMatter lifecycle, LegalMatterParty,
                            IAM and authorization-evidence artifacts remain
                            production authorities; this file owns runtime
                            certification only.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C8 certifies sanctioned topology, physical predecessor
           indexes, exact transactional reads, Partner/Attorney authorization,
           Paralegal denial, durable evidence, commit/rollback, replay,
           chronology, deterministic IDs and firm-decision non-persistence.
           v1.0.1-L9C8 repairs the certificate-only prerequisite chronology
           with fixed whole-second UTC values safely before live authorization.
           v1.0.2-L9C8 asserts the issuer-level bounded rejection for corrupt
           authorization evidence and proves no replacement truth is inserted.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: URI and credentials are never printed; disposable
                             databases contain synthetic opaque identifiers only.
TENANT BOUNDARY: Every fixture and query is explicitly tenant scoped.
AUTHORITY BOUNDARY: Runtime certificate only; no firm-decision registry,
                    Engagement, Representation, Court or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Tests own session start/commit/abort; issuer owns none.
FAIL-CLOSED DECLARATION: Missing topology, stale/corrupt evidence, denied IAM,
                         divergent replay and rollback uncertainty fail.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from typing import Any, Iterator, cast
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision import (
    LegalClientMatterEngagementFirmDecision,
    LegalClientMatterEngagementFirmDecisionType,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.orchestration.legal_client_matter_engagement_firm_decision_orchestrator import (
    LegalClientMatterEngagementFirmDecisionOrchestrationError,
    issue_legal_client_matter_engagement_firm_decision,
)
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.legal_operations.registry import (
    legal_matter_party_registry as party_registry,
    legal_operations_lifecycle_registry as matter_registry,
)
from tools.eos.auth import tenant_authorization_decision_evidence_registry as evidence_module


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
MAX_DB_NAME_LENGTH = 63
TENANT = "tenant-l9c8-real"
PRINCIPAL = "principal-l9c8-real"
MATTER_ID = "matter-l9c8-real"
PARTY_ID = "party-l9c8-real"
# Keep prerequisite evidence safely before the authorization registry's live
# server clock. Whole-second UTC values survive BSON millisecond precision
# without introducing a wall-clock race into the certificate fixture.
NOW = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
SOURCE_FP = "a" * 128


class _Repository:
    """Canonical repository adapter used by the generic IAM evidence registry."""

    def __init__(self, collection: Any, kind: str) -> None:
        self.collection = collection
        self.kind = kind

    def resolve(self, *keys: str, **kwargs: object) -> object:
        session = cast(Any, kwargs.get("session"))
        if self.kind == "principal":
            return PrincipalAuthorityRepository.resolve(
                keys[0], self.collection, session=session
            )
        if self.kind == "membership":
            return TenantMembershipRepository.resolve(
                keys[0], keys[1], self.collection, session=session
            )
        return RoleAssignmentRepository.resolve(
            keys[0], keys[1], keys[2], self.collection, session=session
        )


@dataclass(frozen=True)
class MongoContext:
    client: MongoClient[Any]
    database: Any
    collections: dict[str, Any]
    authorization_registry: TenantAuthorizationDecisionEvidenceRegistry


@pytest.fixture
def mongo_context() -> Iterator[MongoContext]:
    """Open one sanctioned replica-set client and one bounded disposable DB."""
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
        except (OSError, PyMongoError) as error:
            pytest.skip(f"sanctioned Mongo unavailable: {type(error).__name__}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip("unexpected Mongo replica set")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("sanctioned Mongo has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("Mongo logical sessions unavailable")
        database = client[f"wilsy_l9c8_issuer_{uuid4().hex}"]
        assert len(database.name) <= MAX_DB_NAME_LENGTH
        collections = {
            "matter": database[matter_registry.COLLECTION],
            "party": database[party_registry.COLLECTION],
            "principal": database["principal_authorities"],
            "membership": database["tenant_memberships"],
            "assignment": database["role_assignments"],
            "authorization": database[evidence_module.COLLECTION],
        }
        matter_registry.LegalOperationsLifecycleRegistry.ensure_indexes(
            collections["matter"]
        )
        party_registry.LegalMatterPartyRegistry.ensure_indexes(collections["party"])
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        RoleAssignmentRepository.ensure_indexes(collections["assignment"])
        authorization_registry = TenantAuthorizationDecisionEvidenceRegistry(
            collections["authorization"],
            principal_repository=_Repository(collections["principal"], "principal"),
            membership_repository=_Repository(collections["membership"], "membership"),
            role_assignment_repository=_Repository(collections["assignment"], "assignment"),
            business_role_repository=_Repository(collections["assignment"], "assignment"),
        )
        authorization_registry.ensure_indexes()
        yield MongoContext(client, database, collections, authorization_registry)
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _identity(*, status: PrincipalStatus = PrincipalStatus.ACTIVE) -> SovereignIdentity:
    """Create one synthetic authenticated identity without caller overrides."""
    return SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        username=None,
        email=None,
        auth_method="real-mongo-certificate",
        status=status,
    )


def _matter() -> CaseMatter:
    """Create one canonical OPEN CaseMatter fixture value."""
    return CaseMatter(
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        matter_reference="CASE-L9C8-REAL",
        opened_at=NOW,
        evidence_reference="matter-source:l9c8-real",
    )


def _party(matter: CaseMatter | None = None, *, side: LegalMatterPartySide = LegalMatterPartySide.CLIENT_SIDE, role: LegalMatterPartyRole = LegalMatterPartyRole.CLIENT) -> Any:
    """Create one canonical party fixture with controlled classification."""
    source = matter or _matter()
    return register_legal_matter_party(
        matter=source,
        party_id=PARTY_ID,
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=side,
        matter_role=role,
        subject_reference="organization:client-l9c8-real",
        subject_identity_fingerprint=SOURCE_FP,
        display_name="Synthetic client",
        registered_at=NOW + timedelta(minutes=1),
        source_evidence_reference="party-source:l9c8-real",
        source_evidence_fingerprint=SOURCE_FP,
    )


def _seed(context: MongoContext, *, business_role: str = "tenant_legal_partner", grant_role: str = "LEGAL_PARTNER") -> None:
    """Persist canonical matter, party and current IAM authority fixtures."""
    with context.client.start_session() as session:
        with session.start_transaction():
            matter_registry.LegalOperationsLifecycleRegistry.create(
                _matter(), context.collections["matter"], session=session
            )
            party_registry.persist_party(
                _party(), context.collections["party"], session=session
            )
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(PRINCIPAL, PrincipalStatus.ACTIVE, 0),
                context.collections["principal"],
                session=session,
            )
            TenantMembershipRepository.insert(
                TenantMembershipAuthority(
                    PRINCIPAL, TENANT, TenantMembershipStatus.ACTIVE, 7
                ),
                context.collections["membership"],
                session=session,
            )
            RoleAssignmentRepository.insert(
                RoleAssignmentAuthority(
                    PRINCIPAL, TENANT, business_role, RoleAssignmentStatus.ACTIVE, 0
                ),
                context.collections["assignment"],
                session=session,
            )
            RoleAssignmentRepository.insert(
                RoleAssignmentAuthority(
                    PRINCIPAL, TENANT, grant_role, RoleAssignmentStatus.ACTIVE, 0
                ),
                context.collections["assignment"],
                session=session,
            )


def _issue(context: MongoContext, *, decision: LegalClientMatterEngagementFirmDecisionType | str = LegalClientMatterEngagementFirmDecisionType.ACCEPTED, identity: SovereignIdentity | None = None, idempotency_key: str = "firm-decision-intent-real", source_fingerprint: str = SOURCE_FP) -> LegalClientMatterEngagementFirmDecision:
    """Issue one decision in a caller-owned transaction and commit externally."""
    with context.client.start_session() as session:
        with session.start_transaction():
            value = issue_legal_client_matter_engagement_firm_decision(
                identity=identity or _identity(),
                case_matter_id=MATTER_ID,
                client_party_id=PARTY_ID,
                decision=decision,
                source_evidence_reference="firm-request:l9c8-real",
                source_evidence_fingerprint=source_fingerprint,
                idempotency_key=idempotency_key,
                matter_lifecycle_collection=context.collections["matter"],
                party_collection=context.collections["party"],
                authorization_evidence_registry=context.authorization_registry,
                session=session,
            )
        return value


def _index_map(collection: Any) -> dict[str, Any]:
    """Return physical index metadata without exposing document data."""
    return {item["name"]: item for item in collection.list_indexes()}


def test_real_mongo_topology_and_predecessor_indexes(mongo_context: MongoContext) -> None:
    """Certify writable replica-set, sessions, transactions and physical indexes."""
    hello = mongo_context.client.admin.command("hello")
    server_info = mongo_context.client.server_info()
    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    assert isinstance(server_info.get("version"), str)
    assert mongo_context.database.name.startswith("wilsy_l9c8_issuer_")
    assert len(mongo_context.database.name) <= MAX_DB_NAME_LENGTH
    assert "wilsy" != mongo_context.database.name
    assert {
        "legal_operations_tenant_entity_history",
        "legal_operations_tenant_evidence_unique",
    } <= set(_index_map(mongo_context.collections["matter"]))
    assert {
        "legal_party_tenant_party_unique",
        "legal_party_tenant_matter_subject_unique",
    } <= set(_index_map(mongo_context.collections["party"]))
    assert {
        "tenant_authorization_idempotency_unique",
        "authorization_decision_identity_unique",
    } <= set(_index_map(mongo_context.collections["authorization"]))
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            assert session.in_transaction is True


def test_real_mongo_transaction_required_and_open_matter_party_binding(
    mongo_context: MongoContext,
) -> None:
    """Certify exact OPEN matter/client-party reads and caller ownership."""
    _seed(mongo_context)
    with pytest.raises(LegalClientMatterEngagementFirmDecisionOrchestrationError):
        issue_legal_client_matter_engagement_firm_decision(
            identity=_identity(),
            case_matter_id=MATTER_ID,
            client_party_id=PARTY_ID,
            decision=LegalClientMatterEngagementFirmDecisionType.ACCEPTED,
            source_evidence_reference="firm-request:l9c8-real",
            source_evidence_fingerprint=SOURCE_FP,
            idempotency_key="missing-session",
            matter_lifecycle_collection=mongo_context.collections["matter"],
            party_collection=mongo_context.collections["party"],
            authorization_evidence_registry=mongo_context.authorization_registry,
            session=None,
        )
    value = _issue(mongo_context)
    assert value.tenant_id == TENANT
    assert value.case_matter_id == MATTER_ID
    assert value.client_party_id == PARTY_ID
    assert value.matter_fingerprint == _matter().fingerprint
    assert value.subject_reference == "organization:client-l9c8-real"
    assert value.subject_identity_fingerprint == SOURCE_FP


@pytest.mark.parametrize(
    "decision",
    tuple(LegalClientMatterEngagementFirmDecisionType),
)
def test_real_mongo_all_decisions_use_one_neutral_iam_operation(
    mongo_context: MongoContext,
    decision: LegalClientMatterEngagementFirmDecisionType,
) -> None:
    """Certify ACCEPTED, DECLINED and REQUIRES_REVIEW without formation."""
    _seed(mongo_context)
    value = _issue(mongo_context, decision=decision, idempotency_key=f"state-{decision.value}")
    assert value.decision is decision
    assert value.authorization_evidence_reference
    assert mongo_context.collections["authorization"].count_documents({}) == 1
    assert not {"engagements", "representations", "court_authorities"} & set(
        mongo_context.database.list_collection_names()
    )


@pytest.mark.parametrize(
    ("business_role", "grant_role"),
    (("tenant_legal_partner", "LEGAL_PARTNER"), ("tenant_legal_attorney", "LEGAL_ATTORNEY")),
)
def test_real_mongo_partner_and_attorney_authorize(
    mongo_context: MongoContext, business_role: str, grant_role: str
) -> None:
    """Both certified direct roles obtain durable authorization evidence."""
    _seed(mongo_context, business_role=business_role, grant_role=grant_role)
    value = _issue(mongo_context)
    evidence = mongo_context.collections["authorization"].find_one(
        {"tenant_id": TENANT, "principal_id": PRINCIPAL}
    )
    assert evidence is not None
    assert evidence["operation"] == "legal_matter_engagement_firm_decision_write"
    assert evidence["permission"] == "legal_operations:matter_engagement_firm_decision:write"
    assert evidence["business_role"] == business_role
    assert evidence["authorization_role"] == grant_role
    assert value.decision_actor_principal_id == evidence["principal_id"] == PRINCIPAL


def test_real_mongo_paralegal_and_inactive_authority_denied(
    mongo_context: MongoContext,
) -> None:
    """Least-authority and inactive principal/membership/grant states deny."""
    _seed(mongo_context, business_role="tenant_legal_paralegal", grant_role="LEGAL_PARALEGAL")
    with pytest.raises(LegalClientMatterEngagementFirmDecisionOrchestrationError):
        _issue(mongo_context)
    mongo_context.collections["principal"].update_one(
        {"principal_id": PRINCIPAL}, {"$set": {"status": PrincipalStatus.SUSPENDED.value}}
    )
    with pytest.raises(LegalClientMatterEngagementFirmDecisionOrchestrationError):
        _issue(mongo_context, idempotency_key="inactive-principal")


def test_real_mongo_commit_rollback_replay_and_divergence(
    mongo_context: MongoContext,
) -> None:
    """Certify commit durability, caller rollback, exact replay and conflict."""
    _seed(mongo_context)
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            value = issue_legal_client_matter_engagement_firm_decision(
                identity=_identity(), case_matter_id=MATTER_ID, client_party_id=PARTY_ID,
                decision=LegalClientMatterEngagementFirmDecisionType.ACCEPTED,
                source_evidence_reference="firm-request:l9c8-real",
                source_evidence_fingerprint=SOURCE_FP,
                idempotency_key="commit-intent",
                matter_lifecycle_collection=mongo_context.collections["matter"],
                party_collection=mongo_context.collections["party"],
                authorization_evidence_registry=mongo_context.authorization_registry,
                session=session,
            )
            assert mongo_context.collections["authorization"].count_documents({}, session=session) == 1
            assert mongo_context.collections["authorization"].count_documents({}) == 0
    row = mongo_context.collections["authorization"].find_one({"tenant_id": TENANT})
    assert row is not None
    loaded = mongo_context.authorization_registry.get(
        tenant_id=TENANT,
        authorization_decision_id=row["authorization_decision_id"],
    )
    assert value.authorization_evidence_fingerprint == loaded.authorization_evidence_fingerprint
    with mongo_context.client.start_session() as session:
        with pytest.raises(RuntimeError):
            with session.start_transaction():
                issue_legal_client_matter_engagement_firm_decision(
                    identity=_identity(), case_matter_id=MATTER_ID, client_party_id=PARTY_ID,
                    decision=LegalClientMatterEngagementFirmDecisionType.ACCEPTED,
                    source_evidence_reference="firm-request:l9c8-real",
                    source_evidence_fingerprint=SOURCE_FP,
                    idempotency_key="rollback-intent",
                    matter_lifecycle_collection=mongo_context.collections["matter"],
                    party_collection=mongo_context.collections["party"],
                    authorization_evidence_registry=mongo_context.authorization_registry,
                    session=session,
                )
                raise RuntimeError("caller abort")
    assert mongo_context.collections["authorization"].count_documents({"idempotency_key": "rollback-intent"}) == 0
    replay = _issue(mongo_context, idempotency_key="commit-intent")
    assert replay.to_dict() == value.to_dict()
    with pytest.raises(LegalClientMatterEngagementFirmDecisionOrchestrationError):
        _issue(mongo_context, idempotency_key="commit-intent", source_fingerprint="b" * 128)
    assert mongo_context.collections["authorization"].count_documents({}) == 1


def test_real_mongo_non_open_and_corrupt_authority_fail_closed(
    mongo_context: MongoContext,
) -> None:
    """Closed currentness and corrupt authorization replay never downgrade."""
    _seed(mongo_context)
    mongo_context.collections["matter"].update_one(
        {"tenant_id": TENANT, "entity_type": "CaseMatter"},
        {"$set": {"p1_payload.state": "CLOSED"}},
    )
    with pytest.raises(LegalClientMatterEngagementFirmDecisionOrchestrationError):
        _issue(mongo_context)
    mongo_context.collections["matter"].update_one(
        {"tenant_id": TENANT, "entity_type": "CaseMatter"},
        {"$set": {"p1_payload.state": "OPEN"}},
    )
    value = _issue(mongo_context)
    row = mongo_context.collections["authorization"].find_one({"tenant_id": TENANT})
    assert row is not None
    mongo_context.collections["authorization"].update_one(
        {"tenant_id": TENANT}, {"$set": {"authorization_evidence_fingerprint": "corrupt"}}
    )
    authorization_count_before = mongo_context.collections["authorization"].count_documents({})
    with pytest.raises(
        LegalClientMatterEngagementFirmDecisionOrchestrationError
    ) as failure:
        _issue(mongo_context, idempotency_key="firm-decision-intent-real")
    assert failure.value.code == "L9C8_AUTHORIZATION_EVIDENCE_UNAVAILABLE"
    assert str(failure.value) == "L9C8_AUTHORIZATION_EVIDENCE_UNAVAILABLE"
    assert (
        mongo_context.collections["authorization"].count_documents({})
        == authorization_count_before
    )
    assert (
        mongo_context.collections["authorization"].count_documents(
            {"authorization_evidence_fingerprint": "corrupt"}
        )
        == 1
    )
    assert value.fingerprint


def test_real_mongo_static_authority_boundary() -> None:
    """The integration certificate itself introduces no forbidden authority."""
    source = Path(
        "tools/eos/legal_operations/orchestration/legal_client_matter_engagement_firm_decision_orchestrator.py"
    ).read_text()
    tree = ast.parse(source)
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not any("legal_client_acceptance" in module for module in imported)
    assert not any("currentness" in module for module in imported)
    assert not any("representation" in module.lower() for module in imported)
    assert not any("court" in module.lower() for module in imported)
    assert not any("finance" in module.lower() for module in imported)
    assert "datetime.now" not in source
    assert "start_transaction" not in source
    assert "persist_firm_decision" not in source


# ARTIFACT: test_legal_client_matter_engagement_firm_decision_issuer_real_mongo.py
# VERSION: v1.0.2-L9C8-ENGAGEMENT-FIRM-DECISION-ISSUANCE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated physical issuer certificate only
# TENANT POSTURE: UUID-isolated database and exact tenant/matter/party scope
# FAIL-CLOSED POSTURE: topology, transaction, authority, replay, corruption and rollback failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
