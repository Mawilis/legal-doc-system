"""
TITLE:
    WILSY OS Legal Evidence Provider Read-Only Reconciliation Authorization Gate

VERSION:
    v1.0.5-L10A2R-C4D7C-STRICT-TENANT-STATUS

AUTHORITY:
    Wilsy OS Sovereign IAM and Legal Operations

EPITOME:
    Compose one verified internal workload request, current platform-root
    privileged use, exact current SYSTEM reconciliation-read permission
    possession, and server-owned tenant scope resolution before returning a
    read-only reconciliation authorization result.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_authorization_gate.py

COLLABORATION / OWNERSHIP:
    Reuses the canonical P5 current-use authority and current SYSTEM permission
    possession resolver. The caller owns the active Mongo transaction and the
    server composition root owns workload keys, audience, provider identity, and
    the scope-resolver implementation.

CERTIFICATION / UPDATE DATE:
    2026-10-25

CHANGELOG:
    v1.0.5-L10A2R-C4D7C-STRICT-TENANT-STATUS
        Separates canonical tenant identity mismatch from a non-ACTIVE tenant
        status. Archived/inactive tenants now fail with the explicit
        CANONICAL_TENANT_SCOPE_NOT_ACTIVE denial code.

COMPLIANCE:
    Fail-closed. No caller-selected tenant/provider scope, no tenant permission
    substitution, no role-string trust, no wildcard permission, and no fallback
    scope. Scope resolution remains unavailable until a canonical resolver is
    supplied by the server composition root.

SECURITY / PRIVACY POSTURE:
    Request headers/body are supplied by the trusted transport adapter. Workload
    keys and expected audience are fixed at construction from server-controlled
    configuration. The same active session is propagated through P3, P4/P2,
    permission possession, and scope resolution.

TENANT BOUNDARY:
    The operator activation is platform-root scoped with tenant_id=None.
    Reconciliation target tenant scope is separately resolved from a
    server-owned provider-bound scope authority and is never accepted as a
    request parameter.

AUTHORITY BOUNDARY:
    Returns a narrow authorization result for read-only reconciliation only.
    It does not create permissions or activations, prove orphanhood, authorize
    cleanup, release retention/legal hold, delete provider objects, or create
    financial authority.

FINANCIAL AUTHORITY BOUNDARY:
    NONE. Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha3_512
import os
from typing import Any, Mapping, Protocol

from tools.eos.auth.current_system_permission_possession import (
    CurrentSystemPermissionPossessionError,
    CurrentSystemPermissionPossessionResolver,
)
from tools.eos.auth.system_permission_assignment import (
    SystemPermissionAssignment,
)
from tools.eos.saas.tenancy.tenant_registry import (
    TenantRegistry,
    TenantRegistryError,
)
from tools.eos.legal_operations.service.legal_evidence_s3_storage_adapter import (
    DEFAULT_REGION,
    PROVIDER_NAME,
    LegalEvidenceS3Configuration,
    LegalEvidenceS3StorageAdapterError,
)
from tools.eos.auth.privileged_activation import (
    PrivilegedActivation,
)
from tools.eos.auth.privileged_activation_use_authority import (
    PrivilegedActivationUseAuthority,
    PrivilegedActivationUseError,
    PrivilegedActivationUseResult,
)
from tools.eos.auth.privileged_eligibility import (
    SOVEREIGN_ARCHITECT,
    PrivilegedTargetClass,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceProviderDiscoveryScope,
)


VERSION = "v1.0.5-L10A2R-C4D7C-STRICT-TENANT-STATUS"
RECONCILIATION_READ_PERMISSION = (
    "legal_operations:evidence_provider_reconciliation:read"
)
_TRUSTED_REQUEST_FIELDS = frozenset({
    "version",
    "service_id",
    "audience",
    "key_id",
    "timestamp",
    "nonce",
    "body_sha3_512",
    "correlation_id",
    "signature",
    "method",
    "path",
})


class LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
    RuntimeError
):
    """Structured fail-closed reconciliation authorization error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class ServerOwnedReconciliationScopeResolutionError(RuntimeError):
    """Canonical fail-closed scope-resolution error with a stable code."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class ServerOwnedReconciliationScopeResolver(Protocol):
    """Server-owned, provider-bound target-scope resolution contract.

    Implementations must select scope from canonical server configuration or
    governed work state. The resolver is bound to one provider at construction.
    The contract intentionally accepts no request tenant, provider name, bucket,
    prefix, or object identifier.
    """

    @property
    def provider_name(self) -> str:
        """Return the server-configured provider identity bound to this resolver."""
        ...

    def resolve_scope(
        self,
        *,
        principal_id: str,
        activation_id: str,
        at: datetime,
        session: object,
    ) -> LegalEvidenceProviderDiscoveryScope:
        """Return one exact tenant scope from server-owned authority."""
        ...


class ServerConfiguredReconciliationScopeResolver:
    """Resolve one server-configured tenant through canonical TenantRegistry.

    The tenant identifier and provider name are deployment-owned constructor
    values, never request parameters. Tenant currentness is reread through the
    canonical registry using the exact caller-owned transaction. One resolver
    instance is intentionally bound to one tenant/provider pair.
    """

    def __init__(
        self,
        *,
        tenant_id: str,
        provider_name: str,
        tenant_collection: Any,
    ) -> None:
        if (
            not isinstance(tenant_id, str)
            or not tenant_id
            or tenant_id != tenant_id.strip()
            or "*" in tenant_id
        ):
            raise ServerOwnedReconciliationScopeResolutionError(
                "SERVER_CONFIGURED_TENANT_ID_INVALID"
            )
        if (
            not isinstance(provider_name, str)
            or not provider_name
            or provider_name != provider_name.strip()
            or "*" in provider_name
        ):
            raise ServerOwnedReconciliationScopeResolutionError(
                "SERVER_CONFIGURED_PROVIDER_NAME_INVALID"
            )
        if not callable(getattr(tenant_collection, "find_one", None)):
            raise ServerOwnedReconciliationScopeResolutionError(
                "CANONICAL_TENANT_COLLECTION_REQUIRED"
            )
        self._tenant_id = tenant_id
        self._provider_name = provider_name
        self._tenant_collection = tenant_collection

    @property
    def provider_name(self) -> str:
        """Return the fixed server-configured provider binding."""
        return self._provider_name

    def resolve_scope(
        self,
        *,
        principal_id: str,
        activation_id: str,
        at: datetime,
        session: object,
    ) -> LegalEvidenceProviderDiscoveryScope:
        """Reread the fixed canonical tenant and derive its exact scope.

        \`principal_id\` and \`activation_id\` correlate the caller's already
        authorized platform operation. They cannot select or change the target
        tenant/provider pair.
        """
        del principal_id, activation_id, at
        try:
            tenant = TenantRegistry.get(
                self._tenant_id,
                collection=self._tenant_collection,
                session=session,
            )
        except TenantRegistryError as error:
            code = str(error)
            if "INACTIVE" in code or "ARCHIVED" in code:
                raise ServerOwnedReconciliationScopeResolutionError(
                    "CANONICAL_TENANT_SCOPE_NOT_ACTIVE"
                ) from error
            raise ServerOwnedReconciliationScopeResolutionError(
                "CANONICAL_TENANT_CURRENTNESS_UNAVAILABLE"
            ) from error

        if tenant is None:
            raise ServerOwnedReconciliationScopeResolutionError(
                "CANONICAL_TENANT_SCOPE_NOT_ACTIVE"
            )
        if getattr(tenant, "tenant_id", None) != self._tenant_id:
            raise ServerOwnedReconciliationScopeResolutionError(
                "CANONICAL_TENANT_SCOPE_BINDING_INVALID"
            )
        if str(getattr(tenant, "status", "")).upper() != "ACTIVE":
            raise ServerOwnedReconciliationScopeResolutionError(
                "CANONICAL_TENANT_SCOPE_NOT_ACTIVE"
            )

        fingerprint = sha3_512(
            self._tenant_id.encode("utf-8")
        ).hexdigest()
        return LegalEvidenceProviderDiscoveryScope(
            tenant_id=self._tenant_id,
            tenant_scope_fingerprint=fingerprint,
        )


@dataclass(frozen=True, slots=True)
class ServerConfiguredReconciliationTarget:
    """One immutable deployment-configured tenant/provider target.

    The S3 configuration is the same validated configuration object that the
    runtime must use to construct its provider adapter. It is not caller input.
    """

    tenant_id: str
    provider_name: str
    storage_configuration: LegalEvidenceS3Configuration
    scope_resolver: ServerConfiguredReconciliationScopeResolver


def build_server_configured_reconciliation_target(
    *,
    mongo_database: Any,
    env: Mapping[str, str] | None = None,
) -> ServerConfiguredReconciliationTarget:
    """Resolve one server-configured tenant and existing S3 provider config.

    Required deployment variables:
        WILSY_LEGAL_EVIDENCE_RECONCILIATION_TENANT_ID
        WILSY_LEGAL_EVIDENCE_S3_BUCKET

    The region and KMS key follow the existing Legal Evidence S3 adapter
    configuration contract. The function performs no network calls, index
    creation, database writes, or provider operations.
    """
    values = os.environ if env is None else env
    tenant_id = values.get(
        "WILSY_LEGAL_EVIDENCE_RECONCILIATION_TENANT_ID",
        "",
    )
    bucket = values.get("WILSY_LEGAL_EVIDENCE_S3_BUCKET", "")
    region = values.get("WILSY_LEGAL_EVIDENCE_S3_REGION", DEFAULT_REGION)
    kms_key = values.get("WILSY_LEGAL_EVIDENCE_S3_KMS_KEY_ID", "") or None

    if (
        not isinstance(tenant_id, str)
        or not tenant_id
        or tenant_id != tenant_id.strip()
        or "*" in tenant_id
    ):
        raise ServerOwnedReconciliationScopeResolutionError(
            "SERVER_CONFIGURED_TENANT_ID_REQUIRED"
        )
    if (
        not isinstance(bucket, str)
        or not bucket
        or bucket != bucket.strip()
    ):
        raise ServerOwnedReconciliationScopeResolutionError(
            "SERVER_S3_BUCKET_CONFIGURATION_REQUIRED"
        )
    if mongo_database is None or not callable(
        getattr(mongo_database, "__getitem__", None)
    ):
        raise ServerOwnedReconciliationScopeResolutionError(
            "CANONICAL_TENANT_DATABASE_REQUIRED"
        )

    try:
        storage_configuration = LegalEvidenceS3Configuration(
            bucket=bucket,
            region=region,
            kms_key_id=kms_key,
        )
    except LegalEvidenceS3StorageAdapterError as error:
        raise ServerOwnedReconciliationScopeResolutionError(
            "SERVER_S3_CONFIGURATION_INVALID"
        ) from error

    try:
        tenant_collection = mongo_database["tenants"]
    except (KeyError, TypeError) as error:
        raise ServerOwnedReconciliationScopeResolutionError(
            "CANONICAL_TENANT_COLLECTION_REQUIRED"
        ) from error

    resolver = ServerConfiguredReconciliationScopeResolver(
        tenant_id=tenant_id,
        provider_name=PROVIDER_NAME,
        tenant_collection=tenant_collection,
    )
    return ServerConfiguredReconciliationTarget(
        tenant_id=tenant_id,
        provider_name=PROVIDER_NAME,
        storage_configuration=storage_configuration,
        scope_resolver=resolver,
    )


@dataclass(frozen=True, slots=True)
class LegalEvidenceProviderReadOnlyReconciliationAuthorization:
    """Narrow authorization evidence for one read-only reconciliation attempt.

    This value is not an IAM grant or reusable bearer token. It binds the
    verified operator, current activation, current permission assignment,
    server-resolved tenant scope, configured provider, and authorization time.
    """

    principal_id: str
    activation_id: str
    permission_assignment_id: str
    permission_assignment_fingerprint: str
    scope: LegalEvidenceProviderDiscoveryScope
    provider_name: str
    authorized_at: datetime


class LegalEvidenceProviderReadOnlyReconciliationAuthorizationGate:
    """Compose canonical operator IAM and server-owned target scope.

    Authority:
        Internal platform operator only. Uses P5 current use and the canonical
        current SYSTEM permission possession resolver; does not create authority.

    Transaction ownership:
        Every operation uses the supplied already-active caller-owned session.
        The caller must abort the transaction if any step fails after P3 has
        composed evidence. This gate never starts, commits, aborts, or retries.

    Scope:
        The configured provider name and scope resolver are server dependencies.
        The request cannot choose a tenant or provider.
    """

    def __init__(
        self,
        *,
        use_authority: PrivilegedActivationUseAuthority,
        permission_possession_resolver: CurrentSystemPermissionPossessionResolver,
        scope_resolver: ServerOwnedReconciliationScopeResolver,
        workload_keys: Mapping[str, tuple[str, str]],
        expected_audience: str,
        provider_name: str,
    ) -> None:
        if type(use_authority) is not PrivilegedActivationUseAuthority:
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "P5_USE_AUTHORITY_REQUIRED"
            )
        if (
            type(permission_possession_resolver)
            is not CurrentSystemPermissionPossessionResolver
        ):
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "CURRENT_SYSTEM_PERMISSION_RESOLVER_REQUIRED"
            )
        if not callable(getattr(scope_resolver, "resolve_scope", None)):
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "SERVER_OWNED_SCOPE_RESOLVER_REQUIRED"
            )
        if not isinstance(getattr(scope_resolver, "provider_name", None), str):
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "SERVER_OWNED_SCOPE_PROVIDER_BINDING_REQUIRED"
            )
        if not isinstance(workload_keys, Mapping) or not workload_keys:
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "SERVER_WORKLOAD_KEYS_REQUIRED"
            )
        for key_id, pair in workload_keys.items():
            if (
                not isinstance(key_id, str)
                or not key_id
                or key_id != key_id.strip()
                or not isinstance(pair, tuple)
                or len(pair) != 2
                or any(
                    not isinstance(item, str) or not item
                    for item in pair
                )
            ):
                raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                    "SERVER_WORKLOAD_KEYS_INVALID"
                )
        for name, value in (
            ("EXPECTED_AUDIENCE", expected_audience),
            ("PROVIDER_NAME", provider_name),
        ):
            if (
                not isinstance(value, str)
                or not value
                or value != value.strip()
                or "*" in value
            ):
                raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                    name + "_INVALID"
                )

        self._use_authority = use_authority
        self._permission_possession_resolver = permission_possession_resolver
        if scope_resolver.provider_name != provider_name:
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "SERVER_OWNED_SCOPE_PROVIDER_MISMATCH"
            )
        self._scope_resolver = scope_resolver
        self._workload_keys = dict(workload_keys)
        self._expected_audience = expected_audience
        self._provider_name = provider_name

    def authorize(
        self,
        *,
        request: Mapping[str, str],
        body: bytes,
        idempotency_key: str,
        at: datetime,
        session: object,
    ) -> LegalEvidenceProviderReadOnlyReconciliationAuthorization:
        """Authorize one workload request and resolve a server-owned scope.

        Caller supplies only the actual transport-derived request headers/body,
        idempotency key, evaluation time, and active session. Tenant/provider
        scope, workload keys, audience, operator role, and permission identifier
        are fixed by server-side dependencies and this gate's policy.
        """
        if (
            session is None
            or getattr(session, "in_transaction", False) is not True
        ):
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "CALLER_OWNED_ACTIVE_TRANSACTION_REQUIRED"
            )
        if (
            not isinstance(at, datetime)
            or at.tzinfo is None
            or at.utcoffset() is None
        ):
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "EVALUATED_AT_INVALID"
            )
        if (
            not isinstance(idempotency_key, str)
            or not idempotency_key
            or idempotency_key != idempotency_key.strip()
            or "*" in idempotency_key
        ):
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "IDEMPOTENCY_KEY_INVALID"
            )
        if (
            not isinstance(request, Mapping)
            or set(request) != _TRUSTED_REQUEST_FIELDS
            or any(
                not isinstance(key, str) or not isinstance(value, str)
                for key, value in request.items()
            )
            or not isinstance(body, bytes)
        ):
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "TRUSTED_WORKLOAD_REQUEST_INVALID"
            )

        try:
            use = self._use_authority.authorize_noninteractive_workload(
                activation_tenant_id=None,
                privileged_role_id=SOVEREIGN_ARCHITECT,
                target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT,
                at=at,
                request=request,
                body=body,
                keys=self._workload_keys,
                expected_audience=self._expected_audience,
                idempotency_key=idempotency_key,
                session=session,
            )
        except PrivilegedActivationUseError as error:
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "CURRENT_PLATFORM_OPERATOR_USE_DENIED"
            ) from error

        if type(use) is not PrivilegedActivationUseResult:
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "CURRENT_PLATFORM_OPERATOR_USE_INVALID"
            )
        activation = use.activation
        if (
            type(activation) is not PrivilegedActivation
            or use.principal_id != activation.principal_id
            or activation.tenant_id is not None
            or activation.privileged_role_id != SOVEREIGN_ARCHITECT
            or activation.target_class
            is not PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT
            or not activation.is_current(
                at=at,
                tenant_id=None,
                principal_id=use.principal_id,
                privileged_role_id=SOVEREIGN_ARCHITECT,
                target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT,
            )
        ):
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "PLATFORM_OPERATOR_ACTIVATION_BINDING_INVALID"
            )

        try:
            assignment = self._permission_possession_resolver.resolve(
                principal_id=use.principal_id,
                permission_id=RECONCILIATION_READ_PERMISSION,
                session=session,
            )
        except CurrentSystemPermissionPossessionError as error:
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "RECONCILIATION_PERMISSION_CURRENTNESS_UNAVAILABLE"
            ) from error
        if assignment is None:
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "RECONCILIATION_READ_PERMISSION_REQUIRED"
            )
        if (
            type(assignment) is not SystemPermissionAssignment
            or assignment.principal_id != use.principal_id
            or assignment.permission_id != RECONCILIATION_READ_PERMISSION
        ):
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "RECONCILIATION_PERMISSION_BINDING_INVALID"
            )

        try:
            scope = self._scope_resolver.resolve_scope(
                principal_id=use.principal_id,
                activation_id=activation.activation_id,
                at=at,
                session=session,
            )
        except ServerOwnedReconciliationScopeResolutionError as error:
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "SERVER_OWNED_RECONCILIATION_SCOPE_UNAVAILABLE"
            ) from error
        if type(scope) is not LegalEvidenceProviderDiscoveryScope:
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "SERVER_OWNED_RECONCILIATION_SCOPE_INVALID"
            )
        expected_scope_fingerprint = sha3_512(
            scope.tenant_id.encode("utf-8")
        ).hexdigest()
        if scope.tenant_scope_fingerprint != expected_scope_fingerprint:
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "SERVER_OWNED_RECONCILIATION_SCOPE_FINGERPRINT_INVALID"
            )

        assignment_id = getattr(assignment, "assignment_id", None)
        assignment_fingerprint = getattr(
            assignment,
            "assignment_fingerprint",
            None,
        )
        if (
            not isinstance(assignment_id, str)
            or not assignment_id
            or not isinstance(assignment_fingerprint, str)
            or not assignment_fingerprint
        ):
            raise LegalEvidenceProviderReadOnlyReconciliationAuthorizationError(
                "RECONCILIATION_PERMISSION_EVIDENCE_INVALID"
            )

        return LegalEvidenceProviderReadOnlyReconciliationAuthorization(
            principal_id=use.principal_id,
            activation_id=activation.activation_id,
            permission_assignment_id=assignment_id,
            permission_assignment_fingerprint=assignment_fingerprint,
            scope=scope,
            provider_name=self._provider_name,
            authorized_at=at,
        )


__all__ = [
    "VERSION",
    "RECONCILIATION_READ_PERMISSION",
    "LegalEvidenceProviderReadOnlyReconciliationAuthorizationError",
    "ServerOwnedReconciliationScopeResolutionError",
    "ServerOwnedReconciliationScopeResolver",
    "ServerConfiguredReconciliationScopeResolver",
    "ServerConfiguredReconciliationTarget",
    "build_server_configured_reconciliation_target",
    "LegalEvidenceProviderReadOnlyReconciliationAuthorization",
    "LegalEvidenceProviderReadOnlyReconciliationAuthorizationGate",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_evidence_provider_readonly_reconciliation_authorization_gate.py
# VERSION: v1.0.5-L10A2R-C4D7C-STRICT-TENANT-STATUS
# AUTHORITY BOUNDARY:
#   Current platform-root P5 use plus exact current SYSTEM permission possession
#   and server-owned tenant scope resolution. No invocation or mutation authority.
# TENANT POSTURE:
#   Platform-root activation has tenant_id=None; target scope is independently
#   resolved by a server-owned, provider-bound scope authority.
# FAIL-CLOSED POSTURE:
#   Missing/stale P5, permission, transaction, configuration, or scope rejects.
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
