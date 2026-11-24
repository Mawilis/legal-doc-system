"""TITLE: WILSY OS Disposable Company Document Certificate Fixture.
VERSION: v1.2.0-GOVERNED-READER-AND-CURRENTNESS-CERT
AUTHORITY: Test-owned UUID Mongo database only; no production IAM/content writes.
EPITOME: Add explicit reader/author/publisher principals to the canonical company
scope inside an isolated database, then independently verify browser publications.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/company_document_cert_fixture.py
COLLABORATION / OWNERSHIP: Existing browser runner owns URI, base fixture and cleanup.
CERTIFICATION / UPDATE DATE: 2026-11-14
CHANGELOG: v1.2.0-GOVERNED-READER-AND-CURRENTNESS-CERT adds an independent eligible
grantor, scoped currentness actors, exact disposable challenges and audit readback.
Prior certification seeds an explicitly synthetic legacy
Legal entitlement and independent Operations entitlement, then verifies their
immutable truth survives company navigation separation. All prior gates remain.
CHANGELOG: v1.0.0-COMPANY-DOCUMENT-DISPOSABLE-CERT adds isolated source IAM and
read-only revision/receipt verification without changing the base fixture.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identities and visibly synthetic content only.
TENANT BOUNDARY: Canonical company identifier is used only in UUID-owned database.
AUTHORITY BOUNDARY: Explicit test grants never assign production permissions.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively; no financial commands.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from browser_cert_fixture import (
    _owned_database, _uri, kernel_db, AuthRegistry, TenantRegistry,
    _approved_documents, LegalAgreementType, AcceptanceMethod, LegalAcceptanceEvidence, LegalAcceptanceRegistry,
    PrincipalAuthority, PrincipalAuthorityRepository, PrincipalStatus,
    TenantMembershipAuthority, TenantMembershipStatus, TenantMembershipRepository,
    TenantBusinessRoleAuthority, TenantBusinessRoleStatus, TenantBusinessRoleRepository,
    RoleAssignmentAuthority, RoleAssignmentStatus, RoleAssignmentRepository,
)
from tools.eos.auth.company_document_reader_grant import CompanyDocumentReaderGrant
from tools.eos.auth.authorization_role_revocation_evidence_registry import AuthorizationRoleRevocationEvidenceRegistry
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID
from tools.eos.saas.domain.tenant_product_entitlement import create_tenant_product_entitlement, TenantProductEntitlementState
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import derive_tenant_product_entitlement_id
from tools.eos.saas.entitlement import tenant_product_entitlement_registry as product_registry

from tools.eos.saas.company_operating_document_registry import (
    CompanyOperatingDocumentRegistry, COMMAND_COLLECTION, REVISION_COLLECTION,
)
from tools.eos.saas.domain.company_operating_document import CompanyDocumentClass, CompanyDocumentState


def seed(state_path: Path) -> None:
    """Add separately authorized synthetic company capacities in owned fixture only."""
    state = json.loads(state_path.read_text())
    with MongoClient(_uri(), serverSelectionTimeoutMS=5000, tz_aware=True) as client:
        database = _owned_database(client)
        if database.name != state["database_name"]:
            raise RuntimeError("COMPANY_CERT_DATABASE_MISMATCH")
        connected, _ = kernel_db.connect_db(force_reconnect=True)
        if not connected:
            raise RuntimeError("COMPANY_CERT_DATABASE_UNAVAILABLE")
        TenantRegistry.create({"tenant_id": WILSY_COMPANY_TENANT_ID,
            "name": "Synthetic Company Document Certificate", "alias": "company-document-cert-" + uuid4().hex,
            "industry": "Technology", "region": "ZA", "status": "ACTIVE", "verified": True})
        registry = AuthRegistry()
        now = datetime.now(timezone.utc)
        actors = {}
        for key, grants in {
            "reader": ["COMPANY_DOCUMENT_READER"],
            "author": ["COMPANY_DOCUMENT_AUTHOR", "COMPANY_DOCUMENT_PUBLISHER"],
            "publisher": ["COMPANY_DOCUMENT_PUBLISHER"],
            "founder_label": [],
            "grantor": ["ENTERPRISE_ADMIN"],
            "stale_session": ["COMPANY_DOCUMENT_READER"],
            "revoked_member": ["COMPANY_DOCUMENT_READER"],
            "revoked_capacity": ["COMPANY_DOCUMENT_READER"],
        }.items():
            user = registry.register_user(email="company-cert-" + key + "-" + uuid4().hex + "@example.com",
                password="Synthetic-" + uuid4().hex + "!", firstName="Synthetic", lastName=key,
                role="TENANT_OWNER", tenantId=WILSY_COMPANY_TENANT_ID)
            database["users"].update_one({"user_id": user.id}, {"$set": {"mfaRegistered": True}})
            with client.start_session() as session:
                with session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True)):
                    PrincipalAuthorityRepository.create(PrincipalAuthority(user.id, PrincipalStatus.ACTIVE, 0), database["principal_authorities"], session=session)
                    TenantMembershipRepository.insert(TenantMembershipAuthority(user.id, WILSY_COMPANY_TENANT_ID, TenantMembershipStatus.ACTIVE, 0), database["tenant_memberships"], session=session)
                    TenantBusinessRoleRepository.insert(TenantBusinessRoleAuthority(user.id, WILSY_COMPANY_TENANT_ID, "tenant_admin" if key == "grantor" else "tenant_owner", TenantBusinessRoleStatus.ACTIVE, 0, now, None), database["tenant_business_roles"], session=session)
                    for role in ["TENANT_OWNER", *grants]:
                        RoleAssignmentRepository.insert(RoleAssignmentAuthority(user.id, WILSY_COMPANY_TENANT_ID, role, RoleAssignmentStatus.ACTIVE, 0), database["role_assignments"], session=session)
                    for document in _approved_documents(now):
                        method = AcceptanceMethod.ACKNOWLEDGEMENT if document.agreement_type is LegalAgreementType.INSTITUTIONAL_CHARTER else AcceptanceMethod.ACCEPTANCE
                        digest = LegalAcceptanceEvidence.fingerprint_payload(tenant_id=WILSY_COMPANY_TENANT_ID,
                            principal_id=user.id, agreement_type=document.agreement_type, document_id=document.document_id,
                            document_version=document.version, document_sha3_512=document.sha3_512,
                            acceptance_method=method, locale="en-ZA")
                        evidence = LegalAcceptanceEvidence(acceptance_id="COMPANY-CERT-" + uuid4().hex,
                            tenant_id=WILSY_COMPANY_TENANT_ID, principal_id=user.id, agreement_type=document.agreement_type,
                            document_id=document.document_id, document_version=document.version,
                            document_sha3_512=document.sha3_512, accepted_at=now, acceptance_method=method,
                            actor_role_at_acceptance="tenant_owner", session_id="company-cert:" + user.id,
                            locale="en-ZA", authority_representation="authenticated_user_acknowledgement_only",
                            evidence_fingerprint=digest, idempotency_key="company-cert:" + user.id + ":" + document.document_id)
                        LegalAcceptanceRegistry.create_or_replay(evidence, database["legal_acceptance_evidence"],
                            idempotency_key=evidence.idempotency_key, session=session)
            current = registry.get_user_by_id(user.id)
            if current is None:
                raise RuntimeError("COMPANY_CERT_ACTOR_READBACK_MISSING")
            actors[key] = {"principal_id": user.id, "access_token": registry.create_session(current).token}
        CompanyOperatingDocumentRegistry(database).provision_indexes()
        CompanyDocumentReaderGrant(database).evidence.ensure_indexes()
        AuthorizationRoleRevocationEvidenceRegistry(database["authorization_role_revocation_evidence"]).ensure_indexes()
        product_evidence = {}
        with client.start_session() as session:
            with session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True)):
                for product in (TenantProductId.LEGAL_OPERATIONS, TenantProductId.OPERATIONS):
                    entitlement_id = derive_tenant_product_entitlement_id(WILSY_COMPANY_TENANT_ID, product)
                    pending = create_tenant_product_entitlement(tenant_id=WILSY_COMPANY_TENANT_ID,
                        entitlement_id=entitlement_id, product_id=product,
                        source_evidence_reference="SYNTHETIC-LEGACY-PRODUCT-TEST", source_evidence_fingerprint="d" * 128)
                    product_registry.create_or_replay(pending, database[product_registry.HISTORY_COLLECTION], database[product_registry.CURRENT_COLLECTION], session=session)
                    active = product_registry.transition(tenant_id=WILSY_COMPANY_TENANT_ID, entitlement_id=entitlement_id,
                        target_state=TenantProductEntitlementState.ACTIVE, expected_revision=0,
                        evidence_reference="SYNTHETIC-PRODUCT-ACTIVATION", evidence_fingerprint="e" * 128,
                        occurred_at=now, history_collection=database[product_registry.HISTORY_COLLECTION],
                        current_collection=database[product_registry.CURRENT_COLLECTION], session=session)
                    product_evidence[product.value] = {"entitlement_id": entitlement_id, "fingerprint": active.entitlement.fingerprint}
        state["company_documents"] = {"tenant_id": WILSY_COMPANY_TENANT_ID, "actors": actors, "product_evidence": product_evidence}
        state_path.write_text(json.dumps(state, sort_keys=True))


def verify(database, state) -> None:
    """Rehydrate exactly two independently published synthetic browser documents.

    No fixture publication is seeded. All six revisions and six durable command
    receipts must originate from the UI journey and match source lineage/actors.
    """
    company = state["company_documents"]
    if company["tenant_id"] != WILSY_COMPANY_TENANT_ID:
        raise RuntimeError("COMPANY_CERT_TENANT_INVALID")
    registry = CompanyOperatingDocumentRegistry(database)
    registry.require_command_indexes()
    with database.client.start_session() as session:
        with session.start_transaction(read_concern=ReadConcern("snapshot")):
            for product in (TenantProductId.LEGAL_OPERATIONS, TenantProductId.OPERATIONS):
                expected = company["product_evidence"][product.value]
                existing = product_registry.get_current(WILSY_COMPANY_TENANT_ID, expected["entitlement_id"],
                    database[product_registry.HISTORY_COLLECTION], database[product_registry.CURRENT_COLLECTION], session=session)
                if existing.lifecycle_state is not TenantProductEntitlementState.ACTIVE or existing.fingerprint != expected["fingerprint"]:
                    raise RuntimeError("PLATFORM_OWNER_CERT_ENTITLEMENT_MUTATED")
            for classification in CompanyDocumentClass:
                history = registry.history(WILSY_COMPANY_TENANT_ID, classification, session=session)
                if len(history) != 3 or [item.state for item in history] != [CompanyDocumentState.DRAFT, CompanyDocumentState.SUBMITTED, CompanyDocumentState.PUBLISHED]:
                    raise RuntimeError("COMPANY_CERT_PUBLICATION_LINEAGE_MISSING")
                document = registry.current(WILSY_COMPANY_TENANT_ID, classification, session=session, now=datetime.now(timezone.utc))
                if document is None or document.author_principal_id != company["actors"]["author"]["principal_id"] or document.approved_by_principal_id != company["actors"]["publisher"]["principal_id"]:
                    raise RuntimeError("COMPANY_CERT_INDEPENDENT_APPROVAL_MISSING")
                if document.title != "Synthetic browser " + classification.lower() or document.sections[0].body != "Synthetic certification content only. This is not WILSY policy." or document.approval_reference != "SYNTHETIC-BROWSER-APPROVAL":
                    raise RuntimeError("COMPANY_CERT_UI_CONTENT_MISMATCH")
                receipts = list(database[COMMAND_COLLECTION].find({"tenant_id": WILSY_COMPANY_TENANT_ID, "classification": classification.value}, session=session))
                if len(receipts) != 3 or {item["response_fingerprint"] for item in receipts} != {item.fingerprint for item in history}:
                    raise RuntimeError("COMPANY_CERT_DURABLE_RECEIPTS_MISSING")
                for item in receipts:
                    from uuid import UUID
                    if str(UUID(item["idempotency_key"])) != item["idempotency_key"]:
                        raise RuntimeError("COMPANY_CERT_UI_IDEMPOTENCY_INVALID")
            target = company["actors"]["founder_label"]["principal_id"]
            assignment = RoleAssignmentRepository.resolve(target, WILSY_COMPANY_TENANT_ID,
                "COMPANY_DOCUMENT_READER", database["role_assignments"], session=session)
            if assignment.status is not RoleAssignmentStatus.REVOKED or assignment.revision != 1:
                raise RuntimeError("COMPANY_CERT_READER_REVOCATION_NOT_DURABLE")
            audit = CompanyDocumentReaderGrant(database).evidence.find_by_idempotency(
                tenant_id=WILSY_COMPANY_TENANT_ID, idempotency_key="company-reader-grant:synthetic-browser-grant", session=session)
            if audit is None or audit.principal_id != company["actors"]["grantor"]["principal_id"] or audit.business_role != "tenant_admin" or audit.authorization_role != "ENTERPRISE_ADMIN":
                raise RuntimeError("COMPANY_CERT_READER_AUDIT_NOT_DURABLE")
            if database["tenant_authorization_decision_evidence"].count_documents({"tenant_id": WILSY_COMPANY_TENANT_ID}, session=session) != 2:
                raise RuntimeError("COMPANY_CERT_GRANT_REVOKE_EVIDENCE_COUNT_INVALID")
            if database[REVISION_COLLECTION].count_documents({}, session=session) != 6 or database[COMMAND_COLLECTION].count_documents({}, session=session) != 6:
                raise RuntimeError("COMPANY_CERT_UNEXPECTED_MUTATION")
            if database["employees"].count_documents({"$or": [{"tenant_id": WILSY_COMPANY_TENANT_ID}, {"tenantId": WILSY_COMPANY_TENANT_ID}]}, session=session):
                raise RuntimeError("COMPANY_CERT_EMPLOYMENT_MUTATION")


def challenge(state_path: Path, kind: str) -> None:
    """Mutate only a designated synthetic currentness actor in UUID-owned storage.

    Never accepts arbitrary tenant, principal, URI or update operators. This is
    test infrastructure, not an API or canonical repair mechanism.
    """
    if kind not in {"stale_session", "revoked_member", "revoked_capacity"}:
        raise RuntimeError("COMPANY_CERT_CHALLENGE_NOT_ALLOWED")
    state = json.loads(state_path.read_text())
    company = state["company_documents"]
    actor = company["actors"][kind]["principal_id"]
    with MongoClient(_uri(), serverSelectionTimeoutMS=5000, tz_aware=True) as client:
        database = _owned_database(client)
        if database.name != state["database_name"] or company["tenant_id"] != WILSY_COMPANY_TENANT_ID:
            raise RuntimeError("COMPANY_CERT_CHALLENGE_SCOPE_INVALID")
        scope = {"principal_id": actor, "tenant_id": WILSY_COMPANY_TENANT_ID}
        if kind == "stale_session":
            result = database["sessions"].delete_many({"user_id": actor, "tenant_id": WILSY_COMPANY_TENANT_ID})
            if result.deleted_count != 1:
                raise RuntimeError("COMPANY_CERT_SESSION_NOT_FOUND")
        elif kind == "revoked_member":
            result = database["tenant_memberships"].update_one({**scope, "revision": 0, "status": "ACTIVE"},
                {"$set": {"status": "REVOKED", "revision": 1}})
            if result.modified_count != 1:
                raise RuntimeError("COMPANY_CERT_MEMBERSHIP_NOT_FOUND")
        else:
            result = database["tenant_business_roles"].update_one({**scope, "revision": 0, "status": "ACTIVE"},
                {"$set": {"status": "REVOKED", "revision": 1, "revoked_at": datetime.now(timezone.utc)}})
            if result.modified_count != 1:
                raise RuntimeError("COMPANY_CERT_CAPACITY_NOT_FOUND")


def main() -> None:
    """Seed or verify only the runner-selected disposable certification database."""
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("seed", "verify", "challenge"))
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--kind", choices=("stale_session", "revoked_member", "revoked_capacity"))
    args = parser.parse_args()
    if args.action == "challenge":
        challenge(args.state, args.kind)
    elif args.action == "seed":
        seed(args.state)
    else:
        with MongoClient(_uri(), serverSelectionTimeoutMS=5000, tz_aware=True) as client:
            verify(_owned_database(client), json.loads(args.state.read_text()))
    print("COMPANY_DOCUMENT_CERT_" + args.action.upper() + "_PASSED")


if __name__ == "__main__":
    main()

# ARTIFACT: company_document_cert_fixture.py
# VERSION: v1.2.0-GOVERNED-READER-AND-CURRENTNESS-CERT
# AUTHORITY BOUNDARY: Explicit disposable setup and read-only verification only.
# TENANT POSTURE: Exact company scope inside UUID-owned database only.
# FAIL-CLOSED POSTURE: Incomplete lineage, receipts or independent actors reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
