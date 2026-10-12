"""Real-Mongo certificate for L8-8H Legal recipient authority and resolution.

TITLE: Legal Notification Recipient Resolution Real-Mongo Certificate
VERSION: v1.1.0-L8-8H-RECIPIENT-RESOLUTION-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certifies canonical return-to-matter resolution, durable explicit
         recipient binding and current IAM revalidation on a real replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_notification_recipient_resolution_real_mongo.py
COLLABORATION / OWNERSHIP: Certificate only; P1/P2, L8-8F, L8-8H and IAM retain authority.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.1.0 certifies append-only revocation/supersession currentness and
           removal of unverifiable source-authority fields.
           v1.0.0 establishes real indexes, transaction/replay/rollback,
           isolation, ambiguity, stale IAM, corruption and no-contact proofs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic database; opaque IDs only.
TENANT BOUNDARY: Every binding, source and membership assertion is exact scoped.
AUTHORITY BOUNDARY: Recipient authority certificate only; no dispatch or contact lookup.
TRANSACTION BOUNDARY: Certificate owns transactions; production layers do not.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Any topology, integrity, isolation or ambiguity failure fails.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.domain.legal_notification_recipient_binding import LegalNotificationEvent, LegalNotificationRecipientBinding
from tools.eos.legal_operations.domain.legal_notification_recipient_binding_lifecycle import revoke_binding, supersede_binding
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter, LegalInstruction, ProcessDocument, ReturnOfService, ServiceAttempt, ServiceAttemptState, ServiceExecution
from tools.eos.legal_operations.orchestration.legal_notification_recipient_resolution_orchestrator import LegalNotificationRecipientResolutionError, resolve_legal_notification_recipient
from tools.eos.legal_operations.orchestration.legal_return_ready_notification_issuance_orchestrator import issue_return_ready_notification
from tools.eos.legal_operations.registry.legal_notification_recipient_binding_registry import BINDING_IDENTITY_INDEX, COLLECTION as BINDING_COLLECTION, EFFECTIVE_SCOPE_INDEX, LegalNotificationRecipientBindingRegistry
from tools.eos.legal_operations.registry.legal_notification_recipient_binding_lifecycle_registry import COLLECTION as BINDING_LIFECYCLE_COLLECTION, LegalNotificationRecipientBindingLifecycleRegistry
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.legal_return_ready_notification_registry import COLLECTION as NOTIFICATION_COLLECTION, LegalReturnReadyNotificationRegistry

VERSION = "v1.1.0-L8-8H-RECIPIENT-RESOLUTION-REAL-MONGO-CERT"
MONGO_URI = os.environ.get("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
BASE = datetime(2026, 10, 12, 8, 0, tzinfo=timezone.utc)
FP = "a" * 128


@pytest.fixture()
def mongo() -> Iterator[tuple[MongoClient[Any], dict[str, Any]]]:
    """Yield majority-backed UUID-isolated collections on a writable replica set."""
    client: MongoClient[Any] = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000, socketTimeoutMS=10000, retryWrites=True)
    hello = client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS" and hello.get("isWritablePrimary", hello.get("ismaster")) is True
    db = client[f"wilsy_l8_8h_recipient_{uuid4().hex}"]
    names = {"lifecycle": "legal_operations_lifecycle_evidence", "notifications": NOTIFICATION_COLLECTION, "bindings": BINDING_COLLECTION, "binding_lifecycle": BINDING_LIFECYCLE_COLLECTION, "principals": "principal_authorities", "memberships": "tenant_memberships"}
    collections = {name: db.get_collection(value, write_concern=WriteConcern(w="majority", j=True), read_concern=ReadConcern("majority")) for name, value in names.items()}
    LegalOperationsLifecycleRegistry.ensure_indexes(collections["lifecycle"])
    LegalReturnReadyNotificationRegistry.ensure_indexes(collections["notifications"])
    LegalNotificationRecipientBindingRegistry(collections["bindings"]).ensure_indexes()
    LegalNotificationRecipientBindingLifecycleRegistry(collections["binding_lifecycle"]).ensure_indexes()
    PrincipalAuthorityRepository.ensure_indexes(collections["principals"])
    TenantMembershipRepository.ensure_indexes(collections["memberships"])
    try:
        yield client, collections
    finally:
        client.drop_database(db.name); client.close()


def _tx(client: MongoClient[Any], work: Any, *, commit: bool = True) -> Any:
    """Run bounded certificate work inside one explicit transaction."""
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
        result = work(session)
        session.commit_transaction() if commit else session.abort_transaction()
        return result


def _seed(client: MongoClient[Any], c: dict[str, Any], *, tenant: str = "tenant-l8-8h", suffix: str = "1") -> tuple[str, str]:
    """Persist the exact matter/document/instruction/return/intent and current IAM chain."""
    matter = CaseMatter(tenant_id=tenant, case_matter_id=f"matter-{suffix}", matter_reference=f"MAT-{suffix}", opened_at=BASE, evidence_reference=f"matter:{suffix}")
    instruction = LegalInstruction(tenant_id=tenant, instruction_id=f"instruction-{suffix}", case_matter_id=matter.case_matter_id, document_id=f"document-{suffix}", registered_at=BASE, evidence_reference=f"instruction:{suffix}")
    document = ProcessDocument(tenant_id=tenant, document_id=instruction.document_id, case_matter_id=matter.case_matter_id, document_type="RETURN_OF_SERVICE", registered_at=BASE, registration_evidence_reference=f"document:{suffix}")
    allocated = ServiceAttempt(tenant_id=tenant, attempt_id=f"attempt-{suffix}", instruction_id=instruction.instruction_id, document_id=document.document_id, deputy_id=f"deputy-{suffix}", allocated_at=BASE, allocation_evidence_reference=f"allocation:{suffix}")
    attempted = allocated.transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference=f"attempt:{suffix}", occurred_at=BASE + timedelta(minutes=1))
    terminal = attempted.transition_to(ServiceAttemptState.COMPLETED, evidence_reference=f"service:{suffix}", evidence_fingerprint=FP, occurred_at=BASE + timedelta(minutes=2))
    execution = ServiceExecution.from_attempt(attempt=terminal, service_execution_id=f"execution-{suffix}", executed_at=BASE + timedelta(minutes=3))
    returned = ReturnOfService.from_service_execution(instruction_id=instruction.instruction_id, service_execution=execution, return_id=f"return-{suffix}", generated_at=BASE + timedelta(minutes=4))
    principal_id = f"recipient-{suffix}"
    def persist(session: Any) -> None:
        for value in (matter, instruction, document, allocated, attempted, terminal):
            LegalOperationsLifecycleRegistry.create(value, c["lifecycle"], session=session)
        LegalOperationsLifecycleRegistry.create(execution, c["lifecycle"], session=session, source_attempt=terminal)
        LegalOperationsLifecycleRegistry.create(returned, c["lifecycle"], session=session, source_attempt=terminal, source_execution=execution)
        PrincipalAuthorityRepository.create(PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0), c["principals"], session=session)
        TenantMembershipRepository.insert(TenantMembershipAuthority(principal_id, tenant, TenantMembershipStatus.ACTIVE, 0), c["memberships"], session=session)
    _tx(client, persist)
    row = c["lifecycle"].find_one({"tenant_id": tenant, "entity_type": "ReturnOfService", "entity_identity": returned.return_id})
    assert row is not None
    notification_id = f"notification-{suffix}"
    _tx(client, lambda session: issue_return_ready_notification(tenant_id=tenant, return_evidence_identity=row["evidence_identity"], notification_id=notification_id, lifecycle_collection=c["lifecycle"], notification_collection=c["notifications"], session=session))
    return notification_id, principal_id


def _binding(principal_id: str, *, tenant: str = "tenant-l8-8h", suffix: str = "1") -> LegalNotificationRecipientBinding:
    """Create one explicit synthetic recipient decision."""
    return LegalNotificationRecipientBinding(tenant_id=tenant, binding_id=f"binding-{suffix}", case_matter_id=f"matter-{suffix.split('-')[0]}", event=LegalNotificationEvent.RETURN_READY, recipient_principal_id=principal_id, effective_from=BASE + timedelta(minutes=5), effective_until=None, created_by_principal_id="principal-admin", created_at=BASE + timedelta(minutes=4))


def _resolve(client: MongoClient[Any], c: dict[str, Any], notification_id: str, tenant: str = "tenant-l8-8h", at: datetime = BASE + timedelta(minutes=6)) -> Any:
    return _tx(client, lambda session: resolve_legal_notification_recipient(tenant_id=tenant, notification_id=notification_id, resolved_at=at, lifecycle_collection=c["lifecycle"], notification_collection=c["notifications"], binding_collection=c["bindings"], binding_lifecycle_collection=c["binding_lifecycle"], principal_collection=c["principals"], membership_collection=c["memberships"], session=session))


def test_real_mongo_recipient_authority_chain_replay_indexes_isolation_and_no_contact(mongo: tuple[MongoClient[Any], dict[str, Any]]) -> None:
    """Certify the complete bounded chain and durable authority posture."""
    client, c = mongo; notification_id, principal_id = _seed(client, c); binding = _binding(principal_id)
    def persist(session: Any) -> None:
        registry = LegalNotificationRecipientBindingRegistry(c["bindings"])
        assert registry.create_or_replay(binding, session=session) == binding
        assert registry.create_or_replay(binding, session=session) == binding
    _tx(client, persist)
    result = _resolve(client, c, notification_id)
    assert result.recipient_principal_id == principal_id and result.case_matter_id == "matter-1"
    assert c["bindings"].count_documents({}) == 1
    raw = c["bindings"].find_one({}); assert raw is not None
    assert not ({"email", "phone", "address", "channel", "provider", "message"} & set(raw))
    indexes = c["bindings"].index_information()
    assert indexes[BINDING_IDENTITY_INDEX]["unique"] is True
    assert EFFECTIVE_SCOPE_INDEX in indexes and all("expireAfterSeconds" not in meta for meta in indexes.values())
    with pytest.raises(LegalNotificationRecipientResolutionError):
        _resolve(client, c, notification_id, tenant="tenant-foreign")


def test_real_mongo_ambiguity_stale_iam_corruption_and_abort_fail_closed(mongo: tuple[MongoClient[Any], dict[str, Any]]) -> None:
    """Reject competing selection, inactive principals, corruption and aborted writes."""
    client, c = mongo; notification_id, principal_id = _seed(client, c)
    first = _binding(principal_id)
    _tx(client, lambda session: LegalNotificationRecipientBindingRegistry(c["bindings"]).create_or_replay(first, session=session))
    second_principal = "recipient-2"
    _tx(client, lambda session: (PrincipalAuthorityRepository.create(PrincipalAuthority(second_principal, PrincipalStatus.ACTIVE, 0), c["principals"], session=session), TenantMembershipRepository.insert(TenantMembershipAuthority(second_principal, "tenant-l8-8h", TenantMembershipStatus.ACTIVE, 0), c["memberships"], session=session), LegalNotificationRecipientBindingRegistry(c["bindings"]).create_or_replay(_binding(second_principal, suffix="1-second"), session=session)))
    with pytest.raises(LegalNotificationRecipientResolutionError, match="AMBIGUOUS"):
        _resolve(client, c, notification_id)
    c["bindings"].delete_one({"binding_id": "binding-1-second"})
    _tx(client, lambda session: PrincipalAuthorityRepository.compare_and_swap(PrincipalAuthority(principal_id, PrincipalStatus.SUSPENDED, 1), 0, c["principals"], session=session))
    with pytest.raises(LegalNotificationRecipientResolutionError, match="NOT_CURRENT"):
        _resolve(client, c, notification_id)
    before = c["bindings"].count_documents({})
    _tx(client, lambda session: LegalNotificationRecipientBindingRegistry(c["bindings"]).create_or_replay(_binding(principal_id, suffix="1-abort"), session=session), commit=False)
    assert c["bindings"].count_documents({}) == before
    c["bindings"].update_one({"binding_id": "binding-1"}, {"$set": {"fingerprint": "b" * 128}})
    with pytest.raises(LegalNotificationRecipientResolutionError):
        _resolve(client, c, notification_id)


def test_real_mongo_revocation_and_supersession_preserve_time_travel_currentness(mongo: tuple[MongoClient[Any], dict[str, Any]]) -> None:
    """Prove immutable withdrawal, exact successor selection and historical reads."""
    client, c = mongo; notification_id, first_principal = _seed(client, c)
    first = _binding(first_principal)
    second_principal = "recipient-successor"
    second = LegalNotificationRecipientBinding(tenant_id="tenant-l8-8h", binding_id="binding-successor", case_matter_id="matter-1", event=LegalNotificationEvent.RETURN_READY, recipient_principal_id=second_principal, effective_from=BASE + timedelta(minutes=8), effective_until=None, created_by_principal_id="principal-admin", created_at=BASE + timedelta(minutes=7))
    def persist(session: Any) -> None:
        PrincipalAuthorityRepository.create(PrincipalAuthority(second_principal, PrincipalStatus.ACTIVE, 0), c["principals"], session=session)
        TenantMembershipRepository.insert(TenantMembershipAuthority(second_principal, "tenant-l8-8h", TenantMembershipStatus.ACTIVE, 0), c["memberships"], session=session)
        registry = LegalNotificationRecipientBindingRegistry(c["bindings"])
        registry.create_or_replay(first, session=session); registry.create_or_replay(second, session=session)
        event = supersede_binding(lifecycle_event_id="supersede-1", target=first, successor=second, created_by_principal_id="principal-admin", created_at=BASE + timedelta(minutes=7))
        lifecycle = LegalNotificationRecipientBindingLifecycleRegistry(c["binding_lifecycle"])
        assert lifecycle.create_or_replay(event, session=session) == event
        assert lifecycle.create_or_replay(event, session=session) == event
    _tx(client, persist)
    assert _resolve(client, c, notification_id, at=BASE + timedelta(minutes=6)).recipient_principal_id == first_principal
    assert _resolve(client, c, notification_id, at=BASE + timedelta(minutes=8)).recipient_principal_id == second_principal
    assert c["bindings"].count_documents({}) == 2 and c["binding_lifecycle"].count_documents({}) == 1
    revoked = revoke_binding(lifecycle_event_id="revoke-successor", target=second, effective_at=BASE + timedelta(minutes=9), created_by_principal_id="principal-admin", created_at=BASE + timedelta(minutes=9))
    _tx(client, lambda session: LegalNotificationRecipientBindingLifecycleRegistry(c["binding_lifecycle"]).create_or_replay(revoked, session=session))
    with pytest.raises(LegalNotificationRecipientResolutionError, match="BINDING_UNAVAILABLE"):
        _resolve(client, c, notification_id, at=BASE + timedelta(minutes=10))

# ARTIFACT: test_legal_notification_recipient_resolution_real_mongo.py
# VERSION: v1.1.0-L8-8H-RECIPIENT-RESOLUTION-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo recipient authority verification only; no transport
# TENANT POSTURE: UUID database plus exact synthetic tenant scopes
# FAIL-CLOSED POSTURE: topology, integrity, ambiguity, IAM or rollback failure fails
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
