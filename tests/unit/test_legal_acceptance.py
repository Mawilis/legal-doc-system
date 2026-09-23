"""WILSY OS R1D-B0F-B4 legal acceptance certificate.

TITLE: Legal Document and Acceptance Authority Certificate
VERSION: v1.0.1-R1D-B0F-B4-R7B-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves immutable versioned documents, server-derived acceptance, and
         fail-closed separation from corporate execution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_acceptance.py
COLLABORATION / OWNERSHIP: Direct certificate for legal acceptance domain,
                            registries, service, and HTTP contract.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.1 adds the Mongo insert-payload mutation replay regression.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every evidence operation is tenant/principal scoped.
AUTHORITY BOUNDARY: Acknowledgement only; no binding or financial authority.
"""
from datetime import datetime, timezone
from typing import Any, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.legal_operations.domain.legal_acceptance import (
    AcceptanceMethod,
    LegalAcceptanceError,
    LegalAcceptanceStatus,
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
    canonical_document_digest,
)
from tools.eos.legal_operations.registry.legal_acceptance_registry import LegalAcceptanceRegistry, LegalAcceptanceRegistryError
from tools.eos.legal_operations.registry.legal_document_registry import LegalDocumentRegistry, LegalDocumentRegistryError
from tools.eos.legal_operations.service.legal_acceptance_service import LegalAcceptanceService, LegalAcceptanceServiceError


class Collection:
    def __init__(self): self.rows = []
    def insert_one(self, row, *, session=None) -> Any:
        if any(r.get("document_id") == row.get("document_id") and r.get("version") == row.get("version") for r in self.rows):
            raise DuplicateKeyError("duplicate")
        if row.get("tenant_id") is not None and any(r.get("tenant_id") == row.get("tenant_id") and r.get("principal_id") == row.get("principal_id") and r.get("document_id") == row.get("document_id") and r.get("document_version") == row.get("document_version") for r in self.rows):
            raise DuplicateKeyError("duplicate")
        self.rows.append(dict(row)); return type("R", (), {})()
    def find_one(self, query, **kwargs):
        rows = [r for r in self.rows if all(r.get(k) == v for k, v in query.items())]
        for key, direction in reversed(kwargs.get("sort") or []):
            rows.sort(key=lambda item: item.get(key, ""), reverse=direction < 0)
        return rows[0] if rows else None
    def find(self, query, **_):
        return [r for r in self.rows if all(r.get(k) == v for k, v in query.items())]
    def create_index(self, *_args, **_kwargs): return "index"


class DriverMutatingCollection(Collection):
    """Mongo transport double reproducing driver-owned ``_id`` mutation."""

    def __init__(self):
        super().__init__()
        self.sessions = []
        self.insert_payloads = []

    def insert_one(self, row, *, session=None) -> Any:
        self.sessions.append(session)
        row["_id"] = "mongo-generated-id"
        self.insert_payloads.append(row)
        if self.rows:
            raise DuplicateKeyError("E11000 legal_document_version_unique")
        self.rows.append(dict(row))
        return type("R", (), {})()


class IndexRecordingCollection(Collection):
    def __init__(self):
        super().__init__()
        self.indexes = []

    def create_index(self, keys, **kwargs):
        self.indexes.append((keys, kwargs))
        return kwargs["name"]


NOW = datetime(2026, 9, 17, tzinfo=timezone.utc)


def document(family=LegalAgreementType.USER_TERMS, status=LegalDocumentStatus.APPROVED, content="v1", version="1.0.0"):
    reference = f"summary:{family.value}"
    return LegalDocumentVersion(
        document_id=f"DOC-{family.value}", agreement_type=family, version=version,
        title=family.value.replace("_", " ").title(), jurisdiction="ZA", locale="en-ZA",
        effective_from=NOW, status=status, content_reference=reference, content=content,
        sha3_512=canonical_document_digest(content, reference), created_at=NOW,
    )


def identity(role="USER"):
    from tools.eos.auth.principal_status import PrincipalStatus
    return SovereignIdentity(identity_id="principal-1", tenant_id="tenant-1", username="user", email="u@example.com", roles=[role], permissions=[], auth_method="JWT", status=PrincipalStatus.ACTIVE)


def service(business_role: str = "tenant_auditor"):
    from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
    from tools.eos.auth.tenant_membership import TenantMembershipStatus

    class MembershipRepository:
        def resolve(self, principal_id, tenant_id, *, session=None):
            return type(
                "Membership",
                (),
                {
                    "principal_id": principal_id,
                    "tenant_id": tenant_id,
                    "status": TenantMembershipStatus.ACTIVE,
                },
            )()

    class BusinessRoleRepository:
        def resolve(self, principal_id, tenant_id, *, session=None):
            return type(
                "BusinessRole",
                (),
                {
                    "principal_id": principal_id,
                    "tenant_id": tenant_id,
                    "business_role": business_role,
                    "status": TenantBusinessRoleStatus.ACTIVE,
                },
            )()

    docs, acceptances = Collection(), Collection()
    for family in (
        LegalAgreementType.INSTITUTIONAL_CHARTER,
        LegalAgreementType.USER_TERMS,
        LegalAgreementType.ACCEPTABLE_USE,
        LegalAgreementType.PRIVACY_NOTICE,
        LegalAgreementType.AI_ASSISTANCE_NOTICE,
    ):
        LegalDocumentRegistry.register(document(family), docs)
    tenant = lambda tenant_id, **_kwargs: type("Tenant", (), {"tenant_id": tenant_id})()
    return (
        LegalAcceptanceService(
            docs,
            acceptances,
            tenant,
            membership_repository=MembershipRepository(),
            business_role_repository=BusinessRoleRepository(),
        ),
        docs,
        acceptances,
    )


def approved(docs: Collection, family: LegalAgreementType) -> LegalDocumentVersion:
    value = LegalDocumentRegistry.approved_for(family, docs)
    assert value is not None
    return value


def test_document_version_digest_is_immutable_and_draft_cannot_bind():
    docs = Collection(); original = document(); LegalDocumentRegistry.register(original, docs)
    with pytest.raises(LegalDocumentRegistryError):
        LegalDocumentRegistry.register(document(content="changed"), docs)
    draft = document(status=LegalDocumentStatus.DRAFT_REVIEW_REQUIRED, version="0.9.0")
    LegalDocumentRegistry.register(draft, docs)
    assert approved(docs, LegalAgreementType.USER_TERMS).sha3_512 == original.sha3_512


def test_document_exact_replay_isolated_from_driver_id_mutation_and_forwards_session():
    collection = DriverMutatingCollection()
    session = object()
    original = document()
    assert LegalDocumentRegistry.register(original, collection, session=session) == original
    assert LegalDocumentRegistry.register(original, collection, session=session) == original
    assert len(collection.rows) == 1
    assert collection.sessions == [session, session]
    assert "_id" in collection.insert_payloads[1]

    with pytest.raises(LegalDocumentRegistryError, match="IMMUTABILITY_CONFLICT"):
        LegalDocumentRegistry.register(document(content="different"), collection, session=session)

    indexes = IndexRecordingCollection()
    LegalDocumentRegistry.ensure_indexes(indexes)
    assert [entry[1]["name"] for entry in indexes.indexes] == [
        "legal_document_version_unique", "legal_agreement_version_unique"
    ]


def test_acceptance_plan_requires_all_approved_documents():
    svc, _, _ = service(); plan = svc.status(identity(), session_id="session-1")
    assert plan["status"] == LegalAcceptanceStatus.USER_TERMS_REQUIRED
    assert len(plan["missingAgreementTypes"]) == 5
    assert plan["ownerBinding"]["available"] is False


def test_admin_responsibility_applicability_is_explicit_canonical_business_role_policy():
    import tools.eos.legal_operations.service.legal_acceptance_service as module

    expected = frozenset(
        {
            "tenant_owner",
            "tenant_admin",
            "tenant_platform_billing_provider_policy_admin",
            "tenant_inbound_collection_authorization_admin",
            "tenant_inbound_merchant_configuration_admin",
            "tenant_inbound_provider_security_admin",
            "tenant_inbound_provider_policy_admin",
            "tenant_inbound_provider_policy_activation_admin",
        }
    )

    assert getattr(module, "ADMIN_RESPONSIBILITY_BUSINESS_ROLES", None) == expected
    assert "tenant_manager" not in expected
    assert "SUPER_ADMIN" not in expected


def test_governed_business_role_not_jwt_role_controls_admin_notice_applicability():
    governed_admin, _, _ = service("tenant_admin")
    admin_plan = governed_admin.status(
        identity("USER"),
        session_id="session-governed-admin",
    )
    assert (
        LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE.value
        in admin_plan["missingAgreementTypes"]
    )

    governed_non_admin, _, _ = service("tenant_auditor")
    non_admin_plan = governed_non_admin.status(
        identity("SUPER_ADMIN"),
        session_id="session-forged-super",
    )
    assert (
        LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE.value
        not in non_admin_plan["missingAgreementTypes"]
    )


def test_legal_acceptance_role_authority_fails_closed_and_records_governed_role():
    from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
    from tools.eos.auth.tenant_business_role_repository import (
        TenantBusinessRoleNotFoundError,
        TenantBusinessRoleRepositoryError,
    )
    from tools.eos.auth.tenant_membership import TenantMembershipStatus
    from tools.eos.auth.tenant_membership_repository import (
        TenantMembershipNotFoundError,
        TenantMembershipRepositoryError,
    )

    class MembershipRepository:
        def __init__(self, *, status=TenantMembershipStatus.ACTIVE, error=None):
            self.status = status
            self.error = error

        def resolve(self, principal_id, tenant_id, *, session=None):
            if self.error is not None:
                raise self.error
            return type(
                "Membership",
                (),
                {
                    "principal_id": principal_id,
                    "tenant_id": tenant_id,
                    "status": self.status,
                },
            )()

    class BusinessRoleRepository:
        def __init__(
            self,
            role="tenant_admin",
            *,
            status=TenantBusinessRoleStatus.ACTIVE,
            error=None,
        ):
            self.role = role
            self.status = status
            self.error = error

        def resolve(self, principal_id, tenant_id, *, session=None):
            if self.error is not None:
                raise self.error
            return type(
                "BusinessRole",
                (),
                {
                    "principal_id": principal_id,
                    "tenant_id": tenant_id,
                    "business_role": self.role,
                    "status": self.status,
                },
            )()

    def build(membership_repository, business_role_repository):
        docs, acceptances = Collection(), Collection()
        for family in (
            LegalAgreementType.INSTITUTIONAL_CHARTER,
            LegalAgreementType.USER_TERMS,
            LegalAgreementType.ACCEPTABLE_USE,
            LegalAgreementType.PRIVACY_NOTICE,
            LegalAgreementType.AI_ASSISTANCE_NOTICE,
        ):
            LegalDocumentRegistry.register(document(family), docs)
        tenant = lambda tenant_id, **_kwargs: type(
            "Tenant",
            (),
            {"tenant_id": tenant_id},
        )()
        return (
            LegalAcceptanceService(
                docs,
                acceptances,
                tenant,
                membership_repository=membership_repository,
                business_role_repository=business_role_repository,
            ),
            docs,
            acceptances,
        )

    cases = (
        (
            MembershipRepository(
                error=TenantMembershipNotFoundError("TENANT_MEMBERSHIP_NOT_FOUND")
            ),
            BusinessRoleRepository(),
            "LEGAL_ACCEPTANCE_MEMBERSHIP_REQUIRED",
        ),
        (
            MembershipRepository(
                error=TenantMembershipRepositoryError("TENANT_MEMBERSHIP_READ_FAILED")
            ),
            BusinessRoleRepository(),
            "LEGAL_ACCEPTANCE_MEMBERSHIP_AUTHORITY_UNAVAILABLE",
        ),
        (
            MembershipRepository(status=TenantMembershipStatus.REVOKED),
            BusinessRoleRepository(),
            "LEGAL_ACCEPTANCE_MEMBERSHIP_INACTIVE",
        ),
        (
            MembershipRepository(),
            BusinessRoleRepository(
                error=TenantBusinessRoleNotFoundError("TENANT_BUSINESS_ROLE_NOT_FOUND")
            ),
            "LEGAL_ACCEPTANCE_BUSINESS_ROLE_REQUIRED",
        ),
        (
            MembershipRepository(),
            BusinessRoleRepository(
                error=TenantBusinessRoleRepositoryError(
                    "TENANT_BUSINESS_ROLE_READ_FAILED"
                )
            ),
            "LEGAL_ACCEPTANCE_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE",
        ),
        (
            MembershipRepository(),
            BusinessRoleRepository(status=TenantBusinessRoleStatus.REVOKED),
            "LEGAL_ACCEPTANCE_BUSINESS_ROLE_INACTIVE",
        ),
    )

    for membership_repository, business_role_repository, code in cases:
        svc, _, _ = build(membership_repository, business_role_repository)
        with pytest.raises(LegalAcceptanceServiceError, match=code):
            svc.status(identity("SUPER_ADMIN"), session_id=f"session-{code}")

    svc, docs, evidence = build(
        MembershipRepository(),
        BusinessRoleRepository("tenant_admin"),
    )
    doc = approved(docs, LegalAgreementType.USER_TERMS)
    svc.accept(
        identity("SUPER_ADMIN"),
        document_id=doc.document_id,
        document_version=doc.version,
        document_sha3_512=doc.sha3_512,
        acceptance_method=AcceptanceMethod.ACCEPTANCE,
        idempotency_key="idem-governed-role-evidence",
        session_id="session-governed-role-evidence",
    )

    assert len(evidence.rows) == 1
    assert evidence.rows[0]["actor_role_at_acceptance"] == "tenant_admin"
    assert evidence.rows[0]["actor_role_at_acceptance"] != "SUPER_ADMIN"


def test_legacy_signed_super_admin_role_cannot_create_admin_legal_obligation():
    svc, _, _ = service()

    plan = svc.status(identity("SUPER_ADMIN"), session_id="session-legacy-super")

    assert LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE.value not in plan["missingAgreementTypes"]


def test_acceptance_records_and_replays_without_duplicate():
    svc, docs, evidence = service(); doc = approved(docs, LegalAgreementType.USER_TERMS)
    payload: dict[str, Any] = dict(document_id=doc.document_id, document_version=doc.version, document_sha3_512=doc.sha3_512, acceptance_method=AcceptanceMethod.ACCEPTANCE, idempotency_key="idem-1", session_id="session-1")
    first = svc.accept(identity(), **payload); second = svc.accept(identity(), **payload)
    assert first["acceptanceId"] == second["acceptanceId"] and len(evidence.rows) == 1


def test_divergent_replay_and_commercial_execution_fail_closed():
    svc, docs, _ = service(); doc = approved(docs, LegalAgreementType.USER_TERMS)
    args: dict[str, Any] = dict(document_id=doc.document_id, document_version=doc.version, document_sha3_512=doc.sha3_512, acceptance_method=AcceptanceMethod.ACCEPTANCE, idempotency_key="idem-2", session_id="session-1")
    svc.accept(identity(), **args)
    with pytest.raises(LegalAcceptanceServiceError): svc.accept(identity(), **{**args, "document_sha3_512": "0" * 128})
    commercial = document(LegalAgreementType.MASTER_SUBSCRIPTION_AGREEMENT)
    docs.rows.append(commercial.to_document())
    with pytest.raises(LegalAcceptanceServiceError): svc.accept(identity(), document_id=commercial.document_id, document_version=commercial.version, document_sha3_512=commercial.sha3_512, acceptance_method=AcceptanceMethod.ACCEPTANCE, idempotency_key="idem-3", session_id="session-1")


def test_charter_acknowledgement_is_not_contract_execution_and_tenant_isolation():
    svc, docs, evidence = service(); doc = approved(docs, LegalAgreementType.INSTITUTIONAL_CHARTER)
    result = svc.accept(identity(), document_id=doc.document_id, document_version=doc.version, document_sha3_512=doc.sha3_512, acceptance_method=AcceptanceMethod.ACKNOWLEDGEMENT, idempotency_key="idem-charter", session_id="session-1")
    assert result["agreementType"] == LegalAgreementType.INSTITUTIONAL_CHARTER.value
    assert evidence.rows[0]["authority_representation"] == "authenticated_user_acknowledgement_only"


def test_acceptance_rejects_stale_approved_version_after_successor_becomes_current():
    svc, docs, evidence = service()
    stale = approved(docs, LegalAgreementType.USER_TERMS)
    successor = document(LegalAgreementType.USER_TERMS, content="v2", version="1.1.0")
    LegalDocumentRegistry.register(successor, docs)
    assert approved(docs, LegalAgreementType.USER_TERMS) == successor

    with pytest.raises(LegalAcceptanceServiceError, match="LEGAL_ACCEPTANCE_DOCUMENT_NOT_CURRENT"):
        svc.accept(
            identity(),
            document_id=stale.document_id,
            document_version=stale.version,
            document_sha3_512=stale.sha3_512,
            acceptance_method=AcceptanceMethod.ACCEPTANCE,
            idempotency_key="idem-stale-approved",
            session_id="session-1",
        )
    assert evidence.rows == []


def test_public_surfaces_have_no_signature_or_financial_authority():
    import inspect
    from tools.eos.api import legal_acceptance_router
    source = inspect.getsource(legal_acceptance_router)
    assert "Sovereign_Signature_Pad" not in source
    assert "financial" in source.lower() and "Kennel EOS" in source


"""
ARTIFACT: tests/unit/test_legal_acceptance.py
VERSION: v1.0.1-R1D-B0F-B4-R7B-CERT
AUTHORITY BOUNDARY: certificate evidence only
END OF WILSY OS SOVEREIGN ARTIFACT
"""
