"""Current privileged-eligibility composition.

This module creates no privilege, role, permission, activation, membership,
workforce relationship, platform prerequisite, or financial authority.

It answers one narrow question:

    Is one already-persisted P2 eligibility-evidence record still supported by
    current authoritative state?

Historical snapshot booleans inside P2 evidence are never accepted as current
authority. Platform currentness is re-resolved from Core Governance.
Tenant currentness is re-resolved from principal, membership, and, when
required, canonical workforce relationship history.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pymongo.client_session import ClientSession

from tools.eos.auth.current_platform_privileged_eligibility_prerequisite import (
    CurrentPlatformPrerequisiteError,
    CurrentPlatformPrivilegedEligibilityPrerequisiteResolver,
)
from tools.eos.auth.platform_privileged_eligibility_prerequisite import (
    PRIVILEGE_CLASS,
    SCOPE,
    PlatformPrivilegedEligibilityPrerequisite,
)
from tools.eos.auth.principal_authority import PrincipalStatus
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.privileged_eligibility import (
    ENTERPRISE_ADMIN,
    SOVEREIGN_ARCHITECT,
    PrivilegedEligibilityReason,
    PrivilegedTargetClass,
)
from tools.eos.auth.privileged_eligibility_evidence import (
    PrivilegedEligibilityEvidence,
)
from tools.eos.auth.privileged_eligibility_evidence_registry import (
    PrivilegedEligibilityEvidenceNotFoundError,
    PrivilegedEligibilityEvidenceRegistry,
    PrivilegedEligibilityEvidenceRegistryError,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError,
    TenantMembershipRepository,
    TenantMembershipRepositoryError,
)
from tools.eos.auth.workforce_authorization_currentness import (
    WorkforceAuthorizationCurrentnessError,
    derive_tenant_principal_workforce_currentness,
)
from tools.eos.workforce.registry.workforce_relationship_registry import (
    WorkforceRelationshipRegistryError,
    list_principal_relationships,
)


class CurrentPrivilegedEligibilityError(RuntimeError):
    """Fail-closed currentness-composition failure."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _identifier(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "*" in value
    ):
        raise CurrentPrivilegedEligibilityError(name + "_INVALID")
    return value


def _moment(value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise CurrentPrivilegedEligibilityError("EVALUATED_AT_INVALID")
    return value


def _active_transaction(session: object) -> bool:
    if session is None:
        return False

    try:
        marker = getattr(session, "in_transaction")
    except Exception:
        return False

    try:
        value = marker() if callable(marker) else marker
    except Exception:
        return False

    return value is True


class CurrentPrivilegedEligibilityResolver:
    """Read-only conjunction of persisted P2 evidence and live authority."""

    def __init__(
        self,
        *,
        principal_collection: Any,
        membership_collection: Any,
        evidence_registry: PrivilegedEligibilityEvidenceRegistry,
        platform_prerequisite_resolver:
            CurrentPlatformPrivilegedEligibilityPrerequisiteResolver,
        workforce_relationship_collection: Any = None,
    ) -> None:
        if principal_collection is None:
            raise CurrentPrivilegedEligibilityError(
                "PRINCIPAL_COLLECTION_REQUIRED"
            )

        if membership_collection is None:
            raise CurrentPrivilegedEligibilityError(
                "MEMBERSHIP_COLLECTION_REQUIRED"
            )

        if type(evidence_registry) is not PrivilegedEligibilityEvidenceRegistry:
            raise CurrentPrivilegedEligibilityError(
                "EVIDENCE_REGISTRY_REQUIRED"
            )

        if (
            type(platform_prerequisite_resolver)
            is not CurrentPlatformPrivilegedEligibilityPrerequisiteResolver
        ):
            raise CurrentPrivilegedEligibilityError(
                "PLATFORM_PREREQUISITE_RESOLVER_REQUIRED"
            )

        self._principal_collection = principal_collection
        self._membership_collection = membership_collection
        self._evidence_registry = evidence_registry
        self._platform_prerequisite_resolver = platform_prerequisite_resolver
        self._workforce_relationship_collection = (
            workforce_relationship_collection
        )

    def _evidence(
        self,
        *,
        eligibility_evidence_id: str,
        session: ClientSession | None,
    ) -> PrivilegedEligibilityEvidence | None:
        try:
            return self._evidence_registry.get(
                eligibility_evidence_id=eligibility_evidence_id,
                session=session,
            )
        except PrivilegedEligibilityEvidenceNotFoundError:
            return None
        except PrivilegedEligibilityEvidenceRegistryError as error:
            raise CurrentPrivilegedEligibilityError(
                "ELIGIBILITY_EVIDENCE_UNAVAILABLE"
            ) from error

    def _platform_current(
        self,
        *,
        evidence: PrivilegedEligibilityEvidence,
        at: datetime,
        session: ClientSession | None,
    ) -> bool:
        if (
            evidence.target_class
            is not PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT
            or evidence.tenant_id is not None
            or evidence.privileged_role_id != SOVEREIGN_ARCHITECT
            or not evidence.eligible
            or evidence.reason is not PrivilegedEligibilityReason.ELIGIBLE
        ):
            return False

        if (
            evidence.platform_prerequisite_id is None
            or evidence.platform_prerequisite_revision is None
            or evidence.platform_prerequisite_fingerprint is None
            or evidence.platform_prerequisite_source_evidence_reference is None
        ):
            return False

        try:
            current = self._platform_prerequisite_resolver.resolve(
                principal_id=evidence.principal_id,
                privilege_class=PRIVILEGE_CLASS,
                scope=SCOPE,
                at=at,
                session=session,
            )
        except CurrentPlatformPrerequisiteError as error:
            raise CurrentPrivilegedEligibilityError(
                "PLATFORM_CURRENTNESS_UNAVAILABLE"
            ) from error

        if current is None:
            return False

        if not isinstance(
            current,
            PlatformPrivilegedEligibilityPrerequisite,
        ):
            raise CurrentPrivilegedEligibilityError(
                "PLATFORM_CURRENTNESS_INVALID"
            )

        return (
            current.principal_id == evidence.principal_id
            and current.privilege_class == PRIVILEGE_CLASS
            and current.scope == SCOPE
            and current.platform_prerequisite_id
            == evidence.platform_prerequisite_id
            and current.revision == evidence.platform_prerequisite_revision
            and current.prerequisite_fingerprint
            == evidence.platform_prerequisite_fingerprint
            and current.source_evidence_reference
            == evidence.platform_prerequisite_source_evidence_reference
        )

    def _tenant_current(
        self,
        *,
        evidence: PrivilegedEligibilityEvidence,
        at: datetime,
        session: ClientSession | None,
    ) -> bool:
        tenant_id = evidence.tenant_id

        if (
            evidence.target_class
            is not PrivilegedTargetClass.TENANT_PRIVILEGED
            or tenant_id is None
            or evidence.privileged_role_id != ENTERPRISE_ADMIN
            or not evidence.eligible
            or evidence.reason is not PrivilegedEligibilityReason.ELIGIBLE
        ):
            return False

        if any(
            value is not None
            for value in (
                evidence.platform_prerequisite_id,
                evidence.platform_prerequisite_revision,
                evidence.platform_prerequisite_fingerprint,
                evidence.platform_prerequisite_source_evidence_reference,
            )
        ):
            return False

        try:
            principal = PrincipalAuthorityRepository.get(
                evidence.principal_id,
                collection=self._principal_collection,
                session=session,
            )
        except PrincipalAuthorityNotFoundError:
            return False
        except PrincipalAuthorityRepositoryError as error:
            raise CurrentPrivilegedEligibilityError(
                "PRINCIPAL_CURRENTNESS_UNAVAILABLE"
            ) from error

        if principal.principal_id != evidence.principal_id:
            raise CurrentPrivilegedEligibilityError(
                "PRINCIPAL_BINDING_INVALID"
            )

        if principal.status is not PrincipalStatus.ACTIVE:
            return False

        try:
            membership = TenantMembershipRepository.resolve(
                evidence.principal_id,
                tenant_id,
                collection=self._membership_collection,
                session=session,
            )
        except TenantMembershipNotFoundError:
            return False
        except TenantMembershipRepositoryError as error:
            raise CurrentPrivilegedEligibilityError(
                "MEMBERSHIP_CURRENTNESS_UNAVAILABLE"
            ) from error

        if (
            membership.principal_id != evidence.principal_id
            or membership.tenant_id != tenant_id
        ):
            raise CurrentPrivilegedEligibilityError(
                "MEMBERSHIP_BINDING_INVALID"
            )

        if membership.status is not TenantMembershipStatus.ACTIVE:
            return False

        if not evidence.workforce_required:
            return True

        if (
            self._workforce_relationship_collection is None
            or not _active_transaction(session)
        ):
            raise CurrentPrivilegedEligibilityError(
                "WORKFORCE_CURRENTNESS_UNAVAILABLE"
            )

        try:
            relationships = list_principal_relationships(
                "TENANT",
                tenant_id,
                evidence.principal_id,
                collection=self._workforce_relationship_collection,
                session=session,
            )

            currentness = derive_tenant_principal_workforce_currentness(
                relationships,
                tenant_id=tenant_id,
                principal_id=evidence.principal_id,
                observed_at=at,
            )
        except (
            WorkforceRelationshipRegistryError,
            WorkforceAuthorizationCurrentnessError,
        ) as error:
            raise CurrentPrivilegedEligibilityError(
                "WORKFORCE_CURRENTNESS_UNAVAILABLE"
            ) from error
        except Exception as error:
            raise CurrentPrivilegedEligibilityError(
                "WORKFORCE_CURRENTNESS_UNAVAILABLE"
            ) from error

        return (
            currentness.tenant_id == tenant_id
            and currentness.principal_id == evidence.principal_id
            and currentness.observed_at == at
            and currentness.has_active_relationship
        )

    def resolve(
        self,
        *,
        eligibility_evidence_id: str,
        at: datetime,
        session: ClientSession | None = None,
    ) -> PrivilegedEligibilityEvidence | None:
        """Return exact P2 evidence iff live authority still supports it."""

        evidence_id = _identifier(
            "ELIGIBILITY_EVIDENCE_ID",
            eligibility_evidence_id,
        )
        moment = _moment(at)

        evidence = self._evidence(
            eligibility_evidence_id=evidence_id,
            session=session,
        )

        if evidence is None:
            return None

        if (
            evidence.target_class
            is PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT
        ):
            return (
                evidence
                if self._platform_current(
                    evidence=evidence,
                    at=moment,
                    session=session,
                )
                else None
            )

        if (
            evidence.target_class
            is PrivilegedTargetClass.TENANT_PRIVILEGED
        ):
            return (
                evidence
                if self._tenant_current(
                    evidence=evidence,
                    at=moment,
                    session=session,
                )
                else None
            )

        return None

    def is_current(
        self,
        *,
        eligibility_evidence_id: str,
        at: datetime,
        session: ClientSession | None = None,
    ) -> bool:
        """Return currentness fact only; this grants no authority."""

        return (
            self.resolve(
                eligibility_evidence_id=eligibility_evidence_id,
                at=at,
                session=session,
            )
            is not None
        )


__all__ = [
    "CurrentPrivilegedEligibilityError",
    "CurrentPrivilegedEligibilityResolver",
]
