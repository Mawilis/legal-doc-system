"""Trusted composition for WILSY System Services runtime dependencies.

The platform workforce scope is deployment-owned configuration. It is never
accepted from request data and deliberately has no fallback/default.
"""
from __future__ import annotations

import os
from typing import Any
from dataclasses import dataclass

from tools.eos.auth.system_permission_command_evidence import SystemPermissionCommandEvidence
from tools.eos.auth.system_permission_revocation_command_service import SystemPermissionRevocationCommandService
from tools.eos.saas.auth.password_reset_service import PasswordResetService
from tools.eos.system_services.security_incident_response_decision_registry import (
    COLLECTION as RESPONSE_DECISION_COLLECTION,
    EVENT_COLLECTION as RESPONSE_DECISION_EVENT_COLLECTION,
    PLATFORM_AUDIT_COLLECTION,
    PLATFORM_OUTBOX_COLLECTION,
    SecurityIncidentResponseDecisionRegistry,
)
from tools.eos.system_services.security_incident_response_decision_service import (
    SecurityIncidentResponseDecisionService,
)
from tools.eos.system_services.security_incident_response_execution import (
    SecurityIncidentResponseCanonicalExecutor,
)
from tools.eos.system_services.security_incident_registry import (
    COLLECTION as SECURITY_INCIDENT_COLLECTION,
    EVENT_COLLECTION as SECURITY_INCIDENT_EVENT_COLLECTION,
    SecurityIncidentRegistry,
)

from tools.eos.auth.current_system_permission_possession import CurrentSystemPermissionPossessionResolver
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.system_permission_assignment_registry import (
    COLLECTION as SYSTEM_PERMISSION_ASSIGNMENT_COLLECTION,
    SystemPermissionAssignmentRegistry,
)
from tools.eos.system_services.eos_authorizer import (
    SystemServicesAuthorizationUnavailable,
    SystemServicesEosAuthorizer,
)
from tools.eos.system_services.support_case_registry import (
    CASE_COLLECTION,
    EVENT_COLLECTION,
    SupportCaseRegistry,
)
from tools.eos.workforce.registry import workforce_relationship_registry


PLATFORM_WORKFORCE_SCOPE_ENV = "WILSY_PLATFORM_WORKFORCE_SCOPE_ID"


def resolve_platform_workforce_scope_id(value: object) -> str:
    """Validate one trusted deployment-supplied platform workforce scope ID."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 128
        or any(ord(character) < 33 or ord(character) == 127 for character in value)
        or "*" in value
    ):
        raise SystemServicesAuthorizationUnavailable("PLATFORM_WORKFORCE_SCOPE_CONFIGURATION_REQUIRED")
    return value


def configured_platform_workforce_scope_id() -> str:
    """Read only the server process environment; never read request headers/body."""
    return resolve_platform_workforce_scope_id(
        os.environ.get(PLATFORM_WORKFORCE_SCOPE_ENV, "")
    )


def build_system_services_runtime(database: Any, *, platform_workforce_scope_id: str) -> tuple[SupportCaseRegistry, SystemServicesEosAuthorizer]:
    """Compose canonical Mongo repositories and fail-closed current EOS authority."""
    if database is None:
        raise SystemServicesAuthorizationUnavailable("SYSTEM_SERVICES_DATABASE_REQUIRED")
    scope_id = resolve_platform_workforce_scope_id(platform_workforce_scope_id)
    PrincipalAuthorityRepository.ensure_indexes(database["principal_authorities"])
    assignment_registry = SystemPermissionAssignmentRegistry(
        database[SYSTEM_PERMISSION_ASSIGNMENT_COLLECTION]
    )
    assignment_registry.ensure_indexes()
    workforce_collection = database[workforce_relationship_registry.COLLECTION_NAME]
    workforce_relationship_registry.ensure_indexes(workforce_collection)
    possession = CurrentSystemPermissionPossessionResolver(
        principal_collection=database["principal_authorities"],
        assignment_registry=assignment_registry,
    )
    authorizer = SystemServicesEosAuthorizer(
        possession_resolver=possession,
        workforce_collection=workforce_collection,
        platform_scope_id=scope_id,
    )
    case_registry = SupportCaseRegistry(
        cases=database[CASE_COLLECTION],
        events=database[EVENT_COLLECTION],
    )
    return case_registry, authorizer


@dataclass(frozen=True, slots=True)
class SystemServicesResponseRuntime:
    """Separately ready decision governance and canonical execution composition."""

    decision_registry: SecurityIncidentResponseDecisionRegistry
    decision_service: SecurityIncidentResponseDecisionService
    canonical_executor: SecurityIncidentResponseCanonicalExecutor


def build_system_services_response_runtime(
    database: Any,
    *,
    authorizer: SystemServicesEosAuthorizer,
) -> SystemServicesResponseRuntime:
    """Compose response governance without enabling dispatch or owning transactions.

    PasswordResetService is intentionally created without a notification
    dispatcher. Its own transaction remains canonical; permission revocation
    receives the caller-owned session through the canonical executor.
    """
    if database is None:
        raise SystemServicesAuthorizationUnavailable("SYSTEM_SERVICES_DATABASE_REQUIRED")
    if type(authorizer) is not SystemServicesEosAuthorizer:
        raise SystemServicesAuthorizationUnavailable("CURRENT_PLATFORM_AUTHORIZER_REQUIRED")

    decisions = SecurityIncidentResponseDecisionRegistry(
        decisions=database[RESPONSE_DECISION_COLLECTION],
        events=database[RESPONSE_DECISION_EVENT_COLLECTION],
        audit_events=database[PLATFORM_AUDIT_COLLECTION],
        outbox=database[PLATFORM_OUTBOX_COLLECTION],
    )
    decisions.ensure_indexes()

    incidents = SecurityIncidentRegistry(
        incidents=database[SECURITY_INCIDENT_COLLECTION],
        events=database[SECURITY_INCIDENT_EVENT_COLLECTION],
    )
    assignment_registry = SystemPermissionAssignmentRegistry(
        database[SYSTEM_PERMISSION_ASSIGNMENT_COLLECTION]
    )
    assignment_registry.ensure_indexes()
    possession = CurrentSystemPermissionPossessionResolver(
        principal_collection=database["principal_authorities"],
        assignment_registry=assignment_registry,
    )
    revocation = SystemPermissionRevocationCommandService(
        principal_collection=database["principal_authorities"],
        possession_resolver=possession,
        assignment_registry=assignment_registry,
    )
    password_reset = PasswordResetService()
    decision_service = SecurityIncidentResponseDecisionService(
        decisions=decisions,
        incidents=incidents,
        authorizer=authorizer,
    )
    executor = SecurityIncidentResponseCanonicalExecutor(
        password_reset_service=password_reset,
        permission_revocation_service=revocation,
        system_services_authorizer=authorizer,
    )
    return SystemServicesResponseRuntime(
        decision_registry=decisions,
        decision_service=decision_service,
        canonical_executor=executor,
    )


__all__ = [
    "PLATFORM_WORKFORCE_SCOPE_ENV",
    "resolve_platform_workforce_scope_id",
    "configured_platform_workforce_scope_id",
    "build_system_services_runtime",
    "SystemServicesResponseRuntime",
    "build_system_services_response_runtime",
]
