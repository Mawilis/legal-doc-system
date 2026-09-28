"""Real-Mongo certificate for the L9C11-P20 client authority orchestrator.

TITLE: WILSY OS Legal Client Representation Authority Orchestrator Real-Mongo Certificate
VERSION: v1.0.0-L9C11-P20R-CLIENT-REPRESENTATION-AUTHORITY-ORCHESTRATOR-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove the published P20 orchestrator against a writable, UUID-isolated
         Mongo replica set: caller-owned transactions, exact session propagation,
         live prerequisite reads, atomic P17/P1 persistence, rollback, replay,
         divergent-idempotency rejection, tenant isolation and authority limits.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_representation_authority_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: P20 composes published P1/P7, P17/P18, IAM,
                            lifecycle, visibility, capacity and currentness
                            authorities. This certificate owns only disposable
                            runtime evidence; no production authority is added.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P20R certifies real replica-set topology, exact
           caller-session propagation, authenticated self-client prerequisites,
           P17/P1 atomicity, rollback, replay, divergent scope, negative gates,
           representative-role determinism and zero downstream authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; URI, credentials,
                             tokens and personal data are never printed.
TENANT BOUNDARY: Every source and write is exact-tenant scoped; canonical
                 database ``wilsy`` is prohibited.
AUTHORITY BOUNDARY: Client-side appointment orchestration evidence only. No firm
                    decision, final Representation, Court, HTTP/UI/Node or
                    financial authority is created.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for execution.
TRANSACTION BOUNDARY: The certificate owns disposable sessions and transactions;
                      P20 owns none and receives one exact active session.
FAIL-CLOSED DECLARATION: Topology, prerequisites, lineage, currentness, scope,
                         role, replay, persistence, rollback and cleanup failures
                         fail certification.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
import os
from typing import Any, Iterator, Mapping
from uuid import uuid4

import pymongo
import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    COLLECTION as PRINCIPAL_COLLECTION,
    PrincipalAuthorityRepository,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    COLLECTION as MEMBERSHIP_COLLECTION,
    TenantMembershipRepository,
)
from tools.eos.auth.role_assignment_repository import COLLECTION as ASSIGNMENT_COLLECTION
from tools.eos.legal_operations.domain.legal_client_acceptance import record_legal_client_acceptance
from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacityType,
    record_legal_client_acting_capacity,
)
from tools.eos.legal_operations.domain.legal_client_matter_acceptance_instrument import (
    record_legal_client_matter_acceptance_instrument,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    LegalClientMatterEngagement,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate import (
    LegalClientMatterMandate,
    LegalClientMatterMandateBreadth,
    LegalClientMatterMandateCapability,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment import (
    LegalClientMatterMandateAcknowledgment,
    LegalClientMatterMandateAcknowledgmentDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant import (
    LegalClientMatterMandateGrant,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authorization_evidence import (
    LegalClientMatterRepresentationAuthorizationEvidence,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    LegalClientMatterRepresentationAuthority,
)
from tools.eos.legal_operations.domain.legal_client_matter_visibility_binding import (
    LegalClientMatterVisibilityBinding,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_representation_authority_orchestrator import (
    LegalClientMatterRepresentationAuthorityOrchestrationError,
    LegalClientMatterRepresentationAuthorityOrchestrator,
    LegalClientMatterRepresentationAuthorityRequest,
)
from tools.eos.legal_operations.registry import (
    legal_client_acting_capacity_registry as capacity_registry,
    legal_client_matter_engagement_registry as engagement_registry,
    legal_client_matter_mandate_acknowledgment_registry as acknowledgment_registry,
    legal_client_matter_mandate_grant_registry as grant_registry,
    legal_client_matter_mandate_grant_lifecycle_registry as grant_lifecycle_registry,
    legal_client_matter_mandate_registry as mandate_registry,
    legal_client_matter_representation_authority_registry as authority_registry,
    legal_client_matter_representation_authorization_evidence_registry as evidence_registry,
    legal_client_matter_visibility_registry as visibility_registry,
    legal_matter_party_registry as party_registry,
    legal_operations_lifecycle_registry as matter_registry,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 28, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT = "tenant-real-p20"
OTHER_TENANT = "tenant-other-p20"
CLIENT = "principal-client-p20"
REPRESENTATIVE = "principal-representative-p20"
MATTER_ID = "matter-real-p20"
PARTY_ID = "party-real-p20"
CAPACITY_ID = "capacity-real-p20"
GRANT_ID = "grant-real-p20"
MANDATE_ID = "mandate-real-p20"
ENGAGEMENT_ID = "engagement-real-p20"
VISIBILITY_ID = "visibility-real-p20"
HEX_A = hashlib.sha3_512(b"p20-a").hexdigest()
HEX_B = hashlib.sha3_512(b"p20-b").hexdigest()
HEX_C = hashlib.sha3_512(b"p20-c").hexdigest()
HEX_D = hashlib.sha3_512(b"p20-d").hexdigest()
HEX_E = hashlib.sha3_512(b"p20-e").hexdigest()
CAPABILITIES: tuple[LegalClientMatterMandateCapability, ...] = (
    LegalClientMatterMandateCapability.ADVISORY,
    LegalClientMatterMandateCapability.NEGOTIATION,
)


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
    """Expose canonical repositories with injected disposable collections."""

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

    def list_assignments(self, *args: str, **kwargs: Any) -> Any:
        return RoleAssignmentRepository.list_assignments(
            args[0], args[1], self.collection, session=kwargs.get("session")
        )


@dataclass
class MongoContext:
    """Disposable database, raw collections and instrumented handles."""

    client: MongoClient[Any]
    database: Any
    raw: dict[str, Any]
    collections: dict[str, RecordingCollection]
    server_version: str


def _collections(database: Any) -> dict[str, Any]:
    return {
        "matter": database[matter_registry.COLLECTION],
        "party": database[party_registry.COLLECTION],
        "capacity": database[capacity_registry.COLLECTION],
        "visibility": database[visibility_registry.COLLECTION],
        "engagement": database[engagement_registry.COLLECTION],
        "mandate": database[mandate_registry.COLLECTION],
        "grant": database[grant_registry.COLLECTION],
        "grant_lifecycle": database[grant_lifecycle_registry.COLLECTION],
        "acknowledgment": database[acknowledgment_registry.COLLECTION],
        "evidence": database[evidence_registry.COLLECTION],
        "authority": database[authority_registry.COLLECTION],
        "principal": database[PRINCIPAL_COLLECTION],
        "membership": database[MEMBERSHIP_COLLECTION],
        "assignment": database[ASSIGNMENT_COLLECTION],
    }


def _ensure_indexes(raw: Mapping[str, Any]) -> None:
    PrincipalAuthorityRepository.ensure_indexes(raw["principal"])
    TenantMembershipRepository.ensure_indexes(raw["membership"])
    RoleAssignmentRepository.ensure_indexes(raw["assignment"])
    matter_registry.LegalOperationsLifecycleRegistry.ensure_indexes(raw["matter"])
    party_registry.ensure_indexes(raw["party"])
    capacity_registry.ensure_indexes(raw["capacity"])
    visibility_registry.LegalClientMatterVisibilityRegistry.ensure_indexes(raw["visibility"])
    engagement_registry.ensure_indexes(raw["engagement"])
    mandate_registry.ensure_indexes(raw["mandate"])
    grant_registry.ensure_indexes(raw["grant"])
    grant_lifecycle_registry.ensure_indexes(raw["grant_lifecycle"])
    acknowledgment_registry.ensure_indexes(raw["acknowledgment"])
    evidence_registry.ensure_indexes(raw["evidence"])
    authority_registry.ensure_indexes(raw["authority"])


@pytest.fixture()
def mongo_context() -> Iterator[MongoContext]:
    """Yield one UUID-isolated database on the sanctioned writable replica set."""
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
            server_version = client.server_info().get("version")
            with client.start_session() as probe:
                probe.start_transaction()
                assert probe.in_transaction is True
                probe.abort_transaction()
        except PyMongoError as error:
            pytest.skip(f"real Mongo unavailable for operator runtime: {type(error).__name__}")
        assert hello.get("setName") == REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert isinstance(server_version, str) and server_version
        database_name = f"wilsy_l9c11_p20r_{uuid4().hex}"
        assert len(database_name) <= 63
        assert database_name != "wilsy"
        database = client[database_name]
        raw = _collections(database)
        _ensure_indexes(raw)
        wrapped = {name: RecordingCollection(collection) for name, collection in raw.items()}
        yield MongoContext(client, database, raw, wrapped, str(server_version))
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _identity(*, tenant: str = TENANT, principal: str = CLIENT, status: PrincipalStatus = PrincipalStatus.ACTIVE) -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=principal,
        tenant_id=tenant,
        username=None,
        email=None,
        roles=[],
        permissions=[],
        auth_method="synthetic-real-mongo",
        status=status,
    )


def _seed(
    context: MongoContext,
    *,
    client_status: PrincipalStatus = PrincipalStatus.ACTIVE,
    membership_status: TenantMembershipStatus | None = TenantMembershipStatus.ACTIVE,
    representative_status: PrincipalStatus = PrincipalStatus.ACTIVE,
    representative_tenant: str = TENANT,
    representative_membership_status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    representative_roles: tuple[str, ...] = ("LEGAL_ATTORNEY", "LEGAL_PARTNER"),
    capacity_type: LegalClientActingCapacityType = LegalClientActingCapacityType.SELF,
    visibility: str = "ACTIVE",
    engagement_effective: datetime = BASE + timedelta(minutes=6),
    acknowledgment_decision: LegalClientMatterMandateAcknowledgmentDecision = LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED,
    matter_closed: bool = False,
) -> dict[str, Any]:
    """Persist a complete canonical prerequisite bundle through real registries."""
    matter = CaseMatter(
        tenant_id=TENANT,
        case_matter_id=MATTER_ID,
        matter_reference="matter-reference:p20",
        opened_at=BASE,
        evidence_reference="matter-source:p20",
    )
    party = register_legal_matter_party(
        matter=matter,
        party_id=PARTY_ID,
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=LegalMatterPartySide.CLIENT_SIDE,
        matter_role=LegalMatterPartyRole.CLIENT,
        subject_reference="client:subject-p20",
        subject_identity_fingerprint=HEX_A,
        display_name="Synthetic client P20",
        registered_at=BASE + timedelta(minutes=1),
        source_evidence_reference="party-source:p20",
        source_evidence_fingerprint=HEX_B,
    )
    capacity = record_legal_client_acting_capacity(
        case_matter=matter,
        party=party,
        capacity_id=CAPACITY_ID,
        principal_id=CLIENT,
        capacity_type=capacity_type,
        effective_from=BASE + timedelta(minutes=1),
        effective_until=BASE + timedelta(days=30),
        source_evidence_reference="capacity-source:p20",
        source_evidence_fingerprint=HEX_C,
    )
    grant = LegalClientMatterMandateGrant.from_canonical(
        client_grant_id=GRANT_ID,
        case_matter=matter,
        party=party,
        acting_capacity=capacity,
        breadth=LegalClientMatterMandateBreadth.LIMITED,
        scope_reference="scope:p20",
        scope_fingerprint=HEX_D,
        capabilities=CAPABILITIES,
        source_evidence_reference="grant-source:p20",
        source_evidence_fingerprint=HEX_E,
        authorization_evidence_reference="grant-authorization:p20",
        authorization_evidence_fingerprint=HEX_A,
        occurred_at=BASE + timedelta(minutes=1),
        effective_from=BASE + timedelta(minutes=2),
        effective_until=BASE + timedelta(days=30),
        idempotency_key="grant-idempotency:p20",
    )
    acknowledgment = LegalClientMatterMandateAcknowledgment.from_client_grant(
        client_grant=grant,
        acknowledgment_id="acknowledgment-real-p20",
        decision=acknowledgment_decision,
        decision_actor_principal_id=REPRESENTATIVE,
        authorization_evidence_reference="ack-authorization:p20",
        authorization_evidence_fingerprint=HEX_B,
        source_evidence_reference="ack-source:p20",
        source_evidence_fingerprint=HEX_C,
        occurred_at=BASE + timedelta(minutes=2),
        effective_from=BASE + timedelta(minutes=3),
        idempotency_key="acknowledgment-idempotency:p20",
    )
    mandate = LegalClientMatterMandate.from_canonical(
        mandate_id=MANDATE_ID,
        case_matter=matter,
        party=party,
        acting_capacity=capacity,
        breadth=LegalClientMatterMandateBreadth.LIMITED,
        scope_reference="scope:p20",
        scope_fingerprint=HEX_D,
        capabilities=CAPABILITIES,
        source_evidence_reference="mandate-source:p20",
        source_evidence_fingerprint=HEX_E,
        client_grant_reference=grant.client_grant_id,
        client_grant_fingerprint=grant.fingerprint,
        firm_acknowledgment_reference=acknowledgment.acknowledgment_id,
        firm_acknowledgment_fingerprint=acknowledgment.fingerprint,
        occurred_at=BASE + timedelta(minutes=3),
        effective_from=BASE + timedelta(minutes=4),
        effective_until=BASE + timedelta(days=30),
        idempotency_key="mandate-idempotency:p20",
    )
    acceptance = record_legal_client_acceptance(
        case_matter=matter,
        acceptance_id="acceptance-real-p20",
        party_id=party.party_id,
        subject_reference=party.subject_reference,
        subject_identity_fingerprint=party.subject_identity_fingerprint,
        acceptance_scope="client-review:p20",
        actor_principal_id=CLIENT,
        accepted_at=BASE + timedelta(minutes=4),
        source_evidence_reference="acceptance-source:p20",
        source_evidence_fingerprint=HEX_A,
    )
    instrument = record_legal_client_matter_acceptance_instrument(
        case_matter=matter,
        instrument_id="instrument-real-p20",
        version="1",
        instrument_kind="CLIENT_REVIEW_TERMS",
        title="Synthetic P20 client review instrument",
        review_scope="client-review:p20",
        content_reference="content:p20",
        content_fingerprint=HEX_B,
        created_at=BASE,
        effective_from=BASE + timedelta(minutes=1),
        approval_evidence_reference="instrument-approval:p20",
        approval_evidence_fingerprint=HEX_C,
    )
    engagement = LegalClientMatterEngagement.from_canonical(
        engagement_id=ENGAGEMENT_ID,
        case_matter=matter,
        party=party,
        acting_capacity=capacity,
        client_acceptance=acceptance,
        instrument=instrument,
        mandate_id=mandate.mandate_id,
        mandate_scope=mandate.scope_reference,
        mandate_fingerprint=mandate.fingerprint,
        conflict_disposition_id="conflict:p20",
        conflict_disposition_fingerprint=HEX_D,
        firm_decision_id="firm-decision:p20",
        decision_actor_principal_id=REPRESENTATIVE,
        firm_decision_fingerprint=HEX_E,
        authorization_evidence_reference="engagement-authorization:p20",
        authorization_evidence_fingerprint=HEX_A,
        source_evidence_reference="engagement-source:p20",
        source_evidence_fingerprint=HEX_B,
        effective_from=engagement_effective,
        idempotency_key="engagement-idempotency:p20",
    )
    visibility_binding = LegalClientMatterVisibilityBinding.grant(
        client_principal_id=CLIENT,
        case_matter=matter,
        granted_by_principal_id=REPRESENTATIVE,
        granted_at=BASE + timedelta(minutes=1),
        evidence_reference=VISIBILITY_ID,
    )
    revoked_binding = visibility_binding.revoke(
        revoked_by_principal_id=REPRESENTATIVE,
        revoked_at=BASE + timedelta(minutes=2),
        evidence_reference="visibility-revocation:p20",
    )
    closed_matter = matter.transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="matter-close:p20",
        occurred_at=BASE + timedelta(minutes=20),
    )
    with context.client.start_session() as session:
        with session.start_transaction():
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(CLIENT, client_status, 0), context.raw["principal"], session=session
            )
            if membership_status is not None:
                TenantMembershipRepository.insert(
                    TenantMembershipAuthority(CLIENT, TENANT, membership_status, 0),
                    context.raw["membership"], session=session,
                )
            for role in ("tenant_legal_client", "LEGAL_CLIENT"):
                RoleAssignmentRepository.insert(
                    RoleAssignmentAuthority(CLIENT, TENANT, role, RoleAssignmentStatus.ACTIVE, 0),
                    context.raw["assignment"], session=session,
                )
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(REPRESENTATIVE, representative_status, 0),
                context.raw["principal"], session=session,
            )
            TenantMembershipRepository.insert(
                TenantMembershipAuthority(REPRESENTATIVE, representative_tenant, representative_membership_status, 0),
                context.raw["membership"], session=session,
            )
            for role in representative_roles:
                RoleAssignmentRepository.insert(
                    RoleAssignmentAuthority(REPRESENTATIVE, representative_tenant, role, RoleAssignmentStatus.ACTIVE, 0),
                    context.raw["assignment"], session=session,
                )
            matter_registry.LegalOperationsLifecycleRegistry.create(
                matter, context.raw["matter"], session=session
            )
            if matter_closed:
                matter_registry.LegalOperationsLifecycleRegistry.create(
                    closed_matter, context.raw["matter"], session=session
                )
            party_registry.persist_party(party, context.raw["party"], session=session)
            capacity_registry.persist_capacity(capacity, context.raw["capacity"], session=session)
            grant_registry.persist_grant(grant, context.raw["grant"], session=session)
            acknowledgment_registry.persist_acknowledgment(
                acknowledgment, context.raw["acknowledgment"], session=session
            )
            mandate_registry.persist_mandate(mandate, context.raw["mandate"], session=session)
            engagement_registry.persist_engagement(engagement, context.raw["engagement"], session=session)
            if visibility == "ACTIVE":
                visibility_registry.LegalClientMatterVisibilityRegistry.grant(
                    visibility_binding, context.raw["visibility"], session=session
                )
            elif visibility == "REVOKED":
                visibility_registry.LegalClientMatterVisibilityRegistry.grant(
                    visibility_binding, context.raw["visibility"], session=session
                )
                visibility_registry.LegalClientMatterVisibilityRegistry.revoke(
                    revoked_binding, context.raw["visibility"], session=session
                )
    return {
        "matter": matter,
        "party": party,
        "capacity": capacity,
        "grant": grant,
        "mandate": mandate,
        "engagement": engagement,
        "visibility": visibility_binding,
    }


def _orchestrator(context: MongoContext, *, authority_persistence: Any = authority_registry) -> LegalClientMatterRepresentationAuthorityOrchestrator:
    c = context.collections
    principal = _RepositoryAdapter(c["principal"], "principal")
    membership = _RepositoryAdapter(c["membership"], "membership")
    assignments = _RepositoryAdapter(c["assignment"], "assignment")
    return LegalClientMatterRepresentationAuthorityOrchestrator(
        matter_lifecycle_collection=c["matter"],
        visibility_collection=c["visibility"],
        party_collection=c["party"],
        capacity_collection=c["capacity"],
        engagement_collection=c["engagement"],
        mandate_collection=c["mandate"],
        grant_collection=c["grant"],
        grant_lifecycle_collection=c["grant_lifecycle"],
        acknowledgment_collection=c["acknowledgment"],
        evidence_collection=c["evidence"],
        authority_collection=c["authority"],
        principal_repository=principal,
        membership_repository=membership,
        business_role_repository=assignments,
        role_assignment_repository=assignments,
        authority_persistence=authority_persistence,
    )


def _request(bundle: Mapping[str, Any], **overrides: Any) -> LegalClientMatterRepresentationAuthorityRequest:
    values: dict[str, Any] = {
        "tenant_id": TENANT,
        "case_matter_id": MATTER_ID,
        "client_party_id": PARTY_ID,
        "identity": _identity(),
        "representative_principal_id": REPRESENTATIVE,
        "mandate_id": MANDATE_ID,
        "representation_scope_capabilities": ("ADVISORY",),
        "occurred_at": BASE + timedelta(minutes=9),
        "effective_from": BASE + timedelta(minutes=10),
        "idempotency_key": "representation-idempotency:p20",
        "source_evidence_reference": "appointment-source:p20",
        "source_evidence_fingerprint": HEX_C,
    }
    values.update(overrides)
    return LegalClientMatterRepresentationAuthorityRequest(**values)


def _issue_and_commit(context: MongoContext, request: LegalClientMatterRepresentationAuthorityRequest, *, orchestrator: Any | None = None) -> LegalClientMatterRepresentationAuthority:
    value = orchestrator or _orchestrator(context)
    with context.client.start_session() as session:
        session.start_transaction()
        result = value.issue(request, session=session)
        assert session.in_transaction is True
        session.commit_transaction()
        return result


def _count(context: MongoContext, key: str) -> int:
    return context.raw[key].count_documents({"tenant_id": TENANT})


def test_real_topology_and_disposable_database_are_sanctioned(mongo_context: MongoContext) -> None:
    """Prove writable replica-set, sessions, transactions, and UUID isolation."""
    hello = mongo_context.client.admin.command("hello")
    assert hello.get("setName") == REPLICA_SET
    assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    assert mongo_context.server_version
    assert mongo_context.database.name != "wilsy"
    assert len(mongo_context.database.name) <= 63
    assert pymongo.version


def test_missing_and_inactive_transaction_rejected(mongo_context: MongoContext) -> None:
    """P20 requires the caller's active transaction and owns no lifecycle."""
    bundle = _seed(mongo_context)
    request = _request(bundle)
    orchestrator = _orchestrator(mongo_context)
    with pytest.raises(LegalClientMatterRepresentationAuthorityOrchestrationError):
        orchestrator.issue(request, session=None)
    with mongo_context.client.start_session() as session:
        with pytest.raises(LegalClientMatterRepresentationAuthorityOrchestrationError):
            orchestrator.issue(request, session=session)
        assert session.in_transaction is False


def test_real_happy_path_commits_p17_and_p1_with_exact_bindings(mongo_context: MongoContext) -> None:
    """One caller transaction persists exactly one evidence and one authority."""
    bundle = _seed(mongo_context)
    for value in mongo_context.collections.values():
        value.session_ids.clear()
    authority = _issue_and_commit(mongo_context, _request(bundle))
    assert _count(mongo_context, "evidence") == 1
    assert _count(mongo_context, "authority") == 1
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        evidence = evidence_registry.get_authorization_evidence(
            TENANT, authority.authorization_evidence_reference,
            mongo_context.raw["evidence"], session=session,
        )
        hydrated = authority_registry.get_representation_authority(
            TENANT, authority.authority_id, mongo_context.raw["authority"], session=session,
        )
        session.commit_transaction()
    assert isinstance(evidence, LegalClientMatterRepresentationAuthorizationEvidence)
    assert isinstance(hydrated, LegalClientMatterRepresentationAuthority)
    assert hydrated.authorization_evidence_reference == evidence.evidence_id
    assert hydrated.authorization_evidence_fingerprint == evidence.fingerprint
    assert hydrated.tenant_id == evidence.tenant_id == TENANT
    assert hydrated.case_matter_id == evidence.case_matter_id == MATTER_ID
    assert hydrated.matter_fingerprint == evidence.matter_fingerprint == bundle["matter"].fingerprint
    assert hydrated.client_party_id == evidence.client_party_id == PARTY_ID
    assert hydrated.subject_identity_fingerprint == evidence.subject_identity_fingerprint == bundle["party"].subject_identity_fingerprint
    assert hydrated.engagement_id == evidence.engagement_id == bundle["engagement"].engagement_id
    assert hydrated.engagement_fingerprint == evidence.engagement_fingerprint == bundle["engagement"].fingerprint
    assert hydrated.mandate_id == evidence.mandate_id == bundle["mandate"].mandate_id
    assert hydrated.mandate_fingerprint == evidence.mandate_fingerprint == bundle["mandate"].fingerprint
    assert hydrated.acting_capacity_id == evidence.acting_capacity_id == bundle["capacity"].capacity_id
    assert hydrated.acting_capacity_fingerprint == evidence.acting_capacity_fingerprint == bundle["capacity"].fingerprint
    assert hydrated.representative_principal_id == evidence.representative_principal_id == REPRESENTATIVE
    assert hydrated.representative_role == evidence.representative_role == "LEGAL_ATTORNEY"
    assert hydrated.representation_scope_capabilities == evidence.representation_scope_capabilities == ("ADVISORY",)
    observed = {session_id for value in mongo_context.collections.values() for session_id in value.session_ids}
    assert len(observed) == 1


def test_real_abort_rolls_back_both_p17_and_p1(mongo_context: MongoContext) -> None:
    """Caller abort removes both uncommitted authority records."""
    bundle = _seed(mongo_context)
    with pytest.raises(RuntimeError):
        with mongo_context.client.start_session() as session:
            session.start_transaction()
            _orchestrator(mongo_context).issue(_request(bundle), session=session)
            raise RuntimeError("synthetic caller abort")
    assert _count(mongo_context, "evidence") == 0
    assert _count(mongo_context, "authority") == 0


class _FailingAuthorityPersistence:
    """Bounded downstream failure used only to prove caller rollback."""

    @staticmethod
    def persist_representation_authority(value: object, collection: Any, *, session: Any) -> object:
        raise authority_registry.LegalClientMatterRepresentationAuthorityRegistryConflictError(
            "L9C11_P20_SYNTHETIC_AUTHORITY_CONFLICT"
        )


def test_p1_failure_after_evidence_write_leaves_no_partial_evidence(mongo_context: MongoContext) -> None:
    """A downstream P1 failure is contained by the caller transaction."""
    bundle = _seed(mongo_context)
    failing = _orchestrator(mongo_context, authority_persistence=_FailingAuthorityPersistence())
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        try:
            with pytest.raises(LegalClientMatterRepresentationAuthorityOrchestrationError):
                failing.issue(_request(bundle), session=session)
        finally:
            if session.in_transaction:
                session.abort_transaction()
        assert session.in_transaction is False
    assert _count(mongo_context, "evidence") == 0
    assert _count(mongo_context, "authority") == 0


def test_real_exact_replay_is_one_p17_row_and_one_p1_row(mongo_context: MongoContext) -> None:
    """The exact canonical request replays both immutable values."""
    bundle = _seed(mongo_context)
    first = _issue_and_commit(mongo_context, _request(bundle))
    replay = _issue_and_commit(mongo_context, _request(bundle))
    assert replay.to_dict() == first.to_dict()
    assert _count(mongo_context, "evidence") == 1
    assert _count(mongo_context, "authority") == 1


def test_real_divergent_scope_same_idempotency_fails_closed(mongo_context: MongoContext) -> None:
    """A changed representation scope cannot create a second durable truth."""
    bundle = _seed(mongo_context)
    first = _issue_and_commit(mongo_context, _request(bundle))
    with pytest.raises(LegalClientMatterRepresentationAuthorityOrchestrationError):
        _issue_and_commit(
            mongo_context,
            _request(bundle, representation_scope_capabilities=("NEGOTIATION",)),
        )
    assert _count(mongo_context, "evidence") == 1
    assert _count(mongo_context, "authority") == 1
    assert first.authority_id


@pytest.mark.parametrize(
    "identity,request_tenant",
    [
        (_identity(principal="principal-other-p20"), TENANT),
        (_identity(tenant=OTHER_TENANT, principal=CLIENT), OTHER_TENANT),
        (_identity(status=PrincipalStatus.SUSPENDED), TENANT),
    ],
)
def test_real_actor_tenant_and_inactive_identity_rejected(
    mongo_context: MongoContext, identity: SovereignIdentity, request_tenant: str
) -> None:
    """Wrong actor, wrong tenant and inactive client identity never write."""
    bundle = _seed(mongo_context)
    session = _active_session_for_test(mongo_context)
    try:
        with pytest.raises(LegalClientMatterRepresentationAuthorityOrchestrationError):
            _orchestrator(mongo_context).issue(
                _request(bundle, identity=identity, tenant_id=request_tenant),
                session=session,
            )
    finally:
        session.abort_transaction()
        session.end_session()
    assert _count(mongo_context, "evidence") == 0
    assert _count(mongo_context, "authority") == 0


def _active_session_for_test(context: MongoContext) -> Any:
    """Open an active session for a rejection test; caller ends it."""
    session = context.client.start_session()
    session.start_transaction()
    return session


@pytest.mark.parametrize(
    "seed_kwargs",
    [
        {"membership_status": None},
        {"membership_status": TenantMembershipStatus.SUSPENDED},
        {"matter_closed": True},
        {"visibility": "REVOKED"},
        {"capacity_type": LegalClientActingCapacityType.REPRESENTATIVE},
        {"engagement_effective": BASE + timedelta(hours=2)},
        {"acknowledgment_decision": LegalClientMatterMandateAcknowledgmentDecision.DECLINED},
    ],
)
def test_real_prerequisite_negative_gates_are_fail_closed(
    mongo_context: MongoContext, seed_kwargs: dict[str, Any]
) -> None:
    """Missing/stale matter, visibility, capacity or currentness writes nothing."""
    bundle = _seed(mongo_context, **seed_kwargs)
    session = _active_session_for_test(mongo_context)
    try:
        with pytest.raises(LegalClientMatterRepresentationAuthorityOrchestrationError):
            _orchestrator(mongo_context).issue(_request(bundle), session=session)
    finally:
        if session.in_transaction:
            session.abort_transaction()
        session.end_session()
    assert _count(mongo_context, "evidence") == 0
    assert _count(mongo_context, "authority") == 0


def test_real_wrong_client_party_rejected(mongo_context: MongoContext) -> None:
    """The exact client party is an authoritative matter binding."""
    bundle = _seed(mongo_context)
    session = _active_session_for_test(mongo_context)
    try:
        with pytest.raises(LegalClientMatterRepresentationAuthorityOrchestrationError):
            _orchestrator(mongo_context).issue(_request(bundle, client_party_id="party-other-p20"), session=session)
    finally:
        session.abort_transaction()
        session.end_session()
    assert _count(mongo_context, "evidence") == 0


@pytest.mark.parametrize(
    "roles,expected",
    [
        (("LEGAL_ATTORNEY",), "LEGAL_ATTORNEY"),
        (("LEGAL_PARTNER",), "LEGAL_PARTNER"),
        (("LEGAL_ATTORNEY", "LEGAL_PARTNER"), "LEGAL_ATTORNEY"),
    ],
)
def test_real_representative_eligibility_and_deterministic_selection(
    mongo_context: MongoContext, roles: tuple[str, ...], expected: str
) -> None:
    """Attorney/partner eligibility and lexical selection are canonical."""
    bundle = _seed(mongo_context, representative_roles=roles)
    result = _issue_and_commit(mongo_context, _request(bundle))
    assert result.representative_role == expected


@pytest.mark.parametrize(
    "seed_kwargs",
    [
        {"representative_roles": ("LEGAL_PARALEGAL",)},
        {"representative_status": PrincipalStatus.SUSPENDED},
        {"representative_tenant": OTHER_TENANT},
        {"representative_membership_status": TenantMembershipStatus.SUSPENDED},
    ],
)
def test_real_representative_negative_gates_are_fail_closed(
    mongo_context: MongoContext, seed_kwargs: dict[str, Any]
) -> None:
    """Paralegal-only, inactive and cross-tenant representatives are rejected."""
    bundle = _seed(mongo_context, **seed_kwargs)
    session = _active_session_for_test(mongo_context)
    try:
        with pytest.raises(LegalClientMatterRepresentationAuthorityOrchestrationError):
            _orchestrator(mongo_context).issue(_request(bundle), session=session)
    finally:
        session.abort_transaction()
        session.end_session()
    assert _count(mongo_context, "evidence") == 0
    assert _count(mongo_context, "authority") == 0


@pytest.mark.parametrize(
    "scope",
    [("TRANSACTIONAL",), ("COURT_FILING_PREPARATION",), ("PAYMENT_EXECUTION",)],
)
def test_real_scope_widening_court_and_finance_are_rejected(
    mongo_context: MongoContext, scope: tuple[str, ...]
) -> None:
    """P20 cannot widen Mandate scope or create Court/financial authority."""
    bundle = _seed(mongo_context)
    session = _active_session_for_test(mongo_context)
    try:
        with pytest.raises(LegalClientMatterRepresentationAuthorityOrchestrationError):
            _orchestrator(mongo_context).issue(
                _request(bundle, representation_scope_capabilities=scope), session=session
            )
    finally:
        session.abort_transaction()
        session.end_session()
    assert _count(mongo_context, "evidence") == 0
    assert _count(mongo_context, "authority") == 0


def test_real_p20_starts_no_transaction_commits_no_transaction_and_has_no_downstream_authority(
    mongo_context: MongoContext,
) -> None:
    """The caller remains transaction owner and no downstream rows appear."""
    bundle = _seed(mongo_context)
    orchestrator = _orchestrator(mongo_context)
    source = inspect.getsource(orchestrator.__class__)
    assert "start_transaction" not in source
    assert ".commit(" not in source
    assert ".abort(" not in source
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        result = orchestrator.issue(_request(bundle), session=session)
        assert session.in_transaction is True
        session.commit_transaction()
        assert result.is_appointing is True
    collections = set(mongo_context.database.list_collection_names())
    assert not collections.intersection(
        {
            "legal_client_matter_representation_firm_decisions",
            "legal_client_acceptances",
            "representations",
            "court_authorities",
            "financial_approvals",
        }
    )
    assert _count(mongo_context, "evidence") == 1
    assert _count(mongo_context, "authority") == 1


def test_real_p20_does_not_write_currentness_projection(mongo_context: MongoContext) -> None:
    """Currentness is consumed read-only; no currentness collection is created."""
    bundle = _seed(mongo_context)
    _issue_and_commit(mongo_context, _request(bundle))
    assert not {
        "legal_client_matter_engagement_currentness",
        "legal_client_matter_mandate_currentness",
    }.intersection(set(mongo_context.database.list_collection_names()))


def test_real_registry_rows_strictly_hydrate_after_commit(mongo_context: MongoContext) -> None:
    """Fresh-session registry reads prove strict durable cross-binding."""
    bundle = _seed(mongo_context)
    authority = _issue_and_commit(mongo_context, _request(bundle))
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        evidence = evidence_registry.get_authorization_evidence(
            TENANT, authority.authorization_evidence_reference,
            mongo_context.raw["evidence"], session=session,
        )
        persisted = authority_registry.get_representation_authority(
            TENANT, authority.authority_id, mongo_context.raw["authority"], session=session,
        )
        session.commit_transaction()
    assert persisted == authority
    assert evidence.evidence_id == persisted.authorization_evidence_reference
    assert evidence.fingerprint == persisted.authorization_evidence_fingerprint


# ARTIFACT: test_legal_client_matter_representation_authority_orchestrator_real_mongo.py
# VERSION: v1.0.0-L9C11-P20R-CLIENT-REPRESENTATION-AUTHORITY-ORCHESTRATOR-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable P20 orchestrator runtime evidence only
# TENANT POSTURE: UUID-isolated exact-tenant Mongo data; canonical wilsy excluded
# FAIL-CLOSED POSTURE: topology, transaction, prerequisite, rollback, replay and authority failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
