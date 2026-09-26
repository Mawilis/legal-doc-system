"""WILSY OS browser-certificate disposable authority fixture.

TITLE: Authenticated browser certificate fixture
VERSION: v1.0.0-L8-8M-R3-BROWSER-CERT-FIXTURE
AUTHORITY: Test-owned disposable Mongo fixture only.
EPITOME: Seed the existing EOS repositories with one authenticated legal
         operator and one REVIEW_REQUIRED conflict screening so Playwright can
         certify the real browser, HTTP, authorization, and persistence path.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/browser_cert_fixture.py
COLLABORATION / OWNERSHIP: L8-8M-R3 browser certificate; no production authority.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0 establishes UUID-isolated local-replica-set seeding and
           explicit cleanup. It never targets the configured production URI.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identities and credentials only; no
                            secret or token values are printed.
TENANT BOUNDARY: One generated tenant and principal; every fixture row is
                 scoped to that pair.
AUTHORITY BOUNDARY: Fixture setup only. It grants no production authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
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
from tools.eos.kernel import db as kernel_db
from tools.eos.legal_operations.domain.legal_acceptance import (
    AcceptanceMethod,
    LegalAcceptanceEvidence,
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
    canonical_document_digest,
)
from tools.eos.legal_operations.domain.legal_conflict_screening import (
    LegalConflictMatchKind,
    LegalConflictMatchSignal,
    LegalConflictScreeningResult,
    LegalConflictScreeningStatus,
)
from tools.eos.legal_operations.registry.legal_acceptance_registry import (
    LegalAcceptanceRegistry,
)
from tools.eos.legal_operations.registry.legal_document_registry import (
    LegalDocumentRegistry,
)
from tools.eos.legal_operations.registry.legal_conflict_review_registry import (
    LegalConflictReviewRegistry,
)
from tools.eos.legal_operations.registry.legal_conflict_screening_registry import (
    LegalConflictScreeningRegistry,
)
from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry


DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
STATE_VERSION = "v1.0.0-L8-8M-R3-BROWSER-CERT-STATE"


def _uri() -> str:
    value = os.getenv("BROWSER_CERT_MONGO_URI", "").strip()
    if not value or "mongodb+srv://" in value:
        raise RuntimeError("BROWSER_CERT_LOCAL_REPLICA_SET_URI_REQUIRED")
    return value


def _approved_documents(now: datetime) -> tuple[LegalDocumentVersion, ...]:
    values = (
        (LegalAgreementType.INSTITUTIONAL_CHARTER, "WILSY-OS-INSTITUTIONAL-CHARTER"),
        (LegalAgreementType.USER_TERMS, "WILSY-OS-USER-TERMS"),
        (LegalAgreementType.ACCEPTABLE_USE, "WILSY-OS-ACCEPTABLE-USE"),
        (LegalAgreementType.PRIVACY_NOTICE, "WILSY-OS-PRIVACY-NOTICE"),
        (LegalAgreementType.AI_ASSISTANCE_NOTICE, "WILSY-OS-AI-ASSISTANCE-NOTICE"),
    )
    result: list[LegalDocumentVersion] = []
    for agreement_type, document_id in values:
        reference = f"browser-cert://{document_id.lower()}/1.0.0-approved"
        content = (
            f"Synthetic browser certification document for {agreement_type.value}. "
            "It is not production legal text and grants no authority."
        )
        result.append(
            LegalDocumentVersion(
                document_id=document_id,
                agreement_type=agreement_type,
                version="1.0.0-APPROVED",
                title=f"Synthetic {agreement_type.value}",
                jurisdiction="ZA",
                locale="en-ZA",
                effective_from=now,
                status=LegalDocumentStatus.APPROVED,
                content_reference=reference,
                content=content,
                sha3_512=canonical_document_digest(content, reference),
                created_at=now,
            )
        )
    return tuple(result)


def _screening(tenant_id: str, suffix: str, now: datetime) -> LegalConflictScreeningResult:
    source_party_fingerprint = "a" * 128
    subject_fingerprint = "b" * 128
    matched_fingerprint = "c" * 128
    return LegalConflictScreeningResult(
        tenant_id=tenant_id,
        screening_id=f"browser-screening-{suffix}",
        source_party_id=f"browser-source-party-{suffix}",
        source_case_matter_id=f"browser-matter-{suffix}",
        source_party_fingerprint=source_party_fingerprint,
        subject_identity_fingerprint=subject_fingerprint,
        screened_at=now,
        status=LegalConflictScreeningStatus.REVIEW_REQUIRED,
        matches=(
            LegalConflictMatchSignal(
                tenant_id=tenant_id,
                subject_identity_fingerprint=subject_fingerprint,
                source_party_id=f"browser-source-party-{suffix}",
                source_case_matter_id=f"browser-matter-{suffix}",
                source_party_fingerprint=source_party_fingerprint,
                matched_party_id=f"browser-match-party-{suffix}",
                matched_case_matter_id=f"browser-match-matter-{suffix}",
                matched_party_fingerprint=matched_fingerprint,
                match_kind=LegalConflictMatchKind.CROSS_MATTER_EXACT_SUBJECT_MATCH,
            ),
        ),
        source_evidence_reference=f"browser-cert-screening:{suffix}",
        source_evidence_fingerprint=matched_fingerprint,
    )


def seed(state_path: Path) -> None:
    uri = _uri()
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, tz_aware=True)
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or not hello.get("isWritablePrimary"):
            raise RuntimeError("BROWSER_CERT_MONGO_REPLICA_SET_NOT_WRITABLE")
        database = client.get_database()
        connected, _ = kernel_db.connect_db(force_reconnect=True)
        if not connected or kernel_db.get_database() is None:
            raise RuntimeError("BROWSER_CERT_KERNEL_DATABASE_UNAVAILABLE")

        suffix = uuid4().hex
        tenant_id = f"browser-tenant-{suffix}"
        email = f"browser-{suffix}@example.com"
        # BSON stores datetimes at millisecond precision; freeze fixture time
        # to that exact boundary so immutable screening correlation survives
        # the durable write/readback certificate.
        current = datetime.now(timezone.utc)
        now = current.replace(microsecond=(current.microsecond // 1000) * 1000)

        TenantRegistry.create(
            {
                "tenant_id": tenant_id,
                "name": "Synthetic Browser Certification Tenant",
                "alias": f"browser-{suffix}",
                "industry": "Legal",
                "region": "ZA",
                "status": "ACTIVE",
                "verified": True,
            }
        )
        registry = AuthRegistry()
        user = registry.register_user(
            email=email,
            password=f"SyntheticBrowserPassword-{suffix}-2026!",
            firstName="Synthetic",
            lastName="Reviewer",
            role="LEGAL_PARTNER",
            tenantId=tenant_id,
        )
        # AuthRegistry's canonical principal identity is the durable user.id;
        # all IAM rows must bind to that exact value for authenticated reads.
        principal_id = user.id
        database["users"].update_one(
            {"user_id": user.id},
            {"$set": {"mfaRegistered": True}},
        )

        collections = {
            "principal": database["principal_authorities"],
            "membership": database["tenant_memberships"],
            "business": database["tenant_business_roles"],
            "roles": database["role_assignments"],
            "documents": database["legal_document_versions"],
            "acceptance": database["legal_acceptance_evidence"],
            "screening": database["legal_conflict_screenings"],
            "review": database["legal_conflict_reviews"],
        }
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        TenantBusinessRoleRepository.ensure_indexes(collections["business"])
        RoleAssignmentRepository.ensure_indexes(collections["roles"])
        LegalDocumentRegistry.ensure_indexes(collections["documents"])
        LegalAcceptanceRegistry.ensure_indexes(collections["acceptance"])
        LegalConflictScreeningRegistry.ensure_indexes(collections["screening"])
        LegalConflictReviewRegistry.ensure_indexes(collections["review"])

        with client.start_session() as session:
            session.start_transaction(
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
            )
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0),
                collections["principal"],
                session=session,
            )
            TenantMembershipRepository.insert(
                TenantMembershipAuthority(
                    principal_id,
                    tenant_id,
                    TenantMembershipStatus.ACTIVE,
                    0,
                ),
                collections["membership"],
                session=session,
            )
            TenantBusinessRoleRepository.insert(
                TenantBusinessRoleAuthority(
                    principal_id,
                    tenant_id,
                    "tenant_legal_partner",
                    TenantBusinessRoleStatus.ACTIVE,
                    0,
                    now,
                    None,
                ),
                collections["business"],
                session=session,
            )
            RoleAssignmentRepository.insert(
                RoleAssignmentAuthority(
                    principal_id,
                    tenant_id,
                    "LEGAL_PARTNER",
                    RoleAssignmentStatus.ACTIVE,
                    0,
                ),
                collections["roles"],
                session=session,
            )
            for document in _approved_documents(now):
                LegalDocumentRegistry.register(
                    document,
                    collections["documents"],
                    session=session,
                )
                acceptance_method = (
                    AcceptanceMethod.ACKNOWLEDGEMENT
                    if document.agreement_type is LegalAgreementType.INSTITUTIONAL_CHARTER
                    else AcceptanceMethod.ACCEPTANCE
                )
                fingerprint = LegalAcceptanceEvidence.fingerprint_payload(
                    tenant_id=tenant_id,
                    principal_id=principal_id,
                    agreement_type=document.agreement_type,
                    document_id=document.document_id,
                    document_version=document.version,
                    document_sha3_512=document.sha3_512,
                    acceptance_method=acceptance_method,
                    locale="en-ZA",
                )
                evidence = LegalAcceptanceEvidence(
                    acceptance_id=f"BROWSER-ACCEPT-{uuid4().hex}",
                    tenant_id=tenant_id,
                    principal_id=principal_id,
                    agreement_type=document.agreement_type,
                    document_id=document.document_id,
                    document_version=document.version,
                    document_sha3_512=document.sha3_512,
                    accepted_at=now,
                    acceptance_method=acceptance_method,
                    actor_role_at_acceptance="tenant_legal_partner",
                    session_id=f"browser-cert:{principal_id}",
                    locale="en-ZA",
                    authority_representation="authenticated_user_acknowledgement_only",
                    evidence_fingerprint=fingerprint,
                    idempotency_key=f"browser-cert:{document.document_id}",
                )
                LegalAcceptanceRegistry.create_or_replay(
                    evidence,
                    collections["acceptance"],
                    idempotency_key=evidence.idempotency_key,
                    session=session,
                )
            screening = _screening(tenant_id, suffix, now)
            LegalConflictScreeningRegistry.persist_screening(
                screening,
                collections["screening"],
                session=session,
            )
            session.commit_transaction()

        user = registry.get_user_by_id(user.id)
        if user is None:
            raise RuntimeError("BROWSER_CERT_USER_READBACK_FAILED")
        session = registry.create_session(user)
        state_path.write_text(
            json.dumps(
                {
                    "state_version": STATE_VERSION,
                    "database_name": database.name,
                    "tenant_id": tenant_id,
                    "principal_id": principal_id,
                    "email": email,
                    "access_token": session.token,
                    "screening_id": screening.screening_id,
                    "source_case_matter_id": screening.source_case_matter_id,
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
    finally:
        client.close()


def cleanup() -> None:
    uri = _uri()
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        client.drop_database(client.get_default_database().name)
    finally:
        client.close()


def verify(state_path: Path) -> None:
    uri = _uri()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        database = client.get_database()
        screening_count = database["legal_conflict_screenings"].count_documents(
            {"tenant_id": state["tenant_id"], "screening_id": state["screening_id"]}
        )
        review_count = database["legal_conflict_reviews"].count_documents(
            {"tenant_id": state["tenant_id"], "screening_id": state["screening_id"]}
        )
        if screening_count != 1 or review_count != 1:
            raise RuntimeError("BROWSER_CERT_DURABLE_REVIEW_CARDINALITY_INVALID")
    finally:
        client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Disposable browser-cert fixture")
    parser.add_argument("command", choices=("seed", "verify", "cleanup"))
    parser.add_argument("--state", type=Path)
    args = parser.parse_args()
    if args.command == "seed":
        if args.state is None:
            raise SystemExit("--state is required for seed")
        seed(args.state)
    elif args.command == "verify":
        if args.state is None:
            raise SystemExit("--state is required for verify")
        verify(args.state)
    else:
        cleanup()


if __name__ == "__main__":
    main()


# ARTIFACT: browser_cert_fixture.py
# VERSION: v1.0.0-L8-8M-R3-BROWSER-CERT-FIXTURE
# AUTHORITY BOUNDARY: disposable synthetic browser-cert fixture only
# TENANT POSTURE: one generated tenant/principal pair; no production data
# FAIL-CLOSED POSTURE: wrong URI, unavailable replica set, and seed failures stop
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
