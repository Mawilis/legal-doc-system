"""Server-owned legal acceptance policy and orchestration.

TITLE: WILSY OS Legal Acceptance Service
VERSION: v1.2.0-PLATFORM-EXACT-ROLE-CURRENTNESS
AUTHORITY: Wilsy OS Core Governance
EPITOME: Derives a deterministic acceptance plan from canonical documents and
         authenticated identity, then appends immutable evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_acceptance_service.py
COLLABORATION / OWNERSHIP: HTTP router is transport-only; document and
                            acceptance registries own durable truth.
CERTIFICATION / UPDATE DATE: 2026-11-09
CHANGELOG: v1.2.0-PLATFORM-EXACT-ROLE-CURRENTNESS preserves mandatory PLATFORM_WORKSPACE
           admission while independently classifying malformed global roles,
           stale membership and capacity revisions, and selected workspace
           mismatch. Exact signed principal/tenant/session context is required;
           no failed authority is silently accepted.
           v1.1.0-PLATFORM-SCOPE-SELECTED-CAPACITY explicitly identifies these
           mandatory agreements as PLATFORM_WORKSPACE admission and resolves a
           GLOBAL session's exact selected capacity with current revisions.
           No agreement, acceptance evidence, commercial truth or IAM is bypassed.
           v1.0.0 establishes server-owned required-document policy, ordinary
           user/admin flows, owner-flow fail-closed readiness, and replay-safe
           acceptance submission.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Client payloads cannot choose tenant, principal,
                            approval, version, or digest authority.
TENANT BOUNDARY: Authenticated tenant and principal are validated before every
                 plan lookup and acceptance write.
AUTHORITY BOUNDARY: Legal acknowledgement/acceptance only; no signatory,
                    contract execution, payment, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Final

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError,
    TenantMembershipRepository,
    TenantMembershipRepositoryError,
)
from tools.eos.legal_operations.domain.legal_acceptance import (
    AcceptanceMethod,
    LegalAcceptanceEvidence,
    LegalAcceptanceError,
    LegalAcceptanceStatus,
    LegalAgreementType,
    LegalDocumentVersion,
)
from tools.eos.legal_operations.registry.legal_acceptance_registry import (
    LegalAcceptanceRegistry,
    LegalAcceptanceRegistryError,
)
from tools.eos.legal_operations.registry.legal_document_registry import (
    LegalDocumentRegistry,
    LegalDocumentRegistryError,
)
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry
from tools.eos.auth.workspace_bootstrap_projection import (
    WorkspaceBootstrapProjectionError,
    resolve_workspace_id,
)


VERSION: Final[str] = "v1.2.0-PLATFORM-EXACT-ROLE-CURRENTNESS"
PLATFORM_ADMISSION_SCOPE: Final[str] = "PLATFORM_WORKSPACE"
# These are platform-use obligations, not a Legal Operations product grant.
ORDINARY_REQUIRED: Final[tuple[LegalAgreementType, ...]] = (
    LegalAgreementType.INSTITUTIONAL_CHARTER,
    LegalAgreementType.USER_TERMS,
    LegalAgreementType.ACCEPTABLE_USE,
    LegalAgreementType.PRIVACY_NOTICE,
    LegalAgreementType.AI_ASSISTANCE_NOTICE,
)
ADMIN_REQUIRED: Final[tuple[LegalAgreementType, ...]] = ORDINARY_REQUIRED + (LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE,)
ADMIN_RESPONSIBILITY_BUSINESS_ROLES: Final[frozenset[str]] = frozenset(
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
COMMERCIAL_FAMILIES: Final[tuple[LegalAgreementType, ...]] = (
    LegalAgreementType.MASTER_SUBSCRIPTION_AGREEMENT,
    LegalAgreementType.ORDER_FORM,
    LegalAgreementType.DATA_PROCESSING_AGREEMENT,
    LegalAgreementType.SECURITY_SLA_SCHEDULE,
    LegalAgreementType.PRODUCT_ADDENDUM,
)


class LegalAcceptanceServiceError(RuntimeError):
    """Bounded policy, authority, or acceptance failure."""


@dataclass(frozen=True, slots=True)
class AcceptancePrincipal:
    """Authenticated routing context; credential role projections are excluded."""

    tenant_id: str
    principal_id: str
    session_id: str
    locale: str = "en-ZA"


def _principal(identity: SovereignIdentity, session_id: str, locale: str) -> AcceptancePrincipal:
    if not isinstance(identity, SovereignIdentity) or not identity.tenant_id or not identity.identity_id:
        raise LegalAcceptanceServiceError("LEGAL_ACCEPTANCE_AUTHENTICATED_CONTEXT_INVALID")
    if not isinstance(session_id, str) or not session_id.strip():
        raise LegalAcceptanceServiceError("LEGAL_ACCEPTANCE_SESSION_REQUIRED")
    return AcceptancePrincipal(identity.tenant_id, identity.identity_id, session_id, locale or "en-ZA")


class LegalAcceptanceService:
    """Compose platform-use obligations over existing canonical authorities.

    Current tenant, membership and selected capacity determine applicability.
    Approved document versions and immutable acceptance streams remain separate
    authorities; no product entitlement, practice permission, corporate execution,
    payment or settlement is issued. Callers own sessions, transactions and retry.
    """

    def __init__(
        self,
        document_collection: Any = None,
        acceptance_collection: Any = None,
        tenant_resolver: Callable[..., Any] | None = None,
        *,
        membership_repository: Any = None,
        business_role_repository: Any = None,
    ) -> None:
        """Bind existing registries and optionally injected tenant/authority reads.

        Construction performs no I/O, index provisioning, mutation or transaction.
        """
        self.document_collection = document_collection
        self.acceptance_collection = acceptance_collection
        self.document_registry = LegalDocumentRegistry
        self.acceptance_registry = LegalAcceptanceRegistry
        self.tenant_resolver = tenant_resolver or TenantRegistry.resolve_canonical_tenant
        self.membership_repository = (
            membership_repository
            if membership_repository is not None
            else TenantMembershipRepository()
        )
        self.business_role_repository = (
            business_role_repository
            if business_role_repository is not None
            else TenantBusinessRoleRepository()
        )

    def _validate_tenant(self, principal: AcceptancePrincipal, *, session: Any = None) -> None:
        try:
            tenant = self.tenant_resolver(principal.tenant_id, session=session)
        except TypeError:
            tenant = self.tenant_resolver(principal.tenant_id)
        except Exception as error:
            raise LegalAcceptanceServiceError("LEGAL_ACCEPTANCE_TENANT_UNAVAILABLE") from error
        if getattr(tenant, "tenant_id", None) != principal.tenant_id:
            raise LegalAcceptanceServiceError("LEGAL_ACCEPTANCE_TENANT_MISMATCH")

    def _resolve_business_role(
        self,
        principal: AcceptancePrincipal,
        *,
        identity: SovereignIdentity,
        session: Any = None,
    ) -> str:
        """Require current ACTIVE membership and exact durable business-role truth."""
        try:
            membership = self.membership_repository.resolve(
                principal.principal_id,
                principal.tenant_id,
                session=session,
            )
        except TenantMembershipNotFoundError as error:
            raise LegalAcceptanceServiceError(
                "LEGAL_ACCEPTANCE_MEMBERSHIP_REQUIRED"
            ) from error
        except TenantMembershipRepositoryError as error:
            raise LegalAcceptanceServiceError(
                "LEGAL_ACCEPTANCE_MEMBERSHIP_AUTHORITY_UNAVAILABLE"
            ) from error

        if (
            getattr(membership, "principal_id", None) != principal.principal_id
            or getattr(membership, "tenant_id", None) != principal.tenant_id
        ):
            raise LegalAcceptanceServiceError(
                "LEGAL_ACCEPTANCE_MEMBERSHIP_AUTHORITY_INVALID"
            )
        if getattr(membership, "status", None) is not TenantMembershipStatus.ACTIVE:
            raise LegalAcceptanceServiceError(
                "LEGAL_ACCEPTANCE_MEMBERSHIP_INACTIVE"
            )

        scope = identity.principal_scope
        if scope not in (None, "TENANT", "GLOBAL"):
            raise LegalAcceptanceServiceError("LEGAL_ACCEPTANCE_PRINCIPAL_SCOPE_INVALID")
        selected_role: str | None = None
        if scope == "GLOBAL":
            # GLOBAL authentication has already bound the selection. Re-read
            # that exact capacity; resolving all roles would merge or ambiguously
            # reject the Owner/Partner distinction after a successful bootstrap.
            roles = identity.roles
            if (
                identity.identity_id != principal.principal_id
                or identity.tenant_id != principal.tenant_id
                or not isinstance(roles, list)
                or len(roles) != 1
                or not isinstance(roles[0], str)
                or roles[0] not in TENANT_ROLES
                or roles[0] != roles[0].strip()
                or not isinstance(identity.session_reference, str)
                or not identity.session_reference.strip()
                or not isinstance(identity.workspace_id, str)
                or not identity.workspace_id.strip()
                or not isinstance(identity.membership_revision, int)
                or isinstance(identity.membership_revision, bool)
                or identity.membership_revision < 0
                or not isinstance(identity.capacity_revision, int)
                or isinstance(identity.capacity_revision, bool)
                or identity.capacity_revision < 0
            ):
                raise LegalAcceptanceServiceError(
                    "LEGAL_ACCEPTANCE_SELECTED_CAPACITY_INVALID"
                )
            if identity.membership_revision != getattr(membership, "revision", None):
                raise LegalAcceptanceServiceError(
                    "LEGAL_ACCEPTANCE_MEMBERSHIP_REVISION_MISMATCH"
                )
            selected_role = roles[0]

        try:
            if scope == "GLOBAL":
                resolver = getattr(self.business_role_repository, "resolve_business_role", None)
                if not callable(resolver):
                    raise TenantBusinessRoleRepositoryError(
                        "TENANT_BUSINESS_ROLE_EXACT_RESOLVER_REQUIRED"
                    )
                business_role = resolver(
                    principal.principal_id,
                    principal.tenant_id,
                    selected_role,
                    session=session,
                )
            else:
                business_role = self.business_role_repository.resolve(
                    principal.principal_id,
                    principal.tenant_id,
                    session=session,
                )
        except TenantBusinessRoleNotFoundError as error:
            raise LegalAcceptanceServiceError(
                "LEGAL_ACCEPTANCE_BUSINESS_ROLE_REQUIRED"
            ) from error
        except TenantBusinessRoleRepositoryError as error:
            raise LegalAcceptanceServiceError(
                "LEGAL_ACCEPTANCE_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE"
            ) from error

        role = getattr(business_role, "business_role", None)
        if (
            getattr(business_role, "principal_id", None) != principal.principal_id
            or getattr(business_role, "tenant_id", None) != principal.tenant_id
            or not isinstance(role, str)
            or role not in TENANT_ROLES
        ):
            raise LegalAcceptanceServiceError(
                "LEGAL_ACCEPTANCE_BUSINESS_ROLE_AUTHORITY_INVALID"
            )
        if getattr(business_role, "status", None) is not TenantBusinessRoleStatus.ACTIVE:
            raise LegalAcceptanceServiceError(
                "LEGAL_ACCEPTANCE_BUSINESS_ROLE_INACTIVE"
            )
        if scope == "GLOBAL":
            try:
                expected_workspace = resolve_workspace_id(role, tenant_id=principal.tenant_id)
            except WorkspaceBootstrapProjectionError as error:
                raise LegalAcceptanceServiceError(
                    "LEGAL_ACCEPTANCE_SELECTED_CAPACITY_INVALID"
                ) from error
            if role != selected_role:
                raise LegalAcceptanceServiceError(
                    "LEGAL_ACCEPTANCE_BUSINESS_ROLE_AUTHORITY_INVALID"
                )
            if getattr(business_role, "revision", None) != identity.capacity_revision:
                raise LegalAcceptanceServiceError(
                    "LEGAL_ACCEPTANCE_CAPACITY_REVISION_MISMATCH"
                )
            if expected_workspace != identity.workspace_id:
                raise LegalAcceptanceServiceError(
                    "LEGAL_ACCEPTANCE_SELECTED_CAPACITY_STALE"
                )
        return role

    def _required_types(self, business_role: str) -> tuple[LegalAgreementType, ...]:
        return (
            ADMIN_REQUIRED
            if business_role in ADMIN_RESPONSIBILITY_BUSINESS_ROLES
            else ORDINARY_REQUIRED
        )

    def status(self, identity: SovereignIdentity, *, session_id: str, locale: str = "en-ZA", session: Any = None) -> dict[str, Any]:
        """Read the exact principal's mandatory platform agreement plan.

        The plan is scoped PLATFORM_WORKSPACE and is not Legal practice,
        commercial entitlement, signatory or IAM authority. Missing approved
        documents and missing acceptance evidence remain required; existing exact
        version/digest evidence is reused. Every participating read receives the
        caller's session; this service never starts, commits or retries it.

        Raises:
            LegalAcceptanceServiceError: Missing, stale or unavailable authority,
                malformed evidence, or unavailable canonical persistence.
        """
        principal = _principal(identity, session_id, locale)
        self._validate_tenant(principal, session=session)
        business_role = self._resolve_business_role(principal, identity=identity, session=session)
        try:
            evidence = LegalAcceptanceRegistry.list_for_principal(principal.tenant_id, principal.principal_id, self.acceptance_collection, session=session)
        except LegalAcceptanceRegistryError as error:
            raise LegalAcceptanceServiceError(str(error)) from error
        accepted = {(item.agreement_type, item.document_id, item.document_version, item.document_sha3_512) for item in evidence}
        cards: list[dict[str, Any]] = []
        missing: list[str] = []
        for family in self._required_types(business_role):
            try:
                document = LegalDocumentRegistry.approved_for(family, self.document_collection, session=session)
            except LegalDocumentRegistryError as error:
                raise LegalAcceptanceServiceError(str(error)) from error
            if document is None:
                missing.append(family.value)
                continue
            is_accepted = (family, document.document_id, document.version, document.sha3_512) in accepted
            cards.append({"agreementType": family.value, "documentId": document.document_id, "version": document.version, "sha3_512": document.sha3_512, "title": document.title, "jurisdiction": document.jurisdiction, "locale": document.locale, "effectiveFrom": document.effective_from.isoformat(), "summary": document.content_reference, "content": document.content, "accepted": is_accepted})
            if not is_accepted:
                missing.append(family.value)
        if any(item in missing for item in (LegalAgreementType.USER_TERMS.value, LegalAgreementType.ACCEPTABLE_USE.value, LegalAgreementType.PRIVACY_NOTICE.value, LegalAgreementType.AI_ASSISTANCE_NOTICE.value)):
            state = LegalAcceptanceStatus.USER_TERMS_REQUIRED.value
        elif LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE.value in missing:
            state = LegalAcceptanceStatus.ADMIN_ACK_REQUIRED.value
        elif missing:
            state = LegalAcceptanceStatus.DOCUMENT_APPROVAL_REQUIRED.value if not cards else LegalAcceptanceStatus.MATERIAL_REACCEPTANCE_REQUIRED.value
        else:
            state = LegalAcceptanceStatus.COMPLETE.value
        return {"status": state, "admissionScope": PLATFORM_ADMISSION_SCOPE, "tenantId": principal.tenant_id, "principalId": principal.principal_id, "documents": cards, "missingAgreementTypes": missing, "ownerBinding": {"available": False, "reason": "EXPLICIT_AUTHORISED_SIGNATORY_AND_APPROVED_COMMERCIAL_DOCUMENTS_REQUIRED"}, "legacyCompatibility": {"hasSignedCovenant": state == LegalAcceptanceStatus.COMPLETE.value}}

    def accept(self, identity: SovereignIdentity, *, document_id: str, document_version: str, document_sha3_512: str, acceptance_method: AcceptanceMethod, idempotency_key: str, session_id: str, locale: str = "en-ZA", session: Any = None) -> dict[str, Any]:
        """Append evidence for one current approved platform agreement.

        Tenant/principal and the current selected capacity come from authenticated
        authority. Exact document version and SHA3-512 must match the approved
        current record. Immutable registry replay preserves existing evidence;
        divergent replay fails closed. All reads/writes receive the caller's
        session, and the caller owns commit/rollback/retry. This method grants no
        corporate signatory, product/practice, payment or settlement authority.

        Raises:
            LegalAcceptanceServiceError: Invalid/stale authority or document,
                unsupported corporate execution, invalid method/key, or registry
                integrity/persistence failure.
        """
        principal = _principal(identity, session_id, locale)
        self._validate_tenant(principal, session=session)
        business_role = self._resolve_business_role(principal, identity=identity, session=session)
        if acceptance_method not in (AcceptanceMethod.ACCEPTANCE, AcceptanceMethod.ACKNOWLEDGEMENT):
            raise LegalAcceptanceServiceError("LEGAL_ACCEPTANCE_METHOD_INVALID")
        if not isinstance(idempotency_key, str) or not idempotency_key.strip():
            raise LegalAcceptanceServiceError("LEGAL_ACCEPTANCE_IDEMPOTENCY_REQUIRED")
        try:
            document = LegalDocumentRegistry.get(document_id, document_version, self.document_collection, session=session)
        except LegalDocumentRegistryError as error:
            raise LegalAcceptanceServiceError(str(error)) from error
        if document is None or document.status.value != "APPROVED" or document.sha3_512 != document_sha3_512:
            raise LegalAcceptanceServiceError("LEGAL_ACCEPTANCE_DOCUMENT_NOT_APPROVED")
        family = document.agreement_type
        if family in COMMERCIAL_FAMILIES:
            raise LegalAcceptanceServiceError("LEGAL_ACCEPTANCE_CORPORATE_EXECUTION_UNAVAILABLE")
        try:
            current_document = LegalDocumentRegistry.approved_for(family, self.document_collection, session=session)
        except LegalDocumentRegistryError as error:
            raise LegalAcceptanceServiceError(str(error)) from error
        if current_document != document:
            raise LegalAcceptanceServiceError("LEGAL_ACCEPTANCE_DOCUMENT_NOT_CURRENT")
        try:
            now = datetime.now(timezone.utc)
            fingerprint = LegalAcceptanceEvidence.fingerprint_payload(tenant_id=principal.tenant_id, principal_id=principal.principal_id, agreement_type=family, document_id=document.document_id, document_version=document.version, document_sha3_512=document.sha3_512, acceptance_method=acceptance_method, locale=principal.locale)
            evidence = LegalAcceptanceEvidence(acceptance_id=f"LEGAL-ACCEPT-{uuid.uuid4().hex}", tenant_id=principal.tenant_id, principal_id=principal.principal_id, agreement_type=family, document_id=document.document_id, document_version=document.version, document_sha3_512=document.sha3_512, accepted_at=now, acceptance_method=acceptance_method, actor_role_at_acceptance=business_role, session_id=principal.session_id, locale=principal.locale, authority_representation="authenticated_user_acknowledgement_only", evidence_fingerprint=fingerprint, idempotency_key=idempotency_key)
            persisted = LegalAcceptanceRegistry.create_or_replay(evidence, self.acceptance_collection, idempotency_key=idempotency_key, session=session)
        except (LegalAcceptanceRegistryError, LegalAcceptanceError) as error:
            raise LegalAcceptanceServiceError(str(error)) from error
        return {"acceptanceId": persisted.acceptance_id, "agreementType": persisted.agreement_type.value, "documentVersion": persisted.document_version, "evidenceFingerprint": persisted.evidence_fingerprint, "status": "RECORDED"}


__all__ = [
    "ADMIN_RESPONSIBILITY_BUSINESS_ROLES",
    "AcceptancePrincipal",
    "LegalAcceptanceService",
    "LegalAcceptanceServiceError",
    "PLATFORM_ADMISSION_SCOPE",
    "VERSION",
]

# ARTIFACT: legal_acceptance_service.py
# VERSION: v1.2.0-PLATFORM-EXACT-ROLE-CURRENTNESS
# AUTHORITY BOUNDARY: server-derived acceptance planning and evidence composition only
# TENANT POSTURE: canonical tenant is resolved before every read/write
# FAIL-CLOSED POSTURE: absent/unapproved/divergent documents and invalid authority deny
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
