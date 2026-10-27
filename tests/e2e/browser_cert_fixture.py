"""WILSY OS browser-certificate disposable authority fixture.

TITLE: Authenticated browser certificate fixture
VERSION: v1.3.0-PYTHON-EOS-LOGIN-MFA-BROWSER-CERT
AUTHORITY: Test-owned disposable Mongo fixture only.
EPITOME: Seed existing EOS repositories with disposable authenticated Legal
         operators, canonical Legal evidence, and a fully correlated current
         tenant-branding chain so Playwright can certify authenticated branding
         HTTP and browser delivery inside one disposable database.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/e2e/browser_cert_fixture.py
COLLABORATION / OWNERSHIP: L8-8M-R3 browser certificate; no production authority.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.3.0 adds ephemeral synthetic password and TOTP secret material to the
           private fixture state so Playwright can exercise the real Python EOS login/MFA
           flow; the values remain runner-local and are never printed.
           v1.2.0 seeds active canonical branding entitlement/profile/selection
           and PNG logo/favicon assets for the authenticated tenant-branding browser
           certificate, and limits seed/verify/cleanup to the runner-owned database.
           v1.1.1 bounds disposable multi-role passwords below bcrypt's 72-byte
           limit without changing authenticated-session or IAM semantics.
           v1.1.0 adds Partner, Attorney, Paralegal, Secretary and Legal Finance
           authenticated sessions plus one canonical matter for the D6B deadline
           browser certificate; no WILSY AI entitlement or deadline is seeded.
           v1.0.1 adds the canonical ACTIVE D22B5 LEGAL_OPERATIONS product
           entitlement required by the production workspace admission gate.
           v1.0.0 establishes UUID-isolated local-replica-set seeding and
           explicit cleanup. It never targets the configured production URI.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identities, credentials and image
                            bytes only; no token, credential, or image body is
                            printed, and cleanup is name-bounded to the runner DB.
TENANT BOUNDARY: One authenticated tenant/principal plus one foreign tenant
                 without membership; all rows remain within the runner database.
AUTHORITY BOUNDARY: Fixture setup only. It grants no production authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import argparse
import json
import os
import struct
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from typing import Any
from urllib.parse import parse_qs, urlsplit
import zlib

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
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
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
from tools.eos.legal_operations.registry.legal_matter_deadline_registry import (
    LegalMatterDeadlineRegistry,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)
from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
    create_tenant_product_entitlement,
)
from tools.eos.saas.entitlement import tenant_product_entitlement_registry as entitlement_registry
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
    derive_tenant_product_entitlement_id,
)
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry
from tools.eos.saas.billing import tenant_branding_asset_registry as branding_asset_registry
from tools.eos.saas.billing import tenant_branding_entitlement_registry as branding_entitlement_registry
from tools.eos.saas.billing import tenant_branding_profile_registry as branding_profile_registry
from tools.eos.saas.billing.tenant_branding_vas_policy import TenantBrandingTier
from tools.eos.saas.domain.tenant_branding_asset import (
    TenantBrandingAssetKind,
    register_tenant_branding_asset,
)
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlementState,
    create_tenant_branding_entitlement,
)
from tools.eos.saas.domain.tenant_branding_profile import (
    approve_tenant_branding_profile,
)
from tools.eos.saas.domain.tenant_branding_profile_selection import (
    select_tenant_branding_profile,
)


DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
STATE_VERSION = "v1.2.0-D21B13-AUTHENTICATED-BRANDING-BROWSER-CERT-STATE"
BROWSER_CERT_DATABASE_PREFIX = "wilsy_l8_8m_r3_"
BRANDING_EVIDENCE_FINGERPRINT = "f" * 128


def _png_pixel(red: int, green: int, blue: int) -> bytes:
    """Build a deterministic valid 1x1 RGBA PNG for disposable image evidence."""
    def chunk(kind: bytes, payload: bytes) -> bytes:
        checksum = zlib.crc32(kind + payload) & 0xFFFFFFFF
        return struct.pack("!I", len(payload)) + kind + payload + struct.pack("!I", checksum)

    header = struct.pack("!2I5B", 1, 1, 8, 6, 0, 0, 0)
    pixel = zlib.compress(bytes((0, red, green, blue, 255)))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", pixel)
        + chunk(b"IEND", b"")
    )


def _owned_database(client: MongoClient[Any]) -> Any:
    """Return only the UUID-isolated database created by the browser runner."""
    database = client.get_database()
    if not database.name.startswith(BROWSER_CERT_DATABASE_PREFIX):
        raise RuntimeError("BROWSER_CERT_DATABASE_NOT_OWNED")
    return database


def _uri() -> str:
    value = os.getenv("BROWSER_CERT_MONGO_URI", "").strip()
    parsed = urlsplit(value)
    query = parse_qs(parsed.query)
    if (
        parsed.scheme != "mongodb"
        or parsed.hostname not in {"127.0.0.1", "localhost"}
        or parsed.port != 27017
        or parsed.username is not None
        or parsed.password is not None
        or query.get("replicaSet") != ["wilsyVendorCertRS"]
    ):
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


def _seed_branding_chain(
    *,
    tenant_id: str,
    suffix: str,
    now: datetime,
    session: Any,
    collections: dict[str, Any],
    logo_color: tuple[int, int, int],
) -> dict[str, str]:
    """Persist one canonical current logo/favicon chain in the caller transaction."""
    logo_bytes = _png_pixel(*logo_color)
    favicon_bytes = _png_pixel(245, 158, 11)
    logo_reference = f"asset:{tenant_id}:logo:browser-cert"
    favicon_reference = f"asset:{tenant_id}:favicon:browser-cert"
    pending = create_tenant_branding_entitlement(
        tenant_id=tenant_id,
        entitlement_id=f"branding-entitlement-{suffix}",
        branding_tier=TenantBrandingTier.INSTITUTIONAL,
        source_evidence_reference=f"browser-branding-entitlement:{tenant_id}",
        source_evidence_fingerprint=BRANDING_EVIDENCE_FINGERPRINT,
    )
    logo_asset = register_tenant_branding_asset(
        tenant_id=tenant_id,
        asset_reference=logo_reference,
        asset_kind=TenantBrandingAssetKind.LOGO,
        media_type="image/png",
        content=logo_bytes,
        source_evidence_reference=f"browser-branding-logo:{tenant_id}",
        source_evidence_fingerprint=BRANDING_EVIDENCE_FINGERPRINT,
        registered_at=now,
    )
    favicon_asset = register_tenant_branding_asset(
        tenant_id=tenant_id,
        asset_reference=favicon_reference,
        asset_kind=TenantBrandingAssetKind.FAVICON,
        media_type="image/png",
        content=favicon_bytes,
        source_evidence_reference=f"browser-branding-favicon:{tenant_id}",
        source_evidence_fingerprint=BRANDING_EVIDENCE_FINGERPRINT,
        registered_at=now,
    )
    history = collections["branding_entitlement_history"]
    current = collections["branding_entitlement_current"]
    profiles = collections["branding_profiles"]
    selections = collections["branding_selections"]
    profile_current = collections["branding_profile_current"]
    assets = collections["branding_assets"]

    branding_entitlement_registry.create_or_replay(
        pending, history, current, session=session,
    )
    active = branding_entitlement_registry.transition(
        tenant_id=tenant_id,
        entitlement_id=pending.entitlement_id,
        target_state=TenantBrandingEntitlementState.ACTIVE,
        expected_revision=0,
        evidence_reference=f"browser-branding-activation:{tenant_id}",
        evidence_fingerprint=BRANDING_EVIDENCE_FINGERPRINT,
        occurred_at=now,
        history_collection=history,
        current_collection=current,
        session=session,
    ).entitlement
    branding_asset_registry.create_or_replay(
        logo_asset, logo_bytes, assets, session=session,
    )
    branding_asset_registry.create_or_replay(
        favicon_asset, favicon_bytes, assets, session=session,
    )
    profile = approve_tenant_branding_profile(
        entitlement=active,
        profile_id=f"branding-profile-{suffix}",
        profile_label="Synthetic Browser Certification Brand",
        source_evidence_reference=f"browser-branding-profile:{tenant_id}",
        source_evidence_fingerprint=BRANDING_EVIDENCE_FINGERPRINT,
        approved_at=now,
        approval_evidence_reference=f"browser-branding-approval:{tenant_id}",
        approval_evidence_fingerprint=BRANDING_EVIDENCE_FINGERPRINT,
        logo_asset_reference=logo_reference,
        logo_asset_fingerprint=logo_asset.content_fingerprint,
        primary_color="#2563EB",
        secondary_color="#1E3A8A",
        accent_color="#F59E0B",
        email_display_name="Synthetic Browser Certification Brand",
        favicon_asset_reference=favicon_reference,
        favicon_asset_fingerprint=favicon_asset.content_fingerprint,
    )
    branding_profile_registry.persist_profile(profile, profiles, session=session)
    selection = select_tenant_branding_profile(
        profile=profile,
        current_entitlement=active,
        selection_id=f"branding-selection-{suffix}",
        selection_revision=1,
        selected_at=now,
        selection_evidence_reference=f"browser-branding-selection:{tenant_id}",
        selection_evidence_fingerprint=BRANDING_EVIDENCE_FINGERPRINT,
    )
    branding_profile_registry.persist_selection_and_advance_current(
        selection,
        profiles,
        selections,
        profile_current,
        session=session,
    )
    return {
        "logo_reference": logo_reference,
        "logo_fingerprint": logo_asset.content_fingerprint,
        "favicon_reference": favicon_reference,
        "favicon_fingerprint": favicon_asset.content_fingerprint,
    }


def seed(state_path: Path) -> None:
    uri = _uri()
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, tz_aware=True)
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or not hello.get("isWritablePrimary"):
            raise RuntimeError("BROWSER_CERT_MONGO_REPLICA_SET_NOT_WRITABLE")
        database = _owned_database(client)
        connected, _ = kernel_db.connect_db(force_reconnect=True)
        if not connected or kernel_db.get_database() is None:
            raise RuntimeError("BROWSER_CERT_KERNEL_DATABASE_UNAVAILABLE")

        suffix = uuid4().hex
        tenant_id = f"browser-tenant-{suffix}"
        actor_specs = (
            ("partner", "LEGAL_PARTNER", "tenant_legal_partner", "Partner"),
            ("attorney", "LEGAL_ATTORNEY", "tenant_legal_attorney", "Attorney"),
            ("paralegal", "LEGAL_PARALEGAL", "tenant_legal_paralegal", "Paralegal"),
            ("secretary", "LEGAL_SECRETARY", "tenant_legal_secretary", "Secretary"),
            ("finance", "LEGAL_FINANCE", "tenant_legal_finance", "Finance"),
        )
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
        foreign_tenant_id = f"browser-foreign-{suffix}"
        TenantRegistry.create(
            {
                "tenant_id": foreign_tenant_id,
                "name": "Synthetic Foreign Branding Tenant",
                "alias": f"browser-foreign-{suffix}",
                "industry": "Legal",
                "region": "ZA",
                "status": "ACTIVE",
                "verified": True,
            }
        )
        registry = AuthRegistry()
        actors: dict[str, dict[str, str]] = {}
        for key, grant_role, business_role, last_name in actor_specs:
            email = f"browser-{key}-{suffix}@example.com"
            password = f"Bcert-{key}-{suffix[:12]}!"
            user = registry.register_user(
                email=email,
                password=password,
                firstName="Synthetic",
                lastName=last_name,
                role=grant_role,
                tenantId=tenant_id,
            )
            # Enroll a real disposable TOTP secret before setting the enrollment
            # flag so the browser can verify the actual password + MFA protocol.
            registry.get_otp_uri(user.id, email)
            otp_secret = registry.get_otp_secret(user.id)
            if not otp_secret:
                raise RuntimeError("BROWSER_CERT_OTP_SECRET_READBACK_FAILED")
            database["users"].update_one(
                {"user_id": user.id},
                {"$set": {"mfaRegistered": True}},
            )
            actors[key] = {
                "principal_id": user.id,
                "email": email,
                "password": password,
                "otp_secret": otp_secret,
                "grant_role": grant_role,
                "business_role": business_role,
            }

        collections = {
            "principal": database["principal_authorities"],
            "membership": database["tenant_memberships"],
            "business": database["tenant_business_roles"],
            "roles": database["role_assignments"],
            "documents": database["legal_document_versions"],
            "acceptance": database["legal_acceptance_evidence"],
            "screening": database["legal_conflict_screenings"],
            "review": database["legal_conflict_reviews"],
            "lifecycle": database["legal_operations_lifecycle_evidence"],
            "deadline": database["legal_matter_deadlines"],
            "entitlement_history": database["tenant_product_entitlement_history"],
            "entitlement_current": database["tenant_product_entitlement_current"],
            "branding_entitlement_history": database[branding_entitlement_registry.HISTORY_COLLECTION],
            "branding_entitlement_current": database[branding_entitlement_registry.CURRENT_COLLECTION],
            "branding_profiles": database[branding_profile_registry.PROFILE_COLLECTION],
            "branding_selections": database[branding_profile_registry.SELECTION_COLLECTION],
            "branding_profile_current": database[branding_profile_registry.CURRENT_COLLECTION],
            "branding_assets": database[branding_asset_registry.COLLECTION],
        }
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        TenantBusinessRoleRepository.ensure_indexes(collections["business"])
        RoleAssignmentRepository.ensure_indexes(collections["roles"])
        LegalDocumentRegistry.ensure_indexes(collections["documents"])
        LegalAcceptanceRegistry.ensure_indexes(collections["acceptance"])
        LegalConflictScreeningRegistry.ensure_indexes(collections["screening"])
        LegalConflictReviewRegistry.ensure_indexes(collections["review"])
        LegalOperationsLifecycleRegistry.ensure_indexes(collections["lifecycle"])
        LegalMatterDeadlineRegistry.ensure_indexes(collections["deadline"])
        entitlement_registry.ensure_indexes(
            collections["entitlement_history"],
            collections["entitlement_current"],
        )
        branding_entitlement_registry.ensure_indexes(
            collections["branding_entitlement_history"],
            collections["branding_entitlement_current"],
        )
        branding_profile_registry.ensure_indexes(
            collections["branding_profiles"],
            collections["branding_selections"],
            collections["branding_profile_current"],
        )
        branding_asset_registry.ensure_indexes(collections["branding_assets"])

        with client.start_session() as session:
            session.start_transaction(
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
            )
            for actor in actors.values():
                principal_id = actor["principal_id"]
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
                        actor["business_role"],
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
                        actor["grant_role"],
                        RoleAssignmentStatus.ACTIVE,
                        0,
                    ),
                    collections["roles"],
                    session=session,
                )
            entitlement_id = derive_tenant_product_entitlement_id(
                tenant_id,
                TenantProductId.LEGAL_OPERATIONS,
            )
            entitlement = create_tenant_product_entitlement(
                tenant_id=tenant_id,
                entitlement_id=entitlement_id,
                product_id=TenantProductId.LEGAL_OPERATIONS,
                source_evidence_reference=f"browser-cert-product:{tenant_id}",
                source_evidence_fingerprint="d" * 128,
            )
            entitlement_registry.create_or_replay(
                entitlement,
                collections["entitlement_history"],
                collections["entitlement_current"],
                session=session,
            )
            entitlement_registry.transition(
                tenant_id=tenant_id,
                entitlement_id=entitlement.entitlement_id,
                target_state=TenantProductEntitlementState.ACTIVE,
                expected_revision=0,
                evidence_reference=f"browser-cert-product-activation:{tenant_id}",
                evidence_fingerprint="e" * 128,
                occurred_at=now,
                history_collection=collections["entitlement_history"],
                current_collection=collections["entitlement_current"],
                session=session,
            )
            branding = _seed_branding_chain(
                tenant_id=tenant_id,
                suffix=suffix,
                now=now,
                session=session,
                collections=collections,
                logo_color=(37, 99, 235),
            )
            foreign_branding = _seed_branding_chain(
                tenant_id=foreign_tenant_id,
                suffix=f"foreign-{suffix}",
                now=now,
                session=session,
                collections=collections,
                logo_color=(220, 38, 38),
            )
            documents = _approved_documents(now)
            for document in documents:
                LegalDocumentRegistry.register(
                    document,
                    collections["documents"],
                    session=session,
                )
            for actor in actors.values():
                principal_id = actor["principal_id"]
                for document in documents:
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
                        actor_role_at_acceptance=actor["business_role"],
                        session_id=f"browser-cert:{principal_id}",
                        locale="en-ZA",
                        authority_representation="authenticated_user_acknowledgement_only",
                        evidence_fingerprint=fingerprint,
                        idempotency_key=f"browser-cert:{principal_id}:{document.document_id}",
                    )
                    LegalAcceptanceRegistry.create_or_replay(
                        evidence,
                        collections["acceptance"],
                        idempotency_key=evidence.idempotency_key,
                        session=session,
                    )
            matter_id = f"browser-matter-{suffix}"
            LegalOperationsLifecycleRegistry.create(
                CaseMatter(
                    tenant_id=tenant_id,
                    case_matter_id=matter_id,
                    matter_reference=f"BROWSER-MATTER-{suffix[:12]}",
                    opened_at=now,
                    evidence_reference=f"browser-cert-matter:{matter_id}",
                ),
                collections["lifecycle"],
                session=session,
            )
            screening = _screening(tenant_id, suffix, now)
            LegalConflictScreeningRegistry.persist_screening(
                screening,
                collections["screening"],
                session=session,
            )
            session.commit_transaction()

        for actor in actors.values():
            user = registry.get_user_by_id(actor["principal_id"])
            if user is None:
                raise RuntimeError("BROWSER_CERT_USER_READBACK_FAILED")
            actor["access_token"] = registry.create_session(user).token
        partner = actors["partner"]
        state_path.write_text(
            json.dumps(
                {
                    "state_version": STATE_VERSION,
                    "database_name": database.name,
                    "tenant_id": tenant_id,
                    "principal_id": partner["principal_id"],
                    "email": partner["email"],
                    "access_token": partner["access_token"],
                    "actors": actors,
                    "matter_id": matter_id,
                    "screening_id": screening.screening_id,
                    "source_case_matter_id": screening.source_case_matter_id,
                    "foreign_tenant_id": foreign_tenant_id,
                    "branding": branding,
                    "foreign_branding": foreign_branding,
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
        database = _owned_database(client)
        client.drop_database(database.name)
    finally:
        client.close()


def verify(state_path: Path) -> None:
    uri = _uri()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        database = _owned_database(client)
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
# VERSION: v1.3.0-PYTHON-EOS-LOGIN-MFA-BROWSER-CERT
# AUTHORITY BOUNDARY: disposable synthetic browser-cert fixture only
# TENANT POSTURE: authenticated tenant and unjoined foreign tenant in a runner-owned disposable database
# FAIL-CLOSED POSTURE: wrong URI, unavailable replica set, and seed failures stop
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
