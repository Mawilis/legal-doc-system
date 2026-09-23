"""R1D-B0F-B4-R7 isolated real-Mongo certificate for acceptance evidence.

TITLE: Legal Acceptance Evidence Registry Real-Mongo Certificate
VERSION: v1.0.0-R1D-B0F-B4-R7-ACCEPTANCE-RM-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves append-only, tenant/principal-scoped acceptance evidence and
         deterministic replay against durable Mongo indexes.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_acceptance_registry_real_mongo.py
TENANT BOUNDARY: Every read and write is isolated to the authenticated tenant
                 and principal; certification data is UUID-isolated.
AUTHORITY BOUNDARY: User acknowledgement/acceptance evidence only; it cannot
                    bind an organisation or create signatory authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED: Wrong document material, divergent replay, and commercial
             execution attempts are rejected.
"""
from datetime import datetime, timezone
import os
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.domain.legal_acceptance import (
    AcceptanceMethod,
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
    canonical_document_digest,
)
from tools.eos.legal_operations.registry.legal_acceptance_registry import (
    LegalAcceptanceRegistry,
    LegalAcceptanceRegistryError,
)
from tools.eos.legal_operations.registry.legal_document_registry import LegalDocumentRegistry
from tools.eos.legal_operations.service.legal_acceptance_service import (
    LegalAcceptanceService,
    LegalAcceptanceServiceError,
)


URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 17, tzinfo=timezone.utc)


@pytest.fixture(scope="module")
def mongo_database():
    client = MongoClient(URI, serverSelectionTimeoutMS=3000, replicaSet=REPLICA_SET, retryWrites=True)
    try:
        hello = client.admin.command("hello")
    except PyMongoError as error:
        client.close()
        pytest.skip(f"R7 acceptance Mongo runtime unavailable: {type(error).__name__}")
    if hello.get("setName") != REPLICA_SET or not hello.get("isWritablePrimary", hello.get("ismaster", False)):
        client.close()
        pytest.skip("R7 acceptance certificate requires a writable certified replica set")
    name = "r7_legal_acceptance_" + uuid4().hex
    database = client.get_database(name, read_concern=ReadConcern("majority"), write_concern=WriteConcern(w="majority", j=True))
    try:
        yield client, database
    finally:
        client.drop_database(name)
        client.close()


def _identity(tenant_id: str, principal_id: str = "principal-r7", role: str = "USER") -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=principal_id,
        tenant_id=tenant_id,
        username=principal_id,
        email=f"{principal_id}@example.invalid",
        roles=[role],
        permissions=[],
        auth_method="JWT",
        status=PrincipalStatus.ACTIVE,
    )


def _document(family: LegalAgreementType = LegalAgreementType.USER_TERMS) -> LegalDocumentVersion:
    reference = "r7:approved:" + family.value
    content = "Approved isolated R7 legal document"
    return LegalDocumentVersion(
        document_id="DOC-R7-ACCEPT-" + family.value,
        agreement_type=family,
        version="1.0.0",
        title="R7 " + family.value,
        jurisdiction="ZA",
        locale="en-ZA",
        effective_from=NOW,
        status=LegalDocumentStatus.APPROVED,
        content_reference=reference,
        content=content,
        sha3_512=canonical_document_digest(content, reference),
        created_at=NOW,
    )


def test_acceptance_is_append_only_replay_safe_and_tenant_scoped(mongo_database):
    client, database = mongo_database
    documents = database["legal_document_versions"]
    acceptances = database["legal_acceptance_evidence"]
    memberships = database["tenant_memberships"]
    business_roles = database["tenant_business_roles"]

    LegalDocumentRegistry.ensure_indexes(documents)
    LegalAcceptanceRegistry.ensure_indexes(acceptances)
    TenantMembershipRepository.ensure_indexes(memberships)
    TenantBusinessRoleRepository.ensure_indexes(business_roles)

    identity = _identity("tenant-r7")

    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal_id=identity.identity_id,
            tenant_id=identity.tenant_id,
            status=TenantMembershipStatus.ACTIVE,
            revision=0,
        ),
        memberships,
    )
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            principal_id=identity.identity_id,
            tenant_id=identity.tenant_id,
            business_role="tenant_auditor",
            status=TenantBusinessRoleStatus.ACTIVE,
            revision=0,
            effective_at=NOW,
            revoked_at=None,
        ),
        business_roles,
    )

    class BoundMembershipRepository:
        @staticmethod
        def resolve(principal_id, tenant_id, *, session=None):
            return TenantMembershipRepository.resolve(
                principal_id,
                tenant_id,
                memberships,
                session=session,
            )

    class BoundBusinessRoleRepository:
        @staticmethod
        def resolve(principal_id, tenant_id, *, session=None):
            return TenantBusinessRoleRepository.resolve(
                principal_id,
                tenant_id,
                business_roles,
                session=session,
            )

    document = _document()
    LegalDocumentRegistry.register(document, documents)
    resolver = lambda tenant_id, **_: type("Tenant", (), {"tenant_id": tenant_id})()
    service = LegalAcceptanceService(
        documents,
        acceptances,
        resolver,
        membership_repository=BoundMembershipRepository(),
        business_role_repository=BoundBusinessRoleRepository(),
    )
    args = {
        "document_id": document.document_id,
        "document_version": document.version,
        "document_sha3_512": document.sha3_512,
        "acceptance_method": AcceptanceMethod.ACCEPTANCE,
        "idempotency_key": "r7-idempotency-1",
        "session_id": "r7-session-1",
    }
    with client.start_session() as session:
        session.start_transaction()
        first = service.accept(identity, session=session, **args)
        session.commit_transaction()
    replay = service.accept(identity, **args)
    assert replay["acceptanceId"] == first["acceptanceId"]
    assert acceptances.count_documents({"tenant_id": "tenant-r7", "principal_id": "principal-r7"}) == 1
    evidence = LegalAcceptanceRegistry.list_for_principal("tenant-r7", "principal-r7", acceptances)
    assert len(evidence) == 1
    assert evidence[0].evidence_fingerprint == first["evidenceFingerprint"]
    assert LegalAcceptanceRegistry.list_for_principal("other-tenant", "principal-r7", acceptances) == ()

    with pytest.raises(LegalAcceptanceServiceError, match="IDEMPOTENCY_CONFLICT"):
        service.accept(identity, **{**args, "acceptance_method": AcceptanceMethod.ACKNOWLEDGEMENT, "idempotency_key": "r7-idempotency-2"})
    with pytest.raises(LegalAcceptanceServiceError, match="DOCUMENT_NOT_APPROVED"):
        service.accept(identity, **{**args, "document_sha3_512": "0" * 128, "idempotency_key": "r7-idempotency-3"})
    with pytest.raises(LegalAcceptanceServiceError, match="DOCUMENT_NOT_APPROVED"):
        service.accept(_identity("tenant-r7"), **{**args, "document_version": "9.9.9", "idempotency_key": "r7-idempotency-4"})

    successor_reference = "r7:approved:USER_TERMS:1.1.0"
    successor_content = "Approved isolated R7 legal document successor"
    successor = LegalDocumentVersion(
        document_id=document.document_id,
        agreement_type=LegalAgreementType.USER_TERMS,
        version="1.1.0",
        title=document.title,
        jurisdiction=document.jurisdiction,
        locale=document.locale,
        effective_from=NOW,
        status=LegalDocumentStatus.APPROVED,
        content_reference=successor_reference,
        content=successor_content,
        sha3_512=canonical_document_digest(successor_content, successor_reference),
        created_at=NOW,
    )
    LegalDocumentRegistry.register(successor, documents)
    assert LegalDocumentRegistry.approved_for(LegalAgreementType.USER_TERMS, documents) == successor
    with pytest.raises(LegalAcceptanceServiceError, match="LEGAL_ACCEPTANCE_DOCUMENT_NOT_CURRENT"):
        service.accept(identity, **{**args, "idempotency_key": "r7-stale-approved"})

    commercial = _document(LegalAgreementType.MASTER_SUBSCRIPTION_AGREEMENT)
    LegalDocumentRegistry.register(commercial, documents)
    with pytest.raises(LegalAcceptanceServiceError, match="CORPORATE_EXECUTION_UNAVAILABLE"):
        service.accept(identity, document_id=commercial.document_id, document_version=commercial.version, document_sha3_512=commercial.sha3_512, acceptance_method=AcceptanceMethod.ACCEPTANCE, idempotency_key="r7-commercial", session_id="r7-session-1")

    raw = acceptances.find_one({"tenant_id": "tenant-r7"})
    assert raw is not None
    assert raw["authority_representation"] == "authenticated_user_acknowledgement_only"
    assert raw["actor_role_at_acceptance"] == "tenant_auditor"
    assert raw["actor_role_at_acceptance"] != "USER"
    assert "signatory" not in raw["authority_representation"].lower()
    assert "payment" not in str(raw).lower() and "settlement" not in str(raw).lower()
    with pytest.raises(LegalAcceptanceRegistryError, match="SCOPE_INVALID"):
        LegalAcceptanceRegistry.list_for_principal("", "principal-r7", acceptances)


# ARTIFACT: test_legal_acceptance_registry_real_mongo.py
# VERSION: v1.0.0-R1D-B0F-B4-R7-ACCEPTANCE-RM-CERT
# AUTHORITY BOUNDARY: isolated append-only acceptance evidence only
# END OF WILSY OS SOVEREIGN ARTIFACT
