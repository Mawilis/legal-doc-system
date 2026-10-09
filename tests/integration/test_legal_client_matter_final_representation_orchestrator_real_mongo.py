"""Real-Mongo certificate for the L9C11-P25 final Representation orchestrator.

TITLE: WILSY OS Legal Client Matter Final Representation Orchestrator Real-Mongo Certificate
VERSION: v1.0.0-L9C11-P25R-FINAL-REPRESENTATION-ORCHESTRATOR-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify P25 against a writable, UUID-isolated sanctioned Mongo replica
         set: caller-owned transactions, exact session propagation, P21A/P22 and
         Engagement/Mandate revalidation, IAM lineage, deterministic scope
         intersection, P24 persistence, replay, rollback and tenant isolation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_final_representation_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: P21A, P22, Engagement and Mandate composers remain
                            read-only currentness authorities; P24 remains the
                            immutable persistence authority. This certificate
                            owns disposable runtime evidence only.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P25R certifies sanctioned topology, short UUID database
           isolation, active caller transactions, exact upstream bindings,
           representative IAM, scope narrowing, replay/collision behavior,
           rollback, zero upstream writes and no downstream authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; credentials,
                             bearer material and personal data are never logged.
TENANT BOUNDARY: Every read and write is exact-tenant and exact-lineage scoped;
                 canonical database ``wilsy`` is prohibited.
AUTHORITY BOUNDARY: Final Representation formation evidence only. No currentness
                    row, IAM evidence, Court, HTTP/UI/Node or financial truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for execution.
TRANSACTION BOUNDARY: The certificate owns setup and teardown transactions;
                      P25 receives one active caller session and owns none.
FAIL-CLOSED DECLARATION: Any topology, lineage, currentness, IAM, scope,
                         persistence, rollback or isolation failure fails.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
import os
from typing import Any, Iterator, Mapping, cast
from uuid import uuid4

import pymongo
import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import COLLECTION as PRINCIPAL_COLLECTION
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import COLLECTION as ASSIGNMENT_COLLECTION
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import COLLECTION as MEMBERSHIP_COLLECTION
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.domain.legal_client_matter_engagement import LegalClientMatterEngagement
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import LegalClientMatterRepresentationAuthority
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import LegalClientMatterRepresentationFirmDecision
from tools.eos.legal_operations.orchestration.legal_client_matter_engagement_currentness_composer import LegalClientMatterEngagementCurrentnessComposer
from tools.eos.legal_operations.orchestration.legal_client_matter_final_representation_orchestrator import (
    LegalClientMatterFinalRepresentationFormationRequest,
    LegalClientMatterFinalRepresentationOrchestrationError,
    LegalClientMatterFinalRepresentationOrchestrator,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_currentness_composer import LegalClientMatterMandateCurrentnessComposer
from tools.eos.legal_operations.orchestration.legal_client_matter_representation_authority_currentness_composer import LegalClientMatterRepresentationAuthorityCurrentnessComposer
from tools.eos.legal_operations.orchestration.legal_client_matter_representation_authority_currentness_composer import LegalClientMatterRepresentationAuthorityCurrentnessComposerError
from tools.eos.legal_operations.orchestration.legal_client_matter_representation_firm_decision_currentness_composer import LegalClientMatterRepresentationFirmDecisionCurrentnessComposer
from tools.eos.legal_operations.orchestration.legal_client_matter_representation_firm_decision_currentness_composer import LegalClientMatterRepresentationFirmDecisionCurrentnessComposerError
from tools.eos.legal_operations.registry import (
    legal_client_matter_engagement_registry as engagement_registry,
    legal_client_matter_final_representation_registry as final_registry,
    legal_client_matter_mandate_acknowledgment_registry as acknowledgment_registry,
    legal_client_matter_mandate_grant_lifecycle_registry as grant_lifecycle_registry,
    legal_client_matter_mandate_grant_registry as grant_registry,
    legal_client_matter_mandate_registry as mandate_registry,
    legal_client_matter_representation_authority_registry as authority_registry,
    legal_client_matter_representation_firm_decision_registry as decision_registry,
    legal_operations_lifecycle_registry as matter_registry,
)
from tests.integration.test_legal_client_matter_mandate_currentness_composer_real_mongo import _bundle


MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
REPLICA_SET = "wilsyVendorCertRS"
MONGO_VERSION = "7.0.37"
BASE = datetime(2026, 9, 28, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-l9c11-p25r"
OTHER_TENANT = "tenant-other-l9c11-p25r"
REPRESENTATIVE = "principal-representative-l9c11-p25r"
MATTER_FP = hashlib.sha3_512(b"p25r-matter").hexdigest()
SUBJECT_FP = hashlib.sha3_512(b"p25r-subject").hexdigest()
HEX_A = hashlib.sha3_512(b"p25r-a").hexdigest()
HEX_B = hashlib.sha3_512(b"p25r-b").hexdigest()


class RecordingCollection:
    """Delegate a real collection while recording every supplied session."""

    def __init__(self, collection: Any) -> None:
        self._collection = collection
        self.session_ids: list[int] = []

    def __getattr__(self, name: str) -> Any:
        value = getattr(self._collection, name)
        if not callable(value):
            return value

        def invoke(*args: Any, **kwargs: Any) -> Any:
            session = kwargs.get("session")
            if session is not None:
                self.session_ids.append(id(session))
            return value(*args, **kwargs)

        return invoke


class _RepositoryAdapter:
    """Expose canonical IAM repositories with disposable collections."""

    def __init__(self, collection: Any, kind: str) -> None:
        self.collection = collection
        self.kind = kind

    def resolve(self, *args: str, **kwargs: Any) -> Any:
        session = kwargs.get("session")
        if self.kind == "principal":
            return PrincipalAuthorityRepository.resolve(args[0], self.collection, session=session)
        if self.kind == "membership":
            return TenantMembershipRepository.resolve(args[0], args[1], self.collection, session=session)
        return RoleAssignmentRepository.resolve(args[0], args[1], args[2], self.collection, session=session)


@dataclass
class MongoContext:
    """One disposable database and raw/instrumented collection handles."""

    client: MongoClient[Any]
    database: Any
    raw: dict[str, Any]
    collections: dict[str, RecordingCollection]
    server_version: str


def _collections(database: Any) -> dict[str, Any]:
    return {
        "matter": database[matter_registry.COLLECTION],
        "grant": database[grant_registry.COLLECTION],
        "grant_lifecycle": database[grant_lifecycle_registry.COLLECTION],
        "acknowledgment": database[acknowledgment_registry.COLLECTION],
        "mandate": database[mandate_registry.COLLECTION],
        "engagement": database[engagement_registry.COLLECTION],
        "authority": database[authority_registry.COLLECTION],
        "decision": database[decision_registry.COLLECTION],
        "final": database[final_registry.COLLECTION],
        "principal": database[PRINCIPAL_COLLECTION],
        "membership": database[MEMBERSHIP_COLLECTION],
        "assignment": database[ASSIGNMENT_COLLECTION],
    }


def _ensure_indexes(raw: Mapping[str, Any]) -> None:
    matter_registry.LegalOperationsLifecycleRegistry.ensure_indexes(raw["matter"])
    grant_registry.ensure_indexes(raw["grant"])
    grant_lifecycle_registry.ensure_indexes(raw["grant_lifecycle"])
    acknowledgment_registry.ensure_indexes(raw["acknowledgment"])
    mandate_registry.ensure_indexes(raw["mandate"])
    engagement_registry.ensure_indexes(raw["engagement"])
    authority_registry.ensure_indexes(raw["authority"])
    decision_registry.ensure_indexes(raw["decision"])
    final_registry.ensure_indexes(raw["final"])
    PrincipalAuthorityRepository.ensure_indexes(raw["principal"])
    TenantMembershipRepository.ensure_indexes(raw["membership"])
    RoleAssignmentRepository.ensure_indexes(raw["assignment"])


@pytest.fixture()
def mongo_context() -> Iterator[MongoContext]:
    """Yield one writable UUID-isolated database and drop only that database."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000,
        retryWrites=True, tz_aware=True,
    )
    database = None
    try:
        try:
            hello = client.admin.command("hello")
            server_version = str(client.server_info().get("version"))
        except PyMongoError as error:
            pytest.skip(f"real Mongo unavailable for operator runtime: {type(error).__name__}")
        assert hello.get("setName") == REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert server_version == MONGO_VERSION
        database_name = f"wilsy_l9c11_p25r_{uuid4().hex}"
        assert len(database_name) <= 63
        assert database_name != "wilsy"
        database = client[database_name]
        raw = _collections(database)
        _ensure_indexes(raw)
        wrapped = {name: RecordingCollection(value) for name, value in raw.items()}
        yield MongoContext(client, database, raw, wrapped, server_version)
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _persist(context: MongoContext, values: tuple[Any, Any, Any, Any], *, authority: Any, decision: Any, engagement: Any, role: str) -> None:
    """Persist all canonical prerequisites in one setup transaction."""
    matter, grant, acknowledgment, mandate = values
    with context.client.start_session() as session:
        with session.start_transaction():
            matter_registry.LegalOperationsLifecycleRegistry.create(matter, context.raw["matter"], session=session)
            grant_registry.persist_grant(grant, context.raw["grant"], session=session)
            acknowledgment_registry.persist_acknowledgment(acknowledgment, context.raw["acknowledgment"], session=session)
            mandate_registry.persist_mandate(mandate, context.raw["mandate"], session=session)
            engagement_registry.persist_engagement(engagement, context.raw["engagement"], session=session)
            authority_registry.persist_representation_authority(authority, context.raw["authority"], session=session)
            if decision is not None:
                decision_registry.persist_firm_decision(decision, context.raw["decision"], session=session)
            PrincipalAuthorityRepository.create(PrincipalAuthority(REPRESENTATIVE, PrincipalStatus.ACTIVE, 0), context.raw["principal"], session=session)
            TenantMembershipRepository.insert(TenantMembershipAuthority(REPRESENTATIVE, TENANT, TenantMembershipStatus.ACTIVE, 0), context.raw["membership"], session=session)
            RoleAssignmentRepository.insert(RoleAssignmentAuthority(REPRESENTATIVE, TENANT, role, RoleAssignmentStatus.ACTIVE, 0), context.raw["assignment"], session=session)


def _seed(context: MongoContext, *, role: str = "LEGAL_ATTORNEY", authority_decision: str = "APPOINTED", firm_decision: str | None = "ACCEPTED") -> dict[str, Any]:
    """Construct and persist one complete valid P25 prerequisite bundle."""
    values = _bundle(tenant=TENANT, grant_id="grant-p25r", mandate_id="mandate-p25r", matter_id="matter-p25r")
    matter, grant, acknowledgment, mandate = values
    engagement = LegalClientMatterEngagement(
        engagement_id="engagement-p25r", tenant_id=TENANT, case_matter_id=matter.case_matter_id,
        matter_fingerprint=matter.fingerprint, client_party_id=mandate.client_party_id,
        subject_reference="client:subject-p25r", subject_identity_fingerprint=mandate.subject_identity_fingerprint,
        acting_capacity_id=mandate.acting_capacity_id, acting_capacity_fingerprint=mandate.acting_capacity_fingerprint,
        client_acceptance_id="acceptance-p25r", client_acceptance_fingerprint=HEX_A,
        instrument_id="instrument-p25r", version="v1", instrument_fingerprint=HEX_B,
        content_fingerprint=HEX_A, mandate_id=mandate.mandate_id, mandate_scope=mandate.scope_reference,
        mandate_fingerprint=mandate.fingerprint, conflict_disposition_id="conflict-p25r",
        conflict_disposition_fingerprint=HEX_B, firm_decision_id="engagement-decision-p25r",
        decision_actor_principal_id=REPRESENTATIVE, firm_decision_fingerprint=HEX_A,
        authorization_evidence_reference="evidence:engagement-auth-p25r", authorization_evidence_fingerprint=HEX_B,
        source_evidence_reference="evidence:engagement-p25r", source_evidence_fingerprint=HEX_A,
        effective_from=BASE - timedelta(hours=1), idempotency_key="idempotency:engagement-p25r",
    )
    authority = LegalClientMatterRepresentationAuthority(
        authority_id="authority-p25r", tenant_id=TENANT, case_matter_id=matter.case_matter_id,
        matter_fingerprint=matter.fingerprint, client_party_id=mandate.client_party_id,
        subject_reference="client:subject-p25r", subject_identity_fingerprint=mandate.subject_identity_fingerprint,
        engagement_id=engagement.engagement_id, engagement_fingerprint=engagement.fingerprint,
        mandate_id=mandate.mandate_id, mandate_fingerprint=mandate.fingerprint,
        mandate_scope_reference=mandate.scope_reference, mandate_scope_fingerprint=mandate.scope_fingerprint,
        mandate_capabilities=mandate.capabilities, acting_capacity_id=mandate.acting_capacity_id,
        acting_capacity_fingerprint=mandate.acting_capacity_fingerprint, representative_principal_id=REPRESENTATIVE,
        representative_role=role, representation_scope_capabilities=("ADVISORY",), decision=authority_decision,
        appointing_principal_id="principal-client-p25r", source_evidence_reference="evidence:authority-p25r",
        source_evidence_fingerprint=HEX_A, authorization_evidence_reference="evidence:authority-auth-p25r",
        authorization_evidence_fingerprint=HEX_B, occurred_at=BASE - timedelta(minutes=20),
        effective_from=BASE - timedelta(minutes=15), effective_until=BASE + timedelta(days=30),
        idempotency_key="idempotency:authority-p25r",
    )
    decision = None if firm_decision is None else LegalClientMatterRepresentationFirmDecision.from_client_authority(
        client_authority=authority, decision=firm_decision, decision_actor_principal_id="principal-firm-p25r",
        authorization_evidence_reference="evidence:decision-auth-p25r", authorization_evidence_fingerprint=HEX_A,
        source_evidence_reference="evidence:decision-p25r", source_evidence_fingerprint=HEX_B,
        occurred_at=BASE - timedelta(minutes=10), effective_from=BASE - timedelta(minutes=5),
        idempotency_key="idempotency:decision-p25r",
    )
    _persist(context, values, authority=authority, decision=decision, engagement=engagement, role=role)
    return {"values": values, "matter": matter, "mandate": mandate, "engagement": engagement, "authority": authority, "decision": decision}


def _orchestrator(context: MongoContext) -> LegalClientMatterFinalRepresentationOrchestrator:
    c = context.collections
    return LegalClientMatterFinalRepresentationOrchestrator(
        authority_currentness_composer=LegalClientMatterRepresentationAuthorityCurrentnessComposer(authority_collection=c["authority"]),
        decision_currentness_composer=LegalClientMatterRepresentationFirmDecisionCurrentnessComposer(decision_collection=c["decision"]),
        engagement_currentness_composer=LegalClientMatterEngagementCurrentnessComposer(engagement_collection=c["engagement"]),
        mandate_currentness_composer=LegalClientMatterMandateCurrentnessComposer(
            mandate_collection=c["mandate"], grant_collection=c["grant"],
            grant_lifecycle_collection=c["grant_lifecycle"], matter_lifecycle_collection=c["matter"],
            acknowledgment_collection=c["acknowledgment"],
        ),
        authority_collection=c["authority"], decision_collection=c["decision"],
        engagement_collection=c["engagement"], mandate_collection=c["mandate"],
        final_representation_collection=c["final"],
        principal_repository=_RepositoryAdapter(c["principal"], "principal"),
        membership_repository=_RepositoryAdapter(c["membership"], "membership"),
        role_assignment_repository=_RepositoryAdapter(c["assignment"], "assignment"),
        principal_collection=c["principal"], membership_collection=c["membership"],
        role_assignment_collection=c["assignment"],
    )


def _request(bundle: Mapping[str, Any], **overrides: Any) -> LegalClientMatterFinalRepresentationFormationRequest:
    matter = bundle["matter"]
    mandate = bundle["mandate"]
    values: dict[str, Any] = {
        "tenant_id": TENANT, "case_matter_id": matter.case_matter_id,
        "matter_fingerprint": matter.fingerprint, "client_party_id": mandate.client_party_id,
        "subject_identity_fingerprint": mandate.subject_identity_fingerprint,
        "representative_principal_id": REPRESENTATIVE, "evaluated_at": BASE + timedelta(hours=1),
        "effective_from": BASE + timedelta(minutes=1), "occurred_at": BASE + timedelta(minutes=2),
        "idempotency_key": "idempotency:final-p25r", "representative_eligibility_reference": "eligibility:p25r",
        "representative_eligibility_fingerprint": HEX_A, "source_evidence_reference": "evidence:final-p25r",
        "source_evidence_fingerprint": HEX_B, "requested_scope_capabilities": ("ADVISORY",),
    }
    values.update(overrides)
    return LegalClientMatterFinalRepresentationFormationRequest(**values)


def _authority_variant(source: LegalClientMatterRepresentationAuthority, suffix: str) -> LegalClientMatterRepresentationAuthority:
    """Reconstruct a second valid P1 row with the same exact context."""
    payload = source.to_dict()
    payload.update(
        authority_id=f"authority-p25r-{suffix}",
        source_evidence_reference=f"evidence:authority-p25r-{suffix}",
        authorization_evidence_reference=f"evidence:authority-auth-p25r-{suffix}",
        idempotency_key=f"idempotency:authority-p25r-{suffix}",
    )
    payload.pop("fingerprint", None)
    return LegalClientMatterRepresentationAuthority(**cast(Any, payload))


def _decision_variant(source: LegalClientMatterRepresentationAuthority, suffix: str) -> LegalClientMatterRepresentationFirmDecision:
    """Construct a second legal P2 ACCEPTED decision for ambiguity evidence."""
    return LegalClientMatterRepresentationFirmDecision.from_client_authority(
        client_authority=source, decision="ACCEPTED", decision_actor_principal_id=f"principal-firm-{suffix}",
        authorization_evidence_reference=f"evidence:decision-auth-{suffix}", authorization_evidence_fingerprint=HEX_A,
        source_evidence_reference=f"evidence:decision-{suffix}", source_evidence_fingerprint=HEX_B,
        occurred_at=BASE - timedelta(minutes=9), effective_from=BASE - timedelta(minutes=4),
        idempotency_key=f"idempotency:decision-{suffix}",
    )


def _form_commit(context: MongoContext, request: LegalClientMatterFinalRepresentationFormationRequest) -> Any:
    with context.client.start_session() as session:
        session.start_transaction()
        result = _orchestrator(context).form(request, session=session)
        assert session.in_transaction is True
        session.commit_transaction()
        return result


def _count(context: MongoContext, key: str) -> int:
    return context.raw[key].count_documents({"tenant_id": TENANT})


def test_real_topology_database_and_indexes_are_sanctioned(mongo_context: MongoContext) -> None:
    hello = mongo_context.client.admin.command("hello")
    assert hello.get("setName") == REPLICA_SET
    assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    assert mongo_context.server_version == MONGO_VERSION
    assert mongo_context.database.name != "wilsy" and len(mongo_context.database.name) <= 63
    assert pymongo.version
    assert mongo_context.raw["final"].index_information()


def test_missing_and_inactive_sessions_fail_closed(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    request = _request(bundle)
    orchestrator = _orchestrator(mongo_context)
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError):
        orchestrator.form(request, session=None)
    with mongo_context.client.start_session() as session:
        with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError):
            orchestrator.form(request, session=session)


@pytest.mark.parametrize("role", ["LEGAL_ATTORNEY", "LEGAL_PARTNER"])
def test_real_attorney_and_partner_happy_paths_bind_and_persist(mongo_context: MongoContext, role: str) -> None:
    bundle = _seed(mongo_context, role=role)
    result = _form_commit(mongo_context, _request(bundle))
    assert result.tenant_id == TENANT
    assert result.representative_principal_id == REPRESENTATIVE
    assert result.representative_role == role
    assert result.representation_scope_capabilities == ("ADVISORY",)
    assert _count(mongo_context, "final") == 1


def test_exact_session_is_propagated_and_upstreams_are_read_only(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    for collection in mongo_context.collections.values():
        collection.session_ids.clear()
    before = {key: mongo_context.raw[key].count_documents({}) for key in ("matter", "grant", "acknowledgment", "mandate", "engagement", "authority", "decision")}
    _form_commit(mongo_context, _request(bundle))
    observed = {sid for collection in mongo_context.collections.values() for sid in collection.session_ids}
    assert len(observed) == 1
    after = {key: mongo_context.raw[key].count_documents({}) for key in before}
    assert after == before


def test_scope_intersection_narrows_and_widening_rejects(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    narrowed = _form_commit(mongo_context, _request(bundle, requested_scope_capabilities=("ADVISORY",)))
    assert narrowed.representation_scope_capabilities == ("ADVISORY",)
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError):
        _form_commit(mongo_context, _request(bundle, idempotency_key="idempotency:wide", requested_scope_capabilities=("NEGOTIATION",)))


def test_exact_replay_is_one_durable_p24_and_divergence_fails(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    first = _form_commit(mongo_context, _request(bundle))
    replay = _form_commit(mongo_context, _request(bundle))
    assert replay.to_dict() == first.to_dict()
    assert _count(mongo_context, "final") == 1
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError):
        _form_commit(mongo_context, _request(bundle, requested_scope_capabilities=("ADVISORY", "NEGOTIATION")))
    assert _count(mongo_context, "final") == 1


@pytest.mark.parametrize("authority_decision", ["DECLINED", "REQUIRES_REVIEW"])
def test_non_positive_p1_currentness_states_fail_closed(mongo_context: MongoContext, authority_decision: str) -> None:
    """P1 negative truth is seeded without manufacturing an impossible P2."""
    bundle = _seed(mongo_context, authority_decision=authority_decision, firm_decision=None)
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError) as raised:
        _form_commit(mongo_context, _request(bundle))
    assert raised.value.code == "L9C11_P25_P1_APPOINTED_REQUIRED"
    assert _count(mongo_context, "final") == 0


@pytest.mark.parametrize("firm_decision", ["DECLINED", "REQUIRES_REVIEW"])
def test_non_positive_p2_currentness_states_fail_closed(mongo_context: MongoContext, firm_decision: str) -> None:
    bundle = _seed(mongo_context, authority_decision="APPOINTED", firm_decision=firm_decision)
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError):
        _form_commit(mongo_context, _request(bundle))
    assert _count(mongo_context, "final") == 0


def test_p1_ambiguous_state_fails_closed(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    duplicate = _authority_variant(bundle["authority"], "ambiguous")
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            authority_registry.persist_representation_authority(duplicate, mongo_context.raw["authority"], session=session)
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError):
        _form_commit(mongo_context, _request(bundle))
    assert _count(mongo_context, "final") == 0



def test_p1_corrupt_state_fails_closed_at_p21a(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            mongo_context.raw["authority"].insert_one({
                "tenant_id": TENANT, "case_matter_id": bundle["matter"].case_matter_id,
                "matter_fingerprint": bundle["matter"].fingerprint, "client_party_id": bundle["mandate"].client_party_id,
                "subject_identity_fingerprint": bundle["mandate"].subject_identity_fingerprint,
                "representative_principal_id": REPRESENTATIVE, "authority_id": "authority-corrupt-p25r",
            }, session=session)
    with pytest.raises(LegalClientMatterRepresentationAuthorityCurrentnessComposerError) as raised:
        _form_commit(mongo_context, _request(bundle))
    assert raised.value.code == "L9C11_P21A_COMPOSER_HISTORY_READ_FAILED"
    assert _count(mongo_context, "final") == 0


def test_p2_ambiguous_state_fails_closed(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    duplicate = _decision_variant(bundle["authority"], "ambiguous")
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            decision_registry.persist_firm_decision(duplicate, mongo_context.raw["decision"], session=session)
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError):
        _form_commit(mongo_context, _request(bundle))
    assert _count(mongo_context, "final") == 0



def test_p2_corrupt_state_fails_closed(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            mongo_context.raw["decision"].insert_one({
                "tenant_id": TENANT, "case_matter_id": bundle["matter"].case_matter_id,
                "matter_fingerprint": bundle["matter"].fingerprint, "client_party_id": bundle["mandate"].client_party_id,
                "subject_identity_fingerprint": bundle["mandate"].subject_identity_fingerprint,
                "representation_authority_id": bundle["authority"].authority_id,
                "representation_authority_fingerprint": bundle["authority"].fingerprint,
                "representative_principal_id": REPRESENTATIVE, "decision_id": "decision-corrupt-p25r",
            }, session=session)
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionCurrentnessComposerError) as raised:
        _form_commit(mongo_context, _request(bundle))
    assert raised.value.code == "L9C11_P22_COMPOSER_HISTORY_READ_FAILED"
    assert _count(mongo_context, "final") == 0


def test_missing_upstream_rows_fail_closed_without_final_write(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            mongo_context.raw["authority"].delete_many({"tenant_id": TENANT}, session=session)
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError):
        _form_commit(mongo_context, _request(bundle))
    assert _count(mongo_context, "final") == 0


@pytest.mark.parametrize("missing_key", ["authority", "decision", "engagement", "mandate"])
def test_each_missing_upstream_lane_fails_closed(mongo_context: MongoContext, missing_key: str) -> None:
    """Every P1/P2/P3/P4 source is required and never synthesized by P25."""
    bundle = _seed(mongo_context)
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            mongo_context.raw[missing_key].delete_many({"tenant_id": TENANT}, session=session)
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError):
        _form_commit(mongo_context, _request(bundle))
    assert _count(mongo_context, "final") == 0


def test_wrong_tenant_and_wrong_matter_fail_closed(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError):
        _form_commit(mongo_context, _request(bundle, tenant_id=OTHER_TENANT))
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError):
        _form_commit(mongo_context, _request(bundle, case_matter_id="matter-other-p25r"))
    assert _count(mongo_context, "final") == 0


def test_final_registry_hydrates_exact_binding_after_commit(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    formed = _form_commit(mongo_context, _request(bundle))
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        hydrated = final_registry.get_final_representation(TENANT, formed.representation_id, mongo_context.raw["final"], session=session)
        session.commit_transaction()
    assert hydrated.to_dict() == formed.to_dict()
    assert hydrated.representation_authority_id == bundle["authority"].authority_id
    assert hydrated.firm_representation_decision_id == bundle["decision"].decision_id
    assert hydrated.engagement_id == bundle["engagement"].engagement_id
    assert hydrated.mandate_id == bundle["mandate"].mandate_id


def test_other_tenant_has_no_final_representation_oracle(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    formed = _form_commit(mongo_context, _request(bundle))
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(final_registry.LegalClientMatterFinalRepresentationRegistryNotFoundError):
            final_registry.get_final_representation(OTHER_TENANT, formed.representation_id, mongo_context.raw["final"], session=session)
        session.abort_transaction()


def test_role_binding_corruption_is_not_accepted_as_authority(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            mongo_context.raw["authority"].update_one({"authority_id": bundle["authority"].authority_id}, {"$set": {"representative_role": "LEGAL_PARTNER"}}, session=session)
    with pytest.raises(LegalClientMatterRepresentationAuthorityCurrentnessComposerError) as raised:
        _form_commit(mongo_context, _request(bundle))
    assert raised.value.code == "L9C11_P21A_COMPOSER_HISTORY_READ_FAILED"
    assert _count(mongo_context, "final") == 0


def test_inactive_or_missing_iam_fails_closed(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    with mongo_context.client.start_session() as session:
        with session.start_transaction():
            mongo_context.raw["assignment"].update_one({"principal_id": REPRESENTATIVE}, {"$set": {"status": "REVOKED"}}, session=session)
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError):
        _form_commit(mongo_context, _request(bundle))
    assert _count(mongo_context, "final") == 0


def test_temporal_request_and_clock_boundary_are_fail_closed(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    with pytest.raises(LegalClientMatterFinalRepresentationOrchestrationError):
        _form_commit(mongo_context, _request(bundle, occurred_at=BASE - timedelta(minutes=1)))
    source = inspect.getsource(LegalClientMatterFinalRepresentationOrchestrator)
    assert "datetime.now" not in source and "datetime.utcnow" not in source


def test_caller_abort_rolls_back_p24_and_preserves_upstreams(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    with pytest.raises(RuntimeError):
        with mongo_context.client.start_session() as session:
            session.start_transaction()
            _orchestrator(mongo_context).form(_request(bundle), session=session)
            raise RuntimeError("synthetic caller abort")
    assert _count(mongo_context, "final") == 0
    assert _count(mongo_context, "authority") == 1 and _count(mongo_context, "decision") == 1


def test_p25_has_no_downstream_authority_and_one_p24_write(mongo_context: MongoContext) -> None:
    bundle = _seed(mongo_context)
    _form_commit(mongo_context, _request(bundle))
    assert _count(mongo_context, "final") == 1
    assert mongo_context.raw["grant_lifecycle"].count_documents({}) == 0
    assert "currentness" not in final_registry.COLLECTION


# ARTIFACT: test_legal_client_matter_final_representation_orchestrator_real_mongo.py
# VERSION: v1.0.0-L9C11-P25R-FINAL-REPRESENTATION-ORCHESTRATOR-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable P25 formation runtime evidence only
# TENANT POSTURE: exact tenant and same-session propagation across all lanes
# FAIL-CLOSED POSTURE: missing/inactive prerequisites, widening and rollback failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
