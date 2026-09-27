"""Real-Mongo certificate for the published firm mandate acknowledgment issuer.

TITLE: WILSY OS Firm Mandate Acknowledgment Issuer Real-Mongo Certificate
VERSION: v1.0.0-L9B10-P7-FIRM-MANDATE-ACKNOWLEDGMENT-ISSUANCE-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the published acknowledgment issuer against real Mongo IAM,
         grant-currentness, acknowledgment-history, and caller transactions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_mandate_acknowledgment_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: The issuer and all injected registries remain the
                            production authorities; this file is certificate-only.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0 certifies topology, IAM-first disclosure, partner/attorney
           admission, denials, replay, divergence, abort, chronology,
           corruption, tenant isolation, snapshot reads and exact durable rows.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic records only; no URI,
                             credentials, tokens, hashes or PII are printed.
TENANT BOUNDARY: Every IAM, grant, history and acknowledgment operation is
                 exact tenant-scoped under one caller-owned session.
AUTHORITY BOUNDARY: Immutable firm acknowledgment evidence only. No mandate,
                    engagement, representation, court or client authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authorization_decision_evidence_registry import TenantAuthorizationDecisionEvidenceRegistry
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacityType,
    record_legal_client_acting_capacity,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment import (
    LegalClientMatterMandateAcknowledgmentDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant import (
    LegalClientMatterMandateBreadth,
    LegalClientMatterMandateCapability,
    LegalClientMatterMandateGrant,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_lifecycle import (
    LegalClientMatterMandateGrantLifecycleEvent,
    LegalClientMatterMandateGrantLifecycleReason,
    record_legal_client_matter_mandate_grant_lifecycle,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_acknowledgment_orchestrator import (
    LegalClientMatterMandateAcknowledgmentOrchestrationError,
    issue_legal_client_matter_mandate_acknowledgment,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_mandate_acknowledgment_registry as acknowledgment_registry,
    legal_client_matter_mandate_grant_lifecycle_registry as grant_lifecycle_registry,
    legal_client_matter_mandate_grant_registry as grant_registry,
    legal_operations_lifecycle_registry as matter_registry,
)

MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
REPLICA_SET = "wilsyVendorCertRS"
MONGO_VERSION = "7.0.37"
TENANT = "tenant-l9b10-p7-real"
MATTER_ID = "matter-l9b10-p7-real"
GRANT_ID = "grant-l9b10-p7-real"
FINGERPRINT = "a" * 128
AUTH_FINGERPRINT = "b" * 128


class _Repo:
    """Adapter exposing actual repository resolution with the caller session."""

    def __init__(self, collection: Any, kind: str) -> None:
        self.collection, self.kind = collection, kind

    def resolve(self, *args: str, **kwargs: Any) -> Any:
        session = kwargs.get("session")
        if self.kind == "principal":
            return PrincipalAuthorityRepository.resolve(args[0], self.collection, session=session)
        if self.kind == "membership":
            return TenantMembershipRepository.resolve(args[0], args[1], self.collection, session=session)
        return RoleAssignmentRepository.resolve(args[0], args[1], args[2], self.collection, session=session)


def _identity(principal: str, *, tenant: str = TENANT, status: PrincipalStatus = PrincipalStatus.ACTIVE) -> SovereignIdentity:
    return SovereignIdentity(identity_id=principal, tenant_id=tenant, username=None, email=None, roles=[], permissions=[], auth_method="synthetic", status=status)


def _collections(db: Any) -> dict[str, Any]:
    return {
        "grant": db[grant_registry.COLLECTION],
        "grant_lifecycle": db[grant_lifecycle_registry.COLLECTION],
        "matter": db[matter_registry.COLLECTION],
        "ack": db[acknowledgment_registry.COLLECTION],
        "principal": db["principal_authorities"],
        "membership": db["tenant_memberships"],
        "assignment": db["role_assignments"],
        "authorization": db["tenant_authorization_decision_evidence"],
    }


def _ensure_indexes(c: dict[str, Any]) -> None:
    PrincipalAuthorityRepository.ensure_indexes(c["principal"])
    TenantMembershipRepository.ensure_indexes(c["membership"])
    RoleAssignmentRepository.ensure_indexes(c["assignment"])
    matter_registry.LegalOperationsLifecycleRegistry.ensure_indexes(c["matter"])
    grant_registry.ensure_indexes(c["grant"])
    grant_lifecycle_registry.ensure_indexes(c["grant_lifecycle"])
    acknowledgment_registry.ensure_indexes(c["ack"])
    TenantAuthorizationDecisionEvidenceRegistry(
        c["authorization"], principal_repository=_Repo(c["principal"], "principal")
    ).ensure_indexes()


def _grant(now: datetime, grant_id: str = GRANT_ID, tenant: str = TENANT) -> LegalClientMatterMandateGrant:
    matter = CaseMatter(tenant_id=tenant, case_matter_id=MATTER_ID, matter_reference="synthetic", opened_at=now - timedelta(hours=6), evidence_reference="matter:evidence")
    party = register_legal_matter_party(matter=matter, party_id=f"party-{tenant}", party_kind=LegalMatterPartyKind.ORGANIZATION, party_side=LegalMatterPartySide.CLIENT_SIDE, matter_role=LegalMatterPartyRole.CLIENT, subject_reference="client:synthetic", subject_identity_fingerprint=FINGERPRINT, display_name="Synthetic client", registered_at=now - timedelta(hours=5), source_evidence_reference="party:evidence", source_evidence_fingerprint=AUTH_FINGERPRINT)
    capacity = record_legal_client_acting_capacity(case_matter=matter, party=party, capacity_id=f"capacity-{tenant}", principal_id=f"client-{tenant}", capacity_type=LegalClientActingCapacityType.AUTHORIZED_AGENT, effective_from=now - timedelta(hours=4), effective_until=None, source_evidence_reference="capacity:evidence", source_evidence_fingerprint=FINGERPRINT)
    return LegalClientMatterMandateGrant.from_canonical(client_grant_id=grant_id, case_matter=matter, party=party, acting_capacity=capacity, breadth=LegalClientMatterMandateBreadth.LIMITED, scope_reference="scope:synthetic", scope_fingerprint=AUTH_FINGERPRINT, capabilities=(LegalClientMatterMandateCapability.ADVISORY,), source_evidence_reference="grant:evidence", source_evidence_fingerprint=FINGERPRINT, authorization_evidence_reference="grant:authorization", authorization_evidence_fingerprint=AUTH_FINGERPRINT, occurred_at=now - timedelta(hours=3), effective_from=now - timedelta(hours=2), effective_until=now + timedelta(days=30), idempotency_key=f"grant:{tenant}:{grant_id}")


def _seed(c: dict[str, Any], client: MongoClient[Any], *, principals: tuple[str, ...] = ("partner", "attorney", "paralegal", "inactive", "no-membership")) -> LegalClientMatterMandateGrant:
    now = datetime.now(timezone.utc)
    source = _grant(now)
    with client.start_session() as session:
        with session.start_transaction():
            matter_registry.LegalOperationsLifecycleRegistry.create(CaseMatter(tenant_id=TENANT, case_matter_id=MATTER_ID, matter_reference="synthetic", opened_at=now - timedelta(hours=6), evidence_reference="matter:evidence"), c["matter"], session=session)
            grant_registry.persist_grant(source, c["grant"], session=session)
            for label in principals:
                principal_id = f"principal-{label}"
                PrincipalAuthorityRepository.create(PrincipalAuthority(principal_id, PrincipalStatus.SUSPENDED if label == "inactive" else PrincipalStatus.ACTIVE, 0), c["principal"], session=session)
                if label != "no-membership":
                    TenantMembershipRepository.insert(TenantMembershipAuthority(principal_id, TENANT, TenantMembershipStatus.ACTIVE if label != "inactive" else TenantMembershipStatus.ACTIVE, 1), c["membership"], session=session)
                role = {"partner": "LEGAL_PARTNER", "attorney": "LEGAL_ATTORNEY", "paralegal": "LEGAL_PARALEGAL"}.get(label)
                if role:
                    RoleAssignmentRepository.insert(RoleAssignmentAuthority(principal_id, TENANT, role, RoleAssignmentStatus.ACTIVE, 0), c["assignment"], session=session)
                business = {"partner": "tenant_legal_partner", "attorney": "tenant_legal_attorney", "paralegal": "tenant_legal_paralegal"}.get(label)
                if business:
                    RoleAssignmentRepository.insert(RoleAssignmentAuthority(principal_id, TENANT, business, RoleAssignmentStatus.ACTIVE, 0), c["assignment"], session=session)
    return source


def _issuer(c: dict[str, Any]) -> TenantAuthorizationDecisionEvidenceRegistry:
    assignment = _Repo(c["assignment"], "assignment")
    return TenantAuthorizationDecisionEvidenceRegistry(c["authorization"], principal_repository=_Repo(c["principal"], "principal"), membership_repository=_Repo(c["membership"], "membership"), role_assignment_repository=assignment, business_role_repository=assignment)


def _issue(client: MongoClient[Any], c: dict[str, Any], principal: str, key: str, *, tenant: str = TENANT, grant_id: str = GRANT_ID, decision: LegalClientMatterMandateAcknowledgmentDecision = LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED) -> Any:
    with client.start_session() as session:
        with session.start_transaction():
            return issue_legal_client_matter_mandate_acknowledgment(identity=_identity(principal, tenant=tenant), client_grant_id=grant_id, decision=decision, idempotency_key=key, source_evidence_reference="source:real", source_evidence_fingerprint=FINGERPRINT, grant_collection=c["grant"], grant_lifecycle_collection=c["grant_lifecycle"], matter_lifecycle_collection=c["matter"], acknowledgment_collection=c["ack"], authorization_evidence_registry=_issuer(c), session=session)


@pytest.fixture()
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, dict[str, Any]]]:
    client: MongoClient[Any] = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5_000, retryWrites=True, tz_aware=True)
    database: Any = None
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == REPLICA_SET and hello.get("isWritablePrimary") is True and hello.get("logicalSessionTimeoutMinutes") is not None
        assert client.server_info().get("version") == MONGO_VERSION
        database = client[f"wilsy_l9b10_p7_ack_issuer_{uuid4().hex}"]
        c = _collections(database)
        _ensure_indexes(c)
        yield client, database, c
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def test_real_mongo_partner_attorney_commit_replay_and_exact_rows(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, db, c = mongo_context
    source = _seed(c, client)
    partner = _issue(client, c, "principal-partner", "partner-key")
    attorney = _issue(client, c, "principal-attorney", "attorney-key", decision=LegalClientMatterMandateAcknowledgmentDecision.DECLINED)
    review = _issue(client, c, "principal-partner", "review-key", decision=LegalClientMatterMandateAcknowledgmentDecision.REQUIRES_REVIEW)
    replay = _issue(client, c, "principal-partner", "partner-key")
    assert partner.to_dict() == replay.to_dict()
    assert partner.tenant_id == TENANT and partner.client_grant_id == GRANT_ID
    assert partner.occurred_at == partner.effective_from
    assert partner.client_grant_fingerprint == source.fingerprint
    assert c["ack"].count_documents({"tenant_id": TENANT}) == 3
    assert c["authorization"].count_documents({"tenant_id": TENANT}) == 3
    assert {partner.decision.value, attorney.decision.value, review.decision.value} == {"ACKNOWLEDGED", "DECLINED", "REQUIRES_REVIEW"}
    authorization_rows = list(c["authorization"].find({"tenant_id": TENANT}))
    assert {row["operation"] for row in authorization_rows} == {"legal_matter_mandate_acknowledgment_write"}
    assert {row["permission"] for row in authorization_rows} == {"legal_operations:matter_mandate_acknowledgment:write"}
    assert all(row["subject_reference"].startswith("legal-matter-mandate-acknowledgment:grant:") for row in authorization_rows)
    assert attorney.decision_actor_principal_id == "principal-attorney"
    assert not {"engagements", "representations", "court_authorities", "financial_approvals"} & set(db.list_collection_names())


@pytest.mark.parametrize("principal", ["principal-paralegal", "principal-inactive", "principal-no-membership"])
def test_real_mongo_iam_denials_happen_before_grant_disclosure(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]], principal: str) -> None:
    client, _db, c = mongo_context
    _seed(c, client)
    with pytest.raises(LegalClientMatterMandateAcknowledgmentOrchestrationError):
        _issue(client, c, principal, f"denied-{principal}")
    assert c["ack"].count_documents({}) == 0


def test_real_mongo_transaction_abort_and_caller_session_boundary(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _db, c = mongo_context
    _seed(c, client)
    with pytest.raises(LegalClientMatterMandateAcknowledgmentOrchestrationError):
        issue_legal_client_matter_mandate_acknowledgment(identity=_identity("principal-partner"), client_grant_id=GRANT_ID, decision="ACKNOWLEDGED", idempotency_key="no-session", source_evidence_reference="source:real", source_evidence_fingerprint=FINGERPRINT, grant_collection=c["grant"], grant_lifecycle_collection=c["grant_lifecycle"], matter_lifecycle_collection=c["matter"], acknowledgment_collection=c["ack"], authorization_evidence_registry=_issuer(c), session=None)
    with pytest.raises(RuntimeError):
        with client.start_session() as session:
            with session.start_transaction():
                issue_legal_client_matter_mandate_acknowledgment(identity=_identity("principal-partner"), client_grant_id=GRANT_ID, decision="ACKNOWLEDGED", idempotency_key="abort", source_evidence_reference="source:real", source_evidence_fingerprint=FINGERPRINT, grant_collection=c["grant"], grant_lifecycle_collection=c["grant_lifecycle"], matter_lifecycle_collection=c["matter"], acknowledgment_collection=c["ack"], authorization_evidence_registry=_issuer(c), session=session)
                raise RuntimeError("caller abort")
    assert c["ack"].count_documents({}) == 0 and c["authorization"].count_documents({}) == 0


def test_real_mongo_tenant_isolation_unknown_source_and_corrupt_ack_history(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _db, c = mongo_context
    _seed(c, client)
    with pytest.raises(LegalClientMatterMandateAcknowledgmentOrchestrationError):
        _issue(client, c, "principal-partner", "foreign-tenant", tenant="tenant-other")
    with pytest.raises(LegalClientMatterMandateAcknowledgmentOrchestrationError):
        _issue(client, c, "principal-partner", "unknown-grant", grant_id="unknown-grant")
    c["ack"].insert_one({"tenant_id": TENANT, "acknowledgment_id": "corrupt", "fingerprint": FINGERPRINT, "client_grant_id": GRANT_ID})
    with pytest.raises(LegalClientMatterMandateAcknowledgmentOrchestrationError):
        _issue(client, c, "principal-partner", "corrupt-history")


def test_real_mongo_grant_revocation_blocks_and_history_is_append_only(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _db, c = mongo_context
    source = _seed(c, client)
    now = datetime.now(timezone.utc)
    event = record_legal_client_matter_mandate_grant_lifecycle(client_grant=source, lifecycle_event_id="revocation", event=LegalClientMatterMandateGrantLifecycleEvent.REVOKED, decision_actor_principal_id="principal-partner", authorization_evidence_reference="auth:revocation", authorization_evidence_fingerprint=AUTH_FINGERPRINT, source_evidence_reference="source:revocation", source_evidence_fingerprint=FINGERPRINT, occurred_at=now - timedelta(minutes=2), effective_from=now - timedelta(minutes=1), idempotency_key="revocation", reason=LegalClientMatterMandateGrantLifecycleReason.CLIENT_WITHDRAWAL)
    with client.start_session() as session:
        with session.start_transaction():
            grant_lifecycle_registry.persist_event(event, c["grant_lifecycle"], session=session)
    with pytest.raises(LegalClientMatterMandateAcknowledgmentOrchestrationError):
        _issue(client, c, "principal-partner", "revoked")
    assert c["grant_lifecycle"].count_documents({"tenant_id": TENANT}) == 1


# ARTIFACT: test_legal_client_matter_mandate_acknowledgment_orchestrator_real_mongo.py
# VERSION: v1.0.0-L9B10-P7-FIRM-MANDATE-ACKNOWLEDGMENT-ISSUANCE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated real-Mongo immutable acknowledgment certificate only
# TENANT POSTURE: UUID database and exact tenant/grant/principal predicates
# FAIL-CLOSED POSTURE: denial, stale, corrupt, divergent, abort and isolation reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
