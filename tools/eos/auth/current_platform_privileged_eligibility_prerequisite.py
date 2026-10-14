"""Current platform privileged-eligibility prerequisite resolver.

TITLE: Current Platform Privileged Eligibility Prerequisite Resolver
VERSION: v1.0.0-P2-R3-CURRENT-PLATFORM-PREREQUISITE
AUTHORITY: Wilsy OS Sovereign IAM
EPITOME: Read-only conjunction of an ACTIVE principal and exact current Core-Governance prerequisite.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/current_platform_privileged_eligibility_prerequisite.py
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0 establishes same-session, injected-time currentness.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: PLATFORM_SYSTEM only.
AUTHORITY BOUNDARY: Read-only prerequisite fact; no P2 or activation grant.
FINANCIAL AUTHORITY BOUNDARY: None.
"""
from __future__ import annotations

from datetime import datetime

from pymongo.client_session import ClientSession
from typing import Any, Final

from tools.eos.auth.platform_privileged_eligibility_prerequisite import PlatformPrivilegedEligibilityPrerequisite, PRIVILEGE_CLASS, SCOPE
from tools.eos.auth.platform_privileged_eligibility_prerequisite_registry import PlatformPrerequisiteRegistryError, PlatformPrivilegedEligibilityPrerequisiteRegistry
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError, PrincipalAuthorityRepository, PrincipalAuthorityRepositoryError
from tools.eos.auth.principal_status import PrincipalStatus

VERSION: Final[str] = "v1.0.0-P2-R3-CURRENT-PLATFORM-PREREQUISITE"


class CurrentPlatformPrerequisiteError(RuntimeError):
    """Fail-closed currentness composition failure."""


class CurrentPlatformPrivilegedEligibilityPrerequisiteResolver:
    """Resolve current exact platform prerequisite without writes or transaction ownership."""

    def __init__(self, *, principal_collection: Any, prerequisite_registry: PlatformPrivilegedEligibilityPrerequisiteRegistry) -> None:
        if principal_collection is None or type(prerequisite_registry) is not PlatformPrivilegedEligibilityPrerequisiteRegistry:
            raise CurrentPlatformPrerequisiteError("CURRENTNESS_DEPENDENCY_INVALID")
        self._principal_collection = principal_collection
        self._registry = prerequisite_registry

    def resolve(self, *, principal_id: str, privilege_class: str, scope: str,
                at: datetime, session: ClientSession | None = None) -> PlatformPrivilegedEligibilityPrerequisite | None:
        """Require ACTIVE exact principal plus exact current designation using one session."""
        if privilege_class != PRIVILEGE_CLASS or scope != SCOPE or not isinstance(principal_id, str) or not principal_id or "*" in principal_id:
            return None
        try:
            principal = PrincipalAuthorityRepository.get(principal_id, collection=self._principal_collection, session=session)
        except PrincipalAuthorityNotFoundError:
            return None
        except PrincipalAuthorityRepositoryError as error:
            raise CurrentPlatformPrerequisiteError("PRINCIPAL_CURRENTNESS_UNAVAILABLE") from error
        if principal.principal_id != principal_id or principal.status is not PrincipalStatus.ACTIVE:
            return None
        try:
            return self._registry.resolve_current(principal_id=principal_id, privilege_class=privilege_class, scope=scope, at=at, session=session)
        except PlatformPrerequisiteRegistryError as error:
            raise CurrentPlatformPrerequisiteError("PREREQUISITE_CURRENTNESS_UNAVAILABLE") from error


__all__ = ["VERSION", "CurrentPlatformPrerequisiteError", "CurrentPlatformPrivilegedEligibilityPrerequisiteResolver"]

# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: current_platform_privileged_eligibility_prerequisite.py
# VERSION: v1.0.0-P2-R3-CURRENT-PLATFORM-PREREQUISITE
# FORMULA: ACTIVE PRINCIPAL + ACTIVE EXACT PLATFORM PREREQUISITE + EFFECTIVE WINDOW
# SESSION: caller-supplied and propagated; WRITES: NONE
# TENANT / ROLE / ACTIVATION / FINANCIAL AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
