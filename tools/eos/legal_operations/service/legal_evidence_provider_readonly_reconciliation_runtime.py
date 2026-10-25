"""Deployment bootstrap for the governed legal-evidence reconciliation route.

This module binds only canonical Python EOS authorities. It never provisions
platform decision-audit indexes at request time; deployment must run the
separate provisioner against the same explicit audit URI before startup.
"""
from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

from pymongo import MongoClient

from tools.eos.api.authority_bridge_router import (
    _production_noninteractive_assurance_service,
    _service_config,
)
from tools.eos.auth.current_platform_privileged_eligibility_prerequisite import (
    CurrentPlatformPrivilegedEligibilityPrerequisiteResolver,
)
from tools.eos.auth.current_privileged_eligibility import CurrentPrivilegedEligibilityResolver
from tools.eos.auth.current_system_permission_possession import CurrentSystemPermissionPossessionResolver
from tools.eos.auth.platform_privileged_eligibility_prerequisite_registry import (
    PlatformPrivilegedEligibilityPrerequisiteRegistry,
    COLLECTION as PLATFORM_PREREQUISITE_COLLECTION,
)
from tools.eos.auth.privileged_activation_registry import (
    PrivilegedActivationRegistry,
    COLLECTION as ACTIVATION_COLLECTION,
)
from tools.eos.auth.privileged_activation_use_authority import PrivilegedActivationUseAuthority
from tools.eos.auth.privileged_eligibility_evidence_registry import (
    PrivilegedEligibilityEvidenceRegistry,
    COLLECTION as ELIGIBILITY_EVIDENCE_COLLECTION,
)
from tools.eos.auth.principal_authority_repository import PRINCIPAL_AUTHORITY_COLLECTION
from tools.eos.auth.system_permission_assignment_registry import (
    SystemPermissionAssignmentRegistry,
    COLLECTION as SYSTEM_PERMISSION_ASSIGNMENT_COLLECTION,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_production_composition import (
    LegalEvidenceProviderReadOnlyReconciliationProductionComposition,
    build_legal_evidence_provider_readonly_reconciliation_production_composition,
)

AUDIT_URI_ENV = "WILSY_LEGAL_EVIDENCE_RECONCILIATION_AUDIT_MONGODB_URI"


class LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(RuntimeError):
    """Stable startup error without exposing deployment secrets."""


def build_legal_evidence_provider_readonly_reconciliation_runtime(
    *,
    mongo_database: Any,
    env: Mapping[str, str] | None = None,
) -> tuple[LegalEvidenceProviderReadOnlyReconciliationProductionComposition, Any]:
    """Build runtime authority from canonical Mongo collections and explicit config.

    The returned audit client must be retained for application lifetime and
    closed during shutdown. Audit indexes are verified by the composition but
    never created here. Missing or malformed deployment configuration fails
    closed; no fallback URI, audience, tenant, bucket, or workload key exists.
    """
    values = os.environ if env is None else env
    audit_uri = values.get(AUDIT_URI_ENV, "")
    if not isinstance(audit_uri, str) or not audit_uri.strip():
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "RECONCILIATION_AUDIT_URI_REQUIRED"
        )
    if mongo_database is None or getattr(mongo_database, "client", None) is None:
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "CANONICAL_BUSINESS_DATABASE_REQUIRED"
        )

    audit_client = None
    try:
        audit_client = MongoClient(
            audit_uri.strip(),
            tz_aware=True,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        audit_client.admin.command("ping")
        audit_database = audit_client.get_database()
        if audit_database.client is not audit_client or audit_database.client is mongo_database.client:
            raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
                "RECONCILIATION_AUDIT_CLIENT_INVALID"
            )

        workload_keys, _service_id, expected_audience = _service_config(values)
        database = mongo_database
        principals = database[PRINCIPAL_AUTHORITY_COLLECTION]

        prerequisite_registry = PlatformPrivilegedEligibilityPrerequisiteRegistry(
            database[PLATFORM_PREREQUISITE_COLLECTION]
        )
        eligibility_registry = PrivilegedEligibilityEvidenceRegistry(
            database[ELIGIBILITY_EVIDENCE_COLLECTION]
        )
        assignment_registry = SystemPermissionAssignmentRegistry(
            database[SYSTEM_PERMISSION_ASSIGNMENT_COLLECTION]
        )
        activation_registry = PrivilegedActivationRegistry(
            database[ACTIVATION_COLLECTION]
        )

        # Existing canonical registry index methods are deployment-startup work,
        # never request-path DDL.
        prerequisite_registry.ensure_indexes()
        eligibility_registry.ensure_indexes()
        assignment_registry.ensure_indexes()
        activation_registry.ensure_indexes()

        platform_resolver = CurrentPlatformPrivilegedEligibilityPrerequisiteResolver(
            principal_collection=principals,
            prerequisite_registry=prerequisite_registry,
        )
        eligibility_resolver = CurrentPrivilegedEligibilityResolver(
            principal_collection=principals,
            membership_collection=database["tenant_memberships"],
            evidence_registry=eligibility_registry,
            platform_prerequisite_resolver=platform_resolver,
            workforce_relationship_collection=database["workforce_relationships"],
        )
        possession_resolver = CurrentSystemPermissionPossessionResolver(
            principal_collection=principals,
            assignment_registry=assignment_registry,
        )
        use_authority = PrivilegedActivationUseAuthority(
            activation_registry=activation_registry,
            eligibility_resolver=eligibility_resolver,
            noninteractive_assurance_service=_production_noninteractive_assurance_service(
                database=database
            ),
        )
        composition = build_legal_evidence_provider_readonly_reconciliation_production_composition(
            mongo_database=database,
            audit_database=audit_database,
            audit_client=audit_client,
            use_authority=use_authority,
            permission_possession_resolver=possession_resolver,
            workload_keys=workload_keys,
            expected_audience=expected_audience,
            env=values,
        )
        if composition.business_client is not database.client:
            raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
                "RECONCILIATION_BUSINESS_CLIENT_BINDING_MISMATCH"
            )
        return composition, audit_client
    except Exception as error:
        if audit_client is not None:
            audit_client.close()
        if isinstance(error, LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError):
            raise
        raise LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError(
            "RECONCILIATION_RUNTIME_COMPOSITION_UNAVAILABLE"
        ) from error


__all__ = [
    "AUDIT_URI_ENV",
    "LegalEvidenceProviderReadOnlyReconciliationRuntimeBootstrapError",
    "build_legal_evidence_provider_readonly_reconciliation_runtime",
]
