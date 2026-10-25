"""
TITLE:
    WILSY OS Legal Evidence Read-Only Reconciliation Production Composition

VERSION:
    v1.0.1-L10A2R-C4D7C-SOVEREIGN-COMPOSITION-SEAL

AUTHORITY:
    WILSY OS Core Governance / Python EOS Legal Operations

EPITOME:
    Compose canonical P5 privileged-use authority, current SYSTEM permission
    possession, server-configured tenant/provider scope, a strictly read-only
    provider facade, caller-owned business transaction semantics, and an
    independently durable platform authorization decision-evidence registry.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_production_composition.py

COLLABORATION / OWNERSHIP:
    This composition binds existing governed authorities and does not mint
    authority. The approved invocation owner supplies the actual signed ASGI
    request, idempotency contract, active business session, and commit/abort
    lifecycle. Deployment operations own the distinct audit client and explicit
    index provisioning. This module does not mount a route.

CERTIFICATION OR UPDATE DATE:
    2026-10-25

CHANGELOG:
    v1.0.1-L10A2R-C4D7C-SOVEREIGN-COMPOSITION-SEAL
        Adds the mandatory institutional source header and matching sovereign
        end seal. Runtime behavior is unchanged.

    v1.0.0-L10A2R-C4D7C-EXPLICIT-PRODUCTION-COMPOSITION
        Composes canonical authorization, server-owned target, strict read-only
        S3 provider facade, caller-owned business session, and independent
        platform authorization decision evidence. Runtime verifies audit index
        shape and availability; deployment provisions indexes separately.

COMPLIANCE:
    Fail-closed authority composition; tenant isolation; independent durable
    authorization evidence; caller-owned transaction boundaries; no inference
    of provider deletion, orphan proof, retention clearance, or financial truth.

SECURITY / PRIVACY POSTURE:
    Business and audit Mongo clients must be distinct. Audit index verification
    is read-only during runtime composition. No provider network call, business
    write, audit write, session creation, transaction start, or route mount is
    performed by construction. Authorization/audit failures reject closed.

TENANT BOUNDARY:
    Tenant/provider target comes only from validated server configuration and
    canonical tenant registry resolution in the caller's active session.
    Request-supplied tenant, provider, or identity values are not authority.

AUTHORITY BOUNDARY:
    Composition only. P5 current use, exact SYSTEM permission possession,
    signed workload verification, scope resolution, and durable ALLOW/DENY
    evidence remain delegated to canonical authorities. This module does not
    issue privileges or authorize production deployment by its existence.

FINANCIAL AUTHORITY BOUNDARY:
    NONE. Kennel EOS remains the exclusive financial execution authority.
"""
from __future__ import annotations

from datetime import datetime
from hashlib import sha3_512
import json
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
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_idempotency_registry import (
    LegalEvidenceReconciliationOperationIdempotencyRegistry,
)


VERSION = "v1.0.1-L10A2R-C4D7C-SOVEREIGN-COMPOSITION-SEAL"


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

    def verify(self) -> bool:
        """Read-only verification of the deployment-provisioned index contract."""
        return self._registry.verify_indexes()


class LegalEvidenceProviderReadOnlyReconciliationProductionComposition:
    """Explicit composition root; does not own request or transaction lifecycle."""

    __slots__ = (
        "_target",
        "_business_client",
        "_registry",
        "_gate",
        "_dependencies",
        "_idempotency_registry",
        "_audit_indexes_provisioned",
    )

    def __init__(
        self,
        *,
        target: ServerConfiguredReconciliationTarget,
        business_client: Any,
        registry: PlatformAuthorizationDecisionEvidenceRegistry,
        gate: LegalEvidenceProviderReadOnlyReconciliationAuthorizationGate,
        dependencies: LegalEvidenceProviderReadOnlyReconciliationDependencies,
        idempotency_registry: LegalEvidenceReconciliationOperationIdempotencyRegistry | None = None,
    ) -> None:
        if business_client is None or not callable(getattr(business_client, "start_session", None)):
            raise LegalEvidenceProviderReadOnlyReconciliationCompositionError(
                "CANONICAL_BUSINESS_CLIENT_REQUIRED"
            )
        self._target = target
        self._business_client = business_client
        self._registry = registry
        self._gate = gate
        self._dependencies = dependencies
        self._idempotency_registry = idempotency_registry
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

    @property
    def business_client(self) -> Any:
        """The exact deployment-owned business client used to build this graph."""
        return self._business_client

    def authorize_and_reconcile_idempotently(
        self,
        *,
        signed_workload_fields: Mapping[str, str],
        body: bytes,
        idempotency_key: str,
        at: datetime,
        session: object,
    ) -> dict[str, Any]:
        """Authorize every request and replay the exact durable operation result.

        The operation result is stored in the canonical business transaction.
        Correlation and nonce are deliberately not operation keys. Every retry
        must carry a fresh signed nonce; it receives the same cached response
        when service, operation key, exact signed body, and server-owned scope
        match. A changed request or scope conflicts rather than overwriting.
        """
        registry = self._idempotency_registry
        if registry is None:
            raise LegalEvidenceProviderReadOnlyReconciliationCompositionError(
                "RECONCILIATION_OPERATION_IDEMPOTENCY_UNAVAILABLE"
            )
        service_id = signed_workload_fields.get("service_id", "")
        nonce = signed_workload_fields.get("nonce", "")
        key_id = signed_workload_fields.get("key_id", "")
        if not all(isinstance(value, str) and value for value in (service_id, nonce, key_id)):
            raise LegalEvidenceProviderReadOnlyReconciliationCompositionError(
                "RECONCILIATION_SIGNED_WORKLOAD_CONTEXT_INVALID"
            )
        audit_key_material = "\\0".join(
            ("legal-evidence-provider-reconciliation", service_id, key_id, nonce, idempotency_key)
        ).encode("utf-8")
        authorization_audit_key = (
            "legal-evidence-provider-reconciliation:"
            + sha3_512(audit_key_material).hexdigest()
        )
        authorization = self._gate.authorize(
            request=signed_workload_fields,
            body=body,
            idempotency_key=authorization_audit_key,
            at=at,
            session=session,
        )
        fingerprint_material = {
            "operation": "L10A2R_C4D7_RECONCILIATION",
            "service_id": service_id,
            "idempotency_key": idempotency_key,
            "body_sha3_512": signed_workload_fields.get("body_sha3_512", ""),
            "method": signed_workload_fields.get("method", ""),
            "path": signed_workload_fields.get("path", ""),
            "audience": signed_workload_fields.get("audience", ""),
            "tenant_id": authorization.scope.tenant_id,
            "tenant_scope_fingerprint": authorization.scope.tenant_scope_fingerprint,
            "provider_name": authorization.provider_name,
        }
        request_fingerprint = sha3_512(
            json.dumps(
                fingerprint_material,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()
        cached = registry.lookup(
            service_id=service_id,
            idempotency_key=idempotency_key,
            request_fingerprint=request_fingerprint,
            session=session,
        )
        if cached is not None:
            return cached

        result = self._dependencies.coordinator.reconcile(
            scope=authorization.scope,
            provider_name=authorization.provider_name,
            observed_at=at,
            session=session,
        )
        response: dict[str, Any] = {
            "tenant_id": result.tenant_id,
            "tenant_scope_fingerprint": result.tenant_scope_fingerprint,
            "provider_name": result.provider_name,
            "observed_at": result.observed_at.isoformat(),
            "coverage_verification_fingerprint": result.coverage_verification_fingerprint,
            "incomplete_observation_count": result.incomplete_observation_count,
            "completed_observation_count": result.completed_observation_count,
            "classification_count": len(result.classifications),
            "write_intent_correlation_count": len(result.write_intent_correlations),
            "coverage_complete": result.coverage_complete,
            "orphan_proven": result.orphan_proven,
            "provider_delete_authorized": result.provider_delete_authorized,
            "cleanup_authorized": result.cleanup_authorized,
        }
        registry.record(
            service_id=service_id,
            idempotency_key=idempotency_key,
            request_fingerprint=request_fingerprint,
            response=response,
            session=session,
        )
        return response

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
    idempotency_registry: LegalEvidenceReconciliationOperationIdempotencyRegistry | None = None,
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
        business_client=business_client,
        registry=registry,
        gate=gate,
        dependencies=dependencies,
        idempotency_registry=idempotency_registry,
    )


__all__ = [
    "VERSION",
    "LegalEvidenceProviderReadOnlyReconciliationCompositionError",
    "PlatformAuthorizationDecisionEvidenceIndexProvisioner",
    "LegalEvidenceProviderReadOnlyReconciliationProductionComposition",
    "build_legal_evidence_provider_readonly_reconciliation_production_composition",
]

# ARTIFACT: legal_evidence_provider_readonly_reconciliation_production_composition.py
# VERSION: v1.0.1-L10A2R-C4D7C-SOVEREIGN-COMPOSITION-SEAL
# AUTHORITY BOUNDARY: Governed composition only; no route or privilege issuance.
# TENANT POSTURE: Fixed server-owned tenant/provider target; no request-selected scope.
# FAIL-CLOSED POSTURE: Invalid authority, audit client, or audit indexes reject composition.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
