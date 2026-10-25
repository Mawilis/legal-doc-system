"""Governed production composition for Legal Evidence read-only reconciliation.

VERSION: v1.0.0-L10A2R-C4D7C-EXPLICIT-PRODUCTION-COMPOSITION
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

This module composes already-governed IAM authorities with server-owned tenant
and provider configuration, the read-only S3 facade, and a platform-scoped
independent audit registry. It deliberately does not mount an HTTP route, start
a Mongo transaction, or invent a transport trust boundary. An approved transport
adapter must pass the canonical signed-workload fields extracted from its actual
request and own the business transaction lifecycle.

Audit uniqueness indexes must be provisioned explicitly before invocation is
enabled. A composition is unusable until that step succeeds.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from tools.eos.auth.current_system_permission_possession import (
    CurrentSystemPermissionPossessionResolver,
)
from tools.eos.auth.platform_authorization_decision_evidence_registry import (
    COLLECTION as PLATFORM_DECISION_EVIDENCE_COLLECTION,
    PlatformAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.privileged_activation_use_authority import (
    PrivilegedActivationUseAuthority,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_authorization_gate import (
    LegalEvidenceProviderReadOnlyReconciliationAuthorization,
    LegalEvidenceProviderReadOnlyReconciliationAuthorizationGate,
    LegalEvidenceProviderReadOnlyReconciliationAuthorizationError,
    ServerConfiguredReconciliationTarget,
    build_server_configured_reconciliation_target,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_factory import (
    LegalEvidenceProviderReadOnlyReconciliationDependencies,
    build_legal_evidence_provider_readonly_reconciliation_dependencies,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_provider import (
    LegalEvidenceProviderReadOnlyReconciliationProvider,
)
from tools.eos.legal_operations.service.legal_evidence_s3_storage_adapter import (
    LegalEvidenceS3StorageAdapter,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_coordinator import (
    LegalEvidenceProviderReadOnlyReconciliationResult,
)


VERSION = "v1.0.0-L10A2R-C4D7C-EXPLICIT-PRODUCTION-COMPOSITION"


class LegalEvidenceProviderReadOnlyReconciliationCompositionError(RuntimeError):
    """Stable fail-closed error for invalid production composition."""


class PlatformAuthorizationDecisionEvidenceIndexProvisioner:
    """Deployment-only index provisioner backed by a distinct MongoClient.

    Construct this with deployment credentials during governed setup. Do not
    pass the runtime audit client: runtime request handling should only need
    the collection permissions required to append/read evidence.
    """

    __slots__ = ("_client", "_database_name", "_registry")

    def __init__(self, *, audit_database: Any, audit_client: Any) -> None:
        if (
            audit_database is None
            or audit_client is None
            or getattr(audit_database, "client", None) is not audit_client
            or not callable(getattr(audit_client, "start_session", None))
        ):
            raise LegalEvidenceProviderReadOnlyReconciliationCompositionError(
                "DEPLOYMENT_AUDIT_INDEX_CLIENT_INVALID"
            )
        try:
            collection = audit_database[PLATFORM_DECISION_EVIDENCE_COLLECTION]
            self._registry = PlatformAuthorizationDecisionEvidenceRegistry(
                collection,
                audit_client=audit_client,
            )
            self._database_name = audit_database.name
        except Exception as error:
            raise LegalEvidenceProviderReadOnlyReconciliationCompositionError(
                "DEPLOYMENT_AUDIT_INDEX_DATABASE_INVALID"
            ) from error
        self._client = audit_client

    @property
    def audit_client(self) -> Any:
        return self._client

    @property
    def database_name(self) -> str:
        return self._database_name

    def provision(self) -> None:
        self._registry.ensure_indexes()


class LegalEvidenceProviderReadOnlyReconciliationProductionComposition:
    """Explicit composition root; does not own request or transaction lifecycle."""

    __slots__ = (
        "_target",
        "_registry",
        "_gate",
        "_dependencies",
        "_audit_indexes_provisioned",
    )

    def __init__(
        self,
        *,
        target: ServerConfiguredReconciliationTarget,
        registry: PlatformAuthorizationDecisionEvidenceRegistry,
        gate: LegalEvidenceProviderReadOnlyReconciliationAuthorizationGate,
        dependencies: LegalEvidenceProviderReadOnlyReconciliationDependencies,
    ) -> None:
        self._target = target
        self._registry = registry
        self._gate = gate
        self._dependencies = dependencies
        try:
            self._audit_indexes_provisioned = registry.verify_indexes() is True
        except Exception as error:
            raise LegalEvidenceProviderReadOnlyReconciliationCompositionError(
                "PLATFORM_DECISION_AUDIT_INDEX_VERIFICATION_FAILED"
            ) from error
        if not self._audit_indexes_provisioned:
            raise LegalEvidenceProviderReadOnlyReconciliationCompositionError(
                "PLATFORM_DECISION_AUDIT_INDEXES_NOT_PROVISIONED"
            )

    @property
    def audit_indexes_provisioned(self) -> bool:
        """Whether this instance successfully completed explicit index setup."""
        return self._audit_indexes_provisioned

    def authorize_and_reconcile(
        self,
        *,
        signed_workload_fields: Mapping[str, str],
        body: bytes,
        idempotency_key: str,
        at: datetime,
        session: object,
    ) -> LegalEvidenceProviderReadOnlyReconciliationResult:
        """Authorize and reconcile one request using the caller-owned session.

        `signed_workload_fields` must be produced by the approved transport
        adapter from the actual incoming signed-workload request. This method
        does not trust tenant/provider/identity values from that mapping; the
        gate verifies the signed request and derives identity, while target
        tenant/provider coordinates come only from the deployment composition.
        On any exception after transaction start, the caller must abort its
        transaction. The platform audit registry uses a distinct client.
        """
        if not self._audit_indexes_provisioned:
            raise LegalEvidenceProviderReadOnlyReconciliationCompositionError(
                "PLATFORM_DECISION_AUDIT_INDEXES_NOT_PROVISIONED"
            )
        authorization: LegalEvidenceProviderReadOnlyReconciliationAuthorization
        authorization = self._gate.authorize(
            request=signed_workload_fields,
            body=body,
            idempotency_key=idempotency_key,
            at=at,
            session=session,
        )
        return self._dependencies.coordinator.reconcile(
            scope=authorization.scope,
            provider_name=authorization.provider_name,
            observed_at=at,
            session=session,
        )


def build_legal_evidence_provider_readonly_reconciliation_production_composition(
    *,
    mongo_database: Any,
    audit_database: Any,
    audit_client: Any,
    use_authority: PrivilegedActivationUseAuthority,
    permission_possession_resolver: CurrentSystemPermissionPossessionResolver,
    workload_keys: Mapping[str, tuple[str, str]],
    expected_audience: str,
    env: Mapping[str, str] | None = None,
    s3_client: Any | None = None,
) -> LegalEvidenceProviderReadOnlyReconciliationProductionComposition:
    """Compose deployment-owned dependencies without mounting an entry point.

    The canonical business database and audit database must be attached to
    distinct MongoClient instances. Index provisioning is a separate explicit
    deployment step; the runtime composition verifies indexes read-only. No S3 network operation, Mongo write, transaction start,
    or runtime route registration occurs during composition.
    """
    if mongo_database is None or audit_database is None:
        raise LegalEvidenceProviderReadOnlyReconciliationCompositionError(
            "BUSINESS_AND_AUDIT_DATABASES_REQUIRED"
        )
    business_client = getattr(mongo_database, "client", None)
    configured_audit_client = getattr(audit_database, "client", None)
    if (
        business_client is None
        or audit_client is None
        or configured_audit_client is not audit_client
        or business_client is audit_client
    ):
        raise LegalEvidenceProviderReadOnlyReconciliationCompositionError(
            "DISTINCT_SERVER_OWNED_AUDIT_CLIENT_REQUIRED"
        )
    if type(use_authority) is not PrivilegedActivationUseAuthority:
        raise LegalEvidenceProviderReadOnlyReconciliationCompositionError(
            "CANONICAL_P5_USE_AUTHORITY_REQUIRED"
        )
    if type(permission_possession_resolver) is not CurrentSystemPermissionPossessionResolver:
        raise LegalEvidenceProviderReadOnlyReconciliationCompositionError(
            "CANONICAL_SYSTEM_PERMISSION_RESOLVER_REQUIRED"
        )

    target = build_server_configured_reconciliation_target(
        mongo_database=mongo_database,
        env=env,
    )
    adapter = LegalEvidenceS3StorageAdapter(
        target.storage_configuration,
        client=s3_client,
    )
    provider = LegalEvidenceProviderReadOnlyReconciliationProvider(adapter)
    try:
        dependencies = build_legal_evidence_provider_readonly_reconciliation_dependencies(
            provider=provider,
            mongo_database=mongo_database,
        )
        audit_collection = audit_database[PLATFORM_DECISION_EVIDENCE_COLLECTION]
        registry = PlatformAuthorizationDecisionEvidenceRegistry(
            audit_collection,
            audit_client=audit_client,
        )
        gate = LegalEvidenceProviderReadOnlyReconciliationAuthorizationGate(
            use_authority=use_authority,
            permission_possession_resolver=permission_possession_resolver,
            scope_resolver=target.scope_resolver,
            workload_keys=workload_keys,
            expected_audience=expected_audience,
            provider_name=target.provider_name,
            decision_evidence_registry=registry,
        )
    except LegalEvidenceProviderReadOnlyReconciliationCompositionError:
        raise
    except Exception as error:
        raise LegalEvidenceProviderReadOnlyReconciliationCompositionError(
            "PRODUCTION_COMPOSITION_INVALID"
        ) from error

    return LegalEvidenceProviderReadOnlyReconciliationProductionComposition(
        target=target,
        registry=registry,
        gate=gate,
        dependencies=dependencies,
    )


__all__ = [
    "VERSION",
    "LegalEvidenceProviderReadOnlyReconciliationCompositionError",
    "PlatformAuthorizationDecisionEvidenceIndexProvisioner",
    "LegalEvidenceProviderReadOnlyReconciliationProductionComposition",
    "build_legal_evidence_provider_readonly_reconciliation_production_composition",
]
